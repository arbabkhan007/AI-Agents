#!/usr/bin/env python3
"""
Check a built meal planner workbook.

    python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"

The checks are deliberately boring and mechanical: is the tab order right,
is every sheet protected, does every formula only use functions that exist
in Excel 2010, does every cross-sheet reference point at a tab that is
really there, and are there any charts or pictures that should not be.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from collections import Counter
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from meal_planner_spreadsheet.build import SHEET_ORDER
except Exception:                                     # pragma: no cover
    SHEET_ORDER = [
        "Start Here", "Dashboard", "Weekly Planner", "Monthly Planner",
        "Settings", "Lists", "Household", "Recipes", "Recipe Ingredients",
        "Ingredients", "Meal Plan", "Grocery List", "Pantry", "Staples",
        "Leftovers", "Food Waste", "Meal Prep", "Dietary Filters",
        "Nutrition", "Budget", "Recipe Costs", "Converter", "Rotation",
        "Food Safety", "Fridge & Freezer", "Grocery Spending",
        "Store Prices", "Stores", "Events", "Goals", "Sustainability",
        "Reports", "Print Week", "Print Shopping", "Print Recipe", "Help",
    ]

#: every function the workbook is allowed to use.  All of these exist in
#: Excel 2007 and Excel 2010, so the file opens anywhere.
SAFE_FUNCTIONS = {
    "IF", "IFERROR", "AND", "OR", "NOT", "TRUE", "FALSE", "INDEX", "MATCH",
    "VLOOKUP", "HLOOKUP", "LOOKUP", "CHOOSE", "OFFSET", "INDIRECT",
    "COUNTIF", "COUNTIFS", "COUNT", "COUNTA", "COUNTBLANK", "SUM", "SUMIF",
    "SUMIFS", "SUMPRODUCT", "SUBTOTAL", "AVERAGE", "AVERAGEIF",
    "AVERAGEIFS", "MAX", "MIN", "LARGE", "SMALL", "ROUND", "ROUNDUP",
    "ROUNDDOWN", "MROUND", "INT", "MOD", "ABS", "CEILING", "FLOOR", "POWER",
    "SQRT", "EXP", "LN", "LOG", "LOG10", "TEXT", "VALUE", "LEFT", "RIGHT",
    "MID", "LEN", "LOWER", "UPPER", "PROPER", "TRIM", "CONCATENATE", "&",
    "REPT", "SUBSTITUTE", "REPLACE", "FIND", "SEARCH", "T", "N", "ISNUMBER",
    "ISTEXT", "ISBLANK", "ISERROR", "ISNA", "NA", "DATE", "TIME", "TODAY",
    "NOW", "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND", "WEEKDAY",
    "WEEKNUM", "EOMONTH", "EDATE", "DATEVALUE", "TIMEVALUE", "DAYS",
    "DAYS360", "NETWORKDAYS", "WORKDAY", "ROW", "ROWS", "COLUMN", "COLUMNS",
    "RANK", "PERCENTILE", "QUARTILE", "MEDIAN", "MODE", "STDEV", "STDEVP",
    "VAR", "VARP", "CORREL", "SLOPE", "INTERCEPT", "FORECAST", "TREND",
    "GROWTH", "NPV", "IRR", "PMT", "PV", "FV", "RATE", "NPER", "SLN",
    "SYD", "DDB", "XNPV", "XIRR", "SUMPRODUCT", "TRANSPOSE", "MMULT",
    "MDETERM", "MINVERSE", "ROMAN", "ARABIC", "BASE", "DECIMAL", "FACT",
    "COMBIN", "PERMUT", "GCD", "LCM", "SIGN", "TRUNC", "EVEN", "ODD",
    "DEGREES", "RADIANS", "PI", "SIN", "COS", "TAN", "ASIN", "ACOS",
    "ATAN", "ATAN2", "SINH", "COSH", "TANH", "SUMX2MY2", "SUMX2PY2",
    "SUMXMY2", "SERIESSUM", "MULTINOMIAL", "QUOTIENT", "RAND", "RANDBETWEEN",
    "CLEAN", "CODE", "CHAR", "DOLLAR", "FIXED", "EXACT", "CELL", "INFO",
    "HYPERLINK", "GETPIVOTDATA", "DATEDIF", "YEARFRAC",
}

SHEET_FILE = re.compile(r"^xl/worksheets/sheet(\d+)\.xml$")
SHEET_REF = re.compile(r"(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_ .&]*))!")
FORMULA = re.compile(r"<f[^>]*>(.*?)</f>", re.S)
DEFINED_NAME = re.compile(r'<definedName name="([^"]+)"[^>]*>(.*?)</definedName>',
                          re.S)


class Report:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def info(self, message: str) -> None:
        self.lines.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)
        self.lines.append("ERROR   " + message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        self.lines.append("WARNING " + message)

    @property
    def ok(self) -> bool:
        return not self.errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?",
                        default=os.path.join(
                            "output", "Meal Planner & Grocery List.xlsx"))
    parser.add_argument("--min-formulas", type=int, default=50000)
    parser.add_argument("--expect-sample-data", action="store_true",
                        help="fail if the registers look empty")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    path = args.workbook
    rep = Report()

    if not os.path.exists(path):
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2
    size = os.path.getsize(path)
    rep.info(f"{os.path.basename(path)}  ({size / 1024.0:,.0f} KB)")

    zf = zipfile.ZipFile(path)
    names = zf.namelist()

    # ---- sheet order -------------------------------------------------------
    workbook_xml = zf.read("xl/workbook.xml").decode("utf8", "replace")
    order = [unescape(n) for n in
             re.findall(r'<sheet name="([^"]+)"', workbook_xml)]
    if order == SHEET_ORDER:
        rep.info(f"tab order OK ({len(order)} tabs, first {order[0]!r}, "
                 f"last {order[-1]!r})")
    else:
        rep.error(f"tab order mismatch: expected {SHEET_ORDER}, "
                  f"found {order}")

    sheet_files = sorted(n for n in names if SHEET_FILE.match(n))
    if len(sheet_files) != len(SHEET_ORDER):
        rep.error(f"expected {len(SHEET_ORDER)} worksheet parts, "
                  f"found {len(sheet_files)}")
    else:
        rep.info(f"{len(sheet_files)} worksheet parts")

    # ---- per sheet ---------------------------------------------------------
    total_formulas = 0
    total_validations = 0
    total_conditional = 0
    total_comments = 0
    print_areas = 0
    empty_sheets = []
    functions = Counter()
    bad_refs = Counter()
    for index, name in enumerate(sheet_files, start=1):
        data = zf.read(name).decode("utf8", "replace")
        tab = order[index - 1] if index - 1 < len(order) else name
        formulas = FORMULA.findall(data)
        total_formulas += len(formulas)
        total_validations += data.count("<dataValidation ")
        total_conditional += data.count("<conditionalFormatting")
        # comments live in their own parts, not in the sheet XML
        total_comments += sum(zf.read(n).decode("utf8", "replace")
                              .count("<comment ")
                              for n in names
                              if re.match(r"xl/comments\d+\.xml$", n))

        if "<sheetProtection" not in data:
            rep.error(f"{tab}: sheet is not protected")
        # VML parts are the yellow tooltip boxes the data validation input
        # messages use - those are fine.  Real drawing parts are not.
        if re.search(r"<drawing r:id=", data):
            rep.error(f"{tab}: contains a drawing (charts and pictures are "
                      f"not allowed in this workbook)")
        if "<x14:sparkline" in data or "<chart" in data:
            rep.error(f"{tab}: contains a chart or sparkline")

        # Excel 2010 safe functions only
        for formula in formulas:
            for func in re.findall(r"([A-Z][A-Z0-9_.]*)\s*\(", formula):
                if func not in SAFE_FUNCTIONS:
                    functions[(tab, func)] += 1
            for sheet_name in SHEET_REF.findall(formula):
                ref = sheet_name[0] or sheet_name[1]
                if ref and ref not in SHEET_ORDER and not ref.startswith("#"):
                    bad_refs[(tab, ref)] += 1

        if args.expect_sample_data and not formulas and "<c " not in data:
            empty_sheets.append(tab)

    rep.info(f"{total_formulas:,} formulas")
    rep.info(f"{total_validations:,} data validations, "
             f"{total_conditional:,} conditional formats, "
             f"{total_comments:,} cell comments")
    print_areas = len(re.findall(
        r'<definedName name="_xlnm.Print_Area"', workbook_xml))
    rep.info(f"print areas set on {print_areas} of {len(sheet_files)} sheets")
    if print_areas < len(sheet_files):
        rep.warn(f"{len(sheet_files) - print_areas} sheets have no print "
                 f"area")

    if total_formulas < args.min_formulas:
        rep.error(f"only {total_formulas:,} formulas, expected at least "
                  f"{args.min_formulas:,}")
    for (tab, func), count in sorted(functions.items()):
        rep.error(f"{tab}: uses {func} which is not Excel 2010 safe "
                  f"({count} times)")
    for (tab, ref), count in sorted(bad_refs.items()):
        rep.error(f"{tab}: formula references unknown sheet {ref!r} "
                  f"({count} times)")
    if empty_sheets:
        rep.error(f"sheets with no data at all: {empty_sheets}")

    # ---- charts and drawings ----------------------------------------------
    drawings = [n for n in names
                if re.match(r"xl/drawings/drawing\d+\.xml$", n)]
    charts = [n for n in names if "charts/chart" in n]
    vml = [n for n in names if n.startswith("xl/drawings/vmlDrawing")]
    if drawings:
        rep.error(f"{len(drawings)} drawing parts found (none expected)")
    if charts:
        rep.error(f"{len(charts)} chart parts found (none expected)")
    if not charts and not drawings:
        rep.info(f"no charts and no drawings ({len(vml)} validation tooltip "
                 f"parts, which is expected)")

    # ---- defined names ------------------------------------------------------
    defined = [(unescape(n), unescape(t))
               for n, t in DEFINED_NAME.findall(workbook_xml)]
    rep.info(f"{len(defined)} defined names")
    for name, target in defined:
        target = target.strip()
        if "#REF!" in target:
            rep.error(f"defined name {name} points at #REF!")
        if target.startswith("="):
            target = target[1:]
        match = re.match(r"^(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_ .&]*))!", target)
        if match:
            sheet = match.group(1) or match.group(2)
            if sheet not in SHEET_ORDER:
                rep.error(f"defined name {name} points at unknown sheet "
                          f"{sheet!r}")

    # ---- cached error values ------------------------------------------------
    errors = 0
    for name in sheet_files:
        data = zf.read(name).decode("utf8", "replace")
        errors += data.count('t="e"')
    if errors:
        rep.warn(f"{errors} cells carry a cached error value")
    else:
        rep.info("no cached error values")

    # ---- workbook properties -------------------------------------------------
    if "docProps/core.xml" in names:
        core = zf.read("docProps/core.xml").decode("utf8", "replace")
        author = re.search(r"<dc:creator>(.*?)</dc:creator>", core)
        title = re.search(r"<dc:title>(.*?)</dc:title>", core)
        if author:
            rep.info(f"author: {unescape(author.group(1))}")
        if title:
            rep.info(f"title: {unescape(title.group(1))}")

    if not args.quiet:
        print("\n".join(rep.lines))
        print()
        if rep.ok:
            print(f"PASS - {os.path.basename(path)} looks good")
        else:
            print(f"FAIL - {len(rep.errors)} error(s), "
                  f"{len(rep.warnings)} warning(s)")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
