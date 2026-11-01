"""`Getting Started` - what to do first, and what this file is not.

Twenty-three tabs is a lot to open cold.  This page says which five
matter on day one, walks the five things the workbook is actually for,
explains the one idea the whole file turns on - the Booking ID - and
is honest about what a spreadsheet cannot do.
"""

from __future__ import annotations

from ..config import (CONTRACT_NOTE, DISCLAIMER, HONESTY_NOTE,
                      LISTING_TITLE, PRIVACY_NOTE, PRODUCT_NAME,
                      VERSION, Config, Palette)
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Getting Started"
LAST_COL = 10


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)

    s.banner(PRODUCT_NAME,
             "From the first enquiry to the final gallery - read this "
             "page once and the other twenty-two make sense.",
             LAST_COL)
    s.set_col(0, 0, 3)
    s.set_col(1, 1, 30)
    s.set_col(2, LAST_COL, 15)

    row = 4
    row = s.note(
        row,
        "Everything with a white background is yours to type in. "
        "Everything else is a formula, locked so you cannot "
        "accidentally overwrite it. If you want to change a locked "
        "cell, unprotect the sheet - the password is printed at the "
        "bottom of this page.",
        LAST_COL, height=34)
    row += 1

    # ---- the one idea ------------------------------------------------------
    row = s.section(row, "The one thing to understand", LAST_COL)
    row = s.note(
        row,
        "Every wedding gets a Booking ID - WED-0001, WED-0002 and so "
        "on - created for you on the Wedding Bookings tab. That ID is "
        "how the workbook knows that this contract, those three "
        "invoices, that timeline, that shot list, that editing job, "
        "that gallery and those two trips in the car all belong to "
        "the same wedding. Put the Booking ID on a row and it joins "
        "up. Leave it off and the row is an orphan: it still works, "
        "but nothing adds it up.",
        LAST_COL, height=58)
    row += 1
    row = s.bullets(row, [
        "Create the wedding first, on Wedding Bookings. Everything "
        "else refers back to it.",
        "Never type a couple's name where a Booking ID is asked for. "
        "Names are not unique, get spelled two ways, and change.",
        "The Booking ID drop-down on every other tab is live - a "
        "wedding you add this morning is in it this afternoon.",
        "The same idea runs for couples (Client CRM), packages "
        "(Packages & Pricing) and people (Photographer & Staff).",
    ], LAST_COL)
    row += 1

    # ---- the first hour ----------------------------------------------------
    row = s.section(row, "Your first hour", LAST_COL)
    steps = [
        ("1. Settings & Lists",
         "Put your studio name in, then your deposit rule, your "
         "payment dates, your mileage rate and your turnaround "
         "promise. Ten minutes here and every other tab is right."),
        ("2. Packages & Pricing",
         "Type the packages you actually sell, what each includes, "
         "and honestly what each costs you to deliver. The sheet "
         "works out your margin, your real hourly rate and what you "
         "would have to charge to hit your target."),
        ("3. Photographer & Staff",
         "Add yourself first, with 'Owner' set to Yes. Then anybody "
         "who seconds or edits for you, with their rate."),
        ("4. Client CRM",
         "Add the couples you already have booked. Just the names, "
         "the date and how they found you."),
        ("5. Wedding Bookings",
         "One row per wedding. Pick the couple, the date, the times "
         "and the package - the price, the deposit, the balance date "
         "and the delivery date all follow."),
        ("6. Payments & Invoices",
         "Add the instalments you have already taken so the money "
         "columns are true from the start."),
    ]
    for label, text in steps:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, text, fmts.chrome("note"))
        s.row_height(row, 32)
        row += 1
    row += 1

    # ---- the five jobs -----------------------------------------------------
    row = s.section(row, "The five things this is for", LAST_COL)
    jobs = [
        ("An enquiry becomes a booking",
         "Lead Tracker -> Wedding Bookings",
         "Log the enquiry the day it lands. The tab tells you when "
         "to reply, when to chase and when to let it go. When they "
         "say yes, put the Client ID on the lead and create the "
         "wedding - the lead's value and your conversion rate follow "
         "automatically."),
        ("A package becomes money in the bank",
         "Packages & Pricing -> Wedding Bookings -> Payments",
         "The package sets the price. The booking adds overtime, "
         "add-ons and travel, works out the deposit and the balance "
         "date from your rules, and the payments tab chases anything "
         "late. The booking always shows what is still owed."),
        ("Planning the wedding day",
         "Wedding Timeline + Shot List Manager",
         "Build the running order from the ceremony time - the "
         "standard events fill themselves in. Write the family "
         "groups out by name. Print the Client Questionnaire and "
         "take it with you."),
        ("Editing becomes a delivered gallery",
         "Editing Workflow -> Gallery & Delivery",
         "Ten steps from backing up the cards to uploading the "
         "gallery. The promised date comes from your turnaround "
         "setting. After delivery the gallery tab walks you through "
         "the fortnight that follows - open it, ask for the review, "
         "chase the album, warn them before it closes."),
        ("Knowing what a wedding actually made",
         "Profit Analysis",
         "Type a Booking ID and see the whole wedding: what came in, "
         "what went out, how many hours it really took and what that "
         "works out at an hour. It is usually less than you think, "
         "and it is the number that should decide your prices."),
    ]
    for title, tabs, text in jobs:
        s.write(row, 1, title, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, tabs, fmts.chrome("subsection"))
        row += 1
        s.merge(row, 1, LAST_COL, text, fmts.chrome("note"))
        s.row_height(row, 42)
        row += 1
    row += 1

    # ---- how to read a row --------------------------------------------------
    row = s.section(row, "How to read any register", LAST_COL)
    row = s.bullets(row, [
        "Row 4 is the heading, row 5 is the first record. Everything "
        "below it is yours.",
        "White cells are inputs. Shaded cells are worked out and "
        "locked.",
        "The last column on every register is called 'What to do'. It "
        "writes one plain line per row - 'Chase - contract not signed "
        "back', 'Overdue - gallery past the promised date', 'OK'. "
        "Filter by it; do not sort or move populated rows.",
        "The Dashboard counts those lines, so the number next to a "
        "tab's name is the number of rows on that tab wanting "
        "something from you.",
        "Hidden columns hold the plumbing - month keys, sort keys, "
        "yes/no flags the formulas need. Leave them be; they are "
        "hidden because they are dull, not because they are secret.",
        "Formulas cover fixed prepared ranges. Do not insert, delete, "
        "sort or move populated rows: generated IDs depend on position.",
    ], LAST_COL)
    row += 1

    # ---- what it is not ------------------------------------------------------
    row = s.section(row, "What this is not", LAST_COL)
    row = s.note(row, HONESTY_NOTE, LAST_COL, height=58)
    row += 1
    row = s.bullets(row, [
        "It is not connected to anything. No enquiry form, no "
        "calendar sync, no gallery host, no payment processor, no "
        "email. Every figure here is one you typed.",
        "It does not write or sign contracts. Contracts & Documents "
        "records which paperwork exists, when it went out and where "
        "the signed copy is kept - nothing more.",
        "It is not accounting software and it is not tax advice. "
        "Give your accountant the Expense Tracker and the Payments "
        "tab.",
        "It does not store passwords, card numbers or anything else "
        "you would not want in a file you email to your bookkeeper.",
        "It will not make you book more weddings. It will stop you "
        "losing the ones you have already booked, which is nearly as "
        "useful.",
    ], LAST_COL)
    row += 1
    row = s.note(row, CONTRACT_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, PRIVACY_NOTE, LAST_COL, height=48)
    row += 1

    # ---- the tabs ------------------------------------------------------------
    row = s.section(row, "Every tab, and what it is for", LAST_COL)
    head = row
    s.table_head(head, 1, ["Tab", "What it is for", "Fill in first?"],
                 widths=[26, 62, 14])
    row = head + 1
    tabs = [
        ("Dashboard", "Everything at a glance. Read-only.", "No"),
        ("Getting Started", "This page.", "No"),
        ("Settings & Lists",
         "Your studio, your prices, your rules, your drop-downs.",
         "Yes - first"),
        ("Client CRM", "One row per couple.", "Yes"),
        ("Lead Tracker",
         "Every enquiry, and whether you replied in time.", "Yes"),
        ("Booking Calendar",
         "Twelve months of dates with the booked ones coloured.",
         "No"),
        ("Wedding Bookings",
         "One row per wedding. The spine of the whole file.",
         "Yes - second"),
        ("Packages & Pricing",
         "What you sell, what it costs you, what it should cost.",
         "Yes"),
        ("Contracts & Documents",
         "Which paperwork exists and where it is kept.", "As you go"),
        ("Payments & Invoices",
         "Every instalment, due and received.", "Yes"),
        ("Wedding Timeline",
         "The running order of each wedding day.", "Per wedding"),
        ("Shot List Manager",
         "Every photograph promised, grouped and ticked off.",
         "Per wedding"),
        ("Photographer & Staff",
         "Who shoots, who edits, what they cost.", "Yes"),
        ("Editing Workflow",
         "Ten steps from memory card to finished gallery.",
         "Per wedding"),
        ("Gallery & Delivery",
         "Handing it over, and the month afterwards.",
         "Per wedding"),
        ("Equipment Inventory",
         "What you own, what it is worth, what needs looking at.",
         "When you can"),
        ("Travel & Mileage",
         "Every journey, what it cost and what to charge on.",
         "As you go"),
        ("Marketing Calendar",
         "What you posted and whether anybody booked.",
         "When you can"),
        ("Expense Tracker", "Everything the business pays out.",
         "As you go"),
        ("Profit Analysis",
         "What each wedding actually made. Read-only.", "No"),
        ("Client Questionnaire",
         "The printable form, filled in from the booking.", "No"),
        ("Reviews & Referrals",
         "Who you asked, what they wrote, what it led to.",
         "After delivery"),
        ("Monthly & Annual Reports",
         "The month and the year in numbers. Read-only.", "No"),
    ]
    for name, purpose, first in tabs:
        s.write(row, 1, name, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL - 1, purpose, fmts.chrome("note"))
        s.write(row, LAST_COL, first, fmts.chrome("note"))
        row += 1
    row += 1

    # ---- the small print -------------------------------------------------
    row = s.section(row, "The small print", LAST_COL)
    row = s.field(row, "Product", PRODUCT_NAME, mode="calc",
                  value_end=LAST_COL)
    row = s.field(row, "Listing title", LISTING_TITLE, mode="calc",
                  value_end=LAST_COL)
    row = s.field(row, "Version", VERSION, mode="calc")
    row = s.field(row, "Created by", cfg.author, mode="calc")
    row = s.field(row, "Sheet password", cfg.password, mode="calc",
                  help_text="Every sheet is protected so formulas "
                            "cannot be overwritten by accident. Use "
                            "this to unprotect one if you want to "
                            "change it.")
    row = s.field(row, "Example data",
                  "Included" if cfg.include_sample_data
                  else "Not included - this is the blank copy",
                  mode="calc", value_end=LAST_COL)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=96)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
