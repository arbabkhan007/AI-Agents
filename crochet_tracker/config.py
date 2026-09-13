"""
Every layout constant for the Ultimate Crochet Craft Fair Tracker.

Row numbers, column letters, sheet orders, dropdown values and list positions
all live here so the sheet builders stay readable and the whole workbook can
be re-skinned or re-rowed from one audited place.
"""

PRODUCT = "Ultimate Crochet Craft Fair Tracker"
PRODUCT_SHORT = "Crochet Craft Fair Tracker"
TAGLINE = "Products \u2022 Yarn Stock \u2022 Fairs \u2022 Profit"
AUTHOR = "Novality Store"
VERSION = "1.0"

# ===========================================================================
# SHEETS
# ===========================================================================
SHEET_NAMES = {
    "data": "_Data",
    "setup": "\u2699\uFE0F Lists & Settings",
    "dashboard": "\U0001F4CA Dashboard",
    "catalog": "\U0001F9F6 Product Catalog",
    "materials": "\U0001F9F5 Yarn & Materials",
    "production": "\U0001F4E6 Made & Stocked",
    "events": "\U0001F3EA Craft Fairs",
    "sales": "\U0001F4B0 Sales Log",
    "eventprofit": "\U0001F9EE Event Profit",
    "reorder": "\U0001F504 Reorder List",
    "packing": "\U0001F392 Packing Checklist",
    "pricing": "\U0001F4B5 Pricing Calculator",
    "monthly": "\U0001F4C5 Monthly Summary",
    "guide": "\U0001F4D6 Start Here",
}

SHEET_SHORT = {
    "data": "_Data",
    "setup": "Settings",
    "dashboard": "\U0001F3E0 Home",
    "catalog": "Products",
    "materials": "Yarn",
    "production": "Stock",
    "events": "Fairs",
    "sales": "Sales",
    "eventprofit": "Event $",
    "reorder": "Reorder",
    "packing": "Packing",
    "pricing": "Pricing",
    "monthly": "Monthly",
    "guide": "Help",
}

EDITIONS = {
    "premium": ["data", "setup", "dashboard", "catalog", "materials",
                "production", "events", "sales", "eventprofit", "reorder",
                "packing", "pricing", "monthly", "guide"],
    "basic": ["data", "setup", "dashboard", "catalog", "events", "sales",
              "pricing", "guide"],
}

# ===========================================================================
# SHARED TABLE GEOMETRY
# ===========================================================================
ROW_SPACER_1 = 1
ROW_TITLE = 2
ROW_SUBTITLE = 3
ROW_SPACER_2 = 4
ROW_STATS = 5
ROW_SPACER_3 = 6
ROW_HEADER = 7
ROW_FIRST = 8

CAP = {                       # data rows per sheet
    "catalog": 24,
    "materials": 24,
    "production": 30,
    "events": 24,
    "sales": 60,
    "monthly": 12,
    "reorder": 27,            # RO_PROD_FIRST..RO_MAT_LAST via ROW_FIRST
}


def last_row(key):
    return ROW_FIRST + CAP[key] - 1


TICK = "\u2713"

# reorder priority labels
PR_URGENT = "\U0001F534 Urgent"
PR_HIGH = "\U0001F7E0 High"
PR_NORMAL = "\U0001F7E1 Normal"

# stock health labels
ST_OUT = "\U0001F534 Out of stock"
ST_LOW = "\U0001F7E0 Low stock"
ST_OK = "\U0001F7E2 In stock"

RE_YES = "\u2705 Reorder"
RE_NO = "\u274C OK"

# ===========================================================================
# DROPDOWN LIST VALUES (editable on the Setup tab)
# ===========================================================================
CATEGORIES = ["Toys & Amigurumi", "Wearables", "Home & Decor", "Accessories",
              "Baby & Kids", "Seasonal"]

PAYMENT_METHODS = ["Cash", "Card", "Bank transfer", "Mobile wallet",
                   "Online order", "Other"]

YARN_WEIGHTS = ["Lace", "Sock / 4-ply", "DK / light", "Worsted / aran",
                "Chunky", "Super chunky", "Mixed / other"]

UNITS = ["balls", "metres", "grams", "skeins", "cones", "pieces"]

SUPPLIERS = ["Local yarn shop", "Online yarn store", "Wholesale craft",
             "Market stall", "Second-hand / stash", "Other"]

