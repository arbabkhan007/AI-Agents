"""Travel & Mileage - getting to the wedding, and what it costs.

Mileage is the deduction photographers most often lose, because the
record has to be made at the time and nobody wants to make it at
eleven at night in a car park.  One row, four cells, and the rest is
worked out.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, blank, date_num_col, id_col,
                     mileage_cost, money_cf, month_col, status_cf,
                     year_col, yesno, zero)

NAME = "Travel & Mileage"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("date", "TravelPrefix", digits=cfg.digits("travel"),
               header="Trip ID"),

        Col("date", "Date", 11, "date",
            validate=date_check(),
            note="The day you travelled. Log it the same week - "
                 "reconstructing mileage from memory in April is how "
                 "the deduction gets lost.",
            group="The trip"),
        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="Leave blank for travel that is not for one "
                 "particular wedding - a trade show, a bank visit.",
            group="The trip"),
        Col("couple", "Couple", 18, "text",
            formula=blank("date",
                          'IF({booking}{r}="","",'
                          'IFERROR(INDEX('
                          '[[Wedding Bookings.client_name]],'
                          'MATCH({booking}{r},'
                          '[[Wedding Bookings.id]],0))&"",""))'),
            group="The trip"),
        Col("purpose", "Purpose", 16, "text",
            validate=list_from("TravelPurposeList"), group="The trip"),
        Col("from_place", "From", 20, "text", group="The trip"),
        Col("to_place", "To", 20, "text", group="The trip"),
        Col("mode", "How", 12, "text",
            validate=list_from("TravelModeList"), group="The trip"),

        # ---- the distance -----------------------------------------------------
        Col("one_way", "Miles one way", 12, "number1",
            validate=number_check(0, 10000), group="The distance"),
        Col("return_trip", "Return", 9, "flag",
            validate=yesno("Yes doubles the distance. Almost always "
                           "yes, and almost always forgotten."),
            group="The distance"),
        Col("miles", "Total miles", 11, "number1",
            formula=zero("date",
                         'ROUND(IF({one_way}{r}="",0,{one_way}{r})*'
                         'IF({return_trip}{r}="Yes",2,1),1)'),
            group="The distance"),
        Col("scout_trips", "Extra trips", 10, "int",
            validate=number_check(0, 50),
            note="Venue visits, a rehearsal, dropping an album off. "
                 "Each one is the same distance again.",
            group="The distance"),
        Col("all_miles", "Miles in all", 11, "number1",
            formula=zero("date",
                         'ROUND({miles}{r}*(1+'
                         'IF({scout_trips}{r}="",0,'
                         '{scout_trips}{r})),1)'),
            group="The distance"),

        # ---- the cost ---------------------------------------------------------
        Col("mileage", "Mileage cost", 12, "money",
            formula=zero("date",
                         'ROUND({all_miles}{r}*MileageRate,2)'),
            note="At the rate on Settings. Check your own country's "
                 "approved figure each tax year - it changes.",
            group="The cost"),
        Col("fuel", "Fuel instead", 11, "money",
            validate=number_check(0, 100000),
            note="If you claim actual fuel rather than a mileage "
                 "rate, put it here and the mileage figure is "
                 "ignored. Most countries let you do one or the "
                 "other, not both.",
            group="The cost"),
        Col("tolls", "Tolls", 10, "money",
            validate=number_check(0, 100000), group="The cost"),
        Col("parking", "Parking", 10, "money",
            validate=number_check(0, 100000), group="The cost"),
        Col("accommodation", "Accommodation", 13, "money",
            validate=number_check(0, 100000),
            note="For a wedding far enough away that driving home at "
                 "one in the morning is not sensible.",
            group="The cost"),
        Col("other_cost", "Other", 10, "money",
            validate=number_check(0, 100000), group="The cost"),
        Col("total_cost", "Total cost", 12, "money",
            formula=zero("date",
                         'ROUND(IF({fuel}{r}<>"",{fuel}{r},'
                         '{mileage}{r})+'
                         'IF({tolls}{r}="",0,{tolls}{r})+'
                         'IF({parking}{r}="",0,{parking}{r})+'
                         'IF({accommodation}{r}="",0,'
                         '{accommodation}{r})+'
                         'IF({other_cost}{r}="",0,{other_cost}{r}),2)'),
            cf=money_cf(),
            note="What the trip cost you. The wedding subtracts this "
                 "from its profit.",
            group="The cost"),

        # ---- charging it on ----------------------------------------------------
        Col("allowance", "Miles included", 11, "int",
            formula=zero("date",
                         'IF({booking}{r}="",0,'
                         'IFERROR(INDEX('
                         '[[Packages & Pricing.travel_allowance]],'
                         'MATCH(INDEX([[Wedding Bookings.package]],'
                         'MATCH({booking}{r},'
                         '[[Wedding Bookings.id]],0)),'
                         '[[Packages & Pricing.name]],0))*1,'
                         'FreeTravelMiles))'),
            note="Free miles from the package the couple booked.",
            group="Charging it on"),
        Col("billable_miles", "Miles to charge", 12, "number1",
            formula=zero("date",
                         'IF({booking}{r}="",0,'
                         'ROUND(MAX(0,{all_miles}{r}-'
                         '{allowance}{r}),1))'),
            group="Charging it on"),
        Col("suggested", "Suggested charge", 13, "money",
            formula=zero("date",
                         'IF({booking}{r}="",0,'
                         + mileage_cost("{all_miles}{r}",
                                        "{allowance}{r}") + ")"),
            note="Mileage past the package allowance, plus nothing "
                 "else. Tolls and accommodation are a conversation, "
                 "not an automatic charge.",
            group="Charging it on"),
        Col("charge_override", "Charge instead", 12, "money",
            validate=number_check(0, 100000), group="Charging it on"),
        Col("chargeable", "Charged on", 12, "money",
            formula=zero("date",
                         'IF({charge_override}{r}<>"",'
                         '{charge_override}{r},{suggested}{r})'),
            cf=money_cf(),
            note="What the booking adds to the couple's bill. Set "
                 "'Charge instead' to zero to absorb a trip.",
            group="Charging it on"),
        Col("net_cost", "Costs you", 11, "money",
            formula=zero("date",
                         'ROUND({total_cost}{r}-{chargeable}{r},2)'),
            group="Charging it on"),
        Col("hours", "Hours travelling", 12, "number1",
            validate=number_check(0, 100),
            note="Driving time is working time, even though nobody "
                 "pays you for it. Profit per hour on the booking is "
                 "kinder than it should be if you leave this blank.",
            group="Charging it on"),
        Col("receipt", "Receipt kept", 11, "flag",
            validate=yesno(), cf=status_cf(), group="Charging it on"),
        Col("notes", "Notes", 24, "wrap", group="Charging it on"),

        month_col("date"),
        year_col("date"),
        date_num_col("date", "date_num", "Date number"),

        Col("alert", "What to do", 30, "status",
            formula=(
                '=IF({date}{r}="","",'
                'IF({all_miles}{r}<=0,'
                'IF({total_cost}{r}<=0,"Add - no distance or cost",'
                '"OK"),'
                'IF({from_place}{r}="",'
                '"Add - no start point for the journey",'
                'IF({to_place}{r}="","Add - no destination",'
                'IF({receipt}{r}<>"Yes",'
                'IF({total_cost}{r}-{mileage}{r}>0,'
                '"Missing - costs claimed with no receipt","OK"),'
                'IF({booking}{r}="","OK",'
                'IF({net_cost}{r}>TravelLossLimit,'
                '"Loss - this trip cost far more than you charged",'
                '"OK")))))))'),
            cf=alert_cf(), group="Charging it on"),
    ]

    return SheetSpec(
        name=NAME,
        title="Travel & Mileage",
        subtitle=("Every journey for every wedding - the distance, "
                  "the cost and what you can charge on"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("travel", cfg),
        help_text=(
            "Four cells per trip: the date, the Booking ID, the "
            "one-way distance and whether it was a return. Everything "
            "else is worked out - the mileage at your rate, the free "
            "miles the package includes and what is fair to charge on "
            "top."),
        extra_notes=[
            "Mileage rates and what counts as business travel are set "
            "by your own tax authority and change from year to year. "
            "The rate lives on Settings so you can keep it current; "
            "check it against the official figure each April.",
            "Travel between your home and a regular place of work is "
            "usually not deductible, and a wedding venue usually is, "
            "but the line is drawn differently in different "
            "countries. If you are not sure, ask your accountant "
            "rather than this spreadsheet.",
            "Log the hours. A wedding ninety minutes away is three "
            "hours of unpaid driving on top of a ten-hour day, and "
            "that is the difference between a good booking and a "
            "tiring one.",
        ],
    )
