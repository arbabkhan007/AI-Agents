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

