"""
make_user_guide_crochet.py - the illustrated "How to use it" PDF for the
Crochet Craft Fair Tracker, branded Novality Store.

12 A4 pages at 200 dpi (1654 x 2339 px each), rendered with the same design
system as the listing images and illustrated with REAL screenshots of the
workbook (etsy/crochet_screens.py, driven by the live demo data).

Run:  python3 -m etsy.make_user_guide_crochet
Out:  Crochet_Craft_Fair_Tracker_User_Guide.pdf  (repo root)
"""

import io
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etsy import crochet_lib as S
from etsy import crochet_screens as SC
from etsy.crochet_lib import (BORDER, CANVAS, CARD, ROSE, PRIMARY, INK,
                               INFO, MUTED, OK, PLUM, SOFT, WARN, WHITE,
                               GOLD, MAUVE, COLORS)
from etsy.crochet_lib import draw_text, fit_size, get_model, hexrgb, rrect
from etsy.make_listing_images_crochet import (browser, chips_row,
                                               hand_note, strip)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PDF = os.path.join(ROOT, "Crochet_Craft_Fair_Tracker_User_Guide.pdf")

PW, PH = 1654, 2339             # A4 at 200 dpi
DPI = 200.0
MX = 120                         # side margin
CW = PW - 2 * MX                 # content width 1414
BOTTOM = PH - 150                # footer zone starts here
TOTAL_PAGES = 12

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

PAGES = []
SW_CROP = 1320


# ---------------------------------------------------------------------------
# page helpers
# ---------------------------------------------------------------------------
def new_page():
    return Image.new("RGBA", (PW, PH), hexrgb(CANVAS))


def finish_page(img, n, titled=True):
    assert n <= TOTAL_PAGES
    d = ImageDraw.Draw(img)
    if titled:
        d.line([MX, PH - 118, PW - MX, PH - 118], fill=hexrgb(BORDER),
               width=2)
        draw_text(img, (MX, PH - 96), "Crochet Craft Fair Tracker — User "
                  "Guide", S.F("sans_md", 22), MUTED)
        draw_text(img, (PW - MX, PH - 96), f"Page {n} of {TOTAL_PAGES}",
                  S.F("sans_sb", 22), PRIMARY, anchor="ra")
        draw_text(img, (PW / 2.0, PH - 96), "© Novality Store",
                  S.F("sans_b", 22), PRIMARY, anchor="ma")
    PAGES.append(img)
    return img


def kicker(cv, cx, y, text, color=ROSE, size=24, track=9):
    d = ImageDraw.Draw(cv)
    f = S.F("sans_sb", size)
    total = sum(d.textlength(ch, font=f) + track for ch in text) - track
    x = cx - total / 2.0
    for ch in text:
        d.text((x, y), ch, font=f, fill=hexrgb(color))
        x += d.textlength(ch, font=f) + track
    return y + size * 2.1


def h1(img, y, kick, title, size=84, color=PRIMARY):
    y = kicker(img, PW / 2.0, y, kick, ROSE)
    f, _ = fit_size(title, "display_xb", size, CW, 30)
    draw_text(img, (PW / 2.0, y), title, f, color, anchor="ma")
    return y + int(f.size * 1.38)


def h2(img, y, text, color=PRIMARY, size=42, x=MX):
    d = ImageDraw.Draw(img)
    f = S.F("serif_b", size)
    d.rectangle([x, y + 4, x + 12, y + size + 4], fill=hexrgb(color))
    draw_text(img, (x + 32, y), text, f, color)
    return y + size + 26


def para(img, y, text, size=28, color=INK, x=MX, w=CW, lead=1.55):
    f = S.F("sans_md", size)
    from etsy.crochet_lib import wrap
    for line in wrap(text, f, w):
        draw_text(img, (x, y), line, f, color)
        y += int(size * lead)
    return y + 8


