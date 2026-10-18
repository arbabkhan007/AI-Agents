"""The Safety register - checks, talks and policy."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Safety")
    samples = sd.SAFETY if cfg.include_sample_data else []

    columns = [
        Col("id", "ID", 11, "text",
            formula='IF({date}{r}="","",'
                    '"SF-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("type", "Type", 15, "center",
            validate={"type": "list", "source": [
                "Toolbox talk", "Training", "Inspection", "Policy review",
                "Equipment check", "Risk assessment"]}),
        Col("topic", "Topic", 24, "text"),
        Col("area", "Area / Site", 18, "text"),
        Col("risk_level", "Risk", 10, "center",
            validate={"type": "list",
                      "source": ["Low", "Medium", "High"]}),
        Col("finding", "Finding", 28, "text"),
        Col("action", "Action Required", 26, "text"),
        Col("owner", "Owner", 15, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("due_date", "Due", 13, "date"),
        Col("status", "Status", 12, "center",
            validate={"type": "list", "source": [
                "Open", "In progress", "Done", "Not required"]}),
        Col("closed_date", "Closed", 13, "date"),
        Col("attendees", "Attendees", 22, "text"),
        Col("notes", "Notes", 22, "text"),
    ]

    return SheetSpec(
        name="Safety",
        title="Safety & Compliance",
        subtitle="Toolbox talks, inspections and risk assessments - "
                 "evidence that the business takes care of its people.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
