#!/usr/bin/env python3
"""
Upscale the Etsy listing images to 2000 x 2000.

    python tools/upscale_etsy_images.py                # every image
    python tools/upscale_etsy_images.py --prefix meal- # just one product

Etsy asks for at least 2000 px on the shortest side of a listing photo.
The originals in `etsy-images/` are 1024 px, so they are resampled up with
a Lanczos filter and a light sharpening pass into `etsy-images-2000px/`,
keeping the file names so the packer can find them.
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "etsy-images")
TARGET = os.path.join(ROOT, "etsy-images-2000px")
SIZE = 2000

try:
    from PIL import Image, ImageFilter
except ImportError:                              # pragma: no cover
    print("error: Pillow is required (pip install Pillow)", file=sys.stderr)
    raise SystemExit(2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="",
                        help="only files starting with this")
    parser.add_argument("--size", type=int, default=SIZE)
    args = parser.parse_args(argv)

    if not os.path.isdir(SOURCE):
        print(f"error: {SOURCE} does not exist", file=sys.stderr)
        return 2
    os.makedirs(TARGET, exist_ok=True)

    count = 0
    for name in sorted(os.listdir(SOURCE)):
        if args.prefix and not name.startswith(args.prefix):
            continue
        if not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        source = os.path.join(SOURCE, name)
        target = os.path.join(TARGET, name)
        with Image.open(source) as image:
            image = image.convert("RGB")
            if image.size != (args.size, args.size):
                image = image.resize((args.size, args.size),
                                     Image.LANCZOS)
            image = image.filter(ImageFilter.UnsharpMask(radius=1.2,
                                                         percent=60,
                                                         threshold=3))
            image.save(target, "JPEG", quality=92, optimize=True,
                       progressive=True)
        count += 1
        print(f"  {name:42s} {args.size} x {args.size}")

    print(f"{count} image(s) written to {os.path.relpath(TARGET, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
