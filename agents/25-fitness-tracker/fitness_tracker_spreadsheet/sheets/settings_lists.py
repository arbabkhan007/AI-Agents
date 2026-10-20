"""16 Settings & Lists - every drop down, target and conversion factor.

This tab owns the workbook level defined names (Units, KgPerLb, the
list ranges, the MET table) so it is the reference point for every
other tab.  All list blocks are plain input cells: the buyer edits a
list here and every drop down follows.
"""

from __future__ import annotations

from ..config import (ACTIVITY_LEVELS, ACTIVITY_TYPES, DIFFICULTY,
                      EQUIPMENT, GOAL_TYPES, HABIT_DEFAULTS, MEAL_TYPES,
                      MOVEMENT_PATTERNS, MUSCLE_GROUPS, NSV_CATEGORIES,
                      Palette, SEX_OPTIONS, TRAINING_SPLITS, WEEKDAYS,
                      Config)
from ..writer import SheetWriter, list_from

NAME = "16 Settings & Lists"

#: block column layout: label A, values B, help D..
_LIST_DEFS = [
    ("ListMuscle", "Muscle groups", MUSCLE_GROUPS),
    ("ListEquipment", "Equipment", EQUIPMENT),
    ("ListPattern", "Movement patterns", MOVEMENT_PATTERNS),
    ("ListDifficulty", "Difficulty", DIFFICULTY),
    ("ListSplit", "Training splits", TRAINING_SPLITS),
    ("ListMeal", "Meal types", MEAL_TYPES),
    ("ListGoalType", "Goal types", GOAL_TYPES),
    ("ListSex", "Sex (for BMR and Navy body fat)", SEX_OPTIONS),
    ("ListNSV", "Non-scale victory categories", NSV_CATEGORIES),
    ("ListWeekday", "Weekday names, Monday first", WEEKDAYS),
]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary, landscape=False)
    last_col = 9
    sheet.banner("16  Settings & Lists",
                 "Every drop down, target, conversion and habit name in "
                 "one place - edit here, the whole workbook follows.",
                 last_col)
    row = 4
    row = sheet.section(row, "UNITS, CALENDAR AND CONVERSIONS", last_col)
    row = sheet.field(row, "Unit system", cfg.measure_system,
                      validate={"validate": "list",
                                "source": ["Metric", "Imperial"]},
                      name="Units",
                      help_text="Switches every display, chart and target. "
                                "Rows keep their own unit stamp, so nothing "
                                "you logged is misread.")
    row = sheet.field(row, "Week starts on", cfg.week_start,
                      validate={"validate": "list",
                                "source": ["Monday", "Sunday"]},
                      name="WeekStart",
                      help_text="Drives the planner, the weekly summaries "
                                "and the habit grid.")
    row = sheet.field(row, "One glass of water (ml)", cfg.glass_ml,
                      style="int", name="GlassML",
                      help_text="The water tab counts glasses in ml.")
    row = sheet.field(row, "Milestone step",
                      formula='IF(Units="Imperial",5,2)', style="number1",
                      name="MilestoneStep",
                      help_text="A milestone is flagged every 5 lb or 2 kg "
                                "of change from your starting weight.")
    row = sheet.field(row, "Kg per lb", 0.45359237, style="number",
                      name="KgPerLb", help_text="Conversion factor.")
    row = sheet.field(row, "Cm per inch", 2.54, style="number",
                      name="CmPerIn", help_text="Conversion factor.")
    row = sheet.field(row, "Km per mile", 1.609344, style="number",
                      name="KmPerMi", help_text="Conversion factor.")
    row += 1

    row = sheet.section(row, "NUTRITION TARGETS (YOURS TO SET)", last_col)
    row = sheet.field(row, "Daily calories", cfg.calorie_target,
                      style="int", name="CalTarget",
                      help_text="An estimate is on Profile & Goals (TDEE); "
                                "type over it with your own number.")
    row = sheet.field(row, "Daily protein (g)", cfg.protein_target,
                      style="int", name="ProteinTarget")
    row = sheet.field(row, "Daily carbohydrate (g)", cfg.carb_target,
                      style="int", name="CarbTarget")
    row = sheet.field(row, "Daily fat (g)", cfg.fat_target,
                      style="int", name="FatTarget")
    row = sheet.field(row, "Daily fibre (g)", cfg.fibre_target,
                      style="int", name="FibreTarget")
    row = sheet.field(row, "Daily water (ml)", cfg.water_target_ml,
                      style="int", name="WaterTarget")
    row += 1

    row = sheet.section(row, "TRAINING TARGETS", last_col)
    row = sheet.field(row, "Sessions a week", cfg.sessions_per_week,
                      style="int", name="SessionsPerWeek")
    row = sheet.field(row, "Weekly minutes target",
                      cfg.weekly_minutes_target, style="int",
                      name="MinutesTarget")
    row = sheet.field(row, "Training split", cfg.training_split,
                      validate=list_from("ListSplit"), name="TrainingSplit")
    row += 1

    row = sheet.section(row, "ACTIVITY MULTIPLIERS (TDEE)", last_col)
    row = sheet.table_head(row, 1, ["Activity level", "Multiplier"],
                           widths=[44, 12])
    mult_first = row + 1
    for label, mult in ACTIVITY_LEVELS:
        sheet.write(row, 1, label, sheet.f.input("text"))
        sheet.write(row, 2, mult, sheet.f.input("number"))
        row += 1
    book.define_name("ListActivityLevel",
                     f"={_q(sheet)}!$B${mult_first}:$B${row - 1}")
    book.define_name("MultTable",
                     f"={_q(sheet)}!$B${mult_first}:$C${row - 1}")
    row += 1

    row = sheet.section(row, "MET VALUES (OPTIONAL CALORIE ESTIMATE)",
                        last_col)
    row = sheet.note(row, "MET x 3.5 x bodyweight in kg / 200 = kcal a "
                          "minute. Edit any row; the cardio tab reads this "
                          "table. It is an estimate, never a measurement.",
                     last_col, height=26)
    row = sheet.table_head(row, 1, ["Activity type", "MET"],
                           widths=[44, 12])
    met_first = row + 1
    for label, met in ACTIVITY_TYPES:
        sheet.write(row, 1, label, sheet.f.input("text"))
        sheet.write(row, 2, met, sheet.f.input("number"))
        row += 1
    book.define_name("ListActivityType",
                     f"={_q(sheet)}!$B${met_first}:$B${row - 1}")
    book.define_name("MetType",
                     f"={_q(sheet)}!$B${met_first}:$B${row - 1}")
    book.define_name("MetMET",
                     f"={_q(sheet)}!$C${met_first}:$C${row - 1}")
    row += 1

    row = sheet.section(row, "DROP DOWN LISTS (EDIT FREELY)", last_col)
    for name, title, values in _LIST_DEFS:
        row = sheet.subsection(row, title, last_col)
        first = row + 1
        for value in values:
            sheet.write(row, 1, value, sheet.f.input("text"))
            row += 1
        book.define_name(name, f"={_q(sheet)}!$B${first}:$B${row - 1}")
        row += 1

    row = sheet.section(row, "HABIT NAMES (12 SLOTS)", last_col)
    first = row + 1
    for habit in HABIT_DEFAULTS:
        sheet.write(row, 1, habit, sheet.f.input("text"))
        row += 1
    book.define_name("ListHabits", f"={_q(sheet)}!$B${first}:$B${row - 1}")
    row += 1

    row = sheet.section(row, "RPE SCALE (REFERENCE)", last_col)
    rpe = [("1-2", "Walking pace, could hold a long conversation"),
           ("3-4", "Easy work, breathing slightly up"),
           ("5-6", "Steady, talking in short sentences"),
           ("7", "Hard, one or two words at a time"),
           ("8", "Very hard, counting reps in your head"),
           ("9", "One rep left in the tank"),
           ("10", "Nothing left, race finish")]
    for score, meaning in rpe:
        sheet.write(row, 1, score, sheet.f.calc("text"))
        sheet.merge(row, 2, last_col, meaning, sheet.f.chrome("label"))
        row += 1
    row += 1

    row = sheet.section(row, "HOUSEKEEPING", last_col)
    row = sheet.field(row, "Sheet protection password", cfg.password,
                      mode="plain", style="text",
                      help_text="Review > Unprotect Sheet, then this word. "
                                "Protection is a guard rail, not encryption.")
    row = sheet.field(row, "Version", cfg.version, mode="plain")
    row = sheet.field(row, "Author", cfg.author, mode="plain")
    row = sheet.note(row, "Colour key: cream cells are yours to type in, "
                          "grey cells calculate. Every list on this tab is "
                          "a cream cell - add your own exercises, foods, "
                          "habits and goals here and the drop downs grow.",
                     last_col, height=30)
    sheet.finish(freeze_row=3, freeze_col=0, gridlines=False)
    return sheet


def _q(sheet: SheetWriter) -> str:
    from ..layout import quote_sheet
    return quote_sheet(sheet.name)
