"""
screens.py - render pixel "screenshots" of the workbook's tabs, populated
with the REAL demo data, for use in the Etsy listing images.
"""

from datetime import date, timedelta

from PIL import Image, ImageDraw

from etsy import screenlib as S
from etsy.screenlib import (F, ALT, BAD, BORDER, BURGUNDY, CANVAS, CARD,
                            CREAM, GOLD, INK, INFO, MUTED, OK, PINE, PINE2,
                            PLUM, SOFT, WARN, WHITE, blocks_bar, chip,
                            COLORS, draw_table, draw_text, fit_size, hexrgb,
                            kpi_card, pill_row, rrect, section_bar,
                            sheet_header, text_width, wrap)

SW = 1320                                   # screen width
STATUS_COLORS = S.STATUS_COLORS

TODAY = date(2026, 9, 12)                   # demo "today" — matches 104 days


def _fmt_d(d):
    return d.strftime("%d %b")


def _days(d):
    return (d - TODAY).days


def _money(v, cur="$"):
    return f"{cur}{v:,.0f}" if abs(v - round(v)) < 0.005 else f"{cur}{v:,.2f}"


def _status_pill(status):
    return STATUS_COLORS.get(status, ("muted", "ink"))


def _footer(img, h):
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - 54, SW, h], fill=hexrgb(PINE))
    draw_text(img, (44, h - 39), "🎄 Christmas Gift Tracker", F("sans_md", 17),
              CREAM)
    draw_text(img, (SW / 2.0, h - 39), "© Novality Store", F("sans_b", 17),
              CREAM, anchor="ma")
    draw_text(img, (SW - 44, h - 39), "Excel & Google Sheets",
              F("sans_md", 17), CREAM, anchor="ra")


def _nav(img, y):
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 118], 12, fill=hexrgb(CARD),
          outline=hexrgb(BORDER))
    tabs = [("🏠", "Dashboard", PINE), ("🎁", "Gifts", PINE2),
            ("💰", "Budget", GOLD), ("💡", "Wish List", PLUM),
            ("🛍️", "Shopping", INFO), ("📦", "Orders", PINE2),
            ("🎀", "Wrapping", BURGUNDY), ("💌", "Cards", WARN),
            ("🧦", "Stockings", "#8C5A2B"), ("✅", "To-Do", OK),
            ("⚙️", "Setup", MUTED), ("📖", "Guide", BURGUNDY)]
    for i, (em, name, color) in enumerate(tabs):
        row, col = divmod(i, 6)
        x = 68 + col * 206
        yy = y + 10 + row * 54
        f = F("sans_sb", 15)
        label = f"{em} {name}"
        w = text_width(label, f)
        rrect(d, [x, yy, x + w + 24, yy + 38], 19,
              fill=hexrgb(SOFT[_soft_key(color)]))
        draw_text(img, (x + 12, yy + 7), label, f, color)
    return y + 118


def _soft_key(hexcolor):
    for k, v in COLORS.items():
        if v.lower() == hexcolor.lower():
            return k if k in SOFT else "muted"
    return "muted"