def bullets(img, y, items, size=25, x=MX, w=CW, color=OK, lead=1.5,
            gap=12, check=True):
    from etsy.crochet_lib import wrap
    d = ImageDraw.Draw(img)
    for it in items:
        f = S.F("sans_md", size)
        lines = wrap(it, f, w - 56)
        first = True
        for ln in lines:
            if first and check:
                S.check_poly(d, x + 14, y + size * 0.62, size * 0.95,
                             color, max(3, int(size * 0.16)))
            elif first:
                d.ellipse([x + 8, y + size * 0.35, x + 20,
                           y + size * 0.35 + 12], fill=hexrgb(color))
            draw_text(img, (x + 48, y), ln, f, INK)
            y += int(size * lead)
            first = False
        y += gap
    return y


def steps(img, y, items, size=26, x=MX, w=CW, r=27):
    from etsy.crochet_lib import wrap
    for i, (title, body) in enumerate(items, 1):
        d = ImageDraw.Draw(img)
        cy = y + r + 4
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=hexrgb(ROSE))
        draw_text(img, (x + r, cy - 19), str(i), S.F("display_b", 34),
                  WHITE, anchor="ma")
        tx = x + 2 * r + 26
        draw_text(img, (tx, y), title, S.F("sans_b", size), PRIMARY)
        yy = y + size + 8
        f = S.F("sans_md", size - 2)
        for ln in wrap(body, f, w - (2 * r + 26)):
            draw_text(img, (tx, yy), ln, f, INK)
            yy += int((size - 2) * 1.45)
        y = max(yy, cy + r + 10) + 16
    return y


def note_card(img, y, emoji, title, lines, color, h=None, size=24,
              x=MX, w=CW):
    from etsy.crochet_lib import wrap
    pad = 30
    f = S.F("sans_md", size)
    wrapped = []
    for ln in lines:
        wrapped.extend(wrap(ln, f, w - 2 * pad - 40))
    hh = h or (76 + len(wrapped) * int(size * 1.5) + 26)
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + w, y + hh], 16, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [x, y, x + w, y + 62], 16, fill=hexrgb(color))
    d.rectangle([x, y + 31, x + w, y + 62], fill=hexrgb(color))
    draw_text(img, (x + 26, y + 14), f"{emoji} {title}",
              S.F("serif_b", 30), WHITE)
    yy = y + 84
    for ln in wrapped:
        draw_text(img, (x + pad, yy), ln, f, INK)
        yy += int(size * 1.5)
    return y + hh


def sshot(img, y, screen, width=CW, url="Novality Store — Crochet "
           "Craft Fair Tracker", crop=None):
    sc = screen.crop((0, 0, SW_CROP, crop[1])) if crop else screen
    br = browser(sc, width, url=url)
    S.shadow_paste(img, br, (int(PW / 2 - br.width / 2), y), blur=22,
                   alpha=60)
    return y + br.height + 26


def qa_page(img, n, y_last, label):
    assert y_last <= BOTTOM, f"page {n} ({label}) overflows: {y_last} > " \
        f"{BOTTOM}"


# ---------------------------------------------------------------------------
# page 1 — cover
# ---------------------------------------------------------------------------
def p01():
    img = new_page()
    b = strip(True, 290)
    img.alpha_composite(b.resize((PW, 290), Image.LANCZOS), (0, 0))
    y = kicker(img, PW / 2, 330, "NOVALITY STORE  •  PREMIUM EDITION",
               ROSE, 26, 10)
    f, _ = fit_size("Crochet Craft Fair Tracker", "display_xb", 88, CW, 40)
    draw_text(img, (PW / 2, y), "Crochet Craft Fair Tracker", f, PRIMARY,
              anchor="ma")
    y += int(f.size * 1.34)
    d = ImageDraw.Draw(img)
    rrect(d, [PW / 2 - 300, y + 10, PW / 2 + 300, y + 96], 14,
          fill=hexrgb("#3A2430"))
    kicker(img, PW / 2, y + 32, "USER GUIDE", "#F3D98B", 30, 14)
    y += 130
    y = para(img, y, "Every stitch, every sale, every fair — your "
            "five-minute tour of the spreadsheet that does the maths "
            "for you.", 30, MUTED)
    crop = DASH.crop((0, 0, SW_CROP, 1000))
    y = sshot(img, y + 16, crop, 1300)
    y = chips_row(img, PW / 2, y + 20, [("Excel 2016 +", "ok"),
                  ("Microsoft 365", "ok"), ("Mac", "ok"),
                  ("Google Sheets", "ok"), ("No macros", "rose")], 24)
    hand_note(img, PW / 2, y + 36, "Your season, sorted", 56, ROSE, "ma")
    draw_text(img, (PW / 2, PH - 130), "Version 1.0  •  Berry & Mint "
              "themes included  •  © Novality Store", S.F("sans_md", 22),
              MUTED, anchor="ma")
    PAGES.append(img)


