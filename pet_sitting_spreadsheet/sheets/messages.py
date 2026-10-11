"""`Messages` - client communication, feedback, complaints and follow-ups."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, yes_no
from .common import alert_cf, blank, id_col, month_col, rating_validation, \
    status_cf

NAME = "Messages"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"MSG-"'),
        Col("date", "Date", 12, "date", validate=date_check()),
        Col("client", "Client", 20, "text",
            validate=list_from("ClientNames")),
        Col("type", "Message type", 20, "text",
            validate=list_from("MessageTypeList")),
        Col("channel", "Channel", 14, "text",
            validate=list_from("ChannelList")),
        Col("direction", "Direction", 11, "text",
            validate=list_from("DirectionList")),
        Col("summary", "Summary", 40, "wrap"),
        Col("response", "Reply received", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("rating", "Satisfaction (1-5)", 10, "rating",
            validate=rating_validation(),
            cf=[{"type": "cell", "criteria": ">=", "value": 4,
                 "fmt": "good"},
                {"type": "cell", "criteria": "<=", "value": 2,
                 "fmt": "bad"},
                {"type": "cell", "criteria": "=", "value": 3,
                 "fmt": "warn"}]),
        Col("feedback", "Feedback / review", 40, "wrap"),
        Col("complaint", "Complaint?", 9, "flag", validate=yes_no(),
            cf=[{"type": "text", "criteria": "containing", "value": "Yes",
                 "fmt": "bad"}]),
        Col("issue", "Issue raised", 32, "wrap"),
        Col("resolution", "Resolution status", 15, "status",
            validate=list_from("ResolutionList"), cf=status_cf()),
        Col("resolved_date", "Resolved on", 12, "date",
            validate=date_check()),
        Col("follow_due", "Follow-up due", 12, "date",
            validate=date_check()),
        Col("follow_done", "Follow-up done", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("days_open", "Days open", 9, "int",
            formula='=IF(AND({complaint}{r}="Yes",'
                    '{resolution}{r}<>"Resolved",{date}{r}<>""),'
                    'TODAY()-{date}{r},"")',
            cf=[{"type": "cell", "criteria": ">", "value": 7,
                 "fmt": "bad"}]),
        Col("notes", "Notes", 30, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 26, "status",
            formula=blank(
                "date",
                'IF(AND({complaint}{r}="Yes",{resolution}{r}<>"Resolved"),'
                '"Action - unresolved complaint",'
                'IF(AND({follow_due}{r}<>"",{follow_due}{r}<TODAY(),'
                '{follow_done}{r}<>"Yes"),"Overdue follow-up",'
                'IF(AND({follow_due}{r}<>"",'
                '{follow_due}{r}-TODAY()<=ReminderLeadDays,'
                '{follow_done}{r}<>"Yes"),"Follow-up due soon","OK")))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Client Communication, Feedback & Complaints",
        subtitle="Every confirmation, reminder, update, review and "
                 "complaint in one searchable history.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary_mid,
        freeze_cols=3,
        samples=sample(cfg).messages,
        help_text="Log the message the moment you send it. Satisfaction "
                  "ratings feed the customer-experience numbers on the "
                  "Reports tab.",
    )
