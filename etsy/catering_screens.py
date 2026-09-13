"""
catering_screens - pixel renderings of the Catering Business Manager tabs
using the REAL demo business (catering_tracker.demo.Model).  Each screen_*
function returns an RGBA image of width SW that make_listing_images_catering
wraps in browser chrome and make_user_guide_catering crops for figures.
"""

import os
import sys
from datetime import date

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from catering_tracker import config as C
from etsy import catering_lib as L
from etsy.catering_lib import (ALT, BORDER, BRASS, CANVAS, CARD, COPPER,
                               ESPRESSO, INK, LATTE, MUTED, OK, SOFT,
                               STATUS_COLORS, PAY_STATUS_COLORS,
                               STOCK_COLORS, WHITE, WARN, BAD, INFO, PLUM)
from etsy.catering_lib import (COLORS, F, blocks_bar, chip, draw_table,
                               draw_text, doughnut_chart, fit_size, get_model,
                               grouped_columns, hbar_chart, hexrgb, kpi_card,
                               line_series, rrect, section_bar, sheet_header,
                               text_width, wrap)

SW = 1320                                     # screen width (px)
BANNER = None                                 # set by _banner() lazily


def _banner():
    global BANNER
    if BANNER is None:
        import os
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "assets", "banner_classic.png")
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


def nav_row(img, y, prev, nxt):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, SW, y + 56], fill=hexrgb(ESPRESSO))
    f = F("sans_sb", 17)
    draw_text(img, (36, y + 16), f"\u2B05  {prev}", f, "#F1E7D8")
    draw_text(img, (SW / 2, y + 16), "\U0001F3E0  Dashboard", f,
              "#F1E7D8", anchor="ma")
    draw_text(img, (SW - 36, y + 16), f"{nxt}  \u2B05\uFE0F", f,
              "#F1E7D8", anchor="ra")
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
        draw_text(img, (84, 66), "Saffron & Sage Catering Co.", f, ESPRESSO)
        f = F("hand", 42)
        draw_text(img, (90, 130), "Catering Business Manager", f, COPPER)
        d = ImageDraw.Draw(img)
        pillw = 330
        rrect(d, [SW - pillw - 40, 74, SW - 40, 122], 24,
              fill=hexrgb("#F8F4EC"))
        draw_text(img, (SW - pillw - 22, 86), "\u2611 12 events booked",
                  F("sans_sb", 19), COPPER)
    y = sheet_header(img, title, subtitle, y=y)
    return img, y


