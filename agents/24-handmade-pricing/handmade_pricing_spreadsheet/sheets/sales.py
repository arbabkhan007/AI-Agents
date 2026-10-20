"""The Sales tab - the money that actually came in.

One row per order line: what sold, where, how many, at what price, what the
channel took, what the postage cost and what the goods cost. From that comes
the profit and the margin of the sale, and the effective hourly wage behind it
- which is the number that decides whether a product is worth making again.

Refunds and cancellations are handled by the `counts` column rather than by
deleting rows: a refunded sale keeps its cost (the item is gone) but loses its
revenue, so it shows as a loss instead of disappearing. That is what a refund
really does to a month.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from ..writer import list_from
from ..layout import Col
from .common import (calc_col, channel_fee_rate, channel_fixed_fee,
                     channel_lookup, date_col, fetch, id_col, int_col,
                     list_col, money_col, num_col, pct_col, product_col,
                     rank_desc, row_ref, samples, spec_defaults, text_col,
                     wrap_col)

P = Palette

NAME = "Sales"

SUBTITLE = ("Every order: price, fees, postage, cost, profit and what the "
            "hour was worth.")

HELP = ("Pick the product and the date, type the quantity and the price paid. "
        "Everything else is calculated - including the profit and the hourly "
        "wage the order earned. Set the status to Refunded and the row keeps "
        "its cost but loses its revenue, which is what a refund really does.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    sid = row_ref("id")
    has_id = f'{sid}=""'
    product = row_ref("product")
    date = row_ref("date")
    status = row_ref("status")
    qty = f"N({row_ref('qty')})"
    unit_price = f"N({row_ref('unit_price')})"
    discount = f"N({row_ref('discount_pct')})"
    counts = row_ref("counts")

    from_product = (f'IFERROR(INDEX([[Products.channel]],'
                    f'MATCH({product},[[Products.id]],0)),"")')
    chan_raw = (f'IF({row_ref("channel")}="",{from_product},'
                f'{row_ref("channel")})')
    chan = f'IF({chan_raw}="",DefaultChannel,{chan_raw})'
    rate = channel_fee_rate(chan)
    fixed = channel_fixed_fee(chan)
    ship_pct = channel_lookup(chan, "shipping_fee_pct", "0")
    ship_flag = channel_lookup(chan, "fees_on_shipping", "No")
    fees_on_post = (f'IF(EXACT(TRIM({ship_flag}),"Yes"),'
                    f'N({row_ref("shipping_paid")})*{ship_pct},0)')
    gross = f'{qty}*{unit_price}*(1-{discount})'
    unit_cost = fetch("Products", "id", "total_cost", product, "0")
    minutes_used = fetch("Products", "id", "minutes_used", product, "0")

    cols: List[Any] = [
        id_col("PrefixSale", trigger="product", width=11.0),
        date_col("date", "Date", 13.0),
        product_col(),
        calc_col("product_name", "Product",
                 f'IF({product}="","",{fetch("Products", "id", "name", product)})',
                 28.0, "text"),
        calc_col("sku", "SKU",
                 f'IF({product}="","",{fetch("Products", "id", "sku", product)})',
                 14.0, "text"),
        calc_col("craft", "Craft",
                 f'IF({product}="","",{fetch("Products", "id", "craft", product)})',
                 12.0, "text"),
        calc_col("category", "category",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "category", product)})',
                 12.0, "text", hidden=True,
                 note="Hidden - the Reports tab groups the year by category "
                      "with a plain SUMIFS on this column."),
        list_col("channel", "Channel", "ChannelList", 15.0,
                 note="Blank takes the channel from the Products tab."),
        int_col("qty", "Qty", 8.0),
        money_col("unit_price", "Price paid", 12.0,
                  note="What the customer paid for one - after any deal."),
        calc_col("catalog_price", "Catalog price",
                 f'IF({has_id},"",{fetch("Products", "id", "retail_price", product, "0")})',
                 12.0, "money"),
        calc_col("price_check", "Price check",
                 f'IF(OR({has_id},{unit_price}=0),"",'
                 f'IF({unit_price}<N({row_ref("catalog_price")})*0.8,'
                 f'"WELL BELOW LIST",IF({unit_price}>N({row_ref("catalog_price")}),'
                 f'"ABOVE LIST","OK")))', 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "WELL BELOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "ABOVE", "fmt": "good"}]),
        pct_col("discount_pct", "Discount", 10.0,
                note="Taken off this line, as a decimal: 0.15 for 15%."),
        Col(key="promo", header="Promo code", width=14.0, style="text",
            validate=list_from("PromoCodes"),
            note="The code the customer used, if any."),
        calc_col("promo_discount", "Promo discount",
                 f'IF(OR({has_id},{row_ref("promo")}=""),0,'
                 f'{fetch("Promotions", "code", "discount", row_ref("promo"), "0")})',
                 12.0, "percent"),
        calc_col("promo_check", "Promo check",
                 f'IF(OR({has_id},{row_ref("promo")}=""),"",'
                 f'IF(N({fetch("Promotions", "code", "start", row_ref("promo"), "0")})=0,'
                 f'"NO SUCH CODE",'
                 f'IF(N({date})<N({fetch("Promotions", "code", "start", row_ref("promo"), "0")}),'
                 f'"NOT STARTED",'
                 f'IF(N({date})>N({fetch("Promotions", "code", "end", row_ref("promo"), "0")}),'
                 f'"ENDED","IN DATE"))))', 15.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "NO SUCH", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "ENDED", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "IN DATE", "fmt": "good"}]),
        calc_col("counts", "Counts?",
                 f'IF({has_id},"",IF(OR(EXACT(TRIM({status}),"Refunded"),'
                 f'EXACT(TRIM({status}),"Cancelled")),"No","Yes"))', 9.0,
                 "flag",
                 note="Refunded and cancelled rows keep their cost but lose "
                      "their revenue.",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "No", "fmt": "bad"}]),
        calc_col("gross", "Gross",
                 f'IF({has_id},"",IF({counts}="No",0,{gross}))', 12.0, "money"),
        calc_col("fee_rate", "Fee rate", f'IF({has_id},"",{rate})', 10.0,
                 "percent"),
        calc_col("fees_on_postage", "Fees on postage",
                 f'IF({has_id},"",IF({counts}="No",0,{fees_on_post}))',
                 12.0, "money"),
        calc_col("fees", "Fees",
                 f'IF({has_id},"",IF({counts}="No",0,'
                 f'{rate}*N({row_ref("gross")})+{fixed}+{fees_on_post}))',
                 12.0, "money"),
        calc_col("fee_pct", "Fees % of gross",
                 f'IF(N({row_ref("gross")})=0,"",'
                 f'N({row_ref("fees")})/N({row_ref("gross")}))', 11.0,
                 "percent"),
        money_col("shipping_paid", "Postage paid by customer", 13.0),
        money_col("shipping_cost", "Postage it cost you", 13.0),
        calc_col("shipping_gap", "Postage gap",
                 f'IF({has_id},"",N({row_ref("shipping_paid")})'
                 f'-N({row_ref("shipping_cost")}))', 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "warn"}]),
        calc_col("cost", "Cost of goods",
                 f'IF({has_id},"",{qty}*{unit_cost})', 12.0, "money"),
        calc_col("net", "Net revenue",
                 f'IF({has_id},"",IF({counts}="No",0,N({row_ref("gross")})'
                 f'+N({row_ref("shipping_paid")})-N({row_ref("fees")})'
                 f'-N({row_ref("shipping_cost")})))', 12.0, "money"),
        calc_col("profit", "Profit",
                 f'IF({has_id},"",N({row_ref("net")})-N({row_ref("cost")}))',
                 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF(N({row_ref("net")})=0,"",'
                 f'N({row_ref("profit")})/N({row_ref("net")}))', 10.0,
                 "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("margin_flag", "Flag",
                 f'IF({has_id},"",IF(N({row_ref("net")})=0,"",'
                 f'IF(N({row_ref("profit")})<=0,"LOSS",'
                 f'IF(N({row_ref("margin")})<MarginWarning,"THIN","OK"))))',
                 9.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LOSS", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "THIN", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("minutes_total", "Minutes of work",
                 f'IF({has_id},"",{qty}*{minutes_used})', 12.0, "number1"),
        calc_col("effective_hourly", "Hourly earned",
                 f'IF(N({row_ref("minutes_total")})=0,"",'
                 f'N({row_ref("profit")})/(N({row_ref("minutes_total")})/60))',
                 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        list_col("status", "Status", "SaleStatusList", 12.0),
        list_col("payment_method", "Paid by", "PaymentMethodList", 13.0),
        text_col("order_ref", "Order ref", 14.0),
        text_col("customer", "Customer", 20.0,
                 note="A name or a handle - optional, for wholesale and "
                      "repeat buyers."),
        calc_col("month", "Month",
                 f'IF({date}="","",TEXT(N({date}),"yyyy-mm"))', 10.0, "text"),
        calc_col("week_start", "Week beginning",
                 f'IF({date}="","",N({date})-WEEKDAY(N({date}),3))', 12.0,
                 "date", note="Mondays."),
        calc_col("rank_profit", "rank profit", rank_desc("profit"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))


def decorate(sheet, fmts, cfg: Config, reg) -> None:
    """Shade any order that lost money."""
    spec_obj = reg[NAME]
    flag = spec_obj.letter("margin_flag")
    first = spec_obj.first_data_row
    last = spec_obj.last_data_row
    sheet.ws.conditional_format(
        first - 1, 0, last - 1, spec_obj.last_col_index,
        {"type": "formula", "criteria": f'${flag}{first}="LOSS"',
         "format": fmts.cf("bad")})
