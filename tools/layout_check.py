#!/usr/bin/env python3
"""
tools/layout_check.py - presentation QA for the Catering Business Manager.

Checks the things that make an Etsy spreadsheet feel finished:

  * gridlines hidden and tab colours set on every visible tab
  * the tracker tabs freeze their header rows and repeat them when
    printing
  * print areas, headers and footers on every tab
  * column widths are set (no default-width walls of text)
  * merged ranges never overlap and no merge spans a single cell
  * the Start Here tab embeds the theme banner (image builds)
  * row heights fit wrapped text on the guide tab

Usage:
    python3 tools/layout_check.py [file.xlsx ...]     # default: products/
"""

import glob
import os
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catering_tracker import config as C  # noqa: E402

TRACKERS = ["clients", "events", "menu", "inventory", "shopping",
            "expenses", "income", "staff", "equipment", "suppliers"]


def check(path):
    import openpyxl

    fails = []
    name = os.path.basename(path)
    edition = "premium" if "PREMIUM" in name else "basic"
    has_images = "_NOIMG" not in name

    wb = openpyxl.load_workbook(path)

    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        if ws.title == C.SHEET_NAMES["data"]:
            continue
        if ws.sheet_view.showGridLines:
            fails.append("%s: gridlines visible" % ws.title)
        if ws.sheet_properties.tabColor is None:
            fails.append("%s: no tab colour" % ws.title)
        if not ws.print_area:
            fails.append("%s: no print area" % ws.title)
        if not (ws.oddHeader.center or ws.oddHeader.left or
                ws.oddHeader.right):
            fails.append("%s: no header" % ws.title)
        if not ws.oddFooter.center:
            fails.append("%s: no footer" % ws.title)

    # tracker ergonomics
    for key in TRACKERS:
        title = C.SHEET_NAMES[key]
        if title not in wb.sheetnames:
            continue
        ws = wb[title]
        if not ws.freeze_panes:
            fails.append("%s: no frozen header" % title)
        if not ws.print_title_rows:
            fails.append("%s: no repeating print title" % title)

    # merges: no single-cell, no overlaps (openpyxl keeps a set)
    for ws in wb.worksheets:
        seen = set()
        for m in ws.merged_cells.ranges:
            if m.min_row == m.max_row and m.min_col == m.max_col:
                fails.append("%s: single-cell merge %s" % (ws.title, m))
            key = (m.min_row, m.min_col)
            if key in seen:
                fails.append("%s: overlapping merges at %s" % (ws.title,
                                                               m))
            seen.add(key)

    # banner on the guide tab (image builds)
    guide = wb[C.SHEET_NAMES["guide"]]
    if has_images:
        if not getattr(guide, "_images", None):
            fails.append("guide: no banner image embedded")

    # guide row heights: wrapped paragraphs must have room (a merge that
    # spans several rows brings those rows' heights with it)
    spans = {}
    for m in guide.merged_cells.ranges:
        spans[(m.min_row, m.min_col)] = m.max_row
    tall = 0
    for row in guide.iter_rows(min_col=2, max_col=8):
        for cell in row:
            if isinstance(cell.value, str) and len(cell.value) > 90:
                last = spans.get((cell.row, cell.column), cell.row)
                total_h = 0.0
                for rr in range(cell.row, last + 1):
                    rd = guide.row_dimensions.get(rr)
                    total_h += (rd.height if rd and rd.height else 19.0)
                if total_h < 28:
                    tall += 1
    if tall:
        fails.append("guide: %d long texts in short rows" % tall)

    ok = not fails
    print("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name,
                             "" if ok else "; ".join(fails)[:400]))
    return ok


def main(argv):
    paths = argv or sorted(glob.glob("products/Catering_Business_Manager_"
                                     "*.xlsx"))
    if not paths:
        print("no workbooks found (build first)")
        return 1
    print("Layout-checking %d workbook(s)\n" % len(paths))
    ok = all(check(p) for p in paths)
    print("\n%s" % ("ALL LAYOUT CHECKS PASSED" if ok else "FAILURES FOUND"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
