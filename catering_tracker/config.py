"""
Every layout constant for the Ultimate Catering Business Spreadsheet.

Row numbers, column letters, sheet orders, dropdown values and list positions
all live here so the sheet builders stay readable and the whole workbook can be
re-skinned or re-rowed from one audited place.
"""

PRODUCT = "Ultimate Catering Business Spreadsheet"
PRODUCT_SHORT = "Catering Business Manager"
TAGLINE = "Events • Clients • Quotes • Food Cost • Profit"
AUTHOR = "Novality Store"
VERSION = "1.0"

# ===========================================================================
# SHEETS
# ===========================================================================
SHEET_NAMES = {
    "data": "_Data",
    "setup": "\u2699\uFE0F Setup",
    "dashboard": "\U0001F4CA Dashboard",
    "clients": "\U0001F465 Clients",
    "events": "\U0001F4C5 Events",
    "quote": "\U0001F9EE Quote Calculator",
    "menu": "\U0001F37D\uFE0F Menu Costing",
    "inventory": "\U0001F4E6 Inventory",
    "shopping": "\U0001F6D2 Shopping List",
    "expenses": "\U0001F4B8 Expenses",
    "income": "\U0001F4B0 Payments",
    "staff": "\U0001F477 Staff & Labor",
    "equipment": "\U0001F373 Equipment",
    "suppliers": "\U0001F69A Suppliers",
    "calendar": "\U0001F4C6 Event Calendar",
    "reports": "\U0001F4C8 P&L & Reports",
    "tax": "\U0001F9FE Tax Tracker",
    "checklists": "\u2705 Checklists",
    "invoice": "\U0001F5A8\uFE0F Invoice & Proposal",
    "guide": "\U0001F4D6 Start Here",
}

SHEET_SHORT = {
    "data": "_Data",
    "setup": "Setup",
    "dashboard": "\U0001F3E0 Home",
    "clients": "Clients",
    "events": "Events",
    "quote": "Quote",
    "menu": "Menu",
    "inventory": "Stock",
    "shopping": "Shop",
    "expenses": "Expenses",
    "income": "Payments",
    "staff": "Staff",
    "equipment": "Equip",
    "suppliers": "Suppliers",
    "calendar": "Calendar",
    "reports": "P&L",
    "tax": "Tax",
    "checklists": "Checks",
    "invoice": "Invoice",
    "guide": "Help",
}

EDITIONS = {
    "premium": ["data", "setup", "dashboard", "clients", "events", "quote",
                "menu", "inventory", "shopping", "expenses", "income",
                "staff", "equipment", "suppliers", "calendar", "reports",
                "tax", "checklists", "invoice", "guide"],
    "basic": ["data", "setup", "dashboard", "clients", "events", "quote",
              "expenses", "income", "guide"],
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
    "clients": 40,
    "events": 40,
    "menu": 30,
    "inventory": 40,
    "shopping": 40,
    "expenses": 60,
    "income": 60,
    "staff": 50,
    "equipment": 35,
    "suppliers": 30,
}


def last_row(key):
    return ROW_FIRST + CAP[key] - 1


TICK = "\u2713"

# event pipeline
ES_INQUIRY = "\U0001F4AC Inquiry"
ES_QUOTED = "\U0001F4DD Quote Sent"
ES_DEPOSIT = "\U0001F4B0 Deposit Paid"
ES_CONFIRMED = "\u2705 Confirmed"
ES_DONE = "\U0001F389 Completed"
ES_CANCEL = "\u274C Cancelled"
EVENT_STATUSES = [ES_INQUIRY, ES_QUOTED, ES_DEPOSIT, ES_CONFIRMED, ES_DONE,
                  ES_CANCEL]

PS_UNPAID = "\U0001F534 Unpaid"
PS_PART = "\U0001F7E0 Partial"
PS_PAID = "\U0001F7E2 Paid in full"
PAYMENT_STATUSES = [PS_UNPAID, PS_PART, PS_PAID]