# ---------------------------------------------------------------------------
# page 2 — what you downloaded
# ---------------------------------------------------------------------------
def p02():
    img = new_page()
    y = h1(img, 110, "CHAPTER 1", "What you downloaded")
    y = para(img, y + 6, "Your purchase arrived as Excel workbooks "
            "(.xlsx). Nothing to install, nothing to enable — here is "
            "what each file is for.")
    files = [
        ("\U0001F451", "PREMIUM — Berry", "Your complete system: 14 "
         "linked tabs, 1,250+ formulas, warm autumn theme.", PRIMARY),
        ("\U0001F341", "PREMIUM — Mint", "The exact same engine in a "
         "fresh stitch-studio palette — pick whichever you enjoy "
         "opening.", MAUVE),
        ("\U0001F9EA", "EXAMPLE — Willow & Wren", "A filled-in demo of "
         "the PREMIUM file: 8 fairs, 22 sales, 12 products. Every "
         "screenshot in this guide is this file.", ROSE),
        ("\U0001F4D8", "USER GUIDE", "The booklet you are reading — "
         "every tab explained in plain English.", GOLD),
    ]
    for i, (emo, name, desc, col) in enumerate(files):
        y = note_card(img, y + 12, emo, name, [desc], col, size=26)
    y = para(img, y + 18, "Keep the files you edit in one folder (or "
            "your cloud drive) and keep the originals untouched — they "
            "are your backup.")
    qa_page(img, 2, y, "files")
    finish_page(img, 2)


# ---------------------------------------------------------------------------
# page 3 — quick start
# ---------------------------------------------------------------------------
def p03():
    img = new_page()
    y = h1(img, 110, "CHAPTER 2", "Quick start: five minutes")
    y = sshot(img, y + 4, SETUP, 1000, crop=(0, 900),
              url="Crochet Craft Fair Tracker — Lists & Settings")
    y = steps(img, y + 6, [
        ("Tell the file about your studio", "Open the Settings tab and "
         "type your business name, currency symbol, hourly wage, "
         "overhead % and target margin. Twenty seconds, and every "
         "formula in the file now speaks your numbers."),
        ("Add your products and yarn", "In Product Catalog, one row per "
         "thing you make: price, yarn cost, packaging, hours to make. "
         "In Yarn & Materials, log your stash with what each ball "
         "costs."),
        ("Log sales as they happen", "After a fair (or an online order), "
         "add one row per item sold in the Sales Log. The dashboard, "
         "monthly summary and reorder list update themselves."),
    ], size=27)
    y = note_card(img, y + 10, "\u2705", "The golden rule",
                  ["Type only in the open, cream-coloured cells. Every "
                   "formula cell is locked so the maths can never be "
                   "overwritten by accident."], OK, size=25)
    qa_page(img, 3, y, "quickstart")
    finish_page(img, 3)


# ---------------------------------------------------------------------------
# page 4 — dashboard
# ---------------------------------------------------------------------------
def p04():
    img = new_page()
    y = h1(img, 110, "CHAPTER 3", "The Dashboard tab")
    y = para(img, y + 6, "Your whole business on one screen — the "
            "banner, the numbers and every chart refresh themselves as "
            "you log sales.")
    crop = DASH.crop((0, 240, SW_CROP, 1420))
    y = sshot(img, y + 6, crop, CW)
    y = bullets(img, y + 14, [
        "Snapshot cards — gross sales, net profit, margin and units "
        "sold, always current",
        "Pipeline pills — fairs booked, worked so far, average sale, "
        "stock value, sell-through",
        "Charts — sales & net by month, how customers paid, top "
        "products by revenue",
        "Best performers — your top fair, top seller and best-margin "
        "product, named",
        "Restock radar — plain-English alerts with the numbers behind "
        "them",
    ], size=25)
    qa_page(img, 4, y, "dashboard")
    finish_page(img, 4)


