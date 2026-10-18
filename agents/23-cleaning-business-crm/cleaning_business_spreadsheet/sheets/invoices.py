"""The Invoices register."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Invoices")
    samples = sd.INVOICES if cfg.include_sample_data else []
    terms = cfg.payment_terms_days
    tax = cfg.tax_rate

    columns = [
        Col("id", "Invoice ID", 11, "text",
            formula='IF({invoice_number}{r}="","",'
                    '"INV-"&TEXT(ROW()-4,"0000"))'),
        Col("invoice_number", "Invoice #", 14, "text",
            note="Referenced by Payments, Invoice Lines and the "
                 "printable invoice."),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("due", "Due", 13, "date_locked",
            formula='IF({date}{r}="","",{date}{r}+' + str(terms) + ')',
            note=f"Invoice date plus {terms} day terms."),
        Col("client", "Client", 24, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("property", "Property", 22, "text",
            validate={"type": "list", "source": "=Properties_Names",
                      "ignore_blank": True}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("quote_ref", "From Quote", 13, "text",
            validate={"type": "list", "source": "=Quotes_Numbers",
                      "ignore_blank": True}),
        Col("subtotal", "Subtotal", 13, "money_locked",
            formula='IF({invoice_number}{r}="","",'
                    'SUMIFS([[Invoice Lines.line_total]],'
                    '[[Invoice Lines.invoice_ref]],{invoice_number}{r}))',
            note="Sum of the Invoice Lines for this invoice number."),
        Col("tax", cfg.tax_label, 12, "money_locked",
            formula='IF({invoice_number}{r}="","",'
                    'ROUND({subtotal}{r}*' + str(tax) + ',2))'),
        Col("total", "Total", 14, "money_locked",
            formula='IF({invoice_number}{r}="","",'
                    '{subtotal}{r}+{tax}{r})'),
        Col("paid", "Paid", 13, "money_locked",
            formula='IF({invoice_number}{r}="","",'
                    'SUMIFS([[Payments.amount]],'
                    '[[Payments.invoice_ref]],{invoice_number}{r}))',
            note="Sum of the Payments tab for this invoice number."),
        Col("balance", "Balance", 13, "money_locked",
            formula='IF({invoice_number}{r}="","",'
                    'ROUND({total}{r}-{paid}{r},2))'),
        Col("status", "Status", 12, "center",
            validate={"type": "list", "source": [
                "Draft", "Sent", "Part paid", "Paid", "Overdue",
                "Written off"]}),
        Col("job_done", "Job Status", 13, "text_locked",
            formula='IF({job_ref}{r}="","",IFERROR(INDEX([[Jobs.status]],'
                    'MATCH({job_ref}{r},[[Jobs.job_number]],0)),""))',
            note="Make sure the job is completed before invoicing."),
        Col("notes", "Notes", 26, "text"),
    ]

    spec = SheetSpec(
        name="Invoices",
        title="Invoices",
        subtitle="One row per invoice. Lines live on Invoice Lines; money "
                 "in lands on Payments. The balance chases itself.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
    spec.col("balance").cf = [
        {"type": "cell", "criteria": "greater than", "value": 0.01,
         "style": "warning"},
        {"type": "cell", "criteria": "less than or equal to", "value": 0,
         "style": "good"},
    ]
    return spec
