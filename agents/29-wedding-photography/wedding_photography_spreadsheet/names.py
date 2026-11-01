"""Workbook level defined names that point at the register sheets.

The fixed drop-downs - venue types, payment methods, expense categories
- define their own names on `Settings & Lists`.  The names here are the
ones that have to follow live data: the Booking IDs, the couples, the
photographers, the packages you actually sell and the marketing posts
you actually made.  Each is a fixed prepared range, so gaps do not truncate the data and
parallel lookup and value columns stay aligned.

`BookingList` is the important one.  It is the Booking ID column from
`Wedding Bookings`, and it feeds the drop-down on twelve other tabs.
Every join in this workbook runs through it.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    # ---- the join keys, in order of how much work they do -------------
    "BookingList": ("Wedding Bookings", "id"),
    "ClientList": ("Client CRM", "id"),
    "ClientNameList": ("Client CRM", "name"),
    "LeadList": ("Lead Tracker", "id"),
    "StaffList": ("Photographer & Staff", "id"),
    "StaffNameList": ("Photographer & Staff", "name"),
    "PackageList": ("Packages & Pricing", "name"),
    "PackageNameList": ("Packages & Pricing", "name"),
    "CampaignList": ("Marketing Calendar", "id"),
    "EquipmentList": ("Equipment Inventory", "id"),

    # ---- package columns the pricing helpers read ---------------------
    "PackagePriceCol": ("Packages & Pricing", "total_price"),
    "PackageHoursCol": ("Packages & Pricing", "hours"),
    "PackageImagesCol": ("Packages & Pricing", "images"),
    "PackageMarginCol": ("Packages & Pricing", "margin"),
    "PackageSoldCol": ("Packages & Pricing", "sold"),
    "PackageRevenueCol": ("Packages & Pricing", "revenue"),
    "PackageActiveCol": ("Packages & Pricing", "active"),
    "PackageTierCol": ("Packages & Pricing", "tier"),

    # ---- booking columns - the busiest ranges in the workbook ---------
    "BookingClient": ("Wedding Bookings", "client"),
    "BookingCouple": ("Wedding Bookings", "client_name"),
    "BookingDate": ("Wedding Bookings", "wedding_date"),
    "BookingDateNum": ("Wedding Bookings", "wed_num"),
    "BookingStatusCol": ("Wedding Bookings", "status"),
    "BookingPackage": ("Wedding Bookings", "package"),
    "BookingVenue": ("Wedding Bookings", "venue"),
    "BookingVenueType": ("Wedding Bookings", "venue_type"),
    "BookingPhotographer": ("Wedding Bookings", "photographer"),
    "BookingSecond": ("Wedding Bookings", "second"),
    "BookingMonths": ("Wedding Bookings", "month"),
    "BookingYears": ("Wedding Bookings", "year"),
    "BookingSeason": ("Wedding Bookings", "season"),
    "BookingValue": ("Wedding Bookings", "total_value"),
    "BookingCollected": ("Wedding Bookings", "collected"),
    "BookingOutstanding": ("Wedding Bookings", "outstanding"),
    "BookingProfit": ("Wedding Bookings", "profit"),
    "BookingMargin": ("Wedding Bookings", "margin"),
    "BookingHours": ("Wedding Bookings", "coverage_hours"),
    "BookingHolds": ("Wedding Bookings", "holds"),
    "BookingEarns": ("Wedding Bookings", "earns"),
    "BookingShot": ("Wedding Bookings", "shot"),
    "BookingDaysAway": ("Wedding Bookings", "days_away"),
    "BookingAlert": ("Wedding Bookings", "alert"),
    "BookingRowNum": ("Wedding Bookings", "seq_num"),
    "BookingProfitRank": ("Wedding Bookings", "profit_rank"),
    "BookingCeremony": ("Wedding Bookings", "ceremony_time"),
    "BookingContract": ("Wedding Bookings", "contract_state"),
    "BookingGallery": ("Wedding Bookings", "gallery_state"),
    "BookingEditing": ("Wedding Bookings", "editing_state"),

    # ---- the enquiry funnel -------------------------------------------
    "LeadDate": ("Lead Tracker", "enquiry_date"),
    "LeadDateNum": ("Lead Tracker", "enq_num"),
    "LeadSourceCol": ("Lead Tracker", "source"),
    "LeadStatusCol": ("Lead Tracker", "status"),
    "LeadMonths": ("Lead Tracker", "month"),
    "LeadOpen": ("Lead Tracker", "is_open"),
    "LeadWon": ("Lead Tracker", "is_won"),
    "LeadValue": ("Lead Tracker", "booked_value"),
    "LeadCampaign": ("Lead Tracker", "campaign"),
    "LeadWeddingDate": ("Lead Tracker", "wedding_date"),

    # ---- money in and money out ---------------------------------------
    "PaymentBooking": ("Payments & Invoices", "booking"),
    "PaymentMonths": ("Payments & Invoices", "month"),
    "PaymentDueNum": ("Payments & Invoices", "due_num"),
    "PaymentPaidNum": ("Payments & Invoices", "paid_num"),
    "PaymentAmount": ("Payments & Invoices", "amount"),
    "PaymentReceived": ("Payments & Invoices", "received"),
    "PaymentNet": ("Payments & Invoices", "net"),
    "PaymentBalance": ("Payments & Invoices", "balance"),
    "PaymentFee": ("Payments & Invoices", "fee"),
    "PaymentStatusCol": ("Payments & Invoices", "status"),
    "PaymentLate": ("Payments & Invoices", "is_late"),
    "ExpenseMonths": ("Expense Tracker", "month"),
    "ExpenseYears": ("Expense Tracker", "year"),
    "ExpenseDateNum": ("Expense Tracker", "date_num"),
    "ExpenseCategoryCol": ("Expense Tracker", "category"),
    "ExpenseAmounts": ("Expense Tracker", "amount"),
    "ExpenseClaimable": ("Expense Tracker", "claimable"),
    "ExpenseBooking": ("Expense Tracker", "booking"),
    "ExpenseOverhead": ("Expense Tracker", "is_overhead"),
    "ExpenseCapital": ("Expense Tracker", "is_capital"),
    "ExpenseMonthly": ("Expense Tracker", "monthly"),

    # ---- the work -------------------------------------------------------
    "TimelineBooking": ("Wedding Timeline", "booking"),
    "TimelineKey": ("Wedding Timeline", "day_key"),
    "TimelineStart": ("Wedding Timeline", "start"),
    "TimelineFinish": ("Wedding Timeline", "finish"),
    "TimelineShown": ("Wedding Timeline", "shown"),
    "TimelineWho": ("Wedding Timeline", "staff_name"),
    "TimelineWhere": ("Wedding Timeline", "location"),
    "TimelineCritical": ("Wedding Timeline", "critical"),
    "TimelineDone": ("Wedding Timeline", "done"),
    "ShotBooking": ("Shot List Manager", "booking"),
    "ShotGroupCol": ("Shot List Manager", "group_name"),
    "ShotText": ("Shot List Manager", "shot"),
    "ShotPeople": ("Shot List Manager", "people"),
    "ShotMustHave": ("Shot List Manager", "must_have"),
    "ShotDone": ("Shot List Manager", "done"),
    "ShotOpen": ("Shot List Manager", "open"),
    "EditBooking": ("Editing Workflow", "booking"),
    "EditStage": ("Editing Workflow", "stage"),
    "EditProgress": ("Editing Workflow", "progress"),
    "EditDue": ("Editing Workflow", "due"),
    "EditDueNum": ("Editing Workflow", "due_num"),
    "EditLate": ("Editing Workflow", "late"),
    "EditHours": ("Editing Workflow", "hours"),
    "EditCost": ("Editing Workflow", "cost"),
    "GalleryBooking": ("Gallery & Delivery", "booking"),
    "GalleryStatusCol": ("Gallery & Delivery", "status"),
    "GalleryDelivered": ("Gallery & Delivery", "is_delivered"),
    "GalleryDeliveredNum": ("Gallery & Delivery", "delivered_num"),
    "GalleryAfterSales": ("Gallery & Delivery", "after_total"),
    "GalleryExpires": ("Gallery & Delivery", "expires"),

    # ---- everything else the dashboard and the reports scan -------------
    "TravelBooking": ("Travel & Mileage", "booking"),
    "TravelMonths": ("Travel & Mileage", "month"),
    "TravelMiles": ("Travel & Mileage", "all_miles"),
    "TravelCost": ("Travel & Mileage", "total_cost"),
    "TravelCharged": ("Travel & Mileage", "chargeable"),
    "MarketingMonths": ("Marketing Calendar", "month"),
    "MarketingPlatformCol": ("Marketing Calendar", "platform"),
    "MarketingSpend": ("Marketing Calendar", "true_cost"),
    "MarketingRevenue": ("Marketing Calendar", "revenue"),
    "MarketingEnquiries": ("Marketing Calendar", "all_enquiries"),
    "ReviewBooking": ("Reviews & Referrals", "booking"),
    "ReviewMonths": ("Reviews & Referrals", "month"),
    "ReviewRating": ("Reviews & Referrals", "rating"),
    "ReviewPhotographer": ("Reviews & Referrals", "photographer"),
    "ReviewQuote": ("Reviews & Referrals", "quote"),
    "ReviewHas": ("Reviews & Referrals", "has_review"),
    "ContractBooking": ("Contracts & Documents", "booking"),
    "ContractStatusCol": ("Contracts & Documents", "status"),
    "ContractDone": ("Contracts & Documents", "is_done"),
    "EquipmentStatusCol": ("Equipment Inventory", "status"),
    "EquipmentValue": ("Equipment Inventory", "price"),
    "EquipmentInsured": ("Equipment Inventory", "insured"),
    "ProfitBooking": ("Profit Analysis", "booking"),
    "ProfitNet": ("Profit Analysis", "net_profit"),
    "ProfitPerHour": ("Profit Analysis", "per_hour"),
    "ProfitRankCol": ("Profit Analysis", "net_profit_rank"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    missing = []
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            missing.append(f"{name}: no sheet {sheet!r}")
            continue
        spec = reg[sheet]
        if not any(c.key == key for c in spec.columns):
            missing.append(f"{name}: {sheet!r} has no column {key!r}")
            continue
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
    if missing:
        raise KeyError("defined names point at nothing: "
                       + "; ".join(missing))
