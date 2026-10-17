"""
Sustainability - waste, packaging and how local your shopping is.

The spend, waste and habit columns are read from the other tabs, so this
page fills itself in.  Fill in the packaging and local shopping columns
yourself and the score at the end tells you how the month went.
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


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_month = lists("Grocery Spending", "month")
    gs_total = lists("Grocery Spending", "line_total")
    fw_month = lists("Food Waste", "month")
    fw_cost = lists("Food Waste", "cost")
    fw_qty = lists("Food Waste", "qty")
    mp_month = lists("Meal Plan", "month")
    mp_status = lists("Meal Plan", "status")

    columns = [
        Col("month", "Month", 12, "text", group="when",
            note="Type it as 'Jan 2026' to match the other tabs."),
        Col("groceries", "Grocery spend", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_month + ','
                    '{month}{r}))'),
        Col("waste_cost", "Waste cost", 11, "calc", group="waste",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_cost + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("waste_qty", "Waste quantity", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_qty + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("waste_share", "Waste as % of spend", 13, "calc",
            formula='=IF(OR({month}{r}="",{groceries}{r}="",'
                    '{groceries}{r}=0),"",'
                    'IFERROR({waste_cost}{r}/{groceries}{r},""))'),
        Col("waste_target", "Target", 10, "calc",
            formula='=IF({month}{r}="","",Waste_Reduction_Target)'),
        Col("waste_vs_target", "Vs target", 11, "calc",
            formula='=IF(OR({month}{r}="",{waste_share}{r}=""),"",'
                    '{waste_share}{r}-Waste_Reduction_Target)'),
        Col("home_cooked", "Home cooked meals", 12, "calc", group="habits",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Cooked")'
                    '+COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Eaten"))'),
        Col("takeaways", "Takeaways", 10, "calc",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Takeaway")'
                    '+COUNTIFS(' + mp_month + ',{month}{r},'
                    + mp_status + ',"Eating out"))'),
        Col("new_recipes", "New recipes tried", 12, "calc",
            formula='=IF({month}{r}="","",'
                    'COUNTIFS([[Recipes.added_on]],{month}{r}))'),
        Col("local_shops", "Local shops used", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60},
            group="your own numbers"),
        Col("bulk_buys", "Bulk / refill buys", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60}),
        Col("packaging_free", "Plastic free shops", 12, "number",
            validate={"type": "integer", "between": 0, "and": 60}),
        Col("own_grown", "Grown at home", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("score", "Green score", 11, "calc", group="score",
            formula='=IF({month}{r}="","",'
                    'IF({waste_share}{r}="",0,'
                    'MAX(0,100-({waste_share}{r}*1000)))'
                    '+{local_shops}{r}*2+{bulk_buys}{r}*2'
                    '+{packaging_free}{r}*2+{own_grown}{r})'),
        Col("status", "Status", 14, "calc",
            formula='=IF({month}{r}="","",'
                    'IF({waste_vs_target}{r}="","",'
                    'IF({waste_vs_target}{r}<=0,"On target",'
                    '"Over target")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Sustainability",
        title="Sustainability",
        subtitle="Waste, packaging and how local your shopping is",
        columns=columns,
        rows=24,
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Food Waste", "Grocery Spending", "Goals", "Reports",
        "Help"])
