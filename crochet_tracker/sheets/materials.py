"""
Yarn & Materials - your stash, with cost per ball and live remaining counts.

Total spend, remaining = purchased - used, and the reorder flag calculate
themselves; the supplier dropdown comes from Lists & Settings.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "N"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Material", "text", None),
    ("color", "Colour", "text", None),
    ("brand", "Brand", "text", None),
    ("weight", "Yarn weight", "text", None),
    ("purchased", "Purchased", "qty", None),
    ("unit", "Unit", "center", None),
    ("cost_unit", "Cost / unit", "money", None),
    ("total", "Total cost", "calc_money", None),
    ("used", "Used so far", "qty", None),
    ("remaining", "Remaining", "calc_qty", None),
    ("supplier", "Supplier", "text", None),
    ("threshold", "Low at", "qty", None),
    ("reorder", "Reorder?", "calc_c", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("materials")
    demo = bk.demo

    common.sheet_head(bk, "materials", LAST_COL,
                      "\U0001F9F5  Yarn & Materials",
                      "Your whole stash with costs - and what's left on the "
                      "shelf")

    common.chips(bk, "materials", [
        ('="Materials: "&TEXT(COUNTA(%s),"0")' % bk.rng("materials", "name"),
         "plum", "Materials: %d" % (len(demo.materials) if demo else 0), 3),
        ('="Still on the shelf: "&TEXT(SUM(%s),"#,##0")'
         % bk.rng("materials", "remaining"), "info",
         "Still on the shelf: %d"
         % (sum(m["remaining"] for m in demo.materials) if demo else 0), 3),
        ('="Stash value: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("materials", "total"), "gold",
         "Stash value: %s%s" % (demo.settings["currency"] if demo else "$",
                                format(sum(m["total"] for m in demo.materials)
                                       if demo else 0, ",.2f")), 3),
        ('=IF(%s>0,"! "&TEXT(%s,"0")&" materials running low","Stash looks '
         'healthy")' % (bk.kpi("low_materials"), bk.kpi("low_materials")),
         "warn", _low_chip(demo), 3),
    ])

    common.table_frame(bk, "materials", _COLUMNS, height=22)

    for i in range(common.n_rows("materials")):
        rownum = common.first_row() + i
        m = demo.materials[i] if demo and i < len(demo.materials) else None
        values, cached = _row_values(bk, rownum, m)
        common.write_row(bk, "materials", _COLUMNS, rownum, values, cached)

    trow = common.last_row("materials") + 2
    common.totals_row(bk, "materials", trow, {
        "name": ('=COUNTA(%s)' % bk.rng("materials", "name"), "0",
                 len(demo.materials) if demo else 0),
        "total": ('=SUM(%s)' % bk.rng("materials", "total"), "#,##0.00",
                  round(sum(m["total"] for m in demo.materials), 2)
                  if demo else 0),
        "used": ('=SUM(%s)' % bk.rng("materials", "used"), "#,##0",
                 sum(m["used"] for m in demo.materials) if demo else 0),
    }, first_col="B", label="TOTALS", label_span=("C", "E"))

    common.list_dv(bk, "materials", "weight", "weights",
                   title="Yarn weight",
                   message="Pick the weight - edit options on Lists & "
                           "Settings.")
    common.list_dv(bk, "materials", "unit", "units", title="Unit",
                   message="balls, metres, grams... your call.")
    common.list_dv(bk, "materials", "supplier", "suppliers",
                   title="Supplier")
    common.money_dv(bk, "materials", ["cost_unit"])
    common.whole_dv(bk, "materials", ["purchased", "used", "threshold"],
                    0, 99999)

    common.status_cf(bk, "materials", "reorder", {
        C.RE_YES: (th.warn_soft, th.warn),
        C.RE_NO: (th.ok_soft, th.ok),
    })
    common.databar(bk, "materials", "remaining", color=th.plum)

    nrow = trow + 2
    common.note_block(
        bk, "materials", nrow, 1, ci(LAST_COL), [
            "Remaining = purchased - used. Update 'Used so far' as you work "
            "through a ball (rough counts are fine).",
            "When remaining drops to the 'Low at' number, the Reorder List "
            "tab adds it to your shopping list with an estimated cost.",
        ], title="  How this tab works")

    common.footer_nav(bk, "materials", nrow + 5, LAST_COL, zoom=85)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, m):
    col = bk.col
    mt = "materials"
    values = dict.fromkeys([c[0] for c in _COLUMNS], None)
    values["total"] = ('=IF(${n}{row}="","",ROUND(N(${p}{row})*N(${c}{row}),'
                       '2))'
                       .format(n=col(mt, "name"), row=rownum,
                               p=col(mt, "purchased"), c=col(mt,
                                                             "cost_unit")))
    values["remaining"] = ('=IF(${n}{row}="","",N(${p}{row})-N(${u}{row}))'
                           .format(n=col(mt, "name"), row=rownum,
                                   p=col(mt, "purchased"),
                                   u=col(mt, "used")))
    values["reorder"] = ('=IF(${n}{row}="","",IF(${rem}{row}<=${th}{row},'
                         '"{y}","{k}"))'
                         .format(n=col(mt, "name"), row=rownum,
                                 rem=col(mt, "remaining"),
                                 th=col(mt, "threshold"),
                                 y=C.RE_YES, k=C.RE_NO))
    cached = dict.fromkeys(values.keys(), 0)
    if m:
        values.update(name=m["name"], color=m["color"], brand=m["brand"],
                      weight=m["weight"], purchased=m["purchased"],
                      unit=m["unit"], cost_unit=m["cost_unit"],
                      used=m["used"], supplier=m["supplier"],
                      threshold=m["threshold"])
        cached.update(total=m["total"], remaining=m["remaining"],
                      reorder=C.RE_YES if m["remaining"] <= m["threshold"]
                      else C.RE_NO)
    return values, cached


def _low_chip(demo):
    if not demo:
        return "Stash looks healthy"
    n = demo.agg["low_materials"]
    return "! %d materials running low" % n if n else "Stash looks healthy"
