"""
make_user_guide_santa.py - the illustrated "How to use it" PDF for the
Secret Santa & White Elephant Party Tracker, branded Novality Store.

12 A4 pages at 200 dpi (1654 x 2339 px each), illustrated with REAL
screenshots of the finished workbook (tools/render_preview_santa.py on the
PREMIUM Noel EXAMPLE file, with true emoji glyphs) plus hand-drawn versions
of the dashboard's live charts.

Run:  python3 -m etsy.make_user_guide_santa
Out:  Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf  (repo root)
"""

import io
import os
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy.crochet_lib import (F, check_poly, draw_text, doughnut_chart,
                              fit_size, grouped_columns, hbar_chart, hexrgb,
                              rrect, shadow_paste, text_width, wrap)
from tools.render_preview_santa import render as render_sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PDF = os.path.join(
    ROOT, "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf")
XLSX = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx")
RAW_BANNER = os.path.join(ROOT, "assets", "raw_banner_noel.png")
URL = "Novality Store \u2014 Secret Santa & White Elephant Party Tracker"

# ---------------------------------------------------------------------------
# palette - the workbook's own Noel theme
# ---------------------------------------------------------------------------
PRIMARY = "#8C1D2C"          # holly red
PINE = "#1F5C40"             # pine green
GOLD = "#B98A2E"             # antique gold
CANVAS = "#FBF6EE"
CARD = "#FFFFFF"
ALT = "#FCF8F1"
BORDER = "#E7D9C6"
INK = "#33221E"
MUTED = "#9A8474"
OK = "#1F5C40"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
WHITE = "#FFFFFF"

PW, PH = 1654, 2339             # A4 at 200 dpi
DPI = 200.0
MX = 120                         # side margin
CW = PW - 2 * MX                 # content width 1414
BOTTOM = PH - 170                # footer zone starts here
TOTAL_PAGES = 12

PAGES = []
SW_CROP = 1414


# ---------------------------------------------------------------------------
# screenshots of the real workbook
# ---------------------------------------------------------------------------
def shot(sheet, rows, cols, zoom=1.0):
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        render_sheet(XLSX, sheet, tmp, rows, cols, zoom)
        return Image.open(tmp).convert("RGBA")
    finally:
        os.unlink(tmp)


def browser(screen, width, url=URL):
    """Browser chrome (warm cream) around a screen image. Returns RGBA."""
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    chrome_h = 62
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#F0E9DD"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([26 + i * 34, 22, 44 + i * 34, 40], fill=hexrgb(c))
    pill = [width / 2.0 - 430, 14, width / 2.0 + 430, 48]
    rrect(d, pill, 17, fill=hexrgb(WHITE), outline=hexrgb("#E2D6C2"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 19, 830, 11)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 20, 23),
              "\U0001F512 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#E2D6C2"))
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CBB894"),
                                          width=4)
    return out


def sshot(img, y, screen, width=CW, crop_h=None):
    sc = screen.crop((0, 0, screen.width, crop_h)) if crop_h else screen
    br = browser(sc, width)
    shadow_paste(img, br, (int(PW / 2 - br.width / 2), y), blur=22,
                 alpha=60)
    return y + br.height + 26


