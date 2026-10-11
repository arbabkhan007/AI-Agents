"""`Reminders` - the alert centre plus a custom task list."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, Registry, SheetSpec, quote_sheet
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import alert_cf, blank, id_col, status_cf

NAME = "Reminders"

ALERT_HEADER_ROW = 6      # Excel row of the alert panel header
TASK_HEADER_ROW = 38      # Excel row of the task list header
LAST_COL = 9

#: (alert, count formula, value formula, what to do, jump-to sheet)
ALERTS = [
    ("Bookings in the next 7 days",
     '=COUNTIFS([[Bookings.date]],">="&TODAY(),[[Bookings.date]],'
     '"<="&TODAY()+7,[[Bookings.status]],"<>Cancelled")',
     '=SUMIFS([[Bookings.total]],[[Bookings.date]],">="&TODAY(),'
     '[[Bookings.date]],"<="&TODAY()+7,[[Bookings.status]],"<>Cancelled")',
     "Confirm the schedule and send reminders", "Bookings"),
    ("Unconfirmed bookings",
     '=COUNTIFS([[Bookings.date]],">="&TODAY(),[[Bookings.confirm_sent]],'
     '"<>Yes",[[Bookings.status]],"<>Cancelled")', "",
     "Send a confirmation message today", "Bookings"),
    ("Booking conflicts / double bookings",
     '=COUNTIF([[Bookings.conflict]],"Conflict*")', "",
     "Two jobs overlap for the same carer", "Bookings"),
    ("Bookings waiting on a visit log",
     '=COUNTIFS([[Bookings.status]],"Completed",'
     '[[Bookings.visit_logged]],"No")', "",
     "Log the visit so the client has a record", "Visit Log"),
    ("Missed visits",
     '=COUNTIF([[Visit Log.status]],"Missed")', "",
     "Call the client and agree what happens next", "Visit Log"),
    ("Visits with no client update sent",
     '=COUNTIFS([[Visit Log.status]],"Completed",'
     '[[Visit Log.update_sent]],"<>Yes")', "",
     "Send the photo and summary", "Visit Log"),
    ("Overdue invoices",
     '=COUNTIF([[Invoices.pay_status]],"Overdue")'
     '+COUNTIF([[Invoices.pay_status]],"Overdue - part paid")',
     '=SUMIFS([[Invoices.balance]],[[Invoices.pay_status]],"Overdue")'
     '+SUMIFS([[Invoices.balance]],[[Invoices.pay_status]],'
     '"Overdue - part paid")',
     "Send a payment reminder with the late fee", "Invoices"),
    ("Invoices due within the reminder window",
     '=COUNTIFS([[Invoices.balance]],">0.004",[[Invoices.due]],'
     '">="&TODAY(),[[Invoices.due]],"<="&TODAY()+ReminderLeadDays)',
     '=SUMIFS([[Invoices.balance]],[[Invoices.balance]],">0.004",'
     '[[Invoices.due]],">="&TODAY(),[[Invoices.due]],'
     '"<="&TODAY()+ReminderLeadDays)',
     "A friendly nudge before the due date", "Invoices"),
    ("Draft invoices not sent",
     '=COUNTIF([[Invoices.status]],"Draft")',
     '=SUMIFS([[Invoices.total]],[[Invoices.status]],"Draft")',
     "Finish and send them - this is unbilled work", "Invoices"),
    ("Payments not reconciled",
     '=COUNTIF([[Payments.reconciled]],"<>Yes")', "",
     "Match them against your bank statement", "Payments"),
    ("Vaccinations expired",
     '=COUNTIF([[Pets.vacc_status]],"Expired")', "",
     "Ask the owner for an updated certificate", "Pets"),
    ("Vaccinations due soon",
     '=COUNTIF([[Pets.vacc_status]],"Due in*")', "",
     "Remind the owner before the booking", "Pets"),
    ("Medication doses missed",
     '=COUNTIF([[Health Log.status]],"Missed")', "",
     "Tell the owner and note the reason", "Health Log"),
    ("Medication refills due",
     '=COUNTIF([[Health Log.refill_alert]],"Overdue*")'
     '+COUNTIF([[Health Log.refill_alert]],"Due in*")', "",
     "Ask the owner to restock the supply", "Health Log"),
    ("Vet appointments coming up",
     '=COUNTIF([[Health Log.appt_alert]],"Due in*")', "",
     "Confirm transport and who attends", "Health Log"),
    ("Open incidents",
     '=COUNTIF([[Incidents.status]],"Open")'
     '+COUNTIF([[Incidents.status]],"In progress")', "",
     "Close the loop with the owner", "Incidents"),
    ("Clients going inactive",
     '=COUNTIF([[Clients.alert]],"Inactive*")', "",
     "Send a win-back offer", "Clients"),
    ("Client follow-ups overdue",
     '=COUNTIF([[Messages.alert]],"Overdue*")', "",
     "Check the communication log", "Messages"),
    ("Unresolved complaints",
     '=COUNTIFS([[Messages.complaint]],"Yes",[[Messages.resolution]],'
     '"<>Resolved")', "",
     "Resolve it before it becomes a review", "Messages"),
    ("Low or out of stock items",
     '=COUNTIF([[Inventory.stock_status]],"Low*")'
     '+COUNTIF([[Inventory.stock_status]],"Out of stock")', "",
     "Add them to the next supply run", "Inventory"),
    ("Supplies past their expiry date",
     '=COUNTIF([[Inventory.expiry_alert]],"EXPIRED")', "",
     "Dispose of them and reorder", "Inventory"),
    ("Staff certificates expired or expiring",
     '=COUNTIF([[Staff.cert_alert]],"EXPIRED")'
     '+COUNTIF([[Staff.cert_alert]],"Due in*")', "",
     "Book the refresher course", "Staff"),
    ("Client contracts not signed",
     '=COUNTIFS([[Clients.status]],"Active",[[Clients.contract]],'
     '"<>Signed")', "",
     "No service without a signed agreement", "Clients"),
    ("Expenses waiting for a receipt",
     '=COUNTIF([[Expenses.alert]],"Missing receipt")', "",
     "Attach the receipt before tax time", "Expenses"),
]

RENEWALS = [
    ("Business insurance renewal", "=Biz_InsuranceRenewal"),
    ("Licence / permit renewal", "=Biz_LicenceRenewal"),
]


def spec(cfg: Config) -> SheetSpec:
    """The custom task list that sits underneath the alert panel."""
    columns = [
        id_col("task", '"TK-"', digits=3, width=9),
        Col("task", "Task", 38, "text"),
        Col("category", "Category", 16, "text"),
        Col("due", "Due date", 12, "date", validate=date_check()),
        Col("owner", "Owner", 16, "text", validate=list_from("StaffNames")),
        Col("priority", "Priority", 11, "status",
            validate=list_from("PriorityList"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Urgent", "fmt": "bold_bad"},
                {"type": "text", "criteria": "containing", "value": "High",
                 "fmt": "warn"}]),
        Col("status", "Status", 13, "status",
            validate=list_from("TaskStatusList"), cf=status_cf()),
        Col("days_left", "Days left", 9, "int",
            formula='=IF(OR({due}{r}="",{status}{r}="Done",'
                    '{status}{r}="Cancelled"),"",{due}{r}-TODAY())',
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bad"},
                {"type": "cell", "criteria": "between", "minimum": 0,
                 "maximum": 3, "fmt": "warn"}]),
        Col("flag", "Status check", 18, "status",
            formula=blank("task",
                          'IF(OR({status}{r}="Done",'
                          '{status}{r}="Cancelled"),"Closed",'
                          'IF({due}{r}="","No due date",'
                          'IF({due}{r}<TODAY(),"Overdue",'
                          'IF({due}{r}-TODAY()<=ReminderLeadDays,'
                          '"Due soon","On track"))))'),
            cf=alert_cf() + [{"type": "text", "criteria": "containing",
                              "value": "On track", "fmt": "good"},
                             {"type": "text", "criteria": "containing",
                              "value": "Closed", "fmt": "muted"}]),
        Col("notes", "Notes", 34, "wrap"),
    ]

    return SheetSpec(
        name=NAME,
        title="Reminders, Alerts & Task List",
        subtitle="Everything the workbook thinks you should do today, plus "
                 "room for your own reminders.",
        columns=columns,
        rows=cfg.row_count("Tasks"),
        header_row=TASK_HEADER_ROW,
        tab_color=Palette.warn_text,
        freeze_cols=2,
        freeze_at=3,
        samples=sample(cfg).tasks,
        help_text="Add your own reminders here - renewals, marketing "
                  "ideas, supply runs, anything with a due date.",
    )


def decorate(sheet, fmts, cfg: Config, reg: Registry) -> None:
    """Write the automatic alert panel above the task list."""
    ws = sheet.ws
    row = ALERT_HEADER_ROW - 3
    sheet.section(row, "Automatic alerts - refreshed every time the file "
                       "opens", LAST_COL)
    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Anything with a count above zero needs a decision today. "
                "Click the sheet name on the right to jump straight to it.",
                fmts.chrome("note"))
    row += 1

    sheet.write(row, 0, "Alert", fmts.chrome("header_left"))
    sheet.merge(row, 1, 1, "Count", fmts.chrome("header"))
    sheet.merge(row, 2, 3, "Value", fmts.chrome("header"))
    sheet.merge(row, 4, 7, "What to do", fmts.chrome("header"))
    sheet.merge(row, 8, LAST_COL, "Go to", fmts.chrome("header"))
    ws.set_row(row, 22)
    row += 1

    label_fmt = fmts.calc("text")
    count_fmt = fmts.calc("int")
    money_fmt = fmts.calc("money")
    note_fmt = fmts.chrome("note")
    link_fmt = fmts.chrome("nav")

    for label, count, value, todo, target in ALERTS:
        sheet.write(row, 0, label, label_fmt)
        ws.write_formula(row, 1, reg.render(count), count_fmt)
        ws.conditional_format(row, 1, row, 1, {
            "type": "cell", "criteria": ">", "value": 0,
            "format": fmts.cf("bad")})
        if value:
            ws.merge_range(row, 2, row, 3, "", money_fmt)
            ws.write_formula(row, 2, reg.render(value), money_fmt)
        else:
            sheet.merge(row, 2, 3, "", money_fmt)
        sheet.merge(row, 4, 7, todo, note_fmt)
        ws.merge_range(row, 8, row, LAST_COL, "", link_fmt)
        ws.write_url(row, 8, f"internal:{quote_sheet(target)}!A1", link_fmt,
                     target)
        row += 1

    # Renewal dates pulled from the Settings tab.
    row += 1
    sheet.subsection(row, "Renewal dates", LAST_COL)
    row += 1
    sheet.write(row, 0, "Renewal", fmts.chrome("header_left"))
    sheet.merge(row, 1, 2, "Date", fmts.chrome("header"))
    sheet.merge(row, 3, 4, "Days away", fmts.chrome("header"))
    sheet.merge(row, 5, LAST_COL, "Status", fmts.chrome("header"))
    row += 1
    for label, formula in RENEWALS:
        sheet.write(row, 0, label, label_fmt)
        ws.merge_range(row, 1, row, 2, "", fmts.calc("date"))
        ws.write_formula(row, 1, formula, fmts.calc("date"))
        ws.merge_range(row, 3, row, 4, "", fmts.calc("int"))
        ws.write_formula(
            row, 3,
            f'=IF({_cell(1, row)}="","",{_cell(1, row)}-TODAY())',
            fmts.calc("int"))
        ws.merge_range(row, 5, row, LAST_COL, "", fmts.calc("status"))
        ws.write_formula(
            row, 5,
            f'=IF({_cell(1, row)}="","Add the date on the Settings tab",'
            f'IF({_cell(1, row)}<TODAY(),"EXPIRED - renew now",'
            f'IF({_cell(1, row)}-TODAY()<=ExpiryAlertDays,'
            f'"Renew soon","Current")))', fmts.calc("status"))
        ws.conditional_format(row, 5, row, 5, {
            "type": "text", "criteria": "containing", "value": "EXPIRED",
            "format": fmts.cf("bad")})
        ws.conditional_format(row, 5, row, 5, {
            "type": "text", "criteria": "containing", "value": "Renew soon",
            "format": fmts.cf("warn")})
        row += 1


def _cell(col: int, row: int) -> str:
    from ..layout import col_letter
    return f"${col_letter(col)}${row + 1}"
