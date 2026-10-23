"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Salon Business Management System spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, bullets, description,
                                    how-to-use, attributes, FAQ, keywords
    etsy/kit/spreadsheets/          filled sample + blank template
    download/salon-business-etsy-kit.zip

Usage:
    python3 tools/make_etsy_kit.py
    python3 tools/make_etsy_kit.py --contact   # also writes QA contact sheets

AI imagery is used only for the four text-free background photos in
etsy/assets/. Every word in the kit is typeset here with PIL/DejaVu, so
nothing in a listing image can arrive garbled.
"""

from __future__ import annotations

import argparse
import io
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ETSY = ROOT / "etsy"
ASSETS = ETSY / "assets"
KIT = ETSY / "kit"
IMG_OUT = KIT / "etsy-listing-images"
COPY_OUT = KIT / "listing-copy"
SHEETS_OUT = KIT / "spreadsheets"
DOWNLOAD = ROOT / "download"
PRODUCT_ZIP = DOWNLOAD / "salon-business-system.zip"
ZIP_PREFIX = "salon-business-management-system/"

FILLED_NAME = "Salon Business Management System.xlsx"
BLANK_NAME = "Salon Business Management System (Blank).xlsx"

S = 2000                     # canvas size

# ---- brand palette (plum / rose / gold, matches the workbook) --------------
INK         = (46, 36, 48)       # #2E2430
PRIMARY     = (109, 59, 94)      # #6D3B5E - the workbook's own primary
PRIMARY_MID = (154, 92, 134)     # #9A5C86
PRIMARY_DEEP = (76, 42, 66)      # #4C2A42
PRIMARY_SOFT = (243, 230, 239)   # #F3E6EF
ACCENT      = (192, 138, 94)     # #C08A5E - warm gold
ACCENT_SOFT = (247, 236, 225)    # #F7ECE1
CREAM       = (251, 247, 250)    # #FBF7FA
CREAM_DARK  = (240, 230, 238)
CALC        = (250, 245, 248)
WHITE       = (255, 255, 255)
GREY        = (107, 92, 102)     # #6B5C66
GREY_SOFT   = (234, 223, 231)
GOOD        = (47, 90, 43)
GOOD_SOFT   = (220, 235, 216)
BAD         = (156, 42, 36)
BAD_SOFT    = (248, 218, 217)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)      # noqa: E731
F_SANS = lambda s: font("DejaVuSans.ttf", s)             # noqa: E731
F_MONO = lambda s: font("DejaVuSansMono-Bold.ttf", s)    # noqa: E731


# ------------------------------------------------------------------ helpers
def vgrad(top, bottom, size=S):
    img = Image.new("RGB", (size, size), top)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        d.line([(0, y), (size, y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t)
                          for i in range(3)))
    return img


def cover(path: Path, size=S) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = max(size / w, size / h)
    img = img.resize((int(w * scale) + 1, int(h * scale) + 1),
                     Image.LANCZOS)
    w, h = img.size
    left, top = (w - size) // 2, (h - size) // 2
    return img.crop((left, top, left + size, top + size))


def dim(img: Image.Image, alpha: int = 120,
        color=(40, 26, 38)) -> Image.Image:
    overlay = Image.new("RGB", img.size, color)
    return Image.blend(img.convert("RGB"), overlay, alpha / 255)


def scrim(img: Image.Image, side: str = "bottom") -> Image.Image:
    """Soft dark gradient so text stays readable over photos."""
    grad = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(grad)
    for i in range(img.size[1]):
        t = i / img.size[1]
        if side == "bottom":
            a = int(215 * max(0, t - 0.30) / 0.70)
        elif side == "top":
            a = int(215 * max(0, 0.5 - t) / 0.5)
        else:
            a = 120
        d.line([(0, i), (img.size[0], i)], fill=a)
    dark = Image.new("RGB", img.size, (38, 24, 36))
    img.paste(dark, (0, 0), grad)
    return img


def tw(draw: ImageDraw.ImageDraw, s: str, f) -> float:
    return draw.textlength(s, font=f)


def wrap(draw: ImageDraw.ImageDraw, s: str, f, max_w: float):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if tw(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center_text(draw, y, s, f, fill, x0=0, x1=S):
    x = x0 + (x1 - x0 - tw(draw, s, f)) / 2
    draw.text((x, y), s, font=f, fill=fill)


def center_fit(draw, y, s, f_factory, size, fill, x0=0, x1=S,
               max_frac=0.92):
    """Center text, shrinking the font until it fits inside the band."""
    max_w = (x1 - x0) * max_frac
    f = f_factory(size)
    while size > 40 and tw(draw, s, f) > max_w:
        size = int(size * 0.93)
        f = f_factory(size)
    center_text(draw, y, s, f, fill, x0, x1)
    return size


def left_fit(draw, x, y, s, f_factory, size, fill, max_w, max_frac=1.0):
    """Left-aligned text that shrinks to fit a fixed width."""
    limit = max_w * max_frac
    f = f_factory(size)
    while size > 26 and tw(draw, s, f) > limit:
        size = int(size * 0.93)
        f = f_factory(size)
    draw.text((x, y), s, font=f, fill=fill)
    return size


def panel(draw, box, fill=WHITE, outline=None, radius=26, width=3):
    draw.rounded_rectangle(box, radius, fill=fill, outline=outline,
                           width=width)


def chip(draw, x, y, s, f, fg, bg, pad_x=30, pad_y=18, radius=40):
    w = tw(draw, s, f)
    h = f.size + pad_y * 2
    draw.rounded_rectangle([x, y, x + w + pad_x * 2, y + h], radius,
                           fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), s, font=f, fill=fg)
    return w + pad_x * 2, h


def pill(draw, cx, cy, s, f, fg, bg, pad_x=36, pad_y=20):
    w = tw(draw, s, f)
    h = f.size + pad_y * 2
    x = cx - (w + pad_x * 2) / 2
    y = cy - h / 2
    draw.rounded_rectangle([x, y, x + w + pad_x * 2, y + h], h // 2,
                           fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), s, font=f, fill=fg)


def brand_footer(draw, y=1880, color=GREY):
    center_text(draw, y, "by Novality Store", F_SANS_B(38), color)


def kicker(draw, y, s, color=ACCENT):
    center_text(draw, y, s, F_SANS_B(42), color)


def tick(draw, x, y, size=34, color=GOOD):
    draw.ellipse([x, y, x + size, y + size], fill=color)
    draw.line([(x + size * 0.28, y + size * 0.52),
               (x + size * 0.44, y + size * 0.68),
               (x + size * 0.74, y + size * 0.32)],
              fill=WHITE, width=int(size * 0.14))


def head(draw, title: str, sub: str = "") -> None:
    """Standard inner-page heading on a cream canvas."""
    draw.rectangle([0, 0, S, 250], fill=PRIMARY)
    center_fit(draw, 78, title, F_SERIF, 96, WHITE)
    if sub:
        center_fit(draw, 178, sub, F_SANS, 44, PRIMARY_SOFT)
    draw.rectangle([0, 250, S, 258], fill=ACCENT)


def mock_table(d, x, y, widths, header, rows, row_h=76, head_h=64,
               f_head=None, f_body=None):
    """Simple spreadsheet-style mock: header band + striped rows."""
    f_head = f_head or F_SANS_B(34)
    f_body = f_body or F_SANS(34)
    total = sum(widths)
    d.rectangle([x, y, x + total, y + head_h], fill=PRIMARY)
    cx = x
    for w, label in zip(widths, header):
        d.text((cx + 18, y + 14), label, font=f_head, fill=WHITE)
        cx += w
    yy = y + head_h
    for i, row in enumerate(rows):
        if i % 2 == 0:
            d.rectangle([x, yy, x + total, yy + row_h], fill=WHITE)
        else:
            d.rectangle([x, yy, x + total, yy + row_h], fill=CALC)
        cx = x
        for w, (label, colour) in zip(widths, row):
            d.text((cx + 18, yy + 18), label, font=f_body,
                   fill=colour or INK)
            cx += w
        yy += row_h
    d.rectangle([x, y, x + total, yy], outline=GREY_SOFT, width=2)
    return yy


def bars(d, x0, y0, x1, y1, values, colour=PRIMARY_MID, base=None):
    """Tiny column chart mock inside a panel."""
    base = base or (x0, y1, x1, y1)
    d.line([(x0, y1), (x1, y1)], fill=GREY_SOFT, width=3)
    n = len(values)
    bw = (x1 - x0) / n
    top = max(values)
    lo = 0.0
    if top and (top - min(values)) / top < 0.15:
        lo = min(values) - (top - min(values)) * 0.25
    span = top - lo or 1.0
    for i, v in enumerate(values):
        h = (y1 - y0) * ((v - lo) / span)
        d.rectangle([x0 + i * bw + bw * 0.18, y1 - h,
                     x0 + (i + 1) * bw - bw * 0.18, y1], fill=colour)


def feat_card(d, y, title, body, title_colour=ACCENT,
              x0=110, x1=None, h=176):
    """One wide feature strip: bold title + two lines of body."""
    x1 = x1 or (S - 110)
    panel(d, [x0, y, x1, y + h], fill=WHITE)
    d.text((x0 + 60, y + 20), title, font=F_SANS_B(44),
           fill=title_colour)
    lines = wrap(d, body, F_SANS(38), x1 - x0 - 120)
    for j, line in enumerate(lines[:2]):
        d.text((x0 + 60, y + 84 + j * 46), line, font=F_SANS(38),
               fill=GREY)
    return y + h


# ============================================================== the 18 images
def img_cover() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_salon.jpg"), 70), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 240, "INSTANT DOWNLOAD", F_SANS_B(44), INK, ACCENT_SOFT)
    center_fit(d, 370, "SALON BUSINESS", F_SERIF, 168, WHITE)
    center_fit(d, 560, "MANAGEMENT", F_SERIF, 168, WHITE)
    center_fit(d, 750, "SPREADSHEET", F_SERIF, 120, ACCENT_SOFT)
    center_text(d, 990, "20 tabs  ·  20,500+ formulas  ·  Excel 2010-365",
                F_SANS_B(54), PRIMARY_SOFT)
    center_text(d, 1080, "Bookings · Clients · Commission · Stock · Profit",
                F_SANS(48), PRIMARY_SOFT)
    stats = [("20", "TABS"), ("20.5K", "FORMULAS"), ("11", "MONTHS DEMO"),
             ("2", "WORKBOOKS")]
    bw = 380
    x = S / 2 - (len(stats) * bw + (len(stats) - 1) * 30) / 2
    for big, small in stats:
        panel(d, [x, 1290, x + bw, 1520], fill=WHITE)
        center_text(d, 1330, big, F_SERIF(84), PRIMARY, x, x + bw)
        center_text(d, 1450, small, F_SANS_B(34), GREY, x, x + bw)
        x += bw + 30
    brand_footer(d, 1870, WHITE)
    return img


def img_what_you_get() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "WHAT YOU GET", "Two workbooks and a guide - nothing to install")
    files = [
        ("Salon Business Management System.xlsx",
         "the full 20-tab system filled with eleven months of a realistic "
         "example salon, Bloom & Blade Studio - every KPI, commission "
         "statement and P&L line is live"),
        ("Salon Business Management System (Blank).xlsx",
         "the same workbook with empty registers - open this one and run "
         "your own salon from day one"),
        ("HOW TO RUN.txt",
         "one page: where to click first, what to type, what stays locked, "
         "and the money rules the workbook follows"),
    ]
    y = 340
    for name, body in files:
        panel(d, [120, y, S - 120, y + 300], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([120, y, 138, y + 300], fill=PRIMARY_MID)
        d.text((190, y + 34), name, font=F_SANS_B(46), fill=PRIMARY_DEEP)
        lines = wrap(d, body, F_SANS(38), S - 240 - 190)
        for i, line in enumerate(lines[:3]):
            d.text((190, y + 112 + i * 52), line, font=F_SANS(38),
                   fill=GREY)
        y += 330
    chips = ["INSTANT DOWNLOAD", "NO MACROS", "NO SUBSCRIPTION",
             "EXCEL 2010+"]
    x = 150
    for c in chips:
        w, h = chip(d, x, y + 40, c, F_SANS_B(36), WHITE, PRIMARY)
        x += w + 26
    center_text(d, 1800, "Digital product - no physical item is shipped.",
                F_SANS(40), GREY)
    brand_footer(d, 1868)
    return img


def img_tabs() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "20 TABS, ONE SYSTEM", "Every number below is live - nothing "
                                   "typed by hand")
    groups = [
        ("SET UP", "1 Start Here · 20 Settings & Lists - tax, fees, "
                   "commission rates and every drop-down"),
        ("THE DAILY DIARY", "3 Appointment Planner · 6 Sales & "
                            "Transactions · 7 Payments & Deposits"),
        ("PEOPLE", "4 Client CRM · 8 Staff Management · 9 Staff "
                   "Commissions · 10 Payroll & Tips"),
        ("MONEY IN & OUT", "5 Services & Pricing · 11 Expenses · "
                           "12 Profit & Loss"),
        ("STOCK & GROWTH", "13 Product Inventory · 14 Suppliers & "
                           "Purchases · 15 Marketing & Promotions · "
                           "16 Client Loyalty"),
        ("READING IT BACK", "2 Dashboard · 17 Goals & Budget · 18 Business "
                            "Analytics · 19 Weekly & Monthly Reports"),
    ]
    y = 330
    for name, tabs in groups:
        panel(d, [110, y, S - 110, y + 210], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([110, y, 126, y + 210], fill=PRIMARY_MID)
        d.text((168, y + 26), name, font=F_SANS_B(46), fill=PRIMARY_DEEP)
        lines = wrap(d, tabs, F_SANS(36), S - 220 - 168)
        for i, line in enumerate(lines[:3]):
            d.text((168, y + 96 + i * 44), line, font=F_SANS(36),
                   fill=GREY)
        y += 232
    brand_footer(d)
    return img


def img_dashboard() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "THE DASHBOARD", "How the month is going, before you dig")
    tiles = [("REVENUE THIS MONTH", "$14,380", GOOD),
             ("VS TARGET", "103%", GOOD),
             ("BOOKINGS DONE", "182 of 196", PRIMARY),
             ("NO-SHOW RATE", "4%", PRIMARY),
             ("RETAIL SHARE", "14%", PRIMARY_MID),
             ("DEPOSITS HELD", "$1,240", PRIMARY_MID)]
    x, y = 130, 340
    for i, (label, value, colour) in enumerate(tiles):
        panel(d, [x, y, x + 830, y + 210], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x, y, x + 830, y + 12], fill=colour)
        center_text(d, y + 44, label, F_SANS_B(36), GREY, x, x + 830)
        center_text(d, y + 100, value, F_SERIF(78), colour, x, x + 830)
        x += 890
        if i % 2 == 1:
            x = 130
            y += 240
    y += 280
    panel(d, [130, y, S - 130, y + 420], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((180, y + 30), "WHAT TO DO NEXT", font=F_SANS_B(46),
           fill=PRIMARY_DEEP)
    for i, line in enumerate([
        "Three clients are due a rebooking nudge this week",
        "Two deposits are sitting unearned - book the visits",
        "Retail share is under target - one shelf talk per checkout",
        "Commission statements for May are ready on tab 9",
    ]):
        d.ellipse([190, y + 120 + i * 72, 226, y + 156 + i * 72],
                  fill=ACCENT)
        left_fit(d, 260, y + 118 + i * 72, line, F_SANS, 40, GREY,
                 S - 260 - 200)
    center_text(d, 1800, "Revenue, targets, bookings, retail share and "
                         "held deposits - all formulas, nothing typed.",
                F_SANS(40), GREY)
    brand_footer(d, 1868)
    return img


def img_appointments() -> Image.Image:
    img = dim(cover(ASSETS / "bg_tools.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "TAB 3 · APPOINTMENT PLANNER", F_SANS_B(42), WHITE,
         PRIMARY)
    panel(d, [110, 300, S - 110, 830], fill=WHITE)
    d.text((170, 330), "THE DIARY - one row per booking",
           font=F_SANS_B(44), fill=PRIMARY_DEEP)
    mock_table(d, 170, 410, [200, 140, 240, 180, 380, 150, 210],
               ["DATE", "TIME", "CLIENT", "STYLIST", "SERVICE", "PRICE",
                "STATUS"],
               [[("Sat 09", None), ("9:00", None), ("M. Alvarez", None),
                 ("Priya", None), ("Balayage & finish", None),
                 ("185", PRIMARY), ("Completed", GOOD)],
                [("Sat 09", None), ("11:30", None), ("J. Chen", None),
                 ("Marco", None), ("Cut & blow-dry", None),
                 ("65", PRIMARY), ("Confirmed", None)],
                [("Sat 09", None), ("14:00", None), ("R. Osei", None),
                 ("Priya", None), ("Gel manicure", None),
                 ("48", PRIMARY), ("Booked", None)],
                [("Sun 10", None), ("10:00", None), ("T. Byrne", None),
                 ("Aisha", None), ("Lash lift", None),
                 ("75", PRIMARY), ("No show", BAD)]],
               row_h=72, head_h=56)
    y = 880
    for t, b in [("PRICE & DURATION FILL THEMSELVES",
                  "pick the client and the service from drop-downs; price "
                  "and minutes arrive from the menu"),
                 ("DEPOSIT AND BALANCE ON THE ROW",
                  "deposits taken are held as unearned until the visit "
                  "completes - never counted twice"),
                 ("400 BOOKING ROWS",
                  "statuses flow booked to confirmed to completed, "
                  "cancelled or no-show, and the rates compute themselves")]:
        y = feat_card(d, y, t, b) + 16
    brand_footer(d, 1810, PRIMARY_SOFT)
    return img


def img_clients() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "CLIENT CRM", "Everyone who sits in your chair, remembered")
    fields = ["Name", "Phone", "Email", "Allergies", "Patch test date",
              "Colour formula", "Preferences", "Consents", "Last visit",
              "Lifetime spend"]
    x, y = 130, 340
    for fld in fields:
        w, h = chip(d, x, y, fld, F_SANS_B(40), PRIMARY_DEEP, PRIMARY_SOFT)
        x += w + 24
        if x > S - 340:
            x = 130
            y += h + 24
    y += 110
    mock_table(d, 200, y, [380, 260, 260, 200, 300],
               ["CLIENT", "LAST VISIT", "NEXT DUE", "VISITS", "SPEND"],
               [[("M. Alvarez", None), ("12 Apr", None), ("24 May", ACCENT),
                 ("9", None), ("1,240", PRIMARY)],
                [("J. Chen", None), ("02 May", None), ("14 Jun", ACCENT),
                 ("4", None), ("318", PRIMARY)],
                [("R. Osei", None), ("18 May", None), ("-", GREY),
                 ("1", None), ("48", PRIMARY)]],
               row_h=80, head_h=58)
    y += 4 * 80 + 58 + 60
    cards = [("REBOOK REMINDERS", "the next-due date works itself out from "
                                  "the last visit and the usual gap"),
             ("COLOUR FORMULA ON FILE", "so any stylist can pick up where "
                                        "the last one left off"),
             ("SPEND & STATUS", "new, regular, VIP or lapsing - worked out, "
                                "not guessed")]
    x0 = 130
    for t, b in cards:
        panel(d, [x0, y, x0 + 560, y + 380], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x0, y, x0 + 560, y + 14], fill=PRIMARY_MID)
        center_fit(d, y + 50, t, F_SANS_B, 42, PRIMARY_DEEP, x0, x0 + 560)
        lines = wrap(d, b, F_SANS(36), 460)
        for j, line in enumerate(lines[:4]):
            center_text(d, y + 140 + j * 50, line, F_SANS(36), GREY,
                        x0, x0 + 560)
        x0 += 590
    brand_footer(d, y + 440)
    return img


def img_services() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "SERVICES & PRICING", "Your menu, with the maths underneath")
    mock_table(d, 150, 330, [420, 260, 160, 180, 180, 200],
               ["SERVICE", "CATEGORY", "MINS", "PRICE", "COST", "MARGIN"],
               [[("Balayage & finish", None), ("Colour", None),
                 ("150", None), ("185", None), ("31", None),
                 ("83%", GOOD)],
                [("Full colour & cut", None), ("Colour", None),
                 ("120", None), ("140", None), ("24", None),
                 ("83%", GOOD)],
                [("Cut & blow-dry", None), ("Cutting", None),
                 ("45", None), ("65", None), ("4", None),
                 ("94%", GOOD)],
                [("Gel manicure", None), ("Nails", None),
                 ("60", None), ("48", None), ("7", None),
                 ("85%", GOOD)],
                [("Lash lift & tint", None), ("Lashes", None),
                 ("50", None), ("75", None), ("9", None),
                 ("88%", GOOD)]],
               row_h=84, head_h=60)
    y = 1000
    d.text((150, y), "EVERY LINE ALSO CARRIES", font=F_SANS_B(44),
           fill=PRIMARY_DEEP)
    feats = ["direct product cost, so the margin column is honest",
             "duration, so chair hours and utilisation add up",
             "category, so revenue rolls up the way you think about it",
             "a rank flag that quietly marks your slow movers"]
    y += 80
    for f in feats:
        tick(d, 160, y + 6, 36)
        left_fit(d, 230, y + 4, f, F_SANS, 40, GREY, S - 360)
        y += 78
    panel(d, [150, 1480, S - 150, 1760], fill=PRIMARY_SOFT)
    center_fit(d, 1520, "Drop-downs on the diary read this menu:",
               F_SANS_B, 44, PRIMARY_DEEP)
    center_fit(d, 1600, "pick a service and its price and minutes follow",
               F_SANS, 44, GREY)
    brand_footer(d, 1830)
    return img


def img_sales() -> Image.Image:
    img = dim(cover(ASSETS / "bg_desk.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "TABS 6-7 · SALES & PAYMENTS", F_SANS_B(42), WHITE,
         PRIMARY)
    panel(d, [110, 300, S - 110, 800], fill=WHITE)
    mock_table(d, 160, 340, [420, 210, 170, 230, 150, 180],
               ["SALE LINE", "KIND", "GROSS", "DISCOUNT", "TAX", "NET"],
               [[("Balayage & finish", None), ("Service", None),
                 ("185", None), ("0", None), ("0", GREY),
                 ("185", PRIMARY)],
                [("Olaplex No.3, 2x", None), ("Retail", None),
                 ("60", None), ("6", None), ("4.5", GREY),
                 ("58.5", PRIMARY)],
                [("Deposit - lash lift", None), ("Deposit", None),
                 ("20", None), ("0", None), ("held", ACCENT),
                 ("held", ACCENT)]],
               row_h=84, head_h=58)
    y = 860
    for t, b in [("DEPOSITS NEVER COUNTED TWICE",
                  "a deposit is not revenue until the visit completes and "
                  "the sale is invoiced; unearned deposits report "
                  "separately"),
                 ("CARD FEES WORKED OUT",
                  "your percentage plus the fixed fee per transaction, so "
                  "the till and the bank agree"),
                 ("OUTSTANDING BALANCES",
                  "who still owes what, listed on the dashboard until it "
                  "is paid")]:
        y = feat_card(d, y, t, b) + 16
    brand_footer(d, 1810, PRIMARY_SOFT)
    return img


def img_commission() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "STAFF COMMISSIONS", "Payday without the argument")
    methods = [("PERCENTAGE", "one person, one rate: their share of the "
                               "service revenue they completed"),
               ("CATEGORY RATE", "different rates per service category - "
                                 "colour at one rate, nails at another"),
               ("FLAT PER SERVICE", "a set amount per completed booking, "
                                    "plus retail commission on top")]
    x0 = 130
    for t, b in methods:
        panel(d, [x0, 340, x0 + 560, 720], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x0, 340, x0 + 560, 356], fill=PRIMARY_MID)
        center_fit(d, 390, t, F_SANS_B, 44, PRIMARY_DEEP, x0, x0 + 560)
        lines = wrap(d, b, F_SANS(36), 460)
        for j, line in enumerate(lines[:4]):
            center_text(d, 480 + j * 50, line, F_SANS(36), GREY,
                        x0, x0 + 560)
        x0 += 590
    panel(d, [130, 780, S - 130, 1330], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((190, 810), "THE MONTHLY STATEMENT, PER PERSON",
           font=F_SANS_B(44), fill=PRIMARY_DEEP)
    mock_table(d, 190, 890, [300, 260, 280, 160, 200, 280],
               ["STYLIST", "METHOD", "SERVICE REV", "RATE", "RETAIL",
                "COMMISSION"],
               [[("Priya", None), ("Category", None), ("4,820", None),
                 ("45%", None), ("310", None), ("2,214", PRIMARY)],
                [("Marco", None), ("Percentage", None), ("3,140", None),
                 ("40%", None), ("180", None), ("1,274", PRIMARY)],
                [("Aisha", None), ("Flat", None), ("2,660", None),
                 ("8/visit", None), ("95", None), ("452", PRIMARY)]],
               row_h=80, head_h=58)
    panel(d, [130, 1400, S - 130, 1700], fill=PRIMARY)
    center_fit(d, 1450, "Earned versus released, tips split, adjustments "
                        "typed and shown", F_SANS_B, 48, WHITE,
               130, S - 130)
    center_fit(d, 1560, "one statement per person per month, ready to "
                        "print with the pay run", F_SANS, 44, PRIMARY_SOFT,
               130, S - 130)
    brand_footer(d, 1800)
    return img


def img_payroll() -> Image.Image:
    img = dim(cover(ASSETS / "bg_tools.jpg"), 160)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "TABS 10-11 · PAYROLL & EXPENSES", F_SANS_B(42),
         WHITE, PRIMARY)
    panel(d, [110, 300, 980, 1080], fill=WHITE, outline=GREY_SOFT, width=2)
    d.text((170, 330), "PAYROLL & TIPS", font=F_SANS_B(44),
           fill=PRIMARY_DEEP)
    mock_table(d, 170, 410, [260, 180, 180, 190],
               ["PERSON", "HOURS", "RATE", "GROSS"],
               [[("Aisha", None), ("32", None), ("16", None),
                 ("512", PRIMARY)],
                [("Marco", None), ("38", None), ("0", GREY),
                 ("comm.", GREY)],
                [("Front desk", None), ("24", None), ("15", None),
                 ("360", PRIMARY)]],
               row_h=76, head_h=56)
    for i, line in enumerate(["employer burden added on top",
                              "tips logged, split and reported",
                              "pay runs totalled per period"]):
        d.text((170, 760 + i * 56), "- " + line, font=F_SANS(36),
               fill=GREY)
    panel(d, [1020, 300, S - 110, 1080], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((1080, 330), "EXPENSES", font=F_SANS_B(44), fill=PRIMARY_DEEP)
    mock_table(d, 1080, 410, [240, 300, 200],
               ["DATE", "CATEGORY", "AMOUNT"],
               [[("01 May", None), ("Rent", None), ("2,400", PRIMARY)],
                [("03 May", None), ("Product & stock", None),
                 ("610", PRIMARY)],
                [("05 May", None), ("Card fees", None),
                 ("188", PRIMARY)]],
               row_h=76, head_h=56)
    for i, line in enumerate(["recurring costs on their own schedule",
                              "every line in a category the P&L reads",
                              "supplier and method on the row"]):
        d.text((1080, 760 + i * 56), "- " + line, font=F_SANS(36),
               fill=GREY)
    panel(d, [110, 1150, S - 110, 1560], fill=(255, 255, 255, 235))
    center_fit(d, 1210, "WAGES, COMMISSION, TAXES AND EVERY COST",
               F_SANS_B, 52, PRIMARY_DEEP)
    center_fit(d, 1330, "flow straight into the profit & loss - nothing "
                        "re-keyed, nothing missed", F_SANS, 44, GREY)
    center_fit(d, 1430, "400 expense rows and 300 payroll rows of room",
               F_SANS, 44, GREY)
    brand_footer(d, 1700, PRIMARY_SOFT)
    return img


def img_inventory() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_products.jpg"), 70), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 180, "TABS 13-14 · STOCK & PURCHASES", F_SANS_B(42),
         WHITE, PRIMARY)
    center_fit(d, 280, "THE STOCK ROOM,", F_SERIF, 110, WHITE)
    center_fit(d, 410, "COUNTED FOR YOU", F_SERIF, 110, ACCENT_SOFT)
    panel(d, [110, 560, S - 110, 1030], fill=WHITE)
    mock_table(d, 160, 600, [420, 220, 220, 220, 240],
               ["PRODUCT", "KIND", "ON HAND", "REORDER", "COVER"],
               [[("Olaplex No.3", None), ("Retail", None), ("14", None),
                 ("8", None), ("5 wks", GOOD)],
                [("Colour 6.0, 100 ml", None), ("Backbar", None),
                 ("5", None), ("6", None), ("1 wk", BAD)],
                [("Gel base coat", None), ("Backbar", None), ("9", None),
                 ("4", None), ("3 wks", ACCENT)]],
               row_h=84, head_h=58)
    feats = ["on hand = opening + received - used - sold - wasted + "
             "adjustments",
             "purchase orders flip to received and the stock count "
             "follows",
             "weeks of cover against your reorder point - the shelf "
             "never surprises you",
             "retail and backbar kept apart, so margins stay honest"]
    y = 1090
    for f in feats:
        tick(d, 150, y + 4, 38, ACCENT)
        lines = wrap(d, f, F_SANS(40), S - 330)
        for j, line in enumerate(lines[:2]):
            d.text((220, y + j * 50), line, font=F_SANS(40), fill=WHITE)
        y += 50 * min(len(lines), 2) + 30
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_marketing() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "MARKETING & LOYALTY", "Spend that pays, clients that return")
    panel(d, [120, 330, 980, 1080], fill=WHITE, outline=GREY_SOFT, width=2)
    d.text((180, 360), "CAMPAIGNS", font=F_SANS_B(44), fill=PRIMARY_DEEP)
    mock_table(d, 180, 440, [300, 180, 260],
               ["CAMPAIGN", "SPEND", "BROUGHT IN"],
               [[("Spring colour", None), ("240", None),
                 ("1,860", GOOD)],
                [("Referral month", None), ("0", GREY),
                 ("940", GOOD)],
                [("Local press", None), ("380", None),
                 ("210", BAD)]],
               row_h=76, head_h=56)
    for i, line in enumerate(["cost per new client, worked out",
                              "channel on every campaign",
                              "planned, running, finished - dated"]):
        d.text((180, 760 + i * 56), "- " + line, font=F_SANS(36),
               fill=GREY)
    panel(d, [1020, 330, S - 120, 1080], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((1080, 360), "LOYALTY & GIFT CERTS", font=F_SANS_B(40),
           fill=PRIMARY_DEEP)
    bars(d, 1080, 520, 1500, 760, [12, 18, 22, 26, 31, 38], PRIMARY_MID)
    d.text((1080, 790), "points earned per month", font=F_SANS(34),
           fill=GREY)
    for i, line in enumerate([
            "points per spend, reward at your threshold",
            "gift certificate sales held until redeemed",
            "packages prepaid and drawn down honestly"]):
        d.text((1080, 880 + i * 52), "- " + line, font=F_SANS(34),
               fill=GREY)
    panel(d, [120, 1140, S - 120, 1560], fill=PRIMARY)
    center_fit(d, 1200, "KNOW WHICH CHANNEL ACTUALLY PAID", F_SANS_B, 52,
               WHITE)
    center_fit(d, 1320, "and which clients are one nudge away from "
                        "coming back", F_SANS, 44, PRIMARY_SOFT)
    center_fit(d, 1420, "spend follows revenue, not vibes", F_SANS, 44,
               PRIMARY_SOFT)
    brand_footer(d, 1680)
    return img


def img_pnl() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "PROFIT & LOSS", "The month on one honest page")
    panel(d, [140, 330, 1240, 1240], fill=WHITE, outline=GREY_SOFT,
          width=2)
    mock_table(d, 200, 380, [460, 260, 260],
               ["LINE", "THIS MONTH", "LAST MONTH"],
               [[("Revenue", None), ("14,380", PRIMARY),
                 ("13,210", PRIMARY)],
                [("Product & stock cost", None), ("1,940", None),
                 ("1,810", None)],
                [("Wages & commission", None), ("6,420", None),
                 ("6,110", None)],
                [("Rent & utilities", None), ("2,860", None),
                 ("2,860", None)],
                [("Marketing", None), ("620", None), ("380", None)],
                [("Operating profit", None), ("2,540", GOOD),
                 ("2,050", GOOD)]],
               row_h=86, head_h=60)
    panel(d, [1300, 330, S - 140, 1240], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((1360, 360), "BREAK-EVEN", font=F_SANS_B(40),
           fill=PRIMARY_DEEP)
    bars(d, 1360, 520, 1860, 820, [9.8, 10.4, 11.1, 10.6, 11.9, 12.4],
         ACCENT)
    d.text((1360, 850), "revenue needed per month,", font=F_SANS(34),
           fill=GREY)
    d.text((1360, 894), "fixed vs variable split", font=F_SANS(34),
           fill=GREY)
    for i, line in enumerate(["margin per line, % of revenue",
                              "this month against last",
                              "year-to-date column alongside"]):
        d.text((1360, 990 + i * 56), "- " + line, font=F_SANS(36),
               fill=GREY)
    panel(d, [140, 1310, S - 140, 1660], fill=PRIMARY_SOFT)
    center_fit(d, 1360, "Fixed costs, variable costs and the line between "
                        "them", F_SANS_B, 46, PRIMARY_DEEP)
    center_fit(d, 1470, "so break-even is a number you can argue with, "
                        "not a feeling", F_SANS, 42, GREY)
    brand_footer(d, 1760)
    return img


def img_reports() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "REPORTS & ANALYTICS", "Sunday, ten minutes, the whole "
                                   "picture")
    panel(d, [120, 330, 980, 1080], fill=WHITE, outline=GREY_SOFT, width=2)
    d.text((180, 360), "WEEKLY & MONTHLY", font=F_SANS_B(44),
           fill=PRIMARY_DEEP)
    qs = ["Revenue vs last week and vs target",
          "Bookings completed, cancelled, no-shows",
          "Retail share and average ticket",
          "New clients vs returning",
          "Busiest days and hours",
          "Commission and wage totals for the period"]
    yy = 450
    for q in qs:
        tick(d, 180, yy + 4, 34)
        lines = wrap(d, q, F_SANS(36), 640)
        for j, line in enumerate(lines[:2]):
            d.text((240, yy + j * 44), line, font=F_SANS(36), fill=GREY)
        yy += 44 * min(len(lines), 2) + 34
    panel(d, [1020, 330, S - 120, 1080], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((1080, 360), "ANALYTICS", font=F_SANS_B(40),
           fill=PRIMARY_DEEP)
    bars(d, 1080, 520, 1500, 760, [11, 12, 13, 12.6, 13.8, 14.4],
         PRIMARY_MID)
    d.text((1080, 790), "revenue by month", font=F_SANS(34), fill=GREY)
    bars(d, 1540, 520, 1850, 760, [62, 58, 71, 66, 74, 69], ACCENT)
    d.text((1540, 790), "bookings by weekday", font=F_SANS(34),
           fill=GREY)
    for i, line in enumerate([
            "revenue by category and by stylist",
            "retail versus service split",
            "rebooking and retention rates",
            "top and bottom services, ranked"]):
        d.text((1080, 880 + i * 52), "- " + line, font=F_SANS(34),
               fill=GREY)
    panel(d, [120, 1140, S - 120, 1560], fill=PRIMARY)
    center_fit(d, 1200, "THE MONTHLY REPORT LANDS ON ONE PRINTABLE PAGE",
               F_SANS_B, 52, WHITE)
    center_fit(d, 1320, "revenue, costs, profit, clients and the month's "
                        "own notes", F_SANS, 44, PRIMARY_SOFT)
    center_fit(d, 1420, "print it, pin it above the desk, keep going",
               F_SANS, 44, PRIMARY_SOFT)
    brand_footer(d, 1680)
    return img


def img_how() -> Image.Image:
    img = dim(cover(ASSETS / "bg_desk.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "RUNNING IN TEN MINUTES", F_SANS_B(42), WHITE,
         PRIMARY)
    steps = [("1", "OPEN & SET UP",
              "tab 20 Settings & Lists: your salon name, currency, tax "
              "rate, card fees, commission rates and every drop-down "
              "list"),
             ("2", "FILL THE DIARY DAILY",
              "one row per booking, sale, payment, expense; pick clients "
              "and services from drop-downs so spellings always match"),
             ("3", "READ IT BACK",
              "tab 2 every morning, tab 9 at payday, tab 12 at month end "
              "- the dashboard and reports do the reading for you")]
    y = 330
    for num, title, body in steps:
        panel(d, [140, y, S - 140, y + 360], fill=(255, 255, 255, 240))
        d.ellipse([210, y + 60, 350, y + 200], fill=ACCENT)
        center_text(d, y + 82, num, F_SERIF(96), WHITE, 210, 350)
        d.text((420, y + 60), title, font=F_SANS_B(56), fill=PRIMARY_DEEP)
        lines = wrap(d, body, F_SANS(42), S - 620)
        for j, line in enumerate(lines[:3]):
            d.text((420, y + 150 + j * 56), line, font=F_SANS(42),
                   fill=INK)
        y += 400
    center_text(d, 1620, "HOW TO RUN.txt walks the same three steps in "
                         "plain words.", F_SANS(42), PRIMARY_SOFT)
    brand_footer(d, 1720, PRIMARY_SOFT)
    return img


def img_features() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "BUILT TO LAST", "No gimmicks - just a file that keeps working")
    feats = [("EXCEL 2010 AND NEWER",
              "written without XLOOKUP, IFS, LET or dynamic arrays - no "
              "365 subscription needed"),
             ("NO MACROS, NO ADD-INS",
              "plain formulas only, so nothing asks permission or phones "
              "home"),
             ("FORMULAS LOCKED",
              "sheets protected with a password; white cells stay yours "
              "to type in"),
             ("ANY CURRENCY, ANY COUNTRY",
              "symbol, tax rate, fees and lists are settings - nothing is "
              "hard-coded to one place"),
             ("ROOM TO GROW",
              "400 bookings, 600 sales and payment rows, 250 clients, 400 "
              "expenses - years of trading"),
             ("WORKS OFFLINE",
              "one file on your machine or your own cloud folder; Google "
              "Sheets and LibreOffice open it too")]
    x0, y0 = 130, 340
    for i, (t, b) in enumerate(feats):
        x = x0 + (i % 2) * 900
        y = y0 + (i // 2) * 420
        panel(d, [x, y, x + 860, y + 390], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x, y, x + 860, y + 14], fill=PRIMARY_MID)
        center_fit(d, y + 44, t, F_SANS_B, 44, PRIMARY_DEEP, x, x + 860)
        lines = wrap(d, b, F_SANS(38), 740)
        for j, line in enumerate(lines[:4]):
            center_text(d, y + 130 + j * 54, line, F_SANS(38), GREY,
                        x, x + 860)
    brand_footer(d, 1720)
    return img


def img_protected() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_salon.jpg"), 115), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 200, "SAFE TO TYPE IN", F_SANS_B(44), WHITE, PRIMARY)
    center_fit(d, 320, "YOUR CELLS, OUR FORMULAS", F_SERIF, 120, WHITE)
    panel(d, [140, 520, S - 140, 1180], fill=(255, 255, 255, 240))
    rows = [("WHITE CELLS", "unlocked - dates, clients, prices, notes: "
                            "16,218 of them in the sample file"),
            ("PALE CELLS", "locked formulas - 20,509 of them, guarding "
                           "every total, rate and statement"),
            ("PASSWORD", "premium - Review > Unprotect Sheet if you ever "
                         "want to customise, then protect again")]
    y = 580
    for t, b in rows:
        d.text((220, y), t, font=F_SANS_B(46), fill=PRIMARY_DEEP)
        lines = wrap(d, b, F_SANS(40), S - 560)
        for j, line in enumerate(lines[:2]):
            d.text((220, y + 66 + j * 52), line, font=F_SANS(40),
                   fill=INK)
        y += 66 + 52 * 2 + 30
    center_text(d, 1260, "Accidentally type over a formula? It cannot "
                         "happen - that is the point.", F_SANS(46), WHITE)
    center_text(d, 1350, "Drop-downs keep spellings consistent, so "
                         "SUMIFS always finds its rows.", F_SANS(42),
                PRIMARY_SOFT)
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_whofor() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "WHO IT IS FOR", "Any chair, any starting line")
    folks = [("SOLO STYLISTS & ARTISTS",
              "one chair, one book: bookings, money and stock in a single "
              "file instead of five apps"),
             ("SMALL SALON TEAMS",
              "commission statements per person per month end the payday "
              "argument before it starts"),
             ("NAIL, LASH & BROW STUDIOS",
              "services, retail and backbar all fit the same registers - "
              "the categories are yours to rename"),
             ("BARBERS & CHAIR RENTERS",
              "flat-per-service and rent rows sit beside percentage "
              "commission, per person"),
             ("FIRST-TIME OWNERS",
              "the example salon shows every tab working before you type "
              "a single number of your own")]
    y = 340
    for t, b in folks:
        panel(d, [140, y, S - 140, y + 220], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([140, y, 158, y + 220], fill=ACCENT)
        d.text((220, y + 26), t, font=F_SANS_B(46), fill=PRIMARY_DEEP)
        lines = wrap(d, b, F_SANS(38), S - 320)
        for j, line in enumerate(lines[:2]):
            d.text((220, y + 100 + j * 50), line, font=F_SANS(38),
                   fill=GREY)
        y += 244
    center_text(d, y + 20, "A business organiser, not accounting or tax "
                           "advice - check the numbers with your "
                           "accountant.", F_SANS(38), GREY)
    brand_footer(d, y + 110)
    return img


def img_thankyou() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_salon.jpg"), 90), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 260, "THANK YOU", F_SANS_B(48), INK, ACCENT_SOFT)
    center_fit(d, 400, "YOUR SALON,", F_SERIF, 150, WHITE)
    center_fit(d, 580, "ONE HONEST FILE", F_SERIF, 150, WHITE)
    center_text(d, 830, "No apps to install, no subscriptions, no bookings "
                        "held hostage in", F_SANS(46), PRIMARY_SOFT)
    center_text(d, 900, "someone else's cloud. Just your business, "
                        "working for you.", F_SANS(46), PRIMARY_SOFT)
    panel(d, [300, 1060, S - 300, 1560], fill=(255, 255, 255, 235))
    center_fit(d, 1110, "QUESTIONS? MESSAGE THE SHOP", F_SANS_B, 48,
               PRIMARY_DEEP)
    center_fit(d, 1210, "we answer fast, and setup help is always free",
               F_SANS, 42, GREY)
    center_fit(d, 1310, "more Novality spreadsheets in the shop:",
               F_SANS, 40, GREY)
    center_fit(d, 1390, "fitness · pricing · cleaning CRM · social "
                        "planner · meal planner", F_SANS_B, 42, PRIMARY,
               320, S - 320)
    brand_footer(d, 1700, WHITE)
    return img


IMAGES = [
    ("01-cover.jpg", img_cover),
    ("02-what-you-get.jpg", img_what_you_get),
    ("03-tabs.jpg", img_tabs),
    ("04-dashboard.jpg", img_dashboard),
    ("05-appointments.jpg", img_appointments),
    ("06-clients.jpg", img_clients),
    ("07-services.jpg", img_services),
    ("08-sales-payments.jpg", img_sales),
    ("09-commission.jpg", img_commission),
    ("10-payroll-expenses.jpg", img_payroll),
    ("11-inventory.jpg", img_inventory),
    ("12-marketing-loyalty.jpg", img_marketing),
    ("13-profit-loss.jpg", img_pnl),
    ("14-reports-analytics.jpg", img_reports),
    ("15-how.jpg", img_how),
    ("16-features.jpg", img_features),
    ("17-who-for.jpg", img_whofor),
    ("18-thankyou.jpg", img_thankyou),
]


# ============================================================ listing copy
TITLES = """\
Primary (140 chars max):
Salon Business Spreadsheet, Appointment & Client Tracker Excel, Commission
Calculator, Salon Income Expense Profit & Inventory Template

