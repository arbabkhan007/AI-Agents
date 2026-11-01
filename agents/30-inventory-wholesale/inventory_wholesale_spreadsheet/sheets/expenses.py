"""19. Expense Tracker - and the separation that keeps margins honest.

There are two kinds of money going out of an inventory business and
mixing them produces nonsense in both directions.

Buying stock is not an expense in the way rent is. It is cash
converted into an asset that sits on a shelf until it sells, at which
point it becomes cost of goods sold. The workbook already counts it,
line by line, on the Purchase Orders tab - every product's margin is
built from it.

So a stock purchase typed in here as well would be counted twice:
once as COGS against the product and again as an operating cost
against the business. The Stock purchase? column flags exactly that,
and anything it flags is excluded from the operating expense totals
rather than quietly inflating them.

Rent, software, packaging, advertising, your accountant - those
belong here, and nowhere else.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, blank, date_num_col,
                     id_col, monthly_equivalent, month_col,
                     seq_num_col, yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Expense Tracker"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        id_col("description", "ExpensePrefix",
               digits=cfg.digits("expense"), header="Expense ID"),
        Col("date", "Date", 11, "date", validate=date_check()),
        Col("description", "What it was", 28, "text"),
        Col("category", "Category", 18, "text",
            validate=list_from("ExpenseCategoryList"),
            note="Pick carefully. Stock purchases and Raw materials "
                 "are treated as inventory, not as running costs."),
        Col("supplier", "Paid to", 18, "text"),
        Col("amount", "Amount", 11, "money",
            validate=number_check(0, 1000000)),
        Col("tax_amount", "Tax / VAT", 10, "money",
            validate=number_check(0, 1000000),
            note="The recoverable tax on the invoice, if your "
                 "jurisdiction and registration let you reclaim it."),
        Col("total", "Total paid", 11, "money",
            formula=zero("description", 'ROUND({amount}{r}+'
                                        '{tax_amount}{r},2)')),
        Col("method", "Paid by", 12, "text",
            validate=list_from("PaymentMethodList")),
        Col("recurring", "Recurring", 11, "text",
            validate=list_from("FrequencyList"),
            note="One-off, monthly, quarterly, yearly. Anything "
                 "repeating gets converted to a monthly figure in "
                 "the next column."),
        Col("monthly", "Per month", 11, "money",
            formula=blank("description",
                          monthly_equivalent("{amount}{r}",
                                             "{recurring}{r}")),
            note="What this really costs each month. A yearly "
                 "licence and a monthly subscription are not "
                 "comparable until both are stated the same way."),
        Col("tax_category", "Tax category", 16, "text",
            validate=list_from("TaxCategoryList"),
            note="How your accountant will want it treated. Not "
                 "advice - a label, so the conversation is short."),
        Col("receipt", "Receipt", 9, "flag",
            validate=yesno("Have you actually got it?"),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "No", "fmt": "warn"},
                {"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("reference", "Reference", 13, "text",
            note="Invoice number, or the PO this relates to."),
        Col("notes", "Notes", 24, "wrap"),

        # ---- the separation ---------------------------------------
        Col("is_stock", "Stock purchase?", 13, "int",
            formula=zero("description",
                         'IF(COUNTIF(StockCategoryList,'
                         '{category}{r})>0,1,0)'),
            hidden=True,
            note="1 when the category is a stock category. These "
                 "are excluded from operating expenses because the "
                 "Purchase Orders tab already counts them as cost "
                 "of goods."),
        Col("operating", "Operating cost", 12, "money",
            formula=zero("description", 'IF({is_stock}{r}=1,0,'
                                        '{amount}{r})'),
            note="What this contributes to running the business, as "
                 "opposed to filling the shelves. Stock purchases "
                 "show zero here on purpose."),
        Col("inventory_spend", "Inventory spend", 13, "money",
            formula=zero("description", 'IF({is_stock}{r}=1,'
                                        '{amount}{r},0)'),
            hidden=True),
        Col("duplicate", "Possible duplicate", 14, "int",
            formula=zero("description",
                         'IF({amount}{r}<=0,0,'
                         'COUNTIFS({date_first}:{date_last},'
                         '{date}{r},{amount_first}:{amount_last},'
                         '{amount}{r},{supplier_first}:'
                         '{supplier_last},{supplier}{r}))'),
            hidden=True,
            note="Same day, same amount, same payee. Usually a "
                 "double entry rather than a double payment, but "
                 "worth a look either way."),
        Col("size_flag", "Large", 7, "int",
            formula=zero("description",
                         'IF({amount}{r}>LargeExpenseLevel,1,0)'),
            hidden=True),

        month_col("date"),
        date_num_col("date", "date_num"),
        seq_num_col("description"),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Expense Tracker",
        subtitle=("Running costs. Stock purchases are counted on the "
                  "Purchase Orders tab and are deliberately kept out "
                  "of these totals."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("expenses", cfg),
        help_text=("Everything that is not stock: rent, postage, "
                   "software, advertising, fees, your accountant. "
                   "Recurring costs get converted to a monthly "
                   "figure so you can see what the business costs "
                   "to keep open."),
        extra_notes=[
            "If you do type a stock purchase in here - and sooner "
            "or later everybody does - the Stock purchase? flag "
            "catches it and keeps it out of the operating cost "
            "total. It is not an error you need to fix, just one "
            "the workbook refuses to let distort your margins.",
            "Tax category is a label for your accountant's benefit, "
            "not a ruling. What is deductible, and when, depends "
            "entirely on where you trade and how you are set up.",
        ],
    )


def _alert() -> str:
    return alert_chain("description", [
        ('{date}{r}=""', "Add - date"),
        ('{amount}{r}<=0', "Add - amount"),
        ('{category}{r}=""', "Add - category"),
        ('{duplicate}{r}>1',
         "Duplicate - same payee, same amount, same day"),
        ('AND({is_stock}{r}=1,{reference}{r}="")',
         "Check - stock purchase, is it already on a purchase "
         "order?"),
        ('{receipt}{r}="No"', "Missing - no receipt for this one"),
        ('AND({size_flag}{r}=1,{receipt}{r}<>"Yes")',
         "Urgent - large payment with no receipt"),
        ('{receipt}{r}=""', "Check - have you got the receipt?"),
        ('{tax_category}{r}=""',
         "Add - tax category, your accountant will ask"),
        ('{recurring}{r}=""', "Add - is this a one-off or regular?"),
        ('{date}{r}>TodayDate', "Check - dated in the future"),
    ])
