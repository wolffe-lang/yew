"""Deterministic stdio LSP fixture. Copied as the test's `wolf` executable.

The server returns a fixed target, but records the request position so a mouse
navigation test cannot pass by requesting at the old caret. No network I/O.
"""
import json
import os
import sys

source = sys.stdin.buffer
sink = sys.stdout.buffer
while True:
    headers = {}
    while True:
        line = source.readline(4096)
        if not line:
            sys.exit(0)
        if line == b'\r\n':
            break
        key, value = line.decode('ascii').split(':', 1)
        headers[key.lower()] = value.strip()
    length = int(headers['content-length'])
    if not 0 < length <= 1048576:
        sys.exit(2)
    data = source.read(length)
    if len(data) != length:
        sys.exit(2)
    request = json.loads(data)
    with open(os.environ['SELECTION_LSP_LOG'], 'a') as f:
        f.write(json.dumps(request) + '\n')
    method = request.get('method')
    if method == 'exit':
        break
    if 'id' not in request:
        continue
    if method == 'initialize':
        result = {'capabilities': {'textDocumentSync': 1, 'definitionProvider': True,
                                  'positionEncoding': 'utf-16'}}
    elif method == 'textDocument/definition':
        result = [{'uri': os.environ['SELECTION_LSP_TARGET'],
                   'range': {'start': {'line': 0, 'character': 0},
                             'end': {'line': 0, 'character': 17}}}]
    else:
        result = None
    response = json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}).encode()
    sink.write(b'Content-Length: ' + str(len(response)).encode() + b'\r\n\r\n' + response)
    sink.flush()
