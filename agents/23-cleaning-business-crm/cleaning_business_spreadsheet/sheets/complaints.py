"""The Complaints register."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Complaints")
    samples = sd.COMPLAINTS if cfg.include_sample_data else []

    columns = [
        Col("id", "Case ID", 11, "text",
            formula='IF({client}{r}="","",'
                    '"CC-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date Raised", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("client", "Client", 22, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("category", "Category", 15, "center",
            validate={"type": "list", "source": [
                "Quality", "Staff conduct", "Communication", "Billing",
                "Access", "Damage", "Punctuality", "Other"]}),
        Col("severity", "Severity", 11, "center",
            validate={"type": "list",
                      "source": ["Low", "Medium", "High", "Critical"]}),
        Col("description", "What Happened", 34, "text"),
        Col("owner", "Handled By", 15, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "Open", "Investigating", "Resolved", "Closed",
                "Escalated"]}),
        Col("action", "Action Taken", 30, "text"),
        Col("resolved_date", "Resolved On", 13, "date"),
        Col("refund", "Refund / Credit", 13, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("days_open", "Days Open", 11, "int_locked",
            formula='IF({date}{r}="","",IF({resolved_date}{r}="",'
                    'TODAY()-{date}{r},{resolved_date}{r}-{date}{r}))'),
        Col("due", "Follow-up Due", 14, "text_locked",
            formula='IF({client}{r}="","",IF(OR({status}{r}="Closed",'
                    '{status}{r}="Resolved"),"-",'
                    'IF(TODAY()-{date}{r}>3,"FOLLOW UP","On track")))'),
        Col("notes", "Notes", 22, "text"),
    ]

    spec = SheetSpec(
        name="Complaints",
        title="Complaints & Recovery",
        subtitle="What went wrong, who owns it, what was done. Fast, "
                 "visible recovery keeps clients.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
    spec.col("severity").cf = [
        {"type": "text", "criteria": "containing", "value": "Critical",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "High",
         "style": "warning"},
    ]
    return spec
