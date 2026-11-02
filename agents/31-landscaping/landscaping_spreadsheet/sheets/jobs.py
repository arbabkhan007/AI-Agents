"""8. Job & Work Orders - one row per visit, and the hub of the workbook.

Everything meets here. The customer and property say where; the
service says what; the timesheets say what the labour really cost;
the expenses say what was spent on site; the invoice says whether you
were paid for any of it.

The estimated-versus-actual pair of columns is the whole argument for
keeping records at all. Estimated cost is what the quote assumed.
Actual cost is what the crew and the receipts say happened. The gap
between them is where a landscaping business quietly loses money.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, time_check
from .common import (alert_cf, alert_chain, amount, customer_col,
                     date_num_col, id_col, is_catchup_job, is_done_job,
                     is_open_job, lookup_customer, lookup_property,
                     lookup_property_num, lookup_service,
                     lookup_service_num, loss_cf, margin, money_cf,
                     month_col, owing_cf, pick, property_col, scale_cf,
                     service_col, service_tax, status_cf, sum_by,
                     week_start_col, weekday_col, yesno, zero)

NAME = "Job & Work Orders"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Job & Work Orders",
        subtitle="Every visit, booked or done: who, where, what, how "
                 "long it took and what it was really worth.",
        tab_color=Palette.deep,
        rows=cfg.row_count("jobs"),
        samples=sample("jobs", cfg),
        freeze_cols=3,
        help_text=(
            "One row per visit. Book it with a date, a property and a "
            "service; mark it Completed when it is done and fill in "
            "the actual hours. Everything else - the estimate, the "
            "costs, the profit, the invoice status - comes from the "
            "other tabs automatically."),
        extra_notes=[
            "Estimated cost comes from the catalogue time and the "
            "property's difficulty. Actual cost comes from the "
            "timesheets and the expense tracker. Watch the variance "
            "column: a service that is always 20% over is a service "
            "that is underpriced, not a crew that is slow.",
            "'Rained off' and 'Needs revisit' are not failures, they "
            "are work you still owe. They stay on the catch-up list on "
            "the dashboard until they are rescheduled.",
            "Leave the Invoice ID blank until you raise the invoice. "
            "The 'Unbilled' alert finds completed work nobody has "
            "charged for - on most jobs that is the single most "
            "profitable column in this workbook.",
        ],
        columns=[
            id_col("date", "JobPrefix", digits=cfg.digits("job"),
                   header="Job ID",
                   note="Generated. This is what the timesheets, the "
                        "expenses and the invoice all point at."),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="The day of the visit. Start here."),
            Col("weekday", "Day", 8, "text",
                formula='=IF({date}{r}="","",'
                        'TEXT({date}{r},"ddd"))',
                hidden=True),
            customer_col(),
            Col("customer_name", "Customer", 20, "text",
                formula=lookup_customer("name")),
            property_col(),
            Col("address", "Address", 28, "text",
                formula=lookup_property("address")),
            Col("town", "Town", 14, "text",
                formula=lookup_property("town", missing=""),
                note="Used by the route planner to group a day's stops "
                     "sensibly."),
            service_col(),
            Col("crew", "Crew", 12, "text",
                validate=pick("CrewNameList",
                              "Which crew is doing it? Set the crews up "
                              "on the Settings tab."),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "Unassigned", "fmt": "warn"}],
                note="The route planner prints one sheet per crew per "
                     "day from this column."),
            Col("status", "Status", 14, "text",
                validate=list_from("JobStatusList"),
                cf=status_cf(),
                note="Completed is what makes a job count as revenue. "
                     "Nothing is earned until it is done."),
            Col("priority", "Priority", 15, "text",
                validate=list_from("PriorityList"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "1 - Urgent", "fmt": "bold_bad"},
                    {"type": "text", "criteria": "containing",
                     "value": "2 - High", "fmt": "bad"}]),
            Col("contract", "Contract ID", 11, "id",
                validate=pick("ContractIDList",
                              "Pick the agreement this visit belongs "
                              "to."),
                note="If this visit came from a recurring agreement, "
                     "its Contract ID. Blank for one-off work."),
            Col("quote", "Quote ID", 11, "id",
                validate=pick("QuoteIDList",
                              "Pick the quote this work was priced "
                              "from."),
                note="If it came from an accepted quote, its Quote ID. "
                     "That is the audit trail from price to paid."),

            # ---- the plan --------------------------------------------
            Col("start_time", "Start", 9, "time",
                validate=time_check(),
                note="Planned arrival. The route planner sorts the day "
                     "by this."),
            Col("area", "Lawn area", 10, "int",
                formula=lookup_property_num("lawn_area"),
                hidden=True),
            Col("difficulty", "Difficulty", 9, "number1",
                formula='=IF({property}{r}="",1,'
                        'IFERROR(INDEX([[Property Database.difficulty]],'
                        'MATCH({property}{r},'
                        '[[Property Database.id]],0))*1,1))',
                hidden=True),
            Col("cat_minutes", "Catalogue mins", 11, "int",
                formula=lookup_service_num("minutes"),
                hidden=True),
            Col("cat_unit", "Unit", 12, "text",
                formula=lookup_service("unit", missing=""),
                hidden=True),
            Col("units", "Units", 8, "number1",
                formula=zero("service",
                             'IF({cat_unit}{r}="Per 1,000 sq ft",'
                             'MAX(1,{area}{r})/1000,'
                             'IF({cat_unit}{r}="Per 100 sq ft",'
                             'MAX(1,{area}{r})/100,'
                             'IF({cat_unit}{r}="Per sq ft",'
                             'MAX(1,{area}{r}),1)))'),
                hidden=True),
            Col("crew_size", "Crew size", 9, "int",
                validate=amount(1, 20, "How many people are going?",
                                decimal=False),
                note="Blank uses the default crew size on Settings."),
            Col("crew_used", "Crew used", 9, "int",
                formula=zero("date",
                             'IF({crew_size}{r}>0,{crew_size}{r},'
                             'CrewSize)'),
                hidden=True),
            Col("hours_est", "Hours (est)", 10, "number1",
                formula=zero("service",
                             'ROUND({cat_minutes}{r}*{units}{r}*'
                             'MAX(1,{difficulty}{r})/60,2)'),
                note="Crew hours the catalogue expects, adjusted for "
                     "this site."),

            # ---- what happened ---------------------------------------
            Col("hours_logged", "Hours (timesheet)", 13, "number1",
                formula=zero("date", sum_by("Timesheets & Payroll",
                                            "hours", "job", '{id}{r}')),
                hidden=True),
            Col("hours_typed", "Hours (actual)", 12, "number1",
                validate=amount(0, 200,
                                "Total crew hours on site. Leave blank "
                                "if you are using the timesheets."),
                note="Type it here, or let the timesheets fill it in. "
                     "The timesheets win if both are present."),
            Col("hours_actual", "Hours used", 11, "number1",
                formula=zero("date",
                             'IF({hours_logged}{r}>0,{hours_logged}{r},'
                             '{hours_typed}{r})'),
                cf=scale_cf(),
                note="Timesheet hours if there are any, otherwise what "
                     "you typed."),
            Col("hours_var", "Hours vs est", 11, "number1",
                formula='=IF({date}{r}="","",'
                        'IF({hours_actual}{r}<=0,"",'
                        'ROUND({hours_actual}{r}-'
                        '{hours_est}{r},2)))',
                cf=[{"type": "cell", "criteria": ">", "value": 0.5,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<", "value": -0.25,
                     "fmt": "good"}],
                note="Positive means it took longer than the catalogue "
                     "said. A pattern here is a pricing problem."),
            Col("weather", "Weather", 14, "text",
                validate=list_from("WeatherList"),
                note="Why the day went the way it did. Rain is the "
                     "reason most schedules slip."),
            Col("completed_by", "Done by", 14, "text",
                note="Who actually did it, if it was not the crew you "
                     "booked."),
            Col("checklist_done", "Checklist done", 12, "flag",
                validate=yesno("Has the crew worked through the job "
                               "completion checklist?"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "No", "fmt": "warn"}],
                note="Gates shut, clippings cleared, tools counted. The "
                     "checklist itself is on the Seasonal Planner tab."),
            Col("photo_before", "Photo - before", 18, "link"),
            Col("photo_after", "Photo - after", 18, "link",
                note="Links to your cloud drive, not pictures in the "
                     "file. Keeps the workbook fast and the evidence "
                     "safe."),
            Col("issues", "Problems on site", 30, "wrap",
                note="Broken sprinkler, locked gate, a dog out. Write "
                     "it down the same day or it is gone."),
            Col("notes", "Notes", 30, "wrap"),

            # ---- money in --------------------------------------------
            Col("price_quoted", "Agreed price", 12, "money",
                validate=amount(0, 1000000,
                                "What the customer agreed to pay. Blank "
                                "uses the contract or catalogue price."),
                note="Blank falls back to the contract price, then the "
                     "catalogue."),
            Col("contract_price", "Contract price", 11, "money",
                formula=zero("date",
                             'IF({contract}{r}="",0,'
                             'IFERROR(INDEX('
                             '[[Recurring Contracts.visit_price]],'
                             'MATCH({contract}{r},'
                             '[[Recurring Contracts.id]],0))*1,0))'),
                hidden=True),
            Col("cat_price", "Catalogue price", 11, "money",
                formula=zero("service",
                             'ROUND(IFERROR(INDEX('
                             '[[Service Catalog.rate]],'
                             'MATCH({service}{r},'
                             '[[Service Catalog.name]],0))*1,0)*'
                             '{units}{r},2)'),
                hidden=True),
            Col("charge", "Charge", 11, "money",
                formula=zero("date",
                             'ROUND(IF({price_quoted}{r}>0,'
                             '{price_quoted}{r},'
                             'IF({contract_price}{r}>0,'
                             '{contract_price}{r},{cat_price}{r})),2)'),
                cf=money_cf(),
                note="What this visit earns, before tax. Completed "
                     "visits with a charge are your revenue."),
            Col("extras", "Extras charged", 11, "money",
                validate=amount(0, 1000000,
                                "Anything beyond the agreed price - an "
                                "extra bag of mulch, a hedge they asked "
                                "for on the day."),
                note="The work your crew does for nothing unless "
                     "somebody writes it down."),
            Col("tax", "Tax", 10, "money",
                formula=zero("date",
                             service_tax('{charge}{r}+{extras}{r}')),
                hidden=True),
            Col("total_charge", "Total", 11, "money",
                formula=zero("date",
                             'ROUND({charge}{r}+{extras}{r}+'
                             '{tax}{r},2)'),
                cf=money_cf()),

            # ---- money out: estimated, then actual -------------------
            Col("cost_est", "Cost (est)", 11, "money",
                formula=zero("service",
                             'ROUND({hours_est}{r}*(LabourRate+'
                             'OverheadRate)+'
                             'IFERROR(INDEX('
                             '[[Service Catalog.materials_cost]],'
                             'MATCH({service}{r},'
                             '[[Service Catalog.name]],0))*1,0)*'
                             '{units}{r}+'
                             '2*IFERROR(INDEX('
                             '[[Property Database.miles]],'
                             'MATCH({property}{r},'
                             '[[Property Database.id]],0))*1,0)*'
                             'TravelRate,2)'),
                note="What the quote assumed: catalogue time at your "
                     "rates, plus materials, plus the drive."),
            Col("labour_cost", "Labour (actual)", 12, "money",
                formula=zero("date", sum_by("Timesheets & Payroll",
                                            "cost", "job", '{id}{r}')),
                note="From the timesheets, at each person's own rate."),
            Col("labour_fallback", "Labour fallback", 11, "money",
                formula=zero("date",
                             'IF({hours_logged}{r}>0,0,'
                             'ROUND({hours_actual}{r}*LabourRate,2))'),
                hidden=True),
            Col("expense_cost", "Site costs", 11, "money",
                formula=zero("date", sum_by("Expense Tracker", "allocated_cost",
                                            "job", '{id}{r}')),
                note="Usage or wastage and non-inventory costs booked to this "
                     "Job ID. Inventory purchases are allocated on usage."),
            Col("overhead_cost", "Overhead", 10, "money",
                formula=zero("date",
                             'ROUND({hours_actual}{r}*OverheadRate,2)'),
                note="Charged on the hours actually worked, not the "
                     "hours hoped for."),
            Col("travel_cost", "Travel", 10, "money",
                formula=zero("date",
                             'ROUND(2*IFERROR(INDEX('
                             '[[Property Database.miles]],'
                             'MATCH({property}{r},'
                             '[[Property Database.id]],0))*1,0)*'
                             'TravelRate,2)')),
            Col("cost", "Cost (actual)", 12, "money",
                formula=zero("date",
                             'ROUND({labour_cost}{r}+'
                             '{labour_fallback}{r}+{expense_cost}{r}+'
                             '{overhead_cost}{r}+{travel_cost}{r},2)'),
                note="Everything this visit really cost you."),
            Col("cost_var", "Cost vs est", 11, "money",
                formula='=IF({date}{r}="","",'
                        'IF({is_done}{r}=0,"",'
                        'ROUND({cost}{r}-{cost_est}{r},2)))',
                cf=[{"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "good"}],
                note="Red means it cost more than you estimated. This "
                     "column, averaged over a season, is the most "
                     "valuable thing in the workbook."),
            Col("profit", "Profit", 11, "money",
                formula=zero("date",
                             'IF({is_done}{r}=0,0,'
                             'ROUND({charge}{r}+{extras}{r}-'
                             '{cost}{r},2))'),
                cf=loss_cf(),
                note="Completed visits only, and excluding tax - tax is "
                     "never yours."),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({date}{r}="","",'
                        'IF({is_done}{r}=0,"",'
                        f'{margin("{profit}{r}", "({charge}{r}+{extras}{r})")}))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=TargetMargin", "fmt": "good"},
                    {"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": "<",
                     "value": "=MinMargin", "fmt": "bad"}]),
            Col("per_hour", "Earned per hour", 12, "money",
                formula='=IF({date}{r}="","",'
                        'IF({hours_actual}{r}<=0,"",'
                        'ROUND(({charge}{r}+{extras}{r})/'
                        '{hours_actual}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}]),

            # ---- getting paid ----------------------------------------
            Col("invoice", "Invoice ID", 11, "id",
                validate=pick("InvoiceIDList",
                              "Pick the invoice that bills this "
                              "visit."),
                note="Fill in when you raise the invoice. Blank on a "
                     "completed job means unbilled work."),
            Col("invoiced", "Invoiced", 11, "money",
                formula=zero("date", sum_by("Invoice & Payments", "total",
                                            "job", '{id}{r}')),
                hidden=True),
            Col("paid_state", "Payment", 14, "text",
                formula='=IF({date}{r}="","",'
                        'IF({invoice}{r}="",'
                        'IF({is_done}{r}=1,"Not invoiced",""),'
                        'IFERROR(INDEX('
                        '[[Invoice & Payments.status]],'
                        'MATCH({invoice}{r},'
                        '[[Invoice & Payments.id]],0))&"",'
                        '"Check - invoice not found")))',
                cf=status_cf(),
                note="Read straight off the invoice register, so it can "
                     "never disagree with it."),
            Col("outstanding", "Still owed", 11, "money",
                formula=zero("date",
                             'IF({invoice}{r}="",0,'
                             'IFERROR(INDEX('
                             '[[Invoice & Payments.outstanding]],'
                             'MATCH({invoice}{r},'
                             '[[Invoice & Payments.id]],0))*1,0))'),
                cf=owing_cf(),
                hidden=True),

            # ---- the hidden machinery --------------------------------
            Col("is_done", "Done", 6, "int",
                formula=zero("date", f'IF({is_done_job("{status}{r}")},'
                                     '1,0)'),
                hidden=True),
            Col("is_open", "Open", 6, "int",
                formula=zero("date", f'IF({is_open_job("{status}{r}")},'
                                     '1,0)'),
                hidden=True),
            Col("is_catchup", "Catch up", 7, "int",
                formula=zero("date",
                             f'IF({is_catchup_job("{status}{r}")},1,0)'),
                hidden=True),
            Col("is_today", "Today", 6, "int",
                formula=zero("date",
                             'IF(AND({date}{r}=TodayDate,'
                             '{is_open}{r}=1),1,0)'),
                hidden=True),
            Col("is_week", "This week", 7, "int",
                formula=zero("date",
                             'IF(AND({is_open}{r}=1,'
                             '{date}{r}>=TodayDate,'
                             '{date}{r}<=TodayDate+UpcomingDays),1,0)'),
                hidden=True),
            Col("is_unbilled", "Unbilled", 7, "int",
                formula=zero("date",
                             'IF(AND({is_done}{r}=1,{invoice}{r}="",'
                             '{charge}{r}>0),1,0)'),
                hidden=True),
            Col("today_rank", "Today rank", 9, "int",
                formula=zero("date",
                             'IF({is_today}{r}=0,0,'
                             'COUNTIFS({is_today_first}:{is_today}{r},'
                             '1))'),
                hidden=True,
                note="1, 2, 3 ... down today's jobs, so the dashboard "
                     "can list them without an array formula."),
            Col("route_key", "Route key", 14, "text",
                formula='=IF({date}{r}="","",'
                        'TEXT({date}{r},"yyyy-mm-dd")&"|"&'
                        '{crew}{r})',
                hidden=True,
                note="Date and crew together - how the route planner "
                     "finds one crew's day in one lookup."),
            Col("route_time", "Route time", 9, "number",
                formula=zero("date", 'IF({start_time}{r}="",2,{start_time}{r})'),
                hidden=True),
            Col("route_seq", "Stop", 6, "int",
                formula=zero("date",
                             'COUNTIFS({route_key_first}:{route_key_last},'
                             '{route_key}{r},{route_time_first}:{route_time_last},'
                             '"<"&{route_time}{r})+'
                             'COUNTIFS({route_key_first}:{route_key}{r},'
                             '{route_key}{r},{route_time_first}:{route_time}{r},'
                             '{route_time}{r})'),
                hidden=True),
            Col("route_match", "Route match", 12, "int",
                formula=zero("date",
                             'IF(AND({date}{r}=RouteDate,'
                             '{crew}{r}=RouteCrew),{route_seq}{r},0)'),
                hidden=True,
                note="Which line of the printable work order this job "
                     "is, if it is on the chosen day at all."),
            date_num_col("date", "date_num"),
            weekday_col("date", "dow", header="DOW"),
            week_start_col("date"),
            month_col("date"),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("date", [
                    ('AND({is_open}{r}=1,{date}{r}<TodayDate)',
                     "Overdue - booked in the past and never closed off"),
                    ('AND({is_done}{r}=1,{charge}{r}=0)',
                     "Urgent - completed with no charge, is it free?"),
                    ('{is_catchup}{r}=1',
                     "Reschedule - rained off or needs a revisit"),
                    ('AND({is_unbilled}{r}=1,'
                     '{date}{r}<TodayDate-OverdueDays)',
                     "Unbilled - done and never invoiced"),
                    ('AND({is_done}{r}=1,{profit}{r}<0)',
                     "Loss - this visit cost more than it charged"),
                    ('{is_today}{r}=1', "Today - on the list for today"),
                    ('AND({is_open}{r}=1,{crew}{r}="Unassigned")',
                     "Action - booked with nobody assigned to it"),
                    ('AND({is_done}{r}=1,{hours_actual}{r}=0)',
                     "Add - completed with no hours, so profit is "
                     "guesswork"),
                    ('AND({is_done}{r}=1,{checklist_done}{r}="No")',
                     "Check - completion checklist not signed off"),
                    ('AND({is_done}{r}=1,{margin_pct}{r}<>"",'
                     '{margin_pct}{r}<MinMargin)',
                     "Thin margin - under your floor on this visit"),
                    ('{is_week}{r}=1', "This week - coming up"),
                    ('{is_open}{r}=1', "Upcoming - booked"),
                ]),
                cf=alert_cf()),
        ],
    )
