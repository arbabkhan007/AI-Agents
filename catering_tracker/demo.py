"""
Sample data for EXAMPLE builds.

``Model`` mirrors what a real user would type into the workbook for a busy
catering company (Saffron & Sage Catering Co.) in September-December 2026.
Every derived figure (profit, margin, stock value, KPI totals, the monthly
report pools...) is computed here in Python so the EXAMPLE workbooks ship
with correct *cached* values: they look right the instant they are opened,
before Excel recalculates anything.
"""

from datetime import date

from . import config as C

SETTINGS = {
    "business": "Saffron & Sage Catering Co.",
    "currency": "$",
    "tax": 0.05,
    "margin": 0.35,
    "deposit": 0.40,
    "duesoon": 7,
    "year": 2026,
    "cal_month": 9,
    "cal_year": 2026,
    "message": "Confirm October crews early!",
}

TODAY = date(2026, 9, 12)          # "as if opened on" date for the sample

MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _d(m, day):
    return date(2026, m, day)


# ---------------------------------------------------------------------------
# events  (id, client, date, type, guests, menu, staff_req, equipment_req,
#          cost, price, deposit, status, notes)
# ---------------------------------------------------------------------------
EVENTS = [
    dict(id="EV-2026-001", client="Aisha Malik", date=_d(9, 5),
         type="Wedding", guests=180,
         menu="Herb Roast Chicken Platter, Chocolate Fondant",
         staff_req=12, equipment_req="Chafers x8, Tables x20, Linen x20",
         cost=4920, price=7600, deposit=3040, status=C.ES_DONE,
         notes="Nikkah + reception, two seatings"),
    dict(id="EV-2026-002", client="TechNova Pvt Ltd", date=_d(9, 10),
         type="Corporate", guests=60,
         menu="Chicken Tikka Platter, Lemon Tart",
         staff_req=5, equipment_req="Chafers x4, Coffee urns x2",
         cost=1180, price=1850, deposit=740, status=C.ES_DONE,
         notes="Quarterly all-hands lunch"),
    dict(id="EV-2026-003", client="Daniel Fernandes", date=_d(9, 19),
         type="Birthday", guests=45,
         menu="Beef Biryani Feast, Chocolate Fondant",
         staff_req=4, equipment_req="Chafers x3, Beverage dispenser x1",
         cost=890, price=1400, deposit=560, status=C.ES_CONFIRMED,
         notes="40th birthday, garden venue"),
    dict(id="EV-2026-004", client="Meera Khan", date=_d(9, 26),
         type="Private Party", guests=80,
         menu="Lamb Kofta Curry, Seasonal Fruit Display",
         staff_req=6, equipment_req="Chafers x5, Tables x10",
         cost=1620, price=2500, deposit=1000, status=C.ES_CONFIRMED,
         notes="Engagement party - deposit chasing final payment"),
    dict(id="EV-2026-005", client="Zenith Bank", date=_d(10, 3),
         type="Conference", guests=120,
         menu="Grilled Salmon Plate, Lemon Tart",
         staff_req=9, equipment_req="Chafers x6, Coffee urns x3, Glassware x120",
         cost=2450, price=3900, deposit=1560, status=C.ES_DEPOSIT,
         notes="Annual leadership summit, breakfast + lunch"),
    dict(id="EV-2026-006", client="Aisha Malik", date=_d(10, 10),
         type="Cocktail", guests=90,
         menu="Chicken Canapes (4 pc), Grilled Salmon Plate",
         staff_req=7, equipment_req="Glassware x90, Dispensers x2",
         cost=1980, price=3100, deposit=1240, status=C.ES_CONFIRMED,
         notes="Repeat client - mehndi cocktail hour"),
    dict(id="EV-2026-007", client="Omar Sheikh", date=_d(10, 17),
         type="Wedding", guests=220,
         menu="Beef Biryani Feast, Herb Roast Chicken Platter",
         staff_req=14, equipment_req="Chafers x10, Tables x25, Chairs x220",
         cost=6100, price=9800, deposit=3920, status=C.ES_DEPOSIT,
         notes="Biggest booking of the season"),
    dict(id="EV-2026-008", client="Bright Futures School", date=_d(10, 24),
         type="Festival", guests=300,
         menu="Chicken Tikka Platter, Seasonal Fruit Display",
         staff_req=12, equipment_req="Chafers x8, Beverage dispensers x4",
         cost=3400, price=5200, deposit=0, status=C.ES_QUOTED,
         notes="Autumn fair - quote sent, awaiting board approval"),
    dict(id="EV-2026-009", client="Hina Raza", date=_d(11, 7),
         type="Birthday", guests=35,
         menu="Creamy Pasta Alfredo, Chocolate Fondant",
         staff_req=3, equipment_req="Chafers x2",
         cost=640, price=1050, deposit=0, status=C.ES_QUOTED,
         notes="Quote sent Sep 9 - follow up next week"),
    dict(id="EV-2026-010", client="TechNova Pvt Ltd", date=_d(11, 14),
         type="Corporate", guests=75,
         menu="Grilled Salmon Plate, Lemon Tart",
         staff_req=6, equipment_req="Chafers x4, Coffee urns x2",
         cost=1520, price=2400, deposit=960, status=C.ES_CONFIRMED,
         notes="Annual client appreciation dinner"),
    dict(id="EV-2026-011", client="Gulberg Sports Club", date=_d(11, 21),
         type="Buffet", guests=150,
         menu="Beef Biryani Feast, Lamb Kofta Curry",
         staff_req=10, equipment_req="Chafers x8, Tables x15",
         cost=3050, price=4700, deposit=1880, status=C.ES_DEPOSIT,
         notes="Awards night buffet"),
    dict(id="EV-2026-012", client="Zara Ahmed", date=_d(12, 5),
         type="Wedding", guests=200,
         menu="Herb Roast Chicken Platter, Grilled Salmon Plate",
         staff_req=13, equipment_req="Chafers x10, Tables x22, Linen x22",
         cost=5600, price=8900, deposit=3560, status=C.ES_CONFIRMED,
         notes="Winter wedding - confirm salmon supplier early"),
    dict(id="EV-2026-013", client="Liberty Mall Expo", date=_d(12, 19),
         type="Festival", guests=400,
         menu="Chicken Tikka Platter, Beef Biryani Feast",
         staff_req=16, equipment_req="Chafers x12, Stall setup x3",
         cost=4800, price=7200, deposit=0, status=C.ES_INQUIRY,
         notes="Food expo stall - first contact by phone"),
    dict(id="EV-2026-014", client="Bilal Traders", date=_d(12, 28),
         type="Corporate", guests=50,
         menu="Creamy Pasta Alfredo, Lemon Tart",
         staff_req=4, equipment_req="Chafers x3",
         cost=980, price=1500, deposit=300, status=C.ES_CANCEL,
         notes="Client postponed to next year - deposit refunded"),
]

