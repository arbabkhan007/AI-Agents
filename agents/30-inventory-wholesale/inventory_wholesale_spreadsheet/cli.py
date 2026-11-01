"""Command line front end.

    python -m inventory_wholesale_spreadsheet
    python -m inventory_wholesale_spreadsheet -o "out/Stock.xlsx" --blank
    python -m inventory_wholesale_spreadsheet --currency "£" --rows 120
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import (AUTHOR, DEFAULT_ROWS, LISTING_TITLE,
                     PRICE_TIERS, PRODUCT_NAME, SCALE_ANCHOR, Config)

DEFAULT_OUTPUT = os.path.join(
    "output", "Ultimate Inventory & Wholesale Order Manager.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inventory_wholesale_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty (no example "
                             "business)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for "
                             "development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--business", default=None,
                        help="pre-fill the business name on Settings")
    parser.add_argument("--owner", default=None,
                        help="pre-fill the owner's name")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="the year the reports open on")
    parser.add_argument("--markup", type=float, default=None,
                        help="default retail markup on cost, "
                             "e.g. 2.5")
    parser.add_argument("--min-margin", type=float, default=None,
                        help="minimum acceptable gross margin as a "
                             "percentage, e.g. 25 for 25%%")
    parser.add_argument("--lead-time", type=int, default=None,
                        help="default supplier lead time in days")
    parser.add_argument("--safety-days", type=int, default=None,
                        help="safety stock expressed in days of "
                             "cover")
    parser.add_argument("--sales-window", type=int, default=None,
                        help="days of history used for average "
                             "daily sales")
    parser.add_argument("--marketplace-fee", type=float, default=None,
                        help="default marketplace commission as a "
                             "percentage, e.g. 6.5")
    parser.add_argument("--payment-fee", type=float, default=None,
                        help="payment processing as a percentage, "
                             "e.g. 2.9")
    parser.add_argument("--tax", type=float, default=None,
                        help="sales tax or VAT as a percentage, "
                             "e.g. 20 for 20%% (zero by default)")
    parser.add_argument("--revenue-target", type=float, default=None,
                        help="revenue target for the year")
    parser.add_argument("--margin-target", type=float, default=None,
                        help="gross margin target as a percentage, "
                             "e.g. 55 for 55%%")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the defaults are "
                             "scaled to fit this many product rows)")
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
    if args.markup is not None:
        kwargs["default_markup"] = args.markup
    if args.min_margin is not None:
        kwargs["minimum_margin"] = round(args.min_margin / 100.0, 4)
    if args.lead_time is not None:
        kwargs["default_lead_time_days"] = args.lead_time
    if args.safety_days is not None:
        kwargs["safety_stock_days"] = args.safety_days
    if args.sales_window is not None:
        kwargs["sales_history_days"] = args.sales_window
    if args.marketplace_fee is not None:
        kwargs["marketplace_fee_pct"] = round(
            args.marketplace_fee / 100.0, 5)
    if args.payment_fee is not None:
        kwargs["payment_fee_pct"] = round(args.payment_fee / 100.0, 5)
    if args.tax is not None:
        kwargs["tax_rate"] = round(args.tax / 100.0, 5)
        kwargs["tax_on_sales"] = args.tax > 0
    if args.revenue_target is not None:
        kwargs["target_revenue_year"] = args.revenue_target
        kwargs["target_revenue_month"] = round(
            args.revenue_target / 12.0, 2)
    if args.margin_target is not None:
        kwargs["target_gross_margin"] = round(
            args.margin_target / 100.0, 4)
    if args.today:
        kwargs["_today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.blank:
        from .config import Business
        cfg.business = Business(**{name: "" for name in Business.__dataclass_fields__})
    if args.business:
        cfg.business.name = args.business
    if args.owner:
        cfg.business.owner = args.owner
    if args.rows:
        # every register scales against the Product & SKU Database,
        # which is what `row_count()` and `scale_rows()` both read
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
    sign = cfg.currency
    breaks = ", ".join(str(qty) for qty, _label in PRICE_TIERS)

    print(f"{PRODUCT_NAME}")
    print(f"  listing title : {LISTING_TITLE}")
    print(f"  author        : {cfg.author}")
    print(f"  sheets        : {len(SHEET_ORDER)}")
    print(f"  business      : {cfg.business.name} "
          f"({cfg.business.owner})")
    print(f"  today         : {cfg.today.isoformat()}")
    print(f"  register rows : {rows:,} across "
          f"{len(DEFAULT_ROWS)} registers "
          f"(scaled on {SCALE_ANCHOR})")
    print("  costing       : weighted average, everywhere")
    print(f"  price breaks  : {breaks}")
    print(f"  margin floor  : {cfg.minimum_margin:.0%} "
          f"(target {cfg.target_gross_margin:.0%})")
    print(f"  reordering    : (daily sales x lead time) + "
          f"{cfg.safety_stock_days} days safety, "
          f"{cfg.sales_history_days}-day window")
    print(f"  lead time     : {cfg.default_lead_time_days} days "
          f"default, overridden per supplier")
    print(f"  selling costs : marketplace "
          f"{cfg.marketplace_fee_pct:.1%}, payment "
          f"{cfg.payment_fee_pct:.1%} + {sign}"
          f"{cfg.payment_fee_fixed:.2f}")
    print(f"  tax           : {cfg.tax_rate:.2%} "
          f"({'on' if cfg.tax_on_sales else 'off'})")
    print(f"  targets       : {sign}{cfg.target_revenue_year:,.0f} "
          f"revenue, {cfg.target_turnover:.1f} stock turns")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  "
          f"({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
