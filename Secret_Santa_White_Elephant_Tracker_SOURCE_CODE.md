# Secret Santa & White Elephant Party Tracker — Complete Source Code

**Novality Store** • bundled 2026-09-20

Every Python file of the project in one document, for future reference.
Rebuild commands are in the kit `README.md`.

## Contents

1. **`secret_santa_party_tracker.py`** — Entry point / CLI - builds every product workbook (--all --outdir products/ --protect premium).
2. **`santa_tracker/__init__.py`** — Package marker.
3. **`santa_tracker/config.py`** — All constants: tabs, editions, statuses, columns, KPI map, capacities - the single source of truth for every tab.
4. **`santa_tracker/theme.py`** — Noel & Arctic colour themes (tab colours, series, soft tints).
5. **`santa_tracker/styles.py`** — xlsxwriter format factory - every cell style used in the workbooks.
6. **`santa_tracker/demo.py`** — The demo party: people, draw, budgets, wishlists, white elephant game, history + all aggregations (agg) for the dashboard, KPI caches and guide images.
7. **`santa_tracker/workbook.py`** — Workbook bootstrap: sheet order, tab colours, print setup, protection plumbing, EXAMPLE vs blank modes.
8. **`santa_tracker/book.py`** — Book writer: title blocks, KPI cards, bars, charts, conditional formats, data validation, sheet protection + (c) Novality Store footer.
9. **`santa_tracker/sheets/__init__.py`** — Sheet modules.
10. **`santa_tracker/sheets/common.py`** — Shared sheet helpers: headers, chips, dropdowns, tables, footers - plus the chip cache label fix.
11. **`santa_tracker/sheets/data.py`** — Hidden _Data engine room: KPI formulas, status pools, lists.
12. **`santa_tracker/sheets/setup.py`** — Settings & Instructions tab: party basics, seeds, budget range.
13. **`santa_tracker/sheets/dashboard.py`** — Dashboard tab: hero, 12 KPI cards, progress bars, 4 live charts.
14. **`santa_tracker/sheets/participants.py`** — Participants tab.
15. **`santa_tracker/sheets/draw.py`** — Secret Santa Draw tab: seed-driven shuffle, flags, overrides.
16. **`santa_tracker/sheets/rules.py`** — Exclusions & Rules tab (PREMIUM): house rules + custom pairs.
17. **`santa_tracker/sheets/budget.py`** — Budget Tracker tab.
18. **`santa_tracker/sheets/wishlists.py`** — Wishlists tab (PREMIUM).
19. **`santa_tracker/sheets/we.py`** — White Elephant tab (PREMIUM): seats, gifts, holders, statuses.
20. **`santa_tracker/sheets/history.py`** — Game History tab (PREMIUM): turn log that drives the board.
21. **`santa_tracker/sheets/cards.py`** — Santa Cards tab (PREMIUM): fold-and-cut giver cards.
22. **`santa_tracker/sheets/guide.py`** — Start Here guide tab with watercolour banner cover.
23. **`tools/verify_santa.py`** — QA: structural audit - sheet refs, modern functions, hidden writes.
24. **`tools/calc_check_santa.py`** — QA: recalculates the whole workbook with the formulas engine and diffs every cached value.
25. **`tools/layout_check_santa.py`** — QA: finds clipped or overflowing text before buyers do.
26. **`tools/render_preview_santa.py`** — QA: renders any tab to PNG (real emoji glyphs) - powers the user-guide screenshots.
27. **`tools/make_banner_alpha_santa.py`** — Turns the generated banner art into the transparent PNG the workbook embeds.
28. **`etsy/__init__.py`** — Package marker.
29. **`etsy/crochet_lib.py`** — Shared PIL rendering engine (emoji-aware text, fonts, tables, pills, charts) - used to draw the user guide.
30. **`etsy/make_user_guide_santa.py`** — Builds the 12-page illustrated user-guide PDF from real workbook screenshots.
31. **`etsy/make_kit_zip_santa.py`** — Bundles this complete kit zip.
32. **`etsy/make_listing_images_santa.py`** — Draws the 15 Etsy listing images (2400x1800 JPEG) from real workbook screenshots.
33. **`etsy/make_listing_zip_santa.py`** — Bundles the standalone Etsy listing-kit zip (md + 15 images).

---


## `secret_santa_party_tracker.py`

*Entry point / CLI - builds every product workbook (--all --outdir products/ --protect premium).* (54 lines)

````python
#!/usr/bin/env python3
"""Command line entry point for the Secret Santa & White Elephant tracker."""

