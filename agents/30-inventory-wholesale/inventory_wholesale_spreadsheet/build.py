"""Workbook builder: puts the twenty-three tabs together in order.

Typical use::

    from inventory_wholesale_spreadsheet import build_workbook
    build_workbook("Ultimate Inventory & Wholesale Order Manager.xlsx")
"""

from __future__ import annotations

import datetime as _dt
import inspect
import os
from typing import Callable, Dict, List, Optional

from xlsxwriter.workbook import Workbook

from .config import VERSION, Config
from .formats import FormatBook
from .layout import Registry, SheetSpec
from .names import define_cross_sheet_names
from .sheets import (annual, audit, customers, dashboard, expenses,
                     getting_started, inventory, locations, monthly,
                     movements, orders, performance, pricing,
                     printables, products, profit, purchases, reorder,
                     retail, returns, settings, suppliers, valuation)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [
    products, inventory, movements, suppliers, purchases, customers,
    pricing, orders, retail, reorder, valuation, returns, locations,
    audit, performance, expenses, profit,
]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = [
    "Dashboard",
    "Getting Started",
    "Settings & Lists",
    "Product & SKU Database",
    "Inventory Tracker",
    "Stock Movement Log",
    "Supplier Database",
    "Purchase Orders",
    "Wholesale Customer CRM",
    "Wholesale Pricing",
    "Wholesale Orders",
    "Retail Sales Tracker",
    "Reorder Planner",
    "Inventory Valuation & COGS",
    "Returns & Damaged Goods",
    "Warehouse Locations",
    "Stock Audit",
    "Product Performance",
    "Expense Tracker",
    "Profit Analysis",
    "Monthly Reports",
    "Annual Reports",
    "Printable Orders & Invoices",
]

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "Dashboard": dashboard.build,
    "Getting Started": getting_started.build,
    "Settings & Lists": settings.build,
    "Monthly Reports": monthly.build,
    "Annual Reports": annual.build,
    "Printable Orders & Invoices": printables.build,
}

#: register modules by sheet name
REGISTER_BY_NAME = {module.NAME: module for module in REGISTER_MODULES}


# ---------------------------------------------------------------------------

def build_register(book, fmts: FormatBook, cfg: Config, reg: Registry,
                   module) -> SheetWriter:
    """Create one register sheet from its :class:`SheetSpec`."""
    spec: SheetSpec = reg[module.NAME]
    sheet = SheetWriter(book, fmts, cfg, reg, spec.name,
                        tab_color=spec.tab_color)
    sheet.grid(spec)
    decorate = getattr(module, "decorate", None)
    if decorate is not None:
        wants_registry = len(inspect.signature(decorate).parameters) >= 4
        if wants_registry:
            decorate(sheet, fmts, cfg, reg)
        else:
            decorate(sheet, fmts, cfg)
    sheet.protect()
    return sheet


def build_workbook(path: str = "Inventory & Wholesale Manager.xlsx",
                   cfg: Optional[Config] = None) -> str:
    """Write the whole product to *path* and return the path."""
    cfg = cfg or Config()
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    book = Workbook(path)
    _set_properties(book, cfg)

    fmts = FormatBook(book, cfg)
    reg = Registry()

    # 1. Register every spec first so cross sheet formulas resolve no
    #    matter which tab happens to be written first.
    for module in REGISTER_MODULES:
        reg.add(module.spec(cfg))

    # 2. Write the tabs in their final order.
    sheets: Dict[str, SheetWriter] = {}
    for name in SHEET_ORDER:
        if name in REGISTER_BY_NAME:
            sheets[name] = build_register(book, fmts, cfg, reg,
                                          REGISTER_BY_NAME[name])
        elif name in PAGE_BUILDERS:
            sheets[name] = PAGE_BUILDERS[name](book, fmts, cfg, reg)
        else:                                   # pragma: no cover
            raise KeyError(f"No builder for sheet '{name}'")

    # 3. Live lookup names - SKUs above all, because nine tabs take
    #    their drop-down from that one column.
    define_cross_sheet_names(book, reg)

    # 4. Final touches: open on the dashboard.
    first = sheets[SHEET_ORDER[0]].ws
    first.activate()
    first.set_first_sheet()

    book.close()
    return path


def _set_properties(book, cfg: Config) -> None:
    book.set_properties({
        "title": cfg.product_name,
        "subject": "Products, SKUs, stock levels, suppliers, purchase "
                   "orders, wholesale customers, tiered pricing, "
                   "orders, reordering, valuation and profit by "
                   "product",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Small business spreadsheet template",
        "keywords": ("inventory management spreadsheet, stock "
                     "tracker, SKU tracker, wholesale order "
                     "manager, purchase order template, supplier "
                     "database, reorder point calculator, inventory "
                     "valuation, COGS tracker, profit by product, "
                     "small business inventory template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {VERSION}. Formula cells are locked "
                     f"and every sheet is protected with the "
                     f"password '{cfg.password}'. Stock is derived "
                     f"from recorded transactions and is never typed "
                     f"over. Costing is weighted average throughout. "
                     f"This workbook does not connect to or "
                     f"synchronise with any marketplace."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
