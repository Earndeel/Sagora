"""Depuis le Mac (Brave sans tête) : menus Langue et Sous-titres du lecteur, son réellement décodé, changement de langue."""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
URL = "https://sagora.walter-ai.cloud/"
UUID = open("/apps/sagora/production/data/famille-uuid").read().strip()
PW = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
TITLE = sys.argv[1] if len(sys.argv) > 1 else "Coco"
OUT = "/apps/sagora/production/tests/out/"
V = """() => { const v=document.querySelector('video[data-ui=video]'); if(!v) return null;
  return {t:Math.round(v.currentTime), w:v.videoWidth, son_décodé:v.webkitAudioDecodedByteCount||0, err:v.error&&v.error.code,
  pistes_texte:[...v.textTracks].filter(t=>t.mode==='showing').map(t=>t.label.slice(0,30))}; }"""
def menu(page, name):
    page.mouse.move(800, 450); page.mouse.move(820, 460); page.wait_for_timeout(600)
    b = page.locator(f"[data-ui=player-controls] [data-name={name}]").first
    if not b.count(): return None
    b.click(force=True); page.wait_for_timeout(800)
    page.screenshot(path=OUT + f"menu-{name}.png")
    items = page.evaluate("() => [...document.querySelectorAll('[role=menu] [role], [data-radix-menu-content] [role], [data-ui=player-menu] button')].map(e=>e.getAttribute('role')+':'+e.innerText.replace(/\\n/g,' · ')).slice(0,20)")
    return [i.replace("\n", " · ") for i in items]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    ctx = b.new_context(viewport={"width": 1600, "height": 900}, locale="fr-FR"); page = ctx.new_page()
    page.goto(URL); page.wait_for_selector("input", timeout=60000)
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(PW)
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text="Lucas").first.click(); page.wait_for_selector("[data-ui=hero]", timeout=60000)
    href = page.locator("[data-ui=media-row] a[href]", has_text=TITLE).first.get_attribute("href")
    page.evaluate("h => { location.hash = h.replace(/^#/, ''); }", href)
    page.wait_for_selector("[data-ui=item-action][data-name=play]", timeout=60000)
    page.locator("[data-ui=item-action][data-name=play]").click()
    for _ in range(20):
        page.wait_for_timeout(2000); v = page.evaluate(V)
        if v and v["t"] > 5: break
    print("lecture :", json.dumps(v, ensure_ascii=False))
    page.mouse.move(800, 450); page.mouse.move(830, 470); page.wait_for_timeout(500); page.screenshot(path=OUT + "controls.png")
    print("boutons :", page.evaluate("() => [...document.querySelectorAll('[data-ui=player-button]')].map(b=>b.dataset.name)"))
    print("menu Langue :", menu(page, "language")); page.keyboard.press("Escape"); page.wait_for_timeout(400)
    subs = menu(page, "subtitles"); print("menu Sous-titres :", subs[:8] if subs else subs)
    if subs and len(subs) > 1:
        page.locator("[role=menuitemradio], [role=option]").nth(1).click(); page.wait_for_timeout(6000)
        print("après choix d'un sous-titre :", json.dumps(page.evaluate(V), ensure_ascii=False))
    page.screenshot(path=OUT + "mac-subtitles.png")
    langs = menu(page, "language")
    if langs and len(langs) > 1:
        other = [l for l in langs if not l.startswith("Français")]
        if other:
            page.locator("[role=menuitemradio], [role=option]", has_text=other[0].split(" · ")[0]).first.click()
            for _ in range(15):
                page.wait_for_timeout(2000); v2 = page.evaluate(V)
                if v2 and v2["t"] > 5 and v2["w"]: break
            print(f"après Langue → {other[0].split(' · ')[0]} :", json.dumps(v2, ensure_ascii=False))
    ctx.close()
