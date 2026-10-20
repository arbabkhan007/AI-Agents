"""The Settings tab - every number the rest of the workbook reads.

This is the control room. Nothing else in the workbook carries a hard coded
rate, fee, margin or prefix: they all read a defined name that points at a cell
here. Change your hourly rate here and every craft calculator, every product
cost and every break-even figure moves with it.

A few cells are calculated rather than typed, and they matter:

* ``LaborCostHour`` is the rate you pay yourself plus the payroll burden - the
  honest cost of an hour of your own time;
* ``OverheadMonthly`` totals the allocated rows of the Overhead tab, and
  ``OverheadPerHour`` and ``OverheadPerUnit`` divide it the way the overhead
  method says;
* ``TodayDate`` is TODAY(), so the reminders, the aging and the monthly
  columns follow the calendar rather than the day the file was generated.

The cream cells are yours. The sheet is protected, so the calculated ones
cannot be typed over by accident.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import (ROUNDING_RULES, SALES_CHANNELS, Config, Palette)
from ..writer import SheetWriter, list_from
from .common import (FIRST_ROW, OVERHEAD_METHODS, block, other)

P = Palette

NAME = "Settings"

SUBTITLE = ("Your rates, fees, margins, targets and ID prefixes. Every other "
            "tab reads this one.")

HELP = ("Change a figure here and the whole workbook follows. The cream cells "
        "are yours to type in; the calculated ones are locked.")

#: label -> (name, default, style, validate, help)
BUSINESS: List[Dict[str, Any]] = []

PREFIXES: List[tuple] = [
    ("PrefixProduct", "Products", "P-"),
    ("PrefixMaterial", "Materials", "M-"),
    ("PrefixUsage", "Material Usage", "MU-"),
    ("PrefixLabor", "Labor", "L-"),
    ("PrefixPackaging", "Packaging", "PK-"),
    ("PrefixShipping", "Shipping", "SH-"),
    ("PrefixOverhead", "Overhead", "OH-"),
    ("PrefixBundle", "Bundles", "BN-"),
    ("PrefixBundleLine", "Bundle Lines", "BL-"),
    ("PrefixVariation", "Variations", "VR-"),
    ("PrefixBatch", "Batches", "BT-"),
    ("PrefixSale", "Sales", "SL-"),
    ("PrefixPromo", "Promotions", "PM-"),
    ("PrefixHistory", "Price History", "PH-"),
    ("PrefixCompetitor", "Competitors", "CP-"),
    ("PrefixWaste", "Waste Log", "WL-"),
    ("PrefixDevelopment", "Development", "DV-"),
    ("PrefixEvent", "Events", "EV-"),
    ("PrefixCustomer", "Wholesale Customers", "WC-"),
    ("PrefixOrder", "Wholesale Orders", "WO-"),
    ("PrefixCrochet", "Crochet", "CRO-"),
    ("PrefixJewelry", "Jewelry", "JWL-"),
    ("PrefixCandle", "Candles", "CND-"),
    ("PrefixClothing", "Clothing", "CLO-"),
    ("PrefixWood", "Woodworking", "WDW-"),
    ("PrefixDigital", "Digital", "DIG-"),
]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=False)
    last_col = 9
    sheet.banner(NAME, SUBTITLE, last_col)
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 30.0)
    sheet.set_col(3, 4, 17.0)
    sheet.set_col(5, last_col, 15.0)
    sheet.hide_gridlines(2) if hasattr(sheet, "hide_gridlines") else None
    sheet.ws.hide_gridlines(2)

    r = sheet.note(3, HELP, last_col, height=30)

    def field(row, label, value=None, *, name=None, style="text",
              formula=None, validate=None, help_text=""):
        return sheet.field(row, label, value, label_col=1, value_col=3,
                           style=style, name=name, formula=formula,
                           validate=validate, help_text=help_text,
                           help_col=5)

    # ------------------------------------------------------------- the shop
    r = sheet.section(r, "1. Your shop", last_col)
    shop = cfg.shop
    r = field(r, "Shop name", shop.name, name="ShopName",
              help_text="Printed on the printables and the quote.")
    r = field(r, "Maker / owner", shop.owner, name="ShopOwner")
    r = field(r, "Brand", shop.brand, name="ShopBrand")
    r = field(r, "Email", shop.email, name="ShopEmail")
    r = field(r, "Phone", shop.phone, name="ShopPhone")
    r = field(r, "Address", shop.address, name="ShopAddress")
    r = field(r, "Website", shop.website, name="ShopWebsite")
    r = field(r, "Etsy shop", shop.etsy_shop, name="EtsyShop")
    r = field(r, "Instagram", shop.instagram, name="Instagram")
    r = field(r, "Tagline", shop.tagline, name="Tagline")
    r = field(r, "Tax / registration ID", shop.tax_id, name="TaxID",
              help_text="Goes on the wholesale order form.")
    r += 1

    # ------------------------------------------------------------- the dates
    r = sheet.section(r, "2. Dates", last_col)
    r = field(r, "Today", formula="=TODAY()", name="TodayDate", style="date",
              help_text="Calculated - every reminder and aging column reads "
                        "this.")
    r = field(r, "Report year", formula="=YEAR(TodayDate)", name="ReportYear",
              style="int")
    r = field(r, "This month starts",
              formula="=DATE(YEAR(TodayDate),MONTH(TodayDate),1)",
              name="MonthStart", style="date")
    r = field(r, "This month ends", formula="=EOMONTH(MonthStart,0)",
              name="MonthEnd", style="date")
    r = field(r, "This year starts", formula="=DATE(ReportYear,1,1)",
              name="YearStart", style="date")
    r = field(r, "This year ends", formula="=DATE(ReportYear,12,31)",
              name="YearEnd", style="date")
    r = field(r, "Fee schedule last checked", cfg.today, name="FeesReviewed",
              style="date",
              help_text="Marketplace fees move - put the date you last "
                        "checked them.")
    r = field(r, "Check the fees every (days)", cfg.fee_review_days,
              name="FeeReviewDays", style="int")
    r = field(r, "Fee schedule out of date?",
              formula=('=IF(FeesReviewed="","",'
                       'IF(TodayDate-FeesReviewed>FeeReviewDays,"Yes","No"))'),
              name="FeeStale", style="flag",
              help_text="The Dashboard shows a warning when this says Yes.")
    r += 1

    # -------------------------------------------------------------- labour
    r = sheet.section(r, "3. Your labour", last_col)
    r = field(r, "What you pay yourself an hour", cfg.hourly_rate,
              name="HourlyRate", style="money",
              help_text="The rate the whole workbook costs your time at.")
    r = field(r, "Minimum wage where you are", cfg.minimum_wage,
              name="MinimumWage", style="money",
              help_text="Anything earning less than this gets flagged.")
    r = field(r, "An employee's rate an hour", cfg.employee_rate,
              name="EmployeeRate", style="money")
    r = field(r, "A contractor's rate an hour", cfg.contractor_rate,
              name="ContractorRate", style="money")
    r = field(r, "Payroll burden", cfg.payroll_burden, name="PayrollBurden",
              style="percent",
              help_text="Tax, insurance, holiday pay - as a decimal, 0.12 "
                        "for 12%.")
    r = field(r, "True cost of your hour",
              formula="=HourlyRate*(1+PayrollBurden)", name="LaborCostHour",
              style="money",
              help_text="Calculated - this is what every labour cost uses.")
    r = field(r, "Productive hours a month", cfg.productive_hours,
              name="ProductiveHours", style="number",
              help_text="Hours actually spent making, not admin.")
    r = field(r, "Units made a month", cfg.units_per_month,
              name="UnitsPerMonth", style="int")
    r = field(r, "Default batch size", cfg.default_batch_size,
              name="DefaultBatchSize", style="int",
              help_text="Used when a craft row leaves the batch blank.")
    r = field(r, "Supplies an hour", cfg.supplies_per_hour,
              name="SuppliesPerHour", style="money",
              help_text="Thread, blades, sandpaper, gloves - consumables.")
    r = field(r, "Hourly wage you are aiming at",
              formula="=MAX(HourlyRate,LaborCostHour)", name="TargetHourly",
              style="money")
    r += 1

    # ------------------------------------------------------- waste and costs
    r = sheet.section(r, "4. Defaults for materials and packaging", last_col)
    r = field(r, "Default waste", cfg.default_waste, name="DefaultWaste",
              style="percent",
              help_text="Used when a material's own waste is blank.")
    r = field(r, "Default defect rate", cfg.default_defect_rate,
              name="DefaultDefect", style="percent",
              help_text="What a batch loses to seconds, as a decimal.")
    r = field(r, "Default packaging cost", cfg.default_packaging,
              name="DefaultPackaging", style="money",
              help_text="Used when the Packaging tab has nothing for a product.")
    r = field(r, "Default postage absorbed", cfg.default_shipping,
              name="DefaultShipping", style="money",
              help_text="What you pay towards postage when the Shipping tab "
                        "says nothing.")
    r += 1

    # ------------------------------------------------------------- overhead
    r = sheet.section(r, "5. Overhead", last_col)
    overhead_total = reg["Overhead"]
    allocated = other("Overhead", "allocated_month")
    r = field(r, "How overhead is spread", "Per unit", name="OverheadMethod",
              validate=list_from("OverheadMethodList"),
              help_text="Per unit, per hour, or per month divided by the "
                        "units you make.")
    r = field(r, "Overhead a month",
              formula=f"=IFERROR(SUM({allocated}),0)", name="OverheadMonthly",
              style="money",
              help_text="Calculated - the total of the allocated rows on the "
                        "Overhead tab.")
    r = field(r, "Overhead an hour",
              formula="=IF(ProductiveHours<=0,0,OverheadMonthly/"
                      "ProductiveHours)", name="OverheadPerHour",
              style="money4")
    r = field(r, "Overhead a unit",
              formula="=IF(UnitsPerMonth<=0,0,OverheadMonthly/UnitsPerMonth)",
              name="OverheadPerUnit", style="money4")
    r += 1

    # ---------------------------------------------------------------- fees
    r = sheet.section(r, "6. Marketplace fees", last_col)
    r = field(r, "Default channel", SALES_CHANNELS[0], name="DefaultChannel",
              validate=list_from("ChannelList"),
              help_text="Used when a product or a craft row leaves the "
                        "channel blank.")
    r = field(r, "Listing fee", cfg.listing_fee, name="ListingFee",
              style="money")
    r = field(r, "Transaction fee", cfg.transaction_fee,
              name="TransactionFee", style="percent",
              help_text="As a decimal: 0.065 for 6.5%.")
    r = field(r, "Processing percentage", cfg.processing_percent,
              name="ProcessingPercent", style="percent")
    r = field(r, "Processing fixed", cfg.processing_fixed,
              name="ProcessingFixed", style="money")
    r = field(r, "Offsite ad fee", cfg.offsite_ads_fee, name="OffsiteAdsFee",
              style="percent")
    r = field(r, "Share of orders ads bring", cfg.offsite_ads_share,
              name="OffsiteAdsShare", style="percent",
              help_text="The ad fee only applies to those orders.")
    r = field(r, "Regulatory fee", cfg.regulatory_fee, name="RegulatoryFee",
              style="percent")
    r = field(r, "Currency conversion fee", cfg.currency_fee,
              name="CurrencyFee", style="percent")
    r = field(r, "Fees charged on postage too?", cfg.fees_include_shipping,
              name="FeesOnShipping", validate=list_from("YesNoList"))
    r = field(r, "Fees charged on tax?", cfg.fees_include_tax,
              name="FeesIncludeTax", validate=list_from("YesNoList"))
    r = field(r, "Total default fee rate",
              formula="=TransactionFee+ProcessingPercent+RegulatoryFee"
                      "+CurrencyFee+OffsiteAdsFee*OffsiteAdsShare",
              name="DefaultFeeRate", style="percent",
              help_text="Calculated - the Channels tab carries the real "
                        "figures per channel.")
    r += 1

    # -------------------------------------------------------------- pricing
    r = sheet.section(r, "7. Pricing rules", last_col)
    r = field(r, "Target retail margin", cfg.target_retail_margin,
              name="TargetRetailMargin", style="percent",
              help_text="What you want left after cost and fees, as a "
                        "decimal: 0.30 for 30%.")
    r = field(r, "Target wholesale margin", cfg.target_wholesale_margin,
              name="TargetWholesaleMargin", style="percent")
    r = field(r, "Default markup", cfg.default_markup, name="DefaultMarkup",
              style="number",
              help_text="Cost times this, when a markup is used instead of a "
                        "margin.")
    r = field(r, "Wholesale discount", cfg.wholesale_discount,
              name="WholesaleDiscount", style="percent",
              help_text="Off retail: 0.40 means trade buys at 60%.")
    r = field(r, "Margin warning below", cfg.margin_warning,
              name="MarginWarning", style="percent",
              help_text="Anything under this is flagged THIN.")
    r = field(r, "How prices are rounded", cfg.rounding_rule,
              name="RoundingRule", validate=list_from("RoundingList"),
              help_text="Applied to every calculated price in the workbook.")
    r = field(r, "Default discount", cfg.default_discount,
              name="DefaultDiscount", style="percent")
    r = field(r, "Sales tax / VAT rate", cfg.tax_rate, name="TaxRate",
              style="percent",
              help_text="Added on the printables, not to your margin.")
    r = field(r, "Minimum wholesale quantity", cfg.minimum_order_qty,
              name="MinOrderQty", style="int")
    r = field(r, "Minimum wholesale order", cfg.minimum_order_value,
              name="MinOrderValue", style="money")
    r = field(r, "Review a price every (days)", cfg.price_review_days,
              name="PriceReviewDays", style="int")
    r = field(r, "Low stock warning (days)", cfg.low_stock_days,
              name="LowStockDays", style="int")
    r += 1

    # -------------------------------------------------------------- targets
    r = sheet.section(r, "8. Targets the Dashboard measures against", last_col)
    r = field(r, "Revenue a month", cfg.revenue_target_month,
              name="MonthlyRevenueTarget", style="money")
    r = field(r, "Revenue a year", cfg.revenue_target_year,
              name="AnnualRevenueTarget", style="money")
    r = field(r, "Profit a month", cfg.profit_target_month,
              name="MonthlyProfitTarget", style="money")
    r = field(r, "Revenue needed a productive hour",
              formula="=IF(ProductiveHours<=0,0,MonthlyRevenueTarget/"
                      "ProductiveHours)", name="RevenuePerHourTarget",
              style="money")
    r += 1

    # ------------------------------------------------------------- prefixes
    r = sheet.section(r, "9. ID prefixes", last_col)
    r = sheet.note(r, "Every register numbers itself with the prefix below, "
                      "so an ID tells you which tab it came from.", last_col,
                   height=26)
    for name, tab, prefix in PREFIXES:
        r = field(r, f"{tab} prefix", prefix, name=name,
                  help_text=f"Used by the {tab} tab.")
    r += 1

    r = sheet.section(r, "How the price is worked out", last_col)
    for line in [
        "Total unit cost = materials + labour + packaging + postage you "
        "absorb + a share of overhead.",
        "Labour = minutes / 60 x the true cost of your hour (your rate plus "
        "the payroll burden).",
        "Suggested price = (total cost + fixed fees) / (1 - target margin - "
        "channel fee rate), then rounded the way you chose above.",
        "Wholesale price = retail price less the trade discount, rounded the "
        "same way.",
        "Profit = price - fees - total cost. Margin = profit / price.",
    ]:
        r = sheet.note(r, line, last_col, height=17, boxed=False)

    sheet.ws.freeze_panes(4, 0)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet
