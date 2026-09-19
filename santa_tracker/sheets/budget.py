"""💰 Budget Tracker - min/max rules, actual spend, receipts."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "budget"
LAST_COL = "I"

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Gift for (recipient)", "text", None),
    ("min", "Min", "calc_money", None),
    ("max", "Max", "calc_money", None),
    ("spent", "Actual spent", "money", None),
    ("flag", "Budget check", "calc_wrap", None),
    ("receipt", "Receipt?", "tick", None),
    ("ref", "Receipt / order ref", "center", None),
    ("notes", "Notes", "wrap", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F4B0  Budget Tracker",
                 "One row per giver: what they spent on their Secret Santa "
                 "gift, checked against the party's min and max.")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    flagf = bk.S.f(**bk.S.base(font_size=9.5, font_color=th.ink,
                               bg_color=th.alt, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border, text_wrap=True))
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        values = {
            "n": i + 1,
            "name": '=IF(%s!$C$%d="","",%s!$C$%d)'
                    % (bk.q("draw"), row, bk.q("draw"), row),
            "min": "=BudgetMin",
            "max": "=BudgetMax",
            "spent": "",
            "flag": '=IF($E{r}="","",IF($E{r}<$C{r},"%s",IF($E{r}>$D{r},"%s",'
                    '"%s")))' % (C.BF_UNDER, C.BF_OVER, C.BF_OK),
            "receipt": "",
            "ref": "",
            "notes": "",
        }
        cached = {}
        if m and i < len(m.people):
            cached = {"name": m.assign[i], "min": m.settings["bmin"],
                      "max": m.settings["bmax"],
                      "flag": ("" if not m.spent[i] else
                               (C.BF_UNDER if m.spent[i] < m.settings["bmin"]
                                else C.BF_OVER if m.spent[i]
                                > m.settings["bmax"] else C.BF_OK))}
            values["spent"] = m.spent[i] or ""
            values["receipt"] = m.receipts[i]
            values["ref"] = m.refs[i]
        elif m:
            cached = {"name": "", "min": m.settings["bmin"],
                      "max": m.settings["bmax"], "flag": ""}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        ws.write_formula(r(row), ci("F"),
                         values["flag"].format(r=row), flagf,
                         cached.get("flag", ""))
        bk.stats["formulas"] += 1

    K.money_dv(bk, KEY, ("spent",))
    K.tick_dv(bk, KEY, ("receipt",))
    K.tick_cf(bk, KEY, ("receipt",))
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_OVER),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_UNDER),
        "format": bk.S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=$F%d="%s"' % (C.ROW_FIRST, C.BF_OK),
        "format": bk.S.cf(bg=th.ok_soft, fg=th.ok)})

    tot = C.last_row(KEY) + 1
    K.totals_row(bk, KEY, tot, {
        "spent": ("=SUM(E%d:E%d)" % (C.ROW_FIRST, C.last_row(KEY)),
                  "#,##0.00", m.agg["spent"] if m else 0)},
        first_col="B", last_col=LAST_COL)

    sp = "$E$%d:$E$%d" % (C.ROW_FIRST, C.last_row(KEY))
    fl = "$F$%d:$F$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F4B8 Total spent: "&Currency&TEXT(SUM(%s),"#,##0.00")'
         % sp, "primary",
         "Total spent: %s" % (m.money(m.agg["spent"]) if m else "$0.00"), 4),
        ('="\U0001F4CA Average gift: "&Currency&TEXT(%s,"#,##0.00")'
         % bk.kpi("avg_gift"), "info",
         "Average gift: %s" % (m.money(m.agg["avg_gift"]) if m else "$0.00"),
         4),
        ('="\U0001F6A8 Over budget: "&COUNTIF(%s,"%s")' % (fl, C.BF_OVER),
         "bad", "Over budget: %d" % (m.agg["over_budget"] if m else 0), 3),
        ('="\U0001F9FE Receipts filed: "&COUNTIF($G$%d:$G$%d,"%s")'
         % (C.ROW_FIRST, C.last_row(KEY), C.TICK), "ok",
         "Receipts filed: %d" % (sum(1 for x in (m.receipts if m else [])
                                     if x),), 3),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, tot + 2, LAST_COL)
