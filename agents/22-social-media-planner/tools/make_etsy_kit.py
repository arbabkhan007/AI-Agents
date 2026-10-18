"""
make_etsy_kit.py - builds the complete Etsy listing kit for the
Social Media Content Calendar & Analytics Planner spreadsheet.

Produces:
    etsy/kit/etsy-listing-images/   18 listing images (2000x2000)
    etsy/kit/listing-copy/          titles, tags, description, how-to-use
    etsy/kit/spreadsheets/          filled sample + blank template
    download/social-media-content-planner-etsy-kit.zip

Usage:
    python tools/make_etsy_kit.py
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

FILLED = ROOT / "output" / "Social Media Content Planner.xlsx"
BLANK = ROOT / "output" / "Social Media Content Planner (Blank).xlsx"

S = 2000                     # canvas size

# ---- brand palette (indigo / coral / oat) ---------------------------------
INK        = (36, 27, 56)        # #241B38
INDIGO     = (59, 42, 107)       # #3B2A6B
INDIGO_MID = (99, 80, 168)       # #6350A8
INDIGO_DARK = (32, 22, 62)
LILAC      = (231, 227, 246)     # #E7E3F6
LILAC_DEEP = (214, 208, 236)
CORAL      = (242, 102, 94)      # #F2665E
CORAL_SOFT = (253, 235, 233)     # #FDEBE9
OAT        = (244, 239, 230)     # #F4EFE6
OAT_DARK   = (230, 222, 208)
WARM_WHITE = (255, 252, 247)     # #FFFCF7
WHITE      = (255, 255, 255)
GREY       = (95, 90, 112)       # #5F5A70
GREY_SOFT  = (214, 210, 224)
GREEN      = (42, 122, 86)
GREEN_SOFT = (222, 240, 230)
AMBER      = (196, 128, 28)
AMBER_SOFT = (252, 240, 214)

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


def dim(img: Image.Image, alpha: int = 120, color=(28, 20, 48)) -> Image.Image:
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
    dark = Image.new("RGB", img.size, (24, 16, 44))
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


def pill(draw, xy, label, fg=WHITE, bg=INDIGO_MID, pad=(28, 14), size=42,
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
                               radius=radius, fill=(212, 205, 228))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                           width=width)


def soft_panel(img: Image.Image, box, radius=44, alpha=120,
               color=(24, 16, 44)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle(box, radius=radius, fill=(*color, alpha))
    img.paste(overlay, (0, 0), overlay)


def check_icon(draw, cx, cy, r=26, color=INDIGO_MID, width=10):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    draw.line([(cx - r * 0.45, cy + r * 0.05), (cx - r * 0.1, cy + r * 0.45),
               (cx + r * 0.55, cy - r * 0.4)], fill=color, width=width + 2)


def numbered_badge(draw, cx, cy, n, r=54, bg=CORAL, fg=WHITE):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    draw.text((cx, cy), str(n), font=F_SANS_B(int(r * 1.1)), fill=fg,
              anchor="mm")


STATUS_COLORS = {
    "Posted": (GREEN, GREEN_SOFT),
    "Scheduled": (INDIGO, LILAC),
    "Draft": (AMBER, AMBER_SOFT),
    "Idea": (GREY, (238, 236, 242)),
    "In Progress": (CORAL, CORAL_SOFT),
    "Ready": (INDIGO_MID, LILAC),
    "Active": (GREEN, GREEN_SOFT),
}


# ----------------------------------------------------------- spreadsheet UI
def sheet_screen(title, headers, rows, col_w, highlight=None, status_col=None,
                 status_colors=None, size=None, footer=None):
    """A tiny spreadsheet UI: column letters, indigo header, data rows."""
    W = size[0] if size else 1280
    total = sum(col_w)
    scale = (W - 70) / total
    col_w = [w * scale for w in col_w]
    row_h = 62
    H = 86 + 40 + 58 + row_h * len(rows) + (70 if footer else 24)
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 86], fill=INDIGO)
    d.text((30, 43), title, font=F_SANS_B(38), fill=WHITE, anchor="lm")
    y0 = 86
    d.rectangle([0, y0, W, y0 + 40], fill=(236, 233, 244))
    x = 70
    for i, (head, w) in enumerate(zip(headers, col_w)):
        letter = chr(ord("A") + i)
        d.text((x + w / 2, y0 + 20), letter, font=F_SANS_B(26), fill=GREY,
               anchor="mm")
        x += w
    y = y0 + 40
    d.rectangle([0, y, W, y + 58], fill=INDIGO_MID)
    d.rectangle([0, y, 70, y + 58], fill=INDIGO)
    d.text((35, y + 29), "#", font=F_SANS_B(26), fill=WHITE, anchor="mm")
    x = 70
    for head, w in zip(headers, col_w):
        d.text((x + 14, y + 29), head, font=F_SANS_B(27), fill=WHITE,
               anchor="lm")
        x += w
    y += 58
    for ri, row in enumerate(rows):
        bg = WHITE if ri % 2 == 0 else (247, 245, 251)
        if highlight is not None and ri == highlight:
            bg = CORAL_SOFT
        d.rectangle([0, y, W, y + row_h], fill=bg)
        d.rectangle([0, y, 70, y + row_h], fill=(236, 233, 244))
        d.text((35, y + row_h / 2), str(ri + 1), font=F_SANS(26), fill=GREY,
               anchor="mm")
        x = 70
        for ci, (cell, w) in enumerate(zip(row, col_w)):
            if status_col is not None and ci == status_col:
                colors = status_colors or STATUS_COLORS
                fg, bgc = colors.get(str(cell), (INDIGO_MID, LILAC))
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
    x = 70
    for w in col_w:
        d.line([(x, y0), (x, y)], fill=GREY_SOFT, width=2)
        x += w
    d.line([(70, y0), (70, y)], fill=GREY_SOFT, width=2)
    d.line([(0, y), (W, y)], fill=GREY_SOFT, width=2)
    if footer:
        d.rectangle([0, y, W, y + 70], fill=OAT)
        d.text((30, y + 35), footer, font=F_SANS_B(28), fill=INDIGO,
               anchor="lm")
    return img


def laptop(img: Image.Image, screen: Image.Image, cx: int, top: int,
           width: int = 1400):
    d = ImageDraw.Draw(img)
    sw = width
    sh = int(screen.height * sw / screen.width)
    sc = screen.resize((sw, sh), Image.LANCZOS)
    pad = 22
    d.rounded_rectangle([cx - sw / 2 - pad, top - pad,
                         cx + sw / 2 + pad, top + sh + pad],
                        radius=18, fill=(46, 42, 66))
    img.paste(sc, (int(cx - sw / 2), top))
    base_h = 46
    d.polygon([(cx - sw / 2 - pad, top + sh + pad),
               (cx + sw / 2 + pad, top + sh + pad),
               (cx + sw / 2 + 90, top + sh + pad + base_h),
               (cx - sw / 2 - 90, top + sh + pad + base_h)],
              fill=(202, 198, 214))
    d.rounded_rectangle([cx - 120, top + sh + pad + 10, cx + 120,
                         top + sh + pad + 22], radius=6, fill=(150, 146, 170))


def phone(img: Image.Image, screen: Image.Image, cx: int, top: int,
          width: int = 520):
    d = ImageDraw.Draw(img)
    sw = width
    sh = int(screen.height * sw / screen.width)
    sc = screen.resize((sw, sh), Image.LANCZOS)
    pad = 20
    d.rounded_rectangle([cx - sw / 2 - pad, top - pad,
                         cx + sw / 2 + pad, top + sh + pad],
                        radius=64, fill=(34, 30, 52))
    img.paste(sc, (int(cx - sw / 2), top))
    d.rounded_rectangle([cx - 90, top - pad + 8, cx + 90, top - pad + 34],
                        radius=13, fill=(34, 30, 52))


def page_mockup(title, subtitle, lines, col_headers=None, size=(560, 760),
                col_widths=None):
    W, H = size
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 12], fill=INDIGO_MID)
    d.text((W / 2, 60), title, font=F_SANS_B(34), fill=INDIGO, anchor="mm")
    d.text((W / 2, 108), subtitle, font=F_SANS(24), fill=GREY, anchor="mm")
    d.line([(50, 140), (W - 50, 140)], fill=LILAC_DEEP, width=4)
    y = 180
    if col_headers:
        x = 50
        widths = col_widths or [110, 220, 110]
        d.rectangle([40, y - 10, W - 40, y + 38], fill=LILAC)
        for head, w in zip(col_headers, widths):
            d.text((x, y + 14), head, font=F_SANS_B(21), fill=INDIGO,
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
    img = vgrad(INDIGO, INDIGO_DARK)
    d = ImageDraw.Draw(img)
    for r, a in ((1500, 30), (1150, 26), (850, 22)):
        d.ellipse([S - r, -r // 3, S + r // 2, r], outline=(102, 88, 160),
                  width=a)
    d.text((S / 2, 140), "SOCIAL MEDIA", font=F_SERIF(150), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 268), "CONTENT PLANNER", font=F_SERIF(126), fill=CORAL,
           anchor="mm")
    d.text((S / 2, 388), "Content Calendar & Analytics  ·  43-Tab Excel "
           "Spreadsheet", font=F_SANS_B(46), fill=OAT, anchor="mm")

    screen = sheet_screen(
        "CONTENT CALENDAR — March",
        ["Date", "Title / Topic", "Pillar", "Platform", "Status"],
        [["Mon 02", "Throwing a mug, start to finish", "Process",
          "Instagram", "Posted"],
         ["Tue 03", "New glaze reveal", "Product", "Instagram", "Posted"],
         ["Wed 04", "Why I started my studio", "Brand", "Instagram",
          "Posted"],
         ["Thu 05", "Styling open shelving", "Education", "Pinterest",
          "Scheduled"],
         ["Fri 06", "Kiln unboxing", "Process", "TikTok", "In Progress"],
         ["Sat 07", "Customer kitchen feature", "Community", "Instagram",
          "Ready"],
         ["Mon 09", "The mug that sold out twice", "Product", "Facebook",
          "Draft"]],
        [170, 480, 210, 230, 240],
        status_col=4,
        footer="7 posts this week  ·  captions linked  ·  2 campaigns live")
    laptop(img, screen, S // 2, 500, width=1380)

    chips = ["43 TABS", "EXCEL 2010+", "PROTECTED SHEETS",
             "FILLED + BLANK"]
    x = S / 2 - sum(len(c) * 26 + 90 for c in chips) / 2
    for c in chips:
        w, _ = pill(d, (x, 1560), c, fg=INDIGO, bg=OAT, size=40)
        x += w + 26
    d.text((S / 2, 1720), "Plan  ·  Create  ·  Publish  ·  Measure",
           font=F_SANS(46), fill=LILAC, anchor="mm")
    d.text((S / 2, 1860), "Filled sample + blank template  ·  Instant "
           "digital download", font=F_SANS(38), fill=LILAC_DEEP,
           anchor="mm")
    return img


def make_whats_inside():
    img = vgrad(OAT, LILAC)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 170), "WHAT'S INSIDE YOUR DOWNLOAD", font=F_SERIF(86),
           fill=INDIGO, anchor="mm")
    d.text((S / 2, 280), "Everything you need to plan, post and grow",
           font=F_SANS_B(48), fill=INDIGO_MID, anchor="mm")

    items = [
        ("1", "FILLED SAMPLE", "A complete worked example for a small "
         "handmade brand - 30 scheduled posts, real captions, campaigns "
         "and analytics."),
        ("2", "BLANK TEMPLATE", "The same 43-tab workbook with clean "
         "input cells, ready for your brand, your platforms and your "
         "voice."),
        ("3", "HOW-TO GUIDE", "Set up in under an hour, then a weekly "
         "routine that runs itself - with the sheet password included."),
        ("4", "PRINTABLE PAGES", "A one-page content brief for every "
         "post and a weekly schedule for the wall."),
    ]
    cw, ch = 860, 620
    gap = 80
    for i, (n, title, body) in enumerate(items):
        x = 140 + (i % 2) * (cw + gap)
        y = 420 + (i // 2) * (ch + gap)
        card(d, [x, y, x + cw, y + ch], fill=WHITE)
        numbered_badge(d, x + 100, y + 110, n, r=58, bg=INDIGO_MID)
        d.text((x + 190, y + 110), title, font=F_SANS_B(56), fill=INDIGO,
               anchor="lm")
        para(d, (x + 70, y + 220), body, F_SANS(42), INK, cw - 140,
             line_h=64)
        pill(d, (x + 70, y + ch - 130), "INCLUDED", fg=INDIGO, bg=LILAC,
             size=36)
    d.text((S / 2, 1820), "Instant download  ·  No physical item",
           font=F_SANS_B(44), fill=INDIGO_MID, anchor="mm")
    d.text((S / 2, 1910), "Opens in Excel, LibreOffice or Google Sheets",
           font=F_SANS(38), fill=INDIGO_MID, anchor="mm")
    return img


def make_tabs():
    img = vgrad(WARM_WHITE, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "43 TABS. ONE WORKBOOK.", font=F_SERIF(96),
           fill=INDIGO, anchor="mm")
    d.text((S / 2, 258), "From idea to report - every tab is connected",
           font=F_SANS_B(46), fill=INDIGO_MID, anchor="mm")

    groups = [
        ("PLAN", INDIGO_MID,
         ["Content Calendar", "Month View", "Workflow", "Idea Bank",
          "Seasonal Planner", "Campaigns", "Launch Planner"]),
        ("CREATE", CORAL,
         ["Caption Bank", "Hashtag Bank", "Brand Voice", "Assets",
          "Repurposing"]),
        ("PUBLISH", AMBER,
         ["Instagram", "TikTok", "Pinterest", "YouTube", "Facebook"]),
        ("GROW", GREEN,
         ["Influencers", "UGC Tracker", "Competitors", "Trends",
          "Goals"]),
        ("MEASURE", INDIGO,
         ["Analytics", "Performance", "AB Tests", "Ads", "Budget",
          "Reports"]),
        ("START", GREY,
         ["Start Here", "Dashboard", "Annual Dashboard", "Settings",
          "Lists", "Team", "Tasks", "Compliance", "Help"]),
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
        d.line([(90, y - 22), (1910, y - 22)], fill=OAT_DARK, width=3)
    d.text((S / 2, y + 80), "Everything talks to everything else",
           font=F_SANS_B(52), fill=INDIGO, anchor="mm")
    para(d, (300, y + 170),
         "Plan a post and the dashboard counts it. Publish it and the "
         "analytics tab measures it. The numbers roll into the report - "
         "and the report tells you what to plan next.",
         F_SANS(42), INK, 1400, line_h=62, center=True)
    return img


def make_dashboard():
    img = vgrad(LILAC, WARM_WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "A DASHBOARD THAT COUNTS ITSELF",
           font=F_SERIF(84), fill=INDIGO, anchor="mm")
    d.text((S / 2, 258), "Posts, reach, engagement and revenue - live",
           font=F_SANS_B(46), fill=INDIGO_MID, anchor="mm")

    tiles = [("POSTS THIS WEEK", "7"), ("WAITING TO GO LIVE", "3"),
             ("AVG ENGAGEMENT", "5.8%"), ("EST. REVENUE", "$1,420")]
    tw_ = 420
    for i, (label, value) in enumerate(tiles):
        x = 140 + i * (tw_ + 40)
        card(d, [x, 360, x + tw_, 560], fill=WHITE)
        d.text((x + tw_ / 2, 415), label, font=F_SANS_B(26), fill=GREY,
               anchor="mm")
        d.text((x + tw_ / 2, 500), value, font=F_SANS_B(64), fill=INDIGO,
               anchor="mm")

    screen = sheet_screen(
        "DASHBOARD",
        ["Platform", "Posts", "Followers", "Engagement", "Spend"],
        [["Instagram", "12", "8,420", "4.2%", "$320"],
         ["TikTok", "8", "12,800", "6.1%", "$0"],
         ["Pinterest", "15", "2,310", "1.8%", "$45"],
         ["YouTube", "2", "180", "2.2%", "$0"],
         ["Facebook", "6", "1,120", "1.5%", "$60"]],
        [330, 190, 220, 250, 190],
        footer="Total reach 31,220 this month  ·  best post: kiln "
        "unboxing")
    laptop(img, screen, S // 2, 640, width=1380)
    d.text((S / 2, 1740), "The queue shows what is missing a caption, "
           "an asset or a date", font=F_SANS_B(42), fill=INDIGO,
           anchor="mm")
    d.text((S / 2, 1850), "Nothing slips through",
           font=F_SANS_B(44), fill=CORAL, anchor="mm")
    return img


def make_calendar():
    img = vgrad(WARM_WHITE, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "600-ROW CONTENT CALENDAR", font=F_SERIF(88),
           fill=INDIGO, anchor="mm")
    d.text((S / 2, 258), "One row per post - IDs, dates and lookups fill "
           "themselves", font=F_SANS_B(42), fill=INDIGO_MID, anchor="mm")

    screen = sheet_screen(
        "CONTENT CALENDAR",
        ["ID", "Date", "Title / Topic", "Pillar", "Owner", "Status"],
        [["C-0001", "02 Mar", "Throwing a mug, start to finish",
          "Process", "Jordan", "Posted"],
         ["C-0002", "03 Mar", "New glaze: speckled oat", "Product",
          "Jordan", "Posted"],
         ["C-0003", "04 Mar", "Why I started Wildflower", "Brand",
          "Jordan", "Posted"],
         ["C-0004", "05 Mar", "Styling open shelving", "Education",
          "Priya", "Scheduled"],
         ["C-0005", "06 Mar", "Kiln unboxing - spring batch", "Process",
          "Sam", "In Progress"],
         ["C-0006", "07 Mar", "Customer kitchen feature", "Community",
          "Priya", "Ready"],
         ["C-0007", "09 Mar", "The mug that sold out twice", "Product",
          "Jordan", "Draft"],
         ["C-0008", "10 Mar", "3 ways to care for mugs", "Education",
          "Sam", "Posted"]],
        [150, 160, 500, 210, 190, 230],
        status_col=5,
        footer="Filter by month  ·  every register feeds the drop downs")
    laptop(img, screen, S // 2, 380, width=1440)

    feats = ["Statuses drive every dashboard number",
             "Captions, hashtags and assets link by ID",
             "Overdue posts flag themselves"]
    y = 1620
    for f_ in feats:
        check_icon(d, 560, y + 24, r=22, color=INDIGO_MID, width=8)
        d.text((620, y), f_, font=F_SANS(40), fill=INK, anchor="lm")
        y += 100
    return img


def make_month_view():
    img = vgrad(LILAC, WARM_WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "A MONTH YOU CAN ACTUALLY READ",
           font=F_SERIF(80), fill=INDIGO, anchor="mm")
    d.text((S / 2, 258), "The calendar, seen as a wall planner",
           font=F_SANS_B(46), fill=INDIGO_MID, anchor="mm")

    # month grid mock
    x0, y0 = 160, 380
    cw, ch = 240, 250
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        d.rectangle([x0 + i * cw, y0 - 60, x0 + (i + 1) * cw, y0],
                    fill=INDIGO_MID)
        d.text((x0 + i * cw + cw / 2, y0 - 30), day, font=F_SANS_B(28),
               fill=WHITE, anchor="mm")
    filled = {
        (0, 0): ["Throwing a mug", "Kiln unboxing"],
        (1, 0): ["Glaze reveal"],
        (2, 0): ["Brand story"],
        (3, 0): ["Shelf styling", "Care tips"],
        (4, 0): ["ASMR trimming"],
        (0, 1): ["Sold out twice"],
        (2, 1): ["Preview reel", "+1 more"],
        (4, 1): ["Launch day"],
    }
    day = 1
    for row in range(4):
        for col in range(7):
            box = [x0 + col * cw, y0 + row * ch,
                   x0 + (col + 1) * cw, y0 + (row + 1) * ch]
            d.rectangle(box, fill=WHITE, outline=GREY_SOFT, width=2)
            if row == 3 and col > 3:
                continue
            d.text((box[0] + 18, box[1] + 16), str(day), font=F_SANS_B(30),
                   fill=INDIGO, anchor="lm")
            items = filled.get((col, row))
            if items:
                yy = box[1] + 70
                for it in items:
                    color = CORAL if it == "+1 more" else INK
                    d.text((box[0] + 18, yy), "• " + it,
                           font=F_SANS(21), fill=color, anchor="lm")
                    yy += 44
            day += 1

    d.text((S / 2, 1700), "Up to two posts per day on the grid - the "
           "rest tuck behind a '+n more' note",
           font=F_SANS_B(38), fill=INDIGO, anchor="mm")
    d.text((S / 2, 1810), "Set the month at the top - the grid fills "
           "itself", font=F_SANS(38), fill=INDIGO_MID, anchor="mm")
    return img


def make_banks():
    img = vgrad(WARM_WHITE, CORAL_SOFT)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "CAPTIONS, HASHTAGS & IDEAS",
           font=F_SERIF(84), fill=INDIGO, anchor="mm")
    d.text((S / 2, 258), "Write it once. Reuse it forever.",
           font=F_SANS_B(48), fill=CORAL, anchor="mm")

    screen = sheet_screen(
        "CAPTION BANK",
        ["ID", "Hook", "Caption", "Used", "Status"],
        [["CAP-001", "Watch a mug come out of nothing",
          "Six minutes at the wheel...", "3", "Approved"],
         ["CAP-002", "The glaze I almost did not launch",
          "Three test batches later...", "2", "Approved"],
         ["CAP-003", "I quit my job to play with mud",
          "Five years ago I took a class...", "1", "Approved"],
         ["CAP-004", "Open shelves looking chaotic?",
          "Start with one hero piece...", "2", "Approved"],
         ["CAP-005", "The best sound in the studio",
          "Every firing is a surprise...", "1", "Draft"],
         ["CAP-006", "Your shelves, but make it ours",
          "Ana styled her new mugs...", "2", "Approved"]],
        [170, 430, 380, 130, 210],
        status_col=4,
        footer="Caption IDs link to the calendar  ·  Used counts every "
        "placement")
    laptop(img, screen, S // 2, 380, width=1420)

    cards_ = [("IDEA BANK", "Capture sparks, score them, promote the "
               "good ones to the calendar."),
              ("HASHTAG BANK", "Tested sets with live tag counts - never "
               "paste the same block twice."),
              ("BRAND VOICE", "Four words, examples and a checklist - so "
               "every caption sounds like you.")]
    x = 150
    for t, body in cards_:
        card(d, [x, 1560, x + 530, 1860], fill=WHITE)
        d.text((x + 265, 1625), t, font=F_SANS_B(34), fill=INDIGO,
               anchor="mm")
        para(d, (x + 50, 1690), body, F_SANS(28), INK, 430, line_h=40,
             center=True)
        x += 570
    return img


def make_platforms():
    img = vgrad(INDIGO, INDIGO_DARK)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "PLANNER FOR EVERY PLATFORM",
           font=F_SERIF(84), fill=WHITE, anchor="mm")
    d.text((S / 2, 258), "Instagram, TikTok, Pinterest, YouTube and "
           "Facebook - each gets its own tab",
           font=F_SANS_B(38), fill=LILAC, anchor="mm")

    plats = [
        ("INSTAGRAM", "Reels, carousels, stories\nand collab posts",
         "bg_phone.jpg"),
        ("TIKTOK", "Hooks, trends and sounds\ntracked per video",
         "bg_studio.jpg"),
        ("PINTEREST", "Keyword titles and\nboards that compound",
         "bg_desk.jpg"),
        ("YOUTUBE", "Vlogs and tutorials -\nevery video owes 3 shorts",
         "bg_laptop.jpg"),
        ("FACEBOOK", "Community, events and\nlocal reach",
         "bg_laptop.jpg"),
    ]
    x = 120
    for i, (name, body, bg) in enumerate(plats):
        w = 340
        card(d, [x, 420, x + w, 1160], fill=WHITE)
        if bg and (ASSETS / bg).exists():
            photo = cover(ASSETS / bg, size=w - 48).resize((w - 48, 320))
            img.paste(photo, (x + 24, 444))
        else:
            d.rounded_rectangle([x + 24, 444, x + w - 24, 764], radius=24,
                                fill=LILAC)
            d.text((x + w / 2, 604), name.split()[0], font=F_SANS_B(46),
                   fill=INDIGO, anchor="mm")
        d.text((x + w / 2, 850), name, font=F_SANS_B(36), fill=INDIGO,
               anchor="mm")
        para(d, (x + 30, 920), body.replace("\n", " "), F_SANS(27), INK,
             w - 60, line_h=38, center=True)
        x += w + 40

    screen = sheet_screen(
        "TIKTOK PLANNER",
        ["Date", "Hook", "Sound", "Status"],
        [["02 Mar", "Watch a mug come out of nothing", "Original", "Posted"],
         ["06 Mar", "The kiln makes the rules", "Trending", "Posted"],
         ["12 Mar", "Sound on. Trust me.", "Original", "Posted"]],
        [220, 620, 300, 240],
        status_col=3, size=(1200, 380),
        footer=None)
    screen = screen.resize((1100, int(screen.height * 1100 / 1200)),
                           Image.LANCZOS)
    img.paste(screen, ((S - 1100) // 2, 1240))
    d.text((S / 2, 1740), "Master calendar plus a deep planner per "
           "network", font=F_SANS_B(42), fill=WHITE, anchor="mm")
    d.text((S / 2, 1850), "Post natively - plan in one place",
           font=F_SANS_B(40), fill=CORAL, anchor="mm")
    return img


def make_campaigns():
    img = vgrad(OAT, WARM_WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "CAMPAIGNS & LAUNCHES", font=F_SERIF(92),
           fill=INDIGO, anchor="mm")
    d.text((S / 2, 262), "Group the posts that push together - budgets "
           "and countdowns included",
           font=F_SANS_B(40), fill=INDIGO_MID, anchor="mm")

    screen = sheet_screen(
        "CAMPAIGNS",
        ["Campaign", "Start", "Budget", "Spent", "Status"],
        [["Spring Collection", "02 Mar", "$400", "$245", "Active"],
         ["Market Days", "02 Mar", "$60", "$60", "Active"],
         ["Etsy Alchemy Launch", "09 Apr", "$150", "$0", "Draft"],
         ["Summer Solstice", "01 Jun", "$250", "$0", "Idea"]],
        [380, 210, 190, 190, 240],
        status_col=4,
        footer="Actual spend pulled from the Budget tab  ·  no double "
        "entry")
    laptop(img, screen, S // 2, 400, width=1360)

    feats = [("LAUNCH COUNTDOWNS",
              "Every drop gets a date, a countdown and a teaser trail"),
             ("SEASONAL PLANNER",
              "Mother's Day, Black Friday, market days - the year's "
              "moments in view"),
             ("TASK PIPELINE",
              "Who owes what by when - with an overdue flag that does "
              "not negotiate")]
    y = 1520
    for t, body in feats:
        card(d, [180, y, 1820, y + 130], fill=WHITE)
        d.text((240, y + 42), t, font=F_SANS_B(34), fill=CORAL,
               anchor="lm")
        d.text((240, y + 92), body, font=F_SANS(30), fill=INK,
               anchor="lm")
        y += 160
    return img


def make_analytics():
    img = vgrad(INDIGO, (26, 18, 52))
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "ANALYTICS THAT TALK BACK",
           font=F_SERIF(88), fill=WHITE, anchor="mm")
    d.text((S / 2, 262), "Log the numbers once a week - the workbook "
           "does the maths", font=F_SANS_B(42), fill=LILAC, anchor="mm")

    tiles = [("TOTAL REACH", "31,220"), ("AVG ENGAGEMENT", "5.8%"),
             ("BEST DAY", "Thu"), ("ROAS", "2.8x")]
    for i, (label, value) in enumerate(tiles):
        x = 160 + i * 440
        card(d, [x, 380, x + 380, 600], fill=(52, 38, 102))
        d.text((x + 190, 435), label, font=F_SANS_B(26), fill=LILAC_DEEP,
               anchor="mm")
        d.text((x + 190, 525), value, font=F_SANS_B(58), fill=WHITE,
               anchor="mm")

    screen = sheet_screen(
        "PERFORMANCE",
        ["ID", "Platform", "Reach", "Engagement", "Revenue"],
        [["C-0001", "Instagram", "4,820", "10.0%", "$112"],
         ["C-0005", "TikTok", "8,960", "12.1%", "$88"],
         ["C-0008", "TikTok", "7,640", "10.5%", "$62"],
         ["C-0010", "TikTok", "11,240", "15.3%", "$54"],
         ["C-0012", "Instagram", "3,720", "8.7%", "$184"]],
        [170, 260, 220, 260, 220],
        status_col=None,
        footer="Engagement, CTR and revenue calculate themselves")
    laptop(img, screen, S // 2, 680, width=1320)

    d.text((S / 2, 1740), "AB tests, ad spend and monthly reports "
           "in the same place", font=F_SANS_B(42), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 1850), "Stop guessing what worked",
           font=F_SANS_B(46), fill=CORAL, anchor="mm")
    return img


def make_printables():
    photo = scrim(dim(cover(ASSETS / "bg_desk.jpg"), 105), side="bottom")
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 150), "PRINT IT. POST IT.", font=F_SERIF(96),
           fill=WHITE, anchor="mm")
    d.text((S / 2, 262), "Clean pages for the creator who likes paper",
           font=F_SANS_B(42), fill=OAT, anchor="mm")

    brief = page_mockup(
        "CONTENT BRIEF", "C-0012  ·  Spring collection preview",
        ["Publish date — 16 Mar, 9:00",
         "Platforms — Instagram, TikTok",
         "Pillar — Product Spotlight",
         "Caption ref — CAP-012",
         "Hashtag set — HT-002",
         "CTA — Shop the preview link in bio",
         "",
         "Ready-to-post checklist",
         "□ Hook written",
         "□ Visual exported",
         "□ Caption approved",
         "□ Link tested"])
    week = page_mockup(
        "WEEKLY SCHEDULE", "Week of 9 March",
        [["Mon", "Sold out twice"],
         ["Tue", "Glaze colours expl."],
         ["Wed", "Packing day stories"],
         ["Thu", "Launch day hero"],
         ["Fri", "Spring reviews"],
         ["Sat", "Market recap"],
         ["Sun", "Maker's note"]],
        col_headers=["Day", "Posts"],
        col_widths=[140, 340])

    photo.paste(brief, (240, 420))
    photo.paste(week, (1200, 420))
    soft_panel(photo, [220, 1300, 1780, 1560], radius=50, alpha=140)
    d.text((S / 2, 1370), "PRINT BRIEF — one page per post",
           font=F_SANS_B(44), fill=WHITE, anchor="mm")
    d.text((S / 2, 1450), "PRINT WEEK — the schedule for the wall",
           font=F_SANS_B(44), fill=WHITE, anchor="mm")
    d.text((S / 2, 1700), "Both set to print on one page - just press "
           "print", font=F_SANS_B(40), fill=OAT, anchor="mm")
    return photo


def make_how_it_works():
    img = vgrad(WARM_WHITE, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "HOW IT WORKS", font=F_SERIF(100), fill=INDIGO,
           anchor="mm")
    d.text((S / 2, 258), "Set up once in an hour. Then 20 minutes a "
           "week.", font=F_SANS_B(46), fill=INDIGO_MID, anchor="mm")

    steps = [
        ("TELL IT ABOUT YOUR BRAND", "Name, currency, year and defaults "
         "on the Settings tab - the headers follow."),
        ("BUILD THE REFERENCE TABS", "Accounts, pillars and audience "
         "personas. Drop downs fill themselves from the Lists tab."),
        ("PLAN THE CALENDAR", "One row per post. IDs, weekdays and "
         "lookups appear as you type."),
        ("PUBLISH & LOG", "Post natively, then log the numbers in "
         "Performance and Analytics."),
        ("READ & REPEAT", "Reports writes the summary. The next month's "
         "plan practically writes itself."),
    ]
    y = 430
    for i, (t, body) in enumerate(steps):
        card(d, [180, y, 1820, y + 230], fill=WARM_WHITE if i % 2 == 0
             else LILAC)
        numbered_badge(d, 320, y + 115, i + 1, r=62,
                       bg=CORAL if i % 2 == 0 else INDIGO_MID)
        d.text((460, y + 80), t, font=F_SANS_B(50), fill=INDIGO,
               anchor="lm")
        para(d, (460, y + 130), body, F_SANS(38), INK, 1280, line_h=52)
        y += 270

    pill(d, (520, 1830), "Free how-to guide included in your download",
         fg=INDIGO, bg=LILAC, size=42)
    return img


def make_two_versions():
    photo = dim(cover(ASSETS / "bg_studio.jpg"), 95)
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 170), "TWO WORKBOOKS INCLUDED", font=F_SERIF(94),
           fill=WHITE, anchor="mm")
    d.text((S / 2, 280), "Learn from the sample. Make it yours with the "
           "blank.", font=F_SANS_B(44), fill=LILAC, anchor="mm")

    for i, (title, tag, rows) in enumerate([
            ("FILLED SAMPLE", "30 posts · 22 captions · 6 campaigns",
             ["Worked example for a real brand",
              "Every tab filled with data",
              "See how the formulas work",
              "Explore before you type"]),
            ("BLANK TEMPLATE", "clean input cells · same formulas",
             ["Same 43 tabs, no sample data",
              "Add your own platforms and voice",
              "All calculations ready",
              "Start fresh any time"])]):
        x = 160 + i * 880
        card(d, [x, 420, x + 760, 1320], fill=WHITE)
        d.rounded_rectangle([x, 420, x + 760, 580], radius=36,
                            fill=INDIGO_MID if i == 0 else CORAL)
        d.rectangle([x, 530, x + 760, 580],
                    fill=INDIGO_MID if i == 0 else CORAL)
        d.text((x + 380, 500), title, font=F_SANS_B(52), fill=WHITE,
               anchor="mm")
        d.text((x + 380, 650), tag, font=F_SANS_B(32), fill=GREY,
               anchor="mm")
        y = 740
        for row in rows:
            check_icon(d, x + 90, y + 26, r=22,
                       color=INDIGO_MID if i == 0 else CORAL, width=8)
            d.text((x + 140, y), row, font=F_SANS(36), fill=INK,
                   anchor="lm")
            y += 100
        pill(d, (x + 230, 1180), ".XLSX FILE", fg=INDIGO, bg=LILAC,
             size=36)

    soft_panel(photo, [220, 1420, 1780, 1720], radius=50, alpha=135)
    d.text((S / 2, 1510), "Instant download  ·  Yours to keep  ·  "
           "Re-download any time", font=F_SANS_B(46), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 1620), "Opens in Microsoft Excel, LibreOffice Calc "
           "and Google Sheets", font=F_SANS(40), fill=LILAC, anchor="mm")
    return photo


def make_specs():
    img = vgrad(INDIGO, INDIGO_DARK)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 160), "THE SPECS", font=F_SERIF(110), fill=WHITE,
           anchor="mm")
    d.text((S / 2, 280), "Built to work in the spreadsheet you already "
           "have", font=F_SANS_B(46), fill=LILAC, anchor="mm")

    specs = [
        ("FORMAT", ".xlsx - Excel 2010 and later"),
        ("ALSO WORKS IN", "LibreOffice Calc, Google Sheets"),
        ("TABS", "43 connected worksheets"),
        ("SECURITY", "Protected sheets - password in the guide"),
        ("FORMULAS", "Classic formulas only - no macros, no add-ins"),
        ("CALENDAR", "600 rows - a full year of content"),
        ("PRINTABLES", "Content brief + weekly schedule"),
        ("SAMPLE DATA", "30 posts · 22 captions · 6 campaigns"),
        ("LICENSE", "Personal use - copies for your own business"),
        ("DELIVERY", "Instant digital download - no shipping"),
    ]
    y = 420
    for i, (k, v) in enumerate(specs):
        x = 160 + (i % 2) * 900
        yy = y + (i // 2) * 250
        card(d, [x, yy, x + 820, yy + 200], fill=(48, 34, 96))
        d.text((x + 50, yy + 65), k, font=F_SANS_B(34), fill=LILAC,
               anchor="lm")
        para(d, (x + 50, yy + 115), v, F_SANS(34), WHITE, 720, line_h=44)

    d.text((S / 2, 1880), "Instant download after purchase",
           font=F_SANS_B(48), fill=LILAC, anchor="mm")
    return img


def make_perfect_for():
    photo = scrim(dim(cover(ASSETS / "bg_phone.jpg"), 110), side="bottom")
    d = ImageDraw.Draw(photo)
    d.text((S / 2, 170), "PERFECT FOR", font=F_SERIF(110), fill=WHITE,
           anchor="mm")

    people = [
        ("CREATORS", "posting consistently\nwithout living in "
         "the apps"),
        ("SMALL BUSINESSES", "running the shop AND\nthe content - "
         "in one place"),
        ("SOCIAL MANAGERS", "juggling clients, campaigns\nand reporting "
         "deadlines"),
        ("MAKERS & SELLERS", "turning studio moments\ninto a month of "
         "posts"),
    ]
    for i, (t, body) in enumerate(people):
        x = 150 + (i % 2) * 900
        y = 420 + (i // 2) * 540
        card(d, [x, y, x + 800, y + 460], fill=WHITE)
        d.text((x + 400, y + 100), t, font=F_SANS_B(44), fill=INDIGO,
               anchor="mm")
        para(d, (x + 70, y + 190), body.replace("\n", " "), F_SANS(38),
             INK, 660, line_h=54, center=True)

    d.text((S / 2, 1660), "Whoever posts - the system is the same",
           font=F_SANS_B(52), fill=WHITE, anchor="mm")
    d.text((S / 2, 1770), "Plan · Create · Publish · Measure",
           font=F_SANS_B(44), fill=CORAL, anchor="mm")
    return photo


def make_content_that_works():
    img = vgrad(CORAL_SOFT, WARM_WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 300), "PLAN ONCE.", font=F_SERIF(140), fill=INDIGO,
           anchor="mm")
    d.text((S / 2, 460), "POST EVERYWHERE.", font=F_SERIF(140), fill=CORAL,
           anchor="mm")
    d.text((S / 2, 620), "MEASURE EVERYTHING.", font=F_SERIF(120),
           fill=INDIGO_MID, anchor="mm")

    feats = [
        ("REPURPOSING QUEUE", "One reel, five new lives - track every "
         "cut-down, crop and rewrite."),
        ("AB TEST LOG", "Test the hook, the CTA, the hour. Write down "
         "what won and act on it."),
        ("TREND RADAR", "What is moving right now - and whether it fits "
         "your voice before you jump."),
    ]
    y = 880
    for t, body in feats:
        card(d, [220, y, 1780, y + 250], fill=WHITE)
        d.text((300, y + 70), t, font=F_SANS_B(46), fill=INDIGO,
               anchor="lm")
        para(d, (300, y + 135), body, F_SANS(36), INK, 1380, line_h=48)
        y += 290

    d.text((S / 2, 1820), "Good content earns a second life - "
           "this makes sure it gets one.",
           font=F_SANS_B(40), fill=INDIGO, anchor="mm")
    return img


def make_faq():
    img = vgrad(WARM_WHITE, WHITE)
    d = ImageDraw.Draw(img)
    d.text((S / 2, 150), "QUICK ANSWERS", font=F_SERIF(100), fill=INDIGO,
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
        ("Will it work for my platforms?", "Yes - the platform tabs cover "
         "Instagram, TikTok, Pinterest, YouTube and Facebook, and the "
         "lists are editable."),
        ("Is this a physical product?", "No - it is an instant digital "
         "download. Nothing ships."),
    ]
    y = 300
    for i, (q, a) in enumerate(qa):
        card(d, [160, y, 1840, y + 215], fill=WARM_WHITE if i % 2 == 0
             else LILAC)
        d.text((240, y + 65), "Q", font=F_SANS_B(52), fill=CORAL,
               anchor="lm")
        d.text((330, y + 65), q, font=F_SANS_B(46), fill=INDIGO,
               anchor="lm")
        para(d, (330, y + 128), a, F_SANS(38), INK, 1420, line_h=50)
        y += 255
    d.text((S / 2, 1900), "Still stuck? Message us any time - we "
           "usually reply within a day.", font=F_SANS_B(42),
           fill=INDIGO_MID, anchor="mm")
    return img


def make_thankyou():
    img = vgrad(INDIGO, (22, 14, 44))
    d = ImageDraw.Draw(img)
    for r in (1400, 1100, 800):
        d.ellipse([-r // 2, S - r // 2, r, S + r], outline=(88, 74, 150),
                  width=24)
    d.text((S / 2, 420), "PLAN THE CONTENT.", font=F_SERIF(100),
           fill=WHITE, anchor="mm")
    d.text((S / 2, 565), "GROW THE AUDIENCE.", font=F_SERIF(100),
           fill=CORAL, anchor="mm")
    d.text((S / 2, 710), "KNOW WHAT WORKED.", font=F_SERIF(100),
           fill=LILAC, anchor="mm")
    d.line([(700, 870), (1300, 870)], fill=LILAC_DEEP, width=5)
    d.text((S / 2, 1010), "Thank you for shopping with us",
           font=F_SANS_B(58), fill=OAT, anchor="mm")
    d.text((S / 2, 1110), "Social Media Content Planner  ·  43-tab "
           "Excel spreadsheet", font=F_SANS(44), fill=LILAC, anchor="mm")
    pill(d, (600, 1290), "LOVE IT? A REVIEW MAKES OUR DAY",
         fg=INDIGO, bg=OAT, size=42)
    d.text((S / 2, 1550), "Questions about the spreadsheet? Message "
           "the shop any time.", font=F_SANS(40), fill=LILAC_DEEP,
           anchor="mm")
    d.text((S / 2, 1880), "For personal use only  ·  Not for resale",
           font=F_SANS(36), fill=(140, 128, 190), anchor="mm")
    return img


# ------------------------------------------------------------ listing copy
TITLES = [
    "Social Media Content Planner Spreadsheet, Content Calendar Excel, "
    "Caption & Hashtag Bank, Instagram TikTok Planner, Instant Download",
    "Content Calendar Excel Template, Social Media Planner, 12-Month "
    "Calendar, Analytics Tracker, Marketing Planner, Digital Download",
    "Social Media Planner for Excel, Content Calendar, Caption Bank, "
    "Hashtag Tracker, Campaign Planner, Analytics, Instant Download",
    "Content Planner Spreadsheet, Instagram TikTok Pinterest Planner, "
    "Social Media Calendar, Analytics Dashboard, Excel Template",
    "Social Media Content Calendar Excel, Marketing Planner for Small "
    "Business, Analytics & Reports, Printable Briefs, Digital Download",
]

TAGS = [
    "social media planner",
    "content calendar",
    "content planner",
    "instagram planner",
    "social media excel",
    "planner excel",
    "tiktok planner",
    "hashtag tracker",
    "marketing planner",
    "small business",
    "content creator",
    "analytics tracker",
    "social media kit",
]

DESCRIPTION = """\
SOCIAL MEDIA CONTENT CALENDAR & ANALYTICS PLANNER
43-tab Excel spreadsheet  ·  Filled sample + blank template  ·  Instant download

