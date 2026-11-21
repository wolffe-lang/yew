# The `wolf lsp` proxy of tools/lsp-typing-row: see the row's header.
# yw25 measurement shim: `wolf lsp` proxy. Logs every client->server and
# server->client frame (method, bytes, time) to $YW25_LSPLOG (JSONL) and the
# real server's CPU time at exit. Anything but `wolf lsp` execs the real wolf.
import os, sys, json, time, threading, subprocess
real = os.environ["YW25_REAL_WOLF"]
if len(sys.argv) < 2 or sys.argv[1] != "lsp":
    os.execv(real, [real] + sys.argv[1:])
log = open(os.environ["YW25_LSPLOG"], "a", buffering=1)
lock = threading.Lock()
def emit(d):
    d["t"] = time.monotonic()
    with lock:
        log.write(json.dumps(d) + "\n")
p = subprocess.Popen([real] + sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def frames(src, dst, who):
    buf = b""
    while True:
        chunk = os.read(src, 65536)
        if not chunk:
            break
        os.write(dst, chunk)
        buf += chunk
        while True:
            i = buf.find(b"\r\n\r\n")
            if i < 0:
                break
            hdr = buf[:i].decode("latin1").lower()
            n = None
            for line in hdr.split("\r\n"):
                if line.startswith("content-length:"):
                    n = int(line.split(":")[1])
            if n is None or len(buf) < i + 4 + n:
                break
            body = buf[i + 4:i + 4 + n]
            buf = buf[i + 4 + n:]
            try:
                m = json.loads(body)
            except Exception:
                m = {}
            d = {"who": who, "bytes": n, "method": m.get("method", "response" if "id" in m else "?")}
            if d["method"] == "textDocument/didChange":
                cc = m["params"]["contentChanges"]
                d["changes"] = len(cc)
                d["ranged"] = sum(1 for c in cc if "range" in c)
            if d["method"] == "initialize" or (who == "s2c" and "result" in m and "capabilities" in m.get("result", {})):
                d["sync"] = (m.get("result", {}).get("capabilities", {}) or {}).get("textDocumentSync")
            if d["method"] == "textDocument/publishDiagnostics":
                d["ndiag"] = len(m["params"].get("diagnostics", []))
            emit(d)
    try:
        os.close(dst)
    except OSError:
        pass
t1 = threading.Thread(target=frames, args=(0, p.stdin.fileno(), "c2s"), daemon=True)
t2 = threading.Thread(target=frames, args=(p.stdout.fileno(), 1, "s2c"), daemon=True)
t1.start(); t2.start()
def cpu():
    try:
        f = open("/proc/%d/stat" % p.pid).read().rsplit(")", 1)[1].split()
        return (int(f[11]) + int(f[12])) / os.sysconf("SC_CLK_TCK")
    except Exception:
        return None
last = None
while p.poll() is None:
    c = cpu()
    if c is not None:
        last = c
        if int(time.monotonic()) != int(globals().get('_lt', 0)):
            _lt = time.monotonic()
            emit({"who": "cpu", "server_cpu_s": c})
    time.sleep(0.25)
emit({"who": "end", "server_cpu_s": last, "rc": p.returncode})
