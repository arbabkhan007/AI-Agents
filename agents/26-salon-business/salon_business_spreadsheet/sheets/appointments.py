"""3 Appointment Planner - the booking register."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, date_check, list_from, number_check, \
    time_check
from .. import sample_data

NAME = "3 Appointment Planner"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="3  Appointment Planner",
        subtitle="One row per booking - category, duration and price fill "
                 "themselves from the service menu.",
        tab_color="#6D2E4F",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="Type the date, time, client, staff and service (drop "
                  "downs), then the status as the booking moves. Deposit "
                  "is money taken before the visit; balance due is what "
                  "is left to collect.",
        columns=[
            Col("id", "Appt ID", 10, "id",
                formula='="A-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("time", "Time", 9, "time", validate=time_check()),
            Col("client", "Client", 20, "text",
                validate=list_from("ClientNames"),
                note="Pick from the client list - new clients are added "
                     "on tab 4 and appear here at once."),
            Col("staff", "Staff", 16, "text",
                validate=list_from("StaffNames")),
            Col("service", "Service", 26, "text",
                validate=list_from("ServiceNames")),
            Col("category", "Category", 11, "text",
                formula='IF({service}{r}="","",IFERROR(INDEX(ServiceCat,'
                        'MATCH({service}{r},ServiceNames,0)),""))'),
            Col("duration", "Mins", 7, "int",
                formula='IF({service}{r}="","",IFERROR(INDEX(ServiceDur,'
                        'MATCH({service}{r},ServiceNames,0)),""))'),
            Col("price", "Price", 10, "money",
                formula='IF({service}{r}="","",IFERROR(INDEX('
                        'ServicePrice,MATCH({service}{r},ServiceNames,0)),'
                        '""))'),
            Col("status", "Status", 11, "status",
                validate=list_from("ListStatus"),
                cf=[cf_text("No-show", "bad"), cf_text("Cancelled", "warn"),
                    cf_text("Completed", "good")],
                note="Booked / Confirmed are open. Completed, Cancelled "
                     "and No-show are final and feed every KPI."),
            Col("deposit", "Deposit", 10, "money",
                validate=number_check(0, 100000)),
            Col("balance", "Balance due", 11, "money",
                formula='IF({price}{r}="","",ROUND(N({price}{r})'
                        '-N({deposit}{r}),2))'),
            Col("source", "Booked via", 12, "text",
                validate=list_from("ListChannels")),
            Col("walkin", "Walk-in", 9, "flag",
                validate=list_from("ListConsent")),
            Col("cancel_reason", "Cancellation reason", 24, "wrap"),
            Col("rescheduled", "Rescheduled from", 16, "text",
                note="Original date/time when you move a booking."),
            Col("followup", "Rebook reminder", 14, "date",
                formula='IF(OR({date}{r}="",{status}{r}<>"Completed"),"",'
                        '{date}{r}+RebookDays)',
                note="Visit date + the rebooking interval from Settings."),
            Col("final", "final", 6, "flag", hidden=True,
                formula='IF({status}{r}="","",IF(OR({status}{r}='
                        '"Completed",{status}{r}="Cancelled",{status}{r}='
                        '"No-show"),1,0))'),
            Col("done", "done", 6, "flag", hidden=True,
                formula='IF({status}{r}="Completed",1,0)'),
            Col("key", "key", 14, "text", hidden=True,
                formula='IF(OR({client}{r}="",{date}{r}=""),"",'
                        '{client}{r}&"|"&TEXT({date}{r},"yyyymmdd"))'),
            Col("notes", "Notes & preferences", 34, "wrap"),
        ],
        samples=sample_data.appointment_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "A deposit is not revenue until the visit is completed and "
            "invoiced on tab 6 - the dashboard keeps unearned deposits "
            "separate.",
            "Double-booking check: filter by staff and date, sorted by "
            "time; the duration column shows the slot each booking holds.",
        ],
    )
