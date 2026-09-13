"""
The Invoice & Proposal tab: a print-ready one-pager.

Fill the white cells once (they are all unlocked); everything else - the
line totals, subtotal, tax, deposit and the big total - calculates
itself.  Print or File > Export as PDF and it lands on a single page in
portrait.
"""

import datetime

from .. import config as C
from ..book import r
from .common import blank_row

LAST_COL = "H"
N_LINES = 8
R_INV = 4            # invoice number / date row
R_BILL = 7           # bill-to block
R_LINES_1 = 12       # first line item
R_SUM = R_LINES_1 + N_LINES + 1


def build(bk):
    ws = bk.ws("invoice")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("invoice", {"A": 2.2, "B": 26, "C": 12, "D": 12, "E": 30,
                          "F": 14, "G": 14, "H": 14, "I": 3})
    for row in range(0, R_SUM + 16):
        ws.set_row(row, 19)

    ws.set_row(r(2), 34)
    ws.merge_range(r(2), 1, r(2), 4, "", S.hero_title)
    ws.write_formula(r(2), 1,
                     '=IF(BusinessName="","Your Catering Business",'
                     'BusinessName)', S.hero_title,
                     demo.settings["business"] or "Your Catering Business")
    bk.stats["formulas"] += 1
    ws.merge_range(r(2), 5, r(2), 7, "", S.hero_count)
    ws.write(r(2), 5, "INVOICE", S.hero_count)

    # ------------------------------------------------------------------
    # meta block (row 4)
    # ------------------------------------------------------------------
    meta_fmt = S.cell("text")
    ws.write(r(4), 1, "Invoice #", _lab(bk))
    ws.write(r(4), 2, "", meta_fmt)
    ws.write_blank(r(4), 2, None, meta_fmt)
    ws.write(r(4), 4, "Date", _lab(bk, align="right"))
    ws.write(r(4), 5, datetime.date.today(), S.cell("date"))
    ws.write(r(5), 1, "Event date", _lab(bk))
    ws.write_blank(r(5), 2, None, S.cell("date"))
    ws.write(r(5), 4, "Valid until", _lab(bk, align="right"))
    ws.write_blank(r(5), 5, None, S.cell("date"))

    # ------------------------------------------------------------------
    # bill to / prepared by (rows 7-9)
    # ------------------------------------------------------------------
    ws.merge_range(r(7), 1, r(7), 3, "BILL TO", S.section_soft)
    ws.merge_range(r(7), 5, r(7), 7, "PREPARED BY", S.section_soft)
    for i in range(3):
        row = 8 + i
        fmt = S.cell("text")
        ws.merge_range(r(row), 1, r(row), 3, "", fmt)
        ws.merge_range(r(row), 5, r(row), 7, "", fmt)
    ws.data_validation(
        r(8), 1, r(8), 1,
        {"validate": "list", "source": "=ClientsList", "ignore_blank":
         True, "show_input": True, "input_title": "Client",
         "input_message": "Pick a client from the Clients tab (or type "
                          "the details)."})
    bk.stats["validations"] += 1

    # ------------------------------------------------------------------
    # line items (rows 12-19)
    # ------------------------------------------------------------------
    ws.merge_range(r(11), 1, r(11), 4, "WHAT YOU'RE BUYING", S.thead)
    ws.write(r(11), 5, "LINE TOTAL", S.thead)
    ws.set_row(r(11), 22)
    for i in range(N_LINES):
        row = R_LINES_1 + i
        alt = (row % 2) == 0
        ws.write_blank(r(row), 1, None, S.cell("text", alt))
        ws.write_blank(r(row), 2, None, S.cell("qty1", alt))
        ws.write_blank(r(row), 3, None, S.cell("money", alt))
        ws.write_blank(r(row), 4, None, S.cell("text", alt))
        ws.write_formula(r(row), 5,
                         '=IF(OR($C%d="",$D%d=""),"",ROUND($C%d*$D%d,2))'
                         % (row, row, row, row),
                         S.cell("calc_money", alt), "")
        bk.stats["formulas"] += 1
    ws.data_validation(
        r(R_LINES_1), 2, r(R_LINES_1 + N_LINES - 1), 2,
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 1000000, "ignore_blank": True, "show_error": True,
         "error_title": "Quantity", "error_message":
         "Enter a positive number.", "error_type": "warning"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(R_LINES_1), 3, r(R_LINES_1 + N_LINES - 1), 3,
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 1000000, "ignore_blank": True, "show_error": True,
         "error_title": "Unit price", "error_message":
         "Enter a positive number - no currency symbol.",
         "error_type": "warning"})
    bk.stats["validations"] += 1

    # ------------------------------------------------------------------
    # totals (right block)
    # ------------------------------------------------------------------
    L1 = R_LINES_1
    L2 = R_LINES_1 + N_LINES - 1
    sums = [
        ("Subtotal", '=ROUND(SUM($F$%d:$F$%d),2)' % (L1, L2), "money"),
        ("Discount", None, "money"),
        ("Taxable subtotal", '=ROUND($F$%d-IF($F$%d="",0,$F$%d),2)'
         % (R_SUM, R_SUM + 1, R_SUM + 1), "money"),
        ("Tax (%s rate from Setup)",
         '=ROUND($F$%d*TaxRate,2)' % (R_SUM + 2,), "money"),
        ("TOTAL DUE", '=ROUND($F$%d+$F$%d,2)'
         % (R_SUM + 2, R_SUM + 3), "money"),
        ("Deposit to confirm (%s from Setup)",
         '=ROUND($F$%d*DepositPct,2)' % (R_SUM + 4,), "money"),
        ("Balance after deposit", '=ROUND($F$%d-$F$%d,2)'
         % (R_SUM + 4, R_SUM + 5), "money"),
    ]
    for i, (label, formula, kind) in enumerate(sums):
        row = R_SUM + i
        big = label == "TOTAL DUE"
        lfmt = S.f(**S.base(
            font_size=13 if big else 10.5, bold=True,
            font_color=th.white if big else th.ink,
            bg_color=th.primary if big else th.alt,
            align="right", valign="vcenter", indent=1, border=1,
            border_color=th.primary if big else th.border))
        ws.merge_range(r(row), 3, r(row), 4,
                       label if "%s" not in label else label % "", lfmt)
        vfmt = S.kpi_value(th.primary, num_format="#,##0.00",
                           size=14 if big else 11, align="right")
        if formula:
            ws.write_formula(r(row), 5, formula, vfmt, "")
            bk.stats["formulas"] += 1
        else:
            ws.write_blank(r(row), 5, None, S.cell("money"))

    # fix the two %-label formulas properly (they need the live rate)
    ws.write_formula(r(R_SUM + 3), 3,
                     '="Tax ("&TEXT(TaxRate,"0.0%%")&" - from Setup)"',
                     S.f(**S.base(font_size=10.5, bold=True,
                                  font_color=th.ink, bg_color=th.alt,
                                  align="right", valign="vcenter", indent=1,
                                  border=1, border_color=th.border)),
                     "Tax (0.0% - from Setup)")
    bk.stats["formulas"] += 1
    ws.write_formula(r(R_SUM + 5), 3,
                     '="Deposit to confirm ("&TEXT(DepositPct,"0%%")&'
                     '" - from Setup)"',
                     S.f(**S.base(font_size=10.5, bold=True,
                                  font_color=th.ink, bg_color=th.alt,
                                  align="right", valign="vcenter", indent=1,
                                  border=1, border_color=th.border)),
                     "Deposit to confirm (0% - from Setup)")
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # terms + signature
    # ------------------------------------------------------------------
    trow = R_SUM + 8
    ws.merge_range(r(trow), 1, r(trow), 4,
                   "Notes & terms", S.section_soft)
    ws.merge_range(r(trow), 5, r(trow), 7, "Signatures", S.section_soft)
    notes = ("Deposit due to confirm the date.  Final balance due 3 days "
             "before the event.  Prices valid for 14 days.")
    from ..styles import wrap_height
    ws.merge_range(r(trow + 1), 1, r(trow + 4), 4, notes, S.note)
    for i in range(2):
        row = trow + 2 + i * 2
        ws.merge_range(r(row), 5, r(row), 6, "", S.cell("text"))
        ws.write(r(row + 1), 5, "Client signature" if i == 0 else "Date",
                 S.footer)
        ws.write_blank(r(row), 7, None, S.cell("text"))
        ws.write(r(row + 1), 7, "For %s" % (demo.settings["business"]
                                            or "the business"), S.footer)

    blank_row(bk, "invoice", trow + 7, "A", LAST_COL, height=6)
    ws.merge_range(r(trow + 8), 1, r(trow + 8), 7,
                   "Print this page (File > Print) - it is set up to fit "
                   "one portrait page.  Amounts use the currency symbol "
                   "from your Setup tab.", S.footer)
    ws.set_row(r(trow + 8), 22)

    bk.nav_row("invoice", trow + 10, first_col=1, span=1, max_col="H")
    bk.page("invoice", "I", trow + 12, landscape=False, freeze=None,
            fit=True, zoom=100, paper=9)


def _lab(bk, align="left"):
    return bk.S.f(**bk.S.base(
        font_size=10.5, bold=True, font_color=bk.th.ink,
        bg_color=bk.th.card, align=align, valign="vcenter", indent=1,
        border=1, border_color=bk.th.border))
