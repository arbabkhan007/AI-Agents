"""A worked example: one small supply business, mid-year, mid-mess.

Thornfield Supply Co. buys and makes homeware and sells it three
ways - a marketplace shop, a handful of wholesale stockists, and the
occasional market stall. The year it is having is deliberately not a
tidy one, because a sample company where everything reconciles teaches
you nothing about what the alert columns are for.

In this example you will find: a bestseller that has been out of stock
for nine days while the purchase order sits unsent; a supplier whose
deliveries are reliably a week late and whose lead time in the
database still says seven days; a wholesale order confirmed three
weeks ago and never picked, quietly reserving ninety units; a pallet
of mugs received against a purchase order where the invoice quantity
and the delivered quantity disagree; a product being sold at a tier
price below its own floor; and a stock count that found eleven fewer
candles than the system believed.

Every row here is checked twice before it ships. The keys must all be
*input* columns on their register - a value written into a formula
column is silently dropped and takes the formula with it - and every
value that feeds a drop-down must exist in that drop-down's list.
``tools/check_inventory_sample.py`` does both checks.

Dates are relative to ``cfg.today``, so the example stays current
whenever the workbook is built.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Callable, Dict, List

from .config import Config, MOVEMENT_TYPES

Rows = List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _day(cfg: Config, offset: int) -> _dt.date:
    """A date `offset` days from the build date."""
    return cfg.today + _dt.timedelta(days=offset)


def _sup(n: int) -> str:
    return f"SUP-{n:03d}"


def _po(n: int) -> str:
    return f"PO-{n:04d}"


def _cust(n: int) -> str:
    return f"WC-{n:03d}"


def _ord(n: int) -> str:
    return f"WO-{n:04d}"


def _loc(n: int) -> str:
    return f"LOC-{n:03d}"


# ---------------------------------------------------------------------------
# the catalogue
# ---------------------------------------------------------------------------
# (sku, name, category, subcategory, variant, size, colour, material,
#  unit, supplier, cost, retail, wholesale, floor, opening_qty,
#  min, max, status)
_CATALOGUE = [
    ("CND-JAR-SAGE", "Sage & Sea Salt Jar Candle", "Candles",
     "Jar candles", "Standard", "220ml", "Sage", "Soy wax", "Each",
     1, 4.80, 18.00, 9.00, 7.50, 180, 60, 400, "Active"),
    ("CND-JAR-FIG", "Black Fig Jar Candle", "Candles", "Jar candles",
     "Standard", "220ml", "Charcoal", "Soy wax", "Each", 1, 4.80,
     18.00, 9.00, 7.50, 42, 60, 400, "Active"),
    ("CND-JAR-LIN", "Fresh Linen Jar Candle", "Candles",
     "Jar candles", "Standard", "220ml", "White", "Soy wax", "Each",
     1, 4.80, 18.00, 9.00, 7.50, 96, 48, 300, "Active"),
    ("CND-PIL-IVY", "Ivory Pillar Candle", "Candles",
     "Pillar candles", "Tall", "20cm", "Ivory", "Soy wax", "Each", 1,
     3.20, 12.00, 6.00, 5.00, 210, 40, 300, "Active"),
    ("CND-TEA-12", "Tealights, Box of 12", "Candles", "Tealights",
     "Boxed", "12 pack", "Natural", "Soy wax", "Box of 24", 1, 2.40,
     9.50, 4.75, 4.00, 64, 30, 240, "Active"),
    ("CND-MLT-CIT", "Citrus Grove Wax Melts", "Candles", "Wax melts",
     "Clamshell", "6 cube", "Yellow", "Soy wax", "Pack of 6", 1,
     1.60, 7.00, 3.50, 2.90, 150, 40, 260, "Active"),

    ("CER-MUG-350", "Stoneware Mug 350ml", "Ceramics", "Mugs",
     "Glazed", "350ml", "Oat", "Stoneware", "Each", 2, 6.10, 24.00,
     12.00, 10.00, 120, 48, 320, "Active"),
    ("CER-MUG-250", "Stoneware Mug 250ml", "Ceramics", "Mugs",
     "Glazed", "250ml", "Oat", "Stoneware", "Each", 2, 5.40, 21.00,
     10.50, 8.80, 88, 36, 240, "Active"),
    ("CER-MUG-SEC", "Stoneware Mug - Seconds", "Ceramics", "Mugs",
     "Seconds", "350ml", "Mixed", "Stoneware", "Each", 2, 6.10,
     12.00, 7.00, 6.50, 34, 0, 60, "Clearance"),
    ("CER-BWL-SML", "Breakfast Bowl, Small", "Ceramics", "Bowls",
     "Glazed", "14cm", "Oat", "Stoneware", "Each", 2, 7.20, 26.00,
     13.00, 11.00, 60, 24, 180, "Active"),
    ("CER-PLT-TER", "Terracotta Planter", "Ceramics", "Planters",
     "Unglazed", "16cm", "Terracotta", "Clay", "Each", 2, 5.90,
     22.00, 11.00, 9.50, 57, 24, 160, "Active"),
    ("CER-VAS-BUD", "Bud Vase", "Ceramics", "Vases", "Glazed",
     "12cm", "Sage", "Stoneware", "Each", 2, 4.40, 17.00, 8.50,
     7.20, 100, 24, 150, "Active"),

    ("TEX-TWL-2PK", "Linen Tea Towels, Pair", "Textiles",
     "Tea towels", "Pair", "50x70cm", "Natural", "Linen", "Pair", 3,
     5.60, 20.00, 10.00, 8.50, 114, 30, 200, "Active"),
    ("TEX-CSH-45", "Cushion Cover 45cm", "Textiles",
     "Cushion covers", "Zipped", "45cm", "Clay", "Cotton", "Each", 3,
     8.30, 32.00, 16.00, 13.50, 36, 18, 120, "Active"),
    ("TEX-APR-NAT", "Cross-back Apron", "Textiles", "Aprons",
     "Adult", "One size", "Natural", "Linen", "Each", 3, 11.40,
     42.00, 21.00, 18.00, 22, 12, 80, "Active"),
    ("TEX-TOT-CAN", "Canvas Tote Bag", "Textiles", "Tote bags",
     "Printed", "38x42cm", "Natural", "Cotton", "Each", 3, 3.90,
     16.00, 8.00, 6.50, 140, 40, 300, "Active"),

    ("STA-NTB-A5", "A5 Lined Notebook", "Stationery", "Notebooks",
     "Softcover", "A5", "Sage", "Paper", "Each", 4, 3.10, 13.00,
     6.50, 5.40, 160, 48, 320, "Active"),
    ("STA-CRD-6PK", "Greeting Cards, Pack of 6", "Stationery",
     "Greeting cards", "Assorted", "A6", "Mixed", "Paper",
     "Pack of 6", 4, 2.70, 11.00, 5.50, 4.60, 95, 36, 240, "Active"),
    ("STA-PRN-A4", "Botanical Print Set A4", "Stationery",
     "Print sets", "Set of 3", "A4", "Mixed", "Paper", "Pack of 4",
     4, 4.20, 18.00, 9.00, 7.60, 93, 18, 120, "Active"),
    ("STA-STK-SHT", "Sticker Sheet", "Stationery", "Stickers",
     "Single", "A6", "Mixed", "Vinyl", "Each", 4, 0.70, 4.00, 2.00,
     1.60, 320, 100, 600, "Active"),

    ("BTH-SOP-OAT", "Oatmeal Soap Bar", "Bath & Body", "Soap bars",
     "Wrapped", "100g", "Cream", "Soap", "Each", 5, 2.30, 9.00,
     4.50, 3.80, 110, 40, 260, "Active"),
    ("BTH-SLT-LAV", "Lavender Bath Salts", "Bath & Body",
     "Bath salts", "Pouch", "500g", "Purple", "Mineral salt",
     "Each", 5, 3.40, 14.00, 7.00, 5.90, 65, 24, 180, "Active"),
    ("BTH-BLM-LIP", "Lip Balm Trio", "Bath & Body", "Balms",
     "Boxed", "3x10ml", "Mixed", "Beeswax", "Pack of 2", 5, 4.10,
     16.00, 8.00, 6.80, 12, 24, 140, "Active"),

    ("PKG-BOX-SML", "Kraft Gift Box, Small", "Packaging", "Boxes",
     "Flatpack", "12cm", "Kraft", "Card", "Pack of 10", 6, 0.42,
     0.00, 0.00, 0.00, 480, 200, 1200, "Active"),
    ("PKG-TIS-NAT", "Tissue Paper, Natural", "Packaging", "Tissue",
     "Sheet", "50x75cm", "Natural", "Paper", "Pack of 10", 6, 0.09,
     0.00, 0.00, 0.00, 1400, 500, 4000, "Active"),
    ("PKG-LBL-RND", "Round Branded Labels", "Packaging", "Labels",
     "Roll", "40mm", "Sage", "Paper", "Pack of 10", 6, 0.06, 0.00,
     0.00, 0.00, 220, 300, 2000, "Active"),
    ("PKG-MLR-MED", "Padded Mailer, Medium", "Packaging", "Mailers",
     "Padded", "C4", "Kraft", "Paper", "Pack of 10", 6, 0.38, 0.00,
     0.00, 0.00, 36, 150, 900, "Active"),

    ("CND-JAR-ROS", "Wild Rose Jar Candle", "Candles", "Jar candles",
     "Discontinued", "220ml", "Pink", "Soy wax", "Each", 1, 4.80,
     18.00, 9.00, 7.50, 9, 0, 0, "Discontinued"),
    ("TEX-SCF-WOL", "Lambswool Scarf", "Textiles", "Cushion covers",
     "Winter", "180cm", "Charcoal", "Wool", "Each", 3, 14.20, 52.00,
     26.00, 22.00, 18, 10, 60, "Seasonal"),
]


def _sku_at(index: int) -> str:
    return _CATALOGUE[index][0]


def _cost_at(index: int) -> float:
    return _CATALOGUE[index][10]


# ---------------------------------------------------------------------------
# 4. Product & SKU Database
# ---------------------------------------------------------------------------

_DESCRIPTIONS = {
    "CND-JAR-SAGE": "Hand poured, cotton wick, 45 hour burn. The one "
                    "everybody reorders.",
    "CER-MUG-350": "Thrown and glazed in house. Dishwasher safe. "
                   "Sold singly and in fours.",
    "CER-MUG-SEC": "Glaze pooling or a soft rim. Perfectly usable, "
                   "sold cheap, never to stockists.",
    "PKG-MLR-MED": "Despatch packaging. Not for sale - kept here so "
                   "its cost lands in the right place.",
    "CND-JAR-ROS": "Withdrawn after the fragrance house changed the "
                   "oil. Sell the remaining nine and let it go.",
}

_LAUNCH_OFFSETS = [-820, -640, -512, -790, -455, -288, -735, -700,
                   -410, -512, -366, -120, -690, -520, -300, -610,
                   -580, -540, -330, -250, -660, -470, -140, -900,
                   -900, -900, -900, -760, -210]


def products(cfg: Config) -> Rows:
    rows: Rows = []
    for i, item in enumerate(_CATALOGUE):
        (sku, name, cat, sub, variant, size, colour, material, unit,
         sup, cost, retail, wholesale, floor, opening, lo, hi,
         status) = item
        rows.append({
            "sku": sku,
            "name": name,
            "description": _DESCRIPTIONS.get(sku, ""),
            "category": cat,
            "subcategory": sub,
            "brand": "Thornfield",
            "variant": variant,
            "size": size,
            "colour": colour,
            "material": material,
            "barcode": f"50{12000 + i * 37:010d}"[:13],
            "unit": unit,
            "image": "",
            "supplier": _sup(sup),
            "supplier_sku": f"T-{sku.split('-')[-1]}{i:02d}",
            "cost": cost,
            "retail_price": retail,
            "wholesale_price": wholesale,
            "min_price": floor,
            "opening_qty": opening,
            "opening_value": round(opening * cost, 2),
            "min_stock": lo,
            "max_stock": hi,
            "reorder_point": "",
            "status": status,
            "launched": _day(cfg, _LAUNCH_OFFSETS[i]),
            "notes": "",
        })

    # the deliberate duplicate-SKU teaching moment lives in the
    # Stock Audit sheet instead - a duplicate here would corrupt
    # every other tab's sample numbers, which is exactly the point
    # the alert column is making.
    return rows


# ---------------------------------------------------------------------------
# 7. Supplier Database
# ---------------------------------------------------------------------------

#: (name, contact, type, city, country, terms, lead, rating, status,
#:  preferred, supplies, notes)
_SUPPLIERS = [
    ("Kestrel Wax & Wick", "Dan Mehta", "Wholesaler", "Portland",
     "United States", "Net 30", 7, 4, "Preferred", "Yes",
     "Soy wax, wicks, jars, lids, fragrance oils",
     "Reliable on the wax, slow on anything they have to order in. "
     "Lead time says seven days and the scorecard disagrees."),
    ("Ridgeway Ceramics", "Ana Sol", "Manufacturer", "Stoke",
     "United Kingdom", "Net 45", 35, 5, "Preferred", "Yes",
     "Stoneware blanks, glazes, firing",
     "Excellent quality, long lead time, worth planning around. "
     "Ship by sea, so never order in a hurry."),
    ("Fenwick Textiles", "Marta Oyelaran", "Importer", "Leicester",
     "United Kingdom", "Net 30", 21, 3, "Active", "No",
     "Linen, cotton canvas, finished tea towels",
     "Price went up twice this year without warning."),
    ("Marsh & Co Paper", "Theo Lindqvist", "Printer", "Seattle",
     "United States", "Net 14", 10, 4, "Active", "Yes",
     "Notebooks, cards, print sets, stickers", ""),
    ("Lavender Lane Botanics", "Priya Raman", "Maker / artisan",
     "Eugene", "United States", "Prepaid", 14, 4, "Active", "No",
     "Soap bases, bath salts, balms, essential oils", ""),
    ("Northgate Packaging", "Sam Okafor", "Packaging supplier",
     "Tacoma", "United States", "Net 30", 5, 3, "Active", "Yes",
     "Boxes, tissue, labels, mailers, tape",
     "Cheap and quick. Quality is adequate, not lovely."),
    ("Harbour Glass Supply", "Lena Vogt", "Distributor", "Bristol",
     "United Kingdom", "Net 30", 28, 2, "On hold", "No",
     "Glass jars and bottles",
     "Two short deliveries and a damaged pallet. On hold until "
     "they explain themselves."),
    ("Beacon Trade Goods", "Owen Pryce", "Wholesaler", "Denver",
     "United States", "Net 30", 12, 3, "Trial", "No",
     "Mixed homeware for resale", "First order placed, nothing "
     "received yet."),
]


def suppliers(cfg: Config) -> Rows:
    rows: Rows = []
    for i, (name, contact, kind, city, country, terms, lead, rating,
            status, preferred, supplies, note) in enumerate(
                _SUPPLIERS, start=1):
        handle = name.lower().replace(" & ", "").replace(" ", "")[:16]
        rows.append({
            "name": name,
            "contact": contact,
            "email": f"{contact.split()[0].lower()}@{handle}.example",
            "phone": f"(503) 555-0{100 + i * 7:03d}",
            "website": f"{handle}.example",
            "address": f"{i * 13} Trade Street",
            "city": city,
            "country": country,
            "type": kind,
            "supplies": supplies,
            "terms": terms,
            "currency": "GBP" if country == "United Kingdom"
                        else "USD",
            "lead_time": lead,
            "moq": [250, 500, 300, 150, 120, 200, 400, 250][i - 1],
            "free_ship_over": [500, 1500, 800, 400, 0, 350, 0,
                               600][i - 1],
            "discount": [0.05, 0.0, 0.0, 0.03, 0.0, 0.08, 0.0,
                         0.0][i - 1],
            "account_no": f"TH-{4100 + i * 17}",
            "tax_id": "",
            "status": status,
            "preferred": preferred,
            "rating": rating,
            "first_order": _day(cfg, -[700, 640, 520, 480, 400, 610,
                                       300, 24][i - 1]),
            "notes": note,
        })
    return rows


# ---------------------------------------------------------------------------
# 8. Purchase Orders
# ---------------------------------------------------------------------------
# Deliberate teaching cases in here:
#   PO-0007 - sent weeks ago, nothing received, and it is the SKU
#             that is out of stock. The chase list exists for this.
#   PO-0009 - part delivery: 30 of 50 arrived, 20 still outstanding.
#   PO-0011 - invoice disagrees with the order value.
#   PO-0012 - received more than was ordered.
#   PO-0013 - still a draft, dated, never sent.

#: (po, supplier_n, days_ago, lead, [(sku_index, qty, cost, freight,
#:  received)], status, condition, invoice_gap, paid)
_PO_PLAN = [
    ("PO-0001", 1, -96, 7,
     [(0, 240, 4.60, 38.00, 240), (1, 120, 4.60, 19.00, 120),
      (2, 120, 4.60, 19.00, 120)],
     "Fully Received", "Good", 0.0, "Yes"),
    ("PO-0002", 2, -88, 35,
     [(6, 144, 5.90, 120.00, 144), (7, 96, 5.20, 80.00, 96),
      (9, 72, 7.00, 60.00, 72)],
     "Fully Received", "Good", 0.0, "Yes"),
    ("PO-0003", 4, -74, 10,
     [(16, 200, 3.00, 24.00, 200), (17, 120, 2.60, 15.00, 120),
      (19, 400, 0.66, 18.00, 400)],
     "Fully Received", "Good", 0.0, "Yes"),
    ("PO-0004", 6, -66, 5,
     [(23, 600, 0.40, 22.00, 600), (24, 1600, 0.085, 14.00, 1600),
      (26, 300, 0.36, 12.00, 300)],
     "Fully Received", "Good", 0.0, "Yes"),
    ("PO-0005", 3, -58, 21,
     [(12, 96, 5.40, 72.00, 96), (13, 48, 8.00, 44.00, 48),
      (15, 180, 3.75, 54.00, 180)],
     "Fully Received", "Minor damage", 0.0, "Yes"),
    ("PO-0006", 5, -44, 14,
     [(20, 144, 2.20, 26.00, 144), (21, 72, 3.30, 18.00, 72)],
     "Fully Received", "Good", 0.0, "Yes"),
    ("PO-0007", 1, -31, 7,
     [(1, 180, 4.80, 30.00, 0), (11, 96, 4.40, 22.00, 0)],
     "Sent", "", 0.0, ""),
    ("PO-0008", 2, -26, 35,
     [(6, 120, 6.10, 110.00, 0), (10, 60, 5.90, 55.00, 0)],
     "Confirmed", "", 0.0, ""),
    ("PO-0009", 4, -22, 10,
     [(18, 50, 4.10, 16.00, 30), (16, 150, 3.10, 20.00, 150)],
     "Partially Received", "Short delivery", 0.0, "No"),
    ("PO-0010", 6, -16, 5,
     [(27, 500, 0.37, 18.00, 500), (25, 800, 0.058, 9.00, 800)],
     "Fully Received", "Good", 0.0, "No"),
    ("PO-0011", 3, -14, 21,
     [(14, 36, 11.90, 40.00, 36), (12, 72, 5.90, 48.00, 72)],
     "Fully Received", "Good", 86.40, "No"),
    ("PO-0012", 5, -11, 14,
     [(22, 60, 4.10, 16.00, 72)],
     "Fully Received", "Over delivery", 0.0, "No"),
    ("PO-0013", 8, -6, 12,
     [(3, 150, 3.10, 28.00, 0), (4, 90, 2.35, 14.00, 0)],
     "Draft", "", 0.0, ""),
    ("PO-0014", 1, -4, 7,
     [(5, 180, 1.55, 20.00, 0)],
     "Confirmed", "", 0.0, ""),
    ("PO-0015", 6, -2, 5,
     [(23, 400, 0.41, 18.00, 0)],
     "Sent", "", 0.0, ""),
]


def purchases(cfg: Config) -> Rows:
    rows: Rows = []
    checkers = ["Owner", "Warehouse", "Packer", "Assistant"]
    for index, (po, sup, ago, lead, lines, status, condition,
                gap, paid) in enumerate(_PO_PLAN):
        ordered = _day(cfg, ago)
        # the lead time that actually happened, not the promised one
        slip = {1: 6, 2: 3, 3: 9, 4: 1, 5: 2, 6: 0, 7: 0,
                8: 0}.get(sup, 0)
        expected = _day(cfg, ago + lead)
        received_on = _day(cfg, ago + lead + slip)
        got_anything = any(line[4] > 0 for line in lines)
        for pos, (sku_i, qty, cost, freight, received) in enumerate(
                lines):
            row = {
                "po_id": po,
                "supplier": _sup(sup),
                "order_date": ordered if status != "Draft" else "",
                "expected": expected,
                "sku": _sku_at(sku_i),
                "qty": qty,
                "unit_cost": cost,
                "discount": 0.0,
                "freight": freight,
                "received": received,
                "status": status,
                "notes": "",
            }
            if received > 0:
                row["received_date"] = received_on
                row["received_by"] = checkers[(index + pos) % 4]
                row["condition"] = condition or "Good"
            if got_anything and pos == 0:
                row["invoice_no"] = f"INV-{9100 + index * 13}"
                total = sum(q * c + f
                            for _s, q, c, f, _r in lines)
                row["invoice_amount"] = round(total + gap, 2)
                row["paid"] = paid or "No"
            if status == "Draft":
                row["notes"] = ("Drafted after the last stock count "
                                "and never sent. This is what the "
                                "'Send -' alert is for.")
            if po == "PO-0009" and pos == 0:
                row["notes"] = ("Thirty of fifty arrived. The line "
                                "stays open and twenty are still "
                                "counted as on order.")
            if po == "PO-0012":
                row["notes"] = ("Twelve more arrived than were "
                                "ordered. Check before you pay for "
                                "them.")
            if po == "PO-0011" and pos == 0:
                row["notes"] = ("Invoice is higher than the order. "
                                "Price went up and nobody told us.")
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 9. Wholesale Customer CRM
# ---------------------------------------------------------------------------

#: (business, buyer, type, city, tier, terms, limit, min, status,
#:  rating, source, extra discount, notes)
_CUSTOMERS = [
    ("Marlowe & Hart", "Freya Marlowe", "Independent boutique",
     "Portland", "Wholesale", "Net 30", 4000, 250, "Active", 5,
     "Trade show", 0.0,
     "Best account by a distance. Reorders candles monthly without "
     "being asked."),
    ("The Fern Room", "Jonah Beck", "Gift shop", "Seattle",
     "Wholesale", "Net 30", 2500, 200, "Active", 4, "Instagram",
     0.0, ""),
    ("Alder & Oak Living", "Nadia Qureshi", "Garden centre",
     "Eugene", "Trade", "Net 14", 1500, 150, "Active", 4,
     "Referral", 0.0, "Seasonal - heavy in spring, quiet in "
     "winter."),
    ("Coastline Home", "Greg Alvarez", "Online retailer",
     "San Diego", "Distributor", "Net 45", 8000, 600, "Active", 3,
     "Faire or marketplace", 0.02,
     "Biggest volume, thinnest margin. Watch the GP% column before "
     "agreeing to anything else."),
    ("Bramble Cafe", "Ivy Donnelly", "Cafe or restaurant",
     "Portland", "Trade", "Net 14", 800, 100, "Active", 4,
     "Walk-in", 0.0, "Buys mugs and tea towels only."),
    ("Pinewood Museum Shop", "Hal Osei", "Museum shop", "Tacoma",
     "Wholesale", "Net 30", 2000, 200, "Occasional", 4,
     "Cold outreach", 0.0, ""),
    ("Sundry Goods Co.", "Remi Takahashi", "Marketplace seller",
     "Boise", "Trade", "Prepaid", 0, 150, "Active", 3,
     "Website enquiry", 0.0, "Prepay only - they were late twice "
     "and we moved them."),
    ("Harbourview Hotel", "Claire Dunne", "Hotel or B&B",
     "Astoria", "Wholesale", "Net 30", 3000, 300, "Active", 4,
     "Referral", 0.05,
     "Overdue. Lovely people, terrible at paying on time."),
    ("Juniper Box", "Teo Ferreira", "Subscription box", "Denver",
     "Distributor", "Net 30", 6000, 500, "Lapsed", 3,
     "Trade show", 0.0,
     "Ordered twice last year and went quiet. Worth a call."),
    ("Greenhill Interiors", "Suki Lam", "Independent boutique",
     "Vancouver", "Wholesale", "Net 30", 2500, 200, "Prospect", 3,
     "Trade show", 0.0, "Samples sent, no order yet."),
    ("Westbrook Stores", "Martin Ayers", "Department store",
     "Chicago", "Key account", "Net 60", 12000, 1500, "On hold", 2,
     "Sales agent", 0.0,
     "On hold. Wanted 38% of retail and sixty day terms, which "
     "does not work at our costs."),
]


def customers(cfg: Config) -> Rows:
    rows: Rows = []
    first_order_ago = [-430, -380, -300, -250, -210, -180, -150,
                       -340, -400, 0, -120]
    for i, (business, buyer, kind, city, tier, terms, limit, minimum,
            status, rating, source, extra, note) in enumerate(
                _CUSTOMERS):
        handle = business.lower().replace(" & ", "").replace(
            " ", "").replace(".", "")[:18]
        row = {
            "business": business,
            "contact": buyer,
            "email": f"{buyer.split()[0].lower()}@{handle}.example",
            "phone": f"(206) 555-0{200 + i * 9:03d}",
            "website": f"{handle}.example",
            "address": f"{12 + i * 7} High Street",
            "city": city,
            "region": "Oregon" if city in ("Portland", "Eugene",
                                           "Astoria") else "",
            "postcode": f"9{7000 + i * 31:04d}",
            "country": "Canada" if city == "Vancouver"
                       else "United States",
            "type": kind,
            "tier": tier,
            "terms": terms,
            "credit_limit": limit,
            "min_order": minimum,
            "discount": extra,
            "tax_exempt": "Yes" if tier in ("Wholesale",
                                            "Distributor",
                                            "Key account") else "No",
            "resale_no": f"RS-{20450 + i * 13}" if tier != "Trade"
                         else "",
            "shipping_pref": "Courier" if i % 3 else "Pallet",
            "status": status,
            "rating": rating,
            "source": source,
            "notes": note,
        }
        if first_order_ago[i]:
            row["first_order"] = _day(cfg, first_order_ago[i])
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 10. Wholesale Pricing
# ---------------------------------------------------------------------------


def pricing(cfg: Config) -> Rows:
    """Mirrors the catalogue - the sheet generates its own SKU column.

    Two teaching cases: the seconds mugs are priced below their own
    floor at the deepest break, and the lambswool scarf has not been
    reviewed since the wool price moved.
    """
    rows: Rows = []
    for i, item in enumerate(_CATALOGUE):
        sku = item[0]
        wholesale = item[12]
        floor = item[13]
        trade = "No" if sku.startswith("PKG-") else "Yes"
        if wholesale <= 0:
            rows.append({
                "wholesale": "", "tier1_qty": "", "tier1_price": "",
                "tier2_qty": "", "tier2_price": "", "tier3_qty": "",
                "tier3_price": "", "moq": "", "case_qty": 10,
                "available_trade": "No",
                "notes": "Packaging - not sold to trade.",
            })
            continue
        t1 = round(wholesale * 0.94, 2)
        t2 = round(wholesale * 0.88, 2)
        t3 = round(wholesale * 0.82, 2)
        note = ""
        if sku == "CER-MUG-SEC":
            t3 = round(floor - 0.60, 2)
            note = ("The hundred-plus price slipped below the floor "
                    "price when the glaze cost went up. This is what "
                    "the red alert is for.")
        if sku == "TEX-SCF-WOL":
            note = ("Wool went up 20% in the spring and this price "
                    "has not been looked at since.")
        rows.append({
            "wholesale": wholesale,
            "tier1_qty": 10, "tier1_price": t1,
            "tier2_qty": 50, "tier2_price": t2,
            "tier3_qty": 100, "tier3_price": t3,
            "moq": 6 if i % 3 else 12,
            "case_qty": [6, 12, 4, 24][i % 4],
            "available_trade": trade,
            "reviewed": _day(cfg, -(40 + (i * 23) % 300))
                        if sku != "TEX-SCF-WOL"
                        else _day(cfg, -430),
            "notes": note,
        })
    return rows


# ---------------------------------------------------------------------------
# 11. Wholesale Orders
# ---------------------------------------------------------------------------
# Teaching cases:
#   WO-0009 - confirmed three weeks ago, never picked, ninety units
#             reserved the whole time.
#   WO-0012 - confirmed for more units than are available.
#   WO-0006 - shipped, invoiced, overdue, and the customer is the
#             hotel with the reputation for paying late.

#: (order, customer_n, days_ago, [(sku_index, qty)], status,
#:  ship_offset, paid_share, discount)
_ORDER_PLAN = [
    ("WO-0001", 1, -78, [(0, 48), (2, 36), (6, 24)], "Delivered",
     3, 1.0, 0.0),
    ("WO-0002", 2, -70, [(16, 60), (17, 48), (19, 120)], "Delivered",
     2, 1.0, 0.0),
    ("WO-0003", 4, -63, [(0, 120), (3, 96), (12, 72)], "Delivered",
     4, 1.0, 0.0),
    ("WO-0004", 3, -54, [(10, 24), (11, 18), (9, 24)], "Delivered",
     3, 1.0, 0.0),
    ("WO-0005", 5, -45, [(6, 36), (12, 24)], "Delivered", 2, 1.0,
     0.0),
    ("WO-0006", 8, -38, [(0, 60), (20, 48), (21, 36)], "Delivered",
     3, 0.0, 0.0),
    ("WO-0007", 1, -29, [(0, 72), (2, 48), (5, 60)], "Delivered",
     2, 1.0, 0.0),
    ("WO-0008", 6, -24, [(16, 48), (18, 36)], "Shipped", 4, 0.5,
     0.0),
    ("WO-0009", 4, -21, [(0, 60), (6, 30)], "Confirmed", None, 0.0,
     0.0),
    ("WO-0010", 2, -12, [(13, 18), (15, 36)], "Packed", None, 0.0,
     0.0),
    # the order that cleared the bud vase shelf - and the reason
    # PO-0007 sitting unsent is the most expensive row in the book
    ("WO-0011", 4, -12, [(11, 52), (16, 72)], "Delivered", 3, 1.0,
     0.0),
    ("WO-0012", 7, -8, [(19, 96), (17, 36)], "Shipped", 2, 1.0,
     0.0),
    ("WO-0013", 1, -5, [(1, 90), (11, 48)], "Confirmed", None, 0.0,
     0.0),
    ("WO-0014", 5, -3, [(6, 24), (7, 24)], "Processing", None, 0.0,
     0.0),
    ("WO-0015", 3, -2, [(10, 30), (22, 24)], "New", None, 0.0, 0.0),
    ("WO-0016", 2, -1, [(0, 36), (16, 48), (23, 200)], "Confirmed",
     None, 0.0, 0.05),
]


def orders(cfg: Config) -> Rows:
    rows: Rows = []
    methods = ["Courier", "Pallet", "Tracked post", "Own delivery"]
    for index, (order, cust, ago, lines, status, ship_off, paid,
                discount) in enumerate(_ORDER_PLAN):
        placed = _day(cfg, ago)
        shipped = _day(cfg, ago + ship_off) if ship_off is not None \
            else ""
        invoiced = status in ("Shipped", "Delivered")
        for pos, (sku_i, qty) in enumerate(lines):
            item = _CATALOGUE[sku_i]
            row = {
                "order_id": order,
                "date": placed,
                "customer": _cust(cust),
                "po_ref": f"PO{4400 + index * 7}",
                "sku": item[0],
                "qty": qty,
                "line_discount": discount if pos == 0 else 0.0,
                "status": status,
                "notes": "",
            }
            if shipped:
                row["ship_date"] = shipped
                row["ship_method"] = methods[index % 4]
                row["tracking"] = f"TRK{7200100 + index * 431}"
            if invoiced:
                row["invoice_no"] = f"INV-{5200 + index * 11}"
                if pos == 0:
                    row["shipping_charge"] = 0.0 if qty > 80 else 14.50
                if paid > 0:
                    unit = round(item[12] * 0.9, 2)
                    row["paid_amount"] = round(qty * unit * paid, 2)
            if order == "WO-0009":
                row["notes"] = ("Confirmed three weeks ago and never "
                                "picked. Those units have been "
                                "reserved - unavailable to anyone "
                                "else - the whole time.")
            if order == "WO-0013" and pos == 0:
                row["notes"] = ("More than we have. The Short by "
                                "column says exactly how many we "
                                "cannot pick.")
            if order == "WO-0006" and pos == 0:
                row["notes"] = "Invoiced, delivered, still not paid."
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 12. Retail Sales Tracker
# ---------------------------------------------------------------------------


def _stock_timeline(cfg: Config) -> Dict[str, Dict[int, int]]:
    """Inbound and outbound units per SKU per day, retail aside.

    The retail generator below has to know what was actually on the
    shelf on the day it wants to sell something. Without this it
    cheerfully sells forty vases that were never bought, the stock
    tracker shows a negative balance, and the first thing a buyer
    sees in the example data is a number that cannot happen.
    """
    moves: Dict[str, Dict[int, int]] = {}

    def add(sku: str, day: int, qty: int) -> None:
        moves.setdefault(sku, {})
        moves[sku][day] = moves[sku].get(day, 0) + qty

    # opening stock, treated as present from before the window
    for item in _CATALOGUE:
        add(item[0], -9999, item[14])
    # deliveries land on the day they were received
    for index, (_po, _sup, ago, lead, lines, status, _cond, _gap,
                _paid) in enumerate(_PO_PLAN):
        slip = {1: 6, 2: 3, 3: 9, 4: 1, 5: 2, 6: 0, 7: 0,
                8: 0}.get(_sup, 0)
        for sku_i, _qty, _cost, _freight, received in lines:
            if received > 0:
                add(_sku_at(sku_i), ago + lead + slip, received)
    # wholesale orders take stock out when they ship, and reserve it
    # from the day they are confirmed
    for _order, _cust, ago, lines, status, ship_off, _paid, _disc in \
            _ORDER_PLAN:
        for sku_i, qty in lines:
            if status in ("Shipped", "Delivered"):
                add(_sku_at(sku_i), ago + (ship_off or 0), -qty)
            elif status in ("Confirmed", "Processing", "Picking",
                            "Packed"):
                add(_sku_at(sku_i), ago, -qty)      # reserved
    # damage, samples, production use, transfers and corrections
    signs = {name: sign for name, sign, _blurb in MOVEMENT_TYPES}
    for ago, sku_i, kind, qty, *_rest in _MOVEMENTS:
        sign = signs.get(kind, 0)
        if kind == "Adjustment":
            add(_sku_at(sku_i), ago, qty)
        else:
            add(_sku_at(sku_i), ago, sign * qty)
    # returns that went back on the shelf
    for (ago, _src, _ref, _who, sku_i, qty, _reason, condition,
         *_rest) in _RETURNS:
        if condition in ("As new", "Opened - resellable"):
            add(_sku_at(sku_i), ago, qty)
    return moves


def retail(cfg: Config) -> Rows:
    """Four months of marketplace and market-stall trade.

    Generated rather than hand written, because the point of this
    sheet is volume: ninety-day averages, channel splits and run
    rates only mean something when there is a run of real-looking
    days behind them.

    The generator will not sell stock that was not there on the day.
    It walks the window forwards carrying a running balance per SKU,
    and skips a sale it cannot cover - which is what produces the
    nine-day stockout on the bud vase rather than a negative number.
    """
    rows: Rows = []
    channels = ["Etsy", "Etsy", "Etsy", "Shopify", "Shopify",
                "Amazon", "eBay", "Physical Store", "Craft Fair",
                "Direct Sales"]
    sellable = [i for i, item in enumerate(_CATALOGUE)
                if item[12] > 0 and item[17] in ("Active",
                                                 "Clearance",
                                                 "Seasonal")]
    timeline = _stock_timeline(cfg)
    balance = {item[0]: 0 for item in _CATALOGUE}
    for sku, days in timeline.items():
        balance[sku] += sum(q for day, q in days.items() if day < -118)

    seed = 7
    counter = 0
    for day_offset in range(-118, 1):
        for sku, days in timeline.items():
            balance[sku] += days.get(day_offset, 0)
        seed = (seed * 1103515245 + 12345) % 2147483648
        # busier at weekends, quieter in the middle of the week
        weekday = (cfg.today + _dt.timedelta(days=day_offset)).weekday()
        base = 4 if weekday >= 5 else 2
        count = base + seed % 3
        for _ in range(count):
            seed = (seed * 1103515245 + 12345) % 2147483648
            sku_i = sellable[seed % len(sellable)]
            item = _CATALOGUE[sku_i]
            seed = (seed * 1103515245 + 12345) % 2147483648
            channel = channels[seed % len(channels)]
            qty = 1 + (seed // 7) % 3
            if balance.get(item[0], 0) < qty:
                continue            # it was not on the shelf that day
            balance[item[0]] -= qty
            counter += 1
            retail_price = item[11]
            discounted = (counter % 23 == 0)
            price = (round(retail_price * 0.75, 2) if discounted
                     else retail_price)
            heavy = item[8] in ("Box of 24", "Case of 48")
            ship_charged = 0.0 if channel in ("Physical Store",
                                              "Craft Fair",
                                              "Direct Sales") \
                else (0.0 if qty >= 3 else 4.95)
            ship_cost = 0.0 if channel in ("Physical Store",
                                           "Craft Fair") \
                else round((7.80 if heavy else 4.20) +
                           (1.60 if qty > 2 else 0.0), 2)
            row = {
                "sale_id": f"SO-{1000 + counter:04d}",
                "date": _day(cfg, day_offset),
                "channel": channel,
                "sku": item[0],
                "qty": qty,
                "unit_price": price,
                "shipping_charged": ship_charged,
                "shipping_cost": ship_cost,
                "discount": 0.0,
                "status": ("Delivered" if day_offset < -6
                           else "Shipped" if day_offset < -1
                           else "Paid"),
                "customer": f"buyer{(counter * 37) % 900:03d}",
                "location": "Main store",
                "notes": "",
            }
            if channel in ("Physical Store", "Craft Fair"):
                row["status"] = "Collected"
                row["location"] = ("Shop floor"
                                   if channel == "Physical Store"
                                   else "Market stall")
            if counter % 47 == 0:
                row["status"] = "Refunded"
                balance[item[0]] += qty      # it came back
            if counter % 31 == 0:
                row["fee_override"] = round(
                    price * qty * 0.11 + 0.25, 2)
                row["notes"] = ("Real fee from the platform "
                                "statement, which beats the "
                                "estimate.")
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 6. Stock Movement Log
# ---------------------------------------------------------------------------
# Only the things that are NOT purchases, sales or returns: damage,
# loss, samples, production use, transfers and corrections.

_MOVEMENTS = [
    (-104, 6, "Damaged", 4, "Box crushed in transit from Ridgeway. "
     "Claimed and credited.", "PO-0002", "Main store", "Warehouse"),
    (-96, 0, "Sample or gift", 6, "Sent to three prospective "
     "stockists after the Portland trade show.", "", "Main store",
     "Owner"),
    (-88, 23, "Used in production", 120, "Gift boxes used packing "
     "the autumn wholesale orders.", "", "Workshop", "Packer"),
    (-81, 12, "Damaged", 3, "Water damage on the bottom shelf after "
     "the gutter overflowed.", "", "Overflow unit", "Warehouse"),
    (-74, 16, "Found in count", 8, "Found a sealed box behind the "
     "printer stock during the quarterly count.", "AUD-0002",
     "Main store", "Warehouse"),
    (-66, 3, "Transfer out", 40, "Moved to the market stall for the "
     "harvest fair.", "", "Main store", "Assistant"),
    (-66, 3, "Transfer in", 40, "Arrived at the market stall.", "",
     "Market stall", "Assistant"),
    (-61, 19, "Damaged", 22, "Sticker sheets curled in the damp. "
     "Unsellable.", "", "Workshop", "Owner"),
    (-54, 24, "Used in production", 400, "Tissue paper used across "
     "the September despatches.", "", "Workshop", "Packer"),
    (-48, 8, "Adjustment", -5, "Count found five fewer seconds mugs "
     "than the system believed. Most likely sold at the market "
     "stall without being logged.", "AUD-0004", "Main store",
     "Owner"),
    (-41, 20, "Sample or gift", 12, "Soap bars into the gift bags "
     "for the makers' market.", "", "Main store", "Assistant"),
    (-36, 9, "Damaged", 2, "Dropped while restocking the shop "
     "floor.", "", "Shop floor", "Packer"),
    (-29, 26, "Used in production", 180, "Labels used on the "
     "autumn candle run.", "", "Workshop", "Packer"),
    (-24, 0, "Damaged", 3, "Three jars cracked - the wax was poured "
     "too hot.", "", "Workshop", "Owner"),
    (-19, 13, "Lost or stolen", 2, "Two cushion covers missing from "
     "the market stall. No paperwork, no explanation.", "",
     "Market stall", "Assistant"),
    (-16, 2, "Supplier return", 12, "Twelve linen candles returned "
     "to Kestrel - the fragrance was wrong.", "SUP-001",
     "Main store", "Owner"),
    (-12, 7, "Adjustment", -11, "Stocktake found eleven fewer 250ml "
     "mugs. Reason not established. Posted so the system and the "
     "shelf agree again.", "AUD-0007", "Main store", "Owner"),
    (-9, 21, "Damaged", 4, "Bath salt pouches split on the shelf.",
     "", "Main store", "Warehouse"),
    (-6, 18, "Sample or gift", 8, "Print sets sent to a magazine "
     "for a feature.", "", "Main store", "Owner"),
    (-4, 23, "Used in production", 90, "Gift boxes for the "
     "Marlowe & Hart order.", "WO-0015", "Workshop", "Packer"),
    (-2, 4, "Found in count", 6, "Six boxes of tealights found in "
     "the overflow unit.", "AUD-0009", "Overflow unit",
     "Warehouse"),
    (-1, 10, "Damaged", 1, "One planter chipped unloading the "
     "pallet.", "", "Main store", "Warehouse"),
]


def movements(cfg: Config) -> Rows:
    rows: Rows = []
    for ago, sku_i, kind, qty, reason, ref, location, who in \
            _MOVEMENTS:
        row = {
            "date": _day(cfg, ago),
            "sku": _sku_at(sku_i),
            "type": kind,
            "qty": qty,
            "reason": reason,
            "reference": ref,
            "location": location,
            "recorded_by": who,
        }
        if kind == "Transfer out":
            row["to_location"] = "Market stall"
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 15. Returns & Damaged Goods
# ---------------------------------------------------------------------------

_RETURNS = [
    (-92, "Retail customer", "SO-1041", "buyer214", 6, 1,
     "Damaged in transit", "Damaged - not sellable", 18.00, "No",
     0.0, "Yes", "Yes", 6.10,
     "Mug arrived in three pieces. Supplier packed it badly; they "
     "credited us."),
    (-84, "Retail customer", "SO-1063", "buyer377", 0, 1,
     "Customer changed mind", "As new", 18.00, "No", 3.95, "No",
     "No", 0.0, "Back on the shelf, no harm done."),
    (-71, "Wholesale customer", "WO-0002", "The Fern Room", 17, 12,
     "Not as described", "Opened - resellable", 0.0, "Yes", 0.0,
     "No", "No", 0.0,
     "Card designs were not what they expected. Replaced with a "
     "different assortment; these went back into stock."),
    (-58, "Courier damage", "SO-1092", "buyer481", 9, 2,
     "Damaged in transit", "Destroyed", 52.00, "No", 0.0, "No", "No",
     0.0, "Claim with the courier, not the supplier."),
    (-44, "Retail customer", "SO-1130", "buyer092", 13, 1,
     "Incorrect size", "As new", 32.00, "No", 4.20, "No", "No",
     0.0, ""),
    (-37, "Wholesale customer", "WO-0004", "Alder & Oak Living", 11,
     6, "Defective", "Faulty - return to supplier", 0.0, "Yes",
     0.0, "Yes", "Yes", 26.40,
     "Glaze crazing on all six. Ridgeway replaced them."),
    (-29, "Retail customer", "SO-1178", "buyer655", 22, 1,
     "Defective", "Damaged - not sellable", 16.00, "Yes", 0.0,
     "Yes", "No", 0.0,
     "Balm had separated. Supplier's fault and we have still not "
     "claimed for it."),
    (-21, "Marketplace", "SO-1204", "buyer318", 0, 2,
     "Customer changed mind", "Opened - resellable", 36.00, "No",
     5.60, "No", "No", 0.0, ""),
    (-14, "Retail customer", "SO-1241", "buyer730", 20, 3,
     "Wrong item sent", "As new", 27.00, "Yes", 4.20, "No", "No",
     0.0, "Our picking error. Replacement sent same day."),
    (-8, "Own warehouse", "", "", 1, 4, "Damaged in transit",
     "Destroyed", 0.0, "No", 0.0, "Yes", "No", 0.0,
     "Found broken in the box from Kestrel. Their fault, not "
     "claimed yet."),
    (-3, "Wholesale customer", "WO-0011", "Sundry Goods Co.", 19, 24,
     "Not as described", "Opened - resellable", 0.0, "No", 0.0,
     "No", "No", 0.0, "Restocked, no refund - they took a credit "
     "against the next order."),
]


def returns(cfg: Config) -> Rows:
    rows: Rows = []
    for (ago, source, ref, who, sku_i, qty, reason, condition,
         refund, replacement, postage, fault, claimed, credit,
         note) in _RETURNS:
        rows.append({
            "date": _day(cfg, ago),
            "source": source,
            "reference": ref,
            "customer": who,
            "sku": _sku_at(sku_i),
            "qty": qty,
            "reason": reason,
            "condition": condition,
            "location": "Main store" if "resellable" in condition
                        or condition == "As new" else "",
            "refund": refund,
            "replacement": replacement,
            "return_shipping": postage,
            "supplier_fault": fault,
            "claimed": claimed,
            "credit_received": credit,
            "status": "Closed" if ago < -30 else
                      ("Claim raised" if claimed == "Yes"
                       else "Logged"),
            "notes": note,
        })
    return rows


# ---------------------------------------------------------------------------
# 16. Warehouse Locations
# ---------------------------------------------------------------------------

_ZONES = {
    "Main store": ("Zone A", "Shelf"),
    "Workshop": ("Zone B", "Bin"),
    "Overflow unit": ("Zone C", "Pallet"),
    "Shop floor": ("Front", "Shelf"),
    "Market stall": ("Mobile", "Bin"),
}

#: sku index -> [(location, share of stock, primary, capacity)]
_LOCATION_PLAN = {
    0: [("Main store", 0.7, "Yes", 400), ("Shop floor", 0.2, "No", 60),
        ("Market stall", 0.1, "No", 48)],
    2: [("Main store", 0.8, "Yes", 400), ("Shop floor", 0.2, "No", 60)],
    3: [("Main store", 0.6, "Yes", 300),
        ("Overflow unit", 0.4, "No", 600)],
    5: [("Main store", 1.0, "Yes", 300)],
    6: [("Main store", 0.75, "Yes", 240), ("Shop floor", 0.25, "No", 48)],
    7: [("Main store", 1.0, "Yes", 240)],
    9: [("Main store", 0.65, "Yes", 200), ("Shop floor", 0.35, "No", 40)],
    10: [("Overflow unit", 1.0, "Yes", 300)],
    12: [("Main store", 0.7, "Yes", 200), ("Market stall", 0.3, "No", 36)],
    13: [("Main store", 1.0, "Yes", 150)],
    15: [("Main store", 0.8, "Yes", 400), ("Shop floor", 0.2, "No", 60)],
    16: [("Main store", 0.6, "Yes", 500),
         ("Overflow unit", 0.4, "No", 800)],
    17: [("Main store", 1.0, "Yes", 400)],
    19: [("Main store", 1.0, "Yes", 900)],
    20: [("Main store", 0.7, "Yes", 300), ("Shop floor", 0.3, "No", 48)],
    21: [("Main store", 1.0, "Yes", 240)],
    23: [("Workshop", 0.8, "Yes", 1200),
         ("Overflow unit", 0.2, "No", 1500)],
    24: [("Workshop", 1.0, "Yes", 3000)],
    25: [("Workshop", 1.0, "Yes", 2000)],
    26: [("Workshop", 1.0, "Yes", 900)],
    27: [("Workshop", 0.6, "Yes", 700),
         ("Overflow unit", 0.4, "No", 900)],
}


def locations(cfg: Config) -> Rows:
    rows: Rows = []
    bins = {}
    for sku_i in sorted(_LOCATION_PLAN):
        item = _CATALOGUE[sku_i]
        opening = item[14]
        plan = _LOCATION_PLAN[sku_i]
        placed = 0
        for pos, (where, share, primary, capacity) in enumerate(plan):
            zone, kind = _ZONES[where]
            count = bins.get(where, 0) + 1
            bins[where] = count
            qty = (opening - placed if pos == len(plan) - 1
                   else int(opening * share))
            placed += qty
            note = ""
            if where == "Overflow unit":
                note = ("Off-site. Allow an extra day when picking "
                        "from here.")
            rows.append({
                "sku": item[0],
                "location": where,
                "zone": zone,
                "bin": f"{zone.split()[-1][0].upper()}"
                       f"{count:02d}-{pos + 1}",
                "qty_here": max(qty, 0),
                "is_primary": primary,
                "capacity": capacity,
                "type": kind,
                "checked": _day(cfg, -(7 + (sku_i * 11) % 90)),
                "notes": note,
            })
    return rows


# ---------------------------------------------------------------------------
# 17. Stock Audit
# ---------------------------------------------------------------------------
# A count never overwrites stock. It produces a variance, and the
# user posts an adjustment on the Movement Log. The unposted ones
# are what the dashboard counts.

#: (days ago, type, sku index, location, counter, counted, reason,
#:  recount, posted, movement ref, status)
_AUDITS = [
    (-104, "Full stocktake", 0, "Main store", "Owner", None, "", "No",
     "Yes", "", "Closed", ""),
    (-104, "Full stocktake", 6, "Main store", "Owner", None, "", "No",
     "Yes", "", "Closed", ""),
    (-74, "Cycle count", 16, "Main store", "Warehouse", 8,
     "Found elsewhere", "Yes", "Yes", "MOV-0005", "Closed",
     "A sealed box had been shelved behind the printer stock."),
    (-61, "Spot check", 12, "Overflow unit", "Warehouse", None, "",
     "No", "Yes", "", "Closed", ""),
    (-48, "Cycle count", 8, "Main store", "Owner", -5,
     "Sale not recorded", "Yes", "Yes", "MOV-0010", "Closed",
     "Five seconds mugs short. Most likely sold at the market "
     "stall without being logged."),
    (-33, "Cycle count", 19, "Main store", "Packer", None, "", "No",
     "Yes", "", "Closed", ""),
    (-26, "Spot check", 23, "Workshop", "Packer", None, "", "No",
     "Yes", "", "Closed", ""),
    (-12, "Cycle count", 7, "Main store", "Owner", -11, "Unknown",
     "Yes", "Yes", "MOV-0017", "Closed",
     "Eleven 250ml mugs short and no explanation found. Posted as "
     "an adjustment so the shelf and the system agree again."),
    (-9, "Cycle count", 20, "Main store", "Assistant", None, "",
     "No", "Yes", "", "Closed", ""),
    (-5, "Cycle count", 2, "Main store", "Warehouse", -3, "Unknown",
     "Yes", "No", "", "Investigating",
     "Three short. The recount agreed with the first count, so the "
     "stock genuinely is not there. Still not posted."),
    (-4, "Spot check", 13, "Main store", "Assistant", 2,
     "Receipt not recorded", "No", "No", "", "Recount needed",
     "Two more cushion covers than expected - a return that went "
     "back on the shelf without paperwork."),
    (-2, "Cycle count", 17, "Main store", "Packer", None, "", "No",
     "No", "", "Counted", ""),
    (-1, "Cycle count", 21, "Main store", "Warehouse", -2,
     "Damage not logged", "No", "No", "", "Recount needed",
     "Two pouches missing - most likely the split ones that were "
     "binned without being logged."),
]


def audit(cfg: Config) -> Rows:
    rows: Rows = []
    for (ago, kind, sku_i, where, who, delta, reason, recount,
         posted, ref, status, note) in _AUDITS:
        item = _CATALOGUE[sku_i]
        # a clean count matches the opening quantity; a variance is
        # that quantity plus the (signed) difference found
        counted = item[14] + (delta or 0)
        rows.append({
            "date": _day(cfg, ago),
            "audit_type": kind,
            "sku": item[0],
            "location": where,
            "counted_by": who,
            "system_qty": item[14],
            "counted_qty": max(counted, 0),
            "reason": reason,
            "recount": recount,
            "posted": posted,
            "movement_ref": ref,
            "status": status,
            "notes": note,
        })
    return rows


# ---------------------------------------------------------------------------
# 19. Expense Tracker
# ---------------------------------------------------------------------------
# Stock purchases are kept out of the operating total on purpose.
# Buying stock is not a cost until the stock sells; mixing the two
# is how people convince themselves a good month was a bad one.

#: (category, description, amount, method, recurring, tax category)
_MONTHLY_COSTS = [
    ("Warehouse rent", "Unit 4, Thornfield Yard - monthly rent",
     650.00, "Bank transfer", "Monthly", "Operating expense"),
    ("Utilities", "Electricity and water", 118.40, "Direct debit",
     "Monthly", "Operating expense"),
    ("Software subscriptions", "Shop subscription, accounting "
     "software and email", 96.00, "Card", "Monthly", "Operating expense"),
    ("Insurance", "Stock and public liability cover", 74.00,
     "Direct debit", "Monthly", "Operating expense"),
    ("Advertising & marketing", "Marketplace ads", 180.00, "Card",
     "Monthly", "Operating expense"),
    ("Wages & contractors", "Weekend packing help", 420.00,
     "Bank transfer", "Monthly", "Operating expense"),
]

#: (days ago, category, description, amount, method, tax category)
_ONE_OFF_COSTS = [
    (-112, "Packaging & mailers", "Branded tissue and ribbon - "
     "not for resale", 142.60, "Card", "Operating expense"),
    (-104, "Trade shows & markets", "Portland trade show stand",
     480.00, "Bank transfer", "Operating expense"),
    (-96, "Shipping & postage", "Courier account top-up", 300.00,
     "Card", "Operating expense"),
    (-88, "Equipment", "Heat sealer and label printer", 318.00,
     "Card", "Capital / asset"),
    (-77, "Accounting & legal", "Bookkeeper - quarterly", 225.00,
     "Bank transfer", "Operating expense"),
    (-66, "Shipping & postage", "Courier account top-up", 300.00,
     "Card", "Operating expense"),
    (-58, "Travel", "Van hire and fuel for the Ridgeway "
     "collection", 164.30, "Card", "Operating expense"),
    (-51, "Equipment repair", "Shelving repair after the "
     "gutter leak", 88.00, "Cash", "Operating expense"),
    (-44, "Trade shows & markets", "Harvest fair pitch fee",
     95.00, "Cash", "Operating expense"),
    (-38, "Shipping & postage", "Courier account top-up", 300.00,
     "Card", "Operating expense"),
    (-31, "Bank charges", "Quarterly account charges",
     42.00, "Direct debit", "Operating expense"),
    (-24, "Accounting & legal", "Accountant - year-end advice",
     180.00, "Bank transfer", "Operating expense"),
    (-18, "Packaging & mailers", "Void fill and tape", 96.50,
     "Card", "Operating expense"),
    (-11, "Shipping & postage", "Courier account top-up", 300.00,
     "Card", "Operating expense"),
    (-7, "Training", "Small-business pricing course",
     149.00, "Card", "Operating expense"),
    (-3, "Advertising & marketing", "Autumn catalogue print run",
     264.00, "Card", "Operating expense"),
]


def expenses(cfg: Config) -> Rows:
    rows: Rows = []
    # four months of fixed costs, billed on the 1st
    for months_back in range(3, -1, -1):
        when = cfg.today.replace(day=1)
        month = when.month - months_back
        year = when.year
        while month < 1:
            month += 12
            year -= 1
        billed = _dt.date(year, month, 1)
        if billed > cfg.today:
            continue
        for (category, description, amount, method, recurring,
             tax_cat) in _MONTHLY_COSTS:
            rows.append({
                "date": billed,
                "description": description,
                "category": category,
                "supplier": "",
                "amount": amount,
                "tax_amount": 0.0,
                "method": method,
                "recurring": recurring,
                "tax_category": tax_cat,
                "receipt": "Yes",
                "reference": "",
                "notes": "",
            })
    for (ago, category, description, amount, method, tax_cat) in \
            _ONE_OFF_COSTS:
        rows.append({
            "date": _day(cfg, ago),
            "description": description,
            "category": category,
            "supplier": "",
            "amount": amount,
            "tax_amount": 0.0,
            "method": method,
            "recurring": "One off",
            "tax_category": tax_cat,
            "receipt": "Yes" if ago < -10 else "No",
            "reference": "",
            "notes": ("No receipt kept. Find it before the "
                      "year end." if ago >= -10 else ""),
        })
    # and one that proves the point about stock purchases
    rows.append({
        "date": _day(cfg, -14),
        "description": "Ridgeway Ceramics invoice INV-9243 - stock "
                       "for resale",
        "category": "Stock purchases",
        "supplier": _sup(2),
        "amount": 1342.80,
        "tax_amount": 0.0,
        "method": "Bank transfer",
        "recurring": "One off",
        "tax_category": "Cost of sale",
        "receipt": "Yes",
        "reference": "PO-0011",
        "notes": "Logged here for the bank reconciliation only. It "
                 "is deliberately kept out of the operating total - "
                 "stock is a cost when it sells, not when it is "
                 "bought.",
    })
    return rows


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------
# Keyed by register MODULE name, not sheet name. A mismatch here
# produces zero sample rows, silently, and the build still succeeds.

_BUILDERS: Dict[str, Callable[[Config], Rows]] = {
    "products": products,
    "movements": movements,
    "suppliers": suppliers,
    "purchases": purchases,
    "customers": customers,
    "pricing": pricing,
    "orders": orders,
    "retail": retail,
    "returns": returns,
    "locations": locations,
    "audit": audit,
    "expenses": expenses,
}


def get(module: str, cfg: Config) -> Rows:
    """Sample rows for a register module, or an empty list."""
    builder = _BUILDERS.get(module)
    if builder is None:
        return []
    return builder(cfg)
