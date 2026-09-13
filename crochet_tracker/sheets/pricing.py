"""
Pricing Calculator - price one item properly.

Six inputs on the left (yarn, packaging, hours, wage, overhead, target
margin); the right side computes labour, overhead, true cost, the price
that hits your margin, a charm price (.95 / .99), and the profit inside
it. Wage, overhead and margin start from your Lists & Settings values.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "J"

_INPUTS = [
    (C.PR_IN["material"], "Yarn cost for this item", "money", None),
    (C.PR_IN["packaging"], "Packaging, labels, cards", "money", None),
    (C.PR_IN["hours"], "Hours to make", "qty1", None),
    (C.PR_IN["wage"], "Your hourly wage", "money", "=HourlyWage"),
    (C.PR_IN["overhead"], "Overhead %", "pct", "=OverheadPct"),
    (C.PR_IN["margin"], "Target profit margin", "pct", "=TargetMargin"),
]


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("pricing")
    demo = bk.demo
    pr = demo.agg["pricing"] if demo else None

    common.sheet_head(bk, "pricing", LAST_COL,
                      "\U0001F4B5  Pricing Calculator",
                      "Never underprice a hand-made item again")

    # --------------------------------------------------------- inputs
    ws.set_row(r(5), 22)
    bk.band("pricing", 5, 1, ci("F"), S.section, height=22)
    ws.write(r(5), 1, "  What goes into one item", S.section)
    for row, label, kind, default_formula in _INPUTS:
        ws.set_row(r(row), 26)
        ws.merge_range(r(row), ci("B"), r(row), ci("D"), label,
                       S.f(**S.base(
                           font_size=10.5, font_color=th.ink,
                           bg_color=th.card, align="left", valign="vcenter",
                           border=1, border_color=th.border, indent=1)))
        ws.merge_range(r(row), ci("E"), r(row), ci("F"), "", S.cell(kind))
        fmt = S.cell(kind)
        if demo:
            value = demo.pricing[{
                "material": "material", "packaging": "packaging",
                "hours": "hours", "wage": "wage", "overhead": "overhead",
                "margin": "margin"}[_key_for(row)]]
            ws.write(r(row), ci("E"), value, fmt)
        elif default_formula:
            cached = {"=HourlyWage": 15.0, "=OverheadPct": 0.10,
                      "=TargetMargin": 0.45}[default_formula]
            ws.write_formula(r(row), ci("E"), default_formula, fmt, cached)
            bk.stats["formulas"] += 1
        else:
            ws.write_blank(r(row), ci("E"), None, fmt)

    ws.data_validation(
        r(C.PR_IN["material"]), ci("E"), r(C.PR_IN["packaging"]), ci("E"),
        {"validate": "decimal", "criteria": ">=", "value": 0,
         "ignore_blank": True, "show_error": True,
         "error_title": "Enter a cost",
         "error_message": "A positive number, no currency symbol.",
         "error_type": "warning"})
    bk.stats["validations"] += 1
    ws.data_validation(
        r(C.PR_IN["hours"]), ci("E"), r(C.PR_IN["hours"]), ci("E"),
        {"validate": "decimal", "criteria": "between", "minimum": 0,
         "maximum": 1000, "ignore_blank": True, "show_error": True,
         "error_title": "Hours", "error_message": "e.g. 1.5",
         "error_type": "warning"})
    bk.stats["validations"] += 1
    for row in (C.PR_IN["wage"],):
        ws.data_validation(
            r(row), ci("E"), r(row), ci("E"),
            {"validate": "decimal", "criteria": "between", "minimum": 0,
             "maximum": 1000, "ignore_blank": True, "show_error": True,
             "error_title": "Wage", "error_message": "per hour, e.g. 14",
             "error_type": "warning"})
        bk.stats["validations"] += 1
    for row in (C.PR_IN["overhead"], C.PR_IN["margin"]):
        ws.data_validation(
            r(row), ci("E"), r(row), ci("E"),
            {"validate": "decimal", "criteria": "between", "minimum": 0,
             "maximum": 0.9, "ignore_blank": True, "show_error": True,
             "error_title": "Percentage",
             "error_message": "Between 0% and 90%.",
             "error_type": "warning"})
        bk.stats["validations"] += 1

    # -------------------------------------------------------- outputs
    ws.set_row(r(7), 22)
    bk.band("pricing", 7, ci("H") - 1, ci(LAST_COL), S.section_accent,
            height=22)
    ws.write(r(7), ci("H") - 1, "  What to charge", S.section_accent)
    outs = [
        (C.PR_OUT["labor"], "Your labour", "=N($E$%d)*N($E$%d)"
         % (C.PR_IN["hours"], C.PR_IN["wage"]), "calc_money",
         pr["labor"] if pr else 0, False),
        (C.PR_OUT["overhead_amt"], "Overhead", "=ROUND((N($E$%d)+N($E$%d)"
         "+$J$%d)*N($E$%d),2)" % (C.PR_IN["material"],
                                  C.PR_IN["packaging"],
                                  C.PR_OUT["labor"],
                                  C.PR_IN["overhead"]), "calc_money",
         pr["overhead_amt"] if pr else 0, False),
        (C.PR_OUT["true_cost"], "True cost to make", "=ROUND(N($E$%d)+"
         "N($E$%d)+$J$%d+$J$%d,2)" % (C.PR_IN["material"],
                                      C.PR_IN["packaging"],
                                      C.PR_OUT["labor"],
                                      C.PR_OUT["overhead_amt"]),
         "calc_money", pr["true_cost"] if pr else 0, False),
        (C.PR_OUT["price"], "Price at your margin",
         "=IF(N($E$%d)>=1,0,ROUND($J$%d/(1-N($E$%d)),2))"
         % (C.PR_IN["margin"], C.PR_OUT["true_cost"],
            C.PR_IN["margin"]), "calc_money",
         pr["price"] if pr else 0, True),
        (C.PR_OUT["charm"], "Charm price (\u2026.95)",
         "=IF($J$%d<=0,0,CEILING($J$%d,1)-0.05)" % (C.PR_OUT["price"],
                                                    C.PR_OUT["price"]),
         "calc_money", pr["charm"] if pr else 0, False),
        (C.PR_OUT["profit"], "Profit per item", "=ROUND($J$%d-$J$%d,2)"
         % (C.PR_OUT["price"], C.PR_OUT["true_cost"]), "calc_money",
         pr["profit"] if pr else 0, False),
        (C.PR_OUT["check"], "Margin check", "=IFERROR($J$%d/$J$%d,0)"
         % (C.PR_OUT["profit"], C.PR_OUT["price"]), "calc_pct1",
         pr["margin"] if pr else 0, False),
    ]
    for row, label, formula, kind, cached, big in outs:
        ws.set_row(r(row), 26)
        ws.merge_range(r(row), ci("G"), r(row), ci("I"), label,
                       S.f(**S.base(
                           font_size=10.5 if not big else 12,
                           bold=big, font_color=th.ink, bg_color=th.card,
                           align="left", valign="vcenter", border=1,
                           border_color=th.border, indent=1)))
        if big:
            fmt = S.f(**S.base(
                font_size=16, bold=True, font_color=th.primary,
                bg_color=th.primary_soft, align="center", valign="vcenter",
                border=1, border_color=th.border, locked=True,
                num_format="#,##0.00"))
        else:
            fmt = S.cell(kind)
        ws.write_formula(r(row), ci("J"), formula, fmt, cached)
        bk.stats["formulas"] += 1

    # CF: margin check below target glows amber
    colj = ci("J")
    bk.cond("pricing", r(C.PR_OUT["check"]), colj, r(C.PR_OUT["check"]),
            colj, {
                "type": "formula",
                "criteria": "=$J$%d<$E$%d" % (C.PR_OUT["check"],
                                              C.PR_IN["margin"]),
                "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    bk.cond("pricing", r(C.PR_OUT["check"]), colj, r(C.PR_OUT["check"]),
            colj, {
                "type": "formula",
                "criteria": "=$J$%d>=$E$%d" % (C.PR_OUT["check"],
                                               C.PR_IN["margin"]),
                "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True)})

    # ---------------------------------------------------------- notes
    common.note_block(
        bk, "pricing", 23, 1, ci(LAST_COL), [
            "True cost = yarn + packaging + your labour + overhead. The "
            "suggested price is true cost divided by (1 - margin), the "
            "classic retail formula.",
            "The charm price rounds up to the nearest .95 - prices ending "
            "in 5 or 9 feel friendlier and keep the difference in your "
            "pocket.",
            "Wage, overhead and margin start from your Lists & Settings "
            "values - overwrite them here any time for a one-off item.",
        ], title="  How to use it")

    common.footer_nav(
        bk, "pricing", 28, LAST_COL,
        tip="  \U0001F4A1  A quick sanity check: if the suggested price "
            "makes you wince, your hours or wage are telling you something.",
        zoom=100)


def _key_for(row):
    return {C.PR_IN["material"]: "material",
            C.PR_IN["packaging"]: "packaging",
            C.PR_IN["hours"]: "hours", C.PR_IN["wage"]: "wage",
            C.PR_IN["overhead"]: "overhead",
            C.PR_IN["margin"]: "margin"}[row]