def banner_strip(top=True, height=250):
    b = Image.open(RAW_BANNER).convert("RGB")
    crop = b.crop((0, 0, 1600, 300)) if top else \
        b.crop((0, 640 - 300, 1600, 640))
    return crop.resize((PW, height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# page helpers
# ---------------------------------------------------------------------------
def new_page():
    return Image.new("RGBA", (PW, PH), hexrgb(CANVAS))


def finish_page(img, n, titled=True):
    assert n <= TOTAL_PAGES
    d = ImageDraw.Draw(img)
    if titled:
        d.line([MX, PH - 128, PW - MX, PH - 128], fill=hexrgb(BORDER),
               width=2)
        draw_text(img, (MX, PH - 104),
                  "Secret Santa & White Elephant Party Tracker \u2014 "
                  "User Guide", F("sans_md", 22), MUTED)
        draw_text(img, (PW - MX, PH - 104), f"Page {n} of {TOTAL_PAGES}",
                  F("sans_sb", 22), PRIMARY, anchor="ra")
        draw_text(img, (PW / 2.0, PH - 104), "\u00A9 Novality Store",
                  F("sans_b", 22), PRIMARY, anchor="ma")
    PAGES.append(img)
    return img


def kicker(cv, cx, y, text, color=PRIMARY, size=24, track=9):
    d = ImageDraw.Draw(cv)
    f = F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size * 2.1


def h1(img, y, kick, title, size=76, color=PRIMARY):
    y = kicker(img, PW / 2.0, y, kick, GOLD)
    f, _ = fit_size(title, "display_xb", size, CW, 30)
    draw_text(img, (PW / 2.0, y), title, f, color, anchor="ma")
    return y + int(f.size * 1.42)


def h2(img, y, text, color=PRIMARY, size=40, x=MX):
    d = ImageDraw.Draw(img)
    f = F("serif_b", size)
    d.rectangle([x, y + 4, x + 12, y + size + 4], fill=hexrgb(color))
    draw_text(img, (x + 32, y), text, f, color)
    return y + size + 26


def para(img, y, text, size=27, color=INK, x=MX, w=CW, lead=1.55):
    f = F("sans_md", size)
    for line in wrap(text, f, w):
        draw_text(img, (x, y), line, f, color)
        y += int(size * lead)
    return y + 8


def bullets(img, y, items, size=25, x=MX, w=CW, color=PINE, lead=1.5,
            gap=12, check=True):
    d = ImageDraw.Draw(img)
    for it in items:
        f = F("sans_md", size)
        lines = wrap(it, f, w - 56)
        first = True
        for ln in lines:
            if first and check:
                check_poly(d, x + 14, y + size * 0.62, size * 0.95,
                           color, max(3, int(size * 0.16)))
            elif first:
                d.ellipse([x + 8, y + size * 0.35, x + 20,
                           y + size * 0.35 + 12], fill=hexrgb(color))
            draw_text(img, (x + 48, y), ln, f, INK)
            y += int(size * lead)
            first = False
        y += gap
    return y


def steps(img, y, items, size=26, x=MX, w=CW, r=27):
    for i, (title, body) in enumerate(items, 1):
        d = ImageDraw.Draw(img)
        cy = y + r + 4
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=hexrgb(PRIMARY))
        draw_text(img, (x + r, cy - 19), str(i), F("display_b", 34),
                  WHITE, anchor="ma")
        tx = x + 2 * r + 26
        draw_text(img, (tx, y), title, F("sans_b", size), PRIMARY)
        yy = y + size + 8
        f = F("sans_md", size - 2)
        for ln in wrap(body, f, w - (2 * r + 26)):
            draw_text(img, (tx, yy), ln, f, INK)
            yy += int((size - 2) * 1.45)
        y = max(yy, cy + r + 10) + 16
    return y


def note_card(img, y, emoji, title, lines, color, h=None, size=24,
              x=MX, w=CW):
    pad = 30
    f = F("sans_md", size)
    wrapped = []
    for ln in lines:
        wrapped.extend(wrap(ln, f, w - 2 * pad - 40))
    hh = h or (76 + len(wrapped) * int(size * 1.5) + 26)
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + w, y + hh], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [x, y, x + w, y + 62], 16, fill=hexrgb(color))
    d.rectangle([x, y + 31, x + w, y + 62], fill=hexrgb(color))
    draw_text(img, (x + 26, y + 14), f"{emoji} {title}",
              F("serif_b", 30), WHITE)
    yy = y + 84
    for ln in wrapped:
        draw_text(img, (x + pad, yy), ln, f, INK)
        yy += int(size * 1.5)
    return y + hh


def qa_page(img, n, y_last, label):
    assert y_last <= BOTTOM, f"page {n} ({label}) overflows: {y_last} > " \
        f"{BOTTOM}"


