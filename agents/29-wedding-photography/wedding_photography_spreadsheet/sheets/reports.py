"""`Monthly & Annual Reports` - the year in numbers, and the year before.

Two reports on one tab.  The monthly one picks a month and shows what
came in, what went out and what was left.  The annual one shows twelve
months side by side, this year against last, with the figures an
accountant asks for and the figures that tell you whether to put your
prices up.
"""

from __future__ import annotations

from ..config import MONTH_NAMES, Config, Palette
from ..layout import Registry, col_letter
from ..writer import SheetWriter, number_check

NAME = "Monthly & Annual Reports"
LAST_COL = 15

EARNS = '[[Wedding Bookings.earns]],"Yes"'
WED_NUM = "[[Wedding Bookings.wed_num]]"

#: expense groupings the annual report breaks costs down by
COST_GROUPS = [
    ("Second shooters and assistants",
     ["Second shooters", "Assistants"]),
    ("Albums, prints and postage",
     ["Albums & prints", "Packaging & postage"]),
    ("Editing paid out", ["Editing services"]),
    ("Travel, mileage and staying over",
     ["Travel & mileage", "Accommodation", "Meals on shoot"]),
    ("Equipment bought",
     ["Camera equipment", "Lens purchases", "Lighting & grip",
      "Memory & storage", "Editing computer"]),
    ("Equipment repair and hire",
     ["Equipment repair", "Equipment rental"]),
    ("Software and website",
     ["Software subscriptions", "Website & hosting"]),
    ("Marketing", ["Marketing & advertising", "Client gifts"]),
    ("Insurance, licences and professional fees",
     ["Insurance", "Accounting & legal", "Licences & permits"]),
    ("Studio, office and training",
     ["Studio rent", "Office expenses", "Education & training"]),
    ("Bank and card fees", ["Bank & card fees"]),
    ("Everything else", ["Miscellaneous", "Tax & national insurance"]),
]


def _sum_categories(categories, extra: str = "") -> str:
    """Total of several expense categories, with an optional filter."""
    parts = [f'SUMIFS([[Expense Tracker.amount]],'
             f'[[Expense Tracker.category]],"{c}"{extra})'
             for c in categories]
    return "+".join(parts)


