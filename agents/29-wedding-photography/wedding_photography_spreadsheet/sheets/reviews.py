"""Reviews & Referrals - the cheapest marketing there is, tracked.

A wedding photographer's next booking usually comes from the last
couple.  This tab records who was asked, who wrote something, where it
went, and which weddings came back out of it.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, booking_client_col, blank, date_num_col, id_col, lookup_booking,
                     money_cf, month_col, rating_cf, score_validation,
                     status_cf, year_col, yesno, zero)

NAME = "Reviews & Referrals"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "ReviewPrefix", digits=cfg.digits("review"),
               header="Review ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"), group="Who"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="Who"),
        booking_client_col(),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="Who"),
        Col("photographer", "Photographer", 12, "id",
            formula=lookup_booking("photographer", missing=""),
            note="Taken from the booking, so the staff tab can show "
                 "an average review per photographer.",
            group="Who"),

        # ---- the ask ----------------------------------------------------------
        Col("asked_on", "Asked on", 11, "date",
            validate=date_check(),
            note="Ask in the fortnight after they first open the "
                 "gallery. Later than that and the answer is usually "
                 "silence.",
            group="The ask"),
        Col("how_asked", "How you asked", 14, "text",
            validate=list_from("ReviewAskMethodList"), group="The ask"),
        Col("reminders", "Reminders", 10, "int",
            validate=number_check(0, 20), group="The ask"),
        Col("status", "Status", 13, "status",
            validate=list_from("ReviewStatusList"), cf=status_cf(),
            group="The ask"),

        # ---- the review --------------------------------------------------------
        Col("received_on", "Received", 11, "date",
            validate=date_check(), group="The review"),
        Col("platform", "Where", 14, "text",
            validate=list_from("ReviewPlatformList"),
            group="The review"),
        Col("rating", "Rating", 9, "rating",
            validate=score_validation(5), cf=rating_cf(),
            group="The review"),
        Col("headline", "Headline", 24, "text", group="The review"),
        Col("quote", "What they said", 34, "wrap",
            note="Paste the useful sentence. This is the one you "
                 "will want for a listing, a website or a post, and "
                 "hunting for it later takes longer than you think.",
            group="The review"),
        Col("can_use", "May you quote it", 13, "flag",
            validate=yesno(), cf=status_cf(), group="The review"),
        Col("used_on", "Used where", 18, "text", group="The review"),
        Col("responded", "You replied", 11, "flag",
            validate=yesno("Reply to every review, including - "
                           "especially - the ones that are not five "
                           "stars."),
            group="The review"),
        Col("days_to_review", "Days to answer", 12, "int",
            formula=blank("booking",
                          'IF({asked_on}{r}="","",'
                          'IF({received_on}{r}="","",'
                          '{received_on}{r}-{asked_on}{r}))'),
            group="The review"),

        # ---- what it led to -------------------------------------------------------
        Col("referrals", "People referred", 12, "int",
            validate=number_check(0, 100),
            note="How many couples they have sent your way.",
            group="What it led to"),
        Col("referred_leads", "Enquiries from them", 14, "int",
            formula=zero("booking",
                         'COUNTIFS([[Lead Tracker.referred_by]],'
                         '{booking}{r})'),
            note="Counted from the Lead Tracker, where an enquiry "
                 "names this Booking ID as the couple who sent them.",
            group="What it led to"),
        Col("referred_bookings", "Weddings from them", 14, "int",
            formula=zero("booking",
                         'COUNTIFS([[Lead Tracker.referred_by]],'
                         '{booking}{r},[[Lead Tracker.is_won]],"Yes")'),
            group="What it led to"),
        Col("referred_value", "Worth to you", 12, "money",
            formula=zero("booking",
                         'SUMIFS([[Lead Tracker.booked_value]],'
                         '[[Lead Tracker.referred_by]],{booking}{r},'
                         '[[Lead Tracker.is_won]],"Yes")'),
            cf=money_cf(),
            note="What the weddings they sent you were worth. It is "
                 "usually the largest number on this tab.",
            group="What it led to"),
        Col("thanked", "Thanked them", 11, "flag",
            validate=yesno("A card, a print, a discount on their "
                           "album. Somebody who sends you a wedding "
                           "should hear from you."),
            group="What it led to"),
        Col("notes", "Notes", 24, "wrap", group="What it led to"),

        month_col("received_on", "month", "Month received"),
        year_col("received_on"),
        date_num_col("received_on", "received_num", "Received number"),
        Col("has_review", "Got one", 9, "flag",
            formula=blank("booking",
                          'IF({received_on}{r}<>"","Yes","No")'),
            hidden=True),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({received_on}{r}="",'
                'IF({asked_on}{r}="","Send - never asked for one",'
                'IF({status}{r}="Declined","",'
                'IF(TodayDate-{asked_on}{r}>ReviewChaseDays,'
                'IF({reminders}{r}>=2,"Check - asked twice, let it go",'
                '"Follow up - asked a while ago, nothing back"),'
                '"OK"))),'
                'IF({rating}{r}<>"",'
                'IF({rating}{r}<=3,'
                'IF({responded}{r}<>"Yes",'
                '"Urgent - poor review with no reply",'
                '"Check - see what went wrong"),'
                'IF({responded}{r}<>"Yes","Action - reply to it",'
                'IF({can_use}{r}="Yes",'
                'IF({used_on}{r}="",'
                '"Action - good quote going unused","OK"),'
                'IF({referred_bookings}{r}>0,'
                'IF({thanked}{r}<>"Yes",'
                '"Send - they sent you a wedding, thank them",'
                '"OK"),"OK")))),'
                '"Add - review received but no rating")))'),
            cf=alert_cf(), group="What it led to"),
    ]

    return SheetSpec(
        name=NAME,
        title="Reviews & Referrals",
        subtitle=("Who you asked, what they wrote, and the weddings "
                  "that came back out of it"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("reviews", cfg),
        help_text=(
            "One row per couple you asked. The gallery tab tells you "
            "when to ask; this one tracks what came back and keeps "
            "the quotes somewhere you can find them. Tag new leads "
            "with the Booking ID of whoever referred them and the "
            "value finds its way back here."),
        extra_notes=[
            "Ask once, remind once, then stop. A third email does "
            "not produce a review, it produces a slightly worse "
            "memory of you.",
            "Reply to every review. A thoughtful reply to a three "
            "star review reads better to the next couple than the "
            "three stars read badly.",
            "The referral column is usually where the real money is. "
            "A couple who sends you two weddings is worth more than "
            "most of your advertising, and costs a card and a print.",
        ],
    )
