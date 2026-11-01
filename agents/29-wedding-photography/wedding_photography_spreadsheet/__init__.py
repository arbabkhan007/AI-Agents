"""Wedding Photographer Business Manager.

Build the workbook with::

    python -m wedding_photography_spreadsheet -o "output/Wedding.xlsx"

or from Python::

    from wedding_photography_spreadsheet import build_workbook
    build_workbook("Wedding Photographer Business Manager.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "LISTING_TITLE", "VERSION"]
__version__ = VERSION
