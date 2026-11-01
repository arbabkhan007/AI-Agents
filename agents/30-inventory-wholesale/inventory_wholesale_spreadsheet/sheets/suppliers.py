"""7. Supplier Database - who you buy from, and how well it goes.

Contact details are the boring half. The useful half is the scorecard
at the right hand end, which is calculated from your own purchase
order history: what you have actually spent with them, how many
deliveries arrived late, and what their real lead time has been as
opposed to the one they quoted you.

A supplier who promises seven days and takes fourteen is not a
reliability problem you can fix, but it is a number you can order
around.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, id_col, margin,
                     money_cf, rating_cf, scale_cf, score_validation,
                     status_cf, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Supplier Database"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("name", "SupplierPrefix", digits=cfg.digits("supplier"),
               header="Supplier ID",
               note="Generated. This is what products and purchase "
                    "orders point at."),
        Col("name", "Supplier name", 24, "text"),
        Col("contact", "Contact", 18, "text"),
        Col("email", "Email", 24, "text"),
        Col("phone", "Phone", 15, "text"),
        Col("website", "Website", 20, "link"),
        Col("address", "Address", 28, "wrap"),
        Col("city", "City", 14, "text"),
        Col("country", "Country", 13, "text"),
        Col("type", "Supplier type", 14, "text",
            validate=list_from("SupplierTypeList")),
        Col("supplies", "What they supply", 22, "wrap",
            note="Plain words. 'Wax, wicks, jars' beats a category "
                 "code when you are trying to remember who sells "
                 "lids."),

        # ---- commercial terms -------------------------------------
        Col("terms", "Payment terms", 13, "text",
            validate=list_from("PaymentTermsList")),
        Col("currency", "Currency", 9, "text",
            validate=list_from("CurrencyList"),
            note="What they invoice in. Costs elsewhere in the "
                 "workbook are in your own currency - convert when "
                 "you enter the purchase order."),
        Col("lead_time", "Lead time (days)", 13, "int",
            validate=number_check(0, 365),
            note="What they promise. The scorecard works out what "
                 "they actually do."),
        Col("moq", "Min order", 10, "money",
            validate=number_check(0, 1000000),
            note="Minimum order value, if they have one."),
        Col("free_ship_over", "Free ship over", 12, "money",
            validate=number_check(0, 1000000)),
        Col("discount", "Standard discount", 13, "percent0",
            validate=number_check(0, 1),
            note="Any trade discount they give you as standard."),
        Col("account_no", "Account no.", 13, "text"),
        Col("tax_id", "Tax / VAT no.", 14, "text"),

        # ---- relationship -----------------------------------------
        Col("status", "Status", 12, "status",
            validate=list_from("SupplierStatusList"), cf=status_cf()),
        Col("preferred", "Preferred", 10, "flag",
            validate=yesno("Your first choice for these goods."),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("rating", "Rating", 9, "rating",
            validate=score_validation(5), cf=rating_cf(),
            note="Your own score out of five. Quality, "
                 "communication, how they handle a problem."),
        Col("first_order", "First order", 11, "date",
            validate=date_check()),
        Col("notes", "Notes", 30, "wrap"),

        # ---- scorecard, all calculated ----------------------------
        Col("orders", "Orders", 8, "int",
            formula=zero("name", 'COUNTIFS('
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r})'),
            note="Purchase order lines placed with them."),
        Col("spend", "Total spend", 12, "money",
            formula=zero("name", 'SUMIFS('
                                 '[[Purchase Orders.total]],'
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r})'),
            cf=money_cf()),
        Col("spend_year", "Spend this year", 13, "money",
            formula=zero("name", 'SUMIFS('
                                 '[[Purchase Orders.total]],'
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r},'
                                 '[[Purchase Orders.order_num]],'
                                 '">="&YearStart,'
                                 '[[Purchase Orders.order_num]],'
                                 '"<="&YearEnd)'),
            note="Calendar year to date, on the order date."),
        Col("open_orders", "Open", 7, "int",
            formula=zero("name", 'COUNTIFS('
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r},'
                                 '[[Purchase Orders.is_open]],1)'),
            note="Ordered and not yet fully received."),
        Col("open_value", "Open value", 11, "money",
            formula=zero("name", 'SUMIFS('
                                 '[[Purchase Orders.outstanding_value]],'
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r},'
                                 '[[Purchase Orders.is_open]],1)'),
            note="Money committed to goods that have not arrived."),
        Col("late_orders", "Late", 7, "int",
            formula=zero("name", 'COUNTIFS('
                                 '[[Purchase Orders.supplier]],'
                                 '{id}{r},'
                                 '[[Purchase Orders.is_late]],1)'),
            cf=[{"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "bad"}]),
        Col("on_time_rate", "On time", 9, "percent0",
            formula='=IF({name}{r}="","",IF({orders}{r}<=0,"",'
                    'ROUND(1-{late_orders}{r}/{orders}{r},4)))',
            cf=scale_cf(),
            note="Share of their order lines that were not late. "
                 "Below 80% and you are the one absorbing it."),
        Col("actual_lead", "Actual lead", 11, "number1",
            formula='=IF({name}{r}="","",'
                    'IF(COUNTIFS([[Purchase Orders.supplier]],'
                    '{id}{r},[[Purchase Orders.lead_days]],">0")<=0,'
                    '"",ROUND(SUMIFS('
                    '[[Purchase Orders.lead_days]],'
                    '[[Purchase Orders.supplier]],{id}{r},'
                    '[[Purchase Orders.lead_days]],">0")/'
                    'COUNTIFS([[Purchase Orders.supplier]],{id}{r},'
                    '[[Purchase Orders.lead_days]],">0"),1)))',
            note="Average days from order to delivery, measured off "
                 "your own received purchase orders."),
        Col("lead_gap", "Lead gap", 9, "number1",
            formula='=IF({name}{r}="","",IF({actual_lead}{r}="","",'
                    'ROUND({actual_lead}{r}-{lead_time}{r},1)))',
            cf=[{"type": "cell", "criteria": ">", "value": 3,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0,
                 "fmt": "warn"},
                {"type": "cell", "criteria": "<=", "value": 0,
                 "fmt": "good"}],
            note="How many days longer they really take than they "
                 "said. Positive is bad. Add it to the quoted lead "
                 "time when you set reorder points."),
        Col("last_order", "Last order", 11, "date",
            formula='=IF({name}{r}="","",'
                    'IF({last_order_num}{r}<=0,"",'
                    '{last_order_num}{r}))'),
        Col("last_order_num", "Last order (n)", 9, "number",
            formula=zero("name", 'SUMPRODUCT(MAX(('
                                 '[[Purchase Orders.supplier]]='
                                 '{id}{r})*'
                                 '[[Purchase Orders.order_num]]))'),
            hidden=True),
        Col("days_since", "Days since", 10, "int",
            formula='=IF({name}{r}="","",'
                    'IF({last_order_num}{r}<=0,"",'
                    'TodayDate-{last_order_num}{r}))'),
        Col("products", "Products", 9, "int",
            formula=zero("name", 'COUNTIFS('
                                 '[[Product & SKU Database.'
                                 'supplier]],{id}{r})'),
            note="How many SKUs you buy from them. One supplier "
                 "holding thirty lines is a concentration risk."),
        Col("share", "Share of spend", 12, "percent0",
            formula=blank("name", margin("{spend}{r}",
                                         "TotalPurchaseSpend")),
            cf=scale_cf(), hidden=True),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Supplier Database",
        subtitle=("Contacts and terms on the left; how they actually "
                  "perform, measured from your own orders, on the "
                  "right."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        samples=sample("suppliers", cfg),
        help_text=("Add a supplier here before you raise a purchase "
                   "order - the Supplier ID is what the order points "
                   "at. The scorecard columns fill themselves in as "
                   "orders are received."),
        extra_notes=[
            "Lead gap is the column worth watching. A supplier who "
            "quotes seven days and takes fourteen is not necessarily "
            "a supplier to drop, but your reorder points should be "
            "built on fourteen.",
            "Keep retired suppliers rather than deleting them. Their "
            "purchase orders are part of last year's cost of goods, "
            "and a deleted Supplier ID leaves those orders pointing "
            "at nothing.",
        ],
    )


def _alert() -> str:
    return alert_chain("name", [
        ('{email}{r}=""', "Add - email address"),
        ('{terms}{r}=""', "Add - payment terms"),
        ('{lead_time}{r}<=0', "Add - lead time, the reorder planner "
                              "needs it"),
        ('{status}{r}=""', "Add - supplier status"),
        ('{status}{r}="Inactive"', [
            ('{open_orders}{r}>0',
             "Check - marked inactive with orders still open"),
        ], "OK"),
        ('AND({lead_gap}{r}<>"",{lead_gap}{r}>7)',
         "Urgent - deliveries run over a week late, fix the lead "
         "time"),
        ('AND({orders}{r}>=3,{on_time_rate}{r}<>"",'
         '{on_time_rate}{r}<0.8)',
         "Action - late more often than not, worth a conversation"),
        ('AND({lead_gap}{r}<>"",{lead_gap}{r}>2)',
         "Check - slower than quoted, raise the lead time"),
        ('{open_value}{r}>0', [
            ('{late_orders}{r}>0',
             "Chase - money committed to a late delivery"),
        ], "OK"),
        ('AND({products}{r}>0,{orders}{r}=0)',
         "Check - products assigned but nothing ever ordered"),
    ])
