"""
The Clients tab: everyone you have ever cooked for.

The balance column is calculated (quote - deposit) and the status chip is a
dropdown, so the receivables picture on the Dashboard stays honest without
any typing.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Client / company", "text", "accent"),
    ("phone", "Phone", "text", None),
    ("email", "Email", "text", None),
    ("event_date", "Next event", "date", "gold"),
    ("event_type", "Event type", "center", None),
    ("guests", "Guests", "qty", None),
    ("venue", "Venue / address", "text", None),
    ("package", "Package", "center", None),
    ("quote", "Quoted", "money", "ok"),
    ("deposit", "Deposit", "money", "ok"),
    ("balance", "Balance due", "calc_money", None),
    ("status", "Payment status", "center", "warn"),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "O"


def build(bk):
    ws = bk.ws("clients")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("clients")
    bk.title_block("clients", "Clients",
                   "Everyone you cook for - balances and history in one "
                   "place", LAST_COL)
    bk.stats_strip("clients", [
        ('="Clients: "&COUNTA(%s)' % bk.rng("clients", "name"),
         "accent", "Clients: %d" % len(demo.clients)),
        ('="Repeat rate: "&TEXT(%s,"0%%")' % bk.kpi("repeat_pct"),
         "plum", "Repeat rate: %.0f%%"
         % (100 * bk.cached("repeat_pct", 0))),
        ('="Quotes out: "&Currency&TEXT(SUM(%s),"#,##0")'
         % bk.rng("clients", "quote"), "ok",
         "Quotes out: %s" % demo.money(sum(c["quote"]
                                           for c in demo.clients))),
        ('="Still owed: "&Currency&TEXT(%s,"#,##0")' % bk.kpi("outstanding"),
         "warn", "Still owed: %s" % demo.money(bk.cached("outstanding", 0))),
    ])

    common.table_frame(bk, "clients", COLUMNS)
    _rows(bk)

    # validations
    common.list_dv(bk, "clients", "event_type", "event_types",
                   title="Event type",
                   message="Pick from your list (edit it on Setup).")
    common.fixed_dv(bk, "clients", "status", "PaymentStatuses",
                    title="Payment status",
                    message="Unpaid / Partial / Paid in full.")
    common.date_dv(bk, "clients", ["event_date"])
    common.whole_dv(bk, "clients", ["guests"], 0, 100000)
    common.money_dv(bk, "clients", ["quote", "deposit"])

    # conditional formats
    common.status_cf(bk, "clients", "status", {
        C.PS_UNPAID: (th.bad_soft, th.bad),
        C.PS_PART: (th.warn_soft, th.warn),
        C.PS_PAID: (th.ok_soft, th.ok),
    })
    # next event inside the due-soon window glows amber
    L = bk.col("clients", "event_date")
    col = ci(L)
    bk.cond("clients", C.ROW_FIRST, col, C.last_row("clients"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d>=TODAY(),$%s%d-TODAY()<=DueSoonDays)'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST, L, C.ROW_FIRST),
        "format": S.cf(bg=th.info_soft, fg=th.info, bold=True)})

    # totals
    common.totals_row(bk, "clients", C.last_row("clients") + 1, {
        "guests": ("=SUM(%s)" % bk.rng("clients", "guests"), "num",
                   sum(c["guests"] for c in demo.clients)),
        "quote": ("=SUM(%s)" % bk.rng("clients", "quote"), "money0",
                  sum(c["quote"] for c in demo.clients)),
        "deposit": ("=SUM(%s)" % bk.rng("clients", "deposit"), "money0",
                    sum(c["deposit"] for c in demo.clients)),
        "balance": ('=SUM(%s)-SUM(%s)'
                    % (bk.rng("clients", "quote"),
                       bk.rng("clients", "deposit")),
                    "money0", sum(c["quote"] - c["deposit"]
                                  for c in demo.clients)),
    }, first_col="B", last_col=LAST_COL, label="TOTALS",
        label_span=("B", "C"))

    common.note_block(
        bk, "clients", C.last_row("clients") + 3, 1, ci(LAST_COL) - 1, [
            "The Balance due column calculates itself (quote minus deposit) "
            "- type over the white cells only.",
            "Payment status drives the colours here and the receivables "
            "cards on the Dashboard."],
        title="How this tab works")

    bk.nav_row("clients", C.last_row("clients") + 8, first_col=1, span=2,
               max_col=LAST_COL)
    bk.page("clients", LAST_COL, C.last_row("clients") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    """Formulas that live in every row, blank build or demo build alike."""
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "balance": '=IF(OR($K%d="",$L%d=""),"",ROUND($K%d-$L%d,2))'
                   % (rownum, rownum, rownum, rownum),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["clients"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": i + 1, "balance": ""}
        if demo.demo and i < len(demo.clients):
            c = demo.clients[i]
            values.update(
                name=c["name"], phone=c["phone"], email=c["email"],
                event_date=c["event_date"], event_type=c["event_type"],
                guests=c["guests"], venue=c["venue"], package=c["package"],
                quote=c["quote"], deposit=c["deposit"],
                status=c["status"], notes=c["notes"])
            cached["n"] = i + 1
            cached["balance"] = round(c["quote"] - c["deposit"], 2)
        elif demo.demo:
            cached["n"] = ""
        else:
            cached["n"] = ""
        common.write_row(bk, "clients", COLUMNS, rownum, values, cached)
