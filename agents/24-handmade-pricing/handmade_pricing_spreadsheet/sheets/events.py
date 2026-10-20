"""The Events tab - fairs, markets and pop-ups, costed properly.

A craft fair looks profitable at four in the afternoon with an empty table.
This tab costs the whole day: the table fee, the travel, the nights away, the
hours setting up and the hours standing there at your own loaded rate, the card
fees, the packaging, and what the items that sold actually cost you.

`profit_an_hour` is the figure that decides whether to book again - a fair that
takes 600 and pays 400 for fourteen hours on its feet is paying less than the
minimum wage, and the stock left over does not change that. `sell_through`
shows how much of what you loaded in the van came home again.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, id_col, int_col, list_col, money_col,
                     num_col, rank_desc, row_ref, samples, spec_defaults,
                     text_col, wrap_col)

P = Palette

NAME = "Events"

SUBTITLE = ("Fairs, markets and pop-ups: what the day cost, what it took, and "
            "what it paid an hour.")

HELP = ("One row per event. Type the fees, the travel and the hours; the "
        "labour cost, card fees and packaging are calculated, and so is the "
        "profit an hour - the number that decides whether to book it again.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    eid = row_ref("id")
    has_id = f'{eid}=""'
    setup = f"N({row_ref('setup_hours')})"
    staff = f"N({row_ref('staff_hours')})"
    revenue = f"N({row_ref('revenue')})"
    units = f"N({row_ref('units_sold')})"
    hours = f"({setup}+{staff})"
    card_fees = (f'({revenue}*(ProcessingPercent+TransactionFee)'
                 f'+{units}*ProcessingFixed)')
    total_cost = (f'N({row_ref("table_fee")})+N({row_ref("travel")})'
                  f'+N({row_ref("accommodation")})+N({row_ref("labor_cost")})'
                  f'+N({row_ref("card_fees")})'
                  f'+N({row_ref("packaging_cost")})+N({row_ref("cogs")})')

    cols: List[Any] = [
        id_col("PrefixEvent", trigger="name", width=11.0),
        text_col("name", "Event", 32.0,
                 note="What it is called. Filling this in starts the row."),
        list_col("type", "Type", "EventTypeList", 16.0),
        list_col("status", "Status", "EventStatusList", 13.0),
        date_col("date", "Date", 13.0),
        date_col("end_date", "Ends", 13.0),
        int_col("days", "Days", 8.0),
        text_col("location", "Where", 24.0),
        money_col("table_fee", "Table fee", 12.0),
        money_col("travel", "Travel & fuel", 12.0),
        money_col("accommodation", "Nights away", 13.0),
        num_col("setup_hours", "Setup hours", 11.0,
                note="Your own hours: loading in, setting up, packing down."),
        num_col("staff_hours", "Staff hours", 11.0,
                note="Anyone else on the table, paid or not."),
        calc_col("total_hours", "Total hours",
                 f'IF({has_id},"",{hours})', 11.0, "number1"),
        calc_col("labor_cost", "Labour cost",
                 f'IF({has_id},"",{setup}*LaborCostHour+{staff}*EmployeeRate'
                 f'*(1+PayrollBurden))', 12.0, "money",
                 note="Your hours at the loaded rate, staff hours at the "
                      "employee rate on Settings."),
        calc_col("card_fees", "Card fees",
                 f'IF({has_id},"",{card_fees})', 12.0, "money",
                 note="The reader's percentage plus the fixed part per sale."),
        int_col("units_sold", "Units sold", 11.0),
        money_col("revenue", "Revenue", 13.0,
                  note="Everything the table took, before fees."),
        money_col("cogs", "Cost of what sold", 14.0,
                  note="What the items that sold cost you to make - not the "
                       "whole van load."),
        calc_col("cogs_check", "Cost check",
                 f'IF({has_id},"",IF(AND({units}>0,N({row_ref("cogs")})=0),'
                 f'"NO COST TYPED FOR WHAT SOLD",""))', 22.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "NO COST", "fmt": "warn"}]),
        calc_col("packaging_cost", "Packaging",
                 f'IF({has_id},"",{units}*DefaultPackaging)', 12.0, "money"),
        money_col("inventory_cost", "Value of stock taken", 15.0,
                  note="What the van load is worth - information, not a cost."),
        money_col("inventory_left", "Value brought home", 15.0),
        calc_col("sell_through", "Sold of what you took",
                 f'IF({has_id},"",IF(N({row_ref("inventory_cost")})=0,"",'
                 f'(N({row_ref("inventory_cost")})'
                 f'-N({row_ref("inventory_left")}))'
                 f'/N({row_ref("inventory_cost")})))', 13.0, "percent"),
        calc_col("total_cost", "Total cost",
                 f'IF({has_id},"",{total_cost})', 13.0, "money"),
        calc_col("profit", "Profit",
                 f'IF({has_id},"",{revenue}-{total_cost})', 13.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({has_id},"",IF({revenue}=0,"",'
                 f'({revenue}-{total_cost})/{revenue}))', 10.0, "percent"),
        calc_col("revenue_an_hour", "Revenue an hour",
                 f'IF({has_id},"",IF({hours}=0,"",{revenue}/{hours}))',
                 12.0, "money"),
        calc_col("profit_an_hour", "Profit an hour",
                 f'IF({has_id},"",IF({hours}=0,"",'
                 f'({revenue}-{total_cost})/{hours}))', 13.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("cost_a_unit", "Cost a unit sold",
                 f'IF({has_id},"",IF({units}=0,"",{total_cost}/{units}))',
                 12.0, "money"),
        calc_col("verdict", "Book again?",
                 f'IF(OR({has_id},{revenue}=0),"",'
                 f'IF({revenue}-{total_cost}<0,"LOST MONEY",'
                 f'IF(({revenue}-{total_cost})/{hours}<MinimumWage,'
                 f'"BELOW THE MINIMUM WAGE","WORTH BOOKING")))', 24.0,
                 "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOST", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "WORTH", "fmt": "good"}]),
        calc_col("rank_profit", "rank profit", rank_desc("profit"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
