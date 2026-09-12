#!/usr/bin/env python3
"""
Build the Ultimate Christmas Gift Tracker workbooks.

Examples
--------
    python3 christmas_gift_tracker.py --all
    python3 christmas_gift_tracker.py --edition premium --theme festive \
        --mode demo --out products/hero.xlsx
    python3 christmas_gift_tracker.py --edition basic --theme minimal

The script needs nothing but the XlsxWriter library that lives in this
repository (it is imported from the checkout root), so it runs straight from
a fresh clone with a stock Python 3.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from christmas_tracker import build_all, build_workbook  # noqa: E402
from christmas_tracker.workbook import product_filename  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build Christmas / Ultimate Gift Tracker workbooks.")
    p.add_argument("--edition", choices=["basic", "premium", "both"],
                   default="premium")
    p.add_argument("--theme", choices=["festive", "minimal", "both"],
                   default="festive")
    p.add_argument("--mode", choices=["blank", "demo", "both"],
                   default="blank",
                   help="blank = clean template, demo = filled example")
    p.add_argument("--all", action="store_true",
                   help="build the curated Etsy product set into products/")
    p.add_argument("--out", default=None,
                   help="output path (single build only)")
    p.add_argument("--outdir", default="products",
                   help="output folder for --all / multi builds")
    p.add_argument("--protect", default=None, metavar="PASSWORD",
                   help="optionally lock every sheet with a password")
    p.add_argument("--no-images", action="store_true",
                   help="skip the watercolour cover banner")
    args = p.parse_args(argv)

    if args.all:
        stats = build_all(args.outdir, protect=args.protect,
                          images=not args.no_images)
        _report(stats)
        return 0

    editions = ["basic", "premium"] if args.edition == "both" else [args.edition]
    themes_ = ["festive", "minimal"] if args.theme == "both" else [args.theme]
    modes = ["blank", "demo"] if args.mode == "both" else [args.mode]

    stats = []
    for edition in editions:
        for theme_name in themes_:
            for mode in modes:
                if args.out and len(editions) == 1 and len(themes_) == 1 \
                        and len(modes) == 1:
                    path = args.out
                else:
                    os.makedirs(args.outdir, exist_ok=True)
                    path = os.path.join(
                        args.outdir, product_filename(edition, theme_name,
                                                      mode))
                stats.append(build_workbook(path, edition, theme_name, mode,
                                            protect=args.protect,
                                            images=not args.no_images))
    _report(stats)
    return 0


def _report(stats):
    print()
    print("=" * 78)
    print("BUILD COMPLETE")
    print("=" * 78)
    for s in stats:
        print("  %-58s %7.1f KB" % (os.path.basename(s["path"]),
                                    s["size"] / 1024.0))
        print("      formulas %5d   validations %3d   cond. formats %3d   "
              "charts %2d   links %3d"
              % (s["formulas"], s["validations"], s["cond_formats"],
                 s["charts"], s["links"]))
    print()


if __name__ == "__main__":
    sys.exit(main())
