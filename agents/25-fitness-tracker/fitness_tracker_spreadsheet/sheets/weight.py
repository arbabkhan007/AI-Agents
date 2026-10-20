"""8 Weight Tracker - weigh-ins, moving averages, rate and projection.

No fixed schedule: log daily, weekly or whenever.  The 7-day and 28-day
moving averages use AVERAGEIFS over an expanding window (Excel 2007+),
the projection states itself as an estimate, and milestones fire every
5 lb / 2 kg of change from the starting weight.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import (SheetWriter, cf_text, date_check, number_check)
from . import common as C
from .. import sample_data

NAME = "8 Weight Tracker"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="8  Weight Tracker",
        subtitle="Weigh in when you like - the moving averages make one "
                 "bad morning mean nothing.",
        tab_color="#14655A",
        rows=cfg.row_count("Weight Tracker"),
        freeze_cols=3,
        help_text="Type the date and the weight on the scales, in the "
                  "stamped unit or the workbook unit. Everything else on "
                  "the row calculates, including the date you would reach "
                  "your goal at the current 7-day rate.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="W-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Date", 12, "date", validate=date_check(),
                note="Keep dates in order - the moving averages and the "
                     "projection read upwards."),
            Col("weight", "Weight", 10, "number1",
                validate=number_check(20, 400),
                note="As the scales showed it."),
            Col("stamp", "Unit", 7, "flag",
                validate={"validate": "list", "source": ["kg", "lb"],
                          "ignore_blank": True}),
            Col("kg", "kg (canonical)", 10, "number", hidden=True,
                formula="=" + C.kg_from("{weight}{r}", "{stamp}{r}")),
            Col("disp", "In your unit", 11, "number1",
                formula="=" + C.disp_weight("{kg}{r}")),
            Col("chg_start", "Since start", 11, "number1",
                formula='IF({kg}{r}="","",IF(Units="Imperial",'
                        '({kg}{r}-StartKg)/KgPerLb,{kg}{r}-StartKg))',
                cf=[cf_text("-", "muted")]),
            Col("chg_last", "Since last", 10, "number1",
                formula='IF(OR({kg}{r}="",{kg}{r_prev}=""),"",'
                        'IF(Units="Imperial",({kg}{r}-{kg}{r_prev})/KgPerLb,'
                        '{kg}{r}-{kg}{r_prev}))'),
            Col("ma7", "7-day average", 12, "number1",
                formula='IF({kg}{r}="","",AVERAGEIFS({kg_first}:{kg}{r},'
                        '{date_first}:{date}{r},">="&{date}{r}-6,'
                        '{date_first}:{date}{r},"<="&{date}{r}))',
                note="The number worth watching."),
            Col("ma28", "28-day average", 12, "number1",
                formula='IF({kg}{r}="","",AVERAGEIFS({kg_first}:{kg}{r},'
                        '{date_first}:{date}{r},">="&{date}{r}-27,'
                        '{date_first}:{date}{r},"<="&{date}{r}))'),
            Col("ma7_disp", "7-day, your unit", 12, "number1",
                formula="=" + C.disp_weight("{ma7}{r}")),
            Col("rate", "Rate / week", 11, "number1",
                formula='IF(OR({ma7}{r}="",{date}{r}=""),"",IFERROR(IF('
                        'INDEX({ma7_first}:{ma7}{r},MATCH({date}{r}-7,'
                        '{date_first}:{date}{r},1))="","",{ma7}{r}-INDEX('
                        '{ma7_first}:{ma7}{r},MATCH({date}{r}-7,'
                        '{date_first}:{date}{r},1))),""))',
                note="Change in the 7-day average over the last week, in "
                     "kg (or lb when you switch units on Settings)."),
            Col("proj", "Goal at this rate", 14, "date",
                formula='IF(OR({rate}{r}="",{rate}{r}=0,{kg}{r}=""),"",IF('
                        '(GoalKg-{kg}{r})/({rate}{r}/7)<0,"off track",IF('
                        '(GoalKg-{kg}{r})/({rate}{r}/7)>3650,"",{date}{r}+'
                        '(GoalKg-{kg}{r})/({rate}{r}/7))))',
                cf=[cf_text("off track", "warn")],
                note="An estimate from the current rate, not a promise. "
                     "'off track' means the rate is pointing away from "
                     "the goal."),
            Col("milestone", "Milestone", 11, "status",
                formula='IF({kg}{r}="","",IF(INT(ABS(StartKg-{kg}{r})/'
                        'MilestoneStep)>INT(ABS(StartKg-IF({kg}{r_prev}='
                        '"",{kg}{r},{kg}{r_prev}))/MilestoneStep),'
                        '"milestone",""))',
                cf=[cf_text("milestone", "bold_good")],
                note="Fires every 5 lb or 2 kg of change from your "
                     "starting weight."),
            Col("notes", "Notes", 24, "wrap"),
        ],
        samples=sample_data.weight_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    spec_ = reg[NAME]
    sheet.note(spec_.last_data_row + 1,
               "Weigh-ins do not need a schedule. The 7-day average is "
               "the honest line; the projection reads 'off track' rather "
               "than guessing a date when the rate points the wrong way.",
               spec_.last_col_index, height=26)
