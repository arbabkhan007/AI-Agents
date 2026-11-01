"""4. Product & SKU Database - where a SKU is born.

This is the foundation. Every other tab in the workbook matches on the
SKU created here, so two rules apply and the sheet enforces both:

* a SKU is unique, and a duplicate is flagged in red the moment it is
  typed - a repeated SKU means two products share one stock figure,
  which is the worst failure this workbook can have;
* a variant that is stocked separately is a separate SKU. "Mug" is not
  a product; "Mug, 350ml, Sage" is.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, bar_cf, blank, id_col,
                     margin, money_cf, rank_desc, scale_cf, status_cf,
                     zero)
from ..writer import date_check, list_from, number_check

NAME = "Product & SKU Database"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("name", "ProductPrefix", digits=cfg.digits("product"),
               header="Product ID",
               note="Generated for you. The SKU is what the rest of "
                    "the workbook joins on. Do not rename a SKU once other "
                    "rows reference it, or those joins will break."),
        Col("sku", "SKU", 15, "id",
            note="Your unique code for this exact product. One "
                 "stocked variant, one SKU. This is the join key for "
                 "the whole workbook - every other tab picks it from "
                 "a list."),
        Col("name", "Product name", 28, "text",
            note="What you call it on the shelf and on the invoice."),
        Col("description", "Description", 32, "wrap",
            note="The detail a picker needs to grab the right one."),
        Col("category", "Category", 14, "text",
            validate=list_from("CategoryList")),
        Col("subcategory", "Subcategory", 15, "text",
            validate=list_from("SubcategoryList")),
        Col("brand", "Brand", 14, "text"),
        Col("variant", "Variant", 14, "text",
            note="The thing that makes this different from its "
                 "siblings: 'Gift boxed', '6 pack', 'Seconds'."),
        Col("size", "Size", 10, "text"),
        Col("colour", "Colour", 12, "text"),
        Col("material", "Material", 14, "text"),
        Col("barcode", "Barcode", 15, "text",
            note="EAN, UPC or your own. Stored as text so a leading "
                 "zero survives."),
        Col("unit", "Unit", 11, "text",
            validate=list_from("UnitList"),
            note="What one unit of stock is. Sell tealights in packs "
                 "of six and the unit is 'Pack of 6', not 'Each'."),
        Col("image", "Image link", 18, "link",
            note="A link to the photo. The workbook stores the "
                 "address, not the picture - a hundred embedded "
                 "images would make this file unusable."),
        Col("supplier", "Supplier ID", 11, "id",
            validate=list_from("SupplierList"),
            note="Who you normally buy it from. Alternatives live on "
                 "the Supplier Database."),
        Col("supplier_sku", "Their code", 13, "text",
            note="The supplier's own code, so a purchase order makes "
                 "sense at their end."),

        # ---- money -----------------------------------------------
        Col("cost", "Unit cost", 11, "money",
            validate=number_check(0, 1000000),
            note="What one unit costs you to buy or make, landed. "
                 "This seeds the valuation; once you start receiving "
                 "purchase orders the weighted average takes over."),
        Col("retail_price", "Retail price", 12, "money",
            validate=number_check(0, 1000000)),
        Col("wholesale_price", "Wholesale", 11, "money",
            validate=number_check(0, 1000000),
            note="Your standard trade price. Quantity breaks live on "
                 "the Wholesale Pricing tab."),
        Col("min_price", "Floor price", 11, "money",
            validate=number_check(0, 1000000),
            note="The lowest you will go, ever. Any price below this "
                 "is flagged, wherever it appears."),
        Col("retail_margin", "Retail GP%", 10, "percent",
            formula=blank("sku", margin(
                "({retail_price}{r}-{cost}{r})",
                "{retail_price}{r}")),
            cf=scale_cf(),
            note="Gross margin at the retail price."),
        Col("wholesale_margin", "Trade GP%", 10, "percent",
            formula=blank("sku", margin(
                "({wholesale_price}{r}-{cost}{r})",
                "{wholesale_price}{r}")),
            cf=scale_cf()),
        Col("markup", "Markup", 9, "number1",
            formula=blank("sku", 'IF({cost}{r}<=0,"",'
                                 'ROUND({retail_price}{r}/'
                                 '{cost}{r},2))'),
            note="Retail price divided by unit cost. A different way "
                 "of saying the same thing as margin, and the one "
                 "most sellers price with."),

        # ---- stock levels ----------------------------------------
        Col("opening_qty", "Opening stock", 12, "int",
            validate=number_check(0, 1000000),
            note="What you had the day you started using this "
                 "workbook. Type it once and never again - every "
                 "change after this is a row on the Stock Movement "
                 "Log, a receipt, a sale or a return."),
        Col("opening_value", "Opening value", 12, "money",
            validate=number_check(0, 10000000),
            note="What that opening stock cost you in total. The "
                 "weighted average cost starts from this."),
        Col("min_stock", "Min level", 10, "int",
            validate=number_check(0, 1000000)),
        Col("max_stock", "Max level", 10, "int",
            validate=number_check(0, 1000000),
            note="The most you want on the shelf. The reorder "
                 "planner buys up to this, not beyond it."),
        Col("reorder_point", "Reorder at", 10, "int",
            validate=number_check(0, 1000000),
            note="Leave this blank and the Reorder Planner will work "
                 "one out from your actual sales and the supplier's "
                 "lead time. Fill it in and yours wins."),
        Col("status", "Status", 12, "status",
            validate=list_from("ProductStatusList"), cf=status_cf()),
        Col("launched", "Launched", 11, "date",
            validate=date_check(),
            note="When you started selling it. Used only for "
                 "reference."),
        Col("notes", "Notes", 30, "wrap"),

        # ---- derived ---------------------------------------------
        Col("variant_label", "Full name", 26, "text",
            formula=blank("sku", 'TRIM({name}{r}&'
                                 'IF({variant}{r}="",""," - "&'
                                 '{variant}{r})&'
                                 'IF({size}{r}="",""," "&{size}{r})&'
                                 'IF({colour}{r}="",""," "&'
                                 '{colour}{r}))'),
            note="Name, variant, size and colour in one string - what "
                 "a picking list should actually say.",
            hidden=True),
        Col("dup_count", "Dups", 7, "int",
            formula=blank("sku",
                          'COUNTIF({sku_first}:{sku_last},{sku}{r})'),
            hidden=True),
        Col("is_active", "Active", 7, "int",
            formula=zero("sku", 'IF({status}{r}="Active",1,0)'),
            hidden=True),

        # stock, pulled from the tracker so the catalogue can show it
        Col("on_hand", "In stock", 10, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.current]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            cf=bar_cf(),
            note="Live from the Inventory Tracker. You cannot type "
                 "here - stock is always calculated."),
        Col("available", "Available", 10, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.available]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            note="In stock, less what is already promised to a "
                 "confirmed order. This is the number to sell "
                 "against."),
        Col("stock_value", "Stock value", 12, "money",
            formula=zero("sku", 'ROUND({on_hand}{r}*'
                                '{avg_cost}{r},2)'),
            cf=money_cf()),
        Col("avg_cost", "Avg cost", 10, "money4",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Valuation & COGS.'
                                'avg_cost]],MATCH({sku}{r},'
                                '[[Inventory Valuation & COGS.sku]],'
                                '0))*1,{cost}{r})'),
            note="Weighted average cost. Falls back to the unit cost "
                 "you typed until the first purchase order is "
                 "received."),
        Col("units_sold", "Sold", 9, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Product Performance.units_sold]],'
                                'MATCH({sku}{r},'
                                '[[Product Performance.sku]],0))*1,0)'),
            hidden=True),
        Col("value_rank", "Rank", 8, "int",
            formula=rank_desc("stock_value", guard='{sku}{r}=""')
            .formula, hidden=True),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            note="The one column to scan. Everything else on this "
                 "sheet is reference; this is the bit that asks you "
                 "for something."),
    ]

    alert = _alert()
    for col in cols:
        if col.key == "alert":
            col.formula = alert

    return SheetSpec(
        name=NAME,
        title="Product & SKU Database",
        subtitle=("One row per stocked thing. A variant you count "
                  "separately is a separate SKU - that is the whole "
                  "rule."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("products", cfg),
        help_text=("Create the SKU here first, then everything else "
                   "in the workbook can point at it. Stock, cost and "
                   "value on this sheet are calculated - the only "
                   "stock figure you ever type is the opening one."),
        extra_notes=[
            "A duplicate SKU is the one mistake this workbook cannot "
            "work around: two rows sharing a code means two products "
            "sharing one stock figure, one cost and one profit line. "
            "The Dups column counts them and the alert turns red.",
            "Set a floor price on anything you discount. Tiered "
            "wholesale pricing, customer discounts and a tired "
            "Friday afternoon can combine into a sale below cost "
            "without anybody noticing.",
        ],
    )


def _alert() -> str:
    """Priority order: broken data, then money, then housekeeping."""
    return alert_chain("sku", [
        ('{dup_count}{r}>1',
         "Urgent - duplicate SKU, two rows share this code"),
        ('{name}{r}=""', "Add - product name"),
        ('AND({opening_qty}{r}>0,{opening_value}{r}="")', "Add - opening stock value"),
        ('{cost}{r}<=0', "Add - unit cost, nothing can be costed "
                         "without it"),
        ('{retail_price}{r}<=0', "Add - retail price"),
        ('{retail_price}{r}<{cost}{r}',
         "Urgent - retail price is below cost"),
        ('AND({min_price}{r}>0,{wholesale_price}{r}>0,'
         '{wholesale_price}{r}<{min_price}{r})',
         "Urgent - trade price is below your own floor price"),
        ('{status}{r}=""', "Add - product status"),
        ('{status}{r}="Active"', [
            ('{available}{r}<=0',
             "Action - active product, nothing available to sell"),
            ('{min_stock}{r}<=0',
             "Check - no minimum stock level set"),
            ('{available}{r}<={min_stock}{r}',
             "Order - below minimum stock level"),
        ], "OK"),
        ('{on_hand}{r}>0',
         "Check - not active but still holding stock"),
    ])
