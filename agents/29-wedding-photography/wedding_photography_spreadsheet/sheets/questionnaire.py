"""`Client Questionnaire` - the printable form, and the answers.

Pick a Booking ID at the top and the whole sheet fills in from what
you already know, leaving only the questions that need the couple's
answers.  Print it, email it, or work through it on a call.

The answers live on the booking, not here, so whatever is written down
travels with the wedding to the shot list, the timeline and the day
sheet.  This tab is the form, not the filing cabinet.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter, list_from

NAME = "Client Questionnaire"
LAST_COL = 9
SHOT_ROWS = 22
TIMELINE_ROWS = 20


def _b(field: str) -> str:
    """A field from the chosen booking."""
    return (f'IFERROR(INDEX([[Wedding Bookings.{field}]],'
            f'MATCH(QuestionnaireBooking,'
            f'[[Wedding Bookings.id]],0)),"")')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_soft)

    s.banner("Client Questionnaire",
             "Everything you need to know before the day, on one "
             "page. Pick a wedding and the rest fills itself in.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 1, 26)
    s.set_col(2, 4, 20)
    s.set_col(5, LAST_COL, 18)

    row = 4
    row = s.field(row, "Wedding", None, style="text",
                  name="QuestionnaireBooking",
                  validate=list_from("BookingList"),
                  value_end=4, help_col=6,
                  help_text="Pick the Booking ID. Everything below "
                            "follows from this one cell.")
    row += 1

    # ---- what you already know -------------------------------------------
    row = s.section(row, "What you already know", LAST_COL)
    row = s.note(
        row,
        "Taken from the booking - there is no point asking a couple "
        "for information you have already written down.",
        LAST_COL, height=26)
    row += 1

    known = [
        ("Couple", "client_name", "text"),
        ("Partner", "partner_name", "text"),
        ("Wedding date", "wedding_date", "date"),
        ("Day of the week", "weekday", "text"),
        ("Ceremony", "ceremony_time", "time"),
        ("Reception", "reception_time", "time"),
        ("Coverage", "coverage_hours", "number1"),
        ("Main venue", "venue", "text"),
        ("Getting ready at", "prep_location", "text"),
        ("Ceremony at", "ceremony_location", "text"),
        ("Reception at", "reception_location", "text"),
        ("Guests", "guests", "int"),
        ("Package", "package", "text"),
        ("Lead photographer", "photographer_name", "text"),
        ("Second shooter", "second_name", "text"),
        ("Days to go", "days_away", "int"),
    ]
    half = (len(known) + 1) // 2
    top = row
    for index, (label, field, style) in enumerate(known):
        column = 1 if index < half else 5
        line = top + (index if index < half else index - half)
        s.write(line, column, label, fmts.chrome("label_bold"))
        s.merge(line, column + 1, column + 2, None,
                fmts.cell(style, "calc"))
        s.formula(line, column + 1, "=" + _b(field),
                  fmts.cell(style, "calc"))
    row = top + half + 1

    # ---- the questions -----------------------------------------------------
    row = s.section(row, "The questions", LAST_COL)
    row = s.note(
        row,
        "Write the answers straight onto the booking - these cells "
        "show what is recorded there. Keeping the answers on the "
        "wedding rather than on this form is what lets the shot list, "
        "the timeline and the day sheet all use them.",
        LAST_COL, height=32)
    row += 1

    questions = [
        ("Must-have photographs", "must_haves",
         "The shots they would be upset not to have. Ask for five, "
         "not fifty."),
        ("Family groups, by name", "family_list",
         "Names, not relationships. This is the question that saves "
         "forty minutes on the day."),
        ("Important guests", "key_guests",
         "Anybody travelling a long way, anybody elderly, anybody who "
         "must be photographed."),
        ("Traditions and rituals", "traditions",
         "Anything cultural or religious, and roughly when in the day "
         "it happens."),
        ("Venue restrictions", "restrictions",
         "No flash, no photographs during the ceremony, a balcony you "
         "may not stand on. Ask the venue as well as the couple."),
        ("Family sensitivities", "sensitivities",
         "Divorced parents, a recent bereavement, two people who must "
         "not be in a group shot together. Far better known now."),
        ("Anything else", "special_requests",
         "A surprise, a dog, a drone, a second dress, a late-night "
         "sparkler exit."),
    ]
    for label, field, help_text in questions:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, 5, None, fmts.cell("wrap", "calc"))
        s.formula(row, 2, "=" + _b(field), fmts.cell("wrap", "calc"))
        s.merge(row, 6, LAST_COL, help_text, fmts.chrome("note"))
        s.row_height(row, 34)
        row += 1
    row += 1

    s.write(row, 1, "Questionnaire sent", fmts.chrome("label_bold"))
    s.formula(row, 2, "=" + _b("questionnaire_sent"),
              fmts.cell("date", "calc"))
    s.write(row, 3, "Answers back", fmts.chrome("label_right"))
    s.formula(row, 4, "=" + _b("questionnaire_back"),
              fmts.cell("date", "calc"))
    s.merge(row, 5, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 5,
        '=IF(QuestionnaireBooking="","Pick a wedding above.",'
        'IF(' + _b("questionnaire_back") + '<>"",'
        '"Answers are in - read them again the week before.",'
        'IF(' + _b("questionnaire_sent") + '="",'
        '"Not sent yet. Send it once the contract is signed.",'
        '"Sent, nothing back. Chase it - the day plan depends on '
        'it.")))',
        fmts.chrome("note"))
    row += 2

    # ---- the day plan ------------------------------------------------------
    row = s.section(row, "The day as it stands", LAST_COL)
    row = s.note(
        row,
        "Built from the Wedding Timeline tab for this Booking ID, in "
        "time order. Print this page and the couple can see the "
        "running order you are working to.",
        LAST_COL, height=28)
    row += 1

    head = row
    s.table_head(head, 1, ["Time", "Until", "What is happening",
                           "Where", "Who", "Must not miss"],
                 widths=[9, 9, 30, 22, 18, 12])
    row = head + 1
    for n in range(1, TIMELINE_ROWS + 1):
        key = f'QuestionnaireBooking&"|"&{n}'
        for col, (field, style) in enumerate([
                ("start", "time"), ("finish", "time"),
                ("shown", "text"), ("location", "text"),
                ("staff_name", "text"), ("critical", "flag")],
                start=1):
            s.formula(
                row, col,
                f'=IF(QuestionnaireBooking="","",'
                f'IFERROR(INDEX([[Wedding Timeline.{field}]],'
                f'MATCH({key},[[Wedding Timeline.day_key]],0)),""))',
                fmts.cell(style, "calc"))
        row += 1
    row += 1

    # ---- the family groups -------------------------------------------------
    row = s.section(row, "Family and group photographs", LAST_COL)
    row = s.note(
        row,
        "Every shot on the Shot List Manager for this wedding that is "
        "either a family group or flagged as a must-have. Hand this "
        "to whoever is rounding people up - a bridesmaid, an usher, "
        "the best man. It works far better than you shouting.",
        LAST_COL, height=32)
    row += 1

    head = row
    s.table_head(head, 1, ["#", "Group", "Shot", "Who is in it",
                           "Asked for by", "Must have", "Taken"],
                 widths=[4, 14, 30, 26, 15, 11, 9])
    row = head + 1
    for n in range(1, SHOT_ROWS + 1):
        s.write(row, 1, n, fmts.chrome("day_number"))
        rank = (f'MATCH(QuestionnaireBooking&"|"&{n},'
                f'[[Shot List Manager.print_key]],0)')
        for col, (field, style) in enumerate([
                ("group_name", "text"), ("shot", "text"),
                ("people", "wrap"), ("requested_by", "text"),
                ("must_have", "flag"), ("done", "flag")], start=2):
            s.formula(
                row, col,
                f'=IF(QuestionnaireBooking="","",'
                f'IFERROR(INDEX([[Shot List Manager.{field}]],'
                f'{rank}),""))',
                fmts.cell(style, "calc"))
        row += 1
    row += 1

    row = s.note(
        row,
        "Print this page before every wedding. Reading the answers "
        "back the week before is the whole point of asking the "
        "questions six months earlier.",
        LAST_COL, height=26)

    s.finish(freeze_row=5, gridlines=False, fit_width=True,
             print_area=f"A1:{chr(65 + LAST_COL)}{row + 2}")
    s.protect()
    return s
