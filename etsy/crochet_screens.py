"""
crochet_screens - pixel renderings of the Crochet Craft Fair Tracker tabs
using the REAL demo business (crochet_tracker.demo.Demo).  Each screen_*
function returns an RGBA image of width SW that make_listing_images_crochet
wraps in browser chrome and make_user_guide_crochet crops for figures.
"""

import os
import sys
from datetime import date

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crochet_tracker import config as C
from crochet_tracker.theme import THEMES
from etsy import crochet_lib as L
from etsy.crochet_lib import (ALT, BAD, BORDER, CANVAS, CARD, COLORS, GOLD,
                              INFO, INK, MAUVE, MUTED, OK, PLUM, PRIMARY,
                              REORDER_COLORS, ROSE, SOFT, STATUS_COLORS,
                              WHITE)
from etsy.crochet_lib import (F, PRIORITY_COLORS, blocks_bar, draw_table,
                               draw_text, doughnut_chart, fit_size,
                               grouped_columns, hbar_chart, hexrgb,
                               kpi_card, line_series, rrect, section_bar,
                               sheet_header, text_width, wrap)

SW = 1320                                     # screen width (px)
BANNER = None                                 # set by _banner() lazily


def _banner():
    global BANNER
    if BANNER is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "assets", "banner_berry.png")
        BANNER = Image.open(p).convert("RGBA")
    return BANNER


def banner_band(img, y, h=250):
    """The watercolour banner band the real Dashboard tab uses."""
    b = _banner().crop((0, 0, 1600, 640)).resize((SW, int(SW * 0.4)),
                                                 Image.LANCZOS)
    band = b.crop((0, 0, SW, h))
    img.paste(band, (0, y), band)
    d = ImageDraw.Draw(img)
    d.rectangle([0, y + h - 3, SW, y + h], fill=hexrgb(BORDER))
    return y + h


def money(v, dec=0):
    return f"${v:,.{dec}f}"


ST_LABEL = {"ok": C.ST_OK, "low": C.ST_LOW, "out": C.ST_OUT}


def nav_row(img, y, prev, nxt):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, SW, y + 56], fill=hexrgb(PRIMARY))
    f = F("sans_sb", 17)
    draw_text(img, (36, y + 16), f"\u2B05  {prev}", f, "#F4E9F0")
    draw_text(img, (SW / 2, y + 16), "\U0001F3E0  Dashboard", f,
              "#F4E9F0", anchor="ma")
    draw_text(img, (SW - 36, y + 16), f"{nxt}  \u2B05\uFE0F", f,
              "#F4E9F0", anchor="ra")
    return y + 56


def finish(img, y, prev, nxt, min_h=720):
    y = max(y + 30, min_h)
    img2 = img.crop((0, 0, SW, y))
    out = Image.new("RGBA", (SW, y + 56), hexrgb(CANVAS))
    out.paste(img2, (0, 0))
    nav_row(out, y, prev, nxt)
    return out


def start(title, subtitle, h=3600, banner=False):
    img = Image.new("RGBA", (SW, h), hexrgb(CANVAS))
    y = 0
    if banner:
        y = banner_band(img, 0)
        f = F("display_b", 46)
        draw_text(img, (84, 66), "Willow & Wren Crochet Studio", f, PRIMARY)
        f = F("hand", 42)
        draw_text(img, (90, 130), "Crochet Craft Fair Tracker", f, ROSE)
        d = ImageDraw.Draw(img)
        pillw = 330
        rrect(d, [SW - pillw - 40, 74, SW - 40, 122], 24,
              fill=hexrgb("#FAF6F1"))
        draw_text(img, (SW - pillw - 22, 86), "\u2611 8 fairs booked",
                  F("sans_sb", 19), ROSE)
    y = sheet_header(img, title, subtitle, y=y)
    return img, y


def draw_pills(img, y, pills):
    x = 44
    d = ImageDraw.Draw(img)
    for text, color in pills:
        f = F("sans_sb", 18)
        w = text_width(text, f) + 34
        rrect(d, [x, y, x + w, y + 42], 21, fill=hexrgb(SOFT[color]))
        draw_text(img, (x + 17, y + 9), text, f, COLORS[color])
        x += w + 10
        if x > SW - 320:
            x = 44
            y += 52
    return y + 54


