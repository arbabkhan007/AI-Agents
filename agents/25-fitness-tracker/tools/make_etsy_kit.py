"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Fitness & Weight Loss Tracker spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, bullets, description,
                                    how-to-use, attributes, FAQ, keywords
    etsy/kit/spreadsheets/          filled sample + blank template
    download/fitness-weight-loss-tracker-etsy-kit.zip

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

FILLED = ROOT / "output" / "Fitness & Weight Loss Tracker.xlsx"
BLANK = (ROOT / "output" /
         "Fitness & Weight Loss Tracker (Blank).xlsx")

S = 2000                     # canvas size

# ---- brand palette (deep teal / cream / ember, matches the workbook) ------
INK        = (32, 38, 43)        # #20262B
PRIMARY    = (20, 101, 90)       # #14655A - the workbook's own primary
PRIMARY_MID = (62, 137, 125)     # #3E897D
PRIMARY_DEEP = (12, 66, 58)
PRIMARY_SOFT = (221, 237, 233)   # #DDEDE9
ACCENT     = (228, 87, 46)       # #E4572E - ember
ACCENT_SOFT = (251, 227, 218)    # #FBE3DA
CREAM      = (249, 246, 240)
CREAM_DARK = (233, 228, 219)
CALC       = (236, 238, 234)
WHITE      = (255, 255, 255)
GREY       = (98, 106, 104)
GREY_SOFT  = (210, 216, 212)
GOOD       = (20, 101, 90)
GOOD_SOFT  = (221, 237, 233)
BAD        = (168, 60, 48)
BAD_SOFT   = (248, 222, 216)

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
        color=(16, 32, 29)) -> Image.Image:
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
    dark = Image.new("RGB", img.size, (14, 30, 27))
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


# ============================================================== the 18 images
def img_cover() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_gym.jpg"), 70), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 240, "INSTANT DOWNLOAD", F_SANS_B(44), INK, ACCENT_SOFT)
    center_fit(d, 370, "FITNESS & WEIGHT", F_SERIF, 168, WHITE)
    center_fit(d, 560, "LOSS TRACKER", F_SERIF, 168, WHITE)
    center_fit(d, 750, "EXCEL SPREADSHEET", F_SERIF, 120, ACCENT_SOFT)
    center_text(d, 990, "16 tabs  ·  17,700+ formulas  ·  Excel 2010-365",
                F_SANS_B(54), PRIMARY_SOFT)
    center_text(d, 1080, "Workouts · Weight · Macros · Habits · Measurements",
                F_SANS(48), PRIMARY_SOFT)
    stats = [("16", "TABS"), ("17.7K", "FORMULAS"), ("152", "EXERCISES"),
             ("210", "FOODS")]
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
        ("Fitness & Weight Loss Tracker.xlsx",
         "the full tracker with 11 weeks of realistic example data, so "
         "you can see every formula working before you type a thing"),
        ("Fitness & Weight Loss Tracker (Blank).xlsx",
         "the same workbook with empty logs - open this one and start "
         "your own journey on day one"),
        ("HOW TO RUN.txt",
         "one page: where to click first, what to type, what stays "
         "locked, and how to change units or targets"),
    ]
    y = 340
    for name, body in files:
        panel(d, [120, y, S - 120, y + 300], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([120, y, 138, y + 300], fill=PRIMARY_MID)
        d.text((190, y + 34), name, font=F_SANS_B(48), fill=PRIMARY_DEEP)
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
    head(d, "16 TABS, ONE SYSTEM", "Every number below is live - nothing "
                                   "typed by hand")
    groups = [
        ("SET UP", "Start Here · Profile & Goals · Settings & Lists"),
        ("READING IT BACK", "Dashboard · Weekly & Monthly Review · "
                            "Reports & Charts"),
        ("TRAINING", "Workout Planner · Workout Log · Exercise Library · "
                     "Cardio & Activity"),
        ("YOUR BODY", "Weight Tracker · Body Measurements · Habit "
                      "Tracker"),
        ("FUEL & RECOVERY", "Meals & Macros (with a 210-food database) · "
                            "Water & Sleep"),
        ("MILESTONES", "Records & Milestones - non-scale victories, "
                       "lift records, plate maths"),
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
    head(d, "THE DASHBOARD", "How the week is going, before you dig")
    tiles = [("WEIGHT NOW", "74.6 kg", GOOD), ("TOTAL CHANGE", "-3.4 kg",
                                               GOOD),
             ("7-DAY RATE", "-0.31/wk", PRIMARY), ("SESSIONS", "4 of 4",
                                                   PRIMARY),
             ("WATER TODAY", "2.4 L", PRIMARY_MID), ("HABIT STREAK",
                                                     "12 days",
                                                     PRIMARY_MID)]
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
        "Log today's water on tab 12",
        "Sessions left in this week - plan them on tab 4",
        "You have not weighed in for a week - one number, same time of day",
        "Everything is logged - write the week up on tab 14",
    ]):
        d.ellipse([190, y + 120 + i * 72, 226, y + 156 + i * 72],
                  fill=ACCENT)
        left_fit(d, 260, y + 118 + i * 72, line, F_SANS, 40, GREY,
                 S - 260 - 200)
    center_text(d, 1800, "Weight trend, session counts, habit streaks and "
                         "the next best action - all formulas, nothing "
                         "typed.", F_SANS(40), GREY)
    brand_footer(d, 1868)
    return img


