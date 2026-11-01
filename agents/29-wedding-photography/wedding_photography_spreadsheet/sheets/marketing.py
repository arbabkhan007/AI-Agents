"""Marketing Calendar - what you posted, and whether anybody booked.

Most photography marketing advice stops at "post consistently".  This
tab goes one step further and ties posts to the enquiries and the
weddings that came out of them, so you can tell the difference between
the content that fills your diary and the content that fills an hour.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, blank, date_num_col, id_col, money_cf,
                     month_col, rank_desc, status_cf, year_col, yesno, zero)

NAME = "Marketing Calendar"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("date", "MarketingPrefix", digits=cfg.digits("marketing"),
               header="Post ID"),

        Col("date", "Planned for", 11, "date",
            validate=date_check(), group="The post"),
        Col("platform", "Platform", 14, "text",
            validate=list_from("MarketingPlatformList"),
            group="The post"),
        Col("type", "Type", 14, "text",
            validate=list_from("ContentTypeList"), group="The post"),
        Col("title", "Title or hook", 26, "text", group="The post"),
        Col("content", "What it says", 30, "wrap", group="The post"),
        Col("booking", "Wedding featured", 13, "id",
            validate=list_from("BookingList"),
            note="Which wedding the photographs came from. Check the "
                 "couple were happy for their photographs to be used "
                 "before you post them.",
            group="The post"),
        Col("permission", "Permission given", 13, "flag",
            validate=yesno("The couple agreed their photographs can "
                           "be shown publicly. Worth a line in the "
                           "contract and a tick here."),
            cf=status_cf(), group="The post"),
        Col("status", "Status", 13, "status",
            validate=list_from("ContentStatusList"), cf=status_cf(),
            group="The post"),
        Col("posted_on", "Actually posted", 13, "date",
            validate=date_check(), group="The post"),

        # ---- what it did -----------------------------------------------------
        Col("reach", "Reach", 10, "int",
            validate=number_check(0, 100000000), group="What it did"),
        Col("engagement", "Likes and comments", 14, "int",
            validate=number_check(0, 10000000), group="What it did"),
        Col("saves", "Saves or shares", 13, "int",
            validate=number_check(0, 10000000), group="What it did"),
        Col("clicks", "Clicks through", 12, "int",
            validate=number_check(0, 10000000), group="What it did"),
        Col("engagement_rate", "Engagement rate", 13, "percent0",
            formula=blank("date",
                          'IF({reach}{r}="","",IF({reach}{r}<=0,"",'
                          '(IF({engagement}{r}="",0,'
                          '{engagement}{r})+'
                          'IF({saves}{r}="",0,{saves}{r}))/'
                          '{reach}{r}))'),
            group="What it did"),
        Col("enquiries", "Enquiries from it", 13, "int",
            formula=zero("date",
                         'COUNTIFS([[Lead Tracker.campaign]],'
                         '{id}{r})'),
            note="Counted from the Lead Tracker, where a lead names "
                 "this Post ID as the campaign it came from.",
            group="What it did"),
        Col("manual_enquiries", "Counted by hand", 12, "int",
            validate=number_check(0, 1000),
            note="For enquiries you know came from a post but never "
                 "tagged.",
            group="What it did"),
        Col("all_enquiries", "Enquiries in all", 13, "int",
            formula=zero("date",
                         '{enquiries}{r}+'
                         'IF({manual_enquiries}{r}="",0,'
                         '{manual_enquiries}{r})'),
            group="What it did"),
        Col("bookings", "Weddings booked", 13, "int",
            formula=zero("date",
                         'COUNTIFS([[Lead Tracker.campaign]],{id}{r},'
                         '[[Lead Tracker.is_won]],"Yes")'),
            group="What it did"),
        Col("revenue", "Revenue from it", 13, "money",
            formula=zero("date",
                         'SUMIFS([[Lead Tracker.booked_value]],'
                         '[[Lead Tracker.campaign]],{id}{r},'
                         '[[Lead Tracker.is_won]],"Yes")'),
            cf=money_cf(), group="What it did"),

        # ---- what it cost -----------------------------------------------------
        Col("spend", "Spent on it", 11, "money",
            validate=number_check(0, 1000000),
            note="Advertising, a directory listing, a styled shoot. "
                 "Leave blank for anything that only cost you time.",
            group="What it cost"),
        Col("hours", "Hours it took", 11, "number1",
            validate=number_check(0, 500), group="What it cost"),
        Col("time_cost", "Your time is worth", 13, "money",
            formula=zero("date",
                         'ROUND(IF({hours}{r}="",0,{hours}{r})*'
                         'OwnerHourlyValue,2)'),
            note="Hours times what an hour of yours is worth, from "
                 "Settings. Free marketing is not free.",
            group="What it cost"),
        Col("true_cost", "Real cost", 11, "money",
            formula=zero("date",
                         'ROUND(IF({spend}{r}="",0,{spend}{r})+'
                         '{time_cost}{r},2)'),
            group="What it cost"),
        Col("roi", "Return", 10, "number1",
            formula=blank("date",
                          'IF({true_cost}{r}<=0,"",'
                          'ROUND({revenue}{r}/{true_cost}{r},2))'),
            note="Revenue for every pound or dollar it really cost. "
                 "Under 1 means it lost money once your time is "
                 "counted.",
            group="What it cost"),
        Col("cost_per_enquiry", "Cost an enquiry", 12, "money",
            formula=blank("date",
                          'IF({all_enquiries}{r}<=0,"",'
                          'ROUND({true_cost}{r}/'
                          '{all_enquiries}{r},2))'),
            group="What it cost"),
        rank_desc("revenue", guard='{date}{r}=""', header="Best posts"),
        Col("notes", "Notes", 24, "wrap", group="What it cost"),

        month_col("date"),
        year_col("date"),
        date_num_col("date", "date_num", "Date number"),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({date}{r}="","",'
                'IF({status}{r}="Published",'
                'IF({booking}{r}<>"",'
                'IF({permission}{r}<>"Yes",'
                '"Urgent - posted without recorded permission",'
                'IF({reach}{r}="","Add - no figures logged yet",'
                '"OK")),'
                'IF({reach}{r}="","Add - no figures logged yet","OK")),'
                'IF({status}{r}="Cancelled","",'
                'IF({date}{r}<TodayDate,'
                '"Overdue - planned but never posted",'
                'IF({date}{r}-TodayDate<=3,'
                'IF({content}{r}="","Action - nothing written yet",'
                '"Due - posting within three days"),"OK")))))'),
            cf=alert_cf(), group="What it cost"),
    ]

    return SheetSpec(
        name=NAME,
        title="Marketing Calendar",
        subtitle=("What you plan to post, what you actually posted, "
                  "and which of it brought weddings in"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("marketing", cfg),
        help_text=(
            "Plan posts ahead, then come back and fill in what "
            "happened. Put the Post ID into a lead's campaign column "
            "and the enquiries, the weddings and the revenue find "
            "their own way back here."),
        extra_notes=[
            "The 'Real cost' column counts your time at the hourly "
            "value you set on Settings. Four hours editing a blog "
            "post is not free marketing; it is the most expensive "
            "marketing you do.",
            "Tag leads with the Post ID. It takes two seconds at "
            "enquiry and is the only way to ever know which half of "
            "your marketing works.",
            "Check permission before posting a wedding. Most couples "
            "are delighted; the ones who are not tend to be very not, "
            "and a line in your contract plus a tick in this column "
            "settles it.",
        ],
    )
