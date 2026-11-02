"""12. Crew Schedule - who is working, and who is already busy.

This is the people side of the week, as opposed to the Route Planner
which is the stops side. One row per person per day: on, off, holiday
or sick, and how many hours they are down for.

The clash column is the point of the tab. It compares the hours
assigned to a person on a day against the jobs actually booked for
their crew that day, so a day that has been promised to two places at
once shows up before the morning it goes wrong.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, time_check
from .common import (alert_cf, alert_chain, amount, date_num_col, id_col,
                     lookup_crew, month_col, pick,
                     scale_cf, week_start_col, weekday_col,
                     yesno, zero)

NAME = "Crew Schedule"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Crew Schedule",
        subtitle="Who is available, who is off, and whether the day "
                 "you have planned actually fits in the hours.",
        tab_color=Palette.primary_mid,
        rows=cfg.row_count("schedule"),
        samples=sample("schedule", cfg),
        freeze_cols=3,
        help_text=(
            "One row per person per working day. Put the date, pick "
            "the person, and say whether they are working. The "
            "'Planned hours' column adds up the jobs already booked "
            "for their crew that day, so you can see at a glance "
            "whether the day is full, empty or impossible."),
        extra_notes=[
            "You do not need a row for every person every day. Most "
            "businesses fill this in a week ahead for the days that "
            "are unusual - holidays, half days, somebody covering "
            "another crew - and leave the ordinary days blank.",
            "Planned hours counts every open job booked to that crew "
            "on that date, using the estimated hours from the "
            "catalogue. Capacity is their available hours. When "
            "planned is bigger than capacity, something will be late.",
        ],
        columns=[
            id_col("date", '"SCH-"', digits=5, header="Line",
                   note="Just a line number, so two identical rows can "
                        "still be told apart."),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="Start here."),
            Col("weekday", "Day", 8, "text",
                formula='=IF({date}{r}="","",'
                        'TEXT({date}{r},"ddd"))'),
            Col("employee", "Employee", 11, "id",
                validate=pick("CrewIDList",
                              "Pick the Employee ID from the Crew "
                              "Database."),
                note="Pick from the list, never type it."),
            Col("name", "Name", 20, "text",
                formula=lookup_crew("name")),
            Col("crew", "Crew", 12, "text",
                validate=list_from("CrewNameList"),
                note="Which truck they are on that day. It is not "
                     "always their usual one."),
            Col("working", "Working", 10, "flag",
                validate=yesno("Are they available for work on this "
                               "day?"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "No", "fmt": "muted"}]),
            Col("reason", "If not, why", 18, "text",
                validate=pick("AbsenceList",
                              "Holiday, sick, training, weather, or a "
                              "day off."),
                note="Six months of this column tells you what your "
                     "real available workforce is, as opposed to the "
                     "one on paper."),
            Col("start_time", "Start", 9, "time",
                validate=time_check()),
            Col("end_time", "End", 9, "time",
                validate=time_check()),
            Col("break_mins", "Break (mins)", 11, "int",
                validate=amount(0, 480, decimal=False)),
            Col("capacity", "Available hrs", 12, "number1",
                formula=zero("date",
                             'IF({working}{r}<>"Yes",0,'
                             'IF(AND({start_time}{r}<>"",'
                             '{end_time}{r}<>""),'
                             'ROUND(({end_time}{r}-{start_time}{r})*24-'
                             '{break_mins}{r}/60,2),WorkingHours))'),
                note="Worked out from the times if you gave them, "
                     "otherwise the standard working day on Settings."),
            Col("planned", "Planned hrs", 11, "number1",
                formula=zero("date",
                             'ROUND(SUMIFS('
                             '[[Job & Work Orders.hours_est]],'
                             '[[Job & Work Orders.date_num]],'
                             '{date}{r},'
                             '[[Job & Work Orders.crew]],{crew}{r},'
                             '[[Job & Work Orders.is_open]],1)/'
                             'MAX(1,CrewSize),2)'),
                cf=scale_cf(),
                note="Every open job booked to this crew on this date, "
                     "shared across the crew. Automatic."),
            Col("jobs_count", "Jobs booked", 11, "int",
                formula=zero("date",
                             'COUNTIFS('
                             '[[Job & Work Orders.date_num]],{date}{r},'
                             '[[Job & Work Orders.crew]],{crew}{r},'
                             '[[Job & Work Orders.is_open]],1)')),
            Col("logged", "Hours logged", 12, "number1",
                formula=zero("date",
                             'SUMIFS('
                             '[[Timesheets & Payroll.hours]],'
                             '[[Timesheets & Payroll.date_num]],'
                             '{date}{r},'
                             '[[Timesheets & Payroll.employee]],'
                             '{employee}{r})'),
                note="What the timesheets say actually happened. The "
                     "other half of the comparison."),
            Col("spare", "Spare hrs", 10, "number1",
                formula='=IF({date}{r}="","",'
                        'ROUND({capacity}{r}-{planned}{r},2))',
                cf=[{"type": "cell", "criteria": "<", "value": -0.01,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": ">=", "value": 2,
                     "fmt": "info"}],
                note="Negative means the day does not fit. Positive by "
                     "a lot means there is room to sell another job."),
            Col("use_pct", "Day used", 9, "percent",
                formula='=IF({date}{r}="","",'
                        'IF({capacity}{r}<=0,"",'
                        'ROUND({planned}{r}/'
                        '{capacity}{r},4)))',
                cf=[{"type": "cell", "criteria": ">", "value": 1,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": ">=", "value": 0.8,
                     "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0.5,
                     "fmt": "warn"}]),
            Col("cost_rate", "Cost / hr", 10, "money",
                formula='=IF({employee}{r}="","",'
                        'IF(IFERROR(INDEX('
                        '[[Crew Database.cost_rate]],'
                        'MATCH({employee}{r},'
                        '[[Crew Database.id]],0))*1,0)>0,'
                        'IFERROR(INDEX([[Crew Database.cost_rate]],'
                        'MATCH({employee}{r},'
                        '[[Crew Database.id]],0))*1,0),LabourRate))',
                hidden=True),
            Col("day_cost", "Cost of day", 11, "money",
                formula=zero("date",
                             'ROUND({capacity}{r}*'
                             'IF({cost_rate}{r}="",LabourRate,'
                             '{cost_rate}{r}),2)'),
                note="What this person's day costs you whether or not "
                     "the work was sold. That is why empty days hurt."),
            Col("notes", "Notes", 28, "wrap"),

            Col("is_future", "Future", 7, "int",
                formula=zero("date",
                             'IF({date}{r}>=TodayDate,1,0)'),
                hidden=True),
            Col("is_over", "Over", 6, "int",
                formula=zero("date",
                             'IF(AND({working}{r}="Yes",'
                             '{spare}{r}<0),1,0)'),
                hidden=True),
            Col("is_idle", "Idle", 6, "int",
                formula=zero("date",
                             'IF(AND({working}{r}="Yes",'
                             '{is_future}{r}=1,{jobs_count}{r}=0),1,0)'),
                hidden=True),
            date_num_col("date", "date_num"),
            weekday_col("date", "dow", header="DOW"),
            week_start_col("date"),
            month_col("date"),

            Col("alert", "What needs doing", 42, "wrap",
                formula=alert_chain("date", [
                    ('AND({working}{r}="Yes",{spare}{r}<-1)',
                     "Clash - more work booked than hours in the day"),
                    ('AND({working}{r}<>"Yes",{jobs_count}{r}>0)',
                     "Urgent - jobs booked for a crew that is off"),
                    ('{is_over}{r}=1',
                     "Over hours - the day is slightly over, check it"),
                    ('{is_idle}{r}=1',
                     "Schedule - available and nothing booked"),
                    ('AND({working}{r}="Yes",{use_pct}{r}<>"",'
                     '{use_pct}{r}<0.5,{is_future}{r}=1)',
                     "Action - less than half the day is sold"),
                    ('AND({working}{r}<>"Yes",{reason}{r}="")',
                     "Add - marked unavailable with no reason"),
                    ('AND({is_future}{r}=0,{logged}{r}=0,'
                     '{working}{r}="Yes")',
                     "Missing - a worked day with no timesheet"),
                ]),
                cf=alert_cf()),
        ],
    )
