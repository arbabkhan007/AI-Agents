"""13. Reorder Planner - what to buy, how much, and how urgently.

The arithmetic is the standard one and it is worth knowing by heart:

    reorder point = (average daily sales x lead time) + safety stock
    order quantity = maximum stock level - available - on order

Two refinements make it honest. The lead time used is the supplier's
REAL one, measured from your own received purchase orders, not the
one they quoted. And safety stock is expressed in days of cover
rather than a fixed number of units, so a line that sells ten a day
gets a bigger cushion than one that sells ten a month.

Rows sort themselves by urgency, so the top of this sheet is your
purchasing list for the morning.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from .common import (alert_cf, alert_chain, lookup_product,
                     lookup_product_num_zero, priority_cf,
                     status_cf, zero)

NAME = "Reorder Planner"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("sku", "SKU", 15, "id",
            formula='=IF(INDEX([[Product & SKU Database.sku]],'
                    'ROW()-4)="","",'
                    'INDEX([[Product & SKU Database.sku]],ROW()-4))',
            note="Every product gets a planning line automatically."),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("category", "Category", 13, "text",
            formula=lookup_product("category"), hidden=True),
        Col("status", "Product status", 12, "status",
            formula=lookup_product("status"), cf=status_cf(),
            hidden=True),
        Col("supplier", "Supplier ID", 11, "id",
            formula=lookup_product("supplier", missing='""'),
            hidden=True),
        Col("supplier_name", "Supplier", 18, "text",
            formula='=IF({sku}{r}="","",IFERROR(INDEX('
                    '[[Supplier Database.name]],MATCH('
                    '{supplier}{r},[[Supplier Database.id]],0))&"",'
                    '"No supplier set"))'),

        # ---- where you stand --------------------------------------
        Col("available", "Available", 10, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.available]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)')),
        Col("on_order", "On order", 9, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.on_order]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)')),
        Col("position", "Stock position", 13, "int",
            formula=zero("sku", '{available}{r}+{on_order}{r}'),
            note="Available plus what is already coming. Reordering "
                 "against available alone is how you end up with "
                 "two pallets of the same thing."),
        Col("daily_sales", "Sold/day", 9, "number1",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.daily_sales]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            note="Average daily sales over the window on Settings, "
                 "retail and wholesale together."),

        # ---- the calculation --------------------------------------
        Col("quoted_lead", "Quoted lead", 11, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Supplier Database.lead_time]],'
                                'MATCH({supplier}{r},'
                                '[[Supplier Database.id]],0))*1,'
                                'DefaultLeadDays)'),
            hidden=True),
        Col("actual_lead", "Real lead", 10, "number1",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Supplier Database.actual_lead]],'
                                'MATCH({supplier}{r},'
                                '[[Supplier Database.id]],0))*1,0)'),
            hidden=True),
        Col("lead_days", "Lead time", 10, "number1",
            formula=zero("sku",
                         'IF({actual_lead}{r}>0,'
                         'MAX({actual_lead}{r},{quoted_lead}{r}),'
                         'IF({quoted_lead}{r}>0,{quoted_lead}{r},'
                         'DefaultLeadDays))'),
            note="The longer of what they quote and what they "
                 "actually manage. Optimism about lead times is "
                 "paid for in stockouts."),
        Col("safety_stock", "Safety stock", 12, "int",
            formula=zero("sku", 'ROUNDUP({daily_sales}{r}*'
                                'SafetyDays,0)'),
            note="A cushion sized in days of cover rather than a "
                 "flat number of units, set on Settings."),
        Col("calc_point", "Calculated ROP", 13, "int",
            formula=zero("sku", 'ROUNDUP({daily_sales}{r}*'
                                '{lead_days}{r}+'
                                '{safety_stock}{r},0)'),
            note="(average daily sales x lead time) + safety stock."),
        Col("set_point", "Your ROP", 10, "int",
            formula=lookup_product_num_zero("reorder_point"),
            hidden=True),
        Col("reorder_point", "Reorder at", 11, "int",
            formula=zero("sku",
                         'IF({set_point}{r}>0,{set_point}{r},'
                         '{calc_point}{r})'),
            note="Yours if you set one on the product record, "
                 "otherwise the calculated figure."),
        Col("max_stock", "Max level", 10, "int",
            formula=lookup_product_num_zero("max_stock"),
            hidden=True),
        Col("target", "Order up to", 11, "int",
            formula=zero("sku",
                         'IF({max_stock}{r}>0,{max_stock}{r},'
                         'ROUNDUP({reorder_point}{r}*2,0))'),
            hidden=True),
        Col("suggested", "Order qty", 10, "int",
            formula=zero("sku",
                         'IF({position}{r}>{reorder_point}{r},0,'
                         'MAX(0,ROUNDUP({target}{r}-'
                         '{position}{r},0)))'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bold_bad"}],
            note="How many to buy to get back up to the maximum "
                 "level. Zero means you are fine."),
        Col("case_qty", "Case", 7, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Wholesale Pricing.case_qty]],'
                                'MATCH({sku}{r},'
                                '[[Wholesale Pricing.sku]],0))*1,0)'),
            hidden=True),
        Col("order_rounded", "Rounded", 9, "int",
            formula=zero("sku",
                         'IF({suggested}{r}<=0,0,'
                         'IF({case_qty}{r}<=1,{suggested}{r},'
                         'ROUNDUP({suggested}{r}/{case_qty}{r},0)*'
                         '{case_qty}{r}))'),
            note="Rounded up to whole cases where the product has a "
                 "case size."),
        Col("unit_cost", "Unit cost", 10, "money",
            formula=lookup_product_num_zero("cost"), hidden=True),
        Col("order_value", "Order value", 11, "money",
            formula=zero("sku", 'ROUND({order_rounded}{r}*'
                                '{unit_cost}{r},2)'),
            note="What this line would cost to buy. The Dashboard "
                 "adds them up, which is usually a sobering "
                 "number."),

        # ---- urgency ----------------------------------------------
        Col("days_cover", "Days cover", 10, "int",
            formula='=IF({sku}{r}="","",IF({daily_sales}{r}<=0,"",'
                    'ROUND({available}{r}/{daily_sales}{r},0)))',
            cf=[{"type": "cell", "criteria": "<=", "value": 7,
                 "fmt": "bad"},
                {"type": "cell", "criteria": "<=", "value": 21,
                 "fmt": "warn"}]),
        Col("stockout_date", "Runs out", 11, "date",
            formula='=IF({sku}{r}="","",IF({days_cover}{r}="","",'
                    'TodayDate+{days_cover}{r}))',
            note="When the shelf empties at the current rate of "
                 "sale, if nothing arrives."),
        Col("order_by", "Order by", 11, "date",
            formula='=IF({sku}{r}="","",IF({days_cover}{r}="","",'
                    'TodayDate+MAX(0,{days_cover}{r}-'
                    '{lead_days}{r})))',
            cf=[{"type": "cell", "criteria": "<=",
                 "value": "TodayDate", "fmt": "bad"}],
            note="The last day you can place the order and still "
                 "have it arrive before you run out. This is the "
                 "date that matters, not the stockout date."),
        Col("urgency", "Urgency", 12, "status",
            formula='=IF({sku}{r}="","",'
                    'IF({available}{r}<=0,"Out now",'
                    'IF({suggested}{r}<=0,"Fine",'
                    'IF({days_cover}{r}="","Review",'
                    'IF({days_cover}{r}<={lead_days}{r},"Urgent",'
                    'IF({days_cover}{r}<={lead_days}{r}*2,"Soon",'
                    '"Plan"))))))',
            cf=priority_cf()),
        Col("priority", "Rank", 7, "int",
            formula=zero("sku",
                         'IF({suggested}{r}<=0,0,'
                         'IF({available}{r}<=0,1,'
                         'IF({days_cover}{r}="",4,'
                         'IF({days_cover}{r}<={lead_days}{r},2,'
                         'IF({days_cover}{r}<={lead_days}{r}*2,3,'
                         '4)))))'),
            hidden=True),
        Col("needs_order", "To order", 8, "int",
            formula=zero("sku", 'IF({order_rounded}{r}>0,1,0)'),
            hidden=True),

        Col("buy_key", "Buy key", 9, "number",
            formula=zero("sku",
                         'IF({needs_order}{r}=0,0,'
                         '(10-{priority}{r})*1000000+'
                         'ROUND({order_value}{r},0))'),
            hidden=True,
            note="Urgency first, then size of the order. Ties are "
                 "broken below so no two lines ever share a rank."),
        Col("buy_rank", "Buy rank", 9, "int",
            formula=zero("sku",
                         'IF({needs_order}{r}=0,0,'
                         'COUNTIFS({buy_key_first}:{buy_key_last},'
                         '">"&{buy_key}{r})+'
                         'COUNTIFS({buy_key_first}:{buy_key}{r},'
                         '{buy_key}{r}))'),
            hidden=True,
            note="What the Dashboard reads to list the morning's "
                 "purchasing in order."),
        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Reorder Planner",
        subtitle=("(average daily sales x real lead time) + safety "
                  "stock. Everything on this sheet is calculated."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text=("Sort by Rank or filter Order qty to more than "
                   "zero and you have this week's purchasing list. "
                   "Nothing here needs typing - set the lead times "
                   "on the Supplier Database and the levels on the "
                   "Product Database and this sheet keeps itself."),
        extra_notes=[
            "Order by is the date to act on. Running out on the "
            "14th is only a problem if the lead time is ten days "
            "and you order on the 12th - the planner works "
            "backwards from the stockout so you are buying against "
            "the right deadline.",
            "The lead time used is the longer of what the supplier "
            "quotes and what they actually achieve, measured from "
            "your own received orders. A supplier cannot talk their "
            "way out of their own delivery history.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{status}{r}="Discontinued"', "OK"),
        ('{supplier}{r}=""',
         "Add - no supplier on this product, nothing can be "
         "ordered"),
        ('AND({available}{r}<=0,{on_order}{r}>0)',
         "Due - out of stock, delivery already placed"),
        ('{available}{r}<=0',
         "Urgent - out of stock and nothing on order"),
        ('AND({order_by}{r}<>"",{order_by}{r}<TodayDate,'
         '{suggested}{r}>0)',
         "Overdue - past the date you needed to order by"),
        ('AND({urgency}{r}="Urgent",{suggested}{r}>0)',
         "Order - will run out inside the lead time"),
        ('AND({urgency}{r}="Soon",{suggested}{r}>0)',
         "Order - getting low, put it on the next order"),
        ('AND({suggested}{r}>0,{order_value}{r}>0)',
         "Plan - below the reorder point, not urgent yet"),
        ('AND({daily_sales}{r}<=0,{available}{r}>0)',
         "Check - no recent sales, do not reorder on autopilot"),
    ])
