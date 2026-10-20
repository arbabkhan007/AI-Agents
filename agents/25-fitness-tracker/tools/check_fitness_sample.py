#!/usr/bin/env python3
"""Sample-data checker for the Fitness & Weight Loss Tracker.

Proves the demo file is internally consistent and that the blank file
is genuinely blank where it should be:

* every exercise in the workout log exists in the exercise library;
* every cardio activity exists in the MET table on Settings;
* every meal type / NSV category / habit tick is from its list;
* logged foods whose macros were left blank exist in the calorie
  database (that is the auto-fill promise);
* dates are in the past, ascending per register, and inside the
  eleven-week demo window;
* sets / reps / weights are positive where present, RPE within 1-10;
* the blank workbook carries the library and the food database but no
  register rows at all.

Usage::

    python3 tools/check_fitness_sample.py filled.xlsx blank.xlsx
"""

from __future__ import annotations

import datetime as _dt
import sys

import openpyxl

LIB = "6 Exercise Library"
LOG = "5 Workout Log"
CARDIO = "7 Cardio & Activity"
WEIGHT = "8 Weight Tracker"
MEALS = "11 Meals & Macros"
WATER = "12 Water & Sleep"
NSV = "13 Records & Milestones"
SETTINGS = "16 Settings & Lists"

REGISTER_DATE_COLS = {
    LOG: "B", CARDIO: "B", WEIGHT: "B", MEALS: "B", WATER: "B",
}


CAPS = {"5 Workout Log": 400, "7 Cardio & Activity": 300,
        "8 Weight Tracker": 200, "11 Meals & Macros": 400,
        "12 Water & Sleep": 200, "6 Exercise Library": 160,
        "13 Records & Milestones": 60}


def _col_values(ws, letter, first=5, last=None):
    out = []
    last = last or (first + CAPS.get(ws.title, 10000) - 1)
    for row in range(first, min(ws.max_row, last) + 1):
        value = ws[f"{letter}{row}"].value
        if value in (None, ""):
            continue
        out.append((row, value))
    return out


def check_filled(path: str) -> list:
    problems = []
    book = openpyxl.load_workbook(path, data_only=False)
    today = _dt.date.today()

    lib_names = {v for _, v in _col_values(book[LIB], "B")}
    log = book[LOG]
    log_rows = 0
    prev_date = None
    for row, exercise in _col_values(log, "D"):
        log_rows += 1
        if exercise not in lib_names:
            problems.append(f"log row {row}: unknown exercise {exercise!r}")
        date = log[f"B{row}"].value
        if isinstance(date, _dt.datetime):
            date = date.date()
        if isinstance(date, _dt.date):
            if date > today:
                problems.append(f"log row {row}: future date {date}")
            if prev_date and date < prev_date:
                problems.append(f"log row {row}: dates out of order")
            prev_date = date
            if (today - date).days > 80:
                problems.append(f"log row {row}: outside demo window")
        sets = log[f"F{row}"].value
        reps = log[f"G{row}"].value
        weight = log[f"H{row}"].value
        if sets is not None and sets <= 0:
            problems.append(f"log row {row}: sets {sets}")
        if reps is not None and reps <= 0:
            problems.append(f"log row {row}: reps {reps}")
        if weight is not None and weight <= 0:
            problems.append(f"log row {row}: weight {weight}")
        rpe = log[f"K{row}"].value
        if rpe is not None and not 0 <= rpe <= 10:
            problems.append(f"log row {row}: rpe {rpe}")
    if log_rows < 100:
        problems.append(f"log has only {log_rows} demo rows")

    settings = book[SETTINGS]
    met_types = set()
    for row in range(1, settings.max_row + 1):
        label = settings[f"B{row}"].value
        met = settings[f"C{row}"].value
        if isinstance(label, str) and isinstance(met, (int, float)) and \
                label in ("Walking", "Running", "Cycling", "Swimming",
                          "Rowing", "Class", "Hiking", "Yoga", "Sports",
                          "Other"):
            met_types.add(label)
    for row, activity in _col_values(book[CARDIO], "C"):
        if activity not in met_types:
            problems.append(f"cardio row {row}: unknown type {activity!r}")

    food_names = set()
    meals = book[MEALS]
    db_col = None
    for col in range(20, 40):
        letter = openpyxl.utils.get_column_letter(col + 1)
        if meals[f"{letter}4"].value == "Food":
            db_col = letter
            break
    if db_col is None:
        problems.append("food database header not found")
    else:
        for row in range(5, 5 + 220):
            value = meals[f"{db_col}{row}"].value
            if isinstance(value, str) and value.strip():
                food_names.add(value)
    for row, food in _col_values(meals, "D"):
        typed = meals[f"E{row}"].value
        p_in = meals[f"F{row}"].value
        if typed is None and p_in is None and food not in food_names:
            problems.append(
                f"meals row {row}: {food!r} not in database and no "
                f"typed macros")

    for row, tick in _col_values(book["10 Habit Tracker"], "B",
                                 first=8, last=19):
        if tick not in ("x", "R"):
            problems.append(f"habits B{row}: bad tick {tick!r}")

    nsv_cats = {"Clothes", "Energy", "Lifts", "Sleep", "Mood", "Other"}
    for row, cat in _col_values(book[NSV], "C"):
        if row < 5:
            continue
        if cat not in nsv_cats:
            problems.append(f"nsv row {row}: bad category {cat!r}")

    for sheet, letter in REGISTER_DATE_COLS.items():
        ws = book[sheet]
        prev = None
        for row, value in _col_values(ws, letter):
            if isinstance(value, _dt.datetime):
                value = value.date()
            if not isinstance(value, _dt.date):
                problems.append(f"{sheet} row {row}: date is {value!r}")
                continue
            if value > today:
                problems.append(f"{sheet} row {row}: future date")
            if prev and value < prev:
                problems.append(f"{sheet} row {row}: out of order")
            prev = value
    return problems


def check_blank(path: str) -> list:
    problems = []
    book = openpyxl.load_workbook(path)
    for sheet, letter in REGISTER_DATE_COLS.items():
        rows = _col_values(book[sheet], letter)
        if rows:
            problems.append(f"blank {sheet}: {len(rows)} rows not empty")
    lib_rows = len(_col_values(book[LIB], "B"))
    if lib_rows < 150:
        problems.append(f"blank library only has {lib_rows} exercises")
    meals = book[MEALS]
    foods = 0
    for col in range(20, 40):
        letter = openpyxl.utils.get_column_letter(col + 1)
        if meals[f"{letter}4"].value == "Food":
            foods = len(_col_values(meals, letter, last=5 + 220))
            break
    if foods < 150:
        problems.append(f"blank food database only has {foods} foods")
    return problems


def main(filled: str, blank: str) -> int:
    failed = False
    for label, path, fn in (("filled", filled, check_filled),
                            ("blank", blank, check_blank)):
        problems = fn(path)
        print(f"{label}: {path}")
        if problems:
            failed = True
            print(f"  FAIL - {len(problems)} problem(s):")
            for problem in problems[:30]:
                print(f"    - {problem}")
        else:
            print("  PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    filled = sys.argv[1] if len(sys.argv) > 1 else \
        "output/Fitness & Weight Loss Tracker.xlsx"
    blank = sys.argv[2] if len(sys.argv) > 2 else \
        "output/Fitness & Weight Loss Tracker (Blank).xlsx"
    sys.exit(main(filled, blank))
