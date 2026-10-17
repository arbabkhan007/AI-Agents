"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Meal Planner & Grocery List spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, description, how-to-use
    etsy/kit/spreadsheets/          filled sample + blank template
    download/meal-planner-etsy-kit.zip

Usage:
    python tools/make_etsy_kit.py
"""

from __future__ import annotations

import shutil
import textwrap
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

FILLED = ROOT / "output" / "Meal Planner & Grocery List.xlsx"
BLANK = ROOT / "output" / "Meal Planner & Grocery List (Blank).xlsx"

S = 2000                     # canvas size

# ---- brand palette --------------------------------------------------------
INK        = (34, 49, 43)
GREEN_DARK = (28, 66, 56)
GREEN_MID  = (46, 107, 87)
GREEN_SOFT = (122, 164, 138)
SAGE       = (168, 195, 160)
SAGE_SOFT  = (234, 241, 231)
CREAM      = (250, 246, 238)
CREAM_DARK = (238, 230, 215)
AMBER      = (222, 148, 47)
AMBER_SOFT = (250, 235, 208)
WHITE      = (255, 255, 255)
GREY       = (122, 132, 127)
GREY_SOFT  = (214, 220, 214)
RED        = (186, 90, 70)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


F_SERIF   = lambda s: font("DejaVuSerif-Bold.ttf", s)     # noqa: E731
F_SANS_B  = lambda s: font("DejaVuSans-Bold.ttf", s)      # noqa: E731
F_SANS    = lambda s: font("DejaVuSans.ttf", s)           # noqa: E731


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


def dim(img: Image.Image, alpha: int = 120, color=(14, 30, 24)) -> Image.Image:
    overlay = Image.new("RGB", img.size, color)
    return Image.blend(img.convert("RGB"), overlay, alpha / 255)


def scrim(img: Image.Image, side: str = "bottom") -> Image.Image:
    """Soft dark gradient so text stays readable over photos."""
    grad = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(grad)
    for i in range(img.size[1]):
        t = i / img.size[1]
        if side == "bottom":
            a = int(200 * max(0, t - 0.35) / 0.65)
        elif side == "top":
            a = int(200 * max(0, 0.5 - t) / 0.5)
        else:
            a = 110
        d.line([(0, i), (img.size[0], i)], fill=a)
    dark = Image.new("RGB", img.size, (16, 28, 22))
    img.paste(dark, (0, 0), grad)
    return img


def tw(draw: ImageDraw.ImageDraw, s: str, f) -> float:
    return draw.textlength(s, font=f)


def wrap(draw: ImageDraw.ImageDraw, s: str, f, max_w: float):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if tw(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, xy, s, f, fill, max_w, line_h=None, center=False):
    x, y = xy
    line_h = line_h or int(f.size * 1.45)
    for line in wrap(draw, s, f, max_w):
        if center:
            draw.text((x + max_w / 2 - tw(draw, line, f) / 2, y),
                      line, font=f, fill=fill)
        else:
            draw.text((x, y), line, font=f, fill=fill)
        y += line_h
    return y


def pill(draw, xy, label, fg=WHITE, bg=GREEN_MID, pad=(28, 14), size=42,
         outline=None):
    f = F_SANS_B(size)
    x, y = xy
    w = tw(draw, label, f) + pad[0] * 2
    h = f.size + pad[1] * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=bg,
                           outline=outline, width=4 if outline else 0)
    draw.text((x + w / 2, y + h / 2), label, font=f, fill=fg, anchor="mm")
    return w, h


def card(draw, box, fill=WHITE, radius=36, outline=None, width=3, shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        draw.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14],
                               radius=radius, fill=(222, 218, 206))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                           width=width)


def soft_panel(img: Image.Image, box, radius=44, alpha=120,
               color=(16, 28, 22)):
    """Rounded translucent panel behind text, for readability over photos."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle(box, radius=radius, fill=(*color, alpha))
    img.paste(overlay, (0, 0), overlay)


def check_icon(draw, cx, cy, r=26, color=GREEN_MID, width=10):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    draw.line([(cx - r * 0.45, cy + r * 0.05), (cx - r * 0.1, cy + r * 0.45),
               (cx + r * 0.55, cy - r * 0.4)], fill=color, width=width + 2)


def numbered_badge(draw, cx, cy, n, r=54, bg=AMBER, fg=WHITE):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    draw.text((cx, cy), str(n), font=F_SANS_B(int(r * 1.1)), fill=fg,
              anchor="mm")


# ----------------------------------------------------------- spreadsheet UI
def sheet_screen(title, headers, rows, col_w, highlight=None, status_col=None,
                 status_colors=None, size=None, footer=None):
    """A tiny spreadsheet UI: column letters, green header, data rows.
    Column widths are scaled to fit; height follows the content."""
    W = size[0] if size else 1280
    total = sum(col_w)
    scale = (W - 70) / total
    col_w = [w * scale for w in col_w]
    row_h = 62
    H = 86 + 40 + 58 + row_h * len(rows) + (70 if footer else 24)
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    # title band
    d.rectangle([0, 0, W, 86], fill=GREEN_DARK)
    d.text((30, 43), title, font=F_SANS_B(38), fill=WHITE, anchor="lm")
    y0 = 86
    # column letters
    d.rectangle([0, y0, W, y0 + 40], fill=(232, 236, 232))
    x = 70
    for i, (head, w) in enumerate(zip(headers, col_w)):
        letter = chr(ord("A") + i)
        d.text((x + w / 2, y0 + 20), letter, font=F_SANS_B(26), fill=GREY,
               anchor="mm")
        x += w
    y = y0 + 40
    # header row
    d.rectangle([0, y, W, y + 58], fill=GREEN_MID)
    d.rectangle([0, y, 70, y + 58], fill=GREEN_DARK)
    d.text((35, y + 29), "#", font=F_SANS_B(26), fill=WHITE, anchor="mm")
    x = 70
    for head, w in zip(headers, col_w):
        d.text((x + 14, y + 29), head, font=F_SANS_B(27), fill=WHITE,
               anchor="lm")
        x += w
    y += 58
    # data rows
    row_h = 62
    for ri, row in enumerate(rows):
        bg = WHITE if ri % 2 == 0 else (244, 247, 243)
        if highlight is not None and ri == highlight:
            bg = AMBER_SOFT
        d.rectangle([0, y, W, y + row_h], fill=bg)
        d.rectangle([0, y, 70, y + row_h], fill=(232, 236, 232))
        d.text((35, y + row_h / 2), str(ri + 1), font=F_SANS(26), fill=GREY,
               anchor="mm")
        x = 70
        for ci, (cell, w) in enumerate(zip(row, col_w)):
            if status_col is not None and ci == status_col:
                colors = status_colors or {}
                fg, bgc = colors.get(str(cell), (GREEN_MID, SAGE_SOFT))
                chip_w = min(w - 28, 24 + 13 * len(str(cell)))
                d.rounded_rectangle([x + 12, y + 12, x + 12 + chip_w,
                                     y + row_h - 12],
                                    radius=(row_h - 24) / 2, fill=bgc)
                d.text((x + 12 + chip_w / 2, y + row_h / 2), str(cell),
                       font=F_SANS_B(25), fill=fg, anchor="mm")
            else:
                d.text((x + 14, y + row_h / 2), str(cell), font=F_SANS(27),
                       fill=INK, anchor="lm")
            x += w
        y += row_h
    # grid lines
    x = 70
    for w in col_w:
        d.line([(x, y0), (x, y)], fill=GREY_SOFT, width=2)
        x += w
    d.line([(70, y0), (70, y)], fill=GREY_SOFT, width=2)
    d.line([(0, y), (W, y)], fill=GREY_SOFT, width=2)
    if footer:
        d.rectangle([0, y, W, y + 70], fill=CREAM_DARK)
        d.text((30, y + 35), footer, font=F_SANS_B(28), fill=GREEN_DARK,
               anchor="lm")
    return img


