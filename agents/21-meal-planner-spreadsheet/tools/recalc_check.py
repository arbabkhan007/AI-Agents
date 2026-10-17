"""
recalc_check.py - recalculates the workbook and looks for formula errors.

Requires the optional `formulas` package (pip install formulas).  It is a
deeper check than validate_meal_workbook.py: it actually evaluates every
formula and reports any that come back as an error.

Usage:
    python tools/recalc_check.py [path-to-workbook]
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "output" / "Meal Planner & Grocery List.xlsx"


def main() -> int:
    try:
        import formulas  # type: ignore
    except ImportError:
        print("SKIP: the 'formulas' package is not installed.")
        print("      pip install formulas, then run this check again.")
        return 0

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not path.exists():
        print(f"FAIL: workbook not found: {path}")
        return 1

    print(f"Recalculating {path} ...")
    xl_model = formulas.ExcelModel().loads(str(path)).finish()
    solution = xl_model.calculate()

    errors = []
    for key, value in solution.items():
        try:
            text = str(value.value[0, 0])
        except Exception:
            continue
        if text.startswith("#") and text not in ("#EMPTY", "#N/A"):
            errors.append((key, text))

    for key, text in errors[:50]:
        print(f"ERROR {key}: {text}")
    if errors:
        print(f"\n{len(errors)} formula error(s)")
        return 1
    print("PASS: every formula calculates without error")
    return 0


if __name__ == "__main__":
    sys.exit(main())
