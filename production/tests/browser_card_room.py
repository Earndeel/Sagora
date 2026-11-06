"""Aperçu d'une carte : les cartes voisines glissent de côté au lieu d'être recouvertes, puis reviennent à la fermeture.
MAC=1 : Brave du Mac (tunnel CDP :9333). Usage : browser_card_room.py [profil] [dossier de sortie]"""
import os, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

PROFILE = sys.argv[1] if len(sys.argv) > 1 else "Lucas"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/apps/sagora/production/tests/out"
os.makedirs(OUT, exist_ok=True)

MEASURE = """() => { const p = document.querySelector('[data-ui=card-preview]'); if (!p) return null;
  const pr = p.getBoundingClientRect();
  const items = [...p.ownerDocument.querySelectorAll('[data-ui=media-row-item]')].filter(el => {
    const r = el.getBoundingClientRect(); return r.bottom > pr.top && r.top < pr.bottom; });
  return { preview: [Math.round(pr.left), Math.round(pr.right)],
    covered: items.filter(el => { const r = el.getBoundingClientRect();
      return Math.min(r.right, pr.right) - Math.max(r.left, pr.left) > 2 && !el.contains(document.elementFromPoint(r.left + r.width / 2, r.top + 10)) && el.style.transform === ''; }).length,
    overlaps: items.map(el => { const r = el.getBoundingClientRect(); return Math.round(Math.max(0, Math.min(r.right, pr.right) - Math.max(r.left, pr.left))); }),
    moved: items.filter(el => el.style.transform).map(el => el.style.transform) } }"""

with sync_playwright() as p:
    if os.environ.get("MAC") == "1":
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = b.new_context(viewport={"width": 1600, "height": 900}, locale="fr-FR").new_page(); errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("https://stremio.walter-ai.cloud/jellyfin/web/", wait_until="domcontentloaded")
    else:
        b, page, errors = open_app(p)
    page.wait_for_selector("input")
    page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
    page.get_by_role("button", name="Se connecter").click()
    page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
    page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
    page.wait_for_selector("[data-ui=hero]", timeout=60000)
    page.wait_for_timeout(2500)
    rows = page.locator("[data-ui=media-row]")
    row = rows.nth(1); row.scroll_into_view_if_needed(); page.wait_for_timeout(800)
    card = row.locator("[data-ui=media-row-item]").nth(2)
    box = card.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 3)
    page.mouse.move(box["x"] + box["width"] / 2 + 3, box["y"] + box["height"] / 3 + 2)
    page.wait_for_timeout(1300)
    print("sous la souris :", page.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); return e && (e.closest('[data-ui]')?.dataset.ui + ' / ' + e.tagName); }", [box["x"] + box["width"] / 2, box["y"] + box["height"] / 3]), "| rangées :", rows.count(), "| carte :", box)
    m = page.evaluate(MEASURE)
    print("aperçu ouvert :", m and {k: m[k] for k in ("preview", "overlaps", "moved")})
    page.screenshot(path=f"{OUT}/card_room_open.png")
    page.mouse.move(5, 5); page.wait_for_timeout(600)
    left = page.evaluate("() => [...document.querySelectorAll('[data-ui=media-row-item]')].filter(el => el.style.transform).length")
    print("après fermeture : aperçu", page.locator("[data-ui=card-preview]").count(), "| cartes encore décalées", left)
    print("erreurs JS:", errors[:5])
    b.close()