Alt 1:
Hair Salon Management Template, Booking Diary & Client CRM, Staff
Commission & Payroll, Profit & Loss, Inventory, Beauty Business Planner

Alt 2:
Salon Bookkeeping Spreadsheet, Sales Payments Deposit Tracker, Service
Price List, Marketing & Loyalty, Nail Lash Studio Excel Template
"""

TAGS = """\
salon spreadsheet
salon planner
salon booking
salon client list
hair salon tracker
salon bookkeeping
commission tracker
salon inventory
beauty business
nail tech planner
salon price list
salon income
lash artist planner
"""

BULLETS = """\
WHAT YOU GET
- Salon Business Management System.xlsx - 20 tabs filled with eleven months
  of a realistic example salon (Bloom & Blade Studio) so you can watch
  every formula work before you type a thing
- Salon Business Management System (Blank).xlsx - same workbook, empty
  registers, ready for day one
- HOW TO RUN.txt - one page of plain-English setup and the money rules the
  workbook follows

WHAT IT RUNS
- Appointments: 400-row diary; pick client and service from drop-downs and
  price, duration, deposit and balance fill themselves; statuses flow
  booked to completed, cancelled or no-show with the rates computed
- Clients: 250-row CRM with colour formula, allergies, patch-test date,
  consents, preferences, last visit, auto next-due rebooking date, visits
  and lifetime spend
