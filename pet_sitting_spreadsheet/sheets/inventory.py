"""`Inventory` - pet supplies, stock levels, reorder alerts and value."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import alert_cf, blank, id_col

NAME = "Inventory"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("item", '"IT-"', digits=3, width=9),
        Col("item", "Item", 28, "text"),
        Col("category", "Category", 18, "text",
            validate=list_from("InventoryCategoryList")),
        Col("supplier", "Supplier", 20, "text"),
        Col("unit", "Unit", 10, "text"),
        Col("unit_cost", "Unit cost", 11, "money",
            validate=number_check(0, 100000)),
        Col("qty", "In stock", 10, "number1",
            validate=number_check(0, 100000)),
        Col("min_qty", "Minimum level", 10, "number1",
            validate=number_check(0, 100000),
            note="When stock drops to this level the item is flagged for "
                 "reorder on the Reminders tab."),
        Col("reorder", "Reorder qty", 10, "number1",
            validate=number_check(0, 100000)),
        Col("value", "Stock value", 12, "money",
            formula=blank("item",
                          'ROUND(IF({qty}{r}="",0,{qty}{r})'
                          '*IF({unit_cost}{r}="",0,{unit_cost}{r}),2)'),
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("stock_status", "Stock status", 14, "status",
            formula=blank("item",
                          'IF({qty}{r}="","Set stock level",'
                          'IF({qty}{r}<=0,"Out of stock",'
                          'IF({qty}{r}<=IF({min_qty}{r}="",0,'
                          '{min_qty}{r}),"Low - reorder","OK")))'),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Out of stock", "fmt": "bold_bad"},
                {"type": "text", "criteria": "containing", "value": "Low",
                 "fmt": "warn"},
                {"type": "text", "criteria": "containing", "value": "OK",
                 "fmt": "good"}]),
        Col("last_purchase", "Last purchased", 12, "date",
            validate=date_check()),
        Col("qty_purchased", "Qty last bought", 10, "number1",
            validate=number_check(0, 100000)),
        Col("purchase_cost", "Last purchase cost", 12, "money",
            formula=blank("item",
                          'ROUND(IF({qty_purchased}{r}="",0,'
                          '{qty_purchased}{r})*IF({unit_cost}{r}="",0,'
                          '{unit_cost}{r}),2)')),
        Col("expiry", "Expiry date", 12, "date", validate=date_check()),
        Col("expiry_alert", "Expiry status", 14, "status",
            formula=blank("expiry",
                          'IF({expiry}{r}<TODAY(),"EXPIRED",'
                          'IF({expiry}{r}-TODAY()<=ExpiryAlertDays,'
                          '"Use within "&TEXT({expiry}{r}-TODAY(),"0")'
                          '&" days","OK"))'),
            cf=alert_cf() + [{"type": "text", "criteria": "containing",
                              "value": "EXPIRED", "fmt": "bold_bad"},
                             {"type": "text", "criteria": "containing",
                              "value": "Use within", "fmt": "warn"}]),
        Col("used_month", "Used this month", 10, "number1",
            validate=number_check(0, 100000)),
        Col("notes", "Notes", 26, "wrap"),
        Col("alert", "Action needed", 22, "status",
            formula=blank(
                "item",
                'IF({stock_status}{r}="Out of stock",'
                '"Order now - out of stock",'
                'IF({stock_status}{r}="Low - reorder",'
                '"Reorder "&TEXT(IF({reorder}{r}="",0,{reorder}{r}),"0")'
                '&" "&{unit}{r},'
                'IF({expiry_alert}{r}="EXPIRED","Dispose - expired","OK")))'),
            cf=alert_cf() + [{"type": "text", "criteria": "containing",
                              "value": "Order now", "fmt": "bold_bad"},
                             {"type": "text", "criteria": "containing",
                              "value": "Reorder", "fmt": "warn"}]),
    ]

    return SheetSpec(
        name=NAME,
        title="Inventory & Pet Supplies",
        subtitle="Treats, waste bags, cleaning kit, first aid and "
                 "equipment - with low stock and expiry alerts.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
        samples=sample(cfg).inventory,
        help_text="Update the 'In stock' column after each supply run. "
                  "Anything at or below the minimum level is flagged.",
    )
