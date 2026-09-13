"""
Start Here: the cover page and the manual.

A watercolour banner across the top (with a see-through window so the
title shows through), a three-step quick start, a linked directory of
every tab, and the house rules.  This is the page a buyer opens first,
so it is the page that has to answer everything.
"""

import os

from .. import config as C
from ..book import r
from ..styles import wrap_height
from .common import blank_row

BANNER_ROWS = 15                 # rows 1-15 hold the artwork
BANNER_ROW_H = 26                # px

TAB_INFO = [
    ("dashboard", "Your live scorecards and charts - everything on this "
                  "page updates itself."),
    ("setup", "Your business name, currency, margins and every dropdown "
              "list.  Start here."),
    ("clients", "Who you cook for - quotes, deposits and balances."),
    ("events", "Every booking: costs, pricing, profit and the status "
               "pipeline."),
    ("quote", "Price an event in 30 seconds - margin and deposit "
              "included."),
    ("menu", "Cost each dish, set the price, watch the margin."),
    ("inventory", "Stock levels, values and automatic reorder alerts."),
    ("shopping", "What to buy per event, minus what you already have."),
    ("expenses", "Every cost, categorised - feeds the P&L and the "
                 "doughnut chart."),
    ("income", "Invoices, deposits and who still owes what."),
    ("staff", "Shifts, rates, overtime and the wage bill."),
    ("equipment", "What you own, what's reserved, what needs a service."),
    ("suppliers", "Who sells what, at what price, on what terms."),
    ("calendar", "The month at a glance - events and payment deadlines "
                 "marked."),
    ("reports", "Profit & loss, cash by month, top clients and "
                "categories."),
    ("tax", "Sales tax estimated, filed and still due."),
    ("checklists", "Prep, shopping, day-of and wrap-up lists with "
                   "progress bars."),
    ("invoice", "A print-ready one-page invoice / proposal."),
    ("guide", "This page."),
]

CAPACITY = {"clients": 40, "events": 40, "menu": 30, "inventory": 40,
            "shopping": 40, "expenses": 60, "income": 60, "staff": 50,
            "equipment": 35, "suppliers": 30}


