#!/usr/bin/env python3
"""
Recalculate a generated workbook with the ``formulas`` engine and report every
cell that evaluates to an Excel error (#REF!, #NAME?, #VALUE!, #DIV/0! ...).

This is the closest thing to opening the file in Excel without Excel: every
formula is parsed and evaluated for real, so broken references, typos and
unsupported functions show up here instead of in a customer's hands.

    pip install formulas
    python3 tools/calc_check_santa.py products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx

Known limitation: the ``formulas`` package cannot evaluate OFFSET-based defined
names (the auto-expanding dropdown lists), so those report #REF! here while
Excel and Google Sheets handle them normally.  They are listed separately as
"engine limitations" rather than failures.
"""

import glob
import logging
import re
import sys
import warnings

logging.disable(logging.CRITICAL)
warnings.simplefilter("ignore")

import formulas                                     # noqa: E402
import openpyxl                                     # noqa: E402


def check(path, verbose=True, compare=True):
    xl = formulas.ExcelModel().loads(path).finish()
    sol = xl.calculate()

    wb = openpyxl.load_workbook(path)
    wbv = openpyxl.load_workbook(path, data_only=True)
    fname = path.split("/")[-1]          # engine keeps the filename verbatim
    titles = {t.upper(): t for t in wb.sheetnames}

    def key_for(title, coord):
        # the engine uppercases the sheet title but keeps the filename as-is
        return "'[%s]%s'!%s" % (fname, title.upper(), coord)

    def formula_of(key):
        m = re.match(r"^'\[.*\](.*)'!([A-Z]+\d+)$", key)
        if not m:
            return None, None
        sheet, coord = m.group(1), m.group(2)
        real = titles.get(sheet.upper())
        if real is not None:
            return real, wb[real][coord].value
        return sheet, None

    mismatches = []
    if compare:
        for ws in wb.worksheets:
            wsv = wbv[ws.title]
            for row in ws.iter_rows():
                for cell in row:
                    v = cell.value
                    if not (isinstance(v, str) and v.startswith("=")):
                        continue
                    got = sol.get(key_for(ws.title, cell.coordinate))
                    if got is None:
                        continue
                    try:
                        calc = got.value[0, 0]
                    except Exception:
                        calc = got
                    cached = wsv[cell.coordinate].value
                    if calc is None and cached is None:
                        continue
                    if isinstance(calc, (int, float)) and \
                            isinstance(cached, (int, float)):
                        if abs(float(calc) - float(cached)) > 1e-6:
                            mismatches.append((ws.title, cell.coordinate,
                                               calc, cached))
                    elif str(calc).strip() != str(cached).strip():
                        mismatches.append((ws.title, cell.coordinate,
                                           calc, cached))

    errors, limits = [], []
    for key, value in sol.items():
        try:
            val = value.value[0, 0] if hasattr(value, "value") else value
        except Exception:
            continue
        text = str(val).strip()
        if not text.startswith("#"):
            continue
        if text == "#":            # a literal "#" header cell, not an error
            continue
        sheet, f = formula_of(key)
        if sheet is None:          # workbook-level defined name, not a cell
            limits.append((text, key, sheet, f))
            continue
        # things the engine cannot do but Excel and Google Sheets can:
        #   OFFSET() defined names (the auto-expanding dropdown lists)
        #   HYPERLINK()  (not implemented in the formulas package)
        if "OFFSET" in key.upper() or (f and "HYPERLINK(" in str(f).upper()):
            limits.append((text, key, sheet, f))
            continue
        errors.append((text, key, sheet, f))

    if verbose:
        print("=" * 78)
        print(path)
        print("  cells evaluated : %d" % len(sol))
        print("  engine limitations (fine in Excel / Sheets) : %d %s"
              % (len(limits), sorted({t for t, k, s2, f in limits})))
        if mismatches:
            print("  CACHED VALUE OUT OF DATE (%d):" % len(mismatches))
            for sheet, coord, calc, cached in mismatches[:15]:
                print("      %-20s %-6s recalcs to %r, file says %r"
                      % (sheet, coord, str(calc)[:30], str(cached)[:30]))
            if len(mismatches) > 15:
                print("      ... and %d more" % (len(mismatches) - 15))
        if errors:
            print("  ERRORS (%d):" % len(errors))
            for text, key, sheet, f in errors[:30]:
                print("    %-9s %-28s %s" % (text, (sheet or "?"),
                                             str(f)[:90]))
            if len(errors) > 30:
                print("    ... and %d more" % (len(errors) - 30))
        else:
            print("  ERRORS : none \u2713")
    return errors + mismatches, limits


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
        errors, _ = check(p)
        total += len(errors)
    print("=" * 78)
    print("clean" if not total else "%d error cell(s) across %d file(s)"
          % (total, len(paths)))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
