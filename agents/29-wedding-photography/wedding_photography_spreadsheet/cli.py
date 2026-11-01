"""Command line front end.

    python -m wedding_photography_spreadsheet
    python -m wedding_photography_spreadsheet -o "out/Wedding.xlsx" --blank
    python -m wedding_photography_spreadsheet --currency "£" --rows 60
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import (AUTHOR, DEFAULT_ROWS, LISTING_TITLE, PACKAGES,
                     PRODUCT_NAME, SCALE_ANCHOR, Config)

DEFAULT_OUTPUT = os.path.join(
    "output", "Wedding Photographer Business Manager.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wedding_photography_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty (no example "
                             "studio)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for "
                             "development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--studio", default=None,
                        help="pre-fill the studio name on Settings")
    parser.add_argument("--owner", default=None,
                        help="pre-fill the photographer's name")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="the year the reports open on")
    parser.add_argument("--deposit", type=float, default=None,
                        help="deposit to hold a date, as a "
                             "percentage, e.g. 30 for 30%%")
    parser.add_argument("--final-days", type=int, default=None,
                        help="days before the wedding the balance "
                             "falls due")
    parser.add_argument("--extra-hour", type=float, default=None,
                        help="charge for an extra hour on the day")
    parser.add_argument("--second-shooter", type=float, default=None,
                        help="what a second shooter costs you")
    parser.add_argument("--mileage", type=float, default=None,
                        help="mileage rate per mile")
    parser.add_argument("--delivery-days", type=int, default=None,
                        help="your promised gallery turnaround")
    parser.add_argument("--editing-hours", type=float, default=None,
                        help="honest editing hours per wedding")
    parser.add_argument("--tax", type=float, default=None,
                        help="sales tax or VAT on packages, as a "
                             "percentage, e.g. 20 for 20%% (zero by "
                             "default)")
    parser.add_argument("--weddings-target", type=int, default=None,
                        help="how many weddings a year you want")
    parser.add_argument("--revenue-target", type=float, default=None,
                        help="revenue target for the year")
    parser.add_argument("--margin-target", type=float, default=None,
                        help="profit margin target as a percentage, "
                             "e.g. 55 for 55%%")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the defaults are "
                             "scaled to fit this many wedding rows)")
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
        kwargs["currency"] = args.currency
    if args.currency_code:
        kwargs["currency_code"] = args.currency_code
    if args.year:
        kwargs["year"] = args.year
    if args.deposit is not None:
        kwargs["deposit_percent"] = round(args.deposit / 100.0, 5)
    if args.final_days is not None:
        kwargs["final_payment_days_before"] = args.final_days
    if args.extra_hour is not None:
        kwargs["extra_hour_rate"] = args.extra_hour
    if args.second_shooter is not None:
        kwargs["second_shooter_rate"] = args.second_shooter
    if args.mileage is not None:
        kwargs["mileage_rate"] = args.mileage
    if args.delivery_days is not None:
        kwargs["delivery_days"] = args.delivery_days
    if args.editing_hours is not None:
        kwargs["editing_hours_per_wedding"] = args.editing_hours
    if args.tax is not None:
        kwargs["tax_rate"] = round(args.tax / 100.0, 5)
        kwargs["tax_on_packages"] = args.tax > 0
    if args.weddings_target is not None:
        kwargs["target_weddings_year"] = args.weddings_target
    if args.revenue_target is not None:
        kwargs["target_revenue_year"] = args.revenue_target
        kwargs["target_revenue_month"] = round(
            args.revenue_target / 12.0, 2)
    if args.margin_target is not None:
        kwargs["target_profit_margin"] = round(
            args.margin_target / 100.0, 4)
    if args.today:
        kwargs["_today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.blank:
        from .config import Studio
        cfg.studio = Studio(name="", owner="", email="", phone="",
                            website="", instagram="", city="", region="", country="")
    if args.studio:
        cfg.studio.name = args.studio
    if args.owner:
        cfg.studio.owner = args.owner
    if args.rows:
        # every register scales against Wedding Bookings, which is
        # what `row_count()` and `scale_rows()` both read
        cfg.rows_override = args.rows
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

    rows = sum(cfg.row_count(sheet) for sheet in DEFAULT_ROWS)
    cheapest = min(PACKAGES, key=lambda p: p[-1])
    dearest = max(PACKAGES, key=lambda p: p[-1])
    sign = cfg.currency

    print(f"{PRODUCT_NAME}")
    print(f"  listing title : {LISTING_TITLE}")
    print(f"  author        : {cfg.author}")
    print(f"  sheets        : {len(SHEET_ORDER)}")
    print(f"  studio        : {cfg.studio.name} "
          f"({cfg.studio.owner})")
    print(f"  today         : {cfg.today.isoformat()}")
    print(f"  register rows : {rows:,} across "
          f"{len(DEFAULT_ROWS)} registers "
          f"(scaled on {SCALE_ANCHOR})")
    print(f"  packages      : {len(PACKAGES)}, "
          f"{sign}{cheapest[-1]:,.0f} to {sign}{dearest[-1]:,.0f}")
    print(f"  deposit       : {cfg.deposit_percent:.0%} to hold, "
          f"balance {cfg.final_payment_days_before} days before")
    print(f"  turnaround    : preview {cfg.preview_days} days, "
          f"gallery {cfg.delivery_days} days")
    print(f"  extras        : extra hour {sign}"
          f"{cfg.extra_hour_rate:,.0f}, second shooter {sign}"
          f"{cfg.second_shooter_rate:,.0f}, mileage {sign}"
          f"{cfg.mileage_rate:.2f}")
    print(f"  tax           : {cfg.tax_rate:.2%} "
          f"({'on' if cfg.tax_on_packages else 'off'})")
    print(f"  targets       : {cfg.target_weddings_year} weddings, "
          f"{sign}{cfg.target_revenue_year:,.0f}, "
          f"{cfg.target_profit_margin:.0%} margin")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  "
          f"({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
