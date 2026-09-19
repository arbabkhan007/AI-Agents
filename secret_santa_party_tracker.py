#!/usr/bin/env python3
"""Command line entry point for the Secret Santa & White Elephant tracker."""

import argparse
import sys


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build Secret Santa & White Elephant Party Tracker "
                    "workbooks (Novality Store).")
    p.add_argument("--edition", choices=("premium", "basic"),
                   default="premium")
    p.add_argument("--theme", choices=("noel", "arctic"), default="noel")
    p.add_argument("--mode", choices=("blank", "demo"), default="blank")
    p.add_argument("--out", default=None)
    p.add_argument("--outdir", default="products")
    p.add_argument("--all", action="store_true",
                   help="build the curated six-file product set")
    p.add_argument("--protect", default="premium", metavar="PASSWORD",
                   help="sheet-protection password for locked formula "
                        "cells (default: premium)")
    p.add_argument("--no-protect", dest="protect_off", action="store_true",
                   help="ship the workbooks unprotected")
    args = p.parse_args(argv)

    sys.path.insert(0, ".")
    from santa_tracker import config as C
    from santa_tracker import workbook as W
    protect = None if args.protect_off else (args.protect or
                                             C.PROTECT_PASSWORD)
    if args.all:
        rows = W.build_all(args.outdir, protect=protect)
    else:
        from santa_tracker.workbook import product_filename
        out = args.out or product_filename(args.edition, args.theme,
                                           args.mode)
        stats = W.build_workbook(out, args.edition, args.theme, args.mode,
                                 protect=protect)
        rows = [(out, stats)]
    print("=" * 78)
    print("BUILD COMPLETE")
    print("=" * 78)
    for name, stats in rows:
        print("  %-58s %7.1f KB" % (name, stats["size"] / 1024.0))
        print("      formulas %5d   validations %3d   cond. formats %3d   "
              "charts %d" % (stats["formulas"], stats["validations"],
                             stats["cond_formats"], stats["charts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
