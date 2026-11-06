"""Teaser du bandeau sur téléphone (tactile) et bouton son."""
import json
from playwright.sync_api import sync_playwright
from browser_login import open_app, password, UUID
from browser_teasers import STATE

with sync_playwright() as p:
    b, page, errors = open_app(p, width=390, height=844, is_mobile=True, has_touch=True, device_scale_factor=2)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    page.wait_for_timeout(10000)
    print("mobile t+10s", json.dumps(page.evaluate(STATE), ensure_ascii=False))
    btn = page.locator("[data-ui=teaser-sound]")
    if btn.count():
        btn.first.tap(); page.wait_for_timeout(500)
        print("après appui son:", btn.first.get_attribute("aria-label"))
    page.screenshot(path="/apps/sagora/production/tests/out/mobile.png")
    print("erreurs JS:", errors[:5])
    b.close()
