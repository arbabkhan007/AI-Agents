"""The Materials tab - everything bought in to make things.

Yarn, wax, stones, fabric, lumber, mailers: one row per material with what a
unit costs, how much of it is normally lost, and how much is on the shelf. The
stock columns are what turn this into a re-ordering tool - `stock_flag` says
REORDER the moment the shelf drops to the re-order point, and `order_by` shows
the date an order has to go in for the stock to arrive in time.

The `used_qty` and `wasted_qty` columns read the Material Usage and Waste Log
tabs, so `actual_waste_rate` is the real loss rate rather than the guess in
`waste_pct`. When the real rate runs well ahead of the guess the row says so -
that is usually where money is quietly leaking.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, countifs, date_col, id_col, int_col, list_col,
                     money_col, num_col, other, pct_col, rank_desc, rank_flag,
                     row_ref, samples, spec_defaults, sumifs, text_col,
                     wrap_col)

P = Palette

NAME = "Materials"

SUBTITLE = ("Raw materials and supplies: unit cost, waste, stock on hand and "
            "when to re-order.")

HELP = ("Type the material and what one unit costs. The workbook works out "
        "the cost with waste, the value of the stock you hold, how much has "
        "been used and how much has been thrown away. Everything downstream - "
        "bills of materials, craft tabs, product costs - reads this tab.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    mid = row_ref("id")
    has_id = f'{mid}=""'
    unit_cost = f"N({row_ref('unit_cost')})"
    on_hand = f"N({row_ref('on_hand')})"
    waste = f"N({row_ref('waste_pct')})"
    point = f"N({row_ref('reorder_point')})"

    used_qty = sumifs(other("Material Usage", "qty"),
                      [(other("Material Usage", "material"), mid)])
    used_cost = sumifs(other("Material Usage", "cost"),
                       [(other("Material Usage", "material"), mid)])
    products_using = countifs([(other("Material Usage", "material"), mid)])
    wasted_qty = sumifs(other("Waste Log", "qty"),
                        [(other("Waste Log", "material"), mid)])
    wasted_cost = sumifs(other("Waste Log", "cost"),
                         [(other("Waste Log", "material"), mid)])

    stock_status = (f'IF({has_id},"",'
                    f'IF({on_hand}<=0,"Out of stock",'
                    f'IF({on_hand}<={point},"Low","In stock")))')
    stock_flag = (f'IF({has_id},"",'
                  f'IF({on_hand}<=0,"ORDER NOW",'
                  f'IF({on_hand}<={point},"REORDER",'
                  f'IF({on_hand}<={point}*1.5+0.001,"WATCH","OK"))))')
    waste_flag = (f'IF(OR({has_id},{row_ref("actual_waste_rate")}=""),"",'
                  f'IF(N({row_ref("actual_waste_rate")})>{waste}*1.5+0.005,'
                  f'"WASTE HIGH",'
                  f'IF(N({row_ref("actual_waste_rate")})<{waste}*0.5,'
                  f'"BETTER THAN PLAN","OK")))')
    order_by = (f'IF({has_id},"",IF({on_hand}<={point},'
                f'TodayDate,TodayDate+N({row_ref("lead_days")})+30))')

    cols: List[Any] = [
        id_col("PrefixMaterial", trigger="name", width=11.0,
               note="Numbers itself from the prefix on Settings."),
        text_col("name", "Material", 34.0,
                 note="What you buy. Filling this in starts the row."),
        text_col("sku", "Supplier code", 15.0),
        list_col("category", "Category", "MaterialCategoryList", 17.0),
        text_col("supplier", "Supplier", 22.0),
        list_col("supplier_terms", "Terms", "SupplierTermList", 13.0),
        list_col("unit", "Unit", "UnitList", 10.0,
                 note="The unit you buy in: g, oz, skein, each, yard..."),
        num_col("pack_size", "Pack size", 10.0,
                note="How many units one purchase pack holds."),
        money_col("unit_cost", "Cost a unit", 12.0, style="money4",
                  note="What one unit costs, to a fraction of a cent - a "
                       "gram of yarn is not a whole cent."),
        calc_col("pack_cost", "Cost a pack",
                 f'IF({has_id},"",N({row_ref("pack_size")})*{unit_cost})',
                 12.0, "money"),
        pct_col("waste_pct", "Expected waste", 11.0,
                note="How much of this is normally lost: offcuts, shedding, "
                     "breakage. Blank rows can start from DefaultWaste on "
                     "Settings."),
        calc_col("cost_with_waste", "Cost with waste",
                 f'IF({has_id},"",{unit_cost}*(1+{waste}))', 12.0, "money4",
                 note="What a unit really costs once the usual loss is added."),
        num_col("on_hand", "On hand", 11.0),
        calc_col("stock_value", "Stock value",
                 f'IF({has_id},"",{on_hand}*{unit_cost})', 12.0, "money"),
        num_col("reorder_point", "Re-order at", 11.0,
                note="Order when the shelf drops to this."),
        num_col("reorder_qty", "Re-order qty", 11.0),
        calc_col("stock_status", "Stock status", stock_status, 13.0, "status"),
        calc_col("stock_flag", "Action", stock_flag, 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "ORDER NOW", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "REORDER", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "WATCH", "fmt": "info"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("order_cost", "Order cost",
                 f'IF({has_id},"",N({row_ref("reorder_qty")})*{unit_cost})',
                 12.0, "money"),
        int_col("lead_days", "Lead days", 10.0,
                note="How long the supplier takes."),
        calc_col("order_by", "Order by", order_by, 13.0, "date",
                 note="Today if stock is already at the re-order point, "
                      "otherwise the day an order would land."),
        calc_col("used_qty", "Used (units)", used_qty, 11.0, "number"),
        calc_col("used_cost", "Used (cost)", used_cost, 12.0, "money"),
        calc_col("products_using", "Products using it", products_using,
                 11.0, "int"),
        calc_col("wasted_qty", "Wasted (units)", wasted_qty, 11.0, "number"),
        calc_col("wasted_cost", "Wasted (cost)", wasted_cost, 12.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "warn"}]),
        calc_col("actual_waste_rate", "Real waste rate",
                 f'IF({has_id},"",IF(N({used_qty})+N({wasted_qty})=0,"",'
                 f'N({wasted_qty})/(N({used_qty})+N({wasted_qty}))))',
                 11.0, "percent"),
        calc_col("waste_flag", "Waste check", waste_flag, 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "WASTE HIGH", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "BETTER", "fmt": "good"}]),
        text_col("location", "Stored where", 15.0),
        date_col("last_purchase", "Last bought", 13.0),
        calc_col("rank_usage", "rank usage", rank_desc("used_cost"), 9.0,
                 "int", hidden=True),
        calc_col("rank_reorder", "rank reorder",
                 rank_flag("stock_flag", "REORDER"), 9.0, "int", hidden=True,
                 note="Hidden - the Dashboard lists what needs ordering."),
        calc_col("rank_out", "rank out of stock",
                 rank_flag("stock_flag", "ORDER NOW"), 9.0, "int",
                 hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary_mid))
