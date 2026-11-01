"""10. Wholesale Pricing - price breaks, and whether they survive.

One row per SKU, mirroring the product list, with three quantity
breaks you set yourself. Buy ten, pay this; buy fifty, pay that; buy a
hundred, pay less again.

Next to every price is its margin at the current weighted average
cost, which is the part most price lists leave out. A tier price set
eighteen months ago against a cost that has gone up 20% since is the
single commonest way a wholesale business sells hard all year and
makes nothing, and the only defence is to show the margin next to the
price where it cannot be ignored.
"""

from __future__ import annotations

from ..config import PRICE_TIERS, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, lookup_product,
                     lookup_product_num_zero, margin, scale_cf,
                     status_cf, yesno, zero)
from ..writer import date_check, number_check

NAME = "Wholesale Pricing"


def _tier(n: int, default_qty: int) -> list:
    """The three columns that make up one price break."""
    return [
        Col(f"tier{n}_qty", f"Tier {n} from", 11, "int",
            validate=number_check(0, 1000000),
            note=f"Order this many or more and tier {n} applies. "
                 f"Leave the whole tier blank to skip it."),
        Col(f"tier{n}_price", f"Tier {n} price", 11, "money",
            validate=number_check(0, 1000000)),
        Col(f"tier{n}_gp", f"Tier {n} GP%", 10, "percent0",
            formula=blank("sku", margin(
                f'({{tier{n}_price}}{{r}}-{{avg_cost}}{{r}})',
                f'{{tier{n}_price}}{{r}}')),
            cf=scale_cf(),
            note="Margin at this break, against weighted average "
                 "cost. Watch this column, not the price."),
    ]


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("sku", "SKU", 15, "id",
            formula='=IF(INDEX([[Product & SKU Database.sku]],'
                    'ROW()-4)="","",'
                    'INDEX([[Product & SKU Database.sku]],ROW()-4))',
            note="Mirrors the Product Database, so every product has "
                 "a price list row whether you have filled it in or "
                 "not."),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("category", "Category", 13, "text",
            formula=lookup_product("category"), hidden=True),
        Col("status", "Product status", 12, "status",
            formula=lookup_product("status"), cf=status_cf(),
            hidden=True),
        Col("avg_cost", "Avg cost", 10, "money4",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.avg_cost]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,'
                                f'{lookup_product_num_zero("cost")[1:]})'),
            note="Weighted average cost, live. Every margin on this "
                 "sheet is against this number, which moves when "
                 "your suppliers move their prices."),
        Col("retail", "Retail price", 12, "money",
            formula=lookup_product_num_zero("retail_price"),
            note="From the product record, for comparison. A trade "
                 "price above half of retail usually means the "
                 "stockist cannot make it work."),
        Col("floor", "Floor price", 11, "money",
            formula=lookup_product_num_zero("min_price"),
            note="The product's own floor. Nothing on this sheet "
                 "should go below it."),

        Col("wholesale", "Base wholesale", 13, "money",
            validate=number_check(0, 1000000),
            note="Your standard trade price - what a stockist pays "
                 "below the first quantity break. Leave blank and "
                 "the product record's wholesale price is used."),
        Col("wholesale_gp", "Base GP%", 9, "percent0",
            formula=blank("sku", margin(
                '({wholesale}{r}-{avg_cost}{r})', "{wholesale}{r}")),
            cf=scale_cf()),
    ]

    for n, (qty, _label) in enumerate(PRICE_TIERS, start=1):
        cols.extend(_tier(n, qty))

    cols.extend([
        Col("best_price", "Best price", 11, "money",
            formula=zero("sku",
                         'IF({tier3_price}{r}>0,{tier3_price}{r},'
                         'IF({tier2_price}{r}>0,{tier2_price}{r},'
                         'IF({tier1_price}{r}>0,{tier1_price}{r},'
                         '{wholesale}{r})))'),
            note="The lowest price anybody can reach on this SKU by "
                 "buying volume. If this is below your floor, it is "
                 "not a discount, it is a donation."),
        Col("best_gp", "Best GP%", 9, "percent0",
            formula=blank("sku", margin(
                '({best_price}{r}-{avg_cost}{r})', "{best_price}{r}")),
            cf=scale_cf()),
        Col("discount_depth", "Discount", 9, "percent0",
            formula='=IF({sku}{r}="","",'
                    'IF({wholesale}{r}<=0,"",'
                    'ROUND(1-{best_price}{r}/{wholesale}{r},4)))',
            note="How far the deepest break is below your base "
                 "trade price.",
            hidden=True),
        Col("retail_ratio", "Of retail", 9, "percent0",
            formula='=IF({sku}{r}="","",IF({retail}{r}<=0,"",'
                    'ROUND({wholesale}{r}/{retail}{r},4)))',
            note="Base trade price as a share of retail. Half is the "
                 "convention; much over and a shop cannot double it "
                 "and still be competitive.",
            hidden=True),
        Col("moq", "MOQ", 7, "int",
            validate=number_check(0, 100000),
            note="Minimum they can buy of this SKU - a case size, "
                 "usually."),
        Col("case_qty", "Case qty", 9, "int",
            validate=number_check(0, 100000),
            note="How many come in a case. Orders that are not a "
                 "multiple of it are flagged, because splitting "
                 "cases costs you time you never charge for."),
        Col("available_trade", "Sell to trade", 12, "flag",
            validate=yesno("Some lines are retail only - seconds, "
                           "samples, packaging."),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "No", "fmt": "muted"},
                {"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("reviewed", "Last reviewed", 12, "date",
            validate=date_check(),
            note="When you last looked at this price. Anything over "
                 "a year old is flagged."),
        Col("notes", "Notes", 24, "wrap"),

        Col("below_floor", "Below floor", 10, "int",
            formula=zero("sku", 'IF({floor}{r}<=0,0,'
                                'IF({best_price}{r}<=0,0,'
                                'IF({best_price}{r}<{floor}{r},1,'
                                '0)))'),
            hidden=True),
        Col("thin_margin", "Thin", 6, "int",
            formula=zero("sku", 'IF({best_price}{r}<=0,0,'
                                'IF({best_gp}{r}="",0,'
                                'IF({best_gp}{r}<MinGP,1,0)))'),
            hidden=True),
        Col("is_priced", "Priced", 7, "int",
            formula=zero("sku", 'IF({wholesale}{r}>0,1,0)'),
            hidden=True),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ])

    return SheetSpec(
        name=NAME,
        title="Wholesale Pricing",
        subtitle=("Three quantity breaks per SKU, with the margin at "
                  "each one shown next to it - because a price "
                  "without its margin is just a hope."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("pricing", cfg),
        help_text=("Set the base trade price and up to three "
                   "quantity breaks. Wholesale order lines price "
                   "themselves off this sheet: the workbook checks "
                   "the largest break first, so a hundred-unit order "
                   "gets the hundred-unit price."),
        extra_notes=[
            "The breaks are yours to set. The quantities shipped in "
            "the example - ten, fifty, a hundred - are a starting "
            "point, not a rule, and you can change every number on "
            "this sheet including the currency on Settings.",
            "Review prices when costs move, not on a schedule. The "
            "Avg cost column on this sheet updates every time a "
            "purchase order is received, so a supplier's price rise "
            "shows up here as a shrinking margin within days.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{status}{r}="Discontinued"', "Retired - discontinued line"),
        ('{available_trade}{r}="No"', "OK"),
        ('{wholesale}{r}<=0',
         "Add - base wholesale price for this SKU"),
        ('{below_floor}{r}=1',
         "Urgent - your deepest break is below the product's floor "
         "price"),
        ('AND({avg_cost}{r}>0,{best_price}{r}>0,'
         '{best_price}{r}<{avg_cost}{r})',
         "Urgent - selling below what it costs you"),
        ('{thin_margin}{r}=1',
         "Action - margin at the deepest break is under your "
         "minimum"),
        ('AND({tier2_qty}{r}>0,{tier1_qty}{r}>0,'
         '{tier2_qty}{r}<={tier1_qty}{r})',
         "Check - tier 2 does not start above tier 1"),
        ('AND({tier3_qty}{r}>0,{tier2_qty}{r}>0,'
         '{tier3_qty}{r}<={tier2_qty}{r})',
         "Check - tier 3 does not start above tier 2"),
        ('AND({tier1_price}{r}>0,{tier1_price}{r}>={wholesale}{r})',
         "Check - the first break is not cheaper than the base "
         "price"),
        ('AND({tier2_price}{r}>0,{tier1_price}{r}>0,'
         '{tier2_price}{r}>={tier1_price}{r})',
         "Check - tier 2 is not cheaper than tier 1"),
        ('AND({retail}{r}>0,{wholesale}{r}>{retail}{r}*0.7)',
         "Check - trade price is too close to retail for a shop to "
         "make it work"),
        ('AND({reviewed}{r}<>"",TodayDate-{reviewed}{r}>365)',
         "Check - this price has not been reviewed in a year"),
        ('{reviewed}{r}=""', "Add - date you last reviewed this "
                             "price"),
    ])
