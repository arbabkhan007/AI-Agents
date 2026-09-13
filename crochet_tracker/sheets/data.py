"""
The hidden _Data sheet.

Everything the Dashboard, Monthly Summary and charts need is pulled onto
this tab with a single formula per cell, then the visible tabs read from
there.  This keeps formulas short, fast and impossible to break by sorting.

Column map (matches config.py):
  H..N    month table        rows 2-13
  P..Q    payment split      rows 2-7
  S..T    event expense cats rows 2-6
  V..AB   product pool       rows 2-25  (V #, W name, X units, Y revenue,
                            Z stock, AA margin, AB profit)
  AC..AF  event pool         rows 2-25  (AC #, AD name, AE sales, AF net)
  AH/AI   KPI cells          rows 2-27  (26 KPIs)
  AK/AL   product reorder sequence   rows 2-13
  AN/AO   material reorder sequence  rows 2-11
"""

from .. import config as C
from ..book import r, ci

# month table columns
M_N, M_NAME, M_REV, M_COGS, M_FEES, M_NET, M_MARGIN = \
    "H", "I", "J", "K", "L", "M", "N"
# product pool columns
P_N, P_NAME, P_UNITS, P_REV, P_STOCK, P_MARGIN, P_PROFIT = \
    "V", "W", "X", "Y", "Z", "AA", "AB"
# event pool columns
E_N, E_NAME, E_SALES, E_NET = "AC", "AD", "AE", "AF"

PROD_POOL_ROWS = C.CAP["catalog"]          # 24
EVENT_POOL_ROWS = C.CAP["events"]          # 24


def build(bk):
    ws = bk.ws("data")
    th = bk.th
    S = bk.S
    if bk.protect:
        bk.protect_sheet("data")
    hdr = S.f(**S.base(font_size=9, bold=True, font_color=th.muted,
                       bg_color=th.alt, align="center", valign="vcenter"))

    ws.set_column("A:A", 2.2)
    ws.set_column("B:AR", 13)
    ws.write(r(1), ci("A"), "Ultimate Crochet Craft Fair Tracker v%s - "
                         "calculation engine (hidden; do not edit)"
              % C.VERSION, S.footer)

    # ---------------------------------------------------------- months
    for j, lab in enumerate(["#", "Month", "Revenue", "COGS", "Fees",
                             "Net", "Margin"]):
        ws.write(r(1), ci(M_N) + j, lab, hdr)
    for m in range(12):
        row = C.DATA_MONTH_FIRST + m
        ws.write_number(r(row), ci(M_N), m + 1, hdr)
        ws.write(r(row), ci(M_NAME), C.MONTH_NAMES[m], hdr)
        _month_formulas(bk, ws, row, m + 1)

    # -------------------------------------------------------- payments
    for j, lab in enumerate(["Method", "Value"]):
        ws.write(r(1), ci("P") + j, lab, hdr)
    for i, method in enumerate(C.PAYMENT_METHODS):
        row = C.DATA_PAY_FIRST + i
        ws.write(r(row), ci("P"), method, hdr)
        ws.write_formula(
            r(row), ci("Q"),
            '=SUMIFS(%s,%s,$P$%d)'
            % (bk.rng("sales", "total"), bk.rng("sales", "method"), row),
            hdr, _cached_pay(bk, method))
        bk.stats["formulas"] += 1

    # --------------------------------------------------- expense cats
    for j, lab in enumerate(["Category", "Value"]):
        ws.write(r(1), ci("S") + j, lab, hdr)
    cats = [("Booth fees", "booth"), ("Travel", "travel"),
            ("Parking", "parking"), ("Food & drinks", "food"),
            ("Display & decor", "display")]
    for i, (cat, field) in enumerate(cats):
        row = C.DATA_EXP_FIRST + i
        ws.write(r(row), ci("S"), cat, hdr)
        ws.write_formula(r(row), ci("T"), "=SUM(%s)" % bk.rng("events",
                                                              field), hdr,
                         _cached_exp(bk, cat))
        bk.stats["formulas"] += 1

    # ---------------------------------------------------- product pool
    for j, lab in enumerate(["#", "Product", "Units", "Revenue", "Stock",
                             "Margin", "Profit"]):
        ws.write(r(1), ci(P_N) + j, lab, hdr)
    for i in range(PROD_POOL_ROWS):
        _product_formulas(bk, ws, C.DATA_PROD_FIRST + i, i)

    # ------------------------------------------------------ event pool
    for j, lab in enumerate(["#", "Event", "Sales", "Net"]):
        ws.write(r(1), ci(E_N) + j, lab, hdr)
    for i in range(EVENT_POOL_ROWS):
        _event_formulas(bk, ws, C.DATA_EVENT_FIRST + i, i)

    # ----------------------------------------------------- KPI columns
    for key, row in sorted(C.KPI_ROW.items(), key=lambda kv: kv[1]):
        ws.write(r(row), ci("AH"), C.KPI_LABEL[key], hdr)
        f, cached = _kpi_formula(bk, key)
        if f:
            ws.write_formula(r(row), ci("AI"), f, hdr, cached)
            bk.stats["formulas"] += 1
        else:
            ws.write_number(r(row), ci("AI"), 0, hdr)

    # -------------------------------------------------- reorder mirrors
    for j, lab in enumerate(["Ordered", "Item"]):
        ws.write(r(1), ci("AK") + j, lab, hdr)
        ws.write(r(1), ci("AN") + j, lab, hdr)
    _reorder_pools(bk, ws)


