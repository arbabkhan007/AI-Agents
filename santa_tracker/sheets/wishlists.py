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
