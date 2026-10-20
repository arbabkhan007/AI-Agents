"""5 Workout Log - one row per exercise per session.

Volume, estimated 1RM (Epley), personal-record detection and the
"last time" progressive-overload prompt are all calculated with
COUNTIFS / SUMPRODUCT(MAX(...)) and hidden helper columns, so nothing
here needs an array formula or a function newer than Excel 2007.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import (SheetWriter, cf_text, date_check, list_from,
                      number_check, yes_no)
from . import common as C
from .. import sample_data

NAME = "5 Workout Log"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="5  Workout Log",
        subtitle="One row per exercise per session - volume, estimated "
                 "1RM and personal records calculate as you type.",
        tab_color="#14655A",
        rows=cfg.row_count("Workout Log"),
        freeze_cols=4,
        help_text="Type the date, the session name and the exercise "
                  "(drop down), then sets, reps and weight. Warm-up sets "
                  "are excluded from volume by the flag. The 'last time' "
                  "column is your progressive-overload prompt.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="L-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("session", "Session", 14, "text",
                note="Any name you like: Push A, Lower 1, Club night."),
            Col("exercise", "Exercise", 26, "text",
                validate=list_from("ExerciseNames"),
                note="Drop down reads the Exercise Library - add moves "
                     "there and they appear here."),
            Col("muscle", "Muscle group", 13, "text",
                formula='IF({exercise}{r}="","",IFERROR(INDEX('
                        '[[6 Exercise Library.muscle]],MATCH({exercise}{r},'
                        '[[6 Exercise Library.name]],0)),""))'),
            Col("sets", "Sets", 7, "int", validate=number_check(0, 20, False)),
            Col("reps", "Reps / set", 9, "int",
                validate=number_check(0, 100, False)),
            Col("weight", "Weight", 10, "number1",
                validate=number_check(0, 600),
                note="In the unit shown in the stamp column, or the "
                     "workbook unit when the stamp is empty."),
            Col("stamp", "Unit", 7, "flag",
                validate={"validate": "list", "source": ["kg", "lb"],
                          "ignore_blank": True},
                note="Leave empty to use the workbook unit. Stamp rows "
                     "logged in the other unit and switching units never "
                     "misreads them."),
            Col("kg", "kg (canonical)", 10, "number", hidden=True,
                formula="=" + C.kg_from("{weight}{r}", "{stamp}{r}")),
            Col("rpe", "RPE", 7, "int", validate=number_check(0, 10, False)),
            Col("rest", "Rest (sec)", 10, "int",
                validate=number_check(0, 900, False)),
            Col("dur", "Minutes", 9, "number1",
                validate=number_check(0, 600)),
            Col("warmup", "Warm-up?", 10, "flag", validate=yes_no(),
                note="Yes excludes the row from every volume number."),
            Col("done", "Done?", 8, "flag", validate=yes_no()),
            Col("notes", "Notes", 30, "wrap",
                note="Form, tempo, pain, band colour - anything future "
                     "you will want to know."),
            Col("vol", "Volume kg", 10, "number", hidden=True,
                formula='IF(OR({done}{r}<>"Yes",{warmup}{r}="Yes",'
                        '{sets}{r}="",{reps}{r}="",{kg}{r}=""),0,'
                        '{sets}{r}*{reps}{r}*{kg}{r})'),
            Col("e1rm", "e1RM kg", 10, "number", hidden=True,
                formula='IF(OR({kg}{r}="",{reps}{r}="",{reps}{r}<1),0,'
                        '{kg}{r}*(1+{reps}{r}/30))',
                note="Epley: weight x (1 + reps / 30). Edit the formula "
                     "if you prefer another estimator."),
            Col("e1rm_disp", "Est. 1RM", 11, "number1",
                formula='IF({e1rm}{r}=0,"",IF(Units="Imperial",'
                        '{e1rm}{r}/KgPerLb,{e1rm}{r}))'),
            Col("pr", "PR", 7, "status",
                formula='IF(OR({e1rm}{r}=0,{done}{r}<>"Yes"),"",IF('
                        'COUNTIFS({exercise_first}:{exercise}{r_prev},'
                        '{exercise}{r},{e1rm_first}:{e1rm}{r_prev},">"&'
                        '{e1rm}{r})=0,"PR",""))',
                cf=[cf_text("PR", "bold_good")],
                note="Flags the moment a row beats every earlier set of "
                     "the same exercise on estimated 1RM."),
            Col("prev_row", "prev row", 9, "int", hidden=True,
                formula='IF({exercise}{r}="","",SUMPRODUCT(MAX(('
                        '{exercise_first}:{exercise}{r_prev}={exercise}{r})'
                        '*ROW({exercise_first}:{exercise}{r_prev}))))'),
            Col("last_prompt", "Last time", 26, "text",
                formula='IF(OR({prev_row}{r}="",{prev_row}{r}=0),"",'
                        '"Last: "&INDEX({sets_first}:{sets_last},'
                        '{prev_row}{r}-{first}+1)&"x"&INDEX('
                        '{reps_first}:{reps_last},{prev_row}{r}-{first}+1)'
                        '&" @ "&TEXT(IF(Units="Imperial",INDEX('
                        '{kg_first}:{kg_last},{prev_row}{r}-{first}+1)'
                        '/KgPerLb,INDEX({kg_first}:{kg_last},'
                        '{prev_row}{r}-{first}+1)),"0.##")&" "&IF('
                        'Units="Imperial","lb","kg"))',
                note="Progressive overload without scrolling: the last "
                     "logged set of this exercise."),
            Col("dow", "day of week", 8, "int", hidden=True,
                formula='IF({date}{r}="","",' + C.day_of_week("{date}{r}")
                        + ")"),
            Col("wstart", "week start", 11, "date", hidden=True,
                formula='IF({date}{r}="","",'
                        + C.week_start_of("{date}{r}") + ")"),
            Col("sid", "session id", 14, "text", hidden=True,
                formula='IF(OR({date}{r}="",{session}{r}=""),"",'
                        'TEXT({date}{r},"yyyymmdd")&"|"&{session}{r})'),
        ],
        samples=sample_data.log_rows(cfg) if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    spec_ = reg[NAME]
    last = spec_.last_data_row
    sheet.ws.conditional_format(
        spec_.first_data_row - 1, spec_.index("last_prompt"),
        last - 1, spec_.index("last_prompt"),
        {"type": "text", "criteria": "containing", "value": "Last:",
         "format": sheet.f.cf("info")})
