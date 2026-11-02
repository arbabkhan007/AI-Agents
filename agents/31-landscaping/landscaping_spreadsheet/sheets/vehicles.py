"""15. Vehicle & Fuel Tracker - every fill-up and every repair.

One row per fill-up or per vehicle cost. Record the odometer each
time and the workbook works out the miles between fills and the
economy you are actually getting, which is the earliest warning you
will get that something is wrong with a truck.

Fuel entered here also lands on the expense reports, so it is
counted once and only once.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check
from .common import (alert_cf, alert_chain, amount, date_num_col, id_col,
                     money_cf, month_col, pick, scale_cf, yesno, zero)

NAME = "Vehicle & Fuel Tracker"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Vehicle & Fuel Tracker",
        subtitle="Fill-ups, repairs, tax and insurance - by vehicle, "
                 "with the economy you are really getting.",
        tab_color=Palette.accent,
        rows=cfg.row_count("vehicles"),
        samples=sample("vehicles", cfg),
        freeze_cols=3,
        help_text=(
            "One line per fill-up or per vehicle bill. Put the "
            "odometer reading on every fuel line and the miles per "
            "gallon work themselves out from one fill to the next. "
            "Set up your vehicles in the list on the Settings tab "
            "first."),
        extra_notes=[
            "Economy is calculated between consecutive fill-ups for "
            "the same vehicle, so the first fill for each one shows "
            "nothing. That is correct, not a fault.",
            "A truck whose economy drops by a fifth is telling you "
            "something - tyres, a dragging brake, a trailer loaded "
            "wrong, or a driver with a heavy foot.",
            "Costs recorded here flow into the expense reports "
            "automatically. Do not enter the same fuel receipt on "
            "the Expense Tracker as well or it will be counted "
            "twice.",
        ],
        columns=[
            id_col("date", '"VEH-"', digits=5, header="Line"),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="Start here."),
            Col("vehicle", "Vehicle", 16, "text",
                validate=pick("VehicleList",
                              "Pick the vehicle. The list is on the "
                              "Settings tab."),
                note="Pick from the list so one truck's history stays "
                     "in one place."),
            Col("type", "Cost type", 16, "text",
                validate=pick("VehicleCostList",
                              "Fuel, service, repair, tyres, "
                              "insurance, tax, cleaning."),
                note="Fuel lines get the economy treatment; the rest "
                     "are just costs."),
            Col("odometer", "Odometer", 11, "int",
                validate=amount(0, 2000000, decimal=False),
                note="The reading at the pump. Put it on every fuel "
                     "line and the economy columns do the rest."),
            Col("gallons", "Gallons / litres", 13, "number1",
                validate=amount(0, 1000,
                                "How much fuel went in. Use whichever "
                                "unit you buy in, consistently."),
                note="Whatever unit you buy in - just be consistent, "
                     "because the economy figure follows it."),
            Col("amount", "Cost", 11, "money",
                validate=amount(0, 1000000),
                cf=money_cf(),
                note="What you paid."),
            Col("unit_price", "Price per unit", 12, "money",
                formula='=IF({date}{r}="","",'
                        'IF({gallons}{r}<=0,"",'
                        'ROUND({amount}{r}/'
                        '{gallons}{r},3)))',
                note="Worth watching over a season. Fuel is usually "
                     "the third biggest cost in this trade."),
            Col("full_tank", "Filled up", 10, "flag",
                validate=yesno("Was the tank filled right up? Economy "
                               "is only meaningful between full "
                               "tanks."),
                note="Part fills make the economy figure meaningless, "
                     "so they are skipped."),
            Col("driver", "Driver", 16, "text",
                note="Who was driving. Useful when one truck's economy "
                     "is oddly worse than the other's."),
            Col("supplier", "Where", 18, "text"),
            Col("reference", "Receipt / invoice", 16, "text"),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the job, if this cost belongs to "
                              "one."),
                note="Only if this cost belongs to one job - a special "
                     "trip to the tip, for instance. Usually blank."),
            Col("notes", "Notes", 26, "wrap"),

            # ---- the economy -----------------------------------------
            Col("is_fuel", "Fuel", 6, "int",
                formula=zero("date",
                             'IF(AND({type}{r}="Fuel",'
                             '{gallons}{r}>0,{odometer}{r}>0),1,0)'),
                hidden=True),
            Col("prev_odo", "Previous odo", 11, "int",
                formula=zero("date",
                             'IF({is_fuel}{r}=0,0,'
                             'SUMPRODUCT(MAX('
                             '({vehicle_first}:{vehicle_last}='
                             '{vehicle}{r})*'
                             '({is_fuel_first}:{is_fuel_last}=1)*'
                             '({odometer_first}:{odometer_last}<'
                             '{odometer}{r})*'
                             '{odometer_first}:{odometer_last})))'),
                hidden=True,
                note="The highest lower odometer reading for the same "
                     "vehicle - where this tank started. Works out by "
                     "reading, not by row, so entering a receipt late "
                     "does not break it."),
            Col("miles", "Miles on tank", 12, "int",
                formula='=IF({date}{r}="","",'
                        'IF({prev_odo}{r}<=0,"",'
                        '{odometer}{r}-{prev_odo}{r}))',
                note="Blank on the first fill for each vehicle, which "
                     "is as it should be."),
            Col("economy", "Miles per unit", 13, "number1",
                formula='=IF({date}{r}="","",'
                        'IF({is_fuel}{r}=0,"",'
                        'IF({full_tank}{r}<>"Yes","",'
                        'IF({prev_odo}{r}<=0,"",'
                        'ROUND(({odometer}{r}-'
                        '{prev_odo}{r})/{gallons}{r},2)))))',
                cf=scale_cf(),
                note="Only on full tanks with a previous reading to "
                     "measure from."),
            Col("cost_per_mile", "Cost per mile", 12, "money",
                formula='=IF({date}{r}="","",'
                        'IF({miles}{r}="","",'
                        'IF({miles}{r}<=0,"",'
                        'ROUND({amount}{r}/'
                        '{miles}{r},3))))'),
            Col("vehicle_avg", "Vehicle average", 13, "number1",
                formula='=IF({date}{r}="","",'
                        'IF({is_fuel}{r}=0,"",'
                        'IFERROR(AVERAGEIFS('
                        '{economy_first}:{economy_last},'
                        '{vehicle_first}:{vehicle_last},'
                        '{vehicle}{r},'
                        '{economy_first}:{economy_last},">0"),"")))',
                hidden=True),
            Col("economy_gap", "vs average", 10, "percent",
                formula='=IF({date}{r}="","",'
                        'IF({economy}{r}="","",'
                        'IF({vehicle_avg}{r}="","",'
                        'IF({vehicle_avg}{r}<=0,"",'
                        'ROUND({economy}{r}/'
                        '{vehicle_avg}{r}-1,4)))))',
                cf=[{"type": "cell", "criteria": "<", "value": -0.15,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": ">", "value": 0.1,
                     "fmt": "good"}],
                note="How this tank compares with that vehicle's "
                     "normal. A run of red is worth investigating."),
            date_num_col("date", "date_num"),
            month_col("date"),

            Col("alert", "What needs doing", 42, "wrap",
                formula=alert_chain("date", [
                    ('AND({type}{r}="Fuel",{odometer}{r}=0)',
                     "Add - no odometer reading, so economy cannot be "
                     "worked out"),
                    ('{amount}{r}=0', "Add - no cost on this line"),
                    ('AND({economy_gap}{r}<>"",'
                     '{economy_gap}{r}<-0.15)',
                     "Check - economy well below this vehicle's "
                     "average"),
                    ('AND({type}{r}="Fuel",{gallons}{r}=0)',
                     "Add - no quantity, so price per unit is blank"),
                    ('AND({prev_odo}{r}>0,{odometer}{r}<'
                     '{prev_odo}{r})',
                     "Check - odometer lower than a previous reading"),
                    ('{reference}{r}=""',
                     "Add - no receipt reference recorded"),
                ]),
                cf=alert_cf()),
        ],
    )