# ---------------------------------------------------------------------------
# page 5 — catalog & pricing
# ---------------------------------------------------------------------------
def p05():
    img = new_page()
    y = h1(img, 110, "CHAPTER 4", "Products & pricing")
    y = h2(img, y + 2, "Product Catalog — one row per thing you make")
    y = sshot(img, y + 2, CATALOG, 1230, crop=(0, 800),
              url="Crochet Craft Fair Tracker — Product Catalog")
    y = h2(img, y + 8, "Pricing Calculator — what to charge")
    y = sshot(img, y + 2, PRICING, 1230, crop=(0, 700),
              url="Crochet Craft Fair Tracker — Pricing Calculator")
    y = para(img, y + 8, "True cost ÷ (1 − margin) = price — yarn, "
            "packaging, your hours and overhead, at the margin you "
            "set. It even suggests a charm price ($51.95, not $52.00) "
            "and the profit per item.")
    qa_page(img, 5, y, "catalog+pricing")
    finish_page(img, 5)


# ---------------------------------------------------------------------------
# page 6 — yarn & production
# ---------------------------------------------------------------------------
def p06():
    img = new_page()
    y = h1(img, 110, "CHAPTER 5", "Your stash and your makes")
    y = h2(img, y + 2, "Yarn & Materials — the shelf, counted")
    y = sshot(img, y + 2, MATERIALS, 1230, crop=(0, 700),
              url="Crochet Craft Fair Tracker — Yarn & Materials")
    y = h2(img, y + 8, "Made & Stocked — production batches")
    y = sshot(img, y + 2, PRODUCTION, 1230, crop=(0, 760),
              url="Crochet Craft Fair Tracker — Made & Stocked")
    y = bullets(img, y + 10, [
        "Bought minus used equals what's left — per ball, per colour",
        "Cost per ball rolls into every product's unit cost",
        "Anything under its reorder threshold is flagged automatically",
    ], size=24)
    qa_page(img, 6, y, "stash+production")
    finish_page(img, 6)


# ---------------------------------------------------------------------------
# page 7 — fairs & sales
# ---------------------------------------------------------------------------
def p07():
    img = new_page()
    y = h1(img, 110, "CHAPTER 6", "Fairs and sales")
    y = h2(img, y + 2, "Craft Fairs — book it, cost it, judge it")
    y = sshot(img, y + 2, EVENTS, 1230, crop=(0, EVENTS.height),
              url="Crochet Craft Fair Tracker — Craft Fairs")
    y = h2(img, y + 8, "Sales Log — one row per item sold")
    y = sshot(img, y + 2, SALES, 1230, crop=(0, 800),
              url="Crochet Craft Fair Tracker — Sales Log")
    y = para(img, y + 8, "Pick the fair, product and payment method "
            "from dropdowns and type the quantity — every figure "
            "updates on the spot.")
    qa_page(img, 7, y, "fairs+sales")
    finish_page(img, 7)


# ---------------------------------------------------------------------------
# page 8 — event profit & packing
# ---------------------------------------------------------------------------
def p08():
    img = new_page()
    y = h1(img, 110, "CHAPTER 7", "Was that fair worth it?")
    y = h2(img, y + 2, "Event Profit — the honest verdict")
    y = sshot(img, y + 2, EVENTPROFIT, 1230, crop=(0, EVENTPROFIT.height),
              url="Crochet Craft Fair Tracker — Event Profit")
    y = para(img, y + 6, "Pick a fair from the dropdown. Money in on "
            "the left, money out on the right, and the verdict cards "
            "give you net profit, margin, the sales you needed to "
            "break even and your return on every dollar spent on the "
            "booth.")
    y = h2(img, y + 4, "Packing Checklist — tick your way out the door")
    y = sshot(img, y + 2, PACKING, 1230, crop=(0, 580),
              url="Crochet Craft Fair Tracker — Packing Checklist")
    qa_page(img, 8, y, "eventprofit+packing")
    finish_page(img, 8)


