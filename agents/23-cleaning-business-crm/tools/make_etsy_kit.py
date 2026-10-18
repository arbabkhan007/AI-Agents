"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Cleaning Business CRM & Pricing Calculator spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, description, bullets,
                                    how-to-use
    etsy/kit/spreadsheets/          filled sample + blank template
    download/cleaning-business-crm-etsy-kit.zip

Usage:
    python tools/make_etsy_kit.py

AI imagery is used only for the four text-free background photos in
etsy/assets/. Every word in the kit is typeset here with PIL/DejaVu.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ETSY = ROOT / "etsy"
ASSETS = ETSY / "assets"
KIT = ETSY / "kit"
IMG_OUT = KIT / "etsy-listing-images"
COPY_OUT = KIT / "listing-copy"
SHEETS_OUT = KIT / "spreadsheets"
DOWNLOAD = ROOT / "download"

FILLED = ROOT / "output" / "Cleaning Business CRM & Pricing Calculator.xlsx"
BLANK = (ROOT / "output" /
         "Cleaning Business CRM & Pricing Calculator (Blank).xlsx")

S = 2000                     # canvas size

# ---- brand palette (deep teal / aqua / citrus / cream) ---------------------
INK        = (16, 42, 48)        # #102A30
TEAL       = (20, 97, 107)       # #14616B
TEAL_MID   = (47, 143, 157)      # #2F8F9D
TEAL_SOFT  = (220, 238, 240)     # #DCEEF0
TEAL_DEEP  = (10, 58, 66)
CITRUS     = (232, 163, 61)      # #E8A33D
CITRUS_SOFT = (253, 240, 217)    # #FDF0D9
CREAM      = (247, 243, 234)     # #F7F3EA
CREAM_DARK = (232, 225, 210)
WHITE      = (255, 255, 255)
GREY       = (90, 106, 109)      # #5A6A6D
GREY_SOFT  = (208, 220, 222)
GOOD       = (17, 104, 74)
GOOD_SOFT  = (215, 242, 227)
BAD        = (156, 28, 46)
BAD_SOFT   = (251, 217, 221)
AMBER      = (138, 90, 0)
AMBER_SOFT = (255, 240, 206)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)      # noqa: E731
F_SANS = lambda s: font("DejaVuSans.ttf", s)             # noqa: E731


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


def dim(img: Image.Image, alpha: int = 120, color=(10, 40, 46)) -> Image.Image:
    overlay = Image.new("RGB", img.size, color)
    return Image.blend(img.convert("RGB"), overlay, alpha / 255)


def scrim(img: Image.Image, side: str = "bottom") -> Image.Image:
    """Soft dark gradient so text stays readable over photos."""
    grad = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(grad)
    for i in range(img.size[1]):
        t = i / img.size[1]
        if side == "bottom":
            a = int(210 * max(0, t - 0.32) / 0.68)
        elif side == "top":
            a = int(210 * max(0, 0.5 - t) / 0.5)
        else:
            a = 115
        d.line([(0, i), (img.size[0], i)], fill=a)
    dark = Image.new("RGB", img.size, (12, 38, 44))
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
    draw.text((S / 2 - tw(draw, "by Novality Store", F_SANS_B(38)) / 2, y),
              "by Novality Store", font=F_SANS_B(38), fill=color)


def kicker(draw, y, s, color=CITRUS):
    center_text(draw, y, s, F_SANS_B(42), color)


# ============================================================== the 18 images
def img_cover() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_kitchen.jpg"), 70), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 300, "INSTANT DOWNLOAD", F_SANS_B(44), INK, CITRUS)
    center_fit(d, 430, "CLEANING BUSINESS", F_SERIF, 178, WHITE)
    center_fit(d, 630, "CRM & PRICING", F_SERIF, 178, WHITE)
    center_fit(d, 830, "CALCULATOR", F_SERIF, 178, CITRUS)
    center_text(d, 1080, "37 tabs  ·  111,000+ formulas  ·  Excel 2010–365",
                F_SANS_B(56), TEAL_SOFT)
    center_text(d, 1170, "Quotes · Scheduling · Invoices · Expenses · Reports",
                F_SANS(50), TEAL_SOFT)
    # stat strip
    stats = [("37", "TABS"), ("111K+", "FORMULAS"), ("2", "VERSIONS"),
             ("$0", "SUBSCRIPTIONS")]
    bw = 380
    x = S / 2 - (len(stats) * bw + (len(stats) - 1) * 30) / 2
    for big, small in stats:
        panel(d, [x, 1330, x + bw, 1560], fill=(255, 255, 255))
        center_text(d, 1370, big, F_SERIF(86), TEAL, x, x + bw)
        center_text(d, 1490, small, F_SANS_B(34), GREY, x, x + bw)
        x += bw + 30
    brand_footer(d, 1870, WHITE)
    return img


