"""
Sample data ("demo" mode) + the Python twin of every workbook calculation.

Two jobs:

1.  Provide a realistic filled-in example so the product can be screenshotted
    for the Etsy listing (``mode="demo"``).
2.  Compute the *cached values* that XlsxWriter stores next to each formula.
    Excel and Google Sheets both recalculate on open (``fullCalcOnLoad``), but
    the cached values mean the dashboard also looks right in previewers,
    thumbnailers and print-to-PDF tools that never calculate.

The functions in :func:`compute` mirror the worksheet formulas exactly - if
you change a formula in a sheet builder, change its twin here.
"""

from datetime import date, timedelta

from . import config as C

TODAY = date.today()
EVENT_DATE = date(*C.DEFAULT_EVENT_DATE)


def _d(offset_days):
    """A date ``offset_days`` from the event date (negative = before)."""
    return EVENT_DATE + timedelta(days=offset_days)


# ===========================================================================
# GIFT TRACKER
# ===========================================================================
# (recipient, relationship, idea, category, store, link, budget, cost,
#  status, wrapped, delivered, deadline offset, notes)
GIFTS = [
    ("Mum", "Mum", "Cashmere scarf", "Clothing", "John Lewis",
     "https://www.johnlewis.com", 60, 55.00, C.ST_BOUGHT, True, False, -10,
     "Wanted burgundy or cream"),
    ("Mum", "Mum", "Spa gift set", "Beauty", "Sephora",
     "https://www.sephora.com", 45, 42.99, C.ST_WRAPPED, True, False, -10, ""),
    ("Dad", "Dad", "Leather wallet", "Clothing", "Amazon",
     "https://www.amazon.com", 40, 38.50, C.ST_DELIVERED, True, True, -14,
     "Engraved initials"),
    ("Dad", "Dad", "Whisky tasting set", "Food & Drink",
     "Not On The High Street", "https://www.notonthehighstreet.com", 55, 55.00,
     C.ST_BOUGHT, True, False, -8, ""),
    ("Grandma Rose", "Grandma", "Digital photo frame", "Electronics",
     "Amazon", "https://www.amazon.com", 90, 84.99, C.ST_ORDERED, False,
     False, -5, "Pre-load family photos"),
    ("Grandma Rose", "Grandma", "Chunky knitted blanket", "Handmade", "Etsy",
     "https://www.etsy.com", 45, 45.00, C.ST_WRAPPED, True, False, -12, ""),
    ("Grandpa Joe", "Grandpa", "Crossword book bundle", "Books",
     "Local Bookshop", "", 25, 22.00, C.ST_DELIVERED, True, True, -16, ""),
    ("Grandpa Joe", "Grandpa", "Heated slippers", "Clothing", "Amazon",
     "https://www.amazon.com", 30, 27.50, C.ST_DELIVERED, True, True, -16, ""),
    ("Sister Emily", "Sister", "Gold hoop earrings", "Jewellery", "Etsy",
     "https://www.etsy.com", 50, 48.00, C.ST_WRAPPED, True, False, -6, ""),
    ("Sister Emily", "Sister", "Bath bomb gift box", "Beauty", "Sephora",
     "https://www.sephora.com", 25, None, C.ST_NEED, False, False, -6,
     "Check the winter collection"),
    ("Brother Jack", "Brother", "Wireless earbuds", "Electronics",
     "Best Buy", "https://www.bestbuy.com", 80, 74.99, C.ST_ORDERED, False,
     False, -4, "Express delivery paid"),
    ("Brother Jack", "Brother", "Craft beer hamper", "Food & Drink", "Tesco",
     "", 35, 33.00, C.ST_BOUGHT, False, False, -9, ""),
    ("Niece Sophie", "Niece", "LEGO Friends set", "Toys", "Amazon",
     "https://www.amazon.com", 45, 39.99, C.ST_DELIVERED, True, True, -18,
     "Age 8 - checked the age guide"),
    ("Niece Sophie", "Niece", "Art supplies case", "Kids", "Etsy",
     "https://www.etsy.com", 22, 20.00, C.ST_WRAPPED, True, False, -7, ""),
    ("Nephew Leo", "Nephew", "Dinosaur museum tickets", "Experience", "Other",
     "", 40, 36.00, C.ST_BOUGHT, False, False, -3, "Print the voucher"),
    ("Nephew Leo", "Nephew", "Graphic novel bundle", "Books",
     "Local Bookshop", "", 25, None, C.ST_IDEA, False, False, -3,
     "Ask Emily what he is reading"),
    ("Alex (partner)", "Partner", "Weekend getaway", "Experience", "Other",
     "", 180, 165.00, C.ST_BOUGHT, False, False, -2, "Booked, no wrapping!"),
    ("Alex (partner)", "Partner", "Engraved watch", "Jewellery", "Etsy",
     "https://www.etsy.com", 95, 89.00, C.ST_ORDERED, False, False, -5, ""),
    ("Maya (best friend)", "Friend", "Scented candle trio", "Home",
     "Not On The High Street", "https://www.notonthehighstreet.com", 30,
     28.50, C.ST_DELIVERED, True, True, -20, ""),
    ("Maya (best friend)", "Friend", "Baking cookbook", "Books", "Amazon",
     "https://www.amazon.com", 22, None, C.ST_NEED, False, False, -6, ""),
    ("Cousin Dan", "Cousin", "Strategy board game", "Games", "Target",
     "https://www.target.com", 35, 32.00, C.ST_BOUGHT, False, False, -8, ""),
    ("Cousin Dan", "Cousin", "Coffee bean subscription", "Food & Drink",
     "Etsy", "https://www.etsy.com", 30, None, C.ST_NEED, False, False, -8,
     "3-month subscription"),
    ("Aunt Carol", "Aunt", "Silk scarf", "Clothing", "M&S",
     "https://www.marksandspencer.com", 40, 37.50, C.ST_DELIVERED, True, True,
     -21, ""),
    ("Aunt Carol", "Aunt", "Garden gloves & tool set", "Home", "Amazon",
     "https://www.amazon.com", 18, 16.00, C.ST_WRAPPED, True, False, -7, ""),
    ("Secret Santa", "Secret Santa", "Novelty reindeer mug", "Other",
     "Target", "https://www.target.com", 15, 12.99, C.ST_BOUGHT, False, False,
     -4, "Office Secret Santa - $15 limit"),
]

