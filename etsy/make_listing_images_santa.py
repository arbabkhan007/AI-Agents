"""
make_listing_images_santa.py - the 15 Etsy listing images for the Secret
Santa & White Elephant Party Tracker, branded Novality Store.

2400 x 1800 px (4:3) JPEGs, each under 1 MB, drawn with the shared
crochet_lib design engine in the workbook's own Noel palette and
illustrated with REAL screenshots of the finished workbook
(tools/render_preview_santa.py on the PREMIUM Noel EXAMPLE file).

Run:  python3 -m etsy.make_listing_images_santa
Out:  etsy/images_santa/01_hero.jpg .. 15_faq.jpg
"""

import os
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy.crochet_lib import (F, check_poly, draw_text, fit_size, hexrgb,
                              rrect, shadow_paste, text_width, wrap)
from tools.render_preview_santa import render as render_sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "images_santa")
XLSX = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx")
XLSX_ARCTIC = os.path.join(
    ROOT, "products",
    "Secret_Santa_White_Elephant_Tracker_PREMIUM_Arctic.xlsx")
RAW_BANNER = os.path.join(ROOT, "assets", "raw_banner_noel.png")

W, H = 2400, 1800                     # 4:3 listing image
URL = "novalitystore.etsy.com  \u2022  Secret Santa & White Elephant " \
      "Party Tracker \u2014 Instant Download"
FOOT = "Secret Santa & White Elephant Party Tracker \u2014 Excel & Google " \
       "Sheets  \u2022  Instant Digital Download"

# ---------------------------------------------------------------------------
# palette - the workbook's own Noel theme
# ---------------------------------------------------------------------------
PRIMARY = "#8C1D2C"          # holly red
PINE = "#1F5C40"             # pine green
GOLD = "#B98A2E"             # antique gold
CANVAS = "#FBF6EE"
CARD = "#FFFFFF"
BORDER = "#E7D9C6"
INK = "#33221E"
MUTED = "#9A8474"
OK = "#1F5C40"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
WHITE = "#FFFFFF"
SOFT = {PRIMARY: "#F5E1E2", PINE: "#E1EDE5", GOLD: "#F6EDD8",
        INFO: "#E5E9F4", BAD: "#F7E2E0", WARN: "#FBF0D9", MUTED: "#F0EAE2"}


# ---------------------------------------------------------------------------
# screenshots of the real workbook
# ---------------------------------------------------------------------------
def shot(sheet, rows, cols, path=None, zoom=1.0):
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        render_sheet(path or XLSX, sheet, tmp, rows, cols, zoom)
        return Image.open(tmp).convert("RGBA")
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# frame-level helpers
# ---------------------------------------------------------------------------
def canvas():
    return Image.new("RGBA", (W, H), hexrgb(CANVAS))


def banner_img():
    return Image.open(RAW_BANNER).convert("RGB")


def strip(top=True, height=200):
    b = banner_img()
    crop = b.crop((0, 0, 1600, 300)) if top else \
        b.crop((0, 640 - 300, 1600, 640))
    return crop.resize((W, height), Image.LANCZOS).convert("RGBA")


def kicker(cv, cx, y, text, color=PRIMARY, size=34, track=10):
    d = ImageDraw.Draw(cv)
    f = F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size + 14


def headline(cv, cx, y, text, size=96, color=PRIMARY, spec="display_xb"):
    f, _ = fit_size(text, spec, size, W - 220, 30)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.32)


def subline(cv, cx, y, text, size=34, color=INK, spec="sans_md"):
    f, _ = fit_size(text, spec, size, W - 260, 16)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.7)


def chips_row(cv, cx, y, items, size=26, gap=28):
    """items = [(text, color)] centered row of pills."""
    fs, total = [], 0
    for text, color in items:
        f = F("sans_sb", size)
        w = text_width(text, f) + 48
        fs.append((text, color, f, w))
        total += w
    total += gap * (len(items) - 1)
    x = cx - total / 2.0
    for text, color, f, w in fs:
        d = ImageDraw.Draw(cv)
        rrect(d, [x, y, x + w, y + size + 32], (size + 32) / 2.0,
              fill=hexrgb(SOFT[color]))
        draw_text(cv, (x + 24, y + 15), text, f, color)
        x += w + gap
    return y + size + 32


