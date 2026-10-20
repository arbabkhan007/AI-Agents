"""The Jewelry calculator.

One row per piece: the metal, the stones and what they cost, findings, wire,
chain, any plating, and the minutes at the bench. The shared craft tail turns
that into the cost of one item, the price the target margin asks for, and what
an hour of bench work pays.

Stone costs are typed for the piece (`stone_cost`) because a strand is bought
by the lot and used across several designs; `cost_a_stone` divides it back out
so the next design can be costed from the same strand.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, int_col,
                     list_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Jewelry"

SUBTITLE = ("Jewellery: metal, stones, findings and bench time, costed to one "
            "finished piece.")

HELP = ("Type what the piece is made of and what the stones and findings "
        "cost. Minutes are for one piece. The columns to the right of 'Price "
        "today' are calculated - including the hourly wage the piece actually "
        "pays, which is where most jewellery pricing goes wrong.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    jid = row_ref("id")
    has_id = f'{jid}=""'
    product = row_ref("product")
    stones = f"N({row_ref('stones')})"
    minutes = row_ref("minutes")

    material_expr = (f'N({row_ref("stone_cost")})+N({row_ref("findings")})'
                     f'+N({row_ref("wire")})+N({row_ref("chain")})'
                     f'+N({row_ref("plating")})')

    cols: List[Any] = [
        id_col("PrefixJewelry", trigger="design", width=11.0),
        date_col("date", "Date made", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("design", "Design", 30.0,
                 note="What the piece is. Filling this in starts the row."),
        list_col("metal", "Metal", "MetalList", 17.0),
        int_col("stones", "Stones", 9.0),
        money_col("stone_cost", "Stone cost", 12.0,
                  note="What the stones in THIS piece cost - divide a strand "
                       "out if you bought a lot."),
        calc_col("cost_a_stone", "Cost a stone",
                 f'IF({has_id},"",IF({stones}=0,"",'
                 f'N({row_ref("stone_cost")})/{stones}))', 12.0, "money4"),
        money_col("findings", "Findings", 12.0,
                  note="Ear wires, clasps, jump rings, settings."),
        money_col("wire", "Wire", 11.0),
        num_col("chain_inches", "Chain (in)", 11.0,
                note="How much chain the piece takes."),
        money_col("chain", "Chain cost", 12.0),
        money_col("plating", "Plating / finishing", 13.0,
                  note="Outside work: plating, tumbling, engraving."),
        calc_col("findings_total", "Metal & findings total",
                 f'IF({has_id},"",N({row_ref("findings")})'
                 f'+N({row_ref("wire")})+N({row_ref("chain")})'
                 f'+N({row_ref("plating")}))', 14.0, "money"),
        num_col("minutes", "Minutes", 10.0,
                note="Bench time for one piece."),
        calc_col("hours", "Hours",
                 f'IF({has_id},"",N({minutes})/60)', 9.0, "number"),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0),
        list_col("size", "Size", "SizeList", 11.0),
        yesno_col("hallmarked", "Hallmarked", 10.0),
        money_col("price", "Price today", 12.0),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
