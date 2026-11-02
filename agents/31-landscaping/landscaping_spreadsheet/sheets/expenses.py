"""18. Expense Tracker - everything that goes out, and what it belongs to.

Two kinds of line live here and the difference matters. A line with a
Job ID is a cost of doing that job, and it lands on that job's actual
cost and its profit. A line without one is a cost of being in
business - insurance, the accountant, the yard rent - and it belongs
to the month, not to any visit.

Material purchases and material usage are both recorded here, which
is how the materials tab knows what is in the yard without anybody
counting it.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, date_num_col, id_col,
                     is_job_cost, money_cf, month_col, pick,
                     yesno, zero)

NAME = "Expense Tracker"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Expense Tracker",
        subtitle="Every cost: the ones that belong to a job, and the "
                 "ones that belong to the business.",
        tab_color=Palette.deep,
        rows=cfg.row_count("expenses"),
        samples=sample("expenses", cfg),
        freeze_cols=3,
        help_text=(
            "One line per receipt. Put a Job ID on it only if the "
            "cost belongs to that visit - mulch delivered for it, "
            "the tip fee for its waste. Leave it blank for insurance, "
            "rent, advertising and everything else that is the cost "
            "of being open."),
        extra_notes=[
            "Booking a material purchase here with a Material ID and "
            "a quantity is what fills the Materials Inventory. Mark "
            "it as a purchase when it comes into the yard and as "
            "usage when it goes out to a job - the same tab, the "
            "'Purchase or usage' column apart.",
            "For material movements enter purchase amount on Purchase "
            "and the cost of stock consumed on Usage or Wastage. "
            "Monthly costs count purchases, not stock usage; job costs "
            "count usage linked to the job, not inventory purchases.",
            "Do not re-enter fuel from the Vehicle & Fuel Tracker. "
            "It is already counted there, and the monthly reports "
            "add the two together.",
            "The tax category column is there to make your "
            "accountant's year-end quicker. It is a label for your "
            "own records, not tax advice, and what is deductible "
            "depends on where you trade.",
        ],
        columns=[
            id_col("date", '"EXP-"', digits=5, header="Line"),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="Start here."),
            Col("supplier", "Paid to", 22, "text",
                note="Who got the money."),
            Col("description", "What for", 30, "wrap"),
            Col("category", "Category", 22, "text",
                validate=list_from("ExpenseCategoryList"),
                note="Four of these - materials, fuel, subcontract "
                     "and disposal - count as job costs when a Job ID "
                     "is attached."),
            Col("amount", "Amount", 11, "money",
                validate=amount(0, 1000000),
                cf=money_cf(),
                note="What you paid, including tax if you cannot "
                     "reclaim it."),
            Col("tax_amount", "Tax paid", 10, "money",
                validate=amount(0, 1000000),
                note="The tax portion, if you are registered and can "
                     "reclaim it."),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the visit this cost belongs to."),
                note="Only when the cost belongs to one visit. This is "
                     "what makes job profit real rather than "
                     "theoretical."),
            Col("job_address", "Where", 24, "text",
                formula='=IF({job}{r}="","",'
                        'IFERROR(INDEX('
                        '[[Job & Work Orders.address]],'
                        'MATCH({job}{r},'
                        '[[Job & Work Orders.id]],0))&"",'
                        '"Check - Job ID not found"))',
                cf=[{"type": "text", "criteria": "containing",
                     "value": "Check -", "fmt": "bad"}]),
            Col("material", "Material ID", 11, "id",
                validate=pick("MaterialIDList",
                              "Only for material purchases and usage. "
                              "Pick from the Materials Inventory."),
                note="Fills the stock figures on the Materials tab."),
            Col("movement", "Purchase or usage", 15, "text",
                validate=pick("StockMoveList",
                              "Is this material coming into the yard "
                              "or going out to a job?"),
                note="'Purchase' adds to stock; 'Usage' and "
                     "'Wastage' both take it away. Leave blank for "
                     "anything that is not a material."),
            Col("quantity", "Quantity", 10, "number1",
                validate=amount(0, 1000000,
                                "How many units, in the material's own "
                                "unit."),
                note="In the unit set on the Materials tab - bags, "
                     "yards, gallons."),
            Col("equipment", "Equipment ID", 11, "id",
                validate=pick("EquipmentIDList",
                              "For repairs, servicing and parts - "
                              "which machine was it for?"),
                note="Builds each machine's running cost and tells you "
                     "when repairing stops being worth it."),
            Col("vehicle", "Vehicle", 14, "text",
                validate=pick("VehicleList",
                              "For vehicle costs not already on the "
                              "fuel tracker."),
                note="Use the Vehicle & Fuel Tracker for fuel. This is "
                     "for anything else."),
            Col("payment_method", "Paid by", 15, "text",
                validate=list_from("PaymentMethodList")),
            Col("reference", "Receipt no.", 13, "text",
                note="Where to find the paperwork in six months."),
            Col("tax_category", "Tax category", 18, "text",
                validate=list_from("TaxCategoryList"),
                note="A label for your accountant. Not tax advice."),
            Col("recurring", "Recurring", 10, "flag",
                validate=yesno("Does this come round every month?"),
                note="Insurance, rent, software. Worth knowing what "
                     "your fixed monthly floor is."),
            Col("billable", "Rebill?", 9, "flag",
                validate=yesno("Will you charge this on to the "
                               "customer?"),
                note="Rebilled costs should appear as extras on the "
                     "job, otherwise you have paid for them twice."),
            Col("receipt_link", "Receipt link", 18, "link",
                note="A link to the photo of the receipt in your cloud "
                     "drive."),
            Col("notes", "Notes", 24, "wrap"),

            # Purchase-basis management costs and job-level allocation.
            Col("period_cost", "Period cost", 11, "money",
                formula=zero("date", 'IF(OR({movement}{r}="Usage",'
                             '{movement}{r}="Wastage"),0,{amount}{r})'),
                hidden=True),
            Col("allocated_cost", "Job allocated cost", 11, "money",
                formula=zero("date", 'IF(AND({material}{r}<>"",'
                             '{movement}{r}="Purchase"),0,{amount}{r})'),
                hidden=True),
            # ---- the flags other tabs count on -----------------------
            Col("is_job_cost", "Job cost", 8, "int",
                formula=zero("date",
                             'IF(AND({job}{r}<>"",'
                             f'{is_job_cost("{category}{r}")}),1,0)'),
                hidden=True,
                note="A job cost is one with a Job ID AND a category "
                     "that belongs to a job."),
            Col("is_overhead", "Overhead", 8, "int",
                formula=zero("date",
                             'IF({is_job_cost}{r}=1,0,1)'),
                hidden=True),
            Col("is_purchase", "Purchase", 8, "int",
                formula=zero("date",
                             'IF(AND({material}{r}<>"",'
                             '{movement}{r}="Purchase",'
                             '{quantity}{r}>0),1,0)'),
                hidden=True),
            Col("is_usage", "Usage", 7, "int",
                formula=zero("date",
                             'IF(AND({material}{r}<>"",'
                             '({movement}{r}="Usage")+'
                             '({movement}{r}="Wastage")>0,'
                             '{quantity}{r}>0),1,0)'),
                hidden=True),
            Col("unit_cost", "Cost per unit", 11, "money",
                formula='=IF({date}{r}="","",'
                        'IF({quantity}{r}<=0,"",'
                        'IF({is_purchase}{r}=0,"",'
                        'ROUND({amount}{r}/'
                        '{quantity}{r},2))))',
                note="What this delivery actually cost per unit. "
                     "Compare it with the Materials tab - prices "
                     "move."),
            date_num_col("date", "date_num"),
            month_col("date"),

            Col("alert", "What needs doing", 44, "wrap",
                formula=alert_chain("date", [
                    ('{job_address}{r}="Check - Job ID not found"',
                     "Check - the Job ID on this line does not exist"),
                    ('{amount}{r}=0',
                     "Add - no amount on this line"),
                    ('AND({material}{r}<>"",{movement}{r}="")',
                     "Add - material with no purchase or usage set, so "
                     "stock is not moving"),
                    ('AND({material}{r}<>"",{quantity}{r}=0)',
                     "Add - material with no quantity"),
                    ('AND({category}{r}="Materials",{job}{r}="",'
                     '{material}{r}="")',
                     "Check - materials cost tied to neither a job nor "
                     "a material"),
                    ('{category}{r}=""',
                     "Add - no category, so it will not reach the "
                     "right report"),
                    ('AND({billable}{r}="Yes",{job}{r}="")',
                     "Check - marked to rebill but no job to rebill "
                     "it on"),
                    ('{reference}{r}=""',
                     "Add - no receipt reference"),
                ]),
                cf=alert_cf()),
        ],
    )
