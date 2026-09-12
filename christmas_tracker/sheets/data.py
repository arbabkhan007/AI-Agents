"""
The hidden ``_Data`` worksheet.

Everything the dashboard, the charts and the "what's left to do" panel need is
calculated once, here:

  A:C   occasion presets (feeds the Setup "reuse for any event" helper)
  E:F   the preset the user picked, resolved to a month/day
  H:P   per-recipient gift + money summary
  Q:R   spend per gift category            (pie / bar charts)
  T:U   gift status breakdown              (doughnut chart)
  AA:AC the upcoming-deadline pool         (dashboard "next 5 deadlines")
  AE:AF the KPI table - every headline number in the workbook

Keeping the maths on one hidden sheet means the visible tabs stay clean and
the dashboard formulas stay readable (``=_Data!$AF$5`` instead of a
nine-line SUMPRODUCT).
"""

from .. import config as C
from ..book import r, ci

TODAY_FN = "TODAY()"


def _setup_cell(col, row):
    return "'%s'!$%s$%d" % (C.SHEET_NAMES["setup"], col, row)


def build(bk):
    ws = bk.ws("data")
    S = bk.S
    m = bk.demo
    agg = m.agg

    hdr = S.f(**S.base(font_size=9, bold=True, font_color=bk.th.white,
                       bg_color=bk.th.muted, align="center", valign="vcenter",
                       border=1, border_color=bk.th.muted))
    txt = S.f(**S.base(font_size=9, font_color=bk.th.ink, align="left"))
    num = S.f(**S.base(font_size=9, num_format="#,##0.00"))
    integer = S.f(**S.base(font_size=9, num_format="0"))
    dt = S.f(**S.base(font_size=9, num_format="dd mmm yyyy"))
    pct = S.f(**S.base(font_size=9, num_format="0%"))

    ws.set_column("A:A", 20)
    ws.set_column("B:C", 8)
    ws.set_column("D:D", 2)
    ws.set_column("E:F", 10)
    ws.set_column("G:G", 2)
    ws.set_column("H:H", 20)
    ws.set_column("I:P", 11)
    ws.set_column("Q:Q", 18)
    ws.set_column("R:R", 11)
    ws.set_column("S:S", 2)
    ws.set_column("T:T", 18)
    ws.set_column("U:U", 9)
    ws.set_column("V:Z", 2)
    ws.set_column("AA:AA", 13)
    ws.set_column("AB:AB", 44)
    ws.set_column("AC:AC", 7)
    ws.set_column("AD:AD", 2)
    ws.set_column("AE:AE", 30)
    ws.set_column("AF:AF", 14)
    ws.set_column("AG:AH", 40)

    # ------------------------------------------------------------------
    # occasion presets
    # ------------------------------------------------------------------
    for col, label in (("A", "Occasion"), ("B", "Month"), ("C", "Day")):
        ws.write(r(1), ci(col), label, hdr)
    for i, (name, month, day) in enumerate(C.OCCASIONS):
        row = C.DATA_PRESET_FIRST + i
        ws.write(r(row), ci("A"), name, txt)
        ws.write(r(row), ci("B"), month if month else "", integer)
        ws.write(r(row), ci("C"), day if day else "", integer)

    ws.write(r(1), ci("E"), "Preset month", hdr)
    ws.write(r(1), ci("F"), "Preset day", hdr)
    occ_first = C.DATA_PRESET_FIRST
    occ_last = C.DATA_PRESET_FIRST + C.OCCASION_ROWS - 1
    ws.write_formula(
        r(2), ci("E"),
        "=IFERROR(INDEX($B$%d:$B$%d,MATCH(%s,$A$%d:$A$%d,0)),\"\")"
        % (occ_first, occ_last, _setup_cell("C", C.SU_OCCASION),
           occ_first, occ_last), integer, "")
    ws.write_formula(
        r(2), ci("F"),
        "=IFERROR(INDEX($C$%d:$C$%d,MATCH(%s,$A$%d:$A$%d,0)),\"\")"
        % (occ_first, occ_last, _setup_cell("C", C.SU_OCCASION),
           occ_first, occ_last), integer, "")
    bk.stats["formulas"] += 2

    # ------------------------------------------------------------------
    # per-recipient summary  (H:P)
    # ------------------------------------------------------------------
    rec_headers = ["Recipient", "Planned", "Spent", "Gifts", "Bought",
                   "Wrapped", "Delivered", "To buy", "Done %"]
    for i, label in enumerate(rec_headers):
        ws.write(r(1), ci("H") + i, label, hdr)

    g = bk.q("gifts")
    gt_recip = bk.rng("gifts", "recipient")
    gt_budget = bk.rng("gifts", "budget")
    gt_cost = bk.rng("gifts", "cost")
    gt_status = bk.rng("gifts", "status")
    gt_wrap = bk.rng("gifts", "wrapped")
    gt_deliv = bk.rng("gifts", "delivered")

    for i in range(C.DATA_REC_ROWS):
        row = C.DATA_REC_FIRST + i
        setup_row = C.SU_LIST_FIRST + i
        name_ref = "$H%d" % row
        cached_rec = agg["recipients"][i]
        ws.write_formula(r(row), ci("H"),
                         "=IF(%s=\"\",\"\",%s)"
                         % (_setup_cell("B", setup_row),
                            _setup_cell("B", setup_row)),
                         txt, cached_rec["name"])
        ws.write_formula(r(row), ci("I"),
                         "=IF(%s=\"\",0,SUMIF(%s,%s,%s))"
                         % (name_ref, gt_recip, name_ref, gt_budget),
                         num, cached_rec["planned"])
        ws.write_formula(r(row), ci("J"),
                         "=IF(%s=\"\",0,SUMIF(%s,%s,%s))"
                         % (name_ref, gt_recip, name_ref, gt_cost),
                         num, cached_rec["spent"])
        ws.write_formula(r(row), ci("K"),
                         "=IF(%s=\"\",0,COUNTIF(%s,%s))"
                         % (name_ref, gt_recip, name_ref),
                         integer, cached_rec["gifts"])
        bought = "".join(
            "+COUNTIFS(%s,%s,%s,\"%s\")" % (gt_recip, name_ref, gt_status, s)
            for s in (C.ST_BOUGHT, C.ST_WRAPPED, C.ST_DELIVERED))
        ws.write_formula(r(row), ci("L"),
                         "=IF(%s=\"\",0%s+IF(CountOrdered=\"Yes\","
                         "COUNTIFS(%s,%s,%s,\"%s\"),0))"
                         % (name_ref, bought, gt_recip, name_ref, gt_status,
                            C.ST_ORDERED),
                         integer, cached_rec["bought"])
        ws.write_formula(r(row), ci("M"),
                         "=IF(%s=\"\",0,COUNTIFS(%s,%s,%s,\"%s\")"
                         "+SUMPRODUCT((%s=%s)*(%s<>\"%s\")*((%s=\"%s\")"
                         "+(%s=\"%s\")>0)))"
                         % (name_ref, gt_recip, name_ref, gt_wrap, C.TICK,
                            gt_recip, name_ref, gt_wrap, C.TICK, gt_status,
                            C.ST_WRAPPED, gt_status, C.ST_DELIVERED),
                         integer, cached_rec["wrapped"])
        ws.write_formula(r(row), ci("N"),
                         "=IF(%s=\"\",0,COUNTIFS(%s,%s,%s,\"%s\")"
                         "+SUMPRODUCT((%s=%s)*(%s<>\"%s\")*(%s=\"%s\")))"
                         % (name_ref, gt_recip, name_ref, gt_deliv, C.TICK,
                            gt_recip, name_ref, gt_deliv, C.TICK, gt_status,
                            C.ST_DELIVERED),
                         integer, cached_rec["delivered"])
        ws.write_formula(r(row), ci("O"),
                         "=IF(%s=\"\",0,MAX(0,$K%d-$L%d))" % (name_ref, row,
                                                              row),
                         integer, cached_rec["to_buy"])
        ws.write_formula(r(row), ci("P"),
                         "=IF(%s=\"\",\"\",IFERROR($L%d/$K%d,0))"
                         % (name_ref, row, row), pct, cached_rec["pct"])
        bk.stats["formulas"] += 9

    # ------------------------------------------------------------------
    # spend by gift category  (Q:R)
    # ------------------------------------------------------------------
    ws.write(r(1), ci("Q"), "Gift category", hdr)
    ws.write(r(1), ci("R"), "Spent", hdr)
    gt_cat = bk.rng("gifts", "category")
    for i in range(C.DATA_CAT_ROWS):
        row = C.DATA_CAT_FIRST + i
        setup_row = C.SU_LIST_FIRST + i
        cat_ref = "$Q%d" % row
        cached_cat = agg["categories"][i]
        ws.write_formula(r(row), ci("Q"),
                         "=IF(%s=\"\",\"\",%s)"
                         % (_setup_cell("D", setup_row),
                            _setup_cell("D", setup_row)),
                         txt, cached_cat["name"])
        ws.write_formula(r(row), ci("R"),
                         "=IF(%s=\"\",0,SUMIF(%s,%s,%s))"
                         % (cat_ref, gt_cat, cat_ref, gt_cost),
                         num, cached_cat["spent"])
        bk.stats["formulas"] += 2

    # ------------------------------------------------------------------
    # gift status breakdown  (T:U)
    # ------------------------------------------------------------------
    ws.write(r(1), ci("T"), "Status", hdr)
    ws.write(r(1), ci("U"), "Gifts", hdr)
    for i, status in enumerate(C.STATUSES):
        row = C.DATA_STATUS_FIRST + i
        ws.write_formula(r(row), ci("T"),
                         "=%s" % _setup_cell("B", C.SU_FIXED_FIRST + i),
                         txt, status)
        ws.write_formula(r(row), ci("U"),
                         "=COUNTIF(%s,$T%d)" % (gt_status, row),
                         integer, agg["status_counts"][i]["count"])
        bk.stats["formulas"] += 2

    # ------------------------------------------------------------------
    # deadline pool  (AA:AC)
    # ------------------------------------------------------------------
    ws.write(r(1), ci("AA"), "Due", hdr)
    ws.write(r(1), ci("AB"), "What", hdr)
    ws.write(r(1), ci("AC"), "Days", hdr)
    pool = _pool(bk)
    for i, (key, label, days) in enumerate(pool):
        row = C.DATA_POOL_FIRST + i
        ws.write_formula(r(row), ci("AA"), key[0], dt, key[1])
        ws.write_formula(r(row), ci("AB"), label[0], txt, label[1])
        ws.write_formula(r(row), ci("AC"), days[0], integer, days[1])
        bk.stats["formulas"] += 3

    # ------------------------------------------------------------------
    # KPI table  (AE:AF)
    # ------------------------------------------------------------------
    ws.write(r(1), ci("AE"), "Metric", hdr)
    ws.write(r(1), ci("AF"), "Value", hdr)
    for key, formula, numfmt in _kpis(bk):
        row = C.KPI_ROW[key]
        fmt = S.f(**S.base(font_size=9, num_format=numfmt,
                           font_color=bk.th.primary, bold=True))
        cached = agg.get(key, 0)
        if isinstance(cached, bool):
            cached = int(cached)
        ws.write(r(row), ci("AE"), C.KPI_LABEL[key], txt)
        ws.write_formula(r(row), ci("AF"), formula, fmt,
                         cached if cached is not None else 0)
        bk.stats["formulas"] += 1

    ws.write(r(1), ci("AH"),
             "This sheet is hidden on purpose: it feeds the dashboard, the "
             "charts and every automatic number in the workbook. Please do "
             "not delete or rename it (unhide with: right-click any tab > "
             "Unhide).", S.f(**S.base(font_size=10, italic=True,
                                      font_color=bk.th.muted, align="left",
                                      valign="vcenter")))
    ws.set_row(r(1), 22)

    # The engine room is nothing but formulas: lock it with the same
    # password as every other tab.
    bk.protect_sheet("data")
    return ws


