"""Handmade Product Pricing & Profit Calculator.

Build the workbook with::

    python -m handmade_pricing_spreadsheet -o "output/Pricing.xlsx"

or from Python::

    from handmade_pricing_spreadsheet import build_workbook
    build_workbook("Handmade Pricing Calculator.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, PRODUCT_VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "PRODUCT_LISTING_TITLE", "PRODUCT_VERSION"]
__version__ = PRODUCT_VERSION
