"""
\U0001F4A1 Wish List / Gift Ideas - the "parking bay" for ideas.

Capture hints all year, rank them, and see at a glance which ones have already
made it onto the \U0001F381 Gift Tracker (that check is a COUNTIFS against
the gift list, so it stays true as you work).
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "wishlist"
LAST_COL = "K"

COLUMNS = [
    ("n", "#", "idx", None),
    ("person", "Person", "text", None),
    ("idea", "Gift idea", "text", None),
    ("category", "Category", "center", None),
    ("link", "Link", "link", None),
    ("open", "\U0001F517", "calc_c", "gold"),
    ("price", "Price seen", "money", None),
    ("priority", "Priority", "center", None),
    ("in_tracker", "On the gift list?", "calc_c", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F4A1  Wish List & Gift Ideas",
        "  Hints all year round, ranked by how much they really want them.",
        LAST_COL)

    chips = [
        ("B", "C", "\U0001F4A1 Ideas saved: ", "wish_total", "plum"),
        ("D", "E", "\u2B50 Must-haves: ", "wish_must", "gold"),
        ("F", "G", "\U0001F4B0 Value of ideas: ", "wish_value", "accent"),
        ("H", "I", "\u2714 Already on the gift list: ", None, "ok"),
        ("J", LAST_COL, "\u2795 Still to move across: ", None, "warn"),
    ]
    for c1, c2, label, kpi_key, color in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2), "", fmt)
        if kpi_key == "wish_value":
            formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label,
                                                           bk.kpi(kpi_key))
            cached = "%s%s" % (label, m.money(m.agg[kpi_key]))
        elif kpi_key:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        elif label.startswith("\u2714"):
            formula = '="%s"&COUNTIF(%s,"\u2714 In gift tracker")' % (
                label, bk.rng(KEY, "in_tracker"))
            cached = "%s%d" % (label, _in_tracker_count(m))
        else:
            formula = '="%s"&COUNTIF(%s,"\u2795 Not yet")' % (
                label, bk.rng(KEY, "in_tracker"))
            cached = "%s%d" % (label, m.agg["wish_total"] - _in_tracker_count(m))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = _formulas(bk, rownum)
        if i < len(m.wishlist):
            w = m.wishlist[i]
            values.update({k: w[k] for k in ("person", "idea", "category",
                                             "link", "price", "priority",
                                             "notes")})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    K.list_dv(bk, KEY, "person", "recipients", title="Who is it for?")
    K.list_dv(bk, KEY, "category", "gift_categories", title="Category")
    K.fixed_dv(bk, KEY, "priority", "Priorities", title="Priority",
               message="\u2B50\u2B50\u2B50 Must have \u2014 they have "
                       "dropped a serious hint.\n\u2B50\u2B50 Maybe.\n"
                       "\u2B50 Low priority / filler.")
    K.money_dv(bk, KEY, ["price"], label="a price")

    n = C.ROW_FIRST
    K.status_cf(bk, KEY, "priority", {
        C.PR_MUST: (th.gold_soft, th.gold),
        C.PR_MAYBE: (th.info_soft, th.info),
        C.PR_LOW: (th.alt, th.muted),
    })
    K.status_cf(bk, KEY, "in_tracker", {
        "\u2714 In gift tracker": (th.ok_soft, th.ok),
        "\u2795 Not yet": (th.warn_soft, th.warn),
    })
    K.databar(bk, KEY, "price", color=th.plum)

    total_row = C.last_row(KEY) + 2
    K.totals_row(
        bk, KEY, total_row,
        {"price": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "price"),
                                            C.ROW_FIRST, bk.col(KEY, "price"),
                                            C.last_row(KEY)),
                   "#,##0.00", m.agg["wish_value"]),
         "in_tracker": ('=COUNTIF($%s$%d:$%s$%d,"\u2795 Not yet")&" idea(s) '
                        'still to move across"'
                        % (bk.col(KEY, "in_tracker"), C.ROW_FIRST,
                           bk.col(KEY, "in_tracker"), C.last_row(KEY)),
                        "@", "%d idea(s) still to move across"
                        % (m.agg["wish_total"] - _in_tracker_count(m)))},
        label="  TOTALS", label_span=("B", "G"), last_col=LAST_COL)

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  Use this tab all year: when somebody mentions something in "
         "March, write it here and forget about it until November.",
         "\u2022  \u201COn the gift list?\u201D checks the \U0001F381 Gift "
         "Tracker for the same person + same idea, so you always know what "
         "still needs moving across.",
         "\u2022  To move an idea over: copy the person and idea cells, paste "
         "them into a new row on the \U0001F381 Gift Tracker, then set the "
         "status to \U0001F6D2 Need to Buy.",
         "\u2022  Sort by Priority (Data \u2192 Sort, or use the filter "
         "arrows) to build the shopping list in the right order."],
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


def _formulas(bk, n):
    def L(f):
        return bk.col(KEY, f)

    return {
        "n": '=IF($%s%d="","",ROW()-%d)' % (L("idea"), n, C.ROW_FIRST - 1),
        "open": '=IF($%s%d="","",HYPERLINK($%s%d,"\U0001F517"))'
                % (L("link"), n, L("link"), n),
        "in_tracker": ('=IF(OR($%s%d="",$%s%d=""),"",IF(COUNTIFS(%s,$%s%d,%s,'
                       '$%s%d)>0,"\u2714 In gift tracker","\u2795 Not yet"))'
                       % (L("person"), n, L("idea"), n,
                          bk.rng("gifts", "recipient"), L("person"), n,
                          bk.rng("gifts", "idea"), L("idea"), n)),
    }


def _in_tracker_count(m):
    pairs = set((g["recipient"], g["idea"]) for g in m.gifts)
    return len([w for w in m.wishlist
                if (w["person"], w["idea"]) in pairs])


def _cached(m, i):
    if i >= len(m.wishlist):
        return {"n": "", "open": "", "in_tracker": ""}
    w = m.wishlist[i]
    pairs = set((g["recipient"], g["idea"]) for g in m.gifts)
    return {"n": i + 1, "open": "\U0001F517" if w["link"] else "",
            "in_tracker": ("\u2714 In gift tracker"
                           if (w["person"], w["idea"]) in pairs
                           else "\u2795 Not yet")}
