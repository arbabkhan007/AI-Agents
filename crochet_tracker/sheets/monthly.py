"""
Monthly Summary - your year, month by month.

Revenue, cost of goods, fair fees and net profit per month are pulled from
the hidden _Data engine; units, average sale, profit per item and fair
counts compute here. The totals row is your whole year.
"""

from .. import config as C
from ..book import r, ci, cl
from . import common
from . import data as D

LAST_COL = "K"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("month", "Month", "calc", None),
    ("revenue", "Revenue", "calc_money", None),
    ("cogs", "Cost of goods", "calc_money", None),
    ("fees", "Fair fees", "calc_money", None),
    ("net", "Net profit", "calc_money", None),
    ("margin", "Margin", "calc_pct1", None),
    ("units", "Units sold", "calc_qty", None),
    ("aov", "Avg sale", "calc_money", None),
    ("per_item", "Profit / item", "calc_money", None),
    ("markets", "Fairs", "calc_qty", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("monthly")
    demo = bk.demo

    common.sheet_head(bk, "monthly", LAST_COL,
                      "\U0001F4C5  Monthly Summary",
                      "Your whole year, one row per month")

    best = _best_month(demo)
    common.chips(bk, "monthly", [
        ('="Year revenue: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("monthly", "revenue"), "primary",
         "Year revenue: %s%s" % (demo.settings["currency"] if demo else "$",
                                 format(sum(m[1] for m in demo.agg["months"])
                                        if demo else 0, ",.2f")), 3),
        ('="Year net: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("monthly", "net"), "ok",
         "Year net: %s%s" % (demo.settings["currency"] if demo else "$",
                             format(sum(m[4] for m in demo.agg["months"])
                                    if demo else 0, ",.2f")), 3),
        ('="Best month: "&IFERROR(INDEX(%s,MATCH(MAX(%s),%s,0)),"-")'
         % (bk.rng("monthly", "net"), bk.rng("monthly", "net"),
            bk.rng("monthly", "net")), "gold",
         "Best month: %s" % best, 3),
        ('="Fairs this year: "&TEXT(SUM(%s),"0")'
         % bk.rng("monthly", "markets"), "info",
         "Fairs this year: %d" % (sum(m[6] for m in demo.agg["months"])
                                  if demo else 0), 2),
    ])

    common.table_frame(bk, "monthly", _COLUMNS, height=20)

    for m in range(12):
        rownum = common.first_row() + m
        values, cached = _row_values(bk, rownum, m + 1)
        common.write_row(bk, "monthly", _COLUMNS, rownum, values, cached)

    # ------------------------------------------------------ totals
    trow = common.last_row("monthly") + 1
    common.totals_row(bk, "monthly", trow, {
        "revenue": ('=SUM(%s)' % bk.rng("monthly", "revenue"), "#,##0.00",
                    round(sum(m[1] for m in demo.agg["months"]), 2)
                    if demo else 0),
        "cogs": ('=SUM(%s)' % bk.rng("monthly", "cogs"), "#,##0.00",
                 round(sum(m[2] for m in demo.agg["months"]), 2)
                 if demo else 0),
        "fees": ('=SUM(%s)' % bk.rng("monthly", "fees"), "#,##0.00",
                 round(sum(m[3] for m in demo.agg["months"]), 2)
                 if demo else 0),
        "net": ('=SUM(%s)' % bk.rng("monthly", "net"), "#,##0.00",
                round(sum(m[4] for m in demo.agg["months"]), 2)
                if demo else 0),
        "units": ('=SUM(%s)' % bk.rng("monthly", "units"), "#,##0",
                  sum(m[5] for m in demo.agg["months"]) if demo else 0),
        "markets": ('=SUM(%s)' % bk.rng("monthly", "markets"), "#,##0",
                    sum(m[6] for m in demo.agg["months"]) if demo else 0),
    }, first_col="B", last_col=LAST_COL, label="YEAR TOTAL")

    # ------------------------------------------------------ CF bars
    common.databar(bk, "monthly", "revenue", color=th.primary_2)
    L = bk.col("monthly", "net")
    col = ci(L)
    bk.cond("monthly", C.ROW_FIRST, col, C.last_row("monthly"), col, {
        "type": "cell", "criteria": "<", "value": 0,
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond("monthly", C.ROW_FIRST, col, C.last_row("monthly"), col, {
        "type": "cell", "criteria": ">", "value": 0,
        "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})

    # ------------------------------------------------------ notes
    nrow = trow + 2
    common.note_block(
        bk, "monthly", nrow, 1, ci(LAST_COL), [
            "Months follow the Report year on your Lists & Settings tab. "
            "Red net months usually mean fair fees paid before the fair "
            "happened - they catch up next month.",
            "Fair fees land in the month of the fair itself, so a booked "
            "Autumn fair shows its booth fee in September.",
        ], title="  Reading the months")

    common.footer_nav(bk, "monthly", nrow + 5, LAST_COL, zoom=90)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, m):
    drow = C.DATA_MONTH_FIRST + m - 1
    qd = bk.q("data")
    mref = 'DATE(ReportYear,%d,1)' % m
    sdate = bk.rng("sales", "date")
    edate = bk.rng("events", "date")
    cached = [0.0] * 7 + [0]
    if bk.demo:
        for mm, rev, cogs, fees, net, units, markets, txns in \
                bk.demo.agg["months"]:
            if mm == m:
                cached = [rev, cogs, fees, net, units, 0.0, markets]
                txns_c = txns
                break
        else:
            txns_c = 0
    else:
        txns_c = 0
    values = {
        "month": C.MONTH_NAMES[m - 1],
        "revenue": "=%s!%s%d" % (qd, D.M_REV, drow),
        "cogs": "=%s!%s%d" % (qd, D.M_COGS, drow),
        "fees": "=%s!%s%d" % (qd, D.M_FEES, drow),
        "net": "=%s!%s%d" % (qd, D.M_NET, drow),
        "margin": '=IFERROR($%s%d/$%s%d,0)'
                  % (bk.col("monthly", "net"), rownum,
                     bk.col("monthly", "revenue"), rownum),
        "units": '=SUMIFS(%s,%s,">="&%s,%s,"<"&EDATE(%s,1))'
                 % (bk.rng("sales", "qty"), sdate, mref, sdate, mref),
        "aov": '=IFERROR($%s%d/COUNTIFS(%s,">="&%s,%s,"<"&EDATE(%s,1)),0)'
               % (bk.col("monthly", "revenue"), rownum, sdate, mref, sdate,
                  mref),
        "per_item": '=IFERROR($%s%d/$%s%d,0)'
                    % (bk.col("monthly", "net"), rownum,
                       bk.col("monthly", "units"), rownum),
        "markets": '=SUMPRODUCT((%s>=%s)*(%s<EDATE(%s,1))*(%s<>""))'
                   % (edate, mref, edate, mref, bk.rng("events", "name")),
    }
    cached_kv = {
        "revenue": cached[0], "cogs": cached[1], "fees": cached[2],
        "net": cached[3], "units": cached[4],
        "aov": round(cached[0] / txns_c, 2) if txns_c else 0,
        "per_item": round(cached[3] / cached[4], 2) if cached[4] else 0,
        "markets": cached[6], "margin":
            round(cached[3] / cached[0], 4) if cached[0] else 0,
        "month": C.MONTH_NAMES[m - 1],
    }
    return values, cached_kv


def _best_month(demo):
    if not demo:
        return "-"
    months = demo.agg["months"]
    best = max(months, key=lambda m: m[4])
    return C.MONTH_NAMES[best[0] - 1] if best[4] > 0 else "-"
