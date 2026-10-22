"""
Configuration for the Salon Business Management System.

Everything a buyer may want to re-brand lives here, so the workbook can
be regenerated for a different shop, currency or capacity without
touching any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Salon Business Management System"
PRODUCT_SUBTITLE = (
    "Appointments, Client CRM, Services, Sales, Commissions, Payroll, "
    "Inventory, Profit & Loss and Reports for Excel and Google Sheets"
)
PRODUCT_VERSION = "1.0.0"

PRODUCT_LISTING_TITLE = (
    "Salon Business Management Spreadsheet, Appointment Book & Client CRM, "
    "Commission & Payroll Calculator, Inventory & Profit Loss Tracker for "
    "Excel and Google Sheets"
)

#: Password that protects every sheet so formula cells cannot be edited
#: by accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

DISCLAIMER = (
    "This spreadsheet is a business organisation and reporting tool. It is "
    "not accounting, payroll, legal or tax advice, and it does not replace "
    "your accountant or your local regulations. Tax, commission, tip and "
    "budget figures are estimates produced from the numbers you type in; "
    "rates and rules are yours to set and edit on the Settings tab. A "
    "spreadsheet organises bookings but does not send confirmations, text "
    "reminders or synchronise with salon booking platforms. No outcome of "
    "any kind is promised."
)
DISCLAIMER_SHORT = (
    "A business-organising tool - not accounting, payroll or tax advice."
)

#: The twenty tabs, in workbook order.
SHEET_TABS = [
    "1 Start Here",
    "2 Dashboard",
    "3 Appointment Planner",
    "4 Client CRM",
    "5 Services & Pricing",
    "6 Sales & Transactions",
    "7 Payments & Deposits",
    "8 Staff Management",
    "9 Staff Commissions",
    "10 Payroll & Tips",
    "11 Expenses",
    "12 Profit & Loss",
    "13 Product Inventory",
    "14 Suppliers & Purchases",
    "15 Marketing & Promotions",
    "16 Client Loyalty",
    "17 Goals & Budget",
    "18 Business Analytics",
    "19 Weekly & Monthly Reports",
    "20 Settings & Lists",
]

# ---------------------------------------------------------------------------
# Lists that feed the drop downs (all editable on 20 Settings & Lists)
# ---------------------------------------------------------------------------

APPOINTMENT_STATUSES = ["Booked", "Confirmed", "Completed", "Cancelled",
                        "No-show"]
PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer", "Gift Certificate",
                   "Other"]
PAYMENT_KINDS = ["Payment", "Deposit", "Refund"]
BOOKING_CHANNELS = ["Instagram", "Facebook", "Google", "Walk-in",
                    "Referral", "Website", "Phone", "Other"]
SERVICE_CATEGORIES = ["Hair", "Nails", "Lashes", "Brows", "Skincare",
                      "Waxing", "Other"]
EXPENSE_CATEGORIES = ["Rent", "Utilities", "Supplies", "Product Cost",
                      "Marketing", "Software", "Equipment", "Insurance",
                      "Training", "Other"]
STAFF_STATUSES = ["Active", "On Leave", "Left"]
STAFF_TYPES = ["Employee", "Contractor"]
COMMISSION_METHODS = ["Percentage", "Category", "Flat"]
TX_TYPES = ["Service", "Retail"]
PURCHASE_STATUSES = ["Ordered", "Received", "Cancelled"]
CONSENT = ["Yes", "No"]
PREF_CONTACT = ["Phone", "Text", "Email", "Any"]
RECURRING = ["Monthly", "Quarterly", "Annual", "One-time"]
PRODUCT_CATEGORIES = ["Retail", "Backbar"]
CLIENT_TIERS = ["Bronze", "Silver", "Gold"]

#: Service categories that carry their own commission rate when a staff
#: member is paid on the "Category" method (rate table on Settings).
CATEGORY_COMMISSION_DEFAULT = {
    "Hair": 0.45,
    "Nails": 0.50,
    "Lashes": 0.50,
    "Brows": 0.45,
    "Skincare": 0.40,
    "Waxing": 0.45,
    "Other": 0.40,
}

# ---------------------------------------------------------------------------
# Colours - salon palette: deep plum, brushed gold, warm porcelain
# ---------------------------------------------------------------------------

class Palette:
    ink = "#241F26"           # near-black plum - titles
    primary = "#6D2E4F"       # deep plum headers
    primary_mid = "#96587A"   # section bands
    primary_soft = "#F2E4EC"  # light band / alternating rows
    accent = "#B98A2F"        # brushed gold accent
    accent_soft = "#F6EBD6"
    input_bg = "#FFFCF7"      # editable cell background (porcelain)
    input_border = "#E0D3C0"
    calc_bg = "#EFEAEE"       # locked formula cell background
    calc_border = "#DCD3DA"
    white = "#FFFFFF"
    grey_text = "#5F5760"
    line = "#D8CFD6"
    good_bg = "#DCEBD8"
    good_text = "#2F5A2B"
    warn_bg = "#FDEDD2"
    warn_text = "#8A5A00"
    bad_bg = "#F8DAD9"
    bad_text = "#9C2A24"
    info_bg = "#E2E6F3"
    info_text = "#3A4578"
    note_bg = "#F8F6F4"


# ---------------------------------------------------------------------------
# Row capacity of every register
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "3 Appointment Planner": 400,
    "4 Client CRM": 250,
    "5 Services & Pricing": 80,
    "6 Sales & Transactions": 600,
    "7 Payments & Deposits": 600,
    "8 Staff Management": 30,
    "10 Payroll & Tips": 300,
    "11 Expenses": 400,
    "13 Product Inventory": 150,
    "14 Suppliers & Purchases": 150,
    "15 Marketing & Promotions": 80,
    "16 Client Loyalty": 250,
    "17 Goals & Budget": 24,
}

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

    # Business defaults (written to Settings, all editable) -----------------
    salon_name: str = "Bloom & Blade Studio"
    owner_name: str = "Ava Reyes"
    tax_rate: float = 0.00            # configurable, region dependent
    tax_reserve_rate: float = 0.25    # share of profit set aside
    payroll_tax_rate: float = 0.10    # employer-side reserve
    card_fee_rate: float = 0.022
    cash_fee_rate: float = 0.00
    bank_fee_rate: float = 0.005
    other_fee_rate: float = 0.01
    points_per_visit: float = 10.0
    reward_threshold: float = 100.0
    referral_reward: float = 10.0
    rebook_days: int = 42
    flat_commission: float = 18.0     # per completed service, Flat method

    # Behaviour -------------------------------------------------------------
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    def scale_rows(self, sales_rows: int) -> None:
        """Scale every register in place so Sales holds N rows."""
        base = DEFAULT_ROWS["6 Sales & Transactions"]
        factor = max(0.02, float(sales_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings --------------------------------------------------
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
