"""20 Settings & Lists - every rate, rule and drop-down source."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import (APPOINTMENT_STATUSES, BOOKING_CHANNELS,
                      COMMISSION_METHODS, CONSENT, Config,
                      CATEGORY_COMMISSION_DEFAULT, EXPENSE_CATEGORIES,
                      PAYMENT_KINDS, PAYMENT_METHODS, PREF_CONTACT,
                      PRODUCT_CATEGORIES, PURCHASE_STATUSES, RECURRING,
                      SERVICE_CATEGORIES, STAFF_STATUSES, STAFF_TYPES,
                      TX_TYPES)
from ..layout import col_letter, dynamic_name
from ..writer import SheetWriter
from . import common as C

NAME = "20 Settings & Lists"

LISTS = [
    ("list_status", "Booking statuses", APPOINTMENT_STATUSES),
    ("list_methods", "Payment methods", PAYMENT_METHODS),
    ("list_kinds", "Payment kinds", PAYMENT_KINDS),
    ("list_channels", "Channels & sources", BOOKING_CHANNELS),
    ("list_cats", "Service categories", SERVICE_CATEGORIES),
    ("list_expcats", "Expense categories", EXPENSE_CATEGORIES),
    ("list_staffstatus", "Staff statuses", STAFF_STATUSES),
    ("list_stafftypes", "Staff types", STAFF_TYPES),
    ("list_commmethods", "Commission methods", COMMISSION_METHODS),
    ("list_txtypes", "Sale types", TX_TYPES),
    ("list_purchstatus", "Purchase statuses", PURCHASE_STATUSES),
    ("list_consent", "Yes / No", CONSENT),
    ("list_prefcontact", "Preferred contact", PREF_CONTACT),
    ("list_recurring", "Recurring", RECURRING),
    ("list_prodcats", "Product types", PRODUCT_CATEGORIES),
]
LIST_SLOTS = 40          # editable rows per list
PER_BAND = 5             # lists side by side


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color="#241F26", landscape=False)
    last = 9
    sheet.banner("20  Settings & Lists",
                 "Every rate, rule and drop-down list in one place - "
                 "change a value here and the whole workbook follows.",
                 last)
    row = 4
    row = sheet.section(row, "BUSINESS", last)
    row = sheet.field(row, "Salon name", cfg.salon_name, name="SalonName")
    row = sheet.field(row, "Owner name", cfg.owner_name, name="OwnerName")
    row += 1

    row = sheet.section(row, "TAX & FEES (CONFIGURABLE - NOT ADVICE)", last)
    row = sheet.field(row, "Sales tax / VAT rate", cfg.tax_rate,
                      style="percent", name="TaxRate",
                      help_text="Applied to taxable services and products "
                                "on tab 6. Set 0 if your region has none.")
    row = sheet.field(row, "Tax reserve rate", cfg.tax_reserve_rate,
                      style="percent", name="TaxReserveRate",
                      help_text="Share of operating profit the P&L "
                                "suggests setting aside.")
    row = sheet.field(row, "Employer payroll reserve",
                      cfg.payroll_tax_rate, style="percent",
                      name="PayrollTaxRate")
    row = sheet.field(row, "Card processing fee", cfg.card_fee_rate,
                      style="percent", name="CardFeeRate")
    row = sheet.field(row, "Cash handling fee", cfg.cash_fee_rate,
                      style="percent", name="CashFeeRate")
    row = sheet.field(row, "Bank transfer fee", cfg.bank_fee_rate,
                      style="percent", name="BankFeeRate")
    row = sheet.field(row, "Other method fee", cfg.other_fee_rate,
                      style="percent", name="OtherFeeRate")
    row += 1

    row = sheet.section(row, "LOYALTY & REBOOKING", last)
    row = sheet.field(row, "Points per visit", cfg.points_per_visit,
                      style="number1", name="PointsPerVisit")
    row = sheet.field(row, "Reward threshold (points)",
                      cfg.reward_threshold, style="number1",
                      name="RewardThreshold")
    row = sheet.field(row, "Referral credit", cfg.referral_reward,
                      style="money", name="ReferralReward")
    row = sheet.field(row, "Rebooking interval (days)", cfg.rebook_days,
                      style="int", name="RebookDays",
                      help_text="Drives CRM status and the rebook "
                                "reminder on tab 3.")
    row = sheet.field(row, "Flat commission per service",
                      cfg.flat_commission, style="money",
                      name="FlatCommission")
    row += 1

    row = sheet.section(row, "CATEGORY COMMISSION RATES", last)
    sheet.table_head(row, 0, ["Category", "Commission rate"])
    cat_first = row + 1
    for i, cat in enumerate(SERVICE_CATEGORIES):
        r = cat_first + i
        sheet.write(r, 0, cat, sheet.f.calc("text"))
        sheet.write(r, 1, CATEGORY_COMMISSION_DEFAULT[cat],
                    sheet.f.input("percent"))
    book.define_name("CatNames", dynamic_name(
        NAME, "A", cat_first, cat_first + len(SERVICE_CATEGORIES) - 1))
    book.define_name("CatCommRate", dynamic_name(
        NAME, "B", cat_first, cat_first + len(SERVICE_CATEGORIES) - 1,
        count_text=False))
    row = cat_first + len(SERVICE_CATEGORIES) + 1
    row = sheet.note(row,
                     "Used for staff paid on the Category method: each "
                     "sale earns its own category's rate.", last) + 2

    row = sheet.section(row, "DROP-DOWN LISTS (ADD YOUR OWN VALUES)", last)
    geometry = []
    band = 0
    for i, (key, title, values) in enumerate(LISTS):
        slot = i % PER_BAND
        if slot == 0 and i:
            row += LIST_SLOTS + 3
            band += 1
        col = slot * 2
        sheet.merge(row, col, col, title, sheet.f.chrome("subsection"))
        first = row + 1
        for v in range(LIST_SLOTS):
            value = values[v] if v < len(values) else None
            sheet.write(first + v, col, value, sheet.f.input("text"))
        geometry.append((key, col, first))
    for key, col, first in geometry:
        book.define_name(key[0].upper() + key[1:], dynamic_name(
            NAME, col_letter(col), first, first + LIST_SLOTS - 1))
    row += LIST_SLOTS + 2
    row = sheet.note(row,
                     "Type new values under any list - every drop-down in "
                     "the workbook reads these columns live.", last) + 1
    row = sheet.note(row,
                     "Backup and privacy: keep this file on your own "
                     "machine or cloud folder and back it up like any "
                     "business record. It contains no macros and sends "
                     "nothing anywhere.", last) + 1
    C.footer(sheet, cfg, last, row)
    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
