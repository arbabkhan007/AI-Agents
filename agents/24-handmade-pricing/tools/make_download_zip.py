"""
make_download_zip.py - pack the deliverables.

    python3 tools/make_download_zip.py --product handmade

Writes two archives into `download/`:

    handmade-pricing-calculator-source.zip
        Every generator source file, the tools, README_HANDMADE.md and a
        HOW TO RUN note - what you need to rebuild the workbook with
        different rates, margins, currency or row counts.

    handmade-pricing-calculator.zip
        The two workbooks (filled example + blank) and a HOW TO RUN note -
        what a customer downloads.

The workbooks must exist first:

    python3 build_handmade_workbook.py
    python3 build_handmade_workbook.py --blank \
        -o "output/Handmade Product Pricing & Profit Calculator (Blank).xlsx"
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD = ROOT / "download"
OUTPUT = ROOT / "output"

PRODUCTS = {
    "handmade": {
        "folder": "handmade-pricing-calculator",
        "package": "handmade_pricing_spreadsheet",
        "source_zip": "handmade-pricing-calculator-source.zip",
        "product_zip": "handmade-pricing-calculator.zip",
        "filled": "Handmade Product Pricing & Profit Calculator.xlsx",
        "blank": "Handmade Product Pricing & Profit Calculator (Blank).xlsx",
        "readme": "README_HANDMADE.md",
    },
}

HOW_TO_RUN = """\
Handmade Product Pricing & Profit Calculator
============================================

Two workbooks are included:

  * Handmade Product Pricing & Profit Calculator.xlsx
      The full system, filled with a worked example for a real maker
      (Willow & Thread Handmade - candles, crochet, jewellery, clothing,
      woodworking and digital patterns). Every formula, drop-down,
      dashboard and report is live: replace the example with your own
      products and it all recalculates.

  * Handmade Product Pricing & Profit Calculator (Blank).xlsx
      The same workbook with every register empty and the example cleared
      out. Start here if you would rather not delete the example first.

How to use it
-------------
1. Open the workbook in Excel (2010 or newer), Google Sheets, LibreOffice
   Calc or Numbers.
2. Start on the 'Start Here' tab - it walks you through the first three
   steps and explains the pricing maths.
3. Set your shop, your hourly rate, your fees and your target margins on
   'Settings'. Everything else reads from there.
4. List your materials on 'Materials', then give each product its bill of
   materials on 'Material Usage'.
5. Add your products on 'Products' - or use one of the six craft tabs
   (Crochet, Jewelry, Candles, Clothing, Woodworking, Digital), which work
   the cost out from the parts that craft actually uses and fill Products
   for you.
6. Read the suggested price on 'Retail Calculator', check the trade price
   on 'Wholesale Calculator', and see how many you must sell on
   'Profit & Break-Even'.
7. Record sales on 'Sales'. The 'Dashboard' and 'Reports' tabs then tell
   you what the month and the year actually earned.
8. Print 'Print Costing', 'Print Quote' or 'Print Order' - each is laid
   out for one portrait page on your own letterhead.

The pricing maths
-----------------
    price = (cost of one item + fixed fees) / (1 - target margin - fee rate)

Cost of one item = materials + labour (minutes / 60 x your loaded hourly
rate) + packaging + any postage you absorb + your share of overhead.
Dividing rather than adding is what makes the marketplace fee pay for
itself, because the fee is charged on the selling price.

Protection
----------
Every sheet is protected with the password: premium
White cells are unlocked and are yours to type in. Pale cells are locked
formulas. To unprotect a sheet: Review > Unprotect Sheet > premium.

Compatibility
-------------
No macros, no dynamic arrays, no XLOOKUP, no LET - every formula works in
Excel 2010 and later, on Windows, Mac, the web, Google Sheets, LibreOffice
and Numbers.

Questions? Contact the shop you bought this from.
"""


def add_tree(z: zipfile.ZipFile, base: Path, prefix: str = "") -> int:
    """Add every file under *base* (skipping caches and generated output)."""
    count = 0
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.suffix in (".xlsx", ".zip") and "download" in path.parts:
            continue
        if path.name.startswith("SOURCE_CODE_"):
            continue
        arc = prefix + str(path.relative_to(base))
        z.write(path, arc)
        count += 1
    return count


def gather(product: dict) -> List[Tuple[Path, str]]:
    """The files that make up the source package."""
    files: List[Tuple[Path, str]] = []
    pkg = ROOT / product["package"]
    files.append((pkg, product["package"] + "/"))
    for script in sorted(ROOT.glob("*.py")):
        files.append((script, script.name))
    tools = ROOT / "tools"
    if tools.is_dir():
        for script in sorted(tools.glob("*.py")):
            files.append((script, "tools/" + script.name))
    readme = ROOT / product["readme"]
    if readme.exists():
        files.append((readme, product["readme"]))
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        files.append((gitignore, ".gitignore"))
    return files


def build_source_zip(product: dict) -> int:
    DOWNLOAD.mkdir(exist_ok=True)
    folder = product["folder"]
    target = DOWNLOAD / product["source_zip"]
    n = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path, arc in gather(product):
            if path.is_dir():
                n += add_tree(z, path, f"{folder}/{arc}")
            else:
                z.write(path, f"{folder}/{arc}")
                n += 1
        z.writestr(f"{folder}/HOW TO RUN.txt", HOW_TO_RUN)
        n += 1
    print(f"{target.name}: {n} files "
          f"({target.stat().st_size / 1024:.0f} KB)")
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
    folder = product["folder"]
    target = DOWNLOAD / product["product_zip"]
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(filled, f"{folder}/{filled.name}")
        z.write(blank, f"{folder}/{blank.name}")
        z.writestr(f"{folder}/HOW TO RUN.txt", HOW_TO_RUN)
    print(f"{target.name}: 3 files "
          f"({target.stat().st_size / 1024:.0f} KB)")
    return 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", default="handmade",
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
