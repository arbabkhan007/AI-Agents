"""3 Dashboard - KPI tiles, goal bars, week over week, honest empties.

Every tile is a formula over the registers; before any data exists the
tiles show dashes and a single plain-English panel explains what to do
first, so a blank file never looks broken.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import quote_sheet
from ..layout import col_letter
from ..writer import SheetWriter
from . import common as C
from . import habits as H

NAME = "3 Dashboard"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.accent, landscape=False)
    last_col = 11
    sheet.banner("3  Dashboard",
                 "The week at a glance - everything below reads the "
                 "registers, nothing is typed here.", last_col)
    log = reg["5 Workout Log"]
    wt = reg["8 Weight Tracker"]
    meals = reg["11 Meals & Macros"]
    ws_tab = reg["12 Water & Sleep"]
    ql, qw, qm, qs = (quote_sheet(x.name) for x in (log, wt, meals, ws_tab))
    qh = quote_sheet("10 Habit Tracker")
    HW = col_letter(H.SUM_COL0 + 3)   # habit "this week" column
    HB = col_letter(H.SUM_COL0 + 1)   # habit best streak column

    def lr(spec, key):
        return (f"{quote_sheet(spec.name)}!${spec.letter(key)}"
                f"${spec.first_data_row}:${spec.letter(key)}"
                f"${spec.last_data_row}")

    d_log, s_log, w_log, dur_log = (lr(log, k) for k in
                                    ("date", "sid", "wstart", "dur"))
    kg_w, disp_w, date_w, ma7_w = (lr(wt, k) for k in
                                   ("kg", "disp", "date", "ma7_disp"))
    d_m, cal_m = lr(meals, "date"), lr(meals, "cal_used")
    d_s, tot_s, hrs_s = lr(ws_tab, "date"), lr(ws_tab, "total"), \
        lr(ws_tab, "hours")
    mob_s = lr(ws_tab, "mobility")

    ws_this = C.week_start_of("TODAY()")
    ws_last = f"{ws_this}-7"

    def distinct_in(range_dates, cond_extra=""):
        return (f'SUMPRODUCT(({range_dates}<>"")*{cond_extra}/'
                f'COUNTIFS({range_dates},{range_dates}))')

    row = 4
    row = sheet.section(row, "RIGHT NOW", last_col)
    tiles = [
        ("Current weight",
         f'=IFERROR(INDEX({disp_w},MATCH(MAX({date_w}),{date_w},0)),"-")',
         "number1", "latest weigh-in, 7-day line on tab 8"),
        ("Change from start",
         f'=IF(IFERROR(INDEX({kg_w},MATCH(MAX({date_w}),{date_w},0)),"")='
         f'"" ,"-",IF(Units="Imperial",(INDEX({kg_w},MATCH(MAX({date_w}),'
         f'{date_w},0))-StartKg)/KgPerLb,INDEX({kg_w},MATCH(MAX({date_w}),'
         f'{date_w},0))-StartKg))',
         "number1", "since your starting weight"),
        ("Workouts this week",
         f'=IF(SUMPRODUCT(({w_log}={ws_this})/((COUNTIFS({w_log},{w_log},'
         f'{s_log},{s_log})+({s_log}=""))))=0,"-",SUMPRODUCT(({w_log}='
         f'{ws_this})/((COUNTIFS({w_log},{w_log},{s_log},{s_log})+('
         f'{s_log}="")))))',
         "number1", f"target {cfg.sessions_per_week} a week"),
        ("Minutes this week",
         f'=IF(SUMIFS({dur_log},{w_log},{ws_this})=0,"-",SUMIFS({dur_log},'
         f'{w_log},{ws_this}))',
         "int", "strength sessions, tab 5"),
        ("Habit rate this week",
         f'=IF(COUNT({qh}!${HW}$8:${HW}$19)=0,"-",AVERAGE({qh}!${HW}$8:'
         f'${HW}$19)/7)',
         "percent0", "ticks over days, tab 10"),
        ("Best streak going",
         f'=IF(MAX({qh}!${HB}$8:${HB}$19)=0,"-",MAX({qh}!${HB}$8:'
         f'${HB}$19))',
         "int", "days, rest days protected"),
        ("Calories, 7-day average",
         f'=IF(SUMIFS({cal_m},{d_m},">="&TODAY()-6,{d_m},"<="&TODAY())=0,'
         f'"-",SUMIFS({cal_m},{d_m},">="&TODAY()-6,{d_m},"<="&TODAY())/'
         f'MAX(1,{distinct_in(d_m, f"({d_m}>=TODAY()-6)*({d_m}<=TODAY())")}))',
         "int", "logged days only"),
        ("Goal progress",
         '=IF(COUNT(GoalProgress)=0,"-",AVERAGE(GoalProgress))',
         "percent0", "mean of your six goals"),
    ]
    col = 0
    for i, (label, formula, style, note) in enumerate(tiles):
        sheet.kpi(row, col, label, formula, style=style, span=3, note=note)
        col += 3
        if i == 3:
            col = 0
            row += 3
    row += 4

    row = sheet.section(row, "GOAL PROGRESS", last_col)
    for g in range(6):
        gr = f"INDEX(GoalTypes,{g + 1})"
        sheet.formula(row, 0,
                      f'=IF({gr}="","",{gr}&": "&INDEX(GoalDescs,{g + 1}))',
                      sheet.f.calc("text"))
        sheet.formula(row, 3,
                      f'=IF(INDEX(GoalProgress,{g + 1})="","",REPT("|",'
                      f'MIN(20,INT(MAX(0,INDEX(GoalProgress,{g + 1}))*20)))'
                      f'&" "&TEXT(MAX(0,INDEX(GoalProgress,{g + 1})),"0%")'
                      f'&IF(INDEX(GoalToGo,{g + 1})="","","  ("&TEXT('
                      f'INDEX(GoalToGo,{g + 1}),"0.##")&" to go)"))',
                      sheet.f.calc("text"))
        sheet.formula(row, 9, f'=INDEX(GoalStatus,{g + 1})',
                      sheet.f.calc("status"))
        row += 1
    row += 1

    row = sheet.section(row, "THIS WEEK VS LAST WEEK", last_col)
    row = sheet.table_head(row, 0, ["", "This week", "Last week",
                                    "Difference"],
                           widths=[30, 12, 12, 12])
    compare = [
        ("Sessions logged",
         f'SUMPRODUCT(({w_log}={ws_this})/((COUNTIFS({w_log},{w_log},'
         f'{s_log},{s_log})+({s_log}=""))))',
         f'SUMPRODUCT(({w_log}={ws_last})/((COUNTIFS({w_log},{w_log},'
         f'{s_log},{s_log})+({s_log}=""))))', "number1"),
        ("Training minutes",
         f'SUMIFS({dur_log},{w_log},{ws_this})',
         f'SUMIFS({dur_log},{w_log},{ws_last})', "int"),
        ("Calories logged",
         f'SUMIFS({cal_m},{d_m},">="&{ws_this},{d_m},"<="&{ws_this}+6)',
         f'SUMIFS({cal_m},{d_m},">="&{ws_last},{d_m},"<="&{ws_last}+6)',
         "int"),
        ("Water (ml)",
         f'SUMIFS({tot_s},{d_s},">="&{ws_this},{d_s},"<="&{ws_this}+6)',
         f'SUMIFS({tot_s},{d_s},">="&{ws_last},{d_s},"<="&{ws_last}+6)',
         "int"),
        ("Sleep (hours, avg)",
         f'IFERROR(AVERAGEIFS({hrs_s},{d_s},">="&{ws_this},{d_s},"<="&'
         f'{ws_this}+6,{hrs_s},">0"),"")',
         f'IFERROR(AVERAGEIFS({hrs_s},{d_s},">="&{ws_last},{d_s},"<="&'
         f'{ws_last}+6,{hrs_s},">0"),"")', "number1"),
        ("Mobility minutes",
         f'SUMIFS({mob_s},{d_s},">="&{ws_this},{d_s},"<="&{ws_this}+6)',
         f'SUMIFS({mob_s},{d_s},">="&{ws_last},{d_s},"<="&{ws_last}+6)',
         "int"),
    ]
    for label, this_f, last_f, style in compare:
        sheet.write(row, 0, label, sheet.f.calc("text"))
        sheet.formula(row, 1, "=" + this_f, sheet.f.calc(style))
        sheet.formula(row, 2, "=" + last_f, sheet.f.calc(style))
        sheet.formula(row, 3,
                      f'=IF(OR(B{row + 1}="",C{row + 1}="","",0),'
                      f'"",B{row + 1}-C{row + 1})'.replace(",\"\",0)",
                                                          ")"),
                      sheet.f.calc(style))
        row += 1
    row += 1

    row = sheet.section(row, "WEIGHT TREND", last_col)
    # The sparkline must live in a cell of its own: a sparkline (or any
    # content) inside a merged range that it does not anchor makes Excel
    # strip the part's formula records on open.
    spark_cell = f"$D${row + 2}"
    sheet.set_col(3, 3, 36)
    sheet.merge(row, 0, 2, "7-day average, oldest to newest:",
                sheet.f.chrome("label_bold"))
    sheet.merge(row + 1, 0, 2, "", sheet.f.chrome("label"))
    sheet.write(row + 1, 3, None, sheet.f.cell("text", "calc"))
    sheet.ws.add_sparkline(spark_cell, {
        "range": f"{qw}!${wt.letter('ma7')}${wt.first_data_row}:"
                 f"${wt.letter('ma7')}${wt.last_data_row}",
        "type": "line", "plot_hidden": True,
        "empty_cells": "gaps", "markers": True,
        "series_color": "#14655A",
    })
    sheet.formula(row, 6,
                  f'=IF(COUNT({kg_w})=0,"No weigh-ins yet - the line '
                  f'appears with your second entry.",REPT("|",MIN(20,'
                  f'COUNT({kg_w})/10))&" "&COUNT({kg_w})&" weigh-ins '
                  f'logged")',
                  sheet.f.calc("text"))
    row += 3

    row = sheet.section(row, "WHAT TO DO NEXT", last_col)
    sheet.formula(row, 0,
                  f'=IF(COUNTA({d_log})=0,"Open 2 Profile & Goals and type '
                  f'your starting weight - everything else grows from '
                  f'that.",IF(MAX({date_w})<TODAY()-7,"You have not '
                  f'weighed in for a week - one number, same time of '
                  f'day.",IF(SUMPRODUCT(({w_log}={ws_this})/((COUNTIFS('
                  f'{w_log},{w_log},{s_log},{s_log})+({s_log}=""))))<'
                  f'SessionsPerWeek AND WEEKDAY(TODAY(),2)>=5,"Sessions '
                  f'left in this week - plan them on tab 4.",IF(SUMIFS('
                  f'{tot_s},{d_s},TODAY())=0,"Log today\'s water on tab '
                  f'12.","Everything is logged - write the week up on '
                  f'tab 14."))))',
                  sheet.f.chrome("note_box"))
    sheet.row_height(row, 30)
    row += 2
    C.footer(sheet, cfg, last_col, row)
    sheet.finish(freeze_row=3, gridlines=False)
    return sheet