Plan a month of content in an afternoon - and know what worked.

This workbook is a small content studio in one file: a master calendar,
per-platform planners, swipe files for ideas and words, campaign and launch
trackers, and the analytics that tell you what to make more of. Everything is
wired together - plan one post and every dashboard moves.

WHAT YOU GET

  1. Social Media Content Planner.xlsx
     The full planner filled with a worked example for a small handmade
     brand - 30 scheduled posts, 22 captions, 6 campaigns, live analytics
     and a monthly report. Every formula, drop down and dashboard works
     exactly as it will with your own content.

  2. Social Media Content Planner (Blank).xlsx
     The same 43-tab workbook with every register empty - start fresh
     without deleting anything.

  3. How-to guide
     Set up in under an hour, then a weekly routine that runs itself.
     Includes the sheet protection password.

THE TABS

  PLAN    Content Calendar (600 rows), Month View, Workflow, Idea Bank,
          Seasonal Planner, Campaigns, Launch Planner
  CREATE  Caption Bank, Hashtag Bank, Brand Voice, Assets, Repurposing
  PUBLISH Instagram, TikTok, Pinterest, YouTube and Facebook planners
  GROW    Influencers, UGC Tracker, Competitors, Trends, Goals
  MEASURE Analytics, Performance, AB Tests, Ads, Budget, Reports
  START   Start Here, Dashboard, Annual Dashboard, Settings, Lists,
          Team, Tasks, Compliance, Help - plus two printables