- Services & pricing: your menu with duration, price, direct cost and an
  honest margin column; category roll-ups and slow-mover flags
- Sales & payments: gross, discount, tax and net per line; deposits held
  as unearned until the visit completes - never counted twice; card fees
  worked out; outstanding balances listed
- Staff & commissions: three pay models (percentage, category rate, flat
  per service) plus retail commission; one printable statement per person
  per month, earned vs released, tips and adjustments shown
- Payroll & tips, expenses: hours x rate with employer burden, tips logged
  and split; recurring costs on schedule; 400 expense rows
- Inventory & purchases: on hand = opening + received - used - sold -
  wasted + adjustments; purchase orders feed stock; weeks of cover against
  your reorder point; retail and backbar kept apart
- Marketing & loyalty: campaign spend vs revenue brought in and cost per
  new client; loyalty points, gift certificates and packages held until
  redeemed
- Dashboard, profit & loss, goals & budget, analytics and weekly/monthly
  reports: revenue vs target, break-even with fixed/variable split,
  revenue by category and stylist, busiest days, retention - and a
  one-page printable monthly report

WHY IT IS DIFFERENT
- Excel 2010 and newer: no XLOOKUP, IFS, LET or dynamic arrays, so no 365
  subscription is needed; also opens in Google Sheets, LibreOffice and
  Numbers
