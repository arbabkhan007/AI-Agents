"""`Invoices` - invoice register with automatic numbering, tax and ageing."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import DATA_ROW, Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, dup_cf, month_col, owing_cf, status_cf

NAME = "Invoices"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        Col("invoice_no", "Invoice no.", 12, "id",
            formula=blank("client",
                          'InvoicePrefix&TEXT(InvoiceStartNo+ROW()-'
                          f'{DATA_ROW},"0000")'),
            note="Numbered automatically from the first invoice number on "
                 "the Settings tab."),
        Col("date", "Invoice date", 12, "date", validate=date_check()),
        Col("due", "Due date", 12, "date",
            formula=blank("date", '{date}{r}+PaymentTermsDays')),
        Col("client", "Client", 20, "text",
            validate=list_from("ClientNames")),
        Col("booking", "Booking ref", 12, "text",
            validate=list_from("BookingIDs"),
            note="Link a booking and the invoice total is taken straight "
                 "from it. Leave blank to bill manually with Qty x Rate."),
        Col("booking_total", "Booking total", 12, "money",
            # The booking subtotal is used (not the booking total) because
            # this invoice adds the tax itself a few columns to the right.
            formula='=IF({booking}{r}="",0,IFERROR('
                    'INDEX([[Bookings.subtotal]],'
                    'MATCH({booking}{r},[[Bookings.id]],0)),0))'),
        Col("description", "Description of service", 40, "wrap"),
        Col("qty", "Qty", 8, "number", validate=number_check(0, 10000)),
        Col("rate", "Rate", 11, "money", validate=number_check(0, 100000)),
        Col("line_total", "Line amount", 12, "money",
            formula=blank("client",
                          'IF({booking}{r}<>"",{booking_total}{r},'
                          'ROUND(IF({qty}{r}="",0,{qty}{r})'
                          '*IF({rate}{r}="",0,{rate}{r}),2))')),
        Col("fees", "Additional fees", 11, "money",
            validate=number_check(0, 100000)),
        Col("discount", "Discount", 11, "money",
            validate=number_check(0, 100000)),
        Col("subtotal", "Subtotal", 12, "money",
            formula=blank("client",
                          'ROUND({line_total}{r}+IF({fees}{r}="",0,'
                          '{fees}{r})-IF({discount}{r}="",0,'
                          '{discount}{r}),2)')),
        Col("tax", "Tax", 11, "money",
            formula='=IF({subtotal}{r}="","",IF(TaxRegistered<>"Yes",0,'
                    'IF(PricesIncludeTax="Yes",'
                    'ROUND({subtotal}{r}-{subtotal}{r}/(1+TaxRate),2),'
                    'ROUND({subtotal}{r}*TaxRate,2))))'),
        Col("total", "Invoice total", 13, "money",
            formula='=IF({subtotal}{r}="","",IF(PricesIncludeTax="Yes",'
                    '{subtotal}{r},ROUND({subtotal}{r}+{tax}{r},2)))',
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("deposit", "Deposit received", 12, "money",
            formula=blank("invoice_no",
                          'SUMIFS([[Payments.amount]],'
                          '[[Payments.invoice_no]],{invoice_no}{r},'
                          '[[Payments.deposit]],"Yes")'),
            note="Log deposits on the Payments tab with Deposit = Yes."),
        Col("paid", "Amount paid", 12, "money",
            formula=blank("invoice_no",
                          'SUMIFS([[Payments.net]],'
                          '[[Payments.invoice_no]],{invoice_no}{r})')),
        Col("refunded", "Refunded", 11, "money",
            formula=blank("invoice_no",
                          'SUMIFS([[Payments.refund]],'
                          '[[Payments.invoice_no]],{invoice_no}{r})')),
        Col("balance", "Balance due", 12, "money",
            formula=blank("client",
                          'ROUND(IF({status}{r}="Cancelled",0,'
                          '{total}{r}-{paid}{r}),2)'),
            cf=owing_cf()),
        Col("status", "Invoice status", 13, "status",
            validate=list_from("InvoiceStatusList"), cf=status_cf(),
            note="You control Draft / Sent / Cancelled. The payment status "
                 "next to it is calculated from the Payments tab."),
        Col("pay_status", "Payment status", 15, "status",
            formula=blank(
                "invoice_no",
                'IF({status}{r}="Cancelled","Cancelled",'
                'IF({balance}{r}<=0.004,"Paid",'
                'IF({paid}{r}>0.004,IF(AND({due}{r}<>"",TODAY()>{due}{r}),'
                '"Overdue - part paid","Partially paid"),'
                'IF(AND({due}{r}<>"",TODAY()>{due}{r}),"Overdue",'
                'IF({status}{r}="Draft","Draft","Unpaid")))))'),
            cf=status_cf()),
        Col("days_overdue", "Days overdue", 10, "int",
            formula='=IF(OR({due}{r}="",{balance}{r}<=0.004),"",'
                    'MAX(0,TODAY()-{due}{r}))',
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}]),
        Col("aging", "Ageing bucket", 13, "status",
            formula=blank("invoice_no",
                          'IF({balance}{r}<=0.004,"Paid",'
                          'IF({days_overdue}{r}="","Not due",'
                          'IF({days_overdue}{r}=0,"Current",'
                          'IF({days_overdue}{r}<=30,"1-30 days",'
                          'IF({days_overdue}{r}<=60,"31-60 days",'
                          'IF({days_overdue}{r}<=90,"61-90 days",'
                          '"90+ days"))))))'),
            cf=[{"type": "text", "criteria": "containing", "value": "Paid",
                 "fmt": "good"},
                {"type": "text", "criteria": "containing",
                 "value": "90+", "fmt": "bold_bad"},
                {"type": "text", "criteria": "containing",
                 "value": "61-90", "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "31-60", "fmt": "warn"}]),
        Col("late_fee", "Suggested late fee", 11, "money",
            formula='=IF(OR({days_overdue}{r}="",{days_overdue}{r}=0),0,'
                    'ROUND({balance}{r}*LateFeePct,2))'),
        Col("sent_date", "Sent on", 12, "date", validate=date_check()),
        Col("reminder_sent", "Reminder sent", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("dup_check", "Number check", 13, "status",
            formula=blank("invoice_no",
                          'IF(COUNTIF([[Invoices.invoice_no]],'
                          '{invoice_no}{r})>1,"Duplicate number","OK")'),
            cf=dup_cf()),
        Col("notes", "Invoice notes", 30, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 24, "status",
            formula=blank(
                "invoice_no",
                'IF({status}{r}="Draft","Action - still a draft",'
                'IF({pay_status}{r}="Overdue","Overdue - chase payment",'
                'IF({pay_status}{r}="Overdue - part paid",'
                '"Overdue - chase the balance",'
                'IF(AND({balance}{r}>0.004,{due}{r}<>"",'
                '{due}{r}-TODAY()<=ReminderLeadDays,{due}{r}>=TODAY()),'
                '"Due soon - send a reminder","OK"))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Invoices",
        subtitle="Automatic numbering, due dates, tax, balances, ageing "
                 "buckets and overdue alerts - all from the booking you "
                 "link.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.good_text,
        freeze_cols=2,
        samples=sample(cfg).invoices,
        help_text="Type the client name to create the invoice number. "
                  "Link a Booking ID to bill the calculated booking total, "
                  "or use Qty x Rate for anything custom.",
    )
