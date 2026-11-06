#!/usr/bin/env python3
"""Addon Stremio de test (préproduction seulement) : pour tout film ou épisode, une version cassée en tête
puis une vraie vidéo publique (Big Buck Bunny, WebM). Sert à vérifier le repli automatique de version."""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = sys.argv[1] if len(sys.argv) > 1 else "172.17.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 18099
GOOD = "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.360p.vp9.webm"
MANIFEST = {"id": "walter.test.fallback", "version": "1.0.0", "name": "Test repli", "description": "Versions de test",
            "resources": ["stream"], "types": ["movie", "series"], "idPrefixes": ["tt", "tmdb"], "catalogs": []}


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/manifest.json"):
            body = MANIFEST
        elif "/stream/" in self.path:
            body = {"streams": [
                {"name": "TEST 2160p", "title": "Cassée.2160p.WEB-DL.mkv", "url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/0/00/Introuvable-walter-test.webm/Introuvable.360p.webm",
                 "behaviorHints": {"filename": "Cassee.2160p.mkv", "videoSize": 4_000_000_000}},
                {"name": "TEST 360p", "title": "Big.Buck.Bunny.360p.webm", "url": GOOD,
                 "behaviorHints": {"filename": "Big.Buck.Bunny.360p.webm", "videoSize": 30_000_000}},
            ]}
        else:
            self.send_response(404); self.end_headers(); return
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(data)

    def log_message(self, *a):
        pass


ThreadingHTTPServer((HOST, PORT), H).serve_forever()
