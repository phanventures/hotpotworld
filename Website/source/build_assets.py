#!/usr/bin/env python3
"""Turn the scraped hotpotworld.com originals into web-ready assets.
Run from the Website/ root:  python3 source/build_assets.py
"""
from PIL import Image, ImageOps
import numpy as np
import os, shutil

SRC = "source/originals"
OUT = "assets/img/web"
os.makedirs(OUT, exist_ok=True)

BRAND_RED = (0xC0, 0x26, 0x2E)


def save_web(im, name, width, quality=82):
    """Save a JPG at the given width (and a 2x if the source allows)."""
    im = im.convert("RGB")
    for suffix, w in ((f"{name}.jpg", width), (f"{name}@2x.jpg", width * 2)):
        if w > im.width * 1.05:
            continue
        c = im.copy()
        c.thumbnail((w, w * 4), Image.LANCZOS)
        c.save(os.path.join(OUT, suffix), "JPEG", quality=quality,
               optimize=True, progressive=True)
        print(f"  {suffix:34s} {c.width}x{c.height}  "
              f"{os.path.getsize(os.path.join(OUT, suffix))//1024}KB")


def crop_to(im, ratio):
    """Center-crop to an aspect ratio (w/h)."""
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        return im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    nh = int(w / ratio)
    return im.crop((0, (h - nh) // 2, w, (h + nh) // 2))


# ---------------------------------------------------------------- logo
print("logo")
logo = Image.open(f"{SRC}/44288403_1001146560068452_452057668819877888_n-2.jpg").convert("RGB")
a = np.array(logo).astype(np.int16)

# The source is red artwork on a pure-white field. Alpha = how far each pixel
# is from white, so the red edges stay anti-aliased instead of going jaggy.
dist = (255 - a).max(axis=2).astype(np.float32)
alpha = np.clip(dist * (255.0 / max(1.0, dist.max())), 0, 255).astype(np.uint8)

# Trim the transparent margin.
ys, xs = np.where(alpha > 8)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

# Red-on-transparent: flatten every opaque pixel to the exact brand red so the
# JPEG's colour noise doesn't survive into the logo.
rgba = np.dstack([
    np.full(alpha.shape, BRAND_RED[0], np.uint8),
    np.full(alpha.shape, BRAND_RED[1], np.uint8),
    np.full(alpha.shape, BRAND_RED[2], np.uint8),
    alpha,
])
Image.fromarray(rgba, "RGBA").crop(box).save(f"{OUT}/logo.png")

# White knockout for dark backgrounds.
rgba_w = rgba.copy()
rgba_w[..., :3] = 255
Image.fromarray(rgba_w, "RGBA").crop(box).save(f"{OUT}/logo-white.png")

for f in ("logo.png", "logo-white.png"):
    print(f"  {f:34s} {Image.open(os.path.join(OUT, f)).size}")

# ---------------------------------------------------------------- favicons
print("favicons")
mark = Image.open(f"{OUT}/logo.png")
side = max(mark.size)
sq = Image.new("RGBA", (side, side), (255, 255, 255, 0))
sq.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2), mark)
pad = int(side * 0.06)
sq = ImageOps.expand(sq, pad, (255, 255, 255, 0))

for size in (16, 32, 180, 192, 512):
    ic = sq.resize((size, size), Image.LANCZOS)
    if size in (180, 512):                      # opaque tiles want a backdrop
        bg = Image.new("RGBA", ic.size, (255, 255, 255, 255))
        bg.alpha_composite(ic)
        ic = bg
    ic.save(f"{OUT}/favicon-{size}.png")
sq.resize((64, 64), Image.LANCZOS).save(
    f"{OUT}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("  favicon set written")

# ---------------------------------------------------------------- photos
# name              source file                                     ratio  width
PHOTOS = [
    ("hero-spread",   "Hot-Pot-World-Rotary-23-min.jpg",             16 / 9, 1800),
    ("plates-color",  "DSC_7061.jpg",                                 3 / 2, 1200),
    ("plates-raw",    "DSC_7075-min.jpg",                             3 / 2, 1200),
    ("plates-meat",   "DSC_7080-1.jpg",                               3 / 2, 1200),
    ("dish-shrimp",   "Hot-Pot-World-Rotary-10-min-1.jpg",            4 / 3, 900),
    ("dish-seafood",  "Hot-Pot-World-Rotary-13-min-1.jpg",            4 / 3, 900),
    ("dish-teriyaki", "Hot-Pot-World-Rotary-14-min.jpg",              4 / 3, 900),
    ("dish-banhmi",   "Hot-Pot-World-Rotary-2-min-1.jpg",             4 / 3, 900),
    ("dish-padthai",  "Hot-Pot-World-Rotary-20-min-1.jpg",            4 / 3, 900),
    ("dish-friedrice", "Hot-Pot-World-Rotary-9-min-1.jpg",            4 / 3, 900),
    ("room-long",     "280293643_1957657547750677_7557624877628066889_n-e1704854625883.jpg", 4 / 3, 800),
    ("room-tables",   "323349009_716346863260525_3624565524912082488_n-e1704854641785.jpg",  4 / 3, 800),

    # Plated raw cuts, supplied 2026-08 (1024x1024 squares, so 512 is the widest
    # 1x that still leaves room for a real 2x instead of an upscale).
    ("belt-shrimp",     "dad-shrimp-plate.png",       4 / 3, 512),
    ("belt-beefrolls",  "dad-beef-rolls.png",         4 / 3, 512),
    ("belt-shortrib",   "dad-beef-shortrib.png",      4 / 3, 512),
    ("belt-porkbelly",  "dad-pork-belly.png",         4 / 3, 512),
    ("belt-shortrib-dark", "dad-beef-shortrib-dark.png", 4 / 3, 512),

    # Portrait: the drinks station. Ratio is 3/4, not 4/3.
    ("drinks-fountain", "dad-soda-fountain.png",      3 / 4, 600),

    # The belt. These two sat unused in originals/ while the README asked for
    # exactly this shot. room-wide is the home hero; belt-tall is the portrait
    # counterpart. Both are the differentiator, so they get the largest widths.
    # Widths are picked so a real 2x fits inside the source rather than being
    # skipped: 16/9 of 2560 wide leaves 2560, so 1280 doubles cleanly.
    ("room-wide",     "Hot-Pot-World-Rotary-38-min-scaled.jpg",      16 / 9, 1280),
    # Phone hero: drop the top third so the belt and the tables lead instead
    # of the ceiling, keeping the bottom of the chandelier for the room's face.
    ("room-wide-tall", "Hot-Pot-World-Rotary-38-min-scaled.jpg",      4 / 5, 470, (0.06, 0.30, 0.94, 1.0)),
    ("belt-tall",     "Hot-Pot-World-Rotary-27-min-1-scaled.jpg",     3 / 4, 850),
]

# Optional fifth field: a fractional window (left, top, right, bottom) taken
# BEFORE the aspect crop. Needed because crop_to is centred, and a centred
# portrait crop of a landscape photo keeps every pixel of height. On the room
# shot that means a phone hero full of ceiling with the belt squeezed out of
# the bottom. Trimming the ceiling first puts the belt back in the frame.
print("photos")
for row in PHOTOS:
    name, src, ratio, width = row[:4]
    window = row[4] if len(row) > 4 else None
    path = os.path.join(SRC, src)
    if not os.path.exists(path):
        print(f"  MISSING {src}")
        continue
    im = Image.open(path)
    if window:
        w, h = im.size
        l, t, r, b = window
        im = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
    save_web(crop_to(im, ratio), name, width)

print("\ndone ->", os.path.abspath(OUT))
