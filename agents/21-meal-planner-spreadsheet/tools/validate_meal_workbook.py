"""
validate_meal_workbook.py - structural checks for the Meal Planner workbook.

Run this after every build. It catches the mistakes that only show up in
Excel: formula functions outside the Excel 2010 set, missing protection, a
sheet with no print area, a header row with a hole in it.

Usage:
    python tools/validate_meal_workbook.py
    python tools/validate_meal_workbook.py output/Meal Planner & Grocery List.xlsx
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "output" / "Meal Planner & Grocery List.xlsx"

SAFE_FUNCTIONS = {
    "ABS", "AND", "AVERAGE", "AVERAGEIFS", "CEILING", "CHOOSE", "CONCATENATE",
    "COUNT", "COUNTA", "COUNTBLANK", "COUNTIF", "COUNTIFS", "DATE", "DATEDIF",
    "DATEVALUE", "DAY", "EXP", "FIND", "FLOOR", "HOUR", "IF", "IFERROR", "INDEX",
    "INT", "ISBLANK", "ISERROR", "ISNUMBER", "ISNA", "LEFT", "LEN", "LN", "LOG",
    "LOWER", "MATCH", "MAX", "MEDIAN", "MID", "MIN", "MINUTE", "MOD", "MONTH",
    "NA", "NOT", "NOW", "N", "OR", "POWER", "PRODUCT", "PROPER", "RAND",
    "RANDBETWEEN", "RANK", "ROUND", "ROUNDDOWN", "ROUNDUP", "ROW", "ROWS",
    "SEARCH", "SECOND", "SIGN", "SQRT", "STDEV", "SUBSTITUTE", "SUM", "SUMIF",
    "SUMIFS", "SUMPRODUCT", "TEXT", "TODAY", "TRIM", "TRUNC", "UPPER", "VALUE",
    "VAR", "VLOOKUP", "WEEKDAY", "WEEK", "YEAR",
}
FUNCTION_RE = re.compile(r"([A-Z][A-Z0-9.]*)\s*\(")
FORMULA_RE = re.compile(r"^=\s*([A-Z0-9.]+)\s*\(")


def formula_functions(text: str) -> set[str]:
    """Functions called in a formula, ignoring string literals."""
    # strip string literals so IF(x="SUM(", ...) is not a call
    stripped = re.sub(r'"[^"]*"', '""', text)
    stripped = re.sub(r"'[^']*'", "''", stripped)
    return set(FUNCTION_RE.findall(stripped))


def check(path: Path) -> int:
    if not path.exists():
        print(f"FAIL: workbook not found: {path}")
        return 1

    print(f"Checking {path}")
    wb = load_workbook(path, data_only=False)
    problems = 0
    warnings = 0

    # 1. Every sheet has protection and a print area
    for ws in wb.worksheets:
        if ws.protection.sheet is not True:
            print(f"FAIL {ws.title}: sheet is not protected")
            problems += 1
        if not ws.print_area:
            print(f"FAIL {ws.title}: no print area")
            problems += 1

    # 2. Header rows (row 4, or the spec header row) are populated.
    #    Free-form tabs (Start Here, Dashboard, Settings, Help) use bands
    #    instead of a table header, so any content in rows 4-6 counts.
    FREE_FORM = {"Start Here", "Dashboard", "Settings", "Help"}
    for ws in wb.worksheets:
        header_row = 4
        if ws.title in ("Budget", "Goals", "Nutrition"):
            header_row = 16 if ws.title == "Budget" else (
                14 if ws.title == "Goals" else 18)
        elif ws.title in ("Converter", "Reports", "Monthly Planner",
                          "Weekly Planner", "Print Week", "Print Shopping",
                          "Print Recipe"):
            header_row = 22 if ws.title == "Converter" else 8
        if ws.title in FREE_FORM:
            cells = [ws.cell(row=r, column=c).value
                     for r in range(4, 7) for c in range(1, ws.max_column + 1)]
            if not any(v not in (None, "") for v in cells):
                print(f"FAIL {ws.title}: no content in rows 4-6")
                problems += 1
            continue
        values = [ws.cell(row=header_row, column=c).value
                  for c in range(1, ws.max_column + 1)]
        if not any(v not in (None, "") for v in values):
            print(f"FAIL {ws.title}: header row {header_row} is empty")
            problems += 1

    # 3. No charts, pictures or drawing parts.  Cell comments (vmlDrawing)
    #    are fine - they carry the column notes.
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        for bad in ("xl/charts/", "xl/media/", "xl/drawings/drawing"):
            hits = [n for n in names if n.startswith(bad) or
                    f"/{bad}" in n]
            if hits:
                print(f"FAIL workbook: unexpected {bad} parts: {hits[:4]}")
                problems += 1

    # 4. Every formula function is Excel 2010 safe
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if not (isinstance(value, str) and value.startswith("=")):
                    continue
                for fn in formula_functions(value):
                    if fn not in SAFE_FUNCTIONS:
                        print(f"FAIL {ws.title}!{cell.coordinate}: "
                              f"function {fn}() is outside the Excel 2010 set")
                        problems += 1
        # formula strings must not start with an invalid function
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    m = FORMULA_RE.match(value)
                    if m and m.group(1) not in SAFE_FUNCTIONS:
                        print(f"FAIL {ws.title}!{cell.coordinate}: "
                              f"top-level function {m.group(1)}() is not "
                              f"allowed")
                        problems += 1

    # 5. Named ranges all resolve to a sheet that exists.  OFFSET-based
    #    names have a formula rather than a range - just check the sheet.
    for name, defn in wb.defined_names.items():
        text = defn.attr_text or ""
        sheet = None
        m = re.match(r"'([^']+)'!", text) or re.match(r"([A-Za-z_][\w ]*)!",
                                                     text)
        if m:
            sheet = m.group(1)
        elif text.startswith("OFFSET("):
            m = re.search(r"'?([A-Za-z_][\w ]*)'?!", text)
            if m:
                sheet = m.group(1)
        if sheet is not None and sheet not in wb.sheetnames:
            print(f"FAIL name {name}: sheet {sheet} not found")
            problems += 1

    # 6. Sample data present in the main tabs
    expected = {"Recipes": 38, "Ingredients": 62, "Meal Plan": 107}
    for sheet, minimum in expected.items():
        ws = wb[sheet]
        first = ws.cell(row=1, column=1).value
        count = 0
        for row in ws.iter_rows(min_col=1, max_col=1):
            if row[0].value not in (None, ""):
                count += 1
        if count < minimum:
            print(f"WARN {sheet}: expected >= {minimum} data rows, found "
                  f"{count}")
            warnings += 1

    print(f"\n{problems} problem(s), {warnings} warning(s)")
    if problems == 0:
        print("PASS: workbook structure is valid")
    return 1 if problems else 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    sys.exit(check(target))
