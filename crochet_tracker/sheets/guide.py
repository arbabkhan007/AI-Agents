"""
Start Here - the welcome tab.

A friendly onboarding page: what this workbook is, a three-minute setup,
a tour of every tab, the golden rules and workflow tips. In EXAMPLE mode
it also explains the demo data. The theme banner image
(assets/banner_<theme>.png) is scaled to 860 px wide at the top.
"""

import math
import os

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "J"
BANNER_WIDTH = 860
BANNER_FALLBACK = (1600, 640)

_STEPS = [
    ("1.  Tell it about your studio",
     "Open Lists & Settings: type your business name, pick your currency "
     "symbol, set the report year, your hourly wage, overhead % and target "
     "margin. Rename any dropdown list while you're there - categories, "
     "payment methods, yarn weights, suppliers."),
    ("2.  List what you make",
     "On the Product Catalog tab, add one row per product with its price, "
     "yarn cost and packaging. Cost per item, profit and margin calculate "
     "themselves. Set a 'Keep min.' level for each - that's your reorder "
     "trigger."),
    ("3.  Book a fair and sell",
     "Add the fair (and its costs) on the Craft Fairs tab, then log every "
     "sale on the Sales Log - pick the fair and product from the "
     "dropdowns. The Dashboard, Event Profit and Monthly Summary update "
     "instantly."),
]

_RULES = [
    "White cells are yours to type in. Tinted cells calculate themselves "
    "and are locked, so a stray keystroke can't break the maths.",
    "Dropdown lists are yours: rename, add or delete entries on the Lists "
    "& Settings tab and every dropdown follows.",
    "Type new data in the blank rows inside each table - the formulas are "
    "already waiting for you there.",
    "The _Data tab is the engine room that feeds the Dashboard and "
    "charts. It stays hidden on purpose and needs no attention.",
    "No macros, nothing to install: works in Microsoft Excel 2016 and "
    "newer, and uploads cleanly to Google Sheets (Drive \u2192 open with "
    "Google Sheets).",
]

_TIPS = [
    "Price before you stitch: run every new design through the Pricing "
    "Calculator so your wage and overhead are inside the price, not "
    "wishes.",
    "Log production on Made & Stocked as you finish items - stock levels, "
    "the status pills and the Reorder List all follow automatically.",
    "Check the Reorder List a fortnight before a fair: buy what the list "
    "suggests and you won't sell out of your bestseller at 11am.",
    "After each fair, open Event Profit and compare net profit and ROI. "
    "Book the winners again next season; let the losers go.",
    "Once a month, glance at the Monthly Summary - a red net month "
    "usually just means a fair fee paid before the fair happened.",
]

