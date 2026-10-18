"""The Employees register."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Employees")
    samples = sd.EMPLOYEES if cfg.include_sample_data else []
    oncost = cfg.employer_oncost

    columns = [
        Col("id", "Staff ID", 11, "text",
            formula='IF({name}{r}="","",'
                    '"EMP-"&TEXT(ROW()-4,"00"))'),
        Col("name", "Name", 22, "text"),
        Col("role", "Role", 15, "center",
            validate={"type": "list", "source": [
                "Owner", "Manager", "Team lead", "Cleaner", "Driver",
                "Admin", "Contractor"]}),
        Col("phone", "Phone", 14, "text"),
        Col("email", "Email", 22, "text"),
        Col("hourly_pay", "Hourly Pay", 11, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 500},
            note="What you pay them per hour before on-costs."),
        Col("oncost_pay", "Loaded Cost / Hr", 13, "money_locked",
            formula='IF({hourly_pay}{r}="","",'
                    'ROUND({hourly_pay}{r}*' + str(1 + oncost) + ',2))',
            note=f"Pay plus {oncost:.0%} employer on-costs (tax, "
                 "insurance, holiday pay)."),
        Col("hire_date", "Hire Date", 13, "date"),
        Col("status", "Status", 11, "center",
            validate={"type": "list", "source": [
                "Active", "Inactive", "On leave", "Suspended"]}),
        Col("emergency", "Emergency Contact", 18, "text"),
        Col("certs", "Certifications", 18, "text",
            note="OSHA, first aid, DBS check, driving licence..."),
        Col("notes", "Notes", 22, "text"),
        Col("jobs_mtd", "Jobs This Month", 12, "int_locked",
            formula='IF({name}{r}="","",COUNTIFS([[Jobs.crew_lead]],'
                    '{name}{r},[[Jobs.date]],">="&DATE(YEAR(TODAY()),'
                    'MONTH(TODAY()),1)))'),
        Col("hours_mtd", "Hours This Month", 12, "decimal_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Timesheets.hours]],[[Timesheets.employee]],'
                    '{name}{r},[[Timesheets.date]],">="&'
                    'DATE(YEAR(TODAY()),MONTH(TODAY()),1)))'),
        Col("cost_mtd", "Cost This Month", 13, "money_locked",
            formula='IF({name}{r}="","",'
                    'SUMIFS([[Timesheets.pay]],[[Timesheets.employee]],'
                    '{name}{r},[[Timesheets.date]],">="&'
                    'DATE(YEAR(TODAY()),MONTH(TODAY()),1)))'),
    ]

    return SheetSpec(
        name="Employees",
        title="Employees & Crew",
        subtitle="Who works for you, what they cost, what they are "
                 "certified for. Names feed the scheduler drop-downs.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