def img_workout() -> Image.Image:
    img = dim(cover(ASSETS / "bg_gym.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "TABS 4-6 · TRAINING", F_SANS_B(42), WHITE, PRIMARY)
    panel(d, [110, 300, S - 110, 830], fill=WHITE)
    d.text((170, 330), "WORKOUT LOG - one row per exercise",
           font=F_SANS_B(44), fill=PRIMARY_DEEP)
    mock_table(d, 170, 410, [260, 330, 150, 150, 180, 260, 210],
               ["DATE", "EXERCISE", "SETS", "REPS", "KG", "EST. 1-REP",
                "FLAG"],
               [[("Mon", None), ("Back Squat", None), ("4", None),
                 ("6", None), ("92.5", None), ("112.3", PRIMARY),
                 ("PR!", ACCENT)],
                [("Mon", None), ("Bench Press", None), ("4", None),
                 ("6", None), ("72.5", None), ("88.4", PRIMARY), ("", None)],
                [("Tue", None), ("Pull-Up", None), ("4", None),
                 ("8", None), ("+10", None), ("", None), ("", None)],
                [("Thu", None), ("Romanian DL", None), ("3", None),
                 ("10", None), ("80", None), ("99.1", PRIMARY), ("", None)]],
               row_h=72, head_h=56)
    for i, (t, b) in enumerate([
            ("PROGRESSIVE OVERLOAD", "estimated 1-rep max from every set, "
                                     "auto-compared with your last session"),
            ("PR FLAGS", "a new record lights up the row - no hunting "
                         "through history"),
            ("400 ROWS PER LOG", "plus a planner that lays Push / Pull / "
                                 "Legs across the week for you")]):
        y = 880 + i * 190
        panel(d, [110, y, S - 110, y + 168], fill=WHITE)
        d.text((170, y + 20), t, font=F_SANS_B(44), fill=ACCENT)
        lines = wrap(d, b, F_SANS(38), S - 340)
        for j, line in enumerate(lines[:2]):
            d.text((170, y + 84 + j * 46), line, font=F_SANS(38),
                   fill=GREY)
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_library() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "152 EXERCISES, COACHED", "Muscle, equipment, difficulty and "
                                      "how-to - ready to drop into a plan")
    mock_table(d, 120, 330, [420, 260, 300, 240, 540],
               ["EXERCISE", "MUSCLE", "EQUIPMENT", "PATTERN", "HOW TO"],
               [[("Back Squat", None), ("Quads", None), ("Barbell", None),
                 ("Squat", None), ("Brace, sit between hips & knees", GREY)],
                [("Bench Press", None), ("Chest", None), ("Barbell", None),
                 ("Press", None), ("Shoulders down, bar to mid-chest", GREY)],
                [("Pull-Up", None), ("Lats", None), ("Bodyweight", None),
                 ("Pull", None), ("Dead hang, drive elbows to ribs", GREY)],
                [("Lat Pulldown", None), ("Lats", None), ("Machine", None),
                 ("Pull", None), ("Sub if pull-ups are out of reach", ACCENT)],
                [("Plank", None), ("Core", None), ("Bodyweight", None),
                 ("Carry", None), ("Ribs down, glutes on", GREY)]],
               row_h=88, head_h=60)
    y = 980
    d.text((120, y), "EVERY ROW ALSO CARRIES", font=F_SANS_B(44),
           fill=PRIMARY_DEEP)
    feats = ["two swap-in substitutions when equipment or shoulders say no",
             "unilateral flag so left/right work is counted correctly",
             "difficulty rating from beginner to advanced",
             "secondary muscles, so volume per muscle is honest"]
    y += 80
    for f in feats:
        tick(d, 130, y + 6, 36)
        left_fit(d, 200, y + 4, f, F_SANS, 40, GREY, S - 330)
        y += 78
    panel(d, [120, 1480, S - 120, 1760], fill=PRIMARY_SOFT)
    center_fit(d, 1520, "Drop-downs on the log read this library:",
               F_SANS_B, 44, PRIMARY_DEEP)
    center_fit(d, 1600, "type three letters and pick your lift",
               F_SANS, 44, GREY)
    brand_footer(d, 1830)
    return img


def img_weight() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_scale.jpg"), 60), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 180, "TAB 8 · WEIGHT TRACKER", F_SANS_B(42), WHITE,
         PRIMARY)
    panel(d, [110, 280, S - 110, 900], fill=WHITE)
    d.text((170, 310), "ONE NUMBER, SAME TIME OF DAY", font=F_SANS_B(46),
           fill=PRIMARY_DEEP)
    vals = [78.0, 77.6, 77.9, 77.2, 76.8, 77.0, 76.4, 76.1, 76.3, 75.6,
            75.2, 75.4, 74.9, 74.6]
    bars(d, 200, 420, 1180, 830, vals, PRIMARY_MID)
    d.text((1260, 430), "7-DAY AVERAGE", font=F_SANS_B(38), fill=PRIMARY)
    d.text((1260, 490), "smooths the water-", font=F_SANS(36), fill=GREY)
    d.text((1260, 540), "weight noise so the", font=F_SANS(36), fill=GREY)
    d.text((1260, 590), "trend is the truth", font=F_SANS(36), fill=GREY)
    d.text((1260, 680), "28-DAY AVERAGE", font=F_SANS_B(38), fill=ACCENT)
    d.text((1260, 740), "the slower line", font=F_SANS(36), fill=GREY)
    d.text((1260, 790), "you steer by", font=F_SANS(36), fill=GREY)
    feats = [("KG OR LB", "one setting flips the whole workbook, decimals "
                         "and all"),
             ("MILESTONES", "a flag every 2.5 kg, plus your own "
                            "non-scale victories"),
             ("PROJECTION", "at this rate, your goal weight lands on "
                            "this date")]
    y = 960
    for t, b in feats:
        panel(d, [110, y, S - 110, y + 190], fill=WHITE)
        d.text((170, y + 22), t, font=F_SANS_B(44), fill=ACCENT)
        lines = wrap(d, b, F_SANS(38), S - 340)
        for j, line in enumerate(lines[:2]):
            d.text((170, y + 88 + j * 46), line, font=F_SANS(38),
                   fill=GREY)
        y += 212
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_measure() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "13 MEASUREMENTS", "Because the scale never tells the whole "
                               "story")
    sites = ["Neck", "Shoulders", "Chest", "Arms", "Forearms", "Waist",
             "Hips", "Thighs", "Calves"]
    x, y = 130, 340
    for s in sites:
        w, h = chip(d, x, y, s, F_SANS_B(40), PRIMARY_DEEP, PRIMARY_SOFT)
        x += w + 24
        if x > S - 300:
            x = 130
            y += h + 24
    y += 130
    cards = [("WAIST-TO-HIP", "ratio from two numbers you already typed, "
                             "with the health bands"),
             ("WAIST-TO-HEIGHT", "the half-your-height rule, checked "
                                 "automatically"),
             ("NAVY METHOD", "neck + waist (+ hips) estimate body-fat % "
                             "without calipers")]
    for i, (t, b) in enumerate(cards):
        x0 = 130 + i * 590
        panel(d, [x0, y, x0 + 560, y + 420], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x0, y, x0 + 560, y + 14], fill=PRIMARY_MID)
        center_fit(d, y + 50, t, F_SANS_B, 44, PRIMARY_DEEP, x0, x0 + 560)
        lines = wrap(d, b, F_SANS(36), 460)
        for j, line in enumerate(lines[:4]):
            center_text(d, y + 140 + j * 50, line, F_SANS(36), GREY,
                        x0, x0 + 560)
    y += 470
    mock_table(d, 240, y, [340, 300, 300, 340, 340],
               ["DATE", "WAIST", "HIPS", "WAIST-HIP", "CHANGE"],
               [[("12 Aug", None), ("86.0", None), ("99.0", None),
                 ("0.87", PRIMARY), ("-", GREY)],
                [("12 Sep", None), ("83.5", None), ("98.0", None),
                 ("0.85", PRIMARY), ("-2.5 cm", ACCENT)],
                [("12 Oct", None), ("81.0", None), ("97.0", None),
                 ("0.84", PRIMARY), ("-2.5 cm", ACCENT)]],
               row_h=76, head_h=56)
    center_text(d, y + 350, "Change in cm or in - four custom fields for "
                            "whatever matters to you", F_SANS(42), GREY)
    brand_footer(d, y + 450)
    return img