def img_what_you_get() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 140, "YOUR PURCHASE")
    center_text(d, 220, "WHAT YOU GET", F_SERIF(140), INK)
    cards = [
        ("2 COMPLETE WORKBOOKS",
         "A filled example you can study - a real cleaning company with\n"
         "jobs, invoices and payments already in it - plus a clean blank\n"
         "version to start fresh."),
        ("37 WIRED-TOGETHER TABS",
         "CRM, quote calculator, job scheduler, crews and timesheets,\n"
         "job costing, invoicing, stock, expenses, retention, safety,\n"
         "financial plan and reports. Nothing extra to buy."),
        ("3 PRINTABLE DOCUMENTS",
         "Client-ready Print Quote, Print Invoice and Print Job Sheet.\n"
         "Type a number into the yellow cell - the document builds itself.\n"
         "Print area pre-set to one page."),
    ]
    y = 470
    for title, body in cards:
        panel(d, [160, y, S - 160, y + 380], fill=WHITE, outline=TEAL_SOFT)
        d.rounded_rectangle([160, y, 220, y + 380], 26, fill=TEAL)
        d.text((280, y + 52), title, font=F_SANS_B(58), fill=TEAL)
        for i, line in enumerate(body.split("\n")):
            d.text((280, y + 150 + i * 62), line, font=F_SANS(44),
                   fill=GREY)
        y += 440
    brand_footer(d)
    return img


def img_tabs() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 140, "ONE FILE, THE WHOLE BACK OFFICE", CITRUS)
    center_text(d, 220, "EVERYTHING INSIDE", F_SERIF(140), WHITE)
    groups = [
        ("CRM & SALES", ["Clients", "Properties", "Leads", "Services",
                         "Quotes", "Quote Lines", "Quote Calculator"]),
        ("SCHEDULING", ["Jobs", "Job Tasks", "Calendar", "Checklists",
                        "Staff Schedule", "Employees", "Timesheets"]),
        ("MONEY", ["Job Costing", "Invoices", "Invoice Lines",
                   "Payments", "Expenses", "Mileage", "Financial Plan"]),
        ("OPERATIONS", ["Supplies", "Supply Usage", "Equipment",
                        "Client Retention", "Complaints", "Incidents",
                        "Safety"]),
        ("INSIGHT & DOCS", ["Dashboard", "Reports", "Print Quote",
                            "Print Invoice", "Print Job Sheet",
                            "Settings", "Lists & Help"]),
    ]
    y = 460
    for name, tabs in groups:
        panel(d, [160, y, S - 160, y + 220], fill=(255, 255, 255))
        d.text((220, y + 22), name, font=F_SANS_B(42), fill=CITRUS)
        x, cy = 220, y + 108
        for tab in tabs:
            w, h = chip(d, x, cy - 26, tab, F_SANS_B(34), TEAL,
                        TEAL_SOFT, pad_x=22, pad_y=12, radius=28)
            x += w + 16
            if x > S - 380:
                x, cy = 220, cy + 64
        y += 250
    brand_footer(d, 1885, TEAL_SOFT)
    return img


def img_quote() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "THE HEADLINE FEATURE")
    center_text(d, 210, "PRICE A JOB IN 3 MINUTES", F_SERIF(118), INK)
    # calculator panel
    panel(d, [180, 430, 1180, 1660], fill=WHITE, outline=TEAL_SOFT)
    d.text((240, 470), "QUOTE CALCULATOR", font=F_SANS_B(46), fill=TEAL)
    rows = [
        ("Size", "2,400 sq ft"), ("Bedrooms", "4"),
        ("Bathrooms", "2.5"), ("Condition", "Needs attention"),
        ("Frequency", "Fortnightly"), ("Pets", "Yes"),
        ("Interior windows", "12"), ("Oven deep clean", "Yes"),
        ("Travel", "8 miles"), ("Discount", "5%"),
    ]
    y = 570
    for label, value in rows:
        d.text((250, y), label, font=F_SANS(40), fill=GREY)
        vw = tw(d, value, F_SANS_B(40))
        d.text((1110 - vw, y), value, font=F_SANS_B(40), fill=INK)
        d.line([(250, y + 62), (1110, y + 62)], fill=TEAL_SOFT, width=2)
        y += 82
    # result card
    panel(d, [1240, 430, 1860, 1000], fill=INK)
    center_text(d, 500, "QUOTE TOTAL", F_SANS_B(40), TEAL_SOFT, 1240, 1860)
    center_text(d, 570, "$312.00", F_SERIF(120), CITRUS, 1240, 1860)
    center_text(d, 730, "incl. 5% discount", F_SANS(36), TEAL_SOFT,
                1240, 1860)
    pill(d, 1550, 880, "MARGIN 41%", F_SANS_B(40), INK, GOOD_SOFT)
    # cost card
    panel(d, [1240, 1060, 1860, 1470], fill=WHITE, outline=TEAL_SOFT)
    center_text(d, 1110, "YOUR COST", F_SANS_B(38), GREY, 1240, 1860)
    lines = [("Labour (8.2 hrs)", "$174"), ("Supplies", "$21"),
             ("Travel", "$5"), ("Profit", "$112")]
    y = 1180
    for label, value in lines:
        d.text((1300, y), label, font=F_SANS(36), fill=GREY)
        vw = tw(d, value, F_SANS_B(36))
        d.text((1800 - vw, y), value, font=F_SANS_B(36), fill=INK)
        y += 66
    pill(d, 1550, 1570, "NEVER BELOW YOUR MINIMUM", F_SANS_B(36), INK,
         CITRUS_SOFT)
    brand_footer(d, 1860)
    return img


