"""
make_user_guide.py - the illustrated "How to use it" PDF for the Christmas
Gift Tracker, branded Novality Store.

12 A4 pages at 200 dpi (1654 x 2339 px each), rendered with the same design
system as the listing images and illustrated with REAL screenshots of the
workbook (etsy/screens.py, driven by the live demo data).

Run:  python3 -m etsy.make_user_guide
Out:  Christmas_Gift_Tracker_User_Guide.pdf  (repo root)
"""

import io
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import screenlib as S
from etsy import screens as SC
from etsy.screenlib import (BORDER, BURGUNDY, CANVAS, CARD, CREAM, GOLD,
                            INK, INFO, MUTED, OK, PINE, PINE2, PLUM, SOFT,
                            WARN, WHITE, chip, COLORS, draw_text, fit_size,
                            hexrgb, rrect, shadow_paste, text_width, wrap)
from etsy.make_listing_images import (browser, chips_row, hand_note,
                                      num_circle, strip)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PDF = os.path.join(ROOT, "Christmas_Gift_Tracker_User_Guide.pdf")

PW, PH = 1654, 2339             # A4 at 200 dpi
DPI = 200.0
MX = 120                         # side margin
CW = PW - 2 * MX                 # content width 1414
BOTTOM = PH - 150                # footer zone starts here
TOTAL_PAGES = 12

m, bk = S.get_model()
A = {}
DASH = SC.screen_dashboard(m, bk, A)
GIFTS = SC.screen_gifts(m, bk)
BUDGET = SC.screen_budget(m, bk)
WISHLIST = SC.screen_wishlist(m, bk)
SHOPPING = SC.screen_shopping(m, bk)
ORDERS = SC.screen_orders(m, bk)
WRAPPING = SC.screen_wrapping(m, bk)
CARDS = SC.screen_cards(m, bk)
STOCKINGS = SC.screen_stockings(m, bk)
TODO = SC.screen_todo(m, bk)
SETUP = SC.screen_setup(m, bk)

PAGES = []


# ---------------------------------------------------------------------------
# page helpers
# ---------------------------------------------------------------------------
def new_page():
    return Image.new("RGBA", (PW, PH), hexrgb(CANVAS))


def finish_page(img, n, titled=True):
    assert n <= TOTAL_PAGES
    d = ImageDraw.Draw(img)
    if titled:
        d.line([MX, PH - 118, PW - MX, PH - 118], fill=hexrgb(BORDER),
               width=2)
        draw_text(img, (MX, PH - 96), "Christmas Gift Tracker — User Guide",
                  S.F("sans_md", 22), MUTED)
        draw_text(img, (PW - MX, PH - 96), f"Page {n} of {TOTAL_PAGES}",
                  S.F("sans_sb", 22), PINE, anchor="ra")
        draw_text(img, (PW / 2.0, PH - 96), "© Novality Store",
                  S.F("sans_b", 22), PINE, anchor="ma")
    PAGES.append(img)
    return img


def kicker(cv, cx, y, text, color=BURGUNDY, size=24, track=9):
    d = ImageDraw.Draw(cv)
    f = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size * 2.1


def h1(img, y, kick, title, size=86, color=PINE):
    y = kicker(img, PW / 2.0, y, kick, GOLD)
    f, _ = fit_size(title, "display_xb", size, CW, 30)
    draw_text(img, (PW / 2.0, y), title, f, color, anchor="ma")
    return y + int(f.size * 1.38)


def h2(img, y, text, color=PINE, size=44, x=MX):
    d = ImageDraw.Draw(img)
    f = S.F("serif_b", size)
    d.rectangle([x, y + 4, x + 12, y + size + 4], fill=hexrgb(color))
    draw_text(img, (x + 32, y), text, f, color)
    return y + size + 26


def para(img, y, text, size=28, color=INK, x=MX, w=CW, lead=1.55):
    f = S.F("sans_md", size)
    for line in wrap(text, f, w):
        draw_text(img, (x, y), line, f, color)
        y += int(size * lead)
    return y + 8


