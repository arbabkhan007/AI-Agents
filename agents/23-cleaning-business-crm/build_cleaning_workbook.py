#!/usr/bin/env python3
"""Build the Cleaning Business CRM & Pricing Calculator workbook.

    python3 build_cleaning_workbook.py
    python3 build_cleaning_workbook.py -o "output/My Cleaning CRM.xlsx" --blank
    python3 build_cleaning_workbook.py --currency "£" --rate 38 --tax 20

Run `--help` for every option. The generator itself lives in the
`cleaning_business_spreadsheet` package next to this file.
"""

import sys

from cleaning_business_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
