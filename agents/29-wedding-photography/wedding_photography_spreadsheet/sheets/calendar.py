"""`Booking Calendar` - twelve months of dates, at a glance.

A wedding diary is mostly a question of which dates have gone.  This
tab draws a real calendar for any twelve months you choose and colours
every day you are holding, so "are you free on the 14th of June?" is a
glance rather than a scroll through two hundred rows.

Weeks start on Saturday, because that is the day most weddings happen.

It is drawn by formula from the Wedding Bookings tab.  It does not
sync with a phone, a website or an enquiry form: a date is taken here
only because you typed a booking there.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry, col_letter
from ..writer import SheetWriter, cf_formula, date_check, number_check

NAME = "Booking Calendar"
LAST_COL = 24
MONTHS = 12
WEEK_ROWS = 6
PER_ROW = 3                      # month blocks across the page
BLOCK = 8                        # 7 day columns + 1 spacer

#: Saturday first - a wedding photographer's week
WEEKDAYS = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]

HOLDS = '[[Wedding Bookings.holds]],"Yes"'
WED_NUM = "[[Wedding Bookings.wed_num]]"


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.accent)

    s.banner("Booking Calendar",
             "Twelve months of dates with every wedding you are "
             "holding marked. Change the starting month and the whole "
             "year redraws.",
             LAST_COL)
    s.set_col(0, 0, 3)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 6)

    row = 4
    row = s.note(
        row,
        "Weeks begin on Saturday. A day counts as taken when a "
        "booking on that date has a status that holds the diary - "
        "pencilled in counts, cancelled does not. Two live weddings "
        "on one day turn red here and are flagged on the booking too.",
        LAST_COL, height=34)
    row += 1

    row = s.field(row, "Calendar starts", cfg.today.replace(day=1),
                  style="date", name="CalendarStart",
                  validate=date_check(),
                  help_text="Type the first of any month. The twelve "
                            "months below follow on from it.",
                  help_col=8)
    row = s.field(row, "Months to draw", MONTHS, style="int",
                  name="CalendarMonths", validate=number_check(1, 12),
                  help_text="Up to twelve.", help_col=8)
    row += 1

    # ---- legend -----------------------------------------------------------
    s.write(row, 1, "Free", fmts.chrome("legend_input"))
    s.merge(row, 2, 3, "Held", fmts.cf("good"))
    s.merge(row, 4, 6, "Two weddings", fmts.cf("bad"))
    s.merge(row, 7, LAST_COL,
            "Hold a date by giving the booking a status of Pencilled "
            "in or better. Names are in the list underneath.",
            fmts.chrome("note"))
    row += 2

    # ---- twelve month blocks -----------------------------------------------
    grid_top = row
    for index in range(MONTHS):
        band, slot = divmod(index, PER_ROW)
        column = 1 + slot * BLOCK
        top = grid_top + band * (WEEK_ROWS + 5)

        first_of_month = (f'DATE(YEAR(CalendarStart),'
                          f'MONTH(CalendarStart)+{index},1)')
        shown = f'{index + 1}<=CalendarMonths'

        s.merge(top, column, column + 6, None, fmts.chrome("subsection"))
        s.formula(top, column,
                  f'=IF(NOT({shown}),"",'
                  f'TEXT({first_of_month},"mmmm yyyy"))',
                  fmts.chrome("subsection"))

        s.merge(top + 1, column, column + 6, None, fmts.chrome("note"))
        s.formula(
            top + 1, column,
            f'=IF(NOT({shown}),"",'
            f'COUNTIFS({WED_NUM},">="&{first_of_month},'
            f'{WED_NUM},"<="&EOMONTH({first_of_month},0),{HOLDS})'
            f'&" booked")',
            fmts.chrome("note"))

        head = top + 2
        for offset, label in enumerate(WEEKDAYS):
            s.write(head, column + offset, label, fmts.chrome("header"))

        # the Saturday on or before the 1st (serial 6 is a Saturday)
        origin = (f'({first_of_month}-MOD({first_of_month}-6,7))')
        for week in range(WEEK_ROWS):
            line = head + 1 + week
            for offset in range(7):
                serial = f"({origin}+{week * 7 + offset})"
                s.formula(
                    line, column + offset,
                    f'=IF(NOT({shown}),"",'
                    f'IF(MONTH({serial})<>MONTH({first_of_month}),"",'
                    f'DAY({serial})))',
                    fmts.cell("int", "calc"))

        # one pair of conditional rules per block, anchored on its own
        # top-left cell so the relative reference walks the grid
        anchor = f"{col_letter(column)}{head + 2}"
        rng = (f"{anchor}:{col_letter(column + 6)}"
               f"{head + WEEK_ROWS + 1}")
        serial_of_cell = (f'DATE(YEAR(CalendarStart),'
                          f'MONTH(CalendarStart)+{index},{anchor})')
        clash = reg.render(
            f'AND(ISNUMBER({anchor}),'
            f'COUNTIFS({WED_NUM},{serial_of_cell},{HOLDS})>1)')
        held = reg.render(
            f'AND(ISNUMBER({anchor}),'
            f'COUNTIFS({WED_NUM},{serial_of_cell},{HOLDS})>0)')
        s.cf(rng, dict(cf_formula(clash, "bad"), stop_if_true=True))
        s.cf(rng, cf_formula(held, "good"))

    bands = (MONTHS + PER_ROW - 1) // PER_ROW
    row = grid_top + bands * (WEEK_ROWS + 5) + 1

    # ---- the same thing as a list ------------------------------------------
    row = s.section(row, "Every date you are holding", LAST_COL)
    row = s.note(
        row,
        "The diary as a list, soonest first, straight from the "
        "Wedding Bookings tab. This is the one to read down the phone "
        "when somebody asks about a date.",
        LAST_COL, height=28)
    row += 1

    head = row
    s.table_head(head, 1, ["#", "Date", "Day", "Couple", "Status",
                           "Venue", "Photographer", "Ceremony",
                           "Hours", "Value", "Days away",
                           "What to do"],
                 widths=[4, 12, 7, 20, 13, 18, 15, 9, 8, 11, 10, 28])
    row = head + 1
    shown_rows = max(12, cfg.scale_rows(60))
    for n in range(1, shown_rows + 1):
        rank = f'MATCH({n},[[Wedding Bookings.upcoming_rank]],0)'
        s.write(row, 1, n, fmts.chrome("day_number"))
        for col, (field, style) in enumerate([
                ("wedding_date", "date"), ("weekday", "text"),
                ("client_name", "text"), ("status", "status"),
                ("venue", "text"), ("photographer_name", "text"),
                ("ceremony_time", "time"),
                ("coverage_hours", "number1"),
                ("total_value", "money"), ("days_away", "int"),
                ("alert", "text")], start=2):
            s.formula(row, col,
                      f'=IFERROR(INDEX([[Wedding Bookings.{field}]],'
                      f'{rank}),"")',
                      fmts.cell(style, "calc"))
        row += 1
    row += 1

    row = s.note(
        row,
        "This calendar is drawn by formula. It does not connect to "
        "Google Calendar, an enquiry form or a booking platform, and "
        "nothing you do here changes a booking - edit the wedding on "
        "the Wedding Bookings tab and this redraws itself.",
        LAST_COL, height=32)

    s.finish(freeze_row=4, gridlines=False, fit_width=False)
    s.protect()
    return s
