"""
Configuration for the Pet Sitting & Dog Walking Business Spreadsheet generator.

Everything that a shop owner may want to re-brand or re-price lives here, so the
workbook can be regenerated for a different store, currency or country without
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
PRODUCT_NAME = "Pet Sitting & Dog Walking Business Spreadsheet"
PRODUCT_SUBTITLE = (
    "Client Booking, Pet Care Log, Invoices, Payments, Mileage & Profit Tracker"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Pet Sitting Business Spreadsheet, Dog Walker Client Booking, "
    "Payments, Mileage and Profit Tracker"
)

#: Password that protects every sheet so formula cells cannot be edited by
#: accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"


# ---------------------------------------------------------------------------
# Colour palette (modern indigo / amber scheme used across every tab)
#
# A contemporary, low-glare palette: deep indigo for structure, amber for
# accent, cool slate greys for calculated cells and soft semantic tints
# (emerald / amber / rose / blue) for the traffic-light columns.  Change a
# value here and every tab, chart, data bar and conditional format follows.
# ---------------------------------------------------------------------------

class Palette:
    ink = "#0F172A"          # slate-900 - titles, darkest text
    primary = "#4338CA"      # indigo-700 - header bands
    primary_mid = "#6366F1"  # indigo-500 - section bands
    primary_soft = "#EEF2FF"  # indigo-50 - light bands / alternating rows
    accent = "#F59E0B"       # amber-500 - accent
    accent_soft = "#FFFBEB"  # amber-50
    input_bg = "#FFFDF5"     # editable cell background (warm cream)
    input_border = "#E4DFD3"
    calc_bg = "#F1F5F9"      # slate-100 - locked formula cell background
    calc_border = "#CBD5E1"  # slate-300
    white = "#FFFFFF"
    grey_text = "#64748B"    # slate-500 - secondary text
    line = "#CBD5E1"         # slate-300 - hairlines
    good_bg = "#D1FAE5"      # emerald-100
    good_text = "#047857"    # emerald-700
    warn_bg = "#FEF3C7"      # amber-100
    warn_text = "#B45309"    # amber-700
    bad_bg = "#FFE4E6"       # rose-100
    bad_text = "#BE123C"     # rose-700
    info_bg = "#DBEAFE"      # blue-100
    info_text = "#1D4ED8"    # blue-700
    note_bg = "#F8FAFC"      # slate-50


# ---------------------------------------------------------------------------
# Row capacity of every register (how many pre-formatted / pre-formulated rows)
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Settings": 0,
    "Lists": 40,
    "Services": 50,
    "Clients": 250,
    "Pets": 250,
    "Bookings": 400,
    "Visits": 400,
    "Visit Log": 400,
    "Health": 200,
    "Health Log": 200,
    "Incidents": 100,
    "Messages": 200,
    "Invoices": 300,
    "Payments": 300,
    "Expenses": 300,
    "Mileage": 300,
    "Staff": 40,
    "Inventory": 120,
    "Holidays": 30,
    "Tasks": 40,
    "Drawings": 24,
}


@dataclass
class BusinessDefaults:
    """Sample values written into the Settings sheet."""

    name: str = "Happy Paws Pet Care"
    owner: str = "Alex Morgan"
    phone: str = "+1 (555) 014 2200"
    email: str = "hello@happypawspetcare.com"
    website: str = "www.happypawspetcare.com"
    address: str = "28 Brookfield Lane"
    city: str = "Springfield"
    state: str = "IL"
    postcode: str = "62704"
    country: str = "United States"
    tax_id: str = "TAX-884 221 905"
    insurance_provider: str = "PetGuard Business Insurance"
    insurance_policy: str = "PG-7741920"
    licence_name: str = "City Pet Care Operator Licence"
    bank_details: str = "Happy Paws Pet Care - Acct 1023 4455 - Routing 021000021"


@dataclass
class Config:
    """All generator options."""

    output_path: str = "output/Pet Sitting and Dog Walking Business Spreadsheet.xlsx"

    # Branding / document properties
    author: str = AUTHOR
    company: str = AUTHOR
    product_name: str = PRODUCT_NAME
    product_subtitle: str = PRODUCT_SUBTITLE
    version: str = PRODUCT_VERSION
    release_date: str = "2026-10-11"

    # Protection
    password: str = FORMULA_PASSWORD
    protect_sheets: bool = True

    # Formats
    currency_symbol: str = "$"
    currency_code: str = "USD"
    date_format: str = "dd-mmm-yyyy"
    time_format: str = "h:mm AM/PM"
    distance_unit: str = "km"

    # Business / pricing defaults pre-filled on the Settings tab
    business: BusinessDefaults = field(default_factory=BusinessDefaults)
    tax_name: str = "Sales Tax"
    tax_registered: str = "Yes"
    tax_rate: float = 0.08
    prices_include_tax: str = "No"
    payment_terms_days: int = 7
    deposit_percent: float = 0.25
    late_fee_percent: float = 0.05
    invoice_prefix: str = "INV-"
    invoice_start_number: int = 1001
    client_prefix: str = "CL-"
    pet_prefix: str = "PET-"
    booking_prefix: str = "BK-"
    mileage_rate: float = 0.67
    travel_fee_per_unit: float = 0.80
    free_travel_distance: float = 8.0
    holiday_surcharge: float = 0.25
    weekend_surcharge: float = 0.10
    emergency_fee: float = 15.0
    last_minute_days: int = 2
    extra_pet_fee: float = 7.5
    loyalty_discount: float = 0.05
    loyalty_threshold: int = 20
    staff_cost_rate: float = 18.0
    tax_reserve_percent: float = 0.25
    reminder_lead_days: int = 3
    vaccination_alert_days: int = 30
    inactive_client_days: int = 60
    follow_up_days: int = 5
    expiry_alert_days: int = 30
    default_visit_minutes: int = 30
    travel_time_minutes: int = 15
    day_start: str = "07:00"
    day_end: str = "19:00"

    # Content switches
    include_sample_data: bool = True
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    def scale_rows(self, booking_rows: int) -> None:
        """Scale every register in place so Bookings holds `booking_rows`."""
        base = DEFAULT_ROWS["Bookings"]
        factor = max(0.05, float(booking_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        """Return a copy with every register scaled (used by --rows-scale)."""
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings derived from the chosen currency ------------------
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'"{s}"#,##0.00;[Red]-"{s}"#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'"{s}"#,##0;[Red]-"{s}"#,##0'
