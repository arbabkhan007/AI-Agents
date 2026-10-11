"""
The `Lists` tab: every drop down list in the workbook lives here.

Each column becomes a *dynamic* defined name (OFFSET + COUNTIF) so the user can
add or remove options and every drop down in the workbook follows along.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import List, Tuple

from ..config import Config, Palette
from ..layout import (DATA_ROW, HEADER_ROW, Registry, col_letter,
                      dynamic_name, quote_sheet)
from ..writer import SheetWriter

SHEET = "Lists"

#: name -> (column header, options)
LISTS: "OrderedDict[str, Tuple[str, List[str]]]" = OrderedDict([
    ("YesNoList", ("Yes / No", ["Yes", "No"])),
    ("YesNoNAList", ("Yes / No / N/A", ["Yes", "No", "N/A"])),
    ("ClientStatusList", ("Client status", [
        "Active", "Prospective", "On hold", "Inactive", "Lost"])),
    ("ContactMethodList", ("Preferred contact", [
        "Phone call", "SMS", "Email", "WhatsApp", "App message"])),
    ("ReferralSourceList", ("Referral source", [
        "Google search", "Facebook", "Instagram", "Word of mouth",
        "Client referral", "Vet clinic", "Flyer / poster", "Local directory",
        "Repeat client", "Other"])),
    ("ContractStatusList", ("Contract status", [
        "Not sent", "Sent", "Signed", "Expired", "Renewal due"])),
    ("KeyStatusList", ("Key / access status", [
        "Not held", "Key held", "Key returned", "Lockbox code",
        "Smart lock code", "Owner home"])),
    ("PetTypeList", ("Pet type", [
        "Dog", "Cat", "Bird", "Rabbit", "Guinea pig", "Small animal",
        "Reptile", "Fish", "Other"])),
    ("PetGenderList", ("Pet gender", [
        "Male", "Male (neutered)", "Female", "Female (spayed)", "Unknown"])),
    ("TemperamentList", ("Temperament", [
        "Friendly", "Calm", "Playful", "Energetic", "Shy", "Anxious",
        "Reactive", "Protective", "Needs slow introduction"])),
    ("RiskFlagList", ("Risk flag", [
        "None", "Bite risk", "Escape artist", "Door dasher",
        "Pulls on lead", "Not dog friendly", "Not cat friendly",
        "Resource guarding", "Needs muzzle", "Medical risk", "Other"])),
    ("ServiceCategoryList", ("Service category", [
        "Dog walking", "Drop-in visit", "Pet sitting", "Overnight stay",
        "House sitting", "Feeding visit", "Puppy care", "Senior pet care",
        "Medication visit", "Pet transport", "Add-on"])),
    ("BillingUnitList", ("Billing unit", [
        "Per visit", "Per hour", "Per night", "Per walk", "Per day",
        "Flat fee"])),
    ("BookingStatusList", ("Booking status", [
        "Enquiry", "Pending", "Confirmed", "In progress", "Completed",
        "Cancelled", "No show"])),
    ("RecurringList", ("Recurring pattern", [
        "None", "Daily", "Weekdays", "Weekly", "Fortnightly", "Monthly"])),
    ("DiscountTypeList", ("Discount type", [
        "None", "Loyalty", "Promotional", "Package", "Multi-pet",
        "Goodwill", "Custom"])),
    ("CancelReasonList", ("Cancellation reason", [
        "Client cancelled", "Client away", "Pet unwell", "Weather",
        "Staff unavailable", "Double booked", "Payment issue",
        "Rescheduled", "No reason given", "Other"])),
    ("VisitStatusList", ("Visit status", [
        "Scheduled", "Completed", "Partially completed", "Missed",
        "Cancelled"])),
    ("MoodList", ("Pet mood", [
        "Happy", "Calm", "Playful", "Sleepy", "Anxious", "Lethargic",
        "Unwell", "Aggressive"])),
    ("AppetiteList", ("Appetite / intake", [
        "Normal", "Reduced", "None", "Increased", "Not offered"])),
    ("PottyList", ("Potty / litter", [
        "Pee only", "Poo only", "Both", "None", "Litter cleaned",
        "Accident indoors"])),
    ("HealthRecordTypeList", ("Health record type", [
        "Medication", "Vaccination", "Vet visit", "Health observation",
        "Treatment", "Grooming", "Other"])),
    ("MedStatusList", ("Medication status", [
        "Scheduled", "Given", "Missed", "Refused", "Not required"])),
    ("IncidentTypeList", ("Incident type", [
        "Bite / nip", "Escape", "Injury", "Illness", "Property damage",
        "Lost key", "Vehicle incident", "Aggression", "Theft", "Other"])),
    ("SeverityList", ("Severity", ["Low", "Medium", "High", "Critical"])),
    ("IncidentStatusList", ("Incident status", [
        "Open", "In progress", "Resolved", "Closed"])),
    ("MessageTypeList", ("Message type", [
        "Booking confirmation", "Booking reminder", "Visit update",
        "Payment reminder", "Follow-up", "Thank you", "Referral thank-you",
        "Birthday / anniversary", "Complaint", "Review request",
        "Win-back offer", "Other"])),
    ("ChannelList", ("Channel", [
        "Phone call", "SMS", "Email", "WhatsApp", "In person",
        "App message", "Social media"])),
    ("DirectionList", ("Direction", ["Outgoing", "Incoming"])),
    ("ResolutionList", ("Resolution status", [
        "Not required", "Open", "In progress", "Resolved"])),
    ("InvoiceStatusList", ("Invoice status", [
        "Draft", "Sent", "Paid", "Partially paid", "Cancelled",
        "Refunded"])),
    ("PaymentMethodList", ("Payment method", [
        "Cash", "Bank transfer", "Card - in person", "Card - online",
        "Digital wallet", "Direct debit", "Cheque", "Other"])),
    ("ExpenseCategoryList", ("Expense category", [
        "Fuel", "Vehicle maintenance", "Parking & tolls", "Pet supplies",
        "Pet food & treats", "Cleaning supplies", "Equipment",
        "Marketing & advertising", "Software & subscriptions", "Insurance",
        "Licences & permits", "Staff wages", "Contractor payments",
        "Training & certification", "Phone & internet", "Office & admin",
        "Vet & emergency supplies", "Bank & merchant fees", "Other"])),
    ("ExpenseApprovalList", ("Approval status", [
        "Pending", "Approved", "Rejected", "Reimbursed"])),
    ("BusinessPersonalList", ("Business / personal", [
        "Business", "Personal", "Mixed"])),
    ("RecurringExpenseList", ("Recurring expense", [
        "No", "Weekly", "Fortnightly", "Monthly", "Quarterly", "Annually"])),
    ("TripPurposeList", ("Trip purpose", [
        "Client visit", "Dog walk", "Supplies run", "Vet trip",
        "Admin / bank", "Marketing", "Training", "Personal"])),
    ("StaffRoleList", ("Staff role", [
        "Owner", "Dog walker", "Pet sitter", "Assistant", "Admin",
        "Contractor", "Trainee"])),
    ("EmploymentTypeList", ("Employment type", [
        "Employee - full time", "Employee - part time", "Casual",
        "Contractor", "Volunteer"])),
    ("PayTypeList", ("Pay type", [
        "Hourly", "Per visit", "Salary", "Commission %"])),
    ("StaffStatusList", ("Staff status", ["Active", "On leave", "Inactive"])),
    ("InventoryCategoryList", ("Inventory category", [
        "Pet food", "Treats", "Medication", "First aid", "Cleaning",
        "Waste bags", "Leads & harnesses", "Toys", "Equipment", "Office",
        "Other"])),
    ("PriorityList", ("Priority", ["Low", "Medium", "High", "Urgent"])),
    ("TaskStatusList", ("Task status", [
        "Not started", "In progress", "Waiting", "Done", "Cancelled"])),
    ("RatingList", ("Satisfaction rating", ["1", "2", "3", "4", "5"])),
    ("MonthList", ("Dashboard period", [
        "All year", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"])),
])

ROWS = 40


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, SHEET,
                        tab_color=Palette.grey_text)
    last_col = len(LISTS) - 1
    sheet.banner(
        "Customisable Drop Down Lists",
        "Edit, add or delete options below - every drop down in the workbook "
        "updates automatically. Keep each list in one unbroken block, "
        "starting in row 5.",
        last_col,
        tail_text="TIP: lists grow automatically (up to row 44). Deleting "
                  "an option does not change records that already use it.")

    header_fmt = fmts.chrome("header")
    input_fmt = fmts.input("text")
    for idx, (name, (header, values)) in enumerate(LISTS.items()):
        sheet.set_col(idx, idx, max(16, min(26, len(header) + 8)), input_fmt)
        sheet.write(HEADER_ROW - 1, idx, header, header_fmt)
        for offset, value in enumerate(values):
            sheet.write(DATA_ROW - 1 + offset, idx, value, input_fmt)
        book.define_name(name, dynamic_name(SHEET, col_letter(idx),
                                            DATA_ROW, DATA_ROW + ROWS - 1))

    sheet.ws.set_row(HEADER_ROW - 1, 30)
    sheet.ws.freeze_panes(HEADER_ROW, 0)
    sheet.finish(fit_width=False)
    return sheet


def ref(name: str) -> str:
    """A1 reference to this list's column on the current row, e.g.

        Lists!$AH{r}

    Used by the hidden Calc sheet to mirror a list down a block of rows.
    """
    idx = list(LISTS).index(name)
    return f"{quote_sheet(SHEET)}!${col_letter(idx)}{{r}}"


def options(name: str) -> List[str]:
    """Static copy of a list (used for sample data sanity)."""
    return list(LISTS[name][1])
