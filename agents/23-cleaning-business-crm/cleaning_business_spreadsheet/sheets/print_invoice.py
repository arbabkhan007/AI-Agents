"""Print Invoice - a client-ready invoice document."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet

MAX_LINES = 12


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Print Invoice")
    ws.set_tab_color(Palette.ink)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 16)
    ws.set_column(2, 2, 30)
    ws.set_column(3, 3, 10)
    ws.set_column(4, 4, 10)
    ws.set_column(5, 5, 14)
    ws.set_column(6, 6, 14)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    I_num = rng("Invoices", "invoice_number")
    I_client = rng("Invoices", "client")
    I_prop = rng("Invoices", "property")
    I_date = rng("Invoices", "date")
    I_due = rng("Invoices", "due")
    I_sub = rng("Invoices", "subtotal")
    I_tax = rng("Invoices", "tax")
    I_total = rng("Invoices", "total")
    I_paid = rng("Invoices", "paid")
    I_balance = rng("Invoices", "balance")
    I_job = rng("Invoices", "job_ref")

    L_key = rng("Invoice Lines", "match_key")
    L_desc = rng("Invoice Lines", "description")
    L_qty = rng("Invoice Lines", "qty")
    L_price = rng("Invoice Lines", "unit_price")
    L_total = rng("Invoice Lines", "line_total")
    L_date = rng("Invoice Lines", "date")

    ws.merge_range(1, 1, 1, 6, "INVOICE", fmts["print_title"])
    ws.set_row(1, 30)
    ws.write(2, 1, "Business", fmts["print_label"])
    ws.merge_range(2, 2, 2, 4, '=Settings!$C$6', fmts["print_value"])
    ws.merge_range(2, 5, 2, 6, '=Settings!$C$9', fmts["print_value"])
    ws.write(3, 1, "Address", fmts["print_label"])
    ws.merge_range(3, 2, 3, 4, '=Settings!$C$10', fmts["print_value"])
    ws.merge_range(3, 5, 3, 6, '=Settings!$C$8', fmts["print_value"])
    ws.merge_range(4, 1, 4, 6, '=Settings!$C$13', fmts["print_sub"])

    ws.write(6, 1, "Invoice #", fmts["print_label"])
    ws.write(6, 2, "I-2410", fmts["input"])
    ws.data_validation(6, 2, 6, 2,
                       {"validate": "list", "source": "=Invoices_Numbers",
                        "ignore_blank": True})
    ws.merge_range(6, 3, 6, 6,
                   "Type or pick the Invoice #. Print area A1:G48.",
                   fmts["note"])
    pick = "$C$7"

    def find(col_range: str, fallback: str = '""') -> str:
        return (f"IFERROR(INDEX({col_range},"
                f"MATCH({pick},{I_num},0)),{fallback})")

    ws.write(8, 1, "Bill to", fmts["print_label"])
    ws.merge_range(8, 2, 8, 4, f"={find(I_client)}", fmts["print_value"])
    ws.write(8, 5, "Invoice date", fmts["print_label"])
    ws.write_formula(8, 6, f"={find(I_date)}", fmts["print_date"])

    ws.write(9, 1, "Property", fmts["print_label"])
    ws.merge_range(9, 2, 9, 4, f"={find(I_prop)}", fmts["print_value"])
    ws.write(9, 5, "Due date", fmts["print_label"])
    ws.write_formula(9, 6, f"={find(I_due)}", fmts["print_date"])

    ws.write(10, 1, "Job #", fmts["print_label"])
    ws.merge_range(10, 2, 10, 4, f"={find(I_job)}", fmts["print_value"])
    ws.write(10, 5, "Terms", fmts["print_label"])
    ws.write_formula(10, 6, '=Settings!$C$46&" days"',
                     fmts["print_value"])

    row = 12
    ws.write(row - 1, 1, "Date", fmts["print_header"])
    ws.write(row - 1, 2, "Description", fmts["print_header"])
    ws.write(row - 1, 3, "Qty", fmts["print_header"])
    ws.write(row - 1, 4, "Unit price", fmts["print_header"])
    ws.merge_range(row - 1, 5, row - 1, 6, "Amount",
                   fmts["print_header"])
    row += 1

    for i in range(1, MAX_LINES + 1):
        m = f"MATCH({pick}&\"-\"&{i},{L_key},0)"
        ws.write_formula(row - 1, 1, f'=IFERROR(INDEX({L_date},{m}),"")',
                         fmts["print_cell_date"])
        ws.write_formula(row - 1, 2, f'=IFERROR(INDEX({L_desc},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 3, f'=IFERROR(INDEX({L_qty},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 4, f'=IFERROR(INDEX({L_price},{m}),"")',
                         fmts["print_cell_money"])
        ws.merge_range(row - 1, 5, row - 1, 6, "", fmts["print_cell"])
        ws.write_formula(row - 1, 5, f'=IFERROR(INDEX({L_total},{m}),"")',
                         fmts["print_cell_money"])
        row += 1

    money_text = f"{cfg.currency_symbol}#,##0.00"
    for label, expr in [
        ("Subtotal", find(I_sub, "0")),
        (cfg.tax_label, find(I_tax, "0")),
        ("TOTAL", find(I_total, "0")),
        ("Paid to date", find(I_paid, "0")),
    ]:
        ws.merge_range(row, 1, row, 4, label, fmts["print_total"])
        ws.merge_range(row, 5, row, 6, f"={expr}",
                       fmts["print_total_money"])
        row += 1

    ws.merge_range(row, 1, row, 4, "BALANCE DUE", fmts["print_total"])
    ws.merge_range(row, 5, row, 6, f"={find(I_balance, '0')}",
                   fmts["print_total_money"])
    row += 2

    ws.merge_range(row, 1, row, 6, "Payment details", fmts["print_label"])
    row += 1
    details = [
        '="Please pay by bank transfer to "&Settings!$C$6&", '
        'reference "&' + pick + '&"."',
        '="Payment terms: "&Settings!$C$46&" days from the invoice '
        'date. Late balances may attract a late fee."',
        '="Questions? Email "&Settings!$C$8&" or call "&Settings!$C$9&"."',
        f'="Thank you for your business."',
    ]
    for t in details:
        ws.merge_range(row, 1, row, 6, t, fmts["print_value"])
        row += 1

    row += 1
    ws.merge_range(row, 1, row, 6,
                   f'="Balance due: "&TEXT({find(I_balance, "0")},'
                   f'"{money_text}")&"  ·  thank you."',
                   fmts["print_label"])

    ws.set_zoom(100)
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.print_area(0, 0, row, 6)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
