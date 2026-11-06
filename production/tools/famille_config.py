"""Lire et écrire la configuration « Famille » (GET/PUT /api/v1/user ; un PUT remplace TOUT : sauvegarder avant dans /user/Lucas/backups/changes/).
À importer depuis python3 (secrets lus dans Bitwarden par walter-secret, jamais écrits)."""
import base64, json, subprocess, sys, urllib.request
BASE = "http://127.0.0.1:18090/api/v1"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
AUTH = "Basic " + base64.b64encode(f"{uuid}:{pw}".encode()).decode()
def api(m, p, b=None):
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json", "Authorization": AUTH})
    return json.load(urllib.request.urlopen(r, timeout=60))
def get_config():
    d = api("GET", f"/user?uuid={uuid}&password={urllib.request.quote(pw)}") if False else api("GET", "/user")
    return d.get("data", d)
def put_config(c):
    import urllib.error
    try:
        return api("PUT", "/user", {"config": c})
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode()[:800]}
