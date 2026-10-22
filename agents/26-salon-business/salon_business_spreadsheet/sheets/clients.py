"""4 Client CRM - profiles, history and rebooking prompts."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec, max_if, min_if
from ..writer import cf_text, date_check, list_from, number_check
from .. import sample_data

NAME = "4 Client CRM"
SENT = 2958465


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="4  Client CRM",
        subtitle="Every client's history, value and next-visit prompt - "
                 "calculated from the appointment and sales registers.",
        tab_color="#96587A",
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        help_text="Type the contact details once. First visit, last "
                  "visit, visits, lifetime spend and the most recent "
                  "service all come from tabs 3 and 6.",
        columns=[
            Col("id", "Client ID", 10, "id",
                formula='="C-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("name", "Client name", 22, "text",
                note="Use the same spelling everywhere - the drop downs "
                     "and lookups match on this text."),
            Col("phone", "Phone", 15, "text"),
            Col("email", "Email", 26, "text"),
            Col("pref", "Prefers", 9, "flag",
                validate=list_from("ListPrefContact")),
            Col("source", "Found you via", 13, "text",
                validate=list_from("ListChannels")),
            Col("birthday", "Birthday", 12, "date",
                validate=date_check()),
            Col("first", "First visit", 12, "date",
                formula='IF({name}{r}="","",IF(' +
                        min_if("ApptDates", 'ApptClients={name}{r}',
                               'ApptDates>0', sentinel=SENT) +
                        f'>={SENT},"",' +
                        min_if("ApptDates", 'ApptClients={name}{r}',
                               'ApptDates>0', sentinel=SENT) + '))'),
            Col("last", "Last visit", 12, "date",
                formula='IF({name}{r}="","",IF(' +
                        max_if("ApptDates", 'ApptClients={name}{r}',
                               'ApptDone=1') + '="","",' +
                        max_if("ApptDates", 'ApptClients={name}{r}',
                               'ApptDone=1') + '))'),
            Col("visits", "Visits", 7, "int",
                formula='IF({name}{r}="","",COUNTIFS(ApptClients,'
                        '{name}{r},ApptStatus,"Completed"))'),
            Col("spend", "Lifetime spend", 13, "money",
                formula='IF({name}{r}="","",ROUND(SUMIFS(SalesNet,'
                        'SalesClients,{name}{r}),2))'),
            Col("last_service", "Last service", 24, "text",
                formula='IF(OR({name}{r}="",{last}{r}=""),"",'
                        'IFERROR(INDEX(ApptService,MATCH({name}{r}&"|"&'
                        'TEXT({last}{r},"yyyymmdd"),ApptKeys,0)),""))'),
            Col("days_since", "Days since", 9, "int",
                formula='IF({last}{r}="","",TODAY()-{last}{r})'),
            Col("next_due", "Next booking due", 14, "date",
                formula='IF({last}{r}="","",{last}{r}+RebookDays)'),
            Col("status", "Status", 9, "status",
                formula='IF({last}{r}="","",IF({days_since}{r}<='
                        'RebookDays,IF({visits}{r}<=1,"New","Active"),'
                        '"Lapsed"))',
                cf=[cf_text("Lapsed", "warn"), cf_text("New", "info"),
                    cf_text("Active", "good")]),
            Col("referrals", "Referrals sent", 9, "int",
                validate=number_check(0, 999, False)),
            Col("feedback", "Feedback & satisfaction", 30, "wrap"),
            Col("consent_comm", "Marketing consent", 11, "flag",
                validate=list_from("ListConsent"),
                cf=[cf_text("No", "warn")]),
            Col("consent_photos", "Photo consent", 10, "flag",
                validate=list_from("ListConsent"),
                cf=[cf_text("No", "warn")]),
            Col("notes", "Preferences & allergies", 34, "wrap"),
        ],
        samples=sample_data.client_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Status: New = one visit, Active = inside the rebooking "
            "window, Lapsed = overdue. Filter on Lapsed for your win-back "
            "list.",
            "Consent columns are your record for messages and photos - "
            "check them before every campaign.",
        ],
    )
