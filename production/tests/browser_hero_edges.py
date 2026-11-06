"""Bords du teaser (MAC=1 : Brave du Mac) de l'accueil pendant son apparition (fondu) : captures rapprochées à partir du moment où il devient
visible, pour voir si les bords gauche et bas du cadre se montrent en traits nets.
Usage : browser_hero_edges.py [dossier de sortie] [profil]"""
import sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = sys.argv[1] if len(sys.argv) > 1 else "/apps/sagora/production/tests/out/edges"
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "Invité"
import os; os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    if os.environ.get("MAC") == "1":  # Brave sans tête du Mac (tunnel CDP :9333), qui lit vraiment les vidéos
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = b.new_context(viewport={"width": 1920, "height": 1080}, locale="fr-FR").new_page(); errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("https://stremio.walter-ai.cloud/jellyfin/web/", wait_until="domcontentloaded")
    else:
        b, page, errors = open_app(p, width=1920, height=1080)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    page.mouse.move(1900, 1070)
    t0 = time.time()
    while time.time() - t0 < 40 and not page.locator("[data-ui=hero] [data-ui=teaser][data-playing]").count():
        page.wait_for_timeout(50)
    print("teaser visible après", round(time.time() - t0, 1), "s")
    for i in range(10):
        page.screenshot(path=f"{OUT}/f{i:02d}.png", clip={"x": 0, "y": 0, "width": 1920, "height": 700}); page.wait_for_timeout(40)
    page.wait_for_timeout(1500); page.screenshot(path=f"{OUT}/after.png")
    print("transform du lecteur :", page.evaluate("() => document.querySelector('[data-ui=hero] [data-ui=teaser-embed]')?.style.transform"),
          "| cadre :", page.evaluate("() => { const r = document.querySelector('[data-ui=hero] [data-ui=teaser-embed]')?.parentElement.getBoundingClientRect(); return r && [Math.round(r.width), Math.round(r.height)]; }"))
    print("erreurs JS:", errors[:5])
    b.close()