def browser(screen, width, url=URL):
    """Browser chrome (warm cream) around a screen image. Returns RGBA."""
    chrome_h = 68
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#F0E9DD"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([30 + i * 38, 24, 48 + i * 38, 42], fill=hexrgb(c))
    pill = [width / 2.0 - 500, 15, width / 2.0 + 500, 53]
    rrect(d, pill, 19, fill=hexrgb(WHITE), outline=hexrgb("#E2D6C2"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 21, 980, 12)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 24, 26),
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


def sshot(cv, x, y, screen, width, url=URL):
    br = browser(screen, width, url)
    shadow_paste(cv, br, (int(x - br.width / 2), y), blur=24, alpha=60)
    return br.height


def side_card(cv, x, y, w, h, emoji, title, color, lines=None, body_pad=26,
              title_size=34, body_size=25):
    d = ImageDraw.Draw(cv)
    rrect(d, [x, y, x + w, y + h], 18, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    d.rectangle([x, y, x + 14, y + h], fill=hexrgb(color))
    draw_text(cv, (x + 34, y + 22), f"{emoji}  {title}",
              F("serif_b", title_size), color)
    yy = y + 22 + title_size + 18
    if lines:
        f = F("sans_md", body_size)
        for ln in lines:
            for j, part in enumerate(wrap(ln, f, w - 2 * body_pad - 30)):
                if j == 0:
                    check_poly(d, x + body_pad + 9, yy + body_size * 0.55,
                               body_size * 0.85, color, 3)
                draw_text(cv, (x + body_pad + 30, yy), part, f, INK)
                yy += int(body_size * 1.45)
            yy += 8
    return y + h


def num_circle(cv, cx, cy, n, r=56):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(PRIMARY))
    draw_text(cv, (cx, cy - 34), str(n), F("display_b", 52), WHITE,
              anchor="ma")


def arrow_right(cv, x, y, size=54, color=GOLD):
    d = ImageDraw.Draw(cv)
    d.line([x, y, x + size, y], fill=hexrgb(color), width=8)
    d.line([x + size - 18, y - 16, x + size, y], fill=hexrgb(color), width=8)
    d.line([x + size - 18, y + 16, x + size, y], fill=hexrgb(color), width=8)


def footer(cv, note=None):
    d = ImageDraw.Draw(cv)
    d.line([90, H - 96, W - 90, H - 96], fill=hexrgb(BORDER), width=2)
    draw_text(cv, (90, H - 72), note or FOOT, F("sans_md", 26), MUTED)
    draw_text(cv, (W - 90, H - 72), "\u00A9 Novality Store",
              F("sans_b", 26), PRIMARY, anchor="ra")


def hand_note(cv, x, y, text, size=44, color=GOLD, anchor="la"):
    f = F("hand", size)
    for i, ln in enumerate(text.split("\n")):
        draw_text(cv, (x, y + i * int(size * 1.15)), ln, f, color,
                  anchor=anchor)


def save(cv, name):
    os.makedirs(OUT, exist_ok=True)
    rgb = cv.convert("RGB")
    assert rgb.size == (W, H), f"{name}: wrong size {rgb.size}"
    path = os.path.join(OUT, name + ".jpg")
    for q in (90, 87, 84, 80, 76):
        rgb.save(path, "JPEG", quality=q, optimize=True)
        if os.path.getsize(path) <= 1024 * 1024:
            break
    kb = os.path.getsize(path) // 1024
    print(f"  {name}.jpg  {kb} KB")
    assert kb <= 1024, f"{name} exceeds 1 MB"