HOW IT WORKS

  Every drop down is fed from one Lists tab you can edit. Content IDs,
  weekdays, engagement rates, countdowns and budget variances calculate
  themselves. Statuses drive the dashboards, so the numbers are never a
  separate job. Printable content briefs and a weekly schedule are set to
  print on one page.

PERFECT FOR

  Creators who post consistently, small businesses who run the shop AND the
  content, social media managers juggling clients and reporting deadlines,
  and makers who want to turn studio moments into a month of posts.

THE SPECS

  Format        .xlsx - Excel 2010 and later
  Also works in LibreOffice Calc, Google Sheets
  Tabs          43 connected worksheets
  Formulas      Classic formulas only - no macros, no add-ins
  Security      Protected sheets (password in the guide); input cells
                stay unlocked
  Printables    Content brief + weekly schedule
  Language      English, currency symbol changeable in one click
  License       Personal use - make copies for your own business
  Delivery      Instant digital download - nothing ships

HOW TO DOWNLOAD

  This is a digital product. After payment you will find your files under
  Etsy > Purchases and reviews > Downloads. If anything goes wrong,
  message the shop and we will help.

  Thank you for shopping with us - and may your calendar always be full.
"""

HOW_TO = """\
HOW TO USE YOUR SOCIAL MEDIA CONTENT PLANNER
============================================