def img_dashboard() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "KNOW YOUR NUMBERS", CITRUS)
    center_fit(d, 210, "A DASHBOARD THAT TELLS THE TRUTH",
               F_SERIF, 92, WHITE)
    cards = [
        ("REVENUE THIS MONTH", "$5,240", "ON TARGET", GOOD_SOFT, GOOD),
        ("COSTS THIS MONTH", "$3,180", "UNDER BUDGET", GOOD_SOFT, GOOD),
        ("MARGIN THIS MONTH", "39%", "STRONG", CITRUS_SOFT, AMBER),
        ("BOOKED AHEAD", "$2,860", "NEXT 14 DAYS", TEAL_SOFT, TEAL),
    ]
    bw, bh = 800, 300
    for i, (label, big, tag, tag_bg, tag_fg) in enumerate(cards):
        x = 180 + (i % 2) * (bw + 40)
        y = 430 + (i // 2) * (bh + 40)
        panel(d, [x, y, x + bw, y + bh], fill=WHITE)
        d.text((x + 44, y + 40), label, font=F_SANS_B(38), fill=GREY)
        d.text((x + 44, y + 110), big, font=F_SERIF(110), fill=INK)
        chip(d, x + 44, y + 232, tag, F_SANS_B(32), tag_fg, tag_bg,
             pad_x=22, pad_y=10, radius=26)
    # alerts panel
    panel(d, [180, 1120, 1820, 1720], fill=CREAM)
    d.text((240, 1160), "TODAY'S ALERTS", font=F_SANS_B(44), fill=TEAL)
    alerts = [
        ("3", "Overdue invoices to chase"),
        ("2", "Quotes need a follow-up"),
        ("1", "Supply item at reorder level"),
        ("0", "Complaints open"),
    ]
    y = 1250
    for num, text in alerts:
        color = BAD if num != "0" else GOOD
        bg = BAD_SOFT if num != "0" else GOOD_SOFT
        chip(d, 250, y - 8, num, F_SANS_B(44), color, bg, pad_x=30,
             pad_y=12, radius=30)
        d.text((380, y + 4), text, font=F_SANS(42), fill=INK)
        y += 110
    brand_footer(d, 1860, TEAL_SOFT)
    return img


def img_schedule() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "WHO, WHERE, WHEN")
    center_fit(d, 210, "SCHEDULING THAT RUNS ITSELF", F_SERIF, 104, INK)
    # week grid
    x0, y0 = 160, 480
    col = 210
    row = 130
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    names = ["Marisol", "Tasha", "Jordan", "Priya", "Lena"]
    hours = [["3.5", "", "4.5", "", "3.5", "", ""],
             ["3", "3", "", "2", "", "", ""],
             ["", "2", "4.5", "2", "4.5", "", ""],
             ["4.5", "", "5", "", "4", "", ""],
             ["", "3", "", "3", "", "1.5", ""]]
    panel(d, [x0 - 20, y0 - 80, x0 + col * 8 + 20, y0 + row * 6 + 40],
          fill=WHITE, outline=TEAL_SOFT)
    d.text((x0 + 10, y0 - 60), "STAFF SCHEDULE", font=F_SANS_B(40),
           fill=TEAL)
    for c, day in enumerate(days):
        cx = x0 + col + c * col
        center_text(d, y0, day, F_SANS_B(38), GREY, cx, cx + col)
    for r, name in enumerate(names):
        ry = y0 + 70 + r * row
        d.text((x0 + 10, ry + 30), name, font=F_SANS_B(38), fill=INK)
        for c in range(7):
            cx = x0 + col + c * col
            val = hours[r][c]
            if val:
                d.rounded_rectangle([cx + 22, ry + 10, cx + col - 22,
                                     ry + row - 24], 18, fill=TEAL_SOFT)
                center_text(d, ry + 36, val + "h", F_SANS_B(38), TEAL,
                            cx, cx + col)
    # strip below
    y = y0 + row * 6 + 90
    items = [("22", "jobs this week"), ("86h", "scheduled"),
             ("0", "unassigned")]
    x = 200
    for big, small in items:
        panel(d, [x, y, x + 520, y + 230], fill=INK)
        center_text(d, y + 34, big, F_SERIF(86), CITRUS, x, x + 520)
        center_text(d, y + 152, small, F_SANS_B(36), TEAL_SOFT, x, x + 520)
        x += 560
    brand_footer(d, 1870)
    return img


