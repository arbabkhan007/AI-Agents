#!/usr/bin/env python3
"""
tools/calc_check.py - recalculate the workbooks and compare with the
cached values the builder wrote.

Uses the third-party ``formulas`` package when it is installed.  When it
is not (a stock sandbox), the tool prints what it would have done and
exits 0 - the cached-value spot checks in verify_workbook.py still run.

Usage:
    python3 tools/calc_check.py [file.xlsx ...]      # default: products/
"""

import glob
import os
import sys


def main(argv):
    paths = argv or sorted(glob.glob("products/Catering_Business_Manager_"
                                     "*.xlsx"))
    if not paths:
        print("no workbooks found")
        return 1
    try:
        import formulas  # noqa: F401
    except ImportError:
        print("The 'formulas' recalculation package is not installed in "
              "this environment,")
        print("so live formula evaluation is skipped.  Cached values are "
              "checked by")
        print("tools/verify_workbook.py instead.")
        print("\nTo enable full recalculation:  pip install formulas")
        return 0

    import openpyxl
    failures = 0
    for path in paths:
        xl = formulas.ExcelModel().loads(path).finish()
        solved = xl.calculate()
        wb = openpyxl.load_workbook(path, data_only=True)
        bad = 0
        for key, val in solved.items():
            if "!" not in key:
                continue
            sheet, coord = key.rsplit("!", 1)
            sheet = sheet.strip("'")
            if sheet not in wb.sheetnames:
                continue
            try:
                cached = wb[sheet][coord].value
            except Exception:
                continue
            got = val.value[0, 0] if hasattr(val, "value") else val
            if isinstance(cached, (int, float)) and isinstance(
                    got, (int, float)):
                if abs(cached - float(got)) > max(0.01, abs(cached) * 1e-6):
                    bad += 1
        status = "PASS" if bad == 0 else "FAIL"
        print("%-4s %-52s %d mismatches" % (status,
                                            os.path.basename(path), bad))
        failures += bad
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
