"""Start Here - the welcome page."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Start Here")
    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 34)
    ws.set_column(2, 6, 17)

    ws.merge_range(0, 1, 0, 6, cfg.product_name, fmts["title"])
    ws.set_row(0, 34)
    ws.merge_range(1, 1, 1, 6, cfg.product_subtitle, fmts["subtitle"])
    ws.merge_range(2, 1, 2, 6,
                   f"Version {cfg.version}  ·  by {cfg.author}  ·  "
                   f"built for {cfg.business.name}",
                   fmts["nav"])

    r = 4

    def section(text: str) -> None:
        nonlocal r
        ws.merge_range(r - 1, 1, r - 1, 6, text, fmts["section"])
        r += 1

    def line(text: str, style: str = "note", height: int = 22) -> None:
        nonlocal r
        ws.merge_range(r - 1, 1, r - 1, 6, text, fmts[style])
        ws.set_row(r - 1, height)
        r += 1

    def gap() -> None:
        nonlocal r
        r += 1

    section("What this workbook is")
    line("A complete back office for a cleaning business: client CRM, "
         "quoting, job scheduling, crews and timesheets, costing, "
         "invoicing, stock, expenses, retention and a profit dashboard. "
         "37 tabs, all wired together.")
    line(f"Everything is Excel-2010 safe: classic formulas only, no "
         f"special functions. Sheets are protected with the password "
         f"'{cfg.password}' so formulas cannot be broken by accident - "
         "input cells are white and unlocked.", "warning", 32)
    gap()

    section("Start in this order")
    line("1 · Settings  -  your business details, rates, tax and targets.")
    line("2 · Services  -  your price list. The quote calculator reads it.")
    line("3 · Clients & Properties  -  who you clean and where.")
    line("4 · Quote Calculator  -  price a job in 3 minutes, print it "
         "from Print Quote.")
    line("5 · Jobs  -  schedule the work; Job Tasks hold the checklists.")
    line("6 · Timesheets, Supplies & Expenses  -  log the real costs.")
    line("7 · Invoices & Payments  -  bill it, get paid, watch balances.")
    line("8 · Dashboard & Reports  -  the numbers that tell you how the "
         "business is really doing.")
    gap()

    section("Colour key")
    line("White cells are yours to fill in. Pale teal cells are "
         "calculated - do not type over them. Amber highlights mean "
         "something needs you today.", "note", 30)
    gap()

    section("The tabs")
    tabs = [
        ("Settings", "Business profile, pricing and targets"),
        ("Dashboard", "Today, this month, this year at a glance"),
        ("Quote Calculator", "Interactive pricing tool"),
        ("Clients / Properties / Leads", "The CRM"),
        ("Services", "The price list"),
        ("Quotes / Quote Lines", "What you quoted"),
        ("Jobs / Job Tasks", "The schedule and the checklists"),
        ("Calendar / Staff Schedule", "Who, where, when"),
        ("Checklists", "What each service includes"),
        ("Employees / Timesheets", "The team and their hours"),
        ("Job Costing", "True cost and profit per job"),
        ("Invoices / Invoice Lines / Payments", "Money in"),
        ("Supplies / Supply Usage / Equipment", "Stock and machines"),
        ("Expenses / Mileage", "Money out"),
        ("Client Retention / Complaints", "Keeping clients"),
        ("Incidents / Safety", "Keeping everyone safe"),
        ("Financial Plan", "Budget vs actuals, monthly plan"),
        ("Reports", "KPIs, rankings, monthly trend"),
        ("Print Quote / Invoice / Job Sheet", "Client-ready documents"),
        ("Lists / Help", "Drop-down sources and how-to"),
    ]
    ws.write(r - 1, 1, "Tab", fmts["label"])
    ws.merge_range(r - 1, 2, r - 1, 6, "What it does", fmts["label"])
    r += 1
    for tab, what in tabs:
        ws.write(r - 1, 1, tab, fmts["input"])
        ws.merge_range(r - 1, 2, r - 1, 6, what, fmts["input"])
        r += 1

    gap()
    section("Printable documents")
    line("Print Quote, Print Invoice and Print Job Sheet are client-ready "
         "one-pagers. Type a Quote #, Invoice # or Job # into the yellow "
         "cell at the top and the document builds itself. Set the print "
         "area to A1:F45 and print.")
    gap()
    line(f"© {cfg.author}  ·  {cfg.listing_title}", "note")

    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
