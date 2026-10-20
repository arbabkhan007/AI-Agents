"""The Development tab - what it costs to bring something new to market.

A new product is not free before its first sale: pattern drafting, samples,
materials, testing, photography, a photographer, a licence. This tab keeps that
spend in one place, against the hours planned and the hours actually taken, and
sets it next to the target cost and target price the product is aiming at.

`viability` answers the question before the money is spent: at the target price
and the target cost, does the product clear the margin on Settings?
`sales_to_recover` says how many it has to sell before the development spend
comes back - the number that decides whether a new line is worth starting.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, fetch, id_col, list_col, money_col,
                     num_col, product_col, rank_desc, row_ref, samples,
                     spec_defaults, text_col, wrap_col)

P = Palette

NAME = "Development"

SUBTITLE = ("New products, patterns and process work: what it cost, how long "
            "it took, and whether the idea stands up.")

HELP = ("One row per project. Type the hours and the spend as they happen; "
        "the target cost and target price decide whether the idea clears your "
        "margin, and how many sales pay the development back.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    did = row_ref("id")
    has_id = f'{did}=""'
    product = row_ref("product")
    planned = f"N({row_ref('hours_planned')})"
    actual = f"N({row_ref('hours_actual')})"
    spend = (f'N({row_ref("labor_cost")})+N({row_ref("material_cost")})'
             f'+N({row_ref("outsourcing")})')
    target_cost = f"N({row_ref('target_cost')})"
    target_price = f"N({row_ref('target_price')})"
    per_unit = f"({target_price}-{target_cost})"

    cols: List[Any] = [
        id_col("PrefixDevelopment", trigger="name", width=11.0),
        text_col("name", "Project", 32.0,
                 note="What you are developing. Filling this in starts the row."),
        list_col("type", "Type", "DevTypeList", 15.0),
        product_col(note="The catalog product it belongs to, if it has one "
                         "yet."),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        list_col("stage", "Stage", "DevStageList", 14.0),
        date_col("start", "Started", 13.0),
        date_col("due", "Due", 13.0),
        calc_col("days_left", "Days left",
                 f'IF(OR({has_id},{row_ref("due")}=""),"",'
                 f'N({row_ref("due")})-TodayDate)', 11.0, "int",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bad"}]),
        list_col("status", "Status", "DevStatusList", 13.0),
        calc_col("schedule_flag", "Schedule",
                 f'IF(OR({has_id},{row_ref("due")}=""),"",'
                 f'IF(AND(TodayDate>N({row_ref("due")}),'
                 f'NOT(EXACT(TRIM({row_ref("status")}),"Done"))),"OVERDUE",'
                 f'IF(N({row_ref("due")})-TodayDate<=7,"DUE SOON","ON TRACK")))',
                 13.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVERDUE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "DUE SOON", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "ON TRACK", "fmt": "good"}]),
        num_col("hours_planned", "Hours planned", 12.0),
        num_col("hours_actual", "Hours actual", 12.0),
        calc_col("hours_variance", "Hours variance",
                 f'IF({has_id},"",{actual}-{planned})', 12.0, "number1",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "warn"}]),
        calc_col("hours_flag", "Hours check",
                 f'IF({has_id},"",IF({planned}=0,"",'
                 f'IF({actual}>{planned}*1.2,"OVER BUDGET",'
                 f'IF({actual}<{planned}*0.8,"UNDER BUDGET","ON BUDGET"))))',
                 14.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVER", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "ON BUDGET", "fmt": "good"}]),
        calc_col("labor_cost", "Labour cost",
                 f'IF({has_id},"",{actual}*LaborCostHour)', 12.0, "money",
                 note="Your hours at the loaded rate on Settings."),
        money_col("material_cost", "Materials & samples", 13.0),
        money_col("outsourcing", "Outside work", 13.0,
                  note="Photographer, tech editor, pattern grader, printing."),
        calc_col("total_spend", "Total spend",
                 f'IF({has_id},"",{spend})', 13.0, "money"),
        money_col("target_cost", "Target cost a unit", 13.0,
                  note="What one item should cost once it is in production."),
        money_col("target_price", "Target price", 13.0,
                  note="What it should sell for."),
        calc_col("target_margin", "Target margin",
                 f'IF({has_id},"",IF({target_price}=0,"",'
                 f'{per_unit}/{target_price}))', 12.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("viability", "Viability",
                 f'IF(OR({has_id},{target_price}=0),"",'
                 f'IF({per_unit}<=0,"LOSES MONEY EVERY SALE",'
                 f'IF({per_unit}/{target_price}<TargetRetailMargin,'
                 f'"WILL NOT MEET THE TARGET","VIABLE")))', 24.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOSES", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "WILL NOT", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "VIABLE", "fmt": "good"}]),
        calc_col("sales_to_recover", "Sales to recover the spend",
                 f'IF(OR({has_id},{per_unit}<=0),"",'
                 f'ROUNDUP({spend}/{per_unit},0))', 14.0, "int",
                 note="How many it has to sell before the development money "
                      "comes back."),
        calc_col("spend_a_unit", "Spend a unit",
                 f'IF(OR({has_id},{row_ref("sales_to_recover")}=""),"",'
                 f'{spend}/N({row_ref("sales_to_recover")}))', 12.0, "money4"),
        calc_col("rank_spend", "rank spend", rank_desc("total_spend"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
