"""15. Returns & Damaged Goods - and the one question that matters.

Did it go back on the shelf, or is it gone?

That single yes-or-no decides everything downstream. A restocked
return adds a unit back to stock. A write-off does not - it becomes a
loss at cost, counted against the product's profit and the business's
shrinkage. The Restocked column is the flag the Inventory Tracker
reads, and the condition you choose sets it for you.

Returns are also where supplier quality shows itself. Three defective
units from the same batch is a conversation with the supplier, not an
act of God, and the Claimed column is there so you remember to have
it.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, date_num_col,
                     id_col, is_sellable, lookup_product,
                     lookup_product_num_zero, month_col,
                     product_name_col, seq_num_col, sku_col,
                     status_cf, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Returns & Damaged Goods"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("sku", "ReturnPrefix", digits=cfg.digits("return"),
               header="Return ID"),
        Col("date", "Date", 11, "date", validate=date_check()),
        Col("source", "Came from", 13, "text",
            validate=list_from("ReturnSourceList"),
            note="A retail customer, a stockist, or your own "
                 "warehouse finding breakage."),
        Col("reference", "Order ref", 12, "text",
            note="The sale or wholesale order it came back from, if "
                 "there was one."),
        Col("customer", "Customer", 18, "text"),
        sku_col(),
        product_name_col(),
        Col("qty", "Qty", 7, "int",
            validate=number_check(0, 100000)),
        Col("reason", "Reason", 18, "text",
            validate=list_from("ReturnReasonList")),
        Col("condition", "Condition", 20, "text",
            validate=list_from("ReturnConditionList"),
            note="This is the cell that decides whether the units "
                 "come back into stock. As new and Opened - "
                 "resellable go back; everything else is a loss."),
        Col("restocked", "Restocked", 9, "int",
            formula=zero("sku",
                         f'IF({is_sellable("{condition}{r}")},1,0)'),
            note="Set by the condition. 1 means the units went back "
                 "on the shelf and the Inventory Tracker has "
                 "already counted them."),
        Col("customer_return", "Customer return", 10, "int",
            formula=zero("sku", 'IF(OR({source}{r}="Retail customer",'
                        '{source}{r}="Wholesale customer",{source}{r}="Marketplace"),1,0)'),
            hidden=True),
        Col("warehouse_damage", "Warehouse damage", 10, "int",
            formula=zero("sku", 'IF(AND({source}{r}="Own warehouse",'
                        '{condition}{r}<>"",{restocked}{r}=0),1,0)'), hidden=True),
        Col("location", "Back to", 11, "text",
            validate=list_from("LocationList"),
            note="Where the restocked units went."),

        # ---- money -------------------------------------------------
        Col("unit_cost", "Unit cost", 10, "money4",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.avg_cost]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,'
                                f'{lookup_product_num_zero("cost")[1:]})'),
            hidden=True),
        Col("stock_loss", "Stock loss", 11, "money",
            formula=zero("sku", 'IF({restocked}{r}=1,0,'
                                'ROUND({qty}{r}*{unit_cost}{r},2))'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}],
            note="What the units cost you, where they are not going "
                 "back on the shelf."),
        Col("refund", "Refund given", 12, "money",
            validate=number_check(0, 1000000),
            note="What you gave back to the customer."),
        Col("replacement", "Replacement sent", 14, "flag",
            validate=yesno("A replacement is a second unit of stock "
                           "going out - log it as a sale so the "
                           "stock figures stay right."),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "info"}]),
        Col("return_shipping", "Return postage", 13, "money",
            validate=number_check(0, 100000)),
        Col("total_cost", "Total cost", 11, "money",
            formula=zero("sku", 'ROUND({stock_loss}{r}+'
                                '{refund}{r}+'
                                '{return_shipping}{r},2)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bold_bad"}],
            note="The whole cost of this return: the stock, the "
                 "refund and the postage. Returns are rarely as "
                 "cheap as they look."),

        # ---- supplier fault ----------------------------------------
        Col("supplier", "Supplier ID", 11, "id",
            formula=lookup_product("supplier", missing='""'),
            hidden=True),
        Col("supplier_fault", "Supplier fault", 12, "flag",
            validate=yesno("Was this a manufacturing or packing "
                           "fault at their end?"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "warn"}]),
        Col("claimed", "Claimed back", 11, "flag",
            validate=yesno("Have you actually asked them for a "
                           "credit?"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "No", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("credit_received", "Credit received", 13, "money",
            validate=number_check(0, 1000000)),
        Col("net_loss", "Net loss", 11, "money",
            formula=zero("sku", 'ROUND(MAX(0,{total_cost}{r}-'
                                '{credit_received}{r}),2)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}],
            note="What it cost you after anything the supplier gave "
                 "back."),
        Col("profit_effect", "Profit adjustment", 14, "money",
            formula=zero("sku", 'ROUND(IF({refund}{r}="",0,{refund}{r})+'
                        'IF({return_shipping}{r}="",0,{return_shipping}{r})-'
                        'IF({credit_received}{r}="",0,{credit_received}{r})+'
                        'IF({warehouse_damage}{r}=1,{qty}{r}*{unit_cost}{r},0)-'
                        'IF(AND({customer_return}{r}=1,{restocked}{r}=1),'
                        '{qty}{r}*{unit_cost}{r},0),2)'),
            note="Management adjustment: refund and postage minus credit; "
                 "adds warehouse damage and credits restocked customer units "
                 "against the already-recorded sale COGS. Approximate."),
        Col("status", "Status", 12, "status",
            validate=list_from("ReturnStatusList"), cf=status_cf()),
        Col("notes", "Notes", 26, "wrap",
            note="What was actually wrong with it. Three of these "
                 "saying the same thing is a batch problem."),

        Col("is_writeoff", "Write-off", 8, "int",
            formula=zero("sku", 'IF({restocked}{r}=1,0,1)'),
            hidden=True),
        Col("is_open", "Open", 6, "int",
            formula=zero("sku",
                         'IF({status}{r}="Resolved",0,'
                         'IF({status}{r}="Closed",0,1))'),
            hidden=True),
        Col("unclaimed", "Unclaimed", 9, "money",
            formula=zero("sku",
                         'IF({supplier_fault}{r}<>"Yes",0,'
                         'IF({claimed}{r}="Yes",0,'
                         '{total_cost}{r}))'),
            hidden=True,
            note="Supplier's fault, and you have not asked for the "
                 "money back. The Dashboard adds these up."),

        month_col("date"),
        date_num_col("date", "date_num"),
        seq_num_col("sku"),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Returns & Damaged Goods",
        subtitle=("Restocked or written off - the condition decides, "
                  "and the Inventory Tracker follows."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("returns", cfg),
        help_text=("Log what came back, what state it was in, and "
                   "what it cost you. Pick the condition and the "
                   "restocking takes care of itself - there is no "
                   "need to write a separate stock movement."),
        extra_notes=[
            "Customer returns only add sellable units back; unsellable "
            "customer returns were already sold and do not subtract again. "
            "Own warehouse unsellable units reduce stock. Supplier and "
            "courier cases require separate review and manual adjustment. "
            "Do not duplicate a stock change in the movement log.",
            "Supplier fault plus Claimed back is a small habit that "
            "pays for the workbook. Faulty stock you never claimed "
            "for is money you have decided to donate to your "
            "supplier, and the Dashboard will keep reminding you.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{date}{r}=""', "Add - return date"),
        ('{qty}{r}<=0', "Add - how many came back"),
        ('{source}{r}=""', "Add - return source"),
        ('OR({source}{r}="Supplier",{source}{r}="Courier damage")', "Review - stock needs separate adjustment"),
        ('{condition}{r}=""',
         "Add - condition, nothing can be restocked without it"),
        ('{reason}{r}=""', "Add - reason for the return"),
        ('AND({restocked}{r}=1,{location}{r}="")',
         "Add - where the restocked units went"),
        ('{unclaimed}{r}>0',
         "Action - supplier's fault and no claim made yet"),
        ('AND({supplier_fault}{r}="Yes",{claimed}{r}="Yes",'
         '{credit_received}{r}<=0,{status}{r}<>"Closed")',
         "Chase - claim raised, credit never arrived"),
        ('AND({net_loss}{r}>LargeLossLevel,{status}{r}<>"Closed")',
         "Action - expensive return, worth understanding"),
        ('{status}{r}=""', "Add - status"),
        ('AND({is_open}{r}=1,TodayDate-{date}{r}>30)',
         "Follow up - open for over a month"),
        ('AND({refund}{r}>0,{replacement}{r}="Yes")',
         "Check - refunded and replaced, was that intended?"),
    ])
