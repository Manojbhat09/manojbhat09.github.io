#!/usr/bin/env python3
"""
Dev server with CORS + SharedArrayBuffer headers.
Required for wllama multi-threaded WASM inference.
"""
import http.server
import socketserver
import os

PORT = 4001

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(('', PORT), CORSHandler) as httpd:
    print(f"\n  Blog preview  →  http://localhost:{PORT}/preview/index.html")
    print(f"  wllama demo   →  http://localhost:{PORT}/preview/wllama-test.html")
    print(f"  Main site     →  http://localhost:{PORT}/index.html")
    print(f"\n  Press Ctrl+C to stop\n")
    httpd.serve_forever()
