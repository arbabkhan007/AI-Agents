"""`Settings & Lists` - every number and every list the workbook runs on.

Nothing here is hard coded to one country, one currency or one way of
running a lawn care round. Your crew rate, your charge-out rate, your
minimum visit, your travel rate, your margin floor, your service
intervals and all fifty-odd drop-downs are set here, once, and every
other tab follows.

Three groups deserve a second look before you start.

The crew cost rate should be the loaded cost - wages plus payroll tax
plus insurance - not what lands in somebody's bank account. Put the
take-home figure in and every job in this workbook will look more
profitable than it is.

The overhead per crew hour is the one most people leave at zero. The
yard, the truck insurance, the phone, the accountant and the evenings
doing paperwork are all real, and a three-hour visit carries three
hours of them whether or not anybody works it out.

The ID prefixes decide what your Customer IDs, Property IDs, Job IDs
and Invoice IDs look like. Change them before you have typed two
hundred customers, not after.
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Tuple

from ..config import (ABSENCE_REASONS, ACCESS_TYPES, CONTRACT_STATUSES,
                      CREW_NAMES, CREW_ROLES, CREW_STATUSES, CURRENCIES,
                      CUSTOMER_STATUSES, CUSTOMER_TYPES, DEFAULT_VEHICLES,
                      DISCLAIMER, EMPLOYMENT_TYPES, EQUIPMENT_CATEGORIES,
                      EQUIPMENT_CONDITIONS, EQUIPMENT_STATUSES,
                      EXPENSE_CATEGORIES, FEEDBACK_CAUSES,
                      FEEDBACK_SOURCES, FEEDBACK_STATUSES, FEEDBACK_TYPES,
                      FREQUENCIES, HONESTY_NOTE, ID_PREFIX_FIELDS,
                      INVOICE_STATUSES, JOB_STATUSES, LEAD_SOURCES,
                      MAINTENANCE_TYPES, MATERIAL_CATEGORIES,
                      MATERIAL_STATUSES, MATERIAL_UNITS, MONTH_NAMES,
                      PAYMENT_METHODS, PAYMENT_TERMS, PAYROLL_NOTE,
                      PHOTO_NOTE, PRICING_UNITS, PRIORITIES, PRIVACY_NOTE,
                      PROPERTY_STATUSES, PROPERTY_TYPES, QUOTE_STATUSES,
                      ROUTE_NOTE, SEASONS, SERVICE_CATEGORIES,
                      SERVICE_STATUSES, STOCK_MOVES, TASK_TYPES,
                      TAX_CATEGORIES, TERRAIN_TYPES, VEHICLE_COST_TYPES,
                      WEATHER_CONDITIONS, WEATHER_NOTE, WEEKDAYS, YES_NO,
                      Config, Palette)
from ..layout import Registry, col_letter, dynamic_name, quote_sheet
from ..writer import SheetWriter, list_from, number_check, yes_no

NAME = "Settings & Lists"
LAST_COL = 11

#: name -> values. Every drop-down in the workbook comes from this table.
LISTS: List[Tuple[str, List[str]]] = [
    ("YesNoList", list(YES_NO)),
    ("CustomerTypeList", list(CUSTOMER_TYPES)),
    ("CustomerStatusList", list(CUSTOMER_STATUSES)),
    ("LeadSourceList", list(LEAD_SOURCES)),
    ("PropertyTypeList", list(PROPERTY_TYPES)),
    ("PropertyStatusList", list(PROPERTY_STATUSES)),
    ("TerrainList", list(TERRAIN_TYPES)),
    ("AccessList", list(ACCESS_TYPES)),
    ("ServiceCategoryList", list(SERVICE_CATEGORIES)),
    ("ServiceStatusList", list(SERVICE_STATUSES)),
    ("PricingUnitList", list(PRICING_UNITS)),
    ("QuoteStatusList", list(QUOTE_STATUSES)),
    ("JobStatusList", list(JOB_STATUSES)),
    ("PriorityList", list(PRIORITIES)),
    ("WeatherList", list(WEATHER_CONDITIONS)),
    ("ContractStatusList", list(CONTRACT_STATUSES)),
    ("CrewNameList", list(CREW_NAMES)),
    ("CrewRoleList", list(CREW_ROLES)),
    ("CrewStatusList", list(CREW_STATUSES)),
    ("EmploymentTypeList", list(EMPLOYMENT_TYPES)),
    ("AbsenceList", list(ABSENCE_REASONS)),
    ("TaskTypeList", list(TASK_TYPES)),
    ("EquipmentCategoryList", list(EQUIPMENT_CATEGORIES)),
    ("EquipmentStatusList", list(EQUIPMENT_STATUSES)),
    ("EquipmentConditionList", list(EQUIPMENT_CONDITIONS)),
    ("MaintenanceTypeList", list(MAINTENANCE_TYPES)),
    ("VehicleList", list(DEFAULT_VEHICLES)),
    ("VehicleCostList", list(VEHICLE_COST_TYPES)),
    ("MaterialCategoryList", list(MATERIAL_CATEGORIES)),
    ("MaterialUnitList", list(MATERIAL_UNITS)),
    ("MaterialStatusList", list(MATERIAL_STATUSES)),
    ("StockMoveList", list(STOCK_MOVES)),
    ("InvoiceStatusList", list(INVOICE_STATUSES)),
    ("PaymentMethodList", list(PAYMENT_METHODS)),
    ("ExpenseCategoryList", list(EXPENSE_CATEGORIES)),
    ("TaxCategoryList", list(TAX_CATEGORIES)),
    ("FeedbackSourceList", list(FEEDBACK_SOURCES)),
    ("FeedbackTypeList", list(FEEDBACK_TYPES)),
    ("FeedbackStatusList", list(FEEDBACK_STATUSES)),
    ("FeedbackCauseList", list(FEEDBACK_CAUSES)),
    ("SeasonList", list(SEASONS)),
    ("WeekdayList", list(WEEKDAYS)),
    ("MonthNameList", list(MONTH_NAMES)),
    ("CurrencyList", list(CURRENCIES)),
]


def _month_keys(today: _dt.date, back: int = 18,
                ahead: int = 18) -> List[str]:
    """`yyyy-mm` keys around today - what every monthly total groups on."""
    start = today.year * 12 + today.month - 1 - back
    return [f"{(start + n) // 12:04d}-{(start + n) % 12 + 1:02d}"
            for n in range(back + ahead + 1)]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)
    sheet_ref = quote_sheet(NAME)

    s.banner("Settings & Lists",
             "Your business, your rates, your rules, your lists. Set "
             "these once and all twenty-three tabs follow.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 2, 30)
    s.set_col(3, 3, 18)
    s.set_col(4, LAST_COL, 17)

    row = 4
    row = s.note(
        row,
        "White cells are yours to change; everything else is locked "
        "and calculated. Nothing here assumes a country, a currency "
        "or a size of business - put your own rates, your own "
        "margins and your own service intervals in, and the rest of "
        "the workbook follows.",
        LAST_COL, height=34)
    row += 1

    # ------------------------------------------------------ business --
    row = s.section(row, "Your business", LAST_COL)
    row = s.field(row, "Business name", cfg.business.name,
                  name="BusinessName", value_end=5, help_col=7,
                  help_text="Printed at the top of every quote, "
                            "invoice and crew work order.")
    row = s.field(row, "Owner", cfg.business.owner, name="OwnerName",
                  value_end=5, help_col=7)
    row = s.field(row, "Email", cfg.business.email,
                  name="BusinessEmail", value_end=5, help_col=7)
    row = s.field(row, "Phone", cfg.business.phone,
                  name="BusinessPhone", value_end=5, help_col=7)
    row = s.field(row, "Website", cfg.business.website, value_end=5,
                  help_col=7)
    row = s.field(row, "Yard / depot address", cfg.business.address_1,
                  name="BusinessAddress", value_end=5, help_col=7,
                  help_text="Where the trucks start from. Travel "
                            "distances on the Property Database are "
                            "measured from here.")
    row = s.field(row, "Address line 2", cfg.business.address_2,
                  value_end=5, help_col=7)
    row = s.field(row, "City", cfg.business.city, name="BusinessCity",
                  value_end=5, help_col=7)
    row = s.field(row, "Region / state", cfg.business.region,
                  value_end=5, help_col=7)
    row = s.field(row, "Zip / postcode", cfg.business.postcode)
    row = s.field(row, "Country", cfg.business.country, value_end=5,
                  help_col=7)
    row = s.field(row, "Tax / VAT number", cfg.business.tax_id,
                  value_end=5, help_col=7)
    row = s.field(row, "Licence number", cfg.business.licence,
                  name="BusinessLicence", value_end=5, help_col=7,
                  help_text="Pesticide applicator or contractor "
                            "licence, if your state or country "
                            "requires one on the paperwork.")
    row = s.field(row, "Insurance policy", cfg.business.insurance,
                  value_end=5, help_col=7,
                  help_text="Liability policy number. Commercial "
                            "customers ask for it.")
    row = s.field(row, "Currency symbol", cfg.currency,
                  name="CurrencySign",
                  help_text="Shown on screen. The cell formats "
                            "follow the symbol you build the file "
                            "with.")
    row = s.field(row, "Currency code", cfg.currency_code,
                  validate=list_from("CurrencyList"))
    row = s.field(row, "Today", None, style="date", name="TodayDate",
                  mode="calc", formula="=TODAY()",
                  help_text="Live. Everything that says 'overdue', "
                            "'due soon' or 'this week' reads this "
                            "one cell.")
    row = s.field(row, "Reporting year", cfg.report_year, style="int",
                  name="ReportYear", validate=number_check(2000, 2100),
                  help_text="The year the Profit Analysis, Monthly "
                            "and Annual reports cover.")
    row = s.field(row, "Year starts", None, style="date",
                  name="YearStart", mode="calc",
                  formula="=DATE(ReportYear,1,1)")
    row = s.field(row, "Year ends", None, style="date",
                  name="YearEnd", mode="calc",
                  formula="=DATE(ReportYear,12,31)")
    row = s.field(row, "This month", None, style="text",
                  name="ThisMonthKey", mode="calc",
                  formula='=TEXT(TODAY(),"yyyy-mm")',
                  help_text="The month key every monthly total "
                            "groups on.")
    row += 1

    # ------------------------------------------------- labour rates --
    row = s.section(row, "What labour costs you", LAST_COL)
    row = s.note(
        row,
        "The crew cost rate is the most important number in this "
        "workbook and the one most often set too low. It is the "
        "loaded cost of an hour of somebody's time - wages, payroll "
        "tax, insurance, holiday, the share of the truck they ride "
        "in - not the figure on their payslip. A $20 wage usually "
        "costs a business between $26 and $30.",
        LAST_COL, height=46)
    row += 1
    row = s.field(row, "Crew cost per hour", cfg.labour_rate,
                  style="money", name="LabourRate",
                  validate=number_check(0, 1000),
                  help_text="Used wherever a person on the Crew "
                            "Database has no rate of their own.")
    row = s.field(row, "Charge-out rate per hour", cfg.charge_rate,
                  style="money", name="ChargeRate",
                  validate=number_check(0, 1000),
                  help_text="What an hour of crew time is worth to "
                            "a customer. Every 'earns per hour' "
                            "column in the workbook is measured "
                            "against this.")
    row = s.field(row, "Overhead per crew hour", cfg.overhead_per_hour,
                  style="money", name="OverheadRate",
                  validate=number_check(0, 1000),
                  help_text="The yard, the insurance, the phone and "
                            "the paperwork, spread over the hours "
                            "you actually work. Take your yearly "
                            "overheads and divide by your billable "
                            "hours - most small operations land "
                            "between $8 and $15.")
    row = s.field(row, "Standard working day", cfg.working_hours_day,
                  style="number1", name="WorkingHours",
                  validate=number_check(1, 24),
                  help_text="Hours in a normal day, used by the crew "
                            "schedule when no times are given.")
    row = s.field(row, "Overtime after", cfg.overtime_after_hours,
                  style="number1", name="OvertimeAfter",
                  validate=number_check(0, 168),
                  help_text="Hours per person per week before "
                            "overtime starts. An indicator for your "
                            "own planning - your payroll provider is "
                            "the authority on overtime law.")
    row = s.field(row, "Overtime multiplier", cfg.overtime_multiplier,
                  style="number1", name="OvertimeRate",
                  validate=number_check(1, 5))
    row = s.field(row, "Default crew size", cfg.crew_size, style="int",
                  name="CrewSize", validate=number_check(1, 20),
                  help_text="How many people go out on a normal "
                            "job.")
    row += 1

    # --------------------------------------------------- the pricing --
    row = s.section(row, "How you price work", LAST_COL)
    row = s.note(
        row,
        "The quote calculator works out what a job costs you, then "
        "adds the target margin. The minimum margin is the line "
        "below which the workbook starts calling a price a problem - "
        "on a quote, on a service, on a customer and on a contract.",
        LAST_COL, height=38)
    row += 1
    row = s.field(row, "Target profit margin", cfg.target_margin,
                  style="percent", name="TargetMargin",
                  validate=number_check(0, 0.95),
                  help_text="Margin, not markup. 45% margin is the "
                            "same as a 1.82 multiplier on cost.")
    row = s.field(row, "Minimum acceptable margin", cfg.minimum_margin,
                  style="percent", name="MinMargin",
                  validate=number_check(0, 0.95),
                  help_text="Anything below this is flagged in red "
                            "wherever it appears.")
    row = s.field(row, "Minimum visit charge", cfg.minimum_visit,
                  style="money", name="MinimumVisit",
                  validate=number_check(0, 10000),
                  help_text="The least you will turn out for. The "
                            "quote calculator uses it as a floor.")
    row = s.field(row, "Materials markup", cfg.material_markup,
                  style="number1", name="MaterialMarkup",
                  validate=number_check(1, 10),
                  help_text="Multiplier on what materials cost you. "
                            "1.35 means a $100 pallet of mulch is "
                            "charged at $135 - collecting, carrying "
                            "and spreading are real work.")
    row = s.field(row, "Travel rate per mile", cfg.travel_rate_mile,
                  style="money", name="TravelRate",
                  validate=number_check(0, 100),
                  help_text="Fuel, tyres and the share of the truck. "
                            "Charged on the round trip, both ways.")
    row = s.field(row, "Default drive time", cfg.drive_time_minutes,
                  style="int", name="DriveMinutes",
                  validate=number_check(0, 600),
                  help_text="Minutes each way, used when a property "
                            "has no drive time of its own.")
    row = s.field(row, "Mowing minutes per 1,000 sq ft",
                  cfg.mow_minutes_per_1000, style="number1",
                  name="MowMinutesPer1000",
                  validate=number_check(0, 600),
                  help_text="Your own measured pace with your own "
                            "machine, for one person. Used to "
                            "estimate mow time on the Property "
                            "Database.")
    row = s.field(row, "Quote valid for", cfg.quote_valid_days,
                  style="int", name="QuoteValidDays",
                  validate=number_check(1, 365),
                  help_text="Days before a quote expires on its own.")
    row += 1

    # ------------------------------------------------------- the tax --
    row = s.section(row, "Tax", LAST_COL)
    row = s.note(
        row,
        "Whether lawn care is taxable where you trade is a question "
        "for your accountant, and the answer differs by state and by "
        "country - mowing and landscaping are often treated "
        "differently from each other. Switch tax on only when you "
        "know which applies to you, and set the rate you are "
        "actually registered for.",
        LAST_COL, height=46)
    row += 1
    row = s.field(row, "Charge tax on services?",
                  "Yes" if cfg.tax_on_services else "No",
                  name="TaxOnServices", validate=yes_no(),
                  help_text="No means no tax is added anywhere in "
                            "the workbook.")
    row = s.field(row, "Tax rate", cfg.tax_rate, style="percent",
                  name="TaxRate", validate=number_check(0, 1))
    row = s.field(row, "What you call it", cfg.tax_name,
                  name="TaxName", value_end=5,
                  help_text="Sales tax, VAT, GST - whatever appears "
                            "on your paperwork.")
    row += 1

    # -------------------------------------------------- when to warn --
    row = s.section(row, "When the workbook should warn you", LAST_COL)
    row = s.note(
        row,
        "Every 'due', 'overdue' and 'chase' message in the workbook "
        "is measured against one of these. Make them match how you "
        "actually work - a round that runs a fortnight ahead needs a "
        "different upcoming window from one booked the night before.",
        LAST_COL, height=38)
    row += 1
    row = s.field(row, "Upcoming window", cfg.upcoming_days,
                  style="int", name="UpcomingDays",
                  validate=number_check(1, 90),
                  help_text="Days ahead counted as 'coming up' on "
                            "the dashboard.")
    row = s.field(row, "Invoice overdue after", cfg.overdue_days,
                  style="int", name="OverdueDays",
                  validate=number_check(0, 90),
                  help_text="Days past the due date before an "
                            "invoice is called overdue.")
    row = s.field(row, "Chase a quote after", cfg.chase_quote_days,
                  style="int", name="ChaseQuoteDays",
                  validate=number_check(1, 180),
                  help_text="Days with no answer before the quote "
                            "appears on the chase list.")
    row = s.field(row, "Contract renewal warning",
                  cfg.renewal_warning_days, style="int",
                  name="RenewalWarnDays", validate=number_check(1, 365),
                  help_text="Days before a review or end date that "
                            "the reminder starts.")
    row = s.field(row, "Customer dormant after", cfg.dormant_days,
                  style="int", name="DormantDays",
                  validate=number_check(7, 999),
                  help_text="Days since the last completed visit "
                            "before a customer is called dormant.")
    row = s.field(row, "Chase a review after", cfg.feedback_chase_days,
                  style="int", name="FeedbackChaseDays",
                  validate=number_check(1, 180))
    row += 1

    # --------------------------------------------------- the machines --
    row = s.section(row, "Equipment servicing", LAST_COL)
    row = s.note(
        row,
        "Mowers measure their lives in engine hours and everything "
        "else measures it in months, so the workbook tracks both and "
        "warns on whichever comes first. These are the defaults; any "
        "machine can carry its own interval on the Equipment "
        "Inventory tab.",
        LAST_COL, height=38)
    row += 1
    row = s.field(row, "Service every (hours)", cfg.service_hours,
                  style="int", name="ServiceHours",
                  validate=number_check(1, 10000),
                  help_text="Engine hours between services. Check "
                            "the manual - 50 to 100 hours is "
                            "typical for commercial mowers.")
    row = s.field(row, "Service every (months)", cfg.service_months,
                  style="int", name="ServiceMonths",
                  validate=number_check(1, 120))
    row = s.field(row, "Warn this many hours before",
                  cfg.service_warning_hours, style="int",
                  name="ServiceWarnHours", validate=number_check(0, 500))
    row = s.field(row, "Warn this many days before",
                  cfg.service_warning_days, style="int",
                  name="ServiceWarnDays", validate=number_check(0, 365))
    row += 1

    # ---------------------------------------------------- the season --
    row = s.section(row, "Your season and your targets", LAST_COL)
    row = s.field(row, "Season starts (month)", cfg.season_start_month,
                  style="int", name="SeasonStart",
                  validate=number_check(1, 12),
                  help_text="The first month of your main cutting "
                            "season. 3 is March.")
    row = s.field(row, "Season ends (month)", cfg.season_end_month,
                  style="int", name="SeasonEnd",
                  validate=number_check(1, 12),
                  help_text="The last month. 11 is November.")
    row = s.field(row, "Revenue target for the year",
                  cfg.target_revenue_year, style="money",
                  name="RevenueTarget",
                  validate=number_check(0, 100000000),
                  help_text="What you want the year to bring in. The "
                            "monthly target is a twelfth of this "
                            "unless you set your own.")
    row = s.field(row, "Jobs per week target", cfg.target_jobs_week,
                  style="int", name="JobsTarget",
                  validate=number_check(0, 1000))
    row = s.field(row, "Fuel price per gallon", cfg.fuel_price,
                  style="money", name="FuelPrice",
                  validate=number_check(0, 100),
                  help_text="For estimating. Actual spend comes off "
                            "the Vehicle & Fuel Tracker.")
    row += 2

    # ------------------------------------------- payment terms table --
    row = s.section(row, "Payment terms", LAST_COL)
    row = s.note(
        row,
        "What each term means in days. Every invoice works out its "
        "own due date from this table, so if your 'Net 30' really "
        "means thirty days from the end of the month, change the "
        "number here. 'Monthly in advance' is negative because the "
        "money is due before the work.",
        LAST_COL, height=38)
    row += 1
    terms_head = row
    s.table_head(terms_head, 1, ["Term", "Days"], widths=[26, 14])
    first_term = terms_head + 1
    for index, (label, days) in enumerate(PAYMENT_TERMS):
        line = first_term + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, days, fmts.input("int"))
    last_term = first_term + len(PAYMENT_TERMS) - 1
    book.define_name(
        "PaymentTermsList",
        f"={sheet_ref}!$B${first_term + 1}:$B${last_term + 1}")
    book.define_name(
        "TermDays",
        f"={sheet_ref}!$C${first_term + 1}:$C${last_term + 1}")
    row = last_term + 2

    # ----------------------------------------------- frequency table --
    row = s.section(row, "How often work repeats", LAST_COL)
    row = s.note(
        row,
        "This table turns 'Fortnightly' into a number of visits and "
        "a number of days. The contracts tab uses the days to work "
        "out when the next visit is due, and the annual value of "
        "every agreement is the price per visit times the visits a "
        "year. 'One-off' is zero on both counts.",
        LAST_COL, height=38)
    row += 1
    freq_head = row
    s.table_head(freq_head, 1,
                 ["How often", "Visits a year", "Days between"],
                 widths=[24, 16, 16])
    first_freq = freq_head + 1
    for index, (label, per_year, gap) in enumerate(FREQUENCIES):
        line = first_freq + index
        s.write(line, 1, label, fmts.input("text"))
        s.write(line, 2, per_year, fmts.input("int"))
        s.write(line, 3, gap, fmts.input("int"))
    last_freq = first_freq + len(FREQUENCIES) - 1
    book.define_name(
        "FrequencyList",
        f"={sheet_ref}!$B${first_freq + 1}:$B${last_freq + 1}")
    book.define_name(
        "VisitsPerYear",
        f"={sheet_ref}!$C${first_freq + 1}:$C${last_freq + 1}")
    book.define_name(
        "DaysBetween",
        f"={sheet_ref}!$D${first_freq + 1}:$D${last_freq + 1}")
    row = last_freq + 2

    # -------------------------------------------------------- prefixes --
    row = s.section(row, "ID prefixes", LAST_COL)
    row = s.note(
        row,
        "The letters in front of every automatic ID. These are the "
        "keys the workbook joins on - Customer IDs, Property IDs, "
        "Job IDs and Invoice IDs above all. Change the prefixes here "
        "if you want to, but do it before you have typed two hundred "
        "customers, not after: existing rows keep the ID they were "
        "given.",
        LAST_COL, height=44)
    row += 1
    half = (len(ID_PREFIX_FIELDS) + 1) // 2
    top = row
    for index, (label, default, name, _digits, hint) in enumerate(
            ID_PREFIX_FIELDS):
        column = 0 if index < half else 4
        line = top + (index if index < half else index - half)
        s.write(line, column + 1, label, fmts.chrome("label_bold"))
        s.write(line, column + 2, default, fmts.input("text"))
        s.write(line, column + 3, hint, fmts.chrome("note"))
        book.define_name(
            name, f"={sheet_ref}!${col_letter(column + 2)}${line + 1}")
    row = top + half + 1

    # ----------------------------------------------------------- lists --
    row = s.section(row, "Drop-down lists", LAST_COL)
    row = s.note(
        row,
        "Add new entries directly under the last one in a column - "
        "every list has room to grow and blank rows are ignored. Do "
        "not delete a whole column: a drop-down pointing at a "
        "missing list stops working. The crew names and vehicle "
        "names are yours to rename - 'Crew A' and 'Truck 1' are "
        "only a starting point.",
        LAST_COL, height=44)
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
        "The months the reports pick from, in plain yyyy-mm text so "
        "that every monthly total in the workbook groups on exactly "
        "the same thing.",
        LAST_COL, height=28)
    row += 1
    keys = _month_keys(cfg.today)
    s.write(row, 0, "Month", fmts.chrome("header"))
    s.set_col(0, 0, 14)
    # Keep the dropdown relevant when the reporting year changes.
    for offset, _key in enumerate(keys):
        s.formula(row + 1 + offset, 0,
                  f'=TEXT(DATE(ReportYear-1,{offset + 1},1),"yyyy-mm")',
                  fmts.calc("text"))
    book.define_name(
        "MonthKeyList",
        f"={sheet_ref}!$A${row + 2}:$A${row + 1 + len(keys)}")
    book.define_name(
        "MonthKeys",
        dynamic_name(NAME, "A", row + 2, row + 1 + len(keys)))
    row = row + len(keys) + 2

    row = s.note(row, ROUTE_NOTE, LAST_COL, height=62)
    row += 1
    row = s.note(row, PAYROLL_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, WEATHER_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, PHOTO_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, HONESTY_NOTE, LAST_COL, height=68)
    row += 1
    row = s.note(row, PRIVACY_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=76)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
