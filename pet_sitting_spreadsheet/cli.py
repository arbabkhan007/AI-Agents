"""Command line front end.

    python -m pet_sitting_spreadsheet
    python -m pet_sitting_spreadsheet -o "output/Pet Sitting.xlsx" --blank
    python -m pet_sitting_spreadsheet --currency "£" --unit miles --rows 500
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import build_workbook
from .config import AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME, Config

DEFAULT_OUTPUT = os.path.join(
    "output", "Pet Sitting Business Spreadsheet.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pet_sitting_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty "
                             "(no example records)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--business", default=None,
                        help="pre-fill the business name on Settings")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--unit", choices=["km", "miles"], default=None,
                        help="distance unit for mileage")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (default row counts are "
                             "multiplied to fit this many booking rows)")
    parser.add_argument("--today", default=None,
                        help="treat this ISO date as 'today' when "
                             "generating the example data")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the output path")
    return parser


def config_from_args(args: argparse.Namespace) -> Config:
    kwargs = {}
    if args.blank:
        kwargs["include_sample_data"] = False
    if args.no_protect:
        kwargs["protect_sheets"] = False
    if args.password:
        kwargs["password"] = args.password
    if args.author:
        kwargs["author"] = args.author
    if args.currency:
        kwargs["currency_symbol"] = args.currency
    if args.currency_code:
        kwargs["currency_code"] = args.currency_code
    if args.unit:
        kwargs["distance_unit"] = args.unit
    if args.today:
        kwargs["today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.business:
        cfg.business.name = args.business
    if args.rows:
        cfg.scale_rows(args.rows)
    return cfg


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = config_from_args(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    path = build_workbook(args.output, cfg)
    size = os.path.getsize(path) / 1024.0

    if args.quiet:
        print(path)
        return 0

    print(f"{cfg.product_name}")
    print(f"  listing title : {PRODUCT_LISTING_TITLE}")
    print(f"  author        : {cfg.author}")
    print("  sheets        : 27 (1 hidden calculation engine)")
    print(f"  example data  : {'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  ({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
