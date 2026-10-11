"""`Services` - the service catalogue and price list that drives booking costs."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import list_from, number_check, yes_no
from .common import blank, id_col, status_cf

NAME = "Services"


def spec(cfg: Config) -> SheetSpec:
    columns = [
        id_col("name", '"SV-"', digits=3, width=9),
        Col("name", "Service name", 26, "text",
            note="This exact name is used by the Bookings drop down - "
                 "rename it here and every price follows."),
        Col("category", "Category", 16, "text",
            validate=list_from("ServiceCategoryList")),
        Col("description", "What is included", 38, "wrap"),
        Col("unit", "Billing unit", 13, "text",
            validate=list_from("BillingUnitList"),
            note="Per hour multiplies the rate by the booking duration. "
                 "Everything else multiplies the rate by the Qty column on "
                 "the booking."),
        Col("duration", "Standard length (mins)", 12, "int",
            validate=number_check(0, 1440, decimal=False)),
        Col("rate", "Base rate", 12, "money",
            validate=number_check(0, 100000)),
        Col("extra_pet", "Additional pet fee", 12, "money",
            validate=number_check(0, 10000),
            note="Leave blank to use the default additional pet fee from "
                 "the Settings tab."),
        Col("hol_pct", "Holiday surcharge", 11, "percent",
            validate=number_check(0, 2),
            note="Leave blank to use the global holiday surcharge."),
        Col("wkd_pct", "Weekend surcharge", 11, "percent",
            validate=number_check(0, 2),
            note="Leave blank to use the global weekend surcharge."),
        Col("travel", "Travel fee applies?", 11, "flag",
            validate=yes_no()),
        Col("staff_cost", "Staff cost per unit", 12, "money",
            validate=number_check(0, 100000),
            note="What it costs you to deliver one unit - used for the "
                 "profitability columns."),
        Col("profit", "Gross profit per unit", 12, "money",
            formula=blank("rate",
                          '{rate}{r}-IF({staff_cost}{r}="",0,'
                          '{staff_cost}{r})')),
        Col("margin", "Margin %", 10, "percent",
            formula='=IF(OR({rate}{r}="",{rate}{r}=0),"",'
                    '{profit}{r}/{rate}{r})',
            cf=[{"type": "3_color_scale", "min_color": "#FDA4AF",
                 "mid_color": "#FCD34D", "max_color": "#6EE7B7"}]),
        Col("times_booked", "Times booked", 11, "int",
            formula=blank("name",
                          'COUNTIFS([[Bookings.service]],{name}{r},'
                          '[[Bookings.status]],"<>Cancelled")')),
        Col("revenue", "Revenue to date", 13, "money",
            formula=blank("name",
                          'SUMIFS([[Bookings.total]],[[Bookings.service]],'
                          '{name}{r},[[Bookings.status]],"<>Cancelled")'),
            cf=[{"type": "data_bar", "bar_color": "#6366F1"}]),
        Col("avg_value", "Average value", 12, "money",
            formula='=IF(OR({times_booked}{r}="",{times_booked}{r}=0),"",'
                    '{revenue}{r}/{times_booked}{r})'),
        Col("est_profit", "Estimated profit", 13, "money",
            formula='=IF(OR({times_booked}{r}="",{profit}{r}=""),"",'
                    '{times_booked}{r}*{profit}{r})',
            cf=[{"type": "data_bar", "bar_color": "#F59E0B"}]),
        Col("active", "Active?", 9, "flag", validate=yes_no(),
            cf=status_cf()),
        Col("notes", "Notes", 30, "wrap"),
    ]

    return SheetSpec(
        name=NAME,
        title="Services & Price List",
        subtitle="Add every service you sell. Bookings pull the billing "
                 "unit, rate, additional pet fee and surcharges straight "
                 "from this table.",
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
        samples=sample(cfg).services,
        help_text="Cream cells = your prices. Grey cells are locked "
                  "formulas: profit, margin, how often each service sells "
                  "and what it has earned.",
    )
