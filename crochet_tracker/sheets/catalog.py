"""
Product Catalog - one row per thing you make.

Price and costs are yours to type; cost per item, profit, margin, stock
(premium: pulled live from Made & Stocked) and the status pill calculate
themselves.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "P"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("sku", "SKU / code", "text", None),
    ("name", "Product", "text", None),
    ("category", "Category", "text", None),
    ("desc", "Description", "wrap", None),
    ("price", "Price", "money", None),
    ("yarn_cost", "Yarn cost", "money", None),
    ("pack_cost", "Packaging", "money", None),
    ("unit_cost", "Cost / item", "calc_money", None),
    ("profit", "Profit / item", "calc_money", None),
    ("margin", "Margin", "calc_pct1", None),
    ("time_h", "Hours to make", "qty1", None),
    ("stock", "In stock", "calc_qty", None),
    ("min", "Keep min.", "qty", None),
    ("status", "Stock status", "calc_c", None),
    ("link", "Photo / link", "text", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("catalog")
    demo = bk.demo
    premium = bk.has("production")

    common.sheet_head(bk, "catalog", LAST_COL, "\U0001F9F6  Product Catalog",
                      "One row for everything you make - prices, costs and "
                      "stock at a glance")

    common.chips(bk, "catalog", [
        ('="Products: "&TEXT(COUNTA(%s),"0")' % bk.rng("catalog", "name"),
         "primary", (len(demo.products) if demo else 0), 3),
        ('="Avg price: "&Currency&TEXT(IFERROR(AVERAGE(%s),0),"#,##0.00")'
         % bk.rng("catalog", "price"), "accent",
         _avg_price(demo), 3),
        ('="Stock value: "&Currency&TEXT(%s,"#,##0.00")' % bk.kpi("inv_value"),
         "info", _money(demo, "inv_value"), 3),
        ('=IF(%s>0,"! "&TEXT(%s,"0")&" products low on stock","Stock levels OK")'
         % (bk.kpi("low_products"), bk.kpi("low_products")), "warn",
         _low_chip(demo), 3),
    ])

    common.table_frame(bk, "catalog", _COLUMNS, height=22)

    for i in range(common.n_rows("catalog")):
        rownum = common.first_row() + i
        p = demo.products[i] if demo and i < len(demo.products) else None
        values, cached = _row_values(bk, rownum, p, premium)
        common.write_row(bk, "catalog", _COLUMNS, rownum, values, cached)

    # totals
    trow = common.last_row("catalog") + 2
    common.totals_row(bk, "catalog", trow, {
        "name": ('=COUNTA(%s)' % bk.rng("catalog", "name"), "0",
                 len(demo.products) if demo else 0),
        "price": ('=IFERROR(AVERAGE(%s),0)' % bk.rng("catalog", "price"),
                  "#,##0.00", _avg_price(demo)),
        "unit_cost": ('=IFERROR(AVERAGE(%s),0)'
                      % bk.rng("catalog", "unit_cost"), "#,##0.00",
                      _avg(demo, "unit_cost")),
        "profit": ('=IFERROR(AVERAGE(%s),0)' % bk.rng("catalog", "profit"),
                   "#,##0.00", _avg(demo, "profit")),
        "stock": ('=SUM(%s)' % bk.rng("catalog", "stock"), "#,##0",
                  sum(p["stock"] for p in demo.products) if demo else 0),
    }, first_col="B", label="TOTALS / AVERAGES", label_span=("C", "E"))

    # validations
    common.list_dv(bk, "catalog", "category", "categories",
                   title="Category", message="Pick a category - you can edit "
                   "the list on the Lists & Settings tab.")
    common.money_dv(bk, "catalog", ["price", "yarn_cost", "pack_cost"])
    common.whole_dv(bk, "catalog", ["min"], 0, 9999)
    if not premium:
        common.whole_dv(bk, "catalog", ["stock"], 0, 9999)
    bk.ws("catalog").data_validation(
        r(C.ROW_FIRST), ci(bk.col("catalog", "time_h")),
        r(C.last_row("catalog")), ci(bk.col("catalog", "time_h")),
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 1000, "ignore_blank": True, "show_error": True,
         "error_title": "Hours", "error_message": "Enter hours as a number, "
         "e.g. 1.5.", "error_type": "warning"})
    bk.stats["validations"] += 1

    # conditional formats
    L = bk.col("catalog", "status")
    common.status_cf(bk, "catalog", "status", {
        C.ST_OUT: (th.bad_soft, th.bad),
        C.ST_LOW: (th.warn_soft, th.warn),
        C.ST_OK: (th.ok_soft, th.ok),
    })
    common.databar(bk, "catalog", "margin", color=th.primary_2)

    # notes + footer
    nrow = trow + 2
    common.note_block(
        bk, "catalog", nrow, 1, ci(LAST_COL), [
            "Cost / item = yarn + packaging. Profit and margin follow your "
            "price automatically.",
            ("In stock is live from the Made & Stocked tab - every batch you "
             "log updates it instantly."
             if premium else
             "Type your stock count in the In stock column; the status pill "
             "turns it into a to-do list."),
            "Keep min. is your reorder trigger - dip below it and the item "
            "appears on the Reorder List tab.",
        ], title="  How this tab works")

    common.footer_nav(bk, "catalog", nrow + 5, LAST_COL, zoom=85)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, p, premium):
    col = bk.col
    cat = "catalog"
    fx = {}
    fx["unit_cost"] = ('=IF(${name}{row}="","",ROUND(N(${yc}{row})+N(${pc}'
                       '{row}),2))'
                       .format(name=col(cat, "name"), row=rownum,
                               yc=col(cat, "yarn_cost"),
                               pc=col(cat, "pack_cost")))
    fx["profit"] = ('=IF(OR(${name}{row}="",${pr}{row}=""),"",ROUND(${pr}'
                    '{row}-${uc}{row},2))'
                    .format(name=col(cat, "name"), row=rownum,
                            pr=col(cat, "price"), uc=col(cat, "unit_cost")))
    fx["margin"] = ('=IF(OR(${name}{row}="",${pr}{row}=""),"",IFERROR(${pf}'
                    '{row}/${pr}{row},0))'
                    .format(name=col(cat, "name"), row=rownum,
                            pr=col(cat, "price"), pf=col(cat, "profit")))
    if premium:
        fx["stock"] = ('=IF(${name}{row}="",0,SUMIFS({cur},{prod},${name}'
                       '{row}))'
                       .format(name=col(cat, "name"), row=rownum,
                               cur=bk.rng("production", "current"),
                               prod=bk.rng("production", "product")))
    else:
        fx["stock"] = None
    fx["status"] = ('=IF(${name}{row}="","",IF(N(${st}{row})<=0,"{o}",'
                    'IF(N(${st}{row})<${mn}{row},"{l}","{k}")))'
                    .format(name=col(cat, "name"), row=rownum,
                            st=col(cat, "stock"), mn=col(cat, "min"),
                            o=C.ST_OUT, l=C.ST_LOW, k=C.ST_OK))
    values = dict.fromkeys([c[0] for c in _COLUMNS], None)
    values.update(fx)
    cached = dict.fromkeys(values.keys(), 0)
    if p:
        values.update(sku=p["sku"], name=p["name"], category=p["category"],
                      desc=p["desc"], price=p["price"],
                      yarn_cost=p["yarn"], pack_cost=p["pack"],
                      time_h=p["hours"], min=p["min"], link=p["link"])
        cached.update(unit_cost=p["unit_cost"], profit=p["profit"],
                      margin=p["margin"], stock=p["stock"],
                      status=_STATUS_LABEL[p["status"]])
    if not premium:
        values["stock"] = p["stock"] if p else None
        cached["stock"] = 0
    return values, cached


def _avg_price(demo):
    if not demo:
        return 0
    return round(sum(p["price"] for p in demo.products) / len(demo.products),
                 2)


def _avg(demo, field):
    if not demo:
        return 0
    return round(sum(p[field] for p in demo.products) / len(demo.products),
                 2)


def _money(demo, key):
    if not demo:
        return "$0.00"
    return "%s%s" % (demo.settings["currency"],
                     format(demo.agg[key], ",.2f"))


def _low_chip(demo):
    if not demo:
        return "Stock levels OK"
    n = demo.agg["low_products"]
    return "! %d products low on stock" % n if n else "Stock levels OK"


_STATUS_LABEL = {"out": C.ST_OUT, "low": C.ST_LOW, "ok": C.ST_OK}
