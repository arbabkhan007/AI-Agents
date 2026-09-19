"""🏠 Dashboard - party command centre."""

from .. import config as C
from ..book import r, ci
from . import common as K

import datetime as _dt

KEY = "dashboard"
LAST_COL = "N"


def _today():
    from .. import demo as D
    return D.today()


def build(bk):
    th = bk.th
    S = bk.S
    ws = bk.ws(KEY)
    m = bk.demo
    agg = m.agg if m else {}
    bk.widths(KEY, C.WIDTHS[KEY])
    bk.paint(KEY, 0, 0, C.DASH_NAV + 2, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------------------
    # hero
    # ------------------------------------------------------------------
    ws.set_row(r(1), 8)
    ws.set_row(r(2), 34)
    ws.set_row(r(3), 26)
    ws.set_row(r(4), 20)
    ws.set_row(r(5), 22)
    ws.merge_range(r(2), 1, r(2), ci(LAST_COL), "", S.hero_title)
    ws.write_formula(
        r(2), 1,
        '=IF(PartyName="","\U0001F385  Secret Santa & White Elephant '
        'Command Centre","\U0001F385  "&PartyName&"   \u2022   Secret '
        'Santa & White Elephant Command Centre")', S.hero_title,
        "\U0001F385  %s   \u2022   Secret Santa & White Elephant Command "
        "Centre" % (m.settings["party"] if m else ""))
    bk.stats["formulas"] += 1
    ws.merge_range(r(3), 1, r(3), ci(LAST_COL), "", S.hero_count)
    ws.write_formula(
        r(3), 1,
        '=IF(PartyDate="","", "\U0001F384  "&TEXT(PartyDate,"dddd, dd '
        'mmmm yyyy")&"   \u2022   "&PartyLocation&"   \u2022   hosted by '
        '"&PartyHost&"   \u2022   "&MAX(0,PartyDate-TODAY())&" days to '
        'go!")', S.hero_count,
        ("\U0001F384  %s   \u2022   %s   \u2022   hosted by %s   \u2022   "
         "%d days to go!"
         % (m.settings["date"].strftime("%A, %d %B %Y"),
            m.settings["location"], m.settings["host"],
            max(0, (m.settings["date"] - _today()).days)) if m else ""))
    bk.stats["formulas"] += 1
    ws.merge_range(r(4), 1, r(4), ci(LAST_COL), "", S.hero_meta)
    ws.write_formula(
        r(4), 1,
        '="\U0001F465 "&%s&" guests   \u2022   "&%s&" in the draw   '
        '\u2022   "&%s&" white-elephant players   \u2022   draw: "&'
        'DrawStatus' % (bk.kpi("participants"), bk.kpi("assigned"),
                        bk.kpi("we_players")),
        S.hero_meta,
        "\U0001F465 %d guests   \u2022   %d in the draw   \u2022   %d "
        "white-elephant players   \u2022   draw: %s"
        % (agg.get("participants", 0), agg.get("assigned", 0),
           agg.get("we_players", 0),
           m.settings["status"] if m else ""))
    bk.stats["formulas"] += 1
    msgfmt = S.f(**S.base(bg_color=th.gold, font_color=th.white, bold=True,
                          font_size=10.5, align="left", valign="vcenter",
                          indent=1))
    ws.merge_range(r(5), 1, r(5), ci(LAST_COL), "", msgfmt)
    ws.write_formula(r(5), 1, '="\U0001F4AC  "&Message', msgfmt,
                     "\U0001F4AC  %s" % (m.settings["message"] if m
                                          else ""))
    bk.stats["formulas"] += 1

    ws.merge_range(r(7), 1, r(7), ci(LAST_COL),
                   "  \U0001F389  PARTY AT A GLANCE", S.section)
    ws.set_row(r(7), 22)

    cards1 = [
        ("PARTICIPANTS", "primary", "=%s" % bk.kpi("participants"),
         agg.get("participants", 0)),
        ("SANTA ASSIGNED", "ok", '=%s&" of "&%s'
         % (bk.kpi("assigned"), bk.kpi("participants")),
         "%d of %d" % (agg.get("assigned", 0), agg.get("participants", 0))),
        ("GIFTS PURCHASED", "info", "=%s" % bk.kpi("purchased"),
         agg.get("purchased", 0)),
        ("TOTAL BUDGET", "gold", bk.money(bk.kpi("total_budget"),
                                          "#,##0"),
         "$%s" % format(agg.get("total_budget", 0), ",.0f")),
        ("ACTUAL SPEND", "accent", bk.money(bk.kpi("spent"), "#,##0"),
         "$%s" % format(agg.get("spent", 0), ",.0f")),
        ("AVG GIFT COST", "primary_2", bk.money(bk.kpi("avg_gift"),
                                                "#,##0.00"),
         "$%s" % format(agg.get("avg_gift", 0), ",.2f")),
    ]
    cards2 = [
        ("EXCLUSION RULES", "primary", "=%s" % bk.kpi("rules_count"),
         agg.get("rules_count", 0)),
        ("W-E PLAYERS", "info", "=%s" % bk.kpi("we_players"),
         agg.get("we_players", 0)),
        ("GIFTS IN PLAY", "accent", "=%s" % bk.kpi("gifts_in_play"),
         agg.get("gifts_in_play", 0)),
        ("LOCKED GIFTS", "bad", "=%s" % bk.kpi("locked_gifts"),
         agg.get("locked_gifts", 0)),
        ("RSVP YES", "ok", '=%s&" / "&%s'
         % (bk.kpi("rsvp_yes"), bk.kpi("participants")),
         "%d / %d" % (agg.get("rsvp_yes", 0), agg.get("participants", 0))),
        ("COMPLETION", "gold", '=TEXT(%s,"0%%")' % bk.kpi("completion"),
         "%.0f%%" % (100 * agg.get("completion", 0))),
    ]
    _cards(bk, cards1, C.DASH_CARD1_L, C.DASH_CARD1_V)
    _cards(bk, cards2, C.DASH_CARD2_L, C.DASH_CARD2_V)

    _bar(bk, C.DASH_BAR1, "Gift readiness", bk.kpi("purchased"),
         bk.kpi("participants"), agg.get("participants", 0) and
         agg["purchased"] / float(agg["participants"]), "pct")
    _bar(bk, C.DASH_BAR2, "RSVP confirmed", bk.kpi("rsvp_yes"),
         bk.kpi("participants"), agg.get("participants", 0) and
         agg["rsvp_yes"] / float(agg["participants"]), "pct")

    _charts(bk)

    # ------------------------------------------------------------------
    # panels
    # ------------------------------------------------------------------
    row = C.DASH_PANEL
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F3B2  GAME STATE   \u2022   \u26A0\ufe0F  PARTY "
                   "ALERTS", S.section)
    ws.set_row(r(row), 22)
    lab = S.f(**S.base(font_size=10, bold=True, font_color=th.ink,
                       bg_color=th.card, align="left", indent=1,
                       valign="vcenter", border=1, border_color=th.border))
    val = S.f(**S.base(font_size=10.5, bold=True, font_color=th.primary,
                       bg_color=th.card, align="left", indent=1,
                       valign="vcenter", border=1, border_color=th.border))
    left = [
        ("Turns logged", "=%s" % bk.kpi("turns_done"),
         agg.get("turns_done", 0)),
        ("Now playing (seat)", "=%s" % bk.kpi("current_turn"),
         agg.get("current_turn", 0)),
        ("Gifts still stealable", "=%s" % bk.kpi("gifts_in_play"),
         agg.get("gifts_in_play", 0)),
        ("Gifts locked \U0001F512", "=%s" % bk.kpi("locked_gifts"),
         agg.get("locked_gifts", 0)),
    ]
    right = [
        ("RSVP still maybe", "=%s" % bk.kpi("rsvp_pending"),
         agg.get("rsvp_pending", 0)),
        ("Over-budget gifts", "=%s" % bk.kpi("over_budget"),
         agg.get("over_budget", 0)),
        ("Draw rule hits", "=%s" % bk.kpi("violations"),
         agg.get("violations", 0)),
        ("Dietary needs noted", "=%s" % bk.kpi("diets"),
         agg.get("diets", 0)),
    ]
    for i, ((lt, lf, lc), (rt_, rf, rc)) in enumerate(zip(left, right)):
        rr = row + 1 + i
        ws.set_row(r(rr), 20)
        ws.merge_range(r(rr), 1, r(rr), 4, "  " + lt, lab)
        ws.merge_range(r(rr), 5, r(rr), 7, "", val)
        ws.write_formula(r(rr), 5, lf, val, lc)
        bk.stats["formulas"] += 1
        ws.merge_range(r(rr), 8, r(rr), 11, "  " + rt_, lab)
        ws.merge_range(r(rr), 12, r(rr), ci(LAST_COL), "", val)
        ws.write_formula(r(rr), 12, rf, val, rc)
        bk.stats["formulas"] += 1

    K.footer_nav(bk, KEY, C.DASH_NAV, LAST_COL, landscape=True, tip=
                 "  \U0001F4AC  %s" % "Novality Store wishes you a loud, "
                 "glorious, steal-happy party.")


