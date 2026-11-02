"""`Dashboard` - the page that answers "what do I need to do today?"

Everything here is worked out from the other tabs, so nothing is ever
out of date and there is nothing to refresh. The questions are in the
order somebody running a lawn care round actually asks them: what is
on today, what has slipped, who owes me money, what is about to break,
and is any of this actually making a profit.

The top strip is deliberately the week rather than the year. A
landscaping business is run a week at a time; the year is something
you look at in January.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Dashboard"
LAST_COL = 12
LIST_ROWS = 8


def _alert_count(sheet: str, prefix: str) -> str:
    """How many rows on a register are shouting a given prefix."""
    return f'COUNTIF([[{sheet}.alert]],"{prefix}*")'


#: every register that carries a "What needs doing" column
ALERT_SHEETS = [
    "Customer CRM", "Property Database", "Service Catalog",
    "Quote Calculator", "Job & Work Orders", "Recurring Contracts",
    "Crew Database", "Crew Schedule", "Timesheets & Payroll",
    "Equipment Inventory", "Vehicle & Fuel Tracker",
    "Materials Inventory", "Invoice & Payments", "Expense Tracker",
    "Customer Feedback", "Profit Analysis",
]


def _all_alerts(prefix: str) -> str:
    """Total rows across the workbook whose alert starts with prefix."""
    return "+".join(_alert_count(sheet, prefix)
                    for sheet in ALERT_SHEETS)


def _by_rank(sheet: str, rank_key: str, field: str, n: int) -> str:
    """The nth row of a register by one of its hidden rank columns."""
    return (f'IFERROR(INDEX([[{sheet}.{field}]],MATCH({n},'
            f'[[{sheet}.{rank_key}]],0)),"")')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.deep)

    s.banner("Landscaping Business Dashboard",
             "Today, this week, the money and the machines - worked "
             "out from the tabs you have already filled in.",
             LAST_COL)
    s.set_col(0, 0, 26)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 13)

    # ------------------------------------------------------------ head --
    row = 4
    s.merge(row, 0, 0, "Business", fmts.chrome("label_bold"))
    s.merge(row, 1, 3, None, fmts.calc("text"))
    s.formula(row, 1, "=BusinessName", fmts.calc("text"))
    s.merge(row, 4, 4, "Today", fmts.chrome("label_right"))
    s.formula(row, 5, "=TodayDate", fmts.calc("date"))
    s.merge(row, 6, 6, "Customers", fmts.chrome("label_right"))
    s.formula(row, 7, "=SUM(CustIsActive)", fmts.calc("int"))
    s.merge(row, 8, 8, "Properties", fmts.chrome("label_right"))
    s.formula(row, 9, "=SUM(PropIsActive)", fmts.calc("int"))
    s.merge(row, 10, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 10,
        '="Figures update the moment you type. Nothing to refresh."',
        fmts.chrome("note"))
    row += 2

    # -------------------------------------------------------- the week --
    row = s.section(row, "Today and the week ahead", LAST_COL)
    s.kpi(row, 0, "Jobs today", "=SUM(JobIsToday)", "int",
          note="Booked for today and not yet closed off")
    s.kpi(row, 2, "Jobs this week", "=SUM(JobIsWeek)", "int",
          note="Within the upcoming window on Settings")
    s.kpi(row, 4, "Hours booked",
          '=SUMIFS(JobHoursEst,JobIsOpen,1,JobDateNum,'
          '">="&TodayDate,JobDateNum,"<="&TodayDate+UpcomingDays)',
          "number1", note="Crew hours the week needs")
    s.kpi(row, 6, "Worth this week",
          '=SUMIFS(JobCharge,JobIsOpen,1,JobDateNum,">="&TodayDate,'
          'JobDateNum,"<="&TodayDate+UpcomingDays)', "money",
          note="Value of what is booked")
    s.kpi(row, 8, "Unassigned",
          '=COUNTIFS(JobIsOpen,1,JobCrew,"Unassigned")', "int",
          note="Booked with nobody to do it")
    row = s.kpi(row, 10, "Behind schedule",
                '=COUNTIFS(JobIsOpen,1,JobDateNum,"<"&TodayDate)',
                "int", span=3,
                note="Past their date and still open")
    row += 1

    # ------------------------------------------------- work that slipped --
    row = s.section(row, "Work you still owe", LAST_COL)
    row = s.note(
        row,
        "Rain, breakdowns and locked gates are part of the trade. "
        "What costs money is forgetting about them. Everything in "
        "this row is work that was promised and has not happened.",
        LAST_COL, height=30)
    row += 1
    s.kpi(row, 0, "Rained off / revisit", "=SUM(JobIsCatchup)", "int",
          note="Waiting to be rescheduled")
    s.kpi(row, 2, "Contract visits due", "=SUM(ConIsDue)", "int",
          note="Due by the contract and not booked")
    s.kpi(row, 4, "Quotes waiting",
          f"={_alert_count('Quote Calculator', 'Chase -')}", "int",
          note="Sent, no answer, past the chase window")
    s.kpi(row, 6, "Quotes to convert",
          f"={_alert_count('Quote Calculator', 'Action -')}", "int",
          note="Accepted with no work order raised")
    s.kpi(row, 8, "Completed, unbilled", "=SUM(JobIsUnbilled)", "int",
          note="Done and never invoiced")
    row = s.kpi(row, 10, "Value unbilled",
                "=SUMPRODUCT(JobIsUnbilled*JobCharge)", "money",
                span=3, note="Money sitting on the job sheet")
    row += 1

    # ------------------------------------------------------- the money --
    row = s.section(row, "The money", LAST_COL)
    s.kpi(row, 0, "Owed to you", "=SUM(InvOutstanding)", "money",
          note="Invoiced and not yet paid")
    s.kpi(row, 2, "Overdue", "=SUMPRODUCT(InvIsOverdue*InvOutstanding)",
          "money", note="Past the due date - chase these")
    s.kpi(row, 4, "Over 60 days",
          '=SUMIFS(InvOutstanding,InvDaysLate,">=60")', "money",
          note="The ones that need a decision")
    s.kpi(row, 6, "Revenue this month",
          "=SUMIFS(JobCharge,JobMonth,ThisMonthKey,JobIsDone,1)",
          "money", note="Completed visits, excluding tax")
    s.kpi(row, 8, "Costs this month",
          '=SUMIFS(ExpPeriodCost,ExpMonth,ThisMonthKey)+'
          'SUMIFS(TimeCost,TimeMonth,ThisMonthKey)+'
          'SUMIFS(JobLabourFallback,JobMonth,ThisMonthKey)+'
          'SUMIFS(VehAmount,VehMonth,ThisMonthKey)', "money",
          note="Labour, expenses and vehicles")
    row = s.kpi(row, 10, "Booked recurring",
                "=SUMPRODUCT(ConIsLive*ConAnnualValue)", "money",
                span=3, note="Annual value of live contracts")
    row += 1

    # ---------------------------------------------------- the machines --
    row = s.section(row, "Machines, materials and people", LAST_COL)
    s.kpi(row, 0, "Service overdue", "=SUM(EquipServiceDue)", "int",
          note="By hours or by date, whichever came first")
    s.kpi(row, 2, "Service soon", "=SUM(EquipServiceSoon)", "int",
          note="Inside the warning window")
    s.kpi(row, 4, "Out of service",
          '=COUNTIF(EquipStatus,"Out of service")', "int",
          note="Cannot be used at all")
    s.kpi(row, 6, "Materials low", "=SUM(MatIsLow)", "int",
          note="At or below the reorder point")
    s.kpi(row, 8, "Cost to restock", "=SUM(MatOrderValue)", "money",
          note="What the shopping list comes to")
    row = s.kpi(row, 10, "Licences expiring",
                f"={_alert_count('Crew Database', 'Renew -')}+"
                f"{_alert_count('Crew Database', 'Expired -')}",
                "int", span=3, note="Crew tickets about to lapse")
    row += 1

    # ------------------------------------------------- is it working? --
    row = s.section(row, "Is the work paying?", LAST_COL)
    row = s.note(
        row,
        "Revenue is not the test. Profit per crew hour is: it is "
        "what is left after wages, materials, fuel and the "
        "overheads, divided by the hours it took. If it falls while "
        "revenue rises, the extra work is costing you money.",
        LAST_COL, height=34)
    row += 1
    s.kpi(row, 0, "Profit this month",
          '=IFERROR(SUMIFS(ProfitProfit,ProfitMonth,ThisMonthKey),0)',
          "money", note="From the Profit Analysis tab")
    s.kpi(row, 2, "Margin",
          '=IFERROR(SUMIFS(ProfitProfit,ProfitMonth,ThisMonthKey)/'
          'SUMIFS(ProfitRevenue,ProfitMonth,ThisMonthKey),"")',
          "percent0", note="Against your target on Settings")
    s.kpi(row, 4, "Profit per crew hour",
          '=IFERROR(SUMIFS(ProfitProfitHour,ProfitMonth,'
          'ThisMonthKey),"")', "money",
          note="The number that matters most")
    s.kpi(row, 6, "Billable hours",
          '=IFERROR(SUMIFS(ProfitBillablePct,ProfitMonth,'
          'ThisMonthKey),"")', "percent0",
          note="Share of paid time that was sold")
    s.kpi(row, 8, "Quote win rate",
          '=IFERROR(SUM(QuoteIsWon)/(SUM(QuoteIsWon)+'
          'COUNTIF(QuoteStatus,"Declined")),"")', "percent0",
          note="Accepted against answered")
    row = s.kpi(row, 10, "Average visit",
                '=IFERROR(SUMIFS(JobCharge,JobIsDone,1)/'
                'SUM(JobIsDone),"")', "money", span=3,
                note="Across every completed visit")
    row += 1

    # ------------------------------------------------- what needs doing --
    row = s.section(row, "What needs doing", LAST_COL)
    row = s.note(
        row,
        "Every register has a 'What needs doing' column. This is all "
        "sixteen of them added up, by how loudly they are shouting. "
        "Work down from the left.",
        LAST_COL, height=30)
    row += 1
    s.kpi(row, 0, "Urgent", f"={_all_alerts('Urgent -')}", "int",
          note="Something is wrong, not just late")
    s.kpi(row, 2, "Overdue", f"={_all_alerts('Overdue -')}", "int",
          note="Past a date that mattered")
    s.kpi(row, 4, "Chase",
          f"={_all_alerts('Chase -')}+{_all_alerts('Send -')}+"
          f"{_all_alerts('Follow up -')}", "int",
          note="Somebody is waiting on you")
    s.kpi(row, 6, "Schedule",
          f"={_all_alerts('Schedule -')}+"
          f"{_all_alerts('Reschedule -')}", "int",
          note="Work to get in the diary")
    s.kpi(row, 8, "Service & reorder",
          f"={_all_alerts('Service -')}+{_all_alerts('Reorder -')}+"
          f"{_all_alerts('Order -')}+{_all_alerts('Renew -')}", "int",
          note="Machines, materials, contracts")
    row = s.kpi(row, 10, "Tidy up",
                f"={_all_alerts('Add -')}+{_all_alerts('Check -')}+"
                f"{_all_alerts('Action -')}+"
                f"{_all_alerts('Missing -')}", "int", span=3,
                note="Gaps in the record")
    row += 2

    # ------------------------------------------------ today's work list --
    row = s.section(row, "Today's jobs", LAST_COL)
    s.table_head(row, 0,
                 ["Job ID", "Crew", "Start", "Customer", "Address",
                  "Service", "Charge"],
                 widths=[12, 12, 9, 20, 28, 22, 11])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        pick = ('IFERROR(INDEX([[Job & Work Orders.{f}]],'
                'MATCH(ROW()-{h},[[Job & Work Orders.today_rank]],0)),'
                '"")')
        s.formula(line, 0,
                  "=" + pick.format(f="id", h=head + 1),
                  fmts.calc("id"))
        s.formula(line, 1, "=" + pick.format(f="crew", h=head + 1),
                  fmts.calc("text"))
        s.formula(line, 2,
                  '=IFERROR(IF(INDEX([[Job & Work Orders.start_time]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Job & Work Orders.today_rank]],0))="","",'
                  'INDEX([[Job & Work Orders.start_time]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Job & Work Orders.today_rank]],0))),"")',
                  fmts.calc("time"))
        s.formula(line, 3,
                  "=" + pick.format(f="customer_name", h=head + 1),
                  fmts.calc("text"))
        s.formula(line, 4, "=" + pick.format(f="address", h=head + 1),
                  fmts.calc("text"))
        s.formula(line, 5, "=" + pick.format(f="service", h=head + 1),
                  fmts.calc("text"))
        s.formula(line, 6,
                  '=IFERROR(INDEX([[Job & Work Orders.charge]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Job & Work Orders.today_rank]],0))*1,"")',
                  fmts.calc("money"))
    row = head + LIST_ROWS + 2
    row = s.note(
        row,
        "The first eight jobs booked for today, in the order the "
        "Route Planner would print them. Open that tab for the full "
        "day and a sheet the crew can take with them.",
        LAST_COL, height=28)
    row += 1

    # ---------------------------------------------------- chase list --
    row = s.section(row, "Chase these first", LAST_COL)
    s.table_head(row, 0,
                 ["Invoice", "Customer", "Due", "Days late",
                  "Outstanding", "Reminders"],
                 widths=[12, 24, 12, 11, 13, 11])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        s.formula(line, 0,
                  "=" + _by_rank("Invoice & Payments", "late_rank",
                                 "id", f"ROW()-{head + 1}"),
                  fmts.calc("id"))
        s.formula(line, 1,
                  "=" + _by_rank("Invoice & Payments", "late_rank",
                                 "customer_name", f"ROW()-{head + 1}"),
                  fmts.calc("text"))
        s.formula(line, 2,
                  '=IFERROR(IF(INDEX([[Invoice & Payments.due_date]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Invoice & Payments.late_rank]],0))="","",'
                  'INDEX([[Invoice & Payments.due_date]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Invoice & Payments.late_rank]],0))),"")',
                  fmts.calc("date"))
        s.formula(line, 3,
                  '=IFERROR(INDEX([[Invoice & Payments.days_late]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Invoice & Payments.late_rank]],0))*1,"")',
                  fmts.calc("int"))
        s.formula(line, 4,
                  '=IFERROR(INDEX([[Invoice & Payments.outstanding]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Invoice & Payments.late_rank]],0))*1,"")',
                  fmts.calc("money"))
        s.formula(line, 5,
                  '=IFERROR(INDEX([[Invoice & Payments.reminders]],'
                  f'MATCH(ROW()-{head + 1},'
                  '[[Invoice & Payments.late_rank]],0))*1,"")',
                  fmts.calc("int"))
    s.cf(f"D{head + 2}:D{head + 1 + LIST_ROWS}",
         {"type": "cell", "criteria": ">=", "value": 30,
          "format": fmts.cf("bad")})
    row = head + LIST_ROWS + 2

    # --------------------------------------------------- best customers --
    row = s.section(row, "Your best customers", LAST_COL)
    s.table_head(row, 0,
                 ["Customer", "Visits", "Lifetime revenue", "Profit",
                  "Margin", "Contract / yr", "Last visit"],
                 widths=[26, 10, 16, 12, 10, 13, 12])
    head = row
    for n in range(1, LIST_ROWS + 1):
        line = head + n
        rank = f"ROW()-{head + 1}"
        s.formula(line, 0,
                  "=" + _by_rank("Customer CRM", "lifetime_rank",
                                 "name", rank), fmts.calc("text"))
        s.formula(line, 1,
                  '=IFERROR(INDEX([[Customer CRM.jobs_done]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("int"))
        s.formula(line, 2,
                  '=IFERROR(INDEX([[Customer CRM.lifetime]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("money"))
        s.formula(line, 3,
                  '=IFERROR(INDEX([[Customer CRM.profit]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("money"))
        s.formula(line, 4,
                  '=IFERROR(INDEX([[Customer CRM.margin_pct]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("percent"))
        s.formula(line, 5,
                  '=IFERROR(INDEX([[Customer CRM.contract_value]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))*1,'
                  '"")', fmts.calc("money"))
        s.formula(line, 6,
                  '=IFERROR(IF(INDEX([[Customer CRM.last_job]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))="",'
                  '"",INDEX([[Customer CRM.last_job]],'
                  f'MATCH({rank},[[Customer CRM.lifetime_rank]],0))),'
                  '"")', fmts.calc("date"))
    row = head + LIST_ROWS + 2

    # ------------------------------------------------------ the honest bit --
    row = s.note(
        row,
        "What this dashboard is not: it does not know about work "
        "nobody has written down. Every figure above is built from "
        "the job, timesheet, expense and invoice rows you have "
        "entered. A week of visits recorded on the back of an "
        "envelope is a week this page cannot see.",
        LAST_COL, height=44)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
