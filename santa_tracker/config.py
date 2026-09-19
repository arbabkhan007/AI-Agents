"""Geometry, column maps, caps and list definitions for the
Secret Santa + White Elephant Party Tracker (Novality Store)."""

PRODUCT = "Secret Santa & White Elephant Party Tracker"
PRODUCT_SHORT = "Party Tracker"
TAGLINE = "draws, budgets, wishlists and white-elephant chaos - handled"
AUTHOR = "Novality Store"
VERSION = "1.0.0"

# protection password for locked (formula) cells
PROTECT_PASSWORD = "premium"

# ---------------------------------------------------------------------------
# sheet keys, tab names, editions
# ---------------------------------------------------------------------------
SHEET_NAMES = {
    "data": "_Data",
    "setup": "\u2699\ufe0f Settings & Instructions",
    "dashboard": "\U0001F3E0 Dashboard",
    "participants": "\U0001F465 Participants",
    "draw": "\U0001F385 Secret Santa Draw",
    "rules": "\U0001F6AB Exclusions & Rules",
    "budget": "\U0001F4B0 Budget Tracker",
    "wishlists": "\U0001F381 Wishlists",
    "we": "\U0001F3B2 White Elephant",
    "history": "\U0001F504 Game History",
    "cards": "\U0001F39F\ufe0f Santa Cards",
    "guide": "\U0001F4D6 Start Here",
}
SHEET_SHORT = {
    "data": "Data", "setup": "Settings", "dashboard": "Dashboard",
    "participants": "People", "draw": "Draw", "rules": "Rules",
    "budget": "Budget", "wishlists": "Wishlists", "we": "White Elephant",
    "history": "History", "cards": "Cards", "guide": "Start Here",
}

EDITIONS = {
    "premium": ["data", "setup", "dashboard", "participants", "draw",
                "rules", "budget", "wishlists", "we", "history", "cards",
                "guide"],
    "basic": ["data", "setup", "dashboard", "participants", "draw",
              "budget", "guide"],
}

# ---------------------------------------------------------------------------
# band geometry (rows 1-7) shared by every table sheet
# ---------------------------------------------------------------------------
ROW_SPACER_1 = 1
ROW_TITLE = 2
ROW_SUBTITLE = 3
ROW_SPACER_2 = 4
ROW_STATS = 5
ROW_SPACER_3 = 6
ROW_HEADER = 7
ROW_FIRST = 8


def last_row(key):
    return ROW_FIRST + CAP[key] - 1


def cols_last(key):
    return COLS_LAST[key]


CAP = {
    "participants": 24,
    "draw": 24,
    "rules": 16,
    "budget": 24,
    "wishlists": 40,
    "we": 24,
    "history": 60,
}

COLS = {
    "participants": {"n": "A", "name": "B", "team": "C", "household": "D",
                     "rsvp": "E", "diet": "F", "lastyear": "G",
                     "status": "H", "wishes": "I", "notes": "J"},
    "draw": {"n": "A", "giver": "B", "computed": "C", "override": "D",
             "final": "E", "flag": "F", "status": "G"},
    "rules": {"n": "A", "giver": "B", "cannot": "C", "reason": "D"},
    "budget": {"n": "A", "name": "B", "min": "C", "max": "D", "spent": "E",
               "flag": "F", "receipt": "G", "ref": "H", "notes": "I"},
    "wishlists": {"n": "A", "who": "B", "item": "C", "priority": "D",
                  "link": "E", "claimed": "F", "notes": "G"},
    "we": {"n": "A", "order": "B", "player": "C", "giftnum": "D",
           "desc": "E", "value": "F", "steals": "G", "maxsteals": "H",
           "status": "I", "holder": "J", "stolenfrom": "K", "final": "L",
           "key1": "M", "key2": "N"},
    "history": {"n": "A", "turn": "B", "player": "C", "action": "D",
                "gift": "E", "stolenfrom": "F"},
}
COLS_LAST = {
    "participants": "J", "draw": "G", "rules": "D", "budget": "I",
    "wishlists": "G", "we": "L", "history": "F",
}

