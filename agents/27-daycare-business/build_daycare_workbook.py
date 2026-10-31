#!/usr/bin/env python3
"""Build the Daycare & Childcare Business Management Spreadsheet.

    python3 build_daycare_workbook.py
    python3 build_daycare_workbook.py -o "output/My Nursery.xlsx" --blank
    python3 build_daycare_workbook.py --currency "£" --tax 20 --rows 800

Run `--help` for every option. The generator itself lives in the
`daycare_business_spreadsheet` package next to this file.
"""

import sys

from daycare_business_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
