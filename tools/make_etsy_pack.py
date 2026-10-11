"""Pack the Etsy product bundle into one downloadable zip.

    python tools/make_etsy_pack.py

Gathers the two workbooks (filled and blank), the Etsy listing images, the
listing copy, the README and the full source code document, and writes:

    download/pet-sitting-spreadsheet-etsy-pack.zip
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join("download", "pet-sitting-spreadsheet-etsy-pack.zip")

FILLED = os.path.join("output", "Pet Sitting Business Spreadsheet.xlsx")
BLANK = os.path.join(
    "output", "Pet Sitting Business Spreadsheet (Blank - No Example Data).xlsx")
#: 2000 x 2000 versions - Etsy asks for at least 2000 px on the
#: shortest side.  The 1024 px originals stay in etsy-images/.
IMAGES = "etsy-images-2000px"
DOCS = ["README.md", "SOURCE_CODE.md", "HOW_TO_USE.md", "ETSY_LISTING.md"]
SOURCE_TREES = ["pet_sitting_spreadsheet", "tools"]
BUILD_SCRIPT = "build_pet_sitting_workbook.py"

#: Same date for every entry, so the zip only changes when the content does.
STAMP = (2026, 1, 1, 0, 0, 0)


def gather() -> list:
    """`[(archive name, disk path)]` for everything that goes in the zip."""
    items = []

    def add(archive_name: str, path: str) -> None:
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            raise SystemExit(f"missing file: {path}")
        items.append((archive_name, full))

    for name in DOCS:
        add(name, name)
    add("Pet Sitting Business Spreadsheet.xlsx", FILLED)
    add("Pet Sitting Business Spreadsheet (Blank).xlsx", BLANK)
    add(BUILD_SCRIPT, BUILD_SCRIPT)

    folder = os.path.join(ROOT, IMAGES)
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            add(f"etsy-images/{name}", os.path.join(IMAGES, name))

    for tree in SOURCE_TREES:
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
    parser.add_argument("-o", "--output", default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    out = os.path.join(ROOT, args.output)
    folder = os.path.dirname(out)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    items = gather()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for archive_name, disk_path in items:
            info = zipfile.ZipInfo.from_file(disk_path, archive_name)
            info.date_time = STAMP
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(disk_path, "rb") as handle:
                zf.writestr(info, handle.read())

    size = os.path.getsize(out)
    print(f"{args.output}  ({len(items)} files, {size / 1024 / 1024:.1f} MB)")
    for archive_name, _ in items:
        print(f"    {archive_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
