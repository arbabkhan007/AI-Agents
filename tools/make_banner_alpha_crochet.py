#!/usr/bin/env python3
"""
tools/make_banner_alpha_crochet.py - give the crochet cover banners a
see-through window.

The Start Here tab writes the product title *under* the cover artwork and
it shows through a transparent window (Excel draws floating images above
cell text, so the banner itself must be see-through where the title
lands).

Geometry (matches crochet_tracker/sheets/guide.py):
  * the artwork is scaled to 860 px wide on the sheet
  * the title band sits at roughly x 6%-66% of the artwork width and
    spans nearly the full height, so the window is generous:
    (0.06, 0.02, 0.66, 0.98) as fractions of (x0, y0, x1, y1).

This script:
  1. cover-crops the raw generated art to exactly 1600 x 640,
  2. cuts a generously feathered, rounded transparent window,
  3. writes assets/banner_<theme>.png (RGBA).

Usage:
    python3 tools/make_banner_alpha_crochet.py            # both themes
    python3 tools/make_banner_alpha_crochet.py berry      # one theme
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 640                       # final banner size (shown at 860px)
WINDOW = (0.06, 0.02, 0.66, 0.98)      # x0, y0, x1, y1 as fractions
FEATHER = 36                           # soft edge width in px
RADIUS = 30                            # rounded-corner radius in px


def process(theme):
    src = os.path.join(ROOT, "assets", "raw_banner_%s.png" % theme)
    dst = os.path.join(ROOT, "assets", "banner_%s.png" % theme)
    if not os.path.exists(src):
        raise SystemExit("missing %s" % src)

    im = Image.open(src).convert("RGB")
    # cover-crop to the exact banner aspect
    scale = max(W / float(im.width), H / float(im.height))
    im = im.resize((int(round(im.width * scale)),
                    int(round(im.height * scale))), Image.LANCZOS)
    x = (im.width - W) // 2
    y = (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))

    # alpha mask: 255 = opaque artwork, 0 = see-through window
    mask = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(mask)
    x0 = int(WINDOW[0] * W)
    y0 = int(WINDOW[1] * H)
    x1 = int(WINDOW[2] * W)
    y1 = int(WINDOW[3] * H)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=RADIUS, fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(FEATHER))

    out = im.convert("RGBA")
    out.putalpha(mask)
    out.save(dst)
    print("wrote %-40s %dx%d  window=%s" % (dst, W, H, WINDOW))


if __name__ == "__main__":
    themes = sys.argv[1:] or ["berry", "mint"]
    for theme in themes:
        process(theme)
