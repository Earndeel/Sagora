"""Bouton « Bandes-annonces » : ouvre toujours une vidéo en plein écran, jamais la liste.
- teaser en préparation (cliqué tout de suite) → ce teaser en plein écran ;
- pas de teaser (bandes-annonces sous 720p) → première bande-annonce en plein écran.
Usage : browser_trailer_button.py [profil] [id avec teaser HD] [id sans teaser]"""
import sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "Invité"
WITH_TEASER = sys.argv[2] if len(sys.argv) > 2 else "a11201000000056a60ffffffff000000"  # Coco
WITHOUT = sys.argv[3] if len(sys.argv) > 3 else None

STATE = """() => ({ full: document.fullscreenElement ? (document.fullscreenElement.dataset.ui || document.fullscreenElement.tagName) : null,
  sheet: !!document.querySelector('[data-name=trailers][role=dialog], [data-ui=trailers-list]'), url: location.hash })"""


def go(page, path):
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", path)


def click_trailer(page, item, wait_s):
    go(page, f"#/item/{item}")
    page.wait_for_selector("[data-ui=item-action][data-name=trailer]", timeout=60000)
    page.wait_for_timeout(wait_s * 1000)
    page.locator("[data-ui=item-action][data-name=trailer]").first.click()
    page.wait_for_timeout(4000)
    return page.evaluate(STATE)


with sync_playwright() as p:
    b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)

    s = click_trailer(page, WITH_TEASER, 2)
    print("teaser en préparation →", s)
    page.screenshot(path=OUT + "trailer-button-teaser.png")
    page.keyboard.press("Escape"); page.wait_for_timeout(1500)
    if page.evaluate("() => !!document.fullscreenElement"):
        page.evaluate("() => document.exitFullscreen()"); page.wait_for_timeout(1000)

    if WITHOUT:
        s = click_trailer(page, WITHOUT, 20)  # le temps que ses teasers sous 720p soient écartés
        print("sans teaser →", s)
        page.screenshot(path=OUT + "trailer-button-page.png")
        page.mouse.move(800, 450); page.wait_for_timeout(500)
        page.locator("[data-name=exit]").first.click(); page.wait_for_timeout(2500)
        print("retour →", page.evaluate(STATE))
    print("erreurs JS:", errors[:3])
    b.close()
