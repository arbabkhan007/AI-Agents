"""
Single source of truth for the workbook layout.

Every sheet builder reads its geometry from here, which is what makes the
cross-sheet formulas (dashboard -> gift tracker -> budget -> ...) safe:
nothing hard-codes a cell address twice.

All row numbers in this module are **1-indexed** (spreadsheet style); the
sheet builders convert to XlsxWriter's 0-indexed API with ``r()``.
"""

# ===========================================================================
# PRODUCT
# ===========================================================================
PRODUCT = "Ultimate Christmas Gift Tracker"
PRODUCT_SHORT = "Christmas Gift Tracker"
TAGLINE = "Christmas \u2022 Birthdays \u2022 Holidays \u2022 Every Special Occasion"
AUTHOR = "Novality Store"
VERSION = "1.0"

# ===========================================================================
# SHEETS
# ===========================================================================
SHEET_NAMES = {
    "dashboard": "\U0001F384 Dashboard",
    "gifts":     "\U0001F381 Gift Tracker",
    "budget":    "\U0001F4B0 Budget",
    "wishlist":  "\U0001F4A1 Wish List",
    "shopping":  "\U0001F6CD\uFE0F Shopping List",
    "orders":    "\U0001F4E6 Order Tracker",
    "wrapping":  "\U0001F380 Wrapping & Hiding",
    "cards":     "\U0001F48C Card Tracker",
    "stockings": "\U0001F9E6 Stockings",
    "todo":      "\u2705 To-Do List",
    "setup":     "\u2699\uFE0F Setup",
    "guide":     "\U0001F4D6 Start Here",
    "data":      "_Data",
}

# Short labels used by the navigation buttons.
SHEET_SHORT = {
    "dashboard": "\U0001F3E0 Home",
    "gifts":     "\U0001F381 Gifts",
    "budget":    "\U0001F4B0 Budget",
    "wishlist":  "\U0001F4A1 Ideas",
    "shopping":  "\U0001F6CD\uFE0F Shop",
    "orders":    "\U0001F4E6 Orders",
    "wrapping":  "\U0001F380 Wrap",
    "cards":     "\U0001F48C Cards",
    "stockings": "\U0001F9E6 Stockings",
    "todo":      "\u2705 To-Do",
    "setup":     "\u2699\uFE0F Setup",
    "guide":     "\U0001F4D6 Help",
}

# Tab order per edition ("data" is always last and hidden).
EDITIONS = {
    "premium": ["dashboard", "gifts", "budget", "wishlist", "shopping",
                "orders", "wrapping", "cards", "stockings", "todo",
                "setup", "guide", "data"],
    "basic":   ["dashboard", "gifts", "budget", "shopping",
                "setup", "guide", "data"],
}

PREMIUM_ONLY = ("wishlist", "orders", "wrapping", "cards", "stockings", "todo")

# ===========================================================================
# DATA-SHEET GEOMETRY  (identical header band on every tracker tab)
# ===========================================================================
ROW_SPACER_1 = 1      # thin top margin
ROW_TITLE = 2         # big sheet title
ROW_SUBTITLE = 3      # one-line description + "back to dashboard" link
ROW_SPACER_2 = 4
ROW_STATS = 5         # quick-stat strip (formula driven)
ROW_SPACER_3 = 6
ROW_HEADER = 7        # column headers
ROW_FIRST = 8         # first data row

CAP = {
    "gifts": 60,
    "shopping": 45,
    "orders": 40,
    "cards": 40,
    "stockings": 45,
    "wishlist": 40,
    "todo": 40,
    "wrapping": 60,   # mirrors the gift tracker row-for-row
}

RECIPIENT_SLOTS = 16      # dashboard / chart capacity
CATEGORY_SLOTS = 16


def last_row(key):
    """Last data row (1-indexed) of a tracker sheet."""
    return ROW_FIRST + CAP[key] - 1


