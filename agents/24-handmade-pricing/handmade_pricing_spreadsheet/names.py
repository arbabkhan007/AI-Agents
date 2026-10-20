"""Workbook level defined names that point at the register sheets.

The drop down lists on the `Lists` tab define their own names. These are
the ones that have to follow live data - product IDs, material names, the
shops you wholesale to - so they are built from the registry once every
register exists. Each one is an ``OFFSET`` range that grows and shrinks
with the number of filled rows, which is why a new material appears in
the bill of materials drop down the moment you type it.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    # the spine of the whole workbook
    "ProductIDs": ("Products", "id"),
    "ProductNames": ("Products", "name"),
    "ProductSKUs": ("Products", "sku"),
    "MaterialIDs": ("Materials", "id"),
    "MaterialNames": ("Materials", "name"),
    "ChannelNames": ("Channels", "name"),
    "ShipOptions": ("Shipping", "label"),
    "PackComponents": ("Packaging", "name"),
    "BundleIDs": ("Bundles", "id"),
    "BatchIDs": ("Batches", "id"),
    "PromoCodes": ("Promotions", "code"),
    "EventNames": ("Events", "name"),
    "CustomerIDs": ("Wholesale Customers", "id"),
    "CustomerNames": ("Wholesale Customers", "name"),
    "OrderIDs": ("Wholesale Orders", "id"),
    # columns the dashboard and the reports scan
    "ProductCategories": ("Products", "category"),
    "ProductMargins": ("Products", "margin"),
    "SaleDates": ("Sales", "date"),
    "SaleMonths": ("Sales", "month"),
    "SaleProducts": ("Sales", "product"),
    "SaleChannels": ("Sales", "channel"),
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
