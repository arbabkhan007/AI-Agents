"""
The Dashboard: the first thing the buyer sees.

Layout (columns B..Q, all pulled from the hidden _Data engine):
  * hero band       - business name + live revenue chip + the Setup note
  * headline cards  - cash in / cash out / net profit / margin
  * business cards  - events, bookings, receivables
  * progress bars   - REPT() text bars that work in Excel and Google Sheets
  * charts          - monthly combo, expense doughnut, pipeline doughnut,
                      revenue-by-type bar  (2x2 grid)
"""

from .. import config as C
from ..book import r


def build(bk):
    ws = bk.ws("dashboard")
    S, th = bk.S, bk.th
    demo = bk.demo
    has = bk.has

    bk.widths("dashboard", {
        "A": 2.2, "B": 13, "C": 13, "D": 13, "E": 3, "F": 13, "G": 13,
        "H": 13, "I": 3, "J": 13, "K": 13, "L": 13, "M": 3, "N": 13,
        "O": 13, "P": 13, "Q": 3})
    for row in range(0, 90):
        ws.set_row(row, 18)

    # ------------------------------------------------------------------
    # hero band (rows 2-3)
    # ------------------------------------------------------------------
    ws.set_row(r(2), 34)
    ws.set_row(r(3), 22)
    ws.merge_range(r(2), 1, r(2), 9, "", S.hero_title)
    ws.write_formula(r(2), 1,
                     '=IF(BusinessName="","Your Catering Business",'
                     'BusinessName)', S.hero_title,
                     demo.settings["business"] or "Your Catering Business")
    bk.stats["formulas"] += 1
    ws.merge_range(r(2), 10, r(2), 15, "", S.hero_count)
    ws.write_formula(r(2), 10,
                     '="Cash in  "&Currency&TEXT(%s,"#,##0")'
                     % bk.kpi("revenue"), S.hero_count,
                     "Cash in  %s" % demo.money(demo.agg.get("revenue", 0))
                     if demo.demo else "Cash in  0")
    bk.stats["formulas"] += 1
    ws.merge_range(r(3), 1, r(3), 15, "", S.hero_meta)
    ws.write_formula(r(3), 1,
                     '=IF(\'%s\'!$C$%d="","%s",\'%s\'!$C$%d)'
                     % (bk.name("setup"), C.SU_MESSAGE, C.TAGLINE,
                        bk.name("setup"), C.SU_MESSAGE),
                     S.hero_meta, demo.settings["message"] or C.TAGLINE)
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # headline cards (rows 5-7): label row + big value row
    # ------------------------------------------------------------------
    ws.set_row(r(5), 20)
    ws.set_row(r(6), 40)
    ws.set_row(r(7), 8)
    _card(bk, 5, 1, 3, "CASH IN", th.ok, bk.kpi("revenue"), "#,##0",
          _money(bk, demo, "revenue"))
    _card(bk, 5, 5, 3, "CASH OUT", th.bad, bk.kpi("expenses"), "#,##0",
          _money(bk, demo, "expenses"))
    _card(bk, 5, 9, 3, "NET PROFIT", th.primary, bk.kpi("profit"), "#,##0",
          _money(bk, demo, "profit"))
    _card(bk, 5, 13, 3, "NET MARGIN", th.accent, bk.kpi("margin"), "0%",
          bk.cached("margin", 0))

    # ------------------------------------------------------------------
    # business cards (rows 8-10)
    # ------------------------------------------------------------------
    ws.set_row(r(8), 20)
    ws.set_row(r(9), 30)
    ws.set_row(r(10), 8)
    _minicard(bk, 8, 1, 3, "EVENTS ON THE BOOKS",
              '=COUNTIF(%s,"<>%s")+COUNTIF(%s,"%s")'
              % (bk.rng("events", "status"), C.ES_CANCEL,
                 bk.rng("events", "status"), C.ES_CANCEL),
              demo.agg.get("events_total", 0) - demo.agg.get(
                  "events_cancelled", 0) if demo.demo else 0, "0")
    _minicard(bk, 8, 5, 3, "CONFIRMED & COMING UP",
              bk.kpi("events_confirmed"), bk.cached("events_confirmed"),
              "0")
    _minicard(bk, 8, 9, 3, "OUTSTANDING",
              bk.kpi("outstanding"), _money(bk, demo, "outstanding"),
              _cur(bk) + "#,##0")
    _minicard(bk, 8, 13, 3, "OVERDUE INVOICES",
              bk.kpi("overdue"), bk.cached("overdue"), "0")

    # ------------------------------------------------------------------
    # second row of mini cards (rows 11-13) - edition aware
    # ------------------------------------------------------------------
    ws.set_row(r(11), 20)
    ws.set_row(r(12), 30)
    ws.set_row(r(13), 8)
    _minicard(bk, 11, 1, 3, "FOOD COST %", bk.kpi("food_pct"),
              bk.cached("food_pct", 0), "0%")
    _minicard(bk, 11, 5, 3, "LABOR %", bk.kpi("labor_pct"),
              bk.cached("labor_pct", 0), "0%")
    _minicard(bk, 11, 9, 3, "AVG ORDER VALUE", bk.kpi("avg_order"),
              _money(bk, demo, "avg_order"), _cur(bk) + "#,##0")
    _minicard(bk, 11, 13, 3, "GUESTS SERVED", bk.kpi("guests_total"),
              bk.cached("guests_total", 0), "#,##0")

    if bk.edition == "premium":
        ws.set_row(r(14), 20)
        ws.set_row(r(15), 30)
        ws.set_row(r(16), 8)
        _minicard(bk, 14, 1, 3, "INVENTORY VALUE", bk.kpi("inv_value"),
                  _money2(bk, demo, "inv_value"), _cur(bk) + "#,##0.00")
        _minicard(bk, 14, 5, 3, "LOW STOCK", bk.kpi("low_stock"),
                  bk.cached("low_stock", 0), "0")
        _minicard(bk, 14, 9, 3, "SHOPPING TO BUY",
                  '=%s&" lines \u00b7 "&%s'
                  % (bk.kpi("shop_lines"),
                     _money_formula(bk, bk.kpi("shop_cost"), "#,##0")),
                  ("%d lines \u00b7 %s" % (demo.agg.get("shop_lines", 0),
                                           demo.money(
                                               demo.agg.get("shop_cost", 0))))
                  if demo.demo else "0 lines", "@")
        _minicard(bk, 14, 13, 3, "UNPAID SHIFTS", bk.kpi("staff_unpaid"),
                  bk.cached("staff_unpaid", 0), "0")

    # ------------------------------------------------------------------
    # progress bars (rows 18-21)
    # ------------------------------------------------------------------
    bar_row = 18 if bk.edition == "premium" else 15
    ws.merge_range(r(bar_row), 1, r(bar_row), 15,
                   "How the season is going", S.section)
    _bar(bk, bar_row + 1, "Collected vs invoiced",
         "%s" % bk.kpi("revenue"),
         "SUM(%s)" % bk.rng("income", "amount"),
         demo.agg.get("revenue", 0),
         sum(i["amount"] for i in demo.income) if demo.demo else 0)
    _bar(bk, bar_row + 2, "Costs vs cash in",
         "SUM(%s)" % bk.rng("expenses", "amount"),
         "%s" % bk.kpi("revenue"),
         demo.agg.get("expenses", 0), demo.agg.get("revenue", 0))

    # ------------------------------------------------------------------
    # charts (2x2 grid)
    # ------------------------------------------------------------------
    top = bar_row + 5
    ws.merge_range(r(top), 1, r(top), 15, "The picture", S.section)
    _combo_chart(bk, top + 1, 1)                 # B, monthly combo
    _doughnut(bk, top + 1, 9, "Where the money goes", "exp", th.accent)
    _doughnut(bk, top + 22, 1, "Pipeline status", "status", th.info)
    _type_bar(bk, top + 22, 9)

    # ------------------------------------------------------------------
    # footer + nav
    # ------------------------------------------------------------------
    foot = top + 44
    ws.merge_range(r(foot), 1, r(foot), 15,
                   "Every number on this page updates itself from the other "
                   "tabs - nothing here is typed by hand.", S.footer)
    bk.nav_row("dashboard", foot + 2, first_col=1, span=3, max_col="P")
    bk.page("dashboard", "Q", foot + 4, landscape=True, freeze=None,
            fit=True, zoom=90)