def img_cardio() -> Image.Image:
    img = dim(cover(ASSETS / "bg_desk.jpg"), 160)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "TAB 7 · CARDIO & ACTIVITY", F_SANS_B(42), WHITE,
         PRIMARY)
    panel(d, [110, 300, S - 110, 800], fill=WHITE)
    mock_table(d, 160, 340, [300, 300, 240, 240, 300, 300],
               ["ACTIVITY", "DISTANCE", "TIME", "PACE", "STEPS",
                "KCAL BURNED"],
               [[("Sat walk", None), ("6.0 km", None), ("62 min", None),
                 ("10:20", PRIMARY), ("8,400", None), ("312", ACCENT)],
                [("Sun run", None), ("8.0 km", None), ("44 min", None),
                 ("5:30", PRIMARY), ("-", None), ("548", ACCENT)],
                [("Tue cycle", None), ("18.0 km", None), ("51 min", None),
                 ("2:50", PRIMARY), ("-", None), ("430", ACCENT)]],
               row_h=84, head_h=58)
    parts = [("MET-BASED CALORIES", "each activity type carries its MET "
                                    "value; burn follows your body weight"),
             ("PACE BOTH WAYS", "per km and per mile, worked out from "
                                "distance and time"),
             ("STEPS & HEART RATE", "optional columns, averaged into "
                                    "your weekly review")]
    y = 860
    for t, b in parts:
        panel(d, [110, y, S - 110, y + 176], fill=WHITE)
        d.text((170, y + 20), t, font=F_SANS_B(44), fill=ACCENT)
        lines = wrap(d, b, F_SANS(38), S - 340)
        for j, line in enumerate(lines[:2]):
            d.text((170, y + 84 + j * 46), line, font=F_SANS(38),
                   fill=GREY)
        y += 198
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_meals() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_food.jpg"), 70), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 180, "TAB 11 · MEALS & MACROS", F_SANS_B(42), WHITE,
         PRIMARY)
    center_fit(d, 280, "A 210-FOOD DATABASE", F_SERIF, 110, WHITE)
    center_fit(d, 410, "BUILT INTO THE SHEET", F_SERIF, 110, ACCENT_SOFT)
    panel(d, [110, 560, S - 110, 1030], fill=WHITE)
    mock_table(d, 160, 600, [520, 240, 240, 240, 240, 200],
               ["FOOD", "KCAL", "PROTEIN", "CARBS", "FAT", "FIBRE"],
               [[("Chicken breast, 100 g", None), ("165", None),
                 ("31", None), ("0", None), ("4", None), ("0", None)],
                [("Quinoa, cooked, 100 g", None), ("120", None),
                 ("4", None), ("21", None), ("2", None), ("3", None)],
                [("Greek yoghurt, 100 g", None), ("59", None),
                 ("10", None), ("4", None), ("0", None), ("0", None)]],
               row_h=84, head_h=58)
    feats = ["pick a food from the drop-down and its macros fill "
             "themselves",
             "or type your own line - home cooking is welcome here",
             "daily totals stack up against your calorie, protein, carb "
             "and fat targets",
             "every estimate is labelled and editable - your kitchen, "
             "your numbers"]
    y = 1090
    for f in feats:
        tick(d, 150, y + 4, 38, ACCENT)
        lines = wrap(d, f, F_SANS(40), S - 330)
        for j, line in enumerate(lines[:2]):
            d.text((220, y + j * 50), line, font=F_SANS(40), fill=WHITE)
        y += 50 * min(len(lines), 2) + 30
    brand_footer(d, 1800, PRIMARY_SOFT)
    return img


