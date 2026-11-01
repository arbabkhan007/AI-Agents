"""12. Retail Sales Tracker - everything you sell one at a time.

Marketplace orders, your own website, the shop counter, a craft fair.
One row per item sold, because a two-item order that needs its stock
split across two SKUs is two rows.

Marketplace fees are taken seriously here. A twenty pound candle sold
on a platform charging 6.5% plus payment processing at 2.9% and 30p
is not a twenty pound sale, and the net profit column is the only one
telling you the truth. Fees are calculated from the rates on Settings
and can be overridden per row when a platform changes its mind.

Nothing on this tab syncs with anything. You type your sales in or
paste them from a marketplace export; the workbook does the rest.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, date_num_col,
                     is_sold_retail, lookup_product,
                     lookup_product_num_zero, margin, month_col,
                     scale_cf, seq_num_col, sku_col, status_cf,
                     weekday_col, zero)
from ..writer import date_check, list_from, number_check

NAME = "Retail Sales Tracker"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("sale_id", "Sale ID", 11, "id",
            note="Your own reference, or the marketplace order "
                 "number. Repeat it if one order covers two items."),
        Col("date", "Date", 11, "date", validate=date_check()),
        Col("channel", "Channel", 13, "text",
            validate=list_from("ChannelList"),
            note="Where it sold. Drives the fee rate and the channel "
                 "breakdown on the reports."),
        sku_col(),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("qty", "Qty", 7, "int",
            validate=number_check(0, 100000)),
        Col("unit_price", "Unit price", 11, "money",
            validate=number_check(0, 1000000),
            note="What they actually paid, after any sale price or "
                 "coupon. Leave blank to use the product's retail "
                 "price."),
        Col("price_used", "Price used", 11, "money",
            formula=zero("sale_id",
                         'IF({unit_price}{r}>0,{unit_price}{r},'
                         f'{lookup_product_num_zero("retail_price")[1:]})'),
            hidden=True),
        Col("gross", "Gross sale", 11, "money",
            formula=zero("sale_id", 'ROUND({qty}{r}*'
                                    '{price_used}{r},2)')),
        Col("shipping_charged", "Ship charged", 12, "money",
            validate=number_check(0, 100000),
            note="What the customer paid for postage."),
        Col("shipping_cost", "Ship cost", 10, "money",
            validate=number_check(0, 100000),
            note="What the postage actually cost you. The gap "
                 "between these two columns is where small sellers "
                 "quietly lose money."),
        Col("discount", "Discount", 10, "money",
            validate=number_check(0, 1000000),
            note="Coupons and sale reductions, in money."),

        # ---- what the platform keeps ------------------------------
        Col("fee_rate", "Fee rate", 9, "percent0",
            formula=zero("sale_id",
                         'IFERROR(INDEX(ChannelFeeRates,'
                         'MATCH({channel}{r},ChannelList,0)),'
                         'MarketplaceFeePct)'),
            hidden=True),
        Col("platform_fee", "Platform fee", 11, "money",
            formula=zero("sale_id",
                         'IF({fee_override}{r}>0,{fee_override}{r},'
                         'ROUND(({gross}{r}+'
                         '{shipping_charged}{r}-{discount}{r})*'
                         '{fee_rate}{r},2))'),
            note="Taken from the channel's rate on Settings. Put a "
                 "number in Fee override to use the real figure off "
                 "a statement instead."),
        Col("fee_override", "Fee override", 11, "money",
            validate=number_check(0, 100000),
            note="The actual fee from the platform's statement, "
                 "when you have it. Beats the estimate."),
        Col("payment_fee", "Payment fee", 11, "money",
            formula=zero("sale_id",
                         'ROUND(({gross}{r}+'
                         '{shipping_charged}{r}-{discount}{r})*'
                         'PaymentFeePct+PaymentFeeFixed,2)'),
            note="Card and payment processing, from the rates on "
                 "Settings."),
        Col("packaging", "Packaging", 10, "money",
            formula=zero("sale_id", 'PackagingPerOrder'),
            hidden=True),
        Col("net_revenue", "Net revenue", 12, "money",
            formula=zero("sale_id",
                         'ROUND({gross}{r}+{shipping_charged}{r}-'
                         '{discount}{r}-{platform_fee}{r}-'
                         '{payment_fee}{r},2)'),
            note="What reaches your bank: the sale and the postage "
                 "charged, less discounts and everything the "
                 "platform takes."),

        # ---- what it cost you -------------------------------------
        Col("unit_cost", "Unit cost", 10, "money4",
            formula=zero("sale_id", 'IFERROR(INDEX('
                                    '[[Inventory Tracker.avg_cost]],'
                                    'MATCH({sku}{r},'
                                    '[[Inventory Tracker.sku]],0))*1,'
                                    f'{lookup_product_num_zero("cost")[1:]})'),
            hidden=True),
        Col("cogs", "COGS", 10, "money",
            formula=zero("sale_id", 'ROUND({qty}{r}*'
                                    '{unit_cost}{r},2)'),
            note="Cost of goods sold at weighted average cost - the "
                 "same method used everywhere else in the "
                 "workbook."),
        Col("profit", "Net profit", 11, "money",
            formula=zero("sale_id",
                         'ROUND({net_revenue}{r}-{cogs}{r}-'
                         '{shipping_cost}{r}-{packaging}{r},2)'),
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "good"}],
            note="After the platform, the postage, the packaging "
                 "and the stock. This is the number that is "
                 "actually yours."),
        Col("margin", "Margin", 8, "percent0",
            formula=blank("sale_id", margin("{profit}{r}",
                                            "{gross}{r}")),
            cf=scale_cf()),

        # ---- fulfilment -------------------------------------------
        Col("status", "Status", 12, "status",
            validate=list_from("SaleStatusList"), cf=status_cf(),
            note="Stock comes off when this reaches Shipped, "
                 "Delivered or Collected."),
        Col("customer", "Customer", 18, "text",
            note="A name or a marketplace handle. Nothing more is "
                 "needed here, and nothing more should be kept."),
        Col("location", "Sold from", 11, "text",
            validate=list_from("LocationList")),
        Col("notes", "Notes", 22, "wrap"),

        Col("is_sold", "Sold?", 7, "int",
            formula=zero("sale_id",
                         f'IF({is_sold_retail("{status}{r}")},1,0)'),
            hidden=True,
            note="The flag the Inventory Tracker reads. A pending "
                 "or cancelled sale does not move stock."),
        Col("is_loss", "Loss", 6, "int",
            formula=zero("sale_id", 'IF({is_sold}{r}=0,0,'
                                    'IF({profit}{r}<0,1,0))'),
            hidden=True),
        Col("ship_gap", "Ship gap", 9, "money",
            formula=blank("sale_id",
                          'ROUND({shipping_charged}{r}-'
                          '{shipping_cost}{r},2)'),
            cf=[{"type": "cell", "criteria": "<", "value": -0.004,
                 "fmt": "bad"}],
            hidden=True),

        month_col("date"),
        weekday_col("date"),
        date_num_col("date", "date_num"),
        seq_num_col("sale_id"),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Retail Sales Tracker",
        subtitle=("Every single sale, with what the platform took "
                  "out of it. Typed or pasted in - nothing here "
                  "syncs with a marketplace."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("retail", cfg),
        help_text=("One row per item sold. Fees come from the rates "
                   "you set on Settings, so a channel that puts its "
                   "commission up costs you exactly one cell to "
                   "correct."),
        extra_notes=[
            "There is no marketplace connection in this workbook "
            "and there is not going to be one. Export your orders "
            "and paste the columns in, or type them as they come. "
            "Everything downstream - stock, COGS, product profit - "
            "runs off what is on this sheet.",
            "Ship charged against Ship cost is worth a monthly "
            "glance. Free postage over a threshold is a marketing "
            "decision; free postage by accident, on a heavy item, "
            "is just an expensive habit.",
        ],
    )


def _alert() -> str:
    return alert_chain("sale_id", [
        ('{status}{r}="Cancelled"', "OK"),
        ('{sku}{r}=""', "Add - which product sold"),
        ('{date}{r}=""', "Add - sale date"),
        ('{qty}{r}<=0', "Add - quantity"),
        ('{channel}{r}=""', "Add - which channel it sold on"),
        ('{price_used}{r}<=0',
         "Add - price, the product has no retail price either"),
        ('{status}{r}=""', "Add - status"),
        ('AND({is_sold}{r}=1,{profit}{r}<0)',
         "Loss - this sale lost money once fees and postage came "
         "off"),
        ('AND({is_sold}{r}=1,{cogs}{r}<=0)',
         "Check - no cost recorded for this product"),
        ('AND({shipping_charged}{r}>0,{shipping_cost}{r}<=0)',
         "Add - what the postage actually cost you"),
        ('{ship_gap}{r}<-ShipGapTolerance',
         "Check - postage cost well over what you charged"),
        ('AND({margin}{r}<>"",{margin}{r}<MinGP,{is_sold}{r}=1)',
         "Check - margin under your minimum"),
        ('{date}{r}>TodayDate', "Check - dated in the future"),
    ])
