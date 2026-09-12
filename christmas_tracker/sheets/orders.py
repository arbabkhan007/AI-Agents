"""
\U0001F4E6 Order Tracker - the "will it arrive in time?" tab.

Every online order in one place with its expected date, tracking link, the
number of days you have left and an alert that turns red the moment a parcel
is late.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "orders"
LAST_COL = "R"

COLUMNS = [
    ("n", "#", "idx", None),
    ("recipient", "Recipient", "text", None),
    ("item", "Gift / item", "text", None),
    ("store", "Store", "text", None),
    ("order_no", "Order number", "text", None),
    ("order_date", "Ordered on", "date", None),
    ("expected", "Expected", "date", None),
    ("actual", "Arrived", "date", None),
    ("link", "Tracking link", "link", None),
    ("open", "\U0001F517", "calc_c", "gold"),
    ("status", "Order status", "center", None),
    ("days", "Days left", "calc_num", "primary_2"),
    ("alert", "Alert", "calc_c", "primary_2"),
    ("return_by", "Return by", "date", None),
    ("returned", "Returned", "tick", None),
    ("cost", "Cost", "money", None),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F4E6  Online Order Tracker",
        "  Parcels, couriers and cut-off dates \u2014 nothing arrives on "
        "the 27th on your watch.",
        LAST_COL)

    chips = [
        ("B", "D", "\U0001F4E6 Orders: ", "orders_total", "primary", "n"),
        ("E", "G", "\U0001F69A Still coming: ", "orders_outstanding", "info",
         "n"),
        ("H", "I", "\u2705 Arrived: ", None, "ok", "n"),
        ("J", "L", "\U0001F534 Running late: ", "orders_late", "bad", "n"),
        ("M", "N", "\U0001F4B5 Value: ", "orders_value", "accent", "$"),
        ("O", LAST_COL, "\U0001F504 Returns open: ", None, "warn", "n"),
    ]
    for c1, c2, label, kpi_key, color, kind in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2), "", fmt)
        if kpi_key is None and label.startswith("\u2705"):
            formula = '="%s"&COUNTIF(%s,"%s")' % (label,
                                                  bk.rng(KEY, "status"),
                                                  C.OS_DELIVERED)
            cached = "%s%d" % (label, len([x for x in m.orders
                                           if x["status"] == C.OS_DELIVERED]))
        elif kpi_key is None:
            formula = '="%s"&COUNTIF(%s,"%s")' % (label,
                                                  bk.rng(KEY, "returned"),
                                                  C.TICK)
            cached = "%s%d" % (label, len([x for x in m.orders
                                           if x["returned"] == C.TICK]))
        elif kind == "$":
            formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label,
                                                           bk.kpi(kpi_key))
            cached = "%s%s" % (label, m.money(m.agg[kpi_key]))
        else:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = _formulas(bk, rownum)
        if i < len(m.orders):
            o = m.orders[i]
            values.update({k: o[k] for k in
                           ("recipient", "item", "store", "order_no",
                            "order_date", "expected", "actual", "link",
                            "status", "return_by", "returned", "cost",
                            "notes")})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    K.list_dv(bk, KEY, "recipient", "recipients", title="Who is it for?")
    K.list_dv(bk, KEY, "store", "stores", title="Store")
    K.fixed_dv(bk, KEY, "status", "OrderStatuses", title="Order status",
               message="\U0001F6D2 Ordered \u2192 \U0001F4E6 Shipped \u2192 "
                       "\U0001F69A Out for delivery \u2192 \u2705 Delivered "
                       "(or \u21A9\uFE0F Return requested / \u274C "
                       "Cancelled).")
    K.tick_dv(bk, KEY, ["returned"],
               message="Tick \u2713 once the parcel is back with the seller.")
    K.date_dv(bk, KEY, ["order_date", "expected", "actual", "return_by"])
    K.money_dv(bk, KEY, ["cost"])

    n = C.ROW_FIRST
    st = bk.col(KEY, "status")
    K.status_cf(bk, KEY, "status", {
        C.OS_ORDERED: (th.plum_soft, th.plum),
        C.OS_SHIPPED: (th.info_soft, th.info),
        C.OS_OUT: (th.warn_soft, th.warn),
        C.OS_DELIVERED: (th.ok_soft, th.ok),
        C.OS_RETURN: (th.gold_soft, th.gold),
        C.OS_CANCEL: (th.bad_soft, th.bad),
    })
    K.tick_cf(bk, KEY, ["returned"])
    K.deadline_cf(bk, KEY, "expected")
    alert = bk.col(KEY, "alert")
    for text, (bg, fg) in (("\u2705 Arrived", (th.ok_soft, th.ok)),
                           ("\U0001F534 Late", (th.bad_soft, th.bad)),
                           ("\U0001F7E1 Arriving soon", (th.warn_soft,
                                                         th.warn)),
                           ("\U0001F535 On the way", (th.info_soft, th.info)),
                           ("\u274C Cancelled", (th.alt, th.muted)),
                           ("\u21A9\uFE0F Returning", (th.gold_soft, th.gold))):
        bk.cond(KEY, n, ci(alert), C.last_row(KEY), ci(alert), {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (alert, n, text),
            "format": S.cf(bg=bg, fg=fg, bold=True)})
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=$%s%d="%s"' % (st, n, C.OS_DELIVERED),
        "format": S.cf(bg=th.ok_soft, fg=th.primary)})

    total_row = C.last_row(KEY) + 2
    K.totals_row(
        bk, KEY, total_row,
        {"cost": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "cost"), C.ROW_FIRST,
                                           bk.col(KEY, "cost"),
                                           C.last_row(KEY)),
                  "#,##0.00", m.agg["orders_value"]),
         "expected": ('=COUNTIF($%s$%d:$%s$%d,"%s")&" of "&COUNTA($%s$%d:'
                      '$%s$%d)&" arrived"'
                      % (st, C.ROW_FIRST, st, C.last_row(KEY), C.OS_DELIVERED,
                         bk.col(KEY, "item"), C.ROW_FIRST, bk.col(KEY, "item"),
                         C.last_row(KEY)), "@",
                      "%d of %d arrived" % (
                          len([x for x in m.orders
                               if x["status"] == C.OS_DELIVERED]),
                          m.agg["orders_total"]))},
        label="  TOTALS", label_span=("B", "F"), last_col=LAST_COL)

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  \u201CDays left\u201D counts down to the expected delivery "
         "date; the alert turns \U0001F534 red the day after it was due.",
         "\u2022  Paste the courier link in \u201CTracking link\u201D and the "
         "\U0001F517 button opens it in one click.",
         "\u2022  Keep an eye on the \u201CReturn by\u201D column \u2014 "
         "January returns sneak up fast.",
         "\u2022  Order money is NOT added to the budget twice: the gift "
         "itself is counted on the \U0001F381 Gift Tracker. This tab is for "
         "logistics."],
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


def _formulas(bk, n):
    def L(f):
        return bk.col(KEY, f)

    return {
        "n": '=IF($%s%d="","",ROW()-%d)' % (L("item"), n, C.ROW_FIRST - 1),
        "open": '=IF($%s%d="","",HYPERLINK($%s%d,"\U0001F517"))'
                % (L("link"), n, L("link"), n),
        "days": '=IF($%s%d="","",$%s%d-TODAY())' % (L("expected"), n,
                                                    L("expected"), n),
        "alert": ('=IF($%s%d="","",IF($%s%d="%s","\u2705 Arrived",'
                 'IF($%s%d="%s","\u274C Cancelled",IF($%s%d="%s",'
                 '"\u21A9\uFE0F Returning",IF($%s%d="","\u2014",'
                 'IF($%s%d<TODAY(),"\U0001F534 Late",'
                 'IF($%s%d-TODAY()<=DueSoonDays,"\U0001F7E1 Arriving soon",'
                 '"\U0001F535 On the way")))))))'
                 % (L("item"), n, L("status"), n, C.OS_DELIVERED,
                    L("status"), n, C.OS_CANCEL, L("status"), n, C.OS_RETURN,
                    L("expected"), n, L("expected"), n, L("expected"), n)),
    }


def _cached(m, i):
    from datetime import date
    today = date.today()
    if i >= len(m.orders):
        return {"n": "", "open": "", "days": "", "alert": ""}
    o = m.orders[i]
    ex = o["expected"]
    if o["status"] == C.OS_DELIVERED:
        alert = "\u2705 Arrived"
    elif o["status"] == C.OS_CANCEL:
        alert = "\u274C Cancelled"
    elif o["status"] == C.OS_RETURN:
        alert = "\u21A9\uFE0F Returning"
    elif not ex:
        alert = "\u2014"
    elif ex < today:
        alert = "\U0001F534 Late"
    elif (ex - today).days <= m.settings["duesoon"]:
        alert = "\U0001F7E1 Arriving soon"
    else:
        alert = "\U0001F535 On the way"
    return {"n": i + 1, "open": "\U0001F517" if o["link"] else "",
            "days": (ex - today).days if ex else "", "alert": alert}
