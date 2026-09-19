"""🎟️ Santa Cards - printable cut-out cards, one per participant."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "cards"
LAST_COL = "I"

# 24 participants = 24 card slots (2 per row, 12 rows)
N_CARDS = C.CAP["participants"]


def build(bk):
    th = bk.th
    ws = bk.ws(KEY)
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F39F\ufe0f  Santa Cards",
                 "Print this tab, cut along the cards, hand one to each "
                 "guest - their recipient stays secret until then.")
    last_card_row = 8 + ((N_CARDS + 1) // 2 - 1) * 8
    bk.paint(KEY, 0, 0, last_card_row + 8, ci(LAST_COL), bk.S.canvas)

    p = bk.q("participants")
    d = bk.q("draw")
    names = "%s!$B$%d:$B$%d" % (p, C.ROW_FIRST, C.last_row("participants"))
    finals = "%s!$E$%d:$E$%d" % (d, C.ROW_FIRST, C.last_row("draw"))

    frame = bk.S.f(**bk.S.base(bg_color=th.card, border=1,
                               border_color=th.border_strong))
    head = bk.S.f(**bk.S.base(font_size=10, bold=True, font_color=th.white,
                              bg_color=th.primary, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border_strong))
    giver = bk.S.f(**bk.S.base(font_size=15, bold=True,
                               font_color=th.primary, bg_color=th.card,
                               align="center", valign="vcenter", border=1,
                               border_color=th.border_strong))
    lab = bk.S.f(**bk.S.base(font_size=9, italic=True, font_color=th.muted,
                             bg_color=th.card, align="center",
                             valign="vcenter", border=1,
                             border_color=th.border_strong))
    rec = bk.S.f(**bk.S.base(font_size=14, bold=True, font_color=th.accent,
                             bg_color=th.accent_soft, align="center",
                             valign="vcenter", border=1,
                             border_color=th.border_strong))
    meta = bk.S.f(**bk.S.base(font_size=9, font_color=th.ink,
                              bg_color=th.card, align="center",
                              valign="vcenter", border=1,
                              border_color=th.border_strong))

    for k in range(1, N_CARDS + 1):
        col0 = 1 if k % 2 == 1 else 6
        row0 = 8 + ((k - 1) // 2) * 8
        ws.set_row(r(row0), 20)
        ws.set_row(r(row0 + 1), 26)
        ws.set_row(r(row0 + 2), 14)
        ws.set_row(r(row0 + 3), 24)
        ws.set_row(r(row0 + 4), 14)
        ws.set_row(r(row0 + 5), 14)
        ws.merge_range(r(row0), col0, r(row0), col0 + 3,
                       "  \U0001F385  SECRET SANTA CARD  \u2022  %d" % k,
                       head)
        ws.merge_range(r(row0 + 1), col0, r(row0 + 1), col0 + 3, "", giver)
        ws.write_formula(r(row0 + 1), col0,
                         '=IFERROR(INDEX(%s,%d),"")' % (names, k), giver,
                         (m.people[k - 1]["name"]
                          if m and k <= len(m.people) else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 2), col0, r(row0 + 2), col0 + 3,
                       "you are secretly drawing\u2026", lab)
        ws.merge_range(r(row0 + 3), col0, r(row0 + 3), col0 + 3, "", rec)
        ws.write_formula(r(row0 + 3), col0,
                         '=IFERROR(INDEX(%s,%d),"")' % (finals, k), rec,
                         (m.assign[k - 1] if m and k <= len(m.people)
                          else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 4), col0, r(row0 + 4), col0 + 3, "", meta)
        ws.write_formula(
            r(row0 + 4), col0,
            '=IF(COUNTA(%s)=0,"","budget "&Currency&TEXT('
            'BudgetMin,"#,##0")&"\u2013"&Currency&TEXT(BudgetMax,'
            '"#,##0")&"   \u2022   bring it by "&TEXT(PartyDate,'
            '"dd mmm"))' % names, meta,
            ("budget $20\u2013$35   \u2022   bring it by 19 Dec"
             if m else ""))
        bk.stats["formulas"] += 1
        ws.merge_range(r(row0 + 5), col0, r(row0 + 5), col0 + 3, "", meta)
        ws.write_formula(
            r(row0 + 5), col0,
            '=IF(COUNTA(%s)=0,"",PartyName&"  \u2022  "&PartyLocation)'
            % names, meta,
            ("%s  \u2022  %s" % (m.settings["party"],
                                  m.settings["location"]) if m else ""))
        bk.stats["formulas"] += 1
    K.footer_nav(bk, KEY, last_card_row + 7, LAST_COL, landscape=True, tip=
                 "  \u2702\ufe0f  Print landscape, cut along the borders, "
                 "fold once - secret inside.")
