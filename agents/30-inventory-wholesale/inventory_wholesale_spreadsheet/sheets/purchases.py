"""8. Purchase Orders - ordering, and booking the delivery in once.

One row is one line of one purchase order: a PO number, a SKU, a
quantity, a cost. A three-product order is three rows sharing a PO
number.

Receiving works the way it does here for one reason. There is exactly
ONE cell per line where a received quantity can live, so booking the
same delivery in twice is not something the workbook has to detect -
it is something the shape of the sheet makes impossible. Type 40 into
that cell twice and it still says 40. The only way to double count a
delivery is to create a second line for the same PO and SKU, and the
Duplicate line column flags that in red the moment you do.

Part deliveries are normal: received 30 of 50 leaves 20 outstanding,
the line stays open, and the Inventory Tracker counts 30 in stock and
20 still on order.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, date_num_col,
                     is_committed_po, is_open_po, lookup_product,
                     lookup_product_num_zero, lookup_supplier,
                     month_col, seq_num_col,
                     sku_col, status_cf, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Purchase Orders"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("po_id", "PO number", 12, "id",
            note="Your purchase order number. Repeat it on every "
                 "line of the same order - the printable PO on the "
                 "last tab gathers all the lines that share it."),
        Col("line_no", "Line", 6, "int",
            formula=blank("po_id", 'COUNTIFS({po_id_first}:'
                                   '{po_id}{r},{po_id}{r})'),
            note="Line number within this PO, worked out for you."),
        Col("supplier", "Supplier ID", 11, "id",
            validate=list_from("SupplierList")),
        Col("supplier_name", "Supplier", 20, "text",
            formula=lookup_supplier("name")),
        Col("order_date", "Ordered", 11, "date", validate=date_check(),
            note="The date you sent it, not the date you drafted it."),
        Col("expected", "Expected", 11, "date", validate=date_check(),
            note="Enter the expected date manually, using the supplier's "
                 "lead time as a guide."),
        sku_col(),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("supplier_sku", "Their code", 12, "text",
            formula=lookup_product("supplier_sku", missing='""'),
            note="The supplier's own code for it, pulled from the "
                 "product record so the order makes sense to them."),

        # ---- ordering ---------------------------------------------
        Col("qty", "Qty ordered", 11, "int",
            validate=number_check(0, 1000000)),
        Col("unit_cost", "Unit cost", 10, "money",
            validate=number_check(0, 1000000),
            note="What they are charging you per unit on this order. "
                 "Not the standing cost on the product record - what "
                 "this delivery actually cost."),
        Col("discount", "Discount", 9, "percent0",
            validate=number_check(0, 1)),
        Col("freight", "Freight", 10, "money",
            validate=number_check(0, 1000000),
            note="Shipping, duty and handling for THIS line. Spread "
                 "a single carriage charge across the lines and it "
                 "lands in the stock value where it belongs."),
        Col("goods_value", "Goods", 11, "money",
            formula=zero("po_id", 'ROUND({qty}{r}*{unit_cost}{r}*'
                                  '(1-{discount}{r}),2)')),
        Col("total", "Line total", 11, "money",
            formula=zero("po_id", 'ROUND({goods_value}{r}+'
                                  '{freight}{r},2)'),
            note="Goods plus freight - the landed cost of the line, "
                 "which is what inventory should be valued at."),
        Col("landed_each", "Landed each", 11, "money4",
            formula=zero("po_id", 'IF({qty}{r}<=0,{unit_cost}{r},'
                                  'ROUND({total}{r}/{qty}{r},4))'),
            note="Landed cost per unit. This is what feeds the "
                 "weighted average cost, which is why freight "
                 "belongs on the line."),

        # ---- receiving - one cell, once ---------------------------
        Col("received", "Qty received", 12, "int",
            validate=number_check(0, 1000000),
            note="THE receiving cell. One per line, so a delivery "
                 "cannot be booked in twice. Part delivery? Put what "
                 "arrived; the rest stays outstanding. Second "
                 "shipment? Update this number to the running total "
                 "received against this line."),
        Col("received_date", "Received", 11, "date",
            validate=date_check()),
        Col("received_by", "Checked by", 12, "text",
            validate=list_from("StaffList")),
        Col("condition", "Condition", 12, "text",
            validate=list_from("DeliveryConditionList"),
            note="How it turned up. Anything other than Good wants a "
                 "note and probably a claim."),
        Col("received_value", "Received value", 12, "money",
            formula=zero("po_id", 'IF({valid_line}{r}=1,ROUND({received}{r}*'
                                  '{landed_each}{r},2),0)'),
            note="What arrived, at landed cost. This is the number "
                 "the weighted average cost is built from."),
        Col("outstanding", "Still due", 10, "int",
            formula=zero("po_id", 'MAX(0,{qty}{r}-{received}{r})'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"}]),
        Col("outstanding_value", "Due value", 11, "money",
            formula=zero("po_id", 'ROUND({outstanding}{r}*'
                                  '{landed_each}{r},2)'),
            hidden=True),
        Col("status", "Status", 15, "status",
            validate=list_from("POStatusList"), cf=status_cf(),
            note="Set it yourself, or leave it and read the "
                 "Suggested status column, which works it out from "
                 "the quantities."),
        Col("suggested_status", "Suggested", 15, "text",
            formula='=IF({po_id}{r}="","",'
                    'IF({status}{r}="Cancelled","Cancelled",'
                    'IF({received}{r}<=0,'
                    'IF({order_date}{r}="","Draft","Sent"),'
                    'IF({received}{r}>={qty}{r},"Fully Received",'
                    '"Partially Received"))))',
            note="What the quantities say the status should be. "
                 "Where this disagrees with the Status column the "
                 "alert will tell you."),

        # ---- invoicing --------------------------------------------
        Col("invoice_no", "Invoice no.", 12, "text"),
        Col("invoice_amount", "Invoiced", 11, "money",
            validate=number_check(0, 1000000),
            note="What they actually billed. Where this disagrees "
                 "with the line total, the alert says so - price "
                 "creep on a reorder is the commonest way a margin "
                 "quietly disappears."),
        Col("paid", "Paid", 7, "flag", validate=yesno(),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "No", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("due_date", "Payment due", 11, "date",
            formula='=IF({po_id}{r}="","",'
                    'IF({received_date}{r}="","",'
                    '{received_date}{r}+IFERROR(INDEX(TermDays,'
                    'MATCH(IFERROR(INDEX('
                    '[[Supplier Database.terms]],MATCH({supplier}{r},'
                    '[[Supplier Database.id]],0)),""),'
                    'PaymentTermsList,0)),0)))',
            note="Received date plus the supplier's payment terms."),
        Col("notes", "Notes", 26, "wrap"),

        # ---- flags and timing -------------------------------------
        Col("dup_line", "Duplicate line", 12, "int",
            formula=zero("po_id", 'IF({sku}{r}="",0,'
                                  'COUNTIFS({po_id_first}:'
                                  '{po_id_last},{po_id}{r},'
                                  '{sku_first}:{sku_last},'
                                  '{sku}{r}))'),
            hidden=True,
            note="How many lines on this PO are for this SKU. More "
                 "than one and the same goods can be received twice."),
        Col("valid_line", "Count line", 8, "int",
            formula=zero("po_id", 'IF({sku}{r}="",0,'
                         'IF(COUNTIFS({po_id_first}:{po_id}{r},{po_id}{r},'
                         '{sku_first}:{sku}{r},{sku}{r})=1,1,0))'),
            hidden=True,
            note="Only the first row of a PO and SKU pair contributes stock. "
                 "Resolve duplicate alerts; do not use this as a receiving ledger."),
        Col("is_open", "Open", 6, "int",
            formula=zero("po_id",
                         f'IF({is_open_po("{status}{r}")},'
                         'IF(AND({valid_line}{r}=1,{outstanding}{r}>0),1,0),0)'),
            hidden=True),
        Col("is_committed", "Committed", 9, "int",
            formula=zero("po_id",
                         f'IF({is_committed_po("{status}{r}")},1,0)'),
            hidden=True),
        Col("is_received", "Received?", 9, "int",
            formula=zero("po_id", 'IF({received}{r}>0,1,0)'),
            hidden=True),
        Col("is_over", "Over", 6, "int",
            formula=zero("po_id",
                         'IF({received}{r}>{qty}{r},1,0)'),
            hidden=True),
        Col("days_late", "Days late", 9, "int",
            formula='=IF({po_id}{r}="","",IF({expected}{r}="","",'
                    'IF({received_date}{r}<>"",'
                    '{received_date}{r}-{expected}{r},'
                    'IF({is_open}{r}=1,TodayDate-{expected}{r},""))))',
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}],
            note="Against the expected date: how late the delivery "
                 "was, or how late it is running right now."),
        Col("is_late", "Late", 6, "int",
            formula=zero("po_id", 'IF({days_late}{r}="",0,'
                                  'IF({days_late}{r}>0,1,0))'),
            hidden=True),
        Col("lead_days", "Lead days", 9, "int",
            formula=zero("po_id", 'IF({received_date}{r}="",0,'
                                  'IF({order_date}{r}="",0,'
                                  'MAX(0,{received_date}{r}-'
                                  '{order_date}{r})))'),
            hidden=True,
            note="Order to delivery, measured. This is what builds "
                 "the supplier's real lead time."),
        Col("price_gap", "Price gap", 10, "money",
            formula='=IF({po_id}{r}="","",'
                    'IF({invoice_amount}{r}<=0,"",'
                    'ROUND({invoice_amount}{r}-{total}{r},2)))',
            cf=[{"type": "cell", "criteria": ">", "value": 0.004,
                 "fmt": "bad"},
                {"type": "cell", "criteria": "<", "value": -0.004,
                 "fmt": "warn"}],
            note="Invoice against what you expected to pay."),
        Col("cost_drift", "Cost drift", 10, "percent0",
            formula='=IF({po_id}{r}="","",'
                    f'IF({lookup_product_num_zero("cost")[1:]}<=0,"",'
                    'IF({unit_cost}{r}<=0,"",'
                    'ROUND({unit_cost}{r}/'
                    f'{lookup_product_num_zero("cost")[1:]}-1,4))))',
            cf=[{"type": "cell", "criteria": ">", "value": 0.1,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.02,
                 "fmt": "warn"}],
            note="This order's unit cost against the standing cost "
                 "on the product record. A supplier putting prices "
                 "up 12% shows here before it shows in your margin."),

        month_col("order_date"),
        date_num_col("order_date", "order_num"),
        date_num_col("received_date", "received_num"),
        seq_num_col("po_id"),

        Col("po_print_rank", "Print line", 9, "int",
            formula=zero("po_id",
                         'IF({po_id}{r}<>PrintPO,0,{line_no}{r})'),
            hidden=True,
            note="Line number within the PO currently typed on the "
                 "Printable Orders & Invoices tab, and zero on every "
                 "other row. That is how the printable gathers the "
                 "lines of one order without an array formula."),
        Col("chase_key", "Chase key", 9, "number",
            formula=zero("po_id",
                         'IF({is_open}{r}=0,0,'
                         'IF({days_late}{r}="",1000000,'
                         'IF({days_late}{r}>0,'
                         '3000000+{days_late}{r}*1000,1000000))+'
                         'ROUND({outstanding_value}{r},0))'),
            hidden=True),
        Col("chase_rank", "Chase rank", 9, "int",
            formula=zero("po_id",
                         'IF({is_open}{r}=0,0,'
                         'COUNTIFS({chase_key_first}:'
                         '{chase_key_last},">"&{chase_key}{r})+'
                         'COUNTIFS({chase_key_first}:{chase_key}{r},'
                         '{chase_key}{r}))'),
            hidden=True,
            note="Open deliveries, late ones first, then by how "
                 "much money is tied up in them."),
        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    # expected date defaults to the supplier's quoted lead time
    for col in cols:
        if col.key == "expected":
            col.note += (" Shown blank here; the Suggested status and "
                         "late columns only work once it is set.")

    return SheetSpec(
        name=NAME,
        title="Purchase Orders",
        subtitle=("One row per order line. One receiving cell per "
                  "line - which is why the same delivery cannot be "
                  "booked in twice."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("purchases", cfg),
        help_text=("Raise the order, send it, and when the boxes "
                   "arrive put the quantity into Qty received. Stock "
                   "moves by itself, the weighted average cost "
                   "updates, and the supplier's lead time scorecard "
                   "takes note of how long they took."),
        extra_notes=[
            "If a second shipment arrives against the same line, "
            "update Qty received to the running total - 30 arrived, "
            "then 20 more, so the cell reads 50. Do not add a second "
            "line for the same PO and SKU: that is the one way to "
            "create a duplicate. Only the first PO/SKU line contributes "
            "to inventory; correct any duplicate alerts promptly. "
            "Duplicates under different PO numbers are not detectable.",
            "Freight on the line is not optional bookkeeping. Landed "
            "cost per unit is what the weighted average is built "
            "from, so carriage left off the order is margin you "
            "think you have and do not.",
        ],
    )


def _alert() -> str:
    return alert_chain("po_id", [
        ('{dup_line}{r}>1',
         "Urgent - duplicate PO and SKU; only the first line counts"),
        ('{sku}{r}=""', "Add - which product this line is for"),
        ('{supplier}{r}=""', "Add - supplier"),
        ('{qty}{r}<=0', "Add - quantity"),
        ('{unit_cost}{r}<=0', "Add - unit cost"),
        ('{status}{r}="Cancelled"', [
            ('{received}{r}>0',
             "Check - cancelled but stock was received against it"),
        ], "OK"),
        ('{is_over}{r}=1',
         "Urgent - received more than was ordered, check the count"),
        ('AND({received}{r}>0,{received_date}{r}="")',
         "Add - date the delivery was received"),
        ('AND({received}{r}>0,{condition}{r}="")',
         "Check - how did the delivery arrive?"),
        # AND() evaluates every argument, so ABS() still meets the
        # blank price_gap of a continuation line even though the
        # invoice test in front of it is already false. Coerce it.
        ('AND({invoice_amount}{r}>0,ABS(IFERROR({price_gap}{r}*1,0))>'
         'PriceGapTolerance)',
         "Action - invoice does not match the order value"),
        ('AND({status}{r}<>"",{status}{r}<>{suggested_status}{r})',
         "Check - status does not match what has been received"),
        ('AND({is_open}{r}=1,{days_late}{r}<>"",{days_late}{r}>0)',
         "Chase - delivery is overdue"),
        ('AND({status}{r}="Draft",{order_date}{r}<>"")',
         "Send - drafted and dated but never sent"),
        ('AND({received}{r}>=({qty}{r}),{qty}{r}>0,{paid}{r}="No",'
         '{due_date}{r}<>"",{due_date}{r}<TodayDate)',
         "Overdue - supplier invoice is past its due date"),
        ('AND({received}{r}>0,{paid}{r}="")',
         "Check - received, but is it paid?"),
        ('{expected}{r}=""', "Add - expected delivery date"),
    ])