# ===========================================================================
# COLUMN MAPS  (letter per logical field)
# ===========================================================================
GIFT_COLS = {
    "n": "B", "recipient": "C", "relationship": "D", "idea": "E",
    "category": "F", "store": "G", "link": "H", "open": "I",
    "budget": "J", "cost": "K", "diff": "L", "pct": "M",
    "status": "N", "wrapped": "O", "delivered": "P",
    "deadline": "Q", "days": "R", "alert": "S", "notes": "T",
}

SHOP_COLS = {
    "n": "B", "item": "C", "category": "D", "store": "E", "qty": "F",
    "unit": "G", "total": "H", "bought": "I", "cost": "J", "spent": "K",
    "link": "L", "notes": "M",
}

ORDER_COLS = {
    "n": "B", "recipient": "C", "item": "D", "store": "E", "order_no": "F",
    "order_date": "G", "expected": "H", "actual": "I", "link": "J",
    "open": "K", "status": "L", "days": "M", "alert": "N",
    "return_by": "O", "returned": "P", "cost": "Q", "notes": "R",
}

WRAP_COLS = {
    "n": "B", "recipient": "C", "idea": "D", "bought": "E", "wrapped": "F",
    "hiding": "G", "tag": "H", "delivered": "I", "notes": "J",
}

CARD_COLS = {
    "n": "B", "name": "C", "relationship": "D", "address": "E",
    "bought": "F", "written": "G", "sent": "H", "date_sent": "I",
    "received": "J", "postage": "K", "status": "L", "notes": "M",
}

STOCK_COLS = {
    "n": "B", "owner": "C", "item": "D", "category": "E", "budget": "F",
    "cost": "G", "bought": "H", "wrapped": "I", "spent": "J",
    "hiding": "K", "notes": "L",
}

WISH_COLS = {
    "n": "B", "person": "C", "idea": "D", "category": "E", "link": "F",
    "open": "G", "price": "H", "priority": "I", "in_tracker": "J",
    "notes": "K",
}

TODO_COLS = {
    "done": "B", "task": "C", "category": "D", "deadline": "E",
    "days": "F", "status": "G", "notes": "H",
}

BUDGET_COLS = {
    "category": "B", "planned": "C", "manual": "D", "auto": "E",
    "actual": "F", "remaining": "G", "pct": "H", "status": "I",
    "bar": "J", "notes": "K",
}

COLS = {
    "gifts": GIFT_COLS,
    "shopping": SHOP_COLS,
    "orders": ORDER_COLS,
    "wrapping": WRAP_COLS,
    "cards": CARD_COLS,
    "stockings": STOCK_COLS,
    "wishlist": WISH_COLS,
    "todo": TODO_COLS,
    "budget": BUDGET_COLS,
}

# Column widths per sheet (letters are positional: A, B, C ...).
WIDTHS = {
    "gifts":     {"A": 2.2, "B": 4.5, "C": 18, "D": 12, "E": 27, "F": 13,
                  "G": 22, "H": 26, "I": 8.5, "J": 11, "K": 11, "L": 11,
                  "M": 9.5, "N": 16, "O": 9, "P": 9.5, "Q": 12, "R": 8.5,
                  "S": 13, "T": 30},
    "shopping":  {"A": 2.2, "B": 4.5, "C": 28, "D": 16, "E": 14, "F": 7,
                  "G": 11, "H": 11, "I": 10, "J": 11, "K": 11, "L": 20,
                  "M": 28},
    "orders":    {"A": 2.2, "B": 4.5, "C": 18, "D": 26, "E": 20, "F": 20,
                  "G": 12, "H": 13, "I": 13, "J": 26, "K": 8.5, "L": 17,
                  "M": 9, "N": 13, "O": 12, "P": 9.5, "Q": 11, "R": 26},
    "wrapping":  {"A": 2.2, "B": 4.5, "C": 16, "D": 28, "E": 13, "F": 13,
                  "G": 26, "H": 10, "I": 13, "J": 26},
    "cards":     {"A": 2.2, "B": 4.5, "C": 20, "D": 13, "E": 40, "F": 10,
                  "G": 10, "H": 9.5, "I": 12, "J": 10.5, "K": 10, "L": 15,
                  "M": 26},
    "stockings": {"A": 2.2, "B": 4.5, "C": 16, "D": 26, "E": 14, "F": 10.5,
                  "G": 10.5, "H": 10, "I": 10, "J": 10.5, "K": 24, "L": 24},
    "wishlist":  {"A": 2.2, "B": 4.5, "C": 16, "D": 30, "E": 14, "F": 28,
                  "G": 8.5, "H": 11, "I": 18, "J": 16, "K": 26},
    "todo":      {"A": 2.2, "B": 8, "C": 40, "D": 15, "E": 12, "F": 9,
                  "G": 15, "H": 30},
}

