"""Print Quote - a client-ready quote document."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref

MAX_LINES = 12


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Print Quote")
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

    Q_num = rng("Quotes", "quote_number")
    Q_client = rng("Quotes", "client")
    Q_prop = rng("Quotes", "property")
    Q_date = rng("Quotes", "date")
    Q_valid = rng("Quotes", "valid_until")
    Q_freq = rng("Quotes", "frequency")
    Q_sub = rng("Quotes", "subtotal")
    Q_disc = rng("Quotes", "discount")
    Q_tax = rng("Quotes", "tax")
    Q_total = rng("Quotes", "total")
    Q_dep = rng("Quotes", "deposit")
    Q_hours = rng("Quotes", "est_hours")
    Q_service = rng("Quotes", "service")

    L_key = rng("Quote Lines", "match_key")
    L_desc = rng("Quote Lines", "description")
    L_qty = rng("Quote Lines", "qty")
    L_unit = rng("Quote Lines", "unit")
    L_price = rng("Quote Lines", "unit_price")
    L_total = rng("Quote Lines", "line_total")
    L_room = rng("Quote Lines", "room_area")

    # --------------------------------------------------------- document head
    ws.merge_range(1, 1, 1, 6, "QUOTATION", fmts["print_title"])
    ws.set_row(1, 30)
    ws.write(2, 1, "Business", fmts["print_label"])
    ws.merge_range(2, 2, 2, 4, '=Settings!$C$6', fmts["print_value"])
    ws.merge_range(2, 5, 2, 6, '=Settings!$C$9', fmts["print_value"])
    ws.write(3, 1, "Address", fmts["print_label"])
    ws.merge_range(3, 2, 3, 4, '=Settings!$C$10', fmts["print_value"])
    ws.merge_range(3, 5, 3, 6, '=Settings!$C$8', fmts["print_value"])
    ws.merge_range(4, 1, 4, 6, '=Settings!$C$13', fmts["print_sub"])

    # ------------------------------------------------------------ the picker
    ws.write(6, 1, "Quote #", fmts["print_label"])
    ws.write(6, 2, "Q-1010", fmts["input"])
    ws.data_validation(6, 2, 6, 2,
                       {"validate": "list", "source": "=Quotes_Numbers",
                        "ignore_blank": True})
    ws.merge_range(6, 3, 6, 6,
                   "Type or pick the Quote # - the document builds "
                   "itself. Set the print area to A1:G45 and print.",
                   fmts["note"])
    pick = "$C$7"

    def find(col_range: str, fallback: str = '""') -> str:
        return f"IFERROR(INDEX({col_range},MATCH({pick},{Q_num},0)),{fallback})"

    # ------------------------------------------------------- client block
    ws.write(8, 1, "Prepared for", fmts["print_label"])
    ws.merge_range(8, 2, 8, 4,
                   f"={find(Q_client)}", fmts["print_value"])
    ws.write(8, 5, "Date", fmts["print_label"])
    ws.write_formula(8, 6, f"={find(Q_date)}", fmts["print_date"])

    ws.write(9, 1, "Property", fmts["print_label"])
    ws.merge_range(9, 2, 9, 4,
                   f"={find(Q_prop)}", fmts["print_value"])
    ws.write(9, 5, "Valid until", fmts["print_label"])
    ws.write_formula(9, 6, f"={find(Q_valid)}", fmts["print_date"])

    ws.write(10, 1, "Service", fmts["print_label"])
    ws.merge_range(10, 2, 10, 4,
                   f"={find(Q_service)}", fmts["print_value"])
    ws.write(10, 5, "Frequency", fmts["print_label"])
    ws.write_formula(10, 6, f"={find(Q_freq)}", fmts["print_value"])

    ws.write(11, 1, "Est. hours", fmts["print_label"])
    ws.write_formula(11, 2, f"={find(Q_hours)}", fmts["print_value"])

    # ---------------------------------------------------------- line table
    row = 13
    ws.write(row - 1, 1, "Area", fmts["print_header"])
    ws.write(row - 1, 2, "What is included", fmts["print_header"])
    ws.write(row - 1, 3, "Qty", fmts["print_header"])
    ws.write(row - 1, 4, "Unit", fmts["print_header"])
    ws.write(row - 1, 5, "Unit price", fmts["print_header"])
    ws.write(row - 1, 6, "Line total", fmts["print_header"])
    row += 1

    for i in range(1, MAX_LINES + 1):
        key_expr = f'{pick}&"-"&{i}'
        m = f"MATCH({key_expr},{L_key},0)"
        ws.write_formula(row - 1, 1,
                         f'=IFERROR(INDEX({L_room},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 2,
                         f'=IFERROR(INDEX({L_desc},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 3,
                         f'=IFERROR(INDEX({L_qty},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 4,
                         f'=IFERROR(INDEX({L_unit},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 5,
                         f'=IFERROR(INDEX({L_price},{m}),"")',
                         fmts["print_cell_money"])
        ws.write_formula(row - 1, 6,
                         f'=IFERROR(INDEX({L_total},{m}),"")',
                         fmts["print_cell_money"])
        row += 1

    # ------------------------------------------------------------ totals
    ws.merge_range(row, 1, row, 5, "Subtotal", fmts["print_total"])
    ws.write_formula(row, 6, f"={find(Q_sub, '0')}",
                     fmts["print_total_money"])
    row += 1
    ws.merge_range(row, 1, row, 5, "Discount", fmts["print_total"])
    ws.write_formula(row, 6, f"={find(Q_disc, '0')}",
                     fmts["print_total_money"])
    row += 1
    ws.merge_range(row, 1, row, 5, cfg.tax_label, fmts["print_total"])
    ws.write_formula(row, 6, f"={find(Q_tax, '0')}",
                     fmts["print_total_money"])
    row += 1
    ws.merge_range(row, 1, row, 5, "TOTAL", fmts["print_total"])
    ws.write_formula(row, 6, f"={find(Q_total, '0')}",
                     fmts["print_total_money"])
    row += 1
    ws.merge_range(row, 1, row, 5,
                   "Deposit to confirm booking", fmts["print_total"])
    ws.write_formula(row, 6, f"={find(Q_dep, '0')}",
                     fmts["print_total_money"])
    row += 2

    # ------------------------------------------------------------- terms
    ws.merge_range(row, 1, row, 6, "Terms & notes", fmts["print_label"])
    row += 1
    money_text = f"{cfg.currency_symbol}#,##0.00"
    terms = [
        f'="1. This quote is valid until "&TEXT({find(Q_valid)},'
        f'"d mmm yyyy")&"."',
        f'="2. A deposit of "&TEXT({find(Q_dep, "0")},"{money_text}")'
        f'&" confirms the booking."',
        f'="3. Payment is due within {cfg.payment_terms_days} days of '
        f'the invoice."',
        '="4. Access to the property must be provided at the agreed '
        'time; no-access visits are chargeable."',
        '="5. Fragile or high-value items should be flagged before work '
        'starts."',
        '="6. Any change to the scope may adjust this price - we will '
        'always confirm first."',
        '="Thank you for considering "&Settings!$C$6&"."',
    ]
    for t in terms:
        ws.merge_range(row, 1, row, 6, t, fmts["print_value"])
        row += 1

    row += 1
    ws.merge_range(row, 1, row, 6,
                   "Signature: ______________________     "
                   "Date: ______________     "
                   "Accept quote: ☐", fmts["print_label"])

    ws.set_zoom(100)
    ws.set_paper(9)               # A4
    ws.fit_to_pages(1, 1)
    ws.print_area(0, 0, row, 6)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