import argparse
import sys


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build Secret Santa & White Elephant Party Tracker "
                    "workbooks (Novality Store).")
    p.add_argument("--edition", choices=("premium", "basic"),
                   default="premium")
    p.add_argument("--theme", choices=("noel", "arctic"), default="noel")
    p.add_argument("--mode", choices=("blank", "demo"), default="blank")
    p.add_argument("--out", default=None)
    p.add_argument("--outdir", default="products")
    p.add_argument("--all", action="store_true",
                   help="build the curated six-file product set")
    p.add_argument("--protect", default="premium", metavar="PASSWORD",
                   help="sheet-protection password for locked formula "
                        "cells (default: premium)")
    p.add_argument("--no-protect", dest="protect_off", action="store_true",
                   help="ship the workbooks unprotected")
    args = p.parse_args(argv)

    sys.path.insert(0, ".")
    from santa_tracker import config as C
    from santa_tracker import workbook as W
    protect = None if args.protect_off else (args.protect or
                                             C.PROTECT_PASSWORD)
    if args.all:
        rows = W.build_all(args.outdir, protect=protect)
    else:
        from santa_tracker.workbook import product_filename
        out = args.out or product_filename(args.edition, args.theme,
                                           args.mode)
        stats = W.build_workbook(out, args.edition, args.theme, args.mode,
                                 protect=protect)
        rows = [(out, stats)]
    print("=" * 78)
    print("BUILD COMPLETE")
    print("=" * 78)
    for name, stats in rows:
        print("  %-58s %7.1f KB" % (name, stats["size"] / 1024.0))
        print("      formulas %5d   validations %3d   cond. formats %3d   "
              "charts %d" % (stats["formulas"], stats["validations"],
                             stats["cond_formats"], stats["charts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

---
## `santa_tracker/__init__.py`

*Package marker.* (1 lines)

````python

````

---
## `santa_tracker/config.py`

*All constants: tabs, editions, statuses, columns, KPI map, capacities - the single source of truth for every tab.* (234 lines)

````python
"""Geometry, column maps, caps and list definitions for the
Secret Santa + White Elephant Party Tracker (Novality Store)."""

PRODUCT = "Secret Santa & White Elephant Party Tracker"
PRODUCT_SHORT = "Party Tracker"
TAGLINE = "draws, budgets, wishlists and white-elephant chaos - handled"
AUTHOR = "Novality Store"
VERSION = "1.0.0"

# protection password for locked (formula) cells
PROTECT_PASSWORD = "premium"

# ---------------------------------------------------------------------------
# sheet keys, tab names, editions
# ---------------------------------------------------------------------------
SHEET_NAMES = {
    "data": "_Data",
    "setup": "\u2699\ufe0f Settings & Instructions",
    "dashboard": "\U0001F3E0 Dashboard",
    "participants": "\U0001F465 Participants",
    "draw": "\U0001F385 Secret Santa Draw",
    "rules": "\U0001F6AB Exclusions & Rules",
    "budget": "\U0001F4B0 Budget Tracker",
    "wishlists": "\U0001F381 Wishlists",
    "we": "\U0001F3B2 White Elephant",
    "history": "\U0001F504 Game History",
    "cards": "\U0001F39F\ufe0f Santa Cards",
    "guide": "\U0001F4D6 Start Here",
}
SHEET_SHORT = {
    "data": "Data", "setup": "Settings", "dashboard": "Dashboard",
    "participants": "People", "draw": "Draw", "rules": "Rules",
    "budget": "Budget", "wishlists": "Wishlists", "we": "White Elephant",
    "history": "History", "cards": "Cards", "guide": "Start Here",
}

EDITIONS = {
    "premium": ["data", "setup", "dashboard", "participants", "draw",
                "rules", "budget", "wishlists", "we", "history", "cards",
                "guide"],
    "basic": ["data", "setup", "dashboard", "participants", "draw",
              "budget", "guide"],
}

# ---------------------------------------------------------------------------
# band geometry (rows 1-7) shared by every table sheet
# ---------------------------------------------------------------------------
ROW_SPACER_1 = 1
ROW_TITLE = 2
ROW_SUBTITLE = 3
ROW_SPACER_2 = 4
ROW_STATS = 5
ROW_SPACER_3 = 6
ROW_HEADER = 7
ROW_FIRST = 8


def last_row(key):
    return ROW_FIRST + CAP[key] - 1


def cols_last(key):
    return COLS_LAST[key]


CAP = {
    "participants": 24,
    "draw": 24,
    "rules": 16,
    "budget": 24,
    "wishlists": 40,
    "we": 24,
    "history": 60,
}

COLS = {
    "participants": {"n": "A", "name": "B", "team": "C", "household": "D",
                     "rsvp": "E", "diet": "F", "lastyear": "G",
                     "status": "H", "wishes": "I", "notes": "J"},
    "draw": {"n": "A", "giver": "B", "computed": "C", "override": "D",
             "final": "E", "flag": "F", "status": "G"},
    "rules": {"n": "A", "giver": "B", "cannot": "C", "reason": "D"},
    "budget": {"n": "A", "name": "B", "min": "C", "max": "D", "spent": "E",
               "flag": "F", "receipt": "G", "ref": "H", "notes": "I"},
    "wishlists": {"n": "A", "who": "B", "item": "C", "priority": "D",
                  "link": "E", "claimed": "F", "notes": "G"},
    "we": {"n": "A", "order": "B", "player": "C", "giftnum": "D",
           "desc": "E", "value": "F", "steals": "G", "maxsteals": "H",
           "status": "I", "holder": "J", "stolenfrom": "K", "final": "L",
           "key1": "M", "key2": "N"},
    "history": {"n": "A", "turn": "B", "player": "C", "action": "D",
                "gift": "E", "stolenfrom": "F"},
}
COLS_LAST = {
    "participants": "J", "draw": "G", "rules": "D", "budget": "I",
    "wishlists": "G", "we": "L", "history": "F",
}

WIDTHS = {
    "participants": {"A": 2.2, "B": 20, "C": 12, "D": 12, "E": 9, "F": 16,
                     "G": 16, "H": 15, "I": 8, "J": 34},
    "draw": {"A": 2.2, "B": 20, "C": 20, "D": 20, "E": 20, "F": 22,
             "G": 15},
    "rules": {"A": 2.2, "B": 20, "C": 20, "D": 32},
    "budget": {"A": 2.2, "B": 20, "C": 9, "D": 9, "E": 10, "F": 17,
               "G": 9, "H": 14, "I": 22},
    "wishlists": {"A": 2.2, "B": 20, "C": 30, "D": 13, "E": 22, "F": 9,
                  "G": 20},
    "we": {"A": 2.2, "B": 7, "C": 20, "D": 7, "E": 26, "F": 10, "G": 8,
           "H": 8, "I": 13, "J": 18, "K": 16, "L": 9, "M": 10, "N": 10},
    "history": {"A": 2.2, "B": 7, "C": 20, "D": 10, "E": 9, "F": 18},
    "dashboard": {"A": 2.2, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13,
                  "G": 13, "H": 13, "I": 13, "J": 13, "K": 13, "L": 13,
                  "M": 13, "N": 13},
    "setup": {"A": 2.2, "B": 38, "C": 24, "D": 16, "E": 16, "F": 16,
              "G": 16},
    "cards": {"A": 2.2, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13,
              "G": 13, "H": 13, "I": 13},
    "guide": {"A": 2.2, "B": 4, "C": 15, "D": 15, "E": 24, "F": 16,
              "G": 16, "H": 16, "I": 16, "J": 16},
}

# ---------------------------------------------------------------------------
# settings rows
# ---------------------------------------------------------------------------
SU_BUSINESS = 6        # party name
SU_MESSAGE = 7         # dashboard message
SU_CURRENCY = 10
SU_YEAR = 11           # party year
SU_DATE = 12           # party date
SU_LOCATION = 13
SU_HOST = 14
SU_BMIN = 15
SU_BMAX = 16
SU_STEALS = 17
SU_START = 18
SU_SEED = 19           # secret santa draw seed
SU_WESEED = 20         # white elephant seed
SU_STATUS = 21         # Draft / Final lock flag
SU_LIST_HEADER = 25
SU_LIST_FIRST = 26
SU_LIST_ROWS = 16
SU_FIXED_FIRST = 46

LIST_COLS = {"teams": "C", "diets": "D"}

FIXED_BLOCKS = {
    "Statuses": ("C", 4),     # Not Started / Gift Purchased / Wrapped / Complete
    "RSVP": ("D", 3),         # Yes / No / Maybe
    "Actions": ("E", 2),      # Pick / Steal
    "Priorities": ("F", 3),   # Must-love / Nice to have / Just an idea
    "Tick": ("G", 2),         # ✓ / blank
    "OnOff": ("H", 2),        # On / Off
}

TICK = "\u2713"

# statuses
ST_NOT = "Not Started"
ST_BOUGHT = "Gift Purchased"
ST_WRAPPED = "Wrapped"
ST_DONE = "Complete"

# gift statuses (white elephant)
GS_AVAIL = "\U0001F381 Available"
GS_HELD = "\U0001F932 Held"
GS_STOLEN = "\U0001F504 Stolen"
GS_FINAL = "\U0001F512 Final"

# budget flags
BF_UNDER = "\U0001F534 Under budget"
BF_OK = "\u2705 Within budget"
BF_OVER = "\U0001F6A8 Over budget"

# draw lock
DRAW_DRAFT = "Draft \u2014 re-draw allowed"
DRAW_FINAL = "Final \u2014 locked \U0001F512"

# ---------------------------------------------------------------------------
# _Data layout
# ---------------------------------------------------------------------------
DATA_KPI_FIRST = 2          # KPI label col AH, value col AI
KPI_ROW = {
    "participants": 2,
    "rsvp_yes": 3,
    "rsvp_pending": 4,
    "assigned": 5,
    "purchased": 6,
    "wrapped": 7,
    "complete": 8,
    "total_budget": 9,
    "spent": 10,
    "avg_gift": 11,
    "rules_count": 12,
    "we_players": 13,
    "gifts_in_play": 14,
    "locked_gifts": 15,
    "completion": 16,
    "turns_done": 17,
    "current_turn": 18,
    "violations": 19,
    "over_budget": 20,
    "diets": 21,
}
KPI_FMT = {
    "participants": "#,##0", "rsvp_yes": "#,##0", "rsvp_pending": "#,##0",
    "assigned": "#,##0", "purchased": "#,##0", "wrapped": "#,##0",
    "complete": "#,##0", "total_budget": "#,##0.00", "spent": "#,##0.00",
    "avg_gift": "#,##0.00", "rules_count": "#,##0", "we_players": "#,##0",
    "gifts_in_play": "#,##0", "locked_gifts": "#,##0", "completion": "0%",
    "turns_done": "#,##0", "current_turn": "#,##0", "violations": "#,##0",
    "over_budget": "#,##0", "diets": "#,##0",
}

# dashboard rows
DASH_HERO = 2
DASH_MSG = 5
DASH_CARD1_L = 8
DASH_CARD1_V = 9
DASH_CARD2_L = 10
DASH_CARD2_V = 11
DASH_BAR1 = 12
DASH_BAR2 = 13
DASH_CHART1 = 16
DASH_CHART2 = 32
DASH_CHART3 = 48
DASH_PANEL = 64
DASH_FOOTER = 72
DASH_NAV = 74

# white elephant / draw control rows
WE_CTRL_ROW = 5
HIST_NOTE_ROW = 5
````

---
## `santa_tracker/theme.py`

*Noel & Arctic colour themes (tab colours, series, soft tints).* (128 lines)

````python
"""
Colour palettes / design systems for the Secret Santa & White Elephant
Party Tracker (Novality Store).

Two themes ship with the product:

  noel    warm cream canvas, deep holly red, pine green, antique gold
  arctic  cool night canvas paper-white, deep navy, ice blue, berry accent
"""


class Theme(object):
    """Small attribute bag so sheet code can read ``th.primary`` etc."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def soft(self, key):
        """Return the pale 'tint' partner of a colour key."""
        return self.__dict__[key + "_soft"]


# ===========================================================================
# NOEL - "classic Christmas parlour"
# ===========================================================================
NOEL = Theme(
    key="noel",
    label="Noel",
    bg="#FBF6EE",
    cover_bg="#FBF6EE",
    card="#FFFFFF",
    alt="#FCF8F1",
    border="#E7D9C6",
    border_strong="#C9AE8C",
    primary="#8C1D2C",          # holly red
    primary_2="#1F5C40",        # pine
    primary_2_soft="#E1EDE5",
    primary_soft="#F5E1E2",
    accent="#1F5C40",           # pine green
    accent_soft="#E1EDE5",
    gold="#B98A2E",             # antique gold
    gold_soft="#F6EDD8",
    ink="#33221E",
    muted="#9A8474",
    white="#FFFFFF",
    ok="#1F5C40",
    ok_soft="#E1EDE5",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#5E6FA3",
    info_soft="#E5E9F4",
    plum="#8C1D2C",
    plum_soft="#F5E1E2",
    title_font="Georgia",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#9A8474",
        "setup": "#1F5C40",
        "dashboard": "#8C1D2C",
        "participants": "#1F5C40",
        "draw": "#8C1D2C",
        "rules": "#B4761A",
        "budget": "#B98A2E",
        "wishlists": "#5E6FA3",
        "we": "#1F5C40",
        "history": "#5E6FA3",
        "cards": "#8C1D2C",
        "guide": "#9A8474",
    },
)

# ===========================================================================
# ARCTIC - "midnight frost party"
# ===========================================================================
ARCTIC = Theme(
    key="arctic",
    label="Arctic",
    bg="#F4F7FB",
    cover_bg="#F4F7FB",
    card="#FFFFFF",
    alt="#F8FAFD",
    border="#D8E1EC",
    border_strong="#A9BBD0",
    primary="#1F3A5F",          # deep navy
    primary_2="#5B8DB8",        # ice blue
    primary_2_soft="#E4EDF5",
    primary_soft="#E2E9F2",
    accent="#C4485C",           # winter berry
    accent_soft="#F8E3E6",
    gold="#C9A227",             # starlight gold
    gold_soft="#F7F0DA",
    ink="#1E2833",
    muted="#7C8CA0",
    white="#FFFFFF",
    ok="#2F6D5F",
    ok_soft="#E0EEE9",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#5B8DB8",
    info_soft="#E4EDF5",
    plum="#1F3A5F",
    plum_soft="#E2E9F2",
    title_font="Trebuchet MS",
    body_font="Trebuchet MS",
    mono_font="Consolas",
    tabs={
        "data": "#7C8CA0",
        "setup": "#5B8DB8",
        "dashboard": "#1F3A5F",
        "participants": "#2F6D5F",
        "draw": "#C4485C",
        "rules": "#B4761A",
        "budget": "#C9A227",
        "wishlists": "#5B8DB8",
        "we": "#2F6D5F",
        "history": "#5B8DB8",
        "cards": "#C4485C",
        "guide": "#7C8CA0",
    },
)

THEMES = {"noel": NOEL, "arctic": ARCTIC}
````

---
## `santa_tracker/styles.py`

*xlsxwriter format factory - every cell style used in the workbooks.* (324 lines)

````python
"""
Every cell format used by the workbook, generated from the active theme.

Sheet builders never build formats inline - they ask ``Styles`` for a
semantic style (``S.cell("money", alt)``), which keeps the two themes
visually consistent and keeps the format cache small.
"""

import math


class Styles(object):

    def __init__(self, wb, th):
        self.wb = wb
        self.th = th
        self._cache = {}
        self._build()

    # ------------------------------------------------------------------
    # core
    # ------------------------------------------------------------------
    def f(self, props=None, **kw):
        """Cached ``workbook.add_format`` (accepts a dict or keywords)."""
        p = dict(props or {})
        p.update(kw)
        key = tuple(sorted((k, str(v)) for k, v in p.items()))
        fmt = self._cache.get(key)
        if fmt is None:
            fmt = self.wb.add_format(p)
            self._cache[key] = fmt
        return fmt

    def base(self, **over):
        """Body-text defaults + overrides."""
        p = {"font_name": self.th.body_font, "font_size": 10.5,
             "font_color": self.th.ink, "valign": "vcenter"}
        p.update(over)
        return p

    # ------------------------------------------------------------------
    # canvases, banners, sections
    # ------------------------------------------------------------------
    def _build(self):
        th = self.th
        self.canvas = self.f({"bg_color": th.bg})
        self.canvas_card = self.f({"bg_color": th.card})

        self.hero_title = self.f(self.base(
            font_name=th.title_font, font_size=26, bold=True,
            font_color=th.white, bg_color=th.primary, align="left",
            valign="vcenter", indent=1))
        self.hero_count = self.f(self.base(
            font_name=th.title_font, font_size=17, bold=True,
            font_color=th.gold_soft, bg_color=th.accent, align="left",
            valign="vcenter", indent=1))
        self.hero_meta = self.f(self.base(
            font_size=10, italic=True, font_color=th.ink,
            bg_color=th.gold_soft, align="left", valign="vcenter", indent=1))

        self.sheet_title = self.f(self.base(
            font_name=th.title_font, font_size=20, bold=True,
            font_color=th.primary, bg_color=th.bg, align="left",
            valign="vcenter", indent=1))
        self.sheet_sub = self.f(self.base(
            font_size=10.5, italic=True, font_color=th.muted,
            bg_color=th.bg, align="left", valign="vcenter", indent=1))
        self.home_link = self.f(self.base(
            font_size=10, bold=True, font_color=th.white, bg_color=th.accent,
            align="center", valign="vcenter", border=1,
            border_color=th.accent))

        self.section = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.white, bg_color=th.primary, align="left",
            valign="vcenter", indent=1))
        self.section_accent = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.white, bg_color=th.accent, align="left",
            valign="vcenter", indent=1))
        self.section_gold = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.ink, bg_color=th.gold_soft, align="left",
            valign="vcenter", indent=1, bottom=2, bottom_color=th.gold))
        self.section_soft = self.f(self.base(
            font_name=th.title_font, font_size=12, bold=True,
            font_color=th.primary, bg_color=th.primary_soft, align="left",
            valign="vcenter", indent=1, left=4, left_color=th.gold))

        # table header
        self.thead = self.f(self.base(
            font_size=10, bold=True, font_color=th.white, bg_color=th.primary,
            align="center", valign="vcenter", text_wrap=True, border=1,
            border_color=th.primary))

        self.note = self.f(self.base(
            font_size=10, italic=True, font_color=th.muted, bg_color=th.alt,
            align="left", valign="top", text_wrap=True, border=1,
            border_color=th.border, indent=1, locked=False))
        self.note_plain = self.f(self.base(
            font_size=10, italic=True, font_color=th.muted, bg_color=th.bg,
            align="left", valign="top", text_wrap=True))
        self.footer = self.f(self.base(
            font_size=9, italic=True, font_color=th.muted, bg_color=th.bg,
            align="left", valign="vcenter"))

        self.bar_text = self.f(self.base(
            font_name=th.mono_font, font_size=13, bold=True,
            font_color=th.primary_2, bg_color=th.card, align="left",
            valign="vcenter", border=1, border_color=th.border))
        self.bar_label = self.f(self.base(
            font_size=10, bold=True, font_color=th.ink, bg_color=th.card,
            align="left", valign="vcenter", border=1,
            border_color=th.border, indent=1))
        self.bar_pct = self.f(self.base(
            font_name=th.mono_font, font_size=13, bold=True,
            font_color=th.accent, bg_color=th.card, align="center",
            valign="vcenter", border=1, border_color=th.border))

    # ------------------------------------------------------------------
    # table headers in an accent colour
    # ------------------------------------------------------------------
    def header(self, color=None):
        color = color or self.th.primary
        return self.f(self.base(
            font_size=10, bold=True, font_color=self.th.white,
            bg_color=color, align="center", valign="vcenter", text_wrap=True,
            border=1, border_color=color))

    # ------------------------------------------------------------------
    # data cells
    # ------------------------------------------------------------------
    _KINDS = {
        "text":       {"align": "left", "locked": False},
        "center":     {"align": "center", "locked": False},
        "money":      {"align": "right", "num_format": "#,##0.00",
                       "locked": False},
        "money0":     {"align": "right", "num_format": "#,##0",
                       "locked": False},
        "num":        {"align": "right", "num_format": "#,##0",
                       "locked": False},
        "qty":        {"align": "center", "num_format": "#,##0",
                       "locked": False},
        "qty1":       {"align": "center", "num_format": "#,##0.0",
                       "locked": False},
        "pct":        {"align": "center", "num_format": "0%",
                       "locked": False},
        "date":       {"align": "center", "num_format": "dd mmm yyyy",
                       "locked": False},
        "tick":       {"align": "center", "font_size": 13, "bold": True,
                       "font_color": "#2F7D4F", "locked": False},
        "wrap":       {"align": "left", "text_wrap": True, "valign": "top",
                       "locked": False},
        "link":       {"align": "left", "font_color": "#2A5D8F",
                       "underline": 1, "locked": False},
        "url":        {"align": "center", "bold": True, "font_size": 10},
        # calculated columns (locked - they must not be typed over)
        "calc":       {"align": "left"},
        "calc_c":     {"align": "center"},
        "calc_wrap":  {"align": "left", "text_wrap": True},
        "calc_money": {"align": "right", "num_format": "#,##0.00"},
        "calc_num":   {"align": "right", "num_format": "#,##0"},
        "calc_qty1":  {"align": "center", "num_format": "#,##0.0"},
        "calc_pct":   {"align": "center", "num_format": "0%"},
        "calc_date":  {"align": "center", "num_format": "dd mmm yyyy"},
        "calc_tick":  {"align": "center", "font_size": 13, "bold": True},
    }

    def cell(self, kind, alt=False, **over):
        """Data-cell format.  ``alt`` selects the zebra-stripe background."""
        th = self.th
        props = self.base(**self._KINDS[kind])
        if kind.startswith("calc"):
            props["bg_color"] = th.alt
            props["font_color"] = th.ink if kind in ("calc", "calc_wrap",
                                                     "calc_c") else th.ink
            props["locked"] = True
            if kind in ("calc_money", "calc_num", "calc_pct", "calc_date"):
                props["font_color"] = th.primary
        else:
            props["bg_color"] = th.alt if alt else th.card
        props["border"] = 1
        props["border_color"] = th.border
        props.update(over)
        return self.f(**props)

    def idx(self, alt=False):
        """The little grey row-number column."""
        return self.f(self.base(
            font_size=9, font_color=self.th.muted, align="center",
            valign="vcenter", border=1, border_color=self.th.border,
            bg_color=self.th.alt if alt else self.th.card,
            num_format="0"))

    # ------------------------------------------------------------------
    # dashboard furniture
    # ------------------------------------------------------------------
    def kpi_label(self, color, size=9.5, align="left"):
        return self.f(self.base(
            font_size=size, bold=True, font_color=self.th.white,
            bg_color=color, align=align, valign="vcenter", indent=1,
            border=1, border_color=color))

    def kpi_value(self, color, num_format=None, size=21, align="center",
                  bg=None):
        p = self.base(font_name=self.th.title_font, font_size=size, bold=True,
                      font_color=color, bg_color=bg or self.th.card,
                      align=align, valign="vcenter", border=1,
                      border_color=self.th.border)
        if num_format:
            p["num_format"] = num_format
        return self.f(**p)

    def kpi_text(self, color, size=11, align="left", bg=None, bold=True,
                 wrap=False):
        return self.f(self.base(
            font_size=size, bold=bold, font_color=color,
            bg_color=bg or self.th.card, align=align, valign="vcenter",
            border=1, border_color=self.th.border,
            indent=1 if align == "left" else 0,
            text_wrap=wrap))

    def panel(self, color=None, bg=None, size=10.5, bold=False, align="left",
              wrap=True, font_color=None, valign="top", border=True):
        p = self.base(font_size=size, bold=bold, align=align, valign=valign,
                      text_wrap=wrap,
                      bg_color=bg if bg is not None else self.th.card,
                      font_color=font_color or self.th.ink)
        if border:
            p["border"] = 1
            p["border_color"] = color or self.th.border
            if color:
                p["left"] = 3
                p["left_color"] = color
        return self.f(**p)

    def pill(self, bg, fg, size=9.5, bold=True, align="center"):
        return self.f(self.base(font_size=size, bold=bold, font_color=fg,
                                bg_color=bg, align=align, valign="vcenter",
                                border=1, border_color=bg, text_wrap=False))

    def nav(self, color, size=10.5):
        return self.f(self.base(font_size=size, bold=True,
                                font_color=self.th.white, bg_color=color,
                                align="center", valign="vcenter", border=1,
                                border_color=color))

    def nav_soft(self, size=10.5):
        th = self.th
        return self.f(self.base(font_size=size, bold=True,
                                font_color=th.primary,
                                bg_color=th.primary_soft,
                                align="center", valign="vcenter", border=1,
                                border_color=th.border))

    # ------------------------------------------------------------------
    # conditional-format formats (dxf sources)
    # ------------------------------------------------------------------
    def cf(self, bg=None, fg=None, bold=False, strike=False, italic=False,
           border=None, size=None, align=None, num_format=None):
        th = self.th
        p = {}
        if bg:
            p["bg_color"] = bg
        if fg:
            p["font_color"] = fg
        if bold:
            p["bold"] = True
        if strike:
            p["font_strikeout"] = True
        if italic:
            p["italic"] = True
        if size:
            p["font_size"] = size
        if align:
            p["align"] = align
        if num_format:
            p["num_format"] = num_format
        if border:
            p["border"] = 1
            p["border_color"] = border
        p["font_name"] = th.body_font
        return self.f(**p)

    def cf_state(self, state):
        """Semantic state colours: ok / warn / bad / info / plum / gold."""
        th = self.th
        return self.cf(bg=th.soft(state), fg=getattr(th, state), bold=True,
                       border=th.border)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def guide_text(self, size=10.5, bold=False, italic=False, color=None,
                   bg=None, indent=0, align="left"):
        return self.f(self.base(font_size=size, bold=bold, italic=italic,
                                font_color=color or self.th.ink,
                                bg_color=bg or self.th.card, align=align,
                                valign="top", text_wrap=True, indent=indent,
                                border=1, border_color=self.th.border,
                                locked=False))

    def static_height(self, text, width_chars, line_px=14.6, pad=8,
                      minimum=18):
        """Row height needed to show wrapped ``text`` in ``width_chars``."""
        if not text:
            return minimum
        per_line = max(10, int(width_chars * 0.95))
        lines = 0
        for para in str(text).split("\n"):
            lines += max(1, int(math.ceil(len(para) / float(per_line))))
        return max(minimum, lines * line_px + pad)


def wrap_height(text, width_chars, line_px=14.6, pad=8, minimum=18):
    """Module-level twin of :meth:`Styles.static_height`."""
    if not text:
        return minimum
    per_line = max(10, int(width_chars * 0.95))
    lines = 0
    for para in str(text).split("\n"):
        lines += max(1, int(math.ceil(len(para) / float(per_line))))
    return max(minimum, lines * line_px + pad)
````

---
## `santa_tracker/demo.py`

*The demo party: people, draw, budgets, wishlists, white elephant game, history + all aggregations (agg) for the dashboard, KPI caches and guide images.* (292 lines)

````python
"""Fictional demo party: the Novality Store holiday party, December 2026.

Feeds cached values into every formula cell of the EXAMPLE workbooks so the
file opens looking alive (and so calc_check can prove the caches match what
the formulas compute).
"""

import datetime


def today():
    # build-date aware, so the dashboard's "days to go" cache is correct the
    # day the EXAMPLE file is generated (Excel recalculates it on open)
    return datetime.date.today()


# ---------------------------------------------------------------------------
# cast
# ---------------------------------------------------------------------------
PEOPLE = [
    # name, team, household, rsvp, diet, last year gave to, status, notes
    ("Ava Novak", "Studio", "Novak home", "Yes", "", "Jack Byrne",
     "Complete", "Hosting helper - arrives early"),
    ("Ben Carter", "Shop", "", "Yes", "Vegetarian", "Ava Novak",
     "Gift Purchased", "Owes Kia a bet from 2025"),
    ("Chloe Diaz", "Online", "", "Yes", "Vegan", "Grace Liu",
     "Wrapped", ""),
    ("Dan Novak", "Studio", "Novak home", "Yes", "", "Elena Petrov",
     "Gift Purchased", "Ava's husband - couple rule applies"),
    ("Elena Petrov", "Shop", "", "Maybe", "Gluten-free", "Farid Khan",
     "Not Started", "Waiting on shift rota"),
    ("Farid Khan", "Shop", "", "Yes", "Halal", "Chloe Diaz",
     "Wrapped", ""),
    ("Grace Liu", "Online", "Flat 4B", "Yes", "", "Hugo Silva",
     "Complete", "Flat 4B - couple rule applies too"),
    ("Hugo Silva", "Online", "Flat 4B", "Yes", "", "Grace Liu",
     "Gift Purchased", ""),
    ("Isla Moore", "Studio", "", "No", "", "Leo Fontaine",
     "Not Started", "Away in December - sad face"),
    ("Jack Byrne", "Shop", "", "Yes", "Nut allergy", "Ava Novak",
     "Gift Purchased", "Espresso-machine feud with Leo"),
    ("Kia Osei", "Online", "", "Yes", "", "Ben Carter",
     "Wrapped", ""),
    ("Leo Fontaine", "Studio", "", "Yes", "Vegetarian", "Isla Moore",
     "Gift Purchased", ""),
]

CUSTOM_PAIRS = [
    ("Jack Byrne", "Leo Fontaine", "Espresso-machine feud of 2025"),
    ("Kia Osei", "Ben Carter", "Last year's regrettable candle"),
]

RULES = {"couple": "On", "team": "Off", "lastyear": "On"}

SPENT = [32.50, 24.00, 28.75, 31.20, 18.00, 26.40, 33.10, 42.00,
         0.00, 29.95, 27.30, 25.60]
RECEIPTS = ["\u2713", "", "\u2713", "", "", "\u2713", "", "\u2713", "",
            "\u2713", "", "\u2713"]
REFS = ["NV-88121", "", "AMZ-4071", "", "", "ETS-2210", "", "NV-88203",
        "", "AMZ-4188", "", "ETS-2355"]

WISHES = [
    ("Ava Novak", "Chunky knit throw blanket", "Must-love",
     "https://example.com/throw", "\u2713", "Any colour but grey"),
    ("Ava Novak", "Ceramic mug tree", "Nice to have", "", "", ""),
    ("Ben Carter", "Single-origin coffee beans 1kg", "Must-love",
     "https://example.com/beans", "\u2713", "No dark roasts"),
    ("Chloe Diaz", "Vegan candle trio", "Nice to have", "", "", ""),
    ("Chloe Diaz", "Linen tea towel set", "Just an idea", "", "", ""),
    ("Dan Novak", "Whisky tasting set", "Must-love",
     "https://example.com/whisky", "", "Peated, please"),
    ("Elena Petrov", "Gluten-free chocolate box", "Must-love", "", "", ""),
    ("Farid Khan", "Desk plant (low light)", "Nice to have", "", "\u2713", ""),
    ("Grace Liu", "Silk scrunchie set", "Just an idea", "", "", ""),
    ("Grace Liu", "Matcha ceremony kit", "Must-love",
     "https://example.com/matcha", "", ""),
    ("Hugo Silva", "Vinyl: jazz classics", "Nice to have", "", "", ""),
    ("Jack Byrne", "Espresso tamp mat", "Must-love", "", "", "Obvious reasons"),
    ("Kia Osei", "Botanical print A4", "Nice to have", "", "\u2713", ""),
    ("Leo Fontaine", "Sourdough starter kit", "Just an idea", "", "", ""),
    ("Leo Fontaine", "Wooden bread lame", "Nice to have", "", "", ""),
    ("Isla Moore", "Travel journal", "Nice to have", "", "", ""),
]

WE_GIFTS = [
    ("Giant pickle plushie", 12.00),
    ("Disco-ball bauble set", 15.50),
    ("Mystery sealed box", 20.00),
    ("Heated mug coaster", 18.25),
    ("Llama Christmas jumper", 22.00),
    ("Singing fish plaque", 14.75),
    ("Fancy hot chocolate tin", 16.40),
    ("Desktop zen garden", 19.90),
    ("Reindeer antler headband", 11.30),
    ("Marble cheese board", 24.50),
]

# round-1 turns then round-2 catch-up turns for the stolen-from players
HISTORY = [
    (1, "Pick", 4, ""),
    (2, "Pick", 7, ""),
    (3, "Steal", 4, None),     # from order 1
    (4, "Pick", 2, ""),
    (5, "Steal", 4, None),     # from order 3 -> gift 4 locks (2 steals)
    (6, "Pick", 9, ""),
    (7, "Steal", 9, None),     # from order 6
    (8, "Pick", 1, ""),
    (9, "Steal", 1, None),     # from order 8
    (10, "Pick", 6, ""),
    (1, "Pick", 3, ""),        # round 2: Ava replaces her stolen gift
    (2, "Pass", 7, ""),
    (3, "Pick", 5, ""),        # Chloe replaces hers
    (4, "Pass", 2, ""),
]


def _offset_for(people, pairs, rules):
    n = len(people)
    for off in range(1, n):
        ok = True
        for i in range(n):
            rec = people[(i + off) % n][0]
            g = people[i]
            if rec == g[0]:
                ok = False
            if rules["couple"] == "On" and g[2] and \
                    people[(i + off) % n][2] == g[2]:
                ok = False
            if rules["lastyear"] == "On" and rec == g[6 - 1]:
                ok = False
            if (g[0], rec) in pairs:
                ok = False
        if ok:
            return off
    return 1


def _rank(keys):
    """1-based rank, largest first (matches Excel RANK default)."""
    order = sorted(range(len(keys)), key=lambda i: -keys[i])
    out = [0] * len(keys)
    for pos, i in enumerate(order):
        out[i] = pos + 1
    return out


class Demo(object):
    def __init__(self):
        self.people = [dict(zip(
            ("name", "team", "household", "rsvp", "diet", "lastyear",
             "status", "notes"), p)) for p in PEOPLE]
        self.pairs = [(a, b) for a, b, _ in CUSTOM_PAIRS]
        self.pair_reason = {(a, b): r for a, b, r in CUSTOM_PAIRS}
        self.rules = dict(RULES)
        n = len(self.people)
        self.offset = _offset_for(PEOPLE, self.pairs, RULES)
        self.assign = [self.people[(i + self.offset) % n]["name"]
                       for i in range(n)]
        self.spent = list(SPENT)
        self.receipts = list(RECEIPTS)
        self.refs = list(REFS)
        self.wishes = WISHES
        self.settings = {
            "party": "Novality Store Holiday Party",
            "message": "19 Dec - bring a wrapped gift and a stealing face!",
            "currency": "$",
            "year": 2026,
            "date": datetime.date(2026, 12, 19),
            "location": "Novality Loft, 12 Market Street",
            "host": "The Novality Team",
            "bmin": 20.0, "bmax": 35.0, "steals": 2, "start": 1,
            # the workbook's draw shift is MOD(seed-1, N-1); seed = offset+1
            # makes the live formula reproduce this demo's assignment
            "seed": self.offset + 1,
            "weseed": 7,
            "status": "Final \u2014 locked \U0001F512",
        }
        self._build_we()
        self._agg()

    # ------------------------------------------------------------------
    def _build_we(self):
        s = self.settings["weseed"]
        players = [p["name"] for p in self.people if p["rsvp"] != "No"][:10]
        n = len(players)
        k1 = [((s * 7919 * (i + 2) + i * 104729) % 999983) * 100 + i
              for i in range(n)]
        k2 = [((s * 6967 * (i + 5) + i * 1299709) % 999983) * 100 + i
              for i in range(n)]
        # exposed so the sheet builder can cache the hidden helper columns
        self.we_k1 = k1
        self.we_k2 = k2
        seats = _rank(k1)              # seat order per player row
        nums = _rank(k2)               # gift number per player row
        self.we = []
        for i, pl in enumerate(players):
            self.we.append({
                "player": pl, "seat": seats[i], "giftnum": nums[i],
                "desc": WE_GIFTS[i][0], "value": WE_GIFTS[i][1],
            })
        by_seat = {w["seat"]: w for w in self.we}
        by_num = {w["giftnum"]: w for w in self.we}
        self.history = []
        holder = {}
        steals = {}
        for turn, (seat, action, gnum, _) in enumerate(HISTORY, 1):
            pl = by_seat[seat]["player"]
            frm = ""
            if action == "Steal":
                frm = holder.get(gnum, "")
                holder[gnum] = pl
                steals[gnum] = steals.get(gnum, 0) + 1
            elif action == "Pick":
                holder[gnum] = pl
            self.history.append((turn, pl, action, gnum, frm))
        self.holder = holder
        self.steals = steals
        self.last_action = {}
        for turn, pl, action, gnum, frm in self.history:
            self.last_action[gnum] = action
        for w in self.we:
            g = w["giftnum"]
            w["steals"] = steals.get(g, 0)
            w["holder"] = holder.get(g, "")
            w["last"] = self.last_action.get(g, "")
            complete = len(set(holder.values())) == len(self.we)
            if w["steals"] >= self.settings["steals"] or complete:
                w["status"] = "\U0001F512 Final"
            elif g not in holder:
                w["status"] = "\U0001F381 Available"
            elif w["last"] == "Steal":
                w["status"] = "\U0001F504 Stolen"
            else:
                w["status"] = "\U0001F932 Held"
            frm = ""
            for turn, pl, action, gn, f in reversed(self.history):
                if gn == g and action == "Steal":
                    frm = f
                    break
            w["stolenfrom"] = frm if w["status"] == "\U0001F504 Stolen" else ""
            w["final"] = ""
        self.we_players = players
        self.we_by_seat = by_seat
        self.by_num = by_num

    # ------------------------------------------------------------------
    def money(self, value, decimals=2):
        cur = self.settings["currency"]
        if decimals:
            return "%s%.*f" % (cur, decimals, value)
        return "%s%d" % (cur, value)

    def _agg(self):
        n = len(self.people)
        st = [p["status"] for p in self.people]
        bought = sum(1 for s in st if s in ("Gift Purchased", "Wrapped",
                                            "Complete"))
        wrapped = sum(1 for s in st if s in ("Wrapped", "Complete"))
        done = sum(1 for s in st if s == "Complete")
        spent = sum(self.spent)
        rules = sum(1 for v in self.rules.values() if v == "On") + \
            len(self.pairs)
        in_play = sum(1 for w in self.we if w["status"] in
                      ("\U0001F932 Held", "\U0001F504 Stolen"))
        locked = sum(1 for w in self.we if w["status"] == "\U0001F512 Final")
        comp = (bought + wrapped + done) / (3.0 * n)
        self.agg = {
            "participants": n,
            "rsvp_yes": sum(1 for p in self.people if p["rsvp"] == "Yes"),
            "rsvp_pending": sum(1 for p in self.people
                                if p["rsvp"] == "Maybe"),
            "assigned": n,
            "purchased": bought,
            "wrapped": wrapped,
            "complete": done,
            "total_budget": n * self.settings["bmax"],
            "spent": spent,
            "avg_gift": spent / bought,
            "rules_count": rules,
            "we_players": len(self.we),
            "gifts_in_play": in_play,
            "locked_gifts": locked,
            "completion": comp,
            "turns_done": len(self.history),
            "current_turn": (self.settings["start"] - 1 +
                             len(self.history)) % len(self.we) + 1,
            "violations": 0,
            "over_budget": sum(1 for x in self.spent
                               if x > self.settings["bmax"]),
            "diets": sum(1 for p in self.people if p["diet"]),
        }
````

---
## `santa_tracker/workbook.py`

*Workbook bootstrap: sheet order, tab colours, print setup, protection plumbing, EXAMPLE vs blank modes.* (66 lines)

````python
"""Build orchestration: editions, themes, modes and product filenames."""

import os

from . import config as C
from . import theme as T
from .book import Book
from .sheets import (budget, cards, dashboard, data, draw, guide, history,
                     participants, rules, setup, we, wishlists)

BUILDERS = {
    "data": data.build,
    "setup": setup.build,
    "dashboard": dashboard.build,
    "participants": participants.build,
    "draw": draw.build,
    "rules": rules.build,
    "budget": budget.build,
    "wishlists": wishlists.build,
    "we": we.build,
    "history": history.build,
    "cards": cards.build,
    "guide": guide.build,
}


def product_filename(edition, theme_name, mode):
    return "Secret_Santa_White_Elephant_Tracker_%s_%s%s.xlsx" % (
        edition.upper(), T.THEMES[theme_name].label,
        "_EXAMPLE" if mode == "demo" else "")


def build_workbook(path, edition="premium", theme_name="noel",
                   mode="blank", protect=C.PROTECT_PASSWORD, images=True):
    """Write one workbook file and return its build stats."""
    from . import demo as D
    if edition not in ("basic", "premium"):
        raise ValueError("edition must be 'basic' or 'premium'")
    if mode not in ("blank", "demo"):
        raise ValueError("mode must be 'blank' or 'demo'")
    model = D.Demo() if mode == "demo" else None
    bk = Book(path, T.THEMES[theme_name], edition=edition, mode=mode,
              protect=protect, images=images, demo=model)
    for key in bk.order:
        BUILDERS[key](bk)
    bk.close()
    stats = dict(bk.stats)
    stats["size"] = os.path.getsize(path)
    return stats


def build_all(outdir, protect=C.PROTECT_PASSWORD, images=True):
    """The curated six-file Etsy product set."""
    os.makedirs(outdir, exist_ok=True)
    combos = [("premium", "noel", "demo"), ("premium", "noel", "blank"),
              ("premium", "arctic", "blank"), ("basic", "noel", "blank"),
              ("basic", "arctic", "blank"), ("basic", "noel", "demo")]
    out = []
    for edition, theme_name, mode in combos:
        name = product_filename(edition, theme_name, mode)
        path = os.path.join(outdir, name)
        stats = build_workbook(path, edition, theme_name, mode,
                               protect=protect, images=images)
        out.append((name, stats))
    return out
````

---
## `santa_tracker/book.py`

*Book writer: title blocks, KPI cards, bars, charts, conditional formats, data validation, sheet protection + (c) Novality Store footer.* (507 lines)

````python
"""
The build context.

``Book`` owns the workbook, the worksheet registry, the defined names and all
of the little helpers that turn a cell address into a formula fragment.  Sheet
builders receive one ``Book`` and never talk to XlsxWriter's raw indices
directly, which is what keeps the cross-sheet formulas correct when a tab is
missing (Basic edition) or when a capacity changes.
"""

import datetime
import types

import xlsxwriter
try:
    from xlsxwriter.utility import datetime_to_excel_datetime
except ImportError:      # vendored xlsxwriter keeps it private
    from xlsxwriter.utility import _datetime_to_excel_datetime as \
        datetime_to_excel_datetime

from . import config as C
from .styles import Styles, wrap_height

_XLWorksheet = xlsxwriter.worksheet.Worksheet


def _coerce(value):
    """Cached formula results must be a number, a bool or a string.

    XlsxWriter writes whatever it is given straight into ``<v>``; a
    ``datetime.date`` would produce invalid XML that Excel refuses to open.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (datetime.datetime, datetime.date)):
        return datetime_to_excel_datetime(value, False, False)
    if isinstance(value, (str, int, float)):
        return value
    return str(value)


def _safe_write_formula(self, row, col, formula, cell_format=None, value=0):
    """``write_formula`` that also coerces the cached result."""
    return _XLWorksheet.write_formula(self, row, col, formula, cell_format,
                                      _coerce(value))


def r(n):
    """1-indexed spreadsheet row -> 0-indexed XlsxWriter row."""
    return n - 1


def cellref(col, row):
    return "%s%d" % (col, row)


class Book(object):

    def __init__(self, path, theme, edition="premium", mode="blank",
                 protect=None, images=True, demo=None):
        self.path = path
        self.th = theme
        self.edition = edition
        self.mode = mode            # "blank" | "demo"
        self.protect = protect
        self.images = images
        self.demo = demo

        self.order = C.EDITIONS[edition]
        self.wb = xlsxwriter.Workbook(path)
        self.S = Styles(self.wb, theme)
        self.sheets = {}
        self.stats = {"formulas": 0, "validations": 0, "cond_formats": 0,
                      "charts": 0, "links": 0, "cells": 0}

        self._create_sheets()
        self._define_names()

        self.wb.set_properties({
            "title": C.PRODUCT,
            "subject": C.TAGLINE,
            "author": C.AUTHOR,
            "manager": C.AUTHOR,
            "company": C.AUTHOR,
            "category": "Party & Gift Exchange Planning Spreadsheet",
            "keywords": ("secret santa, white elephant, gift exchange, "
                         "party planner, santa draw, wishlists, gift budget, "
                         "party games, excel template, google sheets, "
                         "etsy spreadsheet"),
            "comments": ("%s v%s - %s. Works in Excel 2016+ and Google "
                         "Sheets. No macros, nothing to install."
                         % (C.PRODUCT, C.VERSION, C.TAGLINE)),
        })
        self.wb.set_calc_mode("auto")

    # ------------------------------------------------------------------
    # sheet registry
    # ------------------------------------------------------------------
    def _create_sheets(self):
        for key in self.order:
            ws = self.wb.add_worksheet(C.SHEET_NAMES[key])
            ws.write_formula = types.MethodType(_safe_write_formula, ws)
            ws.set_tab_color(self.th.tabs[key])
            ws.hide_gridlines(2)
            self.sheets[key] = ws
        if "data" in self.sheets:
            self.sheets["data"].hide()
        self.sheets["dashboard"].set_first_sheet()
        self.sheets["dashboard"].activate()
        self.sheets["dashboard"].set_zoom(90)

    def ws(self, key):
        return self.sheets[key]

    def has(self, key):
        return key in self.sheets and key != "data"

    def name(self, key):
        return C.SHEET_NAMES[key]

    def q(self, key):
        """Quoted sheet name for use inside formulas."""
        return "'%s'" % C.SHEET_NAMES[key]

    # ------------------------------------------------------------------
    # defined names
    # ------------------------------------------------------------------
    def _define_names(self):
        su = self.q("setup")
        simple = {
            "PartyName": "%s!$C$%d" % (su, C.SU_BUSINESS),
            "Message": "%s!$C$%d" % (su, C.SU_MESSAGE),
            "Currency": "%s!$C$%d" % (su, C.SU_CURRENCY),
            "PartyYear": "%s!$C$%d" % (su, C.SU_YEAR),
            "PartyDate": "%s!$C$%d" % (su, C.SU_DATE),
            "PartyLocation": "%s!$C$%d" % (su, C.SU_LOCATION),
            "PartyHost": "%s!$C$%d" % (su, C.SU_HOST),
            "BudgetMin": "%s!$C$%d" % (su, C.SU_BMIN),
            "BudgetMax": "%s!$C$%d" % (su, C.SU_BMAX),
            "MaxSteals": "%s!$C$%d" % (su, C.SU_STEALS),
            "StartPlayer": "%s!$C$%d" % (su, C.SU_START),
            "DrawSeed": "%s!$C$%d" % (su, C.SU_SEED),
            "WESeed": "%s!$C$%d" % (su, C.SU_WESEED),
            "DrawStatus": "%s!$C$%d" % (su, C.SU_STATUS),
        }
        for nm, ref in simple.items():
            self.wb.define_name(nm, "=" + ref)

        first = C.SU_LIST_FIRST
        lastc = C.SU_LIST_FIRST + C.SU_LIST_ROWS - 1
        for key, col in sorted(C.LIST_COLS.items()):
            rng = "%s!$%s$%d:$%s$%d" % (su, col, first, col, lastc)
            self.wb.define_name(
                _name_for_list(key),
                "=OFFSET(%s!$%s$%d,0,0,MAX(1,COUNTA(%s)),1)" % (su, col,
                                                                first, rng))

        # Fixed (non-customisable) status lists, in the locked block.
        for nm, (col, n) in sorted(C.FIXED_BLOCKS.items()):
            self.wb.define_name(
                nm, "=%s!$%s$%d:$%s$%d"
                % (su, col, C.SU_FIXED_FIRST, col, C.SU_FIXED_FIRST + n - 1))

        if self.has("rules"):
            ru = self.q("rules")
            for nm, row in (("CoupleRule", 8), ("TeamRule", 9),
                            ("LastYearRule", 10)):
                self.wb.define_name(nm, "=%s!$C$%d" % (ru, row))

        # Dynamic lists that live in the working sheets (grow with the data).
        dyn = {"ParticipantsList": ("participants", "B"),
               "GiftNums": ("we", "D")}
        for nm, (sheet, colL) in sorted(dyn.items()):
            if not self.has(sheet):
                continue
            rng = "%s!$%s$%d:$%s$%d" % (self.q(sheet), colL, C.ROW_FIRST,
                                        colL, C.last_row(sheet))
            base = rng.rsplit("$", 1)[0].rsplit(":", 1)[0]
            self.wb.define_name(
                nm, "=OFFSET(%s,0,0,MAX(1,COUNTA(%s)),1)" % (base, rng))

    # ------------------------------------------------------------------
    # reference helpers
    # ------------------------------------------------------------------
    def col(self, key, field):
        return C.COLS[key][field]

    def rng(self, key, field, first=None, last=None, quoted=True):
        """Absolute range for a column of a tracker sheet."""
        col = self.col(key, field)
        first = C.ROW_FIRST if first is None else first
        last = C.last_row(key) if last is None else last
        ref = "%s!$%s$%d:$%s$%d" % (self.q(key) if quoted else self.name(key),
                                    col, first, col, last)
        return ref

    def cell(self, key, field, row):
        return "%s!$%s$%d" % (self.q(key), self.col(key, field), row)

    def kpi(self, key):
        return "%s!$AI$%d" % (self.q("data"), C.KPI_ROW[key])

    def kpi_fmt(self, key):
        return C.KPI_FMT[key]

    def data_rng(self, col, first, last):
        return "%s!$%s$%d:$%s$%d" % (self.q("data"), col, first, col, last)

    def data_cell(self, col, row):
        return "%s!$%s$%d" % (self.q("data"), col, row)

    def listname(self, key):
        return _name_for_list(key)

    # ------------------------------------------------------------------
    # cached values (so previews look right before Excel recalculates)
    # ------------------------------------------------------------------
    def cached(self, key, default=0):
        if self.demo and key in self.demo.agg:
            return self.demo.agg[key]
        return default

    # ------------------------------------------------------------------
    # money / text formula helpers
    # ------------------------------------------------------------------
    def money(self, value_formula, decimals="#,##0"):
        """Currency-prefixed text, driven by the Currency setting."""
        return 'Currency&TEXT(%s,"%s")' % (value_formula, decimals)

    def bar(self, numerator, denominator, blocks=18):
        """Text progress bar built with REPT()."""
        pct = "MIN(1,IFERROR((%s)/(%s),0))" % (numerator, denominator)
        filled = "ROUND(%s*%d,0)" % (pct, blocks)
        return ('=IFERROR(REPT("\u2588",%s)&REPT("\u2591",%d-%s),"%s")'
                % (filled, blocks, filled, "\u2591" * blocks))

    def bar_static(self, numerator, denominator, blocks=18):
        """Python twin of :meth:`bar` used for cached values."""
        try:
            pct = min(1.0, float(numerator) / float(denominator)) \
                if denominator else 0.0
        except (TypeError, ValueError, ZeroDivisionError):
            pct = 0.0
        filled = int(round(pct * blocks))
        return "\u2588" * filled + "\u2591" * (blocks - filled)

    # ------------------------------------------------------------------
    # page furniture
    # ------------------------------------------------------------------
    def page(self, key, last_col, last_row, landscape=True, freeze=None,
             fit=True, zoom=90, title_rows=None, paper=9):
        ws = self.sheets[key]
        ws.set_zoom(zoom)
        if landscape:
            ws.set_landscape()
        if fit:
            ws.fit_to_pages(1, 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        ws.set_paper(paper)
        ws.set_header("&L&\"%s,Bold\"&11%s&R&\"%s,Italic\"&9Page &P of &N"
                      % (self.th.body_font, C.PRODUCT_SHORT,
                         self.th.body_font))
        ws.set_footer("&C&\"%s,Italic\"&8&A  \u2022  %s v%s  \u2022  "
                      "personal licence"
                      % (self.th.body_font, C.PRODUCT, C.VERSION))
        ws.print_area("A1:%s%d" % (last_col, last_row))
        if title_rows:
            ws.repeat_rows(title_rows[0], title_rows[1])
        if freeze:
            ws.freeze_panes(*freeze)
        if self.protect:
            ws.protect(self.protect, {
                "objects": True, "scenarios": True, "format_cells": True,
                "format_columns": True, "format_rows": True,
                "insert_rows": True, "insert_columns": True,
                "insert_hyperlinks": True, "delete_rows": True,
                "delete_columns": True, "sort": True, "autofilter": True,
                "select_locked_cells": True, "select_unlocked_cells": True,
            })
        return ws

    def widths(self, key, extra=None):
        ws = self.sheets[key]
        for col, width in sorted((C.WIDTHS.get(key, {}) or {}).items()):
            ws.set_column("%s:%s" % (col, col), width)
        for col, width in sorted((extra or {}).items()):
            ws.set_column("%s:%s" % (col, col), width)
        return ws

    def title_block(self, key, title, subtitle, last_col, home=True):
        """Standard 6-row header band used by every tracker tab."""
        ws = self.sheets[key]
        S = self.S
        ws.set_row(r(C.ROW_SPACER_1), 7)
        ws.set_row(r(C.ROW_TITLE), 30)
        ws.set_row(r(C.ROW_SUBTITLE), 18)
        ws.set_row(r(C.ROW_SPACER_2), 7)
        ws.set_row(r(C.ROW_STATS), 26)
        ws.set_row(r(C.ROW_SPACER_3), 7)
        ws.merge_range(r(C.ROW_TITLE), 1, r(C.ROW_TITLE), _ci(last_col) - 3,
                       title, S.sheet_title)
        for c in range(_ci(last_col) - 2, _ci(last_col) + 1):
            ws.write_blank(r(C.ROW_TITLE), c, None, S.canvas)
        ws.merge_range(r(C.ROW_SUBTITLE), 1, r(C.ROW_SUBTITLE),
                       _ci(last_col) - 3, subtitle, S.sheet_sub)
        if home:
            ws.merge_range(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                           r(C.ROW_SUBTITLE), _ci(last_col), "", S.home_link)
            ws.write_url(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                         "internal:%s!A1" % self.q("dashboard"), S.home_link,
                         "\U0001F3E0  Back to Dashboard")
            self.stats["links"] += 1
        else:
            ws.merge_range(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                           r(C.ROW_SUBTITLE), _ci(last_col), "", S.canvas)
        return ws

    def stats_strip(self, key, items, row=None, first_col=1, span=2):
        """Row of small formula chips under the sheet title.

        ``items`` is a list of ``(formula_or_text, colour_key, cached)``.
        """
        ws = self.sheets[key]
        row = C.ROW_STATS if row is None else row
        col = first_col
        for formula, color, cached in items:
            fmt = self.S.pill(self.th.soft(color), getattr(self.th, color),
                              size=10.5, bold=True, align="left")
            ws.merge_range(r(row), col, r(row), col + span - 1, "", fmt)
            if formula.startswith("="):
                ws.write_formula(r(row), col, formula, fmt,
                                 cached if cached is not None else 0)
                self.stats["formulas"] += 1
            else:
                ws.write(r(row), col, formula, fmt)
            col += span
        return ws

    def nav_row(self, key, row, first_col=1, span=2, max_col="N"):
        """Bottom navigation buttons (one per visible tab)."""
        ws = self.sheets[key]
        palette = ["primary", "accent", "gold", "info", "plum", "ok",
                   "primary_2", "warn", "accent", "info"]
        col = first_col
        n = 0
        for target in self.order:
            if target == "data":
                continue
            if col + span - 1 > _ci(max_col):
                row += 1
                col = first_col
                ws.set_row(r(row), 24)
            color = getattr(self.th, palette[n % len(palette)])
            fmt = self.S.nav(color)
            if span > 1:
                ws.merge_range(r(row), col, r(row), col + span - 1, "", fmt)
            label = C.SHEET_SHORT[target]
            if target == key:
                label = "\u25B6 " + label
            ws.write_url(r(row), col, "internal:%s!A1" % self.q(target),
                         fmt, label)
            self.stats["links"] += 1
            col += span
            n += 1
        return row

    # ------------------------------------------------------------------
    # painting / writing helpers
    # ------------------------------------------------------------------
    def paint(self, key, row1, col1, row2, col2, fmt):
        ws = self.sheets[key]
        for rr in range(row1, row2 + 1):
            for cc in range(col1, col2 + 1):
                ws.write_blank(rr, cc, None, fmt)

    def band(self, key, row, col1, col2, fmt, height=None):
        ws = self.sheets[key]
        ws.merge_range(r(row), col1, r(row), col2, "", fmt)
        if height:
            ws.set_row(r(row), height)

    def write(self, key, row, col, value, fmt=None, cached=None):
        ws = self.sheets[key]
        self.stats["cells"] += 1
        if isinstance(value, str) and value.startswith("="):
            ws.write_formula(r(row), col, value, fmt,
                             cached if cached is not None else 0)
            self.stats["formulas"] += 1
        elif value is None or value == "":
            ws.write_blank(r(row), col, None, fmt)
        else:
            ws.write(r(row), col, value, fmt)
        return ws

    def merge(self, key, row1, col1, row2, col2, value, fmt=None,
              cached=None):
        ws = self.sheets[key]
        self.stats["cells"] += 1
        if isinstance(value, str) and value.startswith("="):
            ws.merge_range(r(row1), col1, r(row2), col2, "", fmt)
            ws.write_formula(r(row1), col1, value, fmt,
                             cached if cached is not None else 0)
            self.stats["formulas"] += 1
        else:
            ws.merge_range(r(row1), col1, r(row2), col2, value, fmt)
        return ws

    def para(self, key, row, col1, col2, text, fmt, width_chars=None,
             minimum=18):
        """Merged, wrapped paragraph with a row height that actually fits."""
        if width_chars is None:
            width_chars = sum(
                (C.WIDTHS.get(key, {}) or {}).get(_cl(c), 10)
                for c in range(col1, col2 + 1))
        h = wrap_height(text, width_chars, minimum=minimum)
        self.merge(key, row, col1, row, col2, text, fmt)
        self.sheets[key].set_row(r(row), h)
        return row + 1

    def validate(self, key, row1, col1, row2, col2, source, title=None,
                 message=None, error=None, error_type="stop"):
        ws = self.sheets[key]
        opts = {"validate": "list", "source": source, "ignore_blank": True,
                "show_input": bool(title or message),
                "show_error": bool(error)}
        if title:
            opts["input_title"] = title[:32]
        if message:
            opts["input_message"] = message[:255]
        if error:
            opts["error_title"] = "Pick from the list"[:32]
            opts["error_message"] = error[:255]
            opts["error_type"] = error_type
        res = ws.data_validation(r(row1), col1, r(row2), col2, opts)
        if res == 0:
            self.stats["validations"] += 1
        return res

    def cond(self, key, row1, col1, row2, col2, opts):
        ws = self.sheets[key]
        res = ws.conditional_format(r(row1), col1, r(row2), col2, opts)
        if res == 0:
            self.stats["cond_formats"] += 1
        return res

    def chart(self, ctype, **opts):
        ch = self.wb.add_chart(dict({"type": ctype}, **opts))
        ch.show_hidden_data()          # data lives on the hidden _Data sheet
        ch.show_blanks_as("gap")
        self.stats["charts"] += 1
        return ch

    def close(self):
        self.wb.close()


# ----------------------------------------------------------------------
# small utilities
# ----------------------------------------------------------------------
def _ci(letter):
    """Column letter -> 0-indexed column number."""
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def _cl(index):
    """0-indexed column number -> column letter."""
    s = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        s = chr(65 + rem) + s
    return s


_LIST_NAMES = {
    "teams": "Teams",
    "diets": "Diets",
    "statuses": "Statuses",
    "rsvp": "RSVP",
    "actions": "Actions",
    "priorities": "Priorities",
    "onoff": "OnOff",
    "participants": "ParticipantsList",
    "giftnums": "GiftNums",
}


def _name_for_list(key):
    return _LIST_NAMES[key]


def name_for_list(key):
    return _LIST_NAMES[key]


def ci(letter):
    return _ci(letter)


def cl(index):
    return _cl(index)
````

---
## `santa_tracker/sheets/__init__.py`

*Sheet modules.* (1 lines)

````python

````

---
## `santa_tracker/sheets/common.py`

*Shared sheet helpers: headers, chips, dropdowns, tables, footers - plus the chip cache label fix.* (414 lines)

````python
"""Shared worksheet furniture: headers, data rows, totals, validations."""

from datetime import date, datetime

from .. import config as C
from ..book import r, ci, cl


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def first_row():
    return C.ROW_FIRST


def last_row(key):
    return C.last_row(key)


def n_rows(key):
    return C.CAP[key]


def alt(rownum):
    """Zebra stripe: even spreadsheet rows get the tinted background."""
    return (rownum % 2) == 0


# ---------------------------------------------------------------------------
# headers
# ---------------------------------------------------------------------------
def header_row(bk, key, columns, row=None, height=36):
    """``columns`` = list of (field, label, kind, colour_key|None)."""
    ws = bk.ws(key)
    row = C.ROW_HEADER if row is None else row
    for field, label, kind, color in columns:
        col = ci(bk.col(key, field))
        ws.write(r(row), col, label,
                 bk.S.header(getattr(bk.th, color) if color else None))
    ws.set_row(r(row), height)
    return row


def data_rows(bk, key, height=20):
    ws = bk.ws(key)
    for i in range(n_rows(key)):
        ws.set_row(r(C.ROW_FIRST + i), height)


def table_frame(bk, key, columns, height=20):
    """Write the header and pre-format every empty data cell."""
    header_row(bk, key, columns)
    ws = bk.ws(key)
    data_rows(bk, key, height)
    for i in range(n_rows(key)):
        rownum = C.ROW_FIRST + i
        a = alt(rownum)
        for field, label, kind, color in columns:
            col = ci(bk.col(key, field))
            if kind == "idx":
                fmt = bk.S.idx(a)
            elif kind.startswith("calc"):
                fmt = bk.S.cell(kind)
            else:
                fmt = bk.S.cell(kind, a)
            ws.write_blank(r(rownum), col, None, fmt)
    return ws


# ---------------------------------------------------------------------------
# writing a single row of a tracker table
# ---------------------------------------------------------------------------
def write_row(bk, key, columns, rownum, values, cached=None):
    ws = bk.ws(key)
    a = alt(rownum)
    cached = cached or {}
    for field, label, kind, color in columns:
        col = ci(bk.col(key, field))
        value = values.get(field)
        if kind == "idx":
            fmt = bk.S.idx(a)
        elif kind.startswith("calc"):
            fmt = bk.S.cell(kind)
        else:
            fmt = bk.S.cell(kind, a)
        if value is None or value == "":
            ws.write_blank(r(rownum), col, None, fmt)
        elif isinstance(value, str) and value.startswith("="):
            ws.write_formula(r(rownum), col, value, fmt,
                             cached.get(field, 0))
            bk.stats["formulas"] += 1
            bk.stats["cells"] += 1
        elif isinstance(value, (date, datetime)):
            ws.write_datetime(r(rownum), col, value, fmt)
            bk.stats["cells"] += 1
        else:
            ws.write(r(rownum), col, value, fmt)
            bk.stats["cells"] += 1
    return ws


# ---------------------------------------------------------------------------
# validation presets
# ---------------------------------------------------------------------------
def list_dv(bk, key, field, list_key, title=None, message=None, error=None,
            first=None, last=None):
    return bk.validate(key, first or C.ROW_FIRST, ci(bk.col(key, field)),
                       last or C.last_row(key), ci(bk.col(key, field)),
                       "=" + bk.listname(list_key), title=title,
                       message=message, error=error)


def fixed_dv(bk, key, field, name, title=None, message=None, error=None):
    return bk.validate(key, C.ROW_FIRST, ci(bk.col(key, field)),
                       C.last_row(key), ci(bk.col(key, field)), "=" + name,
                       title=title, message=message, error=error)


def tick_dv(bk, key, fields, message="Pick \u2713 from the dropdown to tick "
                                     "it off (leave blank for not yet)."):
    if isinstance(fields, str):
        fields = (fields,)
    for field in fields:
        bk.validate(key, C.ROW_FIRST, ci(bk.col(key, field)),
                    C.last_row(key), ci(bk.col(key, field)), "=Tick",
                    title="Tick it off", message=message)


def money_dv(bk, key, fields, label="money"):
    if isinstance(fields, str):
        fields = (fields,)
    for field in fields:
        bk.ws(key).data_validation(
            r(C.ROW_FIRST), ci(bk.col(key, field)),
            r(C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "decimal", "criteria": ">=", "value": 0,
             "ignore_blank": True, "show_error": True,
             "error_title": "Enter %s" % label,
             "error_message": "Please enter a positive number (no currency "
                              "symbol) - the symbol comes from Setup.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


def date_dv(bk, key, fields, message="Type a date, or pick one from the "
                                     "calendar picker.", first=None,
            last=None):
    if isinstance(fields, str):
        fields = (fields,)
    for field in fields:
        bk.ws(key).data_validation(
            r(first or C.ROW_FIRST), ci(bk.col(key, field)),
            r(last or C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "date", "criteria": "between",
             "minimum": date(2000, 1, 1), "maximum": date(2100, 12, 31),
             "ignore_blank": True, "show_input": True, "input_title": "Date",
             "input_message": message, "show_error": True,
             "error_title": "That's not a date",
             "error_message": "Enter a date between 2000 and 2100.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


def whole_dv(bk, key, fields, minimum=0, maximum=9999):
    if isinstance(fields, str):
        fields = (fields,)
    for field in fields:
        bk.ws(key).data_validation(
            r(C.ROW_FIRST), ci(bk.col(key, field)),
            r(C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "whole", "criteria": "between", "minimum": minimum,
             "maximum": maximum, "ignore_blank": True, "show_error": True,
             "error_title": "Whole numbers only",
             "error_message": "Please enter a whole number.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


# ---------------------------------------------------------------------------
# conditional formatting presets
# ---------------------------------------------------------------------------
def tick_cf(bk, key, fields):
    """Green glow on any ticked box."""
    if isinstance(fields, str):
        fields = (fields,)
    for field in fields:
        col = ci(bk.col(key, field))
        L = bk.col(key, field)
        bk.cond(key, C.ROW_FIRST, col, C.last_row(key), col, {
            "type": "formula", "criteria": '=$%s%d="%s"' % (L, C.ROW_FIRST,
                                                            C.TICK),
            "format": bk.S.cf(bg=bk.th.ok_soft, fg=bk.th.ok, bold=True,
                              size=13, border=bk.th.border)})


def secret_cf(bk, key, field):
    """Secret Mode: make the hiding-spot text invisible (white on white)."""
    col = ci(bk.col(key, field))
    bk.cond(key, C.ROW_FIRST, col, C.last_row(key), col, {
        "type": "formula", "criteria": '=SecretMode="Yes"',
        "format": bk.S.cf(bg=bk.th.card, fg=bk.th.card)})


def status_cf(bk, key, field, mapping, first=None, last=None):
    """Colour a status column.  ``mapping`` = {cell text: (bg, fg)}."""
    L = bk.col(key, field)
    col = ci(L)
    first = first or C.ROW_FIRST
    last = last or C.last_row(key)
    for text, (bg, fg) in mapping.items():
        bk.cond(key, first, col, last, col, {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (L, first, text),
            "format": bk.S.cf(bg=bg, fg=fg, bold=True, border=bk.th.border)})


def deadline_cf(bk, key, date_field, tick_field=None):
    """Overdue = red, due inside the DueSoonDays window = amber."""
    L = bk.col(key, date_field)
    col = ci(L)
    first, last = C.ROW_FIRST, C.last_row(key)
    done = ""
    if tick_field:
        done = '*($%s%d<>"%s")' % (bk.col(key, tick_field), first, C.TICK)
    bk.cond(key, first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<TODAY()%s)' % (L, first, L, first,
                                                         done),
        "format": bk.S.cf(bg=bk.th.bad_soft, fg=bk.th.bad, bold=True)})
    bk.cond(key, first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d>=TODAY(),$%s%d-TODAY()<=DueSoonDays%s)'
                   % (L, first, L, first, done),
        "format": bk.S.cf(bg=bk.th.warn_soft, fg=bk.th.warn, bold=True)})


def databar(bk, key, field, color=None, first=None, last=None):
    col = ci(bk.col(key, field))
    bk.cond(key, first or C.ROW_FIRST, col, last or C.last_row(key), col, {
        "type": "data_bar", "bar_color": color or bk.th.primary_2,
        "bar_solid": True, "min_type": "num", "min_value": 0,
        "max_type": "num", "max_value": 1})


# ---------------------------------------------------------------------------
# totals row
# ---------------------------------------------------------------------------
def totals_row(bk, key, row, cells, first_col="B", last_col=None,
               label="TOTALS", label_span=None):
    """``cells`` = {field: (formula, kind, cached)}."""
    ws = bk.ws(key)
    th = bk.th
    lab_fmt = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.white,
                                 bg_color=th.primary, align="right",
                                 valign="vcenter", border=1,
                                 border_color=th.primary, indent=1))
    if label_span:
        c1, c2 = label_span
        if c1 == c2:
            ws.write(r(row), ci(c1), label, lab_fmt)
        else:
            ws.merge_range(r(row), ci(c1), r(row), ci(c2), label, lab_fmt)
    else:
        ws.write(r(row), ci(first_col), label, lab_fmt)
    for field, (formula, kind, cached) in cells.items():
        col = ci(bk.col(key, field))
        fmt = bk.S.f(**bk.S.base(
            font_size=11, bold=True, font_color=th.white, bg_color=th.primary,
            align="right" if kind != "center" else "center",
            valign="vcenter", border=1, border_color=th.primary,
            num_format=kind))
        if isinstance(formula, str) and formula.startswith("="):
            ws.write_formula(r(row), col, formula, fmt, cached or 0)
            bk.stats["formulas"] += 1
        else:
            ws.write(r(row), col, formula, fmt)
    if last_col:
        span_end = ci(label_span[1]) if label_span else ci(first_col)
        for c in range(ci(first_col), ci(last_col) + 1):
            letter = cl(c)
            if letter not in [bk.col(key, f) for f in cells] and \
                    c > span_end:
                ws.write_blank(r(row), c, None, bk.S.f(**bk.S.base(
                    bg_color=th.primary, border=1, border_color=th.primary)))
    ws.set_row(r(row), 24)
    return row


def blank_row(bk, key, row, first_col="A", last_col="N", height=8, fmt=None):
    ws = bk.ws(key)
    fmt = fmt or bk.S.canvas
    ws.set_row(r(row), height)
    for c in range(ci(first_col), ci(last_col) + 1):
        ws.write_blank(r(row), c, None, fmt)
    return row


def note_block(bk, key, row, first_col, last_col, lines, title=None):
    """A bordered, wrapped tip box."""
    ws = bk.ws(key)
    width = sum((C.WIDTHS.get(key, {}) or {}).get(cl(c), 10)
                for c in range(ci(first_col), ci(last_col) + 1))
    if title:
        ws.merge_range(r(row), ci(first_col), r(row), ci(last_col), title,
                       bk.S.section_soft)
        ws.set_row(r(row), 22)
        row += 1
    text = "\n".join(lines)
    from ..styles import wrap_height
    h = wrap_height(text, width, minimum=20)
    ws.merge_range(r(row), ci(first_col), r(row), ci(last_col), text,
                   bk.S.note)
    ws.set_row(r(row), h)
    return row + 1


# ===========================================================================
# shared page furniture
# ===========================================================================
def sheet_head(bk, key, last_col, title, sub):
    """Canvas, widths, title band and the home link."""
    from .. import config as _C
    S, th = bk.S, bk.th
    ws = bk.ws(key)
    bk.widths(key, _C.WIDTHS[key])
    try:
        depth = _C.last_row(key) + 10
    except KeyError:
        depth = 60
    # the stats chips live on ROW_STATS and can run past the table width,
    # so the canvas always covers at least column P
    wide_col = max(ci(last_col), 15)
    bk.paint(key, 0, 0, depth, wide_col, S.canvas)
    ws.set_row(r(_C.ROW_SPACER_1), 7)
    ws.set_row(r(_C.ROW_TITLE), 32)
    ws.set_row(r(_C.ROW_SUBTITLE), 18)
    ws.set_row(r(_C.ROW_SPACER_2), 8)
    ws.set_row(r(_C.ROW_STATS), 22)
    ws.set_row(r(_C.ROW_SPACER_3), 8)
    if ci(last_col) >= 5:
        t_end, sub_end, link_c1 = (ci(last_col) - 3, ci(last_col) - 3,
                                   ci(last_col) - 2)
    else:
        # narrow sheet: title across the full width, home link in the
        # last column (no overlap)
        t_end, sub_end, link_c1 = ci(last_col), ci(last_col) - 1, ci(last_col)
    ws.merge_range(r(_C.ROW_TITLE), 1, r(_C.ROW_TITLE), t_end,
                   title, S.sheet_title)
    ws.merge_range(r(_C.ROW_SUBTITLE), 1, r(_C.ROW_SUBTITLE),
                   sub_end, "  " + sub, S.sheet_sub)
    ws.merge_range(r(_C.ROW_SUBTITLE), link_c1,
                   r(_C.ROW_SUBTITLE), ci(last_col), "", S.home_link)
    ws.write_url(r(_C.ROW_SUBTITLE), link_c1,
                 "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                 "\U0001F3E0  Dashboard")


def _chip_cache(formula, cached):
    """Demo chip caches omit the emoji label the formula actually prints."""
    import re as _re
    if not isinstance(cached, str):
        return cached
    m = _re.match(r'^="([^"]*)"&', formula)
    if not m:
        return cached
    parts = m.group(1).split(" ", 1)         # ("\U0001F3B2", "Players: ")
    if len(parts) != 2 or not parts[0].strip():
        return cached
    text = parts[1].rstrip()                 # "Players:" / "Now: seat"
    if text and cached.startswith(text):
        return parts[0] + " " + cached
    return cached


def chips(bk, key, chips, last_col=None):
    """Stats pills on ROW_STATS. chips = (formula, colour, cached, span)."""
    from .. import config as _C
    S, th = bk.S, bk.th
    ws = bk.ws(key)
    last_col = last_col or _C.cols_last(key)
    col = 1
    for formula, color, cached, span in chips:
        cached = _chip_cache(formula, cached)
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5,
                     bold=True, align="left")
        ws.merge_range(r(_C.ROW_STATS), col, r(_C.ROW_STATS),
                       col + span - 1, "", fmt)
        ws.write_formula(r(_C.ROW_STATS), col,
                         formula if formula.startswith("=")
                         else '="' + formula, fmt, cached)
        bk.stats["formulas"] += 1
        col += span
    if col <= ci(last_col):
        ws.merge_range(r(_C.ROW_STATS), col, r(_C.ROW_STATS),
                       ci(last_col), "", S.canvas)


def footer_nav(bk, key, row, last_col, landscape=True, zoom=90, tip=None):
    """Gold tip strip, nav grid and print setup."""
    S, th = bk.S, bk.th
    ws = bk.ws(key)
    ws.set_row(r(row), 30)
    ws.merge_range(r(row), 1, r(row), ci(last_col),
                   tip or "  \U0001F4A1  Cream cells are yours to type in; "
                          "white cells calculate.  Dropdowns keep every "
                          "column honest.",
                   S.f(**S.base(font_size=10, italic=True,
                                font_color=th.ink, bg_color=th.gold_soft,
                                align="left", valign="vcenter", indent=1)))
    nav = row + 2
    ws.set_row(r(nav), 24)
    bk.nav_row(key, nav, max_col=last_col)
    bk.page(key, last_col, nav + 1, landscape=landscape, zoom=zoom)
````

---
## `santa_tracker/sheets/data.py`

*Hidden _Data engine room: KPI formulas, status pools, lists.* (123 lines)

````python
"""_Data - the hidden calculation engine (KPIs for the dashboard)."""

from .. import config as C
from ..book import r, ci


def build(bk):
    key = "data"
    ws = bk.ws(key)
    for col, width in (("A", 3), ("AH", 26), ("AI", 12)):
        ws.set_column(ci(col), ci(col), width)
    m = bk.demo
    premium = bk.has("we")
    has_rules = bk.has("rules")

    hdr = bk.S.f(**bk.S.base(font_size=9, bold=True, font_color=bk.th.white,
                             bg_color=bk.th.muted, align="center",
                             valign="vcenter"))
    ws.write(r(1), ci("AH"), "Metric", hdr)
    ws.write(r(1), ci("AI"), "Value", hdr)

    names = bk.rng("participants", "name")
    rsvp = bk.rng("participants", "rsvp")
    diet = bk.rng("participants", "diet")
    status = bk.rng("participants", "status")
    dfinal = bk.rng("draw", "final")
    dflag = bk.rng("draw", "flag")
    bspent = bk.rng("budget", "spent")
    bflag = bk.rng("budget", "flag")

    F = {}
    F["participants"] = ("=COUNTA(%s)" % names, "#,##0")
    F["rsvp_yes"] = ('=COUNTIF(%s,"Yes")' % rsvp, "#,##0")
    F["rsvp_pending"] = ('=COUNTIF(%s,"Maybe")' % rsvp, "#,##0")
    F["assigned"] = ('=SUMPRODUCT(--(%s<>""))' % dfinal, "#,##0")
    F["purchased"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                      % (status, C.ST_BOUGHT, status, C.ST_WRAPPED,
                         status, C.ST_DONE), "#,##0")
    F["wrapped"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                    % (status, C.ST_WRAPPED, status, C.ST_DONE), "#,##0")
    F["complete"] = ('=COUNTIF(%s,"%s")' % (status, C.ST_DONE), "#,##0")
    F["total_budget"] = ("=$AI$%d*BudgetMax" % C.KPI_ROW["participants"],
                         "#,##0.00")
    F["spent"] = ("=SUM(%s)" % bspent, "#,##0.00")
    F["avg_gift"] = ('=IFERROR($AI$%d/$AI$%d,0)'
                     % (C.KPI_ROW["spent"], C.KPI_ROW["purchased"]),
                     "#,##0.00")
    rules = ('SUMPRODUCT(--(%s<>""))' % bk.rng("rules", "giver")) \
        if has_rules else "0"
    F["rules_count"] = (
        '=(CoupleRule="On")+(TeamRule="On")+(LastYearRule="On")+%s'
        % rules if has_rules else "=0", "#,##0")
    if premium:
        wplayer = bk.rng("we", "player")
        wstatus = bk.rng("we", "status")
        hturn = bk.rng("history", "turn")
        F["we_players"] = ("=COUNTA(%s)" % wplayer, "#,##0")
        F["gifts_in_play"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                              % (wstatus, C.GS_HELD, wstatus, C.GS_STOLEN),
                              "#,##0")
        F["locked_gifts"] = ('=COUNTIF(%s,"%s")' % (wstatus, C.GS_FINAL),
                             "#,##0")
        F["turns_done"] = ("=COUNT(%s)" % hturn, "#,##0")
        F["current_turn"] = ('=IF($AI$%d=0,"",MOD(StartPlayer-1+$AI$%d,'
                             '$AI$%d)+1)'
                             % (C.KPI_ROW["we_players"],
                                C.KPI_ROW["turns_done"],
                                C.KPI_ROW["we_players"]), "#,##0")
    else:
        for k in ("we_players", "gifts_in_play", "locked_gifts",
                  "turns_done", "current_turn"):
            F[k] = ("=0", "#,##0")
    F["completion"] = ('=IFERROR(($AI$%d+$AI$%d+$AI$%d)/(3*$AI$%d),0)'
                       % (C.KPI_ROW["purchased"], C.KPI_ROW["wrapped"],
                          C.KPI_ROW["complete"],
                          C.KPI_ROW["participants"]), "0%")
    F["violations"] = ('=COUNTIF(%s,"?*")-COUNTIF(%s,"%s OK")'
                       % (dflag, dflag, "\u2705"), "#,##0")
    F["over_budget"] = ('=COUNTIF(%s,"%s")' % (bflag, C.BF_OVER), "#,##0")
    F["diets"] = ("=COUNTA(%s)" % diet, "#,##0")

    # small pools for dashboard charts (status + rsvp mixes)
    pool = bk.S.f(**bk.S.base(font_size=9, font_color=bk.th.muted,
                              align="left", valign="vcenter"))
    pval = bk.S.f(**bk.S.base(font_size=9, font_color=bk.th.ink,
                              align="right", valign="vcenter",
                              num_format="#,##0"))
    for i, stt in enumerate((C.ST_NOT, C.ST_BOUGHT, C.ST_WRAPPED,
                             C.ST_DONE)):
        ws.write(r(40 + i), ci("AH"), stt, pool)
        ws.write_formula(r(40 + i), ci("AI"), '=COUNTIF(%s,"%s")'
                         % (status, stt), pval,
                         (sum(1 for x in (m.people if m else [])
                              if x["status"] == stt) if m else 0))
        bk.stats["formulas"] += 1
    for i, rv in enumerate(("Yes", "No", "Maybe")):
        ws.write(r(45 + i), ci("AH"), rv, pool)
        ws.write_formula(r(45 + i), ci("AI"), '=COUNTIF(%s,"%s")'
                         % (rsvp, rv), pval,
                         (sum(1 for x in (m.people if m else [])
                              if x["rsvp"] == rv) if m else 0))
        bk.stats["formulas"] += 1

    lab = bk.S.f(**bk.S.base(font_size=9.5, font_color=bk.th.muted,
                             align="left", valign="vcenter"))
    val = bk.S.f(**bk.S.base(font_size=9.5, font_color=bk.th.ink,
                             align="right", valign="vcenter"))
    for name, row in sorted(C.KPI_ROW.items()):
        formula, fmt = F[name]
        ws.write(r(row), ci("AH"), name, lab)
        # blank workbooks cache 0 (what the formulas give on empty data) and
        # BASIC edition writes plain "=0" for the white-elephant metrics
        cached = 0
        if m and formula != "=0":
            cached = m.agg.get(name, 0)
        ws.write_formula(r(row), ci("AI"), formula,
                         bk.S.f(**bk.S.base(font_size=9.5,
                                            font_color=bk.th.ink,
                                            align="right", valign="vcenter",
                                            num_format=fmt)),
                         cached)
        bk.stats["formulas"] += 1
````

---
## `santa_tracker/sheets/setup.py`

*Settings & Instructions tab: party basics, seeds, budget range.* (148 lines)

````python
"""⚙️ Settings & Instructions - party info, rules of the game, lists."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "setup"
LAST_COL = "H"


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\u2699\ufe0f  Settings & Instructions",
                 "Everything the party needs to know: dates, budgets, "
                 "steal limits and your own dropdown lists.")
    bk.paint(KEY, 0, 0, 70, ci(LAST_COL), bk.S.canvas)

    label = bk.S.f(**bk.S.base(font_size=10.5, bold=True, font_color=th.ink,
                               bg_color=th.card, align="left",
                               valign="vcenter", indent=1, border=1,
                               border_color=th.border))
    text = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.ink,
                              bg_color=th.gold_soft, border=1,
                              border_color=th.border_strong, align="left",
                              valign="vcenter", indent=1, locked=False))
    num = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.ink,
                             bg_color=th.gold_soft, border=1,
                             border_color=th.border_strong, align="right",
                             valign="vcenter", locked=False,
                             num_format="#,##0.00"))
    intf = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.ink,
                              bg_color=th.gold_soft, border=1,
                              border_color=th.border_strong, align="right",
                              valign="vcenter", locked=False,
                              num_format="#,##0"))
    datef = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.ink,
                               bg_color=th.gold_soft, border=1,
                               border_color=th.border_strong, align="right",
                               valign="vcenter", locked=False,
                               num_format="dd mmm yyyy"))
    pick = bk.S.f(**bk.S.base(font_size=10.5, bold=True,
                              font_color=th.primary, bg_color=th.gold_soft,
                              border=1, border_color=th.border_strong,
                              align="left", valign="vcenter", indent=1,
                              locked=False))

    def setting(row, text_, value, fmt, cached=None):
        # single write: the demo value when there is one, the placeholder
        # otherwise (a second write would silently overwrite the first -
        # XlsxWriter lets the last write win)
        ws.set_row(r(row), 22)
        ws.write(r(row), 1, text_, label)
        ws.write(r(row), 2, cached if cached is not None else value, fmt)

    ws.merge_range(r(4), 1, r(4), ci(LAST_COL),
                   "  \U0001F389  THE PARTY", bk.S.section_soft)
    setting(C.SU_BUSINESS, "Party name", "Your party name", pick,
            m.settings["party"] if m else None)
    setting(C.SU_MESSAGE, "Dashboard message of the day",
            "Type a message for the dashboard banner", pick,
            m.settings["message"] if m else None)
    ws.merge_range(r(9), 1, r(9), ci(LAST_COL),
                   "  \U0001F39B\ufe0f  RULES OF THE GAME", bk.S.section_soft)
    setting(C.SU_CURRENCY, "Currency symbol", "$", text,
            m.settings["currency"] if m else None)
    setting(C.SU_YEAR, "Party year (used everywhere)", 2026, intf,
            m.settings["year"] if m else None)
    setting(C.SU_DATE, "Party date", None, datef,
            m.settings["date"] if m else None)
    setting(C.SU_LOCATION, "Location", "Where is the party?", text,
            m.settings["location"] if m else None)
    setting(C.SU_HOST, "Host", "Who is hosting?", text,
            m.settings["host"] if m else None)
    setting(C.SU_BMIN, "Minimum gift budget", 20, num,
            m.settings["bmin"] if m else None)
    setting(C.SU_BMAX, "Maximum gift budget", 35, num,
            m.settings["bmax"] if m else None)
    setting(C.SU_STEALS, "Max steals per gift (White Elephant)", 2, intf,
            m.settings["steals"] if m else None)
    setting(C.SU_START, "Starting player seat (White Elephant)", 1, intf,
            m.settings["start"] if m else None)
    setting(C.SU_SEED, "Secret Santa draw seed (change = re-draw)", 5, intf,
            m.settings["seed"] if m else None)
    setting(C.SU_WESEED, "White Elephant seat seed", 7, intf,
            m.settings["weseed"] if m else None)
    setting(C.SU_STATUS, "Draw status", C.DRAW_DRAFT, pick,
            m.settings["status"] if m else None)
    bk.validate(KEY, C.SU_STATUS, 2, C.SU_STATUS, 2,
                '="%s,%s"' % (C.DRAW_DRAFT, C.DRAW_FINAL),
                title="Draw status")

    # ------------------------------------------------------------------
    ws.merge_range(r(C.SU_LIST_HEADER), 1, r(C.SU_LIST_HEADER), ci(LAST_COL),
                   "  \U0001F4DD  YOUR LISTS - rename or add, every dropdown "
                   "follows", bk.S.section_soft)
    ws.set_row(r(C.SU_LIST_HEADER), 20)
    for col, title in ((ci("C"), "Teams / departments"),
                       (ci("D"), "Dietary restrictions")):
        ws.write(r(C.SU_LIST_HEADER + 1), col, title, bk.S.thead)
    list_fmt = bk.S.f(**bk.S.base(font_size=10, font_color=th.ink,
                                  bg_color=th.card, border=1,
                                  border_color=th.border, locked=False,
                                  align="left", valign="vcenter", indent=1))
    defaults = {"C": ["Studio", "Shop", "Online", "Friends", "Family"],
                "D": ["Vegetarian", "Vegan", "Gluten-free", "Halal",
                      "Nut allergy"]}
    for i in range(C.SU_LIST_ROWS):
        row = C.SU_LIST_FIRST + i
        ws.set_row(r(row), 18)
        for col in ("C", "D"):
            val = defaults[col][i] if i < len(defaults[col]) else ""
            ws.write(r(row), ci(col), val, list_fmt)

    # fixed lists (locked)
    ws.merge_range(r(C.SU_FIXED_FIRST - 2), 1, r(C.SU_FIXED_FIRST - 2),
                   ci(LAST_COL),
                   "  \U0001F512  BUILT-IN LISTS (part of the engine - "
                   "do not edit)", bk.S.section_soft)
    fixed_fmt = bk.S.f(**bk.S.base(font_size=9.5, font_color=th.muted,
                                   align="left", valign="vcenter",
                                   indent=1))
    blocks = {"Statuses": [C.ST_NOT, C.ST_BOUGHT, C.ST_WRAPPED, C.ST_DONE],
              "RSVP": ["Yes", "No", "Maybe"],
              "Actions": ["Pick", "Steal", "Pass"],
              "Priorities": ["Must-love", "Nice to have", "Just an idea"],
              "Tick": [C.TICK, ""],
              "OnOff": ["On", "Off"]}
    for nm, (col, n) in sorted(C.FIXED_BLOCKS.items()):
        ws.write(r(C.SU_FIXED_FIRST - 1), ci(col), nm, bk.S.thead)
        for i, val in enumerate(blocks[nm]):
            ws.write(r(C.SU_FIXED_FIRST + i), ci(col), val, fixed_fmt)

    K.note_block(bk, KEY, C.SU_FIXED_FIRST + 6, "B", "H", [
        "Formula cells are locked so nobody breaks the maths. The sheet "
        "password is \u201cpremium\u201d - unlock via Review \u2192 Unprotect "
        "Sheet if you ever need to change a seed or a formula.",
        "Re-draw the Secret Santa any time: unlock, change the draw seed on "
        "this tab, watch \U0001F385 Secret Santa Draw shuffle, then set Draw "
        "status to Final and re-protect.",
        "White Elephant: log every Pick / Steal / Pass on \U0001F504 Game "
        "History - the \U0001F3B2 White Elephant tab updates holders, steal "
        "counts, locks and final gifts by itself.",
    ], title="\U0001F4D6  HOW TO RUN THE PARTY")
    K.footer_nav(bk, KEY, C.SU_FIXED_FIRST + 12, LAST_COL, landscape=False)
````

---
## `santa_tracker/sheets/dashboard.py`

*Dashboard tab: hero, 12 KPI cards, progress bars, 4 live charts.* (308 lines)

````python
"""🏠 Dashboard - party command centre."""

from .. import config as C
from ..book import r, ci
from . import common as K

import datetime as _dt

KEY = "dashboard"
LAST_COL = "N"


def _today():
    from .. import demo as D
    return D.today()


def build(bk):
    th = bk.th
    S = bk.S
    ws = bk.ws(KEY)
    m = bk.demo
    agg = m.agg if m else {}
    bk.widths(KEY, C.WIDTHS[KEY])
    bk.paint(KEY, 0, 0, C.DASH_NAV + 2, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------------------
    # hero
    # ------------------------------------------------------------------
    ws.set_row(r(1), 8)
    ws.set_row(r(2), 34)
    ws.set_row(r(3), 26)
    ws.set_row(r(4), 20)
    ws.set_row(r(5), 22)
    ws.merge_range(r(2), 1, r(2), ci(LAST_COL), "", S.hero_title)
    ws.write_formula(
        r(2), 1,
        '=IF(PartyName="","\U0001F385  Secret Santa & White Elephant '
        'Command Centre","\U0001F385  "&PartyName&"   \u2022   Secret '
        'Santa & White Elephant Command Centre")', S.hero_title,
        "\U0001F385  %s   \u2022   Secret Santa & White Elephant Command "
        "Centre" % (m.settings["party"] if m else ""))
    bk.stats["formulas"] += 1
    ws.merge_range(r(3), 1, r(3), ci(LAST_COL), "", S.hero_count)
    ws.write_formula(
        r(3), 1,
        '=IF(PartyDate="","", "\U0001F384  "&TEXT(PartyDate,"dddd, dd '
        'mmmm yyyy")&"   \u2022   "&PartyLocation&"   \u2022   hosted by '
        '"&PartyHost&"   \u2022   "&MAX(0,PartyDate-TODAY())&" days to '
        'go!")', S.hero_count,
        ("\U0001F384  %s   \u2022   %s   \u2022   hosted by %s   \u2022   "
         "%d days to go!"
         % (m.settings["date"].strftime("%A, %d %B %Y"),
            m.settings["location"], m.settings["host"],
            max(0, (m.settings["date"] - _today()).days)) if m else ""))
    bk.stats["formulas"] += 1
    ws.merge_range(r(4), 1, r(4), ci(LAST_COL), "", S.hero_meta)
    ws.write_formula(
        r(4), 1,
        '="\U0001F465 "&%s&" guests   \u2022   "&%s&" in the draw   '
        '\u2022   "&%s&" white-elephant players   \u2022   draw: "&'
        'DrawStatus' % (bk.kpi("participants"), bk.kpi("assigned"),
                        bk.kpi("we_players")),
        S.hero_meta,
        "\U0001F465 %d guests   \u2022   %d in the draw   \u2022   %d "
        "white-elephant players   \u2022   draw: %s"
        % (agg.get("participants", 0), agg.get("assigned", 0),
           agg.get("we_players", 0),
           m.settings["status"] if m else ""))
    bk.stats["formulas"] += 1
    msgfmt = S.f(**S.base(bg_color=th.gold, font_color=th.white, bold=True,
                          font_size=10.5, align="left", valign="vcenter",
                          indent=1))
    ws.merge_range(r(5), 1, r(5), ci(LAST_COL), "", msgfmt)
    ws.write_formula(r(5), 1, '="\U0001F4AC  "&Message', msgfmt,
                     "\U0001F4AC  %s" % (m.settings["message"] if m
                                          else ""))
    bk.stats["formulas"] += 1

    ws.merge_range(r(7), 1, r(7), ci(LAST_COL),
                   "  \U0001F389  PARTY AT A GLANCE", S.section)
    ws.set_row(r(7), 22)

    cards1 = [
        ("PARTICIPANTS", "primary", "=%s" % bk.kpi("participants"),
         agg.get("participants", 0)),
        ("SANTA ASSIGNED", "ok", '=%s&" of "&%s'
         % (bk.kpi("assigned"), bk.kpi("participants")),
         "%d of %d" % (agg.get("assigned", 0), agg.get("participants", 0))),
        ("GIFTS PURCHASED", "info", "=%s" % bk.kpi("purchased"),
         agg.get("purchased", 0)),
        ("TOTAL BUDGET", "gold", bk.money(bk.kpi("total_budget"),
                                          "#,##0"),
         "$%s" % format(agg.get("total_budget", 0), ",.0f")),
        ("ACTUAL SPEND", "accent", bk.money(bk.kpi("spent"), "#,##0"),
         "$%s" % format(agg.get("spent", 0), ",.0f")),
        ("AVG GIFT COST", "primary_2", bk.money(bk.kpi("avg_gift"),
                                                "#,##0.00"),
         "$%s" % format(agg.get("avg_gift", 0), ",.2f")),
    ]
    cards2 = [
        ("EXCLUSION RULES", "primary", "=%s" % bk.kpi("rules_count"),
         agg.get("rules_count", 0)),
        ("W-E PLAYERS", "info", "=%s" % bk.kpi("we_players"),
         agg.get("we_players", 0)),
        ("GIFTS IN PLAY", "accent", "=%s" % bk.kpi("gifts_in_play"),
         agg.get("gifts_in_play", 0)),
        ("LOCKED GIFTS", "bad", "=%s" % bk.kpi("locked_gifts"),
         agg.get("locked_gifts", 0)),
        ("RSVP YES", "ok", '=%s&" / "&%s'
         % (bk.kpi("rsvp_yes"), bk.kpi("participants")),
         "%d / %d" % (agg.get("rsvp_yes", 0), agg.get("participants", 0))),
        ("COMPLETION", "gold", '=TEXT(%s,"0%%")' % bk.kpi("completion"),
         "%.0f%%" % (100 * agg.get("completion", 0))),
    ]
    _cards(bk, cards1, C.DASH_CARD1_L, C.DASH_CARD1_V)
    _cards(bk, cards2, C.DASH_CARD2_L, C.DASH_CARD2_V)

    _bar(bk, C.DASH_BAR1, "Gift readiness", bk.kpi("purchased"),
         bk.kpi("participants"), agg.get("participants", 0) and
         agg["purchased"] / float(agg["participants"]), "pct")
    _bar(bk, C.DASH_BAR2, "RSVP confirmed", bk.kpi("rsvp_yes"),
         bk.kpi("participants"), agg.get("participants", 0) and
         agg["rsvp_yes"] / float(agg["participants"]), "pct")

    _charts(bk)

    # ------------------------------------------------------------------
    # panels
    # ------------------------------------------------------------------
    row = C.DASH_PANEL
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F3B2  GAME STATE   \u2022   \u26A0\ufe0F  PARTY "
                   "ALERTS", S.section)
    ws.set_row(r(row), 22)
    lab = S.f(**S.base(font_size=10, bold=True, font_color=th.ink,
                       bg_color=th.card, align="left", indent=1,
                       valign="vcenter", border=1, border_color=th.border))
    val = S.f(**S.base(font_size=10.5, bold=True, font_color=th.primary,
                       bg_color=th.card, align="left", indent=1,
                       valign="vcenter", border=1, border_color=th.border))
    left = [
        ("Turns logged", "=%s" % bk.kpi("turns_done"),
         agg.get("turns_done", 0)),
        ("Now playing (seat)", "=%s" % bk.kpi("current_turn"),
         agg.get("current_turn", 0)),
        ("Gifts still stealable", "=%s" % bk.kpi("gifts_in_play"),
         agg.get("gifts_in_play", 0)),
        ("Gifts locked \U0001F512", "=%s" % bk.kpi("locked_gifts"),
         agg.get("locked_gifts", 0)),
    ]
    right = [
        ("RSVP still maybe", "=%s" % bk.kpi("rsvp_pending"),
         agg.get("rsvp_pending", 0)),
        ("Over-budget gifts", "=%s" % bk.kpi("over_budget"),
         agg.get("over_budget", 0)),
        ("Draw rule hits", "=%s" % bk.kpi("violations"),
         agg.get("violations", 0)),
        ("Dietary needs noted", "=%s" % bk.kpi("diets"),
         agg.get("diets", 0)),
    ]
    for i, ((lt, lf, lc), (rt_, rf, rc)) in enumerate(zip(left, right)):
        rr = row + 1 + i
        ws.set_row(r(rr), 20)
        ws.merge_range(r(rr), 1, r(rr), 4, "  " + lt, lab)
        ws.merge_range(r(rr), 5, r(rr), 7, "", val)
        ws.write_formula(r(rr), 5, lf, val, lc)
        bk.stats["formulas"] += 1
        ws.merge_range(r(rr), 8, r(rr), 11, "  " + rt_, lab)
        ws.merge_range(r(rr), 12, r(rr), ci(LAST_COL), "", val)
        ws.write_formula(r(rr), 12, rf, val, rc)
        bk.stats["formulas"] += 1

    K.footer_nav(bk, KEY, C.DASH_NAV, LAST_COL, landscape=True, tip=
                 "  \U0001F4AC  %s" % "Novality Store wishes you a loud, "
                 "glorious, steal-happy party.")


# ===========================================================================
def _cards(bk, cards, row_l, row_v):
    S, th = bk.S, bk.th
    ws = bk.ws("dashboard")
    pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]
    for (label, colour, formula, cached), (c1, c2) in zip(cards, pairs):
        bg = getattr(th, colour)
        lbl = S.f(**S.base(bold=True, font_size=9.5, font_color=th.white,
                           bg_color=bg, align="left", valign="vcenter",
                           indent=1))
        vfmt = S.f(**S.base(bold=True, font_size=15,
                            font_color=bg if colour != "gold" else th.gold,
                            bg_color=th.card, align="center",
                            valign="vcenter"))
        ws.merge_range(r(row_l), c1, r(row_l), c2, "  " + label, lbl)
        ws.merge_range(r(row_v), c1, r(row_v), c2, "", vfmt)
        ws.write_formula(r(row_v), c1,
                         formula if formula.startswith("=")
                         else "=" + formula, vfmt, cached)
        bk.stats["formulas"] += 1
    ws.set_row(r(row_l), 18)
    ws.set_row(r(row_v), 26)


def _bar(bk, row, label, num_k, den_k, cached_pct, kind=None):
    S, th = bk.S, bk.th
    ws = bk.ws("dashboard")
    ws.set_row(r(row), 20)
    ws.merge_range(r(row), 1, r(row), 2, "  " + label, S.bar_label)
    ws.merge_range(r(row), 3, r(row), 9, "", S.bar_text)
    ws.write_formula(r(row), 3, bk.bar(num_k, den_k, 34), S.bar_text,
                     _bar_cached(cached_pct, 34))
    bk.stats["formulas"] += 1
    ws.merge_range(r(row), 10, r(row), 12, "", S.bar_pct)
    ws.write_formula(r(row), 10,
                     '=TEXT(IFERROR(%s/%s,0),"0.0%%")' % (num_k, den_k),
                     S.bar_pct, "%.1f%%" % (100.0 * float(cached_pct or 0)))
    bk.stats["formulas"] += 1


def _bar_cached(pct, blocks):
    filled = int(round(min(1.0, max(0.0, float(pct or 0))) * blocks))
    return "\u2588" * filled + "\u2591" * (blocks - filled)


# ===========================================================================
def _charts(bk):
    S, th = bk.S, bk.th
    wb = bk.wb
    d = bk.q("data")
    premium = bk.has("we")

    def base_chart(ctype, title):
        ch = wb.add_chart({"type": ctype})
        ch.set_title({"name": title, "name_font": {"size": 11,
                                                   "color": th.primary,
                                                   "bold": True}})
        ch.set_size({"width": 470, "height": 250})
        ch.set_chartarea({"border": {"color": th.border},
                          "fill": {"color": th.card}})
        ch.set_legend({"position": "none"})
        ch.show_hidden_data()
        bk.stats["charts"] += 1
        return ch

    ch1 = base_chart("column", "Actual spend per giver")
    ch1.add_series({
        "name": "Spent",
        "categories": "=%s!$B$%d:$B$%d" % (bk.q("participants"),
                                           C.ROW_FIRST,
                                           C.last_row("participants")),
        "values": "=%s!$E$%d:$E$%d" % (bk.q("budget"),
                                       C.ROW_FIRST, C.last_row("budget")),
        "fill": {"color": th.accent},
        "border": {"color": th.border_strong},
    })
    ws = bk.ws("dashboard")
    ws.insert_chart("C%d" % (C.DASH_CHART1 + 1), ch1)

    ch2 = base_chart("doughnut", "Gift readiness mix")
    ch2.add_series({
        "name": "Status",
        "categories": "=%s!$AH$40:$AH$43" % d,
        "values": "=%s!$AI$40:$AI$43" % d,
        "points": [{"fill": {"color": th.bad}},
                   {"fill": {"color": th.warn}},
                   {"fill": {"color": th.info}},
                   {"fill": {"color": th.ok}}],
    })
    ch2.set_legend({"position": "bottom", "font": {"size": 9,
                                                   "color": th.muted}})
    ws.insert_chart("I%d" % (C.DASH_CHART1 + 1), ch2)

    if premium:
        ch3 = base_chart("bar", "Steals per gift")
        wq = bk.q("we")
        ch3.add_series({
            "name": "Steals",
            "categories": "=%s!$D$%d:$D$%d" % (wq, C.ROW_FIRST,
                                               C.last_row("we")),
            "values": "=%s!$G$%d:$G$%d" % (wq, C.ROW_FIRST,
                                           C.last_row("we")),
            "fill": {"color": th.primary_2},
        })
        ws.insert_chart("C%d" % (C.DASH_CHART2 + 1), ch3)

        ch4 = base_chart("column", "Gift values brought")
        ch4.add_series({
            "name": "Value",
            "categories": "=%s!$D$%d:$D$%d" % (wq, C.ROW_FIRST,
                                               C.last_row("we")),
            "values": "=%s!$F$%d:$F$%d" % (wq, C.ROW_FIRST,
                                           C.last_row("we")),
            "fill": {"color": th.gold},
        })
        ws.insert_chart("I%d" % (C.DASH_CHART2 + 1), ch4)
    else:
        ch3 = base_chart("doughnut", "RSVP mix")
        ch3.add_series({
            "name": "RSVP",
            "categories": "=%s!$AH$45:$AH$47" % d,
            "values": "=%s!$AI$45:$AI$47" % d,
            "points": [{"fill": {"color": th.ok}},
                       {"fill": {"color": th.bad}},
                       {"fill": {"color": th.warn}}],
        })
        ch3.set_legend({"position": "bottom", "font": {"size": 9,
                                                       "color": th.muted}})
        ws.insert_chart("C%d" % (C.DASH_CHART2 + 1), ch3)
````

---
## `santa_tracker/sheets/participants.py`

*Participants tab.* (98 lines)

````python
"""👥 Participants - the guest list with RSVP, teams and status."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "participants"
LAST_COL = "J"

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Participant", "text", None),
    ("team", "Team / dept", "center", None),
    ("household", "Household / couple", "center", None),
    ("rsvp", "RSVP", "center", None),
    ("diet", "Dietary needs", "center", None),
    ("lastyear", "Gave to last year", "center", None),
    ("status", "Gift status", "center", None),
    ("wishes", "Wishes", "calc_num", None),
    ("notes", "Notes", "wrap", None),
]


def build(bk):
    th = bk.th
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F465  Participants",
                 "Everyone in the draw - RSVP, household and team feed the "
                 "exclusion rules automatically.")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    if m:
        for i, p in enumerate(m.people):
            row = C.ROW_FIRST + i
            K.write_row(bk, KEY, COLUMNS, row,
                        {"n": i + 1, "name": p["name"], "team": p["team"],
                         "household": p["household"], "rsvp": p["rsvp"],
                         "diet": p["diet"], "lastyear": p["lastyear"],
                         "status": p["status"], "notes": p["notes"] or ""},
                        {"wishes": sum(1 for w in m.wishes
                                       if w[0] == p["name"])})
    for i in range(len(m.people) if m else 0, C.CAP[KEY]):
        K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                    {"n": i + 1, "name": "", "team": "", "household": "",
                     "rsvp": "", "diet": "", "lastyear": "", "status": "",
                     "wishes": "", "notes": ""})
    # wishes count formula per row
    wrng = bk.rng("wishlists", "who") if bk.has("wishlists") else None
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        if wrng:
            bk.ws(KEY).write_formula(
                r(row), ci(bk.col(KEY, "wishes")),
                '=IF($B%d="","",COUNTIF(%s,$B%d))' % (row, wrng, row),
                bk.S.f(**bk.S.base(font_size=10.5, font_color=th.primary,
                                   bg_color=th.alt, align="center",
                                   valign="vcenter", border=1,
                                   border_color=th.border,
                                   num_format="#,##0")),
                sum(1 for w in (m.wishes if m else [])
                    if w[0] == (m.people[i]["name"] if i < len(m.people)
                                else "")) or "")
            bk.stats["formulas"] += 1

    K.list_dv(bk, KEY, "team", "teams")
    K.list_dv(bk, KEY, "diet", "diets")
    K.fixed_dv(bk, KEY, "rsvp", "RSVP")
    K.fixed_dv(bk, KEY, "status", "Statuses")
    K.status_cf(bk, KEY, "status", {
        C.ST_NOT: (th.bad_soft, th.bad),
        C.ST_BOUGHT: (th.warn_soft, th.warn),
        C.ST_WRAPPED: (th.info_soft, th.info),
        C.ST_DONE: (th.ok_soft, th.ok)})
    K.status_cf(bk, KEY, "rsvp", {
        "Yes": (th.ok_soft, th.ok),
        "No": (th.bad_soft, th.bad),
        "Maybe": (th.warn_soft, th.warn)})

    names = "$B$%d:$B$%d" % (C.ROW_FIRST, C.last_row(KEY))
    st = "$H$%d:$H$%d" % (C.ROW_FIRST, C.last_row(KEY))
    rv = "$E$%d:$E$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F465 In the draw: "&COUNTA(%s)' % names, "primary",
         "In the draw: %d" % (m.agg["participants"] if m else 0), 3),
        ('="\u2705 RSVP yes: "&COUNTIF(%s,"Yes")' % rv, "ok",
         "RSVP yes: %d" % (m.agg["rsvp_yes"] if m else 0), 3),
        ('="\u23F3 Awaiting: "&COUNTIF(%s,"Maybe")+COUNTIF(%s,"No")'
         % (rv, rv), "warn",
         "Awaiting: %d" % (sum(1 for p in m.people
                                if p["rsvp"] in ("Maybe", "No"))
                           if m else 0), 3),
        ('="\U0001F381 Ready (wrapped+done): "&COUNTIF(%s,"%s")+COUNTIF(%s,'
         '"%s")' % (st, C.ST_WRAPPED, st, C.ST_DONE), "gold",
         "Ready: %d" % (m.agg["wrapped"] if m else 0), 3),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, C.last_row(KEY) + 2, LAST_COL)
