#!/usr/bin/env python3
"""
Turn the flat banner art from the image generator into an Excel-ready banner.

Generated PNGs always have a solid background, but the workbook banner sits on
a cream canvas and needs a real alpha channel to blend in.  This tool:

    1. crops the generated image to the banner window (the window covers the
       art band and nothing else)
    2. finds the background colour from the image corners
    3. makes every pixel within TOLERANCE of that colour transparent, with a
       soft 6-step falloff so edges stay smooth
    4. applies the same transparency to near-white and near-black pixels so
       snow, fur and paper tones do not form a box around the artwork
    5. scales the result to the exact banner width and writes banner_X.png

    python3 tools/make_banner_alpha_santa.py assets/raw_banner_noel.png \\
        assets/banner_noel.png
"""

import sys

from PIL import Image

WIN = (0.06, 0.02, 0.68, 0.98)     # l, t, r, b window inside a 1600x640 art
TARGET_W = 996                     # px, matches the insert scale in guide.py
TOLERANCE = 26


def to_alpha(src, dst):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    l, t, r, b = int(W * WIN[0]), int(H * WIN[1]), int(W * WIN[2]), \
        int(H * WIN[3])
    im = im.crop((l, t, r, b))
    im = im.resize((TARGET_W, int(TARGET_W * (b - t) / (r - l))),
                   Image.LANCZOS)
    px = im.load()
    w, h = im.size

    # sample the corner colours: the generator paints a cream/white band
    corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    out = Image.new("RGBA", (w, h))
    op = out.load()
    near_white = (250, 250, 248)
    near_black = (28, 26, 32)
    for y in range(h):
        for x in range(w):
            r_, g_, b_ = px[x, y]
            dist = max(abs(r_ - bg[0]), abs(g_ - bg[1]), abs(b_ - bg[2]))
            a = 255
            if dist <= TOLERANCE:
                a = 0
            elif dist <= TOLERANCE + 6:
                a = int(255 * (dist - TOLERANCE) / 6)
            else:
                for ref in (near_white, near_black):
                    d2 = max(abs(r_ - ref[0]), abs(g_ - ref[1]),
                             abs(b_ - ref[2]))
                    if d2 <= 10:
                        a = min(a, int(255 * d2 / 10))
            op[x, y] = (r_, g_, b_, a)
    out.save(dst)
    print("%s -> %s  (%dx%d, bg=%s)" % (src, dst, w, h, bg))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: make_banner_alpha_santa.py RAW.png OUT.png")
        sys.exit(1)
    to_alpha(sys.argv[1], sys.argv[2])