# ---------------------------------------------------------------------------
def screen_dashboard(m, anchors=None):
    a = m.agg
    img = Image.new("RGBA", (SW, 3800), hexrgb(CANVAS))
    y = banner_band(img, 0)
    f = F("display_b", 48)
    draw_text(img, (84, 64), a and "Saffron & Sage Catering Co." or "", f,
              ESPRESSO)
    draw_text(img, (90, 134), "Catering Business Manager",
              F("hand", 44), COPPER)
    d = ImageDraw.Draw(img)
    rrect(d, [SW - 352, 76, SW - 40, 124], 24, fill=hexrgb("#F8F4EC"))
    draw_text(img, (SW - 334, 88), "\U0001F4C5 12 events booked",
              F("sans_sb", 19), COPPER)

    y += 26
    draw_text(img, (44, y), "Business Snapshot", F("serif_b", 30), ESPRESSO)
    y += 52
    cards = [
        ("\U0001F4B2 Cash In", money(a["revenue"]), "ok"),
        ("\U0001F4B8 Cash Out", money(a["expenses"]), "bad"),
        ("\U0001F4B0 Net Profit", money(a["profit"]), "espresso"),
        ("\U0001F4C8 Margin", f"{a['margin']:.0%}", "copper"),
    ]
    cw, gap = 298, 12
    for i, (lbl, val, col) in enumerate(cards):
        kpi_card(img, 44 + i * (cw + gap), y, cw, lbl, val, col,
                 value_size=40)
    y += 128
    y = draw_pills(img, y, [
        (f"\U0001F3AD Events: {a['events_total']}", "espresso"),
        (f"\u2705 {a['events_confirmed']} confirmed", "ok"),
        (f"\U0001F389 {a['events_done']} done", "brass"),
        (f"\U0001F4B3 Avg order {money(a['avg_order'])}", "copper"),
        (f"\u23F0 Outstanding {money(a['outstanding'])}", "warn"),
        (f"\U0001F534 {a['overdue']} overdue", "bad"),
    ])
    y += 18
    # charts -------------------------------------------------------------
    draw_text(img, (44, y), "How the year is shaping up", F("serif_b", 30),
              ESPRESSO)
    y += 54
    ch = 300
    rrect(d, [44, y, 640, y + ch], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    months = [t for t in a["months"] if t[1] or t[2]][-6:]
    grouped_columns(img, (84, y + 60, 600, y + ch - 24),
                    "Revenue vs expenses by month",
                    [t[0] for t in months],
                    [("Revenue", [t[1] for t in months], COPPER),
                     ("Expenses", [t[2] for t in months], LATTE)],
                    fmt="${:,.0f}")
    rrect(d, [656, y, SW - 44, y + ch], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    types = [t for t in a["types"] if t[1]][:5]
    cols = [COPPER, LATTE, BRASS, INFO, PLUM]
    doughnut_chart(img, (676, y + 60, SW - 64, y + ch - 24),
                   "Revenue by event type",
                   [(t[0], t[1] // 100, c) for t, c in zip(types, cols)],
                   center_word="events", center_value=a["events_total"])
    y += ch + 22
    # best performers ----------------------------------------------------
    rrect(d, [44, y, 640, y + 240], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    hbar_chart(img, (80, y + 58, 604, y + 224), "Top clients by revenue",
               [(c, v) for c, v in a["clients_pool"][:5]], color=ESPRESSO)
    rrect(d, [656, y, SW - 44, y + 240], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (684, y + 18), "Best performers",
              F("serif_b", 23), ESPRESSO)
    rows = [("\U0001F3A9 Best event type", a["best_type"]),
            ("\U0001F91D Top client", a["best_client"]),
            ("\U0001F37D Food cost", f"{a['food_pct']:.1%} of revenue"),
            ("\U0001F9D1 Labor cost", f"{a['labor_pct']:.1%} of revenue")]
    yy = y + 66
    for lbl, val in rows:
        draw_text(img, (684, yy), lbl, F("sans_md", 19), MUTED)
        draw_text(img, (SW - 68, yy - 1), str(val), F("sans_sb", 19),
                  ESPRESSO, anchor="ra")
        yy += 42
    y += 262
    # upcoming -----------------------------------------------------------
    y = section_bar(img, y, "\U0001F4C5  Upcoming events") - 6
    up = a["upcoming"][:6]
    rows = []
    for dt, name, status in up:
        bg, fg = STATUS_COLORS[status]
        rows.append([{"t": dt.strftime("%a %d %b"), "bold": True},
                     name,
                     {"t": status, "pill": (bg, fg), "align": "c"}])
    y = draw_table(img, 44, y, [170, 700, 336],
                   ["Date", "Client — event", "Status"], rows)
    y += 24
    # dues ---------------------------------------------------------------
    y = section_bar(img, y, "\u23F0  Payments due") - 6
    rows = []
    for dt, who, amt in a["dues"][:5]:
        late = dt < date(2026, 9, 13)
        rows.append([{"t": dt.strftime("%d %b %Y"),
                      "color": "bad" if late else "ink", "bold": late},
                     who,
                     {"t": money(amt), "align": "r", "bold": True,
                      "color": "bad" if late else "espresso"}])
    y = draw_table(img, 44, y, [190, 700, 316], ["Due date", "Invoice",
                                                 "Amount"], rows)
    y += 24
    # alerts -------------------------------------------------------------
    y = section_bar(img, y, "\U0001F514  Alerts") - 6
    alerts = [
        ("\U0001F534", f"{a['overdue']} invoice overdue — follow up today",
         "bad"),
        ("\U0001F7E1", f"{a['low_stock']} ingredients at or below reorder "
         "point", "warn"),
        ("\U0001F9D1", f"{a['staff_unpaid']} shifts awaiting payroll",
         "info"),
        ("\U0001F527", f"{a['equip_service']} equipment items due for "
         "service", "plum"),
    ]
    yy = y + 6
    for emo, txt, col in alerts:
        d = ImageDraw.Draw(img)
        rrect(d, [44, yy, SW - 44, yy + 54], 10, fill=hexrgb(SOFT[col]))
        draw_text(img, (66, yy + 12), emo, F("sans_sb", 22))
        draw_text(img, (108, yy + 13), txt, F("sans_md", 21), COLORS[col])
        yy += 62
    y = yy + 6
    return finish(img, y, "Menu Costing", "Events")


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
def screen_events(m):
    img, y = start("\U0001F3AD  Events", "Every booking — pipeline to "
                    "plate — with live profit per event")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{a['events_total']} events in 2026", "espresso"),
        (f"\u2705 {a['events_confirmed']} confirmed", "ok"),
        (f"\U0001F4B0 {money(a['avg_profit'])} avg profit", "copper"),
        (f"\U0001F465 {int(a['avg_guests'])} avg guests", "info"),
    ])
    y += 6
    rows = []
    for e in m.events:
        bg, fg = STATUS_COLORS[e["status"]]
        rows.append([
            {"t": e["id"].replace("EV-2026-", "EV-"), "mono": True},
            e["date"].strftime("%d %b"),
            {"t": e["client"], "bold": True},
            e["type"],
            {"t": f"{e['guests']}", "align": "r"},
            {"t": money(e["cost"]), "align": "r", "color": "muted"},
            {"t": money(e["price"]), "align": "r", "bold": True},
            {"t": money(e["profit"]), "align": "r", "color": "ok"},
            {"t": e["status"], "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [96, 100, 250, 130, 78, 118, 118, 110, 148],
                   ["ID", "Date", "Client", "Type", "Guests", "Cost",
                    "Price", "Profit", "Status"], rows, row_h=44)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 120], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (76, y + 20), "\U0001F9EE  Profit is automatic",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 66), "Price − Cost = Profit, and margin is "
              "recomputed the moment you edit a cost line.",
              F("sans_md", 20), INK)
    y += 150
    return finish(img, y, "Dashboard", "Clients")


def screen_clients(m):
    img, y = start("\U0001F91D  Clients", "Who's booking, what they want, "
                    "and what they owe")
    rows = []
    for c in m.clients:
        bg, fg = {"\U0001F534 Unpaid": ("bad", "bad"),
                  "\U0001F7E0 Partial": ("warn", "warn"),
                  "\U0001F7E2 Paid": ("ok", "ok")}.get(
            c["status"], ("info", "info"))
        rows.append([
            {"t": c["name"], "bold": True},
            c["phone"],
            {"t": c["event_type"], "align": "c"},
            {"t": str(c["guests"]), "align": "r"},
            {"t": c["package"], "align": "c", "color": "copper"},
            {"t": money(c["quote"]), "align": "r", "bold": True},
            {"t": money(c["deposit"]), "align": "r", "color": "muted"},
            {"t": c["status"], "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [240, 160, 120, 80, 100, 120, 120, 148],
                   ["Client", "Phone", "Event", "Guests", "Package",
                    "Quote", "Deposit", "Status"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["copper"]))
    draw_text(img, (76, y + 18), "\U0001F4C8  Repeat business is tracked "
              "for you", F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), f"{m.agg['repeat_pct']:.0%} of this "
              "season's bookings come from returning clients.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Events", "Quote Builder")


# ---------------------------------------------------------------------------
def screen_quote(m):
    q = m.quote
    img, y = start("\U0001F9F1  Quote Builder",
                   "Price an event in 60 seconds — food, labor, kit and "
                   "delivery")
    d = ImageDraw.Draw(img)
    y = draw_pills(img, y, [
        (f"Sample quote — {q['client']}", "copper"),
        (q["date"].strftime("%d %b %Y"), "info"),
        (f"{q['guests']} guests", "espresso"),
    ])
    y += 8
    # inputs -------------------------------------------------------------
    panel_w = 560
    rrect(d, [44, y, 44 + panel_w, y + 560], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [44, y, 44 + panel_w, y + 56], 12, fill=hexrgb(LATTE))
    d.rectangle([44, y + 28, 44 + panel_w, y + 56], fill=hexrgb(LATTE))
    draw_text(img, (68, y + 12), "\u270F  You type these", F("serif_b", 25),
              WHITE)
    inputs = [
        ("Guests", f"{q['guests']}"),
        ("Food cost per guest", f"${q['food_pp']:.2f}"),
        ("Labor", money(q["labor"])),
        ("Equipment rental", money(q["equipment"])),
        ("Transport", money(q["transport"])),
        ("Other costs", money(q["other"])),
    ]
    yy = y + 84
    for lbl, val in inputs:
        draw_text(img, (76, yy), lbl, F("sans_md", 21), INK)
        f = F("mono", 21)
        w = text_width(val, f) + 26
        rrect(d, [44 + panel_w - 60 - w, yy - 6, 44 + panel_w - 60,
                  yy + 32], 6, fill=hexrgb("#F3EDDF"))
        draw_text(img, (44 + panel_w - 60 - w + 13, yy + 1), val, f,
                  ESPRESSO)
        yy += 62
    # outputs ------------------------------------------------------------
    ox = 44 + panel_w + 24
    ow = SW - 44 - ox
    rrect(d, [ox, y, ox + ow, y + 560], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [ox, y, ox + ow, y + 56], 12, fill=hexrgb(COPPER))
    d.rectangle([ox, y + 28, ox + ow, y + 56], fill=hexrgb(COPPER))
    draw_text(img, (ox + 24, y + 12), "\U0001F52C  The sheet does the math",
              F("serif_b", 25), WHITE)
    outs = [
        ("Food total", money(q["food_total"])),
        ("Total cost", money(q["cost_total"])),
        (f"Target profit (35%)", money(q["profit"])),
        ("Cost per guest", f"${q['cost_pp']:.2f}"),
    ]
    yy = y + 84
    for lbl, val in outs:
        draw_text(img, (ox + 24, yy), lbl, F("sans_md", 21), MUTED)
        draw_text(img, (ox + ow - 24, yy - 1), val, F("sans_sb", 22),
                  ESPRESSO, anchor="ra")
        yy += 50
    # big price ----------------------------------------------------------
    yy += 10
    rrect(d, [ox + 24, yy, ox + ow - 24, yy + 150], 12,
          fill=hexrgb(SOFT["espresso"]))
    draw_text(img, (ox + ow / 2, yy + 18), "QUOTE PRICE",
              F("sans_sb", 20), LATTE, anchor="ma")
    f = F("display_b", 72)
    draw_text(img, (ox + ow / 2, yy + 48), money(q["price"], 2), f, WHITE,
              anchor="ma")
    callout = (f"{money(q['price'], 2)} for the event  ·  "
               f"${q['per_guest']:.2f} per guest")
    cf, _ = fit_size(callout, "hand", 40, ow - 80, 24)
    draw_text(img, (ox + ow / 2, yy + 128), callout, cf, BRASS,
              anchor="ma")
    yy += 176
    for lbl, val in (("40% deposit to book", money(q["deposit"])),
                     ("Balance due after event", money(q["balance"]))):
        draw_text(img, (ox + 24, yy), lbl, F("sans_md", 21), INK)
        draw_text(img, (ox + ow - 24, yy - 1), val, F("sans_sb", 22),
                  OK, anchor="ra")
        yy += 52
    y += 560 + 26
    rrect(d, [44, y, SW - 44, y + 104], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (76, y + 18), "\U0001F527  Fully configurable",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Change your target margin, deposit % and "
              "tax on Setup — every quote re-prices itself.",
              F("sans_md", 20), INK)
    y += 134
    return finish(img, y, "Clients", "Menu Costing")


# ---------------------------------------------------------------------------
def screen_menu(m):
    img, y = start("\U0001F37D  Menu Costing",
                   "Cost every dish once — price it right forever")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{a['menu_items']} dishes costed", "espresso"),
        (f"\U0001F4C8 Avg margin {a['menu_margin']:.0%}", "ok"),
        ("Selling price auto-suggested", "copper"),
    ])
    rows = []
    for it in m.menu[:9]:
        rows.append([
            {"t": it["item"], "bold": True},
            {"t": it["category"], "align": "c", "color": "copper"},
            {"t": f"${it['cost']:.2f}", "align": "r", "color": "muted"},
            {"t": f"${it['price']:.2f}", "align": "r", "bold": True},
            {"t": f"${it['profit']:.2f}", "align": "r", "color": "ok"},
            {"t": f"{it['margin']:.0%}", "align": "c",
             "color": "ok" if it["margin"] >= 0.6 else "warn"},
        ])
    y = draw_table(img, 44, y, [380, 120, 130, 130, 130, 120],
                   ["Dish", "Type", "Cost", "Price", "Profit",
                    "Margin"], rows, row_h=46)
    y += 20
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, 660, y + 300], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    items = sorted(m.menu, key=lambda x: -x["margin"])[:6]
    hbar_chart(img, (80, y + 58, 626, y + 280), "Margin per dish",
               [(i["item"].split(" ")[0] + " " +
                 (i["item"].split(" ")[1] if len(i["item"].split(" ")) > 1
                  else ""), int(i["margin"] * 100)) for i in items],
               color=OK, fmt="{:,.0f}%")
    rrect(d, [684, y, SW - 44, y + 300], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (712, y + 20), "\U0001F9EE  The pricing formula",
              F("serif_b", 24), ESPRESSO)
    yy = y + 78
    for txt in (["Price  =  Cost ÷ (1 − target margin)",
                 "A $4.85 dish at 60% margin sells at $12.12 —",
                 "rounded to a menu-friendly $12.50.",
                 "Portion cost, ingredient list and profit",
                 "update automatically as costs change."]):
        draw_text(img, (712, yy), txt, F("mono", 19) if "=" in txt or
                  "$" in txt else F("sans_md", 20), INK)
        yy += 42
    y += 330
    return finish(img, y, "Quote Builder", "Inventory")


