"""
Grocery Spending - every shop you record, against the budget.

Record what you actually spent and the tab works out the week and the
month, compares each week with the weekly budget and keeps a running total
for the month.  This is the tab the Budget and Reports tabs read.
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

PAYMENT = ["Cash", "Debit card", "Credit card", "Phone", "Voucher",
           "Gift card", "Account"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("date", "Date", 12, "date", group="when"),
        Col("week_start", "Week starting", 12, "calc",
            formula='=IF({date}{r}="","",'
                    '{date}{r}-WEEKDAY({date}{r},2)+1)'),
        Col("month", "Month", 11, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("store", "Store", 18, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "store")}),
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("qty", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "unit")}),
        Col("price", "Price / unit", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("line_total", "Line total", 11, "calc", group="money",
            formula='=IF(OR({item}{r}="",{qty}{r}="",{price}{r}=""),"",'
                    '{qty}{r}*{price}{r})'),
        Col("week_spend", "Week spend", 11, "calc",
            formula='=IF(OR({date}{r}="",{line_total}{r}=""),"",'
                    'SUMIFS({line_total_first}:{line_total_last},'
                    '{week_start_first}:{week_start_last},'
                    '{week_start}{r}))'),
        Col("share_of_week", "Share of week", 12, "calc",
            formula='=IF(OR({line_total}{r}="",{week_spend}{r}="",'
                    '{week_spend}{r}=0),"",'
                    '{line_total}{r}/{week_spend}{r})'),
        Col("vs_budget", "Week vs budget", 12, "calc",
            formula='=IF({week_spend}{r}="","",'
                    '{week_spend}{r}-Weekly_Budget)'),
        Col("budget_flag", "Budget flag", 12, "calc",
            formula='=IF({week_spend}{r}="","",'
                    'IF({week_spend}{r}>Weekly_Budget,"Over budget",'
                    'IF({week_spend}{r}>Weekly_Budget*0.9,"Close",'
                    '"Within budget")))'),
        Col("receipt_no", "Receipt", 12, "text", group="detail"),
        Col("payment", "Paid by", 13, "select",
            validate={"type": "list", "source": PAYMENT}),
        Col("on_sale", "On offer", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("savings", "Saving", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({line_total}{r}="","",'
                    'COUNTIFS({line_total_first}:{line_total_last},'
                    '">"&{line_total}{r})+1)'),
        Col("month_running", "Month running total", 13, "calc",
            formula='=IF(OR({date}{r}="",{line_total}{r}=""),"",'
                    'SUMIFS({line_total_first}:{line_total_last},'
                    '{month_first}:{month_last},{month}{r},'
                    '{date_first}:{date_last},"<="&{date}{r}))'),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({on_sale}{r}="Yes","On offer","Full price"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Grocery Spending",
        title="Grocery Spending",
        subtitle="Every shop you record, week by week, against the budget",
        columns=columns,
        rows=cfg.row_count("Grocery Spending"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Budget", "Reports", "Ingredients", "Store Prices",
        "Stores", "Help"])
