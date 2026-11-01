"""9. Wholesale Customer CRM - the shops that buy from you.

A wholesale customer is not a retail buyer with a bigger basket. They
have a tier, terms, a credit limit, a minimum order and a buyer who
expects you to remember what they ordered last time. All of that sits
here, and the Wholesale Orders tab reads the tier off this sheet to
price their lines automatically.

The columns on the right are the ones that decide whether a stockist
is worth keeping: what they have spent, what they still owe, whether
they pay on time, and how long it has been since they last ordered.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, id_col, margin,
                     money_cf, owing_cf, rating_cf, scale_cf,
                     score_validation, status_cf, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Wholesale Customer CRM"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("business", "CustomerPrefix",
               digits=cfg.digits("customer"), header="Customer ID",
               note="Generated. Wholesale orders point at this."),
        Col("business", "Business name", 24, "text"),
        Col("contact", "Buyer", 18, "text",
            note="The person who actually places the order."),
        Col("email", "Email", 24, "text"),
        Col("phone", "Phone", 14, "text"),
        Col("website", "Website / shop", 20, "link"),
        Col("address", "Address", 26, "wrap"),
        Col("city", "City", 13, "text"),
        Col("region", "Region", 12, "text"),
        Col("postcode", "Postcode", 10, "text"),
        Col("country", "Country", 12, "text"),
        Col("type", "Business type", 14, "text",
            validate=list_from("CustomerTypeList"),
            note="Boutique, gift shop, online retailer, distributor. "
                 "Useful when you are deciding who to show a new "
                 "range to first."),

        # ---- trading terms ----------------------------------------
        Col("tier", "Price tier", 12, "text",
            validate=list_from("CustomerTierList"),
            note="Which price list they buy on. The Wholesale Orders "
                 "tab reads this to price their lines, so it is the "
                 "single most important cell on the row."),
        Col("terms", "Payment terms", 13, "text",
            validate=list_from("PaymentTermsList")),
        Col("credit_limit", "Credit limit", 12, "money",
            validate=number_check(0, 1000000),
            note="The most you are willing to be owed by them at "
                 "once. Leave at zero for prepay-only accounts."),
        Col("min_order", "Min order", 10, "money",
            validate=number_check(0, 1000000),
            note="Their minimum order value. Orders below it are "
                 "flagged on the order line."),
        Col("discount", "Extra discount", 12, "percent0",
            validate=number_check(0, 1),
            note="Anything on top of their tier price - an opening "
                 "order deal, a loyalty arrangement. Applied after "
                 "the tier price on every line."),
        Col("tax_exempt", "Tax exempt", 10, "flag",
            validate=yesno("Resellers often are. Check locally."),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "info"}]),
        Col("resale_no", "Resale cert. no.", 14, "text",
            note="Only if your jurisdiction requires you to hold it. "
                 "Nothing else about their identity belongs in a "
                 "spreadsheet."),
        Col("shipping_pref", "Shipping", 13, "text",
            validate=list_from("ShippingMethodList")),

        # ---- relationship -----------------------------------------
        Col("status", "Status", 12, "status",
            validate=list_from("CustomerStatusList"), cf=status_cf()),
        Col("rating", "Rating", 8, "rating",
            validate=score_validation(5), cf=rating_cf(),
            note="How good an account are they, all things "
                 "considered - volume, payment, how much hand "
                 "holding."),
        Col("first_order", "First order", 11, "date",
            validate=date_check()),
        Col("source", "How they found you", 16, "text",
            validate=list_from("LeadSourceList")),
        Col("notes", "Notes", 28, "wrap",
            note="What they stock, what sells for them, who else "
                 "they buy from. This is the column that makes the "
                 "next call easy."),

        # ---- calculated account health ----------------------------
        Col("orders", "Orders", 8, "int",
            formula=zero("business",
                         'IFERROR(SUMPRODUCT((('
                         '[[Wholesale Orders.customer]]={id}{r})*'
                         '[[Wholesale Orders.is_first_line]])),0)'),
            note="Counted as distinct orders, not order lines."),
        Col("units", "Units", 8, "int",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.qty]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r},'
                                     '[[Wholesale Orders.is_shipped]]'
                                     ',1)'),
            hidden=True),
        Col("revenue", "Total revenue", 13, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'line_total]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r})'),
            cf=money_cf()),
        Col("revenue_year", "This year", 12, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'line_total]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r},'
                                     '[[Wholesale Orders.date_num]],'
                                     '">="&YearStart,'
                                     '[[Wholesale Orders.date_num]],'
                                     '"<="&YearEnd)')),
        Col("profit", "Gross profit", 12, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'line_profit]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r})'),
            cf=money_cf()),
        Col("gp_pct", "GP%", 8, "percent0",
            formula=blank("business", margin("{profit}{r}",
                                             "{revenue}{r}")),
            cf=scale_cf(),
            note="Their margin to you. A big account at 18% is "
                 "worth less than a small one at 55%."),
        Col("avg_order", "Avg order", 11, "money",
            formula='=IF({business}{r}="","",IF({orders}{r}<=0,"",'
                    'ROUND({revenue}{r}/{orders}{r},2)))'),
        Col("owing", "Owing now", 11, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'outstanding]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r})'),
            cf=owing_cf(),
            note="Invoiced and unpaid, across every open order."),
        Col("overdue", "Overdue", 11, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'outstanding]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r},'
                                     '[[Wholesale Orders.is_overdue]]'
                                     ',1)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0.004,
                 "fmt": "bold_bad"}]),
        Col("credit_used", "Credit used", 11, "percent0",
            formula='=IF({business}{r}="","",'
                    'IF({credit_limit}{r}<=0,"",'
                    'ROUND({owing}{r}/{credit_limit}{r},4)))',
            cf=[{"type": "cell", "criteria": ">=", "value": 1,
                 "fmt": "bold_bad"},
                {"type": "cell", "criteria": ">=", "value": 0.8,
                 "fmt": "warn"}]),
        Col("reserved_value", "Reserved for them", 14, "money",
            formula=zero("business", 'SUMIFS('
                                     '[[Wholesale Orders.'
                                     'line_total]],'
                                     '[[Wholesale Orders.customer]],'
                                     '{id}{r},'
                                     '[[Wholesale Orders.'
                                     'is_reserved]],1)'),
            hidden=True,
            note="Stock sitting on your shelf with their name on it."),
        Col("last_order_num", "Last order (n)", 9, "number",
            formula=zero("business",
                         'SUMPRODUCT(MAX(('
                         '[[Wholesale Orders.customer]]={id}{r})*'
                         '[[Wholesale Orders.date_num]]))'),
            hidden=True),
        Col("last_order", "Last order", 11, "date",
            formula='=IF({business}{r}="","",'
                    'IF({last_order_num}{r}<=0,"",'
                    '{last_order_num}{r}))'),
        Col("days_since", "Days since", 10, "int",
            formula='=IF({business}{r}="","",'
                    'IF({last_order_num}{r}<=0,"",'
                    'TodayDate-{last_order_num}{r}))',
            cf=[{"type": "cell", "criteria": ">", "value": 180,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 90,
                 "fmt": "warn"}]),
        Col("revenue_rank", "Rank", 7, "int",
            formula=blank("business",
                          'COUNTIFS({revenue_first}:{revenue_last},'
                          '">"&{revenue}{r})+'
                          'COUNTIFS({revenue_first}:{revenue}{r},'
                          '{revenue}{r})'),
            hidden=True),
        Col("share", "Share", 8, "percent0",
            formula=blank("business", margin("{revenue}{r}",
                                             "WholesaleRevenue")),
            cf=scale_cf(), hidden=True,
            note="What share of your wholesale revenue they are. "
                 "Anything over a third is a concentration risk."),

        Col("alert", "What needs doing", 32, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Wholesale Customer CRM",
        subtitle=("Stockists, their terms and their tier - and, on "
                  "the right, whether the account is actually worth "
                  "having."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("customers", cfg),
        help_text=("Set up the account here first. The price tier on "
                   "this row is what the Wholesale Orders tab uses "
                   "to price every line they buy, so get it right "
                   "once and never price an order by hand again."),
        extra_notes=[
            "Credit limit and Owing now work together. When an "
            "account goes past its limit the alert says so before "
            "you pick the next order, which is the only moment the "
            "information is any use.",
            "A stockist who has not ordered in six months has "
            "usually not fallen out with you - they have just run "
            "out and forgotten. Days since is the cheapest sales "
            "lead in the workbook.",
        ],
    )


def _alert() -> str:
    return alert_chain("business", [
        ('{email}{r}=""', "Add - buyer's email"),
        ('{tier}{r}=""',
         "Add - price tier, orders cannot be priced without it"),
        ('{terms}{r}=""', "Add - payment terms"),
        ('{status}{r}=""', "Add - account status"),
        ('{overdue}{r}>0.004',
         "Overdue - money past its due date, chase before shipping "
         "again"),
        ('AND({credit_limit}{r}>0,{owing}{r}>{credit_limit}{r})',
         "Urgent - over their credit limit, do not ship"),
        ('AND({credit_limit}{r}>0,{credit_used}{r}<>"",'
         '{credit_used}{r}>=0.8)',
         "Check - close to their credit limit"),
        ('{status}{r}="On hold"',
         "Action - account on hold, nothing should ship"),
        ('AND({orders}{r}>0,{gp_pct}{r}<>"",{gp_pct}{r}<MinGP)',
         "Check - margin on this account is below your floor"),
        ('AND({orders}{r}>0,{days_since}{r}<>"",'
         '{days_since}{r}>DormantDays)',
         "Follow up - gone quiet, worth a call"),
        ('AND({status}{r}="Prospect",{orders}{r}=0)',
         "Follow up - prospect who has never ordered"),
        ('AND({orders}{r}=0,{first_order}{r}="")',
         "Check - set up but never ordered"),
    ])
