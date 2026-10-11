"""Automated Meal Planner & Grocery List Spreadsheet.

Build the workbook with::

    python -m meal_planner_spreadsheet -o "output/Meal Planner.xlsx"

or from Python::

    from meal_planner_spreadsheet import build_workbook
    build_workbook("Meal Planner.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, PRODUCT_VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "PRODUCT_LISTING_TITLE", "PRODUCT_VERSION"]
__version__ = PRODUCT_VERSION