def img_how() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 140, "FROM ENQUIRY TO PAID", CITRUS)
    center_text(d, 220, "HOW IT WORKS", F_SERIF(140), WHITE)
    steps = [
        ("1", "QUOTE IT",
         "Open the Quote Calculator, type the property's size\n"
         "and rooms, pick the service. Price, cost and margin\n"
         "build themselves. Print the quote."),
        ("2", "RUN IT",
         "Won the work? Schedule it on Jobs. Break it into\n"
         "checklist steps. Assign the crew. Log hours, supplies\n"
         "and travel as they happen."),
        ("3", "BILL IT",
         "Raise the invoice, take the payment, watch the\n"
         "balance clear. The dashboard shows profit, margin\n"
         "and what needs you today."),
    ]
    y = 480
    for num, title, body in steps:
        panel(d, [180, y, S - 180, y + 380], fill=WHITE)
        d.ellipse([240, y + 70, 240 + 170, y + 240], fill=CITRUS)
        center_text(d, y + 100, num, F_SERIF(96), INK, 240, 410)
        d.text((500, y + 60), title, font=F_SANS_B(58), fill=TEAL)
        for i, line in enumerate(body.split("\n")):
            d.text((500, y + 150 + i * 58), line, font=F_SANS(42),
                   fill=GREY)
        y += 440
    brand_footer(d, 1885, TEAL_SOFT)
    return img


def img_pricing() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "PRICING RULES BUILT IN")
    center_fit(d, 210, "NEVER UNDERQUOTE AGAIN", F_SERIF, 122, INK)
    # formula strip
    panel(d, [160, 460, S - 160, 760], fill=INK)
    parts = [("BASE CLEAN", "size + beds + baths"), ("×", ""),
             ("SERVICE", "standard / deep / move"), ("×", ""),
             ("FREQUENCY", "regular = less per visit")]
    x = 220
    for main, sub in parts:
        if main == "×":
            center_text(d, 560, "×", F_SERIF(80), CITRUS, x, x + 80)
            x += 100
            continue
        center_text(d, 500, main, F_SANS_B(44), WHITE, x, x + 340)
        center_text(d, 575, sub, F_SANS(30), TEAL_SOFT, x, x + 340)
        x += 380
    # cards
    cards = [
        ("MINIMUM CHARGE", "No job leaves for less -\n"
                           "the calculator floors every\n"
                           "quote at your minimum."),
        ("MARGIN FLOOR", "Quotes under your margin\n"
                         "floor get flagged: raise it,\n"
                         "cut hours - or walk away."),
        ("TRUE COST", "Labour at your loaded rate\n"
                      "+ supplies + travel. See the\n"
                      "profit before you commit."),
    ]
    x = 160
    for title, body in cards:
        panel(d, [x, 850, x + 540, 1420], fill=WHITE, outline=TEAL_SOFT)
        d.text((x + 40, 900), title, font=F_SANS_B(42), fill=TEAL)
        for i, line in enumerate(body.split("\n")):
            d.text((x + 40, 990 + i * 62), line, font=F_SANS(34),
                   fill=GREY)
        x += 580
    pill(d, S / 2, 1600, "TARGET MARGIN · MARGIN FLOOR · BREAK-EVEN PRICE",
         F_SANS_B(40), INK, CITRUS_SOFT)
    brand_footer(d, 1870)
    return img


def img_invoices() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "MONEY IN, MONEY OUT", CITRUS)
    center_fit(d, 210, "INVOICES & PAYMENTS, TIED OUT", F_SERIF, 104,
               WHITE)
    # invoice mock
    panel(d, [220, 430, 1180, 1560], fill=WHITE)
    d.text((280, 480), "INVOICE  I-2418", font=F_SANS_B(48), fill=TEAL)
    d.text((280, 560), "Whitfield Family  ·  Due 12 Nov",
           font=F_SANS(38), fill=GREY)
    lines = [("Standard clean - visit", "$158.25"),
             ("Oven deep clean", "$45.00"),
             ("Interior windows × 12", "$96.00")]
    y = 680
    for label, value in lines:
        d.text((280, y), label, font=F_SANS(40), fill=INK)
        vw = tw(d, value, F_SANS_B(40))
        d.text((1110 - vw, y), value, font=F_SANS_B(40), fill=INK)
        d.line([(280, y + 62), (1110, y + 62)], fill=TEAL_SOFT, width=2)
        y += 100
    d.text((280, y + 20), "TOTAL", font=F_SANS_B(46), fill=TEAL)
    vw = tw(d, "$299.25", F_SANS_B(54))
    d.text((1110 - vw, y + 12), "$299.25", font=F_SANS_B(54), fill=INK)
    chip(d, 280, y + 140, "PAID IN FULL", F_SANS_B(40), GOOD, GOOD_SOFT,
         pad_x=30, pad_y=14)
    # side cards
    panel(d, [1240, 430, 1840, 860], fill=CREAM)
    center_text(d, 500, "BALANCE DUE", F_SANS_B(40), GREY, 1240, 1840)
    center_text(d, 570, "$1,840", F_SERIF(110), BAD, 1240, 1840)
    center_text(d, 730, "across 6 open invoices", F_SANS(34), GREY,
                1240, 1840)
    panel(d, [1240, 920, 1840, 1350], fill=CREAM)
    center_text(d, 990, "COLLECTED THIS MONTH", F_SANS_B(36), GREY,
                1240, 1840)
    center_text(d, 1060, "$4,620", F_SERIF(110), GOOD, 1240, 1840)
    center_text(d, 1220, "auto-summed from Payments", F_SANS(34), GREY,
                1240, 1840)
    pill(d, 1540, 1490, "OVERDUE ALERTS ON THE DASHBOARD", F_SANS_B(32),
         INK, CITRUS)
    brand_footer(d, 1870, TEAL_SOFT)
    return img


