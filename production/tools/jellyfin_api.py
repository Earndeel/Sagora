"""Appeler l'API Jellyfin de Sagora en tant que configuration Famille (profils, réglages d'utilisateur, pistes par défaut).
À importer depuis python3 (secrets lus dans Bitwarden par walter-secret, jamais écrits)."""
import json, subprocess, urllib.request
BASE = "http://127.0.0.1:18085/jellyfin"; UA = "Mozilla/5.0 Chrome/130"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
def call(m, p, b=None, tok=None, headers=None):
    A = 'MediaBrowser Client="walter-check", Device="vm", DeviceId="lang-check", Version="1"' + (f', Token="{tok}"' if tok else "")
    h = {"Content-Type": "application/json", "User-Agent": UA, "Authorization": A, **(headers or {})}
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers=h)
    with urllib.request.urlopen(r, timeout=120) as f:
        raw = f.read(); return json.loads(raw) if raw else None
tok = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw})["AccessToken"]
def user(name):
    for u in call("GET", "/AIOStreams/Users", tok=tok):
        if u["user"]["Name"] == name:
            t = call("POST", "/AIOStreams/Token", {"UserId": u["user"]["Id"]}, tok=tok)["AccessToken"]
            return t, call("GET", "/Users/Me", tok=t)["Id"]
