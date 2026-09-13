"""
The fictional EXAMPLE business: Willow & Wren Crochet Studio.

Every cached value shown in the workbooks is computed here from the raw
records below, so the filled example is always internally consistent
(sales log <-> production batches <-> fair totals <-> dashboard).
"""

import datetime


def today():
    return datetime.date(2026, 9, 13)


SETTINGS = {
    "business": "Willow & Wren Crochet Studio",
    "message": "Autumn fair season - stock up on chunky yarn!",
    "currency": "$",
    "year": 2026,
    "wage": 14.0,
    "overhead": 0.10,
    "margin": 0.45,
}

# sku, name, category, desc, price, yarn, pack, hours, min, link
PRODUCTS = [
    ("CB-001", "Amigurumi Bunny", "Toys & Amigurumi",
     "Soft cotton bunny with safety eyes", 28.00, 4.20, 0.80, 2.5, 4,
     "photos/bunny.jpg"),
    ("CB-002", "Chunky Beanie", "Wearables",
     "Super chunky merino beanie", 24.00, 5.60, 0.70, 1.5, 6,
     "photos/beanie.jpg"),
    ("CB-003", "Granny Square Cardigan", "Wearables",
     "Hand-joined granny squares", 95.00, 18.40, 2.20, 12.0, 2,
     "photos/cardigan.jpg"),
    ("CB-004", "Market Tote Bag", "Accessories",
     "Sturdy cotton market tote", 32.00, 6.10, 1.00, 3.0, 5,
     "photos/tote.jpg"),
    ("CB-005", "Cozy Scarf", "Wearables",
     "Worsted wool scarf", 38.00, 8.90, 1.10, 4.0, 4, "photos/scarf.jpg"),
    ("CB-006", "Baby Booties", "Baby & Kids",
     "Tiny soft booties, pair", 18.00, 2.60, 0.60, 1.2, 6,
     "photos/booties.jpg"),
    ("CB-007", "Flower Coaster Set", "Home & Decor",
     "Set of 4 cotton coasters", 16.00, 2.20, 0.50, 1.0, 8,
     "photos/coasters.jpg"),
    ("CB-008", "Lap Blanket", "Home & Decor",
     "Granny stripe lap blanket", 75.00, 16.80, 2.00, 10.0, 2,
     "photos/blanket.jpg"),
    ("CB-009", "Ear Warmer Headband", "Accessories",
     "Twisted ear warmer", 16.00, 2.90, 0.50, 1.0, 4, "photos/earwarmer.jpg"),
    ("CB-010", "Stuffed Octopus", "Toys & Amigurumi",
     "Squishy friend octopus", 26.00, 4.60, 0.80, 2.5, 4,
     "photos/octopus.jpg"),
    ("CB-011", "Table Runner", "Home & Decor",
     "Lacy cotton table runner", 55.00, 10.40, 1.60, 7.0, 2,
     "photos/runner.jpg"),
    ("CB-012", "Keychain Charm", "Accessories",
     "Mini amigurumi keychain", 10.00, 1.10, 0.40, 0.5, 6,
     "photos/charm.jpg"),
]

# name, color, brand, weight, purchased, unit, cost_unit, used, supplier,
# threshold
MATERIALS = [
    ("Cotton yarn - natural", "Natural", "Cotton Craft Co",
     "Worsted / aran", 20, "balls", 3.40, 16, "Local yarn shop", 5),
    ("Acrylic yarn - raspberry", "Raspberry", "Value Yarns",
     "Worsted / aran", 15, "balls", 2.60, 9, "Online yarn store", 4),
    ("Merino wool - sage", "Sage", "Highland Fibres", "DK / light", 12,
     "balls", 6.80, 10, "Local yarn shop", 4),
    ("Chenille chunky - cream", "Cream", "Snuggle Spun", "Super chunky", 10,
     "balls", 4.90, 6, "Online yarn store", 3),
    ("Cotton yarn - mustard", "Mustard", "Cotton Craft Co", "DK / light", 8,
     "balls", 3.20, 7, "Local yarn shop", 3),
    ("Wool blend - lavender", "Lavender", "Highland Fibres",
     "Worsted / aran", 10, "balls", 5.40, 4, "Wholesale craft", 3),
    ("Polyester stuffing", "White", "Craft Basics", "Mixed / other", 6,
     "pieces", 2.10, 4, "Wholesale craft", 2),
    ("Bamboo buttons", "Natural", "Craft Basics", "Mixed / other", 40,
     "pieces", 0.35, 22, "Online yarn store", 10),
    ("Safety eyes", "Black", "Craft Basics", "Mixed / other", 30, "pieces",
     0.25, 24, "Wholesale craft", 10),
    ("Paper gift tags", "Kraft", "Print & Tag", "Mixed / other", 60,
     "pieces", 0.15, 35, "Market stall", 20),
]

