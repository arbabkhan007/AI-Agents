"""Workbook builder: puts every tab together in the right order.

Typical use::

    from pet_sitting_spreadsheet import build_workbook
    build_workbook("Pet Sitting Business Spreadsheet.xlsx")
"""

from __future__ import annotations

import datetime as _dt
import inspect
import os
from typing import Callable, Dict, List, Optional

from xlsxwriter.workbook import Workbook

from .config import Config
from .formats import FormatBook
from .layout import Registry, SheetSpec
from .names import define_cross_sheet_names
from .sheets import (bookings, budget, calc, clients, dashboard, expenses,
                     health, help_tab, incidents, inventory, invoices, lists,
                     messages, mileage, payments, pets, printables, reminders,
                     reports, services, settings, staff, start_here, visits)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [services, clients, pets, bookings, visits, health,
                    incidents, messages, invoices, payments, expenses,
                    mileage, staff, inventory, reminders, calc]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = [
    "Start Here", "Dashboard", "Settings", "Lists", "Services", "Clients",
    "Pets", "Bookings", "Visit Log", "Health Log", "Incidents", "Messages",
    "Invoices", "Payments", "Expenses", "Mileage", "Staff", "Inventory",
    "Reminders", "Reports", "Budget", "Print Invoice", "Print Pet Care",
    "Print Visit", "Print Forms", "Help", "Calc",
]

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "Start Here": lambda b, f, c, r: _start_here(b, f, c, r),
    "Dashboard": dashboard.build,
    "Settings": settings.build,
    "Lists": lists.build,
    "Reports": reports.build,
    "Budget": budget.build,
    "Print Invoice": printables.build_invoice,
    "Print Pet Care": printables.build_care_sheet,
    "Print Visit": printables.build_visit_report,
    "Print Forms": printables.build_forms,
    "Help": help_tab.build,
}

#: register modules by sheet name
REGISTER_BY_NAME = {module.NAME: module for module in REGISTER_MODULES}


def _start_here(book, fmts, cfg, reg):
    from .sheets import start_here
    return start_here.build(book, fmts, cfg, reg)


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


def build_workbook(path: str = "Pet Sitting Business Spreadsheet.xlsx",
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

    # 1. Register every spec first so cross sheet formulas can be resolved
    #    no matter which tab is written first.
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

    # 3. Live lookup names (client names, pet references, invoice numbers).
    define_cross_sheet_names(book, reg)

    # 4. Final touches: hide the engine, open on the welcome page.
    if calc.NAME in sheets:
        sheets[calc.NAME].ws.hide()
    first = sheets[SHEET_ORDER[0]].ws
    first.activate()
    first.set_first_sheet()

    book.close()
    return path


def _set_properties(book, cfg: Config) -> None:
    book.set_properties({
        "title": cfg.product_name,
        "subject": "Pet sitting and dog walking business management",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Small business spreadsheet template",
        "keywords": ("pet sitting, dog walking, pet care, client booking, "
                     "invoices, payments, mileage, expenses, profit, "
                     "spreadsheet template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {cfg.version}. Formula cells are locked and "
                     f"every sheet is protected with the password "
                     f"'{cfg.password}'."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