- No macros, no add-ins, no accounts, nothing phones home
- Formulas locked behind the password "premium"; white cells stay unlocked
  for you (16,218 in the sample, 929 in the blank)
- Any currency, any country: symbol, tax rate, fees, commission rates and
  every drop-down list are settings, nothing hard-coded
- Instant download, yours forever

PERFECT FOR
- Solo stylists, barbers, nail, lash and brow artists
- Small salon teams who want payday without the argument
- Chair renters and first-time owners
- Anyone still running the business in five apps and a notebook
"""

HOW_TO_USE = """\
HOW TO USE YOUR SALON BUSINESS MANAGEMENT SYSTEM
------------------------------------------------

1. DOWNLOAD
After purchase, Etsy emails your download link and it also lives in
You > Purchases and reviews. Unzip the folder.

2. OPEN THE RIGHT FILE
- "Salon Business Management System.xlsx" has eleven months of example
  salon data (Bloom & Blade Studio). Browse it first - every tab shows
  what it will do for you.
- "Salon Business Management System (Blank).xlsx" is the one to live in.

3. SET UP (TEN MINUTES, ONCE)
- Tab 20 Settings & Lists: salon name, currency symbol, tax rate and what
  it applies to, card fees, deposit rule, commission rates per person and
  per category, loyalty rules, and every drop-down list.
