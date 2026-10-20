"""The Overhead tab - the cost of having a studio at all.

Rent, power, insurance, subscriptions, the bookkeeper, the depreciation of the
kiln and the saw. Each row says how often it is paid; `per_month` turns every
frequency into a monthly figure so the whole column can be added up.

That total is what Settings calls ``OverheadMonthly``, and the two derived
figures underneath it - ``OverheadPerHour`` and ``OverheadPerUnit`` - are what
the Products tab and the craft tabs spread across the work, following the
method chosen on Settings. Rows marked ``allocated = No`` are real money but
are not pushed into a product cost; `shop_time_check` compares the rest against
the labour hours that were actually recorded.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, id_col, int_col, list_col, money_col,
                     other, row_ref, samples, spec_defaults, sumifs, text_col,
                     wrap_col, yesno_col)

P = Palette

NAME = "Overhead"

SUBTITLE = ("Rent, power, insurance, subscriptions and equipment: the monthly "
            "cost of the studio, spread across the work.")

HELP = ("Type each cost and how often it is paid. 'A month' normalises "
        "everything, 'Allocated' says whether it belongs in a product cost, "
        "and the two columns on the right show what it comes to per unit and "
        "per hour at the volumes on Settings.")

TIMES_A_YEAR = ('IF(EXACT({f},"Weekly"),52,'
                'IF(EXACT({f},"Monthly"),12,'
                'IF(EXACT({f},"Quarterly"),4,'
                'IF(EXACT({f},"Semi-annual"),2,'
                'IF(EXACT({f},"Annual"),1,1)))))')


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    oid = row_ref("id")
    has_id = f'{oid}=""'
    amount = f"N({row_ref('amount')})"
    freq = row_ref("frequency")
    times = TIMES_A_YEAR.format(f=freq)
    per_month = f"N({row_ref('per_month')})"
    allocated = f'IF(EXACT(TRIM({row_ref("allocated")}),"Yes"),{per_month},0)'
    block_allocated = f"SUM({{allocated_month_first}}:{{allocated_month_last}})"
    hours_recorded = sumifs(other("Labor", "hours"), [])

    cols: List[Any] = [
        id_col("PrefixOverhead", trigger="name", width=11.0),
        text_col("name", "Cost", 34.0,
                 note="Rent, electricity, insurance, a subscription..."),
        list_col("category", "Category", "OverheadCategoryList", 16.0),
        money_col("amount", "Amount", 12.0,
                  note="What one payment is."),
        list_col("frequency", "Paid", "OverheadFrequencyList", 13.0),
        calc_col("times_a_year", "Times a year",
                 f'IF({has_id},"",IF({freq}="",0,{times}))', 11.0, "number1"),
        calc_col("per_month", "A month",
                 f'IF({has_id},"",IF({freq}="",0,{amount}*{times}/12))',
                 12.0, "money"),
        calc_col("per_year", "A year",
                 f'IF({has_id},"",{amount}*{times})', 12.0, "money0"),
        yesno_col("allocated", "In product cost?", 12.0,
                  note="No for costs you would rather keep out of a unit cost."),
        calc_col("allocated_month", "Allocated a month",
                 f'IF({has_id},"",{allocated})', 13.0, "money"),
        calc_col("per_unit", "Per unit",
                 f'IF({has_id},"",IF(UnitsPerMonth<=0,0,'
                 f'{allocated}/UnitsPerMonth))', 11.0, "money4",
                 note="At the units a month on Settings."),
        calc_col("per_hour", "Per hour",
                 f'IF({has_id},"",IF(ProductiveHours<=0,0,'
                 f'{allocated}/ProductiveHours))', 11.0, "money4",
                 note="At the productive hours a month on Settings."),
        calc_col("share_of_total", "Share of overhead",
                 f'IF({has_id},"",IF({block_allocated}=0,"",'
                 f'{allocated}/{block_allocated}))', 12.0, "percent"),
        text_col("provider", "Provider", 20.0),
        date_col("last_paid", "Last paid", 13.0),
        calc_col("next_due", "Next due",
                 f'IF(OR({has_id},{row_ref("last_paid")}="",{freq}=""),"",'
                 f'N({row_ref("last_paid")})+ROUND(365/{times},0))',
                 13.0, "date"),
        calc_col("due_flag", "Due",
                 f'IF({row_ref("next_due")}="","",'
                 f'IF(N({row_ref("next_due")})<TodayDate,"OVERDUE",'
                 f'IF(N({row_ref("next_due")})-TodayDate<=14,"DUE SOON","OK")))',
                 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVERDUE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "DUE SOON", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        wrap_col("notes", "Notes", 32.0),
    ]

    spec_obj = SheetSpec(columns=cols, samples=data, freeze_cols=2,
                         **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                         tab_color=P.accent))
    spec_obj.extra_notes = [
        f"Hours recorded on the Labor tab (all rows): {hours_recorded}",
    ]
    return spec_obj
