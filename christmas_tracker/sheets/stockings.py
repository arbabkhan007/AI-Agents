"""
\U0001F9E6 Stocking Stuffers - one row per little present, plus a
per-stocking summary so every stocking ends up equally spoiled (and equally
affordable).
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "stockings"
LAST_COL = "L"
OWNER_ROWS = 8

COLUMNS = [
    ("n", "#", "idx", None),
    ("owner", "Stocking", "text", None),
    ("item", "Item", "text", None),
    ("category", "Type", "center", None),
    ("budget", "Budget", "money", None),
    ("cost", "Cost", "money", None),
    ("bought", "Bought", "tick", None),
    ("wrapped", "Wrapped", "tick", None),
    ("spent", "In budget (auto)", "calc_money", "primary_2"),
    ("hiding", "\U0001F648 Hiding spot", "text", None),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 34, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F9E6  Stocking Stuffer Tracker",
        "  The little things add up fastest \u2014 budget them per stocking "
        "and stop the January regret.",
        LAST_COL)

    chips = [
        ("B", "C", "\U0001F9E6 Stockings: ", None, "primary"),
        ("D", "E", "\U0001F381 Items: ", "stock_items", "info"),
        ("F", "G", "\u2705 Bought: ", "stock_bought", "ok"),
        ("H", "I", "\U0001F4B0 Budget: ", "stock_budget", "gold"),
        ("J", "K", "\U0001F4B8 Spent: ", "stock_spent", "accent"),
        ("L", LAST_COL, "\U0001F3AF Left: ", None, "primary_2"),
    ]
    for c1, c2, label, kpi_key, color in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        if c1 == c2:
            ws.write(r(C.ROW_STATS), ci(c1), "", fmt)
        else:
            ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2),
                           "", fmt)
        if kpi_key in ("stock_budget", "stock_spent"):
            formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label,
                                                           bk.kpi(kpi_key))
            cached = "%s%s" % (label, m.money(m.agg[kpi_key]))
        elif kpi_key:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        elif label.startswith("\U0001F9E6"):
            formula = '="%s"&COUNTA(%s)' % (label, bk.rng(KEY, "owner"))
            cached = "%s%d" % (label, len(set(x["owner"] for x in m.stockings)))
        else:
            formula = '="%s"&Currency&TEXT(%s-%s,"#,##0")' % (
                label, bk.kpi("stock_budget"), bk.kpi("stock_spent"))
            cached = "%s%s" % (label, m.money(m.agg["stock_budget"] -
                                              m.agg["stock_spent"]))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = {"n": '=IF($%s%d="","",ROW()-%d)'
                         % (bk.col(KEY, "item"), rownum, C.ROW_FIRST - 1),
                  "spent": '=IF($%s%d="","",IF($%s%d="%s",IF($%s%d<>"",$%s%d,'
                           'IF($%s%d<>"",$%s%d,0)),0))'
                           % (bk.col(KEY, "owner"), rownum,
                              bk.col(KEY, "bought"), rownum, C.TICK,
                              bk.col(KEY, "cost"), rownum, bk.col(KEY, "cost"),
                              rownum, bk.col(KEY, "budget"), rownum,
                              bk.col(KEY, "budget"), rownum)}
        if i < len(m.stockings):
            s = m.stockings[i]
            values.update({k: s[k] for k in
                           ("owner", "item", "category", "budget", "cost",
                            "bought", "wrapped", "hiding", "notes")})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    K.list_dv(bk, KEY, "owner", "stocking_owners", title="Whose stocking?",
              message="Add or change stockings in \u2699\uFE0F Setup \u2192 "
                      "Stocking owners.")
    K.list_dv(bk, KEY, "category", "stocking_items", title="Type of filler")
    K.tick_dv(bk, KEY, ["bought", "wrapped"])
    K.money_dv(bk, KEY, ["budget", "cost"])
    ws.data_validation(r(C.ROW_FIRST), ci(bk.col(KEY, "hiding")),
                       r(C.last_row(KEY)), ci(bk.col(KEY, "hiding")),
                       {"validate": "list",
                        "source": "=" + bk.listname("hiding_spots"),
                        "ignore_blank": True, "show_input": True,
                        "input_title": "Where is it hiding?",
                        "input_message": "Pick a spot or type your own.",
                        "show_error": True, "error_type": "warning",
                        "error_title": "Free text is fine",
                        "error_message": "Add your own spots to the list in "
                                         "\u2699\uFE0F Setup."})
    bk.stats["validations"] += 1

    n = C.ROW_FIRST
    K.tick_cf(bk, KEY, ["bought", "wrapped"])
    K.secret_cf(bk, KEY, "hiding")
    bought = bk.col(KEY, "bought")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula", "criteria": '=$%s%d="%s"' % (bought, n, C.TICK),
        "format": S.cf(bg=th.ok_soft, fg=th.muted, strike=True)})

    total_row = C.last_row(KEY) + 2
    K.totals_row(
        bk, KEY, total_row,
        {"budget": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "budget"),
                                             C.ROW_FIRST,
                                             bk.col(KEY, "budget"),
                                             C.last_row(KEY)),
                    "#,##0.00", m.agg["stock_budget"]),
         "cost": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "cost"), C.ROW_FIRST,
                                           bk.col(KEY, "cost"),
                                           C.last_row(KEY)),
                  "#,##0.00", sum(x["cost"] or 0 for x in m.stockings)),
         "spent": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "spent"),
                                            C.ROW_FIRST,
                                            bk.col(KEY, "spent"),
                                            C.last_row(KEY)),
                   "#,##0.00", m.agg["stock_spent"])},
        label="  TOTALS", label_span=("B", "E"), last_col=LAST_COL)
    fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                       bg_color=th.primary, align="center", valign="vcenter",
                       border=1, border_color=th.primary))
    ws.merge_range(r(total_row), ci("H"), r(total_row), ci(LAST_COL), "", fmt)
    ws.write_formula(
        r(total_row), ci("H"),
        '="\U0001F9E6 Stocking budget: "&Currency&TEXT(%s,"#,##0")&'
        '"   \u2022   spent: "&Currency&TEXT(%s,"#,##0")&"   \u2022   '
        'remaining: "&Currency&TEXT(%s-%s,"#,##0")'
        % (bk.kpi("stock_budget"), bk.kpi("stock_spent"),
           bk.kpi("stock_budget"), bk.kpi("stock_spent")), fmt,
        "\U0001F9E6 Stocking budget: %s   \u2022   spent: %s   \u2022   "
        "remaining: %s" % (m.money(m.agg["stock_budget"]),
                           m.money(m.agg["stock_spent"]),
                           m.money(m.agg["stock_budget"] -
                                   m.agg["stock_spent"])))
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # per-stocking summary
    # ------------------------------------------------------------------
    row = total_row + 2
    ws.set_row(r(row), 24)
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F9E6  EACH STOCKING AT A GLANCE  (automatic)",
                   S.section_soft)
    row += 1
    heads = [("C", "Stocking"), ("D", "Items"), ("E", "Budget"),
             ("F", "Spent"), ("G", "Remaining"), ("H", "Bought"),
             ("I", "Wrapped"), ("J", "Progress")]
    ws.set_row(r(row), 26)
    for col, label in heads:
        c1 = ci(col)
        c2 = ci(LAST_COL) if col == "J" else c1
        if c2 > c1:
            ws.merge_range(r(row), c1, r(row), c2, label, S.header(th.primary))
        else:
            ws.write(r(row), c1, label, S.header(th.primary))
    for i in range(OWNER_ROWS):
        row += 1
        ws.set_row(r(row), 20)
        setup_row = C.SU_LIST_FIRST + i
        owner_ref = "'%s'!$I$%d" % (C.SHEET_NAMES["setup"], setup_row)
        name_ref = "$C%d" % row
        a = K.alt(row)
        owner_rng = bk.rng(KEY, "owner")
        spent_rng = bk.rng(KEY, "spent")
        budget_rng = bk.rng(KEY, "budget")
        bought_rng = bk.rng(KEY, "bought")
        wrapped_rng = bk.rng(KEY, "wrapped")
        cells = [
            ("C", '=IF(%s="","",%s)' % (owner_ref, owner_ref),
             S.cell("text", a, bold=True), m.owners[i] if i < len(m.owners)
             else ""),
            ("D", '=IF(%s="",0,COUNTIF(%s,%s))' % (name_ref, owner_rng,
                                                   name_ref),
             S.cell("calc_num"), _owner(m, i, "items")),
            ("E", '=IF(%s="",0,SUMIF(%s,%s,%s))' % (name_ref, owner_rng,
                                                    name_ref, budget_rng),
             S.cell("calc_money"), _owner(m, i, "budget")),
            ("F", '=IF(%s="",0,SUMIF(%s,%s,%s))' % (name_ref, owner_rng,
                                                    name_ref, spent_rng),
             S.cell("calc_money"), _owner(m, i, "spent")),
            ("G", '=IF(%s="","",%s)' % (name_ref, "$E%d-$F%d" % (row, row)),
             S.cell("calc_money"), _owner(m, i, "remaining")),
            ("H", '=IF(%s="",0,COUNTIFS(%s,%s,%s,"%s"))'
                  % (name_ref, owner_rng, name_ref, bought_rng, C.TICK),
             S.cell("calc_num"), _owner(m, i, "bought")),
            ("I", '=IF(%s="",0,COUNTIFS(%s,%s,%s,"%s"))'
                  % (name_ref, owner_rng, name_ref, wrapped_rng, C.TICK),
             S.cell("calc_num"),
             len([x for x in m.stockings
                  if i < len(m.owners) and x["owner"] == m.owners[i]
                  and x["wrapped"] == C.TICK])),
        ]
        for col, formula, fmt, cached in cells:
            ws.write_formula(r(row), ci(col), formula, fmt,
                             cached if cached is not None else 0)
            bk.stats["formulas"] += 1
        bar_fmt = S.f(**S.base(font_name=th.mono_font, font_size=10, bold=True,
                               font_color=th.primary_2, bg_color=th.card,
                               align="left", valign="vcenter", border=1,
                               border_color=th.border))
        ws.merge_range(r(row), ci("J"), r(row), ci(LAST_COL), "", bar_fmt)
        bar = ('=IF($C%d="","",REPT("\u2588",ROUND(MIN(1,IFERROR($F%d/$E%d,0))'
               '*16,0))&REPT("\u2591",16-ROUND(MIN(1,IFERROR($F%d/$E%d,0))*16,'
               '0))&"   "&TEXT(IFERROR($F%d/$E%d,0),"0%%")&" spent")'
               % ((row,) * 7))
        pct = 0
        bud = _owner(m, i, "budget") or 0
        spent = _owner(m, i, "spent") or 0
        pct = min(1.0, spent / float(bud)) if bud else 0
        filled = int(round(pct * 16))
        cached_bar = ""
        if i < len(m.owners):
            cached_bar = ("\u2588" * filled + "\u2591" * (16 - filled)
                          + "   %d%% spent" % round(pct * 100))
        ws.write_formula(r(row), ci("J"), bar, bar_fmt, cached_bar)
        bk.stats["formulas"] += 1

    row += 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  One stocking = one name in \u2699\uFE0F Setup \u2192 "
         "Stocking owners. The summary above rebuilds itself as you add rows.",
         "\u2022  Tick \u2713 Bought and the money moves into the "
         "\u201CStocking stuffers\u201D line of the \U0001F4B0 Budget tab.",
         "\u2022  Hiding spots respond to Secret Mode (\u2699\uFE0F Setup) "
         "just like the \U0001F380 Wrapping tab."],
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


def _owner(m, i, field):
    rows = m.agg["stock_by_owner"]
    if i >= len(rows):
        return ""
    val = rows[i][field]
    return val if val != "" else 0


def _cached(m, i):
    if i >= len(m.stockings):
        return {"n": "", "spent": ""}
    s = m.stockings[i]
    return {"n": i + 1, "spent": m._stock_spent(s)}