# ===========================================================================
# COLUMN MAPS  (letter per logical field)
# ===========================================================================
COLS = {
    "catalog": {"n": "A", "sku": "B", "name": "C", "category": "D", "desc": "E",
                "price": "F", "yarn_cost": "G", "pack_cost": "H",
                "unit_cost": "I", "profit": "J", "margin": "K",
                "time_h": "L", "stock": "M", "min": "N", "status": "O",
                "link": "P"},
    "materials": {"n": "A", "name": "B", "color": "C", "brand": "D", "weight": "E",
                  "purchased": "F", "unit": "G", "cost_unit": "H",
                  "total": "I", "used": "J", "remaining": "K",
                  "supplier": "L", "threshold": "M", "reorder": "N"},
    "production": {"n": "A", "product": "B", "date": "C", "made": "D", "reserved": "E",
                   "taken": "F", "sold": "G", "returned": "H",
                   "damaged": "I", "current": "J", "available": "K",
                   "notes": "L"},
    "events": {"n": "A", "name": "B", "date": "C", "location": "D", "organizer": "E",
               "booth": "F", "travel": "G", "parking": "H", "food": "I",
               "display": "J", "total": "K", "taken": "L", "sold": "M",
               "sales": "N", "cogs": "O", "net": "P", "margin": "Q",
               "best": "R"},
    "sales": {"n": "A", "date": "B", "event": "C", "product": "D", "qty": "E",
              "unit": "F", "discount": "G", "total": "H", "method": "I",
              "ref": "J", "notes": "K", "pair": "L", "cost": "M"},
    "reorder": {"item": "B", "current": "C", "min": "D", "suggest": "E",
                "supplier": "F", "est": "G", "priority": "H",
                "ordered": "I", "ordered_date": "J"},
    "monthly": {"n": "A", "month": "B", "revenue": "C", "cogs": "D", "fees": "E",
                "net": "F", "margin": "G", "units": "H", "aov": "I",
                "per_item": "J", "markets": "K"},
}

# Column widths per sheet (letters are positional: A, B, C ...).
WIDTHS = {
    "catalog": {"A": 2.2, "B": 10, "C": 24, "D": 16, "E": 28, "F": 10,
                "G": 10, "H": 10, "I": 10, "J": 10, "K": 9, "L": 8, "M": 8,
                "N": 8, "O": 15, "P": 18},
    "materials": {"A": 2.2, "B": 22, "C": 14, "D": 14, "E": 15, "F": 10,
                  "G": 8, "H": 10, "I": 10, "J": 9, "K": 10, "L": 18,
                  "M": 10, "N": 13},
    "production": {"A": 2.2, "B": 24, "C": 12, "D": 8, "E": 9, "F": 9,
                   "G": 8, "H": 9, "I": 9, "J": 9, "K": 10, "L": 22},
    "events": {"A": 2.2, "B": 22, "C": 12, "D": 18, "E": 16, "F": 9, "G": 9,
               "H": 9, "I": 9, "J": 9, "K": 10, "L": 8, "M": 8, "N": 10,
               "O": 10, "P": 10, "Q": 9, "R": 22},
    "sales": {"A": 2.2, "B": 12, "C": 20, "D": 24, "E": 7, "F": 9, "G": 9,
              "H": 10, "I": 14, "J": 12, "K": 22, "L": 9},
    "reorder": {"A": 2.2, "B": 26, "C": 9, "D": 8, "E": 10, "F": 18, "G": 10,
                "H": 13, "I": 10, "J": 12},
    "monthly": {"A": 2.2, "B": 12, "C": 11, "D": 11, "E": 10, "F": 11,
                "G": 9, "H": 8, "I": 10, "J": 11, "K": 9},
    "eventprofit": {"A": 2.2, "B": 26, "C": 14, "D": 14, "E": 14, "F": 14,
                    "G": 14, "H": 14, "I": 14, "J": 14},
    "pricing": {"A": 2.2, "B": 24, "C": 14, "D": 14, "E": 14, "F": 14,
                "G": 16, "H": 16, "I": 16, "J": 16},
    "packing": {"A": 2.2, "B": 8, "C": 30, "D": 30, "E": 20, "F": 20},
    "dashboard": {"A": 2.2, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13,
                  "G": 13, "H": 13, "I": 13, "J": 13, "K": 13, "L": 13,
                  "M": 13},
    "setup": {"A": 2.2, "B": 24, "C": 16, "D": 13, "E": 16, "F": 11,
              "G": 17, "H": 12, "I": 12, "J": 12},
    "guide": {"A": 2.2, "B": 14, "C": 14, "D": 14, "E": 14, "F": 14,
              "G": 14, "H": 14, "I": 14, "J": 14},
}

# ===========================================================================
# SETUP TAB GEOMETRY
# ===========================================================================
SU_BUSINESS = 6
SU_MESSAGE = 7
SU_CURRENCY = 10
SU_YEAR = 11
SU_WAGE = 12
SU_OVERHEAD = 13
SU_MARGIN = 14
SU_LIST_HEADER = 22
SU_LIST_FIRST = 23
SU_LIST_ROWS = 20
SU_FIXED_HEADER = 46
SU_FIXED_FIRST = 47

# ===========================================================================
# _Data POOL GEOMETRY (hidden sheet)
# ===========================================================================
DATA_MONTH_FIRST = 2          # H..N  rows 2-13: month table
DATA_PAY_FIRST = 2            # P..Q  rows 2-7:  payment methods
DATA_EXP_FIRST = 2            # S..T  rows 2-6:  event expense categories
DATA_PROD_FIRST = 2           # V..AA rows 2-25: product pool
DATA_EVENT_FIRST = 2          # AC..AF rows 2-25: event pool
DATA_KPI_FIRST = 2            # AH/AI rows 2-40: KPI cells
DATA_SEQP_FIRST = 2           # AK/AL rows 2-25: product reorder sequence
DATA_SEQM_FIRST = 2           # AN/AO rows 2-25: material reorder sequence