````

---
## `santa_tracker/sheets/draw.py`

*Secret Santa Draw tab: seed-driven shuffle, flags, overrides.* (206 lines)

````python
"""🎅 Secret Santa Draw - seed-driven derangement with rules validation."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "draw"
LAST_COL = "G"

COLUMNS = [
    ("n", "#", "idx", None),
    ("giver", "Giver", "text", None),
    ("computed", "Drawn (auto)", "calc_c", None),
    ("override", "Manual override", "text", None),
    ("final", "FINAL recipient", "calc_c", None),
    ("flag", "Rules check", "calc_wrap", None),
    ("status", "Gift status", "calc_c", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    has_rules = bk.has("rules")
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F385  Secret Santa Draw",
                 "Change the seed on \u2699\ufe0f Settings to shuffle the "
                 "draw - nobody ever draws themselves.")
    K.table_frame(bk, KEY, COLUMNS, height=22)

    p = bk.q("participants")
    names = "%s!$B$%d:$B$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    hh = "%s!$D$%d:$D$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    tm = "%s!$C$%d:$C$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    ly = "%s!$G$%d:$G$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    pst = "%s!$H$%d:$H$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    xg = bk.rng("rules", "giver") if has_rules else None
    xc = bk.rng("rules", "cannot") if has_rules else None

    calc = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.primary,
                              bg_color=th.alt, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border))
    bold = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.ok,
                              bg_color=th.ok_soft, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border))
    flagf = bk.S.f(**bk.S.base(font_size=9.5, font_color=th.ink,
                               bg_color=th.card, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border, text_wrap=True))
    statf = bk.S.f(**bk.S.base(font_size=10, font_color=th.ink,
                               bg_color=th.card, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border))

    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        n = "COUNTA(%s)" % names
        inner = ('IF($E{r}=$B{r},"Self ","")'
                 + ('&IF(AND(CoupleRule="On",IFERROR(INDEX({hh},MATCH($B{r},'
                  '{nm},0)),"")<>"",INDEX({hh},MATCH($B{r},{nm},0))=INDEX('
                  '{hh},MATCH($E{r},{nm},0))),"Couple ","")'
                  + '&IF(AND(TeamRule="On",IFERROR(INDEX({tm},MATCH($B{r},'
                   '{nm},0)),"")<>"",INDEX({tm},MATCH($B{r},{nm},0))=INDEX('
                   '{tm},MATCH($E{r},{nm},0))),"Team ","")' if has_rules
                  else '')
                 + ('&IF(AND(LastYearRule="On",IFERROR(INDEX({ly},MATCH('
                    '$B{r},{nm},0)),"")=$E{r}),"LastYear ","")'
                   if has_rules else '')
                 + ('&IF(COUNTIFS({xg},$B{r},{xc},$E{r})>0,"Custom ","")'
                    if has_rules else '')).format(
            r=row, hh=hh, tm=tm, ly=ly, nm=names, xg=xg, xc=xc)
        values = {
            "n": i + 1,
            "giver": '=IF(%s!$B$%d="","",%s!$B$%d)'
                     % (p, row, p, row),
            "computed": '=IF($B{r}="","",INDEX({nm},MOD($A{r}-1+MOD('
                        'DrawSeed-1,MAX(1,{n}-1)),{n})+1))'.format(
                            r=row, nm=names, n=n),
            "override": "",
            "final": '=IF($B{r}="","",IF($D{r}<>"",$D{r},$C{r}))'.format(
                r=row),
            "flag": '=IF($E{r}="","",IF(TRIM({inner})="","'
                    '\u2705 OK",TRIM({inner})))'.format(r=row, inner=inner),
            "status": '=IF($B{r}="","",INDEX({st},MATCH($B{r},{nm},0)))'
                      .format(r=row, st=pst, nm=names),
        }
        cached = {}
        if m and i < len(m.people):
            cached = {"giver": m.people[i]["name"],
                      "computed": m.assign[i], "final": m.assign[i],
                      "flag": "\u2705 OK",
                      "status": m.people[i]["status"]}
        elif m:
            cached = {"giver": "", "computed": "", "final": "", "flag": "",
                      "status": ""}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        # restyle the computed/final/flag/status cells (kinds are generic)
        ws.write_formula(r(row), ci("C"), values["computed"], calc,
                         cached.get("computed", ""))
        ws.write_formula(r(row), ci("E"), values["final"], bold,
                         cached.get("final", ""))
        ws.write_formula(r(row), ci("F"), values["flag"], flagf,
                         cached.get("flag", ""))
        ws.write_formula(r(row), ci("G"), values["status"], statf,
                         cached.get("status", ""))
        bk.stats["formulas"] += 4

    K.list_dv(bk, KEY, "override", "participants",
              title="Manual override",
              message="Leave blank to keep the automatic draw.")
    K.status_cf(bk, KEY, "status", {
        C.ST_NOT: (th.bad_soft, th.bad),
        C.ST_BOUGHT: (th.warn_soft, th.warn),
        C.ST_WRAPPED: (th.info_soft, th.info),
        C.ST_DONE: (th.ok_soft, th.ok)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=AND($F%d<>"",$F%d<>"\u2705 OK")'
                    % (C.ROW_FIRST, C.ROW_FIRST),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})

    # ------------------------------------------------------------------
    row = C.last_row(KEY) + 2
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F500  DRAW CONTROLS", bk.S.section_soft)
    ws.set_row(r(row), 22)
    lab = bk.S.f(**bk.S.base(font_size=10.5, bold=True, font_color=th.ink,
                             bg_color=th.card, align="left", indent=1,
                             valign="vcenter", border=1,
                             border_color=th.border))
    seedf = bk.S.f(**bk.S.base(font_size=12, bold=True,
                               font_color=th.primary, bg_color=th.gold_soft,
                               border=1, border_color=th.border_strong,
                               align="center", valign="vcenter",
                               locked=False, num_format="#,##0"))
    stat = bk.S.f(**bk.S.base(font_size=10.5, bold=True,
                              font_color=th.primary, bg_color=th.gold_soft,
                              border=1, border_color=th.border_strong,
                              align="center", valign="vcenter"))
    ws.set_row(r(row + 1), 24)
    ws.merge_range(r(row + 1), 1, r(row + 1), 2, "  Draw seed (change to "
                                                "re-draw)", lab)
    ws.write_formula(r(row + 1), 3, "=DrawSeed", seedf,
                     m.settings["seed"] if m else "")
    bk.stats["formulas"] += 1
    ws.merge_range(r(row + 1), 4, r(row + 1), 5, "  Draw status", lab)
    ws.write_formula(r(row + 1), 6, "=DrawStatus", stat,
                     m.settings["status"] if m else "")
    bk.stats["formulas"] += 1

    row += 3
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F575\ufe0f  PRIVATE LOOKUP - type a name, see "
                   "only their recipient", bk.S.section_soft)
    ws.set_row(r(row), 22)
    ws.set_row(r(row + 1), 26)
    inp = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.ink,
                             bg_color=th.card, border=1,
                             border_color=th.border_strong, align="left",
                             valign="vcenter", indent=1, locked=False))
    out = bk.S.f(**bk.S.base(font_size=11.5, bold=True,
                             font_color=th.primary, bg_color=th.card,
                             align="left", valign="vcenter", indent=1))
    ws.merge_range(r(row + 1), 1, r(row + 1), 2, "  I am...", lab)
    ws.merge_range(r(row + 1), 3, r(row + 1), 4, "", inp)
    bk.validate(KEY, row + 1, 3, row + 1, 3,
                "=" + bk.listname("participants"),
                title="Your name")
    ws.merge_range(r(row + 1), 5, r(row + 1), ci(LAST_COL), "", out)
    ws.write_formula(
        r(row + 1), 5,
        '=IF($C%d="","Type your name to peek at your recipient\u2026",'
        'IFERROR("\U0001F385  You are drawing:  "&INDEX($E$%d:$E$%d,MATCH('
        '$C%d,$B$%d:$B$%d,0))&"   \u2022   budget "&Currency&TEXT(BudgetMin,'
        '"#,##0")&"\u2013"&Currency&TEXT(BudgetMax,"#,##0")&"   \u2022   "'
        '&TEXT(PartyDate,"dd mmm yyyy")&"  \u2014  tell no one!",'
        '"Name not found - check the spelling on \U0001F465 Participants."))'
        % (row + 1, C.ROW_FIRST, C.last_row(KEY), row + 1, C.ROW_FIRST,
           C.last_row(KEY)),
        out, "")
    bk.stats["formulas"] += 1

    chips = [
        ('="\U0001F385 Assigned: "&SUMPRODUCT(--($E$%d:$E$%d<>""))&" of "&'
         'COUNTA(%s!$B$%d:$B$%d)'
         % (C.ROW_FIRST, C.last_row(KEY), p, C.ROW_FIRST,
            C.last_row("participants")), "primary",
         "Assigned: %d of %d" % ((m.agg["assigned"], m.agg["participants"])
                                 if m else (0, 0)), 4),
        ('="\u2705 Clean pairs: "&COUNTIF($F$%d:$F$%d,"\u2705 OK")'
         % (C.ROW_FIRST, C.last_row(KEY)), "ok",
         "Clean pairs: %d" % (m.agg["participants"] if m else 0), 3),
        ('="\u26A0\ufe0f Rule hits: "&%s' % bk.kpi("violations"), "bad",
         "Rule hits: %d" % (m.agg["violations"] if m else 0), 3),
        ('="\U0001F512 Status: "&DrawStatus', "gold",
         "Status: %s" % (m.settings["status"] if m else C.DRAW_DRAFT), 4),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, row + 3, LAST_COL, tip=
                 "  \U0001F4A1  Re-draw: unlock the sheet (password "
                 "\u201cpremium\u201d), change the seed, re-protect.  "
                 "Overrides beat the auto-draw pair by pair.")
````

---
## `santa_tracker/sheets/rules.py`

*Exclusions & Rules tab (PREMIUM): house rules + custom pairs.* (97 lines)

````python
"""🚫 Exclusions & Rules - toggles plus custom no-pair rules."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "rules"
LAST_COL = "M"          # layout band; the table itself is A..D

