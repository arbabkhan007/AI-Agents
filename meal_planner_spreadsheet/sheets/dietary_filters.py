"""
Dietary Filters - allergies, intolerances and dietary needs.

One row per thing to avoid.  The three calculated columns show how far the
exclusion reaches: how many ingredients it matches, how many recipes use
one of them and how many planned meals are flagged.  Anything listed here
is checked automatically on the Recipe Ingredients and Meal Plan tabs.
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

SEVERITY = ["Avoid", "Caution", "Preference"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("filter_id", "Filter ID", 10, "text", group="what",
            note="Anything you like - 'DF-01' is a good pattern."),
        Col("member", "Applies to", 20, "text",
            note="Who the exclusion is for. Leave blank for the whole "
                 "household."),
        Col("exclude", "Avoid this", 24, "text",
            note="The ingredient name to look for. It is matched against "
                 "the Ingredients and Recipe Ingredients tabs."),
        Col("reason", "Reason", 22, "text"),
        Col("severity", "Severity", 12, "select",
            validate={"type": "list", "source": SEVERITY}),
        Col("active", "Active", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("matching_ingredients", "Ingredients matched", 13, "calc",
            group="reach",
            formula='=IF({exclude}{r}="","",'
                    'COUNTIFS([[Ingredients.ingredient]],{exclude}{r}))'),
        Col("recipes_affected", "Recipes affected", 13, "calc",
            formula='=IF({exclude}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{exclude}{r}))'),
        Col("plan_rows_flagged", "Plan rows flagged", 13, "calc",
            formula='=IF({exclude}{r}="","",'
                    'SUMPRODUCT((COUNTIFS('
                    '[[Recipe Ingredients.recipe]],[[Meal Plan.recipe]],'
                    '[[Recipe Ingredients.ingredient]],{exclude}{r})'
                    '>0)*1))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Dietary Filters",
        title="Dietary Filters",
        subtitle="Allergies, intolerances and dietary needs - checked "
                 "against every recipe and plan",
        columns=columns,
        rows=cfg.row_count("Dietary Filters"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Household", "Recipes", "Recipe Ingredients",
        "Meal Plan", "Help"])