# ===========================================================================
def _cards(bk, cards, row_l, row_v):
    S, th = bk.S, bk.th
    ws = bk.ws("dashboard")
    pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]
    for (label, colour, formula, cached), (c1, c2) in zip(cards, pairs):
        bg = getattr(th, colour)
        lbl = S.f(**S.base(bold=True, font_size=9.5, font_color=th.white,
                           bg_color=bg, align="left", valign="vcenter",
                           indent=1))
        vfmt = S.f(**S.base(bold=True, font_size=15,
                            font_color=bg if colour != "gold" else th.gold,
                            bg_color=th.card, align="center",
                            valign="vcenter"))
        ws.merge_range(r(row_l), c1, r(row_l), c2, "  " + label, lbl)
        ws.merge_range(r(row_v), c1, r(row_v), c2, "", vfmt)
        ws.write_formula(r(row_v), c1,
                         formula if formula.startswith("=")
                         else "=" + formula, vfmt, cached)
        bk.stats["formulas"] += 1
    ws.set_row(r(row_l), 18)
    ws.set_row(r(row_v), 26)


def _bar(bk, row, label, num_k, den_k, cached_pct, kind=None):
    S, th = bk.S, bk.th
    ws = bk.ws("dashboard")
    ws.set_row(r(row), 20)
    ws.merge_range(r(row), 1, r(row), 2, "  " + label, S.bar_label)
    ws.merge_range(r(row), 3, r(row), 9, "", S.bar_text)
    ws.write_formula(r(row), 3, bk.bar(num_k, den_k, 34), S.bar_text,
                     _bar_cached(cached_pct, 34))
    bk.stats["formulas"] += 1
    ws.merge_range(r(row), 10, r(row), 12, "", S.bar_pct)
    ws.write_formula(r(row), 10,
                     '=TEXT(IFERROR(%s/%s,0),"0.0%%")' % (num_k, den_k),
                     S.bar_pct, "%.1f%%" % (100.0 * float(cached_pct or 0)))
    bk.stats["formulas"] += 1