COLUMNS = [
    ("n", "#", "idx", None),
    ("giver", "This person\u2026", "text", None),
    ("cannot", "\u2026must never draw", "text", None),
    ("reason", "Why", "wrap", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F6AB  Exclusions & Rules",
                 "Switch the house rules on or off and list custom no-pairs "
                 "- the draw validates itself against all of them.")
    bk.paint(KEY, 0, 0, C.ROW_FIRST + C.CAP[KEY] + 26, ci(LAST_COL),
             bk.S.canvas)

    lab = bk.S.f(**bk.S.base(font_size=10.5, bold=True, font_color=th.ink,
                             bg_color=th.card, align="left", indent=1,
                             valign="vcenter", border=1,
                             border_color=th.border))
    tog = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.primary,
                             bg_color=th.gold_soft, border=1,
                             border_color=th.border_strong, align="center",
                             valign="vcenter", locked=False))
    ws.merge_range(r(7), 1, r(7), ci(LAST_COL),
                   "  \U0001F39B\ufe0f  HOUSE RULES", bk.S.section_soft)
    ws.set_row(r(7), 22)
    toggles = [
        (8, "Couples / households cannot draw each other", "couple"),
        (9, "Same team / department cannot draw each other", "team"),
        (10, "No repeat of last year's pairing", "lastyear"),
    ]
    for row, text, key in toggles:
        ws.set_row(r(row), 22)
        ws.merge_range(r(row), 1, r(row), 2, "  " + text, lab)
        ws.write(r(row), 3, m.rules[key] if m else "On", tog)
    ws.merge_range(r(11), 1, r(11), ci(LAST_COL),
                   "  \u26D4  (Self-draws are always impossible - the draw "
                   "is a closed cycle.)", bk.S.sheet_sub)

    head = 13
    ws.merge_range(r(head), 1, r(head), ci(LAST_COL),
                   "  \u270D\ufe0f  CUSTOM NO-PAIR RULES", bk.S.section_soft)
    ws.set_row(r(head), 22)
    # shift the table down: header row 14, data from 15
    K.header_row(bk, KEY, COLUMNS, row=head + 1, height=24)
    first = head + 2
    last = first + C.CAP[KEY] - 1
    from .common import data_rows
    ws = bk.ws(KEY)
    for i in range(C.CAP[KEY]):
        ws.set_row(r(first + i), 20)
    if m:
        for i, (a, b) in enumerate(m.pairs):
            K.write_row(bk, KEY, COLUMNS, first + i,
                        {"n": i + 1, "giver": a, "cannot": b,
                         "reason": m.pair_reason[(a, b)]})
    for i in range(len(m.pairs) if m else 0, C.CAP[KEY]):
        K.write_row(bk, KEY, COLUMNS, first + i,
                    {"n": i + 1, "giver": "", "cannot": "", "reason": ""})
    K.list_dv(bk, KEY, "giver", "participants", first=first, last=last)
    K.list_dv(bk, KEY, "cannot", "participants", first=first, last=last)

    row = last + 2
    chips = [
        ('="\U0001F6AB Rules armed: "&%s' % bk.kpi("rules_count"),
         "primary", "Rules armed: %d" % (m.agg["rules_count"] if m else 0),
         4),
        ('="\u26A0\ufe0f Draw violations: "&%s' % bk.kpi("violations"),
         "bad", "Draw violations: %d" % (m.agg["violations"] if m else 0),
         4),
        ('="\u270D\ufe0f Custom pairs: "&SUMPRODUCT(--($B$%d:$B$%d<>""))'
         % (first, last), "gold",
         "Custom pairs: %d" % (len(m.pairs) if m else 0), 4),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.note_block(bk, KEY, row + 5, "B", "D", [
        "Every rule you arm here is checked live on the \U0001F385 Secret "
        "Santa Draw tab - any offending pair shows exactly which rule it "
        "breaks (Self / Couple / Team / LastYear / Custom).",
        "Fix a flagged pair with a manual override on the Draw tab, or "
        "re-draw with a new seed until the board is clean.",
    ], title="\U0001F4D0  HOW VALIDATION WORKS")
    K.footer_nav(bk, KEY, row + 9, LAST_COL)
````

---
## `santa_tracker/sheets/budget.py`

*Budget Tracker tab.* (112 lines)

````python
"""💰 Budget Tracker - min/max rules, actual spend, receipts."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "budget"
LAST_COL = "I"

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Gift for (recipient)", "text", None),
    ("min", "Min", "calc_money", None),
    ("max", "Max", "calc_money", None),
    ("spent", "Actual spent", "money", None),
    ("flag", "Budget check", "calc_wrap", None),
    ("receipt", "Receipt?", "tick", None),
    ("ref", "Receipt / order ref", "center", None),
    ("notes", "Notes", "wrap", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F4B0  Budget Tracker",
                 "One row per giver: what they spent on their Secret Santa "
                 "gift, checked against the party's min and max.")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    flagf = bk.S.f(**bk.S.base(font_size=9.5, font_color=th.ink,
                               bg_color=th.alt, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border, text_wrap=True))
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        values = {
            "n": i + 1,
            "name": '=IF(%s!$C$%d="","",%s!$C$%d)'
                    % (bk.q("draw"), row, bk.q("draw"), row),
            "min": "=BudgetMin",
            "max": "=BudgetMax",
            "spent": "",
            "flag": '=IF($E{r}="","",IF($E{r}<$C{r},"%s",IF($E{r}>$D{r},"%s",'
                    '"%s")))' % (C.BF_UNDER, C.BF_OVER, C.BF_OK),
            "receipt": "",
            "ref": "",
            "notes": "",
        }
        cached = {}
        if m and i < len(m.people):
            cached = {"name": m.assign[i], "min": m.settings["bmin"],
                      "max": m.settings["bmax"],
                      "flag": ("" if not m.spent[i] else
                               (C.BF_UNDER if m.spent[i] < m.settings["bmin"]
                                else C.BF_OVER if m.spent[i]
                                > m.settings["bmax"] else C.BF_OK))}
            values["spent"] = m.spent[i] or ""
            values["receipt"] = m.receipts[i]
            values["ref"] = m.refs[i]
        elif m:
            cached = {"name": "", "min": m.settings["bmin"],
                      "max": m.settings["bmax"], "flag": ""}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        ws.write_formula(r(row), ci("F"),
                         values["flag"].format(r=row), flagf,
                         cached.get("flag", ""))
        bk.stats["formulas"] += 1

    K.money_dv(bk, KEY, ("spent",))
    K.tick_dv(bk, KEY, ("receipt",))
    K.tick_cf(bk, KEY, ("receipt",))
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_OVER),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_UNDER),
        "format": bk.S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_OK),
        "format": bk.S.cf(bg=th.ok_soft, fg=th.ok)})

    tot = C.last_row(KEY) + 1
    K.totals_row(bk, KEY, tot, {
        "spent": ("=SUM(E%d:E%d)" % (C.ROW_FIRST, C.last_row(KEY)),
                  "#,##0.00", m.agg["spent"] if m else 0)},
        first_col="B", last_col=LAST_COL)

    sp = "$E$%d:$E$%d" % (C.ROW_FIRST, C.last_row(KEY))
    fl = "$F$%d:$F$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F4B8 Total spent: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % sp, "primary",
         "Total spent: %s" % (m.money(m.agg["spent"]) if m else "$0.00"), 4),
        ('="\U0001F4CA Average gift: "&Currency&TEXT(%s,"#,##0.00")'
         % bk.kpi("avg_gift"), "info",
         "Average gift: %s" % (m.money(m.agg["avg_gift"]) if m else "$0.00"),
         4),
        ('="\U0001F6A8 Over budget: "&COUNTIF(%s,"%s")' % (fl, C.BF_OVER),
         "bad", "Over budget: %d" % (m.agg["over_budget"] if m else 0), 3),
        ('="\U0001F9FE Receipts filed: "&COUNTIF($G$%d:$G$%d,"%s")'
         % (C.ROW_FIRST, C.last_row(KEY), C.TICK), "ok",
         "Receipts filed: %d" % (sum(1 for x in (m.receipts if m else [])
                                     if x),), 3),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, tot + 2, LAST_COL)
````

---
## `santa_tracker/sheets/wishlists.py`

*Wishlists tab (PREMIUM).* (65 lines)

````python
"""🎁 Wishlists - ideas per participant, claimable by their Santa."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "wishlists"
LAST_COL = "G"

COLUMNS = [
    ("n", "#", "idx", None),
    ("who", "Participant", "text", None),
    ("item", "Wish", "wrap", None),
    ("priority", "Priority", "center", None),
    ("link", "Link / shop", "link", None),
    ("claimed", "Claimed", "tick", None),
    ("notes", "Notes", "wrap", None),
]


def build(bk):
    th = bk.th
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F381  Wishlists",
                 "Ideas each participant dropped - tick Claimed once their "
                 "Santa commits (no names shown, no spoilers).")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    if m:
        for i, w in enumerate(m.wishes):
            K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                        {"n": i + 1, "who": w[0], "item": w[1],
                         "priority": w[2], "link": w[3], "claimed": w[4],
                         "notes": w[5]})
    for i in range(len(m.wishes) if m else 0, C.CAP[KEY]):
        K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                    {"n": i + 1, "who": "", "item": "", "priority": "",
                     "link": "", "claimed": "", "notes": ""})
    K.list_dv(bk, KEY, "who", "participants")
    K.fixed_dv(bk, KEY, "priority", "Priorities")
    K.tick_dv(bk, KEY, ("claimed",))
    K.tick_cf(bk, KEY, ("claimed",))
    K.status_cf(bk, KEY, "priority", {
        "Must-love": (th.accent_soft, th.accent),
        "Nice to have": (th.info_soft, th.info),
        "Just an idea": (th.card, th.muted)})

    cl = "$F$%d:$F$%d" % (C.ROW_FIRST, C.last_row(KEY))
    pr = "$D$%d:$D$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F381 Wishes logged: "&SUMPRODUCT(--($C$%d:$C$%d<>""))'
         % (C.ROW_FIRST, C.last_row(KEY)), "primary",
         "Wishes logged: %d" % (len(m.wishes) if m else 0), 4),
        ('="\u2705 Claimed: "&COUNTIF(%s,"%s")' % (cl, C.TICK), "ok",
         "Claimed: %d" % (sum(1 for w in (m.wishes if m else []) if w[4]),),
         4),
        ('="\u2764\ufe0f Must-love open: "&SUMPRODUCT((%s="Must-love")*'
         '(%s<>"%s"))' % (pr, cl, C.TICK), "bad",
         "Must-love open: %d" % (sum(1 for w in (m.wishes if m else [])
                                     if w[2] == "Must-love" and not w[4]),),
         4),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, C.last_row(KEY) + 2, LAST_COL)
````

---
## `santa_tracker/sheets/we.py`

*White Elephant tab (PREMIUM): seats, gifts, holders, statuses.* (155 lines)

````python
"""🎲 White Elephant - seat order, gifts, steals, locks and holders."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "we"
LAST_COL = "L"

COLUMNS = [
    ("n", "#", "idx", None),
    ("order", "Seat", "calc_num", None),
    ("player", "Player", "text", None),
    ("giftnum", "Gift #", "calc_num", None),
    ("desc", "Gift description", "wrap", None),
    ("value", "Gift value", "money", None),
    ("steals", "Steals", "calc_num", None),
    ("maxsteals", "Max", "calc_num", None),
    ("status", "Gift status", "calc_c", None),
    ("holder", "Current holder", "calc_c", None),
    ("stolenfrom", "Last stolen from", "calc_c", None),
    ("final", "Final?", "calc_tick", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F3B2  White Elephant",
                 "Seats and gift numbers shuffle from the seed; holders, "
                 "steal counts and locks follow \U0001F504 Game History.")
    K.table_frame(bk, KEY, COLUMNS, height=22)
    ws.set_column(ci("M"), ci("N"), 10, None, {"hidden": True})

    h = bk.q("history")
    hgift = "%s!$E$%d:$E$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hturn = "%s!$G$%d:$G$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hplayer = "%s!$C$%d:$C$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    haction = "%s!$D$%d:$D$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hfrom = "%s!$F$%d:$F$%d" % (h, C.ROW_FIRST, C.last_row("history"))

    statf = bk.S.f(**bk.S.base(font_size=10, bold=True, font_color=th.ink,
                               bg_color=th.alt, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border))
    keyf = bk.S.f(**bk.S.base(font_size=9, font_color=th.muted,
                              bg_color=th.alt, align="right",
                              valign="vcenter", num_format="#,##0"))
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        lastt = 'SUMPRODUCT(MAX((%s=$D%d)*%s))' % (hgift, row, hturn)
        lastidx = ('SUMPRODUCT((%s=$D%d)*(%s=%s)*(ROW(%s)-%d))'
                   % (hgift, row, hturn, lastt, hgift,
                      C.ROW_FIRST - 1))
        values = {
            "n": i + 1,
            "order": '=IF($C%d="","",1+SUMPRODUCT(--($M$%d:$M$%d>$M%d)))'
                     % (row, C.ROW_FIRST, C.last_row(KEY), row),
            "player": "",
            "giftnum": '=IF($C%d="","",1+SUMPRODUCT(--($N$%d:$N$%d>$N%d)))'
                       % (row, C.ROW_FIRST, C.last_row(KEY), row),
            "desc": "",
            "value": "",
            "steals": '=IF($D%d="","",COUNTIFS(%s,$D%d,%s,"Steal"))'
                      % (row, hgift, row, haction),
            "maxsteals": '=IF($C%d="","",MaxSteals)' % row,
            "status": '=IF($D%d="","",IF($G%d>=$H%d,"%s",IF(COUNTIFS(%s,'
                      '$D%d)=0,"%s",IF(INDEX(%s,%s)="Steal","%s","%s"))))'
                      % (row, row, row, C.GS_FINAL, hgift, row, C.GS_AVAIL,
                         haction, lastidx, C.GS_STOLEN, C.GS_HELD),
            "holder": '=IF($D%d="","",IF(COUNTIFS(%s,$D%d)=0,"",INDEX('
                      '%s,%s)))' % (row, hgift, row, hplayer, lastidx),
            "stolenfrom": '=IF($I%d="%s",IFERROR(INDEX(%s,%s),""),"")'
                          % (row, C.GS_STOLEN, hfrom, lastidx),
            "final": '=IF($C%d="","",IF(COUNTA($J$%d:$J$%d)=COUNTA($C$%d:'
                     '$C$%d),IFERROR(INDEX($D$%d:$D$%d,MATCH($C%d,$J$%d:$J$%d,'
                     '0)),""),"-"))'
                     % (row, C.ROW_FIRST, C.last_row(KEY), C.ROW_FIRST,
                        C.last_row(KEY), C.ROW_FIRST, C.last_row(KEY), row,
                        C.ROW_FIRST, C.last_row(KEY)),
            # hidden shuffle keys (columns M/N) - the seat and gift-number
            # ranks above are computed FROM these, matching the demo's
            # (seed*7919*(i+2)+i*104729) and (seed*6967*(i+5)+i*1299709)
            "key1": '=IF($C%d="",0,MOD(WESeed*7919*(ROW()-6)+(ROW()-8)*'
                    '104729,999983)*100+(ROW()-8))' % row,
            "key2": '=IF($C%d="",0,MOD(WESeed*6967*(ROW()-3)+(ROW()-8)*'
                    '1299709,999983)*100+(ROW()-8))' % row,
        }
        cached = {}
        if m and i < len(m.we):
            w = m.we[i]
            cached = {"order": w["seat"], "giftnum": w["giftnum"],
                      "steals": w["steals"],
                      "maxsteals": m.settings["steals"],
                      "status": w["status"], "holder": w["holder"],
                      "stolenfrom": w["stolenfrom"], "final": "",
                      "key1": m.we_k1[i], "key2": m.we_k2[i]}
            values["player"] = w["player"]
            values["desc"] = w["desc"]
            values["value"] = w["value"]
        elif m:
            cached = {"order": "", "giftnum": "", "steals": "",
                      "maxsteals": "", "status": "", "holder": "",
                      "stolenfrom": "", "final": "", "key1": 0, "key2": 0}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        ws.write_formula(r(row), ci("I"), values["status"], statf,
                         cached.get("status", ""))
        bk.stats["formulas"] += 1
        # the hidden helper columns are not part of COLUMNS - write them
        # directly so the seat / gift-number ranks have something to rank
        ws.write_formula(r(row), ci("M"), values["key1"], keyf,
                         cached.get("key1", 0))
        ws.write_formula(r(row), ci("N"), values["key2"], keyf,
                         cached.get("key2", 0))
        bk.stats["formulas"] += 2

    K.list_dv(bk, KEY, "player", "participants")
    K.money_dv(bk, KEY, ("value",))
    K.status_cf(bk, KEY, "status", {
        C.GS_AVAIL: (th.card, th.muted),
        C.GS_HELD: (th.ok_soft, th.ok),
        C.GS_STOLEN: (th.warn_soft, th.warn),
        C.GS_FINAL: (th.bad_soft, th.bad)})
    # highlight the seat whose turn it is
    bk.cond(KEY, C.ROW_FIRST, 1, C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=AND($C%d<>"",$B%d=%s)'
                    % (C.ROW_FIRST, C.ROW_FIRST, bk.kpi("current_turn")),
        "format": bk.S.cf(bg=th.gold_soft, fg=th.primary, bold=True)})

    now_seat = m.agg["current_turn"] if m else 0
    now_player = (m.we_by_seat[now_seat]["player"]
                  if m and now_seat in m.we_by_seat else "")
    chips = [
        ('="\U0001F3B2 Players: "&COUNTA($C$%d:$C$%d)'
         % (C.ROW_FIRST, C.last_row(KEY)), "primary",
         "Players: %d" % (m.agg["we_players"] if m else 0), 3),
        ('="\U0001F381 In play: "&%s' % bk.kpi("gifts_in_play"), "ok",
         "In play: %d" % (m.agg["gifts_in_play"] if m else 0), 3),
        ('="\U0001F512 Locked: "&%s' % bk.kpi("locked_gifts"), "bad",
         "Locked: %d" % (m.agg["locked_gifts"] if m else 0), 3),
        ('="\U0001F449 Now: seat "&%s&" ("&IFERROR(INDEX($C$%d:$C$%d,MATCH('
         '%s,$B$%d:$B$%d,0)),"game over")&")"'
         % (bk.kpi("current_turn"), C.ROW_FIRST, C.last_row(KEY),
            bk.kpi("current_turn"), C.ROW_FIRST, C.last_row(KEY)), "gold",
         "Now: seat %d (%s)" % (now_seat, now_player), 5),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, C.last_row(KEY) + 2, LAST_COL, tip=
                 "  \U0001F4A1  House rule: one turn per seat per round; if "
                 "your gift was stolen, pick again on your next round turn. "
                 " A gift locks at max steals.")
````

---
## `santa_tracker/sheets/history.py`

*Game History tab (PREMIUM): turn log that drives the board.* (84 lines)

````python
"""🔄 Game History - the white elephant turn log that drives everything."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "history"
LAST_COL = "F"

COLUMNS = [
    ("n", "#", "idx", None),
    ("turn", "Turn", "num", None),
    ("player", "Player", "text", None),
    ("action", "Action", "center", None),
    ("gift", "Gift #", "num", None),
    ("stolenfrom", "Stolen from", "center", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F504  Game History",
                 "Log every Pick, Steal and Pass in order - the White "
                 "Elephant tab reads this log live.")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    if m:
        for i, (turn, pl, action, gnum, frm) in enumerate(m.history):
            K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                        {"n": i + 1, "turn": turn, "player": pl,
                         "action": action, "gift": gnum,
                         "stolenfrom": frm})
    for i in range(len(m.history) if m else 0, C.CAP[KEY]):
        K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                    {"n": i + 1, "turn": "", "player": "", "action": "",
                     "gift": "", "stolenfrom": ""})
    ws.set_column(ci("G"), ci("G"), 8, None, {"hidden": True})
    hf = bk.S.f(**bk.S.base(font_size=9, font_color=bk.th.muted,
                            align="right", valign="vcenter",
                            num_format="#,##0"))
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        ws.write_formula(r(row), ci("G"), '=IF($B%d="",0,$B%d)' % (row, row),
                         hf, (m.history[i][0] if m and i < len(m.history)
                              else 0))
        bk.stats["formulas"] += 1
    K.whole_dv(bk, KEY, ("turn",), minimum=1, maximum=200)
    K.list_dv(bk, KEY, "player", "participants")
    K.fixed_dv(bk, KEY, "action", "Actions")
    K.list_dv(bk, KEY, "gift", "giftnums")
    K.list_dv(bk, KEY, "stolenfrom", "participants")
    K.status_cf(bk, KEY, "action", {
        "Pick": (th.ok_soft, th.ok),
        "Steal": (th.bad_soft, th.bad),
        "Pass": (th.card, th.muted)})

    ac = "$D$%d:$D$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F504 Turns logged: "&COUNT($B$%d:$B$%d)'
         % (C.ROW_FIRST, C.last_row(KEY)), "primary",
         "Turns logged: %d" % (m.agg["turns_done"] if m else 0), 4),
        ('="\U0001F932 Steals: "&COUNTIF(%s,"Steal")' % ac, "bad",
         "Steals: %d" % (sum(1 for h in (m.history if m else [])
                             if h[2] == "Steal"),), 4),
        ('="\U0001F381 Picks: "&COUNTIF(%s,"Pick")' % ac, "ok",
         "Picks: %d" % (sum(1 for h in (m.history if m else [])
                            if h[2] == "Pick"),), 3),
        ('="\u23ED\ufe0f Passes: "&COUNTIF(%s,"Pass")' % ac, "info",
         "Passes: %d" % (sum(1 for h in (m.history if m else [])
                             if h[2] == "Pass"),), 3),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.note_block(bk, KEY, C.last_row(KEY) + 3, "B", "F", [
        "Turn numbers run 1, 2, 3\u2026 in seat order each round; extra "
        "rounds continue the count.",
        "On a Steal row, always say who the gift was stolen from - the "
        "\u201clast stolen from\u201d column on the game tab reads it.",
        "A gift reaches \U0001F512 Final automatically once its steal count "
        "hits the max set on \u2699\ufe0f Settings.",
    ], title="\U0001F4D6  LOGGING THE GAME")
    K.footer_nav(bk, KEY, C.last_row(KEY) + 8, LAST_COL)