# ---------------------------------------------------------------------------
def screen_inventory(m):
    img, y = start("\U0001F9EA  Inventory",
                   "Know what's in the walk-in before you shop")
    a = m.agg
    y = draw_pills(img, y, [
        (f"Stock value {money(a['inv_value'])}", "espresso"),
        (f"\U0001F534 {a['low_stock']} to reorder", "bad"),
        ("Ticker status on every line", "info"),
    ])
    rows = []
    for it in m.inventory[:10]:
        bg, fg = STOCK_COLORS.get(it["status"], ("info", "info"))
        low = it["status"] != "\U0001F7E2 OK"
        rows.append([
            {"t": it["ingredient"], "bold": True},
            {"t": it["category"], "color": "copper"},
            {"t": f"{it['qty']:g} {it['unit']}", "align": "r",
             "color": "bad" if low else "ink", "bold": low},
            {"t": f"{it['min']:g}", "align": "r", "color": "muted"},
            {"t": f"${it['unit_cost']:.2f}", "align": "r"},
            {"t": money(it["value"]), "align": "r", "bold": True},
            {"t": it["status"], "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [280, 140, 140, 100, 120, 140, 152],
                   ["Ingredient", "Category", "On hand", "Min", "Unit cost",
                    "Value", "Status"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["ok"]))
    draw_text(img, (76, y + 18), "\U0001F6D2  Feeds the shopping list",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Anything below its minimum is added to "
              "the auto shopping list with quantities and cost estimates.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Menu Costing", "Shopping List")


def screen_shopping(m):
    img, y = start("\U0001F6D2  Shopping List",
                   "Built automatically from your events and stock levels")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{a['shop_lines']} lines to buy", "warn"),
        (f"Est. spend {money(a['shop_cost'])}", "copper"),
        ("Organised by supplier", "info"),
    ])
    rows = []
    for s in m.shopping:
        rows.append([
            {"t": s["event"].replace("EV-2026-", "EV-"), "mono": True},
            {"t": s["ingredient"], "bold": True},
            {"t": f"{s['required']:g}", "align": "r"},
            {"t": s["supplier"]},
            {"t": f"{s['available']:g}", "align": "r", "color": "muted"},
            {"t": (f"{s['to_buy']:g}" if s["to_buy"] else "—"), "align": "r",
             "bold": s["to_buy"] > 0, "color": "bad" if s["to_buy"] else
             "muted"},
            {"t": money(s["est_cost"]) if s["est_cost"] else "—",
             "align": "r", "bold": s["est_cost"] > 0},
            {"t": "\u2713" if s["purchased"] == "\u2713" else "",
             "align": "c", "tick": s["purchased"] == "\u2713"},
        ])
    y = draw_table(img, 44, y, [90, 270, 100, 190, 100, 90, 120, 120],
                   ["Event", "Ingredient", "Needed", "Supplier", "In stock",
                    "To buy", "Est. cost", "Bought"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["info"]))
    draw_text(img, (76, y + 18), "\u2699  Zero manual entry",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Event menus pull ingredient quantities; "
              "stock on hand is subtracted; the gap lands here.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Inventory", "Expenses")


