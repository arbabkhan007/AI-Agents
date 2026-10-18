"""Defined names.

Only a handful of names are needed - the printable sheets look up which
record to print, and the scheduler views need a short list of clients /
employees to pick from.  Each name is OFFSET based so it grows with the
data, exactly like the previous workbooks in this series.
"""

from __future__ import annotations

from typing import Any

from .layout import Registry, dynamic_name, quote_sheet

# name -> (sheet, column key, count_text?)
DYNAMIC_NAMES = {
    "Clients_Names": ("Clients", "name", True),
    "Employees_Names": ("Employees", "name", True),
    "Quotes_Numbers": ("Quotes", "quote_number", True),
    "Invoices_Numbers": ("Invoices", "invoice_number", True),
    "Jobs_Numbers": ("Jobs", "job_number", True),
    "Properties_Names": ("Properties", "property_name", True),
    "Services_Names": ("Services", "name", True),
    "Supplies_Names": ("Supplies", "name", True),
    "Print_Job_Numbers": ("Jobs", "job_number", True),
}


def apply_defined_names(workbook: Any, reg: Registry, cfg: Any) -> None:
    """Create the named ranges the printable sheets and pickers use."""
    for name, (sheet, key, count_text) in DYNAMIC_NAMES.items():
        spec = reg[sheet]
        workbook.define_name(
            name,
            dynamic_name(sheet, spec.letter(key),
                         spec.first_data_row, spec.last_data_row,
                         count_text=count_text))

    # Business identity used by the printable documents.
    settings = quote_sheet("Settings")
    workbook.define_name("Business_Name", f"{settings}!$C$6")
    workbook.define_name("Business_Phone", f"{settings}!$C$9")
    workbook.define_name("Business_Email", f"{settings}!$C$8")
    workbook.define_name("Business_Address", f"{settings}!$C$10")
    workbook.define_name("Invoice_Terms", f"{settings}!$C$46")

    # Pricing knobs referenced by the quote calculator.
    workbook.define_name("Hourly_Rate", f"{settings}!$C$55")
    workbook.define_name("Minimum_Charge", f"{settings}!$C$57")
    workbook.define_name("Tax_Rate", f"{settings}!$C$45")
