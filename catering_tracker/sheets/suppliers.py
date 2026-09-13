"""
Suppliers: who sells what, at what price, on what terms.

The supplier dropdowns on Inventory and the Shopping List read from column
C here, and the price / minimum-order columns make comparing two quotes a
glance, not a search through WhatsApp.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("supplier", "Supplier", "text", "accent"),
    ("contact", "Contact", "text", None),
    ("phone", "Phone", "text", None),
    ("email", "Email", "text", None),
    ("category", "Category", "center", None),
    ("item", "What they supply", "wrap", None),
    ("price", "From price", "money", "ok"),
    ("min_order", "Min order", "money0", "warn"),
    ("delivery", "Delivery", "center", None),
    ("terms", "Terms", "center", None),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "M"


def build(bk):
    ws = bk.ws("suppliers")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("suppliers")
    bk.title_block("suppliers", "Suppliers",
                   "Who sells what, at what price, on what terms", LAST_COL)
    bk.stats_strip("suppliers", [
        ('="Suppliers: "&COUNTA(%s)' % bk.rng("suppliers", "supplier"),
         "accent", "Suppliers: %d" % len(demo.suppliers)),
        ('="Categories: "&SUMPRODUCT((%s<>"")/COUNTIF(%s,%s&""))'
         % (bk.rng("suppliers", "category"), bk.rng("suppliers", "category"),
            bk.rng("suppliers", "category")), "info", "Categories: %d"
         % len({s["category"] for s in demo.suppliers})),
    ])

    common.table_frame(bk, "suppliers", COLUMNS)
    _rows(bk)

    common.money_dv(bk, "suppliers", ["price", "min_order"])
    ws.data_validation(
        r(C.ROW_FIRST), ci("K"), r(C.last_row("suppliers")), ci("K"),
        {"validate": "list", "source": ["Same day", "Next day", "2 days",
                                        "3 days", "4 days", "5 days",
                                        "Weekly"], "ignore_blank": True,
         "show_input": True, "input_title": "Delivery",
         "input_message": "How fast do they deliver?"})
    bk.stats["validations"] += 1

    # highlight the best (lowest) from-price per... just zebra + bars here
    common.databar(bk, "suppliers", "price", color=th.ok)

    common.note_block(
        bk, "suppliers", C.last_row("suppliers") + 3, 1, ci(LAST_COL) - 1, [
            "Adding a supplier here makes them selectable on the "
            "Inventory and Shopping List tabs.",
            "From price is your reference price for comparisons - the "
            "actual cost per unit lives on the Inventory tab, where the "
            "shopping estimates read it."],
        title="How this tab works")

    bk.nav_row("suppliers", C.last_row("suppliers") + 8, first_col=1,
               span=2, max_col=LAST_COL)
    bk.page("suppliers", LAST_COL, C.last_row("suppliers") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["suppliers"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": ""}
        if demo.demo and i < len(demo.suppliers):
            s = demo.suppliers[i]
            values.update(
                supplier=s["supplier"], contact=s["contact"],
                phone=s["phone"], email=s["email"], category=s["category"],
                item=s["item"], price=s["price"], min_order=s["min_order"],
                delivery=s["delivery"], terms=s["terms"], notes=s["notes"])
            cached["n"] = i + 1
        common.write_row(bk, "suppliers", COLUMNS, rownum, values, cached)
