"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Handmade Product Pricing & Profit Calculator spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, bullets, description,
                                    how-to-use, attributes, FAQ, keywords
    etsy/kit/spreadsheets/          filled sample + blank template
    download/handmade-pricing-calculator-etsy-kit.zip

Usage:
    python3 tools/make_etsy_kit.py
    python3 tools/make_etsy_kit.py --contact   # also writes QA contact sheets

AI imagery is used only for the four text-free background photos in
etsy/assets/. Every word in the kit is typeset here with PIL/DejaVu, so
nothing in a listing image can arrive garbled.
"""

from __future__ import annotations

import argparse
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

FILLED = ROOT / "output" / "Handmade Product Pricing & Profit Calculator.xlsx"
BLANK = (ROOT / "output" /
         "Handmade Product Pricing & Profit Calculator (Blank).xlsx")

S = 2000                     # canvas size

# ---- brand palette (terracotta / cream / sage, matches the workbook) -------
INK        = (48, 34, 27)        # deep cocoa
TERRA      = (140, 74, 50)       # #8C4A32 - the workbook's own primary
TERRA_MID  = (178, 108, 80)
TERRA_DEEP = (96, 48, 32)
TERRA_SOFT = (244, 231, 222)
CREAM      = (249, 245, 239)
CREAM_DARK = (234, 227, 216)
SAGE       = (112, 128, 100)
SAGE_SOFT  = (228, 233, 221)
GOLD       = (186, 142, 78)
GOLD_SOFT  = (248, 239, 223)
WHITE      = (255, 255, 255)
GREY       = (104, 92, 84)
GREY_SOFT  = (214, 206, 198)
GOOD       = (70, 108, 66)
GOOD_SOFT  = (224, 238, 218)
BAD        = (150, 44, 40)
BAD_SOFT   = (248, 219, 214)

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


def dim(img: Image.Image, alpha: int = 120, color=(40, 26, 20)) -> Image.Image:
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
    dark = Image.new("RGB", img.size, (38, 25, 19))
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


def kicker(draw, y, s, color=GOLD):
    center_text(draw, y, s, F_SANS_B(42), color)


def tick(draw, x, y, size=34, color=GOOD):
    draw.ellipse([x, y, x + size, y + size], fill=color)
    draw.line([(x + size * 0.28, y + size * 0.52),
               (x + size * 0.44, y + size * 0.68),
               (x + size * 0.74, y + size * 0.32)],
              fill=WHITE, width=int(size * 0.14))


def head(draw, title: str, sub: str = "") -> None:
    """Standard inner-page heading on a cream canvas."""
    draw.rectangle([0, 0, S, 250], fill=TERRA)
    center_fit(draw, 78, title, F_SERIF, 96, WHITE)
    if sub:
        center_fit(draw, 178, sub, F_SANS, 44, TERRA_SOFT)
    draw.rectangle([0, 250, S, 258], fill=GOLD)


# ============================================================== the 18 images
def img_cover() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_craft_table.jpg"), 78), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 250, "INSTANT DOWNLOAD", F_SANS_B(44), INK, GOLD)
    center_fit(d, 380, "HANDMADE PRODUCT", F_SERIF, 168, WHITE)
    center_fit(d, 570, "PRICING & PROFIT", F_SERIF, 168, WHITE)
    center_fit(d, 760, "CALCULATOR", F_SERIF, 168, GOLD)
    center_text(d, 1010, "40 tabs  ·  100,000+ formulas  ·  Excel 2010-365",
                F_SANS_B(54), TERRA_SOFT)
    center_text(d, 1100, "Materials · Labour · Packaging · Postage · Fees",
                F_SANS(48), TERRA_SOFT)
    stats = [("40", "TABS"), ("100K+", "FORMULAS"), ("6", "CRAFT TABS"),
             ("2", "VERSIONS")]
    bw = 380
    x = S / 2 - (len(stats) * bw + (len(stats) - 1) * 30) / 2
    for big, small in stats:
        panel(d, [x, 1300, x + bw, 1530], fill=WHITE)
        center_text(d, 1340, big, F_SERIF(84), TERRA, x, x + bw)
        center_text(d, 1460, small, F_SANS_B(34), GREY, x, x + bw)
        x += bw + 30
    brand_footer(d, 1870, WHITE)
    return img


def img_what_you_get() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "WHAT YOU GET", "Two workbooks, three print pages, one price model")
    rows = [
        ("FILLED example workbook",
         "40 tabs already wired to a real maker's year: 14 products, "
         "31 materials, 57 sales, 10 trade orders."),
        ("BLANK workbook",
         "The same formulas with every register empty - start clean "
         "without deleting the example first."),
        ("Three printable pages",
         "Print Costing, Print Quote and Print Order - one portrait page "
         "each, on your own letterhead."),
        ("The pricing model",
         "(cost + fixed fees) / (1 - margin - fee rate), rounded the way "
         "you like, on every product and every craft."),
        ("Setup that takes an afternoon",
         "Settings holds your rates, fees and margins once; every other "
         "tab reads them. Start Here walks the order."),
    ]
    y = 330
    for title, body in rows:
        panel(d, [110, y, S - 110, y + 262], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([110, y, 128, y + 262], fill=TERRA)
        d.text((170, y + 34), title, font=F_SANS_B(52), fill=TERRA_DEEP)
        lines = wrap(d, body, F_SANS(40), S - 110 - 170 - 60)
        for i, line in enumerate(lines[:3]):
            d.text((170, y + 112 + i * 50), line, font=F_SANS(40), fill=GREY)
        y += 292
    brand_footer(d)
    return img


def img_tabs() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "40 TABS, ONE SYSTEM", "Everything below is live - nothing typed "
                                  "by hand")
    groups = [
        ("SET UP", "Start Here · Settings · Lists · Help"),
        ("WHAT YOU SELL", "Products · Variations · Bundles · Bundle Lines · "
                          "Development"),
        ("WHAT IT COSTS", "Materials · Material Usage · Labor · Packaging · "
                          "Shipping · Overhead · Waste Log"),
        ("WHAT IT SHOULD COST", "Retail Calculator · Wholesale Calculator · "
                                "Profit & Break-Even · Scenarios"),
        ("MAKING IT", "Crochet · Jewelry · Candles · Clothing · Woodworking · "
                      "Digital · Batches"),
        ("SELLING IT", "Sales · Channels · Promotions · Price History · "
                       "Competitors · Events"),
        ("TRADE", "Wholesale Customers · Wholesale Orders · Print Quote"),
        ("READING IT BACK", "Dashboard · Reports · Print Costing · "
                            "Print Order"),
    ]
    y = 320
    for name, tabs in groups:
        panel(d, [110, y, S - 110, y + 168], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([110, y, 126, y + 168], fill=TERRA_MID)
        d.text((168, y + 22), name, font=F_SANS_B(44), fill=TERRA_DEEP)
        lines = wrap(d, tabs, F_SANS(34), S - 220 - 168)
        for i, line in enumerate(lines[:2]):
            d.text((168, y + 84 + i * 42), line, font=F_SANS(34), fill=GREY)
        y += 188
    brand_footer(d)
    return img


def img_maths() -> Image.Image:
    img = dim(cover(ASSETS / "bg_desk.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "THE ONE FORMULA", F_SANS_B(42), WHITE, TERRA)
    panel(d, [120, 320, S - 120, 700], fill=WHITE)
    center_fit(d, 380, "price  =  (cost + fixed fees)", F_MONO, 92, INK)
    center_fit(d, 500, "/ (1 - margin - fee rate)", F_MONO, 92, TERRA)
    center_text(d, 610, "The division is the trick: the marketplace fee is "
                        "charged on the price,", F_SANS(40), GREY)
    center_text(d, 660, "so adding it on always leaves you short. Dividing "
                        "makes it pay for itself.", F_SANS(40), GREY)
    parts = [
        ("MATERIALS", "your bill of materials, or the craft tab"),
        ("LABOUR", "minutes / 60 x your loaded hourly rate"),
        ("PACKAGING", "matched components, or your default"),
        ("POSTAGE", "the part of shipping you absorb"),
        ("OVERHEAD", "per unit, per hour, or monthly / units"),
    ]
    y = 790
    center_text(d, y - 40, "COST OF ONE ITEM, IN THE OPEN", F_SANS_B(44), GOLD)
    for name, body in parts:
        panel(d, [150, y, S - 150, y + 148], fill=(255, 255, 255, 235))
        d.text((200, y + 20), name, font=F_SANS_B(46), fill=TERRA_DEEP)
        left_fit(d, 640, y + 30, body, F_SANS, 42, GREY, S - 640 - 200)
        y += 168
    center_text(d, 1700, "Every part has its own column on Products - a price "
                        "you can always argue with.", F_SANS(42), WHITE)
    brand_footer(d, 1800, TERRA_SOFT)
    return img


def img_craft() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_yarn.jpg"), 90), "bottom")
    d = ImageDraw.Draw(img)
    center_fit(d, 150, "SIX CRAFT CALCULATORS", F_SERIF, 110, WHITE)
    center_text(d, 290, "Each costs a product from the parts that craft "
                        "actually uses,", F_SANS(44), TERRA_SOFT)
    center_text(d, 350, "then writes the result into your catalog.",
                F_SANS(44), TERRA_SOFT)
    crafts = [
        ("CROCHET", "yarn by weight or yardage, hooks, notions, gauge"),
        ("JEWELRY", "metal by the gram, findings, stones, wire"),
        ("CANDLES", "wax, fragrance load, wicks, vessels, cure days"),
        ("CLOTHING", "fabric by the metre, notions, seams, sizes"),
        ("WOODWORKING", "board feet by species, hardware, finish, joinery"),
        ("DIGITAL", "creation hours amortised across a sales forecast"),
    ]
    y = 470
    for name, body in crafts:
        panel(d, [140, y, S - 140, y + 200], fill=WHITE)
        d.rectangle([140, y, 158, y + 200], fill=TERRA)
        d.text((210, y + 26), name, font=F_SANS_B(50), fill=TERRA_DEEP)
        lines = wrap(d, body, F_SANS(38), S - 280 - 210)
        for i, line in enumerate(lines[:2]):
            d.text((210, y + 100 + i * 46), line, font=F_SANS(38), fill=GREY)
        y += 222
    brand_footer(d, 1870, WHITE)
    return img


def img_costing() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "COSTING THAT ADDS UP", "Nothing is estimated behind your back")
    bars = [
        ("Materials", 0.34, TERRA),
        ("Labour", 0.28, TERRA_MID),
        ("Packaging", 0.10, GOLD),
        ("Postage you absorb", 0.12, SAGE),
        ("Overhead share", 0.16, GREY),
    ]
    y = 360
    for label, frac, colour in bars:
        d.text((140, y), label, font=F_SANS_B(46), fill=INK)
        bx, bw = 760, 1000
        panel(d, [bx, y + 6, bx + bw, y + 62], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rounded_rectangle([bx, y + 6, bx + int(bw * frac), y + 62], 18,
                            fill=colour)
        y += 104
    panel(d, [140, y + 30, S - 140, y + 250], fill=TERRA)
    center_text(d, y + 70, "PLUS THE FEES THAT COME OFF THE TOP",
                F_SANS_B(44), WHITE)
    center_text(d, y + 140, "listing · transaction · processing · offsite "
                            "ads · regulatory · currency", F_SANS(40),
                TERRA_SOFT)
    y += 300
    for line in [
        "Waste and defect rates raise the cost of the pieces that pass.",
        "Your hourly rate is loaded: rate x (1 + payroll burden).",
        "Rounding to .99 / .95 / .50 / whole - your choice on Settings.",
    ]:
        tick(d, 160, y + 8)
        left_fit(d, 230, y + 10, line, F_SANS, 42, GREY, S - 230 - 160)
        y += 84
    brand_footer(d)
    return img


def img_dashboard() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "THE DASHBOARD", "How the month is going, before you dig")
    tiles = [("REVENUE", "$2,418", GOOD), ("PROFIT", "$963", GOOD),
             ("MARGIN", "39.8%", TERRA), ("ORDERS", "31", TERRA),
             ("HOURLY EARNED", "$21.40", SAGE), ("WASTE", "$86", BAD)]
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
    d.text((180, y + 30), "WHAT NEEDS A DECISION", font=F_SANS_B(46),
           fill=TERRA_DEEP)
    for i, line in enumerate([
        "1 product priced below cost after fees",
        "2 margins under your warning level",
        "1 material at its re-order point",
        "Fee schedule not checked in 180 days",
    ]):
        d.ellipse([190, y + 120 + i * 72, 226, y + 156 + i * 72], fill=BAD)
        d.text((260, y + 116 + i * 72), line, font=F_SANS(42), fill=GREY)
    center_text(d, 1800, "Top fives, by-channel and by-craft splits, and the "
                         "month's story - all SUMIFS, nothing typed.",
                F_SANS(40), GREY)
    brand_footer(d, 1868)
    return img


def img_reports() -> Image.Image:
    img = dim(cover(ASSETS / "bg_candles.jpg"), 140)
    d = ImageDraw.Draw(img)
    center_fit(d, 150, "THE YEAR ON ONE PAGE", F_SERIF, 110, WHITE)
    center_text(d, 290, "Reports reads every register and prints landscape, "
                        "one page wide.", F_SANS(44), TERRA_SOFT)
    blocks = [
        "Month by month: orders, units, revenue, cost, fees, profit, margin",
        "By category, by channel and by craft, for the whole year",
        "Top ten products by revenue and by profit",
        "The ten worst margins - the list worth reading",
        "Stock value, re-order lines and what waste cost",
        "Trade: shops, orders, outstanding and overdue",
        "Promotions, events and labour, each with its own block",
    ]
    y = 430
    for line in blocks:
        panel(d, [140, y, S - 140, y + 128], fill=(255, 255, 255))
        tick(d, 180, y + 44, 40, SAGE)
        left_fit(d, 260, y + 40, line, F_SANS, 42, INK, S - 260 - 180)
        y += 150
    panel(d, [260, 1560, S - 260, 1700], fill=WHITE)
    center_text(d, 1600, "It follows TODAY(), so the year never goes stale.",
                F_SANS_B(44), TERRA_DEEP)
    brand_footer(d, 1800, TERRA_SOFT)
    return img


def img_wholesale() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "WHOLESALE WITHOUT TEARS", "Trade prices that still leave a "
                                       "margin")
    rows = [
        ("Pick the shop", "its terms, discount and credit limit arrive from "
                          "Wholesale Customers"),
        ("Trade price", "retail x (1 - discount), rounded like everything "
                        "else"),
        ("Working backwards", "the retail price your trade target asks for, "
                              "and the gap to yours"),
        ("Biggest discount", "the cut that still leaves your wholesale "
                             "margin intact"),
        ("Volume strip", "the same order at 6, 12, 24, 48 and 100 units"),
        ("Aging", "what is outstanding, what is overdue, who has gone "
                  "quiet"),
    ]
    y = 340
    for title, body in rows:
        panel(d, [130, y, S - 130, y + 190], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([130, y, 146, y + 190], fill=SAGE)
        d.text((190, y + 24), title, font=F_SANS_B(46), fill=TERRA_DEEP)
        lines = wrap(d, body, F_SANS(38), S - 250 - 190)
        for i, line in enumerate(lines[:2]):
            d.text((190, y + 96 + i * 46), line, font=F_SANS(38), fill=GREY)
        y += 212
    center_text(d, 1700, "A 40% discount on a thin retail margin is a loss. "
                         "This page says so first.", F_SANS(42), TERRA)
    brand_footer(d)
    return img


def img_scenarios() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "BREAK-EVEN & SCENARIOS", "One product, five margins, side by "
                                      "side")
    cols = [("BUDGET", "15%"), ("FAIR", "25%"), ("STANDARD", "35%"),
            ("PREMIUM", "45%"), ("LUXURY", "55%"), ("TODAY", "-")]
    bw = 245
    gap = 10
    x0 = 450
    d.text((130, 330), "PRICE", font=F_SANS_B(40), fill=GREY)
    d.text((130, 470), "PROFIT", font=F_SANS_B(40), fill=GREY)
    d.text((130, 610), "HOURLY", font=F_SANS_B(40), fill=GREY)
    prices = ["$16.99", "$19.99", "$24.99", "$29.99", "$36.99", "$22.50"]
    profits = ["$1.02", "$2.94", "$5.61", "$8.14", "$11.90", "$4.27"]
    hourly = ["$3.10", "$8.90", "$17.00", "$24.70", "$36.10", "$12.90"]
    for i, (label, _m) in enumerate(cols):
        cx = x0 + i * (bw + gap)
        panel(d, [cx, 320, cx + bw, 720], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([cx, 320, cx + bw, 380],
                    fill=TERRA if i < 5 else SAGE)
        center_text(d, 334, label, F_SANS_B(30), WHITE, cx, cx + bw)
        center_text(d, 402, prices[i], F_SERIF(48), INK, cx, cx + bw)
        center_text(d, 542, profits[i], F_SERIF(48), TERRA, cx, cx + bw)
        centre = hourly[i]
        centre_colour = GOOD if float(centre[1:]) >= 15 else BAD
        center_text(d, 682, centre, F_SERIF(48), centre_colour, cx, cx + bw)
    panel(d, [130, 790, S - 130, 1000], fill=GOLD_SOFT)
    center_text(d, 830, "Sales needed for the same profit", F_SANS_B(46),
                INK)
    center_text(d, 900, "the budget price must sell 5.5x as many to earn what "
                        "the standard price earns", F_SANS(42), GREY)
    bullets = [
        "Break-even: fixed costs / profit an item, six ways",
        "Sensitivity: what a fee rise or a wage rise does to the count",
        "Verdict per column: WORKS, THIN MARGIN, BELOW THE MINIMUM WAGE",
    ]
    y = 1080
    for line in bullets:
        tick(d, 160, y + 6)
        left_fit(d, 230, y + 8, line, F_SANS, 42, GREY, S - 230 - 160)
        y += 80
    brand_footer(d)
    return img


def img_printables() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_desk.jpg"), 100), "bottom")
    d = ImageDraw.Draw(img)
    center_fit(d, 160, "THREE PAGES THAT LEAVE", F_SERIF, 110, WHITE)
    center_fit(d, 300, "THE WORKBOOK", F_SERIF, 110, GOLD)
    pages = [
        ("PRINT COSTING", "one product's full cost build-up, its bill of "
                          "materials, the fees and what the price earns"),
        ("PRINT QUOTE", "a wholesale quote on your letterhead: pick the "
                        "shop, type the lines, totals arrive"),
        ("PRINT ORDER", "a production docket: what to make, how many, the "
                        "materials for that run, steps to sign off"),
    ]
    y = 500
    for name, body in pages:
        panel(d, [170, y, S - 170, y + 300], fill=WHITE)
        d.rectangle([170, y, S - 170, y + 74], fill=TERRA)
        d.text((220, y + 14), name, font=F_SANS_B(44), fill=WHITE)
        lines = wrap(d, body, F_SANS(40), S - 340 - 220)
        for i, line in enumerate(lines[:3]):
            d.text((220, y + 106 + i * 52), line, font=F_SANS(40), fill=GREY)
        y += 330
    center_text(d, 1620, "Each one is laid out for a single portrait page, "
                         "with your shop's details on top.", F_SANS(42),
                TERRA_SOFT)
    brand_footer(d, 1800, WHITE)
    return img


def img_how() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "HOW IT WORKS", "An afternoon to set up, then it runs itself")
    steps = [
        ("1", "SETTINGS", "your shop, your hourly rate, your fee schedule, "
                          "your target margins - once"),
        ("2", "MATERIALS & TIME", "what you stock and what one item uses; "
                                  "minutes from the craft tab or Labor"),
        ("3", "PRODUCTS", "the catalog: cost in five visible parts, the "
                          "suggested price beside yours"),
        ("4", "SALES", "record what sold; Dashboard and Reports tell you "
                       "what it earned"),
    ]
    y = 350
    for num, title, body in steps:
        panel(d, [150, y, S - 150, y + 250], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.ellipse([200, y + 60, 320, y + 180], fill=TERRA)
        center_text(d, y + 82, num, F_SERIF(72), WHITE, 200, 320)
        d.text((370, y + 40), title, font=F_SANS_B(52), fill=TERRA_DEEP)
        lines = wrap(d, body, F_SANS(40), S - 420 - 370)
        for i, line in enumerate(lines[:2]):
            d.text((370, y + 120 + i * 50), line, font=F_SANS(40), fill=GREY)
        y += 280
    center_text(d, 1560, "Drop-downs, hidden rank columns and date logic do "
                         "the rest - no macros, no add-ins.", F_SANS(42),
                TERRA)
    brand_footer(d)
    return img


def img_whofor() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_yarn.jpg"), 95), "bottom")
    d = ImageDraw.Draw(img)
    center_fit(d, 160, "MADE FOR PEOPLE WHO MAKE", F_SERIF, 110, WHITE)
    who = [
        "Crochet and knit makers pricing by the skein and the hour",
        "Candle pourers working out fragrance load and batch cure",
        "Jewellers costing metal by the gram against a moving price",
        "Sewists and pattern makers, paper and digital alike",
        "Woodworkers spreading machine time across a batch",
        "Anyone selling on Etsy, at fairs, or to shops wholesale",
    ]
    y = 360
    for line in who:
        panel(d, [150, y, S - 150, y + 130], fill=WHITE)
        tick(d, 190, y + 45, 40, TERRA)
        left_fit(d, 270, y + 42, line, F_SANS, 42, INK, S - 270 - 190)
        y += 152
    center_text(d, 1420, "If you have ever priced by guessing what someone "
                         "will pay,", F_SANS(46), WHITE)
    center_text(d, 1490, "this is the spreadsheet that ends that.",
                F_SANS(46), GOLD)
    brand_footer(d, 1800, TERRA_SOFT)
    return img


def img_features() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "EVERYTHING IS WIRED", "100,080 formulas, 321 drop-downs, 271 "
                                  "named ranges")
    feats = [
        "No hidden calc tab - top fives use hidden rank columns you can see",
        "Loss, thin-margin and below-minimum-wage flags on every product",
        "Re-order points and waste flags on every material",
        "Fee schedule age warning: fees go stale, the workbook says when",
        "Bundles re-price from their lines, never from a typed number",
        "Batches spread setup and waste over the pieces that pass",
        "Promotions show the margin left before you commit",
        "Events verdict: profit an hour at a fair, before you book it",
        "Price history: what a price change actually did to margin",
        "Competitor gap: where you sit, and by how much",
    ]
    y = 330
    for i, line in enumerate(feats):
        col = i % 2
        x = 120 + col * 900
        row = i // 2
        yy = y + row * 210
        panel(d, [x, yy, x + 870, yy + 190], fill=WHITE, outline=GREY_SOFT,
              width=2)
        tick(d, x + 34, yy + 30, 36, SAGE)
        lines = wrap(d, line, F_SANS(36), 870 - 120)
        for j, l in enumerate(lines[:3]):
            d.text((x + 100, yy + 26 + j * 46), l, font=F_SANS(36), fill=INK)
    brand_footer(d)
    return img


def img_excel() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "OPENS EVERYWHERE", "No macros, no add-ins, no subscription")
    names = ["Excel 2010", "Excel 2013", "Excel 2016", "Excel 2019",
             "Excel 2021", "Excel 365", "Excel for Mac", "Excel on the web",
             "Google Sheets", "LibreOffice Calc", "Apple Numbers"]
    x, y = 150, 360
    for name in names:
        w, h = chip(d, x, y, name, F_SANS_B(40), WHITE, TERRA, pad_x=40,
                    pad_y=24)
        x += w + 26
        if x > S - 380:
            x = 150
            y += h + 26
    y += 150
    panel(d, [150, y, S - 150, y + 330], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((210, y + 40), "WRITTEN THE OLD-FASHIONED WAY", font=F_SANS_B(46),
           fill=TERRA_DEEP)
    for i, line in enumerate([
        "No XLOOKUP, LET, IFS, MINIFS or dynamic arrays",
        "No VBA - nothing a work computer will refuse to open",
        "Every formula a human can click and read",
    ]):
        tick(d, 220, y + 130 + i * 66, 38, GOOD)
        d.text((290, y + 128 + i * 66), line, font=F_SANS(40), fill=GREY)
    center_text(d, 1720, "Your file, your machine or your own cloud folder. "
                         "Nothing is sent anywhere.", F_SANS(42), TERRA)
    brand_footer(d)
    return img


def img_protected() -> Image.Image:
    img = vgrad(TERRA_DEEP, TERRA)
    d = ImageDraw.Draw(img)
    center_fit(d, 170, "PROTECTED, NOT LOCKED OUT", F_SERIF, 104, WHITE)
    center_text(d, 320, "Sheets carry a password so formulas survive; the "
                        "cells you fill never do.", F_SANS(44), TERRA_SOFT)
    panel(d, [170, 440, 990, 800], fill=WHITE)
    d.rectangle([170, 440, 990, 500], fill=TERRA_SOFT)
    d.text((210, 452), "YOU TYPE HERE", font=F_SANS_B(38), fill=INK)
    d.text((210, 540), "White cells: prices, names,", font=F_SANS(40),
           fill=GREY)
    d.text((210, 596), "quantities, dates - unlocked", font=F_SANS(40),
           fill=GREY)
    d.text((210, 680), "and shaded so you can see them.", font=F_SANS(40),
           fill=GREY)
    panel(d, [1010, 440, 1830, 800], fill=CREAM_DARK)
    d.rectangle([1010, 440, 1830, 500], fill=TERRA)
    d.text((1050, 452), "CALCULATES", font=F_SANS_B(38), fill=WHITE)
    d.text((1050, 540), "Pale cells hold formulas.", font=F_SANS(40),
           fill=GREY)
    d.text((1050, 596), "Typing over one is blocked", font=F_SANS(40),
           fill=GREY)
    d.text((1050, 680), "on purpose.", font=F_SANS(40), fill=GREY)
    y = 880
    for line in [
        "Unprotect in two clicks: Review > Unprotect Sheet > the password",
        "Protection is a guard rail, not encryption - it hides nothing",
        "Instant download: the files are in your Etsy account in seconds",
        "One-time purchase. No subscription, no updates to pay for",
    ]:
        tick(d, 200, y + 6, 40, GOLD)
        left_fit(d, 280, y + 8, line, F_SANS, 44, WHITE, S - 280 - 200)
        y += 92
    center_text(d, 1500, "The password travels inside the workbook, on Start "
                         "Here and in HOW TO RUN.", F_SANS(40), TERRA_SOFT)
    brand_footer(d, 1800, TERRA_SOFT)
    return img


def img_specs() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "SPECIFICATIONS", "What is in the download")
    specs = [
        ("Tabs", "40 - registers, calculators, dashboards, print pages"),
        ("Formulas", "100,080, all live; 321 drop-downs; 271 named ranges"),
        ("Versions", "filled example + blank template (.xlsx, no macros)"),
        ("File size", "about 1.7 MB each"),
        ("Rows", "300 products, 800 sales, 250 materials - scale with --rows"),
        ("Currencies", "any symbol: $  £  €  A$  and the code beside it"),
        ("Units", "metric or imperial, grams or ounces, cm or inches"),
        ("Protection", "every sheet, password included in the file"),
        ("Validation", "automated: no broken formulas, no circular refs"),
        ("Support", "message the shop - we answer"),
    ]
    y = 330
    for key, value in specs:
        panel(d, [140, y, S - 140, y + 128], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.text((190, y + 38), key, font=F_SANS_B(44), fill=TERRA_DEEP)
        left_fit(d, 640, y + 44, value, F_SANS, 40, GREY, S - 640 - 190)
        y += 146
    brand_footer(d)
    return img


def img_before_after() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "BEFORE & AFTER", "The same candle, priced two ways")
    panel(d, [130, 340, 990, 1180], fill=BAD_SOFT)
    d.rectangle([130, 340, 990, 430], fill=BAD)
    center_text(d, 362, "GUESSING", F_SANS_B(46), WHITE, 130, 990)
    for i, line in enumerate([
        '"About $18 feels right"',
        "Fee taken off the top: -6.5%",
        "Labour: not counted",
        "Overhead: not counted",
        "What is left: $4.10",
        "An hour of work earns $6.40",
    ]):
        d.text((200, 480 + i * 108), line, font=F_SANS(44), fill=INK)
    panel(d, [1010, 340, 1870, 1180], fill=GOOD_SOFT)
    d.rectangle([1010, 340, 1870, 430], fill=GOOD)
    center_text(d, 362, "THE MODEL", F_SANS_B(46), WHITE, 1010, 1870)
    for i, line in enumerate([
        "Cost built in the open: $9.84",
        "Fees grossed up in the price",
        "Margin 35%, rounded to .99",
        "Price: $24.99",
        "What is left: $6.41",
        "An hour of work earns $21.40",
    ]):
        d.text((1080, 480 + i * 108), line, font=F_SANS(44), fill=INK)
    panel(d, [130, 1240, S - 130, 1560], fill=TERRA)
    center_text(d, 1290, "THE DIFFERENCE IS NOT CONFIDENCE.", F_SANS_B(50),
                WHITE)
    center_text(d, 1370, "It is knowing what an hour of your own hands is "
                         "worth.", F_SANS(44), TERRA_SOFT)
    center_text(d, 1660, "Figures from the example workbook that ships with "
                         "the file.", F_SANS(38), GREY)
    brand_footer(d)
    return img


def img_thankyou() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_craft_table.jpg"), 85), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 300, "INSTANT DOWNLOAD", F_SANS_B(44), INK, GOLD)
    center_fit(d, 430, "PRICE YOUR WORK", F_SERIF, 150, WHITE)
    center_fit(d, 600, "LIKE IT IS WORTH", F_SERIF, 150, WHITE)
    center_fit(d, 770, "SOMETHING", F_SERIF, 150, GOLD)
    center_text(d, 1030, "Because it is. The spreadsheet just does the "
                         "arithmetic.", F_SANS(48), TERRA_SOFT)
    panel(d, [330, 1180, S - 330, 1560], fill=WHITE)
    center_text(d, 1230, "IN YOUR ETSY ACCOUNT IN SECONDS", F_SANS_B(44),
                TERRA_DEEP)
    center_text(d, 1320, "two workbooks · three print pages · HOW TO RUN",
                F_SANS(40), GREY)
    center_text(d, 1390, "questions? message the shop - we reply fast",
                F_SANS(40), GREY)
    brand_footer(d, 1800, WHITE)
    return img


IMAGES = [
    ("01-cover.jpg", img_cover),
    ("02-what-you-get.jpg", img_what_you_get),
    ("03-whats-inside.jpg", img_tabs),
    ("04-the-maths.jpg", img_maths),
    ("05-craft-calculators.jpg", img_craft),
    ("06-costing.jpg", img_costing),
    ("07-dashboard.jpg", img_dashboard),
    ("08-reports.jpg", img_reports),
    ("09-wholesale.jpg", img_wholesale),
    ("10-break-even-scenarios.jpg", img_scenarios),
    ("11-printables.jpg", img_printables),
    ("12-how-it-works.jpg", img_how),
    ("13-who-its-for.jpg", img_whofor),
    ("14-feature-checklist.jpg", img_features),
    ("15-works-in-excel.jpg", img_excel),
    ("16-protected.jpg", img_protected),
    ("17-specs.jpg", img_specs),
    ("18-before-after.jpg", img_before_after),
    ("19-thank-you.jpg", img_thankyou),
]


# ================================================================ listing copy
TITLES = """\
Handmade Pricing Calculator Spreadsheet, Craft Business Planner, Material and Labor Cost Tracker, Profit Margin, Etsy Seller Excel Template
Handmade Product Pricing Spreadsheet, Craft Cost Calculator, Material Cost Tracker, Wholesale Price Calculator, Profit Dashboard, Excel
Craft Business Spreadsheet, Handmade Pricing Calculator, Labor Cost Tracker, Break Even Calculator, Etsy Fees, Profit Margin Excel Template
Handmade Business Planner Spreadsheet, Pricing and Profit Calculator, Material Costing, Craft Fair Tracker, Wholesale Quotes, Excel Sheets
Etsy Seller Pricing Spreadsheet, Handmade Cost Calculator, Yarn and Material Cost Tracker, Profit Margin Dashboard, Excel and Google Sheets
"""

TAGS = """\nhandmade pricing
craft calculator
etsy spreadsheet
pricing calculator
craft business
material cost
labor cost tracker
profit margin
wholesale price
break even
crochet business
candle business
excel spreadsheet
"""

BULLETS = """\
• PRICE EVERYTHING YOU MAKE FROM WHAT IT ACTUALLY COSTS - the model is (cost + fixed fees) / (1 - margin - fee rate), so marketplace fees pay for themselves instead of eating your margin. Cost is built in the open: materials, loaded labour, packaging, absorbed postage and overhead, each in its own column.

