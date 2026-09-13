"""
make_listing_images_catering - builds the 15 Etsy listing images for the
Catering Business Manager into etsy/images_catering/ (2400x1800, <=1 MB
JPEG each).  Mirrors make_listing_images.py (the Christmas kit) but never
writes into etsy/images/.
"""

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import catering_lib as S
from etsy import catering_screens as SC
from etsy.catering_lib import (BORDER, CANVAS, CARD, COPPER, ESPRESSO, INK,
                               LATTE, MUTED, SOFT, WHITE, COLORS)
from etsy.catering_lib import (F, draw_text, fit_size, get_model, hexrgb,
                               rrect, text_width, wrap)

W, H = 2400, 1800
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images_catering")
BANNER = os.path.join(HERE, "..", "assets", "banner_classic.png")

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
    """Watercolour strip cropped from the catering banner art."""
    b = Image.open(BANNER).convert("RGBA")
    crop = b.crop((0, 0, 1600, 250)) if top else \
        b.crop((0, 640 - 250, 1600, 640))
    return crop.resize((W, height), Image.LANCZOS)


def kicker(cv, cx, y, text, color=COPPER, size=30, track=10):
    d = ImageDraw.Draw(cv)
    f = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size + 8


def headline(cv, cx, y, text, size=96, color=ESPRESSO, spec="display_xb"):
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
    frame = Image.new("RGBA", (width, chrome_h + sh + 6), hexrgb("#EFE7D7"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([26 + i * 34, 22, 44 + i * 34, 40], fill=hexrgb(c))
    pill = [width / 2.0 - 430, 14, width / 2.0 + 430, 48]
    rrect(d, pill, 17, fill=hexrgb(WHITE), outline=hexrgb("#DDD2BE"))
    f, _ = fit_size("\U0001F512 " + url, "sans_md", 19, 830, 11)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 20, 23),
              "\U0001F512 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#DDD2BE"))
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CBBFA8"),
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
          fill=hexrgb("#2E2A24"))
    draw_text(cv, (cx - fw / 2.0, cy - 19), formula, f, "#F3D98B")
    if note:
        draw_text(cv, (cx, cy + 52), note, S.F("hand", 44), COPPER,
                  anchor="ma")
    return cy + 80


def num_circle(cv, cx, cy, n, r=52):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(COPPER))
    f = S.F("display_b", 58)
    draw_text(cv, (cx, cy - 34), str(n), f, WHITE, anchor="ma")


def arrow_right(cv, x, y, size=46, color=COPPER):
    d = ImageDraw.Draw(cv)
    d.line([x, y, x + size, y], fill=hexrgb(color), width=10)
    d.polygon([(x + size, y - 22), (x + size + 34, y),
               (x + size, y + 22)], fill=hexrgb(color))


def footer(cv, note=None):
    d = ImageDraw.Draw(cv)
    d.line([120, 1706, W - 120, 1706], fill=hexrgb(BORDER), width=2)
    draw_text(cv, (W / 2.0, 1726), "© Novality Store", S.F("sans_b", 26),
              ESPRESSO, anchor="ma")
    draw_text(cv, (W / 2.0, 1762), note or FOOT, S.F("sans_md", 22), MUTED,
              anchor="ma")


