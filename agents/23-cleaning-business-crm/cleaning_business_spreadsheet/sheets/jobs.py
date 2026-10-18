"""The Jobs register - every clean you do, booked or done."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Jobs")
    samples = sd.JOBS if cfg.include_sample_data else []
    cost_per_hour = cfg.cost_per_hour
    done_statuses = ",".join(f'{{job_status_first}}:{{job_status_last}}'
                             for _ in ())  # placeholder, unused

    columns = [
        Col("id", "Job ID", 11, "text",
            formula='IF({job_number}{r}="","",'
                    '"JB-"&TEXT(ROW()-4,"0000"))'),
        Col("job_number", "Job #", 13, "text",
            note="Referenced by Job Tasks, Timesheets, Job Costing, "
                 "Supply Usage, Mileage and Invoices."),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("start", "Start", 9, "time",
            validate={"type": "time", "criteria": "between",
                      "minimum": "TIME(6,0,0)", "maximum": "TIME(21,0,0)"}),
        Col("hours", "Hours", 9, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 24},
            note="Billable hours on site."),
        Col("end", "End", 9, "time_locked",
            formula='IF(OR({start}{r}="",{hours}{r}=""),"",'
                    '{start}{r}+{hours}{r}/24)'),
        Col("client", "Client", 24, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("property", "Property", 22, "text",
            validate={"type": "list", "source": "=Properties_Names",
                      "ignore_blank": True}),
        Col("service", "Service", 20, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True}),
        Col("frequency", "Frequency", 13, "center",
            validate={"type": "list", "source": [
                "One-off", "Weekly", "Fortnightly", "Every 3 weeks",
                "Monthly", "Quarterly", "Twice a week"]}),
        Col("cleaners", "Cleaners", 9, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 1, "maximum": 12}),
        Col("crew_lead", "Crew Lead", 16, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("team", "Team", 18, "text",
            note="Whoever else is on the job, separated by commas."),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "Enquiry", "Booked", "Confirmed", "In progress",
                "Completed", "Invoiced", "Cancelled", "No access"]}),
        Col("price", "Price", 13, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000},
            note="What the client pays for this visit."),
        Col("quote_ref", "From Quote", 13, "text",
            validate={"type": "list", "source": "=Quotes_Numbers",
                      "ignore_blank": True}),
        Col("access", "Access Notes", 18, "text"),
        Col("instructions", "Special Instructions", 26, "text"),
        Col("completed", "Completed On", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("invoice_ref", "Invoice #", 13, "text",
            validate={"type": "list", "source": "=Invoices_Numbers",
                      "ignore_blank": True}),
        Col("labour_cost", "Labour Cost", 13, "money_locked",
            formula='IF({job_number}{r}="","",'
                    'ROUND({hours}{r}*{cleaners}{r}*' + str(cost_per_hour) +
                    ',2))',
            note=f"Hours x cleaners x {cfg.currency_symbol}"
                 f"{cost_per_hour:,.2f} loaded cost."),
        Col("total_cost", "Total Cost", 13, "money_locked",
            formula='IF({job_number}{r}="","",{labour_cost}{r}+'
                    'SUMIFS([[Supply Usage.total_cost]],'
                    '[[Supply Usage.job_ref]],{job_number}{r})+'
                    'SUMIFS([[Mileage.claim]],[[Mileage.job_ref]],'
                    '{job_number}{r})+'
                    'SUMIFS([[Expenses.amount]],[[Expenses.job_ref]],'
                    '{job_number}{r}))',
            note="Labour plus supplies, mileage and any expenses logged "
                 "against this job number."),
        Col("profit", "Profit", 13, "money_locked",
            formula='IF({job_number}{r}="","",{price}{r}-{total_cost}{r})'),
        Col("margin", "Margin %", 11, "pct_locked",
            formula='IF(OR({job_number}{r}="",{price}{r}=0),"",'
                    '{profit}{r}/{price}{r})'),
        Col("month", "Month", 13, "date_locked",
            formula='IF({date}{r}="","",DATE(YEAR({date}{r}),'
                    'MONTH({date}{r}),1))',
            note="First of the month - the Reports tab groups on this."),
        Col("week", "Week Starting", 13, "date_locked",
            formula='IF({date}{r}="","",{date}{r}-WEEKDAY({date}{r},2)+1)',
            note="The Monday of the job week."),
        Col("tasks_done", "Tasks Done", 12, "text_locked",
            formula='IF({job_number}{r}="","",'
                    'TEXT(COUNTIFS([[Job Tasks.job_ref]],{job_number}{r},'
                    '[[Job Tasks.done]],"Yes"),"0")&"/"&'
                    'TEXT(COUNTIF([[Job Tasks.job_ref]],{job_number}{r}),'
                    '"0"))',
            note="Checklist progress on the Job Tasks tab."),
    ]

    spec = SheetSpec(
        name="Jobs",
        title="Job Register & Scheduler",
        subtitle="The working heart of the system. Everything - costs, "
                 "timesheets, invoices, reports - hangs off the Job #.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )

    status_col = spec.col("status")
    status_col.cf = [
        {"type": "text", "criteria": "containing", "value": "Completed",
         "style": "good"},
        {"type": "text", "criteria": "containing", "value": "Invoiced",
         "style": "info"},
        {"type": "text", "criteria": "containing", "value": "Cancelled",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "No access",
         "style": "warning"},
    ]
    del done_statuses
    return spec