def laptop(img: Image.Image, screen: Image.Image, cx: int, top: int,
           width: int = 1400):
    d = ImageDraw.Draw(img)
    sw = width
    sh = int(screen.height * sw / screen.width)
    sc = screen.resize((sw, sh), Image.LANCZOS)
    # bezel
    pad = 22
    d.rounded_rectangle([cx - sw / 2 - pad, top - pad,
                         cx + sw / 2 + pad, top + sh + pad],
                        radius=18, fill=(44, 52, 48))
    img.paste(sc, (int(cx - sw / 2), top))
    # base
    base_h = 46
    d.polygon([(cx - sw / 2 - pad, top + sh + pad),
               (cx + sw / 2 + pad, top + sh + pad),
               (cx + sw / 2 + 90, top + sh + pad + base_h),
               (cx - sw / 2 - 90, top + sh + pad + base_h)],
              fill=(196, 202, 198))
    d.rounded_rectangle([cx - 120, top + sh + pad + 10, cx + 120,
                         top + sh + pad + 22], radius=6, fill=(150, 158, 152))


def phone(img: Image.Image, screen: Image.Image, cx: int, top: int,
          width: int = 520):
    d = ImageDraw.Draw(img)
    sw = width
    sh = int(screen.height * sw / screen.width)
    sc = screen.resize((sw, sh), Image.LANCZOS)
    pad = 20
    d.rounded_rectangle([cx - sw / 2 - pad, top - pad,
                         cx + sw / 2 + pad, top + sh + pad],
                        radius=64, fill=(34, 42, 38))
    img.paste(sc, (int(cx - sw / 2), top))
    d.rounded_rectangle([cx - 90, top - pad + 8, cx + 90, top - pad + 34],
                        radius=13, fill=(34, 42, 38))


def page_mockup(title, subtitle, lines, col_headers=None, size=(560, 760),
                col_widths=None):
    W, H = size
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 12], fill=GREEN_MID)
    d.text((W / 2, 60), title, font=F_SANS_B(34), fill=GREEN_DARK, anchor="mm")
    d.text((W / 2, 108), subtitle, font=F_SANS(24), fill=GREY, anchor="mm")
    d.line([(50, 140), (W - 50, 140)], fill=SAGE, width=4)
    y = 180
    if col_headers:
        x = 50
        widths = col_widths or [110, 220, 110]
        d.rectangle([40, y - 10, W - 40, y + 38], fill=SAGE_SOFT)
        for head, w in zip(col_headers, widths):
            d.text((x, y + 14), head, font=F_SANS_B(21), fill=GREEN_DARK,
                   anchor="lm")
            x += w
        y += 52
        for row in lines:
            if isinstance(row, (list, tuple)):
                x = 50
                for cell, w in zip(row, widths):
                    d.text((x, y), str(cell), font=F_SANS(21), fill=INK,
                           anchor="lm")
                    x += w
            y += 38
    else:
        for line in lines:
            d.text((50, y), line, font=F_SANS(22), fill=INK, anchor="lm")
            y += 36
    return img


