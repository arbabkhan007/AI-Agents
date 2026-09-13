"""
Inventory: what's on the shelves, and what needs reordering.

Quantity, minimum level and unit cost in; stock value and the
Reorder / Low / OK chip calculate themselves.  The Shopping List reads
quantities straight from here, so "available" is never a guess.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("ingredient", "Ingredient", "text", "accent"),
    ("category", "Category", "center", None),
    ("unit", "Unit", "center", None),
    ("qty", "In stock", "qty1", None),
    ("min", "Min level", "qty1", "warn"),
    ("unit_cost", "Unit cost", "money", None),
    ("value", "Stock value", "calc_money", None),
    ("supplier", "Supplier", "text", None),
    ("status", "Status", "calc_c", None),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "L"

ST_REORDER = "\U0001F534 Reorder"
ST_LOW = "\U0001F7E1 Low"
ST_OK = "\U0001F7E2 OK"


def build(bk):
    ws = bk.ws("inventory")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("inventory")
    bk.title_block("inventory", "Inventory",
                   "Know what's on the shelf - and what to reorder this "
                   "week", LAST_COL)
    bk.stats_strip("inventory", [
        ('="Items tracked: "&COUNTA(%s)' % bk.rng("inventory", "ingredient"),
         "accent", "Items tracked: %d" % len(demo.inventory)),
        ('="Stock value: "&Currency&TEXT(SUMPRODUCT((%s<>"")*%s*%s),'
         '"#,##0.00")'
         % (bk.rng("inventory", "ingredient"), bk.rng("inventory", "qty"),
            bk.rng("inventory", "unit_cost")), "ok",
         "Stock value: %s" % demo.money(bk.cached("inv_value", 0), 2)),
        ('="Below minimum: "&%s' % bk.kpi("low_stock"), "bad",
         "Below minimum: %d" % bk.cached("low_stock", 0)),
        ('="Reorder spend: "&Currency&TEXT(SUMPRODUCT((%s<>"")*(%s<%s)*'
         '(%s-%s)*%s),"#,##0.00")'
         % (bk.rng("inventory", "ingredient"), bk.rng("inventory", "qty"),
            bk.rng("inventory", "min"), bk.rng("inventory", "min"),
            bk.rng("inventory", "qty"), bk.rng("inventory", "unit_cost")),
         "gold",
         "Reorder spend: %s" % demo.money(
             sum(max(0, i["min"] - i["qty"]) * i["unit_cost"]
                 for i in demo.inventory), 2)),
    ])

    common.table_frame(bk, "inventory", COLUMNS)
    _rows(bk)

    common.list_dv(bk, "inventory", "category", "ingredient_categories",
                   title="Category",
                   message="Produce, Meat & Fish... (edit on Setup).")
    ws.data_validation(
        r(C.ROW_FIRST), ci("J"), r(C.last_row("inventory")), ci("J"),
        {"validate": "list", "source": "=SuppliersList",
         "ignore_blank": True, "show_input": True, "input_title":
         "Supplier", "input_message": "Pick from the Suppliers tab "
         "(or type a new one and add it there)."})
    bk.stats["validations"] += 1
    common.money_dv(bk, "inventory", ["unit_cost"])

    common.status_cf(bk, "inventory", "status", {
        ST_REORDER: (th.bad_soft, th.bad),
        ST_LOW: (th.warn_soft, th.warn),
        ST_OK: (th.ok_soft, th.ok),
    })
    common.databar(bk, "inventory", "qty", color=th.ok)

    common.totals_row(bk, "inventory", C.last_row("inventory") + 1, {
        "value": ('=SUMPRODUCT((%s<>"")*%s*%s)'
                  % (bk.rng("inventory", "ingredient"),
                     bk.rng("inventory", "qty"),
                     bk.rng("inventory", "unit_cost")),
                  "money", bk.cached("inv_value", 0)),
    }, first_col="B", last_col=LAST_COL, label="TOTAL STOCK VALUE",
        label_span=("B", "G"))

    common.note_block(
        bk, "inventory", C.last_row("inventory") + 3, 1, ci(LAST_COL) - 1, [
            "Status is automatic: below your minimum it turns red "
            "(Reorder), under 1.5x the minimum it glows amber (Low), "
            "otherwise green (OK).",
            "The Shopping List checks these quantities before telling you "
            "what to buy - keep them honest after every shop."],
        title="How this tab works")

    bk.nav_row("inventory", C.last_row("inventory") + 8, first_col=1,
               span=2, max_col=LAST_COL)
    bk.page("inventory", LAST_COL, C.last_row("inventory") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "value": '=IF(OR($F%d="",$H%d=""),"",ROUND($F%d*$H%d,2))'
                 % (rownum, rownum, rownum, rownum),
        "status": ('=IF($C%d="","",IF($F%d<$G%d,"%s",'
                   'IF($F%d<$G%d*1.5,"%s","%s")))'
                   % (rownum, rownum, rownum, ST_REORDER,
                      rownum, rownum, ST_LOW, ST_OK)),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["inventory"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "value": "", "status": ""}
        if demo.demo and i < len(demo.inventory):
            it = demo.inventory[i]
            values.update(
                ingredient=it["ingredient"], category=it["category"],
                unit=it["unit"], qty=it["qty"], min=it["min"],
                unit_cost=it["unit_cost"], supplier=it["supplier"],
                notes=it["notes"])
            cached.update(n=i + 1, value=it["value"], status=it["status"])
        common.write_row(bk, "inventory", COLUMNS, rownum, values, cached)
