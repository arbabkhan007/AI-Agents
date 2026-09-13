"""
Equipment: what you own, what's out, what needs a service.

Owned / reserved / damaged in; available units, total value and the
Service / Soon / Ready chip calculate themselves.  The maintenance date
glows as it approaches so the chafers never let you down mid-wedding.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("item", "Item", "text", "accent"),
    ("category", "Category", "center", None),
    ("owned", "Owned", "qty", None),
    ("reserved", "Reserved", "qty", "warn"),
    ("damaged", "Damaged", "qty", "bad"),
    ("available", "Available", "calc_qty", None),
    ("unit_value", "Value / unit", "money", None),
    ("value", "Total value", "calc_money", None),
    ("maintenance", "Next service", "date", "gold"),
    ("status", "Status", "calc_c", None),
]

LAST_COL = "L"

ST_SERVICE = "\U0001F527 Service"
ST_SOON = "\U0001F7E1 Soon"
ST_READY = "\U0001F7E2 Ready"


def build(bk):
    ws = bk.ws("equipment")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("equipment")
    bk.title_block("equipment", "Equipment",
                   "Chafers to trailers - availability, value and service "
                   "dates", LAST_COL)
    bk.stats_strip("equipment", [
        ('="Items owned: "&COUNTA(%s)' % bk.rng("equipment", "item"),
         "accent", "Items owned: %d" % len(demo.equipment)),
        ('="Equipment value: "&Currency&TEXT(SUMPRODUCT((%s<>"")*%s*%s),'
         '"#,##0")'
         % (bk.rng("equipment", "item"), bk.rng("equipment", "owned"),
            bk.rng("equipment", "unit_value")), "ok",
         "Equipment value: %s" % demo.money(bk.cached("equip_value", 0))),
        ('="Reserved now: "&SUMPRODUCT((%s<>"")*%s)'
         % (bk.rng("equipment", "item"), bk.rng("equipment", "reserved")),
         "warn", "Reserved now: %d" % sum(q["reserved"]
                                          for q in demo.equipment)),
        ('="Needs attention: "&%s' % bk.kpi("equip_service"), "bad",
         "Needs attention: %d" % bk.cached("equip_service", 0)),
    ])

    common.table_frame(bk, "equipment", COLUMNS)
    _rows(bk)

    # validations
    common.whole_dv(bk, "equipment", ["owned", "reserved", "damaged"],
                    0, 100000)
    common.money_dv(bk, "equipment", ["unit_value"])
    common.date_dv(bk, "equipment", ["maintenance"])

    # conditional formats
    common.status_cf(bk, "equipment", "status", {
        ST_SERVICE: (th.bad_soft, th.bad),
        ST_SOON: (th.warn_soft, th.warn),
        ST_READY: (th.ok_soft, th.ok),
    })
    L = bk.col("equipment", "maintenance")
    col = ci(L)
    bk.cond("equipment", C.ROW_FIRST, col, C.last_row("equipment"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d-TODAY()<=30)'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})

    common.totals_row(bk, "equipment", C.last_row("equipment") + 1, {
        "owned": ("=SUM(%s)" % bk.rng("equipment", "owned"), "num",
                  sum(q["owned"] for q in demo.equipment)),
        "value": ('=SUMPRODUCT((%s<>"")*%s*%s)'
                  % (bk.rng("equipment", "item"),
                     bk.rng("equipment", "owned"),
                     bk.rng("equipment", "unit_value")),
                  "money0", bk.cached("equip_value", 0)),
    }, first_col="B", last_col=LAST_COL, label="FLEET TOTALS",
        label_span=("B", "C"))

    common.note_block(
        bk, "equipment", C.last_row("equipment") + 3, 1, ci(LAST_COL) - 1, [
            "Available = owned - reserved - damaged.  Status turns "
            "\U0001F527 Service when something is damaged and "
            "\U0001F7E1 Soon within 30 days of the service date.",
            "Use Reserved for what's already promised to upcoming events "
            "so you never double-book the trailer."],
        title="How this tab works")

    bk.nav_row("equipment", C.last_row("equipment") + 8, first_col=1,
               span=2, max_col=LAST_COL)
    bk.page("equipment", LAST_COL, C.last_row("equipment") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "available": '=IF($C%d="","",$E%d-$F%d-$G%d)'
                     % (rownum, rownum, rownum, rownum),
        "value": '=IF(OR($E%d="",$I%d=""),"",ROUND($E%d*$I%d,2))'
                 % (rownum, rownum, rownum, rownum),
        "status": ('=IF($C%d="","",IF($G%d>0,"%s",IF($K%d-TODAY()<=30,'
                   '"%s","%s")))'
                   % (rownum, rownum, ST_SERVICE, rownum, ST_SOON,
                      ST_READY)),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["equipment"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "available": "", "value": "", "status": ""}
        if demo.demo and i < len(demo.equipment):
            q = demo.equipment[i]
            values.update(
                item=q["item"], category=q["category"], owned=q["owned"],
                reserved=q["reserved"], damaged=q["damaged"],
                unit_value=q["unit_value"], maintenance=q["maintenance"],
                notes=q["notes"])
            cached.update(n=i + 1, available=q["available"],
                          value=q["value"], status=q["status"])
        common.write_row(bk, "equipment", COLUMNS, rownum, values, cached)
