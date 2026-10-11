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