ACTIVE = (C.ES_DEPOSIT, C.ES_CONFIRMED, C.ES_DONE)
BOOKED = (C.ES_QUOTED, C.ES_DEPOSIT, C.ES_CONFIRMED, C.ES_DONE)


# ---------------------------------------------------------------------------
# clients (12 - mirror of their next / most relevant event)
# ---------------------------------------------------------------------------
def client_rows():
    """Derive the client tracker from the event book (repeat clients show
    their *next* event)."""
    by_name = {}
    for ev in EVENTS:
        prev = by_name.get(ev["client"])
        if prev is None:
            by_name[ev["client"]] = ev
        else:
            # keep the most recent *upcoming* booking for repeat clients
            if ev["date"] >= TODAY and ev["status"] != C.ES_CANCEL:
                by_name[ev["client"]] = ev
    phones = {
        "Aisha Malik": "0300-8899112", "TechNova Pvt Ltd": "0311-5544332",
        "Daniel Fernandes": "0345-2233445", "Meera Khan": "0301-7788990",
        "Zenith Bank": "0321-9090808", "Omar Sheikh": "0308-4455667",
        "Bright Futures School": "0302-3344556", "Hina Raza": "0333-1122334",
        "Gulberg Sports Club": "0344-6677889", "Zara Ahmed": "0306-9988776",
        "Liberty Mall Expo": "0303-1212334", "Bilal Traders": "0315-5566778",
    }
    emails = {
        "Aisha Malik": "aisha.malik@mail.example",
        "TechNova Pvt Ltd": "events@technova.example",
        "Daniel Fernandes": "dan.fernandes@mail.example",
        "Meera Khan": "meera.khan@mail.example",
        "Zenith Bank": "hr.summits@zenithbank.example",
        "Omar Sheikh": "omar.sheikh@mail.example",
        "Bright Futures School": "admin@brightfutures.example",
        "Hina Raza": "hina.raza@mail.example",
        "Gulberg Sports Club": "clubhouse@gulbergtown.example",
        "Zara Ahmed": "zara.ahmed@mail.example",
        "Liberty Mall Expo": "expo@libertymall.example",
        "Bilal Traders": "bilal.traders@mail.example",
    }
    packages = {
        "Aisha Malik": "Gold", "TechNova Pvt Ltd": "Silver",
        "Daniel Fernandes": "Custom", "Meera Khan": "Silver",
        "Zenith Bank": "Gold", "Omar Sheikh": "Gold",
        "Bright Futures School": "Bronze", "Hina Raza": "Custom",
        "Gulberg Sports Club": "Silver", "Zara Ahmed": "Gold",
        "Liberty Mall Expo": "Custom", "Bilal Traders": "Bronze",
    }
    venues = {
        "EV-2026-001": "Royal Marquee, Model Town",
        "EV-2026-002": "TechNova HQ, Arfa Tower",
        "EV-2026-003": "Private home, Gulberg III",
        "EV-2026-004": "Lawn venue, DHA Phase 5",
        "EV-2026-005": "Conference centre, Gulberg",
        "EV-2026-006": "Marquee, Ferozepur Road",
        "EV-2026-007": "Grand Marquee, Raiwind Road",
        "EV-2026-008": "School ground, Johar Town",
        "EV-2026-009": "Private home, Cantonment",
        "EV-2026-010": "TechNova HQ, Arfa Tower",
        "EV-2026-011": "Clubhouse, Gulberg",
        "EV-2026-012": "Winter Marquee, Bedian Road",
        "EV-2026-013": "Liberty Market expo hall",
        "EV-2026-014": "Bilal Traders office",
    }
    notes = {
        "Aisha Malik": "VIP - 2nd booking this season, loves the chicken platter",
        "TechNova Pvt Ltd": "Invoice to accounts@technova.example",
        "Omar Sheikh": "Referred by Aisha Malik",
        "Zenith Bank": "Needs halal certification letter",
        "Bright Futures School": "School board must approve quote",
        "Liberty Mall Expo": "Big volume, thin margin - negotiate staffing",
    }
    rows = []
    for ev in EVENTS:                      # first-seen order == event order
        name = ev["client"]
        if any(r["name"] == name for r in rows):
            continue
        latest = by_name[name]
        paid = (latest["deposit"] if latest["status"] in
                (C.ES_DEPOSIT, C.ES_CONFIRMED, C.ES_DONE) else 0)
        if latest["status"] == C.ES_DONE:
            status = C.PS_PAID
        elif paid:
            status = C.PS_PART
        else:
            status = C.PS_UNPAID
        rows.append(dict(
            name=name, phone=phones[name], email=emails[name],
            event_date=latest["date"], event_type=latest["type"],
            guests=latest["guests"], venue=venues[latest["id"]],
            package=packages[name], quote=latest["price"], deposit=paid,
            status=status, notes=notes.get(name, "")))
    return rows


