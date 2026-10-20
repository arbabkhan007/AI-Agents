"""The Bundles tab - kits, sets and gift boxes.

A bundle is priced here, not guessed: the parts are listed on Bundle Lines, the
list price is what they would cost separately, and the bundle price is what the
customer pays for the set. The tab works out the discount that implies, what
the parts actually cost, the fees the channel takes, and whether the bundle
still clears the target margin.

This is where "a nice little discount" turns out to be a loss. The example shop
has one: a candle and a scarf bundled at 84, where the scarf on its own is
already priced below cost - the flag column says LOSS and the Dashboard lists
it.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (FLAG_LOSS, calc_col, channel_fee_rate,
                     channel_fixed_fee, countifs, date_col, id_col, int_col,
                     list_col, money_col, other, pct_col, price_from,
                     rank_desc, review_flag, row_ref, round_price, samples,
                     spec_defaults, sumifs, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Bundles"

SUBTITLE = ("Kits, sets and gift boxes: what the parts cost, what the bundle "
            "sells for and whether it still makes money.")

HELP = ("Name the bundle, list its parts on the Bundle Lines tab and type the "
        "bundle price. The list price arrives from the parts; the discount, "
        "the fees, the profit and the price your margin asks for are all "
        "calculated here.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    bid = row_ref("id")
    has_id = f'{bid}=""'
    chan = (f'IF({row_ref("channel")}="",DefaultChannel,'
            f'{row_ref("channel")})')
    rate = channel_fee_rate(chan)
    fixed = channel_fixed_fee(chan)
    bundle_price = f"N({row_ref('bundle_price')})"
    cost = (f'N({row_ref("parts_cost")})+N({row_ref("packaging_cost")})'
            f'+N({row_ref("shipping_absorbed")})')
    profit = f'{bundle_price}-({rate}*{bundle_price}+{fixed})-{cost}'
    suggested = price_from(cost, fixed, "TargetRetailMargin", rate)
    wholesale_base = f"{bundle_price}*(1-WholesaleDiscount)"
    products = row_ref("products")

    line_total = sumifs(other("Bundle Lines", "line_total"),
                        [(other("Bundle Lines", "bundle"), bid)])
    line_cost = sumifs(other("Bundle Lines", "line_cost"),
                       [(other("Bundle Lines", "bundle"), bid)])
    line_count = countifs([(other("Bundle Lines", "bundle"), bid)])

    cols: List[Any] = [
        id_col("PrefixBundle", trigger="name", width=11.0),
        text_col("name", "Bundle", 32.0,
                 note="What the set is called. Filling this in starts the row."),
        text_col("products", "Parts (IDs)", 26.0,
                 note="Product IDs separated by commas - a reminder of what "
                      "is in the set. The money comes from Bundle Lines."),
        calc_col("product_count", "Parts listed",
                 f'IF({has_id},"",IF({products}="",0,'
                 f'LEN({products})-LEN(SUBSTITUTE({products},",",""))+1))',
                 11.0, "int"),
        yesno_col("active", "On sale?", 10.0),
        list_col("channel", "Channel", "ChannelList", 15.0),
        calc_col("line_count", "Lines on the tab", line_count, 11.0, "int",
                 note="How many rows the Bundle Lines tab holds for this set."),
        calc_col("list_price", "Parts separately",
                 f'IF({has_id},"",{line_total})', 13.0, "money",
                 note="What the parts would cost bought one at a time."),
        money_col("bundle_price", "Bundle price", 13.0,
                  note="What the customer pays for the set."),
        calc_col("savings_for_customer", "Customer saves",
                 f'IF({has_id},"",N({row_ref("list_price")})-{bundle_price})',
                 13.0, "money"),
        calc_col("discount", "Discount",
                 f'IF({has_id},"",IF(N({row_ref("list_price")})=0,"",'
                 f'1-{bundle_price}/N({row_ref("list_price")})))', 11.0,
                 "percent"),
        calc_col("discount_check", "Discount check",
                 f'IF(OR({has_id},{row_ref("discount")}=""),"",'
                 f'IF(N({row_ref("discount")})>DefaultDiscount*2,'
                 f'"DEEP DISCOUNT",IF(N({row_ref("discount")})<0,'
                 f'"COSTS MORE THAN THE PARTS","OK")))', 20.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "DEEP", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "COSTS MORE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("parts_cost", "Cost of the parts",
                 f'IF({has_id},"",{line_cost})', 13.0, "money",
                 note="What the parts cost you, from the Products tab."),
        money_col("packaging_cost", "Extra packaging", 13.0,
                  note="A gift box or ribbon that only the bundle needs."),
        money_col("shipping_absorbed", "Postage absorbed", 13.0,
                  note="Sets are heavier - type what you pay to send one."),
        calc_col("cost", "Total cost", f'IF({has_id},"",{cost})', 13.0,
                 "money"),
        calc_col("fee_rate", "Channel fee rate",
                 f'IF({has_id},"",{rate})', 11.0, "percent"),
        calc_col("fixed_fees", "Fixed fees",
                 f'IF({has_id},"",{fixed})', 11.0, "money"),
        calc_col("fees", "Fees",
                 f'IF({has_id},"",{rate}*{bundle_price}+{fixed})', 12.0,
                 "money"),
        calc_col("profit", "Profit a bundle",
                 f'IF({has_id},"",IF({bundle_price}=0,"",{profit}))', 13.0,
                 "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({has_id},"",IF({bundle_price}=0,"",{profit}/{bundle_price}))',
                 10.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_flag", "Flag",
                 f'IF({has_id},"",IF({bundle_price}=0,"",'
                 f'IF({profit}<=0,"{FLAG_LOSS}",'
                 f'IF({profit}/{bundle_price}<MarginWarning,"THIN","OK"))))',
                 9.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": FLAG_LOSS, "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "THIN", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("suggested_price", "Suggested bundle price",
                 f'IF({has_id},"",{suggested})', 14.0, "money",
                 note="(cost + fixed fees) / (1 - target margin - fee rate)."),
        calc_col("price_gap", "Gap to suggested",
                 f'IF(OR({has_id},{bundle_price}=0),"",'
                 f'N({row_ref("suggested_price")})-{bundle_price})', 13.0,
                 "money",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "bad"},
                     {"type": "cell", "criteria": "<=", "value": 0,
                      "fmt": "good"}]),
        calc_col("wholesale_price", "Wholesale price",
                 f'IF({has_id},"",{round_price(wholesale_base)})', 13.0,
                 "money",
                 note="The bundle price less the trade discount on Settings."),
        date_col("reviewed", "Last review", 13.0),
        calc_col("next_review", "Next review due",
                 f'IF({row_ref("reviewed")}="","",'
                 f'N({row_ref("reviewed")})+PriceReviewDays)', 13.0, "date"),
        calc_col("review_flag", "Review",
                 review_flag("next_review", "reviewed"), 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVERDUE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "DUE SOON", "fmt": "warn"}]),
        calc_col("rank_margin", "rank margin", rank_desc("margin"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))


def decorate(sheet, fmts, cfg: Config, reg) -> None:
    """Shade a bundle row that loses money."""
    spec_obj = reg[NAME]
    flag = spec_obj.letter("margin_flag")
    first = spec_obj.first_data_row
    last = spec_obj.last_data_row
    sheet.ws.conditional_format(
        first - 1, 0, last - 1, spec_obj.last_col_index,
        {"type": "formula", "criteria": f'${flag}{first}="{FLAG_LOSS}"',
         "format": fmts.cf("bad")})
