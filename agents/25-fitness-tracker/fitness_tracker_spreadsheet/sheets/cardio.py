"""7 Cardio & Activity - pace, splits, distance and MET calories.

Pace is shown both ways (min/km and min/mile) whichever unit system the
buyer chose.  The calorie column is optional: type a number from a
machine and it wins; leave it empty and the MET table on Settings
estimates from body weight at that date.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import SheetWriter, date_check, list_from, number_check
from . import common as C
from .. import sample_data

NAME = "7 Cardio & Activity"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="7  Cardio & Activity",
        subtitle="Walks, runs, rides, swims, rows and classes - pace both "
                 "ways, steps, heart rate and an honest calorie estimate.",
        tab_color="#3E897D",
        rows=cfg.row_count("Cardio & Activity"),
        freeze_cols=3,
        help_text="Distance is typed in the stamped unit (or the workbook "
                  "unit). Pace, splits and the calorie estimate calculate; "
                  "type your own calorie number any time and it wins.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="C-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("type", "Activity", 12, "text",
                validate=list_from("ListActivityType"),
                note="Feeds the MET estimate and the minutes-by-type "
                     "report."),
            Col("distance", "Distance", 10, "number1",
                validate=number_check(0, 500),
                note="In the stamped unit, or the workbook unit when the "
                     "stamp is empty."),
            Col("stamp", "Unit", 7, "flag",
                validate={"validate": "list", "source": ["km", "mi"],
                          "ignore_blank": True}),
            Col("km", "km (canonical)", 10, "number", hidden=True,
                formula="=" + C.km_from("{distance}{r}", "{stamp}{r}")),
            Col("dur", "Minutes", 10, "number1",
                validate=number_check(0, 900)),
            Col("pace", "min / km", 10, "number1", hidden=True,
                formula='IF(OR({km}{r}="",{km}{r}=0,{dur}{r}=""),"",'
                        '{dur}{r}/{km}{r})'),
            Col("pace_txt", "Pace / km", 11, "text",
                formula="=" + C.pace_text("{pace}{r}"),
                note="Minutes:seconds per kilometre."),
            Col("pace_mi_txt", "Pace / mile", 11, "text",
                formula='IF(OR({pace}{r}="",{pace}{r}<=0),"",'
                        'TEXT(INT({pace}{r}*KmPerMi),"0")&":"&TEXT(IF('
                        'ROUND(({pace}{r}*KmPerMi-INT({pace}{r}*KmPerMi))'
                        '*60,0)=60,0,ROUND(({pace}{r}*KmPerMi-INT('
                        '{pace}{r}*KmPerMi))*60,0)),"00"))',
                note="Minutes:seconds per mile, for the runners."),
            Col("steps", "Steps", 9, "int",
                validate=number_check(0, 100000, False)),
            Col("hr", "Avg heart rate", 10, "int",
                validate=number_check(0, 250, False)),
            Col("rpe", "Effort 1-10", 10, "int",
                validate=number_check(0, 10, False)),
            Col("cal_in", "Calories (typed)", 12, "int",
                validate=number_check(0, 5000, False),
                note="Optional. A machine or watch number wins over the "
                     "estimate."),
            Col("met", "MET", 7, "number", hidden=True,
                formula='IF({type}{r}="","",IFERROR(INDEX(MetMET,MATCH('
                        '{type}{r},MetType,0)),""))'),
            Col("bw", "bodyweight kg", 10, "number", hidden=True,
                formula='IF({date}{r}="","",IFERROR(INDEX('
                        '[[8 Weight Tracker.kg]],MATCH({date}{r},'
                        '[[8 Weight Tracker.date]],1)),StartKg))',
                note="The weigh-in on or before this date; your starting "
                     "weight until the first weigh-in exists."),
            Col("kcal", "kcal used", 10, "int", hidden=True,
                formula='IF(OR({dur}="",{dur}{r}=0),0,IF({cal_in}{r}<>"",'
                        '{cal_in}{r},IF(OR({met}="",{bw}{r}=""),0,'
                        '{met}{r}*3.5*{bw}{r}/200*{dur}{r})))'),
            Col("kcal_disp", "Calories", 10, "int",
                formula='IF({kcal}{r}=0,"",{kcal}{r})',
                note="Typed value if you gave one, otherwise MET x 3.5 x "
                     "kg / 200 x minutes. An estimate, labelled as one."),
            Col("notes", "Notes", 26, "wrap"),
        ],
        samples=sample_data.cardio_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    spec_ = reg[NAME]
    sheet.note(spec_.last_data_row + 1,
               "Pace maths: pace = minutes / distance, shown per km and "
               "per mile both ways. The estimate uses the MET table on "
               "16 Settings & Lists and your body weight at the date - "
               "edit either and this tab follows.",
               spec_.last_col_index, height=26)