# product, date, made, reserved, taken, sold, returned, damaged, notes
PRODUCTION = [
    ("Amigurumi Bunny", datetime.date(2026, 3, 2), 11, 1, 10, 6, 0, 0,
     "Best spring seller"),
    ("Chunky Beanie", datetime.date(2026, 3, 12), 15, 1, 12, 5, 0, 0, ""),
    ("Granny Square Cardigan", datetime.date(2026, 4, 18), 3, 0, 2, 1, 0, 0,
     "Made to order"),
    ("Market Tote Bag", datetime.date(2026, 4, 2), 11, 1, 10, 8, 0, 0, ""),
    ("Cozy Scarf", datetime.date(2026, 8, 22), 6, 0, 4, 2, 0, 0,
     "Autumn stock"),
    ("Baby Booties", datetime.date(2026, 3, 28), 8, 0, 6, 5, 0, 0, ""),
    ("Flower Coaster Set", datetime.date(2026, 2, 20), 20, 0, 16, 14, 0, 1,
     "One water damaged"),
    ("Lap Blanket", datetime.date(2026, 2, 10), 3, 0, 3, 2, 0, 0,
     "Sold out online"),
    ("Ear Warmer Headband", datetime.date(2026, 5, 2), 10, 0, 10, 10, 0, 0,
     "Sold out at fete"),
    ("Stuffed Octopus", datetime.date(2026, 8, 25), 10, 2, 6, 3, 0, 0,
     "Reserved for market"),
    ("Table Runner", datetime.date(2026, 3, 5), 3, 0, 3, 3, 0, 0, ""),
    ("Keychain Charm", datetime.date(2026, 4, 20), 18, 0, 16, 18, 0, 0,
     "Impulse buy winner"),
]

# name, date, location, organizer, booth, travel, parking, food, display,
# taken
EVENTS = [
    ("Spring Makers Market", datetime.date(2026, 3, 14), "Town Hall",
     "Makers Guild", 45, 12, 5, 8, 20, 38),
    ("Easter Craft Bazaar", datetime.date(2026, 4, 5), "Church Hall",
     "St Mary's", 30, 8, 0, 6, 10, 20),
    ("School Fete Stall", datetime.date(2026, 5, 16), "Primary School",
     "PTA", 25, 6, 0, 5, 8, 30),
    ("Summer Night Bazaar", datetime.date(2026, 6, 19), "Riverside Park",
     "City Council", 60, 15, 6, 10, 25, 30),
    ("Farmers Market Pop-up", datetime.date(2026, 7, 25), "Market Square",
     "Growers Co-op", 40, 10, 4, 7, 12, 16),
    ("Online Order Batch", datetime.date(2026, 8, 30), "Online",
     "Own shop", 0, 0, 0, 0, 0, 0),
    ("Autumn Craft Fair", datetime.date(2026, 9, 26), "Exhibition Centre",
     "Craft Collective", 75, 20, 8, 12, 30, 0),
    ("Winter Holiday Market", datetime.date(2026, 11, 28), "Civic Square",
     "City Council", 85, 18, 8, 12, 35, 0),
]

