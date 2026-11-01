"""`Dashboard` - the page that answers "how is the business doing?"

Everything here is worked out from the registers, so nothing is ever
out of date and there is nothing to refresh.  The questions are in the
order a wedding photographer actually asks them: what is happening
this week, what needs doing today, am I booked up, is the money in,
how far behind is the editing, and which weddings are actually worth
shooting.
"""

from __future__ import annotations

from ..config import MAX_WEDDINGS_SHOWN, Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Dashboard"
LAST_COL = 12
MONTHS = 12
ACTION_ROWS = 10
PACKAGE_ROWS = 6

EARNS = '[[Wedding Bookings.earns]],"Yes"'
HOLDS = '[[Wedding Bookings.holds]],"Yes"'
WED_NUM = "[[Wedding Bookings.wed_num]]"


def _month_key(n: int) -> str:
    """The `yyyy-mm` key for n months before this one."""
    if n == 0:
        return 'TEXT(TodayDate,"yyyy-mm")'
    return (f'TEXT(DATE(YEAR(TodayDate),MONTH(TodayDate)-{n},1),'
            f'"yyyy-mm")')


def _by_rank(sheet: str, rank_key: str, field: str, n: int) -> str:
    """The nth row of a register by one of its hidden rank columns."""
    return (f'IFERROR(INDEX([[{sheet}.{field}]],MATCH({n},'
            f'[[{sheet}.{rank_key}]],0)),"")')


