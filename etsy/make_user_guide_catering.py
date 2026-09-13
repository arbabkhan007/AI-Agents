"""
make_user_guide_catering.py - the illustrated "How to use it" PDF for the
Catering Business Manager, branded Novality Store.

12 A4 pages at 200 dpi (1654 x 2339 px each), rendered with the same design
system as the listing images and illustrated with REAL screenshots of the
workbook (etsy/catering_screens.py, driven by the live demo data).

Run:  python3 -m etsy.make_user_guide_catering
Out:  Catering_Business_Manager_User_Guide.pdf  (repo root)
"""

import io
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import catering_lib as S
from etsy import catering_screens as SC
from etsy.catering_lib import (BORDER, CANVAS, CARD, COPPER, ESPRESSO, INK,
                               INFO, MUTED, OK, PLUM, SOFT, WARN, WHITE,
                               BRASS, LATTE, COLORS)
from etsy.catering_lib import draw_text, fit_size, get_model, hexrgb, rrect
from etsy.make_listing_images_catering import (browser, chips_row,
                                               hand_note, strip)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PDF = os.path.join(ROOT, "Catering_Business_Manager_User_Guide.pdf")

PW, PH = 1654, 2339             # A4 at 200 dpi
DPI = 200.0
MX = 120                         # side margin
CW = PW - 2 * MX                 # content width 1414
BOTTOM = PH - 150                # footer zone starts here
TOTAL_PAGES = 12

m = get_model()
DASH = SC.screen_dashboard(m)
EVENTS = SC.screen_events(m)
CLIENTS = SC.screen_clients(m)
QUOTE = SC.screen_quote(m)
MENU = SC.screen_menu(m)
INVENTORY = SC.screen_inventory(m)
SHOPPING = SC.screen_shopping(m)
EXPENSES = SC.screen_expenses(m)
INCOME = SC.screen_income(m)
STAFF = SC.screen_staff(m)
EQUIPMENT = SC.screen_equipment(m)
CALENDAR = SC.screen_calendar(m)
REPORTS = SC.screen_reports(m)
SETUP = SC.screen_setup(m)

PAGES = []
SW_CROP = 1320


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
        draw_text(img, (MX, PH - 96), "Catering Business Manager — User "
                  "Guide", S.F("sans_md", 22), MUTED)
        draw_text(img, (PW - MX, PH - 96), f"Page {n} of {TOTAL_PAGES}",
                  S.F("sans_sb", 22), ESPRESSO, anchor="ra")
        draw_text(img, (PW / 2.0, PH - 96), "© Novality Store",
                  S.F("sans_b", 22), ESPRESSO, anchor="ma")
    PAGES.append(img)
    return img


def kicker(cv, cx, y, text, color=COPPER, size=24, track=9):
    d = ImageDraw.Draw(cv)
    f = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size * 2.1


def h1(img, y, kick, title, size=84, color=ESPRESSO):
    y = kicker(img, PW / 2.0, y, kick, COPPER)
    f, _ = fit_size(title, "display_xb", size, CW, 30)
    draw_text(img, (PW / 2.0, y), title, f, color, anchor="ma")
    return y + int(f.size * 1.38)


def h2(img, y, text, color=ESPRESSO, size=42, x=MX):
    d = ImageDraw.Draw(img)
    f = S.F("serif_b", size)
    d.rectangle([x, y + 4, x + 12, y + size + 4], fill=hexrgb(color))
    draw_text(img, (x + 32, y), text, f, color)
    return y + size + 26


def para(img, y, text, size=28, color=INK, x=MX, w=CW, lead=1.55):
    f = S.F("sans_md", size)
    from etsy.catering_lib import wrap
    for line in wrap(text, f, w):
        draw_text(img, (x, y), line, f, color)
        y += int(size * lead)
    return y + 8


