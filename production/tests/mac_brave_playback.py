"""Parcours réel depuis le Mac (Brave sans tête, profil jetable, son coupé) sur l'adresse publique :
connexion, « Qui regarde ? », teaser, Lecture d'un film TorBox, reprise, épisode puis épisode suivant."""
import json, subprocess, sys, time
from playwright.sync_api import sync_playwright

URL = "https://sagora.walter-ai.cloud/"
UUID = open("/apps/sagora/production/data/famille-uuid").read().strip()
PW = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
OUT = "/apps/sagora/production/tests/out/"
VIDEO = """() => { const v=document.querySelector('video[data-ui=video]'); if(!v) return null; let host=''; try{host=new URL(v.currentSrc).host}catch{}
  return {host, t:Math.round(v.currentTime*10)/10, paused:v.paused, err:v.error&&v.error.code, w:v.videoWidth, h:v.videoHeight,
  audio:(v.audioTracks? v.audioTracks.length : null), dur:Math.round(v.duration/60)}; }"""
TOASTS = "() => [...document.querySelectorAll('[data-sonner-toast]')].map(e=>e.innerText)"

def go(page, h):
    page.evaluate("h => { location.hash = h.replace(/^#/, ''); }", h)

def play_and_watch(page, label, seconds=40):
    seen = []; start = None
    for i in range(seconds // 2):
        page.wait_for_timeout(2000)
        v = page.evaluate(VIDEO); t = page.evaluate(TOASTS); seen += [x for x in t if x not in seen]
        err = page.query_selector("[data-ui=player-error]")
        if err: print(f"  {label}: ERREUR affichée →", err.inner_text()[:160]); return v, seen
        if v and v["w"] and not v["paused"] and v["t"] > (start or 0) + 4: break
        if v and start is None: start = v["t"]
    print(f"  {label}: {json.dumps(v, ensure_ascii=False)} | notifications: {seen}")
    return v, seen

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    ctx = b.new_context(viewport={"width": 1600, "height": 900}, locale="fr-FR")
    page = ctx.new_page(); errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    t0 = time.time(); page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=60000)
    print("ouverture → écran de connexion :", round(time.time() - t0, 1), "s |", page.url)
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(PW)
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    print("Qui regarde ? :", [x.replace("\n", " ") for x in page.locator("[data-ui=user-picker-user]").all_inner_texts()])
    t0 = time.time(); page.locator("[data-ui=user-picker-user]", has_text="Lucas").first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    print("profil → accueil :", round(time.time() - t0, 1), "s")
    page.wait_for_timeout(9000)
    print("teaser du bandeau en lecture :", page.evaluate("() => !!document.querySelector('[data-ui=hero] [data-ui=teaser][data-playing]')"),
          "| couleur :", page.evaluate("() => document.documentElement.hasAttribute('data-title-accent') && getComputedStyle(document.documentElement).getPropertyValue('--title-accent')"))
    page.screenshot(path=OUT + "mac-home.png")
    # Série : épisode puis passage au suivant
    series = sys.argv[1]
    go(page, f"#/item/{series}"); page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000)
    page.locator("[data-ui=item-action][data-name=play]").click()
    v, _ = play_and_watch(page, "Mentalist")
    title = lambda: page.evaluate("() => document.title")
    before = title()
    page.evaluate("() => { const v=document.querySelector('video[data-ui=video]'); v.currentTime = v.duration - 4; }")
    page.wait_for_timeout(25000)
    print("  fin d'épisode :", before, "→", title(), "|", json.dumps(page.evaluate(VIDEO)))
    page.screenshot(path=OUT + "mac-next-episode.png")
    print("erreurs JS :", errors[:3])
    ctx.close()
