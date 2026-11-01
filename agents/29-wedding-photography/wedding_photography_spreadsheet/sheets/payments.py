"""Payments & Invoices - every instalment, due and received.

Wedding work is paid in pieces over a year or more, which is why a
photographer can be busy, fully booked and still short of money in
March.  One row per instalment, joined to the wedding by Booking ID.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, booking_client_col, blank, date_num_col, id_col, lookup_booking,
                     month_col, money_cf, owing_cf, status_cf, year_col,
                     zero)

NAME = "Payments & Invoices"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "InvoicePrefix", digits=cfg.digits("invoice"),
               header="Invoice ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="The wedding this instalment belongs to. The booking "
                 "adds up everything received against its ID.",
            group="The invoice"),
        Col("couple", "Couple", 20, "text",
            formula=lookup_booking("client_name"), group="The invoice"),
        booking_client_col(),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The invoice"),
        Col("stage", "Stage", 14, "text",
            validate=list_from("PaymentStageList"),
            note="Deposit, second instalment, balance, an add-on "
                 "bought later, or a refund.",
            group="The invoice"),
        Col("reference", "Your reference", 15, "text",
            note="Your own invoice number if you raise them elsewhere.",
            group="The invoice"),
        Col("description", "What it is for", 26, "wrap",
            group="The invoice"),

        # ---- the money --------------------------------------------------------
        Col("amount", "Amount due", 12, "money",
            validate=number_check(-1000000, 1000000), cf=money_cf(),
            note="Enter a refund as a negative number so the totals "
                 "stay right.",
            group="The money"),
        Col("due_date", "Due", 11, "date",
            validate=date_check(), group="The money"),
        Col("received", "Received", 12, "money",
            validate=number_check(-1000000, 1000000),
            note="What actually arrived. A part payment is fine - "
                 "leave the amount due alone and the balance shows.",
            group="The money"),
        Col("received_date", "Received on", 12, "date",
            validate=date_check(), group="The money"),
        Col("method", "How", 13, "text",
            validate=list_from("PaymentMethodList"), group="The money"),
        Col("fee", "Processing fee", 12, "money",
            validate=number_check(0, 100000),
            note="What the card processor or bank took. Small per "
                 "payment, not small over a year.",
            group="The money"),
        Col("net", "Net to you", 12, "money",
            formula=zero("booking",
                         'ROUND(IF({received}{r}="",0,{received}{r})-'
                         'IF({fee}{r}="",0,{fee}{r}),2)'),
            cf=money_cf(), group="The money"),
        Col("balance", "Still due", 11, "money",
            formula=zero("booking",
                         'ROUND(IF({amount}{r}="",0,{amount}{r})-'
                         'IF({received}{r}="",0,{received}{r}),2)'),
            cf=owing_cf(), group="The money"),

        # ---- where it stands ---------------------------------------------------
        Col("status", "Status", 13, "status",
            formula=blank("booking",
                          'IF({amount}{r}="","Draft",'
                          'IF(IF({amount}{r}<0,{balance}{r}>=-0.004,{balance}{r}<=0.004),"Paid",'
                          'IF(IF({amount}{r}<0,IF({received}{r}="",0,{received}{r})<0,IF({received}{r}="",0,{received}{r})>0),'
                          'IF({due_date}{r}="","Part paid",'
                          'IF(TodayDate>{due_date}{r},"Overdue",'
                          '"Part paid")),'
                          'IF({due_date}{r}="","Unpaid",'
                          'IF(TodayDate>{due_date}{r},"Overdue",'
                          '"Unpaid")))))'),
            cf=status_cf(), group="Where it stands"),
        Col("days_overdue", "Days overdue", 11, "int",
            formula=zero("booking",
                         'IF({due_date}{r}="",0,'
                         'IF(IF({amount}{r}<0,{balance}{r}>=-0.004,{balance}{r}<=0.004),0,'
                         'MAX(0,TodayDate-{due_date}{r})))'),
            group="Where it stands"),
        Col("days_to_pay", "Days taken", 10, "int",
            formula=blank("booking",
                          'IF({due_date}{r}="","",'
                          'IF({received_date}{r}="","",'
                          '{received_date}{r}-{due_date}{r}))'),
            note="Negative means they paid early. Worth knowing who "
                 "does.",
            group="Where it stands"),
        Col("reminders", "Reminders sent", 11, "int",
            validate=number_check(0, 50), group="Where it stands"),
        Col("last_reminder", "Last reminder", 12, "date",
            validate=date_check(), group="Where it stands"),
        Col("notes", "Notes", 26, "wrap", group="Where it stands"),

        # ---- plumbing -----------------------------------------------------------
        month_col("received_date", "month", "Month received"),
        year_col("received_date"),
        date_num_col("due_date", "due_num", "Due date number"),
        date_num_col("received_date", "paid_num", "Paid date number"),
        Col("is_paid", "Paid flag", 9, "flag",
            formula=blank("booking",
                          'IF({amount}{r}="","No",IF(IF({amount}{r}<0,{balance}{r}>=-0.004,{balance}{r}<=0.004),"Yes","No"))'),
            hidden=True),
        Col("is_late", "Late flag", 9, "flag",
            formula=blank("booking",
                          'IF({days_overdue}{r}>0,"Yes","No")'),
            hidden=True),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({amount}{r}="","Add - no amount on this invoice",'
                'IF(IF({amount}{r}<0,{balance}{r}>=-0.004,{balance}{r}<=0.004),"OK",'
                'IF({due_date}{r}="","Add - no due date",'
                'IF({days_overdue}{r}>30,'
                '"Urgent - over a month overdue",'
                'IF({days_overdue}{r}>0,'
                'IF({reminders}{r}>=2,'
                '"Urgent - chased twice, still unpaid",'
                '"Overdue - send a reminder"),'
                'IF({due_date}{r}-TodayDate<=7,'
                '"Due - payment due within the week",'
                'IF({wedding_date}{r}<>"",'
                'IF({wedding_date}{r}-TodayDate<=FinalPaymentDays,'
                '"Chase - wedding is close and this is unpaid","OK"),'
                '"OK"))))))))'),
            cf=alert_cf(),
            note="Review this column and filter rather than sorting rows.",
            group="Where it stands"),
    ]

    return SheetSpec(
        name=NAME,
        title="Payments & Invoices",
        subtitle=("Every instalment for every wedding - what is due, "
                  "what has arrived and what is late"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("payments", cfg),
        help_text=(
            "One row per instalment. A typical wedding has three: a "
            "deposit to hold the date, a second payment some months "
            "out and the balance before the day. Put the Booking ID on "
            "every row and the wedding adds them up for you."),
        extra_notes=[
            "The booking row works out what the deposit and the "
            "balance should be from your rules on Settings. This tab "
            "records what you actually invoiced and what actually "
            "arrived - the two are allowed to differ, and the "
            "difference is the point.",
            "Record processing fees. Two per cent on a $2,500 wedding "
            "is $50, and across twenty-four weddings it is a lens.",
            "Enter refunds and chargebacks as negative amounts rather "
            "than deleting the original row, so the history survives.",
        ],
    )
