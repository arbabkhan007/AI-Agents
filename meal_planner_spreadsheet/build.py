"""
Workbook assembly.

Every sheet lives in ``meal_planner_spreadsheet.sheets.<slug>`` and exposes
``build(writer, registry, cfg, ws)`` which returns the sheet's
:class:`~meal_planner_spreadsheet.layout.SheetSpec`.  ``build_workbook`` runs
two passes:

1. every module declares its sheet, so the registry knows all 36 tabs before
   any formula is rendered;
2. every module then draws itself - either through ``render()`` for the
   free-form tabs (Start Here, Dashboard, Weekly Planner, ...) or through the
   shared register writer for the data tabs.
"""

from __future__ import annotations

import importlib
import os
from typing import Dict, Iterable, List, Optional, Tuple

try:
    from .config import AUTHOR, Config, PRODUCT_NAME
    from .formats import Formats
    from .layout import Registry, SheetSpec
    from .names import install as install_names
    from .writer import Writer
except ImportError:                        # pragma: no cover
    from config import AUTHOR, Config, PRODUCT_NAME
    from formats import Formats
    from layout import Registry, SheetSpec
    from names import install as install_names
    from writer import Writer

#: tab order, exactly as the buyer sees it.
SHEET_ORDER: List[str] = [
    "Start Here",
    "Dashboard",
    "Weekly Planner",
    "Monthly Planner",
    "Settings",
    "Lists",
    "Household",
    "Recipes",
    "Recipe Ingredients",
    "Ingredients",
    "Meal Plan",
    "Grocery List",
    "Pantry",
    "Staples",
    "Leftovers",
    "Food Waste",
    "Meal Prep",
    "Dietary Filters",
    "Nutrition",
    "Budget",
    "Recipe Costs",
    "Converter",
    "Rotation",
    "Food Safety",
    "Fridge & Freezer",
    "Grocery Spending",
    "Store Prices",
    "Stores",
    "Events",
    "Goals",
    "Sustainability",
    "Reports",
    "Print Week",
    "Print Shopping",
    "Print Recipe",
    "Help",
]

#: tab name -> python module slug
SLUGS: Dict[str, str] = {
    "Start Here": "start_here",
    "Dashboard": "dashboard",
    "Weekly Planner": "weekly_planner",
    "Monthly Planner": "monthly_planner",
    "Settings": "settings",
    "Lists": "lists",
    "Household": "household",
    "Recipes": "recipes",
    "Recipe Ingredients": "recipe_ingredients",
    "Ingredients": "ingredients",
    "Meal Plan": "meal_plan",
    "Grocery List": "grocery_list",
    "Pantry": "pantry",
    "Staples": "staples",
    "Leftovers": "leftovers",
    "Food Waste": "food_waste",
    "Meal Prep": "meal_prep",
    "Dietary Filters": "dietary_filters",
    "Nutrition": "nutrition",
    "Budget": "budget",
    "Recipe Costs": "recipe_costs",
    "Converter": "converter",
    "Rotation": "rotation",
    "Food Safety": "food_safety",
    "Fridge & Freezer": "fridge_freezer",
    "Grocery Spending": "grocery_spending",
    "Store Prices": "store_prices",
    "Stores": "stores",
    "Events": "events",
    "Goals": "goals",
    "Sustainability": "sustainability",
    "Reports": "reports",
    "Print Week": "print_week",
    "Print Shopping": "print_shopping",
    "Print Recipe": "print_recipe",
    "Help": "help",
}

#: tabs that are free-form (they draw themselves in ``render``)
CUSTOM_RENDER = {"Start Here", "Dashboard", "Weekly Planner",
                 "Monthly Planner", "Settings", "Lists", "Reports",
                 "Print Week", "Print Shopping", "Print Recipe", "Help",
                 "Nutrition", "Budget", "Converter", "Goals", "Household"}


def module_for(name: str):
    slug = SLUGS[name]
    return importlib.import_module(f".sheets.{slug}", __package__)


def build_workbook(path: str, cfg: Optional[Config] = None) -> str:
    """Write the workbook to ``path`` and return the path."""
    cfg = cfg or Config()
    directory = os.path.dirname(os.path.abspath(path))
    if directory:
        os.makedirs(directory, exist_ok=True)

    import xlsxwriter

    workbook = xlsxwriter.Workbook(path, {
        "strings_to_numbers": False,
        "strings_to_formulas": False,
        "default_date_format": cfg.date_format,
        "use_future_functions": False,     # keep every formula Excel 2010 safe
    })

    workbook.set_properties({
        "title": cfg.product_name,
        "subject": cfg.product_subtitle,
        "author": cfg.author,
        "company": cfg.author,
        "category": "Spreadsheet",
        "keywords": "meal planner, grocery list, recipe organizer, "
                    "meal prep, pantry inventory, food budget, nutrition",
        "comments": f"{cfg.product_name} by {cfg.author}. "
                    f"Version {cfg.version}.",
        "status": "Finished",
        "created": None,
    })
    workbook.set_calc_mode("auto")

    registry = Registry()
    formats = Formats(workbook, cfg)
    writer = Writer(workbook, cfg, registry, formats)

    if cfg.include_sample_data:
        from . import sample_data
        writer.samples = sample_data.build_samples(cfg)

    worksheets: Dict[str, object] = {}
    specs: Dict[str, SheetSpec] = {}
    for name in SHEET_ORDER:
        worksheets[name] = writer.sheet(name)

    # pass 0 - declare every tab.  Sheet modules reference each other's
    # ranges while they build their own columns, so the registry is filled
    # once with placeholder references, then again with the real ones.
    registry.strict = False
    for name in SHEET_ORDER:
        module_for(name).build(writer, registry, cfg, worksheets[name])

    # pass 1 - declare every sheet again, now that every tab exists, so
    # formulas can reference any of the 36 tabs
    registry.strict = True
    for name in SHEET_ORDER:
        module = module_for(name)
        spec = module.build(writer, registry, cfg, worksheets[name])
        if spec.name != name:
            raise ValueError(f"module {SLUGS[name]} registered "
                             f"'{spec.name}' instead of '{name}'")
        specs[name] = spec

    # pass 2 - draw
    for name in SHEET_ORDER:
        module = module_for(name)
        ws = worksheets[name]
        spec = specs[name]
        render = getattr(module, "render", None)
        if render is not None:
            render(ws, spec, writer, cfg)
        else:
            writer.register(ws, spec)
            writer.finish_sheet(ws, spec)

    installed = install_names(workbook, registry, cfg)

    # the first tab is the one the buyer lands on
    worksheets["Start Here"].activate()
    workbook.close()

    cfg._installed_names = installed           # handy for the tools
    return path


def build_pair(directory: str, cfg: Optional[Config] = None,
               blank: bool = True
               ) -> Tuple[str, Optional[str]]:
    """Write the filled workbook and, optionally, the blank one."""
    cfg = cfg or Config()
    base = os.path.join(directory, f"{PRODUCT_NAME}.xlsx")
    filled = build_workbook(base, cfg)
    empty = None
    if blank:
        blank_cfg = Config(**{**cfg.__dict__,
                              "include_sample_data": False})
        empty_path = os.path.join(directory,
                                  f"{PRODUCT_NAME} (Blank - No Example "
                                  f"Data).xlsx")
        empty = build_workbook(empty_path, blank_cfg)
    return filled, empty


def main() -> int:                                # pragma: no cover
    from .cli import main as cli_main
    return cli_main()


if __name__ == "__main__":                        # pragma: no cover
    raise SystemExit(main())
