#!/usr/bin/env python3
"""Versions réellement proposées par TorBox pour quelques films et épisodes (noms et types d'adresse seulement)."""
# Cloudflare refuse la signature « Python-urllib » (erreur 1010) : signature de navigateur.
UA_BROWSER = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
import json, re, subprocess, sys, time, urllib.parse, urllib.request
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18085") + "/jellyfin"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()

CLIENT = __import__("os").environ.get("CLIENT")  # p. ex. « AIOStreams Web » comme l'app dans un navigateur

def call(m, p, b=None, tok=None):
    A = 'MediaBrowser Client="walter-test", Device="vm", DeviceId="torbox-test", Version="1"' + (f', Token="{tok}"' if tok else "")
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json", "User-Agent": UA_BROWSER, "Authorization": A, **({"X-AIOStreams-Client": CLIENT} if CLIENT else {})})
    with urllib.request.urlopen(r, timeout=120) as f:
        raw = f.read(); return json.loads(raw) if raw else None

a = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw}); tok, uid = a["AccessToken"], a["User"]["Id"]
views = call("GET", f"/UserViews?userId={uid}", tok=tok)["Items"]
OFF = int(sys.argv[2]) if len(sys.argv) > 2 else 0
movies = call("GET", f"/Users/{uid}/Items?ParentId={views[0]['Id']}&Limit=3&StartIndex={OFF}", tok=tok)["Items"]
shows = call("GET", f"/Users/{uid}/Items?ParentId={views[1]['Id']}&Limit=2&StartIndex={OFF}", tok=tok)["Items"]
targets = movies[:]
for s in shows:
    eps = call("GET", f"/Shows/{s['Id']}/Episodes?userId={uid}&Limit=2", tok=tok)["Items"]
    targets += [e for e in eps if e.get("LocationType") != "Virtual"][:1]
out = {}
for it in targets:
    t0 = time.time()
    pi = call("POST", f"/Items/{it['Id']}/PlaybackInfo?UserId={uid}", {}, tok=tok)
    srcs = [s for s in pi["MediaSources"] if s.get("Path")]
    label = it["Name"] if it["Type"] != "Episode" else f"{it.get('SeriesName')} S{it.get('ParentIndexNumber')}E{it.get('IndexNumber')}"
    print(f"{label[:40]:40} {len(srcs):2} versions en {time.time()-t0:4.1f}s")
    for s in srcs[:3]:
        host = urllib.parse.urlparse(s["Path"]).netloc
        name = re.sub(r"\s+", " ", s.get("Name", ""))[:70]
        print(f"     · {name} | {host} | {s.get('Container')}")
    out[it["Id"]] = {"label": label, "sources": [s["Id"] for s in srcs]}
json.dump(out, open("/apps/sagora/production/state/torbox-test-items.json", "w"))