def img_costing() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "JOB COSTING")
    center_fit(d, 210, "SEE THE TRUE PROFIT PER JOB", F_SERIF, 112, INK)
    panel(d, [240, 460, 1760, 1520], fill=WHITE, outline=TEAL_SOFT)
    d.text((320, 520), "JOB J-2501  ·  Deep clean  ·  Hawthorne Auto",
           font=F_SANS_B(46), fill=TEAL)
    bars = [("REVENUE", 420, 1050, TEAL), ("LABOUR", 268, 670, GREY),
            ("SUPPLIES", 34, 85, GREY), ("TRAVEL", 12, 30, GREY)]
    y = 660
    for label, amount, width, color in bars:
        d.text((320, y + 24), label, font=F_SANS_B(42), fill=GREY)
        d.rounded_rectangle([700, y + 10, 700 + width, y + 110], 22,
                            fill=color)
        d.text((700 + width + 30, y + 24), f"${amount}",
               font=F_SANS_B(46), fill=INK)
        y += 170
    d.line([(320, y + 30), (1680, y + 30)], fill=TEAL_SOFT, width=3)
    d.text((320, y + 80), "PROFIT", font=F_SANS_B(52), fill=GOOD)
    d.text((700, y + 80), "$106  ·  25% margin", font=F_SANS_B(52),
           fill=GOOD)
    pill(d, S / 2, 1680, "LABOUR + SUPPLIES + MILEAGE + EXPENSES, "
                         "AUTOMATICALLY", F_SANS_B(38), INK, CITRUS_SOFT)
    brand_footer(d, 1880)
    return img


def img_whofor() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 140, "BUILT FOR THE CLEANING INDUSTRY", CITRUS)
    center_text(d, 220, "WHO IT'S FOR", F_SERIF(140), WHITE)
    people = [
        ("SOLO CLEANERS", "Price confidently, look\nprofessional, get paid faster"),
        ("CLEANING TEAMS", "Schedule crews, track hours,\ncost every job"),
        ("DOMESTIC SERVICES", "Recurring homes, deep cleans,\nmove-outs, Airbnb turns"),
        ("COMMERCIAL CONTRACTS", "Offices, clinics, cafes,\nHOAs and retail"),
        ("NEW BUSINESSES", "Start with a system, not\na shoebox of spreadsheets"),
        ("ESTABLISHED FIRMS", "Replace 6 messy files with\none wired-together workbook"),
    ]
    bw, bh = 780, 380
    for i, (title, sub) in enumerate(people):
        x = 180 + (i % 2) * (bw + 60)
        y = 480 + (i // 2) * (bh + 50)
        panel(d, [x, y, x + bw, y + bh], fill=WHITE)
        d.text((x + 50, y + 60), title, font=F_SANS_B(50), fill=TEAL)
        for j, line in enumerate(sub.split("\n")):
            d.text((x + 50, y + 170 + j * 62), line, font=F_SANS(42),
                   fill=GREY)
    brand_footer(d, 1885, TEAL_SOFT)
    return img


def img_features() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "EVERYTHING YOU NEED")
    center_text(d, 210, "FEATURE CHECKLIST", F_SERIF(132), INK)
    feats = [
        "Client CRM & property register", "Interactive quote calculator",
        "Lead pipeline & follow-ups", "Job scheduler & calendar",
        "Crew schedule & timesheets", "Job checklists & task ticks",
        "Job costing & margin flags", "Invoices & payment tracking",
        "Supplies stock & reorder alerts", "Equipment service reminders",
        "Mileage & expense logs", "Complaints & recovery tracking",
        "Incidents & safety compliance", "Financial plan vs actuals",
        "KPI reports & leaderboards", "3 printable client documents",
    ]
    x, y = 200, 460
    for i, feat in enumerate(feats):
        d.ellipse([x, y + 8, x + 54, y + 62], fill=TEAL)
        d.line([(x + 14, y + 36), (x + 24, y + 46)], fill=WHITE, width=7)
        d.line([(x + 24, y + 46), (x + 42, y + 22)], fill=WHITE, width=7)
        d.text((x + 84, y + 8), feat, font=F_SANS(42), fill=INK)
        y += 92
        if (i + 1) % 8 == 0:
            x, y = (200, 460) if x == 200 else (x, y)
            if i == 7:
                x, y = 1080, 460
    pill(d, S / 2, 1700, "NO SUBSCRIPTIONS · NO ADD-ONS · ONE-TIME PURCHASE",
         F_SANS_B(42), INK, CITRUS_SOFT)
    brand_footer(d, 1880)
    return img


