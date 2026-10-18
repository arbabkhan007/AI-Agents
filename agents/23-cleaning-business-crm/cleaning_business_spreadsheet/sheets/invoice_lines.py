"""Invoice Lines - the billed detail behind each invoice."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Invoice Lines")
    samples = sd.INVOICE_LINES if cfg.include_sample_data else []

    columns = [
        Col("id", "Line ID", 11, "text",
            formula='IF({invoice_ref}{r}="","",'
                    '"IL-"&TEXT(ROW()-4,"0000"))'),
        Col("invoice_ref", "Invoice #", 14, "text",
            validate={"type": "list", "source": "=Invoices_Numbers",
                      "ignore_blank": True}),
        Col("line_no", "Line", 7, "int"),
        Col("date", "Date", 12, "date"),
        Col("description", "Description", 40, "text",
            note="What the client sees on the invoice."),
        Col("service", "Service", 20, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True}),
        Col("qty", "Qty", 8, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("unit_price", "Unit Price", 12, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000}),
        Col("line_total", "Line Total", 13, "money_locked",
            formula='IF({invoice_ref}{r}="","",'
                    'ROUND({qty}{r}*{unit_price}{r},2))'),
        Col("match_key", "Match Key", 12, "text_locked",
            formula='IF({invoice_ref}{r}="","",'
                    '{invoice_ref}{r}&"-"&{line_no}{r})',
            hidden=True,
            note="Helper for the printable invoice. Leave hidden."),
    ]

    return SheetSpec(
        name="Invoice Lines",
        title="Invoice Lines",
        subtitle="One row per billed line. The Invoices tab totals these "
                 "by Invoice #.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
