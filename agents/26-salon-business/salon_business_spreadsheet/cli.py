"""Command line entry point."""

from __future__ import annotations

import argparse
import datetime as _dt

from .build import build_workbook
from .config import Config


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(
        prog="build_salon_workbook",
        description="Build the Salon Business Management System workbook.")
    ap.add_argument("-o", "--output",
                    default="output/Salon Business Management System.xlsx")
    ap.add_argument("--blank", action="store_true",
                    help="no sample data - empty registers")
    ap.add_argument("--no-protect", action="store_true",
                    help="leave sheets unprotected (development only)")
    ap.add_argument("--password", default="premium")
    ap.add_argument("--author", default=None)
    ap.add_argument("--currency", default="$")
    ap.add_argument("--rows", type=int, default=None,
                    help="scale registers so Sales holds N rows")
    ap.add_argument("--today", default=None,
                    help="ISO date used as 'today' for sample data")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    cfg = Config()
    if a.blank:
        cfg.include_sample_data = False
    if a.no_protect:
        cfg.protect_sheets = False
    cfg.password = a.password
    if a.author:
        cfg.author = a.author
    cfg.currency_symbol = a.currency
    if a.rows:
        cfg.scale_rows(a.rows)
    if a.today:
        y, m, d = (int(x) for x in a.today.split("-"))
        cfg.today = _dt.date(y, m, d)

    path = build_workbook(a.output, cfg)
    if not a.quiet:
        print(path)


if __name__ == "__main__":
    main()