# --------------------------------------------------------------- image defs
def make_cover():
    img = vgrad(GREEN_DARK, (18, 46, 38))
    d = ImageDraw.Draw(img)
    for r, a in ((1500, 30), (1150, 26), (850, 22)):
        d.ellipse([S - r, -r // 3, S + r // 2, r], outline=(60, 110, 90),
                  width=a)
    d.text((S / 2, 150), "MEAL PLANNER", font=F_SERIF(150), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 280), "& GROCERY LIST", font=F_SERIF(120), fill=SAGE,
           anchor="mm")
    d.text((S / 2, 395), "36-Tab Excel Spreadsheet  ·  Instant Download",
           font=F_SANS_B(52), fill=CREAM, anchor="mm")

    screen = sheet_screen(
        "MEAL PLAN — week 12",
        ["Day", "Breakfast", "Lunch", "Dinner", "Kcal", "Cost"],
        [["Mon 16", "Porridge & banana", "Pasta salad", "Chicken traybake",
          "1,842", "£6.28"],
         ["Tue 17", "Scrambled eggs", "Tomato soup", "Spag bolognese",
          "1,910", "£7.12"],
         ["Wed 18", "Overnight oats", "Chicken Caesar", "Vegetable curry",
          "1,755", "£5.84"],
         ["Thu 19", "Porridge & banana", "Cheese toastie", "Salmon & rice",
          "1,880", "£8.02"],
         ["Fri 20", "Scrambled eggs", "Omelette", "Pizza night",
          "1,796", "£6.94"],
         ["Sat 21", "Pancakes", "Jacket potato", "Beef chilli",
          "1,934", "£7.48"],
         ["Sun 22", "Yoghurt & berries", "Lentil soup", "Beef stew",
          "1,868", "£7.90"],
         ["Mon 23", "Porridge & banana", "Pasta salad", "Stir fry noodles",
          "1,802", "£6.15"]],
        [150, 330, 260, 300, 130, 130],
        status_col=None, footer="Week total  ·  £47.21 planned  ·  "
        "within budget")
    laptop(img, screen, S // 2, 500, width=1380)

    chips = ["36 TABS", "EXCEL 2010+", "PROTECTED SHEETS", "FILLED + BLANK"]
    x = S / 2 - sum(len(c) * 26 + 90 for c in chips) / 2
    for c in chips:
        w, _ = pill(d, (x, 1560), c, fg=GREEN_DARK, bg=CREAM, size=40)
        x += w + 26
    d.text((S / 2, 1720), "Plan the week  ·  Shop the list  ·  Waste less",
           font=F_SANS(46), fill=SAGE, anchor="mm")
    d.text((S / 2, 1860), "Filled sample + blank template  ·  Instant "
           "digital download", font=F_SANS(38), fill=GREEN_SOFT,
           anchor="mm")
    return img


def make_whats_inside():
    img = vgrad(CREAM, SAGE_SOFT)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 170), "WHAT'S INSIDE YOUR DOWNLOAD", font=F_SERIF(86),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 280), "Everything you need to plan, shop, cook and waste "
           "less", font=F_SANS_B(48), fill=GREEN_MID, anchor="mm")

    items = [
        ("1", "FILLED SAMPLE", "A complete worked example - 38 recipes,\n"
         "107 planned meals, real prices and dates.\nSee exactly how it "
         "works before you type."),
        ("2", "BLANK TEMPLATE", "The same 36-tab workbook with clean\ninput "
         "cells, ready for your own recipes,\nbudget and household."),
        ("3", "HOW-TO GUIDE", "A step-by-step guide: set-up in 45\nminutes, "
         "then a 15-minute weekly\nroutine that runs itself."),
        ("4", "PRINTABLE PAGES", "Print Week for the fridge door, Print\n"
         "Shopping for the store, Print Recipe\nfor the kitchen counter."),
    ]
    cw, ch = 860, 620
    gap = 80
    for i, (n, title, body) in enumerate(items):
        x = 140 + (i % 2) * (cw + gap)
        y = 420 + (i // 2) * (ch + gap)
        card(d, [x, y, x + cw, y + ch], fill=WHITE)
        numbered_badge(d, x + 100, y + 110, n, r=58, bg=GREEN_MID)
        d.text((x + 190, y + 110), title, font=F_SANS_B(56), fill=GREEN_DARK,
               anchor="lm")
        para(d, (x + 70, y + 220), body.replace("\n", " "), F_SANS(42), INK,
             cw - 140, line_h=64)
        pill(d, (x + 70, y + ch - 130), "INCLUDED", fg=GREEN_DARK, bg=SAGE_SOFT,
             size=36)
    d.text((S / 2, 1820), "Instant download  ·  No physical item",
           font=F_SANS_B(44), fill=GREEN_MID, anchor="mm")
    d.text((S / 2, 1910), "Opens in Excel, LibreOffice or Google Sheets",
           font=F_SANS(38), fill=GREEN_MID, anchor="mm")
    return img


def make_tabs():
    img = vgrad(CREAM, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "36 TABS. ONE WORKBOOK.", font=F_SERIF(96),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 258), "From recipe book to budget - every tab is "
           "connected", font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    groups = [
        ("PLAN", GREEN_MID, ["Meal Plan", "Weekly Planner",
                             "Monthly Planner", "Rotation", "Events",
                             "Meal Prep"]),
        ("RECIPES", GREEN_DARK, ["Recipes", "Recipe Ingredients",
                                 "Ingredients", "Recipe Costs",
                                 "Dietary Filters", "Food Safety"]),
        ("SHOP", AMBER, ["Grocery List", "Staples", "Grocery Spending",
                         "Store Prices", "Stores", "Pantry"]),
        ("COOK", (142, 106, 62), ["Leftovers", "Fridge & Freezer",
                                  "Converter", "Print Recipe",
                                  "Print Week", "Print Shopping"]),
        ("TRACK", RED, ["Food Waste", "Nutrition", "Budget", "Goals",
                        "Sustainability", "Reports"]),
        ("START", GREY, ["Start Here", "Dashboard", "Settings", "Household",
                         "Lists", "Help"]),
    ]
    y = 380
    for gi, (name, color, tabs) in enumerate(groups):
        x = 90
        pill(d, (x, y + 26), name, fg=WHITE, bg=color, size=40,
             pad=(34, 16))
        x = 420
        cy = y + 18
        for tab in tabs:
            w = tw(d, tab, F_SANS_B(36)) + 56
            if x + w > 1880:
                x = 420
                cy += 74
            pill(d, (x, cy), tab, fg=INK, bg=WHITE, size=36,
                 outline=GREY_SOFT)
            x += w + 20
        y += 210 if cy > y + 18 else 150
        d.line([(90, y - 22), (1910, y - 22)], fill=CREAM_DARK, width=3)
    d.text((S / 2, y + 90), "Everything talks to everything else",
           font=F_SANS_B(52), fill=GREEN_DARK, anchor="mm")
    para(d, (300, y + 180),
         "Plan a meal and the ingredients flow to the grocery list. "
         "Tick off the shopping and the budget updates. Bin something and "
         "the waste tracker prices it. That is the point.",
         F_SANS(42), INK, 1400, line_h=62, center=True)
    return img


def make_dashboard():
    img = vgrad((22, 52, 42), GREEN_DARK)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 140), "THE DASHBOARD", font=F_SERIF(104), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 250), "Your whole week at a glance", font=F_SANS_B(50),
           fill=SAGE, anchor="mm")

    W, H = 1500, 860
    screen = Image.new("RGB", (W, H), CREAM)
    ds = ImageDraw.Draw(screen)
    ds.rectangle([0, 0, W, 90], fill=GREEN_DARK)
    ds.text((36, 45), "DASHBOARD  —  week 12", font=F_SANS_B(40), fill=WHITE,
            anchor="lm")
    tiles = [("MEALS PLANNED", "21", GREEN_MID),
             ("CALORIES / DAY", "1,842", GREEN_MID),
             ("GROCERY COST", "£47.21", AMBER),
             ("BUDGET LEFT", "£72.79", GREEN_MID),
             ("ITEMS TO BUY", "14", GREEN_MID),
             ("USE IT OR LOSE IT", "3", RED)]
    for i, (label, value, color) in enumerate(tiles):
        x = 40 + (i % 3) * 490
        y = 130 + (i // 3) * 240
        ds.rounded_rectangle([x, y, x + 450, y + 200], radius=24, fill=WHITE,
                             outline=GREY_SOFT, width=3)
        ds.text((x + 225, y + 55), label, font=F_SANS_B(28), fill=GREY,
                anchor="mm")
        ds.text((x + 225, y + 125), value, font=F_SANS_B(64), fill=color,
                anchor="mm")
    ds.rounded_rectangle([40, 620, 1460, 820], radius=24, fill=WHITE,
                         outline=GREY_SOFT, width=3)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    bars = [120, 96, 150, 130, 88, 170, 140]
    for i, (day, bar) in enumerate(zip(days, bars)):
        x = 120 + i * 195
        ds.rounded_rectangle([x, 780 - bar, x + 90, 780], radius=12,
                             fill=SAGE if i % 2 else GREEN_MID)
        ds.text((x + 45, 795), day, font=F_SANS_B(28), fill=INK, anchor="mm")
    laptop(img, screen, S // 2, 380, width=1480)

    labels = ["6 live KPI tiles", "Week grid", "Expiry alerts"]
    xs = [220, 800, 1380]
    for text, x in zip(labels, xs):
        pill(d, (x, 1450), text, fg=GREEN_DARK, bg=CREAM, size=42)
    d.text((S / 2, 1640), "Meals, calories, cost, what is about to expire "
           "and what to cook first", font=F_SANS(40), fill=SAGE,
           anchor="mm")
    d.text((S / 2, 1760), "All calculated - there is nothing to type in",
           font=F_SANS_B(42), fill=CREAM, anchor="mm")
    return img


def make_meal_plan():
    img = vgrad(CREAM, SAGE_SOFT)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "THE MEAL PLAN TAB", font=F_SERIF(96),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 258), "One row per meal - everything else fills itself in",
           font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    screen = sheet_screen(
        "MEAL PLAN",
        ["Date", "Slot", "Recipe", "Serves", "Kcal", "Cost", "Diet"],
        [["16 Mar", "Breakfast", "Porridge with banana", "4", "312", "£0.46",
          "OK"],
         ["16 Mar", "Lunch", "Pasta salad", "4", "428", "£1.12", "OK"],
         ["16 Mar", "Dinner", "Chicken & veg traybake", "4", "624", "£2.54",
          "OK"],
         ["17 Mar", "Dinner", "Spaghetti bolognese", "6", "658", "£1.92",
          "Check"],
         ["18 Mar", "Dinner", "Vegetable curry", "4", "512", "£1.14", "OK"],
         ["19 Mar", "Dinner", "Salmon & rice", "4", "586", "£2.86", "OK"],
         ["20 Mar", "Dinner", "Pizza night", "4", "702", "£2.10", "OK"]],
        [130, 150, 340, 110, 120, 110, 120],
        status_col=6,
        status_colors={"OK": (GREEN_MID, SAGE_SOFT), "Check": (RED, (250, 228,
                                                                     222))},
        footer="Auto nutrition  ·  auto cost  ·  rotation guard  ·  "
        "diet checks")
    img.paste(screen.resize((1400, int(1400 * screen.height / screen.width)),
                            Image.LANCZOS), (300, 340))

    feats = [("NUTRITION", "Calories and macros added up per meal"),
             ("COST", "Price per meal from your ingredient prices"),
             ("ROTATION", "Flags meals coming round too fast"),
             ("DIET CHECK", "Catches allergens before you shop")]
    for i, (t, body) in enumerate(feats):
        x = 120 + i * 460
        card(d, [x, 1300, x + 400, 1700], fill=WHITE)
        d.text((x + 200, 1380), t, font=F_SANS_B(42), fill=GREEN_MID,
               anchor="mm")
        para(d, (x + 40, 1450), body, F_SANS(36), INK,
             320, line_h=52, center=True)
        check_icon(d, x + 200, 1648, r=30, color=GREEN_MID, width=10)
    d.text((S / 2, 1830), "Type a meal - the sheet does the rest.",
           font=F_SANS_B(44), fill=GREEN_DARK, anchor="mm")
    return img


def make_grocery():
    photo = scrim(cover(ASSETS / "bg_shopping.jpg"), side="bottom")
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 150), "A GROCERY LIST THAT", font=F_SERIF(100), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 280), "WRITES ITSELF", font=F_SERIF(100), fill=SAGE,
           anchor="mm")

    screen = Image.new("RGB", (520, 1080), CREAM)
    ds = ImageDraw.Draw(screen)
    ds.rectangle([0, 0, 520, 96], fill=GREEN_DARK)
    ds.text((260, 48), "SHOPPING LIST", font=F_SANS_B(36), fill=WHITE,
            anchor="mm")
    y = 130
    for aisle, items in [
            ("MEAT & FISH", [("Chicken breast", "600 g"), ("Salmon fillet",
                                                           "240 g")]),
            ("VEGETABLES", [("Onion", "12"), ("Broccoli", "2"), ("Spinach",
                                                                 "630 g")]),
            ("DAIRY", [("Milk", "4 L"), ("Eggs", "18")]),
            ("BAKERY", [("Bread rolls", "6")])]:
        ds.text((30, y), aisle, font=F_SANS_B(26), fill=GREEN_MID, anchor="lm")
        y += 44
        for name, qty in items:
            ds.rounded_rectangle([24, y, 496, y + 74], radius=16, fill=WHITE,
                                 outline=GREY_SOFT, width=2)
            ds.rounded_rectangle([40, y + 18, 76, y + 54], radius=8,
                                 outline=GREEN_MID, width=4)
            ds.text((96, y + 37), name, font=F_SANS_B(26), fill=INK,
                    anchor="lm")
            ds.text((480, y + 37), qty, font=F_SANS(26), fill=GREY,
                    anchor="rm")
            y += 86
        y += 14
    phone(photo, screen, 480, 560, width=480)

    soft_panel(photo, [950, 520, 1930, 1300], radius=60, alpha=125)
    bullets = ["Built from your meal plan",
               "Reduced by the pantry",
               "Grouped by aisle, with prices",
               "A running total as you shop"]
    y = 620
    for b in bullets:
        check_icon(d, 1030, y + 24, r=22, color=SAGE, width=8)
        d.text((1090, y), b, font=F_SANS_B(42), fill=WHITE, anchor="lm")
        y += 92
    pill(d, (1030, 1010), "14 items  ·  £38.64 estimated", fg=GREEN_DARK,
         bg=CREAM, size=40)
    d.text((1400, 1190), "Tick things off as you shop", font=F_SANS_B(46),
           fill=WHITE, anchor="mm")
    return photo


