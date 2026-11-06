"""Profils : écran « Qui regarde ? », favori et accueil propres à chaque profil, changement de profil."""
import json, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"

def pick(page, name):
    page.locator("[data-ui=user-picker-user]", has_text=name).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)

def favourites(page):
    page.evaluate("() => { history.pushState({}, '', '#/favourites'); dispatchEvent(new PopStateEvent('popstate')); }")
    page.wait_for_timeout(4000)
    return page.evaluate("() => [...document.querySelectorAll('main a[href*=\"/item/\"], [data-page] a[href*=\"/item/\"]')].map(a=>a.getAttribute('href')).filter((v,i,s)=>s.indexOf(v)===i)")

with sync_playwright() as p:
    b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    print("profils proposés:", page.locator("[data-ui=user-picker-user]").all_inner_texts())
    pick(page, "Profil 2")
    href = page.locator("[data-ui=media-row] a[href]").nth(2).get_attribute("href")
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", href)
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000); page.wait_for_timeout(1500)
    print("actions:", page.evaluate("() => [...document.querySelectorAll('[data-ui=item-action],[data-ui=item-quick-action]')].map(e=>e.dataset.ui+':'+e.dataset.name+':'+(e.offsetParent?'visible':'hidden'))"))
    page.screenshot(path=OUT + "item-profile2.png")
    page.locator("[data-ui=item-action][data-name=favourite]").click(); page.wait_for_timeout(2000)
    print("Profil 2 favoris:", favourites(page))
    # Changement de profil sans se déconnecter
    page.evaluate("() => { history.pushState({}, '', '#/users'); dispatchEvent(new PopStateEvent('popstate')); }")
    page.wait_for_timeout(3000)
    if not page.locator("[data-ui=user-picker-user]").count():
        page.screenshot(path=OUT + "switch.png"); print("pas d'écran de choix à #/users :", page.url)
    else:
        pick(page, "Invité")
        print("Invité favoris:", favourites(page))
        page.evaluate("() => { history.pushState({}, '', '#/users'); dispatchEvent(new PopStateEvent('popstate')); }"); page.wait_for_timeout(3000)
        pick(page, "Profil 2")
        print("Profil 2 favoris (retour):", favourites(page))
    print("erreurs JS:", errors[:3])
    b.close()
