"""8 Staff Management - directory, rates and live productivity."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, date_check, list_from, number_check
from .. import sample_data

NAME = "8 Staff Management"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="8  Staff Management",
        subtitle="Who works here, how they are paid, and what they bring "
                 "in - revenue and commissions calculated live.",
        tab_color="#B98A2F",
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        help_text="One row per stylist or technician. The commission "
                  "method decides how tab 9 pays them: Percentage uses "
                  "their own rates, Category uses the category rate table "
                  "on Settings, Flat pays a fixed amount per service.",
        columns=[
            Col("id", "Staff ID", 9, "id",
                formula='="E-"&TEXT(ROW()-{first}+1,"00")'),
            Col("name", "Name", 20, "text",
                note="The name used by every drop down in the workbook."),
            Col("role", "Role", 20, "text"),
            Col("type", "Type", 12, "flag",
                validate=list_from("ListStaffTypes")),
            Col("start", "Started", 12, "date", validate=date_check()),
            Col("availability", "Availability", 26, "wrap",
                note="e.g. Tue-Sat, 9-5. Closed Mondays."),
            Col("hourly", "Hourly rate", 11, "money",
                validate=number_check(0, 1000),
                note="Used by the payroll tab for hourly pay."),
            Col("method", "Commission", 12, "text",
                validate=list_from("ListCommMethods")),
            Col("svc_rate", "Service %", 9, "percent",
                validate=number_check(0, 1, False)),
            Col("retail_rate", "Retail %", 9, "percent",
                validate=number_check(0, 1, False)),
            Col("status", "Status", 10, "status",
                validate=list_from("ListStaffStatus"),
                cf=[cf_text("Left", "bad"), cf_text("On Leave", "warn"),
                    cf_text("Active", "good")]),
            Col("leave", "Leave & absence notes", 26, "wrap"),
            Col("revenue", "Revenue", 12, "money",
                formula='IF({name}{r}="","",ROUND(SUMIFS(SalesNet,'
                        'SalesStaff,{name}{r}),2))'),
            Col("svc_rev", "Service rev", 12, "money",
                formula='IF({name}{r}="","",ROUND(SUMIFS(SalesNet,'
                        'SalesStaff,{name}{r},SalesType,"Service"),2))'),
            Col("ret_rev", "Retail rev", 12, "money",
                formula='IF({name}{r}="","",ROUND(SUMIFS(SalesNet,'
                        'SalesStaff,{name}{r},SalesType,"Retail"),2))'),
            Col("appts", "Appts done", 10, "int",
                formula='IF({name}{r}="","",COUNTIFS(ApptStaff,{name}{r},'
                        'ApptStatus,"Completed"))'),
            Col("ticket", "Avg ticket", 11, "money",
                formula='IF(OR({name}{r}="",{appts}{r}=0),"",ROUND('
                        '{svc_rev}{r}/{appts}{r},2))'),
            Col("commission", "Commission", 12, "money",
                formula='IF({name}{r}="","",ROUND(SUMPRODUCT((SalesStaff='
                        '{name}{r})*(SalesType="Service")*SalesNet*'
                        'SalesRate)+N({retail_rate}{r})*SUMPRODUCT('
                        '(SalesStaff={name}{r})*(SalesType="Retail")'
                        '*SalesNet)+IF(IFERROR(INDEX(StaffMethod,MATCH('
                        '{name}{r},StaffNames,0)),"")="Flat",FlatCommission'
                        '*COUNTIFS(ApptStaff,{name}{r},ApptStatus,'
                        '"Completed"),0),2))',
                note="Service revenue at the applicable rate + retail at "
                     "the retail rate + flat amount where that method is "
                     "chosen."),
        ],
        samples=sample_data.staff_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Commission eligibility is yours to set: change a rate to 0 "
            "for a trainee, or switch the method per person.",
            "Manual adjustments and approvals live on tab 9 next to each "
            "statement.",
        ],
    )
