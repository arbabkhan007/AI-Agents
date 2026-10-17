"""
Grocery List - the shopping list that writes itself.

Every planned meal is copied here by the Meal Plan tab, the quantities are
scaled to the household and reduced by what is already in the pantry, and
the list is grouped by aisle with a priority, a pack count and a running
total.  Tick items off as you fill the basket and the bought price is
compared with the planned price.

The last rows are the weekly staples: anything flagged as a staple on the
Ingredients tab is re-added automatically when stock runs low.
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


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("item", "Item", 26, "text", group="what",
            note="Must match an ingredient name on the Ingredients tab."),
        Col("category", "Aisle / category", 17, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("aisle", "Aisle", 16, "text",
            note="Your shop's aisle, so the printed list walks the store "
                 "in order."),
        Col("price", "Price / unit", 11, "calc", group="money",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("line_total", "Line total", 11, "calc",
            formula='=IF(OR({item}{r}="",{quantity}{r}="",'
                    '{price}{r}=""),"",{quantity}{r}*{price}{r})'),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("packs", "Packs", 9, "calc",
            formula='=IF(OR({quantity}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",CEILING({quantity}{r}/'
                    '{pack_size}{r},1))'),
        Col("pack_total", "Pack total", 11, "calc",
            formula='=IF(OR({packs}{r}="",{pack_size}{r}="",'
                    '{price}{r}=""),"",{packs}{r}*{pack_size}{r}*'
                    '{price}{r})'),
        Col("in_pantry", "In pantry", 10, "calc", group="stock",
            formula='=IF({item}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{item}{r}))'),
        Col("needed", "Still needed", 11, "calc",
            formula='=IF(OR({item}{r}="",{quantity}{r}=""),"",'
                    'MAX(0,{quantity}{r}-{in_pantry}{r}))'),
        Col("buy", "Buy", 8, "select", group="shopping",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bought", "Bought", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bought_date", "Bought on", 12, "date"),
        Col("bought_price", "Price paid", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_diff", "Vs planned", 11, "calc",
            formula='=IF(OR({bought_price}{r}="",{line_total}{r}=""),"",'
                    '{bought_price}{r}-{line_total}{r})'),
        Col("need_rank", "Need rank", 10, "calc", group="rankings",
            formula='=IF({needed}{r}="","",'
                    'COUNTIFS({needed_first}:{needed_last},'
                    '">"&{needed}{r})+1)'),
        Col("sort_key", "Sort key", 9, "calc",
            formula='=IF({line_total}{r}="","",'
                    '{line_total}{r}+ROW()/1000000)'),
        Col("buy_rank", "Buy rank", 10, "calc",
            formula='=IF(OR({buy}{r}<>"Yes",{sort_key}{r}=""),"",'
                    'COUNTIFS({buy_first}:{buy_last},"Yes",'
                    '{sort_key_first}:{sort_key_last},'
                    '"<"&{sort_key}{r})+1)'),
        Col("priority", "Priority", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({bought}{r}="Yes","Bought",'
                    'IF({needed}{r}<=0,"Have it",'
                    'IF({buy}{r}<>"Yes","Skip",'
                    'IF({need_rank}{r}<=10,"Must have","Nice to have")))))'),
        Col("week_start", "Week starting", 12, "date",
            note="Which week this line belongs to."),
        Col("linked_recipe", "From recipe", 22, "calc",
            formula='=IF({item}{r}="","",'
                    'IFERROR(INDEX([[Recipe Ingredients.recipe]],'
                    'MATCH({item}{r},'
                    '[[Recipe Ingredients.ingredient]],0)),""))'),
        Col("staple_flag", "Staple", 9, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("staple")) + ")"),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({bought}{r}="Yes","Bought",'
                    'IF({buy}{r}="Yes","To buy","Not needed")))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Grocery List",
        title="Grocery List",
        subtitle="The automatic shopping list - grouped by aisle, priced, "
                 "and reduced by what you already have",
        columns=columns,
        rows=cfg.row_count("Grocery List"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Meal Plan", "Weekly Planner", "Pantry", "Staples",
        "Print Shopping", "Grocery Spending", "Help"])
