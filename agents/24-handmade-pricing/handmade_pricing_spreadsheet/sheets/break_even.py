"""The Profit & Break-Even tab.

How many of a product you have to sell before the month pays for itself. The
arithmetic is the one that matters for a one person shop:

    contribution an item = price - channel fees - unit cost
    break even units     = fixed costs a month / contribution an item

Fixed costs here are the real ones - the overhead total, every subscription on
the Channels tab, the shop time recorded on the Labor tab that is not on one
product, and any marketing you type in. Variable costs are the ones that move
with each sale.

`margin of safety` is how far sales can fall before the month goes under, and
the sensitivity strip at the bottom shows what a 10% price cut or a 10% cost
rise does to the break even number - usually more than people expect.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..config import VOLUME_STEPS, Config, Palette
from ..layout import lookup
from ..writer import SheetWriter, list_from
from .common import channel_fee_rate, channel_fixed_fee, other

P = Palette

NAME = "Profit & Break-Even"

SUBTITLE = ("How many you have to sell to cover the month, and what different "
            "volumes earn.")

HELP = ("Pick a product. Its price, cost and fees arrive from the catalog; "
        "the fixed costs arrive from Overhead, Channels and Labor. Type a "
        "marketing spend if you have one.")


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=True)
    last_col = 13
    sheet.banner(NAME, SUBTITLE, last_col, badge="Break-even")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 30.0)
    sheet.set_col(3, 4, 15.0)
    sheet.set_col(5, last_col, 13.0)
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

    prod = lambda key: lookup("BeProduct", other("Products", "id"),
                              other("Products", key))
    channel_of = f'IFERROR({prod("channel")},DefaultChannel)'
    r = sheet.note(3, HELP, last_col, height=30)

    # ------------------------------------------------------------- the product
    r = sheet.section(r, "1. The product", last_col)
    r = f(r, "Product", name="BeProduct", input_cell=True,
          validate=list_from("ProductIDs"))
    r = f(r, "Product name", formula=f'=IFERROR({prod("name")},"")')
    r = f(r, "Price", name="BePrice", style="money",
          formula=f'=IFERROR({prod("retail_price")},0)')
    r = f(r, "Cost of one item", name="BeUnitCost", style="money",
          formula=f'=IFERROR({prod("total_cost")},0)')
    r = f(r, "Minutes an item", name="BeMinutes", style="number1",
          formula=f'=IFERROR({prod("minutes_used")},0)')
    r = f(r, "Fee rate", name="BeFeeRate", style="percent",
          formula=f"={channel_fee_rate(channel_of)}")
    r = f(r, "Fixed fees an order", name="BeFixedFees", style="money",
          formula=f"={channel_fixed_fee(channel_of)}")
    r = sheet.field(r, "Contribution an item", None, label_col=1, value_col=3,
                    value_end=4, style="money", name="BeContribution",
                    formula="=IF(N(BePrice)=0,0,N(BePrice)"
                            "-(N(BeFeeRate)*N(BePrice)+N(BeFixedFees))"
                            "-N(BeUnitCost))",
                    help_text="Price less the channel fees less the cost. "
                              "This is what each sale puts towards the fixed "
                              "costs.")
    r = _rule(sheet, fmts, r, 1, 4)
    r = f(r, "Contribution margin", style="percent",
          formula='=IF(N(BePrice)=0,"",N(BeContribution)/N(BePrice))')
    r += 1

    # ------------------------------------------------------------ fixed costs
    r = sheet.section(r, "2. What the month costs whatever you sell",
                      last_col)
    r = f(r, "Overhead a month", name="BeOverhead", style="money",
          formula="=OverheadMonthly",
          help_text="The allocated rows of the Overhead tab.")
    r = f(r, "Subscriptions a month", name="BeSubscriptions", style="money",
          formula=f"=IFERROR(SUM({other('Channels', 'subscription')}),0)")
    r = f(r, "Shop time this month", name="BeShopTime", style="money",
          formula=(f"=IFERROR(SUMIFS({other('Labor', 'overhead_share')},"
                   f"{other('Labor', 'date')},\">=\"&MonthStart,"
                   f"{other('Labor', 'date')},\"<=\"&MonthEnd),0)"),
          help_text="Hours on the Labor tab with no product against them.")
    r = f(r, "Marketing this month", name="BeMarketing", style="money",
          input_cell=True, value=0,
          help_text="Ads, a photographer, a fair table fee - anything you "
                    "spend to get sales.")
    r = sheet.field(r, "Fixed costs a month", None, label_col=1, value_col=3,
                    value_end=4, style="money", name="BeFixed",
                    formula="=N(BeOverhead)+N(BeSubscriptions)"
                            "+N(BeShopTime)+N(BeMarketing)")
    r = _rule(sheet, fmts, r, 1, 4)
    r += 1

    # ------------------------------------------------------------- break even
    r = sheet.section(r, "3. Break-even", last_col)
    r = sheet.field(r, "Units to break even", None, label_col=1, value_col=3,
                    value_end=4, style="int", name="BeUnits",
                    formula='=IF(N(BeContribution)<=0,"NEVER - IT DOES NOT '
                            'CONTRIBUTE",ROUNDUP(N(BeFixed)'
                            '/N(BeContribution),0))',
                    help_text="Fixed costs divided by the contribution an item.")
    r = _rule(sheet, fmts, r, 1, 4)
    r = f(r, "Revenue at break-even", name="BeRevenue", style="money",
          formula='=IF(N(BeUnits)=0,"",N(BeUnits)*N(BePrice))')
    r = f(r, "Hours at break-even", style="number",
          formula='=IF(N(BeUnits)=0,"",N(BeUnits)*N(BeMinutes)/60)',
          help_text="How much of your month that is, at the productive hours "
                    "on Settings.")
    r = f(r, "Share of your productive hours", style="percent",
          formula='=IF(OR(N(BeUnits)=0,ProductiveHours<=0),"",'
                  'N(BeUnits)*N(BeMinutes)/60/ProductiveHours)')
    r = f(r, "Sold this month", name="BeUnitsNow", style="int",
          formula=(f"=IFERROR(SUMIFS({other('Sales', 'qty')},"
                   f"{other('Sales', 'product')},BeProduct,"
                   f"{other('Sales', 'date')},\">=\"&MonthStart,"
                   f"{other('Sales', 'date')},\"<=\"&MonthEnd),0)"))
    r = f(r, "Profit this month", name="BeProfitNow", style="money",
          formula="=N(BeUnitsNow)*N(BeContribution)-N(BeFixed)")
    r = f(r, "Margin of safety", name="BeSafety", style="percent",
          formula='=IF(N(BeUnitsNow)=0,"",(N(BeUnitsNow)-N(BeUnits))'
                  '/N(BeUnitsNow))',
          help_text="How far sales can fall before the month goes under.")
    r = f(r, "Verdict", style="text",
          formula='=IF(N(BeUnitsNow)=0,"NOTHING SOLD YET",'
                  'IF(N(BeProfitNow)>=MonthlyProfitTarget,"ABOVE THE PROFIT '
                  'TARGET",IF(N(BeProfitNow)>=0,"COVERING ITS COSTS",'
                  'IF(N(BeUnitsNow)>=N(BeUnits)*0.75,"CLOSE - PUSH A LITTLE '
                  'MORE","NOT COVERING THE MONTH"))))')
    r += 1

    # ---------------------------------------------------------- volume table
    r = sheet.section(r, "4. What different volumes earn in a month", last_col)
    headers = ["Units", "Revenue", "Fees", "Cost of goods", "Contribution",
               "Profit"]
    sheet.row_height(r, 20)
    for i, head in enumerate(headers):
        col = 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    volumes = list(VOLUME_STEPS) + ["Break-even", "Sold this month"]
    for step in volumes:
        units = (f"N(BeUnits)" if step == "Break-even"
                 else f"N(BeUnitsNow)" if step == "Sold this month"
                 else str(step))
        revenue = f"N(BePrice)*{units}"
        fees = f"N(BeFeeRate)*{revenue}+N(BeFixedFees)*{units}"
        cogs = f"N(BeUnitCost)*{units}"
        contribution = f"N(BeContribution)*{units}"
        profit = f"{contribution}-N(BeFixed)"
        sheet.row_height(r, 18)
        label = str(step)
        sheet.ws.merge_range(r, 1, r, 2, "", fmts.cell("int", "plain"))
        sheet.formula(r, 1, f"={units}", fmts.cell("int", "plain"))
        for i, formula in enumerate([revenue, fees, cogs, contribution,
                                     profit]):
            col = 3 + i * 2
            sheet.ws.merge_range(r, col, r, col + 1, "",
                                 fmts.cell("money", "plain"))
            sheet.formula(r, col, "=" + formula,
                                   fmts.cell("money", "plain"))
        sheet.ws.conditional_format(
            r, 11, r, 12,
            {"type": "cell", "criteria": "<", "value": 0,
             "format": fmts.cf("bold_bad")})
        r += 1
    r += 1

    # ----------------------------------------------------------- sensitivity
    r = sheet.section(r, "5. What changes the break-even number", last_col)
    sheet.row_height(r, 20)
    for i, head in enumerate(["If this happens", "Contribution",
                              "Units to break even", "Change"]):
        col = 1 + i * 3
        sheet.merge(r, col, col + 2, head, fmts.chrome("header_left"))
    r += 1
    cases = [
        ("As it stands", "N(BePrice)", "N(BeUnitCost)"),
        ("Price 10% lower", "N(BePrice)*0.9", "N(BeUnitCost)"),
        ("Price 10% higher", "N(BePrice)*1.1", "N(BeUnitCost)"),
        ("Costs 10% higher", "N(BePrice)", "N(BeUnitCost)*1.1"),
        ("Costs 10% lower", "N(BePrice)", "N(BeUnitCost)*0.9"),
        ("Both go against you", "N(BePrice)*0.9", "N(BeUnitCost)*1.1"),
    ]
    for label, price, cost in cases:
        contribution = (f"({price}-(N(BeFeeRate)*{price}+N(BeFixedFees))"
                        f"-{cost})")
        units = (f'IF({contribution}<=0,"NEVER",'
                 f'ROUNDUP(N(BeFixed)/{contribution},0))')
        sheet.row_height(r, 18)
        sheet.ws.merge_range(r, 1, r, 3, label, fmts.cell("text", "plain"))
        sheet.ws.merge_range(r, 4, r, 6, "", fmts.cell("money", "plain"))
        sheet.formula(r, 4, "=" + contribution,
                               fmts.cell("money", "plain"))
        sheet.ws.merge_range(r, 7, r, 9, "", fmts.cell("int", "plain"))
        sheet.formula(r, 7, "=" + units, fmts.cell("int", "plain"))
        sheet.ws.merge_range(r, 10, r, 12, "", fmts.cell("percent", "plain"))
        sheet.formula(
            r, 10, f'=IFERROR(IF(N(BeUnits)=0,"",{units}/N(BeUnits)-1),"")',
            fmts.cell("percent", "plain"))
        r += 1
    r += 1
    r = sheet.note(
        r,
        "Read the last column as 'how many more I would have to sell'. A 10% "
        "price cut on a product with a thin contribution typically asks for "
        "half as many sales again - which is why discounting is a volume "
        "decision before it is a marketing one.",
        last_col, height=44)

    sheet.ws.freeze_panes(4, 0)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet


def _rule(sheet, fmts, row: int, first_col: int, last_col: int) -> int:
    """Rule under a total, drawn on the blank row below it. Returns the next
    free row so the total above is never overwritten."""
    sheet.row_height(row, 7)
    for col in range(first_col, last_col + 1):
        sheet.ws.write_blank(row, col, None, fmts.chrome("rule"))
    return row + 1
