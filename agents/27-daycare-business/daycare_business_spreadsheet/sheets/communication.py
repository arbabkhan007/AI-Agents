"""`Parent Communication` - what was said, when, and who owes a reply.

Every setting has the conversation that went wrong because nobody
wrote it down.  This is one row per exchange: who, when, how, what
about, and - the only column that really matters - whether the ball is
still in your court.

The workbook does not send anything.  It records that you did.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, time_check
from .common import (alert_cf, blank, id_col, lookup_child,
                     lookup_family, lookup_staff, month_col, status_cf)

NAME = "Parent Communication"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", "MessagePrefix", digits=4, width=10,
               header="Message ID"),
        Col("date", "Date", 11, "date", validate=date_check()),
        month_col("date"),
        Col("time", "Time", 9, "time", validate=time_check(),
            hidden=True),
        Col("family", "Family", 11, "id",
            validate=list_from("FamilyList")),
        Col("family_name", "Family name", 18, "text",
            formula=lookup_family("family_name")),
        Col("parent", "Spoke to", 20, "text",
            formula=lookup_family("parent1"), hidden=True),
        Col("child", "About child", 11, "id",
            validate=list_from("ChildList"),
            note="Optional - some conversations are about the family, "
                 "not one child."),
        Col("child_name", "Child", 18, "text",
            formula=lookup_child("name", missing="")),
        Col("direction", "In or out", 11, "text",
            validate=list_from("DirectionList"),
            note="Did they contact you, or you them? The ratio tells "
                 "you something about how a term is going."),
        Col("method", "How", 15, "text",
            validate=list_from("ContactMethodList")),
        Col("category", "About", 18, "text",
            validate=list_from("CommCategoryList"), cf=status_cf(),
            note="Pick from the list so that a term's worth of "
                 "conversations can be counted by subject."),
        Col("subject", "Subject", 28, "text"),
        Col("notes", "What was said", 40, "wrap",
            note="Facts and what you agreed. Write it as though "
                 "somebody else will read it back to you in six "
                 "months, because one day somebody will."),
        Col("staff", "Logged by", 10, "id",
            validate=list_from("StaffList")),
        Col("staff_name", "Staff", 16, "text",
            formula=lookup_staff("name"), hidden=True),
        # ------------------------------------------------- follow up ---
        Col("follow_date", "Follow up by", 12, "date",
            validate=date_check()),
        Col("follow_action", "Action agreed", 28, "wrap"),
        Col("status", "Status", 15, "status",
            validate=list_from("CommStatusList"), cf=status_cf(),
            note="'Waiting on us' is the one to filter every "
                 "morning."),
        Col("closed_date", "Closed on", 11, "date",
            validate=date_check(), hidden=True),
        Col("days_open", "Days open", 9, "int",
            formula=blank(
                "date",
                'IF(({status}{r}="Closed")+'
                '({status}{r}="No reply needed")>0,'
                'IF({closed_date}{r}="","",'
                '{closed_date}{r}-{date}{r}),'
                'TodayDate-{date}{r})'),
            cf=[{"type": "cell", "criteria": ">=", "value": 14,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">=", "value": 7,
                 "fmt": "warn"}]),
        Col("overdue", "Follow-up late?", 10, "flag",
            formula=blank(
                "date",
                'IF({follow_date}{r}="","No",'
                'IF(({status}{r}="Closed")+'
                '({status}{r}="No reply needed")>0,"No",'
                'IF({follow_date}{r}<TodayDate,"Yes","No")))'),
            hidden=True),
        Col("meeting", "Meeting booked", 11, "date",
            validate=date_check(), hidden=True,
            note="Parent evenings, settling-in reviews, progress "
                 "chats."),
        Col("alert", "Action", 32, "status",
            formula=blank(
                "date",
                'IF({family}{r}="","Add - which family?",'
                'IF({family_name}{r}="Not in Parent Database",'
                '"Check - family ID not found",'
                'IF({category}{r}="","Add - what was it about?",'
                'IF({overdue}{r}="Yes","Overdue - follow-up date has '
                'passed",'
                'IF({status}{r}="Waiting on us","Follow up - the ball '
                'is with you",'
                'IF(IF({status}{r}="Waiting on parent",'
                '{days_open}{r}>=7,FALSE),'
                '"Chase - a week with no reply",'
                'IF(IF({status}{r}="Open",{days_open}{r}>=14,FALSE),'
                '"Chase - open two weeks",'
                'IF({notes}{r}="","Add - nothing written down",'
                '"OK"))))))))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Parent Communication Log",
        subtitle="Every conversation, what was agreed and whether "
                 "anybody is still waiting on you.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.accent,
        freeze_cols=2,
        samples=sample(cfg).messages,
        help_text="Log the conversation while you remember it. Pick "
                  "the family, say what it was about, and set a "
                  "follow-up date if anything was agreed.",
        extra_notes=[
            "This workbook does not send emails, texts or app "
            "notifications. It is a record that you spoke to "
            "somebody, not a way of speaking to them.",
            "Filter the status to 'Waiting on us' at the start of "
            "each day. That is the whole tab's value in one click.",
            "The open items count on each family's record comes from "
            "here, so a parent with three unanswered questions shows "
            "up on the Parent Database too.",
        ],
    )


def decorate(sheet, fmts, cfg: Config, reg) -> None:
    """Communication summary."""
    spec_ = reg[NAME]
    row = spec_.last_data_row + 1
    last = spec_.last_col_index
    row = sheet.section(row, "Conversations", last)
    sheet.table_head(row, 0, [
        "Logged", "This month", "Incoming", "Outgoing",
        "Open", "Waiting on us", "Waiting on parent",
        "Follow-ups overdue", "Average days open", "Complaints",
        "Compliments"])
    sheet.calc_row(row + 1, 0, [
        '=COUNTIF([[Parent Communication.date]],"<>")',
        '=COUNTIFS([[Parent Communication.month]],ThisMonthKey)',
        '=COUNTIFS([[Parent Communication.direction]],"Incoming")',
        '=COUNTIFS([[Parent Communication.direction]],"Outgoing")',
        '=COUNTIFS([[Parent Communication.status]],"Open")',
        '=COUNTIFS([[Parent Communication.status]],"Waiting on us")',
        '=COUNTIFS([[Parent Communication.status]],'
        '"Waiting on parent")',
        '=COUNTIFS([[Parent Communication.overdue]],"Yes")',
        '=IFERROR(ROUND(AVERAGEIF([[Parent Communication.days_open]],'
        '">=0"),1),0)',
        '=COUNTIFS([[Parent Communication.category]],"Complaint")',
        '=COUNTIFS([[Parent Communication.category]],"Compliment")',
    ], ["int", "int", "int", "int", "int", "int", "int", "int",
        "number1", "int", "int"])
