"""Every number, name, list and disclaimer the workbook uses.

Nothing downstream invents a figure. If a price, a lead time, a status
or a drop-down value appears on a sheet, it came from here, which is
why a seller in another country on another costing basis can be matched
without touching a formula.

Two conventions worth knowing before you read the rest:

* **SKU is the join key.** Stock, purchases, sales, returns, audits,
  valuation and profit all match on it. It is a drop-down everywhere
  except the Product Database, where it is created.
* **Stock is derived, never typed.** The only way to change a stock
  figure is to add a row that says why - a purchase received, a sale
  shipped, a return restocked, or an explicit adjustment in the Stock
  Movement Log.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# the product
# ---------------------------------------------------------------------------

PRODUCT_NAME = "Ultimate Inventory & Wholesale Order Manager"
PRODUCT_SHORT = "Inventory & Wholesale Manager"
PRODUCT_SUBTITLE = ("Products, stock, suppliers, purchase orders, "
                    "wholesale customers, tiered pricing and profit by "
                    "product - in one workbook")
LISTING_TITLE = ("Inventory Management Spreadsheet | SKU Stock Tracker, "
                 "Supplier Database, Purchase Orders, Wholesale Orders "
                 "& Profit Dashboard")
VERSION = "1.0.0"
AUTHOR = "Novality Store"
PASSWORD = "premium"

#: how many rows the dashboard lists before it stops
MAX_ROWS_SHOWN = 10
#: the "needs reordering soon" window, in days of cover
COVER_WARNING_DAYS = 21


# ---------------------------------------------------------------------------
# honesty
# ---------------------------------------------------------------------------

HONESTY_NOTE = (
    "This workbook does not connect to Etsy, Shopify, Amazon, eBay or "
    "any other marketplace. There is no sync, no API and no import "
    "robot. You type or paste your orders in, and every stock figure, "
    "cost and profit number on the other twenty-two tabs follows from "
    "what you typed. Anything that claimed otherwise would be lying to "
    "you.")

STOCK_NOTE = (
    "Stock is never typed. There is no cell anywhere in this workbook "
    "where you can simply overwrite a quantity, and that is "
    "deliberate. Current stock is calculated from opening stock plus "
    "what you received, minus what you sold, minus what was damaged, "
    "plus or minus any adjustment you logged. If a number looks wrong, "
    "there is a row that explains it.")

COSTING_NOTE = (
    "This workbook uses WEIGHTED AVERAGE COST throughout. Not FIFO, "
    "not LIFO, not specific identification - weighted average, "
    "everywhere, with no exceptions. Opening stock at its stated cost "
    "plus everything received at what it actually cost, divided by the "
    "units those two represent. Mixing costing methods is the single "
    "most common way a stock spreadsheet stops reconciling, so this "
    "one does not offer you the choice. If your accountant requires "
    "FIFO, tell them which method this is before you hand it over.")

RESERVED_NOTE = (
    "Reserved stock is stock you still physically have but have "
    "already promised to somebody. A confirmed wholesale order "
    "reserves its units; it does not remove them. They leave stock "
    "when the order is marked Shipped. That is why Available Stock "
    "and Current Stock are two different columns, and why selling "
    "against Available is the only safe thing to do.")

PRIVACY_NOTE = (
    "Hold the business details you need to trade: a company name, a "
    "contact, an address, payment terms. You do not need a customer's "
    "card number or a copy of anybody's passport in a spreadsheet, so "
    "there is nowhere here to put one. A resale certificate number is "
    "optional and only there because some jurisdictions require you to "
    "keep it.")

DISCLAIMER = (
    "This is a business organisation tool, not accounting software and "
    "not tax advice. Inventory valuation, cost of goods sold and the "
    "profit figures here are management numbers for making decisions. "
    "How stock and COGS must be reported, and when, depends on your "
    "jurisdiction, your business structure and your accounting basis - "
    "ask an accountant, and tell them this workbook uses weighted "
    "average cost.")


# ---------------------------------------------------------------------------
# colour
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    """A cool, slightly industrial scheme. Stock work is not romantic."""

    ink: str = "#1C2B33"
    deep: str = "#24404D"
    primary: str = "#2E6E7E"
    primary_mid: str = "#59929F"
    primary_soft: str = "#E8F1F3"
    accent: str = "#C2703D"
    good: str = "#2F7D55"
    warn: str = "#B5802A"
    bad: str = "#B33A3A"
    muted: str = "#6D7F87"
    paper: str = "#FCFEFE"
    rule: str = "#C9DBDF"

    # ---- derived tones the formats and the writer ask for ----------
    white: str = "#FFFFFF"
    input_bg: str = "#FFFFFF"
    input_border: str = "#CFE1E5"
    calc_bg: str = "#F5FAFB"
    calc_border: str = "#E2EFF1"
    line: str = "#C9DBDF"
    note_bg: str = "#F8FCFC"
    grey_text: str = "#55676F"
    good_bg: str = "#DCEDE3"
    good_text: str = "#1F5739"
    warn_bg: str = "#F9EBD2"
    warn_text: str = "#7C5712"
    bad_bg: str = "#F7DCDC"
    bad_text: str = "#8C2626"
    info_bg: str = "#E2EAF2"
    info_text: str = "#2E4A6B"
    accent_soft: str = "#FBEADF"


PALETTE = Palette()


# ---------------------------------------------------------------------------
# the business
# ---------------------------------------------------------------------------

@dataclass
class Business:
    name: str = "Thornfield Supply Co."
    owner: str = "Rosa Thornfield"
    email: str = "orders@thornfieldsupply.example"
    phone: str = "(503) 555-0172"
    website: str = "thornfieldsupply.example"
    shop: str = "ThornfieldSupplyCo"
    address_1: str = "Unit 7, Alder Works"
    address_2: str = "118 Kestrel Road"
    city: str = "Portland"
    region: str = "Oregon"
    postcode: str = "97202"
    country: str = "United States"
    tax_id: str = "US-EIN 88-4471203"


# ---------------------------------------------------------------------------
# identifiers - every one of them is a join key somewhere
# ---------------------------------------------------------------------------

ID_PREFIXES: Dict[str, Tuple[str, int]] = {
    "product": ("PRD-", 4),
    "supplier": ("SUP-", 3),
    "purchase": ("PO-", 4),
    "customer": ("WC-", 3),
    "order": ("WO-", 4),
    "sale": ("SO-", 4),
    "movement": ("MOV-", 5),
    "return": ("RET-", 4),
    "audit": ("AUD-", 4),
    "location": ("LOC-", 3),
    "expense": ("EXP-", 4),
    "invoice": ("INV-", 4),
}

#: (label, default, defined name, digits) - rendered as a block on
#: Settings so a seller can use their own code scheme
ID_PREFIX_FIELDS: List[Tuple[str, str, str, int]] = [
    ("Product ID prefix", "PRD-", "ProductPrefix", 4),
    ("Supplier ID prefix", "SUP-", "SupplierPrefix", 3),
    ("Purchase order prefix", "PO-", "PurchasePrefix", 4),
    ("Wholesale customer prefix", "WC-", "CustomerPrefix", 3),
    ("Wholesale order prefix", "WO-", "OrderPrefix", 4),
    ("Retail sale prefix", "SO-", "SalePrefix", 4),
    ("Stock movement prefix", "MOV-", "MovementPrefix", 5),
    ("Return prefix", "RET-", "ReturnPrefix", 4),
    ("Stock audit prefix", "AUD-", "AuditPrefix", 4),
    ("Warehouse location prefix", "LOC-", "LocationPrefix", 3),
    ("Expense prefix", "EXP-", "ExpensePrefix", 4),
    ("Invoice prefix", "INV-", "InvoicePrefix", 4),
]


# ---------------------------------------------------------------------------
# status vocabularies
# ---------------------------------------------------------------------------
# The sets below are what the stock arithmetic actually keys on, so
# they are defined once here and imported by sheets/common.py rather
# than retyped in nine registers.

#: a wholesale order that has committed stock but not shipped it
RESERVING_STATUSES = ["Confirmed", "Processing", "Picking", "Packed"]
#: a wholesale order whose stock has physically left
SHIPPED_STATUSES = ["Shipped", "Delivered", "Returned"]
#: a retail sale that has taken stock off the shelf
SOLD_RETAIL_STATUSES = ["Shipped", "Delivered", "Collected", "Refunded"]
#: a purchase order still expected to arrive
OPEN_PO_STATUSES = ["Sent", "Confirmed", "Partially Received"]
#: a purchase order the supplier has agreed to - stock on order
COMMITTED_PO_STATUSES = ["Confirmed", "Partially Received",
                         "Fully Received"]
#: a returned item that can go back on the shelf
SELLABLE_CONDITIONS = ["As new", "Opened - resellable"]

PO_STATUSES = ["Draft", "Pending Approval", "Sent", "Confirmed",
               "Partially Received", "Fully Received", "Cancelled"]

ORDER_STATUSES = ["New", "Confirmed", "Processing", "Picking",
                  "Packed", "Shipped", "Delivered", "Cancelled",
                  "Returned"]

SALES_CHANNELS = ["Etsy", "Shopify", "Amazon", "eBay", "WooCommerce",
                  "Physical Store", "Direct Sales", "Craft Fair",
                  "Wholesale", "Other"]


# ---------------------------------------------------------------------------
# the worked example's catalogue shape
# ---------------------------------------------------------------------------

#: (category, [subcategories])
CATEGORIES: List[Tuple[str, List[str]]] = [
    ("Candles", ["Jar candles", "Pillar candles", "Tealights",
                 "Wax melts"]),
    ("Ceramics", ["Mugs", "Bowls", "Planters", "Vases"]),
    ("Textiles", ["Tea towels", "Cushion covers", "Aprons",
                  "Tote bags"]),
    ("Stationery", ["Notebooks", "Greeting cards", "Print sets",
                    "Stickers"]),
    ("Bath & Body", ["Soap bars", "Bath salts", "Balms"]),
    ("Packaging", ["Boxes", "Tissue", "Labels", "Mailers"]),
]

UNITS = ["Each", "Pair", "Pack of 2", "Pack of 4", "Pack of 6",
         "Pack of 10", "Pack of 12", "Box of 24", "Case of 48",
         "Metre", "Kilogram", "Litre"]

#: quantity break, label - the default tier ladder on new products
PRICE_TIERS: List[Tuple[int, str]] = [
    (10, "Tier 1 - 10+"),
    (50, "Tier 2 - 50+"),
    (100, "Tier 3 - 100+"),
]

#: how much below retail each customer tier buys at, as a multiplier
CUSTOMER_TIERS: List[Tuple[str, float, str]] = [
    ("Retail", 1.00, "Walk-in and marketplace buyers"),
    ("Trade", 0.60, "Small shops buying a dozen at a time"),
    ("Wholesale", 0.50, "Regular stockists on standard terms"),
    ("Distributor", 0.42, "Volume buyers who resell to shops"),
    ("Key account", 0.38, "Negotiated - check the margin first"),
]

PAYMENT_TERMS: List[Tuple[str, int]] = [
    ("Prepaid", 0),
    ("On delivery", 0),
    ("Net 7", 7),
    ("Net 14", 14),
    ("Net 30", 30),
    ("Net 45", 45),
    ("Net 60", 60),
    ("End of month", 30),
]

#: movement types the Stock Movement Log offers, and the sign each one
#: has on stock: +1 adds, -1 removes, 0 is a correction that carries
#: its own sign
MOVEMENT_TYPES: List[Tuple[str, int, str]] = [
    ("Opening balance", 1, "Stock you already had on day one"),
    ("Purchase received", 1, "Booked in against a purchase order"),
    ("Customer return", 1, "Came back and went on the shelf"),
    ("Found in count", 1, "A stock count found more than expected"),
    ("Transfer in", 1, "Arrived from another location"),
    ("Sale", -1, "Sold and despatched"),
    ("Supplier return", -1, "Sent back to the supplier"),
    ("Damaged", -1, "Broken, spoiled or otherwise unsellable"),
    ("Lost or stolen", -1, "Gone, with no paperwork"),
    ("Sample or gift", -1, "Given away deliberately"),
    ("Used in production", -1, "Consumed making something else"),
    ("Transfer out", -1, "Sent to another location"),
    ("Adjustment", 0, "A correction - say why in the notes"),
]

RETURN_REASONS = ["Damaged in transit", "Defective", "Wrong item sent",
                  "Incorrect size", "Customer changed mind",
                  "Late delivery", "Not as described", "Other"]

RETURN_CONDITIONS = ["As new", "Opened - resellable",
                     "Damaged - not sellable", "Faulty - return to "
                     "supplier", "Destroyed"]

EXPENSE_CATEGORIES = [
    "Stock purchases", "Raw materials", "Packaging & mailers",
    "Shipping & postage", "Courier & freight", "Import duty & customs",
    "Warehouse rent", "Storage & fulfilment", "Utilities",
    "Marketplace fees",
    "Payment processing fees", "Advertising & marketing",
    "Website & hosting", "Software subscriptions", "Photography",
    "Printing & labels", "Equipment", "Equipment repair",
    "Wages & contractors", "Insurance", "Accounting & legal",
    "Bank charges", "Travel", "Trade shows & markets",
    "Samples & giveaways", "Office expenses", "Training",
    "Tax & national insurance", "Miscellaneous",
]

#: expenses that are really the cost of buying stock, not running the
#: business - counting them twice is how a margin ends up negative
STOCK_CATEGORIES = ["Stock purchases", "Raw materials"]

TAX_CATEGORIES = ["Cost of sale", "Operating expense",
                  "Capital / asset", "Owner drawing",
                  "Not deductible", "Review with accountant"]

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]


# ---------------------------------------------------------------------------
# how many rows each register gets
# ---------------------------------------------------------------------------

SCALE_ANCHOR = "Product & SKU Database"

DEFAULT_ROWS: Dict[str, int] = {
    "Product & SKU Database": 300,
    "Inventory Tracker": 300,
    "Stock Movement Log": 900,
    "Supplier Database": 60,
    "Purchase Orders": 500,
    "Wholesale Customer CRM": 120,
    "Wholesale Pricing": 300,
    "Wholesale Orders": 600,
    "Retail Sales Tracker": 900,
    "Reorder Planner": 300,
    "Inventory Valuation & COGS": 300,
    "Returns & Damaged Goods": 200,
    "Warehouse Locations": 200,
    "Stock Audit": 300,
    "Product Performance": 300,
    "Expense Tracker": 400,
    "Profit Analysis": 300,
}


# ---------------------------------------------------------------------------
# configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    business: Business = field(default_factory=Business)
    author: str = AUTHOR
    password: str = PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True

    currency: str = "$"
    currency_code: str = "USD"

    _today: Optional[_dt.date] = None
    year: Optional[int] = None

    # ---- pricing -------------------------------------------------------
    default_markup: float = 2.5          # retail = cost x this
    wholesale_of_retail: float = 0.50    # wholesale = retail x this
    distributor_of_retail: float = 0.42
    minimum_margin: float = 0.25         # refuse to sell below this
    default_moq: int = 10                # minimum wholesale order

    # ---- stock ---------------------------------------------------------
    default_lead_time_days: int = 14
    safety_stock_days: int = 10
    default_reorder_point: int = 12
    default_max_stock: int = 200
    sales_history_days: int = 90         # window for average daily sales
    dead_stock_days: int = 120           # no sales for this long = dead
    slow_stock_days: int = 60
    stocktake_months: int = 3            # how often to count

    # ---- orders --------------------------------------------------------
    default_payment_terms: str = "Net 30"
    default_credit_limit: float = 2000.0
    overdue_chase_days: int = 7
    po_chase_days: int = 3               # chase a late delivery after
    pick_warning_days: int = 2           # unshipped after confirmation

    # ---- money ---------------------------------------------------------
    tax_rate: float = 0.0
    tax_name: str = "Sales tax"
    tax_on_sales: bool = False
    default_shipping_charge: float = 12.50
    free_shipping_over: float = 350.0
    marketplace_fee_pct: float = 0.065
    payment_fee_pct: float = 0.029
    payment_fee_fixed: float = 0.30
    packaging_cost_per_order: float = 1.40

    # ---- targets -------------------------------------------------------
    target_gross_margin: float = 0.55
    target_revenue_month: float = 18000.0
    target_revenue_year: float = 216000.0
    target_turnover: float = 4.0         # inventory turns a year
    target_stock_value: float = 42000.0
    target_return_rate: float = 0.03
    target_fill_rate: float = 0.97

    rows_override: Optional[int] = None

    # ----------------------------------------------------------- dates --
    @property
    def today(self) -> _dt.date:
        return self._today or _dt.date.today()

    @today.setter
    def today(self, value: _dt.date) -> None:
        self._today = value

    @property
    def report_year(self) -> int:
        return self.year or self.today.year

    # --------------------------------------------------------- formats --
    @property
    def money_format(self) -> str:
        return f'{self.currency}#,##0.00;[Red]-{self.currency}#,##0.00'

    @property
    def money_format_0(self) -> str:
        return f'{self.currency}#,##0;[Red]-{self.currency}#,##0'

    @property
    def money_format_4(self) -> str:
        return f'{self.currency}#,##0.0000'

    @property
    def date_format(self) -> str:
        return 'dd mmm yyyy'

    @property
    def time_format(self) -> str:
        return 'hh:mm'

    # ---------------------------------------------------------- naming --
    @property
    def version(self) -> str:
        return VERSION

    @property
    def product_name(self) -> str:
        return PRODUCT_NAME

    @property
    def listing_title(self) -> str:
        return LISTING_TITLE

    # ------------------------------------------------------------- ids --
    def prefix(self, key: str) -> str:
        return ID_PREFIXES[key][0]

    def digits(self, key: str) -> int:
        return ID_PREFIXES[key][1]

    # ------------------------------------------------------------ rows --
    def row_count(self, sheet: str) -> int:
        """Rows for a register, scaled if --rows was given."""
        base = DEFAULT_ROWS.get(sheet, 200)
        if not self.rows_override:
            return base
        anchor = DEFAULT_ROWS[SCALE_ANCHOR]
        scaled = int(round(base * self.rows_override / anchor))
        return max(6, scaled)

    def scale_rows(self, rows: int) -> None:
        self.rows_override = rows

    # ----------------------------------------------------------- lists --
    @property
    def category_names(self) -> List[str]:
        return [name for name, _subs in CATEGORIES]

    @property
    def subcategory_names(self) -> List[str]:
        out: List[str] = []
        for _name, subs in CATEGORIES:
            out.extend(subs)
        return out

    @property
    def customer_tier_names(self) -> List[str]:
        return [name for name, _m, _d in CUSTOMER_TIERS]

    @property
    def payment_term_names(self) -> List[str]:
        return [name for name, _d in PAYMENT_TERMS]

    @property
    def movement_type_names(self) -> List[str]:
        return [name for name, _s, _d in MOVEMENT_TYPES]