def img_printables() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "CLIENT-READY DOCUMENTS", CITRUS)
    center_fit(d, 210, "PRINT IT. SEND IT. LOOK PRO.",
               F_SERIF, 112, WHITE)
    docs = [("PRINT QUOTE", "Professional quotes win\nmore work. Valid-until\ndate and deposit built in."),
            ("PRINT INVOICE", "Balance due, payment\ndetails and terms -\nchase-friendly."),
            ("PRINT JOB SHEET", "Site info, access notes,\nchecklist and client\nsign-off box.")]
    x = 160
    for title, body in docs:
        # page mock
        panel(d, [x, 460, x + 540, 1180], fill=WHITE)
        d.rectangle([x + 40, 510, x + 500, 570], fill=TEAL)
        d.rectangle([x + 40, 620, x + 500, 650], fill=TEAL_SOFT)
        d.rectangle([x + 40, 690, x + 500, 720], fill=TEAL_SOFT)
        d.rectangle([x + 40, 750, x + 500, 780], fill=TEAL_SOFT)
        d.rounded_rectangle([x + 40, 840, x + 500, 960], 18,
                            fill=CITRUS_SOFT)
        d.line([(x + 40, 1040), (x + 500, 1040)], fill=GREY_SOFT, width=3)
        d.line([(x + 40, 1100), (x + 340, 1100)], fill=GREY_SOFT, width=3)
        d.text((x, 1230), title, font=F_SANS_B(48), fill=CITRUS)
        for i, line in enumerate(body.split("\n")):
            d.text((x, 1310 + i * 56), line, font=F_SANS(38),
                   fill=TEAL_SOFT)
        x += 620
    pill(d, S / 2, 1730, "TYPE A NUMBER - THE DOCUMENT BUILDS ITSELF",
         F_SANS_B(42), INK, CITRUS)
    brand_footer(d, 1885, TEAL_SOFT)
    return img


def img_excel() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    kicker(d, 130, "COMPATIBILITY")
    center_fit(d, 210, "WORKS WHERE YOU WORK", F_SERIF, 132, INK)
    apps = [("MICROSOFT EXCEL", "2010, 2013, 2016,\n2019, 2021, 365"),
            ("GOOGLE SHEETS", "Upload and use free\nin your browser"),
            ("APPLE NUMBERS", "Open on Mac,\niPad and iPhone")]
    x = 160
    for title, body in apps:
        panel(d, [x, 460, x + 540, 1020], fill=WHITE, outline=TEAL_SOFT)
        d.rounded_rectangle([x + 40, 510, x + 500, 600], 16, fill=TEAL)
        center_text(d, 528, title, F_SANS_B(40), WHITE, x, x + 540)
        for i, line in enumerate(body.split("\n")):
            center_text(d, 680 + i * 60, line, F_SANS(42), GREY, x,
                        x + 540)
        x += 620
    panel(d, [160, 1120, S - 160, 1560], fill=INK)
    center_text(d, 1180, "CLASSIC FORMULAS ONLY", F_SANS_B(52), CITRUS)
    center_text(d, 1280, "No dynamic arrays. No XLOOKUP. No IFS.",
                F_SANS(44), WHITE)
    center_text(d, 1360, "Nothing that breaks on older versions -",
                F_SANS(44), TEAL_SOFT)
    center_text(d, 1430, "open it in Excel 2010 and it just works.",
                F_SANS(44), TEAL_SOFT)
    brand_footer(d, 1870)
    return img


def img_protected() -> Image.Image:
    img = vgrad(TEAL, TEAL_DEEP)
    d = ImageDraw.Draw(img)
    kicker(d, 140, "FORMULA-SAFE BY DESIGN", CITRUS)
    center_fit(d, 220, "PROTECTED, SO NOTHING BREAKS",
               F_SERIF, 104, WHITE)
    # legend panel
    panel(d, [220, 480, 1120, 1120], fill=WHITE)
    d.text((280, 530), "CELL KEY", font=F_SANS_B(44), fill=TEAL)
    d.rounded_rectangle([280, 630, 700, 730], 16, fill=WHITE,
                        outline=CREAM_DARK, width=3)
    d.text((310, 655), "you type here", font=F_SANS(38), fill=INK)
    d.text((280, 780), "white = unlocked input", font=F_SANS(38),
           fill=GREY)
    d.rounded_rectangle([280, 880, 700, 980], 16, fill=TEAL_SOFT)
    d.text((310, 905), "calculated", font=F_SANS(38), fill=INK)
    d.text((280, 1030), "pale teal = locked formula", font=F_SANS(38),
           fill=GREY)
    # password card
    panel(d, [1200, 480, 1840, 1120], fill=INK)
    center_text(d, 560, "SHEET PASSWORD", F_SANS_B(40), TEAL_SOFT,
                1200, 1840)
    center_text(d, 650, "premium", F_SERIF(96), CITRUS, 1200, 1840)
    center_text(d, 820, "Review ▸ Unprotect Sheet", F_SANS(36), WHITE,
                1200, 1840)
    center_text(d, 900, "to customise anything,", F_SANS(36), WHITE,
                1200, 1840)
    center_text(d, 970, "then re-protect.", F_SANS(36), WHITE,
                1200, 1840)
    panel(d, [220, 1220, 1840, 1560], fill=WHITE)
    center_text(d, 1300, "Every formula checked for balanced parentheses "
                         "and quotes", F_SANS_B(44), TEAL)
    center_text(d, 1390, "before shipping - because Excel silently "
                         "deletes broken ones.", F_SANS(42), GREY)
    brand_footer(d, 1870, TEAL_SOFT)
    return img


