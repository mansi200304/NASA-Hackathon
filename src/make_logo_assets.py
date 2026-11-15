"""Make the web logo assets from the original in docs/brand/ (trim transparent margin, square it, resize).
Usage: python src/make_logo_assets.py            (reads docs/brand/sinkronized-logo-original.png)
Outputs in web/assets/: logo.png (header, 4x), logo-512.png, favicon-32.png, apple-touch-icon.png (180, ivory background: iOS ignores transparency)."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{ROOT}/docs/brand/sinkronized-logo-original.png"; OUT = f"{ROOT}/web/assets"; os.makedirs(OUT, exist_ok=True)
IVORY = (244, 239, 230, 255)   # --canvas in web/styles.css

im = Image.open(SRC).convert("RGBA")
bb = im.getchannel("A").getbbox(); im = im.crop(bb)
side = max(im.size); sq = Image.new("RGBA", (side, side), (0, 0, 0, 0)); sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
def save(img, name, size, bg=None):
    r = img.resize((size, size), Image.LANCZOS)
    if bg is not None:
        base = Image.new("RGBA", (size, size), bg); base.alpha_composite(r); r = base
    r.save(f"{OUT}/{name}", optimize=True); print(f"{name}: {size}x{size}, {os.path.getsize(f'{OUT}/{name}')/1024:.0f} KB")
save(sq, "logo.png", 192); save(sq, "logo-512.png", 512); save(sq, "favicon-32.png", 32)
# apple icon: logo at ~84% on the ivory canvas so the circle is not clipped by iOS rounding
pad = Image.new("RGBA", (side, side), (0, 0, 0, 0)); k = 0.84; inner = sq.resize((int(side * k), int(side * k)), Image.LANCZOS)
pad.paste(inner, ((side - inner.width) // 2, (side - inner.height) // 2), inner); save(pad, "apple-touch-icon.png", 180, IVORY)
