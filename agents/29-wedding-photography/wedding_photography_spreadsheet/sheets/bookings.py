"""Wedding Bookings - one row per wedding, and the spine of the file.

The Booking ID generated here is what the timeline, the shot list, the
contracts, the payments, the editing workflow, the gallery, the travel
log and the profit analysis all point back at.  Nothing else in the
workbook is allowed to identify a wedding by the couple's name.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, time_check
from .common import (alert_cf, countdown_band, date_num_col,
                     flag_no_bad_cf, hours_between, id_col, is_earning,
                     is_holding, is_shot, lookup_client, lookup_package_num,
                     lookup_staff, money_cf, month_col, owing_cf,
                     rank_desc, sales_tax, seq_num_col, status_cf,
                     weekday_col, year_col, zero)

NAME = "Wedding Bookings"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("client", "BookingPrefix", digits=cfg.digits("booking"),
               header="Booking ID",
               note="Automatic, and the most important value in the "
                    "workbook. Nine other tabs join to it."),

        # ---- who and when -------------------------------------------------
        Col("client", "Client ID", 11, "id",
            validate=list_from("ClientList"),
            note="Pick the couple from the Client CRM. Everything else "
                 "about them follows from this one cell.",
            group="The wedding"),
        Col("client_name", "Couple", 20, "text",
            formula=lookup_client("name"), group="The wedding"),
        Col("partner_name", "Partner", 16, "text",
            formula=lookup_client("partner"), group="The wedding"),
        Col("wedding_date", "Wedding date", 13, "date",
            validate=date_check(),
            note="The one date the whole workbook counts from.",
            group="The wedding"),
        weekday_col("wedding_date", header="Day"),
        Col("status", "Booking status", 14, "status",
            validate=list_from("BookingStatusList"), cf=status_cf(),
            note="Pencilled in holds the date but earns nothing. "
                 "Confirmed means signed and deposit paid.",
            group="The wedding"),
        Col("confirmed_date", "Confirmed on", 12, "date",
            validate=date_check(), group="The wedding"),

        # ---- the day ------------------------------------------------------
        Col("ceremony_time", "Ceremony", 10, "time",
            validate=time_check(),
            note="The anchor for the whole wedding-day timeline - every "
                 "default event time is an offset from this.",
            group="The day"),
        Col("reception_time", "Reception", 10, "time",
            validate=time_check(), group="The day"),
        Col("photo_start", "Coverage from", 11, "time",
            validate=time_check(), group="The day"),
        Col("photo_end", "Coverage to", 11, "time",
            validate=time_check(),
            note="If you finish after midnight the workbook still gets "
                 "the hours right.",
            group="The day"),
        Col("venue", "Main venue", 20, "text", group="The day"),
        Col("venue_type", "Venue type", 13, "text",
            validate=list_from("VenueTypeList"), group="The day"),
        Col("prep_location", "Getting ready at", 20, "text",
            group="The day"),
        Col("ceremony_location", "Ceremony at", 20, "text",
            group="The day"),
        Col("reception_location", "Reception at", 20, "text",
            group="The day"),
        Col("guests", "Guests", 8, "int",
            validate=number_check(0, 2000), group="The day"),

        # ---- the team -----------------------------------------------------
        Col("photographer", "Lead photographer", 16, "id",
            validate=list_from("StaffList"), group="The team"),
        Col("photographer_name", "Lead name", 16, "text",
            formula=lookup_staff("name"), group="The team"),
        Col("second", "Second shooter", 14, "id",
            validate=list_from("StaffList"),
            note="Leave blank if shooting alone. Record actual costs on "
                 "Expense Tracker against this Booking ID.",
            group="The team"),
        Col("second_name", "Second name", 15, "text",
            formula=lookup_staff("name", key="second", missing=""),
            group="The team"),

        # ---- the money ----------------------------------------------------
        Col("package", "Package", 17, "text",
            validate=list_from("PackageList"),
            note="Pick from Packages & Pricing. The price, the hours "
                 "and the inclusions all come from that tab.",
            group="The money"),
        Col("package_price", "Package price", 13, "money",
            formula=lookup_package_num("total_price"),
            cf=money_cf(), group="The money"),
        Col("package_hours", "Hours included", 12, "number1",
            formula=lookup_package_num("hours"), group="The money"),
        Col("coverage_hours", "Hours booked", 12, "number1",
            formula=('=IF({client}{r}="","",'
                     + hours_between("{photo_start}{r}", "{photo_end}{r}")
                     + ")"),
            note="Worked out from the coverage times, so overtime "
                 "cannot be forgotten about.",
            group="The money"),
        Col("extra_hours", "Extra hours", 10, "number1",
            formula=('=IF({client}{r}="",0,'
                     'MAX(0,{coverage_hours}{r}-{package_hours}{r}))'),
            group="The money"),
        Col("extra_hour_fee", "Extra hour charge", 14, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({extra_hours}{r}*ExtraHourRate,2))'),
            group="The money"),
        Col("addons", "Other add-ons", 13, "money",
            validate=number_check(0, 1000000),
            note="Albums, extra prints, a drone, a rehearsal dinner. "
                 "Type the total you agreed.",
            group="The money"),
        Col("travel_fee", "Travel charged", 13, "money",
            validate=number_check(0, 100000),
            note="Leave blank to let the Travel & Mileage tab work it "
                 "out from the distance and your mileage rate.",
            group="The money"),
        Col("travel_used", "Travel used", 12, "money",
            formula=('=IF({client}{r}="",0,IF({travel_fee}{r}<>"",'
                     '{travel_fee}{r},'
                     'SUMIFS([[Travel & Mileage.chargeable]],'
                     '[[Travel & Mileage.booking]],{id}{r})))'),
            hidden=True, group="The money"),
        Col("discount", "Discount", 11, "money",
            validate=number_check(0, 1000000), group="The money"),
        Col("subtotal", "Subtotal", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({package_price}{r}+{extra_hour_fee}{r}+'
                     'IF({addons}{r}="",0,{addons}{r})+{travel_used}{r}-'
                     'IF({discount}{r}="",0,{discount}{r}),2))'),
            group="The money"),
        Col("tax", "Tax", 11, "money",
            formula=('=IF({client}{r}="",0,'
                     + sales_tax("{subtotal}{r}") + ")"),
            group="The money"),
        Col("total_value", "Total booking value", 15, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({subtotal}{r}+{tax}{r},2))'),
            cf=money_cf(),
            note="What this wedding is worth. Every revenue figure in "
                 "the workbook is a sum of this column.",
            group="The money"),

        # ---- getting paid --------------------------------------------------
        Col("deposit_due_amount", "Deposit due", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({total_value}{r}*DepositPercent,2))'),
            group="Getting paid"),
        Col("deposit_due_date", "Deposit by", 12, "date",
            formula=('=IF({client}{r}="","",'
                     'IF({confirmed_date}{r}="","",'
                     '{confirmed_date}{r}+DepositDays))'),
            group="Getting paid"),
        Col("final_due_date", "Final payment by", 14, "date",
            formula=('=IF({client}{r}="","",IF({wedding_date}{r}="","",'
                     '{wedding_date}{r}-FinalPaymentDays))'),
            note="Your own rule from Settings, counted back from the "
                 "wedding day.",
            group="Getting paid"),
        Col("collected", "Collected", 12, "money",
            formula=zero("client",
                         'SUMIFS([[Payments & Invoices.received]],'
                         '[[Payments & Invoices.booking]],{id}{r})'),
            cf=money_cf(), group="Getting paid"),
        Col("outstanding", "Outstanding", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({total_value}{r}-{collected}{r},2))'),
            cf=owing_cf(), group="Getting paid"),
        Col("paid_pct", "Paid", 8, "percent0",
            formula=('=IF({client}{r}="","",IF({total_value}{r}<=0,"",'
                     '{collected}{r}/{total_value}{r}))'),
            group="Getting paid"),
        Col("deposit_paid", "Deposit in", 10, "flag",
            formula=('=IF({client}{r}="","",'
                     'IF({collected}{r}>={deposit_due_amount}{r},'
                     'IF({deposit_due_amount}{r}<=0,"n/a","Yes"),"No"))'),
            cf=flag_no_bad_cf(), group="Getting paid"),
        Col("payment_state", "Payment status", 14, "status",
            formula=('=IF({client}{r}="","",'
                     'IF({total_value}{r}<=0,"Nothing to pay",'
                     'IF({outstanding}{r}<=0.004,"Paid in full",'
                     'IF({collected}{r}<=0,'
                     'IF({final_due_date}{r}<>"",'
                     'IF(TodayDate>{final_due_date}{r},"Overdue","Due"),'
                     '"Due"),'
                     'IF({final_due_date}{r}<>"",'
                     'IF(TodayDate>{final_due_date}{r},"Overdue",'
                     '"Part paid"),"Part paid")))))'),
            cf=status_cf(), group="Getting paid"),

        # ---- the questionnaire ---------------------------------------------
        Col("must_haves", "Must-have photographs", 30, "wrap",
            note="The shots they will be upset not to have. Read this "
                 "the night before, not on the morning.",
            group="What they told you"),
        Col("family_list", "Family group list", 30, "wrap",
            note="Write the groups out by name. 'Bride's family' is "
                 "how a forty-minute family session happens.",
            group="What they told you"),
        Col("key_guests", "Important guests", 24, "wrap",
            group="What they told you"),
        Col("traditions", "Traditions and rituals", 24, "wrap",
            note="Anything cultural or religious you need to know "
                 "about, and when in the day it happens.",
            group="What they told you"),
        Col("restrictions", "Venue restrictions", 24, "wrap",
            note="No flash in the church, no photographs during the "
                 "ceremony, a balcony you may not stand on.",
            group="What they told you"),
        Col("sensitivities", "Family sensitivities", 24, "wrap",
            note="Divorced parents, a recent bereavement, somebody who "
                 "must not be in a group shot with somebody else.",
            group="What they told you"),
        Col("special_requests", "Special requests", 24, "wrap",
            group="What they told you"),
        Col("questionnaire_sent", "Questionnaire sent", 13, "date",
            validate=date_check(), group="What they told you"),
        Col("questionnaire_back", "Questionnaire back", 13, "date",
            validate=date_check(), group="What they told you"),
        Col("notes", "Notes", 28, "wrap", group="What they told you"),

        # ---- hidden plumbing ------------------------------------------------
        month_col("wedding_date", "month", "Wedding month"),
        year_col("wedding_date"),
        Col("season", "Season", 9, "text",
            formula=('=IF({wedding_date}{r}="","",'
                     'IF(MONTH({wedding_date}{r})<=2,"Winter",'
                     'IF(MONTH({wedding_date}{r})<=5,"Spring",'
                     'IF(MONTH({wedding_date}{r})<=8,"Summer",'
                     'IF(MONTH({wedding_date}{r})<=11,"Autumn",'
                     '"Winter")))))'),
            hidden=True),
        Col("month_seq", "Line in the month", 9, "int",
            formula=('=IF({client}{r}="","",IF({earns}{r}<>"Yes","",'
                     'COUNTIFS({month_first}:{month}{r},{month}{r},'
                     '{earns_first}:{earns}{r},"Yes")))'),
            hidden=True),
        Col("month_key", "Month key", 14, "text",
            formula=('=IF({month_seq}{r}="","",'
                     '{month}{r}&"|"&{month_seq}{r})'),
            hidden=True,
            note="Lets Monthly & Annual Reports list the weddings in "
                 "a month without an array formula."),
        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        seq_num_col("client"),
        Col("holds", "Holds the date", 9, "flag",
            formula=('=IF({client}{r}="","",'
                     f'IF({is_holding("{status}{r}")},"Yes","No"))'),
            hidden=True),
        Col("earns", "Counts as revenue", 9, "flag",
            formula=('=IF({client}{r}="","",'
                     f'IF({is_earning("{status}{r}")},"Yes","No"))'),
            hidden=True),
        Col("timeline_lines", "Timeline lines", 9, "int",
            formula=('=IF({client}{r}="",0,'
                     'COUNTIFS([[Wedding Timeline.booking]],{id}{r}))'),
            hidden=True),
        Col("shot_lines", "Shot list lines", 9, "int",
            formula=('=IF({client}{r}="",0,'
                     'COUNTIFS([[Shot List Manager.booking]],'
                     '{id}{r}))'),
            hidden=True),
        Col("upcoming_key", "Upcoming key", 12, "number",
            formula=('=IF({client}{r}="",9999999999,'
                     'IF({holds}{r}<>"Yes",9999999999,'
                     'IF({wed_num}{r}<TodayDate,9999999999,'
                     '{wed_num}{r}*10000+ROW()-4)))'),
            hidden=True),
        Col("upcoming_rank", "Next up", 9, "int",
            formula=('=IF({upcoming_key}{r}>=9999999999,"",'
                     'COUNTIFS({upcoming_key_first}:'
                     '{upcoming_key_last},"<"&{upcoming_key}{r})+1)'),
            hidden=True,
            note="1 = the next wedding in the diary. The Dashboard "
                 "and the Booking Calendar read it."),
        Col("shot", "Wedding happened", 9, "flag",
            formula=('=IF({client}{r}="","",'
                     f'IF({is_shot("{status}{r}")},"Yes","No"))'),
            hidden=True),

        # ---- where it is up to ----------------------------------------------
        Col("days_away", "Days away", 10, "int",
            formula=('=IF({client}{r}="","",IF({wedding_date}{r}="","",'
                     '{wedding_date}{r}-TodayDate))'),
            group="Where it is up to"),
        Col("countdown", "When", 13, "text",
            formula=('=IF({client}{r}="","",IF({days_away}{r}="","",'
                     + countdown_band("{days_away}{r}") + "))"),
            group="Where it is up to"),
        Col("clash", "Date clash", 10, "flag",
            formula=('=IF({client}{r}="","",IF({wedding_date}{r}="","",'
                     'IF({holds}{r}<>"Yes","No",'
                     'IF(COUNTIFS([[Wedding Bookings.wed_num]],'
                     '{wed_num}{r},[[Wedding Bookings.holds]],"Yes")>1,'
                     '"Yes","No"))))'),
            cf=flag_no_bad_cf(),
            note="Two live weddings on the same day. Almost always a "
                 "mistake, and much cheaper to find here than in June.",
            group="Where it is up to"),
        Col("team_clash", "Photographer clash", 13, "flag",
            formula=('=IF({client}{r}="","",IF({photographer}{r}="","",'
                     'IF({holds}{r}<>"Yes","No",'
                     'IF(COUNTIFS([[Wedding Bookings.wed_num]],'
                     '{wed_num}{r},[[Wedding Bookings.photographer]],'
                     '{photographer}{r},[[Wedding Bookings.holds]],'
                     '"Yes")>1,"Yes","No"))))'),
            cf=flag_no_bad_cf(),
            note="The same photographer booked twice on one day.",
            group="Where it is up to"),
        Col("contract_done", "Contract settled", 11, "flag",
            formula=('=IF({client}{r}="","",'
                     'IF(COUNTIFS([[Contracts & Documents.booking]],{id}{r},'
                     '[[Contracts & Documents.doc_type]],"Wedding contract",'
                     '[[Contracts & Documents.is_done]],"Yes")>0,"Yes","No"))'),
            hidden=True, group="Where it is up to"),
        Col("contract_state", "Contract", 13, "status",
            formula=('=IF({client}{r}="","",'
                     'IF(COUNTIFS([[Contracts & Documents.booking]],{id}{r},'
                     '[[Contracts & Documents.doc_type]],"Wedding contract")=0,"Not sent",'
                     'IF({contract_done}{r}="Yes","Signed / filed","Outstanding")))'),
            cf=status_cf(), group="Where it is up to"),
        Col("shots_done", "Shot list", 9, "percent0",
            formula=('=IF({client}{r}="","",'
                     'IF(COUNTIFS([[Shot List Manager.booking]],{id}{r})'
                     '<=0,"",'
                     'COUNTIFS([[Shot List Manager.booking]],{id}{r},'
                     '[[Shot List Manager.done]],"Yes")/'
                     'COUNTIFS([[Shot List Manager.booking]],{id}{r})))'),
            group="Where it is up to"),
        Col("editing_state", "Editing", 14, "status",
            formula=('=IF({client}{r}="","",'
                     'IFERROR(INDEX([[Editing Workflow.stage]],'
                     'MATCH({id}{r},[[Editing Workflow.booking]],0))&"",'
                     'IF({shot}{r}="Yes","Not started","")))'),
            cf=status_cf(), group="Where it is up to"),
        Col("gallery_state", "Gallery", 13, "status",
            formula=('=IF({client}{r}="","",'
                     'IFERROR(INDEX([[Gallery & Delivery.status]],'
                     'MATCH({id}{r},[[Gallery & Delivery.booking]],0))&"",'
                     'IF({shot}{r}="Yes","Not created","")))'),
            cf=status_cf(), group="Where it is up to"),
        Col("deliver_by", "Deliver by", 12, "date",
            formula=('=IF({client}{r}="","",IF({wedding_date}{r}="","",'
                     'IF({shot}{r}<>"Yes","",'
                     '{wedding_date}{r}+DeliveryDays)))'),
            note="Your promised turnaround from Settings, counted from "
                 "the wedding day.",
            group="Where it is up to"),
        Col("delivery_overdue", "Days late", 10, "int",
            formula=('=IF({client}{r}="","",IF({deliver_by}{r}="","",'
                     'IF({gallery_state}{r}="Delivered","",'
                     'MAX(0,TodayDate-{deliver_by}{r}))))'),
            group="Where it is up to"),

        # ---- what it made ----------------------------------------------------
        Col("direct_costs", "Direct costs", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'SUMIFS([[Expense Tracker.profit_cost]],'
                     '[[Expense Tracker.booking]],{id}{r})+'
                     'SUMIFS([[Payments & Invoices.fee]],'
                     '[[Payments & Invoices.booking]],{id}{r}))'),
            group="What it made"),
        Col("team_cost", "Team cost", 11, "money",
            formula=('=IF({client}{r}="",0,'
                     'SUMIFS([[Expense Tracker.profit_cost]],'
                     '[[Expense Tracker.booking]],{id}{r},'
                     '[[Expense Tracker.category]],"Second shooters"))'),
            note="Actual second shooter costs entered on Expense Tracker "
                 "against this Booking ID; part of Direct costs, not extra.",
            group="What it made"),
        Col("editing_cost", "Editing cost", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'SUMIFS([[Expense Tracker.profit_cost]],'
                     '[[Expense Tracker.booking]],{id}{r},'
                     '[[Expense Tracker.category]],"Editing services"))'),
            group="What it made"),
        Col("total_cost", "Total cost", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     '{direct_costs}{r})'),
            group="What it made"),
        Col("profit", "Profit", 12, "money",
            formula=('=IF({client}{r}="",0,'
                     'ROUND({total_value}{r}-{tax}{r}-'
                     '{total_cost}{r},2))'),
            cf=money_cf(),
            note="What the wedding actually made: the booking value "
                 "less the tax you only collected, less everything you "
                 "paid out against it.",
            group="What it made"),
        Col("margin", "Margin", 9, "percent0",
            formula=('=IF({client}{r}="","",IF({total_value}{r}<=0,"",'
                     '{profit}{r}/{total_value}{r}))'),
            group="What it made"),
        Col("profit_hour", "Profit an hour", 12, "money",
            formula=('=IF({client}{r}="","",'
                     'IF({coverage_hours}{r}+EditingHours<=0,"",'
                     'ROUND({profit}{r}/({coverage_hours}{r}+'
                     'EditingHours),2)))'),
            note="Coverage plus your assumed editing hours. The number "
                 "that decides whether a cheap wedding was worth it.",
            group="What it made"),
        rank_desc("profit", guard='{client}{r}=""', header="Profit rank",
                  note="1 = your most profitable wedding."),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({client}{r}="","",'
                'IF({status}{r}="Cancelled","",'
                'IF({wedding_date}{r}="","Add - no wedding date",'
                'IF({clash}{r}="Yes","Duplicate - two weddings this day",'
                'IF({team_clash}{r}="Yes",'
                '"Duplicate - photographer booked twice",'
                'IF({package}{r}="","Add - no package chosen",'
                'IF({contract_state}{r}="Not sent",'
                '"Send - contract not out yet",'
                'IF({days_away}{r}>=0,'
                'IF({contract_done}{r}<>"Yes",'
                '"Chase - contract not signed back",'
                'IF({payment_state}{r}="Overdue",'
                '"Overdue - payment past due",'
                'IF({days_away}{r}<=UpcomingDays,'
                'IF({questionnaire_back}{r}="",'
                '"Action - questionnaire not back",'
                'IF({photographer}{r}="","Add - nobody assigned",'
                '"OK - coming up")),"OK"))),'
                'IF({payment_state}{r}="Overdue",'
                '"Overdue - wedding done and still owing",'
                'IF({delivery_overdue}{r}>0,'
                '"Overdue - gallery past the promised date",'
                'IF({gallery_state}{r}="Delivered","OK",'
                '"Action - in post-production")))))))))))'),
            cf=alert_cf(),
            note="One line per wedding, read in priority order. The "
                 "Dashboard's action list counts this column.",
            group="What it made"),
    ]

    return SheetSpec(
        name=NAME,
        title="Wedding Bookings",
        subtitle=("Every wedding you have taken on - the day, the team, "
                  "the money and where it has got to"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("bookings", cfg),
        help_text=(
            "One row per wedding. The Booking ID in column A is the key "
            "the whole workbook turns on - the timeline, the shot list, "
            "the contract, the invoices, the editing job, the gallery, "
            "the travel and the profit analysis all point at it. Create "
            "the booking here first, then use the ID everywhere else."),
        extra_notes=[
            "'Date clash' and 'Photographer clash' read every other row "
            "on this tab. A double booking found in the spreadsheet is "
            "an awkward phone call; one found by the couple is a "
            "refund and a review.",
            "Coverage hours are worked out from the two time cells, so "
            "overtime bills itself. A finish after midnight is handled.",
            "Profit uses business costs entered once on Expense Tracker "
            "plus payment processing fees. Travel and workflow estimates "
            "are not automatically counted as expenses.",
        ],
    )
