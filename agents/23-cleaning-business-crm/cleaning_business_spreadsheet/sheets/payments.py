"""The Payments register - money in."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Payments")
    samples = sd.PAYMENTS if cfg.include_sample_data else []

    columns = [
        Col("id", "Payment ID", 11, "text",
            formula='IF({amount}{r}="","",'
                    '"PAY-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("invoice_ref", "Invoice #", 14, "text",
            validate={"type": "list", "source": "=Invoices_Numbers",
                      "ignore_blank": True},
            note="The invoice this payment settles."),
        Col("client", "Client", 24, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("amount", "Amount", 13, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 10000000}),
        Col("method", "Method", 13, "center",
            validate={"type": "list", "source": [
                "Cash", "Card", "Bank transfer", "Check", "Online",
                "Direct debit", "Other"]}),
        Col("reference", "Reference", 16, "text"),
        Col("notes", "Notes", 22, "text"),
        Col("month", "Month", 13, "date_locked",
            formula='IF({date}{r}="","",DATE(YEAR({date}{r}),'
                    'MONTH({date}{r}),1))'),
        Col("matched", "Matched?", 11, "text_locked",
            formula='IF({invoice_ref}{r}="","",'
                    'IF(COUNTIF([[Invoices.invoice_number]],'
                    '{invoice_ref}{r})>0,"OK","NOT FOUND"))',
            note="Every payment must reference a real invoice number."),
    ]

    spec = SheetSpec(
        name="Payments",
        title="Payments",
        subtitle="Money in, tied to an invoice number. Invoices update "
                 "their paid and balance columns from these rows.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
    spec.col("matched").cf = [
        {"type": "text", "criteria": "containing", "value": "NOT FOUND",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "OK",
         "style": "good"},
    ]
    return spec
