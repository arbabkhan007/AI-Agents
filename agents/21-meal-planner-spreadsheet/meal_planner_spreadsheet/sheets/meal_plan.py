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
