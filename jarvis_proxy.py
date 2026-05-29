#!/usr/bin/env python3
"""
JARVIS Proxy — LM Studio köprüsü
================================
Bu script iki şey yapar:
  1. jarvis.html dosyasını tarayıcıda açar (CORS sorunu olmadan)
  2. Tarayıcıdan gelen istekleri LM Studio'ya iletir

Kullanım:
  python jarvis_proxy.py

Gereksinimler: Sadece Python 3 standart kütüphanesi (pip gerektirmez)
"""

import http.server
import urllib.request
import urllib.error
import json
import os
import sys
import threading
import webbrowser
import time

# ── AYARLAR ──────────────────────────────────
PROXY_PORT   = [proxy port same as html]          # Bu scriptin portu (tarayıcı buraya bağlanır)
LM_STUDIO    = "[LM Studio Server Port]"   # LM Studio varsayılan adresi
HTML_FILE    = "jarvis.html" # Same folder with proxy
# ─────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class JarvisHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Sadece önemli logları göster
        msg = fmt % args
        if "200" in msg or "404" in msg or "500" in msg:
            print(f"  [{self._client_ip()}] {msg}")

    def _client_ip(self):
        return self.client_address[0]

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    # OPTIONS preflight
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # GET — jarvis.html veya statik dosya sun
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/jarvis.html":
            self._serve_html()
        elif path == "/health":
            self._json_response(200, {"status": "ok", "proxy_port": PROXY_PORT, "lm_studio": LM_STUDIO})
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_html(self):
        html_path = os.path.join(SCRIPT_DIR, HTML_FILE)
        if not os.path.exists(html_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"jarvis.html bulunamadi! Ayni klasorde olmali.")
            return
        with open(html_path, "rb") as f:
            content = f.read()
        # HTML icindeki LM Studio URL'lerini proxy URL'siyle degistir
        content = content.replace(
            b"[Same as Line 27]",
            f"http://localhost:{PROXY_PORT}/lm".encode()
        ).replace(
            b"http://localhost:1234",
            f"http://localhost:{PROXY_PORT}/lm".encode()
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self._cors()
        self.end_headers()
        self.wfile.write(content)

    # POST — LM Studio'ya proxy
    def do_POST(self):
        if self.path.startswith("/lm"):
            self._proxy_lm()
        else:
            self.send_response(404)
            self.end_headers()

    def _proxy_lm(self):
        # /lm/v1/chat/completions  →  LM_STUDIO/v1/chat/completions
        lm_path = self.path[3:]  # "/lm" kismini at
        if not lm_path:
            lm_path = "/v1/chat/completions"
        target = LM_STUDIO + lm_path

        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length) if length else b""

        try:
            req = urllib.request.Request(
                target,
                data=body,
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self._cors()
                self.end_headers()
                self.wfile.write(data)
                print(f"  ✓ LM Studio yanıt verdi ({len(data)} byte)")

        except urllib.error.URLError as e:
            err = json.dumps({
                "error": {
                    "message": f"LM Studio'ya ulaşılamadı: {e.reason}. "
                               f"LM Studio açık mı ve sunucu başlatıldı mı?",
                    "type": "connection_error"
                }
            }).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self._cors()
            self.end_headers()
            self.wfile.write(err)
            print(f"  ✗ LM Studio bağlantı hatası: {e.reason}")

        except Exception as e:
            err = json.dumps({"error": {"message": str(e), "type": "proxy_error"}}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self._cors()
            self.end_headers()
            self.wfile.write(err)
            print(f"  ✗ Proxy hatası: {e}")

    # GET proxy (models endpoint için)
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/jarvis.html":
            self._serve_html()
        elif path == "/health":
            self._json_response(200, {"status": "ok"})
        elif path.startswith("/lm"):
            self._proxy_lm_get()
        else:
            self.send_response(404)
            self.end_headers()

    def _proxy_lm_get(self):
        lm_path = self.path[3:]
        if not lm_path:
            lm_path = "/v1/models"
        target = LM_STUDIO + lm_path
        try:
            req = urllib.request.Request(target, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self._cors()
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            err = json.dumps({"error": str(e), "data": []}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self._cors()
            self.end_headers()
            self.wfile.write(err)

    def _json_response(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)


def lm_studio_kontrol():
    """LM Studio'nun erişilebilir olup olmadığını kontrol et."""
    try:
        req = urllib.request.Request(LM_STUDIO + "/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=3) as r:
            d = json.loads(r.read())
            modeller = [m.get("id","") for m in d.get("data",[])]
            return True, modeller
    except Exception as e:
        return False, str(e)


def main():
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║         J.A.R.V.I.S.  PROXY  SERVER             ║")
    print("║                                                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # HTML dosyası kontrolü
    html_path = os.path.join(SCRIPT_DIR, HTML_FILE)
    if not os.path.exists(html_path):
        print(f"  ✗ HATA: '{HTML_FILE}' bulunamadı!")
        print(f"  → Bu script ile jarvis.html aynı klasörde olmalı.")
        print(f"  → Klasör: {SCRIPT_DIR}")
        sys.exit(1)
    print(f"  ✓ jarvis.html bulundu")

    # LM Studio kontrolü
    print(f"  ⏳ LM Studio kontrol ediliyor ({LM_STUDIO})...")
    ok, sonuc = lm_studio_kontrol()
    if ok:
        print(f"  ✓ LM Studio bağlı! Modeller: {', '.join(sonuc) if sonuc else 'yüklü yok'}")
    else:
        print(f"  ⚠  LM Studio şu an erişilemiyor: {sonuc}")
        print(f"  → LM Studio'yu açıp Developer sekmesinden sunucuyu başlatın")
        print(f"  → Proxy çalışmaya devam ediyor, sonra bağlanabilirsiniz")

    # Sunucuyu başlat
    server = http.server.HTTPServer(("localhost", PROXY_PORT), JarvisHandler)
    url = f"http://localhost:{PROXY_PORT}"

    print()
    print(f"  🚀 Proxy sunucusu başlatıldı: {url}")
    print(f"  🌐 Tarayıcı otomatik açılıyor...")
    print()
    print("  Durdurmak için: Ctrl+C")
    print("─" * 52)

    # Tarayıcıyı 1 sn sonra aç
    def ac():
        time.sleep(1.0)
        webbrowser.open(url)
    threading.Thread(target=ac, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  JARVIS proxy kapatıldı. Güle güle efendim.")
        server.shutdown()


if __name__ == "__main__":
    main()
