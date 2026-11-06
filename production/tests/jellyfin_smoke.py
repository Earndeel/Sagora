#!/usr/bin/env python3
"""Vérifie la connexion « Famille » au serveur média AIOStreams et le contenu de l'accueil (aucun secret affiché)."""
# Cloudflare refuse la signature « Python-urllib » (erreur 1010) : signature de navigateur.
UA_BROWSER = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
import json, subprocess, sys, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18090"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"],
                    capture_output=True, text=True, check=True).stdout.strip()
AUTH = 'MediaBrowser Client="walter-test", Device="vm", DeviceId="walter-smoke", Version="1"'


def call(method, path, body=None, token=None):
    h = {"Content-Type": "application/json", "User-Agent": UA_BROWSER, "Authorization": AUTH + (f', Token="{token}"' if token else "")}
    r = urllib.request.Request(BASE + "/jellyfin" + path, method=method, headers=h,
                               data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(r, timeout=60) as f:
        return json.load(f)


a = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw})
tok, uid = a["AccessToken"], a["User"]["Id"]
views = call("GET", f"/Users/{uid}/Views", token=tok)["Items"]
print("utilisateur:", a["User"]["Name"], "| bibliothèques:", len(views))
for v in views[:6]:
    items = call("GET", f"/Users/{uid}/Items?ParentId={v['Id']}&Limit=3&Fields=RemoteTrailers,Overview", token=tok)["Items"]
    print(" -", v["Name"], "→", [(i["Name"], len(i.get("RemoteTrailers") or [])) for i in items])

first = call("GET", f"/Users/{uid}/Items?ParentId={views[0]['Id']}&Limit=1", token=tok)["Items"][0]
detail = call("GET", f"/Users/{uid}/Items/{first['Id']}", token=tok)
print("fiche:", detail["Name"], "| bandes-annonces:", [t.get("Url", "")[:45] for t in detail.get("RemoteTrailers") or []][:3],
      "| fonds:", len(detail.get("BackdropImageTags") or []))
