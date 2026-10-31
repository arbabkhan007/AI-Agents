#!/usr/bin/env python3
"""Parenthesis and quote balance check for every formula in a workbook.

Concatenated nested IFs are the one mistake a generator makes that no
amount of reading catches, so this walks the saved .xlsx and counts
brackets and quotes on every formula cell.

    python3 tools/check_parens.py output/Workbook.xlsx
"""

from __future__ import annotations

import re
import sys
import zipfile
from typing import Dict, Iterable, List, Tuple
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sheet_names(book: zipfile.ZipFile) -> Dict[str, str]:
    """target path -> sheet name, in workbook order."""
    rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    by_id = {
        rel.get("Id"): rel.get("Target").lstrip("/")
        for rel in rels
    }
    root = ET.fromstring(book.read("xl/workbook.xml"))
    names: Dict[str, str] = {}
    for sheet in root.iter(f"{NS}sheet"):
        rid = sheet.get(
            "{http://schemas.openxmlformats.org/officeDocument/"
            "2006/relationships}id")
        target = by_id.get(rid, "")
        if not target.startswith("xl/"):
            target = "xl/" + target
        names[target] = sheet.get("name", "?")
    return names


def balanced(formula: str) -> Tuple[bool, str]:
    """Is the formula balanced for brackets and double quotes?"""
    depth = 0
    in_string = False
    index = 0
    while index < len(formula):
        char = formula[index]
        if char == '"':
            if in_string and index + 1 < len(formula) \
                    and formula[index + 1] == '"':
                index += 2
                continue
            in_string = not in_string
        elif not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    return False, "closes a bracket that never opened"
        index += 1
    if in_string:
        return False, "odd number of double quotes"
    if depth:
        return False, f"{depth} bracket(s) left open"
    return True, ""


def suspicious(formula: str) -> str:
    """Cheap smells that are always bugs in a generated workbook."""
    if "{" in formula or "}" in formula:
        return "unrendered template placeholder"
    if "[[" in formula or "]]" in formula:
        return "unrendered sheet reference"
    if re.search(r"#(REF|NAME|VALUE|DIV/0|N/A)", formula):
        return "hard coded error value"
    if ",," in formula.replace('",,"', ""):
        return "empty argument"
    return ""


def check(path: str) -> int:
    problems: List[str] = []
    total = 0
    with zipfile.ZipFile(path) as book:
        names = sheet_names(book)
        targets: Iterable[str] = [n for n in book.namelist()
                                  if n.startswith("xl/worksheets/sheet")]
        for target in sorted(targets):
            sheet = names.get(target, target)
            root = ET.fromstring(book.read(target))
            for cell in root.iter(f"{NS}c"):
                node = cell.find(f"{NS}f")
                if node is None or not node.text:
                    continue
                total += 1
                formula = node.text
                ok, why = balanced(formula)
                smell = suspicious(formula)
                if not ok or smell:
                    ref = cell.get("r", "?")
                    problems.append(
                        f"{sheet}!{ref}: {why or smell}\n    ={formula[:160]}")
    print(f"{path}: {total:,} formulas checked")
    if problems:
        print(f"  {len(problems)} problem(s):")
        for line in problems[:40]:
            print("  - " + line)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        return 1
    print("  all balanced, no placeholders left behind")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(max(check(arg) for arg in sys.argv[1:]))