# ---------------------------------------------------------------------------
def screen_dashboard(m):
    a = m.agg
    img = Image.new("RGBA", (SW, 3900), hexrgb(CANVAS))
    d = ImageDraw.Draw(img)
    y = banner_band(img, 0)
    draw_text(img, (84, 64), "Willow & Wren Crochet Studio",
              F("display_b", 46), PRIMARY)
    draw_text(img, (90, 132), "Crochet Craft Fair Tracker", F("hand", 44),
              ROSE)
    rrect(d, [SW - 352, 76, SW - 40, 124], 24, fill=hexrgb("#FAF6F1"))
    draw_text(img, (SW - 334, 88),
              f"\U0001F4C5 {a['events_total']} fairs booked",
              F("sans_sb", 19), ROSE)

    y += 26
    draw_text(img, (44, y), "Business Snapshot", F("serif_b", 30), PRIMARY)
    y += 52
    cards = [
        ("\U0001F4B2 Gross Sales", money(a["revenue"], 2), "ok"),
        ("\U0001F4B0 Net Profit", money(a["profit"], 2), "primary"),
        ("\U0001F4C8 Margin", f"{a['margin']:.1%}", "rose"),
        ("\U0001FA9D Units Sold", f"{a['units']}", "gold"),
    ]
    cw, gap = 298, 12
    for i, (lbl, val, col) in enumerate(cards):
        kpi_card(img, 44 + i * (cw + gap), y, cw, lbl, val, col,
                 value_size=38)
    y += 128
    y = draw_pills(img, y, [
        (f"\U0001F3EA Fairs booked: {a['events_total']}", "primary"),
        (f"\u2705 {a['events_done']} worked so far", "ok"),
        (f"\U0001F4B3 Avg sale {money(a['aov'], 2)}", "rose"),
        (f"\U0001F9F5 Stock value {money(a['inv_value'], 2)}", "info"),
        (f"\U0001F4E6 {a['made_total']} items made", "gold"),
        (f"\u2705 {a['sell_through']:.0%} sell-through", "plum"),
    ])
    y += 14
    # charts -------------------------------------------------------------
    draw_text(img, (44, y), "Your year at a glance", F("serif_b", 30),
              PRIMARY)
    y += 54
    ch = 300
    rrect(d, [44, y, 640, y + ch], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    months = a["months"]
    grouped_columns(img, (84, y + 60, 600, y + ch - 24),
                    "Sales & net by month",
                    [C.MONTH_NAMES[t[0] - 1][:3] for t in months],
                    [("Sales", [t[1] for t in months], ROSE),
                     ("Net", [max(0, t[4]) for t in months], PRIMARY)],
                    fmt="${:,.0f}")
    rrect(d, [656, y, SW - 44, y + ch], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    pays = sorted([t for t in a["payments"] if t[1]],
                  key=lambda t: -t[1])[:4]
    cols = [ROSE, PRIMARY, GOLD, INFO]
    doughnut_chart(img, (676, y + 60, SW - 64, y + ch - 24),
                   "How customers paid",
                   [(t[0], int(t[1]) // 100 * 100, c)
                    for t, c in zip(pays, cols)],
                   center_word="sales", center_value=a["txns"])
    y += ch + 22
    # top products -------------------------------------------------------
    rrect(d, [44, y, 640, y + 250], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    top_rev = sorted(a["product_stats"], key=lambda r: -r[2])
    hbar_chart(img, (80, y + 58, 604, y + 234), "Top products by revenue",
               [(r[0], r[2]) for r in top_rev[:5]], color=PRIMARY)
    rrect(d, [656, y, SW - 44, y + 250], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (684, y + 18), "Best performers",
              F("serif_b", 23), PRIMARY)
    rows = [("\U0001F3C6 Best craft fair", a["best_event"]),
            ("\U0001FA9D Top seller", a["bs_units"]),
            ("\U0001F4B0 Top earner", a["bs_revenue"]),
            ("\U0001F3A8 Best margin", a["bs_margin"]),
            ("\U0001F4C9 Sell-through", f"{a['sell_through']:.0%} of "
             f"{a['made_total']} made")]
    yy = y + 64
    for lbl, val in rows:
        draw_text(img, (684, yy), lbl, F("sans_md", 19), MUTED)
        draw_text(img, (SW - 68, yy - 1), str(val), F("sans_sb", 19),
                  PRIMARY, anchor="ra")
        yy += 40
    y += 272
    # top products table ---------------------------------------------------
    y = section_bar(img, y, "\U0001F3AF  Top products (by revenue)") - 6
    top = sorted(a["product_stats"], key=lambda r: -r[2])[:6]
    rows = []
    for i, (name, units, rev, stock, margin, slow) in enumerate(top, 1):
        rows.append([{"t": str(i), "align": "c", "color": "muted"},
                     name,
                     {"t": str(units), "align": "c"},
                     {"t": money(rev, 2), "align": "r", "bold": True},
                     {"t": f"{margin:.0%}", "align": "c", "color": "rose"}])
    y = draw_table(img, 44, y, [60, 420, 130, 180, 120],
                   ["#", "Product", "Units", "Revenue", "Margin"], rows)
    y += 24
    # restock radar --------------------------------------------------------
    y = section_bar(img, y, "\U0001F504  Restock radar") - 6
    alerts = [
        ("\U0001F7E0", f"{a['low_products']} products below their minimum "
         f"— the Reorder List has the shopping list", "warn"),
        ("\U0001F9F5", f"{a['low_materials']} materials running low",
         "info"),
        ("\U0001F4B8", f"Estimated restock bill: {money(a['reorder_cost'], 2)}",
         "bad"),
        ("\U0001F4B5", f"Pricing calculator says: charge "
         f"{money(a['price_suggest'], 2)} for your next new design", "plum"),
    ]
    yy = y + 6
    for emo, txt, col in alerts:
        rrect(d, [44, yy, SW - 44, yy + 54], 10, fill=hexrgb(SOFT[col]))
        draw_text(img, (66, yy + 12), emo, F("sans_sb", 22))
        draw_text(img, (108, yy + 13), txt, F("sans_md", 21), COLORS[col])
        yy += 62
    y = yy + 6
    return finish(img, y, "Sales Log", "Product Catalog")


# ---------------------------------------------------------------------------
def screen_catalog(m):
    img, y = start("\U0001F9F6  Product Catalog",
                   "One row for everything you make — prices, costs, stock "
                   "and margins at a glance")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Products: {len(m.products)}", "primary"),
        (f"Avg price {money(sum(p['price'] for p in m.products) / len(m.products), 2)}",
         "rose"),
        (f"Stock value {money(a['inv_value'], 2)}", "info"),
        (f"! {a['low_products']} low on stock", "warn"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001F4CB  Your products") - 6
    rows = []
    for p in m.products[:11]:
        bg, fg = STATUS_COLORS[ST_LABEL[p["status"]]]
        rows.append([
            p["sku"],
            {"t": p["name"], "bold": True},
            {"t": money(p["price"], 2), "align": "r"},
            {"t": money(p["unit_cost"], 2), "align": "r",
             "color": "muted"},
            {"t": money(p["profit"], 2), "align": "r", "color": "ok",
             "bold": True},
            {"t": f"{p['margin']:.0%}", "align": "c", "color": "rose"},
            {"t": str(p["stock"]), "align": "c", "bold": True},
            {"t": ST_LABEL[p["status"]], "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [96, 330, 120, 120, 120, 100, 100, 220],
                   ["SKU", "Product", "Price", "Cost", "Profit", "Margin",
                    "Stock", "Status"], rows)
    y += 18
    draw_text(img, (44, y), "Margin bars — profit as a share of price",
              F("serif_b", 24), PRIMARY)
    y += 44
    for i, p in enumerate(m.products[:8]):
        yy = y + i * 40
        f = F("sans_md", 18)
        draw_text(img, (44, yy), p["name"], f, INK)
        blocks_bar(img, (420, yy - 6, 1080, yy + 26), p["margin"], n=36,
                   fg=ROSE)
        draw_text(img, (1100, yy - 1), f"{p['margin']:.0%}",
                  F("sans_sb", 18), PRIMARY)
    y += 8 * 40 + 16
    return finish(img, y, "Dashboard", "Yarn & Materials")


# ---------------------------------------------------------------------------
def screen_materials(m):
    img, y = start("\U0001F9F5  Yarn & Materials",
                   "Your whole stash with costs — and what's left on the "
                   "shelf")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Materials: {len(m.materials)}", "plum"),
        (f"Stash value {money(sum(x['total'] for x in m.materials), 2)}",
         "info"),
        (f"! {a['low_materials']} running low", "warn"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001F9F2  The stash") - 6
    rows = []
    for x in m.materials:
        bg, fg = REORDER_COLORS[C.RE_YES if x["remaining"] <= x["threshold"]
                                 else C.RE_NO]
        rows.append([
            {"t": x["name"], "bold": True},
            x["color"],
            x["weight"],
            {"t": f"{x['purchased']} {x['unit']}", "align": "c"},
            {"t": f"{x['used']}", "align": "c", "color": "muted"},
            {"t": str(x["remaining"]), "align": "c", "bold": True},
            {"t": money(x["cost_unit"], 2), "align": "r"},
            {"t": "Reorder" if x["remaining"] <= x["threshold"] else "OK",
             "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [300, 110, 160, 130, 100, 120, 120, 150],
                   ["Material", "Colour", "Weight", "Bought", "Used",
                    "Left", "Cost/unit", "Status"], rows)
    y += 24
    return finish(img, y, "Product Catalog", "Made & Stocked")


# ---------------------------------------------------------------------------
def screen_production(m):
    img, y = start("\U0001F4E6  Made & Stocked",
                   "Log what you make — stock counts itself, batch by batch")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Batches: {len(m.production)}", "ok"),
        (f"Made: {a['made_total']}", "gold"),
        (f"Sold: {a['units']}", "rose"),
        (f"On the shelf: {sum(p['stock'] for p in m.products)}", "info"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001F9F1  Production batches") - 6
    rows = []
    for b in m.production:
        rows.append([
            {"t": b["product"], "bold": True},
            {"t": b["date"].strftime("%d %b"), "align": "c"},
            {"t": str(b["made"]), "align": "c"},
            {"t": str(b["taken"]), "align": "c", "color": "muted"},
            {"t": str(b["sold"]), "align": "c"},
            {"t": str(b["current"]), "align": "c", "bold": True},
            {"t": str(b["available"]), "align": "c", "color": "ok"},
            {"t": b["notes"] or "", "color": "muted"},
        ])
    y = draw_table(img, 44, y, [330, 110, 100, 110, 100, 120, 120, 200],
                   ["Product", "Date", "Made", "Taken", "Sold", "In stock",
                    "Free", "Notes"], rows)
    y += 24
    return finish(img, y, "Yarn & Materials", "Craft Fairs")


# ---------------------------------------------------------------------------
def screen_events(m):
    img, y = start("\U0001F3EA  Craft Fairs",
                   "Book the fair, log the costs — the profit maths runs "
                   "itself")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Fairs booked: {a['events_total']}", "gold"),
        (f"Fair costs {money(a['fees'], 2)}", "warn"),
        (f"Sales {money(a['revenue'], 2)}", "ok"),
        (f"Net {money(a['profit'], 2)}", "info"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001F4C5  The season") - 6
    rows = []
    for e in m.events:
        net_col = "ok" if e["net"] > 0 else ("bad" if e["net"] < 0
                                             else "muted")
        rows.append([
            {"t": e["date"].strftime("%d %b %Y"), "bold": True},
            {"t": e["name"], "bold": True},
            {"t": money(e["sales"], 2), "align": "r"},
            {"t": money(e["total"], 2), "align": "r", "color": "muted"},
            {"t": money(e["cogs"], 2), "align": "r", "color": "muted"},
            {"t": money(e["net"], 2), "align": "r", "bold": True,
             "color": net_col},
            {"t": f"{e['margin']:.0%}", "align": "c", "color": net_col},
            {"t": e["best"] or "—", "color": "muted"},
        ])
    y = draw_table(img, 44, y, [130, 272, 130, 130, 130, 140, 100, 200],
                   ["Date", "Craft fair", "Sales", "Fair cost", "Goods",
                    "Net profit", "Margin", "Top seller"], rows)
    y += 24
    return finish(img, y, "Made & Stocked", "Sales Log")


# ---------------------------------------------------------------------------
def screen_sales(m):
    img, y = start("\U0001F4B0  Sales Log",
                   "One row per line item sold — totals, costs and "
                   "dashboards update live")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Entries: {a['txns']}", "ok"),
        (f"Units: {a['units']}", "gold"),
        (f"Gross {money(a['revenue'], 2)}", "rose"),
        (f"Avg sale {money(a['aov'], 2)}", "info"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001F9FE  Every sale this season") - 6
    ucost = {p["name"]: p["unit_cost"] for p in m.products}
    rows = []
    for s in m.sales[:18]:
        rows.append([
            {"t": s["date"].strftime("%d %b"), "align": "c"},
            {"t": s["event"], "color": "muted"},
            {"t": s["product"], "bold": True},
            {"t": str(s["qty"]), "align": "c"},
            {"t": money(s["unit"], 2), "align": "r"},
            {"t": money(s["qty"] * s["unit"] - s["discount"], 2),
             "align": "r", "bold": True, "color": "ok"},
            {"t": s["method"], "align": "c", "color": "muted"},
            {"t": money(ucost[s["product"]] * s["qty"], 2), "align": "r",
             "color": "muted"},
        ])
    y = draw_table(img, 44, y, [90, 250, 300, 70, 100, 130, 130, 130],
                   ["Date", "Craft fair", "Product", "Qty", "Price",
                    "Total", "Payment", "Cost"], rows)
    y += 16
    draw_text(img, (44, y), f"TOTALS — {a['units']} units · "
              f"{money(a['revenue'], 2)} gross · "
              f"{money(a['cogs'], 2)} cost of goods",
              F("sans_sb", 22), PRIMARY)
    y += 40
    return finish(img, y, "Craft Fairs", "Event Profit")


# ---------------------------------------------------------------------------
def screen_eventprofit(m):
    a = m.agg["event_profit"]
    img, y = start("\U0001F9EE  Event Profit",
                   "Pick a craft fair and see exactly what it earned you")
    d = ImageDraw.Draw(img)
    # picker
    rrect(d, [44, y + 6, SW - 44, y + 74], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (70, y + 22), "Craft fair:", F("sans_b", 22), INK)
    pw = text_width(a["event"], F("sans_sb", 22)) + 60
    rrect(d, [250, y + 16, 250 + pw, y + 64], 24, fill=hexrgb(SOFT["rose"]))
    draw_text(img, (280, y + 24), "\u25BE  " + a["event"],
              F("sans_sb", 22), ROSE)
    y += 96
    # money in / out
    half = (SW - 88 - 24) // 2
    for x0, title, color, items in (
            (44, "Money in", PRIMARY, [
                ("Items sold", str(a["units"])),
                ("Gross sales", money(a["gross"], 2)),
                ("Discounts given", money(a["discounts"], 2))]),
            (44 + half + 24, "Money out", ROSE, [
                ("Cost of goods", money(a["cogs"], 2)),
                ("Booth fee", money(a["booth"], 2)),
                ("Travel + parking", money(a["travel"] + a["parking"], 2)),
                ("Food + display", money(a["food"] + a["display"], 2))])):
        rrect(d, [x0, y, x0 + half, y + 66], 10, fill=hexrgb(color))
        draw_text(img, (x0 + 22, y + 16), title, F("serif_b", 26), WHITE)
        yy = y + 90
        for lbl, val in items:
            draw_text(img, (x0 + 10, yy), lbl, F("sans_md", 21), MUTED)
            draw_text(img, (x0 + half - 10, yy - 1), val,
                      F("sans_sb", 21), INK, anchor="ra")
            d.line([x0 + 10, yy + 34, x0 + half - 10, yy + 34],
                   fill=hexrgb(BORDER), width=1)
            yy += 52
        y2 = yy
    y = y2 + 14
    # verdict
    y = section_bar(img, y, "\U0001F3AF  The verdict") - 6
    cards = [
        ("Net profit", money(a["net"], 2), "ok"),
        ("Margin", f"{a['margin']:.0%}", "rose"),
        ("Breakeven", money(a["breakeven"], 2), "gold"),
        ("ROI", f"{a['roi']:.0%}", "plum"),
    ]
    cw, gap = 298, 12
    for i, (lbl, val, col) in enumerate(cards):
        kpi_card(img, 44 + i * (cw + gap), y + 6, cw, lbl, val, col,
                 value_size=38)
    y += 148
    for lbl, val, col in (
            ("Gross profit (sales − goods)", money(a["gross_profit"], 2),
             "ok"),
            ("True cost of the fair", money(a["total_cost"], 2), "bad"),
            ("Average sale", money(a["avg_sale"], 2), "info")):
        draw_text(img, (44, y), lbl, F("sans_md", 21), MUTED)
        draw_text(img, (SW - 44, y - 1), val, F("sans_sb", 21),
                  COLORS[col], anchor="ra")
        y += 44
    y += 10
    return finish(img, y, "Sales Log", "Reorder List")


# ---------------------------------------------------------------------------
def screen_reorder(m):
    img, y = start("\U0001F504  Reorder List",
                   "Everything running low, in one shopping list")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Need restocking: {a['low_products'] + a['low_materials']}",
         "warn"),
        (f"Estimated bill {money(a['reorder_cost'], 2)}", "bad"),
        (f"Urgent (sold out): 3", "primary"),
    ])
    y += 6
    y = section_bar(img, y, "\U0001FAA1  Products to restitch") - 6
    rows = []
    for p in m.products:
        if p["stock"] < p["min"]:
            prio = C.PR_URGENT if p["stock"] <= 0 else C.PR_HIGH
            bg, fg = PRIORITY_COLORS[prio]
            rows.append([
                {"t": p["name"], "bold": True},
                {"t": str(p["stock"]), "align": "c"},
                {"t": str(p["min"]), "align": "c", "color": "muted"},
                {"t": str(max(0, p["min"] * 2 - p["stock"])), "align": "c",
                 "bold": True},
                {"t": money(max(0, p["min"] * 2 - p["stock"])
                            * p["unit_cost"], 2), "align": "r"},
                {"t": prio.split(" ", 1)[1], "pill": (bg, fg),
                 "align": "c"},
            ])
    y = draw_table(img, 44, y, [340, 110, 110, 110, 150, 150],
                   ["Product", "Have", "Low at", "Buy", "Est. cost",
                    "Priority"], rows)
    y += 22
    y = section_bar(img, y, "\U0001F9F5  Yarn & materials to buy") - 6
    rows = []
    for x in m.materials:
        if x["remaining"] <= x["threshold"]:
            rows.append([
                {"t": x["name"], "bold": True},
                {"t": str(x["remaining"]), "align": "c"},
                {"t": str(x["threshold"]), "align": "c", "color": "muted"},
                {"t": str(max(0, x["threshold"] * 2 - x["remaining"])),
                 "align": "c", "bold": True},
                {"t": x["supplier"], "color": "muted"},
                {"t": money(max(0, x["threshold"] * 2 - x["remaining"])
                            * x["cost_unit"], 2), "align": "r"},
            ])
    y = draw_table(img, 44, y, [340, 110, 110, 110, 260, 150],
                   ["Material", "Left", "Low at", "Buy", "Supplier",
                    "Est. cost"], rows)
    y += 24
    return finish(img, y, "Event Profit", "Packing Checklist")


# ---------------------------------------------------------------------------
def screen_packing(m):
    img, y = start("\U0001F392  Packing Checklist",
                   "Tick your way out the door — nothing left behind")
    d = ImageDraw.Draw(img)
    pw = text_width("Summer Night Bazaar", F("sans_sb", 22)) + 60
    rrect(d, [44, y + 4, 44 + pw, y + 52], 24, fill=hexrgb(SOFT["rose"]))
    draw_text(img, (74, y + 12), "\u25BE  Summer Night Bazaar",
              F("sans_sb", 22), ROSE)
    draw_text(img, (44 + pw + 30, y + 12), "Packed: 14 of 21",
              F("sans_sb", 22), PRIMARY)
    y += 76
    x0, half = 44, (SW - 88 - 24) // 2
    for xi, (title, items) in enumerate(C.PACK_SECTIONS[:2]):
        xx = x0 + xi * (half + 24)
        rrect(d, [xx, y, xx + half, y + 60], 10, fill=hexrgb(PRIMARY))
        draw_text(img, (xx + 22, y + 14), title, F("serif_b", 24), WHITE)
        yy = y + 74
        for j, item in enumerate(items):
            rrect(d, [xx, yy, xx + half, yy + 48], 8, fill=hexrgb(
                ALT if j % 2 else CARD), outline=hexrgb(BORDER))
            done = m.packing.get(item)
            if done:
                L.check_poly(d, xx + 28, yy + 24, 20, OK, 5)
            else:
                rrect(d, [xx + 18, yy + 14, xx + 38, yy + 34], 5,
                      outline=hexrgb(MUTED), width=3)
            draw_text(img, (xx + 56, yy + 12), item, F("sans_md", 20),
                      INK if done else MUTED)
            yy += 56
        y2 = yy
    y = y2 + 24
    for xi, (title, items) in enumerate(C.PACK_SECTIONS[2:]):
        xx = x0 + xi * (half + 24)
        rrect(d, [xx, y, xx + half, y + 60], 10, fill=hexrgb(ROSE))
        draw_text(img, (xx + 22, y + 14), title, F("serif_b", 24), WHITE)
        yy = y + 74
        for i, item in enumerate(items):
            rrect(d, [xx, yy, xx + half, yy + 48], 8, fill=hexrgb(
                ALT if i % 2 else CARD), outline=hexrgb(BORDER))
            done = m.packing.get(item)
            if done:
                L.check_poly(d, xx + 28, yy + 24, 20, OK, 5)
            else:
                rrect(d, [xx + 18, yy + 14, xx + 38, yy + 34], 5,
                      outline=hexrgb(MUTED), width=3)
            draw_text(img, (xx + 56, yy + 12), item, F("sans_md", 20),
                      INK if done else MUTED)
            yy += 56
        y2 = yy
    y = y2 + 20
    return finish(img, y, "Reorder List", "Pricing Calculator")


# ---------------------------------------------------------------------------
def screen_pricing(m):
    p = m.agg["pricing"]
    img, y = start("\U0001F4B5  Pricing Calculator",
                   "Never underprice a hand-made item again")
    d = ImageDraw.Draw(img)
    half = (SW - 88 - 24) // 2
    # inputs
    rrect(d, [44, y, 44 + half, y + 66], 10, fill=hexrgb(PRIMARY))
    draw_text(img, (66, y + 16), "What goes into one item",
              F("serif_b", 24), WHITE)
    yy = y + 90
    ins = [("Yarn cost", money(p["material"], 2)),
           ("Packaging, labels", money(p["packaging"], 2)),
           ("Hours to make", f"{p['hours']:.1f} h"),
           ("Your hourly wage", money(p["wage"], 2)),
           ("Overhead", f"{p['overhead']:.0%}"),
           ("Target margin", f"{p['margin']:.0%}")]
    for lbl, val in ins:
        draw_text(img, (54, yy), lbl, F("sans_md", 21), MUTED)
        draw_text(img, (44 + half - 20, yy - 1), val, F("sans_sb", 21),
                  INK, anchor="ra")
        d.line([54, yy + 34, 44 + half - 20, yy + 34], fill=hexrgb(BORDER),
               width=1)
        yy += 52
    # outputs
    ox = 44 + half + 24
    rrect(d, [ox, y, ox + half, y + 66], 10, fill=hexrgb(ROSE))
    draw_text(img, (ox + 22, y + 16), "What to charge", F("serif_b", 24),
              WHITE)
    oy = y + 90
    outs = [("Your labour", money(p["labor"], 2)),
            ("Overhead", money(p["overhead_amt"], 2)),
            ("True cost to make", money(p["true_cost"], 2))]
    for lbl, val in outs:
        draw_text(img, (ox + 10, oy), lbl, F("sans_md", 21), MUTED)
        draw_text(img, (ox + half - 10, oy - 1), val, F("sans_sb", 21),
                  INK, anchor="ra")
        d.line([ox + 10, oy + 34, ox + half - 10, oy + 34],
               fill=hexrgb(BORDER), width=1)
        oy += 52
    # big price card
    rrect(d, [ox, oy + 8, ox + half, oy + 128], 14,
          fill=hexrgb(SOFT["primary"]), outline=hexrgb(PRIMARY))
    draw_text(img, (ox + 24, oy + 24), "Price at your margin",
              F("sans_sb", 21), MUTED)
    draw_text(img, (ox + half - 24, oy + 18), money(p["price"], 2),
              F("display_b", 58), PRIMARY, anchor="ra")
    draw_text(img, (ox + 24, oy + 88), f"Charm price {money(p['charm'], 2)}"
              f"  ·  profit {money(p['profit'], 2)} per item",
              F("sans_md", 19), ROSE)
    y = oy + 160
    draw_text(img, (44, y), "true cost \u00F7 (1 \u2212 margin) = price",
              F("mono", 26), PRIMARY)
    y += 48
    return finish(img, y, "Packing Checklist", "Monthly Summary")


# ---------------------------------------------------------------------------
def screen_monthly(m):
    img, y = start("\U0001F4C5  Monthly Summary",
                   "Your whole year, one row per month")
    a = m.agg
    y = draw_pills(img, y + 6, [
        (f"Year revenue {money(a['revenue'], 2)}", "primary"),
        (f"Year net {money(a['profit'], 2)}", "ok"),
        ("Best month: August", "gold"),
    ])
    y += 10
    d = ImageDraw.Draw(img)
    ch = 300
    rrect(d, [44, y, SW - 44, y + ch], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    months = a["months"]
    grouped_columns(img, (84, y + 60, SW - 84, y + ch - 24),
                    "Revenue, costs & net by month",
                    [C.MONTH_NAMES[t[0] - 1][:3] for t in months],
                    [("Revenue", [t[1] for t in months], ROSE),
                     ("Fees", [t[3] for t in months], GOLD),
                     ("Net", [max(0, t[4]) for t in months], PRIMARY)],
                    fmt="${:,.0f}")
    y += ch + 24
    y = section_bar(img, y, "\U0001F4C2  Month by month") - 6
    rows = []
    for (mm, rev, cogs, fees, net, units, markets, txns) in a["months"]:
        col = "ok" if net > 0 else ("bad" if net < 0 else "muted")
        rows.append([
            {"t": C.MONTH_NAMES[mm - 1], "bold": True},
            {"t": money(rev, 2), "align": "r"},
            {"t": money(cogs, 2), "align": "r", "color": "muted"},
            {"t": money(fees, 2), "align": "r", "color": "muted"},
            {"t": money(net, 2), "align": "r", "bold": True, "color": col},
            {"t": str(units), "align": "c"},
            {"t": str(markets), "align": "c", "color": "muted"},
        ])
    y = draw_table(img, 44, y, [200, 170, 170, 170, 180, 120, 120],
                   ["Month", "Revenue", "Cost of goods", "Fair fees",
                    "Net profit", "Units", "Fairs"], rows)
    y += 24
    return finish(img, y, "Pricing Calculator", "Start Here")


# ---------------------------------------------------------------------------
def screen_setup(m):
    img, y = start("\u2699\uFE0F  Lists & Settings",
                   "Your studio basics + every dropdown list in one place")
    d = ImageDraw.Draw(img)
    y = section_bar(img, y, "\U0001F3E2  Your studio") - 6
    st = m.settings
    for lbl, val in (("Business name", st["business"]),
                     ("Season note", st["message"]),
                     ("Currency symbol", st["currency"]),
                     ("Report year", str(st["year"])),
                     ("Your hourly wage", money(st["wage"], 2)),
                     ("Overhead %", f"{st['overhead']:.0%}"),
                     ("Target profit margin", f"{st['margin']:.0%}")):
        draw_text(img, (70, y), lbl, F("sans_md", 21), MUTED)
        draw_text(img, (SW - 70, y - 1), val, F("sans_sb", 21), PRIMARY,
                  anchor="ra")
        d.line([70, y + 34, SW - 70, y + 34], fill=hexrgb(BORDER), width=1)
        y += 52
    y += 16
    y = section_bar(img, y, "\U0001F5C2  Your dropdown lists (edit me)",
                    color=ROSE) - 6
    cols = [("Product categories", C.CATEGORIES[:6], "rose"),
            ("Payment methods", C.PAYMENT_METHODS[:6], "ok"),
            ("Yarn weights", C.YARN_WEIGHTS[:6], "plum"),
            ("Suppliers", C.SUPPLIERS[:6], "gold")]
    cw = (SW - 88 - 3 * 20) // 4
    for i, (title, items, col) in enumerate(cols):
        x0 = 44 + i * (cw + 20)
        rrect(d, [x0, y, x0 + cw, y + 56], 10, fill=hexrgb(COLORS[col]))
        f, _ = fit_size(title, "sans_sb", 19, cw - 24, 11)
        draw_text(img, (x0 + cw / 2, y + 14), title, f, WHITE, anchor="ma")
        yy = y + 70
        for j, it in enumerate(items):
            rrect(d, [x0, yy, x0 + cw, yy + 42], 8,
                  fill=hexrgb(ALT if j % 2 else CARD),
                  outline=hexrgb(BORDER))
            draw_text(img, (x0 + 16, yy + 9), it, F("sans_md", 19), INK)
            yy += 50
        y2 = yy
    y = y2 + 24
    return finish(img, y, "Monthly Summary", "Start Here")


# ---------------------------------------------------------------------------
def tabs_bar(m, edition="premium"):
    """The coloured tab strip, like the real workbook's sheet tabs."""
    keys = [k for k in C.EDITIONS[edition] if k != "data"]
    n = len(keys)
    img = Image.new("RGBA", (SW, 150), hexrgb("#EFE6EC"))
    d = ImageDraw.Draw(img)
    x = 24
    for k in keys:
        color = THEMES["berry"].tabs[k]
        label = C.SHEET_SHORT[k]
        f = F("sans_sb", 20)
        w = text_width(label, f) + 44
        h = 86 if k in ("dashboard", "guide") else 76
        rrect(d, [x, 120 - h, x + w, 120], 12, fill=hexrgb(color))
        draw_text(img, (x + 22, 120 - h + (h - 20) / 2), label, f, WHITE)
        x += w + 10
    draw_text(img, (24, 126), f"{n} linked tabs — "
              f"{'premium' if edition == 'premium' else 'basic'} edition",
              F("sans_md", 18), MUTED)
    return img