EVENT_TYPES = ["Wedding", "Corporate", "Birthday", "Private Party", "Buffet",
               "Cocktail", "Conference", "Festival", "Other"]
EXPENSE_CATEGORIES = ["Ingredients", "Packaging", "Staff / Labor",
                      "Transportation", "Equipment", "Kitchen Rental",
                      "Marketing", "Insurance", "Utilities", "Software",
                      "Miscellaneous"]
PAYMENT_METHODS = ["Cash", "Bank Transfer", "Card", "Cheque", "Mobile Wallet",
                   "Other"]
STAFF_ROLES = ["Head Chef", "Chef", "Sous Chef", "Server", "Bartender",
               "Driver", "Setup Crew", "Cleaner", "Manager", "Other"]
MENU_CATEGORIES = ["Starter", "Main", "Dessert", "Sides", "Beverage",
                   "Canapé", "Other"]
INGREDIENT_CATEGORIES = ["Produce", "Meat & Fish", "Dairy", "Pantry",
                         "Bakery", "Beverages", "Packaging", "Other"]

# ===========================================================================
# SETUP SHEET
# ===========================================================================
SU_BUSINESS = 6
SU_MESSAGE = 7
SU_CURRENCY = 10
SU_TAX = 11
SU_MARGIN = 12
SU_DEPOSIT = 13
SU_DUESOON = 14
SU_YEAR = 15
SU_CAL_MONTH = 18
SU_CAL_YEAR = 19

SU_LIST_HEADER = 22
SU_LIST_FIRST = 23
SU_LIST_ROWS = 20
LIST_COLS = {"event_types": "B", "expense_categories": "C",
             "payment_methods": "D", "staff_roles": "E",
             "menu_categories": "F", "ingredient_categories": "G"}
LIST_TITLES = {"event_types": "Event types",
               "expense_categories": "Expense categories",
               "payment_methods": "Payment methods",
               "staff_roles": "Staff roles",
               "menu_categories": "Menu categories",
               "ingredient_categories": "Ingredient categories"}

SU_FIXED_HEADER = 46
SU_FIXED_FIRST = 47
FIXED_COLS = {"event_statuses": "C", "payment_statuses": "D", "tick": "E"}

CURRENCIES = ["$", "€", "£", "¥", "₨", "₹", "A$", "C$", "R", "kr", "CHF"]

# ===========================================================================
# COLUMN MAPS  (field -> column letter)
# ===========================================================================
COLS = {
    "clients": {"n": "B", "name": "C", "phone": "D", "email": "E",
                "event_date": "F", "event_type": "G", "guests": "H",
                "venue": "I", "package": "J", "quote": "K", "deposit": "L",
                "balance": "M", "status": "N", "notes": "O"},
    "events": {"n": "B", "id": "C", "client": "D", "date": "E", "type": "F",
               "guests": "G", "menu": "H", "staff_req": "I",
               "equipment_req": "J", "cost": "K", "price": "L",
               "profit": "M", "margin": "N", "deposit": "O",
               "balance": "P", "status": "Q", "notes": "R"},
    "menu": {"n": "B", "item": "C", "category": "D", "ingredients": "E",
             "portion": "F", "cost": "G", "price": "H", "profit": "I",
             "margin": "J", "notes": "K"},
    "inventory": {"n": "B", "ingredient": "C", "category": "D", "unit": "E",
                  "qty": "F", "min": "G", "unit_cost": "H", "value": "I",
                  "supplier": "J", "status": "K", "notes": "L"},
    "shopping": {"n": "B", "event": "C", "ingredient": "D", "required": "E",
                 "available": "F", "to_buy": "G", "supplier": "H",
                 "est_cost": "I", "purchased": "J", "date": "K",
                 "notes": "L"},
    "expenses": {"n": "B", "date": "C", "vendor": "D", "category": "E",
                 "desc": "F", "amount": "G", "method": "H", "event": "I",
                 "receipt": "J"},
    "income": {"n": "B", "invoice": "C", "client": "D", "event_date": "E",
               "amount": "F", "deposit": "G", "pay1": "H", "pay2": "I",
               "received": "J", "balance": "K", "due": "L", "status": "M"},
    "staff": {"n": "B", "name": "C", "role": "D", "event": "E", "hours": "F",
              "rate": "G", "ot": "H", "total": "I", "paid": "J",
              "notes": "K"},
    "equipment": {"n": "B", "item": "C", "category": "D", "owned": "E",
                  "reserved": "F", "damaged": "G", "available": "H",
                  "unit_value": "I", "value": "J", "maintenance": "K",
                  "status": "L"},
    "suppliers": {"n": "B", "supplier": "C", "contact": "D", "phone": "E",
                  "email": "F", "category": "G", "item": "H", "price": "I",
                  "min_order": "J", "delivery": "K", "terms": "L",
                  "notes": "M"},
}

