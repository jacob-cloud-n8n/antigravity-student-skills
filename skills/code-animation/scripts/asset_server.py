"""本機素材庫的小型 HTTP 伺服器（只綁 127.0.0.1、隨機埠、唯讀），給渲染器與配樂腳本共用。

為什麼需要：瀏覽器的 fetch() 不支援 file:// 網址（就算開了 --allow-file-access-from-files 也一樣），
角色 SVG、Tone.js 載入音效都要 fetch → 改由這個伺服器提供，並加 CORS 標頭讓 file:// 場景能讀。
"""
import os, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ASSET_DIR = Path(os.path.expanduser("~/.local/share/code-animation-assets"))


class _Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_POST(self): self.send_error(405)
    def do_PUT(self): self.send_error(405)
    def log_message(self, *a): pass


def start():
    """回傳 (網址, 停止函式)；素材庫不存在時回傳 ("", 空函式)。"""
    if not ASSET_DIR.exists():
        return "", (lambda: None)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Handler, directory=str(ASSET_DIR)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}", srv.shutdown