# ---------------------------------------------------------------------------
# 01 - hero
# ---------------------------------------------------------------------------
def img01():
    cv = canvas()
    cv.alpha_composite(strip(True, 200), (0, 0))
    y = kicker(cv, W / 2, 236, "NOVALITY STORE  \u2022  PREMIUM EDITION")
    f1, _ = fit_size("Secret Santa & White Elephant", "display_xb", 96,
                     W - 220, 40)
    draw_text(cv, (W / 2, y), "Secret Santa & White Elephant", f1, PRIMARY,
              anchor="ma")
    y += int(f1.size * 1.28)
    f2, _ = fit_size("Party Tracker", "display_xb", 96, W - 220, 40)
    draw_text(cv, (W / 2, y), "Party Tracker", f2, PINE, anchor="ma")
    y += int(f2.size * 1.5)
    y = subline(cv, W / 2, y,
                "The draw, the rules, the budgets and the white elephant "
                "game \u2014 one spreadsheet runs the whole party")
    y = chips_row(cv, W / 2, y + 14, [
        ("Instant Download", PINE), ("700+ Auto-Formulas", PRIMARY),
        ("12 Linked Tabs", GOLD), ("Excel & Google Sheets", INFO)])
    sshot(cv, W / 2, y + 20,
          shot("\U0001F3E0 Dashboard", (1, 40), (1, 14)), 1280)
    footer(cv)
    save(cv, "01_hero")


# ---------------------------------------------------------------------------
# 02 - dashboard
# ---------------------------------------------------------------------------
def img02():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE COMMAND CENTRE")
    y = headline(cv, W / 2, y + 4, "Your whole party, live", 88)
    y = subline(cv, W / 2, y + 2,
                "Guests, draw, budgets and game stats \u2014 recalculated "
                "the moment you type")
    dash = shot("\U0001F3E0 Dashboard", (1, 42), (1, 14))
    br = browser(dash, 1660)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 34
    chips_row(cv, W / 2, y2, [
        ("700+ formulas", PRIMARY), ("4 live charts", PINE),
        ("12 KPI cards", GOLD), ("Locked & safe", INFO)])
    side_card(cv, 90, y + 90, 470, 470, "\U0001F4CA", "Live numbers",
              PINE, [
        "12 KPI cards, always current",
        "Total budget vs actual spend",
        "Average gift cost, RSVPs, rules",
        "4 charts that draw themselves",
        "Progress bars, zero clicks",
    ])
    side_card(cv, W - 90 - 470, y + 90, 470, 470, "\u26A1", "Zero effort",
              PRIMARY, [
        "Log a turn or a receipt once \u2014",
        "the dashboard does the rest",
        "Days-to-go counter on the hero",
        "Works while the party happens",
        "Print-ready for the big night",
    ])
    footer(cv)
    save(cv, "02_dashboard")


