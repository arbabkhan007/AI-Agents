#!/usr/bin/env python3
"""
Ultimate Crochet Craft Fair Tracker - builder CLI.

Builds the Etsy product set:

    python3 crochet_craft_fair_tracker.py --all --outdir products \
        --protect premium

  premium berry demo   -> Crochet_Craft_Fair_Tracker_PREMIUM_Berry_EXAMPLE
  premium berry blank  -> Crochet_Craft_Fair_Tracker_PREMIUM_Berry
  premium mint blank   -> Crochet_Craft_Fair_Tracker_PREMIUM_Mint
  basic berry blank    -> Crochet_Craft_Fair_Tracker_BASIC_Berry
  basic mint blank     -> Crochet_Craft_Fair_Tracker_BASIC_Mint
  basic berry demo     -> Crochet_Craft_Fair_Tracker_BASIC_Berry_EXAMPLE

Use --edition/--theme/--mode/--one for a single build.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crochet_tracker import workbook


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Build the Crochet Craft Fair Tracker workbooks.")
    ap.add_argument("--all", action="store_true",
                    help="build the full six-file Etsy product set")
    ap.add_argument("--edition", choices=("basic", "premium"))
    ap.add_argument("--theme", choices=("berry", "mint"))
    ap.add_argument("--mode", choices=("blank", "demo"))
    ap.add_argument("--one", metavar="FILENAME",
                    help="output filename for a single build")
    ap.add_argument("--outdir", default="products")
    ap.add_argument("--protect", default=None, metavar="PASSWORD",
                    help="lock calculated cells with this password")
    ap.add_argument("--no-images", action="store_true",
                    help="skip the banner image on the Start Here tab")
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    images = not args.no_images

    if args.all:
        rows = [("File", "Edition", "Theme", "Mode", "Sheets", "Formulas",
                 "Validations", "CondFmts", "Charts", "Size")]
        results = workbook.build_all(args.outdir, protect=args.protect,
                                     images=images)
        for name, st in results:
            short = name.replace("Crochet_Craft_Fair_Tracker_", "")
            edition = "PREMIUM" if "_PREMIUM" in name else "BASIC"
            theme = "Berry" if "_Berry" in name else "Mint"
            mode = "EXAMPLE" if "_EXAMPLE" in name else "blank"
            rows.append((name, edition, theme, mode,
                         str(st.get("sheets", "?")),
                         str(st["formulas"]), str(st["validations"]),
                         str(st["cond_formats"]), str(st["charts"]),
                         "%d KB" % (st["size"] // 1024)))
        widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
        for row in rows:
            print("  ".join(str(v).ljust(widths[i])
                            for i, v in enumerate(row)))
        return 0

    if not (args.edition and args.theme and args.mode):
        ap.error("single build needs --edition, --theme and --mode "
                 "(or use --all)")

    name = args.one or workbook.product_filename(args.edition, args.theme,
                                                 args.mode)
    path = os.path.join(args.outdir, name)
    st = workbook.build_workbook(path, args.edition, args.theme, args.mode,
                                 protect=args.protect, images=images)
    print("%s: %d formulas, %d validations, %d cond formats, %d charts, "
          "%d KB" % (name, st["formulas"], st["validations"],
                     st["cond_formats"], st["charts"], st["size"] // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