def chip(img, x, y, text, fg, bg, size=24, pad=22):
    d = ImageDraw.Draw(img)
    f = F("sans_sb", size)
    w = text_width(text, f) + 2 * pad
    rrect(d, [x, y, x + w, y + size + 26], (size + 26) / 2.0,
          fill=hexrgb(bg))
    draw_text(img, (x + pad, y + 12), text, f, fg)
    return x + w + 18


# ---------------------------------------------------------------------------
# demo data for the chart figures
# ---------------------------------------------------------------------------
from santa_tracker import config as SC        # noqa: E402
from santa_tracker.demo import Demo           # noqa: E402

m = Demo()


# ---------------------------------------------------------------------------
# page 1 - cover
# ---------------------------------------------------------------------------
def p01():
    img = new_page()
    img.paste(banner_strip(True, 250), (0, 0))
    y = 300
    y = kicker(img, PW / 2.0, y, "NOVALITY STORE PRESENTS", GOLD, 26, 12)
    f, _ = fit_size("Secret Santa & White Elephant",
                    "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2.0, y), "Secret Santa & White Elephant", f,
              PRIMARY, anchor="ma")
    y += int(f.size * 1.25)
    f, _ = fit_size("Party Tracker", "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2.0, y), "Party Tracker", f, PINE, anchor="ma")
    y += int(f.size * 1.5)
    y = kicker(img, PW / 2.0, y, "THE ILLUSTRATED USER GUIDE", MUTED,
               22, 10)

    # feature chips
    x = PW / 2.0
    items = [("12 linked tabs", PRIMARY, "#F5E1E2"),
             ("2 editions", PINE, "#E1EDE5"),
             ("2 colour themes", GOLD, "#F6EDD8"),
             ("Excel & Google Sheets", INFO, "#E5E9F4")]
    fs = F("sans_sb", 24)
    total = sum(text_width(t, fs) + 44 for t, _, _ in items) + \
        18 * (len(items) - 1)
    cx = x - total / 2.0
    for t, fg, bg in items:
        cx = chip(img, cx, y, t, fg, bg)
    y += 76

    y = sshot(img, y, shot("\U0001F3E0 Dashboard", (1, 42), (1, 14)),
              width=CW)

    y = para(img, y,
             "Plan the whole festive season in one file: guests, the draw, "
             "exclusions, budgets, wishlists, the white elephant game and "
             "printable cards - all wired together so the dashboard "
             "updates itself.",
             size=26, x=MX + 60, w=CW - 120)
    img.paste(banner_strip(False, 190), (0, PH - 190))
    qa_page(img, 1, y, "cover")
    finish_page(img, 1)


# ---------------------------------------------------------------------------
# page 2 - what you get
# ---------------------------------------------------------------------------
def p02():
    img = new_page()
    y = 110
    y = h1(img, y, "YOUR DOWNLOAD", "What's in the box")

    y = h2(img, y, "Six workbooks")
    from etsy.crochet_lib import draw_table
    rows = [
        ["PREMIUM Noel / Arctic", "The full 12-tab tracker, blank and "
         "ready for your party"],
        ["PREMIUM EXAMPLE", "The same file filled with a demo party - "
         "peek at it first"],
        ["BASIC Noel / Arctic", "Guests, draw and budgets - the lean "
         "7-tab edition"],
        ["BASIC EXAMPLE", "The demo party in BASIC form"],
    ]
    from etsy.crochet_lib import draw_table as _dt
    _dt(img, MX, y, [430, 950 - 6],
        ["File", "What it is"],
        [[r[0], r[1]] for r in rows], row_h=64, hdr_h=54, size=19,
        hdr_size=17)
    y += 54 + 64 * len(rows) + 30

    y = h2(img, y, "PREMIUM or BASIC?")
    rows = [
        ["Guest list + RSVP", "yes", "yes"],
        ["Automatic Secret Santa draw", "yes", "yes"],
        ["Budget tracker", "yes", "yes"],
        ["Exclusions & house rules", "yes", "-"],
        ["Wishlists", "yes", "-"],
        ["White Elephant game board", "yes", "-"],
        ["Game history + live stats", "yes", "-"],
        ["Printable Santa cards", "yes", "-"],
    ]
    _dt(img, MX, y, [814, 300, 300 - 6],
        ["Feature", "PREMIUM", "BASIC"],
        rows, row_h=50, hdr_h=50, size=18, hdr_size=17)
    y += 50 + 50 * len(rows) + 26

    y = h2(img, y, "Where it works")
    y = bullets(img, y, [
        "Excel 2016 or later, Microsoft 365 - everything is native Excel "
        "(formulas, dropdowns, conditional formatting, charts).",
        "Google Sheets - upload the .xlsx to Drive and open with Sheets; "
        "the formulas translate automatically.",
        "Apple Numbers - drag the file onto Numbers; charts may need a "
        "small nudge, everything else converts cleanly.",
    ])
    y = note_card(img, y, "\U0001F512", "The maths is locked (on purpose)",
                  ["Every formula cell is protected so a stray keystroke "
                   "cannot break the tracker. Your typing cells - the "
                   "cream ones - stay open. Need to unlock something? The "
                   "Start Here tab inside the workbook explains how.",
                   "The EXAMPLE files are just for looking: start your "
                   "real party in a blank file."], PINE)
    qa_page(img, 2, y, "what you get")
    finish_page(img, 2)


# ---------------------------------------------------------------------------
# page 3 - settings
# ---------------------------------------------------------------------------
def p03():
    img = new_page()
    y = 100
    y = h1(img, y, "FIVE MINUTES, ONCE", "Set up your party")

    y = steps(img, y, [
        ("Open a blank PREMIUM file",
         "Start with Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel."
         "xlsx (or Arctic - same tracker, different colours)."),
        ("Go to the Settings tab",
         "Type your party name, date, host and location. The dashboard "
         "headline and the days-to-go counter follow instantly."),
        ("Set the gift budget",
         "Budget min and max per person (for example 20 - 35). Every "
         "budget row and the dashboard total use these numbers."),
        ("Pick a currency",
         "The currency symbol drives every money figure in the file."),
        ("Choose a draw seed",
         "Any whole number. The seed shuffles the draw - same seed, same "
         "draw; new seed, brand new draw."),
        ("Save the message",
         "The party message appears on the dashboard banner. Done - the "
         "tracker is ready for guests."),
    ])

    y = sshot(img, y,
              shot("\u2699\uFE0F Settings & Instructions", (1, 26), (1, 8)),
              width=CW)
    qa_page(img, 3, y, "settings")
    finish_page(img, 3)


# ---------------------------------------------------------------------------
# page 4 - participants
# ---------------------------------------------------------------------------
def p04():
    img = new_page()
    y = 100
    y = h1(img, y, "THE GUEST LIST", "Add your guests")

    y = para(img, y,
             "One row per guest on the Participants tab. Everything else "
             "in the workbook - the draw, the budget, the white elephant "
             "game - reads from this list, so add people here first.")

    y = sshot(img, y, shot("\U0001F465 Participants", (1, 22), (1, 10)),
              width=CW)

    y = h2(img, y, "The columns that matter")
    y = bullets(img, y, [
        "Name - first name plus surname initial works best for the "
        "printable cards.",
        "RSVP - a dropdown: Yes / Maybe / No. The chips up top count "
         "them live.",
        "Household & team - only used by the exclusion rules (PREMIUM). "
        "Guests in the same household never draw each other when the "
        "couple rule is on.",
        "Diet notes & gift status - free text plus a status dropdown "
        "(Not started, Gift purchased, Wrapped, Complete) that feeds the "
        "readiness chart.",
    ])
    y = note_card(img, y, "\u2705", "Rows you don't need",
                  ["Twelve rows are pre-formatted; blank rows simply stay "
                   "blank everywhere - the draw skips them and the "
                   "dashboard ignores them."], GOLD)
    qa_page(img, 4, y, "participants")
    finish_page(img, 4)


# ---------------------------------------------------------------------------
# page 5 - the draw
# ---------------------------------------------------------------------------
def p05():
    img = new_page()
    y = 100
    y = h1(img, y, "NO HAT, NO SLIPS", "Run the Secret Santa draw")

    y = para(img, y,
             "The draw tab assigns every guest exactly one recipient - no "
             "one draws themselves, and no pair repeats. The shuffle comes "
             "from your draw seed, so it is reproducible: change the seed "
             "on Settings and the whole draw reshuffles.")

    y = sshot(img, y, shot("\U0001F385 Secret Santa Draw", (1, 21), (1, 7)),
              width=1300)

    y = h2(img, y, "Reading the tab")
    y = bullets(img, y, [
        "Every filled guest row shows the drawn recipient plus a flag "
        "column - \u2705 OK means the pair passes every rule you armed.",
        "A warning flag means the pair brushes a rule (for example the "
        "same household). Change the seed for a clean re-draw, or type a "
        "name into the override column to fix a single pair by hand.",
        "The status chip shows when the draw is final and locked.",
        "The print button in your spreadsheet prints just the draw area - "
        "handy for the organiser's eyes only.",
    ])
    qa_page(img, 5, y, "draw")
    finish_page(img, 5)


# ---------------------------------------------------------------------------
# page 6 - rules
# ---------------------------------------------------------------------------
def p06():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Exclusions & house rules")

    y = para(img, y,
             "The Exclusions & Rules tab is where you tell the draw what "
             "is allowed. Flip a toggle to On and the draw respects it "
             "instantly.")

    y = sshot(img, y, shot("\U0001F6AB Exclusions & Rules", (1, 24),
                           (1, 13)), width=CW)

    y = h2(img, y, "The four levers")
    y = steps(img, y, [
        ("Household rule", "On: nobody draws someone in the same "
         "household (the Household column on Participants)."),
        ("Team rule", "On: work teams never draw each other - set the "
         "Team column first."),
        ("Last-year rule", "On: type last year's pairs into the draw's "
         "history column and they will not repeat. Keep it Off if this "
         "is your first year."),
        ("Custom no-pair list", "Any other pair that must never happen - "
         "feuding cousins, identical twins, the hosts. Two columns, as "
         "many rows as you like."),
    ])
    y = note_card(img, y, "\U0001F3AF", "The scoreboards up top",
                  ["Rules armed counts your active rules and custom pairs; "
                   "draw violations should read 0 after a fresh draw - if "
                   "not, nudge the seed once more."], BAD)
    qa_page(img, 6, y, "rules")
    finish_page(img, 6)


# ---------------------------------------------------------------------------
# page 7 - budget
# ---------------------------------------------------------------------------
def p07():
    img = new_page()
    y = 100
    y = h1(img, y, "MONEY, KEPT HONEST", "The budget tracker")

    y = para(img, y,
             "One row per giver, mirroring the draw. The min and max "
             "columns come straight from Settings, so a budget change "
             "updates every row at once.")

    y = sshot(img, y, shot("\U0001F4B0 Budget Tracker", (1, 21), (1, 9)),
              width=CW)

    y = h2(img, y, "How to use it")
    y = bullets(img, y, [
        "Actual spent - type what a gift really cost; the status column "
        "colours itself: under budget, within, or over.",
        "Receipt - tick \u2713 when the receipt is filed; the chip up "
        "top counts them.",
        "Reference & notes - order numbers, links, where the gift is "
        "hiding.",
        "The dashboard totals (total budget, actual spend, average gift "
        "cost) recalculate the moment you type.",
    ])
    y = note_card(img, y, "\U0001F6A8", "Over-budget alarm",
                  ["The over-budget chip on the Budget tab counts rows "
                   "above the max - glance at it before you buy, not "
                   "after."], WARN)
    qa_page(img, 7, y, "budget")
    finish_page(img, 7)


# ---------------------------------------------------------------------------
# page 8 - wishlists
# ---------------------------------------------------------------------------
def p08():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Wishlists that avoid doubles")

    y = para(img, y,
             "Guests jot down a few wishes each; whoever draws them can "
             "claim an idea with a tick so nobody buys the same thing "
             "twice.")

    y = sshot(img, y, shot("\U0001F381 Wishlists", (1, 21), (1, 7)),
              width=1300)

    y = h2(img, y, "The trick is the claim column")
    y = bullets(img, y, [
        "Guest, wish and a category (Must-love, Nice-to-have, Idea, "
        "Please-not) - a dropdown keeps it tidy.",
        "Claimed \u2713 marks an idea as taken; the chips count open "
        "must-loves so the important wishes never sit unclaimed.",
        "Price hint and link columns make remote shopping painless.",
        "Sort or filter the table by guest when you are doing the "
        "buying.",
    ])
    y = note_card(img, y, "\U0001F4B0", "Price hints keep budgets sane",
                  ["Wishes carry an optional price hint - when a guest "
                   "logs one, it lands right next to the budget range "
                   "from Settings, so the buyer instantly sees which "
                   "wishes fit the agreed budget and which need a group "
                   "top-up."], GOLD)
    qa_page(img, 8, y, "wishlists")
    finish_page(img, 8)


# ---------------------------------------------------------------------------
# page 9 - white elephant
# ---------------------------------------------------------------------------
def p09():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "The White Elephant board")

    y = para(img, y,
             "Ten gift slots, one row each. Seats are numbered "
             "automatically in a random-but-stable order, and the board "
             "tracks who holds what as the game unfolds.")

    y = sshot(img, y, shot("\U0001F3B2 White Elephant", (1, 21), (1, 12)),
              width=CW)

    y = h2(img, y, "Statuses, decoded")
    y = bullets(img, y, [
        "\U0001F381 Available - still on the table. \U0001F932 Held - "
        "someone owns it, for now. \U0001F504 Stolen - taken off someone; "
        "a stolen gift usually goes Final after the steal limit. "
        "\U0001F512 Final - locked, out of the game.",
        "The Now chip tells you exactly whose turn it is (seat number "
        "and name) based on the turns you have logged.",
        "The steals column counts thefts per gift - the dashboard chart "
        "turns it into instant drama.",
        "Max steals comes from Settings; when a gift hits the limit it "
        "locks itself Final.",
    ])
    y = note_card(img, y, "\U0001F4DD", "You never edit the board itself",
                  ["Holder, thief and status columns are all formulas "
                   "driven by the Game History tab on the next page - log "
                   "the turns there and this board plays itself. Only the "
                   "gift description and value columns are yours to "
                   "type."], INFO)
    qa_page(img, 9, y, "white elephant")
    finish_page(img, 9)


