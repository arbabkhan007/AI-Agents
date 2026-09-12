"""
\U0001F4B0 Budget - planned vs. actual for every corner of the season.

The "Auto from trackers" column is what makes this tab different from a plain
budget sheet: gift money, shopping-list money, stocking money and postage are
pulled in from the other tabs, so the total is always true.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "budget"
LAST_COL = "K"
FIRST = C.BUD_FIRST
LAST = C.BUD_FIRST + C.BUDGET_ROWS - 1
TOTAL = C.BUD_TOTAL

COLUMNS = [
    ("category", "Category", "text", None),
    ("planned", "Planned budget", "money", None),
    ("manual", "Extra spend (type here)", "money", None),
    ("auto", "Pulled in automatically", "calc_money", "primary_2"),
    ("actual", "Total spent", "calc_money", "primary_2"),
    ("remaining", "Remaining", "calc_money", "primary_2"),
    ("pct", "% used", "calc_pct", "primary_2"),
    ("status", "Status", "calc_c", "primary_2"),
    ("bar", "Progress", "calc", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S = bk.S
    th = bk.th
    m = bk.demo

    bk.widths(KEY, {"A": 2.2, "B": 30, "C": 13, "D": 13, "E": 14, "F": 13,
                    "G": 13, "H": 10, "I": 17, "J": 24, "K": 26})
    bk.paint(KEY, 0, 0, 72, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F4B0  Christmas Budget",
        "  Plan it, watch it, and get told the moment you are about to "
        "overspend.",
        LAST_COL)

    # ------------------------------------------------------------------
    # overview cards
    # ------------------------------------------------------------------
    ws.set_row(r(7), 24)
    ws.merge_range(r(7), 1, r(7), ci(LAST_COL),
                   "  \U0001F4B0  MONEY OVERVIEW", S.section)

    planned_sum = "SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "planned"), FIRST,
                                          bk.col(KEY, "planned"), LAST)
    actual_sum = "SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "actual"), FIRST,
                                         bk.col(KEY, "actual"), LAST)
    cards = [
        ("B", "C", "TOTAL PLANNED BUDGET", "primary",
         '=Currency&TEXT(%s,"#,##0")' % planned_sum,
         m.money(m.agg["budget_planned"])),
        ("D", "E", "SPENT SO FAR", "accent",
         '=Currency&TEXT(%s,"#,##0")' % actual_sum,
         m.money(m.agg["budget_actual"])),
        ("F", "G", "STILL TO SPEND", "ok",
         '=Currency&TEXT(%s-%s,"#,##0")' % (planned_sum, actual_sum),
         m.money(m.agg["budget_remaining"])),
        ("H", "I", "BUDGET USED", "gold",
         "=IFERROR(%s/%s,0)" % (actual_sum, planned_sum),
         m.agg["budget_pct"]),
    ]
    ws.set_row(r(8), 18)
    ws.set_row(r(9), 36)
    for c1, c2, label, color, formula, cached in cards:
        ws.merge_range(r(8), ci(c1), r(8), ci(c2), "  " + label,
                       S.kpi_label(getattr(th, color)))
        if c1 == "H":
            fmt = S.kpi_value(getattr(th, color), num_format="0%", size=22)
        else:
            fmt = S.kpi_value(getattr(th, color), size=19, align="center")
        ws.merge_range(r(9), ci(c1), r(9), ci(c2), "", fmt)
        ws.write_formula(r(9), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    # alert card (two rows tall)
    ws.merge_range(r(8), ci("J"), r(8), ci(LAST_COL), "",
                   S.kpi_label(th.bad))
    ws.write(r(8), ci("J"), "  \u26A0\uFE0F  BUDGET ALERT",
             S.kpi_label(th.bad))
    alert_fmt = S.f(**S.base(font_size=10.5, bold=True, font_color=th.white,
                             bg_color=th.accent, align="left",
                             valign="vcenter", text_wrap=True, indent=1))
    ws.merge_range(r(9), ci("J"), r(9), ci(LAST_COL), "", alert_fmt)
    alert = ('=IF({p}<=0,"\U0001F4DD  Add your planned budgets below to '
             'switch on the alerts.",IF({a}>{p},"\U0001F534  Over budget by "'
             '&Currency&TEXT({a}-{p},"#,##0.00")&" \u2014 pause the '
             'non-essentials.",IF({a}/{p}>=AlertAt,"\u26A0\uFE0F  You\'ve '
             'spent "&TEXT({a}/{p},"0%")&" of your "&EventName&" budget '
             '\u2014 "&Currency&TEXT({p}-{a},"#,##0.00")&" left to '
             'play with.","\U0001F7E2  On track \u2014 "&TEXT({a}/{p},"0%")'
             '&" used, "&Currency&TEXT({p}-{a},"#,##0.00")&" still to '
             'spend.")))').format(p=planned_sum, a=actual_sum)
    ws.write_formula(r(9), ci("J"), alert, alert_fmt, m.agg["budget_alert"])
    bk.stats["formulas"] += 1

    # progress bar
    ws.set_row(r(10), 22)
    ws.merge_range(r(10), ci("B"), r(10), ci("C"), "  Budget progress",
                   S.bar_label)
    ws.merge_range(r(10), ci("D"), r(10), ci(LAST_COL), "", S.bar_text)
    bar = ('=IFERROR(REPT("\u2588",ROUND(MIN(1,{a}/{p})*34,0))&REPT("\u2591",'
           '34-ROUND(MIN(1,{a}/{p})*34,0))&"   "&TEXT({a}/{p},"0%"),"'
           '\u2591\u2591\u2591")').format(p=planned_sum, a=actual_sum)
    ws.write_formula(r(10), ci("D"), bar, S.bar_text,
                     m.agg["bar_budget"] + "   %d%%"
                     % round(m.agg["budget_pct"] * 100))
    bk.stats["formulas"] += 1

    # quick facts
    ws.set_row(r(11), 24)
    facts = [
        ("B", "C", "primary",
         '="\U0001F381 Gifts are "&TEXT(IFERROR($%s%d/%s,0),"0%%")&" of '
         'everything"' % (bk.col(KEY, "actual"), FIRST, actual_sum),
         "\U0001F381 Gifts are %d%% of everything"
         % round(100 * (m.agg["budget_rows"][0]["actual"] /
                        m.agg["budget_actual"])) if m.agg["budget_actual"]
         else "\U0001F381 Gifts are 0% of everything"),
        ("D", "F", "info",
         '="\U0001F4C8 Biggest spend: "&IFERROR(INDEX($%s$%d:$%s$%d,'
         'MATCH(MAX($%s$%d:$%s$%d),$%s$%d:$%s$%d,0)),"\u2014")'
         % ((bk.col(KEY, "category"), FIRST, bk.col(KEY, "category"), LAST)
            + (bk.col(KEY, "actual"), FIRST, bk.col(KEY, "actual"), LAST)
            + (bk.col(KEY, "actual"), FIRST, bk.col(KEY, "actual"), LAST)),
         "\U0001F4C8 Biggest spend: %s"
         % max(m.agg["budget_rows"], key=lambda x: x["actual"])["label"]
         if m.agg["budget_actual"] else "\U0001F4C8 Biggest spend: \u2014"),
        ("G", "H", "bad",
         '=COUNTIF($%s$%d:$%s$%d,"<0")&" over budget"'
         % (bk.col(KEY, "remaining"), FIRST, bk.col(KEY, "remaining"), LAST),
         "%d over budget" % len([x for x in m.agg["budget_rows"]
                                 if x["remaining"] < 0])),
        ("I", LAST_COL, "gold",
         '="\U0001F3AF Target "&Currency&TEXT(TotalBudget,"#,##0")&"   '
         '\u2022   planned "&Currency&TEXT(%s,"#,##0")' % planned_sum,
         "\U0001F3AF Target %s   \u2022   planned %s"
         % (m.money(m.settings["budget"]), m.money(m.agg["budget_planned"]))),
    ]
    for c1, c2, color, formula, cached in facts:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10, bold=True,
                     align="left")
        ws.merge_range(r(11), ci(c1), r(11), ci(c2), "", fmt)
        ws.write_formula(r(11), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1
    ws.set_row(r(12), 8)

    # ------------------------------------------------------------------
    # the table
    # ------------------------------------------------------------------
    ws.set_row(r(13), 24)
    ws.merge_range(r(13), 1, r(13), ci(LAST_COL),
                   "  \U0001F4CB  BUDGET BY CATEGORY   (white = you type, "
                   "tinted = automatic)", S.section_soft)
    K.header_row(bk, KEY, COLUMNS, row=C.BUD_HEADER, height=34)
    for i in range(C.BUDGET_ROWS):
        ws.set_row(r(FIRST + i), 22)
    for i in range(C.BUDGET_ROWS):
        rownum = FIRST + i
        a = K.alt(rownum)
        for field, label, kind, color in COLUMNS:
            ws.write_blank(r(rownum), ci(bk.col(KEY, field)), None,
                           S.cell(kind, a) if not kind.startswith("calc")
                           else S.cell(kind))
    for i, (label, bkey, recipe, demo_planned) in enumerate(C.BUDGET_CATEGORIES):
        rownum = FIRST + i
        cached_row = m.agg["budget_rows"][i]
        bar_fmt = S.f(**S.base(font_name=th.mono_font, font_size=10,
                               bold=True, font_color=th.primary_2,
                               bg_color=th.card, align="left",
                               valign="vcenter", border=1,
                               border_color=th.border, locked=True))
        values = {
            "category": label,
            # demo mode: use the calculator's planned amounts (demo.py
            # BUDGET_PLANNED) so the cached row values agree with what Excel
            # recalculates from the written cells.
            "planned": (m.budget_planned.get(bkey, demo_planned)
                        if bk.mode == "demo" else None),
            "manual": m.budget_manual.get(bkey) if bk.mode == "demo" else None,
            "auto": _auto_formula(bk, recipe, rownum),
            "actual": "=$%s%d+$%s%d" % (bk.col(KEY, "manual"), rownum,
                                        bk.col(KEY, "auto"), rownum),
            "remaining": "=$%s%d-$%s%d" % (bk.col(KEY, "planned"), rownum,
                                           bk.col(KEY, "actual"), rownum),
            "pct": '=IF($%s%d=0,"",$%s%d/$%s%d)'
                   % (bk.col(KEY, "planned"), rownum, bk.col(KEY, "actual"),
                      rownum, bk.col(KEY, "planned"), rownum),
            "status": _status_formula(bk, rownum),
            "bar": _bar_formula(bk, rownum),
            "notes": "",
        }
        cached = {
            "auto": cached_row["auto"], "actual": cached_row["actual"],
            "remaining": cached_row["remaining"], "pct": cached_row["pct"],
            "status": _status_cached(cached_row, m),
            "bar": _bar_cached(cached_row),
        }
        K.write_row(bk, KEY, COLUMNS, rownum, values, cached)
        # the progress column wants its own mono format
        ws.write_formula(r(rownum), ci(bk.col(KEY, "bar")),
                         values["bar"], bar_fmt, cached["bar"])

    # totals row
    tcols = {}
    for field in ("planned", "manual", "auto", "actual", "remaining"):
        col = bk.col(KEY, field)
        cached_key = {"planned": "budget_planned", "actual": "budget_actual",
                      "remaining": "budget_remaining"}.get(field)
        cached_val = m.agg[cached_key] if cached_key else sum(
            x[field] for x in m.agg["budget_rows"])
        tcols[field] = ("=SUM($%s$%d:$%s$%d)" % (col, FIRST, col, LAST),
                        "#,##0.00", cached_val)
    tcols["pct"] = ("=IFERROR(%s/%s,\"\")" % (actual_sum, planned_sum), "0%",
                    m.agg["budget_pct"])
    K.totals_row(bk, KEY, TOTAL, tcols, label="  TOTAL",
                 label_span=("B", "B"), last_col=LAST_COL)
    ws.merge_range(r(TOTAL), ci("I"), r(TOTAL), ci(LAST_COL), "",
                   S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                                bg_color=th.primary, align="center",
                                valign="vcenter", border=1,
                                border_color=th.primary)))
    ws.write_formula(r(TOTAL), ci("I"),
                     '=IF(%s=0,"\u2014","Budget "&TEXT(%s/%s,"0%%")&" used  '
                     '\u2022  "&Currency&TEXT(%s-%s,"#,##0")&" left")'
                     % (planned_sum, actual_sum, planned_sum, planned_sum,
                        actual_sum),
                     S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                                  bg_color=th.primary, align="center",
                                  valign="vcenter", border=1,
                                  border_color=th.primary)),
                     "Budget %d%% used  \u2022  %s left"
                     % (round(100 * m.agg["budget_pct"]),
                        m.money(m.agg["budget_remaining"]))
                     if m.agg["budget_planned"] else "\u2014")
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # conditional formatting
    # ------------------------------------------------------------------
    n = FIRST
    K.databar(bk, KEY, "pct", color=th.gold, first=FIRST, last=LAST)
    pct_col = ci(bk.col(KEY, "pct"))
    bk.cond(KEY, n, pct_col, LAST, pct_col, {
        "type": "formula", "criteria": '=$%s%d>1' % (bk.col(KEY, "pct"), n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond(KEY, n, pct_col, LAST, pct_col, {
        "type": "formula",
        "criteria": '=AND($%s%d<=1,$%s%d>=AlertAt)'
                   % (bk.col(KEY, "pct"), n, bk.col(KEY, "pct"), n),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    rem_col = ci(bk.col(KEY, "remaining"))
    bk.cond(KEY, n, rem_col, LAST, rem_col, {
        "type": "formula",
        "criteria": '=$%s%d<0' % (bk.col(KEY, "remaining"), n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    status_col = ci(bk.col(KEY, "status"))
    for text, (bg, fg) in (("\U0001F534 Over budget", (th.bad_soft, th.bad)),
                           ("\U0001F7E0 Nearly there", (th.warn_soft, th.warn)),
                           ("\U0001F7E2 On track", (th.ok_soft, th.ok)),
                           ("\u26AA Not started", (th.alt, th.muted)),
                           ("\u26AA Set a plan", (th.alt, th.muted))):
        bk.cond(KEY, n, status_col, LAST, status_col, {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (bk.col(KEY, "status"), n, text),
            "format": S.cf(bg=bg, fg=fg, bold=True)})
    bk.cond(KEY, n, ci("B"), LAST, ci(LAST_COL), {
        "type": "formula",
        "criteria": '=$%s%d<0' % (bk.col(KEY, "remaining"), n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad)})

    # ------------------------------------------------------------------
    # charts
    # ------------------------------------------------------------------
    ws.set_row(r(26), 8)
    ws.set_row(r(27), 24)
    ws.merge_range(r(27), 1, r(27), ci(LAST_COL),
                   "  \U0001F4CA  BUDGET vs ACTUAL", S.section)
    cats = "=%s!$%s$%d:$%s$%d" % (bk.q(KEY), bk.col(KEY, "category"), FIRST,
                                  bk.col(KEY, "category"), LAST)
    planned_vals = "=%s!$%s$%d:$%s$%d" % (bk.q(KEY), bk.col(KEY, "planned"),
                                          FIRST, bk.col(KEY, "planned"), LAST)
    actual_vals = "=%s!$%s$%d:$%s$%d" % (bk.q(KEY), bk.col(KEY, "actual"),
                                         FIRST, bk.col(KEY, "actual"), LAST)

    ch1 = bk.chart("column")
    ch1.add_series({"name": "Planned", "categories": cats,
                    "values": planned_vals,
                    "fill": {"color": th.primary_soft and "#BFD3C2"},
                    "border": {"color": th.primary},
                    "gap": 60})
    ch1.add_series({"name": "Actually spent", "categories": cats,
                    "values": actual_vals, "fill": {"color": th.accent},
                    "border": {"color": th.accent}})
    ch1.set_title({"name": "Planned vs actually spent, by category",
                   "name_font": {"size": 12, "bold": True, "color": th.primary,
                                 "name": th.body_font}})
    ch1.set_y_axis({"num_format": "#,##0", "num_font": {"size": 9},
                    "major_gridlines": {"visible": True,
                                        "line": {"color": th.border}}})
    ch1.set_x_axis({"num_font": {"size": 9}, "label_position": "low"})
    ch1.set_size({"width": 560, "height": 290})
    ch1.set_legend({"position": "bottom", "font": {"size": 9}})
    ch1.set_style(2)
    ws.insert_chart(r(28), ci("B"), ch1, {"x_offset": 6, "y_offset": 6})

    ch2 = bk.chart("doughnut")
    ch2.add_series({
        "name": "Spent", "categories": cats, "values": actual_vals,
        "points": [{"fill": {"color": c}} for c in th.series],
        "data_labels": {"percentage": True, "font": {"size": 9,
                                                     "color": th.white}},
    })
    ch2.set_title({"name": "Where the money actually goes",
                   "name_font": {"size": 12, "bold": True,
                                 "color": th.primary, "name": th.body_font}})
    ch2.set_hole_size(58)
    ch2.set_size({"width": 540, "height": 290})
    ch2.set_legend({"position": "right", "font": {"size": 9}})
    ws.insert_chart(r(28), ci("G"), ch2, {"x_offset": 6, "y_offset": 6})

    # ------------------------------------------------------------------
    # notes + nav
    # ------------------------------------------------------------------
    row = 44
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  \u201CPlanned budget\u201D and \u201CExtra spend\u201D are "
         "the only two columns you type in.",
         "\u2022  \u201CPulled in automatically\u201D adds up the money from "
         "the \U0001F381 Gift Tracker, \U0001F6CD\uFE0F Shopping List, "
         "\U0001F9E6 Stockings and \U0001F48C Card postage \u2014 so this "
         "total is always honest.",
         "\u2022  Set the warning level in \u2699\uFE0F Setup (\u201CWarn me "
         "when spending reaches\u201D). At that point the alert card, the "
         "status column and the dashboard all change colour.",
         "\u2022  Add your own category? Insert a row above the TOTAL row and "
         "everything (including the charts) picks it up."],
        title="  \U0001F4A1  How this tab works")
    row += 1
    ws.set_row(r(row), 26)
    row = bk.nav_row(KEY, row, first_col=1, span=2,
                     max_col=LAST_COL) + 2
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  %s v%s  \u2022  %s" % (C.PRODUCT, C.VERSION, C.TAGLINE),
                   S.footer)
    bk.page(KEY, LAST_COL, row + 2, landscape=True, title_rows=(0, 13))
    return ws


# ---------------------------------------------------------------------------
def _auto_formula(bk, recipe, rownum):
    terms = []
    for term in recipe:
        if term == "gifts":
            terms.append("SUM(%s)" % bk.rng("gifts", "cost"))
        elif term == "stock":
            if bk.has("stockings"):
                terms.append("SUM(%s)" % bk.rng("stockings", "spent"))
        elif term == "cards":
            if bk.has("cards"):
                terms.append("SUM(%s)" % bk.rng("cards", "postage"))
        elif term.startswith("shop:"):
            cat = term.split(":", 1)[1]
            if bk.has("shopping"):
                terms.append('SUMIFS(%s,%s,"%s")'
                             % (bk.rng("shopping", "spent"),
                                bk.rng("shopping", "category"), cat))
    if not terms:
        return "=0"
    return "=" + "+".join(terms)


def _status_formula(bk, n):
    planned = "$%s%d" % (bk.col(KEY, "planned"), n)
    actual = "$%s%d" % (bk.col(KEY, "actual"), n)
    return ('=IF({p}=0,"\u26AA Set a plan",IF({a}>{p},"\U0001F534 Over '
            'budget",IF({a}/{p}>=AlertAt,"\U0001F7E0 Nearly there",'
            'IF({a}=0,"\u26AA Not started","\U0001F7E2 On track"))))'
            ).format(p=planned, a=actual)


def _status_cached(row, m):
    if not row["planned"]:
        return "\u26AA Set a plan"
    if row["actual"] > row["planned"]:
        return "\U0001F534 Over budget"
    if row["pct"] and row["pct"] >= m.settings["alert"]:
        return "\U0001F7E0 Nearly there"
    if not row["actual"]:
        return "\u26AA Not started"
    return "\U0001F7E2 On track"


def _bar_formula(bk, n):
    planned = "$%s%d" % (bk.col(KEY, "planned"), n)
    actual = "$%s%d" % (bk.col(KEY, "actual"), n)
    blocks = 12
    pct = "MIN(1,IFERROR({a}/{p},0))".format(a=actual, p=planned)
    filled = "ROUND(%s*%d,0)" % (pct, blocks)
    return ('=IF({p}=0,"\u2014",REPT("\u2588",{f})&REPT("\u2591",{b}-{f})'
            '&" "&TEXT(IFERROR({a}/{p},0),"0%"))').format(p=planned, a=actual,
                                                          f=filled, b=blocks)


def _bar_cached(row, blocks=12):
    if not row["planned"]:
        return "\u2014"
    pct = min(1.0, max(0.0, (row["actual"] or 0) / float(row["planned"])))
    filled = int(round(pct * blocks))
    return ("\u2588" * filled + "\u2591" * (blocks - filled) + " %d%%"
            % round(pct * 100))
