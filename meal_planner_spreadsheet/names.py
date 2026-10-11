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