def hand_note(cv, x, y, text, size=42, color=COPPER, anchor="la"):
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
    cv.alpha_composite(strip(True, 190))
    y = kicker(cv, W / 2, 190, "NOVALITY STORE  PRESENTS", COPPER, 30, 12)
    hand_note(cv, W / 2 - 560, y + 6, "The", 74, S.BRASS, "ra")
    draw_text(cv, (W / 2, y + 8), "Catering Business Manager",
              S.F("display_xb", 104), ESPRESSO, anchor="ma")
    y = subline(cv, W / 2, y + 172,
                "The all-in-one Excel & Google Sheets system for events, "
                "clients, quotes, food cost and profit — built for real "
                "catering businesses.", 32)
    y = chips_row(cv, W / 2, y + 18, [
        ("\u26A1 Instant Download", "espresso"),
        ("\U0001F916 1,500+ Auto-Formulas", "copper"),
        ("\U0001F4CA 20 Linked Tabs", "info"),
        ("\U0001F512 Formulas Protected", "plum"),
    ])
    hero = DASH.crop((0, 0, 1320, 1000))
    br = browser(hero, 1440)
    cv.alpha_composite(br, (int(W / 2 - br.width / 2), y + 24))
    y += 24 + br.height + 8
    hand_note(cv, W / 2, y + 6, "every number below is the live demo "
              "business in the file", 44, S.BRASS, "ma")
    footer(cv)
    save(cv, "01_hero", probes=[(1200, 300, "title_bg"), (1200, 760,
                                                           "hero_browser")])
    return cv


# ---------------------------------------------------------------------------
# 02 — dashboard
# ---------------------------------------------------------------------------
def img02():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "THE COMMAND CENTRE", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Your whole business on one screen", 84)
    br = browser(DASH.crop((0, 0, 1320, 1180)), 1310)
    cv.alpha_composite(br, (110, y + 14))
    x2 = 1470
    y2 = y + 10
    y2 = side_card(cv, x2, y2, 820, 320, "\U0001F4CB", "Live KPIs",
                   ESPRESSO, [
                       "Cash in, cash out, net profit and margin —",
                       "recomputed from every entry you make, with",
                       "average order value and outstanding invoices",
                       "right beside them."])
    y2 = side_card(cv, x2, y2 + 24, 820, 300, "\U0001F3C6", "Best "
                   "performers", COPPER, [
                       "Top clients, best-earning event type and food-cost",
                       "percentages, so you know what to sell more of."])
    formula_chip(cv, x2 + 410, y2 + 170, "price \u2212 cost = profit")
    y2 += 330
    y2 = side_card(cv, x2, y2 - 20, 820, 260, "\U0001F514", "Never miss "
                   "a beat", LATTE, [
                       "Upcoming events, payments due, low stock and",
                       "equipment needing service — flagged on the",
                       "dashboard before they become problems."])
    hand_note(cv, x2 + 400, y2 + 40,
              "no formulas to write!", 46, S.BRASS, "ma")
    footer(cv)
    save(cv, "02_dashboard", probes=[(400, 500, "browser"), (1600, 400,
                                                              "card")])
    return cv


# ---------------------------------------------------------------------------
# 03 — tabs
# ---------------------------------------------------------------------------
def img03():
    cv = canvas()
    y = kicker(cv, W / 2, 84, "WHAT'S INSIDE", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "20 tabs, one system", 88)
    y = subline(cv, W / 2, y - 6, "Premium edition — every tab is linked "
                "to the same live data", 30)
    # premium panel
    d = ImageDraw.Draw(cv)
    ph = 560
    rrect(d, [140, y + 10, 2260, y + 10 + ph], 20, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [140, y + 10, 2260, y + 96], 20, fill=hexrgb(ESPRESSO))
    d.rectangle([140, y + 53, 2260, y + 96], fill=hexrgb(ESPRESSO))
    draw_text(cv, (190, y + 26), "\U0001F451 PREMIUM EDITION — 20 TABS",
              S.F("serif_b", 40), WHITE)
    tb = TABS_PREMIUM.resize((1980, int(TABS_PREMIUM.height * 1980 /
                                         1320.0)), Image.LANCZOS)
    cv.alpha_composite(tb, (170, y + 130))
    yy = y + 10 + ph + 34
    # basic panel
    bh = 330
    rrect(d, [140, yy, 2260, yy + bh], 20, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [140, yy, 2260, yy + 86], 20, fill=hexrgb(COPPER))
    d.rectangle([140, yy + 43, 2260, yy + 86], fill=hexrgb(COPPER))
    draw_text(cv, (190, yy + 16), "\U0001F9F1 BASIC EDITION — 9 TABS "
              "(SOLD SEPARATELY)", S.F("serif_b", 40), WHITE)
    tb2 = TABS_BASIC.resize((1980, int(TABS_BASIC.height * 1980 / 1320.0)),
                            Image.LANCZOS)
    cv.alpha_composite(tb2, (170, yy + 116))
    yy += bh + 30
    chips_row(cv, W / 2, yy, [
        ("\U0001F4D6 Start Here guide tab", "info"),
        ("\U0001F3A8 2 themes: Classic & Fresh", "copper"),
        ("\U0001F50D Example file included", "ok"),
    ])
    footer(cv)
    save(cv, "03_tabs", probes=[(300, 400, "premium_panel"),
                                (300, 1000, "basic_panel")])
    return cv


