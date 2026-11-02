"""7. Quote Calculator - the tab people buy this workbook for.

Pick a property and a service and the price builds itself: lawn size
off the property, labour off the catalogue time, materials, equipment,
the round trip to site, overhead by the hour, then the margin you
asked for. Every line of that build is visible, because a quote you
cannot explain is a quote you cannot defend.

Mark a quote Accepted and the work order columns light up - that is
the hand-off into the Job & Work Orders tab.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, customer_col,
                     date_num_col, id_col, is_live_quote, is_won_quote,
                     lookup_customer, lookup_property, lookup_property_num,
                     lookup_service, lookup_service_num, loss_cf, margin,
                     money_cf, month_col, pick, property_col,
                     service_col, service_tax, status_cf, zero)

NAME = "Quote Calculator"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Quote Calculator",
        subtitle="Lawn size, labour, materials, equipment, travel and "
                 "the margin you want - priced in one row.",
        tab_color=Palette.accent,
        rows=cfg.row_count("quotes"),
        samples=sample("quotes", cfg),
        freeze_cols=3,
        help_text=(
            "Pick the customer, the property and the service. The lawn "
            "area and the drive come from the Property Database, the "
            "time and the materials from the Service Catalog, and the "
            "rates from Settings. Then look at the margin column and "
            "decide whether you are happy. Override any white cell - "
            "the shaded ones work themselves out."),
        extra_notes=[
            "The quote is built cost-up, not price-down: your cost is "
            "worked out first and the margin is added to it. That is "
            "why it can tell you when a price you had in mind is one "
            "you cannot afford.",
            "Travel is charged on the round trip, both ways, because "
            "that is how long the truck is away from anything else.",
            "Accepted quotes are the ones the job register expects to "
            "see. Set the status, write the Job ID you create against "
            "it, and the two tabs stay tied together.",
            "A quote expires on its own after the number of days set "
            "on Settings. An expired quote is a reason to call, not a "
            "reason to delete the row.",
        ],
        columns=[
            id_col("date", "QuotePrefix", digits=cfg.digits("quote"),
                   header="Quote ID",
                   note="Generated. Put this number on the paperwork "
                        "you send out."),
            Col("date", "Quote date", 12, "date",
                validate=date_check(),
                note="Start here. Everything else on the row unlocks "
                     "once there is a date."),
            customer_col(),
            Col("customer_name", "Customer name", 22, "text",
                formula=lookup_customer("name")),
            property_col(),
            Col("address", "Address", 28, "text",
                formula=lookup_property("address")),
            service_col(),
            Col("description", "What is included", 34, "wrap",
                formula='=IF({service}{r}="","",'
                        'IFERROR(INDEX([[Service Catalog.description]],'
                        'MATCH({service}{r},'
                        '[[Service Catalog.name]],0))&"",""))',
                note="Pulled from the catalogue so the quote says the "
                     "same thing every time. Overwrite it on the "
                     "printable if one job is different."),
            Col("frequency", "Frequency", 15, "text",
                validate=pick("FrequencyList",
                              "One-off, or how often it repeats if this "
                              "is a maintenance quote."),
                note="A recurring quote is worth its annual value, not "
                     "its visit value. The column on the right shows "
                     "both."),

            # ---- what the site tells us ------------------------------
            Col("area", "Lawn area", 11, "int",
                formula=lookup_property_num("lawn_area"),
                note="From the Property Database. Measure it there, "
                     "once."),
            Col("difficulty", "Difficulty", 10, "number1",
                formula='=IF({property}{r}="","",'
                        'IFERROR(INDEX([[Property Database.difficulty]],'
                        'MATCH({property}{r},'
                        '[[Property Database.id]],0))*1,1))',
                note="Slope, access, obstacles and the dog, from the "
                     "property record."),
            Col("miles", "Miles each way", 12, "number1",
                formula=lookup_property_num("miles")),

            # ---- the build -------------------------------------------
            Col("cat_minutes", "Catalogue mins", 12, "int",
                formula=lookup_service_num("minutes"),
                hidden=True),
            Col("cat_unit", "Unit", 14, "text",
                formula=lookup_service("unit", missing=""),
                hidden=True),
            Col("cat_crew", "Catalogue crew", 11, "int",
                formula=lookup_service_num("crew_size"),
                hidden=True),
            Col("units", "Units", 10, "number1",
                formula=zero("service",
                             'IF({cat_unit}{r}="Per 1,000 sq ft",'
                             'MAX(1,{area}{r})/1000,'
                             'IF({cat_unit}{r}="Per 100 sq ft",'
                             'MAX(1,{area}{r})/100,'
                             'IF({cat_unit}{r}="Per sq ft",'
                             'MAX(1,{area}{r}),1)))'),
                note="How many units of the catalogue price this site "
                     "needs. For a per-visit service it is simply 1."),
            Col("est_minutes", "Est. minutes", 11, "int",
                formula=zero("service",
                             'ROUND({cat_minutes}{r}*{units}{r}*'
                             'MAX(1,{difficulty}{r}),0)'),
                note="Catalogue time, scaled for the size of this lawn "
                     "and how awkward it is."),
            Col("crew_size", "Crew", 8, "int",
                validate=amount(1, 20, "How many people are going?",
                                decimal=False),
                note="Override the catalogue if you are sending a "
                     "different number of people."),
            Col("crew_used", "Crew used", 9, "int",
                formula=zero("service",
                             'IF({crew_size}{r}>0,{crew_size}{r},'
                             'MAX(1,{cat_crew}{r}))'),
                hidden=True),
            Col("site_hours", "Hours on site", 11, "number1",
                formula=zero("service",
                             'ROUND({est_minutes}{r}/60/'
                             'MAX(1,{crew_used}{r}),2)'),
                note="How long the visit takes with that many people on "
                     "it. Two people halve the clock, not the cost."),
            Col("drive_hours", "Drive hours", 10, "number1",
                formula=zero("service",
                             'ROUND(2*IFERROR(INDEX('
                             '[[Property Database.drive_minutes]],'
                             'MATCH({property}{r},'
                             '[[Property Database.id]],0))*1,'
                             'DriveMinutes)/60*{crew_used}{r},2)'),
                note="Round trip, times the crew, because they are all "
                     "in the truck and all being paid."),
            Col("labour_hours", "Crew hours", 10, "number1",
                formula=zero("service",
                             'ROUND({site_hours}{r}*{crew_used}{r}+'
                             '{drive_hours}{r},2)'),
                note="Total paid hours this quote has to cover."),
            Col("labour_cost", "Labour cost", 11, "money",
                formula=zero("service",
                             'ROUND({labour_hours}{r}*LabourRate,2)'),
                note="At your loaded crew rate from Settings - wages "
                     "plus tax plus insurance, not the take-home."),
            Col("materials_cost", "Materials", 11, "money",
                validate=amount(0, 1000000,
                                "Leave blank to use the catalogue "
                                "figure for this service."),
                note="Your cost, not the customer's price. The markup "
                     "is added below."),
            Col("materials_used", "Materials used", 12, "money",
                formula=zero("service",
                             'IF({materials_cost}{r}>0,'
                             '{materials_cost}{r},'
                             'ROUND(IFERROR(INDEX('
                             '[[Service Catalog.materials_cost]],'
                             'MATCH({service}{r},'
                             '[[Service Catalog.name]],0))*1,0)*'
                             '{units}{r},2))'),
                hidden=True),
            Col("materials_charge", "Materials charged", 13, "money",
                formula=zero("service",
                             'ROUND({materials_used}{r}*'
                             'MaterialMarkup,2)'),
                note="Cost times the markup on Settings. Handling, "
                     "collecting and carrying are real work."),
            Col("equipment_cost", "Equipment", 10, "money",
                validate=amount(0, 1000000,
                                "Hire, blades, fuel for the day, or a "
                                "share of what the machine costs to "
                                "own."),
                note="Anything this job needs that the hourly rate does "
                     "not already cover."),
            Col("travel_cost", "Travel", 10, "money",
                formula=zero("service",
                             'ROUND(2*{miles}{r}*TravelRate,2)'),
                note="Round trip at the mileage rate on Settings. Fuel, "
                     "tyres and the share of the truck."),
            Col("disposal_cost", "Disposal", 10, "money",
                validate=amount(0, 1000000,
                                "Tip fees, green waste, skip hire."),
                note="Taking it away is never free. Charge it."),
            Col("overhead_cost", "Overhead", 10, "money",
                formula=zero("service",
                             'ROUND({labour_hours}{r}*OverheadRate,2)'),
                note="The yard, the van insurance, the phone and the "
                     "evenings doing paperwork, per crew hour."),
            Col("total_cost", "Cost to you", 12, "money",
                formula=zero("service",
                             'ROUND({labour_cost}{r}+'
                             '{materials_used}{r}+{equipment_cost}{r}+'
                             '{travel_cost}{r}+{disposal_cost}{r}+'
                             '{overhead_cost}{r},2)'),
                note="What this visit actually costs you, before a "
                     "penny of profit."),

            # ---- the price -------------------------------------------
            Col("target_margin", "Margin wanted", 11, "percent0",
                validate=amount(0, 0.95,
                                "The profit margin you want on this "
                                "job. Blank uses the target on "
                                "Settings."),
                note="Your number, job by job. A difficult customer or "
                     "a tight season is a reason to change it."),
            Col("margin_used", "Margin used", 10, "percent0",
                formula=zero("service",
                             'IF({target_margin}{r}>0,'
                             '{target_margin}{r},TargetMargin)'),
                hidden=True),
            Col("calc_price", "Calculated price", 13, "money",
                formula=zero("service",
                             'ROUND(MAX(MinimumVisit,'
                             '({total_cost}{r}-{materials_used}{r}+'
                             '{materials_charge}{r})/'
                             'MAX(0.05,1-{margin_used}{r})),2)'),
                cf=money_cf(),
                note="Cost plus the margin you asked for, with the "
                     "minimum visit charge as a floor. This is the "
                     "suggestion."),
            Col("discount", "Discount", 10, "money",
                validate=amount(0, 1000000,
                                "Any reduction you are offering - a "
                                "neighbour deal, a first-visit offer."),
                note="Record it rather than quietly lowering the price, "
                     "so you can see what discounting costs you."),
            Col("quoted_price", "Your price", 12, "money",
                validate=amount(0, 1000000,
                                "What you are actually quoting. Blank "
                                "uses the calculated price."),
                note="Override whenever you like. The margin column "
                     "tells you immediately what the override did."),
            Col("price_used", "Price", 11, "money",
                formula=zero("service",
                             'ROUND(IF({quoted_price}{r}>0,'
                             '{quoted_price}{r},{calc_price}{r})-'
                             '{discount}{r},2)'),
                hidden=True),
            Col("tax", "Tax", 10, "money",
                formula=zero("service", service_tax('{price_used}{r}')),
                note="Only if you have switched tax on, on Settings. "
                     "Whether mowing is taxable where you trade is a "
                     "question for your accountant."),
            Col("total", "Total quoted", 12, "money",
                formula=zero("date",
                             'ROUND({price_used}{r}+{tax}{r},2)'),
                cf=money_cf(),
                note="What goes on the paperwork."),
            Col("profit", "Profit", 11, "money",
                formula=zero("service",
                             'ROUND({price_used}{r}-{total_cost}{r},2)'),
                cf=loss_cf()),
            Col("margin_pct", "Margin", 9, "percent",
                formula='=IF({service}{r}="","",'
                        f'{margin("{profit}{r}", "{price_used}{r}")})',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=TargetMargin", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=MinMargin", "fmt": "bold_bad"},
                    {"type": "cell", "criteria": "<",
                     "value": "=TargetMargin", "fmt": "warn"}],
                note="The number to look at before you press send."),
            Col("per_hour", "Earns per hour", 12, "money",
                formula='=IF({service}{r}="","",'
                        'IF({labour_hours}{r}<=0,"",'
                        'ROUND({price_used}{r}/'
                        '{labour_hours}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}]),
            Col("visits_year", "Visits / year", 11, "int",
                formula=zero("service",
                             'IFERROR(INDEX(VisitsPerYear,'
                             'MATCH({frequency}{r},FrequencyList,0))*1,'
                             '0)'),
                hidden=True),
            Col("annual_value", "Annual value", 12, "money",
                formula=zero("service",
                             'ROUND({total}{r}*{visits_year}{r},2)'),
                cf=money_cf(),
                note="What a recurring quote is really worth over a "
                     "year. A one-off shows zero - that is the point."),

            # ---- where it went ---------------------------------------
            Col("status", "Status", 14, "text",
                validate=list_from("QuoteStatusList"),
                cf=status_cf(),
                note="Accepted is the one that matters - it is the "
                     "signal to raise a work order."),
            Col("sent_date", "Sent", 11, "date",
                validate=date_check()),
            Col("decision_date", "Answered", 11, "date",
                validate=date_check()),
            Col("valid_until", "Valid until", 11, "date",
                formula='=IF({date}{r}="","",'
                        '{date}{r}+QuoteValidDays)',
                note="Automatic, from the date and the validity period "
                     "on Settings."),
            Col("days_out", "Days waiting", 11, "int",
                formula=zero("date",
                             'IF({sent_date}{r}="",0,'
                             'IF({decision_date}{r}<>"",'
                             '{decision_date}{r}-{sent_date}{r},'
                             'TodayDate-{sent_date}{r}))'),
                cf=[{"type": "cell", "criteria": ">=", "value": 14,
                     "fmt": "warn"}]),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the work order this quote turned "
                              "into."),
                note="Once you have raised the work order, write its "
                     "Job ID here. That is the thread from quote to "
                     "job to invoice."),
            Col("contract", "Contract ID", 11, "id",
                validate=pick("ContractIDList",
                              "Pick the agreement this quote became."),
                note="If the quote turned into a recurring agreement, "
                     "put the Contract ID here instead."),
            Col("lost_reason", "If lost, why", 24, "text",
                note="Price, timing, went elsewhere, never replied. Six "
                     "months of this column is worth more than any "
                     "advice about pricing."),
            Col("notes", "Notes", 30, "wrap"),

            Col("is_won", "Won", 6, "int",
                formula=zero("date", f'IF({is_won_quote("{status}{r}")},'
                                     '1,0)'),
                hidden=True),
            Col("is_live", "Live", 6, "int",
                formula=zero("date", f'IF({is_live_quote("{status}{r}")},'
                                     '1,0)'),
                hidden=True),
            Col("is_expired", "Expired", 7, "int",
                formula=zero("date",
                             'IF(AND({is_live}{r}=1,'
                             '{valid_until}{r}<TodayDate),1,0)'),
                hidden=True),
            date_num_col("date", "date_num"),
            month_col("date"),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("date", [
                    ('AND({is_won}{r}=1,{job}{r}="",{contract}{r}="")',
                     "Action - accepted but no work order raised yet"),
                    ('{margin_pct}{r}<0',
                     "Loss - this price is below what the job costs"),
                    ('AND({margin_pct}{r}<>"",'
                     '{margin_pct}{r}<MinMargin,{is_live}{r}=1)',
                     "Urgent - margin under your floor, reprice before "
                     "sending"),
                    ('{is_expired}{r}=1',
                     "Expired - past its validity date, call them"),
                    ('AND({is_live}{r}=1,{sent_date}{r}="")',
                     "Send - quote prepared but never sent"),
                    ('AND({is_live}{r}=1,{days_out}{r}>=ChaseQuoteDays)',
                     "Chase - no answer since you sent it"),
                    ('AND({status}{r}="Declined",{lost_reason}{r}="")',
                     "Add - lost, and no reason recorded"),
                    ('{area}{r}=0',
                     "Check - no lawn area on the property record"),
                    ('AND({margin_pct}{r}<>"",'
                     '{margin_pct}{r}<TargetMargin)',
                     "Thin margin - under target, but above your floor"),
                    ('{is_live}{r}=1', "Quoted - waiting on an answer"),
                ]),
                cf=alert_cf()),
        ],
    )
