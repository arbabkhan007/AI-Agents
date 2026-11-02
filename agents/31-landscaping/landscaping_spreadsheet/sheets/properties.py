"""5. Property Database - the ground you actually work on.

A customer is a person who pays; a property is a place with a gate
code, a slope, a dog and a lawn of a particular size. The two are
separate because one customer can own six of them, and because every
price in this workbook is driven by what is written here: lawn area,
terrain, access and how far it is from the yard.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, count_by, customer_col,
                     id_col,
                     lookup_customer, money_cf,
                     rank_desc, scale_cf, status_cf, sum_by, yesno, zero)

NAME = "Property Database"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Property Database",
        subtitle="Every address you maintain: the size of the lawn, how "
                 "to get in, what is in the way, and how far it is.",
        tab_color=Palette.primary,
        rows=cfg.row_count("properties"),
        samples=sample("properties", cfg),
        help_text=(
            "Pick the customer first, then describe the site. Lawn area "
            "is the single most useful number in the workbook - the "
            "quote calculator, the time estimate and the material "
            "quantities all come off it. Pace it out once and you never "
            "have to guess at that address again."),
        extra_notes=[
            "Measure the area you actually cut, not the plot size. A "
            "quarter acre plot with a house, a drive and a patio on it "
            "is rarely more than 6,000 sq ft of grass.",
            "Gate codes and alarm codes are sensitive. If this file is "
            "shared or stored in the cloud, leave those boxes empty and "
            "keep them somewhere your crew can reach and nobody else "
            "can.",
            "Difficulty multiplier is how this sheet earns its keep: a "
            "steep, tight, dog-occupied garden takes longer than a flat "
            "open one and should be priced accordingly.",
        ],
        columns=[
            id_col("address", "PropertyPrefix",
                   digits=cfg.digits("property"), header="Property ID",
                   note="Generated. Jobs, quotes and contracts point at "
                        "this ID, not at the address text."),
            customer_col(note="Who pays for work at this address. Add "
                              "them on the Customer CRM tab first."),
            Col("customer_name", "Customer name", 22, "text",
                formula=lookup_customer("name"),
                note="Automatic. 'Not in Customer CRM' means the ID is "
                     "wrong."),
            Col("nickname", "Site name", 18, "text",
                note="What the crew calls it: 'the big one on Mill "
                     "Lane', 'Harper rear'. Optional but they will "
                     "thank you."),
            Col("address", "Address", 30, "wrap",
                note="Start typing here. The Property ID appears as "
                     "soon as you do."),
            Col("town", "Town / city", 16, "text"),
            Col("postcode", "Zip / postcode", 12, "text"),
            Col("type", "Property type", 18, "text",
                validate=list_from("PropertyTypeList")),
            Col("lawn_area", "Lawn area (sq ft)", 14, "int",
                validate=amount(
                    0, 2000000,
                    "Roughly how much grass do you cut here, in square "
                    "feet? An average suburban back lawn is 2,000 to "
                    "6,000."),
                note="The number everything is priced from. Measure once, "
                     "properly, and the quote calculator does the rest."),
            Col("beds_area", "Beds / borders (sq ft)", 15, "int",
                validate=amount(0, 2000000),
                note="Planted area. Drives mulch and weeding quantities."),
            Col("hedge_length", "Hedge (linear ft)", 13, "int",
                validate=amount(0, 100000)),
            Col("terrain", "Terrain", 16, "text",
                validate=list_from("TerrainList"),
                note="Flat and open cuts faster than steep and awkward. "
                     "This feeds the difficulty multiplier."),
            Col("access", "Access", 20, "text",
                validate=list_from("AccessList"),
                note="How the mower gets in. A narrow side gate means "
                     "the ride-on stays on the trailer."),
            Col("gate_code", "Gate / alarm code", 14, "text",
                note="Leave empty if this file is shared. Recording a "
                     "code here is a choice, not a requirement."),
            Col("dog", "Dog on site", 10, "flag",
                validate=yesno("Is there a dog that may be loose in the "
                               "garden?"),
                note="The crew needs to know before they open the gate."),
            Col("pets_note", "Site hazards", 26, "wrap",
                note="Ponds, septic lids, irrigation heads, a bad step, "
                     "the neighbour's cat. Anything that costs money if "
                     "it gets hit."),
            Col("parking", "Parking", 18, "text",
                note="Where the truck and trailer actually fit."),
            Col("water", "Water on site", 10, "flag",
                validate=yesno()),
            Col("power", "Power on site", 10, "flag",
                validate=yesno()),
            Col("disposal", "Clippings", 16, "text",
                note="Leave on site, bag them, or take them away. Taking "
                     "them away is a cost - price it."),
            Col("miles", "Miles from yard", 12, "number1",
                validate=amount(0, 2000,
                                      "One way distance from your yard "
                                      "or depot."),
                note="One way. The quote calculator charges the round "
                     "trip at the rate on Settings."),
            Col("drive_minutes", "Drive (mins)", 11, "int",
                validate=amount(0, 600),
                note="One way, in normal traffic. Blank uses the default "
                     "on Settings."),
            Col("difficulty", "Difficulty", 10, "number1",
                formula=zero("address",
                             'ROUND(1'
                             '+IF({terrain}{r}="Steep slope",0.25,'
                             'IF({terrain}{r}="Gentle slope",0.1,'
                             'IF({terrain}{r}="Terraced",0.2,'
                             'IF({terrain}{r}="Rough / uneven",0.15,'
                             'IF({terrain}{r}="Wet / boggy",0.15,0)))))'
                             '+IF({access}{r}="Narrow side gate",0.15,'
                             'IF({access}{r}="Rear access only",0.1,'
                             'IF({access}{r}="Locked gate - code needed",'
                             '0.05,IF({access}{r}="Steps only",0.2,0))))'
                             '+IF({obstacles}{r}>=8,0.15,'
                             'IF({obstacles}{r}>=4,0.08,0))'
                             '+IF({dog}{r}="Yes",0.05,0),2)'),
                cf=scale_cf(),
                note="Worked out from terrain, access, obstacles and the "
                     "dog. 1.00 is an easy flat lawn; 1.50 takes half as "
                     "long again. The quote calculator multiplies by it."),
            Col("obstacles", "Trees / obstacles", 12, "int",
                validate=amount(0, 500,
                                      "Roughly how many things do you "
                                      "have to mow around?"),
                note="Trees, beds, play equipment, washing poles. Every "
                     "one of them is a turn."),
            Col("mowing_minutes", "Mow time (mins)", 12, "int",
                formula=zero("address",
                             'ROUND(MAX(10,{lawn_area}{r}/1000*'
                             'MowMinutesPer1000)*{difficulty}{r},0)'),
                note="An estimate from area and difficulty, for planning. "
                     "Actual times come from the timesheets."),
            Col("status", "Status", 13, "text",
                validate=list_from("PropertyStatusList"),
                cf=status_cf()),
            Col("start_date", "Maintained since", 14, "date",
                validate=date_check()),
            Col("photo_before", "Photo - before", 22, "link",
                note="Paste a link to the photo in your cloud drive. The "
                     "workbook stores the link, not the picture."),
            Col("photo_after", "Photo - after", 22, "link",
                note="The pair of them is the best sales tool you own."),
            Col("map_link", "Map link", 22, "link",
                note="A link to this address in your map app, for the "
                     "crew. The workbook does not navigate."),
            Col("notes", "Site notes", 34, "wrap",
                note="'Cut the verge too', 'nobody home on Fridays', "
                     "'bins out Tuesday so park on the road'."),

            # ---- what happens here -----------------------------------
            Col("jobs_done", "Visits done", 11, "int",
                formula=zero("address", count_by("Job & Work Orders",
                                                 "property", '{id}{r}',
                                                 "is_done", "1")),
                cf=scale_cf()),
            Col("jobs_open", "Visits booked", 12, "int",
                formula=zero("address", count_by("Job & Work Orders",
                                                 "property", '{id}{r}',
                                                 "is_open", "1"))),
            Col("revenue", "Revenue", 12, "money",
                formula=zero("address", sum_by("Job & Work Orders",
                                               "charge", "property",
                                               '{id}{r}', "is_done", "1")),
                cf=money_cf()),
            Col("cost", "Cost", 12, "money",
                formula=zero("address", sum_by("Job & Work Orders", "cost",
                                               "property", '{id}{r}',
                                               "is_done", "1"))),
            Col("profit", "Profit", 12, "money",
                formula=zero("address",
                             'ROUND({revenue}{r}-{cost}{r},2)'),
                cf=[{"type": "cell", "criteria": "<", "value": 0,
                     "fmt": "bold_bad"},
                    {"type": "cell", "criteria": ">", "value": 0,
                     "fmt": "good"}]),
            Col("hours_actual", "Hours booked", 11, "number1",
                formula=zero("address", sum_by("Job & Work Orders",
                                               "hours_actual", "property",
                                               '{id}{r}', "is_done", "1")),
                note="From the timesheets, via the jobs. Compare with "
                     "the mow time estimate - if they disagree, the "
                     "estimate is wrong."),
            Col("per_hour", "Earned per hour", 13, "money",
                formula='=IF({address}{r}="","",'
                        'IF({hours_actual}{r}<=0,"",'
                        'ROUND({revenue}{r}/'
                        '{hours_actual}{r},2)))',
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=ChargeRate", "fmt": "good"},
                    {"type": "cell", "criteria": "<",
                     "value": "=ChargeRate", "fmt": "warn"}],
                note="The honest test of a price. Below your charge-out "
                     "rate means this address is subsidised by the rest."),
            Col("contracts", "On contract", 10, "int",
                formula=zero("address", count_by("Recurring Contracts",
                                                 "property", '{id}{r}',
                                                 "is_live", "1"))),
            Col("last_num", "Last visit #", 11, "number",
                formula=zero("address",
                             'SUMPRODUCT(MAX('
                             '([[Job & Work Orders.property]]={id}{r})*'
                             '([[Job & Work Orders.is_done]]=1)*'
                             '[[Job & Work Orders.date_num]]))'),
                hidden=True),
            Col("last_visit", "Last visit", 12, "date",
                formula='=IF({address}{r}="","",'
                        'IF({last_num}{r}<=0,"",{last_num}{r}))'),
            Col("next_num", "Next visit #", 11, "number",
                formula=zero("address",
                             'IF(COUNTIFS('
                             '[[Job & Work Orders.property]],{id}{r},'
                             '[[Job & Work Orders.is_open]],1)=0,0,'
                             'SUMPRODUCT(MIN(IF('
                             '([[Job & Work Orders.property]]={id}{r})*'
                             '([[Job & Work Orders.is_open]]=1)=1,'
                             '[[Job & Work Orders.date_num]],99999))))'),
                hidden=True),
            Col("next_visit", "Next visit", 12, "date",
                formula='=IF({address}{r}="","",'
                        'IF({next_num}{r}<=0,"",'
                        'IF({next_num}{r}>=99999,"",'
                        '{next_num}{r})))',
                note="The earliest booked visit still outstanding."),
            Col("days_since", "Days since", 10, "int",
                formula=zero("address",
                             'IF({last_num}{r}<=0,0,'
                             'TodayDate-{last_num}{r})'),
                cf=[{"type": "cell", "criteria": ">=",
                     "value": "=DormantDays", "fmt": "bad"}]),
            Col("is_active", "Active", 7, "int",
                formula=zero("address",
                             'IF({status}{r}="Active",1,0)'),
                hidden=True),
            rank_desc("revenue", guard='{address}{r}=""'),

            Col("alert", "What needs doing", 46, "wrap",
                formula=alert_chain("address", [
                    ('{customer_name}{r}="Not in Customer CRM"',
                     "Check - the Customer ID does not exist"),
                    ('{lawn_area}{r}=0',
                     "Add - no lawn area, so nothing here can be priced"),
                    ('AND({is_active}{r}=1,{jobs_open}{r}=0,'
                     '{contracts}{r}=0)',
                     "Schedule - active site with nothing booked and no "
                     "contract"),
                    ('AND({is_active}{r}=1,{days_since}{r}>=DormantDays,'
                     '{jobs_done}{r}>0)',
                     "Dormant - a long time since the last visit here"),
                    ('AND({revenue}{r}>0,{profit}{r}<0)',
                     "Loss - this address costs more than it brings in"),
                    ('AND({hours_actual}{r}>0,{per_hour}{r}<>"",'
                     '{per_hour}{r}<ChargeRate)',
                     "Thin margin - earning under your hourly rate here"),
                    ('{miles}{r}=0',
                     "Add - no distance set, so travel is not being "
                     "charged"),
                    ('AND({jobs_done}{r}=0,{jobs_open}{r}=0)',
                     "Action - no work recorded at this property yet"),
                ]),
                cf=alert_cf()),
        ],
    )
