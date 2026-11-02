"""10. Recurring Contracts - the income you can count on.

A contract says: this service, at this property, every so many days,
for this much. From that the sheet works out the next visit date, how
many visits are left this season, what the agreement is worth over a
year, and when it needs renewing.

The scheduler is deliberately a calculator, not a robot. It tells you
the next date a visit is due; you still create the job. A workbook
that silently invented rows would be a workbook you could not trust.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, count_by, customer_col,
                     date_num_col, id_col, is_live_contract,
                     lookup_customer, lookup_property, money_cf,
                     property_col, scale_cf, service_col, status_cf,
                     sum_by, yesno, zero)

NAME = "Recurring Contracts"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Recurring Contracts",
        subtitle="Standing agreements: what, where, how often, how "
                 "much, and when the next visit is due.",
        tab_color=Palette.primary_mid,
        rows=cfg.row_count("contracts"),
        samples=sample("contracts", cfg),
        freeze_cols=3,
        help_text=(
            "Set up one row per standing agreement. The next due date "
            "is worked out from the last completed visit and the "
            "frequency, so it moves on by itself as the work gets "
            "done. When a visit is due, create it on the Job & Work "
            "Orders tab and put this Contract ID on it."),
        extra_notes=[
            "This is a scheduling calculator, not an automatic "
            "booking system. It tells you what is due; you decide "
            "what actually gets booked, because weather, holidays and "
            "a broken mower all have a vote.",
            "Annual value is the honest measure of a contract. Twelve "
            "visits at $45 is a $540 customer, and that is the number "
            "to think about before offering a discount.",
            "Renewal reminders fire on the number of days set on "
            "Settings. Renewing a good contract is far cheaper than "
            "finding a new customer.",
        ],
        columns=[
            id_col("start_date", "ContractPrefix",
                   digits=cfg.digits("contract"), header="Contract ID",
                   note="Generated. Put it on every job that comes from "
                        "this agreement."),
            customer_col(),
            Col("customer_name", "Customer", 20, "text",
                formula=lookup_customer("name")),
            property_col(),
            Col("address", "Address", 26, "text",
                formula=lookup_property("address")),
            service_col(),
            Col("frequency", "Frequency", 16, "text",
                validate=list_from("FrequencyList"),
                note="How often the visit repeats. Drives both the next "
                     "due date and the annual value."),
            Col("day_pref", "Preferred day", 12, "text",
                validate=list_from("WeekdayList"),
                note="'Always Tuesdays' keeps a round tight and the "
                     "customer happy."),
            Col("start_date", "Starts", 11, "date",
                validate=date_check(),
                note="Start here. The row comes alive with a date."),
            Col("end_date", "Ends", 11, "date",
                validate=date_check(),
                note="Leave blank for a rolling agreement. Fill it in "
                     "for a fixed season."),
            Col("season_only", "Season only", 11, "flag",
                validate=yesno("Does this pause out of season?"),
                note="Mowing stops in winter; snow clearing does not. "
                     "The season months are on Settings."),
            Col("visit_price", "Price per visit", 12, "money",
                validate=amount(0, 1000000,
                                "What the customer pays for each "
                                "visit under this agreement."),
                note="The job register uses this automatically for "
                     "visits carrying this Contract ID."),
            Col("billing", "Billed", 16, "text",
                validate=list_from("PaymentTermsList"),
                note="How this one is invoiced - per visit, monthly in "
                     "advance, however you agreed it."),
            Col("po_number", "PO number", 14, "text",
                note="Commercial accounts often will not pay without "
                     "one."),
            Col("status", "Status", 13, "text",
                validate=list_from("ContractStatusList"),
                cf=status_cf()),
            Col("renewal_date", "Review on", 11, "date",
                validate=date_check(),
                note="When you will revisit the price. Put it in the "
                     "diary before the season starts, not during it."),
            Col("price_review", "Last price change", 13, "date",
                validate=date_check(),
                note="Two seasons without a change, with fuel and wages "
                     "where they are, is a quiet pay cut."),
            Col("notes", "Notes", 30, "wrap"),

            # ---- what it is worth ------------------------------------
            Col("visits_year", "Visits / year", 11, "int",
                formula=zero("start_date",
                             'IFERROR(INDEX(VisitsPerYear,'
                             'MATCH({frequency}{r},FrequencyList,0))*1,'
                             '0)'),
                note="From the frequency list on Settings."),
            Col("gap_days", "Days between", 11, "int",
                formula=zero("start_date",
                             'IFERROR(INDEX(DaysBetween,'
                             'MATCH({frequency}{r},FrequencyList,0))*1,'
                             '0)'),
                hidden=True),
            Col("annual_value", "Annual value", 12, "money",
                formula=zero("start_date",
                             'ROUND({visit_price}{r}*'
                             '{visits_year}{r},2)'),
                cf=money_cf(),
                note="Price per visit times visits per year. The number "
                     "that says how much this customer matters."),
            Col("monthly_value", "Per month", 11, "money",
                formula=zero("start_date",
                             'ROUND({annual_value}{r}/12,2)'),
                note="The same money spread evenly - useful when a "
                     "customer wants a flat monthly bill."),
            Col("visits_done", "Visits done", 11, "int",
                formula=zero("start_date", count_by("Job & Work Orders",
                                                    "contract", '{id}{r}',
                                                    "is_done", "1")),
                cf=scale_cf()),
            Col("visits_booked", "Visits booked", 12, "int",
                formula=zero("start_date", count_by("Job & Work Orders",
                                                    "contract",
                                                    '{id}{r}',
                                                    "is_open", "1"))),
            Col("revenue", "Revenue to date", 13, "money",
                formula=zero("start_date", sum_by("Job & Work Orders",
                                                  "charge", "contract",
                                                  '{id}{r}',
                                                  "is_done", "1")),
                cf=money_cf()),
            Col("cost_total", "Cost to date", 12, "money",
                formula=zero("start_date", sum_by("Job & Work Orders",
                                                  "cost", "contract",
                                                  '{id}{r}',
                                                  "is_done", "1"))),
            Col("profit", "Profit to date", 13, "money",
                formula=zero("start_date",
                             'ROUND({revenue}{r}-{cost_total}{r},2)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "good"}]),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({start_date}{r}="","",'
                        'IF({revenue}{r}<=0,"",'
                        'ROUND({profit}{r}/{revenue}{r},4)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=TargetMargin", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=MinMargin", "fmt": "bad"}],
                note="A contract below your floor is one to renegotiate "
                     "at review, not to cancel in a temper."),

            # ---- when the next one is due ----------------------------
            Col("last_num", "Last visit #", 11, "number",
                formula=zero("start_date",
                             'SUMPRODUCT(MAX('
                             '([[Job & Work Orders.contract]]={id}{r})*'
                             '([[Job & Work Orders.is_done]]=1)*'
                             '[[Job & Work Orders.date_num]]))'),
                hidden=True),
            Col("last_visit", "Last visit", 11, "date",
                formula='=IF({start_date}{r}="","",'
                        'IF({last_num}{r}<=0,"",{last_num}{r}))'),
            Col("next_num", "Next due #", 10, "number",
                formula=zero("start_date",
                             'IF({is_live}{r}=0,0,'
                             'IF({gap_days}{r}<=0,0,'
                             'IF({last_num}{r}<=0,{start_date}{r},'
                             '{last_num}{r}+{gap_days}{r})))'),
                hidden=True),
            Col("next_due", "Next due", 11, "date",
                formula='=IF({start_date}{r}="","",'
                        'IF({next_num}{r}<=0,"",'
                        '{next_num}{r}))',
                cf=[{"type": "formula",
                     "criteria": '=AND(ISNUMBER({next_due}{r}),'
                                 '{next_due}{r}<TodayDate)',
                     "fmt": "bad"}],
                note="Last completed visit plus the gap, or the start "
                     "date if nothing has happened yet."),
            Col("days_to_next", "Days to next", 11, "int",
                formula=zero("start_date",
                             'IF({next_num}{r}<=0,0,'
                             '{next_num}{r}-TodayDate)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<=", "value": 7,
                     "fmt": "warn"}],
                note="Negative means the visit is already late."),
            Col("booked_next", "Next booked", 7, "int",
                formula=zero("start_date",
                             'COUNTIFS([[Job & Work Orders.contract]],'
                             '{id}{r},[[Job & Work Orders.is_open]],1)'),
                hidden=True),
            Col("days_to_renew", "Days to review", 12, "int",
                formula=zero("start_date",
                             'IF({renewal_date}{r}="",0,'
                             '{renewal_date}{r}-TodayDate)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<=",
                     "value": "=RenewalWarnDays", "fmt": "warn"}]),
            Col("days_to_end", "Days to end", 11, "int",
                formula=zero("start_date",
                             'IF({end_date}{r}="",9999,'
                             '{end_date}{r}-TodayDate)'),
                hidden=True),
            Col("is_live", "Live", 6, "int",
                formula=zero("start_date",
                             f'IF(AND({is_live_contract("{status}{r}")},'
                             '({end_date}{r}="")+'
                             '({end_date}{r}>=TodayDate)>0),1,0)'),
                hidden=True),
            Col("is_due", "Due", 6, "int",
                formula=zero("start_date",
                             'IF(AND({is_live}{r}=1,{next_num}{r}>0,'
                             '{next_num}{r}<=TodayDate+UpcomingDays,'
                             '{booked_next}{r}=0),1,0)'),
                hidden=True),
            date_num_col("next_due", "next_date_num", header="Next #"),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("start_date", [
                    ('AND({is_live}{r}=1,{days_to_next}{r}<0,'
                     '{booked_next}{r}=0)',
                     "Overdue - a visit is past due and nothing is "
                     "booked"),
                    ('AND({is_live}{r}=1,{visit_price}{r}=0)',
                     "Add - no price agreed, so the visits earn nothing"),
                    ('AND({is_live}{r}=1,{days_to_renew}{r}<0,'
                     '{renewal_date}{r}<>"")',
                     "Renew - the review date has passed"),
                    ('AND({is_live}{r}=1,{renewal_date}{r}<>"",'
                     '{days_to_renew}{r}<=RenewalWarnDays)',
                     "Renew - review date coming up, agree the new "
                     "price"),
                    ('AND({is_live}{r}=1,{end_date}{r}<>"",'
                     '{days_to_end}{r}<=RenewalWarnDays,'
                     '{days_to_end}{r}>=0)',
                     "Renew - this agreement ends soon"),
                    ('AND({revenue}{r}>0,{profit}{r}<0)',
                     "Loss - this contract is costing you money"),
                    ('{is_due}{r}=1',
                     "Schedule - next visit due, create the work order"),
                    ('AND({is_live}{r}=1,{margin_pct}{r}<>"",'
                     '{margin_pct}{r}<MinMargin)',
                     "Thin margin - raise it at the next review"),
                    ('AND({is_live}{r}=1,{price_review}{r}<>"",'
                     'TodayDate-{price_review}{r}>730)',
                     "Check - the price has not changed in two years"),
                    ('AND({is_live}{r}=1,{renewal_date}{r}="")',
                     "Add - no review date set"),
                ]),
                cf=alert_cf()),
        ],
    )
