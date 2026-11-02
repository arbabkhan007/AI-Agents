"""17. Invoice & Payments - what you billed and what actually arrived.

Outstanding is the whole point: total minus paid, aged against the
due date that comes from the customer's own payment terms. The
overdue column feeds the dashboard, the customer record and the
chase list, so there is exactly one place where a debt lives.

An invoice can cover one job or a month of them. Put the Job ID on it
when it is one job - that is what closes the loop from quote to job
to money in the bank.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, customer_col,
                     date_num_col, id_col, is_owed_invoice,
                     is_paid_invoice, lookup_customer, money_cf,
                     month_col, owing_cf, pick, service_tax,
                     status_cf, term_days, yesno, zero)

NAME = "Invoice & Payments"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Invoice & Payments",
        subtitle="Every invoice, what has been paid against it, and "
                 "exactly how late the rest of it is.",
        tab_color=Palette.deep,
        rows=cfg.row_count("invoices"),
        samples=sample("invoices", cfg),
        freeze_cols=3,
        help_text=(
            "One row per invoice. The due date comes from the "
            "customer's payment terms, the outstanding amount from "
            "what you have recorded as paid, and the overdue flag "
            "from the two together. Record part payments in the paid "
            "column as they arrive."),
        extra_notes=[
            "This tab records invoices; it does not send them and it "
            "does not take card payments. Use the printable invoice on Route Planner "
            "page to produce the document, then record what happens "
            "here.",
            "Age is counted from the due date, not the invoice date, "
            "so an invoice on 30-day terms is not 'thirty days late' "
            "the moment it is sent.",
            "Writing one off is a decision, not a deletion. Set the "
            "status to 'Written off' and the amount stops being "
            "chased but stays in the record, where it belongs.",
        ],
        columns=[
            id_col("date", "InvoicePrefix", digits=cfg.digits("invoice"),
                   header="Invoice ID",
                   note="Generated, sequential and unique. Put it on "
                        "the job it bills."),
            Col("invoice_number", "Your number", 13, "text",
                note="If your accountant needs a particular numbering "
                     "format, put it here. The ID above is what the "
                     "workbook joins on."),
            Col("date", "Invoice date", 12, "date",
                validate=date_check(),
                note="Start here."),
            customer_col(),
            Col("customer_name", "Customer", 22, "text",
                formula=lookup_customer("name")),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the job this invoice bills."),
                note="For a single-job invoice. Leave blank for a "
                     "monthly or multi-job bill and list the work in "
                     "the description."),
            Col("contract", "Contract ID", 11, "id",
                validate=pick("ContractIDList",
                              "Pick the agreement being billed."),
                note="If this is the regular bill for a standing "
                     "agreement."),
            Col("description", "What for", 34, "wrap",
                note="What the customer sees. 'Grass cutting, April - "
                     "4 visits' saves a phone call."),
            Col("period", "Period covered", 14, "text",
                note="For monthly bills: 'April 2026'."),
            Col("po_number", "PO number", 13, "text",
                note="Commercial customers who need one will not pay "
                     "without it."),

            # ---- the money -------------------------------------------
            Col("subtotal", "Subtotal", 12, "money",
                validate=amount(0, 1000000,
                                "The amount before tax. Leave blank "
                                "to use the job's charge."),
                note="Blank pulls the charge from the Job ID, if "
                     "there is one."),
            Col("job_charge", "From job", 11, "money",
                formula=zero("date",
                             'IF({job}{r}="",0,'
                             'IFERROR(INDEX('
                             '[[Job & Work Orders.charge]],'
                             'MATCH({job}{r},'
                             '[[Job & Work Orders.id]],0))*1,0)+'
                             'IFERROR(INDEX('
                             '[[Job & Work Orders.extras]],'
                             'MATCH({job}{r},'
                             '[[Job & Work Orders.id]],0))*1,0))'),
                hidden=True),
            Col("net", "Net", 11, "money",
                formula=zero("date",
                             'ROUND(IF({subtotal}{r}>0,{subtotal}{r},'
                             '{job_charge}{r}),2)'),
                hidden=True),
            Col("discount", "Discount", 10, "money",
                validate=amount(0, 1000000)),
            Col("tax", "Tax", 10, "money",
                formula=zero("date",
                             service_tax('{net}{r}-{discount}{r}')),
                note="Only if tax is switched on for your business on "
                     "the Settings tab."),
            Col("total", "Total", 12, "money",
                formula=zero("date",
                             'ROUND({net}{r}-{discount}{r}+'
                             '{tax}{r},2)'),
                cf=money_cf(),
                note="What you are asking for."),
            Col("paid", "Paid", 11, "money",
                validate=amount(0, 1000000,
                                "How much has arrived. Part payments "
                                "are fine - put the running total."),
                note="Update as money comes in. The rest follows."),
            Col("paid_date", "Paid on", 11, "date",
                validate=date_check(),
                note="The day the last payment landed."),
            Col("method", "Paid by", 15, "text",
                validate=list_from("PaymentMethodList")),
            Col("outstanding", "Outstanding", 12, "money",
                formula=zero("date",
                             'ROUND({total}{r}-{paid}{r},2)'),
                cf=owing_cf(),
                note="Total minus paid. This is the number the "
                     "dashboard and the customer record both read."),

            # ---- when it is due --------------------------------------
            Col("terms", "Terms", 16, "text",
                validate=pick("PaymentTermsList",
                              "Blank uses the terms on the customer's "
                              "record."),
                note="Blank falls back to the customer's own terms."),
            Col("terms_used", "Terms used", 16, "text",
                formula='=IF({date}{r}="","",'
                        'IF({terms}{r}<>"",{terms}{r},'
                        'IFERROR(INDEX([[Customer CRM.terms]],'
                        'MATCH({customer}{r},'
                        '[[Customer CRM.id]],0))&"","Due on receipt")))',
                hidden=True),
            Col("term_days", "Days allowed", 11, "int",
                formula=zero("date", term_days('{terms_used}{r}')),
                hidden=True),
            Col("due_date", "Due", 11, "date",
                formula='=IF({date}{r}="","",'
                        '{date}{r}+MAX(0,{term_days}{r}))',
                cf=[{"type": "formula",
                     "criteria": '=AND(ISNUMBER({due_date}{r}),'
                                 '{due_date}{r}<TodayDate,'
                                 '{outstanding}{r}>0)',
                     "fmt": "bold_bad"}],
                note="Invoice date plus the days your terms allow."),
            Col("days_late", "Days late", 10, "int",
                formula=zero("date",
                             'IF({outstanding}{r}<=0.004,0,'
                             'MAX(0,TodayDate-'
                             '({date}{r}+MAX(0,{term_days}{r}))))'),
                cf=[{"type": "cell", "criteria": ">=", "value": 60,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": ">=", "value": 30,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "warn"}],
                note="Counted from the due date. Zero once it is paid."),
            Col("age_band", "Age", 13, "text",
                formula='=IF({date}{r}="","",'
                        'IF({outstanding}{r}<=0.004,"Paid",'
                        'IF({days_late}{r}<=0,"Not due yet",'
                        'IF({days_late}{r}<=30,"1-30 days",'
                        'IF({days_late}{r}<=60,"31-60 days",'
                        'IF({days_late}{r}<=90,"61-90 days",'
                        '"Over 90 days"))))))',
                cf=[{"type": "text", "criteria": "containing",
                     "value": "Over 90", "fmt": "bold_bad"},
                    {"type": "text", "criteria": "containing",
                     "value": "61-90", "fmt": "bad"},
                    {"type": "text", "criteria": "containing",
                     "value": "31-60", "fmt": "warn"},
                    {"type": "text", "criteria": "containing",
                     "value": "Paid", "fmt": "good"}],
                note="The ageing bucket the monthly report groups on."),
            Col("status", "Status", 14, "text",
                validate=list_from("InvoiceStatusList"),
                cf=status_cf(),
                note="Set it as things happen. The jobs tab reads it "
                     "back, so there is only ever one version of the "
                     "truth."),
            Col("sent", "Sent", 8, "flag",
                validate=yesno("Has it actually gone to the customer?"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "No", "fmt": "warn"}]),
            Col("reminders", "Reminders sent", 12, "int",
                validate=amount(0, 50, decimal=False),
                note="How many times you have chased. Three and still "
                     "nothing is a different conversation."),
            Col("last_chase", "Last chased", 11, "date",
                validate=date_check()),
            Col("notes", "Notes", 26, "wrap"),

            # ---- flags other tabs read -------------------------------
            Col("is_owed", "Owed", 6, "int",
                formula=zero("date",
                             f'IF(AND({is_owed_invoice("{status}{r}")},'
                             '{outstanding}{r}>0.004),1,0)'),
                hidden=True),
            Col("is_paid", "Paid flag", 7, "int",
                formula=zero("date",
                             f'IF({is_paid_invoice("{status}{r}")},'
                             '1,0)'),
                hidden=True),
            Col("is_overdue", "Overdue", 7, "int",
                formula=zero("date",
                             'IF(AND({is_owed}{r}=1,'
                             '{days_late}{r}>0),1,0)'),
                hidden=True),
            Col("late_rank", "Late rank", 9, "int",
                formula=zero("date",
                             'IF({is_overdue}{r}=0,0,'
                             'COUNTIFS({days_late_first}:'
                             '{days_late_last},">"&{days_late}{r},'
                             '{is_overdue_first}:{is_overdue_last},1)+'
                             'COUNTIFS({days_late_first}:'
                             '{days_late}{r},{days_late}{r},'
                             '{is_overdue_first}:{is_overdue}{r},1))'),
                hidden=True,
                note="1 = the latest invoice you have. The dashboard "
                     "chase list reads this."),
            Col("print_rank", "Print line", 9, "int",
                formula=zero("date",
                             'IF({id}{r}=PrintInvoice,1,0)'),
                hidden=True,
                note="Marks the one invoice the printable page is "
                     "showing."),
            date_num_col("date", "date_num"),
            date_num_col("paid_date", "paid_num", header="Paid #"),
            month_col("date"),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("date", [
                    ('{days_late}{r}>=60',
                     "Urgent - more than sixty days late, decide what "
                     "to do about it"),
                    ('AND({is_overdue}{r}=1,{reminders}{r}=0)',
                     "Chase - overdue and never chased"),
                    ('{is_overdue}{r}=1',
                     "Overdue - past its due date and unpaid"),
                    ('AND({total}{r}>0,{sent}{r}<>"Yes")',
                     "Send - raised but never sent to the customer"),
                    ('{status}{r}="Disputed"',
                     "Urgent - disputed, sort it out before it ages"),
                    ('{total}{r}=0',
                     "Add - no amount on this invoice"),
                    ('AND({outstanding}{r}<-0.004)',
                     "Check - paid more than the invoice, refund or "
                     "credit due"),
                    ('AND({is_owed}{r}=1,{days_late}{r}=0)',
                     "Due - sent and waiting, not yet late"),
                    ('AND({paid}{r}>0,{paid_date}{r}="")',
                     "Add - payment recorded with no date"),
                    ('AND({outstanding}{r}<=0.004,'
                     '{status}{r}<>"Paid",{total}{r}>0)',
                     "Check - fully paid but the status says "
                     "otherwise"),
                ]),
                cf=alert_cf()),
        ],
    )