# ---------------------------------------------------------------------------
# deadline pool
# ---------------------------------------------------------------------------
def _pool(bk):
    """Return [(date_formula, cached), (label_formula, cached),
    (days_formula, cached)] for every pool row."""
    m = bk.demo
    rows = []

    gt_dl = bk.col("gifts", "deadline")
    gt_st = bk.col("gifts", "status")
    gt_idea = bk.col("gifts", "idea")
    gt_rec = bk.col("gifts", "recipient")
    for i in range(C.POOL_GIFT_ROWS):
        srow = C.ROW_FIRST + i
        prow = C.DATA_POOL_FIRST + i
        f_date = ("=IF(OR('{g}'!${d}${s}=\"\",'{g}'!${d}${s}<TODAY(),"
                  "'{g}'!${st}${s}=\"{dl}\"),\"\",'{g}'!${d}${s})"
                  ).format(g=C.SHEET_NAMES["gifts"], d=gt_dl, s=srow,
                           st=gt_st, dl=C.ST_DELIVERED)
        f_lab = ("=IF($AA${p}=\"\",\"\",\"\U0001F381 \"&'{g}'!${i}${s}&"
                 "\" \u2014 \"&'{g}'!${c}${s})"
                 ).format(p=prow, g=C.SHEET_NAMES["gifts"], i=gt_idea, s=srow,
                          c=gt_rec)
        f_days = "=IF($AA${p}=\"\",\"\",$AA${p}-TODAY())".format(p=prow)
        cached = ("", "", "")
        if i < len(m.gifts):
            g = m.gifts[i]
            dl = g["deadline"]
            if dl and dl >= _today() and g["status"] != C.ST_DELIVERED:
                cached = (dl, "\U0001F381 %s \u2014 %s" % (g["idea"],
                                                           g["recipient"]),
                          (dl - _today()).days)
        rows.append(((f_date, cached[0]), (f_lab, cached[1]),
                     (f_days, cached[2])))

    if bk.has("todo"):
        td_dl = bk.col("todo", "deadline")
        td_done = bk.col("todo", "done")
        td_task = bk.col("todo", "task")
        for i in range(C.POOL_TODO_ROWS):
            srow = C.ROW_FIRST + i
            prow = C.DATA_POOL_FIRST + C.POOL_GIFT_ROWS + i
            f_date = ("=IF(OR('{t}'!${d}${s}=\"\",'{t}'!${dn}${s}=\"{tick}\","
                      "'{t}'!${d}${s}<TODAY()),\"\",'{t}'!${d}${s})"
                      ).format(t=C.SHEET_NAMES["todo"], d=td_dl, s=srow,
                               dn=td_done, tick=C.TICK)
            f_lab = ("=IF($AA${p}=\"\",\"\",\"\u2705 \"&'{t}'!${c}${s})"
                     ).format(p=prow, t=C.SHEET_NAMES["todo"], c=td_task,
                              s=srow)
            f_days = "=IF($AA${p}=\"\",\"\",$AA${p}-TODAY())".format(p=prow)
            cached = ("", "", "")
            if i < len(m.todos):
                t = m.todos[i]
                dl = t["deadline"]
                if t["done"] != C.TICK and dl and dl >= _today():
                    cached = (dl, "\u2705 %s" % t["task"],
                              (dl - _today()).days)
            rows.append(((f_date, cached[0]), (f_lab, cached[1]),
                         (f_days, cached[2])))

    if bk.has("orders"):
        od_ex = bk.col("orders", "expected")
        od_st = bk.col("orders", "status")
        od_item = bk.col("orders", "item")
        od_store = bk.col("orders", "store")
        for i in range(C.POOL_ORDER_ROWS):
            srow = C.ROW_FIRST + i
            prow = (C.DATA_POOL_FIRST + C.POOL_GIFT_ROWS + C.POOL_TODO_ROWS
                    + i)
            f_date = ("=IF(OR('{o}'!${d}${s}=\"\",'{o}'!${d}${s}<TODAY(),"
                      "'{o}'!${st}${s}=\"{del1}\",'{o}'!${st}${s}=\"{can}\"),"
                      "\"\",'{o}'!${d}${s})").format(
                          o=C.SHEET_NAMES["orders"], d=od_ex, s=srow,
                          st=od_st, del1=C.OS_DELIVERED, can=C.OS_CANCEL)
            f_lab = ("=IF($AA${p}=\"\",\"\",\"\U0001F4E6 \"&'{o}'!${i}${s}&"
                     "\" \u2014 \"&'{o}'!${st}${s})").format(
                         p=prow, o=C.SHEET_NAMES["orders"], i=od_item, s=srow,
                         st=od_store)
            f_days = "=IF($AA${p}=\"\",\"\",$AA${p}-TODAY())".format(p=prow)
            cached = ("", "", "")
            if i < len(m.orders):
                o = m.orders[i]
                ex = o["expected"]
                if ex and ex >= _today() and o["status"] not in (
                        C.OS_DELIVERED, C.OS_CANCEL):
                    cached = (ex,
                              "\U0001F4E6 %s \u2014 %s" % (o["item"],
                                                           o["store"]),
                              (ex - _today()).days)
            rows.append(((f_date, cached[0]), (f_lab, cached[1]),
                         (f_days, cached[2])))
    return rows


