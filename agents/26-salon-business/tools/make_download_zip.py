"""
make_download_zip.py - pack the salon deliverables.

    python3 tools/make_download_zip.py --product salon

Writes two archives into `download/`:

    salon-business-system-source.zip
        Every generator source file, the tools, README_HANDMADE.md and a
        HOW TO RUN note - what you need to rebuild the workbook with
        different rates, margins, currency or row counts.

    salon-business-system.zip
        The two workbooks (filled example + blank) and a HOW TO RUN note -
        what a customer downloads.

The workbooks must exist first:

    python3 build_salon_workbook.py
    python3 build_salon_workbook.py --blank \
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
    "salon": {
        "folder": "salon-business-management-system",
        "package": "salon_business_spreadsheet",
        "source_zip": "salon-business-system-source.zip",
        "product_zip": "salon-business-system.zip",
        "filled": "Salon Business Management System.xlsx",
        "blank": "Salon Business Management System (Blank).xlsx",
        "readme": "README_SALON.md",
        "how_to_run": "HOW_TO_RUN_SALON",
    },
}

HOW_TO_RUN_SALON = """\
Salon Business Management System
================================

Two workbooks are included:

  * Salon Business Management System.xlsx
      The full 20-tab system filled with eleven months of a realistic
      example salon (Bloom & Blade Studio). Every KPI, commission
      statement, P&L line and report is live.
  * Salon Business Management System (Blank).xlsx
      The same workbook with empty registers - start here to run your
      own salon from day one.

How to use it
-------------
1. Open in Excel 2010 or newer, Google Sheets, LibreOffice or Numbers.
2. Tab 20 Settings & Lists: salon name, tax rate, payment fees,
   commission rates per category, loyalty rules, and every drop-down
   list.
3. Tab 8 Staff Management: one row per person with their commission
   method (Percentage, Category or Flat).
4. Tab 5 Services & Pricing: your menu with durations, prices and
   direct costs. Tab 13: retail and backbar stock.
5. Tab 4 Client CRM: your clients, consents and preferences.
6. Daily: tab 3 bookings, tab 6 sales, tab 7 payments and deposits,
   tab 10 payroll, tab 11 expenses.
7. Read tab 2 every morning; tab 9 for commission statements; tab 12
   for the monthly P&L; tab 19 for the owner review; tab 15 for
   campaigns, gift certificates and packages.

Money rules this workbook follows
---------------------------------
  * Net sales = gross - discounts - refunds + tax.
  * A deposit is not revenue until the visit completes and the sale is
    invoiced; unearned deposits are reported separately.
  * Commission = eligible service revenue x the applicable rate (own
    rate, category rate or flat per service) + retail at the retail
    rate, plus typed adjustments.
  * Inventory on hand = opening + received - used - sold - wasted +
    adjustments; received reads the purchase register.
  * Break-even treats rent, utilities, insurance, software and payroll
    as fixed and everything else as variable.

Protection
----------
Every sheet is protected with the password: premium
White cells are unlocked and yours to type in. Pale cells are locked
formulas. Review > Unprotect Sheet > premium to customise.

Compatibility & limits
----------------------
No macros, no XLOOKUP, IFS, LET or dynamic arrays - Excel 2010 and
newer, plus Google Sheets, LibreOffice and Numbers. The workbook
organises bookings and money; it does not send confirmations or
reminders, sync with booking platforms, or give accounting, payroll or
tax advice.

Questions? Contact the shop you bought this from.
"""

RUN_TEXT = {"HOW_TO_RUN_SALON": HOW_TO_RUN_SALON}


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
        z.writestr(f"{folder}/HOW TO RUN.txt",
                   RUN_TEXT[product["how_to_run"]])
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
        z.writestr(f"{folder}/HOW TO RUN.txt",
                   RUN_TEXT[product["how_to_run"]])
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
