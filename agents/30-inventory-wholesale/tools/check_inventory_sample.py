#!/usr/bin/env python3
"""Validate the inventory product's example data before it is built.

Five checks, every one of which has caught a real bug in this repo:

1. every key in a sample row is an *input* column on that register -
   a value written into a formula column is silently dropped and takes
   the formula for that row with it;
2. every value that feeds a drop-down exists in that drop-down's list -
   otherwise Excel flags the cell the moment a buyer clicks it (199 of
   these shipped undetected in an earlier product);
3. every ID that feeds a live list (SKU, Supplier ID, Customer ID,
   location, staff name) actually exists on the register it points at -
   one SKU typo makes every downstream lookup return blank, and on this
   product a SKU is the join key for all seventeen registers;
4. the rows fit in the register;
5. nothing claims stock it cannot have: every SKU used by a purchase
   order, order line, sale, return, movement, count or bin exists in
   the product database.

    python3 tools/check_inventory_sample.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_wholesale_spreadsheet.config import (Config,          # noqa: E402
                                                    MOVEMENT_TYPES,
                                                    PAYMENT_TERMS)
from inventory_wholesale_spreadsheet.build import REGISTER_MODULES   # noqa: E402
from inventory_wholesale_spreadsheet.names import (                  # noqa: E402
    CROSS_SHEET_NAMES)
from inventory_wholesale_spreadsheet.sheets.settings import LISTS    # noqa: E402

#: which register and column each live drop-down reads from
DYNAMIC_LISTS = CROSS_SHEET_NAMES

#: sheets whose ID column is generated, and the config key that names
#: the prefix - so the live list can be rebuilt from the row count
AUTO_IDS = {
    "Supplier Database": "supplier",
    "Wholesale Customer CRM": "customer",
}

#: every register that names a SKU, and the column it uses
SKU_COLUMNS = [
    ("Stock Movement Log", "sku"),
    ("Purchase Orders", "sku"),
    ("Wholesale Orders", "sku"),
    ("Retail Sales Tracker", "sku"),
    ("Returns & Damaged Goods", "sku"),
    ("Warehouse Locations", "sku"),
    ("Stock Audit", "sku"),
]


def main() -> int:
    cfg = Config()
    lists = {name: set(values) for name, values in LISTS}
    # the Settings blocks written row by row rather than as a list
    lists["MovementTypeList"] = {name for name, _sign, _blurb
                                 in MOVEMENT_TYPES}
    lists["PaymentTermsList"] = {label for label, _days in PAYMENT_TERMS}

    specs = {}
    for module in REGISTER_MODULES:
        spec = module.spec(cfg)
        specs[spec.name] = spec

    # Build the live contents of every dynamic list out of the sample
    # data itself, so a SKU typo in Purchase Orders is caught here
    # rather than by a buyer wondering why a row is blank.
    live: dict = {}
    for list_name, (sheet, key) in DYNAMIC_LISTS.items():
        spec = specs.get(sheet)
        if spec is None:
            continue
        column = next((c for c in spec.columns if c.key == key), None)
        values = set()
        if column is not None and column.formula:
            prefix_key = AUTO_IDS.get(sheet)
            if prefix_key:
                digits = cfg.digits(prefix_key)
                prefix = cfg.prefix(prefix_key)
                values = {f"{prefix}{n:0{digits}d}"
                          for n in range(1, len(spec.samples) + 1)}
        else:
            values = {str(row.get(key, "")) for row in spec.samples
                      if row.get(key, "") != ""}
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
                    continue            # an inline list, e.g. Yes/No
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

        print(f"  {spec.name:26s} {len(rows):4d} rows / {spec.rows:4d}, "
              f"{len(inputs)} input columns")

    # ---- the join key the whole product turns on -------------------
    catalogue = {str(row.get("sku", ""))
                 for row in specs["Product & SKU Database"].samples}
    orphans = 0
    for sheet, key in SKU_COLUMNS:
        spec = specs.get(sheet)
        if spec is None:
            continue
        for index, row in enumerate(spec.samples):
            sku = str(row.get(key, ""))
            if sku and sku not in catalogue:
                problems += 1
                orphans += 1
                print(f"{sheet} row {index}: SKU {sku!r} is not in the "
                      f"product database")
    if not orphans:
        print(f"\n  every SKU on every register resolves to one of the "
              f"{len(catalogue)} catalogue products")

    print(f"\n{total_rows} sample rows checked, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
