"""
Menu Costing: every dish priced to the cent.

Cost per portion in, menu price out - profit and margin per dish calculate
themselves, a data-bar shows the healthiest margins, and the chart compares
cost vs price for the whole menu.  The Quote Calculator's "food cost per
guest" comes straight from here.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("item", "Menu item", "text", "accent"),
    ("category", "Category", "center", None),
    ("ingredients", "Key ingredients", "wrap", None),
    ("portion", "Portion", "center", None),
    ("cost", "Cost / portion", "money", "bad"),
    ("price", "Menu price", "money", "ok"),
    ("profit", "Profit", "calc_money", None),
    ("margin", "Margin", "calc_pct", None),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "K"


def build(bk):
    ws = bk.ws("menu")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("menu")
    bk.title_block("menu", "Menu Costing",
                   "Cost every dish - margins that make the quotes honest",
                   LAST_COL)
    bk.stats_strip("menu", [
        ('="Dishes priced: "&COUNTA(%s)' % bk.rng("menu", "item"),
         "accent", "Dishes priced: %d" % len(demo.menu)),
        ('="Avg cost: "&Currency&TEXT(IFERROR(AVERAGE(%s),0),"0.00")'
         % bk.rng("menu", "cost"), "bad",
         "Avg cost: %s" % demo.money(
             sum(m["cost"] for m in demo.menu) / max(1, len(demo.menu)), 2)),
        ('="Avg price: "&Currency&TEXT(IFERROR(AVERAGE(%s),0),"0.00")'
         % bk.rng("menu", "price"), "ok",
         "Avg price: %s" % demo.money(
             sum(m["price"] for m in demo.menu) / max(1, len(demo.menu)), 2)),
        ('="Avg margin: "&TEXT(%s,"0%%")' % bk.kpi("menu_margin"),
         "gold", "Avg margin: %.0f%%"
         % (100 * bk.cached("menu_margin", 0))),
    ])

    common.table_frame(bk, "menu", COLUMNS)
    _rows(bk)

    common.list_dv(bk, "menu", "category", "menu_categories",
                   title="Category",
                   message="Starter, Main, Dessert... (edit on Setup).")
    common.money_dv(bk, "menu", ["cost", "price"])

    # margin health: below the Setup target glows amber
    L = bk.col("menu", "margin")
    col = ci(L)
    bk.cond("menu", C.ROW_FIRST, col, C.last_row("menu"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<DefaultMargin)'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    bk.cond("menu", C.ROW_FIRST, col, C.last_row("menu"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d>=DefaultMargin)'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST),
        "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})
    common.databar(bk, "menu", "cost", color=th.bad)
    common.databar(bk, "menu", "price", color=th.ok)

    common.totals_row(bk, "menu", C.last_row("menu") + 1, {
        "cost": ("=SUM(%s)" % bk.rng("menu", "cost"), "money",
                 round(sum(m["cost"] for m in demo.menu), 2)),
        "price": ("=SUM(%s)" % bk.rng("menu", "price"), "money",
                  round(sum(m["price"] for m in demo.menu), 2)),
        "profit": ("=SUM(%s)-SUM(%s)" % (bk.rng("menu", "price"),
                                         bk.rng("menu", "cost")), "money",
                   round(sum(m["profit"] for m in demo.menu), 2)),
    }, first_col="B", last_col=LAST_COL, label="MENU TOTALS",
        label_span=("B", "D"))

    # cost vs price chart
    ch = bk.chart("column")
    me = bk.name("menu")
    cats = "='%s'!$C$%d:$C$%d" % (me, C.ROW_FIRST, C.last_row("menu"))
    ch.add_series({
        "name": "Cost / portion",
        "categories": cats,
        "values": "='%s'!$G$%d:$G$%d" % (me, C.ROW_FIRST, C.last_row("menu")),
        "fill": {"color": th.bad}, "border": {"none": True},
    })
    ch.add_series({
        "name": "Menu price",
        "categories": cats,
        "values": "='%s'!$H$%d:$H$%d" % (me, C.ROW_FIRST, C.last_row("menu")),
        "fill": {"color": th.ok}, "border": {"none": True},
    })
    ch.set_title({"name": "Cost vs price, dish by dish",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"position": "bottom"})
    ch.set_x_axis({"num_font": {"size": 8, "color": th.muted,
                                "rotation": -45}})
    ch.set_y_axis({"num_format": "0.00",
                   "num_font": {"size": 9, "color": th.muted},
                   "major_gridlines": {"visible": True, "line": {
                       "color": th.border, "width": 0.75}}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 840, "height": 330})
    ws.insert_chart(r(C.last_row("menu") + 4), 1, ch,
                    {"x_offset": 4, "y_offset": 4})

    common.note_block(
        bk, "menu", C.last_row("menu") + 21, 1, ci(LAST_COL) - 1, [
            "Cost per portion = everything on the plate: ingredients plus "
            "a share of packaging.  If the margin bar glows amber the dish "
            "is under your Setup target.",
            "Use these numbers in the Quote Calculator (food cost per "
            "guest) so every quote is backed by real food costs."],
        title="How this tab works")

    bk.nav_row("menu", C.last_row("menu") + 28, first_col=1, span=2,
               max_col=LAST_COL)
    bk.page("menu", LAST_COL, C.last_row("menu") + 30, freeze=(7, 2),
            title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "profit": '=IF(OR($G%d="",$H%d=""),"",ROUND($H%d-$G%d,2))'
                  % (rownum, rownum, rownum, rownum),
        "margin": '=IFERROR(IF($I%d="","",$I%d/$H%d),"")'
                  % (rownum, rownum, rownum),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["menu"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "profit": "", "margin": ""}
        if demo.demo and i < len(demo.menu):
            m = demo.menu[i]
            values.update(
                item=m["item"], category=m["category"],
                ingredients=m["ingredients"], portion=m["portion"],
                cost=m["cost"], price=m["price"], notes=m["notes"])
            cached.update(n=i + 1, profit=m["profit"], margin=m["margin"])
        common.write_row(bk, "menu", COLUMNS, rownum, values, cached)