WIDTHS = {
    "clients": {"A": 2.2, "B": 4.5, "C": 20, "D": 14, "E": 30, "F": 12,
                "G": 13, "H": 8, "I": 26, "J": 16, "K": 11, "L": 11,
                "M": 11, "N": 15, "O": 26},
    "events": {"A": 2.2, "B": 4.5, "C": 10, "D": 21, "E": 12, "F": 13,
               "G": 8, "H": 30, "I": 9, "J": 22, "K": 11, "L": 11, "M": 11,
               "N": 9, "O": 11, "P": 11, "Q": 16, "R": 24},
    "menu": {"A": 2.2, "B": 4.5, "C": 24, "D": 12, "E": 34, "F": 12,
             "G": 12, "H": 11, "I": 11, "J": 9, "K": 24},
    "inventory": {"A": 2.2, "B": 4.5, "C": 22, "D": 14, "E": 8, "F": 10,
                  "G": 10, "H": 10, "I": 12, "J": 18, "K": 14, "L": 22},
    "shopping": {"A": 2.2, "B": 4.5, "C": 12, "D": 22, "E": 10, "F": 10,
                 "G": 11, "H": 18, "I": 11, "J": 10, "K": 12, "L": 22},
    "expenses": {"A": 2.2, "B": 4.5, "C": 12, "D": 20, "E": 16, "F": 34,
                 "G": 11, "H": 14, "I": 12, "J": 14},
    "income": {"A": 2.2, "B": 4.5, "C": 12, "D": 20, "E": 12, "F": 12,
               "G": 11, "H": 11, "I": 11, "J": 12, "K": 12, "L": 12,
               "M": 15},
    "staff": {"A": 2.2, "B": 4.5, "C": 18, "D": 13, "E": 12, "F": 8,
              "G": 10, "H": 8, "I": 12, "J": 9, "K": 22},
    "equipment": {"A": 2.2, "B": 4.5, "C": 27, "D": 14, "E": 8, "F": 10,
                  "G": 9, "H": 10, "I": 11, "J": 12, "K": 13, "L": 16},
    "suppliers": {"A": 2.2, "B": 4.5, "C": 20, "D": 16, "E": 14, "F": 29,
                  "G": 16, "H": 27, "I": 10, "J": 10, "K": 10, "L": 14,
                  "M": 22},
}

# ===========================================================================
# _Data layout
# ===========================================================================
DATA_MONTH_FIRST = 2          # H..L : month, revenue, expenses, profit, events
DATA_EXP_FIRST = 2            # N..O : expense category, spend (pie chart)
DATA_TYPE_FIRST = 16          # N..O : event type, revenue
DATA_STATUS_FIRST = 28        # N..O : event status, count (doughnut chart)
DATA_CLIENT_FIRST = 26        # Q..R : client, revenue
DATA_MENU_FIRST = 26          # T..U : menu item, times booked
DATA_POOL_FIRST = 2           # AA..AC : upcoming events pool (date,label,kind)
DATA_DUE_FIRST = 42           # AA..AC second block: outstanding payments
DATA_POOL_ROWS = 40           # events sheet has 40 rows
DATA_DUE_ROWS = 60            # income sheet has 60 rows
KPI_COL_LABEL = "AE"
KPI_COL_VALUE = "AF"

