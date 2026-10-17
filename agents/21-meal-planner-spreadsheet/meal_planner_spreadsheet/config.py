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
