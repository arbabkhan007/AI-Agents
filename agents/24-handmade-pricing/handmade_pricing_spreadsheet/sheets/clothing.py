"""The Clothing calculator.

One row per garment or accessory: the fabric and how many yards it took, the
interfacing, notions, lining and trim, and the time in three parts - cutting,
sewing, finishing. Splitting the time is deliberate: cutting and finishing are
the steps that get faster in a batch, and seeing them separately is what tells
you whether a garment is slow because of the pattern or because of the binding.

`total_minutes` wins when you type it; otherwise the three parts are added.
The `size_factor` column reads the size table on Lists, so a size L can be
costed from the same row as a size M.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, list_col,
                     material_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Clothing"

SUBTITLE = ("Sewn items: fabric, notions and the time in cutting, sewing and "
            "finishing, costed to one garment.")

HELP = ("Pick the fabric, type the yards and the three times. The cost of one "
        "garment and the price your margin asks for are calculated to the "
        "right. Minutes can be typed as one figure or left to the three parts.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cid = row_ref("id")
    has_id = f'{cid}=""'
    product = row_ref("product")
    fabric = row_ref("fabric")

    material_expr = (f'N({row_ref("fabric_cost")})'
                     f'+N({row_ref("interfacing")})+N({row_ref("notions")})'
                     f'+N({row_ref("lining")})+N({row_ref("trim")})')

    cols: List[Any] = [
        id_col("PrefixClothing", trigger="pattern_name", width=11.0),
        date_col("date", "Date made", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("pattern_name", "Pattern / item", 28.0,
                 note="What you sewed. Filling this in starts the row."),
        text_col("pattern_source", "Pattern by", 20.0,
                 note="Commercial pattern, your own draft, or a licence."),
        material_col("fabric", "Fabric ID", 12.0),
        calc_col("fabric_name", "Fabric",
                 f'IF({fabric}="","",'
                 f'{fetch("Materials", "id", "name", fabric)})', 28.0, "text"),
        calc_col("fabric_unit_cost", "Fabric cost a unit",
                 f'IF({fabric}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", fabric, "0")})',
                 12.0, "money4"),
        num_col("yards", "Yards / metres", 12.0,
                note="In the unit the fabric is bought in, cutting waste "
                     "included."),
        calc_col("fabric_cost", "Fabric cost",
                 f'IF({has_id},"",N({row_ref("yards")})'
                 f'*N({row_ref("fabric_unit_cost")}))', 12.0, "money"),
        money_col("interfacing", "Interfacing", 12.0),
        money_col("notions", "Notions", 12.0,
                  note="Zips, buttons, elastic, thread, grommets, cord."),
        money_col("lining", "Lining", 11.0),
        money_col("trim", "Trim & labels", 12.0),
        list_col("size", "Size", "SizeList", 11.0),
        calc_col("size_factor", "Size factor",
                 f'IF({has_id},"",IFERROR(INDEX(SizeFactors,'
                 f'MATCH({row_ref("size")},SizeNames,0)),1))', 11.0, "number",
                 note="From the size table on Lists - what this size adds to "
                      "the fabric and the time."),
        num_col("cut_minutes", "Cutting min", 11.0),
        num_col("sew_minutes", "Sewing min", 11.0),
        num_col("finish_minutes", "Finishing min", 11.0,
                note="Binding, pressing, labels, quality check."),
        num_col("total_minutes", "Minutes (typed)", 12.0,
                note="Type a total and it beats the three parts."),
        calc_col("minutes", "Minutes used",
                 f'IF({has_id},"",IF(N({row_ref("total_minutes")})>0,'
                 f'N({row_ref("total_minutes")}),'
                 f'N({row_ref("cut_minutes")})+N({row_ref("sew_minutes")})'
                 f'+N({row_ref("finish_minutes")})))', 11.0, "number1"),
        calc_col("hours", "Hours",
                 f'IF({has_id},"",N({row_ref("minutes")})/60)', 9.0, "number"),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0),
        yesno_col("care_label", "Care label", 10.0),
        money_col("price", "Price today", 12.0),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
