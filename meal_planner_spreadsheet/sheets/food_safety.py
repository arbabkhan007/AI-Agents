"""
Food Safety - how long food keeps, and at what temperature.

A ready made reference for the foods you cook most: fridge life, freezer
life, how long cooked food keeps and the safe storage and reheating
temperatures.  Edit the numbers to match your own kitchen and the pantry
and leftover tabs will follow.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
CATEGORIES = ["Meat", "Fish", "Dairy", "Eggs", "Vegetables", "Fruit",
              "Grains", "Cooked food", "Leftovers", "Condiments",
              "Baking", "Drinks"]

ROWS = [
    ("Raw chicken", "Meat", "Fridge", 2, 270, 3, 4, 75),
    ("Raw beef / mince", "Meat", "Fridge", 2, 120, 3, 4, 75),
    ("Raw pork", "Meat", "Fridge", 3, 180, 3, 4, 75),
    ("Cooked chicken", "Cooked food", "Fridge", 3, 90, 3, 4, 75),
    ("Cooked mince / bolognese", "Cooked food", "Fridge", 3, 90, 3, 4, 75),
    ("Sausages", "Meat", "Fridge", 3, 60, 3, 4, 75),
    ("Bacon", "Meat", "Fridge", 7, 60, 3, 4, 75),
    ("White fish", "Fish", "Fridge", 1, 90, 2, 2, 63),
    ("Oily fish", "Fish", "Fridge", 1, 60, 2, 2, 63),
    ("Cooked fish", "Cooked food", "Fridge", 2, 60, 2, 2, 63),
    ("Prawns", "Fish", "Fridge", 1, 90, 2, 2, 63),
    ("Milk (opened)", "Dairy", "Fridge", 5, 30, 0, 5, 72),
    ("Cheese (hard)", "Dairy", "Fridge", 21, 60, 0, 5, 72),
    ("Cheese (soft)", "Dairy", "Fridge", 7, 30, 0, 5, 72),
    ("Butter", "Dairy", "Fridge", 60, 90, 0, 5, 72),
    ("Yoghurt (opened)", "Dairy", "Fridge", 5, 30, 0, 5, 72),
    ("Eggs", "Eggs", "Fridge", 21, 0, 0, 5, 72),
    ("Cooked rice", "Cooked food", "Fridge", 1, 30, 1, 5, 75),
    ("Cooked pasta", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Cooked potatoes", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Soup / stew", "Cooked food", "Fridge", 3, 90, 3, 5, 75),
    ("Curry", "Cooked food", "Fridge", 3, 90, 3, 5, 75),
    ("Salad leaves", "Vegetables", "Fridge", 3, 0, 0, 5, 0),
    ("Chopped veg", "Vegetables", "Fridge", 3, 120, 0, 5, 0),
    ("Tomatoes", "Fruit", "Cupboard", 7, 60, 0, 12, 0),
    ("Bananas", "Fruit", "Cupboard", 5, 60, 0, 12, 0),
    ("Apples", "Fruit", "Fridge", 30, 0, 0, 5, 0),
    ("Berries", "Fruit", "Fridge", 3, 180, 0, 5, 0),
    ("Bread", "Baking", "Cupboard", 4, 90, 0, 20, 0),
    ("Cooked meat (sliced)", "Cooked food", "Fridge", 3, 60, 3, 5, 75),
    ("Gravy", "Condiments", "Fridge", 2, 90, 2, 5, 75),
    ("Pesto (opened)", "Condiments", "Fridge", 14, 60, 0, 5, 0),
    ("Ketchup (opened)", "Condiments", "Cupboard", 60, 0, 0, 20, 0),
    ("Tinned food (opened)", "Condiments", "Fridge", 3, 0, 0, 5, 0),
    ("Leftover pizza", "Leftovers", "Fridge", 3, 60, 3, 5, 75),
    ("Batch cooked chilli", "Cooked food", "Fridge", 3, 120, 3, 5, 75),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    columns = [
        Col("food", "Food", 26, "text", group="what"),
        Col("category", "Category", 14, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("storage", "Store in", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("fridge_days", "Fridge (days)", 11, "number", group="times",
            validate={"type": "integer", "between": 0, "and": 3650}),
        Col("freezer_days", "Freezer (days)", 12, "number",
            validate={"type": "integer", "between": 0, "and": 3650}),
        Col("cooked_days", "Once cooked (days)", 13, "number",
            validate={"type": "integer", "between": 0, "and": 365}),
        Col("safe_temp", "Fridge temp (C)", 12, "number", group="safety",
            validate={"type": "integer", "between": -20, "and": 20}),
        Col("reheat_temp", "Reheat to (C)", 12, "number",
            validate={"type": "integer", "between": 40, "and": 120}),
        Col("source", "Source", 18, "text"),
        Col("status", "Status", 14, "calc",
            formula='=IF({food}{r}="","",'
                    'IF({freezer_days}{r}>0,"Freezable","Fridge only"))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Food Safety",
        title="Food Safety",
        subtitle="How long food keeps, and the temperatures that keep it safe",
        columns=columns,
        rows=cfg.row_count("Food Safety"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec, sample_index=writer.samples.get("Food Safety"))
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Leftovers", "Fridge & Freezer", "Help"],
                        banding=True)
