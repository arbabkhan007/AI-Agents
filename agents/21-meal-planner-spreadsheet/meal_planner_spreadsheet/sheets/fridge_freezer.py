"""
Fridge & Freezer - batch cooked portions and their use-by dates.

Where the Meal Prep tab says what to cook, this tab says what is actually
in there.  Each batch gets a fridge use-by date, a freezer use-by date, a
value and a place in the queue, so a full freezer never turns into a bin
bag three weeks later.
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

STORAGE = ["Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    columns = [
        Col("batch_id", "Batch ID", 11, "text", group="what",
            note="Anything you like - 'FF-01' is a good pattern."),
        Col("item", "What it is", 26, "text"),
        Col("recipe", "From recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("portions", "Portions", 9, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("storage", "Storage", 10, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("cooked_date", "Cooked", 12, "date"),
        Col("use_by", "Use by", 12, "calc", group="dates",
            formula='=IF(OR({batch_id}{r}="",{cooked_date}{r}=""),"",'
                    'IF({storage}{r}="Freezer",'
                    '{cooked_date}{r}+Freezer_Review_Days,'
                    '{cooked_date}{r}+Leftover_Safe_Days))'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({batch_id}{r}="",{use_by}{r}=""),"",'
                    '{use_by}{r}-TODAY())'),
        Col("status", "Status", 14, "calc",
            formula='=IF({batch_id}{r}="","",'
                    'IF({eaten}{r}="Yes","Eaten",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Past its best",'
                    'IF({days_left}{r}<=1,"Eat today",'
                    'IF({days_left}{r}<=3,"Eat this week","Keep"))))))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({batch_id}{r}="",{portions}{r}=""),"",'
                    'IFERROR({portions}{r}*'
                    + lookup("{recipe}{r}", recipes,
                             lists("Recipes", "cost_per_serving"))
                    + ',""))'),
        Col("fridge_rank", "Fridge rank", 10, "calc", group="rankings",
            formula='=IF(OR({storage}{r}<>"Fridge",{days_left}{r}=""),"",'
                    'COUNTIFS({storage_first}:{storage_last},"Fridge",'
                    '{days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("freezer_rank", "Freezer rank", 11, "calc",
            formula='=IF(OR({storage}{r}<>"Freezer",{days_left}{r}=""),"",'
                    'COUNTIFS({storage_first}:{storage_last},"Freezer",'
                    '{days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("container", "Container", 16, "text", group="detail"),
        Col("reheats", "Reheats left", 11, "number",
            validate={"type": "integer", "between": 0, "and": 5}),
        Col("defrost_by", "Defrost by", 12, "calc",
            formula='=IF(OR({batch_id}{r}="",{use_by}{r}=""),"",'
                    '{use_by}{r}-1)'),
        Col("eaten", "Eaten", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Fridge & Freezer",
        title="Fridge & Freezer",
        subtitle="Batch cooked portions, with use-by dates and a queue",
        columns=columns,
        rows=cfg.row_count("Fridge & Freezer"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Meal Prep", "Leftovers", "Pantry", "Food Safety",
        "Help"])
