#!/usr/bin/env python3
"""ローカル確認用の簡易サーバー（音声のシーク・長さの取得に必要な Range リクエスト対応版）。

  python serve.py            # http://localhost:8000/ を開く（index.html または soundtrack.html）
  python serve.py 8080       # ポート指定

python -m http.server は Range リクエストに対応していないため、ブラウザが音声の長さを
正しく取得できず、シークバーの時間がずれたり、シークで途中から再生されたりすることがあります。
このスクリプトは同じ使い方で、Range に対応しています（GitHub Pages は最初から対応済み）。
"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", rng.strip())
        size = os.path.getsize(path)
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return super().send_head()
        if m.group(1) == "":                       # bytes=-N（末尾からNバイト）
            start, end = max(size - int(m.group(2)), 0), size - 1
        else:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else size - 1
        if start >= size or start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            self.send_header("Content-Range", f"bytes */{size}")
            return None
        end = min(end, size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self._range_left = end - start + 1
        return f

    def copyfile(self, source, outputsocket):
        left = getattr(self, "_range_left", None)
        if left is None:
            return super().copyfile(source, outputsocket)
        while left > 0:
            chunk = source.read(min(64 * 1024, left))
            if not chunk:
                break
            outputsocket.write(chunk)
            left -= len(chunk)
        self._range_left = None

    def end_headers(self):
        if self.command in ("GET", "HEAD") and not self._headers_buffer_has("Accept-Ranges"):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def _headers_buffer_has(self, name):
        return any(name.lower().encode() in h.lower() for h in getattr(self, "_headers_buffer", []))

    def log_message(self, fmt, *a):
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))   # このファイルのあるフォルダを公開
    page = "" if os.path.exists("index.html") else "soundtrack.html"    # index.html は / で開く
    print(f"http://localhost:{port}/{page}  （Ctrl+C で終了）")
    try:
        ThreadingHTTPServer(("", port), RangeHandler).serve_forever()
    except KeyboardInterrupt:
        pass