def _nth(sheet: str, trigger: str, field: str, n: int) -> str:
    """Row n of a register, blank when that row is empty."""
    return (f'IFERROR(IF(INDEX([[{sheet}.{trigger}]],{n})="","",'
            f'INDEX([[{sheet}.{field}]],{n})),"")')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.primary)

    s.banner("Wedding Photography Dashboard",
             "Your weddings, your money and your backlog - worked out "
             "from the tabs you have already filled in.",
             LAST_COL)
    s.set_col(0, 0, 24)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 13)

    # ----------------------------------------------------------- header --
    row = 4
    s.merge(row, 0, 0, "Studio", fmts.chrome("label_bold"))
    s.merge(row, 1, 3, None, fmts.calc("text"))
    s.formula(row, 1, "=StudioName", fmts.calc("text"))
    s.merge(row, 4, 4, "Month", fmts.chrome("label_right"))
    s.formula(row, 5, '=TEXT(TodayDate,"mmmm yyyy")', fmts.calc("text"))
    s.merge(row, 6, 6, "Couples", fmts.chrome("label_right"))
    s.formula(row, 7, "=ClientCount", fmts.calc("int"))
    s.merge(row, 8, 8, "Today", fmts.chrome("label_right"))
    s.formula(row, 9, "=TodayDate", fmts.calc("date"))
    s.merge(row, 10, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 10,
        '="Figures update the moment you type. Nothing to refresh."',
        fmts.chrome("note"))
    row += 2

    # ------------------------------------------------------- this week --
    row = s.section(row, "The next few weeks", LAST_COL)

    next_days = (f'COUNTIFS({WED_NUM},">="&TodayDate,{WED_NUM},'
                 f'"<="&TodayDate+UpcomingDays,{HOLDS})')
    s.kpi(row, 0, "Weddings coming up", f"={next_days}", "int",
          note="Inside your 'coming up' window from Settings")
    s.kpi(row, 2, "Next wedding in",
          '=IFERROR(INDEX([[Wedding Bookings.days_away]],'
          'MATCH(1,[[Wedding Bookings.upcoming_rank]],0)),"")',
          "int", note="Days away")
    s.kpi(row, 4, "This weekend",
          f'=COUNTIFS({WED_NUM},">="&TodayDate,{WED_NUM},'
          f'"<="&TodayDate+7,{HOLDS})', "int")
    s.kpi(row, 6, "Timelines not built",
          f'=COUNTIFS({WED_NUM},">="&TodayDate,{WED_NUM},'
          f'"<="&TodayDate+UpcomingDays,{HOLDS},'
          f'[[Wedding Bookings.timeline_lines]],0)', "int",
          note="Upcoming weddings with no running order yet")
    s.kpi(row, 8, "Questionnaires out",
          '=COUNTIFS([[Wedding Bookings.questionnaire_sent]],">0",'
          '[[Wedding Bookings.questionnaire_back]],"",'
          f'{HOLDS})', "int")
    row = s.kpi(row, 10, "Nobody assigned",
                f'=COUNTIFS({WED_NUM},">="&TodayDate,{HOLDS},'
                f'[[Wedding Bookings.photographer]],"")', "int",
                note="Upcoming weddings with no lead photographer")

    s.kpi(row, 0, "Date clashes",
          '=COUNTIFS([[Wedding Bookings.clash]],"Yes")', "int",
          note="Two live weddings on one day")
    s.kpi(row, 2, "Photographer clashes",
          '=COUNTIFS([[Wedding Bookings.team_clash]],"Yes")', "int")
    s.kpi(row, 4, "Contracts unsigned",
          f'=COUNTIFS({HOLDS},[[Wedding Bookings.contract_done]],'
          f'"<>Yes",{WED_NUM},">="&TodayDate)', "int")
    s.kpi(row, 6, "Shot lists empty",
          f'=COUNTIFS({WED_NUM},">="&TodayDate,{WED_NUM},'
          f'"<="&TodayDate+UpcomingDays,{HOLDS},'
          f'[[Wedding Bookings.shot_lines]],0)', "int")
    s.kpi(row, 8, "Must-have shots missed",
          '=COUNTIFS([[Shot List Manager.must_have]],"Yes",'
          '[[Shot List Manager.status]],"Missed")', "int",
          note="Flagged as essential and never taken")
    row = s.kpi(row, 10, "Kit needing attention",
                '=COUNTIFS([[Equipment Inventory.alert]],"Due -*")+'
                'COUNTIFS([[Equipment Inventory.alert]],"Order -*")+'
                'COUNTIFS([[Equipment Inventory.alert]],"Check -*")',
                "int")
    row += 1

    # ------------------------------------------------------- the money --
    row = s.section(row, "The money", LAST_COL)
    s.kpi(row, 0, "Booked this year",
          '=SUMIFS([[Wedding Bookings.total_value]],'
          f'[[Wedding Bookings.year]],YEAR(TodayDate),{EARNS})',
          "money0", note="Value of every confirmed wedding dated this "
                         "year")
    s.kpi(row, 2, "Against target",
          '=IF(TargetRevenue<=0,"",'
          'SUMIFS([[Wedding Bookings.total_value]],'
          f'[[Wedding Bookings.year]],YEAR(TodayDate),{EARNS})/'
          'TargetRevenue)', "percent0")
    s.kpi(row, 4, "Collected",
          f'=SUMIFS([[Wedding Bookings.collected]],{EARNS})', "money0",
          note="Across every confirmed wedding, past and future")
    s.kpi(row, 6, "Still owed",
          f'=SUMIFS([[Wedding Bookings.outstanding]],{EARNS})',
          "money0")
    s.kpi(row, 8, "Overdue now",
          '=SUMIFS([[Payments & Invoices.balance]],'
          '[[Payments & Invoices.is_late]],"Yes")', "money0",
          note="Invoices past their due date")
    row = s.kpi(row, 10, "Invoices late",
                '=COUNTIFS([[Payments & Invoices.is_late]],"Yes")',
                "int")

    s.kpi(row, 0, "Average booking",
          f'=IF(COUNTIFS({EARNS})<=0,"",'
          f'SUMIFS([[Wedding Bookings.total_value]],{EARNS})/'
          f'COUNTIFS({EARNS}))', "money0")
    s.kpi(row, 2, "Average profit",
          f'=IF(COUNTIFS({EARNS})<=0,"",'
          f'SUMIFS([[Wedding Bookings.profit]],{EARNS})/'
          f'COUNTIFS({EARNS}))', "money0")
    s.kpi(row, 4, "Margin",
          f'=IF(SUMIFS([[Wedding Bookings.total_value]],{EARNS})<=0,"",'
          f'SUMIFS([[Wedding Bookings.profit]],{EARNS})/'
          f'SUMIFS([[Wedding Bookings.total_value]],{EARNS}))',
          "percent0", note="Target is on Settings")
    s.kpi(row, 6, "Expenses this year",
          '=SUMIFS([[Expense Tracker.amount]],'
          '[[Expense Tracker.year]],YEAR(TodayDate))', "money0")
    s.kpi(row, 8, "Overheads this year", "=OverheadsThisYear",
          "money0", note="Costs not tied to one wedding")
    row = s.kpi(row, 10, "Earned after delivery",
                '=SUM([[Gallery & Delivery.after_total]])', "money0",
                note="Prints and albums sold once the gallery was up")
    row += 1

    # --------------------------------------------------- what to do now --
    row = s.section(row, "What needs doing", LAST_COL)
    row = s.note(
        row,
        "Every register writes one plain-English line per row saying "
        "what it needs. These are the counts. Filter by the "
        "'What to do' column; do not sort or move register rows.",
        LAST_COL, height=30)
    row += 1

    head = row
    s.table_head(head, 0, ["Where", "Urgent", "Overdue", "Chase or send",
                           "Add or check", "All clear", "Needs you"],
                 widths=[24, 13, 13, 14, 14, 13, 13])
    row = head + 1
    tabs = [
        ("Lead Tracker", "Lead Tracker"),
        ("Wedding Bookings", "Wedding Bookings"),
        ("Contracts & Documents", "Contracts & Documents"),
        ("Payments & Invoices", "Payments & Invoices"),
        ("Wedding Timeline", "Wedding Timeline"),
        ("Shot List Manager", "Shot List Manager"),
        ("Editing Workflow", "Editing Workflow"),
        ("Gallery & Delivery", "Gallery & Delivery"),
        ("Equipment Inventory", "Equipment Inventory"),
        ("Expense Tracker", "Expense Tracker"),
        ("Reviews & Referrals", "Reviews & Referrals"),
    ]
    for label, sheet in tabs:
        col = f"[[{sheet}.alert]]"
        s.write(row, 0, label, fmts.chrome("label_bold"))
        s.formula(row, 1, f'=COUNTIF({col},"Urgent -*")',
                  fmts.cell("int", "calc"))
        s.formula(row, 2, f'=COUNTIF({col},"Overdue -*")',
                  fmts.cell("int", "calc"))
        s.formula(row, 3,
                  f'=COUNTIF({col},"Chase -*")+COUNTIF({col},"Send -*")'
                  f'+COUNTIF({col},"Follow up -*")+'
                  f'COUNTIF({col},"Due -*")',
                  fmts.cell("int", "calc"))
        s.formula(row, 4,
                  f'=COUNTIF({col},"Add -*")+COUNTIF({col},"Check -*")+'
                  f'COUNTIF({col},"Action -*")+'
                  f'COUNTIF({col},"Missing -*")+'
                  f'COUNTIF({col},"Order -*")+'
                  f'COUNTIF({col},"Duplicate -*")+'
                  f'COUNTIF({col},"Loss -*")+'
                  f'COUNTIF({col},"Expired -*")',
                  fmts.cell("int", "calc"))
        s.formula(row, 5, f'=COUNTIF({col},"OK*")',
                  fmts.cell("int", "calc"))
        s.formula(row, 6,
                  f'=COUNTIF({col},"?*")-COUNTIF({col},"OK*")',
                  fmts.cell("int", "calc"))
        row += 1
    s.write(row, 0, "Everything", fmts.chrome("total_label"))
    first_tab, last_tab = head + 1, row - 1
    for column in range(1, 7):
        s.formula(row, column,
                  f"=SUM({chr(65 + column)}{first_tab + 1}:"
                  f"{chr(65 + column)}{last_tab + 1})",
                  fmts.chrome("total_value",
                              num_format=s.num_format("int")))
    row += 2

    # ------------------------------------------------- the next weddings --
    row = s.section(row, "The next weddings", LAST_COL)
    head = row
    s.table_head(head, 0, ["Couple", "Date", "Days", "Venue",
                           "Photographer", "Value", "Paid",
                           "Contract", "What to do"],
                 widths=[22, 12, 8, 20, 16, 12, 9, 13, 30])
    row = head + 1
    for n in range(1, MAX_WEDDINGS_SHOWN + 1):
        rank = (f'MATCH({n},[[Wedding Bookings.upcoming_rank]],0)')
        def pick(field, fmt_style, r=rank):
            return (f'=IFERROR(INDEX([[Wedding Bookings.{field}]],{r}),'
                    f'"")')
        s.formula(row, 0, pick("client_name", "text"),
                  fmts.cell("text", "calc"))
        s.formula(row, 1, pick("wedding_date", "date"),
                  fmts.cell("date", "calc"))
        s.formula(row, 2, pick("days_away", "int"),
                  fmts.cell("int", "calc"))
        s.formula(row, 3, pick("venue", "text"),
                  fmts.cell("text", "calc"))
        s.formula(row, 4, pick("photographer_name", "text"),
                  fmts.cell("text", "calc"))
        s.formula(row, 5, pick("total_value", "money"),
                  fmts.cell("money", "calc"))
        s.formula(row, 6, pick("paid_pct", "percent0"),
                  fmts.cell("percent0", "calc"))
        s.formula(row, 7, pick("contract_state", "status"),
                  fmts.cell("text", "calc"))
        s.formula(row, 8, pick("alert", "status"),
                  fmts.cell("text", "calc"))
        row += 1
    row += 1

    # ----------------------------------------------- post-production ----
    row = s.section(row, "Post-production", LAST_COL)
    s.kpi(row, 0, "Weddings in editing",
          '=COUNTIFS([[Editing Workflow.stage]],"<>Complete",'
          '[[Editing Workflow.booking]],"?*")', "int",
          note="Shot, not yet delivered")
    s.kpi(row, 2, "Galleries overdue",
          '=COUNTIFS([[Editing Workflow.late]],"Yes",'
          '[[Editing Workflow.stage]],"<>Complete")', "int")
    s.kpi(row, 4, "Not backed up",
          '=COUNTIFS([[Editing Workflow.backup]],"<>Yes",'
          '[[Editing Workflow.booking]],"?*")', "int",
          note="The only number on this page that cannot be fixed "
               "later")
    s.kpi(row, 6, "Average turnaround",
          '=IFERROR(AVERAGEIFS([[Editing Workflow.days_taken]],'
          '[[Editing Workflow.days_taken]],">0"),"")', "int",
          note="Days from wedding to finished gallery")
    s.kpi(row, 8, "You promise",
          "=DeliveryDays", "int", note="Days, from Settings")
    row = s.kpi(row, 10, "Delivered, never opened",
                '=COUNTIFS([[Gallery & Delivery.opened]],"No")', "int")

    s.kpi(row, 0, "Albums to send",
          '=COUNTIFS([[Gallery & Delivery.album_ordered]],"Yes",'
          '[[Gallery & Delivery.album_sent]],"")', "int")
    s.kpi(row, 2, "Galleries closing soon",
          '=COUNTIFS([[Gallery & Delivery.expires]],">="&TodayDate,'
          '[[Gallery & Delivery.expires]],"<="&TodayDate+30,'
          '[[Gallery & Delivery.expiry_warned]],"<>Yes")', "int",
          note="Expiring within a month with no warning sent")
    s.kpi(row, 4, "Reviews received",
          '=COUNTIFS([[Reviews & Referrals.has_review]],"Yes")', "int")
    s.kpi(row, 6, "Average review",
          '=IFERROR(AVERAGE([[Reviews & Referrals.rating]]),"")',
          "rating")
    s.kpi(row, 8, "Weddings from referrals",
          '=COUNTIFS([[Lead Tracker.referred_by]],"?*",'
          '[[Lead Tracker.is_won]],"Yes")', "int")
    row = s.kpi(row, 10, "Referral revenue",
                '=SUMIFS([[Lead Tracker.booked_value]],'
                '[[Lead Tracker.referred_by]],"?*",'
                '[[Lead Tracker.is_won]],"Yes")', "money0")
    row += 1

    # ------------------------------------------------------- enquiries --
    row = s.section(row, "Enquiries", LAST_COL)
    s.kpi(row, 0, "Open enquiries",
          '=COUNTIFS([[Lead Tracker.is_open]],"Yes")', "int")
    s.kpi(row, 2, "Needing a reply",
          '=COUNTIF([[Lead Tracker.alert]],"Urgent -*")+'
          'COUNTIF([[Lead Tracker.alert]],"Action -*")', "int")
    s.kpi(row, 4, "Overdue a chase",
          '=COUNTIFS([[Lead Tracker.overdue]],">0",'
          '[[Lead Tracker.is_open]],"Yes")', "int")
    s.kpi(row, 6, "Enquiries this year",
          '=COUNTIFS([[Lead Tracker.enq_num]],">="&'
          'DATE(YEAR(TodayDate),1,1),[[Lead Tracker.enq_num]],'
          '"<"&DATE(YEAR(TodayDate)+1,1,1))', "int")
    s.kpi(row, 8, "Booked from them",
          '=COUNTIFS([[Lead Tracker.enq_num]],">="&'
          'DATE(YEAR(TodayDate),1,1),[[Lead Tracker.enq_num]],'
          '"<"&DATE(YEAR(TodayDate)+1,1,1),'
          '[[Lead Tracker.is_won]],"Yes")', "int")
    row = s.kpi(row, 10, "Conversion",
                '=IF(COUNTIFS([[Lead Tracker.enq_num]],">="&'
                'DATE(YEAR(TodayDate),1,1),[[Lead Tracker.enq_num]],'
                '"<"&DATE(YEAR(TodayDate)+1,1,1))<=0,"",'
                'COUNTIFS([[Lead Tracker.enq_num]],">="&'
                'DATE(YEAR(TodayDate),1,1),[[Lead Tracker.enq_num]],'
                '"<"&DATE(YEAR(TodayDate)+1,1,1),'
                '[[Lead Tracker.is_won]],"Yes")/'
                'COUNTIFS([[Lead Tracker.enq_num]],">="&'
                'DATE(YEAR(TodayDate),1,1),[[Lead Tracker.enq_num]],'
                '"<"&DATE(YEAR(TodayDate)+1,1,1)))', "percent0",
                note="Target is on Settings")
    row += 1

    # --------------------------------------------------- the packages ---
    row = s.section(row, "Which packages are working", LAST_COL)
    head = row
    s.table_head(head, 0, ["Package", "Price", "Cost", "Margin",
                           "Your hourly rate", "Asked about", "Booked",
                           "Conversion", "Revenue", "What to do"],
                 widths=[20, 12, 12, 10, 15, 12, 10, 11, 13, 28])
    row = head + 1
    for n in range(1, PACKAGE_ROWS + 1):
        for col, (field, style) in enumerate([
                ("name", "text"), ("total_price", "money"),
                ("total_cost", "money"), ("margin", "percent0"),
                ("hourly", "money"), ("enquiries", "int"),
                ("sold", "int"), ("conversion", "percent0"),
                ("revenue", "money"), ("alert", "text")]):
            s.formula(row, col,
                      "=" + _nth("Packages & Pricing", "name", field, n),
                      fmts.cell(style, "calc"))
        row += 1
    row += 1

    # ------------------------------------------------ twelve months -----
    row = s.section(row, "The last twelve months", LAST_COL)
    head = row
    s.table_head(head, 0, ["Month", "Weddings", "Revenue booked",
                           "Money in", "Expenses", "Profit",
                           "Enquiries", "Booked", "Conversion",
                           "Against target"],
                 widths=[14, 11, 15, 13, 12, 12, 11, 10, 11, 14])
    row = head + 1
    first_month = row
    for n in range(MONTHS - 1, -1, -1):
        key = _month_key(n)
        s.formula(row, 0, f'={key}', fmts.cell("text", "calc"))
        s.formula(row, 1,
                  f'=COUNTIFS([[Wedding Bookings.month]],{key},{EARNS})',
                  fmts.cell("int", "calc"))
        s.formula(row, 2,
                  f'=SUMIFS([[Wedding Bookings.total_value]],'
                  f'[[Wedding Bookings.month]],{key},{EARNS})',
                  fmts.cell("money", "calc"))
        s.formula(row, 3,
                  f'=SUMIFS([[Payments & Invoices.received]],'
                  f'[[Payments & Invoices.month]],{key})',
                  fmts.cell("money", "calc"))
        s.formula(row, 4,
                  f'=SUMIFS([[Expense Tracker.amount]],'
                  f'[[Expense Tracker.month]],{key})',
                  fmts.cell("money", "calc"))
        s.formula(row, 5,
                  f'=SUMIFS([[Wedding Bookings.profit]],'
                  f'[[Wedding Bookings.month]],{key},{EARNS})-'
                  f'SUMIFS([[Expense Tracker.profit_cost]],'
                  f'[[Expense Tracker.month]],{key},'
                  f'[[Expense Tracker.is_overhead]],"Yes")',
                  fmts.cell("money", "calc"))
        s.formula(row, 6,
                  f'=COUNTIFS([[Lead Tracker.month]],{key})',
                  fmts.cell("int", "calc"))
        s.formula(row, 7,
                  f'=COUNTIFS([[Lead Tracker.month]],{key},'
                  f'[[Lead Tracker.is_won]],"Yes")',
                  fmts.cell("int", "calc"))
        s.formula(row, 8,
                  f'=IF(COUNTIFS([[Lead Tracker.month]],{key})<=0,"",'
                  f'COUNTIFS([[Lead Tracker.month]],{key},'
                  f'[[Lead Tracker.is_won]],"Yes")/'
                  f'COUNTIFS([[Lead Tracker.month]],{key}))',
                  fmts.cell("percent0", "calc"))
        s.formula(row, 9,
                  f'=IF(TargetRevenue<=0,"",'
                  f'SUMIFS([[Wedding Bookings.total_value]],'
                  f'[[Wedding Bookings.month]],{key},{EARNS})/'
                  f'(TargetRevenue/12))',
                  fmts.cell("percent0", "calc"))
        row += 1
    last_month = row - 1
    s.write(row, 0, "Twelve months", fmts.chrome("total_label"))
    for column, style in ((1, "int"), (2, "money"), (3, "money"),
                          (4, "money"), (5, "money"), (6, "int"),
                          (7, "int")):
        letter = chr(65 + column)
        s.formula(row, column,
                  f"=SUM({letter}{first_month + 1}:{letter}"
                  f"{last_month + 1})",
                  fmts.chrome("total_value",
                              num_format=s.num_format(style)))
    s.formula(row, 8,
              f"=IF(G{row + 1}<=0,\"\",H{row + 1}/G{row + 1})",
              fmts.chrome("total_value",
                          num_format=s.num_format("percent0")))
    s.formula(row, 9,
              f'=IF(TargetRevenue<=0,"",C{row + 1}/TargetRevenue)',
              fmts.chrome("total_value",
                          num_format=s.num_format("percent0")))
    row += 2

    # ------------------------------------------------- best and worst ---
    row = s.section(row, "Best and worst", LAST_COL)
    head = row
    s.table_head(head, 0, ["", "Couple", "Date", "Package", "Value",
                           "Profit", "Margin", "Profit an hour"],
                 widths=[18, 20, 12, 16, 12, 12, 10, 14])
    row = head + 1
    for n in range(1, 4):
        s.write(row, 0, f"Most profitable #{n}",
                fmts.chrome("label_bold"))
        for col, (field, style) in enumerate([
                ("couple", "text"), ("wedding_date", "date"),
                ("package", "text"), ("revenue", "money"),
                ("net_profit", "money"), ("net_margin", "percent0"),
                ("per_hour", "money")], start=1):
            s.formula(row, col,
                      "=" + _by_rank("Profit Analysis",
                                     "net_profit_rank", field, n),
                      fmts.cell(style, "calc"))
        row += 1
    for n in range(1, 4):
        s.write(row, 0, f"Least profitable #{n}",
                fmts.chrome("label_bold"))
        for col, (field, style) in enumerate([
                ("couple", "text"), ("wedding_date", "date"),
                ("package", "text"), ("revenue", "money"),
                ("net_profit", "money"), ("net_margin", "percent0"),
                ("per_hour", "money")], start=1):
            s.formula(
                row, col,
                f'=IFERROR(INDEX([[Profit Analysis.{field}]],'
                f'MATCH(COUNTIF([[Profit Analysis.booking]],"?*")'
                f'-{n - 1},[[Profit Analysis.net_profit_rank]],0)),"")',
                fmts.cell(style, "calc"))
        row += 1
    row += 1

    row = s.note(
        row,
        "This workbook is a business organisation tool. It does not "
        "connect to any booking platform, gallery host or payment "
        "processor, it does not send email, and it does not generate "
        "or sign contracts. Every figure on this page comes from "
        "something you typed on one of the other tabs.",
        LAST_COL, height=44)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
