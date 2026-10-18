"""
make_download_zip.py - pack the deliverables.

    python tools/make_download_zip.py --product cleaning

Writes:
    download/cleaning-business-crm-source.zip
        Every generator source file, the tools, README_CLEANING.md and a
        HOW TO RUN note - what you need to rebuild the workbook with
        different settings.

    download/cleaning-business-crm.zip
        The two workbooks (filled sample + blank) and a HOW TO RUN note -
        what a customer downloads.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD = ROOT / "download"
OUTPUT = ROOT / "output"

PRODUCTS = {
    "cleaning": {
        "folder": "cleaning-business-crm",
        "package": "cleaning_business_spreadsheet",
        "source_zip": "cleaning-business-crm-source.zip",
        "product_zip": "cleaning-business-crm.zip",
        "filled": "Cleaning Business CRM & Pricing Calculator.xlsx",
        "blank": "Cleaning Business CRM & Pricing Calculator (Blank).xlsx",
        "readme": "README_CLEANING.md",
    },
}

HOW_TO_RUN = """\
Cleaning Business CRM & Pricing Calculator
==========================================

Two workbooks are included:

  * Cleaning Business CRM & Pricing Calculator.xlsx
      The full system, filled with a worked example for a real cleaning
      company (Bright & Tidy Cleaning Co.). Every formula, drop-down and
      dashboard is live - replace the example with your own business.

  * Cleaning Business CRM & Pricing Calculator (Blank).xlsx
      The same workbook with every register empty. Start here if you
      would rather not delete the example first.

How to use it
-------------
1. Open the workbook in Excel (2010 or newer), Google Sheets or Numbers.
2. Start on the 'Start Here' tab.
3. Set your business, rates and tax on the 'Settings' tab.
4. Build your price list on 'Services'.
5. Add clients and properties, then quote on 'Quote Calculator'.
6. Schedule on 'Jobs', bill on 'Invoices', get paid on 'Payments'.
7. Watch the numbers on 'Dashboard' and 'Reports'.

Protection
----------
Every sheet is protected with the password: premium
White cells are unlocked and are yours to type in. Pale teal cells are
locked formulas. To unprotect a sheet: Review > Unprotect Sheet > premium.

Questions? Contact the shop you bought this from.
"""


def add_tree(z: zipfile.ZipFile, base: Path, prefix: str = "") -> int:
    count = 0
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.suffix in (".xlsx", ".zip") and "download" in path.parts:
            continue
        if path.name == "SOURCE_CODE_CLEANING.md":
            continue
        arc = prefix + str(path.relative_to(base))
        z.write(path, arc)
        count += 1
    return count


def gather(product: dict) -> list:
    """The files that make up the source package."""
    files = []
    pkg = ROOT / product["package"]
    files.append((pkg, product["package"] + "/"))
    for script in sorted(ROOT.glob("*.py")):
        files.append((script, script.name))
    tools = ROOT / "tools"
    for script in sorted(tools.glob("*.py")):
        files.append((script, "tools/" + script.name))
    readme = ROOT / product["readme"]
    if readme.exists():
        files.append((readme, product["readme"]))
    return files


def build_source_zip(product: dict) -> int:
    DOWNLOAD.mkdir(exist_ok=True)
    target = DOWNLOAD / product["source_zip"]
    n = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path, arc in gather(product):
            if path.is_dir():
                n += add_tree(z, path, arc)
            else:
                z.write(path, arc)
                n += 1
        z.writestr("HOW TO RUN.txt", HOW_TO_RUN)
        n += 1
    print(f"{target.name}: {n} files")
    return n


def build_product_zip(product: dict) -> int:
    filled = OUTPUT / product["filled"]
    blank = OUTPUT / product["blank"]
    missing = [p for p in (filled, blank) if not p.exists()]
    if missing:
        print("FAIL: build the workbooks first. Missing:")
        for path in missing:
            print(f"  {path}")
        return 0
    DOWNLOAD.mkdir(exist_ok=True)
    target = DOWNLOAD / product["product_zip"]
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(filled, filled.name)
        z.write(blank, blank.name)
        z.writestr("HOW TO RUN.txt", HOW_TO_RUN)
    print(f"{target.name}: 3 files "
          f"({target.stat().st_size / 1024:.0f} KB)")
    return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default="cleaning",
                        choices=sorted(PRODUCTS))
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--product-only", action="store_true")
    args = parser.parse_args()

    product = PRODUCTS[args.product]
    total = 0
    if not args.product_only:
        total += build_source_zip(product)
    if not args.source_only:
        total += build_product_zip(product)
    return 0 if total else 1


if __name__ == "__main__":
    raise SystemExit(main())
