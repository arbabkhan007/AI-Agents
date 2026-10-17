"""
make_download_zip.py - pack the deliverables.

    python tools/make_download_zip.py --product social

Writes:
    download/social-media-content-planner-source.zip
        Every generator source file, the tools and a README - what you
        need to rebuild the workbook with different settings.

    download/social-media-content-planner.zip
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

FILLED = OUTPUT / "Social Media Content Planner.xlsx"
BLANK = OUTPUT / "Social Media Content Planner (Blank).xlsx"

SOURCE_ZIP = DOWNLOAD / "social-media-content-planner-source.zip"
PRODUCT_ZIP = DOWNLOAD / "social-media-content-planner.zip"

HOW_TO_RUN = """\
Social Media Content Calendar & Analytics Planner
=================================================

Two workbooks are included:

  * Social Media Content Planner.xlsx
      The full planner, filled with a worked example for a small
      handmade brand (Wildflower Studio). Every formula, drop down and
      dashboard is live - replace the example with your own content.

  * Social Media Content Planner (Blank).xlsx
      The same workbook with every register empty. Start here if you
      would rather not delete the example first.

How to use it
-------------
1. Open the workbook in Excel (2010 or newer), Google Sheets or Numbers.
2. Start on the 'Start Here' tab.
3. Set your brand on the 'Settings' tab.
4. Fill 'Accounts', 'Content Pillars' and 'Audience Personas'.
5. Plan on the 'Content Calendar' - everything else counts itself.

Protection
----------
Every sheet is protected with the password: premium
Cream cells are unlocked and are yours to type in. Grey cells are locked
formulas. To unprotect a sheet: Review > Unprotect Sheet > premium.

Questions? Contact the shop you bought this from.
"""


def add_tree(z: zipfile.ZipFile, base: Path, prefix: str = "") -> int:
    count = 0
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.suffix in (".xlsx", ".zip", ".md") and "download" in path.parts:
            continue
        arc = prefix + str(path.relative_to(base))
        z.write(path, arc)
        count += 1
    return count


def build_source_zip() -> int:
    DOWNLOAD.mkdir(exist_ok=True)
    with zipfile.ZipFile(SOURCE_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        n = 0
        n += add_tree(z, ROOT / "social_media_spreadsheet",
                      "social_media_spreadsheet/")
        for script in sorted(ROOT.glob("*.py")):
            z.write(script, script.name)
            n += 1
        tools = ROOT / "tools"
        for script in sorted(tools.glob("*.py")):
            z.write(script, "tools/" + script.name)
            n += 1
        z.writestr("HOW TO RUN.txt", HOW_TO_RUN)
        n += 1
    print(f"{SOURCE_ZIP.name}: {n} files")
    return n


def build_product_zip() -> int:
    missing = [p for p in (FILLED, BLANK) if not p.exists()]
    if missing:
        print("FAIL: build the workbooks first. Missing:")
        for path in missing:
            print(f"  {path}")
        return 0
    DOWNLOAD.mkdir(exist_ok=True)
    with zipfile.ZipFile(PRODUCT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(FILLED, FILLED.name)
        z.write(BLANK, BLANK.name)
        z.writestr("HOW TO RUN.txt", HOW_TO_RUN)
    print(f"{PRODUCT_ZIP.name}: 3 files "
          f"({PRODUCT_ZIP.stat().st_size / 1024:.0f} KB)")
    return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default="social")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--product-only", action="store_true")
    args = parser.parse_args()

    total = 0
    if not args.product_only:
        total += build_source_zip()
    if not args.source_only:
        total += build_product_zip()
    if total == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
