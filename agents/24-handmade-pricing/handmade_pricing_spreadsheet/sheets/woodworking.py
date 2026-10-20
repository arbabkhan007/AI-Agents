"""The Woodworking calculator.

One row per piece: the lumber and how many board feet it took, hardware, the
finish and how much of it, glue, and the time in four parts - cutting, shaping,
sanding and finishing. Sanding and finishing are where a small piece quietly
becomes an expensive one, so they get their own columns rather than being
folded into "making".

Waste is already inside the lumber cost: the Materials tab carries a waste
percentage for the board (12% in the example shop, for knots and planing) and
`cost_with_waste` is what this tab picks up.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, list_col,
                     material_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Woodworking"

SUBTITLE = ("Woodwork: lumber, hardware, finish and the time in cutting, "
            "shaping, sanding and finishing.")

HELP = ("Pick the lumber and the finish from the materials list, type the "
        "board feet and the four times. The cost of one piece and the price "
        "your margin asks for are calculated to the right.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    wid = row_ref("id")
    has_id = f'{wid}=""'
    product = row_ref("product")
    lumber = row_ref("lumber")
    finish = row_ref("finish")

    material_expr = (f'N({row_ref("lumber_cost")})'
                     f'+N({row_ref("hardware")})'
                     f'+N({row_ref("finish_cost")})+N({row_ref("glue")})')

    cols: List[Any] = [
        id_col("PrefixWood", trigger="project", width=11.0),
        date_col("date", "Date made", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("project", "Project", 28.0,
                 note="What you made. Filling this in starts the row."),
        list_col("species", "Species", "WoodSpeciesList", 16.0),
        material_col("lumber", "Lumber ID", 12.0,
                     note="The board as it is listed on Materials, priced a "
                          "board foot."),
        calc_col("lumber_name", "Lumber",
                 f'IF({lumber}="","",'
                 f'{fetch("Materials", "id", "name", lumber)})', 28.0, "text"),
        calc_col("lumber_unit_cost", "Cost a board foot",
                 f'IF({lumber}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", lumber, "0")})',
                 13.0, "money4",
                 note="Waste for knots and planing is already in this figure."),
        num_col("board_feet", "Board feet", 11.0),
        calc_col("lumber_cost", "Lumber cost",
                 f'IF({has_id},"",N({row_ref("board_feet")})'
                 f'*N({row_ref("lumber_unit_cost")}))', 12.0, "money"),
        money_col("hardware", "Hardware", 12.0,
                  note="Hinges, magnets, handles, fixings."),
        material_col("finish", "Finish ID", 12.0),
        calc_col("finish_name", "Finish",
                 f'IF({finish}="","",'
                 f'{fetch("Materials", "id", "name", finish)})', 26.0, "text"),
        calc_col("finish_unit_cost", "Finish cost a unit",
                 f'IF({finish}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", finish, "0")})',
                 12.0, "money4"),
        num_col("finish_oz", "Finish used", 11.0,
                note="In the unit the finish is bought in - fl oz, ml."),
        calc_col("finish_cost", "Finish cost",
                 f'IF({has_id},"",N({row_ref("finish_oz")})'
                 f'*N({row_ref("finish_unit_cost")}))', 12.0, "money"),
        money_col("glue", "Glue & consumables", 13.0,
                  note="Glue, sandpaper, rags, blades - what this piece wore out."),
        num_col("cut_minutes", "Cutting min", 11.0),
        num_col("shape_minutes", "Shaping min", 11.0,
                note="Routing, planing, joinery."),
        num_col("sand_minutes", "Sanding min", 11.0),
        num_col("finish_minutes", "Finishing min", 11.0,
                note="Oiling, waxing, polishing and the waiting in between."),
        num_col("total_minutes", "Minutes (typed)", 12.0,
                note="Type a total and it beats the four parts."),
        calc_col("minutes", "Minutes used",
                 f'IF({has_id},"",IF(N({row_ref("total_minutes")})>0,'
                 f'N({row_ref("total_minutes")}),'
                 f'N({row_ref("cut_minutes")})+N({row_ref("shape_minutes")})'
                 f'+N({row_ref("sand_minutes")})'
                 f'+N({row_ref("finish_minutes")})))', 11.0, "number1"),
        calc_col("hours", "Hours",
                 f'IF({has_id},"",N({row_ref("minutes")})/60)', 9.0, "number"),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0),
        list_col("size", "Size", "SizeList", 11.0),
        yesno_col("food_safe", "Food safe", 10.0,
                  note="Food safe finish, for boards and bowls."),
        money_col("price", "Price today", 12.0),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