# ---------------------------------------------------------------------------
def _month_formulas(bk, ws, row, m):
    mref = 'DATE(ReportYear,%d,1)' % m
    sdate = bk.rng("sales", "date")
    edate = bk.rng("events", "date")
    cached = [0.0] * 5
    if bk.demo:
        for mm, rev, cogs, fees, net, units, markets, txns in \
                bk.demo.agg["months"]:
            if mm == m:
                cached = [rev, cogs, fees, net, 0.0]
    ws.write_formula(
        r(row), ci(M_REV),
        '=SUMIFS(%s,%s,">="&%s,%s,"<"&EDATE(%s,1))'
        % (bk.rng("sales", "total"), sdate, mref, sdate, mref),
        None, cached[0])
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(M_COGS),
        '=SUMIFS(%s,%s,">="&%s,%s,"<"&EDATE(%s,1))'
        % (bk.rng("sales", "cost"), sdate, mref, sdate, mref),
        None, cached[1])
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(M_FEES),
        '=SUMIFS(%s,%s,">="&%s,%s,"<"&EDATE(%s,1))'
        % (bk.rng("events", "total"), edate, mref, edate, mref),
        None, cached[2])
    bk.stats["formulas"] += 1
    ws.write_formula(r(row), ci(M_NET), "=%s%d-%s%d-%s%d"
                     % (M_REV, row, M_COGS, row, M_FEES, row), None,
                     cached[3])
    bk.stats["formulas"] += 1
    ws.write_formula(r(row), ci(M_MARGIN),
                     "=IFERROR(%s%d/%s%d,0)" % (M_NET, row, M_REV, row),
                     None, 0.0)
    bk.stats["formulas"] += 1


