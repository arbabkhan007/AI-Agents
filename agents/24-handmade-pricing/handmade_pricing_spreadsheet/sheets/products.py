"""The Products tab - the catalog and the heart of the workbook.

One row per product. Everything else feeds into it:

* material cost from the bill of materials, or from the product's craft tab if
  it was costed there (never both - the craft figure wins);
* labour, from the minutes recorded here or on the craft tab, at the rate on
  Settings with payroll on-costs added;
* packaging and the postage the seller absorbs, matched by product ID;
* overhead, spread the way Settings says (per unit, per hour, or per month);
* the marketplace fees for the channel the product sells through.

Out of that comes the price the model asks for::

    price = (cost + fixed fees) / (1 - target margin - fee rate)

and, next to it, what the current price actually earns - profit, margin, an
effective hourly wage and a flag when that wage falls below the minimum on
Settings. The three hidden columns at the far right rank the catalog so the
Dashboard and the Reports can pull a top five without an array formula.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (FLAG_LOSS, calc_col, channel_fee_rate, channel_fixed_fee,
                     channel_lookup, countifs, craft_material_total,
                     craft_minutes_total, date_col, hourly_flag, id_col,
                     int_col, link_col, list_col, margin_flag, money_col,
                     num_col, other, overhead_per_unit, pct_col, price_from,
                     rank_desc, rank_flag, review_flag, row_ref, round_price,
                     samples,
                     spec_defaults, sumifs, sumifs_wild, text_col, wrap_col,
                     yesno_col)

P = Palette

NAME = "Products"

SUBTITLE = ("Every product, what it costs to make and what it should sell "
            "for. Cream cells are yours; the rest is calculated.")

HELP = ("Add a product name and the ID numbers itself. Costs arrive from the "
        "bills of materials, the craft tabs, Packaging, Shipping and "
        "Overhead. Compare 'Suggested price' with 'Retail price' - a gap "
        "means the listing is earning less than the target margin asks for.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    pid = row_ref("id")
    has_id = f'{pid}=""'
    chan = f'IF({row_ref("channel")}="",DefaultChannel,{row_ref("channel")})'
    retail = f"N({row_ref('retail_price')})"
    minutes = f"N({row_ref('minutes_used')})"
    hours = f"({minutes}/60)"

    # where the cost of materials comes from
    bom = sumifs(other("Material Usage", "cost"),
                 [(other("Material Usage", "product"), pid)])
    craft_cost = craft_material_total(pid)
    craft_minutes = craft_minutes_total(pid)
    pack_specific = sumifs_wild(other("Packaging", "cost"),
                                other("Packaging", "products"), "id")
    pack_all = sumifs(other("Packaging", "cost"),
                      [(other("Packaging", "products"), '"All"')])
    ship_absorbed = sumifs_wild(other("Shipping", "absorbed"),
                                other("Shipping", "products"), "id")

    sales_qty = sumifs(other("Sales", "qty"), [(other("Sales", "product"), pid)])
    refunded = sumifs(other("Sales", "qty"),
                      [(other("Sales", "product"), pid),
                       (other("Sales", "status"), '"Refunded"')])
    revenue = sumifs(other("Sales", "gross"),
                     [(other("Sales", "product"), pid)])
    sale_profit = sumifs(other("Sales", "profit"),
                         [(other("Sales", "product"), pid)])
    last_sale = (f"SUMPRODUCT(MAX(({other('Sales', 'product')}={pid})"
                 f"*{other('Sales', 'date')}))")
    made = sumifs(other("Batches", "qty_done"),
                  [(other("Batches", "product"), pid)])
    defects = sumifs(other("Batches", "qty_defect"),
                     [(other("Batches", "product"), pid)])
    wasted = sumifs(other("Waste Log", "cost"),
                    [(other("Waste Log", "product"), pid)])

    # the pricing model, written out once so the column below stays readable
    cost_ref = f"N({row_ref('total_cost')})"
    fixed_ref = f"N({row_ref('fixed_fees')})"
    rate_ref = f"N({row_ref('fee_rate')})"
    margin_ref = (f'IF({row_ref("target_margin")}="",TargetRetailMargin,'
                  f'N({row_ref("target_margin")}))')
    suggested = price_from(cost_ref, fixed_ref, margin_ref, rate_ref)
    data_bar = {"type": "data_bar", "bar_color": P.primary_mid}

    cols: List[Any] = [
        id_col("PrefixProduct", trigger="name", width=11.0,
               note="Numbers itself from the prefix on Settings."),
        text_col("name", "Product name", 36.0,
                 note="The name you use for it. Filling this in starts the row."),
        text_col("sku", "SKU", 14.0, note="Your own stock code."),
        list_col("category", "Category", "CategoryList", 20.0,
                 note="Used by the Reports tab to group sales."),
        list_col("craft", "Craft", "CraftList", 13.0,
                 note="Which of the six craft calculators costed this item."),
        list_col("status", "Status", "StatusList", 13.0),
        calc_col("active", "Sellable?",
                 f'IF({row_ref("status")}="","",'
                 f'IF(OR({row_ref("status")}="Active",'
                 f'{row_ref("status")}="Made to order",'
                 f'{row_ref("status")}="Seasonal"),"Yes","No"))',
                 9.0, "flag", note="Active, made to order or seasonal.",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "Yes", "fmt": "good"},
                     {"type": "text", "criteria": "containing",
                      "value": "No", "fmt": "muted"}]),
        list_col("channel", "Main channel", "ChannelList", 15.0,
                 note="Fees for this channel come from the Channels tab."),
        yesno_col("featured", "Featured", 9.0),
        list_col("season", "Season", "SeasonList", 14.0),
        list_col("size", "Size", "SizeList", 11.0),
        text_col("dimensions", "Dimensions", 18.0),
        num_col("weight_oz", "Weight (oz)", 10.0,
                note="Packed weight - the Shipping tab prices by weight."),
        list_col("difficulty", "Difficulty", "DifficultyList", 12.0,
                 note="The craft tabs multiply time by the factor on Lists."),
        int_col("lead_days", "Lead days", 9.0,
                note="How long from order to dispatch."),
        date_col("created", "Created", 13.0),
        date_col("reviewed", "Last price review", 13.0,
                 note="The last time this price was looked at."),
        calc_col("next_review", "Next review due",
                 f'IF({row_ref("reviewed")}="","",'
                 f'N({row_ref("reviewed")})+PriceReviewDays)',
                 13.0, "date", note="Last review plus the window on Settings."),
        calc_col("review_flag", "Review",
                 review_flag("next_review", "reviewed"), 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "OVERDUE", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "DUE SOON", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),

        # ------------------------------------------------------------ costs
        calc_col("bom_cost", "BOM material cost", bom, 12.0, "money",
                 note="Sum of the bill of materials on Material Usage."),
        calc_col("craft_cost", "Craft tab material cost", craft_cost, 12.0,
                 "money", note="Sum of the six craft calculators."),
        calc_col("material_cost", "Material cost",
                 f'IF({has_id},"",IF(N({row_ref("craft_cost")})>0,'
                 f'N({row_ref("craft_cost")}),N({row_ref("bom_cost")})))',
                 12.0, "money",
                 note="The craft figure wins, so nothing is counted twice."),
        calc_col("craft_minutes", "Craft minutes", craft_minutes, 11.0,
                 "number1", note="Minutes recorded on the craft tabs."),
        int_col("labor_minutes", "Minutes (typed)", 11.0,
                note="Only used when the craft tabs say nothing."),
        calc_col("minutes_used", "Minutes used",
                 f'IF({has_id},"",IF(N({row_ref("craft_minutes")})>0,'
                 f'N({row_ref("craft_minutes")}),N({row_ref("labor_minutes")})))',
                 11.0, "number1"),
        calc_col("hours_used", "Hours", f'IF({has_id},"",{minutes}/60)',
                 9.0, "number"),
        calc_col("hourly_rate", "Rate an hour",
                 f'IF({has_id},"",LaborCostHour)', 11.0, "money",
                 note="Your rate on Settings plus payroll on-costs."),
        calc_col("labor_cost", "Labour cost",
                 f'IF({has_id},"",{minutes}/60*LaborCostHour)', 12.0, "money"),
        calc_col("packaging_cost", "Packaging cost",
                 f'IF({has_id},"",IF(N({pack_specific})+N({pack_all})>0,'
                 f'N({pack_specific})+N({pack_all}),DefaultPackaging))',
                 12.0, "money",
                 note="Matched from the Packaging tab, or the default."),
        calc_col("shipping_cost", "Postage absorbed",
                 f'IF({has_id},"",IF(N({ship_absorbed})>0,'
                 f'N({ship_absorbed}),DefaultShipping))', 12.0, "money",
                 note="The part of the postage you pay, not the customer."),
        calc_col("overhead_cost", "Overhead share",
                 f'IF({has_id},"",{overhead_per_unit(minutes, "1")})',
                 12.0, "money"),
        calc_col("total_cost", "Total unit cost",
                 f'IF({has_id},"",N({row_ref("material_cost")})'
                 f'+N({row_ref("labor_cost")})+N({row_ref("packaging_cost")})'
                 f'+N({row_ref("shipping_cost")})'
                 f'+N({row_ref("overhead_cost")}))',
                 13.0, "money",
                 note="Materials + labour + packaging + absorbed postage + "
                      "overhead.",
                 cf=[data_bar]),

        # ------------------------------------------------------------- fees
        pct_col("target_margin", "Target margin", 11.0,
                note="Blank uses the default on Settings."),
        calc_col("fee_rate", "Channel fee rate",
                 f'IF({has_id},"",{channel_fee_rate(chan)})', 11.0, "percent",
                 note="Every percentage this channel takes."),
        calc_col("fixed_fees", "Fixed fees",
                 f'IF({has_id},"",{channel_fixed_fee(chan)})', 11.0, "money",
                 note="Listing fee plus the fixed part of processing."),
        calc_col("listing_fee", "Listing fee",
                 f'IF({has_id},"",{channel_lookup(chan, "listing_fee", "ListingFee")})',
                 10.0, "money"),
        calc_col("transaction_fee", "Transaction fee",
                 f'IF({has_id},"",{retail}*'
                 f'{channel_lookup(chan, "transaction_pct", "TransactionFee")})',
                 11.0, "money"),
        calc_col("processing_fee", "Processing fee",
                 f'IF({has_id},"",{retail}*'
                 f'{channel_lookup(chan, "processing_pct", "ProcessingPercent")}'
                 f'+{channel_lookup(chan, "processing_fixed", "ProcessingFixed")})',
                 11.0, "money"),
        calc_col("ads_fee", "Offsite ads",
                 f'IF({has_id},"",{retail}*'
                 f'{channel_lookup(chan, "ads_effective", "0")})',
                 11.0, "money",
                 note="Ad fee times the share of orders ads bring."),
        calc_col("total_fees", "Total fees",
                 f'IF({has_id},"",N({row_ref("listing_fee")})'
                 f'+N({row_ref("transaction_fee")})'
                 f'+N({row_ref("processing_fee")})+N({row_ref("ads_fee")}))',
                 11.0, "money"),
        calc_col("fee_pct", "Fees % of price",
                 f'IF({retail}=0,"",N({row_ref("total_fees")})/{retail})',
                 10.0, "percent"),

        # ----------------------------------------------------------- pricing
        money_col("retail_price", "Retail price", 12.0,
                  note="What it sells for today."),
        calc_col("net_revenue", "Net revenue",
                 f'IF({row_ref("retail_price")}="","",'
                 f'{retail}-N({row_ref("total_fees")}))', 12.0, "money",
                 note="Price after every fee."),
        calc_col("suggested_price", "Suggested price",
                 f'IF({has_id},"",{suggested})',
                 13.0, "money",
                 note="(cost + fixed fees) / (1 - target margin - fee rate), "
                      "rounded the way Settings says."),
        calc_col("price_gap", "Gap to suggested",
                 f'IF(OR({row_ref("retail_price")}="",'
                 f'{row_ref("suggested_price")}=""),"",'
                 f'N({row_ref("suggested_price")})-N({row_ref("retail_price")}))',
                 12.0, "money",
                 note="Positive means the price is below what the model asks.",
                 cf=[{"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "bad"},
                     {"type": "cell", "criteria": "<=", "value": 0,
                      "fmt": "good"}]),
        calc_col("profit", "Profit a unit",
                 f'IF({row_ref("retail_price")}="","",'
                 f'N({row_ref("net_revenue")})-N({row_ref("total_cost")}))',
                 12.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "cell", "criteria": ">=", "value": 0,
                      "fmt": "good"}]),
        calc_col("margin", "Margin",
                 f'IF({retail}=0,"",(N({row_ref("net_revenue")})'
                 f'-N({row_ref("total_cost")}))/{retail})', 10.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"},
                     {"type": "formula",
                      "criteria": f"AND({row_ref('margin')}<>\"\","
                                  f"{row_ref('margin')}<MarginWarning)",
                      "fmt": "warn"}]),
        calc_col("margin_flag", "Flag",
                 margin_flag(row_ref("margin"), row_ref("profit"),
                             row_ref("retail_price")), 9.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": FLAG_LOSS, "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "THIN", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        calc_col("effective_hourly", "Effective hourly",
                 f'IF({minutes}=0,"",N({row_ref("profit")})/{hours})',
                 12.0, "money", note="What an hour of making this earns."),
        calc_col("hourly_flag", "Wage check",
                 hourly_flag(row_ref("effective_hourly"),
                             row_ref("minutes_used")), 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "PAYING TO WORK", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "GOOD", "fmt": "good"}]),
        calc_col("price_per_hour", "Price an hour of work",
                 f'IF({minutes}=0,"",{retail}/{hours})', 12.0, "money"),
        calc_col("wholesale_price", "Wholesale price",
                 f'IF({row_ref("retail_price")}="","",'
                 f'{round_price(f"{retail}*(1-WholesaleDiscount)")})',
                 12.0, "money",
                 note="Retail less the trade discount on Settings."),
        calc_col("wholesale_margin", "Wholesale margin",
                 f'IF(N({row_ref("wholesale_price")})=0,"",'
                 f'(N({row_ref("wholesale_price")})'
                 f'-N({row_ref("total_cost")}))'
                 f'/N({row_ref("wholesale_price")}))', 11.0, "percent",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        money_col("msrp", "RRP / MSRP", 12.0),
        calc_col("msrp_check", "RRP check",
                 f'IF(OR({row_ref("msrp")}="",'
                 f'{row_ref("retail_price")}=""),"",'
                 f'IF(N({row_ref("msrp")})<{retail},'
                 f'"RRP BELOW RETAIL","OK"))', 15.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "bad"}]),

        # ------------------------------------------------------------ trading
        calc_col("units_sold", "Units sold", sales_qty, 10.0, "int"),
        calc_col("units_refunded", "Refunded", refunded, 10.0, "int"),
        calc_col("revenue", "Revenue", revenue, 13.0, "money"),
        calc_col("gross_profit", "Gross profit", sale_profit, 13.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "bold_bad"}]),
        calc_col("avg_price", "Average selling price",
                 f'IF(N({row_ref("units_sold")})=0,"",'
                 f'N({row_ref("revenue")})/N({row_ref("units_sold")}))',
                 12.0, "money"),
        calc_col("units_made", "Units made", made, 10.0, "int"),
        calc_col("units_defect", "Defects", defects, 9.0, "int"),
        calc_col("stock_left", "Stock left",
                 f'IF({has_id},"",N({row_ref("units_made")})'
                 f'-N({row_ref("units_sold")}))', 10.0, "int",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "warn"}]),
        calc_col("last_sale", "Last sale",
                 f'IF({has_id},"",IF(N({last_sale})=0,"",N({last_sale})))',
                 13.0, "date"),
        calc_col("days_since_sale", "Days since sale",
                 f'IF({row_ref("last_sale")}="","",'
                 f'TodayDate-N({row_ref("last_sale")}))', 11.0, "int",
                 cf=[{"type": "cell", "criteria": ">", "value": 90,
                      "fmt": "warn"}]),
        calc_col("waste_cost", "Waste cost", wasted, 11.0, "money"),
        text_col("batch_id", "Last batch", 12.0,
                 note="Optional - the Batches tab tracks batches itself."),

        # ------------------------------------------------------------- ranks
        calc_col("rank_margin", "rank margin", rank_desc("margin"), 9.0,
                 "int", hidden=True),
        calc_col("rank_revenue", "rank revenue", rank_desc("revenue"), 9.0,
                 "int", hidden=True),
        calc_col("rank_profit", "rank profit", rank_desc("gross_profit"), 9.0,
                 "int", hidden=True),
        calc_col("rank_loss", "rank loss", rank_flag("margin_flag", FLAG_LOSS),
                 9.0, "int", hidden=True,
                 note="Hidden - the Dashboard lists loss making products "
                      "from this."),
        calc_col("rank_review", "rank review",
                 rank_flag("review_flag", "OVERDUE"), 9.0, "int", hidden=True,
                 note="Hidden - the Dashboard lists overdue price reviews "
                      "from this."),

        # -------------------------------------------------------------- text
        wrap_col("notes", "Notes", 34.0),
        wrap_col("tags", "Tags / keywords", 28.0,
                 note="Comma separated - used for listing copy."),
        text_col("photo", "Photo file", 18.0),
        link_col("url", "Listing URL", 26.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=3,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary))


def decorate(sheet, fmts, cfg: Config, reg) -> None:
    """Shade any row that is losing money, from the ID to the URL."""
    spec = reg[NAME]
    flag = spec.letter("margin_flag")
    first = spec.first_data_row
    last = spec.last_data_row
    sheet.ws.conditional_format(
        first - 1, 0, last - 1, spec.last_col_index,
        {"type": "formula", "criteria": f'${flag}{first}="{FLAG_LOSS}"',
         "format": fmts.cf("bad")})
