#!/usr/bin/env python3
"""Build the Wedding Photographer Business Manager workbook.

    python3 build_wedding_workbook.py
    python3 build_wedding_workbook.py -o "out/Wedding.xlsx" --blank
    python3 build_wedding_workbook.py --rows 60 --today 2026-11-01

A thin wrapper around ``python -m wedding_photography_spreadsheet`` so
the product can be built without worrying about the import path.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wedding_photography_spreadsheet.cli import main   # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
