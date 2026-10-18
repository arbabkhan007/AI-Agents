"""The Services register - the price list."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Services")
    samples = sd.SERVICES if cfg.include_sample_data else []

    columns = [
        Col("id", "Service ID", 11, "text",
            formula='IF({name}{r}="","",'
                    f'"SV-"&TEXT(ROW()-{4},"000"))'),
        Col("name", "Service", 26, "text",
            note="Used in the quote calculator and job sheets."),
        Col("category", "Category", 15, "center",
            validate={"type": "list", "source": [
                "Residential", "Commercial", "Deep clean", "Specialist",
                "Add-on"]}),
        Col("description", "What Is Included", 36, "text"),
        Col("unit", "Priced By", 12, "center",
            validate={"type": "list", "source": [
                "hour", f"{cfg.area_unit}", "room", "bedroom",
                "bathroom", "visit", "fixed"]},
            note="Drives the quote calculator's maths."),
        Col("base_price", "Standard Price", 13, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("est_hours", "Est. Hours", 10, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 400}),
        Col("materials", "Materials Cost", 12, "money"),
        Col("frequency", "Default Frequency", 15, "center",
            validate={"type": "list", "source": [
                "One-off", "Weekly", "Fortnightly", "Every 3 weeks",
                "Monthly", "Quarterly", "Twice a week"]}),
        Col("active", "Active", 9, "center",
            validate={"type": "list", "source": ["Yes", "No"]}),
        Col("times_used", "Times Quoted", 11, "int_locked",
            formula='IF({name}{r}="","",'
                    'COUNTIF([[Quote Lines.service]],{name}{r}))'),
        Col("quoted_value", "Quoted Value", 13, "money_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Quote Lines.line_total]],'
                    '[[Quote Lines.service]],{name}{r}))'),
        Col("price_per_hour", "Price / Hour", 12, "money_locked",
            formula='IF(OR({name}{r}="",{est_hours}{r}<=0),"",'
                    '{base_price}{r}/{est_hours}{r})',
            note="Sanity check: should land above your cost per hour "
                 f"({cfg.currency_symbol}{cfg.cost_per_hour:,.2f})."),
    ]

    return SheetSpec(
        name="Services",
        title="Services & Price List",
        subtitle="What you sell, what it costs, how it is priced. The "
                 "quote calculator reads this list.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
