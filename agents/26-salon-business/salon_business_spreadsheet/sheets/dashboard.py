"""2 Dashboard - the salon's morning page."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import Config, Palette
from ..writer import SheetWriter
from . import common as C

NAME = "2 Dashboard"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.accent, landscape=False)
    last = 11
    sheet.banner("2  Dashboard",
                 "Revenue, profit, bookings, balances and stock - every "
                 "tile reads the registers live.", last)
    cur, prv = C.cur_ym(), C.prev_ym()
    m_sales = f'SUMPRODUCT({C.ym_mask("SalesDates", cur)}*SalesNet)'
    m_sales_p = f'SUMPRODUCT({C.ym_mask("SalesDates", prv)}*SalesNet)'
    m_exp = f'SUMPRODUCT({C.ym_mask("ExpDates", cur)}*ExpAmount)'
    m_appt = f'SUMPRODUCT({C.ym_mask("ApptDates", cur)}*ApptDone)'

    row = 4
    row = sheet.section(row, "THIS MONTH", last)
    tiles = [
        ("Revenue", f'=ROUND({m_sales},2)', "money", "net of discounts, "
         "refunds and tax"),
        ("Operating expenses", f'=ROUND({m_exp},2)', "money",
         "tab 11, this month"),
        ("Operating profit", f'=ROUND({m_sales}-{m_exp},2)', "money",
         "before payroll - see P&L"),
        ("Appointments done", f'={m_appt}', "int", "completed visits"),
        ("Average ticket", f'=IF({m_appt}=0,"-",ROUND(SUMPRODUCT('
         f'{C.ym_mask("SalesDates", cur)}*(SalesType="Service")'
         f'*SalesNet)/{m_appt},2))', "money", "service revenue per visit"),
        ("Outstanding balances", '=ROUND(SUM(SalesBalance),2)', "money",
         "owed by clients right now"),
        ("Unearned deposits", '=ROUND(SUMIFS(PayAmount,PayKind,'
         '"Deposit",PayLinkStatus,"<>Completed"),2)', "money",
         "held, not yet revenue"),
        ("No-show rate", '=IF(COUNTIFS(ApptStatus,"Completed")'
         '+COUNTIFS(ApptStatus,"Cancelled")+COUNTIFS(ApptStatus,'
         '"No-show")=0,"-",COUNTIFS(ApptStatus,"No-show")/'
         '(COUNTIFS(ApptStatus,"Completed")+COUNTIFS(ApptStatus,'
         '"Cancelled")+COUNTIFS(ApptStatus,"No-show")))', "percent0",
         "of finalised bookings"),
        ("Cancellation rate", '=IF(COUNTIFS(ApptStatus,"Completed")'
         '+COUNTIFS(ApptStatus,"Cancelled")+COUNTIFS(ApptStatus,'
         '"No-show")=0,"-",COUNTIFS(ApptStatus,"Cancelled")/'
         '(COUNTIFS(ApptStatus,"Completed")+COUNTIFS(ApptStatus,'
         '"Cancelled")+COUNTIFS(ApptStatus,"No-show")))', "percent0",
         "of finalised bookings"),
        ("Repeat-client rate", '=IF(COUNTIFS(ClientVisits,">=1")=0,"-",'
         'COUNTIFS(ClientVisits,">1")/COUNTIFS(ClientVisits,">=1"))',
         "percent0", "clients with more than one visit"),
        ("Active clients", '=COUNTIFS(ClientStatus,"Active")', "int",
         "inside the rebooking window"),
        ("Reorder alerts", '=COUNTIF(InvLow,"REORDER")', "int",
         "products at or below minimum"),
    ]
    col = 0
    for i, (label, formula, style, note) in enumerate(tiles):
        sheet.kpi(row, col, label, formula, style=style, span=3, note=note)
        col += 3
        if i % 4 == 3:
            col = 0
            row += 3
    row += 1

    row = sheet.section(row, "MONTH VERSUS MONTH", last)
    heads = ["", "This month", "Last month", "Change"]
    sheet.table_head(row, 0, heads)
    pairs = [
        ("Revenue", m_sales, m_sales_p),
        ("Completed appointments", m_appt,
         f'SUMPRODUCT({C.ym_mask("ApptDates", prv)}*ApptDone)'),
        ("Expenses", m_exp,
         f'SUMPRODUCT({C.ym_mask("ExpDates", prv)}*ExpAmount)'),
    ]
    for i, (label, a, b) in enumerate(pairs):
        r = row + 1 + i
        sheet.write(r, 0, label, sheet.f.calc("text"))
        sheet.formula(r, 1, f'=ROUND({a},2)', sheet.f.calc("money"))
        sheet.formula(r, 2, f'=ROUND({b},2)', sheet.f.calc("money"))
        sheet.formula(r, 3, f'=IF($C{r}="","",ROUND($B{r}-$C{r},2))',
                      sheet.f.calc("money"))
    row += len(pairs) + 2

    row = sheet.section(row, "TWELVE-MONTH TREND", last)
    sheet.table_head(row, 0, ["Month", "Revenue", "Expenses", "Profit",
                              "Appts done"])
    trend_first = row + 1
    for k in range(12):
        r = trend_first + k
        ym = f'TEXT(EDATE(TODAY(),-{11 - k}),"yyyy-mm")'
        sheet.formula(r, 0, f'={ym}', sheet.f.calc("text"))
        sheet.formula(r, 1, f'=ROUND(SUMPRODUCT('
                            f'{C.ym_mask("SalesDates", f"$A{r}")}'
                            '*SalesNet),2)', sheet.f.calc("money"))
        sheet.formula(r, 2, f'=ROUND(SUMPRODUCT('
                            f'{C.ym_mask("ExpDates", f"$A{r}")}'
                            '*ExpAmount),2)', sheet.f.calc("money"))
        sheet.formula(r, 3, f'=IF($B{r}="","",ROUND($B{r}-$C{r},2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 4, f'=SUMPRODUCT('
                            f'{C.ym_mask("ApptDates", f"$A{r}")}*ApptDone)',
                      sheet.f.calc("int"))
    trend_last = trend_first + 11
    row = trend_last + 2

    row = sheet.section(row, "TOP SERVICES BY REVENUE", last)
    sheet.table_head(row, 0, ["#", "Service", "Times sold", "Revenue"])
    for i in range(5):
        r = row + 1 + i
        sheet.write(r, 0, i + 1, sheet.f.calc("int"))
        sheet.formula(r, 1, f'=IFERROR(INDEX(ServiceNames,MATCH({i + 1},'
                            'ServiceRank,0)),"-")', sheet.f.calc("text"))
        sheet.formula(r, 2, f'=IF($B{r}="-","",IFERROR(INDEX(ServiceSold,'
                            f'MATCH($B{r},ServiceNames,0)),""))',
                      sheet.f.calc("int"))
        sheet.formula(r, 3, f'=IF($B{r}="-","",IFERROR(INDEX(RevenueAll,'
                            f'MATCH($B{r},ServiceNames,0)),""))',
                      sheet.f.calc("money"))
    top_last = row + 5
    row = top_last + 2

    row = sheet.section(row, "REVENUE BY CATEGORY & BY STAFF", last)
    sheet.table_head(row, 0, ["Category", "Revenue", "", "Staff",
                              "Revenue"])
    from ..config import SERVICE_CATEGORIES
    for i, cat in enumerate(SERVICE_CATEGORIES):
        r = row + 1 + i
        sheet.write(r, 0, cat, sheet.f.calc("text"))
        sheet.formula(r, 1, f'=ROUND(SUMPRODUCT((SalesCat=$A{r})'
                            '*SalesNet),2)', sheet.f.calc("money"))
        sheet.formula(r, 3, f'=IFERROR(INDEX(StaffNames,{i + 1}),"")',
                      sheet.f.calc("text"))
        sheet.formula(r, 4, f'=IF($D{r}="","",ROUND(SUMIFS(SalesNet,'
                            f'SalesStaff,$D{r}),2))', sheet.f.calc("money"))
    cat_last = row + len(SERVICE_CATEGORIES)
    row = cat_last + 2

    row = sheet.section(row, "WHAT TO DO NEXT", last)
    sheet.formula(row, 0,
                  '=IF(COUNTIFS(ClientStatus,"?*")=0,"Open tab 20 and set '
                  'your rates, then add staff, services and clients.",'
                  'IF(COUNTIF(InvLow,"REORDER")>0,"REORDER: "&'
                  'COUNTIF(InvLow,"REORDER")&" product(s) at or below '
                  'minimum - tab 13.",IF(SUM(SalesBalance)>0,"Chase "&'
                  'TEXT(SUM(SalesBalance),"0.00")&" of outstanding '
                  f'balances - tab 6.",IF({m_appt}=0,"No completed '
                  'appointments this month yet - plan the week on tab 3."'
                  ',"Everything is logged - write the month up on tab '
                  '19."))))',
                  sheet.f.chrome("note_box"))
    sheet.merge(row, 1, last, "", sheet.f.chrome("note_box"))
    sheet.row_height(row, 30)
    row += 2
    C.footer(sheet, cfg, last, row)

    # native charts ---------------------------------------------------------
    chart = book.add_chart({"type": "column"})
    chart.add_series({
        "name": "Revenue",
        "categories": f"={_q(NAME)}!$A${trend_first}:$A${trend_last}",
        "values": f"={_q(NAME)}!$B${trend_first}:$B${trend_last}",
        "fill": {"color": "#6D2E4F"},
    })
    chart.add_series({
        "name": "Expenses",
        "categories": f"={_q(NAME)}!$A${trend_first}:$A${trend_last}",
        "values": f"={_q(NAME)}!$C${trend_first}:$C${trend_last}",
        "fill": {"color": "#B98A2F"},
    })
    chart.set_title({"name": "Revenue vs expenses by month"})
    chart.set_size({"width": 560, "height": 300})
    chart.set_legend({"position": "bottom"})
    sheet.ws.insert_chart(trend_first - 1, 6, chart)

    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet


def _q(name: str) -> str:
    from ..layout import quote_sheet
    return quote_sheet(name)
