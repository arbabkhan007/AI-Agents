"""6. Stock Movement Log - the audit trail, and the only way to adjust.

Every change to stock that is not a purchase receipt, a sale or a
return gets written here, with a reason. This is deliberately the only
place a human can push a stock figure up or down by hand, and even
here you cannot do it anonymously: the row carries a type, a signed
quantity, a reason and your name.

The log is also where damage and loss are recorded, so "where did
eleven candles go" always has an answer.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, date_num_col,
                     id_col, lookup_product_num_zero,
                     month_col, product_name_col, seq_num_col,
                     sku_col, status_cf, zero)
from ..writer import date_check, list_from, number_check

NAME = "Stock Movement Log"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("sku", "MovementPrefix", digits=cfg.digits("movement"),
               header="Movement ID"),
        Col("date", "Date", 11, "date", validate=date_check(),
            note="When the stock actually moved, not when you got "
                 "round to typing it."),
        sku_col(header="SKU",
                note="Pick the product. Every movement is against one "
                     "SKU - split a mixed delivery across rows."),
        product_name_col(),
        Col("type", "Movement type", 16, "text",
            validate=list_from("MovementTypeList"),
            note="What happened. The type decides the sign: a "
                 "purchase receipt adds, damage removes, an "
                 "adjustment carries whatever sign you type."),
        Col("qty", "Quantity", 10, "int",
            validate=number_check(-1000000, 1000000),
            note="Always a positive number, except on an Adjustment "
                 "row where a negative is how you say 'we have fewer "
                 "than the system thinks'."),
        Col("direction", "In / out", 9, "int",
            formula=zero("sku", 'IFERROR(INDEX(MovementSign,'
                                'MATCH({type}{r},MovementTypeList,'
                                '0)),0)'),
            hidden=True),
        Col("signed_qty", "Change", 9, "int",
            formula=zero("sku", 'IF({direction}{r}=0,{qty}{r},'
                                '{direction}{r}*ABS({qty}{r}))'),
            note="The quantity with its sign applied. An adjustment "
                 "keeps the sign you typed; everything else gets the "
                 "sign its movement type implies.",
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "good"}]),
        Col("reason", "Reason", 30, "wrap",
            note="Required on an adjustment or a write-off. In six "
                 "months this sentence is the only thing standing "
                 "between you and a mystery."),
        Col("reference", "Reference", 13, "text",
            note="The PO, order number, audit ID or invoice this "
                 "relates to, if any."),
        Col("location", "Location", 11, "text",
            validate=list_from("LocationList")),
        Col("to_location", "Moved to", 11, "text",
            validate=list_from("LocationList"),
            note="Only on a transfer. Leave blank otherwise."),
        Col("recorded_by", "Recorded by", 13, "text",
            validate=list_from("StaffList"),
            note="Who made the change. Not bureaucracy - the person "
                 "who wrote the row is usually the only one who "
                 "remembers why."),
        Col("cost_each", "Cost each", 10, "money",
            formula=blank("sku", 'IFERROR(INDEX('
                                 '[[Inventory Tracker.avg_cost]],'
                                 'MATCH({sku}{r},'
                                 '[[Inventory Tracker.sku]],0))*1,'
                                 f'{lookup_product_num_zero("cost")[1:]})'),
            note="Weighted average cost at the time you look, used "
                 "to value what moved."),
        Col("value", "Value", 11, "money",
            formula=zero("sku",
                         'ROUND(ABS({signed_qty}{r})*'
                         '{cost_each}{r},2)'),
            note="What this movement was worth at cost. A write-off "
                 "row is a real loss and this is its size."),

        # ---- the three buckets the Inventory Tracker reads --------
        Col("damaged", "Damaged qty", 10, "int",
            formula=zero("sku",
                         'IF({type}{r}="Damaged",ABS({qty}{r}),'
                         'IF({type}{r}="Lost or stolen",'
                         'ABS({qty}{r}),0))'),
            hidden=True,
            note="Damage and loss, summed by the Inventory Tracker."),
        Col("adjustment", "Adjustment qty", 11, "int",
            formula=zero("sku",
                         'IF({type}{r}="Adjustment",{qty}{r},'
                         'IF({type}{r}="Found in count",'
                         'ABS({qty}{r}),'
                         'IF({type}{r}="Sample or gift",'
                         '-ABS({qty}{r}),'
                         'IF({type}{r}="Used in production",'
                         '-ABS({qty}{r}),'
                         'IF({type}{r}="Supplier return",'
                         '-ABS({qty}{r}),0)))))'),
            hidden=True,
            note="Everything that is a correction rather than a "
                 "trade. Receipts, sales and returns are NOT in "
                 "here - they are counted from their own tabs, and "
                 "counting them twice is the classic way a stock "
                 "spreadsheet drifts."),
        Col("is_writeoff", "Write-off", 8, "int",
            formula=zero("sku", 'IF({damaged}{r}>0,1,0)'),
            hidden=True),
        Col("is_manual", "Manual", 7, "int",
            formula=zero("sku",
                         'IF({type}{r}="Adjustment",1,'
                         'IF({type}{r}="Found in count",1,0))'),
            hidden=True),

        month_col("date"),
        date_num_col("date", "date_num"),
        seq_num_col("sku"),

        Col("stock_after", "Stock after", 11, "int",
            formula=blank("sku", 'IFERROR(INDEX('
                                 '[[Inventory Tracker.current]],'
                                 'MATCH({sku}{r},'
                                 '[[Inventory Tracker.sku]],0))*1,"")'),
            note="Current stock for this SKU as things stand now - "
                 "useful when you are reading the log to work out "
                 "where a number came from."),
        Col("flag", "Check", 14, "status",
            formula='=IF({sku}{r}="","",'
                    'IF({is_manual}{r}=1,"Manual",'
                    'IF({is_writeoff}{r}=1,"Write-off","Routine")))',
            cf=status_cf()),
        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Stock Movement Log",
        subtitle=("Every stock change that is not a purchase, a sale "
                  "or a return - with a reason attached to it."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("movements", cfg),
        help_text=("This is the only place in the workbook where you "
                   "can move stock by hand, and the row will not let "
                   "you do it silently: pick a type, sign the "
                   "quantity, say why."),
        extra_notes=[
            "Do not log purchase receipts, wholesale shipments or "
            "retail sales here. Those are counted from the Purchase "
            "Orders, Wholesale Orders and Retail Sales tabs, and a "
            "duplicate row here would double count them. Use this "
            "log for damage, loss, gifts, production use, transfers "
            "and corrections.",
            "Adjustment is the one type that takes the sign you "
            "type. If a count says you have eleven fewer, enter -11 "
            "and write the reason. Everything else takes its sign "
            "from the movement type.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{date}{r}=""', "Add - movement date"),
        ('{type}{r}=""', "Add - movement type"),
        ('{qty}{r}=0', "Add - quantity"),
        ('AND({is_manual}{r}=1,{reason}{r}="")',
         "Urgent - manual adjustment with no reason given"),
        ('AND({is_writeoff}{r}=1,{reason}{r}="")',
         "Action - write-off needs a reason"),
        ('{recorded_by}{r}=""', "Add - who recorded this"),
        ('AND({type}{r}="Transfer out",{to_location}{r}="")',
         "Add - where it was transferred to"),
        ('AND({direction}{r}=1,{qty}{r}<0)',
         "Check - an incoming movement with a negative quantity"),
        ('{date}{r}>TodayDate', "Check - dated in the future"),
        ('AND({is_writeoff}{r}=1,{value}{r}>WriteoffReview)',
         "Action - large write-off, worth a second look"),
    ])
