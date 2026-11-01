#!/usr/bin/env python3
"""Build the Ultimate Inventory & Wholesale Order Manager workbook.

    python3 build_inventory_workbook.py
    python3 build_inventory_workbook.py -o "out/Stock.xlsx" --blank
    python3 build_inventory_workbook.py --currency "£" --rows 120
"""

from inventory_wholesale_spreadsheet.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
