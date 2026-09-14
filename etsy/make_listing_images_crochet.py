"""
make_listing_images_crochet - builds the 15 Etsy listing images for the
Crochet Craft Fair Tracker into etsy/images_crochet/ (2400x1800, <=1 MB
JPEG each).  Mirrors make_listing_images_catering.py but never writes
into etsy/images_catering/.
"""

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import crochet_lib as S
from etsy import crochet_screens as SC
from etsy.crochet_lib import (BORDER, CANVAS, CARD, COLORS, GOLD, INK,
                               MAUVE, MUTED, PRIMARY, ROSE, SOFT, WHITE)
from etsy.crochet_lib import (F, draw_text, fit_size, get_model, hexrgb,
                               rrect, text_width, wrap)

W, H = 2400, 1800
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images_crochet")
BANNER = os.path.join(HERE, "..", "assets", "banner_berry.png")

m = get_model()
DASH = SC.screen_dashboard(m)
CATALOG = SC.screen_catalog(m)
MATERIALS = SC.screen_materials(m)
PRODUCTION = SC.screen_production(m)
EVENTS = SC.screen_events(m)
SALES = SC.screen_sales(m)
EVENTPROFIT = SC.screen_eventprofit(m)
REORDER = SC.screen_reorder(m)
PACKING = SC.screen_packing(m)
PRICING = SC.screen_pricing(m)
MONTHLY = SC.screen_monthly(m)
SETUP = SC.screen_setup(m)
TABS_PREMIUM = SC.tabs_bar(m, "premium")
TABS_BASIC = SC.tabs_bar(m, "basic")

URL = "novalitystore.etsy.com  •  Catering Business Manager — Instant " \
      "Download"
FOOT = "Catering Business Manager — Excel & Google Sheets  •  Instant " \
       "Digital Download"


# ---------------------------------------------------------------------------
# frame-level helpers
# ---------------------------------------------------------------------------
def canvas():
    return Image.new("RGBA", (W, H), hexrgb(CANVAS))


def strip(top=True, height=200):
    """Watercolour strip cropped from the crochet banner art."""
    b = Image.open(BANNER).convert("RGBA")
    crop = b.crop((0, 0, 1600, 250)) if top else \
        b.crop((0, 640 - 250, 1600, 640))
    return crop.resize((W, height), Image.LANCZOS)


def kicker(cv, cx, y, text, color=ROSE, size=30, track=10):
    d = ImageDraw.Draw(cv)
    f = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size + 8


def headline(cv, cx, y, text, size=96, color=PRIMARY, spec="display_xb"):
    f, _ = fit_size(text, spec, size, W - 220, 30)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.32)


def subline(cv, cx, y, text, size=32, color=INK, spec="sans_md"):
    f, _ = fit_size(text, spec, size, W - 260, 16)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.7)


def chips_row(cv, cx, y, items, size=24, gap=26):
    """items = [(text, color_key)] centered row of pills."""
    fs, total = [], 0
    for text, color in items:
        f = S.F("sans_sb", size)
        w = text_width(text, f) + 44
        fs.append((text, color, f, w))
        total += w
    total += gap * (len(items) - 1)
    x = cx - total / 2.0
    for text, color, f, w in fs:
        d = ImageDraw.Draw(cv)
        rrect(d, [x, y, x + w, y + size + 30], (size + 30) / 2.0,
              fill=hexrgb(SOFT[color]))
        draw_text(cv, (x + 22, y + 14), text, f, COLORS[color])
        x += w + gap
    return y + size + 30


def browser(screen, width, url=URL):
    """Browser chrome around a screen image. Returns RGBA."""
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    chrome_h = 62
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#EFE6EC"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([26 + i * 34, 22, 44 + i * 34, 40], fill=hexrgb(c))
    pill = [width / 2.0 - 430, 14, width / 2.0 + 430, 48]
    rrect(d, pill, 17, fill=hexrgb(WHITE), outline=hexrgb("#E0D5DE"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 19, 830, 11)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 20, 23),
              "\U0001F512 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#E0D5DE"))
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CDBBC9"),
                                          width=4)
    return out