def make_pantry():
    img = vgrad(SAGE_SOFT, CREAM)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "PANTRY, FRIDGE & FREEZER", font=F_SERIF(88),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 256), "Know what you have. Cook it before it expires.",
           font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    screen = sheet_screen(
        "PANTRY",
        ["Item", "Qty", "Store", "Use by", "Days left", "Status"],
        [["Chicken breast", "250 g", "Fridge", "18 Mar", "1", "Use soon"],
         ["Greek yoghurt", "300 g", "Fridge", "21 Mar", "4", "Fresh"],
         ["Spinach", "120 g", "Fridge", "19 Mar", "2", "Use soon"],
         ["Frozen peas", "600 g", "Freezer", "12 Jun", "87", "Fresh"],
         ["Tinned tomatoes", "4 can", "Pantry", "2 Aug", "139", "Fresh"],
         ["Banana", "3", "Cupboard", "17 Mar", "0", "Use soon"],
         ["Cheddar cheese", "320 g", "Fridge", "29 Mar", "12", "Fresh"]],
        [300, 120, 160, 160, 160, 200],
        status_col=5,
        status_colors={"Use soon": (RED, (250, 228, 222)),
                       "Fresh": (GREEN_MID, SAGE_SOFT)},
        footer="Expiry dates calculated from each ingredient's shelf life")
    img.paste(screen.resize((1360, int(1360 * screen.height / screen.width)),
                            Image.LANCZOS), (320, 360))

    feats = [("AUTO EXPIRY DATES", "Shelf life looked up from your "
             "ingredient list"),
             ("USE IT OR LOSE IT", "Ranks what to cook first, fridge and "
             "freezer"),
             ("LOW STOCK FLAGS", "Shows what is running out and what to "
             "reorder")]
    for i, (t, body) in enumerate(feats):
        x = 130 + i * 620
        card(d, [x, 1320, x + 560, 1680], fill=WHITE)
        d.text((x + 280, 1400), t, font=F_SANS_B(38), fill=GREEN_MID,
               anchor="mm")
        para(d, (x + 50, 1460), body, F_SANS(34), INK, 460, line_h=48,
             center=True)
    return img


def make_budget():
    img = vgrad(CREAM, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "BUDGET & SPENDING", font=F_SERIF(96),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 258), "Planned versus actual, month by month",
           font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    # bar chart panel
    card(d, [160, 420, 1240, 1240], fill=WHITE)
    d.text((700, 485), "GROCERY SPEND vs BUDGET", font=F_SANS_B(38),
           fill=GREY, anchor="mm")
    months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    actual = [0.52, 0.78, 0.64, 0.88, 0.71, 0.83]
    planned = [0.88, 0.88, 0.88, 0.88, 0.88, 0.88]
    base_y = 1090
    for i, (m, a, p) in enumerate(zip(months, actual, planned)):
        x = 280 + i * 155
        d.rounded_rectangle([x, base_y - 520 * p, x + 52, base_y], radius=10,
                            fill=SAGE)
        d.rounded_rectangle([x + 60, base_y - 520 * a, x + 112, base_y],
                            radius=10, fill=AMBER if a > 0.8 else GREEN_MID)
        d.text((x + 56, base_y + 42), m, font=F_SANS_B(30), fill=INK,
               anchor="mm")
    pill(d, (280, 1180), "budget", fg=GREEN_DARK, bg=SAGE_SOFT, size=28)
    pill(d, (470, 1180), "actual", fg=WHITE, bg=GREEN_MID, size=28)

    # KPI cards on the right
    tiles = [("THIS MONTH", "£312.40", AMBER),
             ("VS BUDGET", "£72.10 left", GREEN_MID),
             ("WASTE COST", "£8.20", RED),
             ("EATING OUT", "£45.00", GREY)]
    for i, (label, value, color) in enumerate(tiles):
        y = 420 + i * 215
        card(d, [1320, y, 1880, y + 180], fill=WHITE)
        d.text((1600, y + 55), label, font=F_SANS_B(32), fill=GREY,
               anchor="mm")
        d.text((1600, y + 122), value, font=F_SANS_B(54), fill=color,
               anchor="mm")

    d.text((S / 2, 1400), "Groceries, eating out and food waste - "
           "tracked against every month", font=F_SANS_B(44), fill=GREEN_DARK,
           anchor="mm")
    feats = ["Waste priced and logged", "Weekly budget checks",
             "Months ranked by spend"]
    size = 38
    while size > 24:
        widths = [tw(d, "✓ " + f, F_SANS_B(size)) + 56 for f in feats]
        if sum(widths) + 60 <= 1760:
            break
        size -= 2
    x = (S - (sum(widths) + 60)) / 2
    for ftext, w in zip(feats, widths):
        pill(d, (x, 1520), "✓ " + ftext, fg=GREEN_DARK, bg=SAGE_SOFT,
             size=size)
        x += w + 30
    return img


