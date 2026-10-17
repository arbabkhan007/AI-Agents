"""
Leftovers - the queue of cooked food waiting to be eaten.

Batch cooking only pays off if the portions get eaten.  Log each batch, say
whether it is in the fridge or the freezer and the sheet works out both
expiry dates, the days left and the order to eat them in.  The queue rank
always puts the most urgent portion first.
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
        Col("leftover_id", "Batch ID", 11, "text", group="what",
            note="Anything you like - 'LO-01' is a good pattern."),
        Col("item", "What it is", 26, "text"),
        Col("recipe", "From recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("cooked_date", "Cooked", 12, "date"),
        Col("portions", "Portions", 9, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("storage", "Storage", 10, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("fridge_expiry", "Fridge use by", 12, "calc", group="dates",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    '{cooked_date}{r}+Leftover_Safe_Days)'),
        Col("freezer_expiry", "Freezer use by", 12, "calc",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    '{cooked_date}{r}+Freezer_Review_Days)'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({leftover_id}{r}="",{cooked_date}{r}=""),"",'
                    'IF({storage}{r}="Freezer",'
                    '{freezer_expiry}{r}-TODAY(),'
                    '{fridge_expiry}{r}-TODAY()))'),
        Col("status", "Status", 14, "calc",
            formula='=IF({leftover_id}{r}="","",'
                    'IF({thrown}{r}="Yes","Binned",'
                    'IF({used_up}{r}="Yes","Eaten",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Past its best",'
                    'IF({days_left}{r}<=1,"Eat today",'
                    'IF({days_left}{r}<=3,"Eat this week",'
                    '"Keep")))))))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({leftover_id}{r}="",{portions}{r}=""),"",'
                    'IFERROR({portions}{r}*'
                    + lookup("{recipe}{r}", recipes,
                             lists("Recipes", "cost_per_serving"))
                    + ',""))'),
        Col("queue_rank", "Queue rank", 10, "calc", group="rankings",
            formula='=IF(OR({leftover_id}{r}="",{days_left}{r}=""),"",'
                    'COUNTIFS({days_left_first}:{days_left_last},'
                    '"<"&{days_left}{r})+1)'),
        Col("use_by_flag", "Flag", 12, "calc",
            formula='=IF({leftover_id}{r}="","",'
                    'IF({days_left}{r}="","",'
                    'IF({days_left}{r}<0,"Bin it",'
                    'IF({days_left}{r}<=Expiry_Warning_Days,'
                    '"Use it or lose it",""))))'),
        Col("portions_left", "Portions left", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("used_up", "Eaten up", 10, "select", group="tracking",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("thrown", "Binned", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("container", "Container", 14, "text"),
        Col("reheats", "Reheats left", 11, "number",
            validate={"type": "integer", "between": 0, "and": 5}),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Leftovers",
        title="Leftovers",
        subtitle="Batch cooked portions and when to eat them",
        columns=columns,
        rows=cfg.row_count("Leftovers"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Fridge & Freezer", "Meal Prep", "Food Waste",
        "Pantry", "Help"])
