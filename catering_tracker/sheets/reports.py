"""
P&L & Reports: the year on one page.

The profit & loss block is accrual-based (what you booked vs what you
spent, filtered to your Setup report year); the monthly table and charts
are cash-based (what actually landed in the bank).  Both views matter -
the first tells you if you're pricing right, the second if you can pay
the crew on Friday.
"""

from .. import config as C
from ..book import r

LAST_COL = "P"
Y0 = "DATE(ReportYear,1,1)"
Y1 = "DATE(ReportYear,12,31)"

PL_ROWS = {
    "revenue": 9, "cogs": 10, "gross": 11, "opex": 12, "net": 13,
    "gross_pct": 14, "net_pct": 15,
}


def build(bk):
    ws = bk.ws("reports")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("reports", {"A": 2.2, "B": 4, "C": 26, "D": 15, "E": 3,
                          "F": 4, "G": 13, "H": 13, "I": 13, "J": 3,
                          "K": 13, "L": 13, "M": 13, "N": 13, "O": 13,
                          "P": 3})
    for row in range(0, 84):
        ws.set_row(row, 18)

    bk.title_block("reports", "P&L & Reports",
                   "The year in numbers - profit, cash and where it all "
                   "went", LAST_COL)

    ev = bk.q("events")
    ex = bk.q("expenses")
    E_DATE = bk.rng("events", "date")
    E_PRICE = bk.rng("events", "price")
    E_STATUS = bk.rng("events", "status")
    X_DATE = bk.rng("expenses", "date")
    X_CAT = bk.rng("expenses", "category")
    X_AMT = bk.rng("expenses", "amount")

    rev_f = ('=SUMIFS(%s,%s,">="&%s,%s,"<="&%s,%s,"<>%s")'
             % (E_PRICE, E_DATE, Y0, E_DATE, Y1, E_STATUS, C.ES_CANCEL))
    cogs_f = ('=SUMIFS(%s,%s,">="&%s,%s,"<="&%s,%s,"Ingredients")'
              '+SUMIFS(%s,%s,">="&%s,%s,"<="&%s,%s,"Packaging")'
              % (X_AMT, X_DATE, Y0, X_DATE, Y1, X_CAT,
                 X_AMT, X_DATE, Y0, X_DATE, Y1, X_CAT))
    cached = _pl_cache(bk)

    bk.stats_strip("reports", [
        ('="Report year: "&ReportYear', "accent",
         "Report year: %s" % demo.settings["year"]),
        ('="Events completed: "&%s' % bk.kpi("events_done"), "ok",
         "Events completed: %d" % bk.cached("events_done", 0)),
        ('="Cash profit: "&Currency&TEXT(%s,"#,##0")' % bk.kpi("profit"),
         "gold", "Cash profit: %s" % demo.money(bk.cached("profit", 0))),
        ('="Best client: "&%s' % bk.kpi("best_client"), "plum",
         "Best client: %s" % (bk.cached("best_client", "-") or "-")),
    ])

    # ------------------------------------------------------------------
    # the P&L block (column D - rows fixed, the formulas depend on them)
    # ------------------------------------------------------------------
    ws.merge_range(r(8), 1, r(8), 7, "Profit & loss - booked basis",
                   S.section)
    rows = [
        (PL_ROWS["revenue"], "Event revenue (booked, not cancelled)",
         rev_f, cached["revenue"], "money"),
        (PL_ROWS["cogs"], "Cost of goods - food & packaging",
         cogs_f, cached["cogs"], "money"),
        (PL_ROWS["gross"], "GROSS PROFIT",
         '=IF($D$%d="","",ROUND($D$%d-$D$%d,2))'
         % (PL_ROWS["revenue"], PL_ROWS["revenue"], PL_ROWS["cogs"]),
         cached["gross"], "money"),
        (PL_ROWS["opex"], "Operating expenses (everything else)",
         '=IF($D$%d="","",ROUND(SUMIFS(%s,%s,">="&%s,%s,"<="&%s)'
         '-$D$%d,2))'
         % (PL_ROWS["revenue"], X_AMT, X_DATE, Y0, X_DATE, Y1,
            PL_ROWS["cogs"]),
         cached["opex"], "money"),
        (PL_ROWS["net"], "NET PROFIT",
         '=IF($D$%d="","",$D$%d-$D$%d)'
         % (PL_ROWS["opex"], PL_ROWS["gross"], PL_ROWS["opex"]),
         cached["net"], "money"),
        (PL_ROWS["gross_pct"], "Gross margin",
         '=IFERROR($D$%d/$D$%d,"")'
         % (PL_ROWS["gross"], PL_ROWS["revenue"]),
         cached["gross_pct"], "pct"),
        (PL_ROWS["net_pct"], "Net margin",
         '=IFERROR($D$%d/$D$%d,"")' % (PL_ROWS["net"],
                                       PL_ROWS["revenue"]),
         cached["net_pct"], "pct"),
    ]
    for row, label, formula, value, kind in rows:
        big = label in ("GROSS PROFIT", "NET PROFIT")
        lfmt = S.f(**S.base(
            font_size=12 if big else 10.5, bold=True,
            font_color=th.white if big else th.ink,
            bg_color=th.primary if big else th.card, align="left",
            valign="vcenter", indent=1, border=1,
            border_color=th.primary if big else th.border))
        ws.merge_range(r(row), 1, r(row), 2, label, lfmt)
        vfmt = S.kpi_value(th.primary, num_format="#,##0.00" if kind ==
                           "money" else "0%", size=14 if big else 12,
                           align="right")
        ws.write_formula(r(row), 3, formula, vfmt, value)
        bk.stats["formulas"] += 1
    ws.merge_range(r(16), 1, r(16), 6,
                   "Accrual view: bookings and spend inside the report "
                   "year, regardless of when cash moved.", S.note_plain)

    # ------------------------------------------------------------------
    # year cards (right side)
    # ------------------------------------------------------------------
    ws.merge_range(r(8), 9, r(8), 14, "The year in numbers", S.section)
    cards = [
        (10, 9, "EVENTS COMPLETED", bk.kpi("events_done"), "0",
         bk.cached("events_done", 0)),
        (10, 12, "GUESTS SERVED", bk.kpi("guests_total"), "#,##0",
         bk.cached("guests_total", 0)),
        (13, 9, "AVG ORDER VALUE", bk.kpi("avg_order"), "#,##0",
         bk.cached("avg_order", 0)),
        (13, 12, "AVG PROFIT / EVENT", bk.kpi("avg_profit"), "#,##0",
         bk.cached("avg_profit", 0)),
    ]
    for row, col, label, formula, nf, val in cards:
        fmt = S.kpi_label(th.primary_2, size=9)
        ws.merge_range(r(row), col, r(row), col + 2, label, fmt)
        vfmt = S.kpi_value(th.primary_2, num_format=nf, size=16)
        ws.merge_range(r(row + 1), col, r(row + 1), col + 2, "", vfmt)
        ws.write_formula(r(row + 1), col, formula, vfmt, val)
        bk.stats["formulas"] += 1
    for row, col, label, key in ((16, 9, "BEST EARNING EVENT TYPE",
                                  "best_type"),
                                 (16, 12, "HIGHEST VALUE CLIENT",
                                  "best_client")):
        fmt = S.kpi_label(th.plum, size=9)
        ws.merge_range(r(row), col, r(row), col + 2, label, fmt)
        vfmt = S.kpi_text(th.plum, size=12, bg=th.card)
        ws.merge_range(r(row + 1), col, r(row + 1), col + 2, "", vfmt)
        ws.write_formula(r(row + 1), col, "=%s" % bk.kpi(key), vfmt,
                         bk.cached(key, "-"))
        bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # cash by month (reads the _Data pool)
    # ------------------------------------------------------------------
    ws.merge_range(r(19), 1, r(19), 7, "Cash by month - what actually "
                   "landed", S.section)
    heads = ["Month", "Cash in", "Cash out", "Net", "Events"]
    for i, h in enumerate(heads):
        ws.write(r(20), 1 + i, h, S.thead)
    da = bk.name("data")
    months = demo.agg.get("months", []) if demo.demo else []
    for i in range(12):
        row = 21 + i
        m = months[i] if i < len(months) else None
        src = C.DATA_MONTH_FIRST + i
        ws.write(r(row), 1, "='%s'!$H$%d" % (da, src), S.cell("center"),
                 m[0] if m else "")
        ws.write_formula(r(row), 2, "='%s'!$I$%d" % (da, src),
                         S.cell("money0"), m[1] if m else 0)
        ws.write_formula(r(row), 3, "='%s'!$J$%d" % (da, src),
                         S.cell("money0", ), m[2] if m else 0)
        ws.write_formula(r(row), 4, "='%s'!$K$%d" % (da, src),
                         S.cell("money0"), m[3] if m else 0)
        ws.write_formula(r(row), 5, "='%s'!$L$%d" % (da, src),
                         S.cell("qty"), m[4] if m else 0)
        bk.stats["formulas"] += 5
    ws.merge_range(r(33), 1, r(33), 2, "YEAR", S.f(**S.base(
        font_size=11, bold=True, font_color=th.white, bg_color=th.primary,
        align="right", valign="vcenter", border=1, border_color=th.primary,
        indent=1)))
    total_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                             bg_color=th.primary, align="right",
                             valign="vcenter", border=1,
                             border_color=th.primary, num_format="#,##0"))
    for col, key in ((2, 1), (3, 2), (4, 3)):
        ws.write_formula(r(33), col, "=SUM(%s21:%s32)" % ("CDE"[col - 2],
                                                          "CDE"[col - 2]),
                         total_fmt, sum(m[key] for m in months))
        bk.stats["formulas"] += 1
    ws.write_formula(r(33), 5, "=SUM(F21:F32)",
                     S.f(**S.base(font_size=11, bold=True,
                                  font_color=th.white, bg_color=th.primary,
                                  align="center", valign="vcenter", border=1,
                                  border_color=th.primary, num_format="0")),
                     sum(m[4] for m in months))
    bk.stats["formulas"] += 1

    # ------------------------------------------------------------------
    # charts
    # ------------------------------------------------------------------
    _combo_chart(bk, 36)
    _clients_chart(bk, 36)
    _category_chart(bk, 58)

    ws.merge_range(r(80), 1, r(80), 14,
                   "Booked vs cash: the P&L counts bookings and spending "
                   "in the report year; the monthly table counts money "
                   "that actually moved.  Healthy businesses watch both.",
                   S.note)
    ws.set_row(r(80), 30)
    bk.nav_row("reports", 82, first_col=1, span=3, max_col="O")
    bk.page("reports", "P", 84, landscape=True, freeze=None, fit=True)