def side_card(cv, x, y, w, h, emoji, title, color, lines=None, body_pad=26,
              line_gap=38, size=22, extra=None):
    d = ImageDraw.Draw(cv)
    rrect(d, [x, y, x + w, y + h], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [x, y, x + w, y + 62], 16, fill=hexrgb(color))
    d.rectangle([x, y + 31, x + w, y + 62], fill=hexrgb(color))
    draw_text(cv, (x + 24, y + 13), f"{emoji} {title}",
              S.F("serif_b", 27), WHITE)
    yy = y + 62 + body_pad - 8
    if lines:
        for ln in lines:
            f = S.F("sans_md", size)
            for seg in wrap(ln, f, w - 2 * body_pad):
                draw_text(cv, (x + body_pad, yy), seg, f, INK)
                yy += line_gap
            yy += 6
    if extra:
        yy = extra(cv, x, yy + 6, w, h) if callable(extra) else yy
    return y + h


def formula_chip(cv, cx, cy, formula, note=None):
    f = S.F("mono", 30)
    fw = text_width(formula, f)
    d = ImageDraw.Draw(cv)
    w = fw + 76
    rrect(d, [cx - w / 2.0, cy - 34, cx + w / 2.0, cy + 34], 14,
          fill=hexrgb("#3A2430"))
    draw_text(cv, (cx - fw / 2.0, cy - 19), formula, f, "#F3D98B")
    if note:
        draw_text(cv, (cx, cy + 52), note, S.F("hand", 44), ROSE,
                  anchor="ma")
    return cy + 80


def num_circle(cv, cx, cy, n, r=52):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(ROSE))
    f = S.F("display_b", 58)
    draw_text(cv, (cx, cy - 34), str(n), f, WHITE, anchor="ma")


def arrow_right(cv, x, y, size=46, color=ROSE):
    d = ImageDraw.Draw(cv)
    d.line([x, y, x + size, y], fill=hexrgb(color), width=10)
    d.polygon([(x + size, y - 22), (x + size + 34, y),
               (x + size, y + 22)], fill=hexrgb(color))


def footer(cv, note=None):
    d = ImageDraw.Draw(cv)
    d.line([120, 1706, W - 120, 1706], fill=hexrgb(BORDER), width=2)
    draw_text(cv, (W / 2.0, 1726), "© Novality Store", S.F("sans_b", 26),
              PRIMARY, anchor="ma")
    draw_text(cv, (W / 2.0, 1762), note or FOOT, S.F("sans_md", 22), MUTED,
              anchor="ma")


def hand_note(cv, x, y, text, size=42, color=ROSE, anchor="la"):
    f = S.F("hand", size)
    for i, ln in enumerate(text.split("\n")):
        draw_text(cv, (x, y + i * int(size * 1.15)), ln, f, color,
                  anchor=anchor)


def save(cv, name, probes=None):
    os.makedirs(OUT, exist_ok=True)
    rgb = cv.convert("RGB")
    assert rgb.size == (W, H), f"{name}: wrong size {rgb.size}"
    path = os.path.join(OUT, name + ".jpg")
    for q in (90, 87, 84, 80, 76):
        rgb.save(path, "JPEG", quality=q, optimize=True)
        if os.path.getsize(path) <= 1024 * 1024:
            break
    size = os.path.getsize(path)
    assert size <= 1024 * 1024, f"{name}: {size} bytes > 1MB"
    ok = []
    for (x, y, label) in (probes or []):
        ok.append((label, rgb.getpixel((x, y))))
    hist = rgb.convert("L").histogram()
    total = sum(hist)
    dark = sum(hist[:80]) / total
    bg = rgb.getpixel((6, H - 6))
    mask = Image.eval(rgb.convert("L"), lambda v:
                      255 if abs(v - (0.299 * bg[0] + 0.587 * bg[1] +
                                      0.114 * bg[2])) > 12 else 0)
    bbox = mask.getbbox()
    print(f"{name}.jpg  {size//1024} KB  darkpx {dark:.1%}  "
          f"content {bbox}  " +
          "  ".join(f"{l}={p}" for l, p in ok))
    return path


