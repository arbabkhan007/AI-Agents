"""
The hidden ``_Data`` engine.

Every chart and every headline number on the Dashboard reads from small,
tidy pools on this sheet, so the visible tabs never have to carry helper
columns.  The KPI table (AE:AF) is the single source of truth for the
scorecards; the pools in H:L, N:O, Q:R, T:U and AA:AC feed the charts and
the calendar.

In the Basic edition the sheets for menu costing, inventory, shopping,
staff, equipment, suppliers and tax do not exist - those KPIs are written
as plain zeros so the Dashboard never shows a ``#REF!``.
"""

from .. import config as C
from ..book import r

PREMIUM_ONLY = ("inv_value", "low_stock", "shop_lines", "shop_cost",
                "staff_unpaid", "equip_value", "equip_service",
                "tax_collected", "tax_due", "menu_items", "menu_margin")


def build(bk):
    ws = bk.ws("data")
    S, th = bk.S, bk.th
    demo = bk.demo

    ws.write(0, 0, "%s - calculation engine (hidden).  Every number on the "
              "Dashboard and the reports is computed here." % C.PRODUCT,
             S.note_plain)
    ws.set_column("A:A", 60)
    ws.set_column("H:L", 12)
    ws.set_column("N:U", 22)
    ws.set_column("AA:AC", 24)
    ws.set_column("AE:AF", 46)

    ev = bk.q("events")
    ex = bk.q("expenses")
    inc = bk.q("income")

    EV_DATE = "%s!$E$%d:$E$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_TYPE = "%s!$F$%d:$F$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_GUEST = "%s!$G$%d:$G$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_MENU = "%s!$H$%d:$H$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_CLIENT = "%s!$D$%d:$D$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_COST = "%s!$K$%d:$K$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_PRICE = "%s!$L$%d:$L$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_PROFIT = "%s!$M$%d:$M$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EV_STATUS = "%s!$Q$%d:$Q$%d" % (ev, C.ROW_FIRST, C.last_row("events"))
    EX_DATE = "%s!$C$%d:$C$%d" % (ex, C.ROW_FIRST, C.last_row("expenses"))
    EX_CAT = "%s!$E$%d:$E$%d" % (ex, C.ROW_FIRST, C.last_row("expenses"))
    EX_AMT = "%s!$G$%d:$G$%d" % (ex, C.ROW_FIRST, C.last_row("expenses"))
    IN_CLIENT = "%s!$D$%d:$D$%d" % (inc, C.ROW_FIRST, C.last_row("income"))
    IN_DATE = "%s!$E$%d:$E$%d" % (inc, C.ROW_FIRST, C.last_row("income"))
    IN_AMT = "%s!$F$%d:$F$%d" % (inc, C.ROW_FIRST, C.last_row("income"))
    IN_RECV = "%s!$J$%d:$J$%d" % (inc, C.ROW_FIRST, C.last_row("income"))
    IN_BAL = "%s!$K$%d:$K$%d" % (inc, C.ROW_FIRST, C.last_row("income"))
    IN_DUE = "%s!$L$%d:$L$%d" % (inc, C.ROW_FIRST, C.last_row("income"))

    # ------------------------------------------------------------------
    # monthly pool  H2:L13  (month, cash in, cash out, net, events)
    # ------------------------------------------------------------------
    for i, label in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
        row = C.DATA_MONTH_FIRST + i
        ws.write(r(row), 7, label, S.note_plain)              # H
        ws.write_formula(r(row), 8,
                         # comma form + --: a "" formula column (received) would raise
                         # #VALUE! with the * form in Excel
                         "=SUMPRODUCT(--((%s<>\"\")*(MONTH(%s)=%d)),%s)"
                         % (IN_DATE, IN_DATE, i + 1, IN_RECV),
                         S.note_plain, _c(demo, ("months", i, 1)))
        ws.write_formula(r(row), 9,
                         # comma form + --: a "" formula column (received) would raise
                         # #VALUE! with the * form in Excel
                         "=SUMPRODUCT(--((%s<>\"\")*(MONTH(%s)=%d)),%s)"
                         % (EX_DATE, EX_DATE, i + 1, EX_AMT),
                         S.note_plain, _c(demo, ("months", i, 2)))
        ws.write_formula(r(row), 10, "=I%d-J%d" % (row, row),
                         S.note_plain, _c(demo, ("months", i, 3)))
        ws.write_formula(r(row), 11,
                         "=SUMPRODUCT((%s<>\"\")*(MONTH(%s)=%d)*1)"
                         % (EV_DATE, EV_DATE, i + 1),
                         S.note_plain, _c(demo, ("months", i, 4)))
    ws.write(r(C.DATA_MONTH_FIRST - 1), 7, "Month", S.thead)
    ws.write(r(C.DATA_MONTH_FIRST - 1), 8, "Cash in", S.thead)
    ws.write(r(C.DATA_MONTH_FIRST - 1), 9, "Cash out", S.thead)
    ws.write(r(C.DATA_MONTH_FIRST - 1), 10, "Net", S.thead)
    ws.write(r(C.DATA_MONTH_FIRST - 1), 11, "Events", S.thead)

    # ------------------------------------------------------------------
    # expense-category pool  N2:O12
    # ------------------------------------------------------------------
    ws.write(r(C.DATA_EXP_FIRST - 1), 13, "Expense category", S.thead)
    ws.write(r(C.DATA_EXP_FIRST - 1), 14, "Spend", S.thead)
    for i, cat in enumerate(C.EXPENSE_CATEGORIES):
        row = C.DATA_EXP_FIRST + i
        ws.write(r(row), 13, cat, S.note_plain)
        ws.write_formula(r(row), 14,
                         "=SUMIF(%s,$N%d,%s)" % (EX_CAT, row, EX_AMT),
                         S.note_plain,
                         _c(demo, ("exp_cats", cat)))
    # ------------------------------------------------------------------
    # event-type pool  N16:O24
    # ------------------------------------------------------------------
    ws.write(r(C.DATA_TYPE_FIRST - 1), 13, "Event type", S.thead)
    ws.write(r(C.DATA_TYPE_FIRST - 1), 14, "Revenue", S.thead)
    for i, t in enumerate(C.EVENT_TYPES):
        row = C.DATA_TYPE_FIRST + i
        ws.write(r(row), 13, t, S.note_plain)
        ws.write_formula(r(row), 14,
                         "=SUMIFS(%s,%s,$N%d,%s,\"<>%s\")"
                         % (EV_PRICE, EV_TYPE, row, EV_STATUS, C.ES_CANCEL),
                         S.note_plain, _c(demo, ("types", i, 1)))

    # ------------------------------------------------------------------
    # status pool  N28:O33
    # ------------------------------------------------------------------
    ws.write(r(C.DATA_STATUS_FIRST - 1), 13, "Status", S.thead)
    ws.write(r(C.DATA_STATUS_FIRST - 1), 14, "Events", S.thead)
    for i, st in enumerate(C.EVENT_STATUSES):
        row = C.DATA_STATUS_FIRST + i
        ws.write(r(row), 13, st, S.note_plain)
        ws.write_formula(r(row), 14,
                         "=COUNTIF(%s,$N%d)" % (EV_STATUS, row),
                         S.note_plain, _c(demo, ("status_counts", st)))

    # ------------------------------------------------------------------
    # client pool  Q26:R40  (first 15 clients + cash received)
    # ------------------------------------------------------------------
    ws.write(r(C.DATA_CLIENT_FIRST - 1), 16, "Client", S.thead)
    ws.write(r(C.DATA_CLIENT_FIRST - 1), 17, "Received", S.thead)
    cl = bk.q("clients")
    for i in range(15):
        row = C.DATA_CLIENT_FIRST + i
        src = C.ROW_FIRST + i
        ws.write_formula(r(row), 16,
                         "=IF(%s!$C$%d=\"\",\"\",%s!$C$%d)"
                         % (cl, src, cl, src), S.note_plain,
                         _c(demo, ("clients_pool", i, 0), missing=""))
        ws.write_formula(r(row), 17,
                         "=IF($Q%d=\"\",\"\",SUMIF(%s,$Q%d,%s))"
                         % (row, IN_CLIENT, row, IN_RECV), S.note_plain,
                         _c(demo, ("clients_pool", i, 1), missing=""))

    # ------------------------------------------------------------------
    # menu pool  T26:U40  (item + how many booked events feature it)
    # ------------------------------------------------------------------
    if bk.has("menu"):
        ws.write(r(C.DATA_MENU_FIRST - 1), 19, "Menu item", S.thead)
        ws.write(r(C.DATA_MENU_FIRST - 1), 20, "Booked", S.thead)
        me = bk.q("menu")
        for i in range(15):
            row = C.DATA_MENU_FIRST + i
            src = C.ROW_FIRST + i
            ws.write_formula(r(row), 19,
                             "=IF(%s!$C$%d=\"\",\"\",%s!$C$%d)"
                             % (me, src, me, src), S.note_plain,
                             _c(demo, ("menu_pool", i, 0), missing=""))
            ws.write_formula(r(row), 20,
                             "=IF($T%d=\"\",\"\",SUMPRODUCT((%s<>\"\")*"
                             "IFERROR(--ISNUMBER(SEARCH($T%d,%s)),0)))"
                             % (row, EV_MENU, row, EV_MENU),
                             S.note_plain,
                             _c(demo, ("menu_pool", i, 1), missing=""))

    # ------------------------------------------------------------------
    # upcoming-events pool  AA2:AC41  (date-sorted, feeds the calendar)
    # ------------------------------------------------------------------
    live = ('(%s>=TODAY())*(%s<>"%s")*(%s<>"%s")'
            % (EV_DATE, EV_STATUS, C.ES_CANCEL, EV_STATUS, C.ES_DONE))
    ws.write(r(1), 26, "Upcoming date", S.thead)
    ws.write(r(1), 27, "Upcoming event", S.thead)
    ws.write(r(1), 28, "Status", S.thead)
    for i in range(C.DATA_POOL_ROWS):
        row = C.DATA_POOL_FIRST + i
        ws.write_formula(r(row), 26,
                         "=IFERROR(AGGREGATE(15,6,%s/%s,%d),\"\")"
                         % (EV_DATE, live, i + 1), S.note_plain,
                         _c(demo, ("upcoming", i, 0), missing=""))
        ws.write_formula(r(row), 27,
                         "=IF($AA%d=\"\",\"\",INDEX(%s,MATCH($AA%d,%s,0))"
                         "&\" - \"&INDEX(%s,MATCH($AA%d,%s,0)))"
                         % (row, bk.rng("events", "client", quoted=True)[0:0]
                            or "%s!$D$%d:$D$%d" % (ev, C.ROW_FIRST,
                                                   C.last_row("events")),
                            row, EV_DATE,
                            EV_TYPE, row, EV_DATE),
                         S.note_plain, _c(demo, ("upcoming", i, 1), missing=""))
        ws.write_formula(r(row), 28,
                         "=IF($AA%d=\"\",\"\",INDEX(%s,MATCH($AA%d,%s,0)))"
                         % (row, EV_STATUS, row, EV_DATE),
                         S.note_plain, _c(demo, ("upcoming", i, 2), missing=""))

    # ------------------------------------------------------------------
    # outstanding-payments pool  AA42:AC101  (feeds the calendar)
    # ------------------------------------------------------------------
    ws.write(r(C.DATA_DUE_FIRST - 1), 26, "Payment due", S.thead)
    ws.write(r(C.DATA_DUE_FIRST - 1), 27, "Owes", S.thead)
    ws.write(r(C.DATA_DUE_FIRST - 1), 28, "Balance", S.thead)
    dues = sorted(demo.agg.get("dues", []),
                  key=lambda d: d[0]) if demo.demo else []
    for i in range(C.DATA_DUE_ROWS):
        row = C.DATA_DUE_FIRST + i
        ws.write_formula(r(row), 26,
                         # (due<>"") guard: empty rows have a "" balance and
                         # ("" > 0) is TRUE in Excel, which would leak 0
                         # dates into the pool.
                         "=IFERROR(AGGREGATE(15,6,%s/((%s<>\"\")*(%s>0)),"
                         "%d),\"\")"
                         % (IN_DUE, IN_DUE, IN_BAL, i + 1), S.note_plain,
                         _dd(dues, i, 0))
        ws.write_formula(r(row), 27,
                         "=IF($AA%d=\"\",\"\",INDEX(%s,MATCH($AA%d,%s,0))"
                         "&\" (\"&INDEX(%s,MATCH($AA%d,%s,0))&\")\")"
                         % (row, IN_CLIENT, row, IN_DUE,
                            "%s!$C$%d:$C$%d" % (inc, C.ROW_FIRST,
                                                C.last_row("income")),
                            row, IN_DUE),
                         S.note_plain, _dd(dues, i, 1))
        ws.write_formula(r(row), 28,
                         "=IF($AA%d=\"\",\"\",INDEX(%s,MATCH($AA%d,%s,0)))"
                         % (row, IN_BAL, row, IN_DUE),
                         S.note_plain, _dd(dues, i, 2))

    # ------------------------------------------------------------------
    # KPI table  AE2:AF36
    # ------------------------------------------------------------------
    ws.write(r(1), 30, "KPI", S.thead)
    ws.write(r(1), 31, "Value", S.thead)
    formulas = _kpi_formulas(bk, dict(
        EV_DATE=EV_DATE, EV_TYPE=EV_TYPE, EV_GUEST=EV_GUEST,
        EV_PRICE=EV_PRICE, EV_PROFIT=EV_PROFIT, EV_STATUS=EV_STATUS,
        EX_CAT=EX_CAT, EX_AMT=EX_AMT, IN_AMT=IN_AMT, IN_RECV=IN_RECV,
        IN_BAL=IN_BAL, IN_DUE=IN_DUE))
    for key, label in C.KPI_LABEL.items():
        row = C.KPI_ROW[key]
        ws.write(r(row), 30, label, S.note_plain)
        if key in formulas:
            formula, cached = formulas[key]
            ws.write_formula(r(row), 31, formula, S.note_plain, cached)
        else:
            ws.write(r(row), 31, 0, S.note_plain)

    # keep the engine locked down like every other tab
    bk.page("data", "AF", C.DATA_DUE_FIRST + C.DATA_DUE_ROWS,
            landscape=False, fit=False, freeze=None)


