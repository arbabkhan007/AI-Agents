"""
The Events tab: the production calendar of the whole business.

One row per booking.  Profit, margin and balance calculate themselves from
cost / price / deposit, the status pipeline drives the colours and the
Pipeline doughnut on the Dashboard, and the date column glows amber inside
your "due soon" window and red once an uncompleted event has passed.
"""

from .. import config as C
from ..book import r, ci
from . import common

COLUMNS = [
    ("n", "#", "idx", None),
    ("id", "Event ID", "center", None),
    ("client", "Client", "text", "accent"),
    ("date", "Date", "date", "gold"),
    ("type", "Type", "center", None),
    ("guests", "Guests", "qty", None),
    ("menu", "Menu / dishes", "wrap", None),
    ("staff_req", "Crew", "qty", None),
    ("equipment_req", "Equipment needed", "wrap", None),
    ("cost", "Cost", "money", "bad"),
    ("price", "Price", "money", "ok"),
    ("profit", "Profit", "calc_money", None),
    ("margin", "Margin", "calc_pct", None),
    ("deposit", "Deposit", "money", None),
    ("balance", "Balance", "calc_money", None),
    ("status", "Status", "center", "warn"),
    ("notes", "Notes", "wrap", None),
]

LAST_COL = "R"


def build(bk):
    ws = bk.ws("events")
    S, th = bk.S, bk.th
    demo = bk.demo

    bk.widths("events")
    bk.title_block("events", "Events",
                   "Every booking - costs, pricing and profit per event",
                   LAST_COL)
    # COUNTIF(range,"<>x") counts blank cells too in Excel; SUMPRODUCT
    # over non-blank statuses gives the real active-booking count.
    live = ('SUMPRODUCT((%s<>"")*(%s<>"%s"))'
            % (bk.rng("events", "status"), bk.rng("events", "status"),
               C.ES_CANCEL))
    booked = (" + ".join('COUNTIF(%s,"%s")'
                         % (bk.rng("events", "status"), s)
                         for s in (C.ES_QUOTED, C.ES_DEPOSIT, C.ES_CONFIRMED,
                                   C.ES_DONE)))
    bk.stats_strip("events", [
        ('="Bookings: "&%s' % live, "accent",
         "Bookings: %d" % (demo.agg.get("events_total", 0)
                           - demo.agg.get("events_cancelled", 0))
         if demo.demo else "Bookings: 0"),
        ('="In the pipeline: "&%s' % booked, "info",
         "In the pipeline: %d" % sum(
             1 for e in demo.events if e["status"] in
             (C.ES_QUOTED, C.ES_DEPOSIT, C.ES_CONFIRMED, C.ES_DONE))
         if demo.demo else "In the pipeline: 0"),
        ('="Booked value: "&Currency&TEXT(SUMPRODUCT((%s<>"%s")*%s),"#,##0")'
         % (bk.rng("events", "status"), C.ES_CANCEL,
            bk.rng("events", "price")), "ok",
         "Booked value: %s" % demo.money(
             sum(e["price"] for e in demo.events
                 if e["status"] != C.ES_CANCEL))),
        ('="Expected profit: "&Currency&TEXT(SUMPRODUCT((%s<>"%s")*%s)'
         '-SUMPRODUCT((%s<>"%s")*%s),"#,##0")'
         % (bk.rng("events", "status"), C.ES_CANCEL,
            bk.rng("events", "price"),
            bk.rng("events", "status"), C.ES_CANCEL,
            bk.rng("events", "cost")), "gold",
         "Expected profit: %s" % demo.money(
             sum(e["profit"] for e in demo.events
                 if e["status"] != C.ES_CANCEL))),
    ])

    common.table_frame(bk, "events", COLUMNS)
    _rows(bk)

    # validations
    common.list_dv(bk, "events", "type", "event_types", title="Event type",
                   message="Pick from your list (edit it on Setup).")
    common.fixed_dv(bk, "events", "status", "EventStatuses",
                    title="Status",
                    message="Inquiry \u2192 Quote sent \u2192 Deposit paid "
                            "\u2192 Confirmed \u2192 Completed.")
    ws.data_validation(
        r(C.ROW_FIRST), ci("D"), r(C.last_row("events")), ci("D"),
        {"validate": "list", "source": "=ClientsList", "ignore_blank": True,
         "show_input": True, "input_title": "Client",
         "input_message": "Pick a client from the Clients tab (or type a "
                          "new name and add them there)."})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(C.ROW_FIRST), ci("H"), r(C.last_row("events")), ci("H"),
        {"validate": "list", "source": "=MenuItems", "ignore_blank": True,
         "show_input": True, "input_title": "Menu",
         "input_message": "Pick a dish from Menu Costing, or type a "
                          "combination (comma separated).",
         "show_error": True, "error_title": "Not on the menu list",
         "error_message": "That's not one of your priced menu items - "
                          "continue anyway?", "error_type": "warning"})
    bk.stats["validations"] += 1
    common.date_dv(bk, "events", ["date"])
    common.whole_dv(bk, "events", ["guests", "staff_req"], 0, 100000)
    common.money_dv(bk, "events", ["cost", "price", "deposit"])

    # conditional formats
    common.status_cf(bk, "events", "status", {
        C.ES_INQUIRY: (th.info_soft, th.info),
        C.ES_QUOTED: (th.plum_soft, th.plum),
        C.ES_DEPOSIT: (th.warn_soft, th.warn),
        C.ES_CONFIRMED: (th.ok_soft, th.ok),
        C.ES_DONE: (th.gold_soft, th.gold),
        C.ES_CANCEL: (th.bad_soft, th.bad),
    })
    L = bk.col("events", "date")
    col = ci(L)
    first, last = C.ROW_FIRST, C.last_row("events")
    bk.cond("events", first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<TODAY(),$%s%d<>"%s",$%s%d<>"%s")'
                    % (L, first, L, first, bk.col("events", "status"), first,
                       C.ES_DONE, bk.col("events", "status"), first,
                       C.ES_CANCEL),
        "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond("events", first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d>=TODAY(),$%s%d-TODAY()<=DueSoonDays)'
                    % (L, first, L, first, L, first),
        "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    common.databar(bk, "events", "margin", color=th.primary_2)

    # totals
    common.totals_row(bk, "events", C.last_row("events") + 1, {
        # comma form: SUMPRODUCT treats non-numeric entries ("" formulas in
        # the profit column, blank cells) as zeros instead of #VALUE!.
        "guests": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                   % (bk.rng("events", "date"), bk.rng("events", "guests")),
                   "num", sum(e["guests"] for e in demo.events)),
        "staff_req": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                      % (bk.rng("events", "date"),
                         bk.rng("events", "staff_req")),
                      "num", sum(e["staff_req"] for e in demo.events)),
        "cost": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                 % (bk.rng("events", "date"), bk.rng("events", "cost")),
                 "money0", sum(e["cost"] for e in demo.events)),
        "price": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                  % (bk.rng("events", "date"), bk.rng("events", "price")),
                  "money0", sum(e["price"] for e in demo.events)),
        "profit": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                   % (bk.rng("events", "date"), bk.rng("events", "profit")),
                   "money0", sum(e["profit"] for e in demo.events)),
        "deposit": ("=SUMPRODUCT(--(%s<>\"\"),%s)"
                    % (bk.rng("events", "date"),
                       bk.rng("events", "deposit")),
                    "money0", sum(e["deposit"] for e in demo.events)),
        "balance": ("=SUM(%s)-SUM(%s)"
                    % (bk.rng("events", "price"),
                       bk.rng("events", "deposit")),
                    "money0", sum(e["price"] - e["deposit"]
                                  for e in demo.events)),
    }, first_col="B", last_col=LAST_COL, label="TOTALS",
        label_span=("B", "C"))

    common.note_block(
        bk, "events", C.last_row("events") + 3, 1, ci(LAST_COL) - 1, [
            "Profit, Margin and Balance calculate themselves - never type "
            "in the tinted columns.",
            "The Status pipeline feeds the Pipeline doughnut on the "
            "Dashboard; dates go amber inside your due-soon window and red "
            "once a live event has passed."],
        title="How this tab works")

    bk.nav_row("events", C.last_row("events") + 8, first_col=1, span=2,
               max_col=LAST_COL)
    bk.page("events", LAST_COL, C.last_row("events") + 10,
            freeze=(7, 2), title_rows=(6, 6))


