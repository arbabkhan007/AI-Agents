"""Command line front end.

    python -m handmade_pricing_spreadsheet
    python -m handmade_pricing_spreadsheet -o "output/Pricing.xlsx" --blank
    python -m handmade_pricing_spreadsheet --currency "£" --rate 22 --rows 150
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     ROUNDING_RULES, Config)

DEFAULT_OUTPUT = os.path.join(
    "output", "Handmade Product Pricing & Profit Calculator.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="handmade_pricing_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty "
                             "(no example products)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--shop", default=None,
                        help="pre-fill the shop name on Settings")
    parser.add_argument("--owner", default=None,
                        help="pre-fill the maker / owner name")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="the year the reports open on")
    parser.add_argument("--rate", type=float, default=None,
                        help="what you pay yourself an hour")
    parser.add_argument("--margin", type=float, default=None,
                        help="target retail margin as a percentage, "
                             "e.g. 55 for 55%%")
    parser.add_argument("--wholesale-margin", type=float, default=None,
                        help="target wholesale margin as a percentage")
    parser.add_argument("--wholesale-discount", type=float, default=None,
                        help="wholesale price as a percentage off retail, "
                             "e.g. 50 for half price")
    parser.add_argument("--rounding", choices=ROUNDING_RULES, default=None,
                        help="how calculated prices are rounded")
    parser.add_argument("--transaction-fee", type=float, default=None,
                        help="marketplace transaction fee as a "
                             "percentage, e.g. 6.5")
    parser.add_argument("--listing-fee", type=float, default=None,
                        help="fee charged to list one item")
    parser.add_argument("--tax", type=float, default=None,
                        help="sales tax / VAT rate as a percentage")
    parser.add_argument("--units", choices=["Metric", "Imperial"],
                        default=None,
                        help="the measurement system used for materials")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the default row "
                             "counts are multiplied to fit this many "
                             "product rows)")
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
    if args.year:
        kwargs["plan_year"] = args.year
    if args.rate:
        kwargs["hourly_rate"] = args.rate
    if args.margin is not None:
        kwargs["target_retail_margin"] = round(args.margin / 100.0, 4)
    if args.wholesale_margin is not None:
        kwargs["target_wholesale_margin"] = round(
            args.wholesale_margin / 100.0, 4)
    if args.wholesale_discount is not None:
        kwargs["wholesale_discount"] = round(
            args.wholesale_discount / 100.0, 4)
    if args.rounding:
        kwargs["rounding_rule"] = args.rounding
    if args.transaction_fee is not None:
        kwargs["transaction_fee"] = round(args.transaction_fee / 100.0, 5)
    if args.listing_fee is not None:
        kwargs["listing_fee"] = args.listing_fee
    if args.tax is not None:
        kwargs["tax_rate"] = round(args.tax / 100.0, 4)
    if args.units:
        kwargs["measure_system"] = args.units
        if args.units == "Imperial":
            kwargs["weight_unit"] = "oz"
            kwargs["length_unit"] = "inch"
    if args.today:
        kwargs["today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.shop:
        cfg.shop.name = args.shop
    if args.owner:
        cfg.shop.owner = args.owner
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
    print(f"  shop          : {cfg.shop.name}")
    print(f"  labour        : {cfg.currency_symbol}{cfg.hourly_rate:,.2f} an "
          f"hour ({cfg.currency_symbol}{cfg.labor_cost_per_hour:,.2f} with "
          f"on-costs)")
    print(f"  target margin : {cfg.target_retail_margin:.0%} retail, "
          f"{cfg.target_wholesale_margin:.0%} wholesale")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  ({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