# ---------------------------------------------------------------------------
def screen_expenses(m):
    img, y = start("\U0001F4B8  Expenses",
                   "Every cost, tagged to an event — so profit stays honest")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{money(a['expenses'])} spent", "bad"),
        ("11 categories", "espresso"),
        ("Receipt logged column", "ok"),
    ])
    rows = []
    for e in m.expenses[:8]:
        rows.append([
            {"t": e["date"].strftime("%d %b")},
            {"t": e["vendor"], "bold": True},
            {"t": e["category"], "color": "copper"},
            {"t": e["desc"][:44]},
            {"t": money(e["amount"]), "align": "r", "bold": True},
            {"t": e["method"]},
            {"t": "\u2713", "align": "c", "tick": True},
        ])
    y = draw_table(img, 44, y, [90, 190, 150, 380, 120, 180, 122],
                   ["Date", "Vendor", "Category", "Description", "Amount",
                    "Method", "Receipt"], rows, row_h=46)
    y += 20
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 320], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    cats = sorted(m.agg["exp_cats"].items(), key=lambda kv: -kv[1])[:6]
    hbar_chart(img, (84, y + 62, SW - 84, y + 306),
               "Spending by category", cats, color=LATTE)
    y += 350
    return finish(img, y, "Shopping List", "Income")


