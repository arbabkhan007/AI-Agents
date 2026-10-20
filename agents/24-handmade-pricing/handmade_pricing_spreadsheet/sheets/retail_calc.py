"""The Retail Calculator - one product, priced from scratch, on one screen.

Pick a product and every cost arrives from the registers; or type costs into
the cream cells and cost something that does not exist yet. The page then walks
down the model one step at a time - materials, labour at your real hourly cost,
packaging, the postage you absorb, overhead, the channel's fees - and lands on
the price your target margin asks for, next to the price you charge now.

The strip at the bottom prices the same item at five margins, so the cost of
being the cheap option is visible in money rather than in percentages.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..config import PRICING_SCENARIOS, Config, Palette
from ..layout import lookup
from ..writer import SheetWriter, list_from
from .common import (channel_fee_rate, channel_fixed_fee, other, price_from,
                     round_price)

P = Palette

NAME = "Retail Calculator"

SUBTITLE = ("Price one item step by step: costs, fees, the price your margin "
            "asks for, and what it really earns.")

HELP = ("Pick a product and its costs arrive from the catalog. Or type into "
        "the cream cells to cost something that does not exist yet - a "
        "prototype, a custom order, a new design.")

#: names this page defines, in the order they appear
NAMES = ["RcProduct", "RcChannel", "RcChannelUsed", "RcMaterials",
         "RcMinutes", "RcLabour", "RcPackaging", "RcPostage", "RcOverhead",
         "RcCost", "RcFeeRate", "RcFixed", "RcMargin", "RcMarginUsed",
         "RcCatalogPrice", "RcPrice", "RcPriceUsed", "RcSuggested",
         "RcFeesAtPrice", "RcProfit", "RcMarginNow", "RcHourly",
         "RcWholesale"]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=False)
    last_col = 10
    sheet.banner(NAME, SUBTITLE, last_col, badge="Retail pricing")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 26.0)
    sheet.set_col(3, 4, 15.0)
    sheet.set_col(5, last_col, 14.0)
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

    product_lookup = lambda key: lookup("RcProduct", other("Products", "id"),
                                        other("Products", key))
    r = sheet.note(3, HELP, last_col, height=32)

    # ---------------------------------------------------------------- the item
    r = sheet.section(r, "1. What are you pricing?", last_col)
    r = f(r, "Product", formula=None, value=None, name="RcProduct",
          input_cell=True, validate=list_from("ProductIDs"),
          help_text="Pick one and its costs arrive below. Leave it blank and "
                    "type your own figures.")
    r = f(r, "Product name", formula=f'=IFERROR({product_lookup("name")},"")',
          style="text")
    r = f(r, "Craft", formula=f'=IFERROR({product_lookup("craft")},"")')
    r = f(r, "Status", formula=f'=IFERROR({product_lookup("status")},"")')
    r += 1

    # --------------------------------------------------------------- the costs
    r = sheet.section(r, "2. What one item costs", last_col)
    r = f(r, "Materials", name="RcMaterials", style="money",
          formula=f'=IFERROR({product_lookup("material_cost")},0)',
          help_text="From the bill of materials, or from the craft tab. Type "
                    "over it to cost something new.")
    r = f(r, "Minutes of work", name="RcMinutes", style="number1",
          formula=f'=IFERROR({product_lookup("minutes_used")},0)')
    r = f(r, "True cost of your hour", style="money",
          formula="=LaborCostHour",
          help_text="Your rate plus the payroll burden, from Settings.")
    r = f(r, "Labour", name="RcLabour", style="money",
          formula="=IF(N(RcMinutes)=0,0,N(RcMinutes)/60*LaborCostHour)")
    r = f(r, "Packaging", name="RcPackaging", style="money",
          formula=f'=IFERROR({product_lookup("packaging_cost")},DefaultPackaging)')
    r = f(r, "Postage you absorb", name="RcPostage", style="money",
          formula=f'=IFERROR({product_lookup("shipping_cost")},DefaultShipping)',
          help_text="The part of the postage you pay, not the customer.")
    r = f(r, "Share of overhead", name="RcOverhead", style="money",
          formula=f'=IFERROR({product_lookup("overhead_cost")},0)',
          help_text="Spread the way the Overhead method on Settings says.")
    r = sheet.field(r, "Total cost of one item", None, label_col=1,
                    value_col=3, value_end=4, style="money", name="RcCost",
                    formula="=N(RcMaterials)+N(RcLabour)+N(RcPackaging)"
                            "+N(RcPostage)+N(RcOverhead)",
                    help_text="This is the figure the price is built from.")
    r = _bold_row(sheet, fmts, r, 1, 4)
    r += 1

    # ---------------------------------------------------------------- the fees
    r = sheet.section(r, "3. What selling it costs", last_col)
    r = f(r, "Channel", name="RcChannel", input_cell=True,
          validate=list_from("ChannelList"),
          help_text="Blank uses the channel from the catalog, or the default "
                    "on Settings.")
    r = f(r, "Channel used", name="RcChannelUsed",
          formula=f'=IF(RcChannel<>"",RcChannel,'
                  f'IFERROR({product_lookup("channel")},DefaultChannel))')
    r = f(r, "Fee rate", name="RcFeeRate", style="percent",
          formula=f'={channel_fee_rate("RcChannelUsed")}',
          help_text="Transaction, processing, regulatory, currency and the "
                    "share of ad fees, from the Channels tab.")
    r = f(r, "Fixed fees an order", name="RcFixed", style="money",
          formula=f'={channel_fixed_fee("RcChannelUsed")}',
          help_text="The listing fee plus the fixed part of processing.")
    r += 1

    # --------------------------------------------------------------- the price
    r = sheet.section(r, "4. The price your margin asks for", last_col)
    r = f(r, "Target margin", name="RcMargin", style="percent",
          input_cell=True,
          help_text="Blank uses the target on Settings. Type 0.55 for 55%.")
    r = f(r, "Margin used", name="RcMarginUsed", style="percent",
          formula='=IF(RcMargin="",TargetRetailMargin,N(RcMargin))')
    r = sheet.field(r, "Suggested retail price", None, label_col=1,
                    value_col=3, value_end=4, style="money",
                    name="RcSuggested",
                    formula=f'={price_from("N(RcCost)", "N(RcFixed)", "RcMarginUsed", "N(RcFeeRate)")}',
                    help_text="(cost + fixed fees) / (1 - margin - fee rate), "
                              "rounded the way Settings says.")
    r = _bold_row(sheet, fmts, r, 1, 4)
    r = f(r, "Price by markup instead", style="money",
          formula="=N(RcCost)*DefaultMarkup",
          help_text="Cost times the default markup - the quick and usually "
                    "wrong way, shown for comparison.")
    r = f(r, "Catalog price", name="RcCatalogPrice", style="money",
          formula=f'=IFERROR({product_lookup("retail_price")},"")')
    r = f(r, "Price you charge", name="RcPrice", style="money",
          input_cell=True,
          help_text="Blank uses the catalog price.")
    r = f(r, "Price used", name="RcPriceUsed", style="money",
          formula='=IF(RcPrice="",N(RcCatalogPrice),N(RcPrice))')
    r = f(r, "Gap to the model price", style="money",
          formula='=IF(OR(RcPriceUsed="",RcSuggested=""),"",'
                  'N(RcSuggested)-N(RcPriceUsed))',
          help_text="Positive means you are charging less than your own "
                    "target margin asks for.")
    r += 1

    # ---------------------------------------------------------- what it earns
    r = sheet.section(r, "5. What it actually earns", last_col)
    r = f(r, "Fees at this price", name="RcFeesAtPrice", style="money",
          formula="=IF(N(RcPriceUsed)=0,0,N(RcFeeRate)*N(RcPriceUsed)"
                  "+N(RcFixed))")
    r = f(r, "Profit an item", name="RcProfit", style="money",
          formula="=IF(N(RcPriceUsed)=0,\"\",N(RcPriceUsed)"
                  "-N(RcFeesAtPrice)-N(RcCost))")
    r = f(r, "Margin", name="RcMarginNow", style="percent",
          formula="=IF(N(RcPriceUsed)=0,\"\",N(RcProfit)/N(RcPriceUsed))")
    r = f(r, "Margin check", style="text",
          formula="=IF(N(RcPriceUsed)=0,\"\",IF(N(RcProfit)<=0,\"LOSS - "
                  "PRICED BELOW COST\",IF(N(RcMarginNow)<MarginWarning,"
                  "\"THIN - BELOW YOUR WARNING\",\"OK\")))")
    r = f(r, "Effective hourly", name="RcHourly", style="money",
          formula="=IF(N(RcMinutes)=0,\"\",N(RcProfit)/(N(RcMinutes)/60))",
          help_text="What an hour of making this earns, after every fee.")
    r = f(r, "Wage check", style="text",
          formula="=IF(N(RcMinutes)=0,\"\",IF(N(RcHourly)<0,\"PAYING TO "
                  "WORK\",IF(N(RcHourly)<MinimumWage,\"BELOW THE MINIMUM "
                  "WAGE\",IF(N(RcHourly)<HourlyRate,\"BELOW YOUR OWN RATE\","
                  "\"GOOD\"))))")
    r = f(r, "Wholesale price", name="RcWholesale", style="money",
          formula=f'={round_price("N(RcSuggested)*(1-WholesaleDiscount)")}',
          help_text="The model price less the trade discount on Settings.")
    r = f(r, "Wholesale margin", style="percent",
          formula="=IF(N(RcWholesale)=0,\"\",(N(RcWholesale)-N(RcCost))"
                  "/N(RcWholesale))")
    r = f(r, "Wholesale check", style="text",
          formula="=IF(N(RcWholesale)=0,\"\",IF(N(RcWholesale)-N(RcCost)<=0,"
                  "\"TRADE LOSES MONEY\",IF((N(RcWholesale)-N(RcCost))"
                  "/N(RcWholesale)<TargetWholesaleMargin,\"BELOW THE TRADE "
                  "TARGET\",\"OK\")))")
    r += 1

    # --------------------------------------------------------------- scenarios
    r = sheet.section(r, "6. The same item at five margins", last_col)
    sheet.row_height(r, 20)
    for i, head in enumerate(["Scenario", "Margin", "Price", "Profit",
                              "Hourly"]):
        col = 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    for scenario, margin in PRICING_SCENARIOS.items():
        price = price_from("N(RcCost)", "N(RcFixed)", str(margin),
                           "N(RcFeeRate)")
        profit = (f"N({price})-(N(RcFeeRate)*N({price})+N(RcFixed))-N(RcCost)")
        sheet.row_height(r, 18)
        sheet.ws.merge_range(r, 1, r, 2, scenario, fmts.cell("text", "plain"))
        sheet.ws.merge_range(r, 3, r, 4, margin, fmts.cell("percent", "plain"))
        sheet.ws.merge_range(r, 5, r, 6, "", fmts.cell("money", "plain"))
        sheet.ws.write_formula(r, 5, "=" + price, fmts.cell("money", "plain"))
        sheet.ws.merge_range(r, 7, r, 8, "", fmts.cell("money", "plain"))
        sheet.ws.write_formula(r, 7, "=" + profit,
                               fmts.cell("money", "plain"))
        sheet.ws.merge_range(r, 9, r, 10, "", fmts.cell("money", "plain"))
        sheet.ws.write_formula(
            r, 9, f"=IF(N(RcMinutes)=0,\"\",({profit})/(N(RcMinutes)/60))",
            fmts.cell("money", "plain"))
        r += 1
    r += 1

    r = sheet.note(
        r,
        "The margin is in the denominator for a reason. A 30% margin is not "
        "cost plus 30%: if the item costs 20 and the channel takes 10%, "
        "charging 26 leaves 6.60 after fees against a cost of 20, which is a "
        "loss. Charging 33.99 leaves the 30% you meant.",
        last_col, height=44)

    sheet.ws.freeze_panes(4, 0)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet


def _bold_row(sheet, fmts, row: int, first_col: int, last_col: int) -> int:
    """Draw a rule under a total, on the spacer row below it.

    The total has already been written on `row - 1`, so the rule cannot go on
    that row without wiping the label and the value. It goes on the next row
    instead, which is blank anyway, and the caller carries on below it.
    """
    sheet.row_height(row, 7)
    for col in range(first_col, last_col + 1):
        sheet.ws.write_blank(row, col, None, fmts.chrome("rule"))
    return row + 1
