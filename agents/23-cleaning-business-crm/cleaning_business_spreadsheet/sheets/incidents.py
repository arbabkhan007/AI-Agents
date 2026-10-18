"""The Incidents register."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Incidents")
    samples = sd.INCIDENTS if cfg.include_sample_data else []

    columns = [
        Col("id", "Incident ID", 11, "text",
            formula='IF({date}{r}="","",'
                    '"IN-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("time", "Time", 9, "time"),
        Col("type", "Type", 15, "center",
            validate={"type": "list", "source": [
                "Injury", "Near miss", "Property damage", "Security",
                "Vehicle", "Chemical", "Other"]}),
        Col("employee", "Employee", 18, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("client", "Client", 20, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("location", "Location", 18, "text"),
        Col("severity", "Severity", 11, "center",
            validate={"type": "list",
                      "source": ["Low", "Medium", "High", "Critical"]}),
        Col("description", "What Happened", 32, "text"),
        Col("action", "Immediate Action", 28, "text"),
        Col("reported_to", "Reported To", 16, "text"),
        Col("reported_date", "Reported On", 13, "date"),
        Col("status", "Status", 11, "center",
            validate={"type": "list", "source": [
                "Open", "Under review", "Closed"]}),
        Col("days_since", "Days Since", 11, "int_locked",
            formula='IF({date}{r}="","",TODAY()-{date}{r})'),
        Col("notes", "Notes", 22, "text"),
    ]

    spec = SheetSpec(
        name="Incidents",
        title="Incidents & Near Misses",
        subtitle="Everything that happened, however small. Patterns here "
                 "prevent the next one.",
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