# ---------------------------------------------------------------------------
# 01 — hero
# ---------------------------------------------------------------------------
def img01():
    cv = canvas()
    cv.alpha_composite(strip(True, 190), (0, 0))
    y = kicker(cv, W / 2, 214, "NOVALITY STORE  •  PREMIUM EDITION", ROSE)
    y = headline(cv, W / 2, y + 6, "Crochet Craft Fair Tracker", 104)
    y = subline(cv, W / 2, y + 4,
                "The spreadsheet that runs your yarn business — sales, "
                "stock, fairs and profit, all in one file")
    y = chips_row(cv, W / 2, y + 18, [
        ("Instant Download", "ok"), ("1,250+ Auto-Formulas", "rose"),
        ("14 Linked Tabs", "primary"), ("Excel & Google Sheets", "info")])
    crop = DASH.crop((0, 0, SC.SW, 980))
    br = browser(crop, 1280)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 26))
    footer(cv)
    save(cv, "01_hero")


# ---------------------------------------------------------------------------
# 02 — dashboard
# ---------------------------------------------------------------------------
def img02():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE DASHBOARD", ROSE)
    y = headline(cv, W / 2, y + 4, "Your whole craft-fair season", 84)
    y = subline(cv, W / 2, y + 2,
                "Cash in, cash out and what's left — recalculated the "
                "moment you log a sale")
    crop = DASH.crop((0, 240, SC.SW, 1420))
    br = browser(crop, 1280)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 18))
    side_card(cv, 76, y + 60, 430, 360, "\U0001F4CA", "Live numbers",
              PRIMARY, [
        "Gross sales, net profit and margin",
        "Units sold, average sale, sell-through",
        "Money in vs money out, always current",
        "4 charts, redrawn as you type",
    ])
    side_card(cv, W - 76 - 430, y + 60, 430, 360, "\U0001F514", "Plain-English alerts",
              ROSE, [
        "\"3 products below their minimum\"",
        "\"5 materials running low\"",
        "Your restock bill, priced out",
        "What to charge for your next design",
    ])
    footer(cv)
    save(cv, "02_dashboard")


