"""Equipment Inventory - what you own, what it is worth and what it owes you.

Cameras are the second biggest cost in a wedding photography business
after your own time, and the one most often treated as a hobby
purchase.  This tab puts a cost-per-wedding on every body and lens, and
keeps the serial numbers an insurer will ask for.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, blank, id_col, lookup_staff, money_cf,
                     rank_desc, status_cf, yesno, zero)

NAME = "Equipment Inventory"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("item", "EquipmentPrefix", digits=cfg.digits("equipment"),
               header="Item ID"),

        Col("item", "Item", 22, "id", group="What it is"),
        Col("category", "Category", 15, "text",
            validate=list_from("EquipmentCategoryList"),
            group="What it is"),
        Col("make", "Make and model", 22, "text", group="What it is"),
        Col("serial", "Serial number", 18, "text",
            note="The first thing an insurer or the police will ask "
                 "for, and the hardest thing to find afterwards.",
            group="What it is"),
        Col("status", "Status", 13, "status",
            validate=list_from("EquipmentStatusList"), cf=status_cf(),
            group="What it is"),
        Col("condition", "Condition", 12, "text",
            validate=list_from("EquipmentConditionList"),
            group="What it is"),
        Col("assigned", "Assigned to", 12, "id",
            validate=list_from("StaffList"), group="What it is"),
        Col("assigned_name", "Who has it", 16, "text",
            formula=lookup_staff("name", key="assigned", missing=""),
            group="What it is"),
        Col("location", "Kept where", 16, "text", group="What it is"),

        # ---- what it cost -----------------------------------------------------
        Col("bought", "Bought", 11, "date",
            validate=date_check(), group="What it cost"),
        Col("price", "Price paid", 12, "money",
            validate=number_check(0, 1000000), cf=money_cf(),
            group="What it cost"),
        Col("life_years", "Useful life", 10, "number1",
            validate=number_check(0, 40),
            note="How many years you expect to get out of it. Leave "
                 "blank to use the default from Settings.",
            group="What it cost"),
        Col("life_used", "Life used", 10, "number1",
            formula=zero("item",
                         'IF({life_years}{r}="",EquipmentLifeYears,'
                         '{life_years}{r})'),
            hidden=True, group="What it cost"),
        Col("age_years", "Age in years", 11, "number1",
            formula=blank("item",
                          'IF({bought}{r}="","",'
                          'ROUND((TodayDate-{bought}{r})/365.25,2))'),
            group="What it cost"),
        Col("annual_cost", "Cost a year", 11, "money",
            formula=zero("item",
                         'IF({life_used}{r}<=0,0,'
                         'ROUND(IF({price}{r}="",0,{price}{r})/'
                         '{life_used}{r},2))'),
            note="Spread over its useful life. This, not the sticker "
                 "price, is what the camera costs your business each "
                 "year.",
            group="What it cost"),
        Col("written_down", "Written down to", 13, "money",
            formula=zero("item",
                         'IF({price}{r}="",0,'
                         'IF({age_years}{r}="",{price}{r},'
                         'ROUND(MAX(0,{price}{r}-{annual_cost}{r}*'
                         '{age_years}{r}),2)))'),
            note="A rough straight-line figure for your own planning. "
                 "Your accountant's depreciation schedule is the one "
                 "that counts at tax time.",
            group="What it cost"),
        Col("weddings_since", "Weddings since", 12, "int",
            formula=zero("item",
                         'IF({bought}{r}="",0,'
                         'COUNTIFS([[Wedding Bookings.wed_num]],'
                         '">="&{bought}{r},'
                         '[[Wedding Bookings.wed_num]],'
                         '"<="&TodayDate,'
                         '[[Wedding Bookings.earns]],"Yes"))'),
            group="What it cost"),
        Col("cost_per_wedding", "Cost a wedding", 12, "money",
            formula=blank("item",
                          'IF({weddings_since}{r}<=0,"",'
                          'ROUND(IF({price}{r}="",0,{price}{r})/'
                          '{weddings_since}{r},2))'),
            note="What it has cost you per wedding so far. A lens "
                 "that has shot forty weddings has earned its keep; "
                 "one that has shot two has not.",
            group="What it cost"),
        rank_desc("price", guard='{item}{r}=""', header="Value rank"),

        # ---- looking after it --------------------------------------------------
        Col("insured", "Insured", 9, "flag",
            validate=yesno(), cf=status_cf(), group="Looking after it"),
        Col("insured_value", "Insured for", 12, "money",
            validate=number_check(0, 1000000), group="Looking after it"),
        Col("under_insured", "Short by", 11, "money",
            formula=zero("item",
                         'IF({insured}{r}<>"Yes",0,'
                         'MAX(0,IF({price}{r}="",0,{price}{r})-'
                         'IF({insured_value}{r}="",0,'
                         '{insured_value}{r})))'),
            group="Looking after it"),
        Col("warranty_to", "Warranty to", 12, "date",
            validate=date_check(), group="Looking after it"),
        Col("serviced", "Last serviced", 12, "date",
            validate=date_check(), group="Looking after it"),
        Col("service_due", "Service due", 12, "date",
            formula=blank("item",
                          'IF({serviced}{r}="","",'
                          '{serviced}{r}+ServiceMonths*30)'),
            group="Looking after it"),
        Col("shutter", "Shutter count", 12, "int",
            validate=number_check(0, 2000000),
            note="For camera bodies. Most shutters are rated between "
                 "150,000 and 500,000 actuations.",
            group="Looking after it"),
        Col("shutter_limit", "Rated for", 11, "int",
            validate=number_check(0, 2000000), group="Looking after it"),
        Col("shutter_used", "Shutter life used", 13, "percent0",
            formula=blank("item",
                          'IF({shutter_limit}{r}="","",'
                          'IF({shutter_limit}{r}<=0,"",'
                          'IF({shutter}{r}="","",'
                          '{shutter}{r}/{shutter_limit}{r})))'),
            group="Looking after it"),
        Col("backup_for", "Backs up", 16, "text",
            note="Which item this is the spare for. Shooting a "
                 "wedding without a second body is a decision, not an "
                 "accident.",
            group="Looking after it"),
        Col("replace_cost", "Replacement cost", 13, "money",
            validate=number_check(0, 1000000), group="Looking after it"),
        Col("notes", "Notes", 24, "wrap", group="Looking after it"),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({item}{r}="","",'
                'IF({status}{r}="Sold","",'
                'IF({status}{r}="Lost or stolen",'
                '"Check - write it off and tell your insurer",'
                'IF({status}{r}="Being repaired",'
                '"Action - away for repair, check your cover",'
                'IF({serial}{r}="","Add - no serial number recorded",'
                'IF({insured}{r}<>"Yes",'
                'IF(IF({price}{r}="",0,{price}{r})>=InsureAbove,'
                '"Check - valuable and not insured","OK"),'
                'IF({under_insured}{r}>0,'
                '"Check - insured for less than it cost",'
                'IF({shutter_used}{r}<>"",'
                'IF({shutter_used}{r}>=0.8,'
                '"Order - shutter near the end of its life",'
                'IF({service_due}{r}<>"",'
                'IF(TodayDate>{service_due}{r},'
                '"Due - service overdue","OK"),"OK")),'
                'IF({service_due}{r}<>"",'
                'IF(TodayDate>{service_due}{r},'
                '"Due - service overdue","OK"),"OK")))))))))'),
            cf=alert_cf(), group="Looking after it"),
    ]

    return SheetSpec(
        name=NAME,
        title="Equipment Inventory",
        subtitle=("Every body, lens, light and card you own - what it "
                  "is worth, what it costs you and when it needs "
                  "looking at"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=2,
        samples=sample("equipment", cfg),
        help_text=(
            "List everything you would have to replace if the car were "
            "broken into. Serial numbers, what you paid and what it is "
            "insured for. The sheet works out what each item costs you "
            "per year and per wedding, and flags anything expensive "
            "that is not covered."),
        extra_notes=[
            "Record serial numbers now, while the box is in front of "
            "you. Nobody has ever found a serial number quickly on "
            "the day they needed it.",
            "'Cost a wedding' is the honest way to think about kit. A "
            "$2,400 lens across forty weddings is sixty dollars a "
            "wedding; across three it is eight hundred.",
            "The written-down figure here is straight-line and rough, "
            "for your own planning only. Capital allowances and "
            "depreciation for tax are a matter for your accountant "
            "and your country's rules.",
        ],
    )
