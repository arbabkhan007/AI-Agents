#!/usr/bin/env python3
"""Build the Handmade Product Pricing & Profit Calculator workbook.

    python3 build_handmade_workbook.py
    python3 build_handmade_workbook.py -o "output/My Pricing.xlsx" --blank
    python3 build_handmade_workbook.py --currency "£" --rate 22 --margin 60

Run `--help` for every option. The generator itself lives in the
`handmade_pricing_spreadsheet` package next to this file.
"""

import sys

from handmade_pricing_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