CLIENTS = client_rows()


# ---------------------------------------------------------------------------
# menu items  (cost / price are per portion)
# ---------------------------------------------------------------------------
MENU = [
    dict(item="Herb Roast Chicken Platter", category="Main",
         ingredients="Chicken breast, fresh herbs, butter, olive oil",
         portion="1 plate", cost=4.85, price=12.50,
         notes="Signature wedding main"),
    dict(item="Beef Biryani Feast", category="Main",
         ingredients="Beef mince, basmati rice, mixed spice, onions",
         portion="1 plate", cost=3.90, price=9.75, notes="Crowd favourite"),
    dict(item="Chicken Tikka Platter", category="Main",
         ingredients="Chicken breast, yogurt, tikka masala, herbs",
         portion="1 plate", cost=4.40, price=11.50, notes=""),
    dict(item="Grilled Salmon Plate", category="Main",
         ingredients="Salmon fillet, olive oil, lemon, fresh herbs",
         portion="1 plate", cost=8.20, price=18.50, notes="Premium option"),
    dict(item="Creamy Pasta Alfredo", category="Main",
         ingredients="Pasta, heavy cream, cheddar, butter",
         portion="1 plate", cost=2.60, price=7.90, notes="Kids love it"),
    dict(item="Lamb Kofta Curry", category="Main",
         ingredients="Beef mince, onions, tomatoes, whole spices",
         portion="1 bowl", cost=4.10, price=10.50, notes=""),
    dict(item="Garden Salad Bar", category="Sides",
         ingredients="Tomatoes, onions, leafy greens, olive oil",
         portion="1 bowl", cost=1.35, price=4.25, notes="Vegan"),
    dict(item="Garlic Bread Basket", category="Sides",
         ingredients="Flour, butter, garlic, parsley",
         portion="1 basket", cost=0.85, price=2.75, notes=""),
    dict(item="Roast Vegetable Tray", category="Sides",
         ingredients="Seasonal vegetables, olive oil, herbs",
         portion="1 tray", cost=1.20, price=3.90, notes="Vegan"),
    dict(item="Chocolate Fondant", category="Dessert",
         ingredients="Chocolate, butter, eggs, sugar, flour",
         portion="1 piece", cost=1.85, price=5.50, notes="Made fresh on site"),
    dict(item="Lemon Tart", category="Dessert",
         ingredients="Flour, butter, eggs, sugar, lemons",
         portion="1 slice", cost=1.55, price=4.75, notes=""),
    dict(item="Seasonal Fruit Display", category="Dessert",
         ingredients="Fresh seasonal fruit, mint",
         portion="1 plate", cost=1.10, price=3.25, notes=""),
    dict(item="Iced Tea & Lemonade Station", category="Beverage",
         ingredients="Tea, lemons, sugar, mint",
         portion="1 glass", cost=0.45, price=1.90, notes="Self-serve station"),
    dict(item="Chicken Canapes (4 pc)", category="Canape",
         ingredients="Chicken, bread, herbs, butter",
         portion="4 pieces", cost=1.25, price=3.60, notes="Cocktail hour"),
]


# ---------------------------------------------------------------------------
# ingredient inventory
# ---------------------------------------------------------------------------
INVENTORY = [
    dict(ingredient="Basmati Rice", category="Pantry", unit="kg", qty=42,
         min=20, unit_cost=3.80, supplier="Metro Wholesale", notes="Super kernel"),
    dict(ingredient="Chicken Breast", category="Meat & Fish", unit="kg",
         qty=15, min=25, unit_cost=12.00, supplier="City Foods",
         notes="Halal, boneless"),
    dict(ingredient="Beef Mince", category="Meat & Fish", unit="kg", qty=18,
         min=10, unit_cost=9.50, supplier="City Foods", notes=""),
    dict(ingredient="Salmon Fillet", category="Meat & Fish", unit="kg", qty=6,
         min=8, unit_cost=22.00, supplier="City Foods",
         notes="Frozen, order 1 week ahead"),
    dict(ingredient="Olive Oil", category="Pantry", unit="L", qty=9.2, min=6,
         unit_cost=8.20, supplier="Metro Wholesale", notes=""),
    dict(ingredient="Butter", category="Dairy", unit="kg", qty=7, min=5,
         unit_cost=6.40, supplier="Dairy Land", notes="Unsalted"),
    dict(ingredient="Heavy Cream", category="Dairy", unit="L", qty=14, min=8,
         unit_cost=4.10, supplier="Dairy Land", notes=""),
    dict(ingredient="Cheddar Block", category="Dairy", unit="kg", qty=11,
         min=6, unit_cost=7.80, supplier="Dairy Land", notes=""),
    dict(ingredient="Eggs", category="Dairy", unit="tray", qty=24, min=15,
         unit_cost=3.20, supplier="Dairy Land", notes="30 per tray"),
    dict(ingredient="Flour", category="Pantry", unit="kg", qty=30, min=15,
         unit_cost=1.10, supplier="Metro Wholesale", notes=""),
    dict(ingredient="Sugar", category="Pantry", unit="kg", qty=12, min=10,
         unit_cost=1.20, supplier="Metro Wholesale", notes=""),
    dict(ingredient="Mixed Spice", category="Pantry", unit="kg", qty=2.8,
         min=2, unit_cost=14.00, supplier="Spice World", notes="House blend"),
    dict(ingredient="Pasta", category="Pantry", unit="kg", qty=16, min=8,
         unit_cost=2.30, supplier="Metro Wholesale", notes="Penne"),
    dict(ingredient="Tomatoes", category="Produce", unit="kg", qty=8, min=12,
         unit_cost=1.90, supplier="Fresh Mart", notes=""),
    dict(ingredient="Onions", category="Produce", unit="kg", qty=22, min=12,
         unit_cost=0.95, supplier="Fresh Mart", notes=""),
    dict(ingredient="Fresh Herbs", category="Produce", unit="kg", qty=1.8,
         min=2, unit_cost=9.00, supplier="Fresh Mart",
         notes="Coriander, mint, parsley"),
]

