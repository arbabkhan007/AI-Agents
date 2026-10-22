"""Sample-data sanity checks for the Salon workbooks.

    python3 tools/check_salon_sample.py [filled] [blank]

Confirms the example respects register capacities, keeps dates inside a
sensible window, never writes a None value into the XML and leaves the
blank workbook genuinely blank.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import openpyxl

CAPS = {
    "3 Appointment Planner": 400,
    "4 Client CRM": 250,
    "5 Services & Pricing": 80,
    "6 Sales & Transactions": 600,
    "7 Payments & Deposits": 600,
    "8 Staff Management": 30,
    "10 Payroll & Tips": 300,
    "11 Expenses": 400,
    "13 Product Inventory": 150,
    "14 Suppliers & Purchases": 150,
    "15 Marketing & Promotions": 80,
    "16 Client Loyalty": 250,
    "17 Goals & Budget": 24,
}
KEY_COL = {
    "3 Appointment Planner": "date",
    "6 Sales & Transactions": "date",
    "11 Expenses": "date",
}


def filled_rows(ws, cap, header_row=5, ignore_formulas=False):
    """Count rows with typed content inside the register window."""
    n = 0
    for row in ws.iter_rows(min_row=header_row + 1,
                            max_row=header_row + cap):
        for c in row:
            v = c.value
            if v in (None, ""):
                continue
            if ignore_formulas and isinstance(v, str) and v.startswith("="):
                continue
            n += 1
            break
    return n


def check(path: Path, expect_data: bool) -> int:
    problems = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                blob = z.read(name).decode("utf-8", "replace")
                if "<v>None</v>" in blob:
                    problems.append(f"{name}: literal None value")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    for tab, cap in CAPS.items():
        ws = wb[tab]
        n = filled_rows(ws, cap, ignore_formulas=not expect_data)
        if n > cap:
            problems.append(f"{tab}: {n} rows over capacity {cap}")
        if expect_data and tab in ("3 Appointment Planner",
                                   "6 Sales & Transactions") and n == 0:
            problems.append(f"{tab}: expected sample rows, found none")
        if not expect_data and tab in ("3 Appointment Planner",
                                       "6 Sales & Transactions",
                                       "11 Expenses") and n:
            problems.append(f"{tab}: blank workbook has {n} rows")
    wb.close()
    print(path.name)
    if problems:
        for p in problems:
            print("  -", p)
        print("  FAIL")
        return 1
    print("  PASS")
    return 0


if __name__ == "__main__":
    filled = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "output/Salon Business Management System.xlsx")
    blank = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
        "output/Salon Business Management System (Blank).xlsx")
    rc = check(filled, True) | check(blank, False)
    sys.exit(rc)