def bullets(img, y, items, size=25, x=MX, w=CW, color=OK, lead=1.5,
            gap=12, check=True):
    from etsy.catering_lib import wrap
    d = ImageDraw.Draw(img)
    for it in items:
        f = S.F("sans_md", size)
        lines = wrap(it, f, w - 56)
        first = True
        for ln in lines:
            if first and check:
                S.check_poly(d, x + 14, y + size * 0.62, size * 0.95,
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
    from etsy.catering_lib import wrap
    for i, (title, body) in enumerate(items, 1):
        d = ImageDraw.Draw(img)
        cy = y + r + 4
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=hexrgb(COPPER))
        draw_text(img, (x + r, cy - 19), str(i), S.F("display_b", 34),
                  WHITE, anchor="ma")
        tx = x + 2 * r + 26
        draw_text(img, (tx, y), title, S.F("sans_b", size), ESPRESSO)
        yy = y + size + 8
        f = S.F("sans_md", size - 2)
        for ln in wrap(body, f, w - (2 * r + 26)):
            draw_text(img, (tx, yy), ln, f, INK)
            yy += int((size - 2) * 1.45)
        y = max(yy, cy + r + 10) + 16
    return y


def note_card(img, y, emoji, title, lines, color, h=None, size=24,
              x=MX, w=CW):
    from etsy.catering_lib import wrap
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


def sshot(img, y, screen, width=CW, url="Novality Store — Catering "
           "Business Manager", crop=None):
    sc = screen.crop((0, 0, SW_CROP, crop[1])) if crop else screen
    br = browser(sc, width, url=url)
    S.shadow_paste(img, br, (int(PW / 2 - br.width / 2), y), blur=22,
                   alpha=60)
    return y + br.height + 26


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
               COPPER, 26, 10)
    f, _ = fit_size("Catering Business Manager", "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2, y), "Catering Business Manager", f, ESPRESSO,
              anchor="ma")
    y += int(f.size * 1.34)
    d = ImageDraw.Draw(img)
    rrect(d, [PW / 2 - 300, y + 10, PW / 2 + 300, y + 96], 14,
          fill=hexrgb("#3A2E22"))
    kicker(img, PW / 2, y + 32, "USER GUIDE", "#F3D98B", 30, 14)
    y += 130
    y = para(img, y, "Every event, every plate, every dollar — your "
            "five-minute tour of the system that does the maths for you.",
            30, MUTED)
    crop = DASH.crop((0, 0, SW_CROP, 1000))
    y = sshot(img, y + 16, crop, 1300)
    y = chips_row(img, PW / 2, y + 20, [("Excel 2016 +", "ok"),
                  ("Microsoft 365", "ok"), ("Mac", "ok"),
                  ("Google Sheets", "ok"), ("No macros", "copper")], 24)
    hand_note(img, PW / 2, y + 36, "Your season, sorted", 56, COPPER, "ma")
    draw_text(img, (PW / 2, PH - 130), "Version 1.0  •  Classic & Fresh "
              "themes included  •  © Novality Store", S.F("sans_md", 22),
              MUTED, anchor="ma")
    PAGES.append(img)