def bullets(img, y, items, size=26, x=MX, w=CW, color=OK, lead=1.5,
            gap=14, check=True):
    d = ImageDraw.Draw(img)
    for it in items:
        f = S.F("sans_md", size)
        lines = wrap(it, f, w - 56)
        first = True
        for ln in lines:
            if first and check:
                S._check_poly(d, x + 14, y + size * 0.62, size * 0.95,
                              color, max(3, int(size * 0.16)))
            elif first:
                d.ellipse([x + 8, y + size * 0.35, x + 20, y + size * 0.35 +
                           12], fill=hexrgb(color))
            draw_text(img, (x + 48, y), ln, f, INK)
            y += int(size * lead)
            first = False
        y += gap
    return y


def steps(img, y, items, size=27, x=MX, w=CW, r=27):
    for i, (title, body) in enumerate(items, 1):
        d = ImageDraw.Draw(img)
        cy = y + r + 4
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=hexrgb(GOLD))
        draw_text(img, (x + r, cy - 19), str(i), S.F("display_b", 34),
                  WHITE, anchor="ma")
        tx = x + 2 * r + 26
        draw_text(img, (tx, y), title, S.F("sans_b", size), PINE)
        yy = y + size + 8
        f = S.F("sans_md", size - 2)
        for ln in wrap(body, f, w - (2 * r + 26)):
            draw_text(img, (tx, yy), ln, f, INK)
            yy += int((size - 2) * 1.45)
        y = max(yy, cy + r + 10) + 18
    return y


def note_card(img, y, emoji, title, lines, color, h=None, size=25,
              x=MX, w=CW):
    pad = 30
    f = S.F("sans_md", size)
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
              S.F("serif_b", 30), WHITE)
    yy = y + 84
    for ln in wrapped:
        draw_text(img, (x + pad, yy), ln, f, INK)
        yy += int(size * 1.5)
    return y + hh


def sshot(img, y, screen, width=CW, url="Novality Store — Christmas Gift "
           "Tracker", crop=None):
    sc = screen.crop((0, 0, SW_CROP, crop[1])) if crop else screen
    br = browser(sc, width, url=url)
    shadow_paste(img, br, (int(PW / 2 - br.width / 2), y), blur=22,
                 alpha=60)
    return y + br.height + 26


SW_CROP = 1320


def qa_page(img, n, y_last, label):
    assert y_last <= BOTTOM, f"page {n} ({label}) overflows: {y_last} > " \
        f"{BOTTOM}"


# ---------------------------------------------------------------------------
# page 1 — cover
# ---------------------------------------------------------------------------
def p01():
    img = new_page()
    b = strip(True, 290)
    img.alpha_composite(b.resize((PW, 290), Image.LANCZOS), (0, 0))
    y = kicker(img, PW / 2, 330, "NOVALITY STORE  •  PREMIUM EDITION",
               BURGUNDY, 26, 10)
    f, _ = fit_size("Christmas Gift Tracker", "display_xb", 100, CW, 40)
    draw_text(img, (PW / 2, y), "Christmas Gift Tracker", f, PINE,
              anchor="ma")
    y += int(f.size * 1.34)
    d = ImageDraw.Draw(img)
    rrect(d, [PW / 2 - 300, y + 10, PW / 2 + 300, y + 96], 14,
          fill=hexrgb("#3A342B"))
    kicker(img, PW / 2, y + 32, "USER GUIDE", "#F3D98B", 30, 14)
    y += 130
    y = para(img, y, "Every gift, every dollar, every deadline — your "
            "five-minute tour of the planner that does the maths for you.",
            30, MUTED)
    crop = DASH.crop((0, 0, SW_CROP, A["after_gifts"]))
    y = sshot(img, y + 16, crop, 1300)
    y = chips_row(img, PW / 2, y + 20, [("Excel 2016 +", "ok"),
                  ("Microsoft 365", "ok"), ("Mac", "ok"),
                  ("Google Sheets", "ok"), ("No macros", "gold")], 24)
    hand_note(img, PW / 2, y + 36, "Your December, sorted 🎄", 56, BURGUNDY,
              "ma")
    draw_text(img, (PW / 2, PH - 130), "Version 2026  •  Festive & Minimal "
              "themes included  •  © Novality Store", S.F("sans_md", 22),
              MUTED, anchor="ma")
    PAGES.append(img)


