"""The Price History tab - every price change, and what happened next.

One row per change: the old price, the new one, why it moved, what the product
cost at the time, and how many sold afterwards. The margin before and after
are recalculated with the channel's fees, so a rise that looks small on the
listing can be worth a lot on the profit line - and a "sale" that looks
harmless can put the product under water.

This is the tab that settles arguments with yourself. The example shop has the
two useful cases in it: a candle that went up twice with no drop in sales, and
a scarf that was discounted to clear and lost more money for the privilege.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, channel_fee_rate, channel_fixed_fee, date_col,
                     fetch, id_col, int_col, list_col, money_col,
                     product_col, raw_price_col, round_ref, row_ref, samples,
                     spec_defaults, wrap_col)

P = Palette

NAME = "Price History"

SUBTITLE = ("Every price change: what it was, what it became, why, and what "
            "it did to the margin.")

HELP = ("One row per change. Type the old price, the new one, why it moved "
        "and what the product cost at the time - the margins either side are "
        "calculated with the channel fees, and so is the price the target "
        "margin would have asked for.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    hid = row_ref("id")
    has_id = f'{hid}=""'
    product = row_ref("product")
    old_price = f"N({row_ref('old_price')})"
    new_price = f"N({row_ref('new_price')})"
    cost_then = f"N({row_ref('cost_at_time')})"
    units_after = f"N({row_ref('units_after')})"

    from_product = (f'IFERROR(INDEX([[Products.channel]],'
                    f'MATCH({product},[[Products.id]],0)),"")')
    chan = f'IF({from_product}="",DefaultChannel,{from_product})'
    rate = channel_fee_rate(chan)
    fixed = channel_fixed_fee(chan)
    minutes = fetch("Products", "id", "minutes_used", product, "0")

    profit_after = f'{new_price}-({rate}*{new_price}+{fixed})-{cost_then}'
    profit_before = f'{old_price}-({rate}*{old_price}+{fixed})-{cost_then}'

    cols: List[Any] = [
        id_col("PrefixHistory", trigger="product", width=11.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",{fetch("Products", "id", "name", product)})',
                 28.0, "text"),
        date_col("date", "Date changed", 13.0),
        money_col("old_price", "Old price", 12.0),
        money_col("new_price", "New price", 12.0),
        calc_col("change", "Change",
                 f'IF({has_id},"",{new_price}-{old_price})', 11.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bad"},
                     {"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "good"}]),
        calc_col("change_pct", "Change %",
                 f'IF({has_id},"",IF({old_price}=0,"",'
                 f'({new_price}-{old_price})/{old_price}))', 11.0, "percent"),
        calc_col("direction", "Direction",
                 f'IF({has_id},"",IF({new_price}>{old_price},"UP",'
                 f'IF({new_price}<{old_price},"DOWN","UNCHANGED")))',
                 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "UP", "fmt": "good"},
                     {"type": "text", "criteria": "containing",
                      "value": "DOWN", "fmt": "warn"}]),
        list_col("reason", "Why", "PriceReasonList", 17.0),
        money_col("cost_at_time", "Cost at the time", 13.0,
                  note="What one item cost when the price changed - not what "
                       "it costs now."),
        calc_col("fee_rate", "Fee rate then", f'IF({has_id},"",{rate})',
                 11.0, "percent",
                 note="Today's rate for this channel - fees are not stored "
                      "per change."),
        calc_col("profit_before", "Profit before",
                 f'IF({has_id},"",IF({old_price}=0,"",{profit_before}))',
                 12.0, "money"),
        calc_col("margin_before", "Margin before",
                 f'IF({has_id},"",IF({old_price}=0,"",'
                 f'{profit_before}/{old_price}))', 12.0, "percent"),
        calc_col("profit_after", "Profit after",
                 f'IF({has_id},"",IF({new_price}=0,"",{profit_after}))',
                 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_after", "Margin after",
                 f'IF({has_id},"",IF({new_price}=0,"",'
                 f'{profit_after}/{new_price}))', 12.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_change", "Margin change",
                 f'IF(OR({has_id},{row_ref("margin_before")}="",'
                 f'{row_ref("margin_after")}=""),"",'
                 f'N({row_ref("margin_after")})-N({row_ref("margin_before")}))',
                 12.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bad"},
                     {"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "good"}]),
        int_col("units_after", "Units sold since", 12.0,
                note="How many sold at the new price."),
        calc_col("revenue_after", "Revenue since",
                 f'IF({has_id},"",{units_after}*{new_price})', 13.0, "money"),
        calc_col("profit_since", "Profit since",
                 f'IF({has_id},"",{units_after}*IF({new_price}=0,0,{profit_after}))',
                 13.0, "money"),
        calc_col("hourly_after", "Hourly since",
                 f'IF({has_id},"",IF(N({minutes})=0,"",{profit_after}'
                 f'/(N({minutes})/60)))', 12.0, "money"),
        # the unrounded model price gets its own hidden cell: the rounding
        # rule repeats its argument eight times, and eight copies of this
        # expression pass Excel's 8,192 character formula limit
        raw_price_col(cost_then, fixed, "TargetRetailMargin", rate,
                      guard=has_id),
        calc_col("suggested_now", "Model price at that cost",
                 f'IF({has_id},"",{round_ref(row_ref("price_raw"))})',
                 14.0, "money",
                 note="(cost + fixed fees) / (1 - target margin - fee rate) "
                      "at the cost recorded on this row."),
        calc_col("gap_to_suggested", "Gap to model",
                 f'IF(OR({has_id},{new_price}=0),"",'
                 f'N({row_ref("suggested_now")})-{new_price})', 13.0, "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "bad"}]),
        calc_col("flag", "Flag",
                 f'IF(OR({has_id},{row_ref("margin_after")}=""),"",'
                 f'IF(N({row_ref("profit_after")})<=0,"LOSS",'
                 f'IF(N({row_ref("margin_after")})<MarginWarning,"THIN","OK")))',
                 9.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOSS", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "THIN", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