# date, event, product, qty, unit, discount, method, ref, notes
SALES = [
    (datetime.date(2026, 3, 14), "Spring Makers Market", "Amigurumi Bunny",
     4, 28.00, 0, "Card", "SPR-01", ""),
    (datetime.date(2026, 3, 14), "Spring Makers Market", "Chunky Beanie",
     3, 24.00, 0, "Cash", "", ""),
    (datetime.date(2026, 3, 14), "Spring Makers Market",
     "Flower Coaster Set", 5, 16.00, 0, "Cash", "", ""),
    (datetime.date(2026, 3, 14), "Spring Makers Market", "Baby Booties",
     2, 18.00, 0, "Card", "SPR-02", ""),
    (datetime.date(2026, 4, 5), "Easter Craft Bazaar", "Baby Booties",
     3, 18.00, 0, "Cash", "", ""),
    (datetime.date(2026, 4, 5), "Easter Craft Bazaar", "Amigurumi Bunny",
     2, 28.00, 0, "Card", "EAS-01", ""),
    (datetime.date(2026, 4, 5), "Easter Craft Bazaar", "Flower Coaster Set",
     4, 16.00, 0, "Cash", "", ""),
    (datetime.date(2026, 5, 16), "School Fete Stall", "Keychain Charm",
     10, 10.00, 0, "Cash", "", "Kids loved these"),
    (datetime.date(2026, 5, 16), "School Fete Stall", "Ear Warmer Headband",
     6, 16.00, 0, "Cash", "", ""),
    (datetime.date(2026, 5, 16), "School Fete Stall", "Flower Coaster Set",
     3, 16.00, 0, "Cash", "", ""),
    (datetime.date(2026, 6, 19), "Summer Night Bazaar", "Market Tote Bag",
     4, 32.00, 0, "Card", "SUM-01", ""),
    (datetime.date(2026, 6, 19), "Summer Night Bazaar",
     "Ear Warmer Headband", 4, 16.00, 0, "Cash", "", ""),
    (datetime.date(2026, 6, 19), "Summer Night Bazaar", "Chunky Beanie",
     2, 24.00, 0, "Card", "SUM-02", ""),
    (datetime.date(2026, 6, 19), "Summer Night Bazaar", "Keychain Charm",
     8, 10.00, 0, "Cash", "", ""),
    (datetime.date(2026, 6, 19), "Summer Night Bazaar", "Stuffed Octopus",
     3, 26.00, 0, "Card", "SUM-03", ""),
    (datetime.date(2026, 7, 25), "Farmers Market Pop-up", "Market Tote Bag",
     4, 32.00, 0, "Cash", "", ""),
    (datetime.date(2026, 7, 25), "Farmers Market Pop-up", "Cozy Scarf",
     2, 38.00, 0, "Card", "FAR-01", ""),
    (datetime.date(2026, 7, 25), "Farmers Market Pop-up", "Lap Blanket",
     1, 75.00, 0, "Card", "FAR-02", ""),
    (datetime.date(2026, 7, 25), "Farmers Market Pop-up",
     "Flower Coaster Set", 2, 16.00, 2.00, "Cash", "", "Friend discount"),
    (datetime.date(2026, 8, 30), "Online Order Batch",
     "Granny Square Cardigan", 1, 95.00, 0, "Bank transfer", "INV-2041",
     "Commission"),
    (datetime.date(2026, 8, 30), "Online Order Batch", "Lap Blanket",
     1, 75.00, 0, "Bank transfer", "INV-2042", ""),
    (datetime.date(2026, 8, 30), "Online Order Batch", "Table Runner",
     3, 55.00, 0, "Online order", "INV-2043", ""),
]

PACKING_TICKS = {
    "Finished products": True, "Extra inventory": True,
    "Price tags": True, "Product labels / care cards": True,
    "Table": True, "Tablecloth": True, "Display stands / risers": True,
    "Baskets & bins": True, "Signage & banner": False,
    "Business cards": False,
    "Cash float": True, "Card reader": True, "Phone / tablet": True,
    "Charger": False, "Payment QR code": False,
    "Shopping bags": True, "Tissue paper": True, "Tape & scissors": True,
    "Pens": False, "Receipt book": False, "Sticky tack / clips": False,
}

PRICING = {"material": 4.00, "packaging": 1.00, "hours": 1.5, "wage": 14.0,
           "overhead": 0.10, "margin": 0.45}

PROFIT_EVENT = "Summer Night Bazaar"


