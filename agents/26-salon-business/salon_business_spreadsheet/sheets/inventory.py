"""13 Product Inventory - stock on hand, value and reorder alerts."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, date_check, list_from, number_check
from .. import sample_data

NAME = "13 Product Inventory"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="13  Product Inventory",
        subtitle="Retail and backbar stock: receipts from purchases, "
                 "units sold from sales, on-hand and reorder alerts.",
        tab_color="#B98A2F",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="On hand = opening + received - used in services - sold "
                  "- wasted + adjustments. Received comes from tab 14 and "
                  "sold from tab 6, so day-to-day you only type the "
                  "occasional adjustment.",
        columns=[
            Col("id", "Prod ID", 9, "id",
                formula='="P-"&TEXT(ROW()-{first}+1,"000")'),
            Col("sku", "SKU / barcode", 14, "text"),
            Col("name", "Product", 30, "text",
                note="The exact name retail sales rows use on tab 6."),
            Col("category", "Type", 10, "flag",
                validate=list_from("ListProdCats")),
            Col("supplier", "Supplier", 20, "text",
                validate=list_from("SupplierNames")),
            Col("unit_cost", "Unit cost", 10, "money",
                validate=number_check(0, 100000)),
            Col("retail", "Retail price", 11, "money",
                validate=number_check(0, 100000)),
            Col("taxable", "Taxable", 8, "flag",
                validate=list_from("ListConsent")),
            Col("opening", "Opening", 8, "int",
                validate=number_check(0, 9999, False)),
            Col("received", "Received", 9, "int",
                formula='IF({name}{r}="","",SUMIFS(PurchQty,PurchProduct,'
                        '{name}{r},PurchStatus,"Received"))'),
            Col("used", "Used in services", 10, "int",
                validate=number_check(0, 9999, False),
                note="Backbar units consumed at the chair."),
            Col("sold", "Retail sold", 9, "int",
                formula='IF({name}{r}="","",SUMIFS(SalesQty,SalesItem,'
                        '{name}{r},SalesType,"Retail"))'),
            Col("wasted", "Damaged / wasted", 10, "int",
                validate=number_check(0, 9999, False)),
            Col("adjusted", "Adjustments", 10, "int",
                validate=number_check(-9999, 9999, False),
                note="Stocktake corrections, plus or minus."),
            Col("on_hand", "On hand", 9, "int",
                formula='IF({name}{r}="","",N({opening}{r})'
                        '+N({received}{r})-N({used}{r})-N({sold}{r})'
                        '-N({wasted}{r})+N({adjusted}{r}))'),
            Col("min_level", "Min level", 9, "int",
                validate=number_check(0, 9999, False)),
            Col("low", "Reorder", 10, "status",
                formula='IF(OR({name}{r}="",{on_hand}{r}=""),"",IF('
                        '{on_hand}{r}<=N({min_level}{r}),"REORDER",""))',
                cf=[cf_text("REORDER", "bad")]),
            Col("value", "Stock value", 11, "money",
                formula='IF({on_hand}{r}="","",ROUND(N({on_hand}{r})'
                        '*N({unit_cost}{r}),2))'),
            Col("expiry", "Expiry", 11, "date", validate=date_check()),
            Col("batch", "Batch", 12, "text"),
            Col("notes", "Notes", 26, "wrap"),
        ],
        samples=sample_data.inventory_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "REORDER appears the moment on-hand touches the minimum - "
            "filter the column for your shopping list.",
            "Stock value is at cost; the dashboard carries it as money "
            "sitting on the shelves.",
        ],
    )
