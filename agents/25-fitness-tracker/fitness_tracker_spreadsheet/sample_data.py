"""Example data for the filled workbook.

Eleven weeks of believable training that joins up: every exercise name
exists in the library, every cardio type in the MET table, every
matching meal name in the calorie database, and the numbers progress
the way a decent block of training does.  The blank build writes none
of it.
"""

from __future__ import annotations

import datetime as _dt
import math
from typing import Dict, List

from .config import Config

PUSH = ["Barbell Bench Press", "Incline Dumbbell Press", "Overhead Press",
        "Lateral Raise", "Triceps Pushdown"]
PULL = ["Lat Pulldown", "Barbell Row", "Face Pull", "Dumbbell Curl",
        "Hammer Curl"]
LEGS = ["Back Squat", "Romanian Deadlift", "Walking Lunge", "Leg Curl",
        "Standing Calf Raise"]
UPPER = ["Barbell Bench Press", "Barbell Row", "Seated Dumbbell Press",
         "Dumbbell Curl", "Triceps Pushdown"]

SESSIONS = [("Push A", PUSH, 0), ("Pull A", PULL, 1), ("Legs A", LEGS, 3),
            ("Upper B", UPPER, 5)]

BASE_KG = {
    "Barbell Bench Press": 40.0, "Incline Dumbbell Press": 22.0,
    "Overhead Press": 30.0, "Lateral Raise": 8.0,
    "Triceps Pushdown": 20.0, "Lat Pulldown": 45.0, "Barbell Row": 50.0,
    "Face Pull": 25.0, "Dumbbell Curl": 12.0, "Hammer Curl": 14.0,
    "Back Squat": 60.0, "Romanian Deadlift": 70.0, "Walking Lunge": 16.0,
    "Leg Curl": 30.0, "Standing Calf Raise": 40.0,
    "Seated Dumbbell Press": 24.0,
}
BIG_LIFTS = {"Barbell Bench Press", "Back Squat", "Romanian Deadlift",
             "Barbell Row", "Overhead Press"}


def _monday(day: _dt.date) -> _dt.date:
    return day - _dt.timedelta(days=day.weekday())


def _kg(cfg: Config, kg: float) -> float:
    return round(kg if cfg.metric else kg / 0.45359237, 1)


def _km(cfg: Config, km: float) -> float:
    return round(km if cfg.metric else km / 1.609344, 1)


def _cm(cfg: Config, cm: float) -> float:
    return round(cm if cfg.metric else cm / 2.54, 1)


