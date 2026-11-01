"""20. Profit Analysis - the business, month by month.

Product Performance tells you which lines earn their keep. This sheet
tells you whether the business does, which is a different question
and the one that pays your wages.

The structure is the one an accountant would recognise:

    revenue (retail + wholesale, net of what platforms took)
    less  cost of goods sold, at weighted average cost
    =     gross profit
    less  operating expenses, with stock purchases excluded
    =     net profit

Stock purchases are not in the expense line. Buying inventory moves
cash into an asset; it becomes a cost when the thing sells, through
COGS. Counting it in both places is the single commonest way a
spreadsheet reports a loss in a month with a big delivery and a
fortune in the month it sells through.

Twelve months of rows, generated for you.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from .common import (alert_cf, alert_chain, blank, margin, money_cf,
                     scale_cf, status_cf, target_cf, zero)

NAME = "Profit Analysis"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("month", "Month", 11, "text",
            formula='=IF(ROW()-4>12,"",TEXT(DATE(ReportYear,'
                    'ROW()-4,1),"yyyy-mm"))',
            note="Twelve rows, one per month of the reporting year "
                 "set on Settings. Nothing to type."),
        Col("month_name", "Name", 11, "text",
            formula='=IF({month}{r}="","",TEXT(DATE(ReportYear,'
                    'ROW()-4,1),"mmmm"))'),
        Col("start_num", "From", 9, "number",
            formula='=IF({month}{r}="","",DATE(ReportYear,'
                    'ROW()-4,1))', hidden=True),
        Col("end_num", "To", 9, "number",
            formula='=IF({month}{r}="","",DATE(ReportYear,'
                    'ROW()-3,1)-1)', hidden=True),

        # ---- revenue ----------------------------------------------
        Col("retail_revenue", "Retail", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Retail Sales Tracker.gross]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)')),
        Col("wholesale_revenue", "Wholesale", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Wholesale Orders.line_total]],'
                                  '[[Wholesale Orders.ship_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Wholesale Orders.ship_num]],'
                                  '"<="&{end_num}{r},'
                                  '[[Wholesale Orders.is_shipped]],'
                                  '1)')),
        Col("shipping_income", "Shipping in", 11, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Retail Sales Tracker.'
                                  'shipping_charged]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)+SUMIFS('
                                  '[[Wholesale Orders.'
                                  'shipping_charge]],'
                                  '[[Wholesale Orders.ship_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Wholesale Orders.ship_num]],'
                                  '"<="&{end_num}{r},'
                                  '[[Wholesale Orders.is_shipped]],'
                                  '1)'),
            hidden=True),
        Col("revenue", "Total revenue", 13, "money",
            formula=zero("month", 'ROUND({retail_revenue}{r}+'
                                  '{wholesale_revenue}{r}+'
                                  '{shipping_income}{r},2)'),
            cf=money_cf()),

        # ---- cost of sales ----------------------------------------
        Col("cogs", "COGS", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Retail Sales Tracker.cogs]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)+SUMIFS('
                                  '[[Wholesale Orders.line_cost]],'
                                  '[[Wholesale Orders.ship_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Wholesale Orders.ship_num]],'
                                  '"<="&{end_num}{r},'
                                  '[[Wholesale Orders.is_shipped]],'
                                  '1)'),
            note="Units sold at weighted average cost. Not what you "
                 "spent on stock this month - what the things you "
                 "sold this month cost you."),
        Col("fees", "Platform fees", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Retail Sales Tracker.'
                                  'platform_fee]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)+SUMIFS('
                                  '[[Retail Sales Tracker.'
                                  'payment_fee]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)')),
        Col("shipping_cost", "Shipping out", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Retail Sales Tracker.'
                                  'shipping_cost]],'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)'),
            hidden=True),
        Col("gross_profit", "Gross profit", 13, "money",
            formula=zero("month", 'ROUND({revenue}{r}-{cogs}{r}-'
                                  '{fees}{r}-'
                                  '{shipping_cost}{r},2)'),
            cf=money_cf()),
        Col("gross_margin", "GP%", 8, "percent0",
            formula=blank("month", margin("{gross_profit}{r}",
                                          "{revenue}{r}")),
            cf=target_cf("TargetMargin")),

        # ---- running the business ---------------------------------
        Col("expenses", "Operating costs", 14, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Expense Tracker.operating]],'
                                  '[[Expense Tracker.date_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Expense Tracker.date_num]],'
                                  '"<="&{end_num}{r})'),
            note="Rent, software, advertising, your accountant. "
                 "Stock purchases are excluded - they are already "
                 "in COGS."),
        Col("returns_cost", "Returns", 11, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Returns & Damaged Goods.'
                                  'profit_effect]],'
                                  '[[Returns & Damaged Goods.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Returns & Damaged Goods.'
                                  'date_num]],"<="&{end_num}{r})'),
            hidden=True),
        Col("write_offs", "Write-offs", 11, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Stock Movement Log.value]],'
                                  '[[Stock Movement Log.date_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Stock Movement Log.date_num]],'
                                  '"<="&{end_num}{r},'
                                  '[[Stock Movement Log.'
                                  'is_writeoff]],1)'),
            hidden=True,
            note="Damage and loss at cost. A real expense, and one "
                 "most spreadsheets never show."),
        Col("net_profit", "Net profit", 13, "money",
            formula=zero("month", 'ROUND({gross_profit}{r}-'
                                  '{expenses}{r}-'
                                  '{returns_cost}{r}-'
                                  '{write_offs}{r},2)'),
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bold_good"}]),
        Col("net_margin", "Net %", 8, "percent0",
            formula=blank("month", margin("{net_profit}{r}",
                                          "{revenue}{r}")),
            cf=scale_cf()),

        # ---- cash and stock ---------------------------------------
        Col("stock_spend", "Stock bought", 12, "money",
            formula=zero("month", 'SUMIFS('
                                  '[[Purchase Orders.'
                                  'received_value]],'
                                  '[[Purchase Orders.received_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Purchase Orders.received_num]],'
                                  '"<="&{end_num}{r})'),
            note="Cash that went into stock this month. Shown "
                 "separately from profit on purpose: a big delivery "
                 "is not a bad month, it is a full shelf."),
        Col("cash_effect", "Cash effect", 12, "money",
            formula=zero("month", 'ROUND({net_profit}{r}+'
                                  '{cogs}{r}-{stock_spend}{r},2)'),
            cf=[{"type": "cell", "criteria": "<", "value": 0,
                 "fmt": "bad"}],
            note="Roughly what the month did to your bank balance: "
                 "profit, with the stock you sold added back and "
                 "the stock you bought taken off. Profitable months "
                 "can still be cash-negative, and this is where "
                 "that shows."),
        Col("orders", "Orders", 8, "int",
            formula=zero("month", 'COUNTIFS('
                                  '[[Retail Sales Tracker.'
                                  'date_num]],">="&{start_num}{r},'
                                  '[[Retail Sales Tracker.'
                                  'date_num]],"<="&{end_num}{r},'
                                  '[[Retail Sales Tracker.is_sold]],'
                                  '1)+SUMIFS('
                                  '[[Wholesale Orders.'
                                  'is_first_line]],'
                                  '[[Wholesale Orders.ship_num]],'
                                  '">="&{start_num}{r},'
                                  '[[Wholesale Orders.ship_num]],'
                                  '"<="&{end_num}{r},'
                                  '[[Wholesale Orders.is_shipped]],'
                                  '1)'),
            hidden=True),
        Col("avg_order", "Avg order", 11, "money",
            formula='=IF({month}{r}="","",IF({orders}{r}<=0,"",'
                    'ROUND({revenue}{r}/{orders}{r},2)))',
            hidden=True),
        Col("vs_target", "vs target", 10, "percent0",
            formula='=IF({month}{r}="","",'
                    'IF(MonthlyTarget<=0,"",'
                    'ROUND({revenue}{r}/MonthlyTarget-1,4)))',
            cf=[{"type": "cell", "criteria": ">=", "value": 0,
                 "fmt": "good"},
                {"type": "cell", "criteria": "<", "value": -0.15,
                 "fmt": "bad"}]),
        Col("vs_prev", "vs last month", 12, "percent0",
            formula='=IF({month}{r}="","",IF(ROW()-4=1,"",'
                    'IF({revenue}{r_prev}<=0,"",'
                    'ROUND({revenue}{r}/{revenue}{r_prev}-1,4))))',
            cf=[{"type": "cell", "criteria": "<", "value": -0.2,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.2,
                 "fmt": "good"}]),
        Col("band", "Month", 12, "status",
            formula='=IF({month}{r}="","",'
                    'IF({revenue}{r}<=0,"No trading",'
                    'IF({net_profit}{r}<0,"Loss",'
                    'IF({net_margin}{r}="","Review",'
                    'IF({net_margin}{r}>=0.2,"Strong",'
                    'IF({net_margin}{r}>=0.08,"Steady",'
                    '"Thin"))))))',
            cf=status_cf()),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Profit Analysis",
        subtitle=("Revenue, cost of goods, gross profit, operating "
                  "costs, net profit. Twelve months, calculated."),
        columns=cols,
        rows=14,
        freeze_cols=2,
        help_text=("Nothing to fill in. Change the reporting year "
                   "on Settings and all twelve rows follow. Revenue "
                   "is recognised when goods ship, which is why a "
                   "confirmed-but-unshipped order is not in here."),
        extra_notes=[
            "Cash effect is the column to read in a month that "
            "looks profitable but felt tight. Profit counts the "
            "cost of what you sold; cash counts what you paid for "
            "what you bought. A month with a big delivery and a "
            "slow start will show healthy profit and ugly cash, "
            "and both numbers are correct.",
            "Wholesale revenue is counted on the shipping date, "
            "not the order date, so an order confirmed in March "
            "and shipped in April belongs to April. Reserved stock "
            "has not earned anything yet.",
        ],
    )


def _alert() -> str:
    return alert_chain("month", [
        ('{revenue}{r}<=0', "OK"),
        ('{net_profit}{r}<0',
         "Urgent - the business lost money this month"),
        ('AND({gross_margin}{r}<>"",{gross_margin}{r}<MinGP)',
         "Action - gross margin below your minimum"),
        ('{cash_effect}{r}<0',
         "Check - profitable but cash went out, stock buying was "
         "heavy"),
        ('AND({net_margin}{r}<>"",{net_margin}{r}<0.05)',
         "Check - very thin net margin"),
        ('AND({vs_prev}{r}<>"",{vs_prev}{r}<-0.25)',
         "Check - revenue well down on last month"),
        ('AND({vs_target}{r}<>"",{vs_target}{r}<-0.15)',
         "Check - behind the monthly revenue target"),
        ('{expenses}{r}>{gross_profit}{r}',
         "Action - running costs ate the whole gross profit"),
    ])
