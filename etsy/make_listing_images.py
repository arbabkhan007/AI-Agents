"""
make_listing_images.py - build the 15 Etsy listing images (2400x1800 JPEG,
<=1 MB each) for the Christmas Gift Tracker by Novality Store.

Run:  python3 -m etsy.make_listing_images
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import screenlib as S
from etsy import screens as SC
from etsy.screenlib import (ALT, BAD, BORDER, BURGUNDY, CANVAS, CARD, CREAM,
                            GOLD, INK, INFO, MUTED, OK, PINE, PINE2, PLUM,
                            SOFT, WARN, WHITE, blocks_bar, chip, COLORS,
                            draw_text, fit_size, hexrgb, rrect, shadow_paste,
                            text_width, wrap)

W, H = 2400, 1800
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
BANNER = os.path.join(ROOT, "assets", "banner_festive.png")

m, bk = S.get_model()
A = {}
DASH = SC.screen_dashboard(m, bk, A)
GIFTS = SC.screen_gifts(m, bk)
BUDGET = SC.screen_budget(m, bk)
ORDERS = SC.screen_orders(m, bk)
WRAPPING = SC.screen_wrapping(m, bk)
CARDS = SC.screen_cards(m, bk)
STOCKINGS = SC.screen_stockings(m, bk)
TODO = SC.screen_todo(m, bk)
WISHLIST = SC.screen_wishlist(m, bk)
SETUP = SC.screen_setup(m, bk)


# ---------------------------------------------------------------------------
# frame-level helpers
# ---------------------------------------------------------------------------
def canvas():
    return Image.new("RGBA", (W, H), hexrgb(CANVAS))


def strip(top=True, height=200):
    """Watercolour strip cropped from the festive banner art."""
    b = Image.open(BANNER).convert("RGBA")
    crop = b.crop((0, 0, 1600, 250)) if top else \
        b.crop((0, 640 - 250, 1600, 640))
    return crop.resize((W, height), Image.LANCZOS)


def kicker(cv, cx, y, text, color=BURGUNDY, size=30, track=10):
    d = ImageDraw.Draw(cv)
    f = F_ = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=F_) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=F_, fill=hexrgb(color))
        x += d.textlength(ch, font=F_) + track
    return y + size + 8


def headline(cv, cx, y, text, size=96, color=PINE, spec="display_xb"):
    f, _ = fit_size(text, spec, size, W - 220, 30)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.32)


def subline(cv, cx, y, text, size=32, color=INK, spec="sans_md"):
    f, _ = fit_size(text, spec, size, W - 260, 16)
    draw_text(cv, (cx, y), text, f, color, anchor="ma")
    return y + int(f.size * 1.7)


def chips_row(cv, cx, y, items, size=24, gap=26):
    """items = [(text, color_key)] centered row of pills."""
    fs = []
    total = 0
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


def browser(screen, width, url="novalitystore.etsy.com  •  Christmas Gift "
                               "Tracker — Instant Download"):
    """Browser chrome around a screen image. Returns RGBA."""
    chrome_h = 62
    sw = width - 6
    scale = sw / float(screen.width)
    sh = int(screen.height * scale)
    frame = Image.new("RGBA", (width, chrome_h + sh + 6),
                      hexrgb("#EFE7D7"))
    d = ImageDraw.Draw(frame)
    for i, c in enumerate(("#E96B5C", "#F2BD52", "#61C46A")):
        d.ellipse([26 + i * 34, 22, 44 + i * 34, 40], fill=hexrgb(c))
    # url pill
    pill = [width / 2.0 - 430, 14, width / 2.0 + 430, 48]
    rrect(d, pill, 17, fill=hexrgb(WHITE), outline=hexrgb("#DDD2BE"))
    f, _ = fit_size("🔒 " + url, "sans_md", 19, 830, 11)
    draw_text(frame, (width / 2.0 - (pill[2] - pill[0]) / 2.0 + 20, 23),
              "🔒 " + url, f, MUTED)
    scr = screen.resize((sw, sh), Image.LANCZOS)
    frame.paste(scr, (3, chrome_h))
    d.rectangle([0, chrome_h - 2, width, chrome_h], fill=hexrgb("#DDD2BE"))
    # rounded corners + border
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1,
                                            frame.height - 1], 18, fill=255)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.paste(frame, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, width - 1, out.height - 1],
                                          18, outline=hexrgb("#CBBFA8"),
                                          width=4)
    return out


def side_card(cv, x, y, w, h, emoji, title, color, lines=None,
              body_pad=26, line_gap=38, size=22, extra=None):
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
        draw_text(cv, (cx, cy + 52), note, S.F("hand", 44), BURGUNDY,
                  anchor="ma")
    return cy + 80


def num_circle(cv, cx, cy, n, r=52):
    d = ImageDraw.Draw(cv)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(GOLD))
    t = str(n)
    f = S.F("display_b", 58)
    draw_text(cv, (cx, cy - 34), t, f, WHITE, anchor="ma")


def arrow_right(cv, x, y, size=46, color=GOLD):
    d = ImageDraw.Draw(cv)
    d.line([x, y, x + size, y], fill=hexrgb(color), width=10)
    d.polygon([(x + size, y - 22), (x + size + 34, y),
               (x + size, y + 22)], fill=hexrgb(color))


def footer(cv, note=None):
    d = ImageDraw.Draw(cv)
    d.line([120, 1706, W - 120, 1706], fill=hexrgb(BORDER), width=2)
    draw_text(cv, (W / 2.0, 1726), "© Novality Store",
              S.F("sans_b", 26), PINE, anchor="ma")
    draw_text(cv, (W / 2.0, 1762), note or "Christmas Gift Tracker — "
              "Excel & Google Sheets  •  Instant Digital Download",
              S.F("sans_md", 22), MUTED, anchor="ma")


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
    # content probes
    ok = []
    for (x, y, label) in (probes or []):
        ok.append((label, rgb.getpixel((x, y))))
    # global stats
    hist = rgb.convert("L").histogram()
    total = sum(hist)
    dark = sum(hist[:80]) / total
    print(f"{name}.jpg  {size//1024} KB  darkpx {dark:.1%}  " +
          "  ".join(f"{l}={p}" for l, p in ok))
    return path


def hand_note(cv, x, y, text, size=42, color=BURGUNDY, anchor="la"):
    f = S.F("hand", size)
    for i, ln in enumerate(text.split("\n")):
        draw_text(cv, (x, y + i * int(size * 1.15)), ln, f, color,
                  anchor=anchor)


# ---------------------------------------------------------------------------
# 01 — hero
# ---------------------------------------------------------------------------
def img01():
    cv = canvas()
    cv.alpha_composite(strip(True, 190))
    y = kicker(cv, W / 2, 210, "NOVALITY STORE  PRESENTS", BURGUNDY, 30, 12)
    hand_note(cv, W / 2 - 330, y + 6, "The", 74, GOLD, "ra")
    draw_text(cv, (W / 2, y + 8), "Christmas Gift Tracker",
              S.F("display_xb", 122), PINE, anchor="ma")
    y = subline(cv, W / 2, y + 196,
                "The all-in-one Excel & Google Sheets planner for every "
                "gift, dollar and deadline — with a live countdown.",
                33)
    y = chips_row(cv, W / 2, y + 22, [
        ("⚡ Instant Download", "pine"), ("🤖 2,500+ Auto-Formulas", "burgundy"),
        ("🔓 No Macros — Nothing to Install", "gold")], 26)
    crop = DASH.crop((0, 0, 1320, A["after_gifts"]))
    br = browser(crop, 1560)
    shadow_paste(cv, br, (int(W / 2 - br.width / 2), y + 18), blur=30,
                 alpha=80)
    hand_note(cv, 1990, y + 120, "every number\non screen is\na live "
              "formula ✓", 36, BURGUNDY, "la")
    footer(cv)
    save(cv, "01_hero")


# ---------------------------------------------------------------------------
# 02 — dashboard tour
# ---------------------------------------------------------------------------
def img02():
    cv = canvas()
    y = kicker(cv, W / 2, 46, "THE DASHBOARD", GOLD, 26, 12)
    y = headline(cv, W / 2, y, "Your Christmas command centre", 78)
    y = chips_row(cv, W / 2, y + 8, [
        ("⏳ Live countdown", "burgundy"), ("💰 Overspend alerts", "gold"),
        ("📊 4 live charts", "pine"), ("⏰ Auto deadlines", "info"),
        ("🎯 Next-5 to-dos", "pine2")], 22)
    body_y = y + 26
    crop_h = A["after_charts"]
    bw = 1150
    crop = DASH.crop((0, 0, 1320, crop_h))
    br = browser(crop, bw)
    scale = (bw - 6) / 1320.0
    assert 62 + int(crop_h * scale) + 6 <= H - body_y - 50, \
        f"dashboard browser too tall: {62 + int(crop_h * scale) + 6} > " \
        f"{H - body_y - 50}"
    shadow_paste(cv, br, (60, body_y), blur=26, alpha=70)
    # right column: what's left + deadlines + formula
    x, w = 1250, 1090
    lines = [t[1] for t in SC._todo_lines(bk)][:7]
    yy = side_card(cv, x, body_y, w, 560, "🎯", "WHAT'S LEFT TO DO",
                   PINE2, lines, size=21, line_gap=35)
    dl_y = yy + 26
    dcard_h = 480
    d = ImageDraw.Draw(cv)
    rrect(d, [x, dl_y, x + w, dl_y + dcard_h], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [x, dl_y, x + w, dl_y + 62], 16, fill=hexrgb(BURGUNDY))
    d.rectangle([x, dl_y + 31, x + w, dl_y + 62], fill=hexrgb(BURGUNDY))
    draw_text(cv, (x + 24, dl_y + 13), "⏰ YOUR NEXT 5 DEADLINES",
              S.F("serif_b", 27), WHITE)
    ry = dl_y + 84
    for dl, label in m.agg["pool"][:5]:
        rrect(d, [x + 26, ry, x + 130, ry + 36], 8, fill=hexrgb(SOFT["gold"]))
        draw_text(cv, (x + 78, ry + 7), dl.strftime("%d %b"),
                  S.F("sans_sb", 19), INK, anchor="ma")
        f, _ = fit_size(label, "sans_md", 20, w - 420, 12)
        draw_text(cv, (x + 150, ry + 6), label, f, INK)
        nd = (dl - SC.TODAY).days
        chip(cv, (x + w - 160, ry - 1), f"{nd} days" if nd >= 0 else "overdue",
             SOFT["ok"] if nd > 7 else SOFT["warn"],
             OK if nd > 7 else WARN, size=17)
        ry += 52
    draw_text(cv, (x + 26, ry + 12),
              "…and 31 more, all re-dated from your event date.",
              S.F("hand", 40), BURGUNDY)
    fy = dl_y + dcard_h + 26
    formula_chip(cv, x + w / 2, fy + 40, "=EventDate − 45",
                 "every deadline is a formula — change the date, they all "
                 "move")
    footer(cv)
    save(cv, "02_dashboard")


# ---------------------------------------------------------------------------
# 03 — 13 tabs
# ---------------------------------------------------------------------------
TABS = [
    ("🏠", "Dashboard", BURGUNDY, "Live countdown, KPIs, charts & your next"
     " 5 deadlines", "4 charts"),
    ("🎁", "Gift Tracker", PINE2, "Every present: idea → bought → wrapped →"
     " given", "100+ rows"),
    ("💰", "Budget", GOLD, "10 categories, overspend alerts & automatic"
     " totals", "auto maths"),
    ("💡", "Wish List", PLUM, "Gift ideas ranked by must-have, captured all"
     " year", "12 ideas"),
    ("🛍️", "Shopping", INFO, "Wrapping, baking, decor — the quiet budget-"
     "eaters", "24 items"),
    ("📦", "Orders", PINE2, "Parcels, couriers & last-order dates, in one"
     " place", "8 orders"),
    ("🎀", "Wrapping", "#C1443C", "Hiding spots & tags, mirrored from your"
     " gift list", "secret mode"),
    ("💌", "Cards", WARN, "Bought → written → posted → replied, postage"
     " included", "auto postage"),
    ("🧦", "Stockings", "#8C5A2B", "Per-stocking budgets that stop the"
     " January regret", "16 stockings"),
    ("✅", "To-Do List", OK, "20 pre-loaded tasks, every deadline"
     " auto-dated", "auto dates"),
    ("⚙️", "Setup", MUTED, "Date, budget, currency, people & secret mode",
     "3-min setup"),
    ("📖", "Guide", BURGUNDY, "A full manual built in — every tab"
     " explained", "in-app help"),
]


def img03():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "ONE WORKBOOK", GOLD, 28, 12)
    y = headline(cv, W / 2, y, "13 tabs. Every December job, done.", 88)
    y = subline(cv, W / 2, y + 6,
                "Replaces your gift-list spreadsheet, budget file, order "
                "tracker and December to-do list.", 30)
    gx, gy = 70, y + 30
    cw, ch, gap = 552, 372, 24
    for i, (em, name, color, desc, stat) in enumerate(TABS):
        row, col = divmod(i, 4)
        x = gx + col * (cw + gap)
        yy = gy + row * (ch + gap)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, yy, x + cw, yy + ch], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, yy, x + cw, yy + 68], 16, fill=hexrgb(color))
        d.rectangle([x, yy + 34, x + cw, yy + 68], fill=hexrgb(color))
        draw_text(cv, (x + 22, yy + 14), f"{em}  {name}",
                  S.F("serif_b", 30), WHITE)
        ly = yy + 92
        f = S.F("sans_md", 21)
        for seg in wrap(desc, f, cw - 44):
            draw_text(cv, (x + 22, ly), seg, f, INK)
            ly += 30
        chip(cv, (x + 22, yy + ch - 58), stat, SOFT["gold"], INK, size=18)
    # hidden engine banner
    by = gy + 3 * (ch + gap) + 6
    d = ImageDraw.Draw(cv)
    rrect(d, [gx, by, gx + 4 * cw + 3 * gap, by + 108], 16,
          fill=hexrgb("#3A342B"))
    draw_text(cv, (W / 2, by + 18), "🔒  …plus the hidden _Data engine room —"
              " 2,500+ formulas & 56 dropdowns you never have to touch",
              S.F("sans_sb", 27), CREAM, anchor="ma")
    footer(cv)
    save(cv, "03_tabs")


# ---------------------------------------------------------------------------
# 04 — gifts
# ---------------------------------------------------------------------------
def img04():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TAB 2 — GIFTS", PINE2, 28, 12)
    y = headline(cv, W / 2, y, "Every present, one page", 88)
    body_y = y + 26
    br = browser(GIFTS, 1440)
    shadow_paste(cv, br, (60, body_y + max(0, (1092 - br.height) / 2)),
                 blur=26, alpha=70)
    x, w = 1560, 780

    def pipeline(cv2, x, yy, w, h):
        d = ImageDraw.Draw(cv2)
        ems = ["💡", "🛒", "✅", "🎀", "📦"]
        labels = ["Idea", "To Buy", "Bought", "Wrapped", "Given"]
        seg = w / 5.0
        for i, (em, lb) in enumerate(zip(ems, labels)):
            cx = x + seg * i + seg / 2
            draw_text(cv2, (cx, yy + 4), em, S.F("sans_sb", 62), INK,
                      anchor="ma")
            draw_text(cv2, (cx, yy + 88), lb, S.F("sans_sb", 21), MUTED,
                      anchor="ma")
            if i < 4:
                arrow_right(cv2, x + seg * (i + 1) - 44, yy + 44, 34)
        draw_text(cv2, (x + w / 2, yy + 132), "one dropdown — totals update "
                  "as you type", S.F("hand", 40), BURGUNDY, anchor="ma")
        return yy + 190

    yy = side_card(cv, x, body_y, w, 300, "🎁", "THE GIFT PIPELINE", PINE2,
                   extra=pipeline)
    yy = side_card(cv, x, yy + 26, w, 350, "🧮", "BUDGET MATHS, DONE", GOLD, [
        "Budget vs actual — per gift and per person",
        "Under budget = green  •  over = red",
        "Average spend per person: $77, calculated live",
        "Wrapped, given & still-to-buy counted for you"])
    yy = side_card(cv, x, yy + 26, w, 380, "⏰", "BUY-BY DATES, AUTOMATIC",
                   BURGUNDY, [
        "Every gift gets a buy-by date from your event date",
        "A week out it turns amber — overdue turns red",
        "Nothing gets bought in a panic on 24 December"])
    formula_chip(cv, x + w / 2, yy + 46, "=EventDate − 45")
    draw_text(cv, (W / 2 - 660, body_y + 1092 + 120),
              "The gift list feeds every other tab — wrapping, budget and "
              "dashboard all read from it.", S.F("sans_md", 26), MUTED,
              anchor="ma")
    hand_note(cv, W / 2 + 620, body_y + 1092 + 92,
              "one list, zero double-entry ✓", 42, BURGUNDY)
    footer(cv)
    save(cv, "04_gifts")


# ---------------------------------------------------------------------------
# 05 — budget
# ---------------------------------------------------------------------------
def img05():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TAB 3 — BUDGET", GOLD, 28, 12)
    y = headline(cv, W / 2, y, "Watch every dollar", 88)
    body_y = y + 26
    br = browser(BUDGET, 1440)
    shadow_paste(cv, br, (60, body_y + max(0, (1166 - br.height) / 2)),
                 blur=26, alpha=70)
    x, w = 1560, 780

    def alert(cv2, x, yy, w, h):
        d = ImageDraw.Draw(cv2)
        rrect(d, [x + 26, yy, x + w - 26, yy + 96], 12,
              fill=hexrgb(SOFT["warn"]), outline=hexrgb(WARN), width=3)
        f, _ = fit_size(m.agg["budget_alert"], "sans_sb", 22, w - 110, 12)
        draw_text(cv2, (x + 48, yy + 16), m.agg["budget_alert"], f, WARN)
        draw_text(cv2, (x + 48, yy + 124), "…that banner writes itself — "
                  "set your own alert level", S.F("hand", 40), BURGUNDY)
        return yy + 180

    yy = side_card(cv, x, body_y, w, 400, "🚨", "OVERSPEND ALERTS", BURGUNDY,
                   extra=alert)
    yy = side_card(cv, x, yy + 26, w, 400, "🧮", "AUTO vs MANUAL SPEND", GOLD,
                   [
        "Automatic: gifts, stockings, cards & shopping roll up themselves",
        "Manual: travel & one-offs — type them once",
        "Remaining & % used update the moment you type"])
    yy = side_card(cv, x, yy + 26, w, 340, "📋", "PLANNED FOR YOU", PINE, [
        "10 budget categories pre-loaded — edit or rename",
        "Demo budget of $1,500 to overwrite with your own",
        "Everything mirrors straight to the dashboard"])
    draw_text(cv, (W / 2 - 660, body_y + 1166 + 60),
              "Demo budget shown — $1,500 across 10 categories, ready to "
              "overwrite with your own.", S.F("sans_md", 26), MUTED,
              anchor="ma")
    footer(cv)
    save(cv, "05_budget")


# ---------------------------------------------------------------------------
# 06 — charts
# ---------------------------------------------------------------------------
def img06():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "ZERO CHART-EDITING", GOLD, 28, 12)
    y = headline(cv, W / 2, y, "Charts that update themselves", 88)
    y = subline(cv, W / 2, y + 6,
                "Six formula-driven charts — no chart editor, no refresh "
                "button, ever.", 30)
    a = m.agg
    rec = [r for r in a["recipients"] if r["gifts"]][:8]
    cards = [
        ("Spending per person", lambda box: S.hbar_chart(
            cv, box, "Spending per person",
            [(r["name"], r["spent"]) for r in rec], size=1.7)),
        ("Budget vs actual by category", lambda box: S.grouped_columns(
            cv, box, "Budget vs actual by category",
            [c["name"][:8] for c in a["categories"][:10]],
            [("Planned", [m.budget_planned.get(k, 0) for k in
                          ["gifts", "stockings", "wrapping", "cards", "food",
                           "baking", "decor", "party", "travel", "other"]],
              GOLD),
             ("Actual", [next((b["actual"] for b in a["budget_rows"]
                               if b["key"] == k), 0) for k in
                         ["gifts", "stockings", "wrapping", "cards", "food",
                          "baking", "decor", "party", "travel", "other"]],
              BURGUNDY)], size=1.7)),
        ("Where the gifts are at", lambda box: S.doughnut_chart(
            cv, box, "Where the gifts are at",
            [(s["name"], s["count"],
              {"💡 Idea": PLUM, "🛒 Need to Buy": WARN, "🛍️ Ordered": INFO,
               "✅ Purchased": OK, "🎀 Wrapped": GOLD,
               "📦 Delivered": PINE}[s["name"]]) for s in a["status_counts"]],
            size=1.7)),
        ("Bought vs still to buy", lambda box: S.stacked_columns(
            cv, box, "Gifts per person: bought vs to buy",
            [r["name"].split()[0] for r in rec[:8]],
            [("Bought", [r["bought"] for r in rec[:8]], PINE2),
             ("Still to buy", [r["to_buy"] for r in rec[:8]], GOLD)],
            size=1.7)),
    ]
    gx, gy = 70, y + 26
    cw, ch, gap = 1122, 640, 26
    for i, (title, fn) in enumerate(cards):
        row, col = divmod(i, 2)
        x = gx + col * (cw + gap)
        yy = gy + row * (ch + gap)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, yy, x + cw, yy + ch], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        fn((x + 60, yy + 120, x + cw - 50, yy + ch - 56))
    draw_text(cv, (W / 2, gy + 2 * ch + gap + 30),
              "Also on the dashboard: spending-by-category and "
              "gifts-per-person trends.", S.F("sans_md", 26), MUTED,
              anchor="ma")
    footer(cv)
    save(cv, "06_charts")


# ---------------------------------------------------------------------------
# 07 — orders
# ---------------------------------------------------------------------------
def img07():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TAB 6 — ORDERS", PINE2, 28, 12)
    y = headline(cv, W / 2, y, "Nothing arrives on the 27th", 84)
    body_y = y + 26
    br = browser(ORDERS, 1440)
    shadow_paste(cv, br, (60, body_y + max(0, (1066 - br.height) / 2)),
                 blur=26, alpha=70)
    x, w = 1560, 780

    def traffic(cv2, x, yy, w, h):
        d = ImageDraw.Draw(cv2)
        rows = [("#112-4471902-55", "101 days left", OK, SOFT["ok"]),
                ("#301-8822053-77", "7 days — due soon", WARN, SOFT["warn"]),
                ("#402-9901176-31", "2 days OVERDUE", BAD, SOFT["bad"])]
        for i, (no, txt, col, soft) in enumerate(rows):
            ry = yy + i * 78
            rrect(d, [x + 26, ry, x + w - 26, ry + 62], 12, fill=hexrgb(soft))
            d.ellipse([x + 48, ry + 21, x + 74, ry + 47], fill=hexrgb(col))
            draw_text(cv2, (x + 96, ry + 18), no, S.F("mono", 22), INK)
            draw_text(cv2, (x + w - 52, ry + 18), txt, S.F("sans_sb", 22),
                      col, anchor="ra")
        draw_text(cv2, (x + 26, yy + 3 * 78 + 14),
                  "the colour coding is a formula, not a chore",
                  S.F("hand", 40), BURGUNDY)
        return yy + 300

    yy = side_card(cv, x, body_y, w, 470, "🚦", "LATE = RED, AUTOMATICALLY",
                   PINE2, extra=traffic)
    yy = side_card(cv, x, yy + 26, w, 330, "🚚", "COURIER-PROOF", INFO, [
        "Order number, store, cost, expected & actual dates",
        "Days-left countdown from your event date",
        "Returns window auto-calculated (19 Jan 2027)"])
    yy = side_card(cv, x, yy + 26, w, 240, "📦", "DEMO SNAPSHOT", GOLD, [
        f"8 orders tracked  •  4 outstanding  •  0 late",
        f"$417 of parcels followed to the door"])
    draw_text(cv, (W / 2 - 660, body_y + 1066 + 80),
              "8 demo orders shown — order numbers, stores, costs and dates "
              "are all editable.", S.F("sans_md", 26), MUTED, anchor="ma")
    footer(cv)
    save(cv, "07_orders")


# ---------------------------------------------------------------------------
# 08 — wrapping & secret mode
# ---------------------------------------------------------------------------
def img08():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TAB 7 — WRAPPING", "#C1443C", 28, 12)
    y = headline(cv, W / 2, y, "Wrapped, hidden, found on time", 84)
    body_y = y + 26
    br = browser(WRAPPING, 1440)
    shadow_paste(cv, br, (60, body_y + max(0, (1166 - br.height) / 2)),
                 blur=26, alpha=70)
    x, w = 1560, 780

    def secret(cv2, x, yy, w, h):
        chip(cv2, (x + 30, yy + 6), "🙈  OFF — everyone sees everything",
             SOFT["muted"], MUTED, size=22)
        chip(cv2, (x + 30, yy + 76), "🔒  ON — ideas & costs hidden",
             SOFT["plum"], PLUM, size=22)
        draw_text(cv2, (x + 30, yy + 156), "one dropdown in Setup — no "
                  "formulas to write", S.F("hand", 40), BURGUNDY)
        return yy + 220

    yy = side_card(cv, x, body_y, w, 470, "🙈", "SECRET MODE", PLUM,
                   lines=["Hide gift ideas & costs from shoulder-surfers and"
                          " sneaky recipients"], extra=secret)
    yy = side_card(cv, x, yy + 26, w, 380, "🕵️", "WHERE DID I HIDE IT?",
                   "#C1443C", [
        "Hiding-spot dropdown: attic, closet, under-bed, garage…",
        "Grandma's photo frame → “top shelf in closet”",
        "Wrapped vs handed-over tracked separately"])
    yy = side_card(cv, x, yy + 26, w, 290, "🏷", "TAGS & RIBBONS", GOLD, [
        "To / From gift tags ready for every present",
        "13 wrapped, 5 to go, 7 waiting under the tree"])
    draw_text(cv, (W / 2 - 660, body_y + 1166 + 60),
              "The wrapping tab mirrors your gift list — nothing to copy "
              "across.", S.F("sans_md", 26), MUTED, anchor="ma")
    footer(cv)
    save(cv, "08_wrapping")


# ---------------------------------------------------------------------------
# 09 — cards & stockings
# ---------------------------------------------------------------------------
def img09():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TABS 8 & 9", WARN, 28, 12)
    y = headline(cv, W / 2, y, "The bits everyone forgets", 88)
    body_y = y + 34
    br1 = browser(CARDS, 1120, url="novalitystore.etsy.com  •  Card Tracker")
    br2 = browser(STOCKINGS, 1120, url="novalitystore.etsy.com  •  Stocking "
                    "Tracker")
    shadow_paste(cv, br1, (70, body_y), blur=24, alpha=70)
    shadow_paste(cv, br2, (1210, body_y), blur=24, alpha=70)
    yy = body_y + max(br1.height, br2.height) + 26
    chips_row(cv, W / 2, yy, [
        ("💌 Postage rolls into your budget", "warn"),
        ("🧦 Per-stocking budgets", "#8C5A2B".lower() and "gold"),
        ("✅ 13 of 16 fillers already bought", "ok")], 24)
    footer(cv)
    save(cv, "09_cards_stockings")


# ---------------------------------------------------------------------------
# 10 — todo & wishlist
# ---------------------------------------------------------------------------
def img10():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "TABS 10 & 4", OK, 28, 12)
    y = headline(cv, W / 2, y, "The plan that re-dates itself", 84)
    body_y = y + 30
    br1 = browser(TODO, 1120, url="novalitystore.etsy.com  •  To-Do List")
    br2 = browser(WISHLIST, 1120, url="novalitystore.etsy.com  •  Wish List")
    shadow_paste(cv, br1, (70, body_y), blur=24, alpha=70)
    shadow_paste(cv, br2, (1210, body_y), blur=24, alpha=70)
    yy = body_y + max(br1.height, br2.height) + 20
    d = ImageDraw.Draw(cv)
    rrect(d, [430, yy, 1970, yy + 120], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    formula_chip(cv, 620, yy + 60, "=EventDate − 45")
    draw_text(cv, (900, yy + 22), "20 classic tasks come pre-loaded — every "
              "deadline recalculates", S.F("sans_md", 26), INK)
    draw_text(cv, (900, yy + 64), "when you change your event date. Wish "
              "List ideas stay ready for next year.", S.F("sans_md", 26),
              INK)
    sy = yy + 160
    stats = [("✅ 7 of 20 tasks done in the demo", "ok"),
             ("⭐ 12 wish-list ideas — 5 must-haves", "plum"),
             ("⏰ Next deadline: 20 Nov (auto)", "warn")]
    for i, (txt, col) in enumerate(stats):
        cx = 180 + i * 700
        d2 = ImageDraw.Draw(cv)
        rrect(d2, [cx, sy, cx + 660, sy + 96], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(cv, (cx + 330, sy + 30), txt, S.F("sans_sb", 26),
                  COLORS[col], anchor="ma")
    footer(cv)
    save(cv, "10_todo_wishlist")


# ---------------------------------------------------------------------------
# 11 — occasions + setup
# ---------------------------------------------------------------------------
def img11():
    cv = canvas()
    y = kicker(cv, W / 2, 44, "SET IT UP ONCE", PINE, 28, 12)
    y = headline(cv, W / 2, y, "Not just Christmas", 84)
    y = subline(cv, W / 2, y + 4,
                "18 occasions come pre-loaded — set the date and the whole "
                "workbook re-dates itself.", 28)
    OCC = [("🎄", "Christmas"), ("🎅", "Secret Santa"), ("🕎", "Hanukkah"),
           ("🎉", "New Year's Eve"), ("❤️", "Valentine's"), ("💐",
                                                             "Mother's Day"),
           ("🎣", "Father's Day"), ("🐣", "Easter"), ("🎃", "Halloween"),
           ("🦃", "Thanksgiving"), ("🪔", "Diwali"), ("🎂", "Birthdays"),
           ("💍", "Weddings"), ("🍼", "Baby Shower"), ("🎓", "Graduation"),
           ("🏡", "Housewarming"), ("💌", "Anniversaries",), ("✡️",
                                                             "Bat Mitzvah")]
    gx, gy = 70, y + 24
    cw = int((W - 2 * gx - 5 * 24) / 6.0)
    ch, gap = 96, 24
    for i, item in enumerate(OCC):
        em, name = item[0], item[1]
        col = i % 6
        row = i // 6
        x = gx + col * (cw + gap)
        yy = gy + row * (ch + 18)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, yy, x + cw, yy + ch], 48, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        f, _ = fit_size(f"{em}  {name}", "sans_sb", 27, cw - 30, 14)
        draw_text(cv, (x + cw / 2.0, yy + (ch - f.size) / 2.0 - 2),
                  f"{em}  {name}", f, INK, anchor="ma")
    body_y = gy + 3 * (ch + 18) + 26
    br = browser(SETUP, 1120, url="novalitystore.etsy.com  •  Setup")
    shadow_paste(cv, br, (70, body_y), blur=24, alpha=70)
    x, w = 1240, 1090
    yy = side_card(cv, x, body_y, w, 500, "⚙️", "THREE MINUTES, THREE "
                   "THINGS", PINE, [
        "Your date — every countdown, deadline & to-do re-dates",
        "Your budget — alerts, charts & remaining-to-spend go live",
        "Your people — recipients, stockings and cards pre-fill"],
        size=25, line_gap=42)
    yy = side_card(cv, x, yy + 26, w, 320, "🌍", "WORKS EVERYWHERE", PINE2, [
        "US Dollars, Pounds, Euros & 8 more currencies",
        "Excel 2016+ / Microsoft 365 on Windows & Mac",
        "Google Sheets via upload — free with a Google account"], size=25,
        line_gap=42)
    footer(cv)
    save(cv, "11_occasions_setup")


# ---------------------------------------------------------------------------
# 12 — how it works
# ---------------------------------------------------------------------------
def img12():
    cv = canvas()
    y = kicker(cv, W / 2, 52, "FROM CHECKOUT TO PLANNING", GOLD, 28, 12)
    y = headline(cv, W / 2, y, "How it works", 96)
    steps = [
        ("BUY & DOWNLOAD", PINE, [
            "Check out here on Etsy.",
            "Your files are ready instantly —",
            "no waiting, no shipping, no account."]),
        ("OPEN IT ANYWHERE", PINE2, [
            "Works in Excel 2016+,",
            "Microsoft 365 and Mac.",
            "Prefer cloud? Upload to Google",
            "Sheets in four clicks."]),
        ("SET THREE THINGS", BURGUNDY, [
            "Your date. Your budget.",
            "Your people. Every tab, chart",
            "and deadline updates instantly."]),
    ]
    gx, cw, ch = 90, 680, 880
    gy = y + 150
    gap = (W - 2 * gx - 3 * cw) / 2.0
    for i, (title, color, lines) in enumerate(steps):
        x = gx + i * (cw + gap)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, gy, x + cw, gy + ch], 20, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        num_circle(cv, x + cw / 2, gy + 90, i + 1)
        draw_text(cv, (x + cw / 2, gy + 180), title, S.F("serif_b", 36),
                  color, anchor="ma")
        yy = gy + 260
        for ln in lines:
            draw_text(cv, (x + cw / 2, yy), ln, S.F("sans_md", 27), INK,
                      anchor="ma")
            yy += 46
        if i < 2:
            arrow_right(cv, x + cw + gap / 2 - 60, gy + ch / 2, 60, GOLD)
    draw_text(cv, (W / 2, gy + ch + 56), "No macros  •  nothing to "
              "install  •  your data stays on your device",
              S.F("sans_sb", 30), MUTED, anchor="ma")
    chips_row(cv, W / 2, gy + ch + 116, [("Excel 2016 +", "ok"),
              ("Microsoft 365", "ok"), ("Mac", "ok"),
              ("Google Sheets", "ok"), ("Windows", "ok")], 24)
    footer(cv)
    save(cv, "12_how_it_works")


# ---------------------------------------------------------------------------
# 13 — Google Sheets
# ---------------------------------------------------------------------------
def img13():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "PREFER THE CLOUD?", INFO, 28, 12)
    y = headline(cv, W / 2, y, "Google Sheets? Covered.", 92)
    y = subline(cv, W / 2, y + 6,
                "The same file works in both — start in Excel, move to "
                "Sheets whenever you like.", 30)
    body_y = y + 30
    # left: import steps card
    x, w = 70, 1080
    d = ImageDraw.Draw(cv)
    rrect(d, [x, body_y, x + w, body_y + 1030], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    steps = [
        ("1", "Open sheets.google.com, then  File → Import"),
        ("2", "Choose the  Upload  tab and drag your .xlsx in"),
        ("3", "Import settings:  Replace spreadsheet"),
        ("4", "Done — dropdowns, colours & charts come alive"),
    ]
    yy = body_y + 50
    for n, txt in steps:
        d.ellipse([x + 60, yy, x + 120, yy + 60], fill=hexrgb(SOFT["info"]))
        draw_text(cv, (x + 90, yy + 12), n, S.F("sans_b", 28), INFO,
                  anchor="ma")
        f, _ = fit_size(txt, "sans_md", 27, w - 300, 14)
        draw_text(cv, (x + 160, yy + 12), txt, f, INK)
        yy += 128
    # green button mock
    rrect(d, [x + 60, yy + 30, x + 620, yy + 110], 14, fill=hexrgb("#188038"))
    draw_text(cv, (x + 88, yy + 46), "Import data", S.F("sans_sb", 30),
              WHITE)
    hand_note(cv, x + 660, yy + 40, "4 clicks, honestly", 44, BURGUNDY)
    # right: converts card
    x2, w2 = 1210, 1120
    yy = side_card(cv, x2, body_y, w2, 560, "✅", "EVERYTHING CONVERTS", OK,
                   ["2,500+ formulas become Google-native formulas",
                    "56 dropdown menus arrive exactly as they are",
                    "Conditional formatting, colours & locked cells stay "
                    "put",
                    "Charts re-build themselves on import"], size=25,
                   line_gap=44)
    yy = side_card(cv, x2, yy + 26, w2, 430, "💡", "GOOD TO KNOW", GOLD, [
        "Google Sheets is free with any Google account",
        "Keep the .xlsx — it works in Excel, Numbers* and Sheets",
        "*Numbers: formulas import; layout may shift"], size=25, line_gap=44)
    footer(cv)
    save(cv, "13_google_sheets")


# ---------------------------------------------------------------------------
# 14 — what you get
# ---------------------------------------------------------------------------
def img14():
    cv = canvas()
    y = kicker(cv, W / 2, 48, "INSTANT DOWNLOAD", GOLD, 28, 12)
    y = headline(cv, W / 2, y, "What you get", 96)
    files = [
        ("🎁", "PREMIUM — Festive", "Classic Christmas reds & greens, "
         "watercolour accents", PINE),
        ("🎁", "PREMIUM — Minimal", "The same engine in a clean, modern "
         "look", "#3A342B"),
        ("✨", "EXAMPLE — filled in", "The demo you see in these pictures — "
         "every formula working", GOLD),
    ]
    gx, cw, ch, gap = 70, 552, 640, 24
    gy = y + 90
    for i, (em, name, desc, color) in enumerate(files):
        x = gx + i * (cw + gap)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, gy, x + cw, gy + ch], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, gy, x + cw, gy + 70], 16, fill=hexrgb(color))
        d.rectangle([x, gy + 35, x + cw, gy + 70], fill=hexrgb(color))
        draw_text(cv, (x + cw / 2, gy + 16), f"{em}  {name}",
                  S.F("serif_b", 28), WHITE, anchor="ma")
        # file glyph
        fx, fy = x + cw / 2 - 70, gy + 120
        d.rounded_rectangle([fx, fy, fx + 140, fy + 180], 14,
                            fill=hexrgb(SOFT["gold"]))
        d.polygon([(fx + 88, fy + 2), (fx + 138, fy + 52), (fx + 88,
                                                            fy + 52)],
                  fill=hexrgb("#EFE3C2"))
        draw_text(cv, (x + cw / 2, fy + 88), "XLSX", S.F("sans_b", 30), INK,
                  anchor="ma")
        ly = fy + 220
        f = S.F("sans_md", 22)
        for seg in wrap(desc, f, cw - 60):
            draw_text(cv, (x + 30, ly), seg, f, INK)
            ly += 32
        draw_text(cv, (x + 30, gy + ch - 60), "Excel & Google Sheets",
                  S.F("sans_sb", 20), MUTED)
        draw_text(cv, (x + cw - 30, gy + ch - 60), "instant download",
                  S.F("hand", 38), GOLD, anchor="ra")
    # specs band
    sy = gy + ch + 26
    d = ImageDraw.Draw(cv)
    rrect(d, [gx, sy, gx + 3 * cw + 2 * gap, sy + 320], 16,
          fill=hexrgb(CARD), outline=hexrgb(BORDER))
    rrect(d, [gx, sy, gx + 3 * cw + 2 * gap, sy + 64], 16, fill=hexrgb(PINE))
    d.rectangle([gx, sy + 32, gx + 3 * cw + 2 * gap, sy + 64], fill=hexrgb(PINE))
    draw_text(cv, (W / 2, sy + 14), "🔒  2,500+ formulas  •  56 dropdown "
              "menus  •  6 charts  •  46+ colour rules  •  13 tabs",
              S.F("serif_b", 30), WHITE, anchor="ma")
    checks = ["Formulas locked — nothing breaks by accident",
              "2 colour themes: Festive & Minimal",
              "100+ gift rows, 16 recipients, 16 stockings",
              "Free lifetime updates — re-download any time",
              "Works in Excel 2016+, Microsoft 365 & Google Sheets",
              "Your data never leaves your device"]
    for i, txt in enumerate(checks):
        col, row = divmod(i, 2)
        cx = gx + 60 + row * 1150
        cy = sy + 96 + col * 70
        S._check_poly(d, cx + 16, cy + 12, 26, OK, 5)
        draw_text(cv, (cx + 44, cy), txt, S.F("sans_md", 25), INK)
    hand_note(cv, W / 2, sy + 360, "buy once — re-download your updates "
              "forever 🎄", 46, BURGUNDY, "ma")
    footer(cv)
    save(cv, "14_what_you_get")


# ---------------------------------------------------------------------------
# 15 — FAQ & license
# ---------------------------------------------------------------------------
def img15():
    cv = canvas()
    cv.alpha_composite(strip(False, 130), (0, H - 130))
    y = kicker(cv, W / 2, 40, "BEFORE YOU BUY", BURGUNDY, 26, 12)
    y = headline(cv, W / 2, y, "Questions, answered", 80)
    faqs = [
        ("Will it work on my computer?", "Excel 2016 or later (Windows or "
         "Mac), Microsoft 365, or Google Sheets via upload. No macros, "
         "nothing to install."),
        ("Is it hard to set up?", "No. Type your date, budget and people — "
         "the built-in Guide tab walks you through it in three minutes."),
        ("Can I use it every year?", "Yes. Change the event date and every "
         "countdown, deadline and to-do re-dates itself."),
        ("Can I edit the formulas?", "Every input cell is open. The 2,500+ "
         "formulas are locked so nothing breaks by accident."),
        ("What about Google Sheets?", "File → Import → Upload → Replace "
         "spreadsheet. Dropdowns, colours and charts come along."),
        ("How much can I track?", "100+ gifts, 16 recipients, 16 stockings, "
         "24 shopping items, 20 to-dos and 14 cards."),
        ("What if I get stuck?", "A full Guide tab is built into the file, "
         "and we answer Etsy messages within a day."),
        ("Do I get updates?", "Yes — lifetime free updates. Re-download "
         "from Etsy any time for the latest version."),
    ]
    gx, gy, cw, ch, gap = 70, y + 20, 1150, 290, 24
    for i, (q, a) in enumerate(faqs):
        row, col = divmod(i, 2)
        x = gx + col * (cw + gap)
        yy = gy + row * (ch + 22)
        d = ImageDraw.Draw(cv)
        rrect(d, [x, yy, x + cw, yy + ch], 16, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(cv, (x + 34, yy + 28), "Q", S.F("display_b", 40), GOLD)
        draw_text(cv, (x + 84, yy + 34), q, S.F("serif_b", 30), PINE)
        ly = yy + 104
        f = S.F("sans_md", 23)
        for seg in wrap(a, f, cw - 150):
            draw_text(cv, (x + 84, ly), seg, f, INK)
            ly += 34
    ly2 = gy + 4 * (ch + 22) + 6
    d = ImageDraw.Draw(cv)
    rrect(d, [gx, ly2, gx + 2 * cw + gap, ly2 + 96], 16,
          fill=hexrgb("#3A342B"))
    draw_text(cv, (W / 2, ly2 + 18), "Personal use — one household per "
              "purchase  •  not for resale or redistribution",
              S.F("sans_sb", 26), CREAM, anchor="ma")
    draw_text(cv, (W / 2, ly2 + 56), "© Novality Store", S.F("sans_b", 24),
              "#F3D98B", anchor="ma")
    save(cv, "15_faq")


# ---------------------------------------------------------------------------
def main():
    for i, fn in enumerate([img01, img02, img03, img04, img05, img06, img07,
                            img08, img09, img10, img11, img12, img13, img14,
                            img15], 1):
        fn()
        print(f"  [{i}/15] done", flush=True)
    print("ALL 15 LISTING IMAGES BUILT ->", OUT)


if __name__ == "__main__":
    main()
