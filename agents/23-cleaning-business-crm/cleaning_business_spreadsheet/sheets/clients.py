"""The Clients register - the heart of the CRM."""

from __future__ import annotations

from ..formats import FormatBook
from ..layout import Col, SheetSpec
from ..config import Config, Palette


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Clients")
    samples = sd.CLIENTS if cfg.include_sample_data else []
    unit = cfg.area_unit

    columns = [
        Col("id", "Client ID", 12, "text",
            formula='IF({name}{r}="","",' +
                    f'"CL-"&TEXT(ROW()-{4},"0000"))',
            note="Automatic. Each client gets a permanent ID."),
        Col("name", "Client / Company", 26, "text",
            validate={"type": "length", "criteria": "between",
                      "minimum": 2, "maximum": 60},
            note="The person or company you invoice."),
        Col("type", "Type", 12, "center",
            validate={"type": "list",
                      "source": ["Residential", "Commercial", "Both"]}),
        Col("contact", "Contact Person", 20, "text",
            note="Who you deal with on site."),
        Col("email", "Email", 24, "text"),
        Col("phone", "Phone", 15, "text"),
        Col("address", "Billing Address", 28, "text"),
        Col("city", "City / Area", 14, "text"),
        Col("source", "How They Found You", 16, "center",
            validate={"type": "list", "source": [
                "Referral", "Google", "Facebook", "Instagram", "Yelp",
                "Flyer", "Repeat client", "Walk-in", "Partner", "Other"]}),
        Col("frequency", "Default Frequency", 15, "center",
            validate={"type": "list", "source": [
                "One-off", "Weekly", "Fortnightly", "Every 3 weeks",
                "Monthly", "Quarterly", "Twice a week"]},
            note="Sets the default schedule for new quotes and jobs."),
        Col("since", "Client Since", 14, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2000,1,1)", "maximum": "DATE(2100,1,1)"}),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "Active", "Inactive", "On hold", "Do not serve"]}),
        Col("property_ref", "Main Property", 22, "text",
            validate={"type": "list", "source": "=Properties_Names",
                      "ignore_blank": True},
            note="Optional. Links to the Properties tab."),
        Col("notes", "Notes", 30, "text"),
        Col("active_jobs", "Open Jobs", 11, "int_locked",
            formula='IF({name}{r}="","",COUNTIFS([[Jobs.client]],{name}{r},'
                    '[[Jobs.status]],"<>Completed",[[Jobs.status]],'
                    '"<>Invoiced",[[Jobs.status]],"<>Cancelled"))',
            note="Jobs not yet completed or invoiced."),
        Col("billed", f"Total Billed ({cfg.currency_code})", 15,
            "money_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Invoices.total]],[[Invoices.client]],{name}{r}))',
            note="Sum of every invoice raised for this client."),
        Col("outstanding", "Outstanding", 14, "money_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Invoices.balance]],[[Invoices.client]],'
                    '{name}{r}))',
            note="Unpaid invoice balance. Chase anything above zero."),
        Col("last_job", "Last Job", 13, "date_locked",
            formula='IF({name}{r}="","",IF(COUNTIF([[Jobs.client]],'
                    '{name}{r})=0,"",SUMPRODUCT(MAX(([[Jobs.client]]='
                    '{name}{r})*[[Jobs.date]]))))',
            note="Most recent job date for this client."),
        Col("rating", "Satisfaction (1-5)", 12, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 1, "maximum": 5},
            note="Rate the client relationship 1-5. The Reports tab "
                 "averages this."),
    ]

    return SheetSpec(
        name="Clients",
        title="Client CRM",
        subtitle="Every client you work for. Names feed the quote "
                 "calculator, jobs, invoices and reports through the "
                 "drop-downs built from this list.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
        help_text="Add a row per client. Columns shaded pale teal "
                  "calculate themselves - do not type over them.",
    )
