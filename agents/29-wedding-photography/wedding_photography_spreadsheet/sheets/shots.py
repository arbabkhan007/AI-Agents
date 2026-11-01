"""Shot List Manager - the list you work from, grouped and ticked off.

The family-group section is the one that saves a wedding.  Written out
by name beforehand it takes twenty minutes; improvised on the day with
a hundred guests watching, it takes an hour and somebody's grandmother
gets left out of it.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from, time_check
from .common import (alert_cf, blank, date_num_col, id_col, lookup_booking,
                     priority_cf, status_cf, yesno)

NAME = "Shot List Manager"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "ShotPrefix", digits=cfg.digits("shot"),
               header="Shot ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="The wedding this shot belongs to. Copy a standard "
                 "list down, change the Booking ID and you have a shot "
                 "list for the next wedding.",
            group="The wedding"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="The wedding"),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The wedding"),

        # ---- the shot ----------------------------------------------------------
        Col("group_name", "Group", 16, "text",
            validate=list_from("ShotGroupList"),
            note="Details, preparation, couple, family, ceremony, "
                 "reception. Grouping is what makes the list usable "
                 "while you are holding a camera.",
            group="The shot"),
        Col("shot", "Shot", 32, "text",
            note="Be specific. 'Family' is not a shot; 'Bride with "
                 "her mother and both sisters' is.",
            group="The shot"),
        Col("people", "Who is in it", 26, "wrap",
            note="Names, not relationships. On the day you will be "
                 "calling these out across a room.",
            group="The shot"),
        Col("priority", "Priority", 11, "text",
            validate=list_from("PriorityList"), cf=priority_cf(),
            group="The shot"),
        Col("must_have", "Must have", 10, "flag",
            validate=yesno("The shots the couple specifically asked "
                           "for. These are chased separately."),
            group="The shot"),
        Col("requested_by", "Asked for by", 14, "text",
            validate=list_from("RequestSourceList"),
            note="Whether this came from the couple, a parent or your "
                 "own standard list. Useful when there are forty "
                 "family groups and somebody has to be told no.",
            group="The shot"),
        Col("when", "When in the day", 15, "text",
            validate=list_from("ShotWhenList"), group="The shot"),
        Col("location", "Where", 18, "text", group="The shot"),
        Col("notes", "Notes", 26, "wrap", group="The shot"),

        # ---- on the day ----------------------------------------------------------
        Col("done", "Taken", 8, "flag",
            validate=yesno(), cf=status_cf(), group="On the day"),
        Col("taken_at", "Taken at", 10, "time",
            validate=time_check(), group="On the day"),
        Col("skipped", "Skipped", 9, "flag",
            validate=yesno("Yes when it could not happen - the light "
                           "went, the person left, the rain won. Stops "
                           "it being chased as missing."),
            group="On the day"),
        Col("skip_reason", "Why not", 22, "wrap", group="On the day"),
        Col("delivered", "In the gallery", 11, "flag",
            validate=yesno(), group="On the day"),

        # ---- plumbing -------------------------------------------------------------
        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        Col("open", "Outstanding", 9, "flag",
            formula=blank("booking",
                          'IF({done}{r}="Yes","No",'
                          'IF({skipped}{r}="Yes","No","Yes"))'),
            hidden=True),
        Col("print_flag", "On the printed list", 9, "int",
            formula=('=IF({booking}{r}="",0,'
                     'IF({group_name}{r}="Family",1,'
                     'IF({must_have}{r}="Yes",1,0)))'),
            hidden=True),
        Col("print_seq", "Printed line", 9, "int",
            formula=('=IF({booking}{r}="","",'
                     'IF({print_flag}{r}=0,"",'
                     'COUNTIFS({booking_first}:{booking}{r},'
                     '{booking}{r},{print_flag_first}:'
                     '{print_flag}{r},1)))'),
            hidden=True),
        Col("print_key", "Printed key", 14, "text",
            formula=('=IF({print_seq}{r}="","",'
                     '{booking}{r}&"|"&{print_seq}{r})'),
            hidden=True,
            note="Family groups and must-have shots, numbered within "
                 "each wedding. The Client Questionnaire prints them "
                 "in this order."),
        Col("group_total", "In this group", 11, "int",
            formula=blank("booking",
                          'COUNTIFS([[Shot List Manager.booking]],'
                          '{booking}{r},'
                          '[[Shot List Manager.group_name]],'
                          '{group_name}{r})'),
            group="How it is going"),
        Col("group_done", "Group taken", 11, "int",
            formula=blank("booking",
                          'COUNTIFS([[Shot List Manager.booking]],'
                          '{booking}{r},'
                          '[[Shot List Manager.group_name]],'
                          '{group_name}{r},'
                          '[[Shot List Manager.done]],"Yes")'),
            group="How it is going"),
        Col("group_pct", "Group complete", 12, "percent0",
            formula=blank("booking",
                          'IF({group_total}{r}<=0,"",'
                          '{group_done}{r}/{group_total}{r})'),
            group="How it is going"),
        Col("wedding_pct", "Wedding complete", 13, "percent0",
            formula=blank("booking",
                          'IF(COUNTIFS([[Shot List Manager.booking]],'
                          '{booking}{r})<=0,"",'
                          'COUNTIFS([[Shot List Manager.booking]],'
                          '{booking}{r},[[Shot List Manager.done]],'
                          '"Yes")/'
                          'COUNTIFS([[Shot List Manager.booking]],'
                          '{booking}{r}))'),
            group="How it is going"),
        Col("status", "Status", 12, "status",
            formula=blank("booking",
                          'IF({done}{r}="Yes","Taken",'
                          'IF({skipped}{r}="Yes","Skipped",'
                          'IF({wedding_date}{r}="","To do",'
                          'IF({wedding_date}{r}<TodayDate,"Missed",'
                          '"To do"))))'),
            cf=status_cf(), group="How it is going"),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({shot}{r}="","Add - no shot described",'
                'IF({done}{r}="Yes",'
                'IF({delivered}{r}="No",'
                '"Check - taken but not in the gallery","OK"),'
                'IF({skipped}{r}="Yes",'
                'IF({skip_reason}{r}="","Add - say why it was missed",'
                '"OK"),'
                'IF({wedding_date}{r}="","OK",'
                'IF({wedding_date}{r}<TodayDate,'
                'IF({must_have}{r}="Yes",'
                '"Urgent - a must-have shot was never taken",'
                '"Check - not taken and not skipped"),'
                'IF({wedding_date}{r}-TodayDate<=7,'
                'IF({people}{r}="",'
                'IF({group_name}{r}="Family",'
                '"Add - family shot with no names","OK"),"OK"),'
                '"OK")))))))'),
            cf=alert_cf(), group="How it is going"),
    ]

    return SheetSpec(
        name=NAME,
        title="Shot List Manager",
        subtitle=("Every photograph you have promised, grouped the way "
                  "you will shoot it and ticked off as you go"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("shots", cfg),
        help_text=(
            "One row per shot, tagged with the Booking ID. Build a "
            "standard list once, then copy it down and change the "
            "Booking ID for each new wedding. The booking row shows "
            "how much of the list is done, and anything flagged as a "
            "must-have but never taken comes back as an alert."),
        extra_notes=[
            "Write family groups out by name. A list that says "
            "'Bride's family' turns into fifteen minutes of asking who "
            "else should be in it while two hundred guests wait for "
            "their dinner.",
            "'Asked for by' is worth filling in. When the groom's "
            "mother produces a list of nineteen extra groups on the "
            "morning, it helps to know which of the forty you already "
            "have came from the couple themselves.",
            "'Skipped' with a reason is not a failure - the light "
            "goes, people leave, it rains. Recording it stops the shot "
            "being chased and gives you something to say if you are "
            "ever asked about it.",
        ],
    )
