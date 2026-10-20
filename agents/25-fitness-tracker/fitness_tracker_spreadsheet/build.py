"""Workbook builder: puts every tab together in the right order.

Typical use::

    from fitness_tracker_spreadsheet import build_workbook
    build_workbook("Fitness & Weight Loss Tracker.xlsx")
"""

from __future__ import annotations

import datetime as _dt
import inspect
import os
from typing import Callable, Dict, List, Optional

from xlsxwriter.workbook import Workbook

from .config import SHEET_TABS, Config
from .formats import FormatBook
from .layout import Registry, SheetSpec
from .names import define_cross_sheet_names
from .sheets import (cardio, dashboard, exercise_library, habits, meals,
                     measurements, planner, profile, records, reports,
                     review, settings_lists, start_here, water_sleep,
                     weight, workout_log)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [
    workout_log, exercise_library, cardio, weight, measurements,
    meals, water_sleep, records,
]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = list(SHEET_TABS)

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "1 Start Here": start_here.build,
    "2 Profile & Goals": profile.build,
    "3 Dashboard": dashboard.build,
    "4 Workout Planner": planner.build,
    "10 Habit Tracker": habits.build,
    "14 Weekly & Monthly Review": review.build,
    "15 Reports & Charts": reports.build,
    "16 Settings & Lists": settings_lists.build,
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


def build_workbook(path: str = "Fitness Tracker.xlsx",
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

    # 3. Live lookup names (exercise names, food names, log dates).
    define_cross_sheet_names(book, reg)

    # 4. Final touches: open on the first page.
    first = sheets[SHEET_ORDER[0]].ws
    first.activate()
    first.set_first_sheet()

    book.close()
    return path


def _set_properties(book, cfg: Config) -> None:
    book.set_properties({
        "title": cfg.product_name,
        "subject": "Workout planner and log, weight and body measurement "
                   "tracker, habit and macro tracker",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Personal fitness spreadsheet template",
        "keywords": ("fitness tracker spreadsheet, weight loss tracker, "
                     "workout log, workout planner, body measurement "
                     "tracker, habit tracker, macro tracker, Excel "
                     "Google Sheets template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {cfg.version}. Formula cells are locked "
                     f"and every sheet is protected with the password "
                     f"'{cfg.password}'. For personal tracking only - "
                     f"not medical advice."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
