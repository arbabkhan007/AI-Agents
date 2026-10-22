"""9 Staff Commissions - statements per person, method aware."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import Config
from ..writer import SheetWriter
from . import common as C

NAME = "9 Staff Commissions"
STAFF_ROWS = 12


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color="#96587A", landscape=False)
    last = 10
    sheet.banner("9  Staff Commissions",
                 "One statement per person - service commission at the "
                 "applicable rate, retail commission, tips and "
                 "adjustments.", last)
    row = 4
    row = sheet.section(row, "HOW EACH METHOD PAYS", last)
    for line in [
        "Percentage - the staff member's own service % and retail % from "
        "tab 8.",
        "Category - the category rate table on tab 20 applies per sale, "
        "so hair and lashes can pay differently.",
        "Flat - a fixed amount per completed appointment (Settings), "
        "plus their retail %.",
        "Tips are reported from tab 10; adjustments are yours to type "
        "with an approval note.",
    ]:
        row = sheet.note(row, line, last) + 1
    row += 1

    row = sheet.section(row, "COMMISSION STATEMENTS", last)
    sheet.table_head(row, 0, ["Staff", "Method", "Service revenue",
                              "Retail revenue", "Service commission",
                              "Retail commission", "Flat element",
                              "Tips paid out", "Adjustment", "Total due",
                              "Approved by / notes"])
    first = row + 1
    for i in range(STAFF_ROWS):
        r = first + i
        sheet.formula(r, 0, f'=IFERROR(INDEX(StaffNames,{i + 1}),"")',
                      sheet.f.calc("text", bold=True))
        sheet.formula(r, 1, f'=IF($A{r}="","",IFERROR(INDEX(StaffMethod,'
                            f'MATCH($A{r},StaffNames,0)),""))',
                      sheet.f.calc("text"))
        sheet.formula(r, 2, f'=IF($A{r}="","",ROUND(SUMIFS(SalesNet,'
                            f'SalesStaff,$A{r},SalesType,"Service"),2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 3, f'=IF($A{r}="","",ROUND(SUMIFS(SalesNet,'
                            f'SalesStaff,$A{r},SalesType,"Retail"),2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 4, f'=IF($A{r}="","",ROUND(SUMPRODUCT('
                            f'(SalesStaff=$A{r})*(SalesType="Service")'
                            f'*SalesNet*SalesRate),2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 5, f'=IF($A{r}="","",ROUND(IFERROR(INDEX('
                            f'StaffRetRate,MATCH($A{r},StaffNames,0)),0)'
                            f'*SUMPRODUCT((SalesStaff=$A{r})*'
                            f'(SalesType="Retail")*SalesNet),2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 6, f'=IF($A{r}="","",IF($B{r}="Flat",'
                            f'FlatCommission*COUNTIFS(ApptStaff,$A{r},'
                            f'ApptStatus,"Completed"),0))',
                      sheet.f.calc("money"))
        sheet.formula(r, 7, f'=IF($A{r}="","",ROUND(SUMIFS(PayrollTipsOut,'
                            f'PayrollStaff,$A{r}),2))',
                      sheet.f.calc("money"))
        sheet.write(r, 8, None, sheet.f.input("money"))
        sheet.formula(r, 9, f'=IF($A{r}="","",ROUND(N($E{r})+N($F{r})'
                            f'+N($G{r})+N($I{r}),2))',
                      sheet.f.calc("money", bold=True))
        sheet.write(r, 10, None, sheet.f.input("wrap"))
    tot = first + STAFF_ROWS
    sheet.write(tot, 0, "TOTAL", sheet.f.chrome("total_label"))
    for c in (2, 3, 4, 5, 6, 7, 8, 9):
        letter = xl_col_to_name(c)
        sheet.formula(tot, c,
                      f'=ROUND(SUM({letter}${first}:{letter}'
                      f'${first + STAFF_ROWS - 1}),2)',
                      sheet.f.chrome("total_value",
                                     num_format=sheet.num_format("money")))
    row = tot + 2
    row = sheet.section(row, "PAYOUT SUMMARY", last)
    sheet.formula(row, 0,
                  f'=IF(SUM($J${first}:$J${first + STAFF_ROWS - 1})=0,'
                  f'"No commissions yet - log completed sales on tab 6.",'
                  f'"Total commission due this period: "&TEXT(SUM($J$'
                  f'{first}:$J${first + STAFF_ROWS - 1}),"#,##0.00")&'
                  f'" across "&COUNTIF($A${first}:$A${first + STAFF_ROWS - 1}'
                  f',"?*")&" staff.")',
                  sheet.f.chrome("note_box"))
    sheet.merge(row, 1, last, "", sheet.f.chrome("note_box"))
    row += 2
    C.footer(sheet, cfg, last, row)
    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
