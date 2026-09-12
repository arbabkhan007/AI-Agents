"""
\U0001F48C Card Tracker - who got a card, who still needs one, and what the
post office took from you.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "cards"
LAST_COL = "M"

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Name / family", "text", None),
    ("relationship", "Relationship", "center", None),
    ("address", "Address", "text", None),
    ("bought", "Card bought", "tick", None),
    ("written", "Written", "tick", None),
    ("sent", "Sent", "tick", None),
    ("date_sent", "Date sent", "date", None),
    ("received", "Reply back", "tick", None),
    ("postage", "Postage", "money", None),
    ("status", "Status (auto)", "calc_c", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F48C  Christmas Card Tracker",
        "  Bought \u2192 written \u2192 posted \u2192 replied. Nobody gets "
        "forgotten, and postage lands in your budget.",
        LAST_COL)

    chips = [
        ("B", "C", "\U0001F4DD Cards: ", "cards_total", "primary"),
        ("D", "E", "\U0001F6D2 Bought: ", None, "info"),
        ("F", "G", "\u270D\uFE0F Written: ", "cards_written", "warn"),
        ("H", "I", "\U0001F4EE Sent: ", "cards_sent", "ok"),
        ("J", "K", "\U0001F4EC Replies: ", None, "plum"),
        ("L", LAST_COL, "\U0001F4B0 Postage: ", None, "accent"),
    ]
    for c1, c2, label, kpi_key, color in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2), "", fmt)
        if kpi_key:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        elif label.startswith("\U0001F6D2"):
            formula = '="%s"&COUNTIF(%s,"%s")' % (label, bk.rng(KEY, "bought"),
                                                  C.TICK)
            cached = "%s%d" % (label, len([x for x in m.cards
                                           if x["bought"] == C.TICK]))
        elif label.startswith("\U0001F4EC"):
            formula = '="%s"&COUNTIF(%s,"%s")' % (label,
                                                  bk.rng(KEY, "received"),
                                                  C.TICK)
            cached = "%s%d" % (label, m.agg["cards_received"])
        else:
            formula = '="%s"&Currency&TEXT(SUM(%s),"#,##0.00")' % (
                label, bk.rng(KEY, "postage"))
            cached = "%s%s" % (label, m.money(m.agg["cards_postage"], 2))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = {"n": '=IF($%s%d="","",ROW()-%d)'
                         % (bk.col(KEY, "name"), rownum, C.ROW_FIRST - 1),
                  "status": _status_formula(bk, rownum)}
        if i < len(m.cards):
            c = m.cards[i]
            values.update({k: c[k] for k in
                           ("name", "relationship", "address", "bought",
                            "written", "sent", "date_sent", "received",
                            "postage", "notes")})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    K.list_dv(bk, KEY, "relationship", "relationships", title="Relationship")
    K.tick_dv(bk, KEY, ["bought", "written", "sent", "received"])
    K.date_dv(bk, KEY, ["date_sent"])
    K.money_dv(bk, KEY, ["postage"], label="postage")

    n = C.ROW_FIRST
    K.tick_cf(bk, KEY, ["bought", "written", "sent", "received"])
    K.status_cf(bk, KEY, "status", {
        "\U0001F4EE Sent": (th.ok_soft, th.ok),
        "\u270D\uFE0F Written": (th.info_soft, th.info),
        "\U0001F6D2 Bought": (th.warn_soft, th.warn),
        "\U0001F4DD To do": (th.alt, th.muted),
    })
    sent = bk.col(KEY, "sent")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula", "criteria": '=$%s%d="%s"' % (sent, n, C.TICK),
        "format": S.cf(bg=th.ok_soft, fg=th.primary)})

    total_row = C.last_row(KEY) + 2
    fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                       bg_color=th.primary, align="center", valign="vcenter",
                       border=1, border_color=th.primary))
    K.totals_row(
        bk, KEY, total_row,
        {"postage": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "postage"),
                                              C.ROW_FIRST,
                                              bk.col(KEY, "postage"),
                                              C.last_row(KEY)),
                     "#,##0.00", m.agg["cards_postage"])},
        label="  TOTALS", label_span=("B", "I"), last_col=LAST_COL)
    ws.merge_range(r(total_row), ci("J"), r(total_row), ci(LAST_COL), "", fmt)
    ws.write_formula(
        r(total_row), ci("J"),
        '="\U0001F4EE Cards sent: "&%s&" / "&%s'
        % (bk.kpi("cards_sent"), bk.kpi("cards_total")), fmt,
        "\U0001F4EE Cards sent: %d / %d" % (m.agg["cards_sent"],
                                            m.agg["cards_total"]))
    bk.stats["formulas"] += 1

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  Tick the boxes as you go: bought \u2192 written \u2192 sent "
         "\u2192 reply. The status column reads the ticks for you.",
         "\u2022  Postage you type here is added to the \u201CCards & "
         "postage\u201D line on the \U0001F4B0 Budget tab automatically.",
         "\u2022  Posting cut-off: aim for %d days before the big day "
         "(the dashboard shows the exact date)."
         % 14],
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


def _status_formula(bk, n):
    def L(f):
        return "$%s%d" % (bk.col(KEY, f), n)

    return ('=IF({name}="","",IF({sent}="{t}","\U0001F4EE Sent",'
            'IF({written}="{t}","\u270D\uFE0F Written",'
            'IF({bought}="{t}","\U0001F6D2 Bought","\U0001F4DD To do"))))'
            ).format(name=L("name"), sent=L("sent"), written=L("written"),
                     bought=L("bought"), t=C.TICK)


def _cached(m, i):
    if i >= len(m.cards):
        return {"n": "", "status": ""}
    c = m.cards[i]
    if c["sent"] == C.TICK:
        status = "\U0001F4EE Sent"
    elif c["written"] == C.TICK:
        status = "\u270D\uFE0F Written"
    elif c["bought"] == C.TICK:
        status = "\U0001F6D2 Bought"
    else:
        status = "\U0001F4DD To do"
    return {"n": i + 1, "status": status}
