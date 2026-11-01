"""Packages & Pricing - what you sell, what it costs you, what it earns.

This is the pricing calculator at the heart of the product.  Change the
hours on a package and the cost of delivering it, the margin, the
effective hourly rate and the suggested price all move with it, and
every booking already sold on that package re-prices itself.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from, number_check
from .common import (alert_cf, bar_cf, blank, loss_cf, money_cf, rank_desc,
                     status_cf, yesno, zero)

NAME = "Packages & Pricing"


def spec(cfg) -> SheetSpec:
    columns = [
        Col("name", "Package name", 20, "id",
            note="Type the name exactly as you want it to appear on "
                 "the booking drop-down and on your invoices.",
            group="The package"),
        Col("tier", "Tier", 11, "text",
            validate=list_from("TierList"), group="The package"),
        Col("active", "Still selling", 10, "flag",
            validate=yesno("Mark retired packages No and retain their rows for "
                           "historical bookings. They remain in the drop-down; "
                           "do not select them for new bookings."),
            group="The package"),
        Col("summary", "One-line summary", 30, "wrap",
            group="The package"),

        # ---- what the couple gets -----------------------------------------
        Col("hours", "Coverage hours", 12, "number1",
            validate=number_check(0, 24),
            note="Hours on the day. Anything past this bills at your "
                 "extra-hour rate on the booking automatically.",
            group="What they get"),
        Col("photographers", "Photographers", 12, "int",
            validate=number_check(1, 6), group="What they get"),
        Col("engagement", "Engagement shoot", 12, "flag",
            validate=yesno(), group="What they get"),
        Col("images", "Edited images", 11, "int",
            validate=number_check(0, 5000), group="What they get"),
        Col("album", "Album", 14, "text", group="What they get"),
        Col("print_credit", "Print credit", 11, "money",
            validate=number_check(0, 100000), group="What they get"),
        Col("travel_allowance", "Travel included", 12, "int",
            validate=number_check(0, 5000),
            note="Miles included before you start charging mileage.",
            group="What they get"),
        Col("inclusions", "Everything included", 34, "wrap",
            note="The list you paste into a proposal. Write it once "
                 "here rather than re-typing it for every enquiry.",
            group="What they get"),

        # ---- the price ----------------------------------------------------
        Col("base_price", "List price", 12, "money",
            validate=number_check(0, 1000000), cf=money_cf(),
            group="The price"),
        Col("standard_discount", "Standard discount", 13, "money",
            validate=number_check(0, 1000000),
            note="An off-season or weekday reduction you are happy to "
                 "give without being asked.",
            group="The price"),
        Col("total_price", "Price charged", 13, "money",
            formula=zero("name",
                         'ROUND({base_price}{r}-'
                         'IF({standard_discount}{r}="",0,'
                         '{standard_discount}{r}),2)'),
            cf=money_cf(),
            note="What a booking on this package is actually worth. "
                 "Every booking reads this cell.",
            group="The price"),

        # ---- what it costs you ---------------------------------------------
        Col("second_cost", "Second shooter", 12, "money",
            formula=zero("name",
                         'IF({photographers}{r}<=1,0,'
                         '({photographers}{r}-1)*SecondShooterRate)'),
            group="What it costs you"),
        Col("album_cost", "Album cost", 11, "money",
            validate=number_check(0, 100000),
            note="What your lab charges you, not what you charge the "
                 "couple.",
            group="What it costs you"),
        Col("print_cost", "Print cost", 11, "money",
            formula=zero("name",
                         'ROUND(IF({print_credit}{r}="",0,'
                         '{print_credit}{r})*PrintCostRatio,2)'),
            group="What it costs you"),
        Col("engagement_cost", "Engagement cost", 13, "money",
            formula=zero("name",
                         'IF({engagement}{r}<>"Yes",0,'
                         'EngagementCost)'),
            group="What it costs you"),
        Col("editing_hours", "Editing hours", 12, "number1",
            validate=number_check(0, 400),
            note="Leave blank to use the studio default from Settings. "
                 "Be honest here - underestimating editing is how a "
                 "package that looks profitable is not.",
            group="What it costs you"),
        Col("editing_hours_used", "Editing hours used", 13, "number1",
            formula=zero("name",
                         'IF({editing_hours}{r}="",EditingHours,'
                         '{editing_hours}{r})'),
            hidden=True, group="What it costs you"),
        Col("editing_cost", "Editing cost", 12, "money",
            formula=zero("name",
                         'ROUND({editing_hours_used}{r}*EditingRate,2)'),
            group="What it costs you"),
        Col("other_cost", "Other costs", 11, "money",
            validate=number_check(0, 100000),
            note="Insurance apportioned, a sample album, anything else "
                 "this package specifically costs you.",
            group="What it costs you"),
        Col("total_cost", "Cost to deliver", 13, "money",
            formula=zero("name",
                         'ROUND({second_cost}{r}+'
                         'IF({album_cost}{r}="",0,{album_cost}{r})+'
                         '{print_cost}{r}+{engagement_cost}{r}+'
                         '{editing_cost}{r}+'
                         'IF({other_cost}{r}="",0,{other_cost}{r}),2)'),
            group="What it costs you"),

        # ---- is it worth selling --------------------------------------------
        Col("profit", "Profit each", 12, "money",
            formula=zero("name",
                         'ROUND({total_price}{r}-{total_cost}{r},2)'),
            cf=loss_cf(), group="Is it worth selling"),
        Col("margin", "Margin", 9, "percent0",
            formula=blank("name",
                          'IF({total_price}{r}<=0,"",'
                          '{profit}{r}/{total_price}{r})'),
            cf=bar_cf(), group="Is it worth selling"),
        Col("total_hours", "Your hours", 11, "number1",
            formula=zero("name",
                         '{hours}{r}+{editing_hours_used}{r}+'
                         'AdminHoursPerWedding'),
            note="Shooting, editing and the admin every wedding takes. "
                 "The only honest basis for an hourly rate.",
            group="Is it worth selling"),
        Col("hourly", "Your hourly rate", 13, "money",
            formula=blank("name",
                          'IF({total_hours}{r}<=0,"",'
                          'ROUND({profit}{r}/{total_hours}{r},2))'),
            cf=loss_cf(),
            note="Profit divided by every hour the package really "
                 "takes. Compare it with what you would accept from an "
                 "employer before you discount anything.",
            group="Is it worth selling"),
        Col("target_price", "Price for target margin", 15, "money",
            formula=blank("name",
                          'IF(TargetMargin>=1,"",'
                          'ROUND({total_cost}{r}/(1-TargetMargin),2))'),
            note="What this package would have to sell for to hit the "
                 "margin you set on Settings.",
            group="Is it worth selling"),
        Col("price_gap", "Under-priced by", 13, "money",
            formula=zero("name",
                         'IF({target_price}{r}="",0,'
                         'ROUND(MAX(0,{target_price}{r}-'
                         '{total_price}{r}),2))'),
            cf=loss_cf(), group="Is it worth selling"),
        Col("meets_target", "Hits target", 10, "flag",
            formula=blank("name",
                          'IF({total_price}{r}<=0,"",'
                          'IF({margin}{r}>=TargetMargin,"Yes","No"))'),
            cf=status_cf(), group="Is it worth selling"),

        # ---- how it is actually selling ---------------------------------------
        Col("sold", "Weddings sold", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.package]],'
                         '{name}{r},[[Wedding Bookings.earns]],"Yes")'),
            group="How it sells"),
        Col("sold_year", "Sold this year", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Wedding Bookings.package]],'
                         '{name}{r},[[Wedding Bookings.earns]],"Yes",'
                         '[[Wedding Bookings.year]],YEAR(TodayDate))'),
            group="How it sells"),
        Col("enquiries", "Asked about", 11, "int",
            formula=zero("name",
                         'COUNTIFS([[Lead Tracker.package]],{name}{r})'),
            group="How it sells"),
        Col("conversion", "Enquiry to booking", 13, "percent0",
            formula=blank("name",
                          'IF({enquiries}{r}<=0,"",'
                          'MIN(1,{sold}{r}/{enquiries}{r}))'),
            cf=bar_cf(),
            note="How often an enquiry about this package turns into a "
                 "wedding. A package nobody books may be priced wrong, "
                 "or may simply be the one that makes the next one "
                 "look reasonable.",
            group="How it sells"),
        Col("revenue", "Revenue booked", 13, "money",
            formula=zero("name",
                         'SUMIFS([[Wedding Bookings.total_value]],'
                         '[[Wedding Bookings.package]],{name}{r},'
                         '[[Wedding Bookings.earns]],"Yes")'),
            cf=money_cf(), group="How it sells"),
        Col("profit_booked", "Profit booked", 13, "money",
            formula=zero("name",
                         'SUMIFS([[Wedding Bookings.profit]],'
                         '[[Wedding Bookings.package]],{name}{r},'
                         '[[Wedding Bookings.earns]],"Yes")'),
            cf=loss_cf(), group="How it sells"),
        Col("share", "Share of bookings", 12, "percent0",
            formula=blank("name",
                          'IF(COUNTIFS([[Wedding Bookings.earns]],'
                          '"Yes")<=0,"",{sold}{r}/'
                          'COUNTIFS([[Wedding Bookings.earns]],"Yes"))'),
            group="How it sells"),
        rank_desc("revenue", header="Revenue rank",
                  note="1 = the package that has brought in the most."),
        rank_desc("sold", header="Popularity rank"),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({name}{r}="","",'
                'IF({active}{r}<>"Yes","Retired - kept for old bookings",'
                'IF({base_price}{r}="","Add - no price set",'
                'IF({hours}{r}="","Add - no coverage hours",'
                'IF({profit}{r}<0,"Loss - costs more than it sells for",'
                'IF({price_gap}{r}>0,'
                '"Check - under your target margin",'
                'IF({hourly}{r}<>"",'
                'IF({hourly}{r}<MinimumHourly,'
                '"Check - poor hourly rate",'
                'IF({enquiries}{r}>=5,'
                'IF({conversion}{r}<0.1,'
                '"Check - plenty of interest, nobody books it","OK"),'
                '"OK")),"OK")))))))'),
            cf=alert_cf(), group="How it sells"),
    ]

    return SheetSpec(
        name=NAME,
        title="Packages & Pricing",
        subtitle=("What you sell, what each one really costs you to "
                  "deliver, and what it ought to cost"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=2,
        samples=sample("packages", cfg),
        help_text=(
            "Fill in what the package includes and what it costs you to "
            "deliver, and the sheet works out the margin, your real "
            "hourly rate and the price you would need to charge to hit "
            "your target. Bookings read the 'Price charged' column, so "
            "changing a price here re-prices every wedding sold on it."),
        extra_notes=[
            "'Your hours' is coverage plus editing plus the admin every "
            "wedding takes. A package that looks fine on margin can pay "
            "you less per hour than the venue's bar staff, and this is "
            "the column that says so.",
            "Costs here are per wedding. Fixed costs - insurance, "
            "software, your website - belong on the Expense Tracker and "
            "come out of the business as a whole, not out of one "
            "package.",
            "'Price for target margin' uses cost / (1 - margin), which "
            "is the only correct way round. Adding a percentage to cost "
            "gives a smaller margin than you intended.",
        ],
    )