# ---------------------------------------------------------------------------
# 03 — what's inside
# ---------------------------------------------------------------------------
def img03():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "WHAT'S INSIDE", ROSE)
    y = headline(cv, W / 2, y + 4, "14 linked tabs, zero set-up", 82)
    y = subline(cv, W / 2, y + 2,
                "Every tab feeds the next — enter a sale once, watch it "
                "ripple through the whole file")
    d = ImageDraw.Draw(cv)
    # premium panel
    rrect(d, [120, y + 24, 1214, 1372], 20, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [120, y + 24, 1214, y + 24 + 92], 20, fill=hexrgb(PRIMARY))
    d.rectangle([120, y + 24 + 46, 1214, y + 24 + 92], fill=hexrgb(PRIMARY))
    draw_text(cv, (136, y + 24 + 20), "\U0001F451  PREMIUM EDITION — 14 tabs",
              S.F("serif_b", 40), WHITE)
    draw_text(cv, (1198, y + 24 + 30),
              "1,250+ formulas  •  12 charts", S.F("sans_sb", 26),
              "#F4E9F0", anchor="ra")
    cv.alpha_composite(TABS_PREMIUM.resize((1094, 124), Image.LANCZOS),
                       (120, y + 24 + 118))
    rows = [
        ("\U0001F3E0", "Dashboard", "The whole business on one screen"),
        ("\U0001F9F6", "Product Catalog", "Prices, costs, stock and margins"),
        ("\U0001F9F5", "Yarn & Materials", "Your stash, with costs per ball"),
        ("\U0001F4E6", "Made & Stocked", "Production batches, counted live"),
        ("\U0001F3EA", "Craft Fairs", "Every fair, booth fee to net profit"),
        ("\U0001F4B0", "Sales Log", "One row per item sold"),
        ("\U0001F9EE", "Event Profit", "Was that fair worth it?"),
        ("\U0001F504", "Reorder List", "The shopping list that writes itself"),
        ("\U0001F392", "Packing Checklist", "Tick your way out the door"),
        ("\U0001F4B5", "Pricing Calculator", "Never underprice again"),
        ("\U0001F4C5", "Monthly Summary", "Your year, month by month"),
    ]
    col_w = (1094 - 40) / 2.0
    for i, (emo, name, desc) in enumerate(rows):
        col, row = i % 2, i // 2
        xx = 140 + col * (col_w + 40)
        yy = y + 24 + 268 + row * 88
        draw_text(cv, (xx, yy), emo, S.F("sans_sb", 34))
        draw_text(cv, (xx + 56, yy - 4), name, S.F("sans_b", 30), PRIMARY)
        f, _ = fit_size(desc, "sans_md", 24, col_w - 70, 12)
        draw_text(cv, (xx + 56, yy + 36), desc, f, MUTED)
    # basic panel
    rrect(d, [1214 + 66, y + 24, W - 120, 1372], 20, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [1214 + 66, y + 24, W - 120, y + 24 + 92], 20, fill=hexrgb(MAUVE))
    d.rectangle([1214 + 66, y + 24 + 46, W - 120, y + 24 + 92],
                fill=hexrgb(MAUVE))
    draw_text(cv, (1214 + 86, y + 24 + 20), "\U0001F9ED  BASIC EDITION",
              S.F("serif_b", 40), WHITE)
    cv.alpha_composite(TABS_BASIC.resize((984, 111), Image.LANCZOS),
                       (1214 + 66, y + 24 + 118))
    draw_text(cv, (1214 + 66, y + 24 + 262), "sold separately",
              S.F("hand", 46), ROSE)
    side_card(cv, 1214 + 86, y + 24 + 340, 984 - 40, 640, "\U0001F5A5",
              "The starter kit", MAUVE, [
        "8 tabs, 400+ formulas — everything a first-season seller needs",
        "Dashboard, Product Catalog, Craft Fairs, Sales Log and the "
        "Pricing Calculator",
        "Upgrade to Premium any season — the layout matches",
    ])
    y = chips_row(cv, W / 2, 1400, [
        ("\U0001F4D6 Start Here guide tab", "ok"),
        ("\U0001F34D Two themes — Berry & Mint", "plum"),
        ("\U0001F9EA Filled-in example file", "gold")])
    footer(cv)
    save(cv, "03_whats_inside")


# ---------------------------------------------------------------------------
# 04 — product catalog
# ---------------------------------------------------------------------------
def img04():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "PRODUCT CATALOG", ROSE)
    y = headline(cv, W / 2, y + 4, "Every product, priced properly", 82)
    y = subline(cv, W / 2, y + 2,
                "Twelve hand-made products, live stock levels and the "
                "margin on every one")
    crop = CATALOG.crop((0, 0, SC.SW, 1080))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 20))
    y2 = y + 20 + br.height + 44
    formula_chip(cv, W / 2, y2 - 10,
                 "margin = (price − cost) / price",
                 "it's already calculated for every row")
    footer(cv)
    save(cv, "04_catalog")


# ---------------------------------------------------------------------------
# 05 — yarn & materials
# ---------------------------------------------------------------------------
def img05():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "YARN & MATERIALS", ROSE)
    y = headline(cv, W / 2, y + 4, "Your yarn stash, counted", 84)
    y = subline(cv, W / 2, y + 2,
                "Every ball with its cost — and a reorder ticker when the "
                "shelf runs low")
    crop = MATERIALS.crop((0, 0, SC.SW, MATERIALS.height))
    br = browser(crop, 1160)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2) - 220, y + 24))
    side_card(cv, W - 76 - 500, y + 60, 500, 420, "\U0001F9F5", "Stitch by stitch",
              PRIMARY, [
        "Log what you buy and what you use",
        "Cost per ball rolls into product costs",
        "The Reorder List picks up shortages",
        "Suppliers and colourways, one place",
    ])
    footer(cv)
    save(cv, "05_materials")


