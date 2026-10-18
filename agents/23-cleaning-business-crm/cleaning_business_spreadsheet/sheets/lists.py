"""Lists - the source of every drop-down."""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import (CONDITION_FACTORS, Config, DONE_STATUSES,
                      FREQUENCIES, FREQUENCY_FACTORS, INVOICE_STATUSES,
                      JOB_STATUSES, Palette, QUOTE_STATUSES)
from ..formats import FormatBook
from ..layout import Registry

# column letter -> (title, list)
COLUMNS: List[tuple] = [
    ("Job Statuses", JOB_STATUSES),
    ("Done Statuses", DONE_STATUSES),
    ("Quote Statuses", QUOTE_STATUSES),
    ("Invoice Statuses", INVOICE_STATUSES),
    ("Frequencies", FREQUENCIES),
    ("Frequency Price Factor", [f"{k}:{v:.2f}"
                                for k, v in FREQUENCY_FACTORS.items()]),
    ("Condition Factors", [f"{k}:{v:.2f}"
                           for k, v in CONDITION_FACTORS.items()]),
    ("Property Types", ["House", "Apartment", "Condo", "Office", "Retail",
                        "Restaurant", "Warehouse", "School", "Medical",
                        "Airbnb / Rental", "Other"]),
    ("Client Types", ["Residential", "Commercial", "Both"]),
    ("Lead Sources", ["Referral", "Google", "Facebook", "Instagram",
                      "Yelp", "Flyer", "Website", "Walk-in", "Partner",
                      "Other"]),
    ("Payment Methods", ["Cash", "Card", "Bank transfer", "Check",
                         "Online", "Direct debit", "Other"]),
    ("Expense Categories", ["Payroll", "Supplies", "Equipment", "Fuel",
                            "Insurance", "Rent", "Utilities", "Marketing",
                            "Training", "Repairs", "Software", "Fees",
                            "Taxes", "Other"]),
    ("Supply Categories", ["Chemicals", "Paper", "Equipment", "PPE",
                           "Laundry", "Tools", "Other"]),
    ("Equipment Categories", ["Vacuum", "Floor machine",
                              "Pressure washer", "Steamer", "Vehicle",
                              "Tool", "Safety", "Other"]),
    ("Complaint Categories", ["Quality", "Staff conduct", "Communication",
                              "Billing", "Access", "Damage",
                              "Punctuality", "Other"]),
    ("Severity", ["Low", "Medium", "High", "Critical"]),
    ("Rooms / Areas", ["Whole property", "Kitchen", "Bathrooms",
                       "Bedrooms", "Living areas", "Hall & stairs",
                       "Windows", "Floors", "Oven", "Fridge", "Carpet",
                       "Upholstery", "Exterior", "Office area",
                       "Communal areas", "Other"]),
    ("Roles", ["Owner", "Manager", "Team lead", "Cleaner", "Driver",
               "Admin", "Contractor"]),
    ("Yes / No", ["Yes", "No"]),
    ("Units", ["hour", "sq ft", "sq m", "room", "bedroom", "bathroom",
               "visit", "fixed", "item"]),
    ("Safety Types", ["Toolbox talk", "Training", "Inspection",
                      "Policy review", "Equipment check",
                      "Risk assessment"]),
    ("Incident Types", ["Injury", "Near miss", "Property damage",
                        "Security", "Vehicle", "Chemical", "Other"]),
    ("Service Categories", ["Residential", "Commercial", "Deep clean",
                            "Specialist", "Add-on"]),
]


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Lists")
    ws.set_tab_color(Palette.line)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)

    ws.merge_range(0, 1, 0, 10, "Lists  ·  Drop-down Sources",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 10,
                   "Every drop-down in the workbook reads from this tab. "
                   "Add a value to the bottom of a list and it appears in "
                   "the drop-downs on new rows - or edit the validation "
                   "source after unprotecting the sheet.",
                   fmts["subtitle"])

    for i, (title, values) in enumerate(COLUMNS):
        col = 1 + i
        ws.set_column(col, col, 18)
        ws.write(3, col, title, fmts["header"])
        for j, value in enumerate(values):
            ws.write(4 + j, col, value, fmts["text"])

    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