# ----------------------------------------------------------------------
# card + bar writers
# ----------------------------------------------------------------------
def _card(bk, row, col, span, label, color, formula, numfmt, cached):
    ws, S, th = bk.ws("dashboard"), bk.S, bk.th
    fmt = S.kpi_label(th.primary)
    ws.merge_range(r(row), col, r(row), col + span - 1, label, fmt)
    vfmt = S.kpi_value(color, num_format=numfmt, size=22)
    ws.merge_range(r(row + 1), col, r(row + 1), col + span - 1, "", vfmt)
    ws.write_formula(r(row + 1), col, "=" + formula if not
                     formula.startswith("=") else formula, vfmt, cached)
    bk.stats["formulas"] += 1


def _minicard(bk, row, col, span, label, formula, cached, numfmt):
    ws, S, th = bk.ws("dashboard"), bk.S, bk.th
    fmt = S.kpi_label(th.primary_2, size=9)
    ws.merge_range(r(row), col, r(row), col + span - 1, label, fmt)
    vfmt = S.kpi_value(th.primary_2, num_format=numfmt, size=15)
    ws.merge_range(r(row + 1), col, r(row + 1), col + span - 1, "", vfmt)
    ws.write_formula(r(row + 1), col,
                     formula if formula.startswith("=") else "=" + formula,
                     vfmt, cached)
    bk.stats["formulas"] += 1


