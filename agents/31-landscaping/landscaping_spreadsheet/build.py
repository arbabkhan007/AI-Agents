"""Workbook builder: puts the twenty-three tabs together in order.

Typical use::

    from landscaping_spreadsheet import build_workbook
    build_workbook("Ultimate Landscaping & Lawn Care Manager.xlsx")
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
from .sheets import (annual, contracts, crew, customers, dashboard,
                     equipment, expenses, feedback, getting_started,
                     invoices, jobs, materials, monthly, profit,
                     properties, quotes, route, schedule, seasonal,
                     services, settings, timesheets, vehicles)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [
    customers, properties, services, quotes, jobs, contracts, crew,
    schedule, timesheets, equipment, vehicles, materials, invoices,
    expenses, feedback, profit,
]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = [
    "Dashboard",
    "Getting Started",
    "Settings & Lists",
    "Customer CRM",
    "Property Database",
    "Service Catalog",
    "Quote Calculator",
    "Job & Work Orders",
    "Route Planner",
    "Recurring Contracts",
    "Crew Database",
    "Crew Schedule",
    "Timesheets & Payroll",
    "Equipment Inventory",
    "Vehicle & Fuel Tracker",
    "Materials Inventory",
    "Invoice & Payments",
    "Expense Tracker",
    "Customer Feedback",
    "Seasonal Planner",
    "Profit Analysis",
    "Monthly Reports",
    "Annual Reports",
]

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "Dashboard": dashboard.build,
    "Getting Started": getting_started.build,
    "Settings & Lists": settings.build,
    "Route Planner": route.build,
    "Seasonal Planner": seasonal.build,
    "Monthly Reports": monthly.build,
    "Annual Reports": annual.build,
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


def build_workbook(path: str = "Landscaping & Lawn Care Manager.xlsx",
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

    # 3. Live lookup names - the Customer and Property IDs above all,
    #    because every drop-down that joins the workbook reads them.
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
        "subject": "Customers, properties, quotes, jobs, routes, "
                   "recurring contracts, crew, timesheets, equipment, "
                   "materials, invoices and profit by job for a lawn "
                   "care and landscaping business",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Small business spreadsheet template",
        "keywords": ("landscaping business spreadsheet, lawn care "
                     "business template, lawn care scheduling "
                     "spreadsheet, landscaping quote calculator, "
                     "lawn mowing route planner, recurring lawn "
                     "care contracts, crew timesheet tracker, "
                     "equipment maintenance log, landscaping job "
                     "costing, lawn care invoice tracker"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {VERSION}. Formula cells are locked "
                     "and every sheet is protected with the "
                     f"password '{cfg.password}'. Customer, Property, "
                     "Job and Invoice IDs connect the tabs. The "
                     "route planner organises stops manually - it "
                     "is not GPS navigation and does not optimise "
                     "routes. This workbook does not synchronise "
                     "with accounting, payroll or booking "
                     "software."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
