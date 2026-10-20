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

Every row below the price row reads the cells above it rather than repeating
the pricing model. That is how a spreadsheet should be built anyway, and it
also keeps each formula far inside Excel's 8,192 character limit - inlining
the model eight times over, once per row, runs past it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..config import PRICING_SCENARIOS, Config, Palette
from ..layout import col_letter, lookup
from ..writer import SheetWriter, list_from
from .common import (channel_fee_rate, channel_fixed_fee, other, price_from,
                     round_price)

P = Palette

NAME = "Scenarios"

SUBTITLE = ("One product at five margins, side by side, with what each would "
            "earn over a month.")

HELP = ("Pick a product. Every column below is the same item at a different "
        "target margin; the last column is the price you charge today.")

#: the rows of the comparison table, top to bottom
ROWS: Sequence[Tuple[str, str]] = (
    ("Target margin", "percent"),
    ("Price", "money"),
    ("Profit an item", "money"),
    ("Margin after fees", "percent"),
    ("Effective hourly", "money"),
    ("Wholesale price", "money"),
    ("Monthly revenue", "money"),
    ("Monthly profit", "money"),
    ("Sales needed for the same profit", "number1"),
)

MARGIN = "Target margin"
PRICE = "Price"
PROFIT = "Profit an item"
MARGIN_NET = "Margin after fees"
HOURLY = "Effective hourly"


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

    first = r
    row_of = {label: first + i for i, (label, _style) in enumerate(ROWS)}
    verdict_row = first + len(ROWS)

    def cell(label: str, i: int) -> str:
        """Absolute reference to one scenario column on one table row."""
        return f"${col_letter(3 + i * 2)}${row_of[label] + 1}"

    def put(row: int, i: int, formula: str, style: str) -> None:
        col = 3 + i * 2
        fmt = fmts.cell(style, "plain")
        sheet.ws.merge_range(row, col, row, col + 1, "", fmt)
        sheet.formula(row, col, formula, fmt)

    def margin_formula(i: int) -> str:
        if scenarios[i][1] is None:
            return ('=IF(N(ScPriceToday)=0,0,(N(ScPriceToday)'
                    '-(N(ScFeeRate)*N(ScPriceToday)+N(ScFixedFees))'
                    '-N(ScCost))/N(ScPriceToday))')
        return "=" + str(scenarios[i][1])

    def price_formula(i: int) -> str:
        if scenarios[i][1] is None:
            return "=N(ScPriceToday)"
        return "=" + price_from("N(ScCost)", "N(ScFixedFees)",
                                f"N({cell(MARGIN, i)})", "N(ScFeeRate)")

    # ------------------------------------------------------------- table rows
    for i in range(columns):
        put(row_of[MARGIN], i, margin_formula(i), "percent")
        put(row_of[PRICE], i, price_formula(i), "money")

    for i in range(columns):
        price = cell(PRICE, i)
        profit = cell(PROFIT, i)
        hourly = cell(HOURLY, i)
        net = cell(MARGIN_NET, i)
        base_profit = cell(PROFIT, 0)
        put(row_of[PROFIT], i,
            f"=N({price})-(N(ScFeeRate)*N({price})+N(ScFixedFees))-N(ScCost)",
            "money")
        put(row_of[MARGIN_NET], i,
            f'=IF(N({price})=0,"",N({profit})/N({price}))', "percent")
        put(row_of[HOURLY], i,
            f'=IF(N(ScMinutes)=0,"",N({profit})/(N(ScMinutes)/60))', "money")
        put(row_of["Wholesale price"], i,
            f'=IF(N({price})=0,"",'
            f'{round_price(f"N({price})*(1-WholesaleDiscount)")})', "money")
        put(row_of["Monthly revenue"], i, f"=N({price})*N(ScUnits)", "money")
        put(row_of["Monthly profit"], i, f"=N({profit})*N(ScUnits)", "money")
        put(row_of["Sales needed for the same profit"], i,
            f'=IF(N({base_profit})<=0,"n/a",N({base_profit})'
            f'/IF(N({profit})<=0,0.0001,N({profit})))', "number1")
        put(verdict_row, i,
            f'=IF(N({price})=0,"NO PRICE",'
            f'IF(N({profit})<=0,"LOSES MONEY",'
            f'IF(N(ScMinutes)=0,"NO TIME RECORDED",'
            f'IF(N({hourly})<MinimumWage,"BELOW THE MINIMUM WAGE",'
            f'IF(N({net})<MarginWarning,"THIN MARGIN","WORKS")))))', "status")

    # ---------------------------------------------------------- row furniture
    for label, _style in ROWS:
        row = row_of[label]
        sheet.row_height(row, 18)
        bold = label in (PRICE, PROFIT)
        sheet.merge(row, 1, 2, label,
                    fmts.chrome("label_bold" if bold else "label"))
    sheet.row_height(verdict_row, 30)
    sheet.merge(verdict_row, 1, 2, "Verdict", fmts.chrome("label_bold"))
    for i in range(columns):
        col = 3 + i * 2
        for word, kind in (("LOSES", "bold_bad"), ("BELOW", "warn"),
                           ("WORKS", "good")):
            sheet.ws.conditional_format(
                verdict_row, col, verdict_row, col + 1,
                {"type": "text", "criteria": "containing", "value": word,
                 "format": fmts.cf(kind)})
    r = verdict_row + 2

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