def make_nutrition():
    img = vgrad(WHITE, SAGE_SOFT)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "NUTRITION TRACKER", font=F_SERIF(96),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 258), "Calories and macros, measured against your "
           "targets", font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    screen = sheet_screen(
        "NUTRITION — daily log",
        ["Date", "Recipe", "Kcal", "Protein", "Carbs", "Fat", "% target"],
        [["16 Mar", "Porridge with banana", "312", "9 g", "52 g", "7 g",
          "17%"],
         ["16 Mar", "Pasta salad", "428", "14 g", "61 g", "12 g", "23%"],
         ["16 Mar", "Chicken & veg traybake", "624", "48 g", "52 g", "21 g",
          "34%"],
         ["16 Mar", "Fruit salad", "96", "1 g", "22 g", "0 g", "5%"],
         ["17 Mar", "Scrambled eggs on toast", "388", "21 g", "34 g", "16 g",
          "21%"],
         ["17 Mar", "Tomato soup & bread", "412", "12 g", "58 g", "12 g",
          "22%"],
         ["17 Mar", "Spaghetti bolognese", "658", "32 g", "71 g", "22 g",
          "36%"]],
        [130, 360, 110, 130, 120, 110, 140],
        footer="Monthly averages  ·  days on target  ·  sugar & sodium "
        "limits")
    img.paste(screen.resize((1380, int(1380 * screen.height / screen.width)),
                            Image.LANCZOS), (310, 340))

    # progress bars panel
    card(d, [160, 1280, 1840, 1700], fill=WHITE)
    d.text((1000, 1350), "DAILY TARGETS", font=F_SANS_B(38), fill=GREY,
           anchor="mm")
    targets = [("Calories", 0.72), ("Protein", 0.88), ("Fibre", 0.64),
               ("Sugar limit", 0.41)]
    for i, (name, pct) in enumerate(targets):
        y = 1420 + i * 64
        d.text((260, y + 18), name, font=F_SANS_B(32), fill=INK, anchor="lm")
        d.rounded_rectangle([560, y, 1700, y + 36], radius=18,
                            fill=GREY_SOFT)
        color = AMBER if pct < 0.55 else GREEN_MID
        d.rounded_rectangle([560, y, 560 + 1140 * pct, y + 36], radius=18,
                            fill=color)
        d.text((1760, y + 18), f"{int(pct * 100)}%", font=F_SANS_B(32),
               fill=color, anchor="lm")
    return img


def make_batch():
    img = vgrad(CREAM, AMBER_SOFT)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "BATCH COOKING, SORTED", font=F_SERIF(92),
           fill=GREEN_DARK, anchor="mm")
    d.text((S / 2, 258), "Cook once. Eat twice. Lose nothing.",
           font=F_SANS_B(48), fill=GREEN_MID, anchor="mm")

    steps = [
        ("MEAL PREP", "Plan the jobs for\nprep day: what to\ncook, how long,\nin "
         "what order.", GREEN_MID, "Sunday 11am"),
        ("FRIDGE & FREEZER", "Log every batch\nwith its use-by\ndates and "
         "portions.", AMBER, "FF-01 · 4 portions"),
        ("LEFTOVERS", "A ranked queue of\nwhat to eat next -\nmost urgent "
         "first.", RED, "Eat today"),
    ]
    for i, (t, body, color, example) in enumerate(steps):
        x = 130 + i * 620
        card(d, [x, 420, x + 540, 1010], fill=WHITE)
        d.rounded_rectangle([x, 420, x + 540, 560], radius=36, fill=color)
        d.rectangle([x, 510, x + 540, 560], fill=color)
        d.text((x + 270, 490), t, font=F_SANS_B(44), fill=WHITE, anchor="mm")
        numbered_badge(d, x + 270, 655, i + 1, r=52, bg=CREAM, fg=GREEN_DARK)
        para(d, (x + 50, 750), body.replace("\n", " "), F_SANS(38), INK, 440,
             line_h=56, center=True)
        pill(d, (x + 105, 920), example, fg=GREEN_DARK, bg=SAGE_SOFT, size=32)
        if i < 2:
            d.text((x + 575, 715), "→", font=F_SANS_B(90), fill=GREEN_MID,
                   anchor="mm")

    stats = [("USE-BY DATES", "calculated per batch"),
             ("REHEATS LEFT", "tracked per portion"),
             ("QUEUE RANK", "so nothing is forgotten")]
    x = 250
    for t, s in stats:
        card(d, [x, 1150, x + 480, 1410], fill=WHITE)
        d.text((x + 240, 1230), t, font=F_SANS_B(38), fill=GREEN_MID,
               anchor="mm")
        d.text((x + 240, 1320), s, font=F_SANS(32), fill=INK, anchor="mm")
        x += 530
    d.text((S / 2, 1620), "Batch cooking saves money - if the portions "
           "actually get eaten.", font=F_SANS_B(44), fill=GREEN_DARK,
           anchor="mm")
    return img


def make_printables():
    photo = cover(ASSETS / "bg_fridge.jpg")
    photo = scrim(photo, side="top")
    photo = scrim(photo, side="bottom")
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 1650), "PRINT IT. STICK IT. COOK IT.", font=F_SERIF(92),
           fill=WHITE, anchor="mm")
    d.text((S / 2, 1770), "Three print-ready pages, formatted for one page "
           "each", font=F_SANS_B(44), fill=SAGE, anchor="mm")

    pages = [
        page_mockup("WEEKLY MEAL PLAN", "week of 16 March",
                    [["Mon", "Porridge", "Pasta salad", "Chicken traybake"],
                     ["Tue", "Eggs on toast", "Tomato soup", "Spag bol"],
                     ["Wed", "Overnight oats", "Caesar salad", "Veg curry"],
                     ["Thu", "Porridge", "Toastie", "Salmon & rice"],
                     ["Fri", "Pancakes", "Jacket potato", "Pizza night"]],
                    col_headers=["Day", "Breakfast", "Lunch", "Dinner"],
                    col_widths=[75, 135, 135, 115]),
        page_mockup("SHOPPING LIST", "14 items · £38.64",
                    [["Meat", "Chicken breast", "600 g"],
                     ["Meat", "Salmon fillet", "240 g"],
                     ["Veg", "Onion", "12"],
                     ["Veg", "Broccoli", "2"],
                     ["Dairy", "Milk", "4 L"],
                     ["Dairy", "Eggs", "18"],
                     ["Bakery", "Bread rolls", "6"]],
                    col_headers=["Aisle", "Item", "Qty"],
                    col_widths=[110, 230, 110]),
        page_mockup("RECIPE CARD", "Chicken & veg traybake",
                    ["2 chicken breasts, sliced",
                     "3 peppers, chopped",
                     "1 tbsp olive oil",
                     "—",
                     "1. Toss everything in a tray.",
                     "2. Roast 25 min at 200°C.",
                     "3. Rest 5 minutes and serve."]),
    ]
    for i, p in enumerate(pages):
        x = 130 + i * 620
        photo.paste(p.resize((520, int(520 * p.height / p.width)),
                             Image.LANCZOS), (x, 240))
    return photo


def make_how_it_works():
    img = vgrad(CREAM, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "HOW IT WORKS", font=F_SERIF(100), fill=GREEN_DARK,
           anchor="mm")
    d.text((S / 2, 258), "Set up once in 45 minutes. Then 15 minutes a "
           "week.", font=F_SANS_B(46), fill=GREEN_MID, anchor="mm")

    steps = [
        ("SET THE BASICS", "Household, budget, targets and how long food "
         "keeps on the Settings tab."),
        ("ADD YOUR RECIPES", "Start with five favourites. Ingredients and "
         "prices go on their own tabs."),
        ("PLAN THE WEEK", "One row per meal. Nutrition, cost and diet "
         "checks appear as you type."),
        ("SHOP THE LIST", "The grocery list builds itself: aisle by aisle, "
         "reduced by the pantry."),
        ("TRACK & IMPROVE", "Log spending and waste. The Budget and Reports "
         "tabs show the rest."),
    ]
    y = 430
    for i, (t, body) in enumerate(steps):
        card(d, [180, y, 1820, y + 230], fill=WHITE if i % 2 == 0 else
             SAGE_SOFT)
        numbered_badge(d, 320, y + 115, i + 1, r=62, bg=AMBER if i % 2 == 0
                       else GREEN_MID)
        d.text((460, y + 80), t, font=F_SANS_B(50), fill=GREEN_DARK,
               anchor="lm")
        para(d, (460, y + 130), body, F_SANS(38), INK, 1280, line_h=52)
        y += 270

    pill(d, (560, 1830), "Free how-to guide included in your download",
         fg=GREEN_DARK, bg=SAGE_SOFT, size=42)
    return img