# ---------------------------------------------------------------------------
def screen_gifts(m, bk):
    n_planned = m.agg["gifts_planned"]
    pills = [(f"🎯 {n_planned} gifts planned", "pine"),
             (f"✅ {m.agg['gifts_purchased']} bought", "ok"),
             (f"🎀 {m.agg['gifts_wrapped']} wrapped", "gold"),
             (f"📦 {m.agg['gifts_delivered']} handed over", "burgundy"),
             (f"🛒 {m.agg['gifts_to_buy']} still to buy", "warn"),
             (f"📈 {m.agg['gift_completion']:.0%} complete", "pine2")]
    H = 104 + 56 + 48 + 13 * 44 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "🎁  Gift Tracker",
                     "Every present in one place — type in the white cells, "
                     "the tinted cells do the maths.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [128, 236, 128, 92, 92, 158, 74, 96, 224]
    headers = ["For", "Gift idea", "Category", "Budget", "Cost", "Status",
               "🎀 Wrap", "Buy by", "Deadline alert"]
    rows = []
    shown = [g for g in m.gifts
             if g["status"] in ("💡 Idea", "🛒 Need to Buy", "🛍️ Ordered",
                                "✅ Purchased", "🎀 Wrapped")][:12]
    for g in shown:
        dl = g["deadline"]
        days = _days(dl)
        if g["status"] in ("💡 Idea", "🛒 Need to Buy"):
            alert = ({"t": "⚠️ overdue", "pill": ("bad", "bad")} if days < 0
                     else {"t": "due soon", "pill": ("warn", "warn")}
                     if days <= 7 else {"t": "on track", "pill": ("ok", "ok")})
        else:
            alert = {"t": "—", "color": "muted"}
        rows.append([
            g["recipient"], g["idea"], g["category"],
            {"t": _money(g["budget"]), "align": "r"},
            {"t": _money(g["cost"]) if g["cost"] else "—", "align": "r",
             "color": "muted" if not g["cost"] else "ink"},
            {"t": g["status"], "pill": _status_pill(g["status"])},
            {"tick": g["wrapped"] == "✓"},
            {"t": _fmt_d(dl), "align": "c"},
            alert])
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=PINE2)
    tot_b = sum(g["budget"] or 0 for g in m.gifts)
    tot_c = sum(g["cost"] or 0 for g in m.gifts)
    draw_table(img, 44, y + 10, widths,
               ["TOTALS", f"{len(m.gifts)} gifts", "", "", "", "", "", "", ""],
               [[{"t": "TOTALS", "bold": True},
                 {"t": f"{len(m.gifts)} gifts planned", "bold": True},
                 "", {"t": _money(tot_b), "align": "r", "bold": True},
                 {"t": _money(tot_c), "align": "r", "bold": True},
                 {"t": f"{m.agg['gift_completion']:.0%} done", "bold": True,
                  "align": "c"}, "", "",
                 {"t": f"avg {_money(m.agg['avg_per_recipient'])}/person",
                  "bold": True}]], row_h=46, hdr_bg=PINE)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_budget(m, bk):
    a = m.agg
    pills = [(f"💰 Budget {_money(a['budget_planned'])}", "pine"),
             (f"💸 Spent {_money(a['budget_actual'])}", "burgundy"),
             (f"🪙 Left {_money(a['budget_remaining'])}", "ok"),
             (f"📊 {a['budget_pct']:.0%} used", "gold"),
             ("🚨 Alert at 85%", "warn")]
    H = 104 + 56 + 122 + 78 + 48 + 11 * 46 + 26 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "💰  Christmas Budget",
                     "Plan it, watch it, and get told the moment you are "
                     "about to overspend.")
    y = pill_row(img, y + 8, pills) + 16
    # overview cards
    cw = (SW - 88 - 3 * 18) / 4.0
    kx = 44
    kpi_card(img, kx, y, cw, "TOTAL BUDGET", _money(a["budget_planned"]),
             "pine", value_size=36)
    kpi_card(img, kx + (cw + 18), y, cw, "ACTUAL SPEND",
             _money(a["budget_actual"]), "burgundy", value_size=36)
    kpi_card(img, kx + 2 * (cw + 18), y, cw, "REMAINING",
             _money(a["budget_remaining"]), "ok", value_size=36)
    kpi_card(img, kx + 3 * (cw + 18), y, cw, "BUDGET USED",
             f"{a['budget_pct']:.1%}", "gold", value_size=36)
    y += 122
    # alert banner
    d = ImageDraw.Draw(img)
    rrect(d, [44, y, SW - 44, y + 58], 10, fill=hexrgb(SOFT["warn"]),
          outline=hexrgb(WARN))
    draw_text(img, (66, y + 14), a["budget_alert"], F("sans_sb", 20), WARN)
    y += 78
    widths = [268, 104, 116, 96, 108, 116, 74, 152, 200]
    headers = ["Category", "Planned", "Auto spend", "Extras", "Actual",
               "Remaining", "%", "Status", "Progress"]
    rows = []
    for br in a["budget_rows"]:
        pct = br["pct"] if isinstance(br.get("pct"), (int, float)) else 0.0
        rem = br["remaining"] if isinstance(br.get("remaining"),
                                            (int, float)) else 0.0
        if rem < 0:
            st = ("bad", "bad", "over budget")
        elif pct >= 0.85:
            st = ("warn", "warn", "almost gone")
        else:
            st = ("ok", "ok", "on track")
        rows.append([
            br["label"],
            {"t": _money(br["planned"]), "align": "r"},
            {"t": _money(br["auto"]), "align": "r", "color": "muted"},
            {"t": _money(br["manual"]) if br["manual"] else "—", "align": "r",
             "color": "muted"},
            {"t": _money(br["actual"]), "align": "r", "bold": True},
            {"t": _money(rem), "align": "r",
             "color": "bad" if rem < 0 else "ink"},
            {"t": f"{pct:.0%}", "align": "r"},
            {"t": st[2], "pill": (st[0], st[1])},
            {"bar": pct}])
    # totals row + bars need a custom pass; draw bars after table
    y = draw_table(img, 44, y, widths, headers,
                   [[r[i] if not isinstance(r[i], dict) or "bar" not in r[i]
                     else "" for i in range(9)] for r in rows],
                   row_h=46, hdr_bg=GOLD)
    # overlay progress bars in last column
    by = y - 11 * 46
    for i, r in enumerate(rows):
        pct = m.agg["budget_rows"][i]["pct"]
        pct = pct if isinstance(pct, (int, float)) else 0.0
        ry = by + i * 46 + 8
        blocks_bar(img, [44 + sum(widths[:-1]) + 10, ry,
                         44 + sum(widths) - 10, ry + 29],
                   min(pct, 1.0), n=14,
                   fg=BAD if pct > 1 else (WARN if pct >= 0.85 else PINE2),
                   gap=3)
    draw_table(img, 44, y + 10, widths,
               ["", "", "", "", "", "", "", "", ""],
               [[{"t": "TOTALS", "bold": True},
                 {"t": _money(a["budget_planned"]), "align": "r",
                  "bold": True}, "",
                 {"t": _money(sum(m.budget_manual.values())),
                  "align": "r"},
                 {"t": _money(a["budget_actual"]), "align": "r",
                  "bold": True},
                 {"t": _money(a["budget_remaining"]), "align": "r",
                  "bold": True},
                 {"t": f"{a['budget_pct']:.0%}", "align": "r", "bold": True},
                 "", ""]], row_h=48, hdr_bg=GOLD)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_orders(m, bk):
    a = m.agg
    pills = [(f"📦 {a['orders_total']} orders", "pine"),
             (f"🚚 {a['orders_outstanding']} still out", "info"),
             (f"⏰ {a['orders_late']} late", "bad"),
             (f"💵 {a['orders_value']:,.2f} tracked".replace("$", "$"),
              "gold")]
    rows = []
    for o in m.orders[:9]:
        exp = o["expected"]
        days = _days(exp)
        st = o["status"]
        if st == "✅ Delivered":
            pill = ("ok", "ok")
        elif days < 0 and st != "✅ Delivered":
            pill = ("bad", "bad")
            st = "⚠️ Late"
        else:
            pill = ("info", "info")
        rows.append([
            o["recipient"], o["item"], o["store"], o["order_no"][:14] + "…",
            {"t": _fmt_d(exp), "align": "c"},
            {"t": ("arrived ✓" if st == "✅ Delivered" else
                   (f"{days} days" if days >= 0 else f"{-days} days late")),
             "align": "c",
             "color": "ok" if st == "✅ Delivered" else
                      ("bad" if days < 0 else "ink")},
            {"t": st, "pill": pill},
            {"t": _money(o["cost"]), "align": "r"}])
    H = 104 + 56 + 48 + (len(rows) + 1) * 44 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "📦  Online Order Tracker",
                     "Parcels, couriers and cut-off dates — nothing arrives "
                     "on the 27th on your watch.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [128, 216, 128, 208, 108, 118, 214, 112]
    headers = ["For", "Item", "Store", "Order number", "Expected",
               "Days left", "Status", "Cost"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=PINE2)
    draw_table(img, 44, y + 10, widths, [""] * 8,
               [[{"t": "TOTALS", "bold": True},
                 {"t": f"{a['orders_total']} orders", "bold": True}, "", "",
                 "",
                 {"t": f"{a['orders_outstanding']} outstanding", "bold": True,
                  "align": "c"},
                 {"t": f"{a['orders_late']} late", "bold": True, "align": "c"},
                 {"t": "avg 52 days before Christmas", "bold": True},
                 {"t": _money(a["orders_value"]), "align": "r",
                  "bold": True}]], row_h=46, hdr_bg=PINE2)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_wrapping(m, bk):
    a = m.agg
    pills = [(f"🎀 {a['gifts_wrapped']} wrapped", "burgundy"),
             (f"🎁 {a['wrap_to_do']} still to wrap", "warn"),
             (f"📦 {a['deliver_to_do']} to hand over", "info"),
             ("🙈 Secret Mode off", "muted")]
    rows = []
    wrap_rows = [g for g in m.gifts if g["wrapped"] == "✓"][:10]
    for g in wrap_rows:
        rows.append([
            g["recipient"], g["idea"],
            {"t": "wrapped ✓", "pill": ("burgundy", "burgundy")},
            g["hiding"] or "—",
            g["tag"] or "—",
            {"tick": g["delivered"] == "✓"} if g["delivered"] else
            {"t": "waiting", "color": "muted", "align": "c"}])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "🎀  Wrapping & Hiding",
                     "Mirrors your gift list automatically — add the hiding "
                     "spot and the gift tag here.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [150, 260, 168, 300, 190, 164]
    headers = ["For", "Gift", "Wrapped", "Hiding spot", "🏷 Tag",
               "Handed over"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=BURGUNDY)
    draw_table(img, 44, y + 10, widths, [""] * 6,
               [[{"t": "SUMMARY", "bold": True},
                 {"t": f"{a['gifts_wrapped']} wrapped", "bold": True},
                 {"t": f"{a['wrap_to_do']} to go", "bold": True, "align": "c"},
                 {"t": "5 hiding spots in use", "bold": True},
                 {"t": "6 tags ready", "bold": True},
                 {"t": f"{a['deliver_to_do']} parcels under the tree",
                  "bold": True}]], row_h=48, hdr_bg=BURGUNDY)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_cards(m, bk):
    a = m.agg
    pills = [(f"💌 {a['cards_total']} cards", "pine"),
             (f"✍️ {a['cards_written']} written", "info"),
             (f"📮 {a['cards_sent']} posted", "ok"),
             (f"💸 {_money(a['cards_postage'])} postage", "gold")]
    rows = []
    for c in m.cards[:10]:
        rows.append([
            c["name"], c["relationship"], c["address"],
            {"tick": c["bought"] == "✓"},
            {"tick": c["written"] == "✓"},
            {"tick": c["sent"] == "✓"},
            {"t": f"{c['postage']:.2f}", "align": "r", "mono": True},
            {"t": "✅ all done" if c["sent"] == "✓" else "in progress",
             "pill": ("ok", "ok") if c["sent"] == "✓" else
             ("warn", "warn")}])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "💌  Christmas Card Tracker",
                     "Bought → written → posted → replied. Nobody gets "
                     "forgotten, and postage lands in your budget.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [150, 140, 350, 92, 92, 92, 96, 220]
    headers = ["Name", "Relation", "Address", "Bought", "Written", "Posted",
               "Stamp", "Status"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=WARN)
    draw_table(img, 44, y + 10, widths, [""] * 8,
               [[{"t": "SUMMARY", "bold": True},
                 {"t": f"{a['cards_total']} people", "bold": True}, "",
                 {"t": f"{a['cards_total']} / {a['cards_total']}", "align": "c",
                  "bold": True},
                 {"t": f"{a['cards_written']}", "align": "c", "bold": True},
                 {"t": f"{a['cards_sent']}", "align": "c", "bold": True},
                 {"t": _money(a["cards_postage"]), "align": "r", "bold": True},
                 {"t": "auto-added to Budget tab", "bold": True}]],
               row_h=48, hdr_bg=WARN)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_stockings(m, bk):
    a = m.agg
    pills = [(f"🧦 {a['stock_items']} items", "pine"),
             (f"✅ {a['stock_bought']} bought", "ok"),
             (f"💸 {_money(a['stock_spent'])} spent", "burgundy"),
             (f"💰 {_money(a['stock_budget'])} budgeted", "gold")]
    rows = []
    for s in m.stockings[:10]:
        rows.append([
            s["owner"], s["item"], s["category"],
            {"t": _money(s["budget"]), "align": "r"},
            {"t": _money(s["cost"]) if s["cost"] else "—", "align": "r"},
            {"tick": s["bought"] == "✓"},
            s["hiding"] or "—"])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "🧦  Stocking Stuffer Tracker",
                     "The little things add up fastest — budget them per "
                     "stocking and stop the January regret.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [140, 260, 150, 110, 110, 110, 352]
    headers = ["Stocking", "Item", "Type", "Budget", "Cost", "Bought",
               "Hiding spot"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg="#8C5A2B")
    draw_table(img, 44, y + 10, widths, [""] * 7,
               [[{"t": "TOTALS", "bold": True},
                 {"t": f"{a['stock_items']} items", "bold": True}, "",
                 {"t": _money(a["stock_budget"]), "align": "r", "bold": True},
                 {"t": _money(a["stock_spent"]), "align": "r", "bold": True},
                 {"t": f"{a['stock_bought']} bought", "align": "c",
                  "bold": True},
                 {"t": "mirrors the Budget tab", "bold": True}]],
               row_h=48, hdr_bg="#8C5A2B")
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_todo(m, bk):
    a = m.agg
    pills = [(f"✅ {a['todo_done']} of {a['todo_total']} done", "ok"),
             ("⏰ 0 overdue", "pine"),
             ("📅 deadlines auto-set", "info"),
             ("♻️ re-usable every year", "gold")]
    rows = []
    for t in m.todos[:12]:
        done = t["done"] == "✓"
        days = _days(t["deadline"])
        rows.append([
            {"tick": done},
            t["task"], t["category"],
            {"t": _fmt_d(t["deadline"]), "align": "c"},
            {"t": "done ✓" if done else
             (f"{days} days" if days >= 0 else f"{-days} overdue"),
             "align": "c",
             "color": "ok" if done else ("bad" if days < 0 else "ink")},
            {"t": "✔ Done" if done else "on the list",
             "pill": ("ok", "ok") if done else ("muted", "muted")}])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "✅  Christmas To-Do List",
                     "Pre-loaded with the classic holiday checklist — every "
                     "deadline is calculated from your event date.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [80, 420, 130, 130, 150, 190]
    headers = ["Done", "Task", "Category", "Deadline", "Days left", "Status"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=OK)
    draw_table(img, 44, y + 10, widths, [""] * 6,
               [[{"t": "SUMMARY", "bold": True},
                 {"t": f"{a['todo_done']} of {a['todo_total']} complete",
                  "bold": True},
                 "",
                 {"t": "next: 20 Nov", "align": "c", "bold": True},
                 {"t": "auto", "align": "c", "bold": True, "color": "gold"},
                 {"t": "re-dates from EventDate", "bold": True}]],
               row_h=48, hdr_bg=OK)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_wishlist(m, bk):
    a = m.agg
    pills = [(f"💡 {a['wish_total']} ideas saved", "plum"),
             (f"⭐ {a['wish_must']} must-haves", "gold"),
             (f"💵 {_money(a['wish_value'])} value", "burgundy")]
    rows = []
    for w in m.wishlist[:9]:
        rows.append([
            w["person"], w["idea"], w["category"],
            {"t": w["priority"], "pill": ("gold", "gold")
             if "Must" in w["priority"] else ("muted", "muted")},
            {"t": _money(w["price"]) if w["price"] else "—", "align": "r"},
            {"t": "✓ copied to Gifts" if w["idea"] in
             [g["idea"] for g in m.gifts] else "— saved", "align": "c",
             "color": "ok" if w["idea"] in [g["idea"] for g in m.gifts]
             else "muted"}])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "💡  Wish List & Gift Ideas",
                     "Hints all year round, ranked by how much they really "
                     "want them.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [190, 270, 150, 210, 120, 200]
    headers = ["Person", "Idea", "Category", "Priority", "Price",
               "On the gift list?"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=PLUM)
    draw_table(img, 44, y + 10, widths, [""] * 6,
               [[{"t": "SUMMARY", "bold": True},
                 {"t": f"{a['wish_total']} ideas — {a['wish_must']} rated "
                       "must-have", "bold": True},
                 "",
                 {"t": "1–3 stars", "align": "c", "bold": True},
                 {"t": _money(a["wish_value"]), "align": "r", "bold": True},
                 {"t": "one click to Gifts", "bold": True}]],
               row_h=48, hdr_bg=PLUM)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_setup(m, bk):
    H = 104 + 56 + 560 + 40 + 260 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "⚙️  Setup — make it yours",
                     "Three minutes, no formulas to write: set your date, "
                     "budget and people — every tab updates instantly.")
    s = m.settings
    y = pill_row(img, y + 8,
                 [("🎉 event: Christmas 2026", "pine"),
                  ("💰 budget: $1,500", "burgundy"),
                  ("🚨 alert: 85%", "warn"),
                  ("🙈 Secret Mode: off", "muted")]) + 24

    def panel(x, y, w, h, title, color):
        d = ImageDraw.Draw(img)
        rrect(d, [x, y, x + w, y + h], 12, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        rrect(d, [x, y, x + w, y + 52], 12, fill=hexrgb(color))
        d.rectangle([x, y + 26, x + w, y + 52], fill=hexrgb(color))
        draw_text(img, (x + 24, y + 11), title, F("serif_b", 24), WHITE)
        return y + 52

    def setting(x, y, w, label, value, note="", vpill=None):
        d = ImageDraw.Draw(img)
        draw_text(img, (x + 24, y + 4), label, F("sans_md", 19), MUTED)
        if vpill:
            chip(img, (x + w - 330, y - 6), value, SOFT[vpill[0]],
                 vpill[1] if isinstance(vpill[1], str) and
                 not str(vpill[1]).startswith("#") else vpill[1],
                 size=20, bold=False)
        else:
            d.rounded_rectangle([x + w - 330, y - 4, x + w - 24, y + 38], 8,
                                fill=hexrgb("#FFFDF8"),
                                outline=hexrgb(BORDER))
            f, _ = fit_size(value, "sans_sb", 20, 290, 10)
            draw_text(img, (x + w - 318, y + 3), value, f, INK)
        if note:
            draw_text(img, (x + 24, y + 36), note, F("sans", 15), MUTED)

    lx, rx, pw = 44, 44 + 616 + 24, 616
    ly = panel(lx, y, pw, 300, "🎉 Your event", PINE)
    setting(lx, ly + 22, pw, "Event name", s["event_name"])
    setting(lx, ly + 78, pw, "Event date", "25 Dec 2026",
            note="every deadline in the workbook recalculates from this")
    setting(lx, ly + 150, pw, "Countdown message", "auto ⏳ 104 days to go")
    setting(lx, ly + 206, pw, "Occasion", "Christmas  ▾",
            note="18 occasions pre-loaded — birthdays, weddings, Diwali…")
    ry = panel(rx, y, pw, 300, "💰 Money & alerts", BURGUNDY)
    setting(rx, ry + 22, pw, "Currency", "US Dollar  $  ▾")
    setting(rx, ry + 78, pw, "Total budget", "$1,500",
            note="feeds the Budget tab & all the alerts")
    setting(rx, ry + 150, pw, "Alert me at", "85% of budget  ▾")
    setting(rx, ry + 206, pw, "Due-soon window", "7 days  ▾")
    y += 324
    ly = panel(lx, y, pw, 240, "🙈 Secret Mode", PLUM)
    draw_text(img, (lx + 24, ly + 18),
              "Hide gift ideas & costs from anyone peeking over your "
              "shoulder.", F("sans_md", 17), INK)
    chip(img, (lx + 24, ly + 70), "🙈  Off — everyone can see everything",
         SOFT["muted"], MUTED, size=17)
    chip(img, (lx + 24, ly + 128), "🔒  On — ideas & costs hidden, 1-click "
         "toggle", SOFT["plum"], PLUM, size=17)
    ry = panel(rx, y, pw, 240, "👥 Your people", PINE2)
    names = [r for r in m.recipients if r][:8]
    xx, yy = rx + 24, ry + 18
    for nm in names:
        w = chip(img, (xx, yy), f"🎅 {nm}", SOFT["pine2"], PINE2, size=17)
        xx += w + 10
        if xx > rx + pw - 160:
            xx, yy = rx + 24, yy + 46
    draw_text(img, (rx + 24, yy + 60),
              "16 recipient slots • 16 stockings • 100+ gift rows",
              F("sans", 16), MUTED)
    _footer(img, H)
    return img


# ---------------------------------------------------------------------------
def screen_dashboard(m, bk, anchors=None):
    """The big one. Returns (img, anchors dict of y positions for crops)."""
    a = m.agg
    A = {}
    d_img = Image.new("RGBA", (SW, 3700), hexrgb(CANVAS))
    d = ImageDraw.Draw(d_img)
    # hero band
    d.rectangle([0, 0, SW, 108], fill=hexrgb(PINE))
    draw_text(d_img, (44, 24), "🎄 Christmas 2026 — Gift Command Center",
              F("serif_b", 44), CREAM)
    draw_text(d_img, (SW - 44, 36), "by Novality Store", F("hand", 40),
              "#F3D98B", anchor="ra")
    # countdown band
    d.rectangle([0, 108, SW, 108 + 62], fill=hexrgb(BURGUNDY))
    draw_text(d_img, (SW / 2.0, 116), a["countdown"], F("serif_b", 33),
              CREAM, anchor="ma")
    # meta band
    d.rectangle([0, 170, SW, 170 + 42], fill=hexrgb(SOFT["gold"]))
    meta = (f"Today: Saturday 12 September 2026   •   Christmas: Friday "
            f"25 December 2026   •   {a['gifts_purchased']} of "
            f"{a['gifts_planned']} gifts bought")
    f = F("sans_md", 17)
    if text_width(meta, f) > SW - 80:
        meta = (f"Today: 12 September 2026  •  Christmas: 25 December 2026  "
                f"•  {a['gifts_purchased']} of {a['gifts_planned']} gifts "
                f"bought")
    draw_text(d_img, (SW / 2.0, 179), meta, f, INK, anchor="ma")
    y = 228
    # ---- budget section
    y = section_bar(d_img, y, "💰 BUDGET AT A GLANCE", PINE) + 16
    cw = (SW - 88 - 3 * 16) / 4.0
    kx = 44
    kpi_card(d_img, kx, y, cw, "TOTAL BUDGET", _money(a["budget_planned"]),
             "pine", value_size=38)
    kpi_card(d_img, kx + (cw + 16), y, cw, "SPENT SO FAR",
             _money(a["budget_actual"]), "burgundy", value_size=38)
    kpi_card(d_img, kx + 2 * (cw + 16), y, cw, "STILL TO SPEND",
             _money(a["budget_remaining"]), "ok", value_size=38)
    kpi_card(d_img, kx + 3 * (cw + 16), y, cw, "BUDGET USED",
             f"{a['budget_pct']:.1%}", "gold", value_size=38)
    y += 116
    draw_text(d_img, (44, y + 6), "Budget progress", F("sans_sb", 16), MUTED)
    blocks_bar(d_img, [230, y, SW - 250, y + 30], a["budget_pct"], n=40)
    chip(d_img, (SW - 240, y - 5), f"⚠️ {a['budget_pct']:.0%} used",
         SOFT["warn"], WARN, size=16)
    y += 52
    A["after_budget"] = y
    # ---- gift section
    y = section_bar(d_img, y, "🎁 GIFT PROGRESS", BURGUNDY) + 16
    cards = [
        ("GIFTS PLANNED", str(a["gifts_planned"]), "pine"),
        ("PURCHASED", f"{a['gifts_purchased']} / {a['gifts_planned']}",
         "ok"),
        ("WRAPPED", str(a["gifts_wrapped"]), "gold"),
        ("GIVEN", str(a["gifts_delivered"]), "burgundy"),
        ("STILL TO BUY", str(a["gifts_to_buy"]), "warn"),
        ("ON ORDER", str(a["gifts_ordered"]), "info"),
        ("COMPLETION", f"{a['gift_completion']:.0%}", "pine2"),
        ("AVG / PERSON", _money(a["avg_per_recipient"]), "plum"),
    ]
    for i in range(2):
        for j in range(4):
            lbl, val, col = cards[i * 4 + j]
            kpi_card(d_img, kx + j * (cw + 16), y + i * 112, cw, lbl, val,
                     col, value_size=32, h_label=30, h_value=66)
    y += 2 * 112 + 14
    draw_text(d_img, (44, y + 6), "Gift progress", F("sans_sb", 16), MUTED)
    blocks_bar(d_img, [230, y, SW - 250, y + 30],
               a["gifts_purchased"] / float(a["gifts_planned"]), n=40,
               fg=BURGUNDY)
    chip(d_img, (SW - 240, y - 5), f"🎁 {a['gifts_purchased']} / "
         f"{a['gifts_planned']} gifts", SOFT["burgundy"], BURGUNDY, size=16)
    y += 52
    A["after_gifts"] = y
    # ---- charts
    A["charts"] = y
    y = section_bar(d_img, y, "📊 WHERE THE MONEY GOES", GOLD) + 24
    rec = [r for r in a["recipients"] if r["gifts"]][:8]
    S.hbar_chart(d_img, (44, y + 60, 636, y + 300), "Spending per person",
                 [(r["name"], r["spent"]) for r in rec])
    cats = [c["name"] for c in a["categories"][:10]]
    short = [c[:8] + "…" if len(c) > 9 else c for c in cats]
    S.grouped_columns(
        d_img, (660, y + 60, SW - 44, y + 300), "Budget vs actual by category",
        short,
        [("Planned", [m.budget_planned.get(
            ["gifts", "stockings", "wrapping", "cards", "food", "baking",
             "decor", "party", "travel", "other"][i], 0) for i in
            range(len(cats))], GOLD),
         ("Actual", [next((b["actual"] for b in a["budget_rows"]
                           if b["key"] == ["gifts", "stockings", "wrapping",
                                           "cards", "food", "baking", "decor",
                                           "party", "travel", "other"][i]),
                          0) for i in range(len(cats))], BURGUNDY)],
        fmt="{:,.0f}")
    y += 330
    status_items = [(s["name"], s["count"],
                     {"💡 Idea": PLUM, "🛒 Need to Buy": WARN,
                      "🛍️ Ordered": INFO, "✅ Purchased": OK,
                      "🎀 Wrapped": GOLD, "📦 Delivered": PINE}[s["name"]])
                    for s in a["status_counts"]]
    S.doughnut_chart(d_img, (44, y + 60, 636, y + 300),
                     "Where the gifts are at", status_items)
    S.stacked_columns(
        d_img, (660, y + 60, SW - 44, y + 300),
        "Gifts per person: bought vs to buy",
        [r["name"].split()[0][:8] for r in rec[:8]],
        [("Bought", [r["bought"] for r in rec[:8]], PINE2),
         ("Still to buy", [r["to_buy"] for r in rec[:8]], GOLD)],
        fmt="{:,.0f}")
    y += 336
    A["after_charts"] = y
    # ---- what's left + deadlines (also returned for side panels)
    y = section_bar(d_img, y, "🎯 WHAT'S LEFT TO DO", PINE2) + 14
    A["todo_panel"] = y - 66
    todo_lines = [t[1] for t in _todo_lines(bk)]
    yy = y
    for line in todo_lines[:9]:
        draw_text(d_img, (44, yy), line, F("sans_md", 18), INK)
        yy += 34
    y = max(yy, y) + 10
    # deadlines
    dy = section_bar(d_img, y, "⏰ NEXT DEADLINES", BURGUNDY) + 14
    A["deadlines"] = dy - 66
    for dl, label in a["pool"][:6]:
        f = F("sans_sb", 17)
        rrect(d, [44, dy, 120, dy + 30], 6, fill=hexrgb(SOFT["gold"]))
        draw_text(d_img, (82, dy + 5), _fmt_d(dl), f, INK, anchor="ma")
        draw_text(d_img, (140, dy + 5), label, F("sans_md", 17), INK)
        nd = _days(dl)
        chip(d_img, (SW - 200, dy - 2),
             f"{nd} days" if nd >= 0 else "overdue",
             SOFT["ok"] if nd > 7 else SOFT["warn"],
             OK if nd > 7 else WARN, size=15)
        dy += 40
    y = dy + 8
    # key dates strip
    draw_text(d_img, (44, y), "KEY DATES", F("sans_b", 15), MUTED)
    y += 28
    keyd = [("🛒 Last online order", m.event_date.__sub__(
                 timedelta(days=10))),
            ("📮 Cards in the post", m.event_date.__sub__(
                 timedelta(days=14))),
            ("🎀 Wrapping day", m.event_date.__sub__(
                 timedelta(days=2))),
            ("🎄 The big day", m.event_date)]
    xx = 44
    for label, dt in keyd:
        w = max(text_width(label, F("sans_sb", 16)),
                text_width(_fmt_d(dt) + f"  ({_days(dt)}d)", F("sans", 15)))
        rrect(d, [xx, y, xx + w + 36, y + 74], 10, fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
        draw_text(d_img, (xx + 18, y + 10), label, F("sans_sb", 16), PINE)
        draw_text(d_img, (xx + 18, y + 38),
                  f"{dt.strftime('%d %b')}  ({_days(dt)}d)", F("sans", 15),
                  MUTED)
        xx += w + 36 + 14
    y += 100
    A["after_deadlines"] = y
    # ---- per-recipient table
    y = section_bar(d_img, y, "🎅 PER-RECIPIENT SUMMARY", PINE) + 14
    widths = [190, 108, 108, 108, 84, 84, 84, 96, 268]
    headers = ["Recipient", "Budget", "Spent", "Remaining", "Gifts", "Bought",
               "Wrapped", "Done", "Progress"]
    rows = []
    for r in a["recipients"][:9]:
        if not r["name"]:
            continue
        rows.append([
            r["name"],
            {"t": _money(r["planned"]), "align": "r"},
            {"t": _money(r["spent"]), "align": "r"},
            {"t": _money(r["planned"] - r["spent"]), "align": "r",
             "color": "bad" if r["planned"] - r["spent"] < 0 else "ink"},
            {"t": str(r["gifts"]), "align": "c"},
            {"t": str(r["bought"]), "align": "c"},
            {"t": str(r["wrapped"]), "align": "c"},
            {"t": f"{r['pct']:.0%}", "align": "c", "bold": True},
            ""])
    ty = draw_table(d_img, 44, y, widths, headers, rows, row_h=44,
                    hdr_bg=PINE)
    for i, r in enumerate([r for r in a["recipients"][:9] if r["name"]]):
        ry = y + 48 + i * 44 + 8
        blocks_bar(d_img, [44 + sum(widths[:-1]) + 12, ry,
                           44 + sum(widths) - 8, ry + 27],
                   r["pct"], n=12, gap=2)
    y = ty + 10
    # ---- nav + footer
    y = _nav(d_img, y) + 12
    _footer(d_img, y + 54)
    img = d_img.crop((0, 0, SW, y + 54))
    A["full_h"] = img.height
    if anchors is not None:
        anchors.update(A)
    return img


def _todo_lines(bk):
    try:
        from christmas_tracker.sheets.dashboard import _todo_lines as fn
        return fn(bk)
    except Exception:
        return []


# ---------------------------------------------------------------------------
def screen_shopping(m, bk):
    a = m.agg
    pills = [(f"🛍️ {a['shop_total']} items", "info"),
             (f"✅ {a['shop_bought']} bought", "ok"),
             (f"💸 {_money(a['shop_spent'])} spent", "burgundy")]
    rows = []
    for s in m.shopping[:10]:
        rows.append([
            s["item"], s["category"], s["store"],
            {"t": str(s["qty"]), "align": "c"},
            {"t": _money(s["unit"]) if s["unit"] else "—", "align": "r"},
            {"t": _money(s["cost"]) if s["cost"] else "—", "align": "r"},
            {"tick": s["bought"] == "✓"},
            s["notes"] or "—"])
    H = 104 + 56 + 48 + (len(rows) + 1) * 46 + 24 + 54
    img = Image.new("RGBA", (SW, H), hexrgb(CANVAS))
    y = sheet_header(img, "🛍️  Shopping List",
                     "Wrapping, cards, baking, decorations, party bits — the "
                     "stuff that quietly eats the budget.")
    y = pill_row(img, y + 8, pills) + 18
    widths = [330, 160, 150, 80, 110, 110, 110, 272]
    headers = ["Item", "Category", "Store", "Qty", "Unit", "Cost", "Bought",
               "Notes"]
    y = draw_table(img, 44, y, widths, headers, rows, hdr_bg=INFO)
    draw_table(img, 44, y + 10, widths, [""] * 8,
               [[{"t": "TOTALS", "bold": True},
                 {"t": f"{a['shop_total']} items", "bold": True}, "",
                 {"t": f"{a['shop_bought']} bought", "align": "c",
                  "bold": True},
                 "",
                 {"t": _money(a["shop_spent"]), "align": "r", "bold": True},
                 {"t": f"{a['shop_total'] - a['shop_bought']} to go", "align":
                  "c", "bold": True},
                 {"t": "rolls into the Budget tab", "bold": True}]],
               row_h=48, hdr_bg=INFO)
    _footer(img, H)
    return img
