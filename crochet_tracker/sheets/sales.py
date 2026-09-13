"""
Sales Log - one row per line item sold (at a fair or online).

Pick the fair and product from the dropdowns, type qty and price; the row
total and its cost of goods calculate themselves and roll up into the
Craft Fairs tab, the Dashboard and the Monthly Summary.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "M"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("date", "Date", "date", None),
    ("event", "Craft fair / channel", "text", None),
    ("product", "Product", "text", None),
    ("qty", "Qty", "qty", None),
    ("unit", "Unit price", "money", None),
    ("discount", "Discount", "money", None),
    ("total", "Line total", "calc_money", None),
    ("method", "Payment", "text", None),
    ("ref", "Receipt / ref", "text", None),
    ("notes", "Notes", "text", None),
    ("pair", "Gift wrap \u2713", "tick", None),
    ("cost", "Cost of goods", "calc_money", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("sales")
    demo = bk.demo

    common.sheet_head(bk, "sales", LAST_COL, "\U0001F4B0  Sales Log",
                      "Log every sale - totals, costs and dashboards update "
                      "live")

    sls = demo.sales if demo else []
    cur = demo.settings["currency"] if demo else "$"
    common.chips(bk, "sales", [
        ('="Entries: "&TEXT(COUNTA(%s),"0")' % bk.rng("sales", "date"),
         "ok", "Entries: %d" % len(sls), 3),
        ('="Units: "&TEXT(SUM(%s),"#,##0")' % bk.rng("sales", "qty"),
         "gold", "Units: %d" % sum(s["qty"] for s in sls), 3),
        ('="Gross: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("sales", "total"), "accent",
         "Gross: %s%s" % (cur, format(sum(s["qty"] * s["unit"]
                                          - s["discount"]
                                          for s in sls), ",.2f")), 3),
        ('="Avg sale: "&Currency&TEXT(%s,"#,##0.00")' % bk.kpi("aov"), "info",
         "Avg sale: %s%s" % (cur, format(demo.agg["aov"] if demo else 0,
                                         ",.2f")), 3),
    ])

    common.table_frame(bk, "sales", _COLUMNS, height=20)

    for i in range(common.n_rows("sales")):
        rownum = common.first_row() + i
        s = sls[i] if i < len(sls) else None
        values, cached = _row_values(bk, rownum, s)
        common.write_row(bk, "sales", _COLUMNS, rownum, values, cached)

    trow = common.last_row("sales") + 2
    common.totals_row(bk, "sales", trow, {
        "qty": ('=SUM(%s)' % bk.rng("sales", "qty"), "#,##0",
                sum(s["qty"] for s in sls)),
        "discount": ('=SUM(%s)' % bk.rng("sales", "discount"), "#,##0.00",
                     round(sum(s["discount"] for s in sls), 2)),
        "total": ('=SUM(%s)' % bk.rng("sales", "total"), "#,##0.00",
                  round(sum(s["qty"] * s["unit"] - s["discount"]
                            for s in sls), 2)),
        "cost": ('=SUM(%s)' % bk.rng("sales", "cost"), "#,##0.00",
                 round(demo.agg["cogs"], 2) if demo else 0),
    }, first_col="B", label="TOTALS", label_span=("C", "D"))

    common.list_dv(bk, "sales", "event", "events", title="Where?",
                   message="Pick the fair or channel from your Craft Fairs "
                           "tab.")
    common.list_dv(bk, "sales", "product", "products", title="Product",
                   message="Pick a product from your catalog.")
    common.list_dv(bk, "sales", "method", "payments", title="Payment",
                   message="How did they pay?")
    common.tick_dv(bk, "sales", ["pair"])
    common.date_dv(bk, "sales", ["date"])
    common.whole_dv(bk, "sales", ["qty"], 0, 999)
    common.money_dv(bk, "sales", ["unit", "discount"])

    # discounted rows glow amber
    L = bk.col("sales", "discount")
    col = ci(L)
    bk.cond("sales", C.ROW_FIRST, col, C.last_row("sales"), col, {
        "type": "cell", "criteria": ">", "value": 0,
        "format": bk.S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    common.tick_cf(bk, "sales", ["pair"])
    common.databar(bk, "sales", "total", color=th.ok)

    nrow = trow + 2
    common.note_block(
        bk, "sales", nrow, 1, ci(LAST_COL), [
            "Line total = qty x unit price - discount. Cost of goods uses "
            "each product's cost from the Product Catalog.",
            "One row per product per sale - if someone buys two different "
            "things, that's two happy rows.",
            "Discounts glow amber so you can see how generous you've been "
            "this season.",
        ], title="  How this tab works")

    common.footer_nav(bk, "sales", nrow + 5, LAST_COL, zoom=85)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, s):
    col = bk.col
    sa = "sales"
    values = dict.fromkeys([c[0] for c in _COLUMNS], None)
    values["total"] = ('=IF(OR(${p}{row}="",${q}{row}=""),"",ROUND(${q}{row}'
                       '*N(${u}{row})-N(${d}{row}),2))'
                       .format(p=col(sa, "product"), row=rownum,
                               q=col(sa, "qty"), u=col(sa, "unit"),
                               d=col(sa, "discount")))
    values["cost"] = ('=IF(${p}{row}="","",ROUND(N(${q}{row})*IFERROR('
                      'VLOOKUP(${p}{row},{lookup},7,0),0),2))'
                      .format(p=col(sa, "product"), row=rownum,
                              q=col(sa, "qty"),
                              lookup="'%s'!$%s$%d:$%s$%d"
                                     % (bk.name("catalog"),
                                        bk.col("catalog", "name"),
                                        C.ROW_FIRST,
                                        bk.col("catalog", "unit_cost"),
                                        C.last_row("catalog"))))
    cached = dict.fromkeys(values.keys(), 0)
    if s:
        uc = _unit_cost(bk, s["product"])
        values.update(date=s["date"], event=s["event"], product=s["product"],
                      qty=s["qty"], unit=s["unit"], discount=s["discount"],
                      method=s["method"], ref=s["ref"], notes=s["notes"])
        cached.update(total=round(s["qty"] * s["unit"] - s["discount"], 2),
                      cost=round(s["qty"] * uc, 2))
    return values, cached


def _unit_cost(bk, product):
    for p in bk.demo.products:
        if p["name"] == product:
            return p["unit_cost"]
    return 0.0