# ---------------------------------------------------------------------------
# 06 — sales log
# ---------------------------------------------------------------------------
def img06():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "SALES LOG", ROSE)
    y = headline(cv, W / 2, y + 4, "One row per item sold", 84)
    y = subline(cv, W / 2, y + 2,
                "Type the product and the quantity — totals, costs and the "
                "dashboard update themselves")
    crop = SALES.crop((0, 0, SC.SW, 1060))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 20))
    y2 = y + 20 + br.height + 40
    formula_chip(cv, W / 2, y2 - 10,
                 "77 units  →  $1,760 gross  →  $716.50 net",
                 "typed once, counted everywhere")
    footer(cv)
    save(cv, "06_sales")


# ---------------------------------------------------------------------------
# 07 — craft fairs
# ---------------------------------------------------------------------------
def img07():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "CRAFT FAIRS", ROSE)
    y = headline(cv, W / 2, y + 4, "The fairs that pay (and the ones that don't)", 74)
    y = subline(cv, W / 2, y + 2,
                "Booth fees, travel, parking and stock — every fair gets "
                "its true profit")
    crop = EVENTS.crop((0, 0, SC.SW, EVENTS.height))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 22))
    y2 = y + 22 + br.height + 40
    draw_text(cv, (W / 2, y2),
              "Booth fee $60 + travel $21 + goods $82.80 = $163.80 of "
              "costs before you sell a thing",
              S.F("sans_b", 34), INK, anchor="ma")
    footer(cv)
    save(cv, "07_events")


# ---------------------------------------------------------------------------
# 08 — event profit
# ---------------------------------------------------------------------------
def img08():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "EVENT PROFIT", ROSE)
    y = headline(cv, W / 2, y + 4, "Was that fair worth it?", 88)
    y = subline(cv, W / 2, y + 2,
                "Pick a fair from the dropdown — the maths answers before "
                "you've packed the car")
    crop = EVENTPROFIT.crop((0, 0, SC.SW, EVENTPROFIT.height))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 20))
    y2 = y + 20 + br.height + 34
    d = ImageDraw.Draw(cv)
    for i, (lbl, val) in enumerate((
            ("Net profit", "$199.20"), ("Margin", "50.1%"),
            ("Breakeven", "$251.02"), ("ROI", "100.2%"))):
        x0 = 240 + i * 500
        rrect(d, [x0, y2, x0 + 440, y2 + 128], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(cv, (x0 + 220, y2 + 18), lbl, S.F("sans_sb", 24), MUTED,
                  anchor="ma")
        draw_text(cv, (x0 + 220, y2 + 52), val, S.F("display_b", 52),
                  COLORS["ok" if i == 0 else "primary"], anchor="ma")
    footer(cv)
    save(cv, "08_eventprofit")


# ---------------------------------------------------------------------------
# 09 — reorder + packing
# ---------------------------------------------------------------------------
def img09():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "RESTOCK & PACK", ROSE)
    y = headline(cv, W / 2, y + 4, "The list that writes itself", 82)
    y = subline(cv, W / 2, y + 2,
                "Shortages become a shopping list; the packing list makes "
                "sure nothing stays home")
    c1 = REORDER.crop((0, 0, SC.SW, 980))
    c2 = PACKING.crop((0, 0, SC.SW, 980))
    br1 = browser(c1, 1100)
    br2 = browser(c2, 1100)
    cv.alpha_composite(br1, (46, y + 26))
    cv.alpha_composite(br2, (W - 46 - br2.width, y + 26))
    y2 = y + 26 + max(br1.height, br2.height) + 40
    draw_text(cv, (W / 2, y2),
              "12 items low · $342.70 to restock · 14 of 21 packed for "
              "the next fair",
              S.F("sans_b", 34), INK, anchor="ma")
    footer(cv)
    save(cv, "09_reorder_packing")


