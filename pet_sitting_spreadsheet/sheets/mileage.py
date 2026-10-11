"""`Mileage` - trip log with odometer readings and reimbursement maths."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, month_col

NAME = "Mileage"


def spec(cfg: Config) -> SheetSpec:
    unit = cfg.distance_unit
    columns = [
        id_col("date", '"TR-"'),
        Col("date", "Trip date", 12, "date", validate=date_check()),
        Col("staff", "Driver", 15, "text", validate=list_from("StaffNames")),
        Col("client", "Client / booking", 20, "text",
            validate=list_from("ClientNames")),
        Col("purpose", "Purpose", 16, "text",
            validate=list_from("TripPurposeList")),
        Col("start_loc", "From", 20, "text"),
        Col("end_loc", "To", 20, "text"),
        Col("start_odo", "Odometer start", 12, "number1",
            validate=number_check(0, 10000000)),
        Col("end_odo", "Odometer end", 12, "number1",
            validate=number_check(0, 10000000)),
        Col("manual_km", f"Manual {unit}", 10, "number1",
            validate=number_check(0, 10000),
            note="Only needed when you did not record odometer readings."),
        Col("trip_km", f"Trip {unit}", 10, "number1",
            formula='=IF(AND({start_odo}{r}<>"",{end_odo}{r}<>""),'
                    'ROUND({end_odo}{r}-{start_odo}{r},1),'
                    'IF({manual_km}{r}="","",{manual_km}{r}))'),
        Col("round_trip", "Round trip?", 9, "flag", validate=yes_no()),
        Col("total_km", f"Total {unit}", 10, "number1",
            formula='=IF({trip_km}{r}="","",IF({round_trip}{r}="Yes",'
                    'ROUND({trip_km}{r}*2,1),{trip_km}{r}))',
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("business", "Classification", 12, "status",
            formula=blank("purpose",
                          'IF({purpose}{r}="Personal","Personal",'
                          '"Business")'),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Business", "fmt": "good"},
                {"type": "text", "criteria": "containing",
                 "value": "Personal", "fmt": "muted"}]),
        Col("rate", "Rate", 10, "money",
            formula=blank("date", "MileageRate")),
        Col("reimbursement", "Mileage claim", 12, "money",
            formula='=IF({total_km}{r}="","",IF({business}{r}="Business",'
                    'ROUND({total_km}{r}*MileageRate,2),0))'),
        Col("fuel", "Fuel cost", 10, "money",
            validate=number_check(0, 100000),
            note="For reference only - the mileage rate already covers "
                 "fuel. Log fuel receipts on the Expenses tab if you claim "
                 "actual costs instead."),
        Col("parking", "Parking", 10, "money",
            validate=number_check(0, 100000)),
        Col("tolls", "Tolls", 10, "money", validate=number_check(0, 100000)),
        Col("travel_mins", "Travel time (min)", 10, "int",
            validate=number_check(0, 1440, decimal=False)),
        Col("claimable", "Total claimable", 12, "money",
            formula=blank("date",
                          'ROUND(IF({reimbursement}{r}="",0,'
                          '{reimbursement}{r})+IF({business}{r}="Business",'
                          'IF({parking}{r}="",0,{parking}{r})'
                          '+IF({tolls}{r}="",0,{tolls}{r}),0),2)')),
        Col("notes", "Notes", 26, "wrap"),
        month_col("date"),
        Col("alert", "Check", 20, "status",
            formula=blank(
                "date",
                'IF(AND({start_odo}{r}<>"",{end_odo}{r}<>"",'
                '{end_odo}{r}<{start_odo}{r}),"Check odometer readings",'
                'IF({trip_km}{r}="","Action - add distance",'
                'IF({purpose}{r}="","Action - add a purpose","OK")))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Mileage & Travel Log",
        subtitle=f"Odometer in, odometer out: {unit} travelled, round "
                 "trips, reimbursement, parking and tolls - ready for your "
                 "tax return.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.accent,
        freeze_cols=2,
        samples=sample(cfg).mileage,
        help_text="Record trips as you do them. Business trips are valued "
                  "at the mileage rate from the Settings tab.",
    )
