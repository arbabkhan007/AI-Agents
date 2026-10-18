"""The Supplies register - stock on the shelf."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Supplies")
    samples = sd.SUPPLIES if cfg.include_sample_data else []

    columns = [
        Col("id", "Item ID", 11, "text",
            formula='IF({name}{r}="","",'
                    '"SP-"&TEXT(ROW()-4,"000"))'),
        Col("name", "Supply", 26, "text"),
        Col("category", "Category", 14, "center",
            validate={"type": "list", "source": [
                "Chemicals", "Paper", "Equipment", "PPE", "Laundry",
                "Tools", "Other"]}),
        Col("unit", "Unit", 10, "center",
            validate={"type": "list", "source": [
                "bottle", "liter", "gallon", "box", "pack", "each",
                "roll", "kg"]}),
        Col("supplier", "Supplier", 18, "text"),
        Col("cost_per_unit", "Cost / Unit", 12, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("qty_on_hand", "Qty On Hand", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("reorder_level", "Reorder Level", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("reorder_qty", "Reorder Qty", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("last_purchased", "Last Bought", 13, "date"),
        Col("days_left", "Days Left", 10, "decimal_locked",
            formula='IF({name}{r}="","",IFERROR(ROUND({qty_on_hand}{r}/'
                    '({used_month}{r}/30),0),""))',
            note="Rough days of stock left at this month's usage rate."),
        Col("used_month", "Used This Month", 12, "decimal_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Supply Usage.qty]],[[Supply Usage.supply]],'
                    '{name}{r},[[Supply Usage.date]],">="&'
                    'DATE(YEAR(TODAY()),MONTH(TODAY()),1)))'),
        Col("used_cost", "Used Cost (Month)", 13, "money_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Supply Usage.total_cost]],'
                    '[[Supply Usage.supply]],{name}{r},'
                    '[[Supply Usage.date]],">="&'
                    'DATE(YEAR(TODAY()),MONTH(TODAY()),1)))'),
        Col("stock_value", "Stock Value", 13, "money_locked",
            formula='IF({name}{r}="","",'
                    'ROUND({qty_on_hand}{r}*{cost_per_unit}{r},2))'),
        Col("flag", "Reorder?", 11, "text_locked",
            formula='IF({name}{r}="","",IF({qty_on_hand}{r}<='
                    '{reorder_level}{r},"REORDER","OK"))'),
        Col("notes", "Notes", 22, "text"),
    ]

    spec = SheetSpec(
        name="Supplies",
        title="Supplies & Stock",
        subtitle="What is on the shelf, what it cost, when to reorder. "
                 "Usage lands on the Supply Usage tab.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
    spec.col("flag").cf = [
        {"type": "text", "criteria": "containing", "value": "REORDER",
         "style": "warning"},
        {"type": "text", "criteria": "containing", "value": "OK",
         "style": "good"},
    ]
    return spec