def img_specs() -> Image.Image:
    img = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(img)
    kicker(d, 160, "THE NUMBERS", CITRUS)
    center_text(d, 240, "WHAT'S IN THE FILE", F_SERIF(132), WHITE)
    stats = [("37", "TABS, ALL WIRED TOGETHER"),
             ("111,000+", "LIVE FORMULAS"),
             ("2", "WORKBOOKS: FILLED + BLANK"),
             ("3", "PRINTABLE CLIENT DOCUMENTS"),
             ("158", "BUILT-IN DROP-DOWNS"),
             ("$0", "MONTHLY FEES, EVER")]
    x, y = 200, 520
    for big, small in stats:
        center_text(d, y, big, F_SERIF(110), CITRUS, x - 100, x + 700)
        d.text((x + 740, y + 40), small, font=F_SANS_B(46), fill=WHITE)
        y += 210
    brand_footer(d, 1885, TEAL_SOFT)
    return img


def img_before_after() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    center_text(d, 160, "BEFORE", F_SANS_B(54), BAD)
    center_text(d, 240, "AFTER", F_SANS_B(54), GOOD, S / 2, S)
    d.line([(S / 2, 160), (S / 2, 1720)], fill=CREAM_DARK, width=4)
    before = ["Quotes in your head", "Jobs in a notebook",
              "Invoices in Word", "Costs... what costs?",
              "Payments in the bank, mostly",
              "'I think we made money?'"]
    after = ["Quote in 3 minutes", "Schedule the whole week",
             "Invoices in 2 clicks", "True cost per job",
             "Every payment matched",
             "Profit on the dashboard"]
    y = 420
    for b, a in zip(before, after):
        d.text((160, y), "✗  " + b, font=F_SANS(46), fill=BAD)
        d.text((1080, y), "✓  " + a, font=F_SANS(46), fill=GOOD)
        y += 180
    panel(d, [400, 1560, 1600, 1760], fill=INK)
    center_text(d, 1615, "ONE FILE. THE WHOLE BUSINESS.", F_SANS_B(56),
                CITRUS)
    brand_footer(d, 1870)
    return img


def img_thankyou() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_linens.jpg"), 60), "bottom")
    d = ImageDraw.Draw(img)
    center_fit(d, 700, "RUN YOUR CLEANING", F_SERIF, 140, WHITE)
    center_fit(d, 870, "BUSINESS LIKE A PRO", F_SERIF, 140, CITRUS)
    center_text(d, 1090, "Thank you for shopping with Novality Store",
                F_SANS_B(52), WHITE)
    center_text(d, 1180, "Questions? Message us anytime - we reply fast.",
                F_SANS(46), TEAL_SOFT)
    pill(d, S / 2, 1400, "INSTANT DOWNLOAD · START TODAY", F_SANS_B(46),
         INK, CITRUS)
    brand_footer(d, 1870, WHITE)
    return img


IMAGES = [
    ("01-cover.jpg", img_cover),
    ("02-what-you-get.jpg", img_what_you_get),
    ("03-whats-inside.jpg", img_tabs),
    ("04-quote-calculator.jpg", img_quote),
    ("05-dashboard.jpg", img_dashboard),
    ("06-scheduler.jpg", img_schedule),
    ("07-how-it-works.jpg", img_how),
    ("08-pricing-rules.jpg", img_pricing),
    ("09-invoices-payments.jpg", img_invoices),
    ("10-job-costing.jpg", img_costing),
    ("11-who-its-for.jpg", img_whofor),
    ("12-feature-checklist.jpg", img_features),
    ("13-printables.jpg", img_printables),
    ("14-works-in-excel.jpg", img_excel),
    ("15-protected.jpg", img_protected),
    ("16-specs.jpg", img_specs),
    ("17-before-after.jpg", img_before_after),
    ("18-thank-you.jpg", img_thankyou),
]


# ================================================================ listing copy
TITLES = """\
Cleaning Business Spreadsheet, Cleaning Service CRM, Job Scheduler, Quote Calculator, Employee Planner, Invoices and Profit Dashboard
Cleaning Business CRM Spreadsheet, Quote Calculator, Cleaning Service Scheduler, Invoice Tracker, Excel and Google Sheets
Cleaning Service Business Planner, Job Scheduler, Quote Calculator, Employee Timesheets, Invoices, Expenses and Reports
Cleaning Company Spreadsheet, CRM and Pricing Calculator, Job Scheduler, Invoice Tracker, Expense Dashboard, Excel Template
Cleaning Business Management Spreadsheet, Quote and Invoice Templates, Crew Scheduler, Job Costing, Profit Dashboard
"""

TAGS = """\
cleaning business
cleaning service
cleaning spreadsheet
cleaning scheduler
quote calculator
invoice template
cleaning CRM
house cleaning
janitorial
small business
excel spreadsheet
google sheets
instant download
"""