# ---------------------------------------------------------------------------
# 03 - what's inside
# ---------------------------------------------------------------------------
def img03():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "WHAT'S INSIDE")
    y = headline(cv, W / 2, y + 4, "12 linked tabs, zero set-up", 86)
    y = subline(cv, W / 2, y + 2,
                "Every tab feeds the next \u2014 type a name once, watch "
                "the whole party wire itself together")
    tabs = [
        ("\U0001F3E0", "Dashboard", "KPIs & 4 live charts", PRIMARY),
        ("\U0001F465", "Participants", "guests, RSVP, households", PINE),
        ("\U0001F385", "Secret Santa Draw", "seed-driven, fair", PRIMARY),
        ("\U0001F6AB", "Exclusions & Rules", "couples, teams, customs",
         BAD),
        ("\U0001F4B0", "Budget Tracker", "per-giver, min to max", GOLD),
        ("\U0001F381", "Wishlists", "claim before you buy", INFO),
        ("\U0001F3B2", "White Elephant", "seats, gifts, steals", PINE),
        ("\U0001F504", "Game History", "the turn-by-turn log", INFO),
        ("\U0001F39F\uFE0F", "Santa Cards", "print, fold, deal", PRIMARY),
        ("\u2699\uFE0F", "Settings", "party basics & seeds", MUTED),
        ("\U0001F4D6", "Start Here", "the 5-minute tour", GOLD),
        ("\U0001F9E9", "_Data (hidden)", "the formula engine", MUTED),
    ]
    cols, gap = 4, 46
    cw = (W - 180 - gap * (cols - 1)) // cols
    ch = 380
    y += 56
    for i, (emoji, name, sub, color) in enumerate(tabs):
        cx = 90 + (i % cols) * (cw + gap)
        cy = y + (i // cols) * (ch + gap)
        side_card(cv, cx, cy, cw, ch, emoji, name, color, [sub],
                  body_pad=24, title_size=27, body_size=22)
    footer(cv)
    save(cv, "03_whats_inside")


# ---------------------------------------------------------------------------
# 04 - participants
# ---------------------------------------------------------------------------
def img04():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "STEP 1 \u2014 THE GUEST LIST")
    y = headline(cv, W / 2, y + 4, "Everyone in one place", 88)
    y = subline(cv, W / 2, y + 2,
                "RSVP dropdowns, households and teams \u2014 the raw "
                "material for a fair draw")
    sc = shot("\U0001F465 Participants", (1, 28), (1, 10))
    br = browser(sc, 1600)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\u2705", "Kept honest",
              PINE, [
        "RSVP: Yes / Maybe / No",
        "Diet notes for the buffet",
        "Gift status feeds the charts",
        "Blank rows are simply ignored",
        "Diet notes for the buffet",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F3E0",
              "Households & teams", PRIMARY, [
        "Couples never draw each other",
        "when the couple rule is on",
        "Teams stay apart too",
        "Just two extra columns \u2014",
        "the draw reads them itself",
    ])
    footer(cv)
    save(cv, "04_participants")


# ---------------------------------------------------------------------------
# 05 - the draw
# ---------------------------------------------------------------------------
def img05():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "STEP 2 \u2014 THE DRAW")
    y = headline(cv, W / 2, y + 4, "No hat. No paper slips.", 88)
    y = subline(cv, W / 2, y + 2,
                "Type a seed, get a full draw \u2014 nobody draws "
                "themselves, no pair repeats")
    sc = shot("\U0001F385 Secret Santa Draw", (1, 24), (1, 7))
    br = browser(sc, 1460)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2 - 210), y + 16),
                 blur=24, alpha=60)
    side_card(cv, W - 90 - 470, y + 80, 470, 500, "\U0001F3B2",
              "Seed magic", PRIMARY, [
        "Same seed \u2192 same draw",
        "New seed \u2192 fresh shuffle",
        "\u2705 OK flags check every rule",
        "Override a single pair by hand",
        "Nobody draws themselves \u2014",
        "ever, it is built in",
    ])
    hand_note(cv, 110, y + 580,
              "change the seed,\nreshuffle in seconds", 46)
    footer(cv)
    save(cv, "05_draw")


# ---------------------------------------------------------------------------
# 06 - rules
# ---------------------------------------------------------------------------
def img06():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "FAIR BY DEFAULT")
    y = headline(cv, W / 2, y + 4, "Rules that respect real life", 84)
    y = subline(cv, W / 2, y + 2,
                "Couples, teammates, last year's pairs and any grudge you "
                "can name \u2014 all off limits")
    sc = shot("\U0001F6AB Exclusions & Rules", (1, 24), (1, 13))
    br = browser(sc, 1700)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F3AF", "Armed & counted",
              BAD, [
        "The chips count your active rules and custom pairs \u2014 and "
        "draw violations should always read 0. If a pair brushes a rule, "
        "nudge the seed once.",
    ], body_size=26)
    footer(cv)
    save(cv, "06_rules")