def _bar(bk, row, label, num_f, den_f, num_c, den_c):
    """A REPT() progress bar: label | bar | percent."""
    ws, S, th = bk.ws("dashboard"), bk.S, bk.th
    ws.merge_range(r(row), 1, r(row), 3, label, S.bar_label)
    ws.merge_range(r(row), 4, r(row), 11, "", S.bar_text)
    ws.write_formula(r(row), 4, bk.bar(num_f, den_f), S.bar_text,
                     bk.bar_static(num_c, den_c))
    bk.stats["formulas"] += 1
    ws.merge_range(r(row), 12, r(row), 13, "", S.bar_pct)
    ws.write_formula(r(row), 12,
                     "=IFERROR(TEXT(MIN(1,%s/(%s)),\"0%%\"),\"0%%\")"
                     % (num_f, den_f), S.bar_pct,
                     ("%.0f%%" % (100.0 * min(1, num_c / den_c)))
                     if (den_c or 0) > 0 else "0%")
    bk.stats["formulas"] += 1
    ws.merge_range(r(row), 14, r(row), 15, "", S.canvas)


# ----------------------------------------------------------------------
# chart builders
# ----------------------------------------------------------------------
def _combo_chart(bk, row, col):
    ws, th = bk.ws("dashboard"), bk.th
    ch = bk.chart("column")
    ch.add_series({
        "name": "Cash in",
        "categories": "='%s'!$H$%d:$H$%d" % (bk.name("data"),
                                             C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$I$%d:$I$%d" % (bk.name("data"),
                                         C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "fill": {"color": th.ok},
        "border": {"none": True},
    })
    ch.add_series({
        "name": "Cash out",
        "categories": "='%s'!$H$%d:$H$%d" % (bk.name("data"),
                                             C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$J$%d:$J$%d" % (bk.name("data"),
                                         C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "fill": {"color": th.bad},
        "border": {"none": True},
    })
    line = bk.chart("line")
    line.add_series({
        "name": "Net",
        "categories": "='%s'!$H$%d:$H$%d" % (bk.name("data"),
                                             C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$K$%d:$K$%d" % (bk.name("data"),
                                         C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "line": {"color": th.primary, "width": 2.5},
        "marker": {"type": "circle", "size": 5,
                   "fill": {"color": th.primary},
                   "border": {"color": th.primary}},
    })
    ch.combine(line)
    ch.set_title({"name": "Cash in vs cash out, by month",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"position": "bottom"})
    ch.set_x_axis({"num_font": {"size": 9, "color": th.muted}})
    ch.set_y_axis({"num_format": "#,##0",
                   "num_font": {"size": 9, "color": th.muted},
                   "major_gridlines": {"visible": True, "line": {
                       "color": th.border, "width": 0.75}}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_plotarea({"fill": {"color": th.card}})
    ch.set_size({"width": 560, "height": 300})
    ws.insert_chart(r(row), col, ch, {"x_offset": 4, "y_offset": 4})


def _doughnut(bk, row, col, title, which, color):
    ws, th = bk.ws("dashboard"), bk.th
    if which == "exp":
        cats = ("='%s'!$N$%d:$N$%d" % (bk.name("data"), C.DATA_EXP_FIRST,
                                        C.DATA_EXP_FIRST + 10))
        vals = ("='%s'!$O$%d:$O$%d" % (bk.name("data"), C.DATA_EXP_FIRST,
                                        C.DATA_EXP_FIRST + 10))
        points = [{"fill": {"color": c}, "border": {"color": th.card}}
                  for c in _palette_exp(th)]
    else:
        cats = ("='%s'!$N$%d:$N$%d" % (bk.name("data"),
                                        C.DATA_STATUS_FIRST,
                                        C.DATA_STATUS_FIRST + 5))
        vals = ("='%s'!$O$%d:$O$%d" % (bk.name("data"),
                                        C.DATA_STATUS_FIRST,
                                        C.DATA_STATUS_FIRST + 5))
        points = [{"fill": {"color": c}, "border": {"color": th.card}}
                  for c in _palette_status(th)]
    ch = bk.chart("doughnut")
    ch.add_series({
        "name": title,
        "categories": cats,
        "values": vals,
        "points": points,
        "data_labels": {"percentage": True, "font": {"size": 8,
                                                     "color": th.white}},
    })
    ch.set_title({"name": title,
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_hole_size(52)
    ch.set_legend({"position": "right", "font": {"size": 8}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 460, "height": 300})
    ws.insert_chart(r(row), col, ch, {"x_offset": 4, "y_offset": 4})


def _type_bar(bk, row, col):
    ws, th = bk.ws("dashboard"), bk.th
    ch = bk.chart("bar")
    ch.add_series({
        "name": "Revenue",
        "categories": "='%s'!$N$%d:$N$%d" % (bk.name("data"),
                                              C.DATA_TYPE_FIRST,
                                              C.DATA_TYPE_FIRST + 8),
        "values": "='%s'!$O$%d:$O$%d" % (bk.name("data"),
                                         C.DATA_TYPE_FIRST,
                                         C.DATA_TYPE_FIRST + 8),
        "fill": {"color": th.accent},
        "border": {"none": True},
    })
    ch.set_title({"name": "Revenue by event type",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"none": True})
    ch.set_x_axis({"num_format": "#,##0",
                   "num_font": {"size": 9, "color": th.muted}})
    ch.set_y_axis({"reverse": True,
                   "num_font": {"size": 9, "color": th.muted}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 460, "height": 300})
    ws.insert_chart(r(row), col, ch, {"x_offset": 4, "y_offset": 4})


def _palette_exp(th):
    return [th.primary, th.accent, th.gold, th.info, th.plum, th.warn,
            th.ok, th.primary_2, th.bad, "#999999", "#BBBBBB"]


def _palette_status(th):
    return [th.info, th.plum, th.warn, th.ok, th.gold, th.bad]


# ----------------------------------------------------------------------
# cached-value helpers
# ----------------------------------------------------------------------
def _cur(bk):
    return bk.demo.settings["currency"]


def _money(bk, demo, key):
    if not demo.demo:
        return 0
    return demo.agg.get(key, 0)


def _money2(bk, demo, key):
    if not demo.demo:
        return 0
    return demo.agg.get(key, 0)


def _money_formula(bk, ref, fmt):
    return 'Currency&TEXT(%s,"%s")' % (ref, fmt)