# ===========================================================================
# BUDGET TAB
# ===========================================================================
BUD_STATS_ROW = 5           # first row of the summary card block
BUD_HEADER = 14             # table header row
BUD_FIRST = 15              # first category row
BUD_TOTAL = 25              # totals row (BUD_FIRST + 10)

# (label, key, auto-link recipe, demo planned amount)
#   recipe terms: "gifts" = gift tracker actual cost,
#                 "shop:<Category>" = shopping list spend for that category,
#                 "stock" = stocking spend, "cards" = card postage spend
BUDGET_CATEGORIES = [
    ("\U0001F381 Gifts",              "gifts",     ["gifts", "shop:Gifts"], 850),
    ("\U0001F9E6 Stocking stuffers",  "stockings", ["stock", "shop:Stockings"], 140),
    ("\U0001F380 Wrapping & packaging", "wrapping", ["shop:Wrapping"], 55),
    ("\U0001F48C Cards & postage",    "cards",     ["shop:Cards", "shop:Postage", "cards"], 40),
    ("\U0001F35D Food & drink",       "food",      ["shop:Food"], 200),
    ("\U0001F36A Baking & treats",    "baking",    ["shop:Baking"], 35),
    ("\U0001F384 Decorations & tree", "decor",     ["shop:Decorations"], 60),
    ("\U0001F389 Party & entertaining", "party",   ["shop:Party Supplies"], 45),
    ("\U0001F697 Travel",             "travel",    ["shop:Travel"], 35),
    ("\u2764 Charity & other",        "other",     ["shop:Charity", "shop:Other"], 40),
]
BUDGET_ROWS = len(BUDGET_CATEGORIES)

# ===========================================================================
# SETUP TAB
# ===========================================================================
SU_EVENT_NAME = 6
SU_EVENT_DATE = 7
SU_DAYS = 8
SU_YEAR = 9
SU_WEEKS = 10
SU_MESSAGE = 11
SU_OCCASION = 14
SU_SUG_NAME = 15
SU_SUG_DATE = 16
SU_CURRENCY = 21
SU_BUDGET = 22
SU_ALERT = 23
SU_DUESOON = 24
SU_SECRET = 25
SU_COUNT_ORDERED = 26
SU_LIST_HEADER = 29
SU_LIST_FIRST = 30
SU_LIST_ROWS = 20
SU_FIXED_HEADER = 53
SU_FIXED_FIRST = 54

# Editable lists (dynamic named ranges) - column letter on the Setup sheet.
LIST_COLS = {
    "recipients": "B",
    "relationships": "C",
    "gift_categories": "D",
    "stores": "E",
    "shop_categories": "F",
    "hiding_spots": "G",
    "todo_categories": "H",
    "stocking_owners": "I",
    "stocking_items": "J",
}

LIST_TITLES = {
    "recipients": "\U0001F46A Recipients",
    "relationships": "\U0001F465 Relationships",
    "gift_categories": "\U0001F3F7\uFE0F Gift categories",
    "stores": "\U0001F3EC Stores",
    "shop_categories": "\U0001F6D2 Shopping categories",
    "hiding_spots": "\U0001F648 Hiding spots",
    "todo_categories": "\U0001F4CB To-do categories",
    "stocking_owners": "\U0001F9E6 Stocking owners",
    "stocking_items": "\U0001F36C Stocking items",
}

