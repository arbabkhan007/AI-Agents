#!/usr/bin/env python3
"""
Pack a generator into a single zip people can download and run.

    python tools/make_download_zip.py                    # pet sitting
    python tools/make_download_zip.py --product meal     # meal planner

Writes one of

    download/pet-sitting-spreadsheet-source.zip
    download/meal-planner-grocery-list-source.zip

containing the generator, the quality tools, the documentation and a
`requirements.txt`, all under one folder so it unpacks tidily.

Timestamps are fixed so rebuilding the zip without changing any source
produces exactly the same bytes.
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Same date for every entry, so the zip only changes when the code does.
STAMP = (2026, 1, 1, 0, 0, 0)

REQUIREMENTS = """\
# The generator needs one package.
XlsxWriter>=3.0

# Only for the optional checks in tools/
# openpyxl>=3.1     validate_*.py, check_*.py
# formulas>=1.3     recalc_check.py
"""

PRODUCTS = {
    "pet": {
        "folder": "pet-sitting-spreadsheet",
        "output": os.path.join("download",
                               "pet-sitting-spreadsheet-source.zip"),
        "files": ["build_pet_sitting_workbook.py", "README.md",
                  "SOURCE_CODE.md"],
        "trees": ["pet_sitting_spreadsheet", "tools"],
        "how_to_run": """\
Pet Sitting & Dog Walking Business Spreadsheet
==============================================

    pip install XlsxWriter
    python build_pet_sitting_workbook.py

The workbook appears in:

    output/Pet Sitting Business Spreadsheet.xlsx

Useful options
--------------
    --blank                 empty workbook, no example data
    --business "My Name"    your business name on the cover and invoices
    --currency EUR-symbol   e.g. --currency "\\u20ac" --currency-code EUR
    --unit miles            mileage in miles instead of km
    --password secret       change the sheet protection password
    --author "Your Name"    change the document author
    --rows 1000             more rows of capacity in the big registers

Every formula cell is locked and every sheet is protected with the
password `premium` so the maths cannot be typed over by accident; the
cream coloured cells are the ones meant for typing in.

README.md explains how it is built, what is on each of the 27 tabs and
how to change things.  SOURCE_CODE.md is the whole program in one
readable document.
""",
    },
    "meal": {
        "folder": "meal-planner-grocery-list",
        "output": os.path.join("download",
                               "meal-planner-grocery-list-source.zip"),
        "files": ["build_meal_planner_workbook.py", "README_MEAL.md",
                  "HOW_TO_USE_MEAL.md", "SOURCE_CODE_MEAL.md"],
        "trees": ["meal_planner_spreadsheet", "tools"],
        "how_to_run": """\
Automated Meal Planner & Grocery List Spreadsheet
================================================

    pip install XlsxWriter
    python build_meal_planner_workbook.py

The workbook appears in:

    output/Meal Planner & Grocery List.xlsx

Useful options
--------------
    --blank                 empty workbook, no example data
    --household "My Name"   household name on the Settings tab
    --cook "My Name"        main cook's name
    --currency "GBP-symbol" e.g. --currency "\\u00a3" --currency-code GBP
    --units Imperial        ounces and fluid ounces instead of g and ml
    --week-start Sunday     start the week on a Sunday
    --year 2027             planning year
    --budget 150            weekly grocery budget
    --servings 2            default servings per meal
    --password secret       change the sheet protection password
    --author "Your Name"    change the document author
    --rows 300              more rows of capacity in the big registers

Every formula cell is locked and every sheet is protected with the
password `premium` so the maths cannot be typed over by accident; the
cream coloured cells are the ones meant for typing in.

HOW_TO_USE_MEAL.md is the walkthrough: set up, plan a week, shop, cook.
README_MEAL.md explains how the workbook is built and what is on each of
the 36 tabs.  SOURCE_CODE_MEAL.md is the whole program in one readable
document.
""",
    },
}


def gather(product: dict) -> list:
    """`[(archive name, disk path)]` for everything that goes in the zip."""
    items = []
    folder = product["folder"]

    def add(archive_name: str, path: str) -> None:
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            raise SystemExit(f"missing file: {path}")
        items.append((archive_name, full))

    for name in product["files"]:
        add(f"{folder}/{name}", name)

    for tree in product["trees"]:
        base = os.path.join(ROOT, tree)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                add(f"{folder}/{rel.replace(os.sep, '/')}", rel)
    return items


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", choices=sorted(PRODUCTS), default="pet")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args(argv)

    product = PRODUCTS[args.product]
    out = os.path.join(ROOT, args.output or product["output"])
    folder = os.path.dirname(out)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    items = gather(product)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for archive_name, disk_path in items:
            info = zipfile.ZipInfo.from_file(disk_path, archive_name)
            info.date_time = STAMP
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(disk_path, "rb") as handle:
                zf.writestr(info, handle.read())

        for name, text in (("requirements.txt", REQUIREMENTS),
                           ("HOW-TO-RUN.txt", product["how_to_run"])):
            info = zipfile.ZipInfo(f"{product['folder']}/{name}", STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, text)

    size = os.path.getsize(out)
    print(f"{os.path.relpath(out, ROOT)}  ({len(items) + 2} files, "
          f"{size / 1024 / 1024:.1f} MB)")
    for archive_name, _ in items:
        print(f"    {archive_name}")
    print(f"    {product['folder']}/requirements.txt")
    print(f"    {product['folder']}/HOW-TO-RUN.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