# ---------------------------------------------------------------------------
# 07 - budget
# ---------------------------------------------------------------------------
def img07():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "MONEY, KEPT HONEST")
    y = headline(cv, W / 2, y + 4, "Budgets that police themselves", 80)
    y = subline(cv, W / 2, y + 2,
                "Set a min-max per person once \u2014 every row and the "
                "dashboard follow")
    sc = shot("\U0001F4B0 Budget Tracker", (1, 21), (1, 9))
    br = browser(sc, 1730)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\U0001F6A8", "Live flags", BAD, [
        "\U0001F534 under budget \u2022 \u2705 within",
        "\U0001F6A8 over budget, counted live",
        "Receipt column \u2014 tick \u2713 when filed",
        "Notes & reference numbers",
        "Over-budget chip counts live",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F4B8",
              "One number to change", GOLD, [
        "Budget min and max live on",
        "the Settings tab \u2014 change",
        "them there and every row,",
        "chart and KPI updates \u2014",
        "and the dashboard totals",
        "recalculate on the spot.",
    ])
    footer(cv)
    save(cv, "07_budget")


# ---------------------------------------------------------------------------
# 08 - wishlists
# ---------------------------------------------------------------------------
def img08():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "NO MORE DOUBLE GIFTS")
    y = headline(cv, W / 2, y + 4, "Wishlists with a claim column", 82)
    y = subline(cv, W / 2, y + 2,
                "Guests log wishes, buyers claim them \u2014 nobody buys "
                "the same thing twice")
    sc = shot("\U0001F381 Wishlists", (1, 24), (1, 7))
    br = browser(sc, 1580)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    side_card(cv, 90, y + 90, 440, 420, "\u2764\uFE0F", "Must-love radar",
              PRIMARY, [
        "Categories: Must-love,",
        "Nice-to-have, Idea, Please-not",
        "Open must-loves are counted",
        "so the big wishes get bought",
        "No more duplicate gifts",
    ])
    side_card(cv, W - 90 - 440, y + 90, 440, 420, "\U0001F517",
              "Shopping-ready", INFO, [
        "Price hints next to the budget",
        "Links straight to the product",
        "Filter by guest while buying",
        "Claims tick off with one key",
        "Price hints vs your budget",
    ])
    footer(cv)
    save(cv, "08_wishlists")


# ---------------------------------------------------------------------------
# 09 - white elephant
# ---------------------------------------------------------------------------
def img09():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE PARTY GAME, TAMED")
    y = headline(cv, W / 2, y + 4, "The White Elephant board", 88)
    y = subline(cv, W / 2, y + 2,
                "Seats, gifts, holders and steals \u2014 the board plays "
                "itself while you run the room")
    sc = shot("\U0001F3B2 White Elephant", (1, 24), (1, 12))
    br = browser(sc, 1560)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 14), blur=24,
                 alpha=60)
    y2 = y + 14 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F504",
              "Statuses, decoded", PINE, [
        "\U0001F381 Available \u2022 \U0001F932 Held \u2022 "
        "\U0001F504 Stolen \u2022 \U0001F512 Final \u2014 and the Now "
        "chip tells you exactly whose turn it is.",
    ], body_size=26)
    footer(cv)
    save(cv, "09_whiteelephant")


# ---------------------------------------------------------------------------
# 10 - history + cards
# ---------------------------------------------------------------------------
def img10():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "LOG IT ONCE")
    y = headline(cv, W / 2, y + 4, "History in, everything out", 84)
    y = subline(cv, W / 2, y + 2,
                "One row per turn \u2014 the board, the Now chip and the "
                "dashboard follow by themselves")
    sc = shot("\U0001F504 Game History", (1, 20), (1, 6))
    br1 = browser(sc, 1290)
    shadow_paste(cv, br1, (int(W / 2 - br1.width / 2 - 260), y + 14),
                 blur=24, alpha=60)
    sc2 = shot("\U0001F39F\uFE0F Santa Cards", (1, 19), (1, 9))
    br2 = browser(sc2, 1290)
    shadow_paste(cv, br2, (int(W / 2 - br2.width / 2 + 260),
                           y + 14 + (br1.height - br2.height) / 2),
                 blur=24, alpha=60)
    side_card(cv, W - 90 - 420, y + 60, 420, 500, "\U0001F39F\uFE0F",
              "Santa Cards", PRIMARY, [
        "Giver outside, recipient inside",
        "The secret survives the handout",
        "Print the tab, cut, fold, deal",
        "24 cards ready for big parties",
        "Every giver gets their slip",
        "The reveal stays a surprise",
    ])
    footer(cv)
    save(cv, "10_history_cards")


