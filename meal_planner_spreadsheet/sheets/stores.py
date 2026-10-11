"""
Stores - where you shop.

One row per shop with the practical details you actually need: whether they
deliver, the minimum order, what they are best for and how much you have
spent there.  The spend columns are read from the Grocery Spending tab, so
they fill themselves in as you record shops.
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
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday", "n/a"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_store = lists("Grocery Spending", "store")
    gs_total = lists("Grocery Spending", "line_total")

    columns = [
        Col("store", "Store", 22, "text", group="who"),
        Col("address", "Address", 30, "text"),
        Col("phone", "Phone", 16, "text"),
        Col("website", "Website", 22, "text"),
        Col("loyalty", "Loyalty scheme", 18, "text", group="details"),
        Col("delivery", "Delivers", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("pickup", "Click & collect", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("min_order", "Minimum order", 12, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("delivery_fee", "Delivery fee", 12, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("delivery_day", "Delivery day", 13, "select",
            validate={"type": "list", "source": DAYS}),
        Col("opening_hours", "Opening hours", 20, "text"),
        Col("distance_km", "Distance (km)", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000}),
        Col("parking", "Parking", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("organic_range", "Organic range", 12, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("bulk_bins", "Bulk bins", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")}),
        Col("cards", "Cards accepted", 18, "text"),
        Col("visits", "Shops recorded", 12, "calc", group="spend",
            formula='=IF({store}{r}="","",'
                    'COUNTIFS(' + gs_store + ',{store}{r}))'),
        Col("total_spend", "Total spend", 12, "calc",
            formula='=IF({store}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_store + ','
                    '{store}{r}))'),
        Col("avg_basket", "Average basket", 12, "calc",
            formula='=IF(OR({store}{r}="",{visits}{r}=0),"",'
                    'ROUND({total_spend}{r}/{visits}{r},2))'),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF(OR({store}{r}="",{total_spend}{r}=0),"",'
                    'COUNTIFS({total_spend_first}:{total_spend_last},'
                    '">"&{total_spend}{r})+1)'),
        Col("best_for", "Best for", 26, "text", group="notes"),
        Col("rating", "Rating (1-5)", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 5}),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Stores",
        title="Stores",
        subtitle="Where you shop, what they are good for and what you have "
                 "spent there",
        columns=columns,
        rows=cfg.row_count("Stores"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Grocery Spending", "Store Prices", "Lists", "Help"])
