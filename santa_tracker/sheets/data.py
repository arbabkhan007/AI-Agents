"""_Data - the hidden calculation engine (KPIs for the dashboard)."""

from .. import config as C
from ..book import r, ci


def build(bk):
    key = "data"
    ws = bk.ws(key)
    for col, width in (("A", 3), ("AH", 26), ("AI", 12)):
        ws.set_column(ci(col), ci(col), width)
    m = bk.demo
    premium = bk.has("we")
    has_rules = bk.has("rules")

    hdr = bk.S.f(**bk.S.base(font_size=9, bold=True, font_color=bk.th.white,
                             bg_color=bk.th.muted, align="center",
                             valign="vcenter"))
    ws.write(r(1), ci("AH"), "Metric", hdr)
    ws.write(r(1), ci("AI"), "Value", hdr)

    names = bk.rng("participants", "name")
    rsvp = bk.rng("participants", "rsvp")
    diet = bk.rng("participants", "diet")
    status = bk.rng("participants", "status")
    dfinal = bk.rng("draw", "final")
    dflag = bk.rng("draw", "flag")
    bspent = bk.rng("budget", "spent")
    bflag = bk.rng("budget", "flag")

    F = {}
    F["participants"] = ("=COUNTA(%s)" % names, "#,##0")
    F["rsvp_yes"] = ('=COUNTIF(%s,"Yes")' % rsvp, "#,##0")
    F["rsvp_pending"] = ('=COUNTIF(%s,"Maybe")' % rsvp, "#,##0")
    F["assigned"] = ('=SUMPRODUCT(--(%s<>""))' % dfinal, "#,##0")
    F["purchased"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                      % (status, C.ST_BOUGHT, status, C.ST_WRAPPED,
                         status, C.ST_DONE), "#,##0")
    F["wrapped"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                    % (status, C.ST_WRAPPED, status, C.ST_DONE), "#,##0")
    F["complete"] = ('=COUNTIF(%s,"%s")' % (status, C.ST_DONE), "#,##0")
    F["total_budget"] = ("=$AI$%d*BudgetMax" % C.KPI_ROW["participants"],
                         "#,##0.00")
    F["spent"] = ("=SUM(%s)" % bspent, "#,##0.00")
    F["avg_gift"] = ('=IFERROR($AI$%d/$AI$%d,0)'
                     % (C.KPI_ROW["spent"], C.KPI_ROW["purchased"]),
                     "#,##0.00")
    rules = ('SUMPRODUCT(--(%s<>""))' % bk.rng("rules", "giver")) \
        if has_rules else "0"
    F["rules_count"] = (
        '=(CoupleRule="On")+(TeamRule="On")+(LastYearRule="On")+%s'
        % rules if has_rules else "=0", "#,##0")
    if premium:
        wplayer = bk.rng("we", "player")
        wstatus = bk.rng("we", "status")
        hturn = bk.rng("history", "turn")
        F["we_players"] = ("=COUNTA(%s)" % wplayer, "#,##0")
        F["gifts_in_play"] = ('=COUNTIF(%s,"%s")+COUNTIF(%s,"%s")'
                              % (wstatus, C.GS_HELD, wstatus, C.GS_STOLEN),
                              "#,##0")
        F["locked_gifts"] = ('=COUNTIF(%s,"%s")' % (wstatus, C.GS_FINAL),
                             "#,##0")
        F["turns_done"] = ("=COUNT(%s)" % hturn, "#,##0")
        F["current_turn"] = ('=IF($AI$%d=0,"",MOD(StartPlayer-1+$AI$%d,'
                             '$AI$%d)+1)'
                             % (C.KPI_ROW["we_players"],
                                C.KPI_ROW["turns_done"],
                                C.KPI_ROW["we_players"]), "#,##0")
    else:
        for k in ("we_players", "gifts_in_play", "locked_gifts",
                  "turns_done", "current_turn"):
            F[k] = ("=0", "#,##0")
    F["completion"] = ('=IFERROR(($AI$%d+$AI$%d+$AI$%d)/(3*$AI$%d),0)'
                       % (C.KPI_ROW["purchased"], C.KPI_ROW["wrapped"],
                          C.KPI_ROW["complete"],
                          C.KPI_ROW["participants"]), "0%")
    F["violations"] = ('=COUNTIF(%s,"?*")-COUNTIF(%s,"%s OK")'
                       % (dflag, dflag, "\u2705"), "#,##0")
    F["over_budget"] = ('=COUNTIF(%s,"%s")' % (bflag, C.BF_OVER), "#,##0")
    F["diets"] = ("=COUNTA(%s)" % diet, "#,##0")

    # small pools for dashboard charts (status + rsvp mixes)
    pool = bk.S.f(**bk.S.base(font_size=9, font_color=bk.th.muted,
                              align="left", valign="vcenter"))
    pval = bk.S.f(**bk.S.base(font_size=9, font_color=bk.th.ink,
                              align="right", valign="vcenter",
                              num_format="#,##0"))
    for i, stt in enumerate((C.ST_NOT, C.ST_BOUGHT, C.ST_WRAPPED,
                             C.ST_DONE)):
        ws.write(r(40 + i), ci("AH"), stt, pool)
        ws.write_formula(r(40 + i), ci("AI"), '=COUNTIF(%s,"%s")'
                         % (status, stt), pval,
                         (sum(1 for x in (m.people if m else [])
                              if x["status"] == stt) if m else 0))
        bk.stats["formulas"] += 1
    for i, rv in enumerate(("Yes", "No", "Maybe")):
        ws.write(r(45 + i), ci("AH"), rv, pool)
        ws.write_formula(r(45 + i), ci("AI"), '=COUNTIF(%s,"%s")'
                         % (rsvp, rv), pval,
                         (sum(1 for x in (m.people if m else [])
                              if x["rsvp"] == rv) if m else 0))
        bk.stats["formulas"] += 1

    lab = bk.S.f(**bk.S.base(font_size=9.5, font_color=bk.th.muted,
                             align="left", valign="vcenter"))
    val = bk.S.f(**bk.S.base(font_size=9.5, font_color=bk.th.ink,
                             align="right", valign="vcenter"))
    for name, row in sorted(C.KPI_ROW.items()):
        formula, fmt = F[name]
        ws.write(r(row), ci("AH"), name, lab)
        # blank workbooks cache 0 (what the formulas give on empty data) and
        # BASIC edition writes plain "=0" for the white-elephant metrics
        cached = 0
        if m and formula != "=0":
            cached = m.agg.get(name, 0)
        ws.write_formula(r(row), ci("AI"), formula,
                         bk.S.f(**bk.S.base(font_size=9.5,
                                            font_color=bk.th.ink,
                                            align="right", valign="vcenter",
                                            num_format=fmt)),
                         cached)
        bk.stats["formulas"] += 1