# ---------------------------------------------------------------------------
# page 2 — what you downloaded
# ---------------------------------------------------------------------------
def p02():
    img = new_page()
    y = h1(img, 110, "CHAPTER 1", "What you downloaded")
    y = para(img, y + 6, "Your purchase arrived as Excel workbooks "
            "(.xlsx). Nothing to install, nothing to enable — here is what "
            "each file is for.")
    files = [
        ("\U0001F451", "PREMIUM — Classic", "Your complete system: 20 "
         "linked tabs, 1,500+ formulas.", ESPRESSO),
        ("\U0001F451", "PREMIUM — Fresh", "The same engine in the lighter "
         "Fresh theme. Pick your favourite.", COPPER),
        ("\u2728", "EXAMPLE — filled in", "The demo from the listing "
         "pictures: 14 events, every formula working.", BRASS),
        ("\U0001F4D8", "USER GUIDE — this PDF", "Keep it handy: a page "
         "per chapter, plus the Google Sheets walkthrough.", LATTE),
    ]
    cw = (CW - 3 * 24) / 4.0
    for i, (em, name, desc, color) in enumerate(files):
        x = MX + i * (cw + 24)
        d = ImageDraw.Draw(img)
        rrect(d, [x, y, x + cw, y + 380], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, y, x + cw, y + 66], 16, fill=hexrgb(color))
        d.rectangle([x, y + 33, x + cw, y + 66], fill=hexrgb(color))
        f, _ = fit_size(f"{em}  {name}", "serif_b", 24, cw - 20, 13)
        draw_text(img, (x + cw / 2, y + 16), f"{em}  {name}", f, WHITE,
                  anchor="ma")
        yy = y + 92
        from etsy.catering_lib import wrap
        for ln in wrap(desc, S.F("sans_md", 22), cw - 40):
            draw_text(img, (x + 20, yy), ln, S.F("sans_md", 22), INK)
            yy += 32
        draw_text(img, (x + cw / 2, y + 320), "Excel & Google Sheets",
                  S.F("sans_sb", 19), MUTED, anchor="ma")
    hand_note(img, MX + CW - 130, y + 386, "start here! \u2193", 40, COPPER,
              "ra")
    y += 440
    y = note_card(img, y, "\U0001F4A1", "OPEN THE EXAMPLE FILE FIRST", [
        "Spend two minutes clicking around a business that is already "
        "booked solid.",
        "When you are ready to go live, open a PREMIUM file and type over "
        "the demo content — or clear it in one go (page 3)."], BRASS)
    y = h2(img, y + 26, "\u2699 What you need")
    y = bullets(img, y, [
        "Excel 2016 or later (Windows or Mac), or Microsoft 365 — no older "
        "versions, no OpenOffice",
        "Google Sheets: import the file in four clicks (full walkthrough "
        "on page 11)",
        "No macros, no add-ins, no internet needed — it is pure formulas, "
        "so it also works offline",
        "A printer, if you like paper: every tab is already set up to "
        "print neatly"], 24)
    y = note_card(img, y + 18, "\U0001F512", "IF EXCEL SHOWS A YELLOW BAR", [
        "Files downloaded from the internet open in Protected View. Click "
        "\u201CEnable Editing\u201D at the top and everything wakes up. "
        "There are no macros in this file, so nothing else is required."],
        WARN)
    qa_page(img, 2, y, "files")
    finish_page(img, 2)


# ---------------------------------------------------------------------------
# page 3 — the 3-minute setup
# ---------------------------------------------------------------------------
def p03():
    img = new_page()
    y = h1(img, 110, "CHAPTER 2", "The three-minute setup")
    y = sshot(img, y + 4, SETUP, 1000, crop=(0, 900),
              url="Novality Store — Setup tab")
    y = steps(img, y + 2, [
        ("Name your business", "\u2699 Setup → Business name, currency and "
         "season year. The dashboard and invoices pick these up "
         "automatically."),
        ("Set your money rules", "Sales tax %, target profit margin, "
         "deposit % and the \u201Cdue soon\u201D window — every quote and "
         "report obeys them."),
        ("Type your lists", "\u2699 Setup → Editable lists: event types, "
         "categories, staff roles, payment methods. Every dropdown reads "
         "from them."),
        ("Add your world", "Clients, events, menu dishes, ingredients, "
         "suppliers and equipment — one row each, dropdowns wherever "
         "possible."),
        ("Work the pipeline", "Move events from Inquiry to Confirmed; "
         "log expenses and payments as they happen."),
        ("Enjoy the dashboard", "\U0001F4CA Dashboard needs no typing at "
         "all — it recalculates the moment you change anything anywhere.")],
        25)
    y = note_card(img, y + 8, "\U0001F947", "THE GOLDEN RULES", [
        "White cells are yours — type in them freely. Tinted cells are "
        "formula cells: they are locked so the maths can never break.",
        "Pick from the dropdowns instead of typing — the status, category "
        "and tick columns feed the dashboard.",
        "Don\u2019t rename tabs or delete the hidden _Data sheet; the "
        "whole workbook reads from them."], ESPRESSO, size=23)
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
            "morning and it will tell you what needs doing.")
    crop = DASH.crop((0, 0, SW_CROP, 1150))
    y = sshot(img, y + 6, crop, CW)
    y = h2(img, y + 4, "\U0001F9ED What each part is telling you")
    y = bullets(img, y, [
        "\U0001F4B2 Money cards — cash in, cash out, net profit and "
        "margin, straight from your payments and expenses",
        "\U0001F3AD Pipeline pills — events on the books, confirmed, "
        "completed, average order value, outstanding and overdue",
        "\U0001F4CA Charts — revenue vs expenses by month and revenue by "
        "event type, redrawn as you book",
        "\U0001F3C6 Best performers — your top-earning event type, highest-"
        "value client, food and labor cost percentages",
        "\U0001F4C5 Upcoming events and payments due — the five closest, "
        "with overdue amounts in red",
        "\U0001F514 Alerts — low stock, unpaid shifts, equipment needing "
        "service and overdue invoices, in plain English"], 23)
    qa_page(img, 4, y, "dashboard")
    finish_page(img, 4)


