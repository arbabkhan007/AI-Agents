"""4. Customer CRM - everybody who pays you, and what they are worth.

The Customer ID generated here is the first of the four join keys. A
property belongs to a customer, a job happens at a property, and an
invoice bills a customer for jobs. Get this ID wrong and the chain
comes apart three tabs later with nothing to say why.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, count_by, id_col,
                     is_active_customer, loss_cf, margin, money_cf,
                     owing_cf, rank_desc, rating_cf, scale_cf, status_cf,
                     sum_by, yesno, zero)

NAME = "Customer CRM"


def spec(cfg: Config) -> SheetSpec:
    rows = cfg.row_count("customers")
    return SheetSpec(
        name=NAME,
        title="Customer CRM",
        subtitle="Everyone who pays you, what they have spent, and who "
                 "has gone quiet. One row per customer, never per visit.",
        tab_color=Palette.primary,
        rows=rows,
        samples=sample("customers", cfg),
        help_text=(
            "Add the customer here first. The Customer ID appears "
            "automatically and becomes available in every drop-down "
            "that needs it - properties, quotes, jobs, invoices. "
            "A household with two addresses is ONE customer with two "
            "properties, not two customers."),
        extra_notes=[
            "Lifetime value counts completed jobs only, so a quote "
            "nobody accepted never inflates what somebody looks worth.",
            "'Dormant' is worked out, not typed: it is how long since "
            "their last completed visit against the window on Settings.",
        ],
        columns=[
            id_col("name", "CustomerPrefix", digits=cfg.digits("customer"),
                   header="Customer ID",
                   note="Generated. This is the join key - every property, "
                        "job and invoice points back at it."),
            Col("name", "Customer name", 24, "text",
                note="A household, a company or a managing agent. Start "
                     "typing here and the row comes alive."),
            Col("contact", "Main contact", 18, "text",
                note="Who you actually speak to."),
            Col("phone", "Phone", 15, "text"),
            Col("email", "Email", 26, "text"),
            Col("address", "Billing address", 30, "wrap",
                note="Where the invoice goes. The place you mow is a "
                     "Property, on the next tab."),
            Col("town", "Town / city", 16, "text"),
            Col("postcode", "Zip / postcode", 12, "text"),
            Col("type", "Customer type", 20, "text",
                validate=list_from("CustomerTypeList"),
                note="Commercial work pays later and in bigger lumps. "
                     "Worth being able to split the two."),
            Col("source", "How they found you", 20, "text",
                validate=list_from("LeadSourceList"),
                note="Fill this in for a year and you will stop paying "
                     "for the adverts that do not work."),
            Col("first_job", "Customer since", 13, "date",
                validate=date_check()),
            Col("terms", "Payment terms", 17, "text",
                validate=list_from("PaymentTermsList"),
                note="Drives the due date on every invoice to them."),
            Col("method", "Pays by", 16, "text",
                validate=list_from("PaymentMethodList")),
            Col("status", "Status", 13, "text",
                validate=list_from("CustomerStatusList"),
                cf=status_cf()),
            Col("rating", "You rate them", 11, "rating",
                validate={"validate": "integer", "criteria": "between",
                          "minimum": 1, "maximum": 5,
                          "error_title": "1 to 5",
                          "error_message": "How good are they to work "
                                           "for? 5 is a dream job, 1 is "
                                           "one you dread."},
                cf=rating_cf(),
                note="Pays on time, dog is friendly, gate is unlocked. "
                     "Your own judgement, for your own planning."),
            Col("po_required", "Needs a PO", 10, "flag",
                validate=yesno("Does this customer require a purchase "
                               "order number before you can invoice?"),
                note="Commercial accounts often do, and an invoice "
                     "without one does not get paid."),
            Col("tax_exempt", "Tax exempt", 10, "flag",
                validate=yesno()),
            Col("marketing_ok", "Marketing OK", 11, "flag",
                validate=yesno("Have they agreed to seasonal offers and "
                               "reminders?"),
                note="Ask once, record it, and respect it."),
            Col("notes", "Notes", 34, "wrap",
                note="The things that are not a field: 'ring the bell, "
                     "do not use the side gate', 'always wants the "
                     "clippings left'."),

            # ---- what they are actually worth ------------------------
            Col("properties", "Properties", 10, "int",
                formula=zero("name", count_by("Property Database",
                                              "customer", '{id}{r}')),
                note="Automatic. How many addresses you look after for "
                     "them."),
            Col("jobs_done", "Visits done", 11, "int",
                formula=zero("name", count_by("Job & Work Orders",
                                              "customer", '{id}{r}',
                                              "is_done", "1")),
                cf=scale_cf()),
            Col("jobs_open", "Visits booked", 12, "int",
                formula=zero("name", count_by("Job & Work Orders",
                                              "customer", '{id}{r}',
                                              "is_open", "1"))),
            Col("lifetime", "Lifetime revenue", 15, "money",
                formula=zero("name", sum_by("Job & Work Orders", "charge",
                                            "customer", '{id}{r}',
                                            "is_done", "1")),
                cf=money_cf(),
                note="Completed work only. This is the number that tells "
                     "you who you cannot afford to lose."),
            Col("revenue_year", "This year", 13, "money",
                formula=zero("name", sum_by(
                    "Job & Work Orders", "charge", "customer", '{id}{r}',
                    "is_done", "1",
                    "date_num", '">="&YearStart',
                    "date_num", '"<="&YearEnd')),
                cf=money_cf()),
            Col("cost_total", "Cost to serve", 13, "money",
                formula=zero("name", sum_by("Job & Work Orders", "cost",
                                            "customer", '{id}{r}',
                                            "is_done", "1"))),
            Col("profit", "Profit", 12, "money",
                formula=zero("name", 'ROUND({lifetime}{r}-'
                                     '{cost_total}{r},2)'),
                cf=loss_cf(),
                note="What they have actually left you with after the "
                     "crew, the materials and the drive."),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({name}{r}="","",'
                        f'{margin("{profit}{r}", "{lifetime}{r}")})',
                cf=scale_cf()),
            Col("avg_job", "Average visit", 13, "money",
                formula='=IF({name}{r}="","",'
                        'IF({jobs_done}{r}<=0,"",'
                        'ROUND({lifetime}{r}/{jobs_done}{r},2)))'),
            Col("contracts", "Contracts", 10, "int",
                formula=zero("name", count_by("Recurring Contracts",
                                              "customer", '{id}{r}',
                                              "is_live", "1")),
                note="Live recurring agreements. A customer with one is "
                     "worth far more than one without."),
            Col("contract_value", "Contract / yr", 13, "money",
                formula=zero("name", sum_by("Recurring Contracts",
                                            "annual_value", "customer",
                                            '{id}{r}', "is_live", "1")),
                cf=money_cf(),
                note="Booked recurring income. The number a buyer of "
                     "your business would look at first."),

            # ---- money owed ------------------------------------------
            Col("invoiced", "Invoiced", 12, "money",
                formula=zero("name", sum_by("Invoice & Payments", "total",
                                            "customer", '{id}{r}'))),
            Col("received", "Received", 12, "money",
                formula=zero("name", sum_by("Invoice & Payments", "paid",
                                            "customer", '{id}{r}'))),
            Col("owing", "Owing", 11, "money",
                formula=zero("name", 'ROUND({invoiced}{r}-'
                                     '{received}{r},2)'),
                cf=owing_cf()),
            Col("overdue", "Overdue", 11, "money",
                formula=zero("name", sum_by("Invoice & Payments",
                                            "outstanding", "customer",
                                            '{id}{r}', "is_overdue", "1")),
                cf=owing_cf(),
                note="Past the due date and still unpaid. Chase this "
                     "column before you chase anything else."),
            Col("oldest_due", "Days late", 10, "int",
                formula=zero("name", 'IF({overdue}{r}<=0,0,'
                                     'MAX(0,SUMPRODUCT(MAX('
                                     '([[Invoice & Payments.customer]]='
                                     '{id}{r})*'
                                     '[[Invoice & Payments.days_late]]))))'),
                cf=[{"type": "cell", "criteria": ">=", "value": 30,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "warn"}],
                note="The worst one, not the average. A single 90 day "
                     "debt is a different conversation."),

            # ---- how they are getting on -----------------------------
            Col("last_job_num", "Last visit #", 11, "number",
                formula=zero("name", 'SUMPRODUCT(MAX('
                                     '([[Job & Work Orders.customer]]='
                                     '{id}{r})*'
                                     '([[Job & Work Orders.is_done]]=1)*'
                                     '[[Job & Work Orders.date_num]]))'),
                hidden=True),
            Col("last_job", "Last visit", 12, "date",
                formula='=IF({name}{r}="","",'
                        'IF({last_job_num}{r}<=0,"",'
                        '{last_job_num}{r}))',
                note="Automatic, from the job register."),
            Col("days_since", "Days since", 10, "int",
                formula=zero("name", 'IF({last_job_num}{r}<=0,0,'
                                     'TodayDate-{last_job_num}{r})'),
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=DormantDays", "fmt": "bad"}]),
            Col("rating_given", "Their rating", 11, "number1",
                formula='=IF({name}{r}="","",'
                        'IFERROR(AVERAGEIFS('
                        '[[Customer Feedback.score]],'
                        '[[Customer Feedback.customer]],{id}{r},'
                        '[[Customer Feedback.score]],">0"),""))',
                cf=rating_cf(),
                note="What they think of you, averaged from the feedback "
                     "tab. The other direction to the column above."),
            Col("complaints", "Complaints", 10, "int",
                formula=zero("name", count_by("Customer Feedback",
                                              "customer", '{id}{r}',
                                              "is_problem", "1")),
                cf=[{"type": "cell", "criteria": ">=", "value": 2,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "warn"}]),
            Col("is_active", "Active", 7, "int",
                formula=zero("name", f'IF({is_active_customer("{status}{r}")},'
                                     '1,0)'),
                hidden=True),
            rank_desc("lifetime", guard='{name}{r}=""',
                      note="1 = your most valuable customer. The "
                           "dashboard reads this to list them."),
            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("name", [
                    ('{overdue}{r}>0',
                     "Overdue - invoice past its due date, chase it"),
                    ('{complaints}{r}>=2',
                     "Urgent - more than one complaint logged, call them"),
                    ('AND({status}{r}="Lead",{jobs_done}{r}=0)',
                     "Follow up - a lead with no work done yet"),
                    ('{properties}{r}=0',
                     "Add - no property on file, so nothing can be booked"),
                    ('AND({is_active}{r}=1,{days_since}{r}>=DormantDays,'
                     '{jobs_open}{r}=0)',
                     "Dormant - no visit for a long time and nothing "
                     "booked"),
                    ('AND({contracts}{r}=0,{jobs_done}{r}>=4)',
                     "Action - a regular customer with no contract, ask "
                     "for one"),
                    ('AND({lifetime}{r}>0,{margin_pct}{r}<>"",'
                     '{margin_pct}{r}<MinMargin)',
                     "Thin margin - this customer earns less than your "
                     "floor"),
                    ('{owing}{r}>0', "Due - invoiced and not yet paid"),
                    ('{email}{r}=""', "Add - no email address on file"),
                    ('{terms}{r}=""', "Add - payment terms not set"),
                ]),
                cf=alert_cf()),
        ],
    )