# ---------------------------------------------------------------------------
# page 2 — what you downloaded
# ---------------------------------------------------------------------------
def p02():
    img = new_page()
    y = h1(img, 110, "CHAPTER 1", "What you downloaded")
    y = para(img, y + 6, "Your purchase arrived as three Excel files "
            "(.xlsx). Nothing to install, nothing to enable — here is what "
            "each one is for.")
    files = [
        ("🎁", "PREMIUM — Festive", "Your real planner. Classic Christmas "
         "reds & greens, watercolour cover.", PINE),
        ("🎁", "PREMIUM — Minimal", "The exact same engine in a clean, "
         "modern look. Pick whichever you prefer.", "#3A342B"),
        ("✨", "EXAMPLE — filled in", "The demo from the listing pictures: "
         "14 recipients, 25 gifts, every formula working.", GOLD),
    ]
    cw = (CW - 2 * 30) / 3.0
    for i, (em, name, desc, color) in enumerate(files):
        x = MX + i * (cw + 30)
        d = ImageDraw.Draw(img)
        rrect(d, [x, y, x + cw, y + 330], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, y, x + cw, y + 66], 16, fill=hexrgb(color))
        d.rectangle([x, y + 33, x + cw, y + 66], fill=hexrgb(color))
        f, _ = fit_size(f"{em}  {name}", "serif_b", 27, cw - 24, 14)
        draw_text(img, (x + cw / 2, y + 16), f"{em}  {name}", f, WHITE,
                  anchor="ma")
        yy = y + 92
        for ln in wrap(desc, S.F("sans_md", 23), cw - 44):
            draw_text(img, (x + 22, yy), ln, S.F("sans_md", 23), INK)
            yy += 34
        draw_text(img, (x + cw / 2, y + 268), "Excel & Google Sheets",
                  S.F("sans_sb", 19), MUTED, anchor="ma")
    hand_note(img, MX + CW - 130, y + 336, "start here! ↓", 40, BURGUNDY,
              "ra")
    y += 400
    y = note_card(img, y, "💡", "OPEN THE EXAMPLE FILE FIRST", [
        "Spend two minutes clicking around a tracker that is already full.",
        "When you are ready to plan for real, open a PREMIUM file and type "
        "over the demo content — or start from a blank row."], GOLD)
    y = h2(img, y + 26, "⚙️ What you need")
    y = bullets(img, y, [
        "Excel 2016 or later (Windows or Mac), or Microsoft 365 — no older "
        "versions, no OpenOffice",
        "Google Sheets: import the file in four clicks (full walkthrough on "
        "page 11)",
        "No macros, no add-ins, no internet needed — it is pure formulas, "
        "so it also works offline",
        "A printer, if you like paper: every tab is already set up to print "
        "neatly"], 25)
    y = note_card(img, y + 18, "🔒", "IF EXCEL SHOWS A YELLOW BAR", [
        "Files downloaded from the internet open in Protected View. Click "
        "“Enable Editing” at the top and everything wakes up. There are no "
        "macros in this file, so nothing else is required."], WARN)
    qa_page(img, 2, y, "files")
    finish_page(img, 2)