# ===========================================================================
# quote calculator geometry (block sheet)
# ===========================================================================
QUOTE_ROWS = {"client": 10, "date": 11, "guests": 12,
              "food_pp": 14, "labor": 15, "equipment": 16, "transport": 17,
              "other": 18, "margin": 20, "deposit_pct": 21}
QUOTE_OUT = {"food_total": 14, "cost_total": 15, "price": 16,
             "per_guest": 17, "profit": 18, "margin": 19, "deposit": 20,
             "balance": 21, "cost_pp": 22}
QUOTE_LAST_ROW = 26

# ===========================================================================
# tax tracker geometry
# ===========================================================================
TAX_SUM = {"sales": 9, "rate": 10, "collected": 11, "paid": 12, "due": 13}
TAX_LOG_HDR = 19
TAX_LOG_FIRST = 20
TAX_LOG_ROWS = 20
TAX_COLS = {"n": "B", "date": "C", "desc": "D", "amount": "G", "method": "H"}


KPI_ROW = {}                  # filled below
KPI_FMT = {}

_KPI_SPECS = [
    ("revenue", "Cash received (deposits + payments)", "#,##0"),
    ("expenses", "Total expenses", "#,##0"),
    ("profit", "Net profit", "#,##0"),
    ("margin", "Net profit margin", "0%"),
    ("events_total", "Events on the books", "0"),
    ("events_done", "Events completed", "0"),
    ("events_confirmed", "Events confirmed (upcoming)", "0"),
    ("events_cancelled", "Events cancelled", "0"),
    ("avg_order", "Average order value", "#,##0"),
    ("avg_guests", "Average guests per event", "0"),
    ("avg_profit", "Average profit per event", "#,##0"),
    ("guests_total", "Guests catered (completed)", "0"),
    ("outstanding", "Outstanding receivables", "#,##0"),
    ("overdue", "Overdue invoices", "0"),
    ("invoices_open", "Invoices still open", "0"),
    ("food_cost", "Ingredient & packaging spend", "#,##0"),
    ("labor_cost", "Staff / labor spend", "#,##0"),
    ("food_pct", "Food cost % of revenue", "0%"),
    ("labor_pct", "Labor cost % of revenue", "0%"),
    ("repeat_pct", "Repeat customer %", "0%"),
    ("inv_value", "Inventory value", "#,##0.00"),
    ("low_stock", "Ingredients below minimum", "0"),
    ("shop_lines", "Shopping lines open", "0"),
    ("shop_cost", "Shopping list estimated cost", "#,##0.00"),
    ("staff_unpaid", "Unpaid staff shifts", "0"),
    ("equip_value", "Equipment value", "#,##0"),
    ("equip_service", "Equipment needing service", "0"),
    ("tax_collected", "Tax collected on sales", "#,##0.00"),
    ("tax_due", "Estimated tax still due", "#,##0.00"),
    ("quote_price", "Quote calculator: recommended price", "#,##0.00"),
    ("quote_per_guest", "Quote calculator: price per guest", "#,##0.00"),
    ("menu_items", "Menu items priced", "0"),
    ("menu_margin", "Average menu margin", "0%"),
    ("best_type", "Best earning event type", "@"),
    ("best_client", "Highest value client", "@"),
]
for _i, (_key, _label, _fmt) in enumerate(_KPI_SPECS):
    KPI_ROW[_key] = 2 + _i
    KPI_FMT[_key] = _fmt

KPI_LABEL = {k: label for k, label, _ in _KPI_SPECS}

# ===========================================================================
# calendar geometry
# ===========================================================================
CAL_GRID_ROW = 12             # first row of the 6x7 grid
CAL_CELL_H = 62
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]