# ---------------------------------------------------------------------------
# 04 — events
# ---------------------------------------------------------------------------
def img04():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "EVENTS", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Every booking, profit to the plate", 84)
    br = browser(EVENTS, 1430)
    cv.alpha_composite(br, (100, y + 14))
    x2 = 1580
    y2 = y + 20
    y2 = side_card(cv, x2, y2, 720, 330, "\U0001F6E2", "The whole "
                   "pipeline", ESPRESSO, [
                       "Inquiry \u2192 quote \u2192 deposit \u2192 confirmed",
                       "\u2192 completed. Each stage is a drop-down, and",
                       "the dashboard counts them live."])
    y2 = side_card(cv, x2, y2 + 24, 720, 300, "\U0001F9EE", "Profit per "
                   "event", COPPER, [
                       "Log the price and the costs you know —",
                       "the sheet keeps score on every plate."])
    formula_chip(cv, x2 + 360, y2 + 210, "L8 \u2212 K8", None)
    y2 += 330
    hand_note(cv, x2 + 360, y2 + 16, "deposits & balances\ncome from here "
              "too", 44, S.BRASS, "ma")
    footer(cv)
    save(cv, "04_events", probes=[(500, 600, "browser"), (1800, 400,
                                                           "card")])
    return cv


# ---------------------------------------------------------------------------
# 05 — quote builder
# ---------------------------------------------------------------------------
def img05():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "QUOTE BUILDER", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Price an event in 60 seconds", 84)
    br = browser(QUOTE, 1430)
    cv.alpha_composite(br, (100, y + 14))
    x2 = 1580
    y2 = y + 20
    y2 = side_card(cv, x2, y2, 720, 340, "\U0001F52C", "The math behind "
                   "the price", ESPRESSO, [
                       "Guests \u00D7 food cost per guest, plus labor,",
                       "kit, transport — then your target margin is",
                       "added on top automatically."])
    formula_chip(cv, x2 + 360, y2 + 218, "cost \u00F7 (1 \u2212 margin)")
    y2 = side_card(cv, x2, y2 + 30, 720, 300, "\U0001F4B0", "Deposit "
                   "logic built in", COPPER, [
                       "Set your deposit % once. Every quote shows",
                       "what to collect to lock the date, and the",
                       "balance due after the event."])
    hand_note(cv, x2 + 360, y2 + 330, "no more guess-pricing!", 46, S.BRASS,
              "ma")
    footer(cv)
    save(cv, "05_quote", probes=[(500, 600, "browser"), (1800, 400,
                                                          "card")])
    return cv