````

---
## `santa_tracker/sheets/cards.py`

*Santa Cards tab (PREMIUM): fold-and-cut giver cards.* (100 lines)

````python
"""🎟️ Santa Cards - printable cut-out cards, one per participant."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "cards"
LAST_COL = "I"

# 24 participants = 24 card slots (2 per row, 12 rows)
N_CARDS = C.CAP["participants"]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F39F\ufe0f  Santa Cards",
                 "Print this tab, cut along the cards, hand one to each "
                 "guest - their recipient stays secret until then.")
    last_card_row = 8 + ((N_CARDS + 1) // 2 - 1) * 8
    bk.paint(KEY, 0, 0, last_card_row + 8, ci(LAST_COL), bk.S.canvas)

    p = bk.q("participants")
    d = bk.q("draw")
    names = "%s!$B$%d:$B$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    finals = "%s!$E$%d:$E$%d" % (d, C.ROW_FIRST, C.last_row("draw"))

    frame = bk.S.f(**bk.S.base(bg_color=th.card, border=1,
                               border_color=th.border_strong))
    head = bk.S.f(**bk.S.base(font_size=10, bold=True, font_color=th.white,
                              bg_color=th.primary, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border_strong))
    giver = bk.S.f(**bk.S.base(font_size=15, bold=True,
                               font_color=th.primary, bg_color=th.card,
                               align="center", valign="vcenter", border=1,
                               border_color=th.border_strong))
    lab = bk.S.f(**bk.S.base(font_size=9, italic=True, font_color=th.muted,
                             bg_color=th.card, align="center",
                             valign="vcenter", border=1,
                             border_color=th.border_strong))
    rec = bk.S.f(**bk.S.base(font_size=14, bold=True, font_color=th.accent,
                             bg_color=th.accent_soft, align="center",
                             valign="vcenter", border=1,
                             border_color=th.border_strong))
    meta = bk.S.f(**bk.S.base(font_size=9, font_color=th.ink,
                              bg_color=th.card, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border_strong))

    for k in range(1, N_CARDS + 1):
        col0 = 1 if k % 2 == 1 else 6
        row0 = 8 + ((k - 1) // 2) * 8
        ws.set_row(r(row0), 20)
        ws.set_row(r(row0 + 1), 26)
        ws.set_row(r(row0 + 2), 14)
        ws.set_row(r(row0 + 3), 24)
        ws.set_row(r(row0 + 4), 14)
        ws.set_row(r(row0 + 5), 14)
        ws.merge_range(r(row0), col0, r(row0), col0 + 3,
                       "  \U0001F385  SECRET SANTA CARD  \u2022  %d" % k,
                       head)
        ws.merge_range(r(row0 + 1), col0, r(row0 + 1), col0 + 3, "", giver)
        ws.write_formula(r(row0 + 1), col0,
                         '=IFERROR(INDEX(%s,%d),"")' % (names, k), giver,
                         (m.people[k - 1]["name"]
                          if m and k <= len(m.people) else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 2), col0, r(row0 + 2), col0 + 3,
                       "you are secretly drawing\u2026", lab)
        ws.merge_range(r(row0 + 3), col0, r(row0 + 3), col0 + 3, "", rec)
        ws.write_formula(r(row0 + 3), col0,
                         '=IFERROR(INDEX(%s,%d),"")' % (finals, k), rec,
                         (m.assign[k - 1] if m and k <= len(m.people)
                          else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 4), col0, r(row0 + 4), col0 + 3, "", meta)
        ws.write_formula(
            r(row0 + 4), col0,
            '=IF(COUNTA(%s)=0,"","budget "&Currency&TEXT('
            'BudgetMin,"#,##0")&"\u2013"&Currency&TEXT(BudgetMax,'
            '"#,##0")&"   \u2022   bring it by "&TEXT(PartyDate,'
            '"dd mmm"))' % names, meta,
            ("budget $20\u2013$35   \u2022   bring it by 19 Dec"
             if m else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 5), col0, r(row0 + 5), col0 + 3, "", meta)
        ws.write_formula(
            r(row0 + 5), col0,
            '=IF(COUNTA(%s)=0,"",PartyName&"  \u2022  "&PartyLocation)'
            % names, meta,
            ("%s  \u2022  %s" % (m.settings["party"],
                                  m.settings["location"]) if m else ""))
        bk.stats["formulas"] += 1
    K.footer_nav(bk, KEY, last_card_row + 7, LAST_COL, landscape=True, tip=
                 "  \u2702\ufe0f  Print landscape, cut along the borders, "
                 "fold once - secret inside.")
````

---
## `santa_tracker/sheets/guide.py`

*Start Here guide tab with watercolour banner cover.* (274 lines)

````python
"""📖 Start Here - quick start, tab tour, tips and the friendly rules."""

import os

from ..book import r, ci

LAST_COL = "J"


def build(bk):
    key = "guide"
    ws = bk.ws(key)
    S, th = bk.S, bk.th

    bk.widths(key, {"A": 2.2, "B": 4, "C": 15, "D": 15, "E": 15, "F": 15,
                    "G": 15, "H": 15, "I": 15, "J": 15})
    bk.paint(key, 0, 0, 90, ci(LAST_COL), S.canvas)

    body = S.f(**S.base(font_size=10.5, bg_color=th.bg, align="left",
                        valign="vcenter", text_wrap=True))
    body_soft = S.f(**S.base(font_size=10.5, bg_color=th.card, align="left",
                             valign="vcenter", text_wrap=True,
                             border=1, border_color=th.border))
    badge = S.f(**S.base(bold=True, font_size=12, font_color=th.white,
                         bg_color=th.accent, align="center", valign="vcenter"))
    badge2 = S.f(**S.base(bold=True, font_size=12, font_color=th.white,
                          bg_color=th.info, align="center", valign="vcenter"))
    step_title = S.f(**S.base(bold=True, font_size=11.5,
                              font_color=th.primary, bg_color=th.bg,
                              align="left", valign="vcenter", indent=1))
    mark = S.f(**S.base(font_size=10, font_color=th.muted, bg_color=th.bg,
                        align="center", valign="vcenter"))

    def sec(row, emoji, text):
        ws.set_row(r(row), 24)
        ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                       "  %s  %s" % (emoji, text), S.section)

    # ------------------------------------------------------------------
    # cover banner + overlaid title (plain title band when no artwork)
    # ------------------------------------------------------------------
    image = _banner_path(bk)
    row = 1
    ws.set_row(r(row), 7)
    row += 1
    if image:
        w, h = _png_size(image)
        scale = 860.0 / float(w)
        span = int(h * scale / 20.0) + 1
        cover = S.f(**S.base(bg_color=th.cover_bg))
        for i in range(span):
            ws.set_row(r(row + i), 20)
            for col in range(1, ci(LAST_COL) + 1):
                ws.write(r(row + i), col, "", cover)
        ws.insert_image(r(row), 1, image,
                        {"x_scale": scale, "y_scale": scale,
                         "object_position": 1})
        t_row = row + max(1, span // 2 - 1)
        ws.merge_range(r(t_row), ci("C"), r(t_row), ci("G"),
                       "\U0001F4D6  START HERE",
                       S.f(**S.base(font_name=th.title_font, font_size=26,
                                    bold=True, font_color=th.primary,
                                    bg_color=th.cover_bg, align="center",
                                    valign="vcenter")))
        ws.merge_range(r(t_row + 1), ci("C"), r(t_row + 1), ci("G"),
                       "  your 5-minute tour of the Secret Santa & White "
                       "Elephant Party Tracker",
                       S.f(**S.base(font_size=11.5, italic=True,
                                    font_color=th.muted,
                                    bg_color=th.cover_bg, align="center",
                                    valign="vcenter")))
        row += span + 1
        ws.set_row(r(row), 18)
        ws.merge_range(r(row), ci(LAST_COL) - 2, r(row), ci(LAST_COL), "",
                       S.home_link)
        ws.write_url(r(row), ci(LAST_COL) - 2,
                     "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                     "\U0001F3E0  Back to Dashboard")
        row += 2
    else:
        ws.set_row(r(row), 32)
        ws.set_row(r(row + 1), 18)
        ws.merge_range(r(row), 1, r(row), ci(LAST_COL) - 3,
                       "\U0001F4D6  Start Here \u2014 your 5-minute setup",
                       S.sheet_title)
        ws.merge_range(r(row + 1), 1, r(row + 1), ci(LAST_COL) - 3,
                       "  Everything is wired together: log a turn once and "
                       "the game board, budgets and dashboard follow.",
                       S.sheet_sub)
        ws.merge_range(r(row + 1), ci(LAST_COL) - 2, r(row + 1), ci(LAST_COL),
                       "", S.home_link)
        ws.write_url(r(row + 1), ci(LAST_COL) - 2,
                     "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                     "\U0001F3E0  Back to Dashboard")
        row += 3
    # ------------------------------------------------------------------
    sec(row, "\U0001F680", "QUICK START \u2014 FIVE STEPS TO LIVE")
    row += 1
    steps = [
        ("1", "Open \u2699\ufe0f Settings & Instructions",
         "Type the party name, date, location, host, currency, gift budget "
         "min/max, max steals and the two seeds.  Every tab reads these."),
        ("2", "List your guests on \U0001F465 Participants",
         "Names plus team, household/couple, RSVP, dietary needs and who "
         "they drew last year - the exclusion engine feeds off this."),
        ("3", "Draw on \U0001F385 Secret Santa Draw",
         "The draw is a closed cycle: nobody can ever pick themselves.  "
         "Change the seed to shuffle, override any pair by hand, then lock "
         "the draw with the status dropdown."),
        ("4", "Arm your rules on \U0001F6AB Exclusions & Rules",
         "Couples, same-team and last-year repeats toggle on/off; custom "
         "no-pairs go in the table.  The draw flags every breach live."),
        ("5", "Run the party",
         "\U0001F4B0 Budget Tracker watches every spend, \U0001F381 "
         "Wishlists keeps ideas claimable, and \U0001F3B2 White Elephant "
         "plus \U0001F504 Game History run the steal-fest turn by turn."),
    ]
    for num, title, text in steps:
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), 1, num, badge)
        ws.merge_range(r(row), 2, r(row), 3, title, step_title)
        ws.merge_range(r(row), 4, r(row + 1), ci(LAST_COL), text, body)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F5FA\uFE0F", "THE TAB TOUR")
    row += 1
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  Premium edition: every tab below.  Basic edition: the "
                   "tabs marked \u25CF only.",
                   S.f(**S.base(font_size=10, italic=True,
                                font_color=th.muted,
                                bg_color=th.bg, align="left",
                                valign="vcenter", indent=1)))
    row += 1
    tour = [
        ("\u25CF", "\U0001F3E0 Dashboard", "Participants, spend, readiness, "
         "game state, alerts and three live charts."),
        ("\u25CF", "\U0001F465 Participants", "Guest list with RSVP, team, "
         "household, dietary needs and gift status."),
        ("\u25CF", "\U0001F385 Secret Santa Draw", "Auto draw, overrides, "
         "rules check and the private recipient lookup."),
        ("\u25CF", "\U0001F4B0 Budget Tracker", "Min/max rules, actual "
         "spend, under/over flags and receipt tracking."),
        ("\u25CF", "\U0001F3B2 White Elephant", "Seats, gift numbers, steal "
         "counts, locks, holders and final gifts."),
        ("\u25CF", "\U0001F4D6 Start Here", "This page."),
        ("\u25CB", "\U0001F6AB Exclusions & Rules", "House-rule toggles and "
         "custom no-pair list."),
        ("\u25CB", "\U0001F381 Wishlists", "Per-guest ideas with priorities "
         "and anonymous claiming."),
        ("\u25CB", "\U0001F504 Game History", "The turn log: every Pick, "
         "Steal and Pass in order."),
        ("\u25CB", "\U0001F39F\ufe0f Santa Cards", "Printable cut-out "
         "cards so each guest learns their recipient privately."),
    ]
    for mark_txt, tab, blurb in tour:
        ws.set_row(r(row), 18)
        ws.merge_range(r(row), 2, r(row), 3, mark_txt + "  " + tab, step_title)
        ws.merge_range(r(row), 4, r(row), ci(LAST_COL), blurb, body)
        row += 1
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F4A1", "TEN TIPS FROM PARTY ANIMALS")
    row += 1
    tips = [
        "Set the gift budget min AND max - too-cheap gifts hurt feelings "
        "just as much as too-pricey ones.",
        "Collect wishlists before the draw; three wishes each is plenty.",
        "Households in the same couple get the same Household value - the "
        "couple rule then keeps them apart automatically.",
        "Fill in \u201cgave to last year\u201d and arm the repeat rule: "
        "two years running the same pair feels lazy.",
        "Print the Santa Cards, fold them, and let guests pick a card at "
        "random at the door - zero spoilers.",
        "White Elephant: cap steals at 2.  Three or more and the game "
        "stalls; one and nobody gets naughty.",
        "Log steals on Game History as they happen (phone in Sheets) and "
        "the board stays honest without a whiteboard.",
        "The private lookup shows one recipient at a time - perfect for "
        "passing the laptop round without spoilers.",
        "Formula cells are protected with the password \u201cpremium\u201d; "
        "unlock only when you need to change a seed.",
        "Reuse the file every year: bump the party year and date, clear the "
        "logs, keep your lists.",
    ]
    for i, tip in enumerate(tips, 1):
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), 1, str(i), badge2)
        ws.merge_range(r(row), 2, r(row + 1), ci(LAST_COL), tip, body)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F512", "THE GENTLE RULES")
    row += 1
    rules = [
        "Cream-filled cells are yours to type in.  White cells are formulas "
        "\u2014 leave them alone and they will keep working for you.",
        "Sheets are protected to stop accidental edits.  Review \u2192 "
        "Unprotect Sheet if you ever need to restructure something.",
        "Add rows by copying an existing data row and inserting below it "
        "\u2014 the formulas, dropdowns and colours travel with the copy.",
        "This file opens in Excel 2016+ and in Google Sheets (upload to "
        "Drive \u2192 open with Sheets).  A few chart styles look slightly "
        "different in Sheets; every number still calculates.",
        "The EXAMPLE edition is loaded with a fictional office party so "
        "you can see it working.  The blank edition is the one you keep.",
    ]
    for rule in rules:
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), ci(LAST_COL),
                       "\u2022  " + rule, body_soft)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F91D", "SUPPORT")
    row += 1
    ws.set_row(r(row), 16)
    ws.set_row(r(row + 1), 16)
    ws.merge_range(r(row), 1, r(row + 1), ci(LAST_COL),
                   "  Thank you for buying this template \u2014 it was "
                   "built by Novality Store, people who have hosted one "
                   "too many white-elephant stampedes and know what a "
                   "spreadsheet owes you in December.  Message the shop "
                   "any time and a human will help quickly.", body_soft)
    row += 3

    # ------------------------------------------------------------------
    # footer + nav
    # ------------------------------------------------------------------
    ws.set_row(r(row), 30)
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F4AC  Questions about this file?  Your Etsy "
                   "shop message reaches a human, usually the same day.",
                   S.f(**S.base(font_size=10, italic=True, font_color=th.ink,
                                bg_color=th.gold_soft, align="left",
                                valign="vcenter", indent=1)))
    nav = row + 2
    ws.set_row(r(nav), 24)
    bk.nav_row(key, nav, max_col=LAST_COL)
    bk.page(key, LAST_COL, nav + 1, landscape=False, zoom=90)


# ---------------------------------------------------------------------------
def _banner_path(bk):
    """Watercolour cover art for the Start Here tab, if it exists."""
    if not bk.images:
        return None
    here = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(here, "assets", "banner_%s%s" % (bk.th.key, ext))
        if os.path.exists(path):
            return path
    return None


def _png_size(path):
    """Pixel size of a PNG or JPEG, without needing Pillow."""
    with open(path, "rb") as fh:
        data = fh.read(32)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        import struct
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    return 1600, 300
````

---
## `tools/verify_santa.py`

*QA: structural audit - sheet refs, modern functions, hidden writes.* (178 lines)

````python
#!/usr/bin/env python3
"""
Audit a generated .xlsx without needing Excel (santa edition).

Checks performed
    1. the workbook opens (openpyxl) and every expected tab exists / is hidden
    2. every sheet-qualified reference in every formula points at a real sheet
    3. no modern-only function leaked in without the ``_xlfn.`` prefix older
       Excel versions need
    4. no cell contains the literal strings "None", "#REF!" or "nan"
    5. nothing was written *under* a merged range (Excel only ever shows the
       top-left cell of a merge, so such writes would be invisible)

Usage
    python3 tools/verify_santa.py products/Secret_Santa_*.xlsx
"""

import glob
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

import openpyxl
from openpyxl.utils import (column_index_from_string, get_column_letter,
                            range_boundaries)

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Functions that did not exist in Excel 2007 and therefore must be written as
# _xlfn.NAME by a file generator (XlsxWriter does this automatically for the
# names it knows about).
MODERN = {
    "TEXTJOIN", "CONCAT", "IFS", "SWITCH", "MAXIFS", "MINIFS", "XLOOKUP",
    "XMATCH", "FILTER", "SORT", "SORTBY", "UNIQUE", "SEQUENCE", "LET",
    "LAMBDA", "RANDARRAY", "IMAGE", "TEXTSPLIT", "VSTACK", "HSTACK", "TOCOL",
    "TOROW", "TAKE", "DROP", "CHOOSEROWS", "CHOOSECOLS", "WRAPROWS",
    "WRAPCOLS", "GROUPBY", "PIVOTBY", "REGEXTEST", "REGEXEXTRACT",
    "REGEXREPLACE",
}

FUNC_RE = re.compile(r"(?<![A-Za-z0-9_.])([A-Z][A-Z0-9_.]*)\s*\(")
SHEET_REF_RE = re.compile(r"(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_.]*))!")


def sheet_xml(path):
    """{sheet name: worksheet xml} for low level checks."""
    zf = zipfile.ZipFile(path)
    wbxml = zf.read("xl/workbook.xml").decode()
    rels = dict(re.findall(
        r'Id="(rId\d+)"[^>]*Target="([^"]*worksheets/sheet\d+\.xml)"',
        zf.read("xl/_rels/workbook.xml.rels").decode()))
    out = {}
    for name, rid in re.findall(r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"',
                                wbxml):
        out[name] = zf.read("xl/" + rels[rid].lstrip("/")).decode()
    return out, [n for n in zipfile.ZipFile(path).namelist()]


def hidden_writes(path):
    """Cells written inside a merged range but not at its top-left."""
    xmls, _ = sheet_xml(path)
    out = []
    for name, xml in xmls.items():
        covered = {}
        for m in re.findall(r'<mergeCell ref="([A-Z]+\d+:[A-Z]+\d+)"/>', xml):
            c1, r1, c2, r2 = range_boundaries(m)
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    if (rr, cc) != (r1, c1):
                        covered[(rr, cc)] = m
        root = ET.fromstring(xml)
        for row in root.iter(NS + "row"):
            for c in row.iter(NS + "c"):
                m = re.match(r"([A-Z]+)(\d+)", c.get("r"))
                key = (int(m.group(2)), column_index_from_string(m.group(1)))
                if key not in covered:
                    continue
                v = c.find(NS + "v")
                if c.find(NS + "f") is not None or (
                        v is not None and (v.text or "").strip()):
                    out.append((name, c.get("r"), covered[key]))
    return out


def check_formulas(path, problems):
    wb = openpyxl.load_workbook(path, data_only=False)
    sheetnames = set(wb.sheetnames)
    n_formula = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if not (isinstance(v, str) and v.startswith("=")):
                    continue
                n_formula += 1
                if v in ("None", "nan"):
                    problems.append("%s!%s contains %r"
                                    % (ws.title, cell.coordinate, v))
                body = re.sub(r'"[^"]*"', '""', v)     # drop string literals
                for m in SHEET_REF_RE.finditer(body):
                    ref = m.group(1) or m.group(2)
                    if ref not in sheetnames:
                        problems.append("%s!%s references unknown sheet %r"
                                        % (ws.title, cell.coordinate, ref))
                for m in FUNC_RE.finditer(body):
                    fn = m.group(1).split(".")[-1]
                    if fn in MODERN and "_xlfn." not in m.group(1):
                        problems.append(
                            "%s!%s uses modern function %s without _xlfn."
                            % (ws.title, cell.coordinate, fn))
    return n_formula


def audit(path):
    problems = []
    wb = openpyxl.load_workbook(path, data_only=False)
    n_formula = check_formulas(path, problems)

    n_dv = sum(len(ws.data_validations.dataValidation)
               for ws in wb.worksheets)
    n_cf = sum(len(ws.conditional_formatting._cf_rules)
               for ws in wb.worksheets)
    _, names = sheet_xml(path)
    charts = len([n for n in names if n.startswith("xl/charts/chart")])

    for sheet, ref, merge in hidden_writes(path):
        problems.append("%s!%s is written inside merge %s and would never "
                        "be visible" % (sheet, ref, merge))

    return {
        "path": path,
        "sheets": wb.sheetnames,
        "hidden": [s.title for s in wb.worksheets
                   if s.sheet_state != "visible"],
        "formulas": n_formula,
        "validations": n_dv,
        "cond_formats": n_cf,
        "charts": charts,
        "problems": problems,
    }


def main(argv):
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[")
                     else [a])
    if not paths:
        print(__doc__)
        return 1
    bad = 0
    for path in paths:
        r = audit(path)
        print("=" * 78)
        print(path)
        print("  sheets   : %s" % ", ".join(r["sheets"]))
        print("  hidden   : %s" % (", ".join(r["hidden"]) or "-"))
        print("  formulas : %-6d validations %-4d cond. formats %-4d "
              "charts %d" % (r["formulas"], r["validations"],
                             r["cond_formats"], r["charts"]))
        if r["problems"]:
            bad += 1
            print("  PROBLEMS (%d):" % len(r["problems"]))
            for p in r["problems"][:25]:
                print("    - %s" % p)
            if len(r["problems"]) > 25:
                print("    ... and %d more" % (len(r["problems"]) - 25))
        else:
            print("  PROBLEMS : none \u2713")
    print("=" * 78)
    print("clean" if not bad else "%d file(s) need attention" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
````

---
## `tools/calc_check_santa.py`

*QA: recalculates the whole workbook with the formulas engine and diffs every cached value.* (151 lines)

````python
#!/usr/bin/env python3
"""
Recalculate a generated workbook with the ``formulas`` engine and report every
cell that evaluates to an Excel error (#REF!, #NAME?, #VALUE!, #DIV/0! ...).

This is the closest thing to opening the file in Excel without Excel: every
formula is parsed and evaluated for real, so broken references, typos and
unsupported functions show up here instead of in a customer's hands.

    pip install formulas
    python3 tools/calc_check_santa.py products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx

Known limitation: the ``formulas`` package cannot evaluate OFFSET-based defined
names (the auto-expanding dropdown lists), so those report #REF! here while
Excel and Google Sheets handle them normally.  They are listed separately as
"engine limitations" rather than failures.
"""

import glob
import logging
import re
import sys
import warnings

logging.disable(logging.CRITICAL)
warnings.simplefilter("ignore")

import formulas                                     # noqa: E402
import openpyxl                                     # noqa: E402


def check(path, verbose=True, compare=True):
    xl = formulas.ExcelModel().loads(path).finish()
    sol = xl.calculate()

    wb = openpyxl.load_workbook(path)
    wbv = openpyxl.load_workbook(path, data_only=True)
    fname = path.split("/")[-1]          # engine keeps the filename verbatim
    titles = {t.upper(): t for t in wb.sheetnames}

    def key_for(title, coord):
        # the engine uppercases the sheet title but keeps the filename as-is
        return "'[%s]%s'!%s" % (fname, title.upper(), coord)

    def formula_of(key):
        m = re.match(r"^'\[.*\](.*)'!([A-Z]+\d+)$", key)
        if not m:
            return None, None
        sheet, coord = m.group(1), m.group(2)
        real = titles.get(sheet.upper())
        if real is not None:
            return real, wb[real][coord].value
        return sheet, None

    mismatches = []
    if compare:
        for ws in wb.worksheets:
            wsv = wbv[ws.title]
            for row in ws.iter_rows():
                for cell in row:
                    v = cell.value
                    if not (isinstance(v, str) and v.startswith("=")):
                        continue
                    got = sol.get(key_for(ws.title, cell.coordinate))
                    if got is None:
                        continue
                    try:
                        calc = got.value[0, 0]
                    except Exception:
                        calc = got
                    cached = wsv[cell.coordinate].value
                    if calc is None and cached is None:
                        continue
                    if isinstance(calc, (int, float)) and \
                            isinstance(cached, (int, float)):
                        if abs(float(calc) - float(cached)) > 1e-6:
                            mismatches.append((ws.title, cell.coordinate,
                                               calc, cached))
                    elif str(calc).strip() != str(cached).strip():
                        mismatches.append((ws.title, cell.coordinate,
                                           calc, cached))

    errors, limits = [], []
    for key, value in sol.items():
        try:
            val = value.value[0, 0] if hasattr(value, "value") else value
        except Exception:
            continue
        text = str(val).strip()
        if not text.startswith("#"):
            continue
        if text == "#":            # a literal "#" header cell, not an error
            continue
        sheet, f = formula_of(key)
        if sheet is None:          # workbook-level defined name, not a cell
            limits.append((text, key, sheet, f))
            continue
        # things the engine cannot do but Excel and Google Sheets can:
        #   OFFSET() defined names (the auto-expanding dropdown lists)
        #   HYPERLINK()  (not implemented in the formulas package)
        if "OFFSET" in key.upper() or (f and "HYPERLINK(" in str(f).upper()):
            limits.append((text, key, sheet, f))
            continue
        errors.append((text, key, sheet, f))

    if verbose:
        print("=" * 78)
        print(path)
        print("  cells evaluated : %d" % len(sol))
        print("  engine limitations (fine in Excel / Sheets) : %d %s"
              % (len(limits), sorted({t for t, k, s2, f in limits})))
        if mismatches:
            print("  CACHED VALUE OUT OF DATE (%d):" % len(mismatches))
            for sheet, coord, calc, cached in mismatches[:15]:
                print("      %-20s %-6s recalcs to %r, file says %r"
                      % (sheet, coord, str(calc)[:30], str(cached)[:30]))
            if len(mismatches) > 15:
                print("      ... and %d more" % (len(mismatches) - 15))
        if errors:
            print("  ERRORS (%d):" % len(errors))
            for text, key, sheet, f in errors[:30]:
                print("    %-9s %-28s %s" % (text, (sheet or "?"),
                                             str(f)[:90]))
            if len(errors) > 30:
                print("    ... and %d more" % (len(errors) - 30))
        else:
            print("  ERRORS : none \u2713")
    return errors + mismatches, limits


def main(argv):
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[")
                     else [a])
    if not paths:
        print(__doc__)
        return 1
    total = 0
    for p in paths:
        errors, _ = check(p)
        total += len(errors)
    print("=" * 78)
    print("clean" if not total else "%d error cell(s) across %d file(s)"
          % (total, len(paths)))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
````

---
## `tools/layout_check_santa.py`

*QA: finds clipped or overflowing text before buyers do.* (160 lines)

````python
#!/usr/bin/env python3
"""
Layout audit: finds text that will be clipped or overflow in Excel.

Excel never grows a merged cell to fit its text, so wrapped text in a merged
range needs an explicit row height.  This tool re-measures every cell in a
generated workbook the same way the builder did and reports:

    TOO TALL  wrapped text needs more height than the row(s) provide
    OVERFLOW  unwrapped text is wider than its cell and the neighbour is busy
    TINY ROW  an explicit row height smaller than one line of its font

    python3 tools/layout_check_santa.py products/Secret_Santa_*.xlsx
"""

import glob
import math
import sys

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries

DEFAULT_COL_WIDTH = 8.43
CHARS_PER_UNIT = 1.05        # measured against Calibri 11 in Excel


def width_map(ws):
    """Column widths, expanding grouped ranges such as ``set_column("C:L")``."""
    widths = {}
    for dim in ws.column_dimensions.values():
        if not dim.width:
            continue
        lo = dim.min or 1
        hi = dim.max or lo
        for idx in range(lo, hi + 1):
            widths[idx] = dim.width
    return widths


def col_width(ws, idx, widths=None):
    if widths is None:
        widths = width_map(ws)
    return widths.get(idx, DEFAULT_COL_WIDTH)


def row_height(ws, idx, default=15.0):
    dim = ws.row_dimensions.get(idx)
    if dim is not None and dim.height:
        return dim.height
    return default


def check(path, verbose=True):
    wb = openpyxl.load_workbook(path)
    problems = []
    for ws in wb.worksheets:
        widths = width_map(ws)
        merged = {}
        for mr in ws.merged_cells.ranges:
            c1, r1, c2, r2 = range_boundaries(str(mr))
            merged[(r1, c1)] = (r1, c1, r2, c2)
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    if (rr, cc) != (r1, c1):
                        merged[(rr, cc)] = None      # swallowed cell

        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if not isinstance(v, str) or not v.strip():
                    continue
                if v.startswith("="):
                    continue                       # formula: length unknown
                key = (cell.row, cell.column)
                if key in merged and merged[key] is None:
                    continue                       # hidden by a merge
                blocked = True
                if key in merged:
                    r1, c1, r2, c2 = merged[key]
                    width = sum(col_width(ws, c, widths)
                                for c in range(c1, c2 + 1))
                    height = sum(row_height(ws, r) for r in range(r1, r2 + 1))
                else:
                    width = col_width(ws, cell.column, widths)
                    height = row_height(ws, cell.row)
                    nxt = ws.cell(row=cell.row, column=cell.column + 1)
                    blocked = (nxt.value not in (None, "")
                               or (cell.row, cell.column + 1) in merged)

                size = cell.font.size or 11
                room = width * CHARS_PER_UNIT * (11.0 / float(size))
                text = v.strip()
                wrap = bool(cell.alignment.wrap_text)

                if wrap:
                    lines = 0
                    for part in text.split("\n"):
                        lines += max(1,
                                     int(math.ceil(len(part) / max(room, 1))))
                    line_h = size * 1.32 + 2.2
                    need = lines * line_h
                    if need > height + 1.5:
                        problems.append(
                            ("TOO TALL", ws.title, cell.coordinate,
                             "needs ~%.0fpt for %d line(s), has %.0fpt: %r"
                             % (need, lines, height, text[:60])))
                else:
                    if len(text) > room * 1.02 and key not in merged:
                        if blocked:
                            # a pasted web address is always longer than its
                            # column: the clickable button next to it is the
                            # intended way in, so this is by design
                            kind = ("CLIPPED LINK"
                                    if text.lower().startswith("http")
                                    else "OVERFLOW")
                            problems.append(
                                (kind, ws.title, cell.coordinate,
                                 "%d chars in %.0f wide cell: %r"
                                 % (len(text), width, text[:60])))
                if height < size * 1.15 and key not in merged:
                    problems.append(
                        ("TINY ROW", ws.title, cell.coordinate,
                         "row %.0fpt for %spt font" % (height, size)))
    if verbose:
        print("=" * 78)
        print(path)
        if problems:
            by_kind = {}
            for kind, sheet, coord, msg in problems:
                by_kind.setdefault(kind, []).append((sheet, coord, msg))
            for kind, items in sorted(by_kind.items()):
                print("  %-9s %d" % (kind, len(items)))
                for sheet, coord, msg in items[:12]:
                    print("      %-22s %-6s %s" % (sheet, coord, msg))
                if len(items) > 12:
                    print("      ... and %d more" % (len(items) - 12))
        else:
            print("  layout: no clipping or overflow found \u2713")
    return problems


def main(argv):
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[")
                     else [a])
    if not paths:
        print(__doc__)
        return 1
    total = 0
    for p in paths:
        total += len([x for x in check(p) if x[0] != "CLIPPED LINK"])
    print("=" * 78)
    print("clean" if not total else "%d layout issue(s)" % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
````

---
## `tools/render_preview_santa.py`

*QA: renders any tab to PNG (real emoji glyphs) - powers the user-guide screenshots.* (362 lines)

````python
#!/usr/bin/env python3
"""
Render a sheet of a generated .xlsx to a PNG so the design can be eyeballed
without Excel (there is no Excel or LibreOffice in this sandbox).

It is an approximation of Excel's rendering: cached formula values, solid
fills, borders, merged ranges, wrapped text, horizontal/vertical alignment,
number formats and text that spills into empty neighbours.  Emoji are drawn as
coloured tiles because no emoji font is installed - their position and size are
still visible, which is what matters for layout checking.

    python3 tools/render_preview_santa.py products/x.xlsx "🎄 Dashboard" \\
        /tmp/dash.png --rows 1-90
"""

import argparse
import datetime
import os
import re
import sys
import unicodedata

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries
from PIL import Image, ImageDraw, ImageFont

# real emoji glyphs when the Novality Store font kit is available
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    from etsy.crochet_lib import emoji_bitmap as _EMOJI_BITMAP
except Exception:                                        # pragma: no cover
    _EMOJI_BITMAP = None

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
PX_PER_WIDTH = 7.0
PT_TO_PX = 96.0 / 72.0
DEFAULT_ROW_PX = 20
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u2190-\u21FF"
    "\u2700-\u27BF\u2764\u2699\u26A1\u2705\u274C\u2753\u2764]")


def is_emoji(ch):
    if ord(ch) < 0x2100:
        return False
    if ord(ch) in (0xFE0F, 0x2022, 0x2014, 0x2013, 0x201C, 0x201D, 0x2019,
                   0x2026, 0x00B7):
        return False
    cat = unicodedata.category(ch)
    return cat in ("So", "Sk", "Cs") or ord(ch) > 0x2500


def font(size, bold=False, italic=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FONT_DIR + name, max(6, int(round(size))))


def color_of(c, default=None):
    if c is None:
        return default
    rgb = getattr(c, "rgb", None)
    if isinstance(rgb, str) and len(rgb) >= 6:
        rgb = rgb[-6:]
        try:
            return tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            return default
    return default


def fmt_value(value, num_format):
    if value is None:
        return ""
    if isinstance(value, datetime.datetime):
        if value.hour or value.minute:
            return value.strftime("%d %b %Y %H:%M")
        return value.strftime("%d %b %Y")
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    nf = (num_format or "").lower()
    if isinstance(value, (int, float)):
        if "yy" in nf or "dd" in nf or "mmmm" in nf or "hh" in nf:
            try:
                dt = (datetime.datetime(1899, 12, 30)
                      + datetime.timedelta(days=float(value)))
            except (OverflowError, ValueError):
                return str(value)
            if "yyyy" in nf and "d" not in nf:
                return dt.strftime("%Y")
            if "dddd" in nf:
                return dt.strftime("%A %d %B %Y")
            if "ddd" in nf or "dd mmm" in nf or "d mmm" in nf:
                return dt.strftime("%d %b %Y")
            if "mm" in nf or "yy" in nf:
                return dt.strftime("%d/%m/%Y")
            return dt.strftime("%d %b")
        if "%" in nf:
            dp = 2 if "0.00%" in nf else (1 if "0.0%" in nf else 0)
            return ("%%.%df%%%%" % dp) % (value * 100)
        if "#,##0.00" in nf:
            return "{:,.2f}".format(value)
        if "#,##0" in nf or nf in ("0", "#,##0.0"):
            return "{:,.0f}".format(value) if "#,##0.0" not in nf \
                else "{:,.1f}".format(value)
        if value == int(value):
            return str(int(value))
        return "%.2f" % value
    return str(value)


def render(path, sheet_title, out, rows=None, cols=None, zoom=1.0):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet_title]

    # --- geometry -------------------------------------------------------
    widths = {}
    for dim in ws.column_dimensions.values():
        if not dim.width:
            continue
        for idx in range(dim.min or 1, (dim.max or dim.min or 1) + 1):
            widths[idx] = dim.width
    heights = {i: d.height for i, d in ws.row_dimensions.items() if d.height}

    r1, r2 = (rows or (1, ws.max_row))
    c1, c2 = (cols or (1, ws.max_column))

    def col_px(i):
        return int(round(widths.get(i, 8.43) * PX_PER_WIDTH)) + 5

    def row_px(i):
        return int(round(heights.get(i, 15.0) * PT_TO_PX)) or DEFAULT_ROW_PX

    xs = {}
    x = 0
    for i in range(c1, c2 + 1):
        xs[i] = x
        x += col_px(i)
    ys = {}
    y = 0
    for i in range(r1, r2 + 1):
        ys[i] = y
        y += row_px(i)
    W, H = int(x * zoom), int(y * zoom)
    img = Image.new("RGB", (max(W, 1), max(H, 1)), (255, 255, 255))
    d = ImageDraw.Draw(img)

    merges = {}
    swallowed = set()
    for mr in ws.merged_cells.ranges:
        mc1, mr1, mc2, mr2 = range_boundaries(str(mr))
        merges[(mr1, mc1)] = (mr1, mc1, mr2, mc2)
        for rr in range(mr1, mr2 + 1):
            for cc in range(mc1, mc2 + 1):
                if (rr, cc) != (mr1, mc1):
                    swallowed.add((rr, cc))

    def cell_box(rr, cc):
        if (rr, cc) in merges:
            a, b, c_, e = merges[(rr, cc)]
            x1, y1 = xs.get(b, x), ys.get(a, y)
            x2 = xs.get(e, x) + col_px(e)
            y2 = ys.get(c_, y) + row_px(c_)
        else:
            x1, y1 = xs.get(cc, x), ys.get(rr, y)
            x2, y2 = x1 + col_px(cc), y1 + row_px(rr)
        return x1, y1, x2, y2

    def occupied(rr, cc):
        c = ws.cell(row=rr, column=cc)
        return c.value not in (None, "")

    # --- paint ----------------------------------------------------------
    for rr in range(r1, r2 + 1):
        for cc in range(c1, c2 + 1):
            if (rr, cc) in swallowed:
                continue
            cell = ws.cell(row=rr, column=cc)
            x1, y1, x2, y2 = cell_box(rr, cc)
            if x2 <= 0 or y2 <= 0 or x1 >= x or y1 >= y:
                continue
            fill = color_of(cell.fill.start_color) if (
                cell.fill and cell.fill.patternType == "solid") else None
            if fill:
                d.rectangle([x1, y1, x2 - 1, y2 - 1], fill=fill)
            b = cell.border
            for side, edges in ((b.left, (x1, y1, x1, y2)),
                                (b.right, (x2 - 1, y1, x2 - 1, y2)),
                                (b.top, (x1, y1, x2, y1)),
                                (b.bottom, (x1, y2 - 1, x2, y2 - 1))):
                if side is not None and side.style:
                    col = color_of(side.color, (200, 200, 200))
                    thick = 2 if side.style in ("medium", "thick", "double") \
                        else 1
                    d.line(list(edges), fill=col, width=thick)

    # --- text -----------------------------------------------------------
    for rr in range(r1, r2 + 1):
        for cc in range(c1, c2 + 1):
            if (rr, cc) in swallowed:
                continue
            cell = ws.cell(row=rr, column=cc)
            raw = fmt_value(cell.value, cell.number_format)
            if not raw:
                continue
            x1, y1, x2, y2 = cell_box(rr, cc)
            if x2 <= 0 or y2 <= 0 or x1 >= x or y1 >= y:
                continue
            al = cell.alignment
            fnt = font((cell.font.size or 11) * 1.02,
                       bool(cell.font.bold), bool(cell.font.italic))
            col = color_of(cell.font.color, (0, 0, 0))
            indent = int((al.indent or 0) * 8)
            pad = 4 + indent

            # spill into empty neighbours when the text is not wrapped
            box_w = x2 - x1
            if not al.wrap_text:
                cc2 = cc + 1
                while (cc2 <= c2 and not occupied(rr, cc2)
                       and (rr, cc2) not in swallowed
                       and d.textlength(raw, font=fnt) > box_w - 2 * pad):
                    box_w += col_px(cc2)
                    cc2 += 1

            if al.wrap_text:
                words, lines, cur = raw.replace("\n", " \n ").split(), [], ""
                for w in words:
                    trial = (cur + " " + w).strip()
                    if d.textlength(trial, font=fnt) <= box_w - 2 * pad \
                            or not cur:
                        cur = trial
                    else:
                        lines.append(cur)
                        cur = w
                    if w == "\n":
                        lines.append(cur)
                        cur = ""
                if cur:
                    lines.append(cur)
            else:
                lines = raw.split("\n")

            lh = int((cell.font.size or 11) * 1.42)
            total_h = lh * len(lines)
            va = al.vertical or "bottom"
            if va == "center":
                ty = y1 + max(0, (y2 - y1 - total_h) // 2)
            elif va == "top":
                ty = y1 + 3
            else:
                ty = y1 + max(0, (y2 - y1 - total_h) // 2)

            for line in lines:
                drawn, cx = [], x1 + pad
                for ch in line:
                    if is_emoji(ch):
                        drawn.append(("tile", ch))
                    else:
                        drawn.append(("text", ch))
                # measure
                widths_px, tiles = [], []
                for kind, ch in drawn:
                    if kind == "tile":
                        if _EMOJI_BITMAP is not None:
                            wpx = _EMOJI_BITMAP(
                                ch, max(8, int(lh * 1.02))).width + 2
                        else:
                            wpx = int(lh * 0.95)
                    else:
                        wpx = d.textlength(ch, font=fnt)
                    widths_px.append(wpx)
                line_w = sum(widths_px)
                ha = al.horizontal or ("right" if isinstance(
                    cell.value, (int, float)) and not cell.font.bold
                    else "left")
                if ha == "center":
                    cx = x1 + max(pad, (box_w - line_w) // 2)
                elif ha == "right":
                    cx = x1 + max(pad, box_w - line_w - pad)
                for (kind, ch), wpx in zip(drawn, widths_px):
                    if kind == "tile":
                        if _EMOJI_BITMAP is not None:
                            bmp = _EMOJI_BITMAP(ch, max(8, int(lh * 1.02)))
                            img.paste(bmp, (int(cx), ty + max(
                                0, (lh - bmp.height) // 2)), bmp)
                        else:
                            hue = (ord(ch) * 47) % 360
                            import colorsys
                            rgb = tuple(int(255 * v) for v in
                                        colorsys.hsv_to_rgb(hue / 360.0,
                                                            0.55, 0.85))
                            d.rounded_rectangle([cx, ty + 1, cx + wpx - 2,
                                                 ty + lh - 2], radius=3,
                                                fill=rgb)
                    else:
                        d.text((cx, ty), ch, font=fnt, fill=col)
                    cx += wpx
                ty += lh
    # --- inserted pictures ---------------------------------------------
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, \
        TwoCellAnchor, AbsoluteAnchor
    for pic in getattr(ws, "_images", []):
        anc = pic.anchor
        frm = getattr(anc, "_from", None)
        if frm is None:
            continue
        col, row = frm.col + 1, frm.row + 1
        if not (c1 <= col <= c2 and r1 <= row <= r2):
            continue
        x1 = xs.get(col, 0) + int((frm.colOff or 0) / 9525.0)
        y1 = ys.get(row, 0) + int((frm.rowOff or 0) / 9525.0)
        to = getattr(anc, "to", None)
        if to is not None:
            x2 = xs.get(to.col + 1, x) + int((to.colOff or 0) / 9525.0)
            y2 = ys.get(to.row + 1, y) + int((to.rowOff or 0) / 9525.0)
            wpx, hpx = x2 - x1, y2 - y1
        else:
            try:
                ext = anc.ext
                wpx, hpx = int(ext.cx / 9525.0), int(ext.cy / 9525.0)
            except AttributeError:
                wpx, hpx = int(pic.width), int(pic.height)
        try:
            import io as _io
            sub = Image.open(_io.BytesIO(pic._data())).convert("RGBA")
            sub = sub.resize((max(wpx, 1), max(hpx, 1)), Image.LANCZOS)
            img.paste(sub, (x1, y1), sub)
        except Exception as exc:
            print("  (image skipped: %s)" % exc)

    if zoom != 1.0:
        img = img.resize((W, H), Image.LANCZOS)
    img.save(out)
    return out, img.size


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("workbook")
    p.add_argument("sheet")
    p.add_argument("out")
    p.add_argument("--rows", default=None, help="e.g. 1-90")
    p.add_argument("--cols", default=None, help="e.g. A-M")
    p.add_argument("--zoom", type=float, default=1.0)
    a = p.parse_args(argv)
    rows = tuple(int(x) for x in a.rows.split("-")) if a.rows else None
    cols = None
    if a.cols:
        lo, hi = a.cols.split("-")
        cols = (openpyxl.utils.column_index_from_string(lo),
                openpyxl.utils.column_index_from_string(hi))
    out, size = render(a.workbook, a.sheet, a.out, rows, cols, a.zoom)
    print("%s -> %s (%dx%d)" % (a.sheet, out, size[0], size[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
````

---
## `tools/make_banner_alpha_santa.py`

*Turns the generated banner art into the transparent PNG the workbook embeds.* (74 lines)

````python
#!/usr/bin/env python3
"""
Turn the flat banner art from the image generator into an Excel-ready banner.

Generated PNGs always have a solid background, but the workbook banner sits on
a cream canvas and needs a real alpha channel to blend in.  This tool:

    1. crops the generated image to the banner window (the window covers the
       art band and nothing else)
    2. finds the background colour from the image corners
    3. makes every pixel within TOLERANCE of that colour transparent, with a
       soft 6-step falloff so edges stay smooth
    4. applies the same transparency to near-white and near-black pixels so
       snow, fur and paper tones do not form a box around the artwork
    5. scales the result to the exact banner width and writes banner_X.png

    python3 tools/make_banner_alpha_santa.py assets/raw_banner_noel.png \\
        assets/banner_noel.png
"""

import sys

from PIL import Image

WIN = (0.06, 0.02, 0.68, 0.98)     # l, t, r, b window inside a 1600x640 art
TARGET_W = 996                     # px, matches the insert scale in guide.py
TOLERANCE = 26


def to_alpha(src, dst):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    l, t, r, b = int(W * WIN[0]), int(H * WIN[1]), int(W * WIN[2]), \
        int(H * WIN[3])
    im = im.crop((l, t, r, b))
    im = im.resize((TARGET_W, int(TARGET_W * (b - t) / (r - l))),
                   Image.LANCZOS)
    px = im.load()
    w, h = im.size

    # sample the corner colours: the generator paints a cream/white band
    corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    out = Image.new("RGBA", (w, h))
    op = out.load()
    near_white = (250, 250, 248)
    near_black = (28, 26, 32)
    for y in range(h):
        for x in range(w):
            r_, g_, b_ = px[x, y]
            dist = max(abs(r_ - bg[0]), abs(g_ - bg[1]), abs(b_ - bg[2]))
            a = 255
            if dist <= TOLERANCE:
                a = 0
            elif dist <= TOLERANCE + 6:
                a = int(255 * (dist - TOLERANCE) / 6)
            else:
                for ref in (near_white, near_black):
                    d2 = max(abs(r_ - ref[0]), abs(g_ - ref[1]),
                             abs(b_ - ref[2]))
                    if d2 <= 10:
                        a = min(a, int(255 * d2 / 10))
            op[x, y] = (r_, g_, b_, a)
    out.save(dst)
    print("%s -> %s  (%dx%d, bg=%s)" % (src, dst, w, h, bg))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: make_banner_alpha_santa.py RAW.png OUT.png")
        sys.exit(1)
    to_alpha(sys.argv[1], sys.argv[2])
````

---
## `etsy/__init__.py`

*Package marker.* (1 lines)

````python

````

---
## `etsy/crochet_lib.py`

*Shared PIL rendering engine (emoji-aware text, fonts, tables, pills, charts) - used to draw the user guide.* (612 lines)

````python
"""
crochet_lib - draw pixel-perfect "screenshots" of the Crochet Craft Fair
Tracker using the REAL demo data (crochet_tracker.demo.Demo), for the
Etsy listing images and the user-guide PDF.

Everything is drawn with PIL: fonts are Poppins / Gelasio (Georgia-metric)
/ Playfair Display / Caveat / JetBrains Mono, plus NotoColorEmoji for the
emoji the real workbook uses.  The palette mirrors the workbook's Berry
theme (cream / deep berry plum / rose / honey gold).

This module is a sibling of etsy/catering_lib.py and deliberately leaves
that file (and the Christmas engine) untouched.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from crochet_tracker import config as C
from crochet_tracker.demo import Demo

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# ---------------------------------------------------------------------------
# palette (classic theme of the workbook)
# ---------------------------------------------------------------------------
PRIMARY = "#5C3A50"          # deep berry plum  (the "espresso" role)
MAUVE = "#8A5F79"            # dusty mauve      (the "latte" role)
ROSE = "#C05268"             # rose accent      (the "copper" role)
GOLD = "#B98A2E"             # honey gold       (the "brass" role)
INK = "#33222C"
MUTED = "#97818D"
CREAM = "#FAF6F1"
CANVAS = "#FAF6F1"
CARD = "#FFFFFF"
ALT = "#FBF7F3"
BORDER = "#E6D9D2"
WHITE = "#FFFFFF"
OK = "#4C7A4C"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
PLUM = "#7A5273"
SOFT = {
    "primary": "#EDE2E8", "mauve": "#EFE2EA", "rose": "#F8E3E7",
    "gold": "#F6EDD8", "ok": "#E2EEE0", "warn": "#FBF0D9", "bad":
    "#F7E2E0", "info": "#E5E9F4", "plum": "#F0E6EE", "muted": "#F2EBEE",
}
COLORS = {
    "primary": PRIMARY, "mauve": MAUVE, "rose": ROSE, "gold": GOLD,
    "ok": OK, "warn": WARN, "bad": BAD, "info": INFO, "plum": PLUM,
    "muted": MUTED, "ink": INK,
}

EMOJI_STRIKE = 109


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# fonts
# ---------------------------------------------------------------------------
_FILES = {
    "sans": "Poppins-Regular.ttf", "sans_md": "Poppins-Medium.ttf",
    "sans_sb": "Poppins-SemiBold.ttf", "sans_b": "Poppins-Bold.ttf",
    "sans_xb": "Poppins-ExtraBold.ttf",
    "serif": "Gelasio[wght].ttf", "display": "PlayfairDisplay[wght].ttf",
    "hand": "Caveat[wght].ttf", "mono": "JetBrainsMono[wght].ttf",
}
_VAR_WEIGHT = {"serif": "Regular", "serif_b": "Bold", "serif_sb": "SemiBold",
               "display": "Regular", "display_b": "Bold",
               "display_xb": "ExtraBold", "display_blk": "Black",
               "hand": "Bold", "mono": "Medium"}
_font_cache = {}
_emoji_font = None


def F(name, size):
    """Get a cached font.  name in _FILES keys + weight variants."""
    key = (name, size)
    if key in _font_cache:
        return _font_cache[key]
    base = name.split("_")[0] if name.split("_")[0] in ("serif", "display",
                                                        "hand", "mono") \
        else name
    path = os.path.join(FONTS, _FILES[base])
    f = ImageFont.truetype(path, size)
    if base != name:                       # variable weight variant
        try:
            f.set_variation_by_name(_VAR_WEIGHT[name])
        except Exception:
            pass
    _font_cache[key] = f
    return f


def emoji_font():
    global _emoji_font
    if _emoji_font is None:
        _emoji_font = ImageFont.truetype(
            os.path.join(FONTS, "NotoColorEmoji.ttf"), EMOJI_STRIKE)
    return _emoji_font


# ---------------------------------------------------------------------------
# emoji-aware text engine
# ---------------------------------------------------------------------------
_EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2B00, 0x2BFF), (0x2300, 0x23FF),
                 (0x2190, 0x21FF), (0x2600, 0x27BF))
