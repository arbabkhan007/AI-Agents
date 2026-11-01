"""`Settings & Lists` - every number and every list the workbook runs on.

Nothing in this file is hard coded to one country, one currency or one
way of selling. Your price tiers, your lead times, your safety stock,
your marketplace fee rates, your minimum acceptable margin and all
forty-odd drop-downs are set here, once, and every other tab follows.

Two groups of settings deserve a second look before you start.

The ID prefixes decide what your Product IDs, Purchase Order numbers
and Order IDs look like. Change them before you have typed three
hundred products, not after.

The fee rates decide whether your profit figures are true. A
marketplace taking 6.5% and a payment processor taking 2.9% plus a
fixed charge are the difference between a healthy margin and a
hobby, and the defaults here are only a starting point - put your
own in.
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Tuple

from ..config import (CATEGORIES, COSTING_NOTE, CUSTOMER_TIERS,
                      DISCLAIMER, EXPENSE_CATEGORIES, HONESTY_NOTE,
                      ID_PREFIX_FIELDS, MONTH_NAMES, MOVEMENT_TYPES,
                      ORDER_STATUSES, PAYMENT_TERMS, PO_STATUSES,
                      PRICE_TIERS, PRIVACY_NOTE, RESERVED_NOTE,
                      RETURN_CONDITIONS, RETURN_REASONS,
                      SALES_CHANNELS, STOCK_CATEGORIES, STOCK_NOTE,
                      TAX_CATEGORIES, UNITS, Config, Palette)
from ..layout import Registry, col_letter, dynamic_name, quote_sheet
from ..writer import SheetWriter, list_from, number_check

NAME = "Settings & Lists"
LAST_COL = 11

# ---------------------------------------------------------------------------
# lists the config does not already carry, defined where they are used
# ---------------------------------------------------------------------------

YES_NO = ["Yes", "No"]

PRODUCT_STATUSES = ["Active", "Seasonal", "Clearance", "Pre-order",
                    "Out of production", "Discontinued", "Draft"]

SUPPLIER_TYPES = ["Manufacturer", "Wholesaler", "Distributor",
                  "Importer", "Maker / artisan", "Printer",
                  "Packaging supplier", "Dropshipper",
                  "Local retailer", "Other"]

SUPPLIER_STATUSES = ["Active", "Preferred", "Occasional", "Trial",
                     "On hold", "Inactive"]

DELIVERY_CONDITIONS = ["Good", "Minor damage", "Damaged",
                       "Short delivery", "Over delivery",
                       "Wrong items", "Rejected"]

CUSTOMER_TYPES = ["Independent boutique", "Gift shop", "Garden centre",
                  "Department store", "Online retailer",
                  "Marketplace seller", "Subscription box",
                  "Cafe or restaurant", "Hotel or B&B", "Museum shop",
                  "Distributor", "Corporate buyer", "Other"]

CUSTOMER_STATUSES = ["Prospect", "Active", "Occasional", "Lapsed",
                     "On hold", "Closed"]

LEAD_SOURCES = ["Trade show", "Instagram", "Faire or marketplace",
                "Website enquiry", "Cold outreach", "Referral",
                "Existing retail customer", "Sales agent",
                "Trade directory", "Walk-in", "Other"]

SHIPPING_METHODS = ["Collection", "Standard post", "Tracked post",
                    "Courier", "Next day courier", "Pallet",
                    "Freight", "Own delivery", "Dropship"]

SALE_STATUSES = ["Pending", "Paid", "Packing", "Shipped",
                 "Delivered", "Collected", "Refunded", "Cancelled"]

RETURN_SOURCES = ["Retail customer", "Wholesale customer",
                  "Marketplace", "Own warehouse", "Courier damage",
                  "Supplier"]

RETURN_STATUSES = ["Logged", "Inspecting", "Awaiting customer",
                   "Claim raised", "Resolved", "Closed"]

AUDIT_TYPES = ["Full stocktake", "Cycle count", "Spot check",
               "Investigation", "Year end"]

AUDIT_STATUSES = ["Counted", "Recount needed", "Investigating",
                  "Adjusted", "Closed"]

VARIANCE_REASONS = ["Miscount", "Damage not logged",
                    "Sale not recorded", "Receipt not recorded",
                    "Theft or loss", "Wrong SKU picked",
                    "Returned to supplier", "Sample taken",
                    "Used in production", "Found elsewhere",
                    "Unknown"]

STORAGE_TYPES = ["Shelf", "Bin", "Pallet", "Rack", "Drawer",
                 "Cold store", "Fragile", "Secure", "Overflow",
                 "Third party warehouse"]

PAYMENT_METHODS = ["Bank transfer", "Card", "Direct debit",
                   "Standing order", "PayPal", "Cash", "Cheque",
                   "Credit account", "Other"]

RECURRING_FREQUENCIES = ["One off", "Weekly", "Fortnightly",
                         "Monthly", "Quarterly", "Twice a year",
                         "Yearly"]

FREQUENCY_PER_YEAR = {"One off": 0.0, "Weekly": 52.0,
                      "Fortnightly": 26.0, "Monthly": 12.0,
                      "Quarterly": 4.0, "Twice a year": 2.0,
                      "Yearly": 1.0}

CURRENCIES = ["USD", "GBP", "EUR", "CAD", "AUD", "NZD", "JPY", "INR",
              "PKR", "ZAR", "SEK", "CHF", "Other"]

STAFF = ["Owner", "Warehouse", "Packer", "Assistant", "Bookkeeper",
         "Casual help"]

LOCATIONS = ["Main store", "Workshop", "Garage", "Shop floor",
             "Overflow unit", "Market stall", "Third party"]

#: name -> values. Everything the workbook offers you in a drop-down.
LISTS: List[Tuple[str, List[str]]] = [
    ("YesNoList", list(YES_NO)),
    ("ProductStatusList", list(PRODUCT_STATUSES)),
    ("CategoryList", [name for name, _subs in CATEGORIES]),
    ("SubcategoryList", [sub for _n, subs in CATEGORIES
                         for sub in subs]),
    ("UnitList", list(UNITS)),
    ("SupplierTypeList", list(SUPPLIER_TYPES)),
    ("SupplierStatusList", list(SUPPLIER_STATUSES)),
    ("POStatusList", list(PO_STATUSES)),
    ("DeliveryConditionList", list(DELIVERY_CONDITIONS)),
    ("CustomerTypeList", list(CUSTOMER_TYPES)),
    ("CustomerStatusList", list(CUSTOMER_STATUSES)),
    ("CustomerTierList", [name for name, _m, _d in CUSTOMER_TIERS]),
    ("LeadSourceList", list(LEAD_SOURCES)),
    ("OrderStatusList", list(ORDER_STATUSES)),
    ("ShippingMethodList", list(SHIPPING_METHODS)),
    ("ChannelList", list(SALES_CHANNELS)),
    ("SaleStatusList", list(SALE_STATUSES)),
    ("MovementTypeList", [name for name, _s, _d in MOVEMENT_TYPES]),
    ("ReturnSourceList", list(RETURN_SOURCES)),
    ("ReturnReasonList", list(RETURN_REASONS)),
    ("ReturnConditionList", list(RETURN_CONDITIONS)),
    ("ReturnStatusList", list(RETURN_STATUSES)),
    ("AuditTypeList", list(AUDIT_TYPES)),
    ("AuditStatusList", list(AUDIT_STATUSES)),
    ("VarianceReasonList", list(VARIANCE_REASONS)),
    ("StorageTypeList", list(STORAGE_TYPES)),
    ("LocationList", list(LOCATIONS)),
    ("StaffList", list(STAFF)),
    ("ExpenseCategoryList", list(EXPENSE_CATEGORIES)),
    ("StockCategoryList", list(STOCK_CATEGORIES)),
    ("TaxCategoryList", list(TAX_CATEGORIES)),
    ("PaymentMethodList", list(PAYMENT_METHODS)),
    ("FrequencyList", list(RECURRING_FREQUENCIES)),
    ("CurrencyList", list(CURRENCIES)),
    ("MonthNameList", list(MONTH_NAMES)),
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)
    sheet_ref = quote_sheet(NAME)

    s.banner("Settings & Lists",
             "Your business, your prices, your rules, your lists. "
             "Set these once and every tab in the workbook follows.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 2, 30)
    s.set_col(3, 3, 18)
    s.set_col(4, LAST_COL, 17)

    row = 4
    row = s.note(
        row,
        "White cells are yours to change; everything else is locked "
        "and calculated. Nothing here assumes a country, a currency "
        "or a way of selling - set your own price breaks, your own "
        "lead times, your own fee rates and your own targets, and "
        "the rest of the workbook follows.",
        LAST_COL, height=34)
    row += 1

    # ------------------------------------------------------ business --
    row = s.section(row, "Your business", LAST_COL)
    row = s.field(row, "Business name", cfg.business.name,
                  name="BusinessName", value_end=5, help_col=7,
                  help_text="Printed at the top of every report, "
                            "purchase order and invoice.")
    row = s.field(row, "Owner", cfg.business.owner, name="OwnerName",
                  value_end=5, help_col=7)
    row = s.field(row, "Email", cfg.business.email, value_end=5,
                  help_col=7)
    row = s.field(row, "Phone", cfg.business.phone, value_end=5,
                  help_col=7)
    row = s.field(row, "Website", cfg.business.website, value_end=5,
                  help_col=7)
    row = s.field(row, "Shop name", cfg.business.shop, value_end=5,
                  help_col=7,
                  help_text="Your marketplace shop, if you have one.")
    row = s.field(row, "Address line 1", cfg.business.address_1,
                  value_end=5, help_col=7)
    row = s.field(row, "Address line 2", cfg.business.address_2,
                  value_end=5, help_col=7)
    row = s.field(row, "City", cfg.business.city, value_end=5,
                  help_col=7)
    row = s.field(row, "Region", cfg.business.region, value_end=5,
                  help_col=7)
    row = s.field(row, "Postcode", cfg.business.postcode)
    row = s.field(row, "Country", cfg.business.country, value_end=5,
                  help_col=7)
    row = s.field(row, "Tax / VAT number", cfg.business.tax_id,
                  value_end=5, help_col=7)
    row = s.field(row, "Currency symbol", cfg.currency,
                  name="CurrencySign",
                  help_text="Shown on screen. The cell formats "
                            "follow the symbol you build the file "
                            "with.")
    row = s.field(row, "Currency code", cfg.currency_code,
                  validate=list_from("CurrencyList"))
    row = s.field(row, "Today", None, style="date", name="TodayDate",
                  mode="calc", formula="=TODAY()",
                  help_text="Live. Everything that says 'overdue', "
                            "'due soon' or 'this month' reads this "
                            "one cell.")
    row = s.field(row, "Reporting year", cfg.report_year, style="int",
                  name="ReportYear", validate=number_check(2000, 2100),
                  help_text="The year the Profit Analysis, Monthly "
                            "and Annual reports cover.")
    row = s.field(row, "Year starts", None, style="date",
                  name="YearStart", mode="calc",
                  formula="=DATE(ReportYear,1,1)")
    row = s.field(row, "Year ends", None, style="date",
                  name="YearEnd", mode="calc",
                  formula="=DATE(ReportYear,12,31)")
    row = s.field(row, "This month", None, style="text",
                  name="ThisMonthKey", mode="calc",
                  formula='=TEXT(TODAY(),"yyyy-mm")',
                  help_text="The month key every monthly total "
                            "groups on.")
    row += 1

    # ------------------------------------------------- stock settings --
    row = s.section(row, "How you manage stock", LAST_COL)
    row = s.note(
        row,
        "These five numbers drive the Reorder Planner. Safety stock "
        "is expressed in days of cover rather than a flat number of "
        "units, so a line selling ten a day automatically gets a "
        "bigger cushion than one selling ten a month.",
        LAST_COL, height=34)
    row += 1
    row = s.field(row, "Sales window for averages",
                  cfg.sales_history_days, style="int",
                  name="SalesWindow", validate=number_check(7, 730),
                  help_text="Days of sales history used to work out "
                            "average daily sales. Ninety days is a "
                            "reasonable default; shorten it if your "
                            "trade is seasonal and you want the "
                            "planner to react faster.")
    row = s.field(row, "Safety stock, in days", cfg.safety_stock_days,
                  style="int", name="SafetyDays",
                  validate=number_check(0, 365),
                  help_text="The cushion on top of the lead time. "
                            "Ten days is comfortable for most "
                            "sellers.")
    row = s.field(row, "Default lead time",
                  cfg.default_lead_time_days, style="int",
                  name="DefaultLeadDays", validate=number_check(0, 365),
                  help_text="Used when a supplier has no lead time "
                            "of their own on the Supplier Database.")
    row = s.field(row, "Slow moving after", cfg.slow_stock_days,
                  style="int", name="SlowStockDays",
                  validate=number_check(7, 999),
                  help_text="Days without a sale before a product is "
                            "called slow.")
    row = s.field(row, "Dead stock after", cfg.dead_stock_days,
                  style="int", name="DeadStockDays",
                  validate=number_check(7, 999),
                  help_text="Days without a sale before it is dead "
                            "money on a shelf.")
    row = s.field(row, "Count A lines every", cfg.stocktake_months,
                  style="int", name="StocktakeMonths",
                  validate=number_check(1, 24),
                  help_text="Months between cycle counts of your "
                            "highest value lines.")
    row += 1

    # ------------------------------------------------------- the money --
    row = s.section(row, "Pricing and margin", LAST_COL)
    row = s.note(
        row,
        "Minimum margin is the one to set carefully: it is the line "
        "below which the workbook starts calling a price a problem, "
        "on wholesale tiers, on order lines and on individual "
        "products. Everything else here is a default for new rows.",
        LAST_COL, height=34)
    row += 1
    row = s.field(row, "Minimum acceptable margin",
                  cfg.minimum_margin, style="percent",
                  name="MinGP", validate=number_check(0, 1),
                  help_text="Gross margin, not markup. Anything "
                            "below this is flagged wherever it "
                            "appears.")
    row = s.field(row, "Target gross margin", cfg.target_gross_margin,
                  style="percent", name="TargetMargin",
                  validate=number_check(0, 1))
    row = s.field(row, "Default retail markup", cfg.default_markup,
                  style="number1", name="DefaultMarkup",
                  validate=number_check(1, 20),
                  help_text="Cost multiplied by this gives a "
                            "starting retail price. A multiple of "
                            "2.5 is common for handmade goods sold "
                            "both ways.")
    row = s.field(row, "Wholesale as a share of retail",
                  cfg.wholesale_of_retail, style="percent",
                  name="WholesaleRatio", validate=number_check(0, 1),
                  help_text="Half of retail is the convention. A "
                            "stockist needs to double your price "
                            "and still be competitive.")
    row = s.field(row, "Default minimum order quantity",
                  cfg.default_moq, style="int", name="DefaultMOQ",
                  validate=number_check(0, 100000))
    row = s.field(row, "Default credit limit",
                  cfg.default_credit_limit, style="money",
                  name="DefaultCreditLimit",
                  validate=number_check(0, 10000000))
    row += 1

    # ------------------------------------------------- fees and extras --
    row = s.section(row, "What selling actually costs you", LAST_COL)
    row = s.note(
        row,
        "Marketplace commission, payment processing and packaging "
        "come off every retail sale before you see a penny of it. "
        "The rates below are starting points - find your real ones "
        "on a statement and put those in, because this is where "
        "small sellers most often think they are making money and "
        "are not.",
        LAST_COL, height=42)
    row += 1
    row = s.field(row, "Default marketplace fee",
                  cfg.marketplace_fee_pct, style="percent",
                  name="MarketplaceFeePct",
                  validate=number_check(0, 1),
                  help_text="Used for any channel without its own "
                            "rate in the table below.")
    row = s.field(row, "Payment processing", cfg.payment_fee_pct,
                  style="percent", name="PaymentFeePct",
                  validate=number_check(0, 1))
    row = s.field(row, "Payment fixed fee", cfg.payment_fee_fixed,
                  style="money", name="PaymentFeeFixed",
                  validate=number_check(0, 100),
                  help_text="The flat charge per transaction on top "
                            "of the percentage.")
    row = s.field(row, "Packaging per order",
                  cfg.packaging_cost_per_order, style="money",
                  name="PackagingPerOrder",
                  validate=number_check(0, 1000),
                  help_text="Box, tissue, label, filler. Small, "
                            "constant, and worth counting.")
    row = s.field(row, "Default shipping charge",
                  cfg.default_shipping_charge, style="money",
                  name="DefaultShipping",
                  validate=number_check(0, 100000))
    row = s.field(row, "Free shipping over", cfg.free_shipping_over,
                  style="money", name="FreeShippingOver",
                  validate=number_check(0, 1000000))
    row += 1

    # ------------------------------------------------------------ tax --
    row = s.section(row, "Tax", LAST_COL)
    row = s.note(
        row,
        "Whether you charge sales tax or VAT, at what rate, and "
        "whether a wholesale customer is exempt, are local "
        "questions with local answers. The switch ships OFF and the "
        "rate ships at zero, because a wrong tax number is worse "
        "than no tax number.",
        LAST_COL, height=38)
    row += 1
    row = s.field(row, "Charge tax on sales?",
                  "Yes" if cfg.tax_on_sales else "No", style="flag",
                  name="TaxOnSales", validate=list_from("YesNoList"))
    row = s.field(row, "Tax rate", cfg.tax_rate, style="percent",
                  name="TaxRate", validate=number_check(0, 1))
    row = s.field(row, "What it is called", cfg.tax_name,
                  name="TaxName", value_end=5, help_col=7,
                  help_text="Sales tax, VAT, GST - whatever appears "
                            "on your invoices.")
    row += 1

    # --------------------------------------------------------- alerts --
    row = s.section(row, "When to start worrying", LAST_COL)
    row = s.note(
        row,
        "The thresholds the alert columns use. Set them to suit the "
        "size of your business - a fifty pound write-off is a "
        "shrug for some sellers and a bad week for others.",
        LAST_COL, height=30)
    row += 1
    row = s.field(row, "Chase a late delivery after",
                  cfg.po_chase_days, style="int", name="POChaseDays",
                  validate=number_check(0, 90),
                  help_text="Days past the expected date.")
    row = s.field(row, "Flag an unshipped order after",
                  cfg.pick_warning_days, style="int",
                  name="PickWarningDays", validate=number_check(0, 90),
                  help_text="Days a confirmed wholesale order has "
                            "been sitting unpicked.")
    row = s.field(row, "Chase an unpaid invoice after",
                  cfg.overdue_chase_days, style="int",
                  name="ChaseDays", validate=number_check(0, 365))
    row = s.field(row, "A customer is dormant after", 120,
                  style="int", name="DormantDays",
                  validate=number_check(30, 999),
                  help_text="Days since a stockist last ordered.")
    row = s.field(row, "Query an invoice that is out by", 1.00,
                  style="money", name="PriceGapTolerance",
                  validate=number_check(0, 10000),
                  help_text="Difference between the supplier's "
                            "invoice and what you expected to pay.")
    row = s.field(row, "Query postage that overshoots by", 2.00,
                  style="money", name="ShipGapTolerance",
                  validate=number_check(0, 10000))
    row = s.field(row, "A large expense is over", 500.00,
                  style="money", name="LargeExpenseLevel",
                  validate=number_check(0, 1000000))
    row = s.field(row, "A large loss is over", 100.00, style="money",
                  name="LargeLossLevel",
                  validate=number_check(0, 1000000),
                  help_text="Used on returns and stock audits.")
    row = s.field(row, "Review a write-off over", 50.00,
                  style="money", name="WriteoffReview",
                  validate=number_check(0, 1000000))
    row += 1

    # --------------------------------------------------------- targets --
    row = s.section(row, "Targets", LAST_COL)
    row = s.field(row, "Monthly revenue target",
                  cfg.target_revenue_month, style="money",
                  name="MonthlyTarget",
                  validate=number_check(0, 100000000))
    row = s.field(row, "Yearly revenue target",
                  cfg.target_revenue_year, style="money",
                  name="YearlyTarget",
                  validate=number_check(0, 100000000))
    row = s.field(row, "Target stock value", cfg.target_stock_value,
                  style="money", name="TargetStockValue",
                  validate=number_check(0, 100000000),
                  help_text="How much you want tied up in stock. "
                            "More is not better.")
    row = s.field(row, "Target stock turns a year",
                  cfg.target_turnover, style="number1",
                  name="TargetTurns", validate=number_check(0, 100))
    row = s.field(row, "Target return rate", cfg.target_return_rate,
                  style="percent", name="TargetReturnRate",
                  validate=number_check(0, 1))
    row = s.field(row, "Target fill rate", cfg.target_fill_rate,
                  style="percent", name="TargetFillRate",
                  validate=number_check(0, 1),
                  help_text="The share of order lines you can ship "
                            "complete, first time.")
    row += 1

    # --------------------------------------------- business-wide totals --
    row = s.section(row, "Totals the workbook refers to", LAST_COL)
    row = s.note(
        row,
        "Calculated, not typed. Several sheets express a figure as "
        "a share of one of these, and keeping them in one place "
        "means the shares always add up to a hundred per cent.",
        LAST_COL, height=30)
    row += 1
    row = s.field(row, "Total stock value", None, style="money",
                  name="TotalStockValue", mode="calc",
                  formula="=SUM(ValuationStockValue)")
    row = s.field(row, "Total revenue", None, style="money",
                  name="TotalRevenue", mode="calc",
                  formula="=SUM(PerfRevenue)")
    row = s.field(row, "Wholesale revenue", None, style="money",
                  name="WholesaleRevenue", mode="calc",
                  formula="=SUMIF(OrderIsShipped,1,OrderTotal)")
    row = s.field(row, "Retail revenue", None, style="money",
                  name="RetailRevenue", mode="calc",
                  formula="=SUMIF(SaleIsSold,1,SaleGross)")
    row = s.field(row, "Total purchase spend", None, style="money",
                  name="TotalPurchaseSpend", mode="calc",
                  formula="=SUM(POTotal)")
    row += 1

    # ----------------------------------------------- payment terms table --
    row = s.section(row, "Payment terms", LAST_COL)
    row = s.note(
        row,
        "What each term means in days. Purchase orders and wholesale "
        "invoices work out their own due dates from this table, so "
        "if your 'Net 30' really means thirty days from the end of "
        "the month, change the number here.",
        LAST_COL, height=34)
    row += 1
    terms_head = row
    s.table_head(terms_head, 1, ["Term", "Days"], widths=[26, 14])
    first_term = terms_head + 1
    for index, (label, days) in enumerate(PAYMENT_TERMS):
        line = first_term + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, days, fmts.input("int"))
    last_term = first_term + len(PAYMENT_TERMS) - 1
    book.define_name(
        "PaymentTermsList",
        f"={sheet_ref}!$B${first_term + 1}:$B${last_term + 1}")
    book.define_name(
        "TermDays",
        f"={sheet_ref}!$C${first_term + 1}:$C${last_term + 1}")
    row = last_term + 2

    # ----------------------------------------------- movement sign table --
    row = s.section(row, "What each movement type does to stock",
                    LAST_COL)
    row = s.note(
        row,
        "This is the table that gives a stock movement its sign. "
        "Plus one adds to stock, minus one takes away, and zero "
        "means the row carries its own sign - which is why an "
        "Adjustment is the only type where a negative quantity "
        "makes sense.",
        LAST_COL, height=38)
    row += 1
    move_head = row
    s.table_head(move_head, 1, ["Movement type", "Sign",
                                "What it means"],
                 widths=[24, 10, 46])
    first_move = move_head + 1
    for index, (label, sign, meaning) in enumerate(MOVEMENT_TYPES):
        line = first_move + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, sign, fmts.input("int"))
        s.write(line, 3, meaning, fmts.chrome("note"))
    last_move = first_move + len(MOVEMENT_TYPES) - 1
    book.define_name(
        "MovementSign",
        f"={sheet_ref}!$C${first_move + 1}:$C${last_move + 1}")
    row = last_move + 2

    # ------------------------------------------------- channel fee table --
    row = s.section(row, "What each sales channel charges", LAST_COL)
    row = s.note(
        row,
        "Every retail sale is costed with the rate for its channel. "
        "These are rough defaults and they go out of date the "
        "moment a platform changes its pricing - put your own in "
        "from a real statement, and your profit figures become "
        "trustworthy overnight.",
        LAST_COL, height=38)
    row += 1
    fee_head = row
    s.table_head(fee_head, 1, ["Channel", "Fee rate"],
                 widths=[24, 14])
    default_fees = {
        "Etsy": 0.095, "Shopify": 0.02, "Amazon": 0.15,
        "eBay": 0.129, "WooCommerce": 0.0,
        "Physical Store": 0.0, "Direct Sales": 0.0,
        "Craft Fair": 0.0, "Wholesale": 0.0, "Other": 0.0,
    }
    first_fee = fee_head + 1
    for index, channel in enumerate(SALES_CHANNELS):
        line = first_fee + index
        s.write(line, 1, channel, fmts.input("text"))
        s.write(line, 2, default_fees.get(channel, 0.0),
                fmts.input("percent"))
    last_fee = first_fee + len(SALES_CHANNELS) - 1
    book.define_name(
        "ChannelFeeRates",
        f"={sheet_ref}!$C${first_fee + 1}:$C${last_fee + 1}")
    row = last_fee + 2

    # ------------------------------------------------ price tier ladder --
    row = s.section(row, "Default quantity breaks", LAST_COL)
    row = s.note(
        row,
        "The quantity breaks new products start with on the "
        "Wholesale Pricing tab. Ten, fifty and a hundred suit a lot "
        "of small makers; change them to whatever your trade "
        "actually orders in.",
        LAST_COL, height=32)
    row += 1
    tier_head = row
    s.table_head(tier_head, 1, ["Break", "From this quantity"],
                 widths=[24, 20])
    first_tier = tier_head + 1
    for index, (qty, label) in enumerate(PRICE_TIERS):
        line = first_tier + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, qty, fmts.input("int"))
    last_tier = first_tier + len(PRICE_TIERS) - 1
    book.define_name(
        "TierBreaks",
        f"={sheet_ref}!$C${first_tier + 1}:$C${last_tier + 1}")
    row = last_tier + 2

    # ------------------------------------------ customer tier discounts --
    row = s.section(row, "Customer tiers", LAST_COL)
    row = s.note(
        row,
        "What each kind of account pays, as a share of your retail "
        "price. These are a guide for setting your price list - the "
        "actual prices live on the Wholesale Pricing tab, where you "
        "can see the margin next to each one.",
        LAST_COL, height=34)
    row += 1
    ctier_head = row
    s.table_head(ctier_head, 1, ["Tier", "Share of retail",
                                 "Who they are"],
                 widths=[18, 16, 44])
    first_ctier = ctier_head + 1
    for index, (label, mult, who) in enumerate(CUSTOMER_TIERS):
        line = first_ctier + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, mult, fmts.input("percent0"))
        s.write(line, 3, who, fmts.chrome("note"))
    last_ctier = first_ctier + len(CUSTOMER_TIERS) - 1
    book.define_name(
        "TierMultipliers",
        f"={sheet_ref}!$C${first_ctier + 1}:$C${last_ctier + 1}")
    row = last_ctier + 2

    # ------------------------------------------- recurring frequencies --
    row = s.section(row, "How often a recurring cost repeats",
                    LAST_COL)
    row = s.note(
        row,
        "This is what turns any expense into a monthly equivalent, "
        "so a yearly insurance premium and a monthly subscription "
        "can sit in the same breakdown. 'One off' is zero because "
        "it is not a standing cost.",
        LAST_COL, height=32)
    row += 1
    freq_head = row
    s.table_head(freq_head, 1, ["How often", "Times a year"],
                 widths=[24, 16])
    first_freq = freq_head + 1
    for index, label in enumerate(RECURRING_FREQUENCIES):
        line = first_freq + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, FREQUENCY_PER_YEAR.get(label, 0.0),
                fmts.input("number1"))
    last_freq = first_freq + len(RECURRING_FREQUENCIES) - 1
    book.define_name(
        "FrequencyPerYear",
        f"={sheet_ref}!$C${first_freq + 1}:$C${last_freq + 1}")
    row = last_freq + 2

    # -------------------------------------------------------- prefixes --
    row = s.section(row, "ID prefixes", LAST_COL)
    row = s.note(
        row,
        "The letters in front of every automatic ID. These are the "
        "keys the workbook joins on - Product IDs, SKUs, Supplier "
        "IDs, Purchase Order numbers and Order IDs. Change the "
        "prefixes here if you want to, but do it before you have "
        "typed three hundred products, not after.",
        LAST_COL, height=38)
    row += 1
    half = (len(ID_PREFIX_FIELDS) + 1) // 2
    top = row
    for index, (label, default, name, _digits) in enumerate(
            ID_PREFIX_FIELDS):
        column = 0 if index < half else 4
        line = top + (index if index < half else index - half)
        s.write(line, column + 1, label, fmts.chrome("label_bold"))
        s.write(line, column + 2, default, fmts.input("text"))
        book.define_name(
            name, f"={sheet_ref}!${col_letter(column + 2)}${line + 1}")
    row = top + half + 1

    # ----------------------------------------------------------- lists --
    row = s.section(row, "Drop-down lists", LAST_COL)
    row = s.note(
        row,
        "Add new entries directly under the last one in a column - "
        "every list has room to grow and blank rows are ignored. Do "
        "not delete a whole column: a drop-down pointing at a "
        "missing list stops working.",
        LAST_COL, height=32)
    row += 1

    per_row = 4
    spare = 6
    top = row
    column = 0
    tallest = 0
    for index, (name, values) in enumerate(LISTS):
        if index and index % per_row == 0:
            top += tallest + 2
            column = 0
            tallest = 0
        s.write(top, column, name.replace("List", ""),
                fmts.chrome("header"))
        s.set_col(column, column, 28)
        for offset, value in enumerate(values):
            s.write(top + 1 + offset, column, value,
                    fmts.input("text"))
        for offset in range(len(values), len(values) + spare):
            s.write(top + 1 + offset, column, None,
                    fmts.input("text"))
        first = top + 2
        last = top + 1 + len(values) + spare
        book.define_name(
            name,
            f"={sheet_ref}!${col_letter(column)}${first}:"
            f"${col_letter(column)}${last}")
        tallest = max(tallest, len(values) + spare)
        column += 3
    row = top + tallest + 3

    # ------------------------------------------------------ month keys --
    row = s.section(row, "Month keys", LAST_COL)
    row = s.note(
        row,
        "The months the reports pick from, in plain yyyy-mm text so "
        "that every monthly total in the workbook groups on exactly "
        "the same thing.",
        LAST_COL, height=28)
    row += 1
    keys = _month_keys(cfg.today)
    s.write(row, 0, "Month", fmts.chrome("header"))
    s.set_col(0, 0, 14)
    for offset, key in enumerate(keys):
        s.write(row + 1 + offset, 0, key, fmts.input("text"))
    book.define_name(
        "MonthKeyList",
        f"={sheet_ref}!$A${row + 2}:$A${row + 1 + len(keys)}")
    book.define_name(
        "MonthKeys",
        dynamic_name(NAME, "A", row + 2, row + 1 + len(keys)))
    row = row + len(keys) + 2

    row = s.note(row, STOCK_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, COSTING_NOTE, LAST_COL, height=76)
    row += 1
    row = s.note(row, RESERVED_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, HONESTY_NOTE, LAST_COL, height=62)
    row += 1
    row = s.note(row, PRIVACY_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=76)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s


def _month_keys(today: _dt.date, back: int = 18,
                ahead: int = 18) -> List[str]:
    """A window of yyyy-mm keys around today."""
    keys: List[str] = []
    year = today.year
    start = today.month - back
    for step in range(back + ahead + 1):
        m = start + step
        y = year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        keys.append(f"{y:04d}-{m:02d}")
    return keys
