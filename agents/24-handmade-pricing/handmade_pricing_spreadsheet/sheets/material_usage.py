"""The Material Usage tab - bills of materials.

One row per material per product: how much of it one finished item takes and
what that costs once the cutting loss is added. The Products tab adds these
rows up to get `material_cost`, so this is where a price really comes from.

`duplicate_flag` catches the mistake that quietly doubles a cost - the same
material listed twice against the same product.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (NO_MATCH, calc_col, fetch, id_col, list_col_inline,
                     material_col, num_col, pct_col, product_col, rank_desc,
                     row_ref, samples, spec_defaults, wrap_col)

P = Palette

NAME = "Material Usage"

SUBTITLE = ("Bills of materials: what each product is made of and what the "
            "materials cost.")

HELP = ("Pick a product, pick a material, type how much one item takes. The "
        "unit cost arrives from the Materials tab and the scrap allowance "
        "lifts it to what the material really costs. Products adds every row "
        "for one product together.")

SOURCES = ["Bill of materials", "Craft tab", "One off", "Estimate",
           "Sample / prototype"]


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    pid = row_ref("product")
    mid = row_ref("material")
    empty = f'OR({pid}="",{mid}="")'
    qty = f"N({row_ref('qty')})"
    scrap = f"N({row_ref('scrap_pct')})"
    unit_cost = f"N({row_ref('unit_cost')})"
    cost = f"{qty}*(1+{scrap})*{unit_cost}"

    cols: List[Any] = [
        id_col("PrefixUsage", trigger="material", width=11.0,
               note="Numbers itself once a material is picked."),
        product_col(note="Which product this line belongs to."),
        calc_col("product_name", "Product",
                 f'IF({pid}="","",{fetch("Products", "id", "name", pid)})',
                 26.0, "text"),
        calc_col("craft", "Craft",
                 f'IF({pid}="","",{fetch("Products", "id", "craft", pid)})',
                 13.0, "text"),
        material_col(note="Which material this line uses."),
        calc_col("material_name", "Material",
                 f'IF({mid}="","",{fetch("Materials", "id", "name", mid)})',
                 30.0, "text"),
        calc_col("unit", "Unit",
                 f'IF({mid}="","",{fetch("Materials", "id", "unit", mid)})',
                 9.0, "text"),
        calc_col("unit_cost", "Cost a unit",
                 f'IF({mid}="",0,{fetch("Materials", "id", "unit_cost", mid, "0")})',
                 12.0, "money4",
                 note="Straight from the Materials tab."),
        num_col("qty", "Qty an item", 11.0,
                note="How much one finished item takes, in the unit above."),
        pct_col("scrap_pct", "Scrap %", 10.0,
                note="Cutting loss, spills, ends that cannot be used."),
        calc_col("qty_with_scrap", "Qty with scrap",
                 f'IF({empty},"",{qty}*(1+{scrap}))', 11.0, "number",
                 note="What actually has to come off the shelf."),
        calc_col("cost", "Line cost",
                 f'IF({empty},"",{cost})', 12.0, "money",
                 note="Qty with scrap times the unit cost."),
        calc_col("batch_cost", "Cost a batch",
                 f'IF({empty},"",{cost}*DefaultBatchSize)', 12.0, "money",
                 note="The default batch size on Settings."),
        list_col_inline("source", "Source", SOURCES, 17.0,
                        note="Where this line came from."),
        calc_col("duplicate_flag", "Check",
                 f'IF({empty},"",IF(COUNTIFS({{product_first}}:{{product_last}},'
                 f'{pid},{{material_first}}:{{material_last}},{mid})>1,'
                 f'"DUPLICATE",""))', 12.0, "status",
                 note="The same material twice on one product doubles the cost.",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "DUPLICATE", "fmt": "bold_bad"}]),
        calc_col("products_sharing", "Products sharing it",
                 f'IF({mid}="","",COUNTIFS({{material_first}}:{{material_last}},{mid}))',
                 11.0, "int"),
        calc_col("rank_for_print", "rank for print",
                 f'IF(OR({pid}="",PrintProduct=""),{NO_MATCH},'
                 f'IF({pid}<>PrintProduct,{NO_MATCH},'
                 f'COUNTIFS({{product_first}}:{{product_last}},PrintProduct,'
                 f'{{id_first}}:{{id_last}},"<="&{row_ref("id")})))',
                 9.0, "int", hidden=True,
                 note="Hidden - the Print Costing sheet lists a product's "
                      "bill of materials from this."),
        calc_col("rank_cost", "rank cost", rank_desc("cost"), 9.0, "int",
                 hidden=True),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary_mid))
