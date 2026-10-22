"""Assembly order for the Salon Business Management System."""

from __future__ import annotations

import datetime as _dt
import inspect
import os
from typing import Dict, Optional

from xlsxwriter import Workbook

from .config import Config, SHEET_TABS
from .formats import FormatBook
from .layout import Registry, SheetSpec
from .names import define_cross_sheet_names
from .writer import SheetWriter

from .sheets import (analytics, appointments, clients, commissions,
                     dashboard, expenses, goals, inventory, loyalty,
                     marketing, payments, payroll, pnl, purchases,
                     reports, sales, services, settings, staff,
                     start_here)

REGISTER_MODULES = [
    appointments, clients, services, sales, payments, staff, payroll,
    expenses, inventory, purchases, marketing, loyalty, goals,
]
REGISTER_BY_NAME = {m.NAME: m for m in REGISTER_MODULES}

PAGE_BUILDERS = {
    start_here.NAME: start_here.build,
    dashboard.NAME: dashboard.build,
    commissions.NAME: commissions.build,
    pnl.NAME: pnl.build,
    analytics.NAME: analytics.build,
    reports.NAME: reports.build,
    settings.NAME: settings.build,
}

SHEET_ORDER = list(SHEET_TABS)


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


def build_workbook(path: str = "Salon Business Management System.xlsx",
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

    for module in REGISTER_MODULES:
        reg.add(module.spec(cfg))

    sheets: Dict[str, SheetWriter] = {}
    for name in SHEET_ORDER:
        if name in REGISTER_BY_NAME:
            sheets[name] = build_register(book, fmts, cfg, reg,
                                          REGISTER_BY_NAME[name])
        elif name in PAGE_BUILDERS:
            sheets[name] = PAGE_BUILDERS[name](book, fmts, cfg, reg)
        else:                                   # pragma: no cover
            raise KeyError(f"No builder for sheet '{name}'")

    define_cross_sheet_names(book, reg)

    first = sheets[SHEET_ORDER[0]].ws
    first.activate()
    first.set_first_sheet()

    book.close()
    return path


def _set_properties(book, cfg: Config) -> None:
    book.set_properties({
        "title": cfg.product_name,
        "subject": "Salon business management: appointments, client CRM, "
                   "services, sales, commissions, payroll, inventory, "
                   "profit and loss and reports",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Business spreadsheet template",
        "keywords": ("salon spreadsheet, appointment book, client CRM, "
                     "commission calculator, inventory tracker, profit "
                     "and loss, Excel Google Sheets template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {cfg.version}. Formula cells are locked "
                     f"and every sheet is protected with the password "
                     f"'{cfg.password}'. A business-organising tool - "
                     f"not accounting, payroll or tax advice."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
