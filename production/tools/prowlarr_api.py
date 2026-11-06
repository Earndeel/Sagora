"""Appeler l'API de Prowlarr (index, trackers C411/TR4KER, NZBIndex).
À importer depuis python3 (secrets lus dans Bitwarden par walter-secret, jamais écrits)."""
import json, subprocess, urllib.request, urllib.error
BASE = "http://127.0.0.1:19696/prowlarr/api/v1"
KEY = subprocess.run(["walter-secret", "get", "Sagora · Prowlarr API", "password"], capture_output=True, text=True).stdout.strip()
def api(m, p, b=None):
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None,
                               headers={"X-Api-Key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=120) as f:
            raw = f.read(); return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return {"http": e.code, "body": e.read().decode()[:600]}
