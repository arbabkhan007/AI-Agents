"""14 Suppliers & Purchases - directory plus the purchase order register."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import date_check, list_from, number_check
from .. import sample_data

NAME = "14 Suppliers & Purchases"

#: supplier directory block geometry (used by names.py)
SUP_FIRST_ROW = 0   # set in decorate; names.py reads the constant below
SUPPLIER_ROWS = 12


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="14  Suppliers & Purchases",
        subtitle="Supplier directory and the purchase order register that "
                 "feeds stock received on tab 13.",
        tab_color="#6D2E4F",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="Log a purchase order when you raise it and set the "
                  "status to Received when it lands - inventory picks the "
                  "quantity up automatically.",
        columns=[
            Col("id", "PO ID", 10, "id",
                formula='="PO-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Raised", 12, "date", validate=date_check()),
            Col("po", "PO number", 13, "text"),
            Col("supplier", "Supplier", 22, "text",
                validate=list_from("SupplierNames")),
            Col("product", "Product", 28, "text",
                validate=list_from("ProductNames")),
            Col("qty", "Qty", 7, "int", validate=number_check(0, 9999, False)),
            Col("unit_cost", "Unit cost", 10, "money",
                validate=number_check(0, 100000)),
            Col("total", "Total", 11, "money",
                formula='IF({qty}{r}="","",ROUND(N({qty}{r})'
                        '*N({unit_cost}{r}),2))'),
            Col("status", "Status", 11, "status",
                validate=list_from("ListPurchStatus"),
                note="Received is what inventory counts."),
            Col("received_date", "Received", 12, "date",
                validate=date_check()),
            Col("notes", "Notes", 26, "wrap"),
        ],
        samples=sample_data.purchase_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet, fmts, cfg, reg) -> None:
    global SUP_FIRST_ROW
    spec_ = reg[NAME]
    row = spec_.last_data_row + 3
    sheet.section(row, "SUPPLIER DIRECTORY", 7)
    row += 1
    sheet.table_head(row, 0, ["Supplier", "Contact", "Phone", "Email",
                              "Terms", "Lead time", "Notes"])
    SUP_FIRST_ROW = row + 2          # 1-based Excel row of first supplier
    for i, sup in enumerate(sample_data.SUPPLIERS):
        r = row + 1 + i
        for c, val in enumerate(sup):
            sheet.write(r, c, val, sheet.f.input("text"))
    sheet.note(row + len(sample_data.SUPPLIERS) + 2,
               "Add suppliers here - the drop down on the register above "
               "and on tab 13 reads this list.", 7)
