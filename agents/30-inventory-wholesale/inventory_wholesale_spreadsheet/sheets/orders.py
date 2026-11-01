"""11. Wholesale Orders - and the difference between promised and gone.

One row per order line, sharing an Order ID the way purchase order
lines share a PO number. Each line prices itself: the workbook reads
the customer's tier, finds the right quantity break on the Wholesale
Pricing tab, applies any account discount, and tells you the margin
before you confirm.

The status column is doing more work than it looks. It decides whether
the stock on this line is RESERVED or GONE:

* New - nothing has happened to stock yet.
* Confirmed, Processing, Picking, Packed - the units are reserved.
  Still on your shelf, no longer available to sell to anybody else.
* Shipped, Delivered - the units have left. Stock drops.
* Cancelled, Returned - the line releases its stock again.

That distinction is the whole reason the Inventory Tracker has both an
In stock and an Available column, and it is what stops you selling the
same forty mugs to two shops in the same week.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, date_num_col,
                     is_reserving, is_shipped, lookup_customer,
                     lookup_customer_num, lookup_product,
                     lookup_product_num_zero, margin, month_col,
                     owing_cf, scale_cf, seq_num_col, sku_col,
                     status_cf, tier_price, zero)
from ..writer import date_check, list_from, number_check

NAME = "Wholesale Orders"


def spec(cfg: Config) -> SheetSpec:
    sku = "{sku}{r}"

    cols = [
        Col("order_id", "Order ID", 12, "id",
            note="Repeat it across every line of the same order. "
                 "The printable invoice gathers the lines that "
                 "share it."),
        Col("line_no", "Line", 6, "int",
            formula=blank("order_id", 'COUNTIFS({order_id_first}:'
                                      '{order_id}{r},'
                                      '{order_id}{r})')),
        Col("is_first_line", "First line", 8, "int",
            formula=zero("order_id", 'IF({line_no}{r}=1,1,0)'),
            hidden=True,
            note="Marks one line per order, so order counts "
                 "elsewhere count orders rather than lines."),
        Col("date", "Order date", 11, "date", validate=date_check()),
        Col("customer", "Customer ID", 11, "id",
            validate=list_from("CustomerList")),
        Col("customer_name", "Customer", 20, "text",
            formula=lookup_customer("business")),
        Col("tier", "Tier", 11, "text",
            formula=lookup_customer("tier"),
            note="Read off the customer record. Change their tier "
                 "there and every future order follows."),
        Col("po_ref", "Their PO ref", 12, "text",
            note="The reference the shop gave you. Put it on the "
                 "invoice and you get paid faster."),

        sku_col(),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("qty", "Qty", 8, "int",
            validate=number_check(0, 1000000)),

        # ---- pricing, automatic -----------------------------------
        Col("tier_price", "Tier price", 11, "money",
            formula=zero("order_id", tier_price("{qty}{r}", sku)),
            note="The right price break for this quantity, found by "
                 "checking the largest break first so a hundred "
                 "units gets the hundred price, not the ten price."),
        Col("cust_discount", "Acct disc.", 9, "percent0",
            formula=zero("order_id",
                         lookup_customer_num("discount")[1:]),
            hidden=True),
        Col("line_discount", "Line disc.", 9, "percent0",
            validate=number_check(0, 1),
            note="Anything extra on this line only. Leave blank "
                 "unless you mean it."),
        Col("unit_price", "Unit price", 11, "money",
            formula=zero("order_id",
                         'ROUND({tier_price}{r}*'
                         '(1-{cust_discount}{r})*'
                         '(1-{line_discount}{r}),2)'),
            note="Tier price after the account discount and any "
                 "line discount. This is what they pay per unit."),
        Col("line_total", "Line total", 11, "money",
            formula=zero("order_id", 'ROUND({qty}{r}*'
                                     '{unit_price}{r},2)')),
        Col("unit_cost", "Unit cost", 10, "money4",
            formula=zero("order_id", 'IFERROR(INDEX('
                                     '[[Inventory Tracker.'
                                     'avg_cost]],MATCH({sku}{r},'
                                     '[[Inventory Tracker.sku]],0))'
                                     f'*1,{lookup_product_num_zero("cost")[1:]})'),
            hidden=True),
        Col("line_cost", "Line cost", 11, "money",
            formula=zero("order_id", 'ROUND({qty}{r}*'
                                     '{unit_cost}{r},2)'),
            hidden=True),
        Col("line_profit", "Line profit", 11, "money",
            formula=zero("order_id", 'ROUND({line_total}{r}-'
                                     '{line_cost}{r},2)'),
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bold_bad"}]),
        Col("line_gp", "GP%", 8, "percent0",
            formula=blank("order_id", margin("{line_profit}{r}",
                                             "{line_total}{r}")),
            cf=scale_cf()),

        # ---- fulfilment -------------------------------------------
        Col("status", "Status", 13, "status",
            validate=list_from("OrderStatusList"), cf=status_cf(),
            note="This is the cell that moves stock. Confirmed "
                 "through Packed reserves it; Shipped and Delivered "
                 "take it out of stock for good."),
        Col("available", "Available", 10, "int",
            formula=blank("order_id", 'IFERROR(INDEX('
                                      '[[Inventory Tracker.'
                                      'available]],MATCH({sku}{r},'
                                      '[[Inventory Tracker.sku]],0))'
                                      '*1,0)'),
            note="What is free to sell right now, including this "
                 "line's own reservation. Shown here so you can see "
                 "the problem before you promise a date."),
        Col("shortfall", "Short by", 9, "int",
            formula=zero("order_id",
                         'IF({is_shipped}{r}=1,0,'
                         'MAX(0,{qty}{r}-({available}{r}+'
                         'IF({is_reserved}{r}=1,{qty}{r},0))))'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bold_bad"}],
            note="How many you are short if you tried to pick this "
                 "line today. Its own reservation is added back "
                 "first, otherwise every confirmed line would look "
                 "short against itself."),
        Col("ship_date", "Shipped", 11, "date", validate=date_check()),
        Col("tracking", "Tracking", 16, "text"),
        Col("ship_method", "Method", 12, "text",
            validate=list_from("ShippingMethodList")),
        Col("shipping_charge", "Shipping", 10, "money",
            validate=number_check(0, 100000),
            note="What you charged them for carriage, on the first "
                 "line of the order only."),

        # ---- money in ---------------------------------------------
        Col("invoice_no", "Invoice no.", 12, "text"),
        Col("terms", "Terms", 11, "text",
            formula=lookup_customer("terms"), hidden=True),
        Col("due_date", "Payment due", 11, "date",
            formula='=IF({order_id}{r}="","",'
                    'IF({invoice_no}{r}="","",'
                    'IF({ship_date}{r}="","",'
                    '{ship_date}{r}+IFERROR(INDEX(TermDays,'
                    'MATCH({terms}{r},PaymentTermsList,0)),0))))'),
        Col("paid_amount", "Paid", 11, "money",
            validate=number_check(0, 1000000),
            note="What has actually landed against this line. Part "
                 "payments are fine - put the running total."),
        Col("outstanding", "Outstanding", 11, "money",
            formula=zero("order_id",
                         'IF({status}{r}="Cancelled",0,'
                         'IF({invoice_no}{r}="",0,'
                         'ROUND(MAX(0,{line_total}{r}+'
                         '{shipping_charge}{r}-'
                         '{paid_amount}{r}),2)))'),
            cf=owing_cf(),
            note="Invoiced and not yet paid. Nothing counts as owed "
                 "until there is an invoice number on the line."),
        Col("is_overdue", "Overdue", 7, "int",
            formula=zero("order_id",
                         'IF({outstanding}{r}<=0,0,'
                         'IF({due_date}{r}="",0,'
                         'IF({due_date}{r}<TodayDate,1,0)))'),
            hidden=True),
        Col("days_overdue", "Days over", 9, "int",
            formula='=IF({order_id}{r}="","",'
                    'IF({is_overdue}{r}=0,"",'
                    'TodayDate-{due_date}{r}))',
            cf=[{"type": "cell", "criteria": ">", "value": 30,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"}]),
        Col("notes", "Notes", 24, "wrap"),

        # ---- the two flags the whole stock model turns on ---------
        Col("is_reserved", "Reserved", 8, "int",
            formula=zero("order_id",
                         f'IF({is_reserving("{status}{r}")},1,0)'),
            hidden=True,
            note="Confirmed, Processing, Picking or Packed: the "
                 "units are committed but still on the shelf. The "
                 "Inventory Tracker subtracts these from Available "
                 "without touching In stock."),
        Col("is_shipped", "Shipped?", 8, "int",
            formula=zero("order_id",
                         f'IF({is_shipped("{status}{r}")},1,0)'),
            hidden=True,
            note="Shipped or Delivered: the units have physically "
                 "gone and come out of stock."),
        Col("is_open", "Open", 6, "int",
            formula=zero("order_id",
                         'IF({status}{r}="Cancelled",0,'
                         'IF({is_shipped}{r}=1,0,1))'),
            hidden=True),
        Col("units_shipped", "Units out", 9, "int",
            formula=zero("order_id", 'IF({is_shipped}{r}=1,'
                                     '{qty}{r},0)'),
            hidden=True),
        Col("days_to_ship", "Days to ship", 11, "int",
            formula='=IF({order_id}{r}="","",'
                    'IF({ship_date}{r}="","",'
                    'IF({date}{r}="","",'
                    '{ship_date}{r}-{date}{r})))',
            note="Order date to despatch. Wholesale buyers forgive "
                 "a lot, but not a fortnight of silence."),
        Col("age_days", "Age", 7, "int",
            formula='=IF({order_id}{r}="","",IF({date}{r}="","",'
                    'IF({is_shipped}{r}=1,"",TodayDate-{date}{r})))',
            cf=[{"type": "cell", "criteria": ">", "value": 14,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 7,
                 "fmt": "warn"}],
            note="How long an unshipped order has been sitting."),
        Col("below_min", "Below MOQ", 9, "int",
            formula=zero("order_id",
                         'IF({is_first_line}{r}=0,0,'
                         f'IF({lookup_customer_num("min_order")[1:]}'
                         '<=0,0,'
                         'IF(SUMIFS({line_total_first}:'
                         '{line_total_last},{order_id_first}:'
                         '{order_id_last},{order_id}{r})<'
                         f'{lookup_customer_num("min_order")[1:]}'
                         ',1,0)))'),
            hidden=True),

        month_col("date"),
        date_num_col("date", "date_num"),
        date_num_col("ship_date", "ship_num"),
        seq_num_col("order_id"),

        Col("order_print_rank", "Print line", 9, "int",
            formula=zero("order_id",
                         'IF({order_id}{r}<>PrintOrder,0,'
                         '{line_no}{r})'),
            hidden=True,
            note="Line number within the order currently typed on "
                 "the Printable Orders & Invoices tab. Zero "
                 "everywhere else, which is what lets the invoice "
                 "and picking list gather their lines."),
        Col("pick_key", "Pick key", 9, "number",
            formula=zero("order_id",
                         'IF({is_reserved}{r}=0,0,'
                         'IF({shortfall}{r}>0,2000000,1000000)+'
                         'IF({age_days}{r}="",0,{age_days}{r}*100))'),
            hidden=True),
        Col("pick_rank", "Pick rank", 9, "int",
            formula=zero("order_id",
                         'IF({is_reserved}{r}=0,0,'
                         'COUNTIFS({pick_key_first}:{pick_key_last},'
                         '">"&{pick_key}{r})+'
                         'COUNTIFS({pick_key_first}:{pick_key}{r},'
                         '{pick_key}{r}))'),
            hidden=True,
            note="Orders waiting to ship, worst first: anything "
                 "short of stock, then whatever has been sitting "
                 "longest."),
        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Wholesale Orders",
        subtitle=("Lines price themselves off the customer's tier. "
                  "The status column decides whether stock is "
                  "reserved or gone."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("orders", cfg),
        help_text=("Enter the Order ID, the customer and the lines. "
                   "Price, margin and availability appear by "
                   "themselves. Move the status along as the order "
                   "progresses and the stock figures follow."),
        extra_notes=[
            "Confirming an order reserves stock; shipping it removes "
            "stock. Until you mark a line Shipped the units are "
            "still counted as in stock - because they are still in "
            "the building - but they stop being available to sell.",
            "Short by is calculated with this line's own "
            "reservation added back, so it answers the question you "
            "actually have: can I pick this order today?",
        ],
    )


def _alert() -> str:
    return alert_chain("order_id", [
        ('{status}{r}="Cancelled"', "OK"),
        ('{customer}{r}=""', "Add - which customer"),
        ('{sku}{r}=""', "Add - which product"),
        ('{qty}{r}<=0', "Add - quantity"),
        ('{unit_price}{r}<=0',
         "Urgent - no price found, check the Wholesale Pricing tab"),
        ('{line_profit}{r}<0',
         "Urgent - this line sells below cost"),
        ('AND({line_gp}{r}<>"",{line_gp}{r}<MinGP)',
         "Check - margin below your minimum"),
        ('AND({is_shipped}{r}=0,{shortfall}{r}>0)',
         "Urgent - not enough stock to pick this line"),
        ('{status}{r}=""', "Add - order status"),
        ('AND({is_shipped}{r}=1,{ship_date}{r}="")',
         "Add - date it shipped"),
        ('AND({is_shipped}{r}=1,{invoice_no}{r}="")',
         "Send - shipped but never invoiced"),
        ('{is_overdue}{r}=1',
         "Overdue - payment is past its due date, chase it"),
        ('AND({status}{r}="Packed",{ship_date}{r}="")',
         "Send - packed and waiting to go"),
        ('AND({age_days}{r}<>"",{age_days}{r}>PickWarningDays,'
         '{is_reserved}{r}=1)',
         "Action - confirmed a while ago and still not shipped"),
        ('{below_min}{r}=1',
         "Check - order is below this customer's minimum"),
        ('AND({is_shipped}{r}=1,{paid_amount}{r}<=0,'
         '{invoice_no}{r}<>"")',
         "Unpaid - invoiced and nothing received yet"),
    ])
