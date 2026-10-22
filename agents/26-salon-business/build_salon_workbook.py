#!/usr/bin/env python3
"""Build the Salon Business Management System workbook.

Examples:
    python3 build_salon_workbook.py
    python3 build_salon_workbook.py --blank -o out/blank.xlsx
    python3 build_salon_workbook.py --rows 1200 --today 2026-10-18
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from salon_business_spreadsheet.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
