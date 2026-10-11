"""
Events - parties, holidays and dinner guests.

Give the event a date and a head count, pick the dishes you plan to cook
and the tab works out the cost per head, compares it with the budget and
counts down the days.  The prep tasks you need are counted straight from
the Meal Prep tab.
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

MEAL_TYPES = ["Breakfast", "Brunch", "Lunch", "Dinner", "BBQ", "Buffet",
              "Picnic", "Afternoon tea", "Drinks", "Other"]
STATUS = ["Planning", "Invited", "Shopping", "Ready", "Done", "Cancelled"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    menu_cols = [Col(f"menu_{i}", f"Dish {i}", 24, "select",
                     validate={"type": "list", "source": "=" + recipes},
                     group="menu")
                 for i in range(1, 5)]

    columns = [
        Col("event", "Event", 24, "text", group="what",
            note="Anything you like - 'Mum's birthday' is perfect."),
        Col("date", "Date", 12, "date"),
        Col("guests", "Guests", 9, "number",
            validate={"type": "integer", "between": 1, "and": 500}),
        Col("meal_type", "Meal", 13, "select",
            validate={"type": "list", "source": MEAL_TYPES}),
        Col("host", "Host", 16, "text"),
        Col("location", "Where", 22, "text"),
        Col("budget", "Budget", 12, "money", group="money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
    ] + menu_cols + [
        Col("dessert", "Dessert", 24, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("drinks", "Drinks", 22, "text"),
        Col("servings", "Servings each", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 20}),
        Col("menu_cost", "Menu cost", 12, "calc",
            formula='=IF({event}{r}="","",'
                    'IFERROR(' + lookup("{menu_1}{r}", recipes,
                                        rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_2}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_3}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{menu_4}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0)'
                    '+IFERROR(' + lookup("{dessert}{r}", recipes,
                                         rec("cost_per_serving"))
                    + '*{servings}{r}*{guests}{r},0))'),
        Col("cost_per_head", "Cost per head", 12, "calc",
            formula='=IF(OR({event}{r}="",{guests}{r}=0),"",'
                    'IFERROR({menu_cost}{r}/{guests}{r},""))'),
        Col("variance", "Vs budget", 11, "calc",
            formula='=IF(OR({event}{r}="",{budget}{r}=""),"",'
                    '{budget}{r}-{menu_cost}{r})'),
        Col("days_until", "Days to go", 11, "calc", group="planning",
            formula='=IF(OR({event}{r}="",{date}{r}=""),"",'
                    '{date}{r}-TODAY())'),
        Col("prep_tasks", "Prep tasks", 11, "calc",
            formula='=IF({event}{r}="","",'
                    'COUNTIFS([[Meal Prep.recipe]],{menu_1}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_2}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_3}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{menu_4}{r})'
                    '+COUNTIFS([[Meal Prep.recipe]],{dessert}{r}))'),
        Col("dietary_notes", "Dietary notes", 26, "text"),
        Col("leftover_plan", "Leftover plan", 26, "text",
            note="What happens to the food that is left over."),
        Col("status", "Status", 12, "select",
            validate={"type": "list", "source": STATUS}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Events",
        title="Events",
        subtitle="Parties, holidays and dinner guests - with a menu budget",
        columns=columns,
        rows=cfg.row_count("Events"),
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Meal Prep", "Grocery List", "Help"])