# ---------------------------------------------------------------------------
# page 3 — the 3-minute setup
# ---------------------------------------------------------------------------
def p03():
    img = new_page()
    y = h1(img, 110, "CHAPTER 2", "The three-minute setup")
    y = sshot(img, y + 4, SETUP, 1070,
              url="Novality Store — Setup tab")
    y = steps(img, y + 4, [
        ("Set your event", "⚙️ Setup → Event name and Event date. Every "
         "countdown, deadline and key date in the workbook is calculated "
         "from that one date — nothing is hard-coded to a year."),
        ("Make the money yours", "On the same tab: currency, total budget, "
         "the % that triggers the budget warning, and how many days count "
         "as “due soon”."),
        ("Type your people", "⚙️ Setup → Your lists: recipients, "
         "relationships, stores, categories, hiding spots. Every dropdown "
         "in every tab reads from these lists."),
        ("Add your gifts", "🎁 Gift Tracker: one row per present. Use the "
         "Status dropdown as your pipeline — idea to delivered."),
        ("Plan the money", "💰 Budget: type a planned amount per category. "
         "Everything else on that tab is automatic."),
        ("Enjoy the dashboard", "🎄 Dashboard needs no typing at all — it "
         "recalculates the moment you change anything anywhere.")], 26)
    y = note_card(img, y + 10, "🥇", "THE GOLDEN RULES", [
        "White cells are yours — type in them freely. Tinted cells are "
        "formula cells: they are locked so the maths can never break.",
        "Pick ✓ from the dropdowns instead of typing it — the tick columns "
        "feed the dashboards.",
        "Don’t rename tabs or delete the hidden _Data sheet; the whole "
        "workbook reads from them."], PINE, size=24)
    qa_page(img, 3, y, "setup")
    finish_page(img, 3)


# ---------------------------------------------------------------------------
# page 4 — dashboard
# ---------------------------------------------------------------------------
def p04():
    img = new_page()
    y = h1(img, 110, "CHAPTER 3", "The Dashboard — your command centre")
    y = para(img, y + 4, "You never type on this tab. It is a live picture "
            "of everything you have done everywhere else — open it every "
            "morning of December and it will tell you what needs doing.")
    crop = DASH.crop((0, 0, SW_CROP, A["after_gifts"]))
    y = sshot(img, y + 6, crop, CW)
    y = h2(img, y + 6, "🧭 What each part is telling you")
    y = bullets(img, y, [
        "⏳ Countdown band — days and weeks until Christmas, from your "
        "event date",
        "💰 Money cards — budget, spent, remaining and % used, plus the "
        "amber warning when you cross your alert level",
        "🎁 Progress cards — planned, bought, wrapped, given, on order, "
        "average spend per person",
        "█░ Progress bars — the block bars fill up as you buy and wrap",
        "📊 Four charts — spending per person, budget vs actual, where the "
        "gifts are at, bought vs still to buy",
        "🎯 What’s left to do — plain-English sentences written by the "
        "formulas (“4 gifts still to buy, 3 already on order…”)",
        "⏰ Next deadlines — the five closest dates from every tab, with a "
        "days-left chip that goes amber inside your due-soon window",
        "🎅 Per-recipient summary — budget vs spend and a mini bar for "
        "every person on your list"], 24)
    qa_page(img, 4, y, "dashboard")
    finish_page(img, 4)


# ---------------------------------------------------------------------------
# page 5 — gift tracker
# ---------------------------------------------------------------------------
def p05():
    img = new_page()
    y = h1(img, 110, "CHAPTER 4", "Gift Tracker — the heart of it")
    y = chips_row(img, PW / 2, y + 2, [("💡 Idea", "plum"),
                  ("🛒 Need to Buy", "warn"), ("🛍️ Ordered", "info"),
                  ("✅ Purchased", "ok"), ("🎀 Wrapped", "gold"),
                  ("📦 Delivered", "burgundy")], 23)
    y = sshot(img, y + 8, GIFTS, 1290, url="Novality Store — Gift Tracker")
    y = h2(img, y + 4, "✍️ How to fill it in")
    y = bullets(img, y, [
        "One row per present: who it is for, the idea, category, store and "
        "your budget — the dropdowns read your Setup lists",
        "The Status column is your pipeline: move each gift along the six "
        "stages as you go; the dashboard counts them automatically",
        "Cost, difference, % of budget, days left and the alert column are "
        "all tinted — they fill themselves in",
        "Buy-by dates come from your event date; a gift inside the due-soon "
        "window turns amber, an overdue one turns red",
        "Wrapped ✓ and Given ✓ are the last two ticks — tick them and the "
        "Wrapping tab updates itself"], 24)
    qa_page(img, 5, y, "gifts")
    finish_page(img, 5)