# ===========================================================================
# EVENT PROFIT / PRICING GEOMETRY
# ===========================================================================
EP_EVENT_ROW = 8              # event picker row
EP_REV = {"units": 11, "gross": 12, "discounts": 13}
EP_COST = {"cogs": 16, "booth": 17, "travel": 18, "parking": 19,
           "food": 20, "display": 21}
EP_OUT = {"gross_profit": 24, "total_cost": 25, "net": 26, "margin": 27,
          "avg_sale": 28, "breakeven": 29, "roi": 30}
EP_LAST_ROW = 34

PR_IN = {"material": 10, "packaging": 11, "hours": 12, "wage": 13,
         "overhead": 14, "margin": 15}
PR_OUT = {"labor": 14, "overhead_amt": 15, "true_cost": 16, "price": 17,
          "charm": 18, "profit": 19, "check": 20}
PR_LAST_ROW = 26

# ===========================================================================
# REORDER LIST GEOMETRY
# ===========================================================================
RO_PROD_FIRST = 10
RO_PROD_LAST = 21
RO_MAT_FIRST = 25
RO_MAT_LAST = 34

# ===========================================================================
# PACKING CHECKLIST
# ===========================================================================
PACK_EVENT_ROW = 6
PACK_SECTIONS = [
    ("Products", ["Finished products", "Extra inventory", "Price tags",
                  "Product labels / care cards"]),
    ("Booth", ["Table", "Tablecloth", "Display stands / risers",
               "Baskets & bins", "Signage & banner", "Business cards"]),
    ("Payments", ["Cash float", "Card reader", "Phone / tablet", "Charger",
                  "Payment QR code"]),
    ("Supplies", ["Shopping bags", "Tissue paper", "Tape & scissors",
                  "Pens", "Receipt book", "Sticky tack / clips"]),
]

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]

# ===========================================================================
# SETUP LIST COLUMNS (editable dropdown sources)
# ===========================================================================
LIST_COLS = {"categories": "C", "payments": "D", "weights": "E",
             "units": "F", "suppliers": "G"}
LIST_VALUES = {"categories": CATEGORIES, "payments": PAYMENT_METHODS,
               "weights": YARN_WEIGHTS, "units": UNITS,
               "suppliers": SUPPLIERS}
LIST_TITLES = {"categories": "Product categories",
               "payments": "Payment methods", "weights": "Yarn weights",
               "units": "Units", "suppliers": "Suppliers"}
FIXED_COLS = {"tick": "C"}

# ===========================================================================
# KPI CELLS ON _Data (column AH holds the label, AI the formula)
# ===========================================================================
_KPI_SPECS = [
    ("revenue", "Gross sales (all time)", "#,##0.00"),
    ("discounts", "Discounts given", "#,##0.00"),
    ("cogs", "Cost of products sold", "#,##0.00"),
    ("fees", "Event expenses (all fairs)", "#,##0.00"),
    ("profit", "Net profit", "#,##0.00"),
    ("margin", "Profit margin", "0.0%"),
    ("units", "Units sold", "0"),
    ("txns", "Sales log entries", "0"),
    ("aov", "Average sale value", "#,##0.00"),
    ("per_item", "Average profit per item", "#,##0.00"),
    ("events_total", "Fairs on the books", "0"),
    ("events_done", "Fairs worked", "0"),
    ("inv_value", "Inventory value (at unit cost)", "#,##0.00"),
    ("low_products", "Products below minimum", "0"),
    ("low_materials", "Materials below threshold", "0"),
    ("reorder_cost", "Estimated reorder cost", "#,##0.00"),
    ("sell_through", "Sell-through rate", "0.0%"),
    ("made_total", "Units made (all batches)", "0"),
    ("best_product", "Best-selling product", "@"),
    ("best_event", "Best craft fair", "@"),
    ("bs_units", "Most units sold", "@"),
    ("bs_revenue", "Highest revenue product", "@"),
    ("bs_profit", "Highest profit product", "@"),
    ("bs_margin", "Highest margin product", "@"),
    ("bs_slow", "Slowest mover", "@"),
    ("price_suggest", "Pricing calculator: suggested price", "#,##0.00"),
]
KPI_ROW = {}
KPI_FMT = {}
for _i, (_key, _label, _fmt) in enumerate(_KPI_SPECS):
    KPI_ROW[_key] = 2 + _i
    KPI_FMT[_key] = _fmt

KPI_LABEL = {k: label for k, label, _ in _KPI_SPECS}


def cols_last(key):
    """Right-most column letter used by a sheet's chips / head."""
    return {"catalog": "P", "materials": "N", "production": "L",
            "events": "R", "sales": "M", "reorder": "J", "monthly": "K",
            "eventprofit": "J", "pricing": "J", "packing": "F",
            "dashboard": "M", "setup": "J", "guide": "J"}[key]
