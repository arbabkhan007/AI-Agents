"""17. Stock Audit - counting, and what to do with the difference.

You count the shelf, you type what you found, and the sheet tells you
the variance against what the system believed. That part is easy.

The part most stock spreadsheets get wrong is what happens next. A
count does not silently overwrite your stock figure here. It produces
a number and a prompt: post the difference as an adjustment on the
Stock Movement Log, with a reason. That way the stock figure still
reconciles to a list of events rather than to somebody's memory of a
Tuesday afternoon, and six months later the variance is still
explainable.

The Posted column is how you mark that you have done it.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, date_num_col,
                     id_col, lookup_product_num_zero,
                     month_col, product_name_col, seq_num_col,
                     sku_col, status_cf, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Stock Audit"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("sku", "AuditPrefix", digits=cfg.digits("audit"),
               header="Audit ID"),
        Col("date", "Count date", 11, "date", validate=date_check()),
        Col("audit_type", "Type", 13, "text",
            validate=list_from("AuditTypeList"),
            note="A full stocktake, a cycle count of the A lines, "
                 "or a spot check because something looked wrong."),
        sku_col(),
        product_name_col(),
        Col("location", "Location", 11, "text",
            validate=list_from("LocationList")),
        Col("counted_by", "Counted by", 13, "text",
            validate=list_from("StaffList")),

        Col("system_qty", "System at count", 13, "int",
            validate=number_check(-1000000, 1000000),
            note="Manually enter the Inventory Tracker quantity at count time. "
                 "This snapshot keeps the variance stable after adjustments."),
        Col("current_qty", "Current stock", 12, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.current]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            note="Live stock now, not the historical count snapshot."),
        Col("counted_qty", "Counted", 10, "int",
            validate=number_check(0, 1000000),
            note="What is actually on the shelf. Count first, then "
                 "look at the system figure - knowing the answer "
                 "first is how counts come out right and stock "
                 "stays wrong."),
        Col("variance", "Variance", 10, "int",
            formula='=IF({sku}{r}="","",IF(OR({counted_qty}{r}="",{system_qty}{r}=""),"",'
                    '{counted_qty}{r}-{system_qty}{r}))',
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"}],
            note="Counted minus system. Negative means there is "
                 "less on the shelf than there should be."),
        Col("variance_pct", "Variance %", 10, "percent0",
            formula='=IF({sku}{r}="","",IF({counted_qty}{r}="","",'
                    'IF({system_qty}{r}<=0,"",'
                    'ROUND({variance}{r}/{system_qty}{r},4))))',
            cf=[{"type": "cell", "criteria": "<", "value": -0.05,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.05,
                 "fmt": "warn"}]),
        Col("unit_cost", "Unit cost", 10, "money4",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.avg_cost]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,'
                                f'{lookup_product_num_zero("cost")[1:]})'),
            hidden=True),
        Col("variance_value", "Value", 11, "money",
            formula='=IF({sku}{r}="","",IF(OR({counted_qty}{r}="",{system_qty}{r}=""),"",'
                    'ROUND({variance}{r}*{unit_cost}{r},2)))',
            cf=[{"type": "cell", "criteria": "<", "value": -0.004,
                 "fmt": "bold_bad"}],
            note="What the difference is worth. This is the number "
                 "to take seriously - twenty missing stickers is "
                 "noise, two missing aprons is not."),

        Col("reason", "Likely reason", 22, "text",
            validate=list_from("VarianceReasonList"),
            note="Your best guess. Patterns show up fast: one SKU "
                 "that is always short has a process problem, not "
                 "a counting problem."),
        Col("recount", "Recounted", 10, "flag",
            validate=yesno("Did somebody count it a second time?"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("posted", "Adjustment posted", 15, "flag",
            validate=yesno("Have you written the adjustment on the "
                           "Stock Movement Log?"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "No", "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}],
            note="The count on its own changes nothing. Until the "
                 "adjustment is on the movement log, the stock "
                 "figure has not moved - and that is deliberate."),
        Col("movement_ref", "Movement ID", 12, "text",
            note="The MOV- reference of the adjustment you posted, "
                 "so the two records point at each other."),
        Col("status", "Status", 12, "status",
            validate=list_from("AuditStatusList"), cf=status_cf()),
        Col("notes", "Notes", 26, "wrap"),

        Col("has_variance", "Has variance", 11, "int",
            formula=zero("sku", 'IF(OR({counted_qty}{r}="",{system_qty}{r}=""),0,'
                                'IF({variance}{r}=0,0,1))'),
            hidden=True),
        Col("unposted", "Unposted", 9, "int",
            formula=zero("sku", 'IF({has_variance}{r}=0,0,'
                                'IF({posted}{r}="Yes",0,1))'),
            hidden=True,
            note="A counted difference nobody has acted on. These "
                 "are what the Dashboard counts."),
        Col("abs_value", "Abs value", 10, "money",
            formula=zero("sku", 'IF(OR({counted_qty}{r}="",{system_qty}{r}=""),0,'
                                'ABS({variance_value}{r}))'),
            hidden=True),
        Col("accuracy", "Accuracy", 9, "percent0",
            formula='=IF({sku}{r}="","",IF({counted_qty}{r}="","",'
                    'IF({system_qty}{r}<=0,"",'
                    'ROUND(1-ABS({variance}{r})/'
                    '{system_qty}{r},4))))',
            cf=[{"type": "cell", "criteria": "<", "value": 0.95,
                 "fmt": "warn"}],
            hidden=True),

        month_col("date"),
        date_num_col("date", "date_num"),
        seq_num_col("sku"),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Stock Audit",
        subtitle=("Count it, compare it, then post the difference as "
                  "an adjustment. A count never silently overwrites "
                  "your stock."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("audit", cfg),
        help_text=("Enter the current system quantity as a snapshot, then "
                   "count the shelf and type what you found. The "
                   "variance appears with what it is worth. Then "
                   "write the adjustment on the Stock Movement Log "
                   "and tick Adjustment posted - that is the step "
                   "that actually moves the stock figure."),
        extra_notes=[
            "Why not just overwrite the stock number? Because a "
            "stock figure that can be typed over is a figure "
            "nobody can explain. Posting the difference as a dated, "
            "signed adjustment means every unit you hold traces "
            "back to an event, including the ones that went "
            "missing.",
            "Count your A lines - the few SKUs holding most of your "
            "money, shown on the Inventory Valuation tab - monthly, "
            "and everything else once or twice a year. A full "
            "stocktake every quarter is a lot of lost Sundays for "
            "very little extra accuracy.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{date}{r}=""', "Add - count date"),
        ('{counted_qty}{r}=""', "Add - what you counted"),
        ('{system_qty}{r}=""', "Add - system quantity snapshot"),
        ('{counted_by}{r}=""', "Add - who counted it"),
        ('AND({has_variance}{r}=1,{abs_value}{r}>LargeLossLevel,'
         '{recount}{r}<>"Yes")',
         "Urgent - big variance, count it again before you post it"),
        ('{unposted}{r}=1',
         "Action - variance found, adjustment not posted yet"),
        ('AND({posted}{r}="Yes",{movement_ref}{r}="")',
         "Add - the movement ID of the adjustment you posted"),
        ('AND({has_variance}{r}=1,{reason}{r}="")',
         "Add - a likely reason for the difference"),
        ('AND({accuracy}{r}<>"",{accuracy}{r}<0.9)',
         "Check - this line is badly out, look at the process"),
        ('{status}{r}=""', "Add - status"),
    ])
