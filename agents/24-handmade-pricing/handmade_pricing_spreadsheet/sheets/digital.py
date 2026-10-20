"""The Digital calculator.

A download is costed differently from anything else in the shop: it is made
once and sold as many times as it will sell, so the honest unit cost is the
whole investment spread over the units you expect to sell. That is what
`units_forecast` is for, and `cost_a_sale` is the figure the shared craft tail
treats as the material cost.

Minutes a sale are zero, on purpose. The labour went in up front and is inside
`creation_cost`; counting it again on every download would double count it, and
it would make a pattern look like it pays an hourly wage when what it really
does is earn money while you sleep. `break_even_units` is the number that
matters here: how many sales it takes to get the making of the file back.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, craft_tail, date_col, fetch, id_col, int_col,
                     list_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col)

P = Palette

NAME = "Digital"

SUBTITLE = ("Downloads: what a pattern or printable cost to make, spread over "
            "the sales you expect, and when it breaks even.")

HELP = ("Type the hours it took to create the file and how many sales you "
        "expect. The cost a sale, the price your margin asks for and the "
        "number of sales that pays the file back are all calculated.")

#: what a forecast falls back to when nothing is typed
FORECAST_DEFAULT = 100


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    did = row_ref("id")
    has_id = f'{did}=""'
    product = row_ref("product")
    units = (f'IF(N({row_ref("units_forecast")})=0,{FORECAST_DEFAULT},'
             f'N({row_ref("units_forecast")}))')

    material_expr = f'N({row_ref("cost_a_sale")})'

    cols: List[Any] = [
        id_col("PrefixDigital", trigger="file_name", width=11.0),
        date_col("date", "Date published", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        text_col("file_name", "File / title", 30.0,
                 note="What the download is. Filling this in starts the row."),
        list_col("type", "Type", "DigitalTypeList", 16.0),
        list_col("format", "Format", "DigitalFormatList", 11.0),
        int_col("pages", "Pages / files", 11.0),
        num_col("creation_hours", "Hours to create", 12.0,
                note="Writing, photographing, laying out, testing - the whole "
                     "job, once."),
        int_col("units_forecast", "Sales expected", 12.0,
                note=f"Blank assumes {FORECAST_DEFAULT} sales."),
        calc_col("units_used", "Sales used",
                 f'IF({has_id},"",{units})', 11.0, "int"),
        calc_col("creation_cost", "Cost to create",
                 f'IF({has_id},"",N({row_ref("creation_hours")})'
                 f'*LaborCostHour)', 13.0, "money",
                 note="Your hours at the loaded rate on Settings."),
        money_col("software_cost", "Software & assets", 13.0,
                  note="Fonts, mockups, stock, a plugin licence - the total "
                       "for this file."),
        money_col("hosting_cost", "Hosting & tools", 13.0,
                  note="Share of the store subscription and file hosting."),
        calc_col("total_investment", "Total investment",
                 f'IF({has_id},"",N({row_ref("creation_cost")})'
                 f'+N({row_ref("software_cost")})'
                 f'+N({row_ref("hosting_cost")}))', 13.0, "money"),
        calc_col("cost_a_sale", "Cost a sale",
                 f'IF({has_id},"",N({row_ref("total_investment")})/{units})',
                 12.0, "money4",
                 note="The whole investment spread over the sales you expect."),
        calc_col("minutes", "Minutes a sale",
                 f'IF({has_id},"",0)', 11.0, "number1",
                 note="Zero on purpose: a download takes no time per sale. "
                      "The labour is already inside the cost a sale."),
        calc_col("break_even_units", "Sales to break even",
                 f'IF({has_id},"",IF(N({row_ref("price")})=0,"",'
                 f'ROUNDUP(N({row_ref("total_investment")})'
                 f'/N({row_ref("price")}),0)))', 13.0, "int",
                 note="How many sales pay the file back at today's price."),
        money_col("price", "Price today", 12.0),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0),
        wrap_col("notes", "Notes", 30.0),
    ]
    cols += craft_tail(material_expr, has_difficulty=False)

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