- Tab 8 Staff Management: one row per person with their commission method
  (Percentage, Category or Flat).
- Tab 5 Services & Pricing: your menu with durations, prices and direct
  costs.

4. RUN THE DAY
- Tab 3 one row per booking; pick client and service from the drop-downs.
- Tab 6 one row per sale line (service vs retail keeps commission and
  stock honest); tab 7 for payments and deposits.
- Tab 10 payroll, tab 11 expenses, tab 14 purchase orders as they happen.
White cells accept typing. Pale cells are locked formulas.

5. READ IT BACK
- Tab 2 every morning: revenue, target, bookings, deposits held, what to
  do next.
- Tab 9 at payday: one commission statement per person.
- Tab 12 at month end: the profit & loss and break-even.
- Tab 19 for the weekly and monthly report pages.

PROTECTION
Sheets are protected with the password: premium
White cells are unlocked and yours to type in. Pale cells are locked
formulas. To customise: Review > Unprotect Sheet > premium, change what
you need, re-protect.

MONEY RULES THIS WORKBOOK FOLLOWS
- Net sales = gross - discounts - refunds + tax.
- A deposit is not revenue until the visit completes and the sale is
  invoiced; unearned deposits are reported separately.
- Commission = eligible service revenue x the applicable rate + retail at
  the retail rate, plus typed adjustments.
