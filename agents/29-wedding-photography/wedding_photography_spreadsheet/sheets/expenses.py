"""Expense Tracker - everything the business pays out.

Costs that can be pinned to a wedding carry its Booking ID and come
straight off that wedding's profit.  Everything else - insurance,
software, the website - is an overhead the whole year has to carry,
and is treated as one.
"""

from __future__ import annotations

from ..config import DISCLAIMER
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, blank, date_num_col, id_col, is_capital,
                     is_direct_cost, money_cf, month_col, monthly_equivalent,
                     status_cf, year_col, yesno, zero)

NAME = "Expense Tracker"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("date", "ExpensePrefix", digits=cfg.digits("expense"),
               header="Expense ID"),

        Col("date", "Date", 11, "date",
            validate=date_check(), group="What you paid"),
        Col("supplier", "Paid to", 20, "text", group="What you paid"),
        Col("category", "Category", 18, "text",
            validate=list_from("ExpenseCategoryList"),
            note="The category decides whether it comes off one "
                 "wedding or off the year as a whole.",
            group="What you paid"),
        Col("description", "What it was", 28, "wrap",
            group="What you paid"),
        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="Only for costs caused by one wedding - a second "
                 "shooter, an album, parking at the venue. Leave "
                 "blank for anything the whole business uses.",
            group="What you paid"),
        Col("amount", "Amount", 12, "money",
            validate=number_check(-1000000, 1000000), cf=money_cf(),
            note="What left your account, tax included.",
            group="What you paid"),
        Col("tax_amount", "Tax included", 11, "money",
            validate=number_check(0, 1000000),
            note="The sales tax or VAT part, if you can reclaim it.",
            group="What you paid"),
        Col("net", "Net of tax", 11, "money",
            formula=zero("date",
                         'ROUND(IF({amount}{r}="",0,{amount}{r})-'
                         'IF({tax_amount}{r}="",0,{tax_amount}{r}),2)'),
            group="What you paid"),
        Col("method", "How paid", 13, "text",
            validate=list_from("PaymentMethodList"),
            group="What you paid"),
        Col("receipt", "Receipt kept", 11, "flag",
            validate=yesno("Photograph it now. Thermal receipts fade "
                           "to blank in about a year, which is "
                           "exactly when you are asked for them."),
            cf=status_cf(), group="What you paid"),
        Col("reference", "Reference", 14, "text",
            group="What you paid"),

        # ---- how it is treated -------------------------------------------------
        Col("is_direct", "Wedding cost", 11, "flag",
            formula=blank("date",
                          'IF({booking}{r}<>"","Yes",'
                          f'IF({is_direct_cost("{category}{r}")},'
                          '"Yes","No"))'),
            note="A cost caused by one wedding. The booking subtracts "
                 "it from that wedding's profit.",
            group="How it is treated"),
        Col("is_overhead", "Overhead", 10, "flag",
            formula=blank("date",
                          'IF(OR({tax_category}{r}="Capital / asset",'
                          '{tax_category}{r}="Owner drawing",'
                          '{category}{r}="Tax & national insurance"),"No",'
                          'IF({is_direct}{r}="Yes","No","Yes"))'),
            group="How it is treated"),
        Col("is_capital", "Equipment buy", 11, "flag",
            formula=blank("date",
                          f'IF({is_capital("{category}{r}")},'
                          '"Yes","No")'),
            note="Kit you will use for years rather than something "
                 "consumed now. Usually claimed differently.",
            group="How it is treated"),
        Col("recurring", "Repeats", 12, "text",
            validate=list_from("FrequencyList"),
            note="Subscriptions, insurance, your website. Leave blank "
                 "for a one-off.",
            group="How it is treated"),
        Col("monthly", "A month", 11, "money",
            formula=blank("date",
                          'IF({recurring}{r}="","",'
                          + monthly_equivalent("{amount}{r}",
                                               "{recurring}{r}") + ")"),
            note="What a repeating cost really works out at each "
                 "month. A yearly insurance premium and a monthly "
                 "subscription are not comparable until both are "
                 "expressed this way.",
            group="How it is treated"),
        Col("annual", "A year", 11, "money",
            formula=zero("date",
                         'IF({monthly}{r}="",0,'
                         'ROUND({monthly}{r}*12,2))'),
            group="How it is treated"),

        # ---- tax ---------------------------------------------------------------
        Col("business_pct", "Business use", 11, "percent0",
            validate=number_check(0, 1),
            note="For anything used privately too - a phone, a car, "
                 "a room at home. Leave blank to mean entirely "
                 "business.",
            group="Tax"),
        Col("claimable", "Claimable part", 12, "money",
            formula=zero("date",
                         'ROUND({net}{r}*'
                         'IF({business_pct}{r}="",1,'
                         '{business_pct}{r}),2)'),
            note="Your own working figure. What is actually "
                 "deductible is a matter for your accountant and your "
                 "country's rules.",
            group="Tax"),
        Col("tax_category", "Tax category", 16, "text",
            validate=list_from("TaxCategoryList"), group="Tax"),
        Col("notes", "Notes", 24, "wrap", group="Tax"),

        Col("profit_cost", "Cost for profit", 13, "money",
            formula=zero("date", 'IF(OR({tax_category}{r}="Capital / asset",'
                         '{tax_category}{r}="Owner drawing",'
                         '{category}{r}="Tax & national insurance"),0,'
                         'ROUND(IF({amount}{r}="",0,{amount}{r})*'
                         'IF({business_pct}{r}="",1,{business_pct}{r}),2))'),
            note="Management cost: business share of gross amount, excluding "
                 "capital, owner drawings and tax payments. Not tax advice.",
            group="Tax"),
        month_col("date"),
        year_col("date"),
        date_num_col("date", "date_num", "Date number"),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({date}{r}="","",'
                'IF({amount}{r}="","Add - no amount",'
                'IF({category}{r}="","Add - no category",'
                'IF({receipt}{r}<>"Yes",'
                'IF({amount}{r}>=ReceiptThreshold,'
                '"Missing - no receipt for a large payment",'
                '"Missing - no receipt"),'
                'IF({is_direct}{r}="Yes",'
                'IF({booking}{r}="",'
                '"Add - wedding cost with no Booking ID","OK"),'
                'IF({business_pct}{r}<>"",'
                'IF({business_pct}{r}<=0,'
                '"Check - nothing claimable on this one","OK"),'
                '"OK"))))))'),
            cf=alert_cf(), group="Tax"),
    ]

    return SheetSpec(
        name=NAME,
        title="Expense Tracker",
        subtitle=("Everything the business pays out, split between "
                  "the weddings that caused it and the overheads that "
                  "did not"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("expenses", cfg),
        help_text=(
            "One row per payment. Put a Booking ID on anything caused "
            "by a particular wedding and it comes off that wedding's "
            "profit. An unlinked cost is overhead only when its category "
            "is not a wedding-specific category; direct categories need "
            "a Booking ID or they are excluded from profit."),
        extra_notes=[
            DISCLAIMER,
            "Photograph receipts the day you get them. Thermal paper "
            "fades to blank in about a year, which is roughly when "
            "somebody asks to see it.",
            "Equipment is flagged separately because most tax systems "
            "treat buying a camera differently from buying memory "
            "cards. Which rules apply to you is a question for your "
            "accountant.",
            "The repeating costs are the ones that creep. Four "
            "subscriptions at nineteen a month is nine hundred a year "
            "and nobody ever notices it leaving.",
        ],
    )
