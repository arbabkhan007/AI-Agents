#!/usr/bin/env python3
"""Optional recalculation check with the `formulas` package.

The syntax validator (`validate_handmade_workbook.py`) is the hard gate: it
catches every shape of broken formula that produces an Excel repair log. This
tool goes one step further and actually recalculates the workbook in Python,
which finds formulas that are *syntactically* fine but return an error value.

Two things make that awkward with a workbook this size:

* the cross-sheet lookup names are dynamic (``OFFSET`` + ``COUNTIF``), which
  `formulas` cannot resolve - so they are flattened to static ranges in a
  throwaway copy first;
* a full recalculation of ~99k formulas takes a long time, so by default the
  tool refuses workbooks above :data:`BIG` formulas unless ``--force``.

If `formulas` is not installed the tool exits 0 with a note. It is a second
opinion, never the gate.

    python3 tools/recalc_check.py [file.xlsx] [--force] [--show N] [--keep]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT = ROOT / "output" / "Handmade Product Pricing & Profit Calculator.xlsx"

#: above this many formulas a recalculation needs --force
BIG = 25000

#: OFFSET(Sheet!$A$5,0,0,MAX(1,COUNTIF(Sheet!$A$5:$A$304,"?*")))
OFFSET_NAME = re.compile(r"^OFFSET\((.+?),\s*0\s*,\s*0\s*,", re.I)
COUNTIF_RANGE = re.compile(r"COUNTIF\(\s*('[^']+'|[A-Za-z0-9_ ]+)!(\$?[A-Z]{1,3}"
                           r"\$?\d+:\$?[A-Z]{1,3}\$?\d+)")
FORMULA_TAG = re.compile(r"<f[^>]*>([^<]*)</f>")


def formula_cells(path: Path) -> int:
    """Count stored formulas straight from the sheet XML (fast, no openpyxl)."""
    total = 0
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                total += len(FORMULA_TAG.findall(
                    z.read(name).decode("utf-8", "replace")))
    return total


def cell_text(value) -> str:
    """Short printable form of a calculated value."""
    try:
        text = value.value[0, 0] if hasattr(value, "value") else value
    except Exception:                                  # pragma: no cover
        text = value
    return str(text)


def flatten_dynamic_names(path: Path, target: Path) -> int:
    """Copy *path* to *target* with every OFFSET name made static."""
    changed = 0
    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}

    xml = data["xl/workbook.xml"].decode("utf-8")

    def replace(match: re.Match) -> str:
        nonlocal changed
        whole = match.group(0)
        name = match.group(1)
        value = match.group(2)
        if not OFFSET_NAME.match(value):
            return whole
        found = COUNTIF_RANGE.search(value)
        if not found:
            return whole
        sheet, rng = found.group(1), found.group(2)
        changed += 1
        return f'<definedName name="{name}">{sheet}!{rng}</definedName>'

    xml = re.sub(r'<definedName name="([^"]+)"([^>]*)>([^<]*)</definedName>',
                 lambda m: replace_named(m), xml)
    data["xl/workbook.xml"] = xml.encode("utf-8")

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, data[n])
    return changed


def replace_named(match: re.Match) -> str:
    """Rewrite one <definedName> element if it is dynamic."""
    name, attrs, value = match.group(1), match.group(2), match.group(3)
    if not OFFSET_NAME.match(value):
        return match.group(0)
    found = COUNTIF_RANGE.search(value)
    if not found:
        return match.group(0)
    sheet, rng = found.group(1), found.group(2)
    return f'<definedName name="{name}"{attrs}>{sheet}!{rng}</definedName>'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default=str(DEFAULT))
    parser.add_argument("--force", action="store_true",
                        help="recalculate even a very large workbook")
    parser.add_argument("--show", type=int, default=20,
                        help="how many error cells to print")
    parser.add_argument("--keep", action="store_true",
                        help="keep the flattened copy for inspection")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"recalc_check: not found: {path}")
        return 1

    try:
        import formulas                                 # type: ignore
    except ImportError:
        print("recalc_check: 'formulas' not installed - SKIPPED "
              "(validate_handmade_workbook.py is the hard gate)")
        return 0

    count = formula_cells(path)
    print(f"recalc_check: {path.name} - {count:,} formulas")
    if count > BIG and not args.force:
        print(f"recalc_check: more than {BIG:,} formulas - SKIPPED "
              f"(pass --force to recalculate anyway; it is slow)")
        return 0

    tmp = Path(tempfile.gettempdir()) / f"flat-{path.stem}.xlsx"
    n_flat = flatten_dynamic_names(path, tmp)
    print(f"recalc_check: flattened {n_flat} dynamic names -> {tmp}")

    try:
        model = formulas.ExcelModel().loads(str(tmp)).finish()
        solution = model.calculate()
    except Exception as exc:                             # pragma: no cover
        print(f"recalc_check: engine failed ({exc}) - SKIPPED")
        if not args.keep:
            tmp.unlink(missing_ok=True)
        return 0

    errors = []
    for key, value in solution.items():
        text = cell_text(value)
        if text.startswith("#") and text not in ("#EMPTY",):
            errors.append((key, text))

    if not args.keep:
        tmp.unlink(missing_ok=True)

    if errors:
        print(f"recalc_check: {len(errors)} error values")
        for key, text in errors[:args.show]:
            print(f"  {key}: {text}")
        return 1
    print("recalc_check: no error values - PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
