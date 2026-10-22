"""18 Business Analytics - retention, popularity and trends."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import Config, BOOKING_CHANNELS
from ..writer import SheetWriter
from . import common as C

NAME = "18 Business Analytics"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color="#96587A", landscape=False)
    last = 9
    sheet.banner("18  Business Analytics",
                 "Who comes back, what sells, who earns it - the patterns "
                 "behind the month.", last)
    row = 4
    row = sheet.section(row, "RETENTION", last)
    tiles = [
        ("Repeat-client rate",
         '=IF(COUNTIFS(ClientVisits,">=1")=0,"-",COUNTIFS(ClientVisits,'
         '">1")/COUNTIFS(ClientVisits,">=1"))', "percent0",
         "clients with 2+ visits"),
        ("Active clients", '=COUNTIFS(ClientStatus,"Active")', "int",
         "inside rebooking window"),
        ("Lapsed clients", '=COUNTIFS(ClientStatus,"Lapsed")', "int",
         "your win-back list"),
        ("New clients (30d)",
         f'=SUMPRODUCT(({C.ym_mask("ClientFirst", C.cur_ym())}))',
         "int", "first visits this month"),
        ("Avg visits per client",
         '=IF(COUNTIFS(ClientVisits,">=1")=0,"-",ROUND(SUM(ClientVisits)/'
         'COUNTIFS(ClientVisits,">=1"),1))', "number1", "recorded visits"),
        ("Retail attach rate",
         '=IF(SUM(ApptDone)=0,"-",COUNTIFS(SalesType,"Retail")/'
         'SUM(ApptDone))', "percent0", "retail lines per completed visit"),
    ]
    col = 0
    for i, (label, formula, style, note) in enumerate(tiles):
        sheet.kpi(row, col, label, formula, style=style, span=3, note=note)
        col += 5
        if i % 2 == 1:
            col = 0
            row += 3
    row += 1

    row = sheet.section(row, "NEW CLIENTS BY SOURCE", last)
    sheet.table_head(row, 0, ["Channel", "New clients", "Share"])
    for i, ch in enumerate(BOOKING_CHANNELS):
        r = row + 1 + i
        sheet.write(r, 0, ch, sheet.f.calc("text"))
        sheet.formula(r, 1, f'=COUNTIFS(ClientSource,$A{r})',
                      sheet.f.calc("int"))
        sheet.formula(r, 2, f'=IF(SUM($B${row + 1}:$B${row + len(BOOKING_CHANNELS)})=0,"",$B{r}/SUM($B${row + 1}:$B${row + len(BOOKING_CHANNELS)}))',
                      sheet.f.calc("percent0"))
    row += len(BOOKING_CHANNELS) + 2

    row = sheet.section(row, "SERVICE POPULARITY - TOP TEN", last)
    sheet.table_head(row, 0, ["Rank", "Service", "Times sold", "Revenue",
                              "Share of revenue"])
    for i in range(10):
        r = row + 1 + i
        sheet.write(r, 0, i + 1, sheet.f.calc("int"))
        sheet.formula(r, 1, f'=IFERROR(INDEX(ServiceNames,MATCH({i + 1},'
                            f'ServiceRank,0)),"-")', sheet.f.calc("text"))
        sheet.formula(r, 2, f'=IF($B{r}="-","",IFERROR(INDEX(ServiceSold,'
                            f'MATCH($B{r},ServiceNames,0)),""))',
                      sheet.f.calc("int"))
        sheet.formula(r, 3, f'=IF($B{r}="-","",IFERROR(INDEX(RevenueAll,'
                            f'MATCH($B{r},ServiceNames,0)),""))',
                      sheet.f.calc("money"))
        sheet.formula(r, 4, f'=IF(OR($B{r}="-",SUM(RevenueAll)=0),"",'
                            f'$D{r}/SUM(RevenueAll))',
                      sheet.f.calc("percent0"))
    row += 12

    row = sheet.section(row, "BOOKING OUTCOMES", last)
    sheet.table_head(row, 0, ["Status", "Count", "Share of finalised"])
    statuses = ["Completed", "Cancelled", "No-show", "Booked", "Confirmed"]
    for i, st in enumerate(statuses):
        r = row + 1 + i
        sheet.write(r, 0, st, sheet.f.calc("text"))
        sheet.formula(r, 1, f'=COUNTIFS(ApptStatus,$A{r})',
                      sheet.f.calc("int"))
        sheet.formula(r, 2,
                      f'=IF($A{r}="Booked",IF(SUM(ApptDone)+COUNTIFS('
                      f'ApptStatus,"Cancelled")+COUNTIFS(ApptStatus,'
                      f'"No-show")=0,"","open"),IF(SUM(ApptDone)+'
                      f'COUNTIFS(ApptStatus,"Cancelled")+COUNTIFS('
                      f'ApptStatus,"No-show")=0,"",$B{r}/(SUM(ApptDone)+'
                      f'COUNTIFS(ApptStatus,"Cancelled")+COUNTIFS('
                      f'ApptStatus,"No-show"))))',
                      sheet.f.calc("percent0"))
    row += len(statuses) + 2

    row = sheet.section(row, "TWELVE-MONTH CLIENT & REVENUE TREND", last)
    sheet.table_head(row, 0, ["Month", "New clients", "Revenue",
                              "Appointments"])
    for k in range(12):
        r = row + 1 + k
        ym = f'TEXT(EDATE(TODAY(),-{11 - k}),"yyyy-mm")'
        sheet.formula(r, 0, f'={ym}', sheet.f.calc("text"))
        sheet.formula(r, 1, f'=SUMPRODUCT('
                            f'{C.ym_mask("ClientFirst", f"$A{r}")})',
                      sheet.f.calc("int"))
        sheet.formula(r, 2, f'=ROUND(SUMPRODUCT('
                            f'{C.ym_mask("SalesDates", f"$A{r}")}'
                            f'*SalesNet),2)', sheet.f.calc("money"))
        sheet.formula(r, 3, f'=SUMPRODUCT('
                            f'{C.ym_mask("ApptDates", f"$A{r}")}*ApptDone)',
                      sheet.f.calc("int"))
    row += 14
    C.footer(sheet, cfg, last, row)
    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