# ---------------------------------------------------------------------------
# page 10 - history + cards
# ---------------------------------------------------------------------------
def p10():
    img = new_page()
    y = 100
    y = h1(img, y, "PREMIUM FEATURE", "Game history & Santa cards")

    y = para(img, y,
             "Log every turn on the Game History tab - seat number, "
             "player, Pick / Steal / Pass, which gift - and the board, "
             "the Now chip and the dashboard all follow along by "
             "themselves.")

    y = sshot(img, y, shot("\U0001F504 Game History", (1, 16), (1, 6)),
              width=880)
    y = sshot(img, y, shot("\U0001F39F\uFE0F Santa Cards", (1, 19), (1, 9)),
              width=CW)

    y = para(img, y,
             "The Santa Cards tab lays out fold-and-cut cards: giver on "
             "the outside, recipient inside - the secret survives the "
             "handout. Print, cut, fold, deal.")
    qa_page(img, 10, y, "history + cards")
    finish_page(img, 10)


# ---------------------------------------------------------------------------
# page 11 - dashboard
# ---------------------------------------------------------------------------
def p11():
    img = new_page()
    y = 100
    y = h1(img, y, "ONE GLANCE", "The command centre")

    y = sshot(img, y, shot("\U0001F3E0 Dashboard", (1, 40), (1, 14)),
              width=CW)

    y = para(img, y,
             "Twelve KPI cards, four live charts, progress bars for "
             "purchases, wrapping and completion - every figure on this "
             "page is a formula, so it is always current. These are the "
             "same charts, redrawn from the demo party:")

    # four chart figures in a 2 x 2 grid, mirroring the real dashboard
    bw = (CW - 40) // 2
    bh = 300
    gx1, gx2 = MX, MX + bw + 40
    gy = y + 10

    givers = m.assign[:12]
    hbar_chart(img, (gx1, gy, gx1 + bw, gy + bh),
               "Actual spend per giver",
               list(zip(givers, m.spent)), color=PRIMARY, fmt="${:,.0f}",
               size=0.85)

    from collections import Counter
    stc = Counter(p["status"] for p in m.people)
    doughnut_chart(img, (gx2, gy, gx2 + bw, gy + bh),
                   "Gift readiness mix",
                   [(SC.ST_NOT, stc.get(SC.ST_NOT, 0), BAD),
                    (SC.ST_BOUGHT, stc.get(SC.ST_BOUGHT, 0), WARN),
                    (SC.ST_WRAPPED, stc.get(SC.ST_WRAPPED, 0), INFO),
                    (SC.ST_DONE, stc.get(SC.ST_DONE, 0), OK)],
                   size=0.85, center_word="guests")

    gy += bh + 34
    bygift = sorted(m.we, key=lambda r: r["giftnum"])
    hbar_chart(img, (gx1, gy, gx1 + bw, gy + bh), "Steals per gift",
               [(f"gift #{r['giftnum']}", r["steals"]) for r in bygift],
               color=PINE, fmt="{:,.0f}", size=0.85)

    grouped_columns(img, (gx2, gy, gx2 + bw, gy + bh),
                    "Gift values brought",
                    [f"#{r['giftnum']}" for r in bygift],
                    [("Value", [r["value"] for r in bygift], GOLD)],
                    fmt="${:,.0f}", size=0.85)

    y = gy + bh + 10
    qa_page(img, 11, y, "dashboard")
    finish_page(img, 11)


