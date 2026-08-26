"""Novality store — Travel Planner v2 : Etsy listing image generator.

Draws 12 branded marketing images (2000x2000 + Pinterest + shop avatar)
programmatically with Pillow: real spreadsheet mockups, feature tiles,
how-it-works steps and AI-generated background art (assets/hero-bg.png).
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")
ASSETS = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- palette --
NAVY   = (29, 53, 87)
NAVY_D = (18, 34, 56)
TEAL   = (42, 157, 143)
TEAL_D = (28, 118, 106)
SAND   = (233, 196, 106)
SAND_D = (196, 159, 66)
CORAL  = (231, 111, 81)
CORAL_D= (198, 84, 56)
CREAM  = (241, 250, 238)
WHITE  = (255, 255, 255)
INPUTY = (255, 248, 225)
CALCB  = (223, 234, 246)
LINE   = (180, 199, 207)
GRAYTX = (95, 116, 112)
SHADOW = (16, 30, 49)

# ------------------------------------------------------------------- fonts --
FD = os.path.join(ASSETS, "fonts")

def F(size, weight="Bold"):
    p = os.path.join(FD, f"HankenGrotesk-{weight}.otf")
    return ImageFont.truetype(p, size)

def FR(size):
    return ImageFont.truetype(os.path.join(FD, "FredokaOne-Regular.ttf"), size)

def SYM(size, bold=False):
    return ImageFont.truetype(os.path.join(
        FD, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

# ----------------------------------------------------------------- helpers --
def fit_font(text, base, weight, max_w, min_size=18):
    """Shrink font size until text fits max_w. Returns font."""
    s = base
    while s > min_size:
        f = F(s, weight)
        if f.getlength(text) <= max_w:
            return f
        s -= 2
    return F(min_size, weight)

def txt(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def txt_c(d, cx, y, s, font, fill, anchor="mm"):
    d.text((cx, y), s, font=font, fill=fill, anchor=anchor)

def tracked(d, cx, y, s, font, fill, tracking=14):
    widths = [font.getlength(c) for c in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for c, w in zip(s, widths):
        d.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += w + tracking

def tracked_l(d, x, y, s, font, fill, tracking=14):
    for c in s:
        d.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += font.getlength(c) + tracking

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def shadow_rrect(img, d, box, r, fill, outline=None, width=1, blur=18, alpha=70):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0 + 8, y0 + 14, x1 + 8, y1 + 14), radius=r,
                         fill=(13, 24, 40, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    rrect(d, box, r, fill, outline, width)
    return d

def check(d, cx, cy, s, color=TEAL, w=8):
    d.line([(cx - s * 0.9, cy + s * 0.05), (cx - s * 0.25, cy + s * 0.75),
            (cx + s * 0.95, cy - s * 0.65)], fill=color, width=w, joint="curve")

def pill(d, cx, cy, text, font, pad_x=34, fill=WHITE, fg=NAVY, outline=None,
         width=3, tracked_=6):
    tw = sum(font.getlength(c) for c in text) + tracked_ * (len(text) - 1)
    w = tw + pad_x * 2
    h = font.size + pad_x * 1.3
    rrect(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2,
          fill=fill, outline=outline, width=width)
    tracked(d, cx, cy, text, font, fg, tracked_)
    return w

def icon_badge(d, cx, cy, r, glyph, bg=TEAL, fg=WHITE, size=None):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    f = SYM(size or int(r * 1.15))
    txt_c(d, cx, cy, glyph, f, fg, anchor="mm")

def stars(d, cx, cy, n=5, gap=18, size=44, color=SAND):
    f = SYM(size)
    w = f.getlength("★") + gap
    total = w * n - gap
    x = cx - total / 2 + w / 2
    for _ in range(n):
        txt_c(d, x, cy, "★", f, color, anchor="mm")
        x += w

def wrap(s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if font.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------- page chrome/footer --
def footer(img, d, S=2000):
    h = 96
    d.rectangle((0, S - h, S, S), fill=NAVY)
    d.rectangle((0, S - h - 6, S, S - h), fill=SAND)
    txt(d, (70, S - h / 2), "✈", SYM(40, bold=True), SAND, anchor="lm")
    tracked_l(d, 130, S - h / 2, "TRAVEL PLANNER V2  —  NOVALITY STORE",
              F(30, "Bold"), CREAM, 5)
    tracked(d, S - 70, S - h / 2, "DIGITAL SPREADSHEET • INSTANT DOWNLOAD",
            F(28, "SemiBold"), SAND, 4)

def header(img, d, title, sub, S=2000, y=150):
    f_title = FR(148)
    txt_c(d, S / 2, y, title, f_title, NAVY, anchor="mm")
    under = y + 108
    d.rounded_rectangle((S / 2 - 90, under, S / 2 + 90, under + 12), radius=6,
                        fill=CORAL)
    txt_c(d, S / 2, under + 78, sub, F(58, "SemiBold"), TEAL_D, anchor="mm")
    return under + 130

# -------------------------------------------------------- spreadsheet mock --
def sheet_card(img, d, x, y, w, banner, headers, col_ws, rows, total=None,
               row_h=66, header_h=58, banner_h=100, cell_font=None,
               head_font=None, banner_font=None, r=30, tick_col=None):
    """rows: list of list of (text, kind) where kind in 'in','calc','plain'.
    total: list of (text, kind) for navy TOTAL row. Returns bottom y."""
    cf = cell_font or F(32, "Medium")
    hf = head_font or F(29, "SemiBold")
    bf = banner_font or F(42, "Bold")
    n = len(rows) + (1 if total else 0)
    h = banner_h + header_h + n * row_h + 10
    d = ImageDraw.Draw(img)
    d = shadow_rrect(img, d, (x, y, x + w, y + h), r, NAVY)
    # body (white, rounded bottom)
    d.rounded_rectangle((x + 2, y + banner_h, x + w - 2, y + h - 2), radius=r,
                        fill=WHITE)
    d.rectangle((x + 2, y + banner_h, x + w - 2, y + banner_h + r + 4), fill=WHITE)
    # banner text
    txt(d, (x + 34, y + banner_h / 2 - 6), banner, bf, WHITE, anchor="lm")
    txt(d, (x + w - 34, y + banner_h / 2 - 6), "EXCEL", F(26, "Bold"),
        SAND, anchor="rm")
    # header row
    d.rectangle((x + 2, y + banner_h, x + w - 2, y + banner_h + header_h),
                fill=TEAL)
    cols = [x + 2]
    for cw in col_ws:
        cols.append(cols[-1] + int((w - 4) * cw))
    for i, htxt in enumerate(headers):
        f = fit_font(htxt, 29, "SemiBold", cols[i + 1] - cols[i] - 26, 20)
        txt(d, (cols[i] + 16, y + banner_h + header_h / 2), htxt, f, WHITE,
            anchor="lm")
    # body rows
    ry = y + banner_h + header_h
    all_rows = list(rows) + ([total] if total else [])
    for ri, row in enumerate(all_rows):
        is_total = total is not None and ri == len(all_rows) - 1
        if is_total:
            d.rectangle((x + 2, ry, x + w - 2, ry + row_h), fill=NAVY)
        elif ri % 2 == 1:
            d.rectangle((x + 2, ry, x + w - 2, ry + row_h), fill=CREAM)
        for ci, cell in enumerate(row):
            text, kind = cell
            cx0, cx1 = cols[ci], cols[ci + 1]
            pad = 18
            if kind == "in":
                d.rectangle((cx0 + 6, ry + 8, cx1 - 6, ry + row_h - 8),
                            fill=INPUTY)
            elif kind == "calc" and not is_total:
                d.rectangle((cx0 + 6, ry + 8, cx1 - 6, ry + row_h - 8),
                            fill=CALCB)
            fg = WHITE if is_total else (NAVY if kind in ("calc", "in") else GRAYTX)
            weight = "Bold" if (is_total or kind == "calc") else "Medium"
            f = fit_font(text, 33 if not is_total else 34, weight,
                         cx1 - cx0 - pad * 2 - 6, 18)
            txt(d, (cx0 + pad, ry + row_h / 2), text, f, fg, anchor="lm")
        ry += row_h
    d.line([(x + 2, ry), (x + w - 2, ry)], fill=LINE, width=2)
    return ry + 8

def callout(img, d, x, y, w, glyph, title, body, accent=TEAL):
    d = shadow_rrect(img, d, (x, y, x + w, y + 150), 26, WHITE, LINE, 2,
                     blur=12, alpha=55)
    icon_badge(d, x + 74, y + 75, 44, glyph, bg=accent)
    f1 = fit_font(title, 40, "Bold", w - 190, 26)
    txt(d, (x + 142, y + 48), title, f1, NAVY, anchor="lm")
    f2 = fit_font(body, 31, "Medium", w - 190, 18)
    txt(d, (x + 142, y + 105), body, f2, GRAYTX, anchor="lm")

def bg_canvas(color=CREAM, S=2000):
    img = Image.new("RGB", (S, S), color)
    return img, ImageDraw.Draw(img)

def deco_dots(d, S):
    for gx, gy, c in ((120, 150, SAND), (S - 120, 150, CORAL), (90, S - 220, TEAL),
                      (S - 90, S - 220, SAND)):
        d.ellipse((gx - 14, gy - 14, gx + 14, gy + 14), fill=c)

# ============================================================== 01 COVER ====
def img_cover():
    S = 2000
    bg = Image.open(os.path.join(ASSETS, "hero-bg.png")).resize((S, S),
                                                               Image.LANCZOS)
    img = bg
    ov = Image.new("RGB", (S, S), NAVY)
    img = Image.blend(img, ov, 0.38)
    # center scrim
    scrim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.ellipse((150, 520, S - 150, 1560), fill=(16, 30, 50, 130))
    scrim = scrim.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")
    d = ImageDraw.Draw(img)

    # kicker
    pill(d, S / 2, 640, "THE COMPLETE TRIP PLANNING SPREADSHEET", F(36, "SemiBold"),
         fill=(29, 53, 87), fg=SAND, pad_x=44)

    # big title with soft shadow
    t1, t2 = "TRAVEL", "PLANNER"
    f_big = FR(318)
    for i, (t, cy) in enumerate(((t1, 850), (t2, 1128))):
        d.text((S / 2 + 10, cy + 14), t, font=f_big, fill=(14, 26, 44),
               anchor="mm")
        txt_c(d, S / 2, cy, t, f_big, CREAM if i == 0 else SAND, anchor="mm")

    # v2 chip
    rrect(d, (S / 2 - 470, 1280, S / 2 - 330, 1336), 28, fill=CORAL)
    txt_c(d, S / 2 - 400, 1308, "V 2.0", F(34, "Bold"), WHITE, anchor="mm")
    tracked(d, S / 2 + 60, 1308, "29 SMART SHEETS — ONE WORKBOOK",
            F(38, "SemiBold"), CREAM, 6)

    txt_c(d, S / 2, 1400,
          "Budget  •  Itinerary  •  Packing  •  Expenses  •  Maps  •  Memories",
          F(52, "Regular"), (214, 228, 238), anchor="mm")

    # pills
    pw = 520
    pill(d, S / 2 - pw, 1545, "MICROSOFT EXCEL", F(34, "Bold"), fill=TEAL,
         fg=WHITE)
    pill(d, S / 2, 1545, "INSTANT DOWNLOAD", F(34, "Bold"), fill=SAND, fg=NAVY)
    pill(d, S / 2 + pw, 1545, "FORMULAS PROTECTED", F(34, "Bold"), fill=CORAL,
         fg=WHITE)

    txt(d, (S / 2, 1730), "✈", SYM(54, bold=True), SAND, anchor="mm")
    tracked(d, S / 2, 1810, "NOVALITY STORE", F(46, "Bold"), CREAM, 18)
    img.save(os.path.join(OUT, "01-cover.png"), optimize=True)

# ======================================================= 02 WHAT'S INSIDE ===
CATS = [
    ("✎", "PRE-TRIP PLANNING", "6 SHEETS",
     ["Destination Overview", "Budget Tracker", "Savings Goal", "Research & Ideas",
      "Visa & Documents", "Booking Log"], TEAL),
    ("✓", "PACKING & PREP", "4 SHEETS",
     ["Packing Checklist", "Weather Tracker", "Carry-On vs Checked",
      "Pre-Trip To-Do"], TEAL_D),
    ("✈", "ITINERARY & DAILY", "5 SHEETS",
     ["Daily Itinerary", "Hourly Schedule", "Route Planner", "Transportation Log",
      "Accommodation"], NAVY),
    ("$", "EXPENSE TRACKING", "4 SHEETS",
     ["Daily Expense Log", "Currency Converter", "Tipping Guide",
      "Trip Cost Summary"], CORAL),
    ("☀", "FOOD & ACTIVITIES", "4 SHEETS",
     ["Restaurant Wishlist", "Activity Planner", "Local Phrases",
      "Etiquette Notes"], SAND_D),
    ("★", "EXTRAS & MEMORIES", "5 SHEETS",
     ["Emergency Contacts", "Travel Journal", "Ratings & Reviews",
      "Souvenir List", "Wi-Fi & Passwords"], CORAL_D),
]

def img_whats_inside():
    S = 2000
    img, d = bg_canvas()
    deco_dots(d, S)
    y0 = header(img, d, "WHAT'S INSIDE", "29 beautiful sheets that plan the whole trip")
    cw, ch, gap = 586, 640, 24
    x0 = (S - 3 * cw - 2 * gap) / 2
    y_top = y0 + 30
    for i, (glyph, name, count, items, color) in enumerate(CATS):
        cx = x0 + (i % 3) * (cw + gap)
        cy = y_top + (i // 3) * (ch + gap)
        d = shadow_rrect(img, d, (cx, cy, cx + cw, cy + ch), 30, WHITE, LINE, 2)
        d.rectangle((cx, cy, cx + cw, cy + 120), fill=color)
        d.rounded_rectangle((cx, cy, cx + cw, cy + 130), radius=30, fill=color)
        d.rectangle((cx, cy + 90, cx + cw, cy + 130), fill=color)
        icon_badge(d, cx + 74, cy + 62, 36, glyph, bg=WHITE, fg=color)
        f_name = fit_font(name, 40, "Bold", cw - 190, 24)
        txt(d, (cx + 130, cy + 62), name, f_name, WHITE, anchor="lm")
        rrect(d, (cx + cw - 150, cy + 28, cx + cw - 28, cy + 92), 32, fill=CREAM)
        txt_c(d, cx + cw - 89, cy + 60, count, F(30, "Bold"), color, anchor="mm")
        iy = cy + 170
        for it in items:
            check(d, cx + 52, iy, 13, color=TEAL, w=7)
            f = fit_font(it, 36, "Medium", cw - 130, 22)
            txt(d, (cx + 88, iy), it, f, NAVY_D, anchor="lm")
            iy += 74
    footer(img, d, S)
    img.save(os.path.join(OUT, "02-whats-inside.png"), optimize=True)

# ================================================== 03 BUDGET TRACKER =======
def showcase(title, sub, mock_fn, callouts, fname, accent=TEAL):
    S = 2000
    img, d = bg_canvas()
    deco_dots(d, S)
    header(img, d, title, sub, S)
    mock_fn(img, d)
    cx = 1330
    cy = 640
    for glyph, t, b, col in callouts:
        callout(img, d, cx, cy, 600, glyph, t, b, col)
        cy += 190
    footer(img, d, S)
    img.save(os.path.join(OUT, fname), optimize=True)

def mock_budget(img, d):
    sheet_card(img, d, 90, 560, 1140, "BUDGET TRACKER",
               ["CATEGORY", "ESTIMATED", "ACTUAL", "DIFFERENCE"],
               [0.34, 0.22, 0.22, 0.22],
               [[("Flights", "in"), ("$1,200", "in"), ("$1,184", "in"), ("+$16", "calc")],
                [("Hotels", "in"), ("$900", "in"), ("$940", "in"), ("⚠ −$40", "calc")],
                [("Food & dining", "in"), ("$600", "in"), ("$512", "in"), ("+$88", "calc")],
                [("Activities", "in"), ("$450", "in"), ("$380", "in"), ("+$70", "calc")],
                [("Shopping", "in"), ("$250", "in"), ("$310", "in"), ("⚠ −$60", "calc")],
                [("Insurance", "in"), ("$120", "in"), ("$120", "in"), ("$0", "calc")]],
               total=[("TOTAL", "plain"), ("$3,520", "plain"), ("$3,446", "plain"),
                      ("+$74 ✓", "plain")],
               row_h=88)

def img_budget():
    showcase("BUDGET TRACKER", "Know exactly where the money goes",
             mock_budget,
             [("$", "Totals add themselves", "Estimated vs actual, variance & % used", TEAL),
              ("⚠", "Overspending alerts", "Flags any category over budget", CORAL),
              ("✓", "Status at a glance", "On track or over — no math needed", NAVY),
              ("★", "10 trip categories", "Flights, hotels, food, tours, shopping…", SAND_D)],
             "03-budget-tracker.png")

# ================================================== 04 ITINERARY ============
def mock_itinerary(img, d):
    sheet_card(img, d, 90, 560, 1140, "DAY-BY-DAY ITINERARY",
               ["DAY", "TIME", "ACTIVITY", "TRANSPORT"],
               [0.10, 0.18, 0.47, 0.25],
               [[("1", "in"), ("Morning", "in"), ("Land & check in to hotel", "in"), ("Taxi", "in")],
                [("1", "in"), ("Afternoon", "in"), ("Old Town walking tour", "in"), ("Walk", "in")],
                [("1", "in"), ("Evening", "in"), ("Sunset at the harbor", "in"), ("Metro", "in")],
                [("2", "in"), ("Morning", "in"), ("Museum + gallery pass", "in"), ("Bus", "in")],
                [("2", "in"), ("Evening", "in"), ("Riverside dinner cruise", "in"), ("Ferry", "in")],
                [("3", "in"), ("Morning", "in"), ("Day trip to the hills", "in"), ("Train", "in")]],
               total=[("80", "plain"), ("slots", "plain"),
                      ("ready for your whole trip", "plain"), ("", "plain")],
               row_h=88)

def img_itinerary():
    showcase("DAILY ITINERARY", "Every day planned to the hour",
             mock_itinerary,
             [("✈", "80 time slots ready", "Day, time, activity, address & cost", TEAL),
              ("➜", "Transport dropdowns", "Taxi, metro, ferry, walk & more", NAVY),
              ("$", "Planned-cost total", "Itinerary costs sum automatically", CORAL),
              ("⏱", "Hourly grid + route map", "7-day schedule & sketchable map", SAND_D)],
             "04-itinerary.png")

# ================================================== 05 PACKING ==============
def mock_packing(img, d):
    rows = [[("Passport & documents", "in"), ("1", "in"), ("✓", "calc")],
            [("Phone + power bank", "in"), ("1", "in"), ("✓", "calc")],
            [("T-shirts & tops", "in"), ("5", "in"), ("✓", "calc")],
            [("Walking shoes", "in"), ("1", "in"), ("—", "plain")],
            [("Rain jacket", "in"), ("1", "in"), ("—", "plain")],
            [("Sunscreen SPF 50", "in"), ("1", "in"), ("—", "plain")]]
    bottom = sheet_card(img, d, 90, 560, 1140, "PACKING CHECKLIST",
                        ["ITEM", "QTY", "PACKED?"], [0.58, 0.18, 0.24], rows,
                        row_h=88)
    # progress bar under card
    bx0, bx1, by = 130, 1190, bottom + 60
    txt(d, (bx0, by - 34), "PACKING PROGRESS", F(32, "Bold"), NAVY, anchor="lm")
    txt(d, (bx1, by - 34), "17 OF 25", F(32, "Bold"), TEAL_D, anchor="rm")
    rrect(d, (bx0, by, bx1, by + 44), 22, fill=WHITE, outline=LINE, width=3)
    rrect(d, (bx0 + 6, by + 6, bx0 + 6 + (bx1 - bx0 - 12) * 0.68, by + 38), 16,
          fill=TEAL)
    txt(d, (bx0 + (bx1 - bx0) / 2, by + 22), "68%", F(30, "Bold"), NAVY,
        anchor="mm")

def img_packing():
    showcase("SMART PACKING LIST", "59 items pre-loaded — just tick the boxes",
             mock_packing,
             [("✓", "Tick as you pack", "The progress bar fills itself", TEAL),
              ("✎", "6 smart categories", "Clothes, toiletries, tech, docs, meds…", NAVY),
              ("☀", "Weather planner", "Match outfits to the forecast", CORAL),
              ("➜", "Carry-on vs checked", "Two lists, side by side", SAND_D)],
             "05-packing.png")

# ================================================== 06 EXPENSES =============
def mock_expenses(img, d):
    sheet_card(img, d, 90, 560, 1140, "DAILY EXPENSE LOG",
               ["DATE", "ITEM", "SPENT", "HOME ($)" ],
               [0.14, 0.46, 0.20, 0.20],
               [[("Mar 2", "in"), ("Croissant & coffee", "in"), ("€8.50", "in"), ("$9.18", "calc")],
                [("Mar 2", "in"), ("Metro day ticket", "in"), ("€2.90", "in"), ("$3.13", "calc")],
                [("Mar 3", "in"), ("Museum entry", "in"), ("€17.00", "in"), ("$18.36", "calc")],
                [("Mar 3", "in"), ("Bistro dinner", "in"), ("€42.00", "in"), ("$45.36", "calc")],
                [("Mar 4", "in"), ("Market souvenirs", "in"), ("€23.50", "in"), ("$25.38", "calc")]],
               total=[("TOTAL", "plain"), ("auto-converted", "plain"),
                      ("", "plain"), ("$101.41", "plain")],
               row_h=86)
    # converter chip card
    bx, by = 90, 1500
    d = shadow_rrect(img, d, (bx, by, bx + 1140, by + 210), 30, NAVY)
    txt(d, (bx + 40, by + 60), "QUICK CONVERTER", F(34, "Bold"), SAND, anchor="lm")
    rrect(d, (bx + 40, by + 100, bx + 330, by + 166), 33, fill=INPUTY)
    txt_c(d, bx + 185, by + 133, "100 EUR", F(34, "Bold"), NAVY, anchor="mm")
    txt(d, (bx + 380, by + 133), "→", SYM(44, bold=True), SAND, anchor="lm")
    rrect(d, (bx + 460, by + 100, bx + 790, by + 166), 33, fill=TEAL)
    txt_c(d, bx + 625, by + 133, "$108.00", F(34, "Bold"), WHITE, anchor="mm")
    txt(d, (bx + 840, by + 133), "12 currencies built in", F(32, "Medium"),
        CREAM, anchor="lm")

def img_expenses():
    showcase("EXPENSE TRACKING", "Spend in any currency — totals convert themselves",
             mock_expenses,
             [("➜", "Type € ¥ £ ₩…", "Rows convert to your home currency", TEAL),
              ("$", "150-row log", "Date, category, item, payment & notes", NAVY),
              ("☀", "Tipping guide", "Customs for 12+ destinations", CORAL),
              ("★", "Spending by category", "Auto breakdown of every category", SAND_D)],
             "06-expenses.png")

# ================================================== 07 DASHBOARD ============
def mock_dashboard(img, d):
    # savings goal card
    bx, by = 90, 560
    d = shadow_rrect(img, d, (bx, by, bx + 1140, by + 380), 30, WHITE, LINE, 2)
    icon_badge(d, bx + 80, by + 90, 46, "★", bg=TEAL)
    txt(d, (bx + 150, by + 90), "SAVINGS GOAL", F(42, "Bold"), NAVY, anchor="lm")
    txt(d, (bx + 40, by + 165), "Target  $3,400    •    Saved so far  $2,108",
        F(34, "Medium"), GRAYTX, anchor="lm")
    rrect(d, (bx + 40, by + 210, bx + 1100, by + 260), 25, fill=CREAM)
    rrect(d, (bx + 46, by + 216, bx + 46 + (1100 - 46 - 6) * 0.62, by + 254), 19,
          fill=SAND)
    txt(d, (bx + 40, by + 320), "███████████░░░░░░░", SYM(46, bold=True), SAND,
        anchor="lm")
    txt(d, (bx + 560, by + 320), "62% funded", F(36, "Bold"), TEAL_D, anchor="lm")

    # trip cost summary card
    rows = [[("Estimated budget", "in"), ("$3,520", "calc")],
            [("Logged expenses", "in"), ("$2,975", "calc")],
            [("Transport booked", "in"), ("$1,184", "calc")],
            [("Accommodation", "in"), ("$940", "calc")],
            [("Souvenirs & gifts", "in"), ("$180", "calc")]]
    sheet_card(img, d, 90, 990, 1140, "TRIP COST SUMMARY",
               ["ONE DASHBOARD — EVERY TOTAL", "AMOUNT"], [0.68, 0.32], rows,
               total=[("REMAINING BUDGET", "plain"), ("$545 ✓ on track", "plain")],
               row_h=76, banner_h=96)

def img_dashboard():
    showcase("TOTALS THAT UPDATE THEMSELVES", "A dashboard that does the math",
             mock_dashboard,
             [("★", "Savings tracker", "Watch the bar fill as you save", SAND_D),
              ("$", "Trip cost summary", "Every sheet totals, one page", TEAL),
              ("✓", "Budget health", "Over / under at a single glance", NAVY),
              ("➜", "Zero formulas to write", "325 calculations, pre-built", CORAL)],
             "07-dashboard.png")

# ================================================== 08 FEATURES =============
FEATURES = [
    ("⚠", "Locked & protected", "325 formulas can't break — every sheet is guarded", TEAL),
    ("➜", "Dropdown menus", "Tick ✓ packed, set status, pick categories", NAVY),
    ("★", "Progress bars", "Savings, packing & to-do readiness fill as you go", SAND_D),
    ("$", "Auto currency", "12-currency converter — log spend in any money", CORAL),
    ("✎", "Print-ready pages", "Clean layouts for your travel folder or PDF", TEAL_D),
    ("✈", "Reuse every trip", "Duplicate the file — plan unlimited adventures", CORAL_D),
]

def img_features():
    S = 2000
    img, d = bg_canvas()
    deco_dots(d, S)
    header(img, d, "MADE TO BE EASY", "Thoughtful details throughout")
    cw, ch, gap = 586, 640, 24
    x0 = (S - 3 * cw - 2 * gap) / 2
    y_top = 590
    for i, (glyph, t, b, col) in enumerate(FEATURES):
        cx = x0 + (i % 3) * (cw + gap)
        cy = y_top + (i // 3) * (ch + gap)
        d = shadow_rrect(img, d, (cx, cy, cx + cw, cy + ch), 30, WHITE, LINE, 2)
        d.rounded_rectangle((cx, cy, cx + cw, cy + 26), radius=13, fill=col)
        icon_badge(d, cx + cw / 2, cy + 150, 84, glyph, bg=col)
        f1 = fit_font(t, 52, "Bold", cw - 60, 30)
        txt_c(d, cx + cw / 2, cy + 300, t, f1, NAVY, anchor="mm")
        lines = wrap(b, F(35, "Medium"), cw - 110)
        ly = cy + 370
        for ln in lines:
            txt_c(d, cx + cw / 2, ly, ln, F(35, "Medium"), GRAYTX, anchor="mm")
            ly += 52
    footer(img, d, S)
    img.save(os.path.join(OUT, "08-features.png"), optimize=True)

# ================================================== 09 HOW IT WORKS =========
STEPS = [
    ("1", "PURCHASE", "Check out securely here on Etsy — payment confirms instantly", TEAL),
    ("2", "DOWNLOAD", "Your .xlsx file + quick-start guide are ready in minutes", CORAL),
    ("3", "PLAN & GO", "Fill the yellow cells — every total updates itself", NAVY),
]

def img_how():
    S = 2000
    img, d = bg_canvas()
    deco_dots(d, S)
    header(img, d, "HOW IT WORKS", "From checkout to packed suitcase in 3 steps")
    cw, gap = 586, 24
    x0 = (S - 3 * cw - 2 * gap) / 2
    y_top = 640
    for i, (num, t, b, col) in enumerate(STEPS):
        cx = x0 + i * (cw + gap)
        cy = y_top
        d = shadow_rrect(img, d, (cx, cy, cx + cw, cy + 700), 30, WHITE, LINE, 2)
        d.ellipse((cx + cw / 2 - 90, cy + 70, cx + cw / 2 + 90, cy + 250),
                  fill=col)
        txt_c(d, cx + cw / 2, cy + 160, num, FR(120), WHITE, anchor="mm")
        f1 = fit_font(t, 56, "Bold", cw - 60, 30)
        txt_c(d, cx + cw / 2, cy + 330, t, f1, NAVY, anchor="mm")
        lines = wrap(b, F(36, "Medium"), cw - 100)
        ly = cy + 410
        for ln in lines:
            txt_c(d, cx + cw / 2, ly, ln, F(36, "Medium"), GRAYTX, anchor="mm")
            ly += 54
        if i < 2:
            ax = cx + cw + gap / 2
            d.line([(ax - 10, cy + 350), (ax + 10, cy + 350)], fill=SAND_D, width=8)
    # digital-product notice bar
    nb_y = 1520
    rrect(d, (250, nb_y, S - 250, nb_y + 150), 40, fill=NAVY)
    txt_c(d, S / 2, nb_y + 52, "DIGITAL PRODUCT — NO PHYSICAL ITEM IS SHIPPED",
          F(38, "Bold"), SAND, anchor="mm")
    txt_c(d, S / 2, nb_y + 106,
          "Needs Microsoft Excel (2016+, 365, Mac or web) — desktop recommended",
          F(31, "Medium"), CREAM, anchor="mm")
    footer(img, d, S)
    img.save(os.path.join(OUT, "09-how-it-works.png"), optimize=True)

# ================================================== 10 CTA / BRAND ==========
def img_cta():
    S = 2000
    bg = Image.open(os.path.join(ASSETS, "pattern-bg.png")).resize((S, S),
                                                                   Image.LANCZOS)
    ov = Image.new("RGB", (S, S), NAVY_D)
    img = Image.blend(bg, ov, 0.55)
    d = ImageDraw.Draw(img)
    txt_c(d, S / 2, 480, "Plan more.", FR(230), CREAM, anchor="mm")
    txt_c(d, S / 2, 740, "Stress less.", FR(230), SAND, anchor="mm")
    stars(d, S / 2, 990, 5, gap=26, size=64)
    txt_c(d, S / 2, 1110, "TRAVEL PLANNER v2 — the trip kit that thinks for you",
          F(56, "SemiBold"), (214, 228, 238), anchor="mm")
    pill(d, S / 2, 1290, "29 SHEETS  •  325 SMART FORMULAS  •  REUSABLE FOREVER",
         F(38, "Bold"), fill=CORAL, fg=WHITE, pad_x=46)
    txt(d, (S / 2, 1480), "✈", SYM(58, bold=True), SAND, anchor="mm")
    tracked(d, S / 2, 1580, "NOVALITY STORE", F(52, "Bold"), CREAM, 20)
    txt_c(d, S / 2, 1650, "smart spreadsheets for real life", F(38, "Italic" if False else "Regular"),
          (170, 190, 200), anchor="mm")
    txt_c(d, S / 2, 1790, "DIGITAL  •  INSTANT  •  FOR EVERY TRIP YOU'LL EVER TAKE",
          F(32, "SemiBold"), SAND, anchor="mm")
    img.save(os.path.join(OUT, "10-brand.png"), optimize=True)

# ================================================== PINTEREST + LOGO ========
def img_pinterest():
    W, H = 1000, 1500
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 300), fill=NAVY)
    txt_c(d, W / 2, 110, "TRAVEL PLANNER", FR(96), CREAM, anchor="mm")
    txt_c(d, W / 2, 200, "the complete trip planning spreadsheet", F(38, "SemiBold"),
          SAND, anchor="mm")
    sheet_card(img, d, 60, 370, 880, "BUDGET TRACKER",
               ["CATEGORY", "EST.", "ACTUAL"], [0.48, 0.26, 0.26],
               [[("Flights", "in"), ("$1,200", "in"), ("$1,184", "in")],
                [("Hotels", "in"), ("$900", "in"), ("$940", "in")],
                [("Food", "in"), ("$600", "in"), ("$512", "in")],
                [("Tours", "in"), ("$450", "in"), ("$380", "in")]],
               total=[("TOTAL", "plain"), ("$3,150", "plain"), ("$3,016", "plain")],
               row_h=64, banner_h=80, header_h=48, cell_font=F(26, "Medium"),
               head_font=F(23, "SemiBold"), banner_font=F(30, "Bold"))
    y = 950
    for glyph, s in (("✓", "29 smart sheets, pre-built & formatted"),
                     ("$", "Budget, expenses & savings — all automatic"),
                     ("✈", "Itinerary, hourly grid, maps & transport"),
                     ("★", "Packing lists, phrases, tips & memories")):
        icon_badge(d, 105, y, 30, glyph, bg=TEAL)
        txt(d, (160, y), s, F(32, "Medium"), NAVY_D, anchor="lm")
        y += 90
    d.rectangle((0, H - 170, W, H), fill=CORAL)
    txt_c(d, W / 2, H - 120, "INSTANT DOWNLOAD", F(44, "Bold"), WHITE, anchor="mm")
    txt_c(d, W / 2, H - 60, "NOVALITY STORE  •  EXCEL SPREADSHEET", F(28, "Bold"),
          CREAM, anchor="mm")
    img.save(os.path.join(OUT, "pinterest-1000x1500.png"), optimize=True)

def img_logo():
    S = 1000
    img = Image.new("RGB", (S, S), CREAM)
    d = ImageDraw.Draw(img)
    rrect(d, (40, 40, S - 40, S - 40), 190, fill=NAVY)
    # paper plane
    cx, cy = S / 2, 400
    d.polygon([(cx - 190, cy - 40), (cx + 220, cy - 150), (cx - 40, cy + 120)],
              fill=SAND)
    d.polygon([(cx - 190, cy - 40), (cx - 40, cy + 120), (cx - 110, cy + 60)],
              fill=SAND_D)
    d.polygon([(cx - 40, cy + 120), (cx + 220, cy - 150), (cx + 40, cy + 160)],
              fill=CORAL)
    for i, r_ in enumerate((16, 11, 7)):
        x = cx - 230 - i * 60
        d.ellipse((x - r_, cy + 150 - r_, x + r_, cy + 150 + r_), fill=TEAL)
    tracked(d, cx, 700, "NOVALITY", FR(110), CREAM, 14)
    tracked(d, cx, 790, "S T O R E", F(44, "Bold"), SAND, 6)
    txt_c(d, cx, 870, "smart spreadsheets for real life", F(30, "Regular"),
          (150, 170, 185), anchor="mm")
    img.save(os.path.join(OUT, "shop-avatar-1000.png"), optimize=True)

# ------------------------------------------------------------------- main ---
if __name__ == "__main__":
    img_cover();          print("01-cover.png")
    img_whats_inside();   print("02-whats-inside.png")
    img_budget();         print("03-budget-tracker.png")
    img_itinerary();      print("04-itinerary.png")
    img_packing();        print("05-packing.png")
    img_expenses();       print("06-expenses.png")
    img_dashboard();      print("07-dashboard.png")
    img_features();       print("08-features.png")
    img_how();            print("09-how-it-works.png")
    img_cta();            print("10-brand.png")
    img_pinterest();      print("pinterest-1000x1500.png")
    img_logo();           print("shop-avatar-1000.png")
    print("done →", OUT)