GIFT_KEYS = ("recipient", "relationship", "idea", "category", "store", "link",
             "budget", "cost", "status", "wrapped", "delivered", "deadline",
             "notes")

# Where the wrapped presents are hiding (used by the Wrapping & Hiding tab).
# gift index -> (hiding spot, gift tag attached?)
WRAP_DETAILS = {
    1: ("Top shelf in closet", True),
    2: ("Car boot / trunk", True),
    5: ("Suitcase in the attic", True),
    6: ("Behind the books", True),
    7: ("Under the bed", True),
    8: ("Linen closet", True),
    12: ("Garage shelf", True),
    13: ("Top shelf in closet", False),
    18: ("Under the stairs box", True),
    22: ("Shoe box in wardrobe", True),
    23: ("Back of the pantry", True),
}


def gift_rows():
    out = []
    for i, g in enumerate(GIFTS):
        row = dict(zip(GIFT_KEYS, g))
        row["deadline"] = _d(row["deadline"])
        row["wrapped"] = C.TICK if row["wrapped"] else ""
        row["delivered"] = C.TICK if row["delivered"] else ""
        spot, tag = WRAP_DETAILS.get(i, ("", False))
        row["hiding"] = spot
        row["tag"] = C.TICK if tag else ""
        out.append(row)
    return out


# ===========================================================================
# SHOPPING LIST
# ===========================================================================
# (item, category, store, qty, unit cost, bought, actual cost, notes)
SHOPPING = [
    ("Wrapping paper - 3 roll pack", "Wrapping", "Target", 3, 4.00, True,
     11.50, "Gold foil design"),
    ("Ribbon - red & gold", "Wrapping", "Amazon", 2, 3.50, True, 6.80, ""),
    ("Gift tags (pack of 50)", "Wrapping", "Etsy", 1, 6.00, True, 6.00,
     "Hand-lettered"),
    ("Sticky tape & scissors", "Wrapping", "Target", 1, 5.00, False, None, ""),
    ("Tissue paper bundle", "Wrapping", "Target", 1, 3.00, False, None, ""),
    ("Christmas cards (box of 30)", "Cards", "Amazon", 1, 14.00, True, 13.50,
     ""),
    ("Stamps - book of 30", "Postage", "Post office", 1, 20.40, True, 20.40,
     ""),
    ("Thank-you notes", "Cards", "Etsy", 1, 8.00, False, None, "For January"),
    ("Plain flour", "Baking", "Grocery store", 2, 1.80, True, 3.40, ""),
    ("Cookie cutters set", "Baking", "Amazon", 1, 8.00, True, 7.50, ""),
    ("Cake decorating sprinkles", "Baking", "Grocery store", 1, 4.50, False,
     None, ""),
    ("Chocolate for stockings", "Stockings", "Grocery store", 4, 3.20, True,
     12.00, ""),
    ("Candy canes", "Stockings", "Grocery store", 2, 2.00, True, 3.80, ""),
    ("Christmas crackers", "Party Supplies", "Target", 2, 5.50, False, None,
     ""),
    ("Napkins & party plates", "Party Supplies", "Target", 1, 7.00, False,
     None, ""),
    ("Tree baubles - gold", "Decorations", "IKEA", 2, 9.00, True, 16.00, ""),
    ("Fairy lights (warm white)", "Decorations", "Amazon", 1, 15.00, True,
     14.99, ""),
    ("Wreath for the front door", "Decorations", "Local market", 1, 22.00,
     False, None, ""),
    ("Turkey & trimmings", "Food", "Grocery store", 1, 65.00, False, None,
     "Order by 18 Dec"),
    ("Sparkling cider", "Food", "Grocery store", 2, 6.50, False, None, ""),
    ("Chocolate selection boxes", "Food", "Grocery store", 3, 8.00, True,
     22.50, "For neighbours & teachers"),
    ("Petrol / parking for the trip", "Travel", "Shell", 1, 38.40, False,
     None, ""),
    ("Food bank donation", "Charity", "Local charity", 1, 25.00, True, 25.00,
     ""),
    ("Gift bags (spares)", "Other", "Target", 1, 4.00, False, None, ""),
]

