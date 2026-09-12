"""
\U0001F381 Gift Tracker - the heart of the product.

Inputs (white cells): recipient, idea, category, store, link, budget, actual
cost, status, wrapped, delivered, deadline, notes.
Automatic (tinted cells): row number, open-link button, difference, % of
budget, days left and the deadline alert.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "gifts"
LAST_COL = "T"

COLUMNS = [
    ("n", "#", "idx", None),
    ("recipient", "Recipient", "text", None),
    ("relationship", "Relationship", "center", None),
    ("idea", "Gift idea", "text", None),
    ("category", "Category", "center", None),
    ("store", "Store / where from", "text", None),
    ("link", "Link", "link", None),
    ("open", "\U0001F517", "calc_c", "gold"),
    ("budget", "Budget", "money", None),
    ("cost", "Actual cost", "money", None),
    ("diff", "Under / over", "calc_money", "primary_2"),
    ("pct", "% of budget", "calc_pct", "primary_2"),
    ("status", "Status", "center", None),
    ("wrapped", "\U0001F380 Wrapped", "tick", None),
    ("delivered", "\U0001F4E6 Given", "tick", None),
    ("deadline", "Buy-by date", "date", None),
    ("days", "Days left", "calc_num", "primary_2"),
    ("alert", "Deadline alert", "calc_c", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S = bk.S
    th = bk.th
    m = bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F381  Gift Tracker",
        "  Every present in one place \u2014 type in the white cells, the "
        "tinted cells do the maths.",
        LAST_COL)

    # ------------------------------------------------------------------
    # quick-stat strip
    # ------------------------------------------------------------------
    chips = [
        ("B", "D", "\U0001F381 Planned: ", "gifts_planned", "primary"),
        ("E", "G", "\u2705 Purchased: ", "gifts_purchased", "ok"),
        ("H", "J", "\U0001F380 Wrapped: ", "gifts_wrapped", "accent"),
        ("K", "M", "\U0001F4E6 Given: ", "gifts_delivered", "info"),
        ("N", "P", "\U0001F6D2 Still to buy: ", "gifts_to_buy", "warn"),
        ("Q", "S", "\U0001F4B0 Spent on gifts: ", "gift_actual_spent",
         "primary_2"),
    ]
    for c1, c2, label, kpi_key, color in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5,
                     bold=True, align="left")
        ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2), "", fmt)
        if kpi_key == "gift_actual_spent":
            formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label,
                                                           bk.kpi(kpi_key))
            cached = "%s%s" % (label, m.money(m.agg[kpi_key]))
        else:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1
    if LAST_COL != "T":
        ws.merge_range(r(C.ROW_STATS), ci("T"), r(C.ROW_STATS), ci(LAST_COL),
                       "", S.canvas)

    # ------------------------------------------------------------------
    # table
    # ------------------------------------------------------------------
    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        cached = _row_cached(m, i)
        values = _row_formulas(bk, rownum)
        if i < len(m.gifts):
            g = m.gifts[i]
            values.update({k: g[k] for k in
                           ("recipient", "relationship", "idea", "category",
                            "store", "link", "budget", "cost", "status",
                            "wrapped", "delivered", "deadline", "notes")})
        K.write_row(bk, KEY, COLUMNS, rownum, values, cached)

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------
    K.list_dv(bk, KEY, "recipient", "recipients", title="Who is it for?",
              message="Pick a name from your recipient list (\u2699\uFE0F "
                      "Setup \u2192 Your lists). Type a new name to add one.",
              error="Use a name from your list, or type a new one.")
    K.list_dv(bk, KEY, "relationship", "relationships", title="Relationship")
    K.list_dv(bk, KEY, "category", "gift_categories", title="Gift category",
              message="Drives the \u201Cspend by category\u201D chart on the "
                      "dashboard.")
    K.list_dv(bk, KEY, "store", "stores", title="Store")
    K.fixed_dv(bk, KEY, "status", "Statuses", title="Gift status",
               message="The pipeline: \U0001F4A1 Idea \u2192 \U0001F6D2 Need "
                       "to Buy \u2192 \U0001F6CD\uFE0F Ordered \u2192 "
                       "\u2705 Purchased \u2192 \U0001F380 Wrapped \u2192 "
                       "\U0001F4E6 Delivered.",
               error="Pick one of the six statuses \u2014 the colours, the "
                     "counts and the dashboard all depend on them.")
    K.tick_dv(bk, KEY, ["wrapped", "delivered"])
    K.date_dv(bk, KEY, ["deadline"],
              message="The last day you can buy this and still be ready. "
                      "Turns red when it passes.")
    K.money_dv(bk, KEY, ["budget", "cost"])

    # ------------------------------------------------------------------
    # conditional formatting
    # ------------------------------------------------------------------
    n = C.ROW_FIRST
    st = bk.col(KEY, "status")
    K.status_cf(bk, KEY, "status", {
        C.ST_IDEA: (th.plum_soft, th.plum),
        C.ST_NEED: (th.warn_soft, th.warn),
        C.ST_ORDERED: (th.info_soft, th.info),
        C.ST_BOUGHT: (th.ok_soft, th.ok),
        C.ST_WRAPPED: (th.gold_soft, th.gold),
        C.ST_DELIVERED: (th.primary_soft, th.primary),
    })
    # money: under / over budget
    diff = bk.col(KEY, "diff")
    bk.cond(KEY, n, ci(diff), C.last_row(KEY), ci(diff), {
        "type": "formula", "criteria": '=$%s%d<0' % (diff, n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond(KEY, n, ci(diff), C.last_row(KEY), ci(diff), {
        "type": "formula", "criteria": '=$%s%d>0' % (diff, n),
        "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})
    # % of budget: data bar + red over 100%
    pct = bk.col(KEY, "pct")
    K.databar(bk, KEY, "pct", color=th.gold)
    bk.cond(KEY, n, ci(pct), C.last_row(KEY), ci(pct), {
        "type": "formula", "criteria": '=$%s%d>1' % (pct, n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    # buy-by date
    K.deadline_cf(bk, KEY, "deadline", "delivered")
    # ticks
    K.tick_cf(bk, KEY, ["wrapped", "delivered"])
    # deadline alert column
    alert = bk.col(KEY, "alert")
    for text, (bg, fg) in (("\u2705 Done", (th.primary_soft, th.primary)),
                           ("\U0001F534 Overdue", (th.bad_soft, th.bad)),
                           ("\U0001F7E0 Due soon", (th.warn_soft, th.warn)),
                           ("\U0001F7E2 On track", (th.ok_soft, th.ok))):
        bk.cond(KEY, n, ci(alert), C.last_row(KEY), ci(alert), {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (alert, n, text),
            "format": S.cf(bg=bg, fg=fg, bold=True)})
    # nudge: a gift with no budget yet
    budget = bk.col(KEY, "budget")
    idea = bk.col(KEY, "idea")
    bk.cond(KEY, n, ci(budget), C.last_row(KEY), ci(budget), {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d="")' % (idea, n, budget, n),
        "format": S.cf(bg=th.gold_soft, fg=th.warn, bold=True)})
    # whole-row tint once a gift is wrapped / handed over (lowest priority)
    dlv = bk.col(KEY, "delivered")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=OR($%s%d="%s",$%s%d="%s")' % (st, n, C.ST_DELIVERED,
                                                    dlv, n, C.TICK),
        "format": S.cf(bg=th.primary_soft, fg=th.primary)})

    # ------------------------------------------------------------------
    # totals
    # ------------------------------------------------------------------
    total_row = C.last_row(KEY) + 2
    j, k, l = (bk.col(KEY, "budget"), bk.col(KEY, "cost"), bk.col(KEY, "diff"))
    K.totals_row(
        bk, KEY, total_row,
        {
            "budget": ("=SUM($%s$%d:$%s$%d)" % (j, C.ROW_FIRST, j,
                                                C.last_row(KEY)),
                       "#,##0.00", m.agg["gift_budget_planned"]),
            "cost": ("=SUM($%s$%d:$%s$%d)" % (k, C.ROW_FIRST, k,
                                              C.last_row(KEY)),
                     "#,##0.00", m.agg["gift_actual_spent"]),
            "diff": ("=SUM($%s$%d:$%s$%d)" % (l, C.ROW_FIRST, l,
                                              C.last_row(KEY)),
                     "#,##0.00",
                     m.agg["gift_budget_planned"] - m.agg["gift_actual_spent"]),
            "pct": ("=IFERROR(SUM($%s$%d:$%s$%d)/SUM($%s$%d:$%s$%d),\"\")"
                    % (k, C.ROW_FIRST, k, C.last_row(KEY),
                       j, C.ROW_FIRST, j, C.last_row(KEY)),
                    "0%",
                    (m.agg["gift_actual_spent"] / m.agg["gift_budget_planned"])
                    if m.agg["gift_budget_planned"] else ""),
        },
        label="  TOTALS \u2014 gift list", label_span=("B", "I"),
        last_col=LAST_COL)
    summary_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                               bg_color=th.primary, align="center",
                               valign="vcenter", border=1,
                               border_color=th.primary))
    ws.merge_range(r(total_row), ci("N"), r(total_row), ci(LAST_COL), "",
                   summary_fmt)
    text = ('="\u2705 "&%s&" of "&%s&" gifts bought   \u2022   \U0001F380 "'
            '&%s&" wrapped   \u2022   \U0001F4E6 "&%s&" handed over"'
            % (bk.kpi("gifts_purchased"), bk.kpi("gifts_planned"),
               bk.kpi("gifts_wrapped"), bk.kpi("gifts_delivered")))
    cached = ("\u2705 %d of %d gifts bought   \u2022   \U0001F380 %d wrapped"
              "   \u2022   \U0001F4E6 %d handed over"
              % (m.agg["gifts_purchased"], m.agg["gifts_planned"],
                 m.agg["gifts_wrapped"], m.agg["gifts_delivered"]))
    ws.write_formula(r(total_row), ci("N"), text, summary_fmt, cached)
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # tips + navigation
    # ------------------------------------------------------------------
    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  One row = one present. Need more than 60? Click row 67, "
         "drag down, and the formulas, dropdowns and colours come with it.",
         "\u2022  Status is the pipeline (\U0001F4A1 \u2192 \U0001F4E6). The "
         "\U0001F380 Wrapped and \U0001F4E6 Given tick boxes are quick "
         "shortcuts \u2014 ticking one, or moving the status on, both count.",
         "\u2022  Paste a product link in the Link column and the "
         "\U0001F517 column turns into a clickable button.",
         "\u2022  Everything on the \U0001F384 Dashboard, the \U0001F4B0 "
         "Budget tab and the \U0001F380 Wrapping tab reads from this sheet "
         "\u2014 you never re-type a gift twice."],
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


# ---------------------------------------------------------------------------
def _row_formulas(bk, n):
    def L(f):
        return bk.col(KEY, f)

    return {
        "n": '=IF($%s%d="","",ROW()-%d)' % (L("recipient"), n, C.ROW_FIRST - 1),
        "open": '=IF($%s%d="","",HYPERLINK($%s%d,"\U0001F517"))'
                % (L("link"), n, L("link"), n),
        "diff": '=IF($%s%d="","",IF($%s%d="",0,$%s%d)-$%s%d)'
                % (L("cost"), n, L("budget"), n, L("budget"), n, L("cost"), n),
        "pct": '=IF(OR($%s%d="",$%s%d="",$%s%d=0),"",$%s%d/$%s%d)'
               % (L("cost"), n, L("budget"), n, L("budget"), n,
                  L("cost"), n, L("budget"), n),
        "days": '=IF($%s%d="","",$%s%d-TODAY())'
                % (L("deadline"), n, L("deadline"), n),
        "alert": ('=IF($%s%d="","",IF(OR($%s%d="%s",$%s%d="%s"),"\u2705 Done",'
                 'IF($%s%d="","",IF($%s%d<TODAY(),"\U0001F534 Overdue",'
                 'IF($%s%d-TODAY()<=DueSoonDays,"\U0001F7E0 Due soon",'
                 '"\U0001F7E2 On track")))))'
                 % (L("recipient"), n, L("status"), n, C.ST_DELIVERED,
                    L("delivered"), n, C.TICK, L("deadline"), n,
                    L("deadline"), n, L("deadline"), n)),
    }


def _row_cached(m, i):
    """Cached values for the automatic columns (demo mode)."""
    from datetime import date as _date
    today = _date.today()
    if i >= len(m.gifts):
        return {"n": "", "open": "", "diff": "", "pct": "", "days": "",
                "alert": ""}
    g = m.gifts[i]
    budget, cost = g["budget"], g["cost"]
    dl = g["deadline"]
    diff = "" if cost is None else (budget or 0) - cost
    pct = "" if (cost is None or not budget) else cost / float(budget)
    days = "" if not dl else (dl - today).days
    if g["status"] == C.ST_DELIVERED or g["delivered"] == C.TICK:
        alert = "\u2705 Done"
    elif not dl:
        alert = ""
    elif dl < today:
        alert = "\U0001F534 Overdue"
    elif (dl - today).days <= m.settings["duesoon"]:
        alert = "\U0001F7E0 Due soon"
    else:
        alert = "\U0001F7E2 On track"
    return {"n": i + 1, "open": "\U0001F517" if g["link"] else "",
            "diff": diff, "pct": pct, "days": days, "alert": alert}