def _c(demo, path, missing=0):
    """Pull a cached pool value out of the demo model (``missing`` if blank)."""
    if not demo.demo:
        return missing
    try:
        v = demo.agg
        for p in path:
            v = v[p]
    except (KeyError, IndexError, TypeError):
        return missing
    if v is None:
        return missing
    return v


def _dd(dues, i, j):
    try:
        v = dues[i][j]
    except IndexError:
        return ""          # formula returns "" for empty pool rows
    return v


def _kpi_formulas(bk, R):
    """Return {kpi: (formula, cached)} for every KPI the edition supports."""
    evq = bk.q("events")
    clq = bk.q("clients")
    incq = bk.q("income")
    demo, has = bk.demo, bk.has
    cached = bk.cached
    F = {}

    def K(key, formula):
        F[key] = (formula, cached(key, 0))

    K("revenue", "=SUM(%s)" % R["IN_RECV"])
    K("expenses", "=SUM(%s)" % R["EX_AMT"])
    K("profit", "=$AF$2-$AF$3")
    K("margin", "=IFERROR($AF$4/$AF$2,0)")
    K("events_total", "=COUNTA(%s!$C$%d:$C$%d)"
      % (evq, C.ROW_FIRST, C.last_row("events")))
    K("events_done", "=COUNTIF(%s,\"%s\")" % (R["EV_STATUS"], C.ES_DONE))
    K("events_confirmed", "=COUNTIF(%s,\"%s\")+COUNTIF(%s,\"%s\")"
      % (R["EV_STATUS"], C.ES_DEPOSIT, R["EV_STATUS"], C.ES_CONFIRMED))
    K("events_cancelled", "=COUNTIF(%s,\"%s\")"
      % (R["EV_STATUS"], C.ES_CANCEL))
    K("avg_order", "=IFERROR(AVERAGEIF(%s,\"<>%s\",%s),0)"
      % (R["EV_STATUS"], C.ES_CANCEL, R["EV_PRICE"]))
    K("avg_guests", "=IFERROR(AVERAGEIF(%s,\"<>%s\",%s),0)"
      % (R["EV_STATUS"], C.ES_CANCEL, R["EV_GUEST"]))
    K("avg_profit", "=IFERROR(AVERAGEIF(%s,\"<>%s\",%s),0)"
      % (R["EV_STATUS"], C.ES_CANCEL, R["EV_PROFIT"]))
    K("guests_total", "=SUMIF(%s,\"%s\",%s)"
      % (R["EV_STATUS"], C.ES_DONE, R["EV_GUEST"]))
    K("outstanding", "=SUM(%s)" % R["IN_BAL"])
    K("overdue", "=SUMPRODUCT((%s>0)*(%s<>\"\")*(%s<TODAY()))"
      % (R["IN_BAL"], R["IN_DUE"], R["IN_DUE"]))
    K("invoices_open", "=COUNTIF(%s,\">0\")" % R["IN_BAL"])
    K("food_cost", "=SUMIF(%s,\"Ingredients\",%s)+SUMIF(%s,\"Packaging\",%s)"
      % (R["EX_CAT"], R["EX_AMT"], R["EX_CAT"], R["EX_AMT"]))
    K("labor_cost", "=SUMIF(%s,\"Staff / Labor\",%s)"
      % (R["EX_CAT"], R["EX_AMT"]))
    K("food_pct", "=IFERROR($AF$17/$AF$2,0)")
    K("labor_pct", "=IFERROR($AF$18/$AF$2,0)")
    K("repeat_pct",
      "=IFERROR(SUMPRODUCT((COUNTIF(%s!$C$%d:$C$%d,%s!$C$%d:$C$%d&\"\")>1)"
      "*((%s!$C$%d:$C$%d&\"\")<>\"\")*1)/COUNTA(%s!$C$%d:$C$%d),0)"
      % (clq, C.ROW_FIRST, C.last_row("clients"),
         clq, C.ROW_FIRST, C.last_row("clients"),
         clq, C.ROW_FIRST, C.last_row("clients"),
         clq, C.ROW_FIRST, C.last_row("clients")))

    # edition-dependent KPIs ------------------------------------------------
    if has("inventory"):
        ivq = bk.q("inventory")
        IV_VAL = "%s!$I$%d:$I$%d" % (ivq, C.ROW_FIRST, C.last_row("inventory"))
        IV_ST = "%s!$K$%d:$K$%d" % (ivq, C.ROW_FIRST, C.last_row("inventory"))
        K("inv_value", "=SUM(%s)" % IV_VAL)
        K("low_stock", "=COUNTIF(%s,\"%s\")" % (IV_ST, "\U0001F534 Reorder"))
    if has("shopping"):
        shq = bk.q("shopping")
        SH_BUY = "%s!$G$%d:$G$%d" % (shq, C.ROW_FIRST, C.last_row("shopping"))
        SH_COST = "%s!$I$%d:$I$%d" % (shq, C.ROW_FIRST, C.last_row("shopping"))
        SH_TICK = "%s!$J$%d:$J$%d" % (shq, C.ROW_FIRST, C.last_row("shopping"))
        # ISNUMBER guards the to-buy formula column: ("" > 0) is TRUE in
        # Excel, counting every empty row as a line to buy.  Comma form
        # keeps the cost column's "" formulas from raising #VALUE!.
        K("shop_lines", "=SUMPRODUCT(ISNUMBER(%s)*(%s>0)*(%s<>\"%s\"))"
          % (SH_BUY, SH_BUY, SH_TICK, C.TICK))
        K("shop_cost", "=SUMPRODUCT(ISNUMBER(%s)*(%s>0)*(%s<>\"%s\"),%s)"
          % (SH_BUY, SH_BUY, SH_TICK, C.TICK, SH_COST))
    if has("staff"):
        stq = bk.q("staff")
        ST_NAME = "%s!$C$%d:$C$%d" % (stq, C.ROW_FIRST, C.last_row("staff"))
        ST_TICK = "%s!$J$%d:$J$%d" % (stq, C.ROW_FIRST, C.last_row("staff"))
        K("staff_unpaid", "=SUMPRODUCT((%s<>\"\")*(%s<>\"%s\"))"
          % (ST_NAME, ST_TICK, C.TICK))
    if has("equipment"):
        eqq = bk.q("equipment")
        EQ_VAL = "%s!$J$%d:$J$%d" % (eqq, C.ROW_FIRST, C.last_row("equipment"))
        EQ_ST = "%s!$L$%d:$L$%d" % (eqq, C.ROW_FIRST, C.last_row("equipment"))
        K("equip_value", "=SUM(%s)" % EQ_VAL)
        K("equip_service", "=COUNTIF(%s,\"%s\")+COUNTIF(%s,\"%s\")"
          % (EQ_ST, "\U0001F527 Service", EQ_ST, "\U0001F7E1 Soon"))
    if has("tax"):
        txq = bk.q("tax")
        K("tax_collected", "=%s!$C$%d" % (txq, C.TAX_SUM["collected"]))
        K("tax_due", "=%s!$C$%d" % (txq, C.TAX_SUM["due"]))
    if has("quote"):
        quq = bk.q("quote")
        K("quote_price", "=%s!$E$%d" % (quq, C.QUOTE_OUT["price"]))
        K("quote_per_guest", "=%s!$E$%d" % (quq, C.QUOTE_OUT["per_guest"]))
    if has("menu"):
        meq = bk.q("menu")
        ME_ITEM = "%s!$C$%d:$C$%d" % (meq, C.ROW_FIRST, C.last_row("menu"))
        ME_MARGIN = "%s!$J$%d:$J$%d" % (meq, C.ROW_FIRST, C.last_row("menu"))
        K("menu_items", "=COUNTA(%s)" % ME_ITEM)
        K("menu_margin", "=IFERROR(AVERAGE(%s),0)" % ME_MARGIN)

    K("best_type", "=IF(MAX($O$16:$O$24)=0,\"-\",INDEX($N$16:$N$24,"
      "MATCH(MAX($O$16:$O$24),$O$16:$O$24,0)))")
    K("best_client", "=IF(MAX($R$26:$R$40)=0,\"-\",INDEX($Q$26:$Q$40,"
      "MATCH(MAX($R$26:$R$40),$R$26:$R$40,0)))")
    return F
