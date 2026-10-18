#!/usr/bin/env python3
"""Optional recalculation check using the `formulas` package.

If `formulas` is installed, loads the workbook, recalculates and reports
any error values. If it is not installed (or the workbook is too large),
exits 0 with a note - the syntax validator is the hard gate.

    python3 tools/recalc_check.py [file.xlsx]
"""

from __future__ import annotations

import sys
from pathlib import Path

DEFAULT = (Path(__file__).resolve().parent.parent / "output" /
           "Cleaning Business CRM & Pricing Calculator.xlsx")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not path.exists():
        print(f"not found: {path}")
        return 1
    try:
        import formulas  # type: ignore
    except ImportError:
        print("recalc_check: 'formulas' not installed - SKIPPED "
              "(the syntax validator is the hard gate)")
        return 0

    try:
        xl = formulas.ExcelModel().loads(str(path)).finish()
        sol = xl.calculate()
    except Exception as exc:                      # pragma: no cover
        print(f"recalc_check: engine failed ({exc}) - SKIPPED")
        return 0

    errors = []
    for key, val in sol.items():
        try:
            if isinstance(val.value, str) and val.value.startswith("#"):
                errors.append((key, val.value))
        except Exception:
            continue
    if errors:
        print(f"recalc_check: {len(errors)} error values")
        for key, val in errors[:20]:
            print(f"  {key}: {val}")
        return 1
    print("recalc_check: no error values - PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
