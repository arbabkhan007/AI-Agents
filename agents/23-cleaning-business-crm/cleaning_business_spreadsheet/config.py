"""
Configuration for the Cleaning Business CRM & Pricing Calculator.

Everything a shop owner may want to re-brand lives here, so the workbook
can be regenerated for a different company, currency, country or pricing
model without touching any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Cleaning Business CRM & Pricing Calculator"
PRODUCT_SUBTITLE = (
    "Client CRM, Job Scheduler, Quote Calculator, Employee Planner, "
    "Invoices, Expenses & Profit Dashboard"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Cleaning Business Spreadsheet, Cleaning Service CRM, Job Scheduler, "
    "Quote Calculator, Employee Planner, Invoices, Expenses and Profit "
    "Dashboard"
)

#: Password that protects every sheet so formula cells cannot be edited by
#: accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: The job statuses that drive the scheduler, the dashboard and the alerts.
JOB_STATUSES = ["Enquiry", "Booked", "Confirmed", "In progress",
                "Completed", "Invoiced", "Cancelled", "No access"]

#: Statuses that mean the work actually happened.
DONE_STATUSES = ["Completed", "Invoiced"]

#: Quote statuses, in the order a quote moves through them.
QUOTE_STATUSES = ["Draft", "Sent", "Followed up", "Accepted", "Declined",
                  "Expired"]

#: Invoice statuses.
INVOICE_STATUSES = ["Draft", "Sent", "Part paid", "Paid", "Overdue",
                    "Written off"]

#: How often a recurring clean can repeat.
FREQUENCIES = ["One-off", "Weekly", "Fortnightly", "Every 3 weeks",
               "Monthly", "Quarterly", "Twice a week"]

#: Multiplier applied to the standard price for each frequency - regular
#: work is cheaper per visit because the place never gets badly dirty.
FREQUENCY_FACTORS = {
    "One-off": 1.00,
    "Weekly": 0.85,
    "Fortnightly": 0.90,
    "Every 3 weeks": 0.95,
    "Monthly": 1.00,
    "Quarterly": 1.05,
    "Twice a week": 0.80,
}

#: How dirty the place is, and what that does to the hours.
CONDITION_FACTORS = {
    "Very clean - upkeep only": 0.85,
    "Normal": 1.00,
    "Needs attention": 1.20,
    "Heavily soiled": 1.45,
    "Extreme / hoarding": 1.80,
}


# ---------------------------------------------------------------------------
# Colours - a clean, professional palette: deep teal, fresh aqua, citrus
# ---------------------------------------------------------------------------

class Palette:
    ink = "#102A30"           # darkest teal - titles
    primary = "#14616B"       # headers
    primary_mid = "#2F8F9D"   # section bands
    primary_soft = "#DCEEF0"  # light band / alternating rows
    accent = "#E8A33D"        # citrus accent
    accent_soft = "#FDF0D9"
    input_bg = "#FFFFFF"      # editable cell background (clean white)
    input_border = "#D5E3E5"
    calc_bg = "#EDF4F5"       # locked formula cell background (pale teal)
    calc_border = "#CFE0E3"
    white = "#FFFFFF"
    grey_text = "#5A6A6D"
    line = "#BFD6DA"
    good_bg = "#D7F2E3"
    good_text = "#11684A"
    warn_bg = "#FFF0CE"
    warn_text = "#8A5A00"
    bad_bg = "#FBD9DD"
    bad_text = "#9C1C2E"
    info_bg = "#DDE9FA"
    info_text = "#27467F"
    note_bg = "#F5FAFB"


# ---------------------------------------------------------------------------
# Row capacity of every register (how many pre-formatted / pre-formulated rows)
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Settings": 0,
    "Lists": 40,
    "Clients": 500,
    "Properties": 600,
    "Leads": 350,
    "Services": 150,
    "Quotes": 500,
    "Quote Lines": 1800,
    "Jobs": 2100,
    "Job Tasks": 2600,
    "Checklists": 900,
    "Employees": 90,
    "Timesheets": 2800,
    "Job Costing": 1900,
    "Invoices": 900,
    "Invoice Lines": 2100,
    "Payments": 1000,
    "Supplies": 350,
    "Supply Usage": 700,
    "Equipment": 180,
    "Expenses": 900,
    "Mileage": 900,
    "Complaints": 180,
    "Safety": 180,
    "Incidents": 140,
}


@dataclass
class BusinessDefaults:
    """Sample values written into the Business Profile (Settings) sheet."""

    name: str = "Bright & Tidy Cleaning Co."
    owner: str = "Dana Whitfield"
    email: str = "hello@brightandtidy.co"
    phone: str = "(503) 555 0142"
    address: str = "18 Juniper Way, Portland, OR 97214"
    area: str = "Portland metro - 20 mile radius"
    website: str = "brightandtidy.co"
    tagline: str = "Reliable domestic and commercial cleaning since 2019"
    reg_number: str = "BT-CLEAN-2019-0146"
    insurance: str = "Hartfield Commercial - policy HCX-884213"


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
    area_unit: str = "sq ft"             # sq ft | sq m
    distance_unit: str = "miles"         # miles | km

    # Business profile pre-filled on the Settings tab -----------------------
    business: BusinessDefaults = field(default_factory=BusinessDefaults)
    plan_year: int = 0                   # 0 = the year of `today`
    week_start: str = "Monday"

    # Pricing ---------------------------------------------------------------
    hourly_rate: float = 45.00           # what the client pays an hour
    minimum_charge: float = 90.00        # no job leaves for less than this
    rate_per_area: float = 0.09          # per sq ft of a standard clean
    rate_per_bedroom: float = 25.00
    rate_per_bathroom: float = 30.00
    rate_per_room: float = 18.00
    callout_fee: float = 15.00
    deep_clean_uplift: float = 0.45      # +45% on a deep clean
    move_clean_uplift: float = 0.35
    pet_surcharge: float = 20.00
    supplies_per_hour: float = 2.50      # what the chemicals cost you
    target_margin: float = 0.45          # the margin a quote aims for
    margin_floor: float = 0.25           # below this the quote is flagged
    deposit_percent: float = 0.25

    # Staff -----------------------------------------------------------------
    pay_rate: float = 18.00              # what a cleaner costs an hour
    overtime_multiplier: float = 1.5
    employer_oncost: float = 0.18        # tax, insurance, holiday pay
    cleaners_per_job: int = 2
    productive_hours: float = 6.0        # billable hours in a working day
    travel_rate: float = 0.67            # reimbursement a mile
    travel_minutes: int = 20             # allowance between jobs

    # Billing ---------------------------------------------------------------
    tax_rate: float = 0.00               # sales tax / VAT on invoices
    tax_label: str = "Sales tax"
    payment_terms_days: int = 14
    late_fee_percent: float = 0.05
    quote_valid_days: int = 30

    # Targets the dashboard measures against --------------------------------
    monthly_revenue_target: float = 26000.0
    annual_revenue_target: float = 312000.0
    monthly_expense_budget: float = 15000.0
    # the example company is a smaller operation than the defaults
    # assume, so the demo file carries targets it can be measured
    # against - a dashboard showing 16% of target teaches nobody
    # anything
    sample_monthly_revenue_target: float = 6000.0
    sample_annual_revenue_target: float = 72000.0
    sample_monthly_expense_budget: float = 4000.0
    utilisation_target: float = 0.75     # share of paid hours that are billed
    retention_target: float = 0.85
    satisfaction_target: float = 4.5     # out of 5
    quote_win_target: float = 0.50

    # Reminder windows ------------------------------------------------------
    quote_followup_days: int = 3
    overdue_grace_days: int = 0
    reminder_days: int = 2               # how early a job is flagged
    inactive_client_days: int = 60
    low_stock_days: int = 14
    maintenance_days: int = 90           # service interval for equipment
    certificate_warning_days: int = 45
    renewal_warning_days: int = 60

    # Behaviour -------------------------------------------------------------
    top_rows: int = 5                    # size of the "top / best" tables
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
    def expense_budget_month(self) -> float:
        return (self.sample_monthly_expense_budget
                if self.include_sample_data else self.monthly_expense_budget)

    @property
    def imperial(self) -> bool:
        return self.area_unit.replace(" ", "").lower().startswith("sqf")

    def scale_rows(self, job_rows: int) -> None:
        """Scale every register in place so Jobs holds N rows."""
        base = DEFAULT_ROWS["Jobs"]
        factor = max(0.02, float(job_rows) / float(base))
        self.rows = {k: (max(5, int(round(v * factor))) if v else v)
                     for k, v in self.rows.items()}

    def scaled(self, factor: float) -> "Config":
        """Return a copy with every register scaled."""
        rows = {k: max(5, int(round(v * factor))) if v else v
                for k, v in self.rows.items()}
        return replace(self, rows=rows)

    # Number format strings derived from the chosen currency ------------------
    @property
    def money_format(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0.00;[Red]-{s}#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'{s}#,##0;[Red]-{s}#,##0'

    @property
    def cost_per_hour(self) -> float:
        """What one cleaner-hour really costs once on-costs are added."""
        return round(self.pay_rate * (1 + self.employer_oncost), 2)

    @property
    def week_start_date(self) -> date:
        """The Monday (or Sunday) of the week `today` falls in."""
        day = self.today
        offset = day.weekday() if self.week_start == "Monday" \
            else (day.weekday() + 1) % 7
        return date.fromordinal(day.toordinal() - offset)