BULLETS = """\
• RUN THE WHOLE BUSINESS IN ONE FILE — 37 wired-together tabs: client CRM, quote calculator, job scheduler, crews and timesheets, job costing, invoicing, payments, stock, expenses, mileage, retention, safety and a live profit dashboard.

• PRICE ANY JOB IN 3 MINUTES — the built-in quote calculator turns property size, bedrooms, bathrooms, condition and frequency into a fair price with cost and margin shown before you commit. Minimum-charge and margin-floor guards stop underquoting.

• EVERYTHING COUNTS ITSELF — 111,000+ formulas do the maths: invoice balances, job profits, monthly revenue, top clients, expenses by category, staff hours, reorder alerts and follow-up reminders. Excel 2010 through 365, Google Sheets and Numbers.

• LOOK PROFESSIONAL, GET PAID FASTER — three printable client documents (Quote, Invoice, Job Sheet) build themselves from a record number you type in. Terms, deposits, balances and sign-off boxes included.

• INSTANT DOWNLOAD, TWO VERSIONS — a filled example (a real cleaning company with jobs and invoices already inside) plus a clean blank workbook. Formula-safe protection: white cells are yours, pale teal cells calculate. Password: premium. One-time purchase, no subscription.
"""

HOW_TO_USE = """\
HOW TO USE THE CLEANING BUSINESS CRM & PRICING CALCULATOR
=========================================================

1. Open your workbook
   - Excel 2010 or newer: double-click the file.
   - Google Sheets: File > Upload, then open.
   - Apple Numbers: open directly on Mac, iPad or iPhone.
   - Choose the FILLED file to explore, the BLANK file to start clean.

2. Start on 'Start Here'
   It shows the order to set things up and what every tab does.

3. Set up 'Settings' (10 minutes)
   Business name and contact details, currency, area units, hourly
   rate, minimum charge, tax rate, payment terms and targets. Every
   other tab reads these cells.

4. Build your price list on 'Services'
   Your services, what each includes, how each is priced (hour,
   visit, room, item).

5. Add your world
   Clients on 'Clients', addresses and sizes on 'Properties',
   the team on 'Employees'.

6. Quote work
   Open 'Quote Calculator', type the property's size, bedrooms,
   bathrooms, condition and frequency. The price, your cost and the
   margin build themselves. Record it on 'Quotes' + 'Quote Lines',
   then print it on 'Print Quote' (type the Quote # in the yellow cell).

7. Run the work
   Schedule on 'Jobs', break it into steps on 'Job Tasks', see the
   week on 'Calendar' and 'Staff Schedule'. Log hours on 'Timesheets',
   supplies on 'Supply Usage', travel on 'Mileage'.

8. Bill and get paid
   'Invoices' + 'Invoice Lines' for the bill, 'Payments' for the
   money in - balances and overdue flags update themselves. Print
   from 'Print Invoice'.

9. Watch the numbers
   'Dashboard' shows today, this month and the alerts that need you.
   'Reports' ranks services, clients and staff. 'Financial Plan'
   compares budget vs actuals month by month.

PROTECTION
----------
Sheets are protected with the password: premium
White cells are unlocked (type here). Pale teal cells are locked
formulas - typing over them is blocked on purpose. To customise:
Review > Unprotect Sheet > premium, make your changes, re-protect.

TIPS
----
- Use one row per record; the formulas cover thousands of rows.
- The drop-downs read from the 'Lists' tab - add values there.
- Print Quote / Print Invoice / Print Job Sheet print to one page
  (print area is pre-set).
- Save a copy of the file before big customisations.

Made by Novality Store. Questions? Message the shop - we reply fast.
"""


def write_copy() -> int:
    COPY_OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "TITLES.txt": TITLES,
        "TAGS.txt": TAGS,
        "BULLET_POINTS.txt": BULLETS,
        "DESCRIPTION.txt": BULLETS + "\n" + HOW_TO_USE,
        "HOW_TO_USE.txt": HOW_TO_USE,
    }
    for name, text in files.items():
        (COPY_OUT / name).write_text(text, encoding="utf-8")
    return len(files)


def build_images() -> int:
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in IMAGES:
        img = fn()
        path = IMG_OUT / name
        img.save(path, "JPEG", quality=88, optimize=True)
        print(f"  {name}  {img.size[0]}x{img.size[1]}  "
              f"{path.stat().st_size // 1024} KB")
    return len(IMAGES)


def build_kit() -> None:
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)
    for src in (FILLED, BLANK):
        if not src.exists():
            raise SystemExit(f"missing workbook: {src} - build it first")
        shutil.copy2(src, SHEETS_OUT / src.name)

    n_img = build_images()
    n_copy = write_copy()
    print(f"images: {n_img}, copy files: {n_copy}")

    DOWNLOAD.mkdir(exist_ok=True)
    target = DOWNLOAD / "cleaning-business-crm-etsy-kit.zip"
    n = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (IMG_OUT, COPY_OUT, SHEETS_OUT):
            for path in sorted(folder.iterdir()):
                if path.is_file():
                    z.write(path, f"{folder.name}/{path.name}")
                    n += 1
    print(f"{target.name}: {n} files "
          f"({target.stat().st_size / 1024 / 1024:.1f} MB)")
    # integrity
    with zipfile.ZipFile(target) as zf:
        bad = zf.testzip()
        names = zf.namelist()
        print(f"integrity: {'OK' if bad is None else bad}, "
              f"{len(names)} entries")


if __name__ == "__main__":
    build_kit()