_SPECIAL = {"\u2713": "check"}             # drawn as a vector check mark


def _is_emoji(ch):
    o = ord(ch)
    if o == 0x2713:
        return False
    return any(a <= o <= b for a, b in _EMOJI_RANGES)


def tokenize(s):
    """Split into [('text'|'emoji'|'check', run)] runs."""
    runs = []

    def push(kind, chunk):
        if chunk:
            if runs and runs[-1][0] == kind and kind == "text":
                runs[-1] = (kind, runs[-1][1] + chunk)
            else:
                runs.append((kind, chunk))

    for ch in str(s):
        if ord(ch) in (0xFE0F, 0x200D):
            continue
        if ch in _SPECIAL:
            push("check", ch)
        elif _is_emoji(ch):
            push("emoji", ch)
        else:
            push("text", ch)
    return runs


_emoji_bitmap_cache = {}


def emoji_bitmap(ch, height):
    key = (ch, height)
    if key in _emoji_bitmap_cache:
        return _emoji_bitmap_cache[key]
    scratch = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratch)
    d.text((30, 30), ch, font=emoji_font(), embedded_color=True)
    box = scratch.getbbox()
    if box is None:                        # fallback: empty
        bmp = Image.new("RGBA", (height, height), (0, 0, 0, 0))
    else:
        bmp = scratch.crop(box)
        scale = height / float(bmp.height)
        bmp = bmp.resize((max(1, int(bmp.width * scale)), height),
                         Image.LANCZOS)
    _emoji_bitmap_cache[key] = bmp
    return bmp


_scratch_draw = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def text_width(s, font):
    total = 0
    size = font.size
    ascent, _ = font.getmetrics()
    for kind, chunk in tokenize(s):
        if kind == "text":
            total += _scratch_draw.textlength(chunk, font=font)
        elif kind == "emoji":
            for ch in chunk:
                total += emoji_bitmap(ch, int(ascent * 1.02)).width + \
                    int(size * 0.06)
        else:                              # check mark
            total += int(ascent * 0.9)
    return total


def draw_text(img, xy, s, font, fill=INK, anchor="la"):
    """Emoji-aware text.  anchor: la | ma | ra (y is always the top)."""
    x, y = xy
    w = text_width(s, font)
    if anchor == "ma":
        x -= w / 2.0
    elif anchor == "ra":
        x -= w
    d = ImageDraw.Draw(img)
    ascent, descent = font.getmetrics()
    for kind, chunk in tokenize(s):
        if kind == "text":
            d.text((x, y), chunk, font=font, fill=fill)
            x += _scratch_draw.textlength(chunk, font=font)
        elif kind == "emoji":
            h = int(ascent * 1.02)
            for ch in chunk:
                bmp = emoji_bitmap(ch, h)
                img.paste(bmp, (int(x), int(y + (ascent - h) * 0.45)), bmp)
                x += bmp.width + int(font.size * 0.06)
        else:                              # vector check mark
            size = ascent * 0.72
            cx, cy = x + size * 0.1, y + ascent * 0.72
            check_poly(d, cx, cy, size, fill, max(2, int(ascent * 0.11)))
            x += int(ascent * 0.9)
    return w


def check_poly(d, cx, cy, size, color, width):
    """A crisp vector check mark centred on (cx, cy)."""
    s = size / 2.0
    pts = [(cx - s * 0.95, cy + s * 0.05), (cx - s * 0.3, cy + s * 0.7),
           (cx + s * 1.0, cy - s * 0.75)]
    d.line(pts, fill=color, width=width, joint="curve")


def fit_size(s, spec, size, max_w, min_size=10):
    """Shrink font size until the string fits max_w. Returns (font, size)."""
    while size > min_size:
        f = F(spec, size)
        if text_width(s, f) <= max_w:
            return f, size
        size -= 2
    return F(spec, min_size), min_size


def wrap(s, font, max_w):
    lines, line = [], ""
    for word in str(s).split():
        trial = word if not line else line + " " + word
        if text_width(trial, font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or [""]


# ---------------------------------------------------------------------------
# small drawing primitives
# ---------------------------------------------------------------------------
def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def chip(img, xy, s, bg, fg, size=20, spec="sans_sb", pad=(16, 9),
         bold=True, radius=None):
    """Draw a rounded pill of text.  Returns its width."""
    x, y = xy
    f = F(spec, size)
    w = text_width(s, f)
    h = int(size * 1.9)
    d = ImageDraw.Draw(img)
    r = radius if radius is not None else h // 2
    rrect(d, [x, y, x + w + pad[0] * 2, y + h], r, fill=hexrgb(bg) if
          isinstance(bg, str) and bg.startswith("#") else
          (bg if isinstance(bg, tuple) else hexrgb(SOFT[bg])))
    draw_text(img, (x + pad[0], y + (h - size) / 2.0 - size * 0.14), s, f,
              COLORS.get(fg, fg) if not str(fg).startswith("#") else fg)
    return w + pad[0] * 2


def shadow_paste(canvas, img, xy, blur=24, alpha=70, offset=(0, 14)):
    x, y = int(xy[0]), int(xy[1])
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                   fill=255)
    sh.paste(Image.new("RGBA", img.size, (20, 15, 10, alpha)),
             (x + offset[0], y + offset[1]), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh)
    canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)


def blocks_bar(img, box, pct, n=40, fg=MAUVE, bg=CARD, gap=4,
               border=BORDER):
    """The workbook's signature text progress bar, drawn as blocks."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=hexrgb(bg), outline=hexrgb(border))
    inner = [x0 + 5, y0 + 5, x1 - 5, y1 - 5]
    total = int(n * pct + 0.5)
    slot = (inner[2] - inner[0] - gap * (n - 1)) / float(n)
    for i in range(n):
        bx = inner[0] + i * (slot + gap)
        d.rectangle([bx, inner[1], bx + slot, inner[3]],
                    fill=hexrgb(fg if i < total else "#F0E5E9"))


# ---------------------------------------------------------------------------
# sheet chrome shared by every screen
# ---------------------------------------------------------------------------
def screen_canvas(width, height, bg=CANVAS):
    img = Image.new("RGBA", (width, height), hexrgb(bg))
    return img


def sheet_header(img, title, subtitle, y=0, width=1320, pill_home=True):
    """The 3-row title band every tracker tab uses."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, width, y + 92], fill=hexrgb(CANVAS))
    draw_text(img, (44, y + 10), title, F("serif_b", 40), PRIMARY)
    if pill_home:
        f = F("sans_sb", 17)
        s = "\U0001F3E0  Back to Dashboard"
        w = text_width(s, f)
        rrect(d, [width - 44 - w - 36, y + 24, width - 44, y + 66], 8,
              fill=hexrgb(ROSE))
        draw_text(img, (width - 44 - w - 18, y + 30), s, f, WHITE)
    draw_text(img, (44, y + 64), subtitle, F("sans", 18), MUTED)
    return y + 104


def pill_row(img, y, pills, width=1320, x=44, gap=12, size=17):
    """The quick-stat strip. pills = [(text, color_key)]."""
    for text, color in pills:
        f = F("sans_sb", size)
        w = text_width(text, f) + 30
        d = ImageDraw.Draw(img)
        rrect(d, [x, y, x + w, y + 40], 20, fill=hexrgb(SOFT[color]))
        draw_text(img, (x + 15, y + 8), text, f, COLORS[color])
        x += w + gap
    return y + 40


def section_bar(img, y, text, color=PRIMARY, width=1320, h=52, size=24,
                x=44, w_pad=36):
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + width - 88, y + h], 6, fill=hexrgb(color))
    draw_text(img, (x + 20, y + (h - size) / 2.0 - 2), text,
              F("serif_b", size), WHITE)
    return y + h


STATUS_COLORS = {
    C.ST_OUT: ("bad", "bad"), C.ST_LOW: ("warn", "warn"),
    C.ST_OK: ("ok", "ok"),
}
REORDER_COLORS = {
    C.RE_YES: ("warn", "warn"), C.RE_NO: ("ok", "ok"),
}
PRIORITY_COLORS = {
    C.PR_URGENT: ("bad", "bad"), C.PR_HIGH: ("warn", "warn"),
    C.PR_NORMAL: ("gold", "gold"),
}
PAYMENT_COLORS = {
    "Cash": ("ok", "ok"), "Card": ("info", "info"),
    "Bank transfer": ("plum", "plum"), "Mobile wallet": ("gold", "gold"),
    "Online order": ("rose", "rose"), "Other": ("muted", "muted"),
}


def draw_table(img, x, y, widths, headers, rows, row_h=42, hdr_h=48,
               hdr_bg=PRIMARY, size=17, hdr_size=15, pad=12):
    """rows: list of lists; each cell = str or dict:
       {"t": text, "align": "l/c/r", "color": key, "pill": (bgkey, fgkey),
        "tick": bool, "mono": bool, "bold": bool}"""
    d = ImageDraw.Draw(img)
    total_w = sum(widths)
    rrect(d, [x, y, x + total_w, y + hdr_h], 8, fill=hexrgb(hdr_bg))
    cx = x
    for w, htxt in zip(widths, headers):
        f, _ = fit_size(htxt, "sans_sb", hdr_size, w - 10, 10)
        draw_text(img, (cx + w / 2.0, y + (hdr_h - f.size) / 2.0 - 1), htxt,
                  f, WHITE, anchor="ma")
        cx += w
    yy = y + hdr_h
    for ri, row in enumerate(rows):
        bg = ALT if ri % 2 else CARD
        d.rectangle([x, yy, x + total_w, yy + row_h], fill=hexrgb(bg))
        cx = x
        for w, cell in zip(widths, row):
            cell = cell if isinstance(cell, dict) else {"t": cell}
            txt = str(cell.get("t", ""))
            align = cell.get("align", "l")
            color = COLORS.get(cell.get("color", "ink"), INK)
            if cell.get("pill"):
                bgk, fgk = cell["pill"]
                pf = F("sans_sb", size - 1)
                pw = text_width(txt, pf) + 22
                rrect(d, [cx + (w - pw) / 2.0, yy + 6,
                          cx + (w + pw) / 2.0, yy + row_h - 6],
                      (row_h - 12) / 2.0, fill=hexrgb(SOFT[bgk]))
                draw_text(img, (cx + w / 2.0, yy + (row_h - pf.size) / 2.0
                                - 1), txt, pf, COLORS[fgk], anchor="ma")
            elif cell.get("tick"):
                check_poly(d, cx + w / 2.0, yy + row_h / 2.0, size * 1.1,
                           OK, 4)
            else:
                f, _ = fit_size(txt, "sans_b" if cell.get("bold") else
                                ("mono" if cell.get("mono") else "sans_md"),
                                size, w - 2 * pad - 4, 9)
                ty = yy + (row_h - f.size) / 2.0 - 1
                if align == "c":
                    draw_text(img, (cx + w / 2.0, ty), txt, f, color,
                              anchor="ma")
                elif align == "r":
                    draw_text(img, (cx + w - pad, ty), txt, f, color,
                              anchor="ra")
                else:
                    draw_text(img, (cx + pad, ty), txt, f, color)
            cx += w
        cx = x
        for w in widths[:-1]:
            cx += w
            d.line([cx, yy, cx, yy + row_h], fill=hexrgb(BORDER), width=1)
        yy += row_h
    d.rectangle([x, y, x + total_w, yy], outline=hexrgb(BORDER), width=1)
    return yy


# ---------------------------------------------------------------------------
# charts (real data)
# ---------------------------------------------------------------------------
def _axis_title(img, box, title, size=1.0):
    draw_text(img, ((box[0] + box[2]) / 2.0, box[1] - int(34 * size)), title,
              F("serif_sb", int(23 * size)), PRIMARY, anchor="ma")