# ---------------------------------------------------------------------------
# 11 - two themes
# ---------------------------------------------------------------------------
def img11():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "TWO MOODS, ONE ENGINE")
    y = headline(cv, W / 2, y + 4, "Noel warmth or Arctic calm", 86)
    y = subline(cv, W / 2, y + 2,
                "Both themes ship in every download \u2014 pick your "
                "party's palette")
    noel = shot("\U0001F4D6 Start Here", (1, 24), (1, 10))
    arctic = shot("\U0001F4D6 Start Here", (1, 24), (1, 10),
                  path=XLSX_ARCTIC)
    bw = 1090
    br1 = browser(noel, bw)
    br2 = browser(arctic, bw)
    top = y + 24
    shadow_paste(cv, br1, (int(W / 2 - bw / 2 - 40), top), blur=24,
                 alpha=60)
    shadow_paste(cv, br2, (int(W / 2 - bw / 2 + 40),
                           top + br1.height - 74), blur=24, alpha=60)
    draw_text(cv, (140, top + br1.height - 130), "NOEL", F("sans_b", 30),
              PRIMARY)
    draw_text(cv, (W - 140, top + 2 * br1.height - 200), "ARCTIC",
              F("sans_b", 30), INFO, anchor="ra")
    footer(cv)
    save(cv, "11_themes")


# ---------------------------------------------------------------------------
# 12 - example file
# ---------------------------------------------------------------------------
def img12():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "SEE IT WORKING")
    y = headline(cv, W / 2, y + 4, "A demo party comes included", 82)
    y = subline(cv, W / 2, y + 2,
                "12 guests, 10 white elephant gifts, 14 turns \u2014 the "
                "EXAMPLE file shows every formula alive")
    sc = shot("\U0001F3B2 White Elephant", (1, 24), (1, 12))
    br = browser(sc, 1560)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 16), blur=24,
                 alpha=60)
    y2 = y + 16 + br.height + 30
    side_card(cv, W / 2 - 640, y2, 1280, 220, "\U0001F50D", "Peek first",
              GOLD, [
        "Open the EXAMPLE to see a finished party \u2014 then start your "
        "real one in the blank file. Same tabs, same maths, zero set-up.",
    ], body_size=26)
    footer(cv)
    save(cv, "12_example")


