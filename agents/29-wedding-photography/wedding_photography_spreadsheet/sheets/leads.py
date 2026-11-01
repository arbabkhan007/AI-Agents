"""Lead Tracker - every enquiry, and what happened to it.

A lead is not a client.  Most enquiries never book, and the ones that
do take weeks of back and forth to get there.  This tab exists to make
sure nobody is left waiting for a reply, and to answer the only
marketing question that matters: of the people who asked, how many
said yes, and where did they come from?
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, date_num_col, id_col, is_open_lead,
                     is_won_lead, money_cf, month_col, priority_cf,
                     seq_num_col, status_cf)

NAME = "Lead Tracker"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("name", "LeadPrefix", digits=cfg.digits("lead"),
               header="Lead ID"),

        # ---- the enquiry --------------------------------------------------
        Col("name", "Enquiry name", 19, "text",
            note="Whoever wrote to you. Add them to the Client CRM once "
                 "they are worth keeping.",
            group="The enquiry"),
        Col("partner", "Partner name", 16, "text", group="The enquiry"),
        Col("email", "Email", 23, "text", group="The enquiry"),
        Col("phone", "Phone", 14, "text", group="The enquiry"),
        Col("client", "Client ID", 11, "id",
            validate=list_from("ClientList"),
            note="Link the enquiry to a Client CRM row once you have "
                 "created one. Leave blank for a cold enquiry.",
            group="The enquiry"),
        Col("enquiry_date", "Enquiry date", 12, "date",
            validate=date_check(), group="The enquiry"),
        Col("source", "Lead source", 15, "text",
            validate=list_from("LeadSourceList"),
            note="Where this enquiry actually came from. The marketing "
                 "dashboard is only as honest as this column.",
            group="The enquiry"),
        Col("campaign", "Came from post", 13, "id",
            validate=list_from("CampaignList"),
            note="The Post ID from the Marketing Calendar, when you "
                 "know which post they saw. Two seconds here is the "
                 "only way to ever learn which marketing works.",
            group="The enquiry"),
        Col("referred_by", "Referred by", 12, "id",
            validate=list_from("BookingList"),
            note="The Booking ID of the couple who sent them. Using "
                 "the ID rather than a name is what lets Reviews & "
                 "Referrals add up what a past couple has been worth.",
            group="The enquiry"),
        Col("referrer_name", "Referrer", 18, "text",
            formula=('=IF({referred_by}{r}="","",'
                     'IFERROR(INDEX([[Wedding Bookings.client_name]],'
                     'MATCH({referred_by}{r},'
                     '[[Wedding Bookings.id]],0))&"",""))'),
            group="The enquiry"),

        # ---- what they are asking for -------------------------------------
        Col("wedding_date", "Wedding date", 12, "date",
            validate=date_check(), group="What they want"),
        Col("venue", "Venue", 20, "text", group="What they want"),
        Col("guests", "Guests", 8, "int",
            validate=number_check(0, 2000), group="What they want"),
        Col("package", "Package asked about", 17, "text",
            validate=list_from("PackageList"), group="What they want"),
        Col("budget", "Their budget", 12, "money",
            validate=number_check(0, 1000000),
            note="What they said, not what you hope. An honest number "
                 "here makes the conversion rate mean something.",
            group="What they want"),

        # ---- where it got to ----------------------------------------------
        Col("status", "Lead status", 17, "status",
            validate=list_from("LeadStatusList"), cf=status_cf(),
            note="New until you reply. Booked only once the contract is "
                 "signed and the deposit has cleared.",
            group="Where it got to"),
        Col("priority", "Priority", 9, "status",
            validate=list_from("PriorityList"), cf=priority_cf(),
            group="Where it got to"),
        Col("replied", "First replied", 12, "date",
            validate=date_check(),
            note="The date you first answered. Fill this in - the "
                 "response-time figure on the dashboard is read from it.",
            group="Where it got to"),
        Col("consultation", "Consultation", 12, "date",
            validate=date_check(), group="Where it got to"),
        Col("proposal_sent", "Proposal sent", 12, "date",
            validate=date_check(), group="Where it got to"),
        Col("decision_date", "Booked or lost on", 13, "date",
            validate=date_check(), group="Where it got to"),
        Col("lost_reason", "Why it was lost", 22, "text",
            note="Price, date gone, no reply, went with a friend. Six "
                 "months of this column is worth more than any course.",
            group="Where it got to"),
        Col("follow_up", "Follow up on", 12, "date",
            validate=date_check(),
            note="The next time you intend to chase. Leave it blank and "
                 "the workbook will work one out for you.",
            group="Where it got to"),
        Col("notes", "Notes", 30, "wrap", group="Where it got to"),

        # ---- hidden plumbing ----------------------------------------------
        month_col("enquiry_date", "month", "Enquiry month"),
        date_num_col("enquiry_date", "enq_num", "Enquiry date number"),
        date_num_col("follow_up", "follow_num", "Follow up number"),
        seq_num_col("name"),

        # ---- what the workbook works out ----------------------------------
        Col("is_open", "Still live", 9, "flag",
            formula=('=IF({name}{r}="","",'
                     f'IF({is_open_lead("{status}{r}")},"Yes","No"))'),
            hidden=True, group="How it is going"),
        Col("is_won", "Booked", 9, "flag",
            formula=('=IF({name}{r}="","",'
                     f'IF({is_won_lead("{status}{r}")},"Yes","No"))'),
            hidden=True, group="How it is going"),
        Col("response_hours", "Days to reply", 11, "number1",
            formula=('=IF({name}{r}="","",IF({enquiry_date}{r}="","",'
                     'IF({replied}{r}="","",'
                     'ROUND({replied}{r}-{enquiry_date}{r},1))))'),
            note="Couples book the photographer who answered first far "
                 "more often than the one who answered best.",
            group="How it is going"),
        Col("age_days", "Days old", 9, "int",
            formula=('=IF({name}{r}="","",IF({enquiry_date}{r}="","",'
                     'IF({decision_date}{r}<>"",'
                     '{decision_date}{r}-{enquiry_date}{r},'
                     'TodayDate-{enquiry_date}{r})))'),
            group="How it is going"),
        Col("silent_days", "Days since contact", 13, "int",
            formula=('=IF({name}{r}="","",'
                     'IF({is_open}{r}<>"Yes","",'
                     'TodayDate-MAX({enquiry_date}{r}+0,{replied}{r}+0,'
                     '{consultation}{r}+0,{proposal_sent}{r}+0)))'),
            note="How long this couple has been waiting to hear from "
                 "you. Filter rather than sorting or moving rows.",
            group="How it is going"),
        Col("chase_on", "Chase by", 12, "date",
            formula=('=IF({name}{r}="","",IF({is_open}{r}<>"Yes","",'
                     'IF({follow_up}{r}<>"",{follow_up}{r},'
                     'IF({proposal_sent}{r}<>"",'
                     '{proposal_sent}{r}+ConsultationChaseDays,'
                     'IF({replied}{r}<>"",{replied}{r}+LeadChaseDays,'
                     'IF({enquiry_date}{r}="","",'
                     '{enquiry_date}{r}+LeadChaseDays))))))'),
            note="Your own follow-up date if you set one, otherwise the "
                 "chase windows from Settings.",
            group="How it is going"),
        Col("overdue", "Days overdue", 11, "int",
            formula=('=IF({name}{r}="","",IF({chase_on}{r}="","",'
                     'MAX(0,TodayDate-{chase_on}{r})))'),
            group="How it is going"),
        Col("lead_time", "Months to wedding", 13, "number1",
            formula=('=IF({name}{r}="","",IF({wedding_date}{r}="","",'
                     'ROUND(({wedding_date}{r}-{enquiry_date}{r})/30.44,'
                     '1)))'),
            group="How it is going"),
        Col("booked_value", "Booked for", 12, "money",
            formula=('=IF({name}{r}="","",IF({client}{r}="","",'
                     'IF({is_won}{r}<>"Yes","",'
                     'SUMIFS([[Wedding Bookings.total_value]],'
                     '[[Wedding Bookings.client]],{client}{r}))))'),
            cf=money_cf(),
            note="What this enquiry turned into, read back from Wedding "
                 "Bookings through the Client ID.",
            group="How it is going"),
        Col("value_gap", "Against their budget", 15, "money",
            formula=('=IF({name}{r}="","",IF({booked_value}{r}="","",'
                     'IF({budget}{r}<=0,"",'
                     '{booked_value}{r}-{budget}{r})))'),
            note="Positive means they spent more than they first said "
                 "they would, which is what a good proposal does.",
            group="How it is going"),

        Col("alert", "What to do", 30, "status",
            formula=(
                     '=IF({name}{r}="","",IF({is_open}{r}<>"Yes",'
                     'IF({is_won}{r}="Yes",IF({client}{r}="",'
                     '"Add - create the client record","OK"),"OK"),'
                     'IF({enquiry_date}{r}="","Add - date the enquiry",'
                     'IF({replied}{r}="",'
                     'IF(TodayDate-{enquiry_date}{r}>=LeadChaseDays,'
                     '"Urgent - never replied to","Action - reply today"),'
                     'IF({overdue}{r}>14,"Overdue - chase or mark it lost",'
                     'IF({overdue}{r}>0,"Follow up - overdue chase",'
                     'IF({status}{r}="Proposal sent",'
                     '"Follow up - proposal out, no answer",'
                     'IF({wedding_date}{r}<>"",'
                     'IF({wedding_date}{r}-TodayDate<30,'
                     '"Urgent - wedding is close and not booked","OK"),'
                     '"OK"))))))))'),
            cf=alert_cf(), group="How it is going"),
    ]

    return SheetSpec(
        name=NAME,
        title="Lead Tracker",
        subtitle=("Every enquiry, how fast you answered it and whether "
                  "it turned into a wedding"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=2,
        samples=sample("leads", cfg),
        help_text=(
            "One row per enquiry, including the ones that go nowhere - "
            "especially those. A conversion rate calculated only from "
            "the couples who booked is not a conversion rate. Set the "
            "status honestly and the Dashboard will tell you where your "
            "weddings really come from."),
        extra_notes=[
            "Check 'Days since contact' on a Monday "
            "morning. Anything over your chase window is a couple who "
            "is, right now, reading somebody else's reply.",
            "'Why it was lost' takes ten seconds to fill in and is the "
            "most useful thing on the tab after a year. Price and "
            "'date already gone' are very different problems.",
        ],
    )