def make_two_versions():
    photo = dim(cover(ASSETS / "bg_kitchen.jpg"), 95)
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 170), "TWO WORKBOOKS INCLUDED", font=F_SERIF(94),
           fill=WHITE, anchor="mm")
    d.text((S / 2, 280), "Learn from the sample. Make it yours with the "
           "blank.", font=F_SANS_B(44), fill=SAGE, anchor="mm")

    for i, (title, tag, rows) in enumerate([
            ("FILLED SAMPLE", "38 recipes · 107 planned meals",
             ["Worked example, real prices",
              "Every tab filled with data",
              "See how the formulas work",
              "Explore before you type"]),
            ("BLANK TEMPLATE", "clean input cells · same formulas",
             ["Same 36 tabs, no sample data",
              "Add your own recipes",
              "All calculations ready",
              "Start fresh any time"])]):
        x = 160 + i * 880
        card(d, [x, 420, x + 760, 1320], fill=WHITE)
        d.rounded_rectangle([x, 420, x + 760, 580], radius=36,
                            fill=GREEN_MID if i == 0 else AMBER)
        d.rectangle([x, 530, x + 760, 580],
                    fill=GREEN_MID if i == 0 else AMBER)
        d.text((x + 380, 500), title, font=F_SANS_B(52), fill=WHITE,
               anchor="mm")
        d.text((x + 380, 650), tag, font=F_SANS_B(32), fill=GREY,
               anchor="mm")
        y = 740
        for row in rows:
            check_icon(d, x + 90, y + 26, r=22,
                       color=GREEN_MID if i == 0 else AMBER, width=8)
            d.text((x + 140, y), row, font=F_SANS(36), fill=INK, anchor="lm")
            y += 100
        pill(d, (x + 230, 1180), ".XLSX FILE", fg=GREEN_DARK, bg=SAGE_SOFT,
             size=36)

    soft_panel(photo, [220, 1420, 1780, 1720], radius=50, alpha=135)
    d.text((S / 2, 1510), "Instant download  ·  Yours to keep  ·  "
           "Re-download any time", font=F_SANS_B(46), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 1620), "Opens in Microsoft Excel, LibreOffice Calc and "
           "Google Sheets", font=F_SANS(40), fill=SAGE, anchor="mm")
    return photo


def make_specs():
    img = vgrad(GREEN_DARK, (16, 40, 32))
    d = ImageDraw.Draw(img)
    d.text((S / 2, 160), "THE SPECS", font=F_SERIF(110), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 280), "Built to work in the spreadsheet you already "
           "have", font=F_SANS_B(46), fill=SAGE, anchor="mm")

    specs = [
        ("FORMAT", ".xlsx - Excel 2010 and later"),
        ("ALSO WORKS IN", "LibreOffice Calc, Google Sheets"),
        ("TABS", "36 connected worksheets"),
        ("SECURITY", "Protected sheets - password in the guide"),
        ("FORMULAS", "Classic formulas only - no macros, no add-ins"),
        ("SAMPLE DATA", "38 recipes · 62 ingredients · 107 planned meals"),
        ("PRINTABLES", "Week plan, shopping list, recipe card"),
        ("LANGUAGE", "English · currency set to GBP (easy to change)"),
        ("LICENSE", "Personal use - make copies for your own household"),
        ("DELIVERY", "Instant digital download - no shipping"),
    ]
    y = 420
    for i, (k, v) in enumerate(specs):
        x = 160 + (i % 2) * 900
        yy = y + (i // 2) * 250
        card(d, [x, yy, x + 820, yy + 200], fill=(36, 80, 66))
        d.text((x + 50, yy + 65), k, font=F_SANS_B(34), fill=SAGE,
               anchor="lm")
        para(d, (x + 50, yy + 115), v, F_SANS(34), WHITE, 720, line_h=44)

    d.text((S / 2, 1880), "Instant download after purchase", font=F_SANS_B(48),
           fill=SAGE, anchor="mm")
    return img


def make_perfect_for():
    photo = scrim(dim(cover(ASSETS / "bg_flatlay.jpg"), 110), side="bottom")
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 170), "PERFECT FOR", font=F_SERIF(110), fill=WHITE,
           anchor="mm")

    people = [("FAMILIES", "feeding everyone without\nthe 5pm scramble"),
              ("MEAL PREPPERS", "batch cooking with\nnothing lost at the "
               "back\nof the freezer"),
              ("BUDGET KEEPERS", "seeing where the food\nmoney actually "
               "goes"),
              ("SMALL HOUSEHOLDS", "cooking for one or two,\n"
               "students included,\nwithout the waste")]
    for i, (t, body) in enumerate(people):
        x = 150 + (i % 2) * 900
        y = 420 + (i // 2) * 540
        card(d, [x, y, x + 800, y + 460], fill=WHITE)
        d.text((x + 400, y + 100), t, font=F_SANS_B(44),
               fill=GREEN_DARK, anchor="mm")
        para(d, (x + 70, y + 190), body.replace("\n", " "), F_SANS(38), INK,
             660, line_h=54, center=True)

    d.text((S / 2, 1660), "Whoever you feed - the system is the same",
           font=F_SANS_B(52), fill=WHITE, anchor="mm")
    d.text((S / 2, 1770), "Plan · Shop · Cook · Track · Waste less",
           font=F_SANS_B(44), fill=SAGE, anchor="mm")
    return photo


def make_waste_less():
    img = vgrad(AMBER_SOFT, CREAM)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 300), "WASTE LESS.", font=F_SERIF(150), fill=GREEN_DARK,
           anchor="mm")
    d.text((S / 2, 470), "SPEND LESS.", font=F_SERIF(150), fill=AMBER,
           anchor="mm")
    d.text((S / 2, 640), "EAT BETTER.", font=F_SERIF(150), fill=GREEN_MID,
           anchor="mm")

    feats = [
        ("FOOD WASTE LOG", "Log what you bin, why, and what it cost - "
         "ranked so the expensive mistakes stand out."),
        ("USE-BY ALERTS", "Shelf lives are looked up per ingredient, so "
         "the pantry tells you what to cook first."),
        ("LEFTOVERS QUEUE", "A ranked list of every portion waiting to be "
         "eaten - most urgent at the top."),
    ]
    y = 900
    for t, body in feats:
        card(d, [220, y, 1780, y + 240], fill=WHITE)
        d.text((300, y + 70), t, font=F_SANS_B(46), fill=GREEN_DARK,
               anchor="lm")
        para(d, (300, y + 130), body, F_SANS(36), INK, 1380, line_h=48)
        y += 280
    d.text((S / 2, 1780), "The average household bins hundreds of pounds "
           "of food a year.", font=F_SANS_B(42), fill=GREEN_DARK,
           anchor="mm")
    d.text((S / 2, 1880), "This helps you stop.", font=F_SANS_B(42),
           fill=AMBER, anchor="mm")
    return img


def make_faq():
    img = vgrad(CREAM, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "QUICK ANSWERS", font=F_SERIF(100), fill=GREEN_DARK,
           anchor="mm")

    qa = [
        ("What file do I get?", "Two .xlsx workbooks - one filled sample, "
         "one blank - plus a how-to guide."),
        ("Do I need Microsoft Excel?", "No. It works in Excel 2010+, "
         "LibreOffice Calc and Google Sheets."),
        ("Are there macros?", "No macros and no add-ins - just classic "
         "spreadsheet formulas."),
        ("Can I edit the formulas?", "Yes. Sheets are protected to prevent "
         "accidents; the password is in the guide."),
        ("Is this a physical product?", "No - it is an instant digital "
         "download. Nothing ships."),
        ("Can I use it for my family?", "Yes - personal use. Please do not "
         "resell or redistribute the files."),
    ]
    y = 300
    for i, (q, a) in enumerate(qa):
        card(d, [160, y, 1840, y + 215], fill=WHITE if i % 2 == 0 else
             SAGE_SOFT)
        d.text((240, y + 65), "Q", font=F_SANS_B(52), fill=AMBER, anchor="lm")
        d.text((330, y + 65), q, font=F_SANS_B(46), fill=GREEN_DARK,
               anchor="lm")
        para(d, (330, y + 128), a, F_SANS(38), INK, 1420, line_h=50)
        y += 255
    d.text((S / 2, 1900), "Still stuck? Message us any time - we usually "
           "reply within a day.", font=F_SANS_B(42), fill=GREEN_MID,
           anchor="mm")
    return img


