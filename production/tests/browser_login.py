"""Ouvre l'app AIOStreams de préproduction dans Chromium (sorties externes par la sortie Walter :1083), connecte « Famille »."""
import subprocess, time
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:18090"
UUID = open("/apps/sagora/production/data/famille-uuid").read().strip()


def password():
    return subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"],
                          capture_output=True, text=True, check=True).stdout.strip()


def open_app(p, width=1600, height=900, **kw):
    # Sorties externes (YouTube, images TMDB) par la sortie navigateur Walter, jamais l'IP de la VM.
    browser = p.chromium.launch(args=["--proxy-server=socks5://127.0.0.1:1083", "--proxy-bypass-list=127.0.0.1;localhost",
                                      "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": width, "height": height}, locale="fr-FR", **kw)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(BASE + "/jellyfin/web/", wait_until="domcontentloaded")
    return browser, page, errors


def login(page):
    page.wait_for_timeout(3000)
    inputs = page.locator("input")
    return [(inputs.nth(i).get_attribute("type"), inputs.nth(i).get_attribute("name"), inputs.nth(i).get_attribute("placeholder")) for i in range(inputs.count())]


if __name__ == "__main__":
    with sync_playwright() as p:
        b, page, errors = open_app(p)
        print(login(page))
        print(page.url)
        page.screenshot(path="/apps/sagora/production/tests/out/login.png")
        print("errors", errors[:3])
        b.close()