def _calc_formulas(rownum):
    return {
        "n": '=IF($C%d="","",ROW()-%d)' % (rownum, C.ROW_FIRST - 1),
        "profit": '=IF(OR($K%d="",$L%d=""),"",ROUND($L%d-$K%d,2))'
                  % (rownum, rownum, rownum, rownum),
        "margin": '=IFERROR(IF($M%d="","",$M%d/$L%d),"")'
                  % (rownum, rownum, rownum),
        "balance": '=IF($L%d="","",ROUND($L%d-$O%d,2))'
                   % (rownum, rownum, rownum),
    }


def _rows(bk):
    demo = bk.demo
    for i in range(C.CAP["events"]):
        rownum = C.ROW_FIRST + i
        values = dict(_calc_formulas(rownum))
        cached = {"n": "", "profit": "", "margin": "", "balance": ""}
        if demo.demo and i < len(demo.events):
            e = demo.events[i]
            values.update(
                id=e["id"], client=e["client"], date=e["date"],
                type=e["type"], guests=e["guests"], menu=e["menu"],
                staff_req=e["staff_req"], equipment_req=e["equipment_req"],
                cost=e["cost"], price=e["price"], deposit=e["deposit"],
                status=e["status"], notes=e["notes"])
            cached.update(n=i + 1, profit=round(e["profit"], 2),
                          margin=e["margin"], balance=round(e["balance"], 2))
        common.write_row(bk, "events", COLUMNS, rownum, values, cached)
