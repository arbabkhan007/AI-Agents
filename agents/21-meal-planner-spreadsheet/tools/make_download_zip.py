"""
make_download_zip.py - builds the customer download for this product.

Collects the workbook, the readme, the how-to guide and the source export
into `download/meal-planner-spreadsheet.zip`.

Usage:
    python tools/make_download_zip.py --product meal
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
DOWNLOAD = ROOT / "download"

PRODUCTS = {
    "meal": {
        "zip_name": "meal-planner-spreadsheet.zip",
        "workbook": "Meal Planner & Grocery List.xlsx",
        "docs": ["README_MEAL.md", "HOW_TO_USE_MEAL.md"],
        "source": "SOURCE_CODE_MEAL.md",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default="meal", choices=sorted(PRODUCTS))
    args = parser.parse_args()
    spec = PRODUCTS[args.product]

    workbook = OUT / spec["workbook"]
    if not workbook.exists():
        print(f"FAIL: workbook not found: {workbook}")
        print("      run build_meal_planner_workbook.py first")
        return 1

    DOWNLOAD.mkdir(exist_ok=True)
    zip_path = DOWNLOAD / spec["zip_name"]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(workbook, spec["workbook"])
        print(f"  + {spec['workbook']}")
        for rel in spec["docs"]:
            path = ROOT / rel
            if path.exists():
                zf.write(path, rel)
                print(f"  + {rel}")
            else:
                print(f"  skip (missing): {rel}")
        source = ROOT / spec["source"]
        if source.exists():
            zf.write(source, spec["source"])
            print(f"  + {spec['source']}")
        else:
            print(f"  skip (missing): {spec['source']}")

    size = zip_path.stat().st_size
    print(f"\nWrote {zip_path} ({size / 1024 / 1024:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