# Fixed lists (formulas and colours depend on this exact wording).
FIXED_COLS = {"statuses": "B", "order_statuses": "C", "priorities": "D",
              "tick": "E"}

# ===========================================================================
# LIST CONTENTS
# ===========================================================================
STATUSES = [
    "\U0001F4A1 Idea",
    "\U0001F6D2 Need to Buy",
    "\U0001F6CD\uFE0F Ordered",
    "\u2705 Purchased",
    "\U0001F380 Wrapped",
    "\U0001F4E6 Delivered",
]
ST_IDEA, ST_NEED, ST_ORDERED, ST_BOUGHT, ST_WRAPPED, ST_DELIVERED = STATUSES

ORDER_STATUSES = [
    "\U0001F6D2 Ordered",
    "\U0001F4E6 Shipped",
    "\U0001F69A Out for Delivery",
    "\u2705 Delivered",
    "\u21A9\uFE0F Return Requested",
    "\u274C Cancelled",
]
OS_ORDERED, OS_SHIPPED, OS_OUT, OS_DELIVERED, OS_RETURN, OS_CANCEL = ORDER_STATUSES

PRIORITIES = ["\u2B50\u2B50\u2B50 Must Have", "\u2B50\u2B50 Maybe",
              "\u2B50 Low Priority"]
PR_MUST, PR_MAYBE, PR_LOW = PRIORITIES

TICK = "\u2713"

CURRENCIES = ["$", "\u00A3", "\u20AC", "\u00A5", "\u20B9", "R$", "A$", "C$",
              "kr", "z\u0142", "CHF", "RM", "\u20AA", "R"]

YESNO = ["Yes", "No"]

RELATIONSHIPS = ["Mum", "Dad", "Grandma", "Grandpa", "Sister", "Brother",
                 "Partner", "Son", "Daughter", "Niece", "Nephew", "Cousin",
                 "Aunt", "Uncle", "Friend", "Colleague", "Neighbour",
                 "Teacher", "Secret Santa", "Other"]

GIFT_CATEGORIES = ["Clothing", "Beauty", "Electronics", "Toys", "Books",
                   "Home", "Food & Drink", "Gift Card", "Handmade",
                   "Jewellery", "Games", "Sports", "Music", "Kids", "Pets",
                   "Experience", "Other"]

STORES = ["Amazon", "Etsy", "Target", "Walmart", "John Lewis", "Tesco",
          "Argos", "ASOS", "Sephora", "Best Buy", "IKEA", "M&S",
          "Local Bookshop", "Not On The High Street", "Handmade by me",
          "Other"]

SHOP_CATEGORIES = ["Gifts", "Stockings", "Wrapping", "Food", "Baking",
                   "Decorations", "Cards", "Postage", "Party Supplies",
                   "Travel", "Charity", "Other"]

HIDING_SPOTS = ["Top shelf in closet", "Under the bed", "Garage shelf",
                "Suitcase in the attic", "Back of the pantry",
                "Linen closet", "Shoe box in wardrobe", "Behind the books",
                "Under the stairs box", "Car boot / trunk",
                "Decoration box", "At work / office", "Friend's house"]

TODO_CATEGORIES = ["Gifts", "Wrapping", "Cards", "Food", "Decorations",
                   "Travel", "Party", "Family", "Admin", "Other"]

STOCKING_ITEMS = ["Candy", "Chocolate", "Socks", "Beauty", "Hair clips",
                  "Stationery", "Small toy", "Gift card", "Snacks",
                  "Novelty", "Other"]

# Preset occasions: (name, month, day).  month=None -> "you choose the date".
OCCASIONS = [
    ("Christmas", 12, 25),
    ("Christmas Eve", 12, 24),
    ("Secret Santa", 12, 20),
    ("Hanukkah", 12, 15),
    ("New Year's Eve", 12, 31),
    ("Valentine's Day", 2, 14),
    ("Mother's Day", 5, 10),
    ("Father's Day", 6, 21),
    ("Easter", 4, 5),
    ("Halloween", 10, 31),
    ("Thanksgiving", 11, 27),
    ("Diwali", 11, 12),
    ("Birthday", None, None),
    ("Anniversary", None, None),
    ("Baby Shower", None, None),
    ("Wedding", None, None),
    ("Graduation", None, None),
    ("Housewarming", None, None),
]
OCCASION_ROWS = len(OCCASIONS)