WIDTHS = {
    "participants": {"A": 2.2, "B": 20, "C": 12, "D": 12, "E": 9, "F": 16,
                     "G": 16, "H": 15, "I": 8, "J": 34},
    "draw": {"A": 2.2, "B": 20, "C": 20, "D": 20, "E": 20, "F": 22,
             "G": 15},
    "rules": {"A": 2.2, "B": 20, "C": 20, "D": 32},
    "budget": {"A": 2.2, "B": 20, "C": 9, "D": 9, "E": 10, "F": 17,
               "G": 9, "H": 14, "I": 22},
    "wishlists": {"A": 2.2, "B": 20, "C": 30, "D": 13, "E": 22, "F": 9,
                  "G": 20},
    "we": {"A": 2.2, "B": 7, "C": 20, "D": 7, "E": 26, "F": 10, "G": 8,
           "H": 8, "I": 13, "J": 18, "K": 16, "L": 9, "M": 10, "N": 10},
    "history": {"A": 2.2, "B": 7, "C": 20, "D": 10, "E": 9, "F": 18},
    "dashboard": {"A": 2.2, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13,
                  "G": 13, "H": 13, "I": 13, "J": 13, "K": 13, "L": 13,
                  "M": 13, "N": 13},
    "setup": {"A": 2.2, "B": 38, "C": 24, "D": 16, "E": 16, "F": 16,
              "G": 16},
    "cards": {"A": 2.2, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13,
              "G": 13, "H": 13, "I": 13},
    "guide": {"A": 2.2, "B": 4, "C": 15, "D": 15, "E": 24, "F": 16,
              "G": 16, "H": 16, "I": 16, "J": 16},
}

# ---------------------------------------------------------------------------
# settings rows
# ---------------------------------------------------------------------------
SU_BUSINESS = 6        # party name
SU_MESSAGE = 7         # dashboard message
SU_CURRENCY = 10
SU_YEAR = 11           # party year
SU_DATE = 12           # party date
SU_LOCATION = 13
SU_HOST = 14
SU_BMIN = 15
SU_BMAX = 16
SU_STEALS = 17
SU_START = 18
SU_SEED = 19           # secret santa draw seed
SU_WESEED = 20         # white elephant seed
SU_STATUS = 21         # Draft / Final lock flag
SU_LIST_HEADER = 25
SU_LIST_FIRST = 26
SU_LIST_ROWS = 16
SU_FIXED_FIRST = 46

LIST_COLS = {"teams": "C", "diets": "D"}

FIXED_BLOCKS = {
    "Statuses": ("C", 4),     # Not Started / Gift Purchased / Wrapped / Complete
    "RSVP": ("D", 3),         # Yes / No / Maybe
    "Actions": ("E", 2),      # Pick / Steal
    "Priorities": ("F", 3),   # Must-love / Nice to have / Just an idea
    "Tick": ("G", 2),         # ✓ / blank
    "OnOff": ("H", 2),        # On / Off
}

TICK = "\u2713"

# statuses
ST_NOT = "Not Started"
ST_BOUGHT = "Gift Purchased"
ST_WRAPPED = "Wrapped"
ST_DONE = "Complete"

# gift statuses (white elephant)
GS_AVAIL = "\U0001F381 Available"
GS_HELD = "\U0001F932 Held"
GS_STOLEN = "\U0001F504 Stolen"
GS_FINAL = "\U0001F512 Final"

# budget flags
BF_UNDER = "\U0001F534 Under budget"
BF_OK = "\u2705 Within budget"
BF_OVER = "\U0001F6A8 Over budget"

# draw lock
DRAW_DRAFT = "Draft \u2014 re-draw allowed"
DRAW_FINAL = "Final \u2014 locked \U0001F512"

# ---------------------------------------------------------------------------
# _Data layout
# ---------------------------------------------------------------------------
DATA_KPI_FIRST = 2          # KPI label col AH, value col AI
KPI_ROW = {
    "participants": 2,
    "rsvp_yes": 3,
    "rsvp_pending": 4,
    "assigned": 5,
    "purchased": 6,
    "wrapped": 7,
    "complete": 8,
    "total_budget": 9,
    "spent": 10,
    "avg_gift": 11,
    "rules_count": 12,
    "we_players": 13,
    "gifts_in_play": 14,
    "locked_gifts": 15,
    "completion": 16,
    "turns_done": 17,
    "current_turn": 18,
    "violations": 19,
    "over_budget": 20,
    "diets": 21,
}
KPI_FMT = {
    "participants": "#,##0", "rsvp_yes": "#,##0", "rsvp_pending": "#,##0",
    "assigned": "#,##0", "purchased": "#,##0", "wrapped": "#,##0",
    "complete": "#,##0", "total_budget": "#,##0.00", "spent": "#,##0.00",
    "avg_gift": "#,##0.00", "rules_count": "#,##0", "we_players": "#,##0",
    "gifts_in_play": "#,##0", "locked_gifts": "#,##0", "completion": "0%",
    "turns_done": "#,##0", "current_turn": "#,##0", "violations": "#,##0",
    "over_budget": "#,##0", "diets": "#,##0",
}

# dashboard rows
DASH_HERO = 2
DASH_MSG = 5
DASH_CARD1_L = 8
DASH_CARD1_V = 9
DASH_CARD2_L = 10
DASH_CARD2_V = 11
DASH_BAR1 = 12
DASH_BAR2 = 13
DASH_CHART1 = 16
DASH_CHART2 = 32
DASH_CHART3 = 48
DASH_PANEL = 64
DASH_FOOTER = 72
DASH_NAV = 74

# white elephant / draw control rows
WE_CTRL_ROW = 5
HIST_NOTE_ROW = 5
