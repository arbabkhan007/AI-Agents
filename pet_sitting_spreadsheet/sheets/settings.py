"""
The `Settings` tab.

Every rate, surcharge, prefix and reminder window used by the rest of the
workbook is entered once here and published as a defined name (TaxRate,
MileageRate, PaymentTermsDays ...) so the formulas stay readable.
"""

from __future__ import annotations

import datetime as _dt

from ..config import Config, Palette
from ..layout import Registry, col_letter, quote_sheet
from ..writer import SheetWriter, date_check, list_from, number_check

SHEET = "Settings"
LAST_COL = 8

HOLIDAY_ROWS = 30


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, SHEET, tab_color=Palette.accent)
    b = cfg.business

    s.banner("Business Setup & Settings",
             "Fill in the cream cells once. Grey cells are locked formulas. "
             "Everything else in the workbook reads these values.",
             LAST_COL)

    s.set_col(0, 0, 2.5)
    s.set_col(1, 1, 24, fmts.chrome("label"))
    s.set_col(2, 2, 16, fmts.chrome("label"))
    s.set_col(3, 3, 26)
    s.set_col(4, 4, 18)
    s.set_col(5, 8, 17, fmts.chrome("note"))

    r = 4  # 0 based row index -> Excel row 5
    r = s.section(r, "1. Business details (used on invoices and printables)",
                  LAST_COL)
    r = s.field(r, "Business name", b.name, name="Biz_Name", value_end=4,
                help_text="Shown on every printable form and invoice.")
    r = s.field(r, "Owner / main contact", b.owner, name="Biz_Owner",
                value_end=4)
    r = s.field(r, "Phone", b.phone, name="Biz_Phone", value_end=4)
    r = s.field(r, "Email", b.email, name="Biz_Email", value_end=4)
    r = s.field(r, "Website / social", b.website, name="Biz_Web", value_end=4)
    r = s.field(r, "Street address", b.address, name="Biz_Address",
                value_end=4)
    r = s.field(r, "City / suburb", b.city, name="Biz_City", value_end=4)
    r = s.field(r, "State / region", b.state, name="Biz_State", value_end=4)
    r = s.field(r, "Post / ZIP code", b.postcode, name="Biz_Post",
                value_end=4)
    r = s.field(r, "Country", b.country, name="Biz_Country", value_end=4)
    r = s.field(r, "Business / tax number", b.tax_id, name="Biz_TaxID",
                value_end=4)
    r = s.field(r, "Payment details for invoices", b.bank_details,
                name="Biz_Bank", value_end=4,
                help_text="Bank account, payment link or app handle.")
    r = s.field(r, "Insurance provider", b.insurance_provider,
                name="Biz_Insurer", value_end=4)
    r = s.field(r, "Insurance policy number", b.insurance_policy,
                name="Biz_Policy", value_end=4)
    r = s.field(r, "Insurance renewal date",
                cfg.today + _dt.timedelta(days=120), style="date",
                name="Biz_InsuranceRenewal", validate=date_check(),
                help_text="Feeds the renewal reminder on the Reminders tab.")
    r = s.field(r, "Licence / permit", b.licence_name, name="Biz_Licence",
                value_end=4)
    r = s.field(r, "Licence renewal date",
                cfg.today + _dt.timedelta(days=210), style="date",
                name="Biz_LicenceRenewal", validate=date_check())
    r += 1

    r = s.section(r, "2. Logo & branding", LAST_COL)
    r = s.note(r, "To add your logo: unprotect the sheet (Review > Unprotect "
                  f"Sheet, password '{cfg.password}'), click Insert > "
                  "Pictures, place the image in the box below, then protect "
                  "the sheet again. The printable forms have their own logo "
                  "placeholders.", LAST_COL, first_col=1, height=38)
    s.merge(r, 1, 3, "LOGO PLACEHOLDER - insert your image here",
            fmts.chrome("legend_calc", align="center"), row2=r + 3)
    r += 5

    r = s.section(r, "3. Currency, date & time formats", LAST_COL)
    r = s.field(r, "Currency symbol", cfg.currency_symbol,
                name="CurrencySymbol",
                help_text="Display only. To change the cell formatting use "
                          "Format Cells > Currency on the money columns.")
    r = s.field(r, "Currency code", cfg.currency_code, name="CurrencyCode")
    r = s.field(r, "Date format in use", cfg.date_format.upper(),
                mode="plain", help_text="Select a date column and use Format "
                                        "Cells to switch to your local style.")
    r = s.field(r, "Time format in use", cfg.time_format,
                mode="plain", help_text="24 hour clock: format as hh:mm.")
    r = s.field(r, "Distance unit", cfg.distance_unit, name="DistanceUnit",
                validate={"validate": "list", "source": ["km", "miles"]})
    r = s.field(r, "Financial year starts", _dt.date(cfg.today.year, 1, 1),
                style="date", name="FY_Start", validate=date_check())
    r += 1

    r = s.section(r, "4. Tax settings", LAST_COL)
    r = s.field(r, "Tax name", cfg.tax_name, name="TaxName",
                help_text="GST, VAT, Sales Tax ...")
    r = s.field(r, "Registered for tax?", cfg.tax_registered,
                name="TaxRegistered", validate=list_from("YesNoList"),
                help_text="No = tax is never added to bookings or invoices.")
    r = s.field(r, "Tax rate", cfg.tax_rate, style="percent", name="TaxRate",
                validate=number_check(0, 1),
                help_text="Enter as a percentage, e.g. 10%.")
    r = s.field(r, "Prices already include tax?", cfg.prices_include_tax,
                name="PricesIncludeTax", validate=list_from("YesNoList"),
                help_text="Yes = tax is extracted from the price. "
                          "No = tax is added on top.")
    r = s.field(r, "Tax reserve to set aside", cfg.tax_reserve_percent,
                style="percent", name="TaxReservePct",
                validate=number_check(0, 1),
                help_text="Used by the Budget tab to estimate money to park "
                          "for the tax bill.")
    r += 1

    r = s.section(r, "5. Invoicing & payments", LAST_COL)
    r = s.field(r, "Invoice prefix", cfg.invoice_prefix, name="InvoicePrefix")
    r = s.field(r, "First invoice number", cfg.invoice_start_number,
                style="int", name="InvoiceStartNo",
                validate=number_check(1, 999999, decimal=False))
    r = s.field(r, "Payment terms (days)", cfg.payment_terms_days,
                style="int", name="PaymentTermsDays",
                validate=number_check(0, 180, decimal=False),
                help_text="Invoice due date = invoice date + this many days.")
    r = s.field(r, "Standard deposit", cfg.deposit_percent, style="percent",
                name="DepositPct", validate=number_check(0, 1))
    r = s.field(r, "Late fee", cfg.late_fee_percent, style="percent",
                name="LateFeePct", validate=number_check(0, 1),
                help_text="Suggested late fee on overdue invoices.")
    r = s.field(r, "Client ID prefix", cfg.client_prefix, name="ClientPrefix")
    r = s.field(r, "Pet ID prefix", cfg.pet_prefix, name="PetPrefix")
    r = s.field(r, "Booking ID prefix", cfg.booking_prefix,
                name="BookingPrefix")
    r += 1

    r = s.section(r, "6. Pricing, surcharges & discounts", LAST_COL)
    r = s.field(r, "Additional pet fee (default)", cfg.extra_pet_fee,
                style="money", name="ExtraPetFeeDefault",
                validate=number_check(0, 10000),
                help_text="Used when a service has no fee of its own.")
    r = s.field(r, "Holiday surcharge", cfg.holiday_surcharge,
                style="percent", name="HolidaySurcharge",
                validate=number_check(0, 2))
    r = s.field(r, "Weekend surcharge", cfg.weekend_surcharge,
                style="percent", name="WeekendSurcharge",
                validate=number_check(0, 2))
    r = s.field(r, "Emergency / last-minute fee", cfg.emergency_fee,
                style="money", name="EmergencyFee",
                validate=number_check(0, 10000))
    r = s.field(r, "Last-minute window (days)", cfg.last_minute_days,
                style="int", name="LastMinuteDays",
                validate=number_check(0, 30, decimal=False),
                help_text="Booked this close to the visit = emergency fee.")
    r = s.field(r, "Loyalty discount", cfg.loyalty_discount, style="percent",
                name="LoyaltyDiscount", validate=number_check(0, 1))
    r = s.field(r, "Loyalty threshold (bookings)", cfg.loyalty_threshold,
                style="int", name="LoyaltyThreshold",
                validate=number_check(0, 1000, decimal=False),
                help_text="Clients above this many bookings are flagged for "
                          "the loyalty discount.")
    r = s.field(r, "Average staff cost per hour", cfg.staff_cost_rate,
                style="money", name="StaffCostRate",
                validate=number_check(0, 1000),
                help_text="Used for service profitability estimates.")
    r += 1

    r = s.section(r, "7. Travel & mileage", LAST_COL)
    r = s.field(r, f"Mileage rate per {cfg.distance_unit}", cfg.mileage_rate,
                style="money", name="MileageRate",
                validate=number_check(0, 100),
                help_text="Your tax office reimbursement rate.")
    r = s.field(r, f"Client travel fee per {cfg.distance_unit}",
                cfg.travel_fee_per_unit, style="money", name="TravelFeeRate",
                validate=number_check(0, 100))
    r = s.field(r, f"Free travel distance ({cfg.distance_unit})",
                cfg.free_travel_distance, style="number1",
                name="FreeTravelDistance", validate=number_check(0, 1000),
                help_text="Travel inside this radius is not charged.")
    r = s.field(r, "Travel time allowance (mins)", cfg.travel_time_minutes,
                style="int", name="TravelTimeMins",
                validate=number_check(0, 240, decimal=False),
                help_text="Added to each booking when planning the day.")
    r += 1

    r = s.section(r, "8. Reminders, alerts & operations", LAST_COL)
    r = s.field(r, "Booking reminder lead (days)", cfg.reminder_lead_days,
                style="int", name="ReminderLeadDays",
                validate=number_check(0, 60, decimal=False))
    r = s.field(r, "Vaccination alert (days before)",
                cfg.vaccination_alert_days, style="int", name="VaccAlertDays",
                validate=number_check(0, 365, decimal=False))
    r = s.field(r, "Inactive client after (days)", cfg.inactive_client_days,
                style="int", name="InactiveDays",
                validate=number_check(0, 999, decimal=False))
    r = s.field(r, "Follow-up after service (days)", cfg.follow_up_days,
                style="int", name="FollowUpDays",
                validate=number_check(0, 365, decimal=False))
    r = s.field(r, "Expiry / renewal alert (days)", cfg.expiry_alert_days,
                style="int", name="ExpiryAlertDays",
                validate=number_check(0, 365, decimal=False))
    r = s.field(r, "Default visit length (mins)", cfg.default_visit_minutes,
                style="int", name="DefaultVisitMins",
                validate=number_check(0, 1440, decimal=False))
    r = s.field(r, "Working day starts", _time(cfg.day_start), style="time",
                name="DayStart")
    r = s.field(r, "Working day ends", _time(cfg.day_end), style="time",
                name="DayEnd")
    r += 1

    # ------------------------------------------------------------ holidays
    r = s.section(r, "9. Public holidays & peak dates (holiday surcharge)",
                  LAST_COL)
    r = s.note(r, "Any booking dated on one of these days automatically picks "
                  "up the holiday surcharge set above.", LAST_COL,
               first_col=1, height=20)
    head_row = r
    s.write(head_row, 1, "Date", fmts.chrome("header_left"))
    s.write(head_row, 2, "Occasion", fmts.chrome("header"))
    s.write(head_row, 3, "Notes", fmts.chrome("header"))
    s.ws.set_row(head_row, 22)

    first_holiday = head_row + 1
    date_fmt = fmts.input("date")
    text_fmt = fmts.input("text")
    for i in range(HOLIDAY_ROWS):
        s.ws.write_blank(first_holiday + i, 1, None, date_fmt)
        s.ws.write_blank(first_holiday + i, 2, None, text_fmt)
        s.ws.write_blank(first_holiday + i, 3, None, text_fmt)

    if cfg.include_sample_data:
        year = cfg.today.year
        samples = [
            (_dt.date(year, 1, 1), "New Year's Day", "Peak demand"),
            (_dt.date(year, 7, 4), "Independence Day", "Peak demand"),
            (_dt.date(year, 11, 26), "Thanksgiving", "Overnight bookings"),
            (_dt.date(year, 12, 24), "Christmas Eve", "Holiday surcharge"),
            (_dt.date(year, 12, 25), "Christmas Day", "Holiday surcharge"),
            (_dt.date(year, 12, 26), "Boxing Day", "Holiday surcharge"),
            (_dt.date(year, 12, 31), "New Year's Eve", "Holiday surcharge"),
            (_dt.date(year + 1, 1, 1), "New Year's Day", "Holiday surcharge"),
        ]
        for i, (day, name, note) in enumerate(samples):
            s.ws.write_datetime(first_holiday + i, 1, day, date_fmt)
            s.write(first_holiday + i, 2, name, text_fmt)
            s.write(first_holiday + i, 3, note, text_fmt)

    s.ws.data_validation(first_holiday, 1, first_holiday + HOLIDAY_ROWS - 1, 1,
                         date_check())
    last_holiday = first_holiday + HOLIDAY_ROWS
    book.define_name(
        "HolidayDates",
        f"={quote_sheet(SHEET)}!$B${first_holiday + 1}:$B${last_holiday}")

    r = last_holiday + 1
    r = s.note(r, "Backup tip: save a dated copy of this workbook at the end "
                  "of every month (File > Save As > add the date to the file "
                  "name). Keep client addresses and access codes private - "
                  "see the Help tab for data protection guidance.",
               LAST_COL, first_col=1, height=34)

    s.finish(freeze_row=4, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{r + 2}")
    return s


def _time(text: str) -> _dt.time:
    hour, minute = text.split(":")
    return _dt.time(int(hour), int(minute))
