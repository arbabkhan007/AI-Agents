"""11 Expenses - every cost, categorised and month-stamped."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import date_check, list_from, number_check
from . import common as C
from .. import sample_data

NAME = "11 Expenses"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="11  Expenses",
        subtitle="Rent, utilities, supplies, marketing, software, "
                 "equipment - with due dates and a month stamp for the "
                 "P&L.",
        tab_color="#96587A",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="One row per cost. The month column stamps each row "
                  "yyyy-mm so the Profit & Loss and Goals tabs can sum "
                  "any month without helpers.",
        columns=[
            Col("id", "Exp ID", 10, "id",
                formula='="X-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("month", "Month", 9, "flag",
                formula='IF({date}{r}="","",' + C.month_of("{date}{r}") + ')'),
            Col("category", "Category", 13, "text",
                validate=list_from("ListExpCats")),
            Col("vendor", "Vendor", 22, "text"),
            Col("description", "What for", 34, "wrap"),
            Col("recurring", "Recurring", 11, "flag",
                validate=list_from("ListRecurring")),
            Col("method", "Paid by", 13, "text",
                validate=list_from("ListMethods")),
            Col("due", "Due date", 12, "date", validate=date_check()),
            Col("paid", "Paid date", 12, "date", validate=date_check()),
            Col("amount", "Amount", 11, "money",
                validate=number_check(0, 1000000)),
            Col("notes", "Notes", 26, "wrap"),
        ],
        samples=sample_data.expense_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Product costs belong here too when you buy stock - the "
            "purchase order register on tab 14 tracks what arrived.",
            "The Goals tab compares each category against its monthly "
            "budget.",
        ],
    )
