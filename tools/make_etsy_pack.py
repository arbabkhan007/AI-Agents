#!/usr/bin/env python3
"""
Pack a product for the buyer: the workbooks, the docs and the photos.

    python tools/make_etsy_pack.py                 # pet sitting
    python tools/make_etsy_pack.py --product meal  # meal planner

Writes

    download/pet-sitting-spreadsheet-etsy-pack.zip
    download/meal-planner-grocery-list-etsy-pack.zip

The photos come from `etsy-images-2000px/` because Etsy wants 2000 px; the
1024 px originals are the ones in `etsy-images/`. Timestamps are fixed so
the zip only changes when something in it changes.
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Same date for every entry, so the zip only changes when the content does.
STAMP = (2026, 1, 1, 0, 0, 0)

IMAGES = "etsy-images"
IMAGES_2000 = "etsy-images-2000px"
OUTPUT = "output"

PRODUCTS = {
    "pet": {
        "output": os.path.join("download",
                               "pet-sitting-spreadsheet-etsy-pack.zip"),
        "prefix": "",
        "workbooks": [
            ("output/Pet Sitting Business Spreadsheet.xlsx",
             "Pet Sitting Business Spreadsheet.xlsx"),
            ("output/Pet Sitting Business Spreadsheet "
             "(Blank - No Example Data).xlsx",
             "Pet Sitting Business Spreadsheet (Blank).xlsx"),
        ],
        "docs": [("HOW_TO_USE.md", "HOW_TO_USE.md"),
                 ("README.md", "README.md"),
                 ("SOURCE_CODE.md", "SOURCE_CODE.md")],
        "trees": ["pet_sitting_spreadsheet", "tools"],
    },
    "meal": {
        "output": os.path.join("download",
                               "meal-planner-grocery-list-etsy-pack.zip"),
        "prefix": "meal-",
        "workbooks": [
            ("output/Meal Planner & Grocery List.xlsx",
             "Meal Planner & Grocery List.xlsx"),
            ("output/Meal Planner & Grocery List "
             "(Blank - No Example Data).xlsx",
             "Meal Planner & Grocery List (Blank).xlsx"),
        ],
        "docs": [("HOW_TO_USE_MEAL.md", "HOW_TO_USE_MEAL.md"),
                 ("README_MEAL.md", "README_MEAL.md"),
                 ("SOURCE_CODE_MEAL.md", "SOURCE_CODE_MEAL.md")],
        "trees": ["meal_planner_spreadsheet", "tools"],
    },
}


def gather(product: dict) -> list:
    """`[(archive name, disk path)]` for everything that goes in the zip."""
    items = []

    def add(archive_name: str, path: str) -> None:
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            raise SystemExit(f"missing file: {path}")
        items.append((archive_name, full))

    for path, name in product["workbooks"]:
        add(name, path)
    for path, name in product["docs"]:
        add(name, path)

    folder = os.path.join(ROOT, IMAGES_2000)
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if not name.startswith(product["prefix"]):
                continue
            if name.lower().endswith((".jpg", ".jpeg", ".png")):
                add(f"{IMAGES}/{name}", os.path.join(IMAGES_2000, name))

    for tree in product["trees"]:
        base = os.path.join(ROOT, tree)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                add(f"source-code/{rel.replace(os.sep, '/')}", rel)
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

    size = os.path.getsize(out)
    print(f"{os.path.relpath(out, ROOT)}  ({len(items)} files, "
          f"{size / 1024 / 1024:.1f} MB)")
    for archive_name, _ in items:
        print(f"    {archive_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