def hbar_chart(img, box, title, items, color=ROSE, fmt="${:,.0f}",
               size=1.0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    fs = lambda n: F("sans_sb", int(n * size))
    n = len(items)
    row_h = (y1 - y0) / float(n)
    label_w = max(text_width(lbl, fs(16)) for lbl, _ in items) + 18 * size
    val_w = max(text_width(fmt.format(v), fs(16))
                for _, v in items) + 10 * size
    gx0, gx1 = x0 + label_w, x1 - val_w
    vmax = max(v for _, v in items) or 1
    for i in range(5):                     # gridlines
        gx = gx0 + (gx1 - gx0) * i / 4.0
        d.line([gx, y0, gx, y1], fill=hexrgb(BORDER), width=1)
    for i, (lbl, v) in enumerate(items):
        cy = y0 + row_h * (i + 0.5)
        draw_text(img, (x0, cy - 12 * size), lbl, fs(16), INK)
        bw = (gx1 - gx0) * v / float(vmax)
        rrect(d, [gx0, cy - 12 * size, gx0 + max(bw, 6 * size),
                  cy + 12 * size], int(6 * size), fill=hexrgb(color))
        draw_text(img, (x1, cy - 11 * size), fmt.format(v), fs(16),
                  PRIMARY, anchor="ra")


def grouped_columns(img, box, title, cats, series, fmt="{:,.0f}", size=1.0):
    """series = [(name, values, color)]"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    all_v = [v for _, vals, _ in series for v in vals]
    vmax = max(all_v) or 1
    ncat = len(cats)
    slot = (x1 - x0) / float(ncat)
    bw = min(34 * size, slot * 0.32)
    for i in range(5):
        gy = y1 - (y1 - y0 - 30 * size) * i / 4.0
        d.line([x0, gy, x1, gy], fill=hexrgb(BORDER), width=1)
        draw_text(img, (x0 - 8 * size, gy - 9 * size),
                  fmt.format(vmax * i / 4.0), F("sans", int(13 * size)),
                  MUTED, anchor="ra")
    for ci, cat in enumerate(cats):
        cx = x0 + slot * (ci + 0.5)
        f, _ = fit_size(cat, "sans_md", int(13 * size), slot - 6 * size,
                        int(8 * size))
        draw_text(img, (cx, y1 - 26 * size), cat, f, MUTED, anchor="ma")
        for si, (name, vals, color) in enumerate(series):
            v = vals[ci]
            h = (y1 - 30 * size - y0) * v / float(vmax)
            bx = cx - bw - 3 * size + si * (bw + 6 * size)
            d.rectangle([bx, y1 - 30 * size - h, bx + bw, y1 - 30 * size],
                        fill=hexrgb(color))
    lx = x0
    for name, _, color in series:
        d.rectangle([lx, y0 - 22 * size, lx + 16 * size, y0 - 6 * size],
                    fill=hexrgb(color))
        draw_text(img, (lx + 22 * size, y0 - 24 * size), name,
                  F("sans_sb", int(15 * size)), INK)
        lx += 22 * size + text_width(name, F("sans_sb", int(15 * size))) \
            + 26 * size


def line_series(img, box, title, cats, values, color=PRIMARY, fmt="{:,.0f}",
                size=1.0, width=None):
    """A single line with markers (the 'net' line of the combo charts)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    vmax = max(max(values), 1)
    vmin = min(min(values), 0)
    ncat = len(cats)
    slot = (x1 - x0) / float(ncat)
    pts = []
    for ci, v in enumerate(values):
        cx = x0 + slot * (ci + 0.5)
        cy = y1 - 30 * size - (y1 - 30 * size - y0) * (v - vmin) / \
            float(vmax - vmin or 1)
        pts.append((cx, cy))
    if width is None:
        width = max(3, int(4 * size))
    d.line(pts, fill=hexrgb(color), width=width, joint="curve")
    for (cx, cy) in pts:
        d.ellipse([cx - 6 * size, cy - 6 * size, cx + 6 * size,
                   cy + 6 * size], fill=hexrgb(color))


def doughnut_chart(img, box, title, items, size=1.0, center_word="events",
                   center_value=None):
    """items = [(label, value, color)]"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    total = sum(v for _, v, _ in items) or 1
    cx, cy = x0 + (y1 - y0) / 2.0 + 10, (y0 + y1) / 2.0
    r = (y1 - y0) / 2.0 - 6
    start = -90
    for lbl, v, color in items:
        sweep = 360.0 * v / total
        if v:
            d.pieslice([cx - r, cy - r, cx + r, cy + r], start,
                       start + sweep, fill=hexrgb(color),
                       outline=hexrgb(CREAM))
        start += sweep
    hr = r * 0.58
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
    big = center_value if center_value is not None else total
    draw_text(img, (cx, cy - 26 * size), str(big),
              F("display_b", int(44 * size)), PRIMARY, anchor="ma")
    draw_text(img, (cx, cy + 24 * size), center_word,
              F("sans_sb", int(16 * size)), MUTED, anchor="ma")
    lx = cx + r + 40 * size
    ly = y0 + 24 * size
    import re as _re
    for lbl, v, color in items:
        lbl = _re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF"
                      r"\u2300-\u23FF\u2190-\u21FF]\uFE0F?\s*", "", lbl).strip()
        d.rectangle([lx, ly + 4, lx + 16, ly + 20], fill=hexrgb(color))
        f, _ = fit_size(lbl, "sans_md", 15, x1 - lx - 90, 9)
        draw_text(img, (lx + 24, ly), lbl, f, INK)
        draw_text(img, (x1, ly - 1), str(v), F("sans_sb", 16), PRIMARY,
                  anchor="ra")
        ly += 34


def stacked_columns(img, box, title, cats, series, fmt="{:,.0f}", size=1.0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    totals = [sum(vals[i] for _, vals, _ in series) for i in range(len(cats))]
    vmax = max(totals) or 1
    slot = (x1 - x0) / float(len(cats))
    bw = min(44 * size, slot * 0.44)
    for i in range(5):
        gy = y1 - (y1 - y0 - 30 * size) * i / 4.0
        d.line([x0, gy, x1, gy], fill=hexrgb(BORDER), width=1)
        draw_text(img, (x0 - 8 * size, gy - 9 * size),
                  fmt.format(vmax * i / 4.0), F("sans", int(13 * size)),
                  MUTED, anchor="ra")
    for ci, cat in enumerate(cats):
        cx = x0 + slot * (ci + 0.5)
        f, _ = fit_size(cat, "sans_md", int(13 * size), slot - 4 * size,
                        int(8 * size))
        draw_text(img, (cx, y1 - 26 * size), cat, f, MUTED, anchor="ma")
        base = y1 - 30 * size
        for name, vals, color in series:
            v = vals[ci]
            h = (y1 - 30 * size - y0) * v / float(vmax)
            if h > 0:
                d.rectangle([cx - bw / 2.0, base - h, cx + bw / 2.0, base],
                            fill=hexrgb(color))
                base -= h
    lx = x0
    for name, _, color in series:
        d.rectangle([lx, y0 - 22 * size, lx + 16 * size, y0 - 6 * size],
                    fill=hexrgb(color))
        draw_text(img, (lx + 22 * size, y0 - 24 * size), name,
                  F("sans_sb", int(15 * size)), INK)
        lx += 22 * size + text_width(name, F("sans_sb", int(15 * size))) \
            + 26 * size


# ---------------------------------------------------------------------------
# the real data
# ---------------------------------------------------------------------------
def get_model():
    """The demo business, with every aggregate the screens need."""
    return Demo()


def kpi_card(img, x, y, w, label, value, color, value_size=40,
             label_size=15, h_label=34, h_value=76, pct=False):
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + w, y + h_label], 6, fill=hexrgb(COLORS[color]))
    f, _ = fit_size(label, "sans_sb", label_size, w - 16, 9)
    draw_text(img, (x + w / 2.0, y + (h_label - f.size) / 2.0 - 1), label, f,
              WHITE, anchor="ma")
    rrect(d, [x, y + h_label, x + w, y + h_label + h_value], 6,
          fill=hexrgb(CARD), outline=hexrgb(BORDER))
    f, _ = fit_size(value, "display_b", value_size, w - 30, 14)
    draw_text(img, (x + w / 2.0, y + h_label + (h_value - f.size) / 2.0 - 4),
              value, f, COLORS[color], anchor="ma")
    return y + h_label + h_value
````

---
## `etsy/make_user_guide_santa.py`

*Builds the 12-page illustrated user-guide PDF from real workbook screenshots.* (865 lines)

````python
"""
make_user_guide_santa.py - the illustrated "How to use it" PDF for the
Secret Santa & White Elephant Party Tracker, branded Novality Store.

12 A4 pages at 200 dpi (1654 x 2339 px each), illustrated with REAL
screenshots of the finished workbook (tools/render_preview_santa.py on the
PREMIUM Noel EXAMPLE file, with true emoji glyphs) plus hand-drawn versions
of the dashboard's live charts.

Run:  python3 -m etsy.make_user_guide_santa
Out:  Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf  (repo root)
"""

import io
import os
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy.crochet_lib import (F, check_poly, draw_text, doughnut_chart,
                              fit_size, grouped_columns, hbar_chart, hexrgb,
                              rrect, shadow_paste, text_width, wrap)
from tools.render_preview_santa import render as render_sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PDF = os.path.join(
    ROOT, "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf")
XLSX = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx")
RAW_BANNER = os.path.join(ROOT, "assets", "raw_banner_noel.png")
URL = "Novality Store \u2014 Secret Santa & White Elephant Party Tracker"

# ---------------------------------------------------------------------------
# palette - the workbook's own Noel theme
# ---------------------------------------------------------------------------
PRIMARY = "#8C1D2C"          # holly red
PINE = "#1F5C40"             # pine green
GOLD = "#B98A2E"             # antique gold
CANVAS = "#FBF6EE"
CARD = "#FFFFFF"
ALT = "#FCF8F1"
BORDER = "#E7D9C6"
INK = "#33221E"
MUTED = "#9A8474"
OK = "#1F5C40"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
WHITE = "#FFFFFF"

PW, PH = 1654, 2339             # A4 at 200 dpi
DPI = 200.0
MX = 120                         # side margin
CW = PW - 2 * MX                 # content width 1414
BOTTOM = PH - 170                # footer zone starts here
TOTAL_PAGES = 12

PAGES = []
SW_CROP = 1414


# ---------------------------------------------------------------------------
# screenshots of the real workbook
# ---------------------------------------------------------------------------
def shot(sheet, rows, cols, zoom=1.0):
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        render_sheet(XLSX, sheet, tmp, rows, cols, zoom)
        return Image.open(tmp).convert("RGBA")
    finally:
        os.unlink(tmp)


def browser(screen, width, url=URL):
    """Browser chrome (warm cream) around a screen image. Returns RGBA."""
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    chrome_h = 62
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#F0E9DD"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([26 + i * 34, 22, 44 + i * 34, 40], fill=hexrgb(c))
    pill = [width / 2.0 - 430, 14, width / 2.0 + 430, 48]
    rrect(d, pill, 17, fill=hexrgb(WHITE), outline=hexrgb("#E2D6C2"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 19, 830, 11)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 20, 23),
              "\U0001F512 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#E2D6C2"))
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CBB894"),
                                          width=4)
    return out


def sshot(img, y, screen, width=CW, crop_h=None):
    sc = screen.crop((0, 0, screen.width, crop_h)) if crop_h else screen
    br = browser(sc, width)
    shadow_paste(img, br, (int(PW / 2 - br.width / 2), y), blur=22,
                 alpha=60)
    return y + br.height + 26


def banner_strip(top=True, height=250):
    b = Image.open(RAW_BANNER).convert("RGB")
    crop = b.crop((0, 0, 1600, 300)) if top else \
        b.crop((0, 640 - 300, 1600, 640))
    return crop.resize((PW, height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# page helpers
# ---------------------------------------------------------------------------
def new_page():
    return Image.new("RGBA", (PW, PH), hexrgb(CANVAS))


def finish_page(img, n, titled=True):
    assert n <= TOTAL_PAGES
    d = ImageDraw.Draw(img)
    if titled:
        d.line([MX, PH - 128, PW - MX, PH - 128], fill=hexrgb(BORDER),
               width=2)
        draw_text(img, (MX, PH - 104),
                  "Secret Santa & White Elephant Party Tracker \u2014 "
                  "User Guide", F("sans_md", 22), MUTED)
        draw_text(img, (PW - MX, PH - 104), f"Page {n} of {TOTAL_PAGES}",
                  F("sans_sb", 22), PRIMARY, anchor="ra")
        draw_text(img, (PW / 2.0, PH - 104), "\u00A9 Novality Store",
                  F("sans_b", 22), PRIMARY, anchor="ma")
    PAGES.append(img)
    return img


def kicker(cv, cx, y, text, color=PRIMARY, size=24, track=9):
    d = ImageDraw.Draw(cv)
    f = F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size * 2.1


def h1(img, y, kick, title, size=76, color=PRIMARY):
    y = kicker(img, PW / 2.0, y, kick, GOLD)
    f, _ = fit_size(title, "display_xb", size, CW, 30)
    draw_text(img, (PW / 2.0, y), title, f, color, anchor="ma")
    return y + int(f.size * 1.42)


def h2(img, y, text, color=PRIMARY, size=40, x=MX):
    d = ImageDraw.Draw(img)
    f = F("serif_b", size)
    d.rectangle([x, y + 4, x + 12, y + size + 4], fill=hexrgb(color))
    draw_text(img, (x + 32, y), text, f, color)
    return y + size + 26


def para(img, y, text, size=27, color=INK, x=MX, w=CW, lead=1.55):
    f = F("sans_md", size)
    for line in wrap(text, f, w):
        draw_text(img, (x, y), line, f, color)
        y += int(size * lead)
    return y + 8


def bullets(img, y, items, size=25, x=MX, w=CW, color=PINE, lead=1.5,
            gap=12, check=True):
    d = ImageDraw.Draw(img)
    for it in items:
        f = F("sans_md", size)
        lines = wrap(it, f, w - 56)
        first = True
        for ln in lines:
            if first and check:
                check_poly(d, x + 14, y + size * 0.62, size * 0.95,
                           color, max(3, int(size * 0.16)))
            elif first:
                d.ellipse([x + 8, y + size * 0.35, x + 20,
                           y + size * 0.35 + 12], fill=hexrgb(color))
            draw_text(img, (x + 48, y), ln, f, INK)
            y += int(size * lead)
            first = False
        y += gap
    return y


def steps(img, y, items, size=26, x=MX, w=CW, r=27):
    for i, (title, body) in enumerate(items, 1):
        d = ImageDraw.Draw(img)
        cy = y + r + 4
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=hexrgb(PRIMARY))
        draw_text(img, (x + r, cy - 19), str(i), F("display_b", 34),
                  WHITE, anchor="ma")
        tx = x + 2 * r + 26
        draw_text(img, (tx, y), title, F("sans_b", size), PRIMARY)
        yy = y + size + 8
        f = F("sans_md", size - 2)
        for ln in wrap(body, f, w - (2 * r + 26)):
            draw_text(img, (tx, yy), ln, f, INK)
            yy += int((size - 2) * 1.45)
        y = max(yy, cy + r + 10) + 16
    return y


def note_card(img, y, emoji, title, lines, color, h=None, size=24,
              x=MX, w=CW):
    pad = 30
    f = F("sans_md", size)
    wrapped = []
    for ln in lines:
        wrapped.extend(wrap(ln, f, w - 2 * pad - 40))
    hh = h or (76 + len(wrapped) * int(size * 1.5) + 26)
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + w, y + hh], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [x, y, x + w, y + 62], 16, fill=hexrgb(color))
    d.rectangle([x, y + 31, x + w, y + 62], fill=hexrgb(color))
    draw_text(img, (x + 26, y + 14), f"{emoji} {title}",
              F("serif_b", 30), WHITE)
    yy = y + 84
    for ln in wrapped:
        draw_text(img, (x + pad, yy), ln, f, INK)
        yy += int(size * 1.5)
    return y + hh


def qa_page(img, n, y_last, label):
    assert y_last <= BOTTOM, f"page {n} ({label}) overflows: {y_last} > " \
        f"{BOTTOM}"


def chip(img, x, y, text, fg, bg, size=24, pad=22):
    d = ImageDraw.Draw(img)
    f = F("sans_sb", size)
    w = text_width(text, f) + 2 * pad
    rrect(d, [x, y, x + w, y + size + 26], (size + 26) / 2.0,
          fill=hexrgb(bg))
    draw_text(img, (x + pad, y + 12), text, f, fg)
    return x + w + 18


# ---------------------------------------------------------------------------
# demo data for the chart figures
# ---------------------------------------------------------------------------
from santa_tracker import config as SC        # noqa: E402
from santa_tracker.demo import Demo           # noqa: E402

m = Demo()


# ---------------------------------------------------------------------------
# page 1 - cover
# ---------------------------------------------------------------------------
def p01():
    img = new_page()
    img.paste(banner_strip(True, 250), (0, 0))
    y = 300
    y = kicker(img, PW / 2.0, y, "NOVALITY STORE PRESENTS", GOLD, 26, 12)
    f, _ = fit_size("Secret Santa & White Elephant",
                    "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2.0, y), "Secret Santa & White Elephant", f,
              PRIMARY, anchor="ma")
    y += int(f.size * 1.25)
    f, _ = fit_size("Party Tracker", "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2.0, y), "Party Tracker", f, PINE, anchor="ma")
    y += int(f.size * 1.5)
    y = kicker(img, PW / 2.0, y, "THE ILLUSTRATED USER GUIDE", MUTED,
               22, 10)

    # feature chips
    x = PW / 2.0
    items = [("12 linked tabs", PRIMARY, "#F5E1E2"),
             ("2 editions", PINE, "#E1EDE5"),
             ("2 colour themes", GOLD, "#F6EDD8"),
             ("Excel & Google Sheets", INFO, "#E5E9F4")]
    fs = F("sans_sb", 24)
    total = sum(text_width(t, fs) + 44 for t, _, _ in items) + \
        18 * (len(items) - 1)
    cx = x - total / 2.0
    for t, fg, bg in items:
        cx = chip(img, cx, y, t, fg, bg)
    y += 76

    y = sshot(img, y, shot("\U0001F3E0 Dashboard", (1, 42), (1, 14)),
              width=CW)

    y = para(img, y,
             "Plan the whole festive season in one file: guests, the draw, "
             "exclusions, budgets, wishlists, the white elephant game and "
             "printable cards - all wired together so the dashboard "
             "updates itself.",
             size=26, x=MX + 60, w=CW - 120)
    img.paste(banner_strip(False, 190), (0, PH - 190))
    qa_page(img, 1, y, "cover")
    finish_page(img, 1)


# ---------------------------------------------------------------------------
# page 2 - what you get
# ---------------------------------------------------------------------------
def p02():
    img = new_page()
    y = 110
    y = h1(img, y, "YOUR DOWNLOAD", "What's in the box")

    y = h2(img, y, "Six workbooks")
    from etsy.crochet_lib import draw_table
    rows = [
        ["PREMIUM Noel / Arctic", "The full 12-tab tracker, blank and "
         "ready for your party"],
        ["PREMIUM EXAMPLE", "The same file filled with a demo party - "
         "peek at it first"],
        ["BASIC Noel / Arctic", "Guests, draw and budgets - the lean "
         "7-tab edition"],
        ["BASIC EXAMPLE", "The demo party in BASIC form"],
    ]
    from etsy.crochet_lib import draw_table as _dt
    _dt(img, MX, y, [430, 950 - 6],
        ["File", "What it is"],
        [[r[0], r[1]] for r in rows], row_h=64, hdr_h=54, size=19,
        hdr_size=17)
    y += 54 + 64 * len(rows) + 30

    y = h2(img, y, "PREMIUM or BASIC?")
    rows = [
        ["Guest list + RSVP", "yes", "yes"],
        ["Automatic Secret Santa draw", "yes", "yes"],
        ["Budget tracker", "yes", "yes"],
        ["Exclusions & house rules", "yes", "-"],
        ["Wishlists", "yes", "-"],
        ["White Elephant game board", "yes", "-"],
        ["Game history + live stats", "yes", "-"],
        ["Printable Santa cards", "yes", "-"],
    ]
    _dt(img, MX, y, [814, 300, 300 - 6],
        ["Feature", "PREMIUM", "BASIC"],
        rows, row_h=50, hdr_h=50, size=18, hdr_size=17)
    y += 50 + 50 * len(rows) + 26

    y = h2(img, y, "Where it works")
    y = bullets(img, y, [
        "Excel 2016 or later, Microsoft 365 - everything is native Excel "
        "(formulas, dropdowns, conditional formatting, charts).",
        "Google Sheets - upload the .xlsx to Drive and open with Sheets; "
        "the formulas translate automatically.",
        "Apple Numbers - drag the file onto Numbers; charts may need a "
        "small nudge, everything else converts cleanly.",
    ])
    y = note_card(img, y, "\U0001F512", "The maths is locked (on purpose)",
                  ["Every formula cell is protected so a stray keystroke "
                   "cannot break the tracker. Your typing cells - the "
                   "cream ones - stay open. Need to unlock something? The "
                   "Start Here tab inside the workbook explains how.",
                   "The EXAMPLE files are just for looking: start your "
                   "real party in a blank file."], PINE)
    qa_page(img, 2, y, "what you get")
    finish_page(img, 2)


# ---------------------------------------------------------------------------
# page 3 - settings
# ---------------------------------------------------------------------------
def p03():
    img = new_page()
    y = 100
    y = h1(img, y, "FIVE MINUTES, ONCE", "Set up your party")

    y = steps(img, y, [
        ("Open a blank PREMIUM file",
         "Start with Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel."
         "xlsx (or Arctic - same tracker, different colours)."),
        ("Go to the Settings tab",
         "Type your party name, date, host and location. The dashboard "
         "headline and the days-to-go counter follow instantly."),
        ("Set the gift budget",
         "Budget min and max per person (for example 20 - 35). Every "
         "budget row and the dashboard total use these numbers."),
        ("Pick a currency",
         "The currency symbol drives every money figure in the file."),
        ("Choose a draw seed",
         "Any whole number. The seed shuffles the draw - same seed, same "
         "draw; new seed, brand new draw."),
        ("Save the message",
         "The party message appears on the dashboard banner. Done - the "
         "tracker is ready for guests."),
    ])

    y = sshot(img, y,
              shot("\u2699\uFE0F Settings & Instructions", (1, 26), (1, 8)),
              width=CW)
    qa_page(img, 3, y, "settings")
    finish_page(img, 3)


# ---------------------------------------------------------------------------
# page 4 - participants
# ---------------------------------------------------------------------------
def p04():
    img = new_page()
    y = 100
    y = h1(img, y, "THE GUEST LIST", "Add your guests")

    y = para(img, y,
             "One row per guest on the Participants tab. Everything else "
             "in the workbook - the draw, the budget, the white elephant "
             "game - reads from this list, so add people here first.")

    y = sshot(img, y, shot("\U0001F465 Participants", (1, 22), (1, 10)),
              width=CW)

    y = h2(img, y, "The columns that matter")
    y = bullets(img, y, [
        "Name - first name plus surname initial works best for the "
        "printable cards.",
        "RSVP - a dropdown: Yes / Maybe / No. The chips up top count "
         "them live.",
        "Household & team - only used by the exclusion rules (PREMIUM). "
        "Guests in the same household never draw each other when the "
        "couple rule is on.",
        "Diet notes & gift status - free text plus a status dropdown "
        "(Not started, Gift purchased, Wrapped, Complete) that feeds the "
        "readiness chart.",
    ])
    y = note_card(img, y, "\u2705", "Rows you don't need",
                  ["Twelve rows are pre-formatted; blank rows simply stay "
                   "blank everywhere - the draw skips them and the "
                   "dashboard ignores them."], GOLD)
    qa_page(img, 4, y, "participants")
    finish_page(img, 4)


# ---------------------------------------------------------------------------
# page 5 - the draw
# ---------------------------------------------------------------------------
def p05():
    img = new_page()
    y = 100
    y = h1(img, y, "NO HAT, NO SLIPS", "Run the Secret Santa draw")

    y = para(img, y,
             "The draw tab assigns every guest exactly one recipient - no "
             "one draws themselves, and no pair repeats. The shuffle comes "
             "from your draw seed, so it is reproducible: change the seed "
             "on Settings and the whole draw reshuffles.")

    y = sshot(img, y, shot("\U0001F385 Secret Santa Draw", (1, 21), (1, 7)),
              width=1300)

    y = h2(img, y, "Reading the tab")
    y = bullets(img, y, [
        "Every filled guest row shows the drawn recipient plus a flag "
        "column - \u2705 OK means the pair passes every rule you armed.",
        "A warning flag means the pair brushes a rule (for example the "
        "same household). Change the seed for a clean re-draw, or type a "
        "name into the override column to fix a single pair by hand.",
        "The status chip shows when the draw is final and locked.",
        "The print button in your spreadsheet prints just the draw area - "
        "handy for the organiser's eyes only.",
    ])
    qa_page(img, 5, y, "draw")
    finish_page(img, 5)


# ---------------------------------------------------------------------------
# page 6 - rules
# ---------------------------------------------------------------------------
def p06():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Exclusions & house rules")

    y = para(img, y,
             "The Exclusions & Rules tab is where you tell the draw what "
             "is allowed. Flip a toggle to On and the draw respects it "
             "instantly.")

    y = sshot(img, y, shot("\U0001F6AB Exclusions & Rules", (1, 24),
                           (1, 13)), width=CW)

    y = h2(img, y, "The four levers")
    y = steps(img, y, [
        ("Household rule", "On: nobody draws someone in the same "
         "household (the Household column on Participants)."),
        ("Team rule", "On: work teams never draw each other - set the "
         "Team column first."),
        ("Last-year rule", "On: type last year's pairs into the draw's "
         "history column and they will not repeat. Keep it Off if this "
         "is your first year."),
        ("Custom no-pair list", "Any other pair that must never happen - "
         "feuding cousins, identical twins, the hosts. Two columns, as "
         "many rows as you like."),
    ])
    y = note_card(img, y, "\U0001F3AF", "The scoreboards up top",
                  ["Rules armed counts your active rules and custom pairs; "
                   "draw violations should read 0 after a fresh draw - if "
                   "not, nudge the seed once more."], BAD)
    qa_page(img, 6, y, "rules")
    finish_page(img, 6)


# ---------------------------------------------------------------------------
# page 7 - budget
# ---------------------------------------------------------------------------
def p07():
    img = new_page()
    y = 100
    y = h1(img, y, "MONEY, KEPT HONEST", "The budget tracker")

    y = para(img, y,
             "One row per giver, mirroring the draw. The min and max "
             "columns come straight from Settings, so a budget change "
             "updates every row at once.")

    y = sshot(img, y, shot("\U0001F4B0 Budget Tracker", (1, 21), (1, 9)),
              width=CW)

    y = h2(img, y, "How to use it")
    y = bullets(img, y, [
        "Actual spent - type what a gift really cost; the status column "
        "colours itself: under budget, within, or over.",
        "Receipt - tick \u2713 when the receipt is filed; the chip up "
        "top counts them.",
        "Reference & notes - order numbers, links, where the gift is "
        "hiding.",
        "The dashboard totals (total budget, actual spend, average gift "
        "cost) recalculate the moment you type.",
    ])
    y = note_card(img, y, "\U0001F6A8", "Over-budget alarm",
                  ["The over-budget chip on the Budget tab counts rows "
                   "above the max - glance at it before you buy, not "
                   "after."], WARN)
    qa_page(img, 7, y, "budget")
    finish_page(img, 7)


# ---------------------------------------------------------------------------
# page 8 - wishlists
# ---------------------------------------------------------------------------
def p08():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Wishlists that avoid doubles")

    y = para(img, y,
             "Guests jot down a few wishes each; whoever draws them can "
             "claim an idea with a tick so nobody buys the same thing "
             "twice.")

    y = sshot(img, y, shot("\U0001F381 Wishlists", (1, 21), (1, 7)),
              width=1300)

    y = h2(img, y, "The trick is the claim column")
    y = bullets(img, y, [
        "Guest, wish and a category (Must-love, Nice-to-have, Idea, "
        "Please-not) - a dropdown keeps it tidy.",
        "Claimed \u2713 marks an idea as taken; the chips count open "
        "must-loves so the important wishes never sit unclaimed.",
        "Price hint and link columns make remote shopping painless.",
        "Sort or filter the table by guest when you are doing the "
        "buying.",
    ])
    y = note_card(img, y, "\U0001F4B0", "Price hints keep budgets sane",
                  ["Wishes carry an optional price hint - when a guest "
                   "logs one, it lands right next to the budget range "
                   "from Settings, so the buyer instantly sees which "
                   "wishes fit the agreed budget and which need a group "
                   "top-up."], GOLD)
    qa_page(img, 8, y, "wishlists")
    finish_page(img, 8)


# ---------------------------------------------------------------------------
# page 9 - white elephant
# ---------------------------------------------------------------------------
def p09():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "The White Elephant board")

    y = para(img, y,
             "Ten gift slots, one row each. Seats are numbered "
             "automatically in a random-but-stable order, and the board "
             "tracks who holds what as the game unfolds.")

    y = sshot(img, y, shot("\U0001F3B2 White Elephant", (1, 21), (1, 12)),
              width=CW)

    y = h2(img, y, "Statuses, decoded")
    y = bullets(img, y, [
        "\U0001F381 Available - still on the table. \U0001F932 Held - "
        "someone owns it, for now. \U0001F504 Stolen - taken off someone; "
        "a stolen gift usually goes Final after the steal limit. "
        "\U0001F512 Final - locked, out of the game.",
        "The Now chip tells you exactly whose turn it is (seat number "
        "and name) based on the turns you have logged.",
        "The steals column counts thefts per gift - the dashboard chart "
        "turns it into instant drama.",
        "Max steals comes from Settings; when a gift hits the limit it "
        "locks itself Final.",
    ])
    y = note_card(img, y, "\U0001F4DD", "You never edit the board itself",
                  ["Holder, thief and status columns are all formulas "
                   "driven by the Game History tab on the next page - log "
                   "the turns there and this board plays itself. Only the "
                   "gift description and value columns are yours to "
                   "type."], INFO)
    qa_page(img, 9, y, "white elephant")
    finish_page(img, 9)


# ---------------------------------------------------------------------------
# page 10 - history + cards
# ---------------------------------------------------------------------------
def p10():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Game history & Santa cards")

    y = para(img, y,
             "Log every turn on the Game History tab - seat number, "
             "player, Pick / Steal / Pass, which gift - and the board, "
             "the Now chip and the dashboard all follow along by "
             "themselves.")

    y = sshot(img, y, shot("\U0001F504 Game History", (1, 16), (1, 6)),
              width=880)
    y = sshot(img, y, shot("\U0001F39F\uFE0F Santa Cards", (1, 19), (1, 9)),
              width=CW)

    y = para(img, y,
             "The Santa Cards tab lays out fold-and-cut cards: giver on "
             "the outside, recipient inside - the secret survives the "
             "handout. Print, cut, fold, deal.")
    qa_page(img, 10, y, "history + cards")
    finish_page(img, 10)


# ---------------------------------------------------------------------------
# page 11 - dashboard
# ---------------------------------------------------------------------------
def p11():
    img = new_page()
    y = 100
    y = h1(img, y, "ONE GLANCE", "The command centre")

    y = sshot(img, y, shot("\U0001F3E0 Dashboard", (1, 40), (1, 14)),
              width=CW)

    y = para(img, y,
             "Twelve KPI cards, four live charts, progress bars for "
             "purchases, wrapping and completion - every figure on this "
             "page is a formula, so it is always current. These are the "
             "same charts, redrawn from the demo party:")

    # four chart figures in a 2 x 2 grid, mirroring the real dashboard
    bw = (CW - 40) // 2
    bh = 300
    gx1, gx2 = MX, MX + bw + 40
    gy = y + 10

    givers = m.assign[:12]
    hbar_chart(img, (gx1, gy, gx1 + bw, gy + bh),
               "Actual spend per giver",
               list(zip(givers, m.spent)), color=PRIMARY, fmt="${:,.0f}",
               size=0.85)

    from collections import Counter
    stc = Counter(p["status"] for p in m.people)
    doughnut_chart(img, (gx2, gy, gx2 + bw, gy + bh),
                   "Gift readiness mix",
                   [(SC.ST_NOT, stc.get(SC.ST_NOT, 0), BAD),
                    (SC.ST_BOUGHT, stc.get(SC.ST_BOUGHT, 0), WARN),
                    (SC.ST_WRAPPED, stc.get(SC.ST_WRAPPED, 0), INFO),
                    (SC.ST_DONE, stc.get(SC.ST_DONE, 0), OK)],
                   size=0.85, center_word="guests")

    gy += bh + 34
    bygift = sorted(m.we, key=lambda r: r["giftnum"])
    hbar_chart(img, (gx1, gy, gx1 + bw, gy + bh), "Steals per gift",
               [(f"gift #{r['giftnum']}", r["steals"]) for r in bygift],
               color=PINE, fmt="{:,.0f}", size=0.85)

    grouped_columns(img, (gx2, gy, gx2 + bw, gy + bh),
                    "Gift values brought",
                    [f"#{r['giftnum']}" for r in bygift],
                    [("Value", [r["value"] for r in bygift], GOLD)],
                    fmt="${:,.0f}", size=0.85)

    y = gy + bh + 10
    qa_page(img, 11, y, "dashboard")
    finish_page(img, 11)


# ---------------------------------------------------------------------------
# page 12 - tips + support
# ---------------------------------------------------------------------------
def p12():
    img = new_page()
    y = 100
    y = h1(img, y, "FROM PARTY ANIMALS", "Ten tips for a smooth night")

    tips = [
        "Add every guest before you draw - new rows after the draw need "
        "a seed nudge.",
        "Draw early: the moment pairs exist, budgets and wishlists get "
        "useful.",
        "Change the seed, not the names, when a pair brushes a rule.",
        "Keep the couple rule On unless your crowd loves chaos.",
        "Log white elephant turns as they happen - the Now chip keeps "
        "arguments to zero.",
        "Photograph receipts the same night; the receipt column will "
        "thank you in January.",
        "Print Santa cards on stiff paper; they fold in half by "
        "themselves.",
        "Set Max steals to 2 or 3 - unlimited stealing is how friendships "
        "end.",
        "Duplicate the file per year: last year's pairs then feed the "
        "last-year rule.",
        "Open the dashboard on a tablet by the door; it doubles as the "
        "scoreboard.",
    ]
    f = F("sans_md", 24)
    col_w = (CW - 60) // 2
    for i, tip in enumerate(tips):
        col = i % 2
        row = i // 2
        tx = MX + col * (col_w + 60)
        ty = y + row * 128
        d = ImageDraw.Draw(img)
        d.ellipse([tx, ty + 4, tx + 44, ty + 48], fill=hexrgb(GOLD))
        draw_text(img, (tx + 22, ty + 10), str(i + 1),
                  F("display_b", 26), WHITE, anchor="ma")
        yy = ty
        for ln in wrap(tip, f, col_w - 70):
            draw_text(img, (tx + 62, yy), ln, f, INK)
            yy += 34
    y += 5 * 128 + 16

    y = h2(img, y, "Quick answers")
    qa = [
        ("Google Sheets?", "Yes - upload to Drive and open with Sheets. "
         "The dropdowns, formulas and conditional formatting translate "
         "automatically."),
        ("More than 12 guests?", "The pre-formatted rows cover a big "
         "party; blank rows are simply ignored, and you can insert more "
         "rows inside the table area."),
        ("Need to unlock a cell?", "The Start Here tab inside the "
         "workbook explains unlocking - you will not need it for normal "
         "use."),
    ]
    for q, a in qa:
        draw_text(img, (MX, y), q, F("sans_b", 24), PRIMARY)
        y += 34
        f2 = F("sans_md", 23)
        for ln in wrap(a, f2, CW - 20):
            draw_text(img, (MX, y), ln, f2, INK)
            y += 32
        y += 10

    y = note_card(img, y, "\U0001F9ED", "Support",
                  ["Questions, wishes or a stubborn formula? Message "
                   "Novality Store through the shop you bought from and "
                   "you will get a human answer.",
                   "Your purchase is a personal licence for your own "
                   "parties - please do not resell or share the files."],
                  PINE)
    qa_page(img, 12, y, "tips")
    finish_page(img, 12)


# ---------------------------------------------------------------------------
# PDF writer (JPEG pages in a hand-rolled PDF 1.4 container)
# ---------------------------------------------------------------------------
def write_pdf(pages, path, title, author):
    jpgs = []
    for im in pages:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=92, optimize=True,
                               subsampling=1)
        jpgs.append((buf.getvalue(), im.width, im.height))

    n = len(jpgs)
    objs = {}

    def put(oid, body):
        objs[oid] = body

    kids = " ".join(f"{3 + 3 * i} 0 R" for i in range(n))
    put(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    put(2, f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, (data, w, h) in enumerate(jpgs):
        wpt = w * 72.0 / DPI
        hpt = h * 72.0 / DPI
        put(3 + 3 * i,
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {wpt:.2f} "
             f"{hpt:.2f}] /Resources << /XObject << /Im{i} {5 + 3 * i} 0 R "
             f">> >> /Contents {4 + 3 * i} 0 R >>").encode())
        content = f"q {wpt:.2f} 0 0 {hpt:.2f} 0 0 cm /Im{i} Do Q".encode()
        put(4 + 3 * i,
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" +
            content + b"\nendstream")
        put(5 + 3 * i,
            (f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
             f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter "
             f"/DCTDecode /Length {len(data)} >>").encode() +
            b"\nstream\n" + data + b"\nendstream")
    esc = lambda s: s.replace("\\", r"\\").replace("(", r"\(").replace(
        ")", r"\)")
    put(3 + 3 * n, (f"<< /Title ({esc(title)}) /Author ({esc(author)}) "
                    f"/Creator (Novality Store) >>").encode())

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for oid in sorted(objs):
        offsets[oid] = out.tell()
        out.write(f"{oid} 0 obj\n".encode())
        out.write(objs[oid])
        out.write(b"\nendobj\n")
    xref_pos = out.tell()
    maxoid = max(objs)
    out.write(f"xref\n0 {maxoid + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for oid in range(1, maxoid + 1):
        out.write(f"{offsets.get(oid, 0):010d} 00000 n \n".encode())
    out.write((f"trailer\n<< /Size {maxoid + 1} /Root 1 0 R "
               f"/Info {3 + 3 * n} 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
               ).encode())
    with open(path, "wb") as fh:
        fh.write(out.getvalue())
    return os.path.getsize(path)


# ---------------------------------------------------------------------------
def main():
    for fn in (p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12):
        fn()
    assert len(PAGES) == TOTAL_PAGES, len(PAGES)
    size = write_pdf(PAGES, OUT_PDF,
                     "Secret Santa & White Elephant Party Tracker \u2014 "
                     "User Guide", "Novality Store")
    print(f"built {os.path.basename(OUT_PDF)}")
    print(f"  pages : {len(PAGES)}  (A4, {int(DPI)} dpi)")
    print(f"  size  : {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
````

---
## `etsy/make_kit_zip_santa.py`

*Bundles this complete kit zip.* (341 lines)

````python
"""
make_kit_zip_santa.py - bundle the complete Novality Store Secret Santa &
White Elephant Party Tracker kit into ONE zip:

  products/   6 Excel workbooks (PREMIUM + BASIC, Noel + Arctic, EXAMPLE)
  the 12-page illustrated user-guide PDF
  source      santa_tracker package, entry point, QA tools, banner art
  SOURCE_CODE.md   every Python file embedded in one Markdown document
  README.md   master guide + rebuild instructions

Run from the repo root:   python3 -m etsy.make_kit_zip_santa
"""

import os
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT.zip"
PREFIX = "Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT"

DESCRIPTIONS = {
    "secret_santa_party_tracker.py":
        "Entry point / CLI - builds every product workbook "
        "(--all --outdir products/ --protect premium).",
    "santa_tracker/__init__.py": "Package marker.",
    "santa_tracker/config.py":
        "All constants: tabs, editions, statuses, columns, KPI map, "
        "capacities - the single source of truth for every tab.",
    "santa_tracker/theme.py":
        "Noel & Arctic colour themes (tab colours, series, soft tints).",
    "santa_tracker/styles.py":
        "xlsxwriter format factory - every cell style used in the "
        "workbooks.",
    "santa_tracker/demo.py":
        "The demo party: people, draw, budgets, wishlists, white "
        "elephant game, history + all aggregations (agg) for the "
        "dashboard, KPI caches and guide images.",
    "santa_tracker/workbook.py":
        "Workbook bootstrap: sheet order, tab colours, print setup, "
        "protection plumbing, EXAMPLE vs blank modes.",
    "santa_tracker/book.py":
        "Book writer: title blocks, KPI cards, bars, charts, conditional "
        "formats, data validation, sheet protection + (c) Novality Store "
        "footer.",
    "santa_tracker/sheets/__init__.py": "Sheet modules.",
    "santa_tracker/sheets/common.py":
        "Shared sheet helpers: headers, chips, dropdowns, tables, "
        "footers - plus the chip cache label fix.",
    "santa_tracker/sheets/data.py":
        "Hidden _Data engine room: KPI formulas, status pools, lists.",
    "santa_tracker/sheets/setup.py":
        "Settings & Instructions tab: party basics, seeds, budget range.",
    "santa_tracker/sheets/dashboard.py":
        "Dashboard tab: hero, 12 KPI cards, progress bars, 4 live "
        "charts.",
    "santa_tracker/sheets/participants.py": "Participants tab.",
    "santa_tracker/sheets/draw.py":
        "Secret Santa Draw tab: seed-driven shuffle, flags, overrides.",
    "santa_tracker/sheets/rules.py":
        "Exclusions & Rules tab (PREMIUM): house rules + custom pairs.",
    "santa_tracker/sheets/budget.py": "Budget Tracker tab.",
    "santa_tracker/sheets/wishlists.py": "Wishlists tab (PREMIUM).",
    "santa_tracker/sheets/we.py":
        "White Elephant tab (PREMIUM): seats, gifts, holders, statuses.",
    "santa_tracker/sheets/history.py":
        "Game History tab (PREMIUM): turn log that drives the board.",
    "santa_tracker/sheets/cards.py":
        "Santa Cards tab (PREMIUM): fold-and-cut giver cards.",
    "santa_tracker/sheets/guide.py":
        "Start Here guide tab with watercolour banner cover.",
    "tools/verify_santa.py":
        "QA: structural audit - sheet refs, modern functions, hidden "
        "writes.",
    "tools/calc_check_santa.py":
        "QA: recalculates the whole workbook with the formulas engine "
        "and diffs every cached value.",
    "tools/layout_check_santa.py":
        "QA: finds clipped or overflowing text before buyers do.",
    "tools/render_preview_santa.py":
        "QA: renders any tab to PNG (real emoji glyphs) - powers the "
        "user-guide screenshots.",
    "tools/make_banner_alpha_santa.py":
        "Turns the generated banner art into the transparent PNG the "
        "workbook embeds.",
    "etsy/__init__.py": "Package marker.",
    "etsy/crochet_lib.py":
        "Shared PIL rendering engine (emoji-aware text, fonts, tables, "
        "pills, charts) - used to draw the user guide.",
    "etsy/make_user_guide_santa.py":
        "Builds the 12-page illustrated user-guide PDF from real "
        "workbook screenshots.",
    "etsy/make_kit_zip_santa.py":
        "Bundles this complete kit zip.",
    "etsy/make_listing_images_santa.py":
        "Draws the 15 Etsy listing images (2400x1800 JPEG) from real "
        "workbook screenshots.",
    "etsy/make_listing_zip_santa.py":
        "Bundles the standalone Etsy listing-kit zip (md + 15 images).",
}

SOURCE_FILES = list(DESCRIPTIONS.keys())

KIT_README = """# Secret Santa & White Elephant Party Tracker — COMPLETE KIT
**Novality Store** • bundled {today}

Everything needed to sell, rebuild and extend the Secret Santa & White
Elephant Party Tracker spreadsheet on Etsy, in one folder.

```
Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT/
├── README.md                 <- you are here (master guide)
├── SOURCE_CODE.md            <- every Python file in one Markdown document
├── Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf
│                               <- 12-page illustrated user guide
├── products/                 <- the 6 finished Excel workbooks (ready to sell)
├── etsy/
│   ├── LISTING_KIT_SANTA.md  <- SEO title, 13+7 tags, description, alt texts
│   ├── images_santa/         <- 15 listing images (2400x1800 JPEG, <1 MB)
│   ├── fonts/                <- OFL fonts used to render the guide
│   ├── crochet_lib.py        <- shared image engine (emoji text, charts)
│   ├── make_listing_images_santa.py <- rebuild images: python3 -m etsy.make_listing_images_santa
│   ├── make_user_guide_santa.py   <- rebuild guide: python3 -m etsy.make_user_guide_santa
│   └── make_kit_zip_santa.py      <- rebuild this zip: python3 -m etsy.make_kit_zip_santa
├── secret_santa_party_tracker.py  <- build CLI (entry point)
├── santa_tracker/            <- the spreadsheet generator (8 modules + 14 sheets)
├── tools/                    <- QA suite + banner alpha tool
├── assets/                   <- banner art used by the Start Here tab
└── xlsxwriter/               <- vendored xlsxwriter 3.2.9 (no pip needed)
```

## 1. The product (ready to sell)

| File | What it is |
|------|------------|
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel.xlsx` | Flagship - 12 tabs, 700+ formulas, 4 charts, Noel theme |
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Arctic.xlsx` | Same engine, Arctic theme |
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx` | Filled-in demo of the premium file |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Noel.xlsx` | Basic edition - 7 tabs, ~400 formulas |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Arctic.xlsx` | Basic edition, Arctic theme |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Noel_EXAMPLE.xlsx` | Filled-in demo of the starter file |

- Works in **Excel 2016+ / Microsoft 365 (Win & Mac)** and **Google Sheets**
  (File -> Import -> Upload -> Replace spreadsheet).
- **No macros.** All formula cells are **locked** (password: `premium`) so
  buyers can't break the maths; every input cell is open. The Start Here
  tab documents unlocking for buyers - the PDF guide never mentions the
  password.
- Author/branding: **Novality Store** (baked into file properties, cover
  sheet and every tab footer).

## 2. The Etsy listing

Everything is in **`etsy/LISTING_KIT_SANTA.md`**: title (127 chars), 13
recommended tags + 7 spares, the full description, alt texts for the 15
images, pricing and a publish checklist. Upload
`etsy/images_santa/01_hero.jpg` .. `15_faq.jpg` in order - image 01
becomes the thumbnail.

## 3. The buyer guide

`Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf` is the 12-page
illustrated how-to (real screenshots, chart figures, ten tips, FAQ). Attach
it to the Etsy listing as a supporting PDF or drop it into the digital
download.

## 4. Rebuilding everything from source

Requires Python 3.10+ and Pillow (`pip install pillow`) - xlsxwriter is
vendored, openpyxl is only needed for verification.

```bash
# rebuild all 6 workbooks (formulas locked with password 'premium')
python3 secret_santa_party_tracker.py --all --outdir products/ --protect premium

# QA: structure audit, full recalculation, layout audit
python3 tools/verify_santa.py "products/Secret_Santa_White_Elephant_Tracker_*.xlsx"
python3 tools/calc_check_santa.py products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx
python3 tools/layout_check_santa.py "products/Secret_Santa_White_Elephant_Tracker_*.xlsx"

# rebuild the 15 listing images (needs etsy/fonts/ + products/)
python3 -m etsy.make_listing_images_santa

# rebuild the 12-page user guide
python3 -m etsy.make_user_guide_santa

# re-bundle this kit zip
python3 -m etsy.make_kit_zip_santa
```

See **SOURCE_CODE.md** for the annotated source of every file.

## 5. Licences

- Product workbooks: (c) Novality Store - one party organiser per purchase,
  no resale or redistribution.
- Python source: same repository licence as the original repo.
- Fonts in `etsy/fonts/`: SIL Open Font License (Poppins, Gelasio, Playfair
  Display, Caveat, JetBrains Mono, Noto Color Emoji).
- Vendored xlsxwriter: BSD-2-Clause (John McNamara).
"""


def build_source_md():
    parts = [
        "# Secret Santa & White Elephant Party Tracker — Complete Source "
        "Code\n\n",
        "**Novality Store** • bundled " + date.today().isoformat() + "\n\n",
        "Every Python file of the project in one document, for future "
        "reference.\nRebuild commands are in the kit `README.md`.\n\n"
        "## Contents\n\n",
    ]
    for i, f in enumerate(SOURCE_FILES, 1):
        desc = DESCRIPTIONS[f]
        parts.append(f"{i}. **`{f}`** — {desc}\n")
    parts.append("\n---\n\n")
    for f in SOURCE_FILES:
        path = os.path.join(ROOT, f)
        code = open(path, encoding="utf8").read()
        n_lines = code.count("\n") + 1
        parts.append(f"\n## `{f}`\n\n")
        parts.append(f"*{DESCRIPTIONS[f]}* ({n_lines:,} lines)\n\n")
        parts.append("````python\n" + code.rstrip("\n") +
                     "\n````\n\n")   # 4-backtick fence: code may embed ```
        parts.append("---")
    return "".join(parts)


def add_dir(z, src, arcdir,
            skip_prefixes=(".git", "__pycache__", ".pytest_cache")):
    n = 0
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", ".pytest_cache")]
        for fn in sorted(filenames):
            if fn.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, src)
            z.write(full, os.path.join(arcdir, rel))
            n += 1
    return n


def main():
    out = os.path.join(ROOT, ZIP_NAME)
    source_md = build_source_md()
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        # master README + annotated source
        z.writestr(os.path.join(PREFIX, "README.md"),
                   KIT_README.format(today=date.today().isoformat()))
        z.writestr(os.path.join(PREFIX, "SOURCE_CODE.md"), source_md)
        # products — ONLY the santa workbooks (never the other products)
        for fn in sorted(os.listdir(os.path.join(ROOT, "products"))):
            if fn.startswith("Secret_Santa_White_Elephant_Tracker") and \
                    fn.endswith(".xlsx"):
                z.write(os.path.join(ROOT, "products", fn),
                        os.path.join(PREFIX, "products", fn))
                count += 1
        # guide engine + scripts + fonts
        for fn in ("__init__.py", "crochet_lib.py",
                   "make_user_guide_santa.py", "make_kit_zip_santa.py",
                   "make_listing_images_santa.py",
                   "make_listing_zip_santa.py"):
            z.write(os.path.join(ROOT, "etsy", fn),
                    os.path.join(PREFIX, "etsy", fn))
            count += 1
        count += add_dir(z, os.path.join(ROOT, "etsy", "fonts"),
                         os.path.join(PREFIX, "etsy", "fonts"))
        # Etsy listing kit (md + 15 listing images)
        z.write(os.path.join(ROOT, "etsy", "LISTING_KIT_SANTA.md"),
                os.path.join(PREFIX, "etsy", "LISTING_KIT_SANTA.md"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "etsy", "images_santa"),
                         os.path.join(PREFIX, "etsy", "images_santa"))
        # spreadsheet source
        z.write(os.path.join(ROOT, "secret_santa_party_tracker.py"),
                os.path.join(PREFIX, "secret_santa_party_tracker.py"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "santa_tracker"),
                         os.path.join(PREFIX, "santa_tracker"))
        # QA tools
        for fn in ("verify_santa.py", "calc_check_santa.py",
                   "layout_check_santa.py", "render_preview_santa.py",
                   "make_banner_alpha_santa.py"):
            z.write(os.path.join(ROOT, "tools", fn),
                    os.path.join(PREFIX, "tools", fn))
            count += 1
        # banner art (finished PNGs the workbook embeds + raw sources)
        for fn in ("banner_noel.png", "banner_arctic.png",
                   "raw_banner_noel.png", "raw_banner_arctic.png"):
            z.write(os.path.join(ROOT, "assets", fn),
                    os.path.join(PREFIX, "assets", fn))
            count += 1
        # the illustrated user-guide PDF
        guide = os.path.join(
            ROOT, "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf")
        assert os.path.exists(guide), "build the user guide first"
        z.write(guide, os.path.join(
            PREFIX,
            "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf"))
        count += 1
        # vendored xlsxwriter (no pycache / dist-info)
        count += add_dir(z, os.path.join(ROOT, "xlsxwriter"),
                         os.path.join(PREFIX, "xlsxwriter"))
        total = len(z.namelist())
    # verify
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        assert bad is None, f"corrupt member: {bad}"
        names = z.namelist()
    size = os.path.getsize(out)
    print(f"built {ZIP_NAME}")
    print(f"  members : {total}")
    print(f"  files   : {count}")
    print(f"  size    : {size/1024/1024:.1f} MB")
    print(f"  zip ok  : integrity verified")
    # sanity: every key artifact present, no other-product artifacts leaked
    for must in ("etsy/LISTING_KIT_SANTA.md",
                 "etsy/images_santa/01_hero.jpg",
                 "etsy/images_santa/15_faq.jpg",
                 "products/Secret_Santa_White_Elephant_Tracker_PREMIUM_"
                 "Noel.xlsx",
                 "products/Secret_Santa_White_Elephant_Tracker_BASIC_"
                 "Arctic.xlsx",
                 "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf",
                 "santa_tracker/book.py", "tools/verify_santa.py",
                 "assets/banner_noel.png", "etsy/fonts/NotoColorEmoji.ttf",
                 "SOURCE_CODE.md", "README.md", "xlsxwriter/__init__.py"):
        assert any(n.endswith(must) for n in names), f"missing {must}"
    assert not any(("Crochet" in n) or ("Catering" in n) or
                   ("Christmas_Gift" in n) for n in names), \
        "other-product artifact leaked into santa kit"
    print("  content : all key artifacts present, no other-product files")


if __name__ == "__main__":
    main()
````

---
## `etsy/make_listing_images_santa.py`

*Draws the 15 Etsy listing images (2400x1800 JPEG) from real workbook screenshots.* (726 lines)

````python
"""
make_listing_images_santa.py - the 15 Etsy listing images for the Secret
Santa & White Elephant Party Tracker, branded Novality Store.

2400 x 1800 px (4:3) JPEGs, each under 1 MB, drawn with the shared
crochet_lib design engine in the workbook's own Noel palette and
illustrated with REAL screenshots of the finished workbook
(tools/render_preview_santa.py on the PREMIUM Noel EXAMPLE file).

Run:  python3 -m etsy.make_listing_images_santa
Out:  etsy/images_santa/01_hero.jpg .. 15_faq.jpg
"""

import os
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy.crochet_lib import (F, check_poly, draw_text, fit_size, hexrgb,
                              rrect, shadow_paste, text_width, wrap)
from tools.render_preview_santa import render as render_sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "images_santa")
XLSX = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx")
XLSX_ARCTIC = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Arctic.xlsx")
RAW_BANNER = os.path.join(ROOT, "assets", "raw_banner_noel.png")

W, H = 2400, 1800                     # 4:3 listing image
URL = "novalitystore.etsy.com  \u2022  Secret Santa & White Elephant " \
      "Party Tracker \u2014 Instant Download"
FOOT = "Secret Santa & White Elephant Party Tracker \u2014 Excel & Google " \
       "Sheets  \u2022  Instant Digital Download"

# ---------------------------------------------------------------------------
# palette - the workbook's own Noel theme
# ---------------------------------------------------------------------------
PRIMARY = "#8C1D2C"          # holly red
PINE = "#1F5C40"             # pine green
GOLD = "#B98A2E"             # antique gold
CANVAS = "#FBF6EE"
CARD = "#FFFFFF"
BORDER = "#E7D9C6"
INK = "#33221E"
MUTED = "#9A8474"
OK = "#1F5C40"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
WHITE = "#FFFFFF"
SOFT = {PRIMARY: "#F5E1E2", PINE: "#E1EDE5", GOLD: "#F6EDD8",
        INFO: "#E5E9F4", BAD: "#F7E2E0", WARN: "#FBF0D9", MUTED: "#F0EAE2"}


# ---------------------------------------------------------------------------
# screenshots of the real workbook
# ---------------------------------------------------------------------------
def shot(sheet, rows, cols, path=None, zoom=1.0):
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        render_sheet(path or XLSX, sheet, tmp, rows, cols, zoom)
        return Image.open(tmp).convert("RGBA")
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# frame-level helpers
# ---------------------------------------------------------------------------
def canvas():
    return Image.new("RGBA", (W, H), hexrgb(CANVAS))


def banner_img():
    return Image.open(RAW_BANNER).convert("RGB")


def strip(top=True, height=200):
    b = banner_img()
    crop = b.crop((0, 0, 1600, 300)) if top else \
        b.crop((0, 640 - 300, 1600, 640))
    return crop.resize((W, height), Image.LANCZOS).convert("RGBA")


def kicker(cv, cx, y, text, color=PRIMARY, size=34, track=10):
    d = ImageDraw.Draw(cv)
    f = F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size + 14


def headline(cv, cx, y, text, size=96, color=PRIMARY, spec="display_xb"):
    f, _ = fit_size(text, spec, size, W - 220, 30)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.32)


def subline(cv, cx, y, text, size=34, color=INK, spec="sans_md"):
    f, _ = fit_size(text, spec, size, W - 260, 16)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.7)


def chips_row(cv, cx, y, items, size=26, gap=28):
    """items = [(text, color)] centered row of pills."""
    fs, total = [], 0
    for text, color in items:
        f = F("sans_sb", size)
        w = text_width(text, f) + 48
        fs.append((text, color, f, w))
        total += w
    total += gap * (len(items) - 1)
    x = cx - total / 2.0
    for text, color, f, w in fs:
        d = ImageDraw.Draw(cv)
        rrect(d, [x, y, x + w, y + size + 32], (size + 32) / 2.0,
              fill=hexrgb(SOFT[color]))
        draw_text(cv, (x + 24, y + 15), text, f, color)
        x += w + gap
    return y + size + 32


def browser(screen, width, url=URL):
    """Browser chrome (warm cream) around a screen image. Returns RGBA."""
    chrome_h = 68
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#F0E9DD"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([30 + i * 38, 24, 48 + i * 38, 42], fill=hexrgb(c))
    pill = [width / 2.0 - 500, 15, width / 2.0 + 500, 53]
    rrect(d, pill, 19, fill=hexrgb(WHITE), outline=hexrgb("#E2D6C2"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 21, 980, 12)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 24, 26),
              "\U0001F512 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#E2D6C2"))
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CBB894"),
                                          width=4)
    return out


def sshot(cv, x, y, screen, width, url=URL):
    br = browser(screen, width, url)
    shadow_paste(cv, br, (int(x - br.width / 2), y), blur=24, alpha=60)
    return br.height


def side_card(cv, x, y, w, h, emoji, title, color, lines=None, body_pad=26,
              title_size=34, body_size=25):
    d = ImageDraw.Draw(cv)
    rrect(d, [x, y, x + w, y + h], 18, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    d.rectangle([x, y, x + 14, y + h], fill=hexrgb(color))
    draw_text(cv, (x + 34, y + 22), f"{emoji}  {title}",
              F("serif_b", title_size), color)
    yy = y + 22 + title_size + 18
    if lines:
        f = F("sans_md", body_size)
        for ln in lines:
            for j, part in enumerate(wrap(ln, f, w - 2 * body_pad - 30)):
                if j == 0:
                    check_poly(d, x + body_pad + 9, yy + body_size * 0.55,
                               body_size * 0.85, color, 3)
                draw_text(cv, (x + body_pad + 30, yy), part, f, INK)
                yy += int(body_size * 1.45)
            yy += 8
    return y + h


def num_circle(cv, cx, cy, n, r=56):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(PRIMARY))
    draw_text(cv, (cx, cy - 34), str(n), F("display_b", 52), WHITE,
              anchor="ma")


def arrow_right(cv, x, y, size=54, color=GOLD):
    d = ImageDraw.Draw(cv)
    d.line([x, y, x + size, y], fill=hexrgb(color), width=8)
    d.line([x + size - 18, y - 16, x + size, y], fill=hexrgb(color), width=8)
    d.line([x + size - 18, y + 16, x + size, y], fill=hexrgb(color), width=8)


def footer(cv, note=None):
    d = ImageDraw.Draw(cv)
    d.line([90, H - 96, W - 90, H - 96], fill=hexrgb(BORDER), width=2)
    draw_text(cv, (90, H - 72), note or FOOT, F("sans_md", 26), MUTED)
    draw_text(cv, (W - 90, H - 72), "\u00A9 Novality Store",
              F("sans_b", 26), PRIMARY, anchor="ra")


def hand_note(cv, x, y, text, size=44, color=GOLD, anchor="la"):
    f = F("hand", size)
    for i, ln in enumerate(text.split("\n")):
        draw_text(cv, (x, y + i * int(size * 1.15)), ln, f, color,
                  anchor=anchor)


def save(cv, name):
    os.makedirs(OUT, exist_ok=True)
    rgb = cv.convert("RGB")
    assert rgb.size == (W, H), f"{name}: wrong size {rgb.size}"
    path = os.path.join(OUT, name + ".jpg")
    for q in (90, 87, 84, 80, 76):
        rgb.save(path, "JPEG", quality=q, optimize=True)
        if os.path.getsize(path) <= 1024 * 1024:
            break
    kb = os.path.getsize(path) // 1024
    print(f"  {name}.jpg  {kb} KB")
    assert kb <= 1024, f"{name} exceeds 1 MB"


# ---------------------------------------------------------------------------
# 01 - hero
# ---------------------------------------------------------------------------
def img01():
    cv = canvas()
    cv.alpha_composite(strip(True, 200), (0, 0))
    y = kicker(cv, W / 2, 236, "NOVALITY STORE  \u2022  PREMIUM EDITION")
    f1, _ = fit_size("Secret Santa & White Elephant", "display_xb", 96,
                     W - 220, 40)
    draw_text(cv, (W / 2, y), "Secret Santa & White Elephant", f1, PRIMARY,
              anchor="ma")
    y += int(f1.size * 1.28)
    f2, _ = fit_size("Party Tracker", "display_xb", 96, W - 220, 40)
    draw_text(cv, (W / 2, y), "Party Tracker", f2, PINE, anchor="ma")
    y += int(f2.size * 1.5)
    y = subline(cv, W / 2, y,
                "The draw, the rules, the budgets and the white elephant "
                "game \u2014 one spreadsheet runs the whole party")
    y = chips_row(cv, W / 2, y + 14, [
        ("Instant Download", PINE), ("700+ Auto-Formulas", PRIMARY),
        ("12 Linked Tabs", GOLD), ("Excel & Google Sheets", INFO)])
    sshot(cv, W / 2, y + 20,
          shot("\U0001F3E0 Dashboard", (1, 40), (1, 14)), 1280)
    footer(cv)
    save(cv, "01_hero")


# ---------------------------------------------------------------------------
# 02 - dashboard
# ---------------------------------------------------------------------------
def img02():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE COMMAND CENTRE")
    y = headline(cv, W / 2, y + 4, "Your whole party, live", 88)
    y = subline(cv, W / 2, y + 2,
                "Guests, draw, budgets and game stats \u2014 recalculated "
                "the moment you type")
    dash = shot("\U0001F3E0 Dashboard", (1, 42), (1, 14))
    br = browser(dash, 1660)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 34
    chips_row(cv, W / 2, y2, [
        ("700+ formulas", PRIMARY), ("4 live charts", PINE),
        ("12 KPI cards", GOLD), ("Locked & safe", INFO)])
    side_card(cv, 90, y + 90, 470, 470, "\U0001F4CA", "Live numbers",
              PINE, [
        "12 KPI cards, always current",
        "Total budget vs actual spend",
        "Average gift cost, RSVPs, rules",
        "4 charts that draw themselves",
        "Progress bars, zero clicks",
    ])
    side_card(cv, W - 90 - 470, y + 90, 470, 470, "\u26A1", "Zero effort",
              PRIMARY, [
        "Log a turn or a receipt once \u2014",
        "the dashboard does the rest",
        "Days-to-go counter on the hero",
        "Works while the party happens",
        "Print-ready for the big night",
    ])
    footer(cv)
    save(cv, "02_dashboard")


# ---------------------------------------------------------------------------
# 03 - what's inside
# ---------------------------------------------------------------------------
def img03():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "WHAT'S INSIDE")
    y = headline(cv, W / 2, y + 4, "12 linked tabs, zero set-up", 86)
    y = subline(cv, W / 2, y + 2,
                "Every tab feeds the next \u2014 type a name once, watch "
                "the whole party wire itself together")
    tabs = [
        ("\U0001F3E0", "Dashboard", "KPIs & 4 live charts", PRIMARY),
        ("\U0001F465", "Participants", "guests, RSVP, households", PINE),
        ("\U0001F385", "Secret Santa Draw", "seed-driven, fair", PRIMARY),
        ("\U0001F6AB", "Exclusions & Rules", "couples, teams, customs",
         BAD),
        ("\U0001F4B0", "Budget Tracker", "per-giver, min to max", GOLD),
        ("\U0001F381", "Wishlists", "claim before you buy", INFO),
        ("\U0001F3B2", "White Elephant", "seats, gifts, steals", PINE),
        ("\U0001F504", "Game History", "the turn-by-turn log", INFO),
        ("\U0001F39F\uFE0F", "Santa Cards", "print, fold, deal", PRIMARY),
        ("\u2699\uFE0F", "Settings", "party basics & seeds", MUTED),
        ("\U0001F4D6", "Start Here", "the 5-minute tour", GOLD),
        ("\U0001F9E9", "_Data (hidden)", "the formula engine", MUTED),
    ]
    cols, gap = 4, 46
    cw = (W - 180 - gap * (cols - 1)) // cols
    ch = 380
    y += 56
    for i, (emoji, name, sub, color) in enumerate(tabs):
        cx = 90 + (i % cols) * (cw + gap)
        cy = y + (i // cols) * (ch + gap)
        side_card(cv, cx, cy, cw, ch, emoji, name, color, [sub],
                  body_pad=24, title_size=27, body_size=22)
    footer(cv)
    save(cv, "03_whats_inside")


# ---------------------------------------------------------------------------
# 04 - participants
# ---------------------------------------------------------------------------
def img04():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "STEP 1 \u2014 THE GUEST LIST")
    y = headline(cv, W / 2, y + 4, "Everyone in one place", 88)
    y = subline(cv, W / 2, y + 2,
                "RSVP dropdowns, households and teams \u2014 the raw "
                "material for a fair draw")
    sc = shot("\U0001F465 Participants", (1, 28), (1, 10))
    br = browser(sc, 1600)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\u2705", "Kept honest",
              PINE, [
        "RSVP: Yes / Maybe / No",
        "Diet notes for the buffet",
        "Gift status feeds the charts",
        "Blank rows are simply ignored",
        "Diet notes for the buffet",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F3E0",
              "Households & teams", PRIMARY, [
        "Couples never draw each other",
        "when the couple rule is on",
        "Teams stay apart too",
        "Just two extra columns \u2014",
        "the draw reads them itself",
    ])
    footer(cv)
    save(cv, "04_participants")


# ---------------------------------------------------------------------------
# 05 - the draw
# ---------------------------------------------------------------------------
def img05():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "STEP 2 \u2014 THE DRAW")
    y = headline(cv, W / 2, y + 4, "No hat. No paper slips.", 88)
    y = subline(cv, W / 2, y + 2,
                "Type a seed, get a full draw \u2014 nobody draws "
                "themselves, no pair repeats")
    sc = shot("\U0001F385 Secret Santa Draw", (1, 24), (1, 7))
    br = browser(sc, 1460)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2 - 210), y + 16),
                 blur=24, alpha=60)
    side_card(cv, W - 90 - 470, y + 80, 470, 500, "\U0001F3B2",
              "Seed magic", PRIMARY, [
        "Same seed \u2192 same draw",
        "New seed \u2192 fresh shuffle",
        "\u2705 OK flags check every rule",
        "Override a single pair by hand",
        "Nobody draws themselves \u2014",
        "ever, it is built in",
    ])
    hand_note(cv, 110, y + 580,
              "change the seed,\nreshuffle in seconds", 46)
    footer(cv)
    save(cv, "05_draw")


# ---------------------------------------------------------------------------
# 06 - rules
# ---------------------------------------------------------------------------
def img06():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "FAIR BY DEFAULT")
    y = headline(cv, W / 2, y + 4, "Rules that respect real life", 84)
    y = subline(cv, W / 2, y + 2,
                "Couples, teammates, last year's pairs and any grudge you "
                "can name \u2014 all off limits")
    sc = shot("\U0001F6AB Exclusions & Rules", (1, 24), (1, 13))
    br = browser(sc, 1700)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F3AF", "Armed & counted",
              BAD, [
        "The chips count your active rules and custom pairs \u2014 and "
        "draw violations should always read 0. If a pair brushes a rule, "
        "nudge the seed once.",
    ], body_size=26)
    footer(cv)
    save(cv, "06_rules")


# ---------------------------------------------------------------------------
# 07 - budget
# ---------------------------------------------------------------------------
def img07():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "MONEY, KEPT HONEST")
    y = headline(cv, W / 2, y + 4, "Budgets that police themselves", 80)
    y = subline(cv, W / 2, y + 2,
                "Set a min-max per person once \u2014 every row and the "
                "dashboard follow")
    sc = shot("\U0001F4B0 Budget Tracker", (1, 21), (1, 9))
    br = browser(sc, 1730)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\U0001F6A8", "Live flags", BAD, [
        "\U0001F534 under budget \u2022 \u2705 within",
        "\U0001F6A8 over budget, counted live",
        "Receipt column \u2014 tick \u2713 when filed",
        "Notes & reference numbers",
        "Over-budget chip counts live",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F4B8",
              "One number to change", GOLD, [
        "Budget min and max live on",
        "the Settings tab \u2014 change",
        "them there and every row,",
        "chart and KPI updates \u2014",
        "and the dashboard totals",
        "recalculate on the spot.",
    ])
    footer(cv)
    save(cv, "07_budget")


# ---------------------------------------------------------------------------
# 08 - wishlists
# ---------------------------------------------------------------------------
def img08():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "NO MORE DOUBLE GIFTS")
    y = headline(cv, W / 2, y + 4, "Wishlists with a claim column", 82)
    y = subline(cv, W / 2, y + 2,
                "Guests log wishes, buyers claim them \u2014 nobody buys "
                "the same thing twice")
    sc = shot("\U0001F381 Wishlists", (1, 24), (1, 7))
    br = browser(sc, 1580)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\u2764\uFE0F", "Must-love radar",
              PRIMARY, [
        "Categories: Must-love,",
        "Nice-to-have, Idea, Please-not",
        "Open must-loves are counted",
        "so the big wishes get bought",
        "No more duplicate gifts",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F517",
              "Shopping-ready", INFO, [
        "Price hints next to the budget",
        "Links straight to the product",
        "Filter by guest while buying",
        "Claims tick off with one key",
        "Price hints vs your budget",
    ])
    footer(cv)
    save(cv, "08_wishlists")


# ---------------------------------------------------------------------------
# 09 - white elephant
# ---------------------------------------------------------------------------
def img09():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE PARTY GAME, TAMED")
    y = headline(cv, W / 2, y + 4, "The White Elephant board", 88)
    y = subline(cv, W / 2, y + 2,
                "Seats, gifts, holders and steals \u2014 the board plays "
                "itself while you run the room")
    sc = shot("\U0001F3B2 White Elephant", (1, 24), (1, 12))
    br = browser(sc, 1560)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 14), blur=24,
                 alpha=60)
    y2 = y + 14 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F504",
              "Statuses, decoded", PINE, [
        "\U0001F381 Available \u2022 \U0001F932 Held \u2022 "
        "\U0001F504 Stolen \u2022 \U0001F512 Final \u2014 and the Now "
        "chip tells you exactly whose turn it is.",
    ], body_size=26)
    footer(cv)
    save(cv, "09_whiteelephant")


# ---------------------------------------------------------------------------
# 10 - history + cards
# ---------------------------------------------------------------------------
def img10():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "LOG IT ONCE")
    y = headline(cv, W / 2, y + 4, "History in, everything out", 84)
    y = subline(cv, W / 2, y + 2,
                "One row per turn \u2014 the board, the Now chip and the "
                "dashboard follow by themselves")
    sc = shot("\U0001F504 Game History", (1, 20), (1, 6))
    br1 = browser(sc, 1290)
    shadow_paste(cv, br1, (int(W / 2 - br1.width / 2 - 260), y + 14),
                 blur=24, alpha=60)
    sc2 = shot("\U0001F39F\uFE0F Santa Cards", (1, 19), (1, 9))
    br2 = browser(sc2, 1290)
    shadow_paste(cv, br2, (int(W / 2 - br2.width / 2 + 260),
                           y + 14 + (br1.height - br2.height) / 2),
                 blur=24, alpha=60)
    side_card(cv, W - 90 - 420, y + 60, 420, 500, "\U0001F39F\uFE0F",
              "Santa Cards", PRIMARY, [
        "Giver outside, recipient inside",
        "The secret survives the handout",
        "Print the tab, cut, fold, deal",
        "24 cards ready for big parties",
        "Every giver gets their slip",
        "The reveal stays a surprise",
    ])
    footer(cv)
    save(cv, "10_history_cards")


# ---------------------------------------------------------------------------
# 11 - two themes
# ---------------------------------------------------------------------------
def img11():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "TWO MOODS, ONE ENGINE")
    y = headline(cv, W / 2, y + 4, "Noel warmth or Arctic calm", 86)
    y = subline(cv, W / 2, y + 2,
                "Both themes ship in every download \u2014 pick your "
                "party's palette")
    noel = shot("\U0001F4D6 Start Here", (1, 24), (1, 10))
    arctic = shot("\U0001F4D6 Start Here", (1, 24), (1, 10),
                  path=XLSX_ARCTIC)
    bw = 1090
    br1 = browser(noel, bw)
    br2 = browser(arctic, bw)
    top = y + 24
    shadow_paste(cv, br1, (int(W / 2 - bw / 2 - 40), top), blur=24,
                 alpha=60)
    shadow_paste(cv, br2, (int(W / 2 - bw / 2 + 40),
                           top + br1.height - 74), blur=24, alpha=60)
    draw_text(cv, (140, top + br1.height - 130), "NOEL", F("sans_b", 30),
              PRIMARY)
    draw_text(cv, (W - 140, top + 2 * br1.height - 200), "ARCTIC",
              F("sans_b", 30), INFO, anchor="ra")
    footer(cv)
    save(cv, "11_themes")


# ---------------------------------------------------------------------------
# 12 - example file
# ---------------------------------------------------------------------------
def img12():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "SEE IT WORKING")
    y = headline(cv, W / 2, y + 4, "A demo party comes included", 82)
    y = subline(cv, W / 2, y + 2,
                "12 guests, 10 white elephant gifts, 14 turns \u2014 the "
                "EXAMPLE file shows every formula alive")
    sc = shot("\U0001F3B2 White Elephant", (1, 24), (1, 12))
    br = browser(sc, 1560)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F50D", "Peek first",
              GOLD, [
        "Open the EXAMPLE to see a finished party \u2014 then start your "
        "real one in the blank file. Same tabs, same maths, zero set-up.",
    ], body_size=26)
    footer(cv)
    save(cv, "12_example")


# ---------------------------------------------------------------------------
# 13 - how it works
# ---------------------------------------------------------------------------
def img13():
    cv = canvas()
    y = kicker(cv, W / 2, 110, "FROM DOWNLOAD TO DRAW IN 5 MINUTES")
    y = headline(cv, W / 2, y + 4, "How it works", 96)
    y = subline(cv, W / 2, y + 2,
                "Three steps \u2014 the spreadsheet does every hard part")
    steps = [
        ("Set the party", "Name, date, budget range and a draw seed on "
         "the Settings tab", PRIMARY),
        ("Add your guests", "One row per person with RSVP, household and "
         "team", PINE),
        ("Draw & play", "Press enter on the seed \u2014 pairs, budgets "
         "and the game board appear", GOLD),
    ]
    bw = 660
    gap = 90
    x0 = W / 2 - (3 * bw + 2 * gap) / 2
    top = y + 130
    for i, (title, body, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        side_card(cv, x, top, bw, 620, "", title, color, [body],
                  body_pad=30, title_size=36, body_size=26)
        num_circle(cv, x + bw / 2, top - 40, i + 1)
        if i < 2:
            arrow_right(cv, x + bw + gap / 2 - 30, top + 310, 60)
    y2 = top + 620 + 80
    y2 = chips_row(cv, W / 2, y2, [
        ("No macros", PINE), ("No setup files", PRIMARY),
        ("Works offline", GOLD), ("Google Sheets ready", INFO)])
    side_card(cv, W / 2 - 800, y2 + 56, 1600, 270, "\U0001F552",
              "Five minutes, once", GOLD, [
        "Most buyers go from download to a finished draw before the "
        "kettle boils \u2014 the Settings tab asks six questions and "
        "the rest is automatic."], body_size=26)
    footer(cv)
    save(cv, "13_howitworks")


# ---------------------------------------------------------------------------
# 14 - files
# ---------------------------------------------------------------------------
def img14():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "INSTANT DOWNLOAD")
    y = headline(cv, W / 2, y + 4, "4 files, one tidy folder", 90)
    y = subline(cv, W / 2, y + 2,
                "Yours the moment you check out \u2014 nothing to install, "
                "nothing to enable")
    files = [
        ("\U0001F7E9", "PREMIUM \u2014 Noel", "the full 12-tab tracker",
         PRIMARY),
        ("\U0001F7E7", "PREMIUM \u2014 Arctic", "same engine, cool tones",
         INFO),
        ("\u2728", "PREMIUM \u2014 EXAMPLE", "the demo party, filled in",
         GOLD),
        ("\U0001F4D8", "User Guide", "12-page illustrated PDF", PINE),
    ]
    bw, gap = 1000, 70
    x0 = W / 2 - (2 * bw + gap) / 2
    top = y + 100
    for i, (emoji, name, sub, color) in enumerate(files):
        x = x0 + (i % 2) * (bw + gap)
        yy = top + (i // 2) * 370
        side_card(cv, x, yy, bw, 330, emoji, name, color, [sub],
                  body_pad=30, title_size=32, body_size=25)
    y2 = top + 2 * 370 + 40
    y2 = side_card(cv, W / 2 - 800, y2, 1600, 300, "\U0001F9ED",
                   "Looking for a lighter start?", MUTED, [
        "The BASIC edition (7 tabs: guests, draw, budget, dashboard) is a "
        "separate listing in this shop \u2014 and the demo files let you "
        "peek before you plan.",
    ], body_size=25)
    footer(cv)
    save(cv, "14_files")


# ---------------------------------------------------------------------------
# 15 - FAQ
# ---------------------------------------------------------------------------
def img15():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "GOOD QUESTIONS")
    y = headline(cv, W / 2, y + 4, "Everything people ask", 90)
    y = subline(cv, W / 2, y + 2,
                "Straight answers before you buy")
    faq = [
        ("Does it work in Google Sheets?",
         "Yes \u2014 upload the .xlsx to Drive and open with Sheets; the "
         "formulas, dropdowns and colours translate automatically.", PINE),
        ("And in Excel?", "Excel 2016 or later on Windows and Mac, and "
         "Microsoft 365. No macros, nothing to enable.", PRIMARY),
        ("Can I break the formulas?",
         "No \u2014 every formula cell is locked for safety. All your "
         "typing cells (the cream ones) stay wide open.", GOLD),
        ("What if my party is huge?",
         "24 pre-formatted rows for guests and gifts; blank rows are "
         "ignored, and the EXAMPLE shows a full 12-person party.", INFO),
    ]
    top = y + 60
    for i, (q, a, color) in enumerate(faq):
        side_card(cv, 150, top, W - 300, 300, "\u2753", q, color, [a],
                  body_pad=32, title_size=31, body_size=25)
        top += 300 + 36
    footer(cv)
    save(cv, "15_faq")


# ---------------------------------------------------------------------------
def main():
    print("building santa listing images ...")
    for fn in (img01, img02, img03, img04, img05, img06, img07, img08,
               img09, img10, img11, img12, img13, img14, img15):
        fn()
    print("done \u2014 15 images in etsy/images_santa/")


if __name__ == "__main__":
    main()
````

---
## `etsy/make_listing_zip_santa.py`

*Bundles the standalone Etsy listing-kit zip (md + 15 images).* (57 lines)

````python
"""
make_listing_zip_santa.py - bundle the Etsy listing kit for the Secret
Santa & White Elephant Party Tracker into ONE zip:

  LISTING_KIT_SANTA.md   title, 13+7 tags, description, alt texts,
                         pricing, publish checklist
  images_santa/          15 listing images (2400x1800 JPEG, < 1 MB each)

Run from the repo root:   python3 -m etsy.make_listing_zip_santa
"""

import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Secret_Santa_White_Elephant_Tracker_Etsy_Listing_Kit.zip"

IMAGES = [
    "01_hero", "02_dashboard", "03_whats_inside", "04_participants",
    "05_draw", "06_rules", "07_budget", "08_wishlists", "09_whiteelephant",
    "10_history_cards", "11_themes", "12_example", "13_howitworks",
    "14_files", "15_faq",
]


def main():
    src_md = os.path.join(ROOT, "etsy", "LISTING_KIT_SANTA.md")
    assert os.path.exists(src_md), "etsy/LISTING_KIT_SANTA.md missing"
    for n in IMAGES:
        p = os.path.join(ROOT, "etsy", "images_santa", n + ".jpg")
        assert os.path.exists(p), f"missing image {n}.jpg - run " \
            f"python3 -m etsy.make_listing_images_santa first"

    out = os.path.join(ROOT, ZIP_NAME)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        z.write(src_md, "LISTING_KIT_SANTA.md")
        for n in IMAGES:
            p = os.path.join(ROOT, "etsy", "images_santa", n + ".jpg")
            z.write(p, os.path.join("images_santa", n + ".jpg"))

    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        assert bad is None, f"corrupt member: {bad}"
        names = z.namelist()
        assert len(names) == 16, names

    size = os.path.getsize(out)
    print(f"built {ZIP_NAME}")
    print(f"  members : {len(names)} (1 kit md + 15 images)")
    print(f"  size    : {size/1024/1024:.1f} MB")
    print(f"  zip ok  : integrity verified")


if __name__ == "__main__":
    main()
````

---