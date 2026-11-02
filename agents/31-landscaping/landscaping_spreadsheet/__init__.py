"""Ultimate Landscaping & Lawn Care Business Manager.

A twenty-three tab Excel workbook for lawn care and landscaping
businesses: customers, properties, quoting, jobs, routes, recurring
contracts, crew, equipment, materials, invoicing and profit by job.

    from landscaping_spreadsheet import build_workbook
    build_workbook("Landscaping Manager.xlsx")
"""

from .build import build_workbook
from .config import PRODUCT_NAME, VERSION, Config

__all__ = ["build_workbook", "Config", "PRODUCT_NAME", "VERSION"]
