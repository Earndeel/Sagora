"""Bouton rond « Versions » de la fiche (à côté de « Bandes-annonces ») : ouvre la liste des versions (sources) à choisir.
Usage : browser_versions_button.py [profil] [id…]"""
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "Invité"
ITEMS = sys.argv[2:] or ["a11201000000056a60ffffffff000000"]  # Coco

with sync_playwright() as p:
    b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    for n, item in enumerate(ITEMS):
        page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", f"#/item/{item}")
        page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000); page.wait_for_timeout(1500)
        order = page.evaluate("() => [...document.querySelectorAll('[data-ui=item-action]')].filter(e => e.offsetParent).map(e => e.dataset.name)")
        print(item, "boutons :", order)
        page.locator("[data-ui=item-action][data-name=versions]").first.click()
        page.wait_for_selector("[data-ui=version]", timeout=90000); page.wait_for_timeout(1000)
        names = page.locator("[data-ui=version-name]").all_inner_texts()
        print("  versions :", len(names), "|", [x.replace("\n", " ")[:60] for x in names[:3]])
        page.screenshot(path=OUT + f"versions-button-{n}.png")
        page.keyboard.press("Escape"); page.wait_for_timeout(1000)
    print("erreurs JS:", errors[:3])
    b.close()
