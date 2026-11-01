"""Editing Workflow - one row per wedding, ten steps from card to gallery.

The backlog is where wedding photography businesses quietly fail.  The
shooting is finished, the money is mostly in, and three weddings sit
unedited while the next one is being booked.  This tab makes the
backlog visible and puts a date on it.
"""

from __future__ import annotations

from ..config import EDITING_STEPS
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, bar_cf, blank, date_num_col, id_col,
                     lookup_booking, lookup_staff, money_cf, status_cf,
                     yesno, zero)

NAME = "Editing Workflow"

#: the ten steps become ten tick columns, and the stage is derived
STEP_KEYS = [f"step_{key}" for key, _ in EDITING_STEPS]


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "EditPrefix", digits=cfg.digits("edit"),
               header="Job ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="One row per wedding. The booking shows the stage "
                 "this job has reached.",
            group="The job"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="The job"),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The job"),
        Col("editor", "Editor", 11, "id",
            validate=list_from("StaffList"), group="The job"),
        Col("editor_name", "Editor name", 16, "text",
            formula=lookup_staff("name", key="editor", missing=""),
            group="The job"),
        Col("outsourced", "Outsourced", 10, "flag",
            validate=yesno("Yes when an outside editor does it. The "
                           "cost goes on the Expense Tracker against "
                           "the same Booking ID."),
            group="The job"),
        Col("priority", "Priority", 11, "text",
            validate=list_from("PriorityList"), group="The job"),
        Col("rush", "Rush job", 9, "flag",
            validate=yesno("Yes if they paid the rush fee. The "
                           "promised date tightens automatically."),
            group="The job"),
    ]

    # ---- the ten steps ------------------------------------------------------
    for key, label in EDITING_STEPS:
        columns.append(
            Col(f"step_{key}", label, 13, "flag",
                validate=yesno(), cf=status_cf(), group="The ten steps"))

    done_sum = "+".join(f'({{step_{key}}}{{r}}="Yes")' for key, _ in EDITING_STEPS)
    steps = len(EDITING_STEPS)

    # the stage name is the last ticked step, so it can never disagree
    # with the ticks themselves
    stage = '""'
    for key, label in EDITING_STEPS:
        stage = f'IF({{step_{key}}}{{r}}="Yes","{label}",{stage})'

    columns += [
        Col("steps_done", "Steps done", 10, "int",
            formula=zero("booking", done_sum), group="How far along"),
        Col("progress", "Progress", 10, "percent0",
            formula=blank("booking", f"{{steps_done}}{{r}}/{steps}"),
            cf=bar_cf(), group="How far along"),
        Col("stage", "Stage", 20, "status",
            formula=blank("booking",
                          f'IF({{steps_done}}{{r}}<=0,"Not started",'
                          f'IF({{steps_done}}{{r}}>={steps},"Complete",'
                          f'{stage}))'),
            cf=status_cf(),
            note="Always the last step you ticked, so the stage and "
                 "the ticks can never disagree.",
            group="How far along"),

        # ---- dates ------------------------------------------------------------
        Col("started", "Started", 11, "date",
            validate=date_check(), group="Dates"),
        Col("preview_due", "Preview due", 12, "date",
            formula=blank("booking",
                          'IF({wedding_date}{r}="","",'
                          '{wedding_date}{r}+PreviewDays)'),
            group="Dates"),
        Col("preview_sent", "Preview sent", 12, "date",
            validate=date_check(), group="Dates"),
        Col("due", "Gallery promised", 14, "date",
            formula=blank("booking",
                          'IF({wedding_date}{r}="","",'
                          'IF({rush}{r}="Yes",'
                          '{wedding_date}{r}+RushDeliveryDays,'
                          '{wedding_date}{r}+DeliveryDays))'),
            note="Your standard turnaround from Settings, or the "
                 "shorter rush promise if they paid for it.",
            group="Dates"),
        Col("finished", "Finished", 11, "date",
            validate=date_check(), group="Dates"),
        Col("days_taken", "Days taken", 10, "int",
            formula=blank("booking",
                          'IF({finished}{r}="","",'
                          'IF({wedding_date}{r}="","",'
                          '{finished}{r}-{wedding_date}{r}))'),
            group="Dates"),
        Col("days_left", "Days left", 10, "int",
            formula=blank("booking",
                          'IF({due}{r}="","",'
                          'IF({finished}{r}<>"","",'
                          '{due}{r}-TodayDate))'),
            note="Negative means you are past the date you promised.",
            group="Dates"),
        Col("late", "Late", 8, "flag",
            formula=blank("booking",
                          'IF({due}{r}="","No",'
                          'IF({finished}{r}<>"",'
                          'IF({finished}{r}>{due}{r},"Yes","No"),'
                          'IF(TodayDate>{due}{r},"Yes","No")))'),
            cf=status_cf(), group="Dates"),

        # ---- the work -----------------------------------------------------------
        Col("shot_count", "Photos taken", 11, "int",
            validate=number_check(0, 100000), group="The work"),
        Col("kept", "Kept after culling", 13, "int",
            validate=number_check(0, 100000), group="The work"),
        Col("delivered_count", "Delivered", 10, "int",
            validate=number_check(0, 100000), group="The work"),
        Col("promised_count", "Package promises", 13, "int",
            formula=zero("booking",
                         'IFERROR(INDEX('
                         '[[Packages & Pricing.images]],'
                         'MATCH(INDEX([[Wedding Bookings.package]],'
                         'MATCH({booking}{r},'
                         '[[Wedding Bookings.id]],0)),'
                         '[[Packages & Pricing.name]],0))*1,0)'),
            note="How many edited images the package says they get.",
            group="The work"),
        Col("short", "Short by", 9, "int",
            formula=zero("booking",
                         'IF({delivered_count}{r}="",0,'
                         'MAX(0,{promised_count}{r}-'
                         '{delivered_count}{r}))'),
            group="The work"),
        Col("keep_rate", "Keep rate", 10, "percent0",
            formula=blank("booking",
                          'IF({shot_count}{r}="","",'
                          'IF({shot_count}{r}<=0,"",'
                          'IF({kept}{r}="","",'
                          '{kept}{r}/{shot_count}{r})))'),
            group="The work"),
        Col("hours", "Hours spent", 11, "number1",
            validate=number_check(0, 500),
            note="Be honest. This is the number that decides whether "
                 "your packages are priced properly.",
            group="The work"),
        Col("hours_expected", "Hours expected", 12, "number1",
            formula=zero("booking", "EditingHours"), hidden=True,
            group="The work"),
        Col("hours_over", "Hours over", 10, "number1",
            formula=zero("booking",
                         'IF({hours}{r}="",0,'
                         'ROUND({hours}{r}-{hours_expected}{r},2))'),
            group="The work"),
        Col("rate", "Editing rate", 11, "money",
            formula=zero("booking",
                         'IF({editor}{r}="",EditingRate,'
                         'IFERROR(INDEX('
                         '[[Photographer & Staff.edit_rate]],'
                         'MATCH({editor}{r},'
                         '[[Photographer & Staff.id]],0))*1,'
                         'EditingRate))'),
            hidden=True, group="The work"),
        Col("cost", "Editing cost", 12, "money",
            formula=zero("booking",
                         'ROUND(IF({hours}{r}="",0,{hours}{r})*'
                         '{rate}{r},2)'),
            cf=money_cf(),
            note="Hours times the editor's rate. The booking subtracts "
                 "this from the wedding's profit.",
            group="The work"),
        Col("backup", "Backed up twice", 12, "flag",
            validate=yesno("Two copies in two places. The one thing "
                           "on this tab you cannot undo."),
            cf=status_cf(), group="The work"),
        Col("notes", "Notes", 26, "wrap", group="The work"),

        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        date_num_col("due", "due_num", "Due date number"),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({steps_done}{r}>=' + str(steps) + ','
                'IF({short}{r}>0,'
                '"Check - fewer images than the package promises",'
                '"OK"),'
                'IF({backup}{r}<>"Yes",'
                '"Urgent - not backed up in two places",'
                'IF({wedding_date}{r}="","Check - booking has no date",'
                'IF({wedding_date}{r}>TodayDate,"OK - not shot yet",'
                'IF({late}{r}="Yes",'
                'IF({days_left}{r}<>"",'
                'IF({days_left}{r}<-14,'
                '"Urgent - two weeks past the promised date",'
                '"Overdue - past the date you promised"),'
                '"Overdue - past the date you promised"),'
                'IF({preview_sent}{r}="",'
                'IF({preview_due}{r}<>"",'
                'IF(TodayDate>{preview_due}{r},'
                '"Action - preview images are overdue",'
                '"OK - in progress"),"OK - in progress"),'
                'IF({days_left}{r}<>"",'
                'IF({days_left}{r}<=7,'
                '"Action - gallery due within the week","OK"),'
                '"OK"))))))))'),
            cf=alert_cf(), group="The work"),
    ]

    return SheetSpec(
        name=NAME,
        title="Editing Workflow",
        subtitle=("Every wedding between the last frame and the "
                  "finished gallery, and how late it is"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("editing", cfg),
        help_text=(
            "One row per wedding. Tick the ten steps as you work "
            "through them and the stage, the progress bar and the "
            "booking all keep up on their own. The promised date "
            "comes from your turnaround setting, counted from the "
            "wedding day."),
        extra_notes=[
            "Tick 'Backed up twice' before anything else, and mean "
            "it. Two copies in two places. Everything else on this "
            "tab can be redone; this cannot.",
            "Log the hours honestly. A wedding that took twenty-six "
            "hours to edit instead of eighteen is not a disaster, but "
            "a package priced on eighteen hours that always takes "
            "twenty-six is.",
            "A backlog of three unedited weddings in August is "
            "normal. A backlog of three unedited weddings in January "
            "is a business problem, and this tab is where you see the "
            "difference.",
        ],
    )
