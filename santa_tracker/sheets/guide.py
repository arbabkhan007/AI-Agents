"""📖 Start Here - quick start, tab tour, tips and the friendly rules."""

import os

from ..book import r, ci

LAST_COL = "J"


def build(bk):
    key = "guide"
    ws = bk.ws(key)
    S, th = bk.S, bk.th

    bk.widths(key, {"A": 2.2, "B": 4, "C": 15, "D": 15, "E": 15, "F": 15,
                    "G": 15, "H": 15, "I": 15, "J": 15})
    bk.paint(key, 0, 0, 90, ci(LAST_COL), S.canvas)

    body = S.f(**S.base(font_size=10.5, bg_color=th.bg, align="left",
                        valign="vcenter", text_wrap=True))
    body_soft = S.f(**S.base(font_size=10.5, bg_color=th.card, align="left",
                             valign="vcenter", text_wrap=True,
                             border=1, border_color=th.border))
    badge = S.f(**S.base(bold=True, font_size=12, font_color=th.white,
                         bg_color=th.accent, align="center", valign="vcenter"))
    badge2 = S.f(**S.base(bold=True, font_size=12, font_color=th.white,
                          bg_color=th.info, align="center", valign="vcenter"))
    step_title = S.f(**S.base(bold=True, font_size=11.5,
                              font_color=th.primary, bg_color=th.bg,
                              align="left", valign="vcenter", indent=1))
    mark = S.f(**S.base(font_size=10, font_color=th.muted, bg_color=th.bg,
                        align="center", valign="vcenter"))

    def sec(row, emoji, text):
        ws.set_row(r(row), 24)
        ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                       "  %s  %s" % (emoji, text), S.section)

    # ------------------------------------------------------------------
    # cover banner + overlaid title (plain title band when no artwork)
    # ------------------------------------------------------------------
    image = _banner_path(bk)
    row = 1
    ws.set_row(r(row), 7)
    row += 1
    if image:
        w, h = _png_size(image)
        scale = 860.0 / float(w)
        span = int(h * scale / 20.0) + 1
        cover = S.f(**S.base(bg_color=th.cover_bg))
        for i in range(span):
            ws.set_row(r(row + i), 20)
            for col in range(1, ci(LAST_COL) + 1):
                ws.write(r(row + i), col, "", cover)
        ws.insert_image(r(row), 1, image,
                        {"x_scale": scale, "y_scale": scale,
                         "object_position": 1})
        t_row = row + max(1, span // 2 - 1)
        ws.merge_range(r(t_row), ci("C"), r(t_row), ci("G"),
                       "\U0001F4D6  START HERE",
                       S.f(**S.base(font_name=th.title_font, font_size=26,
                                    bold=True, font_color=th.primary,
                                    bg_color=th.cover_bg, align="center",
                                    valign="vcenter")))
        ws.merge_range(r(t_row + 1), ci("C"), r(t_row + 1), ci("G"),
                       "  your 5-minute tour of the Secret Santa & White "
                       "Elephant Party Tracker",
                       S.f(**S.base(font_size=11.5, italic=True,
                                    font_color=th.muted,
                                    bg_color=th.cover_bg, align="center",
                                    valign="vcenter")))
        row += span + 1
        ws.set_row(r(row), 18)
        ws.merge_range(r(row), ci(LAST_COL) - 2, r(row), ci(LAST_COL), "",
                       S.home_link)
        ws.write_url(r(row), ci(LAST_COL) - 2,
                     "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                     "\U0001F3E0  Back to Dashboard")
        row += 2
    else:
        ws.set_row(r(row), 32)
        ws.set_row(r(row + 1), 18)
        ws.merge_range(r(row), 1, r(row), ci(LAST_COL) - 3,
                       "\U0001F4D6  Start Here \u2014 your 5-minute setup",
                       S.sheet_title)
        ws.merge_range(r(row + 1), 1, r(row + 1), ci(LAST_COL) - 3,
                       "  Everything is wired together: log a turn once and "
                       "the game board, budgets and dashboard follow.",
                       S.sheet_sub)
        ws.merge_range(r(row + 1), ci(LAST_COL) - 2, r(row + 1), ci(LAST_COL),
                       "", S.home_link)
        ws.write_url(r(row + 1), ci(LAST_COL) - 2,
                     "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                     "\U0001F3E0  Back to Dashboard")
        row += 3
    # ------------------------------------------------------------------
    sec(row, "\U0001F680", "QUICK START \u2014 FIVE STEPS TO LIVE")
    row += 1
    steps = [
        ("1", "Open \u2699\ufe0f Settings & Instructions",
         "Type the party name, date, location, host, currency, gift budget "
         "min/max, max steals and the two seeds.  Every tab reads these."),
        ("2", "List your guests on \U0001F465 Participants",
         "Names plus team, household/couple, RSVP, dietary needs and who "
         "they drew last year - the exclusion engine feeds off this."),
        ("3", "Draw on \U0001F385 Secret Santa Draw",
         "The draw is a closed cycle: nobody can ever pick themselves.  "
         "Change the seed to shuffle, override any pair by hand, then lock "
         "the draw with the status dropdown."),
        ("4", "Arm your rules on \U0001F6AB Exclusions & Rules",
         "Couples, same-team and last-year repeats toggle on/off; custom "
         "no-pairs go in the table.  The draw flags every breach live."),
        ("5", "Run the party",
         "\U0001F4B0 Budget Tracker watches every spend, \U0001F381 "
         "Wishlists keeps ideas claimable, and \U0001F3B2 White Elephant "
         "plus \U0001F504 Game History run the steal-fest turn by turn."),
    ]
    for num, title, text in steps:
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), 1, num, badge)
        ws.merge_range(r(row), 2, r(row), 3, title, step_title)
        ws.merge_range(r(row), 4, r(row + 1), ci(LAST_COL), text, body)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F5FA\uFE0F", "THE TAB TOUR")
    row += 1
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  Premium edition: every tab below.  Basic edition: the "
                   "tabs marked \u25CF only.",
                   S.f(**S.base(font_size=10, italic=True,
                                font_color=th.muted,
                                bg_color=th.bg, align="left",
                                valign="vcenter", indent=1)))
    row += 1
    tour = [
        ("\u25CF", "\U0001F3E0 Dashboard", "Participants, spend, readiness, "
         "game state, alerts and three live charts."),
        ("\u25CF", "\U0001F465 Participants", "Guest list with RSVP, team, "
         "household, dietary needs and gift status."),
        ("\u25CF", "\U0001F385 Secret Santa Draw", "Auto draw, overrides, "
         "rules check and the private recipient lookup."),
        ("\u25CF", "\U0001F4B0 Budget Tracker", "Min/max rules, actual "
         "spend, under/over flags and receipt tracking."),
        ("\u25CF", "\U0001F3B2 White Elephant", "Seats, gift numbers, steal "
         "counts, locks, holders and final gifts."),
        ("\u25CF", "\U0001F4D6 Start Here", "This page."),
        ("\u25CB", "\U0001F6AB Exclusions & Rules", "House-rule toggles and "
         "custom no-pair list."),
        ("\u25CB", "\U0001F381 Wishlists", "Per-guest ideas with priorities "
         "and anonymous claiming."),
        ("\u25CB", "\U0001F504 Game History", "The turn log: every Pick, "
         "Steal and Pass in order."),
        ("\u25CB", "\U0001F39F\ufe0f Santa Cards", "Printable cut-out "
         "cards so each guest learns their recipient privately."),
    ]
    for mark_txt, tab, blurb in tour:
        ws.set_row(r(row), 18)
        ws.merge_range(r(row), 2, r(row), 3, mark_txt + "  " + tab, step_title)
        ws.merge_range(r(row), 4, r(row), ci(LAST_COL), blurb, body)
        row += 1
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F4A1", "TEN TIPS FROM PARTY ANIMALS")
    row += 1
    tips = [
        "Set the gift budget min AND max - too-cheap gifts hurt feelings "
        "just as much as too-pricey ones.",
        "Collect wishlists before the draw; three wishes each is plenty.",
        "Households in the same couple get the same Household value - the "
        "couple rule then keeps them apart automatically.",
        "Fill in \u201cgave to last year\u201d and arm the repeat rule: "
        "two years running the same pair feels lazy.",
        "Print the Santa Cards, fold them, and let guests pick a card at "
        "random at the door - zero spoilers.",
        "White Elephant: cap steals at 2.  Three or more and the game "
        "stalls; one and nobody gets naughty.",
        "Log steals on Game History as they happen (phone in Sheets) and "
        "the board stays honest without a whiteboard.",
        "The private lookup shows one recipient at a time - perfect for "
        "passing the laptop round without spoilers.",
        "Formula cells are protected with the password \u201cpremium\u201d; "
        "unlock only when you need to change a seed.",
        "Reuse the file every year: bump the party year and date, clear the "
        "logs, keep your lists.",
    ]
    for i, tip in enumerate(tips, 1):
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), 1, str(i), badge2)
        ws.merge_range(r(row), 2, r(row + 1), ci(LAST_COL), tip, body)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F512", "THE GENTLE RULES")
    row += 1
    rules = [
        "Cream-filled cells are yours to type in.  White cells are formulas "
        "\u2014 leave them alone and they will keep working for you.",
        "Sheets are protected to stop accidental edits.  Review \u2192 "
        "Unprotect Sheet if you ever need to restructure something.",
        "Add rows by copying an existing data row and inserting below it "
        "\u2014 the formulas, dropdowns and colours travel with the copy.",
        "This file opens in Excel 2016+ and in Google Sheets (upload to "
        "Drive \u2192 open with Sheets).  A few chart styles look slightly "
        "different in Sheets; every number still calculates.",
        "The EXAMPLE edition is loaded with a fictional office party so "
        "you can see it working.  The blank edition is the one you keep.",
    ]
    for rule in rules:
        ws.set_row(r(row), 16)
        ws.set_row(r(row + 1), 16)
        ws.merge_range(r(row), 1, r(row + 1), ci(LAST_COL),
                       "\u2022  " + rule, body_soft)
        row += 2
    row += 1

    # ------------------------------------------------------------------
    sec(row, "\U0001F91D", "SUPPORT")
    row += 1
    ws.set_row(r(row), 16)
    ws.set_row(r(row + 1), 16)
    ws.merge_range(r(row), 1, r(row + 1), ci(LAST_COL),
                   "  Thank you for buying this template \u2014 it was "
                   "built by Novality Store, people who have hosted one "
                   "too many white-elephant stampedes and know what a "
                   "spreadsheet owes you in December.  Message the shop "
                   "any time and a human will help quickly.", body_soft)
    row += 3

    # ------------------------------------------------------------------
    # footer + nav
    # ------------------------------------------------------------------
    ws.set_row(r(row), 30)
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  \U0001F4AC  Questions about this file?  Your Etsy "
                   "shop message reaches a human, usually the same day.",
                   S.f(**S.base(font_size=10, italic=True, font_color=th.ink,
                                bg_color=th.gold_soft, align="left",
                                valign="vcenter", indent=1)))
    nav = row + 2
    ws.set_row(r(nav), 24)
    bk.nav_row(key, nav, max_col=LAST_COL)
    bk.page(key, LAST_COL, nav + 1, landscape=False, zoom=90)


# ---------------------------------------------------------------------------
def _banner_path(bk):
    """Watercolour cover art for the Start Here tab, if it exists."""
    if not bk.images:
        return None
    here = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(here, "assets", "banner_%s%s" % (bk.th.key, ext))
        if os.path.exists(path):
            return path
    return None


def _png_size(path):
    """Pixel size of a PNG or JPEG, without needing Pillow."""
    with open(path, "rb") as fh:
        data = fh.read(32)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        import struct
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    return 1600, 300
