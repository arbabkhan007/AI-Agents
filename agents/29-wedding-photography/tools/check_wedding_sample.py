#!/usr/bin/env python3
"""Validate the wedding product's example data before it is built.

Four checks, every one of which has caught a real bug in this repo:

1. every key in a sample row is an *input* column on that register -
   a value written into a formula column is silently dropped and takes
   the formula for that row with it;
2. every value that feeds a drop-down exists in that drop-down's list -
   otherwise Excel flags the cell the moment a buyer clicks it (199 of
   these shipped undetected in an earlier product);
3. every ID that feeds a live list (Booking ID, Client ID, Staff ID,
   package name, campaign ID) actually exists on the register it points
   at - a Booking ID typo makes every downstream lookup return blank;
4. the rows fit in the register.

    python3 tools/check_wedding_sample.py
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wedding_photography_spreadsheet.config import (Config,          # noqa: E402
                                                    TIMELINE_EVENTS)
from wedding_photography_spreadsheet.build import REGISTER_MODULES   # noqa: E402
from wedding_photography_spreadsheet.names import CROSS_SHEET_NAMES  # noqa: E402
from wedding_photography_spreadsheet.sheets.settings import LISTS    # noqa: E402

ID_PATTERN = re.compile(r"^[A-Z]{3}-\d+$")

#: which register and ID column each live drop-down reads from
DYNAMIC_LISTS = CROSS_SHEET_NAMES


def main() -> int:
    cfg = Config()
    lists = {name: set(values) for name, values in LISTS}
    # the Settings blocks that are written row by row rather than as
    # a plain list literal
    lists["TimelineEventList"] = {label for _k, label, *_r
                                  in TIMELINE_EVENTS}
    lists["TimelineRoleList"] = {role for *_r, role in TIMELINE_EVENTS}

    specs = {}
    for module in REGISTER_MODULES:
        spec = module.spec(cfg)
        specs[spec.name] = spec

    # Build the live contents of every dynamic list (BookingList and
    # friends) out of the sample data itself, so a Booking ID typo in
    # Payments is caught here rather than by a buyer wondering why a
    # row is blank.
    live: dict = {}
    for list_name, (sheet, key) in DYNAMIC_LISTS.items():
        spec = specs.get(sheet)
        if spec is None:
            continue
        column = next((c for c in spec.columns if c.key == key), None)
        values = set()
        if column is not None and column.formula:
            # an auto-numbered ID column: PREFIX-0001 per sample row
            prefix = _prefix_for(cfg, sheet)
            if prefix:
                values = {f"{prefix}{n:0{_digits_for(cfg, sheet)}d}"
                          for n in range(1, len(spec.samples) + 1)}
        else:
            values = {str(row.get(key, "")) for row in spec.samples
                      if row.get(key, "")}
        live[list_name] = values

    problems = 0
    total_rows = 0
    for module in REGISTER_MODULES:
        spec = module.spec(cfg)
        inputs = {c.key for c in spec.columns if not c.formula}
        by_key = {c.key: c for c in spec.columns}
        rows = spec.samples
        total_rows += len(rows)

        if len(rows) > spec.rows:
            problems += 1
            print(f"{spec.name}: {len(rows)} sample rows will not fit "
                  f"in {spec.rows}")

        for index, row in enumerate(rows):
            extra = sorted(set(row) - inputs)
            if extra:
                problems += 1
                print(f"{spec.name} row {index}: not input columns "
                      f"-> {extra}")
            for key, value in row.items():
                column = by_key.get(key)
                if column is None or not column.validate:
                    continue
                source = column.validate.get("source")
                if not isinstance(source, str):
                    continue
                if not source.startswith("="):
                    # an inline list, e.g. ["Yes", "No"]
                    continue
                name = source.lstrip("=")
                if value in ("", None):
                    continue
                if name in lists:
                    if value not in lists[name]:
                        problems += 1
                        print(f"{spec.name}.{key} row {index}: "
                              f"{value!r} is not in {name}")
                elif name in live:
                    if value not in live[name]:
                        problems += 1
                        print(f"{spec.name}.{key} row {index}: "
                              f"{value!r} is not a live {name} value")
                else:
                    problems += 1
                    print(f"{spec.name}.{key} row {index}: unknown "
                          f"list {name}")

        print(f"  {spec.name:24s} {len(rows):4d} rows / {spec.rows:4d}, "
              f"{len(inputs)} input columns")

    print(f"\n{total_rows} sample rows checked, {problems} problems")
    return 1 if problems else 0


def _prefix_for(cfg, sheet: str) -> str:
    key = {"Wedding Bookings": "booking", "Client CRM": "client",
           "Photographer & Staff": "staff",
           "Marketing Calendar": "marketing"}.get(sheet)
    return cfg.prefix(key) if key else ""


def _digits_for(cfg, sheet: str) -> int:
    key = {"Wedding Bookings": "booking", "Client CRM": "client",
           "Photographer & Staff": "staff",
           "Marketing Calendar": "marketing"}.get(sheet)
    return cfg.digits(key) if key else 4


if __name__ == "__main__":
    raise SystemExit(main())
