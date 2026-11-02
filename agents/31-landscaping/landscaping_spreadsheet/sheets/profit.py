"""21. Profit Analysis - the month-by-month truth.

Fourteen rows, one per month, every figure calculated. Revenue from
completed jobs, labour from the timesheets, materials and overheads
from the expenses, fuel from the vehicle tracker - and what is left.

The useful column is the one on the right: profit per crew hour.
Revenue can grow while that number shrinks, and when it does you are
working harder for less. No other single figure in this trade is
worth as much attention.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, loss_cf, money_cf, scale_cf,
                     zero)

NAME = "Profit Analysis"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Profit Analysis",
        subtitle="Month by month: what came in, what went out, what "
                 "was left, and what each crew hour earned.",
        tab_color=Palette.deep,
        rows=cfg.row_count("profit"),
        samples=sample("profit", cfg),
        freeze_cols=2,
        help_text=(
            "Choose a month in the first column and every figure on "
            "the row fills itself in from the registers. Nothing "
            "here is typed except the month and your own target. "
            "Fourteen rows gives you a full year plus the two months "
            "either side for comparison."),
        extra_notes=[
            "Revenue counts completed jobs only, excluding tax. Tax "
            "collected is never yours and does not belong in a "
            "profit figure.",
            "Period costs count material purchases, not usage; job "
            "costing counts usage. Collected uses the last paid date "
            "for the cumulative amount, not a payment ledger.",
            "Labour is what the timesheets cost, including the hours "
            "that were not billable. Driving and yard time are real "
            "wages and leaving them out is the most common way a "
            "landscaping business flatters itself.",
            "Profit per crew hour is the number to watch across the "
            "season. If it falls while revenue rises, the extra work "
            "is not paying for itself.",
        ],
        columns=[
            Col("month", "Month", 11, "text",
                validate={"validate": "list", "source": "=MonthKeys",
                          "input_message": "Pick a month in yyyy-mm "
                                           "form."},
                note="Pick the month. Everything else follows."),
            Col("label", "Period", 14, "text",
                formula='=IF({month}{r}="","",'
                        'TEXT(DATE(VALUE(LEFT({month}{r},4)),'
                        'VALUE(RIGHT({month}{r},2)),1),'
                        '"mmmm yyyy"))'),
            Col("start_num", "From", 10, "number",
                formula=zero("month",
                             'DATE(VALUE(LEFT({month}{r},4)),'
                             'VALUE(RIGHT({month}{r},2)),1)'),
                hidden=True),
            Col("end_num", "To", 10, "number",
                formula=zero("month",
                             'DATE(VALUE(LEFT({month}{r},4)),'
                             'VALUE(RIGHT({month}{r},2))+1,1)-1'),
                hidden=True),

            # ---- money in --------------------------------------------
            Col("jobs_done", "Visits done", 11, "int",
                formula=zero("month",
                             'COUNTIFS([[Job & Work Orders.month]],'
                             '{month}{r},'
                             '[[Job & Work Orders.is_done]],1)'),
                cf=scale_cf()),
            Col("revenue", "Revenue", 12, "money",
                formula=zero("month",
                             'ROUND(SUMIFS('
                             '[[Job & Work Orders.charge]],'
                             '[[Job & Work Orders.month]],{month}{r},'
                             '[[Job & Work Orders.is_done]],1)+'
                             'SUMIFS([[Job & Work Orders.extras]],'
                             '[[Job & Work Orders.month]],{month}{r},'
                             '[[Job & Work Orders.is_done]],1),2)'),
                cf=money_cf(),
                note="Completed visits, excluding tax."),
            Col("invoiced", "Invoiced", 12, "money",
                formula=zero("month",
                             'SUMIFS([[Invoice & Payments.total]],'
                             '[[Invoice & Payments.month]],'
                             '{month}{r})'),
                note="What you billed in the month, which is not the "
                     "same thing as what you earned in it."),
            Col("collected", "Collected", 12, "money",
                formula=zero("month",
                             'SUMIFS([[Invoice & Payments.paid]],'
                             '[[Invoice & Payments.paid_num]],">="&{start_num}{r},'
                             '[[Invoice & Payments.paid_num]],"<="&{end_num}{r})'),
                note="Cumulative paid amount grouped by last paid date; "
                     "partial payments in different months are not tracked separately."),

            # ---- money out -------------------------------------------
            Col("labour", "Labour", 11, "money",
                formula=zero("month",
                             'SUMIFS([[Timesheets & Payroll.cost]],'
                             '[[Timesheets & Payroll.month]],'
                             '{month}{r})+'
                             'SUMIFS([[Job & Work Orders.labour_fallback]],'
                             '[[Job & Work Orders.month]],{month}{r})'),
                note="Timesheets plus job-hour fallback where no job "
                     "timesheet hours exist."),
            Col("materials", "Materials", 11, "money",
                formula=zero("month",
                             'SUMIFS([[Expense Tracker.period_cost]],'
                             '[[Expense Tracker.month]],{month}{r},'
                             '[[Expense Tracker.category]],'
                             '"Materials")'),
                note="Bought in the month, from the expense tracker."),
            Col("fuel", "Fuel & vehicles", 13, "money",
                formula=zero("month",
                             'SUMIFS('
                             '[[Vehicle & Fuel Tracker.amount]],'
                             '[[Vehicle & Fuel Tracker.month]],'
                             '{month}{r})'),
                note="Everything on the vehicle tracker - fuel, "
                     "repairs, tax and insurance."),
            Col("other_costs", "Other costs", 12, "money",
                formula=zero("month",
                             'ROUND(SUMIFS('
                             '[[Expense Tracker.period_cost]],'
                             '[[Expense Tracker.month]],{month}{r})-'
                             'SUMIFS([[Expense Tracker.period_cost]],'
                             '[[Expense Tracker.month]],{month}{r},'
                             '[[Expense Tracker.category]],'
                             '"Materials"),2)'),
                note="Everything else on the expense tracker - "
                     "insurance, rent, advertising, the accountant."),
            Col("total_costs", "Total costs", 12, "money",
                formula=zero("month",
                             'ROUND({labour}{r}+{materials}{r}+'
                             '{fuel}{r}+{other_costs}{r},2)')),

            # ---- what is left ----------------------------------------
            Col("profit", "Profit", 12, "money",
                formula=zero("month",
                             'ROUND({revenue}{r}-{total_costs}{r},2)'),
                cf=loss_cf(),
                note="Revenue less everything. The number that pays "
                     "you."),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({month}{r}="","",'
                        'IF({revenue}{r}<=0,"",'
                        'ROUND({profit}{r}/'
                        '{revenue}{r},4)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=TargetMargin", "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": "<",
                     "value": "=MinMargin", "fmt": "bad"}]),
            Col("hours", "Crew hours", 11, "number1",
                formula=zero("month",
                             'SUMIFS([[Timesheets & Payroll.hours]],'
                             '[[Timesheets & Payroll.month]],'
                             '{month}{r})')),
            Col("billable_hours", "Billable hrs", 11, "number1",
                formula=zero("month",
                             'SUMIFS([[Timesheets & Payroll.hours]],'
                             '[[Timesheets & Payroll.month]],'
                             '{month}{r},'
                             '[[Timesheets & Payroll.is_billable]],'
                             '1)')),
            Col("billable_pct", "Billable %", 10, "percent",
                formula='=IF({month}{r}="","",'
                        'IF({hours}{r}<=0,"",'
                        'ROUND({billable_hours}{r}/'
                        '{hours}{r},4)))',
                cf=[{"type": "cell", "criteria": ">=", "value": 0.75,
                     "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0.55,
                     "fmt": "bad"}],
                note="How much of the paid day was sold. The quiet "
                     "killer in this trade."),
            Col("revenue_hour", "Revenue / hour", 12, "money",
                formula='=IF({month}{r}="","",'
                        'IF({hours}{r}<=0,"",'
                        'ROUND({revenue}{r}/'
                        '{hours}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}]),
            Col("profit_hour", "Profit / hour", 12, "money",
                formula='=IF({month}{r}="","",'
                        'IF({hours}{r}<=0,"",'
                        'ROUND({profit}{r}/'
                        '{hours}{r},2)))',
                cf=loss_cf(),
                note="The single most useful number on the tab. Watch "
                     "it across a season."),
            Col("avg_job", "Average visit", 12, "money",
                formula='=IF({month}{r}="","",'
                        'IF({jobs_done}{r}<=0,"",'
                        'ROUND({revenue}{r}/'
                        '{jobs_done}{r},2)))'),
            Col("new_customers", "New customers", 12, "int",
                formula=zero("month",
                             'COUNTIFS([[Customer CRM.first_job]],'
                             '">="&{start_num}{r},'
                             '[[Customer CRM.first_job]],'
                             '"<="&{end_num}{r})')),
            Col("target", "Your target", 11, "money",
                validate={"validate": "decimal", "criteria": "between",
                          "minimum": 0, "maximum": 10000000,
                          "error_title": "Monthly target",
                          "error_message": "What you want this month "
                                           "to bring in. Blank uses "
                                           "the yearly target divided "
                                           "by twelve."},
                note="Your number for this month. Blank falls back to "
                     "a twelfth of the annual target on Settings."),
            Col("target_used", "Target used", 11, "money",
                formula=zero("month",
                             'IF({target}{r}>0,{target}{r},'
                             'ROUND(RevenueTarget/12,2))'),
                hidden=True),
            Col("vs_target", "vs target", 11, "money",
                formula=zero("month",
                             'ROUND({revenue}{r}-'
                             '{target_used}{r},2)'),
                cf=loss_cf()),
            Col("target_pct", "% of target", 10, "percent",
                formula='=IF({month}{r}="","",'
                        'IF({target_used}{r}<=0,"",'
                        'ROUND({revenue}{r}/'
                        '{target_used}{r},4)))',
                cf=[{"type": "cell", "criteria": ">=", "value": 1,
                     "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0.8,
                     "fmt": "bad"}]),
            Col("notes", "Notes", 30, "wrap",
                note="Why the month went the way it did. 'Three weeks "
                     "of rain' explains a lot, a year later."),

            Col("alert", "What it is telling you", 44, "wrap",
                formula=alert_chain("month", [
                    ('{profit}{r}<0',
                     "Loss - this month cost more than it earned"),
                    ('AND({revenue}{r}>0,{margin_pct}{r}<>"",'
                     '{margin_pct}{r}<MinMargin)',
                     "Urgent - margin below your floor"),
                    ('AND({hours}{r}>0,{billable_pct}{r}<>"",'
                     '{billable_pct}{r}<0.55)',
                     "Check - too much of the paid day was not sold"),
                    ('AND({revenue}{r}>0,{target_pct}{r}<>"",'
                     '{target_pct}{r}<0.8)',
                     "Action - well under target for the month"),
                    ('AND({revenue}{r}>0,{collected}{r}<'
                     '{invoiced}{r}*0.7)',
                     "Chase - a lot of what you invoiced is still "
                     "out"),
                    ('AND({revenue}{r}>0,{margin_pct}{r}<>"",'
                     '{margin_pct}{r}<TargetMargin)',
                     "Thin margin - under target, above the floor"),
                    ('AND({revenue}{r}=0,{month}{r}<>"")',
                     "Add - no completed work recorded this month"),
                    ('AND({target_pct}{r}<>"",{target_pct}{r}>=1)',
                     "OK - target met"),
                ]),
                cf=alert_cf()),
        ],
    )