INV_QTY = {row["ingredient"]: row["qty"] for row in INVENTORY}
INV_COST = {row["ingredient"]: row["unit_cost"] for row in INVENTORY}


# ---------------------------------------------------------------------------
# shopping list (drives off the next three events)
# ---------------------------------------------------------------------------
SHOPPING = [
    dict(event="EV-2026-003", ingredient="Chicken Breast", required=12,
         supplier="City Foods", purchased=C.TICK, date=_d(9, 8),
         notes="For birani + tikka"),
    dict(event="EV-2026-003", ingredient="Mixed Spice", required=2,
         supplier="Spice World", purchased=C.TICK, date=_d(9, 8), notes=""),
    dict(event="EV-2026-003", ingredient="Fresh Herbs", required=1.5,
         supplier="Fresh Mart", purchased="", date=None, notes="Buy 2 days before"),
    dict(event="EV-2026-004", ingredient="Beef Mince", required=10,
         supplier="City Foods", purchased="", date=None, notes=""),
    dict(event="EV-2026-004", ingredient="Tomatoes", required=8,
         supplier="Fresh Mart", purchased="", date=None, notes=""),
    dict(event="EV-2026-004", ingredient="Heavy Cream", required=6,
         supplier="Dairy Land", purchased=C.TICK, date=_d(9, 11), notes=""),
    dict(event="EV-2026-005", ingredient="Basmati Rice", required=15,
         supplier="Metro Wholesale", purchased="", date=None, notes=""),
    dict(event="EV-2026-005", ingredient="Chicken Breast", required=30,
         supplier="City Foods", purchased="", date=None,
         notes="Order by Sep 20"),
    dict(event="EV-2026-005", ingredient="Salmon Fillet", required=10,
         supplier="City Foods", purchased="", date=None,
         notes="Frozen - 1 week lead time"),
    dict(event="EV-2026-005", ingredient="Butter", required=4,
         supplier="Dairy Land", purchased="", date=None, notes=""),
]


# ---------------------------------------------------------------------------
# expenses  (actual money out, Aug 20 - Sep 12)
# ---------------------------------------------------------------------------
EXPENSES = [
    dict(date=_d(8, 20), vendor="Metro Wholesale", category="Ingredients",
         desc="Chicken breasts - 40 kg (EV-001)", amount=480.00,
         method="Bank Transfer", event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(8, 22), vendor="Metro Wholesale", category="Ingredients",
         desc="Basmati rice - 25 kg sack", amount=95.00, method="Cash",
         event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(8, 24), vendor="Fresh Mart", category="Ingredients",
         desc="Salad produce & vegetables", amount=380.00, method="Card",
         event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(8, 26), vendor="Meta Ads", category="Marketing",
         desc="Instagram & Facebook campaign", amount=220.00, method="Card",
         event="", receipt=C.TICK),
    dict(date=_d(8, 28), vendor="Dairy Land", category="Ingredients",
         desc="Cream, butter & cheese restock", amount=165.00, method="Card",
         event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(8, 30), vendor="ChefGear", category="Equipment",
         desc="Chafing fuel & spare pans", amount=120.00, method="Card",
         event="", receipt=C.TICK),
    dict(date=_d(8, 21), vendor="SecureNow", category="Insurance",
         desc="Public liability - quarterly", amount=450.00,
         method="Bank Transfer", event="", receipt=C.TICK),
    dict(date=_d(9, 1), vendor="Cloud Kitchen Co", category="Kitchen Rental",
         desc="September production kitchen", amount=900.00,
         method="Bank Transfer", event="", receipt=C.TICK),
    dict(date=_d(9, 1), vendor="Metro Wholesale", category="Ingredients",
         desc="Corporate lunch ingredients", amount=240.00,
         method="Bank Transfer", event="EV-2026-002", receipt=C.TICK),
    dict(date=_d(9, 2), vendor="City Utilities", category="Utilities",
         desc="Electricity - August", amount=180.00, method="Bank Transfer",
         event="", receipt=C.TICK),
    dict(date=_d(9, 3), vendor="Ledgerly", category="Software",
         desc="Accounting software - annual", amount=240.00, method="Card",
         event="", receipt=C.TICK),
    dict(date=_d(9, 4), vendor="PrintHub", category="Marketing",
         desc="Menus, flyers & business cards", amount=110.00, method="Card",
         event="", receipt=C.TICK),
    dict(date=_d(9, 5), vendor="Fuel Stop", category="Transportation",
         desc="Delivery van fuel - EV-001 week", amount=90.00, method="Card",
         event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(9, 6), vendor="PackRight", category="Packaging",
         desc="Boxes & cutlery packs (EV-002)", amount=95.00, method="Card",
         event="EV-2026-002", receipt=C.TICK),
    dict(date=_d(9, 6), vendor="Payroll", category="Staff / Labor",
         desc="Event crew wages - EV-001", amount=1456.00,
         method="Bank Transfer", event="EV-2026-001", receipt=C.TICK),
    dict(date=_d(9, 7), vendor="General Store", category="Miscellaneous",
         desc="Cleaning supplies", amount=65.00, method="Cash", event="",
         receipt=C.TICK),
    dict(date=_d(9, 8), vendor="City Utilities", category="Utilities",
         desc="Gas - August", amount=95.00, method="Bank Transfer", event="",
         receipt=C.TICK),
    dict(date=_d(9, 8), vendor="Fresh Mart", category="Ingredients",
         desc="Ingredients - September parties", amount=950.00, method="Card",
         event="EV-2026-003", receipt=""),
    dict(date=_d(9, 9), vendor="ChefGear", category="Equipment",
         desc="Replacement serving utensils", amount=85.00, method="Card",
         event="", receipt=""),
    dict(date=_d(9, 10), vendor="MoveIt Rentals", category="Transportation",
         desc="Refrigerated van rental", amount=150.00, method="Card",
         event="EV-2026-003", receipt=""),
    dict(date=_d(9, 10), vendor="Metro Wholesale", category="Ingredients",
         desc="Rice & flour bulk top-up", amount=260.00,
         method="Bank Transfer", event="EV-2026-004", receipt=""),
    dict(date=_d(9, 11), vendor="PackRight", category="Packaging",
         desc="Platters, foil & serving trays", amount=180.00, method="Card",
         event="", receipt=""),
    dict(date=_d(9, 11), vendor="City Foods", category="Ingredients",
         desc="Meat & poultry bulk - Oct weddings", amount=1490.00,
         method="Bank Transfer", event="EV-2026-007", receipt=""),
    dict(date=_d(9, 11), vendor="Payroll", category="Staff / Labor",
         desc="Chef & servers - EV-002", amount=582.00,
         method="Bank Transfer", event="EV-2026-002", receipt=C.TICK),
    dict(date=_d(9, 12), vendor="Payroll", category="Staff / Labor",
         desc="Kitchen prep team - week 37", amount=560.00,
         method="Bank Transfer", event="", receipt=""),
    dict(date=_d(9, 12), vendor="City Foods", category="Ingredients",
         desc="Seafood & premium produce", amount=640.00,
         method="Bank Transfer", event="EV-2026-006", receipt=""),
]


