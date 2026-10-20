"""The Channels tab - what each place you sell charges you.

Etsy, your own website, a craft fair, wholesale: every channel has its own fee
structure, and pricing without it is guesswork. Each row carries the listing
fee, the transaction percentage, payment processing, the ad fee and the share
of orders ads actually bring, plus the small regulatory and currency fees.

`total_rate` is the percentage a channel takes, `fee_on_100` shows what that
means on a 100 order, and `ads_effective` is the one the Products tab uses -
the ad percentage times the share of orders that come from ads, which is zero
when ads are switched off. The three trading columns at the right count this
month's orders, revenue and fees straight off the Sales tab, so `effective_rate`
is what the channel really charged rather than what its schedule says.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, int_col, list_col, money_col, other, pct_col,
                     row_ref, samples, spec_defaults, sumifs, text_col,
                     wrap_col, yesno_col)

P = Palette

NAME = "Channels"

SUBTITLE = ("Marketplace and channel fees: what each place you sell really "
            "takes, and what it took this month.")

HELP = ("Keep the fee schedule current - these numbers move. 'Fee on a 100 "
        "order' is the quickest way to compare two channels. Check the "
        "schedule against the effective rate the Sales tab reports; if they "
        "differ, one of them is out of date.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cname = row_ref("name")
    has_name = f'{cname}=""'
    transaction = f"N({row_ref('transaction_pct')})"
    processing = f"N({row_ref('processing_pct')})"
    proc_fixed = f"N({row_ref('processing_fixed')})"
    listing = f"N({row_ref('listing_fee')})"
    regulatory = f"N({row_ref('regulatory_fee')})"
    currency = f"N({row_ref('currency_fee')})"
    ads = f"N({row_ref('ads_effective')})"
    total_rate = f"({transaction}+{processing}+{regulatory}+{currency}+{ads})"
    fee_on_100 = f"(100*{total_rate}+{listing}+{proc_fixed})"

    month_orders = (f'IFERROR(COUNTIFS({other("Sales", "channel")},{cname},'
                    f'{other("Sales", "date")},">="&MonthStart,'
                    f'{other("Sales", "date")},"<="&MonthEnd),0)')
    month_revenue = sumifs(other("Sales", "gross"),
                           [(other("Sales", "channel"), cname),
                            (other("Sales", "date"), '">="&MonthStart'),
                            (other("Sales", "date"), '"<="&MonthEnd')])
    month_fees = sumifs(other("Sales", "fees"),
                        [(other("Sales", "channel"), cname),
                         (other("Sales", "date"), '">="&MonthStart'),
                         (other("Sales", "date"), '"<="&MonthEnd')])

    cols: List[Any] = [
        text_col("name", "Channel", 20.0,
                 note="Must match the channel names used on Products and "
                      "Sales, or the lookups come back empty."),
        list_col("type", "Type", "ChannelTypeList", 15.0),
        money_col("listing_fee", "Listing fee", 11.0,
                  note="Charged once per listing or per order."),
        pct_col("transaction_pct", "Transaction %", 11.0),
        pct_col("processing_pct", "Processing %", 11.0,
                note="Payment processing percentage."),
        money_col("processing_fixed", "Processing fixed", 12.0,
                  note="The flat part of payment processing."),
        pct_col("offsite_ads_pct", "Ad fee %", 11.0,
                note="What the marketplace charges on an order its ads brought."),
        yesno_col("offsite_ads_active", "Ads on?", 9.0),
        calc_col("ads_effective", "Ad fee in use",
                 f'IF({has_name},"",IF(EXACT(TRIM({row_ref("offsite_ads_active")}),'
                 f'"Yes"),N({row_ref("offsite_ads_pct")})*OffsiteAdsShare,0))',
                 11.0, "percent",
                 note="Ad percentage times the share of orders ads bring."),
        pct_col("regulatory_fee", "Regulatory %", 11.0),
        pct_col("currency_fee", "Currency %", 11.0,
                note="Conversion fee on sales in another currency."),
        calc_col("total_rate", "Total rate",
                 f'IF({has_name},"",{total_rate})', 11.0, "percent",
                 note="Every percentage this channel takes."),
        pct_col("shipping_fee_pct", "Fees on postage %", 12.0,
                note="Some marketplaces charge their fee on postage too."),
        yesno_col("fees_on_shipping", "Fees on postage?", 12.0),
        money_col("subscription", "Subscription a month", 13.0),
        int_col("payout_days", "Payout days", 10.0,
                note="How long the money takes to reach the bank."),
        money_col("chargeback_fee", "Chargeback fee", 12.0),
        calc_col("fee_on_100", "Fee on a 100 order",
                 f'IF({has_name},"",{fee_on_100})', 13.0, "money",
                 note="The quickest way to compare two channels."),
        calc_col("net_on_100", "You keep on 100",
                 f'IF({has_name},"",100-{fee_on_100})', 13.0, "money"),
        calc_col("subscription_per_unit", "Subscription a unit",
                 f'IF({has_name},"",IF(UnitsPerMonth<=0,0,'
                 f'N({row_ref("subscription")})/UnitsPerMonth))', 12.0,
                 "money4"),
        calc_col("orders_this_month", "Orders this month", month_orders,
                 12.0, "int"),
        calc_col("revenue_this_month", "Revenue this month", month_revenue,
                 13.0, "money"),
        calc_col("fees_this_month", "Fees this month", month_fees, 13.0,
                 "money"),
        calc_col("effective_rate", "Effective rate",
                 f'IF({has_name},"",IF(N({row_ref("revenue_this_month")})=0,"",'
                 f'N({row_ref("fees_this_month")})'
                 f'/N({row_ref("revenue_this_month")})))', 12.0, "percent",
                 note="What the channel actually charged this month."),
        calc_col("fee_drift", "Fee check",
                 f'IF(OR({has_name},{row_ref("effective_rate")}=""),"",'
                 f'IF(N({row_ref("effective_rate")})>{total_rate}+0.01,'
                 f'"FEES HIGHER THAN SCHEDULE",'
                 f'IF(N({row_ref("effective_rate")})<{total_rate}-0.01,'
                 f'"FEES LOWER - CHECK SCHEDULE","MATCHES")))', 22.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "HIGHER", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "LOWER", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "MATCHES", "fmt": "good"}]),
        calc_col("payout_flag", "Cash lag",
                 f'IF({has_name},"",IF(N({row_ref("payout_days")})>14,'
                 f'"SLOW PAYOUT",IF(N({row_ref("payout_days")})=0,'
                 f'"PAID ON THE DAY","NORMAL")))', 14.0, "status"),
        yesno_col("active", "Selling here?", 11.0),
        text_col("fee_source", "Fee schedule source", 24.0,
                 note="Where you checked these figures, and when."),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=1,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
