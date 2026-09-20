"""
The Shopping List: what to buy, for which event, minus what you already
have.

Pick the event and ingredient, type how much you need - the list works out
what's already in Inventory, what's left to buy, and what it will cost at
your last-paid unit prices.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("event", "Event", "center", None),
    ("ingredient", "Ingredient", "text", "accent"),
    ("required", "Needed", "qty1", None),
    ("available", "In stock", "calc_qty1", None),
    ("to_buy", "To buy", "calc_qty1", None),
    ("supplier", "Supplier", "text", None),
    ("est_cost", "Est. cost", "calc_money", None),
    ("purchased", "Bought", "tick", "ok"),
    ("date", "Bought on", "date", None),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "L"


def build(bk):
    ws = bk.ws("shopping")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("shopping")
    bk.title_block("shopping", "Shopping List",
                   "Buy exactly what each event needs - nothing more, "
                   "nothing less", LAST_COL)
    bk.stats_strip("shopping", [
        ('="Lines to buy: "&%s' % bk.kpi("shop_lines"), "accent",
         "Lines to buy: %d" % bk.cached("shop_lines", 0)),
        ('="Estimated cost: "&Currency&TEXT(%s,"#,##0.00")'
         % bk.kpi("shop_cost"), "gold",
         "Estimated cost: %s" % demo.money(bk.cached("shop_cost", 0), 2)),
        ('="Bought: "&COUNTIF(%s,"%s")&" of "&COUNTA(%s)'
         % (bk.rng("shopping", "purchased"), C.TICK,
            bk.rng("shopping", "ingredient")), "ok",
         "Bought: %d of %d" % (sum(1 for s in demo.shopping
                                    if s["purchased"] == C.TICK),
                               len(demo.shopping))),
    ])

    common.table_frame(bk, "shopping", COLUMNS)
    _rows(bk)

    # validations
    ws.data_validation(
        r(C.ROW_FIRST), ci("C"), r(C.last_row("shopping")), ci("C"),
        {"validate": "list", "source": "=EventList", "ignore_blank": True,
         "show_input": True, "input_title": "Event",
         "input_message": "Pick the event this purchase is for."})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(C.ROW_FIRST), ci("H"), r(C.last_row("shopping")), ci("H"),
        {"validate": "list", "source": "=SuppliersList", "ignore_blank":
         True, "show_input": True, "input_title": "Supplier",
         "input_message": "Pick from the Suppliers tab."})
    bk.stats["validations"] += 1
    common.tick_dv(bk, "shopping", ["purchased"])
    common.date_dv(bk, "shopping", ["date"])

    # conditional formats
    common.tick_cf(bk, "shopping", ["purchased"])
    L = bk.col("shopping", "to_buy")
    col = ci(L)
    bk.cond("shopping", C.ROW_FIRST, col, C.last_row("shopping"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d>0,$%s%d<>"%s")'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST,
                       bk.col("shopping", "purchased"), C.ROW_FIRST,
                       C.TICK),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    L2 = bk.col("shopping", "est_cost")
    common.databar(bk, "shopping", "est_cost", color=th.gold)

    common.totals_row(bk, "shopping", C.last_row("shopping") + 1, {
        # comma form + --: the est-cost column holds "" formulas on empty
        # rows; the * form turns those into #VALUE! in Excel.
        "est_cost": ('=SUMPRODUCT(--((%s<>"%s")*(%s<>"")),%s)'
                     % (bk.rng("shopping", "purchased"), C.TICK,
                        bk.rng("shopping", "ingredient"),
                        bk.rng("shopping", "est_cost")),
                     "money", bk.cached("shop_cost", 0)),
    }, first_col="B", last_col=LAST_COL, label="STILL TO BUY",
        label_span=("B", "G"))

    common.note_block(
        bk, "shopping", C.last_row("shopping") + 3, 1, ci(LAST_COL) - 1, [
            "In stock and To buy are looked up from the Inventory tab "
            "automatically - type the event, ingredient and how much you "
            "need.",
            "Estimated cost uses the unit cost on the Inventory tab; the "
            "total only counts lines you haven't ticked off yet."],
        title="How this tab works")

    bk.nav_row("shopping", C.last_row("shopping") + 8, first_col=1,
               span=2, max_col=LAST_COL)
    bk.page("shopping", LAST_COL, C.last_row("shopping") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(bk, rownum):
    inv = bk.name("inventory")      # raw name: the templates quote it
    first, last = C.ROW_FIRST, C.last_row("inventory")
    return {
        "n": '=IF($D%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "available": ('=IF($D%d="","",IFERROR(SUMIF(\'%s\'!$C$%d:$C$%d,'
                      '$D%d,\'%s\'!$F$%d:$F$%d),0))'
                      % (rownum, inv, first, last, rownum, inv, first,
                         last)),
        "to_buy": '=IF($E%d="","",MAX(0,ROUND($E%d-$F%d,1)))'
                  % (rownum, rownum, rownum),
        "est_cost": ('=IF(OR($G%d="",NOT(ISNUMBER($G%d))),"",'
                     'ROUND($G%d*IFERROR(SUMIF(\'%s\'!$C$%d:$C$%d,$D%d,'
                     '\'%s\'!$H$%d:$H$%d),0),2))'
                     % (rownum, rownum, rownum, inv, first, last, rownum,
                        inv, first, last)),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["shopping"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(bk, rownum))
        cached = {"n": "", "available": "", "to_buy": "", "est_cost": ""}
        if demo.demo and i < len(demo.shopping):
            s = demo.shopping[i]
            values.update(
                event=s["event"], ingredient=s["ingredient"],
                required=s["required"], supplier=s["supplier"],
                purchased=s["purchased"] or "",
                date=s["date"], notes=s["notes"])
            cached.update(n=i + 1, available=s["available"],
                          to_buy=s["to_buy"], est_cost=s["est_cost"])
        common.write_row(bk, "shopping", COLUMNS, rownum, values, cached)
