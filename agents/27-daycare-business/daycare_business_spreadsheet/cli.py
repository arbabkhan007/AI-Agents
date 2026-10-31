"""Command line front end.

    python -m daycare_business_spreadsheet
    python -m daycare_business_spreadsheet -o "output/Daycare.xlsx" --blank
    python -m daycare_business_spreadsheet --currency "£" --tax 20 --rows 800
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import (AGE_BANDS, AUTHOR, BILLING_BASES,
                     PRODUCT_LISTING_TITLE, PRODUCT_NAME, Config)

DEFAULT_OUTPUT = os.path.join(
    "output", "Daycare Business Management Spreadsheet.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="daycare_business_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty (no demo "
                             "setting)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for "
                             "development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--centre", default=None,
                        help="pre-fill the setting's name on Settings")
    parser.add_argument("--owner", default=None,
                        help="pre-fill the owner or director's name")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="the year the reports open on")
    parser.add_argument("--tax", type=float, default=None,
                        help="tax rate as a percentage, e.g. 20 for "
                             "20%% (childcare is exempt in many "
                             "places - the default is zero)")
    parser.add_argument("--tax-on", choices=["both", "tuition",
                                             "extras", "neither"],
                        default=None,
                        help="what the tax rate applies to")
    parser.add_argument("--capacity", type=int, default=None,
                        help="licensed places for the whole setting")
    parser.add_argument("--open-days", type=int, default=None,
                        help="days open a week")
    parser.add_argument("--open-hour", type=float, default=None,
                        help="opening time as a 24 hour number, "
                             "e.g. 7 for 7am")
    parser.add_argument("--close-hour", type=float, default=None,
                        help="closing time as a 24 hour number, "
                             "e.g. 18 for 6pm")
    parser.add_argument("--weeks-open", type=int, default=None,
                        help="trading weeks a year")
    parser.add_argument("--full-time-week", type=float, default=None,
                        help="the standard full-time weekly fee")
    parser.add_argument("--basis", choices=BILLING_BASES, default=None,
                        help="the billing basis new children start on")
    parser.add_argument("--sibling-discount", type=float, default=None,
                        help="sibling discount as a percentage, "
                             "e.g. 10")
    parser.add_argument("--hourly", type=float, default=None,
                        help="default staff hourly rate")
    parser.add_argument("--burden", type=float, default=None,
                        help="employer costs on wages as a percentage")
    parser.add_argument("--overtime-after", type=float, default=None,
                        help="hours a week before overtime starts")
    parser.add_argument("--target", type=float, default=None,
                        help="monthly revenue target")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the default row "
                             "counts are scaled to fit this many "
                             "attendance rows)")
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
    if args.tax is not None:
        kwargs["tax_rate"] = round(args.tax / 100.0, 5)
    if args.tax_on:
        kwargs["tax_on_tuition"] = ("Yes" if args.tax_on in
                                    ("both", "tuition") else "No")
        kwargs["tax_on_extras"] = ("Yes" if args.tax_on in
                                   ("both", "extras") else "No")
    if args.capacity is not None:
        kwargs["licensed_capacity"] = args.capacity
    if args.open_days is not None:
        kwargs["open_days"] = args.open_days
    if args.open_hour is not None:
        kwargs["open_hour"] = args.open_hour
    if args.close_hour is not None:
        kwargs["close_hour"] = args.close_hour
    if args.weeks_open is not None:
        kwargs["weeks_open"] = args.weeks_open
    if args.full_time_week is not None:
        kwargs["full_time_week"] = args.full_time_week
    if args.basis:
        kwargs["default_billing_basis"] = args.basis
    if args.sibling_discount is not None:
        kwargs["sibling_discount"] = round(
            args.sibling_discount / 100.0, 4)
    if args.hourly is not None:
        kwargs["default_hourly"] = args.hourly
    if args.burden is not None:
        kwargs["payroll_burden"] = round(args.burden / 100.0, 4)
    if args.overtime_after is not None:
        kwargs["overtime_after_hours"] = args.overtime_after
    if args.target is not None:
        kwargs["monthly_revenue_target"] = args.target
        kwargs["sample_monthly_revenue_target"] = args.target
    if args.today:
        kwargs["today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.blank:
        cfg.centre.name = ''
        cfg.centre.owner = ''
    if args.centre:
        cfg.centre.name = args.centre
    if args.owner:
        cfg.centre.owner = args.owner
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

    tax_on = []
    if cfg.tax_on_tuition == "Yes":
        tax_on.append("tuition")
    if cfg.tax_on_extras == "Yes":
        tax_on.append("extras")

    bands = ", ".join(f"{label} 1:{per}"
                      for label, _f, _t, per, _m in AGE_BANDS[:3])

    print(f"{cfg.product_name}")
    print(f"  listing title : {PRODUCT_LISTING_TITLE}")
    print(f"  author        : {cfg.author}")
    print(f"  sheets        : {len(SHEET_ORDER)}")
    print(f"  year          : {cfg.year}")
    print(f"  setting       : {cfg.centre.name}")
    print(f"  capacity      : {cfg.licensed_capacity} places, "
          f"{cfg.open_days} days a week, "
          f"{cfg.open_hours_day:,.1f} hours a day")
    print(f"  ratios        : {bands} (editable on Settings)")
    print(f"  tax           : {cfg.tax_rate:.2%} on "
          f"{' and '.join(tax_on) if tax_on else 'nothing'}")
    print(f"  full-time fee : {cfg.currency_symbol}"
          f"{cfg.full_time_week:,.2f} a week, basis "
          f"'{cfg.default_billing_basis}'")
    print(f"  target        : {cfg.currency_symbol}"
          f"{cfg.revenue_target_month:,.0f} a month")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  ({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