SHOP_KEYS = ("item", "category", "store", "qty", "unit", "bought", "cost",
             "notes")


def shop_rows():
    out = []
    for s in SHOPPING:
        row = dict(zip(SHOP_KEYS, s))
        row["bought"] = C.TICK if row["bought"] else ""
        out.append(row)
    return out


def shop_presets():
    """Starter rows shipped with the blank workbook."""
    out = []
    for item, cat, store, qty, unit in C.SHOP_PRESETS:
        out.append({"item": item, "category": cat, "store": store, "qty": qty,
                    "unit": unit, "bought": "", "cost": None, "notes": ""})
    return out


# ===========================================================================
# ORDER TRACKER
# ===========================================================================
# (recipient, item, store, order no, order date, expected, actual, link,
#  status, cost, return deadline, notes)
ORDERS = [
    ("Grandma Rose", "Digital photo frame", "Amazon", "112-4471902-5563810",
     _d(-20), _d(-3), None, "https://www.amazon.com/gp/your-account/order-details?order=112-4471902",
     C.OS_SHIPPED, 84.99, _d(25), "Tracking updated twice a day"),
    ("Brother Jack", "Wireless earbuds", "Best Buy", "BB-9938-2211", _d(-18),
     _d(-4), None, "https://www.bestbuy.com/orders", C.OS_OUT, 74.99, _d(24),
     "Signature required"),
    ("Alex (partner)", "Engraved watch", "Etsy", "ETSY-778201", _d(-25),
     _d(-6), None, "https://www.etsy.com/your/orders", C.OS_SHIPPED, 89.00,
     _d(22), "Engraving takes 5 days"),
    ("Dad", "Leather wallet", "Amazon", "112-8830042-1120394", _d(-32),
     _d(-14), _d(-15), "https://www.amazon.com/gp/your-account/order-details?order=112-8830042",
     C.OS_DELIVERED, 38.50, _d(16), "Left with neighbour"),
    ("Niece Sophie", "LEGO Friends set", "Amazon", "112-2291047-9930112",
     _d(-40), _d(-18), _d(-18), "https://www.amazon.com/gp/your-account/order-details?order=112-2291047",
     C.OS_DELIVERED, 39.99, _d(12), ""),
    ("Maya (best friend)", "Scented candle trio", "Not On The High Street",
     "NOTHS-55231", _d(-45), _d(-20), _d(-19),
     "https://www.notonthehighstreet.com/my-account", C.OS_DELIVERED, 28.50,
     _d(10), ""),
    ("Aunt Carol", "Silk scarf", "M&S", "MS-4419287", _d(-50), _d(-21),
     _d(-21), "https://www.marksandspencer.com/my-account", C.OS_DELIVERED,
     37.50, _d(9), ""),
    ("Sister Emily", "Bath bomb gift box", "Sephora", "SEPH-88213", _d(-6),
     _d(-1), None, "https://www.sephora.com/account/orders", C.OS_ORDERED,
     24.00, _d(29), "Waiting for dispatch"),
]

ORDER_KEYS = ("recipient", "item", "store", "order_no", "order_date",
              "expected", "actual", "link", "status", "cost", "return_by",
              "notes")


def order_rows():
    out = []
    for o in ORDERS:
        row = dict(zip(ORDER_KEYS, o))
        row["returned"] = ""
        out.append(row)
    return out