# ---------------------------------------------------------------------------
# income / invoices  (one per booked event, cancelled excluded)
# ---------------------------------------------------------------------------
def income_rows():
    rows, n = [], 1000
    for ev in EVENTS:
        if ev["status"] == C.ES_CANCEL:
            continue
        n += 1
        price, dep = ev["price"], ev["deposit"]
        paid_full = ev["status"] == C.ES_DONE
        pay2 = price - dep if paid_full else 0
        # one deliberately late balance so the OVERDUE flag has something to do
        due = _d(9, 10) if ev["id"] == "EV-2026-004" else ev["date"]
        rows.append(dict(
            invoice="INV-%d" % n, client=ev["client"], event_date=ev["date"],
            amount=price, deposit=dep, pay1=0, pay2=pay2,
            due=due, event_id=ev["id"]))
    return rows


INCOME = income_rows()


# ---------------------------------------------------------------------------
# staff shifts
# ---------------------------------------------------------------------------
STAFF = [
    dict(name="Imran Qureshi", role="Head Chef", event="EV-2026-001", hours=14,
         rate=25, ot=2, paid=C.TICK, notes="Ran both seatings"),
    dict(name="Fatima Noor", role="Sous Chef", event="EV-2026-001", hours=12,
         rate=18, ot=0, paid=C.TICK, notes=""),
    dict(name="Ali Hassan", role="Chef", event="EV-2026-001", hours=12,
         rate=16, ot=0, paid=C.TICK, notes=""),
    dict(name="Zoya Sheikh", role="Server", event="EV-2026-001", hours=10,
         rate=11, ot=2, paid=C.TICK, notes=""),
    dict(name="Hassan Raza", role="Server", event="EV-2026-001", hours=10,
         rate=11, ot=0, paid=C.TICK, notes=""),
    dict(name="Maryam Javed", role="Bartender", event="EV-2026-001", hours=10,
         rate=13, ot=0, paid=C.TICK, notes=""),
    dict(name="Kashif Ali", role="Driver", event="EV-2026-001", hours=8,
         rate=12, ot=0, paid=C.TICK, notes="Two delivery runs"),
    dict(name="Nadia Aslam", role="Setup Crew", event="EV-2026-001", hours=9,
         rate=10, ot=0, paid=C.TICK, notes=""),
    dict(name="Usman Ghani", role="Cleaner", event="EV-2026-001", hours=6,
         rate=9, ot=0, paid=C.TICK, notes=""),
    dict(name="Imran Qureshi", role="Head Chef", event="EV-2026-002", hours=8,
         rate=25, ot=0, paid=C.TICK, notes=""),
    dict(name="Fatima Noor", role="Sous Chef", event="EV-2026-002", hours=8,
         rate=18, ot=0, paid=C.TICK, notes=""),
    dict(name="Ali Hassan", role="Chef", event="EV-2026-002", hours=7,
         rate=16, ot=0, paid=C.TICK, notes=""),
    dict(name="Zoya Sheikh", role="Server", event="EV-2026-002", hours=6,
         rate=11, ot=0, paid=C.TICK, notes=""),
    dict(name="Kashif Ali", role="Driver", event="EV-2026-002", hours=5,
         rate=12, ot=0, paid=C.TICK, notes=""),
    dict(name="Imran Qureshi", role="Head Chef", event="EV-2026-003", hours=10,
         rate=25, ot=0, paid="", notes="Scheduled"),
    dict(name="Sara Butt", role="Server", event="EV-2026-003", hours=8,
         rate=11, ot=0, paid="", notes="Scheduled"),
    dict(name="Hassan Raza", role="Server", event="EV-2026-004", hours=9,
         rate=11, ot=0, paid="", notes="Scheduled"),
    dict(name="Bilal Ahmad", role="Setup Crew", event="EV-2026-005", hours=8,
         rate=10, ot=0, paid="", notes="Scheduled"),
]


