"""
Rotation - how often each meal repeats.

Nothing kills a meal plan faster than the same dinner three times in a
fortnight.  This tab reads the Meal Plan, works out how long it has been
since each recipe was last cooked, when it is allowed back in the plan and
which meals are the most overdue.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick a recipe from your recipe book."),
        Col("category", "Category", 15, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("category")) + ")"),
        Col("cuisine", "Cuisine", 14, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("cuisine")) + ")"),
        Col("times_planned", "Times cooked", 12, "calc", group="history",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Cooked")'
                    '+COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Eaten"))'),
        Col("last_planned", "Last cooked", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("last_planned")) + ")"),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    'TODAY()-{last_planned}{r})'),
        Col("avg_gap", "Average gap (days)", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{times_planned}{r}=0),"",'
                    'ROUND(365/{times_planned}{r},0))'),
        Col("rotation_ok", "Rotation", 10, "calc", group="rules",
            formula='=IF({recipe}{r}="","",'
                    'IF({days_since}{r}="","Yes",'
                    'IF({days_since}{r}>=Rotation_Gap_Days,"Yes","No")))'),
        Col("next_earliest", "Back in the plan", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    '{last_planned}{r}+Rotation_Gap_Days)'),
        Col("days_until_ok", "Days until", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{next_earliest}{r}=""),"",'
                    '{next_earliest}{r}-TODAY())'),
        Col("rotation_rank", "Overdue rank", 12, "calc", group="rankings",
            formula='=IF(OR({recipe}{r}="",{days_since}{r}=""),"",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '"<"&{days_since}{r})+1)'),
        Col("favourite", "Favourite", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("favourite"))
                    + ")"),
        Col("rating", "Rating", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("rating")) + ")"),
        Col("plan_flag", "Plan flag", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({rotation_ok}{r}="No","Too soon",'
                    'IF({days_since}{r}="","Never cooked",'
                    'IF({days_since}{r}>=90,"Overdue","Available"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Rotation",
        title="Rotation",
        subtitle="How often each meal repeats, so the plan never gets boring",
        columns=columns,
        rows=cfg.row_count("Rotation"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Meal Plan", "Weekly Planner", "Help"])