# ===========================================================================
# CARD TRACKER
# ===========================================================================
CARDS = [
    ("Grandma Rose", "Grandma", "14 Rosewood Lane, Harrogate HG1 2AB, UK",
     True, True, True, _d(-12), True, 0.68, "Big handwriting card"),
    ("Grandpa Joe", "Grandpa", "14 Rosewood Lane, Harrogate HG1 2AB, UK",
     True, True, True, _d(-12), True, 0.68, "Same envelope as Grandma"),
    ("Aunt Carol", "Aunt", "88 Maple Drive, Leeds LS6 4QT, UK", True, True,
     True, _d(-10), False, 0.68, ""),
    ("Uncle Bill", "Uncle", "88 Maple Drive, Leeds LS6 4QT, UK", True, True,
     True, _d(-10), False, 0.68, ""),
    ("Cousin Dan", "Cousin", "3 Ash Court, Manchester M1 5AN, UK", True, True,
     True, _d(-9), False, 0.68, ""),
    ("Cousin Priya", "Cousin", "3 Ash Court, Manchester M1 5AN, UK", True,
     True, False, None, False, 0.00, "Card written, needs posting"),
    ("Maya (best friend)", "Friend", "27b Kingsland Road, London E2 8AA, UK",
     True, True, True, _d(-8), True, 0.68, "Hand delivered a gift too"),
    ("Tom & Jess", "Friend", "5 Cedar Walk, Bristol BS1 4TR, UK", True, True,
     False, None, False, 0.00, ""),
    ("Mrs Higgins (neighbour)", "Neighbour", "9 Birch Hill, York YO1 7HD, UK",
     True, False, False, None, False, 0.00, "Write after the 15th"),
    ("Ms Patel (teacher)", "Teacher", "St Anne's Primary, School Office", True,
     False, False, None, False, 0.00, "From Sophie"),
    ("Office team", "Colleague", "Hand delivered", True, True, True, _d(-5),
     False, 0.00, "Left on the team table"),
    ("Nana Flo", "Grandma", "2 Willow Cottages, Derby DE1 3RT, UK", False,
     False, False, None, False, 0.00, "Buy a photo card"),
    ("The Robinsons", "Neighbour", "11 Oakfield Road, Sheffield S10 2QN, UK",
     False, False, False, None, False, 0.00, ""),
    ("Cousin Sam", "Cousin", "44 Station Road, Newcastle NE1 5BR, UK", False,
     False, False, None, False, 0.00, ""),
]

CARD_KEYS = ("name", "relationship", "address", "bought", "written", "sent",
             "date_sent", "received", "postage", "notes")


def card_rows():
    out = []
    for c in CARDS:
        row = dict(zip(CARD_KEYS, c))
        for k in ("bought", "written", "sent", "received"):
            row[k] = C.TICK if row[k] else ""
        out.append(row)
    return out


# ===========================================================================
# STOCKINGS
# ===========================================================================
STOCKINGS = [
    ("Emma", "Lip balm trio", "Beauty", 8, 7.50, True, True,
     "Top shelf in closet", "Peppermint - her favourite"),
    ("Emma", "Hair clips set", "Hair clips", 6, 5.00, True, False,
     "Top shelf in closet", ""),
    ("Emma", "Chocolate coins", "Chocolate", 5, 4.20, True, True,
     "Under the bed", ""),
    ("Emma", "Mini diary & pen", "Stationery", 9, 8.00, False, False, "", ""),
    ("Emma", "Fuzzy socks", "Socks", 7, 6.50, True, False, "Linen closet", ""),
    ("Oliver", "Dinosaur figures", "Small toy", 12, 11.00, True, True,
     "Garage shelf", ""),
    ("Oliver", "Candy cane pack", "Candy", 4, 3.80, True, True,
     "Back of the pantry", ""),
    ("Oliver", "Football stickers", "Novelty", 6, 5.50, True, False,
     "Shoe box in wardrobe", ""),
    ("Oliver", "Comic book", "Stationery", 7, None, False, False, "",
     "Ask what he is reading"),
    ("Oliver", "Bath bubble bombs", "Beauty", 8, 7.00, True, False,
     "Linen closet", ""),
    ("Mum", "Silk eye mask", "Beauty", 15, 14.00, True, True,
     "Suitcase in the attic", ""),
    ("Mum", "Hand cream & nails set", "Beauty", 12, 11.50, True, False,
     "Under the stairs box", ""),
    ("Mum", "Favourite tea blend", "Snacks", 9, 8.50, True, True,
     "Back of the pantry", ""),
    ("Dad", "Leather keyring", "Novelty", 14, 13.00, True, False,
     "Car boot / trunk", "Initials J.M."),
    ("Dad", "Golf balls (3 pack)", "Other", 12, 11.00, True, True,
     "Garage shelf", ""),
    ("Dad", "Hot sauce bundle", "Snacks", 10, 9.50, False, False, "",
     "Check the heat levels!"),
]

STOCK_KEYS = ("owner", "item", "category", "budget", "cost", "bought",
              "wrapped", "hiding", "notes")


