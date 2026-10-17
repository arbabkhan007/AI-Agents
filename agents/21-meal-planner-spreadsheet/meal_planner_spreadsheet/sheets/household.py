"""
Household - who you are cooking for.

One row per person.  The calorie and protein targets are pulled from
Settings and scaled by age, the dietary needs feed the Dietary Filters tab
and the servings column is what the planner multiplies recipes by.
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

YES_NO = ["Yes", "No"]
ROLES = ["Adult", "Teenager", "Child", "Toddler", "Baby", "Guest",
         "Carer", "Pet"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("member", "Household member", 22, "text", group="who",
            note="Name or initials - whatever you will recognise."),
        Col("role", "Role", 12, "select",
            validate={"type": "list", "source": ROLES}),
        Col("age", "Age", 7, "number",
            validate={"type": "integer", "between": 0, "and": 120}),
        Col("diet", "Dietary need", 16, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "diet")}),
        Col("allergies", "Allergies", 22, "text",
            note="Free text. Anything listed here is checked against the "
                 "Dietary Filters tab."),
        Col("dislikes", "Dislikes", 22, "text"),
        Col("calorie_target", "Calories / day", 12, "calc",
            group="targets",
            formula='=IF({member}{r}="","",IF({age}{r}="",Calorie_Target,'
                    'IF({age}{r}<4,Calorie_Target*0.4,'
                    'IF({age}{r}<9,Calorie_Target*0.6,'
                    'IF({age}{r}<14,Calorie_Target*0.8,'
                    'IF({age}{r}<19,Calorie_Target*0.95,Calorie_Target))))))'),
        Col("protein_target", "Protein / day (g)", 13, "calc",
            formula='=IF({member}{r}="","",IF({age}{r}="",Protein_Target,'
                    'IF({age}{r}<4,Protein_Target*0.5,'
                    'IF({age}{r}<9,Protein_Target*0.65,'
                    'IF({age}{r}<14,Protein_Target*0.8,'
                    'IF({age}{r}<19,Protein_Target*0.9,Protein_Target))))))'),
        Col("servings", "Servings", 10, "number", group="planning",
            validate={"type": "decimal", "between": 0, "and": 20},
            note="Portions this person takes from a shared meal."),
        Col("packed_lunch", "Packed lunch", 12, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("notes", "Notes", 34, "text_wrap"),
        Col("status", "Status", 12, "calc",
            formula='=IF({member}{r}="","",'
                    'IF({allergies}{r}<>"","Allergy noted","OK"))'),
    ]

    spec = SheetSpec(
        name="Household",
        title="Household",
        subtitle="Who you cook for, what they eat and what they need each day",
        columns=columns,
        rows=cfg.row_count("Household"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Settings", "Dietary Filters", "Meal Plan", "Help"])
