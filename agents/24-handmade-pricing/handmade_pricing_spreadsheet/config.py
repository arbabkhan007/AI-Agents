"""
Configuration for the Handmade Product Pricing & Profit Calculator.

Everything a maker may want to re-brand lives here, so the workbook can
be regenerated for a different shop, currency, country or pricing model
without touching any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Handmade Product Pricing & Profit Calculator"
PRODUCT_SUBTITLE = (
    "Material & Labor Cost Tracker, Retail and Wholesale Pricing, "
    "Profit Margin & Break-Even Calculator"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Handmade Product Pricing Calculator, Material and Labor Cost "
    "Tracker, Profit Margin and Wholesale Price Spreadsheet"
)

#: Password that protects every sheet so formula cells cannot be edited
#: by accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: Where a product is sold.  Each one carries its own fee structure on
#: the Channels tab.
SALES_CHANNELS = ["Etsy", "Own website", "Craft fair", "Wholesale",
                  "Instagram / direct", "Amazon Handmade", "Other"]

#: Product status, in the order a product moves through them.
PRODUCT_STATUSES = ["Idea", "Prototype", "Draft", "Active", "Made to order",
                    "Seasonal", "Out of stock", "Discontinued"]

#: The six specialised calculators, in tab order.  The product catalog
#: pulls its costs from whichever of these a product belongs to.
CRAFT_SHEETS = ["Crochet", "Jewelry", "Candles", "Clothing",
                "Woodworking", "Digital"]

#: Product categories offered in the drop downs.
PRODUCT_CATEGORIES = [
    "Crochet & knitting", "Jewelry", "Candles & home fragrance",
    "Clothing & accessories", "Woodworking", "Digital download",
    "Ceramics & pottery", "Bath & body", "Paper & stationery",
    "Art & prints", "Bags & leather", "Toys & amigurumi",
    "Pet products", "Wedding & occasion", "Other handmade",
]

#: How a price is rounded once it has been calculated.
ROUNDING_RULES = ["None", "Nearest 0.99", "Nearest 0.95", "Nearest 0.50",
                  "Nearest 1", "Nearest 5", "Up to whole 1",
                  "Up to whole 5"]

#: Pricing scenarios compared on the Scenarios tab: a name and the
#: target margin that goes with it.
PRICING_SCENARIOS = {
    "Budget market": 0.15,
    "Conservative": 0.22,
    "Standard": 0.30,
    "Premium": 0.40,
    "Luxury": 0.50,
}

#: Sales volumes the profit analyser forecasts against.
VOLUME_STEPS = [5, 10, 25, 50, 100]

#: Unit conversions written into the Lists tab: unit -> (base unit,
#: how many base units one of it is).
UNIT_CONVERSIONS = [
    ("g", "g", 1.0), ("kg", "g", 1000.0), ("oz", "g", 28.3495),
    ("lb", "g", 453.592), ("ml", "ml", 1.0), ("l", "ml", 1000.0),
    ("fl oz", "ml", 29.5735), ("cm", "cm", 1.0), ("m", "cm", 100.0),
    ("inch", "cm", 2.54), ("ft", "cm", 30.48), ("yard", "cm", 91.44),
    ("each", "each", 1.0), ("pair", "each", 2.0), ("sheet", "each", 1.0),
    ("skein", "each", 1.0), ("metre", "cm", 100.0),
]


# ---------------------------------------------------------------------------
# Colours - warm craft studio palette: clay, terracotta, sage, cream
# ---------------------------------------------------------------------------

class Palette:
    ink = "#3B2A26"           # darkest clay - titles
    primary = "#8C4A32"       # terracotta headers
    primary_mid = "#B5704F"   # section bands
    primary_soft = "#F6E4D7"  # light band / alternating rows
    accent = "#5E7B5A"        # sage accent
    accent_soft = "#E4EDE1"
    input_bg = "#FFFFFF"      # editable cell background
    input_border = "#E3D2C6"
    calc_bg = "#FBF3EC"       # locked formula cell background (warm cream)
    calc_border = "#EADCCF"
    white = "#FFFFFF"
    grey_text = "#6E5C55"
    line = "#DCC9BB"
    good_bg = "#DCEBD8"
    good_text = "#2F5A2B"
    warn_bg = "#FDEDD2"
    warn_text = "#8A5A00"
    bad_bg = "#F8DAD9"
    bad_text = "#9C2A24"
    info_bg = "#E2E6F3"
    info_text = "#3A4578"
    note_bg = "#FBF7F3"


# ---------------------------------------------------------------------------
# Row capacity of every register
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Settings": 0,
    "Lists": 60,
    "Products": 300,
    "Materials": 250,
    "Material Usage": 900,
    "Labor": 300,
    "Packaging": 80,
    "Shipping": 60,
    "Overhead": 40,
    "Channels": 14,
    "Crochet": 80,
    "Jewelry": 80,
    "Candles": 80,
    "Clothing": 80,
    "Woodworking": 80,
    "Digital": 80,
    "Bundles": 60,
    "Bundle Lines": 200,
    "Variations": 300,
    "Batches": 200,
    "Sales": 800,
    "Promotions": 40,
    "Price History": 300,
    "Competitors": 150,
    "Waste Log": 200,
    "Development": 80,
    "Events": 40,
    "Wholesale Customers": 60,
    "Wholesale Orders": 200,
}


@dataclass
class ShopDefaults:
    """Sample values written into the business profile on Settings."""

    name: str = "Willow & Thread Handmade"
    owner: str = "Maya Albright"
    brand: str = "Willow & Thread"
    email: str = "hello@willowandthread.co"
    phone: str = "(828) 555 0176"
    address: str = "42 Larkspur Lane, Asheville, NC 28801"
    website: str = "willowandthread.co"
    etsy_shop: str = "WillowAndThreadCo"
    instagram: str = "@willowandthread"
    tagline: str = "Small batch crochet, candles and keepsakes since 2021"
    tax_id: str = "NC-HM-2021-4471"


# ---------------------------------------------------------------------------
# The configuration object every sheet module reads
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Everything the generator needs to know to write one workbook."""

    author: str = AUTHOR
    product_name: str = PRODUCT_NAME
    product_subtitle: str = PRODUCT_SUBTITLE
    listing_title: str = PRODUCT_LISTING_TITLE
    version: str = PRODUCT_VERSION
    password: str = FORMULA_PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True

    # Formatting ------------------------------------------------------------
    currency_symbol: str = "$"
    currency_code: str = "USD"
    date_format: str = "dd-mmm-yyyy"
    time_format: str = "h:mm AM/PM"
    decimals: int = 2
    measure_system: str = "Metric"       # Metric | Imperial
    weight_unit: str = "g"               # g | oz
    length_unit: str = "cm"              # cm | inch

    # Shop profile pre-filled on the Settings tab ---------------------------
    shop: ShopDefaults = field(default_factory=ShopDefaults)
    plan_year: int = 0                   # 0 = the year of `today`

    # Labour ----------------------------------------------------------------
    hourly_rate: float = 25.00           # what the maker pays themselves
    minimum_wage: float = 15.00          # the floor the workbook warns at
    employee_rate: float = 18.00
    contractor_rate: float = 32.00
    payroll_burden: float = 0.12         # tax, insurance, holiday pay
    default_batch_size: int = 10

    # Pricing ---------------------------------------------------------------
    target_retail_margin: float = 0.30
    target_wholesale_margin: float = 0.20
    default_markup: float = 1.20         # 120% on cost when markup is used
    wholesale_discount: float = 0.40     # trade price = 60% of retail
    margin_warning: float = 0.15         # below this the row is flagged
    rounding_rule: str = "Nearest 0.99"
    default_discount: float = 0.10
    minimum_order_qty: int = 6
    minimum_order_value: float = 150.00

    # Costs -----------------------------------------------------------------
    default_packaging: float = 1.85
    default_shipping: float = 0.00       # what the seller absorbs
    default_waste: float = 0.05          # 5% of every material is lost
    default_defect_rate: float = 0.03    # 3% of a batch is unsellable
    supplies_per_hour: float = 0.60      # consumables while working

    # Marketplace fees (editable - these move, check the fee schedule) ------
    listing_fee: float = 0.20
    transaction_fee: float = 0.065       # 6.5% of the order
    processing_percent: float = 0.03     # payment processing
    processing_fixed: float = 0.25
    offsite_ads_fee: float = 0.15        # only on orders that come from ads
    offsite_ads_share: float = 0.20      # how many orders those are
    regulatory_fee: float = 0.0040
    currency_fee: float = 0.025
    fees_include_shipping: str = "Yes"
    fees_include_tax: str = "No"

    # Overhead --------------------------------------------------------------
    monthly_overhead: float = 420.00     # typed on the Overhead tab
    productive_hours: float = 70.0       # hours a month actually making
    units_per_month: int = 24
    tax_rate: float = 0.00               # sales tax, if you add it on

    # Targets the dashboard measures against --------------------------------
    monthly_revenue_target: float = 3500.0
    annual_revenue_target: float = 42000.0
    monthly_profit_target: float = 1400.0
    # the example shop is smaller than the defaults assume, so the demo
    # file carries targets it can actually be measured against
    sample_monthly_revenue_target: float = 2400.0
    sample_annual_revenue_target: float = 28800.0
    sample_monthly_profit_target: float = 900.0

    # Reminder windows ------------------------------------------------------
    price_review_days: int = 180         # how often a price gets a look
    fee_review_days: int = 180           # how often the fee schedule does
    low_stock_days: int = 21

    # Behaviour -------------------------------------------------------------
    top_rows: int = 5                    # size of the "top / best" tables
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    @property
    def year(self) -> int:
        return self.plan_year or self.today.year

    @property
    def revenue_target_month(self) -> float:
        """Monthly revenue target, scaled to whoever is reading it."""
        return (self.sample_monthly_revenue_target
                if self.include_sample_data else self.monthly_revenue_target)

    @property
    def revenue_target_year(self) -> float:
        return (self.sample_annual_revenue_target
                if self.include_sample_data else self.annual_revenue_target)

    @property
    def profit_target_month(self) -> float:
        return (self.sample_monthly_profit_target
                if self.include_sample_data else self.monthly_profit_target)

    @property
    def metric(self) -> bool:
        return self.measure_system.lower().startswith("met")

    @property
    def labor_cost_per_hour(self) -> float:
        """An hour of the maker's own time, once on-costs are added."""
        return round(self.hourly_rate * (1 + self.payroll_burden), 2)

    @property
    def overhead_per_hour(self) -> float:
        if self.productive_hours <= 0:
            return 0.0
        return round(self.monthly_overhead / self.productive_hours, 2)

    def scale_rows(self, product_rows: int) -> None:
        """Scale every register in place so Products holds N rows."""
        base = DEFAULT_ROWS["Products"]
        factor = max(0.02, float(product_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        """Return a copy with every register scaled."""
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings derived from the chosen currency ----------------
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.00;[Red]-{s}#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0;[Red]-{s}#,##0'

    @property
    def money_format_4(self) -> str:
        """Unit costs can be fractions of a cent - a gram of yarn is."""
        s = self.currency_symbol
        return f'{s}#,##0.0000;[Red]-{s}#,##0.0000'
