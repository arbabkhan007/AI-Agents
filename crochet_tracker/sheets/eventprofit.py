"""
Event Profit - the "was this fair worth it?" tab.

Pick a fair from the dropdown; the tab pulls its sales, costs and stock
movement from the other tabs and works out gross profit, true cost, net,
breakeven and return on investment.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "J"


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("eventprofit")
    demo = bk.demo
    ep = demo.agg["event_profit"] if demo else None

    common.sheet_head(
        bk, "eventprofit", LAST_COL, "\U0001F9EE  Event Profit",
        "Pick a craft fair and see exactly what it earned you")

    # ---------------------------------------------------- fair picker
    ws.set_row(r(5), 22)
    bk.band("eventprofit", 5, 1, ci(LAST_COL), S.section, height=22)
    ws.write(r(5), 1, "  Pick a craft fair", S.section)
    ws.set_row(r(C.EP_EVENT_ROW), 30)
    ws.write(r(C.EP_EVENT_ROW), ci("B"), "Craft fair:", S.f(**S.base(
        font_size=12, bold=True, font_color=th.ink, bg_color=th.card,
        align="left", valign="vcenter", border=1, border_color=th.border,
        indent=1)))
    ws.merge_range(r(C.EP_EVENT_ROW), ci("C"), r(C.EP_EVENT_ROW),
                   ci(LAST_COL), "", S.f(**S.base(
                       font_size=13, bold=True, font_color=th.primary,
                       bg_color=th.card, align="left", valign="vcenter",
                       border=1, border_color=th.border, indent=1,
                       locked=False)))
    ws.data_validation(
        r(C.EP_EVENT_ROW), ci("C"), r(C.EP_EVENT_ROW), ci("C"),
        {"validate": "list", "source": "=EventList", "ignore_blank": True,
         "show_input": True, "input_title": "Craft fair",
         "input_message": "Pick one of your fairs from the Craft Fairs "
                          "tab.", "show_error": True,
         "error_title": "Pick from the list",
         "error_message": "Choose a fair you've entered on the Craft Fairs "
                          "tab.", "error_type": "warning"})
    bk.stats["validations"] += 1
    if ep:
        ws.write(r(C.EP_EVENT_ROW), ci("C"), ep["event"], S.f(**S.base(
            font_size=13, bold=True, font_color=th.primary,
            bg_color=th.card, align="left", valign="vcenter", border=1,
            border_color=th.border, indent=1, locked=False)))

    E8 = "$C$%d" % C.EP_EVENT_ROW

    def block(title, rows, band_fmt, first_row):
        """rows = list of (label, formula, cached, kind)."""
        ws.set_row(r(first_row - 1), 22)
        bk.band("eventprofit", first_row - 1, 1, ci(LAST_COL), band_fmt,
                height=22)
        ws.write(r(first_row - 1), 1, "  " + title, band_fmt)
        for i, (label, formula, cached, kind) in enumerate(rows):
            row = first_row + i
            ws.set_row(r(row), 24)
            ws.merge_range(r(row), ci("B"), r(row), ci("D"), label,
                           S.f(**S.base(
                               font_size=10.5, bold=False, font_color=th.ink,
                               bg_color=th.card, align="left",
                               valign="vcenter", border=1,
                               border_color=th.border, indent=1)))
            fmt = S.cell(kind)
            ws.write_formula(r(row), ci("E"), formula, fmt, cached)
            bk.stats["formulas"] += 1
            ws.merge_range(r(row), ci("F"), r(row), ci(LAST_COL), "",
                           S.canvas)
        return first_row + len(rows)

    # ------------------------------------------------------ money in
    def s(field, extra=""):
        return 'SUMIFS(%s,%s,%s%s)' % (bk.rng("sales", field),
                                       bk.rng("sales", "event"), E8, extra)

    def ev(field):
        return 'INDEX(%s,MATCH(%s,%s,0))' % (bk.rng("events", field), E8,
                                             bk.rng("events", "name"))

    ws.set_row(r(C.EP_REV["units"] - 1), 22)
    block("Money in", [
        ("Items sold", '=IF(%s="",0,%s)' % (E8, s("qty")),
         ep["units"] if ep else 0, "calc_num"),
        ("Gross sales", '=IF(%s="",0,%s)' % (E8, s("total")),
         ep["gross"] if ep else 0, "calc_money"),
        ("Discounts given", '=IF(%s="",0,%s)' % (E8, s("discount")),
         ep["discounts"] if ep else 0, "calc_money"),
    ], S.section, C.EP_REV["units"])

    # ----------------------------------------------------- money out
    block("Money out", [
        ("Cost of goods sold", '=IF(%s="",0,%s)' % (E8, s("cost")),
         ep["cogs"] if ep else 0, "calc_money"),
        ("Booth fee", '=IFERROR(IF(%s="",0,%s),0)' % (E8, ev("booth")),
         ep["booth"] if ep else 0, "calc_money"),
        ("Travel", '=IFERROR(IF(%s="",0,%s),0)' % (E8, ev("travel")),
         ep["travel"] if ep else 0, "calc_money"),
        ("Parking", '=IFERROR(IF(%s="",0,%s),0)' % (E8, ev("parking")),
         ep["parking"] if ep else 0, "calc_money"),
        ("Food & drinks", '=IFERROR(IF(%s="",0,%s),0)' % (E8, ev("food")),
         ep["food"] if ep else 0, "calc_money"),
        ("Display & decor", '=IFERROR(IF(%s="",0,%s),0)' % (E8, ev("display")),
         ep["display"] if ep else 0, "calc_money"),
    ], S.section_accent, C.EP_COST["cogs"])

    # -------------------------------------------------------- verdict
    ws.set_row(r(C.EP_OUT["gross_profit"] - 1), 22)
    bk.band("eventprofit", C.EP_OUT["gross_profit"] - 1, 1, ci(LAST_COL),
            S.section_gold, height=22)
    ws.write(r(C.EP_OUT["gross_profit"] - 1), 1, "  The verdict",
             S.section_gold)
    verdict_rows = [
        ("Gross profit (sales - goods)",
         '=IF(%s="",0,ROUND($E$%d-$E$%d,2))'
         % (E8, C.EP_REV["gross"], C.EP_COST["cogs"]),
         ep["gross_profit"] if ep else 0, "calc_money", False),
        ("True cost of the fair",
         '=IF(%s="",0,ROUND(SUM($E$%d:$E$%d),2))'
         % (E8, C.EP_COST["cogs"], C.EP_COST["display"]),
         ep["total_cost"] if ep else 0, "calc_money", False),
        ("Net profit", '=IF(%s="",0,ROUND($E$%d-$E$%d,2))'
         % (E8, C.EP_REV["gross"], C.EP_OUT["total_cost"]),
         ep["net"] if ep else 0, "calc_money", True),
        ("Profit margin", '=IF(%s="",0,IFERROR($E$%d/$E$%d,0))'
         % (E8, C.EP_OUT["net"], C.EP_REV["gross"]),
         ep["margin"] if ep else 0, "calc_pct1", False),
        ("Average sale", '=IF(%s="",0,IFERROR($E$%d/COUNTIFS(%s,%s),0))'
         % (E8, C.EP_REV["gross"], bk.rng("sales", "event"), E8),
         ep["avg_sale"] if ep else 0, "calc_money", False),
        ("Breakeven sales",
         '=IF(%s="",0,IFERROR(ROUND($E$%d/($E$%d/$E$%d),2),0))'
         % (E8, C.EP_OUT["total_cost"], C.EP_OUT["gross_profit"],
            C.EP_REV["gross"]),
         ep["breakeven"] if ep else 0, "calc_money", False),
        ("Return on investment",
         '=IF(%s="",0,IFERROR($E$%d/$E$%d,0))'
         % (E8, C.EP_OUT["net"], C.EP_OUT["total_cost"]),
         ep["roi"] if ep else 0, "calc_pct1", False),
    ]
    for i, (label, formula, cached, kind, big) in enumerate(verdict_rows):
        row = C.EP_OUT["gross_profit"] + i
        ws.set_row(r(row), 24)
        ws.merge_range(r(row), ci("B"), r(row), ci("D"), label,
                       S.f(**S.base(
                           font_size=10.5 if not big else 12,
                           bold=big, font_color=th.ink, bg_color=th.card,
                           align="left", valign="vcenter", border=1,
                           border_color=th.border, indent=1)))
        fmt = S.cell(kind) if not big else S.f(**S.base(
            font_size=15, bold=True, font_color=th.primary,
            bg_color=th.primary_soft, align="right", valign="vcenter",
            border=1, border_color=th.border, locked=True,
            num_format="#,##0.00"))
        ws.write_formula(r(row), ci("E"), formula, fmt, cached)
        bk.stats["formulas"] += 1
        if row != C.EP_OUT["net"]:
            ws.merge_range(r(row), ci("F"), r(row), ci(LAST_COL), "",
                           S.canvas)

    # verdict banner: net profit big card at F..J on the net row
    net_row = C.EP_OUT["net"]
    net_fmt = S.kpi_value(th.ok if not demo or ep["net"] >= 0 else th.bad,
                          num_format="#,##0.00", size=18, align="center")
    ws.merge_range(r(net_row), ci("F"), r(net_row), ci(LAST_COL), "",
                   net_fmt)
    ws.write_formula(r(net_row), ci("F"),
                     '=IF(%s="","",Currency&TEXT($E$%d,"#,##0.00"))'
                     % (E8, net_row), net_fmt,
                     ("%s%s" % (demo.settings["currency"],
                                format(ep["net"], ",.2f"))) if ep else "")

    # CF: net < 0 red
    col_e = ci("E")
    for rr in (C.EP_OUT["gross_profit"], C.EP_OUT["total_cost"],
               C.EP_OUT["net"]):
        bk.cond("eventprofit", r(rr), col_e, r(rr), col_e, {
            "type": "cell", "criteria": "<", "value": 0,
            "format": S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})

    # ---------------------------------------------------------- notes
    nrow = C.EP_LAST_ROW + 1
    common.note_block(
        bk, "eventprofit", nrow, 1, ci(LAST_COL), [
            "Gross profit = sales - cost of goods. True cost adds the "
            "booth, travel, parking, food and display you logged on the "
            "Craft Fairs tab.",
            "Breakeven is the sales figure where the fair stops costing "
            "you money - anything above it is profit.",
            "Return on investment: for every 1 of fair cost, how much "
            "profit came back. Above 100% = a very good day.",
        ], title="  Reading the numbers")

    common.footer_nav(
        bk, "eventprofit", nrow + 5, LAST_COL,
        tip="  \U0001F4A1  Every number here is pulled live from your "
            "Sales Log and Craft Fairs tabs - nothing to re-type.",
        zoom=95)