# ---------------------------------------------------------------------------
# page 5 — clients & events
# ---------------------------------------------------------------------------
def p05():
    img = new_page()
    y = h1(img, 110, "CHAPTER 4", "Clients & Events")
    y = h2(img, y + 2, "\U0001F91D Clients — who is booking")
    y = sshot(img, y + 2, CLIENTS, 1230, crop=(0, 640),
              url="Novality Store — Clients")
    y = bullets(img, y - 16, [
        "One row per client: contact details, next event, package tier "
        "and what they have paid so far",
        "Payment status ticks itself from green to amber to red based on "
        "the invoice tab"], 23, gap=8)
    y = h2(img, y + 12, "\U0001F3AD Events — the pipeline to the plate")
    y = sshot(img, y + 2, EVENTS, 1230, crop=(0, 700),
              url="Novality Store — Events")
    y = bullets(img, y - 16, [
        "Status dropdown runs the pipeline: Inquiry \u2192 Quote Sent "
        "\u2192 Deposit Paid \u2192 Confirmed \u2192 Completed",
        "Cost, price, profit and margin fill themselves in — tag expenses "
        "to the event ID and the maths is done"], 23, gap=8)
    qa_page(img, 5, y, "clients+events")
    finish_page(img, 5)


# ---------------------------------------------------------------------------
# page 6 — quote builder & menu costing
# ---------------------------------------------------------------------------
def p06():
    img = new_page()
    y = h1(img, 110, "CHAPTER 5", "Quotes & Menu Costing")
    y = h2(img, y + 2, "\U0001F9F1 Quote Builder — price in 60 seconds")
    y = sshot(img, y + 2, QUOTE, 1230, crop=(0, 660),
              url="Novality Store — Quote Builder")
    y = bullets(img, y - 16, [
        "Type guests, food cost per guest, labor, kit and transport — "
        "the recommended price appears instantly",
        "Your target margin and deposit % from Setup are applied for "
        "you; the quote shows what to collect to book the date"], 23,
        gap=8)
    y = h2(img, y + 12, "\U0001F37D Menu Costing — cost once, price right")
    y = sshot(img, y + 2, MENU, 1230, crop=(0, 640),
              url="Novality Store — Menu Costing")
    y = bullets(img, y - 16, [
        "Each dish: ingredients, portion, cost and a suggested price at "
        "your target margin",
        "Margins are colour-coded, so the dishes that quietly bleed cash "
        "stand out immediately"], 23, gap=8)
    qa_page(img, 6, y, "quote+menu")
    finish_page(img, 6)


