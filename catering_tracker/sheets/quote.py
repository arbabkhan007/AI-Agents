"""
The Quote Calculator: price an event in thirty seconds.

Type the guest count and your costs on the left; the right-hand column
builds the quote with your target margin (from Setup, overridable per
quote), the deposit, and the per-guest numbers caterers actually quote by.
"""

import datetime

from .. import config as C
from ..book import r
from ..styles import wrap_height
from .common import blank_row

Q = C.QUOTE_ROWS      # client 10, date 11, guests 12, food_pp 14, labor 15,
                      # equipment 16, transport 17, other 18, margin 20,
                      # deposit_pct 21
O = C.QUOTE_OUT       # food_total 14, cost_total 15, price 16, per_guest 17,
                      # profit 18, margin 19, deposit 20, balance 21,
                      # cost_pp 22
LAST_COL = "F"

INPUT_ROWS = [
    (Q["client"], "Client / enquiry", "text"),
    (Q["date"], "Event date", "date"),
    (Q["guests"], "Guests", "qty"),
    (Q["food_pp"], "Food cost per guest", "money"),
    (Q["labor"], "Kitchen & service crew", "money"),
    (Q["equipment"], "Equipment & rentals", "money"),
    (Q["transport"], "Transport & fuel", "money"),
    (Q["other"], "Other costs", "money"),
    (Q["margin"], "Target margin", "pct"),
    (Q["deposit_pct"], "Deposit %", "pct"),
]

_OUTPUTS = [
    (O["food_total"], "Food total",
     '=IF($C$%d="","",ROUND($C$%d*$C$%d,2))'
     % (Q["guests"], Q["guests"], Q["food_pp"])),
    (O["cost_total"], "Total cost",
     '=IF($C$%d="","",ROUND($C$%d*$C$%d+$C$%d+$C$%d+$C$%d+$C$%d,2))'
     % (Q["guests"], Q["guests"], Q["food_pp"], Q["labor"],
        Q["equipment"], Q["transport"], Q["other"])),
    (O["price"], "RECOMMENDED PRICE",
     '=IF($E$%d="","",ROUND($E$%d/(1-$C$%d),2))'
     % (O["cost_total"], O["cost_total"], Q["margin"])),
    (O["per_guest"], "Price per guest",
     '=IF($E$%d="","",ROUND($E$%d/$C$%d,2))'
     % (O["price"], O["price"], Q["guests"])),
    (O["profit"], "Profit on the job",
     '=IF($E$%d="","",ROUND($E$%d-$E$%d,2))'
     % (O["price"], O["price"], O["cost_total"])),
    (O["margin"], "Margin",
     '=IFERROR(IF($E$%d="","",$E$%d/$E$%d),"")'
     % (O["profit"], O["profit"], O["price"])),
    (O["deposit"], "Deposit to confirm",
     '=IF($E$%d="","",ROUND($E$%d*$C$%d,2))'
     % (O["price"], O["price"], Q["deposit_pct"])),
    (O["balance"], "Balance after deposit",
     '=IF($E$%d="","",ROUND($E$%d*(1-$C$%d),2))'
     % (O["price"], O["price"], Q["deposit_pct"])),
    (O["cost_pp"], "Cost per guest",
     '=IF($E$%d="","",ROUND($E$%d/$C$%d,2))'
     % (O["cost_total"], O["cost_total"], Q["guests"])),
]

DEMO_FIELDS = {Q["guests"]: "guests", Q["food_pp"]: "food_pp",
               Q["labor"]: "labor", Q["equipment"]: "equipment",
               Q["transport"]: "transport", Q["other"]: "other"}


