"""Qualité qui suit le débit (MAC=1 : Brave sans tête du Mac par le tunnel CDP :9333, qui lit le H.264/AAC) : connexion bridée pendant la lecture → passage seul à une version plus légère,
au même endroit ; puis la lecture suivante démarre directement sur une version sous le débit retenu.
Usage : browser_adaptive.py [id du titre] [profil] [débit en Mbit/s]"""
import json, sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

ITEM = sys.argv[1] if len(sys.argv) > 1 else "a11201000000056a60ffffffff000000"  # Coco
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "Invité"
MBPS = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

STATE = """() => { const v = document.querySelector('video');
  return { url: location.hash, t: v ? Math.round(v.currentTime) : null, paused: v ? v.paused : null,
           toasts: [...document.querySelectorAll('[data-sonner-toast]')].map(e => e.innerText.slice(0, 80)),
           cap: localStorage.getItem('sagora-adaptive-cap') } }"""


def source_of(hash_):
    return hash_.split("source=")[1].split("&")[0] if "source=" in hash_ else ""


with sync_playwright() as p:
    import os
    if os.environ.get("MAC") == "1":
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = b.new_context(viewport={"width": 1400, "height": 800}, locale="fr-FR").new_page(); errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type in ("error", "warning") and errors.append("console: " + m.text[:160]))
        page.goto("https://stremio.walter-ai.cloud/", wait_until="domcontentloaded")
    else:
        b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    page.evaluate("() => localStorage.removeItem('sagora-adaptive-cap')")
    cdp = page.context.new_cdp_session(page)
    cdp.send("Network.enable")
    if MBPS > 0:  # bridé dès le départ : pas de grosse réserve prise à pleine vitesse
        cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 40,
                 "downloadThroughput": MBPS * 1e6 / 8, "uploadThroughput": 1e6 / 8})
        print(f"connexion bridée à {MBPS} Mbit/s avant la lecture")
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", f"#/play/{ITEM}?source=")
    t0 = time.time()
    while time.time() - t0 < 90:
        s = page.evaluate(STATE)
        if s["t"] and s["t"] > 3: break
        page.wait_for_timeout(1000)
    first = page.evaluate(STATE)
    print("démarré :", json.dumps({k: first[k] for k in ("t", "paused")}), "| version", source_of(first["url"])[:12])
    if MBPS == 0:  # coupure franche de 14 s, puis retour
        cdp.send("Network.emulateNetworkConditions", {"offline": True, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
        print("connexion coupée 14 s"); page.wait_for_timeout(14000)
        print("pendant la coupure :", json.dumps(page.evaluate(STATE))[:200])
        cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})

    switched = None
    t1 = time.time()
    last = None
    while time.time() - t1 < 240:
        s = page.evaluate(STATE)
        line = (round(time.time() - t1), s["url"][-40:], s["t"], s["paused"], s["toasts"][:2])
        if line[1:] != last:
            print("   ", line); last = line[1:]
        if source_of(s["url"]) and source_of(s["url"]) != source_of(first["url"]):
            switched = s; break
        page.wait_for_timeout(1000 if time.time() - t1 < 30 else 5000)
    if switched:
        print(f"après {time.time() - t1:.0f}s : nouvelle version {source_of(switched['url'])[:12]} | position {switched['t']}s | "
              f"messages {switched['toasts']} | plafond retenu {switched['cap']}")
    else:
        print("pas de changement de version en 4 min ; état :", json.dumps(page.evaluate(STATE))[:300])
    print("erreurs JS:", errors[:8])
    b.close()
