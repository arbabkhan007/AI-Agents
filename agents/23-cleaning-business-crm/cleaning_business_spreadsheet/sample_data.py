"""Example data for the Cleaning Business CRM.

`build(cfg)` fills the module-level lists with a coherent demo book of
business for Bright & Tidy Cleaning Co. - a real cleaning company in
microcosm: clients, properties, quotes, a schedule of jobs, timesheets,
costs, invoices and payments that all tie out.

Every date is generated relative to `cfg.today`, so the dashboard always
opens on a live-looking business.  Numbers are handcrafted (not random),
so the file is deterministic and the sample checks can assert on it.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# module state - filled by build(cfg)
# ---------------------------------------------------------------------------

CLIENTS: List[Dict[str, Any]] = []
PROPERTIES: List[Dict[str, Any]] = []
LEADS: List[Dict[str, Any]] = []
SERVICES: List[Dict[str, Any]] = []
QUOTES: List[Dict[str, Any]] = []
QUOTE_LINES: List[Dict[str, Any]] = []
JOBS: List[Dict[str, Any]] = []
JOB_TASKS: List[Dict[str, Any]] = []
CHECKLISTS: List[Dict[str, Any]] = []
EMPLOYEES: List[Dict[str, Any]] = []
TIMESHEETS: List[Dict[str, Any]] = []
JOB_COSTING: List[Dict[str, Any]] = []
INVOICES: List[Dict[str, Any]] = []
INVOICE_LINES: List[Dict[str, Any]] = []
PAYMENTS: List[Dict[str, Any]] = []
SUPPLIES: List[Dict[str, Any]] = []
SUPPLY_USAGE: List[Dict[str, Any]] = []
EQUIPMENT: List[Dict[str, Any]] = []
EXPENSES: List[Dict[str, Any]] = []
MILEAGE: List[Dict[str, Any]] = []
COMPLAINTS: List[Dict[str, Any]] = []
SAFETY: List[Dict[str, Any]] = []
INCIDENTS: List[Dict[str, Any]] = []

ALL = [
    "CLIENTS", "PROPERTIES", "LEADS", "SERVICES", "QUOTES",
    "QUOTE_LINES", "JOBS", "JOB_TASKS", "CHECKLISTS", "EMPLOYEES",
    "TIMESHEETS", "JOB_COSTING", "INVOICES", "INVOICE_LINES",
    "PAYMENTS", "SUPPLIES", "SUPPLY_USAGE", "EQUIPMENT", "EXPENSES",
    "MILEAGE", "COMPLAINTS", "SAFETY", "INCIDENTS",
]


def _rows(keys: List[str], table: List[tuple]) -> List[Dict[str, Any]]:
    out = []
    for tup in table:
        row = {}
        for k, v in zip(keys, tup):
            if v is not None:
                row[k] = v
        out.append(row)
    return out


def build(cfg: Any) -> None:
    """Fill every sample list relative to cfg.today."""
    global CLIENTS, PROPERTIES, LEADS, SERVICES, QUOTES, QUOTE_LINES
    global JOBS, JOB_TASKS, CHECKLISTS, EMPLOYEES, TIMESHEETS, JOB_COSTING
    global INVOICES, INVOICE_LINES, PAYMENTS, SUPPLIES, SUPPLY_USAGE
    global EQUIPMENT, EXPENSES, MILEAGE, COMPLAINTS, SAFETY, INCIDENTS

    t: dt.date = cfg.today

    def d(days: int) -> dt.date:
        return t + dt.timedelta(days=days)

    # ---------------------------------------------------------------- team
    EMPLOYEES = _rows(
        ["name", "role", "phone", "email", "hourly_pay", "hire_date",
         "status", "emergency", "certs", "notes"],
        [
            ("Dana Whitfield", "Owner", "(503) 555 0101",
             "dana@brightandtidy.co", 32.00, dt.date(2019, 3, 4), "Active",
             "Rob Whitfield (503) 555 0102", "First aid, OSHA 30",
             "Founder. Still takes the big commercial jobs."),
            ("Marisol Reyes", "Team lead", "(503) 555 0111",
             "marisol@brightandtidy.co", 22.00, dt.date(2020, 6, 15),
             "Active", "Luis Reyes (503) 555 0112",
             "First aid, DBS check", "Runs the north side crew."),
            ("Tasha Kim", "Cleaner", "(503) 555 0121",
             "tasha@brightandtidy.co", 18.50, dt.date(2021, 2, 1),
             "Active", "Jin Kim (503) 555 0122", "DBS check",
             "Best with deep cleans and ovens."),
            ("Jordan Blake", "Cleaner", "(503) 555 0131",
             "jordan@brightandtidy.co", 18.00, dt.date(2022, 9, 12),
             "Active", "Kim Blake (503) 555 0132", "OSHA 10",
             "Prefers morning slots."),
            ("Priya Nair", "Cleaner", "(503) 555 0141",
             "priya@brightandtidy.co", 19.00, dt.date(2023, 1, 9),
             "Active", "Arun Nair (503) 555 0142", "First aid",
             "Trained on the floor machines."),
            ("Sam Okafor", "Driver", "(503) 555 0151",
             "sam@brightandtidy.co", 20.00, dt.date(2021, 11, 2),
             "Active", "Ada Okafor (503) 555 0152",
             "Clean driving licence", "Van 2. Also does pressure washing."),
            ("Lena Ford", "Cleaner", "(503) 555 0161",
             "lena@brightandtidy.co", 18.00, dt.date(2024, 4, 8),
             "Active", "Mark Ford (503) 555 0162", "DBS check",
             "Newest hire - great with clients."),
            ("Chris Dalton", "Admin", "(503) 555 0171",
             "chris@brightandtidy.co", 21.00, dt.date(2020, 1, 20),
             "Active", "Sam Dalton (503) 555 0172", "Bookkeeping cert",
             "Invoices, quotes, chasing payments."),
        ])

    # ------------------------------------------------------------- clients
    CLIENTS = _rows(
        ["name", "type", "contact", "email", "phone", "address", "city",
         "source", "frequency", "since", "status", "property_ref",
         "notes", "rating"],
        [
            ("Whitfield Family", "Residential", "Sarah Whitfield",
             "sarah.w@email.com", "(503) 555 2001", "44 Alder Court",
             "Portland", "Referral", "Fortnightly",
             dt.date(2021, 4, 12), "Active", "Whitfield - Family Home",
             "Dog (Biscuit). Key safe by the side gate.", 5),
            ("Nguyen Household", "Residential", "Linh Nguyen",
             "linh.n@email.com", "(503) 555 2002", "2180 SE Stark St",
             "Portland", "Google", "Weekly",
             dt.date(2022, 1, 8), "Active", "Nguyen - Townhouse",
             "Two cats. Prefers unscented products.", 5),
            ("Harborview Dental", "Commercial", "Dr. Ellen Park",
             "epark@harborview.dental", "(503) 555 2003",
             "900 NW Naito Pkwy, Suite 210", "Portland", "Referral",
             "Weekly", dt.date(2020, 9, 1), "Active",
             "Harborview Dental - Clinic",
             "Clinical waste protocols apply. After-hours only.", 5),
            ("Bramble & Vine Cafe", "Commercial", "Owen Hart",
             "owen@bramblevine.cafe", "(503) 555 2004",
             "77 SE Belmont St", "Portland", "Walk-in", "Twice a week",
             dt.date(2023, 3, 20), "Active", "Bramble & Vine - Cafe",
             "Kitchen deep clean monthly. Early mornings.", 4),
            ("Colin Mercer", "Residential", "Colin Mercer",
             "cmercer@email.com", "(503) 555 2005", "1503 SW Vista Ave",
             "Portland", "Yelp", "Monthly",
             dt.date(2022, 7, 30), "Active", "Mercer - Condo",
             "Travels a lot - confirm the week before.", 4),
            ("Riverside Yoga Studio", "Commercial", "Amara Singh",
             "amara@riverside.yoga", "(503) 555 2006",
             "312 NE Couch St", "Portland", "Instagram", "Weekly",
             dt.date(2023, 8, 14), "Active", "Riverside Yoga - Studio",
             "Mirrors and floors are the priority.", 5),
            ("Elena Vasquez", "Residential", "Elena Vasquez",
             "elena.v@email.com", "(503) 555 2007", "845 N Tillamook St",
             "Portland", "Referral", "Every 3 weeks",
             dt.date(2024, 2, 2), "Active", "Vasquez - Bungalow",
             "New baby in the house - fragrance free.", 5),
            ("Fairmount Apartments", "Commercial", "Greg Lyle",
             "g.fairmount@email.com", "(503) 555 2008",
             "1500 SE Fairmount Blvd", "Portland", "Partner", "Weekly",
             dt.date(2021, 11, 5), "Active",
             "Fairmount - Communal Areas",
             "Turnover cleans between tenants as needed.", 4),
            ("The Okonkwo Family", "Residential", "Beatrice Okonkwo",
             "b.okonkwo@email.com", "(503) 555 2009",
             "6212 SE Woodstock Blvd", "Portland", "Facebook", "Weekly",
             dt.date(2023, 5, 19), "Active", "Okonkwo - Family Home",
             "Three kids, one very friendly labrador.", 5),
            ("Cascade Legal Group", "Commercial", "Peter Huang",
             "phuang@cascadelegal.com", "(503) 555 2010",
             "1200 SW 6th Ave, Floor 8", "Portland", "Referral",
             "Weekly", dt.date(2022, 2, 14), "Active",
             "Cascade Legal - Office Floor",
             "Confidential waste bins. Fridays after 6pm.", 4),
            ("Martha Doyle", "Residential", "Martha Doyle",
             "m.doyle@email.com", "(503) 555 2011", "4128 NE 22nd Ave",
             "Portland", "Referral", "Fortnightly",
             dt.date(2020, 5, 11), "Active", "Doyle - Family Home",
             "Elderly client - always knock twice.", 5),
            ("Sundial Bookshop", "Commercial", "Rosa Delgado",
             "rosa@sundial.books", "(503) 555 2012", "3555 SE Hawthorne",
             "Portland", "Flyer", "Weekly",
             dt.date(2024, 1, 22), "Active", "Sundial - Bookshop",
             "Careful with the rare books shelf.", 5),
            ("Tyler Briggs", "Residential", "Tyler Briggs",
             "tyler.b@email.com", "(503) 555 2013", "901 SW 18th Ave",
             "Portland", "Google", "Monthly",
             dt.date(2023, 10, 7), "Active", "Briggs - Apartment",
             "Bachelor pad - always needs the kitchen deep.", 4),
            ("Lakeview HOA", "Commercial", "Denise Park",
             "denise@lakeviewhoa.org", "(503) 555 2014",
             "4000 NE Halsey St", "Portland", "Partner", "Weekly",
             dt.date(2022, 6, 1), "Active", "Lakeview HOA - Clubhouse",
             "Gym and pool house included.", 4),
            ("Grace Okafor", "Residential", "Grace Okafor",
             "grace.o@email.com", "(503) 555 2015", "5510 SE Woodstock",
             "Portland", "Referral", "Every 3 weeks",
             dt.date(2024, 3, 30), "Active", "Okafor - Family Home",
             "Prefers Fridays.", 5),
            ("Northbank Coworking", "Commercial", "Iris Chen",
             "iris@northbank.work", "(503) 555 2016",
             "220 NE Oregon St", "Portland", "Google", "Twice a week",
             dt.date(2023, 12, 1), "Active",
             "Northbank Coworking - Main Floor",
             "24/7 access fob held by Iris.", 4),
            ("Paul & Nina Reyes", "Residential", "Nina Reyes",
             "nina.reyes@email.com", "(503) 555 2017",
             "127 SE 28th Ave", "Portland", "Referral", "Weekly",
             dt.date(2021, 8, 23), "Active", "Reyes - Family Home",
             "Wedding photos wall - dust carefully.", 5),
            ("Hawthorne Auto Care", "Commercial", "Big Mike",
             "mike@hawthorneauto.com", "(503) 555 2018",
             "4411 SE Hawthorne Blvd", "Portland", "Walk-in", "Monthly",
             dt.date(2023, 4, 17), "Active", "Hawthorne Auto - Shop",
             "Grease floors - heavy duty kit needed.", 3),
            ("Jenna Park", "Residential", "Jenna Park",
             "jenna.park@email.com", "(503) 555 2019",
             "2330 N Williams Ave", "Portland", "Instagram", "Monthly",
             dt.date(2024, 5, 6), "Active", "Park - Loft",
             "Found us through Instagram - loves the checklist.", 5),
            ("St. Marks Community Hall", "Commercial", "Rev. Alan Ford",
             "alan@stmarks.org", "(503) 555 2020", "805 NE 8th Ave",
             "Portland", "Referral", "Fortnightly",
             dt.date(2022, 10, 3), "Active",
             "St Marks - Main Hall",
             "Events at weekends - clean early Monday.", 4),
            ("Chris & Amy Lombardi", "Residential", "Amy Lombardi",
             "amy.l@email.com", "(503) 555 2021", "7230 SE 32nd Ave",
             "Portland", "Referral", "Fortnightly",
             dt.date(2022, 3, 28), "Active", "Lombardi - Family Home",
             "Wine cellar - stay out unless asked.", 5),
            ("Priya Sharma", "Residential", "Priya Sharma",
             "priya.s@email.com", "(503) 555 2022", "1644 SE Bybee Blvd",
             "Portland", "Google", "Monthly",
             dt.date(2024, 6, 12), "Active", "Sharma - Townhouse",
             "Happy to be a reference.", 5),
            ("Aisha Mohammed", "Residential", "Aisha Mohammed",
             "aisha.m@email.com", "(503) 555 3005", "2910 NE 33rd Ave",
             "Portland", "Facebook", "One-off",
             d(-5), "Active", "Mohammed - New Home",
             "New client - moved in this month. Quote Q-1022 accepted.",
             5),
            ("Baxter Insurance", "Commercial", "Joyce Baxter",
             "joyce@baxterinsure.com", "(503) 555 2023",
             "520 SW Yamhill St, Suite 300", "Portland", "Referral",
             "Weekly", dt.date(2021, 1, 18), "Active",
             "Baxter Insurance - Office",
             "Kitchen and washrooms nightly; carpets monthly.", 4),
            ("Leo Martinez", "Residential", "Leo Martinez",
             "leo.m@email.com", "(503) 555 2024", "3101 NE 15th Ave",
             "Portland", "Yelp", "One-off",
             dt.date(2024, 7, 2), "Inactive", "Martinez - Apartment",
             "One-off move-out clean - great review on Yelp.", 5),
        ])

    # --------------------------------------------------------- properties
    PROPERTIES = _rows(
        ["property_name", "client", "type", "address", "city", "postcode",
         "size", "bedrooms", "bathrooms", "rooms", "floors", "travel",
         "access", "parking", "pets", "alarm", "hazards", "notes"],
        [
            ("Whitfield - Family Home", "Whitfield Family", "House",
             "44 Alder Court", "Portland", "97214", 2400, 4, 2.5, 3, 2,
             7, "Key safe - code 4412", "On site", "Dog", "None",
             "Dog (Biscuit) - friendly", "Alarm panel by the door."),
            ("Nguyen - Townhouse", "Nguyen Household", "House",
             "2180 SE Stark St", "Portland", "97214", 1650, 3, 2, 2, 2,
             5, "Lockbox - code 1180", "Street", "Cats", "None",
             "Two cats - keep doors shut", "Litter box area daily."),
            ("Harborview Dental - Clinic", "Harborview Dental",
             "Medical", "900 NW Naito Pkwy, Suite 210", "Portland",
             "97209", 3200, 0, 2, 6, 1, 12, "Fob - reception",
             "Paid", "None", "After-hours alarm",
             "Clinical waste - red bag protocol", "Sharps containers present."),
            ("Bramble & Vine - Cafe", "Bramble & Vine Cafe",
             "Restaurant", "77 SE Belmont St", "Portland", "97214",
             1400, 0, 1, 3, 1, 6, "Key with manager", "Permit",
             "None", "None", "Hot kitchen equipment", "Grease trap area."),
            ("Mercer - Condo", "Colin Mercer", "Condo",
             "1503 SW Vista Ave", "Portland", "97219", 1100, 2, 2, 1, 1,
             9, "Concierge", "Paid", "None", "Concierge alarm",
             "None", "Building has service lift."),
            ("Riverside Yoga - Studio", "Riverside Yoga Studio",
             "Studio", "312 NE Couch St", "Portland", "97232", 2000, 0,
             2, 2, 1, 8, "Code - 2200", "Street", "None", "None",
             "Mirrors - use streak-free only", "Cork floors - no bleach."),
            ("Vasquez - Bungalow", "Elena Vasquez", "House",
             "845 N Tillamook St", "Portland", "97227", 1350, 3, 1, 2,
             1, 10, "Key under the pot", "Street", "None", "None",
             "Baby - fragrance free products only", "Nursery is off limits."),
            ("Fairmount - Communal Areas", "Fairmount Apartments",
             "Apartment", "1500 SE Fairmount Blvd", "Portland",
             "97214", 4800, 0, 4, 8, 3, 4, "Office key", "On site",
             "None", "None", "Lobby always busy", "Includes laundry room."),
            ("Okonkwo - Family Home", "The Okonkwo Family", "House",
             "6212 SE Woodstock Blvd", "Portland", "97206", 2750, 4, 3,
             3, 2, 11, "Key safe - code 0721", "On site", "Dog",
             "None", "Labrador (Scout)", "Playroom always a challenge."),
            ("Cascade Legal - Office Floor", "Cascade Legal Group",
             "Office", "1200 SW 6th Ave, Floor 8", "Portland",
             "97204", 5600, 0, 4, 12, 1, 14, "Night fob", "Paid",
             "None", "Building alarm", "Confidential waste bins",
             "Server room - do not enter."),
            ("Doyle - Family Home", "Martha Doyle", "House",
             "4128 NE 22nd Ave", "Portland", "97212", 1800, 3, 2, 2, 2,
             8, "Client always home", "Street", "None", "None",
             "Elderly client - clear walkways", "Knock twice."),
            ("Sundial - Bookshop", "Sundial Bookshop", "Retail",
             "3555 SE Hawthorne Blvd", "Portland", "97214", 2200, 0, 1,
             4, 1, 6, "Key with owner", "Street", "None", "None",
             "Rare books shelf", "Dust carefully around stock."),
            ("Briggs - Apartment", "Tyler Briggs", "Apartment",
             "901 SW 18th Ave", "Portland", "97219", 850, 1, 1, 1, 1,
             8, "Gate code 55#", "Paid", "None", "None", "None",
             "Kitchen always needs extra time."),
            ("Lakeview HOA - Clubhouse", "Lakeview HOA", "Other",
             "4000 NE Halsey St", "Portland", "97213", 3000, 0, 3, 5, 1,
             12, "HOA key box", "On site", "None", "None",
             "Pool area - wet floors", "Gym equipment included."),
            ("Okafor - Family Home", "Grace Okafor", "House",
             "5510 SE Woodstock", "Portland", "97206", 1900, 3, 2, 2, 1,
             11, "Key safe - code 9931", "On site", "None", "None",
             "None", "Prefers Fridays."),
            ("Northbank Coworking - Main Floor", "Northbank Coworking",
             "Office", "220 NE Oregon St", "Portland", "97232", 6400, 0,
             6, 14, 1, 9, "24/7 fob", "Paid", "None", "None",
             "Standing desks - careful", "Kitchen twice daily."),
            ("Reyes - Family Home", "Paul & Nina Reyes", "House",
             "127 SE 28th Ave", "Portland", "97214", 1750, 3, 2, 2, 2,
             5, "Key safe - code 2207", "Street", "None", "None",
             "Photo wall in hall", "Dust carefully."),
            ("Hawthorne Auto - Shop", "Hawthorne Auto Care",
             "Warehouse", "4411 SE Hawthorne Blvd", "Portland",
             "97215", 3600, 0, 2, 4, 1, 7, "Shop key", "On site",
             "None", "None", "Grease, oil, solvents", "Heavy duty degreaser."),
            ("Park - Loft", "Jenna Park", "Apartment",
             "2330 N Williams Ave", "Portland", "97227", 1000, 1, 1, 2,
             1, 9, "Door code 1902", "Street", "None", "None", "None",
             "Polished concrete floors."),
            ("St Marks - Main Hall", "St. Marks Community Hall",
             "Other", "805 NE 8th Ave", "Portland", "97232", 4200, 0, 3,
             6, 1, 10, "Rev. Ford has keys", "On site", "None", "None",
             "Stackable chairs - lift properly", "Kitchen included."),
            ("Lombardi - Family Home", "Chris & Amy Lombardi", "House",
             "7230 SE 32nd Ave", "Portland", "97202", 2900, 4, 3, 3, 2,
             13, "Key safe - code 3344", "On site", "None", "None",
             "Wine cellar - stay out", "Wine cellar is strictly off limits."),
            ("Sharma - Townhouse", "Priya Sharma", "House",
             "1644 SE Bybee Blvd", "Portland", "97202", 1550, 2, 2.5, 2,
             3, 12, "Lockbox 88#", "Street", "None", "None", "None",
             "Happy to be a reference."),
            ("Baxter Insurance - Office", "Baxter Insurance", "Office",
             "520 SW Yamhill St, Suite 300", "Portland", "97205", 2800,
             0, 2, 8, 1, 13, "Night fob", "Paid", "None", "None",
             "None", "Carpet monthly."),
            ("Martinez - Apartment", "Leo Martinez", "Apartment",
             "3101 NE 15th Ave", "Portland", "97212", 780, 1, 1, 1, 1,
             8, "Key returned", "Street", "None", "None", "None",
             "Move-out clean completed."),
            ("Mohammed - New Home", "Aisha Mohammed", "House",
             "2910 NE 33rd Ave", "Portland", "97212", 1600, 3, 2, 2, 2,
             9, "Key safe - code 7788", "Street", "None", "None",
             "Moving boxes may still be around", "Fresh move-in."),
        ])

    # ------------------------------------------------------------ services
    SERVICES = _rows(
        ["name", "category", "description", "unit", "base_price",
         "est_hours", "materials", "frequency", "active"],
        [
            ("Standard House Clean", "Residential",
             "Kitchen, bathrooms, floors, dusting, bins", f"{cfg.area_unit}",
             185.00, 3.5, 4.00, "Fortnightly", "Yes"),
            ("Deep Clean", "Deep clean",
             "Everything in a standard clean plus inside oven, fridge, "
             "windows, skirting, doors", f"{cfg.area_unit}",
             320.00, 6.0, 8.00, "One-off", "Yes"),
            ("Move-In / Move-Out Clean", "Deep clean",
             "Empty property deep clean, inside cupboards, limescale "
             "treatment", f"{cfg.area_unit}", 380.00, 7.0, 10.00,
             "One-off", "Yes"),
            ("Office Cleaning", "Commercial",
             "Desks, kitchens, washrooms, floors, bins", f"{cfg.area_unit}",
             160.00, 3.0, 5.00, "Weekly", "Yes"),
            ("Cafe & Restaurant Clean", "Commercial",
             "FOH and BOH degrease, floors, washrooms", "visit",
             210.00, 4.0, 9.00, "Twice a week", "Yes"),
            ("Medical Clinic Clean", "Commercial",
             "Clinical standard, touch points, waste handling", "visit",
             240.00, 4.5, 12.00, "Weekly", "Yes"),
            ("Post-Construction Clean", "Specialist",
             "Dust removal, paint marks, glass, final polish", f"{cfg.area_unit}",
             450.00, 8.0, 15.00, "One-off", "Yes"),
            ("Carpet & Upholstery", "Specialist",
             "Hot water extraction, stains, deodorise", "room",
             65.00, 1.0, 6.00, "One-off", "Yes"),
            ("Window Cleaning (Interior)", "Add-on",
             "Inside glass, frames, sills", "item", 8.00, 0.15, 1.00,
             "Monthly", "Yes"),
            ("Oven Deep Clean", "Add-on",
             "Degrease oven, racks, trays, hood", "fixed", 45.00, 1.0,
             3.00, "One-off", "Yes"),
            ("Fridge Deep Clean", "Add-on",
             "Empty, degrease, sanitise, defrost", "fixed", 35.00, 0.75,
             2.00, "One-off", "Yes"),
            ("Laundry & Ironing", "Add-on",
             "Wash, dry, fold, iron", "hour", 35.00, 1.0, 1.00,
             "Weekly", "No"),
        ])

    # --------------------------------------------------------------- leads
    LEADS = _rows(
        ["name", "type", "contact", "email", "phone", "source",
         "service", "estimate", "status", "follow_up", "owner",
         "notes"],
        [
            ("Derek Mills", "Residential", "Derek Mills",
             "derek.mills@email.com", "(503) 555 3001", "Google",
             "Standard House Clean", 180.00, "Quoted", d(2),
             "Chris Dalton", "Wants fortnightly. Quote sent."),
            ("Fern & Fig Florist", "Commercial", "Nadia Rahal",
             "nadia@fernfig.com", "(503) 555 3002", "Instagram",
             "Office Cleaning", 420.00, "Contacted", d(-3),
             "Dana Whitfield", "Follow up overdue - wants weekly."),
            ("Harold Jenkins", "Residential", "Harold Jenkins",
             "h.jenkins@email.com", "(503) 555 3003", "Referral",
             "Deep Clean", 300.00, "New", d(1), "Chris Dalton",
             "Left voicemail Tuesday."),
            ("Summit Dental Care", "Commercial", "Ruth Adams",
             "radams@summitdental.com", "(503) 555 3004", "Referral",
             "Medical Clinic Clean", 250.00, "Quoted", d(4),
             "Dana Whitfield", "Competing with two other firms."),
            ("Aisha Mohammed", "Residential", "Aisha Mohammed",
             "aisha.m@email.com", "(503) 555 3005", "Facebook",
             "Move-In / Move-Out Clean", 390.00, "Booked", d(6),
             "Chris Dalton", "Moving in on the 20th."),
            ("Brian Teague", "Residential", "Brian Teague",
             "bteague@email.com", "(503) 555 3006", "Yelp",
             "Standard House Clean", 170.00, "Lost", d(-12),
             "Chris Dalton", "Went cheaper. Keep in touch."),
            ("Quill Coffee Roasters", "Commercial", "Ben Quill",
             "ben@quillroasters.com", "(503) 555 3007", "Walk-in",
             "Cafe & Restaurant Clean", 220.00, "Contacted", d(3),
             "Dana Whitfield", "Wants to see a cafe reference."),
            ("Melanie Frost", "Residential", "Melanie Frost",
             "mel.frost@email.com", "(503) 555 3008", "Referral",
             "Deep Clean", 310.00, "New", d(-1), "Chris Dalton",
             "Asked about fragrance-free."),
            ("Parkside Dental Studio", "Commercial", "Dr. Neil Gopal",
             "neil@parkside.dental", "(503) 555 3009", "Google",
             "Medical Clinic Clean", 260.00, "Followed up", d(5),
             "Dana Whitfield", "Second viewing booked."),
            ("Susan Yoon", "Residential", "Susan Yoon",
             "susan.yoon@email.com", "(503) 555 3010", "Referral",
             "Standard House Clean", 190.00, "Quoted", d(2),
             "Chris Dalton", "Needs a decision by Friday."),
        ])

    # ----------------------------------------------------------- checklists
    CHECKLISTS = _rows(
        ["service", "room_area", "step_no", "item", "required", "est_min",
         "kit", "standard"],
        [
            ("Standard House Clean", "Kitchen", 1, "Worktops and sink",
             "Yes", 10, "All-purpose, cloths", "No streaks, sink shining"),
            ("Standard House Clean", "Kitchen", 2,
             "Appliance exteriors", "Yes", 8, "Microfibre",
             "Fingerprints gone"),
            ("Standard House Clean", "Kitchen", 3, "Floor vacuum and mop",
             "Yes", 12, "Vacuum, mop", "Edges done, dry floor"),
            ("Standard House Clean", "Bathrooms", 4,
             "Toilet, basin, shower", "Yes", 15, "Bathroom cleaner",
             "Limescale free, fresh smell"),
            ("Standard House Clean", "Bathrooms", 5, "Mirror and glass",
             "Yes", 5, "Glass cleaner", "Streak free"),
            ("Standard House Clean", "Whole property", 6, "Dusting",
             "Yes", 20, "Duster, polish", "Surfaces clear"),
            ("Standard House Clean", "Whole property", 7, "Bins emptied",
             "Yes", 5, "Bin bags", "New liners in"),
            ("Standard House Clean", "Whole property", 8, "Floors vacuumed",
             "Yes", 25, "Vacuum", "Carpets raked one way"),
            ("Deep Clean", "Kitchen", 1, "Inside oven", "Yes", 25,
             "Oven degreaser", "Racks and trays spotless"),
            ("Deep Clean", "Kitchen", 2, "Inside fridge", "Yes", 20,
             "Fridge sanitiser", "Shelves out and clean"),
            ("Deep Clean", "Whole property", 3, "Skirting and doors",
             "Yes", 30, "All-purpose", "Marks removed"),
            ("Deep Clean", "Windows", 4, "Interior windows", "Yes", 40,
             "Glass kit", "Frames and sills too"),
            ("Deep Clean", "Whole property", 5, "Limescale treatment",
             "Yes", 20, "Limescale remover", "Taps like new"),
            ("Deep Clean", "Whole property", 6, "Light switches / handles",
             "Yes", 15, "Antibac", "All touch points"),
            ("Office Cleaning", "Office area", 1, "Desks wiped", "Yes",
             20, "Antibac", "Paper left in place"),
            ("Office Cleaning", "Communal areas", 2, "Kitchen and washrooms",
             "Yes", 25, "All-purpose, bathroom", "Stock checked"),
            ("Office Cleaning", "Whole property", 3, "Floors", "Yes", 30,
             "Vacuum, mop", "No cords disturbed"),
            ("Office Cleaning", "Whole property", 4, "Bins and recycling",
             "Yes", 10, "Bags", "Separated correctly"),
            ("Cafe & Restaurant Clean", "Kitchen", 1, "Degrease surfaces",
             "Yes", 25, "Degreaser", "No grease film"),
            ("Cafe & Restaurant Clean", "Kitchen", 2, "Floors (anti-slip)",
             "Yes", 20, "Floor degreaser", "Dry before opening"),
            ("Cafe & Restaurant Clean", "Whole property", 3,
             "Washrooms restocked", "Yes", 10, "Consumables",
             "Stock at par"),
            ("Cafe & Restaurant Clean", "Whole property", 4, "FOH polish",
             "Yes", 15, "Polish", "Tables and counter"),
            ("Medical Clinic Clean", "Whole property", 1,
             "Touch point sanitising", "Yes", 30, "Clinical wipes",
             "Logged on the sheet"),
            ("Medical Clinic Clean", "Whole property", 2,
             "Clinical waste handling", "Yes", 15, "Red bags",
             "Segregated correctly"),
        ])

    # ------------------------------------------------------------- supplies
    SUPPLIES = _rows(
        ["name", "category", "unit", "supplier", "cost_per_unit",
         "qty_on_hand", "reorder_level", "reorder_qty", "last_purchased",
         "notes"],
        [
            ("All-purpose cleaner 5L", "Chemicals", "bottle",
             "CleanSource", 12.50, 9, 4, 6, d(-18), "Workhorse product."),
            ("Bathroom descaler 5L", "Chemicals", "bottle",
             "CleanSource", 14.00, 5, 3, 6, d(-18), ""),
            ("Glass cleaner 5L", "Chemicals", "bottle", "CleanSource",
             11.00, 6, 3, 6, d(-18), ""),
            ("Oven degreaser 5L", "Chemicals", "bottle", "ProChem",
             18.50, 3, 3, 4, d(-30), "Runs hot in deep-clean season."),
            ("Floor degreaser 5L", "Chemicals", "bottle", "ProChem",
             16.00, 4, 2, 4, d(-30), ""),
            ("Antibac spray 5L", "Chemicals", "bottle", "ProChem",
             15.50, 7, 3, 6, d(-12), "Clinics use most of it."),
            ("Microfibre cloths (pack 50)", "Paper", "pack",
             "CleanSource", 22.00, 6, 3, 4, d(-25), "Colour coded."),
            ("Bin liners 90L (pack 200)", "Paper", "pack", "JanPack",
             18.00, 8, 4, 6, d(-15), ""),
            ("Toilet rolls (pack 48)", "Paper", "pack", "JanPack",
             28.00, 5, 3, 4, d(-15), "For commercial sites."),
            ("Paper hand towels (pack 12)", "Paper", "pack", "JanPack",
             32.00, 4, 2, 4, d(-15), ""),
            ("Nitrile gloves (box 100)", "PPE", "box", "SafeKit",
             9.50, 12, 6, 10, d(-40), ""),
            ("Dust masks (pack 20)", "PPE", "pack", "SafeKit", 8.00, 6,
             3, 6, d(-40), ""),
            ("Vacuum bags (pack 10)", "Equipment", "pack", "ProChem",
             14.00, 4, 2, 4, d(-60), "Fits the Numatics."),
            ("Mop heads (pack 5)", "Equipment", "pack", "ProChem",
             16.00, 3, 2, 4, d(-60), ""),
            ("Laundry powder 5kg", "Laundry", "box", "CleanSource",
             13.00, 3, 2, 4, d(-20), ""),
            ("Air freshener refill (pack 6)", "Chemicals", "pack",
             "JanPack", 21.00, 2, 2, 4, d(-15), "Reorder."),
        ])

    # ------------------------------------------------------------ equipment
    EQUIPMENT = _rows(
        ["name", "category", "serial", "purchase_date", "purchase_cost",
         "condition", "status", "last_service", "assigned_to", "location",
         "notes"],
        [
            ("Numatic Henry Xtra", "Vacuum", "NV-2201",
             dt.date(2021, 4, 2), 320.00, "Good", "In service",
             d(-20), "Marisol Reyes", "Van 1", "Bag changed weekly."),
            ("Miele Complete C3", "Vacuum", "MV-4410",
             dt.date(2022, 8, 18), 410.00, "Excellent", "In service",
             d(-35), "Tasha Kim", "Van 1", ""),
            ("Karcher SC3 Steamer", "Steamer", "KS-1102",
             dt.date(2023, 2, 10), 290.00, "Good", "In service",
             d(-10), "Priya Nair", "Store room", "Descaled last service."),
            ("Vax Air Stretch", "Vacuum", "VX-8820",
             dt.date(2020, 6, 25), 180.00, "Fair", "In for repair",
             d(-95), "Jordan Blake", "Repair shop",
             "Motor whining - booked in."),
            ("Numatic Floor Polisher", "Floor machine", "NF-6640",
             dt.date(2022, 1, 30), 890.00, "Good", "In service",
             d(-25), "Priya Nair", "Store room", "Pad driver replaced."),
            ("Karcher K4 Washer", "Pressure washer", "KW-3307",
             dt.date(2023, 5, 12), 350.00, "Excellent", "In service",
             d(-5), "Sam Okafor", "Van 2", ""),
            ("Ford Transit Connect", "Vehicle", "VIN-FTC-114",
             dt.date(2021, 9, 1), 18500.00, "Good", "In service",
             d(-15), "Sam Okafor", "Depot", "MOT due next quarter."),
            ("Ford Transit Custom", "Vehicle", "VIN-FTC-229",
             dt.date(2023, 3, 20), 24000.00, "Excellent", "In service",
             d(-8), "Marisol Reyes", "Depot", ""),
            ("Pressure sprayer 8L", "Tool", "TL-0091",
             dt.date(2023, 7, 7), 65.00, "Good", "In service",
             d(-50), "Tasha Kim", "Store room", ""),
            ("Safety step ladder", "Safety", "SF-4412",
             dt.date(2022, 11, 11), 120.00, "Good", "In service",
             d(-70), "Team", "Van 1", "Annual inspection logged."),
        ])

    # ------------------------------------------------------ quotes & lines
    quote_rows = [
        ("Q-1010", d(-24), "Whitfield Family", "Whitfield - Family Home",
         "Sarah Whitfield", "sarah.w@email.com", "(503) 555 2001",
         "Standard House Clean", "Fortnightly", 0.05, "Accepted",
         "Dana Whitfield", "Yes", "Signed for a year of fortnightly cleans."),
        ("Q-1011", d(-23), "Derek Mills", "Mills - Rental Property",
         "Derek Mills", "derek.mills@email.com", "(503) 555 3001",
         "Standard House Clean", "Fortnightly", 0, "Sent",
         "Chris Dalton", "No", "Asked for fortnightly pricing."),
        ("Q-1012", d(-21), "Summit Dental Care", "Summit - Clinic",
         "Ruth Adams", "radams@summitdental.com", "(503) 555 3004",
         "Medical Clinic Clean", "Weekly", 0, "Sent",
         "Dana Whitfield", "No", "Waiting on their board."),
        ("Q-1013", d(-19), "Elena Vasquez", "Vasquez - Bungalow",
         "Elena Vasquez", "elena.v@email.com", "(503) 555 2007",
         "Deep Clean", "One-off", 0, "Accepted", "Chris Dalton", "Yes",
         "Fragrance-free products - noted."),
        ("Q-1014", d(-17), "Quill Coffee Roasters", "Quill - Roastery Cafe",
         "Ben Quill", "ben@quillroasters.com", "(503) 555 3007",
         "Cafe & Restaurant Clean", "Twice a week", 0.03, "Followed up",
         "Dana Whitfield", "No", "Wants a cafe reference."),
        ("Q-1015", d(-15), "Jenna Park", "Park - Loft", "Jenna Park",
         "jenna.park@email.com", "(503) 555 2019", "Standard House Clean",
         "Monthly", 0, "Accepted", "Chris Dalton", "Yes", ""),
        ("Q-1016", d(-12), "Leo Martinez", "Martinez - Apartment",
         "Leo Martinez", "leo.m@email.com", "(503) 555 2024",
         "Move-In / Move-Out Clean", "One-off", 0, "Accepted",
         "Chris Dalton", "Yes", "Move-out at the old place."),
        ("Q-1017", d(-10), "Fern & Fig Florist", "Fern & Fig - Shop",
         "Nadia Rahal", "nadia@fernfig.com", "(503) 555 3002",
         "Office Cleaning", "Weekly", 0, "Sent", "Dana Whitfield", "No",
         "Follow-up overdue."),
        ("Q-1018", d(-8), "Susan Yoon", "Yoon - Family Home", "Susan Yoon",
         "susan.yoon@email.com", "(503) 555 3010", "Standard House Clean",
         "Weekly", 0.05, "Sent", "Chris Dalton", "No", "Deciding Friday."),
        ("Q-1019", d(-6), "Parkside Dental Studio", "Parkside - Clinic",
         "Dr. Neil Gopal", "neil@parkside.dental", "(503) 555 3009",
         "Medical Clinic Clean", "Weekly", 0, "Followed up",
         "Dana Whitfield", "No", "Second viewing booked."),
        ("Q-1020", d(-5), "Melanie Frost", "Frost - Family Home",
         "Melanie Frost", "mel.frost@email.com", "(503) 555 3008",
         "Deep Clean", "One-off", 0, "Sent", "Chris Dalton", "No",
         "Fragrance-free asked."),
        ("Q-1021", d(-3), "Harold Jenkins", "Jenkins - Bungalow",
         "Harold Jenkins", "h.jenkins@email.com", "(503) 555 3003",
         "Deep Clean", "One-off", 0, "Sent", "Chris Dalton", "No",
         "Voicemail left."),
        ("Q-1022", d(-2), "Aisha Mohammed", "Mohammed - New Home",
         "Aisha Mohammed", "aisha.m@email.com", "(503) 555 3005",
         "Move-In / Move-Out Clean", "One-off", 0, "Accepted",
         "Chris Dalton", "Yes", "Moving day 20th."),
        ("Q-1023", d(-1), "St. Marks Community Hall", "St Marks - Kitchen",
         "Rev. Alan Ford", "alan@stmarks.org", "(503) 555 2020",
         "Deep Clean", "One-off", 0, "Draft", "Dana Whitfield", "No",
         "Kitchen only - draft."),
    ]
    QUOTES = _rows(
        ["quote_number", "date", "client", "property", "contact", "email",
         "phone", "service", "frequency", "discount_pct", "status",
         "owner", "job_created", "notes"],
        quote_rows)

    ql_rows = []
    ql_no = 1

    def ql(quote, area, service, desc, qty, unit, price, hours, mats):
        nonlocal ql_no
        ql_rows.append((quote, ql_no, area, service, desc, qty, unit,
                        price, hours, mats))
        ql_no += 1

    for q, _dt_, client, prop, *_rest in quote_rows:
        ql_no = 1
        service = _rest[3]
        freq = _rest[4]
        if service == "Standard House Clean":
            ql(q, "Whole property", service, "Standard clean per checklist",
               1, "visit", 165.00, 3.0, 4.00)
            if client in ("Whitfield Family", "Nguyen Household"):
                ql(q, "Kitchen", "Oven Deep Clean", "Oven degrease",
                   1, "fixed", 45.00, 1.0, 3.00)
        elif service == "Deep Clean":
            ql(q, "Whole property", service, "Full deep clean per checklist",
               1, "visit", 320.00, 6.0, 8.00)
            ql(q, "Windows", "Window Cleaning (Interior)",
               "Interior windows and sills", 12, "item", 8.00, 1.5, 1.50)
        elif service == "Move-In / Move-Out Clean":
            ql(q, "Whole property", service,
               "Empty property move clean", 1, "visit", 380.00, 7.0,
               10.00)
        elif service == "Medical Clinic Clean":
            ql(q, "Whole property", service,
               "Weekly clinical clean", 1, "visit", 240.00, 4.5, 12.00)
        elif service == "Cafe & Restaurant Clean":
            ql(q, "Kitchen", service, "Degrease and floors",
               1, "visit", 130.00, 2.5, 6.00)
            ql(q, "Whole property", service,
               "FOH, washrooms, bins", 1, "visit", 90.00, 1.5, 3.00)
        else:
            ql(q, "Whole property", service, "Service per quote",
               1, "visit", 180.00, 3.5, 4.00)
        if freq in ("Weekly", "Fortnightly", "Twice a week"):
            pass  # frequency discount applied at quote level

    QUOTE_LINES = _rows(
        ["quote_ref", "line_no", "room_area", "service", "description",
         "qty", "unit", "unit_price", "hours", "materials"],
        ql_rows)

    # ------------------------------------------------------- jobs & tasks
    slots = [
        ("Whitfield Family", "Whitfield - Family Home",
         "Standard House Clean", "Fortnightly", 165.00, 3.5, 2,
         "Marisol Reyes", 7),
        ("Nguyen Household", "Nguyen - Townhouse", "Standard House Clean",
         "Weekly", 145.00, 3.0, 2, "Tasha Kim", 1),
        ("Harborview Dental", "Harborview Dental - Clinic",
         "Medical Clinic Clean", "Weekly", 240.00, 4.5, 2,
         "Marisol Reyes", 2),
        ("Bramble & Vine Cafe", "Bramble & Vine - Cafe",
         "Cafe & Restaurant Clean", "Twice a week", 110.00, 2.0, 1,
         "Jordan Blake", 3),
        ("Colin Mercer", "Mercer - Condo", "Standard House Clean",
         "Monthly", 150.00, 3.0, 1, "Lena Ford", 10),
        ("Riverside Yoga Studio", "Riverside Yoga - Studio",
         "Office Cleaning", "Weekly", 170.00, 3.5, 2, "Priya Nair", 4),
        ("Elena Vasquez", "Vasquez - Bungalow", "Standard House Clean",
         "Every 3 weeks", 155.00, 3.0, 2, "Tasha Kim", 9),
        ("Fairmount Apartments", "Fairmount - Communal Areas",
         "Office Cleaning", "Weekly", 220.00, 4.5, 3, "Jordan Blake", 5),
        ("The Okonkwo Family", "Okonkwo - Family Home",
         "Standard House Clean", "Weekly", 185.00, 4.0, 2,
         "Marisol Reyes", 1),
        ("Cascade Legal Group", "Cascade Legal - Office Floor",
         "Office Cleaning", "Weekly", 260.00, 5.0, 3, "Priya Nair", 6),
        ("Martha Doyle", "Doyle - Family Home", "Standard House Clean",
         "Fortnightly", 160.00, 3.5, 2, "Lena Ford", 3),
        ("Sundial Bookshop", "Sundial - Bookshop", "Office Cleaning",
         "Weekly", 165.00, 3.5, 2, "Jordan Blake", 2),
        ("The Okonkwo Family", "Okonkwo - Family Home", "Deep Clean",
         "One-off", 330.00, 6.5, 2, "Tasha Kim", 8),
        ("Lakeview HOA", "Lakeview HOA - Clubhouse", "Office Cleaning",
         "Weekly", 195.00, 4.0, 2, "Priya Nair", 5),
        ("Grace Okafor", "Okafor - Family Home", "Standard House Clean",
         "Every 3 weeks", 155.00, 3.0, 1, "Lena Ford", 12),
        ("Northbank Coworking", "Northbank Coworking - Main Floor",
         "Office Cleaning", "Twice a week", 175.00, 3.5, 2,
         "Priya Nair", 1),
        ("Paul & Nina Reyes", "Reyes - Family Home",
         "Standard House Clean", "Weekly", 165.00, 3.5, 2, "Tasha Kim", 4),
        ("Baxter Insurance", "Baxter Insurance - Office",
         "Office Cleaning", "Weekly", 185.00, 3.5, 2, "Lena Ford", 6),
    ]

    jobs = []
    jnum = 2401
    # 6 past weeks + current week + 2 future weeks
    for slot_i, (client, prop, service, freq, price, hours, cleaners,
                 lead, day_of_week) in enumerate(slots):
        step = 14 if freq == "Fortnightly" else (
            7 if freq in ("Weekly", "One-off") else 21)
        if freq == "Twice a week":
            step = 3 or 3
        weeks_back = [-42, -35, -28, -21, -14, -7, 0, 7, 14]
        if freq == "Twice a week":
            weeks_back = [-42, -39, -35, -32, -28, -25, -21, -18,
                          -14, -11, -7, -4, 0, 3, 7, 10, 14]
        if freq == "Fortnightly":
            weeks_back = [-42, -28, -14, 0, 14]
        if freq == "Every 3 weeks":
            weeks_back = [-42, -21, 0, 21][:4]
        if freq == "Monthly":
            weeks_back = [-42, -14, 14]
        if freq == "One-off":
            weeks_back = [-12]
        for wb in weeks_back:
            base = t + dt.timedelta(days=wb)
            shift = (day_of_week - base.weekday()) % 7
            jdate = base + dt.timedelta(days=shift)
            if jdate > t + dt.timedelta(days=21):
                continue
            if jdate < t - dt.timedelta(days=46):
                continue
            if jdate <= t - dt.timedelta(days=1):
                status = "Invoiced" if (slot_i + wb) % 3 else "Completed"
            elif jdate == t:
                status = "Confirmed"
            else:
                status = "Booked" if (slot_i + wb) % 4 else "Confirmed"
            jobs.append((f"J-{jnum}", jdate, client, prop, service, freq,
                         price, hours, cleaners, lead, status))
            jnum += 1

    # a few story rows: cancelled, no access, deep clean, move-out
    jobs.append(("J-2501", t - dt.timedelta(days=9), "Hawthorne Auto Care",
                 "Hawthorne Auto - Shop", "Deep Clean", "One-off",
                 420.00, 7.5, 3, "Sam Okafor", "Completed"))
    jobs.append(("J-2502", t - dt.timedelta(days=6), "Leo Martinez",
                 "Martinez - Apartment", "Move-In / Move-Out Clean",
                 "One-off", 380.00, 7.0, 2, "Tasha Kim", "Invoiced"))
    jobs.append(("J-2503", t - dt.timedelta(days=4), "Martha Doyle",
                 "Doyle - Family Home", "Standard House Clean",
                 "Fortnightly", 160.00, 3.5, 2, "Lena Ford", "No access"))
    jobs.append(("J-2504", t + dt.timedelta(days=5), "Aisha Mohammed",
                 "Mohammed - New Home", "Move-In / Move-Out Clean",
                 "One-off", 390.00, 7.5, 3, "Marisol Reyes", "Booked"))
    jobs.append(("J-2505", t - dt.timedelta(days=2), "Bramble & Vine Cafe",
                 "Bramble & Vine - Cafe", "Cafe & Restaurant Clean",
                 "Twice a week", 110.00, 2.0, 1, "Jordan Blake",
                 "Cancelled"))

    jobs.sort(key=lambda x: (x[1], x[0]))
    JOBS = _rows(
        ["job_number", "date", "client", "property", "service", "frequency",
         "price", "hours", "cleaners", "crew_lead", "status"],
        jobs)

    job_by_num = {j["job_number"]: j for j in JOBS}

    # job tasks: tasks for jobs in the last 3 weeks and the deep cleans
    task_defs = {
        "Standard House Clean": [
            ("Kitchen", "Worktops, sink, appliance fronts"),
            ("Bathrooms", "Toilet, basin, shower, mirror"),
            ("Whole property", "Dusting all surfaces"),
            ("Whole property", "Vacuum throughout"),
            ("Whole property", "Mop hard floors"),
            ("Whole property", "Bins emptied and relined"),
        ],
        "Deep Clean": [
            ("Kitchen", "Inside oven and hood"),
            ("Kitchen", "Inside fridge"),
            ("Windows", "Interior windows and sills"),
            ("Whole property", "Skirting, doors, switches"),
            ("Bathrooms", "Limescale treatment"),
            ("Whole property", "Final vacuum and mop"),
        ],
        "Move-In / Move-Out Clean": [
            ("Kitchen", "Inside all cupboards"),
            ("Kitchen", "Oven, fridge, dishwasher filter"),
            ("Bathrooms", "Full descale"),
            ("Whole property", "Windows interior"),
            ("Whole property", "Floors throughout"),
        ],
        "Medical Clinic Clean": [
            ("Whole property", "Touch point sanitise"),
            ("Whole property", "Clinical waste handling"),
            ("Bathrooms", "Washrooms clinical standard"),
            ("Office area", "Reception and desks"),
            ("Whole property", "Floors vacuum and mop"),
        ],
        "Cafe & Restaurant Clean": [
            ("Kitchen", "Degrease surfaces and splashbacks"),
            ("Kitchen", "Anti-slip floor treatment"),
            ("Whole property", "Washrooms restocked"),
            ("Whole property", "FOH tables and counter"),
        ],
        "Office Cleaning": [
            ("Office area", "Desks wiped"),
            ("Communal areas", "Kitchen and washrooms"),
            ("Whole property", "Floors vacuum and mop"),
            ("Whole property", "Bins and recycling"),
        ],
    }
    task_rows = []
    tnum = 1
    for j in JOBS:
        if j["date"] < t - dt.timedelta(days=22) and \
                j["service"] != "Deep Clean":
            continue
        defs = task_defs.get(j["service"], task_defs["Standard House Clean"])
        for step_no, (area, task) in enumerate(defs, start=1):
            done = ("Yes" if j["date"] <= t and j["status"] in (
                "Completed", "Invoiced") else "No")
            done_by = j["crew_lead"] if done == "Yes" else None
            done_at = j["date"] if done == "Yes" else None
            task_rows.append((j["job_number"], step_no, area, task,
                              j["crew_lead"], 15, done, done_by, done_at,
                              None))
            tnum += 1
    JOB_TASKS = _rows(
        ["job_ref", "step_no", "room_area", "task", "assigned_to",
         "est_min", "done", "done_by", "done_at", "notes"],
        task_rows)

    # ------------------------------------------------------------ timesheets
    ts_rows = []
    team_pool = ["Tasha Kim", "Jordan Blake", "Priya Nair", "Lena Ford",
                 "Marisol Reyes", "Sam Okafor"]
    for i, j in enumerate(JOBS):
        if j["status"] in ("Cancelled", "No access"):
            continue
        if j["date"] > t + dt.timedelta(days=7):
            continue
        lead = j["crew_lead"]
        lead_hours = round(j["hours"] * 0.6, 2)
        helper = team_pool[(i + 1) % len(team_pool)]
        if helper == lead:
            helper = team_pool[(i + 2) % len(team_pool)]
        start_hour = 8 + (i % 3)
        ts_rows.append((j["date"], lead, j["job_number"],
                        dt.time(start_hour, 0),
                        dt.time(start_hour + int(lead_hours) + 1,
                                int((lead_hours % 1) * 60) or 30),
                        30, 0, "Yes", "Lead hours"))
        if j["cleaners"] > 1:
            helper_hours = round(j["hours"] - lead_hours, 2)
            ts_rows.append((j["date"], helper, j["job_number"],
                            dt.time(start_hour, 0),
                            dt.time(start_hour + int(helper_hours),
                                    int((helper_hours % 1) * 60) or 0),
                            30, 0, "Yes", ""))
    # a couple of non-job entries
    ts_rows.append((t - dt.timedelta(days=3), "Lena Ford", None,
                    dt.time(9, 0), dt.time(12, 0), 30, 0, "Yes",
                    "In-house training"))
    ts_rows.append((t - dt.timedelta(days=3), "Jordan Blake", None,
                    dt.time(9, 0), dt.time(12, 0), 30, 1.5, "Yes",
                    "Training + overtime cover"))
    TIMESHEETS = _rows(
        ["date", "employee", "job_ref", "start", "end", "break_min",
         "overtime", "approved", "notes"],
        ts_rows)

    # ---------------------------------------------------------- job costing
    jc_rows = []
    for j in JOBS:
        if j["status"] in ("Completed", "Invoiced") and \
                j["date"] <= t - dt.timedelta(days=1):
            other = 0.0
            if j["service"] == "Deep Clean":
                other = 12.50
            elif j["service"] == "Move-In / Move-Out Clean":
                other = 18.00
            jc_rows.append((j["job_number"], other))
    JOB_COSTING = _rows(["job_ref", "other"], jc_rows)

    # ----------------------------------------------- invoices & payments
    inv_rows = []
    line_rows = []
    pay_rows = []
    inum = 2401
    lnum_global = 1
    pnum = 1
    for i, j in enumerate(JOBS):
        if j["status"] != "Invoiced":
            continue
        inv_date = j["date"] + dt.timedelta(days=1)
        inv_num = f"I-{inum}"
        inum += 1
        inv_rows.append((inv_num, inv_date, j["client"], j["property"],
                         j["job_number"], None, ""))
        # split: main service line (+ occasional add-on)
        if j["service"] == "Standard House Clean" and i % 3 == 0:
            line_rows.append((inv_num, 1, j["date"], j["service"] +
                              " - visit", j["service"], 1,
                              round(j["price"] - 45.0, 2)))
            line_rows.append((inv_num, 2, j["date"],
                              "Oven deep clean", "Oven Deep Clean", 1,
                              45.00))
        elif j["service"] == "Deep Clean":
            line_rows.append((inv_num, 1, j["date"],
                              "Deep clean per checklist", j["service"],
                              1, round(j["price"] - 96.0, 2)))
            line_rows.append((inv_num, 2, j["date"],
                              "Interior windows x12",
                              "Window Cleaning (Interior)", 12, 8.00))
        else:
            line_rows.append((inv_num, 1, j["date"], j["service"] +
                              " - visit", j["service"], 1, j["price"]))
        # payments: most paid in full, some part, some open
        age = (t - inv_date).days
        if i % 7 == 3:
            continue  # unpaid - recent
        amount = j["price"]
        if i % 5 == 1:
            amount = round(j["price"] * 0.5, 2)  # part paid
        pay_rows.append((inv_date + dt.timedelta(days=min(age, 10)),
                         inv_num, j["client"], amount,
                         ["Bank transfer", "Card", "Bank transfer",
                          "Online"][i % 4],
                         f"REF-{inum}{i}", ""))
    INVOICES = _rows(
        ["invoice_number", "date", "client", "property", "job_ref",
         "quote_ref", "notes"], inv_rows)
    INVOICE_LINES = _rows(
        ["invoice_ref", "line_no", "date", "description", "service",
         "qty", "unit_price"], line_rows)
    PAYMENTS = _rows(
        ["date", "invoice_ref", "client", "amount", "method", "reference",
         "notes"], pay_rows)

    # -------------------------------------------------------- supply usage
    supply_names = [s["name"] for s in SUPPLIES]
    su_rows = []
    su_count = 0
    for j in JOBS:
        if j["status"] in ("Cancelled", "No access") or j["date"] > t:
            continue
        if su_count >= 42:
            break
        for k in range(2):
            name = supply_names[(su_count + k) % len(supply_names)]
            qty = 0.25 if "5L" in name else 1
            su_rows.append((j["date"], j["job_number"], name, qty,
                            j["crew_lead"], None))
        su_count += 1
    SUPPLY_USAGE = _rows(
        ["date", "job_ref", "supply", "qty", "employee", "notes"],
        su_rows)

    # ----------------------------------------------------------- expenses
    exp_rows = []
    for months_back in range(6, -1, -1):
        mdate = dt.date(t.year, t.month, 1) - \
            dt.timedelta(days=0)
        # first of month, months_back ago
        y, m = t.year, t.month - months_back
        while m < 1:
            m += 12
            y -= 1
        first = dt.date(y, m, 1)
        exp_rows.append((first + dt.timedelta(days=2), "Rent",
                         "Riverstone Properties", "Office / store rent",
                         950.00, "Bank transfer", None, "Yes", "Yes"))
        exp_rows.append((first + dt.timedelta(days=5), "Utilities",
                         "Portland General Electric", "Electricity",
                         210.00 + (months_back % 3) * 18, "Direct debit",
                         None, "Yes", "Yes"))
        exp_rows.append((first + dt.timedelta(days=7), "Insurance",
                         "Hartfield Commercial", "Liability insurance",
                         145.00, "Direct debit", None, "Yes", "Yes"))
        exp_rows.append((first + dt.timedelta(days=10), "Supplies",
                         "CleanSource", "Monthly stock order",
                         320.00 + (months_back % 2) * 45, "Card", None,
                         "Yes", "Yes"))
        exp_rows.append((first + dt.timedelta(days=12), "Fuel",
                         "Shell", "Van fuel", 180.00 + (months_back % 4) * 22,
                         "Card", None, "Yes", "No"))
        exp_rows.append((first + dt.timedelta(days=15), "Software",
                         "Jobber", "Scheduling software", 49.00,
                         "Card", None, "Yes", "Yes"))
        exp_rows.append((first + dt.timedelta(days=18), "Marketing",
                         "Google Ads", "Local search ads",
                         220.00 if months_back % 2 else 120.00, "Card",
                         None, "Yes", "No"))
    # one-offs
    exp_rows.append((t - dt.timedelta(days=26), "Equipment",
                     "ProChem", "Replacement mop heads and bags",
                     86.50, "Card", None, "Yes", "No"))
    exp_rows.append((t - dt.timedelta(days=14), "Repairs",
                     "VacFix", "Vax vacuum repair (motor)", 95.00,
                     "Card", "J-2501", "Yes", "No"))
    exp_rows.append((t - dt.timedelta(days=11), "Training",
                     "SafeKit", "First aid refresher (2 staff)", 180.00,
                     "Bank transfer", None, "Yes", "No"))
    exp_rows.append((t - dt.timedelta(days=5), "Fees",
                     "Square", "Card processing fees", 62.30, "Online",
                     None, "Yes", "Yes"))
    EXPENSES = _rows(
        ["date", "category", "payee", "description", "amount", "method",
         "job_ref", "receipt", "recurring"], exp_rows)

    # ------------------------------------------------------------- mileage
    ml_rows = []
    mnum = 1
    for j in JOBS[::3][:26]:
        if j["date"] > t + dt.timedelta(days=10):
            continue
        dist = 6 + (mnum * 3) % 17
        ml_rows.append((j["date"], j["crew_lead"], j["job_number"],
                        j["client"], "Job travel", 41200 + mnum * 23,
                        41200 + mnum * 23 + dist, None))
        mnum += 1
    ml_rows.append((t - dt.timedelta(days=20), "Sam Okafor", None,
                    None, "Supply run", 41180, 41192, None))
    ml_rows.append((t - dt.timedelta(days=9), "Dana Whitfield", None,
                    "Summit Dental Care", "Estimate visit", 41310,
                    41319, None))
    MILEAGE = _rows(
        ["date", "employee", "job_ref", "client", "purpose",
         "start_odometer", "end_odometer", "notes"], ml_rows)

    # ---------------------------------------------------------- complaints
    COMPLAINTS = _rows(
        ["date", "client", "job_ref", "category", "severity",
         "description", "owner", "status", "action", "resolved_date",
         "refund", "notes"],
        [
            (t - dt.timedelta(days=28), "Martha Doyle", "J-2408", "Quality",
             "Medium", "Bathroom limescale missed on first pass",
             "Marisol Reyes", "Closed",
             "Re-cleaned next morning, no charge", t - dt.timedelta(days=27),
             0.00, "Turned into a positive - she referred a friend."),
            (t - dt.timedelta(days=21), "Bramble & Vine Cafe", None,
             "Punctuality", "High", "Crew arrived 25 minutes late",
             "Dana Whitfield", "Closed",
             "Van issue - apology and 10% off that week",
             t - dt.timedelta(days=20), 22.00, "Traffic - leave earlier."),
            (t - dt.timedelta(days=16), "Hawthorne Auto Care", "J-2501",
             "Quality", "Low", "Degrease not thorough near the lifts",
             "Sam Okafor", "Closed", "Returned same week",
             t - dt.timedelta(days=14), 0.00, ""),
            (t - dt.timedelta(days=9), "Colin Mercer", None, "Access",
             "Low", "Cleaner could not find the key fob", "Chris Dalton",
             "Resolved", "Concierge protocol updated",
             t - dt.timedelta(days=8), 0.00, ""),
            (t - dt.timedelta(days=3), "The Okonkwo Family", None,
             "Damage", "High", "Vase broken in the living room",
             "Dana Whitfield", "Investigating",
             "Replacement quoted at $60 - awaiting client", None, 0.00,
             "Photographs taken."),
            (t - dt.timedelta(days=1), "Riverside Yoga Studio", None,
             "Communication", "Medium",
             "Schedule change not passed to the instructor",
             "Chris Dalton", "Open", "", None, 0.00, ""),
        ])

    # -------------------------------------------------------------- safety
    SAFETY = _rows(
        ["date", "type", "topic", "area", "risk_level", "finding",
         "action", "owner", "due_date", "status", "closed_date",
         "attendees", "notes"],
        [
            (t - dt.timedelta(days=40), "Toolbox talk",
             "Chemical handling and COSHH", "Store room", "Medium",
             "Two bottles unlabelled", "Re-labelled and refresher given",
             "Dana Whitfield", t - dt.timedelta(days=35), "Done",
             t - dt.timedelta(days=36),
             "Marisol, Tasha, Jordan, Priya", ""),
            (t - dt.timedelta(days=30), "Inspection",
             "Van first aid kits", "Van 1 & 2", "Low",
             "Van 2 kit short of dressings", "Restocked",
             "Sam Okafor", t - dt.timedelta(days=28), "Done",
             t - dt.timedelta(days=29), "", ""),
            (t - dt.timedelta(days=22), "Training",
             "Working at heights", "All sites", "Medium",
             "Step ladder technique reviewed", "Signed attendance sheet",
             "Dana Whitfield", t - dt.timedelta(days=20), "Done",
             t - dt.timedelta(days=20), "All crew", ""),
            (t - dt.timedelta(days=15), "Risk assessment",
             "Wet floor procedures at the cafe", "Bramble & Vine",
             "High", "Anti-slip mats needed at the sink",
             "Mats purchased and placed", "Marisol Reyes",
             t - dt.timedelta(days=12), "Done", t - dt.timedelta(days=13),
             "", ""),
            (t - dt.timedelta(days=10), "Equipment check",
             "Steamer descaling and seals", "Store room", "Low",
             "Seal worn on the Karcher", "Seal kit ordered",
             "Priya Nair", t - dt.timedelta(days=5), "Done",
             t - dt.timedelta(days=6), "", ""),
            (t - dt.timedelta(days=7), "Toolbox talk",
             "Lone working policy", "All sites", "Medium",
             "Check-in times not always kept",
             "New check-in schedule started", "Dana Whitfield",
             t - dt.timedelta(days=2), "Done", t - dt.timedelta(days=3),
             "All crew", ""),
            (t - dt.timedelta(days=4), "Inspection",
             "PPE stock and condition", "Store room", "Low",
             "Gloves running low (again)",
             "Standing monthly order added", "Chris Dalton",
             t + dt.timedelta(days=2), "In progress", None, "", ""),
            (t - dt.timedelta(days=2), "Policy review",
             "Clinical waste at the dental clinic", "Harborview Dental",
             "High", "Policy refresh needed after staff change",
             "Refresh with the clinic manager", "Dana Whitfield",
             t + dt.timedelta(days=5), "Open", None,
             "Marisol, Tasha", ""),
        ])

    # ----------------------------------------------------------- incidents
    INCIDENTS = _rows(
        ["date", "time", "type", "employee", "client", "job_ref",
         "location", "severity", "description", "action", "reported_to",
         "reported_date", "status", "notes"],
        [
            (t - dt.timedelta(days=34), dt.time(10, 30), "Near miss",
             "Jordan Blake", "Fairmount Apartments", None,
             "Stairwell B", "Low",
             "Slipped on a wet step but held the rail",
             "Wet floor signs placed", "Marisol Reyes",
             t - dt.timedelta(days=34), "Closed",
             "Signs now in both vans."),
            (t - dt.timedelta(days=19), dt.time(14, 15), "Property damage",
             "Tasha Kim", "The Okonkwo Family", None,
             "Living room", "Medium", "Vase knocked while dusting",
             "Photographed, client informed same day", "Dana Whitfield",
             t - dt.timedelta(days=19), "Under review",
             "See the complaints tab."),
            (t - dt.timedelta(days=11), dt.time(9, 5), "Injury",
             "Priya Nair", "Cascade Legal Group", None,
             "8th floor kitchen", "Low",
             "Minor burn from the coffee machine while cleaning",
             "Cold water, first aid kit, rest of shift reassigned",
             "Dana Whitfield", t - dt.timedelta(days=11), "Closed",
             "RIDDOR not required."),
            (t - dt.timedelta(days=3), dt.time(16, 40), "Vehicle",
             "Sam Okafor", None, None, "SE Division St", "Low",
             "Van 2 mirror clipped a bollard in traffic",
             "Photos, no other vehicle involved", "Dana Whitfield",
             t - dt.timedelta(days=3), "Open",
             "Small scuff - monitor."),
        ])

    _ = (ql_no, lnum_global, pnum, tnum)  # quiet the unused counters