# ----------------------------------------------------------------------
# cached P&L values from the demo model
# ----------------------------------------------------------------------
def _pl_cache(bk):
    demo = bk.demo
    if not demo.demo:
        return dict(revenue=0, cogs=0, gross=0, opex=0, net=0,
                    gross_pct=0, net_pct=0)
    year = demo.settings["year"]
    live = [e for e in demo.events
            if e["status"] != C.ES_CANCEL and e["date"].year == year]
    revenue = sum(e["price"] for e in live)
    cogs = sum(x["amount"] for x in demo.expenses
               if x["date"].year == year
               and x["category"] in ("Ingredients", "Packaging"))
    total_x = sum(x["amount"] for x in demo.expenses
                  if x["date"].year == year)
    opex = total_x - cogs
    gross = revenue - cogs
    net = gross - opex
    return dict(revenue=round(revenue, 2), cogs=round(cogs, 2),
                gross=round(gross, 2), opex=round(opex, 2),
                net=round(net, 2),
                gross_pct=(gross / revenue) if revenue else 0,
                net_pct=(net / revenue) if revenue else 0)


# ----------------------------------------------------------------------
# charts
# ----------------------------------------------------------------------
def _combo_chart(bk, row):
    ws, th = bk.ws("reports"), bk.th
    da = bk.name("data")
    ch = bk.chart("column")
    ch.add_series({
        "name": "Cash in",
        "categories": "='%s'!$H$%d:$H$%d" % (da, C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$I$%d:$I$%d" % (da, C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "fill": {"color": th.ok}, "border": {"none": True},
    })
    ch.add_series({
        "name": "Cash out",
        "categories": "='%s'!$H$%d:$H$%d" % (da, C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$J$%d:$J$%d" % (da, C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "fill": {"color": th.bad}, "border": {"none": True},
    })
    line = bk.chart("line")
    line.add_series({
        "name": "Net",
        "categories": "='%s'!$H$%d:$H$%d" % (da, C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$K$%d:$K$%d" % (da, C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "line": {"color": th.primary, "width": 2.5},
        "marker": {"type": "circle", "size": 5,
                   "fill": {"color": th.primary},
                   "border": {"color": th.primary}},
    })
    ch.combine(line)
    ch.set_title({"name": "Cash in vs cash out",
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
    ch.set_size({"width": 560, "height": 310})
    ws.insert_chart(r(row), 1, ch, {"x_offset": 4, "y_offset": 4})


def _clients_chart(bk, row):
    ws, th = bk.ws("reports"), bk.th
    da = bk.name("data")
    ch = bk.chart("bar")
    ch.add_series({
        "name": "Cash received",
        "categories": "='%s'!$Q$%d:$Q$%d" % (da, C.DATA_CLIENT_FIRST,
                                             C.DATA_CLIENT_FIRST + 14),
        "values": "='%s'!$R$%d:$R$%d" % (da, C.DATA_CLIENT_FIRST,
                                         C.DATA_CLIENT_FIRST + 14),
        "fill": {"color": th.plum}, "border": {"none": True},
    })
    ch.set_title({"name": "Top clients by cash received",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"none": True})
    ch.set_x_axis({"reverse": True, "num_font": {"size": 9,
                                                 "color": th.muted}})
    ch.set_y_axis({"num_format": "#,##0",
                   "num_font": {"size": 9, "color": th.muted}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 520, "height": 310})
    ws.insert_chart(r(row), 8, ch, {"x_offset": 4, "y_offset": 4})


def _category_chart(bk, row):
    ws, th = bk.ws("reports"), bk.th
    da = bk.name("data")
    ch = bk.chart("bar")
    ch.add_series({
        "name": "Spend",
        "categories": "='%s'!$N$%d:$N$%d" % (da, C.DATA_EXP_FIRST,
                                             C.DATA_EXP_FIRST + 10),
        "values": "='%s'!$O$%d:$O$%d" % (da, C.DATA_EXP_FIRST,
                                         C.DATA_EXP_FIRST + 10),
        "fill": {"color": th.gold}, "border": {"none": True},
    })
    ch.set_title({"name": "Where the money goes (by category)",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"none": True})
    ch.set_x_axis({"reverse": True, "num_font": {"size": 9,
                                                 "color": th.muted}})
    ch.set_y_axis({"num_format": "#,##0",
                   "num_font": {"size": 9, "color": th.muted}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 560, "height": 330})
    ws.insert_chart(r(row), 1, ch, {"x_offset": 4, "y_offset": 4})
