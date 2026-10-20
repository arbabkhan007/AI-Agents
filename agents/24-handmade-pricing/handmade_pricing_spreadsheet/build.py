"""Workbook builder: puts every tab together in the right order.

Typical use::

    from handmade_pricing_spreadsheet import build_workbook
    build_workbook("Handmade Product Pricing & Profit Calculator.xlsx")
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
from .sheets import (batches, break_even, bundle_lines, bundles, candles,
                     channels, clothing, competitors, crochet, dashboard,
                     development, digital, events, help_tab, jewelry,
                     labor, lists, material_usage, materials, overhead,
                     packaging, price_history, printables, products,
                     promotions, reports, retail_calc, sales, scenarios,
                     settings, shipping, start_here, variations,
                     waste, wholesale_calc, wholesale_customers,
                     wholesale_orders, woodworking)
from .writer import SheetWriter

#: register modules, in the order their specs are registered
REGISTER_MODULES = [
    products, materials, material_usage, labor, packaging, shipping,
    overhead, channels, crochet, jewelry, candles, clothing, woodworking,
    digital, bundles, bundle_lines, variations, batches, sales,
    promotions, price_history, competitors, waste, development, events,
    wholesale_customers, wholesale_orders,
]

#: tab order of the finished workbook
SHEET_ORDER: List[str] = [
    "Start Here", "Settings", "Dashboard",
    "Products", "Materials", "Material Usage", "Labor",
    "Packaging", "Shipping", "Overhead", "Channels",
    "Retail Calculator", "Wholesale Calculator", "Profit & Break-Even",
    "Crochet", "Jewelry", "Candles", "Clothing", "Woodworking", "Digital",
    "Bundles", "Bundle Lines", "Variations", "Batches",
    "Sales", "Promotions", "Price History", "Competitors",
    "Waste Log", "Development", "Events",
    "Wholesale Customers", "Wholesale Orders",
    "Scenarios", "Reports",
    "Print Costing", "Print Quote", "Print Order",
    "Lists", "Help",
]

#: sheets that are not registers - name -> builder(book, fmts, cfg, reg)
PAGE_BUILDERS: Dict[str, Callable] = {
    "Start Here": start_here.build,
    "Settings": settings.build,
    "Dashboard": dashboard.build,
    "Retail Calculator": retail_calc.build,
    "Wholesale Calculator": wholesale_calc.build,
    "Profit & Break-Even": break_even.build,
    "Scenarios": scenarios.build,
    "Reports": reports.build,
    "Print Costing": printables.build_costing,
    "Print Quote": printables.build_quote,
    "Print Order": printables.build_order,
    "Lists": lists.build,
    "Help": help_tab.build,
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


def build_workbook(path: str = "Handmade Pricing Calculator.xlsx",
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

    # 3. Live lookup names (product IDs, material names, who buys wholesale).
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
        "subject": "Handmade product pricing, material and labour costing, "
                   "margins and wholesale prices",
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Small business spreadsheet template",
        "keywords": ("handmade pricing calculator, Etsy pricing "
                     "spreadsheet, craft pricing, material cost "
                     "tracker, labor cost calculator, profit margin "
                     "calculator, wholesale price calculator, "
                     "break-even calculator, craft business, "
                     "spreadsheet template"),
        "comments": (f"{cfg.product_name}. Created by {cfg.author}. "
                     f"Version {cfg.version}. Formula cells are locked "
                     f"and every sheet is protected with the password "
                     f"'{cfg.password}'."),
        "status": "Final",
        "created": _dt.datetime(cfg.today.year, cfg.today.month,
                                cfg.today.day),
    })
