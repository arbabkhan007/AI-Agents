"""
\U0001F380 Wrapping & Hiding - the fun one (and the one parents love).

Everything on the left is pulled live from the \U0001F381 Gift Tracker, so
there is nothing to re-type: this tab is where you record *where the wrapped
present is hiding* and whether the gift tag is on it.

Secret Mode (\u2699\uFE0F Setup) makes the hiding-spot text invisible so a
nosy helper cannot spoil the surprise by glancing at your screen.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "wrapping"
LAST_COL = "J"

COLUMNS = [
    ("n", "#", "calc_c", "primary_2"),
    ("recipient", "For", "calc", "primary_2"),
    ("idea", "Gift", "calc", "primary_2"),
    ("bought", "Bought?", "calc_c", "primary_2"),
    ("wrapped", "Wrapped?", "calc_c", "primary_2"),
    ("hiding", "\U0001F648 Hiding spot", "text", None),
    ("tag", "\U0001F3F7\uFE0F Tag on", "tick", None),
    ("delivered", "Handed over?", "calc_c", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo
    gt = bk.q("gifts")

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F380  Wrapping & Hiding",
        "  Mirrors your gift list automatically \u2014 add the hiding spot "
        "and the gift tag here.",
        LAST_COL)

    chips = [
        ("B", "C", "\U0001F380 To wrap: ", "wrap_to_do", "warn", "n"),
        ("D", "E", "\u2705 Wrapped: ", "gifts_wrapped", "ok", "n"),
        ("F", "G", "\U0001F3F7\uFE0F Tags done: ", None, "info", "n"),
        ("H", "H", "\U0001F648 Spots noted: ", None, "plum", "n"),
        ("I", "I", "\U0001F4E6 Handed over: ", "gifts_delivered", "primary",
         "n"),
        ("J", LAST_COL, None, None, "accent", "secret"),
    ]
    for c1, c2, label, kpi_key, color, kind in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        if c1 == c2:
            ws.write(r(C.ROW_STATS), ci(c1), "", fmt)
        else:
            ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2),
                           "", fmt)
        if kind == "secret":
            formula = ('=IF(SecretMode="Yes","\U0001F648 Secret Mode ON '
                       '\u2014 hiding spots are invisible","\U0001F440 '
                       'Secret Mode off \u2014 switch it on in '
                       '\u2699\uFE0F Setup")')
            cached = ("\U0001F648 Secret Mode ON \u2014 hiding spots are "
                      "invisible" if m.settings["secret"] == "Yes"
                      else "\U0001F440 Secret Mode off \u2014 switch it on "
                           "in \u2699\uFE0F Setup")
        elif kpi_key:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        elif label.startswith("\U0001F3F7"):
            formula = '="%s"&COUNTIF(%s,"%s")' % (label, bk.rng(KEY, "tag"),
                                                  C.TICK)
            cached = "%s%d" % (label, _tags_done(m))
        else:
            formula = '="%s"&COUNTA(%s)' % (label, bk.rng(KEY, "hiding"))
            cached = "%s%d" % (label, _spots_noted(m))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = _formulas(bk, rownum, gt)
        if i < len(m.gifts) and m.gifts[i]["idea"]:
            values["hiding"] = m.gifts[i].get("hiding", "")
            values["tag"] = m.gifts[i].get("tag", "")
            values["notes"] = ""
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i, gt))

    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    bk.ws(KEY).data_validation(
        r(C.ROW_FIRST), ci(bk.col(KEY, "hiding")), r(C.last_row(KEY)),
        ci(bk.col(KEY, "hiding")),
        {"validate": "list", "source": "=" + bk.listname("hiding_spots"),
         "ignore_blank": True, "show_input": True,
         "input_title": "Where is it hiding?",
         "input_message": "Pick a spot or type your own.",
         "show_error": True, "error_type": "warning",
         "error_title": "Free text is fine",
         "error_message": "Keep it short \u2014 or add your own spots to the "
                          "list in \u2699\uFE0F Setup."})
    K.tick_dv(bk, KEY, ["tag"], message="Tick \u2713 when the name tag is on "
                                        "the parcel.")

    n = C.ROW_FIRST
    for field, mapping in (
            ("bought", {"\u2705 Bought": (th.ok_soft, th.ok),
                        "\U0001F69A On the way": (th.info_soft, th.info),
                        "\u23F3 Not yet": (th.alt, th.muted)}),
            ("wrapped", {"\U0001F380 Wrapped": (th.gold_soft, th.gold),
                         "\u2014 to wrap": (th.warn_soft, th.warn)}),
            ("delivered", {"\U0001F4E6 Given": (th.primary_soft, th.primary),
                           "\u2014": (th.alt, th.muted)})):
        K.status_cf(bk, KEY, field, mapping)
    K.tick_cf(bk, KEY, ["tag"])
    K.secret_cf(bk, KEY, "hiding")
    wrapped = bk.col(KEY, "wrapped")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=$%s%d="\U0001F380 Wrapped"' % (wrapped, n),
        "format": S.cf(bg=th.gold_soft, fg=th.ink)})

    total_row = C.last_row(KEY) + 2
    K.totals_row(
        bk, KEY, total_row,
        {"tag": ('=COUNTIF(%s,"%s")' % (bk.rng(KEY, "tag"), C.TICK), "0",
                 _tags_done(m)),
         "hiding": ("=COUNTA(%s)" % bk.rng(KEY, "hiding"), "0",
                    _spots_noted(m))},
        label="  WRAPPING ROOM", label_span=("B", "E"), last_col=LAST_COL)
    fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                       bg_color=th.primary, align="center", valign="vcenter",
                       border=1, border_color=th.primary))
    ws.merge_range(r(total_row), ci("I"), r(total_row), ci(LAST_COL), "", fmt)
    ws.write_formula(r(total_row), ci("I"),
                     '="\U0001F380 "&%s&" wrapped   \u2022   \u23F3 "&%s'
                     '&" still to wrap"'
                     % (bk.kpi("gifts_wrapped"), bk.kpi("wrap_to_do")), fmt,
                     "\U0001F380 %d wrapped   \u2022   \u23F3 %d still to wrap"
                     % (m.agg["gifts_wrapped"], m.agg["wrap_to_do"]))
    bk.stats["formulas"] += 1

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  The left-hand columns are live mirrors of the "
         "\U0001F381 Gift Tracker \u2014 tick \U0001F380 Wrapped or move the "
         "status on over there and this tab updates itself.",
         "\u2022  Type the hiding spot here (\U0001F648). Parents: this is "
         "the column that stops you wrapping the same present twice or "
         "losing it in the loft.",
         "\u2022  Someone about to glance at your screen? \u2699\uFE0F Setup "
         "\u2192 Secret Mode = Yes and every hiding spot turns white-on-white "
         "instantly. For total privacy, right-click column G \u2192 Hide.",
         "\u2022  \U0001F3F7\uFE0F Tag on = the name label is attached, so "
         "nothing ends up under the wrong tree."],
        title="  \U0001F4A1  How this tab works")
    row += 1
    ws.set_row(r(row), 26)
    row = bk.nav_row(KEY, row, first_col=1, span=2,
                     max_col=LAST_COL) + 2
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  %s v%s  \u2022  %s" % (C.PRODUCT, C.VERSION, C.TAGLINE),
                   S.footer)
    bk.page(KEY, LAST_COL, row + 2, landscape=True,
            title_rows=(0, C.ROW_HEADER - 1))
    return ws


def _formulas(bk, n, gt):
    def G(f):
        return "%s!$%s$%d" % (gt, bk.col("gifts", f), n)

    bought_states = 'OR(%s="%s",%s="%s",%s="%s")' % (
        G("status"), C.ST_BOUGHT, G("status"), C.ST_WRAPPED, G("status"),
        C.ST_DELIVERED)
    wrapped_states = 'OR(%s="%s",%s="%s",%s="%s")' % (
        G("wrapped"), C.TICK, G("status"), C.ST_WRAPPED, G("status"),
        C.ST_DELIVERED)
    return {
        "n": '=IF(%s="","",ROW()-%d)' % (G("recipient"), C.ROW_FIRST - 1),
        "recipient": '=IF(%s="","",%s)' % (G("recipient"), G("recipient")),
        "idea": '=IF(%s="","",%s)' % (G("recipient"), G("idea")),
        "bought": '=IF(%s="","",IF(%s,"\u2705 Bought",IF(%s="%s",'
                  '"\U0001F69A On the way","\u23F3 Not yet")))'
                  % (G("recipient"), bought_states, G("status"), C.ST_ORDERED),
        "wrapped": '=IF(%s="","",IF(%s,"\U0001F380 Wrapped","\u2014 to wrap"))'
                   % (G("recipient"), wrapped_states),
        "delivered": '=IF(%s="","",IF(OR(%s="%s",%s="%s"),"\U0001F4E6 Given",'
                     '"\u2014"))' % (G("recipient"), G("delivered"), C.TICK,
                                     G("status"), C.ST_DELIVERED),
    }


def _cached(m, i, gt):
    if i >= len(m.gifts) or not m.gifts[i]["idea"]:
        return {"n": "", "recipient": "", "idea": "", "bought": "",
                "wrapped": "", "delivered": ""}
    g = m.gifts[i]
    st = g["status"]
    if st in (C.ST_BOUGHT, C.ST_WRAPPED, C.ST_DELIVERED):
        bought = "\u2705 Bought"
    elif st == C.ST_ORDERED:
        bought = "\U0001F69A On the way"
    else:
        bought = "\u23F3 Not yet"
    wrapped = ("\U0001F380 Wrapped"
               if (g["wrapped"] == C.TICK or st in (C.ST_WRAPPED,
                                                    C.ST_DELIVERED))
               else "\u2014 to wrap")
    delivered = ("\U0001F4E6 Given"
                 if (g["delivered"] == C.TICK or st == C.ST_DELIVERED)
                 else "\u2014")
    return {"n": i + 1, "recipient": g["recipient"], "idea": g["idea"],
            "bought": bought, "wrapped": wrapped, "delivered": delivered}


def _tags_done(m):
    return len([g for g in m.gifts if g.get("tag") == C.TICK])


def _spots_noted(m):
    return len([g for g in m.gifts if g.get("hiding")])
