"""`Clients` - the client database with lifetime value and follow-up flags."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import (alert_cf, blank, dup_cf, id_col, owing_cf,
                     status_cf)

NAME = "Clients"

_LAST_SERVICE = ('SUMPRODUCT(MAX(([[Bookings.client]]={name}{r})'
                 '*([[Bookings.status]]="Completed")*[[Bookings.date]]))')
_NEXT_BOOKING = ('SUMPRODUCT(MIN((([[Bookings.client]]={name}{r})'
                 '*([[Bookings.date]]>=TODAY())'
                 '*([[Bookings.status]]<>"Cancelled"))*[[Bookings.date]]'
                 '+(1-(([[Bookings.client]]={name}{r})'
                 '*([[Bookings.date]]>=TODAY())'
                 '*([[Bookings.status]]<>"Cancelled")))*2958465))')


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("name", "ClientPrefix"),
        Col("name", "Client name", 22, "text",
            note="Used everywhere else in the workbook. If two clients "
                 "share a name add an initial, e.g. 'Sam B.'."),
        Col("phone", "Phone", 17, "text"),
        Col("email", "Email", 26, "text"),
        Col("address", "Street address", 26, "text"),
        Col("city", "City / suburb", 15, "text"),
        Col("postcode", "Post code", 10, "text"),
        Col("emergency_name", "Emergency contact", 20, "text"),
        Col("emergency_phone", "Emergency phone", 17, "text"),
        Col("contact_method", "Preferred contact", 14, "text",
            validate=list_from("ContactMethodList")),
        Col("referral", "Referral source", 16, "text",
            validate=list_from("ReferralSourceList")),
        Col("reg_date", "Registered on", 13, "date", validate=date_check()),
        Col("status", "Status", 12, "status",
            validate=list_from("ClientStatusList"), cf=status_cf()),
        Col("key_status", "Key / access", 14, "text",
            validate=list_from("KeyStatusList")),
        Col("key_tag", "Key tag / ref", 12, "text"),
        Col("key_returned", "Key returned on", 13, "date",
            validate=date_check()),
        Col("access_notes", "Home access instructions", 32, "wrap"),
        Col("access_code", "Alarm / gate code", 16, "text",
            note="Security tip: store full alarm codes in a separate "
                 "password manager and keep only a hint here."),
        Col("contract", "Contract status", 13, "status",
            validate=list_from("ContractStatusList"), cf=status_cf()),
        Col("agreement_date", "Agreement signed", 13, "date",
            validate=date_check()),
        Col("vet_consent", "Emergency vet consent", 11, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("vet_limit", "Vet spend authority", 12, "money",
            validate=number_check(0, 100000)),
        Col("preferences", "Preferences & special instructions", 36, "wrap"),
        Col("notes", "Notes & communication history", 36, "wrap"),
        Col("pets", "Pets", 8, "int",
            formula=blank("name", 'COUNTIF([[Pets.owner]],{name}{r})')),
        Col("bookings", "Bookings", 9, "int",
            formula=blank("name",
                          'COUNTIFS([[Bookings.client]],{name}{r})')),
        Col("visits", "Visits done", 9, "int",
            formula=blank("name",
                          'COUNTIFS([[Visit Log.client]],{name}{r},'
                          '[[Visit Log.status]],"Completed")')),
        Col("last_service", "Last service", 13, "date",
            formula=('=IF({name}{r}="","",'
                     f'IF({_LAST_SERVICE}=0,"",{_LAST_SERVICE}))')),
        Col("days_since", "Days since", 9, "int",
            formula='=IF({last_service}{r}="","",TODAY()-{last_service}{r})',
            cf=[{"type": "cell", "criteria": ">",
                 "value": "=InactiveDays", "fmt": "warn"}]),
        Col("next_booking", "Next booking", 13, "date",
            formula=('=IF({name}{r}="","",IF(COUNTIFS([[Bookings.client]],'
                     '{name}{r},[[Bookings.date]],">="&TODAY(),'
                     '[[Bookings.status]],"<>Cancelled")=0,"",'
                     f'{_NEXT_BOOKING}))')),
        Col("revenue", "Lifetime revenue", 14, "money",
            formula=blank("name",
                          'SUMIFS([[Payments.received]],'
                          '[[Payments.client]],{name}{r})'),
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("invoiced", "Invoiced to date", 14, "money",
            formula=blank("name",
                          'SUMIFS([[Invoices.total]],[[Invoices.client]],'
                          '{name}{r},[[Invoices.status]],"<>Draft")')),
        Col("outstanding", "Outstanding", 13, "money",
            formula=blank("name",
                          'SUMIFS([[Invoices.balance]],[[Invoices.client]],'
                          '{name}{r},[[Invoices.status]],"<>Cancelled")'),
            cf=owing_cf()),
        Col("avg_booking", "Average booking", 13, "money",
            formula='=IF(OR({bookings}{r}="",{bookings}{r}=0),"",'
                    'SUMIFS([[Bookings.total]],[[Bookings.client]],'
                    '{name}{r},[[Bookings.status]],"<>Cancelled")'
                    '/{bookings}{r})'),
        Col("loyalty", "Loyalty status", 14, "status",
            formula=blank("name",
                          'IF({bookings}{r}>=LoyaltyThreshold,'
                          '"Loyalty discount","Standard")'),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Loyalty", "fmt": "good"}]),
        Col("dup_check", "Duplicate check", 14, "status",
            formula=blank("name",
                          'IF(COUNTIF([[Clients.name]],{name}{r})>1,'
                          '"Duplicate name",IF(AND({phone}{r}<>"",'
                          'COUNTIF([[Clients.phone]],{phone}{r})>1),'
                          '"Duplicate phone","OK"))'),
            cf=dup_cf()),
        Col("data_check", "Missing information", 20, "status",
            formula=blank("name",
                          'IF(AND({phone}{r}<>"",{email}{r}<>"",'
                          '{reg_date}{r}<>"",{status}{r}<>""),"OK",'
                          '"Add: "&IF({phone}{r}="","phone ","")'
                          '&IF({email}{r}="","email ","")'
                          '&IF({reg_date}{r}="","date ","")'
                          '&IF({status}{r}="","status",""))'),
            cf=alert_cf()),
        Col("alert", "Action needed", 22, "status",
            formula=blank(
                "name",
                'IF({outstanding}{r}>0.5,"Overdue - chase payment",'
                'IF(AND({status}{r}="Active",ISNUMBER({days_since}{r}),'
                '{days_since}{r}>InactiveDays),"Inactive - win back",'
                'IF(AND({status}{r}="Active",{contract}{r}<>"Signed"),'
                '"Action - contract not signed",'
                'IF(AND({status}{r}="Prospective",{next_booking}{r}=""),'
                '"Action - follow up quote","OK"))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Client Database",
        subtitle="One row per client. Grey columns calculate pets, visits, "
                 "lifetime revenue, outstanding balances and follow-up "
                 "actions for you.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary,
        freeze_cols=2,
        samples=sample(cfg).clients,
        help_text="Type the client name first - the Client ID appears "
                  "automatically. Use the filter arrows in the header row "
                  "to search; avoid re-sorting rows so IDs stay stable.",
    )
