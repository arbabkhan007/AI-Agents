"""Quote Calculator - the interactive pricing tool.

White cells are the job. Pale teal cells are the maths. Every rate is
read live from the Settings tab, so changing a price there reprices
every future quote.
"""

from __future__ import annotations

from typing import Any

from ..config import (CONDITION_FACTORS, Config, FREQUENCY_FACTORS,
                      Palette)
from ..formats import FormatBook
from ..layout import Registry
from .settings import settings_ref


def _nest_if(key: str, mapping: dict, default: str = "1") -> str:
    """Build IF(C17="x",f1,IF(C17="y",f2,...,default))."""
    expr = default
    for label, factor in reversed(list(mapping.items())):
        expr = f'IF({key}="{label}",{factor},{expr})'
    return expr


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Quote Calculator")
    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 18)
    ws.set_column(3, 5, 18)

    ws.merge_range(0, 1, 0, 5,
                   "Quote Calculator  ·  Price a Job in 3 Minutes",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 5,
                   "Fill the white cells. The price, the cost and the "
                   "margin build themselves. Rates come from Settings - "
                   "change them there, not here.",
                   fmts["subtitle"])

    def label(row: int, text: str, note: str = "") -> None:
        ws.write(row - 1, 1, text, fmts["label"])
        if note:
            ws.merge_range(row - 1, 3, row - 1, 5, note, fmts["note"])
        else:
            ws.merge_range(row - 1, 3, row - 1, 5, "", fmts["note"])

    def section(row: int, text: str) -> None:
        ws.merge_range(row - 1, 1, row - 1, 5, text, fmts["section"])

    def value(row: int, formula: str, style: str, raw=None) -> None:
        if raw is not None and not str(formula).startswith("="):
            if isinstance(raw, (int, float)):
                ws.write_number(row - 1, 2, raw, fmts[style])
            else:
                ws.write(row - 1, 2, raw, fmts[style])
        else:
            ws.write_formula(row - 1, 2, formula, fmts[style])

    def input_row(row: int, text: str, style: str, raw, note: str,
                  validation: dict = None) -> None:
        label(row, text, note)
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            ws.write_number(row - 1, 2, raw, fmts[style])
        else:
            ws.write(row - 1, 2, raw, fmts[style])
        if validation:
            ws.data_validation(row - 1, 2, row - 1, 2, validation)

    # ----------------------------------------------------------- the job
    section(5, "1 · The Job")
    input_row(6, "Quote Date", "input_date", cfg.today,
              "When the quote is prepared.")
    input_row(7, "Client", "input", "",
              "Type the client name (see the Clients tab).",
              {"validate": "list", "source": "=Clients_Names",
               "ignore_blank": True})
    input_row(8, "Property", "input", "",
              "The place being cleaned (see the Properties tab).",
              {"validate": "list", "source": "=Properties_Names",
               "ignore_blank": True})
    input_row(9, "Service Type", "input", "Standard clean",
              "Drives the uplift multiplier.",
              {"validate": "list", "source": [
                  "Standard clean", "Deep clean",
                  "Move-in / Move-out", "End of tenancy", "Office clean",
                  "Post-construction"]})

    # -------------------------------------------------------- the property
    section(11, "2 · The Property")
    input_row(12, f"Size ({cfg.area_unit})", "input", 1800,
              "Total floor area to clean.")
    input_row(13, "Bedrooms", "input_int", 3, "")
    input_row(14, "Bathrooms", "input_int", 2, "")
    input_row(15, "Other Rooms", "input_int", 2,
              "Living room, dining, office... (rooms beyond bed/bath).")
    input_row(16, "Floors", "input_int", 1, "")
    input_row(17, "Condition", "input", "Normal",
              "How dirty it is - this changes the hours.",
              {"validate": "list", "source": list(CONDITION_FACTORS)})

    # ------------------------------------------------------- job details
    section(19, "3 · The Job Details")
    input_row(20, "Frequency", "input", "One-off",
              "Regular work is cheaper per visit.",
              {"validate": "list", "source": list(FREQUENCY_FACTORS)})
    input_row(21, "Pets", "input", "No", "Adds the pet surcharge.",
              {"validate": "list", "source": ["Yes", "No"]})
    input_row(22, "Interior Windows", "input_int", 0,
              "Priced each on top of the clean.")
    input_row(23, "Oven Deep Clean", "input", "No", "",
              {"validate": "list", "source": ["Yes", "No"]})
    input_row(24, "Fridge Deep Clean", "input", "No", "",
              {"validate": "list", "source": ["Yes", "No"]})
    input_row(25, "Carpet / Upholstery", "input", "No", "",
              {"validate": "list", "source": ["Yes", "No"]})
    input_row(26, f"Travel ({cfg.distance_unit})", "input", 8,
              "Round trip distance to the job.")
    input_row(27, "Discount %", "input_pct", 0,
              "Goodwill, package deal, haggling room.")

    # ---------------------------------------------------------- the maths
    section(29, "4 · The Maths (live)")
    freq_factor = _nest_if("C20", FREQUENCY_FACTORS)
    cond_factor = _nest_if("C17", CONDITION_FACTORS)
    deep_mult = ('IF(OR(C9="Deep clean",C9="Post-construction",'
                 'C9="End of tenancy",C9="Move-in / Move-out"),'
                 '1+' + settings_ref("deep_uplift") + ',1)')

    rows = [
        (30, "Base clean price",
         f'=C12*{settings_ref("rate_per_area")}'
         f'+C13*{settings_ref("rate_per_bedroom")}'
         f'+C14*{settings_ref("rate_per_bathroom")}'
         f'+C15*{settings_ref("rate_per_room")}',
         "calc_money",
         "Size + bedrooms + bathrooms + rooms, at your Settings rates."),
        (31, "Service adjustment", f'=C30*{deep_mult}', "calc_money",
         "Deep / move / post-construction work is harder - it is priced "
         "higher."),
        (32, "Frequency factor", f'={freq_factor}', "decimal_locked",
         "Regular work gets a better per-visit price."),
        (33, "Condition factor (hours)", f'={cond_factor}',
         "decimal_locked",
         "Changes the hours estimate, not the price."),
        (34, "Extras total",
         f'=IF(C21="Yes",{settings_ref("pet_surcharge")},0)'
         '+C22*8+IF(C23="Yes",35,0)+IF(C24="Yes",30,0)'
         f'+IF(C25="Yes",45,0)+C26*{settings_ref("travel_rate")}',
         "calc_money",
         "Pets, windows, oven, fridge, carpet and travel."),
        (35, "Estimated hours",
         f'=ROUND((C12*0.004+C13*0.35+C14*0.5+C15*0.25)*C33*{deep_mult},1)',
         "decimal_locked",
         "How long the crew will be there."),
        (36, "Labour cost",
         f'=ROUND(C35*{settings_ref("cleaners_per_job")}*'
         f'{settings_ref("cost_per_hour")},2)',
         "calc_money", "Hours x cleaners x your loaded hourly cost."),
        (37, "Supplies cost",
         f'=ROUND(C35*{settings_ref("supplies_per_hour")},2)',
         "calc_money", "Chemicals and materials."),
        (38, "Travel cost",
         f'=ROUND(C26*{settings_ref("travel_rate")},2)',
         "calc_money", "Distance at your travel rate."),
        (39, "Total cost", '=C36+C37+C38', "calc_money",
         "What the job costs you."),
    ]
    for row, text, formula, style, note in rows:
        label(row, text, note)
        ws.write_formula(row - 1, 2, formula, fmts[style])

    # --------------------------------------------------------- the price
    section(41, "5 · The Price")
    price_rows = [
        (42, "Price before discount",
         f'=MAX({settings_ref("minimum_charge")},'
         'C31*C32+C34)', "calc_money",
         "Adjusted base x frequency factor + extras, never below the "
         "minimum charge."),
        (43, "Discount", '=ROUND(C42*C27,2)', "calc_money", ""),
        (44, "Quote total (ex tax)", '=C42-C43', "calc_money",
         "What you quote the client."),
        (45, "Tax", f'=ROUND(C44*{settings_ref("tax_rate")},2)',
         "calc_money", "Add only if you charge sales tax / VAT."),
        (46, "Total with tax", '=C44+C45', "calc_money", ""),
        (47, "Deposit due",
         f'=ROUND(C46*{settings_ref("deposit_pct")},2)', "calc_money",
         "Collect before work starts on big jobs."),
        (48, "Margin %", '=IF(C44=0,"",(C44-C39)/C44)', "calc_pct",
         "(Price - cost) / price."),
        (49, "Margin verdict",
         '=IF(C44=0,"-",IF(C48<' + settings_ref("margin_floor") +
         ',"LOW MARGIN - review the price",IF(C48<' +
         settings_ref("target_margin") +
         ',"OK - below target","STRONG")))', "calc",
         "Below the floor means this job does not pay."),
        (50, "Break-even price at target margin",
         '=IF(' + settings_ref("target_margin") + '>=1,"",'
         f'ROUND(C39/(1-{settings_ref("target_margin")}),2))',
         "calc_money",
         "What you would need to charge to hit the target margin."),
        (51, "Price per hour quoted", '=IF(C35=0,"",ROUND(C44/C35,2))',
         "calc_money",
         f"Compare with your hourly rate "
         f"({cfg.currency_symbol}{cfg.hourly_rate:,.2f})."),
    ]
    for row, text, formula, style, note in price_rows:
        label(row, text, note)
        ws.write_formula(row - 1, 2, formula, fmts[style])

    # -------------------------------------------------------- next steps
    section(53, "6 · Next steps")
    steps = [
        "Happy with the number? Add one row to the Quotes tab and one "
        "row per line to Quote Lines (same Quote #).",
        "Print the client a copy from the Print Quote tab - type the "
        "Quote # into its yellow cell.",
        "Won the work? Copy the details to the Jobs tab and schedule "
        "the crew.",
        "Margin verdict amber or red? Cut the hours, add the extras, "
        "raise the price - or decline. Unprofitable work is worse than "
        "no work.",
    ]
    rr = 54
    for text in steps:
        ws.merge_range(rr - 1, 1, rr - 1, 5, "•  " + text, fmts["note"])
        ws.set_row(rr - 1, 24)
        rr += 1

    ws.freeze_panes(3, 0)
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
