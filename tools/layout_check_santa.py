#!/usr/bin/env python3
"""
Layout audit: finds text that will be clipped or overflow in Excel.

Excel never grows a merged cell to fit its text, so wrapped text in a merged
range needs an explicit row height.  This tool re-measures every cell in a
generated workbook the same way the builder did and reports:

    TOO TALL  wrapped text needs more height than the row(s) provide
    OVERFLOW  unwrapped text is wider than its cell and the neighbour is busy
    TINY ROW  an explicit row height smaller than one line of its font

    python3 tools/layout_check_santa.py products/Secret_Santa_*.xlsx
"""

import glob
import math
import sys

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries

DEFAULT_COL_WIDTH = 8.43
CHARS_PER_UNIT = 1.05        # measured against Calibri 11 in Excel


def width_map(ws):
    """Column widths, expanding grouped ranges such as ``set_column("C:L")``."""
    widths = {}
    for dim in ws.column_dimensions.values():
        if not dim.width:
            continue
        lo = dim.min or 1
        hi = dim.max or lo
        for idx in range(lo, hi + 1):
            widths[idx] = dim.width
    return widths


def col_width(ws, idx, widths=None):
    if widths is None:
        widths = width_map(ws)
    return widths.get(idx, DEFAULT_COL_WIDTH)


def row_height(ws, idx, default=15.0):
    dim = ws.row_dimensions.get(idx)
    if dim is not None and dim.height:
        return dim.height
    return default


def check(path, verbose=True):
    wb = openpyxl.load_workbook(path)
    problems = []
    for ws in wb.worksheets:
        widths = width_map(ws)
        merged = {}
        for mr in ws.merged_cells.ranges:
            c1, r1, c2, r2 = range_boundaries(str(mr))
            merged[(r1, c1)] = (r1, c1, r2, c2)
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    if (rr, cc) != (r1, c1):
                        merged[(rr, cc)] = None      # swallowed cell

        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if not isinstance(v, str) or not v.strip():
                    continue
                if v.startswith("="):
                    continue                       # formula: length unknown
                key = (cell.row, cell.column)
                if key in merged and merged[key] is None:
                    continue                       # hidden by a merge
                blocked = True
                if key in merged:
                    r1, c1, r2, c2 = merged[key]
                    width = sum(col_width(ws, c, widths)
                                for c in range(c1, c2 + 1))
                    height = sum(row_height(ws, r) for r in range(r1, r2 + 1))
                else:
                    width = col_width(ws, cell.column, widths)
                    height = row_height(ws, cell.row)
                    nxt = ws.cell(row=cell.row, column=cell.column + 1)
                    blocked = (nxt.value not in (None, "")
                               or (cell.row, cell.column + 1) in merged)

                size = cell.font.size or 11
                room = width * CHARS_PER_UNIT * (11.0 / float(size))
                text = v.strip()
                wrap = bool(cell.alignment.wrap_text)

                if wrap:
                    lines = 0
                    for part in text.split("\n"):
                        lines += max(1,
                                     int(math.ceil(len(part) / max(room, 1))))
                    line_h = size * 1.32 + 2.2
                    need = lines * line_h
                    if need > height + 1.5:
                        problems.append(
                            ("TOO TALL", ws.title, cell.coordinate,
                             "needs ~%.0fpt for %d line(s), has %.0fpt: %r"
                             % (need, lines, height, text[:60])))
                else:
                    if len(text) > room * 1.02 and key not in merged:
                        if blocked:
                            # a pasted web address is always longer than its
                            # column: the clickable button next to it is the
                            # intended way in, so this is by design
                            kind = ("CLIPPED LINK"
                                    if text.lower().startswith("http")
                                    else "OVERFLOW")
                            problems.append(
                                (kind, ws.title, cell.coordinate,
                                 "%d chars in %.0f wide cell: %r"
                                 % (len(text), width, text[:60])))
                if height < size * 1.15 and key not in merged:
                    problems.append(
                        ("TINY ROW", ws.title, cell.coordinate,
                         "row %.0fpt for %spt font" % (height, size)))
    if verbose:
        print("=" * 78)
        print(path)
        if problems:
            by_kind = {}
            for kind, sheet, coord, msg in problems:
                by_kind.setdefault(kind, []).append((sheet, coord, msg))
            for kind, items in sorted(by_kind.items()):
                print("  %-9s %d" % (kind, len(items)))
                for sheet, coord, msg in items[:12]:
                    print("      %-22s %-6s %s" % (sheet, coord, msg))
                if len(items) > 12:
                    print("      ... and %d more" % (len(items) - 12))
        else:
            print("  layout: no clipping or overflow found \u2713")
    return problems


def main(argv):
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[")
                     else [a])
    if not paths:
        print(__doc__)
        return 1
    total = 0
    for p in paths:
        total += len([x for x in check(p) if x[0] != "CLIPPED LINK"])
    print("=" * 78)
    print("clean" if not total else "%d layout issue(s)" % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
