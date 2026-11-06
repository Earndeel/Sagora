"""Langue par profil : la langue de l'interface d'un profil change aussi titres, résumés et bandes-annonces,
sans toucher les autres profils. Passe « Invité » en anglais le temps du test puis remet le français."""
import json, re, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "Invité"


def go(page, path):
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", path)


def pick(page, name):
    page.locator("[data-ui=user-picker-user]", has_text=name).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)


def item_state(page, href):
    go(page, href)
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000)
    page.wait_for_timeout(2500)
    return page.evaluate("""() => ({
      title: document.querySelector('[data-ui=item-logo]')?.alt || document.querySelector('[data-ui=item-title]')?.innerText || null,
      overview: (document.querySelector('[data-ui=overview-text]')?.innerText || document.querySelector('[data-ui=overview]')?.innerText || '').slice(0, 120),
    })""")


def set_language(page, label):
    go(page, "#/settings?tab=interface")
    page.wait_for_timeout(2500)
    select = page.locator("[data-ui=settings-card][data-name=language] button").first
    select.click()
    option = page.get_by_role("option", name=label).first
    option.scroll_into_view_if_needed()
    option.focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(2500)


with sync_playwright() as p:
    b, page, errors = open_app(p)
    sent = []
    page.on("request", lambda r: "/jellyfin/" in r.url and "/web/" not in r.url and sent.append(r.headers.get("x-aiostreams-language")))
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    pick(page, PROFILE)
    href = page.locator("[data-ui=media-row] a[href*='/item/']").nth(1).get_attribute("href")
    before = item_state(page, href)
    print("fr      ", json.dumps(before, ensure_ascii=False), "| en-tête:", sorted(set(filter(None, sent))))
    try:
        sent.clear()
        set_language(page, re.compile(r"English"))
        after = item_state(page, href)
        page.screenshot(path=OUT + "profile-language-en.png")
        print("anglais ", json.dumps(after, ensure_ascii=False), "| en-tête:", sorted(set(filter(None, sent))))
    finally:
        set_language(page, re.compile(r"^Français$"))
    back = item_state(page, href)
    print("retour  ", json.dumps(back, ensure_ascii=False))
    print("erreurs JS:", errors[:3])
    b.close()
