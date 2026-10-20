"""The Wholesale Orders tab - trade orders, from quote to paid.

One row per order: the shop, the purchase order number, the retail value of
what they took, the trade discount, the postage and tax, and where the order is
in its life. `due` is worked out from the shop's terms on the Wholesale
Customers tab, so a Net 30 order knows when it falls due on its own, and
`aging_flag` says CURRENT, DUE SOON or OVERDUE against today.

Trade orders are where a pricing model gets tested hardest: the discount is
big, the postage is heavy and the money arrives a month later. `margin` here is
the margin after the discount and the fees, and `profit_an_order` is what is
left once the goods themselves are paid for.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..writer import list_from
from .common import (calc_col, channel_fee_rate, channel_fixed_fee, date_col,
                     fetch, id_col, int_col, list_col, money_col, pct_col,
                     rank_desc, row_ref, samples, spec_defaults, text_col,
                     wrap_col)

P = Palette

NAME = "Wholesale Orders"

SUBTITLE = ("Trade orders: the discount, the postage, the terms, what is owed "
            "and whether it is late.")

HELP = ("Pick the shop and type the retail value of the order. The trade "
        "discount arrives from their terms, the due date from the payment "
        "terms, and the fees from the Wholesale channel on the Channels tab.")

WHOLESALE_CHANNEL = '"Wholesale"'


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    oid = row_ref("id")
    has_id = f'{oid}=""'
    customer = row_ref("customer")
    date = row_ref("date")
    status = row_ref("status")
    list_total = f"N({row_ref('list_total')})"
    eff = f"N({row_ref('effective_discount')})"
    wholesale = f"N({row_ref('wholesale_total')})"
    order_total = f"N({row_ref('order_total')})"

    rate = channel_fee_rate(WHOLESALE_CHANNEL)
    fixed = channel_fixed_fee(WHOLESALE_CHANNEL)
    terms = fetch("Wholesale Customers", "id", "terms", customer)
    terms_days = (f'IF(EXACT(TRIM({terms}),"Net 15"),15,'
                  f'IF(EXACT(TRIM({terms}),"Net 30"),30,'
                  f'IF(EXACT(TRIM({terms}),"Net 45"),45,'
                  f'IF(EXACT(TRIM({terms}),"Net 60"),60,'
                  f'IF(EXACT(TRIM({terms}),"Prepaid"),0,30)))))')

    cols: List[Any] = [
        id_col("PrefixOrder", trigger="customer", width=11.0),
        date_col("date", "Order date", 13.0),
        Col(key="customer", header="Customer ID", width=13.0, style="id",
            validate=list_from("CustomerIDs"),
            note="The shop, from the Wholesale Customers tab. Filling this in "
                 "starts the row."),
        calc_col("customer_name", "Shop",
                 f'IF({customer}="","",'
                 f'{fetch("Wholesale Customers", "id", "name", customer)})',
                 28.0, "text"),
        text_col("po_number", "Their PO", 15.0),
        text_col("products", "What they took", 30.0,
                 note="Free text: P-0001 x24, P-0004 x12."),
        int_col("qty", "Units", 9.0),
        calc_col("terms", "Terms", f'IF({has_id},"",{terms})', 11.0, "text"),
        calc_col("customer_discount", "Their discount",
                 f'IF({has_id},"",'
                 f'{fetch("Wholesale Customers", "id", "discount", customer, "0")})',
                 12.0, "percent"),
        pct_col("discount_rate", "Discount (typed)", 13.0,
                note="Type one for this order and it beats their standing "
                     "discount."),
        calc_col("effective_discount", "Discount used",
                 f'IF({has_id},"",IF({row_ref("discount_rate")}="",'
                 f'N({row_ref("customer_discount")}),{eff_raw()}))', 12.0,
                 "percent"),
        money_col("list_total", "Retail value", 13.0,
                  note="What the order would come to at your retail prices."),
        calc_col("wholesale_total", "Trade value",
                 f'IF({has_id},"",{list_total}*(1-{eff}))', 13.0, "money"),
        money_col("shipping", "Postage charged", 13.0),
        money_col("shipping_cost", "Postage it cost you", 14.0),
        money_col("tax", "Tax", 11.0),
        calc_col("tax_check", "Tax check",
                 f'IF({has_id},"",IF(AND(N({row_ref("tax")})>0,'
                 f'EXACT(TRIM({fetch("Wholesale Customers", "id", "tax_exempt", customer)}),'
                 f'"Yes")),"TAX CHARGED TO AN EXEMPT SHOP",""))', 24.0,
                 "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "EXEMPT", "fmt": "warn"}]),
        calc_col("order_total", "Order total",
                 f'IF({has_id},"",{wholesale}+N({row_ref("shipping")})'
                 f'+N({row_ref("tax")}))', 13.0, "money"),
        money_col("unit_cost", "Cost a unit", 12.0,
                  note="What one unit cost you - from the Products tab."),
        calc_col("cogs", "Cost of the goods",
                 f'IF({has_id},"",N({row_ref("qty")})*N({row_ref("unit_cost")}))',
                 13.0, "money"),
        calc_col("fees", "Fees",
                 f'IF({has_id},"",{rate}*{order_total}+{fixed})', 12.0,
                 "money", note="From the Wholesale channel on Channels."),
        calc_col("profit", "Profit",
                 f'IF({has_id},"",{wholesale}+N({row_ref("shipping")})'
                 f'-N({row_ref("shipping_cost")})-N({row_ref("cogs")})'
                 f'-N({row_ref("fees")}))', 13.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({has_id},"",IF({order_total}=0,"",'
                 f'N({row_ref("profit")})/{order_total}))', 10.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("min_order_check", "Minimum order",
                 f'IF({has_id},"",IF({wholesale}<'
                 f'N({fetch("Wholesale Customers", "id", "min_order", customer, "0")}),'
                 f'"BELOW THEIR MINIMUM","OK"))', 18.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        list_col("status", "Status", "OrderStatusList", 13.0),
        calc_col("due", "Due",
                 f'IF(OR({has_id},{date}=""),"",'
                 f'N({date})+{terms_days})', 13.0, "date",
                 note="Order date plus the payment terms."),
        date_col("paid", "Paid on", 13.0),
        calc_col("days_to_pay", "Days to pay",
                 f'IF(OR({has_id},{row_ref("paid")}="",{date}=""),"",'
                 f'IF(NOT(EXACT(TRIM({status}),"Paid")),"",'
                 f'N({row_ref("paid")})-N({date})))', 11.0, "int"),
        calc_col("aging_flag", "Aging",
                 f'IF({has_id},"",IF(EXACT(TRIM({status}),"Paid"),"PAID",'
                 f'IF(EXACT(TRIM({status}),"Cancelled"),"CANCELLED",'
                 f'IF(EXACT(TRIM({status}),"Quote"),"QUOTE ONLY",'
                 f'IF({row_ref("due")}="","NO DUE DATE",'
                 f'IF(TodayDate>N({row_ref("due")}),"OVERDUE",'
                 f'IF(N({row_ref("due")})-TodayDate<=7,"DUE SOON",'
                 f'"CURRENT")))))))', 14.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVERDUE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "DUE SOON", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "PAID", "fmt": "good"}]),
        calc_col("balance_outstanding", "Still owed",
                 f'IF({has_id},"",IF(EXACT(TRIM({status}),"Paid"),0,'
                 f'IF(EXACT(TRIM({status}),"Cancelled"),0,{order_total})))',
                 13.0, "money"),
        calc_col("rank_total", "rank total", rank_desc("order_total"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))


def eff_raw() -> str:
    """The typed discount, when there is one."""
    return f"N({row_ref('discount_rate')})"
