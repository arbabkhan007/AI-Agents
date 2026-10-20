"""The Variations tab - the options under one listing.

A scent, a stone, a size, a length, a personalisation: each one is a row, with
what it adds to the price and what it adds to the cost. The base price and the
base cost come off the Products tab, so a variation is always costed against
the current catalog figures rather than a copy that has gone stale.

`extra minutes` is the time the variation adds - a size L takes longer than a
size M, a dark stain needs another coat and another day. It is costed at the
loaded rate on Settings and folded into the variation's cost, which is the part
most shops forget and then wonder why the bigger size earns less.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, channel_fee_rate, channel_fixed_fee, countifs,
                     date_col, fetch, id_col, int_col, list_col, money_col,
                     other, product_col, rank_desc, raw_price_col, round_ref,
                     row_ref, samples, spec_defaults, text_col, wrap_col,
                     yesno_col)

P = Palette

NAME = "Variations"

SUBTITLE = ("Sizes, colours, scents and stones: what each option adds to the "
            "price, the cost and the time.")

HELP = ("Pick the product, pick the option and type what it adds. The base "
        "price and cost arrive from Products; the variation price, its margin "
        "and the price your target margin asks for are calculated here.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    vid = row_ref("id")
    has_id = f'{vid}=""'
    product = row_ref("product")
    base_price = fetch("Products", "id", "retail_price", product, "0")
    base_cost = fetch("Products", "id", "total_cost", product, "0")
    channel_of_product = fetch("Products", "id", "channel", product)
    chan = f'IF({channel_of_product}="",DefaultChannel,{channel_of_product})'
    rate = channel_fee_rate(chan)
    fixed = channel_fixed_fee(chan)
    vprice = f"N({row_ref('variation_price')})"
    vcost = (f'N({row_ref("variation_cost")})'
             f'+N({row_ref("extra_time_cost")})')
    profit = f'{vprice}-({rate}*{vprice}+{fixed})-{vcost}'

    cols: List[Any] = [
        id_col("PrefixVariation", trigger="value", width=11.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",{fetch("Products", "id", "name", product)})',
                 28.0, "text"),
        list_col("option", "Option", "VariationOptionList", 15.0,
                 note="Size, colour, scent, stone, finish, length..."),
        text_col("value", "Value", 20.0,
                 note="The choice itself: L, Amethyst, Cedar & sage."),
        text_col("sku", "Variation SKU", 16.0),
        calc_col("size_factor", "Size factor",
                 f'IF({has_id},"",IFERROR(INDEX(SizeFactors,'
                 f'MATCH({row_ref("value")},SizeNames,0)),1))', 11.0, "number",
                 note="From the size table on Lists, when the value is a size."),
        calc_col("base_price", "Base price",
                 f'IF({has_id},"",{base_price})', 12.0, "money"),
        money_col("price_adj", "Price adjustment", 13.0,
                  note="What this option adds to the price - negative for a "
                       "smaller size."),
        calc_col("variation_price", "Variation price",
                 f'IF({has_id},"",N({row_ref("base_price")})'
                 f'+N({row_ref("price_adj")}))', 13.0, "money"),
        calc_col("base_cost", "Base cost", f'IF({has_id},"",{base_cost})',
                 12.0, "money"),
        money_col("cost_adj", "Cost adjustment", 13.0,
                  note="What this option adds to the materials."),
        calc_col("variation_cost", "Materials cost",
                 f'IF({has_id},"",N({row_ref("base_cost")})'
                 f'+N({row_ref("cost_adj")}))', 13.0, "money"),
        int_col("qty_delta", "Extra minutes", 12.0,
                note="Time this option adds - a bigger size, an extra coat, "
                     "personalisation."),
        calc_col("extra_time_cost", "Extra time cost",
                 f'IF({has_id},"",N({row_ref("qty_delta")})/60*LaborCostHour)',
                 13.0, "money"),
        calc_col("total_cost", "Total cost",
                 f'IF({has_id},"",{vcost})', 13.0, "money"),
        calc_col("fee_rate", "Fee rate", f'IF({has_id},"",{rate})', 11.0,
                 "percent"),
        calc_col("fees", "Fees",
                 f'IF({has_id},"",{rate}*{vprice}+{fixed})', 12.0, "money"),
        calc_col("profit", "Profit",
                 f'IF({has_id},"",IF({vprice}=0,"",{profit}))', 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({has_id},"",IF({vprice}=0,"",{profit}/{vprice}))',
                 10.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_flag", "Flag",
                 f'IF({has_id},"",IF({vprice}=0,"",IF({profit}<=0,"LOSS",'
                 f'IF({profit}/{vprice}<MarginWarning,"THIN","OK"))))',
                 9.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOSS", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "THIN", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        # the unrounded model price gets its own hidden cell: the rounding
        # rule repeats its argument eight times, and eight copies of this
        # cost expression pass Excel's 8,192 character formula limit
        raw_price_col(vcost, fixed, "TargetRetailMargin", rate, guard=has_id),
        calc_col("suggested_price", "Suggested price",
                 f'IF({has_id},"",{round_ref(row_ref("price_raw"))})',
                 13.0, "money"),
        calc_col("price_gap", "Gap to suggested",
                 f'IF(OR({has_id},{vprice}=0),"",'
                 f'N({row_ref("suggested_price")})-{vprice})', 13.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "bad"}]),
        int_col("stock", "Stock", 10.0,
                note="Blank or zero means made to order."),
        calc_col("stock_flag", "Stock",
                 f'IF({has_id},"",IF(N({row_ref("stock")})=0,"MADE TO ORDER",'
                 f'IF(N({row_ref("stock")})<=2,"LOW","IN STOCK")))', 15.0,
                 "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "MADE TO ORDER", "fmt": "info"}]),
        yesno_col("active", "On sale?", 10.0),
        calc_col("in_bundles", "In bundles",
                 countifs([(other("Bundle Lines", "product"), product)]),
                 11.0, "int"),
        calc_col("sku_check", "SKU check",
                 f'IF(OR({has_id},{row_ref("sku")}=""),"",'
                 f'IF(COUNTIFS({{sku_first}}:{{sku_last}},{row_ref("sku")})>1,'
                 f'"DUPLICATE SKU",""))', 14.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "DUPLICATE", "fmt": "bold_bad"}]),
        date_col("created", "Added", 13.0),
        wrap_col("notes", "Notes", 30.0),
        calc_col("rank_margin", "rank margin", rank_desc("margin"), 9.0,
                 "int", hidden=True),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
