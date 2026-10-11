"""`Bookings` - the scheduling engine: prices, surcharges, conflicts, alerts."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, month_col, status_cf

NAME = "Bookings"


def _svc(field: str, fallback: str = "0") -> str:
    """INDEX/MATCH into the Services table for the booked service."""
    return (f'IFERROR(INDEX([[Services.{field}]],'
            f'MATCH({{service}}{{r}},[[Services.name]],0)),{fallback})')


def spec(cfg: Config) -> SheetSpec:
    conflict = ('SUMPRODUCT(([[Bookings.staff]]={staff}{r})'
                '*([[Bookings.date]]={date}{r})'
                '*([[Bookings.start]]<{end}{r})'
                '*([[Bookings.end]]>{start}{r})'
                '*([[Bookings.status]]<>"Cancelled"))')

    columns = [
        id_col("client", "BookingPrefix"),
        Col("request_date", "Requested on", 12, "date",
            validate=date_check(),
            note="When the client asked for the booking. Used to spot "
                 "last-minute bookings."),
        Col("client", "Client", 20, "text",
            validate=list_from("ClientNames")),
        Col("client_id", "Client ID", 10, "text",
            formula=blank("client",
                          'IFERROR(INDEX([[Clients.id]],'
                          'MATCH({client}{r},[[Clients.name]],0)),"")')),
        Col("pet", "Pet", 24, "text", validate=list_from("PetLabels")),
        Col("extra_pets", "Additional pets", 20, "text"),
        Col("pet_count", "No. of pets", 9, "int",
            validate=number_check(1, 20, decimal=False),
            note="Blank counts as 1. Extra pets are charged the additional "
                 "pet fee."),
        Col("service", "Service", 24, "text",
            validate=list_from("ServiceNames")),
        Col("date", "Booking date", 12, "date", validate=date_check()),
        Col("day", "Day", 7, "flag",
            formula=blank("date", 'TEXT({date}{r},"ddd")')),
        Col("start", "Start", 9, "time"),
        Col("end", "End", 9, "time"),
        Col("duration", "Hours", 8, "number",
            formula='=IF(OR({start}{r}="",{end}{r}=""),"",'
                    'ROUND(({end}{r}-{start}{r}+IF({end}{r}<{start}{r},1,0))'
                    '*24,2))'),
        Col("qty", "Qty / nights", 9, "number",
            validate=number_check(0, 1000),
            note="Number of visits, nights or hours being billed. Blank "
                 "counts as 1."),
        Col("unit", "Billing unit", 11, "text",
            formula=blank("service", _svc("unit", '""'))),
        Col("rate", "Rate", 11, "money",
            formula=blank("service", _svc("rate"))),
        Col("pet_rate", "Extra pet rate", 10, "money", hidden=True,
            formula=blank("service",
                          f'IF({_svc("extra_pet")}=0,ExtraPetFeeDefault,'
                          f'{_svc("extra_pet")})')),
        Col("hol_pct", "Holiday %", 9, "percent", hidden=True,
            formula=blank("service",
                          f'IF({_svc("hol_pct")}=0,HolidaySurcharge,'
                          f'{_svc("hol_pct")})')),
        Col("wkd_pct", "Weekend %", 9, "percent", hidden=True,
            formula=blank("service",
                          f'IF({_svc("wkd_pct")}=0,WeekendSurcharge,'
                          f'{_svc("wkd_pct")})')),
        Col("travel_flag", "Travel billable", 9, "flag", hidden=True,
            formula=blank("service", _svc("travel", '"No"'))),
        Col("base", "Base charge", 12, "money",
            formula=blank(
                "service",
                'ROUND(IF({unit}{r}="Per hour",{rate}{r}*IF({duration}{r}="",'
                'IF({qty}{r}="",1,{qty}{r}),{duration}{r}),'
                '{rate}{r}*IF({qty}{r}="",1,{qty}{r})),2)')),
        Col("extra_pet_fee", "Extra pet fee", 11, "money",
            formula=blank("service",
                          'ROUND(MAX(0,IF({pet_count}{r}="",1,'
                          '{pet_count}{r})-1)*{pet_rate}{r},2)')),
        Col("holiday", "Holiday?", 9, "flag",
            formula=blank("date",
                          'IF(COUNTIF(HolidayDates,{date}{r})>0,"Yes","No")'),
            cf=[{"type": "text", "criteria": "containing", "value": "Yes",
                 "fmt": "warn"}]),
        Col("weekend", "Weekend?", 9, "flag",
            formula=blank("date",
                          'IF(WEEKDAY({date}{r},2)>5,"Yes","No")'),
            cf=[{"type": "text", "criteria": "containing", "value": "Yes",
                 "fmt": "info"}]),
        Col("surcharge", "Surcharges", 11, "money",
            formula=blank("service",
                          'ROUND(({base}{r}+{extra_pet_fee}{r})'
                          '*(IF({holiday}{r}="Yes",{hol_pct}{r},0)'
                          '+IF({weekend}{r}="Yes",{wkd_pct}{r},0)),2)')),
        Col("distance", "Travel distance", 10, "number1",
            validate=number_check(0, 2000)),
        Col("travel_fee", "Travel fee", 10, "money",
            formula=blank("service",
                          'IF({travel_flag}{r}<>"Yes",0,'
                          'ROUND(MAX(0,IF({distance}{r}="",0,'
                          '{distance}{r})-FreeTravelDistance)'
                          '*TravelFeeRate,2))')),
        Col("travel_time", "Travel allowance (min)", 10, "int",
            formula=blank("date", "TravelTimeMins")),
        Col("rush_fee", "Last-minute fee", 10, "money",
            formula='=IF(OR({date}{r}="",{request_date}{r}=""),0,'
                    'IF({date}{r}-{request_date}{r}<=LastMinuteDays,'
                    'EmergencyFee,0))',
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"}]),
        Col("discount_type", "Discount type", 13, "text",
            validate=list_from("DiscountTypeList")),
        Col("discount_pct", "Discount %", 9, "percent",
            validate=number_check(0, 1)),
        Col("discount", "Discount", 11, "money",
            formula=blank("service",
                          'ROUND(({base}{r}+{extra_pet_fee}{r}'
                          '+{surcharge}{r}+{travel_fee}{r}+{rush_fee}{r})'
                          '*IF({discount_pct}{r}="",0,{discount_pct}{r}),2)')),
        Col("override", "Price override", 11, "money",
            validate=number_check(0, 100000),
            note="Only fill this in to force a price. Always add the reason "
                 "in the next column."),
        Col("override_note", "Override reason", 20, "text"),
        Col("subtotal", "Subtotal", 12, "money",
            formula=blank("service",
                          'IF({override}{r}<>"",{override}{r},'
                          'ROUND({base}{r}+{extra_pet_fee}{r}+{surcharge}{r}'
                          '+{travel_fee}{r}+{rush_fee}{r}-{discount}{r},2))')),
        Col("tax", "Tax", 10, "money",
            formula='=IF({subtotal}{r}="","",IF(TaxRegistered<>"Yes",0,'
                    'IF(PricesIncludeTax="Yes",'
                    'ROUND({subtotal}{r}-{subtotal}{r}/(1+TaxRate),2),'
                    'ROUND({subtotal}{r}*TaxRate,2))))'),
        Col("total", "Booking total", 13, "money",
            formula='=IF({subtotal}{r}="","",IF(PricesIncludeTax="Yes",'
                    '{subtotal}{r},ROUND({subtotal}{r}+{tax}{r},2)))',
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("staff", "Assigned to", 16, "text",
            validate=list_from("StaffNames")),
        Col("status", "Status", 13, "status",
            validate=list_from("BookingStatusList"), cf=status_cf()),
        Col("confirm_sent", "Confirmed to client", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("reminder_sent", "Reminder sent", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("recurring", "Repeats", 12, "text",
            validate=list_from("RecurringList")),
        Col("next_due", "Next booking due", 13, "date",
            formula='=IF(OR({date}{r}="",{recurring}{r}="",'
                    '{recurring}{r}="None"),"",'
                    'IF({recurring}{r}="Monthly",EDATE({date}{r},1),'
                    '{date}{r}+IF({recurring}{r}="Daily",1,'
                    'IF({recurring}{r}="Weekdays",'
                    'IF(WEEKDAY({date}{r},2)>=5,8-WEEKDAY({date}{r},2),1),'
                    'IF({recurring}{r}="Weekly",7,'
                    'IF({recurring}{r}="Fortnightly",14,0))))))'),
        Col("conflict", "Schedule check", 18, "status",
            formula=('=IF(OR({date}{r}="",{staff}{r}="",{start}{r}="",'
                     '{end}{r}=""),"",IF(' + conflict +
                     '>1,"Conflict - double booked","OK"))'),
            cf=alert_cf()),
        Col("visit_logged", "Visit logged", 10, "flag",
            formula=blank("id",
                          'IF(COUNTIF([[Visit Log.booking]],{id}{r})>0,'
                          '"Yes","No")'),
            cf=status_cf()),
        Col("invoice_no", "Invoice", 12, "text",
            formula=blank("id",
                          'IFERROR(INDEX([[Invoices.invoice_no]],'
                          'MATCH({id}{r},[[Invoices.booking]],0)),"")')),
        Col("paid_status", "Payment status", 15, "status",
            formula=blank("id",
                          'IF({invoice_no}{r}="","Not invoiced",'
                          'IFERROR(INDEX([[Invoices.pay_status]],'
                          'MATCH({invoice_no}{r},'
                          '[[Invoices.invoice_no]],0)),""))'),
            cf=status_cf() + [{"type": "text", "criteria": "containing",
                               "value": "Not invoiced", "fmt": "warn"}]),
        Col("cancel_reason", "Cancellation reason", 18, "text",
            validate=list_from("CancelReasonList")),
        Col("resched_from", "Rescheduled from", 12, "date",
            validate=date_check()),
        Col("notes", "Notes & special requests", 34, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 24, "status",
            formula=blank(
                "date",
                'IF({status}{r}="Cancelled","Cancelled",'
                'IF(AND({date}{r}<TODAY(),OR({status}{r}="Pending",'
                '{status}{r}="Confirmed",{status}{r}="Enquiry")),'
                '"Overdue - update status",'
                'IF(AND({status}{r}="Completed",{visit_logged}{r}="No"),'
                '"Action - log the visit",'
                'IF({date}{r}=TODAY(),"Today",'
                'IF(AND({date}{r}>TODAY(),{date}{r}-TODAY()<=ReminderLeadDays,'
                '{confirm_sent}{r}<>"Yes"),"Action - unconfirmed",'
                'IF(AND({date}{r}>TODAY(),'
                '{date}{r}-TODAY()<=ReminderLeadDays),"Upcoming","OK"))))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Bookings & Schedule",
        subtitle="Every booking, priced automatically from the Services "
                 "tab with holiday, weekend, extra pet, travel and "
                 "last-minute rules applied.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.accent,
        freeze_cols=3,
        samples=sample(cfg).bookings,
        help_text="Fill the cream cells from left to right. Everything "
                  "grey - prices, surcharges, totals, conflicts and alerts "
                  "- is calculated and locked.",
    )
