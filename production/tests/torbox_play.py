#!/usr/bin/env python3
"""Lecture réelle d'une version TorBox, comme un lecteur : le lien proposé est suivi jusqu'au fichier TorBox,
puis ffmpeg décode 8 s d'image et de son à partir d'une position (aucun nouveau téléchargement : sources en cache)."""
# Cloudflare refuse la signature « Python-urllib » (erreur 1010) : signature de navigateur.
UA_BROWSER = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
import json, subprocess, sys, time, urllib.parse, urllib.request
sys.path.insert(0, "/apps/sagora/production/tests")
BASE = "http://127.0.0.1:18085/jellyfin"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
def call(m, p, b=None, tok=None):
    A = 'MediaBrowser Client="walter-test", Device="vm", DeviceId="torbox-play", Version="1"' + (f', Token="{tok}"' if tok else "")
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json", "User-Agent": UA_BROWSER, "Authorization": A})
    with urllib.request.urlopen(r, timeout=120) as f:
        raw = f.read(); return json.loads(raw) if raw else None
a = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw}); tok, uid = a["AccessToken"], a["User"]["Id"]
views = call("GET", f"/UserViews?userId={uid}", tok=tok)["Items"]
picks = call("GET", f"/Users/{uid}/Items?ParentId={views[0]['Id']}&Limit=2&StartIndex=6", tok=tok)["Items"]
show = call("GET", f"/Users/{uid}/Items?ParentId={views[1]['Id']}&Limit=1&StartIndex=0", tok=tok)["Items"][0]
picks += [e for e in call("GET", f"/Shows/{show['Id']}/Episodes?userId={uid}&Limit=3", tok=tok)["Items"]][1:2]
for it in picks:
    label = it["Name"] if it["Type"] != "Episode" else f"{it.get('SeriesName')} S{it.get('ParentIndexNumber')}E{it.get('IndexNumber')}"
    pi = call("POST", f"/Items/{it['Id']}/PlaybackInfo?UserId={uid}", {}, tok=tok)
    src = next(s for s in pi["MediaSources"] if s.get("Path"))
    t0 = time.time()
    # Le lecteur suit les redirections : on note seulement les hôtes traversés.
    hops, url = [], src["Path"]
    for _ in range(6):
        req = urllib.request.Request(url, method="GET", headers={"Range": "bytes=0-0", "User-Agent": "mpv"})
        opener = urllib.request.build_opener(type("NoRedirect", (urllib.request.HTTPRedirectHandler,), {"redirect_request": lambda *a, **k: None}))
        try:
            r = opener.open(req, timeout=60); status = r.status; loc = None
        except urllib.error.HTTPError as e:
            status, loc = e.code, e.headers.get("Location")
        hops.append(f"{urllib.parse.urlparse(url).netloc}:{status}")
        if loc and status in (301, 302, 303, 307, 308):
            url = urllib.parse.urljoin(url, loc); continue
        break
    resolve_s = time.time() - t0
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:stream_tags=language:format=duration", "-of", "json", url], capture_output=True, text=True, timeout=120)
    info = json.loads(probe.stdout or "{}")
    streams = [f"{s['codec_type'][0]}:{s.get('codec_name')}{'/'+s['tags']['language'] if s.get('tags',{}).get('language') else ''}{' '+str(s.get('height'))+'p' if s.get('height') else ''}" for s in info.get("streams", []) if s["codec_type"] in ("video", "audio")]
    t1 = time.time()
    dec = subprocess.run(["ffmpeg", "-v", "error", "-ss", "600", "-i", url, "-t", "8", "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"], capture_output=True, text=True, timeout=300)
    print(f"{label[:34]:34} | {' → '.join(hops)} | lien {resolve_s:.1f}s | {', '.join(streams[:5])} | durée {float(info.get('format',{}).get('duration',0))/60:.0f} min | décodage 8 s à 10:00 : {'OK' if dec.returncode == 0 else 'ÉCHEC ' + dec.stderr[-120:]} ({time.time()-t1:.0f}s)")