def make_thankyou():
    img = vgrad(GREEN_DARK, (14, 36, 28))
    d = ImageDraw.Draw(img)
    for r in (1400, 1100, 800):
        d.ellipse([-r // 2, S - r // 2, r, S + r], outline=(52, 96, 78),
                  width=24)
    d.text((S / 2, 420), "PLAN THE WEEK.", font=F_SERIF(110), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 570), "SHOP THE LIST.", font=F_SERIF(110), fill=SAGE,
           anchor="mm")
    d.text((S / 2, 720), "WASTE LESS.", font=F_SERIF(110), fill=AMBER,
           anchor="mm")
    d.line([(700, 880), (1300, 880)], fill=SAGE, width=5)
    d.text((S / 2, 1020), "Thank you for shopping with us", font=F_SANS_B(58),
           fill=CREAM, anchor="mm")
    d.text((S / 2, 1120), "Meal Planner & Grocery List  ·  36-tab Excel "
           "spreadsheet", font=F_SANS(44), fill=SAGE, anchor="mm")
    pill(d, (620, 1300), "LOVE IT? A REVIEW MAKES OUR DAY",
         fg=GREEN_DARK, bg=CREAM, size=42)
    d.text((S / 2, 1560), "Questions about the spreadsheet? Message the "
           "shop any time.", font=F_SANS(40), fill=GREEN_SOFT, anchor="mm")
    d.text((S / 2, 1880), "For personal use only  ·  Not for resale",
           font=F_SANS(36), fill=(120, 160, 140), anchor="mm")
    return img


# ------------------------------------------------------------ listing copy
TITLES = [
    "Meal Planner & Grocery List Spreadsheet, Excel Meal Planning Template, "
    "Pantry Inventory, Food Budget Tracker, Instant Download",
    "Excel Meal Planner Spreadsheet, Weekly Meal Planner, Grocery List "
    "Template, Recipe Organizer, Nutrition Tracker, Digital Download",
    "Meal Planning Spreadsheet for Excel, Grocery List, Pantry Tracker, Meal "
    "Prep Planner, Food Waste Log, Budget Tracker, Digital Download",
    "Family Meal Planner Spreadsheet, Weekly & Monthly Planner, Grocery "
    "Budget Tracker, Recipe Organizer, Excel Template, Instant Download",
    "Meal Planner Excel Template, Grocery List, Pantry Inventory, Food "
    "Budget & Nutrition Tracker, Kitchen Organization, Instant Download",
]

TAGS = [
    "meal planner",
    "grocery list",
    "meal planning excel",
    "meal planner excel",
    "meal plan template",
    "grocery template",
    "pantry inventory",
    "recipe organizer",
    "food waste tracker",
    "weekly meal planner",
    "meal prep planner",
    "grocery budget",
    "nutrition tracker",
]

DESCRIPTION = """\
MEAL PLANNER & GROCERY LIST SPREADSHEET | 36-Tab Excel Workbook

Plan the week, shop the list, cook the food, waste less. This is a complete
meal planning system in one Excel workbook - recipes, meal plans, an
automatic grocery list, pantry stock with use-by dates, batch cooking, food
waste, nutrition and a food budget, all connected to each other.

You get TWO workbooks: a filled sample packed with example data so you can
see exactly how it works, and a blank template ready for your own kitchen.

-----------------------------------------------------------------------
WHAT'S INCLUDED
-----------------------------------------------------------------------

* Filled sample workbook (.xlsx) - 38 recipes, 62 ingredients, 107 planned
  meals, real prices, dates and a full worked month of data.
* Blank template (.xlsx) - the same 36 tabs with clean input cells, ready
  for your own recipes, budget and household.
* How-to guide - the 45-minute set-up and the 15-minute weekly routine.
* Print-ready pages - Print Week (fridge door), Print Shopping (store),
  Print Recipe (kitchen counter).

-----------------------------------------------------------------------
THE 36 TABS
-----------------------------------------------------------------------

PLAN: Meal Plan, Weekly Planner, Monthly Planner, Rotation, Events, Meal
Prep
RECIPES: Recipes, Recipe Ingredients, Ingredients, Recipe Costs, Dietary
Filters, Food Safety
SHOP: Grocery List, Staples, Grocery Spending, Store Prices, Stores, Pantry
COOK: Leftovers, Fridge & Freezer, Converter, Print Recipe, Print Week,
Print Shopping
TRACK: Food Waste, Nutrition, Budget, Goals, Sustainability, Reports
START: Start Here, Dashboard, Settings, Household, Lists, Help

-----------------------------------------------------------------------
HOW IT WORKS
-----------------------------------------------------------------------

Every tab is connected:

* Plan a meal and its ingredients flow to the grocery list automatically -
  scaled to your servings and reduced by what the pantry already has.
* Record what you spent and the Budget tab compares it with the plan, month
  by month.
* Log what you bin on the Food Waste tab and it is priced, ranked and
  counted against your waste target.
* The Dashboard shows the whole week at a glance: meals, calories, cost,
  what is about to expire and which meals are overdue for another turn.

-----------------------------------------------------------------------
HOW TO USE IT
-----------------------------------------------------------------------

SET UP (about 45 minutes, once)

1. Settings - household size, weekly budget, prep day, shopping day,
   calorie target, how long leftovers keep.
2. Household - who eats with you and anything they avoid.
3. Dietary Filters - allergies and things to avoid (checked automatically
   against every recipe and plan).
4. Recipes + Recipe Ingredients - start with the 5-10 meals you cook most.
5. Ingredients - your ingredient list with a price, a unit and a shelf life.
6. Staples and Stores - the things you buy every week, and where you shop.

EVERY WEEK (about 15 minutes)

1. Plan the meals on the Meal Plan tab - one row per meal.
2. Open the Grocery List: it is already built, grouped by aisle and priced.
   Tick off what you already have and shop the rest.
3. Record what you actually spent on Grocery Spending.
4. Log anything you bin on Food Waste - with the reason.
5. On prep day, batch cook from the Meal Prep tab and log the portions on
   Leftovers and Fridge & Freezer.

EVERY MONTH (about 10 minutes)

Add a Budget row, read the Reports tab, check the Rotation tab for overdue
meals, and set a Goal - waste under 5%, four home-cooked meals a week,
whatever matters to you.

-----------------------------------------------------------------------
FEATURES
-----------------------------------------------------------------------

* Automatic grocery list - built from your plan, adjusted for the pantry
* Use-by dates calculated per ingredient and per batch
* Cost per recipe, per meal and per serving, from your own prices
* Nutrition tracking against your own calorie and macro targets
* Food waste log with costs, reasons and monthly shares
* Budget: planned vs actual groceries, eating out and waste
* Rotation guard - flags meals that are coming round too fast
* Dietary filter checks on every planned meal
* Printable week plan, shopping list and recipe card
* Named ranges and guided Start Here and Help tabs

-----------------------------------------------------------------------
THE SPECS
-----------------------------------------------------------------------

* File format: .xlsx (two workbooks)
* Works in: Microsoft Excel 2010 and later, LibreOffice Calc, Google Sheets
* No macros, no add-ins, no subscription - classic spreadsheet formulas
* Sheets are protected to keep the formulas safe (password is in the guide;
  input cells stay unlocked so you can just type)
* Sample data: a UK family of four with a GBP 120 weekly budget - the
  currency and labels are easy to change
* Language: English

-----------------------------------------------------------------------
LICENCE & SUPPORT
-----------------------------------------------------------------------

For personal use. Make copies for your own household - please do not
resell, redistribute or share the files.

This is an instant digital download; nothing will be shipped. If anything
is unclear, or you need a hand opening the file, message the shop - we
usually reply within a day.

Thank you for shopping with us. Plan the week. Shop the list. Waste less.
"""

