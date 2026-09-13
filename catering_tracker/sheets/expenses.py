"""
Expenses: every rupee, dollar or dinar that leaves the business.

Categorised spending feeds the expense doughnut on the Dashboard, the food
cost / labor percentages, and the P&L - tag the event and the receipt so
year-end is a filter, not a hunt.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("date", "Date", "date", "gold"),
    ("vendor", "Vendor", "text", "accent"),
    ("category", "Category", "center", None),
    ("desc", "What / description", "wrap", None),
    ("amount", "Amount", "money", "bad"),
    ("method", "Paid by", "center", None),
    ("event", "Event", "center", None),
    ("receipt", "Receipt", "tick", "ok"),
]

LAST_COL = "J"


def build(bk):
    ws = bk.ws("expenses")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("expenses")
    bk.title_block("expenses", "Expenses",
                   "Every cost, categorised - the P&L builds itself from "
                   "here", LAST_COL)
    this_month = ('SUMPRODUCT((%s<>"")*(MONTH(%s)=MONTH(TODAY()))*'
                  '(YEAR(%s)=YEAR(TODAY()))*%s)'
                  % (bk.rng("expenses", "date"), bk.rng("expenses", "date"),
                     bk.rng("expenses", "date"), bk.rng("expenses", "amount")))
    bk.stats_strip("expenses", [
        ('="Total spend: "&Currency&TEXT(SUM(%s),"#,##0")'
         % bk.rng("expenses", "amount"), "bad",
         "Total spend: %s" % demo.money(bk.cached("expenses", 0))),
        ('="This month: "&Currency&TEXT(%s,"#,##0")' % this_month, "warn",
         "This month: %s" % demo.money(
             sum(x["amount"] for x in demo.expenses
                 if (x["date"].month, x["date"].year) == (9, 2026)))),
        ('="Food & packaging: "&Currency&TEXT(%s,"#,##0")'
         % bk.kpi("food_cost"), "gold",
         "Food & packaging: %s" % demo.money(bk.cached("food_cost", 0))),
        ('="No receipt: "&COUNTA(%s)-COUNTIF(%s,"%s")'
         % (bk.rng("expenses", "date"), bk.rng("expenses", "receipt"),
            C.TICK), "info",
         "No receipt: %d" % sum(1 for x in demo.expenses
                                if x["receipt"] != C.TICK)),
    ])

    common.table_frame(bk, "expenses", COLUMNS)
    _rows(bk)

    # validations
    common.list_dv(bk, "expenses", "category", "expense_categories",
                   title="Category",
                   message="Ingredients, Staff / Labor... (edit on Setup).")
    common.list_dv(bk, "expenses", "method", "payment_methods",
                   title="Paid by",
                   message="Cash, Bank Transfer... (edit on Setup).")
    ws.data_validation(
        r(C.ROW_FIRST), ci("I"), r(C.last_row("expenses")), ci("I"),
        {"validate": "list", "source": "=EventList", "ignore_blank": True,
         "show_input": True, "input_title": "Event",
         "input_message": "Tag the event this cost belongs to (optional "
                          "but gold at year-end)."})
    bk.stats["validations"] += 1
    common.date_dv(bk, "expenses", ["date"])
    common.money_dv(bk, "expenses", ["amount"])
    common.tick_dv(bk, "expenses", ["receipt"])

    # conditional formats
    common.tick_cf(bk, "expenses", ["receipt"])
    L = bk.col("expenses", "category")
    col = ci(L)
    bk.cond("expenses", C.ROW_FIRST, col, C.last_row("expenses"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",OR($%s%d="Ingredients",$%s%d='
                    '"Packaging"))'
                    % (L, C.ROW_FIRST, L, C.ROW_FIRST, L, C.ROW_FIRST),
        "format": S.cf(bg=th.gold_soft, fg=th.gold, bold=True)})
    L2 = bk.col("expenses", "amount")
    common.databar(bk, "expenses", "amount", color=th.bad)

    common.totals_row(bk, "expenses", C.last_row("expenses") + 1, {
        "amount": ("=SUM(%s)" % bk.rng("expenses", "amount"), "money0",
                   round(sum(x["amount"] for x in demo.expenses), 2)),
    }, first_col="B", last_col=LAST_COL, label="TOTAL SPEND",
        label_span=("B", "F"))

    common.note_block(
        bk, "expenses", C.last_row("expenses") + 3, 1, ci(LAST_COL) - 1, [
            "Categorising is what makes the Dashboard doughnut, the food "
            "cost % and the P&L work - pick from the dropdown rather than "
            "typing.",
            "Ingredients + Packaging count as food cost; everything else "
            "is operating cost in the P&L."],
        title="How this tab works")

    bk.nav_row("expenses", C.last_row("expenses") + 8, first_col=1,
               span=2, max_col=LAST_COL)
    bk.page("expenses", LAST_COL, C.last_row("expenses") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["expenses"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": ""}
        if demo.demo and i < len(demo.expenses):
            x = demo.expenses[i]
            values.update(
                date=x["date"], vendor=x["vendor"], category=x["category"],
                desc=x["desc"], amount=x["amount"], method=x["method"],
                event=x["event"], receipt=x["receipt"])
            cached["n"] = i + 1
        common.write_row(bk, "expenses", COLUMNS, rownum, values, cached)