WHAT IS IN THE FOLDER

  * Social Media Content Planner.xlsx
      The full planner, filled with a worked example. Explore this one
      first - every formula, drop down and dashboard is live.

  * Social Media Content Planner (Blank).xlsx
      The same workbook with empty registers. Start here once you know
      your way around.

  * HOW TO RUN.txt
      This guide.

FIRST HOUR: SET UP

  1. Open the workbook in Excel (2010 or newer), LibreOffice Calc or
     upload it to Google Sheets.
  2. Start on 'Start Here' - it walks you through the tabs.
  3. Go to 'Settings': brand name, currency, planning year, default
     owner and your average order value.
  4. Fill 'Accounts' with the profiles you post from.
  5. Define 4-6 'Content Pillars' - the themes everything hangs on.
  6. Sketch 3-5 'Audience Personas' like real people.
  7. Check the 'Lists' tab - every drop down in the workbook reads
     from it. Edit the words there and the change applies everywhere.

EVERY WEEK (ABOUT 20 MINUTES)

  1. Open the Dashboard. The queue shows what is waiting to go live.
  2. Fill the Content Calendar - one row per post. IDs and weekdays
     fill themselves; pick pillar, platform, owner and status from the
     drop downs.
  3. Write or pull captions from the Caption Bank and tag the hashtag
     sets you will use.
  4. Post natively on each platform, then log the numbers on the
     'Performance' and 'Analytics' tabs within a week.
  5. First of the month: open 'Reports', write the story beside the
     numbers, and copy the summary straight into an email.

