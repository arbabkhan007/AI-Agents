"""The Crochet calculator.

One row per piece (or per batch of pieces): the yarn, how many skeins it took,
the notions, and the minutes at the hook. From that the shared craft tail works
out the cost of one finished item, the price the model asks for, what the
current price really earns and what an hour of crocheting pays.

The yarn cost comes off the Materials tab through the yarn ID, waste allowance
included, so a change in the price of merino moves every scarf that uses it.
The `difficulty_factor` column reads the factor table on Lists - a Hard pattern
is assumed to take longer than an Easy one, and that assumption is editable.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, list_col,
                     material_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col)

P = Palette

NAME = "Crochet"

SUBTITLE = ("Crochet and knitting: yarn, notions and time at the hook, costed "
            "to one finished item.")

HELP = ("Pick the yarn from the materials list and type the skeins and the "
        "minutes. Everything to the right of 'Price' is calculated: the cost "
        "of one item, the price your target margin asks for, and what an hour "
        "of this work actually pays you.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cid = row_ref("id")
    has_id = f'{cid}=""'
    yarn = row_ref("yarn")
    product = row_ref("product")
    minutes = row_ref("minutes")

    material_expr = (f'N({row_ref("yarn_cost")})+N({row_ref("hooks")})'
                     f'+N({row_ref("notions")})')

    cols: List[Any] = [
        id_col("PrefixCrochet", trigger="pattern", width=11.0),
        date_col("date", "Date made", 13.0),
        product_col(note="The catalog product this piece belongs to, if it "
                         "has one. Prototypes can leave it blank."),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("pattern", "Pattern", 28.0,
                 note="What you made. Filling this in starts the row."),
        text_col("pattern_source", "Pattern by", 20.0,
                 note="Designer, book or your own - and whether a licence fee "
                      "applies."),
        material_col("yarn", "Yarn ID", 12.0,
                     note="The yarn as it is listed on the Materials tab."),
        calc_col("yarn_name", "Yarn",
                 f'IF({yarn}="","",{fetch("Materials", "id", "name", yarn)})',
                 30.0, "text"),
        calc_col("yarn_unit", "Unit",
                 f'IF({yarn}="","",{fetch("Materials", "id", "unit", yarn)})',
                 9.0, "text"),
        calc_col("yarn_unit_cost", "Cost a unit",
                 f'IF({yarn}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", yarn, "0")})',
                 12.0, "money4",
                 note="From Materials, with the expected waste added."),
        num_col("skeins", "Skeins", 10.0,
                note="In the unit above: skeins, ounces, grams."),
        num_col("yardage", "Yardage / metres", 12.0,
                note="Optional - useful when a pattern gives a length."),
        calc_col("yarn_cost", "Yarn cost",
                 f'IF({has_id},"",N({row_ref("skeins")})'
                 f'*N({row_ref("yarn_unit_cost")}))', 12.0, "money"),
        money_col("hooks", "Hooks & tools", 12.0,
                  note="Share of hooks, stitch markers, scissors - the tools "
                       "this piece wears out."),
        money_col("notions", "Notions", 12.0,
                  note="Buttons, zips, safety eyes, labels, stuffing."),
        text_col("gauge", "Gauge", 14.0, note="e.g. 12 st = 4in"),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0),
        list_col("size", "Size", "SizeList", 11.0),
        num_col("minutes", "Minutes", 10.0,
                note="Time at the hook for ONE item, not the whole batch."),
        calc_col("hours", "Hours",
                 f'IF({has_id},"",N({minutes})/60)', 9.0, "number"),
        money_col("price", "Price today", 12.0,
                  note="What this piece actually sells for."),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
