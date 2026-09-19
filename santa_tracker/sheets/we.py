"""🎲 White Elephant - seat order, gifts, steals, locks and holders."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "we"
LAST_COL = "L"

COLUMNS = [
    ("n", "#", "idx", None),
    ("order", "Seat", "calc_num", None),
    ("player", "Player", "text", None),
    ("giftnum", "Gift #", "calc_num", None),
    ("desc", "Gift description", "wrap", None),
    ("value", "Gift value", "money", None),
    ("steals", "Steals", "calc_num", None),
    ("maxsteals", "Max", "calc_num", None),
    ("status", "Gift status", "calc_c", None),
    ("holder", "Current holder", "calc_c", None),
    ("stolenfrom", "Last stolen from", "calc_c", None),
    ("final", "Final?", "calc_tick", None),
]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F3B2  White Elephant",
                 "Seats and gift numbers shuffle from the seed; holders, "
                 "steal counts and locks follow \U0001F504 Game History.")
    K.table_frame(bk, KEY, COLUMNS, height=22)
    ws.set_column(ci("M"), ci("N"), 10, None, {"hidden": True})

    h = bk.q("history")
    hgift = "%s!$E$%d:$E$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hturn = "%s!$G$%d:$G$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hplayer = "%s!$C$%d:$C$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    haction = "%s!$D$%d:$D$%d" % (h, C.ROW_FIRST, C.last_row("history"))
    hfrom = "%s!$F$%d:$F$%d" % (h, C.ROW_FIRST, C.last_row("history"))

    statf = bk.S.f(**bk.S.base(font_size=10, bold=True, font_color=th.ink,
                               bg_color=th.alt, align="center",
                               valign="vcenter", border=1,
                               border_color=th.border))
    keyf = bk.S.f(**bk.S.base(font_size=9, font_color=th.muted,
                              bg_color=th.alt, align="right",
                              valign="vcenter", num_format="#,##0"))
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        lastt = 'SUMPRODUCT(MAX((%s=$D%d)*%s))' % (hgift, row, hturn)
        lastidx = ('SUMPRODUCT((%s=$D%d)*(%s=%s)*(ROW(%s)-%d))'
                   % (hgift, row, hturn, lastt, hgift,
                      C.ROW_FIRST - 1))
        values = {
            "n": i + 1,
            "order": '=IF($C%d="","",1+SUMPRODUCT(--($M$%d:$M$%d>$M%d)))'
                     % (row, C.ROW_FIRST, C.last_row(KEY), row),
            "player": "",
            "giftnum": '=IF($C%d="","",1+SUMPRODUCT(--($N$%d:$N$%d>$N%d)))'
                       % (row, C.ROW_FIRST, C.last_row(KEY), row),
            "desc": "",
            "value": "",
            "steals": '=IF($D%d="","",COUNTIFS(%s,$D%d,%s,"Steal"))'
                      % (row, hgift, row, haction),
            "maxsteals": '=IF($C%d="","",MaxSteals)' % row,
            "status": '=IF($D%d="","",IF($G%d>=$H%d,"%s",IF(COUNTIFS(%s,'
                      '$D%d)=0,"%s",IF(INDEX(%s,%s)="Steal","%s","%s"))))'
                      % (row, row, row, C.GS_FINAL, hgift, row, C.GS_AVAIL,
                         haction, lastidx, C.GS_STOLEN, C.GS_HELD),
            "holder": '=IF($D%d="","",IF(COUNTIFS(%s,$D%d)=0,"",INDEX('
                      '%s,%s)))' % (row, hgift, row, hplayer, lastidx),
            "stolenfrom": '=IF($I%d="%s",IFERROR(INDEX(%s,%s),""),"")'
                          % (row, C.GS_STOLEN, hfrom, lastidx),
            "final": '=IF($C%d="","",IF(COUNTA($J$%d:$J$%d)=COUNTA($C$%d:'
                     '$C$%d),IFERROR(INDEX($D$%d:$D$%d,MATCH($C%d,$J$%d:$J$%d,'
                     '0)),""),"-"))'
                     % (row, C.ROW_FIRST, C.last_row(KEY), C.ROW_FIRST,
                        C.last_row(KEY), C.ROW_FIRST, C.last_row(KEY), row,
                        C.ROW_FIRST, C.last_row(KEY)),
            # hidden shuffle keys (columns M/N) - the seat and gift-number
            # ranks above are computed FROM these, matching the demo's
            # (seed*7919*(i+2)+i*104729) and (seed*6967*(i+5)+i*1299709)
            "key1": '=IF($C%d="",0,MOD(WESeed*7919*(ROW()-6)+(ROW()-8)*'
                    '104729,999983)*100+(ROW()-8))' % row,
            "key2": '=IF($C%d="",0,MOD(WESeed*6967*(ROW()-3)+(ROW()-8)*'
                    '1299709,999983)*100+(ROW()-8))' % row,
        }
        cached = {}
        if m and i < len(m.we):
            w = m.we[i]
            cached = {"order": w["seat"], "giftnum": w["giftnum"],
                      "steals": w["steals"],
                      "maxsteals": m.settings["steals"],
                      "status": w["status"], "holder": w["holder"],
                      "stolenfrom": w["stolenfrom"], "final": "",
                      "key1": m.we_k1[i], "key2": m.we_k2[i]}
            values["player"] = w["player"]
            values["desc"] = w["desc"]
            values["value"] = w["value"]
        elif m:
            cached = {"order": "", "giftnum": "", "steals": "",
                      "maxsteals": "", "status": "", "holder": "",
                      "stolenfrom": "", "final": "", "key1": 0, "key2": 0}
        K.write_row(bk, KEY, COLUMNS, row, values, cached)
        ws.write_formula(r(row), ci("I"), values["status"], statf,
                         cached.get("status", ""))
        bk.stats["formulas"] += 1
        # the hidden helper columns are not part of COLUMNS - write them
        # directly so the seat / gift-number ranks have something to rank
        ws.write_formula(r(row), ci("M"), values["key1"], keyf,
                         cached.get("key1", 0))
        ws.write_formula(r(row), ci("N"), values["key2"], keyf,
                         cached.get("key2", 0))
        bk.stats["formulas"] += 2

    K.list_dv(bk, KEY, "player", "participants")
    K.money_dv(bk, KEY, ("value",))
    K.status_cf(bk, KEY, "status", {
        C.GS_AVAIL: (th.card, th.muted),
        C.GS_HELD: (th.ok_soft, th.ok),
        C.GS_STOLEN: (th.warn_soft, th.warn),
        C.GS_FINAL: (th.bad_soft, th.bad)})
    # highlight the seat whose turn it is
    bk.cond(KEY, C.ROW_FIRST, 1, C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=AND($C%d<>"",$B%d=%s)'
                    % (C.ROW_FIRST, C.ROW_FIRST, bk.kpi("current_turn")),
        "format": bk.S.cf(bg=th.gold_soft, fg=th.primary, bold=True)})

    now_seat = m.agg["current_turn"] if m else 0
    now_player = (m.we_by_seat[now_seat]["player"]
                  if m and now_seat in m.we_by_seat else "")
    chips = [
        ('="\U0001F3B2 Players: "&COUNTA($C$%d:$C$%d)'
         % (C.ROW_FIRST, C.last_row(KEY)), "primary",
         "Players: %d" % (m.agg["we_players"] if m else 0), 3),
        ('="\U0001F381 In play: "&%s' % bk.kpi("gifts_in_play"), "ok",
         "In play: %d" % (m.agg["gifts_in_play"] if m else 0), 3),
        ('="\U0001F512 Locked: "&%s' % bk.kpi("locked_gifts"), "bad",
         "Locked: %d" % (m.agg["locked_gifts"] if m else 0), 3),
        ('="\U0001F449 Now: seat "&%s&" ("&IFERROR(INDEX($C$%d:$C$%d,MATCH('
         '%s,$B$%d:$B$%d,0)),"game over")&")"'
         % (bk.kpi("current_turn"), C.ROW_FIRST, C.last_row(KEY),
            bk.kpi("current_turn"), C.ROW_FIRST, C.last_row(KEY)), "gold",
         "Now: seat %d (%s)" % (now_seat, now_player), 5),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, C.last_row(KEY) + 2, LAST_COL, tip=
                 "  \U0001F4A1  House rule: one turn per seat per round; if "
                 "your gift was stolen, pick again on your next round turn. "
                 " A gift locks at max steals.")
