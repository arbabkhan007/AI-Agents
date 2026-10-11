"""
Pet Sitting & Dog Walking Business Spreadsheet
==============================================

Generates a ready-to-sell Excel workbook for pet sitters and dog walkers:
clients, pets, bookings, visit logs, health records, invoices, payments,
expenses, mileage, staff, inventory, a dashboard, reports, a budget, a
reminder centre and printable forms.

    python -m pet_sitting_spreadsheet --output "My Workbook.xlsx"

or from Python::

    from pet_sitting_spreadsheet import build_workbook, Config
    build_workbook("workbook.xlsx", Config(include_sample_data=False))

Every formula cell is locked and every sheet is protected with the password
in :class:`~pet_sitting_spreadsheet.config.Config` (default ``premium``), so
the maths cannot be edited by accident while the input cells stay open.
"""

from .build import build_workbook
from .config import AUTHOR, FORMULA_PASSWORD, Config

__all__ = ["build_workbook", "Config", "AUTHOR", "FORMULA_PASSWORD",
           "__version__"]

__version__ = "1.0.0"
__author__ = AUTHOR
