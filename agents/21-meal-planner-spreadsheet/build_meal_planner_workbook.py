#!/usr/bin/env python3
"""Build the Automated Meal Planner & Grocery List Spreadsheet.

    python build_meal_planner_workbook.py
    python build_meal_planner_workbook.py --blank -o "output/Blank.xlsx"
    python build_meal_planner_workbook.py --rows 400 --currency "£"

Everything lives in the `meal_planner_spreadsheet` package; this file is
just a friendly front door so you do not have to remember `-m`.
"""

from __future__ import annotations

import sys

from meal_planner_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