def build(bk):
    ws = bk.ws("guide")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("guide", {"A": 2.2, "B": 15, "C": 15, "D": 14, "E": 14,
                        "F": 14, "G": 14, "H": 14, "I": 3})
    for row in range(0, 96):
        ws.set_row(row, 19)

    # ------------------------------------------------------------------
    # the cover banner (rows 1-15)
    # ------------------------------------------------------------------
    for row in range(1, BANNER_ROWS + 1):
        ws.set_row(r(row), BANNER_ROW_H)
    banner = _banner_path(bk)
    if banner:
        ws.insert_image(r(1), 0, banner,
                        {"x_scale": 0.62, "y_scale": 0.62})
        title_fmt = S.f(**S.base(
            font_name=th.title_font, font_size=30, bold=True,
            font_color=th.primary, bg_color=th.bg, align="left",
            valign="vcenter"))
        sub_fmt = S.f(**S.base(
            font_size=12, font_color=th.ink, bg_color=th.bg, align="left",
            valign="vcenter"))
        ws.merge_range(r(5), 1, r(7), 7, "", title_fmt)
        ws.write(r(5), 1, C.PRODUCT, title_fmt)
        ws.merge_range(r(8), 1, r(9), 7, "", sub_fmt)
        ws.write(r(8), 1, "%s  \u00b7  by %s  \u00b7  v%s"
                 % (C.TAGLINE, C.AUTHOR, C.VERSION), sub_fmt)
        note_fmt = S.f(**S.base(
            font_size=11, italic=True, font_color=th.muted,
            bg_color=th.bg, align="left", valign="vcenter"))
        ws.merge_range(r(11), 1, r(12), 5, "", note_fmt)
        ws.write(r(11), 1,
                 "Works in Microsoft Excel (2016 and newer) and Google "
                 "Sheets - no macros, nothing to install.", note_fmt)
    else:
        ws.merge_range(r(2), 1, r(6), 7, "", S.hero_title)
        ws.write(r(2), 1, C.PRODUCT, S.hero_title)
        ws.merge_range(r(7), 1, r(8), 7, "", S.hero_meta)
        ws.write(r(7), 1, "%s  \u00b7  by %s  \u00b7  v%s"
                 % (C.TAGLINE, C.AUTHOR, C.VERSION), S.hero_meta)

    row = BANNER_ROWS + 2

    # ------------------------------------------------------------------
    # welcome
    # ------------------------------------------------------------------
    ws.merge_range(r(row), 1, r(row), 7, "Welcome", S.section)
    row += 1
    if demo.demo:
        text = ("You're holding the EXAMPLE edition, filled with a "
                "sample business (Saffron & Sage Catering Co.) so you can "
                "see every moving part working.  Explore the tabs, then "
                "clear the white input cells and make it yours.")
    else:
        text = ("This is your whole catering operation in one file: "
                "clients, events, quotes, menu costs, inventory, "
                "shopping, staff, equipment, money and tax - with a "
                "dashboard that adds it all up for you.")
    row = _para(bk, row, text)
    row += 1

    # ------------------------------------------------------------------
    # quick start
    # ------------------------------------------------------------------
    ws.merge_range(r(row), 1, r(row), 7, "Start in three steps", S.section)
    row += 1
    steps = [
        "Open the Setup tab: type your business name, pick your currency "
        "and set your target margin and deposit %.",
        "Add your first event on the Events tab - cost, price, deposit, "
        "status.  The Dashboard, Calendar and P&L update instantly.",
        "Log the deposit on the Payments tab and the ingredients on the "
        "Shopping List.  That's the whole loop - repeat and grow.",
    ]
    for i, step in enumerate(steps):
        num_fmt = S.f(**S.base(
            font_name=th.title_font, font_size=15, bold=True,
            font_color=th.white, bg_color=th.accent, align="center",
            valign="vcenter", border=1, border_color=th.accent))
        ws.merge_range(r(row), 1, r(row + 1), 1, str(i + 1), num_fmt)
        row = _para(bk, row, step, start_col=2, cols=6, tall=True)
        row += 1
    row += 1

    # ------------------------------------------------------------------
    # tab directory
    # ------------------------------------------------------------------
    ws.merge_range(r(row), 1, r(row), 7, "What each tab does", S.section)
    row += 1
    for key, blurb in TAB_INFO:
        if not bk.has(key):
            continue
        color = th.tabs[key]
        link_fmt = S.f(**S.base(
            font_size=10.5, bold=True, font_color=color,
            bg_color=th.card, align="left", valign="vcenter", indent=1,
            border=1, border_color=th.border, underline=1))
        ws.merge_range(r(row), 1, r(row), 2, "", link_fmt)
        ws.write_url(r(row), 1, "internal:%s!A1" % bk.q(key), link_fmt,
                     C.SHEET_NAMES[key])
        bk.stats["links"] += 1
        d_fmt = S.f(**S.base(font_size=10, font_color=th.ink,
                             bg_color=th.card, align="left",
                             valign="vcenter", indent=1, border=1,
                             border_color=th.border, text_wrap=True))
        ws.merge_range(r(row), 3, r(row), 7, blurb, d_fmt)
        ws.set_row(r(row), max(19, wrap_height(blurb, 62, minimum=16)))
        row += 1
    row += 1

    # ------------------------------------------------------------------
    # the rules
    # ------------------------------------------------------------------
    ws.merge_range(r(row), 1, r(row), 7, "The house rules", S.section)
    row += 1
    rules = [
        "Type only in the white cells.  Tinted columns calculate "
        "themselves - if you type over one you'll get the number back on "
        "the next edit anyway.",
        "Every formula is protected, so a stray keystroke can't break "
        "the file.  All the input cells stay open; if you ever need to "
        "change a formula, use Review \u203a Unprotect Sheet and it's "
        "yours.",
        "Dropdowns: click a cell and pick.  The lists live on the Setup "
        "tab - add your own options whenever you like and every dropdown "
        "updates.",
        "Dates: type them in almost any format (\u201c15 Oct 2026\u201d "
        "works) or double-click and pick from the calendar.",
        "Room to grow: Clients holds %d rows, Events %d, Expenses %d, "
        "Payments %d, Menu %d.  Need more?  Right-click a row number "
        "inside a table and choose Insert."
        % (CAPACITY["clients"], CAPACITY["events"], CAPACITY["expenses"],
           CAPACITY["income"], CAPACITY["menu"]),
        "Google Sheets: upload the file to Google Drive and open it with "
        "Google Sheets - formulas, dropdowns, colours and charts all "
        "carry over.",
    ]
    for rule in rules:
        row = _para(bk, row, rule, bullet=True)
    row += 1

    # ------------------------------------------------------------------
    # edition note + licence
    # ------------------------------------------------------------------
    if demo.demo:
        ws.merge_range(r(row), 1, r(row), 7,
                       "About this EXAMPLE edition", S.section_soft)
        row += 1
        row = _para(bk, row,
                    "The sample data belongs to a fictional company.  To "
                    "start fresh: go to each tab, select the white input "
                    "cells (not the tinted ones) and press Delete.  The "
                    "Setup tab is yours to overwrite too.")
        row += 1
    ws.merge_range(r(row), 1, r(row), 7, "Licence & support", S.section)
    row += 1
    row = _para(bk, row,
                "Personal licence: one purchase, use it for your own "
                "business forever, on as many of your own devices as you "
                "like.  Please don't resell or share the file.  Stuck, "
                "or spotted something odd?  Message us through the shop "
                "- we read and answer everything.  \u2014 %s" % C.AUTHOR)
    row += 1

    blank_row(bk, "guide", row, "A", "H", height=8)
    bk.nav_row("guide", row + 2, first_col=1, span=2, max_col="H")
    bk.page("guide", "I", row + 4, landscape=False, freeze=None,
            fit=True, zoom=100)


# ----------------------------------------------------------------------
def _banner_path(bk):
    if not bk.images:
        return None
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    path = os.path.join(root, "assets", "banner_%s.png" % bk.th.key)
    return path if os.path.exists(path) else None


def _para(bk, row, text, start_col=1, cols=7, bullet=False, tall=False):
    """One merged, wrapped paragraph; returns the next row to use."""
    ws = bk.ws("guide")
    S, th = bk.S, bk.th
    txt = ("\u2022  " + text) if bullet else text
    if bullet:
        start_col, cols = 2, 6
    fmt = S.guide_text(size=10.5)
    width = sum((C.WIDTHS.get("guide", {}) or {}).get(_cl(c), 14)
                for c in range(start_col, start_col + cols))
    h = wrap_height(txt, width, minimum=24 if tall else 19)
    if bullet:
        ws.write_blank(r(row), 1, None, S.f(**S.base(
            bg_color=th.card, border=1, border_color=th.border)))
    ws.merge_range(r(row), start_col, r(row), start_col + cols - 1, txt,
                   fmt)
    ws.set_row(r(row), h)
    return row + 1


def _cl(index):
    s = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        s = chr(65 + rem) + s
    return s
