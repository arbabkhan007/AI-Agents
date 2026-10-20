"""
Configuration for the Fitness & Weight Loss Tracker.

Everything a buyer may want to re-brand lives here, so the workbook can
be regenerated for a different shop, unit system or capacity without
touching any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Fitness & Weight Loss Tracker"
PRODUCT_SUBTITLE = (
    "Workout Planner and Log, Weight and Body Measurement Tracker, "
    "Habit and Macro Tracker for Excel and Google Sheets"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Fitness & Weight Loss Tracker Spreadsheet, Workout Planner and Log, "
    "Weight and Body Measurement Tracker, Habit and Macro Tracker for "
    "Excel and Google Sheets"
)

#: Password that protects every sheet so formula cells cannot be edited
#: by accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: The health disclaimer that travels in the file and in the listing.
DISCLAIMER = (
    "This spreadsheet is a personal organisation and tracking tool. It is "
    "not medical advice, a diagnosis, a treatment plan or a substitute for "
    "professional care. Calorie, macro, body-fat and energy-expenditure "
    "figures are estimates produced from the numbers you type in, and all "
    "targets are yours to set and edit. Speak to a doctor or a registered "
    "professional before starting a new exercise or nutrition programme, "
    "particularly if you are pregnant, managing a health condition, or "
    "taking medication. No outcome of any kind is promised."
)
DISCLAIMER_SHORT = (
    "For personal tracking only - not medical advice. "
    "All targets are yours to set."
)

#: The sixteen tabs, in workbook order.  The numbers are part of the tab
#: names so the file opens in a sensible order.
SHEET_TABS = [
    "1 Start Here",
    "2 Profile & Goals",
    "3 Dashboard",
    "4 Workout Planner",
    "5 Workout Log",
    "6 Exercise Library",
    "7 Cardio & Activity",
    "8 Weight Tracker",
    "9 Body Measurements",
    "10 Habit Tracker",
    "11 Meals & Macros",
    "12 Water & Sleep",
    "13 Records & Milestones",
    "14 Weekly & Monthly Review",
    "15 Reports & Charts",
    "16 Settings & Lists",
]

# ---------------------------------------------------------------------------
# Lists that feed the drop downs (all editable on 16 Settings & Lists)
# ---------------------------------------------------------------------------

MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps", "Quadriceps",
    "Hamstrings", "Glutes", "Calves", "Core", "Full body",
]

EQUIPMENT = [
    "Barbell", "Dumbbell", "Kettlebell", "Cable", "Machine",
    "Pull-up bar", "Bands", "Bodyweight", "EZ bar", "Trap bar",
    "Ring", "Medicine ball", "Rowing machine", "Treadmill", "Bike",
    "Other",
]

MOVEMENT_PATTERNS = [
    "Squat", "Hinge", "Lunge", "Push", "Pull", "Carry", "Rotate",
    "Brace", "Jump", "Isolation", "Conditioning",
]

DIFFICULTY = ["Beginner", "Intermediate", "Advanced"]

TRAINING_SPLITS = [
    "Push / Pull / Legs", "Upper / Lower", "Full body",
    "Bro split", "Custom",
]

ACTIVITY_LEVELS = [
    ("Sedentary - desk day, little training", 1.2),
    ("Light - training 1-3 days a week", 1.375),
    ("Moderate - training 3-5 days a week", 1.55),
    ("Active - training 6-7 days a week", 1.725),
    ("Athlete - twice a day or physical job", 1.9),
]

#: Activity type -> MET value used for the optional calorie estimate.
#: MET x 3.5 x bodyweight(kg) / 200 = kcal per minute.
ACTIVITY_TYPES = [
    ("Walking", 3.5),
    ("Running", 9.8),
    ("Cycling", 7.5),
    ("Swimming", 6.0),
    ("Rowing", 7.0),
    ("Class", 6.5),
    ("Hiking", 6.0),
    ("Yoga", 3.0),
    ("Sports", 8.0),
    ("Other", 5.0),
]

MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack", "Drink"]

GOAL_TYPES = ["Weight", "Strength", "Consistency", "Distance",
              "Habit", "Custom"]

SEX_OPTIONS = ["Female", "Male", "Other"]

#: Mifflin-St Jeor constant per sex option.
SEX_FACTORS = [("Female", -161), ("Male", 5), ("Other", -78)]

HABIT_DEFAULTS = [
    "Train as planned", "10k steps", "Protein at every meal",
    "2 L water", "Sleep 7+ hours", "No liquid calories",
    "Stretch or mobility", "Log meals", "Early night",
    "Morning walk", "Strength session", "Vegetables at dinner",
]

NSV_CATEGORIES = ["Clothes", "Energy", "Lifts", "Sleep", "Mood", "Other"]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]

#: Plate denominations for the plate calculator, heaviest first.
PLATES_KG = [25.0, 20.0, 15.0, 10.0, 5.0, 2.5, 1.25]
PLATES_LB = [45.0, 35.0, 25.0, 10.0, 5.0, 2.5]
BAR_KG = 20.0
BAR_LB = 45.0

#: Conversion factors (also written on Settings & Lists).
KG_PER_LB = 0.45359237
CM_PER_IN = 2.54
KM_PER_MI = 1.609344

#: Milestone step for the weight tracker, per unit system.
MILESTONE_KG = 2.0
MILESTONE_LB = 5.0


# ---------------------------------------------------------------------------
# Colours - training palette: pine green, energy orange, chalk cream
# ---------------------------------------------------------------------------

class Palette:
    ink = "#20262B"           # near-black slate - titles
    primary = "#14655A"       # pine green headers
    primary_mid = "#3E897D"   # section bands
    primary_soft = "#DDEDE9"  # light band / alternating rows
    accent = "#E4572E"        # energy orange accent
    accent_soft = "#FBE3DA"
    input_bg = "#FFFDF5"      # editable cell background (cream)
    input_border = "#D9CDB4"
    calc_bg = "#ECEEEA"       # locked formula cell background (cool grey)
    calc_border = "#D4D8D2"
    white = "#FFFFFF"
    grey_text = "#5C6660"
    line = "#CBD3CC"
    good_bg = "#DCEBD8"
    good_text = "#2F5A2B"
    warn_bg = "#FDEDD2"
    warn_text = "#8A5A00"
    bad_bg = "#F8DAD9"
    bad_text = "#9C2A24"
    info_bg = "#E2E6F3"
    info_text = "#3A4578"
    note_bg = "#F7F6F1"


# ---------------------------------------------------------------------------
# Row capacity of every register
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Workout Log": 400,
    "Exercise Library": 160,
    "Cardio & Activity": 300,
    "Weight Tracker": 200,
    "Body Measurements": 104,
    "Meals & Macros": 400,
    "Food Database": 220,
    "Water & Sleep": 200,
    "Non-Scale Victories": 60,
}


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
    decimals: int = 2
    measure_system: str = "Metric"       # Metric | Imperial

    # Profile defaults ------------------------------------------------------
    height_cm: float = 172.0
    age_years: int = 34
    sex: str = "Female"
    start_weight_kg: float = 78.0
    goal_weight_kg: float = 70.0
    activity_level: str = ACTIVITY_LEVELS[2][0]

    # Nutrition targets -----------------------------------------------------
    calorie_target: float = 1900.0
    protein_target: float = 130.0
    carb_target: float = 170.0
    fat_target: float = 55.0
    fibre_target: float = 25.0
    water_target_ml: float = 2000.0
    glass_ml: float = 250.0

    # Training --------------------------------------------------------------
    sessions_per_week: int = 4
    weekly_minutes_target: float = 180.0
    training_split: str = TRAINING_SPLITS[0]
    week_start: str = "Monday"           # Monday | Sunday
    programme_weeks: int = 12

    # Behaviour -------------------------------------------------------------
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    @property
    def metric(self) -> bool:
        return self.measure_system.lower().startswith("met")

    @property
    def weight_unit(self) -> str:
        return "kg" if self.metric else "lb"

    @property
    def length_unit(self) -> str:
        return "cm" if self.metric else "in"

    @property
    def distance_unit(self) -> str:
        return "km" if self.metric else "mi"

    @property
    def milestone_step(self) -> float:
        return MILESTONE_KG if self.metric else MILESTONE_LB

    def scale_rows(self, log_rows: int) -> None:
        """Scale every register in place so Workout Log holds N rows."""
        base = DEFAULT_ROWS["Workout Log"]
        factor = max(0.02, float(log_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings (money is kept for completeness: some buyers
    # track coaching or class costs in the notes of their own columns).
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.00;[Red]-{s}#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0;[Red]-{s}#,##0'

    @property
    def money_format_4(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.0000;[Red]-{s}#,##0.0000'
