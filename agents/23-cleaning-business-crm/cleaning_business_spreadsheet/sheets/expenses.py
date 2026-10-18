"""The Expenses register - money out."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Expenses")
    samples = sd.EXPENSES if cfg.include_sample_data else []

    columns = [
        Col("id", "Expense ID", 11, "text",
            formula='IF({amount}{r}="","",'
                    '"EX-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("category", "Category", 15, "center",
            validate={"type": "list", "source": [
                "Payroll", "Supplies", "Equipment", "Fuel", "Insurance",
                "Rent", "Utilities", "Marketing", "Training", "Repairs",
                "Software", "Fees", "Taxes", "Other"]}),
        Col("payee", "Paid To", 20, "text"),
        Col("description", "Description", 30, "text"),
        Col("amount", "Amount", 13, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 10000000}),
        Col("method", "Method", 13, "center",
            validate={"type": "list", "source": [
                "Cash", "Card", "Bank transfer", "Check", "Online",
                "Direct debit", "Other"]}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True},
            note="Optional - job-related extras flow into Job Costing."),
        Col("receipt", "Receipt", 9, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]}),
        Col("recurring", "Recurring", 10, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]}),
        Col("month", "Month", 13, "date_locked",
            formula='IF({date}{r}="","",DATE(YEAR({date}{r}),'
                    'MONTH({date}{r}),1))'),
        Col("notes", "Notes", 22, "text"),
    ]

    return SheetSpec(
        name="Expenses",
        title="Expenses",
        subtitle="Every cost of running the business. Categories feed the "
                 "Financial Plan and the Reports tab.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
