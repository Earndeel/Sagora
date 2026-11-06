"""Se connecter au tableau de bord d'administration d'AIOStreams (compte walter), p. ex. fournisseurs Usenet.
À importer depuis python3 (secrets lus dans Bitwarden par walter-secret, jamais écrits)."""
import json, subprocess, urllib.request, urllib.error, http.cookiejar
BASE = "http://127.0.0.1:18090/api/v1"
jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def sec(item, field="password"): return subprocess.run(["walter-secret", "get", item, field], capture_output=True, text=True).stdout.strip()
def api(m, p, b=None):
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json"})
    try:
        with op.open(r, timeout=60) as f: raw = f.read(); return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e: return {"http": e.code, "body": e.read().decode()[:500]}
def login():
    return api("POST", "/auth/login", {"username": "walter", "password": sec("60fd7166-82ec-48e6-ac6d-6e6c25fd7805")})
