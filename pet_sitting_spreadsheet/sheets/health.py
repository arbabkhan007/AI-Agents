"""`Health Log` - medication administration, vaccinations and vet events."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, month_col, status_cf

NAME = "Health Log"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"HL-"'),
        Col("date", "Date", 12, "date", validate=date_check()),
        Col("time", "Time", 9, "time"),
        Col("pet", "Pet", 24, "text", validate=list_from("PetLabels")),
        Col("client", "Client", 20, "text",
            formula=blank("pet",
                          'IFERROR(INDEX([[Pets.owner]],'
                          'MATCH({pet}{r},[[Pets.label]],0)),"")')),
        Col("type", "Record type", 16, "text",
            validate=list_from("HealthRecordTypeList")),
        Col("item", "Medication / treatment", 24, "text"),
        Col("dosage", "Dosage & instructions", 28, "wrap"),
        Col("sched_time", "Scheduled", 9, "time"),
        Col("given_time", "Given at", 9, "time"),
        Col("staff", "Given by", 15, "text", validate=list_from("StaffNames")),
        Col("status", "Status", 13, "status",
            validate=list_from("MedStatusList"), cf=status_cf()),
        Col("supply", "Supply left", 10, "number1",
            validate=number_check(0, 10000),
            note="Doses, tablets or ml left in the client's supply."),
        Col("refill_due", "Refill due", 12, "date", validate=date_check()),
        Col("refill_alert", "Refill alert", 16, "status",
            formula=blank("refill_due",
                          'IF({refill_due}{r}<TODAY(),"Overdue - refill now",'
                          'IF({refill_due}{r}-TODAY()<=ExpiryAlertDays,'
                          '"Due in "&TEXT({refill_due}{r}-TODAY(),"0")'
                          '&" days","OK"))'),
            cf=alert_cf()),
        Col("vet_appt", "Vet appointment", 12, "date",
            validate=date_check()),
        Col("appt_alert", "Appointment alert", 16, "status",
            formula=blank("vet_appt",
                          'IF({vet_appt}{r}<TODAY(),"Past",'
                          'IF({vet_appt}{r}-TODAY()<=ExpiryAlertDays,'
                          '"Due in "&TEXT({vet_appt}{r}-TODAY(),"0")'
                          '&" days","Booked"))'),
            cf=alert_cf() + [{"type": "text", "criteria": "containing",
                              "value": "Booked", "fmt": "good"}]),
        Col("cost", "Cost", 11, "money", validate=number_check(0, 100000),
            note="Vet bills or treatment costs you paid on behalf of the "
                 "client - recharge them on the invoice."),
        Col("notified", "Owner notified", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("notes", "Notes", 34, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 24, "status",
            formula=blank(
                "date",
                'IF({status}{r}="Missed","Missed dose - tell the owner",'
                'IF({status}{r}="Refused","Refused - monitor and report",'
                'IF(AND({status}{r}="Scheduled",{date}{r}<TODAY()),'
                '"Overdue - not recorded",'
                'IF(AND({notified}{r}<>"Yes",{type}{r}="Vet visit"),'
                '"Action - update the owner","OK"))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Medication & Health Monitoring",
        subtitle="A dated record of every dose given, vaccination, vet "
                 "visit and health observation - your proof of care.",
        columns=columns,
        rows=cfg.row_count("Health"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
        samples=sample(cfg).health,
        help_text="Log every dose, even missed ones. The alerts column "
                  "tells you what still needs an owner conversation.",
    )
