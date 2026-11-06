"""Parcours des teasers et couleurs dynamiques sur l'accueil (desktop, souris)."""
import json, sys
from playwright.sync_api import sync_playwright
from browser_login import open_app, password, UUID

OUT = "/apps/sagora/production/tests/out/"
STATE = """() => ({
  heroTeaser: !!document.querySelector('[data-ui=hero] [data-ui=teaser][data-playing]'),
  previewTeaser: !!document.querySelector('[data-ui=card-preview] [data-ui=teaser][data-playing]'),
  frames: document.querySelectorAll('[data-ui=teaser-embed], [data-ui=teaser-video]').length,
  preview: !!document.querySelector('[data-ui=card-preview]'),
  sound: [...document.querySelectorAll('[data-ui=teaser-sound]')].map(b => b.getAttribute('aria-label')),
  accent: document.documentElement.hasAttribute('data-title-accent') ? getComputedStyle(document.documentElement).getPropertyValue('--title-accent').trim() : null,
  playBg: (() => { const b = document.querySelector('[data-ui=hero-action][data-name=play]'); return b && getComputedStyle(b).backgroundColor; })(),
  title: document.querySelector('[data-ui=hero-logo]')?.alt || document.querySelector('[data-ui=hero-title]')?.innerText || null,
})"""

if __name__ == "__main__":
  with sync_playwright() as p:
      b, page, errors = open_app(p)
      page.wait_for_selector("input")
      page.locator("input").nth(0).fill(UUID)
      page.locator("input[type=password]").fill(password())
      page.get_by_role("button", name="Se connecter").click()
      # Écran « Qui regarde ? » depuis les profils natifs.
      page.wait_for_selector("[data-ui=user-picker-user]", timeout=60000)
      page.locator("[data-ui=user-picker-user]", has_text=sys.argv[1] if len(sys.argv) > 1 else "Invité").first.click()
      page.wait_for_selector("[data-ui=hero]", timeout=60000)
      page.mouse.move(5, 890)
      page.wait_for_timeout(1500)
      s0 = page.evaluate(STATE); print("t+1.5s", json.dumps(s0, ensure_ascii=False))
      page.screenshot(path=OUT + "home-image.png")
      page.wait_for_timeout(9000)
      s1 = page.evaluate(STATE); print("t+10s ", json.dumps(s1, ensure_ascii=False))
      page.screenshot(path=OUT + "home-teaser.png")
      # Survol d'une carte : la prévisualisation prend la main sur le bandeau.
      card = page.locator("[data-ui=media-row] a[href]").nth(4)
      card.scroll_into_view_if_needed()
      box = card.bounding_box()
      page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
      page.mouse.move(box["x"] + box["width"] / 2 + 3, box["y"] + box["height"] / 2 + 2)
      page.wait_for_timeout(12000)
      s2 = page.evaluate(STATE); print("survol", json.dumps(s2, ensure_ascii=False))
      page.screenshot(path=OUT + "card-teaser.png")
      page.mouse.move(5, 5)
      page.wait_for_timeout(1500)
      s3 = page.evaluate(STATE); print("sortie", json.dumps(s3, ensure_ascii=False))
      print("erreurs JS:", errors[:5])
      b.close()
