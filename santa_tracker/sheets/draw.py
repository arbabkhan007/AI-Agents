"""🎅 Secret Santa Draw - seed-driven derangement with rules validation."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "draw"
LAST_COL = "G"

COLUMNS = [
    ("n", "#", "idx", None),
    ("giver", "Giver", "text", None),
    ("computed", "Drawn (auto)", "calc_c", None),
    ("override", "Manual override", "text", None),
    ("final", "FINAL recipient", "calc_c", None),
    ("flag", "Rules check", "calc_wrap", None),
    ("status", "Gift status", "calc_c", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    has_rules = bk.has("rules")
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F385  Secret Santa Draw",
                 "Change the seed on \u2699\ufe0f Settings to shuffle the "
                 "draw - nobody ever draws themselves.")
    K.table_frame(bk, KEY, COLUMNS, height=22)

    p = bk.q("participants")
    names = "%s!$B$%d:$B$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    hh = "%s!$D$%d:$D$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    tm = "%s!$C$%d:$C$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    ly = "%s!$G$%d:$G$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    pst = "%s!$H$%d:$H$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    xg = bk.rng("rules", "giver") if has_rules else None
    xc = bk.rng("rules", "cannot") if has_rules else None

    calc = bk.S.f(**bk.S.base(font_size=10.5, font_color=th.primary,
                              bg_color=th.alt, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border))
    bold = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.ok,
                              bg_color=th.ok_soft, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border))
    flagf = bk.S.f(**bk.S.base(font_size=9.5, font_color=th.ink,
                               bg_color=th.card, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border, text_wrap=True))
    statf = bk.S.f(**bk.S.base(font_size=10, font_color=th.ink,
                               bg_color=th.card, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border))

    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        n = "COUNTA(%s)" % names
        inner = ('IF($E{r}=$B{r},"Self ","")'
                 + ('&IF(AND(CoupleRule="On",IFERROR(INDEX({hh},MATCH($B{r},'
                  '{nm},0)),"")<>"",INDEX({hh},MATCH($B{r},{nm},0))=INDEX('
                  '{hh},MATCH($E{r},{nm},0))),"Couple ","")'
                  + '&IF(AND(TeamRule="On",IFERROR(INDEX({tm},MATCH($B{r},'
                   '{nm},0)),"")<>"",INDEX({tm},MATCH($B{r},{nm},0))=INDEX('
                   '{tm},MATCH($E{r},{nm},0))),"Team ","")' if has_rules
                  else '')
                 + ('&IF(AND(LastYearRule="On",IFERROR(INDEX({ly},MATCH('
                    '$B{r},{nm},0)),"")=$E{r}),"LastYear ","")'
                   if has_rules else '')
                 + ('&IF(COUNTIFS({xg},$B{r},{xc},$E{r})>0,"Custom ","")'
                    if has_rules else '')).format(
            r=row, hh=hh, tm=tm, ly=ly, nm=names, xg=xg, xc=xc)
        values = {
            "n": i + 1,
            "giver": '=IF(%s!$B$%d="","",%s!$B$%d)'
                     % (p, row, p, row),
            "computed": '=IF($B{r}="","",INDEX({nm},MOD($A{r}-1+MOD('
                        'DrawSeed-1,MAX(1,{n}-1)),{n})+1))'.format(
                            r=row, nm=names, n=n),
            "override": "",
            "final": '=IF($B{r}="","",IF($D{r}<>"",$D{r},$C{r}))'.format(
                r=row),
            "flag": '=IF($E{r}="","",IF(TRIM({inner})="","'
                    '\u2705 OK",TRIM({inner})))'.format(r=row, inner=inner),
            "status": '=IF($B{r}="","",INDEX({st},MATCH($B{r},{nm},0)))'
                      .format(r=row, st=pst, nm=names),
        }
        cached = {}
        if m and i < len(m.people):
            cached = {"giver": m.people[i]["name"],
                      "computed": m.assign[i], "final": m.assign[i],
                      "flag": "\u2705 OK",
                      "status": m.people[i]["status"]}
        elif m:
            cached = {"giver": "", "computed": "", "final": "", "flag": "",
                      "status": ""}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        # restyle the computed/final/flag/status cells (kinds are generic)
        ws.write_formula(r(row), ci("C"), values["computed"], calc,
                         cached.get("computed", ""))
        ws.write_formula(r(row), ci("E"), values["final"], bold,
                         cached.get("final", ""))
        ws.write_formula(r(row), ci("F"), values["flag"], flagf,
                         cached.get("flag", ""))
        ws.write_formula(r(row), ci("G"), values["status"], statf,
                         cached.get("status", ""))
        bk.stats["formulas"] += 4

    K.list_dv(bk, KEY, "override", "participants",
              title="Manual override",
              message="Leave blank to keep the automatic draw.")
    K.status_cf(bk, KEY, "status", {
        C.ST_NOT: (th.bad_soft, th.bad),
        C.ST_BOUGHT: (th.warn_soft, th.warn),
        C.ST_WRAPPED: (th.info_soft, th.info),
        C.ST_DONE: (th.ok_soft, th.ok)})
    bk.cond(KEY, C.ROW_FIRST, ci("F"), C.last_row(KEY), ci("F"), {
        "type": "formula",
        "criteria": '=AND($F%d<>"",$F%d<>"\u2705 OK")'
                    % (C.ROW_FIRST, C.ROW_FIRST),
        "format": bk.S.cf(bg=th.bad_soft, fg=th.bad, bold=True)})

    # ------------------------------------------------------------------
    row = C.last_row(KEY) + 2
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F500  DRAW CONTROLS", bk.S.section_soft)
    ws.set_row(r(row), 22)
    lab = bk.S.f(**bk.S.base(font_size=10.5, bold=True, font_color=th.ink,
                             bg_color=th.card, align="left", indent=1,
                             valign="vcenter", border=1,
                             border_color=th.border))
    seedf = bk.S.f(**bk.S.base(font_size=12, bold=True,
                               font_color=th.primary, bg_color=th.gold_soft,
                               border=1, border_color=th.border_strong,
                               align="center", valign="vcenter",
                               locked=False, num_format="#,##0"))
    stat = bk.S.f(**bk.S.base(font_size=10.5, bold=True,
                              font_color=th.primary, bg_color=th.gold_soft,
                              border=1, border_color=th.border_strong,
                              align="center", valign="vcenter"))
    ws.set_row(r(row + 1), 24)
    ws.merge_range(r(row + 1), 1, r(row + 1), 2, "  Draw seed (change to "
                                                "re-draw)", lab)
    ws.write_formula(r(row + 1), 3, "=DrawSeed", seedf,
                     m.settings["seed"] if m else "")
    bk.stats["formulas"] += 1
    ws.merge_range(r(row + 1), 4, r(row + 1), 5, "  Draw status", lab)
    ws.write_formula(r(row + 1), 6, "=DrawStatus", stat,
                     m.settings["status"] if m else "")
    bk.stats["formulas"] += 1

    row += 3
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F575\ufe0f  PRIVATE LOOKUP - type a name, see "
                   "only their recipient", bk.S.section_soft)
    ws.set_row(r(row), 22)
    ws.set_row(r(row + 1), 26)
    inp = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.ink,
                             bg_color=th.card, border=1,
                             border_color=th.border_strong, align="left",
                             valign="vcenter", indent=1, locked=False))
    out = bk.S.f(**bk.S.base(font_size=11.5, bold=True,
                             font_color=th.primary, bg_color=th.card,
                             align="left", valign="vcenter", indent=1))
    ws.merge_range(r(row + 1), 1, r(row + 1), 2, "  I am...", lab)
    ws.merge_range(r(row + 1), 3, r(row + 1), 4, "", inp)
    bk.validate(KEY, row + 1, 3, row + 1, 3,
                "=" + bk.listname("participants"),
                title="Your name")
    ws.merge_range(r(row + 1), 5, r(row + 1), ci(LAST_COL), "", out)
    ws.write_formula(
        r(row + 1), 5,
        '=IF($C%d="","Type your name to peek at your recipient\u2026",'
        'IFERROR("\U0001F385  You are drawing:  "&INDEX($E$%d:$E$%d,MATCH('
        '$C%d,$B$%d:$B$%d,0))&"   \u2022   budget "&Currency&TEXT(BudgetMin,'
        '"#,##0")&"\u2013"&Currency&TEXT(BudgetMax,"#,##0")&"   \u2022   "'
        '&TEXT(PartyDate,"dd mmm yyyy")&"  \u2014  tell no one!",'
        '"Name not found - check the spelling on \U0001F465 Participants."))'
        % (row + 1, C.ROW_FIRST, C.last_row(KEY), row + 1, C.ROW_FIRST,
           C.last_row(KEY)),
        out, "")
    bk.stats["formulas"] += 1

    chips = [
        ('="\U0001F385 Assigned: "&SUMPRODUCT(--($E$%d:$E$%d<>""))&" of "&'
         'COUNTA(%s!$B$%d:$B$%d)'
         % (C.ROW_FIRST, C.last_row(KEY), p, C.ROW_FIRST,
            C.last_row("participants")), "primary",
         "Assigned: %d of %d" % ((m.agg["assigned"], m.agg["participants"])
                                 if m else (0, 0)), 4),
        ('="\u2705 Clean pairs: "&COUNTIF($F$%d:$F$%d,"\u2705 OK")'
         % (C.ROW_FIRST, C.last_row(KEY)), "ok",
         "Clean pairs: %d" % (m.agg["participants"] if m else 0), 3),
        ('="\u26A0\ufe0f Rule hits: "&%s' % bk.kpi("violations"), "bad",
         "Rule hits: %d" % (m.agg["violations"] if m else 0), 3),
        ('="\U0001F512 Status: "&DrawStatus', "gold",
         "Status: %s" % (m.settings["status"] if m else C.DRAW_DRAFT), 4),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, row + 3, LAST_COL, tip=
                 "  \U0001F4A1  Re-draw: unlock the sheet (password "
                 "\u201cpremium\u201d), change the seed, re-protect.  "
                 "Overrides beat the auto-draw pair by pair.")
