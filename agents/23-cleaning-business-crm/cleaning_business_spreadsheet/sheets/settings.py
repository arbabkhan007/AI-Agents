"""The Settings tab - business profile, pricing and working rules.

Row map matters: the defined names (Business_Name, Tax_Rate,
Hourly_Rate, Minimum_Charge, ...) point at fixed cells on this sheet.
"""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry

#: Fixed cells on this sheet other pages reference (keep rows in sync!).
SETTINGS_CELLS = {
    "business_name": "$C$6", "owner": "$C$7", "email": "$C$8",
    "phone": "$C$9", "address": "$C$10",
    "plan_year": "$C$18", "week_start": "$C$19",
    "currency_symbol": "$C$20", "currency_code": "$C$21",
    "area_unit": "$C$22", "distance_unit": "$C$23",
    "cleaners_per_job": "$C$27", "productive_hours": "$C$28",
    "travel_rate": "$C$29", "travel_minutes": "$C$30",
    "job_reminder_days": "$C$31", "quote_followup_days": "$C$32",
    "quote_valid_days": "$C$33", "inactive_client_days": "$C$34",
    "low_stock_days": "$C$35", "maintenance_days": "$C$36",
    "pay_rate": "$C$39", "overtime_multiplier": "$C$40",
    "employer_oncost": "$C$41", "cost_per_hour": "$C$42",
    "tax_rate": "$C$45", "payment_terms": "$C$46", "late_fee": "$C$47",
    "tax_label": "$C$48", "deposit_pct": "$C$49",
    "rate_per_area": "$C$52", "rate_per_bedroom": "$C$53",
    "rate_per_bathroom": "$C$54", "hourly_rate": "$C$55",
    "rate_per_room": "$C$56", "minimum_charge": "$C$57",
    "deep_uplift": "$C$58", "move_uplift": "$C$59",
    "pet_surcharge": "$C$60", "callout_fee": "$C$61",
    "supplies_per_hour": "$C$62", "target_margin": "$C$63",
    "margin_floor": "$C$64",
    "revenue_target_month": "$C$67", "revenue_target_year": "$C$68",
    "expense_budget_month": "$C$69", "utilisation_target": "$C$70",
    "retention_target": "$C$71", "satisfaction_target": "$C$72",
    "quote_win_target": "$C$73",
}


def settings_ref(key: str) -> str:
    """Absolute reference to a Settings cell, e.g. Settings!$C$55."""
    return f"Settings!{SETTINGS_CELLS[key]}"


def _section(ws, fmts, row: int, text: str) -> None:
    ws.merge_range(row - 1, 1, row - 1, 6, text, fmts["section"])


def _note(ws, fmts, row: int, text: str) -> None:
    ws.merge_range(row - 1, 1, row - 1, 6, text, fmts["note"])
    ws.set_row(row - 1, 26)


