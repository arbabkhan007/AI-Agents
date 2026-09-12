"""
\U0001F384 Dashboard - the "wow" page and the reason the product feels
premium.

Everything here is a formula: countdown, money, gift progress, text progress
bars, four charts, the "what's left to do" panel, the next five deadlines and
the per-recipient table.  Nothing is typed on this tab.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "dashboard"
LAST_COL = "M"
CARDS = [("B", "D"), ("E", "G"), ("H", "J"), ("K", "M")]

ROW_HERO_1, ROW_HERO_2, ROW_HERO_3 = 2, 3, 4
ROW_BUD_SEC, ROW_BUD_LBL, ROW_BUD_VAL, ROW_BUD_BAR = 6, 7, 8, 9
ROW_GIF_SEC = 11
ROW_GIF_LBL1, ROW_GIF_VAL1 = 12, 13
ROW_GIF_LBL2, ROW_GIF_VAL2 = 14, 15
ROW_GIF_BAR = 16
ROW_CHART_SEC = 18
ROW_CHART_1 = 19
ROW_CHART_2 = 34
ROW_PANEL_SEC = 49
ROW_PANEL = 50
ROW_REC_SEC = 61
ROW_REC_HDR = 62
ROW_REC_FIRST = 63
ROW_REC_TOTAL = 79
ROW_NAV_SEC = 81
ROW_NAV = 82
ROW_FOOTER = 88


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo
    agg = m.agg

    ws.set_column("A:A", 2.2)
    ws.set_column("B:M", 13)
    bk.paint(KEY, 0, 0, ROW_FOOTER + 2, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------------------
    # hero
    # ------------------------------------------------------------------
    ws.set_row(r(1), 8)
    ws.set_row(r(ROW_HERO_1), 40)
    ws.set_row(r(ROW_HERO_2), 34)
    ws.set_row(r(ROW_HERO_3), 20)
    title = ('="\U0001F384  "&EventName&" "&TEXT(EventDate,"yyyy")&'
             '"   \u2022   Gift Command Center"')
    ws.merge_range(r(ROW_HERO_1), 1, r(ROW_HERO_1), ci(LAST_COL), "",
                   S.hero_title)
    ws.write_formula(r(ROW_HERO_1), 1, title, S.hero_title,
                     "\U0001F384  %s %d   \u2022   Gift Command Center"
                     % (m.settings["event_name"], m.agg["event_year"]))
    ws.merge_range(r(ROW_HERO_2), 1, r(ROW_HERO_2), ci(LAST_COL), "",
                   S.hero_count)
    ws.write_formula(r(ROW_HERO_2), 1, "=" + _countdown(bk), S.hero_count,
                     agg["countdown"])
    ws.merge_range(r(ROW_HERO_3), 1, r(ROW_HERO_3), ci(LAST_COL), "",
                   S.hero_meta)
    meta = ('=TEXT(TODAY(),"dddd d mmmm yyyy")&"   \u2022   "&EventName&'
            '" falls on "&TEXT(EventDate,"dddd d mmmm yyyy")&"   \u2022   "'
            '&%s&" of "&%s&" gifts bought   \u2022   "&%s&" wrapped   '
            '\u2022   "&%s&" handed over   \u2022   by %s"'
            % (bk.kpi("gifts_purchased"), bk.kpi("gifts_planned"),
               bk.kpi("gifts_wrapped"), bk.kpi("gifts_delivered"),
               C.AUTHOR))
    ws.write_formula(r(ROW_HERO_3), 1, meta, S.hero_meta,
                     "%s   \u2022   %s falls on %s   \u2022   %d of %d gifts "
                     "bought   \u2022   %d wrapped   \u2022   %d handed over"
                     "   \u2022   by %s"
                     % (_today_text(), m.settings["event_name"],
                        m.event_date.strftime("%A %d %B %Y"),
                        agg["gifts_purchased"], agg["gifts_planned"],
                        agg["gifts_wrapped"], agg["gifts_delivered"],
                        C.AUTHOR))
    bk.stats["formulas"] += 3
    ws.set_row(r(5), 8)

    # ------------------------------------------------------------------
    # budget cards
    # ------------------------------------------------------------------
    _section(ws, S, ROW_BUD_SEC, "  \U0001F4B0  BUDGET AT A GLANCE")
    budget_cards = [
        ("TOTAL %s BUDGET" % m.settings["event_name"].upper(), "primary",
         '=Currency&TEXT(%s,"#,##0")' % bk.kpi("budget_planned"),
         m.money(agg["budget_planned"])),
        ("SPENT SO FAR", "accent",
         '=Currency&TEXT(%s,"#,##0")' % bk.kpi("budget_actual"),
         m.money(agg["budget_actual"])),
        ("STILL TO SPEND", "ok",
         '=Currency&TEXT(%s,"#,##0")' % bk.kpi("budget_remaining"),
         m.money(agg["budget_remaining"])),
        ("BUDGET USED", "gold", "=%s" % bk.kpi("budget_pct"),
         agg["budget_pct"]),
    ]
    _cards(bk, ROW_BUD_LBL, ROW_BUD_VAL, budget_cards,
           num_formats=[None, None, None, "0%"])

    # budget progress bar
    ws.set_row(r(ROW_BUD_BAR), 24)
    ws.merge_range(r(ROW_BUD_BAR), 1, r(ROW_BUD_BAR), ci("C"),
                   "  Budget progress", S.bar_label)
    ws.merge_range(r(ROW_BUD_BAR), ci("D"), r(ROW_BUD_BAR), ci("K"), "",
                   S.bar_text)
    ws.write_formula(r(ROW_BUD_BAR), ci("D"),
                     _bar_formula(bk, bk.kpi("budget_actual"),
                                  bk.kpi("budget_planned"), 40), S.bar_text,
                     _bar(agg["budget_pct"], 40))
    ws.merge_range(r(ROW_BUD_BAR), ci("L"), r(ROW_BUD_BAR), ci(LAST_COL), "",
                   S.bar_pct)
    ws.write_formula(r(ROW_BUD_BAR), ci("L"),
                     '=TEXT(%s,"0%%")&" used"' % bk.kpi("budget_pct"),
                     S.bar_pct, "%d%% used" % round(agg["budget_pct"] * 100))
    bk.stats["formulas"] += 2
    ws.set_row(r(10), 8)

    # ------------------------------------------------------------------
    # gift cards
    # ------------------------------------------------------------------
    _section(ws, S, ROW_GIF_SEC, "  \U0001F381  GIFT PROGRESS",
             style=S.section_accent)
    gift_cards_1 = [
        ("\U0001F381 GIFTS PLANNED", "primary", "=%s" % bk.kpi("gifts_planned"),
         agg["gifts_planned"]),
        ("\u2705 PURCHASED", "ok",
         '=%s&" / "&%s' % (bk.kpi("gifts_purchased"), bk.kpi("gifts_planned")),
         "%d / %d" % (agg["gifts_purchased"], agg["gifts_planned"])),
        ("\U0001F380 WRAPPED", "accent", "=%s" % bk.kpi("gifts_wrapped"),
         agg["gifts_wrapped"]),
        ("\U0001F4E6 DELIVERED / GIVEN", "info",
         "=%s" % bk.kpi("gifts_delivered"), agg["gifts_delivered"]),
    ]
    gift_cards_2 = [
        ("\U0001F6D2 STILL TO BUY", "warn", "=%s" % bk.kpi("gifts_to_buy"),
         agg["gifts_to_buy"]),
        ("\U0001F6CD\uFE0F ON ORDER", "plum", "=%s" % bk.kpi("gifts_ordered"),
         agg["gifts_ordered"]),
        ("\U0001F4C8 COMPLETION", "gold", "=%s" % bk.kpi("gift_completion"),
         agg["gift_completion"]),
        ("\U0001F465 AVG SPEND PER PERSON", "primary_2",
         '=Currency&TEXT(%s,"#,##0")' % bk.kpi("avg_per_recipient"),
         m.money(agg["avg_per_recipient"])),
    ]
    _cards(bk, ROW_GIF_LBL1, ROW_GIF_VAL1, gift_cards_1)
    _cards(bk, ROW_GIF_LBL2, ROW_GIF_VAL2, gift_cards_2,
           num_formats=[None, None, "0%", None])

    ws.set_row(r(ROW_GIF_BAR), 24)
    ws.merge_range(r(ROW_GIF_BAR), 1, r(ROW_GIF_BAR), ci("C"),
                   "  Gift progress", S.bar_label)
    ws.merge_range(r(ROW_GIF_BAR), ci("D"), r(ROW_GIF_BAR), ci("K"), "",
                   S.bar_text)
    ws.write_formula(r(ROW_GIF_BAR), ci("D"),
                     _bar_formula(bk, bk.kpi("gifts_purchased"),
                                  bk.kpi("gifts_planned"), 40), S.bar_text,
                     _bar(agg["gift_completion"], 40))
    ws.merge_range(r(ROW_GIF_BAR), ci("L"), r(ROW_GIF_BAR), ci(LAST_COL), "",
                   S.bar_pct)
    ws.write_formula(r(ROW_GIF_BAR), ci("L"),
                     '=%s&" / "&%s&" gifts"'
                     % (bk.kpi("gifts_purchased"), bk.kpi("gifts_planned")),
                     S.bar_pct, "%d / %d gifts" % (agg["gifts_purchased"],
                                                   agg["gifts_planned"]))
    bk.stats["formulas"] += 2
    ws.set_row(r(17), 8)

    # ------------------------------------------------------------------
    # charts
    # ------------------------------------------------------------------
    _section(ws, S, ROW_CHART_SEC, "  \U0001F4CA  WHERE THE MONEY GOES")
    for row in range(ROW_CHART_1, ROW_CHART_2 + 15):
        ws.set_row(r(row), 20)
    _charts(bk)
    ws.set_row(r(48), 8)

    # ------------------------------------------------------------------
    # panels: what's left + deadlines
    # ------------------------------------------------------------------
    ws.set_row(r(ROW_PANEL_SEC), 22)
    ws.merge_range(r(ROW_PANEL_SEC), 1, r(ROW_PANEL_SEC), ci("G"),
                   "  \U0001F3AF  WHAT'S LEFT TO DO", S.section)
    ws.merge_range(r(ROW_PANEL_SEC), ci("H"), r(ROW_PANEL_SEC), ci(LAST_COL),
                   "  \u23F0  UPCOMING DEADLINES", S.section_gold)
    _left_panel(bk)
    _right_panel(bk)
    ws.set_row(r(60), 8)

    # ------------------------------------------------------------------
    # per-recipient table
    # ------------------------------------------------------------------
    _section(ws, S, ROW_REC_SEC,
             "  \U0001F385  PER-RECIPIENT SUMMARY   (automatic)",
             style=S.section_soft)
    _recipients(bk)
    ws.set_row(r(80), 8)

    # ------------------------------------------------------------------
    # navigation + footer
    # ------------------------------------------------------------------
    _section(ws, S, ROW_NAV_SEC, "  \U0001F9ED  JUMP STRAIGHT TO",
             style=S.section_soft)
    ws.set_row(r(ROW_NAV), 26)
    ws.set_row(r(ROW_NAV + 1), 26)
    foot = bk.nav_row(KEY, ROW_NAV, first_col=1, span=2,
                      max_col=LAST_COL) + 2
    ws.set_row(r(foot - 1), 8)
    ws.merge_range(r(foot), 1, r(foot), ci(LAST_COL),
                   "  %s v%s  \u2022  %s  \u2022  Excel 2016+ and Google "
                   "Sheets  \u2022  no macros  \u2022  change the event date "
                   "in \u2699\uFE0F Setup and the whole workbook follows"
                   % (C.PRODUCT, C.VERSION, C.TAGLINE), S.footer)

    bk.page(KEY, LAST_COL, foot + 2, landscape=True, zoom=85)
    return ws


# ===========================================================================
# pieces
# ===========================================================================
def _section(ws, S, row, text, style=None):
    ws.set_row(r(row), 22)
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL), text, style or S.section)


def _cards(bk, label_row, value_row, cards, num_formats=None,
           label_formulas=None):
    ws, S, th = bk.ws(KEY), bk.S, bk.th
    num_formats = num_formats or [None] * len(cards)
    label_formulas = label_formulas or [False] * len(cards)
    ws.set_row(r(label_row), 18)
    ws.set_row(r(value_row), 38)
    for i, (label, color, formula, cached) in enumerate(cards):
        c1, c2 = CARDS[i]
        lbl_fmt = S.kpi_label(getattr(th, color), size=9.5,
                              align="center" if not label_formulas[i] else
                              "center")
        ws.merge_range(r(label_row), ci(c1), r(label_row), ci(c2), "",
                       lbl_fmt)
        if label_formulas[i] or (isinstance(label, str) and
                                 label.startswith("=")):
            ws.write_formula(r(label_row), ci(c1), label, lbl_fmt, "")
            bk.stats["formulas"] += 1
        else:
            ws.write(r(label_row), ci(c1), label, lbl_fmt)
        val_fmt = S.kpi_value(getattr(th, color),
                              num_format=num_formats[i], size=22)
        ws.merge_range(r(value_row), ci(c1), r(value_row), ci(c2), "",
                       val_fmt)
        ws.write_formula(r(value_row), ci(c1), formula, val_fmt, cached)
        bk.stats["formulas"] += 1


def _charts(bk):
    ws, th = bk.ws(KEY), bk.th
    d = bk.q("data")

    # 1 - spending per person (horizontal bar)
    ch = bk.chart("bar")
    ch.add_series({
        "name": "Spent",
        "categories": "=%s!$H$%d:$H$%d" % (d, C.DATA_REC_FIRST,
                                           C.DATA_REC_FIRST +
                                           C.DATA_REC_ROWS - 1),
        "values": "=%s!$J$%d:$J$%d" % (d, C.DATA_REC_FIRST,
                                       C.DATA_REC_FIRST + C.DATA_REC_ROWS - 1),
        "fill": {"color": th.accent},
        "border": {"color": th.accent},
        "gap": 45,
    })
    ch.set_title({"name": "Spending per person",
                  "name_font": {"size": 12, "bold": True, "color": th.primary,
                                "name": th.body_font}})
    ch.set_x_axis({"num_format": "#,##0", "num_font": {"size": 9},
                   "major_gridlines": {"visible": True,
                                       "line": {"color": th.border}}})
    ch.set_y_axis({"num_font": {"size": 9}, "label_position": "low"})
    ch.set_size({"width": 555, "height": 275})
    ch.set_legend({"none": True})
    ws.insert_chart(r(ROW_CHART_1), ci("B"), ch, {"x_offset": 8,
                                                  "y_offset": 6})

    # 2 - planned vs spent by budget category
    b = bk.q("budget")
    first, last = C.BUD_FIRST, C.BUD_FIRST + C.BUDGET_ROWS - 1
    cats = "=%s!$B$%d:$B$%d" % (b, first, last)
    ch = bk.chart("column")
    ch.add_series({"name": "Planned", "categories": cats,
                   "values": "=%s!$C$%d:$C$%d" % (b, first, last),
                   "fill": {"color": th.border_strong},
                   "border": {"color": th.border_strong},
                   "gap": 55})
    ch.add_series({"name": "Spent", "categories": cats,
                   "values": "=%s!$F$%d:$F$%d" % (b, first, last),
                   "fill": {"color": th.primary},
                   "border": {"color": th.primary}})
    ch.set_title({"name": "Budget vs actual, by category",
                  "name_font": {"size": 12, "bold": True, "color": th.primary,
                                "name": th.body_font}})
    ch.set_y_axis({"num_format": "#,##0", "num_font": {"size": 9},
                   "major_gridlines": {"visible": True,
                                       "line": {"color": th.border}}})
    ch.set_x_axis({"num_font": {"size": 8}})
    ch.set_size({"width": 555, "height": 275})
    ch.set_legend({"position": "bottom", "font": {"size": 9}})
    ws.insert_chart(r(ROW_CHART_1), ci("H"), ch, {"x_offset": 8,
                                                  "y_offset": 6})

    # 3 - gift status doughnut
    ch = bk.chart("doughnut")
    ch.add_series({
        "name": "Gifts",
        "categories": "=%s!$T$%d:$T$%d" % (d, C.DATA_STATUS_FIRST,
                                           C.DATA_STATUS_FIRST + 5),
        "values": "=%s!$U$%d:$U$%d" % (d, C.DATA_STATUS_FIRST,
                                       C.DATA_STATUS_FIRST + 5),
        "points": [{"fill": {"color": c}} for c in
                   [th.plum, th.warn, th.info, th.ok, th.gold, th.primary]],
        "data_labels": {"value": True, "font": {"size": 9,
                                                "color": th.white}},
    })
    ch.set_title({"name": "Where the gifts are at",
                  "name_font": {"size": 12, "bold": True, "color": th.primary,
                                "name": th.body_font}})
    ch.set_hole_size(58)
    ch.set_size({"width": 555, "height": 275})
    ch.set_legend({"position": "right", "font": {"size": 9}})
    ws.insert_chart(r(ROW_CHART_2), ci("B"), ch, {"x_offset": 8,
                                                  "y_offset": 6})

    # 4 - bought vs still to buy, per person
    ch = bk.chart("column", subtype="stacked")
    ch.add_series({
        "name": "Bought",
        "categories": "=%s!$H$%d:$H$%d" % (d, C.DATA_REC_FIRST,
                                           C.DATA_REC_FIRST +
                                           C.DATA_REC_ROWS - 1),
        "values": "=%s!$L$%d:$L$%d" % (d, C.DATA_REC_FIRST,
                                       C.DATA_REC_FIRST + C.DATA_REC_ROWS - 1),
        "fill": {"color": th.primary}, "border": {"color": th.primary},
        "gap": 60, "overlap": 100})
    ch.add_series({
        "name": "Still to buy",
        "categories": "=%s!$H$%d:$H$%d" % (d, C.DATA_REC_FIRST,
                                           C.DATA_REC_FIRST +
                                           C.DATA_REC_ROWS - 1),
        "values": "=%s!$O$%d:$O$%d" % (d, C.DATA_REC_FIRST,
                                       C.DATA_REC_FIRST + C.DATA_REC_ROWS - 1),
        "fill": {"color": th.gold}, "border": {"color": th.gold}})
    ch.set_title({"name": "Gifts per person: bought vs still to buy",
                  "name_font": {"size": 12, "bold": True, "color": th.primary,
                                "name": th.body_font}})
    ch.set_y_axis({"num_font": {"size": 9}, "major_unit": 1,
                   "major_gridlines": {"visible": True,
                                       "line": {"color": th.border}}})
    ch.set_x_axis({"num_font": {"size": 8}})
    ch.set_size({"width": 555, "height": 275})
    ch.set_legend({"position": "bottom", "font": {"size": 9}})
    ws.insert_chart(r(ROW_CHART_2), ci("H"), ch, {"x_offset": 8,
                                                  "y_offset": 6})


def _left_panel(bk):
    ws, S, th, m = bk.ws(KEY), bk.S, bk.th, bk.demo
    lines = _todo_lines(bk)
    panel = S.panel(color=th.border, size=10.5, bold=False, valign="vcenter",
                    wrap=False)
    for i, (formula, cached) in enumerate(lines[:10]):
        row = ROW_PANEL + i
        ws.set_row(r(row), 19)
        ws.merge_range(r(row), 1, r(row), ci("G"), "", panel)
        ws.write_formula(r(row), 1, formula, panel, cached)
        bk.stats["formulas"] += 1
    for i in range(len(lines), 10):
        row = ROW_PANEL + i
        ws.set_row(r(row), 19)
        ws.merge_range(r(row), 1, r(row), ci("G"), "", panel)
    # colour the panic lines
    bk.cond(KEY, ROW_PANEL, 1, ROW_PANEL + 9, ci("G"), {
        "type": "formula",
        "criteria": '=ISNUMBER(SEARCH("\U0001F534",$B%d))' % ROW_PANEL,
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond(KEY, ROW_PANEL, 1, ROW_PANEL + 9, ci("G"), {
        "type": "formula",
        "criteria": '=ISNUMBER(SEARCH("\u26A0\uFE0F",$B%d))' % ROW_PANEL,
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    bk.cond(KEY, ROW_PANEL, 1, ROW_PANEL + 9, ci("G"), {
        "type": "formula",
        "criteria": '=ISNUMBER(SEARCH("\u2705",$B%d))' % ROW_PANEL,
        "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})


def _right_panel(bk):
    ws, S, th, m = bk.ws(KEY), bk.S, bk.th, bk.demo
    pool_first = C.DATA_POOL_FIRST
    pool_last = C.DATA_POOL_FIRST + C.pool_size(bk.edition) - 1
    dates = bk.data_rng("AA", pool_first, pool_last)
    labels = bk.data_rng("AB", pool_first, pool_last)

    date_fmt = S.f(**S.base(font_size=10, bold=True, font_color=th.accent,
                            bg_color=th.card, align="center",
                            valign="vcenter", border=1,
                            border_color=th.border,
                            num_format="dd mmm"))
    label_fmt = S.f(**S.base(font_size=10, font_color=th.ink,
                             bg_color=th.card, align="left", valign="vcenter",
                             border=1, border_color=th.border, indent=1))
    days_fmt = S.f(**S.base(font_size=10, bold=True, font_color=th.primary,
                            bg_color=th.card, align="center",
                            valign="vcenter", border=1,
                            border_color=th.border, num_format='0 "days"'))
    pool = m.agg["pool"]
    for i in range(5):
        row = ROW_PANEL + i
        ws.set_row(r(row), 19)
        small = "SMALL(%s,%d)" % (dates, i + 1)
        ws.write_formula(r(row), ci("H"), "=IFERROR(%s,\"\")" % small,
                         date_fmt, pool[i][0] if i < len(pool) else "")
        ws.merge_range(r(row), ci("I"), r(row), ci("K"), "", label_fmt)
        ws.write_formula(
            r(row), ci("I"),
            '=IF($H%d="","\u2014 nothing scheduled \u2014",IFERROR(INDEX(%s,'
            'MATCH(%s,%s,0)),""))' % (row, labels, small, dates),
            label_fmt, pool[i][1] if i < len(pool)
            else "\u2014 nothing scheduled \u2014")
        ws.merge_range(r(row), ci("L"), r(row), ci(LAST_COL), "", days_fmt)
        ws.write_formula(r(row), ci("L"),
                         '=IF($H%d="","",$H%d-TODAY())' % (row, row),
                         days_fmt, (pool[i][0] - _today()).days
                         if i < len(pool) else "")
        bk.stats["formulas"] += 3

    # key dates
    key_hdr = S.f(**S.base(font_size=10, bold=True, font_color=th.ink,
                           bg_color=th.gold_soft, align="left",
                           valign="vcenter", border=1, border_color=th.border,
                           indent=1))
    row = ROW_PANEL + 5
    ws.set_row(r(row), 19)
    ws.merge_range(r(row), ci("H"), r(row), ci(LAST_COL),
                   "  \U0001F5D3\uFE0F  KEY DATES (calculated from your "
                   "event date)", key_hdr)
    key_dates = [
        ("\U0001F4EE Last online order date", 10),
        ("\U0001F48C Cards in the post by", 14),
        ("\U0001F380 Wrapping day", 2),
        ("\U0001F384 The big day", 0),
    ]
    for i, (label, back) in enumerate(key_dates):
        row += 1
        ws.set_row(r(row), 19)
        when = "EventDate" if back == 0 else "EventDate-%d" % back
        from datetime import timedelta
        ws.write_formula(r(row), ci("H"), "=" + when, date_fmt,
                         m.event_date - timedelta(days=back))
        ws.merge_range(r(row), ci("I"), r(row), ci("K"), label, label_fmt)
        ws.merge_range(r(row), ci("L"), r(row), ci(LAST_COL), "", days_fmt)
        ws.write_formula(r(row), ci("L"),
                         '=IF($H%d-TODAY()<0,"\u2713 passed",$H%d-TODAY())'
                         % (row, row), days_fmt,
                         "\u2713 passed"
                         if (m.event_date - timedelta(days=back)) < _today()
                         else ((m.event_date - timedelta(days=back)) -
                               _today()).days)
        bk.stats["formulas"] += 2


def _recipients(bk):
    ws, S, th, m = bk.ws(KEY), bk.S, bk.th, bk.demo
    heads = [("B", "C", "Recipient"), ("D", None, "Budget"),
             ("E", None, "Spent"), ("F", None, "Remaining"),
             ("G", None, "Gifts"), ("H", None, "Bought"),
             ("I", None, "Wrapped"), ("J", None, "Given"),
             ("K", None, "To buy"), ("L", None, "Done %"),
             ("M", None, "Progress")]
    ws.set_row(r(ROW_REC_HDR), 26)
    for c1, c2, label in heads:
        if c2:
            ws.merge_range(r(ROW_REC_HDR), ci(c1), r(ROW_REC_HDR), ci(c2),
                           label, S.header(th.primary))
        else:
            ws.write(r(ROW_REC_HDR), ci(c1), label, S.header(th.primary))

    name_fmt = S.f(**S.base(font_size=10.5, bold=True, font_color=th.ink,
                            bg_color=th.card, align="left", valign="vcenter",
                            border=1, border_color=th.border, indent=1))
    money_fmt = S.f(**S.base(font_size=10.5, font_color=th.ink,
                             bg_color=th.card, align="right",
                             valign="vcenter", border=1,
                             border_color=th.border, num_format="#,##0"))
    num_fmt = S.f(**S.base(font_size=10.5, font_color=th.ink,
                           bg_color=th.card, align="center", valign="vcenter",
                           border=1, border_color=th.border,
                           num_format="0"))
    pct_fmt = S.f(**S.base(font_size=10.5, bold=True, font_color=th.primary,
                           bg_color=th.card, align="center", valign="vcenter",
                           border=1, border_color=th.border, num_format="0%"))
    bar_fmt = S.f(**S.base(font_name=th.mono_font, font_size=10, bold=True,
                           font_color=th.primary_2, bg_color=th.card,
                           align="left", valign="vcenter", border=1,
                           border_color=th.border))
    data_cols = ["D", "E", "F", "G", "H", "I", "J", "K", "L"]
    src = ["I", "J", None, "K", "L", "M", "N", "O", "P"]
    for i in range(C.DATA_REC_ROWS):
        row = ROW_REC_FIRST + i
        drow = C.DATA_REC_FIRST + i
        rec = m.agg["recipients"][i]
        blank = not rec["name"]
        ws.set_row(r(row), 18)
        ws.merge_range(r(row), ci("B"), r(row), ci("C"), "", name_fmt)
        ws.write_formula(r(row), ci("B"), "=%s!$H$%d" % (bk.q("data"), drow),
                         name_fmt, rec["name"])
        for col, sc in zip(data_cols, src):
            guard = '=IF($B%d="","",%%s)' % row
            if sc is None:                       # remaining = budget - spent
                formula = '=IF(OR($B%d="",%s!$H$%d=""),"",$D%d-$E%d)' % (
                    row, bk.q("data"), drow, row, row)
                cached = "" if blank else rec["planned"] - rec["spent"]
                fmt = money_fmt
            elif col == "L":
                formula = guard % ("%s!$%s$%d" % (bk.q("data"), sc, drow))
                cached = "" if blank else rec["pct"]
                fmt = pct_fmt
            elif col in ("D", "E"):
                formula = guard % ("%s!$%s$%d" % (bk.q("data"), sc, drow))
                cached = "" if blank else rec["planned" if col == "D"
                                            else "spent"]
                fmt = money_fmt
            else:
                formula = guard % ("%s!$%s$%d" % (bk.q("data"), sc, drow))
                key = {"G": "gifts", "H": "bought", "I": "wrapped",
                       "J": "delivered", "K": "to_buy"}[col]
                cached = "" if blank else rec[key]
                fmt = num_fmt
            ws.write_formula(r(row), ci(col), formula, fmt,
                             cached if cached != "" else "")
            bk.stats["formulas"] += 1
        ws.write_formula(r(row), ci("M"),
                         '=IF($B%d="","",REPT("\u2588",ROUND(IFERROR($L%d,0)'
                         '*10,0))&REPT("\u2591",10-ROUND(IFERROR($L%d,0)*10,0)))'
                         % ((row,) * 3), bar_fmt,
                         _bar(rec["pct"] or 0, 10) if not blank else "")
        bk.stats["formulas"] += 1

    # totals
    total_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                             bg_color=th.primary, align="center",
                             valign="vcenter", border=1,
                             border_color=th.primary))
    money_total = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                               bg_color=th.primary, align="right",
                               valign="vcenter", border=1,
                               border_color=th.primary, num_format="#,##0"))
    bar_total = S.f(**S.base(font_name=th.mono_font, font_size=10, bold=True,
                             font_color=th.gold_soft, bg_color=th.primary,
                             align="center", valign="vcenter", border=1,
                             border_color=th.primary))
    ws.set_row(r(ROW_REC_TOTAL), 24)
    ws.merge_range(r(ROW_REC_TOTAL), 1, r(ROW_REC_TOTAL), ci("C"),
                   "  EVERYBODY", total_fmt)
    pct_total = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                             bg_color=th.primary, align="center",
                             valign="vcenter", border=1,
                             border_color=th.primary, num_format="0%"))
    for col, fmt in (("D", money_total), ("E", money_total),
                     ("F", money_total), ("G", total_fmt), ("H", total_fmt),
                     ("I", total_fmt), ("J", total_fmt), ("K", total_fmt),
                     ("L", pct_total), ("M", bar_total)):
        ws.write_formula(
            r(ROW_REC_TOTAL), ci(col),
            "=SUM(%s%d:%s%d)" % (col, ROW_REC_FIRST, col,
                                 ROW_REC_FIRST + C.DATA_REC_ROWS - 1)
            if col != "L" else
            '=IFERROR(%s/%s,0)' % (bk.kpi("gifts_purchased"),
                                   bk.kpi("gifts_planned"))
            if col != "M" else
            '=REPT("\u2588",ROUND(IFERROR(%s/%s,0)*10,0))&REPT("\u2591",'
            '10-ROUND(IFERROR(%s/%s,0)*10,0))'
            % ((bk.kpi("gifts_purchased"), bk.kpi("gifts_planned")) * 2),
            fmt,
            (sum(x["planned"] for x in m.agg["recipients"]) if col == "D" else
             sum(x["spent"] for x in m.agg["recipients"]) if col == "E" else
             sum(x["planned"] - x["spent"] for x in m.agg["recipients"])
             if col == "F" else
             m.agg["gifts_planned"] if col == "G" else
             m.agg["gifts_purchased"] if col == "H" else
             m.agg["gifts_wrapped"] if col == "I" else
             m.agg["gifts_delivered"] if col == "J" else
             m.agg["gifts_to_buy"] if col == "K" else
             m.agg["gift_completion"] if col == "L" else
             _bar(m.agg["gift_completion"] or 0, 10)))
        bk.stats["formulas"] += 1

    # hide the unused rows of the table
    bk.cond(KEY, ROW_REC_FIRST, 1, ROW_REC_FIRST + C.DATA_REC_ROWS - 1,
            ci(LAST_COL), {
                "type": "formula",
                "criteria": '=$B%d=""' % ROW_REC_FIRST,
                "format": S.cf(bg=th.card, fg=th.card, border=th.card)})
    bk.cond(KEY, ROW_REC_FIRST, ci("L"),
            ROW_REC_FIRST + C.DATA_REC_ROWS - 1, ci("L"), {
                "type": "data_bar", "bar_color": th.primary_2,
                "bar_solid": True, "min_type": "num", "min_value": 0,
                "max_type": "num", "max_value": 1})


# ===========================================================================
# formula fragments
# ===========================================================================
def _countdown(bk):
    days = bk.kpi("days_to_event")
    return ('IF({d}>1,"\u23F3  "&{d}&" Days Until "&EventName&"  \U0001F381",'
            'IF({d}=1,"\u23F3  Tomorrow is "&EventName&"!  \U0001F381",'
            'IF({d}=0,"\U0001F389  It\'s "&EventName&" today!  \U0001F384",'
            '"\U0001F384  "&EventName&" "&TEXT(EventDate,"yyyy")&" has been '
            'and gone \u2014 set a new date in \u2699\uFE0F Setup")))'
            ).format(d=days)


def _bar_formula(bk, numerator, denominator, blocks):
    pct = "MIN(1,IFERROR((%s)/(%s),0))" % (numerator, denominator)
    filled = "ROUND(%s*%d,0)" % (pct, blocks)
    return ('=IFERROR(REPT("\u2588",%s)&REPT("\u2591",%d-%s),"%s")'
            % (filled, blocks, filled, "\u2591" * blocks))


def _bar(pct, blocks):
    try:
        pct = min(1.0, max(0.0, float(pct)))
    except (TypeError, ValueError):
        pct = 0.0
    filled = int(round(pct * blocks))
    return "\u2588" * filled + "\u2591" * (blocks - filled)


def _today():
    from datetime import date
    return date.today()


def _today_text():
    return _today().strftime("%A %d %B %Y")


def _lit(text):
    """A quoted Excel string literal (with inner quotes escaped)."""
    return '"%s"' % str(text).replace('"', '""')


def _cat(*parts):
    return "&".join(parts)


def _iff(cond, then, other):
    return "IF(%s,%s,%s)" % (cond, then, other)


def _todo_lines(bk):
    """The 'what's left to do' sentences: (formula, cached text) x 10."""
    m = bk.demo
    agg = m.agg
    out = []

    def K(name):
        return bk.kpi(name)

    # 1. gifts still to buy
    tb, od = K("gifts_to_buy"), K("gifts_ordered")
    out.append((
        "=" + _iff(tb + "=0",
                   _lit("\u2705  Every gift is bought \u2014 nice work!"),
                   _cat(_lit("\U0001F6D2  "), tb,
                        _lit(" gift(s) still to buy"),
                        _iff(od + ">0",
                             _cat(_lit(" ("), od, _lit(" already on order)")),
                             _lit("")))),
        ("\u2705  Every gift is bought \u2014 nice work!"
         if agg["gifts_to_buy"] == 0 else
         "\U0001F6D2  %d gift(s) still to buy%s"
         % (agg["gifts_to_buy"],
            " (%d already on order)" % agg["gifts_ordered"]
            if agg["gifts_ordered"] else ""))))

    # 2. wrapping
    w = K("wrap_to_do")
    out.append((
        "=" + _iff(w + "=0", _lit("\u2705  Everything is wrapped"),
                   _cat(_lit("\U0001F380  "), w,
                        _lit(" present(s) still to wrap"))),
        ("\u2705  Everything is wrapped" if agg["wrap_to_do"] == 0
         else "\U0001F380  %d present(s) still to wrap" % agg["wrap_to_do"])))

    # 3. handing over
    d = K("deliver_to_do")
    out.append((
        "=" + _iff(d + "=0", _lit("\u2705  All wrapped gifts handed over"),
                   _cat(_lit("\U0001F4E6  "), d,
                        _lit(" wrapped gift(s) not given yet"))),
        ("\u2705  All wrapped gifts handed over" if agg["deliver_to_do"] == 0
         else "\U0001F4E6  %d wrapped gift(s) not given yet"
         % agg["deliver_to_do"])))

    # 4. budget
    p, rem, pct = K("budget_planned"), K("budget_remaining"), K("budget_pct")
    out.append((
        "=" + _iff(
            p + "=0",
            _lit("\U0001F4DD  Set your category budgets on the "
                 "\U0001F4B0 Budget tab"),
            _iff(rem + "<0",
                 _cat(_lit("\U0001F534  Over budget by "), "Currency",
                      "TEXT(-" + rem + ',"#,##0")'),
                 _iff(pct + ">=AlertAt",
                      _cat(_lit("\u26A0\uFE0F  "), "TEXT(" + pct + ',"0%")',
                           _lit(" of the budget used \u2014 "), "Currency",
                           "TEXT(" + rem + ',"#,##0")',
                           _lit(" left to play with")),
                      _cat(_lit("\U0001F4B0  "), "Currency",
                           "TEXT(" + rem + ',"#,##0")',
                           _lit(" left to spend ("), "TEXT(" + pct + ',"0%")',
                           _lit(" used)"))))),
        _budget_line(m)))

    # 5. shopping list
    t, b = K("shop_total"), K("shop_bought")
    left = agg["shop_total"] - agg["shop_bought"]
    out.append((
        "=" + _iff(t + "=0", _lit("\U0001F6CD\uFE0F  Your shopping list is "
                                 "empty"),
                   _iff(t + "=" + b,
                        _cat(_lit("\u2705  Shopping list complete ("), t,
                             _lit(" items)")),
                        _cat(_lit("\U0001F6CD\uFE0F  "), "(" + t + "-" + b
                             + ")", _lit(" of "), t,
                             _lit(" shopping items still to buy")))),
        ("\U0001F6CD\uFE0F  Your shopping list is empty"
         if agg["shop_total"] == 0 else
         "\u2705  Shopping list complete (%d items)" % agg["shop_total"]
         if left == 0 else
         "\U0001F6CD\uFE0F  %d of %d shopping items still to buy"
         % (left, agg["shop_total"]))))

    # 6. parcels
    if bk.has("orders"):
        t, l, o = K("orders_total"), K("orders_late"), K("orders_outstanding")
        out.append((
            "=" + _iff(t + "=0",
                       _lit("\U0001F4E6  No online orders yet \u2014 log "
                            "them on the \U0001F4E6 Order Tracker"),
                       _iff(l + ">0",
                            _cat(_lit("\U0001F534  "), l,
                                 _lit(" parcel(s) are late \u2014 chase them "
                                      "up")),
                            _cat(_lit("\U0001F69A  "), o,
                                 _lit(" parcel(s) still on the way")))),
            ("\U0001F4E6  No online orders yet" if agg["orders_total"] == 0
             else "\U0001F534  %d parcel(s) are late \u2014 chase them up"
             % agg["orders_late"] if agg["orders_late"]
             else "\U0001F69A  %d parcel(s) still on the way"
             % agg["orders_outstanding"])))

    # 7. cards
    if bk.has("cards"):
        t, s = K("cards_total"), K("cards_sent")
        left = agg["cards_total"] - agg["cards_sent"]
        out.append((
            "=" + _iff(t + "=0",
                       _lit("\U0001F48C  Add your card list to the "
                            "\U0001F48C Card Tracker"),
                       _iff(t + "=" + s,
                            _cat(_lit("\u2705  All "), t,
                                 _lit(" cards are posted")),
                            _cat(_lit("\U0001F48C  "), "(" + t + "-" + s + ")",
                                 _lit(" of "), t,
                                 _lit(" cards still to post")))),
            ("\U0001F48C  Add your card list" if agg["cards_total"] == 0
             else "\u2705  All %d cards are posted" % agg["cards_total"]
             if left == 0 else
             "\U0001F48C  %d of %d cards still to post"
             % (left, agg["cards_total"]))))

    # 8. stockings
    if bk.has("stockings"):
        t, b = K("stock_items"), K("stock_bought")
        left = agg["stock_items"] - agg["stock_bought"]
        out.append((
            "=" + _iff(t + "=0",
                       _lit("\U0001F9E6  Stockings not started \u2014 add "
                            "fillers on the \U0001F9E6 Stockings tab"),
                       _iff(t + "=" + b,
                            _cat(_lit("\u2705  All "), t,
                                 _lit(" stocking fillers bought")),
                            _cat(_lit("\U0001F9E6  "), "(" + t + "-" + b + ")",
                                 _lit(" of "), t,
                                 _lit(" stocking fillers still to buy")))),
            ("\U0001F9E6  Stockings not started" if agg["stock_items"] == 0
             else "\u2705  All %d stocking fillers bought" % agg["stock_items"]
             if left == 0 else
             "\U0001F9E6  %d of %d stocking fillers still to buy"
             % (left, agg["stock_items"]))))

    # 9. checklist
    if bk.has("todo"):
        t, o, dn = K("todo_total"), K("todo_overdue"), K("todo_done")
        out.append((
            "=" + _iff(t + "=0", _lit("\u2705  No tasks on the checklist"),
                       _iff(o + ">0",
                            _cat(_lit("\U0001F534  "), o,
                                 _lit(" overdue task(s) on the \u2705 To-Do "
                                      "list")),
                            _cat(_lit("\u2705  "), dn, _lit(" of "), t,
                                 _lit(" checklist tasks done")))),
            ("\u2705  No tasks on the checklist" if agg["todo_total"] == 0
             else "\U0001F534  %d overdue task(s) on the \u2705 To-Do list"
             % agg["todo_overdue"] if agg["todo_overdue"]
             else "\u2705  %d of %d checklist tasks done"
             % (agg["todo_done"], agg["todo_total"]))))

    # 10. wish list
    if bk.has("wishlist"):
        t, mu = K("wish_total"), K("wish_must")
        out.append((
            "=" + _iff(t + "=0",
                       _lit("\U0001F4A1  Save gift ideas on the \U0001F4A1 "
                            "Wish List all year round"),
                       _cat(_lit("\U0001F4A1  "), t, _lit(" idea(s) saved "
                                                           "\u2014 "), mu,
                            _lit(" of them must-haves"))),
            ("\U0001F4A1  Save gift ideas on the \U0001F4A1 Wish List"
             if agg["wish_total"] == 0 else
             "\U0001F4A1  %d idea(s) saved \u2014 %d of them must-haves"
             % (agg["wish_total"], agg["wish_must"]))))

    tips = [
        "\U0001F4A1  Tip: sort the \U0001F381 Gift Tracker by \u201CStore"
        "\u201D and you shop the whole list in one trip.",
        "\U0001F4A1  Tip: the \U0001F380 Wrapping tab remembers where every "
        "present is hiding.",
        "\U0001F4A1  Tip: change the event date in \u2699\uFE0F Setup and "
        "every deadline re-dates itself.",
        "\U0001F4A1  Tip: use this file for birthdays too \u2014 pick an "
        "occasion in \u2699\uFE0F Setup.",
        "\U0001F4A1  Tip: \U0001F648 Secret Mode hides the hiding spots when "
        "somebody is watching.",
    ]
    for tip in tips:
        if len(out) >= 10:
            break
        out.append(("=" + _lit(tip), tip))
    while len(out) < 10:
        out.append(('=""', ""))
    return out[:10]


def _budget_line(m):
    agg, cur = m.agg, m.settings["currency"]
    if agg["budget_planned"] == 0:
        return ("\U0001F4DD  Set your category budgets on the \U0001F4B0 "
                "Budget tab")
    if agg["budget_remaining"] < 0:
        return "\U0001F534  Over budget by %s" % m.money(-agg["budget_remaining"])
    if agg["budget_pct"] >= m.settings["alert"]:
        return ("\u26A0\uFE0F  %d%% of the budget used \u2014 %s left to play "
                "with" % (round(agg["budget_pct"] * 100),
                          m.money(agg["budget_remaining"])))
    return ("\U0001F4B0  %s left to spend (%d%% used)"
            % (m.money(agg["budget_remaining"]),
               round(agg["budget_pct"] * 100)))
