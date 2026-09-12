#!/usr/bin/env python3
"""
tools/make_banner_alpha.py - give the cover banners a see-through middle.

The Start Here tab overlays the workbook title (28pt, merged C:H) on top of
the cover artwork.  Excel draws floating images ABOVE cell text, so the banner
needs a transparent window exactly where the title lands for it to shine
through.

Geometry (matches christmas_tracker/sheets/guide.py):
  * the artwork is scaled to 860 px wide on the sheet
  * banner rows are 20pt tall = 26.7 px; span = height_px / 26.7 + 1 rows
  * title_row = span // 2 - 1, so the title band sits at roughly 33-65% of
    the image height, starting at x ~= 3% (column C) and ending at x ~= 65%
    (column H) of the artwork width.

This script:
  1. cover-crops the raw generated art to exactly 1600 x 640,
  2. cuts a generously feathered, rounded transparent window over the title
     band,
  3. writes assets/banner_<theme>.png (RGBA).

Usage:
    python3 tools/make_banner_alpha.py            # process both themes
    python3 tools/make_banner_alpha.py festive    # process one theme
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1600, 640                       # final banner size (displayed at 860px)
WINDOW = (0.045, 0.315, 0.70, 0.72)    # x0, y0, x1, y1 as fractions
FEATHER = 34                           # soft edge width in px
RADIUS = 28                            # rounded-corner radius in px


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
    print("wrote %-38s %dx%d  window=%s" % (dst, W, H, WINDOW))


if __name__ == "__main__":
    themes = sys.argv[1:] or ["festive", "minimal"]
    for theme in themes:
        process(theme)
