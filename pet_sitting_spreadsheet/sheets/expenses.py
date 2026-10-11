"""`Expenses` - every business cost, with tax, deductibility and approvals."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import alert_cf, blank, id_col, month_col, status_cf

NAME = "Expenses"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("date", '"EX-"'),
        Col("date", "Date", 12, "date", validate=date_check()),
        Col("category", "Category", 22, "text",
            validate=list_from("ExpenseCategoryList")),
        Col("description", "Description", 34, "wrap"),
        Col("supplier", "Supplier / vendor", 20, "text"),
        Col("amount", "Amount paid", 12, "money",
            validate=number_check(0, 1000000),
            note="Enter the full amount you paid, including tax."),
        Col("tax", "Tax included", 11, "money",
            formula=blank("amount",
                          'IF(TaxRegistered<>"Yes",0,'
                          'ROUND({amount}{r}-{amount}{r}/(1+TaxRate),2))')),
        Col("net", "Net cost", 11, "money",
            formula=blank("amount", 'ROUND({amount}{r}-{tax}{r},2)')),
        Col("method", "Paid by", 16, "text",
            validate=list_from("PaymentMethodList")),
        Col("type", "Business / personal", 12, "status",
            validate=list_from("BusinessPersonalList"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Personal", "fmt": "muted"}]),
        Col("deductible", "Business use %", 10, "percent",
            validate=number_check(0, 1),
            note="Blank counts as 100%. Use 50% for a phone bill you share "
                 "with personal use."),
        Col("claim", "Claimable amount", 12, "money",
            formula=blank("amount",
                          'IF({type}{r}="Personal",0,'
                          'ROUND({net}{r}*IF({deductible}{r}="",1,'
                          '{deductible}{r}),2))')),
        Col("receipt", "Receipt link / ref", 18, "text"),
        Col("recurring", "Recurring", 12, "text",
            validate=list_from("RecurringExpenseList")),
        Col("next_due", "Next due", 12, "date",
            formula='=IF(OR({date}{r}="",{recurring}{r}="",'
                    '{recurring}{r}="No"),"",'
                    'IF({recurring}{r}="Monthly",EDATE({date}{r},1),'
                    'IF({recurring}{r}="Quarterly",EDATE({date}{r},3),'
                    'IF({recurring}{r}="Annually",EDATE({date}{r},12),'
                    '{date}{r}+IF({recurring}{r}="Weekly",7,'
                    'IF({recurring}{r}="Fortnightly",14,0))))))'),
        Col("approval", "Approval", 12, "status",
            validate=list_from("ExpenseApprovalList"), cf=status_cf()),
        Col("related", "Related client / booking", 18, "text"),
        Col("staff", "Staff member", 15, "text",
            validate=list_from("StaffNames")),
        Col("notes", "Notes", 26, "wrap"),
        month_col("date"),
        Col("alert", "Action needed", 22, "status",
            formula=blank(
                "date",
                'IF({approval}{r}="Pending","Awaiting approval",'
                'IF({receipt}{r}="","Missing receipt",'
                'IF(AND({next_due}{r}<>"",{next_due}{r}<=TODAY()),'
                '"Recurring cost due","OK")))'),
            cf=alert_cf()),
    ]

    return SheetSpec(
        name=NAME,
        title="Expense Management",
        subtitle="Fuel, supplies, wages, insurance, software and every "
                 "other cost - split into tax, net and claimable amounts.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.bad_text,
        freeze_cols=2,
        samples=sample(cfg).expenses,
        help_text="Keep a photo of every receipt. The Reports tab groups "
                  "these by category and the Budget tab compares them to "
                  "your monthly budget.",
    )