def _field(ws, fmts, row: int, label: str, value: Any,
           style: str = "input", note: str = "") -> None:
    ws.write(row - 1, 1, label, fmts["label"])
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        ws.write_number(row - 1, 2, value, fmts[style])
    else:
        ws.write(row - 1, 2, value, fmts[style])
    if note:
        ws.merge_range(row - 1, 3, row - 1, 6, note, fmts["note"])
    else:
        ws.merge_range(row - 1, 3, row - 1, 6, "", fmts["note"])


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Settings")
    ws.set_tab_color(Palette.primary_mid)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 24)
    ws.set_column(3, 6, 16)

    ws.merge_range(0, 1, 0, 6,
                   f"{cfg.product_name}  ·  Settings",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 6,
                   "Set the business up once, then never touch this tab "
                   "again. Everything downstream - quotes, invoices, "
                   "costs, reports - reads these cells.",
                   fmts["subtitle"])

    b = cfg.business

    # --- rows 4-15: business profile (Business_Name = C6) ---------------
    _section(ws, fmts, 4, "1 · Business Profile")
    _note(ws, fmts, 5,
          "These details print on quotes and invoices.")
    _field(ws, fmts, 6, "Business Name", b.name,
           note="Shown on the printable documents.")
    _field(ws, fmts, 7, "Owner / Manager", b.owner)
    _field(ws, fmts, 8, "Email", b.email)
    _field(ws, fmts, 9, "Phone", b.phone)
    _field(ws, fmts, 10, "Address", b.address)
    _field(ws, fmts, 11, "Service Area", b.area)
    _field(ws, fmts, 12, "Website", b.website)
    _field(ws, fmts, 13, "Tagline", b.tagline)
    _field(ws, fmts, 14, "Registration / License #", b.reg_number)
    _field(ws, fmts, 15, "Insurance Policy", b.insurance)

    # --- rows 16-24: calendar & display ---------------------------------
    _section(ws, fmts, 16, "2 · Calendar & Display")
    _note(ws, fmts, 17,
          "The planner year, the currency and the units you price in.")
    _field(ws, fmts, 18, "Plan Year", cfg.year, "input_int",
           "Reports and the Calendar open on this year.")
    _field(ws, fmts, 19, "Week Starts", cfg.week_start,
           note="Monday suits most; Sunday suits the Middle East and US.")
    _field(ws, fmts, 20, "Currency Symbol", cfg.currency_symbol)
    _field(ws, fmts, 21, "Currency Code", cfg.currency_code)
    _field(ws, fmts, 22, "Area Unit", cfg.area_unit,
           note="sq ft or sq m - the quote calculator prices per unit.")
    _field(ws, fmts, 23, "Distance Unit", cfg.distance_unit)
    _field(ws, fmts, 24, "Time Format", cfg.time_format,
           note="Display preference - Excel uses your system format.")

    # --- rows 25-36: working rules --------------------------------------
    _section(ws, fmts, 25, "3 · Working Rules")
    _note(ws, fmts, 26,
          "How the business runs day to day. Drives the scheduler "
          "reminders and the costings.")
    _field(ws, fmts, 27, "Cleaners per Job", cfg.cleaners_per_job,
           "input_int", "Default crew size when costing a job.")
    _field(ws, fmts, 28, "Billable Hours per Day", cfg.productive_hours,
           "input", "Real productive hours per cleaner, per day.")
    _field(ws, fmts, 29, f"Travel Rate per {cfg.distance_unit}",
           cfg.travel_rate, "input_money",
           "Reimbursed per unit of business travel.")
    _field(ws, fmts, 30, "Travel Minutes Between Jobs",
           cfg.travel_minutes, "input_int")
    _field(ws, fmts, 31, "Job Reminder (days)", cfg.reminder_days,
           "input_int", "How early the Calendar flags a job.")
    _field(ws, fmts, 32, "Quote Follow-up (days)",
           cfg.quote_followup_days, "input_int")
    _field(ws, fmts, 33, "Quote Valid (days)", cfg.quote_valid_days,
           "input_int")
    _field(ws, fmts, 34, "Inactive Client (days)",
           cfg.inactive_client_days, "input_int",
           "Clients with no job this long show on Client Retention.")
    _field(ws, fmts, 35, "Low Stock Warning (days)",
           cfg.low_stock_days, "input_int")
    _field(ws, fmts, 36, "Equipment Service Interval (days)",
           cfg.maintenance_days, "input_int")

    # --- rows 37-42: payroll -------------------------------------------
    _section(ws, fmts, 37, "4 · Payroll")
    _note(ws, fmts, 38,
          "What an hour of cleaning really costs you.")
    _field(ws, fmts, 39, "Default Hourly Pay", cfg.pay_rate,
           "input_money", "Fallback when an employee has no own rate.")
    _field(ws, fmts, 40, "Overtime Multiplier", cfg.overtime_multiplier,
           "input")
    _field(ws, fmts, 41, "Employer On-costs", cfg.employer_oncost,
           "input_pct",
           "Tax, insurance, holiday pay on top of wages.")
    _field(ws, fmts, 42, "Loaded Cost per Hour", cfg.cost_per_hour,
           "calc_money",
           "Pay x (1 + on-costs). This is what jobs are costed at.")

    # --- rows 43-49: billing (Tax_Rate = C45, Invoice_Terms = C46) ------
    _section(ws, fmts, 43, "5 · Billing & Tax")
    _note(ws, fmts, 44,
          "How invoices are calculated and chased.")
    _field(ws, fmts, 45, "Tax Rate", cfg.tax_rate, "input_pct",
           "Sales tax or VAT. Set 0 for none.")
    _field(ws, fmts, 46, "Payment Terms (days)", cfg.payment_terms_days,
           "input_int", "Days from invoice date to due date.")
    _field(ws, fmts, 47, "Late Fee", cfg.late_fee_percent, "input_pct")
    _field(ws, fmts, 48, "Tax Label", cfg.tax_label,
           note="What it says on the invoice.")
    _field(ws, fmts, 49, "Deposit %", cfg.deposit_percent, "input_pct",
           "Collected before work starts on big jobs.")

    # --- rows 50-64: pricing (Hourly_Rate = C55, Minimum_Charge = C57) --
    _section(ws, fmts, 50, "6 · Pricing")
    _note(ws, fmts, 51,
          "The knobs the Quote Calculator turns. Get these right and "
          "every quote is right.")
    _field(ws, fmts, 52, f"Rate per {cfg.area_unit} (standard)",
           cfg.rate_per_area, "input_money")
    _field(ws, fmts, 53, "Rate per Bedroom", cfg.rate_per_bedroom,
           "input_money")
    _field(ws, fmts, 54, "Rate per Bathroom", cfg.rate_per_bathroom,
           "input_money")
    _field(ws, fmts, 55, "Hourly Rate", cfg.hourly_rate, "input_money",
           "What the client pays per hour of cleaning.")
    _field(ws, fmts, 56, "Rate per Room", cfg.rate_per_room,
           "input_money")
    _field(ws, fmts, 57, "Minimum Charge", cfg.minimum_charge,
           "input_money", "No job leaves for less than this.")
    _field(ws, fmts, 58, "Deep Clean Uplift", cfg.deep_clean_uplift,
           "input_pct", "Added to the standard clean price.")
    _field(ws, fmts, 59, "Move Clean Uplift", cfg.move_clean_uplift,
           "input_pct")
    _field(ws, fmts, 60, "Pet Surcharge", cfg.pet_surcharge,
           "input_money")
    _field(ws, fmts, 61, "Callout Fee", cfg.callout_fee,
           "input_money")
    _field(ws, fmts, 62, "Supplies Cost per Hour",
           cfg.supplies_per_hour, "input_money",
           "Chemicals and materials consumed per hour worked.")
    _field(ws, fmts, 63, "Target Margin", cfg.target_margin,
           "input_pct", "The margin a healthy quote should show.")
    _field(ws, fmts, 64, "Margin Floor", cfg.margin_floor, "input_pct",
           "Quotes below this get flagged for review.")

    # --- rows 65-73: targets -------------------------------------------
    _section(ws, fmts, 65, "7 · Targets")
    _note(ws, fmts, 66,
          "What good looks like this year. The Dashboard measures "
          "against these.")
    _field(ws, fmts, 67, "Monthly Revenue Target",
           cfg.revenue_target_month, "input_money")
    _field(ws, fmts, 68, "Annual Revenue Target",
           cfg.revenue_target_year, "input_money")
    _field(ws, fmts, 69, "Monthly Expense Budget",
           cfg.expense_budget_month, "input_money")
    _field(ws, fmts, 70, "Staff Utilisation Target",
           cfg.utilisation_target, "input_pct",
           "Share of paid hours that are billed to jobs.")
    _field(ws, fmts, 71, "Client Retention Target", cfg.retention_target,
           "input_pct")
    _field(ws, fmts, 72, "Satisfaction Target", cfg.satisfaction_target,
           "input", "Out of 5.")
    _field(ws, fmts, 73, "Quote Win Rate Target", cfg.quote_win_target,
           "input_pct")

    ws.merge_range(75, 1, 75, 6,
                   "Input cells are white and unlocked. Pale teal cells "
                   f"calculate themselves. Sheets are protected with the "
                   f"password '{cfg.password}' - use Review > Unprotect "
                   "Sheet to restructure.",
                   fmts["note"])
    ws.set_row(75, 28)
    ws.freeze_panes(3, 0)
    ws.set_zoom(100)
    _protect(ws, cfg)


def _protect(ws: Any, cfg: Config) -> None:
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
            "format_cells": False,
        })
