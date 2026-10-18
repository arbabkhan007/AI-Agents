"""The Leads register - new business pipeline."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Leads")
    samples = sd.LEADS if cfg.include_sample_data else []
    grace = cfg.quote_followup_days

    columns = [
        Col("id", "Lead ID", 11, "text",
            formula='IF({name}{r}="","",'
                    '"LD-"&TEXT(ROW()-4,"0000"))'),
        Col("name", "Lead Name", 24, "text"),
        Col("type", "Type", 12, "center",
            validate={"type": "list",
                      "source": ["Residential", "Commercial"]}),
        Col("contact", "Contact", 18, "text"),
        Col("email", "Email", 22, "text"),
        Col("phone", "Phone", 15, "text"),
        Col("source", "Source", 13, "center",
            validate={"type": "list", "source": [
                "Referral", "Google", "Facebook", "Instagram", "Yelp",
                "Flyer", "Website", "Walk-in", "Partner", "Other"]}),
        Col("service", "Service Wanted", 18, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True}),
        Col("estimate", "Estimate", 12, "money",
            note="Rough value of the work if it lands."),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "New", "Contacted", "Quoted", "Followed up", "Booked",
                "Lost", "Dead"]}),
        Col("follow_up", "Follow Up", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"},
            note="The Client Retention tab chases anything overdue."),
        Col("owner", "Owner", 14, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("notes", "Notes", 30, "text"),
        Col("age", "Days Open", 11, "int_locked",
            formula='IF({name}{r}="","",IF(OR({status}{r}="Booked",'
                    '{status}{r}="Lost",{status}{r}="Dead"),"",'
                    'TODAY()-{follow_up}{r}+' + str(grace) + '))',
            note="How many days past the follow-up date this lead sits. "
                 "Big numbers mean the lead is going cold."),
        Col("due", "Follow-up Due", 14, "text_locked",
            formula='IF({name}{r}="","",IF(OR({status}{r}="Booked",'
                    '{status}{r}="Lost",{status}{r}="Dead"),"-",'
                    'IF(TODAY()>{follow_up}{r}+' + str(grace) + ','
                    '"CHASE NOW","On track")))'),
    ]

    return SheetSpec(
        name="Leads",
        title="Lead Pipeline",
        subtitle="Enquiries that have not become clients yet. Chase the "
                 "follow-ups, quote the interested ones, book the keen ones.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
