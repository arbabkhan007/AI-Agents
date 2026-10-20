"""4 Workout Planner - a 12-week programme block and a weekly template.

The programme start date drives every week row; completed sessions and
minutes are pulled from the log with COUNTIFS / SUMIFS over the hidden
week-start column, and the distinct-session count uses the
SUMPRODUCT(1/COUNTIFS(...)) idiom so no array formula is needed.
Works whether the buyer starts in January or on a random Tuesday.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import quote_sheet
from ..writer import SheetWriter, number_check, yes_no
from . import common as C

NAME = "4 Workout Planner"
LOG = "5 Workout Log"

PHASE_DEFAULT = ["Base", "Base", "Base", "Deload", "Build", "Build",
                 "Build", "Deload", "Peak", "Peak", "Peak", "Deload"]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary_mid, landscape=False)
    last_col = 9
    sheet.banner("4  Workout Planner",
                 "Twelve weeks of intent, one repeating week of detail - "
                 "planned versus completed, always.", last_col)
    log = reg[LOG]
    ql = quote_sheet(LOG)
    wstart = f"{ql}!${log.letter('wstart')}${log.first_data_row}:" \
             f"${log.letter('wstart')}${log.last_data_row}"
    sid = f"{ql}!${log.letter('sid')}${log.first_data_row}:" \
          f"${log.letter('sid')}${log.last_data_row}"
    dur = f"{ql}!${log.letter('dur')}${log.first_data_row}:" \
          f"${log.letter('dur')}${log.last_data_row}"
    dow = f"{ql}!${log.letter('dow')}${log.first_data_row}:" \
          f"${log.letter('dow')}${log.last_data_row}"

    row = 4
    row = sheet.section(row, "THE PROGRAMME", last_col)
    row = sheet.field(row, "Programme start date",
                      cfg.today - _td(days=77) if cfg.include_sample_data
                      else None, style="date", name="ProgrammeStart",
                      help_text="Any date works - January 1st or a random "
                                "Tuesday. Every week row follows it.")
    row = sheet.field(row, "Training split", None, formula="=TrainingSplit",
                      help_text="Changed on 16 Settings & Lists.")
    row = sheet.table_head(row, 0, ["Week", "Starts", "Phase", "Deload",
                                    "Sessions planned", "Sessions done",
                                    "Minutes planned", "Minutes done",
                                    "Status"],
                           widths=[7, 12, 12, 9, 12, 12, 12, 12, 12])
    first = row
    for i in range(cfg.programme_weeks):
        ws = f"ProgrammeStart+{7 * i}"
        sheet.formula(row, 0, f"={i + 1}", sheet.f.calc("int"))
        sheet.formula(row, 1, "=" + ws, sheet.f.calc("date"))
        sheet.write(row, 2, PHASE_DEFAULT[i] if cfg.include_sample_data
                    else None, sheet.f.input("text"))
        sheet.write(row, 3, "Yes" if (cfg.include_sample_data and
                                      PHASE_DEFAULT[i] == "Deload")
                    else None, sheet.f.input("flag"))
        sheet.ws.data_validation(row, 3, row, 3, yes_no())
        sheet.write(row, 4, 3 if PHASE_DEFAULT[i] == "Deload"
                    else cfg.sessions_per_week, sheet.f.input("int"))
        sheet.ws.data_validation(row, 4, row, 4, number_check(0, 14, False))
        sheet.formula(row, 5,
                      f'=IF($B{row + 1}="","",SUMPRODUCT(({wstart}='
                      f'$B{row + 1})/((COUNTIFS({wstart},{wstart},{sid},'
                      f'{sid})+({sid}="")))))',
                      sheet.f.calc("number1"))
        sheet.write(row, 6, 45 if PHASE_DEFAULT[i] == "Deload" else 60,
                    sheet.f.input("int"))
        sheet.ws.data_validation(row, 6, row, 6, number_check(0, 900, False))
        sheet.formula(row, 7,
                      f'=SUMIFS({dur},{wstart},$B{row + 1})',
                      sheet.f.calc("int"))
        sheet.formula(row, 8,
                      f'=IF($E{row + 1}="","",IF($F{row + 1}>=$E{row + 1},'
                      f'"planned met",IF($F{row + 1}=0,"not started",'
                      f'"part way")))',
                      sheet.f.calc("status"))
        row += 1
    sheet.ws.conditional_format(first, 8, row - 1, 8,
                                {"type": "text", "criteria": "containing",
                                 "value": "planned met",
                                 "format": sheet.f.cf("good")})
    row += 1

    row = sheet.section(row, "THE REPEATING WEEK", last_col)
    row = sheet.note(row, "One template week. The completed minutes read "
                          "the current week from the log, by weekday, so "
                          "the plan and the truth sit side by side.",
                     last_col, height=24)
    row = sheet.table_head(row, 0, ["Day", "Focus", "Planned exercises",
                                    "Sets", "Target reps",
                                    "Minutes planned",
                                    "Minutes done this week"],
                           widths=[12, 14, 40, 8, 11, 12, 14])
    focus_default = ["Push", "Pull", "Legs", "Rest or walk", "Upper",
                     "Lower", "Walk or mobility"]
    for i in range(7):
        sheet.formula(row, 0,
                      f'=INDEX(ListWeekday,MOD(IF(WeekStart="Sunday",6,0)'
                      f'+{i},7)+1)',
                      sheet.f.calc("text"))
        sheet.write(row, 1, focus_default[i] if cfg.include_sample_data
                    else None, sheet.f.input("text"))
        sheet.write(row, 2, None, sheet.f.input("wrap"))
        sheet.write(row, 3, None, sheet.f.input("int"))
        sheet.write(row, 4, None, sheet.f.input("text"))
        sheet.write(row, 5, 0 if focus_default[i].startswith(("Rest",
                                                              "Walk"))
                    else 50, sheet.f.input("int"))
        sheet.formula(row, 6,
                      f'=SUMIFS({dur},{dow},{i + 1},{wstart},'
                      f'{C.week_start_of("TODAY()")})',
                      sheet.f.calc("int"))
        row += 1
    row += 1
    row = sheet.note(row, "Rest days are planned days. A walk in the "
                          "template is part of the programme, not a "
                          "failure to train.", last_col, height=24)
    C.footer(sheet, cfg, last_col, row + 1)
    sheet.finish(freeze_row=3, gridlines=False)
    return sheet


def _td(days: int):
    import datetime as _dt
    return _dt.timedelta(days=days)