# ---------------------------------------------------------------------------
# 06 — menu costing
# ---------------------------------------------------------------------------
def img06():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "MENU COSTING", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Cost every dish once, price it right", 80)
    br = browser(MENU, 1430)
    cv.alpha_composite(br, (100, y + 14))
    x2 = 1580
    y2 = y + 20
    y2 = side_card(cv, x2, y2, 720, 340, "\U0001F37D", "Signature dish "
                   "economics", ESPRESSO, [
                       "A $4.85 chicken platter at a 60% margin sells",
                       "at $12.12 — the sheet rounds it to a clean",
                       "$12.50 menu price and tracks the profit."])
    y2 = side_card(cv, x2, y2 + 24, 720, 330, "\U0001F346", "Your menu, "
                   "your margins", COPPER, [
                       "14 sample dishes are costed and priced —",
                       "swap in your own recipes and watch margin,",
                       "profit and per-plate numbers update."])
    formula_chip(cv, x2 + 360, y2 + 232, "price = cost \u00F7 0.4", None)
    footer(cv)
    save(cv, "06_menu", probes=[(500, 600, "browser"), (1800, 400,
                                                         "card")])
    return cv


# ---------------------------------------------------------------------------
# 07 — money in / money out
# ---------------------------------------------------------------------------
def img07():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "MONEY", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Expenses & payments, connected", 84)
    y = subline(cv, W / 2, y - 6, "Every cost is tagged to an event, so "
                "profit stays honest", 30)
    e1 = browser(EXPENSES, 1120, url="novalitystore.etsy.com  •  "
                 "Catering Business Manager — Expenses")
    e2 = browser(INCOME, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Payments")
    x1 = 1200 - e1.width - 40
    cv.alpha_composite(e1, (x1, y + 20))
    cv.alpha_composite(e2, (1240, y + 20))
    yy = y + 20 + max(e1.height, e2.height) + 26
    chips_row(cv, W / 2, yy, [
        ("\U0001F4B8 11 expense categories", "bad"),
        ("\U0001F4B0 Deposits & part-payments tracked", "ok"),
        ("\U0001F551 Late payers flagged red", "warn"),
    ])
    hand_note(cv, W / 2, yy + 110, "profit you can trust", 52, S.BRASS,
              "ma")
    footer(cv)
    save(cv, "07_money", probes=[(400, 700, "expenses"), (1900, 700,
                                                           "income")])
    return cv


# ---------------------------------------------------------------------------
# 08 — charts
# ---------------------------------------------------------------------------
def img08():
    cv = canvas()
    y = kicker(cv, W / 2, 90, "REPORTING", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Charts that build themselves", 84)
    a = m.agg
    d = ImageDraw.Draw(cv)
    card_w, card_h = 1080, 620
    positions = [(160, y + 16), (1300, y + 16), (160, y + 16 + card_h + 22),
                 (1300, y + 16 + card_h + 22)]
    for px, py in positions:
        rrect(d, [px, py, px + card_w, py + card_h], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
    months = [t for t in a["months"] if t[1] or t[2]][-6:]
    S.grouped_columns(cv, (200, positions[0][1] + 90,
                           1200, positions[0][1] + card_h - 40),
                      "Revenue vs expenses by month",
                      [t[0] for t in months],
                      [("Revenue", [max(t[1], 0) for t in months], COPPER),
                       ("Expenses", [max(t[2], 0) for t in months], LATTE)],
                      fmt="${:,.0f}", size=1.7)
    types = [t for t in a["types"] if t[1]][:5]
    S.doughnut_chart(cv, (1340, positions[1][1] + 90,
                          2340, positions[1][1] + card_h - 40),
                     "Revenue by event type",
                     [(t[0], t[1] // 100, c) for t, c in
                      zip(types, [COPPER, LATTE, S.BRASS, S.INFO, S.PLUM])],
                     size=1.7, center_word="events",
                     center_value=a["events_total"])
    S.hbar_chart(cv, (200, positions[2][1] + 96,
                      1200, positions[2][1] + card_h - 40),
                 "Top clients by revenue",
                 [(c, v) for c, v in a["clients_pool"][:5]], color=ESPRESSO,
                 fmt="${:,.0f}", size=1.7)
    sc = a["status_counts"]
    S.doughnut_chart(cv, (1340, positions[3][1] + 90,
                          2340, positions[3][1] + card_h - 40),
                     "Event pipeline mix",
                     [(k, v, c) for (k, v), c in
                      zip(sorted(sc.items(), key=lambda kv: -kv[1]),
                          [COPPER, S.OK, LATTE, S.BRASS, S.INFO, S.BAD])],
                     size=1.7, center_word="bookings",
                     center_value=a["events_total"])
    footer(cv)
    save(cv, "08_charts", probes=[(600, 500, "chart1"), (1800, 500,
                                                          "chart2")])
    return cv


# ---------------------------------------------------------------------------
# 09 — inventory & shopping
# ---------------------------------------------------------------------------
def img09():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "STOCK", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "A stock room that shops for itself", 80)
    y = subline(cv, W / 2, y - 6, "Event menus subtract what you already "
                "own — the gap becomes your shopping list", 30)
    e1 = browser(INVENTORY, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Inventory")
    e2 = browser(SHOPPING, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Shopping List")
    x1 = 1200 - e1.width - 40
    cv.alpha_composite(e1, (x1, y + 20))
    cv.alpha_composite(e2, (1240, y + 20))
    yy = y + 20 + max(e1.height, e2.height) + 26
    chips_row(cv, W / 2, yy, [
        ("\U0001F534 Reorder ticker on every ingredient", "bad"),
        ("\U0001F6D2 Grouped by supplier", "info"),
        ("\U0001F4B2 Estimated spend included", "copper"),
    ])
    footer(cv)
    save(cv, "09_inventory_shopping", probes=[(400, 700, "inventory"),
                                              (1900, 700, "shopping")])
    return cv


# ---------------------------------------------------------------------------
# 10 — staff & equipment
# ---------------------------------------------------------------------------
def img10():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "PEOPLE & KIT", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Crew, shifts and chafing dishes", 84)
    e1 = browser(STAFF, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Staff")
    e2 = browser(EQUIPMENT, 1120, url="novalitystore.etsy.com  •  "
                 "Catering Business Manager — Equipment")
    x1 = 1200 - e1.width - 40
    cv.alpha_composite(e1, (x1, y + 20))
    cv.alpha_composite(e2, (1240, y + 20))
    yy = y + 20 + max(e1.height, e2.height) + 26
    chips_row(cv, W / 2, yy, [
        ("\U0001F553 Overtime at 1.5\u00D7", "plum"),
        ("\U0001F527 Service reminders", "warn"),
        ("\U0001F4E6 Availability auto-checked", "ok"),
    ])
    footer(cv)
    save(cv, "10_staff_equipment", probes=[(400, 700, "staff"),
                                           (1900, 700, "equipment")])
    return cv


# ---------------------------------------------------------------------------
# 11 — calendar & reports
# ---------------------------------------------------------------------------
def img11():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "PLANNING & NUMBERS", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "See the season, then read the score", 80)
    e1 = browser(CALENDAR, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Calendar")
    e2 = browser(REPORTS, 1120, url="novalitystore.etsy.com  •  Catering "
                 "Business Manager — Reports")
    x1 = 1200 - e1.width - 40
    cv.alpha_composite(e1, (x1, y + 20))
    cv.alpha_composite(e2, (1240, y + 20))
    yy = y + 20 + max(e1.height, e2.height) + 26
    chips_row(cv, W / 2, yy, [
        ("\U0001F4C6 Bookings + payment deadlines", "info"),
        ("\U0001F4BC Season P&L", "espresso"),
        ("\U0001F9FD Sales-tax helper", "ok"),
    ])
    footer(cv)
    save(cv, "11_calendar_reports", probes=[(400, 700, "calendar"),
                                            (1900, 700, "reports")])
    return cv


# ---------------------------------------------------------------------------
# 12 — how it works
# ---------------------------------------------------------------------------
def img12():
    cv = canvas()
    y = kicker(cv, W / 2, 110, "HOW IT WORKS", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "From download to profit in 10 minutes", 84)
    steps = [
        ("\U0001F4E5", "Download instantly", "Your files arrive the moment "
         "you check out — no waiting, nothing to ship."),
        ("\U0001F5A5", "Open in Excel or Sheets", "Works in Microsoft "
         "Excel (2016+) and uploads straight to Google Sheets."),
        ("\u270F", "Type over the examples", "A demo catering business is "
         "included so you can see every formula working."),
        ("\U0001F4C8", "Run your season", "Quotes, shopping lists, payroll "
         "and profit — updated on every entry."),
    ]
    cw, gap = 528, 40
    x = (W - (cw * 4 + gap * 3)) / 2.0
    d = ImageDraw.Draw(cv)
    yy = y + 50
    for i, (emo, title, body) in enumerate(steps):
        rrect(d, [x, yy, x + cw, yy + 640], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        num_circle(cv, x + cw / 2, yy + 110, i + 1)
        draw_text(cv, (x + cw / 2, yy + 200), emo, S.F("sans_xb", 68),
                  anchor="ma")
        f, _ = fit_size(title, "serif_b", 37, cw - 60, 24)
        draw_text(cv, (x + cw / 2, yy + 306), title, f, ESPRESSO,
                  anchor="ma")
        yy2 = yy + 386
        for seg in wrap(body, S.F("sans_md", 23), cw - 80):
            draw_text(cv, (x + cw / 2, yy2), seg, S.F("sans_md", 23), INK,
                      anchor="ma")
            yy2 += 38
        if i < 3:
            arrow_right(cv, x + cw + 2, yy + 300, 34)
        x += cw + gap
    yy += 640 + 56
    formula_chip(cv, W / 2, yy + 30, "you type  \u2192  the sheet thinks")
    hand_note(cv, W / 2, yy + 150, "it really is that simple", 52, S.BRASS,
              "ma")
    footer(cv)
    save(cv, "12_how_it_works", probes=[(400, 500, "step1"),
                                        (1950, 500, "step4")])
    return cv


# ---------------------------------------------------------------------------
# 13 — google sheets
# ---------------------------------------------------------------------------
def img13():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "COMPATIBILITY", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Made for Excel, happy in Google Sheets", 78)
    y = chips_row(cv, W / 2, y + 14, [
        ("\u2705 Microsoft Excel 2016+", "ok"),
        ("\u2705 Google Sheets", "info"),
        ("\u2705 Windows & Mac", "espresso"),
        ("\u26A1 No macros — nothing to enable", "copper"),
    ])
    steps = [("1", "Buy & download", "Download the files from Etsy the "
              "moment you check out."),
             ("2", "Upload to Drive", "Drag the .xlsx into Google Drive "
              "from your browser."),
             ("3", "Open with Sheets", "Right-click the file \u2192 Open "
              "with \u2192 Google Sheets."),
             ("4", "Make a copy", "File \u2192 Save as Google Sheets — "
              "formulas carry over.")]
    d = ImageDraw.Draw(cv)
    sw_, gap = 528, 40
    x = (W - (sw_ * 4 + gap * 3)) / 2.0
    yy = y + 40
    for i, (n, title, body) in enumerate(steps):
        rrect(d, [x, yy, x + sw_, yy + 470], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        num_circle(cv, x + sw_ / 2, yy + 104, n)
        f, _ = fit_size(title, "serif_b", 36, sw_ - 60, 22)
        draw_text(cv, (x + sw_ / 2, yy + 196), title, f, ESPRESSO,
                  anchor="ma")
        yy2 = yy + 280
        for seg in wrap(body, S.F("sans_md", 23), sw_ - 80):
            draw_text(cv, (x + sw_ / 2, yy2), seg, S.F("sans_md", 23), INK,
                      anchor="ma")
            yy2 += 38
        if i < 3:
            arrow_right(cv, x + sw_ + 2, yy + 220, 34)
        x += sw_ + gap
    yy += 470 + 44
    br = browser(QUOTE.crop((0, 0, 1320, 560)), 860,
                 url="docs.google.com/spreadsheets  •  Catering Business "
                     "Manager")
    cv.alpha_composite(br, (150, yy))
    side_card(cv, 1080, yy + 6, 1170, 470, "\U0001F510", "What carries "
              "over to Sheets", ESPRESSO, [
        "Every formula, dropdown, conditional format and chart —",
        "the workbook is pure Excel, no macros or add-ons, so",
        "Google Sheets reads it natively. Your copy stays in your",
        "own Drive: no subscriptions, no accounts, no data leaves",
        "your laptop."])
    hand_note(cv, 620, yy + 486, "free updates for life, one purchase",
              48, S.BRASS, "la")
    footer(cv, "Novality Store — digital spreadsheets for people who'd "
            "rather be cooking")
    save(cv, "13_google_sheets", probes=[(400, 500, "step1"),
                                         (1950, 500, "step4")])
    return cv


# ---------------------------------------------------------------------------
# 14 — what you get
# ---------------------------------------------------------------------------
def img14():
    cv = canvas()
    y = kicker(cv, W / 2, 90, "YOUR DOWNLOAD", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Everything in the box", 90)
    d = ImageDraw.Draw(cv)
    cards = [
        ("\U0001F451", "PREMIUM EDITION", ESPRESSO, "20 TABS", [
            "1,500+ live formulas", "Classic + Fresh themes",
            "Charts, calendar, invoice, tax", "75 dropdown menus"]),
        ("\u2728", "EXAMPLE — FILLED IN", COPPER, "THE DEMO", [
            "14 events, 12 clients, 14 dishes", "The demo in the pictures",
            "See every formula working", "Type over it or clear it"]),
        ("\U0001F4D8", "USER GUIDE PDF", LATTE, "12 PAGES", [
            "Page-per-tab walkthrough", "Google Sheets import steps",
            "Troubleshooting & FAQ", "Works on any device"]),
        ("\U0001F381", "EXTRAS", S.INFO, "FREE", [
            "Start Here guide tab", "Editable dropdown lists",
            "Future updates included", "Lifetime access"]),
    ]
    cw, gap = 528, 40
    x = (W - (cw * 4 + gap * 3)) / 2.0
    yy = y + 40
    for emo, title, col, big, items in cards:
        rrect(d, [x, yy, x + cw, yy + 640], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, yy, x + cw, yy + 72], 16, fill=hexrgb(col))
        d.rectangle([x, yy + 36, x + cw, yy + 72], fill=hexrgb(col))
        draw_text(cv, (x + cw / 2, yy + 16), f"{emo} {title}",
                  S.F("serif_b", 30), WHITE, anchor="ma")
        draw_text(cv, (x + cw / 2, yy + 100), big, S.F("display_b", 46),
                  COLORS["copper"], anchor="ma")
        yi = yy + 210
        for it in items:
            draw_text(cv, (x + 56, yi), "\u2713", S.F("sans_b", 26),
                      COLORS["ok"])
            for j, seg in enumerate(wrap(it, S.F("sans_md", 23), cw - 130)):
                draw_text(cv, (x + 96, yi + j * 32), seg,
                          S.F("sans_md", 23), INK)
            nlines = len(wrap(it, S.F("sans_md", 23), cw - 130))
            yi += 34 + (0 if nlines == 1 else 30)
        x += cw + gap
    yy += 640 + 40
    # file strip
    rrect(d, [200, yy, 2200, yy + 190], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(cv, (240, yy + 18), "\U0001F4E6  Inside the download",
              S.F("serif_b", 30), ESPRESSO)
    files = ["PREMIUM Classic", "PREMIUM Fresh", "Example file",
             "User guide PDF"]
    fx, fy = 240, yy + 78
    for i, f_ in enumerate(files):
        chip_w = text_width("\U0001F4C4 " + f_, S.F("mono", 21)) + 44
        if fx + chip_w > 2160:
            fx, fy = 240, fy + 52
        rrect(d, [fx, fy, fx + chip_w, fy + 42], 8, fill=hexrgb("#F3EDDF"))
        draw_text(cv, (fx + 20, fy + 8), "\U0001F4C4 " + f_,
                  S.F("mono", 21), ESPRESSO)
        fx += chip_w + 14
    yy += 190 + 36
    chips_row(cv, W / 2, yy, [
        ("\u26A1 Instant digital download", "espresso"),
        ("\U0001F512 Formulas protected — your cells stay editable",
         "plum"),
        ("\U0001F4E6 One file, every device", "info"),
    ])
    footer(cv)
    save(cv, "14_what_you_get", probes=[(400, 500, "premium"),
                                        (1950, 500, "extras")])
    return cv


# ---------------------------------------------------------------------------
# 15 — FAQ
# ---------------------------------------------------------------------------
def img15():
    cv = canvas()
    y = kicker(cv, W / 2, 96, "GOOD TO KNOW", COPPER, 28, 10)
    y = headline(cv, W / 2, y, "Questions, answered", 92)
    d = ImageDraw.Draw(cv)
    qas = [
        ("Do I need Excel?",
         "No — the workbook opens in Microsoft Excel (2016 and newer) and "
         "in Google Sheets. The guide shows the import steps, and there "
         "are no macros to enable on either platform."),
        ("Is it hard to set up?",
         "It opens ready to go. A demo catering business is filled in so "
         "you can see how everything works — then you simply type over "
         "it with your own events, dishes and prices."),
        ("Can I trust the math?",
         "Yes. Over 1,500 formulas are pre-built and protected, so they "
         "can't be deleted by accident. You only ever edit the white "
         "input cells."),
        ("Will it fit my business?",
         "It's built for caterers, food trucks, bakeries and private "
         "chefs. Event types, categories and dropdown lists are all "
         "editable on the Setup tab."),
        ("What exactly do I receive?",
         "Instantly: the Premium edition in both themes, a filled-in "
         "example file, and a 12-page illustrated user guide. A 9-tab "
         "Basic edition is available separately."),
        ("What if I get stuck?",
         "The Start Here tab walks you through every section, and the "
         "guide covers each tab plus Google Sheets import. Novality "
         "Store is a message away."),
    ]
    cw, gap = 1102, 96
    x0 = (W - (cw * 2 + gap)) / 2.0
    yy = y + 30
    col_x = [x0, x0 + cw + gap]
    h = 300
    for i, (q, a) in enumerate(qas):
        x = col_x[i % 2]
        if i % 2 == 0 and i > 0:
            yy += h + 24
        rrect(d, [x, yy, x + cw, yy + h], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, yy, x + 84, yy + h], 16, fill=hexrgb(SOFT["copper"]))
        draw_text(cv, (x + 42, yy + h / 2 - 30), "Q", S.F("display_b", 52),
                  COPPER, anchor="ma")
        f, _ = fit_size(q, "serif_b", 36, cw - 140, 22)
        draw_text(cv, (x + 112, yy + 30), q, f, ESPRESSO)
        yy2 = yy + 100
        for seg in wrap(a, S.F("sans_md", 24), cw - 150):
            draw_text(cv, (x + 112, yy2), seg, S.F("sans_md", 24), INK)
            yy2 += 36
    yy += h + 40
    hand_note(cv, W / 2, yy, "made with love for small food businesses",
              50, S.BRASS, "ma")
    footer(cv)
    save(cv, "15_faq", probes=[(600, 600, "qa1"), (1900, 1100, "qa4")])
    return cv


# ---------------------------------------------------------------------------
def main():
    for i in range(1, 16):
        globals()[f"img{i:02d}"]()
    print("all 15 catering listing images written to", OUT)


if __name__ == "__main__":
    main()
