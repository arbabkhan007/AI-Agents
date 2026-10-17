#!/usr/bin/env python3
"""
Build the Social Media Content Calendar & Analytics Planner.

Double click it, or run::

    python build_social_media_workbook.py

The finished .xlsx lands in the ``output`` folder next to this script.
Author of the generated workbook: Novality Store.

Options (all optional)::

    python build_social_media_workbook.py --blank        # no example data
    python build_social_media_workbook.py --currency "£" --currency-code GBP
    python build_social_media_workbook.py --year 2027
    python build_social_media_workbook.py -o "~/Desktop/Planner.xlsx"

See ``python build_social_media_workbook.py --help`` for the full list.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_media_spreadsheet.cli import main   # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
