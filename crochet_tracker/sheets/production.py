"""
Made & Stocked - production batches.

Log each making session; the sheet keeps a running per-batch stock count
(made + returns - sold - damaged) and what's still free to sell (current -
reserved). The Product Catalog reads 'current' live, so stock is never
double-counted across batches.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "L"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("product", "Product", "text", None),
    ("date", "Date made", "date", None),
    ("made", "Made", "qty", None),
    ("reserved", "Reserved", "qty", None),
    ("taken", "Taken to fair", "qty", None),
    ("sold", "Sold", "qty", None),
    ("returned", "Returned", "qty", None),
    ("damaged", "Damaged / gifted", "qty", None),
    ("current", "In stock now", "calc_qty", None),
    ("available", "Free to sell", "calc_qty", None),
    ("notes", "Notes", "text", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("production")
    demo = bk.demo

    common.sheet_head(bk, "production", LAST_COL,
                      "\U0001F4E6  Made & Stocked",
                      "Log what you make - stock counts itself, batch by "
                      "batch")

    made_total = sum(b["made"] for b in demo.production) if demo else 0
    sold_total = sum(b["sold"] for b in demo.production) if demo else 0
    stock_total = sum(b["current"] for b in demo.production) if demo else 0
    common.chips(bk, "production", [
        ('="Batches: "&TEXT(COUNTA(%s),"0")'
         % bk.rng("production", "product"), "ok",
         "Batches: %d" % (len(demo.production) if demo else 0), 3),
        ('="Made this year: "&TEXT(SUM(%s),"#,##0")'
         % bk.rng("production", "made"), "gold",
         "Made this year: %d" % made_total, 3),
        ('="Sold: "&TEXT(SUM(%s),"#,##0")' % bk.rng("production", "sold"),
         "accent", "Sold: %d" % sold_total, 3),
        ('="On the shelf: "&TEXT(SUM(%s),"#,##0")'
         % bk.rng("production", "current"), "info",
         "On the shelf: %d" % stock_total, 3),
    ])

    common.table_frame(bk, "production", _COLUMNS, height=22)

    for i in range(common.n_rows("production")):
        rownum = common.first_row() + i
        b = demo.production[i] if demo and i < len(demo.production) else None
        values, cached = _row_values(bk, rownum, b)
        common.write_row(bk, "production", _COLUMNS, rownum, values, cached)

    trow = common.last_row("production") + 2
    common.totals_row(bk, "production", trow, {
        "made": ('=SUM(%s)' % bk.rng("production", "made"), "#,##0",
                 made_total),
        "taken": ('=SUM(%s)' % bk.rng("production", "taken"), "#,##0",
                  sum(b["taken"] for b in demo.production) if demo else 0),
        "sold": ('=SUM(%s)' % bk.rng("production", "sold"), "#,##0",
                 sold_total),
        "current": ('=SUM(%s)' % bk.rng("production", "current"), "#,##0",
                    stock_total),
    }, first_col="B", label="TOTALS", label_span=("C", "E"))

    common.list_dv(bk, "production", "product", "products",
                   title="Product",
                   message="Pick a product from your catalog.")
    common.date_dv(bk, "production", ["date"])
    common.whole_dv(bk, "production",
                    ["made", "reserved", "taken", "sold", "returned",
                     "damaged"], 0, 9999)

    L = bk.col("production", "available")
    col = ci(L)
    bk.cond("production", C.ROW_FIRST, col, C.last_row("production"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<0)' % (bk.col("production",
                                                        "product"),
                                                 C.ROW_FIRST, L,
                                                 C.ROW_FIRST),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    common.databar(bk, "production", "current", color=th.ok)

    nrow = trow + 2
    common.note_block(
        bk, "production", nrow, 1, ci(LAST_COL), [
            "In stock now = made + returned - sold - damaged. Free to sell "
            "also removes items you've reserved (custom orders, prizes).",
            "The same product can span several batches - the Product "
            "Catalog adds them all up automatically.",
            "Negative 'Free to sell' glows red: you've promised more than "
            "you made.",
        ], title="  How this tab works")

    common.footer_nav(bk, "production", nrow + 5, LAST_COL, zoom=85)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, b):
    col = bk.col
    pr = "production"
    values = dict.fromkeys([c[0] for c in _COLUMNS], None)
    values["current"] = ('=IF(${p}{row}="","",N(${m}{row})+N(${rt}{row})'
                         '-N(${s}{row})-N(${d}{row}))'
                         .format(p=col(pr, "product"), row=rownum,
                                 m=col(pr, "made"), rt=col(pr, "returned"),
                                 s=col(pr, "sold"), d=col(pr, "damaged")))
    values["available"] = ('=IF(${p}{row}="","",${c}{row}-N(${r}{row}))'
                           .format(p=col(pr, "product"), row=rownum,
                                   c=col(pr, "current"),
                                   r=col(pr, "reserved")))
    cached = dict.fromkeys(values.keys(), 0)
    if b:
        values.update(product=b["product"], date=b["date"], made=b["made"],
                      reserved=b["reserved"], taken=b["taken"],
                      sold=b["sold"], returned=b["returned"],
                      damaged=b["damaged"], notes=b["notes"])
        cached.update(current=b["current"], available=b["available"])
    return values, cached
