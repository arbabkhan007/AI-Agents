"""14 Weekly & Monthly Review - adherence first, reflections after.

Twelve weekly blocks and twelve monthly ones.  The numbers (sessions,
minutes, calories against target, weight change) are pulled in
automatically with SUMIFS / COUNTIFS / INDEX-MATCH; the wins, barriers,
lessons and next three goals are the buyer's own words.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import quote_sheet
from ..writer import SheetWriter
from . import common as C

NAME = "14 Weekly & Monthly Review"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary_mid, landscape=False)
    last_col = 7
    sheet.banner("14  Weekly & Monthly Review",
                 "The numbers arrive first, then your words - twelve "
                 "weeks and twelve months of them.", last_col)
    log = reg["5 Workout Log"]
    wt = reg["8 Weight Tracker"]
    meals = reg["11 Meals & Macros"]
    ql, qw, qm = (quote_sheet(x.name) for x in (log, wt, meals))
    d_log, w_log, dur_log, s_log = (
        f"{ql}!${log.letter(k)}${log.first_data_row}:"
        f"${log.letter(k)}${log.last_data_row}"
        for k in ("date", "wstart", "dur", "sid"))
    d_w, ma7_w = (f"{qw}!${wt.letter(k)}${wt.first_data_row}:"
                  f"${wt.letter(k)}${wt.last_data_row}"
                  for k in ("date", "ma7"))
    d_m, cal_m = (f"{qm}!${meals.letter(k)}${meals.first_data_row}:"
                  f"${meals.letter(k)}${meals.last_data_row}"
                  for k in ("date", "cal_used"))

    row = 4
    row = sheet.section(row, "TWELVE WEEKLY REVIEWS", last_col)
    for i in range(12):
        ws = f"ProgrammeStart+{7 * i}"
        we = f"{ws}+6"
        sheet.merge(row, 0, last_col,
                    f"WEEK {i + 1}", sheet.f.chrome("subsection"))
        row += 1
        rows = [
            ("Week", "=" + ws, "date"),
            ("Sessions logged",
             f'=SUMPRODUCT(({w_log}>={ws})*({w_log}<={we})/((COUNTIFS('
             f'{w_log},{w_log},{s_log},{s_log})+({s_log}=""))))', "number1"),
            ("Training minutes",
             f'=SUMIFS({dur_log},{w_log},">="&{ws},{w_log},"<="&{we})',
             "int"),
            ("Calories a day (logged)",
             f'=IF(SUMIFS({cal_m},{d_m},">="&{ws},{d_m},"<="&{we})=0,"",'
             f'SUMIFS({cal_m},{d_m},">="&{ws},{d_m},"<="&{we})/7)', "int"),
            ("Weight change, 7-day line",
             f'=IF(IFERROR(INDEX({ma7_w},MATCH({we},{d_w},1)),"")="","",'
             f'IF(IFERROR(INDEX({ma7_w},MATCH({ws},{d_w},1)),"")="","",'
             f'INDEX({ma7_w},MATCH({we},{d_w},1))-INDEX({ma7_w},MATCH('
             f'{ws},{d_w},1))))', "number1"),
        ]
        for label, formula, style in rows:
            sheet.merge(row, 0, 1, label, sheet.f.chrome("label"))
            sheet.formula(row, 2, formula, sheet.f.calc(style))
            row += 1
        for label in ("Wins", "Barriers", "Lessons",
                      "Next week's three goals"):
            sheet.merge(row, 0, 1, label, sheet.f.chrome("label"))
            sheet.merge(row, 2, last_col, None, sheet.f.input("wrap"))
            row += 1
        row += 1

    row = sheet.section(row, "TWELVE MONTHLY REVIEWS", last_col)
    for i in range(12):
        ms = f'EDATE(DATE(YEAR(ProgrammeStart),MONTH(ProgrammeStart),1),' \
             f'{i})'
        me = f'EDATE(DATE(YEAR(ProgrammeStart),MONTH(ProgrammeStart),1),' \
             f'{i + 1})-1'
        sheet.merge(row, 0, last_col, f"MONTH {i + 1}",
                    sheet.f.chrome("subsection"))
        row += 1
        rows = [
            ("Month", "=" + ms, "date"),
            ("Sessions logged",
             f'=SUMPRODUCT(({d_log}>={ms})*({d_log}<={me})/((COUNTIFS('
             f'{d_log},{d_log})+({d_log}=""))))', "number1"),
            ("Training minutes",
             f'=SUMIFS({dur_log},{d_log},">="&{ms},{d_log},"<="&{me})',
             "int"),
            ("Calories a day (logged)",
             f'=IF(SUMIFS({cal_m},{d_m},">="&{ms},{d_m},"<="&{me})=0,"",'
             f'SUMIFS({cal_m},{d_m},">="&{ms},{d_m},"<="&{me})/30)', "int"),
        ]
        for label, formula, style in rows:
            sheet.merge(row, 0, 1, label, sheet.f.chrome("label"))
            sheet.formula(row, 2, formula, sheet.f.calc(style))
            row += 1
        for label in ("Wins", "Barriers", "Lessons",
                      "Next month's three goals"):
            sheet.merge(row, 0, 1, label, sheet.f.chrome("label"))
            sheet.merge(row, 2, last_col, None, sheet.f.input("wrap"))
            row += 1
        row += 1
    C.footer(sheet, cfg, last_col, row)
    sheet.finish(freeze_row=3, gridlines=False)
    return sheet