# ---------------------------------------------------------------------------
# page 9 — reorder & monthly
# ---------------------------------------------------------------------------
def p09():
    img = new_page()
    y = h1(img, 110, "CHAPTER 8", "Restock and review")
    y = h2(img, y + 2, "Reorder List — the shopping list that writes itself")
    y = sshot(img, y + 2, REORDER, 1230, crop=(0, 880),
              url="Crochet Craft Fair Tracker — Reorder List")
    y = para(img, y + 6, "Products below their minimum and materials "
            "under their threshold land here automatically, with how "
            "many to buy, the estimated bill and a priority flag. Tick "
            "the Ordered column as you shop.")
    y = h2(img, y + 4, "Monthly Summary — your year, one row per month")
    y = sshot(img, y + 2, MONTHLY, 1230, crop=(0, 700),
              url="Crochet Craft Fair Tracker — Monthly Summary")
    qa_page(img, 9, y, "reorder+monthly")
    finish_page(img, 9)


# ---------------------------------------------------------------------------
# page 10 — lists & settings
# ---------------------------------------------------------------------------
def p10():
    img = new_page()
    y = h1(img, 110, "CHAPTER 9", "Make it yours")
    y = sshot(img, y + 4, SETUP, 1230, crop=(0, SETUP.height),
              url="Crochet Craft Fair Tracker — Lists & Settings")
    y = bullets(img, y + 10, [
        "Every dropdown list is yours — product categories, payment "
        "methods, yarn weights, suppliers",
        "Change your hourly wage or target margin once, and every "
        "price suggestion follows",
        "The season note is your scratchpad — it appears on the "
        "dashboard banner",
        "Colours, fonts and layout are part of the locked design, so "
        "the file stays beautiful",
    ], size=25)
    y = note_card(img, y + 8, "\U0001F5DD", "A note on locked cells",
                  ["The 1,250+ formula cells are protected so a stray "
                   "keystroke can't break the maths. If you understand "
                   "spreadsheets and truly want to tinker, most "
                   "spreadsheet apps let you unprotect a sheet — but "
                   "for almost everyone, the open cells are everything "
                   "you need."], PRIMARY, size=24)
    qa_page(img, 10, y, "setup")
    finish_page(img, 10)


# ---------------------------------------------------------------------------
# page 11 — FAQ
# ---------------------------------------------------------------------------
def p11():
    img = new_page()
    y = h1(img, 110, "CHAPTER 10", "Questions & answers")
    qa = [
        ("\U0001F4BB", "Which apps open this file?", [
            "Excel 2016 or newer on Windows, Excel for Mac, Microsoft "
            "365, and Google Sheets (File → Import → Upload → Replace "
            "spreadsheet). No macros — nothing to enable."], PRIMARY),
        ("\U0001F9F5", "Can I add more products, materials or fairs?", [
            "Yes — insert rows inside the existing tables and the "
            "formulas, dropdowns and charts keep working. The Start "
            "Here tab inside the file shows the safe way to do it."],
         MAUVE),
        ("\U0001F4B2", "Does it handle discounts and part-payments?", [
            "The Sales Log has a discount column, and the Event Profit "
            "tab nets everything out for you."], ROSE),
        ("\U0001F3EA", "What if a fair loses money?", [
            "It happens — the Craft Fairs tab shows it in red, Event "
            "Profit tells you the sales you'd have needed to break "
            "even, and the Monthly Summary keeps the season honest."],
         GOLD),
        ("\U0001F468\u200D\U0001F3A8", "Do I need both themes?", [
            "No — Berry and Mint are the same engine in two looks. "
            "Keep whichever you prefer as your working copy."], OK),
    ]
    for emo, q, lines, col in qa:
        y = note_card(img, y + 10, emo, q, lines, col, size=24)
    qa_page(img, 11, y, "faq")
    finish_page(img, 11)