class Demo(object):
    """Raw records plus every aggregate the builders cache."""

    def __init__(self):
        self.settings = dict(SETTINGS)
        self.products = [dict(zip(
            ("sku", "name", "category", "desc", "price", "yarn", "pack",
             "hours", "min", "link"), p)) for p in PRODUCTS]
        self.materials = [dict(zip(
            ("name", "color", "brand", "weight", "purchased", "unit",
             "cost_unit", "used", "supplier", "threshold"), m))
            for m in MATERIALS]
        self.production = [dict(zip(
            ("product", "date", "made", "reserved", "taken", "sold",
             "returned", "damaged", "notes"), p)) for p in PRODUCTION]
        self.events = [dict(zip(
            ("name", "date", "location", "organizer", "booth", "travel",
             "parking", "food", "display", "taken"), e)) for e in EVENTS]
        self.sales = [dict(zip(
            ("date", "event", "product", "qty", "unit", "discount",
             "method", "ref", "notes"), s)) for s in SALES]
        self.packing = dict(PACKING_TICKS)
        self.pricing = dict(PRICING)
        self.profit_event = PROFIT_EVENT
        for p in self.products:
            p["unit_cost"] = round(p["yarn"] + p["pack"], 2)
            p["profit"] = round(p["price"] - p["unit_cost"], 2)
            p["margin"] = p["profit"] / p["price"]
        for m in self.materials:
            m["total"] = round(m["purchased"] * m["cost_unit"], 2)
            m["remaining"] = m["purchased"] - m["used"]
        for b in self.production:
            b["current"] = (b["made"] + b["returned"] - b["sold"]
                            - b["damaged"])
            b["available"] = b["current"] - b["reserved"]
        for p in self.products:
            p["stock"] = sum(b["current"] for b in self.production
                             if b["product"] == p["name"])
            p["status"] = (_stock_status(p["stock"], p["min"]))
        for e in self.events:
            e["total"] = (e["booth"] + e["travel"] + e["parking"] + e["food"]
                          + e["display"])
            rows = [s for s in self.sales if s["event"] == e["name"]]
            e["sold"] = sum(s["qty"] for s in rows)
            e["sales"] = round(sum(s["qty"] * s["unit"] - s["discount"]
                                   for s in rows), 2)
            e["cogs"] = round(sum(s["qty"] * _uc(self, s["product"])
                                  for s in rows), 2)
            e["net"] = round(e["sales"] - e["total"] - e["cogs"], 2)
            e["margin"] = (e["net"] / e["sales"]) if e["sales"] else 0.0
            e["best"] = _best_product(rows)
        self.agg = self._aggregates()

    # ------------------------------------------------------------------
    def _aggregates(self):
        a = {}
        rev = round(sum(s["qty"] * s["unit"] - s["discount"]
                        for s in self.sales), 2)
        disc = round(sum(s["discount"] for s in self.sales), 2)
        cogs = round(sum(s["qty"] * _uc(self, s["product"])
                         for s in self.sales), 2)
        fees = round(sum(e["total"] for e in self.events), 2)
        units = sum(s["qty"] for s in self.sales)
        profit = round(rev - cogs - fees, 2)
        made = sum(b["made"] for b in self.production)
        a.update(revenue=rev, discounts=disc, cogs=cogs, fees=fees,
                 profit=profit, margin=profit / rev if rev else 0.0,
                 units=units, txns=len(self.sales),
                 aov=rev / len(self.sales) if self.sales else 0.0,
                 per_item=profit / units if units else 0.0,
                 events_total=len(self.events),
                 events_done=sum(1 for e in self.events
                                 if e["date"] <= today() and e["sales"]),
                 inv_value=round(sum(p["stock"] * p["unit_cost"]
                                     for p in self.products), 2),
                 low_products=sum(1 for p in self.products
                                  if p["stock"] < p["min"]),
                 low_materials=sum(1 for m in self.materials
                                   if m["remaining"] <= m["threshold"]),
                 sell_through=units / made if made else 0.0,
                 made_total=made)
        a["reorder_cost"] = round(self._reorder_cost(), 2)
        done = [e for e in self.events if e["sales"]]
        a["best_event"] = max(done, key=lambda e: e["net"])["name"] if done \
            else ""
        per_prod = self._product_stats()
        a["best_product"] = max(per_prod, key=lambda r: r["revenue"])["name"]
        a["bs_units"] = max(per_prod, key=lambda r: r["units"])["name"]
        a["bs_revenue"] = max(per_prod, key=lambda r: r["revenue"])["name"]
        a["bs_profit"] = max(per_prod, key=lambda r: r["profit"])["name"]
        a["bs_margin"] = max(per_prod, key=lambda r: r["margin_adj"])["name"]
        a["bs_slow"] = min(per_prod, key=lambda r: r["slow_adj"])["name"]
        a["product_stats"] = [(r["name"], r["units"], r["revenue"],
                               r["stock"], r["margin_adj"], r["slow_adj"])
                              for r in per_prod]
        a["event_stats"] = [(e["name"], e["sales"], e["net"], e["sold"])
                            for e in self.events]
        a["months"] = self._months()
        a["payments"] = self._payments()
        a["exp_cats"] = [("Booth fees", sum(e["booth"] for e in self.events)),
                         ("Travel", sum(e["travel"] for e in self.events)),
                         ("Parking", sum(e["parking"]
                                         for e in self.events)),
                         ("Food & drinks", sum(e["food"]
                                               for e in self.events)),
                         ("Display & decor", sum(e["display"]
                                                 for e in self.events))]
        q = self.pricing
        labor = q["hours"] * q["wage"]
        sub = q["material"] + q["packaging"] + labor
        oh = sub * q["overhead"]
        true_cost = sub + oh
        price = true_cost / (1 - q["margin"]) if q["margin"] < 1 else 0
        a["price_suggest"] = round(price, 2)
        a["pricing"] = dict(q, labor=labor, overhead_amt=oh,
                            true_cost=true_cost, price=price,
                            charm=_charm(price), profit=price - true_cost)
        ep = self.profit_event
        ev = [e for e in self.events if e["name"] == ep][0]
        rows = [s for s in self.sales if s["event"] == ep]
        gross = ev["sales"]
        gp = gross - ev["cogs"]
        tc = ev["cogs"] + ev["total"]
        a["event_profit"] = {
            "event": ep, "units": ev["sold"], "gross": gross,
            "discounts": round(sum(s["discount"] for s in rows), 2),
            "cogs": ev["cogs"], "booth": ev["booth"], "travel": ev["travel"],
            "parking": ev["parking"], "food": ev["food"],
            "display": ev["display"], "gross_profit": round(gp, 2),
            "total_cost": round(tc, 2), "net": ev["net"],
            "margin": ev["margin"],
            "avg_sale": gross / len(rows) if rows else 0.0,
            "breakeven": tc / (gp / gross) if gross and gp else 0.0,
            "roi": ev["net"] / tc if tc else 0.0}
        a["packed"] = sum(1 for v in self.packing.values() if v)
        a["packed_total"] = len(self.packing)
        return a

    # ------------------------------------------------------------------
    def _product_stats(self):
        out = []
        for p in self.products:
            rows = [s for s in self.sales if s["product"] == p["name"]]
            units = sum(s["qty"] for s in rows)
            revenue = round(sum(s["qty"] * s["unit"] - s["discount"]
                                for s in rows), 2)
            out.append({"name": p["name"], "units": units,
                        "revenue": revenue, "stock": p["stock"],
                        "profit": round(units * p["profit"], 2),
                        "margin_adj": p["margin"] if units else 0.0,
                        "slow_adj": units})
        return out

    def _months(self):
        out = []
        for m in range(1, 13):
            rows = [s for s in self.sales if s["date"].month == m
                    and s["date"].year == self.settings["year"]]
            evs = [e for e in self.events if e["date"].month == m
                   and e["date"].year == self.settings["year"]]
            rev = round(sum(s["qty"] * s["unit"] - s["discount"]
                            for s in rows), 2)
            cogs = round(sum(s["qty"] * _uc(self, s["product"])
                             for s in rows), 2)
            fees = round(sum(e["total"] for e in evs), 2)
            units = sum(s["qty"] for s in rows)
            net = round(rev - cogs - fees, 2)
            out.append((m, rev, cogs, fees, net, units, len(evs),
                        len(rows)))
        return out

    def _payments(self):
        out = []
        for method in ("Cash", "Card", "Bank transfer", "Mobile wallet",
                       "Online order", "Other"):
            out.append((method, round(sum(
                s["qty"] * s["unit"] - s["discount"]
                for s in self.sales if s["method"] == method), 2)))
        return out

    def _reorder_cost(self):
        total = 0.0
        for p in self.products:
            if p["stock"] < p["min"]:
                total += (p["min"] * 2 - p["stock"]) * p["unit_cost"]
        for m in self.materials:
            if m["remaining"] <= m["threshold"]:
                total += (m["threshold"] * 2 - m["remaining"]) * \
                    m["cost_unit"]
        return total

    # ------------------------------------------------------------------
    def money(self, value, decimals=0):
        return "%s%s" % (self.settings["currency"],
                         format(round(value, decimals),
                                ",.%df" % decimals))


def _uc(demo, product):
    for p in demo.products:
        if p["name"] == product:
            return p["unit_cost"]
    return 0.0


def _stock_status(stock, minimum):
    if stock <= 0:
        return "out"
    if stock < minimum:
        return "low"
    return "ok"


def _best_product(rows):
    if not rows:
        return ""
    tally = {}
    for s in rows:
        tally[s["product"]] = tally.get(s["product"], 0) + s["qty"]
    return max(tally, key=tally.get)


def _charm(price):
    import math
    if not price:
        return 0.0
    return round(math.ceil(price) - 0.05, 2)
