"""`Visit Log` - the daily pet care log, one row per visit or walk."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, month_col, status_cf

NAME = "Visit Log"


def _bk(field: str, fallback: str = '""') -> str:
    return (f'IFERROR(INDEX([[Bookings.{field}]],'
            f'MATCH({{booking}}{{r}},[[Bookings.id]],0)),{fallback})')


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"VS-"'),
        Col("booking", "Booking ID", 12, "text",
            validate=list_from("BookingIDs"),
            note="Pick the booking and the client, pet, service and "
                 "scheduled time fill themselves in."),
        Col("date", "Visit date", 12, "date", validate=date_check()),
        Col("client", "Client", 20, "text",
            formula=blank("booking", _bk("client"))),
        Col("pet", "Pet", 24, "text",
            formula=blank("booking", _bk("pet"))),
        Col("service", "Service", 22, "text",
            formula=blank("booking", _bk("service"))),
        Col("staff", "Carer", 15, "text", validate=list_from("StaffNames")),
        Col("sched_start", "Scheduled", 9, "time",
            formula=blank("booking", _bk("start", '""'))),
        Col("arrive", "Arrived", 9, "time"),
        Col("depart", "Departed", 9, "time"),
        Col("duration", "Minutes on site", 10, "int",
            formula='=IF(OR({arrive}{r}="",{depart}{r}=""),"",'
                    'ROUND(({depart}{r}-{arrive}{r}'
                    '+IF({depart}{r}<{arrive}{r},1,0))*1440,0))'),
        Col("punctual", "On time?", 13, "status",
            formula='=IF(OR({arrive}{r}="",{sched_start}{r}=""),"",'
                    'IF({arrive}{r}<={sched_start}{r}+TIME(0,10,0),'
                    '"On time","Late "'
                    '&TEXT(({arrive}{r}-{sched_start}{r})*1440,"0")&" min"))',
            cf=[{"type": "text", "criteria": "containing",
                 "value": "On time", "fmt": "good"},
                {"type": "text", "criteria": "containing",
                 "value": "Late", "fmt": "warn"}]),
        Col("walk_start", "Walk start", 9, "time"),
        Col("walk_end", "Walk end", 9, "time"),
        Col("walk_mins", "Walk minutes", 9, "int",
            formula='=IF(OR({walk_start}{r}="",{walk_end}{r}=""),"",'
                    'ROUND(({walk_end}{r}-{walk_start}{r}'
                    '+IF({walk_end}{r}<{walk_start}{r},1,0))*1440,0))'),
        Col("walk_distance", "Distance walked", 10, "number1",
            validate=number_check(0, 100)),
        Col("fed", "Fed", 8, "flag", validate=list_from("YesNoNAList"),
            cf=status_cf()),
        Col("water", "Fresh water", 9, "flag",
            validate=list_from("YesNoNAList"), cf=status_cf()),
        Col("meds", "Medication given", 10, "flag",
            validate=list_from("YesNoNAList"), cf=status_cf()),
        Col("potty", "Potty / litter", 14, "text",
            validate=list_from("PottyList")),
        Col("play", "Exercise & play", 22, "text"),
        Col("grooming", "Grooming / cleaning", 20, "text"),
        Col("mood", "Mood & behaviour", 14, "text",
            validate=list_from("MoodList"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Unwell", "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Anxious", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Aggressive", "fmt": "bad"}]),
        Col("appetite", "Appetite", 12, "text",
            validate=list_from("AppetiteList"),
            cf=[{"type": "text", "criteria": "containing", "value": "None",
                 "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Reduced", "fmt": "warn"}]),
        Col("health", "Health observations", 30, "wrap"),
        Col("incident", "Incident?", 9, "flag", validate=yes_no(),
            cf=[{"type": "text", "criteria": "containing", "value": "Yes",
                 "fmt": "bad"}]),
        Col("incident_ref", "Incident ref", 11, "text"),
        Col("photos", "Photos / report link", 20, "text"),
        Col("update_sent", "Client updated", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("checklist", "Care checklist done", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("status", "Visit status", 15, "status",
            validate=list_from("VisitStatusList"), cf=status_cf()),
        Col("notes", "Visit notes", 36, "wrap"),
        month_col("date"),
        # Hidden helper keys used by the printable report sheets: they
        # number each visit within its booking / pet so a one page report
        # can pull "line 1, line 2, ..." without array formulas.
        Col("line_key", "Line key", 10, "text", hidden=True,
            formula='=IF({booking}{r}="","",{booking}{r}&"|"'
                    '&COUNTIF(${booking}${first}:${booking}{r},'
                    '{booking}{r}))'),
        Col("pet_key", "Pet key", 10, "text", hidden=True,
            formula='=IF({pet}{r}="","",{pet}{r}&"|"'
                    '&COUNTIF(${pet}${first}:${pet}{r},{pet}{r}))'),
        Col("alert", "Action needed", 24, "status",
            formula=blank(
                "date",
                'IF({status}{r}="Missed","Missed visit - contact client",'
                'IF({incident}{r}="Yes","Incident logged - follow up",'
                'IF(AND({status}{r}="Completed",{update_sent}{r}<>"Yes"),'
                '"Action - send client update",'
                'IF(AND({status}{r}="Completed",{checklist}{r}<>"Yes"),'
                '"Check care checklist",'
                'IF(AND({date}{r}<TODAY(),{status}{r}="Scheduled"),'
                '"Overdue - log the result","OK")))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Daily Visit & Pet Care Log",
        subtitle="Proof of service for every walk, drop-in and overnight: "
                 "times, care given, mood, health notes and client updates.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.accent,
        freeze_cols=3,
        samples=sample(cfg).visits,
        help_text="Start with the Booking ID - the client, pet, service "
                  "and scheduled time are pulled in automatically. "
                  "Minutes on site, punctuality and alerts are calculated.",
    )
