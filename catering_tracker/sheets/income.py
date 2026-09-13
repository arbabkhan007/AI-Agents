"""
Payments: deposits, installments and final balances.

One row per invoice: the amount, the deposit, any extra payments, and the
due date.  Received, balance and the paid/partial/unpaid chip calculate
themselves; overdue balances go red and the receivable cards on the
Dashboard stay honest.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("invoice", "Invoice #", "center", "accent"),
    ("client", "Client", "text", None),
    ("event_date", "Event date", "date", "gold"),
    ("amount", "Invoice total", "money", None),
    ("deposit", "Deposit", "money", "ok"),
    ("pay1", "Payment 2", "money", None),
    ("pay2", "Final payment", "money", None),
    ("received", "Received", "calc_money", None),
    ("balance", "Balance", "calc_money", None),
    ("due", "Due date", "date", "warn"),
    ("status", "Status", "calc_c", None),
]

LAST_COL = "M"


def build(bk):
    ws = bk.ws("income")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("income")
    bk.title_block("income", "Payments",
                   "Deposits, installments and final balances - who owes "
                   "what", LAST_COL)
    bk.stats_strip("income", [
        ('="Invoiced: "&Currency&TEXT(SUM(%s),"#,##0")'
         % bk.rng("income", "amount"), "accent",
         "Invoiced: %s" % demo.money(
             sum(i["amount"] for i in demo.income))),
        ('="Received: "&Currency&TEXT(%s,"#,##0")' % bk.kpi("revenue"),
         "ok", "Received: %s" % demo.money(bk.cached("revenue", 0))),
        ('="Outstanding: "&Currency&TEXT(%s,"#,##0")' % bk.kpi("outstanding"),
         "warn", "Outstanding: %s" % demo.money(
             bk.cached("outstanding", 0))),
        ('="Overdue: "&%s&" invoice%s"' % (bk.kpi("overdue"), "s"),
         "bad", "Overdue: %d invoice%s"
         % (bk.cached("overdue", 0), "s" if bk.cached("overdue", 0) != 1
            else "")),
    ])

    common.table_frame(bk, "income", COLUMNS)
    _rows(bk)

    # validations
    ws.data_validation(
        r(C.ROW_FIRST), ci("D"), r(C.last_row("income")), ci("D"),
        {"validate": "list", "source": "=ClientsList", "ignore_blank": True,
         "show_input": True, "input_title": "Client",
         "input_message": "Pick a client from the Clients tab."})
    bk.stats["validations"] += 1
    common.date_dv(bk, "income", ["event_date", "due"])
    common.money_dv(bk, "income", ["amount", "deposit", "pay1", "pay2"])

    # conditional formats
    common.status_cf(bk, "income", "status", {
        C.PS_UNPAID: (th.bad_soft, th.bad),
        C.PS_PART: (th.warn_soft, th.warn),
        C.PS_PAID: (th.ok_soft, th.ok),
    })
    L = bk.col("income", "due")
    col = ci(L)
    first, last = C.ROW_FIRST, C.last_row("income")
    bk.cond("income", first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<TODAY(),$%s%d>0)'
                    % (L, first, L, first, bk.col("income", "balance"),
                       first),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond("income", first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d>=TODAY(),$%s%d-TODAY()'
                    '<=DueSoonDays,$%s%d>0)'
                    % (L, first, L, first, L, first,
                       bk.col("income", "balance"), first),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})

    common.totals_row(bk, "income", C.last_row("income") + 1, {
        "amount": ("=SUM(%s)" % bk.rng("income", "amount"), "money0",
                   round(sum(i["amount"] for i in demo.income), 2)),
        "received": ('=SUM(%s)+SUM(%s)+SUM(%s)'
                     % (bk.rng("income", "deposit"), bk.rng("income", "pay1"),
                        bk.rng("income", "pay2")),
                     "money0", round(bk.cached("revenue", 0), 2)),
        "balance": ('=SUM(%s)-SUM(%s)-SUM(%s)-SUM(%s)'
                    % (bk.rng("income", "amount"),
                       bk.rng("income", "deposit"),
                       bk.rng("income", "pay1"), bk.rng("income", "pay2")),
                     "money0", round(bk.cached("outstanding", 0), 2)),
    }, first_col="B", last_col=LAST_COL, label="TOTALS",
        label_span=("B", "D"))

    # monthly receipts chart (works in both editions - reads the _Data pool)
    ch = bk.chart("column")
    da = bk.name("data")
    ch.add_series({
        "name": "Cash received",
        "categories": "='%s'!$H$%d:$H$%d" % (da, C.DATA_MONTH_FIRST,
                                             C.DATA_MONTH_FIRST + 11),
        "values": "='%s'!$I$%d:$I$%d" % (da, C.DATA_MONTH_FIRST,
                                         C.DATA_MONTH_FIRST + 11),
        "fill": {"color": th.ok}, "border": {"none": True},
    })
    ch.set_title({"name": "Cash received, by month",
                  "name_font": {"name": th.title_font, "size": 11,
                                "bold": True, "color": th.ink}})
    ch.set_legend({"none": True})
    ch.set_x_axis({"num_font": {"size": 9, "color": th.muted}})
    ch.set_y_axis({"num_format": "#,##0",
                   "num_font": {"size": 9, "color": th.muted},
                   "major_gridlines": {"visible": True, "line": {
                       "color": th.border, "width": 0.75}}})
    ch.set_chartarea({"border": {"color": th.border},
                      "fill": {"color": th.card}})
    ch.set_size({"width": 840, "height": 300})
    ws.insert_chart(r(C.last_row("income") + 4), 1, ch,
                    {"x_offset": 4, "y_offset": 4})

    common.note_block(
        bk, "income", C.last_row("income") + 21, 1, ci(LAST_COL) - 1, [
            "Received and Balance calculate themselves from the deposit "
            "and payment columns - only type in the white cells.",
            "Due dates go amber inside your due-soon window and red once "
            "they pass with a balance left; the Dashboard overdue card "
            "counts them."],
        title="How this tab works")

    bk.nav_row("income", C.last_row("income") + 28, first_col=1, span=2,
               max_col=LAST_COL)
    bk.page("income", LAST_COL, C.last_row("income") + 30, freeze=(7, 2),
            title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "received": '=IF($F%d="","",ROUND($G%d+$H%d+$I%d,2))'
                    % (rownum, rownum, rownum, rownum),
        "balance": '=IF($F%d="","",$F%d-$J%d)'
                   % (rownum, rownum, rownum),
        "status": ('=IF($F%d="","",IF($K%d<=0,"%s",IF($J%d>0,"%s","%s")))'
                   % (rownum, rownum, C.PS_PAID, rownum, C.PS_PART,
                      C.PS_UNPAID)),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["income"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "received": "", "balance": "", "status": ""}
        if demo.demo and i < len(demo.income):
            inv = demo.income[i]
            values.update(
                invoice=inv["invoice"], client=inv["client"],
                event_date=inv["event_date"], amount=inv["amount"],
                deposit=inv["deposit"], pay1=inv["pay1"], pay2=inv["pay2"],
                due=inv["due"])
            cached.update(n=i + 1, received=round(inv["received"], 2),
                          balance=round(inv["balance"], 2),
                          status=inv["status"])
        common.write_row(bk, "income", COLUMNS, rownum, values, cached)
