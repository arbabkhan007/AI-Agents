#!/usr/bin/env python3
"""
Build the Ultimate Catering Business Spreadsheet workbooks.

Examples
--------
    python3 catering_business_tracker.py --all
    python3 catering_business_tracker.py --edition premium --theme classic \
        --mode demo --out products/hero.xlsx
    python3 catering_business_tracker.py --edition basic --theme fresh

The script needs nothing but the XlsxWriter library that lives in this
repository (it is imported from the checkout root), so it runs straight from
a fresh clone with a stock Python 3.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from catering_tracker import build_all, build_workbook  # noqa: E402
from catering_tracker.workbook import product_filename  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build Ultimate Catering Business Spreadsheet workbooks.")
    p.add_argument("--edition", choices=["basic", "premium", "both"],
                   default="premium")
    p.add_argument("--theme", choices=["classic", "fresh", "both"],
                   default="classic")
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
                   help="skip cover banner images (smaller files)")
    args = p.parse_args(argv)

    if args.all:
        stats = build_all(args.outdir, protect=args.protect,
                          images=not args.no_images)
        _report(stats)
        return 0

    editions = (["basic", "premium"] if args.edition == "both"
                else [args.edition])
    themes_ = (["classic", "fresh"] if args.theme == "both"
               else [args.theme])
    modes = ["blank", "demo"] if args.mode == "both" else [args.mode]

    stats = []
    for edition in editions:
        for theme_name in themes_:
            for mode in modes:
                if (args.out and len(editions) == 1 and len(themes_) == 1
                        and len(modes) == 1):
                    path = args.out
                else:
                    os.makedirs(args.outdir, exist_ok=True)
                    path = os.path.join(
                        args.outdir,
                        product_filename(edition, theme_name, mode))
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