# ---------------------------------------------------------------------------
# page 12 - tips + support
# ---------------------------------------------------------------------------
def p12():
    img = new_page()
    y = 100
    y = h1(img, y, "FROM PARTY ANIMALS", "Ten tips for a smooth night")

    tips = [
        "Add every guest before you draw - new rows after the draw need "
        "a seed nudge.",
        "Draw early: the moment pairs exist, budgets and wishlists get "
        "useful.",
        "Change the seed, not the names, when a pair brushes a rule.",
        "Keep the couple rule On unless your crowd loves chaos.",
        "Log white elephant turns as they happen - the Now chip keeps "
        "arguments to zero.",
        "Photograph receipts the same night; the receipt column will "
        "thank you in January.",
        "Print Santa cards on stiff paper; they fold in half by "
        "themselves.",
        "Set Max steals to 2 or 3 - unlimited stealing is how friendships "
        "end.",
        "Duplicate the file per year: last year's pairs then feed the "
        "last-year rule.",
        "Open the dashboard on a tablet by the door; it doubles as the "
        "scoreboard.",
    ]
    f = F("sans_md", 24)
    col_w = (CW - 60) // 2
    for i, tip in enumerate(tips):
        col = i % 2
        row = i // 2
        tx = MX + col * (col_w + 60)
        ty = y + row * 128
        d = ImageDraw.Draw(img)
        d.ellipse([tx, ty + 4, tx + 44, ty + 48], fill=hexrgb(GOLD))
        draw_text(img, (tx + 22, ty + 10), str(i + 1),
                  F("display_b", 26), WHITE, anchor="ma")
        yy = ty
        for ln in wrap(tip, f, col_w - 70):
            draw_text(img, (tx + 62, yy), ln, f, INK)
            yy += 34
    y += 5 * 128 + 16

    y = h2(img, y, "Quick answers")
    qa = [
        ("Google Sheets?", "Yes - upload to Drive and open with Sheets. "
         "The dropdowns, formulas and conditional formatting translate "
         "automatically."),
        ("More than 12 guests?", "The pre-formatted rows cover a big "
         "party; blank rows are simply ignored, and you can insert more "
         "rows inside the table area."),
        ("Need to unlock a cell?", "The Start Here tab inside the "
         "workbook explains unlocking - you will not need it for normal "
         "use."),
    ]
    for q, a in qa:
        draw_text(img, (MX, y), q, F("sans_b", 24), PRIMARY)
        y += 34
        f2 = F("sans_md", 23)
        for ln in wrap(a, f2, CW - 20):
            draw_text(img, (MX, y), ln, f2, INK)
            y += 32
        y += 10

    y = note_card(img, y, "\U0001F9ED", "Support",
                  ["Questions, wishes or a stubborn formula? Message "
                   "Novality Store through the shop you bought from and "
                   "you will get a human answer.",
                   "Your purchase is a personal licence for your own "
                   "parties - please do not resell or share the files."],
                  PINE)
    qa_page(img, 12, y, "tips")
    finish_page(img, 12)


