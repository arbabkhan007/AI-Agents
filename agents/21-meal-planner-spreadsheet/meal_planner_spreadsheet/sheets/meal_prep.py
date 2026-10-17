"""
Meal Prep - batch cooking tasks and what to do when.

List the jobs for your prep day, how long each takes and the order to do
them in.  The urgency column counts down to the day the batch is needed and
the todo rank puts the most pressing task at the top of the list.
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

YES_NO = ["Yes", "No"]
STATUS = ["To do", "In progress", "Done", "Skipped"]
EQUIPMENT = ["Oven", "Hob", "Slow cooker", "Air fryer", "Grill",
             "Food processor", "Blender", "Microwave", "No cooking"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    columns = [
        Col("task_id", "Task ID", 10, "text", group="what",
            note="Anything you like - 'P-01' is a good pattern."),
        Col("prep_day", "Prep day", 12, "select",
            validate={"type": "list",
                      "source": ["Monday", "Tuesday", "Wednesday",
                                 "Thursday", "Friday", "Saturday",
                                 "Sunday"]}),
        Col("task", "Task", 30, "text"),
        Col("recipe", "Recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("duration_min", "Minutes", 9, "number", group="effort",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("order", "Order", 8, "number",
            validate={"type": "integer", "between": 1, "and": 99},
            note="The order to do the tasks in."),
        Col("due_date", "Needed by", 12, "date"),
        Col("days_until", "Days until", 10, "calc", group="urgency",
            formula='=IF(OR({task_id}{r}="",{due_date}{r}=""),"",'
                    '{due_date}{r}-TODAY())'),
        Col("urgency", "Urgency", 13, "calc",
            formula='=IF({task_id}{r}="","",'
                    'IF({completed}{r}="Yes","Done",'
                    'IF({days_until}{r}="","No date",'
                    'IF({days_until}{r}<0,"Overdue",'
                    'IF({days_until}{r}<=Prep_Reminder_Days,"This week",'
                    '"Later")))))'),
        Col("todo_rank", "Todo rank", 10, "calc", group="rankings",
            formula='=IF(OR({task_id}{r}="",{days_until}{r}=""),"",'
                    'COUNTIFS({days_until_first}:{days_until_last},'
                    '"<"&{days_until}{r})+1)'),
        Col("assigned_to", "Who", 16, "text", group="detail"),
        Col("equipment", "Equipment", 15, "select",
            validate={"type": "list", "source": EQUIPMENT}),
        Col("batch_qty", "Batch size", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("portions", "Portions", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("fridge_until", "Fridge until", 12, "calc",
            formula='=IF(OR({task_id}{r}="",{completed_date}{r}=""),"",'
                    '{completed_date}{r}+Leftover_Safe_Days)'),
        Col("freezer_until", "Freezer until", 12, "calc",
            formula='=IF(OR({task_id}{r}="",{completed_date}{r}=""),"",'
                    '{completed_date}{r}+Freezer_Review_Days)'),
        Col("linked_slot", "For meal slot", 14, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "meal_slot")}),
        Col("calories", "Calories", 10, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        lists("Recipes", "calories"))
                    + '*{servings}{r},""))'),
        Col("cost", "Cost", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=""),"",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        lists("Recipes",
                                              "cost_per_serving"))
                    + '*{servings}{r},""))'),
        Col("completed", "Done", 9, "select", group="tracking",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("completed_date", "Completed on", 12, "date"),
        Col("status", "Status", 12, "select",
            validate={"type": "list", "source": STATUS}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Meal Prep",
        title="Meal Prep",
        subtitle="Batch cooking tasks, in the order to do them",
        columns=columns,
        rows=cfg.row_count("Meal Prep"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Leftovers", "Fridge & Freezer", "Recipes",
        "Print Week", "Help"])
