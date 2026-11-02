"""13. Timesheets & Payroll - the hours, and what they really cost.

Every line is one person, one day, and usually one job. Hours booked
against a Job ID flow straight into that job's actual cost, which is
what makes the estimated-versus-actual comparison possible at all.

Hours that are not against a job - driving, yard time, mending a
mower, quoting - still cost money and are still recorded here. They
are what the billable percentage measures, and that percentage
explains more bad months than any other number in the workbook.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, time_check
from .common import (alert_cf, alert_chain, amount, date_num_col, id_col,
                     lookup_crew, money_cf,
                     month_col, pick, scale_cf, week_start_col,
                     weekday_col, yesno, zero)

NAME = "Timesheets & Payroll"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Timesheets & Payroll",
        subtitle="Hours by person, by day and by job - costed at each "
                 "person's own rate, and fed back into job profit.",
        tab_color=Palette.primary_mid,
        rows=cfg.row_count("timesheets"),
        samples=sample("timesheets", cfg),
        freeze_cols=3,
        help_text=(
            "One line per person per job per day. Put the Job ID on "
            "it and the hours cost that job automatically. Leave the "
            "Job ID blank for travel, yard work or anything else that "
            "is not chargeable - it still costs you, and it still "
            "belongs here."),
        extra_notes=[
            "Hours can be entered either as a start and finish time "
            "or as a plain number of hours. If both are present the "
            "times win, because they are the harder thing to "
            "misremember.",
            "Overtime is worked out per person per week against the "
            "threshold on Settings, and costed at the multiplier. It "
            "is an indicator for your own planning, not a payroll "
            "calculation - overtime law varies and your payroll "
            "provider is the authority on it. Enter rows in chronological "
            "order for each employee and week: overtime is allocated in "
            "row order, so late backdated entries can change job costs.",
            "This tab does not file taxes, produce payslips or "
            "report to any payroll service. It records what was "
            "worked so that your job costs are honest.",
        ],
        columns=[
            id_col("date", '"TS-"', digits=5, header="Line"),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="Start here."),
            Col("employee", "Employee", 11, "id",
                validate=pick("CrewIDList",
                              "Pick the Employee ID from the Crew "
                              "Database."),
                note="Pick from the list. Their own cost rate is used."),
            Col("name", "Name", 20, "text",
                formula=lookup_crew("name")),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the job these hours were worked "
                              "on."),
                note="The job these hours belong to. Leave blank for "
                     "non-chargeable time - that is not a mistake, it "
                     "is the point of the billable column."),
            Col("job_address", "Where", 26, "text",
                formula='=IF({job}{r}="","",'
                        'IFERROR(INDEX('
                        '[[Job & Work Orders.address]],'
                        'MATCH({job}{r},'
                        '[[Job & Work Orders.id]],0))&"",'
                        '"Check - Job ID not found"))',
                cf=[{"type": "text", "criteria": "containing",
                     "value": "Check -", "fmt": "bad"}]),
            Col("task", "What they did", 22, "text",
                validate=pick("TaskTypeList",
                              "Mowing, driving, maintenance, quoting, "
                              "yard work."),
                note="Non-job time is worth classifying. It is where "
                     "the day goes."),
            Col("start_time", "Start", 9, "time",
                validate=time_check()),
            Col("end_time", "End", 9, "time",
                validate=time_check()),
            Col("break_mins", "Break", 8, "int",
                validate=amount(0, 480, decimal=False)),
            Col("hours_typed", "Hours", 9, "number1",
                validate=amount(0, 24,
                                "Hours worked, if you are not using "
                                "start and finish times."),
                note="Use this or the times, whichever suits. Not "
                     "both."),
            Col("hours", "Hours used", 11, "number1",
                formula=zero("date",
                             'IF(AND({start_time}{r}<>"",'
                             '{end_time}{r}<>""),'
                             'ROUND(MAX(0,MOD({end_time}{r}-'
                             '{start_time}{r},1)*24-'
                             '{break_mins}{r}/60),2),'
                             '{hours_typed}{r})'),
                cf=scale_cf(),
                note="From the times if they are there, otherwise the "
                     "typed figure."),
            Col("week_hours", "Week to date", 12, "number1",
                formula=zero("date",
                             'SUMIFS({hours_first}:{hours_last},'
                             '{employee_first}:{employee_last},'
                             '{employee}{r},'
                             '{week_start_first}:{week_start_last},'
                             '{week_start}{r})'),
                hidden=True,
                note="This person's hours in the same week, used to "
                     "work out where overtime starts."),
            Col("week_before", "Week before line", 12, "number1",
                formula=zero("date",
                             'SUMIFS({hours_first}:{hours}{r},'
                             '{employee_first}:{employee}{r},'
                             '{employee}{r},'
                             '{week_start_first}:{week_start}{r},'
                             '{week_start}{r})-{hours}{r}'),
                hidden=True),
            Col("overtime_hours", "Overtime", 10, "number1",
                formula=zero("date",
                             'ROUND(MAX(0,{week_before}{r}+'
                             '{hours}{r}-OvertimeAfter)-'
                             'MAX(0,{week_before}{r}-OvertimeAfter),2)'),
                cf=[{"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "warn"}],
                note="The part of this line that falls past the weekly "
                     "threshold on Settings."),
            Col("normal_hours", "Normal hours", 11, "number1",
                formula=zero("date",
                             'ROUND({hours}{r}-'
                             '{overtime_hours}{r},2)'),
                hidden=True),
            Col("rate", "Cost / hr", 10, "money",
                formula=zero("date",
                             'IF(IFERROR(INDEX('
                             '[[Crew Database.cost_rate]],'
                             'MATCH({employee}{r},'
                             '[[Crew Database.id]],0))*1,0)>0,'
                             'IFERROR(INDEX('
                             '[[Crew Database.cost_rate]],'
                             'MATCH({employee}{r},'
                             '[[Crew Database.id]],0))*1,0),'
                             'LabourRate)'),
                note="Their loaded rate from the Crew Database, or the "
                     "default on Settings if it is blank."),
            Col("ot_multiplier", "Overtime x", 10, "number1",
                formula=zero("date",
                             'IF(IFERROR(INDEX('
                             '[[Crew Database.overtime_rate]],'
                             'MATCH({employee}{r},'
                             '[[Crew Database.id]],0))*1,0)>0,'
                             'IFERROR(INDEX('
                             '[[Crew Database.overtime_rate]],'
                             'MATCH({employee}{r},'
                             '[[Crew Database.id]],0))*1,0),'
                             'OvertimeRate)'),
                hidden=True),
            Col("cost", "Cost", 11, "money",
                formula=zero("date",
                             'ROUND({normal_hours}{r}*{rate}{r}+'
                             '{overtime_hours}{r}*{rate}{r}*'
                             '{ot_multiplier}{r},2)'),
                cf=money_cf(),
                note="What this line costs the business. Lines with a "
                     "Job ID land on that job's actual cost."),
            Col("pay", "Gross pay", 11, "money",
                formula=zero("date",
                             'ROUND(({normal_hours}{r}+'
                             '{overtime_hours}{r}*'
                             '{ot_multiplier}{r})*'
                             'IFERROR(INDEX('
                             '[[Crew Database.pay_rate]],'
                             'MATCH({employee}{r},'
                             '[[Crew Database.id]],0))*1,0),2)'),
                note="At their wage rate, for your own reference. Not "
                     "a payslip, and no tax is calculated."),
            Col("mileage", "Miles driven", 11, "number1",
                validate=amount(0, 2000),
                note="Personal vehicle miles to reimburse, if that is "
                     "how you work."),
            Col("approved", "Approved", 10, "flag",
                validate=yesno("Have you checked and approved this "
                               "line?"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "No", "fmt": "warn"}]),
            Col("notes", "Notes", 26, "wrap"),

            # ---- the bits other tabs read ----------------------------
            Col("is_billable", "Billable", 8, "int",
                formula=zero("date",
                             'IF(AND({job}{r}<>"",{hours}{r}>0),1,0)'),
                hidden=True),
            Col("job_value", "Job value share", 12, "money",
                formula=zero("date",
                             'IF({is_billable}{r}=0,0,'
                             'ROUND(IFERROR(INDEX('
                             '[[Job & Work Orders.charge]],'
                             'MATCH({job}{r},'
                             '[[Job & Work Orders.id]],0))*1,0)*'
                             '{hours}{r}/MAX({hours}{r},SUMIFS('
                             '{hours_first}:{hours_last},'
                             '{job_first}:{job_last},{job}{r})),2))'),
                hidden=True,
                note="This line's share of what the job was worth, "
                     "split by hours. Used for the crew scorecard."),
            date_num_col("date", "date_num"),
            weekday_col("date", "dow", header="DOW"),
            week_start_col("date"),
            month_col("date"),

            Col("alert", "What needs doing", 42, "wrap",
                formula=alert_chain("date", [
                    ('{job_address}{r}="Check - Job ID not found"',
                     "Check - the Job ID on this line does not exist"),
                    ('{hours}{r}=0',
                     "Add - no hours on this line"),
                    ('{hours}{r}>14',
                     "Check - more than fourteen hours in one day"),
                    ('{rate}{r}=0',
                     "Add - no cost rate for this person"),
                    ('{overtime_hours}{r}>0',
                     "Over hours - part of this line is overtime"),
                    ('AND({job}{r}="",{task}{r}="")',
                     "Add - non-job time with no explanation"),
                    ('{approved}{r}<>"Yes"',
                     "Check - not approved yet"),
                ]),
                cf=alert_cf()),
        ],
    )
