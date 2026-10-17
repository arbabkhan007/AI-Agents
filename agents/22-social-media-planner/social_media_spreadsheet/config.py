"""
Configuration for the Social Media Content Calendar & Analytics Planner.

Everything a shop owner may want to re-brand lives here, so the workbook can
be regenerated for a different brand, currency or country without touching
any of the sheet code.

Author of the generated workbooks: Novality Store.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date


# ---------------------------------------------------------------------------
# Product / branding constants
# ---------------------------------------------------------------------------

AUTHOR = "Novality Store"
PRODUCT_NAME = "Social Media Content Calendar & Analytics Planner"
PRODUCT_SUBTITLE = (
    "12-Month Content Calendar, Caption & Hashtag Banks, Campaigns and "
    "Instagram, TikTok, Pinterest, YouTube & Facebook Analytics"
)
PRODUCT_VERSION = "1.0.0"

#: Title suggested for the shop listing.
PRODUCT_LISTING_TITLE = (
    "Social Media Content Planner Spreadsheet, 12-Month Content Calendar, "
    "Instagram, TikTok, Pinterest, YouTube and Facebook Analytics Tracker"
)

#: Password that protects every sheet so formula cells cannot be edited by
#: accident.  Input cells stay unlocked, formula cells are locked.
FORMULA_PASSWORD = "premium"

#: The platforms the workbook reports on out of the box.  Change these on the
#: Lists tab and every drop down follows; the five analytics columns on the
#: dashboards follow :data:`TRACKED_PLATFORMS`.
TRACKED_PLATFORMS = ["Instagram", "TikTok", "Pinterest", "YouTube",
                     "Facebook"]


# ---------------------------------------------------------------------------
# Colour palette (indigo / coral scheme used across every tab)
# ---------------------------------------------------------------------------

class Palette:
    ink = "#241B38"          # darkest indigo - titles
    primary = "#3B2A6B"      # headers
    primary_mid = "#6350A8"  # section bands
    primary_soft = "#E7E3F6"  # light band / alternating rows
    accent = "#F2665E"       # coral accent
    accent_soft = "#FDEBE9"
    input_bg = "#FFFCF7"     # editable cell background (warm white)
    input_border = "#E8DCC8"
    calc_bg = "#F1EFF8"      # locked formula cell background (soft lilac)
    calc_border = "#D8D2EA"
    white = "#FFFFFF"
    grey_text = "#5F5A70"
    line = "#C7C1DA"
    good_bg = "#D9F2E4"
    good_text = "#0E6B45"
    warn_bg = "#FFF1CF"
    warn_text = "#8A5A00"
    bad_bg = "#FBD9DD"
    bad_text = "#9C1C2E"
    info_bg = "#DEE8FA"
    info_text = "#2A4A8B"
    note_bg = "#F8F7FC"


# ---------------------------------------------------------------------------
# Row capacity of every register (how many pre-formatted / pre-formulated rows)
# ---------------------------------------------------------------------------

DEFAULT_ROWS = {
    "Settings": 0,
    "Lists": 40,
    "Accounts": 30,
    "Audience Personas": 12,
    "Content Pillars": 20,
    "Content Calendar": 600,
    "Idea Bank": 300,
    "Caption Bank": 200,
    "Hashtag Bank": 300,
    "Instagram": 200,
    "TikTok": 200,
    "Pinterest": 200,
    "YouTube": 120,
    "Facebook": 200,
    "Campaigns": 60,
    "Launch Planner": 40,
    "Seasonal Planner": 60,
    "Influencers": 60,
    "UGC Tracker": 100,
    "Repurposing": 150,
    "Competitors": 40,
    "Trends": 80,
    "Analytics": 150,
    "Performance": 400,
    "AB Tests": 40,
    "Ads": 100,
    "Assets": 250,
    "Goals": 40,
    "Budget": 60,
    "Team": 30,
    "Tasks": 60,
}


@dataclass
class BrandDefaults:
    """Sample values written into the Business Setup (Settings) sheet."""

    name: str = "Wildflower Studio"
    owner: str = "Jordan Avery"
    email: str = "hello@wildflowerstudio.com"
    phone: str = "+1 (555) 017 4410"
    website: str = "www.wildflowerstudio.com"
    shop: str = "shop.wildflowerstudio.com"
    industry: str = "Handmade home & lifestyle"
    niche: str = "Sustainable ceramics and home styling"
    audience: str = ("Women 28-45 who love slow living, handmade homeware "
                     "and styling their first home")
    goal: str = "Grow to 25,000 followers and 1,200 shop visits a month"
    logo_link: str = "brand-assets/wildflower-logo.png"
    palette: str = "#3B2A6B indigo, #F2665E coral, #F4EFE6 oat"
    fonts: str = "Headings: Canela. Body: Inter."
    timezone: str = "GMT-05:00 Eastern Time"
    hashtag: str = "#wildflowerstudio"


@dataclass
class Config:
    """All generator options."""

    output_path: str = "output/Social Media Content Planner.xlsx"

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

    # Brand / planning defaults pre-filled on the Settings tab
    brand: BrandDefaults = field(default_factory=BrandDefaults)
    plan_year: int = 0               # 0 = the year of `today`
    week_start: str = "Monday"
    posts_per_week_target: int = 3
    monthly_post_target: int = 13
    engagement_target: float = 0.045
    follower_goal: int = 25000
    reach_goal: int = 120000
    click_goal: int = 1800
    lead_goal: int = 240
    conversion_goal: int = 90
    revenue_goal: float = 36000.0
    monthly_budget: float = 900.0
    annual_budget: float = 10800.0
    roas_target: float = 4.0
    cost_per_lead_target: float = 6.0
    production_days: int = 5          # draft deadline before publishing
    approval_days: int = 2            # approval deadline before publishing
    overdue_grace_days: int = 0
    idea_review_days: int = 14
    trend_window_days: int = 14
    asset_review_days: int = 180
    inactive_account_days: int = 30
    top_rows: int = 5                 # size of the "top content" tables

    # Content switches
    include_sample_data: bool = True
    rows: dict = field(default_factory=lambda: dict(DEFAULT_ROWS))
    today: date = field(default_factory=date.today)

    # ---------------------------------------------------------------- helpers
    def row_count(self, sheet: str) -> int:
        return int(self.rows.get(sheet, 100))

    @property
    def year(self) -> int:
        return self.plan_year or self.today.year

    @property
    def MONTHS(self) -> "list[str]":
        """Twelve 'Mmm-yy' labels for the planning year (Mar-26 style)."""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                  "Sep", "Oct", "Nov", "Dec"]
        yy = str(self.year)[-2:]
        return [f"{m}-{yy}" for m in months]

    def scale_rows(self, calendar_rows: int) -> None:
        """Scale every register in place so the calendar holds N rows."""
        base = DEFAULT_ROWS["Content Calendar"]
        factor = max(0.02, float(calendar_rows) / float(base))
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
        return f'"{s}"#,##0.00;[Red]-"{s}"#,##0.00'

    @property
    def money_format_0(self) -> str:
        s = self.currency_symbol
        return f'"{s}"#,##0;[Red]-"{s}"#,##0'
