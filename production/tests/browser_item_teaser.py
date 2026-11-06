"""Teaser sur la page d'un titre : se lance seul, n'apparaît qu'une fois l'habillage YouTube parti et en HD (720p+).
Usage : browser_item_teaser.py [id du titre] [profil]"""
import json, sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
ITEM = sys.argv[1] if len(sys.argv) > 1 else "a11201000000056a60ffffffff000000"  # Coco
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "Invité"

PROBE = """() => {
  const t = document.querySelector('[data-ui=item-backdrop] [data-ui=teaser]');
  const f = document.querySelector('[data-ui=item-backdrop] [data-ui=teaser-embed]');
  return { mounted: !!t, playing: !!(t && t.hasAttribute('data-playing')), opacity: t ? getComputedStyle(t).opacity : null,
           embed: f ? { w: f.offsetWidth, h: f.offsetHeight, transform: f.style.transform } : null,
           sound: !!document.querySelector('[data-ui=teaser-sound]') };
}"""

with sync_playwright() as p:
    b, page, errors = open_app(p)
    yt = []
    page.on("console", lambda m: None)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    t0 = time.time()
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", f"#/item/{ITEM}")
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000)
    shown_at = None
    while time.time() - t0 < 25:
        s = page.evaluate(PROBE)
        el = round(time.time() - t0, 1)
        print(el, json.dumps(s))
        if s["playing"] and shown_at is None:
            shown_at = el
            page.screenshot(path=OUT + "item-teaser-reveal.png")
        if shown_at and el - shown_at > 3:
            page.screenshot(path=OUT + "item-teaser-after.png")
            break
        page.wait_for_timeout(700)
    print("teaser visible après", shown_at, "s ; erreurs JS:", errors[:3])
    b.close()
