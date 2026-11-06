#!/usr/bin/env python3
"""Icônes Sagora à partir de sagora.svg (symbole crème, fond transparent) :
logo.png (transparent, comme l'ancien logo d'AIOStreams), puis favicon / icône Apple / icônes d'appli
sur fond #070707 (couleur de l'app). Relancer après un changement de sagora.svg."""
import io, os, re, subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BG = "#070707"
src = open(os.path.join(HERE, "sagora.svg")).read()
vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
path = re.search(r"<path[^>]*/>", src, re.S).group(0)


def svg(size, mark_share, background):
    """Le symbole centré, sa hauteur = mark_share × size."""
    x0, y0, w, h = vb
    scale = size * mark_share / h
    tx = (size - w * scale) / 2 - x0 * scale
    ty = (size - h * scale) / 2 - y0 * scale
    bg = f'<rect width="{size}" height="{size}" fill="{background}"/>' if background else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'<title>Sagora</title>{bg}<g transform="translate({tx:.2f} {ty:.2f}) scale({scale:.5f})">{path}</g></svg>')


def png(svg_text, size):
    out = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-f", "png"],
                         input=svg_text.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGBA")


def save(name, data):
    with open(os.path.join(HERE, name), "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


# Logo de l'interface : symbole seul, transparent (barre latérale, connexion, page de configuration).
png(svg(512, 0.96, None), 512).save(os.path.join(HERE, "logo.png"))
# Icône vectorielle des onglets, et versions bitmap.
icon_svg = svg(512, 0.70, BG)
save("icon0.svg", icon_svg)
png(icon_svg, 180).save(os.path.join(HERE, "apple-icon.png"))
# Icônes d'appli : « maskable » garde le symbole dans la zone sûre (80 % central).
png(svg(512, 0.60, BG), 192).save(os.path.join(HERE, "web-app-manifest-192x192.png"))
png(svg(512, 0.60, BG), 512).save(os.path.join(HERE, "web-app-manifest-512x512.png"))
png(icon_svg, 256).save(os.path.join(HERE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
save("manifest.json", """{
  "name": "Sagora",
  "short_name": "Sagora",
  "icons": [
    { "src": "/web-app-manifest-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/web-app-manifest-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/web-app-manifest-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
    { "src": "/web-app-manifest-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "theme_color": "#070707",
  "start_url": ".",
  "background_color": "#070707",
  "display": "standalone"
}
""")
# Vignette du lanceur du dongle TV (tuile 366×166, ×3) : symbole + nom, police Inter (OFL) de l'interface.
from PIL import ImageDraw, ImageFont
W, H = 1098, 498
banner = Image.new("RGBA", (W, H), BG)
side = 330
mark = png(svg(side, 0.98, None), side)
font = ImageFont.truetype(os.path.join(HERE, "inter-600.woff2"), 170)
text = "Sagora"
x0, y0, x1, y1 = font.getbbox(text)
mark_w = round(side * vb[2] / vb[3])  # largeur réelle du symbole dans son carré
gap = 40
total = mark_w + gap + (x1 - x0)
left = (W - total) // 2
banner.alpha_composite(mark, (left - (side - mark_w) // 2, (H - side) // 2))
ImageDraw.Draw(banner).text((left + mark_w + gap - x0, (H - (y1 - y0)) // 2 - y0), text, font=font, fill="#FAF7F2")
banner.convert("RGB").save(os.path.join(HERE, "tv-banner.png"))
print("ok:", sorted(os.listdir(HERE)))
