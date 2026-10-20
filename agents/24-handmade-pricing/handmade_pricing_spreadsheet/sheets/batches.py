"""The Batches tab - what a run of making actually cost.

A batch is the honest check on a catalog cost. The Products tab says what one
item *should* cost from the bill of materials and the standard minutes; this
tab says what the run of twelve actually cost, including the jar that cracked,
the board that warped and the extra hour the finishing took.

`material_variance` is the difference between the two, and `cost_check` says
whether the batch came out above or below the catalog figure. A batch that
keeps coming out above is a bill of materials that is wrong, a supplier price
that moved, or a defect rate that is higher than the one on Settings - all
three are worth knowing before the price is set from the wrong number.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_packaging, date_col, fetch, id_col,
                     int_col, money_col, num_col, other, product_col,
                     rank_desc, row_ref, samples, spec_defaults, sumifs,
                     wrap_col)

P = Palette

NAME = "Batches"

SUBTITLE = ("Runs of making: what a batch cost, what one item came out at, "
            "and how that compares with the catalog cost.")

HELP = ("One row per run. Type what the materials cost and how long it took; "
        "the labour, overhead and packaging are calculated, and so is the "
        "cost of one sellable item once the defects are taken out.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    bid = row_ref("id")
    has_id = f'{bid}=""'
    product = row_ref("product")
    planned = f"N({row_ref('qty_planned')})"
    done = f"N({row_ref('qty_done')})"
    defect = f"N({row_ref('qty_defect')})"
    sellable = f"({done}-{defect})"
    minutes = f"N({row_ref('labor_minutes')})"
    labor_cost = f"{minutes}/60*LaborCostHour"
    packaging = craft_packaging(product)
    batch_cost = (f'N({row_ref("material_cost")})+{labor_cost}'
                  f'+N({row_ref("overhead")})+N({row_ref("packaging_cost")})')
    sold_since = sumifs(other("Sales", "qty"),
                        [(other("Sales", "product"), product),
                         (other("Sales", "date"),
                          '">="&N(' + row_ref("started") + ')')])

    cols: List[Any] = [
        id_col("PrefixBatch", trigger="product", width=11.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",{fetch("Products", "id", "name", product)})',
                 28.0, "text"),
        calc_col("craft", "Craft",
                 f'IF({product}="","",{fetch("Products", "id", "craft", product)})',
                 13.0, "text"),
        date_col("started", "Started", 13.0),
        date_col("finished", "Finished", 13.0),
        calc_col("days_taken", "Days taken",
                 f'IF(OR({has_id},{row_ref("started")}="",'
                 f'{row_ref("finished")}=""),"",'
                 f'N({row_ref("finished")})-N({row_ref("started")}))',
                 11.0, "int"),
        int_col("qty_planned", "Planned", 10.0),
        int_col("qty_done", "Made", 10.0),
        int_col("qty_defect", "Defects", 10.0,
                note="Pieces that cannot be sold: cracks, warping, missed "
                     "stitches, failed test burns."),
        calc_col("qty_sellable", "Sellable",
                 f'IF({has_id},"",{sellable})', 10.0, "int"),
        calc_col("completion", "Made of planned",
                 f'IF({has_id},"",IF({planned}=0,"",{done}/{planned}))',
                 12.0, "percent"),
        calc_col("defect_rate", "Defect rate",
                 f'IF({has_id},"",IF({done}=0,"",{defect}/{done}))', 11.0,
                 "percent"),
        calc_col("defect_flag", "Defect check",
                 f'IF(OR({has_id},{row_ref("defect_rate")}=""),"",'
                 f'IF(N({row_ref("defect_rate")})>DefaultDefect,'
                 f'"ABOVE THE TARGET",IF({defect}=0,"CLEAN","OK")))',
                 17.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "ABOVE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "CLEAN", "fmt": "good"}]),
        money_col("material_cost", "Materials (typed)", 13.0,
                  note="What the materials for this batch really cost."),
        calc_col("expected_material", "Materials (expected)",
                 f'IF({has_id},"",{planned}*'
                 f'{fetch("Products", "id", "material_cost", product, "0")})',
                 13.0, "money",
                 note="Planned units times the catalog material cost."),
        calc_col("material_variance", "Variance",
                 f'IF({has_id},"",N({row_ref("material_cost")})'
                 f'-N({row_ref("expected_material")}))', 12.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "warn"},
                     {"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "good"}]),
        num_col("labor_minutes", "Minutes (whole batch)", 13.0),
        calc_col("minutes_a_unit", "Minutes an item",
                 f'IF({has_id},"",IF({sellable}<=0,"",{minutes}/{sellable}))',
                 12.0, "number1"),
        calc_col("labor_cost", "Labour cost",
                 f'IF({has_id},"",{labor_cost})', 12.0, "money"),
        calc_col("overhead", "Overhead",
                 f'IF({has_id},"",IF(OverheadMethod="Per hour",'
                 f'{minutes}/60*OverheadPerHour,'
                 f'IF(OverheadMethod="Per unit",'
                 f'IF({sellable}<=0,0,{sellable}*OverheadPerUnit),'
                 f'IF(UnitsPerMonth<=0,0,'
                 f'{sellable}*OverheadMonthly/UnitsPerMonth))))', 12.0,
                 "money", note="Spread the way Settings says."),
        calc_col("packaging_cost", "Packaging",
                 f'IF({has_id},"",IF({sellable}<=0,0,{sellable}*{packaging}))',
                 12.0, "money"),
        calc_col("batch_cost", "Batch cost",
                 f'IF({has_id},"",{batch_cost})', 13.0, "money"),
        calc_col("cost_per_unit", "Cost an item",
                 f'IF({has_id},"",IF({sellable}<=0,"",{batch_cost}/{sellable}))',
                 13.0, "money",
                 note="The real cost of one sellable item from this run."),
        calc_col("catalog_cost", "Catalog cost",
                 f'IF({has_id},"",{fetch("Products", "id", "total_cost", product, "0")})',
                 12.0, "money",
                 note="What the Products tab thinks one item costs."),
        calc_col("cost_check", "Cost check",
                 f'IF(OR({has_id},{row_ref("cost_per_unit")}=""),"",'
                 f'IF(N({row_ref("cost_per_unit")})>'
                 f'N({row_ref("catalog_cost")})*1.05,'
                 f'"BATCH COSTS MORE THAN CATALOG",'
                 f'IF(N({row_ref("cost_per_unit")})<'
                 f'N({row_ref("catalog_cost")})*0.95,'
                 f'"CHEAPER THAN CATALOG","MATCHES")))', 26.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "MORE THAN", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "CHEAPER", "fmt": "info"},
                     {"type": "text", "criteria": "containing",
                      "value": "MATCHES", "fmt": "good"}]),
        int_col("cure_days", "Cure / rest days", 12.0,
                note="Candles cure, glue and oil dry, dye sets."),
        calc_col("ready_date", "Ready to sell",
                 f'IF(OR({has_id},{row_ref("finished")}=""),"",'
                 f'N({row_ref("finished")})+N({row_ref("cure_days")}))',
                 13.0, "date"),
        calc_col("sold_since", "Sold since it started", sold_since, 12.0,
                 "int"),
        calc_col("left_from_batch", "Left from this batch",
                 f'IF({has_id},"",IF({sellable}<=0,"",'
                 f'{sellable}-N({row_ref("sold_since")})))', 13.0, "int"),
        calc_col("rank_cost", "rank cost", rank_desc("cost_per_unit"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