def stock_rows():
    out = []
    for s in STOCKINGS:
        row = dict(zip(STOCK_KEYS, s))
        row["bought"] = C.TICK if row["bought"] else ""
        row["wrapped"] = C.TICK if row["wrapped"] else ""
        out.append(row)
    return out


# ===========================================================================
# WISH LIST
# ===========================================================================
WISHLIST = [
    ("Alex (partner)", "Engraved watch", "Jewellery",
     "https://www.etsy.com/listing/watch", 95.00, C.PR_MUST,
     "Mentioned it in October"),
    ("Alex (partner)", "Cast iron skillet", "Home",
     "https://www.amazon.com", 45.00, C.PR_MAYBE, "For the new kitchen"),
    ("Mum", "Cashmere scarf", "Clothing", "https://www.johnlewis.com", 60.00,
     C.PR_MUST, "Burgundy or cream"),
    ("Mum", "Gardening book", "Books", "", 18.00, C.PR_LOW, ""),
    ("Sister Emily", "Bath bomb gift box", "Beauty",
     "https://www.sephora.com", 25.00, C.PR_MUST, "On the wish list she sent"),
    ("Sister Emily", "Silk pillowcase", "Home", "https://www.amazon.com",
     32.00, C.PR_MAYBE, ""),
    ("Nephew Leo", "Graphic novel bundle", "Books", "", 25.00, C.PR_MAYBE,
     "Ages 10-12"),
    ("Niece Sophie", "Watercolour set", "Kids", "https://www.etsy.com", 20.00,
     C.PR_LOW, ""),
    ("Grandma Rose", "Digital photo frame", "Electronics",
     "https://www.amazon.com", 90.00, C.PR_MUST, "Big buttons, simple menu"),
    ("Brother Jack", "Wireless earbuds", "Electronics",
     "https://www.bestbuy.com", 80.00, C.PR_MUST, ""),
    ("Maya (best friend)", "Pottery class for two", "Experience", "", 70.00,
     C.PR_MAYBE, "Birthday idea for March"),
    ("Cousin Dan", "Coffee bean subscription", "Food & Drink",
     "https://www.etsy.com", 30.00, C.PR_LOW, ""),
]

WISH_KEYS = ("person", "idea", "category", "link", "price", "priority",
             "notes")


def wish_rows():
    return [dict(zip(WISH_KEYS, w)) for w in WISHLIST]


# ===========================================================================
# BUDGET (planned amounts) + manual actuals
# ===========================================================================
BUDGET_PLANNED = {
    "gifts": 1050, "stockings": 120, "wrapping": 50, "cards": 35,
    "food": 130, "baking": 25, "decor": 40, "party": 25, "travel": 0,
    "other": 25,
}
BUDGET_MANUAL = {"travel": 38.40}


# ===========================================================================
# TO-DO LIST (presets, with which ones are already ticked in the demo)
# ===========================================================================
TODO_DONE = {
    "Write the gift list & set the budget",
    "Order Christmas cards",
    "Buy wrapping paper, ribbon & tags",
    "Order gifts that need delivery time",
    "Buy the main gifts",
    "Buy the decorations & set up the tree",
    "Mail any packages",
}


def todo_rows(mode):
    """To-do presets.  ``offset`` = days BEFORE the event date."""
    out = []
    for task, cat, offset, _done in C.TODO_PRESETS:
        done = (mode == "demo" and task in TODO_DONE)
        out.append({"done": C.TICK if done else "", "task": task,
                    "category": cat, "offset": offset,
                    "deadline": EVENT_DATE + timedelta(days=-offset),
                    "notes": ""})
    return out


# ===========================================================================
# SETTINGS
# ===========================================================================
SETTINGS = {
    "event_name": C.DEFAULT_EVENT_NAME,
    "currency": C.DEFAULT_CURRENCY,
    "budget": C.DEFAULT_BUDGET,
    "alert": C.DEFAULT_ALERT,
    "duesoon": C.DEFAULT_DUESOON,
    "secret": "No",
    "count_ordered": "No",
    "occasion": "Christmas",
}