# ---------------------------------------------------------------------------
# 10 — pricing calculator
# ---------------------------------------------------------------------------
def img10():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "PRICING CALCULATOR", ROSE)
    y = headline(cv, W / 2, y + 4, "Stop underpricing your work", 84)
    y = subline(cv, W / 2, y + 2,
                "Yarn + packaging + your hours + overhead, at the margin "
                "you actually want")
    crop = PRICING.crop((0, 0, SC.SW, PRICING.height))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 20))
    y2 = y + 20 + br.height + 40
    formula_chip(cv, W / 2, y2 - 10,
                 "price = true cost ÷ (1 − margin)",
                 "$4 yarn + $1 packaging + 1.5 h at $14 → charge $52.00")
    footer(cv)
    save(cv, "10_pricing")


# ---------------------------------------------------------------------------
# 11 — monthly summary
# ---------------------------------------------------------------------------
def img11():
    cv = canvas()
    y = kicker(cv, W / 2, 92, "MONTHLY SUMMARY", ROSE)
    y = headline(cv, W / 2, y + 4, "Your year at a glance", 84)
    y = subline(cv, W / 2, y + 2,
                "Revenue, goods, fees and net — one row per month, "
                "totalling your season")
    crop = MONTHLY.crop((0, 0, SC.SW, MONTHLY.height))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 20))
    y2 = y + 20 + br.height + 40
    draw_text(cv, (W / 2, y2),
              "August earned $259.60 net · September's booth deposits are "
              "already logged",
              S.F("sans_b", 34), INK, anchor="ma")
    footer(cv)
    save(cv, "11_monthly")


# ---------------------------------------------------------------------------
# 12 — example file
# ---------------------------------------------------------------------------
def img12():
    cv = canvas()
    cv.alpha_composite(strip(False, 170), (0, H - 170))
    y = kicker(cv, W / 2, 92, "INCLUDED: EXAMPLE FILE", ROSE)
    y = headline(cv, W / 2, y + 4, "Meet Willow & Wren Crochet Studio", 76)
    y = subline(cv, W / 2, y + 2,
                "A filled-in demo of the premium file — 8 fairs, 22 sales, "
                "12 products, so you can see every formula working before "
                "you type a thing")
    crop = CATALOG.crop((0, 0, SC.SW, 1000))
    br = browser(crop, 1240)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 18))
    hand_note(cv, W / 2, y + 18 + br.height + 34,
              "this exact file ships with your download", 48, ROSE, "ma")
    footer(cv)
    save(cv, "12_example")


# ---------------------------------------------------------------------------
# 13 — how it works
# ---------------------------------------------------------------------------
def img13():
    cv = canvas()
    y = kicker(cv, W / 2, 100, "HOW IT WORKS", ROSE)
    y = headline(cv, W / 2, y + 4, "Set up once, log as you go", 84)
    y = subline(cv, W / 2, y + 2,
                "If you can type in a spreadsheet, you can run this file")
    steps = [
        (1, "\U0001F3E2", "Add your studio basics",
         "Business name, currency, hourly wage and target margin in the "
         "Settings tab."),
        (2, "\U0001F9F6", "List your products & yarn",
         "Prices and costs per item — the catalog and stash tabs do the "
         "restocking maths."),
        (3, "\U0001F4B0", "Log sales at the fair",
         "Product, quantity, payment method. The dashboard, monthly "
         "summary and reorder list update instantly."),
    ]
    yy = y + 40
    for i, (n, emo, title, body) in enumerate(steps):
        x0 = 160 + i * 720
        num_circle(cv, x0 + 260, yy + 80, n)
        side_card(cv, x0, yy + 170, 540, 480, emo, title, PRIMARY, [body],
                  size=26)
        if i < 2:
            arrow_right(cv, x0 + 560, yy + 250, 60)
    y2 = yy + 170 + 480 + 60
    y2 = chips_row(cv, W / 2, y2, [
        ("No macros", "ok"), ("No formulas to write", "ok"),
        ("Works offline", "ok"), ("5-minute start", "gold")])
    footer(cv)
    save(cv, "13_howitworks")


