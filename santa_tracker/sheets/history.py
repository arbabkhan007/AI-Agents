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
