"""Every default, list, package and palette the workbook is built from.

Nothing in the generated file is hard coded to one photographer's way
of working: the packages, their inclusions and their prices, the
payment schedule, the mileage rate, the editing turnaround, the shot
list and the wedding-day timeline are all settings a buyer types over.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# the product
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PASSWORD = "premium"
VERSION = "1.0.0"

PRODUCT_NAME = "Wedding Photographer Business Manager"
PRODUCT_SHORT = "Wedding Photography Business"
PRODUCT_SUBTITLE = ("From first enquiry to final gallery - one workbook "
                    "for the whole wedding photography business")
LISTING_TITLE = ("Wedding Photographer Business Spreadsheet | Photography "
                 "CRM, Booking Calendar, Pricing, Invoices & Client "
                 "Management")

#: said plainly on Getting Started, on Settings and in the listing
HONESTY_NOTE = (
    "This workbook is a business organisation tool. It is not a live "
    "booking integration, it is not a contract-signing platform and it "
    "is not a gallery host. It does not connect to your calendar, your "
    "email, your gallery provider or your bank, and it cannot send a "
    "contract for signature or take a payment. It records what you have "
    "sent, signed, delivered and been paid, so that nothing is lost "
    "between the enquiry and the final gallery.")

#: the Contracts tab says this at the top, every time
CONTRACT_NOTE = (
    "This tab tracks the status of your paperwork. It does not draft, "
    "generate or execute a contract and nothing in it is legal advice. "
    "Have your contract, model release and cancellation policy written "
    "or reviewed by a lawyer in your own country, then record here when "
    "each one was sent, signed and filed.")

#: the privacy line on the client tabs
PRIVACY_NOTE = (
    "Record only what you need to photograph the wedding well. Do not "
    "store card numbers, bank details, passport or ID scans in a "
    "spreadsheet. Guest lists and family notes are personal data - keep "
    "the file somewhere private, share it with nobody who does not need "
    "it, and delete a wedding's personal notes once the gallery has "
    "been delivered and the review is in.")

#: the tax line
DISCLAIMER = (
    "Nothing here is accounting or tax advice. How a cost is "
    "classified, what is deductible, whether a camera body is an "
    "expense or a capital asset, and how self-employed photography "
    "income is taxed all depend on your jurisdiction and your "
    "circumstances. The figures are organised so that the conversation "
    "with an accountant is a short one; they do not replace it.")


# ---------------------------------------------------------------------------
# lists - every drop down in the workbook
# ---------------------------------------------------------------------------

LEAD_SOURCES = [
    "Instagram", "Pinterest", "Website", "Google search", "Referral",
    "Facebook", "Wedding fair", "Venue recommendation", "Past client",
    "Wedding directory", "TikTok", "Word of mouth", "Other",
]

LEAD_STATUSES = [
    "New", "Contacted", "Consultation booked", "Consultation done",
    "Proposal sent", "Booked", "Lost", "Not a fit", "Date unavailable",
]

#: lead statuses that are still live, so still worth chasing
OPEN_LEAD_STATUSES = ["New", "Contacted", "Consultation booked",
                      "Consultation done", "Proposal sent"]
WON_LEAD_STATUSES = ["Booked"]
LOST_LEAD_STATUSES = ["Lost", "Not a fit", "Date unavailable"]

CLIENT_STATUSES = [
    "Enquiry", "Booked", "Wedding done", "Delivered", "Complete",
    "Cancelled", "Postponed",
]

PRIORITY_LEVELS = ["High", "Normal", "Low"]

BOOKING_STATUSES = [
    "Pencilled in", "Confirmed", "Wedding done", "In editing",
    "Delivered", "Complete", "Cancelled", "Postponed",
]
#: a booking that still occupies the date
HOLDING_STATUSES = ["Pencilled in", "Confirmed", "Wedding done",
                    "In editing", "Delivered", "Complete"]
#: a booking that counts towards revenue
EARNING_STATUSES = ["Confirmed", "Wedding done", "In editing",
                    "Delivered", "Complete"]
#: a booking whose wedding day has happened
SHOT_STATUSES = ["Wedding done", "In editing", "Delivered", "Complete"]

CONTRACT_STATUSES = [
    "Not sent", "Sent", "Viewed", "Signed", "Counter-signed",
    "Amended", "Cancelled",
]

DOC_STATUSES = ["Not needed", "Outstanding", "Sent", "Received",
                "Signed", "Filed"]

PAYMENT_STATUSES = [
    "Not due yet", "Due", "Part paid", "Paid in full", "Overdue",
    "Refunded", "Written off",
]

PAYMENT_STAGES = [
    "Booking deposit", "Second instalment", "Third instalment",
    "Final payment", "Add-on", "Album", "Prints", "Travel",
    "Overtime", "Refund", "Other",
]

PAYMENT_METHODS = [
    "Bank transfer", "Debit card", "Credit card", "Cash", "PayPal",
    "Stripe", "Cheque", "Direct debit", "Other",
]

PACKAGE_TIERS = ["Essential", "Classic", "Premium", "Luxury", "Elopement",
                 "Micro wedding", "Custom"]

#: the four packages the workbook ships with, all editable on Settings
#: (name, tier, hours, photographers, engagement session, edited images,
#:  album, print credit, travel allowance miles, price)
PACKAGES: List[Tuple[str, str, float, int, str, int, str, float,
                     float, float]] = [
    ("Essential Wedding", "Essential", 6, 1, "No", 350,
     "No album", 0, 30, 1200),
    ("Classic Wedding", "Classic", 8, 1, "Yes", 500,
     "20 page album", 100, 60, 1800),
    ("Premium Wedding", "Premium", 10, 2, "Yes", 700,
     "30 page album", 250, 100, 2500),
    ("Luxury Wedding", "Luxury", 12, 2, "Yes", 900,
     "40 page album + parent copies", 500, 150, 3500),
]

ALBUM_OPTIONS = ["No album", "10 page album", "20 page album",
                 "30 page album", "40 page album",
                 "40 page album + parent copies", "Album to be chosen"]

ADD_ON_TYPES = [
    "Extra hour", "Second shooter", "Engagement session",
    "Bridal portraits", "Rehearsal dinner", "Album upgrade",
    "Parent albums", "Extra prints", "Wall art", "Drone coverage",
    "Photo booth", "Video add-on", "Rush delivery", "Raw files",
    "Travel", "Accommodation", "Other",
]

STAFF_ROLES = [
    "Lead photographer", "Second shooter", "Third shooter", "Assistant",
    "Videographer", "Editor", "Retoucher", "Album designer",
    "Studio manager", "Intern",
]

PAY_BASIS = ["Per wedding", "Per hour", "Per day", "Per image",
             "Monthly retainer", "% of booking", "Not paid (owner)"]

AVAILABILITY = ["Any day", "Weekends only", "Weekdays only",
                "By arrangement", "Unavailable"]

#: the wedding-day timeline the workbook ships with.  Every row is
#: (key, label, default minutes before/after the ceremony, default
#:  duration in minutes, who usually covers it)
TIMELINE_EVENTS: List[Tuple[str, str, int, int, str]] = [
    ("venue_detail", "Venue and detail shots", -300, 30,
     "Lead photographer"),
    ("bride_prep", "Bridal preparation", -270, 75, "Lead photographer"),
    ("groom_prep", "Groom preparation", -240, 45, "Second shooter"),
    ("dress_details", "Dress, rings and detail shots", -210, 20,
     "Lead photographer"),
    ("first_look", "First look", -120, 30, "Lead photographer"),
    ("couple_portraits_1", "Couple portraits before the ceremony",
     -90, 30, "Lead photographer"),
    ("guests_arrive", "Guests arriving", -30, 20, "Second shooter"),
    ("ceremony", "Wedding ceremony", 0, 45, "Lead photographer"),
    ("confetti", "Confetti and congratulations", 50, 15,
     "Lead photographer"),
    ("family_groups", "Family group photographs", 70, 40,
     "Lead photographer"),
    ("wedding_party", "Wedding party photographs", 115, 25,
     "Lead photographer"),
    ("couple_portraits_2", "Couple portraits", 145, 30,
     "Lead photographer"),
    ("cocktail_hour", "Cocktail hour and candids", 145, 45,
     "Second shooter"),
    ("reception_detail", "Reception room details", 180, 20,
     "Second shooter"),
    ("entrance", "Reception entrance", 210, 10, "Lead photographer"),
    ("speeches", "Speeches", 240, 45, "Lead photographer"),
    ("cake_cutting", "Cake cutting", 300, 10, "Lead photographer"),
    ("first_dance", "First dance", 315, 15, "Lead photographer"),
    ("dancing", "Dancing and party coverage", 330, 60,
     "Lead photographer"),
    ("sparkler_exit", "Sparkler or night exit", 400, 15,
     "Lead photographer"),
]

#: the shot list, grouped exactly as a photographer works through it.
#: (key, group label, [shot, ...])
SHOT_LIST: List[Tuple[str, str, List[str]]] = [
    ("details", "Details and venue", [
        "Venue exterior",
        "Ceremony room before guests",
        "Reception room before guests",
        "Table settings and stationery",
        "Flowers and decorations",
        "The dress hanging",
        "Shoes, rings and jewellery",
        "Invitation suite flat lay",
    ]),
    ("prep", "Getting ready", [
        "Bride in robe with the wedding party",
        "Hair and make-up",
        "Mother or friend helping with the dress",
        "Bride fully ready, window light portrait",
        "Groom and party getting ready",
        "Groom's details - watch, cufflinks, buttonhole",
        "Letters, gifts and first-look-at-the-note moments",
    ]),
    ("couple", "Bride and groom", [
        "Bride solo portraits",
        "Groom solo portraits",
        "First look",
        "Couple walking together",
        "Romantic close-ups",
        "Full length couple portrait with the venue",
        "Golden hour couple portraits",
        "Night portrait with off-camera light",
    ]),
    ("family", "Family and groups", [
        "Bride with her parents",
        "Groom with his parents",
        "Both families together",
        "Siblings",
        "Grandparents",
        "Extended family",
        "Wedding party together",
        "Bride with bridesmaids",
        "Groom with groomsmen",
    ]),
    ("ceremony", "Ceremony", [
        "Guests arriving and being seated",
        "Groom waiting at the front",
        "Walking down the aisle",
        "The couple's faces during the vows",
        "Exchange of rings",
        "First kiss",
        "Signing the register",
        "Ceremony exit and confetti",
    ]),
    ("reception", "Reception", [
        "Reception room and cake",
        "Entrance of the couple",
        "Speeches - speakers and reactions",
        "First dance",
        "Cake cutting",
        "Guests dancing",
        "Candid guest moments",
        "Bouquet toss",
        "Send-off",
    ]),
]

EDITING_STAGES = [
    "Not started", "Cards backed up", "Imported", "Culling",
    "Culled", "Editing", "Colour correction", "Retouching",
    "Album design", "Preview sent", "Revisions", "Ready to deliver",
    "Delivered",
]

#: the editing workflow checklist, in order.  (key, label)
EDITING_STEPS: List[Tuple[str, str]] = [
    ("backed_up", "Memory cards backed up"),
    ("imported", "Photos imported"),
    ("culled", "Culling complete"),
    ("selected", "Selection complete"),
    ("edited", "Editing complete"),
    ("colour", "Colour correction done"),
    ("retouched", "Retouching done"),
    ("album_designed", "Album designed"),
    ("preview_sent", "Client preview sent"),
    ("final_uploaded", "Final gallery uploaded"),
]

GALLERY_STATUSES = [
    "Not created", "Created", "Preview sent", "Client reviewing",
    "Revisions requested", "Delivered", "Archived", "Expired",
]

EQUIPMENT_CATEGORIES = [
    "Camera body", "Lens", "Flash / speedlight", "Studio lighting",
    "Light modifier", "Tripod / monopod", "Memory card", "Battery",
    "Camera bag", "Backup drive", "Editing computer", "Monitor",
    "Audio", "Drone", "Software licence", "Other",
]

EQUIPMENT_CONDITIONS = ["New", "Excellent", "Good", "Fair",
                        "Needs repair", "Retired", "Lost or stolen"]

INSURANCE_STATUSES = ["Insured", "Not insured", "Pending", "Expired",
                      "Not needed"]

TRAVEL_MODES = ["Car", "Train", "Flight", "Taxi", "Hire car", "Other"]

REIMBURSEMENT_STATUSES = ["Not charged", "To invoice", "Invoiced",
                          "Reimbursed", "Absorbed"]

MARKETING_PLATFORMS = [
    "Instagram", "Pinterest", "Facebook", "TikTok", "Blog", "Website",
    "Google Business", "Wedding directory", "Email newsletter",
    "YouTube", "Print ad", "Wedding fair", "Other",
]

CONTENT_TYPES = [
    "Full wedding gallery", "Sneak peek", "Carousel", "Reel / video",
    "Story", "Blog post", "Behind the scenes", "Client testimonial",
    "Educational post", "Promotion", "Portfolio update", "Other",
]

CONTENT_STATUSES = ["Idea", "Drafted", "Scheduled", "Published",
                    "Evergreen", "Archived"]

EXPENSE_CATEGORIES = [
    "Camera equipment", "Lens purchases", "Lighting & grip",
    "Memory & storage", "Software subscriptions", "Editing services",
    "Second shooters", "Assistants", "Albums & prints",
    "Packaging & postage", "Marketing & advertising",
    "Website & hosting", "Insurance", "Equipment repair",
    "Equipment rental", "Studio rent", "Travel & mileage",
    "Accommodation", "Meals on shoot", "Office expenses",
    "Education & training", "Accounting & legal", "Bank & card fees",
    "Licences & permits", "Client gifts", "Tax & national insurance",
    "Miscellaneous",
]

TAX_CATEGORIES = [
    "Operating expense", "Capital / asset", "Cost of sale",
    "Owner drawing", "Not deductible", "Review with accountant",
]

#: expenses that are usually an asset rather than an expense
CAPITAL_CATEGORIES = ["Camera equipment", "Lens purchases",
                      "Lighting & grip", "Editing computer"]

#: expenses that belong to one wedding rather than to the business
DIRECT_CATEGORIES = ["Second shooters", "Assistants", "Albums & prints",
                     "Packaging & postage", "Travel & mileage",
                     "Accommodation", "Meals on shoot",
                     "Editing services"]

RECURRING_FREQUENCIES = ["One off", "Weekly", "Monthly", "Quarterly",
                         "Twice a year", "Annual"]

FREQUENCY_PER_YEAR = {
    "One off": 0, "Weekly": 52, "Monthly": 12, "Quarterly": 4,
    "Twice a year": 2, "Annual": 1,
}

REVIEW_PLATFORMS = ["Google", "Facebook", "Instagram", "Website",
                    "Wedding directory", "Email", "Word of mouth",
                    "Other"]

REVIEW_STATUSES = ["Not requested", "Requested", "Received",
                   "No review left", "Declined", "Chased"]

WEDDING_STYLES = [
    "Classic", "Documentary", "Fine art", "Editorial", "Rustic",
    "Boho", "Modern", "Vintage", "Destination", "Elopement",
    "Micro wedding", "Traditional cultural", "Other",
]

PHOTO_STYLES = ["Light and airy", "Dark and moody", "True to colour",
                "Film emulation", "Black and white heavy",
                "Mixed - photographer's choice"]

DELIVERY_PREFERENCES = ["Online gallery only", "Gallery + USB",
                        "Gallery + album", "Gallery + prints",
                        "Everything"]

VENUE_TYPES = ["Hotel", "Barn", "Country house", "Church", "Registry office",
               "Marquee", "Vineyard", "Beach", "Garden", "Restaurant",
               "Castle", "Other"]

YES_NO = ["Yes", "No"]
YES_NO_NA = ["Yes", "No", "Not needed"]
YES_NO_PENDING = ["Yes", "No", "Pending"]

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday"]

#: (name, first month, last month) - winter wraps the year end
SEASONS: List[Tuple[str, int, int]] = [
    ("Winter", 12, 2), ("Spring", 3, 5),
    ("Summer", 6, 8), ("Autumn", 9, 11),
]

COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia", "Ireland",
    "New Zealand", "France", "Spain", "Italy", "Germany", "Portugal",
    "Netherlands", "Greece", "Mexico", "India", "South Africa", "Other",
]

#: how far ahead a wedding counts as "coming up"
LEAD_TIME_BANDS = [
    ("This week", 0, 7), ("Next 30 days", 8, 30),
    ("1-3 months", 31, 90), ("3-6 months", 91, 180),
    ("6-12 months", 181, 365), ("Over a year", 366, 3650),
]

#: every named drop-down list the workbook defines
LIST_NAMES = [
    "LeadSourceList", "LeadStatusList", "ClientStatusList",
    "PriorityList", "BookingStatusList", "ContractStatusList",
    "DocStatusList", "PaymentStatusList", "PaymentStageList",
    "PaymentMethodList", "PackageList", "PackageTierList",
    "AlbumList", "AddOnList", "StaffRoleList", "PayBasisList",
    "AvailabilityList", "EditingStageList", "GalleryStatusList",
    "EquipmentCategoryList", "EquipmentConditionList",
    "InsuranceStatusList", "TravelModeList", "ReimbursementList",
    "MarketingPlatformList", "ContentTypeList", "ContentStatusList",
    "ExpenseCategoryList", "TaxCategoryList", "FrequencyList",
    "ReviewPlatformList", "ReviewStatusList", "WeddingStyleList",
    "PhotoStyleList", "DeliveryPreferenceList", "VenueTypeList",
    "YesNoList", "YesNoNAList", "YesNoPendingList", "CountryList",
    "MonthKeyList", "ClientList", "ClientNameList", "LeadList",
    "BookingList", "StaffList", "StaffNameList", "EquipmentList",
    "InvoiceList", "ShotGroupList", "TimelineEventList",
]

#: (label, default prefix, defined name, digits)
ID_PREFIX_FIELDS: List[Tuple[str, str, str, int]] = [
    ("Client", "CLT-", "ClientPrefix", 4),
    ("Lead", "LED-", "LeadPrefix", 4),
    ("Booking", "WED-", "BookingPrefix", 4),
    ("Package", "PKG-", "PackagePrefix", 2),
    ("Contract", "CON-", "ContractPrefix", 4),
    ("Invoice", "INV-", "InvoicePrefix", 4),
    ("Timeline row", "TLN-", "TimelinePrefix", 4),
    ("Shot", "SHT-", "ShotPrefix", 4),
    ("Photographer", "PHG-", "StaffPrefix", 3),
    ("Editing job", "EDT-", "EditPrefix", 4),
    ("Gallery", "GAL-", "GalleryPrefix", 4),
    ("Equipment", "EQP-", "EquipmentPrefix", 3),
    ("Travel", "TRV-", "TravelPrefix", 4),
    ("Marketing", "MKT-", "MarketingPrefix", 4),
    ("Expense", "EXP-", "ExpensePrefix", 4),
    ("Profit row", "PRF-", "ProfitPrefix", 4),
    ("Review", "REV-", "ReviewPrefix", 4),
]

ID_PREFIXES: Dict[str, Tuple[str, int]] = {
    "client": ("CLT-", 4), "lead": ("LED-", 4), "booking": ("WED-", 4),
    "package": ("PKG-", 2), "contract": ("CON-", 4),
    "invoice": ("INV-", 4), "timeline": ("TLN-", 4), "shot": ("SHT-", 4),
    "staff": ("PHG-", 3), "edit": ("EDT-", 4), "gallery": ("GAL-", 4),
    "equipment": ("EQP-", 3), "travel": ("TRV-", 4),
    "marketing": ("MKT-", 4), "expense": ("EXP-", 4),
    "profit": ("PRF-", 4), "review": ("REV-", 4),
}


# ---------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------

#: the register the `--rows` switch scales everything else against
SCALE_ANCHOR = "Wedding Bookings"

#: weddings shown side by side on the dashboard and the reports
MAX_WEDDINGS_SHOWN = 10

#: days on the dashboard's "what is coming up" strip
UPCOMING_STRIP_DAYS = 14

DEFAULT_ROWS: Dict[str, int] = {
    "Client CRM": 300,
    "Lead Tracker": 400,
    "Wedding Bookings": 200,
    "Packages & Pricing": 30,
    "Contracts & Documents": 200,
    "Payments & Invoices": 600,
    "Wedding Timeline": 900,
    "Shot List Manager": 1400,
    "Photographer & Staff": 40,
    "Editing Workflow": 200,
    "Gallery & Delivery": 200,
    "Equipment Inventory": 150,
    "Travel & Mileage": 300,
    "Marketing Calendar": 400,
    "Expense Tracker": 600,
    "Profit Analysis": 200,
    "Reviews & Referrals": 200,
}


# ---------------------------------------------------------------------------
# palette
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    ink: str = "#2B2118"
    deep: str = "#4A3528"
    primary: str = "#8C6A4F"
    primary_mid: str = "#B08B68"
    primary_soft: str = "#F3EBE3"
    accent: str = "#A8577A"
    good: str = "#3F7D5C"
    warn: str = "#B8862A"
    bad: str = "#B23A48"
    muted: str = "#8A7D72"
    paper: str = "#FFFDFB"
    rule: str = "#D9CBBE"

    # ---- derived tones the formats and the writer ask for ----------
    # A warm neutral scheme: inputs are plain white so they read as
    # "type here", calculated cells sit a shade warmer, and the four
    # status colours are muted enough to survive a whole page of them.
    white: str = "#FFFFFF"
    input_bg: str = "#FFFFFF"
    input_border: str = "#E3D5C7"
    calc_bg: str = "#FBF7F3"
    calc_border: str = "#EDE2D7"
    line: str = "#D9CBBE"
    note_bg: str = "#FCF9F6"
    grey_text: str = "#6E6259"
    good_bg: str = "#DEEDE3"
    good_text: str = "#26563E"
    warn_bg: str = "#F8EBD3"
    warn_text: str = "#7F5B12"
    bad_bg: str = "#F7DCDE"
    bad_text: str = "#8E2531"
    info_bg: str = "#EDE4EC"
    info_text: str = "#6B3A56"
    accent_soft: str = "#F7E9EF"


PALETTE = Palette()


# ---------------------------------------------------------------------------
# the business
# ---------------------------------------------------------------------------

@dataclass
class Studio:
    name: str = "Rowan & Fern Photography"
    owner: str = "Marisa Calloway"
    email: str = "hello@rowanandfern.example"
    phone: str = "(503) 555-0148"
    website: str = "rowanandfern.example"
    instagram: str = "@rowanandfern"
    city: str = "Portland"
    region: str = "Oregon"
    country: str = "United States"


@dataclass
class Config:
    """Everything the build reads.  One object, passed everywhere."""

    studio: Studio = field(default_factory=Studio)

    author: str = AUTHOR
    password: str = PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True

    currency: str = "$"
    currency_code: str = "USD"

    _today: Optional[_dt.date] = None
    year: Optional[int] = None

    # ---- pricing ----------------------------------------------------------
    default_package: str = "Classic Wedding"
    extra_hour_rate: float = 250.0
    second_shooter_rate: float = 350.0
    assistant_rate: float = 150.0
    engagement_session_price: float = 400.0
    album_base_price: float = 650.0
    mileage_rate: float = 0.67
    free_travel_miles: float = 60.0
    rush_delivery_fee: float = 350.0

    # ---- the payment schedule ---------------------------------------------
    deposit_percent: float = 0.30
    second_percent: float = 0.35
    deposit_days_after_booking: int = 7
    second_payment_days_before: int = 90
    final_payment_days_before: int = 14
    payment_terms_days: int = 14

    # ---- tax ---------------------------------------------------------------
    tax_rate: float = 0.0
    tax_name: str = "Sales tax"
    tax_on_packages: bool = False

    # ---- the workflow ------------------------------------------------------
    preview_days: int = 7
    delivery_days: int = 42
    album_days: int = 60
    gallery_months_live: int = 12
    editing_hours_per_wedding: float = 18.0
    editing_cost_per_hour: float = 35.0
    images_per_hour_culled: int = 400

    # ---- alert windows -----------------------------------------------------
    lead_chase_days: int = 3
    consultation_chase_days: int = 7
    upcoming_days: int = 30
    contract_warn_days: int = 30
    payment_chase_days: int = 7
    review_chase_days: int = 14
    maintenance_warn_days: int = 45
    warranty_warn_days: int = 60

    # ---- targets -----------------------------------------------------------
    target_weddings_year: int = 24
    target_booking_value: float = 2400.0
    target_revenue_year: float = 72000.0
    target_revenue_month: float = 6000.0
    target_profit_margin: float = 0.55
    target_conversion: float = 0.30
    target_rating: float = 4.9
    target_delivery_days: int = 42

    rows_override: Optional[int] = None

    # ---------------------------------------------------------------- dates --
    @property
    def today(self) -> _dt.date:
        return self._today or _dt.date.today()

    @today.setter
    def today(self, value: _dt.date) -> None:
        self._today = value

    @property
    def report_year(self) -> int:
        return self.year or self.today.year

    # ------------------------------------------------------------- formats --
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
        """24 hour, because a wedding timeline that says 7:30 twice
        is how a photographer ends up at the church in the morning."""
        return 'hh:mm'

    # -------------------------------------------------------------- naming --
    @property
    def version(self) -> str:
        return VERSION

    @property
    def product_name(self) -> str:
        return PRODUCT_NAME

    @property
    def listing_title(self) -> str:
        return LISTING_TITLE

    @property
    def studio_name(self) -> str:
        return self.studio.name

    # ------------------------------------------------------------ packages --
    @property
    def package_table(self) -> List[Tuple]:
        return list(PACKAGES)

    @property
    def package_names(self) -> List[str]:
        return [row[0] for row in PACKAGES]

    def package_price(self, name: str) -> float:
        for row in PACKAGES:
            if row[0] == name:
                return float(row[9])
        return 0.0

    # ---------------------------------------------------------------- rows --
    def row_count(self, sheet: str) -> int:
        base = DEFAULT_ROWS.get(sheet, 0)
        if not base or not self.rows_override:
            return base
        anchor = DEFAULT_ROWS[SCALE_ANCHOR]
        scaled = int(round(base * self.rows_override / anchor))
        return max(12, scaled)

    def scale_rows(self, count: int) -> int:
        """Scale a hand written row count the same way a register scales."""
        if not self.rows_override:
            return count
        anchor = DEFAULT_ROWS[SCALE_ANCHOR]
        return max(6, int(round(count * self.rows_override / anchor)))

    @property
    def scaled(self) -> bool:
        return bool(self.rows_override)

    # ----------------------------------------------------------------- ids --
    def rid(self, kind: str, row: int) -> str:
        """The ID a given record row will show, as plain text."""
        prefix, digits = ID_PREFIXES[kind]
        return f"{prefix}{row:0{digits}d}"

    def prefix(self, kind: str) -> str:
        return ID_PREFIXES[kind][0]

    def digits(self, kind: str) -> int:
        return ID_PREFIXES[kind][1]
