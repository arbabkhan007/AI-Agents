"""12 Water & Sleep - hydration, sleep maths and recovery signals.

Sleep hours use MOD(wake - bed, 1) so a bedtime before midnight and a
wake time after it compute correctly.  The weekly summary block reads
the register with SUMIFS / AVERAGEIFS over date windows.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec, col_letter, quote_sheet
from ..writer import (SheetWriter, cf_formula, date_check, number_check,
                      time_check)
from . import common as C
from .. import sample_data

NAME = "12 Water & Sleep"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="12  Water & Sleep",
        subtitle="Glasses or millilitres, bedtime and wake time - hours "
                 "slept cross midnight correctly.",
        tab_color="#3E897D",
        rows=cfg.row_count("Water & Sleep"),
        freeze_cols=3,
        help_text="Log glasses, ml, or both - they add up. Sleep quality, "
                  "mood and energy are 1-5, your scale, your rules. The "
                  "weekly summary below the register rolls everything up.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="S-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("glasses", "Glasses", 9, "int",
                validate=number_check(0, 30, False)),
            Col("ml", "Extra ml", 10, "int",
                validate=number_check(0, 6000, False),
                note="Bottles, flasks, anything not counted in glasses."),
            Col("total", "Total ml", 10, "int",
                formula='IF(AND({glasses}{r}="",{ml}{r}=""),"",IF('
                        '{glasses}{r}="",0,{glasses}{r}*GlassML)+IF('
                        '{ml}{r}="",0,{ml}{r}))'),
            Col("target", "Target ml", 10, "int",
                formula='IF({date}{r}="","",WaterTarget)'),
            Col("gap", "Gap to target", 12, "int",
                formula='IF({total}{r}="","",IF(Units="Imperial","", '
                        '{total}{r}-WaterTarget))',
                cf=[cf_formula("=AND($G5<>\"\",$G5<0)", "warn")],
                note="Negative means short of your target."),
            Col("bed", "Bedtime", 10, "time", validate=time_check()),
            Col("wake", "Wake time", 10, "time", validate=time_check()),
            Col("hours", "Hours slept", 11, "number1",
                formula='IF(OR({bed}{r}="",{wake}{r}=""),"",MOD({wake}{r}-'
                        '{bed}{r},1)*24)',
                note="Crosses midnight correctly."),
            Col("quality", "Quality 1-5", 10, "int",
                validate=number_check(1, 5, False)),
            Col("mood", "Mood 1-5", 9, "int",
                validate=number_check(1, 5, False)),
            Col("energy", "Energy 1-5", 10, "int",
                validate=number_check(1, 5, False)),
            Col("mobility", "Mobility min", 11, "int",
                validate=number_check(0, 240, False),
                note="Stretching, mobility, foam rolling - the minutes "
                     "that keep the next session possible."),
            Col("notes", "Notes", 24, "wrap"),
        ],
        samples=sample_data.water_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    spec_ = reg[NAME]
    q = quote_sheet(NAME)
    first, last = spec_.first_data_row, spec_.last_data_row
    d = f"{q}!${spec_.letter('date')}${first}:${spec_.letter('date')}${last}"
    tot = f"{q}!${spec_.letter('total')}${first}:" \
          f"${spec_.letter('total')}${last}"
    hrs = f"{q}!${spec_.letter('hours')}${first}:" \
          f"${spec_.letter('hours')}${last}"
    qual = f"{q}!${spec_.letter('quality')}${first}:" \
           f"${spec_.letter('quality')}${last}"
    mob = f"{q}!${spec_.letter('mobility')}${first}:" \
          f"${spec_.letter('mobility')}${last}"
    top = last + 2
    row = sheet.section(top, "LAST EIGHT WEEKS", 8)
    row = sheet.table_head(row, 0, ["Week starting", "Water (ml)",
                                    "Avg sleep (h)", "Avg quality",
                                    "Mobility (min)"],
                           widths=[16, 12, 13, 12, 13])
    for week in range(7, -1, -1):
        ws_expr = f"{C.week_start_of('TODAY()')}-{7 * week}"
        sheet.formula(row, 0, "=" + ws_expr, sheet.f.calc("date"))
        sheet.formula(row, 1, f'=SUMIFS({tot},{d},">="&$A{row + 1},{d},'
                              f'"<="&$A{row + 1}+6)',
                      sheet.f.calc("int"))
        sheet.formula(row, 2, f'=IFERROR(AVERAGEIFS({hrs},{d},">="&'
                              f'$A{row + 1},{d},"<="&$A{row + 1}+6,{hrs},'
                              f'">0"),"")',
                      sheet.f.calc("number1"))
        sheet.formula(row, 3, f'=IFERROR(AVERAGEIFS({qual},{d},">="&'
                              f'$A{row + 1},{d},"<="&$A{row + 1}+6,{qual},'
                              f'">0"),"")',
                      sheet.f.calc("number1"))
        sheet.formula(row, 4, f'=SUMIFS({mob},{d},">="&$A{row + 1},{d},'
                              f'"<="&$A{row + 1}+6)',
                      sheet.f.calc("int"))
        row += 1
    sheet.finish(freeze_row=4, freeze_col=2,
                 print_area=f"$A$1:${col_letter(spec_.last_col_index)}$"
                            f"{last}")
