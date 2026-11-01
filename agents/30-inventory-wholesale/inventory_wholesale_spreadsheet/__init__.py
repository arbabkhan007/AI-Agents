"""Ultimate Inventory & Wholesale Order Manager.

Build the workbook with::

    python -m inventory_wholesale_spreadsheet -o "output/Inventory.xlsx"

or from Python::

    from inventory_wholesale_spreadsheet import build_workbook
    build_workbook("Ultimate Inventory & Wholesale Order Manager.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "LISTING_TITLE", "VERSION"]
__version__ = VERSION
