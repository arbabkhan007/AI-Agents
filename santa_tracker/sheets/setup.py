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