def img_habits() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "HABITS, WATER & SLEEP", "The quiet columns where journeys are "
                                     "won")
    panel(d, [120, 330, S - 120, 950], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((180, 360), "HABIT MONTH - tick a day, keep the chain",
           font=F_SANS_B(44), fill=PRIMARY_DEEP)
    habits = ["Steps 8k", "Protein hit", "Sleep 7h", "No snacks"]
    y = 450
    for hname in habits:
        d.text((180, y + 14), hname, font=F_SANS(38), fill=INK)
        x = 560
        for day in range(16):
            on = (day * 7 + len(hname)) % 5 != 0
            if on:
                d.rounded_rectangle([x, y, x + 44, y + 44], 10,
                                    fill=PRIMARY_MID)
            else:
                d.rounded_rectangle([x, y, x + 44, y + 44], 10,
                                    outline=GREY_SOFT, width=2)
            x += 58
        y += 74
    d.text((1560, 450), "STREAK", font=F_SANS_B(38), fill=GREY)
    d.text((1560, 500), "12 days", font=F_SERIF(56), fill=PRIMARY)
    d.text((1560, 600), "BEST", font=F_SANS_B(38), fill=GREY)
    d.text((1560, 650), "19 days", font=F_SERIF(56), fill=PRIMARY)
    tiles = [("WATER", "glasses + bottle ml, against your target"),
             ("SLEEP", "bed & wake times become hours and a quality note"),
             ("MOOD & ENERGY", "1-5 scales that reveal what recovery "
                               "actually needs")]
    x = 130
    for t, b in tiles:
        panel(d, [x, 1010, x + 560, 1430], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x, 1010, x + 560, 1024], fill=ACCENT)
        center_fit(d, 1060, t, F_SANS_B, 44, PRIMARY_DEEP, x, x + 560)
        lines = wrap(d, b, F_SANS(36), 460)
        for j, line in enumerate(lines[:4]):
            center_text(d, 1150 + j * 50, line, F_SANS(36), GREY,
                        x, x + 560)
        x += 590
    center_text(d, 1520, "Miss a day and the streak resets honestly - "
                         "that is the point of a chain.",
                F_SANS(42), GREY)
    brand_footer(d, 1620)
    return img


