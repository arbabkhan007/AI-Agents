"""Calendar - a live month view of the job book."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Calendar")
    ws.set_tab_color(Palette.primary_mid)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 7, 15)
    ws.set_column(8, 8, 3)
    ws.set_column(9, 10, 20)

    j_date = f"{quote_sheet('Jobs')}!${reg.letter('Jobs', 'date')}$5:" \
             f"${reg.letter('Jobs', 'date')}${reg['Jobs'].last_data_row}"
    j_status = f"{quote_sheet('Jobs')}!${reg.letter('Jobs', 'status')}$5:" \
               f"${reg.letter('Jobs', 'status')}${reg['Jobs'].last_data_row}"
    j_price = f"{quote_sheet('Jobs')}!${reg.letter('Jobs', 'price')}$5:" \
              f"${reg.letter('Jobs', 'price')}${reg['Jobs'].last_data_row}"
    j_hours = f"{quote_sheet('Jobs')}!${reg.letter('Jobs', 'hours')}$5:" \
              f"${reg.letter('Jobs', 'hours')}${reg['Jobs'].last_data_row}"

    ws.merge_range(0, 1, 0, 7, "Calendar  ·  Month View", fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 7,
                   "Pick a month below. Job counts and revenue per day "
                   "read live from the Jobs tab. Weekend columns are "
                   "shaded.",
                   fmts["subtitle"])

    # --- month picker -----------------------------------------------------
    ws.write(4, 1, "Month shown", fmts["label"])
    ws.write_formula(
        4, 2,
        f'=DATE(YEAR(TODAY()),MONTH(TODAY()),1)', fmts["input_date"])
    ws.merge_range(4, 3, 4, 7,
                   "Type any date in the month you want - the grid "
                   "follows it. (Cell is a formula default; overwrite it "
                   "with a date.)", fmts["note"])

    month_cell = "$C$5"
    first_day = f"DATE(YEAR({month_cell}),MONTH({month_cell}),1)"
    first_grid = f"({first_day}-WEEKDAY({first_day},{_week_num(cfg)})+1)"

    weekdays = (["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                if cfg.week_start == "Monday" else
                ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])

    # --- grid: day numbers ----------------------------------------------
    ws.merge_range(6, 1, 6, 7, "Day of month", fmts["nav"])
    for c, name in enumerate(weekdays):
        ws.write(7, 1 + c, name, fmts["header"])

    for week in range(6):
        for c in range(7):
            formula = (f'=IF(MONTH({first_grid}+{week * 7 + c})='
                       f'MONTH({month_cell}),'
                       f'{first_grid}+{week * 7 + c},"")')
            ws.write_formula(8 + week, 1 + c, formula,
                             fmts["calc_day"])
        ws.set_row(8 + week, 22)

    # --- grid: job counts -------------------------------------------------
    ws.merge_range(15, 1, 15, 7, "Jobs scheduled", fmts["nav"])
    for week in range(6):
        for c in range(7):
            grid_date = (f"({first_grid}+{week * 7 + c})")
            formula = (f'=IF(MONTH({grid_date})=MONTH({month_cell}),'
                       f'COUNTIFS({j_date},{grid_date},{j_status},'
                       f'"<>Cancelled"),"")')
            ws.write_formula(16 + week, 1 + c, formula,
                             fmts["calc_int"])

    # --- grid: revenue ----------------------------------------------------
    ws.merge_range(23, 1, 23, 7, "Revenue scheduled", fmts["nav"])
    for week in range(6):
        for c in range(7):
            grid_date = (f"({first_grid}+{week * 7 + c})")
            formula = (f'=IF(MONTH({grid_date})=MONTH({month_cell}),'
                       f'SUMIFS({j_price},{j_date},{grid_date},{j_status},'
                       f'"<>Cancelled"),"")')
            ws.write_formula(24 + week, 1 + c, formula,
                             fmts["calc_money"])

    # --- month summary ----------------------------------------------------
    r = 31
    ws.merge_range(r - 1, 1, r - 1, 7, "This month at a glance",
                   fmts["section"])
    r += 1
    month_start = f"DATE(YEAR({month_cell}),MONTH({month_cell}),1)"
    month_end = f"DATE(YEAR({month_cell}),MONTH({month_cell})+1,1)-1"
    stats = [
        ("Jobs this month",
         f'=SUMPRODUCT((MONTH({j_date}+0)=MONTH({month_cell}))*'
         f'(YEAR({j_date}+0)=YEAR({month_cell}))*'
         f'({j_status}<>"Cancelled")*({j_status}<>"")*1)',
         "calc_int"),
        ("Revenue this month",
         f'=SUMPRODUCT((MONTH({j_date}+0)=MONTH({month_cell}))*'
         f'(YEAR({j_date}+0)=YEAR({month_cell}))*'
         f'({j_status}<>"Cancelled")*{j_price})',
         "calc_money"),
        ("Hours this month",
         f'=SUMPRODUCT((MONTH({j_date}+0)=MONTH({month_cell}))*'
         f'(YEAR({j_date}+0)=YEAR({month_cell}))*'
         f'({j_status}<>"Cancelled")*{j_hours})',
         "calc_decimal"),
        ("Cancelled",
         f'=SUMPRODUCT((MONTH({j_date}+0)=MONTH({month_cell}))*'
         f'(YEAR({j_date}+0)=YEAR({month_cell}))*'
         f'({j_status}="Cancelled")*1)',
         "calc_int"),
    ]
    for label, formula, style in stats:
        ws.write(r - 1, 1, label, fmts["label"])
        ws.write_formula(r - 1, 2, formula, fmts[style])
        r += 1

    ws.merge_range(r, 1, r, 7,
                   "The month statistics use SUMPRODUCT so they work on "
                   "any month without helper columns.", fmts["note"])
    ws.freeze_panes(8, 0)
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })


def _xl(week: int, col: int) -> str:
    from ..layout import col_letter
    return f"{col_letter(1 + col)}{9 + week}"


def _week_num(cfg: Config) -> int:
    return 2 if cfg.week_start == "Monday" else 1
