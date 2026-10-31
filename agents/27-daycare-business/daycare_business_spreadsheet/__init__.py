"""Daycare & Childcare Business Management Spreadsheet.

Build the workbook with::

    python -m daycare_business_spreadsheet -o "output/Daycare.xlsx"

or from Python::

    from daycare_business_spreadsheet import build_workbook
    build_workbook("Daycare Business Management Spreadsheet.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, PRODUCT_VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "PRODUCT_LISTING_TITLE", "PRODUCT_VERSION"]
__version__ = PRODUCT_VERSION
