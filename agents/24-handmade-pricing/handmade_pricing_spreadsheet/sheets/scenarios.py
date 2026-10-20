"""The Scenarios tab - the same product priced five ways.

One product, five target margins from the budget end of the market to luxury,
plus what it earns at the price you charge today. Same costs, same fees, same
hours - only the margin changes, so the difference between the columns is pure
pricing.

The point of the page is the two rows at the bottom. `Monthly revenue` and
`Monthly profit` multiply each price by the units a month on Settings, which
turns a percentage argument into money: a budget price that needs three times
the sales to earn the same is a different business, not just a different
number.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..config import PRICING_SCENARIOS, Config, Palette
from ..layout import lookup
from ..writer import SheetWriter, list_from
from .common import (channel_fee_rate, channel_fixed_fee, other, price_from,
                     round_price)

P = Palette

NAME = "Scenarios"

SUBTITLE = ("One product at five margins, side by side, with what each would "
            "earn over a month.")

HELP = ("Pick a product. Every column below is the same item at a different "
        "target margin; the last column is the price you charge today.")


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=True)
    scenarios = list(PRICING_SCENARIOS.items()) + [("At today's price", None)]
    columns = len(scenarios)
    last_col = 2 + columns * 2
    sheet.banner(NAME, SUBTITLE, last_col, badge="Pricing scenarios")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 30.0)
    for i in range(columns):
        sheet.set_col(3 + i * 2, 4 + i * 2, 14.0)
    sheet.ws.hide_gridlines(2)

    def f(row: int, label: str, *, formula: Optional[str] = None,
          value: Any = None, name: Optional[str] = None, style: str = "text",
          input_cell: bool = False, validate: Optional[Dict[str, Any]] = None,
          help_text: str = "") -> int:
        return sheet.field(row, label, value, label_col=1, value_col=3,
                           value_end=4, style=style,
                           mode="input" if input_cell else "calc",
                           name=name, validate=validate,
                           help_text=help_text, help_col=5, formula=formula)

    prod = lambda key: lookup("ScProduct", other("Products", "id"),
                              other("Products", key))
    channel_of = f'IFERROR({prod("channel")},DefaultChannel)'

    r = sheet.note(3, HELP, last_col, height=30)

    r = sheet.section(r, "1. The product", last_col)
    r = f(r, "Product", name="ScProduct", input_cell=True,
          validate=list_from("ProductIDs"))
    r = f(r, "Product name", formula=f'=IFERROR({prod("name")},"")')
    r = f(r, "Craft", formula=f'=IFERROR({prod("craft")},"")')
    r = f(r, "Cost of one item", name="ScCost", style="money",
          formula=f'=IFERROR({prod("total_cost")},0)')
    r = f(r, "Minutes an item", name="ScMinutes", style="number1",
          formula=f'=IFERROR({prod("minutes_used")},0)')
    r = f(r, "Fee rate", name="ScFeeRate", style="percent",
          formula=f"={channel_fee_rate(channel_of)}")
    r = f(r, "Fixed fees an order", name="ScFixedFees", style="money",
          formula=f"={channel_fixed_fee(channel_of)}")
    r = f(r, "Price today", name="ScPriceToday", style="money",
          formula=f'=IFERROR({prod("retail_price")},0)')
    r = f(r, "Units a month", name="ScUnits", style="int",
          formula="=UnitsPerMonth",
          help_text="From Settings - change it there to test a different "
                    "volume.")
    r += 1

    # --------------------------------------------------------- the comparison
    r = sheet.section(r, "2. The same item at every margin", last_col)
    header_row = r
    sheet.row_height(header_row, 30)
    sheet.merge(header_row, 1, 2, "Scenario", fmts.chrome("header_left"))
    for i, (label, _margin) in enumerate(scenarios):
        col = 3 + i * 2
        sheet.ws.merge_range(header_row, col, header_row, col + 1, label,
                             fmts.chrome("header"))
    r += 1

    def margin_expr(i: int) -> str:
        if scenarios[i][1] is None:
            return ('IF(N(ScPriceToday)=0,0,(N(ScPriceToday)'
                    '-(N(ScFeeRate)*N(ScPriceToday)+N(ScFixedFees))'
                    '-N(ScCost))/N(ScPriceToday))')
        return str(scenarios[i][1])

    def price_expr(i: int) -> str:
        if scenarios[i][1] is None:
            return "N(ScPriceToday)"
        return ("N(" + price_from("N(ScCost)", "N(ScFixedFees)",
                                  margin_expr(i), "N(ScFeeRate)") + ")")

    def profit_expr(i: int) -> str:
        price = price_expr(i)
        return (f"{price}-(N(ScFeeRate)*{price}+N(ScFixedFees))-N(ScCost)")

    rows: List[Tuple[str, str, Sequence[str]]] = [
        ("Target margin", "percent", [margin_expr(i) for i in range(columns)]),
        ("Price", "money", [price_expr(i) for i in range(columns)]),
        ("Profit an item", "money", [profit_expr(i) for i in range(columns)]),
        ("Margin after fees", "percent",
         [f'IF({price_expr(i)}=0,"",{profit_expr(i)}/{price_expr(i)})'
          for i in range(columns)]),
        ("Effective hourly", "money",
         [f'IF(N(ScMinutes)=0,"",({profit_expr(i)})/(N(ScMinutes)/60))'
          for i in range(columns)]),
        ("Wholesale price", "money",
         [round_price(f"{price_expr(i)}*(1-WholesaleDiscount)")
          for i in range(columns)]),
        ("Monthly revenue", "money",
         [f"{price_expr(i)}*N(ScUnits)" for i in range(columns)]),
        ("Monthly profit", "money",
         [f"({profit_expr(i)})*N(ScUnits)-0" for i in range(columns)]),
        ("Sales needed for the same profit", "number1",
         [f'IF({profit_expr(0)}<=0,"n/a",{profit_expr(0)}'
          f'/IF({profit_expr(i)}<=0,0.0001,{profit_expr(i)}))'
          for i in range(columns)]),
    ]

    for label, style, formulas in rows:
        sheet.row_height(r, 18)
        sheet.merge(r, 1, 2, label, fmts.chrome("label_bold"))
        for i, formula in enumerate(formulas):
            col = 3 + i * 2
            fmt = fmts.cell(style, "plain")
            sheet.ws.merge_range(r, col, r, col + 1, "", fmt)
            sheet.ws.write_formula(r, col,
                                   formula if formula.startswith("=")
                                   else "=" + formula, fmt)
        r += 1

    # verdict row
    sheet.row_height(r, 30)
    sheet.merge(r, 1, 2, "Verdict", fmts.chrome("label_bold"))
    for i in range(columns):
        col = 3 + i * 2
        verdict = (f'=IF(N({price_expr(i)})=0,"NO PRICE",'
                   f'IF({profit_expr(i)}<=0,"LOSES MONEY",'
                   f'IF(({profit_expr(i)})/(N(ScMinutes)/60+0.0001)'
                   f'<MinimumWage,"BELOW THE MINIMUM WAGE",'
                   f'IF(({profit_expr(i)})/N({price_expr(i)})'
                   f'<MarginWarning,"THIN MARGIN","WORKS"))))')
        if scenarios[i][1] is None:
            verdict = (f'=IF(N(ScPriceToday)=0,"NO PRICE",'
                       f'IF({profit_expr(i)}<=0,"LOSES MONEY",'
                       f'IF(N(ScMinutes)=0,"NO TIME RECORDED",'
                       f'IF(({profit_expr(i)})/(N(ScMinutes)/60)'
                       f'<MinimumWage,"BELOW THE MINIMUM WAGE",'
                       f'IF(({profit_expr(i)})/N(ScPriceToday)'
                       f'<MarginWarning,"THIN MARGIN","WORKS")))))')
        fmt = fmts.cell("status", "plain")
        sheet.ws.merge_range(r, col, r, col + 1, "", fmt)
        sheet.ws.write_formula(r, col, verdict, fmt)
        sheet.ws.conditional_format(
            r, col, r, col + 1,
            {"type": "text", "criteria": "containing", "value": "LOSES",
             "format": fmts.cf("bold_bad")})
        sheet.ws.conditional_format(
            r, col, r, col + 1,
            {"type": "text", "criteria": "containing", "value": "BELOW",
             "format": fmts.cf("warn")})
        sheet.ws.conditional_format(
            r, col, r, col + 1,
            {"type": "text", "criteria": "containing", "value": "WORKS",
             "format": fmts.cf("good")})
    r += 2

    r = sheet.note(
        r,
        "'Sales needed for the same profit' compares each column with the "
        "Budget market column: a figure of 3 means the budget price has to "
        "sell three times as many to earn what that column earns. That is the "
        "real cost of being the cheap option.",
        last_col, height=44)

    sheet.ws.freeze_panes(header_row + 1, 3)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet
