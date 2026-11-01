"""Profit Analysis - what each wedding actually made, line by line.

The booking row gives a profit figure.  This tab shows the working:
where the money came from, where it went, how many hours it really
took and what that works out at an hour.  Type a Booking ID and every
other cell fills itself in.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from
from .common import (alert_cf, bar_cf, blank, date_num_col, id_col,
                     lookup_booking, lookup_booking_num_zero, loss_cf,
                     money_cf, month_col, rank_desc, status_cf, year_col,
                     zero)

NAME = "Profit Analysis"


def _b(field: str) -> str:
    """A numeric field from the booking, zero when it is missing."""
    return lookup_booking_num_zero(field)[1:]


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "ProfitPrefix", digits=cfg.digits("profit"),
               header="Line ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="Type or pick a Booking ID. Everything to the right "
                 "fills itself in - this tab is read-only working.",
            group="The wedding"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="The wedding"),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The wedding"),
        Col("package", "Package", 16, "text",
            formula=lookup_booking("package", missing=""),
            group="The wedding"),
        Col("status", "Status", 13, "status",
            formula=lookup_booking("status", missing=""),
            cf=status_cf(), group="The wedding"),
        Col("venue_type", "Venue type", 12, "text",
            formula=lookup_booking("venue_type", missing=""),
            group="The wedding"),
        Col("season", "Season", 9, "text",
            formula=lookup_booking("season", missing=""),
            group="The wedding"),

        # ---- what came in -----------------------------------------------------
        Col("package_price", "Package", 12, "money",
            formula=zero("booking", _b("package_price")),
            group="What came in"),
        Col("extra_hours", "Extra hours", 11, "money",
            formula=zero("booking", _b("extra_hour_fee")),
            group="What came in"),
        Col("addons", "Add-ons", 11, "money",
            formula=zero("booking", _b("addons")),
            group="What came in"),
        Col("travel_charged", "Travel charged", 12, "money",
            formula=zero("booking", _b("travel_used")),
            group="What came in"),
        Col("discount", "Discount given", 12, "money",
            formula=zero("booking", _b("discount")),
            cf=loss_cf(), group="What came in"),
        Col("after_sales", "Prints and albums", 13, "money",
            formula=zero("booking",
                         'SUMIFS([[Gallery & Delivery.after_total]],'
                         '[[Gallery & Delivery.booking]],'
                         '{booking}{r})'),
            note="Money the gallery earned after delivery. The "
                 "booking does not count it; the year should.",
            group="What came in"),
        Col("tax_collected", "Tax collected", 11, "money",
            formula=zero("booking", _b("tax")),
            note="Shown for information; revenue already excludes tax.",
            group="What came in"),
        Col("revenue", "Revenue", 12, "money",
            formula=zero("booking",
                         'ROUND({package_price}{r}+{extra_hours}{r}+'
                         '{addons}{r}+{travel_charged}{r}-'
                         '{discount}{r}+{after_sales}{r},2)'),
            cf=money_cf(),
            note="Everything the wedding brought in, before tax and "
                 "before costs.",
            group="What came in"),
        Col("collected", "Actually received", 13, "money",
            formula=zero("booking", _b("collected")),
            group="What came in"),
        Col("outstanding", "Still owed", 11, "money",
            formula=zero("booking", _b("outstanding")),
            cf=loss_cf(), group="What came in"),

        # ---- what went out -----------------------------------------------------
        Col("second_cost", "Second shooter", 12, "money",
            formula=zero("booking", _b("team_cost")),
            group="What went out"),
        Col("editing_cost", "Editing", 11, "money",
            formula=zero("booking", _b("editing_cost")),
            group="What went out"),
        Col("travel_cost", "Travel", 11, "money",
            formula=zero("booking",
                         'SUMIFS([[Expense Tracker.profit_cost]],'
                         '[[Expense Tracker.booking]],{booking}{r},'
                         '[[Expense Tracker.category]],"Travel & mileage")+'
                         'SUMIFS([[Expense Tracker.profit_cost]],'
                         '[[Expense Tracker.booking]],{booking}{r},'
                         '[[Expense Tracker.category]],"Accommodation")+'
                         'SUMIFS([[Expense Tracker.profit_cost]],'
                         '[[Expense Tracker.booking]],{booking}{r},'
                         '[[Expense Tracker.category]],"Meals on shoot")'),
            group="What went out"),
        Col("album_cost", "Albums and prints", 13, "money",
            formula=zero("booking",
                         'SUMIFS([[Expense Tracker.profit_cost]],'
                         '[[Expense Tracker.booking]],{booking}{r},'
                         '[[Expense Tracker.category]],'
                         '"Albums & prints")'),
            group="What went out"),
        Col("other_direct", "Other wedding costs", 14, "money",
            formula=zero("booking",
                         'IFERROR(INDEX([[Wedding Bookings.direct_costs]],'
                         'MATCH({booking}{r},[[Wedding Bookings.id]],0)),0)-'
                         '{album_cost}{r}-{second_cost}{r}-'
                         '{editing_cost}{r}-{travel_cost}{r}'),
            group="What went out"),
        Col("overhead_share", "Share of overheads", 14, "money",
            formula=zero("booking",
                         'IF(OR({wedding_date}{r}="",IFERROR(INDEX([[Wedding Bookings.earns]],MATCH({booking}{r},[[Wedding Bookings.id]],0)),"No")<>"Yes"),0,'
                         'IF(COUNTIFS([[Wedding Bookings.year]],YEAR({wedding_date}{r}),'
                         '[[Wedding Bookings.earns]],"Yes")=0,0,'
                         'ROUND(SUMIFS([[Expense Tracker.profit_cost]],'
                         '[[Expense Tracker.year]],YEAR({wedding_date}{r}),'
                         '[[Expense Tracker.is_overhead]],"Yes")/'
                         'COUNTIFS([[Wedding Bookings.year]],YEAR({wedding_date}{r}),'
                         '[[Wedding Bookings.earns]],"Yes"),2)))'),
            note="The year's overheads spread evenly across the "
                 "year's weddings. Rough, but far better than "
                 "pretending insurance and software are free.",
            group="What went out"),
        Col("direct_total", "Direct costs", 12, "money",
            formula=zero("booking",
                         'ROUND({second_cost}{r}+{editing_cost}{r}+'
                         '{travel_cost}{r}+{album_cost}{r}+'
                         '{other_direct}{r},2)'),
            group="What went out"),
        Col("total_cost", "All costs", 12, "money",
            formula=zero("booking",
                         'ROUND({direct_total}{r}+'
                         '{overhead_share}{r},2)'),
            group="What went out"),

        # ---- what it made --------------------------------------------------------
        Col("gross_profit", "Profit before overheads", 16, "money",
            formula=zero("booking",
                         'ROUND({revenue}{r}-{direct_total}{r},2)'),
            cf=loss_cf(), group="What it made"),
        Col("gross_margin", "Gross margin", 11, "percent0",
            formula=blank("booking",
                          'IF({revenue}{r}<=0,"",'
                          '{gross_profit}{r}/{revenue}{r})'),
            cf=bar_cf(), group="What it made"),
        Col("net_profit", "Profit after overheads", 16, "money",
            formula=zero("booking",
                         'ROUND({revenue}{r}-{total_cost}{r},2)'),
            cf=loss_cf(),
            note="The real number. What this wedding left you once "
                 "its share of running the business is taken out.",
            group="What it made"),
        Col("net_margin", "Net margin", 10, "percent0",
            formula=blank("booking",
                          'IF({revenue}{r}<=0,"",'
                          '{net_profit}{r}/{revenue}{r})'),
            cf=bar_cf(), group="What it made"),

        # ---- what it took ---------------------------------------------------------
        Col("shoot_hours", "Hours shooting", 12, "number1",
            formula=zero("booking", _b("coverage_hours")),
            group="What it took"),
        Col("edit_hours", "Hours editing", 12, "number1",
            formula=zero("booking",
                         'IFERROR(INDEX([[Editing Workflow.hours]],'
                         'MATCH({booking}{r},'
                         '[[Editing Workflow.booking]],0))*1,'
                         'EditingHours)'),
            group="What it took"),
        Col("travel_hours", "Hours travelling", 13, "number1",
            formula=zero("booking",
                         'SUMIFS([[Travel & Mileage.hours]],'
                         '[[Travel & Mileage.booking]],{booking}{r})'),
            group="What it took"),
        Col("admin_hours", "Hours on admin", 12, "number1",
            formula=zero("booking", "AdminHoursPerWedding"),
            group="What it took"),
        Col("total_hours", "Hours in all", 11, "number1",
            formula=zero("booking",
                         'ROUND({shoot_hours}{r}+{edit_hours}{r}+'
                         '{travel_hours}{r}+{admin_hours}{r},2)'),
            note="Shooting, editing, driving and admin. The whole "
                 "job, not just the day.",
            group="What it took"),
        Col("per_hour", "Profit an hour", 12, "money",
            formula=blank("booking",
                          'IF({total_hours}{r}<=0,"",'
                          'ROUND({net_profit}{r}/'
                          '{total_hours}{r},2))'),
            cf=loss_cf(),
            note="The number worth knowing before you agree to the "
                 "next discount.",
            group="What it took"),
        Col("vs_target", "Against target", 12, "money",
            formula=zero("booking",
                         'ROUND({net_profit}{r}-'
                         '(TargetAverageValue*TargetMargin),2)'),
            cf=loss_cf(), group="What it took"),
        Col("beats_hourly", "Beats your rate", 12, "flag",
            formula=blank("booking",
                          'IF({per_hour}{r}="","",'
                          'IF({per_hour}{r}>=MinimumHourly,'
                          '"Yes","No"))'),
            cf=status_cf(), group="What it took"),
        rank_desc("net_profit", guard='{booking}{r}=""',
                  header="Profit rank"),
        rank_desc("per_hour", guard='{booking}{r}=""',
                  header="Hourly rank"),

        month_col("wedding_date", "month", "Wedding month"),
        year_col("wedding_date"),
        date_num_col("wedding_date", "wed_num", "Wedding date number"),

        Col("verdict", "What it tells you", 34, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({revenue}{r}<=0,"Check - no revenue on this one",'
                'IF({net_profit}{r}<0,'
                '"Loss - this wedding cost more than it earned",'
                'IF({outstanding}{r}>0,'
                '"Unpaid - profitable on paper, not yet in the bank",'
                'IF({per_hour}{r}<>"",'
                'IF({per_hour}{r}<MinimumHourly,'
                '"Check - below the hourly rate you set",'
                'IF({net_margin}{r}<>"",'
                'IF({net_margin}{r}<TargetMargin,'
                '"Check - under your target margin",'
                'IF({discount}{r}>0,'
                '"OK - good wedding, and you discounted it",'
                '"OK - this is the kind you want more of")),'
                '"OK")),"OK"))))) '.strip()),
            cf=alert_cf(), group="What it took"),
    ]

    return SheetSpec(
        name=NAME,
        title="Profit Analysis",
        subtitle=("What each wedding really made once travel, "
                  "editing, the second shooter and a share of the "
                  "overheads come out"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("profit", cfg),
        help_text=(
            "Type a Booking ID in column B and the whole line fills "
            "itself in. Nothing else on this tab is typed - it is the "
            "working behind the profit figure on the booking, "
            "including the hours and the overheads the booking "
            "leaves out."),
        extra_notes=[
            "'Profit after overheads' spreads the year's running "
            "costs evenly across the year's weddings. It is a rough "
            "apportionment, and it is still far closer to the truth "
            "than pretending insurance, software and your website "
            "cost nothing.",
            "'Profit an hour' counts shooting, editing, driving and "
            "admin. It is usually a third of what photographers think "
            "it is, and it is the single most useful number in this "
            "workbook.",
            "A wedding can be profitable and still be a problem if it "
            "is unpaid. The verdict column says so rather than "
            "letting a good margin hide a bad debt.",
        ],
    )
