"""The hidden engine tab.

Exposes the *Report Date* named cell plus a few window helpers everything
else uses, and quietly fills the columns from B to CG so the workbook always
has scratch space. The visible content stays in columns A to E.
"""

from __future__ import annotations

import datetime as _dt

from ..layout import quote_sheet
from ..writer import SheetWriter, date_check

NAME = "Calc"
LAST_COL = 85            # CG
WINDOW_DAYS = 365


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#A0A0A0")
    f = sheet.f
    sheet.ws.hide_gridlines(2)

    sheet.set_col(0, 0, 22)
    sheet.set_col(1, 1, 14)
    sheet.set_col(2, 4, 18)
    # Scratch columns, hidden from curious eyes.
    sheet.set_col(5, 8, 12, hidden=True)
    sheet.set_col(9, 21, 11, hidden=True)
    sheet.set_col(22, LAST_COL, 11, hidden=True)

    sheet.merge(0, 0, 4, "Engine - hidden. Unhide only to troubleshoot.",
                f.chrome("title"))
    sheet.row_height(0, 28)

    report_date = cfg.today
    sheet.write(2, 0, "Report_Date", f.chrome("label_bold"))
    sheet.write(2, 1, report_date, f.cell("date", "input"))
    sheet.ws.data_validation(2, 1, 2, 1, date_check())
    book.define_name("Report_Date", f"={quote_sheet(NAME)}!$B$3")

    sheet.write(3, 0, "Window_Start", f.chrome("label_bold"))
    sheet.ws.write_formula(
        3, 1,
        f"={quote_sheet(NAME)}!$B$3-13", f.cell("date", "calc"))
    book.define_name("Window_Start", f"={quote_sheet(NAME)}!$B$4")

    sheet.write(4, 0, "Window_End", f.chrome("label_bold"))
    sheet.ws.write_formula(
        4, 1,
        f"={quote_sheet(NAME)}!$B$3+13", f.cell("date", "calc"))
    book.define_name("Window_End", f"={quote_sheet(NAME)}!$B$5")

    sheet.write(5, 0, "Today Serial", f.chrome("label_bold"))
    sheet.ws.write_formula(
        5, 1, f"={quote_sheet(NAME)}!$B$3", f.cell("int", "calc"))
    book.define_name("TodaySerial", f"={quote_sheet(NAME)}!$B$6")

    # A year of daily date keys in columns J..(J+364) - the Month View and
    # the print week sheets hang off these.
    start_col = 9
    sheet.write(2, start_col - 1, "Daily keys", f.chrome("label_bold"))
    for i in range(WINDOW_DAYS):
        if i == 0:
            formula = f"={quote_sheet(NAME)}!$B$4"
        else:
            col = start_col + i - 1
            formula = f"={quote_sheet(NAME)}!${_col(col)}$3+1"
        sheet.ws.write_formula(2, start_col + i, formula,
                               f.cell("date", "plain"))
    book.define_name("DayKeys",
                     f"={quote_sheet(NAME)}!${_col(start_col)}$3:"
                     f"${_col(start_col + WINDOW_DAYS - 1)}$3")

    # Notes for future us.
    notes = [
        "Named cells defined here: Report Date, Window Start, Window End, "
        "TodaySerial, DayKeys.",
        "Report Date drives every countdown, overdue flag and week "
        "boundary in the workbook.",
        "Change Report Date on this tab to preview the planner at another "
        "point in the year.",
    ]
    for i, note in enumerate(notes):
        sheet.merge(7 + i, 0, 4, note, f.chrome("note"))
    sheet.protect()
    return sheet


def _col(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters
