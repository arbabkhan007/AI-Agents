"""
check_meal_sample.py - does the sample data hang together?

Checks that every recipe ingredient exists on the Ingredients list, that
the planned meals cover 107 rows, that the grocery spending covers every
month of the planning year and that the household matches the config.
Run it after any change to sample_data.py.

Usage:
    python tools/check_meal_sample.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from meal_planner_spreadsheet.config import Config  # noqa: E402
from meal_planner_spreadsheet.sample_data import (  # noqa: E402
    INGREDIENTS, RECIPES, RECIPE_INGREDIENTS, build_samples,
)

problems = 0


def fail(msg: str) -> None:
    global problems
    problems += 1
    print(f"FAIL: {msg}")


def ok(msg: str) -> None:
    print(f"  ok: {msg}")


def main() -> int:
    cfg = Config()
    s = build_samples(cfg)

    names = {row[0] for row in INGREDIENTS}
    recipe_names = {row[0] for row in RECIPES}

    if len(INGREDIENTS) != 62:
        fail(f"expected 62 ingredients, found {len(INGREDIENTS)}")
    else:
        ok("62 ingredients")

    if len(RECIPES) != 38:
        fail(f"expected 38 recipes, found {len(RECIPES)}")
    else:
        ok("38 recipes")

    plan_rows = s["Meal Plan"]
    if len(plan_rows) != 107:
        fail(f"expected 107 planned meals, found {len(plan_rows)}")
    else:
        ok("107 planned meals")

    if len(s["Recipe Ingredients"]) < 160:
        fail(f"expected >= 160 recipe ingredient rows, found "
             f"{len(s['Recipe Ingredients'])}")
    else:
        ok(f"{len(s['Recipe Ingredients'])} recipe ingredient rows")

    for row in RECIPE_INGREDIENTS:
        recipe, ingredient = row[0], row[1]
        if ingredient not in names:
            fail(f"recipe ingredient not in Ingredients: {ingredient!r} "
                 f"(recipe {recipe!r})")
        if recipe not in recipe_names:
            fail(f"recipe not in Recipes: {recipe!r}")

    for rec in plan_rows.values():
        if rec["recipe"] not in recipe_names:
            fail(f"planned meal uses unknown recipe: {rec['recipe']!r}")

    for rec in s["Staples"].values():
        if rec["staple"] not in names:
            fail(f"staple not in Ingredients: {rec['staple']!r}")

    for rec in s["Pantry"].values():
        if rec["item"] not in names:
            fail(f"pantry item not in Ingredients: {rec['item']!r}")

    for rec in s["Leftovers"].values():
        if rec["recipe"] not in recipe_names:
            fail(f"leftover from unknown recipe: {rec['recipe']!r}")

    for rec in s["Food Waste"].values():
        if rec["item"] not in names:
            fail(f"waste item not in Ingredients: {rec['item']!r}")

    for rec in s["Nutrition"].values():
        if rec["recipe"] not in recipe_names:
            fail(f"nutrition row uses unknown recipe: {rec['recipe']!r}")

    for rec in s["Grocery List"].values():
        if rec["item"] not in names:
            fail(f"grocery item not in Ingredients: {rec['item']!r}")

    for rec in s["Grocery Spending"].values():
        if rec["item"] not in names:
            fail(f"spending item not in Ingredients: {rec['item']!r}")

    # every month on the Budget tab must have spending behind it
    months = {rec["date"].strftime("%b %Y")
              for rec in s["Grocery Spending"].values()}
    budget_months = {rec["month"] for rec in s["Budget"].values()}
    missing = budget_months - months
    if missing:
        fail(f"grocery spending missing Budget months: {sorted(missing)}")
    else:
        ok(f"grocery spending covers all {len(budget_months)} Budget months")
    if len(months) < 6:
        fail(f"expected spending across >= 6 months, found {len(months)}")
    else:
        ok(f"spending across {len(months)} months: {sorted(months)}")

    household = s["Household"]
    if len(household) != 4:
        fail(f"expected a household of 4, found {len(household)}")
    else:
        ok("household of 4")

    total_spend = sum(rec.get("price", 0) * rec.get("qty", 0)
                      for rec in s["Grocery Spending"].values())
    print(f"  info: sample grocery spend total = {total_spend:,.2f}")
    print(f"  info: meal plan rows by status = "
          f"{sorted({r['status'] for r in plan_rows.values()})}")

    if problems == 0:
        print("\nPASS: sample data hangs together")
        return 0
    print(f"\n{problems} problem(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
