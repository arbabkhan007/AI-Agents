"""The Waste Log - what got thrown away, and what it cost.

Every broken jar, every mis-cut length of linen, every board with a loose knot.
The Materials tab adds these rows up to give a real waste rate against the
guessed one, the Products tab can pick up the cost by product, and the Reports
tab totals it by month and by reason.

Waste is the cost nobody writes down, which is exactly why it never gets fixed.
`recoverable` and `recovered_value` are here for the seconds that still sell -
a warped board becomes a coaster, a chipped jar becomes a sample - so `net_loss`
is the money that actually went.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, fetch, id_col, list_col_inline,
                     material_col, money_col, num_col, product_col, rank_desc,
                     row_ref, samples, spec_defaults, wrap_col, yesno_col)

P = Palette

NAME = "Waste Log"

SUBTITLE = ("What got broken, spoiled or mis-cut, what it cost and whether any "
            "of it was recovered.")

HELP = ("One row per loss. Pick the material and the cost per unit arrives "
        "from the Materials tab. Add a product when the loss happened while "
        "making something specific - the Products tab picks the cost up.")

STAGES = ["Making", "Finishing", "Packing", "Shipping", "Storage",
          "Supplier fault", "Sample", "Customer return"]


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    wid = row_ref("id")
    has_id = f'{wid}=""'
    material = row_ref("material")
    product = row_ref("product")
    date = row_ref("date")
    qty = f"N({row_ref('qty')})"
    unit_cost = f"N({row_ref('unit_cost')})"

    cols: List[Any] = [
        id_col("PrefixWaste", trigger="material", width=11.0),
        date_col("date", "Date", 13.0),
        product_col(note="Blank when the loss was not part of one product."),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        material_col(),
        calc_col("material_name", "Material",
                 f'IF({material}="","",'
                 f'{fetch("Materials", "id", "name", material)})', 28.0,
                 "text"),
        calc_col("unit", "Unit",
                 f'IF({material}="","",'
                 f'{fetch("Materials", "id", "unit", material)})', 9.0,
                 "text"),
        calc_col("unit_cost", "Cost a unit",
                 f'IF({material}="",0,'
                 f'{fetch("Materials", "id", "cost_with_waste", material, "0")})',
                 12.0, "money4"),
        num_col("qty", "Qty lost", 11.0,
                note="In the unit the material is bought in."),
        calc_col("cost", "Cost of the loss",
                 f'IF({has_id},"",{qty}*{unit_cost})', 13.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "warn"}]),
        list_col_inline("reason", "Reason", 
                        ["Breakage", "Spillage", "Cutting error", "Defect",
                         "Misprint", "Shedding", "Knots",
                         "Damaged in storage", "Expired", "Wrong colour",
                         "Sample", "Other"], 17.0,
                        note="Also on the Lists tab as WasteReasonList."),
        list_col_inline("stage", "Where it happened", STAGES, 15.0),
        yesno_col("recoverable", "Recovered?", 11.0,
                  note="Sold as a second, used as a sample, remade into "
                       "something smaller."),
        money_col("recovered_value", "Value recovered", 13.0),
        calc_col("net_loss", "Net loss",
                 f'IF({has_id},"",N({row_ref("cost")})'
                 f'-N({row_ref("recovered_value")}))', 12.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "bad"}]),
        calc_col("month", "Month",
                 f'IF({date}="","",TEXT(N({date}),"yyyy-mm"))', 10.0, "text"),
        calc_col("rank_cost", "rank cost", rank_desc("cost"), 9.0, "int",
                 hidden=True),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