def screen_income(m):
    img, y = start("\U0001F4B0  Income & Payments",
                   "Deposits, balances and late payers at a glance")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{money(a['revenue'])} collected", "ok"),
        (f"\u23F0 {money(a['outstanding'])} outstanding", "warn"),
        (f"\U0001F534 {a['overdue']} overdue", "bad"),
    ])
    rows = []
    for i in m.income[:8]:
        bg, fg = PAY_STATUS_COLORS[i["status"]]
        rows.append([
            {"t": i["invoice"], "mono": True},
            {"t": i["client"], "bold": True},
            {"t": i["event_date"].strftime("%d %b")},
            {"t": money(i["amount"]), "align": "r"},
            {"t": money(i["received"]), "align": "r", "color": "ok"},
            {"t": money(i["balance"]) if i["balance"] else "—",
             "align": "r", "color": "bad" if i["balance"] else "muted",
             "bold": bool(i["balance"])},
            {"t": i["due"].strftime("%d %b"),
             "color": "bad" if i["overdue"] else "ink",
             "bold": i["overdue"]},
            {"t": i["status"], "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [130, 230, 90, 130, 130, 120, 100, 160],
                   ["Invoice", "Client", "Event", "Amount", "Received",
                    "Balance", "Due", "Status"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["warn"]))
    draw_text(img, (76, y + 18), "\U0001F551  Paid partial? No problem",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Log each payment as it arrives — the "
              "balance, aging and overdue flags look after themselves.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Expenses", "Staff")


# ---------------------------------------------------------------------------
def screen_staff(m):
    img, y = start("\U0001F9D1  Staff & Shifts",
                   "Crew schedules, hours and payroll in one place")
    a = m.agg
    y = draw_pills(img, y, [
        (f"{len(m.staff)} shifts scheduled", "espresso"),
        (f"{a['staff_unpaid']} awaiting pay", "warn"),
        ("Overtime tracked at 1.5×", "copper"),
    ])
    rows = []
    for s in m.staff[:9]:
        rows.append([
            {"t": s["name"], "bold": True},
            {"t": s["role"], "color": "copper"},
            {"t": s["event"].replace("EV-2026-", "EV-"), "mono": True},
            {"t": f"{s['hours']:g}", "align": "r"},
            {"t": f"${s['rate']}/h", "align": "r"},
            {"t": f"{s['ot']:g}", "align": "r",
             "color": "warn" if s["ot"] else "muted"},
            {"t": money(s["total"]), "align": "r", "bold": True},
            {"t": "\u2713", "align": "c",
             "tick": s["paid"] == "\u2713"},
        ])
    y = draw_table(img, 44, y, [230, 150, 100, 90, 100, 90, 120, 120],
                   ["Name", "Role", "Event", "Hrs", "Rate", "OT",
                    "Total", "Paid"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["plum"]))
    draw_text(img, (76, y + 18), "\U0001F4B3  Payroll math included",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Hours × rate + overtime × 1.5 = shift "
              "cost. Totals flow into each event and the P&L.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Income & Payments", "Equipment")


def screen_equipment(m):
    img, y = start("\U0001F527  Equipment",
                   "Chafers, tables, linens — what's free, what's out, "
                   "what needs service")
    a = m.agg
    y = draw_pills(img, y, [
        (f"Kit value {money(a['equip_value'])}", "espresso"),
        (f"\U0001F527 {a['equip_service']} due for service", "warn"),
        ("Availability auto-checked", "ok"),
    ])
    rows = []
    equip_colors = {"\U0001F527 Service": ("warn", "warn"),
                    "\U0001F7E1 Soon": ("brass", "brass"),
                    "\U0001F7E2 Ready": ("ok", "ok")}
    for e in m.equipment[:9]:
        st = e["status"]
        bg, fg = equip_colors.get(st, ("info", "info"))
        rows.append([
            {"t": e["item"], "bold": True},
            {"t": e["category"], "color": "copper"},
            {"t": str(e["owned"]), "align": "r"},
            {"t": str(e["reserved"]), "align": "r", "color": "warn" if
             e["reserved"] else "muted"},
            {"t": str(e["damaged"]), "align": "r", "color": "bad" if
             e["damaged"] else "muted"},
            {"t": str(e["available"]), "align": "r", "bold": True,
             "color": "ok" if e["available"] else "bad"},
            {"t": money(e["value"]), "align": "r"},
            {"t": st, "pill": (bg, fg), "align": "c"},
        ])
    y = draw_table(img, 44, y, [300, 120, 90, 110, 100, 110, 120, 146],
                   ["Item", "Category", "Owned", "Reserved", "Damaged",
                    "Free", "Value", "Status"], rows, row_h=46)
    y += 24
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 108], 12, fill=hexrgb(SOFT["latte"]))
    draw_text(img, (76, y + 18), "\U0001F4C6  Double-booked? It shows",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 60), "Reserved counts come from confirmed "
              "events, so the 'Free' column always tells the truth.",
              F("sans_md", 20), INK)
    y += 136
    return finish(img, y, "Staff & Shifts", "Calendar")


