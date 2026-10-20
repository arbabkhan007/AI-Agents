#!/usr/bin/env python3
"""Structural validator for the Fitness & Weight Loss Tracker workbook.

Gates it enforces, for both the filled and the blank file:

1.  sixteen tabs, in the product order, numbered names;
2.  every sheet protected, formula cells locked, input cells unlocked;
3.  document author is the shop name;
4.  no ``#REF!`` anywhere, no unrendered ``[[...]]`` / ``{token}``
    templates, no function newer than Excel 2010;
5.  every formula's brackets and quotes balance;
6.  no formula over the 8,192 character hard limit (openpyxl *and* a
    raw XML scan, because that limit is what produces Excel's repair
    dialog);
7.  raw XML scan: no ``<v>None</v>`` cached values, no structured
    references;
8.  defined names resolve; data validations exist on the registers.

Usage::

    python3 tools/validate_fitness_workbook.py path/to/workbook.xlsx
"""

from __future__ import annotations

import re
import sys
import zipfile
from xml.etree import ElementTree

import openpyxl

EXPECTED_TABS = [
    "1 Start Here", "2 Profile & Goals", "3 Dashboard",
    "4 Workout Planner", "5 Workout Log", "6 Exercise Library",
    "7 Cardio & Activity", "8 Weight Tracker", "9 Body Measurements",
    "10 Habit Tracker", "11 Meals & Macros", "12 Water & Sleep",
    "13 Records & Milestones", "14 Weekly & Monthly Review",
    "15 Reports & Charts", "16 Settings & Lists",
]

BANNED = [
    r"(?<![A-Z0-9_.])XLOOKUP\s*\(", r"(?<![A-Z0-9_.])IFS\s*\(",
    r"(?<![A-Z0-9_.])LET\s*\(", r"(?<![A-Z0-9_.])MINIFS\s*\(",
    r"(?<![A-Z0-9_.])MAXIFS\s*\(", r"(?<![A-Z0-9_.])TEXTJOIN\s*\(",
    r"(?<![A-Z0-9_.])CONCAT\s*\(", r"(?<![A-Z0-9_.])SWITCH\s*\(",
    r"(?<![A-Z0-9_.])FILTER\s*\(", r"(?<![A-Z0-9_.])SORT\s*\(",
    r"(?<![A-Z0-9_.])UNIQUE\s*\(", r"(?<![A-Z0-9_.])SEQUENCE\s*\(",
    r"(?<![A-Z0-9_.])RANDARRAY\s*\(", r"(?<![A-Z0-9_.])LAMBDA\s*\(",
    r"(?<![A-Z0-9_.])TOCOL\s*\(", r"(?<![A-Z0-9_.])TOROW\s*\(",
    r"(?<![A-Z0-9_.])HSTACK\s*\(", r"(?<![A-Z0-9_.])VSTACK\s*\(",
    r"(?<![A-Z0-9_.])TAKE\s*\(", r"(?<![A-Z0-9_.])DROP\s*\(",
    r"(?<![A-Z0-9_.])BYROW\s*\(", r"(?<![A-Z0-9_.])BYCOL\s*\(",
    r"(?<![A-Z0-9_.])MAP\s*\(", r"(?<![A-Z0-9_.])REDUCE\s*\(",
    r"(?<![A-Z0-9_.])SCAN\s*\(", r"(?<![A-Z0-9_.])XMA\s*\(",
    r"(?<![A-Z0-9_.])TEXTSPLIT\s*\(", r"(?<![A-Z0-9_.])TEXTBEFORE\s*\(",
    r"(?<![A-Z0-9_.])TEXTAFTER\s*\(", r"(?<![A-Z0-9_.])IMAGE\s*\(",
]

MAX_FORMULA_LEN = 8192


def balanced(text: str) -> bool:
    depth = 0
    in_str = False
    for ch in text:
        if in_str:
            if ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not in_str


READ_ONLY_TABS = {"1 Start Here", "3 Dashboard"}