# ---------------------------------------------------------------------------
# 14 — what you receive
# ---------------------------------------------------------------------------
def img14():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "WHAT YOU RECEIVE", ROSE)
    y = headline(cv, W / 2, y + 4, "Instant download, 4 files", 84)
    y = subline(cv, W / 2, y + 2,
                "Two themes of the premium file, a filled-in example, and "
                "an illustrated 12-page guide")
    files = [
        ("\U0001F451", "PREMIUM — Berry", "14 tabs, 1,250+ formulas, 12 "
         "charts, warm autumn theme", PRIMARY),
        ("\U0001F341", "PREMIUM — Mint", "the same engine in a fresh "
         "stitch-studio palette", MAUVE),
        ("\U0001F9EA", "EXAMPLE — Willow & Wren", "the filled-in demo from "
         "these pictures", ROSE),
        ("\U0001F4D8", "USER GUIDE — 12 pages", "every tab explained, "
         "printed or on screen", GOLD),
    ]
    for i, (emo, name, desc, col) in enumerate(files):
        x0 = 150 + (i % 2) * 1080
        yy = y + 30 + (i // 2) * 380
        side_card(cv, x0, yy, 1020, 330, emo, name, col, [desc], size=28)
    y2 = y + 30 + 760 + 70
    draw_text(cv, (W / 2, y2), "Every file: .xlsx — opens in Excel 2016+, "
              "Microsoft 365, Mac Excel and Google Sheets",
              S.F("sans_b", 32), INK, anchor="ma")
    y2 = chips_row(cv, W / 2, y2 + 48, [
        ("Formulas locked for safety", "ok"),
        ("1,250+ ready-made formulas", "primary"),
        ("No macros — just spreadsheets", "info")])
    footer(cv)
    save(cv, "14_files")


# ---------------------------------------------------------------------------
# 15 — FAQ / specs
# ---------------------------------------------------------------------------
def img15():
    cv = canvas()
    y = kicker(cv, W / 2, 90, "GOOD TO KNOW", ROSE)
    y = headline(cv, W / 2, y + 4, "Questions, answered", 84)
    qa = [
        ("\U0001F4BB", "Does it work on my computer?",
         "Yes — Excel 2016 or newer (Windows or Mac), Microsoft 365, and "
         "Google Sheets. No macros to enable."),
        ("\U0001F469\u200D\U0001F4BC", "I'm not a spreadsheet person.",
         "You only type in the open cells — every one of the 1,250+ "
         "formulas is locked and already written for you."),
        ("\U0001F4E6", "What exactly do I get?",
         "4 files: the premium tracker in two themes, a filled-in example, "
         "and a 12-page illustrated PDF guide. Instant download."),
        ("\U0001F6E0", "Can I edit the lists?",
         "Every dropdown list — categories, payment methods, yarn "
         "weights, suppliers — is yours to edit in Settings."),
        ("\U0001F4B8", "What about my own prices?",
         "Your hourly wage, overhead and target margin live in Settings; "
         "the pricing calculator uses them."),
    ]
    for i, (emo, q, a) in enumerate(qa):
        yy = y + 18 + i * 262
        side_card(cv, 170, yy, 2060, 240, emo, q, PRIMARY if i % 2 == 0
                  else ROSE, [a], size=27)
    y2 = y + 18 + 5 * 262 + 20
    draw_text(cv, (W / 2, y2), "© Novality Store — made for makers who'd "
              "rather be crocheting than spreadsheeting",
              S.F("hand", 52), ROSE, anchor="ma")
    footer(cv)
    save(cv, "15_faq")


# ---------------------------------------------------------------------------
def main():
    for i in range(1, 16):
        globals()[f"img{i:02d}"]()
    print("all 15 crochet listing images written to", OUT)


if __name__ == "__main__":
    main()