# ---------------------------------------------------------------------------
def screen_calendar(m):
    img, y = start("\U0001F4C6  Event Calendar",
                   "September 2026 — bookings and payment deadlines "
                   "together")
    a = m.agg
    d = ImageDraw.Draw(img)
    # month grid ---------------------------------------------------------
    y += 10
    rrect(d, [44, y, 860, y + 620], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (44 + 408, y + 18), "September 2026",
              F("display_b", 40), ESPRESSO, anchor="ma")
    cal = _month_grid(2026, 9)
    ev_by_day = {}
    for dt, name, status in a["upcoming"]:
        ev_by_day.setdefault(dt.day, []).append(("ev", status))
    for dt, who, amt in a["dues"]:
        ev_by_day.setdefault(dt.day, []).append(("due", None))
    gx, gy = 74, y + 92
    cw, chh = 112, 80
    for i, wd in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
                            "Sun")):
        draw_text(img, (gx + i * cw + cw / 2, gy - 34), wd,
                  F("sans_sb", 17), MUTED, anchor="ma")
    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            x, yy = gx + c * cw, gy + r * chh
            if day:
                in_ev = day in ev_by_day
                dd = ImageDraw.Draw(img)
                if in_ev:
                    rrect(dd, [x - 4, yy - 6, x + cw - 8, yy + chh - 14],
                          8, fill=hexrgb(SOFT["copper"]))
                draw_text(img, (x + 4, yy), str(day),
                          F("sans_sb", 20 if not in_ev else 21),
                          ESPRESSO if in_ev else MUTED)
                marks = ev_by_day.get(day, [])
                mx = x + 8
                for kind, status in marks[:2]:
                    col = COPPER if kind == "ev" else BAD
                    dd.ellipse([mx, yy + 32, mx + 14, yy + 46],
                               fill=hexrgb(col))
                    if kind == "due":
                        draw_text(img, (mx + 20, yy + 30), "\u25B2",
                                  F("sans_sb", 17), BAD)
                    mx += 44
    # side panel ---------------------------------------------------------
    px = 884
    rrect(d, [px, y, SW - 44, y + 620], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (px + 28, y + 18), "This month",
              F("serif_b", 26), ESPRESSO)
    yy = y + 74
    rows = [("\U0001F3AD Events", "3"), ("\u23F0 Payments due", "2"),
            ("\U0001F4B0 Due value", "$2,340"),
            ("\u2705 Confirmed", "2")]
    for lbl, val in rows:
        draw_text(img, (px + 28, yy), lbl, F("sans_md", 20), MUTED)
        draw_text(img, (SW - 68, yy - 1), val, F("sans_sb", 20), ESPRESSO,
                  anchor="ra")
        yy += 46
    yy += 10
    for txt, col in (("\u25CF  Event day", COPPER),
                     ("\u25B2  Payment due", BAD)):
        draw_text(img, (px + 28, yy), txt, F("sans_sb", 19), col)
        yy += 38
    yy += 12
    draw_text(img, (px + 28, yy), "19 Sep", F("sans_b", 20), ESPRESSO)
    draw_text(img, (px + 28, yy + 30), "\u25CF Fernandes birthday",
              F("sans_md", 18), INK)
    draw_text(img, (px + 28, yy + 58), "\u25B2 INV-1003 due",
              F("sans_md", 18), BAD)
    y += 648
    return finish(img, y, "Equipment", "Reports")


def _month_grid(year, month):
    import calendar
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year,
                                                                month)
    return weeks


