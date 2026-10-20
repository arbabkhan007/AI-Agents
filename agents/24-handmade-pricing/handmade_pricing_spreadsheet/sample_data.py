"""
Sample data for the demo workbook.

One coherent little shop - *Willow & Thread Handmade*, Asheville, North
Carolina - selling candles, jewellery, crochet, clothing, woodwork and digital
patterns. Every register cross references the ones above it, and the numbers
are chosen so the story reads correctly:

* the best sellers are also the most profitable ones;
* one product (the Chunky Ribbed Scarf) is priced below cost and the workbook
  flags it everywhere, because that is the most useful thing a pricing
  calculator can show you;
* 57 sales spread over five months, with a clear seasonal dip in summer;
* four wholesale customers, one of which has been flagged late;
* a bundle priced under the sum of its parts (as bundles should be);
* four events, one of which lost money on table fees.

Delete the `Samples` folder or run with `--blank` for a clean template.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List, Optional

from .config import Config

_DATE = _dt.date

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _days(cfg: Config, offset: int) -> _dt.date:
    """A date *offset* days before today (negative = in the future)."""
    return cfg.today - _dt.timedelta(days=offset)


def _month(cfg: Config, months_back: int, day: int = 1) -> _dt.date:
    year = cfg.today.year
    month = cfg.today.month - months_back
    while month < 1:
        month += 12
        year -= 1
    return _dt.date(year, month, min(day, 28))


# ---------------------------------------------------------------------------
# Materials - everything bought in to make things
# ---------------------------------------------------------------------------

def _materials(cfg: Config) -> List[Dict[str, Any]]:
    return [
        # ---- candle supplies
        dict(id="M-0001", name="Golden Brands 464 soy wax", sku="WAX-464",
             category="Wax", supplier="CandleScience", unit="lb",
             pack_size=50, unit_cost=2.05, waste_pct=0.03, reorder_point=40,
             reorder_qty=100, on_hand=120, location="Shelf A1", lead_days=5,
             notes="50 lb case. Melts at 185F, pours at 135F."),
        dict(id="M-0002", name="Beeswax pastilles", sku="WAX-BEE",
             category="Wax", supplier="Local Bee Farm", unit="lb",
             pack_size=10, unit_cost=8.40, waste_pct=0.02, reorder_point=5,
             reorder_qty=10, on_hand=8, location="Shelf A2", lead_days=14,
             notes="Blended 30% into soy for the pillar candles."),
        dict(id="M-0003", name="Candle fragrance oil - cedar & sage",
             sku="FRG-CED", category="Fragrance", supplier="CandleScience",
             unit="fl oz", pack_size=16, unit_cost=3.10, waste_pct=0.02,
             reorder_point=12, reorder_qty=32, on_hand=26,
             location="Shelf A3", lead_days=5,
             notes="Load at 8% of wax weight."),
        dict(id="M-0004", name="Candle fragrance oil - lavender fields",
             sku="FRG-LAV", category="Fragrance", supplier="CandleScience",
             unit="fl oz", pack_size=16, unit_cost=2.95, waste_pct=0.02,
             reorder_point=12, reorder_qty=32, on_hand=31,
             location="Shelf A3", lead_days=5, notes="Load at 8%."),
        dict(id="M-0005", name="Candle fragrance oil - vanilla bourbon",
             sku="FRG-VAN", category="Fragrance", supplier="CandleScience",
             unit="fl oz", pack_size=16, unit_cost=3.25, waste_pct=0.02,
             reorder_point=12, reorder_qty=32, on_hand=9,
             location="Shelf A3", lead_days=5, notes="Low - reorder."),
        dict(id="M-0006", name="CDN-12 wicks (6in, 100 pack)", sku="WCK-12",
             category="Wick", supplier="CandleScience", unit="ea",
             pack_size=100, unit_cost=0.085, waste_pct=0.05,
             reorder_point=150, reorder_qty=300, on_hand=410,
             location="Bin B1", lead_days=5, notes="For 8 oz jars."),
        dict(id="M-0007", name="Wick stickers (500 pack)", sku="WCK-STK",
             category="Wick", supplier="CandleScience", unit="ea",
             pack_size=500, unit_cost=0.012, waste_pct=0.05,
             reorder_point=200, reorder_qty=500, on_hand=640,
             location="Bin B1", lead_days=5, notes=""),
        dict(id="M-0008", name="8 oz amber glass jar", sku="JAR-8AM",
             category="Vessel", supplier="Glass & Co", unit="ea",
             pack_size=24, unit_cost=1.85, waste_pct=0.02, reorder_point=48,
             reorder_qty=96, on_hand=132, location="Shelf C1",
             lead_days=9, notes="Breakage allowance built into waste."),
        dict(id="M-0009", name="Matte black jar lid", sku="LID-8BK",
             category="Vessel", supplier="Glass & Co", unit="ea",
             pack_size=24, unit_cost=0.42, waste_pct=0.02, reorder_point=48,
             reorder_qty=96, on_hand=128, location="Shelf C1",
             lead_days=9, notes=""),
        dict(id="M-0010", name="Candle warning label", sku="LBL-WRN",
             category="Label", supplier="PrintLocal", unit="ea",
             pack_size=500, unit_cost=0.045, waste_pct=0.03,
             reorder_point=100, reorder_qty=500, on_hand=380,
             location="Bin B2", lead_days=3, notes="Required on every jar."),
        # ---- yarn and fibre
        dict(id="M-0011", name="Merino superwash DK yarn", sku="YRN-MER",
             category="Yarn", supplier="Mountain Yarn Co", unit="skein",
             pack_size=10, unit_cost=11.50, waste_pct=0.04, reorder_point=8,
             reorder_qty=20, on_hand=22, location="Shelf D1", lead_days=12,
             notes="100g / 230m per skein."),
        dict(id="M-0012", name="Organic cotton worsted yarn", sku="YRN-COT",
             category="Yarn", supplier="Mountain Yarn Co", unit="skein",
             pack_size=10, unit_cost=7.25, waste_pct=0.04, reorder_point=10,
             reorder_qty=25, on_hand=31, location="Shelf D1",
             lead_days=12, notes="100g / 180m."),
        dict(id="M-0013", name="Chunky roving merino (super bulky)",
             sku="YRN-RVG", category="Yarn", supplier="Fibre Direct",
             unit="oz", pack_size=16, unit_cost=1.95, waste_pct=0.06,
             reorder_point=24, reorder_qty=48, on_hand=58,
             location="Shelf D2", lead_days=18,
             notes="Arm knit scarves. Sheds - 6% waste."),
        dict(id="M-0014", name="Wooden toggle buttons", sku="BTN-TGL",
             category="Notions", supplier="NotionBox", unit="ea",
             pack_size=50, unit_cost=0.55, waste_pct=0.02, reorder_point=20,
             reorder_qty=50, on_hand=64, location="Bin D3", lead_days=7,
             notes=""),
        dict(id="M-0015", name="Branded woven label", sku="LBL-WVN",
             category="Label", supplier="NameTags Inc", unit="ea",
             pack_size=100, unit_cost=0.34, waste_pct=0.03, reorder_point=30,
             reorder_qty=100, on_hand=112, location="Bin B2", lead_days=21,
             notes="Sewn into every finished piece."),
        # ---- jewellery
        dict(id="M-0016", name="Sterling silver ear wires (pair)",
             sku="JWL-EAR", category="Findings", supplier="Rio Metal",
             unit="pair", pack_size=50, unit_cost=0.95, waste_pct=0.03,
             reorder_point=25, reorder_qty=100, on_hand=86,
             location="Drawer E1", lead_days=6, notes=""),
        dict(id="M-0017", name="Sterling silver 20mm jump ring",
             sku="JWL-JMP", category="Findings", supplier="Rio Metal",
             unit="ea", pack_size=100, unit_cost=0.22, waste_pct=0.05,
             reorder_point=50, reorder_qty=200, on_hand=214,
             location="Drawer E1", lead_days=6, notes=""),
        dict(id="M-0018", name="Rose quartz bead 8mm", sku="JWL-RQZ",
             category="Stone", supplier="GemSource", unit="ea",
             pack_size=40, unit_cost=0.62, waste_pct=0.08, reorder_point=30,
             reorder_qty=80, on_hand=96, location="Drawer E2",
             lead_days=20, notes="Drilling defects - 8% waste."),
        dict(id="M-0019", name="Labradorite teardrop 14x10mm",
             sku="JWL-LAB", category="Stone", supplier="GemSource",
             unit="ea", pack_size=20, unit_cost=2.85, waste_pct=0.06,
             reorder_point=12, reorder_qty=40, on_hand=34,
             location="Drawer E2", lead_days=20, notes=""),
        dict(id="M-0020", name="14k gold filled chain (per inch)",
             sku="JWL-GFC", category="Chain", supplier="Rio Metal",
             unit="in", pack_size=40, unit_cost=0.78, waste_pct=0.04,
             reorder_point=30, reorder_qty=80, on_hand=61,
             location="Drawer E1", lead_days=6, notes="Sold by the inch."),
        # ---- fabric and notions
        dict(id="M-0021", name="Linen cotton fabric (per yard)",
             sku="FAB-LCN", category="Fabric", supplier="Fabric House",
             unit="yd", pack_size=10, unit_cost=9.75, waste_pct=0.08,
             reorder_point=6, reorder_qty=15, on_hand=18,
             location="Roll F1", lead_days=8,
             notes="Cutting waste 8% - width 54in."),
        dict(id="M-0022", name="Cotton drawstring cord", sku="NOT-CRD",
             category="Notions", supplier="NotionBox", unit="yd",
             pack_size=50, unit_cost=0.18, waste_pct=0.03, reorder_point=10,
             reorder_qty=50, on_hand=42, location="Bin F2", lead_days=7,
             notes=""),
        dict(id="M-0023", name="Brass grommet set", sku="NOT-GRM",
             category="Notions", supplier="NotionBox", unit="ea",
             pack_size=100, unit_cost=0.14, waste_pct=0.04, reorder_point=40,
             reorder_qty=100, on_hand=148, location="Bin F2",
             lead_days=7, notes=""),
        dict(id="M-0024", name="Hard maple board (per board foot)",
             sku="WDW-MPL", category="Lumber", supplier="Sawmill Direct",
             unit="bf", pack_size=20, unit_cost=6.40, waste_pct=0.12,
             reorder_point=8, reorder_qty=25, on_hand=26,
             location="Rack G1", lead_days=15,
             notes="12% waste for knots and planing."),
        dict(id="M-0025", name="Food safe hard wax oil finish",
             sku="WDW-FIN", category="Finish", supplier="Sawmill Direct",
             unit="fl oz", pack_size=32, unit_cost=1.15, waste_pct=0.05,
             reorder_point=8, reorder_qty=32, on_hand=22,
             location="Shelf G2", lead_days=15, notes="Two coats."),
        dict(id="M-0026", name="Sandpaper assortment sheet", sku="WDW-SND",
             category="Consumable", supplier="Tool Depot", unit="ea",
             pack_size=25, unit_cost=0.48, waste_pct=0.10, reorder_point=6,
             reorder_qty=25, on_hand=19, location="Shelf G2",
             lead_days=3, notes=""),
        # ---- packaging
        dict(id="M-0027", name="Kraft bubble mailer 10x13", sku="PKG-BUB",
             category="Mailer", supplier="PackRight", unit="ea",
             pack_size=100, unit_cost=0.42, waste_pct=0.02, reorder_point=40,
             reorder_qty=100, on_hand=96, location="Shelf H1",
             lead_days=4, notes=""),
        dict(id="M-0028", name="Corrugated shipping box 12x9x4",
             sku="PKG-BOX", category="Box", supplier="PackRight",
             unit="ea", pack_size=25, unit_cost=0.98, waste_pct=0.02,
             reorder_point=20, reorder_qty=50, on_hand=38,
             location="Shelf H1", lead_days=4, notes=""),
        dict(id="M-0029", name="Tissue paper sheet", sku="PKG-TIS",
             category="Wrap", supplier="PackRight", unit="ea",
             pack_size=100, unit_cost=0.055, waste_pct=0.05,
             reorder_point=50, reorder_qty=200, on_hand=240,
             location="Shelf H2", lead_days=4, notes=""),
        dict(id="M-0030", name="Branded sticker seal", sku="PKG-STK",
             category="Wrap", supplier="PrintLocal", unit="ea",
             pack_size=250, unit_cost=0.085, waste_pct=0.04,
             reorder_point=60, reorder_qty=250, on_hand=310,
             location="Shelf H2", lead_days=3, notes=""),
        dict(id="M-0031", name="Care card (thank you insert)",
             sku="PKG-CARD", category="Insert", supplier="PrintLocal",
             unit="ea", pack_size=250, unit_cost=0.12, waste_pct=0.03,
             reorder_point=60, reorder_qty=250, on_hand=188,
             location="Shelf H2", lead_days=3, notes=""),
    ]


# ---------------------------------------------------------------------------
# Products - 14 items across six craft types
# ---------------------------------------------------------------------------

def _products(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="P-0001", name="Soy candle 8oz - cedar & sage",
             sku="WT-CND-001", category="Candle", craft="Candles",
             status="Active", channel="Etsy",
             retail_price=32.00, wholesale_price=16.00, msrp=34.00,
             material_cost=6.18, labor_minutes=38, packaging_cost=1.05,
             shipping_cost=6.40, overhead_cost=1.58, total_cost=15.19,
             target_margin=0.55, suggested_price=33.76, profit=16.81,
             margin=0.499, units_sold=96, revenue=3072.00, gross_profit=1613.76,
             hourly_rate=25.00, labor_cost=15.83, effective_hourly=25.40,
             listing_fee=0.20, transaction_fee=2.08, processing_fee=1.21,
             ads_fee=0.00, total_fees=3.49, fee_pct=0.104,
             net_revenue=28.51, price_per_hour=25.40,
             notes="Best seller. Poured in batches of 12.",
             tags="candle, soy, home fragrance, cedar, sage, gift",
             photo="candle-cedar.jpg", url="etsy.com/listing/wt-cnd-001",
             created=_days(cfg, 420), reviewed=_days(cfg, 41),
             next_review=_days(cfg, -49), batch_id="BT-0001",
             size="8 oz", weight_oz=11.2, dimensions="3.5 x 3.5 x 4 in",
             difficulty="Easy", lead_days=3, active="Yes",
             featured="Yes", season="Autumn / Winter"),
        dict(id="P-0002", name="Soy candle 8oz - lavender fields",
             sku="WT-CND-002", category="Candle", craft="Candles",
             status="Active", channel="Etsy",
             retail_price=32.00, wholesale_price=16.00, msrp=34.00,
             material_cost=5.94, labor_minutes=38, packaging_cost=1.05,
             shipping_cost=6.40, overhead_cost=1.58, total_cost=14.97,
             target_margin=0.55, suggested_price=33.27, profit=17.03,
             margin=0.502, units_sold=84, revenue=2688.00,
             gross_profit=1430.52, hourly_rate=25.00, labor_cost=15.83,
             effective_hourly=25.11, listing_fee=0.20, transaction_fee=2.08,
             processing_fee=1.21, ads_fee=0.00, total_fees=3.49,
             fee_pct=0.103, net_revenue=28.51, price_per_hour=25.11,
             notes="Second best seller.",
             tags="candle, soy, lavender, relaxation, gift for her",
             photo="candle-lavender.jpg", url="etsy.com/listing/wt-cnd-002",
             created=_days(cfg, 420), reviewed=_days(cfg, 41),
             next_review=_days(cfg, -49), batch_id="BT-0001", size="8 oz",
             weight_oz=11.2, dimensions="3.5 x 3.5 x 4 in",
             difficulty="Easy", lead_days=3, active="Yes", featured="No",
             season="All year"),
        dict(id="P-0003", name="Soy candle trio gift set",
             sku="WT-CND-003", category="Candle", craft="Candles",
             status="Active", channel="Etsy",
             retail_price=78.00, wholesale_price=39.00, msrp=85.00,
             material_cost=17.20, labor_minutes=95, packaging_cost=3.40,
             shipping_cost=11.20, overhead_cost=3.96, total_cost=75.31,
             target_margin=0.50, suggested_price=150.62, profit=2.69,
             margin=0.044, units_sold=22, revenue=1716.00,
             gross_profit=59.18, hourly_rate=25.00, labor_cost=39.58,
             effective_hourly=2.03, listing_fee=0.20, transaction_fee=5.07,
             processing_fee=2.59, ads_fee=11.70, total_fees=19.56,
             fee_pct=0.127, net_revenue=58.44, price_per_hour=2.03,
             notes="Priced too low - raise to at least 129 or drop the gift box.",
             tags="candle set, gift box, housewarming, trio",
             photo="candle-trio.jpg", url="etsy.com/listing/wt-cnd-003",
             created=_days(cfg, 300), reviewed=_days(cfg, 96),
             next_review=_days(cfg, -6), batch_id="BT-0002", size="3 x 8 oz",
             weight_oz=36.0, dimensions="11 x 4 x 4.5 in",
             difficulty="Medium", lead_days=5, active="Yes", featured="Yes",
             season="Holiday"),
        dict(id="P-0004", name="Rose quartz drop earrings",
             sku="WT-JWL-001", category="Jewelry", craft="Jewelry",
             status="Active", channel="Etsy",
             retail_price=46.00, wholesale_price=23.00, msrp=52.00,
             material_cost=4.32, labor_minutes=42, packaging_cost=1.65,
             shipping_cost=4.85, overhead_cost=1.75, total_cost=29.99,
             target_margin=0.55, suggested_price=66.64, profit=16.01,
             margin=0.389, units_sold=38, revenue=1748.00,
             gross_profit=608.38, hourly_rate=25.00, labor_cost=17.50,
             effective_hourly=24.98, listing_fee=0.20, transaction_fee=3.00,
             processing_fee=1.63, ads_fee=0.00, total_fees=4.83,
             fee_pct=0.105, net_revenue=41.17, price_per_hour=24.98,
             notes="Sterling findings. Good repeat purchase rate.",
             tags="earrings, rose quartz, sterling silver, gemstone, dainty",
             photo="earrings-rosequartz.jpg",
             url="etsy.com/listing/wt-jwl-001",
             created=_days(cfg, 380), reviewed=_days(cfg, 28),
             next_review=_days(cfg, -62), batch_id="", size="One size",
             weight_oz=0.9, dimensions="1.5 in drop", difficulty="Medium",
             lead_days=2, active="Yes", featured="Yes", season="All year"),
        dict(id="P-0005", name="Labradorite pendant necklace",
             sku="WT-JWL-002", category="Jewelry", craft="Jewelry",
             status="Active", channel="Etsy",
             retail_price=88.00, wholesale_price=44.00, msrp=95.00,
             material_cost=19.40, labor_minutes=65, packaging_cost=2.10,
             shipping_cost=5.20, overhead_cost=2.71, total_cost=56.50,
             target_margin=0.58, suggested_price=134.52, profit=31.50,
             margin=0.389, units_sold=17, revenue=1496.00,
             gross_profit=535.50, hourly_rate=25.00, labor_cost=27.08,
             effective_hourly=29.08, listing_fee=0.20, transaction_fee=5.72,
             processing_fee=2.89, ads_fee=13.20, total_fees=22.01,
             fee_pct=0.125, net_revenue=65.99, price_per_hour=29.08,
             notes="Higher end. Only 2-3 a month but strong margin per hour.",
             tags="necklace, labradorite, gold filled, pendant, statement",
             photo="necklace-labradorite.jpg",
             url="etsy.com/listing/wt-jwl-002",
             created=_days(cfg, 260), reviewed=_days(cfg, 34),
             next_review=_days(cfg, -56), batch_id="", size="18in chain",
             weight_oz=1.4, dimensions="14 x 10 mm stone",
             difficulty="Hard", lead_days=3, active="Yes", featured="No",
             season="All year"),
        dict(id="P-0006", name="Cotton market tote",
             sku="WT-CLO-001", category="Clothing", craft="Clothing",
             status="Active", channel="Etsy",
             retail_price=54.00, wholesale_price=27.00, msrp=60.00,
             material_cost=12.60, labor_minutes=75, packaging_cost=1.20,
             shipping_cost=7.10, overhead_cost=3.13, total_cost=55.28,
             target_margin=0.50, suggested_price=110.56, profit=-1.28,
             margin=-0.018, units_sold=31, revenue=1674.00,
             gross_profit=-39.68, hourly_rate=25.00, labor_cost=31.25,
             effective_hourly=-1.02, listing_fee=0.20, transaction_fee=3.51,
             processing_fee=1.87, ads_fee=0.00, total_fees=5.58,
             fee_pct=0.103, net_revenue=48.42, price_per_hour=-1.02,
             notes="UNDERPRICED - raise to 79 or shorten the strap hardware step.",
             tags="tote, market bag, linen, reusable, eco",
             photo="tote-linen.jpg", url="etsy.com/listing/wt-clo-001",
             created=_days(cfg, 200), reviewed=_days(cfg, 120),
             next_review=_days(cfg, 30), batch_id="BT-0004",
             size="15 x 16 in", weight_oz=7.5,
             dimensions="15 x 16 x 4 in", difficulty="Medium",
             lead_days=4, active="Yes", featured="No", season="All year"),
        dict(id="P-0007", name="Linen apron - cross back",
             sku="WT-CLO-002", category="Clothing", craft="Clothing",
             status="Active", channel="Etsy",
             retail_price=92.00, wholesale_price=46.00, msrp=98.00,
             material_cost=24.80, labor_minutes=140, packaging_cost=1.85,
             shipping_cost=7.90, overhead_cost=5.83, total_cost=102.88,
             target_margin=0.55, suggested_price=228.62, profit=-10.88,
             margin=-0.101, units_sold=12, revenue=1104.00,
             gross_profit=-130.56, hourly_rate=25.00, labor_cost=58.33,
             effective_hourly=-7.77, listing_fee=0.20, transaction_fee=5.98,
             processing_fee=3.01, ads_fee=0.00, total_fees=9.19,
             fee_pct=0.100, net_revenue=82.81, price_per_hour=-7.77,
             notes="UNDERPRICED. 140 min of sewing cannot sell at 92.",
             tags="apron, linen, cross back, kitchen, gift",
             photo="apron-linen.jpg", url="etsy.com/listing/wt-clo-002",
             created=_days(cfg, 150), reviewed=_days(cfg, 15),
             next_review=_days(cfg, -75), batch_id="", size="One size",
             weight_oz=10.0, dimensions="24 x 32 in", difficulty="Hard",
             lead_days=7, active="Yes", featured="No", season="All year"),
        dict(id="P-0008", name="Chunky ribbed scarf",
             sku="WT-CRO-001", category="Crochet", craft="Crochet",
             status="Active", channel="Etsy",
             retail_price=68.00, wholesale_price=34.00, msrp=75.00,
             material_cost=23.40, labor_minutes=180, packaging_cost=1.45,
             shipping_cost=8.20, overhead_cost=7.50, total_cost=118.55,
             target_margin=0.50, suggested_price=237.10, profit=-50.55,
             margin=-0.426, units_sold=9, revenue=612.00,
             gross_profit=-454.95, hourly_rate=25.00, labor_cost=75.00,
             effective_hourly=-16.85, listing_fee=0.20,
             transaction_fee=4.42, processing_fee=2.29, ads_fee=0.00,
             total_fees=6.91, fee_pct=0.101, net_revenue=61.09,
             price_per_hour=-16.85,
             notes="LOSS MAKER. 3 hours of crochet at 68 is unsustainable. "
                   "Either raise to 165, switch to a cheaper roving, or "
                   "retire the pattern.",
             tags="scarf, chunky, arm knit, merino, winter",
             photo="scarf-chunky.jpg", url="etsy.com/listing/wt-cro-001",
             created=_days(cfg, 330), reviewed=_days(cfg, 9),
             next_review=_days(cfg, -81), batch_id="BT-0003",
             size="60 in", weight_oz=19.0, dimensions="8 x 60 in",
             difficulty="Easy", lead_days=6, active="Yes", featured="No",
             season="Winter"),
        dict(id="P-0009", name="Cotton granny square cardigan",
             sku="WT-CRO-002", category="Crochet", craft="Crochet",
             status="Active", channel="Own website",
             retail_price=285.00, wholesale_price=0.00, msrp=300.00,
             material_cost=58.00, labor_minutes=720, packaging_cost=3.20,
             shipping_cost=12.40, overhead_cost=30.00, total_cost=343.60,
             target_margin=0.60, suggested_price=859.00, profit=-58.60,
             margin=-0.171, units_sold=3, revenue=855.00,
             gross_profit=-175.80, hourly_rate=25.00, labor_cost=300.00,
             effective_hourly=-4.88, listing_fee=0.00,
             transaction_fee=0.00, processing_fee=8.81, ads_fee=25.65,
             total_fees=34.46, fee_pct=0.040, net_revenue=820.54,
             price_per_hour=-4.88,
             notes="12 hours of work. Made to order only, deposit required. "
                   "Raise to 549 for a 25/hr wage.",
             tags="cardigan, granny square, cotton, handmade clothing, "
                  "slow fashion",
             photo="cardigan-granny.jpg", url="willowandthread.com/cardigan",
             created=_days(cfg, 240), reviewed=_days(cfg, 60),
             next_review=_days(cfg, 30), batch_id="", size="M",
             weight_oz=34.0, dimensions="20 x 26 in", difficulty="Hard",
             lead_days=21, active="Yes", featured="Yes", season="Autumn"),
        dict(id="P-0010", name="Amigurumi fox - made to order",
             sku="WT-CRO-003", category="Crochet", craft="Crochet",
             status="Active", channel="Etsy",
             retail_price=52.00, wholesale_price=0.00, msrp=58.00,
             material_cost=9.20, labor_minutes=150, packaging_cost=1.85,
             shipping_cost=6.90, overhead_cost=6.25, total_cost=86.70,
             target_margin=0.50, suggested_price=173.40, profit=-34.70,
             margin=-0.400, units_sold=14, revenue=728.00,
             gross_profit=-485.80, hourly_rate=25.00, labor_cost=62.50,
             effective_hourly=-13.88, listing_fee=0.20,
             transaction_fee=3.38, processing_fee=1.81, ads_fee=0.00,
             total_fees=5.39, fee_pct=0.104, net_revenue=46.61,
             price_per_hour=-13.88,
             notes="LOSS MAKER - 2.5 hours each. Keep as a pattern product "
                   "instead (see P-0013).",
             tags="amigurumi, fox, plush, nursery, toy pattern",
             photo="amigurumi-fox.jpg", url="etsy.com/listing/wt-cro-003",
             created=_days(cfg, 190), reviewed=_days(cfg, 22),
             next_review=_days(cfg, -68), batch_id="", size="9 in",
             weight_oz=5.5, dimensions="9 x 5 x 6 in", difficulty="Medium",
             lead_days=10, active="Yes", featured="No", season="All year"),
        dict(id="P-0011", name="Maple serving board",
             sku="WT-WDW-001", category="Woodwork", craft="Woodworking",
             status="Active", channel="Craft fair",
             retail_price=64.00, wholesale_price=32.00, msrp=70.00,
             material_cost=16.80, labor_minutes=110, packaging_cost=2.40,
             shipping_cost=12.60, overhead_cost=4.58, total_cost=84.28,
             target_margin=0.50, suggested_price=168.56, profit=-20.28,
             margin=-0.241, units_sold=8, revenue=512.00,
             gross_profit=-162.24, hourly_rate=25.00, labor_cost=45.83,
             effective_hourly=-11.07, listing_fee=0.00,
             transaction_fee=0.00, processing_fee=2.17, ads_fee=0.00,
             total_fees=2.17, fee_pct=0.034, net_revenue=61.83,
             price_per_hour=-11.07,
             notes="Heavy - shipping kills it. Sell at fairs only or raise "
                   "to 119 online.",
             tags="serving board, maple, cutting board, kitchen, wedding gift",
             photo="board-maple.jpg", url="willowandthread.com/board",
             created=_days(cfg, 210), reviewed=_days(cfg, 45),
             next_review=_days(cfg, 45), batch_id="BT-0005",
             size="18 x 8 in", weight_oz=42.0, dimensions="18 x 8 x 1 in",
             difficulty="Medium", lead_days=10, active="Yes", featured="No",
             season="Holiday"),
        dict(id="P-0012", name="Wooden ring box - walnut",
             sku="WT-WDW-002", category="Woodwork", craft="Woodworking",
             status="Active", channel="Etsy",
             retail_price=48.00, wholesale_price=24.00, msrp=55.00,
             material_cost=7.20, labor_minutes=85, packaging_cost=2.20,
             shipping_cost=7.40, overhead_cost=3.54, total_cost=55.79,
             target_margin=0.55, suggested_price=123.98, profit=-7.79,
             margin=-0.142, units_sold=11, revenue=528.00,
             gross_profit=-85.69, hourly_rate=25.00, labor_cost=35.42,
             effective_hourly=-5.51, listing_fee=0.20,
             transaction_fee=3.12, processing_fee=1.69, ads_fee=0.00,
             total_fees=5.01, fee_pct=0.095, net_revenue=42.99,
             price_per_hour=-5.51,
             notes="Wedding season seller. Needs a price rise to 74.",
             tags="ring box, walnut, wedding, proposal, keepsake",
             photo="ringbox-walnut.jpg", url="etsy.com/listing/wt-wdw-002",
             created=_days(cfg, 170), reviewed=_days(cfg, 18),
             next_review=_days(cfg, -72), batch_id="", size="4 x 4 x 2 in",
             weight_oz=9.0, dimensions="4 x 4 x 2 in", difficulty="Hard",
             lead_days=7, active="Yes", featured="No", season="All year"),
        dict(id="P-0013", name="Fox amigurumi PDF pattern",
             sku="WT-DIG-001", category="Digital", craft="Digital",
             status="Active", channel="Etsy",
             retail_price=8.50, wholesale_price=0.00, msrp=9.00,
             material_cost=0.00, labor_minutes=0, packaging_cost=0.00,
             shipping_cost=0.00, overhead_cost=0.35, total_cost=0.35,
             target_margin=0.85, suggested_price=2.33, profit=8.15,
             margin=0.894, units_sold=142, revenue=1207.00,
             gross_profit=1077.30, hourly_rate=25.00, labor_cost=0.00,
             effective_hourly=0.00, listing_fee=0.20, transaction_fee=0.55,
             processing_fee=0.51, ads_fee=0.00, total_fees=1.26,
             fee_pct=0.104, net_revenue=7.24, price_per_hour=0.00,
             notes="Passive income. Zero material cost - highest margin in "
                   "the shop.",
             tags="pdf pattern, amigurumi, crochet pattern, fox, instant "
                  "download",
             photo="pattern-fox.jpg", url="etsy.com/listing/wt-dig-001",
             created=_days(cfg, 185), reviewed=_days(cfg, 65),
             next_review=_days(cfg, 25), batch_id="", size="PDF",
             weight_oz=0.0, dimensions="US Letter + A4", difficulty="Easy",
             lead_days=0, active="Yes", featured="Yes", season="All year"),
        dict(id="P-0014", name="Granny square cardigan PDF pattern",
             sku="WT-DIG-002", category="Digital", craft="Digital",
             status="Draft", channel="Etsy",
             retail_price=12.00, wholesale_price=0.00, msrp=14.00,
             material_cost=0.00, labor_minutes=0, packaging_cost=0.00,
             shipping_cost=0.00, overhead_cost=0.50, total_cost=0.50,
             target_margin=0.85, suggested_price=3.33, profit=11.50,
             margin=0.892, units_sold=0, revenue=0.00, gross_profit=0.00,
             hourly_rate=25.00, labor_cost=0.00, effective_hourly=0.00,
             listing_fee=0.20, transaction_fee=0.00, processing_fee=0.00,
             ads_fee=0.00, total_fees=0.20, fee_pct=0.000, net_revenue=0.00,
             price_per_hour=0.00,
             notes="Photography and sizing chart still to do.",
             tags="pdf pattern, cardigan, granny square, crochet pattern",
             photo="", url="", created=_days(cfg, 35), reviewed=_days(cfg, 5),
             next_review=_days(cfg, -85), batch_id="", size="PDF",
             weight_oz=0.0, dimensions="US Letter + A4", difficulty="Medium",
             lead_days=0, active="No", featured="No", season="Autumn"),
    ]


# ---------------------------------------------------------------------------
# Material usage - bill of materials per product
# ---------------------------------------------------------------------------

def _material_usage(cfg: Config) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    plan = [
        # (product, material, qty per unit)
        ("P-0001", "M-0001", 0.55), ("P-0001", "M-0003", 0.42),
        ("P-0001", "M-0006", 1), ("P-0001", "M-0007", 1),
        ("P-0001", "M-0008", 1), ("P-0001", "M-0009", 1),
        ("P-0001", "M-0010", 1),
        ("P-0002", "M-0001", 0.55), ("P-0002", "M-0004", 0.42),
        ("P-0002", "M-0006", 1), ("P-0002", "M-0007", 1),
        ("P-0002", "M-0008", 1), ("P-0002", "M-0009", 1),
        ("P-0002", "M-0010", 1),
        ("P-0003", "M-0001", 1.65), ("P-0003", "M-0003", 0.42),
        ("P-0003", "M-0004", 0.42), ("P-0003", "M-0005", 0.42),
        ("P-0003", "M-0006", 3), ("P-0003", "M-0007", 3),
        ("P-0003", "M-0008", 3), ("P-0003", "M-0009", 3),
        ("P-0003", "M-0010", 3), ("P-0003", "M-0029", 3),
        ("P-0004", "M-0016", 1), ("P-0004", "M-0017", 2),
        ("P-0004", "M-0018", 2),
        ("P-0005", "M-0019", 1), ("P-0005", "M-0017", 2),
        ("P-0005", "M-0020", 18),
        ("P-0006", "M-0021", 0.9), ("P-0006", "M-0022", 2),
        ("P-0006", "M-0023", 4), ("P-0006", "M-0015", 1),
        ("P-0007", "M-0021", 1.8), ("P-0007", "M-0022", 3),
        ("P-0007", "M-0015", 1),
        ("P-0008", "M-0013", 12), ("P-0008", "M-0014", 2),
        ("P-0008", "M-0015", 1),
        ("P-0009", "M-0012", 8), ("P-0009", "M-0014", 6),
        ("P-0009", "M-0015", 1),
        ("P-0010", "M-0011", 1.5), ("P-0010", "M-0015", 1),
        ("P-0011", "M-0024", 2.2), ("P-0011", "M-0025", 3),
        ("P-0011", "M-0026", 2),
        ("P-0012", "M-0024", 0.8), ("P-0012", "M-0025", 1.5),
        ("P-0012", "M-0026", 1),
    ]
    for n, (pid, mid, qty) in enumerate(plan, start=1):
        rows.append(dict(
            id=f"MU-{n:04d}", product=pid, material=mid, qty=qty,
            unit="per unit", scrap_pct=0.05, cost=0.0, notes="",
            source="Bill of materials"))
    return rows


# ---------------------------------------------------------------------------
# Labour
# ---------------------------------------------------------------------------

def _labor(cfg: Config) -> List[Dict[str, Any]]:
    rate = cfg.hourly_rate
    rows: List[Dict[str, Any]] = [
        dict(id="L-0001", date=_days(cfg, 30), employee="Maya Albright",
             task="Pouring candles", product="P-0001", hours=3.0,
             rate=rate, cost=75.00, notes="Batch of 12 - 8 oz jars."),
        dict(id="L-0002", date=_days(cfg, 28), employee="Maya Albright",
             task="Wicking and labeling", product="P-0001", hours=1.5,
             rate=rate, cost=37.50, notes=""),
        dict(id="L-0003", date=_days(cfg, 26), employee="Maya Albright",
             task="Assembly - earrings", product="P-0004", hours=2.5,
             rate=rate, cost=62.50, notes="Six pairs."),
        dict(id="L-0004", date=_days(cfg, 24), employee="Maya Albright",
             task="Crochet - scarf", product="P-0008", hours=3.0,
             rate=rate, cost=75.00, notes="One finished scarf."),
        dict(id="L-0005", date=_days(cfg, 22), employee="Nadia Whitfield",
             task="Sewing - totes", product="P-0006", hours=5.0,
             rate=18.00, cost=90.00, notes="Four totes."),
        dict(id="L-0006", date=_days(cfg, 20), employee="Nadia Whitfield",
             task="Sewing - aprons", product="P-0007", hours=4.5,
             rate=18.00, cost=81.00, notes="Two aprons."),
        dict(id="L-0007", date=_days(cfg, 18), employee="Maya Albright",
             task="Woodworking - boards", product="P-0011", hours=3.5,
             rate=rate, cost=87.50, notes="Two boards, sanding and oil."),
        dict(id="L-0008", date=_days(cfg, 16), employee="Maya Albright",
             task="Photography", product="", hours=2.0, rate=rate,
             cost=50.00, notes="New cardigan photos."),
        dict(id="L-0009", date=_days(cfg, 14), employee="Maya Albright",
             task="Listing and SEO", product="P-0014", hours=1.5,
             rate=rate, cost=37.50, notes="Pattern listing copy."),
        dict(id="L-0010", date=_days(cfg, 12), employee="Nadia Whitfield",
             task="Packing orders", product="", hours=3.0, rate=18.00,
             cost=54.00, notes="14 orders."),
        dict(id="L-0011", date=_days(cfg, 10), employee="Maya Albright",
             task="Craft fair setup", product="", hours=4.0, rate=rate,
             cost=100.00, notes="River Arts fair."),
        dict(id="L-0012", date=_days(cfg, 8), employee="Maya Albright",
             task="Jewellery - pendant", product="P-0005", hours=2.0,
             rate=rate, cost=50.00, notes="Two pendants."),
    ]
    return rows


# ---------------------------------------------------------------------------
# Packaging components
# ---------------------------------------------------------------------------

def _packaging(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="PK-0001", name="Kraft bubble mailer", material="M-0027",
             qty=1, cost=0.42, weight_oz=1.2, type="Mailer",
             products="P-0004, P-0005, P-0013, P-0014", notes="Jewellery and "
                  "patterns."),
        dict(id="PK-0002", name="Tissue wrap", material="M-0029", qty=2,
             cost=0.11, weight_oz=0.4, type="Wrap",
             products="P-0001, P-0002, P-0004, P-0005", notes="Two sheets."),
        dict(id="PK-0003", name="Branded seal sticker", material="M-0030",
             qty=1, cost=0.085, weight_oz=0.1, type="Seal",
             products="All", notes=""),
        dict(id="PK-0004", name="Thank you care card", material="M-0031",
             qty=1, cost=0.12, weight_oz=0.3, type="Insert",
             products="All", notes="Handwritten note on the back."),
        dict(id="PK-0005", name="Corrugated box 12x9x4", material="M-0028",
             qty=1, cost=0.98, weight_oz=6.0, type="Box",
             products="P-0003, P-0006, P-0007, P-0008, P-0009",
             notes="Fragile glass - double box the trio."),
    ]


# ---------------------------------------------------------------------------
# Shipping options
# ---------------------------------------------------------------------------

def _shipping(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="SH-0001", label="Digital download", carrier="None",
             service="Instant", zone="N/A", weight_from=0, weight_to=0,
             base_cost=0.00, per_oz=0.00, handling=0.00, retail_charge=0.00,
             absorbed=0.00, tracking="No", insurance="No",
             products="P-0013, P-0014", notes="No postage at all."),
        dict(id="SH-0002", label="USPS First Class - jewellery",
             carrier="USPS", service="First Class", zone="Domestic",
             weight_from=0.1, weight_to=15.9, base_cost=4.10, per_oz=0.05,
             handling=0.75, retail_charge=5.50, absorbed=0.00,
             tracking="Yes", insurance="No", products="P-0004, P-0005",
             notes="Padded mailer."),
        dict(id="SH-0003", label="USPS Priority - candle single",
             carrier="USPS", service="Priority Mail", zone="Domestic",
             weight_from=16, weight_to=32, base_cost=8.15, per_oz=0.04,
             handling=1.20, retail_charge=9.50, absorbed=3.85,
             tracking="Yes", insurance="No", products="P-0001, P-0002",
             notes="Glass - insurance recommended above 60."),
        dict(id="SH-0004", label="USPS Priority - candle trio",
             carrier="USPS", service="Priority Mail", zone="Domestic",
             weight_from=33, weight_to=64, base_cost=9.95, per_oz=0.04,
             handling=1.25, retail_charge=12.00, absorbed=0.45,
             tracking="Yes", insurance="Yes", products="P-0003",
             notes=""),
        dict(id="SH-0005", label="UPS Ground - woodwork",
             carrier="UPS", service="Ground", zone="Domestic",
             weight_from=33, weight_to=96, base_cost=12.60, per_oz=0.03,
             handling=2.50, retail_charge=14.00, absorbed=1.10,
             tracking="Yes", insurance="No",
             products="P-0011, P-0012", notes="Heavy and awkward."),
        dict(id="SH-0006", label="USPS Priority - textiles",
             carrier="USPS", service="Priority Mail", zone="Domestic",
             weight_from=16, weight_to=48, base_cost=8.15, per_oz=0.04,
             handling=1.05, retail_charge=9.00, absorbed=0.20,
             tracking="Yes", insurance="No",
             products="P-0006, P-0007, P-0008, P-0009, P-0010",
             notes=""),
    ]


# ---------------------------------------------------------------------------
# Overhead
# ---------------------------------------------------------------------------

def _overhead(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="OH-0001", name="Studio rent (half of shared space)",
             category="Space", amount=425.00, frequency="Monthly",
             per_month=425.00, allocated="Yes", notes="240 sq ft corner."),
        dict(id="OH-0002", name="Electricity", category="Utilities",
             amount=86.00, frequency="Monthly", per_month=86.00,
             allocated="Yes", notes="Kiln and melters push this up in winter."),
        dict(id="OH-0003", name="Internet", category="Utilities",
             amount=55.00, frequency="Monthly", per_month=55.00,
             allocated="Yes", notes="Split with the other studio."),
        dict(id="OH-0004", name="Etsy Plus subscription",
             category="Platform", amount=10.00, frequency="Monthly",
             per_month=10.00, allocated="Yes", notes=""),
        dict(id="OH-0005", name="Shopify Basic", category="Platform",
             amount=39.00, frequency="Monthly", per_month=39.00,
             allocated="Yes", notes="Own website."),
        dict(id="OH-0006", name="Liability insurance", category="Insurance",
             amount=280.00, frequency="Quarterly", per_month=93.33,
             allocated="Yes", notes="Covers craft fairs too."),
        dict(id="OH-0007", name="Bookkeeper", category="Professional",
             amount=150.00, frequency="Monthly", per_month=150.00,
             allocated="Yes", notes=""),
        dict(id="OH-0008", name="Design software", category="Software",
             amount=13.00, frequency="Monthly", per_month=13.00,
             allocated="Yes", notes="Pattern layout and mockups."),
        dict(id="OH-0009", name="Phone", category="Utilities",
             amount=45.00, frequency="Monthly", per_month=45.00,
             allocated="Yes", notes=""),
        dict(id="OH-0010", name="Equipment depreciation",
             category="Equipment", amount=1200.00, frequency="Annual",
             per_month=100.00, allocated="Yes",
             notes="Kiln, sewing machine, table saw - 5 year life."),
        dict(id="OH-0011", name="Studio supplies (cleaning, gloves)",
             category="Supplies", amount=24.00, frequency="Monthly",
             per_month=24.00, allocated="No", notes="Not allocated to product."),
    ]


# ---------------------------------------------------------------------------
# Sales channels
# ---------------------------------------------------------------------------

def _channels(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(name="Etsy", type="Marketplace", listing_fee=0.20,
             transaction_pct=0.065, processing_pct=0.03,
             processing_fixed=0.25, offsite_ads_pct=0.15,
             offsite_ads_active="Yes", currency_fee=0.025,
             regulatory_fee=0.004, subscription=10.00, shipping_fee_pct=0.065,
             fees_on_shipping="Yes", payout_days=3, chargeback_fee=15.00,
             notes="Main channel. Offsite ads are mandatory above 10k."),
        dict(name="Craft fair", type="In person", listing_fee=0.00,
             transaction_pct=0.00, processing_pct=0.027,
             processing_fixed=0.05, offsite_ads_pct=0.00,
             offsite_ads_active="No", currency_fee=0.00,
             regulatory_fee=0.00, subscription=0.00, shipping_fee_pct=0.00,
             fees_on_shipping="No", payout_days=0, chargeback_fee=0.00,
             notes="Card reader only. Table fee lives on the Events tab."),
        dict(name="Own website", type="Own store", listing_fee=0.00,
             transaction_pct=0.00, processing_pct=0.029,
             processing_fixed=0.30, offsite_ads_pct=0.00,
             offsite_ads_active="No", currency_fee=0.01,
             regulatory_fee=0.00, subscription=39.00, shipping_fee_pct=0.00,
             fees_on_shipping="No", payout_days=2, chargeback_fee=15.00,
             notes="Shopify Basic."),
        dict(name="Wholesale", type="Wholesale", listing_fee=0.00,
             transaction_pct=0.00, processing_pct=0.029,
             processing_fixed=0.30, offsite_ads_pct=0.00,
             offsite_ads_active="No", currency_fee=0.00,
             regulatory_fee=0.00, subscription=0.00, shipping_fee_pct=0.00,
             fees_on_shipping="No", payout_days=30, chargeback_fee=0.00,
             notes="Net 30 terms on the Wholesale Orders tab."),
    ]


# ---------------------------------------------------------------------------
# Craft calculators
# ---------------------------------------------------------------------------

def _crochet(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="CRO-0001", date=_days(cfg, 96), product="P-0008",
             pattern="Chunky ribbed scarf", yarn="M-0013", skeins=12,
             yardage=340, hooks=0.00, notions=1.10, gauge="6 st = 4in",
             minutes=180, difficulty="Easy", size="60 in",
             price=68.00, notes="Roving sheds - bought 20% extra."),
        dict(id="CRO-0002", date=_days(cfg, 60), product="P-0009",
             pattern="Granny square cardigan", yarn="M-0012", skeins=8,
             yardage=1440, hooks=0.00, notions=3.30, gauge="12 st = 4in",
             minutes=720, difficulty="Hard", size="M", price=285.00,
             notes="Made to order. 12 hours over three weeks."),
        dict(id="CRO-0003", date=_days(cfg, 22), product="P-0010",
             pattern="Fox amigurumi", yarn="M-0011", skeins=1.5,
             yardage=345, hooks=0.00, notions=2.00, gauge="20 st = 4in",
             minutes=150, difficulty="Medium", size="9 in", price=52.00,
             notes="Safety eyes included in notions."),
        dict(id="CRO-0004", date=_days(cfg, 12), product="",
             pattern="Market bag swatch", yarn="M-0012", skeins=1,
             yardage=180, hooks=0.00, notions=0.00, gauge="10 st = 4in",
             minutes=45, difficulty="Easy", size="Sample", price=0.00,
             notes="Testing a new handle construction."),
    ]


def _jewelry(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="JWL-0001", date=_days(cfg, 90), product="P-0004",
             design="Rose quartz drop earrings", metal="Sterling silver",
             stones=2, stone_cost=1.24, findings=2.08, wire=0.00,
             chain=0.00, plating=0.00, minutes=42, difficulty="Medium",
             size="1.5 in drop", price=46.00, notes="Six pairs in one sitting."),
        dict(id="JWL-0002", date=_days(cfg, 16), product="P-0005",
             design="Labradorite pendant", metal="14k gold filled",
             stones=1, stone_cost=2.85, findings=0.44, wire=0.00,
             chain=14.04, plating=0.00, minutes=65, difficulty="Hard",
             size="18in chain", price=88.00, notes="Wire wrapped bezel."),
        dict(id="JWL-0003", date=_days(cfg, 8), product="",
             design="Brass cuff prototype", metal="Brass", stones=0,
             stone_cost=0.00, findings=1.20, wire=2.40, chain=0.00,
             plating=3.50, minutes=95, difficulty="Hard", size="One size",
             price=0.00, notes="Prototype - not for sale yet."),
    ]


def _candles(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="CND-0001", date=_days(cfg, 30), product="P-0001",
             blend="Cedar & sage", wax="M-0001", wax_lb=6.6,
             fragrance="M-0003", fragrance_pct=0.08, wick="M-0006",
             vessel="M-0008", vessel_cost=1.85, cure_days=14,
             pour_temp=135, melt_temp=185, burn_hours=45,
             minutes_per_pour=38, batch_size=12, price=32.00,
             notes="Test burn passed - full melt pool at 3 hours."),
        dict(id="CND-0002", date=_days(cfg, 28), product="P-0002",
             blend="Lavender fields", wax="M-0001", wax_lb=6.6,
             fragrance="M-0004", fragrance_pct=0.08, wick="M-0006",
             vessel="M-0008", vessel_cost=1.85, cure_days=14,
             pour_temp=135, melt_temp=185, burn_hours=45,
             minutes_per_pour=38, batch_size=12, price=32.00, notes=""),
        dict(id="CND-0003", date=_days(cfg, 20), product="P-0003",
             blend="Trio gift set", wax="M-0001", wax_lb=4.95,
             fragrance="M-0005", fragrance_pct=0.08, wick="M-0006",
             vessel="M-0008", vessel_cost=5.55, cure_days=14,
             pour_temp=135, melt_temp=185, burn_hours=45,
             minutes_per_pour=95, batch_size=6, price=78.00,
             notes="Three scents in one box."),
    ]


def _clothing(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="CLO-0001", date=_days(cfg, 22), product="P-0006",
             pattern_name="Market tote v2", fabric="M-0021", yards=0.9,
             interfacing=0.40, notions=0.72, lining=0.00, trim=0.00,
             size="15 x 16 in", cut_minutes=25, sew_minutes=45,
             finish_minutes=5, total_minutes=75, difficulty="Medium",
             price=54.00, notes="Four cut in one layout."),
        dict(id="CLO-0002", date=_days(cfg, 20), product="P-0007",
             pattern_name="Cross back apron", fabric="M-0021", yards=1.8,
             interfacing=0.00, notions=0.60, lining=0.00, trim=0.00,
             size="One size", cut_minutes=35, sew_minutes=95,
             finish_minutes=10, total_minutes=140, difficulty="Hard",
             price=92.00, notes="Bias binding is the slow part."),
    ]


def _woodworking(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="WDW-0001", date=_days(cfg, 18), product="P-0011",
             project="Maple serving board", species="Hard maple",
             board_feet=2.2, hardware=0.00, finish="M-0025",
             finish_oz=3, glue=0.35, cut_minutes=30, shape_minutes=25,
             sand_minutes=30, finish_minutes=25, total_minutes=110,
             difficulty="Medium", size="18 x 8 in", price=64.00,
             notes="Two coats of hard wax oil, 24h between."),
        dict(id="WDW-0002", date=_days(cfg, 14), product="P-0012",
             project="Walnut ring box", species="Black walnut",
             board_feet=0.8, hardware=1.80, finish="M-0025", finish_oz=1.5,
             glue=0.25, cut_minutes=20, shape_minutes=25, sand_minutes=20,
             finish_minutes=20, total_minutes=85, difficulty="Hard",
             size="4 x 4 x 2 in", price=48.00, notes="Hinge and magnet "
                  "counted in hardware."),
    ]


def _digital(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="DIG-0001", date=_days(cfg, 185), product="P-0013",
             file_name="fox-amigurumi-pattern.pdf", type="PDF pattern",
             format="PDF", pages=24, creation_hours=40,
             software_cost=0.00, hosting_cost=0.00, price=8.50,
             difficulty="Easy", notes="US Letter and A4 versions included."),
        dict(id="DIG-0002", date=_days(cfg, 35), product="P-0014",
             file_name="granny-cardigan-pattern.pdf", type="PDF pattern",
             format="PDF", pages=38, creation_hours=65,
             software_cost=0.00, hosting_cost=0.00, price=12.00,
             difficulty="Medium", notes="Sizing chart still to photograph."),
    ]


# ---------------------------------------------------------------------------
# Bundles
# ---------------------------------------------------------------------------

def _bundles(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="BN-0001", name="Cosy night in - candle + scarf",
             products="P-0001, P-0008", list_price=100.00,
             bundle_price=84.00, discount=0.16, cost=0.00, profit=0.00,
             margin=0.000, active="Yes", channel="Etsy",
             notes="Winter promotion. Should really be retired until the "
                   "scarf is repriced."),
        dict(id="BN-0002", name="Gift box - earrings + candle",
             products="P-0004, P-0002", list_price=78.00, bundle_price=68.00,
             discount=0.128, cost=0.00, profit=0.00, margin=0.000,
             active="Yes", channel="Etsy",
             notes="Strongest bundle - both parts are profitable."),
        dict(id="BN-0003", name="Starter kit - pattern + yarn",
             products="P-0013", list_price=8.50, bundle_price=8.50,
             discount=0.000, cost=0.00, profit=0.00, margin=0.000,
             active="No", channel="Etsy",
             notes="On hold - waiting on a yarn supplier who will drop ship."),
    ]


def _bundle_lines(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="BL-0001", bundle="BN-0001", product="P-0001", qty=1,
             unit_price=32.00, line_total=32.00, notes="Cedar & sage."),
        dict(id="BL-0002", bundle="BN-0001", product="P-0008", qty=1,
             unit_price=68.00, line_total=68.00, notes="Chunky scarf."),
        dict(id="BL-0003", bundle="BN-0002", product="P-0004", qty=1,
             unit_price=46.00, line_total=46.00, notes=""),
        dict(id="BL-0004", bundle="BN-0002", product="P-0002", qty=1,
             unit_price=32.00, line_total=32.00, notes=""),
        dict(id="BL-0005", bundle="BN-0003", product="P-0013", qty=1,
             unit_price=8.50, line_total=8.50, notes="Pattern only."),
    ]


# ---------------------------------------------------------------------------
# Variations
# ---------------------------------------------------------------------------

def _variations(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="VR-0001", product="P-0001", option="Scent",
             value="Cedar & sage", sku="WT-CND-001-CED", price_adj=0.00,
             cost_adj=0.00, qty_delta=0, stock=42, active="Yes",
             notes="Default."),
        dict(id="VR-0002", product="P-0001", option="Scent",
             value="Vanilla bourbon", sku="WT-CND-001-VAN", price_adj=2.00,
             cost_adj=0.30, qty_delta=0, stock=18, active="Yes",
             notes="Fragrance oil costs more."),
        dict(id="VR-0003", product="P-0004", option="Stone",
             value="Amethyst", sku="WT-JWL-001-AME", price_adj=0.00,
             cost_adj=-0.10, qty_delta=0, stock=24, active="Yes", notes=""),
        dict(id="VR-0004", product="P-0004", option="Stone",
             value="Moonstone", sku="WT-JWL-001-MOO", price_adj=6.00,
             cost_adj=1.40, qty_delta=0, stock=12, active="Yes",
             notes="Premium stone."),
        dict(id="VR-0005", product="P-0009", option="Size", value="S",
             sku="WT-CRO-002-S", price_adj=-25.00, cost_adj=-6.00,
             qty_delta=-1, stock=0, active="Yes", notes="Made to order."),
        dict(id="VR-0006", product="P-0009", option="Size", value="L",
             sku="WT-CRO-002-L", price_adj=45.00, cost_adj=12.00,
             qty_delta=2, stock=0, active="Yes", notes="Made to order."),
        dict(id="VR-0007", product="P-0011", option="Finish",
             value="Dark walnut stain", sku="WT-WDW-001-DW", price_adj=8.00,
             cost_adj=1.20, qty_delta=0, stock=3, active="Yes",
             notes="Extra coat and 24h drying."),
    ]


# ---------------------------------------------------------------------------
# Batches
# ---------------------------------------------------------------------------

def _batches(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="BT-0001", product="P-0001", started=_days(cfg, 30),
             finished=_days(cfg, 16), qty_planned=12, qty_done=12,
             qty_defect=1, material_cost=74.16, labor_minutes=228,
             overhead=18.96, batch_cost=110.62, cost_per_unit=9.22,
             cure_days=14, notes="One jar cracked in the pour."),
        dict(id="BT-0002", product="P-0003", started=_days(cfg, 20),
             finished=_days(cfg, 6), qty_planned=6, qty_done=6,
             qty_defect=0, material_cost=103.20, labor_minutes=570,
             overhead=23.75, batch_cost=364.45, cost_per_unit=60.74,
             cure_days=14, notes="Gift boxes for the holiday push."),
        dict(id="BT-0003", product="P-0008", started=_days(cfg, 24),
             finished=_days(cfg, 21), qty_planned=3, qty_done=2,
             qty_defect=0, material_cost=70.20, labor_minutes=360,
             overhead=15.00, batch_cost=235.20, cost_per_unit=117.60,
             cure_days=0, notes="One still on the hook."),
        dict(id="BT-0004", product="P-0006", started=_days(cfg, 22),
             finished=_days(cfg, 19), qty_planned=4, qty_done=4,
             qty_defect=0, material_cost=50.40, labor_minutes=300,
             overhead=12.50, batch_cost=187.90, cost_per_unit=46.98,
             cure_days=0, notes=""),
        dict(id="BT-0005", product="P-0011", started=_days(cfg, 18),
             finished=_days(cfg, 11), qty_planned=3, qty_done=2,
             qty_defect=1, material_cost=50.40, labor_minutes=210,
             overhead=8.75, batch_cost=146.65, cost_per_unit=73.33,
             cure_days=0, notes="One board warped - kiln dried stock next time."),
        dict(id="BT-0006", product="P-0004", started=_days(cfg, 12),
             finished=_days(cfg, 10), qty_planned=6, qty_done=6,
             qty_defect=0, material_cost=25.92, labor_minutes=252,
             overhead=10.50, batch_cost=141.42, cost_per_unit=23.57,
             cure_days=0, notes=""),
    ]


# ---------------------------------------------------------------------------
# Promotions
# ---------------------------------------------------------------------------

def _promotions(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="PM-0001", code="AUTUMN15", name="Autumn 15% off",
             type="Percentage", discount=0.15, start=_days(cfg, 45),
             end=_days(cfg, 15), applies_to="P-0001, P-0002",
             min_qty=1, max_uses=100, used=64, active="No",
             notes="Finished. 64 redemptions."),
        dict(id="PM-0002", code="FREESHIP", name="Free shipping over 60",
             type="Shipping", discount=0.00, start=_days(cfg, 30),
             end=_days(cfg, -30), applies_to="All", min_qty=1,
             max_uses=0, used=41, active="Yes",
             notes="Shipping is absorbed - watch the margin."),
        dict(id="PM-0003", code="HOLIDAY25", name="Holiday 25% off bundles",
             type="Percentage", discount=0.25, start=_days(cfg, -20),
             end=_days(cfg, -60), applies_to="BN-0001, BN-0002",
             min_qty=1, max_uses=50, used=0, active="Yes",
             notes="Scheduled for the holiday push."),
        dict(id="PM-0004", code="WHOLESALE10", name="Wholesale early pay 10%",
             type="Percentage", discount=0.10, start=_days(cfg, 90),
             end=_days(cfg, -90), applies_to="Wholesale orders",
             min_qty=6, max_uses=0, used=3, active="Yes",
             notes="For paying inside 10 days."),
    ]


# ---------------------------------------------------------------------------
# Price history
# ---------------------------------------------------------------------------

def _price_history(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="PH-0001", product="P-0001", date=_days(cfg, 420),
             old_price=0.00, new_price=28.00, reason="Launch",
             cost_at_time=13.90, margin_after=0.414, units_after=0,
             notes="First listing price."),
        dict(id="PH-0002", product="P-0001", date=_days(cfg, 300),
             old_price=28.00, new_price=30.00, reason="Cost increase",
             cost_at_time=14.60, margin_after=0.436, units_after=22,
             notes="Wax went up 8%."),
        dict(id="PH-0003", product="P-0001", date=_days(cfg, 180),
             old_price=30.00, new_price=32.00, reason="Repositioning",
             cost_at_time=15.19, margin_after=0.449, units_after=41,
             notes="No drop in sales - good signal."),
        dict(id="PH-0004", product="P-0004", date=_days(cfg, 380),
             old_price=0.00, new_price=42.00, reason="Launch",
             cost_at_time=27.10, margin_after=0.270, units_after=0,
             notes=""),
        dict(id="PH-0005", product="P-0004", date=_days(cfg, 150),
             old_price=42.00, new_price=46.00, reason="Cost increase",
             cost_at_time=29.99, margin_after=0.300, units_after=19,
             notes="Silver findings up."),
        dict(id="PH-0006", product="P-0006", date=_days(cfg, 200),
             old_price=0.00, new_price=48.00, reason="Launch",
             cost_at_time=52.10, margin_after=-0.079, units_after=0,
             notes="Launched below cost by mistake."),
        dict(id="PH-0007", product="P-0006", date=_days(cfg, 90),
             old_price=48.00, new_price=54.00, reason="Cost increase",
             cost_at_time=55.28, margin_after=-0.024, units_after=14,
             notes="Still below cost."),
        dict(id="PH-0008", product="P-0008", date=_days(cfg, 330),
             old_price=0.00, new_price=72.00, reason="Launch",
             cost_at_time=112.00, margin_after=-0.357, units_after=0,
             notes=""),
        dict(id="PH-0009", product="P-0008", date=_days(cfg, 120),
             old_price=72.00, new_price=68.00, reason="Sale",
             cost_at_time=118.55, margin_after=-0.426, units_after=5,
             notes="Discounted to clear - wrong move."),
        dict(id="PH-0010", product="P-0013", date=_days(cfg, 185),
             old_price=0.00, new_price=6.50, reason="Launch",
             cost_at_time=0.35, margin_after=0.892, units_after=0,
             notes=""),
        dict(id="PH-0011", product="P-0013", date=_days(cfg, 100),
             old_price=6.50, new_price=8.50, reason="Repositioning",
             cost_at_time=0.35, margin_after=0.918, units_after=88,
             notes="Sales went UP after the rise."),
        dict(id="PH-0012", product="P-0011", date=_days(cfg, 210),
             old_price=0.00, new_price=64.00, reason="Launch",
             cost_at_time=81.00, margin_after=-0.210, units_after=0,
             notes=""),
        dict(id="PH-0013", product="P-0005", date=_days(cfg, 260),
             old_price=0.00, new_price=88.00, reason="Launch",
             cost_at_time=56.50, margin_after=0.270, units_after=0,
             notes=""),
    ]


# ---------------------------------------------------------------------------
# Competitors
# ---------------------------------------------------------------------------

def _competitors(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="CP-0001", name="Hearth & Hollow Candles", url="etsy.com/hh",
             product="Soy candle 8oz", category="Candle",
             my_product="P-0001", competitor_price=29.00, my_price=32.00,
             shipping=5.99, rating=4.8, reviews=2410, sales="10k+",
             position="Cheaper", notes="Pours in bigger batches."),
        dict(id="CP-0002", name="Blue Ridge Wick Co", url="blueridgewick.com",
             product="Soy candle trio", category="Candle",
             my_product="P-0003", competitor_price=96.00, my_price=78.00,
             shipping=0.00, rating=4.7, reviews=640, sales="3k+",
             position="Cheaper", notes="Free shipping, so really 96 all in."),
        dict(id="CP-0003", name="Stone & Silver Studio",
             url="etsy.com/stonesilver", product="Gemstone drop earrings",
             category="Jewelry", my_product="P-0004",
             competitor_price=52.00, my_price=46.00, shipping=4.50,
             rating=4.9, reviews=1820, sales="8k+", position="Cheaper",
             notes="Room to raise to 49."),
        dict(id="CP-0004", name="Aster Fine Jewellery",
             url="asterfine.com", product="Labradorite pendant",
             category="Jewelry", my_product="P-0005",
             competitor_price=145.00, my_price=88.00, shipping=0.00,
             rating=4.9, reviews=310, sales="1k+", position="Cheaper",
             notes="Solid gold, not filled - not a true comparison."),
        dict(id="CP-0005", name="Loom & Linen", url="etsy.com/loomlinen",
             product="Linen market tote", category="Clothing",
             my_product="P-0006", competitor_price=62.00, my_price=54.00,
             shipping=8.00, rating=4.6, reviews=940, sales="5k+",
             position="Cheaper", notes="They charge shipping on top."),
        dict(id="CP-0006", name="Fielder Apparel", url="fielderapparel.com",
             product="Cross back linen apron", category="Clothing",
             my_product="P-0007", competitor_price=118.00, my_price=92.00,
             shipping=0.00, rating=4.5, reviews=220, sales="500+",
             position="Cheaper", notes="Confirms 92 is far too low."),
        dict(id="CP-0007", name="Hook & Story", url="etsy.com/hookstory",
             product="Chunky knit scarf", category="Crochet",
             my_product="P-0008", competitor_price=145.00, my_price=68.00,
             shipping=12.00, rating=4.9, reviews=1560, sales="6k+",
             position="Cheaper", notes="THIS is the real market price."),
        dict(id="CP-0008", name="Slow Stitch Club", url="slowstitch.club",
             product="Granny square cardigan", category="Crochet",
             my_product="P-0009", competitor_price=420.00, my_price=285.00,
             shipping=0.00, rating=5.0, reviews=180, sales="300+",
             position="Cheaper", notes="Waitlist of 6 weeks."),
        dict(id="CP-0009", name="Grain & Groove", url="grainandgroove.com",
             product="Maple serving board", category="Woodwork",
             my_product="P-0011", competitor_price=85.00, my_price=64.00,
             shipping=15.00, rating=4.7, reviews=410, sales="2k+",
             position="Cheaper", notes="They ship for 15 - I ship for 12.60."),
        dict(id="CP-0010", name="Pattern Press", url="etsy.com/patternpress",
             product="Amigurumi PDF pattern", category="Digital",
             my_product="P-0013", competitor_price=7.50, my_price=8.50,
             shipping=0.00, rating=4.8, reviews=5200, sales="20k+",
             position="Premium", notes="Only place I am above market - and it "
                                     "is working."),
    ]


# ---------------------------------------------------------------------------
# Waste
# ---------------------------------------------------------------------------

def _waste(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="WL-0001", date=_days(cfg, 88), product="P-0001",
             material="M-0008", qty=2, cost=3.70, reason="Breakage",
             notes="Two jars chipped in transit from the supplier."),
        dict(id="WL-0002", date=_days(cfg, 74), product="P-0001",
             material="M-0001", qty=0.4, cost=0.82, reason="Spillage",
             notes="Melter tipped."),
        dict(id="WL-0003", date=_days(cfg, 66), product="P-0004",
             material="M-0018", qty=3, cost=1.86, reason="Defect",
             notes="Beads with cracked drill holes."),
        dict(id="WL-0004", date=_days(cfg, 58), product="P-0006",
             material="M-0021", qty=0.4, cost=3.90, reason="Cutting error",
             notes="Mis-aligned the pattern piece."),
        dict(id="WL-0005", date=_days(cfg, 50), product="P-0008",
             material="M-0013", qty=1.5, cost=2.93, reason="Shedding",
             notes="Roving unusable at the ends."),
        dict(id="WL-0006", date=_days(cfg, 44), product="P-0011",
             material="M-0024", qty=0.9, cost=5.76, reason="Knots",
             notes="Board had a loose knot - scrapped."),
        dict(id="WL-0007", date=_days(cfg, 37), product="",
             material="M-0027", qty=6, cost=2.52, reason="Damaged in storage",
             notes="Water damage on the floor stock."),
        dict(id="WL-0008", date=_days(cfg, 29), product="P-0003",
             material="M-0009", qty=3, cost=1.26, reason="Defect",
             notes="Lids with scratched finish."),
        dict(id="WL-0009", date=_days(cfg, 21), product="P-0009",
             material="M-0012", qty=0.5, cost=3.63, reason="Cutting error",
             notes="Cut a sleeve too short."),
        dict(id="WL-0010", date=_days(cfg, 13), product="P-0012",
             material="M-0025", qty=2, cost=2.30, reason="Spillage",
             notes="Finish tin knocked over."),
        dict(id="WL-0011", date=_days(cfg, 6), product="P-0002",
             material="M-0010", qty=20, cost=0.90, reason="Misprint",
             notes="Warning labels printed with the wrong address."),
    ]


# ---------------------------------------------------------------------------
# Product development
# ---------------------------------------------------------------------------

def _development(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="DV-0001", name="Beeswax pillar candle line",
             type="New product", product="", stage="Prototyping",
             hours_planned=18, hours_actual=11, material_cost=64.00,
             outsourcing=0.00, target_cost=18.00, target_price=44.00,
             start=_days(cfg, 60), due=_days(cfg, -25), status="On track",
             notes="Blending 30% beeswax for a slower burn."),
        dict(id="DV-0002", name="Granny cardigan pattern - photo shoot",
             type="Pattern", product="P-0014", stage="Testing",
             hours_planned=12, hours_actual=9, material_cost=0.00,
             outsourcing=250.00, target_cost=0.50, target_price=12.00,
             start=_days(cfg, 35), due=_days(cfg, -10), status="At risk",
             notes="Photographer booked, sample still being seamed."),
        dict(id="DV-0003", name="Linen apron repricing test",
             type="Price test", product="P-0007", stage="Research",
             hours_planned=6, hours_actual=2, material_cost=0.00,
             outsourcing=0.00, target_cost=102.88, target_price=139.00,
             start=_days(cfg, 15), due=_days(cfg, -45), status="On track",
             notes="Testing 139 against competitor at 118."),
        dict(id="DV-0004", name="Brass cuff collection",
             type="New product", product="", stage="Ideation",
             hours_planned=30, hours_actual=4, material_cost=28.00,
             outsourcing=0.00, target_cost=14.00, target_price=58.00,
             start=_days(cfg, 8), due=_days(cfg, -90), status="On track",
             notes="Prototype on the Jewelry tab."),
        dict(id="DV-0005", name="Walnut ring box - faster hinge method",
             type="Process", product="P-0012", stage="Prototyping",
             hours_planned=10, hours_actual=14, material_cost=18.00,
             outsourcing=0.00, target_cost=48.00, target_price=74.00,
             start=_days(cfg, 40), due=_days(cfg, 5), status="Overdue",
             notes="Over budget on hours - jig did not work."),
        dict(id="DV-0006", name="Wholesale line sheet refresh",
             type="Marketing", product="", stage="Done", hours_planned=8,
             hours_actual=7, material_cost=0.00, outsourcing=0.00,
             target_cost=0.00, target_price=0.00, start=_days(cfg, 70),
             due=_days(cfg, 40), status="Done",
             notes="Shipped to four retailers."),
    ]


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def _events(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="EV-0001", name="River Arts Spring Craft Fair",
             type="Craft fair", date=_days(cfg, 150), days=1,
             table_fee=85.00, travel=32.00, setup_hours=5,
             staff_hours=9, inventory_cost=640.00, units_sold=34,
             revenue=1642.00, notes="Best fair of the year. Book again."),
        dict(id="EV-0002", name="Downtown Saturday Market",
             type="Market stall", date=_days(cfg, 95), days=1,
             table_fee=45.00, travel=12.00, setup_hours=3,
             staff_hours=7, inventory_cost=280.00, units_sold=11,
             revenue=384.00, notes="Quiet - rain all morning."),
        dict(id="EV-0003", name="Handmade Holiday Expo",
             type="Craft fair", date=_days(cfg, 40), days=2,
             table_fee=320.00, travel=68.00, setup_hours=8,
             staff_hours=22, inventory_cost=1450.00, units_sold=58,
             revenue=3210.00, notes="Two days. Table fee was worth it."),
        dict(id="EV-0004", name="Winter Makers Pop-Up",
             type="Pop-up shop", date=_days(cfg, 10), days=1,
             table_fee=120.00, travel=25.00, setup_hours=4,
             staff_hours=8, inventory_cost=520.00, units_sold=9,
             revenue=412.00,
             notes="Lost money after labour - do not repeat."),
        dict(id="EV-0005", name="Spring Fling Maker Fair",
             type="Craft fair", date=_days(cfg, -60), days=1,
             table_fee=95.00, travel=35.00, setup_hours=5,
             staff_hours=9, inventory_cost=700.00, units_sold=0,
             revenue=0.00, notes="Booked - inventory to pull from stock."),
    ]


# ---------------------------------------------------------------------------
# Wholesale
# ---------------------------------------------------------------------------

def _wholesale_customers(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="WC-0001", name="Magnolia Home & Gift", contact="Ruth Ellery",
             email="ruth@magnoliahome.example", phone="(828) 555-0142",
             address="118 Haywood Rd, Asheville NC", terms="Net 30",
             discount=0.50, min_order=300.00, credit_limit=2500.00,
             balance=0.00, status="Approved", tax_exempt="Yes",
             first_order=_days(cfg, 220), last_order=_days(cfg, 35),
             notes="Buys candles and jewellery. Pays on time."),
        dict(id="WC-0002", name="Blue Ridge General Store",
             contact="Tom Vasquez", email="tom@brgs.example",
             phone="(828) 555-0177", address="44 Main St, Boone NC",
             terms="Net 30", discount=0.45, min_order=250.00,
             credit_limit=1800.00, balance=0.00, status="Approved",
             tax_exempt="Yes", first_order=_days(cfg, 180),
             last_order=_days(cfg, 62), notes=""),
        dict(id="WC-0003", name="The Woven Nest", contact="Priya Raman",
             email="priya@wovennest.example", phone="(704) 555-0119",
             address="902 Central Ave, Charlotte NC", terms="Net 15",
             discount=0.40, min_order=200.00, credit_limit=900.00,
             balance=0.00, status="Approved", tax_exempt="No",
             first_order=_days(cfg, 120), last_order=_days(cfg, 18),
             notes="Textiles only."),
        dict(id="WC-0004", name="Cedar & Stone Boutique",
             contact="Alice Ndiaye", email="alice@cedarstone.example",
             phone="(615) 555-0163", address="210 12th Ave S, Nashville TN",
             terms="Net 30", discount=0.50, min_order=400.00,
             credit_limit=3000.00, balance=0.00, status="Prospect",
             tax_exempt="No", first_order=_days(cfg, 0),
             last_order=_days(cfg, 0),
             notes="Line sheet sent. Waiting on a first order."),
        dict(id="WC-0005", name="Pigeon River Books & Gifts",
             contact="Sam Kowalski", email="sam@prbg.example",
             phone="(828) 555-0198", address="7 Depot St, Waynesville NC",
             terms="Net 30", discount=0.45, min_order=150.00,
             credit_limit=600.00, balance=0.00, status="On hold",
             tax_exempt="Yes", first_order=_days(cfg, 300),
             last_order=_days(cfg, 140),
             notes="Two late payments - hold until the balance clears."),
    ]


def _wholesale_orders(cfg: Config) -> List[Dict[str, Any]]:
    return [
        dict(id="WO-0001", date=_days(cfg, 120), customer="WC-0001",
             po_number="MHG-2291", products="P-0001 x24, P-0004 x12",
             qty=36, unit_cost=0.00, list_total=1248.00,
             discount_rate=0.50, wholesale_total=624.00, shipping=28.00,
             tax=0.00, order_total=652.00, status="Paid",
             due=_days(cfg, 90), paid=_days(cfg, 96), notes=""),
        dict(id="WO-0002", date=_days(cfg, 105), customer="WC-0002",
             po_number="BRGS-1140", products="P-0002 x18, P-0011 x6",
             qty=24, unit_cost=0.00, list_total=960.00,
             discount_rate=0.45, wholesale_total=528.00, shipping=42.00,
             tax=0.00, order_total=570.00, status="Paid",
             due=_days(cfg, 75), paid=_days(cfg, 80), notes=""),
        dict(id="WO-0003", date=_days(cfg, 88), customer="WC-0003",
             po_number="WN-0455", products="P-0006 x10", qty=10,
             unit_cost=0.00, list_total=540.00, discount_rate=0.40,
             wholesale_total=324.00, shipping=24.00, tax=0.00,
             order_total=348.00, status="Paid", due=_days(cfg, 73),
             paid=_days(cfg, 71), notes=""),
        dict(id="WO-0004", date=_days(cfg, 62), customer="WC-0002",
             po_number="BRGS-1188", products="P-0001 x30, P-0002 x30",
             qty=60, unit_cost=0.00, list_total=1920.00,
             discount_rate=0.45, wholesale_total=1056.00, shipping=54.00,
             tax=0.00, order_total=1110.00, status="Paid",
             due=_days(cfg, 32), paid=_days(cfg, 40), notes="Paid a week late."),
        dict(id="WO-0005", date=_days(cfg, 45), customer="WC-0001",
             po_number="MHG-2364", products="P-0003 x8, P-0005 x6",
             qty=14, unit_cost=0.00, list_total=1152.00,
             discount_rate=0.50, wholesale_total=576.00, shipping=38.00,
             tax=0.00, order_total=614.00, status="Paid",
             due=_days(cfg, 15), paid=_days(cfg, 14), notes=""),
        dict(id="WO-0006", date=_days(cfg, 35), customer="WC-0001",
             po_number="MHG-2380", products="P-0001 x36", qty=36,
             unit_cost=0.00, list_total=1152.00, discount_rate=0.50,
             wholesale_total=576.00, shipping=32.00, tax=0.00,
             order_total=608.00, status="Shipped", due=_days(cfg, -5),
             paid=_days(cfg, 0), notes="In transit."),
        dict(id="WO-0007", date=_days(cfg, 18), customer="WC-0003",
             po_number="WN-0501", products="P-0007 x6", qty=6,
             unit_cost=0.00, list_total=552.00, discount_rate=0.40,
             wholesale_total=331.20, shipping=22.00, tax=0.00,
             order_total=353.20, status="Invoiced", due=_days(cfg, -3),
             paid=_days(cfg, 0), notes="Net 15 - falls due soon."),
        dict(id="WO-0008", date=_days(cfg, 12), customer="WC-0002",
             po_number="BRGS-1231", products="P-0004 x18, P-0012 x8",
             qty=26, unit_cost=0.00, list_total=1212.00,
             discount_rate=0.45, wholesale_total=666.60, shipping=36.00,
             tax=0.00, order_total=702.60, status="Invoiced",
             due=_days(cfg, -18), paid=_days(cfg, 0), notes=""),
        dict(id="WO-0009", date=_days(cfg, 6), customer="WC-0001",
             po_number="MHG-2402", products="P-0002 x24", qty=24,
             unit_cost=0.00, list_total=768.00, discount_rate=0.50,
             wholesale_total=384.00, shipping=30.00, tax=0.00,
             order_total=414.00, status="Packed", due=_days(cfg, -24),
             paid=_days(cfg, 0), notes="Packing today."),
        dict(id="WO-0010", date=_days(cfg, 2), customer="WC-0003",
             po_number="WN-0512", products="P-0006 x12", qty=12,
             unit_cost=0.00, list_total=648.00, discount_rate=0.40,
             wholesale_total=388.80, shipping=28.00, tax=0.00,
             order_total=416.80, status="Quote", due=_days(cfg, -28),
             paid=_days(cfg, 0), notes="Quote out, awaiting approval."),
    ]


# ---------------------------------------------------------------------------
# Sales - 57 orders over five months
# ---------------------------------------------------------------------------

def _sales(cfg: Config) -> List[Dict[str, Any]]:
    channel_of = {
        "P-0001": "Etsy", "P-0002": "Etsy", "P-0003": "Etsy",
        "P-0004": "Etsy", "P-0005": "Etsy", "P-0006": "Etsy",
        "P-0007": "Etsy", "P-0008": "Etsy", "P-0009": "Own website",
        "P-0010": "Etsy", "P-0011": "Craft fair", "P-0012": "Etsy",
        "P-0013": "Etsy", "P-0014": "Etsy",
    }
    price_of = {
        "P-0001": 32.00, "P-0002": 32.00, "P-0003": 78.00, "P-0004": 46.00,
        "P-0005": 88.00, "P-0006": 54.00, "P-0007": 92.00, "P-0008": 68.00,
        "P-0009": 285.00, "P-0010": 52.00, "P-0011": 64.00, "P-0012": 48.00,
        "P-0013": 8.50,
    }
    # (days ago, product, qty, channel override, promo, notes)
    plan = [
        (150, "P-0013", 1, None, "", "Organic search."),
        (148, "P-0001", 2, None, "", ""),
        (146, "P-0004", 1, None, "", ""),
        (143, "P-0013", 1, None, "", ""),
        (141, "P-0002", 1, None, "", ""),
        (138, "P-0011", 2, None, "", "Sold at the spring fair."),
        (135, "P-0001", 3, None, "", ""),
        (132, "P-0013", 2, None, "", ""),
        (129, "P-0006", 1, None, "", ""),
        (126, "P-0005", 1, None, "", ""),
        (124, "P-0010", 1, None, "", ""),
        (121, "P-0001", 2, None, "", ""),
        (118, "P-0013", 1, None, "", ""),
        (115, "P-0004", 2, None, "", ""),
        (112, "P-0002", 2, None, "", ""),
        (109, "P-0012", 1, None, "", ""),
        (106, "P-0013", 3, None, "", "Etsy ads brought these."),
        (103, "P-0008", 1, None, "", ""),
        (100, "P-0001", 2, None, "", ""),
        (97, "P-0006", 2, None, "", ""),
        (94, "P-0013", 1, None, "", ""),
        (91, "P-0004", 1, None, "", ""),
        (88, "P-0003", 1, None, "", "Gift set."),
        (85, "P-0011", 1, None, "", ""),
        (82, "P-0001", 3, None, "", ""),
        (79, "P-0013", 2, None, "", ""),
        (76, "P-0007", 1, None, "", ""),
        (73, "P-0002", 2, None, "", ""),
        (70, "P-0009", 1, None, "", "Made to order - deposit taken."),
        (66, "P-0013", 1, None, "", ""),
        (62, "P-0004", 2, None, "", ""),
        (58, "P-0001", 2, None, "", ""),
        (54, "P-0012", 2, None, "", ""),
        (50, "P-0013", 4, None, "", "Best pattern week."),
        (46, "P-0006", 1, None, "", ""),
        (42, "P-0002", 1, None, "", ""),
        (38, "P-0010", 1, None, "", ""),
        (34, "P-0001", 2, None, "", ""),
        (30, "P-0013", 2, None, "", ""),
        (27, "P-0005", 1, None, "", ""),
        (24, "P-0004", 1, None, "", ""),
        (21, "P-0008", 1, None, "", ""),
        (18, "P-0001", 3, None, "", ""),
        (15, "P-0013", 2, None, "", ""),
        (13, "P-0011", 1, None, "", ""),
        (11, "P-0002", 2, None, "", ""),
        (9, "P-0006", 1, None, "", ""),
        (7, "P-0013", 3, None, "", ""),
        (6, "P-0003", 1, None, "", ""),
        (5, "P-0004", 2, None, "", ""),
        (4, "P-0012", 1, None, "", ""),
        (3, "P-0001", 2, None, "", ""),
        (2, "P-0013", 2, None, "", ""),
        (2, "P-0009", 1, None, "", "Second cardigan order."),
        (1, "P-0007", 1, None, "", ""),
        (1, "P-0002", 1, None, "", ""),
        (0, "P-0013", 1, None, "", "This morning."),
    ]
    rows: List[Dict[str, Any]] = []
    for n, (ago, pid, qty, chan, promo, note) in enumerate(plan, start=1):
        price = price_of[pid]
        rows.append(dict(
            id=f"SL-{n:04d}", date=_days(cfg, ago), product=pid,
            channel=chan or channel_of[pid], qty=qty, unit_price=price,
            discount_pct=0.00, gross=0.00, fees=0.00, shipping_paid=0.00,
            shipping_cost=0.00, net=0.00, cost=0.00, profit=0.00,
            margin=0.000, promo=promo or "", status="Paid", notes=note))
    return rows


# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------

def build_sample_data(cfg: Config) -> Dict[str, List[Dict[str, Any]]]:
    """Sample rows keyed by sheet name."""
    s: Dict[str, List[Dict[str, Any]]] = {}
    s["Products"] = _products(cfg)
    s["Materials"] = _materials(cfg)
    s["Material Usage"] = _material_usage(cfg)
    s["Labor"] = _labor(cfg)
    s["Packaging"] = _packaging(cfg)
    s["Shipping"] = _shipping(cfg)
    s["Overhead"] = _overhead(cfg)
    s["Channels"] = _channels(cfg)
    s["Crochet"] = _crochet(cfg)
    s["Jewelry"] = _jewelry(cfg)
    s["Candles"] = _candles(cfg)
    s["Clothing"] = _clothing(cfg)
    s["Woodworking"] = _woodworking(cfg)
    s["Digital"] = _digital(cfg)
    s["Bundles"] = _bundles(cfg)
    s["Bundle Lines"] = _bundle_lines(cfg)
    s["Variations"] = _variations(cfg)
    s["Batches"] = _batches(cfg)
    s["Promotions"] = _promotions(cfg)
    s["Price History"] = _price_history(cfg)
    s["Competitors"] = _competitors(cfg)
    s["Waste Log"] = _waste(cfg)
    s["Development"] = _development(cfg)
    s["Events"] = _events(cfg)
    s["Wholesale Customers"] = _wholesale_customers(cfg)
    s["Wholesale Orders"] = _wholesale_orders(cfg)
    s["Sales"] = _sales(cfg)
    return s