# ---------------------------------------------------------------------------
# PDF writer (JPEG pages in a hand-rolled PDF 1.4 container)
# ---------------------------------------------------------------------------
def write_pdf(pages, path, title, author):
    jpgs = []
    for im in pages:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=92, optimize=True,
                               subsampling=1)
        jpgs.append((buf.getvalue(), im.width, im.height))

    n = len(jpgs)
    objs = {}

    def put(oid, body):
        objs[oid] = body

    kids = " ".join(f"{3 + 3 * i} 0 R" for i in range(n))
    put(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    put(2, f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, (data, w, h) in enumerate(jpgs):
        wpt = w * 72.0 / DPI
        hpt = h * 72.0 / DPI
        put(3 + 3 * i,
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {wpt:.2f} "
             f"{hpt:.2f}] /Resources << /XObject << /Im{i} {5 + 3 * i} 0 R "
             f">> >> /Contents {4 + 3 * i} 0 R >>").encode())
        content = f"q {wpt:.2f} 0 0 {hpt:.2f} 0 0 cm /Im{i} Do Q".encode()
        put(4 + 3 * i,
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" +
            content + b"\nendstream")
        put(5 + 3 * i,
            (f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
             f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter "
             f"/DCTDecode /Length {len(data)} >>").encode() +
            b"\nstream\n" + data + b"\nendstream")
    esc = lambda s: s.replace("\\", r"\\").replace("(", r"\(").replace(
        ")", r"\)")
    put(3 + 3 * n, (f"<< /Title ({esc(title)}) /Author ({esc(author)}) "
                    f"/Creator (Novality Store) >>").encode())

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for oid in sorted(objs):
        offsets[oid] = out.tell()
        out.write(f"{oid} 0 obj\n".encode())
        out.write(objs[oid])
        out.write(b"\nendobj\n")
    xref_pos = out.tell()
    maxoid = max(objs)
    out.write(f"xref\n0 {maxoid + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for oid in range(1, maxoid + 1):
        out.write(f"{offsets.get(oid, 0):010d} 00000 n \n".encode())
    out.write((f"trailer\n<< /Size {maxoid + 1} /Root 1 0 R "
               f"/Info {3 + 3 * n} 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
               ).encode())
    with open(path, "wb") as fh:
        fh.write(out.getvalue())
    return os.path.getsize(path)


# ---------------------------------------------------------------------------
def main():
    for fn in (p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12):
        fn()
    assert len(PAGES) == TOTAL_PAGES, len(PAGES)
    size = write_pdf(PAGES, OUT_PDF,
                     "Secret Santa & White Elephant Party Tracker \u2014 "
                     "User Guide", "Novality Store")
    print(f"built {os.path.basename(OUT_PDF)}")
    print(f"  pages : {len(PAGES)}  (A4, {int(DPI)} dpi)")
    print(f"  size  : {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