HOW_TO = """\
HOW TO USE THE MEAL PLANNER & GROCERY LIST
==========================================

Thank you for your purchase! Here is the short version of how to get
running. (The workbook itself has Start Here and Help tabs that say the
same thing, with pictures.)

WHAT YOU HAVE
-------------
* Meal Planner & Grocery List.xlsx          - filled sample
* Meal Planner & Grocery List (Blank).xlsx  - blank template
* This guide

Open either workbook in Excel 2010+, LibreOffice Calc or Google Sheets.
Every sheet is protected so the formulas cannot be overwritten - the
yellow/cream cells are yours to type in. The password to unprotect any
sheet is: premium

THE 45-MINUTE SET-UP (once)
---------------------------
1. Settings tab: household size, weekly food budget, prep day, shopping
   day, calorie target, how many days leftovers keep, and your waste
   reduction target.
2. Household tab: one row per person, with anything they will not eat.
3. Dietary Filters tab: allergies and avoidances - these are checked
   automatically on every planned meal.
4. Recipes + Recipe Ingredients tabs: add the 5-10 meals you cook most
   and what goes into them.
5. Ingredients tab: the same ingredients, with a price, a unit and a
   shelf life in days. (Names must match exactly between tabs - that is
   the golden rule.)
6. Staples + Stores: weekly basics and where you shop.

THE 15-MINUTE WEEKLY ROUTINE
----------------------------
1. Meal Plan tab: one row per meal - date, slot, recipe, servings.
   Nutrition, cost and diet checks appear as you go.
2. Grocery List tab: already built from your plan, grouped by aisle and
   reduced by the pantry. Tick things off as you shop.
3. Grocery Spending tab: record what you actually spent.
4. Food Waste tab: log anything you bin, with the reason and the cost.
5. Prep day: batch cook from the Meal Prep tab; log portions on
   Leftovers and Fridge & Freezer.

THE 10-MINUTE MONTHLY ROUTINE
-----------------------------
* Budget tab: add a row for the new month (planned/actual fill in).
* Reports tab: favourites, most expensive dishes, biggest waste, where
  the money goes.
* Rotation tab: which meals are overdue for another turn.
* Goals tab: set one habit target and watch the progress bar fill up.

THE PRINTABLES
--------------
* Print Week   - one page for the fridge door
* Print Shopping - one page for the store, sorted by aisle
* Print Recipe  - one recipe in a big friendly layout
All are formatted to fit one page. Change the week or the recipe at the
top and print.

TIPS
----
* Plan around what is already in the house - the Dashboard's
  "Use it or lose it" tile shows the most urgent items.
* Cook double: a second portion costs minutes, not pounds.
* Log the waste for one month - most households cut it just by seeing it.
* Ingredient names must match exactly between tabs.

QUESTIONS?
-----------
Message the shop any time - we usually reply within a day.
"""


def write_copy():
    COPY_OUT.mkdir(parents=True, exist_ok=True)
    for i, title in enumerate(TITLES, 1):
        assert len(title) <= 140, f"title {i} too long: {len(title)}"
    for tag in TAGS:
        assert len(tag) <= 20, f"tag too long: {tag}"

    (COPY_OUT / "TITLES.txt").write_text(
        "ETSY LISTING TITLES (each under 140 characters)\n"
        + "=" * 50 + "\n\n"
        + "\n\n".join(f"{i}. {t}" for i, t in enumerate(TITLES, 1)),
        encoding="utf-8")
    (COPY_OUT / "TAGS.txt").write_text(
        "ETSY TAGS (13 tags, each under 20 characters)\n"
        + "=" * 50 + "\n\n"
        + "\n".join(f"{i:2}. {t}" for i, t in enumerate(TAGS, 1)),
        encoding="utf-8")
    (COPY_OUT / "DESCRIPTION.txt").write_text(DESCRIPTION, encoding="utf-8")
    (COPY_OUT / "HOW_TO_USE.txt").write_text(HOW_TO, encoding="utf-8")
    (COPY_OUT / "BULLET_POINTS.txt").write_text(
        "SHORT BULLET POINTS (for the listing highlights / social posts)\n"
        + "=" * 50 + "\n\n"
        + "\n".join([
            "- 36-tab Excel meal planner: plan, shop, cook and track",
            "- Automatic grocery list - built from your meal plan",
            "- Pantry tracker with calculated use-by dates",
            "- Food budget: planned vs actual, month by month",
            "- Nutrition log against your own targets",
            "- Recipe book with cost per serving and diet checks",
            "- Batch cooking, leftovers and freezer tracking",
            "- Food waste log that prices what you bin",
            "- 3 printables: week plan, shopping list, recipe card",
            "- Filled sample + blank template included",
            "- Excel 2010+, LibreOffice and Google Sheets",
            "- No macros - protected sheets, easy to use",
            "- Instant digital download",
        ]), encoding="utf-8")


# --------------------------------------------------------------- assembly
IMAGE_BUILDERS = [
    ("01-cover.jpg", make_cover),
    ("02-whats-inside.jpg", make_whats_inside),
    ("03-36-tabs.jpg", make_tabs),
    ("04-dashboard.jpg", make_dashboard),
    ("05-meal-plan.jpg", make_meal_plan),
    ("06-grocery-list.jpg", make_grocery),
    ("07-pantry.jpg", make_pantry),
    ("08-budget.jpg", make_budget),
    ("09-nutrition.jpg", make_nutrition),
    ("10-batch-cooking.jpg", make_batch),
    ("11-printables.jpg", make_printables),
    ("12-how-it-works.jpg", make_how_it_works),
    ("13-two-versions.jpg", make_two_versions),
    ("14-specs.jpg", make_specs),
    ("15-perfect-for.jpg", make_perfect_for),
    ("16-waste-less.jpg", make_waste_less),
    ("17-faq.jpg", make_faq),
    ("18-thank-you.jpg", make_thankyou),
]


def main() -> int:
    if not FILLED.exists() or not BLANK.exists():
        print("FAIL: build both workbooks first:")
        print("  python build_meal_planner_workbook.py")
        print("  python build_meal_planner_workbook.py --blank "
              "-o \"output/Meal Planner & Grocery List (Blank).xlsx\"")
        return 1

    IMG_OUT.mkdir(parents=True, exist_ok=True)
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)

    for name, builder in IMAGE_BUILDERS:
        img = builder().convert("RGB")
        out = IMG_OUT / name
        img.save(out, "JPEG", quality=90, optimize=True)
        print(f"  image {name}  ({out.stat().st_size // 1024} KB)")

    write_copy()
    print(f"  listing copy -> {COPY_OUT}")

    shutil.copy2(FILLED, SHEETS_OUT / FILLED.name)
    shutil.copy2(BLANK, SHEETS_OUT / BLANK.name)
    print(f"  workbooks -> {SHEETS_OUT}")

    DOWNLOAD.mkdir(exist_ok=True)
    zip_path = DOWNLOAD / "meal-planner-etsy-kit.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in (IMG_OUT, COPY_OUT, SHEETS_OUT):
            for f in sorted(folder.iterdir()):
                zf.write(f, f"meal-planner-etsy-kit/{folder.name}/{f.name}")
    print(f"\nWrote {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.1f} "
          f"MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
