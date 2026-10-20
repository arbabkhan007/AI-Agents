"""The Wholesale Calculator - a trade order, costed before you quote it.

Trade is where a good retail price can still turn into a bad deal: the discount
is large, the parcel is heavy, the fees are different and the money arrives a
month later. Pick the shop and the product, type the quantity, and this page
shows the trade price their discount implies, what the order is worth, what you
keep after the fees and the cost of the goods, and whether the margin clears
the target for trade on Settings.

It also works backwards. `Retail price needed` answers the question that comes
up at every wholesale show: what does the retail price have to be for this
trade price to still work?
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..config import Config, Palette
from ..layout import lookup
from ..writer import SheetWriter, list_from
from .common import (channel_fee_rate, channel_fixed_fee, other, price_from,
                     round_price)

P = Palette

NAME = "Wholesale Calculator"

SUBTITLE = ("A trade order priced properly: discount, fees, postage, terms and "
            "what is left for you.")

HELP = ("Pick the shop and the product, type the quantity. Their discount and "
        "terms arrive from the Wholesale Customers tab; the fees come from the "
        "Wholesale channel.")

WHOLESALE_CHANNEL = '"Wholesale"'

QTY_STEPS = [6, 12, 24, 48, 100]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=False)
    last_col = 10
    sheet.banner(NAME, SUBTITLE, last_col, badge="Wholesale pricing")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 28.0)
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

    cust = lambda key: lookup("WcCustomer",
                              other("Wholesale Customers", "id"),
                              other("Wholesale Customers", key))
    prod = lambda key: lookup("WcProduct", other("Products", "id"),
                              other("Products", key))

    r = sheet.note(3, HELP, last_col, height=32)

    # ------------------------------------------------------------ the order
    r = sheet.section(r, "1. The order", last_col)
    r = f(r, "Shop", name="WcCustomer", input_cell=True,
          validate=list_from("CustomerIDs"),
          help_text="From the Wholesale Customers tab.")
    r = f(r, "Shop name", formula=f'=IFERROR({cust("name")},"")')
    r = f(r, "Their terms", formula=f'=IFERROR({cust("terms")},"")')
    r = f(r, "Their standing discount", style="percent",
          formula=f'=IFERROR({cust("discount")},WholesaleDiscount)')
    r = f(r, "Their minimum order", style="money",
          formula=f'=IFERROR({cust("min_order")},MinOrderValue)')
    r = f(r, "Their credit limit", style="money",
          formula=f'=IFERROR({cust("credit_limit")},0)')
    r = f(r, "Product", name="WcProduct", input_cell=True,
          validate=list_from("ProductIDs"))
    r = f(r, "Product name", formula=f'=IFERROR({prod("name")},"")')
    r = f(r, "Retail price", name="WcRetail", style="money",
          formula=f'=IFERROR({prod("retail_price")},0)')
    r = f(r, "Cost of one item", name="WcUnitCost", style="money",
          formula=f'=IFERROR({prod("total_cost")},0)')
    r = f(r, "Minutes an item", name="WcMinutes", style="number1",
          formula=f'=IFERROR({prod("minutes_used")},0)')
    r = f(r, "Units in the order", name="WcQty", style="int",
          input_cell=True, value=cfg.minimum_order_qty,
          help_text="How many they want.")
    r = f(r, "Discount for this order", name="WcDiscount", style="percent",
          input_cell=True,
          help_text="Blank uses their standing discount.")
    r = f(r, "Discount used", name="WcDiscountUsed", style="percent",
          formula='=IF(WcDiscount="",WholesaleDiscount,N(WcDiscount))')
    r += 1

    # ------------------------------------------------------- the trade price
    r = sheet.section(r, "2. The trade price", last_col)
    r = sheet.field(r, "Trade price an item", None, label_col=1, value_col=3,
                    value_end=4, style="money", name="WcTradePrice",
                    formula=f'={round_price("N(WcRetail)*(1-N(WcDiscountUsed))")}',
                    help_text="Retail less the discount, rounded the way "
                              "Settings says.")
    r = _rule(sheet, fmts, r, 1, 4)
    r = f(r, "Order value", name="WcOrderValue", style="money",
          formula="=N(WcTradePrice)*N(WcQty)")
    r = f(r, "Postage you charge", name="WcPostage", style="money",
          input_cell=True, value=0,
          help_text="A trade parcel is heavy - type what you will charge.")
    r = f(r, "Postage it costs you", name="WcPostageCost", style="money",
          input_cell=True, value=0)
    r = f(r, "Tax", name="WcTax", style="money", input_cell=True, value=0,
          help_text="Zero for a tax exempt shop with a resale certificate.")
    r = f(r, "Order total", name="WcOrderTotal", style="money",
          formula="=N(WcOrderValue)+N(WcPostage)+N(WcTax)")
    r += 1

    # --------------------------------------------------------- what you keep
    r = sheet.section(r, "3. What you keep", last_col)
    rate = channel_fee_rate(WHOLESALE_CHANNEL)
    fixed = channel_fixed_fee(WHOLESALE_CHANNEL)
    r = f(r, "Wholesale fee rate", name="WcFeeRate", style="percent",
          formula=f"={rate}",
          help_text="From the Wholesale channel on the Channels tab.")
    r = f(r, "Fees on the order", name="WcFees", style="money",
          formula=f"=N(WcFeeRate)*N(WcOrderTotal)+{fixed}")
    r = f(r, "Cost of the goods", name="WcCogs", style="money",
          formula="=N(WcUnitCost)*N(WcQty)")
    r = sheet.field(r, "Profit on the order", None, label_col=1, value_col=3,
                    value_end=4, style="money", name="WcProfit",
                    formula="=N(WcOrderValue)+N(WcPostage)"
                            "-N(WcPostageCost)-N(WcFees)-N(WcCogs)",
                    help_text="After fees, postage and the cost of the goods.")
    r = _rule(sheet, fmts, r, 1, 4)
    r = f(r, "Margin", name="WcMargin", style="percent",
          formula='=IF(N(WcOrderValue)=0,"",N(WcProfit)/N(WcOrderValue))')
    r = f(r, "Margin check", style="text",
          formula='=IF(N(WcOrderValue)=0,"",IF(N(WcProfit)<=0,'
                  '"TRADE LOSES MONEY",IF(N(WcMargin)<TargetWholesaleMargin,'
                  '"BELOW THE TRADE TARGET","OK")))')
    r = f(r, "Profit an item", style="money",
          formula='=IF(N(WcQty)=0,"",N(WcProfit)/N(WcQty))')
    r = f(r, "Hours in the order", style="number",
          formula="=N(WcMinutes)*N(WcQty)/60")
    r = f(r, "Hourly earned", name="WcHourly", style="money",
          formula='=IF(N(WcMinutes)=0,"",N(WcProfit)/(N(WcMinutes)*N(WcQty)/60))')
    r = f(r, "Minimum order check", style="text",
          formula='=IF(N(WcOrderValue)=0,"",IF(N(WcOrderValue)'
                  '<MAX(N(MinOrderValue),0),"BELOW YOUR MINIMUM",'
                  'IF(N(WcQty)<MinOrderQty,"FEWER UNITS THAN YOUR MINIMUM",'
                  '"OK")))')
    r = f(r, "Credit check", style="text",
          formula='=IF(N(WcOrderTotal)=0,"",IF(N(WcOrderTotal)'
                  '+IFERROR(N(WcBalance),0)>N(IFERROR(WcCreditLimit,0))'
                  ',"WOULD GO OVER THEIR LIMIT","WITHIN THEIR LIMIT"))')
    r = f(r, "Money arrives", style="text",
          formula='=IF(WcCustomer="","",IF(EXACT(TRIM(WcTerms),"Prepaid"),'
                  '"ON ORDER","AFTER " & WcTerms))')
    r = f(r, "Their terms (name)", name="WcTerms",
          formula=f'=IFERROR({cust("terms")},"")')
    r = f(r, "Outstanding balance", name="WcBalance", style="money",
          formula=f'=IFERROR({cust("balance")},0)')
    r = f(r, "Credit limit (name)", name="WcCreditLimit", style="money",
          formula=f'=IFERROR({cust("credit_limit")},0)')
    r += 1

    # ---------------------------------------------------------- working back
    r = sheet.section(r, "4. Working backwards", last_col)
    r = sheet.field(r, "Trade price your target asks for", None, label_col=1,
                    value_col=3, value_end=4, style="money",
                    name="WcSuggestedTrade",
                    formula=f"={price_from('N(WcUnitCost)', fixed, 'TargetWholesaleMargin', 'N(WcFeeRate)')}",
                    help_text="(cost + fixed fees) / (1 - trade target margin "
                              "- fee rate).")
    r = _rule(sheet, fmts, r, 1, 4)
    retail_needed = round_price(
        "IF(N(WcDiscountUsed)>=1,0,"
        "N(WcSuggestedTrade)/(1-N(WcDiscountUsed)))")
    r = f(r, "Retail price needed", name="WcRetailNeeded", style="money",
          formula=f"={retail_needed}",
          help_text="What the retail price has to be for the trade price to "
                    "work at this discount.")
    r = f(r, "Gap to your retail price", style="money",
          formula='=IF(OR(N(WcRetailNeeded)=0,N(WcRetail)=0),"",'
                  'N(WcRetailNeeded)-N(WcRetail))',
          help_text="Positive means your retail price is too low to support "
                    "the trade discount.")
    r = f(r, "Biggest discount you can give", style="percent",
          formula='=IF(N(WcRetail)=0,"",MAX(0,1-N(WcSuggestedTrade)'
                  '/N(WcRetail)))',
          help_text="The discount that still leaves the trade target margin.")
    r += 1

    # ---------------------------------------------------------- volume strip
    r = sheet.section(r, "5. The same product at five quantities", last_col)
    sheet.row_height(r, 20)
    for i, head in enumerate(["Units", "Order value", "Fees", "Cost of goods",
                              "Profit", "Margin"]):
        col = 1 + i * 2 if i < 3 else 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    for qty in QTY_STEPS:
        value = f"N(WcTradePrice)*{qty}"
        fees = f"N(WcFeeRate)*({value}+N(WcPostage)+N(WcTax))+{fixed}"
        cogs = f"N(WcUnitCost)*{qty}"
        profit = f"{value}+N(WcPostage)-N(WcPostageCost)-{fees}-{cogs}"
        sheet.row_height(r, 18)
        sheet.ws.merge_range(r, 1, r, 2, qty, fmts.cell("int", "plain"))
        for i, (formula, style) in enumerate([
                (value, "money"), (fees, "money"), (cogs, "money"),
                (profit, "money"),
                (f'IF({value}=0,"",{profit}/{value})', "percent")]):
            col = 3 + i * 2
            sheet.ws.merge_range(r, col, r, col + 1, "",
                                 fmts.cell(style, "plain"))
            sheet.formula(r, col, "=" + formula,
                                   fmts.cell(style, "plain"))
        r += 1
    r += 1
    r = sheet.note(
        r,
        "Trade prices are usually agreed for a season, so the discount on this "
        "page is the one to write on the line sheet. If the retail price "
        "needed is above the one you charge, the answer is not a smaller "
        "discount - it is a higher retail price.",
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
