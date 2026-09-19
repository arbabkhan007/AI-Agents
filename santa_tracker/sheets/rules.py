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
