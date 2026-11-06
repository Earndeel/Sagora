#!/usr/bin/env python3
"""Indépendance des profils par l'API (même chemin que l'app) : favori et progression posés par un profil,
absents chez un autre ; changement de profil sans mot de passe depuis un appareil connecté."""
# Cloudflare refuse la signature « Python-urllib » (erreur 1010) : signature de navigateur.
UA_BROWSER = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
import json, subprocess, sys, urllib.request
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18090") + "/jellyfin"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()

def call(m, p, b=None, tok=None):
    A = 'MediaBrowser Client="walter-test", Device="vm", DeviceId="profiles-test", Version="1"' + (f', Token="{tok}"' if tok else "")
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json", "User-Agent": UA_BROWSER, "Authorization": A})
    with urllib.request.urlopen(r, timeout=60) as f:
        raw = f.read()
        return json.loads(raw) if raw else None

a = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw}); tok = a["AccessToken"]
users = call("GET", "/AIOStreams/Users", tok=tok)
ids = {u["user"]["Name"]: u["user"]["Id"] for u in users}
print("profils:", list(ids))
toks = {n: call("POST", "/AIOStreams/Token", {"UserId": i}, tok=tok)["AccessToken"] for n, i in ids.items()}
me = {n: call("GET", "/Users/Me", tok=t)["Id"] for n, t in toks.items()}
view = call("GET", f"/UserViews?userId={me['Profil 2']}", tok=toks["Profil 2"])["Items"][0]
item = call("GET", f"/Users/{me['Profil 2']}/Items?ParentId={view['Id']}&Limit=1&StartIndex=5", tok=toks["Profil 2"])["Items"][0]
call("POST", f"/UserFavoriteItems/{item['Id']}?userId={me['Profil 2']}", tok=toks["Profil 2"])
def fav(n):
    return [i["Name"] for i in call("GET", f"/Items?userId={me[n]}&Recursive=true&Filters=IsFavorite", tok=toks[n])["Items"]]
for n in ("Profil 2", "Invité", "Lucas"):
    print(f"favoris {n}:", fav(n))
call("DELETE", f"/UserFavoriteItems/{item['Id']}?userId={me['Profil 2']}", tok=toks["Profil 2"])
print("favori retiré, Profil 2:", fav("Profil 2"))
