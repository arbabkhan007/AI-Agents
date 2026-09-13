"""
Reorder List - your restock shopping list, built by itself.

The product block watches every catalog item's stock against its minimum;
the material block watches your yarn stash. Items only appear when they
dip below the line, each with a suggested quantity, supplier, estimated
cost and an urgency pill. Tick the \u2713 when you've ordered.
"""

import datetime

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "J"

_COLUMNS = [
    ("item", "Item", "calc", None),
    ("current", "Have now", "calc_qty", None),
    ("min", "Low at", "calc_qty", None),
    ("suggest", "Buy", "calc_qty", None),
    ("supplier", "Supplier", "text", None),
    ("est", "Est. cost", "calc_money", None),
    ("priority", "Priority", "calc_c", None),
    ("ordered", "Ordered \u2713", "tick", None),
    ("ordered_date", "Ordered on", "date", None),
]

_PROD_SRC = ("catalog", C.COLS["catalog"])
_MAT_SRC = ("materials", C.COLS["materials"])


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("reorder")
    demo = bk.demo

    common.sheet_head(bk, "reorder", LAST_COL, "\U0001F504  Reorder List",
                      "Everything running low, in one shopping list")

    common.chips(bk, "reorder", [
        ('="Need restocking: "&TEXT(COUNTIF($B$%d:$B$%d,"?*")'
         '+COUNTIF($B$%d:$B$%d,"?*"),"0")'
         % (C.RO_PROD_FIRST, C.RO_PROD_LAST, C.RO_MAT_FIRST,
            C.RO_MAT_LAST), "warn",
         "Need restocking: %d" % _count_low(demo), 3),
        ('="Estimated bill: "&Currency&TEXT(SUM($G$%d:$G$%d),"#,##0.00")'
         % (C.RO_PROD_FIRST, C.RO_MAT_LAST), "bad",
         "Estimated bill: %s%s" % (demo.settings["currency"] if demo
                                   else "$",
                                   format(demo.agg["reorder_cost"]
                                          if demo else 0, ",.2f")), 3),
        ('="Urgent (sold out): "&TEXT(COUNTIF($H$%d:$H$%d,"%s"),"0")'
         % (C.RO_PROD_FIRST, C.RO_MAT_LAST, C.PR_URGENT), "primary",
         "Urgent (sold out): %d" % _count_urgent(demo), 3),
    ])

    # ------------------------------------------------------ products
    ws.set_row(r(8), 22)
    bk.band("reorder", 8, 1, ci(LAST_COL), S.section, height=22)
    ws.write(r(8), 1, "  Products to restitch", S.section)
    common.header_row(bk, "reorder", _COLUMNS, row=9, height=30)
    for i in range(C.RO_PROD_LAST - C.RO_PROD_FIRST + 1):
        rownum = C.RO_PROD_FIRST + i
        values, cached = _prod_row(bk, rownum, i)
        common.write_row(bk, "reorder", _COLUMNS, rownum, values, cached)
        ws.set_row(r(rownum), 20)

    # ----------------------------------------------------- materials
    ws.set_row(r(C.RO_MAT_FIRST - 2), 22)
    bk.band("reorder", C.RO_MAT_FIRST - 2, 1, ci(LAST_COL), S.section_accent,
            height=22)
    ws.write(r(C.RO_MAT_FIRST - 2), 1, "  Yarn & materials to buy",
             S.section_accent)
    common.header_row(bk, "reorder", _COLUMNS, row=C.RO_MAT_FIRST - 1,
                      height=30)
    for i in range(C.RO_MAT_LAST - C.RO_MAT_FIRST + 1):
        rownum = C.RO_MAT_FIRST + i
        values, cached = _mat_row(bk, rownum, i)
        common.write_row(bk, "reorder", _COLUMNS, rownum, values, cached)
        ws.set_row(r(rownum), 20)

    # -------------------------------------------------------- totals
    trow = C.RO_MAT_LAST + 2
    common.totals_row(bk, "reorder", trow, {
        "est": ('=SUM($G$%d:$G$%d)' % (C.RO_PROD_FIRST, C.RO_MAT_LAST),
                "#,##0.00", demo.agg["reorder_cost"] if demo else 0),
        "suggest": ('=SUM($E$%d:$E$%d)' % (C.RO_PROD_FIRST, C.RO_MAT_LAST),
                    "#,##0", _suggest_total(demo)),
    }, first_col="B", label="SHOPPING LIST TOTAL", label_span=("C", "F"))

    # ------------------------------------------------- DV + CF blocks
    ws.data_validation(
        r(C.RO_PROD_FIRST), ci("F"), r(C.RO_PROD_LAST), ci("F"),
        {"validate": "list", "source": "=Suppliers", "ignore_blank": True,
         "show_error": False})
    bk.stats["validations"] += 1
    tick_opts = {"validate": "list", "source": "=Tick",
                 "ignore_blank": True, "show_input": True,
                 "input_title": "Tick it off",
                 "input_message": "Pick \u2713 once the item is ordered."}
    date_opts = {"validate": "date", "criteria": "between",
                 "minimum": datetime.date(2000, 1, 1),
                 "maximum": datetime.date(2100, 12, 31),
                 "ignore_blank": True, "show_error": True,
                 "error_title": "That's not a date",
                 "error_message": "Enter the date you ordered it.",
                 "error_type": "warning"}
    for colL, opts in ((bk.col("reorder", "ordered"), tick_opts),
                       (bk.col("reorder", "ordered_date"), date_opts)):
        col = ci(colL)
        for first, last in ((C.RO_PROD_FIRST, C.RO_PROD_LAST),
                            (C.RO_MAT_FIRST, C.RO_MAT_LAST)):
            ws.data_validation(r(first), col, r(last), col, opts)
            bk.stats["validations"] += 1

    H = bk.col("reorder", "priority")
    colH = ci(H)
    for first, last in ((C.RO_PROD_FIRST, C.RO_PROD_LAST),
                        (C.RO_MAT_FIRST, C.RO_MAT_LAST)):
        bk.cond("reorder", r(first), colH, r(last), colH, {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (H, first, C.PR_URGENT),
            "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
        bk.cond("reorder", r(first), colH, r(last), colH, {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (H, first, C.PR_HIGH),
            "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    common.tick_cf(bk, "reorder", ["ordered"])

    nrow = trow + 2
    common.note_block(
        bk, "reorder", nrow, 1, ci(LAST_COL), [
            "Products appear when stock drops below the 'Keep min.' level "
            "you set on the Product Catalog; materials when the stash "
            "reaches its 'Low at' number.",
            "Buy = double your minimum minus what's left - enough to "
            "rebuild the buffer without over-buying yarn.",
            "Tick the \u2713 once it's ordered and add the date - the list "
            "becomes your paper trail.",
        ], title="  How the list builds itself")

    common.footer_nav(bk, "reorder", nrow + 5, LAST_COL, zoom=90)


# ---------------------------------------------------------------------------
def _prod_row(bk, rownum, i):
    cat = bk.q("catalog")
    crow = C.ROW_FIRST + i
    p = bk.demo.products[i] if bk.demo and i < len(bk.demo.products) else None
    st, mn = C.COLS["catalog"]["stock"], C.COLS["catalog"]["min"]
    n_col = C.COLS["catalog"]["name"]
    values = {
        "item": '=IF(OR({cat}!${nc}{cr}="",{cat}!${sc}{cr}>={cat}!${mc}{cr})'
                ',"",{cat}!${nc}{cr})'.format(cat=cat, nc=n_col, cr=crow,
                                              sc=st, mc=mn),
        "current": '=IF($B{row}="","",{cat}!${sc}{cr})'.format(
            row=rownum, cat=cat, sc=st, cr=crow),
        "min": '=IF($B{row}="","",{cat}!${mc}{cr})'.format(
            row=rownum, cat=cat, mc=mn, cr=crow),
        "suggest": '=IF($B{row}="","",MAX(0,$D{row}*2-$C{row}))'.format(
            row=rownum),
        "est": '=IF($B{row}="","",ROUND($E{row}*IFERROR(VLOOKUP($B{row},'
               '{cat}!${nc}{fr}:${uc}{lr},7,0),0),2))'.format(
            row=rownum, cat=cat, nc=C.COLS["catalog"]["name"],
            fr=C.ROW_FIRST, uc=C.COLS["catalog"]["unit_cost"],
            lr=C.last_row("catalog")),
        "priority": '=IF($B{row}="","",IF($C{row}<=0,"{u}","{h}"))'.format(
            row=rownum, u=C.PR_URGENT, h=C.PR_HIGH),
    }
    cached = dict.fromkeys(values.keys(), 0)
    if p and p["stock"] < p["min"]:
        cached.update(item=p["name"], current=p["stock"], min=p["min"],
                      suggest=max(0, p["min"] * 2 - p["stock"]),
                      est=round(max(0, p["min"] * 2 - p["stock"])
                              * p["unit_cost"], 2),
                      priority=C.PR_URGENT if p["stock"] <= 0 else C.PR_HIGH)
    elif p:
        cached.update(item="", current="", min="", suggest="", est="",
                      priority="")
    return values, cached


def _mat_row(bk, rownum, i):
    mt = bk.q("materials")
    crow = C.ROW_FIRST + i
    nm, rem, thr = (C.COLS["materials"]["name"],
                    C.COLS["materials"]["remaining"],
                    C.COLS["materials"]["threshold"])
    sup, cu = C.COLS["materials"]["supplier"], C.COLS["materials"]["cost_unit"]
    m = bk.demo.materials[i] if bk.demo and i < len(bk.demo.materials) \
        else None
    values = {
        "item": '=IF(OR({mt}!${nc}{cr}="",{mt}!${rc}{cr}>{mt}!${tc}{cr}),'
                '"",{mt}!${nc}{cr})'.format(mt=mt, nc=nm, cr=crow, rc=rem,
                                            tc=thr),
        "current": '=IF($B{row}="","",{mt}!${rc}{cr})'.format(
            row=rownum, mt=mt, rc=rem, cr=crow),
        "min": '=IF($B{row}="","",{mt}!${tc}{cr})'.format(
            row=rownum, mt=mt, tc=thr, cr=crow),
        "suggest": '=IF($B{row}="","",MAX(0,$D{row}*2-$C{row}))'.format(
            row=rownum),
        "supplier": '=IF($B{row}="","",{mt}!${sc}{cr})'.format(
            row=rownum, mt=mt, sc=sup, cr=crow),
        "est": '=IF($B{row}="","",ROUND($E{row}*IFERROR(VLOOKUP($B{row},'
               '{mt}!${nc}{fr}:${uc}{lr},7,0),0),2))'.format(
            row=rownum, mt=mt, nc=nm, fr=C.ROW_FIRST, uc=cu,
            lr=C.last_row("materials")),
        "priority": '=IF($B{row}="","",IF($C{row}<=0,"{u}","{h}"))'.format(
            row=rownum, u=C.PR_URGENT, h=C.PR_HIGH),
    }
    cached = dict.fromkeys(values.keys(), 0)
    if m and m["remaining"] <= m["threshold"]:
        cached.update(item=m["name"], current=m["remaining"],
                      min=m["threshold"],
                      suggest=max(0, m["threshold"] * 2 - m["remaining"]),
                      supplier=m["supplier"],
                      est=round(max(0, m["threshold"] * 2 - m["remaining"])
                              * m["cost_unit"], 2),
                      priority=C.PR_URGENT if m["remaining"] <= 0
                      else C.PR_HIGH)
    elif m:
        cached.update(item="", current="", min="", suggest="", est="",
                      priority="", supplier="")
    return values, cached


def _count_low(demo):
    if not demo:
        return 0
    return demo.agg["low_products"] + demo.agg["low_materials"]


def _count_urgent(demo):
    if not demo:
        return 0
    n = 0
    for p in demo.products:
        if p["stock"] < p["min"] and p["stock"] <= 0:
            n += 1
    for m in demo.materials:
        if m["remaining"] <= m["threshold"] and m["remaining"] <= 0:
            n += 1
    return n


def _suggest_total(demo):
    if not demo:
        return 0
    total = 0
    for p in demo.products:
        if p["stock"] < p["min"]:
            total += max(0, p["min"] * 2 - p["stock"])
    for m in demo.materials:
        if m["remaining"] <= m["threshold"]:
            total += max(0, m["threshold"] * 2 - m["remaining"])
    return total
