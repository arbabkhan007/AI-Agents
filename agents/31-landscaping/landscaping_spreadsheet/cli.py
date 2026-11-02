"""Command line entry point for building the workbook."""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys

from .build import build_workbook
from .config import PRODUCT_NAME, VERSION, Config, Business


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="landscaping_spreadsheet",
        description=f"Build {PRODUCT_NAME} (version {VERSION}).")
    parser.add_argument("-o", "--output",
                        default="Ultimate Landscaping & Lawn Care "
                                "Business Manager.xlsx",
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="build without the worked example data")
    parser.add_argument("--rows", type=int, default=None,
                        help="override the row count of every "
                             "register (useful for quick tests)")
    parser.add_argument("--today", default=None,
                        help="treat this ISO date as today, so the "
                             "sample data lands around it")
    parser.add_argument("--quiet", action="store_true",
                        help="print nothing on success")
    args = parser.parse_args(argv)

    today = None
    if args.today:
        today = _dt.date.fromisoformat(args.today)

    cfg = Config(include_sample_data=not args.blank,
                 rows_override=args.rows,
                 _today=today)
    if args.blank:
        cfg.business = Business(**{key: "" for key in Business.__dataclass_fields__})
    path = build_workbook(args.output, cfg)
    if not args.quiet:
        size = os.path.getsize(path)
        print(f"{PRODUCT_NAME} v{VERSION}")
        print(f"  wrote {path} ({size:,} bytes)")
        print(f"  sample data: {'no' if args.blank else 'yes'}")
    return 0


if __name__ == "__main__":        # pragma: no cover
    sys.exit(main())