# ---------------------------------------------------------------------------
# page 6 — budget
# ---------------------------------------------------------------------------
def p06():
    img = new_page()
    y = h1(img, 110, "CHAPTER 5", "Budget — watch every dollar")
    y = sshot(img, y + 4, BUDGET, 1240, url="Novality Store — Budget tab")
    y = h2(img, y + 4, "🧮 Planned vs automatic vs manual")
    y = bullets(img, y, [
        "Planned — type your target for each of the 10 categories (rename "
        "them if your Christmas looks different)",
        "Pulled in automatically — the tinted column adds up the real money "
        "from the Gift Tracker, Shopping List, Stockings and card postage",
        "Extras — for spending that lives outside the tabs (travel, the "
        "tree, the turkey), type it once in the manual column",
        "Remaining and % used recalculate instantly; a category over budget "
        "turns red, nearly over turns amber",
        "The banner at the top warns you in plain English the moment you "
        "cross the % you set in Setup (default 85%)"], 24)
    qa_page(img, 6, y, "budget")
    finish_page(img, 6)


# ---------------------------------------------------------------------------
# page 7 — wish list & shopping
# ---------------------------------------------------------------------------
def p07():
    img = new_page()
    y = h1(img, 110, "CHAPTER 6", "Wish List & Shopping List")
    y = h2(img, y + 2, "💡 Wish List — ideas all year round")
    y = sshot(img, y + 2, WISHLIST, 1300, crop=(0, 560),
              url="Novality Store — Wish List")
    y = bullets(img, y - 16, [
        "Park every “they mentioned it in March” idea here, ranked "
        "⭐ to ⭐⭐⭐ Must Have",
        "The last column tells you when an idea has already made it onto "
        "the gift list — no duplicate presents"], 24, gap=8)
    y = h2(img, y + 10, "🛍️ Shopping List — the quiet budget-eaters")
    y = sshot(img, y + 2, SHOPPING, 1300, crop=(0, 560),
              url="Novality Store — Shopping List")
    y = bullets(img, y - 16, [
        "Wrapping paper, cards, baking, decorations, party bits — with "
        "quantities and unit costs",
        "Everything you tick as bought rolls straight into the Budget tab, "
        "so December surprises stop happening"], 24, gap=8)
    qa_page(img, 7, y, "wish+shop")
    finish_page(img, 7)


# ---------------------------------------------------------------------------
# page 8 — orders & wrapping
# ---------------------------------------------------------------------------
def p08():
    img = new_page()
    y = h1(img, 110, "CHAPTER 7", "Order Tracker & Wrapping")
    y = h2(img, y + 2, "📦 Online Order Tracker")
    y = sshot(img, y + 2, ORDERS, 1180,
              url="Novality Store — Order Tracker")
    y = bullets(img, y - 14, [
        "Order number, store, cost, expected and actual arrival dates — one "
        "row per parcel",
        "Days-left counts down from your event date; the day after it was "
        "due, a parcel turns red — chase the courier",
        "The returns window is calculated for you (typically 14 January)"], 
        24, gap=8)
    y = h2(img, y + 12, "🎀 Wrapping & Hiding")
    y = sshot(img, y + 2, WRAPPING, 1180, crop=(0, 700),
              url="Novality Store — Wrapping tab")
    y = bullets(img, y - 14, [
        "Mirrors your gift list automatically — add the hiding spot and "
        "the To/From tag",
        "Wrapped and handed-over are tracked separately, so nothing gets "
        "“found” early and nothing is left under the bed on 26 December"],
        24, gap=8)
    qa_page(img, 8, y, "orders+wrap")
    finish_page(img, 8)