def log_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    monday = _monday(today)
    for week in range(10, -1, -1):
        week_start = monday - _dt.timedelta(days=7 * week)
        sessions = SESSIONS if week else SESSIONS[:2]
        for name, exercises, day_offset in sessions:
            day = week_start + _dt.timedelta(days=day_offset)
            if day > today:
                continue
            for i, exercise in enumerate(exercises):
                base = BASE_KG[exercise]
                step = 2.5 if exercise in BIG_LIFTS else 1.25
                weight = base + step * ((10 - week) // 2)
                reps = 8 if week else 7
                rows.append({
                    "date": day,
                    "session": name,
                    "exercise": exercise,
                    "sets": 3,
                    "reps": reps,
                    "weight": _kg(cfg, weight),
                    "stamp": "kg" if cfg.metric else "lb",
                    "rpe": 7 + (1 if (10 - week) % 3 == 2 else 0),
                    "rest": 120 if exercise in BIG_LIFTS else 90,
                    "dur": 55 if i == 0 else None,
                    "warmup": "Yes" if i == 0 else "No",
                    "done": "Yes",
                    "notes": "sample row - delete me" if week == 10
                             and i == 0 else None,
                })
    return rows


def cardio_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    monday = _monday(today)
    for week in range(10, -1, -1):
        week_start = monday - _dt.timedelta(days=7 * week)
        saturday = week_start + _dt.timedelta(days=5)
        sunday = week_start + _dt.timedelta(days=6)
        if saturday <= today:
            rows.append({
                "date": saturday, "type": "Walking",
                "distance": _km(cfg, 6.0 + (week % 3) * 0.5),
                "stamp": "km" if cfg.metric else "mi",
                "dur": 65 + (week % 3) * 5, "steps": 9200 + week * 37,
                "hr": 104 + (week % 4), "rpe": 3,
                "notes": None,
            })
        if sunday <= today:
            if week % 2:
                rows.append({
                    "date": sunday, "type": "Running",
                    "distance": _km(cfg, 5.0), "stamp": "km" if cfg.metric
                    else "mi", "dur": 33 - (10 - week) // 3,
                    "hr": 148, "rpe": 7,
                })
            else:
                rows.append({
                    "date": sunday, "type": "Cycling",
                    "distance": _km(cfg, 18.0), "stamp": "km" if cfg.metric
                    else "mi", "dur": 55, "hr": 132, "rpe": 5,
                })
    return rows


def weight_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    monday = _monday(today)
    i = 0
    for week in range(10, -1, -1):
        week_start = monday - _dt.timedelta(days=7 * week)
        for offset in (0, 2, 4):
            day = week_start + _dt.timedelta(days=offset)
            if day > today:
                continue
            elapsed = (10 - week) + offset / 7.0
            value = 78.0 - 0.30 * elapsed + 0.35 * math.sin(i * 1.7)
            rows.append({"date": day,
                         "weight": _kg(cfg, round(value, 1)),
                         "stamp": "kg" if cfg.metric else "lb"})
            i += 1
    return rows


def measurement_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    monday = _monday(today)
    sites = [("neck", 36.5, 0.05), ("shoulders", 112.0, 0.10),
             ("chest", 96.0, 0.10), ("arms", 33.0, 0.05),
             ("forearms", 27.5, 0.0), ("waist", 88.0, 0.45),
             ("hips", 102.0, 0.25), ("thighs", 58.0, 0.15),
             ("calves", 38.0, 0.0)]
    for step, week in enumerate(range(10, -1, -2)):
        day = monday - _dt.timedelta(days=7 * week) + _dt.timedelta(days=6)
        if day > today:
            continue
        row = {"date": day,
               "stamp": "cm" if cfg.metric else "in"}
        for key, base, rate in sites:
            row[key] = _cm(cfg, round(base - rate * step, 1))
        rows.append(row)
    return rows


def meal_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    plan = [
        ("Breakfast", "Oats, rolled, dry", {}),
        ("Breakfast", "Greek yoghurt 0%", {}),
        ("Lunch", "Chicken breast, cooked", {}),
        ("Lunch", "White rice, cooked", {}),
        ("Dinner", "Salmon fillet, cooked", {}),
        ("Dinner", "Broccoli, steamed", {}),
        ("Snack", "Apple", {}),
        ("Snack", "Home soup, one bowl",
         {"cal_in": 320, "p_in": 18.0, "c_in": 30.0, "f_in": 12.0}),
    ]
    for back in range(13, -1, -1):
        day = today - _dt.timedelta(days=back)
        for meal, food, typed in plan:
            if meal == "Dinner" and back % 2 == 0 and food.startswith(
                    "Salmon"):
                continue
            if meal == "Dinner" and back % 2 == 1 and (
                    food.startswith("Salmon") or
                    food.startswith("Broccoli")):
                continue
            row = {"date": day, "meal": meal, "food": food}
            row.update(typed)
            rows.append(row)
    return rows


def water_rows(cfg: Config) -> List[Dict]:
    rows: List[Dict] = []
    today = cfg.today
    for back in range(13, -1, -1):
        day = today - _dt.timedelta(days=back)
        training = day.weekday() in (0, 1, 3, 5)
        rows.append({
            "date": day,
            "glasses": 6 + (back % 3),
            "ml": 500 if training else None,
            "bed": _dt.time(22, 30) if back % 3 else _dt.time(23, 0),
            "wake": _dt.time(6, 15) if back % 2 else _dt.time(6, 45),
            "quality": 3 + (back % 2),
            "mood": 3 + (back % 3) // 2,
            "energy": 4 if training else 3,
            "mobility": 10 if training else None,
        })
    return rows


def nsv_rows(cfg: Config) -> List[Dict]:
    t = cfg.today
    return [
        {"date": t - _dt.timedelta(days=30), "category": "Clothes",
         "victory": "The jeans zip without a battle.",
         "reward": "New belt, one size down"},
        {"date": t - _dt.timedelta(days=21), "category": "Energy",
         "victory": "The 3pm slump is gone on training weeks.",
         "reward": "Late walk instead of a nap"},
        {"date": t - _dt.timedelta(days=12), "category": "Lifts",
         "victory": "Five reps at a weight that used to be a one-rep "
                    "scrape.", "reward": "Log a proper PR row"},
        {"date": t - _dt.timedelta(days=4), "category": "Sleep",
         "victory": "Four nights this week over seven hours.",
         "reward": "Sunday morning, no alarm"},
    ]