# Default recipient / stocking-owner lists used when the workbook ships blank.
BLANK_RECIPIENTS = ["Mum", "Dad", "Grandma Rose", "Grandpa Joe",
                    "Sister Emily", "Brother Jack", "Niece Sophie",
                    "Nephew Leo", "Alex (partner)", "Maya (best friend)",
                    "Cousin Dan", "Aunt Carol"]
BLANK_OWNERS = ["Emma", "Oliver", "Mum", "Dad"]

# ===========================================================================
# HIDDEN "_Data" SHEET
# ===========================================================================
DATA_PRESET_FIRST = 2          # occasion table rows 2..2+len(OCCASIONS)-1
DATA_MATCH_MONTH = "E2"
DATA_MATCH_DAY = "F2"

DATA_REC_FIRST = 2             # recipient table H..P
DATA_REC_ROWS = RECIPIENT_SLOTS
DATA_CAT_FIRST = 2             # category table Q..R
DATA_CAT_ROWS = CATEGORY_SLOTS
DATA_STATUS_FIRST = 2          # status table T..U
DATA_BUD_FIRST = 2             # budget table W..Y
DATA_POOL_FIRST = 2            # deadline pool AA..AC

DATA_KPI_FIRST = 2             # KPI table AE(label) / AF(value)

# KPI registry: key -> (human label, number format).  Row order matters only
# for readability; the row number is derived from the position in this list.
KPI = [
    ("days_to_event",      "Days until the event", "0"),
    ("event_year",         "Event year", "0"),
    ("gifts_planned",      "Gifts planned", "0"),
    ("gifts_purchased",    "Gifts purchased", "0"),
    ("gifts_wrapped",      "Gifts wrapped", "0"),
    ("gifts_delivered",    "Gifts delivered / given", "0"),
    ("gifts_to_buy",       "Gifts still to buy", "0"),
    ("gifts_ordered",      "Gifts on order", "0"),
    ("wrap_to_do",         "Bought but not wrapped", "0"),
    ("deliver_to_do",      "Wrapped but not delivered", "0"),
    ("gift_completion",    "Gift completion %", "0%"),
    ("recipients_gifted",  "Recipients with gifts", "0"),
    ("avg_per_recipient",  "Average spend per recipient", "#,##0.00"),
    ("gift_budget_planned", "Gift budgets entered", "#,##0.00"),
    ("gift_actual_spent",  "Gift money spent", "#,##0.00"),
    ("budget_planned",     "Total planned budget", "#,##0.00"),
    ("budget_actual",      "Total spent (everything)", "#,##0.00"),
    ("budget_remaining",   "Budget remaining", "#,##0.00"),
    ("budget_pct",         "Budget used %", "0%"),
    ("shop_total",         "Shopping list items", "0"),
    ("shop_bought",        "Shopping items bought", "0"),
    ("shop_spent",         "Shopping list spend", "#,##0.00"),
    ("cards_total",        "Cards to send", "0"),
    ("cards_written",      "Cards written", "0"),
    ("cards_sent",         "Cards sent", "0"),
    ("stock_budget",       "Stocking budget", "#,##0.00"),
    ("stock_spent",        "Stocking spend", "#,##0.00"),
    ("stock_items",        "Stocking items", "0"),
    ("stock_bought",       "Stocking items bought", "0"),
    ("orders_total",       "Online orders", "0"),
    ("orders_outstanding", "Orders still coming", "0"),
    ("orders_late",        "Orders running late", "0"),
    ("orders_value",       "Value of orders", "#,##0.00"),
    ("todo_total",         "To-do tasks", "0"),
    ("todo_done",          "To-do tasks done", "0"),
    ("todo_overdue",       "To-do tasks overdue", "0"),
    ("wish_total",         "Gift ideas saved", "0"),
    ("wish_must",          "Must-have ideas", "0"),
    ("wish_value",         "Value of saved ideas", "#,##0.00"),
]

