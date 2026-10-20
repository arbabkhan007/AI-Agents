"""The Promotions tab - discounts, and what they cost.

A discount is a pricing decision, so it gets costed like one. Each row says
what the offer is, when it runs, what it applies to, and how many times it has
been used. The trading columns read the Sales tab: how many orders quoted the
code, what they brought in, what they earned, and what the margin was with the
discount taken out.

`discount_given` is the money the offer gave away, worked back from the
discounted revenue. `state` says whether the offer is live, still scheduled or
already over, so a code that has ended stops being typed into new orders.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, id_col, int_col, list_col, money_col,
                     other, pct_col, row_ref, samples, spec_defaults, sumifs,
                     text_col, wrap_col, yesno_col, countifs)

P = Palette

NAME = "Promotions"

SUBTITLE = ("Discounts and offers: when they run, what they apply to and what "
            "they did to the margin.")

HELP = ("Type the code, the discount and the dates. The Sales tab records "
        "which code each order used, so the redemptions, the revenue and the "
        "margin with the discount taken out are all counted here.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    pid = row_ref("id")
    has_id = f'{pid}=""'
    code = row_ref("code")
    discount = f"N({row_ref('discount')})"
    start = row_ref("start")
    end = row_ref("end")

    redemptions = countifs([(other("Sales", "promo"), code)])
    revenue = sumifs(other("Sales", "gross"), [(other("Sales", "promo"), code)])
    profit = sumifs(other("Sales", "profit"),
                    [(other("Sales", "promo"), code)])

    cols: List[Any] = [
        id_col("PrefixPromo", trigger="code", width=11.0),
        text_col("code", "Code", 16.0,
                 note="What the customer types. Filling this in starts the row."),
        text_col("name", "Offer", 30.0),
        list_col("type", "Type", "PromoTypeList", 15.0),
        pct_col("discount", "Discount", 11.0,
                note="As a decimal: 0.15 for 15%."),
        money_col("fixed_amount", "Or a fixed amount", 13.0,
                  note="For 'take 10 off' offers - the percentage is ignored "
                       "when this is filled in."),
        date_col("start", "Starts", 13.0),
        date_col("end", "Ends", 13.0),
        calc_col("days_running", "Days running",
                 f'IF(OR({has_id},{start}="",{end}=""),"",'
                 f'N({end})-N({start}))', 11.0, "int"),
        calc_col("state", "State",
                 f'IF({has_id},"",IF({start}="","NO DATES",'
                 f'IF(TodayDate<N({start}),"SCHEDULED",'
                 f'IF(N({end})>0,IF(TodayDate>N({end}),"ENDED","LIVE"),'
                 f'"LIVE"))))', 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LIVE", "fmt": "good"},
                     {"type": "text", "criteria": "containing",
                      "value": "ENDED", "fmt": "muted"},
                     {"type": "text", "criteria": "containing",
                      "value": "SCHEDULED", "fmt": "info"},
                     {"type": "text", "criteria": "containing",
                      "value": "NO DATES", "fmt": "warn"}]),
        yesno_col("active", "Switched on?", 11.0),
        text_col("applies_to", "Applies to", 26.0,
                 note="Product IDs, bundle IDs, or a word like All, "
                      "Wholesale orders."),
        int_col("min_qty", "Minimum qty", 11.0),
        money_col("min_order", "Minimum order", 12.0),
        int_col("max_uses", "Maximum uses", 12.0,
                note="Zero means no limit."),
        int_col("used", "Used (typed)", 11.0,
                note="Your own count - the Sales tab keeps its own below."),
        calc_col("uses_left", "Uses left",
                 f'IF({has_id},"",IF(N({row_ref("max_uses")})=0,"No limit",'
                 f'N({row_ref("max_uses")})-N({row_ref("used")})))', 11.0,
                 "int"),
        calc_col("usage_flag", "Usage check",
                 f'IF({has_id},"",IF(N({row_ref("max_uses")})=0,"",'
                 f'IF(N({row_ref("used")})>=N({row_ref("max_uses")}),'
                 f'"USED UP","OK")))', 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "USED UP", "fmt": "bold_bad"}]),
        calc_col("redemptions", "Orders using it", redemptions, 12.0, "int",
                 note="Counted from the promo code on the Sales tab."),
        calc_col("revenue_with_promo", "Revenue", revenue, 13.0, "money"),
        calc_col("profit_with_promo", "Profit", profit, 13.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_with_promo", "Margin with the discount",
                 f'IF(N({row_ref("revenue_with_promo")})=0,"",'
                 f'N({row_ref("profit_with_promo")})'
                 f'/N({row_ref("revenue_with_promo")}))', 13.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("discount_given", "Discount given away",
                 f'IF(N({row_ref("revenue_with_promo")})=0,"",'
                 f'IF({discount}>=1,"",'
                 f'N({row_ref("revenue_with_promo")})*{discount}'
                 f'/(1-{discount})))', 14.0, "money",
                 note="Worked back from the discounted revenue."),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
