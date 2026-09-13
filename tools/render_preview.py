#!/usr/bin/env python3
"""
tools/render_preview.py - turn the workbooks into PNG previews.

Requires LibreOffice (soffice) to convert to PDF, then pdftoppm/poppler
for the pages.  When those tools are not installed the script says so
and exits cleanly - it is a convenience for listing screenshots, never a
build step.

Usage:
    python3 tools/render_preview.py [file.xlsx ...]   # default: products/
"""

import glob
import os
import shutil
import subprocess
import sys


def main(argv):
    paths = argv or sorted(glob.glob("products/Catering_Business_Manager_"
                                     "*.xlsx"))
    if not paths:
        print("no workbooks found")
        return 1
    if shutil.which("soffice") is None and \
            shutil.which("libreoffice") is None:
        print("LibreOffice is not installed in this environment, so "
              "spreadsheet->PNG previews")
        print("cannot be rendered here.  The workbooks themselves are "
              "unaffected - open")
        print("them in Excel or upload to Google Sheets to see them "
              "live.")
        return 0

    outdir = "previews"
    os.makedirs(outdir, exist_ok=True)
    for path in paths:
        base = os.path.splitext(os.path.basename(path))[0]
        print("rendering %s ..." % base)
        subprocess.check_call(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", outdir, path])
        pdf = os.path.join(outdir, base + ".pdf")
        if os.path.exists(pdf) and shutil.which("pdftoppm"):
            subprocess.check_call(
                ["pdftoppm", "-png", "-r", "110", pdf,
                 os.path.join(outdir, base)])
    print("\nwrote previews to %s/" % outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