# ---------------------------------------------------------------------------
# page 9 — cards & stockings
# ---------------------------------------------------------------------------
def p09():
    img = new_page()
    y = h1(img, 110, "CHAPTER 8", "Card Tracker & Stockings")
    y = h2(img, y + 2, "💌 Christmas Card Tracker")
    y = sshot(img, y + 2, CARDS, 1130, url="Novality Store — Card Tracker")
    y = bullets(img, y - 14, [
        "Bought → written → posted → replied: four ticks per person, "
        "nobody gets forgotten",
        "Postage is added up and lands in your Budget automatically"], 24,
        gap=8)
    y = h2(img, y + 12, "🧦 Stocking Stuffer Tracker")
    y = sshot(img, y + 2, STOCKINGS, 1130,
              url="Novality Store — Stockings")
    y = bullets(img, y - 14, [
        "The little things add up fastest — budget per stocking and watch "
        "the per-owner summary",
        "Bought, wrapped and hidden are tracked per filler; costs roll "
        "into the Budget tab"], 24, gap=8)
    qa_page(img, 9, y, "cards+stock")
    finish_page(img, 9)


# ---------------------------------------------------------------------------
# page 10 — to-do + reuse
# ---------------------------------------------------------------------------
def p10():
    img = new_page()
    y = h1(img, 110, "CHAPTER 9", "To-Do List & next Christmas")
    y = sshot(img, y + 4, TODO, 1180, url="Novality Store — To-Do List")
    y = bullets(img, y - 14, [
        "20 classic Christmas tasks come pre-loaded, each with a deadline "
        "calculated from your event date",
        "Tick the ✓ column as you go; overdue tasks turn red, coming-up "
        "ones amber"], 24, gap=8)
    y = h2(img, y + 14, "♻️ Use it again next year — and for every "
           "occasion")
    y = steps(img, y, [
        ("Change the date", "⚙️ Setup → Event date → 25 Dec 2027 (or any "
         "occasion: birthdays, Diwali, weddings…). Every countdown, "
         "deadline and to-do re-dates itself."),
        ("Clear your rows", "Select the white cells in the Gift Tracker, "
         "Orders, Cards, Stockings and To-Do tabs and press Delete. Your "
         "people, stores and categories in Setup stay put."),
        ("Start planning", "Your Wish List carried over — the ideas you "
         "parked in January are exactly where you need them in November.")],
        26)
    y = chips_row(img, PW / 2, y + 14, [("🎄 Christmas", "pine"),
                  ("🎅 Secret Santa", "burgundy"), ("🎂 Birthdays",
                  "info"), ("💍 Weddings", "plum"), ("🪔 Diwali", "warn"),
                  ("🍼 Baby Shower", "ok"), ("+ 12 more", "gold")], 22)
    qa_page(img, 10, y, "todo+reuse")
    finish_page(img, 10)


# ---------------------------------------------------------------------------
# page 11 — google sheets
# ---------------------------------------------------------------------------
def p11():
    img = new_page()
    y = h1(img, 110, "CHAPTER 10", "Using it in Google Sheets")
    y = para(img, y + 4, "The same file works in both. Start in Excel, "
            "move to Sheets, or skip Excel entirely — the import takes "
            "under a minute.")
    y = steps(img, y + 6, [
        ("Open Sheets", "Go to sheets.google.com (free with any Google "
         "account) and start a blank spreadsheet."),
        ("File → Import", "Choose the Upload tab and drag your .xlsx file "
         "in — or click “Select a file from your device”."),
        ("Replace spreadsheet", "In Import settings choose “Replace "
         "spreadsheet” so every tab arrives together, then click Import "
         "data."),
        ("Done", "Dropdowns, colours, conditional formatting, locked cells "
         "and charts all come along. Formulas become Google-native "
         "formulas.")], 28)
    y = h2(img, y + 8, "✅ What converts")
    y = bullets(img, y, [
        "All 2,500+ formulas (translated to Google Sheets equivalents)",
        "All 56 dropdown menus and every conditional-format colour rule",
        "Sheet protection — the formula cells stay locked in Sheets too",
        "Charts — Google Sheets rebuilds them from the same data"], 24)
    y = note_card(img, y + 16, "💡", "GOOD TO KNOW", [
        "Keep the original .xlsx — it is your master copy and works in "
        "Excel, Google Sheets and (formulas only) Apple Numbers.",
        "Editing on the phone app works for quick ticks; the dashboard is "
        "happiest on a laptop or tablet screen."], INFO, size=24)
    qa_page(img, 11, y, "sheets")
    finish_page(img, 11)


