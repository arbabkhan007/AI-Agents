"""
Store Prices - the same item, priced at every shop.

Log a price whenever you notice one.  The tab converts every price to a
price per unit so packs of different sizes can be compared, flags the
cheapest offer for each item and shows how far the dearest shop is from
the best.
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
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab."),
        Col("store", "Store", 18, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "store")}),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "unit")}),
        Col("price", "Price", 11, "money", group="price",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_per_unit", "Price / unit", 11, "calc",
            formula='=IF(OR({price}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",{price}{r}/{pack_size}{r})'),
        Col("date", "Seen on", 12, "date"),
        Col("on_sale", "On offer", 9, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("usual_price", "Usual price", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("saving", "Saving", 11, "calc", group="offers",
            formula='=IF(OR({price}{r}="",{usual_price}{r}=""),"",'
                    '{usual_price}{r}-{price}{r})'),
        Col("saving_pct", "Saving %", 10, "calc",
            formula='=IF(OR({saving}{r}="",{usual_price}{r}="",'
                    '{usual_price}{r}=0),"",'
                    '{saving}{r}/{usual_price}{r})'),
        Col("best_price", "Best price", 11, "calc", group="comparison",
            formula='=IF({item}{r}="","",'
                    'IF(SUMPRODUCT(MIN((' + lists("Store Prices", "item")
                    + '={item}{r})*' + lists("Store Prices",
                                             "price_per_unit")
                    + '+(' + lists("Store Prices", "item")
                    + '<>{item}{r})*1000000))>=1000000,"",'
                    'SUMPRODUCT(MIN((' + lists("Store Prices", "item")
                    + '={item}{r})*'
                    + lists("Store Prices", "price_per_unit")
                    + '+(' + lists("Store Prices", "item")
                    + '<>{item}{r})*1000000))))'),
        Col("vs_best", "Vs best", 10, "calc",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}="",'
                    '{best_price}{r}=""),"",'
                    '{price_per_unit}{r}-{best_price}{r})'),
        Col("best_flag", "Best buy", 10, "calc",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}=""),"",'
                    'IF({price_per_unit}{r}={best_price}{r},"Best",""))'),
        Col("rank", "Price rank", 10, "calc", group="rankings",
            formula='=IF(OR({item}{r}="",{price_per_unit}{r}=""),"",'
                    'COUNTIFS(' + lists("Store Prices", "item") + ','
                    '{item}{r},' + lists("Store Prices",
                                         "price_per_unit") + ','
                    '"<"&{price_per_unit}{r})+1)'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Store Prices",
        title="Store Prices",
        subtitle="The same item, priced at every shop",
        columns=columns,
        rows=cfg.row_count("Store Prices"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Ingredients", "Stores", "Grocery Spending", "Help"])
