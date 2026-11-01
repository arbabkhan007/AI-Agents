"""18. Product Performance - which products deserve the shelf.

One row per SKU, mirroring the catalogue, ranking everything you sell
by the measures that actually decide what to reorder, what to
discount and what to stop making.

Revenue rank flatters big cheap sellers. Profit rank is better.
Profit per unit of stock held - the last column group on this sheet -
is better still, because it asks the only question a small business
with finite cash actually faces: of the money I have tied up in
stock, which lines are earning it back fastest?

Dead stock gets its own flag. A line that has not sold in four months
is not waiting for its moment; it is a shelf you are renting to
yourself.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from .common import (alert_cf, alert_chain, bar_cf, blank,
                     lookup_product, margin,
                     money_cf, rank_desc, scale_cf, status_cf, zero)

NAME = "Product Performance"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("sku", "SKU", 15, "id",
            formula='=IF(INDEX([[Product & SKU Database.sku]],'
                    'ROW()-4)="","",'
                    'INDEX([[Product & SKU Database.sku]],ROW()-4))'),
        Col("product", "Product", 24, "text",
            formula=lookup_product("name")),
        Col("category", "Category", 13, "text",
            formula=lookup_product("category")),
        Col("status", "Status", 11, "status",
            formula=lookup_product("status"), cf=status_cf()),

        # ---- volume -----------------------------------------------
        Col("units_retail", "Retail units", 11, "int",
            formula=zero("sku", 'SUMIFS('
                                '[[Retail Sales Tracker.qty]],'
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],'
                                '1)'),
            hidden=True),
        Col("units_wholesale", "Trade units", 11, "int",
            formula=zero("sku", 'SUMIFS([[Wholesale Orders.qty]],'
                                '[[Wholesale Orders.sku]],{sku}{r},'
                                '[[Wholesale Orders.is_shipped]],'
                                '1)'),
            hidden=True),
        Col("units_sold", "Units sold", 10, "int",
            formula=zero("sku", '{units_retail}{r}+'
                                '{units_wholesale}{r}'),
            cf=bar_cf()),
        Col("orders", "Orders", 8, "int",
            formula=zero("sku", 'COUNTIFS('
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],1)'
                                '+COUNTIFS([[Wholesale Orders.sku]],'
                                '{sku}{r},'
                                '[[Wholesale Orders.is_shipped]],1)'),
            hidden=True),

        # ---- money ------------------------------------------------
        Col("revenue_retail", "Retail revenue", 13, "money",
            formula=zero("sku", 'SUMIFS('
                                '[[Retail Sales Tracker.gross]],'
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],'
                                '1)'),
            hidden=True),
        Col("revenue_wholesale", "Trade revenue", 13, "money",
            formula=zero("sku", 'SUMIFS('
                                '[[Wholesale Orders.line_total]],'
                                '[[Wholesale Orders.sku]],{sku}{r},'
                                '[[Wholesale Orders.is_shipped]],'
                                '1)'),
            hidden=True),
        Col("revenue", "Revenue", 12, "money",
            formula=zero("sku", 'ROUND({revenue_retail}{r}+'
                                '{revenue_wholesale}{r},2)'),
            cf=money_cf()),
        Col("cogs", "COGS", 11, "money",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Valuation & COGS.'
                                'cogs]],MATCH({sku}{r},'
                                '[[Inventory Valuation & COGS.sku]],'
                                '0))*1,0)'),
            note="At weighted average cost, from the valuation "
                 "tab - the same method as everywhere else."),
        Col("fees", "Platform fees", 12, "money",
            formula=zero("sku", 'SUMIFS('
                                '[[Retail Sales Tracker.'
                                'platform_fee]],'
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],1)'
                                '+SUMIFS([[Retail Sales Tracker.'
                                'payment_fee]],'
                                '[[Retail Sales Tracker.sku]],'
                                '{sku}{r},'
                                '[[Retail Sales Tracker.is_sold]],'
                                '1)'),
            hidden=True,
            note="What the marketplaces and payment processors "
                 "took on this product's retail sales."),
        Col("returns_cost", "Returns cost", 12, "money",
            formula=zero("sku", 'SUMIFS('
                                '[[Returns & Damaged Goods.'
                                'profit_effect]],'
                                '[[Returns & Damaged Goods.sku]],'
                                '{sku}{r})'),
            hidden=True),
        Col("profit", "Profit", 12, "money",
            formula=zero("sku", 'ROUND({revenue}{r}-{cogs}{r}-'
                                '{fees}{r}-{returns_cost}{r},2)'),
            cf=money_cf(),
            note="Revenue less cost of goods, less what the "
                 "platforms took, less what the returns cost. "
                 "Operating expenses are not in here - they live on "
                 "the Profit Analysis tab, where they belong."),
        Col("gp_pct", "GP%", 8, "percent0",
            formula=blank("sku", margin("{profit}{r}",
                                        "{revenue}{r}")),
            cf=scale_cf()),
        Col("profit_per_unit", "Profit/unit", 11, "money",
            formula='=IF({sku}{r}="","",IF({units_sold}{r}<=0,"",'
                    'ROUND({profit}{r}/{units_sold}{r},2)))',
            note="What one more sale is worth to you. The honest "
                 "comparison between a cheap fast seller and an "
                 "expensive slow one."),

        # ---- rate and return on stock -----------------------------
        Col("daily_sales", "Sold/day", 9, "number1",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.daily_sales]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            hidden=True),
        Col("monthly_units", "Units/month", 11, "number1",
            formula=zero("sku", 'ROUND({daily_sales}{r}*30,1)'),
            note="Run rate over the sales window, not a count of "
                 "last month."),
        Col("stock_value", "Stock held", 12, "money",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Valuation & COGS.'
                                'stock_value]],MATCH({sku}{r},'
                                '[[Inventory Valuation & COGS.sku]],'
                                '0))*1,0)')),
        Col("return_on_stock", "Return on stock", 14, "percent0",
            formula='=IF({sku}{r}="","",IF({stock_value}{r}<=0,"",'
                    'ROUND({profit}{r}/{stock_value}{r},4)))',
            cf=scale_cf(),
            note="Profit earned per pound of stock held. The "
                 "sharpest single measure on this sheet, and the "
                 "one to sort by when cash is tight."),
        Col("turns", "Turns", 7, "number1",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Valuation & COGS.'
                                'turns]],MATCH({sku}{r},'
                                '[[Inventory Valuation & COGS.sku]],'
                                '0))*1,0)'),
            hidden=True),
        Col("last_sold_num", "Last sold (n)", 9, "number",
            formula=zero("sku",
                         'MAX(SUMPRODUCT(MAX(('
                         '[[Retail Sales Tracker.sku]]={sku}{r})*'
                         '[[Retail Sales Tracker.is_sold]]*'
                         '[[Retail Sales Tracker.date_num]])),'
                         'SUMPRODUCT(MAX(('
                         '[[Wholesale Orders.sku]]={sku}{r})*'
                         '[[Wholesale Orders.is_shipped]]*'
                         '[[Wholesale Orders.date_num]])))'),
            hidden=True),
        Col("last_sold", "Last sold", 11, "date",
            formula='=IF({sku}{r}="","",'
                    'IF({last_sold_num}{r}<=0,"",'
                    '{last_sold_num}{r}))'),
        Col("days_since_sale", "Days since", 10, "int",
            formula='=IF({sku}{r}="","",'
                    'IF({last_sold_num}{r}<=0,"",'
                    'TodayDate-{last_sold_num}{r}))',
            cf=[{"type": "cell", "criteria": ">", "value": 120,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 60,
                 "fmt": "warn"}]),

        # ---- ranking ----------------------------------------------
        rank_desc("revenue", guard='{sku}{r}=""', header="Rev rank"),
        rank_desc("profit", guard='{sku}{r}=""',
                  header="Profit rank"),
        Col("units_rank", "Unit rank", 9, "int",
            formula=blank("sku",
                          'COUNTIFS({units_sold_first}:'
                          '{units_sold_last},">"&'
                          '{units_sold}{r})+'
                          'COUNTIFS({units_sold_first}:'
                          '{units_sold}{r},{units_sold}{r})'),
            hidden=True),
        Col("revenue_share", "Share", 8, "percent0",
            formula=blank("sku", margin("{revenue}{r}",
                                        "TotalRevenue")),
            hidden=True),
        Col("band", "Performance", 13, "status",
            formula='=IF({sku}{r}="","",'
                    'IF({units_sold}{r}<=0,"No sales",'
                    'IF({profit}{r}<0,"Losing money",'
                    'IF({days_since_sale}{r}="","Review",'
                    'IF({days_since_sale}{r}>DeadStockDays,"Dead",'
                    'IF({profit_rank}{r}<=5,"Star",'
                    'IF({days_since_sale}{r}>SlowStockDays,"Slow",'
                    'IF({gp_pct}{r}="","Review",'
                    'IF({gp_pct}{r}<MinGP,"Thin margin",'
                    '"Steady")))))))))',
            cf=status_cf()),
        Col("is_dead", "Dead", 6, "int",
            formula=zero("sku", 'IF({band}{r}="Dead",1,0)'),
            hidden=True),
        Col("is_star", "Star", 6, "int",
            formula=zero("sku", 'IF({band}{r}="Star",1,0)'),
            hidden=True),

        Col("dead_key", "Dead key", 9, "number",
            formula=zero("sku",
                         'IF({stock_value}{r}<=0,0,'
                         'IF({units_sold}{r}=0,3000000,'
                         'IF({is_dead}{r}=1,2000000,'
                         'IF({band}{r}="Slow",1000000,0)))+'
                         'ROUND({stock_value}{r},0))'),
            hidden=True),
        Col("dead_rank", "Dead rank", 9, "int",
            formula=zero("sku",
                         'IF({dead_key}{r}<=0,0,'
                         'COUNTIFS({dead_key_first}:{dead_key_last},'
                         '">"&{dead_key}{r})+'
                         'COUNTIFS({dead_key_first}:{dead_key}{r},'
                         '{dead_key}{r}))'),
            hidden=True,
            note="Stock that is not selling, most expensive first. "
                 "What the Dashboard lists as not earning its "
                 "shelf."),
        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Product Performance",
        subtitle=("Units, revenue, profit and return on the stock "
                  "held - ranked, so the decisions make themselves."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text=("Everything here is calculated from your sales. "
                   "Sort by Return on stock when cash is tight, by "
                   "Profit rank when you are deciding what to "
                   "promote, and by Days since when you are "
                   "deciding what to clear."),
        extra_notes=[
            "Profit on this sheet is after cost of goods, "
            "marketplace fees and returns, but before your "
            "operating expenses. That is deliberate: rent and "
            "software are not caused by any one SKU, and spreading "
            "them across products invents a precision that does not "
            "exist. Business-level profit is on the Profit Analysis "
            "tab.",
            "A Dead line with stock still in it is worth clearing "
            "even at cost. The money is not in the product, it is "
            "in the shelf space and the cash - and both can be "
            "spent on something that sells.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{status}{r}="Discontinued"', "OK"),
        ('AND({units_sold}{r}=0,{stock_value}{r}>0)',
         "Action - holding stock that has never sold"),
        ('{units_sold}{r}=0', "OK"),
        ('{profit}{r}<0',
         "Urgent - this product loses money on every pass"),
        ('AND({gp_pct}{r}<>"",{gp_pct}{r}<MinGP)',
         "Action - margin below your minimum, reprice or drop it"),
        ('{is_dead}{r}=1',
         "Action - no sales in months, clear the stock"),
        ('AND({band}{r}="Slow",{stock_value}{r}>0)',
         "Check - slowing down, think about a promotion"),
        ('AND({is_star}{r}=1,{days_since_sale}{r}<>"")',
         "OK"),
        ('AND({return_on_stock}{r}<>"",{return_on_stock}{r}<0.2,'
         '{stock_value}{r}>0)',
         "Check - poor return on the cash tied up here"),
    ])
