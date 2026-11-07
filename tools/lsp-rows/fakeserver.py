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

The feature modes (yw11b) serve full sync and the capabilities named:
  null       hover, definition, references, documentSymbol: every one
             answered `null`
  error      the same four, every one answered with error -32603, then a
             receipt
  stale      hover, answered ("late") only once the document has changed
             since it was opened (at once if it already has, else at the
             next didChange), then a receipt: the answer is stale on any
             host
  deadline   definition: MARKER created when the request arrives, and
             the answer (a location on line 1) held until the next
             didSave, then sent with a receipt. The row saves once the
             request's 10 s deadline (jsonrpc.h:20) has passed, so the
             answer comes after it on any host; no timer here
  partial    definition alone: every other feature is absent
  highlight  documentHighlight: a read on line 1 (0-2) and a write on
             line 2 (4-5)
  signature  signatureHelp, triggered by "(": one signature, its first
             parameter active
  renamefiles rename: a workspace edit over the open file (the
             definition on line 1 and the call on line 6) and
             src/other.lu, not open (the call on its line 2)

yw15's mode:
  root       full sync, no features: initialize's rootUri (and rootPath)
             written to MARKER, one per line, before it is answered: the
             root the editor resolved for the document it opens with

A receipt follows an answer the editor is to show nothing for: the
document's diagnostics republished as one warning on line 1 per such
answer so far. The editor reads it after the answer on the same pipe, so
a row waits on its badge (`W:N`) instead of a quiet gap.
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


FOUR = {"hoverProvider": True, "definitionProvider": True,
        "referencesProvider": True, "documentSymbolProvider": True}
FEATURE_CAPS = {
    "null": FOUR,
    "error": FOUR,
    "stale": {"hoverProvider": True},
    "deadline": {"definitionProvider": True},
    "partial": {"definitionProvider": True},
    "highlight": {"documentHighlightProvider": True},
    "signature": {"signatureHelpProvider": {"triggerCharacters": ["("]}},
    "renamefiles": {"renameProvider": True},
}
FEATURE_METHODS = (
    "textDocument/hover", "textDocument/definition",
    "textDocument/references", "textDocument/documentSymbol",
    "textDocument/documentHighlight", "textDocument/signatureHelp",
    "textDocument/rename",
)


def span(line, lo, hi):
    return {"start": {"line": line, "character": lo},
            "end": {"line": line, "character": hi}}


RECEIPTS = [0]


def receipt(uri):
    """One more warning on line 1 (see the module's doc): the badge reads
    W:N after the Nth answer the editor shows nothing for."""
    RECEIPTS[0] += 1
    n = RECEIPTS[0]
    diags = [{"range": span(0, 0, 1), "severity": 2, "source": "fake",
              "message": "answer %d sent" % (k + 1)} for k in range(n)]
    send({"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
          "params": {"uri": uri, "diagnostics": diags}})


# The stale mode's text at didOpen and its hovers waiting for a change;
# the deadline mode's definitions waiting for a save.
OPENED = {}
STALE_WAITING = []
LATE_WAITING = []


def answer_stale(mid, uri):
    send({"jsonrpc": "2.0", "id": mid,
          "result": {"contents": {"kind": "plaintext", "value": "late"}}})
    receipt(uri)


def answer_late(mid, uri):
    send({"jsonrpc": "2.0", "id": mid,
          "result": {"uri": uri, "range": span(0, 0, 0)}})
    receipt(uri)


def answer_feature(msg, docs):
    """A feature request in a feature mode."""
    mid = msg.get("id")
    method = msg["method"]
    if MODE == "null":
        send({"jsonrpc": "2.0", "id": mid, "result": None})
    elif MODE == "error":
        send({"jsonrpc": "2.0", "id": mid,
              "error": {"code": -32603, "message": "boom"}})
        receipt(msg["params"]["textDocument"]["uri"])
    elif MODE == "stale":
        uri = msg["params"]["textDocument"]["uri"]
        if docs.get(uri) != OPENED.get(uri):
            answer_stale(mid, uri)
        else:
            STALE_WAITING.append((mid, uri))
    elif MODE == "deadline":
        uri = msg["params"]["textDocument"]["uri"]
        LATE_WAITING.append((mid, uri))
        if MARKER:
            open(MARKER, "w").close()
    elif MODE == "partial":
        loc = {"uri": msg["params"]["textDocument"]["uri"],
               "range": span(0, 0, 0)}
        send({"jsonrpc": "2.0", "id": mid, "result": loc})
    elif MODE == "highlight":
        send({"jsonrpc": "2.0", "id": mid,
              "result": [{"range": span(0, 0, 2), "kind": 2},
                         {"range": span(1, 4, 5), "kind": 3}]})
    elif MODE == "signature":
        sig = {"label": "plus(x: int, y: int)",
               "parameters": [{"label": [5, 11]}, {"label": [13, 19]}]}
        send({"jsonrpc": "2.0", "id": mid,
              "result": {"signatures": [sig], "activeSignature": 0,
                         "activeParameter": 0}})
    elif MODE == "renamefiles":
        p = msg["params"]
        uri = p["textDocument"]["uri"]
        name = p["newName"]
        other = uri.rsplit("/", 1)[0] + "/other.lu"
        send({"jsonrpc": "2.0", "id": mid,
              "result": {"changes": {
                  uri: [{"range": span(0, 3, 6), "newText": name},
                        {"range": span(5, 4, 7), "newText": name}],
                  other: [{"range": span(1, 4, 7), "newText": name}]}}})


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
            if MODE == "root" and MARKER:
                p = msg.get("params") or {}
                with open(MARKER, "w") as fh:
                    fh.write("%s\n%s\n" % (p.get("rootUri"), p.get("rootPath")))
            if MODE == "slow":
                time.sleep(1.5)
            sync = {"openClose": True, "change": 2 if incremental else 1,
                    "save": {"includeText": False}}
            caps = {"textDocumentSync": sync}
            caps.update(FEATURE_CAPS.get(MODE, {}))
            send({"jsonrpc": "2.0", "id": mid,
                  "result": {"capabilities": caps,
                             "serverInfo": {"name": "fake"}}})
        elif method in FEATURE_METHODS and MODE in FEATURE_CAPS:
            answer_feature(msg, docs)
        elif method == "textDocument/didOpen":
            td = msg["params"]["textDocument"]
            docs[td["uri"]] = td["text"]
            OPENED.setdefault(td["uri"], td["text"])
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
            if MODE == "stale" and text != OPENED.get(uri):
                for waiting in [w for w in STALE_WAITING if w[1] == uri]:
                    STALE_WAITING.remove(waiting)
                    answer_stale(*waiting)
        elif method == "textDocument/didSave" and MODE in ("crash", "malformed"):
            if MARKER:
                open(MARKER, "w").close()
            if MODE == "crash":
                return 3
            write_raw(b"Content-Length: nope\r\n\r\n{}")
        elif method == "textDocument/didSave" and MODE == "deadline":
            for waiting in list(LATE_WAITING):
                LATE_WAITING.remove(waiting)
                answer_late(*waiting)
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
