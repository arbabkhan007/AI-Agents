"""Wedding Timeline - the running order of a wedding day, hour by hour.

Pick the event and the sheet knows roughly when it happens relative to
the ceremony, so a full day's timeline is a column of drop-downs rather
than an hour of arithmetic.  Every default can be overridden, because
no two weddings run the same.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from, number_check, time_check
from .common import (alert_cf, blank, date_num_col, id_col, lookup_booking,
                     lookup_staff, status_cf, yesno, zero)

NAME = "Wedding Timeline"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "TimelinePrefix", digits=cfg.digits("timeline"),
               header="Line ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="Which wedding this line belongs to. Add one row per "
                 "event - the day plan for a wedding is all the rows "
                 "sharing a Booking ID.",
            group="The wedding"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="The wedding"),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The wedding"),
        Col("ceremony", "Ceremony at", 11, "time",
            formula=lookup_booking("ceremony_time", missing=""),
            note="Taken from the booking. Change it there and every "
                 "line of the day moves with it.",
            group="The wedding"),

        # ---- the event --------------------------------------------------------
        Col("event", "Event", 24, "text",
            validate=list_from("TimelineEventList"),
            note="Choosing a standard event fills in a sensible time "
                 "and length. Type over either if this wedding is "
                 "different.",
            group="The event"),
        Col("label", "Your wording", 24, "text",
            note="Optional. What you want printed on the day sheet if "
                 "'Reception entrance' is not what they call it.",
            group="The event"),
        Col("shown", "Shows as", 24, "text",
            formula=blank("booking",
                          'IF({label}{r}<>"",{label}{r},{event}{r})'),
            group="The event"),
        Col("offset_default", "Standard offset", 12, "int",
            formula=zero("booking",
                         'IFERROR(INDEX(TimelineOffsetList,'
                         'MATCH({event}{r},TimelineEventList,0))*1,0)'),
            hidden=True, group="The event"),
        Col("offset", "Minutes from ceremony", 15, "int",
            validate=number_check(-900, 900),
            note="Negative is before the ceremony, positive is after. "
                 "Leave blank to use the standard offset.",
            group="The event"),
        Col("offset_used", "Offset used", 11, "int",
            formula=zero("booking",
                         'IF({offset}{r}="",{offset_default}{r},'
                         '{offset}{r})'),
            hidden=True, group="The event"),
        Col("time_override", "Fixed time", 10, "time",
            validate=time_check(),
            note="For anything with a time of its own - a church slot, "
                 "a sunset, the venue's curfew.",
            group="The event"),
        Col("start", "Starts", 10, "time",
            formula=blank("booking",
                          'IF({time_override}{r}<>"",{time_override}{r},'
                          'IF({ceremony}{r}="","",'
                          'MOD({ceremony}{r}+{offset_used}{r}/1440,1)))'),
            note="Worked out from the ceremony time unless you have "
                 "fixed it.",
            group="The event"),
        Col("duration_default", "Standard length", 12, "int",
            formula=zero("booking",
                         'IFERROR(INDEX(TimelineDurationList,'
                         'MATCH({event}{r},TimelineEventList,0))*1,0)'),
            hidden=True, group="The event"),
        Col("duration", "Minutes", 9, "int",
            validate=number_check(0, 900), group="The event"),
        Col("duration_used", "Length used", 10, "int",
            formula=zero("booking",
                         'IF({duration}{r}="",{duration_default}{r},'
                         '{duration}{r})'),
            hidden=True, group="The event"),
        Col("finish", "Ends", 10, "time",
            formula=blank("booking",
                          'IF({start}{r}="","",'
                          'MOD({start}{r}+{duration_used}{r}/1440,1))'),
            group="The event"),

        # ---- who and where -----------------------------------------------------
        Col("location", "Where", 20, "text", group="Who and where"),
        Col("role", "Who covers it", 16, "text",
            formula=blank("booking",
                          'IFERROR(INDEX(TimelineRoleList,'
                          'MATCH({event}{r},TimelineEventList,0))&"",'
                          '"Lead photographer")'),
            group="Who and where"),
        Col("staff", "Assigned to", 12, "id",
            validate=list_from("StaffList"), group="Who and where"),
        Col("staff_name", "Name", 16, "text",
            formula=lookup_staff("name", key="staff", missing=""),
            group="Who and where"),
        Col("critical", "Must not miss", 11, "flag",
            validate=yesno("The moments there is no second take of - "
                           "the vows, the first kiss, the speeches."),
            group="Who and where"),
        Col("notes", "Notes", 28, "wrap", group="Who and where"),

        # ---- on the day ---------------------------------------------------------
        Col("done", "Done", 8, "flag",
            validate=yesno("Tick it off on the day, or afterwards "
                           "when you are checking nothing was missed."),
            group="On the day"),
        Col("actual", "Actually at", 11, "time",
            validate=time_check(), group="On the day"),
        Col("drift", "Minutes late", 11, "int",
            formula=blank("booking",
                          'IF({actual}{r}="","",IF({start}{r}="","",'
                          'ROUND(MOD({actual}{r}-{start}{r}+0.5,1)'
                          '*1440-720,0)))'),
            note="How far off the plan the day ran. Positive is late. "
                 "Useful next time you are asked how long the family "
                 "photographs really take.",
            group="On the day"),
        Col("status", "Status", 13, "status",
            formula=blank("booking",
                          'IF({done}{r}="Yes","Done",'
                          'IF({wedding_date}{r}="","Planned",'
                          'IF({wedding_date}{r}<TodayDate,"Missed",'
                          '"Planned")))'),
            cf=status_cf(), group="On the day"),

        # ---- plumbing ------------------------------------------------------------
        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        Col("start_num", "Start number", 10, "number",
            formula=zero("booking", 'IF({start}{r}="",0,{start}{r})'),
            hidden=True),
        Col("sort_key", "Sort key", 12, "number",
            formula=zero("booking",
                         'ROUND({start_num}{r}*100000,0)+ROW()-4'),
            hidden=True),
        Col("day_order", "Order", 8, "int",
            formula=blank("booking",
                          'COUNTIFS([[Wedding Timeline.booking]],'
                          '{booking}{r},[[Wedding Timeline.sort_key]],'
                          '"<"&{sort_key}{r})+1'),
            note="Where this line falls in the running order for its "
                 "wedding. The printable day sheet reads it.",
            group="On the day"),
        Col("day_key", "Day key", 14, "text",
            formula=blank("booking",
                          '{booking}{r}&"|"&{day_order}{r}'),
            hidden=True),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({done}{r}="Yes","",'
                'IF({event}{r}="","Add - no event chosen",'
                'IF({start}{r}="","Check - no time worked out",'
                'IF({wedding_date}{r}="","Check - booking has no date",'
                'IF({wedding_date}{r}<TodayDate,'
                'IF({critical}{r}="Yes",'
                '"Check - a must-not-miss moment is unticked",'
                '"Check - not ticked off"),'
                'IF({wedding_date}{r}-TodayDate<=7,'
                'IF({staff}{r}="","Add - nobody assigned yet","OK"),'
                '"OK")))))))'),
            cf=alert_cf(), group="On the day"),
    ]

    return SheetSpec(
        name=NAME,
        title="Wedding Timeline",
        subtitle=("The running order of each wedding day, built from "
                  "the ceremony time"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("timeline", cfg),
        help_text=(
            "Add one row per event and pick the Booking ID it belongs "
            "to. Choosing a standard event sets a time relative to the "
            "ceremony and a sensible length, so a twenty-line day plan "
            "takes a couple of minutes. Override anything that differs "
            "and the rest of the day keeps up."),
        extra_notes=[
            "Change the ceremony time on the booking and every "
            "calculated line on this tab moves with it. This is the "
            "reason to let the sheet work the times out rather than "
            "typing them: ceremony times move, and they move late.",
            "'Must not miss' is for the moments with no second take. "
            "Anything flagged and left unticked after the wedding "
            "comes back as an alert, which is a much better way to "
            "find out than an email from the couple.",
            "'Minutes late' builds up real numbers for how long each "
            "part of a day actually takes. After a dozen weddings you "
            "will know whether your forty-minute family slot has ever "
            "once taken forty minutes.",
        ],
    )
