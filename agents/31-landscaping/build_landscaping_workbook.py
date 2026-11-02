#!/usr/bin/env python3
"""Build the Ultimate Landscaping & Lawn Care Business Manager.

    python3 build_landscaping_workbook.py
    python3 build_landscaping_workbook.py --blank -o blank.xlsx
"""

import sys

from landscaping_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
