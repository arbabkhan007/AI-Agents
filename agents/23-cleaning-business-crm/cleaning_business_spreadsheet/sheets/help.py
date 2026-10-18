"""Help - how the workbook works."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry

SECTIONS = [
    ("1 · Getting started", [
        "Fill in Settings first - business name, rates, tax and targets. "
        "Everything prints from there.",
        "Add your price list on Services. The Quote Calculator reads it.",
        "Add clients on Clients and their addresses on Properties.",
        "Unprotect a sheet with Review > Unprotect Sheet and the "
        "password if you really need to restructure. Re-protect "
        "afterwards.",
    ]),
    ("2 · Quoting a job in 3 minutes", [
        "Open Quote Calculator and type the property's size, bedrooms "
        "and bathrooms into the white cells.",
        "Pick a service and a frequency - the price updates live.",
        "Check the margin. Below the margin floor (Settings) the quote "
        "is flagged amber: raise the price, cut the hours, or walk away.",
        "Record the quote on the Quotes tab (one row) and the detail on "
        "Quote Lines (one row per line, same Quote #).",
        "Print it from Print Quote by typing the Quote # into the yellow "
        "cell.",
    ]),
    ("3 · Scheduling and running jobs", [
        "Won work goes on Jobs: job number, date, time, hours, crew, "
        "price. The status moves Enquiry > Booked > Completed > Invoiced.",
        "Job Tasks hold the checklist for each job - tick items as they "
        "are done; the Jobs tab shows x/y progress.",
        "Calendar shows what is happening each day; Staff Schedule shows "
        "who is where.",
        "Log hours on Timesheets, supplies on Supply Usage, travel on "
        "Mileage. Job Costing rolls it all up per job.",
    ]),
    ("4 · Getting paid", [
        "Raise the invoice on Invoices (one row) with its lines on "
        "Invoice Lines (same Invoice #).",
        "Payments land against the Invoice #; paid and balance columns "
        "update themselves.",
        "Anything with a balance and a past due date shows as Overdue on "
        "the dashboard and in the alerts.",
        "Print the invoice from Print Invoice - it includes the balance "
        "and the payment details.",
    ]),
    ("5 · Reading the numbers", [
        "Dashboard: today's jobs, this month's money, the alerts that "
        "need you.",
        "Reports: KPI panel, monthly trend, revenue by service, top "
        "clients, expenses by category, staff leaderboard.",
        "Financial Plan: budget vs actuals by month with variance "
        "flags.",
        "Client Retention: who is drifting, who is due a thank-you, "
        "which quotes to chase.",
    ]),
    ("6 · Pricing rules the calculator uses", [
        "Base price = size x rate per unit + bedrooms x rate per bedroom "
        "+ bathrooms x rate per bathroom.",
        "Multiply by the service type (standard, deep, move) and the "
        "frequency factor (regular work is cheaper per visit).",
        "Add pets, callout and materials. Never go below the minimum "
        "charge.",
        "Hours estimated from the size and rooms x condition factor; "
        "labour cost = hours x cleaners x your loaded hourly cost.",
        "Margin = (price - cost) / price. Target is on Settings.",
    ]),
    ("7 · Common questions", [
        "Can I add columns? Yes - unprotect the sheet, insert the "
        "column, and copy an adjacent formula down if you need one.",
        "Can I rename a tab? No - the cross-sheet formulas quote the "
        "tab names. Rename at your own risk.",
        "Why are some cells locked? They are formulas. Type only in the "
        "white cells.",
        "How do I change the password? Review > Unprotect/Protect Sheet "
        "with the current password, then set a new one on each sheet.",
        "Excel says it needs to recalculate. Let it - the workbook asks "
        "for a full recalc when it opens.",
    ]),
    ("8 · Care of the workbook", [
        "Save a copy before big restructures.",
        "Keep one row per record; delete rows only when you mean to "
        "delete history.",
        "Archive old years by copying the file and deleting old rows.",
        "Back up weekly - this file IS your business.",
    ]),
]


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Help")
    ws.set_tab_color(Palette.line)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 34)
    ws.set_column(2, 5, 18)

    ws.merge_range(0, 1, 0, 5, "Help  ·  How This Workbook Works",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 5,
                   f"{cfg.product_name} by {cfg.author}. Everything you "
                   "need to run the system day to day.",
                   fmts["subtitle"])

    r = 4
    for title, lines in SECTIONS:
        ws.merge_range(r - 1, 1, r - 1, 5, title, fmts["section"])
        r += 1
        for text in lines:
            ws.merge_range(r - 1, 1, r - 1, 5, "•  " + text, fmts["note"])
            ws.set_row(r - 1, 28)
            r += 1
        r += 1

    ws.merge_range(r - 1, 1, r - 1, 5,
                   f"Made by {cfg.author}. Questions? Start with the "
                   "Start Here tab.", fmts["nav"])
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