# ---------------------------------------------------------------------------
# 13 - how it works
# ---------------------------------------------------------------------------
def img13():
    cv = canvas()
    y = kicker(cv, W / 2, 110, "FROM DOWNLOAD TO DRAW IN 5 MINUTES")
    y = headline(cv, W / 2, y + 4, "How it works", 96)
    y = subline(cv, W / 2, y + 2,
                "Three steps \u2014 the spreadsheet does every hard part")
    steps = [
        ("Set the party", "Name, date, budget range and a draw seed on "
         "the Settings tab", PRIMARY),
        ("Add your guests", "One row per person with RSVP, household and "
         "team", PINE),
        ("Draw & play", "Press enter on the seed \u2014 pairs, budgets "
         "and the game board appear", GOLD),
    ]
    bw = 660
    gap = 90
    x0 = W / 2 - (3 * bw + 2 * gap) / 2
    top = y + 130
    for i, (title, body, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        side_card(cv, x, top, bw, 620, "", title, color, [body],
                  body_pad=30, title_size=36, body_size=26)
        num_circle(cv, x + bw / 2, top - 40, i + 1)
        if i < 2:
            arrow_right(cv, x + bw + gap / 2 - 30, top + 310, 60)
    y2 = top + 620 + 80
    y2 = chips_row(cv, W / 2, y2, [
        ("No macros", PINE), ("No setup files", PRIMARY),
        ("Works offline", GOLD), ("Google Sheets ready", INFO)])
    side_card(cv, W / 2 - 800, y2 + 56, 1600, 270, "\U0001F552",
              "Five minutes, once", GOLD, [
        "Most buyers go from download to a finished draw before the "
        "kettle boils \u2014 the Settings tab asks six questions and "
        "the rest is automatic."], body_size=26)
    footer(cv)
    save(cv, "13_howitworks")


# ---------------------------------------------------------------------------
# 14 - files
# ---------------------------------------------------------------------------
def img14():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "INSTANT DOWNLOAD")
    y = headline(cv, W / 2, y + 4, "4 files, one tidy folder", 90)
    y = subline(cv, W / 2, y + 2,
                "Yours the moment you check out \u2014 nothing to install, "
                "nothing to enable")
    files = [
        ("\U0001F7E9", "PREMIUM \u2014 Noel", "the full 12-tab tracker",
         PRIMARY),
        ("\U0001F7E7", "PREMIUM \u2014 Arctic", "same engine, cool tones",
         INFO),
        ("\u2728", "PREMIUM \u2014 EXAMPLE", "the demo party, filled in",
         GOLD),
        ("\U0001F4D8", "User Guide", "12-page illustrated PDF", PINE),
    ]
    bw, gap = 1000, 70
    x0 = W / 2 - (2 * bw + gap) / 2
    top = y + 100
    for i, (emoji, name, sub, color) in enumerate(files):
        x = x0 + (i % 2) * (bw + gap)
        yy = top + (i // 2) * 370
        side_card(cv, x, yy, bw, 330, emoji, name, color, [sub],
                  body_pad=30, title_size=32, body_size=25)
    y2 = top + 2 * 370 + 40
    y2 = side_card(cv, W / 2 - 800, y2, 1600, 300, "\U0001F9ED",
                   "Looking for a lighter start?", MUTED, [
        "The BASIC edition (7 tabs: guests, draw, budget, dashboard) is a "
        "separate listing in this shop \u2014 and the demo files let you "
        "peek before you plan.",
    ], body_size=25)
    footer(cv)
    save(cv, "14_files")


# ---------------------------------------------------------------------------
# 15 - FAQ
# ---------------------------------------------------------------------------
def img15():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "GOOD QUESTIONS")
    y = headline(cv, W / 2, y + 4, "Everything people ask", 90)
    y = subline(cv, W / 2, y + 2,
                "Straight answers before you buy")
    faq = [
        ("Does it work in Google Sheets?",
         "Yes \u2014 upload the .xlsx to Drive and open with Sheets; the "
         "formulas, dropdowns and colours translate automatically.", PINE),
        ("And in Excel?", "Excel 2016 or later on Windows and Mac, and "
         "Microsoft 365. No macros, nothing to enable.", PRIMARY),
        ("Can I break the formulas?",
         "No \u2014 every formula cell is locked for safety. All your "
         "typing cells (the cream ones) stay wide open.", GOLD),
        ("What if my party is huge?",
         "24 pre-formatted rows for guests and gifts; blank rows are "
         "ignored, and the EXAMPLE shows a full 12-person party.", INFO),
    ]
    top = y + 60
    for i, (q, a, color) in enumerate(faq):
        side_card(cv, 150, top, W - 300, 300, "\u2753", q, color, [a],
                  body_pad=32, title_size=31, body_size=25)
        top += 300 + 36
    footer(cv)
    save(cv, "15_faq")


# ---------------------------------------------------------------------------
def main():
    print("building santa listing images ...")
    for fn in (img01, img02, img03, img04, img05, img06, img07, img08,
               img09, img10, img11, img12, img13, img14, img15):
        fn()
    print("done \u2014 15 images in etsy/images_santa/")


if __name__ == "__main__":
    main()
