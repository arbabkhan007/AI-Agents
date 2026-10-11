"""`Incidents` - safety, emergency contacts and the incident report register."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check, yes_no
from .common import alert_cf, blank, id_col, status_cf

NAME = "Incidents"

#: The emergency directory block sits above the register.
DIRECTORY_HEADER_ROW = 5          # Excel row of the directory header
REGISTER_HEADER_ROW = 17          # Excel row of the register header

DIRECTORY = [
    ("Business emergency line", "=Biz_Phone", "Answered 07:00 - 21:00"),
    ("Owner / manager", "=Biz_Owner", "Call for any High or Critical event"),
    ("24/7 emergency vet", "24/7 Springfield Pet ER",
     "+1 (555) 100 9111 - open all night"),
    ("Backup emergency vet", "Riverton Vet Clinic",
     "+1 (555) 100 2000 - 08:00 to 18:00"),
    ("Animal poison helpline", "Pet Poison Hotline", "+1 (555) 100 7788"),
    ("Animal control / council", "Springfield Animal Services",
     "+1 (555) 100 4422"),
    ("Insurance claims", "=Biz_Insurer", "=Biz_Policy"),
    ("Backup sitter on call", "Priya Shah", "+1 (555) 772 6690"),
    ("Locksmith / key issues", "Springfield Locks", "+1 (555) 100 6655"),
]


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"IN-"', digits=3, width=9),
        Col("date", "Date", 12, "date", validate=date_check()),
        Col("time", "Time", 9, "time"),
        Col("client", "Client", 20, "text",
            validate=list_from("ClientNames")),
        Col("pet", "Pet", 22, "text", validate=list_from("PetLabels")),
        Col("staff", "Reported by", 15, "text",
            validate=list_from("StaffNames")),
        Col("ref", "Booking / visit ref", 13, "text"),
        Col("type", "Incident type", 16, "text",
            validate=list_from("IncidentTypeList")),
        Col("severity", "Severity", 11, "status",
            validate=list_from("SeverityList"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Critical", "fmt": "bold_bad"},
                {"type": "text", "criteria": "containing", "value": "High",
                 "fmt": "bad"},
                {"type": "text", "criteria": "containing",
                 "value": "Medium", "fmt": "warn"},
                {"type": "text", "criteria": "containing", "value": "Low",
                 "fmt": "good"}]),
        Col("description", "What happened", 44, "wrap"),
        Col("action", "Action taken", 40, "wrap"),
        Col("vet_contacted", "Vet contacted", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("clinic", "Clinic attended", 20, "text"),
        Col("owner_notified", "Owner notified", 10, "flag",
            validate=yes_no(), cf=status_cf()),
        Col("notified_at", "Notified when", 16, "text"),
        Col("follow_up", "Follow-up needed", 10, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("follow_due", "Follow-up due", 12, "date",
            validate=date_check()),
        Col("status", "Status", 13, "status",
            validate=list_from("IncidentStatusList"), cf=status_cf()),
        Col("cost", "Cost incurred", 11, "money",
            validate=number_check(0, 100000)),
        Col("claim", "Insurance claim", 10, "flag", validate=yes_no()),
        Col("days_open", "Days open", 9, "text",
            formula=blank("date",
                          'IF(OR({status}{r}="Resolved",'
                          '{status}{r}="Closed"),"Closed",'
                          'TEXT(TODAY()-{date}{r},"0")&" days")')),
        Col("notes", "Notes & outcome", 34, "wrap"),
        Col("alert", "Action needed", 24, "status",
            formula=blank(
                "date",
                'IF({owner_notified}{r}<>"Yes","Action - notify the owner",'
                'IF(AND({follow_up}{r}="Yes",{follow_due}{r}<>"",'
                '{follow_due}{r}<TODAY(),{status}{r}<>"Resolved",'
                '{status}{r}<>"Closed"),"Overdue follow-up",'
                'IF(OR({status}{r}="Open",{status}{r}="In progress"),'
                '"Open - keep working it","OK")))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Pet Safety, Emergencies & Incident Reports",
        subtitle="Emergency numbers at the top, a dated incident report "
                 "register below. Print a row straight from this tab if "
                 "an owner or insurer asks for it.",
        columns=columns,
        rows=cfg.row_count(NAME),
        header_row=REGISTER_HEADER_ROW,
        tab_color=Palette.bad_text,
        freeze_cols=2,
        freeze_at=3,
        samples=sample(cfg).incidents,
        help_text="Every incident needs: what happened, what you did, who "
                  "you told and when. The alert column chases anything "
                  "still open.",
    )


def decorate(sheet, fmts, cfg: Config) -> None:
    """Write the emergency contact directory above the register."""
    row = DIRECTORY_HEADER_ROW - 2  # 0 based row for the section band
    sheet.section(row, "Emergency contact directory - keep this current",
                  7)
    head = DIRECTORY_HEADER_ROW - 1
    sheet.write(head, 0, "Contact", fmts.chrome("header_left"))
    sheet.merge(head, 1, 2, "Name", fmts.chrome("header"))
    sheet.merge(head, 3, 6, "Number / details", fmts.chrome("header"))
    sheet.write(head, 7, "Notes", fmts.chrome("header"))
    sheet.ws.set_row(head, 20)

    label_fmt = fmts.chrome("label_bold")
    value_fmt = fmts.input("text")
    for i, (label, name, detail) in enumerate(DIRECTORY):
        r = head + 1 + i
        sheet.write(r, 0, label, label_fmt)
        if isinstance(name, str) and name.startswith("="):
            sheet.ws.merge_range(r, 1, r, 2, "", fmts.calc("text"))
            sheet.ws.write_formula(r, 1, name, fmts.calc("text"))
        else:
            sheet.merge(r, 1, 2, name, value_fmt)
        if isinstance(detail, str) and detail.startswith("="):
            sheet.ws.merge_range(r, 3, r, 6, "", fmts.calc("text"))
            sheet.ws.write_formula(r, 3, detail, fmts.calc("text"))
        else:
            sheet.merge(r, 3, 6, detail, value_fmt)
        sheet.ws.write_blank(r, 7, None, value_fmt)
