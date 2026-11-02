"""11. Crew Database - the people, their rates and their paperwork.

The hourly cost recorded here is what the whole workbook uses to work
out what a job cost. It should be the loaded cost - wage plus payroll
tax plus insurance plus the share of the truck they ride in - not the
figure on their payslip. If you put the payslip number in, every job
in the workbook will look more profitable than it is.
"""

from __future__ import annotations

from ..config import ACTIVE_CREW_STATUSES, Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, count_by, id_col,
                     in_list, money_cf, rank_desc, rating_cf, scale_cf,
                     status_cf, sum_by, yesno, zero)

NAME = "Crew Database"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Crew Database",
        subtitle="Who works for you, what they cost per hour, what "
                 "they are qualified to do and when it expires.",
        tab_color=Palette.primary_mid,
        rows=cfg.row_count("crew"),
        samples=sample("crew", cfg),
        help_text=(
            "Add each person once. The Employee ID appears "
            "automatically and feeds the timesheets, where hours are "
            "costed at that person's own rate. Expiry dates for "
            "licences and certificates are tracked here and warn you "
            "before they lapse."),
        extra_notes=[
            "Hourly cost should be the loaded cost, not the wage. A "
            "$20 wage usually costs the business $26 to $30 once tax, "
            "insurance and downtime are counted. Guessing low here "
            "makes every job in the workbook look better than it is.",
            "Keep people who have left, with status 'Left'. Their "
            "hours are part of last season's costs, and deleting the "
            "row leaves those timesheets pointing at nobody.",
            "This is a record of hours and rates for your own "
            "planning. It is not a payroll system and it does not "
            "calculate tax withholding - your payroll provider or "
            "accountant does that.",
        ],
        columns=[
            id_col("name", "CrewPrefix", digits=cfg.digits("crew"),
                   header="Employee ID",
                   note="Generated. The timesheets point at this."),
            Col("name", "Name", 22, "text",
                note="Start here."),
            Col("role", "Role", 20, "text",
                validate=list_from("CrewRoleList")),
            Col("crew", "Usual crew", 12, "text",
                validate=list_from("CrewNameList"),
                note="Which truck they normally ride with."),
            Col("employment", "Employment", 16, "text",
                validate=list_from("EmploymentTypeList"),
                note="Seasonal and subcontract people cost differently "
                     "and are worth separating."),
            Col("phone", "Phone", 15, "text"),
            Col("email", "Email", 24, "text"),
            Col("emergency", "Emergency contact", 22, "text",
                note="Name and number. The one field you hope never to "
                     "use, and must have when you do."),
            Col("start_date", "Started", 11, "date",
                validate=date_check()),
            Col("end_date", "Left", 11, "date",
                validate=date_check(),
                note="Fill in rather than deleting the row."),
            Col("status", "Status", 12, "text",
                validate=list_from("CrewStatusList"),
                cf=status_cf()),
            Col("pay_rate", "Pay rate / hr", 12, "money",
                validate=amount(0, 1000, "What you pay them per hour."),
                note="The wage itself, for reference and for payroll."),
            Col("cost_rate", "Cost to you / hr", 13, "money",
                validate=amount(0, 1000,
                                "Wage plus payroll tax plus insurance "
                                "plus overheads attached to this "
                                "person."),
                note="The real number. This is what costs every job in "
                     "the workbook. Blank falls back to the crew rate "
                     "on Settings."),
            Col("overtime_rate", "Overtime x", 10, "number1",
                validate=amount(1, 5,
                                "Multiplier for hours over the weekly "
                                "threshold."),
                note="Blank uses the multiplier on Settings."),
            Col("licence", "Licence / cert", 20, "text",
                note="Pesticide applicator, chainsaw ticket, CDL. The "
                     "ones that stop work if they lapse."),
            Col("licence_expiry", "Expires", 11, "date",
                validate=date_check(),
                cf=[{"type": "formula",
                     "criteria": '=AND(ISNUMBER({licence_expiry}{r}),'
                                 '{licence_expiry}{r}<TodayDate)',
                     "fmt": "bold_bad"}],
                note="Warned about well before the date, and in red "
                     "after it."),
            Col("insurance_expiry", "Insurance to", 12, "date",
                validate=date_check()),
            Col("licence_days", "Days to expiry", 12, "int",
                formula=zero("name",
                             'IF({licence_expiry}{r}="",9999,'
                             '{licence_expiry}{r}-TodayDate)'),
                hidden=True),
            Col("can_spray", "Can spray", 10, "flag",
                validate=yesno("Are they licensed to apply pesticide or "
                               "fertiliser?"),
                note="Jobs flagged as needing a licence should only go "
                     "to people marked Yes here."),
            Col("can_drive", "Can drive", 10, "flag",
                validate=yesno()),
            Col("equipment_ok", "Machinery trained", 14, "wrap",
                note="Which machines they are signed off on. A free "
                     "text note, because every yard is different."),
            Col("notes", "Notes", 28, "wrap"),

            # ---- what they actually do -------------------------------
            Col("hours_total", "Hours logged", 12, "number1",
                formula=zero("name", sum_by("Timesheets & Payroll",
                                            "hours", "employee",
                                            '{id}{r}')),
                cf=scale_cf()),
            Col("hours_year", "Hours this year", 13, "number1",
                formula=zero("name", sum_by(
                    "Timesheets & Payroll", "hours", "employee",
                    '{id}{r}',
                    "date_num", '">="&YearStart',
                    "date_num", '"<="&YearEnd'))),
            Col("hours_billable", "Billable hours", 13, "number1",
                formula=zero("name", sum_by("Timesheets & Payroll",
                                            "hours", "employee",
                                            '{id}{r}',
                                            "is_billable", "1")),
                note="Hours booked to a job, as opposed to travel, "
                     "yard time and machine repairs."),
            Col("billable_pct", "Billable %", 10, "percent",
                formula='=IF({name}{r}="","",'
                        'IF({hours_total}{r}<=0,"",'
                        'ROUND({hours_billable}{r}/'
                        '{hours_total}{r},4)))',
                cf=[{"type": "cell", "criteria": ">=", "value": 0.75,
                     "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0.5,
                     "fmt": "bad"}],
                note="The number that explains a bad month better than "
                     "anything else. Below 60% means the day is being "
                     "eaten by driving and faffing."),
            Col("cost_total", "Labour cost", 12, "money",
                formula=zero("name", sum_by("Timesheets & Payroll",
                                            "cost", "employee",
                                            '{id}{r}'))),
            Col("revenue", "Revenue worked on", 15, "money",
                formula=zero("name", sum_by("Timesheets & Payroll",
                                            "job_value", "employee",
                                            '{id}{r}')),
                cf=money_cf(),
                note="Their share of what the jobs they worked on were "
                     "worth. A rough measure, but a fair one."),
            Col("value_per_hour", "Value per hour", 13, "money",
                formula='=IF({name}{r}="","",'
                        'IF({hours_billable}{r}<=0,"",'
                        'ROUND({revenue}{r}/'
                        '{hours_billable}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}]),
            Col("jobs_done", "Jobs worked", 11, "int",
                formula=zero("name", count_by("Timesheets & Payroll",
                                              "employee", '{id}{r}',
                                              "is_billable", "1"))),
            Col("rating", "Quality score", 12, "number1",
                formula='=IF({name}{r}="","",'
                        'IFERROR(AVERAGEIFS('
                        '[[Customer Feedback.score]],'
                        '[[Customer Feedback.crew]],{crew}{r},'
                        '[[Customer Feedback.score]],">0"),""))',
                cf=rating_cf(),
                note="Feedback for the crew they ride with, since "
                     "customers rate the visit, not the individual."),
            Col("overtime_hours", "Overtime hrs", 11, "number1",
                formula=zero("name", sum_by("Timesheets & Payroll",
                                            "overtime_hours", "employee",
                                            '{id}{r}')),
                cf=[{"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "warn"}]),
            Col("is_active", "Active", 7, "int",
                formula=zero("name",
                             f'IF({in_list("{status}{r}", ACTIVE_CREW_STATUSES)},'
                             '1,0)'),
                hidden=True),
            rank_desc("revenue", guard='{name}{r}=""'),

            Col("alert", "What needs doing", 44, "wrap",
                formula=alert_chain("name", [
                    ('AND({is_active}{r}=1,{licence}{r}<>"",'
                     '{licence_days}{r}<0)',
                     "Expired - licence has lapsed, they cannot do "
                     "that work"),
                    ('AND({is_active}{r}=1,{cost_rate}{r}=0,'
                     '{pay_rate}{r}=0)',
                     "Add - no rate set, so their hours cost nothing"),
                    ('AND({is_active}{r}=1,{licence}{r}<>"",'
                     '{licence_days}{r}<=60)',
                     "Renew - licence expires within two months"),
                    ('AND({is_active}{r}=1,{emergency}{r}="")',
                     "Add - no emergency contact on file"),
                    ('{overtime_hours}{r}>0',
                     "Check - overtime logged, is the round too big?"),
                    ('AND({hours_total}{r}>0,{billable_pct}{r}<>"",'
                     '{billable_pct}{r}<0.5)',
                     "Check - under half their hours are billable"),
                    ('AND({is_active}{r}=1,{hours_total}{r}=0)',
                     "Action - no hours ever logged for this person"),
                    ('AND({is_active}{r}=1,{cost_rate}{r}=0)',
                     "Add - no loaded cost rate, jobs use the default"),
                ]),
                cf=alert_cf()),
        ],
    )
