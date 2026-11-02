"""`Monthly Reports` - one month, read properly.

Pick a month at the top and everything below it changes: the money,
the work, the crew, the customers who grew and the ones who went
quiet. It is the fifteen minutes at the end of a month that tells you
whether the last four weeks were worth doing.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Monthly Reports"
LAST_COL = 11
LIST_ROWS = 8


def _month_sum(name_range: str, month_range: str) -> str:
    return f"SUMIFS({name_range},{month_range},ReportMonth)"


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_mid)

    s.banner("Monthly Reports",
             "Pick a month. The whole page follows - money, work, "
             "crew, customers and what to do about them.",
             LAST_COL)
    s.set_col(0, 0, 26)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 14)

    row = 4
    row = s.field(row, "Month to report on", cfg.today.strftime("%Y-%m"), style="text",
                  name="ReportMonth", mode="input", help_col=5,
                  help_text="Select the month to report on; change this "
                            "when you want another month.")
    s.ws.data_validation(row - 1, 3, row - 1, 3,
                         {"validate": "list", "source": "=MonthKeys",
                          "input_message": "Pick a month in yyyy-mm "
                                           "form, for example "
                                           "2026-07."})
    row += 1
    row = s.note(
        row,
        "The month cell above is the only thing you change on this "
        "page. Everything else is calculated from the registers, so "
        "a report for March is never out of date - it is rebuilt "
        "the moment you ask for it.",
        LAST_COL, height=30)
    row += 1

    # ----------------------------------------------------------- money --
    row = s.section(row, "The money", LAST_COL)
    s.kpi(row, 0, "Revenue",
          '=SUMIFS(JobCharge,JobMonth,ReportMonth,JobIsDone,1)+'
          'SUMIFS(JobExtras,JobMonth,ReportMonth,JobIsDone,1)',
          "money", note="Completed visits, excluding tax")
    s.kpi(row, 2, "Invoiced", f'={_month_sum("InvTotal", "InvMonth")}',
          "money", note="What you billed in the month")
    s.kpi(row, 4, "Collected", '=SUMIFS(InvPaid,InvPaidDate,">="&DATE(VALUE(LEFT(ReportMonth,4)),VALUE(RIGHT(ReportMonth,2)),1),InvPaidDate,"<"&DATE(VALUE(LEFT(ReportMonth,4)),VALUE(RIGHT(ReportMonth,2))+1,1))',
          "money", note="Cumulative amounts grouped by last paid date")
    s.kpi(row, 6, "Labour cost",
          f'={_month_sum("TimeCost", "TimeMonth")}+{_month_sum("JobLabourFallback", "JobMonth")}', "money",
          note="Every hour, billable or not")
    s.kpi(row, 8, "Other costs",
          f'={_month_sum("ExpPeriodCost", "ExpMonth")}+'
          f'{_month_sum("VehAmount", "VehMonth")}', "money",
          note="Expenses and vehicles")
    row = s.kpi(row, 10, "Profit",
                '=SUMIFS(JobCharge,JobMonth,ReportMonth,JobIsDone,1)+'
                'SUMIFS(JobExtras,JobMonth,ReportMonth,JobIsDone,1)-'
                f'{_month_sum("TimeCost", "TimeMonth")}-'
                f'{_month_sum("JobLabourFallback", "JobMonth")}-'
                f'{_month_sum("ExpPeriodCost", "ExpMonth")}-'
                f'{_month_sum("VehAmount", "VehMonth")}',
                "money", note="What was left")
    row += 1

    # ------------------------------------------------------------ work --
    row = s.section(row, "The work", LAST_COL)
    s.kpi(row, 0, "Visits completed",
          '=COUNTIFS(JobMonth,ReportMonth,JobIsDone,1)', "int")
    s.kpi(row, 2, "Visits cancelled",
          '=COUNTIFS(JobMonth,ReportMonth,JobStatus,"Cancelled")',
          "int", note="Worth watching the reason")
    s.kpi(row, 4, "Rained off",
          '=COUNTIFS(JobMonth,ReportMonth,JobStatus,"Rained off")',
          "int")
    s.kpi(row, 6, "Crew hours",
          f'={_month_sum("TimeHours", "TimeMonth")}', "number1")
    s.kpi(row, 8, "Billable hours",
          '=SUMIFS(TimeHours,TimeMonth,ReportMonth,TimeIsBillable,1)',
          "number1")
    row = s.kpi(row, 10, "Billable share",
                '=IFERROR(SUMIFS(TimeHours,TimeMonth,ReportMonth,'
                'TimeIsBillable,1)/'
                f'{_month_sum("TimeHours", "TimeMonth")},"")',
                "percent0", note="Share of paid time that was sold")
    row += 1

    # ---------------------------------------------------- per hour --
    row = s.section(row, "What an hour was worth", LAST_COL)
    s.kpi(row, 0, "Revenue per crew hour",
          '=IFERROR((SUMIFS(JobCharge,JobMonth,ReportMonth,'
          'JobIsDone,1)+SUMIFS(JobExtras,JobMonth,ReportMonth,'
          f'JobIsDone,1))/{_month_sum("TimeHours", "TimeMonth")},"")',
          "money", note="Against your charge-out rate")
    s.kpi(row, 2, "Average visit",
          '=IFERROR(SUMIFS(JobCharge,JobMonth,ReportMonth,JobIsDone,1)'
          '/COUNTIFS(JobMonth,ReportMonth,JobIsDone,1),"")', "money")
    s.kpi(row, 4, "Quotes sent",
          '=COUNTIFS(QuoteMonth,ReportMonth)', "int")
    s.kpi(row, 6, "Quotes won",
          '=COUNTIFS(QuoteMonth,ReportMonth,QuoteIsWon,1)', "int")
    s.kpi(row, 8, "Win rate",
          '=IFERROR(COUNTIFS(QuoteMonth,ReportMonth,QuoteIsWon,1)/'
          'COUNTIFS(QuoteMonth,ReportMonth),"")', "percent0")
    row = s.kpi(row, 10, "New customers",
                '=COUNTIFS(CustFirstJob,">="&DATE(VALUE(LEFT('
                'ReportMonth,4)),VALUE(RIGHT(ReportMonth,2)),1),'
                'CustFirstJob,"<="&DATE(VALUE(LEFT(ReportMonth,4)),'
                'VALUE(RIGHT(ReportMonth,2))+1,1)-1)', "int")
    row += 1

    # ----------------------------------------------------- money owed --
    row = s.section(row, "Money still out there", LAST_COL)
    row = s.note(
        row,
        "Aged from the due date, not the invoice date, so an "
        "invoice on thirty day terms is not counted late the "
        "moment it is sent. These four buckets cover every unpaid "
        "invoice in the workbook, not only this month's.",
        LAST_COL, height=32)
    row += 1
    s.kpi(row, 0, "Not due yet",
          '=SUMIFS(InvOutstanding,InvAgeBand,"Not due yet")', "money")
    s.kpi(row, 2, "1-30 days",
          '=SUMIFS(InvOutstanding,InvAgeBand,"1-30 days")', "money")
    s.kpi(row, 4, "31-60 days",
          '=SUMIFS(InvOutstanding,InvAgeBand,"31-60 days")', "money")
    s.kpi(row, 6, "61-90 days",
          '=SUMIFS(InvOutstanding,InvAgeBand,"61-90 days")', "money")
    s.kpi(row, 8, "Over 90 days",
          '=SUMIFS(InvOutstanding,InvAgeBand,"Over 90 days")',
          "money", note="Decide: chase, settle or write off")
    row = s.kpi(row, 10, "Total owed", "=SUM(InvOutstanding)",
                "money")
    row += 2

    # ------------------------------------------------ top services --
    row = s.section(row, "What sold this month", LAST_COL)
    s.table_head(row, 0,
                 ["Service", "Visits", "Revenue", "Avg price",
                  "Share of month"],
                 widths=[30, 11, 13, 13, 14])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        pick = ('IFERROR(INDEX([[Service Catalog.name]],'
                f'MATCH(ROW()-{head + 1},'
                '[[Service Catalog.revenue_rank]],0)),"")')
        s.formula(line, 0, "=" + pick, fmts.calc("text"))
        s.formula(line, 1,
                  f'=IF($A{line + 1}="","",'
                  f'COUNTIFS(JobService,$A{line + 1},JobMonth,'
                  'ReportMonth,JobIsDone,1))', fmts.calc("int"))
        s.formula(line, 2,
                  f'=IF($A{line + 1}="","",'
                  f'SUMIFS(JobCharge,JobService,$A{line + 1},'
                  'JobMonth,ReportMonth,JobIsDone,1))',
                  fmts.calc("money"))
        s.formula(line, 3,
                  f'=IF($B{line + 1}="","",IF($B{line + 1}=0,"",'
                  f'ROUND($C{line + 1}/$B{line + 1},2)))',
                  fmts.calc("money"))
        s.formula(line, 4,
                  f'=IFERROR($C{line + 1}/'
                  'SUMIFS(JobCharge,JobMonth,ReportMonth,JobIsDone,1)'
                  ',"")', fmts.calc("percent"))
    row = head + LIST_ROWS + 2

    # ------------------------------------------------- top customers --
    row = s.section(row, "Who spent the most this month", LAST_COL)
    s.table_head(row, 0,
                 ["Customer", "Visits", "Revenue", "Owing",
                  "Last visit"],
                 widths=[28, 11, 13, 13, 13])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        rank = f"ROW()-{head + 1}"
        s.formula(line, 0,
                  '=IFERROR(INDEX([[Customer CRM.name]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0)),'
                  '"")', fmts.calc("text"))
        s.formula(line, 1,
                  '=IFERROR(COUNTIFS(JobCustomer,'
                  f'INDEX([[Customer CRM.id]],MATCH({rank},'
                  '[[Customer CRM.lifetime_rank]],0)),JobMonth,'
                  'ReportMonth,JobIsDone,1),"")', fmts.calc("int"))
        s.formula(line, 2,
                  '=IFERROR(SUMIFS(JobCharge,JobCustomer,'
                  f'INDEX([[Customer CRM.id]],MATCH({rank},'
                  '[[Customer CRM.lifetime_rank]],0)),JobMonth,'
                  'ReportMonth,JobIsDone,1),"")', fmts.calc("money"))
        s.formula(line, 3,
                  '=IFERROR(INDEX([[Customer CRM.owing]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("money"))
        s.formula(line, 4,
                  '=IFERROR(IF(INDEX([[Customer CRM.last_job]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))='
                  '"","",INDEX([[Customer CRM.last_job]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))),'
                  '"")', fmts.calc("date"))
    row = head + LIST_ROWS + 2

    # --------------------------------------------------- the crew --
    row = s.section(row, "The crew this month", LAST_COL)
    s.table_head(row, 0,
                 ["Name", "Hours", "Billable", "Billable %", "Cost",
                  "Overtime"],
                 widths=[24, 11, 11, 12, 12, 11])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        rank = f"ROW()-{head + 1}"
        who = (f'INDEX([[Crew Database.id]],MATCH({rank},'
               '[[Crew Database.revenue_rank]],0))')
        s.formula(line, 0,
                  '=IFERROR(INDEX([[Crew Database.name]],'
                  f'MATCH({rank},[[Crew Database.revenue_rank]],0)),'
                  '"")', fmts.calc("text"))
        s.formula(line, 1,
                  f'=IFERROR(SUMIFS(TimeHours,TimeEmployee,{who},'
                  'TimeMonth,ReportMonth),"")', fmts.calc("number1"))
        s.formula(line, 2,
                  f'=IFERROR(SUMIFS(TimeHours,TimeEmployee,{who},'
                  'TimeMonth,ReportMonth,TimeIsBillable,1),"")',
                  fmts.calc("number1"))
        s.formula(line, 3,
                  f'=IF($B{line + 1}="","",IF($B{line + 1}=0,"",'
                  f'ROUND($C{line + 1}/$B{line + 1},4)))',
                  fmts.calc("percent"))
        s.formula(line, 4,
                  f'=IFERROR(SUMIFS(TimeCost,TimeEmployee,{who},'
                  'TimeMonth,ReportMonth),"")', fmts.calc("money"))
        s.formula(line, 5,
                  '=IFERROR(SUMIFS(TimeOvertimeHours,TimeEmployee,'
                  f'{who},TimeMonth,ReportMonth),"")',
                  fmts.calc("number1"))
    row = head + LIST_ROWS + 2

    # ------------------------------------------------ what to do next --
    row = s.section(row, "What this month is telling you", LAST_COL)
    row = s.bullets(row, [
        "Collected well below invoiced means the problem is "
        "getting paid, not getting work. Start at the top of the "
        "ageing table.",
        "Billable share under 60% means the day is being eaten by "
        "driving, loading and yard time. Look at the round order "
        "before you look at the crew.",
        "Revenue per crew hour below your charge-out rate means "
        "your prices and your times disagree. The Service Catalog "
        "tab shows which service is the culprit.",
        "A win rate over 90% is not good news - it means you are "
        "the cheapest quote in town. Test a higher price on the "
        "next five.",
        "Cancelled and rained-off visits are lost capacity. If they "
        "are not rescheduled within a fortnight they are simply "
        "gone.",
    ], LAST_COL, height=30)
    row += 1

    row = s.note(
        row,
        "Every figure on this page comes from the rows you have "
        "entered. A month with visits done but no timesheets will "
        "look wonderfully profitable and tell you nothing at all.",
        LAST_COL, height=30)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