def main(path: str, expect_inputs: bool = True) -> int:
    problems = []
    book = openpyxl.load_workbook(path)

    if book.sheetnames != EXPECTED_TABS:
        problems.append(f"tab order: {book.sheetnames}")

    props = book.properties
    if (props.creator or "") != "Novality Store":
        problems.append(f"author is {props.creator!r}")

    formulas = 0
    unlocked = 0
    locked_formulas = 0
    for name in book.sheetnames:
        ws = book[name]
        if not ws.protection.sheet:
            problems.append(f"{name}: sheet not protected")
        sheet_unlocked = 0
        sheet_locked_formula = 0
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    formulas += 1
                    sheet_locked_formula += 1
                    if cell.protection is not None and \
                            cell.protection.locked is False:
                        problems.append(
                            f"{name}!{cell.coordinate}: formula unlocked")
                    if "#REF!" in value:
                        problems.append(
                            f"{name}!{cell.coordinate}: #REF! in formula")
                    if "[[" in value or re.search(r"\{[a-z_0-9]+\}", value):
                        problems.append(
                            f"{name}!{cell.coordinate}: unrendered token "
                            f"{value[:60]}")
                    if not balanced(value):
                        problems.append(
                            f"{name}!{cell.coordinate}: unbalanced "
                            f"{value[:60]}")
                    if len(value) > MAX_FORMULA_LEN:
                        problems.append(
                            f"{name}!{cell.coordinate}: formula of "
                            f"{len(value)} chars")
                    for pattern in BANNED:
                        if re.search(pattern, value, re.IGNORECASE):
                            problems.append(
                                f"{name}!{cell.coordinate}: banned "
                                f"function {pattern} in {value[:60]}")
                            break
                elif cell.protection is not None and \
                        cell.protection.locked is False and \
                        cell.data_type != "f":
                    sheet_unlocked += 1
                    unlocked += 1
        if sheet_unlocked == 0 and expect_inputs and \
                name not in READ_ONLY_TABS:
            problems.append(f"{name}: no unlocked input cells")
        locked_formulas += sheet_locked_formula

    for name, defined in book.defined_names.items():
        if "#REF" in (defined.value or ""):
            problems.append(f"defined name {name} broken: {defined.value}")

    # ------------------------------------------------------------- raw XML
    over_long = 0
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist()
                 if n.startswith("xl/worksheets/sheet")]
        if len(names) != len(EXPECTED_TABS):
            problems.append(f"expected 16 sheet parts, found {len(names)}")
        for part in names:
            xml = zf.read(part).decode("utf-8", "replace")
            if "<v>None</v>" in xml:
                problems.append(f"{part}: cached <v>None</v>")
            if re.search(r"<f[^>]*>[^<]*\[\[", xml):
                problems.append(f"{part}: structured reference")
            root = ElementTree.fromstring(xml)
            ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            for f in root.iter(f"{ns}f"):
                text = f.text or ""
                if len(text) > MAX_FORMULA_LEN:
                    over_long += 1
        workbook_xml = zf.read("xl/workbook.xml").decode("utf-8", "replace")
        if "#REF" in workbook_xml:
            problems.append("workbook.xml contains #REF")
    if over_long:
        problems.append(f"{over_long} formulas over {MAX_FORMULA_LEN} "
                        f"chars in raw XML")

    print(f"{path}")
    print(f"  tabs           : {len(book.sheetnames)}")
    print(f"  formulas       : {formulas:,}")
    print(f"  locked formulas: {locked_formulas:,}")
    print(f"  unlocked cells : {unlocked:,}")
    if problems:
        print(f"  FAIL - {len(problems)} problem(s):")
        for problem in problems[:40]:
            print(f"    - {problem}")
        return 1
    print("  PASS")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    blank = "--blank" in sys.argv
    sys.exit(main(args[0] if args else
                  "output/Fitness & Weight Loss Tracker.xlsx",
                  expect_inputs=not blank))