def build(bk):
    ws = bk.ws("quote")
    S, th = bk.S, bk.th
    demo = bk.demo
    q = demo.quote if demo.demo else {}

    bk.widths("quote", {"A": 2.2, "B": 25, "C": 16, "D": 3, "E": 25,
                        "F": 18, "G": 3})
    for row in range(0, 36):
        ws.set_row(row, 21)

    bk.title_block("quote", "Quote Calculator",
                   "Price an event in 30 seconds - margin, deposit and "
                   "per-guest numbers included", LAST_COL, home=True)

    # ------------------------------------------------------------------
    # two columns: inputs | outputs
    # ------------------------------------------------------------------
    ws.merge_range(r(8), 1, r(8), 2, "1 \u00b7 Your inputs", S.section)
    ws.merge_range(r(8), 3, r(8), 4, "2 \u00b7 The quote (automatic)",
                   S.section_accent)

    lab_fmt = S.f(**S.base(font_size=10.5, bold=True, font_color=th.ink,
                           bg_color=th.card, align="left", valign="vcenter",
                           indent=1, border=1, border_color=th.border))
    defaults = {Q["margin"]: ("=DefaultMargin", demo.settings["margin"]),
                Q["deposit_pct"]: ("=DepositPct", demo.settings["deposit"])}
    for row, label, kind in INPUT_ROWS:
        ws.write(r(row), 1, label, lab_fmt)
        cell = S.cell(kind)
        if row in defaults:
            formula, cached = defaults[row]
            ws.write_formula(r(row), 2, formula, cell, cached)
            bk.stats["formulas"] += 1
        elif q and row == Q["client"]:
            ws.write(r(row), 2, q.get("client", ""), cell)
        elif q and row == Q["date"]:
            ws.write_datetime(r(row), 2, q["date"], cell)
        elif q and row in DEMO_FIELDS:
            ws.write(r(row), 2, q[DEMO_FIELDS[row]], cell)
        else:
            ws.write_blank(r(row), 2, None, cell)

    out_cache = {}
    if q:
        out_cache = {
            O["food_total"]: round(q["food_total"], 2),
            O["cost_total"]: round(q["cost_total"], 2),
            O["price"]: round(q["price"], 2),
            O["per_guest"]: round(q["per_guest"], 2),
            O["profit"]: round(q["profit"], 2),
            O["margin"]: (q["profit"] / q["price"]) if q["price"] else 0,
            O["deposit"]: round(q["deposit"], 2),
            O["balance"]: round(q["balance"], 2),
            O["cost_pp"]: round(q["cost_pp"], 2),
        }
    for row, label, formula in _OUTPUTS:
        big = (row == O["price"])
        lfmt = S.f(**S.base(
            font_size=13 if big else 10.5, bold=True,
            font_color=th.white if big else th.primary,
            bg_color=th.accent if big else th.alt,
            align="left", valign="vcenter", indent=1, border=1,
            border_color=th.accent if big else th.border))
        ws.write(r(row), 3, label, lfmt)
        vfmt = S.kpi_value(th.accent if big else th.primary,
                           num_format="#,##0.00",
                           size=16 if big else 12, align="right")
        ws.write_formula(r(row), 4, formula, vfmt,
                         out_cache.get(row, ""))
        bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # the big callout (rows 24-25)
    # ------------------------------------------------------------------
    callout = S.f(**S.base(
        font_name=th.title_font, font_size=17, bold=True,
        font_color=th.white, bg_color=th.primary, align="center",
        valign="vcenter", text_wrap=True))
    ws.merge_range(r(24), 1, r(25), 5, "", callout)
    ws.write_formula(r(24), 1,
                     '=IF($E$%d="","",Currency&TEXT($E$%d,"#,##0.00")&'
                     '"  for the event   \u00b7   "&Currency&TEXT($E$%d,'
                     '"#,##0.00")&" per guest")'
                     % (O["price"], O["price"], O["per_guest"]),
                     callout,
                     ("%s for the event   \u00b7   %s per guest"
                      % (demo.money(q["price"], 2),
                         demo.money(q["per_guest"], 2))) if q else "")
    bk.stats["formulas"] += 1

    blank_row(bk, "quote", 26, "A", "G", height=8)

    # ------------------------------------------------------------------
    # how it works
    # ------------------------------------------------------------------
    lines = [
        "Price = Total cost \u00f7 (1 - margin).  At a 35% target margin, "
        "$1,000 of costs prices at $1,538 - you keep $538.",
        "The margin and deposit start from your Setup defaults; type over "
        "them here for a one-off quote without changing the defaults.",
        "When they say yes: add the event on the Events tab, the deposit "
        "on the Payments tab, and the ingredients on the Shopping List.",
    ]
    row = 27
    ws.merge_range(r(row), 1, r(row), 5, "How the math works", S.section_soft)
    ws.set_row(r(row), 22)
    row += 1
    for line in lines:
        h = wrap_height("\u2022  " + line, 76, minimum=20)
        ws.merge_range(r(row), 1, r(row), 5, "\u2022  " + line, S.note)
        ws.set_row(r(row), h)
        row += 1

    _validations(bk)
    bk.nav_row("quote", row + 1, first_col=1, span=2, max_col="F")
    bk.page("quote", "G", row + 3, landscape=False, freeze=None, zoom=100)


def _validations(bk):
    ws = bk.ws("quote")
    ws.data_validation(
        r(Q["guests"]), 2, r(Q["guests"]), 2,
        {"validate": "whole", "criteria": "between", "minimum": 1,
         "maximum": 100000, "ignore_blank": True, "show_error": True,
         "error_title": "Guest count", "error_message":
         "Enter the headcount as a whole number.", "error_type": "warning"})
    bk.stats["validations"] += 1
    for row_ in (Q["food_pp"], Q["labor"], Q["equipment"], Q["transport"],
                 Q["other"]):
        ws.data_validation(
            r(row_), 2, r(row_), 2,
            {"validate": "decimal", "criteria": "between", "minimum": 0,
             "maximum": 1000000, "ignore_blank": True, "show_error": True,
             "error_title": "Cost", "error_message":
             "Enter a positive number - no currency symbol.",
             "error_type": "warning"})
        bk.stats["validations"] += 1
    ws.data_validation(
        r(Q["margin"]), 2, r(Q["margin"]), 2,
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 0.9, "ignore_blank": True, "show_error": True,
         "error_title": "Margin", "error_message":
         "Enter a share between 0% and 90%.", "error_type": "warning"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(Q["deposit_pct"]), 2, r(Q["deposit_pct"]), 2,
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 1, "ignore_blank": True, "show_error": True,
         "error_title": "Deposit", "error_message":
         "Enter a share between 0% and 100%.", "error_type": "warning"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(Q["date"]), 2, r(Q["date"]), 2,
        {"validate": "date", "criteria": "between",
         "minimum": datetime.date(2000, 1, 1),
         "maximum": datetime.date(2100, 12, 31),
         "ignore_blank": True, "show_input": True, "input_title": "Date",
         "input_message": "Type a date, or pick one from the calendar.",
         "show_error": True, "error_title": "That's not a date",
         "error_message": "Enter a date between 2000 and 2100.",
         "error_type": "warning"})
    bk.stats["validations"] += 1