def _month_filter(prefix: str = "Report") -> str:
    return (f'[[Expense Tracker.month]],{prefix}Key')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.deep)

    s.banner("Monthly & Annual Reports",
             "One month in detail, then the whole year beside the "
             "year before it.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 1, 34)
    for column in range(2, LAST_COL + 1):
        s.set_col(column, column, 13)

    # ================================================= the monthly report ==
    row = 4
    row = s.section(row, "Monthly report", LAST_COL)
    row = s.field(row, "Month", cfg.today.month, style="int",
                  name="ReportMonth", validate=number_check(1, 12),
                  help_text="1 to 12.", help_col=6)
    row = s.field(row, "Year", cfg.today.year, style="int",
                  name="ReportYear", validate=number_check(2000, 2100),
                  help_text="Both reports read these two cells.",
                  help_col=6)
    row = s.field(row, "Reporting on", None, style="text",
                  name="ReportKey", mode="calc",
                  formula='=TEXT(DATE(ReportYear,ReportMonth,1),'
                          '"yyyy-mm")',
                  help_text="The month key everything groups on.",
                  help_col=6)
    row = s.field(row, "From", None, style="date", name="ReportFrom",
                  mode="calc",
                  formula="=DATE(ReportYear,ReportMonth,1)")
    row = s.field(row, "To", None, style="date", name="ReportTo",
                  mode="calc",
                  formula="=EOMONTH(DATE(ReportYear,ReportMonth,1),0)")
    row += 1

    month_cost = _month_filter()

    s.kpi(row, 1, "Weddings shot",
          f'=COUNTIFS([[Wedding Bookings.month]],ReportKey,{EARNS})',
          "int")
    s.kpi(row, 3, "Value of them",
          f'=SUMIFS([[Wedding Bookings.total_value]],'
          f'[[Wedding Bookings.month]],ReportKey,{EARNS})', "money0")
    s.kpi(row, 5, "Money actually in",
          '=SUMIFS([[Payments & Invoices.received]],'
          '[[Payments & Invoices.month]],ReportKey)', "money0",
          note="Payments received in the month, whatever wedding "
               "they were for")
    s.kpi(row, 7, "Processing fees",
          '=SUMIFS([[Payments & Invoices.fee]],'
          '[[Payments & Invoices.month]],ReportKey)', "money0")
    s.kpi(row, 9, "Spent",
          '=SUMIFS([[Expense Tracker.amount]],'
          '[[Expense Tracker.month]],ReportKey)', "money0")
    row = s.kpi(row, 11, "Left over",
                '=SUMIFS([[Payments & Invoices.received]],'
                '[[Payments & Invoices.month]],ReportKey)-'
                'SUMIFS([[Payments & Invoices.fee]],'
                '[[Payments & Invoices.month]],ReportKey)-'
                'SUMIFS([[Expense Tracker.amount]],'
                '[[Expense Tracker.month]],ReportKey)', "money0",
                note="Cash in less cash out. Not the same as profit "
                     "on the weddings")

    s.kpi(row, 1, "Enquiries",
          '=COUNTIFS([[Lead Tracker.month]],ReportKey)', "int")
    s.kpi(row, 3, "Booked from them",
          '=COUNTIFS([[Lead Tracker.month]],ReportKey,'
          '[[Lead Tracker.is_won]],"Yes")', "int")
    s.kpi(row, 5, "Conversion",
          '=IF(COUNTIFS([[Lead Tracker.month]],ReportKey)<=0,"",'
          'COUNTIFS([[Lead Tracker.month]],ReportKey,'
          '[[Lead Tracker.is_won]],"Yes")/'
          'COUNTIFS([[Lead Tracker.month]],ReportKey))', "percent0")
    s.kpi(row, 7, "Galleries delivered",
          '=COUNTIFS([[Gallery & Delivery.delivered_num]],'
          '">="&ReportFrom,'
          '[[Gallery & Delivery.delivered_num]],"<="&ReportTo)', "int")
    s.kpi(row, 9, "Miles driven",
          '=SUMIFS([[Travel & Mileage.all_miles]],'
          '[[Travel & Mileage.month]],ReportKey)', "number1")
    row = s.kpi(row, 11, "Reviews in",
                '=COUNTIFS([[Reviews & Referrals.month]],ReportKey)',
                "int")
    row += 1

    # ---- where the month's money went ---------------------------------
    row = s.subsection(row, "Where the month's money went", LAST_COL)
    head = row
    s.table_head(head, 1, ["Cost", "This month", "Share",
                           "Same month last year", "Change"],
                 widths=[34, 14, 10, 20, 12])
    row = head + 1
    first_cost = row
    for label, categories in COST_GROUPS:
        s.write(row, 1, label, fmts.chrome("label"))
        s.formula(row, 2, "=" + _sum_categories(categories,
                                                f",{month_cost}"),
                  fmts.cell("money", "calc"))
        s.formula(row, 3,
                  f'=IF(SUMIFS([[Expense Tracker.amount]],'
                  f'[[Expense Tracker.month]],ReportKey)<=0,"",'
                  f'C{row + 1}/SUMIFS([[Expense Tracker.amount]],'
                  f'[[Expense Tracker.month]],ReportKey))',
                  fmts.cell("percent0", "calc"))
        last_year = ('[[Expense Tracker.month]],'
                     'TEXT(DATE(ReportYear-1,ReportMonth,1),"yyyy-mm")')
        s.formula(row, 4,
                  "=" + _sum_categories(categories, f",{last_year}"),
                  fmts.cell("money", "calc"))
        s.formula(row, 5,
                  f'=IF(E{row + 1}<=0,"",C{row + 1}/E{row + 1}-1)',
                  fmts.cell("percent0", "calc"))
        row += 1
    last_cost = row - 1
    s.write(row, 1, "Everything", fmts.chrome("total_label"))
    for column, style in ((2, "money"), (4, "money")):
        letter = col_letter(column)
        s.formula(row, column,
                  f"=SUM({letter}{first_cost + 1}:{letter}"
                  f"{last_cost + 1})",
                  fmts.chrome("total_value",
                              num_format=s.num_format(style)))
    s.formula(row, 5,
              f'=IF(E{row + 1}<=0,"",C{row + 1}/E{row + 1}-1)',
              fmts.chrome("total_value",
                          num_format=s.num_format("percent0")))
    row += 2

    # ---- the weddings in the month ---------------------------------------
    row = s.subsection(row, "The weddings in this month", LAST_COL)
    head = row
    s.table_head(head, 1, ["Date", "Couple", "Package", "Venue",
                           "Value", "Collected", "Outstanding",
                           "Profit", "Margin", "Status"],
                 widths=[12, 20, 16, 18, 12, 12, 12, 12, 9, 14])
    row = head + 1
    for n in range(1, 13):
        rank = (f'MATCH(ReportKey&"|"&{n},'
                f'[[Wedding Bookings.month_key]],0)')
        for col, (field, style) in enumerate([
                ("wedding_date", "date"), ("client_name", "text"),
                ("package", "text"), ("venue", "text"),
                ("total_value", "money"), ("collected", "money"),
                ("outstanding", "money"), ("profit", "money"),
                ("margin", "percent0"), ("status", "status")],
                start=1):
            s.formula(row, col,
                      f'=IFERROR(INDEX([[Wedding Bookings.{field}]],'
                      f'{rank}),"")',
                      fmts.cell(style, "calc"))
        row += 1
    row += 2

    # ================================================== the annual report ==
    row = s.section(row, "Annual report", LAST_COL)
    row = s.note(
        row,
        "Twelve months of the year chosen above, with last year "
        "underneath for comparison. Revenue is counted against the "
        "month the wedding happens, which is how a photographer "
        "thinks about a year; cash received is counted when it "
        "actually arrived, which is how a bank does.",
        LAST_COL, height=38)
    row += 1

    head = row
    s.table_head(head, 1,
                 ["Month"] + list(MONTH_NAMES) + ["Year"],
                 widths=[16] + [9] * 12 + [14])
    row = head + 1

    def month_row(label, template, style, total=True):
        nonlocal row
        s.write(row, 1, label, fmts.chrome("label"))
        for month in range(1, 13):
            key = f'TEXT(DATE(ReportYear,{month},1),"yyyy-mm")'
            s.formula(row, 1 + month, "=" + template.format(key=key),
                      fmts.cell(style, "calc"))
        if total:
            s.formula(row, 14,
                      f"=SUM(C{row + 1}:N{row + 1})",
                      fmts.chrome("total_value",
                                  num_format=s.num_format(style)))
        else:
            s.write(row, 14, None, fmts.cell(style, "calc"))
        row += 1

    month_row("Weddings",
              f'COUNTIFS([[Wedding Bookings.month]],{{key}},{EARNS})',
              "int")
    revenue_row = row
    month_row("Revenue booked",
              f'SUMIFS([[Wedding Bookings.total_value]],'
              f'[[Wedding Bookings.month]],{{key}},{EARNS})', "money")
    month_row("Money received",
              'SUMIFS([[Payments & Invoices.received]],'
              '[[Payments & Invoices.month]],{key})', "money")
    month_row("Direct costs",
              f'SUMIFS([[Wedding Bookings.total_cost]],'
              f'[[Wedding Bookings.month]],{{key}},{EARNS})', "money")
    month_row("Overheads",
              'SUMIFS([[Expense Tracker.profit_cost]],'
              '[[Expense Tracker.month]],{key},'
              '[[Expense Tracker.is_overhead]],"Yes")', "money")
    month_row("Profit",
              f'SUMIFS([[Wedding Bookings.profit]],'
              f'[[Wedding Bookings.month]],{{key}},{EARNS})-'
              f'SUMIFS([[Expense Tracker.profit_cost]],'
              f'[[Expense Tracker.month]],{{key}},'
              f'[[Expense Tracker.is_overhead]],"Yes")', "money")
    month_row("Enquiries",
              'COUNTIFS([[Lead Tracker.month]],{key})', "int")
    month_row("Enquiries booked",
              'COUNTIFS([[Lead Tracker.month]],{key},'
              '[[Lead Tracker.is_won]],"Yes")', "int")
    s.write(row, 1, "Galleries delivered", fmts.chrome("label"))
    for month in range(1, 13):
        s.formula(row, 1 + month,
                  f'=COUNTIFS([[Gallery & Delivery.delivered_num]],'
                  f'">="&DATE(ReportYear,{month},1),'
                  f'[[Gallery & Delivery.delivered_num]],"<="&'
                  f'EOMONTH(DATE(ReportYear,{month},1),0))',
                  fmts.cell("int", "calc"))
    s.formula(row, 14, f"=SUM(C{row + 1}:N{row + 1})",
              fmts.chrome("total_value",
                          num_format=s.num_format("int")))
    row += 1
    month_row("Miles",
              'SUMIFS([[Travel & Mileage.all_miles]],'
              '[[Travel & Mileage.month]],{key})', "number1")

    s.write(row, 1, "Last year's revenue", fmts.chrome("label"))
    for month in range(1, 13):
        key = f'TEXT(DATE(ReportYear-1,{month},1),"yyyy-mm")'
        s.formula(row, 1 + month,
                  f'=SUMIFS([[Wedding Bookings.total_value]],'
                  f'[[Wedding Bookings.month]],{key},{EARNS})',
                  fmts.cell("money", "calc"))
    s.formula(row, 14, f"=SUM(C{row + 1}:N{row + 1})",
              fmts.chrome("total_value",
                          num_format=s.num_format("money")))
    last_year_row = row
    row += 1

    s.write(row, 1, "Change on last year", fmts.chrome("label"))
    for month in range(1, 13):
        letter = col_letter(1 + month)
        s.formula(row, 1 + month,
                  f'=IF({letter}{last_year_row + 1}<=0,"",'
                  f'{letter}{revenue_row + 1}/'
                  f'{letter}{last_year_row + 1}-1)',
                  fmts.cell("percent0", "calc"))
    s.formula(row, 14,
              f'=IF(O{last_year_row + 1}<=0,"",'
              f'O{revenue_row + 1}/O{last_year_row + 1}-1)',
              fmts.chrome("total_value",
                          num_format=s.num_format("percent0")))
    row += 2

    # ---- the year in one glance -------------------------------------------
    row = s.subsection(row, "The year in one glance", LAST_COL)
    year_earns = f'[[Wedding Bookings.year]],ReportYear,{EARNS}'
    s.kpi(row, 1, "Weddings",
          f'=COUNTIFS({year_earns})', "int")
    s.kpi(row, 3, "Against target",
          f'=IF(TargetWeddings<=0,"",COUNTIFS({year_earns})/'
          f'TargetWeddings)', "percent0")
    s.kpi(row, 5, "Revenue",
          f'=SUMIFS([[Wedding Bookings.total_value]],{year_earns})',
          "money0")
    s.kpi(row, 7, "Average wedding",
          f'=IF(COUNTIFS({year_earns})<=0,"",'
          f'SUMIFS([[Wedding Bookings.total_value]],{year_earns})/'
          f'COUNTIFS({year_earns}))', "money0")
    s.kpi(row, 9, "Profit",
          f'=SUMIFS([[Wedding Bookings.profit]],{year_earns})-'
          f'SUMIFS([[Expense Tracker.profit_cost]],'
          f'[[Expense Tracker.year]],ReportYear,'
          f'[[Expense Tracker.is_overhead]],"Yes")', "money0")
    row = s.kpi(row, 11, "Margin",
                f'=IF(SUMIFS([[Wedding Bookings.total_value]],'
                f'{year_earns})<=0,"",'
                f'(SUMIFS([[Wedding Bookings.profit]],{year_earns})-'
                f'SUMIFS([[Expense Tracker.profit_cost]],'
                f'[[Expense Tracker.year]],ReportYear,'
                f'[[Expense Tracker.is_overhead]],"Yes"))/'
                f'SUMIFS([[Wedding Bookings.total_value]],'
                f'{year_earns}))', "percent0")

    s.kpi(row, 1, "Hours shooting",
          f'=SUMIFS([[Wedding Bookings.coverage_hours]],{year_earns})',
          "number1")
    s.kpi(row, 3, "Hours editing",
          '=SUMIFS([[Editing Workflow.hours]],'
          '[[Editing Workflow.booking]],"?*")', "number1",
          note="All recorded editing, not only this year's")
    s.kpi(row, 5, "Equipment owned",
          '=SUM([[Equipment Inventory.price]])', "money0",
          note="What it cost, not what it is worth now")
    s.kpi(row, 7, "Insured value",
          '=SUMIFS([[Equipment Inventory.insured_value]],'
          '[[Equipment Inventory.insured]],"Yes")', "money0")
    s.kpi(row, 9, "Claimable expenses",
          '=SUMIFS([[Expense Tracker.claimable]],'
          '[[Expense Tracker.year]],ReportYear)', "money0",
          note="Your own working figure - not tax advice")
    row = s.kpi(row, 11, "Tax collected",
                f'=SUMIFS([[Wedding Bookings.tax]],{year_earns})',
                "money0",
                note="Only yours to pass on, never to spend")
    row += 1

    row = s.note(
        row,
        "These figures are a management summary built from what you "
        "typed, not a set of accounts. Which costs are deductible, "
        "how equipment is written down and when revenue is "
        "recognised all depend on your country's rules and on how "
        "your business is set up. Give your accountant the Expense "
        "Tracker and the Payments tab, not this page.",
        LAST_COL, height=48)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
