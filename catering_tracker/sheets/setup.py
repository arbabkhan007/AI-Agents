"""
The Setup tab: one screen of settings + every dropdown list in the workbook.

Nothing here is calculated - it is all yours to edit.  The dropdown lists
feed the data-validation on every other tab through OFFSET defined names, so
adding "Barbecue" to the event types makes it appear in every dropdown the
moment you type it.

Row numbers come straight from config.py (SU_* constants), which every other
module - and the defined names - agree on.
"""

from .. import config as C
from ..book import r, ci
from .common import blank_row

LISTS = {
    "event_types": C.EVENT_TYPES,
    "expense_categories": C.EXPENSE_CATEGORIES,
    "payment_methods": C.PAYMENT_METHODS,
    "staff_roles": C.STAFF_ROLES,
    "menu_categories": C.MENU_CATEGORIES,
    "ingredient_categories": C.INGREDIENT_CATEGORIES,
}


def build(bk):
    ws = bk.ws("setup")
    S, th = bk.S, bk.th
    st = bk.demo.settings

    bk.widths("setup", {"A": 2.2, "B": 22, "C": 13, "D": 13, "E": 15,
                        "F": 15, "G": 15, "H": 46, "I": 4})
    for row in range(0, 58):
        ws.set_row(row, 20)
    ws.set_row(r(2), 30)
    ws.set_row(r(3), 18)

    # compact header (the config places the first input at row 6)
    ws.merge_range(r(2), 1, r(2), 5, "Settings & lists", S.sheet_title)
    ws.merge_range(r(2), 6, r(2), 7, "", S.canvas)
    ws.merge_range(r(3), 1, r(3), 5,
                   "Set up once - every tab reads from here", S.sheet_sub)
    ws.merge_range(r(3), 6, r(3), 7, "", S.home_link)
    ws.write_url(r(3), 6, "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                 "\U0001F3E0  Back to Dashboard")
    bk.stats["links"] += 1

    # ------------------------------------------------------------------
    # 1 - your business (rows 6-7)
    # ------------------------------------------------------------------
    ws.merge_range(r(5), 1, r(5), 7, "1 \u00b7 Your business", S.section)
    _label(bk, C.SU_BUSINESS, "Business name")
    _input(bk, C.SU_BUSINESS, st["business"] or "", span=3)
    _hint(bk, C.SU_BUSINESS, "Shown on the Dashboard and the Invoice tab.")
    _label(bk, C.SU_MESSAGE, "Dashboard note")
    _input(bk, C.SU_MESSAGE, st["message"] or "", span=3)
    _hint(bk, C.SU_MESSAGE, "A little reminder for the team - shown under "
                            "the Dashboard title.")

    # ------------------------------------------------------------------
    # 2 - money settings (rows 10-15)
    # ------------------------------------------------------------------
    ws.merge_range(r(9), 1, r(9), 7, "2 \u00b7 Money settings", S.section)
    money_rows = [
        (C.SU_CURRENCY, "Currency symbol", st["currency"], "center",
         "Pick from the dropdown, or type your own symbol."),
        (C.SU_TAX, "Sales tax / VAT rate", st["tax"], "pct",
         "Applied on the Invoice tab and in the Tax Tracker."),
        (C.SU_MARGIN, "Target profit margin", st["margin"], "pct",
         "The Quote Calculator prices events to hit this."),
        (C.SU_DEPOSIT, "Deposit to confirm", st["deposit"], "pct",
         "Suggested deposit share of the total price."),
        (C.SU_DUESOON, "\u201cDue soon\u201d window (days)", st["duesoon"],
         "center", "Dates inside this window glow amber on every tab."),
        (C.SU_YEAR, "Report year", st["year"], "center",
         "Drives the P&L and the Tax Tracker."),
    ]
    for row, label, value, kind, hint in money_rows:
        _label(bk, row, label)
        _input(bk, row, value, span=2, kind=kind)
        _hint(bk, row, hint)

    bk.validate("setup", r(C.SU_CURRENCY), 2, r(C.SU_CURRENCY), 3,
                ",".join(C.CURRENCIES), title="Currency symbol",
                message="Pick a symbol, or type your own (e.g. Rs).",
                error=None)
    _decimal_dv(bk, C.SU_TAX, 0, 0.5)
    _decimal_dv(bk, C.SU_MARGIN, 0, 0.9)
    _decimal_dv(bk, C.SU_DEPOSIT, 0, 1)
    _whole_dv(bk, C.SU_DUESOON, 1, 90, "1 - 90 days",
              "Pick a window between 1 and 90 days.")
    _whole_dv(bk, C.SU_YEAR, 2000, 2100, "Year",
              "Enter a 4-digit year.")

    # ------------------------------------------------------------------
    # 3 - calendar (rows 18-19)
    # ------------------------------------------------------------------
    ws.merge_range(r(17), 1, r(17), 7, "3 \u00b7 Calendar", S.section)
    _label(bk, C.SU_CAL_MONTH, "Month to show")
    _label(bk, C.SU_CAL_YEAR, "Year to show")
    month_fmt = bk.S.cell("center", num_format="mmmm")
    bk.ws("setup").merge_range(r(C.SU_CAL_MONTH), 2, r(C.SU_CAL_MONTH), 3,
                               "", month_fmt)
    bk.ws("setup").write(r(C.SU_CAL_MONTH), 2, st["cal_month"], month_fmt)
    _input(bk, C.SU_CAL_YEAR, st["cal_year"], span=2, kind="center")
    _hint(bk, C.SU_CAL_MONTH, "The Event Calendar tab shows this month "
                              "(1 = January ... 12 = December).")
    _hint(bk, C.SU_CAL_YEAR, "")
    bk.ws("setup").data_validation(
        r(C.SU_CAL_MONTH), 2, r(C.SU_CAL_MONTH), 3,
        {"validate": "whole", "criteria": "between", "minimum": 1,
         "maximum": 12, "ignore_blank": True, "show_input": True,
         "input_title": "Month",
         "input_message": "1 = January ... 12 = December.  The cell "
                          "shows the month name."})
    bk.stats["validations"] += 1
    _whole_dv(bk, C.SU_CAL_YEAR, 2000, 2100, "Year",
              "Enter a 4-digit year.")

    # ------------------------------------------------------------------
    # 4 - editable lists (header 22, items 23-42)
    # ------------------------------------------------------------------
    ws.merge_range(r(C.SU_LIST_HEADER - 1), 1, r(C.SU_LIST_HEADER - 1), 7,
                   "4 \u00b7 Your dropdown lists (edit freely)",
                   S.section_gold)
    for key, col in sorted(C.LIST_COLS.items()):
        ws.write(r(C.SU_LIST_HEADER), ci(col) - 1, C.LIST_TITLES[key],
                 S.thead)
    for key, col in sorted(C.LIST_COLS.items()):
        for i in range(C.SU_LIST_ROWS):
            row = C.SU_LIST_FIRST + i
            fmt = S.cell("text", (row % 2) == 0)
            val = LISTS[key][i] if i < len(LISTS[key]) else None
            if val is None:
                ws.write_blank(r(row), ci(col) - 1, None, fmt)
            else:
                ws.write(r(row), ci(col) - 1, val, fmt)

    # ------------------------------------------------------------------
    # 5 - fixed lists (header 46, items 47+)
    # ------------------------------------------------------------------
    ws.merge_range(r(C.SU_FIXED_HEADER - 2), 1, r(C.SU_FIXED_HEADER - 2), 7,
                   "5 \u00b7 Fixed lists (the status formulas depend on "
                   "these exact texts - locked)", S.section_soft)
    fixed = {"event_statuses": C.EVENT_STATUSES,
             "payment_statuses": C.PAYMENT_STATUSES,
             "tick": [C.TICK]}
    heads = {"event_statuses": "Event statuses",
             "payment_statuses": "Payment statuses", "tick": "Tick"}
    for key, col in sorted(C.FIXED_COLS.items()):
        ws.write(r(C.SU_FIXED_HEADER), ci(col) - 1, heads[key], S.thead)
        for i, val in enumerate(fixed[key]):
            row = C.SU_FIXED_FIRST + i
            ws.write(r(row), ci(col) - 1, val, S.cell("center"))
    for i in range(len(C.EVENT_STATUSES)):        # colour the status chips
        row = C.SU_FIXED_FIRST + i
        colour = [th.info, th.plum, th.warn, th.ok, th.gold, th.bad][i]
        ws.write(r(row), ci("C") - 1, C.EVENT_STATUSES[i], bk.S.cf(
            bg=th.soft(["info", "plum", "warn", "ok", "gold", "bad"][i]),
            fg=colour, bold=True, border=th.border))

    last = C.SU_FIXED_FIRST + 8
    blank_row(bk, "setup", last, "A", "H", height=8)
    ws.merge_range(r(last + 1), 1, r(last + 1), 7,
                   "Tip: empty rows in a list simply don't appear in the "
                   "dropdowns.  Add options at the bottom of a column and "
                   "they show up everywhere, instantly.", S.note)
    ws.set_row(r(last + 1), 30)

    bk.nav_row("setup", last + 3, first_col=1, span=1, max_col="H")
    bk.page("setup", "H", last + 5, landscape=False, freeze=None,
            fit=True, zoom=100)


# ----------------------------------------------------------------------
# little cell writers
# ----------------------------------------------------------------------
def _label(bk, row, text):
    fmt = bk.S.f(**bk.S.base(
        font_size=10.5, bold=True, font_color=bk.th.ink,
        bg_color=bk.th.card, align="left", valign="vcenter", indent=1,
        border=1, border_color=bk.th.border))
    bk.ws("setup").write(r(row), 1, text, fmt)


def _input(bk, row, value, span=2, kind="text"):
    ws = bk.ws("setup")
    fmt = bk.S.cell(kind)
    if span > 1:
        ws.merge_range(r(row), 2, r(row), 1 + span, "", fmt)
    if value == "" or value is None:
        ws.write_blank(r(row), 2, None, fmt)
    else:
        ws.write(r(row), 2, value, fmt)


def _hint(bk, row, text):
    if not text:
        return
    bk.ws("setup").write(r(row), 7, text, bk.S.note_plain)


def _decimal_dv(bk, row, lo, hi):
    bk.ws("setup").data_validation(
        r(row), 2, r(row), 3,
        {"validate": "decimal", "criteria": "between", "minimum": lo,
         "maximum": hi, "ignore_blank": True, "show_error": True,
         "error_title": "Pick a percentage", "error_message":
         "Enter a share of the price between %d%% and %d%%."
         % (lo * 100, hi * 100), "error_type": "warning"})
    bk.stats["validations"] += 1


def _whole_dv(bk, row, lo, hi, title, message):
    bk.ws("setup").data_validation(
        r(row), 2, r(row), 3,
        {"validate": "whole", "criteria": "between", "minimum": lo,
         "maximum": hi, "ignore_blank": True, "show_error": True,
         "error_title": title, "error_message": message,
         "error_type": "warning"})
    bk.stats["validations"] += 1
