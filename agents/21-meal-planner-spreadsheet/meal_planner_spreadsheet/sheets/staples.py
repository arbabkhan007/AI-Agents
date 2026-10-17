"""
Staples - the things you buy every single week.

Add your bread, milk, eggs, coffee and pasta here with how often you buy
them.  When a staple is due, or the pantry drops below a week of cover, it
is flagged so it never gets forgotten on the grocery list.
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

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("staple", "Staple", 24, "text", group="what",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({staple}{r}="","",'
                    + lookup("{staple}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("usual_unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("usual_qty", "Usual quantity", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100000},
            note="How much you buy each time."),
        Col("last_bought", "Last bought", 12, "date", group="rhythm"),
        Col("buy_interval_days", "Buy every (days)", 12, "number",
            validate={"type": "integer", "between": 1, "and": 365}),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({staple}{r}="",{last_bought}{r}=""),"",'
                    'TODAY()-{last_bought}{r})'),
        Col("due", "Due", 9, "calc",
            formula='=IF(OR({staple}{r}="",{days_since}{r}="",'
                    '{buy_interval_days}{r}=""),"",'
                    'IF({days_since}{r}>={buy_interval_days}{r},"Yes",'
                    '"No"))'),
        Col("auto_add", "Auto add", 10, "select", group="behaviour",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")},
            note="Yes = this staple is added to the grocery list whenever "
                 "it is due."),
        Col("qty_to_add", "Quantity to add", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("avg_price", "Average price", 12, "calc", group="prices",
            formula='=IF({staple}{r}="","",'
                    'IFERROR(AVERAGEIFS([[Grocery Spending.price]],'
                    '[[Grocery Spending.item]],{staple}{r}),""))'),
        Col("last_price", "Last price", 11, "calc",
            formula='=IF({staple}{r}="","",'
                    'IFERROR(AVERAGEIFS([[Grocery Spending.price]],'
                    '[[Grocery Spending.item]],{staple}{r},'
                    '[[Grocery Spending.date]],'
                    'SUMPRODUCT(MAX(([[Grocery Spending.item]]='
                    '{staple}{r})*[[Grocery Spending.date]]))),""))'),
        Col("price_delta", "Vs average", 11, "calc",
            formula='=IF(OR({staple}{r}="",{last_price}{r}="",'
                    '{avg_price}{r}=""),"",{last_price}{r}-{avg_price}{r})'),
        Col("pantry_qty", "In pantry", 10, "calc", group="stock",
            formula='=IF({staple}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{staple}{r}))'),
        Col("on_list", "On list", 9, "calc",
            formula='=IF({staple}{r}="","",'
                    'COUNTIFS([[Grocery List.item]],{staple}{r}))'),
        Col("rank", "Urgency rank", 12, "calc", group="rankings",
            formula='=IF(OR({staple}{r}="",{days_since}{r}=""),"",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '">"&{days_since}{r})+1)'),
        Col("status", "Status", 14, "calc",
            formula='=IF({staple}{r}="","",'
                    'IF({due}{r}="Yes","Buy this week",'
                    'IF({pantry_qty}{r}<=0,"Out of stock","In stock")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Staples",
        title="Staples",
        subtitle="The weekly basics, with a buy-by rhythm so nothing gets "
                 "forgotten",
        columns=columns,
        rows=cfg.row_count("Staples"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Grocery List", "Ingredients", "Help"])
