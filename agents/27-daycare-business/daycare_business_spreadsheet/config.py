"""
Configuration for the Daycare & Childcare Business Management Spreadsheet.

Everything a childcare provider might want to change - the currency, the
age groups, the staff-to-child ratios, the fee basis, the late pickup
charge, every drop-down list - lives in this one module, so the workbook
can be regenerated for a different country, licence or price list
without touching a single sheet.

Nothing here assumes one country's licensing rules.  Ratios, age bands,
tax, subsidy handling and document types are all settings, not
hard-coded constants.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Daycare & Childcare Business Management Spreadsheet"
PRODUCT_SUBTITLE = (
    "Enrollment, Attendance, Tuition, Invoices, Daily Reports, Staff, "
    "Classrooms and Profit in one workbook"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Daycare Business Spreadsheet, Childcare Management System, "
    "Enrollment Attendance Tuition Invoice Staff and Parent Tracker, "
    "Home Daycare and Preschool Excel Template"
)

#: Password that protects every sheet so formula cells cannot be edited
#: by accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: The workbook organises a childcare business.  It is not a medical
#: record, not a licensing compliance system and not an accountant.
DISCLAIMER = (
    "This workbook is a business organising tool for a childcare "
    "setting. It is not accounting, payroll, legal, medical or "
    "licensing advice, it does not file or submit anything, and it "
    "does not make you compliant with any regulator. It does not send "
    "messages to parents and it does not connect to any childcare app "
    "or payment provider. Allergy, medication and incident pages are "
    "working notes for your own staff - they do not replace your "
    "setting's medical records, medication protocols, safeguarding "
    "procedures or emergency plans. Child and family records are "
    "sensitive personal data: keep this file somewhere access "
    "controlled and backed up, and set the ratios, age bands and "
    "document types to match the rules that actually apply where you "
    "operate."
)

#: Short line printed on the pages that carry the most sensitive data.
PRIVACY_NOTE = (
    "Sensitive personal data. Keep this file in a password protected, "
    "access controlled location, share it only with staff who need it, "
    "and delete records when your retention policy says to."
)


# ---------------------------------------------------------------------------
# Vocabularies - every one of these becomes a drop-down on Settings & Lists
# ---------------------------------------------------------------------------

#: The programmes a setting can offer.
PROGRAM_TYPES = [
    "Infant", "Young toddler", "Toddler", "Preschool", "Pre-K",
    "Kindergarten", "Before school", "After school", "Before & after",
    "Drop-in", "Holiday club", "Summer camp",
]

#: Where a child is up to with you.
ENROLLMENT_STATUSES = [
    "Enquiry", "Waitlisted", "Pending start", "Active", "On hold",
    "Notice given", "Withdrawn", "Graduated",
]

#: Statuses that mean the child currently occupies a seat.
OCCUPYING_STATUSES = ["Active", "On hold", "Notice given"]

#: How many days a week, and which part of the day.
SCHEDULE_TYPES = [
    "Full-time 5 days", "4 days", "3 days", "2 days", "1 day",
    "Half day 5 days", "Half day 3 days", "Mornings only",
    "Afternoons only", "Before school", "After school",
    "Before & after", "Drop-in", "Flexible hours",
]

#: What happened on the day.
ATTENDANCE_STATUSES = [
    "Present", "Late", "Early pickup", "Absent - sick",
    "Absent - family", "Absent - unexplained", "Holiday - child",
    "Public holiday", "Centre closed", "Snow day", "Not scheduled",
]

#: Attendance statuses that mean the child was in the building.
PRESENT_STATUSES = ["Present", "Late", "Early pickup"]

#: Statuses that mean a scheduled day was missed.
ABSENT_STATUSES = ["Absent - sick", "Absent - family",
                   "Absent - unexplained", "Holiday - child"]

#: Statuses where nobody was expected, so they do not count against the
#: attendance percentage.
NON_SESSION_STATUSES = ["Public holiday", "Centre closed", "Snow day",
                        "Not scheduled"]

#: How a family's tuition is worked out.  The owner picks per child -
#: nothing is assumed.
BILLING_BASES = [
    "Weekly rate", "Monthly rate", "Daily rate", "Hourly rate",
    "Per session", "Fortnightly rate", "Term rate", "No charge",
]

#: What a charge line is for.
FEE_TYPES = [
    "Tuition", "Registration fee", "Enrollment deposit",
    "Late pickup fee", "Late payment fee", "Meal fee", "Snack fee",
    "Transport fee", "Activity fee", "Field trip", "Supply fee",
    "Nappy & wipes fee", "Holiday club", "Extra day", "Extra hours",
    "Sibling discount", "Staff discount", "Promotional discount",
    "Subsidy credit", "Scholarship credit", "Goodwill credit",
    "Other charge",
]

#: Fee types that reduce the bill rather than add to it.  Entered as a
#: positive number and subtracted, so a parent never sees a minus sign.
CREDIT_FEE_TYPES = [
    "Sibling discount", "Staff discount", "Promotional discount",
    "Subsidy credit", "Scholarship credit", "Goodwill credit",
]

#: Where a charge came from - handy when a parent queries a bill.
CHARGE_SOURCES = [
    "Contracted schedule", "Extra day booked", "Extra hours",
    "Late pickup", "Meals", "Transport", "Activity or trip",
    "One-off request", "Registration", "Annual increase",
    "Manual adjustment",
]

#: Money movements on the Invoices & Receipts ledger.
LEDGER_TYPES = ["Invoice", "Payment", "Credit note", "Refund",
                "Write-off"]

#: Ledger types that increase what a family owes.
CHARGE_TYPES = ["Invoice", "Refund"]

#: How a family pays.
PAYMENT_METHODS = [
    "Cash", "Card", "Bank transfer", "Direct debit", "Standing order",
    "Cheque", "Mobile wallet", "Online payment", "Childcare voucher",
    "Government subsidy", "Employer paid", "Other",
]

#: Where an invoice is up to.
INVOICE_STATUSES = ["Draft", "Sent", "Part paid", "Paid", "Overdue",
                    "Written off", "Cancelled"]

#: Who a guardian is to the child.
RELATIONSHIPS = [
    "Mother", "Father", "Step-mother", "Step-father", "Grandmother",
    "Grandfather", "Legal guardian", "Foster carer", "Aunt", "Uncle",
    "Adult sibling", "Family friend", "Social worker", "Other",
]

#: How a family prefers to hear from you.
CONTACT_METHODS = [
    "Phone call", "Text message", "Email", "WhatsApp", "App message",
    "In person at pickup", "Paper note home", "Do not contact",
]

#: How a child seemed today.
MOODS = ["Happy", "Settled", "Playful", "Quiet", "Tired", "Clingy",
         "Tearful", "Unsettled", "Unwell", "Excited", "Frustrated"]

#: Sittings on the meal tracker.
MEAL_SITTINGS = ["Breakfast", "Morning snack", "Lunch",
                 "Afternoon snack", "Tea", "Dinner", "Bottle",
                 "Drink only"]

#: How much of it went in.
EATEN_AMOUNTS = ["All", "Most", "About half", "A little", "None",
                 "Refused", "Not offered", "Brought own"]

#: Dietary requirements and restrictions.
DIET_TYPES = [
    "No restrictions", "Vegetarian", "Vegan", "Halal", "Kosher",
    "Dairy free", "Gluten free", "Nut free", "Egg free", "Soy free",
    "Shellfish free", "Low sugar", "Texture modified", "Allergy plan",
    "Other - see notes",
]

#: How serious an allergy is - drives the colour coding.
ALLERGY_SEVERITY = ["None recorded", "Mild", "Moderate", "Severe",
                    "Anaphylaxis risk"]

#: What kind of medical record a row is.
MEDICAL_RECORD_TYPES = [
    "Allergy", "Intolerance", "Asthma", "Epilepsy", "Diabetes",
    "Eczema", "Medical condition", "Regular medication",
    "As-needed medication", "Dietary requirement", "Mobility need",
    "Additional need", "Immunisation", "Medication given",
    "Medication refused", "Other",
]

#: Medical rows that are an event rather than a standing profile.  The
#: medication administration log lives in the same register, flagged by
#: its record type, so a dose is always filed next to the plan it
#: belongs to and nothing has to be cross-referenced by hand.
MEDICAL_EVENT_TYPES = ["Medication given", "Medication refused"]

#: What happened.
INCIDENT_CATEGORIES = [
    "Minor injury", "Fall", "Bump to head", "Cut or graze", "Bruise",
    "Bite", "Scratch", "Allergic reaction", "Asthma episode",
    "Illness at the setting", "Medication error", "Behaviour incident",
    "Near miss", "Property damage", "Lost or found property",
    "Safeguarding concern", "Other",
]

#: Where it happened.
INCIDENT_LOCATIONS = [
    "Infant room", "Toddler room", "Preschool room", "Classroom",
    "Playground", "Garden", "Hallway", "Bathroom", "Nap room",
    "Kitchen", "Dining area", "Entrance", "Car park", "Outing",
    "Minibus", "Other",
]

#: How badly hurt, if at all.
INCIDENT_SEVERITY = ["No injury", "Minor", "Moderate", "Serious",
                     "Emergency services called"]

#: Jobs in a childcare setting.
STAFF_ROLES = [
    "Owner / Director", "Centre manager", "Deputy manager",
    "Room leader", "Lead teacher", "Teacher", "Assistant teacher",
    "Early years practitioner", "Infant room staff", "Floater",
    "Apprentice / trainee", "Substitute / supply", "Cook",
    "Kitchen assistant", "Cleaner", "Administrator", "Bus driver",
    "Volunteer", "Other",
]

#: Where a staff member is up to.
EMPLOYMENT_STATUSES = ["Active", "Probation", "On leave",
                       "Casual / bank", "Notice period", "Inactive",
                       "Left"]

#: How they are paid.
PAY_TYPES = ["Hourly", "Salary", "Daily rate", "Contractor",
             "Volunteer - unpaid"]

#: Shifts on the rota.
SHIFT_TYPES = ["Opening", "Early", "Morning", "Mid", "Afternoon",
               "Late", "Closing", "Full day", "Split shift",
               "Sub cover", "Training", "Admin", "Off", "Leave"]

#: Why somebody is not in.
LEAVE_TYPES = ["Annual leave", "Sick leave", "Unpaid leave",
               "Parental leave", "Compassionate leave", "Training",
               "Public holiday", "TOIL"]

#: How often a pay run happens.
PAY_PERIODS = ["Weekly", "Fortnightly", "Four weekly", "Monthly",
               "Twice monthly", "One off"]

#: Where the money goes, in the order a profit and loss wants it.
EXPENSE_CATEGORIES = [
    "Rent", "Mortgage & loan", "Utilities", "Food & groceries",
    "Nappies & hygiene", "Cleaning supplies", "Toys & learning materials",
    "Educational supplies", "Arts & crafts", "Furniture & equipment",
    "Staff wages", "Payroll taxes & on-costs", "Staff benefits",
    "Recruitment", "Training & qualifications", "Insurance",
    "Licensing & registration", "Inspection & compliance",
    "Repairs & maintenance", "Transport & vehicle", "Field trips",
    "Marketing & advertising", "Software & subscriptions",
    "Telephone & internet", "Office & admin", "Bank & card fees",
    "Professional fees", "Waste & recycling", "Security",
    "Other expense",
]

#: Categories whose cost is already on the Payroll Tracker.  The profit
#: and loss skips them unless the owner says otherwise on Settings.
PAYROLL_EXPENSE_CATEGORIES = ["Staff wages", "Payroll taxes & on-costs"]

#: What is in the store cupboard.
SUPPLY_CATEGORIES = [
    "Food & kitchen", "Drinks & formula", "Cleaning & sanitising",
    "Nappies & wipes", "Hygiene & bathroom", "Arts & crafts",
    "Learning materials", "Books", "Toys", "Outdoor equipment",
    "Office & stationery", "First aid", "Safety & PPE",
    "Linen & bedding", "Other supplies",
]

#: Paperwork a setting has to keep on top of.
DOCUMENT_TYPES = [
    "Enrollment agreement", "Emergency contact form",
    "Medical authorization", "Immunisation record",
    "Photo & video consent", "Pickup authorization",
    "Allergy action plan", "Medication consent",
    "Parent handbook acknowledgment", "Field trip consent",
    "Sunscreen consent", "Birth certificate sighted",
    "Subsidy paperwork", "Custody / court order",
    "Staff contract", "Staff ID check", "Background check",
    "First aid certificate", "CPR certificate",
    "Child protection training", "Food handling certificate",
    "Qualification certificate", "Reference check",
    "Business licence", "Insurance policy", "Fire inspection",
    "Health inspection", "Risk assessment", "Policy review", "Other",
]

#: Who a document belongs to.
DOCUMENT_HOLDERS = ["Child", "Parent / family", "Staff", "Business"]

#: Where a document is up to.
DOCUMENT_STATUSES = ["Not started", "Requested", "Chased", "Received",
                     "Signed", "On file", "Expired", "Not required"]

#: What a conversation with a parent was about.
COMM_CATEGORIES = [
    "General update", "Settling in", "Attendance", "Late pickup",
    "Behaviour", "Health & illness", "Medication", "Allergy",
    "Accident / incident", "Billing & fees", "Enrollment change",
    "Schedule change", "Meeting request", "Progress update",
    "Complaint", "Compliment", "Policy notice", "Closure notice",
    "Photo consent", "Other",
]

#: Where a conversation is up to.
COMM_STATUSES = ["Open", "Waiting on parent", "Waiting on us",
                 "Meeting booked", "Closed", "No reply needed"]

#: How a family found you.
INQUIRY_SOURCES = [
    "Google search", "Google Maps", "Facebook", "Instagram",
    "Word of mouth", "Parent referral", "Staff referral",
    "Sign outside", "Flyer or leaflet", "Local directory",
    "Childcare website", "Employer scheme", "School referral",
    "Walk in", "Returning family", "Sibling already here", "Other",
]

#: Where an enquiry is up to on the waitlist.
WAITLIST_STATUSES = [
    "New enquiry", "Information sent", "Tour booked", "Toured",
    "Place offered", "Offer accepted", "Offer declined", "Enrolled",
    "Waiting - no space", "Waiting - future date", "Lost", "Withdrawn",
]

#: Priority on the waitlist.
WAITLIST_PRIORITY = ["Sibling", "Staff child", "Returning family",
                     "Standard", "Low"]

#: Why a family left.
LEAVING_REASONS = [
    "Aged out / started school", "Moved away", "Parent left work",
    "Cost", "Changed provider", "Hours did not suit",
    "Parental leave", "Unhappy with service", "Not stated", "Other",
]

#: How often a recurring cost comes round.
FREQUENCIES = ["One off", "Weekly", "Fortnightly", "Four weekly",
               "Monthly", "Quarterly", "Twice a year", "Yearly"]

#: Months per occurrence, used to turn any frequency into a monthly cost.
FREQUENCY_MONTHS = {
    "Weekly": 52.0 / 12.0,
    "Fortnightly": 26.0 / 12.0,
    "Four weekly": 13.0 / 12.0,
    "Monthly": 1.0,
    "Quarterly": 1.0 / 3.0,
    "Twice a year": 1.0 / 6.0,
    "Yearly": 1.0 / 12.0,
}

#: Offered because some settings record it and some deliberately do not.
GENDERS = ["Girl", "Boy", "Prefer not to say", "Not recorded"]

#: Who started the conversation.
COMM_DIRECTIONS = ["Incoming", "Outgoing"]

#: Where a classroom is up to.
ROOM_STATUSES = ["Open", "Full", "Planned", "Closed", "Seasonal"]

#: Nappy / toileting entries on the daily report.
TOILETING_OPTIONS = ["Nappy - wet", "Nappy - soiled", "Nappy - dry",
                     "Potty - success", "Potty - tried", "Toilet",
                     "Accident", "Not applicable"]


# ---------------------------------------------------------------------------
# Age bands and the staff-to-child ratios that go with them.
#
# These are the single most country-specific numbers in the whole
# product, which is exactly why they are a table on the Settings tab
# rather than a constant in a formula.  Defaults are a middle-of-the-road
# starting point, nothing more.
# ---------------------------------------------------------------------------

#: (label, from months, to months, children per adult, max group size)
AGE_BANDS = [
    ("Infant", 0, 12, 4, 8),
    ("Young toddler", 12, 24, 5, 10),
    ("Toddler", 24, 36, 6, 12),
    ("Preschool", 36, 48, 10, 20),
    ("Pre-K", 48, 60, 12, 22),
    ("School age", 60, 156, 15, 30),
]


# ---------------------------------------------------------------------------
# ID prefixes.  Each one is an editable field on Settings with a defined
# name, so a setting can renumber its own records without touching a
# formula: (label, default, defined name, digits).
# ---------------------------------------------------------------------------

ID_PREFIXES = [
    ("Child IDs", "CHD-", "ChildPrefix", 4),
    ("Family IDs", "FAM-", "FamilyPrefix", 4),
    ("Waitlist IDs", "WL-", "WaitlistPrefix", 4),
    ("Attendance IDs", "ATT-", "AttendancePrefix", 5),
    ("Charge IDs", "FEE-", "FeePrefix", 5),
    ("Invoice IDs", "INV-", "InvoicePrefix", 5),
    ("Receipt IDs", "RCP-", "ReceiptPrefix", 5),
    ("Daily report IDs", "DR-", "ReportPrefix", 5),
    ("Meal log IDs", "MEA-", "MealPrefix", 5),
    ("Medical record IDs", "MED-", "MedicalPrefix", 4),
    ("Incident IDs", "INC-", "IncidentPrefix", 4),
    ("Staff IDs", "EMP-", "StaffPrefix", 3),
    ("Shift IDs", "SHF-", "ShiftPrefix", 5),
    ("Pay run IDs", "PAY-", "PayrollPrefix", 4),
    ("Classroom IDs", "ROOM-", "ClassroomPrefix", 2),
    ("Expense IDs", "EXP-", "ExpensePrefix", 4),
    ("Supply IDs", "SUP-", "SupplyPrefix", 3),
    ("Message IDs", "MSG-", "MessagePrefix", 4),
    ("Document IDs", "DOC-", "DocumentPrefix", 4),
]

#: defined name -> (prefix, digits), for the demo data generator.
PREFIX_BY_NAME = {name: (prefix, digits)
                  for _label, prefix, name, digits in ID_PREFIXES}


def rid(kind: str, number: int) -> str:
    """Build the ID the workbook itself will generate on row `number`.

    ``rid("Child", 7)`` -> ``"CHD-0007"``.  The demo data has to agree
    with the ID formulas exactly, because the IDs are what tie the
    twenty-three tabs together.
    """
    prefix, digits = PREFIX_BY_NAME[f"{kind}Prefix"]
    return f"{prefix}{number:0{digits}d}"


#: The twelve month names used by every monthly roll-up.
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December"]

#: Weekday names, Monday first.
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# Colours - a childcare palette: teal, sky, warm amber, soft cream
# ---------------------------------------------------------------------------

class Palette:
    ink = "#1E333C"            # near black teal - titles
    deep = "#14505F"           # deep teal - money and staff tabs
    primary = "#1F6F8B"        # teal headers
    primary_mid = "#4D96AE"    # section bands
    primary_soft = "#E7F2F6"   # light band / alternating rows
    accent = "#E09B2D"         # warm amber accent
    accent_soft = "#FDF3E0"
    input_bg = "#FFFFFF"       # editable cell background
    input_border = "#D3E4EB"
    calc_bg = "#F5FAFC"        # locked formula cell background
    calc_border = "#E3EFF4"
    white = "#FFFFFF"
    grey_text = "#5B6B73"
    line = "#C9DDE5"
    good_bg = "#DBEDD7"
    good_text = "#2C5A28"
    warn_bg = "#FDEDD2"
    warn_text = "#8A5A00"
    bad_bg = "#F8DAD9"
    bad_text = "#9C2A24"
    info_bg = "#E2E7F3"
    info_text = "#36447A"
    note_bg = "#F7FBFC"


# ---------------------------------------------------------------------------
# Row capacity of every register
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Dashboard": 0,
    "Getting Started": 0,
    "Settings & Lists": 0,
    "Child Enrollment": 150,
    "Parent Database": 200,
    "Waitlist": 120,
    "Attendance": 2000,
    "Tuition & Fees": 700,
    "Invoices & Receipts": 700,
    "Daily Reports": 600,
    "Meal Tracker": 600,
    "Allergy & Medical": 180,
    "Incident Reports": 150,
    "Staff Database": 60,
    "Staff Schedule": 750,
    "Payroll Tracker": 350,
    "Classroom Management": 30,
    "Expense Tracker": 500,
    "Supply Inventory": 180,
    "Parent Communication": 350,
    "Document Tracker": 500,
    "Monthly Reports": 0,
    "Annual Reports": 0,
}

#: The register the `--rows` switch scales everything else against.
SCALE_ANCHOR = "Attendance"


@dataclass
class CentreDefaults:
    """Sample values written into the business profile on Settings."""

    name: str = "Little Acorns Childcare"
    owner: str = "Marianne Okafor"
    brand: str = "Little Acorns"
    email: str = "hello@littleacorns.example"
    phone: str = "(614) 555 0142"
    address: str = "47 Willow Grove, Columbus, OH 43206"
    website: str = "littleacorns.example"
    licence: str = "OH-CC-2017-04418"
    tax_id: str = "EIN 84-3920117"
    opening_hours: str = "Mon-Fri 7:00am - 6:00pm"
    tagline: str = "A small, warm place to grow since 2017"


# ---------------------------------------------------------------------------
# The configuration object every sheet module reads
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """Everything the generator needs to know to write one workbook."""

    author: str = AUTHOR
    product_name: str = PRODUCT_NAME
    product_subtitle: str = PRODUCT_SUBTITLE
    listing_title: str = PRODUCT_LISTING_TITLE
    version: str = PRODUCT_VERSION
    password: str = FORMULA_PASSWORD
    protect_sheets: bool = True
    include_sample_data: bool = True

    # Formatting ------------------------------------------------------------
    currency_symbol: str = "$"
    currency_code: str = "USD"
    date_format: str = "dd-mmm-yyyy"
    time_format: str = "h:mm AM/PM"
    decimals: int = 2
    week_start: str = "Monday"

    # The setting's own profile, pre-filled on Settings ---------------------
    centre: CentreDefaults = field(default_factory=CentreDefaults)
    plan_year: int = 0                   # 0 = the year of `today`

    # Opening hours and capacity -------------------------------------------
    open_hour: float = 7.0
    close_hour: float = 18.0
    open_days: int = 5                   # sessions a week
    licensed_capacity: int = 42          # the licence number on the wall
    classrooms: int = 4
    weeks_open: int = 50                 # trading weeks in a year
    term_weeks: int = 13                 # weeks in a term, for term fees

    # Fees ------------------------------------------------------------------
    default_billing_basis: str = "Weekly rate"
    full_time_week: float = 285.00
    part_time_day: float = 68.00
    hourly_rate_fee: float = 11.50
    registration_fee: float = 95.00
    enrollment_deposit: float = 200.00
    meal_fee_day: float = 6.50
    transport_fee_week: float = 25.00
    sibling_discount: float = 0.10       # second and later child
    staff_discount: float = 0.30
    late_pickup_grace: int = 10          # minutes before the clock starts
    late_pickup_fee: float = 15.00       # the first block
    late_pickup_per: float = 1.00        # per minute after the block
    late_pickup_block: int = 15          # minutes in the first block
    late_payment_fee: float = 25.00
    payment_terms_days: int = 7          # invoice due this many days out
    invoice_day: int = 1                 # day of the month you invoice
    tax_rate: float = 0.0                # childcare is often exempt
    tax_on_tuition: str = "No"
    tax_on_extras: str = "No"
    tax_registered: str = "No"
    card_fee_percent: float = 0.029
    card_fee_fixed: float = 0.30

    # Staff pay -------------------------------------------------------------
    default_pay_type: str = "Hourly"
    default_hourly: float = 16.50
    overtime_after_hours: float = 40.0   # hours a week before overtime
    overtime_multiplier: float = 1.5
    payroll_burden: float = 0.14         # employer tax, insurance, cover
    paid_break_minutes: int = 0          # unpaid break length, in minutes
    break_minutes: int = 30

    # Ratios and capacity ---------------------------------------------------
    ratio_warning_percent: float = 0.90  # flag a room at 90% full
    include_staff_children: str = "Yes"

    # Targets the dashboard measures against --------------------------------
    monthly_revenue_target: float = 42000.0
    annual_revenue_target: float = 504000.0
    monthly_profit_target: float = 6000.0
    target_occupancy: float = 0.90
    target_attendance: float = 0.92
    target_collection: float = 0.97      # share of billings collected
    enrollment_target: int = 40
    # the example setting is smaller than the defaults assume, so the
    # demo file carries targets it can actually be measured against
    sample_monthly_revenue_target: float = 30000.0
    sample_annual_revenue_target: float = 360000.0
    sample_monthly_profit_target: float = 3000.0
    sample_enrollment_target: int = 34

    # Supplies --------------------------------------------------------------
    reorder_weeks: float = 3.0
    stock_warning_weeks: float = 1.5

    # Reminders -------------------------------------------------------------
    document_warning_days: int = 45      # amber before an expiry
    document_urgent_days: int = 14
    birthday_window_days: int = 30
    absence_chase_days: int = 3          # unexplained absences in a row
    overdue_chase_days: int = 7

    # Behaviour -------------------------------------------------------------
    top_rows: int = 5                    # size of the "top / best" tables
    months_shown: int = 12
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    @property
    def year(self) -> int:
        return self.plan_year or self.today.year

    @property
    def revenue_target_month(self) -> float:
        """Monthly revenue target, scaled to whoever is reading it."""
        return (self.sample_monthly_revenue_target
                if self.include_sample_data else self.monthly_revenue_target)

    @property
    def revenue_target_year(self) -> float:
        return (self.sample_annual_revenue_target
                if self.include_sample_data else self.annual_revenue_target)

    @property
    def profit_target_month(self) -> float:
        return (self.sample_monthly_profit_target
                if self.include_sample_data else self.monthly_profit_target)

    @property
    def enrollment_goal(self) -> int:
        return (self.sample_enrollment_target
                if self.include_sample_data else self.enrollment_target)

    @property
    def open_hours_day(self) -> float:
        return round(self.close_hour - self.open_hour, 2)

    @property
    def labor_cost_per_hour(self) -> float:
        """An hour of paid time once employer on-costs are added."""
        return round(self.default_hourly * (1 + self.payroll_burden), 2)

    @property
    def capacity_weeks_year(self) -> int:
        """Licensed child-weeks available in a year - the occupancy base."""
        return int(self.licensed_capacity * self.weeks_open)

    def scale_rows(self, main_rows: int) -> None:
        """Scale every register in place so Attendance holds N rows."""
        base = DEFAULT_ROWS[SCALE_ANCHOR]
        factor = max(0.02, float(main_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        """Return a copy with every register scaled."""
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings derived from the chosen currency ----------------
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.00;[Red]-{s}#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0;[Red]-{s}#,##0'

    @property
    def money_format_4(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.0000;[Red]-{s}#,##0.0000'