# ===========================================================================
# THE CALCULATOR
# ===========================================================================
class Model(object):
    """Everything the workbook would calculate if Excel did it for us."""

    def __init__(self, mode="blank", edition="premium"):
        self.mode = mode
        self.edition = edition
        self.demo = (mode == "demo")
        self.settings = dict(SETTINGS) if self.demo else {
            "event_name": C.DEFAULT_EVENT_NAME,
            "currency": C.DEFAULT_CURRENCY, "budget": 0,
            "alert": C.DEFAULT_ALERT, "duesoon": C.DEFAULT_DUESOON,
            "secret": "No", "count_ordered": "No", "occasion": "Christmas"}
        self.event_date = EVENT_DATE
        self.recipients = (GIFT_RECIPIENTS if self.demo
                           else list(C.BLANK_RECIPIENTS))
        self.owners = (STOCK_OWNERS if self.demo else list(C.BLANK_OWNERS))
        self.categories = list(C.GIFT_CATEGORIES)

        self.gifts = gift_rows() if self.demo else []
        self.shopping = shop_rows() if self.demo else shop_presets()
        self.orders = order_rows() if (self.demo and edition == "premium") else []
        self.cards = card_rows() if (self.demo and edition == "premium") else []
        self.stockings = stock_rows() if (self.demo and edition == "premium") else []
        self.wishlist = wish_rows() if (self.demo and edition == "premium") else []
        self.todos = todo_rows(mode)
        self.budget_planned = dict(BUDGET_PLANNED) if self.demo else {}
        self.budget_manual = dict(BUDGET_MANUAL) if self.demo else {}
        self.agg = {}
        self._compute()

    # ------------------------------------------------------------------
    def _compute(self):
        a = self.agg
        g = self.gifts

        # --- gifts -----------------------------------------------------
        a["gifts_planned"] = len([x for x in g if x["idea"]])
        bought_states = (C.ST_BOUGHT, C.ST_WRAPPED, C.ST_DELIVERED)
        a["gifts_purchased"] = len([x for x in g if x["status"] in bought_states])
        if self.settings["count_ordered"] == "Yes":
            a["gifts_purchased"] += len([x for x in g
                                         if x["status"] == C.ST_ORDERED])
        a["gifts_wrapped"] = len([
            x for x in g
            if x["wrapped"] == C.TICK
            or (x["wrapped"] != C.TICK
                and x["status"] in (C.ST_WRAPPED, C.ST_DELIVERED))])
        a["gifts_delivered"] = len([
            x for x in g
            if x["delivered"] == C.TICK
            or (x["delivered"] != C.TICK and x["status"] == C.ST_DELIVERED)])
        a["gifts_to_buy"] = len([x for x in g
                                 if x["status"] in (C.ST_IDEA, C.ST_NEED)])
        a["gifts_ordered"] = len([x for x in g if x["status"] == C.ST_ORDERED])
        a["wrap_to_do"] = max(0, a["gifts_purchased"] - a["gifts_wrapped"])
        a["deliver_to_do"] = max(0, a["gifts_wrapped"] - a["gifts_delivered"])
        a["gift_completion"] = (a["gifts_purchased"] / float(a["gifts_planned"])
                                if a["gifts_planned"] else 0)
        a["gift_budget_planned"] = sum(x["budget"] or 0 for x in g)
        a["gift_actual_spent"] = sum(x["cost"] or 0 for x in g)

        # --- recipients ------------------------------------------------
        rec = []
        for i in range(C.RECIPIENT_SLOTS):
            name = self.recipients[i] if i < len(self.recipients) else ""
            rows = [x for x in g if x["recipient"] == name] if name else []
            gifts_n = len(rows)
            bought_n = len([x for x in rows if x["status"] in bought_states])
            wrapped_n = len([x for x in rows
                             if x["wrapped"] == C.TICK
                             or x["status"] in (C.ST_WRAPPED, C.ST_DELIVERED)])
            delivered_n = len([x for x in rows
                               if x["delivered"] == C.TICK
                               or x["status"] == C.ST_DELIVERED])
            rec.append({
                "name": name,
                "planned": sum(x["budget"] or 0 for x in rows),
                "spent": sum(x["cost"] or 0 for x in rows),
                "gifts": gifts_n, "bought": bought_n, "wrapped": wrapped_n,
                "delivered": delivered_n,
                "to_buy": max(0, gifts_n - bought_n),
                "pct": (bought_n / float(gifts_n)) if gifts_n else "",
            })
        a["recipients"] = rec
        a["recipients_gifted"] = len([x for x in rec if x["gifts"] > 0])
        a["avg_per_recipient"] = (a["gift_actual_spent"] /
                                  float(a["recipients_gifted"])
                                  if a["recipients_gifted"] else 0)

        # --- categories ------------------------------------------------
        cats = []
        for i in range(C.CATEGORY_SLOTS):
            name = self.categories[i] if i < len(self.categories) else ""
            cats.append({
                "name": name,
                "spent": sum(x["cost"] or 0 for x in g
                             if name and x["category"] == name)})
        a["categories"] = cats

        # --- status breakdown ------------------------------------------
        a["status_counts"] = [{"name": s,
                               "count": len([x for x in g if x["status"] == s])}
                              for s in C.STATUSES]

        # --- shopping --------------------------------------------------
        sh = self.shopping
        a["shop_total"] = len([x for x in sh if x["item"]])
        a["shop_bought"] = len([x for x in sh if x["bought"] == C.TICK])
        a["shop_spent"] = sum(self._shop_spent(x) for x in sh)

        # --- budget ----------------------------------------------------
        rows = []
        for label, key, recipe, demo_planned in C.BUDGET_CATEGORIES:
            planned = self.budget_planned.get(key, demo_planned if self.demo else 0)
            manual = self.budget_manual.get(key, 0)
            auto = self._budget_auto(recipe)
            actual = manual + auto
            rows.append({"label": label, "key": key, "planned": planned,
                         "manual": manual, "auto": auto, "actual": actual,
                         "remaining": planned - actual,
                         "pct": (actual / float(planned)) if planned else ""})
        a["budget_rows"] = rows
        a["budget_planned"] = sum(x["planned"] for x in rows)
        a["budget_actual"] = sum(x["actual"] for x in rows)
        a["budget_remaining"] = a["budget_planned"] - a["budget_actual"]
        a["budget_pct"] = (a["budget_actual"] / float(a["budget_planned"])
                           if a["budget_planned"] else 0)

        # --- cards -----------------------------------------------------
        a["cards_total"] = len([x for x in self.cards if x["name"]])
        a["cards_written"] = len([x for x in self.cards
                                  if x["written"] == C.TICK])
        a["cards_sent"] = len([x for x in self.cards if x["sent"] == C.TICK])
        a["cards_received"] = len([x for x in self.cards
                                   if x["received"] == C.TICK])
        a["cards_postage"] = sum(x["postage"] or 0 for x in self.cards)

        # --- stockings -------------------------------------------------
        st = self.stockings
        a["stock_items"] = len([x for x in st if x["item"]])
        a["stock_bought"] = len([x for x in st if x["bought"] == C.TICK])
        a["stock_budget"] = sum(x["budget"] or 0 for x in st)
        a["stock_spent"] = sum(self._stock_spent(x) for x in st)
        a["stock_by_owner"] = self._stock_by_owner()

        # --- orders ----------------------------------------------------
        od = self.orders
        a["orders_total"] = len([x for x in od if x["item"]])
        a["orders_outstanding"] = len([
            x for x in od
            if x["status"] not in (C.OS_DELIVERED, C.OS_CANCEL, C.OS_RETURN)])
        a["orders_late"] = len([
            x for x in od
            if x["expected"] and x["expected"] < TODAY
            and x["status"] not in (C.OS_DELIVERED, C.OS_CANCEL)])
        a["orders_value"] = sum(x["cost"] or 0 for x in od)

        # --- to-do -----------------------------------------------------
        td = self.todos
        a["todo_total"] = len([x for x in td if x["task"]])
        a["todo_done"] = len([x for x in td if x["done"] == C.TICK])
        a["todo_overdue"] = len([x for x in td
                                 if x["done"] != C.TICK and x["deadline"]
                                 and x["deadline"] < TODAY])
        a["todo_soon"] = len([x for x in td
                              if x["done"] != C.TICK and x["deadline"]
                              and TODAY <= x["deadline"]
                              <= TODAY + timedelta(days=self.settings["duesoon"])])

        # --- wish list -------------------------------------------------
        wl = self.wishlist
        a["wish_total"] = len([x for x in wl if x["idea"]])
        a["wish_must"] = len([x for x in wl if x["priority"] == C.PR_MUST])
        a["wish_value"] = sum(x["price"] or 0 for x in wl)

        # --- countdown -------------------------------------------------
        a["days_to_event"] = (self.event_date - TODAY).days
        a["event_year"] = self.event_date.year
        a["weeks_to_event"] = max(0, -(-(self.event_date - TODAY).days // 7))

        # --- deadline pool ---------------------------------------------
        a["pool"] = self._deadline_pool()

        # --- text ------------------------------------------------------
        a.update(self._text())

    # ------------------------------------------------------------------
    def _shop_spent(self, row):
        if row["bought"] != C.TICK:
            return 0
        if row.get("cost"):
            return row["cost"]
        return (row.get("qty") or 0) * (row.get("unit") or 0)

    def _stock_spent(self, row):
        if row["bought"] != C.TICK:
            return 0
        if row.get("cost") is not None:
            return row["cost"]
        return row.get("budget") or 0

    def _budget_auto(self, recipe):
        total = 0.0
        for term in recipe:
            if term == "gifts":
                total += sum(x["cost"] or 0 for x in self.gifts)
            elif term == "stock":
                total += sum(self._stock_spent(x) for x in self.stockings)
            elif term == "cards":
                total += sum(x["postage"] or 0 for x in self.cards)
            elif term.startswith("shop:"):
                cat = term.split(":", 1)[1]
                total += sum(self._shop_spent(x) for x in self.shopping
                             if x["category"] == cat)
        return round(total, 2)

    def _stock_by_owner(self):
        out = []
        for i in range(C.RECIPIENT_SLOTS):
            name = self.owners[i] if i < len(self.owners) else ""
            rows = [x for x in self.stockings if x["owner"] == name] if name else []
            budget = sum(x["budget"] or 0 for x in rows)
            spent = sum(self._stock_spent(x) for x in rows)
            out.append({"name": name, "items": len(rows), "budget": budget,
                        "spent": spent, "remaining": budget - spent,
                        "bought": len([x for x in rows
                                       if x["bought"] == C.TICK])})
        return out

    def _deadline_pool(self):
        pool = []
        for x in self.gifts:
            if x["deadline"] and x["deadline"] >= TODAY and \
                    x["status"] != C.ST_DELIVERED:
                pool.append((x["deadline"],
                             "\U0001F381 %s \u2014 %s" % (x["idea"],
                                                         x["recipient"])))
        for x in self.todos:
            if x["done"] != C.TICK and x["deadline"] and x["deadline"] >= TODAY:
                pool.append((x["deadline"], "\u2705 %s" % x["task"]))
        for x in self.orders:
            if x["expected"] and x["expected"] >= TODAY and x["status"] not in (
                    C.OS_DELIVERED, C.OS_CANCEL):
                pool.append((x["expected"],
                             "\U0001F4E6 %s \u2014 %s" % (x["item"],
                                                          x["store"])))
        pool.sort(key=lambda t: t[0])
        return pool

    def _text(self):
        a = self.agg
        cur = self.settings["currency"]
        name = self.settings["event_name"]
        days = a["days_to_event"]
        t = {}
        if days > 1:
            t["countdown"] = "\u23F3  %d Days Until %s  \U0001F381" % (days, name)
        elif days == 1:
            t["countdown"] = "\u23F3  Tomorrow is %s!  \U0001F381" % name
        elif days == 0:
            t["countdown"] = "\U0001F389  It's %s today!  \U0001F384" % name
        else:
            t["countdown"] = ("\U0001F384  %s %d has been and gone \u2014 "
                              "update the date in \u2699\uFE0F Setup to plan "
                              "next year" % (name, self.event_date.year))

        pct = a["budget_pct"]
        if a["budget_planned"] <= 0:
            t["budget_alert"] = ("\U0001F4DD  Set your planned budgets on the "
                                 "\U0001F4B0 Budget tab to turn on the alerts.")
        elif a["budget_actual"] > a["budget_planned"]:
            over = a["budget_actual"] - a["budget_planned"]
            t["budget_alert"] = ("\U0001F534  Over budget by %s%s \u2014 pause "
                                 "the non-essentials."
                                 % (cur, format(over, ",.2f")))
        elif pct >= self.settings["alert"]:
            t["budget_alert"] = ("\u26A0\uFE0F  You've spent %.0f%% of your "
                                 "%s budget \u2014 %s%s left."
                                 % (pct * 100, name, cur,
                                    format(a["budget_remaining"], ",.2f")))
        else:
            t["budget_alert"] = ("\U0001F7E2  On track \u2014 %.0f%% of the "
                                 "budget used, %s%s still to spend."
                                 % (pct * 100, cur,
                                    format(a["budget_remaining"], ",.2f")))

        t["bar_budget"] = _bar(a["budget_pct"])
        t["bar_gifts"] = _bar(a["gift_completion"])
        t["bar_cards"] = _bar(a["cards_sent"] / float(a["cards_total"])
                              if a["cards_total"] else 0)
        t["bar_stock"] = _bar(a["stock_bought"] / float(a["stock_items"])
                              if a["stock_items"] else 0)
        t["bar_shop"] = _bar(a["shop_bought"] / float(a["shop_total"])
                             if a["shop_total"] else 0)
        t["bar_todo"] = _bar(a["todo_done"] / float(a["todo_total"])
                             if a["todo_total"] else 0)
        return t

    # ------------------------------------------------------------------
    def money(self, value, decimals=0):
        fmt = ",.%df" % decimals
        return self.settings["currency"] + format(value or 0, fmt)


GIFT_RECIPIENTS = [
    "Mum", "Dad", "Grandma Rose", "Grandpa Joe", "Sister Emily",
    "Brother Jack", "Niece Sophie", "Nephew Leo", "Alex (partner)",
    "Maya (best friend)", "Cousin Dan", "Aunt Carol", "Uncle Bill",
    "Secret Santa",
]
STOCK_OWNERS = ["Emma", "Oliver", "Mum", "Dad"]


def _bar(pct, blocks=18):
    try:
        pct = min(1.0, max(0.0, float(pct)))
    except (TypeError, ValueError):
        pct = 0.0
    filled = int(round(pct * blocks))
    return "\u2588" * filled + "\u2591" * (blocks - filled)
