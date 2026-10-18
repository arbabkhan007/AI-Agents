"""Print Job Sheet - what the crew takes to the job."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet

MAX_TASKS = 16


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Print Job Sheet")
    ws.set_tab_color(Palette.ink)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 14)
    ws.set_column(3, 3, 32)
    ws.set_column(4, 4, 16)
    ws.set_column(5, 5, 12)
    ws.set_column(6, 6, 12)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    J_num = rng("Jobs", "job_number")
    J_date = rng("Jobs", "date")
    J_start = rng("Jobs", "start")
    J_hours = rng("Jobs", "hours")
    J_client = rng("Jobs", "client")
    J_prop = rng("Jobs", "property")
    J_service = rng("Jobs", "service")
    J_crew = rng("Jobs", "crew_lead")
    J_team = rng("Jobs", "team")
    J_status = rng("Jobs", "status")
    J_access = rng("Jobs", "access")
    J_instr = rng("Jobs", "instructions")
    J_price = rng("Jobs", "price")

    T_key = rng("Job Tasks", "match_key")
    T_step = rng("Job Tasks", "step_no")
    T_room = rng("Job Tasks", "room_area")
    T_task = rng("Job Tasks", "task")
    T_who = rng("Job Tasks", "assigned_to")
    T_min = rng("Job Tasks", "est_min")

    P_prop = rng("Properties", "property_name")
    P_pets = rng("Properties", "pets")
    P_park = rng("Properties", "parking")
    P_alarm = rng("Properties", "alarm")
    P_hazard = rng("Properties", "hazards")

    ws.merge_range(1, 1, 1, 6, "JOB SHEET", fmts["print_title"])
    ws.set_row(1, 30)
    ws.write(2, 1, "Business", fmts["print_label"])
    ws.merge_range(2, 2, 2, 4, '=Settings!$C$6', fmts["print_value"])
    ws.merge_range(2, 5, 2, 6, '=Settings!$C$9', fmts["print_value"])
    ws.merge_range(3, 1, 3, 6, '=Settings!$C$13', fmts["print_sub"])

    ws.write(5, 1, "Job #", fmts["print_label"])
    ws.write(5, 2, "J-2411", fmts["input"])
    ws.data_validation(5, 2, 5, 2,
                       {"validate": "list", "source": "=Print_Job_Numbers",
                        "ignore_blank": True})
    ws.merge_range(5, 3, 5, 6,
                   "Type or pick the Job #. Print area A1:G44.",
                   fmts["note"])
    pick = "$C$6"

    def find(col_range: str, fallback: str = '""') -> str:
        return (f"IFERROR(INDEX({col_range},"
                f"MATCH({pick},{J_num},0)),{fallback})")

    ws.write(7, 1, "Date", fmts["print_label"])
    ws.write_formula(7, 2, f"={find(J_date)}", fmts["print_date"])
    ws.write(7, 3, "Start", fmts["print_label"])
    ws.write_formula(7, 4, f"={find(J_start)}", fmts["print_value"])
    ws.write(7, 5, "Hours", fmts["print_label"])
    ws.write_formula(7, 6, f"={find(J_hours)}", fmts["print_value"])

    ws.write(8, 1, "Client", fmts["print_label"])
    ws.merge_range(8, 2, 8, 3, f"={find(J_client)}", fmts["print_value"])
    ws.write(8, 4, "Service", fmts["print_label"])
    ws.merge_range(8, 5, 8, 6, f"={find(J_service)}", fmts["print_value"])

    ws.write(9, 1, "Property", fmts["print_label"])
    ws.merge_range(9, 2, 9, 3, f"={find(J_prop)}", fmts["print_value"])
    ws.write(9, 4, "Status", fmts["print_label"])
    ws.merge_range(9, 5, 9, 6, f"={find(J_status)}", fmts["print_value"])

    ws.write(10, 1, "Crew lead", fmts["print_label"])
    ws.merge_range(10, 2, 10, 3, f"={find(J_crew)}", fmts["print_value"])
    ws.write(10, 4, "Team", fmts["print_label"])
    ws.merge_range(10, 5, 10, 6, f"={find(J_team)}", fmts["print_value"])

    # property safety panel
    pm = f"MATCH({find(J_prop)}, {P_prop},0)".replace("=IFERROR", "IFERROR")
    prop_pets = (f'=IFERROR(INDEX({P_pets},MATCH({find(J_prop)},'
                 f'{P_prop},0)),"")')
    prop_park = (f'=IFERROR(INDEX({P_park},MATCH({find(J_prop)},'
                 f'{P_prop},0)),"")')
    prop_alarm = (f'=IFERROR(INDEX({P_alarm},MATCH({find(J_prop)},'
                  f'{P_prop},0)),"")')
    prop_hazard = (f'=IFERROR(INDEX({P_hazard},MATCH({find(J_prop)},'
                   f'{P_prop},0)),"")')
    del pm

    ws.write(12, 1, "Site info", fmts["print_label"])
    ws.merge_range(12, 2, 12, 6, "", fmts["print_value"])
    ws.write_formula(12, 2,
                     f'="Pets: "&{prop_pets[1:]}&"   ·   Parking: "&'
                     f'{prop_park[1:]}&"   ·   Alarm: "&{prop_alarm[1:]}',
                     fmts["print_value"])
    ws.write(13, 1, "Hazards", fmts["print_label"])
    ws.merge_range(13, 2, 13, 6, "", fmts["print_value"])
    ws.write_formula(13, 2, prop_hazard, fmts["print_value"])
    ws.write(14, 1, "Access", fmts["print_label"])
    ws.merge_range(14, 2, 14, 6, f"={find(J_access)}", fmts["print_value"])
    ws.write(15, 1, "Special instructions", fmts["print_label"])
    ws.merge_range(15, 2, 15, 6, f"={find(J_instr)}", fmts["print_value"])

    row = 17
    ws.write(row - 1, 1, "Step", fmts["print_header"])
    ws.write(row - 1, 2, "Area", fmts["print_header"])
    ws.write(row - 1, 3, "Task", fmts["print_header"])
    ws.write(row - 1, 4, "Who", fmts["print_header"])
    ws.write(row - 1, 5, "Est. min", fmts["print_header"])
    ws.write(row - 1, 6, "Done ✓", fmts["print_header"])
    row += 1

    for i in range(1, MAX_TASKS + 1):
        m = f"MATCH({pick}&\"-\"&{i},{T_key},0)"
        ws.write_formula(row - 1, 1, f'=IFERROR(INDEX({T_step},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 2, f'=IFERROR(INDEX({T_room},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 3, f'=IFERROR(INDEX({T_task},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 4, f'=IFERROR(INDEX({T_who},{m}),"")',
                         fmts["print_cell"])
        ws.write_formula(row - 1, 5, f'=IFERROR(INDEX({T_min},{m}),"")',
                         fmts["print_cell"])
        ws.write_blank(row - 1, 6, None, fmts["print_cell"])
        row += 1

    row += 1
    ws.merge_range(row, 1, row, 4,
                   "Client sign-off (work completed to standard)",
                   fmts["print_label"])
    ws.merge_range(row, 5, row, 6, "Time out: __________",
                   fmts["print_label"])
    row += 1
    ws.merge_range(row, 1, row, 6,
                   "Name: ______________________     "
                   "Signature: ______________________     "
                   "Date: ____________", fmts["print_label"])
    row += 2
    ws.merge_range(row, 1, row, 6,
                   f'="Price to client: "&TEXT({find(J_price, "0")},'
                   f'"{cfg.currency_symbol}#,##0.00")&'
                   f'"  ·  office use only."',
                   fmts["print_sub"])

    ws.set_zoom(100)
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.print_area(0, 0, row, 6)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
