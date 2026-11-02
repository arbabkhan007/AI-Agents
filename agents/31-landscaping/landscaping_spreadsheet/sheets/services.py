"""6. Service Catalog - your price list, and what each job really costs.

Thirty services come filled in with a rate, a unit and a realistic
time. Change every one of them: these are plausible numbers for a
two-person crew in a mid-cost area, not a recommendation. What the
sheet is really for is the column on the right - the margin each
service earns once the crew, the materials and the overhead are paid.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from
from .common import (alert_cf, alert_chain, amount, count_by, loss_cf, margin,
                     money_cf, rank_desc, scale_cf, status_cf, sum_by,
                     yesno, zero)

NAME = "Service Catalog"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Service Catalog",
        subtitle="What you sell, what you charge for it, how long it "
                 "takes and what it leaves you with.",
        tab_color=Palette.primary,
        rows=cfg.row_count("services"),
        samples=sample("services", cfg),
        help_text=(
            "The service name is the join key - the quote calculator, "
            "the job register and the contracts all pick from this "
            "list, so renaming a service here renames it everywhere "
            "that has not been written yet, but NOT on rows already "
            "recorded. Add a new line instead of renaming an old one "
            "once you are trading."),
        extra_notes=[
            "'Unit' decides how the quote calculator reads the rate. "
            "Per 1,000 sq ft multiplies by the lawn area; per visit, "
            "per hour and per job do not.",
            "Minutes per unit is your own measured time, and it is the "
            "number that makes a quote honest. If the catalogue says "
            "35 minutes and the timesheets say 50, change the "
            "catalogue.",
            "Margin here is before overhead; the quote calculator adds "
            "overhead per crew hour on top. A service showing 55% here "
            "is nearer 35% once the yard, the insurance and the "
            "paperwork are paid for.",
        ],
        columns=[
            Col("name", "Service", 30, "text",
                note="The name your customers see on the quote. This is "
                     "the join key - keep it short and keep it stable."),
            Col("category", "Category", 18, "text",
                validate=list_from("ServiceCategoryList")),
            Col("description", "What it includes", 40, "wrap",
                note="Worth writing properly: this is what stops the "
                     "'I thought that included the hedges' conversation."),
            Col("unit", "Priced per", 17, "text",
                validate=list_from("PricingUnitList"),
                note="How the rate is read. 'Per 1,000 sq ft' multiplies "
                     "by the lawn area; 'Per visit' does not."),
            Col("rate", "Your rate", 11, "money",
                validate=amount(0, 100000),
                note="What you charge for one unit. Every price in the "
                     "workbook starts here."),
            Col("minutes", "Minutes per unit", 13, "int",
                validate=amount(0, 10000),
                note="Your own measured time for one unit of this "
                     "service, for one person."),
            Col("crew_size", "Crew needed", 11, "int",
                validate=amount(1, 20),
                note="How many people it takes. Two people for 30 "
                     "minutes is one crew hour, not half of one."),
            Col("materials_cost", "Materials per unit", 14, "money",
                validate=amount(0, 100000),
                note="Fertiliser, mulch, seed, bags. Leave at 0 for "
                     "pure labour services like mowing."),
            Col("equipment", "Main equipment", 20, "text",
                validate=list_from("EquipmentCategoryList"),
                note="What has to be on the trailer. Useful when a "
                     "machine goes in for repair and you need to know "
                     "which jobs are affected."),
            Col("min_charge", "Minimum charge", 12, "money",
                validate=amount(0, 100000),
                note="The least you will turn out for. Blank uses the "
                     "minimum visit charge on Settings."),
            Col("season", "Main season", 15, "text",
                validate=list_from("SeasonList"),
                note="When this sells. Drives the seasonal planner."),
            Col("frequency", "Usual frequency", 16, "text",
                validate=list_from("FrequencyList"),
                note="How often a customer typically buys it."),
            Col("taxable", "Taxable", 9, "flag",
                validate=yesno("Is this service subject to sales tax or "
                               "VAT where you trade?"),
                note="Rules differ by state and country, and mowing is "
                     "not always treated the same as landscaping. Ask "
                     "your accountant, then set this."),
            Col("skill", "Skill needed", 16, "text",
                validate=list_from("CrewRoleList"),
                note="Who on the crew can actually do it. Pesticide work "
                     "needs the licence."),
            Col("licence_needed", "Licence needed", 12, "flag",
                validate=yesno("Does this service require a pesticide or "
                               "trade licence?"),
                note="If Yes, only licensed crew should be assigned."),
            Col("status", "Status", 12, "text",
                validate=list_from("ServiceStatusList"),
                cf=status_cf()),
            Col("notes", "Notes", 30, "wrap"),

            # ---- the economics ---------------------------------------
            Col("hours_per_unit", "Crew hours", 10, "number1",
                formula=zero("name",
                             'ROUND({minutes}{r}*MAX(1,{crew_size}{r})'
                             '/60,2)'),
                note="Minutes times the number of people, in hours. This "
                     "is what the labour actually costs you."),
            Col("labour_cost", "Labour cost", 11, "money",
                formula=zero("name",
                             'ROUND({hours_per_unit}{r}*LabourRate,2)'),
                note="At the crew rate on Settings. Set a real loaded "
                     "rate there - wage plus tax plus insurance."),
            Col("overhead_cost", "Overhead", 10, "money",
                formula=zero("name",
                             'ROUND({hours_per_unit}{r}*OverheadRate,2)'),
                note="The yard, the insurance and the office, charged "
                     "by the crew hour."),
            Col("total_cost", "Cost per unit", 12, "money",
                formula=zero("name",
                             'ROUND({labour_cost}{r}+{materials_cost}{r}'
                             '+{overhead_cost}{r},2)'),
                note="Everything except the drive, which depends on the "
                     "property."),
            Col("profit_unit", "Profit per unit", 13, "money",
                formula=zero("name",
                             'ROUND({rate}{r}-{total_cost}{r},2)'),
                cf=loss_cf()),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({name}{r}="","",'
                        f'{margin("{profit_unit}{r}", "{rate}{r}")})',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=TargetMargin", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=MinMargin", "fmt": "bad"},
                    {"type": "cell", "criteria": "<",
                     "value": "=TargetMargin", "fmt": "warn"}],
                note="Green at or above your target, red below your "
                     "floor. Both are set on Settings."),
            Col("per_hour", "Earns per hour", 12, "money",
                formula='=IF({name}{r}="","",'
                        'IF({hours_per_unit}{r}<=0,"",'
                        'ROUND({rate}{r}/'
                        '{hours_per_unit}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}],
                note="The one number to compare services on. A service "
                     "earning below your charge-out rate is underpriced, "
                     "however good the margin looks."),
            Col("suggested", "Suggested rate", 13, "money",
                formula=zero("name",
                             'ROUND({total_cost}{r}/'
                             'MAX(0.05,1-TargetMargin),2)'),
                note="What this rate would have to be to hit your target "
                     "margin. A suggestion, not a price - the market has "
                     "a vote."),
            Col("gap", "Rate gap", 10, "money",
                formula=zero("name",
                             'ROUND({rate}{r}-{suggested}{r},2)'),
                cf=loss_cf(),
                note="Negative means you are charging less than your own "
                     "target says you should."),

            # ---- how it is selling -----------------------------------
            Col("times_sold", "Visits done", 11, "int",
                formula=zero("name", count_by("Job & Work Orders",
                                              "service", '{name}{r}',
                                              "is_done", "1")),
                cf=scale_cf()),
            Col("revenue", "Revenue", 12, "money",
                formula=zero("name", sum_by("Job & Work Orders", "charge",
                                            "service", '{name}{r}',
                                            "is_done", "1")),
                cf=money_cf()),
            Col("quoted", "Times quoted", 11, "int",
                formula=zero("name", count_by("Quote Calculator",
                                              "service", '{name}{r}'))),
            Col("won", "Quotes won", 10, "int",
                formula=zero("name", count_by("Quote Calculator",
                                              "service", '{name}{r}',
                                              "is_won", "1"))),
            Col("win_rate", "Win rate", 9, "percent",
                formula='=IF({name}{r}="","",'
                        'IF({quoted}{r}<=0,"",'
                        'ROUND({won}{r}/{quoted}{r},4)))',
                cf=scale_cf(),
                note="Winning everything usually means the price is too "
                     "low, not that the selling is good."),
            Col("avg_actual", "Actual hours avg", 13, "number1",
                formula='=IF({name}{r}="","",'
                        'IFERROR(AVERAGEIFS('
                        '[[Job & Work Orders.hours_actual]],'
                        '[[Job & Work Orders.service]],{name}{r},'
                        '[[Job & Work Orders.is_done]],1,'
                        '[[Job & Work Orders.hours_actual]],">0"),""))',
                note="What this service really takes, from the "
                     "timesheets. The reality check on the estimate."),
            Col("contracts", "On contract", 10, "int",
                formula=zero("name", count_by("Recurring Contracts",
                                              "service", '{name}{r}',
                                              "is_live", "1"))),
            Col("is_active", "Active", 7, "int",
                formula=zero("name", 'IF({status}{r}="Active",1,0)'),
                hidden=True),
            rank_desc("revenue", guard='{name}{r}=""'),

            Col("alert", "What needs doing", 44, "wrap",
                formula=alert_chain("name", [
                    ('{rate}{r}=0', "Add - no rate set for this service"),
                    ('{minutes}{r}=0',
                     "Add - no time set, so it cannot be scheduled "
                     "honestly"),
                    ('{profit_unit}{r}<0',
                     "Loss - this service costs more than it charges"),
                    ('AND({margin_pct}{r}<>"",{margin_pct}{r}<MinMargin)',
                     "Urgent - margin is below your floor, reprice it"),
                    ('AND({avg_actual}{r}<>"",{hours_per_unit}{r}>0,'
                     '{avg_actual}{r}>{hours_per_unit}{r}*1.25)',
                     "Check - it really takes longer than the catalogue "
                     "says"),
                    ('AND({quoted}{r}>=5,{win_rate}{r}<>"",'
                     '{win_rate}{r}<0.2)',
                     "Check - rarely accepted, the price may be too "
                     "high"),
                    ('AND({quoted}{r}>=5,{win_rate}{r}<>"",'
                     '{win_rate}{r}>0.9)',
                     "Action - you win nearly every one, test a higher "
                     "price"),
                    ('AND({margin_pct}{r}<>"",'
                     '{margin_pct}{r}<TargetMargin)',
                     "Thin margin - under your target, review the rate"),
                    ('AND({is_active}{r}=1,{times_sold}{r}=0,'
                     '{quoted}{r}=0)',
                     "Action - never sold or quoted, is it worth "
                     "offering?"),
                    ('{description}{r}=""',
                     "Add - no description, so the quote is vague"),
                ]),
                cf=alert_cf()),
        ],
    )
