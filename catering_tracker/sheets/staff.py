"""
Staff & Labor: the roster and the wage bill.

One row per shift: hours and rate in, overtime at 1.5x, the shift cost
calculates itself.  Unpaid shifts stay highlighted until you tick them,
and the Dashboard keeps a running count.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Team member", "text", "accent"),
    ("role", "Role", "center", None),
    ("event", "Event", "center", None),
    ("hours", "Hours", "qty1", None),
    ("rate", "Rate", "money", None),
    ("ot", "OT hrs", "qty1", None),
    ("total", "Shift cost", "calc_money", None),
    ("paid", "Paid", "tick", "ok"),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "K"


def build(bk):
    ws = bk.ws("staff")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("staff")
    bk.title_block("staff", "Staff & Labor",
                   "Crew, shifts and the wage bill - overtime at 1.5x",
                   LAST_COL)
    bk.stats_strip("staff", [
        ('="Shifts logged: "&COUNTA(%s)' % bk.rng("staff", "name"),
         "accent", "Shifts logged: %d" % len(demo.staff)),
        ('="Wage bill: "&Currency&TEXT(SUMPRODUCT((%s<>"")*%s*%s)'
         '+SUMPRODUCT((%s<>"")*%s*%s*1.5),"#,##0")'
         % (bk.rng("staff", "name"), bk.rng("staff", "hours"),
            bk.rng("staff", "rate"), bk.rng("staff", "name"),
            bk.rng("staff", "ot"), bk.rng("staff", "rate")),
         "bad", "Wage bill: %s" % demo.money(
             sum(s["total"] for s in demo.staff))),
        ('="Unpaid shifts: "&%s' % bk.kpi("staff_unpaid"), "warn",
         "Unpaid shifts: %d" % bk.cached("staff_unpaid", 0)),
    ])

    common.table_frame(bk, "staff", COLUMNS)
    _rows(bk)

    # validations
    common.list_dv(bk, "staff", "role", "staff_roles", title="Role",
                   message="Head Chef, Server... (edit on Setup).")
    ws.data_validation(
        r(C.ROW_FIRST), ci("E"), r(C.last_row("staff")), ci("E"),
        {"validate": "list", "source": "=EventList", "ignore_blank": True,
         "show_input": True, "input_title": "Event",
         "input_message": "Which booking is this shift for?"})
    bk.stats["validations"] += 1
    common.money_dv(bk, "staff", ["rate"])
    common.tick_dv(bk, "staff", ["paid"])

    # conditional formats
    common.tick_cf(bk, "staff", ["paid"])
    L = bk.col("staff", "paid")
    col = ci(L)
    bk.cond("staff", C.ROW_FIRST, col, C.last_row("staff"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<>"%s")'
                    % (bk.col("staff", "name"), C.ROW_FIRST, L,
                       C.ROW_FIRST, C.TICK),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})

    common.totals_row(bk, "staff", C.last_row("staff") + 1, {
        "total": ('=SUMPRODUCT((%s<>"")*%s*%s)+SUMPRODUCT((%s<>"")*%s*%s'
                  '*1.5)'
                  % (bk.rng("staff", "name"), bk.rng("staff", "hours"),
                     bk.rng("staff", "rate"), bk.rng("staff", "name"),
                     bk.rng("staff", "ot"), bk.rng("staff", "rate")),
                  "money", round(sum(s["total"] for s in demo.staff), 2)),
    }, first_col="B", last_col=LAST_COL, label="TOTAL WAGE BILL",
        label_span=("B", "G"))

    common.note_block(
        bk, "staff", C.last_row("staff") + 3, 1, ci(LAST_COL) - 1, [
            "Shift cost = hours x rate + overtime x rate x 1.5.  It "
            "calculates itself; the totals feed the labor % on the "
            "Dashboard when you log wages on the Expenses tab.",
            "Tick the Paid box when the shift is settled - unpaid shifts "
            "stay amber until you do."],
        title="How this tab works")

    bk.nav_row("staff", C.last_row("staff") + 8, first_col=1, span=2,
               max_col=LAST_COL)
    bk.page("staff", LAST_COL, C.last_row("staff") + 10, freeze=(7, 2),
            title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "total": '=IF(OR($F%d="",$G%d=""),"",ROUND($F%d*$G%d+$H%d*$G%d*1.5,2))'
                 % (rownum, rownum, rownum, rownum, rownum, rownum),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["staff"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "total": ""}
        if demo.demo and i < len(demo.staff):
            s = demo.staff[i]
            values.update(
                name=s["name"], role=s["role"], event=s["event"],
                hours=s["hours"], rate=s["rate"], ot=s["ot"],
                paid=s["paid"] or "", notes=s["notes"])
            cached.update(n=i + 1, total=s["total"])
        common.write_row(bk, "staff", COLUMNS, rownum, values, cached)
