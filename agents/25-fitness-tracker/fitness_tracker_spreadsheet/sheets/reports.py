"""15 Reports & Charts - the printable year.

A month-by-month table plus five native charts: weight and its 7-day
line, sessions per month, minutes by activity type, habit consistency
and the performance of any one exercise picked from a drop down.  The
exercise series lives in a hidden helper column so the chart needs no
array formula.  Print area is one landscape page wide.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import quote_sheet
from ..writer import SheetWriter, list_from
from . import common as C

NAME = "15 Reports & Charts"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.accent)
    last_col = 12
    sheet.banner("15  Reports & Charts",
                 "The year on pages you can print - weight, volume, "
                 "minutes, habits and one exercise of your choice.",
                 last_col)
    log = reg["5 Workout Log"]
    wt = reg["8 Weight Tracker"]
    ca = reg["7 Cardio & Activity"]
    meals = reg["11 Meals & Macros"]
    ql, qw, qc, qm = (quote_sheet(x.name) for x in (log, wt, ca, meals))

    def lr(spec, key):
        return (f"{quote_sheet(spec.name)}!${spec.letter(key)}"
                f"${spec.first_data_row}:${spec.letter(key)}"
                f"${spec.last_data_row}")

    d_log, w_log, dur_log = (lr(log, k) for k in ("date", "wstart", "dur"))
    d_w, kg_w, ma7_w, disp_w = (lr(wt, k) for k in
                                ("date", "kg", "ma7", "ma7_disp"))
    c_type, c_dur, c_km = (lr(ca, k) for k in ("type", "dur", "km"))
    d_m, cal_m, p_m = (lr(meals, k) for k in ("date", "cal_used", "p_used"))

    # ------------------------------------------------------------ month table
    row = 4
    row = sheet.section(row, "MONTH BY MONTH", last_col)
    row = sheet.table_head(row, 0, ["Month", "Sessions", "Minutes",
                                    "Distance", "kcal / day",
                                    "Protein g / day", "Weight (7-day)"],
                           widths=[13, 10, 10, 10, 11, 13, 13])
    first_month = row
    for i in range(12):
        ms = (f'EDATE(DATE(YEAR(ProgrammeStart),MONTH(ProgrammeStart),1),'
              f'{i})')
        me = (f'EDATE(DATE(YEAR(ProgrammeStart),MONTH(ProgrammeStart),1),'
              f'{i + 1})-1')
        sheet.formula(row, 0, f'=IF({ms}>TODAY()+365,"",TEXT({ms},'
                              f'"mmm yyyy"))', sheet.f.calc("text"))
        sheet.formula(row, 1,
                      f'=IF($A{row + 1}="","",SUMPRODUCT(({d_log}>={ms})*'
                      f'({d_log}<={me})/((COUNTIFS({d_log},{d_log})+('
                      f'{d_log}="")))))',
                      sheet.f.calc("number1"))
        sheet.formula(row, 2,
                      f'=IF($A{row + 1}="","",SUMIFS({dur_log},{d_log},'
                      f'">="&{ms},{d_log},"<="&{me}))',
                      sheet.f.calc("int"))
        sheet.formula(row, 3,
                      f'=IF($A{row + 1}="","",IF(SUMIFS({c_km},{lr(ca, "date")},'
                      f'">="&{ms},{lr(ca, "date")},"<="&{me})=0,"",IF('
                      f'Units="Imperial",SUMIFS({c_km},{lr(ca, "date")},'
                      f'">="&{ms},{lr(ca, "date")},"<="&{me})/KmPerMi,'
                      f'SUMIFS({c_km},{lr(ca, "date")},">="&{ms},'
                      f'{lr(ca, "date")},"<="&{me}))))',
                      sheet.f.calc("number1"))
        sheet.formula(row, 4,
                      f'=IF($A{row + 1}="","",IF(SUMIFS({cal_m},{d_m},'
                      f'">="&{ms},{d_m},"<="&{me})=0,"",SUMIFS({cal_m},'
                      f'{d_m},">="&{ms},{d_m},"<="&{me})/30))',
                      sheet.f.calc("int"))
        sheet.formula(row, 5,
                      f'=IF($A{row + 1}="","",IF(SUMIFS({p_m},{d_m},">="&'
                      f'{ms},{d_m},"<="&{me})=0,"",SUMIFS({p_m},{d_m},'
                      f'">="&{ms},{d_m},"<="&{me})/30))',
                      sheet.f.calc("int"))
        sheet.formula(row, 6,
                      f'=IF($A{row + 1}="","",IFERROR(INDEX({ma7_w},'
                      f'MATCH({me},{d_w},1)),""))',
                      sheet.f.calc("number1"))
        row += 1
    last_month = row - 1
    row += 1

    # ------------------------------------------------- minutes by type block
    row = sheet.section(row, "MINUTES BY ACTIVITY TYPE", 4)
    type_first = row
    from ..config import ACTIVITY_TYPES
    for label, _met in ACTIVITY_TYPES:
        sheet.write(row, 0, label, sheet.f.calc("text"))
        sheet.formula(row, 1, f'=SUMIFS({c_dur},{c_type},$A{row + 1})',
                      sheet.f.calc("int"))
        row += 1
    type_last = row - 1
    row += 1

    # ------------------------------------------- exercise performance picker
    row = sheet.section(row, "ONE EXERCISE OVER TIME", last_col)
    row = sheet.field(row, "Pick an exercise", None, label_col=0,
                      value_col=2, validate=list_from("ExerciseNames"),
                      help_text="The hidden column to the right builds "
                                "the series; the chart below follows it.")
    pick = f"$C${row}"
    helper_col = last_col + 2
    sheet.set_col(helper_col, helper_col, 9, hidden=True)
    sheet.write(3, helper_col, "series", sheet.f.chrome("header"))
    for offset in range(log.rows):
        lr_ = log.first_data_row + offset
        sheet.formula(4 + offset, helper_col,
                      f'=IF({ql}!${log.letter("exercise")}${lr_}={pick},'
                      f'{ql}!${log.letter("e1rm_disp")}${lr_},"")',
                      sheet.f.calc("number1"))
    row += 1
    row = sheet.note(row, "Estimated 1RM per logged row of that "
                          "exercise, blanks between - the chart connects "
                          "the dots.", last_col, height=24)

    # ---------------------------------------------------------------- charts
    ch = book.add_chart({"type": "line"})
    ch.add_series({
        "name": "7-day average weight",
        "categories": [qw, wt.first_data_row - 1, wt.letter_index("date"),
                       wt.last_data_row - 1, wt.letter_index("date")]
        if hasattr(wt, "letter_index") else
        f"{qw}!${wt.letter('date')}${wt.first_data_row}:"
        f"${wt.letter('date')}${wt.last_data_row}",
        "values": f"{qw}!${wt.letter('ma7_disp')}${wt.first_data_row}:"
                  f"${wt.letter('ma7_disp')}${wt.last_data_row}",
        "line": {"color": "#14655A", "width": 2},
    })
    ch.set_title({"name": "Weight - 7-day average"})
    ch.set_size({"width": 620, "height": 300})
    sheet.ws.insert_chart("H5", ch)

    ch2 = book.add_chart({"type": "column"})
    ch2.add_series({
        "name": "Sessions",
        "categories": f"={quote_sheet(NAME)}!$A${first_month}:"
                      f"$A${last_month}",
        "values": f"={quote_sheet(NAME)}!$B${first_month}:"
                  f"$B${last_month}",
    })
    ch2.set_title({"name": "Sessions per month"})
    ch2.set_size({"width": 620, "height": 300})
    sheet.ws.insert_chart("H22", ch2)

    ch3 = book.add_chart({"type": "bar"})
    ch3.add_series({
        "name": "Minutes",
        "categories": f"={quote_sheet(NAME)}!$A${type_first}:"
                      f"$A${type_last}",
        "values": f"={quote_sheet(NAME)}!$B${type_first}:"
                  f"$B${type_last}",
    })
    ch3.set_title({"name": "Minutes by activity type"})
    ch3.set_size({"width": 620, "height": 300})
    sheet.ws.insert_chart("H39", ch3)

    ch4 = book.add_chart({"type": "line"})
    ch4.add_series({
        "name": "Estimated 1RM",
        "categories": f"{ql}!${log.letter('date')}${log.first_data_row}:"
                      f"${log.letter('date')}${log.last_data_row}",
        "values": f"{quote_sheet(NAME)}!$"
                  f"{_letter(helper_col)}${log.first_data_row}:"
                  f"${_letter(helper_col)}${log.last_data_row}",
        "line": {"color": "#E4572E", "width": 2},
    })
    ch4.set_title({"name": "Chosen exercise - estimated 1RM"})
    ch4.set_size({"width": 620, "height": 300})
    sheet.ws.insert_chart("H56", ch4)

    C.footer(sheet, cfg, last_col, row + 2)
    sheet.finish(freeze_row=4, freeze_col=1,
                 print_area=f"$A$1:$G${last_month + 3}")
    return sheet


def _letter(index: int) -> str:
    from ..layout import col_letter
    return col_letter(index)