# ---------------------------------------------------------------------------
# page 12 — troubleshooting, license, closing
# ---------------------------------------------------------------------------
def p12():
    img = new_page()
    y = h1(img, 110, "CHAPTER 11", "Troubleshooting & FAQ")
    faqs = [
        ("The numbers look wrong or stale",
         "Press F9 (Ctrl+F9 on Mac) to force a recalculation. In Google "
         "Sheets reload the page. If you typed into a tinted cell by "
         "mistake, press Ctrl+Z."),
        ("A dropdown is missing a name",
         "Add the person or store on the ⚙️ Setup tab — every dropdown "
         "updates instantly."),
        ("I typed in a formula cell and it broke",
         "The tinted cells are locked, so this should not be possible. If "
         "a value looks odd, Ctrl+Z straight away, or re-download your "
         "files from Etsy."),
        ("Can I add more rows?",
         "Yes — insert rows inside the existing tables (not above the "
         "first row) and the formulas copy down with them."),
        ("Can I print it?",
         "Every tab has print areas set. File → Print, and it fits the "
         "page — the block progress bars are designed for exactly that."),
        ("Where do I get updates?",
         "Lifetime updates are included: re-download from Etsy → You → "
         "Purchases any time."),
    ]
    for q, a in faqs:
        d = ImageDraw.Draw(img)
        hh = 176
        rrect(d, [MX, y, MX + CW, y + hh], 14, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(img, (MX + 30, y + 20), "Q", S.F("display_b", 40), GOLD)
        draw_text(img, (MX + 82, y + 24), q, S.F("serif_b", 30), PINE)
        yy = y + 84
        for ln in wrap(a, S.F("sans_md", 22), CW - 130)[:2]:
            draw_text(img, (MX + 82, yy), ln, S.F("sans_md", 22), INK)
            yy += 33
        y += hh + 20
    y = note_card(img, y + 8, "📜", "LICENSE & SUPPORT", [
        "Personal use — one household per purchase. Not for resale or "
        "redistribution.",
        "Stuck or spotted a bug? Message Novality Store on Etsy — we reply "
        "within a day."], "#3A342B", size=24)
    img.alpha_composite(strip(False, 150).resize((PW, 150), Image.LANCZOS),
                        (0, PH - 150))
    draw_text(img, (PW / 2, PH - 118), "Thank you for supporting our small "
              "shop — Novality Store", S.F("hand", 54), BURGUNDY, anchor="ma")
    PAGES.append(img)


# ---------------------------------------------------------------------------
# minimal PDF writer (JPEG pages, full control of quality)
# ---------------------------------------------------------------------------
def write_pdf(pages, path, title, author):
    jpgs = []
    for im in pages:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=92, optimize=True,
                               subsampling=1)
        jpgs.append((buf.getvalue(), im.width, im.height))

    n = len(jpgs)
    # object ids: 1 catalog, 2 pages, per page i: 3+3i page, 4+3i content,
    # 5+3i image; then 3+3n = info
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
                     "Christmas Gift Tracker — User Guide",
                     "Novality Store")
    print(f"built {os.path.basename(OUT_PDF)}")
    print(f"  pages : {len(PAGES)}  (A4, {int(DPI)} dpi)")
    print(f"  size  : {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
