"""`Payments` - money received, deposits, tips, refunds and reconciliation."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, month_col, status_cf

NAME = "Payments"


def _inv(field: str, fallback: str = '""') -> str:
    return (f'IFERROR(INDEX([[Invoices.{field}]],'
            f'MATCH({{invoice_no}}{{r}},[[Invoices.invoice_no]],0)),'
            f'{fallback})')


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"PM-"'),
        Col("date", "Payment date", 12, "date", validate=date_check()),
        Col("client", "Client", 20, "text",
            validate=list_from("ClientNames")),
        Col("invoice_no", "Invoice no.", 12, "text",
            validate=list_from("InvoiceNos"),
            note="Match the payment to an invoice so balances update "
                 "automatically. Leave blank for an unlinked payment."),
        Col("amount", "Amount applied", 12, "money",
            validate=number_check(0, 1000000),
            note="The part of the payment that pays down the invoice."),
        Col("method", "Payment method", 16, "text",
            validate=list_from("PaymentMethodList")),
        Col("reference", "Reference", 14, "text"),
        Col("tip", "Tip / gratuity", 10, "money",
            validate=number_check(0, 100000)),
        Col("late_fee", "Late fee collected", 10, "money",
            validate=number_check(0, 100000)),
        Col("refund", "Refund given", 11, "money",
            validate=number_check(0, 1000000)),
        Col("net", "Applied to invoice", 12, "money",
            formula=blank("date",
                          'ROUND(IF({amount}{r}="",0,{amount}{r})'
                          '-IF({refund}{r}="",0,{refund}{r}),2)')),
        Col("received", "Total cash in", 12, "money",
            formula=blank("date",
                          'ROUND(IF({amount}{r}="",0,{amount}{r})'
                          '+IF({tip}{r}="",0,{tip}{r})'
                          '+IF({late_fee}{r}="",0,{late_fee}{r})'
                          '-IF({refund}{r}="",0,{refund}{r}),2)'),
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("deposit", "Deposit?", 9, "flag", validate=yes_no()),
        Col("confirmed", "Cleared / confirmed", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("reconciled", "Reconciled to bank", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("inv_total", "Invoice total", 12, "money",
            formula=blank("invoice_no", _inv("total", "0"))),
        Col("inv_balance", "Invoice balance", 12, "money",
            formula=blank("invoice_no", _inv("balance", "0")),
            cf=[{"type": "cell", "criteria": ">", "value": 0.004,
                 "fmt": "warn"}]),
        Col("notes", "Notes", 30, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 22, "status",
            formula=blank(
                "date",
                'IF({confirmed}{r}<>"Yes","Unconfirmed - check it cleared",'
                'IF({reconciled}{r}<>"Yes","To reconcile",'
                'IF(AND({invoice_no}{r}<>"",{inv_balance}{r}>0.004),'
                '"Invoice still has a balance","OK")))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Payment Tracking",
        subtitle="Every cash, card, transfer, wallet and deposit payment, "
                 "with tips, refunds and bank reconciliation.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.good_text,
        freeze_cols=2,
        samples=sample(cfg).payments,
        help_text="Record payments the day they land. 'Applied to invoice' "
                  "clears the balance; 'Total cash in' (tips and late fees "
                  "included) is what the dashboard counts as revenue.",
    )
