#!/usr/bin/env python3
"""fakeserver: a deterministic language server for the yw11a PTY rows.

    fakeserver.py MODE [MARKER]

Speaks JSON-RPC over stdio with Content-Length framing, written from the
LSP specification for these rows alone (no LSP or JSON-RPC library). It
is the error-path half of tools/run-lsp-rows: C yew and the port each
run it under the same config, and their screens are compared.

MODE:
  mirror     incremental sync (change 2, UTF-16 positions): applies every
             didChange to its own copy; on didSave reads the file and
             publishes one diagnostic on line 1: "view matches disk (N
             bytes)" (information) or "view DIFFERS from disk" (error)
  crash      full sync; after didOpen publishes "before the crash"; on
             didSave creates MARKER and exits 3. A server started with
             MARKER present publishes "after the restart" and serves on
  malformed  as crash, but on didSave it writes a frame whose header is
             not a length ("Content-Length: nope") and serves on
  slow       answers initialize 1500 ms late, then as mirror
  hang       never answers initialize (the editor's deadline fires)
  deaf       serves as mirror but never answers shutdown and ignores exit
"""
import json
import os
import sys
import time
import urllib.parse

MODE = sys.argv[1] if len(sys.argv) > 1 else "mirror"
MARKER = sys.argv[2] if len(sys.argv) > 2 else ""
IN = sys.stdin.buffer
OUT = sys.stdout.buffer


def read_message():
    length = None
    while True:
        line = IN.readline()
        if not line:
            return None
        line = line.rstrip(b"\r\n")
        if not line:
            break
        name, _, value = line.partition(b":")
        if name.strip().lower() == b"content-length":
            length = int(value.strip())
    if length is None:
        return None
    body = IN.read(length)
    if len(body) != length:
        return None
    return json.loads(body.decode("utf-8"))


def write_raw(data):
    OUT.write(data)
    OUT.flush()


def send(obj):
    body = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    write_raw(b"Content-Length: %d\r\n\r\n" % len(body) + body)


def publish(uri, version, severity, message):
    diag = {
        "range": {"start": {"line": 0, "character": 0},
                  "end": {"line": 0, "character": 1}},
        "severity": severity,
        "source": "fake",
        "message": message,
    }
    params = {"uri": uri, "diagnostics": [diag]}
    if version is not None:
        params["version"] = version
    send({"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
          "params": params})


def utf16_offset(text, line, character):
    """The str index of LSP position (line, character in UTF-16 units)."""
    at = 0
    for _ in range(line):
        nl = text.find("\n", at)
        if nl < 0:
            return len(text)
        at = nl + 1
    units = 0
    while at < len(text) and text[at] != "\n" and units < character:
        units += 2 if ord(text[at]) > 0xFFFF else 1
        at += 1
    return at


def path_of(uri):
    assert uri.startswith("file://")
    return urllib.parse.unquote(uri[len("file://"):])


def main():
    docs = {}
    incremental = MODE in ("mirror", "slow", "deaf")
    while True:
        msg = read_message()
        if msg is None:
            return 0
        method = msg.get("method")
        mid = msg.get("id")
        if method == "initialize":
            if MODE == "hang":
                continue
            if MODE == "slow":
                time.sleep(1.5)
            sync = {"openClose": True, "change": 2 if incremental else 1,
                    "save": {"includeText": False}}
            send({"jsonrpc": "2.0", "id": mid,
                  "result": {"capabilities": {"textDocumentSync": sync},
                             "serverInfo": {"name": "fake"}}})
        elif method == "textDocument/didOpen":
            td = msg["params"]["textDocument"]
            docs[td["uri"]] = td["text"]
            if MODE in ("crash", "malformed"):
                if MARKER and os.path.exists(MARKER):
                    publish(td["uri"], td["version"], 2, "after the restart")
                else:
                    publish(td["uri"], td["version"], 1, "before the crash")
        elif method == "textDocument/didChange":
            p = msg["params"]
            uri = p["textDocument"]["uri"]
            text = docs.get(uri, "")
            for ch in p["contentChanges"]:
                if "range" not in ch:
                    text = ch["text"]
                    continue
                r = ch["range"]
                lo = utf16_offset(text, r["start"]["line"], r["start"]["character"])
                hi = utf16_offset(text, r["end"]["line"], r["end"]["character"])
                text = text[:lo] + ch["text"] + text[hi:]
            docs[uri] = text
        elif method == "textDocument/didSave" and MODE in ("crash", "malformed"):
            if MARKER:
                open(MARKER, "w").close()
            if MODE == "crash":
                return 3
            write_raw(b"Content-Length: nope\r\n\r\n{}")
        elif method == "textDocument/didSave":
            uri = msg["params"]["textDocument"]["uri"]
            with open(path_of(uri), "rb") as f:
                disk = f.read()
            view = docs.get(uri, "").encode("utf-8")
            if view == disk:
                publish(uri, None, 3, "view matches disk (%d bytes)" % len(disk))
            else:
                publish(uri, None, 1, "view DIFFERS from disk")
        elif method == "textDocument/didClose":
            docs.pop(msg["params"]["textDocument"]["uri"], None)
        elif method == "shutdown":
            if MODE == "deaf":
                continue
            send({"jsonrpc": "2.0", "id": mid, "result": None})
        elif method == "exit":
            if MODE == "deaf":
                continue
            return 0
        elif mid is not None and method is not None:
            send({"jsonrpc": "2.0", "id": mid,
                  "error": {"code": -32601, "message": "method not found"}})


if __name__ == "__main__":
    sys.exit(main())
