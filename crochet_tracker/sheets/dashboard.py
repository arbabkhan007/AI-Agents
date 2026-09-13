"""
Dashboard - the landing tab.

Hero banner with the studio name, two rows of live KPI cards, six charts
pulled from the hidden _Data engine, a top-products leaderboard and (in
the premium edition) a restock radar. Every number on this tab is a
formula - nothing here is ever typed.
"""

import os

from .. import config as C
from ..book import r, ci
from . import common
from . import data as D

LAST_COL = "M"


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("dashboard")
    demo = bk.demo
    premium = bk.edition == "premium"
    cur = demo.settings["currency"] if demo else "$"

    # ------------------------------------------------------- painting
    try:
        depth = 110
    except KeyError:
        depth = 110
    bk.paint("dashboard", 0, 0, depth, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------------ hero
    ws.set_row(r(1), 7)
    ws.set_row(r(2), 36)
    ws.set_row(r(3), 22)
    ws.set_row(r(4), 8)
    ws.set_row(r(5), 22)
    ws.set_row(r(6), 8)
    ws.merge_range(r(2), 1, r(2), 6, "", S.hero_title)
    ws.write_formula(r(2), 1,
                     '=IF(BusinessName="","My Crochet Studio",'
                     'BusinessName)', S.hero_title,
                     demo.settings["business"] if demo
                     else "My Crochet Studio")
    bk.stats["formulas"] += 1
    ws.merge_range(r(2), 7, r(2), ci(LAST_COL), "", S.hero_meta)
    ws.write_formula(r(2), 7,
                     '=IF(Message="","Plan it, make it, sell it.",Message)',
                     S.hero_meta,
                     demo.settings["message"] if demo
                     else "Plan it, make it, sell it.")
    bk.stats["formulas"] += 1
    ws.merge_range(r(3), 1, r(3), 6,
                   "  \U0001F9F6  Your craft fair business at a glance",
                   S.sheet_sub)
    badge_fmt = S.pill(th.primary_soft, th.primary, size=10.5, bold=True)
    ws.merge_range(r(3), 7, r(3), ci(LAST_COL), "", badge_fmt)
    ws.write(r(3), 7,
             ("PREMIUM EDITION  \u2022  14 tabs" if premium
              else "BASIC EDITION  \u2022  8 tabs"), badge_fmt)

    # ------------------------------------------------------- top chips
    healthy = (not demo) or (demo.agg["low_products"]
                             + demo.agg["low_materials"] == 0)
    common.chips(bk, "dashboard", [
        ('="Sales logged: "&TEXT(%s,"0")' % bk.kpi("txns"), "ok",
         "Sales logged: %d" % (demo.agg["txns"] if demo else 0), 3),
        ('="Units sold: "&TEXT(%s,"#,##0")' % bk.kpi("units"), "gold",
         "Units sold: %d" % (demo.agg["units"] if demo else 0), 3),
        ('="Fairs booked: "&TEXT(%s,"0")' % bk.kpi("events_total"),
         "primary", "Fairs booked: %d" % (demo.agg["events_total"]
                                          if demo else 0), 3),
        ('=IF(%s+%s>0,"! Restock needed - see Reorder List",'
         '"Stock levels look healthy")'
         % (bk.kpi("low_products"), bk.kpi("low_materials")), "warn",
         "Restock needed - see Reorder List" if not healthy
         else "Stock levels look healthy", 3),
    ], last_col=LAST_COL)

    # ------------------------------------------------------ KPI cards
    def card(row, col, span, color_key, label, formula, cached, size=17):
        color = getattr(th, color_key)
        ws.set_row(r(row), 16)
        lab = S.kpi_label(color)
        ws.merge_range(r(row), col, r(row), col + span - 1, "", lab)
        ws.write(r(row), col, label, lab)
        val = S.kpi_text(color, size=size, align="center", bg=th.card,
                         bold=True)
        ws.merge_range(r(row + 1), col, r(row + 2), col + span - 1, "",
                       val)
        ws.write_formula(r(row + 1), col, formula, val, cached)
        bk.stats["formulas"] += 1

    def money(k):
        return '=Currency&TEXT(%s,"#,##0.00")' % bk.kpi(k)

    def moneyc(k):
        return "%s%s" % (cur, format(demo.agg[k], ",.2f") if demo
                         else "0.00")

    row = 7
    cards1 = [
        ("GROSS SALES", money("revenue"), moneyc("revenue"), "primary", 17),
        ("NET PROFIT", money("profit"), moneyc("profit"), "ok", 17),
        ("PROFIT MARGIN", '=TEXT(%s,"0.0%%")' % bk.kpi("margin"),
         format(demo.agg["margin"], ".1%") if demo else "0.0%", "accent",
         17),
        ("UNITS SOLD", '=TEXT(%s,"#,##0")' % bk.kpi("units"),
         format(demo.agg["units"], ",d") if demo else "0", "info", 17),
        ("AVERAGE SALE", money("aov"), moneyc("aov"), "gold", 17),
        ("STOCK VALUE", money("inv_value"), moneyc("inv_value"), "plum",
         17),
    ]
    for i, (label, formula, cached, color, size) in enumerate(cards1):
        card(row, 1 + i * 2, 2, color, label, formula, cached, size)
    ws.set_row(r(row + 1), 26)
    ws.set_row(r(row + 2), 26)

    row = 11
    if premium:
        cards2 = [
            ("FAIRS WORKED",
             '=TEXT(%s,"0")&" of "&TEXT(%s,"0")'
             % (bk.kpi("events_done"), bk.kpi("events_total")),
             "%d of %d" % (demo.agg["events_done"],
                           demo.agg["events_total"]) if demo else "0 of 0",
             "primary_2", 15),
            ("BEST CRAFT FAIR", '=%s' % bk.kpi("best_event"),
             demo.agg["best_event"] if demo else "", "gold", 13),
            ("TOP SELLER", '=%s' % bk.kpi("bs_units"),
             demo.agg["bs_units"] if demo else "", "accent", 13),
            ("TOP EARNER", '=%s' % bk.kpi("bs_revenue"),
             demo.agg["bs_revenue"] if demo else "", "ok", 13),
            ("ITEMS MADE", '=TEXT(%s,"#,##0")' % bk.kpi("made_total"),
             format(demo.agg["made_total"], ",d") if demo else "0",
             "info", 15),
            ("REORDER BILL", money("reorder_cost"), moneyc("reorder_cost"),
             "bad", 15),
        ]
    else:
        cards2 = [
            ("FAIRS WORKED",
             '=TEXT(%s,"0")&" of "&TEXT(%s,"0")'
             % (bk.kpi("events_done"), bk.kpi("events_total")),
             "%d of %d" % (demo.agg["events_done"],
                           demo.agg["events_total"]) if demo else "0 of 0",
             "primary_2", 15),
            ("BEST CRAFT FAIR", '=%s' % bk.kpi("best_event"),
             demo.agg["best_event"] if demo else "", "gold", 13),
            ("TOP SELLER", '=%s' % bk.kpi("bs_units"),
             demo.agg["bs_units"] if demo else "", "accent", 13),
            ("TOP EARNER", '=%s' % bk.kpi("bs_revenue"),
             demo.agg["bs_revenue"] if demo else "", "ok", 13),
            ("PRODUCTS IN CATALOG",
             '=TEXT(COUNTA(%s),"0")' % bk.rng("catalog", "name"),
             format(len(demo.products), ",d") if demo else "0", "info",
             15),
            ("SUGGESTED PRICE", money("price_suggest"),
             moneyc("price_suggest"), "plum", 15),
        ]
    for i, (label, formula, cached, color, size) in enumerate(cards2):
        card(row, 1 + i * 2, 2, color, label, formula, cached, size)
    ws.set_row(r(row + 1), 26)
    ws.set_row(r(row + 2), 26)

    # --------------------------------------------------------- charts
    row = 15
    ws.set_row(r(row), 22)
    bk.band("dashboard", row, 1, ci(LAST_COL), S.section, height=22)
    ws.write(r(row), 1, "  Your year at a glance", S.section)

    qd = bk.q("data")

    def zone(start):
        for rr in range(start, start + 16):
            ws.set_row(r(rr), 20)

    def col_chart(title, cats, vals, color, y_name=None):
        ch = bk.chart("column")
        ch.add_series({
            "name": title,
            "categories": "=%s!%s" % (qd, cats),
            "values": "=%s!%s" % (qd, vals),
            "fill": {"color": color},
            "border": {"none": True},
            "gap": 40,
        })
        _style(ch, title, th)
        ch.set_y_axis({"num_format": "#,##0", "major_gridlines": {
            "visible": True, "line": {"color": th.border}}})
        return ch

    def pie_chart(title, cats, vals, colors):
        ch = bk.chart("pie")
        ch.add_series({
            "name": title,
            "categories": "=%s!%s" % (qd, cats),
            "values": "=%s!%s" % (qd, vals),
            "points": [{"fill": {"color": c}} for c in colors],
            "data_labels": {"percentage": True, "font": {
                "name": th.body_font, "size": 9, "color": th.white,
                "bold": True}},
        })
        _style(ch, title, th)
        ch.set_legend({"position": "right", "font": {
            "name": th.body_font, "size": 9, "color": th.ink}})
        return ch

    def bar_chart(title, cats, vals, color):
        ch = bk.chart("bar")
        ch.add_series({
            "name": title,
            "categories": "=%s!%s" % (qd, cats),
            "values": "=%s!%s" % (qd, vals),
            "fill": {"color": color},
            "border": {"none": True},
            "gap": 30,
        })
        _style(ch, title, th)
        ch.set_x_axis({"num_format": "#,##0"})
        return ch

    def line_chart(title, cats, vals, color):
        ch = bk.chart("line")
        ch.add_series({
            "name": title,
            "categories": "=%s!%s" % (qd, cats),
            "values": "=%s!%s" % (qd, vals),
            "line": {"color": color, "width": 2.5},
            "marker": {"type": "circle", "size": 6,
                       "fill": {"color": color},
                       "border": {"color": th.white}},
        })
        _style(ch, title, th)
        ch.set_y_axis({"num_format": "#,##0"})
        return ch

    pie_colors = [th.primary, th.accent, th.gold, th.info, th.plum,
                  th.primary_2]
    zone(16)
    ws.insert_chart(r(16), 1, col_chart(
        "Sales by month", "$%s$%d:$%s$%d" % (D.M_NAME, 2, D.M_NAME, 13),
        "$%s$%d:$%s$%d" % (D.M_REV, 2, D.M_REV, 13), th.primary),
        {"x_offset": 2, "y_offset": 2})
    ws.insert_chart(r(16), 7, pie_chart(
        "How customers paid", "$P$2:$P$7", "$Q$2:$Q$7", pie_colors),
        {"x_offset": 2, "y_offset": 2})

    zone(33)
    ws.insert_chart(r(33), 1, bar_chart(
        "Top products by revenue",
        "$%s$%d:$%s$%d" % (D.P_NAME, 2, D.P_NAME, 13),
        "$%s$%d:$%s$%d" % (D.P_REV, 2, D.P_REV, 13), th.accent),
        {"x_offset": 2, "y_offset": 2})
    ws.insert_chart(r(33), 7, pie_chart(
        "Where the fair money went", "$S$2:$S$6", "$T$2:$T$6",
        [th.gold, th.info, th.plum, th.ok, th.warn]),
        {"x_offset": 2, "y_offset": 2})

    zone(50)
    ws.insert_chart(r(50), 1, col_chart(
        "Net profit by fair",
        "$%s$%d:$%s$%d" % (D.E_NAME, 2, D.E_NAME, 9),
        "$%s$%d:$%s$%d" % (D.E_NET, 2, D.E_NET, 9), th.ok),
        {"x_offset": 2, "y_offset": 2})
    ws.insert_chart(r(50), 7, line_chart(
        "Monthly net profit", "$%s$%d:$%s$%d" % (D.M_NAME, 2, D.M_NAME, 13),
        "$%s$%d:$%s$%d" % (D.M_NET, 2, D.M_NET, 13), th.accent),
        {"x_offset": 2, "y_offset": 2})

    # ------------------------------------------------- top products
    row = 67
    ws.set_row(r(row), 22)
    bk.band("dashboard", row, 1, ci(LAST_COL), S.section_soft, height=22)
    ws.write(r(row), 1, "  Top products (by revenue)", S.section_soft)
    hdr = row + 1
    ws.set_row(r(hdr), 22)
    ws.write(r(hdr), ci("B"), "#", S.header(th.muted))
    ws.merge_range(r(hdr), ci("C"), r(hdr), ci("G"), "Product",
                   S.header(th.primary))
    ws.write(r(hdr), ci("H"), "Units", S.header(th.primary))
    ws.write(r(hdr), ci("I"), "Revenue", S.header(th.primary))
    ws.write(r(hdr), ci("J"), "Profit", S.header(th.primary))
    ws.merge_range(r(hdr), ci("K"), r(hdr), ci(LAST_COL), "Margin",
                   S.header(th.primary))

    pool_name = "$%s$%d:$%s$%d" % (D.P_NAME, 2, D.P_NAME, 25)
    pool_units = "$%s$%d:$%s$%d" % (D.P_UNITS, 2, D.P_UNITS, 25)
    pool_rev = "$%s$%d:$%s$%d" % (D.P_REV, 2, D.P_REV, 25)
    pool_profit = "$%s$%d:$%s$%d" % (D.P_PROFIT, 2, D.P_PROFIT, 25)
    pool_margin = "$%s$%d:$%s$%d" % (D.P_MARGIN, 2, D.P_MARGIN, 25)
    top = _top_products(bk)
    for i in range(5):
        rr = hdr + 1 + i
        ws.set_row(r(rr), 20)
        a = common.alt(rr)
        ws.write_number(r(rr), ci("B"), i + 1, S.idx(a))
        name_fmt = S.cell("calc")
        ws.merge_range(r(rr), ci("C"), r(rr), ci("G"), "", name_fmt)
        ws.write_formula(
            r(rr), ci("C"),
            '=IFERROR(INDEX(%s,MATCH(LARGE(%s,%d),%s,0)),"")'
            % (pool_name, pool_rev, i + 1, pool_rev), name_fmt,
            top[i][0] if top else "")
        bk.stats["formulas"] += 1
        ws.write_formula(
            r(rr), ci("H"),
            '=IFERROR(INDEX(%s,MATCH($C%d,%s,0)),"")'
            % (pool_units, rr, pool_name), S.cell("calc_qty"),
            top[i][1] if top else 0)
        bk.stats["formulas"] += 1
        ws.write_formula(
            r(rr), ci("I"), '=IFERROR(LARGE(%s,%d),0)' % (pool_rev, i + 1),
            S.cell("calc_money"), top[i][2] if top else 0)
        bk.stats["formulas"] += 1
        ws.write_formula(
            r(rr), ci("J"),
            '=IFERROR(INDEX(%s,MATCH($C%d,%s,0)),"")'
            % (pool_profit, rr, pool_name), S.cell("calc_money"),
            top[i][3] if top else 0)
        bk.stats["formulas"] += 1
        mrg_fmt = S.cell("calc_pct1")
        ws.merge_range(r(rr), ci("K"), r(rr), ci(LAST_COL), "", mrg_fmt)
        ws.write_formula(
            r(rr), ci("K"),
            '=IFERROR(INDEX(%s,MATCH($C%d,%s,0)),"")'
            % (pool_margin, rr, pool_name), mrg_fmt,
            top[i][4] if top else "")
        bk.stats["formulas"] += 1

    # -------------------------------------------------- restock radar
    row = hdr + 7
    if premium:
        ws.set_row(r(row), 22)
        bk.band("dashboard", row, 1, ci(LAST_COL), S.section_accent,
                height=22)
        ws.write(r(row), 1, "  Restock radar", S.section_accent)
        common.chips(bk, "dashboard", [
            ('="Products below minimum: "&TEXT(%s,"0")'
             % bk.kpi("low_products"), "warn",
             "Products below minimum: %d"
             % (demo.agg["low_products"] if demo else 0), 4),
            ('="Materials running low: "&TEXT(%s,"0")'
             % bk.kpi("low_materials"), "warn",
             "Materials running low: %d"
             % (demo.agg["low_materials"] if demo else 0), 4),
            ('="Estimated shopping list: "&Currency&TEXT(%s,"#,##0.00")'
             % bk.kpi("reorder_cost"), "bad",
             "Estimated shopping list: %s" % moneyc("reorder_cost"), 4),
        ], last_col=LAST_COL, row=row + 2)
        ws.set_row(r(row + 2), 22)
        note = ("The Reorder List tab turns these into a ready-to-buy "
                "shopping list with suppliers and costs - tick items off "
                "as you order.")
        ws.merge_range(r(row + 4), 1, r(row + 4), ci(LAST_COL), note,
                       S.note)
        ws.set_row(r(row + 4), 26)
        footer_row = row + 6
    else:
        footer_row = row + 1

    common.footer_nav(
        bk, "dashboard", footer_row, LAST_COL, landscape=True, zoom=90,
        tip="  \U0001F4A1  Every number on this page is live - log a sale "
            "on the Sales Log tab and watch it land here instantly.")


def _style(ch, title, th):
    ch.set_title({"name": title, "name_font": {
        "name": th.title_font, "size": 12, "bold": True,
        "color": th.primary}})
    ch.set_chartarea({"border": {"none": True}})
    ch.set_plotarea({"border": {"none": True}})
    ch.set_legend({"none": True})
    ch.set_size({"width": 452, "height": 296})


def _top_products(bk):
    if not bk.demo:
        return []
    rows = []
    for name, units, revenue, stock, margin, slow in \
            bk.demo.agg["product_stats"]:
        profit = round(sum(s["qty"] * _p(bk, name)["profit"]
                           for s in bk.demo.sales if s["product"] == name),
                       2)
        rows.append((name, units, revenue, profit,
                     margin if units else ""))
    rows.sort(key=lambda t: -t[2])
    return rows[:5]


def _p(bk, name):
    for p in bk.demo.products:
        if p["name"] == name:
            return p
    return {"profit": 0}
