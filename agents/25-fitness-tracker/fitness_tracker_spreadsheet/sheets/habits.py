"""10 Habit Tracker - twelve habits, a month grid, honest streaks.

Streaks run left to right through hidden helper rows: a tick adds one,
a blank resets, and a rest day ("R") carries the streak through without
counting as a done day - the single most common complaint about habit
trackers, handled.  The grid is start-date agnostic: pick any month.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import col_letter
from ..writer import SheetWriter, date_check
from . import common as C

NAME = "10 Habit Tracker"

DAYS = 31
DAY_COL0 = 1                      # column B is day 1
SUM_COL0 = DAY_COL0 + DAYS + 1    # two columns of breathing room


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary_mid)
    last_col = SUM_COL0 + 5
    sheet.banner("10  Habit Tracker",
                 "Twelve habits you name yourself, a month at a time - "
                 "rest days protect the streak instead of breaking it.",
                 last_col)
    row = 4
    row = sheet.field(row, "Month on the grid",
                      _month_start(cfg) , style="date",
                      name="HabitMonth", validate=date_check(),
                      label_col=0, value_col=2,
                      help_text="The first day of any month. Ticks: x = "
                                "done, R = planned rest (keeps the "
                                "streak, does not add to it).")
    head_row = row + 1            # 0 based row of the ddd header
    date_row = row                # hidden row carrying real dates
    grid_first = head_row + 1
    grid_last = grid_first + 11
    help_row = grid_last + 1      # hidden streak helpers

    # hidden date row + weekday header
    for d in range(1, DAYS + 1):
        col = DAY_COL0 + d - 1
        sheet.formula(date_row, col,
                      f'=IF({d}>DAY(EOMONTH(HabitMonth,0)),"",'
                      f'HabitMonth+{d}-1)',
                      sheet.f.calc("int"))
        sheet.formula(head_row, col,
                      f'=IF({d}>DAY(EOMONTH(HabitMonth,0)),"",TEXT('
                      f'HabitMonth+{d}-1,"ddd"))',
                      sheet.f.calc("flag"))
        sheet.set_col(col, col, 4.2)
    sheet.ws.set_row(date_row, 6, None, {"hidden": True})
    sheet.write(head_row, 0, "Habit", sheet.f.chrome("header_left"))
    sheet.set_col(0, 0, 26)

    tick_validate = {"validate": "list", "source": ["x", "R"],
                     "ignore_blank": True}
    ticks = sample_ticks(cfg) if cfg.include_sample_data else {}
    for h in range(12):
        r = grid_first + h
        sheet.formula(r, 0, f'=INDEX(ListHabits,{h + 1})',
                      sheet.f.calc("text"))
        for d in range(1, DAYS + 1):
            col = DAY_COL0 + d - 1
            value = ticks.get((h, d))
            if value:
                sheet.write(r, col, value, sheet.f.input("flag"))
            else:
                sheet.write(r, col, None, sheet.f.input("flag"))
        sheet.ws.data_validation(r, DAY_COL0, r, DAY_COL0 + DAYS - 1,
                                 tick_validate)
        # hidden streak helper row
        for d in range(1, DAYS + 1):
            col = DAY_COL0 + d - 1
            tick = f"{col_letter(col)}{r + 1}"
            prev = (f"{col_letter(col - 1)}{help_row + 1}" if d > 1
                    else "0")
            sheet.formula(help_row + h, col,
                          f'=IF({col_letter(col)}{head_row + 1}="","",'
                          f'IF({tick}="R",{prev},IF({tick}<>"",IF({prev}='
                          f'"",1,{prev}+1),0)))',
                          sheet.f.calc("int"))
        sheet.ws.set_row(help_row + h, 6, None, {"hidden": True})

    # summary columns
    heads = ["Current streak", "Best streak", "Done %", "This week",
             "Rest days"]
    for i, text in enumerate(heads):
        sheet.write(head_row, SUM_COL0 + i, text, sheet.f.chrome("header"))
        sheet.set_col(SUM_COL0 + i, SUM_COL0 + i, 11)
    anchor = ('IF(EOMONTH(HabitMonth,0)<TODAY(),DAY(EOMONTH(HabitMonth,0)),'
              'IF(HabitMonth>TODAY(),0,DAY(TODAY())))')
    for h in range(12):
        r = grid_first + h
        tick_rng = f"{col_letter(DAY_COL0)}{r + 1}:" \
                   f"{col_letter(DAY_COL0 + DAYS - 1)}{r + 1}"
        help_rng = f"{col_letter(DAY_COL0)}{help_row + h + 1}:" \
                   f"{col_letter(DAY_COL0 + DAYS - 1)}{help_row + h + 1}"
        date_rng = f"{col_letter(DAY_COL0)}{date_row + 1}:" \
                   f"{col_letter(DAY_COL0 + DAYS - 1)}{date_row + 1}"
        sheet.formula(r, SUM_COL0,
                      f'=IF({anchor}=0,0,INDEX({help_rng},{anchor}))',
                      sheet.f.calc("int"))
        sheet.formula(r, SUM_COL0 + 1, f'=MAX({help_rng})',
                      sheet.f.calc("int"))
        sheet.formula(r, SUM_COL0 + 2,
                      f'=IF({anchor}=0,"",COUNTIF({tick_rng},"x")/MAX(1,'
                      f'{anchor}-COUNTIF({tick_rng},"R")))',
                      sheet.f.calc("percent0"))
        sheet.formula(r, SUM_COL0 + 3,
                      f'=COUNTIFS({date_rng},">="&{C.week_start_of("TODAY()")},'
                      f'{date_rng},"<="&{C.week_start_of("TODAY()")}+6,'
                      f'{tick_rng},"x")',
                      sheet.f.calc("int"))
        sheet.formula(r, SUM_COL0 + 4, f'=COUNTIF({tick_rng},"R")',
                      sheet.f.calc("int"))
    sheet.ws.conditional_format(grid_first, SUM_COL0 + 2, grid_last,
                                SUM_COL0 + 2,
                                {"type": "cell", "criteria": ">=",
                                 "value": 0.8,
                                 "format": sheet.f.cf("good")})

    # today marker across the grid
    sheet.ws.conditional_format(
        grid_first, DAY_COL0, grid_last, DAY_COL0 + DAYS - 1,
        {"type": "formula",
         "criteria": f"=AND({col_letter(DAY_COL0)}${date_row + 1}=TODAY(),"
                     f"{col_letter(DAY_COL0)}${date_row + 1}<>\"\")",
         "format": sheet.f.cf("info")})

    row = help_row + 12 + 1
    row = sheet.section(row, "WEEKLY CONSISTENCY SCORECARD", last_col)
    row = sheet.table_head(row, 0, ["Habit", "Week 1", "Week 2", "Week 3",
                                    "Week 4", "Week 5"],
                           widths=[26, 9, 9, 9, 9, 9])
    for h in range(12):
        r = grid_first + h
        tick_rng = f"{col_letter(DAY_COL0)}{r + 1}:" \
                   f"{col_letter(DAY_COL0 + DAYS - 1)}{r + 1}"
        date_rng = f"{col_letter(DAY_COL0)}{date_row + 1}:" \
                   f"{col_letter(DAY_COL0 + DAYS - 1)}{date_row + 1}"
        sheet.formula(row, 0, f"=INDEX(ListHabits,{h + 1})",
                      sheet.f.calc("text"))
        for w in range(5):
            ws_expr = f"HabitMonth-WEEKDAY(HabitMonth,IF(WeekStart=" \
                      f'"Sunday",1,2))+1+{7 * w}'
            we_expr = f"{ws_expr}+6"
            days_in = f'COUNTIFS({date_rng},">="&{ws_expr},{date_rng},' \
                      f'"<="&{we_expr})'
            rests = f'COUNTIFS({date_rng},">="&{ws_expr},{date_rng},' \
                    f'"<="&{we_expr},{tick_rng},"R")'
            dones = f'COUNTIFS({date_rng},">="&{ws_expr},{date_rng},' \
                    f'"<="&{we_expr},{tick_rng},"x")'
            sheet.formula(row, 1 + w,
                          f'=IF({days_in}=0,"",{dones}/MAX(1,{days_in}-'
                          f'{rests}))',
                          sheet.f.calc("percent0"))
        row += 1
    row += 1
    row = sheet.section(row, "ROUTINE CHECKLIST (MORNING OR EVENING)",
                        last_col)
    checklist = ["Glass of water before coffee", "5 minutes of mobility",
                 "Protein at breakfast", "Walk after lunch",
                 "Screen off 30 min before bed"]
    for item in checklist:
        sheet.write(row, 0, item, sheet.f.input("text"))
        sheet.merge(row, 1, last_col,
                    "tick it in the grid as its own habit if you want "
                    "the streak maths", sheet.f.chrome("note"))
        row += 1
    row += 1
    C.footer(sheet, cfg, last_col, row)
    sheet.finish(freeze_row=grid_first, freeze_col=1, gridlines=False,
                 print_area=f"$A$1:${col_letter(last_col)}"
                            f"${grid_last + 27}")
    return sheet


def _month_start(cfg: Config):
    import datetime as _dt
    if cfg.include_sample_data:
        return _dt.date(cfg.today.year, cfg.today.month, 1)
    return None


def sample_ticks(cfg: Config):
    """A believable month of ticks and planned rests for the demo file."""
    import datetime as _dt
    ticks = {}
    today = cfg.today
    if today.month == 12:
        return ticks
    patterns = {
        0: lambda d: d % 2 == 0,              # train as planned
        1: lambda d: d % 3 != 0,              # steps
        2: lambda d: True,                    # protein
        3: lambda d: d % 4 != 1,              # water
        4: lambda d: d % 5 != 2,              # sleep
        5: lambda d: d % 7 not in (0, 6),     # no liquid calories
        6: lambda d: d % 2 == 1,              # mobility
        7: lambda d: True,                    # log meals
        8: lambda d: d % 6 != 3,              # early night
        9: lambda d: d % 2 == 0,              # morning walk
        10: lambda d: d % 7 in (1, 3, 5),     # strength
        11: lambda d: d % 3 == 0,             # veg at dinner
    }
    rests = {0: (6, 13, 20, 27), 10: (7, 14, 21, 28)}
    for h, fn in patterns.items():
        for d in range(1, DAYS + 1):
            day = _dt.date(today.year, today.month, d)
            if day > today:
                continue
            if d in rests.get(h, ()):
                ticks[(h, d)] = "R"
            elif fn(d):
                ticks[(h, d)] = "x"
    return ticks