• 40 TABS, ONE SYSTEM - catalog, materials and bills of materials, labour, packaging, shipping, overhead, six craft calculators (crochet, jewelry, candles, clothing, woodworking, digital), bundles, batches, sales, promotions, price history, competitors, waste, events, wholesale customers and orders, plus a dashboard and a full year report.

• SIX CRAFT CALCULATORS THAT THINK LIKE THE CRAFT - yarn by the skein or the yard, metal by the gram, wax and fragrance load with batch cure days, fabric by the metre, board feet by species, and digital patterns with creation hours amortised over a sales forecast. Each writes its product straight into the catalog.

• IT TELLS YOU WHEN A PRODUCT IS NOT WORTH MAKING - loss, thin-margin and below-minimum-wage flags on every product; re-order and waste flags on every material; break-even six ways; five target margins side by side on Scenarios; the ten worst margins on Reports. 100,080 live formulas, no hidden calc tab.

• INSTANT DOWNLOAD, TWO VERSIONS, THREE PRINT PAGES - a filled example (a real maker's year already inside) plus a clean blank workbook, and Print Costing, Print Quote and Print Order laid out for one portrait page on your letterhead. Excel 2010-365, Google Sheets, Numbers. No macros, no subscription. Sheets protected, password included.
"""

HOW_TO_USE = """\
HOW TO USE THE HANDMADE PRODUCT PRICING & PROFIT CALCULATOR
===========================================================

1. Open your workbook
   - Excel 2010 or newer: double-click the file.
   - Google Sheets: File > Upload, then open.
   - Apple Numbers: open directly on Mac, iPad or iPhone.
   - FILLED shows a complete example; BLANK starts you clean.

2. Start on 'Start Here'
   The first three steps, the pricing maths in plain words, and what
   every tab is for.

3. Set up 'Settings' (about 15 minutes)
   Shop details, currency, hourly rate and payroll burden, overhead
   method, the fee schedule for your marketplaces, target margins and
   the rounding rule you like. Every other tab reads these cells.

4. List what you stock and what one item uses
   'Materials' for what you buy; 'Material Usage' for each product's
   bill of materials (quantity, unit, scrap %). Or skip both: a craft
   tab builds the cost from the parts that craft uses.

5. Price it
   'Products' shows cost in five parts beside the suggested price and
   your price, with the gap between them. 'Retail Calculator' does one
   product in depth; 'Scenarios' shows five margins at once;
   'Profit & Break-Even' shows how many you must sell.

6. Sell it
   Record sales on 'Sales'. 'Promotions' shows the margin left before
   you commit; 'Price History' shows what a change did; 'Competitors'
   shows where you sit; 'Events' verdicts a fair before you book it.

7. Trade
   'Wholesale Customers' holds shops and terms; 'Wholesale Calculator'
   works the trade price backwards from your target; 'Print Quote'
   prints the quote on your letterhead.

8. Read it back
   'Dashboard' for this month and its warnings; 'Reports' for the year
   month by month, by category, channel and craft, top ten and the ten
   worst margins.

PRINTING
--------
Print Costing, Print Quote and Print Order are pre-set to one portrait
page with your shop's details on top. Reports prints landscape, one
page wide.

PROTECTION
----------
Sheets are protected with the password: premium
White cells are unlocked and yours to type in. Pale cells are locked
formulas. To customise: Review > Unprotect Sheet > premium, change what
you need, re-protect.

TIPS
----
- One row per record; the formulas cover hundreds of rows each.
- Drop-downs read the 'Lists' tab - add your own values there.
- The example is a real maker's year; delete it row by row, or just
  open the BLANK file instead.
- Keep a copy of the file before big customisations.

Made by Novality Store. Questions? Message the shop - we reply fast.
"""

ATTRIBUTES = """\
Type: Digital download - spreadsheet template (.xlsx)
Compatible with: Excel 2010+, Excel 365, Google Sheets, LibreOffice, Numbers
Macros: none
Sheets: 40 tabs, 100,080 formulas, 321 drop-down validations
Versions: filled example + blank template
Language: English
Customisable: currency, units, rates, margins, fees, rounding, row counts
Delivery: instant download, two .xlsx files + HOW TO RUN.txt
Use: pricing, costing, inventory, profit tracking for handmade businesses
"""

FAQ = """\
Q. Will it work in my Excel?
A. Excel 2010 and every version since, on Windows and Mac, plus Excel for
the web, Google Sheets, LibreOffice Calc and Apple Numbers. It is written
without XLOOKUP, LET, IFS or dynamic arrays, so nothing needs a 365
subscription.

Q. Do I have to delete the example?
A. No. The BLANK file is the same workbook with empty registers. Use the
filled one to learn it, the blank one to run your business.

Q. I sell on Etsy - are the fees right?
A. Settings holds the whole fee schedule (listing, transaction, processing,
offsite ads, regulatory, currency) and how many orders the ads bring. Put
your marketplace's current numbers in once; every price follows.

Q. Can it handle wholesale?
A. Yes: customers with their own terms and discounts, a wholesale
calculator that works backwards from your trade margin, order aging and
outstanding balances, and a printable quote.

Q. What if I make in batches?
A. Batches spread setup time, waste and defects over the pieces that pass,
and the cost per unit falls accordingly. Candles pour by the batch with
cure days built in.

Q. Is my data sent anywhere?
A. No. It is one file on your machine or your own cloud folder. There are
no macros, no links out, no telemetry.

Q. What exactly do I get?
A. Two workbooks (filled example + blank), HOW TO RUN.txt, and the three
print pages inside each workbook. Instant download from your Etsy
account.
"""

KEYWORDS = """\nhandmade pricing calculator
craft pricing spreadsheet
etsy pricing template
material cost tracker
labor cost calculator
profit margin spreadsheet
wholesale price calculator
break even calculator
craft business planner
crochet pricing
candle cost calculator
jewelry costing
sewing cost calculator
woodworking pricing
digital pattern pricing
etsy fee calculator
small business spreadsheet
excel template handmade
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


def build_images() -> int:
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in IMAGES:
        img = fn()
        path = IMG_OUT / name
        img.save(path, "JPEG", quality=88, optimize=True)
        print(f"  {name}  {img.size[0]}x{img.size[1]}  "
              f"{path.stat().st_size // 1024} KB")
    return len(IMAGES)


def contact_sheets(tile: int = 1000, per: int = 4) -> int:
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
        out = Path("/tmp") / f"handmade_kit_contact_{n + 1}.png"
        sheet.save(out)
        print(f"  contact sheet {out}")
        n += 1
    return n


def build_kit(contact: bool = False) -> None:
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)
    for src in (FILLED, BLANK):
        if not src.exists():
            raise SystemExit(f"missing workbook: {src} - build it first")
        shutil.copy2(src, SHEETS_OUT / src.name)

    n_img = build_images()
    if contact:
        contact_sheets()
    n_copy = write_copy()
    print(f"images: {n_img}, copy files: {n_copy}")

    DOWNLOAD.mkdir(exist_ok=True)
    target = DOWNLOAD / "handmade-pricing-calculator-etsy-kit.zip"
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
                    help="also write QA contact sheets to /tmp")
    build_kit(contact=ap.parse_args().contact)
