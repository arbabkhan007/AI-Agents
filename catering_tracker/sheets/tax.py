"""
The Tax Tracker: sales tax estimated, filed, and still due.

The summary block pulls the year's invoiced sales, applies your Setup tax
rate, and subtracts what you have already filed and paid (the log below).
It is an organiser, not an accountant - but it means no more 11pm
spreadsheet archaeology every quarter.
"""

from datetime import date

from .. import config as C
from ..book import r, ci
from .common import blank_row

T = C.TAX_SUM          # sales 9, rate 10, collected 11, paid 12, due 13
LOG_FIRST = C.TAX_LOG_FIRST
LOG_ROWS = C.TAX_LOG_ROWS
LAST_COL = "J"

Y0 = "DATE(ReportYear,1,1)"
Y1 = "DATE(ReportYear,12,31)"


def build(bk):
    ws = bk.ws("tax")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("tax", {"A": 2.2, "B": 4.5, "C": 13, "D": 30, "E": 12,
                      "F": 13, "G": 12, "H": 15, "I": 3, "J": 3})
    for row in range(0, 52):
        ws.set_row(row, 19)

    bk.title_block("tax", "Tax Tracker",
                   "Sales tax estimated, filed and still due - the honest "
                   "picture", LAST_COL)

    inc = bk.q("income")
    I_DATE = bk.rng("income", "event_date")
    I_AMT = bk.rng("income", "amount")

    bk.stats_strip("tax", [
        ('="Report year: "&ReportYear', "accent",
         "Report year: %s" % demo.settings["year"]),
        # single % only - a %% here reaches Excel literally (it is not
        # Python-escaped: no % operator is applied to this string)
        ('="Tax rate: "&TEXT(TaxRate,"0.0%")', "info",
         "Tax rate: %.1f%%" % (100 * demo.settings["tax"])),
        ('="Collected to date: "&Currency&TEXT(%s,"#,##0.00")'
         % bk.kpi("tax_collected"), "gold",
         "Collected to date: %s" % demo.money(
             bk.cached("tax_collected", 0), 2)),
        ('="Still due: "&Currency&TEXT(%s,"#,##0.00")' % bk.kpi("tax_due"),
         "bad", "Still due: %s" % demo.money(bk.cached("tax_due", 0), 2)),
    ])

    # ------------------------------------------------------------------
    # summary block (column C, rows fixed - the KPI table reads them)
    # ------------------------------------------------------------------
    ws.merge_range(r(T["sales"] - 2), 1, r(T["sales"] - 2), 7,
                   "The estimate", S.section)
    rows = [
        (T["sales"], "Sales subject to tax (invoiced, year)",
         '=SUMIFS(%s,%s,">="&%s,%s,"<="&%s)'
         % (I_AMT, I_DATE, Y0, I_DATE, Y1), "money",
         round(sum(i["amount"] for i in demo.income
                   if i["event_date"].year == demo.settings["year"]), 2)),
        (T["rate"], "Your tax rate (from Setup)", "=TaxRate", "pct",
         demo.settings["tax"]),
        (T["collected"], "Tax collected on those sales",
         '=ROUND($C$%d*$C$%d,2)' % (T["sales"], T["rate"]), "money",
         bk.cached("tax_collected", 0)),
        (T["paid"], "Tax already filed & paid",
         '=SUM($G$%d:$G$%d)' % (LOG_FIRST, LOG_FIRST + LOG_ROWS - 1),
         "money",
         round(sum(t["amount"] for t in demo.tax_paid), 2)),
        (T["due"], "ESTIMATED TAX STILL DUE",
         '=ROUND($C$%d-$C$%d,2)' % (T["collected"], T["paid"]), "money",
         bk.cached("tax_due", 0)),
    ]
    for row, label, formula, kind, cached in rows:
        big = label.startswith("ESTIMATED")
        vfmt = S.kpi_value(th.primary, num_format="#,##0.00" if kind ==
                           "money" else "0%", size=14 if big else 12,
                           align="right")
        ws.write_formula(r(row), 2, formula, vfmt, cached)
        lfmt = S.f(**S.base(
            font_size=12 if big else 10.5, bold=True,
            font_color=th.white if big else th.ink,
            bg_color=th.primary if big else th.card, align="left",
            valign="vcenter", indent=1, border=1,
            border_color=th.primary if big else th.border))
        ws.merge_range(r(row), 3, r(row), 7, label, lfmt)
        bk.stats["formulas"] += 1
    ws.merge_range(r(T["due"] + 2), 1, r(T["due"] + 2), 7,
                   "Estimates only - rates and rules vary by country and "
                   "state.  Share this sheet with your accountant, keep "
                   "the filings log below up to date, and you'll never "
                   "dread a quarter-end again.", S.note)
    ws.set_row(r(T["due"] + 2), 30)

    # ------------------------------------------------------------------
    # filings log (header 19, rows 20-39)
    # ------------------------------------------------------------------
    ws.merge_range(r(C.TAX_LOG_HDR - 1), 1, r(C.TAX_LOG_HDR - 1), 7,
                   "Filings & payments log", S.section_gold)
    heads = [("B", "#", "idx", None), ("C", "Date", "date", "gold"),
             ("D", "What was filed / paid", "text", "accent"),
             ("E", "Reference", "center", None),
             ("F", "Type", "center", None),
             ("G", "Amount", "money", "bad"),
             ("H", "Paid by", "center", None)]
    for colL, label, kind, color in heads:
        ws.write(r(C.TAX_LOG_HDR), ci(colL) - 1, label, S.thead)
    ws.set_row(r(C.TAX_LOG_HDR), 22)
    for i in range(LOG_ROWS):
        row = LOG_FIRST + i
        ws.set_row(r(row), 19)
        for colL, label, kind, color in heads:
            fmt = S.idx((row % 2) == 0) if kind == "idx" else \
                S.cell(kind, (row % 2) == 0)
            ws.write_blank(r(row), ci(colL) - 1, None, fmt)
        ws.write_formula(r(row), 1,
                         # log starts at LOG_FIRST, not ROW_FIRST
                         '=IF($C%d="","",ROW()-%d)' % (row, LOG_FIRST - 1),
                         S.idx((row % 2) == 0), i + 1 if demo.demo and
                         i < len(demo.tax_paid) else "")
        bk.stats["formulas"] += 1
        if demo.demo and i < len(demo.tax_paid):
            t = demo.tax_paid[i]
            ws.write_datetime(r(row), 2, t["date"], S.cell("date"))
            ws.write(r(row), 3, t["desc"], S.cell("text"))
            ws.write(r(row), 4, "Q%d-%d" % ((t["date"].month - 1) // 3 + 1,
                                             t["date"].year),
                     S.cell("center"))
            ws.write(r(row), 5, "Sales tax" if "sales" in t["desc"].lower()
                     else "Income tax", S.cell("center"))
            ws.write(r(row), 6, t["amount"], S.cell("money"))
            ws.write(r(row), 7, "Bank Transfer", S.cell("center"))

    # validations
    ws.data_validation(
        r(LOG_FIRST), ci("H"), r(LOG_FIRST + LOG_ROWS - 1), ci("H"),
        {"validate": "list", "source": "=PaymentMethods",
         "ignore_blank": True, "show_input": True, "input_title":
         "Paid by", "input_message": "How was the payment made?"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(LOG_FIRST), ci("G"), r(LOG_FIRST + LOG_ROWS - 1), ci("G"),
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 10000000, "ignore_blank": True, "show_error": True,
         "error_title": "Amount", "error_message":
         "Enter the amount as a positive number.", "error_type":
         "warning"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(LOG_FIRST), ci("C"), r(LOG_FIRST + LOG_ROWS - 1), ci("C"),
        {"validate": "date", "criteria": "between",
         "minimum": date(2000, 1, 1), "maximum": date(2100, 12, 31),
         "ignore_blank": True, "show_input": True, "input_title": "Date",
         "input_message": "When was it filed / paid?",
         "show_error": True, "error_title": "That's not a date",
         "error_message": "Enter a date between 2000 and 2100.",
         "error_type": "warning"})
    bk.stats["validations"] += 1

    # totals for the log
    ws.merge_range(r(LOG_FIRST + LOG_ROWS), 1, r(LOG_FIRST + LOG_ROWS), 5,
                   "FILED & PAID", S.f(**S.base(
                       font_size=11, bold=True, font_color=th.white,
                       bg_color=th.primary, align="right",
                       valign="vcenter", border=1,
                       border_color=th.primary, indent=1)))
    tfmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                        bg_color=th.primary, align="right", valign="vcenter",
                        border=1, border_color=th.primary,
                        num_format="#,##0.00"))
    ws.write_formula(r(LOG_FIRST + LOG_ROWS), 6,
                     "=SUM($G$%d:$G$%d)" % (LOG_FIRST,
                                            LOG_FIRST + LOG_ROWS - 1),
                     tfmt, round(sum(t["amount"] for t in demo.tax_paid), 2))
    bk.stats["formulas"] += 1

    blank_row(bk, "tax", LOG_FIRST + LOG_ROWS + 2, "A", "H", height=8)
    bk.nav_row("tax", LOG_FIRST + LOG_ROWS + 4, first_col=1, span=1,
               max_col="H")
    bk.page("tax", "J", LOG_FIRST + LOG_ROWS + 6, landscape=False,
            freeze=None, zoom=100)