- Inventory on hand = opening + received - used - sold - wasted +
  adjustments; received reads the purchase register.
- Break-even treats rent, utilities, insurance, software and payroll as
  fixed and everything else as variable.

TIPS
- One row per record; the formulas cover hundreds of rows each.
- Drop-downs read the Settings & Lists tab - add your own values there.
- The example is a real eleven-month salon; delete it row by row, or just
  open the BLANK file instead.
- Keep a copy of the file before big customisations.

Made by Novality Store. Questions? Message the shop - we reply fast.
"""

ATTRIBUTES = """\
Type: Digital download - spreadsheet template (.xlsx)
Compatible with: Excel 2010+, Excel 365, Google Sheets, LibreOffice, Numbers
Macros: none
Sheets: 20 tabs, 20,509 formulas, drop-down validations on every register
Versions: filled example (11 months) + blank template
Language: English
Customisable: currency symbol and code, tax rate and scope, card fees,
deposit rule, commission rates and methods, loyalty rules, all drop-down
lists, row counts
Included extras: client CRM with colour formulas, service margin maths,
commission statements, break-even calculator, printable monthly report
Delivery: instant download, two .xlsx files + HOW TO RUN.txt
Use: salon booking diary, client CRM, sales and payment tracking, staff
commission, payroll, expenses, profit & loss, inventory, marketing,
loyalty
Limits (stated honestly): organises bookings and money; does not send
confirmations or reminders, does not sync with booking platforms, is not
accounting, payroll or tax advice
"""

FAQ = """\
Q. Will it work in my Excel?
A. Excel 2010 and every version since, on Windows and Mac, plus Excel for
the web, Google Sheets, LibreOffice Calc and Apple Numbers. It is written
without XLOOKUP, LET, IFS or dynamic arrays, so nothing needs a 365
subscription.