def _bar_cached(pct, blocks):
    filled = int(round(min(1.0, max(0.0, float(pct or 0))) * blocks))
    return "\u2588" * filled + "\u2591" * (blocks - filled)


# ===========================================================================
def _charts(bk):
    S, th = bk.S, bk.th
    wb = bk.wb
    d = bk.q("data")
    premium = bk.has("we")

    def base_chart(ctype, title):
        ch = wb.add_chart({"type": ctype})
        ch.set_title({"name": title, "name_font": {"size": 11,
                                                   "color": th.primary,
                                                   "bold": True}})
        ch.set_size({"width": 470, "height": 250})
        ch.set_chartarea({"border": {"color": th.border},
                          "fill": {"color": th.card}})
        ch.set_legend({"position": "none"})
        ch.show_hidden_data()
        bk.stats["charts"] += 1
        return ch

    ch1 = base_chart("column", "Actual spend per giver")
    ch1.add_series({
        "name": "Spent",
        "categories": "=%s!$B$%d:$B$%d" % (bk.q("participants"),
                                           C.ROW_FIRST,
                                           C.last_row("participants")),
        "values": "=%s!$E$%d:$E$%d" % (bk.q("budget"),
                                       C.ROW_FIRST, C.last_row("budget")),
        "fill": {"color": th.accent},
        "border": {"color": th.border_strong},
    })
    ws = bk.ws("dashboard")
    ws.insert_chart("C%d" % (C.DASH_CHART1 + 1), ch1)

    ch2 = base_chart("doughnut", "Gift readiness mix")
    ch2.add_series({
        "name": "Status",
        "categories": "=%s!$AH$40:$AH$43" % d,
        "values": "=%s!$AI$40:$AI$43" % d,
        "points": [{"fill": {"color": th.bad}},
                   {"fill": {"color": th.warn}},
                   {"fill": {"color": th.info}},
                   {"fill": {"color": th.ok}}],
    })
    ch2.set_legend({"position": "bottom", "font": {"size": 9,
                                                   "color": th.muted}})
    ws.insert_chart("I%d" % (C.DASH_CHART1 + 1), ch2)

    if premium:
        ch3 = base_chart("bar", "Steals per gift")
        wq = bk.q("we")
        ch3.add_series({
            "name": "Steals",
            "categories": "=%s!$D$%d:$D$%d" % (wq, C.ROW_FIRST,
                                               C.last_row("we")),
            "values": "=%s!$G$%d:$G$%d" % (wq, C.ROW_FIRST,
                                           C.last_row("we")),
            "fill": {"color": th.primary_2},
        })
        ws.insert_chart("C%d" % (C.DASH_CHART2 + 1), ch3)

        ch4 = base_chart("column", "Gift values brought")
        ch4.add_series({
            "name": "Value",
            "categories": "=%s!$D$%d:$D$%d" % (wq, C.ROW_FIRST,
                                               C.last_row("we")),
            "values": "=%s!$F$%d:$F$%d" % (wq, C.ROW_FIRST,
                                           C.last_row("we")),
            "fill": {"color": th.gold},
        })
        ws.insert_chart("I%d" % (C.DASH_CHART2 + 1), ch4)
    else:
        ch3 = base_chart("doughnut", "RSVP mix")
        ch3.add_series({
            "name": "RSVP",
            "categories": "=%s!$AH$45:$AH$47" % d,
            "values": "=%s!$AI$45:$AI$47" % d,
            "points": [{"fill": {"color": th.ok}},
                       {"fill": {"color": th.bad}},
                       {"fill": {"color": th.warn}}],
        })
        ch3.set_legend({"position": "bottom", "font": {"size": 9,
                                                       "color": th.muted}})
        ws.insert_chart("C%d" % (C.DASH_CHART2 + 1), ch3)
