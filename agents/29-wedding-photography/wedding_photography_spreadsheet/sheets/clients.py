"""Client CRM - one row per couple, from first enquiry to final gallery.

This is the people half of the join.  A client row carries who they
are, how to reach them and what they said they wanted; everything that
happens to their wedding is read back from the other tabs through the
Booking ID.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, blank, date_num_col, id_col, month_col,
                     money_cf, owing_cf, priority_cf, rank_desc, seq_num_col,
                     status_cf, yesno, zero)

NAME = "Client CRM"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("name", "ClientPrefix", digits=cfg.digits("client"),
               header="Client ID",
               note="Automatic. This is the ID the Lead Tracker and "
                    "Wedding Bookings point back at."),

        # ---- who they are ------------------------------------------------
        Col("name", "Client name", 20, "text",
            note="The person you deal with. One row per couple, not one "
                 "per person.",
            group="The couple"),
        Col("partner", "Partner name", 18, "text", group="The couple"),
        Col("email", "Email", 24, "text", group="The couple"),
        Col("phone", "Phone", 15, "text", group="The couple"),
        Col("country", "Country", 14, "text",
            validate=list_from("CountryList"), group="The couple"),
        Col("status", "Client status", 14, "status",
            validate=list_from("ClientStatusList"),
            cf=status_cf(),
            note="Enquiry while you are still talking, Booked once the "
                 "contract is signed, Complete when the gallery is out "
                 "and the review is in.",
            group="The couple"),
        Col("priority", "Priority", 10, "status",
            validate=list_from("PriorityList"), cf=priority_cf(),
            group="The couple"),

        # ---- the wedding -------------------------------------------------
        Col("wedding_date", "Wedding date", 13, "date",
            validate=date_check(),
            note="Leave blank for an enquiry with no date yet.",
            group="The wedding"),
        Col("venue", "Venue", 22, "text", group="The wedding"),
        Col("venue_city", "Venue town or city", 16, "text",
            group="The wedding"),
        Col("source", "How they found you", 16, "text",
            validate=list_from("LeadSourceList"),
            note="The single most valuable column on this tab - it is "
                 "what tells you where to spend your marketing time.",
            group="The wedding"),
        Col("referred_by", "Referred by", 18, "text",
            note="If a past client or a venue sent them, name them here "
                 "and the Reviews & Referrals tab will credit it.",
            group="The wedding"),
        Col("first_contact", "First contact", 12, "date",
            validate=date_check(), group="The wedding"),

        # ---- what they want ----------------------------------------------
        Col("style", "Wedding style", 15, "text",
            validate=list_from("WeddingStyleList"), group="What they want"),
        Col("photo_style", "Photography style", 17, "text",
            validate=list_from("PhotoStyleList"), group="What they want"),
        Col("delivery_pref", "Delivery preference", 17, "text",
            validate=list_from("DeliveryPreferenceList"),
            group="What they want"),
        Col("notes", "Notes", 34, "wrap",
            note="What they are like, what they care about, what they are "
                 "worried about. Read this before every call.",
            group="What they want"),
        Col("marketing_ok", "Happy to be featured", 12, "flag",
            validate=yesno("Did they agree you may post their photographs?"),
            note="Ask, record the answer, and do not post until it says "
                 "Yes. A signed contract clause is not the same as a "
                 "couple who want their faces on Instagram.",
            group="What they want"),

        # ---- hidden plumbing ---------------------------------------------
        month_col("wedding_date", "wedding_month", "Wedding month"),
        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        seq_num_col("name"),

        # ---- what the rest of the workbook knows --------------------------
        Col("bookings", "Weddings", 9, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.client]],{id}{r})'),
            note="Counted from Wedding Bookings. A couple can have more "
                 "than one - an engagement shoot and the wedding.",
            group="What they are worth"),
        Col("booked_value", "Booked value", 13, "money",
            formula=zero("name",
                         'SUMIFS([[Wedding Bookings.total_value]],'
                         '[[Wedding Bookings.client]],{id}{r})'),
            cf=money_cf(), group="What they are worth"),
        Col("collected", "Collected", 12, "money",
            formula=zero("name",
                         'SUMIFS([[Payments & Invoices.received]],'
                         '[[Payments & Invoices.client]],{id}{r})'),
            cf=money_cf(), group="What they are worth"),
        Col("outstanding", "Still owed", 12, "money",
            formula=blank("name", '{booked_value}{r}-{collected}{r}'),
            cf=owing_cf(),
            note="Booked value less everything received. The number you "
                 "check before the wedding day, not after it.",
            group="What they are worth"),
        Col("next_date", "Next wedding", 13, "date",
            formula=('=IF({name}{r}="","",'
                     'IF(SUMPRODUCT(MAX(([[Wedding Bookings.client]]='
                     '{id}{r})*([[Wedding Bookings.wed_num]]>=TodayDate)*'
                     '[[Wedding Bookings.seq_num]]))<=0,"",'
                     'IFERROR(INDEX([[Wedding Bookings.wedding_date]],'
                     'SUMPRODUCT(MAX(([[Wedding Bookings.client]]={id}{r})*'
                     '([[Wedding Bookings.wed_num]]>=TodayDate)*'
                     '[[Wedding Bookings.seq_num]]))),"")))'),
            note="The next wedding of theirs that has not happened yet.",
            group="What they are worth"),
        Col("days_away", "Days away", 10, "int",
            formula=('=IF({name}{r}="","",IF({next_date}{r}="","",'
                     '{next_date}{r}-TodayDate))'),
            group="What they are worth"),
        Col("delivered", "Gallery delivered", 13, "date",
            formula=('=IF({name}{r}="","",'
                     'IF(SUMPRODUCT(MAX(([[Gallery & Delivery.client]]='
                     '{id}{r})*[[Gallery & Delivery.delivered_num]]))<=0,"",'
                     'SUMPRODUCT(MAX(([[Gallery & Delivery.client]]='
                     '{id}{r})*[[Gallery & Delivery.delivered_num]]))))'),
            group="What they are worth"),
        Col("review", "Review", 11, "text",
            formula=('=IF({name}{r}="","",'
                     'IFERROR(INDEX([[Reviews & Referrals.status]],'
                     'MATCH({id}{r},[[Reviews & Referrals.client]],0))&"",'
                     '"Not requested"))'),
            group="What they are worth"),
        Col("referrals", "Referrals sent", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Client CRM.referred_by]],{name}{r})'),
            note="How many other couples named this one as the reason "
                 "they got in touch.",
            group="What they are worth"),
        rank_desc("booked_value", header="Value rank",
                  note="1 = the couple who has booked the most with you."),

        Col("alert", "What to do", 30, "status",
            formula=('=IF({name}{r}="","",'
                     'IF({status}{r}="Cancelled","",'
                     'IF({name}{r}="","Add - name this client",'
                     'IF({email}{r}="","Missing - no email address",'
                     'IF({status}{r}="Enquiry",'
                     'IF({wedding_date}{r}="","Follow up - no date yet",'
                     '"Follow up - enquiry not yet booked"),'
                     'IF({outstanding}{r}>0.004,'
                     'IF({days_away}{r}<>"",'
                     'IF({days_away}{r}<0,"Overdue - wedding done and '
                     'still owing","Due - balance before the wedding"),'
                     '"Due - balance outstanding"),'
                     'IF({status}{r}="Delivered",'
                     'IF({review}{r}="Received","OK",'
                     '"Send - ask for the review"),"OK")))))))'),
            cf=alert_cf(),
            note="One line per client. Everything on the dashboard's "
                 "action list is counted from this column.",
            group="What they are worth"),
    ]

    return SheetSpec(
        name=NAME,
        title="Client CRM",
        subtitle=("Every couple who has ever got in touch, what they "
                  "booked and what they still owe"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=2,
        samples=sample("clients", cfg),
        help_text=(
            "One row per couple. The Client ID in column A is what the "
            "Lead Tracker and Wedding Bookings point back at, so never "
            "retype a client's name into another tab - point at the ID "
            "and the name, the venue and the date follow."),
        extra_notes=[
            "'How they found you' is the column that pays for this "
            "workbook. Fill it in every single time, even for a walk-in, "
            "and the Dashboard will tell you which channel is actually "
            "worth your Sunday evenings.",
            "Record only what you need. No card numbers, no bank details "
            "and no ID scans belong in a spreadsheet.",
        ],
    )
