"""
Craft Fairs - every fair on the books.

Type the fair's name, date and what it costs you; sales, cost of goods and
net profit pull themselves from the Sales Log. The fair names here feed the
dropdowns everywhere else.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "R"

_COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Craft fair", "text", None),
    ("date", "Date", "date", None),
    ("location", "Location", "text", None),
    ("organizer", "Organiser", "text", None),
    ("booth", "Booth fee", "money", None),
    ("travel", "Travel", "money", None),
    ("parking", "Parking", "money", None),
    ("food", "Food", "money", None),
    ("display", "Display", "money", None),
    ("total", "Fair cost", "calc_money", None),
    ("taken", "Items taken", "qty", None),
    ("sold", "Items sold", "calc_qty", None),
    ("sales", "Sales", "calc_money", None),
    ("cogs", "Cost of goods", "calc_money", None),
    ("net", "Net profit", "calc_money", None),
    ("margin", "Margin", "calc_pct1", None),
    ("best", "Top seller (fill in)", "text", None),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("events")
    demo = bk.demo

    common.sheet_head(bk, "events", LAST_COL, "\U0001F3EA  Craft Fairs",
                      "Book the fair, log the costs - the profit maths runs "
                      "itself")

    evs = demo.events if demo else []
    common.chips(bk, "events", [
        ('="Fairs booked: "&TEXT(COUNTA(%s),"0")' % bk.rng("events", "name"),
         "gold", "Fairs booked: %d" % len(evs), 3),
        ('="Fair costs: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("events", "total"), "warn",
         "Fair costs: %s%s" % (demo.settings["currency"] if demo else "$",
                               format(sum(e["total"] for e in evs), ",.2f")),
         3),
        ('="Sales: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("events", "sales"), "ok",
         "Sales: %s%s" % (demo.settings["currency"] if demo else "$",
                          format(sum(e["sales"] for e in evs), ",.2f")), 3),
        ('="Net: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % bk.rng("events", "net"), "info",
         "Net: %s%s" % (demo.settings["currency"] if demo else "$",
                        format(sum(e["net"] for e in evs), ",.2f")), 3),
    ])

    common.table_frame(bk, "events", _COLUMNS, height=22)

    for i in range(common.n_rows("events")):
        rownum = common.first_row() + i
        e = evs[i] if i < len(evs) else None
        values, cached = _row_values(bk, rownum, e)
        common.write_row(bk, "events", _COLUMNS, rownum, values, cached)

    trow = common.last_row("events") + 2
    common.totals_row(bk, "events", trow, {
        "total": ('=SUM(%s)' % bk.rng("events", "total"), "#,##0.00",
                  round(sum(e["total"] for e in evs), 2)),
        "taken": ('=SUM(%s)' % bk.rng("events", "taken"), "#,##0",
                  sum(e["taken"] for e in evs)),
        "sold": ('=SUM(%s)' % bk.rng("events", "sold"), "#,##0",
                 sum(e["sold"] for e in evs)),
        "sales": ('=SUM(%s)' % bk.rng("events", "sales"), "#,##0.00",
                  round(sum(e["sales"] for e in evs), 2)),
        "cogs": ('=SUM(%s)' % bk.rng("events", "cogs"), "#,##0.00",
                 round(sum(e["cogs"] for e in evs), 2)),
        "net": ('=SUM(%s)' % bk.rng("events", "net"), "#,##0.00",
                round(sum(e["net"] for e in evs), 2)),
    }, first_col="B", label="TOTALS", label_span=("C", "E"))

    common.date_dv(bk, "events", ["date"])
    common.money_dv(bk, "events", ["booth", "travel", "parking", "food",
                                   "display"])
    common.whole_dv(bk, "events", ["taken"], 0, 9999)

    # net < 0 glows red; strong nets glow green
    L = bk.col("events", "net")
    col = ci(L)
    bk.cond("events", C.ROW_FIRST, col, C.last_row("events"), col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<0)' % (bk.col("events", "name"),
                                                 C.ROW_FIRST, L,
                                                 C.ROW_FIRST),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond("events", C.ROW_FIRST, col, C.last_row("events"), col, {
        "type": "formula",
        "criteria": '=$%s%d>0' % (L, C.ROW_FIRST),
        "format": bk.S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})

    nrow = trow + 2
    common.note_block(
        bk, "events", nrow, 1, ci(LAST_COL), [
            "Fair cost adds up the five expense columns; Sales, cost of "
            "goods and net profit pull straight from the Sales Log.",
            "Net = sales - fair cost - cost of goods. Red means that fair "
            "lost money - worth knowing before you book it again!",
            "The fair names you type here power the dropdowns on the Sales "
            "Log, Event Profit and Packing tabs.",
        ], title="  How this tab works")

    common.footer_nav(bk, "events", nrow + 5, LAST_COL, zoom=80)


# ---------------------------------------------------------------------------
def _row_values(bk, rownum, e):
    col = bk.col
    ev = "events"
    values = dict.fromkeys([c[0] for c in _COLUMNS], None)
    values["total"] = ('=IF(${n}{row}="","",ROUND(N(${b}{row})+N(${t}{row})'
                       '+N(${p}{row})+N(${f}{row})+N(${d}{row}),2))'
                       .format(n=col(ev, "name"), row=rownum,
                               b=col(ev, "booth"), t=col(ev, "travel"),
                               p=col(ev, "parking"), f=col(ev, "food"),
                               d=col(ev, "display")))
    values["sold"] = ('=IF(${n}{row}="","",SUMIFS({q},{ev},${n}{row}))'
                      .format(n=col(ev, "name"), row=rownum,
                              q=bk.rng("sales", "qty"),
                              ev=bk.rng("sales", "event")))
    values["sales"] = ('=IF(${n}{row}="","",SUMIFS({t},{ev},${n}{row}))'
                       .format(n=col(ev, "name"), row=rownum,
                              t=bk.rng("sales", "total"),
                              ev=bk.rng("sales", "event")))
    values["cogs"] = ('=IF(${n}{row}="","",SUMIFS({c},{ev},${n}{row}))'
                      .format(n=col(ev, "name"), row=rownum,
                              c=bk.rng("sales", "cost"),
                              ev=bk.rng("sales", "event")))
    values["net"] = ('=IF(${n}{row}="","",ROUND(${s}{row}-${tc}{row}'
                     '-${c}{row},2))'
                     .format(n=col(ev, "name"), row=rownum,
                             s=col(ev, "sales"), tc=col(ev, "total"),
                             c=col(ev, "cogs")))
    values["margin"] = ('=IF(OR(${n}{row}="",${s}{row}=0),"",IFERROR(${ne}'
                        '{row}/${s}{row},0))'
                        .format(n=col(ev, "name"), row=rownum,
                                s=col(ev, "sales"), ne=col(ev, "net")))
    cached = dict.fromkeys(values.keys(), 0)
    if e:
        values.update(name=e["name"], date=e["date"],
                      location=e["location"], organizer=e["organizer"],
                      booth=e["booth"], travel=e["travel"],
                      parking=e["parking"], food=e["food"],
                      display=e["display"], taken=e["taken"],
                      best=e["best"])
        cached.update(total=e["total"], sold=e["sold"], sales=e["sales"],
                      cogs=e["cogs"], net=e["net"], margin=e["margin"])
    return values, cached