# ---------------------------------------------------------------------------
# equipment
# ---------------------------------------------------------------------------
EQUIPMENT = [
    dict(item="Chafing Dishes (full size)", category="Serving", owned=24,
         reserved=8, damaged=1, unit_value=45, maintenance=_d(10, 1),
         notes="1 dented lid"),
    dict(item="Round Banquet Tables", category="Furniture", owned=20,
         reserved=0, damaged=0, unit_value=60, maintenance=_d(12, 1),
         notes="Seats 10 each"),
    dict(item="Rectangular Tables", category="Furniture", owned=15, reserved=6,
         damaged=0, unit_value=45, maintenance=date(2027, 1, 15),
         notes=""),
    dict(item="Banquet Chairs", category="Furniture", owned=200, reserved=80,
         damaged=4, unit_value=12, maintenance=date(2026, 11, 1),
         notes="4 frames bent"),
    dict(item="Table Linen Sets", category="Linens", owned=40, reserved=12,
         damaged=2, unit_value=18, maintenance=date(2026, 10, 5),
         notes="2 sets stained - replace"),
    dict(item="Dinnerware Sets (10 pc)", category="Tableware", owned=30,
         reserved=10, damaged=0, unit_value=25, maintenance=date(2027, 2, 1),
         notes=""),
    dict(item="Glassware Sets", category="Tableware", owned=60, reserved=20,
         damaged=3, unit_value=6, maintenance=date(2026, 10, 10),
         notes="Chips on 3 goblets"),
    dict(item="Cutlery Sets", category="Tableware", owned=250, reserved=100,
         damaged=0, unit_value=3, maintenance=date(2027, 3, 1), notes=""),
    dict(item="Beverage Dispensers", category="Beverage", owned=8,
         reserved=2, damaged=0, unit_value=55, maintenance=date(2026, 9, 25),
         notes="Tap service check"),
    dict(item="Portable Gas Ranges", category="Kitchen", owned=4, reserved=1,
         damaged=0, unit_value=320, maintenance=date(2026, 10, 8),
         notes=""),
    dict(item="Refrigerated Trailer", category="Transport", owned=1,
         reserved=1, damaged=0, unit_value=4500, maintenance=date(2026, 9, 20),
         notes="Booked for EV-007"),
    dict(item="Coffee Urns (100 cup)", category="Beverage", owned=6,
         reserved=2, damaged=1, unit_value=70, maintenance=date(2026, 12, 15),
         notes="1 element burnt out"),
]


# ---------------------------------------------------------------------------
# suppliers
# ---------------------------------------------------------------------------
SUPPLIERS = [
    dict(supplier="Metro Wholesale", contact="Aslam Bhai",
         phone="0300-1234567", email="orders@metrowholesale.example",
         category="Pantry", item="Rice, flour, pulses, oil", price=3.80,
         min_order=100, delivery="Next day", terms="Net 15",
         notes="Bulk discount over $500"),
    dict(supplier="City Foods", contact="Rana Sahib", phone="0321-7654321",
         email="sales@cityfoods.example", category="Meat & Fish",
         item="Chicken, beef, lamb, fish", price=12.00, min_order=50,
         delivery="Same day", terms="Cash", notes="Halal certified"),
    dict(supplier="Fresh Mart", contact="Ayesha K.", phone="0333-2224444",
         email="hello@freshmart.example", category="Produce",
         item="Vegetables, fruit, herbs", price=1.90, min_order=30,
         delivery="Same day", terms="Cash", notes="Farm fresh, seasonal"),
    dict(supplier="Dairy Land", contact="Usman D.", phone="0345-8889999",
         email="info@dairyland.example", category="Dairy",
         item="Cream, butter, cheese, eggs", price=6.40, min_order=40,
         delivery="Next day", terms="Net 7", notes=""),
    dict(supplier="Spice World", contact="Sana M.", phone="0301-5557777",
         email="orders@spiceworld.example", category="Pantry",
         item="Whole & ground spices", price=14.00, min_order=25,
         delivery="2 days", terms="Prepaid", notes="Custom blends available"),
    dict(supplier="PackRight", contact="Kamran S.", phone="0302-1112222",
         email="sales@packright.example", category="Packaging",
         item="Platters, boxes, cutlery", price=0.55, min_order=100,
         delivery="3 days", terms="Net 15", notes="Eco range available"),
    dict(supplier="ChefGear", contact="Adnan R.", phone="0334-7778888",
         email="support@chefgear.example", category="Equipment",
         item="Chafers, utensils, spares", price=45.00, min_order=0,
         delivery="4 days", terms="Net 30", notes=""),
    dict(supplier="Linen & Co", contact="Hira T.", phone="0311-4445555",
         email="hello@linenco.example", category="Linens",
         item="Cloths, napkins, runners", price=18.00, min_order=20,
         delivery="5 days", terms="50% advance", notes=""),
    dict(supplier="Beverage House", contact="Zeeshan A.",
         phone="0322-6667777", email="orders@bevhouse.example",
         category="Beverage", item="Teas, juices, syrups, water", price=2.10,
         min_order=60, delivery="2 days", terms="Net 15", notes=""),
    dict(supplier="Event Ice Co", contact="Mariam N.", phone="0308-3334444",
         email="info@eventice.example", category="Other",
         item="Ice, dry ice, cooler rental", price=0.80, min_order=50,
         delivery="Same day", terms="Cash", notes="Delivers to venue"),
]