# ---------------------------------------------------------------------------
def screen_reports(m):
    img, y = start("\U0001F4CA  Reports & P&L",
                   "Board-ready numbers without touching a formula")
    d = ImageDraw.Draw(img)
    a = m.agg
    # P&L card -----------------------------------------------------------
    rrect(d, [44, y, 640, y + 430], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [44, y, 640, y + 54], 12, fill=hexrgb(ESPRESSO))
    d.rectangle([44, y + 27, 640, y + 54], fill=hexrgb(ESPRESSO))
    draw_text(img, (68, y + 11), "\U0001F4BC  P&L — season to date",
              F("serif_b", 25), WHITE)
    pl = [("Revenue (cash in)", 59600, "ok"),
          ("Food cost", -4975, "bad"),
          ("Gross profit", 54625, "espresso"),
          ("Operating expenses", -5303, "bad"),
          ("Net profit", 49322, "espresso")]
    yy = y + 78
    for lbl, val, col in pl:
        draw_text(img, (76, yy), lbl, F("sans_md", 21), INK)
        draw_text(img, (612, yy - 1),
                  ("" if val < 0 else "") + money(abs(val)),
                  F("sans_sb", 22), COLORS[col], anchor="ra")
        yy += 46
    blocks_bar(img, (76, yy + 8, 612, yy + 30), 0.83, n=40, fg=ESPRESSO)
    draw_text(img, (76, yy + 42), "83% of revenue kept as net profit",
              F("sans_md", 19), MUTED)
    # tax card -----------------------------------------------------------
    rrect(d, [656, y, SW - 44, y + 430], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    rrect(d, [656, y, SW - 44, y + 54], 12, fill=hexrgb(COPPER))
    d.rectangle([656, y + 27, SW - 44, y + 54], fill=hexrgb(COPPER))
    draw_text(img, (680, y + 11), "\U0001F9FD  Sales tax helper",
              F("serif_b", 25), WHITE)
    tax = [("Taxable revenue", money(59600)),
           ("Sales tax rate", "5%"),
           ("Tax collected", money(a["tax_collected"])),
           ("Tax already paid", money(1010)),
           ("Tax still due", money(a["tax_due"]))]
    yy = y + 78
    for lbl, val in tax:
        draw_text(img, (688, yy), lbl, F("sans_md", 21), INK)
        draw_text(img, (SW - 68, yy - 1), val, F("sans_sb", 22), ESPRESSO,
                  anchor="ra")
        yy += 56
    y += 454
    # charts -------------------------------------------------------------
    rrect(d, [44, y, SW - 44, y + 330], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    months = [t for t in a["months"] if t[1] or t[2]][-6:]
    grouped_columns(img, (110, y + 66, SW - 110, y + 310),
                    "Monthly revenue, expenses & net profit",
                    [t[0] for t in months],
                    [("Revenue", [max(t[1], 0) for t in months], COPPER),
                     ("Net", [max(t[3], 0) for t in months], OK)],
                    fmt="${:,.0f}")
    y += 354
    rrect(d, [44, y, SW - 44, y + 96], 12, fill=hexrgb(SOFT["brass"]))
    draw_text(img, (76, y + 14), "\U0001F4C4  One-click summaries",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 56), "P&L, tax helper, monthly trends and "
              "best-performer tables all update from your entries.",
              F("sans_md", 20), INK)
    y += 124
    return finish(img, y, "Calendar", "Checklists")


def screen_checklists(m):
    img, y = start("\u2705  Checklists",
                   "Prep, shop, event day and wrap-up — nothing forgotten")
    d = ImageDraw.Draw(img)
    import catering_tracker.demo as demo
    cols = [("\U0001F373 Prep week", m.checks["prep"],
             ["Lock menu & portions", "Confirm guest count",
              "Book staff & brief roles", "Reserve equipment",
              "Order protein & dairy", "Dry-store shopping run",
              "Print run-sheets & labels", "Prep desserts"]),
            ("\U0001F6D2 Shopping", m.checks["shop"],
             ["Butcher order confirmed", "Produce market pickup",
              "Dry goods delivered", "Beverages chilled",
              "Packing & disposables", "Cash float for market",
              "Taste-test sauces", "Photograph plating"]),
            ("\U0001F552 Event day", m.checks["day"],
             ["Load van by 7:00", "Venue walk-through",
              "Kitchen handover", "Hot line starts 11:30",
              "Service briefing", "Buffet replenish ×3",
              "Dessert station setup", "Client walkthrough"]),
            ("\U0001F3C1 Wrap-up", m.checks["end"],
             ["Strike & pack by 22:00", "Van unload & count",
              "Equipment damage check", "Wash & store linens",
              "Staff paid & tipped out", "Leftovers donated",
              "Invoice balance sent", "Client thank-you note"])]
    cw = (SW - 88 - 3 * 18) // 4
    y += 4
    for i, (title, done, items) in enumerate(cols):
        x = 44 + i * (cw + 18)
        rrect(d, [x, y, x + cw, y + 560], 12, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, y, x + cw, y + 50], 12, fill=hexrgb(
            OK if len(done) == len(items) else LATTE))
        d.rectangle([x, y + 25, x + cw, y + 50], fill=hexrgb(
            OK if len(done) == len(items) else LATTE))
        draw_text(img, (x + cw / 2, y + 10), title, F("sans_sb", 19),
                  WHITE, anchor="ma")
        yy = y + 74
        for j, item in enumerate(items):
            if j in done:
                draw_text(img, (x + 18, yy), "\u2713", F("sans_b", 20), OK)
                draw_text(img, (x + 48, yy + 1), item, F("sans_md", 17),
                          MUTED)
            else:
                rrect(d, [x + 18, yy + 1, x + 36, yy + 19], 4,
                      outline=hexrgb(LATTE), width=2)
                draw_text(img, (x + 48, yy + 1), item, F("sans_md", 17),
                          INK)
            yy += 40
        yy += 8
        blocks_bar(img, (x + 18, yy, x + cw - 18, yy + 18),
                   len(done) / float(len(items)), n=24,
                   fg=OK if len(done) == len(items) else LATTE, gap=2)
        draw_text(img, (x + cw - 18, yy + 26), f"{len(done)}/{len(items)}",
                  F("sans_sb", 16), MUTED, anchor="ra")
    y += 600
    return finish(img, y, "Reports & P&L", "Invoice")


