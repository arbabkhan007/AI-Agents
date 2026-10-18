"""The Quotes register - one row per quote sent."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Quotes")
    samples = sd.QUOTES if cfg.include_sample_data else []
    valid = cfg.quote_valid_days
    follow = cfg.quote_followup_days
    tax = cfg.tax_rate
    deposit = cfg.deposit_percent

    columns = [
        Col("id", "Quote ID", 11, "text",
            formula='IF({quote_number}{r}="","",'
                    '"QT-"&TEXT(ROW()-4,"0000"))'),
        Col("quote_number", "Quote #", 14, "text",
            note="Quote number used on the Quote Lines tab and the "
                 "printable quote."),
        Col("date", "Date Sent", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("client", "Client", 24, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("property", "Property", 22, "text",
            validate={"type": "list", "source": "=Properties_Names",
                      "ignore_blank": True}),
        Col("contact", "Contact", 16, "text"),
        Col("email", "Email", 22, "text"),
        Col("phone", "Phone", 14, "text"),
        Col("service", "Main Service", 18, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True}),
        Col("frequency", "Frequency", 14, "center",
            validate={"type": "list", "source": [
                "One-off", "Weekly", "Fortnightly", "Every 3 weeks",
                "Monthly", "Quarterly", "Twice a week"]}),
        Col("valid_until", "Valid Until", 13, "date_locked",
            formula='IF({date}{r}="","",{date}{r}+' + str(valid) + ')'),
        Col("subtotal", "Subtotal", 13, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    'SUMIFS([[Quote Lines.line_total]],'
                    '[[Quote Lines.quote_ref]],{quote_number}{r}))',
            note="Sum of the Quote Lines for this quote number."),
        Col("discount_pct", "Discount %", 11, "pct",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 0.9}),
        Col("discount", "Discount", 12, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    'ROUND({subtotal}{r}*{discount_pct}{r},2))'),
        Col("tax", cfg.tax_label, 12, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    'ROUND(({subtotal}{r}-{discount}{r})*' +
                    str(tax) + ',2))'),
        Col("total", "Quote Total", 14, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    '{subtotal}{r}-{discount}{r}+{tax}{r})'),
        Col("deposit", "Deposit Due", 13, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    'ROUND({total}{r}*' + str(deposit) + ',2))',
            note=f"{deposit:.0%} of the total, collected before work "
                 "starts on big jobs."),
        Col("est_hours", "Est. Hours", 11, "decimal_locked",
            formula='IF({quote_number}{r}="","",'
                    'SUMIFS([[Quote Lines.hours]],'
                    '[[Quote Lines.quote_ref]],{quote_number}{r}))'),
        Col("est_cost", "Est. Cost", 13, "money_locked",
            formula='IF({quote_number}{r}="","",'
                    'SUMIFS([[Quote Lines.line_cost]],'
                    '[[Quote Lines.quote_ref]],{quote_number}{r}))',
            note="Labour at your cost per hour plus materials on the "
                 "quote lines."),
        Col("margin", "Est. Margin", 11, "pct_locked",
            formula='IF(OR({quote_number}{r}="",{subtotal}{r}=0),"",'
                    '({subtotal}{r}-{discount}{r}-{est_cost}{r})/'
                    '({subtotal}{r}-{discount}{r}))'),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "Draft", "Sent", "Followed up", "Accepted", "Declined",
                "Expired"]}),
        Col("follow_up", "Follow Up", 13, "date_locked",
            formula='IF({date}{r}="","",{date}{r}+' + str(follow) + ')',
            note="Chase the client on this date."),
        Col("owner", "Salesperson", 14, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("job_created", "Job Created", 12, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]}),
        Col("notes", "Notes", 28, "text"),
    ]

    spec = SheetSpec(
        name="Quotes",
        title="Quotes",
        subtitle="One row per quote. Add the detail lines on Quote Lines "
                 "using the same Quote #, and print the quote from the "
                 "Print Quote tab.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )

    spec.col("status").cf = [
        {"type": "text", "criteria": "containing", "value": "Accepted",
         "style": "good"},
        {"type": "text", "criteria": "containing", "value": "Declined",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "Expired",
         "style": "warning"},
    ]
    return spec
