"""`Settings & Lists` - every number and every list the workbook runs on.

Nothing in this file is hard coded to one country, one currency or one
way of pricing a wedding.  Your deposit percentage, when the balance is
due, what an extra hour costs, your mileage rate, how long a gallery
stays up, your target margin and all fifty-odd drop-downs are set here,
once, and every other tab follows.

The money rules matter most.  A photographer in Portland charging 30%
to hold a date and a photographer in Perth charging 50% are both right,
and a spreadsheet that bakes in either one is wrong for the other.
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Tuple

from ..config import (BOOKING_STATUSES, CLIENT_STATUSES, CONTENT_TYPES,
                      COUNTRIES, DELIVERY_PREFERENCES, DISCLAIMER,
                      EQUIPMENT_CATEGORIES, EQUIPMENT_CONDITIONS,
                      EXPENSE_CATEGORIES, FREQUENCY_PER_YEAR,
                      GALLERY_STATUSES, HONESTY_NOTE, ID_PREFIX_FIELDS,
                      LEAD_SOURCES, LEAD_STATUSES, MARKETING_PLATFORMS,
                      MONTH_NAMES, PACKAGE_TIERS, PAYMENT_METHODS,
                      PAYMENT_STAGES, PHOTO_STYLES, PRIORITY_LEVELS,
                      PRIVACY_NOTE, RECURRING_FREQUENCIES,
                      REVIEW_PLATFORMS, REVIEW_STATUSES, SHOT_LIST,
                      STAFF_ROLES, TAX_CATEGORIES, TIMELINE_EVENTS,
                      TRAVEL_MODES, VENUE_TYPES, WEDDING_STYLES, YES_NO,
                      Config, Palette)
from ..layout import Registry, col_letter, dynamic_name, quote_sheet
from ..writer import SheetWriter, number_check

NAME = "Settings & Lists"
LAST_COL = 11

#: lists the config does not already carry, defined where they are used
DOCUMENT_TYPES = [
    "Wedding contract", "Booking form", "Model release",
    "Venue permit", "Venue public liability", "Insurance certificate",
    "Questionnaire", "Timeline sign-off", "Shot list sign-off",
    "Invoice", "Receipt", "Album sign-off", "Second shooter agreement",
    "Other",
]
DOCUMENT_STATUSES = [
    "Not needed", "Outstanding", "Sent", "Viewed", "Signed",
    "Counter-signed", "Filed", "Cancelled",
]
EQUIPMENT_STATUSES = [
    "In use", "Spare", "Being repaired", "On loan", "Sold",
    "Lost or stolen", "Retired",
]
GALLERY_PLATFORMS = [
    "Pic-Time", "Pixieset", "ShootProof", "CloudSpot", "SmugMug",
    "Zenfolio", "Dropbox", "Google Drive", "WeTransfer",
    "Own website", "USB only", "Other",
]
MARKETING_STATUSES = [
    "Idea", "Drafted", "Scheduled", "Published", "Evergreen",
    "Archived", "Cancelled",
]
REQUEST_SOURCES = [
    "Couple asked for it", "Parent asked for it",
    "Wedding planner", "Venue", "Your standard list",
    "Your own idea", "Other",
]
REVIEW_ASK_METHODS = [
    "Email", "Text message", "In the gallery", "In person",
    "Thank-you card", "Automatic reminder", "Other",
]
SHOT_GROUP_LABELS = {
    "details": "Details", "prep": "Preparation", "couple": "Couple",
    "family": "Family", "ceremony": "Ceremony",
    "reception": "Reception",
}
SHOT_WHEN = [
    "Before the ceremony", "Getting ready", "Ceremony",
    "Straight after the ceremony", "Family groups", "Couple portraits",
    "Golden hour", "Reception", "Evening", "Any time",
]
STAFF_STATUSES = ["Active", "Occasional", "On leave", "Left", "Prospect"]
STAFF_TYPES = [
    "Owner", "Employee", "Self-employed contractor", "Agency",
    "Unpaid helper",
]
TRAVEL_PURPOSES = [
    "Wedding day", "Engagement shoot", "Venue visit", "Consultation",
    "Rehearsal", "Album delivery", "Equipment collection",
    "Training or workshop", "Networking", "Other",
]

#: name -> values.  Everything the workbook offers you in a drop-down.
LISTS: List[Tuple[str, List[str]]] = [
    ("YesNoList", list(YES_NO)),
    ("BookingStatusList", list(BOOKING_STATUSES)),
    ("ClientStatusList", list(CLIENT_STATUSES)),
    ("LeadStatusList", list(LEAD_STATUSES)),
    ("LeadSourceList", list(LEAD_SOURCES)),
    ("PriorityList", list(PRIORITY_LEVELS)),
    ("TierList", list(PACKAGE_TIERS)),
    ("VenueTypeList", list(VENUE_TYPES)),
    ("WeddingStyleList", list(WEDDING_STYLES)),
    ("PhotoStyleList", list(PHOTO_STYLES)),
    ("DeliveryPreferenceList", list(DELIVERY_PREFERENCES)),
    ("DocumentTypeList", list(DOCUMENT_TYPES)),
    ("DocumentStatusList", list(DOCUMENT_STATUSES)),
    ("PaymentStageList", list(PAYMENT_STAGES)),
    ("PaymentMethodList", list(PAYMENT_METHODS)),
    ("ShotGroupList", [SHOT_GROUP_LABELS[g[0]] for g in SHOT_LIST]),
    ("ShotWhenList", list(SHOT_WHEN)),
    ("RequestSourceList", list(REQUEST_SOURCES)),
    ("StaffRoleList", list(STAFF_ROLES)),
    ("StaffStatusList", list(STAFF_STATUSES)),
    ("StaffTypeList", list(STAFF_TYPES)),
    ("GalleryStatusList", list(GALLERY_STATUSES)),
    ("GalleryPlatformList", list(GALLERY_PLATFORMS)),
    ("EquipmentCategoryList", list(EQUIPMENT_CATEGORIES)),
    ("EquipmentStatusList", list(EQUIPMENT_STATUSES)),
    ("EquipmentConditionList", list(EQUIPMENT_CONDITIONS)),
    ("TravelModeList", list(TRAVEL_MODES)),
    ("TravelPurposeList", list(TRAVEL_PURPOSES)),
    ("MarketingPlatformList", list(MARKETING_PLATFORMS)),
    ("ContentTypeList", list(CONTENT_TYPES)),
    ("ContentStatusList", list(MARKETING_STATUSES)),
    ("ExpenseCategoryList", list(EXPENSE_CATEGORIES)),
    ("TaxCategoryList", list(TAX_CATEGORIES)),
    ("FrequencyList", list(RECURRING_FREQUENCIES)),
    ("ReviewStatusList", list(REVIEW_STATUSES)),
    ("ReviewPlatformList", list(REVIEW_PLATFORMS)),
    ("ReviewAskMethodList", list(REVIEW_ASK_METHODS)),
    ("CountryList", list(COUNTRIES)),
    ("MonthNameList", list(MONTH_NAMES)),
]


def _month_keys(today: _dt.date, back: int = 15, ahead: int = 21
                ) -> List[str]:
    """`yyyy-mm` keys around today, oldest first.

    Weddings are booked a long way ahead, so this window reaches
    further forward than it does back.
    """
    keys: List[str] = []
    year, month = today.year, today.month
    start = month - back
    while start <= 0:
        start += 12
        year -= 1
    for step in range(back + ahead + 1):
        m = start + step
        y = year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        keys.append(f"{y:04d}-{m:02d}")
    return keys


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)
    sheet_ref = quote_sheet(NAME)

    s.banner("Settings & Lists",
             "Your studio, your prices, your rules, your lists. Set "
             "these once and every tab in the workbook follows.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 2, 26)
    s.set_col(3, 3, 20)
    s.set_col(4, LAST_COL, 17)

    row = 4
    row = s.note(
        row,
        "White cells are yours to change; everything else is locked "
        "and calculated. Nothing here assumes a country, a currency "
        "or a way of pricing a wedding - set your own deposit rule, "
        "your own payment dates, your own mileage rate and your own "
        "targets, and the rest of the workbook follows.",
        LAST_COL, height=34)
    row += 1

    # --------------------------------------------------------- studio --
    row = s.section(row, "Your studio", LAST_COL)
    row = s.field(row, "Studio name", cfg.studio.name, name="StudioName",
                  value_end=5, help_col=7,
                  help_text="Printed at the top of every report and "
                            "every printable sheet you take to a "
                            "wedding.")
    row = s.field(row, "Photographer", cfg.studio.owner,
                  name="OwnerName", value_end=5, help_col=7)
    row = s.field(row, "Email", cfg.studio.email, value_end=5,
                  help_col=7)
    row = s.field(row, "Phone", cfg.studio.phone, value_end=5,
                  help_col=7)
    row = s.field(row, "Website", cfg.studio.website, value_end=5,
                  help_col=7)
    row = s.field(row, "Instagram", cfg.studio.instagram, value_end=5,
                  help_col=7)
    row = s.field(row, "Based in", f"{cfg.studio.city}, "
                  f"{cfg.studio.region}", value_end=5, help_col=7)
    row = s.field(row, "Country", cfg.studio.country, value_end=5,
                  help_col=7)
    row = s.field(row, "Currency symbol", cfg.currency,
                  name="CurrencySign",
                  help_text="Shown on screen. The cell formats follow "
                            "the symbol you build the file with.")
    row = s.field(row, "Currency code", cfg.currency_code)
    row = s.field(row, "Today", None, style="date", name="TodayDate",
                  mode="calc", formula="=TODAY()",
                  help_text="Live. Everything that says 'overdue', "
                            "'coming up' or 'this month' reads this "
                            "one cell.")
    row = s.field(row, "This month", None, style="text",
                  name="ThisMonthKey", mode="calc",
                  formula='=TEXT(TODAY(),"yyyy-mm")',
                  help_text="The month key every monthly total groups "
                            "on.")
    row = s.field(row, "This year", None, style="int",
                  name="ThisYear", mode="calc",
                  formula="=YEAR(TODAY())")
    row += 1

    # ------------------------------------------------- the money rules --
    row = s.section(row, "How you take the money", LAST_COL)
    row = s.note(
        row,
        "These four rules decide what every booking shows as a "
        "deposit, when the balance is due and when a payment counts "
        "as late. There is no standard - 30% on booking with the "
        "balance a fortnight out is common, 50/50 is common, and "
        "your contract is what actually matters. Put yours in.",
        LAST_COL, height=42)
    row += 1
    row = s.field(row, "Deposit to hold a date", cfg.deposit_percent,
                  style="percent", name="DepositPercent",
                  validate=number_check(0, 1),
                  help_text="A share of the total booking value. "
                            "Non-refundable deposits are normal in "
                            "wedding photography and should be "
                            "spelled out in your contract.")
    row = s.field(row, "Deposit due within", cfg.deposit_days_after_booking,
                  style="int", name="DepositDays",
                  validate=number_check(0, 365),
                  help_text="Days after you confirm the booking. "
                            "Until it arrives the date is not really "
                            "held.")
    row = s.field(row, "Second instalment", cfg.second_percent,
                  style="percent", name="SecondPercent",
                  validate=number_check(0, 1))
    row = s.field(row, "Second instalment due",
                  cfg.second_payment_days_before, style="int",
                  name="SecondPaymentDays", validate=number_check(0, 999),
                  help_text="Days before the wedding.")
    row = s.field(row, "Balance due", cfg.final_payment_days_before,
                  style="int", name="FinalPaymentDays",
                  validate=number_check(0, 365),
                  help_text="Days before the wedding. Collect the "
                            "balance before the day, never after - "
                            "chasing money from a couple on honeymoon "
                            "is a miserable job.")
    row = s.field(row, "Invoice payment terms", cfg.payment_terms_days,
                  style="int", name="PaymentTerms",
                  validate=number_check(0, 365))
    row = s.field(row, "Chase an unpaid invoice after",
                  cfg.payment_chase_days, style="int",
                  name="PaymentChaseDays", validate=number_check(1, 365))
    row += 1

    # ----------------------------------------------------- the pricing --
    row = s.section(row, "What the extras cost", LAST_COL)
    row = s.note(
        row,
        "Package prices live on Packages & Pricing, one row each. "
        "These are the charges a booking works out for itself: "
        "overtime, a second shooter, mileage past the free miles.",
        LAST_COL, height=30)
    row += 1
    row = s.field(row, "Extra hour on the day", cfg.extra_hour_rate,
                  style="money", name="ExtraHourRate",
                  validate=number_check(0, 100000),
                  help_text="Charged automatically when the coverage "
                            "times run past the package hours.")
    row = s.field(row, "Second shooter", cfg.second_shooter_rate,
                  style="money", name="SecondShooterRate",
                  validate=number_check(0, 100000),
                  help_text="What a second shooter costs you for a "
                            "wedding day.")
    row = s.field(row, "Assistant", cfg.assistant_rate, style="money",
                  name="AssistantRate", validate=number_check(0, 100000))
    row = s.field(row, "Engagement session", cfg.engagement_session_price,
                  style="money", name="EngagementPrice",
                  validate=number_check(0, 100000))
    row = s.field(row, "Engagement session costs you",
                  round(cfg.engagement_session_price * 0.35, 2),
                  style="money", name="EngagementCost",
                  validate=number_check(0, 100000),
                  help_text="Your time and travel for a shoot you have "
                            "included in a package.")
    row = s.field(row, "Album base price", cfg.album_base_price,
                  style="money", name="AlbumPrice",
                  validate=number_check(0, 100000))
    row = s.field(row, "Rush delivery fee", cfg.rush_delivery_fee,
                  style="money", name="RushFee",
                  validate=number_check(0, 100000))
    row = s.field(row, "Print credit costs you", 0.4, style="percent",
                  name="PrintCostRatio", validate=number_check(0, 1),
                  help_text="What a dollar of print credit actually "
                            "costs you at the lab. Packages use it to "
                            "cost their print allowance.")
    row = s.field(row, "Mileage rate", cfg.mileage_rate, style="money4",
                  name="MileageRate", validate=number_check(0, 100),
                  help_text="Per mile. Check your own tax authority's "
                            "approved rate each year - it changes, and "
                            "it is different in every country.")
    row = s.field(row, "Free miles included", cfg.free_travel_miles,
                  style="int", name="FreeTravelMiles",
                  validate=number_check(0, 10000),
                  help_text="Used when the package does not set its "
                            "own travel allowance.")
    row = s.field(row, "Flag a trip that loses more than", 150,
                  style="money", name="TravelLossLimit",
                  validate=number_check(0, 100000))
    row += 1

    # ---------------------------------------------------------- the tax --
    row = s.section(row, "Tax", LAST_COL)
    row = s.note(
        row,
        "Whether wedding photography is taxable where you are, at "
        "what rate, and whether you are even registered, are local "
        "questions with local answers. The rate ships at zero and the "
        "switch ships off, so the workbook does nothing until you "
        "tell it what is true for you.",
        LAST_COL, height=38)
    row += 1
    row = s.field(row, "Add tax to packages",
                  "Yes" if cfg.tax_on_packages else "No", style="flag",
                  name="TaxOnPackages",
                  validate={"validate": "list", "source": "=YesNoList"},
                  help_text="No by default. Turn it on only if you "
                            "charge sales tax or VAT on photography.")
    row = s.field(row, "Tax rate", cfg.tax_rate, style="percent",
                  name="TaxRate", validate=number_check(0, 1))
    row = s.field(row, "What it is called", cfg.tax_name,
                  name="TaxName", value_end=5, help_col=7)
    row = s.field(row, "Receipt needed above", 25, style="money",
                  name="ReceiptThreshold", validate=number_check(0, 100000),
                  help_text="Expenses over this with no receipt are "
                            "flagged. Your own rules may be stricter.")
    row += 1

    # ------------------------------------------------- the work after it --
    row = s.section(row, "Editing and delivery", LAST_COL)
    row = s.field(row, "Preview images within", cfg.preview_days,
                  style="int", name="PreviewDays",
                  validate=number_check(0, 365),
                  help_text="Days after the wedding. A handful of "
                            "images in the first week buys you weeks "
                            "of patience on the rest.")
    row = s.field(row, "Full gallery within", cfg.delivery_days,
                  style="int", name="DeliveryDays",
                  validate=number_check(1, 730),
                  help_text="Days after the wedding. Promise what you "
                            "can do in your worst month, not your "
                            "best.")
    row = s.field(row, "Rush delivery within", 14, style="int",
                  name="RushDeliveryDays", validate=number_check(1, 365))
    row = s.field(row, "Album within", cfg.album_days, style="int",
                  name="AlbumDays", validate=number_check(1, 730))
    row = s.field(row, "Gallery stays up for",
                  cfg.gallery_months_live * 30, style="int",
                  name="GalleryLiveDays", validate=number_check(30, 3650),
                  help_text="Days from delivery. Tell the couple this "
                            "date when you hand the gallery over.")
    row = s.field(row, "Editing hours a wedding",
                  cfg.editing_hours_per_wedding, style="number1",
                  name="EditingHours", validate=number_check(0, 500),
                  help_text="Your honest average. Packages cost their "
                            "editing on it and profit per hour depends "
                            "on it.")
    row = s.field(row, "Editing cost an hour", cfg.editing_cost_per_hour,
                  style="money", name="EditingRate",
                  validate=number_check(0, 10000),
                  help_text="What an hour of editing costs the "
                            "business - an outside editor's rate, or "
                            "what your own hour is worth.")
    row = s.field(row, "Admin hours a wedding", 6, style="number1",
                  name="AdminHoursPerWedding", validate=number_check(0, 200),
                  help_text="Enquiries, the consultation, the "
                            "contract, the invoices, the "
                            "questionnaire, the delivery email. Six "
                            "hours is a conservative guess.")
    row += 1

    # ----------------------------------------------------- when to nag --
    row = s.section(row, "When the workbook should nag you", LAST_COL)
    row = s.field(row, "Chase an enquiry after", cfg.lead_chase_days,
                  style="int", name="LeadChaseDays",
                  validate=number_check(1, 90),
                  help_text="Days with no reply from them. Wedding "
                            "enquiries go cold fast - most couples "
                            "contact several photographers the same "
                            "evening.")
    row = s.field(row, "Chase after a consultation",
                  cfg.consultation_chase_days, style="int",
                  name="ConsultationChaseDays", validate=number_check(1, 90))
    row = s.field(row, "Chase an unsigned document",
                  cfg.contract_warn_days, style="int",
                  name="DocumentChaseDays", validate=number_check(1, 180))
    row = s.field(row, "Chase a review after", cfg.review_chase_days,
                  style="int", name="ReviewChaseDays",
                  validate=number_check(1, 180))
    row = s.field(row, "'Coming up' means within", cfg.upcoming_days,
                  style="int", name="UpcomingDays",
                  validate=number_check(1, 365),
                  help_text="Days. Controls what the dashboard calls "
                            "an upcoming wedding.")
    row = s.field(row, "Warn about a warranty", cfg.warranty_warn_days,
                  style="int", name="WarrantyWarnDays",
                  validate=number_check(1, 365))
    row = s.field(row, "Service kit every", 12, style="int",
                  name="ServiceMonths", validate=number_check(1, 120),
                  help_text="Months between services for anything you "
                            "have put a service date against.")
    row = s.field(row, "Insure anything worth over", 500, style="money",
                  name="InsureAbove", validate=number_check(0, 1000000))
    row = s.field(row, "Equipment useful life", 5, style="number1",
                  name="EquipmentLifeYears", validate=number_check(1, 40),
                  help_text="Years. Used to spread what a camera cost "
                            "across the years you will use it.")
    row += 1

    # ------------------------------------------------------- the targets --
    row = s.section(row, "Your targets", LAST_COL)
    row = s.note(
        row,
        "The dashboard measures you against these, so make them real. "
        "A target you set because it sounded good makes every chart "
        "in the workbook useless.",
        LAST_COL, height=30)
    row += 1
    row = s.field(row, "Weddings a year", cfg.target_weddings_year,
                  style="int", name="TargetWeddings",
                  validate=number_check(1, 400))
    row = s.field(row, "Average booking value", cfg.target_booking_value,
                  style="money", name="TargetAverageValue",
                  validate=number_check(0, 1000000))
    row = s.field(row, "Revenue a year", cfg.target_revenue_year,
                  style="money", name="TargetRevenue",
                  validate=number_check(0, 100000000))
    row = s.field(row, "Profit margin", cfg.target_profit_margin,
                  style="percent", name="TargetMargin",
                  validate=number_check(0, 1),
                  help_text="Packages use this to work out what they "
                            "would have to sell for.")
    row = s.field(row, "Enquiry to booking", cfg.target_conversion,
                  style="percent", name="TargetConversion",
                  validate=number_check(0, 1))
    row = s.field(row, "Average review", cfg.target_rating,
                  style="rating", name="TargetRating",
                  validate=number_check(1, 5))
    row = s.field(row, "Lowest hourly rate you will accept", 45,
                  style="money", name="MinimumHourly",
                  validate=number_check(0, 10000),
                  help_text="Profit per hour across shooting, "
                            "editing, travel and admin. Anything under "
                            "this is flagged, on the package and on "
                            "the wedding.")
    row = s.field(row, "An hour of yours is worth", 60, style="money",
                  name="OwnerHourlyValue", validate=number_check(0, 10000),
                  help_text="Used to cost the hours you put into "
                            "marketing. Free marketing is not free.")
    row += 1

    # ------------------------------------------------ live totals ------
    row = s.section(row, "Worked out from your data", LAST_COL)
    row = s.note(
        row,
        "These three are calculated, not typed. Profit Analysis uses "
        "them to spread the year's overheads across the year's "
        "weddings.",
        LAST_COL, height=28)
    row += 1
    row = s.field(row, "Weddings this year", None, style="int",
                  name="WeddingsThisYear", mode="calc",
                  formula='=COUNTIFS([[Wedding Bookings.year]],'
                          'YEAR(TODAY()),'
                          '[[Wedding Bookings.earns]],"Yes")')
    row = s.field(row, "Overheads this year", None, style="money",
                  name="OverheadsThisYear", mode="calc",
                  formula='=SUMIFS([[Expense Tracker.profit_cost]],'
                          '[[Expense Tracker.year]],YEAR(TODAY()),'
                          '[[Expense Tracker.is_overhead]],"Yes")')
    row = s.field(row, "Couples on the books", None, style="int",
                  name="ClientCount", mode="calc",
                  formula='=COUNTIF([[Client CRM.name]],"?*")')
    row += 1

    # ------------------------------------------- the timeline template --
    row = s.section(row, "Standard wedding day timeline", LAST_COL)
    row = s.note(
        row,
        "The Wedding Timeline tab builds a day plan from this table. "
        "Minutes are counted from the ceremony - negative is before "
        "it, positive is after. These are sensible starting points for "
        "a traditional day; change them to match how you actually "
        "work, and override anything on the wedding itself.",
        LAST_COL, height=44)
    row += 1
    head = row
    s.table_head(head, 1, ["Event", "Minutes from ceremony",
                           "How long", "Who covers it"],
                 widths=[30, 20, 14, 22])
    first = head + 1
    spare = 6
    for index, (_key, label, offset, length, role) in enumerate(
            TIMELINE_EVENTS):
        line = first + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, offset, fmts.input("int"))
        s.write(line, 3, length, fmts.input("int"))
        s.write(line, 4, role, fmts.input("text"))
    for index in range(len(TIMELINE_EVENTS),
                       len(TIMELINE_EVENTS) + spare):
        line = first + index
        for column, style in ((1, "text"), (2, "int"), (3, "int"),
                              (4, "text")):
            s.write(line, column, None, fmts.input(style))
    last = first + len(TIMELINE_EVENTS) + spare - 1
    for key, column in (("TimelineEventList", 1),
                        ("TimelineOffsetList", 2),
                        ("TimelineDurationList", 3),
                        ("TimelineRoleList", 4)):
        book.define_name(
            key, f"={sheet_ref}!${col_letter(column)}${first + 1}:"
                 f"${col_letter(column)}${last + 1}")
    row = last + 2

    # ------------------------------------------- recurring frequencies --
    row = s.section(row, "How often a recurring cost repeats", LAST_COL)
    row = s.note(
        row,
        "This is what turns any expense into a monthly equivalent, so "
        "a yearly insurance premium and a monthly subscription can sit "
        "in the same breakdown. 'One off' is zero because it is not a "
        "standing cost.",
        LAST_COL, height=30)
    row += 1
    freq_head = row
    s.table_head(freq_head, 1, ["How often", "Times a year"],
                 widths=[24, 16])
    first_freq = freq_head + 1
    for index, label in enumerate(RECURRING_FREQUENCIES):
        line = first_freq + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, FREQUENCY_PER_YEAR.get(label, 0.0),
                fmts.input("number1"))
    last_freq = first_freq + len(RECURRING_FREQUENCIES) - 1
    book.define_name(
        "FrequencyPerYear",
        f"={sheet_ref}!$C${first_freq + 1}:$C${last_freq + 1}")
    row = last_freq + 2

    # -------------------------------------------------------- prefixes --
    row = s.section(row, "ID prefixes", LAST_COL)
    row = s.note(
        row,
        "The letters in front of every automatic ID. Booking IDs are "
        "the ones that matter - they are the key the whole workbook "
        "joins on. Change the prefixes here if you want to, but do it "
        "before you have typed two hundred weddings, not after.",
        LAST_COL, height=32)
    row += 1
    half = (len(ID_PREFIX_FIELDS) + 1) // 2
    top = row
    for index, (label, default, name, _digits) in enumerate(
            ID_PREFIX_FIELDS):
        column = 0 if index < half else 4
        line = top + (index if index < half else index - half)
        s.write(line, column + 1, label, fmts.chrome("label_bold"))
        s.write(line, column + 2, default, fmts.input("text"))
        book.define_name(
            name, f"={sheet_ref}!${col_letter(column + 2)}${line + 1}")
    row = top + half + 1

    # ----------------------------------------------------------- lists --
    row = s.section(row, "Drop-down lists", LAST_COL)
    row = s.note(
        row,
        "Add new entries directly under the last one in a column - "
        "every list has room to grow and blank rows are ignored. Do "
        "not delete a whole column: a drop-down pointing at a missing "
        "list stops working.",
        LAST_COL, height=30)
    row += 1

    per_row = 4
    spare = 6
    top = row
    column = 0
    tallest = 0
    for index, (name, values) in enumerate(LISTS):
        if index and index % per_row == 0:
            top += tallest + 2
            column = 0
            tallest = 0
        s.write(top, column, name.replace("List", ""),
                fmts.chrome("header"))
        s.set_col(column, column, 28)
        for offset, value in enumerate(values):
            s.write(top + 1 + offset, column, value, fmts.input("text"))
        for offset in range(len(values), len(values) + spare):
            s.write(top + 1 + offset, column, None, fmts.input("text"))
        first = top + 2
        last = top + 1 + len(values) + spare
        book.define_name(
            name,
            f"={sheet_ref}!${col_letter(column)}${first}:"
            f"${col_letter(column)}${last}")
        tallest = max(tallest, len(values) + spare)
        column += 3
    row = top + tallest + 3

    # ------------------------------------------------------ month keys --
    row = s.section(row, "Month keys", LAST_COL)
    row = s.note(
        row,
        "The months the reports pick from. Plain text in yyyy-mm form "
        "so that every monthly total in the workbook groups on exactly "
        "the same thing. The window runs further forward than back, "
        "because weddings are booked a long way ahead.",
        LAST_COL, height=32)
    row += 1
    keys = _month_keys(cfg.today)
    s.write(row, 0, "Month", fmts.chrome("header"))
    s.set_col(0, 0, 14)
    for offset, key in enumerate(keys):
        s.write(row + 1 + offset, 0, key, fmts.input("text"))
    book.define_name(
        "MonthKeyList",
        f"={sheet_ref}!$A${row + 2}:$A${row + 1 + len(keys)}")
    book.define_name(
        "MonthKeys",
        dynamic_name(NAME, "A", row + 2, row + 1 + len(keys)))
    row = row + len(keys) + 2

    row = s.note(row, HONESTY_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, PRIVACY_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=96)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
