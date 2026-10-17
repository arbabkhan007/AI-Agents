"""Workbook builder: puts every tab together in the right order.

Typical use::

    from social_media_spreadsheet import build_workbook
    build_workbook("Social Media Content Planner.xlsx")
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
from .sheets import (ab_tests, accounts, ads, analytics, annual, assets,
                     brand_voice, budget, calc, calendar_sheet, campaigns,
                     captions, competitors, compliance, dashboard, goals,
                     hashtags, help_tab, ideas, influencers, launches,
                     lists, month_view, performance, personas, pillars,
                     platforms, printables, reports, repurposing, seasonal,
                     settings, start_here, tasks, team, trends, ugc,
                     workflow)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [
    accounts, personas, pillars, calendar_sheet, ideas, captions, hashtags,
    platforms.INSTAGRAM, platforms.TIKTOK, platforms.PINTEREST,
    platforms.YOUTUBE, platforms.FACEBOOK, campaigns, launches, seasonal,
    influencers, ugc, repurposing, competitors, trends, analytics,
    performance, ab_tests, ads, assets, goals, budget, team, tasks,
    compliance,
]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = [
    "Start Here", "Dashboard", "Annual Dashboard", "Settings", "Lists",
    "Brand Voice", "Accounts", "Audience Personas", "Content Pillars",
    "Content Calendar", "Month View", "Workflow",
    "Idea Bank", "Caption Bank", "Hashtag Bank",
    "Instagram", "TikTok", "Pinterest", "YouTube", "Facebook",
    "Campaigns", "Launch Planner", "Seasonal Planner",
    "Influencers", "UGC Tracker", "Repurposing", "Competitors", "Trends",
    "Analytics", "Performance", "AB Tests", "Ads", "Assets",
    "Goals", "Budget", "Team", "Tasks", "Compliance",
    "Reports", "Print Brief", "Print Week", "Help",
    "Calc",
]

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "Start Here": start_here.build,
    "Dashboard": dashboard.build,
    "Annual Dashboard": annual.build,
    "Month View": month_view.build,
    "Workflow": workflow.build,
    "Settings": settings.build,
    "Lists": lists.build,
    "Brand Voice": brand_voice.build,
    "Reports": reports.build,
    "Print Brief": printables.build_brief,
    "Print Week": printables.build_week,
    "Help": help_tab.build,
    "Calc": calc.build,
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


def build_workbook(path: str = "Social Media Content Planner.xlsx",
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

    # 3. Live lookup names (content IDs, campaign names, team members).
    define_cross_sheet_names(book, reg)

    # 4. Final touches: hide the engine, open on the first page.
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
        "subject": "Social media content planning and analytics",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Small business spreadsheet template",
        "keywords": ("social media, content calendar, content planner, "
                     "instagram, tiktok, pinterest, youtube, facebook, "
                     "analytics, engagement, hashtags, spreadsheet "
                     "template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {cfg.version}. Formula cells are locked and "
                     f"every sheet is protected with the password "
                     f"'{cfg.password}'."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
