"""Make the web logo assets from the original in docs/brand/ (trim transparent margin, square it, resize).
Usage: python src/make_logo_assets.py            (reads docs/brand/sinkronized-logo-original.png)
Outputs in web/assets/: logo.png (header, 4x), logo-512.png, favicon-32.png, apple-touch-icon.png (180, ivory background: iOS ignores transparency)."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{ROOT}/docs/brand/sinkronized-logo-original.png"; OUT = f"{ROOT}/web/assets"; os.makedirs(OUT, exist_ok=True)
IVORY = (244, 239, 230, 255)   # --canvas in web/styles.css

def remove_white_background(img):
    """If the logo has no transparency (opaque white page around the emblem), make that white transparent.
    Only near-white pixels CONNECTED to the image border are removed, so cream and highlights inside the emblem stay.
    A one-pixel band next to the cleared area is half-transparent, which avoids a white fringe."""
    import numpy as np
    from scipy import ndimage
    px = np.array(img.convert("RGBA")); rgb = px[..., :3].astype(int)
    white = (rgb.min(axis=2) >= 238) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 14)
    lab, _ = ndimage.label(white)
    edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge_labels))
    band = ndimage.binary_dilation(bg, iterations=1) & ~bg
    px[..., 3] = 255; px[bg, 3] = 0; px[band, 3] = 120
    return Image.fromarray(px, "RGBA")

im = Image.open(SRC)
if im.convert("RGBA").getchannel("A").getextrema()[0] == 255:      # fully opaque: remove the white page
    im = remove_white_background(im)
im = im.convert("RGBA")
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
