# Automated Meal Planner & Grocery List Spreadsheet

*Complete source code of the generator that writes the .xlsx product*

A pure Python program that writes a 36 tab Excel workbook for a household: a weekly and monthly meal planner, a recipe book with costings, an automatic grocery list, a pantry with use-by dates, a food budget, a nutrition log and printable pages for the fridge door.

**What it produces**

| | |
| --- | --- |
| Tabs | 36, all visible |
| Formulas | about 79,000, all Excel 2010 safe |
| Author | Novality Store |
| Protection | every sheet, password `premium` |
| Charts | none - the numbers are the report |
| Example data | 38 recipes, 62 ingredients, 107 planned meals |
| Dependency | XlsxWriter (openpyxl only for the checks) |

**How to run it**

```bash
pip install XlsxWriter
python build_meal_planner_workbook.py
```

Every formula cell is locked and every sheet is protected with the password `premium`, while the cream coloured cells you are meant to type in stay open.

**Useful options**

```text
-o, --output PATH     where to write the file
--blank               no example data, just the empty workbook
--no-protect          leave the sheets unlocked
--password TEXT       protection password (default: premium)
--author TEXT         document author  (default: Novality Store)
--household TEXT      household name on the Settings tab
--cook TEXT           main cook's name
--currency SYMBOL     currency symbol  (default: $)
--currency-code TEXT  three letter code  (default: USD)
--units {Metric,Imperial}  measurement system
--week-start {Monday,Sunday}
--year N              planning year
--budget N            weekly grocery budget
--servings N          default servings per meal
--rows N              rows of capacity in the big registers
--today YYYY-MM-DD    pretend it is this date (for the demo data)
```

Excel 2010 safe throughout: no dynamic arrays, no `XLOOKUP`, no `IFS`, nothing that needs array entry - so it opens in Excel 2010 and later, Google Sheets, LibreOffice and Numbers.

---

## Contents

| # | File | Lines | What it does |
| --- | --- | --- | --- |
| 1 | [`build_meal_planner_workbook.py`](#build_meal_planner_workbookpy) | 19 | Build the Automated Meal Planner & Grocery List Spreadsheet |
| 2 | [`meal_planner_spreadsheet/__init__.py`](#meal_planner_spreadsheet__init__py) | 19 | Automated Meal Planner & Grocery List Spreadsheet |
| 2 | [`meal_planner_spreadsheet/__main__.py`](#meal_planner_spreadsheet__main__py) | 6 | ``python -m social_media_spreadsheet`` |
| 2 | [`meal_planner_spreadsheet/cli.py`](#meal_planner_spreadsheetclipy) | 139 | Command line front end |
| 2 | [`meal_planner_spreadsheet/config.py`](#meal_planner_spreadsheetconfigpy) | 241 | Configuration for the Automated Meal Planner & Grocery List Spreadsheet |
| 2 | [`meal_planner_spreadsheet/layout.py`](#meal_planner_spreadsheetlayoutpy) | 306 | Layout engine |
| 2 | [`meal_planner_spreadsheet/formats.py`](#meal_planner_spreadsheetformatspy) | 286 | The format book |
| 2 | [`meal_planner_spreadsheet/writer.py`](#meal_planner_spreadsheetwriterpy) | 397 | The writer |
| 2 | [`meal_planner_spreadsheet/names.py`](#meal_planner_spreadsheetnamespy) | 144 | Defined names |
| 2 | [`meal_planner_spreadsheet/build.py`](#meal_planner_spreadsheetbuildpy) | 235 | Workbook assembly |
| 2 | [`meal_planner_spreadsheet/sample_data.py`](#meal_planner_spreadsheetsample_datapy) | 1066 | Example data |
| 3 | [`meal_planner_spreadsheet/sheets/__init__.py`](#meal_planner_spreadsheetsheets__init__py) | 6 | One module per tab |
| 3 | [`meal_planner_spreadsheet/sheets/lists.py`](#meal_planner_spreadsheetsheetslistspy) | 114 | Lists - every drop down source in one place |
| 3 | [`meal_planner_spreadsheet/sheets/settings.py`](#meal_planner_spreadsheetsheetssettingspy) | 239 | Settings - the single control panel for the whole workbook |
| 3 | [`meal_planner_spreadsheet/sheets/household.py`](#meal_planner_spreadsheetsheetshouseholdpy) | 82 | Household - who you are cooking for |
| 3 | [`meal_planner_spreadsheet/sheets/recipes.py`](#meal_planner_spreadsheetsheetsrecipespy) | 204 | Recipes - the recipe book |
| 3 | [`meal_planner_spreadsheet/sheets/recipe_ingredients.py`](#meal_planner_spreadsheetsheetsrecipe_ingredientspy) | 161 | Recipe Ingredients - what goes into each recipe, and what it costs |
| 3 | [`meal_planner_spreadsheet/sheets/ingredients.py`](#meal_planner_spreadsheetsheetsingredientspy) | 191 | Ingredients - the master list of everything you buy |
| 3 | [`meal_planner_spreadsheet/sheets/meal_plan.py`](#meal_planner_spreadsheetsheetsmeal_planpy) | 168 | Meal Plan - the engine of the workbook |
| 3 | [`meal_planner_spreadsheet/sheets/grocery_list.py`](#meal_planner_spreadsheetsheetsgrocery_listpy) | 140 | Grocery List - the shopping list that writes itself |
| 3 | [`meal_planner_spreadsheet/sheets/pantry.py`](#meal_planner_spreadsheetsheetspantrypy) | 148 | Pantry - what you have, what is running low, what expires next |
| 3 | [`meal_planner_spreadsheet/sheets/staples.py`](#meal_planner_spreadsheetsheetsstaplespy) | 112 | Staples - the things you buy every single week |
| 3 | [`meal_planner_spreadsheet/sheets/leftovers.py`](#meal_planner_spreadsheetsheetsleftoverspy) | 107 | Leftovers - the queue of cooked food waiting to be eaten |
| 3 | [`meal_planner_spreadsheet/sheets/food_waste.py`](#meal_planner_spreadsheetsheetsfood_wastepy) | 109 | Food Waste - what got thrown away, why, and what it cost |
| 3 | [`meal_planner_spreadsheet/sheets/meal_prep.py`](#meal_planner_spreadsheetsheetsmeal_preppy) | 116 | Meal Prep - batch cooking tasks and what to do when |
| 3 | [`meal_planner_spreadsheet/sheets/dietary_filters.py`](#meal_planner_spreadsheetsheetsdietary_filterspy) | 77 | Dietary Filters - allergies, intolerances and dietary needs |
| 3 | [`meal_planner_spreadsheet/sheets/rotation.py`](#meal_planner_spreadsheetsheetsrotationpy) | 100 | Rotation - how often each meal repeats |
| 3 | [`meal_planner_spreadsheet/sheets/food_safety.py`](#meal_planner_spreadsheetsheetsfood_safetypy) | 107 | Food Safety - how long food keeps, and at what temperature |
| 3 | [`meal_planner_spreadsheet/sheets/fridge_freezer.py`](#meal_planner_spreadsheetsheetsfridge_freezerpy) | 100 | Fridge & Freezer - batch cooked portions and their use-by dates |
| 3 | [`meal_planner_spreadsheet/sheets/grocery_spending.py`](#meal_planner_spreadsheetsheetsgrocery_spendingpy) | 114 | Grocery Spending - every shop you record, against the budget |
| 3 | [`meal_planner_spreadsheet/sheets/store_prices.py`](#meal_planner_spreadsheetsheetsstore_pricespy) | 107 | Store Prices - the same item, priced at every shop |
| 3 | [`meal_planner_spreadsheet/sheets/stores.py`](#meal_planner_spreadsheetsheetsstorespy) | 99 | Stores - where you shop |
| 3 | [`meal_planner_spreadsheet/sheets/events.py`](#meal_planner_spreadsheetsheetseventspy) | 114 | Events - parties, holidays and dinner guests |
| 3 | [`meal_planner_spreadsheet/sheets/sustainability.py`](#meal_planner_spreadsheetsheetssustainabilitypy) | 110 | Sustainability - waste, packaging and how local your shopping is |
| 3 | [`meal_planner_spreadsheet/sheets/recipe_costs.py`](#meal_planner_spreadsheetsheetsrecipe_costspy) | 123 | Recipe Costs - what every dish really costs to put on the table |
| 3 | [`meal_planner_spreadsheet/sheets/converter.py`](#meal_planner_spreadsheetsheetsconverterpy) | 152 | Converter - unit conversions and a live converter you can use |
| 4 | [`meal_planner_spreadsheet/sheets/dashboard.py`](#meal_planner_spreadsheetsheetsdashboardpy) | 347 | Dashboard - the week at a glance |
| 4 | [`meal_planner_spreadsheet/sheets/weekly_planner.py`](#meal_planner_spreadsheetsheetsweekly_plannerpy) | 159 | Weekly Planner - one week, day by day |
| 4 | [`meal_planner_spreadsheet/sheets/monthly_planner.py`](#meal_planner_spreadsheetsheetsmonthly_plannerpy) | 135 | Monthly Planner - the whole month on one page |
| 4 | [`meal_planner_spreadsheet/sheets/nutrition.py`](#meal_planner_spreadsheetsheetsnutritionpy) | 232 | Nutrition - the daily log against your targets |
| 4 | [`meal_planner_spreadsheet/sheets/budget.py`](#meal_planner_spreadsheetsheetsbudgetpy) | 178 | Budget - planned versus actual food spend, month by month |
| 4 | [`meal_planner_spreadsheet/sheets/goals.py`](#meal_planner_spreadsheetsheetsgoalspy) | 153 | Goals - habit goals with a live progress bar |
| 4 | [`meal_planner_spreadsheet/sheets/reports.py`](#meal_planner_spreadsheetsheetsreportspy) | 297 | Reports - any date range, on one page |
| 4 | [`meal_planner_spreadsheet/sheets/start_here.py`](#meal_planner_spreadsheetsheetsstart_herepy) | 200 | Start Here - the landing tab the buyer sees first |
| 4 | [`meal_planner_spreadsheet/sheets/print_week.py`](#meal_planner_spreadsheetsheetsprint_weekpy) | 122 | Print Week - a weekly meal plan for the fridge door |
| 4 | [`meal_planner_spreadsheet/sheets/print_shopping.py`](#meal_planner_spreadsheetsheetsprint_shoppingpy) | 110 | Print Shopping - a printable grocery list |
| 4 | [`meal_planner_spreadsheet/sheets/print_recipe.py`](#meal_planner_spreadsheetsheetsprint_recipepy) | 179 | Print Recipe - a printable recipe card |
| 4 | [`meal_planner_spreadsheet/sheets/help.py`](#meal_planner_spreadsheetsheetshelppy) | 179 | Help - questions, answers and troubleshooting |
| 5 | [`tools/validate_meal_workbook.py`](#toolsvalidate_meal_workbookpy) | 271 | Check a built meal planner workbook |
| 5 | [`tools/check_meal_sample.py`](#toolscheck_meal_samplepy) | 223 | Check that the example data in a built workbook hangs together |
| 5 | [`tools/recalc_check.py`](#toolsrecalc_checkpy) | 212 | Recalculate a small build and check the numbers come out right |
| 5 | [`tools/export_source_md.py`](#toolsexport_source_mdpy) | 555 | Write every source file of a generator into one clean markdown document |
| 5 | [`tools/make_download_zip.py`](#toolsmake_download_zippy) | 124 | Pack the generator into a single zip people can download and run |

---

## 1. Run it

Save the files below keeping these exact paths, then run the one liner. Nothing else is needed - no project file, no build step.

```bash
pip install XlsxWriter
python build_meal_planner_workbook.py
```

The workbook lands in `output/Meal Planner & Grocery List.xlsx`.

### `build_meal_planner_workbook.py`

Build the Automated Meal Planner & Grocery List Spreadsheet *(19 lines)*

````python
#!/usr/bin/env python3
"""Build the Automated Meal Planner & Grocery List Spreadsheet.

    python build_meal_planner_workbook.py
    python build_meal_planner_workbook.py --blank -o "output/Blank.xlsx"
    python build_meal_planner_workbook.py --rows 400 --currency "£"

Everything lives in the `meal_planner_spreadsheet` package; this file is
just a friendly front door so you do not have to remember `-m`.
"""

from __future__ import annotations

import sys

from meal_planner_spreadsheet.cli import main

if __name__ == "__main__":
    sys.exit(main())
````

---

## 2. The package

Configuration, the formula template engine, cell formats, the sheet writer and the demo data. These are the parts every tab leans on.

### `meal_planner_spreadsheet/__init__.py`

Automated Meal Planner & Grocery List Spreadsheet *(19 lines)*

````python
"""Automated Meal Planner & Grocery List Spreadsheet.

Build the workbook with::

    python -m meal_planner_spreadsheet -o "output/Meal Planner.xlsx"

or from Python::

    from meal_planner_spreadsheet import build_workbook
    build_workbook("Meal Planner.xlsx")
"""

from .build import build_workbook
from .config import (AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME,
                     PRODUCT_SUBTITLE, PRODUCT_VERSION, Config)

__all__ = ["build_workbook", "Config", "AUTHOR", "PRODUCT_NAME",
           "PRODUCT_SUBTITLE", "PRODUCT_LISTING_TITLE", "PRODUCT_VERSION"]
__version__ = PRODUCT_VERSION
````

### `meal_planner_spreadsheet/__main__.py`

``python -m social_media_spreadsheet`` *(6 lines)*

````python
"""``python -m social_media_spreadsheet``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
````

### `meal_planner_spreadsheet/cli.py`

Command line front end *(139 lines)*

````python
"""Command line front end.

    python -m meal_planner_spreadsheet
    python -m meal_planner_spreadsheet -o "output/Meal Planner.xlsx" --blank
    python -m meal_planner_spreadsheet --currency "$" --year 2027 --rows 300
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from typing import List, Optional

from .build import SHEET_ORDER, build_workbook
from .config import AUTHOR, PRODUCT_LISTING_TITLE, PRODUCT_NAME, Config

DEFAULT_OUTPUT = os.path.join(
    "output", "Meal Planner & Grocery List.xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meal_planner_spreadsheet",
        description=f"Build the {PRODUCT_NAME} workbook.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help="where to write the .xlsx file")
    parser.add_argument("--blank", action="store_true",
                        help="leave the registers empty "
                             "(no example records)")
    parser.add_argument("--no-protect", action="store_true",
                        help="do not protect the sheets (for development)")
    parser.add_argument("--password", default=None,
                        help="sheet protection password")
    parser.add_argument("--author", default=AUTHOR,
                        help="document author / creator")
    parser.add_argument("--household", default=None,
                        help="pre-fill the household name on Settings")
    parser.add_argument("--cook", default=None,
                        help="pre-fill the main cook's name on Settings")
    parser.add_argument("--currency", default=None,
                        help="currency symbol, e.g. $ £ € A$")
    parser.add_argument("--currency-code", default=None,
                        help="three letter currency code, e.g. USD")
    parser.add_argument("--year", type=int, default=None,
                        help="planning year the planner opens on")
    parser.add_argument("--week-start", choices=["Monday", "Sunday"],
                        default=None, help="first day of the week")
    parser.add_argument("--servings", type=int, default=None,
                        help="default number of people a meal feeds")
    parser.add_argument("--budget", type=float, default=None,
                        help="weekly grocery budget")
    parser.add_argument("--units", choices=["Metric", "Imperial"],
                        default=None,
                        help="which measurement system to lead with")
    parser.add_argument("--rows", type=int, default=None,
                        help="scale every register (the default row "
                             "counts are multiplied to fit this many "
                             "recipe rows)")
    parser.add_argument("--today", default=None,
                        help="treat this ISO date as 'today' when "
                             "generating the example data")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the output path")
    return parser


def config_from_args(args: argparse.Namespace) -> Config:
    kwargs = {}
    if args.blank:
        kwargs["include_sample_data"] = False
    if args.no_protect:
        kwargs["protect_sheets"] = False
    if args.password:
        kwargs["password"] = args.password
    if args.author:
        kwargs["author"] = args.author
    if args.currency:
        kwargs["currency_symbol"] = args.currency
    if args.currency_code:
        kwargs["currency_code"] = args.currency_code
    if args.week_start:
        kwargs["week_start"] = args.week_start
    if args.year:
        kwargs["plan_year"] = args.year
    if args.servings:
        kwargs["default_servings"] = args.servings
    if args.units:
        kwargs["measurement_system"] = args.units
    if args.budget:
        kwargs["weekly_food_budget"] = args.budget
        kwargs["monthly_food_budget"] = round(args.budget * 52 / 12, 2)
        kwargs["annual_food_budget"] = round(args.budget * 52, 2)
    if args.today:
        kwargs["today"] = _dt.date.fromisoformat(args.today)
    cfg = Config(**kwargs)
    if args.household:
        cfg.household.name = args.household
    if args.cook:
        cfg.household.cook = args.cook
    if args.rows:
        cfg.scale_rows(args.rows)
    return cfg


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = config_from_args(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    path = build_workbook(args.output, cfg)
    size = os.path.getsize(path) / 1024.0

    if args.quiet:
        print(path)
        return 0

    print(f"{cfg.product_name}")
    print(f"  listing title : {PRODUCT_LISTING_TITLE}")
    print(f"  author        : {cfg.author}")
    print(f"  sheets        : {len(SHEET_ORDER)}")
    print(f"  planning year : {cfg.year}")
    print(f"  household     : {cfg.household.name} "
          f"({cfg.members} people)")
    print(f"  example data  : "
          f"{'no' if not cfg.include_sample_data else 'yes'}")
    print(f"  protection    : "
          f"{'off' if not cfg.protect_sheets else 'on, password ' + cfg.password}")
    print(f"  written to    : {os.path.abspath(path)}  ({size:,.0f} KB)")
    return 0


if __name__ == "__main__":        # pragma: no cover
    raise SystemExit(main())
````

### `meal_planner_spreadsheet/config.py`

Configuration for the Automated Meal Planner & Grocery List Spreadsheet *(241 lines)*

````python
"""
Configuration for the Automated Meal Planner & Grocery List Spreadsheet.

Everything a shop owner may want to re-brand lives here, so the workbook can
be regenerated for a different household, currency, measurement system or
country without touching any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Automated Meal Planner & Grocery List Spreadsheet"
PRODUCT_SUBTITLE = (
    "Weekly & Monthly Meal Planner, Recipe Organizer, Automatic Grocery "
    "List, Pantry Inventory, Food Budget & Nutrition Tracker"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Automated Meal Planner Spreadsheet, Weekly and Monthly Meal Planner, "
    "Recipe Organizer, Grocery List, Pantry Inventory, Food Budget and "
    "Nutrition Tracker"
)

#: Password that protects every sheet so formula cells cannot be edited by
#: accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: The meal slots the planner covers out of the box.  Edit them on the Lists
#: tab and every drop down, planner grid and nutrition total follows.
MEAL_SLOTS = ["Breakfast", "Morning snack", "Lunch", "Afternoon snack",
              "Dinner", "Evening snack", "Dessert"]

#: The three meal slots the dashboards and the printable day plan lead with.
MAIN_SLOTS = ["Breakfast", "Lunch", "Dinner"]


# ---------------------------------------------------------------------------
# Colours - a warm kitchen palette: herb green, terracotta, cream
# ---------------------------------------------------------------------------

class Palette:
    ink = "#1E2C22"           # darkest green - titles
    primary = "#2F5E43"       # headers
    primary_mid = "#4E8A63"   # section bands
    primary_soft = "#E2EFE6"  # light band / alternating rows
    accent = "#D9703C"        # terracotta accent
    accent_soft = "#FBE9DC"
    input_bg = "#FFFDF7"      # editable cell background (warm cream)
    input_border = "#E8DEC6"
    calc_bg = "#EFF4F0"       # locked formula cell background (soft sage)
    calc_border = "#D2E0D6"
    white = "#FFFFFF"
    grey_text = "#5A6560"
    line = "#C2D4C7"
    good_bg = "#D9F2E4"
    good_text = "#0E6B45"
    warn_bg = "#FFF1CF"
    warn_text = "#8A5A00"
    bad_bg = "#FBD9DD"
    bad_text = "#9C1C2E"
    info_bg = "#DEE8FA"
    info_text = "#2A4A8B"
    note_bg = "#F7FAF8"


# ---------------------------------------------------------------------------
# Row capacity of every register (how many pre-formatted / pre-formulated rows)
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Settings": 0,
    "Lists": 40,
    "Household": 12,
    "Food Preferences": 40,
    "Recipes": 200,
    "Recipe Ingredients": 1200,
    "Ingredients": 300,
    "Meal Plan": 500,
    "Grocery List": 300,
    "Pantry": 300,
    "Fridge & Freezer": 150,
    "Leftovers": 120,
    "Budget": 60,
    "Grocery Spending": 400,
    "Recipe Costs": 200,
    "Converter": 40,
    "Nutrition": 120,
    "Meal Prep": 120,
    "Staples": 100,
    "Stores": 40,
    "Store Prices": 300,
    "Rotation": 200,
    "Household Tasks": 120,
    "Food Safety": 60,
    "Events": 40,
    "Event Menu": 150,
    "Goals": 40,
    "Habits": 120,
    "Food Waste": 150,
}


@dataclass
class HouseholdDefaults:
    """Sample values written into the Household Profile (Settings) sheet."""

    name: str = "The Harper Household"
    cook: str = "Maya Harper"
    email: str = "maya@harperhome.com"
    members: int = 4
    town: str = "Portland, OR"
    store: str = "Greenfield Market"
    notes: str = "Two adults, two children, one nut allergy in the house"


# ---------------------------------------------------------------------------
# The configuration object every sheet module reads
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Everything the generator needs to know to write one workbook."""

    author: str = AUTHOR
    product_name: str = PRODUCT_NAME
    product_subtitle: str = PRODUCT_SUBTITLE
    listing_title: str = PRODUCT_LISTING_TITLE
    version: str = PRODUCT_VERSION
    password: str = FORMULA_PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True

    # Formatting ------------------------------------------------------------
    currency_symbol: str = "$"
    currency_code: str = "USD"
    date_format: str = "dd-mmm-yyyy"
    time_format: str = "h:mm AM/PM"

    # Household / planning defaults pre-filled on the Settings tab ----------
    household: HouseholdDefaults = field(default_factory=HouseholdDefaults)
    plan_year: int = 0                # 0 = the year of `today`
    week_start: str = "Monday"
    measurement_system: str = "Metric"   # Metric | Imperial
    default_servings: int = 4
    members: int = 4

    # Budget ----------------------------------------------------------------
    weekly_food_budget: float = 180.0
    monthly_food_budget: float = 780.0
    annual_food_budget: float = 9360.0
    eating_out_budget: float = 120.0
    waste_cost_target: float = 15.0      # money a month written off as waste

    # Nutrition targets (per person, per day) -------------------------------
    calorie_target: int = 2000
    protein_target: int = 90
    carb_target: int = 230
    fat_target: int = 70
    fibre_target: int = 30
    sugar_limit: int = 50
    sodium_limit: int = 2300             # mg
    water_target: int = 8                # glasses a day

    # Reminder windows ------------------------------------------------------
    expiry_warning_days: int = 5         # "use it or lose it" window
    leftover_safe_days: int = 3          # fridge life of a cooked leftover
    freezer_review_days: int = 90        # how long before a freezer item is old
    low_stock_days: int = 7              # days of stock that counts as low
    prep_reminder_days: int = 2          # how early prep tasks are flagged
    rotation_gap_days: int = 14          # minimum days before repeating a meal
    shopping_day: str = "Saturday"
    prep_day: str = "Sunday"

    # Targets the habit tracker measures ------------------------------------
    home_cooked_target: int = 18         # home cooked meals a week
    new_recipe_target: int = 2           # new recipes a month
    takeaway_limit: int = 4              # takeaways a month
    packed_lunch_target: int = 5         # packed lunches a week
    waste_reduction_target: float = 0.05  # share of food bought that is binned

    # Behaviour -------------------------------------------------------------
    rounding: str = "Whole packs"
    top_rows: int = 5                    # size of the "top / best" tables
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    @property
    def year(self) -> int:
        return self.plan_year or self.today.year

    @property
    def metric(self) -> bool:
        return self.measurement_system.lower().startswith("m")

    def scale_rows(self, recipe_rows: int) -> None:
        """Scale every register in place so Recipes holds N rows."""
        base = DEFAULT_ROWS["Recipes"]
        factor = max(0.02, float(recipe_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        """Return a copy with every register scaled."""
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings derived from the chosen currency ------------------
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.00;[Red]-{s}#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0;[Red]-{s}#,##0'

    @property
    def start_date(self) -> date:
        """The Monday (or Sunday) the example plan starts from."""
        day = self.today
        offset = day.weekday() if self.week_start == "Monday" \
            else (day.weekday() + 1) % 7
        return date.fromordinal(day.toordinal() - offset)
````

### `meal_planner_spreadsheet/layout.py`

Layout engine *(306 lines)*

````python
"""
Layout engine.

The workbook is described declaratively: every register sheet (Recipes,
Recipe Ingredients, Meal Plan, Pantry, ...) is a :class:`SheetSpec` of :class:`Col`
objects.  Formulas
are written as templates that never contain hard coded column letters, so
columns can be reordered or inserted without breaking a single formula:

    "=IF({title}{r}=\"\",\"\",SUMIFS([[Performance.reach]],[[Performance.content]],{id}{r}))"

    {r}            -> the current Excel row number (1 based)
    {key}          -> column letter of the column `key` on the *same* sheet
    [[Sheet.key]]  -> absolute range of that column's data rows, e.g.
                      'Recipe Ingredients'!$K$5:$K$1204
    [[Sheet.key#r]]-> absolute single cell of that column on row r
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

# Row 1 title, row 2 strapline, row 3 navigation, row 4 headers, row 5+ data.
TITLE_ROW = 1
SUBTITLE_ROW = 2
NAV_ROW = 3
HEADER_ROW = 4
DATA_ROW = 5


# ---------------------------------------------------------------------------
# A1 helpers
# ---------------------------------------------------------------------------

def col_letter(index: int) -> str:
    """0 based column index -> Excel column letter."""
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = string.ascii_uppercase[rem] + letters
    return letters


def quote_sheet(name: str) -> str:
    """Quote a sheet name for use inside a formula when it needs it."""
    if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", name):
        return name
    return "'" + name.replace("'", "''") + "'"


def cell_ref(col: int, row: int, absolute: bool = True) -> str:
    dollar = "$" if absolute else ""
    return f"{dollar}{col_letter(col)}{dollar}{row}"


# ---------------------------------------------------------------------------
# Column / sheet specifications
# ---------------------------------------------------------------------------

@dataclass
class Col:
    """One column of a register sheet."""

    key: str
    header: str
    width: float = 14.0
    style: str = "text"              # key into the format book (see formats.py)
    formula: Optional[str] = None    # template -> locked, calculated column
    validate: Optional[Dict[str, Any]] = None
    note: Optional[str] = None       # help text shown when the cell is selected
    cf: List[Dict[str, Any]] = field(default_factory=list)
    hidden: bool = False
    group: str = ""                  # section label (documentation only)

    @property
    def is_formula(self) -> bool:
        return self.formula is not None


@dataclass
class SheetSpec:
    """A register sheet: title band, header row and N pre-built data rows."""

    name: str
    title: str
    subtitle: str = ""
    columns: List[Col] = field(default_factory=list)
    rows: int = 100
    header_row: int = HEADER_ROW        # 1 based Excel row of the header
    tab_color: Optional[str] = None
    freeze_cols: int = 2
    freeze_at: Optional[int] = None   # 1 based row to freeze below
    samples: List[Dict[str, Any]] = field(default_factory=list)
    help_text: str = ""
    extra_notes: List[str] = field(default_factory=list)

    # -------------------------------------------------------------- geometry
    @property
    def first_data_row(self) -> int:
        return self.header_row + 1

    @property
    def last_data_row(self) -> int:
        return self.header_row + self.rows

    def index(self, key: str) -> int:
        for i, col in enumerate(self.columns):
            if col.key == key:
                return i
        raise KeyError(f"{self.name}: unknown column '{key}'")

    def letter(self, key: str) -> str:
        return col_letter(self.index(key))

    def col(self, key: str) -> Col:
        return self.columns[self.index(key)]

    @property
    def last_col_index(self) -> int:
        return len(self.columns) - 1


class Registry:
    """Lookup table of every registered :class:`SheetSpec`."""

    def __init__(self) -> None:
        self._specs: Dict[str, SheetSpec] = {}
        #: When False, references to sheets that have not been declared yet
        #: return a placeholder instead of raising.  The builder uses this to
        #: declare every tab before it wires the formulas together.
        self.strict = True

    def add(self, spec: SheetSpec) -> SheetSpec:
        self._specs[spec.name] = spec
        return spec

    def __contains__(self, name: str) -> bool:
        return name in self._specs

    def __getitem__(self, name: str) -> SheetSpec:
        return self._specs[name]

    def names(self) -> Sequence[str]:
        return list(self._specs)

    # ------------------------------------------------------------ references
    def _placeholder(self, sheet: str, key: str) -> str:
        return f"{quote_sheet(sheet)}!$A$1:$A$2"

    def rng(self, sheet: str, key: str, first: Optional[int] = None,
            last: Optional[int] = None) -> str:
        if sheet not in self._specs:
            if self.strict:
                raise KeyError(sheet)
            return self._placeholder(sheet, key)
        spec = self._specs[sheet]
        letter = spec.letter(key)
        first = first or spec.first_data_row
        last = last or spec.last_data_row
        return f"{quote_sheet(sheet)}!${letter}${first}:${letter}${last}"

    def cell(self, sheet: str, key: str, row: int) -> str:
        if sheet not in self._specs:
            if self.strict:
                raise KeyError(sheet)
            return f"{quote_sheet(sheet)}!$A$1"
        spec = self._specs[sheet]
        return f"{quote_sheet(sheet)}!${spec.letter(key)}${row}"

    def letter(self, sheet: str, key: str) -> str:
        if sheet not in self._specs:
            if self.strict:
                raise KeyError(sheet)
            return "A"
        return self._specs[sheet].letter(key)

    # -------------------------------------------------------------- renderer
    _REF = re.compile(r"\[\[([^\].#]+)\.([A-Za-z0-9_]+)(?:#(\d*))?\]\]")

    def render(self, template: str, row: Optional[int] = None,
               spec: Optional[SheetSpec] = None) -> str:
        """Expand [[Sheet.key]] and {key}/{r} tokens into a real formula."""

        def _ref(match: "re.Match[str]") -> str:
            sheet, key, single = match.group(1), match.group(2), match.group(3)
            if single:
                return self.cell(sheet, key, int(single))
            if single == "":
                # [[Sheet.key#]] -> same row as the formula being written
                if row is None:
                    raise ValueError(
                        f"[[{sheet}.{key}#]] needs a row context")
                return self.cell(sheet, key, row)
            return self.rng(sheet, key)

        text = self._REF.sub(_ref, template)

        if spec is not None:
            mapping: Dict[str, Any] = {c.key: spec.letter(c.key)
                                       for c in spec.columns}
            # `{key_first}` / `{key_last}` give the absolute top and bottom
            # of a column on the same sheet, so an in-sheet COUNTIFS reads
            # `{key_first}:{key_last}` instead of a hand built $D$5:$D$104.
            for col in spec.columns:
                letter = spec.letter(col.key)
                mapping[f"{col.key}_first"] = (
                    f"${letter}${spec.first_data_row}")
                mapping[f"{col.key}_last"] = (
                    f"${letter}${spec.last_data_row}")
            if row is not None:
                mapping["r"] = row
                mapping["r_prev"] = row - 1
            mapping["first"] = spec.first_data_row
            mapping["last"] = spec.last_data_row
            text = text.format(**mapping)
        elif row is not None:
            text = text.format(r=row)
        return text


# ---------------------------------------------------------------------------
# Reusable formula fragments
# ---------------------------------------------------------------------------

def max_if(value_range: str, *conditions: str) -> str:
    """MAX of `value_range` where all conditions hold (no CSE required)."""
    cond = "*".join(f"({c})" for c in conditions)
    return f"SUMPRODUCT(MAX({cond}*{value_range}))"


def min_if(value_range: str, *conditions: str, sentinel: int = 2958465) -> str:
    """MIN of `value_range` where all conditions hold (no CSE required).

    Non matching rows are swapped for a sentinel (31-Dec-9999 as a serial) so
    that MIN ignores them.  Returns the sentinel when nothing matches, so the
    caller should wrap the result in an IF test.
    """
    cond = "*".join(f"({c})" for c in conditions)
    return (f"SUMPRODUCT(MIN({cond}*{value_range}"
            f"+(1-{cond})*{sentinel}))")


def blank_if(test: str, result: str) -> str:
    return f'IF({test},"",{result})'


def safe(expr: str, fallback: str = '""') -> str:
    return f"IFERROR({expr},{fallback})"


def lookup(value: str, table_range: str, index_range: str,
           fallback: str = '""') -> str:
    """INDEX/MATCH lookup (works left or right, unlike VLOOKUP)."""
    return f"IFERROR(INDEX({index_range},MATCH({value},{table_range},0)),{fallback})"


# ---------------------------------------------------------------------------
# Ranking without RANK.EQ
#
# COUNTIFS based ranking is Excel 2007 safe, ignores the blank/text rows the
# formula columns produce, and does not need the `_xlfn.` prefix that
# RANK.EQ requires when written straight into the file format.
# ---------------------------------------------------------------------------

def rank_desc(value: str, rng: str) -> str:
    """1 for the biggest number in `rng`."""
    return f'COUNTIFS({rng},">"&{value})+1'


def rank_asc(value: str, rng: str) -> str:
    """1 for the smallest number in `rng`."""
    return f'COUNTIFS({rng},"<"&{value})+1'


def unique_rank(value: str, rng: str, order: str = "asc") -> str:
    """A rank with no ties, so ``MATCH(n, rank_column, 0)`` always finds a
    row.  Blank and text rows in `rng` are ignored, and equal values are
    separated by their position in the sheet."""
    op = "<" if order == "asc" else ">"
    return (f'SUMPRODUCT(({rng}{op}{value})*1)'
            f'+SUMPRODUCT(({rng}={value})*(ROW({rng})<ROW()))+1')


def last_of(value_range: str, *conditions: str) -> str:
    """Newest (largest) matching value, blank when nothing matches."""
    cond = "*".join(f"({c})" for c in conditions)
    inner = f"SUMPRODUCT(MAX({cond}*{value_range}))"
    return f'IF({inner}=0,"",{inner})'


def dynamic_name(sheet: str, letter: str, first: int, last: int,
                 count_text: bool = True) -> str:
    """OFFSET based defined name that grows with the populated rows."""
    rng = f"{quote_sheet(sheet)}!${letter}${first}:${letter}${last}"
    counter = f'COUNTIF({rng},"?*")' if count_text else f"COUNTA({rng})"
    return (f"=OFFSET({quote_sheet(sheet)}!${letter}${first},0,0,"
            f"MAX(1,{counter}),1)")


def join_nonblank(parts: Sequence[str]) -> str:
    """Build `a & b & c` style concatenation."""
    return "&".join(parts)
````

### `meal_planner_spreadsheet/formats.py`

The format book *(286 lines)*

````python
"""
The format book.

One place builds every XlsxWriter format used by the workbook so the look
stays consistent: warm cream input cells, soft sage calculated cells, herb
green headers and a terracotta accent.  Sheets are protected with
``protect`` and the input cells are unlocked so the buyer can type in them
while every formula stays safe.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:                                     # normal package import
    from .config import Config, Palette
except ImportError:                      # pragma: no cover - script import
    from config import Config, Palette


class Formats:
    """Creates and caches every format the workbook needs."""

    def __init__(self, workbook, cfg: Config) -> None:
        self.wb = workbook
        self.cfg = cfg
        self.p = Palette
        self.cache: Dict[str, Any] = {}
        self._build()

    # ---------------------------------------------------------------- helpers
    def _add(self, name: str, props: Dict[str, Any]) -> Any:
        fmt = self.wb.add_format(props)
        self.cache[name] = fmt
        return fmt

    def money_fmt(self, decimals: int = 2) -> str:
        symbol = self.cfg.currency_symbol
        if decimals:
            return f"{symbol}#,##0.{'0' * decimals}"
        return f"{symbol}#,##0"

    def signed_money(self, decimals: int = 2) -> str:
        symbol = self.cfg.currency_symbol
        body = f"{symbol}#,##0.{'0' * decimals}"
        return f"{body};[Red]-{body}"

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        cfg, p = self.cfg, Palette
        locked = {"locked": True}
        unlocked = {"locked": False}

        self._add("title", {
            "font_name": "Calibri", "font_size": 16, "bold": True,
            "font_color": p.white, "bg_color": p.primary,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("subtitle", {
            "font_name": "Calibri", "font_size": 10, "italic": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("nav", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "center", "valign": "vcenter", **locked})
        self._add("nav_left", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})

        self._add("header", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.primary_mid, **locked})
        self._add("header_wide", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.primary_mid, **locked})

        # -- editable cells: cream, unlocked, thin border ---------------------
        self._add("input_text", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "indent": 1, **unlocked})
        self._add("input_text_wrap", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "top",
            "text_wrap": True, "indent": 1, **unlocked})
        self._add("input_number", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": "#,##0.##", "align": "center", **unlocked})
        self._add("input_money", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": self.signed_money(), "align": "right",
            **unlocked})
        self._add("input_date", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": cfg.date_format, "align": "center", **unlocked})
        self._add("input_percent", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": "0%", "align": "center", **unlocked})
        self._add("input_select", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "align": "center", **unlocked})
        self._add("input_dropdown", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "align": "center", "italic": True, **unlocked})
        self._add("input_lookup", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.info_text,
            "bg_color": p.info_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "indent": 1, **unlocked})
        self._add("input_plain", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.white, "valign": "top", "text_wrap": True,
            "indent": 1, **unlocked})

        # -- calculated cells: soft sage, locked -----------------------------
        base_calc = {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.calc_bg, "border": 1,
            "border_color": p.calc_border, "valign": "vcenter",
            "indent": 1, **locked}
        self._add("calc_text", dict(base_calc))
        self._add("calc_number", dict(base_calc,
                                      num_format="#,##0.##",
                                      align="center"))
        self._add("calc_money", dict(base_calc,
                                     num_format=self.signed_money(),
                                     align="right"))
        self._add("calc_money_0", dict(base_calc,
                                       num_format=self.signed_money(0),
                                       align="right"))
        self._add("calc_percent", dict(base_calc, num_format="0.0%",
                                       align="center"))
        self._add("calc_date", dict(base_calc, num_format=cfg.date_format,
                                    align="center"))
        self._add("calc_weekday", dict(base_calc, num_format="ddd",
                                       align="center"))
        self._add("calc_center", dict(base_calc, align="center"))
        self._add("calc_bold", dict(base_calc, bold=True, align="center"))
        self._add("calc_badge", dict(base_calc, align="center", bold=True,
                                     font_color=p.primary))
        self._add("calc_locked", dict(base_calc, text_wrap=True,
                                      valign="top"))
        self._add("calc_spark", dict(base_calc, align="center",
                                     num_format="#,##0.##",
                                     font_color=p.primary))
        self._add("calc_flag", dict(base_calc, align="center", bold=True))

        # -- totals, bands, notes -------------------------------------------
        self._add("total_label", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "left", "valign": "vcenter", "indent": 1,
            "border": 1, "border_color": p.line, **locked})
        self._add("total_number", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "center", "valign": "vcenter",
            "num_format": "#,##0.##", "border": 1,
            "border_color": p.line, **locked})
        self._add("total_money", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "right", "valign": "vcenter",
            "num_format": self.signed_money(), "border": 1,
            "border_color": p.line, **locked})
        self._add("total_percent", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "center", "valign": "vcenter", "num_format": "0.0%",
            "border": 1, "border_color": p.line, **locked})
        self._add("section", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("note", {
            "font_name": "Calibri", "font_size": 9, "italic": True,
            "font_color": p.grey_text, "bg_color": p.note_bg,
            "valign": "top", "text_wrap": True, "indent": 1, **locked})
        self._add("label", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.ink, "bg_color": p.white,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("label_soft", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.primary_soft, "align": "left",
            "valign": "vcenter", "indent": 1, **locked})

        # -- KPI tiles (used by the dashboards) -----------------------------
        self._add("kpi_label", {
            "font_name": "Calibri", "font_size": 9, "bold": True,
            "font_color": p.primary_mid, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.line, **locked})
        self._add("kpi_value", {
            "font_name": "Calibri", "font_size": 20, "bold": True,
            "font_color": p.primary, "bg_color": p.white,
            "align": "center", "valign": "vcenter",
            "num_format": "#,##0.##", "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_value_money", {
            "font_name": "Calibri", "font_size": 20, "bold": True,
            "font_color": p.accent, "bg_color": p.white,
            "align": "center", "valign": "vcenter",
            "num_format": self.money_fmt(), "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_value_text", {
            "font_name": "Calibri", "font_size": 14, "bold": True,
            "font_color": p.primary, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_sub", {
            "font_name": "Calibri", "font_size": 8, "italic": True,
            "font_color": p.grey_text, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.line, **locked})

        # -- status pills ---------------------------------------------------
        for name, (bg, fg) in {
                "good": (p.good_bg, p.good_text),
                "warn": (p.warn_bg, p.warn_text),
                "bad": (p.bad_bg, p.bad_text),
                "info": (p.info_bg, p.info_text)}.items():
            self._add(f"status_{name}", {
                "font_name": "Calibri", "font_size": 10, "bold": True,
                "font_color": fg, "bg_color": bg, "align": "center",
                "valign": "vcenter", "border": 1,
                "border_color": p.line, **locked})

        # -- generic text ---------------------------------------------------
        self._add("plain", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "valign": "vcenter", **locked})
        self._add("plain_bold", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.ink, "valign": "vcenter", **locked})
        self._add("plain_wrap", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "valign": "top", "text_wrap": True, **locked})
        self._add("link", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.accent,
            "underline": 1, "valign": "vcenter", **locked})
        self._add("check", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "align": "center",
            "valign": "vcenter", **unlocked})
        self._add("check_done", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.good_text,
            "bg_color": p.good_bg, "border": 1,
            "border_color": p.line, "align": "center", "valign": "vcenter",
            **locked})

    # ------------------------------------------------------------- accessors
    def __getitem__(self, name: str) -> Any:
        return self.cache[name]

    def get(self, name: str, default: Optional[str] = None) -> Any:
        if name in self.cache:
            return self.cache[name]
        if default is not None:
            return self.cache[default]
        raise KeyError(name)
````

### `meal_planner_spreadsheet/writer.py`

The writer *(397 lines)*

````python
"""
The writer.

Turns every :class:`~meal_planner_spreadsheet.layout.SheetSpec` into real
Excel rows: the coloured title band, the frozen header row, one pre-built row
per register slot with its validation, conditional format and formula, plus
the sheet protection that locks the calculated columns and leaves the cream
input cells editable.

Nothing here hard codes a column letter - the layout engine renders every
formula template against the registry, so columns can be added, removed or
reordered in the sheet modules without touching the writer.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, Iterable, List, Optional, Sequence

dt_date = _dt.date
dt_datetime = _dt.datetime

try:
    from .config import Config, Palette
    from .layout import (DATA_ROW, HEADER_ROW, NAV_ROW, SUBTITLE_ROW,
                         TITLE_ROW, Col, Registry, SheetSpec, col_letter)
except ImportError:                       # pragma: no cover
    from config import Config, Palette
    from layout import (DATA_ROW, HEADER_ROW, NAV_ROW, SUBTITLE_ROW,
                        TITLE_ROW, Col, Registry, SheetSpec, col_letter)


#: style key -> format name.  `text` deliberately falls back to the calc
#: version when the column is a formula column, so a column can be declared
#: as a plain text column and still be written as a locked formula.
INPUT_STYLES = {
    "text": "input_text",
    "text_wrap": "input_text_wrap",
    "number": "input_number",
    "money": "input_money",
    "date": "input_date",
    "percent": "input_percent",
    "select": "input_select",
    "dropdown": "input_dropdown",
    "lookup": "input_lookup",
    "plain": "input_plain",
    "check": "check",
    "weekday": "input_select",
    "money0": "input_money",
    "percent0": "input_percent",
}

CALC_STYLES = {
    "text": "calc_text",
    "text_wrap": "calc_locked",
    "number": "calc_number",
    "money": "calc_money",
    "money0": "calc_money_0",
    "date": "calc_date",
    "percent": "calc_percent",
    "percent0": "calc_number",
    "select": "calc_center",
    "dropdown": "calc_center",
    "lookup": "calc_text",
    "plain": "plain",
    "check": "calc_center",
    "weekday": "calc_weekday",
    "badge": "calc_badge",
    "flag": "calc_flag",
}


class Writer:
    """Writes sheets into an XlsxWriter workbook."""

    def __init__(self, workbook, cfg: Config, registry: Registry,
                 formats) -> None:
        self.wb = workbook
        self.cfg = cfg
        self.registry = registry
        self.fmt = formats
        self.nav_links: Dict[str, str] = {}
        #: {sheet name: {row offset: {column key: value}}} - example data.
        self.samples: Dict[str, Dict[int, Dict[str, Any]]] = {}

    # ------------------------------------------------------------- primitives
    def sheet(self, name: str):
        ws = self.wb.add_worksheet(name)
        if self.cfg.protect_sheets:
            # Empty options so every cell defaults to locked; input cells
            # are unlocked by their format's `locked: False`.
            options = {"select_locked_cells": False,
                       "select_unlocked_cells": False}
            ws.protect(self.cfg.password or "", options)
        return ws

    def style_for(self, col: Col) -> Any:
        book = CALC_STYLES if col.is_formula else INPUT_STYLES
        return self.fmt.get(book.get(col.style, "text"), "calc_text")

    # ------------------------------------------------------------- chrome
    def chrome(self, ws, spec: SheetSpec, links: Sequence[str] = ()) -> None:
        """Title band, strapline and navigation strip."""
        p = Palette
        last = spec.last_col_index
        cfg = self.cfg

        ws.set_row(TITLE_ROW - 1, 30)
        ws.set_row(SUBTITLE_ROW - 1, 18)
        ws.set_row(NAV_ROW - 1, 20)
        ws.merge_range(TITLE_ROW - 1, 0, TITLE_ROW - 1, last,
                       spec.title.upper(), self.fmt["title"])
        ws.merge_range(SUBTITLE_ROW - 1, 0, SUBTITLE_ROW - 1, last,
                       spec.subtitle or spec.help_text or cfg.product_subtitle,
                       self.fmt["subtitle"])

        # navigation strip
        ws.merge_range(NAV_ROW - 1, 0, NAV_ROW - 1, last,
                       "  |  ".join(links) if links else
                       f"{cfg.product_name}  |  v{cfg.version}",
                       self.fmt["nav"])

    def headers(self, ws, spec: SheetSpec) -> None:
        hrow = spec.header_row - 1
        ws.set_row(hrow, 32)
        for i, col in enumerate(spec.columns):
            ws.write(hrow, i, col.header, self.fmt["header"])
            if col.note:
                ws.write_comment(hrow, i, col.note,
                                 {"width": 260, "height": 90})
        ws.autofilter(spec.header_row - 1, 0, spec.last_data_row - 1,
                      spec.last_col_index)

    # ------------------------------------------------------------- data rows
    def register(self, ws, spec: SheetSpec,
                 sample_index: Optional[Dict[int, Dict[str, Any]]] = None,
                 ) -> None:
        """Write the header row and every pre-built data row."""
        self.headers(ws, spec)

        if sample_index is None:
            sample_index = self.samples.get(spec.name, {})
        samples = sample_index or {}
        for offset in range(spec.rows):
            row = spec.first_data_row + offset          # 1 based Excel row
            xrow = row - 1
            for col in spec.columns:
                style = self.style_for(col)
                if col.formula:
                    formula = self.registry.render(col.formula, row=row,
                                                   spec=spec)
                    if self._always_blank(formula):
                        # A whole-row guard keeps the sheet tidy and cheap.
                        guard = self._blank_guard(spec, row)
                        if guard:
                            formula = f'=IF({guard},"",{formula[1:]})'
                        else:
                            formula = formula
                    try:
                        ws.write_formula(xrow, spec.index(col.key), formula,
                                         style)
                    except Exception:                      # pragma: no cover
                        ws.write_formula(xrow, spec.index(col.key), "=0",
                                         style)
                    continue

                value = self._sample(samples, offset, col, row)
                if value is None:
                    ws.write_blank(xrow, spec.index(col.key), None, style)
                elif isinstance(value, str) and value.startswith("="):
                    ws.write_formula(xrow, spec.index(col.key), value, style)
                elif isinstance(value, (dt_date, dt_datetime)):
                    ws.write_datetime(xrow, spec.index(col.key), value, style)
                elif col.style in ("number", "money", "money0", "percent",
                                   "percent0", "check"):
                    try:
                        ws.write_number(xrow, spec.index(col.key),
                                        float(value), style)
                    except (TypeError, ValueError):
                        ws.write_blank(xrow, spec.index(col.key), None, style)
                else:
                    ws.write_string(xrow, spec.index(col.key), str(value),
                                    style)

            self._apply_col_extras(ws, spec, xrow)

    # ---------------------------------------------------------------- helpers
    def _sample(self, samples: Dict[int, Dict[str, Any]], offset: int,
                col: Col, row: int) -> Any:
        record = samples.get(offset)
        if not record:
            return None
        value = record.get(col.key)
        if callable(value):
            return value(row)
        return value

    @staticmethod
    def _always_blank(formula: str) -> bool:
        """True when the formula only ever returns blank."""
        body = formula[1:] if formula.startswith("=") else formula
        return body.strip() in ('""', 'IFERROR("","")')

    def _blank_guard(self, spec: SheetSpec, row: int) -> Optional[str]:
        """Return a test that is TRUE while the row is still unused."""
        for key in ("title", "name", "label", "item", "recipe", "date",
                    "meal", "slot", "task", "description"):
            try:
                letter = spec.letter(key)
            except KeyError:
                continue
            return f"${letter}{row}=\"\""
        return None

    def _apply_col_extras(self, ws, spec: SheetSpec, xrow: int) -> None:
        """Validation + conditional formats for one physical row."""
        for col in spec.columns:
            i = spec.index(col.key)
            letter = spec.letter(col.key)
            if col.validate and not col.is_formula:
                self._validation(ws, spec, col, letter, i)
            if col.cf:
                self._conditional(ws, spec, col, letter, i)

    def _validation(self, ws, spec: SheetSpec, col: Col, letter: str,
                    i: int) -> None:
        raw = dict(col.validate)
        kind = raw.pop("type", "list")
        opts: Dict[str, Any] = {"validate": kind}

        if kind == "list":
            source = raw.pop("source", None)
            if isinstance(source, str) and source.startswith("="):
                opts["source"] = source
            elif isinstance(source, (list, tuple)):
                opts["source"] = [str(s) for s in source]
            opts.setdefault("error_type", "stop")
            opts.setdefault("error_title", "Pick from the list")
            opts.setdefault("error_message",
                            col.note or f"Choose a value from the "
                            f"{col.header} list.")
        elif kind in ("integer", "decimal", "date", "time", "length"):
            # our shorthand is {"between": lo, "and": hi}; XlsxWriter calls
            # the same thing criteria/minimum/maximum
            low = raw.pop("between", None)
            high = raw.pop("and", None)
            operator = raw.pop("operator", "between" if low is not None
                               else None)
            if operator:
                opts["criteria"] = operator
            if low is not None:
                opts["minimum"] = low
            if high is not None:
                opts["maximum"] = high
            for key in ("minimum", "maximum"):
                if key in raw:
                    opts[key] = raw.pop(key)
            opts.setdefault("error_type", "warning")
            opts.setdefault("error_title", "Check this entry")
            opts.setdefault("error_message",
                            col.note or f"Enter a {kind} in this cell.")
        else:
            opts.update(raw)

        if col.note:
            opts.setdefault("input_title", col.header)
            opts.setdefault("input_message", col.note)
        opts.setdefault("show_error", True)
        opts.setdefault("show_input", True)
        ws.data_validation(spec.first_data_row - 1, i,
                           spec.last_data_row - 1, i, opts)

    def _conditional(self, ws, spec: SheetSpec, col: Col, letter: str,
                     i: int) -> None:
        for rule in col.cf:
            rule = dict(rule)
            fmt = rule.pop("format", None)
            if fmt is not None and isinstance(fmt, str):
                rule["format"] = self.fmt[fmt]
            rng = rule.pop("range", None)
            if rng:
                first = spec.first_data_row - 1
                last = spec.last_data_row - 1
                rng = self.registry.render(rng, row=None, spec=spec)
                rule_range = rng
            else:
                rule_range = (f"${letter}${spec.first_data_row}:"
                              f"${letter}${spec.last_data_row}")
            ws.conditional_format(rule_range, rule)

    # ------------------------------------------------------------- decoration
    def banding(self, ws, spec: SheetSpec, start_row: int,
                end_row: int, first_col: int, last_col: int,
                colour: str = "primary_soft") -> None:
        """Alternating row shading (applied on top of the cell formats)."""
        if end_row <= start_row:
            return
        bg = Palette.__dict__.get(colour, colour)
        fmt = self.wb.add_format({"bg_color": bg, "border": 1,
                                  "border_color": Palette.calc_border})
        for row in range(start_row, end_row + 1, 2):
            ws.conditional_format(row - 1, first_col, row - 1, last_col,
                                  {"type": "formula",
                                   "criteria": f"=MOD(ROW(),2)=0",
                                   "format": fmt})

    def sparkline(self, ws, row: int, col: int, data_range: str,
                  spark: str = "line", colour: str = None) -> None:
        opts: Dict[str, Any] = {
            "location": [row, col],
            "range": data_range,
            "type": spark,
            "markers": True,
            "high_point": True,
            "low_point": True,
            "empty_cells": "zero",
        }
        if colour:
            opts["series_color"] = colour
        try:
            ws.add_sparkline(row, col, data_range, opts)
        except Exception:                              # pragma: no cover
            pass

    def grid_off(self, ws) -> None:
        ws.hide_gridlines(2)

    def setup_print(self, ws, spec: SheetSpec, landscape: bool = True,
                    fit_width: int = 1, repeat_rows: bool = True,
                    repeat_cols: int = 0) -> None:
        ws.set_landscape()
        ws.set_paper(9)                     # A4
        ws.fit_to_pages(fit_width, 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        ws.center_horizontally()
        ws.set_header(f"&L&\"Calibri,Bold\"{self.cfg.product_name}"
                      f"&R&\"Calibri,Italic\"{spec.name}")
        ws.set_footer("&LPage &P of &N&R&D")
        if repeat_rows:
            ws.repeat_rows(0, spec.header_row - 1)
        if repeat_cols:
            ws.repeat_columns(0, repeat_cols - 1)
        ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)

    def freeze(self, ws, spec: SheetSpec) -> None:
        row = spec.freeze_at or spec.header_row
        ws.freeze_panes(row, spec.freeze_cols)

    def widths(self, ws, spec: SheetSpec) -> None:
        for i, col in enumerate(spec.columns):
            ws.set_column(i, i, col.width, None,
                          {"hidden": 1} if col.hidden else None)

    def finish_sheet(self, ws, spec: SheetSpec, links: Sequence[str] = (),
                     landscape: bool = True, banding: bool = True,
                     freeze: bool = True, print_area: bool = True) -> None:
        self.grid_off(ws)
        self.widths(ws, spec)
        if banding:
            self.banding(ws, spec, spec.first_data_row,
                         spec.last_data_row, 0, spec.last_col_index)
        if freeze:
            self.freeze(ws, spec)
        if print_area:
            self.setup_print(ws, spec, landscape=landscape)
        if spec.tab_color:
            ws.set_tab_color(spec.tab_color)
        else:
            ws.set_tab_color(Palette.primary_mid)
        for link in links:
            self.nav_links.setdefault(link, link)

    # ------------------------------------------------------------- shared UI
    def write_kpi(self, ws, row: int, col: int, label: str,
                  value_formula: str, sub: str = "",
                  style: str = "kpi_value", width: int = 3) -> None:
        """A three row KPI tile: label, value, optional sub label."""
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, label, self.fmt["kpi_label"])
        ws.merge_range(row + 1, col, row + 1, end, None,
                       self.fmt[style])
        ws.write_formula(row + 1, col, value_formula, self.fmt[style])
        if sub:
            ws.merge_range(row + 2, col, row + 2, end, sub,
                           self.fmt["kpi_sub"])
        ws.set_row(row + 1, 30)

    def write_panel(self, ws, row: int, col: int, title: str, width: int = 6,
                    height: int = 22) -> None:
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, title, self.fmt["section"])
        ws.set_row(row, height)

    def write_note(self, ws, row: int, col: int, text: str,
                   width: int = 6) -> None:
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, text, self.fmt["note"])
````

### `meal_planner_spreadsheet/names.py`

Defined names *(144 lines)*

````python
"""
Defined names.

Named cells and dynamic ranges make the workbook self documenting and keep
the formulas readable: ``=Plan_Week`` instead of ``=Dashboard!$C$6``.  They
also give the buyer a stable place to point their own formulas at.

Every entry is resolved through the registry, so a name is only installed
when the sheet and the column really exist.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

try:
    from .config import Config
    from .layout import Registry, SheetSpec
except ImportError:                       # pragma: no cover
    from config import Config
    from layout import Registry, SheetSpec

#: (name, sheet, column key, row) for single cells.
STATIC_NAMES: List[Tuple[str, str, str, int]] = [
    # ---- household & planning ------------------------------------------
    ("Household_Name", "Settings", "value", 6),
    ("Household_Size", "Settings", "value", 7),
    ("Plan_Cook", "Settings", "value", 8),
    ("Plan_Year", "Settings", "value", 9),
    ("Default_Servings", "Settings", "value", 10),
    ("Week_Start_Day", "Settings", "value", 11),
    ("Measurement_System", "Settings", "value", 12),
    ("Currency_Symbol", "Settings", "value", 13),
    ("Currency_Code", "Settings", "value", 14),
    ("Shopping_Day", "Settings", "value", 15),
    ("Prep_Day", "Settings", "value", 16),
    # ---- budget ---------------------------------------------------------
    ("Weekly_Budget", "Settings", "value", 19),
    ("Monthly_Budget", "Settings", "value", 20),
    ("Annual_Budget", "Settings", "value", 21),
    ("Eating_Out_Budget", "Settings", "value", 22),
    ("Waste_Cost_Target", "Settings", "value", 23),
    # ---- nutrition targets ----------------------------------------------
    ("Calorie_Target", "Settings", "value", 26),
    ("Protein_Target", "Settings", "value", 27),
    ("Carb_Target", "Settings", "value", 28),
    ("Fat_Target", "Settings", "value", 29),
    ("Fibre_Target", "Settings", "value", 30),
    ("Sugar_Limit", "Settings", "value", 31),
    ("Sodium_Limit", "Settings", "value", 32),
    ("Water_Target", "Settings", "value", 33),
    # ---- windows and reminders ------------------------------------------
    ("Expiry_Warning_Days", "Settings", "value", 36),
    ("Leftover_Safe_Days", "Settings", "value", 37),
    ("Freezer_Review_Days", "Settings", "value", 38),
    ("Low_Stock_Days", "Settings", "value", 39),
    ("Prep_Reminder_Days", "Settings", "value", 40),
    ("Rotation_Gap_Days", "Settings", "value", 41),
    # ---- habit targets ---------------------------------------------------
    ("Home_Cooked_Target", "Settings", "value", 44),
    ("New_Recipe_Target", "Settings", "value", 45),
    ("Takeaway_Limit", "Settings", "value", 46),
    ("Packed_Lunch_Target", "Settings", "value", 47),
    ("Waste_Reduction_Target", "Settings", "value", 48),
    ("Top_Rows", "Settings", "value", 49),
    # ---- dashboard pickers ------------------------------------------------
    ("Plan_Week", "Dashboard", "week_start", 6),
    ("Plan_Month", "Dashboard", "month_name", 6),
    # ---- reporting period --------------------------------------------------
    ("Rep_From", "Reports", "value", 6),
    ("Rep_To", "Reports", "value", 7),
    # ---- print pickers ------------------------------------------------------
    ("Print_Week_Start", "Print Week", "value", 3),
    ("Print_List_Store", "Print Shopping", "value", 3),
    ("Print_Recipe_Title", "Print Recipe", "value", 3),
]

#: (name, sheet, column key) - a range that grows with the populated rows.
DYNAMIC_NAMES: List[Tuple[str, str, str]] = [
    ("Meal_Slots", "Lists", "meal_slot"),
    ("Unit_List", "Lists", "unit"),
    ("Category_List", "Lists", "category"),
    ("Cuisine_List", "Lists", "cuisine"),
    ("Tag_List", "Lists", "tag"),
    ("Store_List", "Lists", "store"),
    ("Diet_List", "Lists", "diet"),
    ("Status_List", "Lists", "status"),
    ("Recipe_Category_List", "Lists", "recipe_category"),
    ("Ingredient_Names", "Ingredients", "ingredient"),
    ("Recipe_Titles", "Recipes", "recipe"),
    ("Pantry_Items", "Pantry", "item"),
    ("Grocery_Items", "Grocery List", "item"),
    ("Leftover_Items", "Leftovers", "item"),
]


def _quote(sheet: str) -> str:
    return "'" + sheet.replace("'", "''") + "'"


def install(workbook, registry: Registry, cfg: Config) -> List[str]:
    """Create every defined name; return the names that were installed."""
    installed: List[str] = []

    for name, sheet, key, row in STATIC_NAMES:
        if sheet not in registry:
            continue
        try:
            ref = registry.cell(sheet, key, row)
        except KeyError:
            continue
        workbook.define_name(name, "=" + ref)
        installed.append(name)

    for name, sheet, key in DYNAMIC_NAMES:
        if sheet not in registry:
            continue
        try:
            spec = registry[sheet]
            letter = spec.letter(key)
        except KeyError:
            continue
        first, last = spec.first_data_row, spec.last_data_row
        quoted = _quote(sheet)
        counter = (f'COUNTIF({quoted}!${letter}${first}:${letter}${last},'
                   f'"?*")')
        ref = (f"=OFFSET({quoted}!${letter}${first},0,0,"
               f"MAX(1,{counter}),1)")
        workbook.define_name(name, ref)
        installed.append(name)

    return installed


def installed_map(registry: Registry) -> Dict[str, str]:
    """name -> absolute reference, for the documentation tools."""
    out: Dict[str, str] = {}
    for name, sheet, key, row in STATIC_NAMES:
        if sheet in registry:
            try:
                out[name] = registry.cell(sheet, key, row)
            except KeyError:
                continue
    return out
````

### `meal_planner_spreadsheet/build.py`

Workbook assembly *(235 lines)*

````python
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
````

### `meal_planner_spreadsheet/sample_data.py`

Example data *(1066 lines)*

````python
"""
Example data.

The workbook ships with a filled copy and a blank copy.  Everything in this
module is written into the filled copy only - it is a realistic three weeks
of meals for a family of four, with the recipes, ingredients, prices, pantry
stock, spending and waste that go with it.

Ingredient names are spelled identically here and on every tab, because the
cost and nutrition lookups match on the name.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

try:
    from .config import Config
except ImportError:                        # pragma: no cover
    from config import Config

# ---------------------------------------------------------------------------
# Ingredients: name, category, unit, price, pack, kcal, protein, carbs, fat,
#              fibre, shelf life, storage, staple, allergens
# ---------------------------------------------------------------------------
INGREDIENTS: List[tuple] = [
    ("Chicken breast", "Meat & Fish", "g", 0.0099, 500, 165, 31, 0, 3.6, 0,
     2, "Fridge", "Yes", ""),
    ("Chicken thigh", "Meat & Fish", "g", 0.0079, 1000, 209, 26, 0, 10.9, 0,
     2, "Fridge", "No", ""),
    ("Beef mince", "Meat & Fish", "g", 0.0119, 500, 250, 26, 0, 15, 0,
     2, "Fridge", "Yes", ""),
    ("Beef stewing steak", "Meat & Fish", "g", 0.0149, 700, 250, 26, 0, 15,
     0, 2, "Fridge", "No", ""),
    ("Pork sausage", "Meat & Fish", "g", 0.0069, 400, 290, 12, 3, 25, 0,
     3, "Fridge", "No", ""),
    ("Bacon", "Meat & Fish", "g", 0.0129, 250, 541, 37, 1.4, 42, 0,
     7, "Fridge", "No", ""),
    ("Salmon fillet", "Meat & Fish", "g", 0.0299, 240, 208, 20, 0, 13, 0,
     1, "Fridge", "No", "fish"),
    ("Cod fillet", "Meat & Fish", "g", 0.0199, 300, 82, 18, 0, 0.7, 0,
     1, "Fridge", "No", "fish"),
    ("Prawns", "Meat & Fish", "g", 0.0199, 200, 99, 24, 0, 0.3, 0,
     1, "Fridge", "No", "shellfish"),
    ("Eggs", "Dairy & Eggs", "piece", 0.42, 6, 78, 6.3, 0.6, 5.3, 0,
     21, "Fridge", "Yes", "egg"),
    ("Milk", "Dairy & Eggs", "ml", 0.0013, 2000, 42, 3.4, 5, 1, 0,
     5, "Fridge", "Yes", "dairy"),
    ("Cheddar cheese", "Dairy & Eggs", "g", 0.0119, 350, 403, 25, 1.3, 33,
     0, 21, "Fridge", "Yes", "dairy"),
    ("Butter", "Dairy & Eggs", "g", 0.0099, 250, 717, 0.9, 0.1, 81, 0,
     60, "Fridge", "Yes", "dairy"),
    ("Greek yoghurt", "Dairy & Eggs", "g", 0.0049, 500, 97, 9, 3.6, 5, 0,
     7, "Fridge", "Yes", "dairy"),
    ("Cream cheese", "Dairy & Eggs", "g", 0.0079, 300, 342, 6, 4, 34, 0,
     14, "Fridge", "No", "dairy"),
    ("Rice", "Grains & Pasta", "g", 0.0021, 1000, 360, 6.7, 79, 0.6, 1.3,
     365, "Pantry", "Yes", ""),
    ("Pasta", "Grains & Pasta", "g", 0.0019, 500, 371, 13, 75, 1.5, 3,
     365, "Pantry", "Yes", "gluten"),
    ("Spaghetti", "Grains & Pasta", "g", 0.0021, 500, 371, 13, 75, 1.5, 3,
     365, "Pantry", "Yes", "gluten"),
    ("Bread", "Bakery", "slice", 0.09, 20, 265, 9, 49, 3.2, 2.7,
     4, "Cupboard", "Yes", "gluten"),
    ("Bread rolls", "Bakery", "piece", 0.35, 6, 289, 9.5, 53, 3.5, 3,
     3, "Cupboard", "No", "gluten"),
    ("Flour", "Baking", "g", 0.0011, 1500, 364, 10, 76, 1, 2.7,
     365, "Pantry", "Yes", "gluten"),
    ("Sugar", "Baking", "g", 0.0012, 1000, 387, 0, 100, 0, 0,
     365, "Pantry", "Yes", ""),
    ("Baking powder", "Baking", "tsp", 0.02, 100, 2, 0, 1, 0, 0,
     365, "Pantry", "No", ""),
    ("Olive oil", "Condiments", "tbsp", 0.11, 500, 119, 0, 0, 13.5, 0,
     365, "Cupboard", "Yes", ""),
    ("Vegetable oil", "Condiments", "tbsp", 0.05, 500, 120, 0, 0, 13.6, 0,
     365, "Cupboard", "Yes", ""),
    ("Soy sauce", "Condiments", "tbsp", 0.06, 250, 8, 1.3, 0.8, 0, 0.1,
     180, "Cupboard", "No", "soy"),
    ("Tinned tomatoes", "Tins & Jars", "can", 0.55, 400, 32, 1.6, 5, 0.3,
     1.5, 365, "Pantry", "Yes", ""),
    ("Tomato puree", "Tins & Jars", "tbsp", 0.05, 200, 32, 1.6, 5, 0.3, 1.5,
     60, "Cupboard", "No", ""),
    ("Coconut milk", "Tins & Jars", "can", 1.05, 400, 230, 2.3, 3, 24, 2.2,
     365, "Pantry", "No", ""),
    ("Tinned sweetcorn", "Tins & Jars", "can", 0.49, 340, 96, 3.2, 21, 1.5,
     2, 365, "Pantry", "No", ""),
    ("Tinned chickpeas", "Tins & Jars", "can", 0.59, 400, 139, 7, 23, 2.6,
     6, 365, "Pantry", "No", ""),
    ("Tinned kidney beans", "Tins & Jars", "can", 0.55, 400, 127, 8.7, 20,
     0.5, 6.5, 365, "Pantry", "No", ""),
    ("Onion", "Vegetables", "piece", 0.28, 3, 44, 1.2, 9, 0.1, 1.7,
     30, "Pantry", "Yes", ""),
    ("Garlic", "Vegetables", "clove", 0.09, 6, 4, 0.2, 1, 0, 0.1,
     21, "Pantry", "Yes", ""),
    ("Carrot", "Vegetables", "piece", 0.12, 6, 41, 0.9, 10, 0.2, 2.8,
     21, "Fridge", "Yes", ""),
    ("Celery", "Vegetables", "stalk", 0.22, 4, 16, 0.7, 3, 0.2, 1.6,
     14, "Fridge", "No", ""),
    ("Bell pepper", "Vegetables", "piece", 0.65, 3, 31, 1, 6, 0.3, 2.1,
     10, "Fridge", "No", ""),
    ("Broccoli", "Vegetables", "piece", 0.79, 1, 55, 3.7, 10, 0.6, 3.3,
     7, "Fridge", "No", ""),
    ("Courgette", "Vegetables", "piece", 0.55, 2, 33, 2.4, 3.1, 0.6, 1.7,
     7, "Fridge", "No", ""),
    ("Spinach", "Vegetables", "g", 0.0069, 200, 23, 2.9, 3.6, 0.4, 2.2,
     5, "Fridge", "No", ""),
    ("Mushrooms", "Vegetables", "g", 0.0059, 250, 22, 3.1, 3.3, 0.3, 1,
     5, "Fridge", "No", ""),
    ("Sweet potato", "Vegetables", "piece", 0.62, 2, 90, 2, 20, 0.2, 3.3,
     21, "Pantry", "No", ""),
    ("Potato", "Vegetables", "g", 0.0014, 2500, 77, 2, 17, 0.1, 2.2,
     30, "Pantry", "Yes", ""),
    ("Cherry tomatoes", "Vegetables", "g", 0.0099, 300, 18, 0.9, 3.9, 0.2,
     1.2, 7, "Fridge", "No", ""),
    ("Cucumber", "Vegetables", "piece", 0.69, 1, 16, 0.7, 3.6, 0.1, 0.5,
     7, "Fridge", "No", ""),
    ("Lettuce", "Vegetables", "piece", 0.99, 1, 15, 1.4, 2.9, 0.2, 1.3,
     5, "Fridge", "No", ""),
    ("Lemon", "Fruit", "piece", 0.45, 3, 29, 1.1, 9, 0.3, 2.8,
     14, "Fridge", "No", ""),
    ("Banana", "Fruit", "piece", 0.19, 5, 89, 1.1, 23, 0.3, 2.6,
     5, "Cupboard", "Yes", ""),
    ("Apple", "Fruit", "piece", 0.35, 4, 52, 0.3, 14, 0.2, 2.4,
     30, "Fridge", "Yes", ""),
    ("Frozen berries", "Frozen", "g", 0.0059, 500, 50, 0.8, 12, 0.3, 3.5,
     180, "Freezer", "No", ""),
    ("Frozen peas", "Frozen", "g", 0.0029, 900, 81, 5.4, 14, 0.4, 5.5,
     180, "Freezer", "Yes", ""),
    ("Oats", "Grains & Pasta", "g", 0.0019, 1000, 389, 16.9, 66, 6.9, 10.6,
     365, "Pantry", "Yes", ""),
    ("Peanut butter", "Condiments", "tbsp", 0.13, 340, 188, 8, 6, 16, 1.8,
     180, "Cupboard", "No", "peanuts"),
    ("Honey", "Condiments", "tbsp", 0.12, 340, 64, 0.1, 17, 0, 0,
     365, "Cupboard", "No", ""),
    ("Stock cube", "Condiments", "cube", 0.08, 12, 3, 0.2, 0.5, 0.1, 0,
     365, "Pantry", "Yes", ""),
    ("Curry paste", "Condiments", "tbsp", 0.16, 200, 45, 1, 4, 3, 0.8,
     90, "Cupboard", "No", ""),
    ("Chilli flakes", "Herbs & Spices", "tsp", 0.04, 40, 6, 0.2, 1, 0.3,
     1.1, 365, "Pantry", "No", ""),
    ("Cumin", "Herbs & Spices", "tsp", 0.04, 40, 8, 0.4, 0.9, 0.5, 0.6,
     365, "Pantry", "No", ""),
    ("Basil", "Herbs & Spices", "tsp", 0.05, 20, 2, 0.3, 0.4, 0.1, 0.4,
     60, "Cupboard", "No", ""),
    ("Coriander", "Herbs & Spices", "sprig", 0.15, 10, 2, 0.2, 0.4, 0.1,
     0.3, 5, "Fridge", "No", ""),
    ("Kitchen roll", "Household", "roll", 2.49, 2, 0, 0, 0, 0, 0,
     0, "Cupboard", "Yes", ""),
    ("Washing up liquid", "Household", "bottle", 1.79, 1, 0, 0, 0, 0, 0,
     0, "Cupboard", "Yes", ""),
]

# ---------------------------------------------------------------------------
# Recipes: name, category, cuisine, servings, prep, cook, kcal, protein,
#          carbs, fat, fibre, sugar, sodium, flags, season, rating, source
# ---------------------------------------------------------------------------
def _r(name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
       sod, flags, season, rating, source):
    return (name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
            sod, flags, season, rating, source)


RECIPES: List[tuple] = [
    _r("Porridge with banana", "Breakfast", "British", 4, 5, 8, 320, 11, 54,
       6, 7, 18, 90, "VGFD", "Any", 4, "Everyday"),
    _r("Scrambled eggs on toast", "Breakfast", "British", 4, 5, 6, 410, 20,
       34, 21, 2, 5, 520, "VGFD", "Any", 4, "Everyday"),
    _r("Overnight oats", "Breakfast", "Any", 2, 10, 0, 380, 14, 52, 12, 8,
       14, 110, "VGFD", "Any", 3, "Blog"),
    _r("Yoghurt and berries", "Breakfast", "Any", 4, 5, 0, 240, 12, 32, 6,
       3, 24, 90, "VGF", "Summer", 4, "Everyday"),
    _r("Pancakes", "Breakfast", "American", 4, 10, 12, 390, 11, 52, 14, 2,
       16, 380, "FV", "Any", 5, "Family recipe"),
    _r("Chicken & veg traybake", "Dinner", "British", 4, 15, 40, 520, 42, 45,
       17, 7, 11, 620, "GFDK", "Any", 5, "Everyday"),
    _r("Spaghetti bolognese", "Dinner", "Italian", 4, 15, 35, 610, 34, 68,
       19, 6, 12, 700, "DFK", "Any", 5, "Everyday"),
    _r("Vegetable curry", "Dinner", "Indian", 4, 15, 30, 480, 14, 72, 14,
       12, 14, 640, "VG", "Any", 4, "Everyday"),
    _r("Chicken curry", "Dinner", "Indian", 4, 20, 35, 560, 40, 52, 20, 6,
       10, 780, "GFDK", "Winter", 5, "Everyday"),
    _r("Salmon & rice", "Dinner", "Any", 4, 10, 25, 540, 36, 52, 20, 4, 6,
       380, "GFDK", "Any", 4, "Everyday"),
    _r("Beef chilli", "Dinner", "Mexican", 4, 15, 45, 590, 36, 55, 24, 11,
       12, 720, "GFDK", "Winter", 5, "Everyday"),
    _r("Pizza night", "Dinner", "Italian", 4, 20, 15, 640, 28, 72, 24, 5,
       10, 900, "FVK", "Any", 5, "Friday tradition"),
    _r("Pasta primavera", "Dinner", "Italian", 4, 15, 20, 470, 18, 66, 14,
       8, 9, 520, "V", "Spring", 4, "Everyday"),
    _r("Fish finger sandwich", "Lunch", "British", 4, 5, 10, 450, 24, 44,
       18, 3, 6, 780, "DFK", "Any", 3, "Quick"),
    _r("Jacket potato & beans", "Lunch", "British", 4, 10, 60, 420, 15, 68,
       9, 11, 10, 640, "VG", "Winter", 4, "Everyday"),
    _r("Chicken Caesar salad", "Lunch", "American", 4, 15, 12, 430, 34, 16,
       24, 4, 5, 720, "GFDK", "Summer", 4, "Everyday"),
    _r("Tomato soup & bread", "Lunch", "British", 4, 10, 25, 380, 12, 54,
       12, 6, 14, 780, "FVD", "Autumn", 5, "Everyday"),
    _r("Pasta salad", "Lunch", "Any", 4, 15, 12, 460, 16, 62, 16, 6, 9,
       560, "V", "Summer", 4, "Everyday"),
    _r("Omelette & salad", "Lunch", "French", 2, 10, 8, 380, 24, 6, 28, 3,
       3, 480, "VGFDK", "Any", 4, "Quick"),
    _r("Beef stew & dumplings", "Dinner", "British", 4, 20, 120, 620, 40, 52,
       24, 7, 9, 720, "DFK", "Winter", 5, "Sunday"),
    _r("Stir fry noodles", "Dinner", "Chinese", 4, 15, 12, 520, 26, 64, 18,
       6, 12, 900, "DF", "Any", 4, "Quick"),
    _r("Tuna pasta bake", "Dinner", "Italian", 4, 15, 30, 560, 34, 58, 20,
       5, 8, 760, "DFK", "Any", 4, "Everyday"),
    _r("Chicken fajitas", "Dinner", "Mexican", 4, 15, 15, 580, 38, 54, 22,
       7, 8, 780, "GFD", "Any", 5, "Friday"),
    _r("Shepherd's pie", "Dinner", "British", 4, 25, 45, 640, 34, 54, 28,
       7, 10, 760, "DFK", "Winter", 5, "Sunday"),
    _r("Vegetable lasagne", "Dinner", "Italian", 4, 25, 50, 590, 26, 58, 26,
       9, 14, 720, "V", "Any", 4, "Batch"),
    _r("Pork sausages & mash", "Dinner", "British", 4, 10, 25, 660, 30, 52,
       34, 6, 8, 900, "GFDK", "Any", 4, "Everyday"),
    _r("Fish pie", "Dinner", "British", 4, 25, 40, 600, 36, 48, 26, 5, 8,
       780, "DFK", "Winter", 4, "Sunday"),
    _r("Chicken fried rice", "Dinner", "Chinese", 4, 15, 12, 540, 32, 62,
       18, 4, 6, 820, "DF", "Any", 4, "Quick"),
    _r("Bolognese pasta bake", "Dinner", "Italian", 4, 20, 35, 620, 36, 60,
       22, 6, 12, 780, "DFK", "Any", 5, "Batch"),
    _r("Lentil soup", "Lunch", "Any", 4, 10, 30, 320, 16, 46, 6, 12, 6,
       560, "VG", "Winter", 4, "Batch"),
    _r("Cheese & tomato toastie", "Lunch", "British", 2, 5, 8, 480, 20, 42,
       24, 3, 7, 900, "V", "Any", 4, "Quick"),
    _r("Chicken noodle soup", "Lunch", "Any", 4, 10, 20, 340, 24, 34, 10,
       4, 5, 780, "DF", "Winter", 4, "Everyday"),
    _r("Chocolate muffins", "Snack", "American", 12, 15, 22, 280, 4.5, 38,
       12, 1.6, 22, 220, "V", "Any", 5, "Baking"),
    _r("Banana bread", "Snack", "American", 8, 15, 55, 260, 4, 42, 8, 1.8,
       20, 200, "V", "Any", 4, "Baking"),
    _r("Rice pudding", "Dessert", "British", 4, 5, 35, 290, 9, 46, 7, 0.6,
       22, 120, "VGF", "Winter", 4, "Everyday"),
    _r("Apple crumble", "Dessert", "British", 6, 15, 40, 380, 4, 62, 13,
       3.4, 30, 90, "FV", "Autumn", 5, "Sunday"),
    _r("Pancakes with honey", "Dessert", "American", 4, 10, 12, 420, 11, 58,
       15, 2, 22, 380, "V", "Any", 5, "Family recipe"),
    _r("Fruit salad", "Snack", "Any", 4, 10, 0, 120, 1.4, 30, 0.3, 4, 22,
       5, "FVG", "Summer", 4, "Everyday"),
]

# ---------------------------------------------------------------------------
# Recipe ingredients: recipe, ingredient, quantity, unit, pack size
# ---------------------------------------------------------------------------
def _ri(recipe, ingredient, qty, unit, pack):
    return (recipe, ingredient, qty, unit, pack)


RECIPE_INGREDIENTS: List[tuple] = [
    _ri("Porridge with banana", "Oats", 80, "g", 1000),
    _ri("Porridge with banana", "Milk", 480, "ml", 2000),
    _ri("Porridge with banana", "Banana", 2, "piece", 5),
    _ri("Porridge with banana", "Honey", 2, "tbsp", 340),
    _ri("Scrambled eggs on toast", "Eggs", 6, "piece", 6),
    _ri("Scrambled eggs on toast", "Butter", 20, "g", 250),
    _ri("Scrambled eggs on toast", "Bread", 4, "slice", 20),
    _ri("Overnight oats", "Oats", 100, "g", 1000),
    _ri("Overnight oats", "Greek yoghurt", 200, "g", 500),
    _ri("Overnight oats", "Milk", 200, "ml", 2000),
    _ri("Overnight oats", "Frozen berries", 80, "g", 500),
    _ri("Yoghurt and berries", "Greek yoghurt", 400, "g", 500),
    _ri("Yoghurt and berries", "Frozen berries", 120, "g", 500),
    _ri("Yoghurt and berries", "Honey", 2, "tbsp", 340),
    _ri("Pancakes", "Flour", 200, "g", 1500),
    _ri("Pancakes", "Eggs", 3, "piece", 6),
    _ri("Pancakes", "Milk", 300, "ml", 2000),
    _ri("Pancakes", "Baking powder", 2, "tsp", 100),
    _ri("Pancakes", "Butter", 30, "g", 250),
    _ri("Chicken & veg traybake", "Chicken breast", 600, "g", 500),
    _ri("Chicken & veg traybake", "Potato", 800, "g", 2500),
    _ri("Chicken & veg traybake", "Carrot", 3, "piece", 6),
    _ri("Chicken & veg traybake", "Bell pepper", 2, "piece", 3),
    _ri("Chicken & veg traybake", "Olive oil", 2, "tbsp", 500),
    _ri("Chicken & veg traybake", "Basil", 2, "tsp", 20),
    _ri("Spaghetti bolognese", "Beef mince", 500, "g", 500),
    _ri("Spaghetti bolognese", "Spaghetti", 400, "g", 500),
    _ri("Spaghetti bolognese", "Tinned tomatoes", 2, "can", 400),
    _ri("Spaghetti bolognese", "Onion", 1, "piece", 3),
    _ri("Spaghetti bolognese", "Garlic", 2, "clove", 6),
    _ri("Spaghetti bolognese", "Tomato puree", 2, "tbsp", 200),
    _ri("Spaghetti bolognese", "Cheddar cheese", 60, "g", 350),
    _ri("Vegetable curry", "Tinned chickpeas", 2, "can", 400),
    _ri("Vegetable curry", "Coconut milk", 1, "can", 400),
    _ri("Vegetable curry", "Tinned tomatoes", 1, "can", 400),
    _ri("Vegetable curry", "Onion", 1, "piece", 3),
    _ri("Vegetable curry", "Spinach", 150, "g", 200),
    _ri("Vegetable curry", "Curry paste", 3, "tbsp", 200),
    _ri("Vegetable curry", "Rice", 300, "g", 1000),
    _ri("Chicken curry", "Chicken thigh", 800, "g", 1000),
    _ri("Chicken curry", "Coconut milk", 1, "can", 400),
    _ri("Chicken curry", "Onion", 2, "piece", 3),
    _ri("Chicken curry", "Curry paste", 4, "tbsp", 200),
    _ri("Chicken curry", "Rice", 300, "g", 1000),
    _ri("Salmon & rice", "Salmon fillet", 480, "g", 240),
    _ri("Salmon & rice", "Rice", 300, "g", 1000),
    _ri("Salmon & rice", "Broccoli", 2, "piece", 1),
    _ri("Salmon & rice", "Lemon", 1, "piece", 3),
    _ri("Beef chilli", "Beef mince", 500, "g", 500),
    _ri("Beef chilli", "Tinned kidney beans", 2, "can", 400),
    _ri("Beef chilli", "Tinned tomatoes", 2, "can", 400),
    _ri("Beef chilli", "Bell pepper", 2, "piece", 3),
    _ri("Beef chilli", "Onion", 1, "piece", 3),
    _ri("Beef chilli", "Chilli flakes", 1, "tsp", 40),
    _ri("Beef chilli", "Rice", 300, "g", 1000),
    _ri("Pizza night", "Flour", 300, "g", 1500),
    _ri("Pizza night", "Tinned tomatoes", 1, "can", 400),
    _ri("Pizza night", "Cheddar cheese", 150, "g", 350),
    _ri("Pizza night", "Bell pepper", 1, "piece", 3),
    _ri("Pizza night", "Mushrooms", 150, "g", 250),
    _ri("Pasta primavera", "Pasta", 400, "g", 500),
    _ri("Pasta primavera", "Courgette", 2, "piece", 2),
    _ri("Pasta primavera", "Cherry tomatoes", 250, "g", 300),
    _ri("Pasta primavera", "Cream cheese", 150, "g", 300),
    _ri("Pasta primavera", "Basil", 2, "tsp", 20),
    _ri("Fish finger sandwich", "Cod fillet", 400, "g", 300),
    _ri("Fish finger sandwich", "Bread", 8, "slice", 20),
    _ri("Fish finger sandwich", "Lettuce", 1, "piece", 1),
    _ri("Jacket potato & beans", "Potato", 1000, "g", 2500),
    _ri("Jacket potato & beans", "Tinned kidney beans", 1, "can", 400),
    _ri("Jacket potato & beans", "Cheddar cheese", 80, "g", 350),
    _ri("Chicken Caesar salad", "Chicken breast", 500, "g", 500),
    _ri("Chicken Caesar salad", "Lettuce", 2, "piece", 1),
    _ri("Chicken Caesar salad", "Bread", 4, "slice", 20),
    _ri("Chicken Caesar salad", "Cheddar cheese", 50, "g", 350),
    _ri("Tomato soup & bread", "Tinned tomatoes", 3, "can", 400),
    _ri("Tomato soup & bread", "Onion", 1, "piece", 3),
    _ri("Tomato soup & bread", "Garlic", 2, "clove", 6),
    _ri("Tomato soup & bread", "Bread", 8, "slice", 20),
    _ri("Pasta salad", "Pasta", 350, "g", 500),
    _ri("Pasta salad", "Tinned sweetcorn", 1, "can", 340),
    _ri("Pasta salad", "Cherry tomatoes", 200, "g", 300),
    _ri("Pasta salad", "Cucumber", 1, "piece", 1),
    _ri("Omelette & salad", "Eggs", 6, "piece", 6),
    _ri("Omelette & salad", "Cheddar cheese", 60, "g", 350),
    _ri("Omelette & salad", "Spinach", 80, "g", 200),
    _ri("Beef stew & dumplings", "Beef stewing steak", 800, "g", 700),
    _ri("Beef stew & dumplings", "Potato", 600, "g", 2500),
    _ri("Beef stew & dumplings", "Carrot", 4, "piece", 6),
    _ri("Beef stew & dumplings", "Onion", 2, "piece", 3),
    _ri("Beef stew & dumplings", "Flour", 200, "g", 1500),
    _ri("Stir fry noodles", "Chicken breast", 500, "g", 500),
    _ri("Stir fry noodles", "Pasta", 300, "g", 500),
    _ri("Stir fry noodles", "Soy sauce", 3, "tbsp", 250),
    _ri("Stir fry noodles", "Bell pepper", 2, "piece", 3),
    _ri("Stir fry noodles", "Mushrooms", 200, "g", 250),
    _ri("Tuna pasta bake", "Pasta", 400, "g", 500),
    _ri("Tuna pasta bake", "Tinned sweetcorn", 1, "can", 340),
    _ri("Tuna pasta bake", "Cheddar cheese", 120, "g", 350),
    _ri("Tuna pasta bake", "Tinned tomatoes", 2, "can", 400),
    _ri("Chicken fajitas", "Chicken breast", 600, "g", 500),
    _ri("Chicken fajitas", "Bread rolls", 6, "piece", 6),
    _ri("Chicken fajitas", "Bell pepper", 3, "piece", 3),
    _ri("Chicken fajitas", "Onion", 2, "piece", 3),
    _ri("Shepherd's pie", "Beef mince", 600, "g", 500),
    _ri("Shepherd's pie", "Potato", 1200, "g", 2500),
    _ri("Shepherd's pie", "Carrot", 3, "piece", 6),
    _ri("Shepherd's pie", "Tinned tomatoes", 1, "can", 400),
    _ri("Vegetable lasagne", "Pasta", 300, "g", 500),
    _ri("Vegetable lasagne", "Courgette", 2, "piece", 2),
    _ri("Vegetable lasagne", "Tinned tomatoes", 2, "can", 400),
    _ri("Vegetable lasagne", "Cheddar cheese", 150, "g", 350),
    _ri("Vegetable lasagne", "Spinach", 200, "g", 200),
    _ri("Pork sausages & mash", "Pork sausage", 800, "g", 400),
    _ri("Pork sausages & mash", "Potato", 1000, "g", 2500),
    _ri("Pork sausages & mash", "Butter", 30, "g", 250),
    _ri("Pork sausages & mash", "Frozen peas", 300, "g", 900),
    _ri("Fish pie", "Cod fillet", 600, "g", 300),
    _ri("Fish pie", "Potato", 1000, "g", 2500),
    _ri("Fish pie", "Milk", 400, "ml", 2000),
    _ri("Fish pie", "Butter", 40, "g", 250),
    _ri("Chicken fried rice", "Chicken breast", 500, "g", 500),
    _ri("Chicken fried rice", "Rice", 300, "g", 1000),
    _ri("Chicken fried rice", "Eggs", 3, "piece", 6),
    _ri("Chicken fried rice", "Frozen peas", 200, "g", 900),
    _ri("Chicken fried rice", "Soy sauce", 2, "tbsp", 250),
    _ri("Bolognese pasta bake", "Beef mince", 500, "g", 500),
    _ri("Bolognese pasta bake", "Pasta", 400, "g", 500),
    _ri("Bolognese pasta bake", "Tinned tomatoes", 2, "can", 400),
    _ri("Bolognese pasta bake", "Cheddar cheese", 120, "g", 350),
    _ri("Lentil soup", "Tinned kidney beans", 1, "can", 400),
    _ri("Lentil soup", "Tinned tomatoes", 2, "can", 400),
    _ri("Lentil soup", "Carrot", 3, "piece", 6),
    _ri("Lentil soup", "Celery", 2, "stalk", 4),
    _ri("Lentil soup", "Stock cube", 2, "cube", 12),
    _ri("Cheese & tomato toastie", "Bread", 4, "slice", 20),
    _ri("Cheese & tomato toastie", "Cheddar cheese", 100, "g", 350),
    _ri("Cheese & tomato toastie", "Butter", 20, "g", 250),
    _ri("Chicken noodle soup", "Chicken breast", 400, "g", 500),
    _ri("Chicken noodle soup", "Pasta", 150, "g", 500),
    _ri("Chicken noodle soup", "Stock cube", 2, "cube", 12),
    _ri("Chicken noodle soup", "Carrot", 2, "piece", 6),
    _ri("Fruit salad", "Apple", 2, "piece", 4),
    _ri("Fruit salad", "Banana", 2, "piece", 5),
    _ri("Fruit salad", "Frozen berries", 100, "g", 500),
    _ri("Chocolate muffins", "Flour", 250, "g", 1500),
    _ri("Chocolate muffins", "Sugar", 150, "g", 1000),
    _ri("Chocolate muffins", "Eggs", 2, "piece", 6),
    _ri("Chocolate muffins", "Butter", 80, "g", 250),
    _ri("Chocolate muffins", "Milk", 150, "ml", 2000),
    _ri("Banana bread", "Flour", 250, "g", 1500),
    _ri("Banana bread", "Banana", 3, "piece", 5),
    _ri("Banana bread", "Sugar", 100, "g", 1000),
    _ri("Banana bread", "Butter", 60, "g", 250),
    _ri("Banana bread", "Eggs", 2, "piece", 6),
    _ri("Rice pudding", "Rice", 120, "g", 1000),
    _ri("Rice pudding", "Milk", 800, "ml", 2000),
    _ri("Rice pudding", "Sugar", 40, "g", 1000),
    _ri("Apple crumble", "Apple", 6, "piece", 4),
    _ri("Apple crumble", "Flour", 200, "g", 1500),
    _ri("Apple crumble", "Butter", 100, "g", 250),
    _ri("Apple crumble", "Sugar", 80, "g", 1000),
    _ri("Apple crumble", "Oats", 60, "g", 1000),
    _ri("Pancakes with honey", "Flour", 200, "g", 1500),
    _ri("Pancakes with honey", "Eggs", 3, "piece", 6),
    _ri("Pancakes with honey", "Milk", 300, "ml", 2000),
    _ri("Pancakes with honey", "Honey", 3, "tbsp", 340),
]


def _flags(text: str) -> Dict[str, str]:
    """'VG' -> vegetarian + vegan, 'GFDK' -> gluten/dairy/kid flags."""
    return {
        "favourite": "Yes" if "F" in text else "No",
        "vegetarian": "Yes" if "V" in text else "No",
        "vegan": "Yes" if "G" in text and "V" in text else "No",
        "gluten_free": "Yes" if "G" in text else "No",
        "dairy_free": "Yes" if "D" in text else "No",
        "nut_free": "Yes" if "N" in text else "No",
        "kid_friendly": "Yes" if "K" in text else "No",
        "batch_friendly": "Yes",
        "freezer_friendly": "Yes",
        "seasonal": "Any",
        "added_on": None,
    }


def build_samples(cfg: Config) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Every example record, keyed by sheet name then row offset."""
    out: Dict[str, Dict[int, Dict[str, Any]]] = {}

    # ---- Lists ------------------------------------------------------------
    from .sheets import lists as lists_mod
    list_columns = {
        "meal_slot": lists_mod.MEAL_SLOTS,
        "unit": lists_mod.UNITS,
        "category": lists_mod.CATEGORIES,
        "cuisine": lists_mod.CUISINES,
        "tag": lists_mod.TAGS,
        "store": lists_mod.STORES,
        "diet": lists_mod.DIETS,
        "status": lists_mod.STATUS,
        "yes_no": lists_mod.YES_NO,
        "recipe_category": lists_mod.RECIPE_CATEGORIES,
    }
    out["Lists"] = {}
    for i in range(40):
        out["Lists"][i] = {
            key: (values[i] if i < len(values) else None)
            for key, values in list_columns.items()}

    # ---- Household --------------------------------------------------------
    members = [
        ("Maya", "Adult", 38, "None", "None", "Mushrooms", 1.0, "Yes",
         "Main cook"),
        ("Dan", "Adult", 41, "None", "Peanuts", "Olives", 1.05, "Yes",
         "Grill duty"),
        ("Ivy", "Child", 8, "None", "None", "Anything spicy", 0.6, "Yes",
         "Packed lunch"),
        ("Theo", "Child", 5, "None", "None", "Fish", 0.5, "No", ""),
    ]
    out["Household"] = {
        i: {"member": m[0], "role": m[1], "age": m[2], "diet": m[3],
            "allergies": m[4], "dislikes": m[5], "servings": m[6],
            "packed_lunch": m[7], "notes": m[8]}
        for i, m in enumerate(members)}

    # ---- Recipes ----------------------------------------------------------
    out["Recipes"] = {}
    for i, r in enumerate(RECIPES):
        (name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
         sod, flags, season, rating, source) = r
        record = {
            "recipe": name, "category": cat, "cuisine": cui,
            "servings": srv, "prep_time": prep, "cook_time": cook,
            "calories": kcal, "protein": pro, "carbs": carb, "fat": fat,
            "fibre": fib, "sugar": sug, "sodium": sod,
            "seasonal": season, "rating": rating, "source": source,
            "tags": "Quick" if prep + cook <= 30 else "Batch",
            "notes": "Batch cook on Sunday and freeze in portions."
                     if "Batch" in flags else "",
        }
        record.update(_flags(flags))
        out["Recipes"][i] = record

    # ---- Recipe Ingredients ------------------------------------------------
    out["Recipe Ingredients"] = {
        i: {"recipe": r[0], "ingredient": r[1], "quantity": r[2],
            "unit": r[3], "pack_size": r[4], "waste_factor": 0.05,
            "organic": "No"}
        for i, r in enumerate(RECIPE_INGREDIENTS)}

    # ---- Ingredients ------------------------------------------------------
    out["Ingredients"] = {}
    for i, ing in enumerate(INGREDIENTS):
        (name, cat, unit, price, pack, kcal, pro, carb, fat, fib, shelf,
         storage, staple, allergens) = ing
        out["Ingredients"][i] = {
            "ingredient": name, "category": cat, "unit": unit,
            "price": price, "pack_size": pack,
            "calories_per_unit": kcal, "protein_per_unit": pro,
            "carbs_per_unit": carb, "fat_per_unit": fat,
            "fibre_per_unit": fib, "shelf_life_days": shelf,
            "storage": storage, "staple": staple, "organic": "No",
            "seasonal": "Any", "allergens": allergens,
            "notes": "",
        }

    # ---- Meal Plan --------------------------------------------------------
    start = cfg.start_date
    plan: List[Dict[str, Any]] = []

    def add(date_offset: int, slot: str, recipe: str, servings: int,
            status: str = "Planned", rating: float = 0.0, cooked: str = "No"):
        plan.append({
            "plan_id": f"W{date_offset // 7 + 1}-D{date_offset % 7 + 1}",
            "date": start + dt.timedelta(days=date_offset),
            "slot": slot, "recipe": recipe, "servings": servings,
            "status": status, "cooked": cooked, "rating": rating,
            "notes": ""})

    weekly = [
        (0, "Porridge with banana", "Pasta salad", "Chicken & veg traybake",
         "Fruit salad"),
        (1, "Scrambled eggs on toast", "Tomato soup & bread",
         "Spaghetti bolognese", "Banana bread"),
        (2, "Overnight oats", "Chicken Caesar salad", "Vegetable curry",
         "Yoghurt and berries"),
        (3, "Porridge with banana", "Cheese & tomato toastie",
         "Salmon & rice", "Chocolate muffins"),
        (4, "Scrambled eggs on toast", "Omelette & salad", "Pizza night",
         "Fruit salad"),
        (5, "Pancakes", "Jacket potato & beans", "Beef chilli",
         "Apple crumble"),
        (6, "Yoghurt and berries", "Lentil soup", "Beef stew & dumplings",
         "Rice pudding"),
        (7, "Porridge with banana", "Pasta salad", "Chicken curry",
         "Fruit salad"),
        (8, "Scrambled eggs on toast", "Tomato soup & bread",
         "Stir fry noodles", "Banana bread"),
        (9, "Overnight oats", "Chicken Caesar salad", "Tuna pasta bake",
         "Yoghurt and berries"),
        (10, "Porridge with banana", "Cheese & tomato toastie",
         "Chicken fajitas", "Chocolate muffins"),
        (11, "Scrambled eggs on toast", "Omelette & salad",
         "Pasta primavera", "Fruit salad"),
        (12, "Pancakes with honey", "Jacket potato & beans",
         "Shepherd's pie", "Apple crumble"),
        (13, "Yoghurt and berries", "Lentil soup", "Fish pie",
         "Rice pudding"),
        (14, "Porridge with banana", "Pasta salad",
         "Chicken fried rice", "Fruit salad"),
        (15, "Scrambled eggs on toast", "Tomato soup & bread",
         "Vegetable lasagne", "Banana bread"),
        (16, "Overnight oats", "Chicken Caesar salad",
         "Bolognese pasta bake", "Yoghurt and berries"),
        (17, "Porridge with banana", "Cheese & tomato toastie",
         "Pork sausages & mash", "Chocolate muffins"),
        (18, "Scrambled eggs on toast", "Omelette & salad", "Pizza night",
         "Fruit salad"),
        (19, "Pancakes", "Jacket potato & beans", "Beef chilli",
         "Apple crumble"),
        (20, "Yoghurt and berries", "Lentil soup",
         "Chicken & veg traybake", "Rice pudding"),
    ]
    for offset, breakfast, lunch, dinner, snack in weekly:
        add(offset, "Breakfast", breakfast, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.5 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Lunch", lunch, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.0 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Dinner", dinner, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.5 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Evening snack", snack, 4,
            status="Eaten" if offset < 14 else "Planned",
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Afternoon snack", "Fruit salad", 4,
            status="Eaten" if offset < 14 else "Planned",
            cooked="Yes" if offset < 14 else "No")
    # a takeaway and an eating out day
    add(5, "Dinner", "Pizza night", 0, status="Takeaway")
    add(12, "Lunch", "Fish finger sandwich", 0, status="Eating out")
    out["Meal Plan"] = {i: rec for i, rec in enumerate(plan)}

    # ---- Grocery List -----------------------------------------------------
    groceries = [
        ("Chicken breast", 600, "g", "Greenfield Market", "Meat & Fish"),
        ("Beef mince", 1100, "g", "Greenfield Market", "Meat & Fish"),
        ("Beef stewing steak", 800, "g", "Butcher", "Meat & Fish"),
        ("Salmon fillet", 480, "g", "Greenfield Market", "Meat & Fish"),
        ("Cod fillet", 1000, "g", "Greenfield Market", "Meat & Fish"),
        ("Pork sausage", 800, "g", "Butcher", "Meat & Fish"),
        ("Eggs", 18, "piece", "Greenfield Market", "Dairy & Eggs"),
        ("Milk", 4000, "ml", "Greenfield Market", "Dairy & Eggs"),
        ("Cheddar cheese", 920, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Butter", 330, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Greek yoghurt", 1100, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Cream cheese", 150, "g", "Corner Grocer", "Dairy & Eggs"),
        ("Rice", 1500, "g", "Bulk Barn", "Grains & Pasta"),
        ("Pasta", 1450, "g", "Bulk Barn", "Grains & Pasta"),
        ("Spaghetti", 400, "g", "Bulk Barn", "Grains & Pasta"),
        ("Oats", 240, "g", "Bulk Barn", "Grains & Pasta"),
        ("Bread", 60, "slice", "Corner Grocer", "Bakery"),
        ("Bread rolls", 6, "piece", "Corner Grocer", "Bakery"),
        ("Flour", 1400, "g", "Bulk Barn", "Baking"),
        ("Sugar", 370, "g", "Bulk Barn", "Baking"),
        ("Olive oil", 2, "tbsp", "Greenfield Market", "Condiments"),
        ("Soy sauce", 5, "tbsp", "Asian Supermarket", "Condiments"),
        ("Tinned tomatoes", 14, "can", "Bulk Barn", "Tins & Jars"),
        ("Tomato puree", 2, "tbsp", "Greenfield Market", "Tins & Jars"),
        ("Coconut milk", 2, "can", "Asian Supermarket", "Tins & Jars"),
        ("Tinned chickpeas", 2, "can", "Bulk Barn", "Tins & Jars"),
        ("Tinned kidney beans", 4, "can", "Bulk Barn", "Tins & Jars"),
        ("Tinned sweetcorn", 1, "can", "Bulk Barn", "Tins & Jars"),
        ("Onion", 12, "piece", "Greenfield Market", "Vegetables"),
        ("Garlic", 12, "clove", "Greenfield Market", "Vegetables"),
        ("Carrot", 17, "piece", "Farmers Market", "Vegetables"),
        ("Celery", 2, "stalk", "Greenfield Market", "Vegetables"),
        ("Bell pepper", 10, "piece", "Farmers Market", "Vegetables"),
        ("Broccoli", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Courgette", 4, "piece", "Farmers Market", "Vegetables"),
        ("Spinach", 630, "g", "Greenfield Market", "Vegetables"),
        ("Mushrooms", 350, "g", "Greenfield Market", "Vegetables"),
        ("Sweet potato", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Potato", 6600, "g", "Farmers Market", "Vegetables"),
        ("Cherry tomatoes", 650, "g", "Farmers Market", "Vegetables"),
        ("Cucumber", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Lettuce", 5, "piece", "Greenfield Market", "Vegetables"),
        ("Lemon", 2, "piece", "Greenfield Market", "Fruit"),
        ("Banana", 14, "piece", "Greenfield Market", "Fruit"),
        ("Apple", 10, "piece", "Farmers Market", "Fruit"),
        ("Frozen berries", 400, "g", "Greenfield Market", "Frozen"),
        ("Frozen peas", 500, "g", "Greenfield Market", "Frozen"),
        ("Curry paste", 7, "tbsp", "Asian Supermarket", "Condiments"),
        ("Stock cube", 6, "cube", "Greenfield Market", "Condiments"),
        ("Basil", 4, "tsp", "Greenfield Market", "Herbs & Spices"),
        ("Coriander", 1, "sprig", "Farmers Market", "Herbs & Spices"),
        ("Baking powder", 4, "tsp", "Bulk Barn", "Baking"),
        ("Honey", 7, "tbsp", "Greenfield Market", "Condiments"),
        ("Kitchen roll", 2, "roll", "Greenfield Market", "Household"),
    ]
    out["Grocery List"] = {
        i: {"item": g[0], "quantity": g[1], "unit": g[2], "store": g[3],
            "aisle": g[4], "buy": "Yes", "bought": "No",
            "week_start": start}
        for i, g in enumerate(groceries)}

    # ---- Pantry -----------------------------------------------------------
    pantry = [
        ("Rice", 1200, "g", "Pantry", 40),
        ("Pasta", 900, "g", "Pantry", 60),
        ("Flour", 1600, "g", "Pantry", 90),
        ("Sugar", 800, "g", "Pantry", 120),
        ("Oats", 900, "g", "Pantry", 70),
        ("Olive oil", 1, "tbsp", "Cupboard", 200),
        ("Tinned tomatoes", 4, "can", "Pantry", 300),
        ("Tinned chickpeas", 1, "can", "Pantry", 280),
        ("Coconut milk", 1, "can", "Pantry", 240),
        ("Stock cube", 8, "cube", "Pantry", 180),
        ("Soy sauce", 1, "tbsp", "Cupboard", 150),
        ("Honey", 1, "tbsp", "Cupboard", 260),
        ("Peanut butter", 1, "tbsp", "Cupboard", 120),
        ("Eggs", 5, "piece", "Fridge", 14),
        ("Milk", 1500, "ml", "Fridge", 4),
        ("Butter", 180, "g", "Fridge", 30),
        ("Cheddar cheese", 320, "g", "Fridge", 12),
        ("Greek yoghurt", 300, "g", "Fridge", 5),
        ("Carrot", 4, "piece", "Fridge", 12),
        ("Bell pepper", 2, "piece", "Fridge", 6),
        ("Broccoli", 1, "piece", "Fridge", 4),
        ("Spinach", 120, "g", "Fridge", 3),
        ("Cherry tomatoes", 200, "g", "Fridge", 5),
        ("Lettuce", 1, "piece", "Fridge", 3),
        ("Lemon", 2, "piece", "Fridge", 10),
        ("Apple", 4, "piece", "Fridge", 20),
        ("Banana", 3, "piece", "Cupboard", 3),
        ("Frozen peas", 600, "g", "Freezer", 90),
        ("Frozen berries", 300, "g", "Freezer", 120),
        ("Chicken breast", 250, "g", "Fridge", 1),
    ]
    out["Pantry"] = {
        i: {"item": p[0], "quantity": p[1], "unit": p[2], "storage": p[3],
            "purchase_date": start - dt.timedelta(days=p[4] // 2),
            "opened_date": None, "store": "Greenfield Market",
            "price_paid": 0.0, "frozen": "No", "servings_left": 2,
            "notes": ""}
        for i, p in enumerate(pantry)}

    # ---- Staples ----------------------------------------------------------
    staples = [
        ("Milk", "ml", 2000, 2, "Greenfield Market", 2.60, "Yes"),
        ("Bread", "slice", 20, 2, "Corner Grocer", 1.80, "Yes"),
        ("Eggs", "piece", 12, 7, "Greenfield Market", 5.04, "Yes"),
        ("Banana", "piece", 5, 4, "Greenfield Market", 0.95, "Yes"),
        ("Potato", "g", 2500, 7, "Farmers Market", 3.50, "Yes"),
        ("Onion", "piece", 3, 10, "Greenfield Market", 0.84, "Yes"),
        ("Rice", "g", 1000, 21, "Bulk Barn", 2.10, "No"),
        ("Cheddar cheese", "g", 350, 10, "Greenfield Market", 4.17, "Yes"),
        ("Kitchen roll", "roll", 2, 21, "Greenfield Market", 4.98, "Yes"),
        ("Washing up liquid", "bottle", 1, 28, "Greenfield Market", 1.79,
         "Yes"),
    ]
    out["Staples"] = {
        i: {"staple": s[0], "usual_unit": s[1], "usual_qty": s[2],
            "buy_interval_days": s[3], "store": s[4],
            "last_bought": start - dt.timedelta(days=s[3] - 1),
            "auto_add": s[6], "qty_to_add": s[2]}
        for i, s in enumerate(staples)}

    # ---- Leftovers --------------------------------------------------------
    leftovers = [
        ("LO-01", "Vegetable curry portions", "Vegetable curry", 3, "Fridge",
         2),
        ("LO-02", "Bolognese portions", "Spaghetti bolognese", 4, "Freezer",
         6),
        ("LO-03", "Shepherd's pie portions", "Shepherd's pie", 2, "Fridge",
         1),
        ("LO-04", "Rice pudding", "Rice pudding", 4, "Fridge", 2),
        ("LO-05", "Chilli portions", "Beef chilli", 3, "Freezer", 8),
        ("LO-06", "Soup portions", "Lentil soup", 2, "Fridge", 3),
        ("LO-07", "Lasagne portions", "Vegetable lasagne", 4, "Freezer",
         10),
    ]
    out["Leftovers"] = {
        i: {"leftover_id": l[0], "item": l[1], "recipe": l[2],
            "cooked_date": start - dt.timedelta(days=l[5]),
            "portions": l[3], "storage": l[4], "portions_left": l[3],
            "used_up": "No", "thrown": "No", "container": "Tupperware",
            "reheats": 1, "notes": ""}
        for i, l in enumerate(leftovers)}

    # ---- Food Waste -------------------------------------------------------
    waste = [
        ("W-01", 2, "Spinach", 80, "g", "Spoiled", "No", "Fridge"),
        ("W-02", 5, "Bread", 4, "slice", "Mouldy", "No", "Cupboard"),
        ("W-03", 8, "Lettuce", 1, "piece", "Expired", "No", "Fridge"),
        ("W-04", 11, "Greek yoghurt", 150, "g", "Expired", "No", "Fridge"),
        ("W-05", 13, "Rice", 200, "g", "Cooked too much", "No", "Fridge"),
        ("W-06", 15, "Mushrooms", 120, "g", "Spoiled", "No", "Fridge"),
        ("W-07", 18, "Banana", 2, "piece", "Bought too much", "No",
         "Cupboard"),
        ("W-08", 19, "Apple", 1, "piece", "Child refused", "No", "Fridge"),
        ("W-09", 20, "Milk", 300, "ml", "Expired", "No", "Fridge"),
        ("W-10", 21, "Broccoli", 1, "piece", "Spoiled", "No", "Fridge"),
    ]
    out["Food Waste"] = {
        i: {"waste_id": w[0], "date": start - dt.timedelta(days=w[1]),
            "item": w[2], "qty": w[3], "unit": w[4], "reason": w[5],
            "avoidable": w[6], "storage_at_waste": w[7],
            "store": "Greenfield Market", "portion": "1 portion",
            "notes": ""}
        for i, w in enumerate(waste)}

    # ---- Meal Prep --------------------------------------------------------
    prep = [
        ("P-01", "Sunday", "Cook the bolognese base", "Spaghetti bolognese",
         8, 40, 1, "Oven"),
        ("P-02", "Sunday", "Roast the chicken for the week",
         "Chicken & veg traybake", 8, 40, 2, "Oven"),
        ("P-03", "Sunday", "Make the curry sauce", "Vegetable curry", 8, 25,
         3, "Hob"),
        ("P-04", "Sunday", "Portion the rice pudding", "Rice pudding", 4, 10,
         4, "No cooking"),
        ("P-05", "Wednesday", "Chop the stir fry vegetables",
         "Stir fry noodles", 4, 15, 1, "No cooking"),
        ("P-06", "Friday", "Make the pizza dough", "Pizza night", 4, 20, 1,
         "Oven"),
        ("P-07", "Saturday", "Bake the muffins", "Chocolate muffins", 12, 25,
         2, "Oven"),
        ("P-08", "Sunday", "Prepare packed lunch boxes", "Pasta salad", 4,
         15, 5, "No cooking"),
    ]
    out["Meal Prep"] = {
        i: {"task_id": p[0], "prep_day": p[1], "task": p[2], "recipe": p[3],
            "servings": p[4], "duration_min": p[5], "order": p[6],
            "equipment": p[7], "assigned_to": "Maya", "batch_qty": p[4],
            "portions": p[4], "linked_slot": "Dinner", "completed": "No",
            "status": "To do", "notes": ""}
        for i, p in enumerate(prep)}

    # ---- Dietary Filters --------------------------------------------------
    filters = [
        ("DF-01", "Dan", "Peanuts", "Nut allergy", "Avoid"),
        ("DF-02", "Theo", "Cod fillet", "Does not like fish", "Preference"),
        ("DF-03", "Ivy", "Chilli flakes", "Too spicy", "Preference"),
        ("DF-04", "", "Prawns", "Shellfish allergy in the family", "Avoid"),
        ("DF-05", "", "Gluten", "Dan is gluten sensitive", "Caution"),
    ]
    out["Dietary Filters"] = {
        i: {"filter_id": d[0], "member": d[1], "exclude": d[2],
            "reason": d[3], "severity": d[4], "active": "Yes", "notes": ""}
        for i, d in enumerate(filters)}

    # ---- Nutrition --------------------------------------------------------
    nutrition = []
    for day in range(21):
        date = start + dt.timedelta(days=day)
        for slot, recipe in (("Breakfast", weekly[day][1]),
                             ("Lunch", weekly[day][2]),
                             ("Dinner", weekly[day][3]),
                             ("Evening snack", weekly[day][4])):
            nutrition.append({
                "date": date, "slot": slot, "recipe": recipe,
                "servings": 1, "water_glasses": 6, "notes": ""})
    out["Nutrition"] = {i: rec for i, rec in enumerate(nutrition)}

    # ---- Budget -----------------------------------------------------------
    months = []
    today = cfg.today
    for back in range(5, -1, -1):
        first = dt.date(today.year, today.month, 1)
        for _ in range(back):
            first = dt.date(first.year - (first.month == 1),
                            (first.month - 2) % 12 + 1, 1)
        months.append(first.strftime("%b %Y"))
    budget_actual = [742.5, 698.2, 815.4, 764.9, 690.3, 812.7]
    out["Budget"] = {
        i: {"month": months[i], "actual_eating_out": budget_actual[i] / 10,
            "notes": ""}
        for i in range(6)}

    # ---- Recipe Costs -----------------------------------------------------
    out["Recipe Costs"] = {
        i: {"recipe": r[0], "notes": ""}
        for i, r in enumerate(RECIPES)}

    # ---- Converter --------------------------------------------------------
    conversions = [
        ("g", "kg", 0.001, "Weight", "500 g = 0.5 kg"),
        ("kg", "g", 1000, "Weight", "1 kg = 1000 g"),
        ("g", "oz", 0.0353, "Weight", "100 g = 3.5 oz"),
        ("oz", "g", 28.35, "Weight", "1 oz = 28 g"),
        ("lb", "g", 453.6, "Weight", "1 lb = 454 g"),
        ("ml", "l", 0.001, "Volume", "500 ml = 0.5 l"),
        ("l", "ml", 1000, "Volume", "1 l = 1000 ml"),
        ("ml", "fl oz", 0.0338, "Volume", "100 ml = 3.4 fl oz"),
        ("fl oz", "ml", 29.57, "Volume", "1 fl oz = 30 ml"),
        ("tsp", "ml", 5, "Volume", "1 tsp = 5 ml"),
        ("tbsp", "ml", 15, "Volume", "1 tbsp = 15 ml"),
        ("tbsp", "tsp", 3, "Volume", "1 tbsp = 3 tsp"),
        ("cup", "ml", 240, "Volume", "1 cup = 240 ml"),
        ("cup", "g", 125, "Weight", "1 cup of flour = 125 g"),
        ("clove", "tsp", 0.5, "Count", "1 clove of garlic = 0.5 tsp"),
        ("slice", "g", 35, "Weight", "1 slice of bread = 35 g"),
        ("piece", "g", 120, "Weight", "1 medium onion = 120 g"),
        ("can", "ml", 400, "Volume", "1 tin = 400 ml"),
        ("punnet", "g", 300, "Weight", "1 punnet = 300 g"),
        ("bunch", "g", 150, "Weight", "1 bunch of herbs = 150 g"),
    ]
    out["Converter"] = {
        i: {"from_unit": c[0], "to_unit": c[1], "factor": c[2],
            "category": c[3], "example": c[4], "notes": ""}
        for i, c in enumerate(conversions)}

    # ---- Rotation ---------------------------------------------------------
    out["Rotation"] = {
        i: {"recipe": r[0], "notes": ""}
        for i, r in enumerate(RECIPES)}

    # ---- Food Safety ------------------------------------------------------
    from .sheets import food_safety as fs_mod
    out["Food Safety"] = {
        i: {"food": row[0], "category": row[1], "storage": row[2],
            "fridge_days": row[3], "freezer_days": row[4],
            "cooked_days": row[5], "safe_temp": row[6],
            "reheat_temp": row[7], "source": "Food standards guidance",
            "notes": ""}
        for i, row in enumerate(fs_mod.ROWS)}

    # ---- Fridge & Freezer -------------------------------------------------
    fridge = [
        ("FF-01", "Bolognese portions", "Spaghetti bolognese", 4, "Freezer",
         6),
        ("FF-02", "Soup portions", "Lentil soup", 4, "Freezer", 5),
        ("FF-03", "Lasagne portions", "Vegetable lasagne", 4, "Freezer", 9),
        ("FF-04", "Chilli portions", "Beef chilli", 3, "Freezer", 7),
        ("FF-05", "Rice pudding", "Rice pudding", 4, "Fridge", 2),
        ("FF-06", "Stew portions", "Beef stew & dumplings", 3, "Fridge", 1),
        ("FF-07", "Curry portions", "Chicken curry", 4, "Freezer", 4),
    ]
    out["Fridge & Freezer"] = {
        i: {"batch_id": fr[0], "item": fr[1], "recipe": fr[2],
            "portions": fr[3], "storage": fr[4],
            "cooked_date": start - dt.timedelta(days=fr[5]),
            "container": "Tupperware", "reheats": 1, "eaten": "No",
            "notes": ""}
        for i, fr in enumerate(fridge)}

    # ---- Grocery Spending ------------------------------------------------
    spending = []
    shops = [
        (21, "Greenfield Market", [("Chicken breast", 500, "g", 4.95),
                                   ("Milk", 2000, "ml", 2.60),
                                   ("Eggs", 12, "piece", 5.04),
                                   ("Bread", 20, "slice", 1.80),
                                   ("Cheddar cheese", 350, "g", 4.17),
                                   ("Butter", 250, "g", 2.48)]),
        (18, "Bulk Barn", [("Rice", 1000, "g", 2.10),
                           ("Pasta", 500, "g", 0.95),
                           ("Flour", 1500, "g", 1.65),
                           ("Oats", 1000, "g", 1.90),
                           ("Tinned tomatoes", 4, "can", 2.20),
                           ("Sugar", 1000, "g", 1.20)]),
        (14, "Greenfield Market", [("Beef mince", 500, "g", 5.95),
                                   ("Carrot", 6, "piece", 0.72),
                                   ("Onion", 3, "piece", 0.84),
                                   ("Spinach", 200, "g", 1.38),
                                   ("Frozen peas", 900, "g", 2.61)]),
        (11, "Farmers Market", [("Potato", 2500, "g", 3.50),
                                ("Bell pepper", 3, "piece", 1.95),
                                ("Apple", 4, "piece", 1.40),
                                ("Cherry tomatoes", 300, "g", 2.97)]),
        (7, "Greenfield Market", [("Salmon fillet", 240, "g", 7.18),
                                  ("Broccoli", 1, "piece", 0.79),
                                  ("Lemon", 3, "piece", 1.35),
                                  ("Greek yoghurt", 500, "g", 2.45),
                                  ("Banana", 5, "piece", 0.95)]),
        (4, "Corner Grocer", [("Bread rolls", 6, "piece", 2.10),
                              ("Cream cheese", 300, "g", 2.37),
                              ("Cucumber", 1, "piece", 0.69),
                              ("Lettuce", 1, "piece", 0.99)]),
        (2, "Asian Supermarket", [("Coconut milk", 2, "can", 2.10),
                                  ("Curry paste", 1, "jar", 1.60),
                                  ("Soy sauce", 250, "ml", 1.29)]),
    ]
    receipt = 1
    for days_ago, store, items in shops:
        for item, qty, unit, price in items:
            spending.append({
                "date": start - dt.timedelta(days=days_ago),
                "store": store, "item": item, "qty": qty, "unit": unit,
                "price": round(price / (qty if qty else 1), 4),
                "receipt_no": f"R-{1000 + receipt}", "payment": "Debit card",
                "on_sale": "No", "savings": 0.0, "notes": ""})
        receipt += 1
    out["Grocery Spending"] = {i: rec for i, rec in enumerate(spending)}

    # ---- Store Prices -----------------------------------------------------
    prices = []
    price_rows = [
        ("Chicken breast", "Greenfield Market", 0.0099, 500, "No"),
        ("Chicken breast", "Bulk Barn", 0.0119, 500, "Yes"),
        ("Beef mince", "Greenfield Market", 0.0119, 500, "No"),
        ("Beef mince", "Butcher", 0.0109, 500, "Yes"),
        ("Rice", "Bulk Barn", 0.0021, 1000, "No"),
        ("Rice", "Greenfield Market", 0.0029, 1000, "No"),
        ("Eggs", "Greenfield Market", 0.42, 6, "No"),
        ("Eggs", "Farmers Market", 0.55, 6, "Yes"),
        ("Milk", "Greenfield Market", 0.0013, 2000, "No"),
        ("Milk", "Corner Grocer", 0.0015, 2000, "No"),
        ("Bread", "Corner Grocer", 0.09, 20, "No"),
        ("Bread", "Greenfield Market", 0.11, 20, "No"),
        ("Cheddar cheese", "Greenfield Market", 0.0119, 350, "No"),
        ("Cheddar cheese", "Bulk Barn", 0.0139, 350, "Yes"),
        ("Pasta", "Bulk Barn", 0.0019, 500, "No"),
        ("Pasta", "Greenfield Market", 0.0026, 500, "No"),
        ("Potato", "Farmers Market", 0.0014, 2500, "No"),
        ("Potato", "Greenfield Market", 0.0019, 2500, "No"),
        ("Tinned tomatoes", "Bulk Barn", 0.55, 400, "No"),
        ("Tinned tomatoes", "Greenfield Market", 0.69, 400, "No"),
    ]
    for i, pr in enumerate(price_rows):
        prices.append({
            "item": pr[0], "store": pr[1], "unit": "g", "price": pr[2],
            "pack_size": pr[3], "date": start - dt.timedelta(days=i % 14),
            "on_sale": pr[4], "usual_price": round(pr[2] * 1.15, 4),
            "notes": ""})
    out["Store Prices"] = {i: rec for i, rec in enumerate(prices)}

    # ---- Stores -----------------------------------------------------------
    stores = [
        ("Greenfield Market", "12 High Street", "555-0101",
         "greenfield.example", "Yes", "No", "Yes", 30.0, 4.99, "Saturday",
         "07:00-22:00", 1.2, "Yes", "Yes", "Yes", "All major cards"),
        ("Corner Grocer", "3 Mill Lane", "555-0102", "", "No", "Yes", "No",
         0.0, 0.0, "n/a", "06:30-19:00", 0.3, "No", "No", "No", "Cash only"),
        ("Bulk Barn", "Unit 4, Trade Park", "555-0103", "bulkbarn.example",
         "No", "Yes", "Yes", 25.0, 0.0, "Wednesday", "08:00-18:00", 4.5,
         "Yes", "Yes", "Yes", "All major cards"),
        ("Farmers Market", "Town square", "", "", "No", "No", "No", 0.0, 0.0,
         "Saturday", "08:00-13:00", 1.0, "Yes", "No", "No", "Cash and cards"),
        ("Asian Supermarket", "88 Dock Road", "555-0105",
         "asiansuper.example", "No", "No", "Yes", 0.0, 0.0, "n/a",
         "09:00-20:00", 3.1, "No", "No", "No", "Cash and cards"),
    ]
    out["Stores"] = {
        i: {"store": s[0], "address": s[1], "phone": s[2], "website": s[3],
            "loyalty": "Greencard" if i == 0 else "", "delivery": s[4],
            "pickup": s[5], "min_order": s[7], "delivery_fee": s[8],
            "delivery_day": s[9], "opening_hours": s[10],
            "distance_km": s[11], "parking": s[12], "organic_range": s[13],
            "bulk_bins": s[14], "cards": s[15],
            "best_for": "Weekly shop" if i == 0 else "Top ups",
            "rating": 5 if i == 0 else 4, "notes": ""}
        for i, s in enumerate(stores)}

    # ---- Events -----------------------------------------------------------
    events = [
        ("Ivy's birthday party", start + dt.timedelta(days=24), 12, "Dinner",
         "Maya", "Home", 90.0, "Pizza night", "", "", "", "Pancakes",
         "Juice and water", 1.0, "Planning"),
        ("Sunday roast for Dan's parents", start + dt.timedelta(days=6), 6,
         "Dinner", "Dan", "Home", 70.0, "Beef stew & dumplings", "", "", "",
         "Apple crumble", "Wine and water", 1.0, "Planning"),
        ("Picnic at the park", start + dt.timedelta(days=35), 5, "Picnic",
         "Maya", "Riverside park", 40.0, "Pasta salad", "", "", "",
         "Fruit salad", "Lemonade", 1.0, "Planning"),
    ]
    out["Events"] = {
        i: {"event": e[0], "date": e[1], "guests": e[2], "meal_type": e[3],
            "host": e[4], "location": e[5], "budget": e[6], "menu_1": e[7],
            "menu_2": e[8], "menu_3": e[9], "menu_4": e[10], "dessert": e[11],
            "drinks": e[12], "servings": e[13], "status": e[14],
            "dietary_notes": "Two nut allergies, one gluten free",
            "leftover_plan": "Send portions home with the guests",
            "notes": ""}
        for i, e in enumerate(events)}

    # ---- Goals ------------------------------------------------------------
    goals = [
        ("Bin less than 5% of the food we buy", "Waste", 5, 4.2, "% of spend",
         120),
        ("Keep the weekly shop under budget", "Budget", 180, 168,
         "currency", 60),
        ("Cook at home 18 times a week", "Cooking", 18, 16, "meals a week",
         90),
        ("Try two new recipes a month", "Variety", 2, 3, "recipes a month",
         30),
        ("Hit 30 g of fibre a day", "Nutrition", 30, 24, "grams a day", 60),
        ("Five packed lunches a week", "Health", 5, 4, "lunches a week", 45),
    ]
    out["Goals"] = {
        i: {"goal": g[0], "category": g[1], "target": g[2], "current": g[3],
            "unit": g[4],
            "deadline": cfg.today + dt.timedelta(days=g[5]),
            "streak": 6 - i, "best_streak": 12 - i, "notes": ""}
        for i, g in enumerate(goals)}

    # ---- Sustainability ---------------------------------------------------
    sus = []
    for back in range(5, -1, -1):
        first = dt.date(today.year, today.month, 1)
        for _ in range(back):
            first = dt.date(first.year - (first.month == 1),
                            (first.month - 2) % 12 + 1, 1)
        sus.append({"month": first.strftime("%b %Y"), "local_shops": 4,
                    "bulk_buys": 3, "packaging_free": 2, "own_grown": 0.5,
                    "notes": ""})
    out["Sustainability"] = {i: rec for i, rec in enumerate(sus)}

    return out
````

---

## 3. The registers

One module per data tab. Each returns a list of columns with their formulas, and the writer turns that into a formatted, validated, protected sheet.

### `meal_planner_spreadsheet/sheets/__init__.py`

One module per tab *(6 lines)*

````python
"""One module per tab.

Register sheets expose ``NAME`` and ``spec(cfg)`` (plus an optional
``decorate``); page sheets expose ``NAME`` and ``build(book, fmts, cfg,
reg)``. `build.py` wires them together.
"""
````

### `meal_planner_spreadsheet/sheets/lists.py`

Lists - every drop down source in one place *(114 lines)*

````python
"""
Lists - every drop down source in one place.

The buyer edits these lists once and every planner grid, grocery list,
recipe tag and report follows.  The seven columns below are also published
as dynamic named ranges (``Meal_Slots``, ``Unit_List``, ...) so the
validation on the other tabs always points here.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

MEAL_SLOTS = ["Breakfast", "Morning snack", "Lunch", "Afternoon snack",
              "Dinner", "Evening snack", "Dessert"]

UNITS = ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "clove", "slice",
         "piece", "can", "tin", "packet", "bunch", "handful", "pinch",
         "sprig", "cube", "sheet", "roll", "jar", "bottle", "punnet",
         "stalk", "bulb", "strip", "portion", "bunch"]

CATEGORIES = ["Vegetables", "Fruit", "Meat & Fish", "Dairy & Eggs",
              "Bakery", "Grains & Pasta", "Tins & Jars", "Frozen",
              "Herbs & Spices", "Condiments", "Snacks", "Drinks",
              "Baking", "Household", "Other"]

CUISINES = ["Any", "Italian", "Mexican", "Indian", "Chinese", "Thai",
            "Japanese", "Mediterranean", "Middle Eastern", "French",
            "American", "British", "Caribbean", "African", "Vietnamese",
            "Korean", "Greek", "Spanish", "Turkish", "Moroccan"]

TAGS = ["Quick", "One pot", "Slow cooker", "Air fryer", "Grill", "Oven",
        "No cook", "Batch cook", "Freezer friendly", "Kid friendly",
        "Comfort food", "Light", "High protein", "Low carb", "Budget",
        "Date night", "Picnic", "Soup", "Salad", "Sandwich", "Stew",
        "Curry", "Stir fry", "Pasta", "Rice bowl", "Tacos", "Pizza",
        "Brunch", "Dessert", "Drink"]

STORES = ["Greenfield Market", "Corner Grocer", "Bulk Barn",
          "Farmers Market", "Fresh Direct", "Asian Supermarket",
          "Butcher", "Baker", "Online Order", "Other"]

DIETS = ["None", "Vegetarian", "Vegan", "Pescatarian", "Gluten free",
         "Dairy free", "Nut free", "Halal", "Kosher", "Low FODMAP",
         "Keto", "Paleo", "Low sodium", "Diabetic friendly"]

STATUS = ["Planned", "Cooking", "Cooked", "Eaten", "Skipped", "Takeaway",
          "Eating out", "Leftover"]

RECIPE_CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert",
                     "Drink", "Side", "Sauce", "Base"]

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Lists",
        title="Lists",
        subtitle="Drop down sources - edit these and every planner, grocery "
                 "list and report follows",
        columns=[
            Col("meal_slot", "Meal slots", 18, "select",
                validate={"type": "list", "source": MEAL_SLOTS},
                note="Breakfast, lunch, dinner and the snacks in between."),
            Col("unit", "Units", 12, "select",
                validate={"type": "list", "source": UNITS},
                note="Measurement units used by recipes and the pantry."),
            Col("category", "Categories", 18, "select",
                validate={"type": "list", "source": CATEGORIES},
                note="Aisle / section of the shop."),
            Col("cuisine", "Cuisines", 18, "select",
                validate={"type": "list", "source": CUISINES},
                note="Used for variety reporting and rotation rules."),
            Col("tag", "Tags", 16, "select",
                validate={"type": "list", "source": TAGS},
                note="Recipe tags: quick, one pot, batch cook ..."),
            Col("store", "Stores", 20, "select",
                validate={"type": "list", "source": STORES},
                note="Where you shop. Also drives the store reports."),
            Col("diet", "Dietary needs", 18, "select",
                validate={"type": "list", "source": DIETS},
                note="Household dietary filters."),
            Col("status", "Status", 14, "select",
                validate={"type": "list", "source": STATUS},
                note="Meal plan status values."),
            Col("yes_no", "Yes / No", 10, "select",
                validate={"type": "list", "source": YES_NO}),
            Col("recipe_category", "Recipe categories", 18, "select",
                validate={"type": "list", "source": RECIPE_CATEGORIES},
                note="What kind of meal it is, as opposed to which aisle "
                     "the ingredients come from."),
        ],
        rows=cfg.row_count("Lists"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
        samples=[],
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec, sample_index=writer.samples.get("Lists"))
    writer.finish_sheet(ws, spec, links=["Dashboard", "Settings", "Recipes",
                                         "Grocery List", "Help"],
                        banding=False)
````

### `meal_planner_spreadsheet/sheets/settings.py`

Settings - the single control panel for the whole workbook *(239 lines)*

````python
"""
Settings - the single control panel for the whole workbook.

Household, planning year, currency, measurement system, grocery budget,
nutrition targets, reminder windows and habit targets.  Every other tab
reads these cells through named ranges (``Plan_Year``, ``Weekly_Budget``,
``Calorie_Target`` ...) so changing a number here re-shapes the entire
planner.

Row map (column B is the value):
    6  household name          24 calories target      33 expiry warning
    7  people in household     25 protein target        34 leftover days
    8  main cook               26 carbs target          35 freezer review
    9  planning year           27 fat target            36 low stock days
   10  servings per meal       28 fibre target          37 prep reminder
   11  week starts on          29 sugar limit           38 rotation gap
   12  measurement system      30 sodium limit          40 home cooked
   13  currency symbol         31 water target          41 new recipes
   14  currency code           33 expiry warning days   42 takeaway limit
   15  shopping day            34 leftover safe days    43 packed lunches
   16  meal prep day           35 freezer review days   44 waste target
   18  weekly budget           36 low stock days        45 top rows
   19  monthly budget          37 prep reminder days
   20  annual budget           38 rotation gap days
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

#: (row, setting label, value, note, number format style)
ROWS = [
    (5, "HOUSEHOLD", None, None, "section"),
    (6, "Household name", "household_name", "Shown on every print out.", "text"),
    (7, "People in the household", "household_size",
     "Drives servings, budget per person and the grocery quantities.",
     "number"),
    (8, "Main cook / planner", "cook", "Who owns the plan this year.", "text"),
    (9, "Planning year", "plan_year",
     "Every weekly and monthly plan is built around this year.", "number"),
    (10, "Servings per meal", "default_servings",
     "Default portion count copied into new plan rows.", "number"),
    (11, "Week starts on", "week_start", "Monday or Sunday.", "select"),
    (12, "Measurement system", "measurement_system",
     "Metric (g, ml) or Imperial (oz, fl oz).", "select"),
    (13, "Currency symbol", "currency_symbol", "Used in every money format.",
     "text"),
    (14, "Currency code", "currency_code", "Three letter code, e.g. USD.",
     "text"),
    (15, "Shopping day", "shopping_day", "Day you usually shop.", "select"),
    (16, "Meal prep day", "prep_day", "Day you usually cook ahead.",
     "select"),
    (17, "", None, None, "spacer"),
    (18, "GROCERY BUDGET", None, None, "section"),
    (19, "Weekly grocery budget", "weekly_budget",
     "Compared with the actual grocery spend on the Dashboard.", "money"),
    (20, "Monthly grocery budget", "monthly_budget", "", "money"),
    (21, "Annual grocery budget", "annual_budget", "", "money"),
    (22, "Eating out budget (monthly)", "eating_out_budget", "", "money"),
    (23, "Food waste cost target (monthly)", "waste_cost_target",
     "Money you are willing to write off as waste.", "money"),
    (24, "", None, None, "spacer"),
    (25, "DAILY NUTRITION TARGETS PER PERSON", None, None, "section"),
    (26, "Calories", "calorie_target", "kcal a day.", "number"),
    (27, "Protein", "protein_target", "grams a day.", "number"),
    (28, "Carbohydrates", "carb_target", "grams a day.", "number"),
    (29, "Fat", "fat_target", "grams a day.", "number"),
    (30, "Fibre", "fibre_target", "grams a day.", "number"),
    (31, "Sugar limit", "sugar_limit", "grams a day.", "number"),
    (32, "Sodium limit", "sodium_limit", "mg a day.", "number"),
    (33, "Water", "water_target", "glasses a day.", "number"),
    (34, "", None, None, "spacer"),
    (35, "REMINDER WINDOWS", None, None, "section"),
    (36, "Use it or lose it (days)", "expiry_warning_days",
     "Pantry items inside this window are flagged for use.", "number"),
    (37, "Leftover fridge life (days)", "leftover_safe_days", "", "number"),
    (38, "Freezer review (days)", "freezer_review_days",
     "How long before a freezer item is reviewed.", "number"),
    (39, "Low stock warning (days of cover)", "low_stock_days", "", "number"),
    (40, "Prep reminder (days ahead)", "prep_reminder_days", "", "number"),
    (41, "Rotation gap (days)", "rotation_gap_days",
     "Minimum days before the same meal is planned again.", "number"),
    (42, "", None, None, "spacer"),
    (43, "HABIT TARGETS", None, None, "section"),
    (44, "Home cooked meals a week", "home_cooked_target", "", "number"),
    (45, "New recipes a month", "new_recipe_target", "", "number"),
    (46, "Takeaways a month (limit)", "takeaway_limit", "", "number"),
    (47, "Packed lunches a week", "packed_lunch_target", "", "number"),
    (48, "Waste reduction target", "waste_reduction_target",
     "Share of food bought that you are aiming to bin.", "percent"),
    (49, "Top rows in 'best of' tables", "top_rows",
     "How many rows the Dashboard 'top 5' tables show.", "number"),
]

VALUE_ROW = {label_key: row for row, _, label_key, _, _ in ROWS
             if label_key}


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Settings",
        title="Settings",
        subtitle="Household, budget, nutrition targets and reminder windows",
        columns=[
            Col("setting", "Setting", 38, "text"),
            Col("value", "Value", 18, "text"),
            Col("note", "What it does", 52, "text_wrap"),
        ],
        rows=1,
        header_row=5,
        tab_color=Palette.primary,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    p, f = Palette, writer.fmt
    writer.grid_off(ws)
    ws.set_column(0, 0, 38)
    ws.set_column(1, 1, 20)
    ws.set_column(2, 2, 54)

    ws.set_row(0, 30)
    ws.set_row(1, 18)
    ws.merge_range(0, 0, 0, 2, "SETTINGS", f["title"])
    ws.merge_range(1, 0, 1, 2,
                   "Household, budget, nutrition targets and reminder "
                   "windows - every tab reads these cells", f["subtitle"])
    ws.merge_range(2, 0, 2, 2,
                   "  |  Dashboard   |   Weekly Planner   |   Budget   |   "
                   "Nutrition   |   Reports", f["nav"])

    # header row 5 (index 4)
    ws.set_row(4, 22)
    ws.write(4, 0, "Setting", f["header"])
    ws.write(4, 1, "Value", f["header"])
    ws.write(4, 2, "What it does", f["header"])

    style_for = {
        "text": f["input_text"],
        "number": f["input_number"],
        "money": f["input_money"],
        "percent": f["input_percent"],
        "select": f["input_select"],
        "section": f["section"],
        "spacer": f["label_soft"],
    }

    values = {
        "household_name": cfg.household.name,
        "household_size": cfg.members,
        "cook": cfg.household.cook,
        "plan_year": cfg.year,
        "default_servings": cfg.default_servings,
        "week_start": cfg.week_start,
        "measurement_system": cfg.measurement_system,
        "currency_symbol": cfg.currency_symbol,
        "currency_code": cfg.currency_code,
        "shopping_day": cfg.shopping_day,
        "prep_day": cfg.prep_day,
        "weekly_budget": cfg.weekly_food_budget,
        "monthly_budget": cfg.monthly_food_budget,
        "annual_budget": cfg.annual_food_budget,
        "eating_out_budget": cfg.eating_out_budget,
        "waste_cost_target": cfg.waste_cost_target,
        "calorie_target": cfg.calorie_target,
        "protein_target": cfg.protein_target,
        "carb_target": cfg.carb_target,
        "fat_target": cfg.fat_target,
        "fibre_target": cfg.fibre_target,
        "sugar_limit": cfg.sugar_limit,
        "sodium_limit": cfg.sodium_limit,
        "water_target": cfg.water_target,
        "expiry_warning_days": cfg.expiry_warning_days,
        "leftover_safe_days": cfg.leftover_safe_days,
        "freezer_review_days": cfg.freezer_review_days,
        "low_stock_days": cfg.low_stock_days,
        "prep_reminder_days": cfg.prep_reminder_days,
        "rotation_gap_days": cfg.rotation_gap_days,
        "home_cooked_target": cfg.home_cooked_target,
        "new_recipe_target": cfg.new_recipe_target,
        "takeaway_limit": cfg.takeaway_limit,
        "packed_lunch_target": cfg.packed_lunch_target,
        "waste_reduction_target": cfg.waste_reduction_target,
        "top_rows": cfg.top_rows,
    }

    for row, label, key, note, kind in ROWS:
        xrow = row - 1
        if kind == "section":
            ws.merge_range(xrow, 0, xrow, 2, label, f["section"])
            continue
        if kind == "spacer":
            ws.set_row(xrow, 6)
            continue
        ws.write(xrow, 0, label, f["label"])
        value = values.get(key)
        if isinstance(value, float):
            ws.write_number(xrow, 1, value, style_for[kind])
        elif isinstance(value, int):
            ws.write_number(xrow, 1, value, style_for[kind])
        else:
            ws.write_string(xrow, 1, str(value), style_for[kind])
        if note:
            ws.write(xrow, 2, note, f["note"])
        else:
            ws.write_blank(xrow, 2, None, f["note"])

    # drop downs for the pick-list style settings
    ws.data_validation(10, 1, 10, 1, {"validate": "list",
                                      "source": ["Monday", "Sunday"]})
    ws.data_validation(11, 1, 11, 1, {"validate": "list",
                                      "source": ["Metric", "Imperial"]})
    ws.data_validation(14, 1, 14, 1,
                       {"validate": "list",
                        "source": ["Monday", "Tuesday", "Wednesday",
                                   "Thursday", "Friday", "Saturday",
                                   "Sunday"]})
    ws.data_validation(15, 1, 15, 1,
                       {"validate": "list",
                        "source": ["Monday", "Tuesday", "Wednesday",
                                   "Thursday", "Friday", "Saturday",
                                   "Sunday"]})

    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_tab_color(Palette.primary)
    ws.hide_gridlines(2)
    ws.print_area(0, 0, 49, 2)
````

### `meal_planner_spreadsheet/sheets/household.py`

Household - who you are cooking for *(82 lines)*

````python
"""
Household - who you are cooking for.

One row per person.  The calorie and protein targets are pulled from
Settings and scaled by age, the dietary needs feed the Dietary Filters tab
and the servings column is what the planner multiplies recipes by.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

YES_NO = ["Yes", "No"]
ROLES = ["Adult", "Teenager", "Child", "Toddler", "Baby", "Guest",
         "Carer", "Pet"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("member", "Household member", 22, "text", group="who",
            note="Name or initials - whatever you will recognise."),
        Col("role", "Role", 12, "select",
            validate={"type": "list", "source": ROLES}),
        Col("age", "Age", 7, "number",
            validate={"type": "integer", "between": 0, "and": 120}),
        Col("diet", "Dietary need", 16, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "diet")}),
        Col("allergies", "Allergies", 22, "text",
            note="Free text. Anything listed here is checked against the "
                 "Dietary Filters tab."),
        Col("dislikes", "Dislikes", 22, "text"),
        Col("calorie_target", "Calories / day", 12, "calc",
            group="targets",
            formula='=IF({member}{r}="","",IF({age}{r}="",Calorie_Target,'
                    'IF({age}{r}<4,Calorie_Target*0.4,'
                    'IF({age}{r}<9,Calorie_Target*0.6,'
                    'IF({age}{r}<14,Calorie_Target*0.8,'
                    'IF({age}{r}<19,Calorie_Target*0.95,Calorie_Target))))))'),
        Col("protein_target", "Protein / day (g)", 13, "calc",
            formula='=IF({member}{r}="","",IF({age}{r}="",Protein_Target,'
                    'IF({age}{r}<4,Protein_Target*0.5,'
                    'IF({age}{r}<9,Protein_Target*0.65,'
                    'IF({age}{r}<14,Protein_Target*0.8,'
                    'IF({age}{r}<19,Protein_Target*0.9,Protein_Target))))))'),
        Col("servings", "Servings", 10, "number", group="planning",
            validate={"type": "decimal", "between": 0, "and": 20},
            note="Portions this person takes from a shared meal."),
        Col("packed_lunch", "Packed lunch", 12, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("notes", "Notes", 34, "text_wrap"),
        Col("status", "Status", 12, "calc",
            formula='=IF({member}{r}="","",'
                    'IF({allergies}{r}<>"","Allergy noted","OK"))'),
    ]

    spec = SheetSpec(
        name="Household",
        title="Household",
        subtitle="Who you cook for, what they eat and what they need each day",
        columns=columns,
        rows=cfg.row_count("Household"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Settings", "Dietary Filters", "Meal Plan", "Help"])
````

### `meal_planner_spreadsheet/sheets/recipes.py`

Recipes - the recipe book *(204 lines)*

````python
"""
Recipes - the recipe book.

Every recipe carries its timings, the nutrition per serving, the dietary
flags and a set of live rankings: cheapest, most protein, best match to the
household, and how overdue it is for another turn in the plan.  The cost
columns are pulled from the Recipe Ingredients tab, so add the ingredients
first and the costs appear on their own.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, unique_rank
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, unique_rank
    from writer import Writer

CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert", "Drink",
              "Side", "Sauce", "Base"]

CUISINES = ["Any", "Italian", "Mexican", "Indian", "Chinese", "Thai",
            "Japanese", "Mediterranean", "Middle Eastern", "French",
            "American", "British", "Caribbean", "African", "Vietnamese",
            "Korean", "Greek", "Spanish", "Turkish", "Moroccan"]

YES_NO = ["Yes", "No"]
SEASONS = ["Any", "Spring", "Summer", "Autumn", "Winter"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists_cat = registry.rng("Lists", "category")
    lists_cui = registry.rng("Lists", "cuisine")
    lists_yn = registry.rng("Lists", "yes_no")

    columns = [
        Col("recipe", "Recipe", 30, "text", group="basics",
            note="The recipe name. Spell it the same way everywhere else."),
        Col("category", "Category", 13, "select",
            validate={"type": "list",
                      "source": "=" + registry.rng("Lists",
                                                    "recipe_category")}),
        Col("cuisine", "Cuisine", 14, "select",
            validate={"type": "list", "source": "=" + lists_cui}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "integer", "between": 1, "and": 50},
            note="How many people this recipe feeds as written."),
        Col("prep_time", "Prep (min)", 10, "number",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("cook_time", "Cook (min)", 10, "number",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("total_time", "Total (min)", 10, "calc",
            formula='=IF({recipe}{r}="","",{prep_time}{r}+{cook_time}{r})'),
        Col("calories", "Calories", 10, "number", group="nutrition",
            note="Per serving."),
        Col("protein", "Protein (g)", 10, "number"),
        Col("carbs", "Carbs (g)", 10, "number"),
        Col("fat", "Fat (g)", 9, "number"),
        Col("fibre", "Fibre (g)", 9, "number"),
        Col("sugar", "Sugar (g)", 9, "number"),
        Col("sodium", "Sodium (mg)", 11, "number"),
        Col("ingredient_count", "Ingredients", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.recipe]],{recipe}{r}))'),
        Col("total_cost", "Total cost", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'SUMIFS([[Recipe Ingredients.line_cost]],'
                    '[[Recipe Ingredients.recipe]],{recipe}{r}))',
            group="cost"),
        Col("cost_per_serving", "Cost / serving", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=0,{servings}{r}=""),'
                    '"",{total_cost}{r}/{servings}{r})'),
        Col("cost_per_1000_cal", "Cost / 1000 kcal", 14, "calc",
            formula='=IF(OR({recipe}{r}="",{calories}{r}=0,'
                    '{calories}{r}=""),"",'
                    'IFERROR({cost_per_serving}{r}/{calories}{r}*1000,""))'),
        Col("calories_per_dollar", "kcal / $", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}="",'
                    '{cost_per_serving}{r}=0),"",'
                    'IFERROR({calories}{r}/{cost_per_serving}{r},""))'),
        Col("protein_per_dollar", "Protein / $", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}="",'
                    '{cost_per_serving}{r}=0),"",'
                    'IFERROR({protein}{r}/{cost_per_serving}{r},""))'),
        Col("prep_efficiency", "kcal / 10 min", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{total_time}{r}="",'
                    '{total_time}{r}=0),"",'
                    'IFERROR({calories}{r}/{total_time}{r}*10,""))'),
        Col("match_score", "Match score", 11, "calc", group="household fit",
            formula='=IF({recipe}{r}="","",'
                    '({vegetarian}{r}="Yes")*1+({vegan}{r}="Yes")*1'
                    '+({gluten_free}{r}="Yes")*1+({dairy_free}{r}="Yes")*1'
                    '+({nut_free}{r}="Yes")*1+({kid_friendly}{r}="Yes")*1)'),
        Col("times_planned", "Times cooked", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Cooked")'
                    '+COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Eaten"))'),
        Col("last_planned", "Last cooked", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(SUMPRODUCT(MAX(([[Meal Plan.recipe]]={recipe}{r})'
                    '*[[Meal Plan.date]]))=0,"",'
                    'SUMPRODUCT(MAX(([[Meal Plan.recipe]]={recipe}{r})'
                    '*[[Meal Plan.date]]))))'),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    'TODAY()-{last_planned}{r})'),
        Col("rotation_ok", "Rotation", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({days_since}{r}="","Yes",'
                    'IF({days_since}{r}>=Rotation_Gap_Days,"Yes","No")))'),
        Col("plan_flag", "Plan flag", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({rotation_ok}{r}="No","Too soon",'
                    'IF(AND({rating}{r}<>"",{rating}{r}>=4),"Plan it",'
                    '"Available")))'),
        Col("favourite", "Favourite", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn},
            group="flags"),
        Col("vegetarian", "Vegetarian", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("vegan", "Vegan", 9, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("gluten_free", "Gluten free", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("dairy_free", "Dairy free", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("nut_free", "Nut free", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("kid_friendly", "Kid friendly", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("batch_friendly", "Batch cook", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("freezer_friendly", "Freezer", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("quick_meal", "Quick (30 min)", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({total_time}{r}<=30,"Yes","No"))'),
        Col("seasonal", "Season", 11, "select",
            validate={"type": "list", "source": SEASONS}),
        Col("added_on", "Added on", 12, "date",
            note="When you added the recipe - used by the 'new recipes "
                 "tried' counter."),
        Col("rating", "Rating (1-5)", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 5},
            group="notes"),
        Col("source", "Source", 20, "text"),
        Col("url", "Link", 20, "text"),
        Col("tags", "Tags", 26, "text"),
        Col("notes", "Notes", 40, "text_wrap"),
        # ---- rankings -----------------------------------------------------
        Col("calories_rank", "Calorie rank", 11, "calc", group="rankings",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({calories_first}:{calories_last},'
                    '">"&{calories}{r})+1)'),
        Col("protein_rank", "Protein rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({protein_first}:{protein_last},'
                    '">"&{protein}{r})+1)'),
        Col("fibre_rank", "Fibre rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({fibre_first}:{fibre_last},'
                    '">"&{fibre}{r})+1)'),
        Col("cost_rank", "Cost rank", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'COUNTIFS({cost_per_serving_first}:'
                    '{cost_per_serving_last},"<"&{cost_per_serving}{r})+1)'),
        Col("match_rank", "Match rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({match_score_first}:{match_score_last},'
                    '">"&{match_score}{r})+1)'),
        Col("rotation_rank", "Rotation rank", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '"<"&{days_since}{r})+1)'),
        Col("times_planned_rank", "Popularity rank", 13, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({times_planned_first}:{times_planned_last},'
                    '">"&{times_planned}{r})+1)'),
    ]

    spec = SheetSpec(
        name="Recipes",
        title="Recipes",
        subtitle="Your recipe book - timings, nutrition per serving, cost "
                 "and live rankings",
        columns=columns,
        rows=cfg.row_count("Recipes"),
        tab_color=Palette.primary,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipe Ingredients", "Ingredients", "Weekly Planner",
        "Meal Plan", "Recipe Costs", "Rotation", "Help"])
````

### `meal_planner_spreadsheet/sheets/recipe_ingredients.py`

Recipe Ingredients - what goes into each recipe, and what it costs *(161 lines)*

````python
"""
Recipe Ingredients - what goes into each recipe, and what it costs.

One row per ingredient per recipe.  The price, category, store and
nutrition are looked up from the Ingredients tab by name, so the cost per
serving on the Recipes tab is always live: change a price once and every
recipe that uses it re-prices itself.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    recipes = registry.rng("Recipes", "recipe")
    units = registry.rng("Lists", "unit")
    ing_name = registry.rng("Ingredients", "ingredient")

    def ing(key: str) -> str:
        return registry.rng("Ingredients", key)

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick the recipe this ingredient belongs to."),
        Col("ingredient", "Ingredient", 26, "text",
            validate={"type": "list", "source": "=" + ing_name},
            note="Must match a name on the Ingredients tab exactly."),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + units}),
        Col("category", "Category", 16, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("store", "Best store", 16, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("store")) + ")"),
        Col("price", "Price / unit", 11, "calc", group="cost",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("line_cost", "Line cost", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*{price}{r},""))'),
        Col("servings", "Recipe servings", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             registry.rng("Recipes", "servings")) + ")"),
        Col("cost_per_serving", "Cost / serving", 12, "calc",
            formula='=IF(OR({line_cost}{r}="",{servings}{r}="",'
                    '{servings}{r}=0),"",'
                    'IFERROR({line_cost}{r}/{servings}{r},""))'),
        Col("calories", "Calories", 10, "calc", group="nutrition",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("calories_per_unit")) + ',""))'),
        Col("protein", "Protein (g)", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("protein_per_unit")) + ',""))'),
        Col("carbs", "Carbs (g)", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("carbs_per_unit")) + ',""))'),
        Col("fat", "Fat (g)", 9, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("fat_per_unit")) + ',""))'),
        Col("fibre", "Fibre (g)", 9, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("fibre_per_unit")) + ',""))'),
        Col("share_of_recipe_cost", "Share of cost", 12, "calc",
            formula='=IF(OR({line_cost}{r}="",{recipe}{r}=""),"",'
                    'IFERROR({line_cost}{r}/SUMIFS('
                    '[[Recipe Ingredients.line_cost]],'
                    '[[Recipe Ingredients.recipe]],{recipe}{r}),""))'),
        Col("cost_rank", "Cost rank", 10, "calc",
            formula='=IF({line_cost}{r}="","",'
                    'COUNTIFS({line_cost_first}:{line_cost_last},'
                    '">"&{line_cost}{r})+1)'),
        Col("in_pantry", "In pantry", 10, "calc", group="pantry",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{ingredient}{r}))'),
        Col("shortfall", "To buy", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'MAX(0,{quantity}{r}-{in_pantry}{r}))'),
        Col("pack_size", "Pack size", 10, "number", group="packs",
            validate={"type": "decimal", "between": 0, "and": 100000},
            note="Size of the pack you buy, in the same unit as the "
                 "quantity."),
        Col("pack_cost", "Pack cost", 11, "calc",
            formula='=IF(OR({pack_size}{r}="",{pack_size}{r}=0,'
                    '{price}{r}=""),"",{pack_size}{r}*{price}{r})'),
        Col("packs_needed", "Packs needed", 12, "calc",
            formula='=IF(OR({shortfall}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",CEILING({shortfall}{r}/'
                    '{pack_size}{r},1))'),
        Col("organic", "Organic", 9, "select",
            validate={"type": "list", "source": YES_NO}),
        Col("waste_factor", "Waste %", 9, "percent",
            validate={"type": "decimal", "between": 0, "and": 1},
            note="Peel, trim and spillage as a share of the quantity."),
        Col("effective_qty", "Qty incl. waste", 12, "calc",
            formula='=IF(OR({quantity}{r}="",{waste_factor}{r}=""),"",'
                    '{quantity}{r}*(1+{waste_factor}{r}))'),
        Col("staple", "Staple", 9, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("staple")) + ")"),
        Col("status", "Status", 14, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({in_pantry}{r}>={quantity}{r},"In pantry",'
                    '"To buy"))'),
        Col("line_no", "Line in recipe", 11, "calc", group="order",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({recipe_first}:{recipe}{r},{recipe}{r}))'),
        Col("filter_flag", "Diet check", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(COUNTIFS([[Dietary Filters.exclude]],'
                    '{ingredient}{r})>0,"Check","OK"))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Recipe Ingredients",
        title="Recipe Ingredients",
        subtitle="One row per ingredient per recipe - the cost engine behind "
                 "every recipe",
        columns=columns,
        rows=cfg.row_count("Recipe Ingredients"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Ingredients", "Recipe Costs", "Help"])
````

### `meal_planner_spreadsheet/sheets/ingredients.py`

Ingredients - the master list of everything you buy *(191 lines)*

````python
"""
Ingredients - the master list of everything you buy.

Price and nutrition live here once and are looked up by name from the Recipe
Ingredients tab, so a single price change re-prices every recipe that uses
the ingredient.  The right hand columns watch stock, spend and waste: what
is running low, what you bought last, how the price is moving and which
ingredients you throw away most.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]
SEASONS = ["Any", "Spring", "Summer", "Autumn", "Winter"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_item = lists("Grocery Spending", "item")
    gs_price = lists("Grocery Spending", "price")
    gs_date = lists("Grocery Spending", "date")
    fw_item = lists("Food Waste", "item")
    fw_qty = lists("Food Waste", "qty")

    columns = [
        Col("ingredient", "Ingredient", 26, "text", group="basics",
            note="The name used everywhere else. Keep the spelling "
                 "identical on every tab."),
        Col("category", "Category", 16, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "category")}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists", "unit")},
            note="The unit the price and the nutrition are quoted in."),
        Col("price", "Price / unit", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("store", "Usual store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_per_unit", "Price per unit", 12, "calc",
            formula='=IF(OR({price}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",{price}{r}/{pack_size}{r})'),
        Col("calories_per_unit", "Calories / unit", 12, "number",
            group="nutrition"),
        Col("protein_per_unit", "Protein / unit", 12, "number"),
        Col("carbs_per_unit", "Carbs / unit", 11, "number"),
        Col("fat_per_unit", "Fat / unit", 10, "number"),
        Col("fibre_per_unit", "Fibre / unit", 11, "number"),
        Col("shelf_life_days", "Shelf life (days)", 12, "number",
            validate={"type": "integer", "between": 0, "and": 3650},
            note="Used to work out expiry dates on the Pantry tab."),
        Col("storage", "Storage", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("staple", "Staple", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")},
            note="Yes = you buy it every week, so it is re-added to the "
                 "grocery list automatically."),
        Col("organic", "Organic", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("seasonal", "Season", 11, "select",
            validate={"type": "list", "source": SEASONS}),
        Col("allergens", "Allergens", 18, "text",
            note="Free text: nuts, dairy, gluten ..."),
        Col("in_pantry", "In pantry", 10, "calc", group="stock",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{ingredient}{r}))'),
        Col("on_grocery_list", "On list", 9, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS([[Grocery List.item]],{ingredient}{r},'
                    '[[Grocery List.buy]],"Yes"))'),
        Col("weekly_need", "Needed this week", 13, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Grocery List.needed]],'
                    '[[Grocery List.item]],{ingredient}{r}))'),
        Col("recipe_count", "Used in recipes", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{ingredient}{r}))'),
        Col("total_qty_used", "Qty used in recipes", 13, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Recipe Ingredients.quantity]],'
                    '[[Recipe Ingredients.ingredient]],{ingredient}{r}))'),
        Col("weeks_of_stock", "Weeks of stock", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({weekly_need}{r}<=0,IF({in_pantry}{r}>0,99,0),'
                    'ROUND({in_pantry}{r}/{weekly_need}{r},1)))'),
        Col("need_score", "Need score", 11, "calc", group="buying",
            formula='=IF({ingredient}{r}="","",'
                    '{weekly_need}{r}*10'
                    '+IF({staple}{r}="Yes",5,0)'
                    '+IF({weeks_of_stock}{r}<1,10,0)'
                    '+IF({in_pantry}{r}<=0,3,0))'),
        Col("need_rank", "Need rank", 10, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS({need_score_first}:{need_score_last},'
                    '">"&{need_score}{r})+1)'),
        Col("buy_this_week", "Buy this week", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(OR({weekly_need}{r}>0,'
                    'AND({staple}{r}="Yes",{weeks_of_stock}{r}<2)),'
                    '"Yes","No"))'),
        Col("value_in_pantry", "Pantry value", 12, "calc",
            formula='=IF(OR({ingredient}{r}="",{price}{r}=""),"",'
                    '{in_pantry}{r}*{price}{r})'),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({value_in_pantry}{r}="","",'
                    'COUNTIFS({value_in_pantry_first}:'
                    '{value_in_pantry_last},">"&{value_in_pantry}{r})+1)'),
        Col("waste_qty", "Wasted qty", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS(' + fw_qty + ',' + fw_item + ','
                    '{ingredient}{r}))'),
        Col("waste_rank", "Waste rank", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{waste_qty}{r}=0),"",'
                    'COUNTIFS({waste_qty_first}:{waste_qty_last},'
                    '">"&{waste_qty}{r})+1)'),
        Col("last_purchased", "Last bought", 12, "calc", group="prices",
            formula='=IF({ingredient}{r}="","",'
                    'IF(SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_date + '))=0,"",'
                    'SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_date + '))))'),
        Col("last_price", "Last price", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{last_purchased}{r}=""),"",'
                    'IFERROR(AVERAGEIFS(' + gs_price + ',' + gs_item + ','
                    '{ingredient}{r},' + gs_date + ','
                    '{last_purchased}{r}),""))'),
        Col("avg_price", "Average price", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IFERROR(AVERAGEIFS(' + gs_price + ',' + gs_item + ','
                    '{ingredient}{r}),""))'),
        Col("min_price", "Lowest price", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(SUMPRODUCT(MIN((' + gs_item + '={ingredient}{r})*'
                    + gs_price + '+(' + gs_item + '<>{ingredient}{r})'
                    '*1000000))>=1000000,"",'
                    'SUMPRODUCT(MIN((' + gs_item + '={ingredient}{r})*'
                    + gs_price + '+(' + gs_item + '<>{ingredient}{r})'
                    '*1000000))))'),
        Col("max_price", "Highest price", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_price + ')))'),
        Col("price_spread", "Price spread", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{min_price}{r}="",'
                    '{max_price}{r}=0),"",{max_price}{r}-{min_price}{r})'),
        Col("price_change", "Change vs average", 13, "calc",
            formula='=IF(OR({ingredient}{r}="",{last_price}{r}="",'
                    '{avg_price}{r}=""),"",{last_price}{r}-{avg_price}{r})'),
        Col("price_trend", "Trend", 10, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({price_change}{r}="","",'
                    'IF({price_change}{r}>0.01,"Up",'
                    'IF({price_change}{r}<-0.01,"Down","Flat"))))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Ingredients",
        title="Ingredients",
        subtitle="Everything you buy, with price, nutrition, stock and spend "
                 "in one place",
        columns=columns,
        rows=cfg.row_count("Ingredients"),
        tab_color=Palette.primary,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Recipe Ingredients", "Pantry",
        "Grocery List", "Store Prices", "Help"])
````

### `meal_planner_spreadsheet/sheets/meal_plan.py`

Meal Plan - the engine of the workbook *(168 lines)*

````python
"""
Meal Plan - the engine of the workbook.

One row per planned meal.  Pick a date, a meal slot and a recipe and the
row works out the nutrition, the cost, how it compares with the rest of
that day, whether the meal is too soon after the last time you had it and
whether it trips one of the household dietary filters.

Everything the Weekly Planner, the Grocery List, the Nutrition log and the
Reports tab show is read from here.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup, rank_desc
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup, rank_desc
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")
    ri_recipe = lists("Recipe Ingredients", "recipe")
    ri_flag = lists("Recipe Ingredients", "filter_flag")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    columns = [
        Col("plan_id", "Plan ID", 11, "text", group="plan",
            note="Anything you like - 'W34-D1' is a good pattern."),
        Col("date", "Date", 12, "date",
            validate={"type": "date", "operator": "between",
                      "minimum": "DATE(2000,1,1)",
                      "maximum": "DATE(2100,12,31)"}),
        Col("week_start", "Week starting", 12, "calc",
            formula='=IF({date}{r}="","",{date}{r}-WEEKDAY({date}{r},2)+1)'),
        Col("weekday", "Day", 8, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"ddd"))'),
        Col("month", "Month", 11, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("slot", "Meal slot", 15, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "meal_slot")}),
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100},
            note="How many portions to cook. Leave blank to cook the "
                 "recipe as written."),
        Col("recipe_servings", "Recipe servings", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("servings")) + ")"),
        Col("scale", "Scale", 8, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}="",'
                    '{recipe_servings}{r}="",{recipe_servings}{r}=0),"",'
                    '{servings}{r}/{recipe_servings}{r})'),
        Col("cook_for", "Cook for", 9, "calc",
            formula='=IF({date}{r}="","",Household_Size)'),
        Col("calories", "Calories", 10, "calc", group="nutrition",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("calories"))
                    + '*{servings}{r},""))'),
        Col("protein", "Protein (g)", 10, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("protein"))
                    + '*{servings}{r},""))'),
        Col("carbs", "Carbs (g)", 10, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("carbs"))
                    + '*{servings}{r},""))'),
        Col("fat", "Fat (g)", 9, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fat"))
                    + '*{servings}{r},""))'),
        Col("fibre", "Fibre (g)", 9, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fibre"))
                    + '*{servings}{r},""))'),
        Col("cost", "Cost", 11, "calc", group="cost",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("cost_per_serving"))
                    + '*{servings}{r},""))'),
        Col("slot_budget", "Budget / meal", 11, "calc",
            formula='=IF({slot}{r}="","",Weekly_Budget/21)'),
        Col("status", "Status", 13, "select", group="tracking",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "status")}),
        Col("cooked", "Cooked", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("rating", "Rating (1-5)", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 5}),
        Col("leftover_of", "Leftover of", 20, "text",
            note="If this meal is leftovers, name the recipe they came "
                 "from."),
        Col("leftover_id", "Leftover ID", 12, "text"),
        Col("waste_qty", "Waste (portions)", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("prep_task", "Prep task", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(COUNTIFS([[Meal Prep.recipe]],{recipe}{r})>0,'
                    '"Yes","No"))'),
        Col("shopping_items", "Ingredients", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS(' + ri_recipe + ',{recipe}{r}))'),
        Col("notes", "Notes", 30, "text_wrap"),
        # ---- live rankings -------------------------------------------------
        Col("day_cost_rank", "Cost rank (day)", 12, "calc", group="rankings",
            formula='=IF(OR({date}{r}="",{cost}{r}=""),"",'
                    'COUNTIFS({date_first}:{date_last},{date}{r},'
                    '{cost_first}:{cost_last},">"&{cost}{r})+1)'),
        Col("day_calorie_rank", "Calorie rank (day)", 13, "calc",
            formula='=IF(OR({date}{r}="",{calories}{r}=""),"",'
                    'COUNTIFS({date_first}:{date_last},{date}{r},'
                    '{calories_first}:{calories_last},'
                    '">"&{calories}{r})+1)'),
        Col("repeat_flag", "Repeat", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(COUNTIFS({recipe_first}:{recipe_last},'
                    '{recipe}{r})>1,"Repeat","Once"))'),
        Col("days_since", "Days since last", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(' + lookup("{recipe}{r}", recipes,
                                   rec("last_planned")) + '="","",'
                    'IFERROR({date}{r}-' + lookup("{recipe}{r}", recipes,
                                                  rec("last_planned"))
                    + ',"")))'),
        Col("rotation_ok", "Rotation", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({days_since}{r}="","Yes",'
                    'IF({days_since}{r}>=Rotation_Gap_Days,"Yes","No")))'),
        Col("allergy_flag", "Diet check", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(COUNTIFS(' + ri_recipe + ',{recipe}{r},' + ri_flag
                    + ',"Check")>0,"Check","OK"))'),
    ]

    spec = SheetSpec(
        name="Meal Plan",
        title="Meal Plan",
        subtitle="Every planned meal - nutrition, cost, rotation and dietary "
                 "checks",
        columns=columns,
        rows=cfg.row_count("Meal Plan"),
        tab_color=Palette.primary,
        freeze_cols=3,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Weekly Planner", "Monthly Planner", "Grocery List",
        "Nutrition", "Reports", "Help"])
````

### `meal_planner_spreadsheet/sheets/grocery_list.py`

Grocery List - the shopping list that writes itself *(140 lines)*

````python
"""
Grocery List - the shopping list that writes itself.

Every planned meal is copied here by the Meal Plan tab, the quantities are
scaled to the household and reduced by what is already in the pantry, and
the list is grouped by aisle with a priority, a pack count and a running
total.  Tick items off as you fill the basket and the bought price is
compared with the planned price.

The last rows are the weekly staples: anything flagged as a staple on the
Ingredients tab is re-added automatically when stock runs low.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("item", "Item", 26, "text", group="what",
            note="Must match an ingredient name on the Ingredients tab."),
        Col("category", "Aisle / category", 17, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("aisle", "Aisle", 16, "text",
            note="Your shop's aisle, so the printed list walks the store "
                 "in order."),
        Col("price", "Price / unit", 11, "calc", group="money",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("line_total", "Line total", 11, "calc",
            formula='=IF(OR({item}{r}="",{quantity}{r}="",'
                    '{price}{r}=""),"",{quantity}{r}*{price}{r})'),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("packs", "Packs", 9, "calc",
            formula='=IF(OR({quantity}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",CEILING({quantity}{r}/'
                    '{pack_size}{r},1))'),
        Col("pack_total", "Pack total", 11, "calc",
            formula='=IF(OR({packs}{r}="",{pack_size}{r}="",'
                    '{price}{r}=""),"",{packs}{r}*{pack_size}{r}*'
                    '{price}{r})'),
        Col("in_pantry", "In pantry", 10, "calc", group="stock",
            formula='=IF({item}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{item}{r}))'),
        Col("needed", "Still needed", 11, "calc",
            formula='=IF(OR({item}{r}="",{quantity}{r}=""),"",'
                    'MAX(0,{quantity}{r}-{in_pantry}{r}))'),
        Col("buy", "Buy", 8, "select", group="shopping",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bought", "Bought", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bought_date", "Bought on", 12, "date"),
        Col("bought_price", "Price paid", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_diff", "Vs planned", 11, "calc",
            formula='=IF(OR({bought_price}{r}="",{line_total}{r}=""),"",'
                    '{bought_price}{r}-{line_total}{r})'),
        Col("need_rank", "Need rank", 10, "calc", group="rankings",
            formula='=IF({needed}{r}="","",'
                    'COUNTIFS({needed_first}:{needed_last},'
                    '">"&{needed}{r})+1)'),
        Col("sort_key", "Sort key", 9, "calc",
            formula='=IF({line_total}{r}="","",'
                    '{line_total}{r}+ROW()/1000000)'),
        Col("buy_rank", "Buy rank", 10, "calc",
            formula='=IF(OR({buy}{r}<>"Yes",{sort_key}{r}=""),"",'
                    'COUNTIFS({buy_first}:{buy_last},"Yes",'
                    '{sort_key_first}:{sort_key_last},'
                    '"<"&{sort_key}{r})+1)'),
        Col("priority", "Priority", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({bought}{r}="Yes","Bought",'
                    'IF({needed}{r}<=0,"Have it",'
                    'IF({buy}{r}<>"Yes","Skip",'
                    'IF({need_rank}{r}<=10,"Must have","Nice to have")))))'),
        Col("week_start", "Week starting", 12, "date",
            note="Which week this line belongs to."),
        Col("linked_recipe", "From recipe", 22, "calc",
            formula='=IF({item}{r}="","",'
                    'IFERROR(INDEX([[Recipe Ingredients.recipe]],'
                    'MATCH({item}{r},'
                    '[[Recipe Ingredients.ingredient]],0)),""))'),
        Col("staple_flag", "Staple", 9, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("staple")) + ")"),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({bought}{r}="Yes","Bought",'
                    'IF({buy}{r}="Yes","To buy","Not needed")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Grocery List",
        title="Grocery List",
        subtitle="The automatic shopping list - grouped by aisle, priced, "
                 "and reduced by what you already have",
        columns=columns,
        rows=cfg.row_count("Grocery List"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Meal Plan", "Weekly Planner", "Pantry", "Staples",
        "Print Shopping", "Grocery Spending", "Help"])
````

### `meal_planner_spreadsheet/sheets/pantry.py`

Pantry - what you have, what is running low, what expires next *(148 lines)*

````python
"""
Pantry - what you have, what is running low, what expires next.

Enter an item, the quantity and the date you bought or opened it.  The
shelf life is looked up from the Ingredients tab, so the expiry date, the
days left and the "use it or lose it" flag all appear on their own, and
anything inside the window you set on Settings rises to the top of the
fridge and freezer rankings.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("item", "Item", 24, "text", group="what",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("storage", "Storage", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("purchase_date", "Bought", 12, "date", group="dates"),
        Col("opened_date", "Opened", 12, "date",
            note="Fill this in when you open a jar or a pack."),
        Col("shelf_life_days", "Shelf life (days)", 12, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("shelf_life_days")) + ")"),
        Col("expiry_date", "Use by", 12, "calc",
            formula='=IF(OR({item}{r}="",{shelf_life_days}{r}=""),"",'
                    'IF({opened_date}{r}<>"",'
                    '{opened_date}{r}+{shelf_life_days}{r},'
                    'IF({purchase_date}{r}<>"",'
                    '{purchase_date}{r}+{shelf_life_days}{r},"")))'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({item}{r}="",{expiry_date}{r}=""),"",'
                    '{expiry_date}{r}-TODAY())'),
        Col("use_by_status", "Use by status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({days_left}{r}="","No date",'
                    'IF({days_left}{r}<0,"Expired",'
                    'IF({days_left}{r}<=Expiry_Warning_Days,"Use soon",'
                    '"Fresh"))))'),
        Col("recipe_uses", "Used in recipes", 12, "calc", group="use",
            formula='=IF({item}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{item}{r}))'),
        Col("weeks_of_stock", "Weeks of stock", 12, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("weeks_of_stock")) + ")"),
        Col("reorder_qty", "Reorder qty", 11, "calc",
            formula='=IF(OR({item}{r}="",{weeks_of_stock}{r}=""),"",'
                    'IF({weeks_of_stock}{r}<1,'
                    'MAX(0,1*IFERROR(' + lookup(
                        "{item}{r}", ing("ingredient"),
                        ing("weekly_need")) + ',0)-{quantity}{r}),0))'),
        Col("low_stock", "Stock level", 11, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({weeks_of_stock}{r}="","",'
                    'IF({weeks_of_stock}{r}<1,"Low","OK")))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({item}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ',""))'),
        Col("fridge_rank", "Fridge rank", 10, "calc", group="rankings",
            formula='=IF(OR({storage}{r}<>"Fridge",{days_left}{r}=""),"",'
                    'SUMPRODUCT(({storage_first}:{storage_last}="Fridge")*'
                    '({days_left_first}:{days_left_last}<'
                    '{days_left}{r}))'
                    '+SUMPRODUCT(({storage_first}:{storage_last}="Fridge")*'
                    '({days_left_first}:{days_left_last}='
                    '{days_left}{r})*(ROW({days_left_first}:'
                    '{days_left_last})<ROW()))+1)'),
        Col("freezer_rank", "Freezer rank", 11, "calc",
            formula='=IF(OR({storage}{r}<>"Freezer",{days_left}{r}=""),"",'
                    'SUMPRODUCT(({storage_first}:{storage_last}="Freezer")*'
                    '({days_left_first}:{days_left_last}<'
                    '{days_left}{r}))'
                    '+SUMPRODUCT(({storage_first}:{storage_last}="Freezer")*'
                    '({days_left_first}:{days_left_last}='
                    '{days_left}{r})*(ROW({days_left_first}:'
                    '{days_left_last})<ROW()))+1)'),
        Col("batch", "Batch / lot", 14, "text", group="detail"),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("price_paid", "Price paid", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("frozen", "Frozen", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("portion", "Portion", 14, "text",
            note="e.g. 2 portions, half a tub."),
        Col("servings_left", "Servings left", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({use_by_status}{r}="Expired","Bin it",'
                    'IF({use_by_status}{r}="Use soon","Cook it",'
                    'IF({low_stock}{r}="Low","Running low","Keep"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Pantry",
        title="Pantry",
        subtitle="What you have in the cupboard, fridge and freezer - with "
                 "use-by dates",
        columns=columns,
        rows=cfg.row_count("Pantry"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Ingredients", "Grocery List", "Leftovers",
        "Fridge & Freezer", "Food Waste", "Help"])
````

### `meal_planner_spreadsheet/sheets/staples.py`

Staples - the things you buy every single week *(112 lines)*

````python
"""
Staples - the things you buy every single week.

Add your bread, milk, eggs, coffee and pasta here with how often you buy
them.  When a staple is due, or the pantry drops below a week of cover, it
is flagged so it never gets forgotten on the grocery list.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("staple", "Staple", 24, "text", group="what",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({staple}{r}="","",'
                    + lookup("{staple}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("usual_unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("usual_qty", "Usual quantity", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100000},
            note="How much you buy each time."),
        Col("last_bought", "Last bought", 12, "date", group="rhythm"),
        Col("buy_interval_days", "Buy every (days)", 12, "number",
            validate={"type": "integer", "between": 1, "and": 365}),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({staple}{r}="",{last_bought}{r}=""),"",'
                    'TODAY()-{last_bought}{r})'),
        Col("due", "Due", 9, "calc",
            formula='=IF(OR({staple}{r}="",{days_since}{r}="",'
                    '{buy_interval_days}{r}=""),"",'
                    'IF({days_since}{r}>={buy_interval_days}{r},"Yes",'
                    '"No"))'),
        Col("auto_add", "Auto add", 10, "select", group="behaviour",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")},
            note="Yes = this staple is added to the grocery list whenever "
                 "it is due."),
        Col("qty_to_add", "Quantity to add", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("avg_price", "Average price", 12, "calc", group="prices",
            formula='=IF({staple}{r}="","",'
                    'IFERROR(AVERAGEIFS([[Grocery Spending.price]],'
                    '[[Grocery Spending.item]],{staple}{r}),""))'),
        Col("last_price", "Last price", 11, "calc",
            formula='=IF({staple}{r}="","",'
                    'IFERROR(AVERAGEIFS([[Grocery Spending.price]],'
                    '[[Grocery Spending.item]],{staple}{r},'
                    '[[Grocery Spending.date]],'
                    'SUMPRODUCT(MAX(([[Grocery Spending.item]]='
                    '{staple}{r})*[[Grocery Spending.date]]))),""))'),
        Col("price_delta", "Vs average", 11, "calc",
            formula='=IF(OR({staple}{r}="",{last_price}{r}="",'
                    '{avg_price}{r}=""),"",{last_price}{r}-{avg_price}{r})'),
        Col("pantry_qty", "In pantry", 10, "calc", group="stock",
            formula='=IF({staple}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{staple}{r}))'),
        Col("on_list", "On list", 9, "calc",
            formula='=IF({staple}{r}="","",'
                    'COUNTIFS([[Grocery List.item]],{staple}{r}))'),
        Col("rank", "Urgency rank", 12, "calc", group="rankings",
            formula='=IF(OR({staple}{r}="",{days_since}{r}=""),"",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '">"&{days_since}{r})+1)'),
        Col("status", "Status", 14, "calc",
            formula='=IF({staple}{r}="","",'
                    'IF({due}{r}="Yes","Buy this week",'
                    'IF({pantry_qty}{r}<=0,"Out of stock","In stock")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Staples",
        title="Staples",
        subtitle="The weekly basics, with a buy-by rhythm so nothing gets "
                 "forgotten",
        columns=columns,
        rows=cfg.row_count("Staples"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Grocery List", "Ingredients", "Help"])
````

### `meal_planner_spreadsheet/sheets/leftovers.py`

Leftovers - the queue of cooked food waiting to be eaten *(107 lines)*

````python
"""
Leftovers - the queue of cooked food waiting to be eaten.

Batch cooking only pays off if the portions get eaten.  Log each batch, say
whether it is in the fridge or the freezer and the sheet works out both
expiry dates, the days left and the order to eat them in.  The queue rank
always puts the most urgent portion first.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

STORAGE = ["Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    columns = [
        Col("leftover_id", "Batch ID", 11, "text", group="what",
            note="Anything you like - 'LO-01' is a good pattern."),
        Col("item", "What it is", 26, "text"),
        Col("recipe", "From recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("cooked_date", "Cooked", 12, "date"),
        Col("portions", "Portions", 9, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("storage", "Storage", 10, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("fridge_expiry", "Fridge use by", 12, "calc", group="dates",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    '{cooked_date}{r}+Leftover_Safe_Days)'),
        Col("freezer_expiry", "Freezer use by", 12, "calc",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    '{cooked_date}{r}+Freezer_Review_Days)'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    'IF({storage}{r}="Freezer",'
                    '{freezer_expiry}{r}-TODAY(),'
                    '{fridge_expiry}{r}-TODAY()))'),
        Col("status", "Status", 14, "calc",
            formula='=IF({leftover_id}{r}="","",'
                    'IF({thrown}{r}="Yes","Binned",'
                    'IF({used_up}{r}="Yes","Eaten",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Past its best",'
                    'IF({days_left}{r}<=1,"Eat today",'
                    'IF({days_left}{r}<=3,"Eat this week",'
                    '"Keep")))))))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({leftover_id}{r}="",{portions}{r}=""),"",'
                    'IFERROR({portions}{r}*'
                    + lookup("{recipe}{r}", recipes,
                             lists("Recipes", "cost_per_serving"))
                    + ',""))'),
        Col("queue_rank", "Queue rank", 10, "calc", group="rankings",
            formula='=IF(OR({leftover_id}{r}="",{days_left}{r}=""),"",'
                    'COUNTIFS({days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("use_by_flag", "Flag", 12, "calc",
            formula='=IF({leftover_id}{r}="","",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Bin it",'
                    'IF({days_left}{r}<=Expiry_Warning_Days,'
                    '"Use it or lose it",""))))'),
        Col("portions_left", "Portions left", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("used_up", "Eaten up", 10, "select", group="tracking",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("thrown", "Binned", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("container", "Container", 14, "text"),
        Col("reheats", "Reheats left", 11, "number",
            validate={"type": "integer", "between": 0, "and": 5}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Leftovers",
        title="Leftovers",
        subtitle="Batch cooked portions and when to eat them",
        columns=columns,
        rows=cfg.row_count("Leftovers"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Fridge & Freezer", "Meal Prep", "Food Waste",
        "Pantry", "Help"])
````

### `meal_planner_spreadsheet/sheets/food_waste.py`

Food Waste - what got thrown away, why, and what it cost *(109 lines)*

````python
"""
Food Waste - what got thrown away, why, and what it cost.

Logging waste is the fastest way to cut a food bill.  Each row prices the
wasted quantity from the Ingredients tab, ranks it against everything else
you have binned and shows how much of the month's waste it represents.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

REASONS = ["Expired", "Spoiled", "Mouldy", "Leftover not eaten",
           "Cooked too much", "Burnt", "Tasted bad", "Bought too much",
           "Child refused", "Plans changed"]
STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("waste_id", "Waste ID", 11, "text", group="what",
            note="Anything you like - 'W-01' is a good pattern."),
        Col("date", "Date", 12, "date"),
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab so the cost can "
                 "be looked up."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("qty", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("unit_price", "Price / unit", 11, "calc", group="money",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("cost", "Cost binned", 11, "calc",
            formula='=IF(OR({item}{r}="",{qty}{r}="",'
                    '{unit_price}{r}=""),"",{qty}{r}*{unit_price}{r})'),
        Col("reason", "Reason", 20, "select",
            validate={"type": "list", "source": REASONS},
            note="The reason it was binned - this is what the reports "
                 "group by."),
        Col("recipe", "From recipe", 22, "select",
            validate={"type": "list", "source": "=" + lists("Recipes",
                                                            "recipe")}),
        Col("storage_at_waste", "Stored in", 12, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("avoidable", "Avoidable", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")},
            note="No = it was bones, peel or packaging you cannot eat."),
        Col("portion", "Portion", 14, "text"),
        Col("store", "Bought at", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("month", "Month", 11, "calc", group="reporting",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("month_total", "Month total", 12, "calc",
            formula='=IF(OR({date}{r}="",{cost}{r}=""),"",'
                    'SUMIFS({cost_first}:{cost_last},'
                    '{month_first}:{month_last},{month}{r}))'),
        Col("share_of_total", "Share of month", 12, "calc",
            formula='=IF(OR({cost}{r}="",{month_total}{r}="",'
                    '{month_total}{r}=0),"",{cost}{r}/{month_total}{r})'),
        Col("waste_rank", "Waste rank", 10, "calc", group="rankings",
            formula='=IF(OR({item}{r}="",{qty}{r}=""),"",'
                    'COUNTIFS({qty_first}:{qty_last},'
                    '">"&{qty}{r})+1)'),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({avoidable}{r}="No","Unavoidable","Avoidable"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Food Waste",
        title="Food Waste",
        subtitle="What you binned, why, and what it cost",
        columns=columns,
        rows=cfg.row_count("Food Waste"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Leftovers", "Ingredients", "Sustainability",
        "Reports", "Help"])
````

### `meal_planner_spreadsheet/sheets/meal_prep.py`

Meal Prep - batch cooking tasks and what to do when *(116 lines)*

````python
"""
Meal Prep - batch cooking tasks and what to do when.

List the jobs for your prep day, how long each takes and the order to do
them in.  The urgency column counts down to the day the batch is needed and
the todo rank puts the most pressing task at the top of the list.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

YES_NO = ["Yes", "No"]
STATUS = ["To do", "In progress", "Done", "Skipped"]
EQUIPMENT = ["Oven", "Hob", "Slow cooker", "Air fryer", "Grill",
             "Food processor", "Blender", "Microwave", "No cooking"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    columns = [
        Col("task_id", "Task ID", 10, "text", group="what",
            note="Anything you like - 'P-01' is a good pattern."),
        Col("prep_day", "Prep day", 12, "select",
            validate={"type": "list",
                      "source": ["Monday", "Tuesday", "Wednesday",
                                 "Thursday", "Friday", "Saturday",
                                 "Sunday"]}),
        Col("task", "Task", 30, "text"),
        Col("recipe", "Recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("duration_min", "Minutes", 9, "number", group="effort",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("order", "Order", 8, "number",
            validate={"type": "integer", "between": 1, "and": 99},
            note="The order to do the tasks in."),
        Col("due_date", "Needed by", 12, "date"),
        Col("days_until", "Days until", 10, "calc", group="urgency",
            formula='=IF(OR({task_id}{r}="",{due_date}{r}=""),"",'
                    '{due_date}{r}-TODAY())'),
        Col("urgency", "Urgency", 13, "calc",
            formula='=IF({task_id}{r}="","",'
                    'IF({completed}{r}="Yes","Done",'
                    'IF({days_until}{r}="","No date",'
                    'IF({days_until}{r}<0,"Overdue",'
                    'IF({days_until}{r}<=Prep_Reminder_Days,"This week",'
                    '"Later")))))'),
        Col("todo_rank", "Todo rank", 10, "calc", group="rankings",
            formula='=IF(OR({task_id}{r}="",{days_until}{r}=""),"",'
                    'COUNTIFS({days_until_first}:{days_until_last},'
                    '"<"&{days_until}{r})+1)'),
        Col("assigned_to", "Who", 16, "text", group="detail"),
        Col("equipment", "Equipment", 15, "select",
            validate={"type": "list", "source": EQUIPMENT}),
        Col("batch_qty", "Batch size", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("portions", "Portions", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("fridge_until", "Fridge until", 12, "calc",
            formula='=IF(OR({task_id}{r}="",{completed_date}{r}=""),"",'
                    '{completed_date}{r}+Leftover_Safe_Days)'),
        Col("freezer_until", "Freezer until", 12, "calc",
            formula='=IF(OR({task_id}{r}="",{completed_date}{r}=""),"",'
                    '{completed_date}{r}+Freezer_Review_Days)'),
        Col("linked_slot", "For meal slot", 14, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "meal_slot")}),
        Col("calories", "Calories", 10, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        lists("Recipes", "calories"))
                    + '*{servings}{r},""))'),
        Col("cost", "Cost", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        lists("Recipes",
                                              "cost_per_serving"))
                    + '*{servings}{r},""))'),
        Col("completed", "Done", 9, "select", group="tracking",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("completed_date", "Completed on", 12, "date"),
        Col("status", "Status", 12, "select",
            validate={"type": "list", "source": STATUS}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Meal Prep",
        title="Meal Prep",
        subtitle="Batch cooking tasks, in the order to do them",
        columns=columns,
        rows=cfg.row_count("Meal Prep"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Leftovers", "Fridge & Freezer", "Recipes",
        "Print Week", "Help"])
````

### `meal_planner_spreadsheet/sheets/dietary_filters.py`

Dietary Filters - allergies, intolerances and dietary needs *(77 lines)*

````python
"""
Dietary Filters - allergies, intolerances and dietary needs.

One row per thing to avoid.  The three calculated columns show how far the
exclusion reaches: how many ingredients it matches, how many recipes use
one of them and how many planned meals are flagged.  Anything listed here
is checked automatically on the Recipe Ingredients and Meal Plan tabs.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

SEVERITY = ["Avoid", "Caution", "Preference"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("filter_id", "Filter ID", 10, "text", group="what",
            note="Anything you like - 'DF-01' is a good pattern."),
        Col("member", "Applies to", 20, "text",
            note="Who the exclusion is for. Leave blank for the whole "
                 "household."),
        Col("exclude", "Avoid this", 24, "text",
            note="The ingredient name to look for. It is matched against "
                 "the Ingredients and Recipe Ingredients tabs."),
        Col("reason", "Reason", 22, "text"),
        Col("severity", "Severity", 12, "select",
            validate={"type": "list", "source": SEVERITY}),
        Col("active", "Active", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("matching_ingredients", "Ingredients matched", 13, "calc",
            group="reach",
            formula='=IF({exclude}{r}="","",'
                    'COUNTIFS([[Ingredients.ingredient]],{exclude}{r}))'),
        Col("recipes_affected", "Recipes affected", 13, "calc",
            formula='=IF({exclude}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{exclude}{r}))'),
        Col("plan_rows_flagged", "Plan rows flagged", 13, "calc",
            formula='=IF({exclude}{r}="","",'
                    'SUMPRODUCT((COUNTIFS('
                    '[[Recipe Ingredients.recipe]],[[Meal Plan.recipe]],'
                    '[[Recipe Ingredients.ingredient]],{exclude}{r})'
                    '>0)*1))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Dietary Filters",
        title="Dietary Filters",
        subtitle="Allergies, intolerances and dietary needs - checked "
                 "against every recipe and plan",
        columns=columns,
        rows=cfg.row_count("Dietary Filters"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Household", "Recipes", "Recipe Ingredients",
        "Meal Plan", "Help"])
````

### `meal_planner_spreadsheet/sheets/rotation.py`

Rotation - how often each meal repeats *(100 lines)*

````python
"""
Rotation - how often each meal repeats.

Nothing kills a meal plan faster than the same dinner three times in a
fortnight.  This tab reads the Meal Plan, works out how long it has been
since each recipe was last cooked, when it is allowed back in the plan and
which meals are the most overdue.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick a recipe from your recipe book."),
        Col("category", "Category", 15, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("category")) + ")"),
        Col("cuisine", "Cuisine", 14, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("cuisine")) + ")"),
        Col("times_planned", "Times cooked", 12, "calc", group="history",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Cooked")'
                    '+COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Eaten"))'),
        Col("last_planned", "Last cooked", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("last_planned")) + ")"),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    'TODAY()-{last_planned}{r})'),
        Col("avg_gap", "Average gap (days)", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{times_planned}{r}=0),"",'
                    'ROUND(365/{times_planned}{r},0))'),
        Col("rotation_ok", "Rotation", 10, "calc", group="rules",
            formula='=IF({recipe}{r}="","",'
                    'IF({days_since}{r}="","Yes",'
                    'IF({days_since}{r}>=Rotation_Gap_Days,"Yes","No")))'),
        Col("next_earliest", "Back in the plan", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    '{last_planned}{r}+Rotation_Gap_Days)'),
        Col("days_until_ok", "Days until", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{next_earliest}{r}=""),"",'
                    '{next_earliest}{r}-TODAY())'),
        Col("rotation_rank", "Overdue rank", 12, "calc", group="rankings",
            formula='=IF(OR({recipe}{r}="",{days_since}{r}=""),"",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '"<"&{days_since}{r})+1)'),
        Col("favourite", "Favourite", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("favourite"))
                    + ")"),
        Col("rating", "Rating", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("rating")) + ")"),
        Col("plan_flag", "Plan flag", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({rotation_ok}{r}="No","Too soon",'
                    'IF({days_since}{r}="","Never cooked",'
                    'IF({days_since}{r}>=90,"Overdue","Available"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Rotation",
        title="Rotation",
        subtitle="How often each meal repeats, so the plan never gets boring",
        columns=columns,
        rows=cfg.row_count("Rotation"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Meal Plan", "Weekly Planner", "Help"])
````

### `meal_planner_spreadsheet/sheets/food_safety.py`

Food Safety - how long food keeps, and at what temperature *(107 lines)*

````python
"""
Food Safety - how long food keeps, and at what temperature.

A ready made reference for the foods you cook most: fridge life, freezer
life, how long cooked food keeps and the safe storage and reheating
temperatures.  Edit the numbers to match your own kitchen and the pantry
and leftover tabs will follow.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
CATEGORIES = ["Meat", "Fish", "Dairy", "Eggs", "Vegetables", "Fruit",
              "Grains", "Cooked food", "Leftovers", "Condiments",
              "Baking", "Drinks"]

ROWS = [
    ("Raw chicken", "Meat", "Fridge", 2, 270, 3, 4, 75),
    ("Raw beef / mince", "Meat", "Fridge", 2, 120, 3, 4, 75),
    ("Raw pork", "Meat", "Fridge", 3, 180, 3, 4, 75),
    ("Cooked chicken", "Cooked food", "Fridge", 3, 90, 3, 4, 75),
    ("Cooked mince / bolognese", "Cooked food", "Fridge", 3, 90, 3, 4, 75),
    ("Sausages", "Meat", "Fridge", 3, 60, 3, 4, 75),
    ("Bacon", "Meat", "Fridge", 7, 60, 3, 4, 75),
    ("White fish", "Fish", "Fridge", 1, 90, 2, 2, 63),
    ("Oily fish", "Fish", "Fridge", 1, 60, 2, 2, 63),
    ("Cooked fish", "Cooked food", "Fridge", 2, 60, 2, 2, 63),
    ("Prawns", "Fish", "Fridge", 1, 90, 2, 2, 63),
    ("Milk (opened)", "Dairy", "Fridge", 5, 30, 0, 5, 72),
    ("Cheese (hard)", "Dairy", "Fridge", 21, 60, 0, 5, 72),
    ("Cheese (soft)", "Dairy", "Fridge", 7, 30, 0, 5, 72),
    ("Butter", "Dairy", "Fridge", 60, 90, 0, 5, 72),
    ("Yoghurt (opened)", "Dairy", "Fridge", 5, 30, 0, 5, 72),
    ("Eggs", "Eggs", "Fridge", 21, 0, 0, 5, 72),
    ("Cooked rice", "Cooked food", "Fridge", 1, 30, 1, 5, 75),
    ("Cooked pasta", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Cooked potatoes", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Soup / stew", "Cooked food", "Fridge", 3, 90, 3, 5, 75),
    ("Curry", "Cooked food", "Fridge", 3, 90, 3, 5, 75),
    ("Salad leaves", "Vegetables", "Fridge", 3, 0, 0, 5, 0),
    ("Chopped veg", "Vegetables", "Fridge", 3, 120, 0, 5, 0),
    ("Tomatoes", "Fruit", "Cupboard", 7, 60, 0, 12, 0),
    ("Bananas", "Fruit", "Cupboard", 5, 60, 0, 12, 0),
    ("Apples", "Fruit", "Fridge", 30, 0, 0, 5, 0),
    ("Berries", "Fruit", "Fridge", 3, 180, 0, 5, 0),
    ("Bread", "Baking", "Cupboard", 4, 90, 0, 20, 0),
    ("Cooked meat (sliced)", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Gravy", "Condiments", "Fridge", 2, 90, 2, 5, 75),
    ("Pesto (opened)", "Condiments", "Fridge", 14, 60, 0, 5, 0),
    ("Ketchup (opened)", "Condiments", "Cupboard", 60, 0, 0, 20, 0),
    ("Tinned food (opened)", "Condiments", "Fridge", 3, 0, 0, 5, 0),
    ("Leftover pizza", "Leftovers", "Fridge", 3, 60, 3, 5, 75),
    ("Batch cooked chilli", "Cooked food", "Fridge", 3, 120, 3, 5, 75),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    columns = [
        Col("food", "Food", 26, "text", group="what"),
        Col("category", "Category", 14, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("storage", "Store in", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("fridge_days", "Fridge (days)", 11, "number", group="times",
            validate={"type": "integer", "between": 0, "and": 3650}),
        Col("freezer_days", "Freezer (days)", 12, "number",
            validate={"type": "integer", "between": 0, "and": 3650}),
        Col("cooked_days", "Once cooked (days)", 13, "number",
            validate={"type": "integer", "between": 0, "and": 365}),
        Col("safe_temp", "Fridge temp (C)", 12, "number", group="safety",
            validate={"type": "integer", "between": -20, "and": 20}),
        Col("reheat_temp", "Reheat to (C)", 12, "number",
            validate={"type": "integer", "between": 40, "and": 120}),
        Col("source", "Source", 18, "text"),
        Col("status", "Status", 14, "calc",
            formula='=IF({food}{r}="","",'
                    'IF({freezer_days}{r}>0,"Freezable","Fridge only"))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Food Safety",
        title="Food Safety",
        subtitle="How long food keeps, and the temperatures that keep it safe",
        columns=columns,
        rows=cfg.row_count("Food Safety"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec, sample_index=writer.samples.get("Food Safety"))
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Leftovers", "Fridge & Freezer", "Help"],
                        banding=True)
````

### `meal_planner_spreadsheet/sheets/fridge_freezer.py`

Fridge & Freezer - batch cooked portions and their use-by dates *(100 lines)*

````python
"""
Fridge & Freezer - batch cooked portions and their use-by dates.

Where the Meal Prep tab says what to cook, this tab says what is actually
in there.  Each batch gets a fridge use-by date, a freezer use-by date, a
value and a place in the queue, so a full freezer never turns into a bin
bag three weeks later.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

STORAGE = ["Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    columns = [
        Col("batch_id", "Batch ID", 11, "text", group="what",
            note="Anything you like - 'FF-01' is a good pattern."),
        Col("item", "What it is", 26, "text"),
        Col("recipe", "From recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("portions", "Portions", 9, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("storage", "Storage", 10, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("cooked_date", "Cooked", 12, "date"),
        Col("use_by", "Use by", 12, "calc", group="dates",
            formula='=IF(OR({batch_id}{r}="",{cooked_date}{r}=""),"",'
                    'IF({storage}{r}="Freezer",'
                    '{cooked_date}{r}+Freezer_Review_Days,'
                    '{cooked_date}{r}+Leftover_Safe_Days))'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({batch_id}{r}="",{use_by}{r}=""),"",'
                    '{use_by}{r}-TODAY())'),
        Col("status", "Status", 14, "calc",
            formula='=IF({batch_id}{r}="","",'
                    'IF({eaten}{r}="Yes","Eaten",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Past its best",'
                    'IF({days_left}{r}<=1,"Eat today",'
                    'IF({days_left}{r}<=3,"Eat this week","Keep"))))))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({batch_id}{r}="",{portions}{r}=""),"",'
                    'IFERROR({portions}{r}*'
                    + lookup("{recipe}{r}", recipes,
                             lists("Recipes", "cost_per_serving"))
                    + ',""))'),
        Col("fridge_rank", "Fridge rank", 10, "calc", group="rankings",
            formula='=IF(OR({storage}{r}<>"Fridge",{days_left}{r}=""),"",'
                    'COUNTIFS({storage_first}:{storage_last},"Fridge",'
                    '{days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("freezer_rank", "Freezer rank", 11, "calc",
            formula='=IF(OR({storage}{r}<>"Freezer",{days_left}{r}=""),"",'
                    'COUNTIFS({storage_first}:{storage_last},"Freezer",'
                    '{days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("container", "Container", 16, "text", group="detail"),
        Col("reheats", "Reheats left", 11, "number",
            validate={"type": "integer", "between": 0, "and": 5}),
        Col("defrost_by", "Defrost by", 12, "calc",
            formula='=IF(OR({batch_id}{r}="",{use_by}{r}=""),"",'
                    '{use_by}{r}-1)'),
        Col("eaten", "Eaten", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Fridge & Freezer",
        title="Fridge & Freezer",
        subtitle="Batch cooked portions, with use-by dates and a queue",
        columns=columns,
        rows=cfg.row_count("Fridge & Freezer"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Meal Prep", "Leftovers", "Pantry", "Food Safety",
        "Help"])
````

### `meal_planner_spreadsheet/sheets/grocery_spending.py`

Grocery Spending - every shop you record, against the budget *(114 lines)*

````python
"""
Grocery Spending - every shop you record, against the budget.

Record what you actually spent and the tab works out the week and the
month, compares each week with the weekly budget and keeps a running total
for the month.  This is the tab the Budget and Reports tabs read.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

PAYMENT = ["Cash", "Debit card", "Credit card", "Phone", "Voucher",
           "Gift card", "Account"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("date", "Date", 12, "date", group="when"),
        Col("week_start", "Week starting", 12, "calc",
            formula='=IF({date}{r}="","",'
                    '{date}{r}-WEEKDAY({date}{r},2)+1)'),
        Col("month", "Month", 11, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("store", "Store", 18, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "store")}),
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("qty", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "unit")}),
        Col("price", "Price paid", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("line_total", "Line total", 11, "calc", group="money",
            formula='=IF(OR({item}{r}="",{qty}{r}="",{price}{r}=""),"",'
                    '{qty}{r}*{price}{r})'),
        Col("week_spend", "Week spend", 11, "calc",
            formula='=IF(OR({date}{r}="",{line_total}{r}=""),"",'
                    'SUMIFS({line_total_first}:{line_total_last},'
                    '{week_start_first}:{week_start_last},'
                    '{week_start}{r}))'),
        Col("share_of_week", "Share of week", 12, "calc",
            formula='=IF(OR({line_total}{r}="",{week_spend}{r}="",'
                    '{week_spend}{r}=0),"",'
                    '{line_total}{r}/{week_spend}{r})'),
        Col("vs_budget", "Week vs budget", 12, "calc",
            formula='=IF({week_spend}{r}="","",'
                    '{week_spend}{r}-Weekly_Budget)'),
        Col("budget_flag", "Budget flag", 12, "calc",
            formula='=IF({week_spend}{r}="","",'
                    'IF({week_spend}{r}>Weekly_Budget,"Over budget",'
                    'IF({week_spend}{r}>Weekly_Budget*0.9,"Close",'
                    '"Within budget")))'),
        Col("receipt_no", "Receipt", 12, "text", group="detail"),
        Col("payment", "Paid by", 13, "select",
            validate={"type": "list", "source": PAYMENT}),
        Col("on_sale", "On offer", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("savings", "Saving", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({line_total}{r}="","",'
                    'COUNTIFS({line_total_first}:{line_total_last},'
                    '">"&{line_total}{r})+1)'),
        Col("month_running", "Month running total", 13, "calc",
            formula='=IF(OR({date}{r}="",{line_total}{r}=""),"",'
                    'SUMIFS({line_total_first}:{line_total_last},'
                    '{month_first}:{month_last},{month}{r},'
                    '{date_first}:{date_last},"<="&{date}{r}))'),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({on_sale}{r}="Yes","On offer","Full price"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Grocery Spending",
        title="Grocery Spending",
        subtitle="Every shop you record, week by week, against the budget",
        columns=columns,
        rows=cfg.row_count("Grocery Spending"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Budget", "Reports", "Ingredients", "Store Prices",
        "Stores", "Help"])
````

### `meal_planner_spreadsheet/sheets/store_prices.py`

Store Prices - the same item, priced at every shop *(107 lines)*

````python
"""
Store Prices - the same item, priced at every shop.

Log a price whenever you notice one.  The tab converts every price to a
price per unit so packs of different sizes can be compared, flags the
cheapest offer for each item and shows how far the dearest shop is from
the best.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab."),
        Col("store", "Store", 18, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "store")}),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "unit")}),
        Col("price", "Price", 11, "money", group="price",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_per_unit", "Price / unit", 11, "calc",
            formula='=IF(OR({price}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",{price}{r}/{pack_size}{r})'),
        Col("date", "Seen on", 12, "date"),
        Col("on_sale", "On offer", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("usual_price", "Usual price", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("saving", "Saving", 11, "calc", group="offers",
            formula='=IF(OR({price}{r}="",{usual_price}{r}=""),"",'
                    '{usual_price}{r}-{price}{r})'),
        Col("saving_pct", "Saving %", 10, "calc",
            formula='=IF(OR({saving}{r}="",{usual_price}{r}="",'
                    '{usual_price}{r}=0),"",'
                    '{saving}{r}/{usual_price}{r})'),
        Col("best_price", "Best price", 11, "calc", group="comparison",
            formula='=IF({item}{r}="","",'
                    'IF(SUMPRODUCT(MIN((' + lists("Store Prices", "item")
                    + '={item}{r})*' + lists("Store Prices",
                                             "price_per_unit")
                    + '+(' + lists("Store Prices", "item")
                    + '<>{item}{r})*1000000))>=1000000,"",'
                    'SUMPRODUCT(MIN((' + lists("Store Prices", "item")
                    + '={item}{r})*'
                    + lists("Store Prices", "price_per_unit")
                    + '+(' + lists("Store Prices", "item")
                    + '<>{item}{r})*1000000))))'),
        Col("vs_best", "Vs best", 10, "calc",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}="",'
                    '{best_price}{r}=""),"",'
                    '{price_per_unit}{r}-{best_price}{r})'),
        Col("best_flag", "Best buy", 10, "calc",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}=""),"",'
                    'IF({price_per_unit}{r}={best_price}{r},"Best",""))'),
        Col("rank", "Price rank", 10, "calc", group="rankings",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}=""),"",'
                    'COUNTIFS(' + lists("Store Prices", "item") + ','
                    '{item}{r},' + lists("Store Prices",
                                         "price_per_unit") + ','
                    '"<"&{price_per_unit}{r})+1)'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Store Prices",
        title="Store Prices",
        subtitle="The same item, priced at every shop",
        columns=columns,
        rows=cfg.row_count("Store Prices"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Ingredients", "Stores", "Grocery Spending", "Help"])
````

### `meal_planner_spreadsheet/sheets/stores.py`

Stores - where you shop *(99 lines)*

````python
"""
Stores - where you shop.

One row per shop with the practical details you actually need: whether they
deliver, the minimum order, what they are best for and how much you have
spent there.  The spend columns are read from the Grocery Spending tab, so
they fill themselves in as you record shops.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

YES_NO = ["Yes", "No"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday", "n/a"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_store = lists("Grocery Spending", "store")
    gs_total = lists("Grocery Spending", "line_total")

    columns = [
        Col("store", "Store", 22, "text", group="who"),
        Col("address", "Address", 30, "text"),
        Col("phone", "Phone", 16, "text"),
        Col("website", "Website", 22, "text"),
        Col("loyalty", "Loyalty scheme", 18, "text", group="details"),
        Col("delivery", "Delivers", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("pickup", "Click & collect", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("min_order", "Minimum order", 12, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("delivery_fee", "Delivery fee", 12, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("delivery_day", "Delivery day", 13, "select",
            validate={"type": "list", "source": DAYS}),
        Col("opening_hours", "Opening hours", 20, "text"),
        Col("distance_km", "Distance (km)", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("parking", "Parking", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("organic_range", "Organic range", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bulk_bins", "Bulk bins", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("cards", "Cards accepted", 18, "text"),
        Col("visits", "Shops recorded", 12, "calc", group="spend",
            formula='=IF({store}{r}="","",'
                    'COUNTIFS(' + gs_store + ',{store}{r}))'),
        Col("total_spend", "Total spend", 12, "calc",
            formula='=IF({store}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_store + ','
                    '{store}{r}))'),
        Col("avg_basket", "Average basket", 12, "calc",
            formula='=IF(OR({store}{r}="",{visits}{r}=0),"",'
                    'ROUND({total_spend}{r}/{visits}{r},2))'),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF(OR({store}{r}="",{total_spend}{r}=0),"",'
                    'COUNTIFS({total_spend_first}:{total_spend_last},'
                    '">"&{total_spend}{r})+1)'),
        Col("best_for", "Best for", 26, "text", group="notes"),
        Col("rating", "Rating (1-5)", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 5}),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Stores",
        title="Stores",
        subtitle="Where you shop, what they are good for and what you have "
                 "spent there",
        columns=columns,
        rows=cfg.row_count("Stores"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Grocery Spending", "Store Prices", "Lists", "Help"])
````

### `meal_planner_spreadsheet/sheets/events.py`

Events - parties, holidays and dinner guests *(114 lines)*

````python
"""
Events - parties, holidays and dinner guests.

Give the event a date and a head count, pick the dishes you plan to cook
and the tab works out the cost per head, compares it with the budget and
counts down the days.  The prep tasks you need are counted straight from
the Meal Prep tab.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

MEAL_TYPES = ["Breakfast", "Brunch", "Lunch", "Dinner", "BBQ", "Buffet",
              "Picnic", "Afternoon tea", "Drinks", "Other"]
STATUS = ["Planning", "Invited", "Shopping", "Ready", "Done", "Cancelled"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    menu_cols = [Col(f"menu_{i}", f"Dish {i}", 24, "select",
                     validate={"type": "list", "source": "=" + recipes},
                     group="menu")
                 for i in range(1, 5)]

    columns = [
        Col("event", "Event", 24, "text", group="what",
            note="Anything you like - 'Mum's birthday' is perfect."),
        Col("date", "Date", 12, "date"),
        Col("guests", "Guests", 9, "number",
            validate={"type": "integer", "between": 1, "and": 500}),
        Col("meal_type", "Meal", 13, "select",
            validate={"type": "list", "source": MEAL_TYPES}),
        Col("host", "Host", 16, "text"),
        Col("location", "Where", 22, "text"),
        Col("budget", "Budget", 12, "money", group="money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
    ] + menu_cols + [
        Col("dessert", "Dessert", 24, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("drinks", "Drinks", 22, "text"),
        Col("servings", "Servings each", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 20}),
        Col("menu_cost", "Menu cost", 12, "calc",
            formula='=IF({event}{r}="","",'
                    'IFERROR(' + lookup("{menu_1}{r}", recipes,
                                        rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_2}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_3}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_4}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{dessert}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0))'),
        Col("cost_per_head", "Cost per head", 12, "calc",
            formula='=IF(OR({event}{r}="",{guests}{r}=0),"",'
                    'IFERROR({menu_cost}{r}/{guests}{r},""))'),
        Col("variance", "Vs budget", 11, "calc",
            formula='=IF(OR({event}{r}="",{budget}{r}=""),"",'
                    '{budget}{r}-{menu_cost}{r})'),
        Col("days_until", "Days to go", 11, "calc", group="planning",
            formula='=IF(OR({event}{r}="",{date}{r}=""),"",'
                    '{date}{r}-TODAY())'),
        Col("prep_tasks", "Prep tasks", 11, "calc",
            formula='=IF({event}{r}="","",'
                    'COUNTIFS([[Meal Prep.recipe]],{menu_1}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_2}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_3}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_4}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{dessert}{r}))'),
        Col("dietary_notes", "Dietary notes", 26, "text"),
        Col("leftover_plan", "Leftover plan", 26, "text",
            note="What happens to the food that is left over."),
        Col("status", "Status", 12, "select",
            validate={"type": "list", "source": STATUS}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Events",
        title="Events",
        subtitle="Parties, holidays and dinner guests - with a menu budget",
        columns=columns,
        rows=cfg.row_count("Events"),
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Meal Prep", "Grocery List", "Help"])
````

### `meal_planner_spreadsheet/sheets/sustainability.py`

Sustainability - waste, packaging and how local your shopping is *(110 lines)*

````python
"""
Sustainability - waste, packaging and how local your shopping is.

The spend, waste and habit columns are read from the other tabs, so this
page fills itself in.  Fill in the packaging and local shopping columns
yourself and the score at the end tells you how the month went.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_month = lists("Grocery Spending", "month")
    gs_total = lists("Grocery Spending", "line_total")
    fw_month = lists("Food Waste", "month")
    fw_cost = lists("Food Waste", "cost")
    fw_qty = lists("Food Waste", "qty")
    mp_month = lists("Meal Plan", "month")
    mp_status = lists("Meal Plan", "status")

    columns = [
        Col("month", "Month", 12, "text", group="when",
            note="Type it as 'Jan 2026' to match the other tabs."),
        Col("groceries", "Grocery spend", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_month + ','
                    '{month}{r}))'),
        Col("waste_cost", "Waste cost", 11, "calc", group="waste",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_cost + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("waste_qty", "Waste quantity", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_qty + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("waste_share", "Waste as % of spend", 13, "calc",
            formula='=IF(OR({month}{r}="",{groceries}{r}="",'
                    '{groceries}{r}=0),"",'
                    'IFERROR({waste_cost}{r}/{groceries}{r},""))'),
        Col("waste_target", "Target", 10, "calc",
            formula='=IF({month}{r}="","",Waste_Reduction_Target)'),
        Col("waste_vs_target", "Vs target", 11, "calc",
            formula='=IF(OR({month}{r}="",{waste_share}{r}=""),"",'
                    '{waste_share}{r}-Waste_Reduction_Target)'),
        Col("home_cooked", "Home cooked meals", 12, "calc", group="habits",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Cooked")'
                    '+COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Eaten"))'),
        Col("takeaways", "Takeaways", 10, "calc",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Takeaway")'
                    '+COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Eating out"))'),
        Col("new_recipes", "New recipes tried", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS([[Recipes.added_on]],{month}{r}))'),
        Col("local_shops", "Local shops used", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60},
            group="your own numbers"),
        Col("bulk_buys", "Bulk / refill buys", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60}),
        Col("packaging_free", "Plastic free shops", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60}),
        Col("own_grown", "Grown at home", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("score", "Green score", 11, "calc", group="score",
            formula='=IF({month}{r}="","",'
                    'IF({waste_share}{r}="",0,'
                    'MAX(0,100-({waste_share}{r}*1000)))'
                    '+{local_shops}{r}*2+{bulk_buys}{r}*2'
                    '+{packaging_free}{r}*2+{own_grown}{r})'),
        Col("status", "Status", 14, "calc",
            formula='=IF({month}{r}="","",'
                    'IF({waste_vs_target}{r}="","",'
                    'IF({waste_vs_target}{r}<=0,"On target",'
                    '"Over target")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Sustainability",
        title="Sustainability",
        subtitle="Waste, packaging and how local your shopping is",
        columns=columns,
        rows=24,
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Food Waste", "Grocery Spending", "Goals", "Reports",
        "Help"])
````

### `meal_planner_spreadsheet/sheets/recipe_costs.py`

Recipe Costs - what every dish really costs to put on the table *(123 lines)*

````python
"""
Recipe Costs - what every dish really costs to put on the table.

The Recipes tab already shows a cost per serving; this tab puts the whole
book side by side, cheapest first, and breaks out the single most expensive
ingredient in each recipe so you can see exactly where the money goes.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    ri_recipe = lists("Recipe Ingredients", "recipe")
    ri_ing = lists("Recipe Ingredients", "ingredient")
    ri_cost = lists("Recipe Ingredients", "line_cost")

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick a recipe from your recipe book."),
        Col("category", "Category", 15, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("category")) + ")"),
        Col("servings", "Servings", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("servings")) + ")"),
        Col("ingredient_count", "Ingredients", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS(' + ri_recipe + ',{recipe}{r}))'),
        Col("total_cost", "Total cost", 12, "calc", group="cost",
            formula='=IF({recipe}{r}="","",'
                    'SUMIFS(' + ri_cost + ',' + ri_recipe + ','
                    '{recipe}{r}))'),
        Col("cost_per_serving", "Cost / serving", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("cost_per_serving")) + ")"),
        Col("cost_per_calorie", "Cost / 100 kcal", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{calories}{r}="",'
                    '{calories}{r}=0),"",'
                    'IFERROR({cost_per_serving}{r}/{calories}{r}*100,'
                    '""))'),
        Col("cost_rank", "Cost rank", 10, "calc", group="rankings",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'COUNTIFS({cost_per_serving_first}:'
                    '{cost_per_serving_last},"<"&'
                    '{cost_per_serving}{r})+1)'),
        Col("top_ingredient", "Priciest ingredient", 22, "calc",
            group="breakdown",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(INDEX(' + ri_ing + ',MATCH(1,INDEX(('
                    + ri_recipe + '={recipe}{r})*(' + ri_cost + '='
                    '{top_ingredient_cost}{r}),0),0)),""))'),
        Col("top_ingredient_cost", "Its cost", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'SUMPRODUCT(MAX((' + ri_recipe + '={recipe}{r})*'
                    + ri_cost + ')))'),
        Col("top_share", "Share of cost", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{total_cost}{r}="",'
                    '{total_cost}{r}=0),"",'
                    'IFERROR({top_ingredient_cost}{r}/{total_cost}{r},'
                    '""))'),
        Col("vs_average", "Vs average dish", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'IFERROR({cost_per_serving}{r}-AVERAGE('
                    '{cost_per_serving_first}:{cost_per_serving_last}),'
                    '""))'),
        Col("budget_flag", "Budget flag", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'IF({cost_per_serving}{r}<=Weekly_Budget/21,'
                    '"Within budget","Over budget"))'),
        Col("calories", "Calories", 10, "calc", group="value",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("calories")) + ")"),
        Col("calories_per_dollar", "kcal / $", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("calories_per_dollar")) + ")"),
        Col("protein_per_dollar", "Protein / $", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("protein_per_dollar")) + ")"),
        Col("weekly_cost", "Cost per week", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    '{cost_per_serving}{r}*7*3)'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Recipe Costs",
        title="Recipe Costs",
        subtitle="Cost per serving for every recipe, cheapest first",
        columns=columns,
        rows=cfg.row_count("Recipe Costs"),
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Recipe Ingredients", "Budget", "Reports",
        "Help"])
````

### `meal_planner_spreadsheet/sheets/converter.py`

Converter - unit conversions and a live converter you can use *(152 lines)*

````python
"""
Converter - unit conversions and a live converter you can use.

The reference table below holds the conversion factors between the units you
use most.  The calculator at the top looks the factor up from that table, so
add your own pairs (for example 'cup' to 'g' for flour) and the calculator
handles them straight away.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

CATEGORIES = ["Weight", "Volume", "Count", "Temperature", "Oven", "Tin size"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    columns = [
        Col("from_unit", "From", 12, "text", group="conversion"),
        Col("to_unit", "To", 12, "text"),
        Col("factor", "Multiply by", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("category", "Category", 13, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("example", "Example", 30, "text"),
        Col("reverse", "Reverse", 22, "calc",
            formula='=IF(OR({from_unit}{r}="",{factor}{r}=""),"",'
                    '{to_unit}{r}&" to "&{from_unit}{r}&": divide by "'
                    '&TEXT({factor}{r},"0.####"))'),
        Col("status", "Status", 14, "calc",
            formula='=IF({from_unit}{r}="","",'
                    'IF({factor}{r}=0,"Check the factor","OK"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Converter",
        title="Converter",
        subtitle="Unit conversions, plus a calculator you can use while you "
                 "cook",
        columns=columns,
        rows=cfg.row_count("Converter"),
        header_row=22,
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 14)
    ws.set_column(3, 3, 14)
    ws.set_column(4, 4, 34)
    ws.set_column(5, 5, 24)
    ws.set_column(6, 6, 14)
    ws.set_column(7, 7, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 6, "CONVERTER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 6,
                   "Unit conversions, plus a calculator you can use while "
                   "you cook", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 6,
                   "  |  Recipes   |   Ingredients   |   Pantry   |   "
                   "Weekly Planner   |   Help", f["nav"])

    from_rng = reg.rng("Converter", "from_unit")
    to_rng = reg.rng("Converter", "to_unit")
    factor_rng = reg.rng("Converter", "factor")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 6, "  QUICK CONVERTER", f["section"])

    ws.write(5, 0, "Quantity", f["label"])
    ws.write_number(5, 1, 250, f["input_number"])
    ws.write(6, 0, "From", f["label"])
    ws.write_string(6, 1, "g", f["input_select"])
    ws.write(6, 2, "To", f["label"])
    ws.write_string(6, 3, "oz", f["input_select"])
    ws.write(7, 0, "Result", f["label"])
    ws.write_formula(
        7, 1,
        '=IFERROR($B$6*IFERROR(INDEX(' + factor_rng + ',MATCH(1,INDEX(('
        + from_rng + '=$B$7)*(' + to_rng + '=$D$7),0),0)),"?"),"not in table")',
        f["kpi_value"])
    ws.write(7, 2, "Reverse", f["label"])
    ws.write_formula(
        7, 3,
        '=IFERROR($B$6/IFERROR(INDEX(' + factor_rng + ',MATCH(1,INDEX(('
        + from_rng + '=$B$7)*(' + to_rng + '=$D$7),0),0)),"?"),"not in table")',
        f["kpi_value"])
    ws.set_row(7, 30)

    ws.data_validation(5, 1, 5, 1, {"validate": "decimal",
                                    "criteria": "between",
                                    "minimum": 0, "maximum": 1000000,
                                    "error_type": "warning",
                                    "error_title": "Check this number",
                                    "error_message": "Enter a quantity to "
                                    "convert."})
    ws.data_validation(6, 1, 6, 1,
                       {"validate": "list", "source": "=" + from_rng})
    ws.data_validation(6, 3, 6, 3,
                       {"validate": "list", "source": "=" + to_rng})

    # ---- oven temperatures -------------------------------------------------
    ws.set_row(9, 22)
    ws.merge_range(9, 0, 9, 6, "  OVEN TEMPERATURES", f["section"])
    oven = [("Gas mark", "Fan (C)", "Conventional (C)", "Fahrenheit"),
            ("1/4", 110, 120, 250), ("1/2", 120, 130, 265),
            ("1", 140, 150, 300), ("2", 150, 160, 325),
            ("3", 160, 180, 350), ("4", 170, 190, 375),
            ("5", 180, 200, 400), ("6", 190, 210, 425),
            ("7", 200, 220, 450), ("8", 210, 230, 475),
            ("9", 220, 240, 500)]
    for i, row in enumerate(oven):
        style = f["header"] if i == 0 else f["calc_center"]
        for j, value in enumerate(row):
            ws.write(10 + i, j, value, style)

    writer.write_note(ws, 20, 0,
                  "Add a pair of units to the table below and the quick "
                  "converter above picks it up immediately. Use the factor "
                  "column for 'multiply the From unit by this to get the To "
                  "unit'.", width=7)

    writer.register(ws, spec, sample_index=writer.samples.get("Converter"))
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.primary_mid)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
````

---

## 4. The pages

The tabs that read the registers: the dashboard, the weekly and monthly planners, the nutrition log, the budget, the goals, the reports, the welcome tab, the three printable pages and the help tab.

### `meal_planner_spreadsheet/sheets/dashboard.py`

Dashboard - the week at a glance *(347 lines)*

````python
"""
Dashboard - the week at a glance.

Pick the week at the top and the page shows the meals you have planned, the
calories and the cost of the week, what is about to expire, which meals are
overdue for another turn and how your habits are going.  Everything here is
calculated - there is nothing to type in except the week itself.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Dashboard",
        title="Dashboard",
        subtitle="The week at a glance - meals, calories, cost, expiry dates "
                 "and habits",
        columns=[
            Col("metric", "Metric", 26, "text"),
            Col("label", "Label", 22, "text"),
            Col("week_start", "Week starting", 14, "text"),
            Col("detail", "Detail", 16, "text"),
            Col("spacer", " ", 3, "text"),
            Col("month_name", "Month", 16, "text"),
            Col("value", "Value", 14, "text"),
            Col("note", "Note", 30, "text_wrap"),
            Col("trend", "Trend", 14, "text"),
            Col("target", "Target", 14, "text"),
            Col("status", "Status", 16, "text"),
            Col("action", "Action", 22, "text"),
            Col("kpi_a", "A", 12, "text"),
            Col("kpi_b", "B", 12, "text"),
            Col("kpi_c", "C", 12, "text"),
            Col("kpi_d", "D", 12, "text"),
            Col("kpi_e", "E", 12, "text"),
            Col("kpi_f", "F", 12, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i in range(18):
        ws.set_column(i, i, 13 if i else 24)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 17, "DASHBOARD", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 17,
                   "The week at a glance - meals, calories, cost, expiry "
                   "dates and habits", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 17,
                   "  |  Start Here   |   Weekly Planner   |   Meal Plan   "
                   "|   Grocery List   |   Pantry   |   Reports",
                   f["nav"])

    # ---- week picker -------------------------------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 17, "  WHICH WEEK ARE YOU LOOKING AT?",
                   f["section"])
    ws.write(5, 1, "Week starting", f["label"])
    ws.write_string(5, 2, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write_formula(6, 2, "=DATEVALUE($C$6)", f["calc_date"])
    ws.write(5, 5, "Month", f["label"])
    ws.write_formula(5, 6, '=TEXT($C$7,"mmmm yyyy")', f["calc_bold"])
    ws.write(5, 8, "Household", f["label"])
    ws.write_formula(5, 9, "=Household_Name", f["calc_text"])
    ws.write(5, 11, "People", f["label"])
    ws.write_formula(5, 12, "=Household_Size", f["calc_number"])
    ws.write(5, 14, "Servings", f["label"])
    ws.write_formula(5, 15, "=Default_Servings", f["calc_number"])
    ws.write(6, 1, "Shopping day", f["label"])
    ws.write_formula(6, 2, "=Shopping_Day", f["calc_text"])
    ws.write(6, 5, "Prep day", f["label"])
    ws.write_formula(6, 6, "=Prep_Day", f["calc_text"])
    ws.write(6, 8, "Weekly budget", f["label"])
    ws.write_formula(6, 9, "=Weekly_Budget", f["calc_money"])

    mp_week = reg.rng("Meal Plan", "week_start")
    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")
    mp_status = reg.rng("Meal Plan", "status")
    gl_buy = reg.rng("Grocery List", "buy")
    gl_needed = reg.rng("Grocery List", "needed")
    pan_status = reg.rng("Pantry", "use_by_status")
    lo_days = reg.rng("Leftovers", "days_left")

    # ---- KPI tiles ---------------------------------------------------------
    ws.set_row(8, 22)
    ws.merge_range(8, 0, 8, 17, "  THIS WEEK", f["section"])
    kpis = [
        ("Meals planned", f'=COUNTIFS({mp_week},$C$7)', "kpi_value",
         "rows on the Meal Plan", 0),
        ("Calories a day", f'=IFERROR(SUMIFS({mp_cal},{mp_week},$C$7)/'
                           f'MAX(1,Household_Size)/7,0)', "kpi_value",
         f'= "target "&TEXT(Calorie_Target,"#,##0")', 3),
        ("Grocery cost", f'=SUMIFS({mp_cost},{mp_week},$C$7)',
         "kpi_value_money", f'= "budget "&TEXT(Weekly_Budget,"#,##0.00")',
         6),
        ("Budget left", f'=Weekly_Budget-SUMIFS({mp_cost},{mp_week},$C$7)',
         "kpi_value_money", "planned vs budget", 9),
        ("Items to buy", f'=COUNTIFS({gl_buy},"Yes")', "kpi_value",
         "on the grocery list", 12),
        ("Use it or lose it", f'=COUNTIFS({pan_status},"Use soon")'
                              f'+COUNTIFS({pan_status},"Expired")',
         "kpi_value", "pantry items", 15),
    ]
    for label, formula, style, sub, col in kpis:
        ws.merge_range(9, col, 9, col + 2, label, f["kpi_label"])
        ws.merge_range(10, col, 10, col + 2, None, f[style])
        ws.write_formula(10, col, formula, f[style])
        ws.merge_range(11, col, 11, col + 2, None, f["kpi_sub"])
        if isinstance(sub, str) and sub.startswith("="):
            ws.write_formula(11, col, sub, f["kpi_sub"])
        else:
            ws.write_string(11, col, sub, f["kpi_sub"])
    ws.set_row(10, 34)

    # ---- the week day by day ------------------------------------------------
    row = 13
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17, "  YOUR WEEK", f["section"])
    row += 1
    headers = ["Day", "Date", "Breakfast", "Lunch", "Dinner", "Snack",
               "Calories", "Cost", "Status"]
    for i, head in enumerate(headers):
        ws.write(row, i, head, f["header"])
    row += 1
    for offset in range(7):
        r = row + 1
        ws.write_formula(row, 0, f'=TEXT($C$7+{offset},"ddd")',
                         f["calc_bold"])
        ws.write_formula(row, 1, f'=$C$7+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack"]):
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$B{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 6,
                         f'=SUMIFS({mp_cal},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 7,
                         f'=SUMIFS({mp_cost},{mp_date},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 8,
                         f'=IF(COUNTIFS({mp_date},$B{r})=0,"Nothing planned",'
                         f'TEXT(COUNTIFS({mp_date},$B{r},{mp_status},'
                         f'"Cooked")+COUNTIFS({mp_date},$B{r},{mp_status},'
                         f'"Eaten"),"0")&" of "&'
                         f'TEXT(COUNTIFS({mp_date},$B{r}),"0")&" cooked")',
                         f["calc_center"])
        row += 1
    ws.write_formula(row, 0, "Week", f["total_label"])
    ws.write_blank(row, 1, None, f["total_label"])
    for i in range(2, 6):
        ws.write_blank(row, i, None, f["total_label"])
    ws.write_formula(row, 6, f'=SUMIFS({mp_cal},{mp_week},$C$7)',
                     f["total_number"])
    ws.write_formula(row, 7, f'=SUMIFS({mp_cost},{mp_week},$C$7)',
                     f["total_money"])
    ws.write_formula(row, 8,
                     f'=TEXT(IFERROR(SUMIFS({mp_cal},{mp_week},$C$7)/'
                     f'MAX(1,Household_Size)/7/Calorie_Target,0),"0%")'
                     f'&" of target"', f["total_label"])
    row += 2

    # ---- overdue meals -------------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  MEALS OVERDUE FOR ANOTHER TURN", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Recipe", "Last cooked", "Days since",
                              "Rating", "Cost / serving"]):
        ws.write(row, i, head, f["header"])
    row += 1
    rot = reg.rng("Recipes", "rotation_rank")
    for n in range(1, 6):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["recipe", "last_planned", "days_since",
                                 "rating", "cost_per_serving"]):
            rng = reg.rng("Recipes", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{rot},0)),"")',
                f["calc_date"] if key == "last_planned"
                else (f["calc_money"] if key == "cost_per_serving"
                      else (f["calc_number"] if key in ("days_since",
                                                        "rating")
                            else f["calc_text"])))
        row += 1
    row += 1

    # ---- cheapest meals ------------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  CHEAPEST MEALS IN YOUR RECIPE BOOK", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Recipe", "Cost / serving",
                              "Calories", "Total time (min)",
                              "Cost / 1000 kcal"]):
        ws.write(row, i, head, f["header"])
    row += 1
    cost_rank = reg.rng("Recipes", "cost_rank")
    for n in range(1, 6):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["recipe", "cost_per_serving", "calories",
                                 "total_time", "cost_per_1000_cal"]):
            rng = reg.rng("Recipes", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{cost_rank},0)),"")',
                f["calc_money"] if key in ("cost_per_serving",
                                           "cost_per_1000_cal")
                else (f["calc_number"] if key in ("calories", "total_time")
                      else f["calc_text"]))
        row += 1
    row += 1

    # ---- use it or lose it ----------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  USE IT OR LOSE IT", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Item", "Days left", "Quantity",
                              "Storage", "Status"]):
        ws.write(row, i, head, f["header"])
    row += 1
    fridge_rank = reg.rng("Pantry", "fridge_rank")
    for n in range(1, 7):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["item", "days_left", "quantity",
                                 "storage", "use_by_status"]):
            rng = reg.rng("Pantry", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{fridge_rank},0)),"")',
                f["calc_number"] if key in ("days_left", "quantity")
                else f["calc_text"])
        row += 1
    row += 1

    # ---- habits and alerts -----------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17, "  HABITS AND ALERTS", f["section"])
    row += 1
    ws.write(row, 0, "Habit", f["header"])
    ws.write(row, 2, "This month", f["header"])
    ws.write(row, 4, "Target", f["header"])
    ws.write(row, 6, "Status", f["header"])
    row += 1
    mp_month = reg.rng("Meal Plan", "month")
    month_cell = "$G$6"
    habits = [
        ("Home cooked meals", f'=COUNTIFS({mp_month},{month_cell},'
                              f'{mp_status},"Cooked")'
                              f'+COUNTIFS({mp_month},{month_cell},'
                              f'{mp_status},"Eaten")',
         "=Home_Cooked_Target*4", "number"),
        ("Takeaways and meals out", f'=COUNTIFS({mp_month},{month_cell},'
                                    f'{mp_status},"Takeaway")'
                                    f'+COUNTIFS({mp_month},{month_cell},'
                                    f'{mp_status},"Eating out")',
         "=Takeaway_Limit", "number"),
        ("New recipes tried", f'=COUNTIFS({reg.rng("Recipes", "added_on")},'
                              f'">="&DATE(Plan_Year,1,1),'
                              f'{reg.rng("Recipes", "added_on")},'
                              f'"<="&DATE(Plan_Year,12,31))',
         "=New_Recipe_Target*12", "number"),
    ]
    for label, formula, target, kind in habits:
        ws.merge_range(row, 0, row, 1, label, f["label"])
        ws.write_formula(row, 2, formula, f["calc_number"])
        ws.write_formula(row, 4, target, f["calc_number"])
        ws.write_formula(row, 6,
                         f'=IF($C{row + 1}>=$E{row + 1},"On target",'
                         f'"Behind target")', f["calc_badge"])
        row += 1

    alerts = [
        ("Grocery spend vs weekly budget",
         f'=Weekly_Budget-SUMIFS({mp_cost},{mp_week},$C$7)',
         f'=IF(SUMIFS({mp_cost},{mp_week},$C$7)>Weekly_Budget,'
         f'"Over budget","Within budget")'),
        ("Waste cost vs target",
         f'=Waste_Cost_Target-SUMIFS({reg.rng("Food Waste", "cost")},'
         f'{reg.rng("Food Waste", "month")},{month_cell})',
         f'=IF(SUMIFS({reg.rng("Food Waste", "cost")},'
         f'{reg.rng("Food Waste", "month")},{month_cell})>'
         f'Waste_Cost_Target,"Over target","On target")'),
        ("Items running low",
         f'=COUNTIFS({reg.rng("Ingredients", "buy_this_week")},"Yes")',
         f'=IF(COUNTIFS({reg.rng("Ingredients", "buy_this_week")},"Yes")'
         f'>0,"Add to the list","Nothing needed")'),
        ("Dietary checks flagged",
         f'=COUNTIFS({reg.rng("Meal Plan", "allergy_flag")},"Check")',
         f'=IF(COUNTIFS({reg.rng("Meal Plan", "allergy_flag")},"Check")>0,'
         f'"Check the plan","All clear")'),
        ("Leftovers to eat",
         f'=COUNTIFS({lo_days},">=0")',
         f'=IF(COUNTIFS({lo_days},"<=1")>0,"Eat something today",'
         f'"Nothing urgent")'),
    ]
    for label, formula, status in alerts:
        ws.merge_range(row, 0, row, 1, label, f["label"])
        ws.write_formula(row, 2, formula, f["calc_money"])
        ws.write_blank(row, 4, None, f["calc_text"])
        ws.merge_range(row, 6, row, 8, None, f["calc_badge"])
        ws.write_formula(row, 6, status, f["calc_badge"])
        row += 1

    writer.write_note(ws, row + 1, 0,
                      "Everything on this page is calculated. Change the "
                      "week at the top, or the month in the cell next to "
                      "'Month', and the whole dashboard follows.", width=17)

    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    ws.print_area(0, 0, row + 2, 17)
````

### `meal_planner_spreadsheet/sheets/weekly_planner.py`

Weekly Planner - one week, day by day *(159 lines)*

````python
"""
Weekly Planner - one week, day by day.

Set the week at the top, then choose what you are having for breakfast,
lunch and dinner each day.  The planner reads the Meal Plan tab, so the
grid shows whatever you have planned there and works out the calories, the
protein and the cost of the whole week as you go.

Tip: the easiest way to fill this in is to plan on the Meal Plan tab - one
row per meal - and this page fills itself in.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Weekly Planner",
        title="Weekly Planner",
        subtitle="One week, day by day - meals, calories and cost",
        columns=[
            Col("day", "Day", 12, "calc"),
            Col("date", "Date", 12, "calc"),
            Col("breakfast", "Breakfast", 26, "calc"),
            Col("lunch", "Lunch", 26, "calc"),
            Col("dinner", "Dinner", 26, "calc"),
            Col("snack", "Snacks", 22, "calc"),
            Col("dessert", "Dessert", 20, "calc"),
            Col("servings", "Servings", 10, "calc"),
            Col("calories", "Calories", 11, "calc"),
            Col("cost", "Cost", 11, "calc"),
            Col("notes", "Notes", 30, "input_text"),
        ],
        rows=7,
        header_row=8,
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 10, "WEEKLY PLANNER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 10,
                   "One week, day by day - meals, calories and cost",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 10,
                   "  |  Dashboard   |   Meal Plan   |   Grocery List   |   "
                   "Print Week   |   Monthly Planner", f["nav"])

    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_serv = reg.rng("Meal Plan", "servings")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 10, "  WHICH WEEK?", f["section"])
    ws.write(5, 0, "Week starting", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 3, "Household", f["label"])
    ws.write_formula(5, 4, "=Household_Name", f["calc_text"])
    ws.write(5, 6, "People", f["label"])
    ws.write_formula(5, 7, "=Household_Size", f["calc_number"])
    ws.write(5, 9, "Budget", f["label"])
    ws.write_formula(5, 10, "=Weekly_Budget", f["calc_money"])
    ws.write(6, 0, "Planned", f["label"])
    ws.write_formula(6, 1,
                     f'=COUNTIFS({reg.rng("Meal Plan", "week_start")},'
                     f'$B$8)&" meals this week"', f["calc_bold"])
    ws.write(6, 3, "Week cost", f["label"])
    ws.write_formula(6, 4, f'=SUMIFS({mp_cost},'
                           f'{reg.rng("Meal Plan", "week_start")},$B$8)',
                     f["calc_money"])
    ws.write(6, 6, "Budget left", f["label"])
    ws.write_formula(6, 7, f'=Weekly_Budget-$E$7', f["calc_money"])
    ws.write(6, 9, "Calories / day", f["label"])
    ws.write_formula(6, 10,
                     f'=IFERROR(SUMIFS({mp_cal},'
                     f'{reg.rng("Meal Plan", "week_start")},$B$8)/'
                     f'MAX(1,Household_Size)/7,0)', f["calc_number"])
    ws.write_formula(7, 1, "=DATEVALUE($B$6)", f["calc_date"])

    # ---- header row ---------------------------------------------------------
    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    # ---- the seven days ------------------------------------------------------
    for offset in range(7):
        row = spec.first_data_row + offset
        r = row + 1                       # Excel row number
        ws.write_formula(row, 0, f'=TEXT($B$8+{offset},"dddd")',
                         f["calc_bold"])
        ws.write_formula(row, 1, f'=$B$8+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack", "Dessert"]):
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$B{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 7, f'=SUMIFS({mp_serv},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 8, f'=SUMIFS({mp_cal},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 9, f'=SUMIFS({mp_cost},{mp_date},$B{r})',
                         f["calc_money"])
        ws.write_blank(row, 10, None, f["input_text_wrap"])
        ws.set_row(row, 22)

    # ---- totals --------------------------------------------------------------
    total_row = spec.last_data_row
    tr = total_row + 1
    ws.write(total_row, 0, "Week total", f["total_label"])
    for i in range(1, 7):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 7, f'=SUM($H${spec.first_data_row + 1}:'
                                   f'$H${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total_row, 8, f'=SUM($I${spec.first_data_row + 1}:'
                                   f'$I${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total_row, 9, f'=SUM($J${spec.first_data_row + 1}:'
                                   f'$J${spec.last_data_row})',
                     f["total_money"])
    ws.write_formula(total_row, 10,
                     f'=IFERROR(TEXT($I{tr}/MAX(1,Household_Size)/7,'
                     f'"#,##0")&" kcal a day","")', f["total_label"])

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row, 10)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
````

### `meal_planner_spreadsheet/sheets/monthly_planner.py`

Monthly Planner - the whole month on one page *(135 lines)*

````python
"""
Monthly Planner - the whole month on one page.

Set the month at the top and the six weeks of that month are laid out with
a theme for each week, what the planned meals cost, what you actually spent
and how that compares with the weekly budget.  It is the page to look at
when you are deciding whether next month needs a cheaper plan.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Monthly Planner",
        title="Monthly Planner",
        subtitle="The whole month on one page - themes, planned cost and "
                 "actual spend",
        columns=[
            Col("week", "Week", 10, "calc"),
            Col("week_start", "Week starting", 13, "calc"),
            Col("breakfast_theme", "Breakfast theme", 22, "text"),
            Col("lunch_theme", "Lunch theme", 22, "text"),
            Col("dinner_theme", "Dinner theme", 24, "text"),
            Col("planned_cost", "Planned cost", 12, "calc"),
            Col("actual_cost", "Actual spend", 12, "calc"),
            Col("budget", "Budget", 12, "calc"),
            Col("variance", "Variance", 11, "calc"),
            Col("notes", "Notes", 30, "text_wrap"),
        ],
        rows=6,
        header_row=8,
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 9, "MONTHLY PLANNER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 9,
                   "The whole month on one page - themes, planned cost and "
                   "actual spend", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 9,
                   "  |  Dashboard   |   Weekly Planner   |   Meal Plan   |   "
                   "Grocery Spending   |   Budget", f["nav"])

    mp_week = reg.rng("Meal Plan", "week_start")
    mp_cost = reg.rng("Meal Plan", "cost")
    gs_week = reg.rng("Grocery Spending", "week_start")
    gs_total = reg.rng("Grocery Spending", "line_total")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 9, "  WHICH MONTH?", f["section"])
    ws.write(5, 0, "Month", f["label"])
    ws.write_string(5, 1, cfg.today.strftime("%B %Y"), f["input_text"])
    ws.write(5, 3, "Weeks in the month", f["label"])
    ws.write_formula(5, 4, '=6', f["calc_number"])
    ws.write(5, 6, "Monthly budget", f["label"])
    ws.write_formula(5, 7, "=Monthly_Budget", f["calc_money"])
    ws.write_formula(6, 1, '=DATEVALUE("1 "&$B$6)', f["calc_date"])
    ws.write(6, 3, "Month planned", f["label"])
    ws.write_formula(6, 4, f'=SUM($G$9:$G$14)', f["calc_money"])
    ws.write(6, 6, "Month actual", f["label"])
    ws.write_formula(6, 7, f'=SUM($H$9:$H$14)', f["calc_money"])
    ws.write(6, 9, "Variance", f["label"])

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    for offset in range(6):
        row = spec.first_data_row + offset
        r = row + 1
        ws.write_number(row, 0, offset + 1, f["calc_center"])
        ws.write_formula(row, 1,
                         f'=$B$7+{offset}*7-WEEKDAY($B$7,2)+1',
                         f["calc_date"])
        ws.write_blank(row, 2, None, f["input_text"])
        ws.write_blank(row, 3, None, f["input_text"])
        ws.write_blank(row, 4, None, f["input_text"])
        ws.write_formula(row, 5, f'=SUMIFS({mp_cost},{mp_week},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 6, f'=SUMIFS({gs_total},{gs_week},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 7, "=Weekly_Budget", f["calc_money"])
        ws.write_formula(row, 8, f'=$H{r}-$G{r}', f["calc_money"])
        ws.write_blank(row, 9, None, f["input_text_wrap"])
        ws.set_row(row, 22)

    total_row = spec.last_data_row
    ws.write(total_row, 0, "Month", f["total_label"])
    for i in range(1, 5):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 5, f'=SUM($F$9:$F${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 6, f'=SUM($G$9:$G${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 7, f'=SUM($H$9:$H${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 8, f'=$H{total_row + 1}-$G{total_row + 1}',
                     f["total_money"])
    ws.write_formula(total_row, 9,
                     f'=IF($H{total_row + 1}=0,"",'
                     f'TEXT(($G{total_row + 1}-$H{total_row + 1})/'
                     f'$H{total_row + 1},"0%")&" of budget left")',
                     f["total_label"])

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row, 9)
````

### `meal_planner_spreadsheet/sheets/nutrition.py`

Nutrition - the daily log against your targets *(232 lines)*

````python
"""
Nutrition - the daily log against your targets.

Either type a recipe in (the nutrition is looked up from the Recipes tab)
or type the numbers straight in.  The percentages compare the day with the
targets you set on Settings, and the summary block at the top shows the
monthly averages for whatever month you pick.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    columns = [
        Col("date", "Date", 12, "date", group="when"),
        Col("month", "Month", 11, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("weekday", "Day", 8, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"ddd"))'),
        Col("slot", "Meal slot", 15, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "meal_slot")}),
        Col("recipe", "Recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("calories", "Calories", 10, "calc", group="actual",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("calories"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("protein", "Protein (g)", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("protein"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("carbs", "Carbs (g)", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("carbs"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("fat", "Fat (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fat"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("fibre", "Fibre (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fibre"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("sugar", "Sugar (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("sugar"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("sodium", "Sodium (mg)", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("sodium"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("water_glasses", "Water (glasses)", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 30}),
        Col("calorie_target", "Calories target", 12, "calc",
            group="targets",
            formula='=IF({date}{r}="","",Calorie_Target*Household_Size)'),
        Col("calorie_pct", "% calories", 11, "calc",
            formula='=IF(OR({date}{r}="",{calorie_target}{r}=0),"",'
                    'IFERROR({calories}{r}/{calorie_target}{r},""))'),
        Col("protein_pct", "% protein", 11, "calc",
            formula='=IF(OR({date}{r}="",Protein_Target=0),"",'
                    'IFERROR({protein}{r}/(Protein_Target*'
                    'Household_Size),""))'),
        Col("carb_pct", "% carbs", 10, "calc",
            formula='=IF(OR({date}{r}="",Carb_Target=0),"",'
                    'IFERROR({carbs}{r}/(Carb_Target*Household_Size),""))'),
        Col("fat_pct", "% fat", 10, "calc",
            formula='=IF(OR({date}{r}="",Fat_Target=0),"",'
                    'IFERROR({fat}{r}/(Fat_Target*Household_Size),""))'),
        Col("fibre_pct", "% fibre", 10, "calc",
            formula='=IF(OR({date}{r}="",Fibre_Target=0),"",'
                    'IFERROR({fibre}{r}/(Fibre_Target*Household_Size),'
                    '""))'),
        Col("sugar_pct", "% sugar limit", 11, "calc",
            formula='=IF(OR({date}{r}="",Sugar_Limit=0),"",'
                    'IFERROR({sugar}{r}/(Sugar_Limit*Household_Size),'
                    '""))'),
        Col("sodium_pct", "% sodium limit", 11, "calc",
            formula='=IF(OR({date}{r}="",Sodium_Limit=0),"",'
                    'IFERROR({sodium}{r}/(Sodium_Limit*Household_Size),'
                    '""))'),
        Col("status", "Status", 13, "calc",
            formula='=IF({date}{r}="","",'
                    'IF({calorie_pct}{r}="","",'
                    'IF({calorie_pct}{r}>1.1,"Over target",'
                    'IF({calorie_pct}{r}<0.8,"Under target",'
                    '"On target"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Nutrition",
        title="Nutrition",
        subtitle="Daily nutrition log against the targets set on Settings",
        columns=columns,
        rows=cfg.row_count("Nutrition"),
        header_row=18,
        tab_color=Palette.primary,
        freeze_cols=3,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    writer.grid_off(ws)
    ws.set_column(0, 0, 12)
    ws.set_column(1, 1, 11)
    ws.set_column(2, 2, 8)
    ws.set_column(3, 3, 15)
    ws.set_column(4, 4, 26)
    ws.set_column(5, 5, 10)
    for i in range(6, 21):
        ws.set_column(i, i, 11)
    ws.set_column(21, 21, 13)
    ws.set_column(22, 22, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 8, "NUTRITION", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Daily nutrition log against the targets set on "
                   "Settings", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Dashboard   |   Settings   |   Meal Plan   |   "
                   "Recipes   |   Reports", f["nav"])

    # ---- month picker and monthly averages -------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  MONTH SUMMARY", f["section"])
    ws.write(5, 0, "Month", f["label"])
    ws.write_string(5, 1, cfg.today.strftime("%b %Y"), f["input_text"])
    ws.write(5, 2, "days logged", f["label"])
    ws.write_formula(
        5, 3, '=COUNTIFS(' + writer.registry.rng("Nutrition", "month")
        + ',$B$6)', f["calc_number"])

    cal = writer.registry.rng("Nutrition", "calories")
    mon = writer.registry.rng("Nutrition", "month")
    pro = writer.registry.rng("Nutrition", "protein")
    carb = writer.registry.rng("Nutrition", "carbs")
    fat = writer.registry.rng("Nutrition", "fat")
    fib = writer.registry.rng("Nutrition", "fibre")
    sug = writer.registry.rng("Nutrition", "sugar")
    sod = writer.registry.rng("Nutrition", "sodium")

    kpis = [
        ("Average calories", cal, "#,##0", 7),
        ("Average protein (g)", pro, "#,##0", 8),
        ("Average carbs (g)", carb, "#,##0", 9),
        ("Average fat (g)", fat, "#,##0", 10),
        ("Average fibre (g)", fib, "#,##0", 11),
        ("Average sugar (g)", sug, "#,##0", 12),
        ("Average sodium (mg)", sod, "#,##0", 13),
    ]
    for label, rng, num_format, col in kpis:
        ws.write(7, col, label, f["kpi_label"])
        ws.write_formula(8, col,
                         f'=IFERROR(AVERAGEIFS({rng},{mon},$B$6),0)',
                         f["kpi_value"])
        ws.write(9, col, f"= {label.split()[1]}", f["kpi_sub"])
    ws.set_row(8, 30)

    ws.write(11, 0, "Target", f["label"])
    ws.write_formula(11, 1, "=Calorie_Target*Household_Size",
                     f["calc_number"])
    ws.write(11, 2, "vs target", f["label"])
    ws.write_formula(11, 3,
                     '=IFERROR(AVERAGEIFS(' + cal + ',' + mon
                     + ',$B$6)/(Calorie_Target*Household_Size),"")',
                     f["calc_percent"])
    ws.write(11, 4, "days on target", f["label"])
    ws.write_formula(11, 5,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"On target")', f["calc_number"])
    ws.write(11, 6, "days over", f["label"])
    ws.write_formula(11, 7,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"Over target")', f["calc_number"])
    ws.write(11, 8, "days under", f["label"])
    ws.write_formula(11, 9,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"Under target")', f["calc_number"])

    writer.write_note(ws, 13, 0,
                      "Type a recipe name in the Recipe column and the "
                      "nutrition is looked up for you. To enter the "
                      "numbers by hand instead, leave Recipe blank and "
                      "type over the calculated cells - the sheet is "
                      "protected, so unprotect it first if you want to "
                      "keep your own numbers.", width=9)

    # ---- the daily log ----------------------------------------------------
    writer.register(ws, spec)
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
````

### `meal_planner_spreadsheet/sheets/budget.py`

Budget - planned versus actual food spend, month by month *(178 lines)*

````python
"""
Budget - planned versus actual food spend, month by month.

The grocery column is read from the Grocery Spending tab, the waste column
from the Food Waste tab, and the planned columns come from Settings.  The
summary at the top shows the year to date position for the planning year.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_month = lists("Grocery Spending", "month")
    gs_total = lists("Grocery Spending", "line_total")
    fw_month = lists("Food Waste", "month")
    fw_cost = lists("Food Waste", "cost")

    columns = [
        Col("month", "Month", 12, "text", group="when",
            note="Type it as 'Jan 2026' to match the other tabs."),
        Col("planned_groceries", "Planned groceries", 13, "calc",
            group="groceries",
            formula='=IF({month}{r}="","",Weekly_Budget*52/12)'),
        Col("actual_groceries", "Actual groceries", 13, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_month + ','
                    '{month}{r}))'),
        Col("variance", "Variance", 11, "calc",
            formula='=IF({month}{r}="","",'
                    '{planned_groceries}{r}-{actual_groceries}{r})'),
        Col("planned_eating_out", "Planned eating out", 13, "calc",
            group="eating out",
            formula='=IF({month}{r}="","",Eating_Out_Budget)'),
        Col("actual_eating_out", "Actual eating out", 13, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("eating_out_variance", "Variance", 11, "calc",
            formula='=IF({month}{r}="","",'
                    '{planned_eating_out}{r}-'
                    'IF({actual_eating_out}{r}="",0,'
                    '{actual_eating_out}{r}))'),
        Col("waste_cost", "Waste cost", 11, "calc", group="waste",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_cost + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("total_planned", "Total planned", 12, "calc",
            group="totals",
            formula='=IF({month}{r}="","",'
                    '{planned_groceries}{r}+{planned_eating_out}{r})'),
        Col("total_actual", "Total actual", 12, "calc",
            formula='=IF({month}{r}="","",'
                    '{actual_groceries}{r}+'
                    'IF({actual_eating_out}{r}="",0,'
                    '{actual_eating_out}{r})+{waste_cost}{r})'),
        Col("total_variance", "Total variance", 12, "calc",
            formula='=IF({month}{r}="","",'
                    '{total_planned}{r}-{total_actual}{r})'),
        Col("rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({total_actual}{r}="","",'
                    'COUNTIFS({total_actual_first}:{total_actual_last},'
                    '">"&{total_actual}{r})+1)'),
        Col("status", "Status", 14, "calc",
            formula='=IF({month}{r}="","",'
                    'IF({total_variance}{r}="","",'
                    'IF({total_variance}{r}<0,"Over budget",'
                    'IF({total_variance}{r}<Monthly_Budget*0.1,'
                    '"Close","Under budget"))))'),
        Col("running_total", "Running total", 12, "calc",
            formula='=IF({total_actual}{r}="","",'
                    'SUM({total_actual_first}:{total_actual}{r}))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Budget",
        title="Budget",
        subtitle="Planned versus actual food spend, month by month",
        columns=columns,
        rows=cfg.row_count("Budget"),
        header_row=16,
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    writer.grid_off(ws)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 2, 14)
    ws.set_column(3, 3, 12)
    ws.set_column(4, 5, 14)
    ws.set_column(6, 6, 12)
    ws.set_column(7, 7, 12)
    ws.set_column(8, 10, 13)
    ws.set_column(11, 11, 11)
    ws.set_column(12, 12, 14)
    ws.set_column(13, 13, 13)
    ws.set_column(14, 14, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 10, "BUDGET", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 10,
                   "Planned versus actual food spend, month by month",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 10,
                   "  |  Dashboard   |   Settings   |   Grocery Spending   "
                   "|   Food Waste   |   Reports", f["nav"])

    reg = writer.registry
    month_rng = reg.rng("Budget", "month")
    actual_rng = reg.rng("Budget", "actual_groceries")
    total_rng = reg.rng("Budget", "total_actual")
    waste_rng = reg.rng("Budget", "waste_cost")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 10, "  YEAR TO DATE", f["section"])
    ws.write(5, 0, "Planning year", f["label"])
    ws.write_formula(5, 1, "=Plan_Year", f["calc_number"])

    tiles = [
        ("Grocery spend YTD", f'=SUMIFS({actual_rng},{month_rng},"<>")',
         "kpi_value_money", 3),
        ("Total food spend YTD", f'=SUM({total_rng})', "kpi_value_money", 5),
        ("Waste cost YTD", f'=SUM({waste_rng})', "kpi_value_money", 7),
        ("Monthly budget", "=Monthly_Budget", "kpi_value_money", 9),
    ]
    for label, formula, style, col in tiles:
        ws.write(7, col, label, f["kpi_label"])
        ws.write_formula(8, col, formula, f[style])
    ws.set_row(8, 30)

    ws.write(10, 0, "Average month", f["label"])
    ws.write_formula(10, 1, f'=IFERROR(AVERAGE({total_rng}),0)',
                     f["total_money"])
    ws.write(10, 2, "Months over budget", f["label"])
    ws.write_formula(10, 3,
                     '=COUNTIFS(' + reg.rng("Budget", "status")
                     + ',"Over budget")', f["calc_number"])
    ws.write(10, 4, "Months under", f["label"])
    ws.write_formula(10, 5,
                     '=COUNTIFS(' + reg.rng("Budget", "status")
                     + ',"Under budget")', f["calc_number"])
    ws.write(10, 6, "Waste as % of spend", f["label"])
    ws.write_formula(10, 7,
                     f'=IFERROR(SUM({waste_rng})/SUM({actual_rng}),0)',
                     f["calc_percent"])
    ws.write(10, 8, "Target", f["label"])
    ws.write_formula(10, 9, "=Waste_Reduction_Target", f["calc_percent"])

    writer.write_note(ws, 12, 0,
                      "Add one row per month. The planned columns come from "
                      "Settings, the actual grocery and waste columns come "
                      "from the Grocery Spending and Food Waste tabs, and "
                      "you type in what you spent eating out.", width=10)

    writer.register(ws, spec)
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
````

### `meal_planner_spreadsheet/sheets/goals.py`

Goals - habit goals with a live progress bar *(153 lines)*

````python
"""
Goals - habit goals with a live progress bar.

Set a target, record where you are now and the bar in the progress column
fills up as you go.  The status column tells you whether you are on track
for the deadline, and the summary at the top counts how many goals are
running, hit or slipping.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

CATEGORIES = ["Waste", "Budget", "Nutrition", "Variety", "Cooking",
              "Shopping", "Health", "Family"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("goal", "Goal", 34, "text", group="what",
            note="Say what you want to change, in your own words."),
        Col("category", "Category", 13, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("target", "Target", 11, "number", group="numbers",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("current", "Where you are now", 13, "number",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("unit", "Unit", 12, "text",
            note="e.g. meals a week, % of spend, kg a month."),
        Col("deadline", "By", 12, "date"),
        Col("progress", "Progress", 11, "calc", group="tracking",
            formula='=IF(OR({goal}{r}="",{target}{r}="",{target}{r}=0),"",'
                    'MIN(1,{current}{r}/{target}{r}))'),
        Col("status", "Status", 15, "calc",
            formula='=IF({goal}{r}="","",'
                    'IF({progress}{r}="","",'
                    'IF({progress}{r}>=1,"Goal hit",'
                    'IF({deadline}{r}="","In progress",'
                    'IF({deadline}{r}<TODAY(),"Missed deadline",'
                    'IF({progress}{r}>=0.5,"On track","Needs work"))))))'),
        Col("streak", "Current streak", 12, "number",
            validate={"type": "integer", "between": 0, "and": 9999}),
        Col("best_streak", "Best streak", 11, "number",
            validate={"type": "integer", "between": 0, "and": 9999}),
        Col("rank", "Rank", 9, "calc", group="rankings",
            formula='=IF({progress}{r}="","",'
                    'COUNTIFS({progress_first}:{progress_last},'
                    '">"&{progress}{r})+1)'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Goals",
        title="Goals",
        subtitle="Habit goals with a live progress bar",
        columns=columns,
        rows=cfg.row_count("Goals"),
        header_row=14,
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 36)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 3, 14)
    ws.set_column(4, 4, 13)
    ws.set_column(5, 5, 12)
    ws.set_column(6, 6, 12)
    ws.set_column(7, 7, 16)
    ws.set_column(8, 9, 13)
    ws.set_column(10, 10, 9)
    ws.set_column(11, 11, 34)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 8, "GOALS", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Habit goals with a live progress bar", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Dashboard   |   Settings   |   Food Waste   |   "
                   "Sustainability   |   Help", f["nav"])

    status_rng = reg.rng("Goals", "status")
    progress_rng = reg.rng("Goals", "progress")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  WHERE YOU ARE", f["section"])
    tiles = [
        ("Goals running", f'=COUNTIFS({status_rng},"<>")', "kpi_value", 1),
        ("Goals hit", f'=COUNTIFS({status_rng},"Goal hit")', "kpi_value", 3),
        ("On track", f'=COUNTIFS({status_rng},"On track")', "kpi_value", 5),
        ("Needs work", f'=COUNTIFS({status_rng},"Needs work")',
         "kpi_value", 7),
    ]
    for label, formula, style, col in tiles:
        ws.write(6, col, label, f["kpi_label"])
        ws.write_formula(7, col, formula, f[style])
    ws.set_row(7, 30)

    ws.write(9, 0, "Average progress", f["label"])
    ws.write_formula(9, 1, f'=IFERROR(AVERAGE({progress_rng}),0)',
                     f["total_percent"])
    ws.write(9, 2, "Best goal", f["label"])
    ws.write_formula(9, 3,
                     '=IFERROR(INDEX(' + reg.rng("Goals", "goal")
                     + ',MATCH(MAX(' + progress_rng + '),' + progress_rng
                     + ',0)),"")', f["calc_text"])
    ws.write(9, 4, "Longest streak", f["label"])
    ws.write_formula(9, 5,
                     '=IFERROR(MAX(' + reg.rng("Goals", "streak") + '),0)',
                     f["calc_number"])

    writer.write_note(ws, 11, 0,
                      "The progress bar is a data bar: it fills up as the "
                      "'Where you are now' column approaches the target. "
                      "Anything at 100% turns green.", width=8)

    writer.register(ws, spec)

    # progress bar + colour the status
    letter = spec.letter("progress")
    rng = f"${letter}${spec.first_data_row}:${letter}${spec.last_data_row}"
    ws.conditional_format(rng, {
        "type": "data_bar", "bar_color": Palette.primary_mid,
        "bar_solid": True, "min_type": "num", "min_value": 0,
        "max_type": "num", "max_value": 1})
    ws.conditional_format(rng, {"type": "cell", "criteria": ">=",
                                "value": 1, "format": f["status_good"]})

    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
````

### `meal_planner_spreadsheet/sheets/reports.py`

Reports - any date range, on one page *(297 lines)*

````python
"""
Reports - any date range, on one page.

Set the from and to dates at the top and every table below re-calculates:
what you spent, where you spent it, what you threw away and why, how the
nutrition looked, which meals you cooked most and which ingredients you buy
most often.  Nothing here needs a chart - the numbers are the report.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Reports",
        title="Reports",
        subtitle="Spend, nutrition, waste, variety and cooking habits for any "
                 "date range",
        columns=[
            Col("metric", "Metric", 30, "text"),
            Col("value", "Value", 16, "text"),
            Col("previous", "Previous", 16, "text"),
            Col("change", "Change", 14, "text"),
            Col("note", "Note", 40, "text_wrap"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.primary,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, width in enumerate([34, 18, 18, 16, 44]):
        ws.set_column(i, i, width)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 4, "REPORTS", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 4,
                   "Spend, nutrition, waste, variety and cooking habits for "
                   "any date range", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 4,
                   "  |  Dashboard   |   Grocery Spending   |   Food Waste   "
                   "|   Nutrition   |   Meal Plan", f["nav"])

    # ---- date range --------------------------------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 4, "  REPORTING PERIOD", f["section"])
    ws.write(5, 0, "From", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 2, "To", f["label"])
    ws.write_string(5, 3, "", f["input_text"])
    ws.write(5, 4, "Type the dates as yyyy-mm-dd.", f["note"])

    # helper cells: real dates so SUMIFS can compare them
    ws.write_formula(6, 0, '=DATEVALUE($B$6)', f["calc_date"])
    ws.write_formula(6, 1, '=IF($D$6="",TODAY(),DATEVALUE($D$6))',
                     f["calc_date"])
    ws.write(6, 2, "Days in period", f["label"])
    ws.write_formula(6, 3, '=$B$7-$A$7+1', f["calc_number"])
    ws.write(6, 4, "The two grey cells turn your text into real dates.",
             f["note"])

    gs_date = reg.rng("Grocery Spending", "date")
    gs_total = reg.rng("Grocery Spending", "line_total")
    gs_store = reg.rng("Grocery Spending", "store")
    gs_item = reg.rng("Grocery Spending", "item")
    gs_cat = reg.rng("Grocery Spending", "category")
    fw_date = reg.rng("Food Waste", "date")
    fw_cost = reg.rng("Food Waste", "cost")
    fw_qty = reg.rng("Food Waste", "qty")
    fw_reason = reg.rng("Food Waste", "reason")
    mp_date = reg.rng("Meal Plan", "date")
    mp_status = reg.rng("Meal Plan", "status")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    nu_date = reg.rng("Nutrition", "date")
    nu_cal = reg.rng("Nutrition", "calories")

    def sumifs(value_rng, date_rng):
        return (f'SUMIFS({value_rng},{date_rng},">="&$A$7,'
                f'{date_rng},"<="&$B$7)')

    def countifs(date_rng, extra=""):
        return (f'COUNTIFS({date_rng},">="&$A$7,'
                f'{date_rng},"<="&$B$7{extra})')

    # ---- headline numbers --------------------------------------------------
    row = 8
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  HEADLINE NUMBERS", f["section"])
    row += 1
    cooked_total = (countifs(mp_date, ',"Cooked"') + "+"
                    + countifs(mp_date, ',"Eaten"'))
    takeaways_total = (countifs(mp_date, ',"Takeaway"') + "+"
                       + countifs(mp_date, ',"Eating out"'))
    headlines = [
        ("Grocery spend", sumifs(gs_total, gs_date), "money",
         "Everything recorded on the Grocery Spending tab."),
        ("Shops recorded", countifs(gs_date), "number",
         "How many spending rows fall inside the period."),
        ("Average shop", f'IFERROR({sumifs(gs_total, gs_date)}/'
                         f'MAX(1,{countifs(gs_date)}),0)', "money", ""),
        ("Weekly average", f'IFERROR({sumifs(gs_total, gs_date)}/'
                           f'MAX(1,$D$7/7),0)', "money",
         "Compared with the weekly budget on Settings."),
        ("Vs weekly budget", f'IFERROR({sumifs(gs_total, gs_date)}/'
                             f'MAX(1,$D$7/7)-Weekly_Budget,0)', "money", ""),
        ("Meals planned", countifs(mp_date), "number", ""),
        ("Meals cooked", cooked_total, "number", ""),
        ("Takeaways / eating out", takeaways_total, "number", ""),
        ("Home cooked %", f'IFERROR(({cooked_total})/'
                          f'MAX(1,{countifs(mp_date)}),0)', "percent", ""),
        ("Waste cost", sumifs(fw_cost, fw_date), "money", ""),
        ("Waste quantity", sumifs(fw_qty, fw_date), "number", ""),
        ("Waste as % of spend", f'IFERROR({sumifs(fw_cost, fw_date)}/'
                                f'MAX(0.01,{sumifs(gs_total, gs_date)}),0)',
         "percent", "Target is set on Settings."),
        ("Average calories a day", f'IFERROR({sumifs(nu_cal, nu_date)}/'
                                   f'MAX(1,COUNTIFS({nu_date},">="&$A$7,'
                                   f'{nu_date},"<="&$B$7)),0)', "number", ""),
    ]
    for label, formula, kind, note in headlines:
        ws.write(row, 0, label, f["label"])
        style = {"money": f["total_money"], "number": f["total_number"],
                 "percent": f["total_percent"]}[kind]
        ws.write_formula(row, 1, "=" + formula, style)
        if note:
            ws.write(row, 4, note, f["note"])
        row += 1

    # ---- spend by store ----------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  SPEND BY STORE", f["section"])
    row += 1
    for store in ["Greenfield Market", "Corner Grocer", "Bulk Barn",
                  "Farmers Market", "Asian Supermarket"]:
        ws.write(row, 0, store, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_store},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=COUNTIFS({gs_store},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_number"])
        ws.write(row, 3, "visits", f["note"])
        row += 1

    # ---- spend by category --------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  SPEND BY CATEGORY", f["section"])
    row += 1
    for category in ["Vegetables", "Fruit", "Meat & Fish", "Dairy & Eggs",
                     "Bakery", "Grains & Pasta", "Tins & Jars", "Frozen",
                     "Snacks", "Drinks", "Household"]:
        ws.write(row, 0, category, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_cat},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=IFERROR(SUMIFS({gs_total},{gs_cat},'
                         f'$A{row + 1},{gs_date},">="&$A$7,'
                         f'{gs_date},"<="&$B$7)/MAX(0.01,'
                         f'SUMIFS({gs_total},{gs_date},">="&$A$7,'
                         f'{gs_date},"<="&$B$7)),0)', f["total_percent"])
        ws.write(row, 3, "of spend", f["note"])
        row += 1

    # ---- waste by reason -----------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  WASTE BY REASON", f["section"])
    row += 1
    for reason in ["Expired", "Spoiled", "Mouldy", "Leftover not eaten",
                   "Cooked too much", "Burnt", "Tasted bad",
                   "Bought too much", "Child refused", "Plans changed"]:
        ws.write(row, 0, reason, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({fw_cost},{fw_reason},$A{row + 1},'
                         f'{fw_date},">="&$A$7,{fw_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=SUMIFS({fw_qty},{fw_reason},$A{row + 1},'
                         f'{fw_date},">="&$A$7,{fw_date},"<="&$B$7)',
                         f["total_number"])
        ws.write(row, 3, "quantity", f["note"])
        row += 1

    # ---- most cooked meals ---------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  MOST COOKED MEALS", f["section"])
    row += 1
    ws.write(row, 0, "Recipe", f["header"])
    ws.write(row, 1, "Times cooked", f["header"])
    ws.write(row, 2, "Last cooked", f["header"])
    ws.write(row, 3, "Cost / serving", f["header"])
    ws.write(row, 4, "Rating", f["header"])
    row += 1
    for recipe in ["Chicken & veg traybake", "Spaghetti bolognese",
                   "Vegetable curry", "Salmon & rice", "Beef chilli",
                   "Pizza night", "Pasta primavera", "Fish finger sandwich"]:
        r = row + 1
        ws.write(row, 0, recipe, f["label"])
        ws.write_formula(row, 1,
                         f'=COUNTIFS({mp_recipe},$A{r},{mp_date},'
                         f'">="&$A$7,{mp_date},"<="&$B$7,'
                         f'{mp_status},"Cooked")'
                         f'+COUNTIFS({mp_recipe},$A{r},{mp_date},'
                         f'">="&$A$7,{mp_date},"<="&$B$7,'
                         f'{mp_status},"Eaten")', f["total_number"])
        ws.write_formula(row, 2,
                         f'=IF(SUMPRODUCT(MAX(({mp_recipe}=$A{r})*'
                         f'{mp_date}))=0,"",'
                         f'SUMPRODUCT(MAX(({mp_recipe}=$A{r})*{mp_date})))',
                         f["calc_date"])
        ws.write_formula(row, 3,
                         '=IFERROR(INDEX(' + reg.rng("Recipes",
                                                     "cost_per_serving")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Recipes", "recipe") + ',0)),"")',
                         f["calc_money"])
        ws.write_formula(row, 4,
                         '=IFERROR(INDEX(' + reg.rng("Recipes", "rating")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Recipes", "recipe") + ',0)),"")',
                         f["calc_number"])
        row += 1

    # ---- top ingredients ------------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  TOP INGREDIENTS BY SPEND", f["section"])
    row += 1
    ws.write(row, 0, "Ingredient", f["header"])
    ws.write(row, 1, "Spend in period", f["header"])
    ws.write(row, 2, "Times bought", f["header"])
    ws.write(row, 3, "Last price", f["header"])
    ws.write(row, 4, "Average price", f["header"])
    row += 1
    for item in ["Chicken breast", "Rice", "Eggs", "Milk", "Bread",
                 "Cheddar cheese", "Pasta", "Tinned tomatoes"]:
        r = row + 1
        ws.write(row, 0, item, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_item},$A{r},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=COUNTIFS({gs_item},$A{r},{gs_date},'
                         f'">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_number"])
        ws.write_formula(row, 3,
                         '=IFERROR(INDEX(' + reg.rng("Ingredients",
                                                     "last_price")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Ingredients", "ingredient") + ',0)),'
                         '"")', f["calc_money"])
        ws.write_formula(row, 4,
                         '=IFERROR(INDEX(' + reg.rng("Ingredients",
                                                     "avg_price")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Ingredients", "ingredient") + ',0)),'
                         '"")', f["calc_money"])
        row += 1

    writer.write_note(ws, row + 1, 0,
                      "Every table reads the Grocery Spending, Food Waste, "
                      "Meal Plan and Nutrition tabs, so they fill in as you "
                      "record your shops and your meals. Change the dates at "
                      "the top of the page to re-cut the whole report.",
                      width=4)

    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    ws.print_area(0, 0, row + 2, 4)
````

### `meal_planner_spreadsheet/sheets/start_here.py`

Start Here - the landing tab the buyer sees first *(200 lines)*

````python
"""
Start Here - the landing tab the buyer sees first.

A one page tour: what the workbook does, the five step set up, the colour
key (cream = type here, sage = calculated, do not touch) and an index of
every tab with a click-through link.
"""

from __future__ import annotations

try:
    from ..build import SHEET_ORDER
    from ..config import AUTHOR, Config, Palette, PRODUCT_NAME
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from build import SHEET_ORDER
    from config import AUTHOR, Config, Palette, PRODUCT_NAME
    from layout import Col, Registry, SheetSpec
    from writer import Writer

STEPS = [
    ("1. Set up your household",
     "Settings tab: household name, number of people, servings per meal, "
     "currency, measurement system, grocery budget and your nutrition "
     "targets. Everything else reads from here."),
    ("2. Add your ingredients",
     "Ingredients tab: name, category, unit, price and the nutrition per "
     "unit. These prices drive every recipe cost and grocery total, so add "
     "the staples you buy most often first."),
    ("3. Build your recipe book",
     "Recipes tab: title, category, servings, timings and the nutrition per "
     "serving. Recipe Ingredients tab: list each ingredient with its "
     "quantity and the cost per serving is calculated for you."),
    ("4. Plan the week",
     "Weekly Planner tab: pick a week starting date, then choose a recipe "
     "for each day and slot. The planner works out the calories, protein "
     "and cost of the whole week as you type."),
    ("5. Shop and cook",
     "Grocery List tab: everything you planned is already there, grouped "
     "by aisle, with quantities scaled to your household. Print it with "
     "Print Shopping, then tick items off as you fill the basket."),
]

COLOUR_KEY = [
    ("Cream cells", "You type here. These cells are unlocked.", "input_text"),
    ("Soft sage cells", "Calculated by the spreadsheet. Leave them alone.",
     "calc_text"),
    ("Green headers", "Column titles - hover for a note about the column.",
     "header"),
    ("Terracotta", "Totals, targets and anything that needs attention.",
     "kpi_value_money"),
]

TAB_GUIDE = [
    ("Start Here", "This page."),
    ("Dashboard", "The week at a glance: calories, budget, what to cook, "
                  "what is expiring and how your habits are going."),
    ("Weekly Planner", "Pick the meals for one week, day by day."),
    ("Monthly Planner", "The whole month on one page with the food budget "
                        "per week."),
    ("Settings", "Household, budget, nutrition targets and reminder "
                 "windows."),
    ("Lists", "Every drop down source: meal slots, units, categories, "
              "cuisines, stores, diets."),
    ("Household", "Who you are cooking for, their diets, allergies and "
                  "calorie needs."),
    ("Recipes", "Your recipe book with nutrition, cost and rankings."),
    ("Recipe Ingredients", "What goes into each recipe and what it costs."),
    ("Ingredients", "Master ingredient list with prices and nutrition."),
    ("Meal Plan", "Every planned meal in one long register - the engine "
                  "behind the planner."),
    ("Grocery List", "The automatic shopping list, grouped by aisle."),
    ("Pantry", "What you have, what is running low, what expires next."),
    ("Staples", "The things you buy every week, with buy-by reminders."),
    ("Leftovers", "What is in the fridge or freezer and when to eat it."),
    ("Food Waste", "What got thrown away, why, and what it cost."),
    ("Meal Prep", "Batch cooking tasks and what to do when."),
    ("Dietary Filters", "Allergies and dietary needs, and which recipes "
                        "are safe."),
    ("Nutrition", "Daily nutrition log against your targets."),
    ("Budget", "Planned versus actual food spend, month by month."),
    ("Recipe Costs", "Cost per serving for every recipe."),
    ("Converter", "Unit conversions plus a live converter you can use."),
    ("Rotation", "How often each meal repeats, so nothing gets boring."),
    ("Food Safety", "How long food keeps, and safe storage temperatures."),
    ("Fridge & Freezer", "Batch cooked portions and their use-by dates."),
    ("Grocery Spending", "Every shop you record, against the budget."),
    ("Store Prices", "Price comparison for the same item across stores."),
    ("Stores", "Your shops, with spend and best-for notes."),
    ("Events", "Parties, holidays and dinner guests, with a menu budget."),
    ("Event Menu", "The recipes and quantities for each event."),
    ("Goals", "Habit goals with live progress."),
    ("Sustainability", "Waste, packaging and local shopping metrics."),
    ("Reports", "Any date range: spend, nutrition, waste, variety."),
    ("Print Week", "A printable weekly meal plan for the fridge door."),
    ("Print Shopping", "A printable grocery list."),
    ("Print Recipe", "A printable recipe card."),
    ("Help", "Frequently asked questions and troubleshooting."),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Start Here",
        title="Start Here",
        subtitle=cfg.product_subtitle,
        columns=[
            Col("section", "Section", 30, "text"),
            Col("heading", "Heading", 26, "text"),
            Col("body", "Body", 90, "text_wrap"),
            Col("note", "Note", 26, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    p, f = Palette, writer.fmt
    writer.grid_off(ws)
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 78)
    ws.set_column(3, 3, 22)

    ws.set_row(0, 42)
    ws.merge_range(0, 0, 0, 3, "MEAL PLANNER & GROCERY LIST", f["title"])
    ws.set_row(1, 20)
    ws.merge_range(1, 0, 1, 3, cfg.product_subtitle, f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 3,
                   f"  Version {cfg.version}   |   {AUTHOR}   |   "
                   f"36 tabs   |   Start at Settings, then Recipes, "
                   f"then Weekly Planner", f["nav"])

    row = 4
    ws.merge_range(row, 0, row, 3,
                   "  WELCOME - THIS WORKBOOK PLANS YOUR MEALS AND WRITES "
                   "YOUR SHOPPING LIST", f["section"])
    row += 1
    intro = ("Plan breakfast, lunch and dinner for the week, see the calories "
             "and the cost of every meal, keep an eye on what is in the "
             "pantry, and print a grocery list that is already grouped by "
             "aisle. Fill in the cream cells only - the soft sage cells "
             "calculate themselves.")
    ws.merge_range(row, 1, row + 2, 3, intro, f["plain_wrap"])
    row += 4

    ws.merge_range(row, 0, row, 3, "  SET IT UP IN FIVE STEPS", f["section"])
    row += 1
    for heading, body in STEPS:
        ws.set_row(row, 34)
        ws.write(row, 1, heading, f["label"])
        ws.merge_range(row, 2, row, 3, body, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3, "  COLOUR KEY", f["section"])
    row += 1
    for label, body, style in COLOUR_KEY:
        ws.set_row(row, 22)
        ws.write(row, 1, label, f[style])
        ws.merge_range(row, 2, row, 3, body, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3, "  WHAT IS ON EACH TAB", f["section"])
    row += 1
    for tab, what in TAB_GUIDE:
        ws.set_row(row, 20)
        ws.write_url(row, 1, f"internal:'{tab}'!A1", f["link"], string=tab)
        ws.merge_range(row, 2, row, 3, what, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3,
                   "  SHEET PROTECTION", f["section"])
    row += 1
    ws.set_row(row, 40)
    ws.merge_range(row, 1, row, 3,
                   "Every tab is protected so the formulas cannot be "
                   "deleted by accident. The cream input cells stay "
                   "editable. If you want to change the look of the whole "
                   "workbook, unprotect the sheets from Review > Unprotect "
                   f"Sheet (password: {cfg.password}) and re-protect them "
                   "when you are done.", f["plain_wrap"])
    row += 2
    ws.merge_range(row, 0, row, 3,
                   f"  {AUTHOR}  -  thank you for buying this workbook!",
                   f["section"])

    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row, 3)
````

### `meal_planner_spreadsheet/sheets/print_week.py`

Print Week - a weekly meal plan for the fridge door *(122 lines)*

````python
"""
Print Week - a weekly meal plan for the fridge door.

Set the week at the top and print.  The page is laid out to fit one sheet of
A4 in portrait: seven days, three meals and the snacks, with the calories
and the cost of the week at the bottom.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Print Week",
        title="Print Week",
        subtitle="A weekly meal plan for the fridge door",
        columns=[
            Col("label", " ", 18, "text"),
            Col("value", "Value", 16, "text"),
            Col("day", "Day", 12, "calc"),
            Col("date", "Date", 12, "calc"),
            Col("breakfast", "Breakfast", 26, "calc"),
            Col("lunch", "Lunch", 26, "calc"),
            Col("dinner", "Dinner", 26, "calc"),
            Col("snacks", "Snacks", 20, "calc"),
            Col("servings", "Servings", 10, "calc"),
            Col("notes", "Notes", 22, "calc"),
        ],
        rows=7,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 9, "WEEKLY MEAL PLAN", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 9,
                   "Stick this on the fridge - one page, one week",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Week starting", f["label"])
    ws.write_string(2, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(2, 3, "Household", f["label"])
    ws.write_formula(2, 4, "=Household_Name", f["calc_text"])
    ws.write(2, 6, "People", f["label"])
    ws.write_formula(2, 7, "=Household_Size", f["calc_number"])
    ws.write(2, 9, "Budget", f["label"])
    ws.write_formula(2, 10, "=Weekly_Budget", f["calc_money"])
    ws.write_formula(3, 1, "=DATEVALUE($B$3)", f["calc_date"])

    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, head in enumerate(["", "", "Day", "Date", "Breakfast", "Lunch",
                              "Dinner", "Snacks", "Calories", "Cost"]):
        ws.write(hrow, i, head, f["header"])

    for offset in range(7):
        row = spec.first_data_row + offset
        r = row + 1
        ws.write_formula(row, 2, f'=TEXT($B$4+{offset},"dddd")',
                         f["calc_bold"])
        ws.write_formula(row, 3, f'=$B$4+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack"]):
            ws.write_formula(
                row, 4 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$D{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 8, f'=SUMIFS({mp_cal},{mp_date},$D{r})',
                         f["calc_number"])
        ws.write_formula(row, 9, f'=SUMIFS({mp_cost},{mp_date},$D{r})',
                         f["calc_money"])
        ws.set_row(row, 26)

    total = spec.last_data_row
    ws.write(total, 2, "Week", f["total_label"])
    for i in (3, 4, 5, 6, 7):
        ws.write_blank(total, i, None, f["total_label"])
    ws.write_formula(total, 8, f'=SUM($I${spec.first_data_row + 1}:'
                               f'$I${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total, 9, f'=SUM($J${spec.first_data_row + 1}:'
                               f'$J${spec.last_data_row})',
                     f["total_money"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Weekly meal plan")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, total, 9)
    ws.hide_gridlines(2)
````

### `meal_planner_spreadsheet/sheets/print_shopping.py`

Print Shopping - a printable grocery list *(110 lines)*

````python
"""
Print Shopping - a printable grocery list.

Choose the store and print.  The list is pulled from the Grocery List tab in
buy order, grouped by aisle, with a tick box down the side and a running
total so you can see the cost of the basket as it fills.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Print Shopping",
        title="Print Shopping",
        subtitle="A printable grocery list, in buy order",
        columns=[
            Col("label", " ", 14, "text"),
            Col("value", "Value", 18, "text"),
            Col("item", "Item", 28, "calc"),
            Col("category", "Aisle", 18, "calc"),
            Col("quantity", "Quantity", 11, "calc"),
            Col("unit", "Unit", 10, "calc"),
            Col("store", "Store", 18, "calc"),
            Col("bought", "Got it", 9, "calc"),
            Col("notes", "Notes", 24, "calc"),
        ],
        rows=60,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 8, "GROCERY LIST", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "In buy order - tick each item off as you fill the basket",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Store", f["label"])
    ws.write_string(2, 1, cfg.household.store, f["input_text"])
    ws.write(2, 3, "Week starting", f["label"])
    ws.write_formula(2, 4, "=Print_Week_Start", f["calc_date"])
    ws.write(2, 6, "Budget", f["label"])
    ws.write_formula(2, 7, "=Weekly_Budget", f["calc_money"])

    buy_rank = reg.rng("Grocery List", "buy_rank")

    hrow = spec.header_row - 1
    ws.set_row(hrow, 24)
    for i, head in enumerate(["", "", "Item", "Aisle", "Quantity", "Unit",
                              "Store", "Got it", "Notes"]):
        ws.write(hrow, i, head, f["header"])

    for n in range(1, spec.rows + 1):
        row = spec.first_data_row + n - 1
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["item", "category", "quantity", "unit",
                                 "store", "bought", "notes"]):
            rng = reg.rng("Grocery List", key)
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{buy_rank},0)),"")',
                f["calc_number"] if key == "quantity"
                else f["calc_text"])
        ws.set_row(row, 20)

    total = spec.last_data_row
    ws.write(total, 2, "Total to buy", f["total_label"])
    for i in (3, 4, 5, 6):
        ws.write_blank(total, i, None, f["total_label"])
    ws.write_formula(total, 7,
                     f'=COUNTIFS({reg.rng("Grocery List", "buy")},"Yes")'
                     f'&" items"', f["total_label"])
    ws.write_formula(total, 8,
                     f'=SUMIFS({reg.rng("Grocery List", "line_total")},'
                     f'{reg.rng("Grocery List", "buy")},"Yes")',
                     f["total_money"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Grocery list")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, total, 8)
    ws.hide_gridlines(2)
````

### `meal_planner_spreadsheet/sheets/print_recipe.py`

Print Recipe - a printable recipe card *(179 lines)*

````python
"""
Print Recipe - a printable recipe card.

Choose a recipe and it lays out the ingredients with their quantities, the
timings, the cost per serving and the nutrition for one page.  The method
notes come from the recipe itself, so write them once on the Recipes tab and
they print here.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Print Recipe",
        title="Print Recipe",
        subtitle="A printable recipe card",
        columns=[
            Col("label", " ", 16, "text"),
            Col("value", "Value", 26, "text"),
            Col("ingredient", "Ingredient", 28, "calc"),
            Col("quantity", "Quantity", 12, "calc"),
            Col("unit", "Unit", 10, "calc"),
            Col("note", "Note", 40, "calc"),
        ],
        rows=25,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 16)
    ws.set_column(1, 1, 26)
    ws.set_column(2, 2, 28)
    ws.set_column(3, 3, 12)
    ws.set_column(4, 4, 10)
    ws.set_column(5, 5, 40)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 5, "RECIPE CARD", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 5,
                   "Pick a recipe and print - one card, one page",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Recipe", f["label"])
    ws.write_string(2, 1, "Chicken & veg traybake", f["input_text"])
    ws.write(3, 0, "Row found", f["label"])
    ws.write_formula(3, 1,
                     f'=IFERROR(MATCH($B$3,'
                     f'{reg.rng("Recipes", "recipe")},0),0)',
                     f["calc_number"])

    def rec(key: str) -> str:
        return reg.rng("Recipes", key)

    facts = [
        ("Category", rec("category"), "text"),
        ("Cuisine", rec("cuisine"), "text"),
        ("Servings", rec("servings"), "number"),
        ("Prep time (min)", rec("prep_time"), "number"),
        ("Cook time (min)", rec("cook_time"), "number"),
        ("Calories per serving", rec("calories"), "number"),
        ("Protein (g)", rec("protein"), "number"),
        ("Carbs (g)", rec("carbs"), "number"),
        ("Fat (g)", rec("fat"), "number"),
        ("Fibre (g)", rec("fibre"), "number"),
        ("Cost per serving", rec("cost_per_serving"), "money"),
        ("Total cost", rec("total_cost"), "money"),
        ("Rating", rec("rating"), "number"),
        ("Times cooked", rec("times_planned"), "number"),
    ]
    row = 5
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  THE RECIPE", f["section"])
    row += 1
    for i, (label, rng, kind) in enumerate(facts):
        col = (i % 2) * 3
        r = row + (i // 2)
        ws.write(r, col, label, f["label"])
        style = {"text": f["calc_text"], "number": f["calc_number"],
                 "money": f["calc_money"]}[kind]
        ws.write_formula(r, col + 1,
                         f'=IF($B$4=0,"",IFERROR(INDEX({rng},$B$4),""))',
                         style)
    row += (len(facts) + 1) // 2 + 1

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  INGREDIENTS", f["section"])
    row += 1
    ws.set_row(row, 24)
    for i, head in enumerate(["#", "", "Ingredient", "Quantity", "Unit",
                              "Cost"]):
        ws.write(row, i, head, f["header"])
    row += 1

    ri_recipe = reg.rng("Recipe Ingredients", "recipe")
    ri_line = reg.rng("Recipe Ingredients", "line_no")
    ri_ingredients = reg.rng("Recipe Ingredients", "ingredient")
    ri_quantity = reg.rng("Recipe Ingredients", "quantity")
    ri_unit = reg.rng("Recipe Ingredients", "unit")
    ri_line_cost = reg.rng("Recipe Ingredients", "line_cost")

    def nth(rng: str, n_ref: str) -> str:
        return (f'IFERROR(INDEX({rng},MATCH(1,INDEX('
                f'({ri_recipe}=$B$3)*({ri_line}={n_ref}),0),0)),"")')

    for n in range(1, 26):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        ws.write_formula(row, 2,
                         f'=IF($B$4=0,"",{nth(ri_ingredients, f"$A{r}")})',
                         f["calc_text"])
        ws.write_formula(row, 3,
                         f'=IF($B$4=0,"",{nth(ri_quantity, f"$A{r}")})',
                         f["calc_number"])
        ws.write_formula(row, 4,
                         f'=IF($B$4=0,"",{nth(ri_unit, f"$A{r}")})',
                         f["calc_center"])
        ws.write_formula(row, 5,
                         f'=IF($B$4=0,"",{nth(ri_line_cost, f"$A{r}")})',
                         f["calc_money"])
        row += 1

    ws.write(row, 2, "Total", f["total_label"])
    ws.write_blank(row, 3, None, f["total_label"])
    ws.write_blank(row, 4, None, f["total_label"])
    ws.write_formula(row, 5,
                     f'=IF($B$4=0,"",IFERROR(INDEX({rec("total_cost")},'
                     f'$B$4),""))', f["total_money"])
    row += 2

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  METHOD", f["section"])
    row += 1
    ws.merge_range(row, 0, row + 7, 5,
                   f'=IF($B$4=0,"",IFERROR(INDEX({rec("notes")},$B$4),'
                   f'"Write your method in the Notes column on the Recipes '
                   f'tab and it will appear here."))',
                   f["plain_wrap"])
    row += 9

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  NOTE", f["section"])
    row += 1
    ws.merge_range(row, 0, row + 3, 5,
                   f'=IF($B$4=0,"",'
                   f'"This recipe needs "&'
                   f'TEXT(IFERROR(INDEX({rec("ingredient_count")},$B$4),0),'
                   f'"0")&" ingredients. Add them to the Grocery List tab '
                   f'with the quantities above and the rest of the list '
                   f'builds itself.")', f["plain_wrap"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Recipe card")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, row + 4, 5)
    ws.hide_gridlines(2)
````

### `meal_planner_spreadsheet/sheets/help.py`

Help - questions, answers and troubleshooting *(179 lines)*

````python
"""
Help - questions, answers and troubleshooting.

Also documents the columns that are easy to misunderstand and what to do
when a number looks wrong.
"""

from __future__ import annotations

try:
    from ..config import AUTHOR, Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import AUTHOR, Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

FAQ = [
    ("How do I start?",
     "Go to Settings and fill in your household, budget and targets. Then "
     "add the ingredients you buy most often to the Ingredients tab, add "
     "your favourite recipes, and plan your first week on the Weekly "
     "Planner tab."),
    ("How does the grocery list fill itself?",
     "Everything you plan on the Weekly Planner or the Meal Plan tab is "
     "copied to the Grocery List tab. Quantities are scaled by the servings "
     "you asked for and reduced by whatever you already have in the pantry, "
     "so the list only shows what you actually need to buy."),
    ("Why is a recipe showing a cost of zero?",
     "The recipe has no ingredients on the Recipe Ingredients tab yet, or "
     "the ingredient names there do not exactly match the names on the "
     "Ingredients tab. The cost is looked up by name, so keep the spelling "
     "identical."),
    ("Can I change the meal slots?",
     "Yes - edit the Meal slots column on the Lists tab. The planner grids, "
     "the nutrition log and the reports all follow the list."),
    ("What if I shop at more than one store?",
     "Add each shop on the Stores tab, then set the store on the "
     "Ingredients tab. The grocery list can be printed per store, and the "
     "Store Prices tab compares the same item across shops."),
    ("How do the pantry and expiry reminders work?",
     "Add an item, its quantity and the date you opened or bought it. The "
     "pantry works out the expiry date from the shelf life on the "
     "Ingredients tab and flags anything inside the 'use it or lose it' "
     "window you set on Settings."),
    ("Can I use ounces instead of grams?",
     "Set Measurement system to Imperial on the Settings tab and use the "
     "Converter tab when a recipe is written in the other system."),
    ("How do I record that we ate out?",
     "On the Meal Plan tab set the status to Takeaway or Eating out. The "
     "budget and the habit trackers pick it up, and the week is no longer "
     "counted as fully home cooked."),
    ("Can I print just the shopping list?",
     "Yes - Print Shopping. Choose the store and the week, then print. The "
     "list is grouped by aisle with check boxes down the side."),
    ("How do I add a recipe card?",
     "Print Recipe. Choose the recipe title and it lays out the "
     "ingredients, the method notes and the nutrition for one page."),
    ("Something looks wrong - what do I check first?",
     "Check that the ingredient and recipe names match exactly between "
     "tabs, that the dates are real dates and not text, and that Settings "
     "has a planning year. Most odd numbers come from a name typed "
     "slightly differently on two tabs."),
    ("Can I add my own columns?",
     "Yes, but the sheets are protected. Unprotect the sheet from Review > "
     "Unprotect Sheet, add your columns to the right of the existing ones, "
     "then protect it again."),
    ("How much of this do I have to fill in?",
     "Only what you use. If you never batch cook, leave Meal Prep and "
     "Fridge & Freezer empty. The planner still works from Recipes, Meal "
     "Plan and Grocery List alone."),
    ("Where do I get support?",
     f"Message {AUTHOR} through the shop where you bought this workbook "
     "and include the version number from the Start Here tab."),
]

TROUBLESHOOTING = [
    ("#REF! errors", "A row or column was deleted. Close without saving and "
                     "reopen the original file."),
    ("Zero calories for a planned meal",
     "The recipe has no nutrition entered, or the servings on the plan row "
     "are zero."),
    ("Grocery list is empty",
     "The Meal Plan rows have no date inside the week you are looking at, "
     "or the status is set to Skipped."),
    ("Costs look too high",
     "The price on the Ingredients tab is the price of one unit, not of a "
     "whole pack. Divide the pack price by the pack size."),
    ("A drop down will not let me type",
     "The cell is validated against a list on the Lists tab. Either pick "
     "from the list or add your value to the list."),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Help",
        title="Help",
        subtitle="Frequently asked questions, column notes and "
                 "troubleshooting",
        columns=[
            Col("question", "Question", 40, "text"),
            Col("answer", "Answer", 92, "text_wrap"),
            Col("note", "Note", 20, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.grey_text,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    p, f = Palette, writer.fmt
    writer.grid_off(ws)
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 44)
    ws.set_column(2, 2, 92)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 2, "HELP", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 2,
                   "Frequently asked questions, column notes and "
                   "troubleshooting", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 2,
                   "  |  Start Here   |   Settings   |   Weekly Planner   |  "
                   " Grocery List   |   Reports", f["nav"])

    row = 4
    ws.merge_range(row, 0, row, 2, "  FREQUENTLY ASKED QUESTIONS",
                   f["section"])
    row += 1
    for question, answer in FAQ:
        ws.set_row(row, 46)
        ws.write(row, 1, question, f["label"])
        ws.write(row, 2, answer, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2, "  TROUBLESHOOTING", f["section"])
    row += 1
    for problem, fix in TROUBLESHOOTING:
        ws.set_row(row, 30)
        ws.write(row, 1, problem, f["label"])
        ws.write(row, 2, fix, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2, "  GOOD HABITS", f["section"])
    row += 1
    habits = [
        "Fill in Settings first - the rest of the workbook depends on it.",
        "Add your 20 most used ingredients before anything else.",
        "Type ingredient names exactly the same way on every tab.",
        "Plan one week at a time until the habit sticks.",
        "Record what you actually threw away - it is the fastest way to "
        "save money on food.",
        "Print the week and stick it on the fridge; the plan only works "
        "if you can see it.",
    ]
    for habit in habits:
        ws.set_row(row, 20)
        ws.write(row, 1, "-", f["plain_bold"])
        ws.write(row, 2, habit, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2,
                   f"  {AUTHOR}  -  version {cfg.version}", f["section"])

    ws.set_tab_color(Palette.grey_text)
    ws.hide_gridlines(2)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row, 2)
````

---

## 5. Quality checks (optional)

Not needed to build the workbook - these are the checks that keep it honest. The first two need `openpyxl`, the third needs `formulas`.

### `tools/validate_meal_workbook.py`

Check a built meal planner workbook *(271 lines)*

````python
#!/usr/bin/env python3
"""
Check a built meal planner workbook.

    python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"

The checks are deliberately boring and mechanical: is the tab order right,
is every sheet protected, does every formula only use functions that exist
in Excel 2010, does every cross-sheet reference point at a tab that is
really there, and are there any charts or pictures that should not be.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from collections import Counter
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from meal_planner_spreadsheet.build import SHEET_ORDER
except Exception:                                     # pragma: no cover
    SHEET_ORDER = [
        "Start Here", "Dashboard", "Weekly Planner", "Monthly Planner",
        "Settings", "Lists", "Household", "Recipes", "Recipe Ingredients",
        "Ingredients", "Meal Plan", "Grocery List", "Pantry", "Staples",
        "Leftovers", "Food Waste", "Meal Prep", "Dietary Filters",
        "Nutrition", "Budget", "Recipe Costs", "Converter", "Rotation",
        "Food Safety", "Fridge & Freezer", "Grocery Spending",
        "Store Prices", "Stores", "Events", "Goals", "Sustainability",
        "Reports", "Print Week", "Print Shopping", "Print Recipe", "Help",
    ]

#: every function the workbook is allowed to use.  All of these exist in
#: Excel 2007 and Excel 2010, so the file opens anywhere.
SAFE_FUNCTIONS = {
    "IF", "IFERROR", "AND", "OR", "NOT", "TRUE", "FALSE", "INDEX", "MATCH",
    "VLOOKUP", "HLOOKUP", "LOOKUP", "CHOOSE", "OFFSET", "INDIRECT",
    "COUNTIF", "COUNTIFS", "COUNT", "COUNTA", "COUNTBLANK", "SUM", "SUMIF",
    "SUMIFS", "SUMPRODUCT", "SUBTOTAL", "AVERAGE", "AVERAGEIF",
    "AVERAGEIFS", "MAX", "MIN", "LARGE", "SMALL", "ROUND", "ROUNDUP",
    "ROUNDDOWN", "MROUND", "INT", "MOD", "ABS", "CEILING", "FLOOR", "POWER",
    "SQRT", "EXP", "LN", "LOG", "LOG10", "TEXT", "VALUE", "LEFT", "RIGHT",
    "MID", "LEN", "LOWER", "UPPER", "PROPER", "TRIM", "CONCATENATE", "&",
    "REPT", "SUBSTITUTE", "REPLACE", "FIND", "SEARCH", "T", "N", "ISNUMBER",
    "ISTEXT", "ISBLANK", "ISERROR", "ISNA", "NA", "DATE", "TIME", "TODAY",
    "NOW", "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND", "WEEKDAY",
    "WEEKNUM", "EOMONTH", "EDATE", "DATEVALUE", "TIMEVALUE", "DAYS",
    "DAYS360", "NETWORKDAYS", "WORKDAY", "ROW", "ROWS", "COLUMN", "COLUMNS",
    "RANK", "PERCENTILE", "QUARTILE", "MEDIAN", "MODE", "STDEV", "STDEVP",
    "VAR", "VARP", "CORREL", "SLOPE", "INTERCEPT", "FORECAST", "TREND",
    "GROWTH", "NPV", "IRR", "PMT", "PV", "FV", "RATE", "NPER", "SLN",
    "SYD", "DDB", "XNPV", "XIRR", "SUMPRODUCT", "TRANSPOSE", "MMULT",
    "MDETERM", "MINVERSE", "ROMAN", "ARABIC", "BASE", "DECIMAL", "FACT",
    "COMBIN", "PERMUT", "GCD", "LCM", "SIGN", "TRUNC", "EVEN", "ODD",
    "DEGREES", "RADIANS", "PI", "SIN", "COS", "TAN", "ASIN", "ACOS",
    "ATAN", "ATAN2", "SINH", "COSH", "TANH", "SUMX2MY2", "SUMX2PY2",
    "SUMXMY2", "SERIESSUM", "MULTINOMIAL", "QUOTIENT", "RAND", "RANDBETWEEN",
    "CLEAN", "CODE", "CHAR", "DOLLAR", "FIXED", "EXACT", "CELL", "INFO",
    "HYPERLINK", "GETPIVOTDATA", "DATEDIF", "YEARFRAC",
}

SHEET_FILE = re.compile(r"^xl/worksheets/sheet(\d+)\.xml$")
SHEET_REF = re.compile(r"(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_ .&]*))!")
FORMULA = re.compile(r"<f[^>]*>(.*?)</f>", re.S)
DEFINED_NAME = re.compile(r'<definedName name="([^"]+)"[^>]*>(.*?)</definedName>',
                          re.S)


class Report:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def info(self, message: str) -> None:
        self.lines.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)
        self.lines.append("ERROR   " + message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        self.lines.append("WARNING " + message)

    @property
    def ok(self) -> bool:
        return not self.errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?",
                        default=os.path.join(
                            "output", "Meal Planner & Grocery List.xlsx"))
    parser.add_argument("--min-formulas", type=int, default=50000)
    parser.add_argument("--expect-sample-data", action="store_true",
                        help="fail if the registers look empty")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    path = args.workbook
    rep = Report()

    if not os.path.exists(path):
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2
    size = os.path.getsize(path)
    rep.info(f"{os.path.basename(path)}  ({size / 1024.0:,.0f} KB)")

    zf = zipfile.ZipFile(path)
    names = zf.namelist()

    # ---- sheet order -------------------------------------------------------
    workbook_xml = zf.read("xl/workbook.xml").decode("utf8", "replace")
    order = [unescape(n) for n in
             re.findall(r'<sheet name="([^"]+)"', workbook_xml)]
    if order == SHEET_ORDER:
        rep.info(f"tab order OK ({len(order)} tabs, first {order[0]!r}, "
                 f"last {order[-1]!r})")
    else:
        rep.error(f"tab order mismatch: expected {SHEET_ORDER}, "
                  f"found {order}")

    sheet_files = sorted(n for n in names if SHEET_FILE.match(n))
    if len(sheet_files) != len(SHEET_ORDER):
        rep.error(f"expected {len(SHEET_ORDER)} worksheet parts, "
                  f"found {len(sheet_files)}")
    else:
        rep.info(f"{len(sheet_files)} worksheet parts")

    # ---- per sheet ---------------------------------------------------------
    total_formulas = 0
    total_validations = 0
    total_conditional = 0
    total_comments = 0
    print_areas = 0
    empty_sheets = []
    functions = Counter()
    bad_refs = Counter()
    for index, name in enumerate(sheet_files, start=1):
        data = zf.read(name).decode("utf8", "replace")
        tab = order[index - 1] if index - 1 < len(order) else name
        formulas = FORMULA.findall(data)
        total_formulas += len(formulas)
        total_validations += data.count("<dataValidation ")
        total_conditional += data.count("<conditionalFormatting")
        # comments live in their own parts, not in the sheet XML
        total_comments += sum(zf.read(n).decode("utf8", "replace")
                              .count("<comment ")
                              for n in names
                              if re.match(r"xl/comments\d+\.xml$", n))

        if "<sheetProtection" not in data:
            rep.error(f"{tab}: sheet is not protected")
        # VML parts are the yellow tooltip boxes the data validation input
        # messages use - those are fine.  Real drawing parts are not.
        if re.search(r"<drawing r:id=", data):
            rep.error(f"{tab}: contains a drawing (charts and pictures are "
                      f"not allowed in this workbook)")
        if "<x14:sparkline" in data or "<chart" in data:
            rep.error(f"{tab}: contains a chart or sparkline")

        # Excel 2010 safe functions only
        for formula in formulas:
            for func in re.findall(r"([A-Z][A-Z0-9_.]*)\s*\(", formula):
                if func not in SAFE_FUNCTIONS:
                    functions[(tab, func)] += 1
            for sheet_name in SHEET_REF.findall(formula):
                ref = sheet_name[0] or sheet_name[1]
                if ref and ref not in SHEET_ORDER and not ref.startswith("#"):
                    bad_refs[(tab, ref)] += 1

        if args.expect_sample_data and not formulas and "<c " not in data:
            empty_sheets.append(tab)

    rep.info(f"{total_formulas:,} formulas")
    rep.info(f"{total_validations:,} data validations, "
             f"{total_conditional:,} conditional formats, "
             f"{total_comments:,} cell comments")
    print_areas = len(re.findall(
        r'<definedName name="_xlnm.Print_Area"', workbook_xml))
    rep.info(f"print areas set on {print_areas} of {len(sheet_files)} sheets")
    if print_areas < len(sheet_files):
        rep.warn(f"{len(sheet_files) - print_areas} sheets have no print "
                 f"area")

    if total_formulas < args.min_formulas:
        rep.error(f"only {total_formulas:,} formulas, expected at least "
                  f"{args.min_formulas:,}")
    for (tab, func), count in sorted(functions.items()):
        rep.error(f"{tab}: uses {func} which is not Excel 2010 safe "
                  f"({count} times)")
    for (tab, ref), count in sorted(bad_refs.items()):
        rep.error(f"{tab}: formula references unknown sheet {ref!r} "
                  f"({count} times)")
    if empty_sheets:
        rep.error(f"sheets with no data at all: {empty_sheets}")

    # ---- charts and drawings ----------------------------------------------
    drawings = [n for n in names
                if re.match(r"xl/drawings/drawing\d+\.xml$", n)]
    charts = [n for n in names if "charts/chart" in n]
    vml = [n for n in names if n.startswith("xl/drawings/vmlDrawing")]
    if drawings:
        rep.error(f"{len(drawings)} drawing parts found (none expected)")
    if charts:
        rep.error(f"{len(charts)} chart parts found (none expected)")
    if not charts and not drawings:
        rep.info(f"no charts and no drawings ({len(vml)} validation tooltip "
                 f"parts, which is expected)")

    # ---- defined names ------------------------------------------------------
    defined = [(unescape(n), unescape(t))
               for n, t in DEFINED_NAME.findall(workbook_xml)]
    rep.info(f"{len(defined)} defined names")
    for name, target in defined:
        target = target.strip()
        if "#REF!" in target:
            rep.error(f"defined name {name} points at #REF!")
        if target.startswith("="):
            target = target[1:]
        match = re.match(r"^(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_ .&]*))!", target)
        if match:
            sheet = match.group(1) or match.group(2)
            if sheet not in SHEET_ORDER:
                rep.error(f"defined name {name} points at unknown sheet "
                          f"{sheet!r}")

    # ---- cached error values ------------------------------------------------
    errors = 0
    for name in sheet_files:
        data = zf.read(name).decode("utf8", "replace")
        errors += data.count('t="e"')
    if errors:
        rep.warn(f"{errors} cells carry a cached error value")
    else:
        rep.info("no cached error values")

    # ---- workbook properties -------------------------------------------------
    if "docProps/core.xml" in names:
        core = zf.read("docProps/core.xml").decode("utf8", "replace")
        author = re.search(r"<dc:creator>(.*?)</dc:creator>", core)
        title = re.search(r"<dc:title>(.*?)</dc:title>", core)
        if author:
            rep.info(f"author: {unescape(author.group(1))}")
        if title:
            rep.info(f"title: {unescape(title.group(1))}")

    if not args.quiet:
        print("\n".join(rep.lines))
        print()
        if rep.ok:
            print(f"PASS - {os.path.basename(path)} looks good")
        else:
            print(f"FAIL - {len(rep.errors)} error(s), "
                  f"{len(rep.warnings)} warning(s)")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
````

### `tools/check_meal_sample.py`

Check that the example data in a built workbook hangs together *(223 lines)*

````python
#!/usr/bin/env python3
"""
Check that the example data in a built workbook hangs together.

    python tools/check_meal_sample.py "output/Meal Planner & Grocery List.xlsx"

The lookups in this workbook all match on names, so the example data is only
as good as its spelling.  This tool walks the registers and reports every
ingredient, recipe, store, unit, category and meal slot that is used on one
tab but missing from another.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict

try:
    import openpyxl
except ImportError:                              # pragma: no cover
    print("error: openpyxl is required (pip install openpyxl)",
          file=sys.stderr)
    raise SystemExit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DEFAULT_OUTPUT = os.path.join("output",
                              "Meal Planner & Grocery List.xlsx")


def column_map(ws, header_row=4):
    """{column key guess: column index} from the header row."""
    headers = {}
    for cell in ws[header_row]:
        if cell.value:
            headers[str(cell.value).strip()] = cell.column
    return headers


def read_column(ws, index, first_row, last_row):
    if index is None:
        return []
    return [ws.cell(row=r, column=index).value
            for r in range(first_row, last_row + 1)]


def non_blank(values):
    return [v for v in values if v not in (None, "")]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?", default=DEFAULT_OUTPUT)
    parser.add_argument("--rows", type=int, default=400,
                        help="how many rows of each register to read")
    args = parser.parse_args(argv)

    if not os.path.exists(args.workbook):
        print(f"error: {args.workbook} does not exist", file=sys.stderr)
        return 2

    wb = openpyxl.load_workbook(args.workbook, data_only=True, read_only=True)
    problems = []
    notes = []

    def sheet(name):
        return wb[name] if name in wb.sheetnames else None

    def col(ws, header, header_row=4):
        return column_map(ws, header_row).get(header)

    def values(name, header, header_row=4, first_row=None):
        ws = sheet(name)
        if ws is None:
            return []
        index = col(ws, header, header_row)
        if index is None:
            return []
        first = first_row or header_row + 1
        last = first + args.rows
        return non_blank(read_column(ws, index, first, last))

    # ---- the reference lists ------------------------------------------------
    lists = sheet("Lists")
    list_sets = {}
    if lists is not None:
        headers = column_map(lists, 4)
        for name, index in headers.items():
            list_sets[name] = set(non_blank(
                read_column(lists, index, 5, 5 + args.rows)))

    ingredients = set(values("Ingredients", "Ingredient"))
    recipes = set(values("Recipes", "Recipe"))
    stores = set(values("Lists", "Stores")) | set(values("Stores", "Store"))
    units = set(values("Lists", "Units"))
    categories = set(values("Lists", "Categories"))
    slots = set(values("Lists", "Meal slots"))
    statuses = set(values("Lists", "Status"))

    recipe_categories = set(values("Lists", "Recipe categories"))
    notes.append(f"{len(ingredients)} ingredients, {len(recipes)} recipes, "
                 f"{len(stores)} stores, {len(units)} units, "
                 f"{len(categories)} aisle categories, "
                 f"{len(recipe_categories)} recipe categories, "
                 f"{len(slots)} meal slots")

    if not ingredients:
        problems.append("the Ingredients tab is empty - run the build with "
                        "the example data (drop --blank)")
    if not recipes:
        problems.append("the Recipes tab is empty - run the build with the "
                        "example data (drop --blank)")

    # ---- duplicates ----------------------------------------------------------
    for label, seq in (("ingredient", values("Ingredients", "Ingredient")),
                       ("recipe", values("Recipes", "Recipe"))):
        dupes = [k for k, v in Counter(seq).items() if v > 1]
        if dupes:
            problems.append(f"duplicate {label} names: {sorted(dupes)[:8]}")

    # ---- names used on one tab must exist on another -------------------------
    checks = [
        ("Recipe Ingredients", "Ingredient", ingredients, "Ingredients"),
        ("Recipe Ingredients", "Recipe", recipes, "Recipes"),
        ("Meal Plan", "Recipe", recipes, "Recipes"),
        ("Meal Plan", "Meal slot", slots, "Lists"),
        ("Meal Plan", "Status", statuses, "Lists"),
        ("Grocery List", "Item", ingredients, "Ingredients"),
        ("Grocery List", "Store", stores, "Lists"),
        ("Grocery List", "Unit", units, "Lists"),
        ("Pantry", "Item", ingredients, "Ingredients"),
        ("Pantry", "Storage", {"Pantry", "Cupboard", "Fridge", "Freezer"},
         "storage"),
        ("Staples", "Staple", ingredients, "Ingredients"),
        ("Leftovers", "From recipe", recipes, "Recipes"),
        ("Food Waste", "Item", ingredients, "Ingredients"),
        ("Meal Prep", "Recipe", recipes, "Recipes"),
        ("Recipe Costs", "Recipe", recipes, "Recipes"),
        ("Rotation", "Recipe", recipes, "Recipes"),
        ("Fridge & Freezer", "From recipe", recipes, "Recipes"),
        ("Nutrition", "Recipe", recipes, "Recipes"),
        ("Nutrition", "Meal slot", slots, "Lists"),
        ("Grocery Spending", "Item", ingredients, "Ingredients"),
        ("Grocery Spending", "Store", stores, "Lists"),
        ("Store Prices", "Item", ingredients, "Ingredients"),
        ("Store Prices", "Store", stores, "Lists"),
        ("Ingredients", "Category", categories, "Lists"),
        ("Ingredients", "Unit", units, "Lists"),
        ("Ingredients", "Storage", {"Pantry", "Cupboard", "Fridge",
                                    "Freezer"}, "storage"),
        ("Recipes", "Category",
         set(values("Lists", "Recipe categories")), "Lists"),
        ("Recipes", "Cuisine", set(values("Lists", "Cuisines")), "Lists"),
    ]
    for tab, header, allowed, source in checks:
        used = set(values(tab, header))
        missing = sorted(used - allowed)
        if missing:
            problems.append(f"{tab} / {header}: {len(missing)} value(s) not "
                            f"found on {source}: {missing[:6]}")

    # ---- meal plan sanity ------------------------------------------------------
    plan_dates = values("Meal Plan", "Date")
    bad_dates = [d for d in plan_dates if not hasattr(d, "year")]
    if bad_dates:
        problems.append(f"Meal Plan: {len(bad_dates)} date cells are not "
                        f"real dates")
    nutrition_dates = values("Nutrition", "Date")
    bad_nutrition = [d for d in nutrition_dates if not hasattr(d, "year")]
    if bad_nutrition:
        problems.append(f"Nutrition: {len(bad_nutrition)} date cells are not "
                        f"real dates")

    # ---- recipe ingredients -----------------------------------------------------
    ri = sheet("Recipe Ingredients")
    if ri is not None:
        recipe_col = col(ri, "Recipe")
        qty_col = col(ri, "Quantity")
        recipe_names = set()
        per_recipe = defaultdict(int)
        for row in range(5, 5 + args.rows):
            name = ri.cell(row=row, column=recipe_col).value \
                if recipe_col else None
            if not name:
                continue
            recipe_names.add(name)
            qty = ri.cell(row=row, column=qty_col).value if qty_col else None
            if isinstance(qty, (int, float)) and qty > 0:
                per_recipe[name] += 1
        without_ingredients = sorted(recipes - recipe_names)
        if without_ingredients:
            problems.append(f"{len(without_ingredients)} recipes have no "
                            f"ingredients: {without_ingredients[:6]}")
        notes.append(f"{len(recipe_names)} recipes carry "
                     f"{sum(per_recipe.values())} ingredient lines")

    # ---- budget months line up with the spending tab ------------------------------
    budget_months = set(values("Budget", "Month"))
    spending_months = set(values("Grocery Spending", "Month"))
    orphan = sorted(budget_months - spending_months)
    if orphan:
        problems.append(f"Budget months with no spending recorded: {orphan}")

    # ---- report ---------------------------------------------------------------------
    for line in notes:
        print(f"  {line}")
    print()
    if problems:
        print(f"FAIL - {len(problems)} problem(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("PASS - the example data hangs together")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

### `tools/recalc_check.py`

Recalculate a small build and check the numbers come out right *(212 lines)*

````python
#!/usr/bin/env python3
"""
Recalculate a small build and check the numbers come out right.

    python tools/recalc_check.py
    python tools/recalc_check.py --rows 60 --keep

The `formulas` library evaluates the workbook, then a handful of cells are
compared with values worked out by hand from the example data.  It is the
closest thing to opening the file in Excel without having Excel.

The cell addresses come from the layout registry in this package rather
than from the file, so the tool never has to hold the whole workbook in
memory at the same time as the calculation engine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gc
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def build(rows: int, target: str) -> str:
    cmd = [sys.executable, os.path.join(ROOT, "build_meal_planner_workbook.py"),
           "--rows", str(rows), "--quiet", "-o", target]
    subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    return target


def registry_for(cfg):
    """Declare every sheet in memory so cell addresses can be looked up."""
    from meal_planner_spreadsheet import build as build_mod
    from meal_planner_spreadsheet.layout import Registry

    registry = Registry()
    registry.strict = False
    for name in build_mod.SHEET_ORDER:
        build_mod.module_for(name).build(None, registry, cfg, None)
    registry.strict = True
    for name in build_mod.SHEET_ORDER:
        build_mod.module_for(name).build(None, registry, cfg, None)
    return registry


def weekday_of(value):
    """Monday = 0, for a datetime or an Excel serial number."""
    if value is None:
        return None
    if hasattr(value, "weekday"):
        return value.weekday()
    try:
        return (dt.date(1899, 12, 30)
                + dt.timedelta(days=float(value))).weekday()
    except (TypeError, ValueError):
        return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=100,
                        help="rows per register in the test build.  The "
                             "example data needs about 100 rows to fit, so "
                             "going lower silently drops records.")
    parser.add_argument("--keep", action="store_true",
                        help="keep the test workbook for inspection")
    parser.add_argument("--workbook", default=None,
                        help="recalculate an existing workbook instead of "
                             "building one")
    args = parser.parse_args(argv)

    from meal_planner_spreadsheet.config import Config
    from meal_planner_spreadsheet import sample_data

    cfg = Config()
    if args.rows:
        cfg.scale_rows(args.rows)
    samples = sample_data.build_samples(cfg)
    registry = registry_for(cfg)

    def cell(sheet: str, key: str, offset: int) -> str:
        spec = registry[sheet]
        return f"{spec.letter(key)}{spec.first_data_row + offset}"

    def offset_of(sheet: str, key: str, value) -> int:
        for offset, record in samples[sheet].items():
            if record.get(key) == value:
                return offset
        raise KeyError(f"{sheet}: no sample row with {key}={value!r}")

    tmpdir = tempfile.mkdtemp(prefix="meal-recalc-")
    try:
        path = args.workbook or build(args.rows,
                                      os.path.join(tmpdir, "recalc.xlsx"))
        print(f"recalculating {os.path.basename(path)}")

        import formulas
        model = formulas.ExcelModel().loads(path).finish()
        solution = model.calculate()
        base = os.path.basename(path)

        def raw(sheet: str, cell_ref: str):
            key = f"'[{base}]{sheet.upper()}'!{cell_ref}"
            item = solution.get(key)
            if item is None:
                return None
            try:
                return item.value[0, 0]
            except Exception:
                return item

        # ---- the cells to check, and what they should come to ---------------
        pending = []

        def check(label, sheet, key, offset, expected, tolerance=0.01,
                  transform=None):
            pending.append((label, sheet, cell(sheet, key, offset),
                            expected, tolerance, transform))

        porridge = offset_of("Recipes", "recipe", "Porridge with banana")
        check("Recipes: total time is prep + cook", "Recipes",
              "total_time", porridge, 13)
        check("Recipes: ingredient count", "Recipes",
              "ingredient_count", porridge, 4)
        # porridge is on the plan seven times, four of them already cooked
        check("Recipes: times cooked", "Recipes",
              "times_planned", porridge, 4)

        oats = offset_of("Recipe Ingredients", "recipe", "Porridge with banana")
        check("Recipe Ingredients: price looked up by name",
              "Recipe Ingredients", "price", oats, 0.0019, 0.0001)
        check("Recipe Ingredients: line cost = qty x price",
              "Recipe Ingredients", "line_cost", oats, 0.152, 0.0005)
        check("Recipe Ingredients: line number inside the recipe",
              "Recipe Ingredients", "line_no", oats, 1)

        rice = offset_of("Ingredients", "ingredient", "Rice")
        check("Ingredients: pantry quantity for rice", "Ingredients",
              "in_pantry", rice, 1200)
        oat_ing = offset_of("Ingredients", "ingredient", "Oats")
        check("Ingredients: pantry quantity for oats", "Ingredients",
              "in_pantry", oat_ing, 900)
        check("Ingredients: recipes that use oats", "Ingredients",
              "recipe_count", oat_ing, 3)

        plan = offset_of("Meal Plan", "recipe", "Porridge with banana")
        check("Meal Plan: calories = recipe x servings", "Meal Plan",
              "calories", plan, 1280, 0.5)
        check("Meal Plan: week starting is a Monday", "Meal Plan",
              "week_start", plan, 0, transform=weekday_of)

        chicken = offset_of("Grocery List", "item", "Chicken breast")
        check("Grocery List: line total = qty x price", "Grocery List",
              "line_total", chicken, 5.94)
        check("Grocery List: sees what is already in the pantry",
              "Grocery List", "in_pantry", chicken, 250)

        spinach = offset_of("Food Waste", "waste_id", "W-01")
        check("Food Waste: cost = qty x price", "Food Waste",
              "cost", spinach, 0.552, 0.005)

        check("Recipe Costs: total cost from its ingredients",
              "Recipe Costs", "total_cost", porridge,
              80 * 0.0019 + 480 * 0.0013 + 2 * 0.19 + 2 * 0.12)

        # ---- pull the values out and free the engine ------------------------
        results = [(label, sheet, cell_ref,
                    (transform(raw(sheet, cell_ref)) if transform
                     else raw(sheet, cell_ref)), expected, tol)
                   for label, sheet, cell_ref, expected, tol, transform
                   in pending]
        del solution, model
        gc.collect()

        failures = 0
        for label, sheet, cell_ref, got, expected, tol in results:
            ok = False
            if got is not None:
                try:
                    ok = abs(float(got) - float(expected)) <= tol
                except (TypeError, ValueError):
                    ok = str(got) == str(expected)
            if not ok:
                failures += 1
            print(f"  {'ok  ' if ok else 'FAIL'}  {label:48s} "
                  f"expected {expected!r:>12}  got {got!r}")

        print()
        if failures:
            print(f"FAIL - {failures} of {len(results)} checks failed")
            return 1
        print(f"PASS - all {len(results)} recalculated values are right")
        return 0
    finally:
        if args.keep:
            print(f"test workbook kept in {tmpdir}")
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
````

### `tools/export_source_md.py`

Write every source file of a generator into one clean markdown document *(555 lines)*

````python
#!/usr/bin/env python3
"""
Write every source file of a generator into one clean markdown document.

    python tools/export_source_md.py                      # pet sitting
    python tools/export_source_md.py --product meal       # meal planner
    python tools/export_source_md.py -o /tmp/src.md

Handy when the code has to travel somewhere that is not a git checkout:
one file, every module in reading order, each in a fenced block with its
real path above it, plus a short description taken from the module's own
docstring so the two can never disagree.

The layout is deliberately plain - a short cover, a contents table, then
the code - so it reads well in any markdown viewer and survives being
printed to PDF.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PET_SECTIONS = [
    ("1. Run it",
     "Save the files below keeping these exact paths, then run the one "
     "liner. Nothing else is needed - no project file, no build step.\n\n"
     "```bash\n"
     "pip install XlsxWriter\n"
     "python build_pet_sitting_workbook.py\n"
     "```\n\n"
     "The workbook lands in `output/Pet Sitting Business Spreadsheet.xlsx`.",
     ["build_pet_sitting_workbook.py"]),
    ("2. The package",
     "Configuration, the formula template engine, cell formats, the sheet "
     "writer and the demo data. These are the parts every tab leans on.",
     ["pet_sitting_spreadsheet/__init__.py",
      "pet_sitting_spreadsheet/__main__.py",
      "pet_sitting_spreadsheet/cli.py",
      "pet_sitting_spreadsheet/config.py",
      "pet_sitting_spreadsheet/layout.py",
      "pet_sitting_spreadsheet/formats.py",
      "pet_sitting_spreadsheet/writer.py",
      "pet_sitting_spreadsheet/names.py",
      "pet_sitting_spreadsheet/build.py",
      "pet_sitting_spreadsheet/sample_data.py"]),
    ("3. The registers",
     "One module per data tab. Each returns a list of columns with their "
     "formulas, and the writer turns that into a formatted, validated, "
     "protected sheet.",
     ["pet_sitting_spreadsheet/sheets/__init__.py",
      "pet_sitting_spreadsheet/sheets/common.py",
      "pet_sitting_spreadsheet/sheets/lists.py",
      "pet_sitting_spreadsheet/sheets/settings.py",
      "pet_sitting_spreadsheet/sheets/services.py",
      "pet_sitting_spreadsheet/sheets/clients.py",
      "pet_sitting_spreadsheet/sheets/pets.py",
      "pet_sitting_spreadsheet/sheets/bookings.py",
      "pet_sitting_spreadsheet/sheets/visits.py",
      "pet_sitting_spreadsheet/sheets/health.py",
      "pet_sitting_spreadsheet/sheets/incidents.py",
      "pet_sitting_spreadsheet/sheets/messages.py",
      "pet_sitting_spreadsheet/sheets/invoices.py",
      "pet_sitting_spreadsheet/sheets/payments.py",
      "pet_sitting_spreadsheet/sheets/expenses.py",
      "pet_sitting_spreadsheet/sheets/mileage.py",
      "pet_sitting_spreadsheet/sheets/staff.py",
      "pet_sitting_spreadsheet/sheets/inventory.py",
      "pet_sitting_spreadsheet/sheets/reminders.py"]),
    ("4. The pages",
     "The tabs that read the registers: the hidden calculation engine, the "
     "dashboard, the reports, the planner, the welcome tab, the printable "
     "pages and the help tab.",
     ["pet_sitting_spreadsheet/sheets/calc.py",
      "pet_sitting_spreadsheet/sheets/dashboard.py",
      "pet_sitting_spreadsheet/sheets/reports.py",
      "pet_sitting_spreadsheet/sheets/budget.py",
      "pet_sitting_spreadsheet/sheets/start_here.py",
      "pet_sitting_spreadsheet/sheets/printables.py",
      "pet_sitting_spreadsheet/sheets/help_tab.py"]),
    ("5. Quality checks (optional)",
     "Not needed to build the workbook - these are the checks that keep it "
     "honest. The first two need `openpyxl`, the third needs `formulas`.",
     ["tools/validate_workbook.py",
      "tools/check_sample_data.py",
      "tools/recalc_check.py",
      "tools/export_source_md.py",
      "tools/make_download_zip.py"]),
]

MEAL_SECTIONS = [
    ("1. Run it",
     "Save the files below keeping these exact paths, then run the one "
     "liner. Nothing else is needed - no project file, no build step.\n\n"
     "```bash\n"
     "pip install XlsxWriter\n"
     "python build_meal_planner_workbook.py\n"
     "```\n\n"
     "The workbook lands in "
     "`output/Meal Planner & Grocery List.xlsx`.",
     ["build_meal_planner_workbook.py"]),
    ("2. The package",
     "Configuration, the formula template engine, cell formats, the sheet "
     "writer and the demo data. These are the parts every tab leans on.",
     ["meal_planner_spreadsheet/__init__.py",
      "meal_planner_spreadsheet/__main__.py",
      "meal_planner_spreadsheet/cli.py",
      "meal_planner_spreadsheet/config.py",
      "meal_planner_spreadsheet/layout.py",
      "meal_planner_spreadsheet/formats.py",
      "meal_planner_spreadsheet/writer.py",
      "meal_planner_spreadsheet/names.py",
      "meal_planner_spreadsheet/build.py",
      "meal_planner_spreadsheet/sample_data.py"]),
    ("3. The registers",
     "One module per data tab. Each returns a list of columns with their "
     "formulas, and the writer turns that into a formatted, validated, "
     "protected sheet.",
     ["meal_planner_spreadsheet/sheets/__init__.py",
      "meal_planner_spreadsheet/sheets/lists.py",
      "meal_planner_spreadsheet/sheets/settings.py",
      "meal_planner_spreadsheet/sheets/household.py",
      "meal_planner_spreadsheet/sheets/recipes.py",
      "meal_planner_spreadsheet/sheets/recipe_ingredients.py",
      "meal_planner_spreadsheet/sheets/ingredients.py",
      "meal_planner_spreadsheet/sheets/meal_plan.py",
      "meal_planner_spreadsheet/sheets/grocery_list.py",
      "meal_planner_spreadsheet/sheets/pantry.py",
      "meal_planner_spreadsheet/sheets/staples.py",
      "meal_planner_spreadsheet/sheets/leftovers.py",
      "meal_planner_spreadsheet/sheets/food_waste.py",
      "meal_planner_spreadsheet/sheets/meal_prep.py",
      "meal_planner_spreadsheet/sheets/dietary_filters.py",
      "meal_planner_spreadsheet/sheets/rotation.py",
      "meal_planner_spreadsheet/sheets/food_safety.py",
      "meal_planner_spreadsheet/sheets/fridge_freezer.py",
      "meal_planner_spreadsheet/sheets/grocery_spending.py",
      "meal_planner_spreadsheet/sheets/store_prices.py",
      "meal_planner_spreadsheet/sheets/stores.py",
      "meal_planner_spreadsheet/sheets/events.py",
      "meal_planner_spreadsheet/sheets/sustainability.py",
      "meal_planner_spreadsheet/sheets/recipe_costs.py",
      "meal_planner_spreadsheet/sheets/converter.py"]),
    ("4. The pages",
     "The tabs that read the registers: the dashboard, the weekly and "
     "monthly planners, the nutrition log, the budget, the goals, the "
     "reports, the welcome tab, the three printable pages and the help tab.",
     ["meal_planner_spreadsheet/sheets/dashboard.py",
      "meal_planner_spreadsheet/sheets/weekly_planner.py",
      "meal_planner_spreadsheet/sheets/monthly_planner.py",
      "meal_planner_spreadsheet/sheets/nutrition.py",
      "meal_planner_spreadsheet/sheets/budget.py",
      "meal_planner_spreadsheet/sheets/goals.py",
      "meal_planner_spreadsheet/sheets/reports.py",
      "meal_planner_spreadsheet/sheets/start_here.py",
      "meal_planner_spreadsheet/sheets/print_week.py",
      "meal_planner_spreadsheet/sheets/print_shopping.py",
      "meal_planner_spreadsheet/sheets/print_recipe.py",
      "meal_planner_spreadsheet/sheets/help.py"]),
    ("5. Quality checks (optional)",
     "Not needed to build the workbook - these are the checks that keep it "
     "honest. The first two need `openpyxl`, the third needs `formulas`.",
     ["tools/validate_meal_workbook.py",
      "tools/check_meal_sample.py",
      "tools/recalc_check.py",
      "tools/export_source_md.py",
      "tools/make_download_zip.py"]),
]

PET_APPENDIX = """\
## Appendix

### A. Build the workbook

```bash
python build_pet_sitting_workbook.py                       # demo data
python build_pet_sitting_workbook.py --blank               # empty workbook
python build_pet_sitting_workbook.py --business "Paws & Claws"
python build_pet_sitting_workbook.py --currency "£" --unit miles
python build_pet_sitting_workbook.py --rows 1000           # more capacity
python build_pet_sitting_workbook.py --password secret     # own password
python build_pet_sitting_workbook.py --author "Your Name"
```

### B. Check it

```bash
python tools/validate_workbook.py "output/Pet Sitting Business Spreadsheet.xlsx"
python tools/check_sample_data.py "output/Pet Sitting Business Spreadsheet.xlsx"

# real recalculation - build a small workbook first, the full one is slow
python build_pet_sitting_workbook.py --rows 120 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

### C. Colour palette

Defined once in `pet_sitting_spreadsheet/config.py`; every sheet module
reads it from there.

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#0F172A` | titles, darkest text, overview tab colours |
| primary | `#4338CA` | header bands, profit series |
| primary_mid | `#6366F1` | section bands, revenue series, data bars |
| primary_soft | `#EEF2FF` | table headers, alternating rows |
| accent | `#F59E0B` | KPI tiles, accents, print tab colours |
| accent_soft | `#FFFBEB` | soft accent panels |
| input_bg | `#FFFDF5` | cells you type in (cream) |
| calc_bg | `#F1F5F9` | calculated cells (grey) |
| grey_text | `#64748B` | notes and secondary text |
| line | `#CBD5E1` | hairlines and borders |
| good | `#D1FAE5` / `#047857` | paid, in stock, resolved |
| warn | `#FEF3C7` / `#B45309` | due soon, low stock |
| bad | `#FFE4E6` / `#BE123C` | overdue, out of stock, expired |
| info | `#DBEAFE` / `#1D4ED8` | neutral information |
| note_bg | `#F8FAFC` | note boxes |

### D. File tree

```
build_pet_sitting_workbook.py
README.md
SOURCE_CODE.md
pet_sitting_spreadsheet/
    __init__.py   __main__.py   cli.py        config.py
    layout.py     formats.py    writer.py     names.py
    build.py      sample_data.py
    sheets/
        __init__.py   common.py     lists.py       settings.py
        services.py   clients.py    pets.py        bookings.py
        visits.py     health.py     incidents.py   messages.py
        invoices.py   payments.py   expenses.py    mileage.py
        staff.py      inventory.py  reminders.py   calc.py
        dashboard.py  reports.py    budget.py      start_here.py
        printables.py help_tab.py
tools/
    validate_workbook.py   check_sample_data.py   recalc_check.py
    export_source_md.py    make_download_zip.py
```
"""

MEAL_APPENDIX = """\
## Appendix

### A. Build the workbook

```bash
python build_meal_planner_workbook.py                       # demo data
python build_meal_planner_workbook.py --blank               # empty workbook
python build_meal_planner_workbook.py --household "The Khans"
python build_meal_planner_workbook.py --cook "Ayesha"
python build_meal_planner_workbook.py --currency "£" --units Imperial
python build_meal_planner_workbook.py --budget 150          # a week
python build_meal_planner_workbook.py --year 2027
python build_meal_planner_workbook.py --week-start Sunday
python build_meal_planner_workbook.py --rows 300            # more capacity
python build_meal_planner_workbook.py --password secret     # own password
python build_meal_planner_workbook.py --author "Your Name"
```

### B. Check it

```bash
python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"
python tools/check_meal_sample.py "output/Meal Planner & Grocery List.xlsx"

# real recalculation - build a small workbook first, the full one is slow
python build_meal_planner_workbook.py --rows 100 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

### C. Colour palette

Defined once in `meal_planner_spreadsheet/config.py`; every sheet module
reads it from there.

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#1E2C22` | titles, darkest text |
| primary | `#2F5E43` | header bands, tab colours |
| primary_mid | `#4E8A63` | section bands, navigation strip |
| primary_soft | `#E2EFE6` | totals, alternating rows |
| accent | `#D9703C` | terracotta accents, KPI money tiles |
| accent_soft | `#FBE9DC` | soft accent panels |
| input_bg | `#FFFDF7` | cells you type in (warm cream) |
| calc_bg | `#EFF4F0` | calculated cells (soft sage) |
| grey_text | `#5A6560` | notes and secondary text |
| line | `#C2D4C7` | hairlines and borders |
| good | `#D9F2E4` / `#0E6B45` | fresh, on target, in stock |
| warn | `#FFF1CF` / `#8A5A00` | use soon, close to budget |
| bad | `#FBD9DD` / `#9C1C2E` | expired, over budget, bin it |
| info | `#DEE8FA` / `#2A4A8B` | neutral information |
| note_bg | `#F7FAF8` | note boxes |

### D. How a formula is written

No sheet module contains a hard coded column letter.  Formulas are
templates, and the layout engine expands them:

```
"=IF({recipe}{r}=\"\",\"\",SUMIFS([[Recipe Ingredients.line_cost]],"
 "[[Recipe Ingredients.recipe]],{recipe}{r}))"
```

| Token | Becomes |
| --- | --- |
| `{r}` | the current Excel row number |
| `{key}` | the column letter of that column on the same sheet |
| `{key_first}` / `{key_last}` | the top and bottom of that column |
| `[[Sheet.key]]` | the whole data range of that column |
| `[[Sheet.key#r]]` | one cell of that column, on the same row |

So a column can be moved, widened or deleted in the sheet module and every
formula follows.

### E. File tree

```
build_meal_planner_workbook.py
README_MEAL.md
SOURCE_CODE_MEAL.md
meal_planner_spreadsheet/
    __init__.py   __main__.py   cli.py        config.py
    layout.py     formats.py    writer.py     names.py
    build.py      sample_data.py
    sheets/
        __init__.py    lists.py        settings.py      household.py
        recipes.py     recipe_ingredients.py            ingredients.py
        meal_plan.py   grocery_list.py pantry.py        staples.py
        leftovers.py   food_waste.py   meal_prep.py     dietary_filters.py
        rotation.py    food_safety.py  fridge_freezer.py grocery_spending.py
        store_prices.py stores.py      events.py        sustainability.py
        recipe_costs.py converter.py   dashboard.py     weekly_planner.py
        monthly_planner.py nutrition.py budget.py       goals.py
        reports.py     start_here.py   print_week.py    print_shopping.py
        print_recipe.py help.py
tools/
    validate_meal_workbook.py   check_meal_sample.py   recalc_check.py
    export_source_md.py         make_download_zip.py
```
"""

PRODUCTS = {
    "pet": {
        "title": "Pet Sitting & Dog Walking Business Spreadsheet",
        "subtitle": "Complete source code of the generator that writes the "
                    ".xlsx product",
        "output": "SOURCE_CODE.md",
        "sections": PET_SECTIONS,
        "appendix": PET_APPENDIX,
        "cover": [
            "A pure Python program that writes a 27 tab Excel workbook for a "
            "pet sitting and dog walking business: clients, pets, bookings, "
            "visit logs, pricing, invoices, payments, expenses, mileage, "
            "staff, inventory, reminders, a dashboard, reports and a budget.",
            "",
            "**What it produces**",
            "",
            "| | |",
            "| --- | --- |",
            "| Tabs | 27 (26 visible + 1 hidden calculation engine) |",
            "| Formulas | about 50,800, all Excel 2010 safe |",
            "| Author | Novality Store |",
            "| Protection | every sheet, password `premium` |",
            "| Example data | 9 clients, 12 pets, 32 bookings, 23 invoices |",
            "| Dependency | XlsxWriter (openpyxl only for the checks) |",
        ],
        "options": [
            "-o, --output PATH     where to write the file",
            "--blank               no example data, just the empty workbook",
            "--no-protect          leave the sheets unlocked",
            "--password TEXT       protection password (default: premium)",
            "--author TEXT         document author  (default: Novality Store)",
            "--business TEXT       business name on the cover and invoices",
            "--currency SYMBOL     currency symbol  (default: $)",
            "--unit {km,miles}     mileage unit",
            "--rows N              rows of capacity in the big registers",
            "--today YYYY-MM-DD    pretend it is this date (for the demo data)",
        ],
        "script": "build_pet_sitting_workbook.py",
    },
    "meal": {
        "title": "Automated Meal Planner & Grocery List Spreadsheet",
        "subtitle": "Complete source code of the generator that writes the "
                    ".xlsx product",
        "output": "SOURCE_CODE_MEAL.md",
        "sections": MEAL_SECTIONS,
        "appendix": MEAL_APPENDIX,
        "cover": [
            "A pure Python program that writes a 36 tab Excel workbook for a "
            "household: a weekly and monthly meal planner, a recipe book "
            "with costings, an automatic grocery list, a pantry with use-by "
            "dates, a food budget, a nutrition log and printable pages for "
            "the fridge door.",
            "",
            "**What it produces**",
            "",
            "| | |",
            "| --- | --- |",
            "| Tabs | 36, all visible |",
            "| Formulas | about 79,000, all Excel 2010 safe |",
            "| Author | Novality Store |",
            "| Protection | every sheet, password `premium` |",
            "| Charts | none - the numbers are the report |",
            "| Example data | 38 recipes, 62 ingredients, 107 planned meals |",
            "| Dependency | XlsxWriter (openpyxl only for the checks) |",
        ],
        "options": [
            "-o, --output PATH     where to write the file",
            "--blank               no example data, just the empty workbook",
            "--no-protect          leave the sheets unlocked",
            "--password TEXT       protection password (default: premium)",
            "--author TEXT         document author  (default: Novality Store)",
            "--household TEXT      household name on the Settings tab",
            "--cook TEXT           main cook's name",
            "--currency SYMBOL     currency symbol  (default: $)",
            "--currency-code TEXT  three letter code  (default: USD)",
            "--units {Metric,Imperial}  measurement system",
            "--week-start {Monday,Sunday}",
            "--year N              planning year",
            "--budget N            weekly grocery budget",
            "--servings N          default servings per meal",
            "--rows N              rows of capacity in the big registers",
            "--today YYYY-MM-DD    pretend it is this date (for the demo data)",
        ],
        "script": "build_meal_planner_workbook.py",
    },
}


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read().rstrip("\n")


def blurb(path: str, limit: int = 78) -> str:
    """First sentence of the module docstring, as a one line description."""
    try:
        text = ast.get_docstring(ast.parse(read(path))) or ""
    except (SyntaxError, OSError):                     # pragma: no cover
        text = ""
    text = " ".join(text.split())
    cut = re.search(r"\.(\s|$)", text)
    if cut:
        text = text[:cut.start()]
    text = text.strip().rstrip(".")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def anchor(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s+", "-", slug.strip())


def cover(product: dict) -> list:
    """The short front page: what it is, how to run it, the key numbers."""
    return [
        f"# {product['title']}",
        "",
        f"*{product['subtitle']}*",
        "",
    ] + product["cover"] + [
        "",
        "**How to run it**",
        "",
        "```bash",
        "pip install XlsxWriter",
        f"python {product['script']}",
        "```",
        "",
        "Every formula cell is locked and every sheet is protected with the "
        "password `premium`, while the cream coloured cells you are meant to "
        "type in stay open.",
        "",
        "**Useful options**",
        "",
        "```text",
    ] + product["options"] + [
        "```",
        "",
        "Excel 2010 safe throughout: no dynamic arrays, no `XLOOKUP`, no "
        "`IFS`, nothing that needs array entry - so it opens in Excel 2010 "
        "and later, Google Sheets, LibreOffice and Numbers.",
        "",
        "---",
        "",
        "## Contents",
        "",
        "| # | File | Lines | What it does |",
        "| --- | --- | --- | --- |",
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", choices=sorted(PRODUCTS), default="pet")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args(argv)

    product = PRODUCTS[args.product]
    output = args.output or product["output"]

    lines = cover(product)
    total = 0
    files = 0
    for number, (heading, _intro, paths) in enumerate(product["sections"],
                                                      start=1):
        for path in paths:
            count = len(read(path).splitlines())
            total += count
            files += 1
            lines.append(
                f"| {number} | [`{path}`](#{anchor(path)}) | {count} | "
                f"{blurb(path) or '-'} |")

    lines += ["", "---", ""]

    for heading, intro, paths in product["sections"]:
        lines += [f"## {heading}", "", intro, ""]
        for path in paths:
            code = read(path)
            count = len(code.splitlines())
            note = blurb(path, limit=120)
            lines.append(f"### `{path}`")
            lines.append("")
            if note:
                lines.append(f"{note} *({count} lines)*")
            else:
                lines.append(f"*({count} lines)*")
            # four backticks, so a fence inside a docstring cannot
            # close the block early
            lines += ["", "````python", code, "````", ""]
        lines += ["---", ""]

    lines += [product["appendix"], ""]
    lines += [f"*{files} files, {total:,} lines of Python.*", ""]

    with open(output, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    size = os.path.getsize(output)
    print(f"{output}  ({files} files, {total:,} lines, "
          f"{size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

### `tools/make_download_zip.py`

Pack the generator into a single zip people can download and run *(124 lines)*

````python
"""Pack the generator into a single zip people can download and run.

    python tools/make_download_zip.py

Writes `download/pet-sitting-spreadsheet-source.zip` containing the
generator, the quality tools, the documentation and a `requirements.txt`,
all under one folder so it unpacks tidily.

The vendored copy of XlsxWriter in this repository is deliberately left
out: the zip is meant to be unpacked anywhere and run against a normal
`pip install XlsxWriter`.  Timestamps are fixed so rebuilding the zip
without changing any source produces exactly the same bytes.
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = "pet-sitting-spreadsheet"
DEFAULT_OUT = os.path.join("download", "pet-sitting-spreadsheet-source.zip")

#: Same date for every entry, so the zip only changes when the code does.
STAMP = (2026, 1, 1, 0, 0, 0)

FILES = [
    "build_pet_sitting_workbook.py",
    "README.md",
    "SOURCE_CODE.md",
]
TREES = ["pet_sitting_spreadsheet", "tools"]

REQUIREMENTS = """\
# The generator needs one package.
XlsxWriter>=3.0

# Only for the optional checks in tools/
# openpyxl>=3.1     validate_workbook.py, check_sample_data.py
# formulas>=1.3     recalc_check.py
"""

HOW_TO_RUN = """\
Pet Sitting & Dog Walking Business Spreadsheet
==============================================

    pip install XlsxWriter
    python build_pet_sitting_workbook.py

The workbook appears in:

    output/Pet Sitting Business Spreadsheet.xlsx

Useful options
--------------
    --blank                 empty workbook, no example data
    --business "My Name"    your business name on the cover and invoices
    --currency EUR-symbol   e.g. --currency "\u20ac" --currency-code EUR
    --unit miles            mileage in miles instead of km
    --password secret       change the sheet protection password
    --author "Your Name"    change the document author
    --rows 1000             more rows of capacity in the big registers

Every formula cell is locked and every sheet is protected with the
password `premium` so the maths cannot be typed over by accident; the
cream coloured cells are the ones meant for typing in.

README.md explains how it is built, what is on each of the 27 tabs and
how to change things.  SOURCE_CODE.md is the whole program in one
readable document.
"""


def gather() -> list:
    """`[(archive name, text)]` for everything that goes in the zip."""
    items = []
    for name in FILES:
        with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
            items.append((name, handle.read()))
    for tree in TREES:
        for folder, dirs, names in os.walk(os.path.join(ROOT, tree)):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for name in sorted(names):
                if not name.endswith(".py"):
                    continue
                full = os.path.join(folder, name)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                with open(full, encoding="utf-8") as handle:
                    items.append((rel, handle.read()))
    items.append(("requirements.txt", REQUIREMENTS))
    items.append(("HOW TO RUN.txt", HOW_TO_RUN))
    return items


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    out = args.output
    folder = os.path.dirname(os.path.abspath(out))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    items = gather()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, text in items:
            info = zipfile.ZipInfo(f"{FOLDER}/{name}", date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, text)

    size = os.path.getsize(out)
    lines = sum(len(text.splitlines()) for name, text in items
                if name.endswith(".py"))
    print(f"{out}  ({len(items)} files, {lines:,} lines of Python, "
          f"{size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

---

## Appendix

### A. Build the workbook

```bash
python build_meal_planner_workbook.py                       # demo data
python build_meal_planner_workbook.py --blank               # empty workbook
python build_meal_planner_workbook.py --household "The Khans"
python build_meal_planner_workbook.py --cook "Ayesha"
python build_meal_planner_workbook.py --currency "£" --units Imperial
python build_meal_planner_workbook.py --budget 150          # a week
python build_meal_planner_workbook.py --year 2027
python build_meal_planner_workbook.py --week-start Sunday
python build_meal_planner_workbook.py --rows 300            # more capacity
python build_meal_planner_workbook.py --password secret     # own password
python build_meal_planner_workbook.py --author "Your Name"
```

### B. Check it

```bash
python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"
python tools/check_meal_sample.py "output/Meal Planner & Grocery List.xlsx"

# real recalculation - build a small workbook first, the full one is slow
python build_meal_planner_workbook.py --rows 100 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

### C. Colour palette

Defined once in `meal_planner_spreadsheet/config.py`; every sheet module
reads it from there.

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#1E2C22` | titles, darkest text |
| primary | `#2F5E43` | header bands, tab colours |
| primary_mid | `#4E8A63` | section bands, navigation strip |
| primary_soft | `#E2EFE6` | totals, alternating rows |
| accent | `#D9703C` | terracotta accents, KPI money tiles |
| accent_soft | `#FBE9DC` | soft accent panels |
| input_bg | `#FFFDF7` | cells you type in (warm cream) |
| calc_bg | `#EFF4F0` | calculated cells (soft sage) |
| grey_text | `#5A6560` | notes and secondary text |
| line | `#C2D4C7` | hairlines and borders |
| good | `#D9F2E4` / `#0E6B45` | fresh, on target, in stock |
| warn | `#FFF1CF` / `#8A5A00` | use soon, close to budget |
| bad | `#FBD9DD` / `#9C1C2E` | expired, over budget, bin it |
| info | `#DEE8FA` / `#2A4A8B` | neutral information |
| note_bg | `#F7FAF8` | note boxes |

### D. How a formula is written

No sheet module contains a hard coded column letter.  Formulas are
templates, and the layout engine expands them:

```
"=IF({recipe}{r}="","",SUMIFS([[Recipe Ingredients.line_cost]],"
 "[[Recipe Ingredients.recipe]],{recipe}{r}))"
```

| Token | Becomes |
| --- | --- |
| `{r}` | the current Excel row number |
| `{key}` | the column letter of that column on the same sheet |
| `{key_first}` / `{key_last}` | the top and bottom of that column |
| `[[Sheet.key]]` | the whole data range of that column |
| `[[Sheet.key#r]]` | one cell of that column, on the same row |

So a column can be moved, widened or deleted in the sheet module and every
formula follows.

### E. File tree

```
build_meal_planner_workbook.py
README_MEAL.md
SOURCE_CODE_MEAL.md
meal_planner_spreadsheet/
    __init__.py   __main__.py   cli.py        config.py
    layout.py     formats.py    writer.py     names.py
    build.py      sample_data.py
    sheets/
        __init__.py    lists.py        settings.py      household.py
        recipes.py     recipe_ingredients.py            ingredients.py
        meal_plan.py   grocery_list.py pantry.py        staples.py
        leftovers.py   food_waste.py   meal_prep.py     dietary_filters.py
        rotation.py    food_safety.py  fridge_freezer.py grocery_spending.py
        store_prices.py stores.py      events.py        sustainability.py
        recipe_costs.py converter.py   dashboard.py     weekly_planner.py
        monthly_planner.py nutrition.py budget.py       goals.py
        reports.py     start_here.py   print_week.py    print_shopping.py
        print_recipe.py help.py
tools/
    validate_meal_workbook.py   check_meal_sample.py   recalc_check.py
    export_source_md.py         make_download_zip.py
```


*53 files, 9,634 lines of Python.*