KPI_ROW = {key: DATA_KPI_FIRST + i for i, (key, _label, _fmt) in enumerate(KPI)}
KPI_LABEL = {key: label for key, label, _fmt in KPI}
KPI_FMT = {key: fmt for key, _label, fmt in KPI}

# Deadline pool: gift rows, then to-do rows, then order rows.
POOL_GIFT_ROWS = CAP["gifts"]
POOL_TODO_ROWS = CAP["todo"]
POOL_ORDER_ROWS = CAP["orders"]


def pool_size(edition):
    n = POOL_GIFT_ROWS
    if edition == "premium":
        n += POOL_TODO_ROWS + POOL_ORDER_ROWS
    return n


# ===========================================================================
# MISC
# ===========================================================================
DEFAULT_EVENT_NAME = "Christmas"
DEFAULT_EVENT_YEAR = 2026
DEFAULT_EVENT_DATE = (DEFAULT_EVENT_YEAR, 12, 25)
DEFAULT_BUDGET = 1500
DEFAULT_ALERT = 0.85
DEFAULT_DUESOON = 7
DEFAULT_CURRENCY = "$"

# To-do presets: (task, category, days BEFORE the event date, done?)
TODO_PRESETS = [
    ("Write the gift list & set the budget", "Gifts", 75, False),
    ("Order Christmas cards", "Cards", 60, False),
    ("Buy wrapping paper, ribbon & tags", "Wrapping", 45, False),
    ("Address & write all cards", "Cards", 35, False),
    ("Post the cards", "Cards", 25, False),
    ("Order gifts that need delivery time", "Gifts", 30, False),
    ("Buy the main gifts", "Gifts", 21, False),
    ("Prepare the stockings", "Gifts", 18, False),
    ("Buy the decorations & set up the tree", "Decorations", 20, False),
    ("Plan the Christmas dinner menu", "Food", 14, False),
    ("Book travel / check the car", "Travel", 21, False),
    ("Bake cookies & treats", "Food", 10, False),
    ("Buy the groceries", "Food", 5, False),
    ("Wrap the presents", "Wrapping", 7, False),
    ("Hide the wrapped gifts", "Wrapping", 6, False),
    ("Mail any packages", "Admin", 12, False),
    ("Confirm plans with family", "Family", 10, False),
    ("Charge cameras / buy batteries", "Admin", 4, False),
    ("Set the table & plan outfits", "Party", 3, False),
    ("Write the thank-you list", "Admin", -5, False),
]

# Shopping list presets used by the blank workbook (a helpful starter list).
SHOP_PRESETS = [
    ("Wrapping paper (3 rolls)", "Wrapping", "Target", 3, 4.00),
    ("Ribbon - red & gold", "Wrapping", "Amazon", 2, 3.50),
    ("Gift tags (pack of 50)", "Wrapping", "Etsy", 1, 6.00),
    ("Sticky tape & scissors", "Wrapping", "Target", 1, 5.00),
    ("Christmas cards (box of 30)", "Cards", "Amazon", 1, 14.00),
    ("Stamps", "Postage", "Post office", 30, 0.68),
    ("Plain flour", "Baking", "Grocery store", 2, 1.80),
    ("Cookie cutters", "Baking", "Amazon", 1, 8.00),
    ("Christmas crackers", "Party Supplies", "Target", 2, 5.50),
    ("Napkins & party plates", "Party Supplies", "Target", 1, 7.00),
    ("Tree baubles (gold)", "Decorations", "IKEA", 2, 9.00),
    ("Fairy lights", "Decorations", "Amazon", 1, 15.00),
    ("Wrapping tissue paper", "Wrapping", "Target", 1, 3.00),
    ("Chocolate for stockings", "Stockings", "Grocery store", 4, 3.20),
]