# ---------------------------------------------------------------------------
def screen_invoice(m):
    inv = next((i for i in m.income if i["status"] == "\U0001F7E0 Partial"),
               m.income[0])
    img, y = start("\U0001F9FE  Invoice Generator",
                   "Branded, itemised invoices — filled in for you")
    d = ImageDraw.Draw(img)
    y += 6
    rrect(d, [44, y, SW - 44, y + 560], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    # letterhead
    draw_text(img, (84, y + 34), "Saffron & Sage Catering Co.",
              F("display_b", 40), ESPRESSO)
    draw_text(img, (84, y + 88), "catering@saffronsage.example  ·  "
              "0300-8899112", F("sans_md", 18), MUTED)
    draw_text(img, (SW - 84, y + 34), inv["invoice"], F("display_b", 40),
              COPPER, anchor="ra")
    draw_text(img, (SW - 84, y + 90), "31 October 2026", F("sans_md", 18),
              MUTED, anchor="ra")
    # meta
    yy = y + 150
    draw_text(img, (84, yy), "BILL TO", F("sans_sb", 16), LATTE)
    draw_text(img, (84, yy + 30), inv["client"], F("serif_b", 28), INK)
    draw_text(img, (84, yy + 70), "Marquee, Ferozepur Road · 90 guests",
              F("sans_md", 19), MUTED)
    draw_text(img, (SW - 84, yy + 30), "Due 31 October 2026",
              F("sans_sb", 20), WARN, anchor="ra")
    # lines
    yy += 130
    lines = [("Cocktail package — 90 guests", "1", 3100),
             ("Service staff × 6 (incl. setup)", "1", 420),
             ("Beverage station refill", "1", 180),
             ("Transport & equipment", "1", 160)]
    yx = 84
    draw_text(img, (yx, yy), "Description", F("sans_sb", 17), LATTE)
    draw_text(img, (SW - 500, yy), "Qty", F("sans_sb", 17), LATTE,
              anchor="ra")
    draw_text(img, (SW - 84, yy), "Amount", F("sans_sb", 17), LATTE,
              anchor="ra")
    yy += 36
    for desc, qty, amt in lines:
        d.line([84, yy - 6, SW - 84, yy - 6], fill=hexrgb(BORDER), width=1)
        draw_text(img, (yx, yy), desc, F("sans_md", 20), INK)
        draw_text(img, (SW - 500, yy), qty, F("sans_md", 20), INK,
                  anchor="ra")
        draw_text(img, (SW - 84, yy), money(amt), F("sans_md", 20), INK,
                  anchor="ra")
        yy += 44
    d.line([84, yy - 4, SW - 84, yy - 4], fill=hexrgb(ESPRESSO), width=2)
    # totals
    total = sum(a for _, _, a in lines)
    dep = int(total * 0.4)
    for lbl, val, col, big in (("Subtotal", money(total), INK, False),
                               ("Deposit received", "− " + money(dep),
                                OK, False),
                               ("Balance due", money(total - dep), COPPER,
                                True)):
        if big:
            yy += 12
            f = F("serif_b", 30)
        else:
            f = F("sans_md", 21)
        draw_text(img, (SW - 400, yy), lbl, f, col)
        draw_text(img, (SW - 84, yy), val, f, col, anchor="ra")
        yy += 44 if not big else 52
    # footer strip
    d.rectangle([44, y + 470, SW - 44, y + 560], fill=hexrgb(SOFT["latte"]))
    draw_text(img, (84, y + 494), "\U0001F4B3  Payable by bank transfer — "
              "details on Setup", F("sans_md", 20), INK)
    draw_text(img, (84, y + 524), "Thank you for booking with us!",
              F("hand", 34), COPPER)
    y += 590
    rrect(d, [44, y, SW - 44, y + 96], 12, fill=hexrgb(SOFT["copper"]))
    draw_text(img, (76, y + 14), "\u2699  Pulls from your event data",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 54), "Client, package and deposit arrive "
              "pre-filled; print or export as PDF.", F("sans_md", 20), INK)
    y += 124
    return finish(img, y, "Checklists", "Setup")


# ---------------------------------------------------------------------------
def screen_setup(m):
    img, y = start("\u2699  Setup", "Make the tracker yours — once")
    d = ImageDraw.Draw(img)
    s = m.settings
    y = draw_pills(img, y, [
        ("Your business name & logo colours", "espresso"),
        ("Currency, tax & margins", "copper"),
        ("Drop-down lists you can edit", "info"),
    ])
    panels = [
        ("\U0001F3EA  Business details", ESPRESSO,
         [("Business name", s["business"]),
          ("Currency", s["currency"] + "  (dollar)"),
          ("Season year", str(s["year"])),
          ("Dashboard message", s["message"])]),
        ("\U0001F4B0  Money rules", COPPER,
         [("Sales tax rate", f"{s['tax']:.0%}"),
          ("Target profit margin", f"{s['margin']:.0%}"),
          ("Deposit to book", f"{s['deposit']:.0%}"),
          ("'Due soon' window", f"{s['duesoon']} days")]),
    ]
    for title, col, rows in panels:
        rrect(d, [44, y, SW - 44, y + 320], 12, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [44, y, SW - 44, y + 54], 12, fill=hexrgb(col))
        d.rectangle([44, y + 27, SW - 44, y + 54], fill=hexrgb(col))
        draw_text(img, (68, y + 11), title, F("serif_b", 25), WHITE)
        yy = y + 82
        for lbl, val in rows:
            draw_text(img, (76, yy), lbl, F("sans_md", 21), MUTED)
            draw_text(img, (SW - 76, yy - 1), val, F("sans_sb", 21),
                      ESPRESSO, anchor="ra")
            yy += 58
        y += 348
    rrect(d, [44, y, SW - 44, y + 150], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    draw_text(img, (76, y + 18), "\U0001F5C2  Editable lists",
              F("serif_b", 24), ESPRESSO)
    draw_text(img, (76, y + 62), "Event types, package tiers, expense "
              "categories, roles and stock categories are plain lists —",
              F("sans_md", 20), INK)
    draw_text(img, (76, y + 92), "edit them and every drop-down updates "
              "across all 20 tabs.", F("sans_md", 20), INK)
    y += 180
    return finish(img, y, "Invoice Generator", "Dashboard")


# ---------------------------------------------------------------------------
def tabs_bar(m, edition="premium"):
    """A wide strip of every tab — for the 'what's inside' image."""
    tabs = [C.SHEET_NAMES[k] for k in C.EDITIONS[edition] if k != "data"]
    img = Image.new("RGBA", (SW, 400), hexrgb(CANVAS))
    d = ImageDraw.Draw(img)
    x, y = 20, 20
    for label in tabs:
        f = F("sans_sb", 17)
        w = text_width(label, f) + 30
        if x + w > SW - 20:
            x = 20
            y += 56
        rrect(d, [x, y, x + w, y + 42], 8, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(img, (x + 14, y + 9), label, f, ESPRESSO)
        x += w + 10
    return img.crop((0, 0, SW, y + 66))
