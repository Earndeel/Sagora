"""Mode « Suit la carte sélectionnée » (celui des TV) piloté au clavier comme une télécommande :
le bandeau suit la carte, son teaser démarre, la couleur suit, une seule vidéo à la fois."""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app

UUID = open("/apps/sagora/production/data/test-repli-uuid").read().strip()
PW = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Test", "password"], capture_output=True, text=True).stdout.strip()
OUT = "/apps/sagora/production/tests/out/"
STATE = """() => ({title: document.querySelector('[data-follow] [data-ui=hero-logo]')?.alt || document.querySelector('[data-follow] [data-ui=hero-title]')?.innerText,
  teaser: !!document.querySelector('[data-ui=teaser][data-playing]'), frames: document.querySelectorAll('[data-ui=teaser-embed]').length,
  accent: getComputedStyle(document.documentElement).getPropertyValue('--title-accent').trim(), focus: document.activeElement?.getAttribute('aria-label') || document.activeElement?.innerText?.slice(0,30)})"""

def go(page, h):
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", h)

with sync_playwright() as p:
    b, page, errors = open_app(p, width=1920, height=1080)
    page.add_init_script("""window.__yt=[];addEventListener('message',e=>{if(String(e.origin).includes('youtube'))try{const d=JSON.parse(e.data);if(['onError','onReady'].includes(d.event)||d.event==='infoDelivery'&&d.info&&d.info.playerState!==undefined)__yt.push([Math.round(performance.now()/100)/10,d.event,JSON.stringify(d.info).slice(0,40)])}catch{}})""")
    page.reload()
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(PW)
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    go(page, "#/settings?tab=interface"); page.wait_for_timeout(2500)
    page.locator("xpath=//label[normalize-space()='Bannière à la une']/following::button[1]").click(); page.wait_for_timeout(500)
    page.get_by_role("option", name="Suit la carte sélectionnée", exact=True).click(); page.wait_for_timeout(1500)
    go(page, "#/"); page.wait_for_selector("[data-follow]", timeout=30000); page.wait_for_timeout(1500)
    page.locator("[data-ui=media-row] a[href]").first.focus()
    page.keyboard.press("ArrowRight"); page.wait_for_timeout(300); page.keyboard.press("ArrowLeft")
    seen = []
    for step in range(3):
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(9000)
        s = page.evaluate(STATE); seen.append(s); print("carte", step + 1, json.dumps(s, ensure_ascii=False))
        print("   yt:", page.evaluate("() => { const x = window.__yt; window.__yt = []; return x.slice(-8); }"))
    page.screenshot(path=OUT + "follow-tv.png")
    go(page, "#/settings?tab=interface"); page.wait_for_timeout(2000)
    page.locator("xpath=//label[normalize-space()='Bannière à la une']/following::button[1]").click(); page.wait_for_timeout(500)
    page.get_by_role("option", name="Fait défiler les titres à la une", exact=True).click(); page.wait_for_timeout(1000)
    print("erreurs JS:", errors[:3])
    b.close()