_TAB_TOUR = {
    "setup": ("\u2699\uFE0F  Lists & Settings",
              "Your studio name, money settings and every dropdown list."),
    "dashboard": ("\U0001F3E0  Dashboard",
                  "Live KPIs, charts and your top products."),
    "catalog": ("\U0001F9F6  Product Catalog",
                "One row per product: price, costs, margin, stock."),
    "materials": ("\U0001F9F5  Yarn & Materials",
                  "Your whole stash with costs and what's left."),
    "production": ("\U0001F4E6  Made & Stocked",
                   "Log making sessions; stock counts itself."),
    "events": ("\U0001F3EA  Craft Fairs",
               "Book fairs and their costs; profit maths runs itself."),
    "sales": ("\U0001F4B0  Sales Log",
              "One row per line item sold - at fairs or online."),
    "eventprofit": ("\U0001F9EE  Event Profit",
                    "Was that fair worth it? Net, breakeven and ROI."),
    "reorder": ("\U0001F504  Reorder List",
                "An auto-built shopping list for stock and yarn."),
    "packing": ("\U0001F392  Packing Checklist",
                "Tick your way out the door - nothing left behind."),
    "pricing": ("\U0001F4B5  Pricing Calculator",
                "Price items so crafting actually pays you."),
    "monthly": ("\U0001F4C5  Monthly Summary",
                "Your whole year, one row per month."),
    "guide": ("\U0001F4D6  Start Here", "This page."),
}


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("guide")
    demo = bk.demo
    premium = bk.edition == "premium"

    bk.paint("guide", 0, 0, 140, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------- banner
    # With artwork present, the product title is written *under* the
    # banner and shows through its transparent window (see
    # tools/make_banner_alpha_crochet.py).  Without artwork we fall back
    # to a plain title block.
    first_free = _banner(bk)
    if first_free:
        ws.set_row(r(first_free), 24)
        ws.merge_range(r(first_free), 7, r(first_free), ci(LAST_COL), "",
                       S.home_link)
        ws.write_url(r(first_free), 7,
                     "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                     "\U0001F3E0  Dashboard")
        bk.stats["links"] += 1
        cur = first_free + 2
    else:
        ws.set_row(r(4), 30)
        ws.merge_range(r(4), 1, r(4), 6, "\U0001F4D6  Start Here",
                       S.sheet_title)
        ws.merge_range(r(4), 7, r(4), ci(LAST_COL), "", S.home_link)
        ws.write_url(r(4), 7, "internal:%s!A1" % bk.q("dashboard"),
                     S.home_link, "\U0001F3E0  Dashboard")
        bk.stats["links"] += 1
        ws.set_row(r(5), 18)
        ws.merge_range(r(5), 1, r(5), ci(LAST_COL),
                       "  Two minutes of setup, a whole season of calm",
                       S.sheet_sub)
        cur = 7

    # ------------------------------------------------------- welcome
    welcome = ("%s is a complete little business system for crochet "
               "sellers: products and pricing, yarn stash, stock, craft "
               "fairs, sales and profit - all in one tidy workbook that "
               "does the maths for you." % C.PRODUCT)
    cur = bk.para("guide", cur, 1, ci(LAST_COL), welcome, S.guide_text(),
                  minimum=20) + 1

    # badge chips
    badges = [
        ("PREMIUM EDITION  \u2022  14 tabs" if premium
         else "BASIC EDITION  \u2022  8 tabs", 3, th.primary,
         th.primary_soft),
        ("%s theme" % th.label, 2, th.accent, th.accent_soft),
        ("Excel 2016+  \u2022  Google Sheets", 3, th.ok, th.ok_soft),
        ("No macros", 2, th.info, th.info_soft),
    ]
    ws.set_row(r(cur), 22)
    col = 1
    for text, span, fg, bg in badges:
        fmt = S.pill(bg, fg, size=10, bold=True, align="center")
        ws.merge_range(r(cur), col, r(cur), col + span - 1, "", fmt)
        ws.write(r(cur), col, text, fmt)
        col += span
    if col <= ci(LAST_COL):
        ws.merge_range(r(cur), col, r(cur), ci(LAST_COL), "", S.canvas)
    cur += 2

    # --------------------------------------------------------- steps
    ws.set_row(r(cur), 22)
    bk.band("guide", cur, 1, ci(LAST_COL), S.section, height=22)
    ws.write(r(cur), 1, "  Set up in three minutes", S.section)
    cur += 1
    for title, body in _STEPS:
        ws.set_row(r(cur), 18)
        ws.merge_range(r(cur), 1, r(cur), ci(LAST_COL), title,
                       S.f(**S.base(font_name=th.title_font, font_size=12,
                                    bold=True, font_color=th.primary,
                                    bg_color=th.card, align="left",
                                    valign="vcenter", indent=1, border=1,
                                    border_color=th.border)))
        cur += 1
        cur = bk.para("guide", cur, 1, ci(LAST_COL), body, S.guide_text(),
                      minimum=20)
        cur += 1

    # ------------------------------------------------------ tab tour
    ws.set_row(r(cur), 22)
    bk.band("guide", cur, 1, ci(LAST_COL), S.section_accent, height=22)
    ws.write(r(cur), 1, "  Your tabs, left to right", S.section_accent)
    cur += 1
    ws.set_row(r(cur), 20)
    ws.merge_range(r(cur), 1, r(cur), 3, "Tab", S.header(th.primary))
    ws.merge_range(r(cur), 4, r(cur), ci(LAST_COL), "What it does",
                   S.header(th.primary))
    cur += 1
    for key in bk.order:
        if key in ("data", "guide"):
            continue
        title, blurb = _TAB_TOUR.get(key, (C.SHEET_NAMES[key], ""))
        ws.set_row(r(cur), 20)
        a = common.alt(cur)
        link_fmt = S.f(**S.base(font_size=10.5, bold=True,
                                font_color=th.primary,
                                bg_color=th.alt if a else th.card,
                                align="left", valign="vcenter", indent=1,
                                border=1, border_color=th.border))
        ws.merge_range(r(cur), 1, r(cur), 3, "", link_fmt)
        ws.write_url(r(cur), 1, "internal:%s!A1" % bk.q(key), link_fmt,
                     title)
        bk.stats["links"] += 1
        ws.merge_range(r(cur), 4, r(cur), ci(LAST_COL), blurb,
                       S.cell("text", a))
        cur += 1
    cur += 1

    # --------------------------------------------------------- rules
    ws.set_row(r(cur), 22)
    bk.band("guide", cur, 1, ci(LAST_COL), S.section_gold, height=22)
    ws.write(r(cur), 1, "  The golden rules", S.section_gold)
    cur += 1
    for rule in _RULES:
        cur = bk.para("guide", cur, 1, ci(LAST_COL),
                      "\u2022  " + rule, S.guide_text(size=10.5),
                      minimum=18)
    cur += 1

    # ---------------------------------------------------------- tips
    ws.set_row(r(cur), 22)
    bk.band("guide", cur, 1, ci(LAST_COL), S.section, height=22)
    ws.write(r(cur), 1, "  Work like a pro", S.section)
    cur += 1
    for tip in _TIPS:
        cur = bk.para("guide", cur, 1, ci(LAST_COL), "\u2022  " + tip,
                      S.guide_text(size=10.5), minimum=18)
    cur += 1

    # ------------------------------------------------- example notice
    if demo:
        note = ("This EXAMPLE copy is filled with Willow & Wren Crochet "
                "Studio - a fictional small crochet business - so you can "
                "see every formula, chart and pill doing its job. Browse "
                "the tabs, then make it yours: type over the example rows "
                "or delete them and start fresh. Nothing breaks when you "
                "clear the data out.")
        ws.merge_range(r(cur), 1, r(cur + 1), ci(LAST_COL), note,
                       S.f(**S.base(font_size=10.5, italic=True,
                                    font_color=th.ink,
                                    bg_color=th.gold_soft, align="left",
                                    valign="vcenter", text_wrap=True,
                                    indent=1, border=1,
                                    border_color=th.gold)))
        ws.set_row(r(cur), 22)
        ws.set_row(r(cur + 1), 22)
        cur += 3

    # -------------------------------------------------------- footer
    cur = bk.para(
        "guide", cur, 1, ci(LAST_COL),
        "Questions or a wish for the next version? Message me through "
        "Etsy - I read and answer everything.",
        S.f(**S.base(font_size=10.5, bold=True, font_color=th.primary,
                     bg_color=th.primary_soft, align="left",
                     valign="vcenter", text_wrap=True, indent=1, border=1,
                     border_color=th.border)), minimum=22)
    cur = bk.para(
        "guide", cur, 1, ci(LAST_COL),
        "%s v%s  \u2022  %s  \u2022  \u00A9 %s"
        % (C.PRODUCT, C.VERSION,
           "14-tab Premium edition" if premium else "8-tab Basic edition",
           C.AUTHOR),
        S.footer, minimum=16)

    common.footer_nav(
        bk, "guide", cur + 1, LAST_COL, landscape=False, zoom=100,
        tip="  \U0001F4A1  Start on the Dashboard tab - it's the front "
            "door to everything else.")


# ---------------------------------------------------------------------------
def _banner(bk):
    """Insert the theme banner; return the first free 1-indexed row."""
    ws = bk.ws("guide")
    S = bk.S
    path = os.path.join("assets", "banner_%s.png" % bk.th.key)
    if bk.images and os.path.exists(path):
        w, h = BANNER_FALLBACK
        try:
            from PIL import Image
            with Image.open(path) as im:
                w, h = im.size
        except Exception:
            pass
        scale = BANNER_WIDTH / float(w)
        rows = int(math.ceil((h * scale + 8) / 20.0))
        ws.set_row(r(0), 6)
        for rr in range(1, rows + 1):
            ws.set_row(r(rr), 20)
        ws.insert_image(r(1), 1, path, {"x_scale": scale, "y_scale": scale,
                                        "x_offset": 2, "y_offset": 2})
        return rows + 2
    # no image: fall back to a coloured hero band
    ws.set_row(r(0), 6)
    ws.set_row(r(1), 40)
    ws.merge_range(r(1), 1, r(1), ci(LAST_COL), "", S.hero_title)
    ws.write(r(1), 1, "  " + C.PRODUCT, S.hero_title)
    ws.set_row(r(2), 8)
    return 4
