"""Son des teasers activé par défaut (Monsieur, 2026-11-05) : sans toucher au bouton de son, le teaser de la fiche
monte progressivement en volume une fois visible. Après un rechargement sans clic ni touche, le navigateur
interdit le son : le teaser joue muet (bouton barré), puis le son arrive à la première touche.
Usage : browser_teaser_sound_default.py [id du titre] [profil]"""
import sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID
from browser_teaser_sound_full import LISTEN, go, wait_shown, merged

ITEM = sys.argv[1] if len(sys.argv) > 1 else "a11201000000056a60ffffffff000000"  # Coco
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "Invité"


def ramp(page, since_ms=0):
    seen, out = set(), []
    for e in merged(page):
        if e["ms"] >= since_ms and e["v"] is not None and (e["v"], e["m"]) not in seen:
            seen.add((e["v"], e["m"])); out.append((round(e["ms"] / 1000, 1), e["v"], e["m"]))
    return out


def button(page):
    b = page.locator("[data-ui=teaser-sound]")
    return "absent" if not b.count() else ("barré" if b.first.get_attribute("data-muted") else "son")


with sync_playwright() as p:
    b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)

    page.evaluate(LISTEN)
    go(page, f"#/item/{ITEM}")
    shown = wait_shown(page)
    page.wait_for_timeout(4500)
    print("1. après clics : visible après", shown, "s ; bouton :", button(page))
    print("   volume (s, volume, coupé) :", ramp(page)[:14])

    page.reload(); page.wait_for_timeout(3000)
    if page.locator("[data-ui=user-picker-user]").count():
        print("   (rechargement : choix du profil redemandé, test sans clic impossible)")
    else:
        page.evaluate(LISTEN)
        go(page, f"#/item/{ITEM}")
        shown = wait_shown(page)
        page.wait_for_timeout(3000)
        r = ramp(page)
        print("2. rechargé sans clic : visible après", shown, "s ; bouton :", button(page), "; son entendu :",
              any(m is False and (v or 0) > 0 for _, v, m in r), "; joue :", page.evaluate("() => !!document.querySelector('[data-ui=teaser][data-playing]')"))
        t_key = page.evaluate("() => performance.now()")
        page.keyboard.press("Shift")
        page.wait_for_timeout(4500)
        print("3. après une touche : bouton :", button(page), "; volume :", ramp(page)[-8:])
    print("erreurs JS:", errors[:5])
    b.close()