# ---------------------------------------------------------------------------
# page 7 — money
# ---------------------------------------------------------------------------
def p07():
    img = new_page()
    y = h1(img, 110, "CHAPTER 6", "Expenses & Payments")
    y = h2(img, y + 2, "\U0001F4B8 Expenses — every dollar tagged")
    y = sshot(img, y + 2, EXPENSES, 1230, crop=(0, 640),
              url="Novality Store — Expenses")
    y = bullets(img, y - 16, [
        "Log each purchase against an event ID and category — the "
        "spend-by-category chart builds itself",
        "The receipt column is a simple tick: end-of-season bookkeeping "
        "becomes a filter, not a hunt"], 23, gap=8)
    y = h2(img, y + 12, "\U0001F4B0 Payments — deposits, balances, "
           "stragglers")
    y = sshot(img, y + 2, INCOME, 1230, crop=(0, 600),
              url="Novality Store — Payments")
    y = bullets(img, y - 16, [
        "Each invoice tracks deposit, payments received and balance — "
        "log money as it arrives",
        "An invoice past its due date turns red on its own, and the "
        "dashboard counts it as overdue"], 23, gap=8)
    qa_page(img, 7, y, "money")
    finish_page(img, 7)


# ---------------------------------------------------------------------------
# page 8 — inventory & shopping
# ---------------------------------------------------------------------------
def p08():
    img = new_page()
    y = h1(img, 110, "CHAPTER 7", "Inventory & Shopping List")
    y = h2(img, y + 2, "\U0001F9EA Inventory — know your walk-in")
    y = sshot(img, y + 2, INVENTORY, 1230, crop=(0, 640),
              url="Novality Store — Inventory")
    y = bullets(img, y - 16, [
        "Every ingredient has an on-hand quantity, a minimum and a "
        "supplier — the status ticker turns red at or below minimum",
        "Stock value is totalled live, so insurance and year-end counts "
        "are already done"], 23, gap=8)
    y = h2(img, y + 12, "\U0001F6D2 Shopping List — built for you")
    y = sshot(img, y + 2, SHOPPING, 1230, crop=(0, 620),
              url="Novality Store — Shopping List")
    y = bullets(img, y - 16, [
        "Event menus pull ingredient quantities, stock on hand is "
        "subtracted, and the gap lands here with estimated costs",
        "Lines are grouped by supplier, and ticking \u201Cbought\u201D "
        "removes them from the open count"], 23, gap=8)
    qa_page(img, 8, y, "stock")
    finish_page(img, 8)


# ---------------------------------------------------------------------------
# page 9 — staff & equipment
# ---------------------------------------------------------------------------
def p09():
    img = new_page()
    y = h1(img, 110, "CHAPTER 8", "Staff, Equipment & Suppliers")
    y = h2(img, y + 2, "\U0001F9D1 Staff & Shifts — crew and payroll")
    y = sshot(img, y + 2, STAFF, 1230, crop=(0, 640),
              url="Novality Store — Staff & Shifts")
    y = bullets(img, y - 16, [
        "One row per shift: hours, rate and overtime at 1.5\u00D7 give "
        "the shift cost that flows into the event and the P&L",
        "The paid column keeps payroll honest — unpaid shifts appear on "
        "the dashboard"], 23, gap=8)
    y = h2(img, y + 12, "\U0001F527 Equipment — the kit that earns its "
           "keep")
    y = sshot(img, y + 2, EQUIPMENT, 1230, crop=(0, 620),
              url="Novality Store — Equipment")
    y = bullets(img, y - 16, [
        "Owned, reserved, damaged and free are tracked per item — "
        "reservations come from confirmed events",
        "A \U0001F680 Suppliers tab keeps every vendor, price list and "
        "delivery term one click away"], 23, gap=8)
    qa_page(img, 9, y, "staff+kit")
    finish_page(img, 9)


