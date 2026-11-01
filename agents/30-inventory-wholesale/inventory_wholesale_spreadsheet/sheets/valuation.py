"""14. Inventory Valuation & COGS - what the stock is worth, one way.

This workbook uses WEIGHTED AVERAGE COST. Not FIFO, not LIFO, not
specific identification, and never two of them in the same sum. The
calculation is on this sheet in full, one column per term, so you can
follow it rather than trust it:

    average cost = (opening value + value received)
                   / (opening units + units received)

Everything else in the workbook - stock value, cost of goods sold,
product profit, the margin on a wholesale line - reads that one
number. That is the point of picking a method and sticking to it.
Mixing methods is the single most reliable way to produce a set of
inventory figures that cannot be reconciled with anything, including
themselves.

If your accountant needs FIFO, tell them which method this is before
you hand the file over.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from .common import (alert_cf, alert_chain, blank, lookup_product,
                     lookup_product_num_zero, margin, money_cf,
                     received_qty, scale_cf, sold_qty, status_cf,
                     sum_by_sku, weighted_average_cost, zero)

NAME = "Inventory Valuation & COGS"


def spec(cfg: Config) -> SheetSpec:
    sku = "{sku}{r}"

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
            formula=lookup_product("status"), cf=status_cf(),
            hidden=True),

        # ---- the weighted average, term by term -------------------
        Col("opening_qty", "Opening units", 12, "int",
            formula=lookup_product_num_zero("opening_qty")),
        Col("opening_value", "Opening value", 13, "money",
            formula=lookup_product_num_zero("opening_value")),
        Col("received_qty", "Units received", 13, "int",
            formula=zero("sku", received_qty(sku))),
        Col("received_value", "Value received", 13, "money",
            formula=zero("sku", sum_by_sku("Purchase Orders",
                                           "received_value", sku)),
            note="At landed cost - goods plus freight - which is "
                 "why carriage belongs on the purchase order line."),
        Col("total_qty", "Units in", 10, "int",
            formula=zero("sku", '{opening_qty}{r}+'
                                '{received_qty}{r}'),
            hidden=True),
        Col("total_value", "Value in", 12, "money",
            formula=zero("sku", 'ROUND({opening_value}{r}+'
                                '{received_value}{r},2)'),
            hidden=True),
        Col("avg_cost", "Average cost", 12, "money4",
            formula=zero("sku", weighted_average_cost(sku)),
            note="Value in divided by units in. Falls back to the "
                 "cost on the product record until the first "
                 "purchase order is received. THIS is the number "
                 "the rest of the workbook costs everything at."),
        Col("book_cost", "Standard cost", 12, "money",
            formula=lookup_product_num_zero("cost"), hidden=True),
        Col("cost_drift", "Drift", 9, "percent0",
            formula='=IF({sku}{r}="","",IF({book_cost}{r}<=0,"",'
                    'ROUND({avg_cost}{r}/{book_cost}{r}-1,4)))',
            cf=[{"type": "cell", "criteria": ">", "value": 0.1,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.03,
                 "fmt": "warn"}],
            note="Real average cost against the standard cost you "
                 "typed. Drifting up means your prices are built on "
                 "a cost that no longer exists."),

        # ---- what is left -----------------------------------------
        Col("units_sold", "Units sold", 10, "int",
            formula=zero("sku", sold_qty(sku))),
        Col("on_hand", "Units held", 10, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.current]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)')),
        Col("stock_value", "Stock at cost", 13, "money",
            formula=zero("sku", 'ROUND({on_hand}{r}*'
                                '{avg_cost}{r},2)'),
            cf=money_cf(),
            note="Your inventory valuation for this line. Add the "
                 "column up for the balance sheet figure."),
        Col("cogs", "COGS", 12, "money",
            formula=zero("sku", 'ROUND({units_sold}{r}*'
                                '{avg_cost}{r},2)'),
            note="Units sold at weighted average cost. The same "
                 "number the Profit Analysis tab uses."),
        Col("revenue", "Revenue", 12, "money",
            formula=zero("sku",
                         'SUMIFS([[Wholesale Orders.line_total]],'
                         '[[Wholesale Orders.sku]],{sku}{r},'
                         '[[Wholesale Orders.is_shipped]],1)+'
                         'SUMIFS([[Retail Sales Tracker.gross]],'
                         '[[Retail Sales Tracker.sku]],{sku}{r},'
                         '[[Retail Sales Tracker.is_sold]],1)')),
        Col("gross_profit", "Gross profit", 12, "money",
            formula=zero("sku", 'ROUND({revenue}{r}-{cogs}{r},2)'),
            cf=money_cf()),
        Col("gp_pct", "GP%", 8, "percent0",
            formula=blank("sku", margin("{gross_profit}{r}",
                                        "{revenue}{r}")),
            cf=scale_cf()),

        # ---- losses and tied-up cash ------------------------------
        Col("write_offs", "Written off", 11, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.damaged]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)')),
        Col("writeoff_value", "Write-off value", 13, "money",
            formula=zero("sku", 'ROUND({write_offs}{r}*'
                                '{avg_cost}{r},2)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}],
            note="Damage, loss and unsellable returns, at cost. "
                 "This is a real expense and most spreadsheets "
                 "never show it."),
        Col("shrinkage", "Shrinkage", 9, "percent0",
            formula='=IF({sku}{r}="","",'
                    'IF({total_value}{r}<=0,"",'
                    'ROUND({writeoff_value}{r}/'
                    '{total_value}{r},4)))',
            cf=[{"type": "cell", "criteria": ">", "value": 0.03,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.01,
                 "fmt": "warn"}],
            note="Written off as a share of everything that came "
                 "in. Over 2% on a non-fragile line is worth "
                 "investigating."),
        Col("turns", "Stock turns", 11, "number1",
            formula='=IF({sku}{r}="","",IF({stock_value}{r}<=0,"",'
                    'ROUND({cogs}{r}/{stock_value}{r},1)))',
            cf=[{"type": "cell", "criteria": "<", "value": 1,
                 "fmt": "warn"}],
            note="How many times the stock has turned over. Low "
                 "means cash sitting on a shelf; very high means "
                 "you keep running out."),
        Col("value_share", "Share of value", 12, "percent0",
            formula=blank("sku", margin("{stock_value}{r}",
                                        "TotalStockValue")),
            cf=scale_cf(), hidden=True),
        Col("abc_class", "ABC", 6, "text",
            formula='=IF({sku}{r}="","",'
                    'IF({stock_value}{r}<=0,"C",'
                    'IF({value_share}{r}="","C",'
                    'IF({value_share}{r}>=0.05,"A",'
                    'IF({value_share}{r}>=0.01,"B","C")))))',
            cf=[{"type": "text", "criteria": "containing",
                 "value": "A", "fmt": "info"}],
            note="A lines hold most of your money and deserve "
                 "counting often. C lines can be counted once a "
                 "year without anybody noticing."),
        Col("dead_value", "Dead stock", 11, "money",
            formula=zero("sku",
                         'IF(IFERROR(INDEX('
                         '[[Inventory Tracker.is_dead]],'
                         'MATCH({sku}{r},'
                         '[[Inventory Tracker.sku]],0))*1,0)=1,'
                         '{stock_value}{r},0)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"}],
            hidden=True),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Inventory Valuation & COGS",
        subtitle=("Weighted average cost, shown term by term. One "
                  "method, used everywhere, with no exceptions."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text=("Nothing to fill in. This sheet exists so that "
                   "the number every other tab costs things at can "
                   "be checked by hand, which is what an accountant "
                   "will want to do."),
        extra_notes=[
            "Weighted average cost: (opening value + value "
            "received) divided by (opening units + units received). "
            "Received value is at landed cost, so freight and duty "
            "are in the stock valuation where they belong.",
            "Stock turns and the ABC class together tell you where "
            "to spend your counting time. A lines - the top few per "
            "cent of value - should be counted monthly; C lines "
            "once a year is plenty.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{total_qty}{r}<=0', [
            ('{book_cost}{r}<=0',
             "Add - no cost anywhere for this product"),
        ], "OK"),
        ('{avg_cost}{r}<=0',
         "Urgent - no average cost, every profit figure for this "
         "line is wrong"),
        ('{on_hand}{r}<0',
         "Urgent - negative stock, something was sold that was "
         "never received"),
        ('AND({revenue}{r}>0,{gp_pct}{r}<>"",{gp_pct}{r}<0)',
         "Loss - sold below cost over the period"),
        ('AND({shrinkage}{r}<>"",{shrinkage}{r}>0.03)',
         "Action - heavy write-offs on this line"),
        ('AND({cost_drift}{r}<>"",{cost_drift}{r}>0.1)',
         "Action - real cost is well above standard, reprice it"),
        ('{dead_value}{r}>0',
         "Check - cash tied up in stock that is not selling"),
        ('AND({stock_value}{r}>0,{turns}{r}<>"",{turns}{r}<1)',
         "Check - slow turning stock"),
        ('AND({abc_class}{r}="A",{on_hand}{r}>0)',
         "OK"),
    ])
