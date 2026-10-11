"""Workbook level defined names that point at the register sheets.

The drop down lists on the `Lists` tab define their own names; these are the
ones that have to follow live data (client names, pet references, invoice
numbers, ...), so they are built from the registry once every register has
been created.  Each one is an ``OFFSET`` range that grows and shrinks with
the number of filled rows.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    "ClientNames": ("Clients", "name"),
    "ClientIDs": ("Clients", "id"),
    "PetLabels": ("Pets", "label"),
    "PetNames": ("Pets", "name"),
    "ServiceNames": ("Services", "name"),
    "StaffNames": ("Staff", "name"),
    "BookingIDs": ("Bookings", "id"),
    "InvoiceNos": ("Invoices", "invoice_no"),
    "VisitIDs": ("Visit Log", "id"),
    "IncidentIDs": ("Incidents", "id"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            continue
        spec = reg[sheet]
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
