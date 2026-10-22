"""1 Start Here - welcome, setup checklist, legend, FAQ, disclaimer."""

from __future__ import annotations

from ..config import Config, DISCLAIMER
from xlsxwriter.utility import xl_col_to_name

from ..writer import SheetWriter
from . import common as C

NAME = "1 Start Here"


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=cfg and "#6D2E4F", landscape=False)
    last = 9
    sheet.banner("1  Start Here",
                 "Your salon, one organised workbook - read this page "
                 "once, then never again.", last)
    row = 4
    row = sheet.section(row, "WELCOME", last)
    for line in [
        f"{cfg.salon_name} runs on twenty tabs: bookings, clients, the "
        "service menu, sales, payments, staff, commissions, payroll, "
        "expenses, stock, marketing, loyalty, goals, analytics and "
        "reports.",
        "White cells are yours. Pale grey cells are locked formulas - "
        "they do the maths so you do not have to.",
        "Everything recalculates the moment you type: the dashboard, the "
        "commission statements, the P&L and the reports all read the "
        "registers live.",
    ]:
        row = sheet.note(row, line, last) + 1
    row += 1

    row = sheet.section(row, "SETUP CHECKLIST - TEN MINUTES, ONCE", last)
    steps = [
        ("1", "Tab 20 Settings & Lists", "salon name, tax rate, payment "
         "fees, commission rates per category, loyalty rules, and every "
         "drop-down list"),
        ("2", "Tab 8 Staff Management", "one row per person: role, hourly "
         "rate, commission method and rates"),
        ("3", "Tab 5 Services & Pricing", "your menu with durations, "
         "prices, product and labour costs"),
        ("4", "Tab 13 Product Inventory", "retail and backbar stock with "
         "opening quantities and minimum levels"),
        ("5", "Tab 4 Client CRM", "your existing clients - contacts, "
         "consents and preferences"),
        ("6", "Tab 17 Goals & Budget", "a revenue target and an expense "
         "budget per month, plus category budgets"),
        ("7", "Tabs 3, 6, 7, 10, 11", "log bookings, sales, payments, "
         "payroll and expenses as they happen"),
        ("8", "Tab 2 every morning", "the dashboard tells you revenue, "
         "who is overdue a booking, what is owing and what to reorder"),
    ]
    for num, where, what in steps:
        sheet.merge(row, 0, 0, num, sheet.f.chrome("day_number"))
        sheet.merge(row, 1, 3, where, sheet.f.calc("text", bold=True))
        sheet.merge(row, 4, last, what, sheet.f.chrome("note_box"))
        sheet.row_height(row, 30)
        row += 1
    row += 1

    row = sheet.section(row, "COLOUR LEGEND", last)
    legend = [
        ("input", "White / porcelain - unlocked, type here"),
        ("calc", "Pale grey - locked formula, do not type here"),
        ("good", "Green - healthy: completed, active, on target"),
        ("warn", "Amber - watch: cancelled, lapsed, over budget"),
        ("bad", "Red - act: no-show, refund, reorder, balance owing"),
    ]
    for style, text in legend:
        sheet.merge(row, 0, 1, text.split(" - ")[0],
                    sheet.f.chrome("legend_input") if style == "input"
                    else sheet.f.chrome("legend_calc") if style == "calc"
                    else sheet.f.chrome(style))
        sheet.merge(row, 2, last, text, sheet.f.chrome("note_box"))
        row += 1
    row += 1

    row = sheet.section(row, "SAMPLE DATA", last)
    row = sheet.note(row,
                     "This file ships with a realistic example salon so "
                     "you can see every formula working. Your download "
                     "also includes a BLANK workbook with empty registers "
                     "- open that one to start clean. To clear this file "
                     "instead, select each register's rows and delete "
                     "them; formulas stay for the next entry.", last) + 1
    row += 1

    row = sheet.section(row, "FAQ", last)
    faq = [
        ("Will it work in my Excel?",
         "Excel 2010 and every version since, Windows and Mac, plus "
         "Google Sheets, LibreOffice and Numbers. No 365 subscription: "
         "nothing uses XLOOKUP, IFS, LET or dynamic arrays."),
        ("Can I break a formula?",
         "Practically no. Formula cells are locked behind the password "
         "'premium'; only input cells accept typing."),
        ("Does it send reminders or sync with booking apps?",
         "No. A spreadsheet organises bookings; confirmations, texts and "
         "platform sync need separate tools. The rebook-reminder column "
         "tells you who to call."),
        ("Is the tax right for my country?",
         "The rate is yours to set on Settings, including 0. Tax here is "
         "a configured percentage, not advice."),
        ("How do commissions work?",
         "Per staff member you choose Percentage (their own rates), "
         "Category (the category rate table on Settings) or Flat (a fixed "
         "amount per completed service). Retail keeps its own rate."),
        ("Where are my deposits?",
         "Tab 7. A deposit is not revenue until the visit completes and "
         "the sale is invoiced on tab 6 - unearned deposits are reported "
         "separately."),
        ("Can I add rows?",
         "Yes - insert above the last register row and copy the pale "
         "cells down, or simply use the next empty row; every formula "
         "already covers the full register."),
        ("Is my data private?",
         "The file lives on your machine or your own cloud folder. No "
         "macros, no links out, no telemetry. Keep backups like any "
         "business record."),
    ]
    for q, a in faq:
        sheet.merge(row, 0, last, "Q.  " + q, sheet.f.chrome("subsection"))
        row += 1
        sheet.merge(row, 0, last, "A.  " + a, sheet.f.chrome("note_box"))
        sheet.row_height(row, 28)
        row += 1
    row += 1

    row = sheet.section(row, "DISCLAIMER", last)
    sheet.merge(row, 0, last, DISCLAIMER, sheet.f.chrome("note_box"))
    sheet.row_height(row, 60)
    row += 2
    C.footer(sheet, cfg, last, row)
    sheet.finish(print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