PROTECTION

  Every sheet is protected so formula cells cannot be overwritten by
  accident. The password is: premium
  (Review > Unprotect Sheet if you need to change something structural.
  Cream cells are input cells and stay editable without unprotecting.)

TROUBLESHOOTING

  * A drop down is empty - add items to the matching Lists column.
  * A grey column is blank - its input columns are still empty.
  * You see #REF! after deleting a row - undo. IDs are calculated from
    row order; deleting rows in the middle renumbers the rest.
  * Google Sheets looks different - formulas still work; some
    formatting shifts are normal.

LICENSE

  Personal use. Make copies for your own business. Please do not
  resell or redistribute the files.

Questions? Message the shop any time - we usually reply within a day.
"""

BULLETS = [
    "43-tab social media content planner: plan, post and measure",
    "600-row content calendar with automatic IDs and status lookups",
    "Caption bank, hashtag bank and idea bank - write once, reuse forever",
    "Instagram, TikTok, Pinterest, YouTube and Facebook planners",
    "Campaigns, launches and seasonal moments with live budgets",
    "Analytics dashboard - engagement, revenue and best posting times",
    "AB tests, ads and repurposing queue in one workbook",
    "Printable content brief and weekly schedule",
    "Monthly report writes its own summary email",
    "Filled sample + blank template included",
    "Excel 2010+, LibreOffice and Google Sheets",
    "No macros - protected sheets, easy to use",
    "Instant digital download",
]


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
        + "\n".join(f"- {b}" for b in BULLETS),
        encoding="utf-8")


# --------------------------------------------------------------- assembly
IMAGE_BUILDERS = [
    ("01-cover.jpg", make_cover),
    ("02-whats-inside.jpg", make_whats_inside),
    ("03-43-tabs.jpg", make_tabs),
    ("04-dashboard.jpg", make_dashboard),
    ("05-content-calendar.jpg", make_calendar),
    ("06-month-view.jpg", make_month_view),
    ("07-caption-hashtag-banks.jpg", make_banks),
    ("08-platform-planners.jpg", make_platforms),
    ("09-campaigns-launches.jpg", make_campaigns),
    ("10-analytics.jpg", make_analytics),
    ("11-printables.jpg", make_printables),
    ("12-how-it-works.jpg", make_how_it_works),
    ("13-two-versions.jpg", make_two_versions),
    ("14-specs.jpg", make_specs),
    ("15-perfect-for.jpg", make_perfect_for),
    ("16-content-that-works.jpg", make_content_that_works),
    ("17-faq.jpg", make_faq),
    ("18-thank-you.jpg", make_thankyou),
]


def main() -> int:
    if not FILLED.exists() or not BLANK.exists():
        print("FAIL: build both workbooks first:")
        print("  python build_social_media_workbook.py")
        print("  python build_social_media_workbook.py --blank "
              "-o \"output/Social Media Content Planner (Blank).xlsx\"")
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
    zip_path = DOWNLOAD / "social-media-content-planner-etsy-kit.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in (IMG_OUT, COPY_OUT, SHEETS_OUT):
            for f in sorted(folder.iterdir()):
                zf.write(
                    f,
                    f"social-media-content-planner-etsy-kit/"
                    f"{folder.name}/{f.name}")
    print(f"\nWrote {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.1f} "
          f"MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
