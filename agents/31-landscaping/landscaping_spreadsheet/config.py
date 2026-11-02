"""Everything a landscaping business might want to change.

No price, rate, status, threshold or disclaimer is written into a
formula anywhere else in this package. A two-man mowing round in
Georgia and a six-crew design-and-build firm in Surrey are the same
workbook with different numbers on the Settings tab.

Nothing in here is a `Config` attribute unless it is a field on the
dataclass. The module level constants - the status sets, the lists,
the notes - are imported directly.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------

PRODUCT_NAME = "Ultimate Landscaping & Lawn Care Business Manager"
PRODUCT_SHORT = "Landscaping Business Manager"
PRODUCT_SUBTITLE = ("Customers, properties, quotes, recurring routes, "
                    "crews, equipment and profit by job")
LISTING_TITLE = ("Landscaping Business Spreadsheet | Lawn Care CRM, Quote "
                 "Calculator, Route Planner, Crew Scheduling, Invoices & "
                 "Job Profit Tracker")

VERSION = "1.0.0"
AUTHOR = "Novality Store"
PASSWORD = "premium"

#: how many rows a dashboard list shows before it stops
MAX_ROWS_SHOWN = 10


# ---------------------------------------------------------------------------
# the honest notes - the validator checks these actually appear
# ---------------------------------------------------------------------------

HONESTY_NOTE = (
    "This is a workbook, not an app. It does not sync with QuickBooks, "
    "Xero, Jobber, Yardbook or any payroll service, and it cannot take "
    "a card payment. You enter what happened and the formulas do the "
    "arithmetic."
)

ROUTE_NOTE = (
    "The route planner puts your stops in the order YOU give them. It "
    "is for organising a day on paper - it is not GPS navigation and it "
    "does not optimise a route. The drive times are your own estimates, "
    "not live traffic."
)

PAYROLL_NOTE = (
    "Timesheets work out gross labour cost so you can price a job "
    "properly. They are not a payroll filing: tax, national insurance, "
    "workers' compensation and overtime law vary by state and country. "
    "Give these totals to whoever runs your payroll."
)

WEATHER_NOTE = (
    "Rain days are something you record, not something the workbook "
    "knows. There is no weather feed. Mark a job rained off and the "
    "schedule tells you what has to be caught up."
)

PHOTO_NOTE = (
    "Before-and-after photos are stored as links. A spreadsheet cannot "
    "hold hundreds of site photographs without becoming unopenable, so "
    "put them in your phone's cloud folder and paste the share link."
)

PRIVACY_NOTE = (
    "This file holds customer addresses, gate codes and alarm "
    "information. Keep it somewhere access-controlled and encrypted, "
    "never on a shared crew tablet, and remove a property's access "
    "notes when the contract ends."
)

DISCLAIMER = (
    "Figures here are a management tool, not an accounting record and "
    "not tax advice. Chemical application records may have legal "
    "requirements where you work - check what your licence obliges you "
    "to keep."
)


# ---------------------------------------------------------------------------
# palette
# ---------------------------------------------------------------------------


class Palette:
    """The green the whole workbook is built in."""

    deep = "#1B4332"
    primary = "#2D6A4F"
    primary_mid = "#40916C"
    primary_light = "#74C69D"
    wash = "#D8F3DC"
    accent = "#B7791F"
    accent_light = "#FAF089"
    ink = "#1C2321"
    muted = "#6B7A72"
    rule = "#B7C9BE"
    paper = "#FBFDFB"

    good_bg, good_fg = "#D8F3DC", "#1B4332"
    warn_bg, warn_fg = "#FFF3C4", "#7A5B00"
    bad_bg, bad_fg = "#FFD9D4", "#8A2208"
    info_bg, info_fg = "#D6E8F5", "#14425F"
    muted_bg, muted_fg = "#EDF1EF", "#6B7A72"

    # ---- the tones the formats and the writer ask for by name ------
    white = "#FFFFFF"
    input_bg = "#FFFFFF"
    input_border = "#CBDDD2"
    calc_bg = "#F4F9F5"
    calc_border = "#E3EFE7"
    line = "#B7C9BE"
    note_bg = "#F7FBF8"
    grey_text = "#5A6B62"
    primary_soft = "#E8F3EC"
    accent_soft = "#FBF0DC"
    good_text = good_fg
    warn_text = warn_fg
    bad_text = bad_fg
    info_text = info_fg
    good = "#2F7D55"
    warn = "#B5802A"
    bad = "#B33A3A"


PALETTE = Palette


# ---------------------------------------------------------------------------
# ID prefixes - the join keys the whole product rests on
# ---------------------------------------------------------------------------

ID_PREFIXES: Dict[str, Tuple[str, int]] = {
    "customer": ("CUS-", 4),
    "property": ("PRP-", 4),
    "service": ("SVC-", 3),
    "quote": ("QTE-", 4),
    "job": ("JOB-", 5),
    "contract": ("CON-", 4),
    "crew": ("EMP-", 3),
    "equipment": ("EQP-", 3),
    "vehicle": ("VEH-", 3),
    "material": ("MAT-", 4),
    "invoice": ("INV-", 5),
}

#: (config key, label, help text) for the Settings page
ID_PREFIX_FIELDS: List[Tuple[str, str, str, int, str]] = [
    ("Customer ID", ID_PREFIXES["customer"][0], "CustomerPrefix",
     ID_PREFIXES["customer"][1],
     "Every customer you invoice."),
    ("Property ID", ID_PREFIXES["property"][0], "PropertyPrefix",
     ID_PREFIXES["property"][1],
     "Every address you work at."),
    ("Quote ID", ID_PREFIXES["quote"][0], "QuotePrefix",
     ID_PREFIXES["quote"][1],
     "Every estimate you send out."),
    ("Job ID", ID_PREFIXES["job"][0], "JobPrefix",
     ID_PREFIXES["job"][1],
     "Every visit. The busiest ID in the book."),
    ("Contract ID", ID_PREFIXES["contract"][0], "ContractPrefix",
     ID_PREFIXES["contract"][1],
     "Every recurring agreement."),
    ("Employee ID", ID_PREFIXES["crew"][0], "CrewPrefix",
     ID_PREFIXES["crew"][1],
     "Everyone who works a job."),
    ("Equipment ID", ID_PREFIXES["equipment"][0], "EquipmentPrefix",
     ID_PREFIXES["equipment"][1],
     "Every mower, trimmer and blower."),
    ("Material ID", ID_PREFIXES["material"][0], "MaterialPrefix",
     ID_PREFIXES["material"][1],
     "Fertiliser, mulch, seed, chemicals."),
    ("Invoice ID", ID_PREFIXES["invoice"][0], "InvoicePrefix",
     ID_PREFIXES["invoice"][1],
     "Every invoice you raise."),
]


# ---------------------------------------------------------------------------
# status sets - what a status MEANS, in one place
# ---------------------------------------------------------------------------

JOB_STATUSES = ["Scheduled", "Dispatched", "In progress", "Completed",
                "Rained off", "Skipped", "Cancelled", "Needs revisit"]

#: a job that still has to happen
OPEN_JOB_STATUSES = ("Scheduled", "Dispatched", "In progress",
                     "Needs revisit")
#: a job that was done and can be invoiced
DONE_JOB_STATUSES = ("Completed",)
#: a job that was not done and is not coming back
DROPPED_JOB_STATUSES = ("Skipped", "Cancelled")
#: a job that has to be caught up
CATCHUP_JOB_STATUSES = ("Rained off", "Needs revisit")

QUOTE_STATUSES = ["Draft", "Sent", "Followed up", "Accepted", "Declined",
                  "Expired", "Withdrawn"]
#: a quote still in play
LIVE_QUOTE_STATUSES = ("Sent", "Followed up")
WON_QUOTE_STATUSES = ("Accepted",)
LOST_QUOTE_STATUSES = ("Declined", "Expired", "Withdrawn")

INVOICE_STATUSES = ["Draft", "Sent", "Part paid", "Paid", "Overdue",
                    "Written off", "Disputed"]
#: an invoice that is still money owed to you
OWED_INVOICE_STATUSES = ("Sent", "Part paid", "Overdue", "Disputed")
PAID_INVOICE_STATUSES = ("Paid",)

CONTRACT_STATUSES = ["Active", "Paused", "Seasonal break", "Due renewal",
                     "Expired", "Cancelled"]
LIVE_CONTRACT_STATUSES = ("Active", "Due renewal")

CUSTOMER_STATUSES = ["Lead", "Active", "Occasional", "Seasonal", "Dormant",
                     "On hold", "Lost"]
ACTIVE_CUSTOMER_STATUSES = ("Active", "Seasonal", "Occasional")

EQUIPMENT_STATUSES = ["In service", "Needs service", "In repair",
                      "Out of service", "Spare", "Retired", "Sold"]
USABLE_EQUIPMENT_STATUSES = ("In service", "Spare")


# ---------------------------------------------------------------------------
# the lists behind the drop-downs
# ---------------------------------------------------------------------------

CUSTOMER_TYPES = ["Residential", "Residential - premium", "Commercial",
                  "Property management", "HOA / strata", "Municipal",
                  "School or college", "Church", "Retail park",
                  "Construction contract", "One-off"]

PROPERTY_TYPES = ["Front and back lawn", "Front lawn only", "Back lawn only",
                  "Large grounds", "Commercial frontage", "Car park verges",
                  "Sports pitch", "Communal gardens", "Roof terrace",
                  "Allotment or plot", "New build plot"]

ACCESS_TYPES = ["Open access", "Side gate", "Locked gate - key held",
                "Locked gate - code", "Through garage", "Key safe",
                "Customer must be home", "Barrier or fob", "Dog on site",
                "Restricted hours"]

TERRAIN_TYPES = ["Flat", "Gentle slope", "Steep slope", "Terraced",
                 "Uneven", "Wet or boggy", "Heavily shaded",
                 "Obstacle heavy"]

#: (service name, category, unit, default minutes per unit, blurb)
SERVICE_CATALOGUE: List[Tuple[str, str, str, float, str]] = [
    ("Lawn mowing - standard", "Mowing", "Per 1,000 sq ft", 9.0,
     "Cut, edge the perimeter and blow down the hard surfaces."),
    ("Lawn mowing - large grounds", "Mowing", "Per 1,000 sq ft", 5.5,
     "Ride-on work. Cheaper per foot, worth more per hour."),
    ("String trimming", "Mowing", "Per 1,000 sq ft", 3.5,
     "Around beds, posts, trees and anything the mower cannot reach."),
    ("Edging - hard surfaces", "Mowing", "Per linear ft", 0.12,
     "Drives, paths and kerbs cut back to a clean line."),
    ("Blow down and tidy", "Mowing", "Per visit", 8.0,
     "Clearing clippings off paths, drives and patios."),
    ("Hedge trimming", "Pruning", "Per linear ft", 1.6,
     "Sides and top, cuttings removed."),
    ("Shrub and bush pruning", "Pruning", "Per hour", 60.0,
     "Shaping, deadheading and taking out damage."),
    ("Small tree pruning", "Pruning", "Per hour", 60.0,
     "Under 15 ft only. Anything taller is a tree surgeon's job."),
    ("Fertiliser application", "Treatment", "Per 1,000 sq ft", 2.5,
     "Granular feed, spread and watered in."),
    ("Weed control - selective", "Treatment", "Per 1,000 sq ft", 2.5,
     "Broadleaf spray. Licence required in most places."),
    ("Weed control - hard surface", "Treatment", "Per 1,000 sq ft", 2.0,
     "Paths, drives and gravel."),
    ("Moss treatment", "Treatment", "Per 1,000 sq ft", 3.0,
     "Iron sulphate, then scarify once it blackens."),
    ("Grub and pest treatment", "Treatment", "Per 1,000 sq ft", 2.5,
     "Curative or preventative, depending on the season."),
    ("Aeration", "Renovation", "Per 1,000 sq ft", 6.0,
     "Hollow tine. Hard work, high margin, once or twice a year."),
    ("Scarification", "Renovation", "Per 1,000 sq ft", 9.0,
     "Takes out the thatch. Generates a lot of waste."),
    ("Overseeding", "Renovation", "Per 1,000 sq ft", 4.0,
     "Best paired with aeration in the same visit."),
    ("Topdressing", "Renovation", "Per 1,000 sq ft", 7.0,
     "Levelling and soil improvement."),
    ("Turf laying", "Install", "Per sq ft", 0.09,
     "Ground prep, lay and firm. Priced with the turf."),
    ("Mulch install", "Install", "Per cu yd", 35.0,
     "Delivered, barrowed and spread to depth."),
    ("Planting - shrubs", "Install", "Per plant", 11.0,
     "Dig, plant, backfill, water in."),
    ("Planting - bedding", "Install", "Per tray", 8.0,
     "Seasonal colour, usually twice a year."),
    ("Bed edging and redefining", "Install", "Per linear ft", 0.5,
     "Cutting a new edge and shaping the bed line."),
    ("Spring cleanup", "Seasonal", "Per visit", 180.0,
     "The big one. Clear winter debris, cut back, first feed."),
    ("Leaf clearance", "Seasonal", "Per visit", 120.0,
     "Autumn, repeatedly, and always underestimated."),
    ("Fall cleanup", "Seasonal", "Per visit", 180.0,
     "Final cut, leaves away, beds put to bed."),
    ("Gutter clearing", "Seasonal", "Per visit", 45.0,
     "Single storey only, from a ladder."),
    ("Pressure washing", "Seasonal", "Per 100 sq ft", 12.0,
     "Patios and drives. Sells itself after a wet winter."),
    ("Snow clearance", "Seasonal", "Per visit", 50.0,
     "Where winter justifies it. Keeps a crew paid in January."),
    ("Irrigation check", "Maintenance", "Per visit", 40.0,
     "Heads, timers, leaks. Start and end of season."),
    ("Green waste disposal", "Maintenance", "Per cu yd", 10.0,
     "Tip fees are real money. Always charge them on."),
]

SERVICE_CATEGORIES = ["Mowing", "Pruning", "Treatment", "Renovation",
                      "Install", "Seasonal", "Maintenance", "Other"]

PRICING_UNITS = ["Per visit", "Per hour", "Per 1,000 sq ft", "Per sq ft",
                 "Per linear ft", "Per cu yd", "Per plant", "Per tray",
                 "Per 100 sq ft", "Per item"]

#: (label, visits a year, days between) - the recurring round
FREQUENCIES: List[Tuple[str, float, int]] = [
    ("Weekly", 52, 7),
    ("Every 10 days", 36, 10),
    ("Fortnightly", 26, 14),
    ("Every 3 weeks", 17, 21),
    ("Monthly", 12, 30),
    ("Every 6 weeks", 9, 42),
    ("Quarterly", 4, 91),
    ("Twice a year", 2, 182),
    ("Annually", 1, 365),
    ("Seasonal - mowing only", 30, 7),
    ("One-off", 0, 0),
]

CREW_ROLES = ["Owner / operator", "Crew leader", "Groundsperson",
              "Machine operator", "Horticulturist", "Spray technician",
              "Arborist", "Driver", "Apprentice", "Seasonal casual",
              "Office / admin"]

EMPLOYMENT_TYPES = ["Full time", "Part time", "Seasonal", "Casual",
                    "Subcontractor", "Owner"]

CREW_STATUSES = ["Active", "On holiday", "Off sick", "Seasonal layoff",
                 "Left"]

CREW_NAMES = ["Crew A", "Crew B", "Crew C", "Solo", "Unassigned"]

EQUIPMENT_CATEGORIES = ["Ride-on mower", "Walk-behind mower", "Push mower",
                        "String trimmer", "Hedge trimmer", "Leaf blower",
                        "Chainsaw", "Edger", "Aerator", "Scarifier",
                        "Sprayer", "Pressure washer", "Spreader",
                        "Trailer", "Hand tools", "Safety equipment",
                        "Other"]

EQUIPMENT_CONDITIONS = ["New", "Good", "Fair", "Worn", "Needs attention",
                        "Broken"]

VEHICLE_TYPES = ["Pickup truck", "Flatbed", "Van", "Tipper", "Trailer",
                 "Utility vehicle", "Car"]

FUEL_TYPES = ["Petrol / gasoline", "Diesel", "Mixed 2-stroke", "Electric",
              "LPG"]

MAINTENANCE_TYPES = ["Routine service", "Oil change", "Blade sharpen",
                     "Blade replace", "Air filter", "Spark plug",
                     "Belt replace", "Tyre or wheel", "Brake work",
                     "Hydraulics", "Bodywork", "Breakdown repair",
                     "Safety inspection", "Annual test", "Winterise"]

MATERIAL_CATEGORIES = ["Fertiliser", "Weed control", "Pesticide",
                       "Grass seed", "Turf", "Mulch", "Bark", "Topsoil",
                       "Compost", "Sand", "Gravel", "Plants", "Bedding",
                       "Edging", "Membrane", "Fuel", "Oil and lubricant",
                       "Consumables", "Other"]

MATERIAL_UNITS = ["Bag", "Sack", "Tote", "Bottle", "Drum", "Litre",
                  "Gallon", "Kilogram", "Pound", "Cubic yard", "Tonne",
                  "Roll", "Square metre", "Square foot", "Each", "Tray"]

PAYMENT_METHODS = ["Bank transfer", "Card", "Direct debit", "Standing order",
                   "Cash", "Cheque", "Online payment link", "Account"]

#: (label, days until due)
PAYMENT_TERMS: List[Tuple[str, int]] = [
    ("Due on completion", 0),
    ("Net 7", 7),
    ("Net 14", 14),
    ("Net 30", 30),
    ("Net 45", 45),
    ("Net 60", 60),
    ("Monthly in advance", -30),
    ("Monthly in arrears", 30),
]

EXPENSE_CATEGORIES = ["Fuel - vehicles", "Fuel - machinery", "Materials",
                      "Green waste disposal", "Equipment purchase",
                      "Equipment repair", "Equipment hire",
                      "Vehicle maintenance", "Vehicle insurance",
                      "Business insurance", "Licences and certification",
                      "Wages and subcontractors", "Advertising",
                      "Website and software", "Phone", "Workwear and PPE",
                      "Yard or storage rent", "Accounting and legal",
                      "Bank charges", "Training", "Office expenses",
                      "Tax and national insurance", "Miscellaneous"]

#: costs that belong to a job rather than to the business
JOB_COST_CATEGORIES = ["Fuel - machinery", "Materials",
                       "Green waste disposal", "Equipment hire"]

TAX_CATEGORIES = ["Cost of sale", "Operating expense", "Capital / asset",
                  "Vehicle expense", "Owner drawing", "Not deductible",
                  "Review with accountant"]

LEAD_SOURCES = ["Word of mouth", "Existing customer referral",
                "Google search", "Google Business profile", "Facebook",
                "Instagram", "Nextdoor", "Checkatrade or similar",
                "Van signage", "Leaflet drop", "Door knock", "Yard sign",
                "Repeat customer", "Property manager", "Other"]

FEEDBACK_SOURCES = ["Asked on site", "Email", "Text message", "Phone call",
                    "Google review", "Facebook review", "Checkatrade",
                    "Complaint", "Unprompted"]

FEEDBACK_TYPES = ["Compliment", "Review", "Suggestion", "Complaint",
                  "Quality issue", "Damage claim", "Billing query"]

FEEDBACK_STATUSES = ["Logged", "Acknowledged", "Being fixed",
                     "Revisit booked", "Resolved", "Refunded",
                     "Lost the customer"]

SEASONS = ["Spring", "Summer", "Autumn / Fall", "Winter", "All year"]

#: (label, months) - what the seasonal planner groups on
SEASON_MONTHS: Dict[str, Tuple[int, ...]] = {
    "Spring": (3, 4, 5),
    "Summer": (6, 7, 8),
    "Autumn / Fall": (9, 10, 11),
    "Winter": (12, 1, 2),
}

#: the states a property can be in
PROPERTY_STATUSES = [
    "Active", "Seasonal only", "One-off only", "On hold", "Lost",
    "Sold / moved", "Archived",
]

#: the states a service in the catalogue can be in
SERVICE_STATUSES = ["Active", "Seasonal", "On request", "Retired"]

#: the states a material can be in
MATERIAL_STATUSES = ["Active", "Seasonal", "Special order",
                     "Discontinued"]

#: crew who are still on the books, however they are feeling today
ACTIVE_CREW_STATUSES = ("Active", "On holiday", "Off sick")

#: why somebody is not available on a given day
ABSENCE_REASONS = [
    "Holiday", "Sick", "Training", "Rained off", "Public holiday",
    "Unpaid day off", "Working elsewhere", "Equipment down",
    "Not scheduled",
]

#: what an hour on the timesheet was spent doing
TASK_TYPES = [
    "Mowing", "Strimming and edging", "Hedge and shrub work",
    "Planting and beds", "Leaf clearance", "Snow clearance",
    "Hardscaping", "Irrigation", "Tree work", "Clean-up and hauling",
    "Driving", "Loading and unloading", "Yard and workshop",
    "Equipment maintenance", "Quoting and site visits",
    "Admin and invoicing", "Training", "Other",
]

#: whether a material line is coming into the yard or going out of it
STOCK_MOVES = ["Purchase", "Usage", "Wastage"]

#: what a vehicle line is for
VEHICLE_COST_TYPES = [
    "Fuel", "Service", "Repair", "Tyres", "Insurance",
    "Road tax / licence", "Finance payment", "Cleaning", "Other",
]

#: a starting fleet - rename these on the Settings tab
DEFAULT_VEHICLES = [
    "Truck 1", "Truck 2", "Van", "Trailer 1", "Trailer 2",
    "Personal vehicle",
]

#: why the feedback happened - the column that teaches you something
FEEDBACK_CAUSES = [
    "Rushed the job", "Missed an area", "Wrong day or no-show",
    "Late arrival", "Damage to property", "Clippings left behind",
    "Gate or access problem", "Machine broke down",
    "Weather delay", "Price surprise", "Invoice error",
    "Communication", "New crew member", "Nothing - it went well",
    "Other",
]

WEATHER_CONDITIONS = ["Dry", "Light rain", "Heavy rain", "Frozen", "Snow",
                      "High wind", "Heatwave", "Too wet to cut"]

PRIORITIES = ["1 - Urgent", "2 - High", "3 - Normal", "4 - Low",
              "5 - When convenient"]

YES_NO = ["Yes", "No"]

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]

CURRENCIES = ["USD", "GBP", "EUR", "CAD", "AUD", "NZD", "ZAR"]


# ---------------------------------------------------------------------------
# register capacity
# ---------------------------------------------------------------------------

#: module name -> rows. Scaled together by --rows.
DEFAULT_ROWS: Dict[str, int] = {
    "customers": 250,
    "properties": 300,
    "services": 80,
    "quotes": 300,
    "jobs": 1500,
    "contracts": 250,
    "crew": 40,
    "schedule": 900,
    "timesheets": 900,
    "equipment": 120,
    "vehicles": 400,
    "materials": 200,
    "invoices": 600,
    "expenses": 600,
    "feedback": 200,
    "profit": 14,
}

#: the register --rows is expressed in terms of
SCALE_ANCHOR = "Job & Work Orders"


# ---------------------------------------------------------------------------
# the configuration object
# ---------------------------------------------------------------------------


@dataclass
class Business:
    name: str = "Thornhill Grounds Care"
    owner: str = "Marcus Thornhill"
    phone: str = "(555) 014-2288"
    email: str = "office@thornhillgrounds.example"
    website: str = "thornhillgrounds.example"
    address_1: str = "Unit 6, Fallow Yard"
    address_2: str = "Ashbourne Road"
    city: str = "Granton"
    region: str = "Ohio"
    postcode: str = "44021"
    country: str = "United States"
    tax_id: str = ""
    licence: str = "OH-PEST-21884"
    insurance: str = "GL-7741-2290"


@dataclass
class Config:
    """Everything the generator needs to write one workbook."""

    business: Business = field(default_factory=Business)

    currency: str = "$"
    currency_code: str = "USD"

    # ---- pricing -----------------------------------------------------
    labour_rate: float = 38.00        # what an hour of crew time costs you
    charge_rate: float = 72.00        # what you charge for that hour
    minimum_visit: float = 45.00      # you do not get out of the truck for less
    target_margin: float = 0.45       # the gross margin you are aiming at
    minimum_margin: float = 0.25      # the one you refuse to go under
    material_markup: float = 1.35     # what you add to materials
    travel_rate_mile: float = 1.10    # what a mile of travel costs the job
    overhead_per_hour: float = 11.00  # yard, insurance, admin, per crew hour
    quote_valid_days: int = 30

    # ---- operations --------------------------------------------------
    crew_size: int = 2
    working_hours_day: float = 8.0
    overtime_after_hours: float = 40.0
    overtime_multiplier: float = 1.5
    drive_time_minutes: int = 12      # average hop between stops
    mow_minutes_per_1000: float = 9.0  # minutes per 1,000 sq ft, one person
    season_start_month: int = 3
    season_end_month: int = 11

    # ---- alert windows -----------------------------------------------
    upcoming_days: int = 7            # the "coming up" window
    overdue_days: int = 1             # when an invoice turns overdue
    chase_quote_days: int = 5         # when an unanswered quote nags
    renewal_warning_days: int = 45    # when a contract renewal warns
    service_hours: int = 100          # engine hours between services
    service_months: int = 12          # or months, whichever comes first
    service_warning_hours: int = 25   # engine hours before a service warns
    service_warning_days: int = 30    # or days since the last one
    dormant_days: int = 90            # when a customer has gone quiet
    feedback_chase_days: int = 14     # when an unresolved complaint nags

    # ---- money -------------------------------------------------------
    tax_rate: float = 0.0
    tax_on_services: bool = False
    tax_name: str = "Sales tax"
    fuel_price: float = 3.85
    target_revenue_year: float = 240000.0
    target_jobs_week: int = 60

    # ---- generation --------------------------------------------------
    author: str = AUTHOR
    password: str = PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True
    rows_override: int = 0
    _today: _dt.date = None

    # ---- derived -----------------------------------------------------

    @property
    def today(self) -> _dt.date:
        return self._today or _dt.date.today()

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
    def product_short(self) -> str:
        return PRODUCT_SHORT

    @property
    def listing_title(self) -> str:
        return LISTING_TITLE

    @property
    def report_year(self) -> int:
        return self.today.year

    def prefix(self, key: str) -> str:
        return ID_PREFIXES[key][0]

    def digits(self, key: str) -> int:
        return ID_PREFIXES[key][1]

    def row_count(self, module: str) -> int:
        """Rows for a register, scaled if --rows was given."""
        base = DEFAULT_ROWS.get(module, 200)
        if not self.rows_override:
            return base
        anchor = DEFAULT_ROWS["jobs"]
        scaled = int(round(base * self.rows_override / anchor))
        return max(6, scaled)

    def scale_rows(self, count: int) -> int:
        if not self.rows_override:
            return count
        anchor = DEFAULT_ROWS["jobs"]
        return max(4, int(round(count * self.rows_override / anchor)))

    def service_names(self) -> List[str]:
        return [name for name, *_rest in SERVICE_CATALOGUE]

    def frequency_labels(self) -> List[str]:
        return [label for label, *_rest in FREQUENCIES]

    def term_labels(self) -> List[str]:
        return [label for label, _days in PAYMENT_TERMS]
