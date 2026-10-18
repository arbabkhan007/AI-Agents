"""Quote Lines - the priced detail behind each quote."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Quote Lines")
    samples = sd.QUOTE_LINES if cfg.include_sample_data else []
    cost_per_hour = cfg.cost_per_hour

    columns = [
        Col("id", "Line ID", 11, "text",
            formula='IF({quote_ref}{r}="","",'
                    '"QL-"&TEXT(ROW()-4,"0000"))'),
        Col("quote_ref", "Quote #", 14, "text",
            validate={"type": "list", "source": "=Quotes_Numbers",
                      "ignore_blank": True},
            note="Must match a Quote # on the Quotes tab."),
        Col("line_no", "Line", 7, "int"),
        Col("room_area", "Room / Area", 16, "text",
            validate={"type": "list", "source": [
                "Whole property", "Kitchen", "Bathrooms", "Bedrooms",
                "Living areas", "Hall & stairs", "Windows", "Floors",
                "Oven", "Fridge", "Carpet", "Upholstery", "Exterior",
                "Office area", "Communal areas", "Other"]}),
        Col("service", "Service", 22, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True}),
        Col("description", "Description", 34, "text"),
        Col("qty", "Qty", 8, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("unit", "Unit", 11, "center",
            validate={"type": "list", "source": [
                "hour", f"{cfg.area_unit}", "room", "bedroom",
                "bathroom", "visit", "fixed", "item"]}),
        Col("unit_price", "Unit Price", 12, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000}),
        Col("hours", "Hours", 9, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 400},
            note="Your labour hours for this line."),
        Col("materials", "Materials", 12, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("line_total", "Line Total", 13, "money_locked",
            formula='IF({quote_ref}{r}="","",'
                    'ROUND({qty}{r}*{unit_price}{r}+{materials}{r},2))'),
        Col("line_cost", "Line Cost", 13, "money_locked",
            formula='IF({quote_ref}{r}="","",'
                    'ROUND({hours}{r}*' + str(cost_per_hour) +
                    '+{materials}{r},2))',
            note=f"Hours at {cfg.currency_symbol}{cost_per_hour:,.2f} "
                 "fully loaded plus materials."),
        Col("line_profit", "Line Profit", 13, "money_locked",
            formula='IF({quote_ref}{r}="","",'
                    '{line_total}{r}-{line_cost}{r})'),
        Col("line_margin", "Margin %", 11, "pct_locked",
            formula='IF(OR({quote_ref}{r}="",{line_total}{r}=0),"",'
                    '{line_profit}{r}/{line_total}{r})'),
        Col("match_key", "Match Key", 12, "text_locked",
            formula='IF({quote_ref}{r}="","",'
                    '{quote_ref}{r}&"-"&{line_no}{r})',
            hidden=True,
            note="Helper for the printable quote. Leave hidden."),
    ]

    return SheetSpec(
        name="Quote Lines",
        title="Quote Lines",
        subtitle="One row per line of a quote. The Quotes tab totals these "
                 "by Quote #, so the same quote number can have as many "
                 "lines as you need.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