def _today():
    from datetime import date
    return date.today()


# ---------------------------------------------------------------------------
# KPI formulas
# ---------------------------------------------------------------------------
def _kpis(bk):
    """Yield (key, formula, number_format) for the whole KPI table."""
    m = bk.demo
    out = []

    def k(name):
        return "$AF$%d" % C.KPI_ROW[name]

    def kfmt(name):
        return C.KPI_FMT[name]

    gt = bk.q("gifts")
    out.append(("days_to_event", "=EventDate-TODAY()", kfmt("days_to_event")))
    out.append(("event_year", "=YEAR(EventDate)", kfmt("event_year")))

    st = bk.rng("gifts", "status")
    idea = bk.rng("gifts", "idea")
    wrap = bk.rng("gifts", "wrapped")
    deliv = bk.rng("gifts", "delivered")

    out.append(("gifts_planned", "=COUNTA(%s)" % idea, kfmt("gifts_planned")))
    bought = "+".join('COUNTIF(%s,"%s")' % (st, s)
                      for s in (C.ST_BOUGHT, C.ST_WRAPPED, C.ST_DELIVERED))
    bought += '+IF(CountOrdered="Yes",COUNTIF(%s,"%s"),0)' % (st, C.ST_ORDERED)
    out.append(("gifts_purchased", "=" + bought, kfmt("gifts_purchased")))
    out.append(("gifts_wrapped",
                '=COUNTIF(%s,"%s")+SUMPRODUCT((%s<>"%s")*((%s="%s")+(%s="%s")>0))'
                % (wrap, C.TICK, wrap, C.TICK, st, C.ST_WRAPPED, st,
                   C.ST_DELIVERED), kfmt("gifts_wrapped")))
    out.append(("gifts_delivered",
                '=COUNTIF(%s,"%s")+SUMPRODUCT((%s<>"%s")*(%s="%s"))'
                % (deliv, C.TICK, deliv, C.TICK, st, C.ST_DELIVERED),
                kfmt("gifts_delivered")))
    out.append(("gifts_to_buy",
                '=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                % (st, C.ST_IDEA, st, C.ST_NEED), kfmt("gifts_to_buy")))
    out.append(("gifts_ordered", '=COUNTIF(%s,"%s")' % (st, C.ST_ORDERED),
                kfmt("gifts_ordered")))
    out.append(("wrap_to_do",
                "=MAX(0,%s-%s)" % (k("gifts_purchased"), k("gifts_wrapped")),
                kfmt("wrap_to_do")))
    out.append(("deliver_to_do",
                "=MAX(0,%s-%s)" % (k("gifts_wrapped"), k("gifts_delivered")),
                kfmt("deliver_to_do")))
    out.append(("gift_completion",
                "=IFERROR(%s/%s,0)" % (k("gifts_purchased"),
                                       k("gifts_planned")),
                kfmt("gift_completion")))
    out.append(("recipients_gifted",
                "=COUNTIF($K$%d:$K$%d,\">0\")"
                % (C.DATA_REC_FIRST, C.DATA_REC_FIRST + C.DATA_REC_ROWS - 1),
                kfmt("recipients_gifted")))
    out.append(("avg_per_recipient",
                "=IFERROR(%s/%s,0)" % (k("gift_actual_spent"),
                                       k("recipients_gifted")),
                kfmt("avg_per_recipient")))
    out.append(("gift_budget_planned", "=SUM(%s)" % bk.rng("gifts", "budget"),
                kfmt("gift_budget_planned")))
    out.append(("gift_actual_spent", "=SUM(%s)" % bk.rng("gifts", "cost"),
                kfmt("gift_actual_spent")))

    bud = bk.q("budget")
    out.append(("budget_planned",
                "=SUM(%s!$%s$%d:$%s$%d)"
                % (bud, C.BUDGET_COLS["planned"], C.BUD_FIRST,
                   C.BUDGET_COLS["planned"], C.BUD_FIRST + C.BUDGET_ROWS - 1),
                kfmt("budget_planned")))
    out.append(("budget_actual",
                "=SUM(%s!$%s$%d:$%s$%d)"
                % (bud, C.BUDGET_COLS["actual"], C.BUD_FIRST,
                   C.BUDGET_COLS["actual"], C.BUD_FIRST + C.BUDGET_ROWS - 1),
                kfmt("budget_actual")))
    out.append(("budget_remaining",
                "=%s-%s" % (k("budget_planned"), k("budget_actual")),
                kfmt("budget_remaining")))
    out.append(("budget_pct",
                "=IFERROR(%s/%s,0)" % (k("budget_actual"), k("budget_planned")),
                kfmt("budget_pct")))

    def simple(key, formula, zero="0"):
        if bk.has(_sheet_for(key)):
            return (key, formula, kfmt(key))
        return (key, "=" + zero, kfmt(key))

    sh = bk.q("shopping")
    out.append(simple("shop_total", "=COUNTA(%s)" % bk.rng("shopping", "item")))
    out.append(simple("shop_bought", '=COUNTIF(%s,"%s")'
                      % (bk.rng("shopping", "bought"), C.TICK)))
    out.append(simple("shop_spent", "=SUM(%s)" % bk.rng("shopping", "spent")))

    out.append(simple("cards_total", "=COUNTA(%s)" % bk.rng("cards", "name")))
    out.append(simple("cards_written", '=COUNTIF(%s,"%s")'
                      % (bk.rng("cards", "written"), C.TICK)))
    out.append(simple("cards_sent", '=COUNTIF(%s,"%s")'
                      % (bk.rng("cards", "sent"), C.TICK)))

    out.append(simple("stock_budget", "=SUM(%s)"
                      % bk.rng("stockings", "budget")))
    out.append(simple("stock_spent", "=SUM(%s)" % bk.rng("stockings", "spent")))
    out.append(simple("stock_items", "=COUNTA(%s)"
                      % bk.rng("stockings", "item")))
    out.append(simple("stock_bought", '=COUNTIF(%s,"%s")'
                      % (bk.rng("stockings", "bought"), C.TICK)))

    ost = bk.rng("orders", "status")
    oex = bk.rng("orders", "expected")
    out.append(simple("orders_total", "=COUNTA(%s)"
                      % bk.rng("orders", "item")))
    out.append(simple("orders_outstanding",
                      '=SUMPRODUCT((%s<>"")*(%s<>"%s")*(%s<>"%s")*(%s<>"%s"))'
                      % (ost, ost, C.OS_DELIVERED, ost, C.OS_CANCEL, ost,
                         C.OS_RETURN)))
    out.append(simple("orders_late",
                      '=SUMPRODUCT((%s<>"")*(%s<TODAY())*(%s<>"%s")*(%s<>"%s"))'
                      % (oex, oex, ost, C.OS_DELIVERED, ost, C.OS_CANCEL)))
    out.append(simple("orders_value", "=SUM(%s)" % bk.rng("orders", "cost")))

    td = bk.rng("todo", "deadline")
    tdn = bk.rng("todo", "done")
    out.append(simple("todo_total", "=COUNTA(%s)" % bk.rng("todo", "task")))
    out.append(simple("todo_done", '=COUNTIF(%s,"%s")' % (tdn, C.TICK)))
    out.append(simple("todo_overdue",
                      '=SUMPRODUCT((%s<>"%s")*(%s<>"")*(%s<TODAY()))'
                      % (tdn, C.TICK, td, td)))

    out.append(simple("wish_total", "=COUNTA(%s)" % bk.rng("wishlist", "idea")))
    out.append(simple("wish_must", '=COUNTIF(%s,"%s")'
                      % (bk.rng("wishlist", "priority"), C.PR_MUST)))
    out.append(simple("wish_value", "=SUM(%s)" % bk.rng("wishlist", "price")))

    return out


_SHEET_FOR = {
    "shop_total": "shopping", "shop_bought": "shopping",
    "shop_spent": "shopping", "cards_total": "cards",
    "cards_written": "cards", "cards_sent": "cards",
    "stock_budget": "stockings", "stock_spent": "stockings",
    "stock_items": "stockings", "stock_bought": "stockings",
    "orders_total": "orders", "orders_outstanding": "orders",
    "orders_late": "orders", "orders_value": "orders",
    "todo_total": "todo", "todo_done": "todo", "todo_overdue": "todo",
    "wish_total": "wishlist", "wish_must": "wishlist",
    "wish_value": "wishlist",
}


def _sheet_for(key):
    return _SHEET_FOR.get(key, "gifts")
