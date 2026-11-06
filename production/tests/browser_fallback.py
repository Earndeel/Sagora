"""Lecture réelle dans Chromium : version cassée en tête → repli automatique → vraie vidéo qui joue ; reprise ensuite."""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app

UUID = open("/apps/sagora/production/data/test-repli-uuid").read().strip()
PW = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Test", "password"], capture_output=True, text=True).stdout.strip()
VIDEO = "() => { const v=document.querySelector('video[data-ui=video]'); return v && {src:(v.currentSrc||'').split('/').pop().slice(0,40), t:Math.round(v.currentTime*10)/10, paused:v.paused, err:v.error&&v.error.code, w:v.videoWidth}; }"

with sync_playwright() as p:
    b, page, errors = open_app(p)
    toasts = []
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(PW)
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    href = page.locator("[data-ui=media-row] a[href]").nth(int(sys.argv[1]) if len(sys.argv) > 1 else 1).get_attribute("href")
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", href)
    print("fiche:", href)
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000)
    item_url = page.url
    title = page.evaluate("() => document.querySelector('[data-ui=item-logo]')?.alt || document.title")
    page.locator("[data-ui=item-action][data-name=play]").click()
    for i in range(20):
        page.wait_for_timeout(1500)
        t = page.evaluate("() => [...document.querySelectorAll('[data-sonner-toast]')].map(e=>e.innerText)")
        toasts += [x for x in t if x not in toasts]
        v = page.evaluate(VIDEO)
        print(f"{(i+1)*1.5:>5}s", v, "| erreur affichée:" , bool(page.query_selector("[data-ui=player-error]")))
        if v and v["t"] and v["t"] > 6: break
    print("titre:", title, "| notifications:", toasts)
    page.screenshot(path="/apps/sagora/production/tests/out/fallback-playing.png")
    pos = page.evaluate(VIDEO)["t"]
    page.goto(item_url); page.wait_for_timeout(4000)
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=30000)
    label = page.locator("[data-ui=item-action][data-name=play]").inner_text()
    print("bouton après arrêt à", pos, "s :", label)
    page.locator("[data-ui=item-action][data-name=play]").click()
    page.wait_for_timeout(6000)
    print("reprise:", page.evaluate(VIDEO))
    print("erreurs JS:", errors[:5])
    b.close()
