"""Command line front end.

    python -m cleaning_business_spreadsheet
    python -m cleaning_business_spreadsheet -o "output/Cleaning.xlsx" --blank
    python -m cleaning_business_spreadsheet --currency "£" --rate 38 --rows 300
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME, Config

DEFAULT_OUTPUT = os.path.join(
    "output", "Cleaning Business CRM & Pricing Calculator.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cleaning_business_spreadsheet",
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
    parser.add_argument("--owner", default=None,
                        help="pre-fill the owner / manager name")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="the year the planner and reports open on")
    parser.add_argument("--week-start", choices=["Monday", "Sunday"],
                        default=None, help="first day of the week")
    parser.add_argument("--rate", type=float, default=None,
                        help="default hourly rate charged to the client")
    parser.add_argument("--pay", type=float, default=None,
                        help="default hourly pay rate of a cleaner")
    parser.add_argument("--minimum", type=float, default=None,
                        help="minimum charge for any job")
    parser.add_argument("--tax", type=float, default=None,
                        help="sales tax / VAT rate as a percentage, "
                             "e.g. 20 for 20%%")
    parser.add_argument("--terms", type=int, default=None,
                        help="payment terms in days")
    parser.add_argument("--units", choices=["sq ft", "sq m"], default=None,
                        help="the area unit used for pricing")
    parser.add_argument("--distance", choices=["miles", "km"], default=None,
                        help="the distance unit used for mileage")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the default row "
                             "counts are multiplied to fit this many "
                             "job rows)")
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
    if args.week_start:
        kwargs["week_start"] = args.week_start
    if args.year:
        kwargs["plan_year"] = args.year
    if args.rate:
        kwargs["hourly_rate"] = args.rate
    if args.pay:
        kwargs["pay_rate"] = args.pay
    if args.minimum:
        kwargs["minimum_charge"] = args.minimum
    if args.tax is not None:
        kwargs["tax_rate"] = round(args.tax / 100.0, 4)
    if args.terms:
        kwargs["payment_terms_days"] = args.terms
    if args.units:
        kwargs["area_unit"] = args.units
    if args.distance:
        kwargs["distance_unit"] = args.distance
    if args.today:
        kwargs["today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.business:
        cfg.business.name = args.business
    if args.owner:
        cfg.business.owner = args.owner
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
    print(f"  sheets        : {len(SHEET_ORDER)}")
    print(f"  year          : {cfg.year}")
    print(f"  business      : {cfg.business.name}")
    print(f"  pricing       : {cfg.currency_symbol}{cfg.hourly_rate:,.2f} an "
          f"hour, minimum {cfg.currency_symbol}{cfg.minimum_charge:,.2f}")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  ({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
