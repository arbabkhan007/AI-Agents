"""`Annual Reports` - the year, and the shape of the season.

Twelve months across, the things worth comparing down the side. The
seasonal curve is the point: a landscaping business earns most of its
money in about seven months and pays wages for twelve, and seeing
that written down changes how you price the busy months.
"""

from __future__ import annotations

from ..config import MONTH_NAMES, Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Annual Reports"
LAST_COL = 14
LIST_ROWS = 10


def _key(n: int) -> str:
    """The yyyy-mm key for month n of the reporting year."""
    return f'TEXT(DATE(ReportYear,{n},1),"yyyy-mm")'


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.deep)

    s.banner("Annual Reports",
             "Twelve months side by side - where the money came "
             "from, when it came, and what it cost to earn.",
             LAST_COL)
    s.set_col(0, 0, 26)
    for column in range(1, 13):
        s.set_col(column, column, 11)
    s.set_col(13, LAST_COL, 14)

    row = 4
    s.merge(row, 0, 0, "Reporting year", fmts.chrome("label_bold"))
    s.formula(row, 1, "=ReportYear", fmts.calc("int"))
    s.merge(row, 2, 3, "Change it on Settings & Lists",
            fmts.chrome("note"))
    s.merge(row, 4, LAST_COL, None, fmts.chrome("note"))
    s.formula(row, 4,
              '="Season: months "&SeasonStart&" to "&SeasonEnd&'
              '".  Target for the year: "&TEXT(RevenueTarget,'
              '"#,##0")', fmts.chrome("note"))
    row += 2

    # ------------------------------------------------- the month grid --
    row = s.section(row, "Month by month", LAST_COL)
    s.table_head(row, 0, [""] + list(MONTH_NAMES) + ["Year"],
                 widths=[26] + [11] * 12 + [14])
    head = row

    def line(offset: int, label: str, formula_for, style: str,
             total: str = "sum", note: str = ""):
        """One row of the grid: twelve months, then a year column."""
        r = head + offset
        s.write(r, 0, label, fmts.chrome("label_bold"))
        for n in range(1, 13):
            s.formula(r, n, "=" + formula_for(n), fmts.calc(style))
        letters = [chr(ord("B") + i) for i in range(12)]
        span = f"B{r + 1}:M{r + 1}"
        if total == "sum":
            s.formula(r, 13, f"=SUM({span})", fmts.calc(style))
        elif total == "avg":
            s.formula(r, 13, f'=IFERROR(AVERAGE({span}),"")',
                      fmts.calc(style))
        else:
            s.formula(r, 13, "=" + total, fmts.calc(style))
        del letters
        return r

    offset = 1
    line(offset, "Visits completed",
         lambda n: f'COUNTIFS(JobMonth,{_key(n)},JobIsDone,1)', "int")
    offset += 1
    line(offset, "Revenue",
         lambda n: (f'SUMIFS(JobCharge,JobMonth,{_key(n)},JobIsDone,1)'
                    f'+SUMIFS(JobExtras,JobMonth,{_key(n)},'
                    'JobIsDone,1)'), "money")
    revenue_row = head + offset
    offset += 1
    line(offset, "Labour cost",
         lambda n: f'SUMIFS(TimeCost,TimeMonth,{_key(n)})+SUMIFS(JobLabourFallback,JobMonth,{_key(n)})', "money")
    labour_row = head + offset
    offset += 1
    line(offset, "Materials and expenses",
         lambda n: f'SUMIFS(ExpPeriodCost,ExpMonth,{_key(n)})', "money")
    expense_row = head + offset
    offset += 1
    line(offset, "Fuel and vehicles",
         lambda n: f'SUMIFS(VehAmount,VehMonth,{_key(n)})', "money")
    fuel_row = head + offset
    offset += 1
    line(offset, "Profit",
         lambda n: (f'SUMIFS(JobCharge,JobMonth,{_key(n)},JobIsDone,1)'
                    f'+SUMIFS(JobExtras,JobMonth,{_key(n)},JobIsDone,1)'
                    f'-SUMIFS(TimeCost,TimeMonth,{_key(n)})-SUMIFS(JobLabourFallback,JobMonth,{_key(n)})'
                    f'-SUMIFS(ExpPeriodCost,ExpMonth,{_key(n)})'
                    f'-SUMIFS(VehAmount,VehMonth,{_key(n)})'),
         "money")
    profit_row = head + offset
    offset += 1
    r = head + offset
    s.write(r, 0, "Margin", fmts.chrome("label_bold"))
    for n in range(1, 13):
        col = chr(ord("B") + n - 1)
        s.formula(r, n,
                  f'=IFERROR({col}{profit_row + 1}/'
                  f'{col}{revenue_row + 1},"")', fmts.calc("percent"))
    s.formula(r, 13,
              f'=IFERROR(N{profit_row + 1}/N{revenue_row + 1},"")',
              fmts.calc("percent"))
    s.cf(f"B{r + 1}:N{r + 1}",
         {"type": "cell", "criteria": "<", "value": 0,
          "format": fmts.cf("bad")})
    offset += 1
    line(offset, "Crew hours",
         lambda n: f'SUMIFS(TimeHours,TimeMonth,{_key(n)})',
         "number1")
    hours_row = head + offset
    offset += 1
    r = head + offset
    s.write(r, 0, "Profit per crew hour", fmts.chrome("label_bold"))
    for n in range(1, 13):
        col = chr(ord("B") + n - 1)
        s.formula(r, n,
                  f'=IFERROR({col}{profit_row + 1}/'
                  f'{col}{hours_row + 1},"")', fmts.calc("money"))
    s.formula(r, 13,
              f'=IFERROR(N{profit_row + 1}/N{hours_row + 1},"")',
              fmts.calc("money"))
    offset += 1
    line(offset, "Invoiced",
         lambda n: f'SUMIFS(InvTotal,InvMonth,{_key(n)})', "money")
    offset += 1
    line(offset, "Collected",
         lambda n: f'SUMIFS(InvPaid,InvPaidDate,">="&DATE(ReportYear,{n},1),InvPaidDate,"<"&DATE(ReportYear,{n}+1,1))', "money")
    offset += 1
    line(offset, "Quotes sent",
         lambda n: f'COUNTIFS(QuoteMonth,{_key(n)})', "int")
    offset += 1
    line(offset, "Quotes won",
         lambda n: f'COUNTIFS(QuoteMonth,{_key(n)},QuoteIsWon,1)',
         "int")
    offset += 1
    r = head + offset
    s.write(r, 0, "Share of the year", fmts.chrome("label_bold"))
    for n in range(1, 13):
        col = chr(ord("B") + n - 1)
        s.formula(r, n,
                  f'=IFERROR({col}{revenue_row + 1}/'
                  f'N{revenue_row + 1},"")', fmts.calc("percent"))
    s.formula(r, 13, '=IF(N%d=0,"",1)' % (revenue_row + 1),
              fmts.calc("percent"))
    s.cf(f"B{r + 1}:M{r + 1}",
         {"type": "data_bar", "bar_color": "#40916C"})
    del labour_row, expense_row, fuel_row
    row = head + offset + 2

    # ------------------------------------------------- the year's shape --
    row = s.section(row, "The year in one line", LAST_COL)
    s.kpi(row, 0, "Revenue",
          f'=N{revenue_row + 1}', "money")
    s.kpi(row, 2, "Profit", f'=N{profit_row + 1}', "money")
    s.kpi(row, 4, "Margin",
          f'=IFERROR(N{profit_row + 1}/N{revenue_row + 1},"")',
          "percent0")
    s.kpi(row, 6, "vs target",
          f'=IFERROR(N{revenue_row + 1}/RevenueTarget,"")',
          "percent0", note="Against the Settings target")
    s.kpi(row, 8, "Crew hours", f'=N{hours_row + 1}', "number1")
    s.kpi(row, 10, "Per crew hour",
          f'=IFERROR(N{profit_row + 1}/N{hours_row + 1},"")',
          "money")
    row = s.kpi(row, 12, "Customers", "=SUM(CustIsActive)", "int",
                span=2, note="Active on the CRM tab")
    row += 1

    # ---------------------------------------------- season comparison --
    row = s.section(row, "In season and out", LAST_COL)
    row = s.note(
        row,
        "Your season runs between the months set on Settings. The "
        "months outside it still cost you wages, insurance and yard "
        "rent, which is the argument for pricing the busy months "
        "properly rather than hoping winter pays for itself.",
        LAST_COL, height=32)
    row += 1
    in_season = ('(MONTH(JobDateNum)>=SeasonStart)*'
                 '(MONTH(JobDateNum)<=SeasonEnd)*'
                 '(YEAR(JobDateNum)=ReportYear)*JobIsDone')
    out_season = ('((MONTH(JobDateNum)<SeasonStart)+'
                  '(MONTH(JobDateNum)>SeasonEnd))*'
                  '(YEAR(JobDateNum)=ReportYear)*JobIsDone')
    s.kpi(row, 0, "In-season revenue",
          f'=SUMPRODUCT({in_season}*JobCharge)', "money")
    s.kpi(row, 2, "In-season visits",
          f'=SUMPRODUCT({in_season})', "int")
    s.kpi(row, 4, "Out-of-season revenue",
          f'=SUMPRODUCT({out_season}*JobCharge)', "money")
    s.kpi(row, 6, "Out-of-season visits",
          f'=SUMPRODUCT({out_season})', "int")
    s.kpi(row, 8, "Season share",
          f'=IFERROR(SUMPRODUCT({in_season}*JobCharge)/'
          f'N{revenue_row + 1},"")', "percent0")
    row = s.kpi(row, 10, "Recurring income",
                "=SUMPRODUCT(ConIsLive*ConAnnualValue)", "money",
                span=4,
                note="Annual value of every live contract - the part "
                     "you can plan on")
    row += 2

    # --------------------------------------------- best and worst work --
    row = s.section(row, "What earned, and what did not", LAST_COL)
    s.table_head(row, 0,
                 ["Service", "Visits", "Revenue", "Margin",
                  "Earns per hour", "Actual vs catalogue hours"],
                 widths=[30, 11, 13, 11, 14, 22])
    head = row
    for n in range(1, LIST_ROWS + 1):
        lr = head + n
        rank = f"ROW()-{head + 1}"
        base = (f'MATCH({rank},[[Service Catalog.revenue_rank]],0)')
        s.formula(lr, 0,
                  f'=IFERROR(INDEX([[Service Catalog.name]],{base}),'
                  '"")', fmts.calc("text"))
        s.formula(lr, 1,
                  '=IFERROR(INDEX([[Service Catalog.times_sold]],'
                  f'{base})*1,"")', fmts.calc("int"))
        s.formula(lr, 2,
                  '=IFERROR(INDEX([[Service Catalog.revenue]],'
                  f'{base})*1,"")', fmts.calc("money"))
        s.formula(lr, 3,
                  '=IFERROR(INDEX([[Service Catalog.margin_pct]],'
                  f'{base})*1,"")', fmts.calc("percent"))
        s.formula(lr, 4,
                  '=IFERROR(INDEX([[Service Catalog.per_hour]],'
                  f'{base})*1,"")', fmts.calc("money"))
        s.formula(lr, 5,
                  '=IFERROR(IF(INDEX('
                  f'[[Service Catalog.avg_actual]],{base})="","",'
                  'TEXT(INDEX([[Service Catalog.avg_actual]],'
                  f'{base}),"0.0")&" vs "&'
                  'TEXT(INDEX([[Service Catalog.hours_per_unit]],'
                  f'{base}),"0.0")),"")', fmts.calc("text"))
    row = head + LIST_ROWS + 2

    # --------------------------------------------------- the questions --
    row = s.section(row, "The questions a year of records can answer",
                    LAST_COL)
    row = s.bullets(row, [
        "Which month actually pays for the winter? Look at profit, "
        "not revenue - a busy June with thin margins pays for "
        "nothing.",
        "Is the recurring income growing? Contracts are the only "
        "part of a landscaping business you can plan on, and the "
        "number above is what a buyer would value.",
        "Which services earn their hours? The table above sorts by "
        "revenue; read the 'earns per hour' column instead, and "
        "then read the one next to it.",
        "Where did the catalogue times turn out to be wrong? Any "
        "service whose actual hours are consistently above the "
        "catalogue is underpriced, every single visit.",
        "How many customers were lost this year, and why? The "
        "Customer CRM and Customer Feedback tabs between them hold "
        "the answer, and it is almost never price.",
    ], LAST_COL, height=30)
    row += 1

    row = s.note(
        row,
        "This page reports the year set on the Settings tab. Change "
        "the reporting year there and every figure here moves with "
        "it, so last year's report is always one cell away.",
        LAST_COL, height=28)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
