"""The Bundle Lines tab - what is actually inside each bundle.

One row per product per bundle. The unit price comes off the Products tab (or
from `price_override` when a part is priced specially inside the set), the unit
cost comes off the same row, and the Bundles tab adds the lines up to get the
list price, the real cost and the profit of the set.

`line_profit` is the column that catches a bad bundle: a part that loses money
on its own loses money inside the set too, and discounting on top of it makes
it worse.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from ..writer import list_from
from .common import (calc_col, fetch, id_col, int_col, money_col, product_col,
                     row_ref, samples, spec_defaults, wrap_col)
from ..layout import Col

P = Palette

NAME = "Bundle Lines"

SUBTITLE = ("What is inside each bundle, at what price and at what cost.")

HELP = ("Pick the bundle, pick a product, type the quantity. The price and the "
        "cost arrive from the Products tab; Bundles adds the lines together.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    lid = row_ref("id")
    has_id = f'{lid}=""'
    bundle = row_ref("bundle")
    product = row_ref("product")
    qty = f"N({row_ref('qty')})"
    unit_price = f"N({row_ref('unit_price')})"
    unit_cost = f"N({row_ref('unit_cost')})"

    cols: List[Any] = [
        id_col("PrefixBundleLine", trigger="product", width=11.0),
        Col(key="bundle", header="Bundle ID", width=12.0, style="id",
            validate=list_from("BundleIDs"),
            note="Which bundle this line belongs to."),
        calc_col("bundle_name", "Bundle",
                 f'IF({bundle}="","",{fetch("Bundles", "id", "name", bundle)})',
                 28.0, "text"),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 28.0, "text"),
        calc_col("product_active", "Sellable?",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "active", product)})', 10.0,
                 "flag",
                 note="A bundle cannot sell a product that is not active.",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "No", "fmt": "warn"}]),
        int_col("qty", "Qty in the set", 11.0),
        money_col("price_override", "Special price", 12.0,
                  note="Type a price for this part inside the set and it "
                       "beats the catalog price."),
        calc_col("unit_price", "Unit price",
                 f'IF({has_id},"",IF(N({row_ref("price_override")})>0,'
                 f'N({row_ref("price_override")}),'
                 f'IFERROR(INDEX([[Products.retail_price]],'
                 f'MATCH({product},[[Products.id]],0)),0)))', 12.0, "money"),
        calc_col("line_total", "Line total",
                 f'IF({has_id},"",{qty}*{unit_price})', 12.0, "money"),
        calc_col("unit_cost", "Unit cost",
                 f'IF({has_id},"",{fetch("Products", "id", "total_cost", product, "0")})',
                 12.0, "money"),
        calc_col("line_cost", "Line cost",
                 f'IF({has_id},"",{qty}*{unit_cost})', 12.0, "money"),
        calc_col("line_profit", "Line profit",
                 f'IF({has_id},"",{qty}*({unit_price}-{unit_cost}))', 12.0,
                 "money",
                 note="Before the bundle discount and the channel fees.",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
