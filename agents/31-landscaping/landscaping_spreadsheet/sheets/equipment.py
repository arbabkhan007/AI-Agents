"""14. Equipment Inventory - the machines, and when they are due.

Mowers measure their lives in engine hours, not calendar months, so
this tab tracks both: hours since the last service against the
interval you set, and days since the last service against the months
you set. Whichever comes first wins, which is how the manual says it
and how the dashboard alert works.

A machine that fails in July costs a week of the season. The warning
columns here exist so that it fails in the workshop in February
instead.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, count_by, id_col,
                     is_usable_equipment, rank_desc, scale_cf,
                     status_cf, sum_by, yesno, zero)

NAME = "Equipment Inventory"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Equipment Inventory",
        subtitle="Every machine you own: what it cost, what it is "
                 "worth, when it was last serviced and what it owes "
                 "you.",
        tab_color=Palette.accent,
        rows=cfg.row_count("equipment"),
        samples=sample("equipment", cfg),
        help_text=(
            "List every machine worth more than a few days' hire. "
            "Record the engine hours when you service it and the "
            "workbook works out when the next one is due, by hours "
            "and by date, and warns you before either arrives."),
        extra_notes=[
            "Service intervals are set per machine because a "
            "commercial mower and a hedge trimmer do not live the "
            "same life. The defaults on Settings are used when a row "
            "leaves them blank.",
            "Cost per hour is the number that tells you whether to "
            "repair or replace. Once a machine's running cost per "
            "hour passes what hiring one would cost, the decision "
            "has already been made for you.",
            "Depreciation here is straight line and is for your own "
            "planning only. Your accountant will use a different "
            "method for tax, and theirs is the one that counts.",
        ],
        columns=[
            id_col("name", "EquipmentPrefix",
                   digits=cfg.digits("equipment"), header="Equipment ID",
                   note="Generated. Useful on a sticker on the "
                        "machine itself."),
            Col("name", "Equipment", 26, "text",
                note="Start here. 'Exmark Lazer Z 60\"' beats 'big "
                     "mower' when there are three of them."),
            Col("category", "Category", 20, "text",
                validate=list_from("EquipmentCategoryList")),
            Col("make", "Make", 15, "text"),
            Col("model", "Model", 16, "text"),
            Col("serial", "Serial number", 18, "text",
                note="The one the insurer and the police ask for. "
                     "Photograph the plate as well."),
            Col("purchase_date", "Bought", 11, "date",
                validate=date_check()),
            Col("purchase_price", "Cost", 11, "money",
                validate=amount(0, 1000000)),
            Col("life_years", "Life (years)", 11, "int",
                validate=amount(0, 50, decimal=False),
                note="How long you expect to keep it working. Drives "
                     "the depreciation estimate."),
            Col("warranty_end", "Warranty to", 11, "date",
                validate=date_check(),
                note="Worth checking before paying for a repair."),
            Col("status", "Status", 15, "text",
                validate=list_from("EquipmentStatusList"),
                cf=status_cf()),
            Col("condition", "Condition", 14, "text",
                validate=list_from("EquipmentConditionList"),
                cf=[{"type": "text", "criteria": "containing",
                     "value": "Poor", "fmt": "bad"},
                    {"type": "text", "criteria": "containing",
                     "value": "Needs replacing", "fmt": "bold_bad"}]),
            Col("assigned", "Assigned to", 13, "text",
                validate=list_from("CrewNameList"),
                note="Which crew has it on the trailer."),
            Col("location", "Kept at", 16, "text",
                note="Yard, trailer two, Danny's garage."),

            # ---- servicing -------------------------------------------
            Col("hours_now", "Engine hours", 12, "number1",
                validate=amount(0, 100000,
                                "The reading on the hour meter today."),
                note="Update it when you service the machine. It is "
                     "the only honest measure of a mower's life."),
            Col("last_service", "Last service", 12, "date",
                validate=date_check()),
            Col("last_service_hours", "Hours at service", 14, "number1",
                validate=amount(0, 100000),
                note="The hour meter reading at the last service."),
            Col("service_hours", "Service every (hrs)", 15, "int",
                validate=amount(0, 10000, decimal=False),
                note="Blank uses the default interval on Settings."),
            Col("service_months", "Service every (months)", 16, "int",
                validate=amount(0, 120, decimal=False),
                note="Some machines are due by the calendar even if "
                     "they have barely run."),
            Col("hours_used", "Hours since", 11, "number1",
                formula=zero("name",
                             'MAX(0,{hours_now}{r}-'
                             '{last_service_hours}{r})'),
                note="Engine hours since the last service."),
            Col("hours_interval", "Interval used", 11, "int",
                formula=zero("name",
                             'IF({service_hours}{r}>0,'
                             '{service_hours}{r},ServiceHours)'),
                hidden=True),
            Col("hours_left", "Hours to service", 14, "number1",
                formula='=IF({name}{r}="","",'
                        'ROUND({hours_interval}{r}-'
                        '{hours_used}{r},1))',
                cf=[{"type": "cell", "criteria": "<=", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": "<=", "value": 10,
                     "fmt": "warn"}],
                note="Negative means the service is overdue by that "
                     "many engine hours."),
            Col("days_since_service", "Days since", 11, "int",
                formula=zero("name",
                             'IF({last_service}{r}="",0,'
                             'TodayDate-{last_service}{r})'),
                hidden=True),
            Col("months_interval", "Months used", 10, "int",
                formula=zero("name",
                             'IF({service_months}{r}>0,'
                             '{service_months}{r},ServiceMonths)'),
                hidden=True),
            Col("next_service_date", "Service due", 12, "date",
                formula='=IF({name}{r}="","",'
                        'IF({last_service}{r}="","",'
                        'EDATE({last_service}{r},'
                        '{months_interval}{r})))',
                cf=[{"type": "formula",
                     "criteria": '=AND(ISNUMBER({next_service_date}{r}),'
                                 '{next_service_date}{r}<TodayDate)',
                     "fmt": "bold_bad"}],
                note="By the calendar. The hours column may get there "
                     "first - whichever does, wins."),
            Col("days_to_service", "Days to service", 13, "int",
                formula=zero("name",
                             'IF({last_service}{r}="",0,'
                             'EDATE({last_service}{r},'
                             '{months_interval}{r})-TodayDate)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<=",
                     "value": "=ServiceWarnDays", "fmt": "warn"}]),
            Col("service_due", "Due now", 8, "int",
                formula=zero("name",
                             'IF(({hours_left}{r}<=0)+'
                             '(AND({last_service}{r}<>"",'
                             '{days_to_service}{r}<=0))>0,1,0)'),
                hidden=True,
                note="Either measure being past due makes this 1. The "
                     "dashboard counts it."),
            Col("service_soon", "Due soon", 8, "int",
                formula=zero("name",
                             'IF(AND({service_due}{r}=0,'
                             '({hours_left}{r}<=ServiceWarnHours)+'
                             '(AND({last_service}{r}<>"",'
                             '{days_to_service}{r}<='
                             'ServiceWarnDays))>0),1,0)'),
                hidden=True),

            # ---- what it costs ---------------------------------------
            Col("maintenance_cost", "Maintenance spend", 15, "money",
                formula=zero("name", sum_by("Expense Tracker", "amount",
                                            "equipment", '{id}{r}')),
                note="Everything booked to this machine on the expense "
                     "tracker."),
            Col("maintenance_count", "Repairs", 9, "int",
                formula=zero("name", count_by("Expense Tracker",
                                              "equipment", '{id}{r}'))),
            Col("age_years", "Age (years)", 10, "number1",
                formula='=IF({purchase_date}{r}="","",'
                        'ROUND((TodayDate-'
                        '{purchase_date}{r})/365.25,1))'),
            Col("depreciated", "Written down to", 13, "money",
                formula=zero("name",
                             'IF({life_years}{r}<=0,0,'
                             'ROUND(MAX(0,{purchase_price}{r}*'
                             '(1-MIN(1,(TodayDate-'
                             '{purchase_date}{r})/365.25/'
                             '{life_years}{r}))),2))'),
                note="Straight line, for planning. Your accountant "
                     "will do it differently for tax."),
            Col("total_cost", "Owned cost", 12, "money",
                formula=zero("name",
                             'ROUND({purchase_price}{r}+'
                             '{maintenance_cost}{r},2)')),
            Col("cost_per_hour", "Cost per hour", 12, "money",
                formula='=IF({name}{r}="","",'
                        'IF({hours_now}{r}<=0,"",'
                        'ROUND({total_cost}{r}/'
                        '{hours_now}{r},2)))',
                cf=scale_cf(),
                note="Purchase plus repairs, divided by the hours it "
                     "has run. Compare it with the hire rate."),
            Col("replace_flag", "Replace?", 10, "flag",
                validate=yesno("Are you planning to replace this in "
                               "the next twelve months?"),
                note="Planning it beats discovering it in June."),
            Col("insured", "Insured", 9, "flag",
                validate=yesno()),
            Col("notes", "Notes", 28, "wrap"),

            Col("is_usable", "Usable", 7, "int",
                formula=zero("name",
                             f'IF({is_usable_equipment("{status}{r}")},'
                             '1,0)'),
                hidden=True),
            rank_desc("maintenance_cost", guard='{name}{r}=""'),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("name", [
                    ('{status}{r}="Out of service"',
                     "Urgent - out of service, jobs needing it will "
                     "slip"),
                    ('AND({is_usable}{r}=1,{service_due}{r}=1)',
                     "Service - overdue, book it in now"),
                    ('{condition}{r}="Needs replacing"',
                     "Action - condition says it needs replacing"),
                    ('AND({is_usable}{r}=1,{service_soon}{r}=1)',
                     "Due - service coming up shortly"),
                    ('AND({purchase_price}{r}>0,'
                     '{maintenance_cost}{r}>{purchase_price}{r}*0.5)',
                     "Check - repairs have passed half what it cost"),
                    ('AND({hours_now}{r}>0,{last_service}{r}="")',
                     "Add - no service history recorded"),
                    ('AND({is_usable}{r}=1,{hours_now}{r}=0)',
                     "Add - no engine hours, so servicing cannot be "
                     "tracked"),
                    ('{insured}{r}="No"',
                     "Check - not marked as insured"),
                    ('{replace_flag}{r}="Yes"',
                     "Plan - flagged for replacement this year"),
                ]),
                cf=alert_cf()),
        ],
    )