def img_records() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "RECORDS & MILESTONES", "Proof you are changing, in more than "
                                    "one direction")
    cols = [("NON-SCALE VICTORIES", ["Jeans fit again", " Slept through "
                                     "the night", "Carried the shopping "
                                     "in one trip", "Said no, kindly"],
             ACCENT),
            ("LIFT RECORDS", ["Squat 112.5 kg", "Bench 88.0 kg",
                              "Deadlift 140.0 kg", "Press 52.5 kg"],
             PRIMARY),
            ("PLATE MATHS", ["112.5 = 20+2x(25+10+1.25)", "bar included, "
                             "checked for you", "cardio records with "
                             "dates", "milestone ladder, 2.5 kg a rung"],
             PRIMARY_MID)]
    x = 130
    for title, rows, colour in cols:
        panel(d, [x, 340, x + 560, 1120], fill=WHITE, outline=GREY_SOFT,
              width=2)
        d.rectangle([x, 340, x + 560, 356], fill=colour)
        center_fit(d, 390, title, F_SANS_B, 42, PRIMARY_DEEP, x, x + 560)
        yy = 480
        for r in rows:
            lines = wrap(d, r.strip(), F_SANS(36), 460)
            for j, line in enumerate(lines[:2]):
                center_text(d, yy + j * 46, line, F_SANS(36), GREY,
                            x, x + 560)
            yy += 46 * min(len(lines), 2) + 40
        x += 590
    panel(d, [130, 1200, S - 130, 1560], fill=PRIMARY_SOFT)
    center_fit(d, 1250, "The record book writes itself:", F_SANS_B, 46,
               PRIMARY_DEEP)
    center_fit(d, 1340, "every logged set is compared with history, and "
                        "new bests are filed with the date", F_SANS, 42,
               GREY)
    center_fit(d, 1440, "you just collect the wins", F_SANS, 42, GREY)
    brand_footer(d, 1680)
    return img


def img_reports() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "REVIEW & REPORTS", "Sunday, ten minutes, the whole picture")
    panel(d, [120, 330, 980, 1080], fill=WHITE, outline=GREY_SOFT, width=2)
    d.text((180, 360), "WEEKLY REVIEW", font=F_SANS_B(44),
           fill=PRIMARY_DEEP)
    qs = ["Sessions done vs planned", "Average rate of change",
          "Protein target hit how many days", "Sleep average & mood",
          "What worked - keep it", "What fought you - change it"]
    yy = 450
    for q in qs:
        tick(d, 180, yy + 4, 34)
        lines = wrap(d, q, F_SANS(36), 640)
        for j, line in enumerate(lines[:2]):
            d.text((240, yy + j * 44), line, font=F_SANS(36), fill=GREY)
        yy += 44 * min(len(lines), 2) + 34
    panel(d, [1020, 330, S - 120, 1080], fill=WHITE, outline=GREY_SOFT,
          width=2)
    d.text((1080, 360), "CHARTS & MONTHLY ROLL-UP", font=F_SANS_B(40),
           fill=PRIMARY_DEEP)
    bars(d, 1080, 520, 1500, 760, [3, 4, 4, 5, 4, 4, 5], PRIMARY_MID)
    d.text((1080, 790), "sessions per week", font=F_SANS(34), fill=GREY)
    bars(d, 1560, 520, 1880, 760, [78, 77, 76.5, 76, 75.4, 75, 74.6],
         ACCENT)
    d.text((1560, 790), "weight, 7-day avg", font=F_SANS(34), fill=GREY)
    for i, line in enumerate([
            "volume per muscle group, month by month",
            "cardio minutes and calories, stacked by type",
            "habit completion rates and best streaks",
            "measurements change table, site by site"]):
        d.text((1080, 880 + i * 52), "- " + line, font=F_SANS(34),
               fill=GREY)
    panel(d, [120, 1140, S - 120, 1560], fill=PRIMARY)
    center_fit(d, 1200, "MONTHLY SUMMARY LANDS ON ONE PRINTABLE PAGE",
               F_SANS_B, 52, WHITE)
    center_fit(d, 1320, "weights, averages, sessions, calories, habits "
                        "and the month's own words", F_SANS, 44,
               PRIMARY_SOFT)
    center_fit(d, 1420, "print it, stick it on the fridge, keep going",
               F_SANS, 44, PRIMARY_SOFT)
    brand_footer(d, 1680)
    return img


