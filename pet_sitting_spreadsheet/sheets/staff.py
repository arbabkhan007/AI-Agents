"""`Staff` - team directory, workload, timesheet totals and pay."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import alert_cf, blank, id_col, status_cf

NAME = "Staff"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("name", '"ST-"', digits=3, width=9),
        Col("name", "Name", 18, "text",
            note="This name is used by the Bookings, Visit Log and Mileage "
                 "drop downs."),
        Col("phone", "Phone", 17, "text"),
        Col("email", "Email", 26, "text"),
        Col("role", "Role", 14, "text", validate=list_from("StaffRoleList")),
        Col("employment", "Employment type", 18, "text",
            validate=list_from("EmploymentTypeList")),
        Col("start_date", "Started on", 12, "date", validate=date_check()),
        Col("status", "Status", 11, "status",
            validate=list_from("StaffStatusList"), cf=status_cf()),
        Col("availability", "Availability", 22, "text"),
        Col("days_off", "Regular days off", 14, "text"),
        Col("pay_type", "Pay type", 13, "text",
            validate=list_from("PayTypeList")),
        Col("pay_rate", "Pay rate", 11, "money",
            validate=number_check(0, 100000),
            note="Hourly rate, per-visit fee, or the commission "
                 "percentage as a number (55 = 55%)."),
        Col("certs", "Certifications", 26, "wrap"),
        Col("cert_expiry", "Certificate expires", 12, "date",
            validate=date_check()),
        Col("cert_alert", "Certificate status", 16, "status",
            formula=blank("cert_expiry",
                          'IF({cert_expiry}{r}<TODAY(),"EXPIRED",'
                          'IF({cert_expiry}{r}-TODAY()<=ExpiryAlertDays,'
                          '"Due in "&TEXT({cert_expiry}{r}-TODAY(),"0")'
                          '&" days","Valid"))'),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "EXPIRED", "fmt": "bold_bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Due in", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Valid", "fmt": "good"}]),
        Col("check_date", "Background check", 12, "date",
            validate=date_check()),
        Col("emergency", "Emergency contact", 24, "text"),
        Col("leave", "Leave & absence", 22, "wrap"),
        Col("bookings", "Bookings assigned", 10, "int",
            formula=blank("name",
                          'COUNTIFS([[Bookings.staff]],{name}{r},'
                          '[[Bookings.status]],"<>Cancelled")')),
        Col("visits", "Visits completed", 10, "int",
            formula=blank("name",
                          'COUNTIFS([[Visit Log.staff]],{name}{r},'
                          '[[Visit Log.status]],"Completed")')),
        Col("hours", "Hours worked", 10, "number",
            formula=blank("name",
                          'ROUND(SUMIFS([[Visit Log.duration]],'
                          '[[Visit Log.staff]],{name}{r},'
                          '[[Visit Log.status]],"Completed")/60,2)')),
        Col("distance", f"{cfg.distance_unit.title()} driven", 10, "number1",
            formula=blank("name",
                          'SUMIFS([[Mileage.total_km]],[[Mileage.staff]],'
                          '{name}{r},[[Mileage.business]],"Business")')),
        Col("revenue", "Revenue delivered", 13, "money",
            formula=blank("name",
                          'SUMIFS([[Bookings.total]],[[Bookings.staff]],'
                          '{name}{r},[[Bookings.status]],"<>Cancelled")'),
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("wages", "Pay due", 12, "money",
            formula=blank("name",
                          'ROUND(IF({pay_type}{r}="Hourly",{hours}{r}'
                          '*IF({pay_rate}{r}="",0,{pay_rate}{r}),'
                          'IF({pay_type}{r}="Per visit",{visits}{r}'
                          '*IF({pay_rate}{r}="",0,{pay_rate}{r}),'
                          'IF({pay_type}{r}="Commission %",{revenue}{r}'
                          '*IF({pay_rate}{r}="",0,{pay_rate}{r})/100,0))),2)'),
            note="Salaried team members show 0 - pay them from payroll."),
        Col("rev_per_hour", "Revenue per hour", 11, "money",
            formula='=IF(OR({hours}{r}="",{hours}{r}=0),"",'
                    'ROUND({revenue}{r}/{hours}{r},2))'),
        Col("completion", "Completion rate", 10, "percent",
            formula='=IF(OR({bookings}{r}="",{bookings}{r}=0),"",'
                    '{visits}{r}/{bookings}{r})',
            cf=[{"type": "cell", "criteria": "<", "value": 0.8,
                 "fmt": "warn"},
                {"type": "cell", "criteria": ">=", "value": 0.95,
                 "fmt": "good"}]),
        Col("notes", "Notes", 28, "wrap"),
        Col("alert", "Action needed", 22, "status",
            formula=blank(
                "name",
                'IF({cert_alert}{r}="EXPIRED","Certificate expired",'
                'IF(LEFT({cert_alert}{r},6)="Due in","Certificate due",'
                'IF({check_date}{r}="","Action - background check",'
                'IF(AND({status}{r}="Active",{bookings}{r}=0),'
                '"No bookings assigned","OK"))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Staff & Contractors",
        subtitle="Who works for you, when they are available, what they "
                 "have delivered and what they are owed.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary,
        freeze_cols=2,
        samples=sample(cfg).staff,
        help_text="Hours and pay come from completed visits in the Visit "
                  "Log, so log every visit to keep the timesheet honest.",
    )
