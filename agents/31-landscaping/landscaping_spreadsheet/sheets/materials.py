"""16. Materials Inventory - mulch, seed, fertiliser and fuel cans.

Stock on hand is derived, never typed: opening stock, plus what the
expense tracker says you bought, minus what the jobs say you used.
Typing a stock figure over the top of a calculation is how a stock
sheet stops being believed, so this one will not let you.

The low-stock alert uses your own reorder point, and the three
columns next to it tell you how long what you have will last at the
rate you are getting through it.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, count_by, id_col,
                     money_cf, rank_desc, scale_cf, status_cf, sum_by,
                     yesno, zero)

NAME = "Materials Inventory"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Materials Inventory",
        subtitle="What is in the yard, what it cost, and what you are "
                 "about to run out of.",
        tab_color=Palette.accent,
        rows=cfg.row_count("materials"),
        samples=sample("materials", cfg),
        help_text=(
            "Add each material once with its unit, its cost and the "
            "level at which you want to be warned. Record purchases "
            "on the Expense Tracker against the Material ID and usage "
            "on the same tab - stock on hand follows automatically."),
        extra_notes=[
            "Stock on hand is opening stock plus purchases minus "
            "usage. If it is wrong, one of those three is wrong - "
            "fix the entry, not the number, or you lose the ability "
            "to trust any of it.",
            "Weeks of cover is based on what you have actually used "
            "in the last ninety days. In March it will look alarming "
            "and in November reassuring; read it with the season in "
            "mind.",
            "Charge-out price is what the customer pays per unit. It "
            "should be above cost - handling, collecting and "
            "carrying are real work and the markup on Settings is "
            "there to cover them.",
        ],
        columns=[
            id_col("name", "MaterialPrefix",
                   digits=cfg.digits("material"), header="Material ID",
                   note="Generated. Book purchases and usage against "
                        "it on the Expense Tracker."),
            Col("name", "Material", 26, "text",
                note="Start here. 'Hardwood mulch, bulk' is more use "
                     "than 'mulch'."),
            Col("category", "Category", 20, "text",
                validate=list_from("MaterialCategoryList")),
            Col("unit", "Unit", 14, "text",
                validate=list_from("MaterialUnitList"),
                note="Bag, yard, gallon, roll. Be consistent - half "
                     "the value of this tab is in the unit."),
            Col("supplier", "Supplier", 20, "text"),
            Col("supplier_code", "Their code", 14, "text",
                note="The code to quote when you ring up to order."),
            Col("cost_unit", "Cost per unit", 12, "money",
                validate=amount(0, 1000000),
                note="What you pay. Drives job costs and the "
                     "suggested charge-out price."),
            Col("charge_unit", "Charge per unit", 13, "money",
                validate=amount(0, 1000000,
                                "What the customer pays per unit. "
                                "Blank uses cost times the markup on "
                                "Settings."),
                note="Blank falls back to cost times the markup."),
            Col("charge_used", "Charged", 11, "money",
                formula=zero("name",
                             'IF({charge_unit}{r}>0,{charge_unit}{r},'
                             'ROUND({cost_unit}{r}*MaterialMarkup,2))'),
                hidden=True),
            Col("markup_pct", "Markup", 9, "percent",
                formula='=IF({name}{r}="","",'
                        'IF({cost_unit}{r}<=0,"",'
                        'ROUND({charge_used}{r}/'
                        '{cost_unit}{r}-1,4)))',
                cf=scale_cf()),
            Col("opening", "Opening stock", 12, "number1",
                validate=amount(0, 1000000,
                                "How much you had when you started "
                                "using this workbook."),
                note="Set once, when you start. After that the "
                     "purchases and usage do the work."),
            Col("reorder_at", "Reorder at", 11, "number1",
                validate=amount(0, 1000000),
                note="The level at which you want a warning. Set it "
                     "to a week's use plus whatever your supplier's "
                     "lead time is."),
            Col("reorder_qty", "Order quantity", 12, "number1",
                validate=amount(0, 1000000),
                note="How much you usually buy at once."),
            Col("location", "Kept at", 16, "text"),
            Col("status", "Status", 13, "text",
                validate=list_from("MaterialStatusList"),
                cf=status_cf()),
            Col("hazardous", "Hazardous", 10, "flag",
                validate=yesno("Does this need a safety data sheet or "
                               "a licence to apply?"),
                note="Fertiliser, herbicide and fuel all have rules. "
                     "Know which ones apply to you."),
            Col("expiry", "Use by", 11, "date",
                validate=date_check(),
                note="Seed and chemicals do go off."),
            Col("notes", "Notes", 26, "wrap"),

            # ---- stock, derived --------------------------------------
            Col("purchased", "Bought", 11, "number1",
                formula=zero("name", sum_by("Expense Tracker", "quantity",
                                            "material", '{id}{r}',
                                            "is_purchase", "1")),
                note="From the Expense Tracker, automatically."),
            Col("used", "Used", 11, "number1",
                formula=zero("name", sum_by("Expense Tracker", "quantity",
                                            "material", '{id}{r}',
                                            "is_usage", "1")),
                note="Booked out to jobs on the Expense Tracker."),
            Col("on_hand", "On hand", 11, "number1",
                formula=zero("name",
                             'ROUND({opening}{r}+{purchased}{r}-'
                             '{used}{r},2)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "formula",
                     "criteria": '=AND({name}{r}<>"",'
                                 '{on_hand}{r}<={reorder_at}{r})',
                     "fmt": "warn"}],
                note="Opening plus bought minus used. Calculated - you "
                     "cannot type over it, and that is deliberate."),
            Col("stock_value", "Stock value", 12, "money",
                formula=zero("name",
                             'ROUND(MAX(0,{on_hand}{r})*'
                             '{cost_unit}{r},2)'),
                cf=money_cf(),
                note="What is sitting in the yard, at cost."),
            Col("used_90", "Used (90 days)", 12, "number1",
                formula=zero("name",
                             'SUMIFS([[Expense Tracker.quantity]],'
                             '[[Expense Tracker.material]],{id}{r},'
                             '[[Expense Tracker.is_usage]],1,'
                             '[[Expense Tracker.date_num]],'
                             '">="&TodayDate-90)'),
                hidden=True),
            Col("weekly_use", "Used per week", 12, "number1",
                formula=zero("name",
                             'ROUND({used_90}{r}/13,2)'),
                note="Averaged over the last ninety days."),
            Col("weeks_cover", "Weeks of cover", 13, "number1",
                formula='=IF({name}{r}="","",'
                        'IF({weekly_use}{r}<=0,"",'
                        'ROUND(MAX(0,{on_hand}{r})/'
                        '{weekly_use}{r},1)))',
                cf=[{"type": "cell", "criteria": "<=", "value": 1,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": "<=", "value": 3,
                     "fmt": "warn"},
                    {"type": "cell", "criteria": ">=", "value": 20,
                     "fmt": "info"}],
                note="At the current rate. Blank means you have not "
                     "used any lately, so there is nothing to project."),
            Col("spend_total", "Spent to date", 12, "money",
                formula=zero("name", sum_by("Expense Tracker", "amount",
                                            "material", '{id}{r}',
                                            "is_purchase", "1")),
                cf=money_cf()),
            Col("times_bought", "Orders", 9, "int",
                formula=zero("name", count_by("Expense Tracker",
                                              "material", '{id}{r}',
                                              "is_purchase", "1"))),
            Col("last_buy_num", "Last bought #", 11, "number",
                formula=zero("name",
                             'SUMPRODUCT(MAX('
                             '([[Expense Tracker.material]]={id}{r})*'
                             '([[Expense Tracker.is_purchase]]=1)*'
                             '[[Expense Tracker.date_num]]))'),
                hidden=True),
            Col("last_bought", "Last bought", 11, "date",
                formula='=IF({name}{r}="","",'
                        'IF({last_buy_num}{r}<=0,"",'
                        '{last_buy_num}{r}))'),
            Col("is_low", "Low", 6, "int",
                formula=zero("name",
                             'IF(AND({status}{r}="Active",'
                             '{on_hand}{r}<={reorder_at}{r}),1,0)'),
                hidden=True,
                note="What the dashboard's low-material count reads."),
            Col("order_value", "Cost to restock", 13, "money",
                formula=zero("name",
                             'IF({is_low}{r}=0,0,'
                             'ROUND(MAX({reorder_qty}{r},'
                             '{reorder_at}{r}-{on_hand}{r})*'
                             '{cost_unit}{r},2))'),
                note="What it would cost to bring the low ones back "
                     "up. The shopping list, in money."),
            rank_desc("spend_total", guard='{name}{r}=""'),

            Col("alert", "What needs doing", 44, "wrap",
                formula=alert_chain("name", [
                    ('{on_hand}{r}<0',
                     "Urgent - stock has gone negative, a purchase is "
                     "missing"),
                    ('AND({status}{r}="Active",{on_hand}{r}<=0)',
                     "Out of stock - none left in the yard"),
                    ('AND({expiry}{r}<>"",{expiry}{r}<TodayDate,'
                     '{on_hand}{r}>0)',
                     "Expired - past its use-by date"),
                    ('{is_low}{r}=1',
                     "Reorder - at or below your reorder point"),
                    ('AND({weeks_cover}{r}<>"",{weeks_cover}{r}<=1)',
                     "Order - less than a week of cover left"),
                    ('{cost_unit}{r}=0',
                     "Add - no cost per unit, so job costs are "
                     "understated"),
                    ('AND({expiry}{r}<>"",'
                     '{expiry}{r}<TodayDate+60,{on_hand}{r}>0)',
                     "Due - use-by date within two months"),
                    ('{reorder_at}{r}=0',
                     "Add - no reorder point, so you will not be "
                     "warned"),
                    ('AND({hazardous}{r}="Yes",{notes}{r}="")',
                     "Check - hazardous with no handling note"),
                ]),
                cf=alert_cf()),
        ],
    )
