"""
validate_social_workbook.py - structural checks for the Social Media
Content Calendar & Analytics Planner workbook.

Run this after every build. It catches the mistakes that only show up in
Excel: formula functions outside the Excel 2010 set, missing protection, a
broken defined name, the wrong sheet order, an author name that breaks the
listing.

Usage:
    python tools/validate_social_workbook.py
    python tools/validate_social_workbook.py "output/Social Media Content Planner.xlsx"
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "output" / "Social Media Content Planner.xlsx"

CREATOR = "Novality Store"
PASSWORD = "premium"

SHEET_ORDER = [
    "Start Here", "Dashboard", "Annual Dashboard", "Settings", "Lists",
    "Brand Voice", "Accounts", "Audience Personas", "Content Pillars",
    "Content Calendar", "Month View", "Workflow",
    "Idea Bank", "Caption Bank", "Hashtag Bank",
    "Instagram", "TikTok", "Pinterest", "YouTube", "Facebook",
    "Campaigns", "Launch Planner", "Seasonal Planner",
    "Influencers", "UGC Tracker", "Repurposing", "Competitors", "Trends",
    "Analytics", "Performance", "AB Tests", "Ads", "Assets",
    "Goals", "Budget", "Team", "Tasks", "Compliance",
    "Reports", "Print Brief", "Print Week", "Help",
    "Calc",
]

SAFE_FUNCTIONS = {
    "ABS", "AND", "AVERAGE", "AVERAGEIF", "AVERAGEIFS", "CEILING", "CHAR",
    "CHOOSE", "COLUMN", "CONCATENATE", "COUNT", "COUNTA", "COUNTBLANK",
    "COUNTIF", "COUNTIFS", "DATE", "DATEDIF", "DATEVALUE", "DAY", "EDATE",
    "EOMONTH",
    "EXP", "FIND", "FLOOR", "HOUR", "HYPERLINK", "IF", "IFERROR", "INDEX",
    "INT", "ISBLANK", "ISERROR", "ISNUMBER", "ISNA", "LEFT", "LEN", "LN",
    "LOG", "LOWER", "MATCH", "MAX", "MEDIAN", "MID", "MIN", "MINUTE", "MOD",
    "MONTH", "NA", "NOT", "NOW", "N", "OR", "POWER", "PRODUCT", "PROPER",
    "RAND", "RANDBETWEEN", "RANK", "ROUND", "ROUNDDOWN", "ROUNDUP", "ROW",
    "ROWS", "SEARCH", "SECOND", "SIGN", "SMALL", "SQRT", "STDEV",
    "SUBSTITUTE", "SUM", "SUMIF", "SUMIFS", "SUMPRODUCT", "TEXT", "TODAY",
    "TRIM", "TRUNC", "UPPER", "VALUE", "VAR", "VLOOKUP", "WEEKDAY", "WEEK",
    "YEAR", "LARGE",
}

#: Deliberately banned even where a modern Excel knows them: they break
#: Excel 2010, Google Sheets imports, or Numbers.
MODERN_ONLY = {
    "XLOOKUP", "XMATCH", "IFS", "TEXTJOIN", "TEXTSPLIT", "MAXIFS",
    "MINIFS", "CONCAT", "SWITCH", "LET", "FILTER", "SORT", "UNIQUE",
    "SEQUENCE", "RANDARRAY", "AGGREGATE", "IFNA", "XLOOKUP", "WEBSERVICE",
}

FUNCTION_RE = re.compile(r"([A-Z][A-Z0-9.]*)\s*\(")


def formula_functions(text: str) -> set:
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

    # 1. Document properties -------------------------------------------------
    if wb.properties.creator != CREATOR:
        print(f"FAIL: creator is {wb.properties.creator!r}, "
              f"expected {CREATOR!r}")
        problems += 1
    modified = getattr(wb.properties, "lastModifiedBy", None)
    if modified not in (None, CREATOR):
        print(f"FAIL: lastModifiedBy is {modified!r}")
        problems += 1

    # 2. Sheet order and visibility -----------------------------------------
    if wb.sheetnames != SHEET_ORDER:
        print("FAIL: sheet order does not match the product spec")
        print(f"   got      : {wb.sheetnames}")
        print(f"   expected : {SHEET_ORDER}")
        problems += 1
    hidden = [ws.title for ws in wb.worksheets if ws.sheet_state != "visible"]
    if hidden != ["Calc"]:
        print(f"FAIL: hidden sheets are {hidden}, expected ['Calc']")
        problems += 1

    # 3. Protection on every sheet ------------------------------------------
    for ws in wb.worksheets:
        if ws.protection.sheet is not True:
            print(f"FAIL {ws.title}: sheet is not protected")
            problems += 1
        if not ws.protection.password and not ws.protection.set_password:
            print(f"FAIL {ws.title}: no protection password")
            problems += 1

    # 4. Defined names resolve ----------------------------------------------
    broken_names = 0
    name_count = 0
    for name, defined in wb.defined_names.items():
        name_count += 1
        value = defined.value if hasattr(defined, "value") else str(defined)
        if value is None or "#" in str(value):
            print(f"FAIL: defined name {name!r} looks broken: {value!r}")
            broken_names += 1
            continue
        for sheet in re.findall(r"'([^']+)'!", str(value)):
            if sheet not in wb.sheetnames:
                print(f"FAIL: defined name {name!r} points at missing "
                      f"sheet {sheet!r}")
                broken_names += 1
    problems += broken_names
    if name_count < 40:
        print(f"FAIL: only {name_count} defined names (expected at least 40)")
        problems += 1
    else:
        print(f"  defined names: {name_count}")

    # 5. Formula functions are Excel 2010 safe -------------------------------
    banned_hits = 0
    unsafe_hits = 0
    formula_count = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if not (isinstance(value, str) and value.startswith("=")):
                    continue
                formula_count += 1
                funcs = formula_functions(value)
                for fn in funcs:
                    if fn in MODERN_ONLY:
                        print(f"FAIL {ws.title}!{cell.coordinate}: "
                              f"banned function {fn}()")
                        banned_hits += 1
                    elif fn not in SAFE_FUNCTIONS:
                        print(f"FAIL {ws.title}!{cell.coordinate}: "
                              f"function outside the Excel 2010 set: {fn}()")
                        unsafe_hits += 1
    problems += banned_hits + unsafe_hits
    print(f"  formulas scanned: {formula_count}")

    # 6. Print areas ---------------------------------------------------------
    for ws in wb.worksheets:
        if ws.title == "Calc":
            continue
        if not ws.print_area:
            print(f"WARN {ws.title}: no print area set")
            warnings += 1

    print(f"  sheets: {len(wb.sheetnames)}  problems: {problems}  "
          f"warnings: {warnings}")
    if problems:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    raise SystemExit(check(target))
