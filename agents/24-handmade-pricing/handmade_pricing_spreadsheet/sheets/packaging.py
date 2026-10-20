"""The Packaging tab - what it costs to get one item out of the door.

Each row is one packaging component: a mailer, a box, tissue, a seal sticker, a
care card. `products` says which products it goes with - a comma separated list
of product IDs, or the word ``All`` for the things every order gets. The
Products tab adds the components that match a product plus everything marked
``All``, and falls back to the default packaging cost on Settings when nothing
matches.

`override_cost` is there for the box you buy from a different supplier at a
different price: type a figure and it wins over the material lookup.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, fetch, id_col, list_col, material_col,
                     money_col, num_col, rank_desc, row_ref, samples,
                     spec_defaults, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Packaging"

SUBTITLE = ("Boxes, mailers, tissue and inserts: what one packed order costs "
            "and which products it applies to.")

HELP = ("List every component that goes into a parcel. In 'Applies to' type "
        "product IDs separated by commas, or the word All for components "
        "every order gets. Products picks these up automatically.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    pk = row_ref("id")
    has_id = f'{pk}=""'
    qty = f"N({row_ref('qty')})"
    unit_cost = f"N({row_ref('unit_cost')})"
    override = f"N({row_ref('override_cost')})"
    cost = (f'IF({override}>0,{override},{qty}*{unit_cost})')
    products = row_ref("products")

    cols: List[Any] = [
        id_col("PrefixPackaging", trigger="name", width=11.0),
        text_col("name", "Component", 30.0,
                 note="What it is: kraft mailer, tissue sheet, seal sticker."),
        list_col("type", "Type", "PackTypeList", 14.0),
        material_col(note="The material this component is bought as."),
        calc_col("material_name", "Material",
                 f'IF({row_ref("material")}="","",'
                 f'{fetch("Materials", "id", "name", row_ref("material"))})',
                 28.0, "text"),
        calc_col("unit_cost", "Cost a unit",
                 f'IF({row_ref("material")}="",0,'
                 f'{fetch("Materials", "id", "unit_cost", row_ref("material"), "0")})',
                 12.0, "money4"),
        num_col("qty", "Qty an order", 10.0,
                note="How many of these go in one parcel."),
        money_col("override_cost", "Override cost", 12.0,
                  note="Type a cost here and it beats the material lookup."),
        calc_col("cost", "Cost an order", f'IF({has_id},"",{cost})',
                 12.0, "money"),
        num_col("weight_oz", "Weight (oz)", 10.0,
                note="Packaging weight - it is posted too."),
        yesno_col("fragile", "Fragile", 9.0),
        yesno_col("reusable", "Reusable", 9.0),
        yesno_col("branded", "Branded", 9.0),
        text_col("products", "Applies to", 26.0,
                 note="Product IDs separated by commas, or the word All."),
        calc_col("applies_all", "Every order?",
                 f'IF({has_id},"",IF(EXACT(TRIM({products}),"All"),"Yes","No"))',
                 11.0, "flag",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "Yes", "fmt": "info"}]),
        calc_col("product_count", "Products listed",
                 f'IF({has_id},"",IF({products}="",0,'
                 f'IF(EXACT(TRIM({products}),"All"),"All",'
                 f'LEN({products})-LEN(SUBSTITUTE({products},",",""))+1)))',
                 11.0, "int"),
        calc_col("per_batch", "Cost a batch",
                 f'IF({has_id},"",{cost}*DefaultBatchSize)', 12.0, "money"),
        text_col("supplier", "Supplier", 20.0),
        num_col("on_hand", "On hand", 10.0),
        calc_col("stock_value", "Stock value",
                 f'IF({has_id},"",N({row_ref("on_hand")})*{cost})', 12.0,
                 "money"),
        num_col("reorder_point", "Re-order at", 11.0),
        calc_col("stock_flag", "Action",
                 f'IF({has_id},"",IF(N({row_ref("on_hand")})=0,"",'
                 f'IF(N({row_ref("on_hand")})<=N({row_ref("reorder_point")}),'
                 f'"REORDER","OK")))', 11.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "REORDER", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        text_col("recycle_note", "Recycling note", 22.0,
                 note="Goes on the care card: recyclable, compostable..."),
        date_col("last_ordered", "Last ordered", 13.0),
        calc_col("rank_cost", "rank cost", rank_desc("cost"), 9.0, "int",
                 hidden=True),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary_mid))
