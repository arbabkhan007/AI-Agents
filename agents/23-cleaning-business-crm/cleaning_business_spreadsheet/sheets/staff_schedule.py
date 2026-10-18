"""Staff Schedule - who works where, this week."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Staff Schedule")
    ws.set_tab_color(Palette.primary_mid)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 22)
    ws.set_column(2, 8, 13)
    ws.set_column(9, 9, 12)
    ws.set_column(10, 11, 16)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    j_date = rng("Jobs", "date")
    j_status = rng("Jobs", "status")
    j_hours = rng("Jobs", "hours")
    j_crew = rng("Jobs", "crew_lead")
    j_client = rng("Jobs", "client")
    e_name = rng("Employees", "name")

    ws.merge_range(0, 1, 0, 9, "Staff Schedule  ·  Week View",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 9,
                   "Hours per employee, per day, read live from the Jobs "
                   "tab (crew lead column). Overwrite the week cell to "
                   "look at another week.",
                   fmts["subtitle"])

    ws.write(4, 1, "Week starting", fmts["label"])
    ws.write_formula(
        4, 2,
        f'=TODAY()-WEEKDAY(TODAY(),{2 if cfg.week_start == "Monday" else 1})+1',
        fmts["input_date"])
    ws.merge_range(4, 3, 4, 9,
                   "Type any date to see that week (Monday-based).",
                   fmts["note"])

    week_cell = "$C$5"
    weekdays = (["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                if cfg.week_start == "Monday" else
                ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])

    # header row
    ws.write(6, 1, "Employee", fmts["header"])
    for c, name in enumerate(weekdays):
        day_ref = f"{week_cell}+{c}"
        ws.write_formula(6, 2 + c,
                         f'={day_ref}', fmts["header"])
        ws.write(7, 2 + c, name, fmts["nav"])
    ws.write(6, 9, "Week total", fmts["header"])
    ws.write(6, 10, "Jobs", fmts["header"])
    ws.write(6, 11, "Cost", fmts["header"])
    ws.set_row(6, 22)

    # employee rows (first 14 rows of the Employees register)
    e_spec = reg["Employees"]
    for i in range(14):
        r = 9 + i
        erow = e_spec.first_data_row + i
        ws.write_formula(
            r - 1, 1,
            f"=IF({quote_sheet('Employees')}!${e_spec.letter('name')}"
            f"${erow}=\"\",\"\",{quote_sheet('Employees')}!"
            f"${e_spec.letter('name')}${erow})",
            fmts["text_locked"])
        for c in range(7):
            day_ref = f"{week_cell}+{c}"
            formula = (
                f'=IF($B{r}="","",IF(SUMIFS({j_hours},{j_date},{day_ref},'
                f'{j_crew},$B{r},{j_status},"<>Cancelled")=0,"",'
                f'SUMIFS({j_hours},{j_date},{day_ref},{j_crew},$B{r},'
                f'{j_status},"<>Cancelled")))')
            ws.write_formula(r - 1, 2 + c, formula, fmts["calc_decimal"])
        ws.write_formula(
            r - 1, 9,
            f'=IF($B{r}="","",SUM(C{r}:I{r}))', fmts["calc_decimal"])
        ws.write_formula(
            r - 1, 10,
            f'=IF($B{r}="","",COUNTIFS({j_crew},$B{r},{j_date},'
            f'">="&{week_cell},{j_date},"<="&{week_cell}+6,'
            f'{j_status},"<>Cancelled"))', fmts["calc_int"])
        ws.write_formula(
            r - 1, 11,
            f'=IF($B{r}="","",SUMIFS({j_hours},{j_crew},$B{r},{j_date},'
            f'">="&{week_cell},{j_date},"<="&{week_cell}+6,'
            f'{j_status},"<>Cancelled")*{quote_sheet("Settings")}!'
            f'$C$42)', fmts["calc_money"])

    # totals row
    tr = 23
    ws.write(tr - 1, 1, "Totals", fmts["total_label"])
    for c in range(7):
        col = chr(ord("C") + c)
        ws.write_formula(tr - 1, 2 + c,
                         f'=SUM({col}9:{col}22)', fmts["total_money"])
    ws.write_formula(tr - 1, 9, '=SUM(J9:J22)', fmts["total_money"])
    ws.write_formula(tr - 1, 10, '=SUM(K9:K22)', fmts["total_int"])
    ws.write_formula(tr - 1, 11, '=SUM(L9:L22)', fmts["total_money"])

    # week summary
    r = 25
    ws.merge_range(r - 1, 1, r - 1, 9, "This week at a glance",
                   fmts["section"])
    r += 1
    stats = [
        ("Jobs this week",
         f'=COUNTIFS({j_date},">="&{week_cell},{j_date},'
         f'"<="&{week_cell}+6,{j_status},"<>Cancelled")', "calc_int"),
        ("Revenue scheduled",
         f'=SUMIFS({quote_sheet("Jobs")}!$'
         f'{reg.letter("Jobs", "price")}$5:$'
         f'{reg.letter("Jobs", "price")}${reg["Jobs"].last_data_row},'
         f'{j_date},">="&{week_cell},{j_date},"<="&{week_cell}+6,'
         f'{j_status},"<>Cancelled")', "calc_money"),
        ("Hours scheduled",
         f'=SUMIFS({j_hours},{j_date},">="&{week_cell},{j_date},'
         f'"<="&{week_cell}+6,{j_status},"<>Cancelled")', "calc_decimal"),
        ("Unassigned jobs (no crew lead)",
         f'=COUNTIFS({j_date},">="&{week_cell},{j_date},'
         f'"<="&{week_cell}+6,{j_status},"<>Cancelled",{j_crew},"")',
         "calc_int"),
    ]
    for label, formula, style in stats:
        ws.write(r - 1, 1, label, fmts["label"])
        ws.write_formula(r - 1, 2, formula, fmts[style])
        r += 1

    ws.merge_range(r, 1, r, 9,
                   "Cells show scheduled hours per crew lead. Add crews "
                   "on the Employees tab - the first 14 appear here.",
                   fmts["note"])
    ws.freeze_panes(8, 2)
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