def _product_formulas(bk, ws, row, i):
    cat = bk.q("catalog")
    crow = C.ROW_FIRST + i
    name_c = "%s!$%s$%d" % (cat, C.COLS["catalog"]["name"], crow)
    ws.write_number(r(row), ci(P_N), i + 1, None)
    ws.write_formula(r(row), ci(P_NAME), '=IF(%s="","",%s)'
                     % (name_c, name_c), None, _cached_prod(bk, i, "name"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(P_UNITS),
        '=IF($%s%d="","",SUMIFS(%s,%s,$%s%d))'
        % (P_NAME, row, bk.rng("sales", "qty"), bk.rng("sales", "product"),
           P_NAME, row),
        None, _cached_prod(bk, i, "units"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(P_REV),
        '=IF($%s%d="","",SUMIFS(%s,%s,$%s%d))'
        % (P_NAME, row, bk.rng("sales", "total"), bk.rng("sales", "product"),
           P_NAME, row),
        None, _cached_prod(bk, i, "revenue"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(P_STOCK),
        '=IF($%s%d="","",INDEX(%s,MATCH($%s%d,%s,0)))'
        % (P_NAME, row, bk.rng("catalog", "stock"), P_NAME, row,
           bk.rng("catalog", "name")),
        None, _cached_prod(bk, i, "stock"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(P_MARGIN),
        '=IF(OR($%s%d="",$%s%d=0),"",INDEX(%s,MATCH($%s%d,%s,0)))'
        % (P_NAME, row, P_UNITS, row, bk.rng("catalog", "margin"),
           P_NAME, row, bk.rng("catalog", "name")),
        None, _cached_prod(bk, i, "margin"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(P_PROFIT),
        '=IF($%s%d="","",$%s%d-SUMIFS(%s,%s,$%s%d))'
        % (P_NAME, row, P_REV, row, bk.rng("sales", "cost"),
           bk.rng("sales", "product"), P_NAME, row),
        None, _cached_prod(bk, i, "profit"))
    bk.stats["formulas"] += 1


def _event_formulas(bk, ws, row, i):
    ev = bk.q("events")
    erow = C.ROW_FIRST + i
    name_c = "%s!$%s$%d" % (ev, C.COLS["events"]["name"], erow)
    ws.write_number(r(row), ci(E_N), i + 1, None)
    ws.write_formula(r(row), ci(E_NAME), '=IF(%s="","",%s)'
                     % (name_c, name_c), None, _cached_event(bk, i, "name"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(E_SALES),
        '=IF($%s%d="","",SUMIFS(%s,%s,$%s%d))'
        % (E_NAME, row, bk.rng("sales", "total"), bk.rng("sales", "event"),
           E_NAME, row),
        None, _cached_event(bk, i, "sales"))
    bk.stats["formulas"] += 1
    ws.write_formula(
        r(row), ci(E_NET),
        '=IF($%s%d="","",$%s%d-SUMIFS(%s,%s,$%s%d)-SUMIFS(%s,%s,$%s%d))'
        % (E_NAME, row, E_SALES, row, bk.rng("events", "total"),
           bk.rng("sales", "event"), E_NAME, row, bk.rng("sales", "cost"),
           bk.rng("sales", "event"), E_NAME, row),
        None, _cached_event(bk, i, "net"))
    bk.stats["formulas"] += 1


# ---------------------------------------------------------------------------
def _cached_pay(bk, method):
    if not bk.demo:
        return 0
    for name, value in bk.demo.agg["payments"]:
        if name == method:
            return value
    return 0


def _cached_exp(bk, cat):
    if not bk.demo:
        return 0
    for name, value in bk.demo.agg["exp_cats"]:
        if name == cat:
            return value
    return 0


def _cached_prod(bk, i, field):
    if not bk.demo or i >= len(bk.demo.products):
        return "" if field in ("name",) else 0
    p = bk.demo.products[i]
    if field == "units":
        rows = [s for s in bk.demo.sales if s["product"] == p["name"]]
        return sum(s["qty"] for s in rows)
    if field == "revenue":
        rows = [s for s in bk.demo.sales if s["product"] == p["name"]]
        return round(sum(s["qty"] * s["unit"] - s["discount"]
                         for s in rows), 2)
    if field == "profit":
        rows = [s for s in bk.demo.sales if s["product"] == p["name"]]
        rev = sum(s["qty"] * s["unit"] - s["discount"] for s in rows)
        return round(rev - sum(s["qty"] * p["unit_cost"] for s in rows), 2)
    if field == "stock":
        return p["stock"]
    if field == "margin":
        rows = [s for s in bk.demo.sales if s["product"] == p["name"]]
        return p["margin"] if rows else ""
    return p["name"]


def _cached_event(bk, i, field):
    if not bk.demo or i >= len(bk.demo.events):
        return "" if field == "name" else 0
    e = bk.demo.events[i]
    if field == "net":
        return e["net"]
    if field == "sales":
        return e["sales"]
    return e["name"]


# ---------------------------------------------------------------------------
def _kpi_formula(bk, key):
    """Return (formula | None, cached value)."""
    sa = bk.q("sales")
    sales_total = bk.rng("sales", "total")
    sales_qty = bk.rng("sales", "qty")
    sales_prod = bk.rng("sales", "product")
    sales_cost = bk.rng("sales", "cost")
    cat_name = bk.rng("catalog", "name")
    cat_cost = bk.rng("catalog", "unit_cost")
    cat_stock = bk.rng("catalog", "stock")
    cat_min = bk.rng("catalog", "min")
    cached = bk.cached(key, 0)

    pool_name = "$%s$%d:$%s$%d" % (P_NAME, C.DATA_PROD_FIRST, P_NAME,
                                   C.DATA_PROD_FIRST + PROD_POOL_ROWS - 1)
    pool_units = "$%s$%d:$%s$%d" % (P_UNITS, C.DATA_PROD_FIRST, P_UNITS,
                                    C.DATA_PROD_FIRST + PROD_POOL_ROWS - 1)
    pool_rev = "$%s$%d:$%s$%d" % (P_REV, C.DATA_PROD_FIRST, P_REV,
                                  C.DATA_PROD_FIRST + PROD_POOL_ROWS - 1)
    pool_margin = "$%s$%d:$%s$%d" % (P_MARGIN, C.DATA_PROD_FIRST, P_MARGIN,
                                     C.DATA_PROD_FIRST + PROD_POOL_ROWS - 1)
    pool_profit = "$%s$%d:$%s$%d" % (P_PROFIT, C.DATA_PROD_FIRST, P_PROFIT,
                                     C.DATA_PROD_FIRST + PROD_POOL_ROWS - 1)
    ev_name = "$%s$%d:$%s$%d" % (E_NAME, C.DATA_EVENT_FIRST, E_NAME,
                                 C.DATA_EVENT_FIRST + EVENT_POOL_ROWS - 1)
    ev_net = "$%s$%d:$%s$%d" % (E_NET, C.DATA_EVENT_FIRST, E_NET,
                                C.DATA_EVENT_FIRST + EVENT_POOL_ROWS - 1)

    if key == "revenue":
        return "=SUM(%s)" % sales_total, cached
    if key == "discounts":
        return "=SUM(%s)" % bk.rng("sales", "discount"), cached
    if key == "cogs":
        return "=SUM(%s)" % sales_cost, cached
    if key == "fees":
        return "=SUM(%s)" % bk.rng("events", "total"), cached
    if key == "profit":
        return "=AI%d-AI%d-AI%d" % (C.KPI_ROW["revenue"],
                                    C.KPI_ROW["cogs"],
                                    C.KPI_ROW["fees"]), cached
    if key == "margin":
        return "=IFERROR(AI%d/AI%d,0)" % (C.KPI_ROW["profit"],
                                          C.KPI_ROW["revenue"]), cached
    if key == "units":
        return "=SUM(%s)" % sales_qty, cached
    if key == "txns":
        return "=COUNTA(%s)" % bk.rng("sales", "date"), cached
    if key == "aov":
        return "=IFERROR(AI%d/AI%d,0)" % (C.KPI_ROW["revenue"],
                                          C.KPI_ROW["txns"]), cached
    if key == "per_item":
        return "=IFERROR(AI%d/AI%d,0)" % (C.KPI_ROW["profit"],
                                          C.KPI_ROW["units"]), cached
    if key == "events_total":
        return "=COUNTA(%s)" % bk.rng("events", "name"), cached
    if key == "events_done":
        return ('=SUMPRODUCT((%s<>"")/COUNTIF(%s,%s&""))'
                % (bk.rng("sales", "event"), bk.rng("sales", "event"),
                   bk.rng("sales", "event"))), cached
    if key == "inv_value":
        return "=SUMPRODUCT(%s*%s)" % (cat_stock, cat_cost), cached
    if key == "low_products":
        return '=SUMPRODUCT((%s<>"")*(%s<%s))' % (cat_name, cat_stock,
                                                  cat_min), cached
    if key == "low_materials":
        if bk.has("materials"):
            return ('=SUMPRODUCT((%s<>"")*(%s<=%s))'
                    % (bk.rng("materials", "name"),
                       bk.rng("materials", "remaining"),
                       bk.rng("materials", "threshold"))), cached
        return None, 0
    if key == "reorder_cost":
        if bk.has("reorder"):
            ro = bk.q("reorder")
            return "=SUM(%s!$%s$%d:$%s$%d)" % (
                ro, C.COLS["reorder"]["est"], C.RO_PROD_FIRST,
                C.COLS["reorder"]["est"], C.RO_MAT_LAST), cached
        return None, 0
    if key == "made_total":
        if bk.has("production"):
            return "=SUM(%s)" % bk.rng("production", "made"), cached
        return None, 0
    if key == "sell_through":
        if bk.has("production"):
            return ("=IFERROR(AI%d/AI%d,0)"
                    % (C.KPI_ROW["units"], C.KPI_ROW["made_total"])), cached
        return None, 0
    if key == "best_product":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (pool_name, pool_rev, pool_rev)), cached
    if key == "best_event":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (ev_name, ev_net, ev_net)), cached
    if key == "bs_units":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (pool_name, pool_units, pool_units)), cached
    if key == "bs_revenue":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (pool_name, pool_rev, pool_rev)), cached
    if key == "bs_profit":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (pool_name, pool_profit, pool_profit)), cached
    if key == "bs_margin":
        return ('=IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"")'
                % (pool_name, pool_margin, pool_margin)), cached
    if key == "bs_slow":
        return ('=IFERROR(INDEX(%s,MATCH(MIN(%s),%s,0)),"")'
                % (pool_name, pool_units, pool_units)), cached
    if key == "price_suggest":
        return "=%s!$%s$%d" % (bk.q("pricing"), "J", C.PR_OUT["price"]), \
            cached
    return None, cached


# ---------------------------------------------------------------------------
def _reorder_pools(bk, ws):
    """Mirror the Reorder List so other tabs can count what's on order."""
    if not bk.has("reorder"):
        return
    ro = bk.q("reorder")
    for i in range(C.RO_PROD_LAST - C.RO_PROD_FIRST + 1):
        row = C.DATA_SEQP_FIRST + i
        src = C.RO_PROD_FIRST + i
        ws.write_formula(r(row), ci("AK"),
                         "=IF(%s!$%s$%d=\"\",\"\",%s!$%s$%d)"
                         % (ro, C.COLS["reorder"]["item"], src,
                            ro, C.COLS["reorder"]["ordered"], src),
                         None, "")
        ws.write_formula(r(row), ci("AL"),
                         "=IF(%s!$%s$%d=\"\",\"\",%s!$%s$%d)"
                         % (ro, C.COLS["reorder"]["item"], src,
                            ro, C.COLS["reorder"]["item"], src),
                         None, "")
        bk.stats["formulas"] += 2
    for i in range(C.RO_MAT_LAST - C.RO_MAT_FIRST + 1):
        row = C.DATA_SEQM_FIRST + i
        src = C.RO_MAT_FIRST + i
        ws.write_formula(r(row), ci("AN"),
                         "=IF(%s!$%s$%d=\"\",\"\",%s!$%s$%d)"
                         % (ro, C.COLS["reorder"]["item"], src,
                            ro, C.COLS["reorder"]["ordered"], src),
                         None, "")
        ws.write_formula(r(row), ci("AO"),
                         "=IF(%s!$%s$%d=\"\",\"\",%s!$%s$%d)"
                         % (ro, C.COLS["reorder"]["item"], src,
                            ro, C.COLS["reorder"]["item"], src),
                         None, "")
        bk.stats["formulas"] += 2
