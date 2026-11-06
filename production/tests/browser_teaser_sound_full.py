"""Teaser de la fiche : silencieux tant qu'il est caché, son qui monte progressivement une fois visible ;
« Bandes-annonces » passe ce même lecteur en plein écran sans repartir du début.
Usage : browser_teaser_sound_full.py [id du titre] [profil]"""
import json, sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/apps/sagora/production/tests")
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
ITEM = sys.argv[1] if len(sys.argv) > 1 else "a11201000000056a60ffffffff000000"  # Coco
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "Invité"

# Ce que le lecteur YouTube annonce (volume, coupé, position), horodaté côté page.
LISTEN = """() => { window.__yt = []; const t0 = performance.now();
  addEventListener('message', e => { if (!String(e.origin).includes('youtube')) return;
    try { const d = JSON.parse(e.data); const i = d.info || {};
      if (typeof i === 'object' && (i.volume != null || i.muted != null || i.currentTime != null))
        window.__yt.push({ ms: Math.round(performance.now() - t0), v: i.volume, m: i.muted, t: i.currentTime }); } catch {} }); }"""
STATE = """() => { const t = document.querySelector('[data-ui=item-backdrop] [data-ui=teaser], [data-ui=teaser][data-full]');
  return { playing: !!(t && t.hasAttribute('data-playing')), full: !!document.fullscreenElement && document.fullscreenElement === t }; }"""


def go(page, path):
    page.evaluate("h => { history.pushState({}, '', h); dispatchEvent(new PopStateEvent('popstate')); }", path)


def wait_shown(page, limit=30):
    t0 = time.time()
    while time.time() - t0 < limit:
        if page.evaluate(STATE)["playing"]:
            return round(time.time() - t0, 1)
        page.wait_for_timeout(300)
    return None


def merged(page):
    """Volume / coupé / position connus à chaque message (YouTube n'envoie que ce qui change)."""
    out, cur = [], {"v": None, "m": None, "t": None}
    for e in page.evaluate("window.__yt"):
        for k in ("v", "m", "t"):
            if e.get(k) is not None:
                cur[k] = e[k]
        out.append({"ms": e["ms"], **cur})
    return out


if __name__ == "__main__":
  with sync_playwright() as p:
      b, page, errors = open_app(p)
      page.wait_for_selector("input")
      page.locator("input").nth(0).fill(UUID); page.locator("input[type=password]").fill(password())
      page.get_by_role("button", name="Se connecter").click()
      page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
      page.locator("[data-ui=user-picker-user]", has_text=PROFILE).first.click()
      page.wait_for_selector("[data-ui=hero]", timeout=60000)

      # 1. Un premier passage sur la fiche (le son est activé par défaut depuis le 2026-11-05), puis l'accueil.
      go(page, f"#/item/{ITEM}")
      print("1er affichage après", wait_shown(page), "s")
      go(page, "#/"); page.wait_for_timeout(2000)

      # 2. Revenir sur la fiche : son coupé tant que caché, puis montée progressive.
      page.evaluate(LISTEN)
      t_nav = time.time()
      go(page, f"#/item/{ITEM}")
      shown = wait_shown(page)
      page.wait_for_timeout(4000)
      log = merged(page)
      shown_ms = (shown or 0) * 1000
      before = [e for e in log if e["ms"] < shown_ms - 500]
      loud_before = [e for e in before if e["m"] is False and (e["v"] or 0) > 0]
      print("2e affichage après", shown, "s ; messages avant affichage :", len(before), "dont avec son :", len(loud_before))
      after = [e for e in log if e["ms"] >= shown_ms - 500]
      vols = [(round(e["ms"] / 1000, 1), e["v"], e["m"]) for e in after if e["v"] is not None]
      seen, ramp = set(), []
      for x in vols:
          if x[1] not in seen:
              seen.add(x[1]); ramp.append(x)
      print("volume après affichage (s, volume, coupé) :", ramp[:25])

      # 3. Bandes-annonces → plein écran, même lecteur, sans repartir de zéro.
      before_t = merged(page)[-1]["t"]
      page.locator("[data-ui=item-action][data-name=trailer]").first.click()
      page.wait_for_timeout(2500)
      st = page.evaluate(STATE)
      last = merged(page)[-1]
      print("plein écran :", st["full"], "| position avant clic", before_t, "→ après", last["t"], "| volume", last["v"], "coupé", last["m"],
            "| page :", page.url.split("#")[-1])
      page.screenshot(path=OUT + "teaser-full.png")
      page.locator("[data-ui=teaser-full-controls]").click(position={"x": 400, "y": 400}); page.wait_for_timeout(1500)
      print("pause au clic :", page.locator("[data-ui=teaser-full-controls] svg").count() > 1)
      page.locator("[data-ui=teaser-full-close]").click(); page.wait_for_timeout(1500)
      print("sortie du plein écran :", page.evaluate("() => !document.fullscreenElement"), "| erreurs JS:", errors[:3])
      b.close()