# ---------------------------------------------------------------------------
# page 12 — licence & recap
# ---------------------------------------------------------------------------
def p12():
    img = new_page()
    y = h1(img, 110, "CHAPTER 11", "Licence & the short version")
    y = h2(img, y + 4, "Your licence")
    y = bullets(img, y, [
        "One business per purchase — use it for your own crochet "
        "studio, forever",
        "Please don't resell, share or redistribute the files",
        "Need it for a team or a gift for a maker friend? A second "
        "copy is the kind thing to do",
    ], size=25)
    y = h2(img, y + 6, "The whole system in one breath")
    y = para(img, y, "Set your wages and margin once. List your "
            "products and your yarn. Log each sale in one row. The "
            "dashboard tells you what's selling, the pricing "
            "calculator keeps you profitable, the reorder list keeps "
            "the shelf full, and the monthly summary keeps the season "
            "honest.")
    y = bullets(img, y + 10, [
        "14 tabs, 1,250+ locked formulas, 12 self-updating charts",
        "Works in Excel and Google Sheets, no macros",
        "Two themes, one filled-in example, this guide",
    ], size=25)
    hand_note(img, PW / 2, y + 30,
              "made for makers who'd rather be crocheting", 50, ROSE,
              "ma")
    draw_text(img, (PW / 2, PH - 240), "Crochet Craft Fair Tracker — "
              "User Guide", S.F("sans_b", 24), PRIMARY, anchor="ma")
    draw_text(img, (PW / 2, PH - 200), "© Novality Store", S.F("sans_b",
              24), PRIMARY, anchor="ma")
    qa_page(img, 12, y + 90, "licence")
    finish_page(img, 12)


# ---------------------------------------------------------------------------
# minimal PDF writer (JPEG pages, full control of quality)
# ---------------------------------------------------------------------------
def write_pdf(pages, path, title, author):
    jpgs = []
    for im in pages:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=92, optimize=True,
                               subsampling=1)
        jpgs.append((buf.getvalue(), im.width, im.height))

    n = len(jpgs)
    objs = {}

    def put(oid, body):
        objs[oid] = body

    kids = " ".join(f"{3 + 3 * i} 0 R" for i in range(n))
    put(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    put(2, f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    for i, (data, w, h) in enumerate(jpgs):
        wpt = w * 72.0 / DPI
        hpt = h * 72.0 / DPI
        put(3 + 3 * i,
            (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {wpt:.2f} "
             f"{hpt:.2f}] /Resources << /XObject << /Im{i} {5 + 3 * i} 0 R "
             f">> >> /Contents {4 + 3 * i} 0 R >>").encode())
        content = f"q {wpt:.2f} 0 0 {hpt:.2f} 0 0 cm /Im{i} Do Q".encode()
        put(4 + 3 * i,
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" +
            content + b"\nendstream")
        put(5 + 3 * i,
            (f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
             f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter "
             f"/DCTDecode /Length {len(data)} >>").encode() +
            b"\nstream\n" + data + b"\nendstream")
    esc = lambda s: s.replace("\\", r"\\").replace("(", r"\(").replace(
        ")", r"\)")
    put(3 + 3 * n, (f"<< /Title ({esc(title)}) /Author ({esc(author)}) "
                    f"/Creator (Novality Store) >>").encode())

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for oid in sorted(objs):
        offsets[oid] = out.tell()
        out.write(f"{oid} 0 obj\n".encode())
        out.write(objs[oid])
        out.write(b"\nendobj\n")
    xref_pos = out.tell()
    maxoid = max(objs)
    out.write(f"xref\n0 {maxoid + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for oid in range(1, maxoid + 1):
        out.write(f"{offsets.get(oid, 0):010d} 00000 n \n".encode())
    out.write((f"trailer\n<< /Size {maxoid + 1} /Root 1 0 R "
               f"/Info {3 + 3 * n} 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
               ).encode())
    with open(path, "wb") as fh:
        fh.write(out.getvalue())
    return os.path.getsize(path)

# ---------------------------------------------------------------------------
def main():
    for fn in (p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12):
        fn()
    assert len(PAGES) == TOTAL_PAGES, len(PAGES)
    size = write_pdf(PAGES, OUT_PDF,
                     "Crochet Craft Fair Tracker — User Guide",
                     "Novality Store")
    print(f"built {os.path.basename(OUT_PDF)}")
    print(f"  pages : {len(PAGES)}  (A4, {int(DPI)} dpi)")
    print(f"  size  : {size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