Q. Do I have to delete the example data?
A. No. The BLANK file is the same workbook with empty registers. Use the
filled one to learn it, the blank one to run your salon.

Q. I run a nail / lash / barber studio, not a hair salon - will it fit?
A. Yes. Every list (service categories, expense categories, payment
methods, channels) is editable on tab 20, and the registers care only
about dates, people, services and money.

Q. How does commission work for my team?
A. Each person gets their own method on tab 8: a percentage of their
service revenue, a rate per service category, or a flat amount per
completed service, plus retail commission. Tab 9 prints one statement per
person per month with tips and adjustments shown.

Q. My country's tax rules are different - is that a problem?
A. No. The tax rate, what it applies to, the currency symbol and the
rounding are settings on tab 20. Nothing is hard-coded to one country.
The workbook organises your numbers; your accountant decides what they
mean.

Q. Can I break it by typing in the wrong place?
A. Practically no. Formula cells are locked behind the password "premium";
only white input cells accept typing, and drop-downs keep spellings
consistent so the totals always find their rows.

Q. Does it send booking confirmations or sync with my booking app?
A. No, and it never will - it is a spreadsheet, not a booking platform.
It organises what already happened and tells you what to chase next.

Q. Is my data sent anywhere?
A. No. It is one file on your machine or your own cloud folder. There are
no macros, no links out, no telemetry.

