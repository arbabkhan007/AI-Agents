"""
\U0001F6CD\uFE0F Shopping List - everything that is not a present:
wrapping, cards, baking, decorations, party bits.  Money spent here flows
straight into the \U0001F4B0 Budget tab.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "shopping"
LAST_COL = "M"

COLUMNS = [
    ("n", "#", "idx", None),
    ("item", "Item", "text", None),
    ("category", "Category", "center", None),
    ("store", "Store", "text", None),
    ("qty", "Qty", "qty", None),
    ("unit", "Unit cost", "money", None),
    ("total", "Total (auto)", "calc_money", "primary_2"),
    ("bought", "Bought", "tick", None),
    ("cost", "Actual cost", "money", None),
    ("spent", "In budget (auto)", "calc_money", "primary_2"),
    ("link", "Link", "link", None),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \U0001F6CD\uFE0F  Shopping List",
        "  Wrapping, cards, baking, decorations, party bits \u2014 the stuff "
        "that quietly eats the budget.",
        LAST_COL)

    chips = [
        ("B", "D", "\U0001F4DD Items: ", "shop_total", "primary", "0"),
        ("E", "F", "\u2705 Bought: ", "shop_bought", "ok", "0"),
        ("G", "H", "\U0001F4B0 Spent: ", "shop_spent", "accent", "$"),
        ("I", "J", "\U0001F4B5 Estimated: ", None, "gold", "$"),
        ("K", LAST_COL, "\U0001F4CA Progress: ", None, "info", "%"),
    ]
    for c1, c2, label, kpi_key, color, kind in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2), "", fmt)
        est = "SUM(%s)" % bk.rng(KEY, "total")
        if kpi_key:
            if kind == "$":
                formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label,
                                                               bk.kpi(kpi_key))
                cached = "%s%s" % (label, m.money(m.agg[kpi_key]))
            else:
                formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
                cached = "%s%d" % (label, m.agg[kpi_key])
        elif kind == "$":
            formula = '="%s"&Currency&TEXT(%s,"#,##0")' % (label, est)
            cached = "%s%s" % (label, m.money(sum(
                (x["qty"] or 0) * (x["unit"] or 0) for x in m.shopping)))
        else:
            formula = '="%s"&TEXT(IFERROR(%s/%s,0),"0%%")' % (
                label, bk.kpi("shop_bought"), bk.kpi("shop_total"))
            pct = (m.agg["shop_bought"] / float(m.agg["shop_total"])
                   if m.agg["shop_total"] else 0)
            cached = "%s%d%%" % (label, round(pct * 100))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = _formulas(bk, rownum)
        if i < len(m.shopping):
            row = m.shopping[i]
            values.update({"item": row["item"], "category": row["category"],
                           "store": row["store"], "qty": row["qty"],
                           "unit": row["unit"], "bought": row["bought"],
                           "cost": row["cost"], "notes": row["notes"]})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), ci("C"))

    K.list_dv(bk, KEY, "category", "shop_categories", title="Category",
              message="This is what links the item to a line on the "
                      "\U0001F4B0 Budget tab.")
    K.list_dv(bk, KEY, "store", "stores", title="Store")
    K.tick_dv(bk, KEY, ["bought"],
               message="Tick \u2713 when it is in the basket \u2014 the cost "
                       "then flows into your budget automatically.")
    K.money_dv(bk, KEY, ["unit", "cost"])
    K.whole_dv(bk, KEY, ["qty"])

    n = C.ROW_FIRST
    K.tick_cf(bk, KEY, ["bought"])
    bought = bk.col(KEY, "bought")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula", "criteria": '=$%s%d="%s"' % (bought, n, C.TICK),
        "format": S.cf(bg=th.ok_soft, fg=th.muted, strike=True)})

    total_row = C.last_row(KEY) + 2
    est_total = sum((x["qty"] or 0) * (x["unit"] or 0) for x in m.shopping)
    K.totals_row(
        bk, KEY, total_row,
        {"total": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "total"),
                                            C.ROW_FIRST, bk.col(KEY, "total"),
                                            C.last_row(KEY)),
                   "#,##0.00", est_total),
         "bought": ('=COUNTIF($%s$%d:$%s$%d,"%s")&" / "&COUNTA($%s$%d:$%s$%d)'
                    % (bk.col(KEY, "bought"), C.ROW_FIRST,
                       bk.col(KEY, "bought"), C.last_row(KEY), C.TICK,
                       bk.col(KEY, "item"), C.ROW_FIRST, bk.col(KEY, "item"),
                       C.last_row(KEY)), "@",
                    "%d / %d" % (m.agg["shop_bought"], m.agg["shop_total"])),
         "cost": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "cost"), C.ROW_FIRST,
                                           bk.col(KEY, "cost"),
                                           C.last_row(KEY)),
                  "#,##0.00", sum(x["cost"] or 0 for x in m.shopping)),
         "spent": ("=SUM($%s$%d:$%s$%d)" % (bk.col(KEY, "spent"),
                                            C.ROW_FIRST, bk.col(KEY, "spent"),
                                            C.last_row(KEY)),
                   "#,##0.00", m.agg["shop_spent"])},
        label="  TOTALS", label_span=("B", "F"), last_col=LAST_COL)

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  Tick \u2713 Bought and the \u201CIn budget\u201D column "
         "picks up the actual cost (or the estimate if you have not typed one "
         "yet).",
         "\u2022  The category decides which \U0001F4B0 Budget line the money "
         "lands on \u2014 Wrapping, Cards, Postage, Food, Baking, "
         "Decorations, Party Supplies, Travel, Charity, Other.",
         "\u2022  Starter rows are pre-filled so you can see how it works "
         "\u2014 overwrite or delete them freely."],
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
        "total": '=IF($%s%d="","",IF($%s%d="",1,$%s%d)*$%s%d)'
                 % (L("unit"), n, L("qty"), n, L("qty"), n, L("unit"), n),
        "spent": '=IF($%s%d="%s",IF($%s%d<>"",$%s%d,IF($%s%d<>"",$%s%d,0)),0)'
                 % (L("bought"), n, C.TICK, L("cost"), n, L("cost"), n,
                    L("total"), n, L("total"), n),
    }


def _cached(m, i):
    if i >= len(m.shopping):
        return {"n": "", "total": "", "spent": 0}
    row = m.shopping[i]
    qty, unit = row["qty"] or 0, row["unit"] or 0
    total = "" if row["unit"] is None else qty * unit
    return {"n": i + 1, "total": total, "spent": m._shop_spent(row)}
