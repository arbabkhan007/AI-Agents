"""Photographer & Staff - who shoots, who edits, and what they cost.

Small studios and solo photographers with a regular second shooter both
need the same thing: a rate on file, a count of who is working which
weekend, and an honest figure for what the team costs against what the
weddings bring in.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec, min_if
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, bar_cf, blank, id_col, money_cf, rank_desc,
                     rating_cf, status_cf, yesno, zero)

NAME = "Photographer & Staff"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("name", "StaffPrefix", digits=cfg.digits("staff"),
               header="Staff ID",
               note="Automatic. Bookings, the timeline and the editing "
                    "workflow all assign work by this ID."),

        Col("name", "Name", 20, "id", group="Who"),
        Col("role", "Role", 15, "text",
            validate=list_from("StaffRoleList"), group="Who"),
        Col("status", "Status", 12, "status",
            validate=list_from("StaffStatusList"), cf=status_cf(),
            group="Who"),
        Col("type", "Employment", 13, "text",
            validate=list_from("StaffTypeList"),
            note="Whether somebody is an employee or a contractor is a "
                 "legal question in your country, not a spreadsheet "
                 "one. This column records your answer, it does not "
                 "decide it.",
            group="Who"),
        Col("phone", "Phone", 15, "text", group="Who"),
        Col("email", "Email", 24, "text", group="Who"),
        Col("started", "Started", 11, "date",
            validate=date_check(), group="Who"),

        # ---- what they cost -------------------------------------------------
        Col("day_rate", "Wedding day rate", 13, "money",
            validate=number_check(0, 100000),
            note="What you pay them for a full wedding. Leave blank "
                 "for yourself - your pay is the profit.",
            group="What they cost"),
        Col("hour_rate", "Hourly rate", 11, "money",
            validate=number_check(0, 10000), group="What they cost"),
        Col("edit_rate", "Editing rate", 11, "money",
            validate=number_check(0, 10000), group="What they cost"),
        Col("is_owner", "Owner", 8, "flag",
            validate=yesno("Yes for you. Owner time is not counted as "
                           "a cost, because paying yourself a wage out "
                           "of your own profit counts it twice."),
            group="What they cost"),

        # ---- what they can do -----------------------------------------------
        Col("can_lead", "Can lead", 9, "flag",
            validate=yesno(), group="What they can do"),
        Col("can_second", "Can second", 10, "flag",
            validate=yesno(), group="What they can do"),
        Col("can_edit", "Can edit", 9, "flag",
            validate=yesno(), group="What they can do"),
        Col("specialism", "Specialism", 18, "text",
            group="What they can do"),
        Col("kit", "Own kit", 20, "wrap", group="What they can do"),
        Col("insured", "Insured", 9, "flag",
            validate=yesno("Their own public liability cover, if they "
                           "carry it. Yours is on the Expense Tracker."),
            group="What they can do"),
        Col("insurance_expiry", "Insurance to", 12, "date",
            validate=date_check(), group="What they can do"),

        # ---- how much they work ---------------------------------------------
        Col("leading", "Leading", 9, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.photographer]],'
                         '{id}{r},[[Wedding Bookings.holds]],"Yes")'),
            group="How much they work"),
        Col("seconding", "Seconding", 10, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.second]],{id}{r},'
                         '[[Wedding Bookings.holds]],"Yes")'),
            group="How much they work"),
        Col("weddings", "Weddings", 9, "int",
            formula=zero("name", '{leading}{r}+{seconding}{r}'),
            group="How much they work"),
        Col("upcoming", "Still to come", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.photographer]],'
                         '{id}{r},[[Wedding Bookings.holds]],"Yes",'
                         '[[Wedding Bookings.wed_num]],">="&TodayDate)+'
                         'COUNTIFS([[Wedding Bookings.second]],{id}{r},'
                         '[[Wedding Bookings.holds]],"Yes",'
                         '[[Wedding Bookings.wed_num]],">="&TodayDate)'),
            group="How much they work"),
        Col("next_num", "Next wedding number", 12, "number",
            formula=zero("name", min_if(
                "[[Wedding Bookings.wed_num]]",
                '([[Wedding Bookings.photographer]]={id}{r})'
                '+([[Wedding Bookings.second]]={id}{r})>0',
                '[[Wedding Bookings.holds]]="Yes"',
                '[[Wedding Bookings.wed_num]]>=TodayDate')),
            hidden=True, group="How much they work"),
        Col("next_wedding", "Next wedding", 12, "date",
            formula=blank("name",
                          'IF({next_num}{r}>=2958465,"",'
                          'IF({next_num}{r}<=0,"",{next_num}{r}))'),
            group="How much they work"),
        Col("shoot_hours", "Hours on the day", 13, "number1",
            formula=zero("name",
                         'SUMIFS([[Wedding Bookings.coverage_hours]],'
                         '[[Wedding Bookings.photographer]],{id}{r},'
                         '[[Wedding Bookings.holds]],"Yes")'),
            group="How much they work"),
        Col("edit_jobs", "Editing jobs", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Editing Workflow.editor]],'
                         '{id}{r})'),
            group="How much they work"),
        Col("edit_hours", "Editing hours", 12, "number1",
            formula=zero("name",
                         'SUMIFS([[Editing Workflow.hours]],'
                         '[[Editing Workflow.editor]],{id}{r})'),
            group="How much they work"),

        # ---- what it comes to -------------------------------------------------
        Col("shoot_pay", "Shoot pay", 12, "money",
            formula=zero("name",
                         'IF({is_owner}{r}="Yes",0,'
                         'ROUND({weddings}{r}*'
                         'IF({day_rate}{r}="",0,{day_rate}{r}),2))'),
            group="What it comes to"),
        Col("edit_pay", "Editing pay", 11, "money",
            formula=zero("name",
                         'IF({is_owner}{r}="Yes",0,'
                         'ROUND({edit_hours}{r}*'
                         'IF({edit_rate}{r}="",0,{edit_rate}{r}),2))'),
            group="What it comes to"),
        Col("total_pay", "Total pay", 12, "money",
            formula=zero("name", '{shoot_pay}{r}+{edit_pay}{r}'),
            cf=money_cf(), group="What it comes to"),
        Col("revenue_touched", "Revenue worked on", 14, "money",
            formula=zero("name",
                         'SUMIFS([[Wedding Bookings.total_value]],'
                         '[[Wedding Bookings.photographer]],{id}{r},'
                         '[[Wedding Bookings.earns]],"Yes")'),
            cf=money_cf(),
            note="Only weddings they led. A second shooter has not "
                 "brought the booking in.",
            group="What it comes to"),
        Col("pay_ratio", "Pay as share", 11, "percent0",
            formula=blank("name",
                          'IF({revenue_touched}{r}<=0,"",'
                          '{total_pay}{r}/{revenue_touched}{r})'),
            cf=bar_cf(), group="What it comes to"),
        rank_desc("weddings", header="Busiest"),

        # ---- how they are doing -----------------------------------------------
        Col("rating", "Average review", 11, "rating",
            formula=blank("name",
                          'IFERROR(AVERAGEIFS('
                          '[[Reviews & Referrals.rating]],'
                          '[[Reviews & Referrals.photographer]],'
                          '{id}{r}),"")'),
            cf=rating_cf(), group="How they are doing"),
        Col("late_jobs", "Late deliveries", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Editing Workflow.editor]],{id}{r},'
                         '[[Editing Workflow.late]],"Yes")'),
            group="How they are doing"),
        Col("notes", "Notes", 28, "wrap", group="How they are doing"),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({name}{r}="","",'
                'IF({status}{r}<>"Active","",'
                'IF({insured}{r}="Yes",'
                'IF({insurance_expiry}{r}<>"",'
                'IF({insurance_expiry}{r}<TodayDate,'
                '"Expired - their insurance has run out",'
                'IF({insurance_expiry}{r}-TodayDate<=30,'
                '"Due - insurance expires within a month","OK")),'
                '"Check - insured but no expiry date"),'
                'IF({late_jobs}{r}>=2,'
                '"Check - more than one late delivery",'
                'IF({day_rate}{r}="",'
                'IF({is_owner}{r}="Yes","OK",'
                '"Add - no day rate on file"),"OK")))))'),
            cf=alert_cf(), group="How they are doing"),
    ]

    return SheetSpec(
        name=NAME,
        title="Photographer & Staff",
        subtitle=("Everybody who shoots or edits for you, what they "
                  "cost and how much they are working"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=2,
        samples=sample("staff", cfg),
        help_text=(
            "Add yourself as the first row with 'Owner' set to Yes. "
            "Bookings pick a lead photographer and an optional second "
            "shooter from this list, the editing workflow picks an "
            "editor, and the pay columns add up what the team costs "
            "against the weddings they worked on."),
        extra_notes=[
            "Owner rows are costed at zero on purpose. Your time is "
            "paid out of the profit, and counting a notional wage as a "
            "cost as well would understate every wedding twice over.",
            "Whether somebody is an employee or a self-employed "
            "contractor is a legal test in your country, and getting "
            "it wrong is expensive. The 'Employment' column records "
            "what you have decided; it does not decide it for you.",
        ],
    )