Q. What exactly do I get?
A. Two workbooks (filled example + blank), HOW TO RUN.txt, and the
printable monthly report page inside the workbook. Instant download from
your Etsy account.
"""

KEYWORDS = """
salon business spreadsheet
hair salon management excel
salon appointment book
salon client tracker
commission calculator excel
salon bookkeeping template
salon income expense tracker
nail tech business planner
lash artist spreadsheet
salon inventory tracker
salon price list template
beauty salon bookkeeping
salon profit and loss
chair rental tracker
salon payroll template
salon marketing tracker
client loyalty spreadsheet
salon dashboard excel
"""


def write_copy() -> int:
    COPY_OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "TITLES.txt": TITLES,
        "TAGS.txt": TAGS,
        "BULLET_POINTS.txt": BULLETS,
        "DESCRIPTION.txt": BULLETS + "\n" + HOW_TO_USE,
        "HOW_TO_USE.txt": HOW_TO_USE,
        "ATTRIBUTES.txt": ATTRIBUTES,
        "FAQ.txt": FAQ,
        "KEYWORDS.txt": KEYWORDS,
    }
    for name, text in files.items():
        (COPY_OUT / name).write_text(text, encoding="utf-8")
    return len(files)


def stage_spreadsheets() -> int:
    """Copy the two workbooks into the kit: prefer a fresh local build,
    otherwise unpack them from the delivered product zip."""
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)
    out = ROOT / "output"
    n = 0
    for name in (FILLED_NAME, BLANK_NAME):
        src = out / name
        if src.exists():
            shutil.copy2(src, SHEETS_OUT / name)
            n += 1
    if n == 2:
        return n
    if not PRODUCT_ZIP.exists():
        raise SystemExit(f"missing {PRODUCT_ZIP} - restore it from git")
    with zipfile.ZipFile(PRODUCT_ZIP) as z:
        for name in (FILLED_NAME, BLANK_NAME):
            data = z.read(ZIP_PREFIX + name)
            (SHEETS_OUT / name).write_bytes(data)
            n += 1
    return n


def build_images() -> int:
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in IMAGES:
        img = fn()
        path = IMG_OUT / name
        img.save(path, "JPEG", quality=88, optimize=True)
        print(f"  {name}  {img.size[0]}x{img.size[1]}  "
              f"{path.stat().st_size // 1024} KB")
    return len(IMAGES)


def contact_sheets(tile: int = 1000, per: int = 6) -> int:
    """QA grids so every image can be eyeballed for overflow at a glance."""
    paths = [IMG_OUT / name for name, _ in IMAGES]
    n = 0
    for i in range(0, len(paths), per):
        batch = paths[i:i + per]
        cols, rows = 2, (len(batch) + 1) // 2
        sheet = Image.new("RGB", (cols * tile, rows * tile), (30, 30, 30))
        for j, p in enumerate(batch):
            im = Image.open(p).resize((tile, tile), Image.LANCZOS)
            sheet.paste(im, ((j % cols) * tile, (j // cols) * tile))
        out = KIT / f"qa-contact-{n + 1}.png"
        sheet.save(out)
        print(f"  contact sheet {out}")
        n += 1
    return n


def build_kit(contact: bool = False) -> None:
    n_sheets = stage_spreadsheets()
    n_img = build_images()
    if contact:
        contact_sheets()
    n_copy = write_copy()
    print(f"sheets: {n_sheets}, images: {n_img}, copy files: {n_copy}")

    DOWNLOAD.mkdir(exist_ok=True)
    target = DOWNLOAD / "salon-business-etsy-kit.zip"
    n = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (IMG_OUT, COPY_OUT, SHEETS_OUT):
            for path in sorted(folder.iterdir()):
                if path.is_file():
                    z.write(path, f"{folder.name}/{path.name}")
                    n += 1
    print(f"{target.name}: {n} files "
          f"({target.stat().st_size / 1024 / 1024:.1f} MB)")
    with zipfile.ZipFile(target) as zf:
        bad = zf.testzip()
        print(f"integrity: {'OK' if bad is None else bad}, "
              f"{len(zf.namelist())} entries")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact", action="store_true",
                    help="also write QA contact sheets into etsy/kit/")
    build_kit(contact=ap.parse_args().contact)
