"""19 Weekly & Monthly Reports - the owner's review page."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import Config
from ..writer import SheetWriter
from . import common as C

NAME = "19 Weekly & Monthly Reports"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color="#B98A2F", landscape=False)
    last = 7
    sheet.banner("19  Weekly & Monthly Reports",
                 "Sunday, ten minutes: what happened, what it means, "
                 "what you will do about it.", last)
    ws = C.week_start_of("TODAY()")
    row = 4
    row = sheet.section(row, "THIS WEEK VS LAST WEEK", last)
    sheet.table_head(row, 0, ["Measure", "This week", "Last week",
                              "Change"])
    wk = [
        ("Revenue",
         f'SUMIFS(SalesNet,SalesDates,">="&{ws},SalesDates,"<="&TODAY())',
         f'SUMIFS(SalesNet,SalesDates,">="&{ws}-7,SalesDates,"<"&{ws})'),
        ("Appointments completed",
         f'SUMIFS(ApptDone,ApptDates,">="&{ws},ApptDates,"<="&TODAY())',
         f'SUMIFS(ApptDone,ApptDates,">="&{ws}-7,ApptDates,"<"&{ws})'),
        ("No-shows",
         f'SUMPRODUCT((ApptDates>={ws})*(ApptDates<=TODAY())*'
         '(ApptStatus="No-show"))',
         f'SUMPRODUCT((ApptDates>={ws}-7)*(ApptDates<{ws})*'
         '(ApptStatus="No-show"))'),
        ("Retail lines",
         f'SUMPRODUCT((SalesDates>={ws})*(SalesDates<=TODAY())*'
         '(SalesType="Retail"))',
         f'SUMPRODUCT((SalesDates>={ws}-7)*(SalesDates<{ws})*'
         '(SalesType="Retail"))'),
    ]
    for i, (label, a, b) in enumerate(wk):
        r = row + 1 + i
        sheet.write(r, 0, label, sheet.f.calc("text"))
        sheet.formula(r, 1, f'=ROUND({a},2)', sheet.f.calc("number1"))
        sheet.formula(r, 2, f'=ROUND({b},2)', sheet.f.calc("number1"))
        sheet.formula(r, 3, f'=ROUND($B{r}-$C{r},2)',
                      sheet.f.calc("number1"))
    row += len(wk) + 2

    row = sheet.section(row, "THIS MONTH IN ONE BREATH", last)
    cur = C.cur_ym()
    lines = [
        ("Revenue", f'=ROUND(SUMPRODUCT('
                    f'{C.ym_mask("SalesDates", cur)}*SalesNet),2)',
         "money"),
        ("Operating expenses", f'=ROUND(SUMPRODUCT('
                               f'{C.ym_mask("ExpDates", cur)}*ExpAmount),2)',
         "money"),
        ("Payroll cost", f'=ROUND(SUMPRODUCT('
                         f'{C.ym_mask("PayrollDates", cur)}*PayrollCost),2)',
         "money"),
        ("Best service", '=IFERROR(INDEX(ServiceNames,MATCH(1,'
                         'ServiceRank,0)),"-")', "text"),
        ("Top earner", '=IFERROR(INDEX(StaffNames,MATCH(MAX(StaffRevenue),'
                       'StaffRevenue,0)),"-")', "text"),
        ("Rebook reminders due", '=SUMPRODUCT((ApptFollow<>"")*'
         '(ApptFollow<=TODAY()))', "int"),
    ]
    for i, (label, formula, style) in enumerate(lines):
        r = row + i
        sheet.write(r, 0, label, sheet.f.calc("text", bold=True))
        sheet.formula(r, 1, formula, sheet.f.calc(style))
    row += len(lines) + 1

    row = sheet.section(row, "OWNER ACTION PLAN - TYPE HERE", last)
    prompts = [
        "What worked this month and deserves more of your calendar?",
        "Which service or slot under-earned - reprice, retime or retire?",
        "Who is lapsed or overdue a rebooking - call list for Monday?",
        "What will you reorder, repair or renegotiate?",
        "Which number will you move next month, and by how much?",
        "One thing to stop doing completely:",
    ]
    for i, p in enumerate(prompts):
        sheet.merge(row, 0, last, p, sheet.f.chrome("subsection"))
        row += 1
        sheet.merge(row, 0, last, None, sheet.f.input("wrap"))
        sheet.row_height(row, 34)
        row += 1
    row += 1
    row = sheet.note(row,
                     "Print this page for the monthly review - the print "
                     "area is set. Numbers above update themselves; the "
                     "plan is yours.", last) + 2
    C.footer(sheet, cfg, last, row)
    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