# ---------------------------------------------------------------------------
# quote calculator demo state
# ---------------------------------------------------------------------------
QUOTE = dict(client="Fatima & Co (new enquiry)", date=_d(10, 31),
             guests=120, food_pp=9.50, labor=1200.00, equipment=250.00,
             transport=120.00, other=150.00)


# ---------------------------------------------------------------------------
# tax payments logged so far (tax sheet)
# ---------------------------------------------------------------------------
TAX_PAID = [
    dict(date=_d(7, 15), desc="Q2 sales tax filing", amount=610.00),
    dict(date=_d(8, 14), desc="Advance income tax", amount=400.00),
]


# ===========================================================================
# derived numbers + aggregates
# ===========================================================================
class Model(object):
    """Computed sample business - mirrors the Christmas tracker Model API."""

    def __init__(self, mode="demo", edition="premium"):
        self.mode = mode
        self.edition = edition
        self.demo = (mode == "demo")
        self.settings = dict(SETTINGS) if self.demo else {
            "business": "", "currency": "$", "tax": 0.0, "margin": 0.35,
            "deposit": 0.40, "duesoon": 7, "year": date.today().year,
            "cal_month": date.today().month, "cal_year": date.today().year,
            "message": "",
        }
        self.events = EVENTS if self.demo else []
        self.clients = CLIENTS if self.demo else []
        self.menu = MENU if self.demo else []
        self.inventory = INVENTORY if self.demo else []
        self.shopping = SHOPPING if self.demo else []
        self.expenses = EXPENSES if self.demo else []
        self.income = INCOME if self.demo else []
        self.staff = STAFF if self.demo else []
        self.equipment = EQUIPMENT if self.demo else []
        self.suppliers = SUPPLIERS if self.demo else []
        self.quote = dict(QUOTE) if self.demo else {}
        self.tax_paid = TAX_PAID if self.demo else []
        self.checks = {}
        self.agg = {}
        if self.demo:
            self._derive()

    def money(self, value, decimals=0):
        fmt = ",.%df" % decimals
        return self.settings["currency"] + format(value or 0, fmt)

    # ------------------------------------------------------------------
    def _derive(self):
        ev = self.events
        live = [e for e in ev if e["status"] != C.ES_CANCEL]
        done = [e for e in ev if e["status"] == C.ES_DONE]
        upcoming = [e for e in ev if e["status"] in
                    (C.ES_DEPOSIT, C.ES_CONFIRMED) and e["date"] >= TODAY]

        # per-event money
        for e in ev:
            e["profit"] = e["price"] - e["cost"]
            e["margin"] = (e["profit"] / e["price"]) if e["price"] else 0
            e["balance"] = e["price"] - e["deposit"]

        # income derivations
        for inv in self.income:
            e = next(x for x in ev if x["id"] == inv["event_id"])
            inv["received"] = inv["deposit"] + inv["pay1"] + inv["pay2"]
            inv["balance"] = inv["amount"] - inv["received"]
            if inv["received"] >= inv["amount"]:
                inv["status"] = C.PS_PAID
            elif inv["received"] > 0:
                inv["status"] = C.PS_PART
            else:
                inv["status"] = C.PS_UNPAID
            inv["overdue"] = (inv["balance"] > 0 and inv["due"] < TODAY)

        # shopping derivations
        for s in self.shopping:
            s["available"] = INV_QTY.get(s["ingredient"], 0)
            s["to_buy"] = max(0.0, s["required"] - s["available"])
            s["est_cost"] = round(s["to_buy"] * INV_COST.get(s["ingredient"], 0), 2)

        # menu derivations
        for m in self.menu:
            m["profit"] = round(m["price"] - m["cost"], 2)
            m["margin"] = (m["profit"] / m["price"]) if m["price"] else 0

        # inventory derivations
        for it in self.inventory:
            it["value"] = round(it["qty"] * it["unit_cost"], 2)
            if it["qty"] < it["min"]:
                it["status"] = "\U0001F534 Reorder"
            elif it["qty"] < it["min"] * 1.5:
                it["status"] = "\U0001F7E1 Low"
            else:
                it["status"] = "\U0001F7E2 OK"

        # staff derivations
        for s in self.staff:
            s["total"] = round(s["hours"] * s["rate"]
                               + s["ot"] * s["rate"] * 1.5, 2)

        # equipment derivations
        for q in self.equipment:
            q["available"] = q["owned"] - q["reserved"] - q["damaged"]
            q["value"] = q["owned"] * q["unit_value"]
            if q["damaged"] > 0:
                q["status"] = "\U0001F527 Service"
            elif q["maintenance"] <= date(2026, 10, 12):
                q["status"] = "\U0001F7E1 Soon"
            else:
                q["status"] = "\U0001F7E2 Ready"

        # quote calculator outputs
        q = self.quote
        food_total = q["guests"] * q["food_pp"]
        cost_total = food_total + q["labor"] + q["equipment"] \
            + q["transport"] + q["other"]
        margin = self.settings["margin"]
        price = cost_total / (1 - margin) if margin < 1 else cost_total
        q.update(food_total=food_total, cost_total=cost_total,
                 profit=price - cost_total, price=price,
                 per_guest=price / q["guests"],
                 deposit=price * self.settings["deposit"],
                 balance=price * (1 - self.settings["deposit"]),
                 cost_pp=cost_total / q["guests"])

        # ------------------------------------------------------------
        # aggregates (cached KPI / report values)
        # ------------------------------------------------------------
        a = self.agg
        revenue = sum(i["received"] for i in self.income)
        expenses = sum(x["amount"] for x in self.expenses)
        food_cost = sum(x["amount"] for x in self.expenses
                        if x["category"] in ("Ingredients", "Packaging"))
        labor_cost = sum(x["amount"] for x in self.expenses
                         if x["category"] == "Staff / Labor")
        outstanding = sum(i["balance"] for i in self.income)
        overdue_n = sum(1 for i in self.income if i["overdue"])
        invoices_open = sum(1 for i in self.income if i["balance"] > 0)

        a["revenue"] = revenue
        a["expenses"] = expenses
        a["profit"] = revenue - expenses
        a["margin"] = (revenue - expenses) / revenue if revenue else 0
        a["events_total"] = len(ev)
        a["events_done"] = len(done)
        a["events_confirmed"] = len([e for e in ev if e["status"] in
                                     (C.ES_DEPOSIT, C.ES_CONFIRMED)])
        a["events_cancelled"] = sum(1 for e in ev
                                    if e["status"] == C.ES_CANCEL)
        a["avg_order"] = sum(e["price"] for e in live) / len(live)
        a["avg_guests"] = sum(e["guests"] for e in live) / len(live)
        a["avg_profit"] = sum(e["profit"] for e in live) / len(live)
        a["guests_total"] = sum(e["guests"] for e in done)
        a["outstanding"] = outstanding
        a["overdue"] = overdue_n
        a["invoices_open"] = invoices_open
        a["food_cost"] = food_cost
        a["labor_cost"] = labor_cost
        a["food_pct"] = food_cost / revenue if revenue else 0
        a["labor_pct"] = labor_cost / revenue if revenue else 0
        repeat = sum(1 for name in {e["client"] for e in ev}
                     if sum(1 for e in ev if e["client"] == name) > 1)
        a["repeat_pct"] = repeat / len(CLIENTS)
        a["inv_value"] = round(sum(i["value"] for i in self.inventory), 2)
        a["low_stock"] = sum(1 for i in self.inventory
                             if i["qty"] < i["min"])
        a["shop_lines"] = sum(1 for s in self.shopping
                              if s["to_buy"] > 0 and s["purchased"] != C.TICK)
        a["shop_cost"] = round(sum(s["est_cost"] for s in self.shopping
                                   if s["purchased"] != C.TICK), 2)
        a["staff_unpaid"] = sum(1 for s in self.staff if s["paid"] != C.TICK)
        a["equip_value"] = sum(q["value"] for q in self.equipment)
        a["equip_service"] = sum(1 for q in self.equipment
                                 if q["damaged"] > 0
                                 or q["maintenance"] <= date(2026, 10, 12))
        taxable = sum(i["amount"] for i in self.income)
        a["tax_collected"] = round(taxable * self.settings["tax"], 2)
        a["tax_due"] = round(a["tax_collected"]
                             - sum(t["amount"] for t in self.tax_paid), 2)
        a["quote_price"] = round(q["price"], 2)
        a["quote_per_guest"] = round(q["per_guest"], 2)
        a["menu_items"] = len(self.menu)
        a["menu_margin"] = sum(m["margin"] for m in self.menu) / len(self.menu)

        # monthly pools (cash in, by event month)
        months = []
        for mi in range(12):
            label = MONTH_SHORT[mi]
            mrev = sum(i["received"] for i in self.income
                       if i["event_date"].month == mi + 1)
            mexp = sum(x["amount"] for x in self.expenses
                       if x["date"].month == mi + 1)
            mcnt = sum(1 for e in ev if e["date"].month == mi + 1)
            months.append((label, mrev, mexp, mrev - mexp, mcnt))
        a["months"] = months

        # revenue by event type (booked price, cancelled excluded)
        a["types"] = [(t, sum(e["price"] for e in live if e["type"] == t))
                      for t in C.EVENT_TYPES]

        # revenue by client (cash received)
        a["clients_pool"] = [(cl["name"],
                              sum(i["received"] for i in self.income
                                  if i["client"] == cl["name"]))
                             for cl in self.clients]

        # menu popularity (events featuring each dish)
        a["menu_pool"] = [(m["item"],
                           sum(1 for e in live if m["item"] in e["menu"]))
                          for m in self.menu]

        # checklist tick state for the EXAMPLE build
        self.checks = {
            "prep": set(range(8)),
            "shop": {0, 1, 2, 3, 5, 6},
            "day": set(),
            "end": set(range(8)),
        }

        # expense-category + status pools for the charts
        a["exp_cats"] = {}
        for x in self.expenses:
            a["exp_cats"][x["category"]] = \
                a["exp_cats"].get(x["category"], 0) + x["amount"]
        a["status_counts"] = {}
        for e in ev:
            a["status_counts"][e["status"]] = \
                a["status_counts"].get(e["status"], 0) + 1

        best_type = max(a["types"], key=lambda t: t[1])
        best_client = max(a["clients_pool"], key=lambda t: t[1])
        a["best_type"] = best_type[0] if best_type[1] else "-"
        a["best_client"] = best_client[0] if best_client[1] else "-"

        # upcoming-events pool (future, not cancelled/done) + dues pool
        a["upcoming"] = [(e["date"], "%s - %s" % (e["client"], e["type"]),
                          e["status"])
                         for e in ev
                         if e["date"] >= TODAY and e["status"] not in
                         (C.ES_CANCEL, C.ES_DONE)]
        a["dues"] = [(i["due"], "%s (%s)" % (i["client"], i["invoice"]),
                      i["balance"])
                     for i in self.income if i["balance"] > 0]
