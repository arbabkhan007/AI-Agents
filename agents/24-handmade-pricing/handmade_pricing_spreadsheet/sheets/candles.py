"""The Candles calculator.

Candles are costed by the pour, not by the jar: you type the wax in the
melting pot, the fragrance load, the wicks and vessels, and how many jars the
pour made. The tab divides the pour back down to one jar and costs it - wax,
fragrance at the load you actually use, wick, vessel - then adds the minutes a
jar takes.

`fragrance_oz_item` is worked out from the wax weight (pounds to ounces, then
the load percentage). If you weigh in grams, or buy fragrance by the drop,
type the cost straight into `fragrance_override` and it wins.

`cure_days`, the pour and melt temperatures and the burn hours are here because
they are the numbers a candle buyer asks about and a recall needs - they do not
feed the cost.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, int_col,
                     material_col, money_col, num_col, pct_col, product_col,
                     row_ref, samples, spec_defaults, text_col, wrap_col)

P = Palette

NAME = "Candles"

SUBTITLE = ("Candles: one pour costed down to a single jar, with the cure "
            "times and burn figures you need on the label.")

HELP = ("Type the wax in the pot, the fragrance load, the wicks and vessels, "
        "and how many jars the pour made. The cost of one jar and the price "
        "your margin asks for are worked out to the right.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cid = row_ref("id")
    has_id = f'{cid}=""'
    product = row_ref("product")
    wax = row_ref("wax")
    fragrance = row_ref("fragrance")
    wick = row_ref("wick")
    vessel = row_ref("vessel")
    batch = f"N({row_ref('batch_qty')})"
    wax_lb = f"N({row_ref('wax_lb')})"
    load = f"N({row_ref('fragrance_pct')})"

    batch_col = calc_col(
        "batch_qty", "Jars in the pour",
        f'IF({has_id},"",IF(N({row_ref("batch_size")})=0,DefaultBatchSize,'
        f'N({row_ref("batch_size")})))', 12.0, "int",
        note="How many jars one pour makes. Blank uses the default on "
             "Settings.")

    material_expr = (f'N({row_ref("wax_cost_item")})'
                     f'+N({row_ref("fragrance_cost_item")})'
                     f'+N({row_ref("wick_cost")})'
                     f'+N({row_ref("vessel_cost")})')

    cols: List[Any] = [
        id_col("PrefixCandle", trigger="blend", width=11.0),
        date_col("date", "Date poured", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("blend", "Blend / scent", 26.0,
                 note="What you poured. Filling this in starts the row."),
        material_col("wax", "Wax ID", 12.0,
                     note="The wax as it is listed on the Materials tab."),
        calc_col("wax_name", "Wax",
                 f'IF({wax}="","",{fetch("Materials", "id", "name", wax)})',
                 26.0, "text"),
        calc_col("wax_unit_cost", "Wax cost a unit",
                 f'IF({wax}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", wax, "0")})',
                 12.0, "money4"),
        num_col("wax_lb", "Wax in the pot", 12.0,
                note="Total wax melted for this pour, in the unit the "
                     "material is bought in (lb for the example shop)."),
        material_col("fragrance", "Fragrance ID", 12.0),
        calc_col("fragrance_name", "Fragrance",
                 f'IF({fragrance}="","",'
                 f'{fetch("Materials", "id", "name", fragrance)})', 26.0,
                 "text"),
        calc_col("fragrance_unit_cost", "Fragrance cost a unit",
                 f'IF({fragrance}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", fragrance, "0")})',
                 12.0, "money4"),
        pct_col("fragrance_pct", "Fragrance load", 11.0,
                note="Percentage of the wax weight - 8% is typical for soy."),
        material_col("wick", "Wick ID", 12.0),
        calc_col("wick_cost", "Wick cost a jar",
                 f'IF({wick}="",0,{fetch("Materials", "id", "cost_with_waste", wick, "0")})',
                 12.0, "money4"),
        material_col("vessel", "Vessel ID", 12.0),
        calc_col("vessel_name", "Vessel",
                 f'IF({vessel}="","",{fetch("Materials", "id", "name", vessel)})',
                 24.0, "text"),
        money_col("vessel_cost", "Vessel cost a jar", 13.0,
                  note="Jar plus lid for ONE item - a trio gift set costs "
                       "three of them."),
        num_col("batch_size", "Jars poured", 11.0,
                note="How many jars came out of this pour."),
        num_col("minutes_per_pour", "Minutes a jar", 12.0,
                note="Wicking, pouring, labelling and cleaning up, per jar."),
        calc_col("minutes", "Minutes used",
                 f'IF({has_id},"",N({row_ref("minutes_per_pour")}))', 11.0,
                 "number1", note="What the cost columns use."),
        calc_col("wax_per_item", "Wax a jar",
                 f'IF({has_id},"",IF({batch}=0,"",{wax_lb}/{batch}))',
                 11.0, "number"),
        calc_col("wax_cost_item", "Wax cost a jar",
                 f'IF({has_id},"",N({row_ref("wax_per_item")})'
                 f'*N({row_ref("wax_unit_cost")}))', 12.0, "money"),
        calc_col("fragrance_oz_item", "Fragrance a jar",
                 f'IF({has_id},"",N({row_ref("wax_per_item")})*16*{load})',
                 12.0, "number",
                 note="Wax weight in ounces times the load. Assumes the wax "
                      "is weighed in pounds."),
        money_col("fragrance_override", "Fragrance cost (typed)", 13.0,
                  note="Type a cost here and it beats the calculated one."),
        calc_col("fragrance_cost_item", "Fragrance cost a jar",
                 f'IF({has_id},"",IF(N({row_ref("fragrance_override")})>0,'
                 f'N({row_ref("fragrance_override")}),'
                 f'N({row_ref("fragrance_oz_item")})'
                 f'*N({row_ref("fragrance_unit_cost")})))', 13.0, "money"),
        int_col("cure_days", "Cure days", 10.0,
                note="How long the jar rests before it burns properly."),
        int_col("pour_temp", "Pour temp (F)", 11.0),
        int_col("melt_temp", "Melt temp (F)", 11.0),
        num_col("burn_hours", "Burn hours", 10.0,
                note="Total burn time - goes on the listing."),
        money_col("price", "Price today", 12.0),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr, has_difficulty=False,
                       batch_col=batch_col)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