# ---------------------------------------------------------------------------
# page 10 — calendar & reports
# ---------------------------------------------------------------------------
def p10():
    img = new_page()
    y = h1(img, 110, "CHAPTER 9", "Calendar, Reports & the rest")
    y = h2(img, y + 2, "\U0001F4C6 Event Calendar — the month at a glance")
    y = sshot(img, y + 2, CALENDAR, 1230, crop=(0, 660),
              url="Novality Store — Event Calendar")
    y = bullets(img, y - 16, [
        "Bookings and payment deadlines share one grid — dots for "
        "events, triangles for dues",
        "The month and year are dropdowns on Setup; nothing to re-build "
        "next season"], 23, gap=8)
    y = h2(img, y + 12, "\U0001F4BC P&L, tax and the supporting cast")
    y = sshot(img, y + 2, REPORTS, 1230, crop=(0, 600),
              url="Novality Store — P&L & Reports")
    y = bullets(img, y - 16, [
        "Season P&L, sales-tax helper, monthly trends and best-performer "
        "tables — all from your entries",
        "\u2705 Checklists cover prep week, shopping, event day and "
        "wrap-up; \U0001F5A8 Invoice & Proposal prints a branded, "
        "pre-filled invoice per event"], 23, gap=8)
    qa_page(img, 10, y, "cal+reports")
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
        ("File \u2192 Import", "Choose the Upload tab and drag your .xlsx "
         "file in — or click \u201CSelect a file from your device\u201D."),
        ("Replace spreadsheet", "In Import settings choose \u201CReplace "
         "spreadsheet\u201D so every tab arrives together, then click "
         "Import data."),
        ("Done", "Dropdowns, colours, conditional formatting, locked "
         "cells and charts all come along. Formulas become Google-native "
         "formulas.")], 28)
    y = h2(img, y + 8, "\u2705 What converts")
    y = bullets(img, y, [
        "All 1,500+ formulas (translated to Google Sheets equivalents)",
        "Every dropdown menu and conditional-format colour rule",
        "Sheet protection — the formula cells stay locked in Sheets too",
        "Charts — Google Sheets rebuilds them from the same data"], 24)
    y = note_card(img, y + 16, "\U0001F4A1", "GOOD TO KNOW", [
        "Keep the original .xlsx — it is your master copy and works in "
        "Excel, Google Sheets and (formulas only) Apple Numbers.",
        "Editing on the phone app works for quick ticks; the dashboard "
        "is happiest on a laptop or tablet screen."], INFO, size=24)
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
        ("A dropdown is missing an option",
         "Add the event type, category or role on the \u2699 Setup tab — "
         "every dropdown updates instantly."),
        ("I typed in a formula cell and it broke",
         "The tinted cells are locked, so this should not be possible. "
         "If a value looks odd, Ctrl+Z straight away, or re-download "
         "your files from Etsy."),
        ("Can I add more rows?",
         "Yes — insert rows inside the existing tables (not above the "
         "first row) and the formulas copy down with them."),
        ("Can I print it?",
         "Every tab has print areas set. File \u2192 Print, and it fits "
         "the page — the checklists and invoice were designed for it."),
        ("Where do I get updates?",
         "Lifetime updates are included: re-download from Etsy \u2192 "
         "You \u2192 Purchases any time."),
    ]
    from etsy.catering_lib import wrap
    for q, a in faqs:
        d = ImageDraw.Draw(img)
        hh = 176
        rrect(d, [MX, y, MX + CW, y + hh], 14, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(img, (MX + 30, y + 20), "Q", S.F("display_b", 40), COPPER)
        draw_text(img, (MX + 82, y + 24), q, S.F("serif_b", 30), ESPRESSO)
        yy = y + 84
        for ln in wrap(a, S.F("sans_md", 22), CW - 130)[:2]:
            draw_text(img, (MX + 82, yy), ln, S.F("sans_md", 22), INK)
            yy += 33
        y += hh + 20
    y = note_card(img, y + 8, "\U0001F4DC", "LICENSE & SUPPORT", [
        "One business per purchase. Not for resale or redistribution.",
        "Stuck or spotted a bug? Message Novality Store on Etsy — we "
        "reply within a day."], "#3A2E22", size=24)
    img.alpha_composite(strip(False, 150).resize((PW, 150), Image.LANCZOS),
                        (0, PH - 150))
    draw_text(img, (PW / 2, PH - 118), "Thank you for supporting our "
              "small shop — Novality Store", S.F("hand", 54), COPPER,
              anchor="ma")
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
                     "Catering Business Manager — User Guide",
                     "Novality Store")
    print(f"built {os.path.basename(OUT_PDF)}")
    print(f"  pages : {len(PAGES)}  (A4, {int(DPI)} dpi)")
    print(f"  size  : {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
