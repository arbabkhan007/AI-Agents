"""The Wholesale Customers tab - the shops that buy from you.

One row per retailer: the contact, the trade terms, the discount they get, the
minimum order and the credit limit. Everything else is counted off the Wholesale
Orders tab - how many orders, what they are worth, what is still outstanding,
how long since the last one, and whether the invoices get paid inside the terms.

Two flags matter. `credit_flag` says when the outstanding balance is close to
or over the limit, and `late_flag` says when a shop pays late often enough that
the terms should change. The example shop has one of each: a boutique sitting
at its limit, and a bookshop on hold after two late payments.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec, max_if, min_if
from ..writer import list_from
from ..layout import Col
from .common import (calc_col, countifs, date_col, id_col, list_col, money_col,
                     other, pct_col, rank_desc, row_ref, samples,
                     spec_defaults, sumifs, text_col, wrap_col, yesno_col)

P = Palette

NAME = "Wholesale Customers"

#: what min_if returns when nothing matched - 31 December 9999
NO_DATE = 2958465

SUBTITLE = ("Retailers who buy at trade prices: terms, limits, what they owe "
            "and how they pay.")

HELP = ("One row per shop. The order counts, the lifetime value, the "
        "outstanding balance and the payment record are all counted from the "
        "Wholesale Orders tab.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cid = row_ref("id")
    has_id = f'{cid}=""'
    key = other("Wholesale Orders", "customer")
    totals = other("Wholesale Orders", "order_total")
    dates = other("Wholesale Orders", "date")
    statuses = other("Wholesale Orders", "status")

    orders = countifs([(key, cid)])
    lifetime = sumifs(totals, [(key, cid)])
    paid_total = sumifs(totals, [(key, cid), (statuses, '"Paid"')])
    paid_orders = countifs([(key, cid), (statuses, '"Paid"')])
    first_raw = min_if(dates, f"{key}={cid}")
    last_raw = max_if(dates, f"{key}={cid}")

    cols: List[Any] = [
        id_col("PrefixCustomer", trigger="name", width=11.0),
        text_col("name", "Shop", 30.0,
                 note="Who buys from you. Filling this in starts the row."),
        text_col("contact", "Contact", 20.0),
        text_col("email", "Email", 28.0),
        text_col("phone", "Phone", 16.0),
        wrap_col("address", "Address", 32.0),
        text_col("country", "Country", 14.0),
        list_col("terms", "Terms", "CustomerTermList", 12.0),
        pct_col("discount", "Trade discount", 12.0,
                note="Off your retail price: 0.5 is half price."),
        money_col("min_order", "Minimum order", 13.0),
        money_col("credit_limit", "Credit limit", 13.0),
        yesno_col("tax_exempt", "Tax exempt?", 11.0),
        list_col("status", "Status", "CustomerStatusList", 13.0),
        calc_col("orders_count", "Orders", orders, 9.0, "int"),
        calc_col("lifetime_value", "Lifetime value", lifetime, 13.0, "money"),
        calc_col("avg_order", "Average order",
                 f'IF({has_id},"",IF(N({row_ref("orders_count")})=0,"",'
                 f'N({row_ref("lifetime_value")})'
                 f'/N({row_ref("orders_count")})))', 13.0, "money"),
        calc_col("balance", "Outstanding",
                 f'IF({has_id},"",N({row_ref("lifetime_value")})'
                 f'-{paid_total})', 13.0, "money",
                 note="Everything ordered less everything marked Paid.",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "warn"}]),
        calc_col("credit_used", "Limit used",
                 f'IF({has_id},"",IF(N({row_ref("credit_limit")})=0,"",'
                 f'N({row_ref("balance")})/N({row_ref("credit_limit")})))',
                 11.0, "percent"),
        calc_col("credit_flag", "Credit check",
                 f'IF({has_id},"",IF(N({row_ref("credit_limit")})=0,"NO LIMIT",'
                 f'IF(N({row_ref("balance")})>N({row_ref("credit_limit")}),'
                 f'"OVER THE LIMIT",'
                 f'IF(N({row_ref("balance")})>'
                 f'N({row_ref("credit_limit")})*0.8,"NEAR THE LIMIT","OK"))))',
                 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVER", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "NEAR", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("paid_on_time", "Paid share",
                 f'IF({has_id},"",IF(N({row_ref("orders_count")})=0,"",'
                 f'{paid_orders}/N({row_ref("orders_count")})))', 11.0,
                 "percent", note="Orders marked Paid, of all their orders."),
        calc_col("late_flag", "Payment record",
                 f'IF({has_id},"",IF(N({row_ref("orders_count")})<2,"",'
                 f'IF(N({row_ref("paid_on_time")})<0.8,"LATE PAYER",'
                 f'IF(N({row_ref("paid_on_time")})<1,"SOMETIMES LATE",'
                 f'"PAID UP"))))', 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LATE PAYER", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "SOMETIMES", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "PAID UP", "fmt": "good"}]),
        calc_col("first_raw", "first raw", first_raw, 12.0, "date",
                 hidden=True),
        calc_col("first_order", "First order",
                 f'IF({has_id},"",IF(N({row_ref("first_raw")})>={NO_DATE},"",'
                 f'N({row_ref("first_raw")})))', 13.0, "date"),
        calc_col("last_raw", "last raw", last_raw, 12.0, "date", hidden=True),
        calc_col("last_order", "Last order",
                 f'IF({has_id},"",IF(N({row_ref("last_raw")})=0,"",'
                 f'N({row_ref("last_raw")})))', 13.0, "date"),
        calc_col("days_since_order", "Days since",
                 f'IF({row_ref("last_order")}="","",'
                 f'TodayDate-N({row_ref("last_order")}))', 11.0, "int"),
        calc_col("lapsed_flag", "Relationship",
                 f'IF({row_ref("last_order")}="","",'
                 f'IF(TodayDate-N({row_ref("last_order")})>180,"LAPSED",'
                 f'IF(TodayDate-N({row_ref("last_order")})>90,"QUIET",'
                 f'"ACTIVE")))', 13.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "LAPSED", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "QUIET", "fmt": "info"},
                     {"type": "text", "criteria": "containing",
                      "value": "ACTIVE", "fmt": "good"}]),
        calc_col("rank_value", "rank value", rank_desc("lifetime_value"), 9.0,
                 "int", hidden=True),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))
