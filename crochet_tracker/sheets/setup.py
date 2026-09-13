"""
Lists & Settings - the control panel.

Studio name, money settings and every editable dropdown list live here.
All of it feeds the rest of the workbook through defined names
(BusinessName, Currency, ReportYear, HourlyWage, OverheadPct, TargetMargin
and the OFFSET-backed list names).
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "J"

_SETTING_ROWS = [
    (C.SU_CURRENCY, "Currency symbol", "text", "currency",
     "Every money column shows this symbol."),
    (C.SU_YEAR, "Report year", "num", "year",
     "The Dashboard's month chart follows this year."),
    (C.SU_WAGE, "Your hourly wage", "money", "wage",
     "Used by the Pricing Calculator to pay yourself properly."),
    (C.SU_OVERHEAD, "Overhead %", "pct", "overhead",
     "Card fees, electricity, glue, parking... a little on top of "
     "everything."),
    (C.SU_MARGIN, "Target profit margin", "pct", "margin",
     "The default margin the Pricing Calculator aims for."),
]

_DEFAULTS = {"currency": "$", "year": 2026, "wage": 15.0, "overhead": 0.10,
             "margin": 0.45}


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("setup")
    demo = bk.demo

    common.sheet_head(bk, "setup", LAST_COL, "\u2699\uFE0F  Lists & Settings",
                      "Your studio basics + every dropdown list in one place")

    # ------------------------------------------------ your studio block
    ws.set_row(r(5), 24)
    bk.band("setup", 5, 1, ci(LAST_COL), S.section, height=24)
    ws.write(r(5), 1, "  Your studio", S.section)

    def label(row, text):
        ws.write(r(row), ci("B"), text, S.f(**S.base(
            font_size=10.5, bold=True, font_color=th.ink, bg_color=th.card,
            align="left", valign="vcenter", border=1, border_color=th.border,
            indent=1, locked=True)))

    def input_note(row, text):
        ws.merge_range(r(row), ci("E"), r(row), ci(LAST_COL), text,
                       S.f(**S.base(font_size=9.5, italic=True,
                                    font_color=th.muted, bg_color=th.card,
                                    align="left", valign="vcenter",
                                    border=1, border_color=th.border,
                                    indent=1)))

    ws.set_row(r(C.SU_BUSINESS), 26)
    ws.set_row(r(C.SU_MESSAGE), 26)
    label(C.SU_BUSINESS, "Business name")
    ws.merge_range(r(C.SU_BUSINESS), ci("C"), r(C.SU_BUSINESS), ci("D"), "",
                   S.cell("text"))
    ws.write(r(C.SU_BUSINESS), ci("C"),
             demo.settings["business"] if demo else "", S.cell("text"))
    input_note(C.SU_BUSINESS, "Shown big on the Dashboard banner.")

    label(C.SU_MESSAGE, "Season note")
    ws.merge_range(r(C.SU_MESSAGE), ci("C"), r(C.SU_MESSAGE), ci("D"), "",
                   S.cell("text"))
    ws.write(r(C.SU_MESSAGE), ci("C"),
             demo.settings["message"] if demo else "", S.cell("text"))
    input_note(C.SU_MESSAGE, "A little reminder for yourself (optional).")

    # ------------------------------------------------ money & targets
    ws.set_row(r(9), 24)
    bk.band("setup", 9, 1, ci(LAST_COL), S.section_accent, height=24)
    ws.write(r(9), 1, "  Money & targets", S.section_accent)
    for row, lab, kind, vkey, note in _SETTING_ROWS:
        ws.set_row(r(row), 24)
        label(row, lab)
        if kind == "num":
            fmt = S.cell("num", num_format="0")
        elif kind == "pct":
            fmt = S.cell("pct", num_format="0%")
        else:
            fmt = S.cell(kind)
        value = (demo.settings[vkey] if demo else _DEFAULTS[vkey])
        ws.write(r(row), ci("C"), value, fmt)
        input_note(row, note)

    # currency + numeric guards
    bk.ws("setup").data_validation(
        r(C.SU_CURRENCY), ci("C"), r(C.SU_CURRENCY), ci("C"),
        {"validate": "list",
         "source": ["$", "\u00A3", "\u20AC", "\u20B9", "\u00A5", "kr",
                    "R$", "A$", "C$", "CHF"],
         "ignore_blank": True, "show_error": True,
         "error_title": "Pick a symbol",
         "error_message": "Choose a currency symbol from the dropdown.",
         "error_type": "warning"})
    bk.stats["validations"] += 1
    for row, lo, hi, msg in [
            (C.SU_YEAR, 2020, 2100, "a year (2020-2100)"),
            (C.SU_WAGE, 0, 10000, "an hourly wage")]:
        bk.ws("setup").data_validation(
            r(row), ci("C"), r(row), ci("C"),
            {"validate": "decimal", "criteria": "between", "minimum": lo,
             "maximum": hi, "ignore_blank": True, "show_error": True,
             "error_title": "Check the number",
             "error_message": "Please enter %s." % msg,
             "error_type": "warning"})
        bk.stats["validations"] += 1
    for row in (C.SU_OVERHEAD, C.SU_MARGIN):
        bk.ws("setup").data_validation(
            r(row), ci("C"), r(row), ci("C"),
            {"validate": "decimal", "criteria": "between", "minimum": 0,
             "maximum": 0.9, "ignore_blank": True, "show_error": True,
             "error_title": "Enter a percentage",
             "error_message": "Type a percentage between 0% and 90% - "
                              "e.g. 10% or 45%.",
             "error_type": "warning"})
        bk.stats["validations"] += 1

    # ------------------------------------------------- how lists work
    note = ("These five columns feed every dropdown in the workbook. Rename "
            "anything, add new rows or delete ones you don't use - the "
            "dropdowns update automatically. Keep each list inside its own "
            "column and leave no big gaps between entries.")
    ws.merge_range(r(16), 1, r(18), ci(LAST_COL), note, S.note)
    for rr in range(16, 19):
        ws.set_row(r(rr), 16)

    # ----------------------------------------------- editable lists
    ws.set_row(r(C.SU_LIST_HEADER), 26)
    colors = {"categories": "accent", "payments": "ok", "weights": "plum",
              "units": "info", "suppliers": "gold"}
    for key, col in sorted(C.LIST_COLS.items(), key=lambda kv:
                           ci(kv[1])):
        fmt = S.header(getattr(th, colors[key]))
        ws.write(r(C.SU_LIST_HEADER), ci(col), C.LIST_TITLES[key], fmt)
    for i in range(C.SU_LIST_ROWS):
        rownum = C.SU_LIST_FIRST + i
        a = common.alt(rownum)
        ws.set_row(r(rownum), 18)
        for key, col in C.LIST_COLS.items():
            values = C.LIST_VALUES[key]
            value = values[i] if i < len(values) else None
            ws.write(r(rownum), ci(col), value, S.cell("text", a))

    # --------------------------------------------------- fixed lists
    ws.set_row(r(44), 24)
    bk.band("setup", 44, 1, ci(LAST_COL), S.section_gold, height=24)
    ws.write(r(44), 1, "  Built-in marks (fixed)", S.section_gold)
    fix_note = ("The tick marks below power every \u2713 box in the "
                "workbook. They're fixed on purpose so the green tick "
                "highlights keep working - just pick them from the "
                "dropdowns.")
    ws.merge_range(r(45), 1, r(45), ci(LAST_COL), fix_note, S.note)
    ws.set_row(r(45), 30)
    ws.write(r(C.SU_FIXED_HEADER), ci("C"), "Tick marks", S.header(th.plum))
    ws.write(r(C.SU_FIXED_FIRST), ci("C"), C.TICK, S.cell("tick"))
    ws.write(r(C.SU_FIXED_FIRST + 1), ci("C"), "\u2717 Skip",
             S.cell("center"))

    # --------------------------------------------------------- footer
    common.footer_nav(
        bk, "setup", 52, LAST_COL,
        tip="  \U0001F4A1  Change a setting once and every sheet follows - "
            "currency, year, wage and dropdowns all live here.")
    ws.set_zoom(100)
