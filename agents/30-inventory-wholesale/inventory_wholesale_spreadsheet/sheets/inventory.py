"""5. Inventory Tracker - the answer to "how many have I got?".

There is not one typeable cell on this sheet, and that is the point.
Every row mirrors a row of the Product Database, and every quantity is
the arithmetic of things that happened:

    current  = opening + received - sold + returned - damaged
               +/- adjustments
    reserved = units on confirmed wholesale orders not yet shipped
    available = current - reserved

Available is the number that matters. Current stock is what is on the
shelf; available is what you are still allowed to sell. A seller who
promises against current stock sells the same pallet twice.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from .common import (adjustment_qty, alert_cf, alert_chain, bar_cf,
                     damaged_qty, lookup_product, lookup_product_num_zero,
                     received_qty, reserved_qty, returned_sellable_qty,
                     sold_qty, status_cf, weighted_average_cost, zero)

NAME = "Inventory Tracker"


def spec(cfg: Config) -> SheetSpec:
    sku = "{sku}{r}"

    cols = [
        Col("sku", "SKU", 15, "id",
            formula='=IF(INDEX([[Product & SKU Database.sku]],'
                    'ROW()-4)="","",'
                    'INDEX([[Product & SKU Database.sku]],ROW()-4))',
            note="Mirrors the Product Database row for row. Add a "
                 "product there and its stock line appears here by "
                 "itself - there is nothing to maintain on this tab."),
        Col("product", "Product", 26, "text",
            formula=lookup_product("name")),
        Col("category", "Category", 13, "text",
            formula=lookup_product("category")),
        Col("unit", "Unit", 10, "text",
            formula=lookup_product("unit")),
        Col("status", "Product status", 12, "status",
            formula=lookup_product("status"), cf=status_cf()),
        Col("location", "Location", 11, "text",
            formula='=IF({sku}{r}="","",IFERROR(INDEX('
                    '[[Warehouse Locations.location]],MATCH({sku}{r},'
                    '[[Warehouse Locations.sku]],0))&"",""))',
            note="The first bin this SKU is stored in. Split across "
                 "two shelves? The Warehouse Locations tab holds all "
                 "of them."),

        # ---- the arithmetic, one term per column ------------------
        Col("opening", "Opening", 9, "int",
            formula=lookup_product_num_zero("opening_qty"),
            note="What you declared on day one, straight from the "
                 "Product Database."),
        Col("received", "Received", 9, "int",
            formula=zero("sku", received_qty(sku)),
            note="Booked in against purchase orders. Receiving is "
                 "counted from the first PO/SKU line. Review duplicate "
                 "alerts; duplicate receipts under different POs are not detected."),
        Col("sold", "Sold", 9, "int",
            formula=zero("sku", sold_qty(sku)),
            note="Shipped wholesale orders plus completed retail "
                 "sales. A confirmed order that has not shipped is "
                 "not in here - it is in Reserved."),
        Col("returned", "Returned in", 10, "int",
            formula=zero("sku", returned_sellable_qty(sku)),
            note="Came back and went back on the shelf."),
        Col("damaged", "Damaged", 9, "int",
            formula=zero("sku", damaged_qty(sku)),
            note="Written off: returns that could not be resold, plus "
                 "breakage logged on the Stock Movement Log."),
        Col("adjusted", "Adjusted", 9, "int",
            formula=zero("sku", adjustment_qty(sku)),
            note="Manual corrections from the movement log, signed. A "
                 "stock count that found eleven fewer candles shows "
                 "as -11 here, and the reason is on that row."),

        Col("current", "In stock", 10, "int",
            formula=zero("sku", '{opening}{r}+{received}{r}-'
                                '{sold}{r}+{returned}{r}-'
                                '{damaged}{r}+{adjusted}{r}'),
            cf=bar_cf(),
            note="Opening + received - sold + returned - damaged "
                 "+/- adjustments. Physically on the shelf."),
        Col("reserved", "Reserved", 9, "int",
            formula=zero("sku", reserved_qty(sku)),
            note="Promised to a wholesale order that is confirmed, "
                 "being picked or packed, but not yet shipped. Still "
                 "in the building; no longer yours to sell."),
        Col("available", "Available", 10, "int",
            formula=zero("sku", '{current}{r}-{reserved}{r}'),
            cf=[{"type": "cell", "criteria": "<=", "value": 0,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": "<", "value": 5,
                 "fmt": "warn"}],
            note="In stock less reserved. THIS is the number to quote "
                 "a customer, and the number the reorder planner "
                 "works from."),
        Col("on_order", "On order", 9, "int",
            formula=zero("sku", 'SUMIFS([[Purchase Orders.qty]],'
                                '[[Purchase Orders.sku]],{sku}{r},'
                                '[[Purchase Orders.is_open]],1)-'
                                'SUMIFS([[Purchase Orders.received]],'
                                '[[Purchase Orders.sku]],{sku}{r},'
                                '[[Purchase Orders.is_open]],1)'),
            note="Ordered from a supplier, not arrived. Counted as "
                 "the outstanding balance of open purchase order "
                 "lines, so a part delivery leaves only the rest."),
        Col("next_po_row", "Next PO row", 9, "int",
            formula=zero("sku", 'SUMPRODUCT(MAX(('
                                '[[Purchase Orders.sku]]={sku}{r})*('
                                '[[Purchase Orders.is_open]]=1)*'
                                '[[Purchase Orders.seq_num]]))'),
            hidden=True),
        Col("incoming", "Next delivery", 12, "date",
            formula='=IF({sku}{r}="","",IF({next_po_row}{r}<=0,"",'
                    'IF(INDEX([[Purchase Orders.expected]],'
                    '{next_po_row}{r})="","",'
                    'INDEX([[Purchase Orders.expected]],'
                    '{next_po_row}{r}))))',
            note="The expected date on the most recent open purchase "
                 "order line for this SKU."),

        # ---- money ------------------------------------------------
        Col("avg_cost", "Avg cost", 10, "money4",
            formula=zero("sku", weighted_average_cost(sku)),
            note="Weighted average, the one costing method this "
                 "workbook uses. See the note at the bottom of "
                 "Inventory Valuation & COGS."),
        Col("stock_value", "Stock value", 12, "money",
            formula=zero("sku", 'ROUND({current}{r}*{avg_cost}{r},2)'),
            note="What is sitting on the shelf, at cost. Add this "
                 "column up and you have your inventory valuation."),
        Col("retail_value", "Retail value", 12, "money",
            formula=zero("sku", 'ROUND({current}{r}*'
                                'IFERROR(INDEX('
                                '[[Product & SKU Database.'
                                'retail_price]],MATCH({sku}{r},'
                                '[[Product & SKU Database.sku]],0))'
                                '*1,0),2)'),
            hidden=True),

        # ---- levels and cover -------------------------------------
        Col("min_stock", "Min", 7, "int",
            formula=lookup_product_num_zero("min_stock"), hidden=True),
        Col("max_stock", "Max", 7, "int",
            formula=lookup_product_num_zero("max_stock"), hidden=True),
        Col("daily_sales", "Sold/day", 9, "number1",
            formula=zero("sku", 'ROUND(SUMIFS('
                                '[[Retail Sales Tracker.qty]],'
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],1,'
                                '[[Retail Sales Tracker.date_num]],'
                                '">="&TodayDate-SalesWindow+1,'
                                '[[Retail Sales Tracker.date_num]],"<="&TodayDate)/'
                                'SalesWindow+SUMIFS('
                                '[[Wholesale Orders.qty]],'
                                '[[Wholesale Orders.sku]],{sku}{r},'
                                '[[Wholesale Orders.is_shipped]],1,'
                                '[[Wholesale Orders.ship_num]],'
                                '">="&TodayDate-SalesWindow+1,'
                                '[[Wholesale Orders.ship_num]],"<="&TodayDate)/'
                                'SalesWindow,2)'),
            note="Average units a day over the sales window set on "
                 "Settings - retail and shipped wholesale together."),
        Col("days_cover", "Days cover", 10, "int",
            formula='=IF({sku}{r}="","",IF({daily_sales}{r}<=0,"",'
                    'ROUND({available}{r}/{daily_sales}{r},0)))',
            cf=[{"type": "cell", "criteria": "<=", "value": 7,
                 "fmt": "bad"},
                {"type": "cell", "criteria": "<=", "value": 21,
                 "fmt": "warn"},
                {"type": "cell", "criteria": ">", "value": 120,
                 "fmt": "info"}],
            note="How long the available stock lasts at the current "
                 "rate of sale. Blank means nothing has sold lately, "
                 "which is its own kind of answer."),
        Col("stock_state", "Stock level", 13, "status",
            formula='=IF({sku}{r}="","",'
                    'IF({current}{r}<=0,"Out of stock",'
                    'IF({available}{r}<=0,"All reserved",'
                    'IF({min_stock}{r}>0,'
                    'IF({available}{r}<={min_stock}{r}*0.5,"Critical",'
                    'IF({available}{r}<={min_stock}{r},"Low",'
                    'IF({max_stock}{r}>0,'
                    'IF({current}{r}>{max_stock}{r},"Overstocked",'
                    '"OK"),"OK"))),'
                    'IF({available}{r}<5,"Low","OK")))))',
            cf=status_cf()),
        Col("last_move_num", "Last moved (n)", 9, "number",
            formula=zero("sku", 'SUMPRODUCT(MAX(('
                                '[[Stock Movement Log.sku]]='
                                '{sku}{r})*'
                                '[[Stock Movement Log.date_num]]))'),
            hidden=True),
        Col("last_movement", "Last moved", 11, "date",
            formula='=IF({sku}{r}="","",IF({last_move_num}{r}<=0,"",'
                    '{last_move_num}{r}))',
            note="The most recent dated row on the movement log for "
                 "this SKU."),

        # ---- hidden flags the dashboard counts --------------------
        Col("is_out", "Out", 6, "int",
            formula=zero("sku", 'IF({available}{r}<=0,1,0)'),
            hidden=True),
        Col("is_low", "Low", 6, "int",
            formula=zero("sku",
                         'IF({available}{r}<=0,0,'
                         'IF({min_stock}{r}<=0,0,'
                         'IF({available}{r}<={min_stock}{r},1,0)))'),
            hidden=True),
        Col("is_over", "Over", 6, "int",
            formula=zero("sku",
                         'IF({max_stock}{r}<=0,0,'
                         'IF({current}{r}>{max_stock}{r},1,0))'),
            hidden=True),
        Col("is_dead", "Dead", 6, "int",
            formula=zero("sku",
                         'IF({current}{r}<=0,0,'
                         'IF({daily_sales}{r}>0,0,1))'),
            hidden=True),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Inventory Tracker",
        subtitle=("Every quantity here is calculated. There is nothing "
                  "to type on this sheet - and no way to quietly "
                  "overwrite a stock figure."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text=("One line per product, mirroring the Product "
                   "Database. To change a number here, add the row "
                   "that explains it: receive a purchase order, log a "
                   "sale, record a return, or write an adjustment on "
                   "the Stock Movement Log."),
        extra_notes=[
            "In stock and Available are different on purpose. A "
            "confirmed wholesale order reserves its units - they are "
            "still in the building, so In stock does not move, but "
            "they are spoken for, so Available does. Quote customers "
            "from Available.",
            "On order is the balance still owed on open purchase "
            "order lines, not the whole order. Receive half a pallet "
            "and only the other half is still counted as coming.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{status}{r}="Discontinued"', [
            ('{current}{r}>0',
             "Retired - discontinued, still holding stock, sell it "
             "through"),
        ], "OK"),
        ('{current}{r}<0',
         "Urgent - negative stock, something was sold that was never "
         "received"),
        ('{current}{r}<{reserved}{r}',
         "Urgent - more reserved than you physically hold"),
        ('AND({available}{r}<=0,{on_order}{r}>0)',
         "Due - nothing available, delivery already on order"),
        ('{available}{r}<=0',
         "Order - out of stock and nothing on order"),
        ('AND({min_stock}{r}>0,{available}{r}<={min_stock}{r}*0.5,'
         '{on_order}{r}<=0)',
         "Urgent - critically low, nothing on order"),
        ('AND({min_stock}{r}>0,{available}{r}<={min_stock}{r},'
         '{on_order}{r}<=0)',
         "Order - below minimum level"),
        ('{is_dead}{r}=1',
         "Check - holding stock with no sales in the window"),
        ('{is_over}{r}=1',
         "Check - above your maximum stock level, cash is tied up"),
    ])
