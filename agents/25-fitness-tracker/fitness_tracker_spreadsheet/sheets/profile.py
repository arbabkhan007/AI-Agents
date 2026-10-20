"""2 Profile & Goals - who is training, and six independent goals.

BMI, BMR (Mifflin-St Jeor) and TDEE are shipped as estimates the buyer
can overwrite - the workbook never tells anyone what to eat.  Each of
the six goals carries its own target, deadline and progress maths; a
weight goal reads the latest weigh-in by itself.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import col_letter, quote_sheet
from ..writer import SheetWriter, date_check, list_from, number_check
from . import common as C

NAME = "2 Profile & Goals"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary, landscape=False)
    last_col = 9
    sheet.banner("2  Profile & Goals",
                 "Your numbers, your targets - every estimate on this "
                 "page can be typed over.", last_col)
    q = quote_sheet(NAME)
    row = 4
    row = sheet.section(row, "PROFILE", last_col)

    rows = {}

    def field(label, key, value=None, **kw):
        nonlocal row
        rows[key] = row          # 0 based row of the value cell
        row = sheet.field(row, label, value, **kw)

    field("Name", "name", "Maya" if cfg.include_sample_data else None,
          value_end=5, help_text="Optional. The print headers use it.")
    field("Sex", "sex", cfg.sex, validate=list_from("ListSex"),
          name="Sex",
          help_text="Used only by the BMR constant and the optional "
                    "Navy body-fat formula.")
    field("Age", "age", cfg.age_years if cfg.include_sample_data else None,
          style="int", name="AgeYears",
          validate=number_check(10, 100, False))
    field(f"Height ({cfg.length_unit})", "height",
          _len(cfg, cfg.height_cm) if cfg.include_sample_data else None,
          style="number1", validate=number_check(80, 250))
    field("Height unit stamp", "height_stamp",
          "cm" if cfg.metric else "in",
          validate={"validate": "list", "source": ["cm", "in"],
                    "ignore_blank": True},
          help_text="Stamp the unit you typed; switching the workbook "
                    "unit never misreads it.")
    field("Starting weight", "start_w",
          _wt(cfg, cfg.start_weight_kg) if cfg.include_sample_data
          else None, style="number1", validate=number_check(20, 400))
    field("Starting weight stamp", "start_stamp",
          "kg" if cfg.metric else "lb",
          validate={"validate": "list", "source": ["kg", "lb"],
                    "ignore_blank": True})
    field("Goal weight", "goal_w",
          _wt(cfg, cfg.goal_weight_kg) if cfg.include_sample_data
          else None, style="number1", validate=number_check(20, 400))
    field("Goal weight stamp", "goal_stamp",
          "kg" if cfg.metric else "lb",
          validate={"validate": "list", "source": ["kg", "lb"],
                    "ignore_blank": True})
    field("Target date", "goal_date",
          _plus_months(cfg.today, 4) if cfg.include_sample_data else None,
          style="date", name="GoalDate", validate=date_check())
    field("Activity level", "activity", cfg.activity_level,
          validate=list_from("ListActivityLevel"), name="ActivityLevel")
    row += 1

    book.define_name("HeightCm", "=" + C.cm_from(
        f"{q}!$D${rows['height'] + 1}", f"{q}!$D${rows['height_stamp'] + 1}"))
    book.define_name("StartKg", "=" + C.kg_from(
        f"{q}!$D${rows['start_w'] + 1}",
        f"{q}!$D${rows['start_stamp'] + 1}"))
    book.define_name("GoalKg", "=" + C.kg_from(
        f"{q}!$D${rows['goal_w'] + 1}",
        f"{q}!$D${rows['goal_stamp'] + 1}"))

    row = sheet.section(row, "ESTIMATES (YOURS TO OVERWRITE)", last_col)
    row = sheet.field(row, "BMI",
                      formula='IF(OR(HeightCm=0,StartKg="",StartKg=0),"",'
                              'StartKg/(HeightCm/100)^2)',
                      style="number1",
                      help_text="A population statistic, not a verdict "
                                "on an individual.")
    row = sheet.field(row, "BMR (Mifflin-St Jeor)",
                      formula='IF(OR(HeightCm=0,AgeYears="",StartKg=""),'
                              '"",10*StartKg+6.25*HeightCm-5*AgeYears+IF('
                              'Sex="Male",5,IF(Sex="Female",-161,-78)))',
                      style="int", name="BMR",
                      help_text="Calories at complete rest. An estimate.")
    row = sheet.field(row, "TDEE (BMR x activity)",
                      formula='IF(BMR="","",BMR*INDEX(MultTable,MATCH('
                              'ActivityLevel,ListActivityLevel,0),2))',
                      style="int", name="TDEE",
                      help_text="The maintenance estimate paid apps "
                                "show. Type your own number over the "
                                "targets on Settings any time.")
    row = sheet.field(row, "Target vs TDEE",
                      formula='IF(OR(TDEE="",CalTarget=""),"","Your '
                              'calorie target sits "&TEXT(ABS(TDEE-'
                              'CalTarget),"0")&" kcal "&IF(TDEE>CalTarget,'
                              '"below","above")&" the estimate - a "&'
                              'TEXT(IF(TDEE=0,0,ABS(TDEE-CalTarget)/TDEE),'
                              '"0%")&" "&IF(TDEE>CalTarget,"deficit",'
                              '"surplus")&", your call to make.")',
                      style="text", help_text="Arithmetic, not advice.")
    row += 1

    row = sheet.section(row, "SIX GOALS, EACH WITH ITS OWN TARGET",
                        last_col)
    row = sheet.table_head(row, 0, ["Type", "What it means", "Start",
                                    "Target", "Deadline", "Current",
                                    "Auto / current", "Progress", "To go",
                                    "Status"],
                           widths=[13, 28, 9, 9, 12, 10, 11, 10, 9, 12])
    goals = _sample_goals(cfg) if cfg.include_sample_data else [{}] * 6
    first_goal = row
    for i in range(6):
        goal = goals[i] if i < len(goals) else {}
        sheet.write(row, 0, goal.get("type"), sheet.f.input("text"))
        sheet.ws.data_validation(row, 0, row, 0, list_from("ListGoalType"))
        sheet.write(row, 1, goal.get("desc"), sheet.f.input("wrap"))
        sheet.write(row, 2, goal.get("start"), sheet.f.input("number1"))
        sheet.write(row, 3, goal.get("target"), sheet.f.input("number1"))
        sheet.write(row, 4, goal.get("deadline"), sheet.f.input("date"))
        sheet.write(row, 5, goal.get("current"), sheet.f.input("number1"))
        sheet.formula(row, 6,
                      f'=IF($A{row + 1}="","",IF($A{row + 1}="Weight",'
                      f'{_latest_weight()},IF($F{row + 1}="","",'
                      f'$F{row + 1})))',
                      sheet.f.calc("number1"))
        sheet.formula(row, 7,
                      f'=IF(OR($G{row + 1}="",$C{row + 1}="",$D{row + 1}='
                      f'"",$D{row + 1}=$C{row + 1}),"",($G{row + 1}-'
                      f'$C{row + 1})/($D{row + 1}-$C{row + 1}))',
                      sheet.f.calc("percent0"))
        sheet.formula(row, 8,
                      f'=IF(OR($G{row + 1}="",$D{row + 1}=""),"",'
                      f'$D{row + 1}-$G{row + 1})',
                      sheet.f.calc("number1"))
        sheet.formula(row, 9,
                      f'=IF($H{row + 1}="","",IF($H{row + 1}>=1,'
                      f'"achieved",IF($E{row + 1}="","in progress",IF('
                      f'TODAY()>$E{row + 1},"past due","in progress"))))',
                      sheet.f.calc("status"))
        row += 1
    for gname, gcol in [("GoalTypes", 0), ("GoalDescs", 1),
                        ("GoalProgress", 7), ("GoalToGo", 8),
                        ("GoalStatus", 9)]:
        letter = col_letter(gcol)
        book.define_name(gname, f"={q}!${letter}${first_goal + 1}:"
                                f"${letter}${first_goal + 6}")
    sheet.ws.conditional_format(first_goal, 9, row - 1, 9,
                                {"type": "text", "criteria": "containing",
                                 "value": "achieved",
                                 "format": sheet.f.cf("bold_good")})
    sheet.ws.conditional_format(first_goal, 9, row - 1, 9,
                                {"type": "text", "criteria": "containing",
                                 "value": "past due",
                                 "format": sheet.f.cf("warn")})
    row += 1
    row = sheet.note(row, "A weight goal reads your latest weigh-in by "
                          "itself; every other goal takes the current "
                          "value from the cream cell so you decide what "
                          "counts.", last_col, height=26)
    C.footer(sheet, cfg, last_col, row + 1)
    sheet.finish(freeze_row=3, gridlines=False)
    return sheet


def _len(cfg: Config, cm: float) -> float:
    return round(cm if cfg.metric else cm / 2.54, 1)


def _wt(cfg: Config, kg: float) -> float:
    return round(kg if cfg.metric else kg / 0.45359237, 1)


def _plus_months(day, months: int):
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    return day.replace(year=year, month=month, day=min(day.day, 28))


def _latest_weight() -> str:
    return ('IFERROR(INDEX([[8 Weight Tracker.ma7_disp]],MATCH(MAX('
            '[[8 Weight Tracker.date]]),[[8 Weight Tracker.date]],0)),"")')


def _sample_goals(cfg):
    t = cfg.today
    return [
        {"type": "Weight", "desc": "Reach the goal weight on the scale",
         "start": _wt(cfg, cfg.start_weight_kg),
         "target": _wt(cfg, cfg.goal_weight_kg),
         "deadline": _plus_months(t, 4), "current": None},
        {"type": "Strength", "desc": "Squat five reps at bodyweight",
         "start": 40.0, "target": _wt(cfg, cfg.start_weight_kg),
         "deadline": _plus_months(t, 6), "current": 55.0},
        {"type": "Consistency", "desc": "Sessions a week, 4-week average",
         "start": 1.0, "target": 4.0, "deadline": _plus_months(t, 3),
         "current": 3.0},
        {"type": "Distance", "desc": "Run 10 km without stopping",
         "start": 5.0, "target": 10.0, "deadline": _plus_months(t, 5),
         "current": 7.0},
        {"type": "Habit", "desc": "Protein at every meal, weekly rate",
         "start": 0.4, "target": 0.9, "deadline": _plus_months(t, 2),
         "current": 0.7},
        {"type": "Custom", "desc": "Morning mobility, minutes a week",
         "start": 0.0, "target": 60.0, "deadline": _plus_months(t, 2),
         "current": 25.0},
    ]