def img_how() -> Image.Image:
    img = dim(cover(ASSETS / "bg_desk.jpg"), 150)
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 190, "RUNNING IN TEN MINUTES", F_SANS_B(42), WHITE,
         PRIMARY)
    steps = [("1", "OPEN & SET UP", "type your starting weight, height, "
                                    "age and goal on tab 2; pick metric "
                                    "or imperial on tab 16"),
             ("2", "LOG AS YOU GO", "one row per workout, meal, weigh-in "
                                    "or walk; drop-downs and the food "
                                    "database do the typing for you"),
             ("3", "READ THE DASHBOARD", "it tells you the trend, the "
                                         "streaks and the single next "
                                         "best action - then review on "
                                         "Sunday")]
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
    center_text(d, 1620, "HOW TO RUN.txt walks the same three steps with "
                         "screens-free plain words.", F_SANS(42),
                PRIMARY_SOFT)
    brand_footer(d, 1720, PRIMARY_SOFT)
    return img


def img_features() -> Image.Image:
    img = vgrad(CREAM, CREAM_DARK)
    d = ImageDraw.Draw(img)
    head(d, "BUILT TO LAST", "No gimmicks - just a file that keeps working")
    feats = [("METRIC OR IMPERIAL", "one setting converts weights, "
                                   "distances and measurements everywhere"),
             ("EXCEL 2010 AND NEWER", "written without XLOOKUP, IFS, LET "
                                      "or dynamic arrays - no 365 "
                                      "subscription needed"),
             ("NO MACROS, NO ADD-INS", "plain formulas only, so nothing "
                                       "asks permission or phones home"),
             ("FORMULAS LOCKED", "sheets protected with a password; "
                                 "white cells stay yours to type in"),
             ("ROOM TO GROW", "400 workout rows, 400 meal rows, 300 "
                              "cardio rows, 200 weigh-ins - years of "
                              "logging"),
             ("WORKS OFFLINE", "one file on your machine or your own "
                               "cloud folder; Google Sheets and "
                               "LibreOffice open it too")]
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
    img = scrim(dim(cover(ASSETS / "bg_scale.jpg"), 115), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 200, "SAFE TO TYPE IN", F_SANS_B(44), WHITE, PRIMARY)
    center_fit(d, 320, "YOUR CELLS, OUR FORMULAS", F_SERIF, 120, WHITE)
    panel(d, [140, 520, S - 140, 1180], fill=(255, 255, 255, 240))
    rows = [("WHITE CELLS", "unlocked - dates, weights, foods, notes: "
                            "7,362 of them in the sample file"),
            ("PALE CELLS", "locked formulas - 17,754 of them, guarding "
                           "every total and trend"),
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
    head(d, "WHO IT IS FOR", "Any body, any starting line")
    folks = [("STARTING FROM ZERO", "no gym experience needed - the "
                                     "library teaches each lift and "
                                     "offers easier swaps"),
             ("COMING BACK", "after a break, a baby or an injury: the "
                             "record book shows where you were, kindly"),
             ("LOSING FAT", "calorie and protein targets against what "
                            "you actually ate, week after week"),
             ("BUILDING MUSCLE", "progressive overload made visible - "
                                 "every set compared with your last"),
             ("BUSY & HUMAN", "miss a day and nothing breaks; streaks "
                              "reset, averages forgive, the dashboard "
                              "just tells you the next step")]
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
    center_text(d, y + 20, "A tracking tool, not medical advice - check "
                           "big changes with your doctor.",
                F_SANS(38), GREY)
    brand_footer(d, y + 110)
    return img


def img_thankyou() -> Image.Image:
    img = scrim(dim(cover(ASSETS / "bg_desk.jpg"), 90), "bottom")
    d = ImageDraw.Draw(img)
    pill(d, S / 2, 260, "THANK YOU", F_SANS_B(48), INK, ACCENT_SOFT)
    center_fit(d, 400, "YOUR JOURNEY,", F_SERIF, 150, WHITE)
    center_fit(d, 580, "ONE HONEST FILE", F_SERIF, 150, WHITE)
    center_text(d, 830, "No apps to install, no accounts, no streaks "
                        "held hostage in someone", F_SANS(46),
                PRIMARY_SOFT)
    center_text(d, 900, "else's cloud. Just your numbers, working for "
                        "you.", F_SANS(46), PRIMARY_SOFT)
    panel(d, [300, 1060, S - 300, 1560], fill=(255, 255, 255, 235))
    center_fit(d, 1110, "QUESTIONS? MESSAGE THE SHOP", F_SANS_B, 48,
               PRIMARY_DEEP)
    center_fit(d, 1210, "we answer fast, and setup help is always free",
               F_SANS, 42, GREY)
    center_fit(d, 1310, "more Novality spreadsheets in the shop:",
               F_SANS, 40, GREY)
    center_fit(d, 1390, "pricing · cleaning CRM · social planner · "
                        "meal planner", F_SANS_B, 42, PRIMARY)
    brand_footer(d, 1700, WHITE)
    return img


IMAGES = [
    ("01-cover.jpg", img_cover),
    ("02-what-you-get.jpg", img_what_you_get),
    ("03-tabs.jpg", img_tabs),
    ("04-dashboard.jpg", img_dashboard),
    ("05-workout.jpg", img_workout),
    ("06-library.jpg", img_library),
    ("07-weight.jpg", img_weight),
    ("08-measurements.jpg", img_measure),
    ("09-cardio.jpg", img_cardio),
    ("10-meals.jpg", img_meals),
    ("11-habits-water.jpg", img_habits),
    ("12-records.jpg", img_records),
    ("13-review-reports.jpg", img_reports),
    ("14-how.jpg", img_how),
    ("15-features.jpg", img_features),
    ("16-protected.jpg", img_protected),
    ("17-who-for.jpg", img_whofor),
    ("18-thankyou.jpg", img_thankyou),
]


# ============================================================ listing copy
TITLES = """\
Primary (140 chars max):
Fitness Tracker Spreadsheet, Weight Loss Tracker Excel, Workout Log & Macro
Tracker, Gym Progress Planner, Body Measurement & Habit Tracker Template

Alt 1:
Weight Loss Spreadsheet Bundle, Fitness Journal Excel Template, Calorie &
Macro Tracker, Workout Planner, Water Sleep Habit Log, Instant Download

Alt 2:
Gym Tracker Excel Spreadsheet, Fitness Planner Template, Weight Log,
Exercise Library 152 Lifts, Food Database 210 Foods, Progress Dashboard
"""

TAGS = """\
fitness tracker
weight loss tracker
workout log
macro tracker
gym spreadsheet
excel template
calorie tracker
habit tracker
body measurements
meal prep planner
progress tracker
workout planner
fitness journal
"""

BULLETS = """\
WHAT YOU GET
- Fitness & Weight Loss Tracker.xlsx - 16 tabs with 11 weeks of realistic
  example data so you can watch every formula work before you type
- Fitness & Weight Loss Tracker (Blank).xlsx - same workbook, empty logs,
  ready for day one
- HOW TO RUN.txt - one page of plain-English setup

WHAT IT TRACKS
- Workouts: planner lays Push/Pull/Legs across your week; the log holds 400
  rows with sets, reps, weight, RPE and rest; estimated 1-rep-max and PR
  flags appear by themselves; 152-exercise library with how-to notes and
  two substitutions each
- Weight: kg or lb, 7-day and 28-day averages, rate of change, milestone
  flags and a goal-date projection
- Body: 13 measurement sites plus waist-hip ratio, waist-height ratio and
  Navy body-fat estimate
- Cardio & activity: MET-based calorie burn from your body weight, pace per
  km and per mile, steps and heart rate
- Food: 210-food database built into the sheet - pick a food and its
  calories, protein, carbs and fat fill in; daily totals stack against your
  targets; your own recipes welcome
- Habits, water & sleep: monthly tick grid with honest streaks, glasses and
  bottle ml, bed/wake times into hours, mood and energy scales
- Records & milestones: non-scale victories, automatic lift record book,
  plate-maths calculator
- Dashboard, weekly review, monthly roll-up and charts - every number live

WHY IT IS DIFFERENT
- Excel 2010 and newer: no XLOOKUP, IFS, LET or dynamic arrays, so no 365
  subscription is needed; also opens in Google Sheets and LibreOffice
- No macros, no add-ins, no accounts, nothing phones home
- Formulas locked behind the password "premium"; white cells stay unlocked
  for you (7,362 in the sample, 4,217 in the blank)
- Metric or imperial from one setting
- Instant download, yours forever

PERFECT FOR
- Beginners who want one honest place for everything
- Returnees after a break, a baby or an injury
- Fat-loss and muscle-gain journeys alike
- Busy people who miss days and need a system that forgives
"""

HOW_TO_USE = """\
HOW TO USE YOUR FITNESS & WEIGHT LOSS TRACKER
---------------------------------------------

1. DOWNLOAD
After purchase, Etsy emails your download link and it also lives in
You > Purchases and reviews. Unzip the folder.

2. OPEN THE RIGHT FILE
- "Fitness & Weight Loss Tracker.xlsx" has 11 weeks of example data.
  Browse it first - every tab shows what it will do for you.
- "Fitness & Weight Loss Tracker (Blank).xlsx" is the one to live in.

3. SET UP (TEN MINUTES, ONCE)
- Tab 2 Profile & Goals: sex, age, height, starting weight, goal weight
  and goal date. BMR and calorie targets calculate themselves.
- Tab 16 Settings & Lists: metric or imperial, week start day, water and
  macro targets, your training split. Add your own drop-down values here.

4. LOG AS YOU GO
- Tab 5 one row per exercise; pick the lift from the drop-down.
- Tab 8 one weigh-in, same time of day, as often as you like.
- Tab 11 pick foods from the database or type your own line.
- Tabs 7, 9, 10, 12 for cardio, measurements, habits, water and sleep.
White cells accept typing. Pale cells are locked formulas.

5. READ IT BACK
- Tab 3 Dashboard: trend, streaks, sessions and the next best action.
- Tab 14 on Sunday: ten minutes to review the week in plain sentences.
- Tab 15 at month end: charts and a one-page printable summary.

PROTECTION
Sheets are protected with the password: premium
White cells are unlocked and yours to type in. Pale cells are locked
formulas. To customise: Review > Unprotect Sheet > premium, change what
you need, re-protect.

TIPS
- One row per record; the formulas cover hundreds of rows each.
- Drop-downs read the Settings & Lists tab - add your own values there.
- The example is a real 11-week journey; delete it row by row, or just
  open the BLANK file instead.
- Keep a copy of the file before big customisations.

Made by Novality Store. Questions? Message the shop - we reply fast.
"""

ATTRIBUTES = """\
Type: Digital download - spreadsheet template (.xlsx)
Compatible with: Excel 2010+, Excel 365, Google Sheets, LibreOffice, Numbers
Macros: none
Sheets: 16 tabs, 17,754 formulas, drop-down validations on every log
Versions: filled example + blank template
Language: English
Customisable: units (metric/imperial), targets, week start, drop-down lists,
row counts
Included extras: 152-exercise library, 210-food database, plate calculator
Delivery: instant download, two .xlsx files + HOW TO RUN.txt
Use: weight loss, muscle gain, workout logging, macro tracking, habit
tracking, body measurements, progress reviews
"""

FAQ = """\
Q. Will it work in my Excel?
A. Excel 2010 and every version since, on Windows and Mac, plus Excel for
the web, Google Sheets, LibreOffice Calc and Apple Numbers. It is written
without XLOOKUP, LET, IFS or dynamic arrays, so nothing needs a 365
subscription.

Q. Do I have to delete the example data?
A. No. The BLANK file is the same workbook with empty logs. Use the filled
one to learn it, the blank one to run your journey.

Q. I am a complete beginner - is this too much?
A. Start with three tabs: log workouts on 5, weigh in on 8, read the
dashboard on 3. Everything else can wait until you want it; the library
teaches each exercise as you meet it.

Q. Does it count calories for me?
A. Yes. Pick a food from the built-in 210-food database and its calories,
protein, carbs and fat fill the row; the day's totals compare with your
targets. Your own recipes can be typed in with their numbers.

Q. Metric or imperial?
A. Either. One setting on tab 16 converts weights, distances and
measurements across the whole workbook.

Q. Can I break it by typing in the wrong place?
A. Practically no. Formula cells are locked behind the password "premium";
only white input cells accept typing, and drop-downs keep spellings
consistent so the totals always find their rows.

Q. Is my data sent anywhere?
A. No. It is one file on your machine or your own cloud folder. There are
no macros, no links out, no telemetry.

Q. What exactly do I get?
A. Two workbooks (filled example + blank), HOW TO RUN.txt, and the
printable monthly summary page inside the workbook. Instant download from
your Etsy account.
"""

KEYWORDS = """\nfitness tracker spreadsheet
weight loss tracker excel
workout log template
macro tracker spreadsheet
gym progress planner
calorie tracker excel
habit tracker template
body measurement tracker
meal prep spreadsheet
excel fitness journal
progress tracker template
workout planner excel
weight log spreadsheet
gym progress tracker
exercise library spreadsheet
food database spreadsheet
strength training log
fitness dashboard excel
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
        out = Path("/tmp") / f"fitness_kit_contact_{n + 1}.png"
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
    target = DOWNLOAD / "fitness-weight-loss-tracker-etsy-kit.zip"
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
