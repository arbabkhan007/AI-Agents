"""Fitness & Weight Loss Tracker.

Build the workbook with::

    python -m fitness_tracker_spreadsheet -o "output/Tracker.xlsx"

or from Python::

    from fitness_tracker_spreadsheet import build_workbook
    build_workbook("Fitness Tracker.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, PRODUCT_VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "PRODUCT_LISTING_TITLE", "PRODUCT_VERSION"]
__version__ = PRODUCT_VERSION
