"""`Getting Started` - the hour that makes the other twenty-two tabs work.

Written in the order somebody actually does it, with the honest bits
included: what this workbook does, what it does not do, and the four
IDs that hold the whole thing together.
"""

from __future__ import annotations

from ..config import (DISCLAIMER, HONESTY_NOTE, PAYROLL_NOTE,
                      PHOTO_NOTE, PRIVACY_NOTE, ROUTE_NOTE,
                      WEATHER_NOTE, Config, Palette)
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Getting Started"
LAST_COL = 9

STEPS = [
    ("1. Settings & Lists - half an hour, once",
     "Your business details, your crew cost per hour, your "
     "charge-out rate, your overhead per hour, your margins and "
     "your warning windows. Everything else in the workbook is "
     "calculated from these. The crew cost rate and the overhead "
     "rate are the two that decide whether your profit figures are "
     "true - set them properly before anything else."),
    ("2. Service Catalog - your price list",
     "Add your services, rates, units and times; the demo has "
     "illustrative examples, not recommendations. Set every rate "
     "to yours, and change the "
     "minutes to what the work actually takes you. The margin "
     "column will tell you straight away which of your prices do "
     "not work."),
    ("3. Customer CRM - who pays you",
     "One row per customer, and the Customer ID appears on its own. "
     "A household with two addresses is one customer with two "
     "properties, not two customers."),
    ("4. Property Database - where the work happens",
     "One row per address, pointing at a customer. Measure the lawn "
     "once and measure it properly - the area drives every price, "
     "every time estimate and every material quantity in the "
     "workbook. Record the access, the slope, the obstacles and the "
     "dog while you are there."),
    ("5. Crew Database - who does the work",
     "Each person, with their loaded cost per hour: wages plus "
     "payroll tax plus insurance, not take-home pay. Put the "
     "take-home figure in and every job will look more profitable "
     "than it really is."),
    ("6. Quote Calculator - price the first job",
     "Pick a customer, a property and a service and watch the price "
     "build itself from the lawn size, the labour, the materials, "
     "the travel and the margin you asked for. Override anything "
     "in the white input cells; the margin column shows what the "
     "override cost you."),
    ("7. Job & Work Orders - book the work",
     "A row per visit. Mark it Completed when it is done, and put "
     "the real hours on it. That one habit is what turns this from "
     "a list into a costing system."),
    ("8. Recurring Contracts - the income you can count on",
     "Set up the standing agreements. The workbook tells you when "
     "the next visit is due and what each agreement is worth over a "
     "year - and it will remind you to renew before the season "
     "starts."),
    ("9. Invoice & Payments - get paid",
     "Raise the invoice, put the Job ID on it, record payments as "
     "they arrive. The overdue column is the one that pays for this "
     "workbook."),
    ("10. Timesheets, Expenses, Equipment - the truth",
     "Hours against job numbers, receipts against job numbers, "
     "engine hours against machines. This is the unglamorous part, "
     "and it is the part that makes the Profit Analysis tab worth "
     "reading."),
]

WHAT_IT_DOES = [
    "Prices a job from lawn size, labour hours, materials, "
    "equipment, travel and the profit margin you want.",
    "Keeps customers and properties as separate, linked records, so "
    "one customer can own six addresses.",
    "Works out when every recurring visit is next due, from the "
    "frequency and the last completed visit.",
    "Costs every job twice - what you estimated and what it "
    "actually took - and shows you the gap.",
    "Tracks crew hours, overtime and the share of the day that was "
    "actually billable.",
    "Warns you when a machine is due a service, by engine hours or "
    "by date, whichever comes first.",
    "Flags overdue invoices, aged into buckets, worst first.",
    "Prints a quote, an invoice and a daily crew work order.",
    "Shows profit by job, by customer, by property, by service and "
    "by month.",
]

WHAT_IT_DOES_NOT = [
    "It does not navigate. The Route Planner organises the stops "
    "you choose onto a printable sheet; it is not GPS and it does "
    "not work out the shortest route.",
    "It does not sync with QuickBooks, Xero, Jobber, Yardbook or "
    "any other software. Nothing in it connects to the internet.",
    "It does not take card payments or send invoices. It records "
    "what you billed and what arrived.",
    "It does not run payroll or calculate tax withholding. It "
    "records hours and costs so your job figures are honest.",
    "It does not book jobs by itself. The contract scheduler tells "
    "you what is due; you decide what actually gets booked, because "
    "weather and breakdowns get a vote.",
    "It does not know about work nobody wrote down. Every figure in "
    "here is built from the rows you enter.",
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_light)

    s.banner("Getting Started",
             "An hour here and the other twenty-two tabs do the rest "
             "of the year for you.",
             LAST_COL)
    s.set_col(0, 0, 4)
    s.set_col(1, 1, 40)
    s.set_col(2, LAST_COL, 14)

    row = 4
    row = s.note(
        row,
        "Work down this list in order. Each step depends on the one "
        "before it - there is no point pricing a job before the "
        "property it happens at exists, and no point costing it "
        "before the crew rate is right. The whole thing takes an "
        "hour or two, once.",
        LAST_COL, height=38)
    row += 1

    # ---------------------------------------------------- the four IDs --
    row = s.section(row, "The four IDs that hold this together",
                    LAST_COL)
    row = s.note(
        row,
        "This is a connected workbook, not twenty-three separate "
        "lists, and four automatic IDs are what connect it. Every "
        "one of them is generated for you, and every cell that "
        "refers to one is a drop-down rather than free text. Pick "
        "from the list - a typed ID is a row that quietly stops "
        "being part of your business.",
        LAST_COL, height=44)
    row += 1
    for label, body in [
        ("Customer ID",
         "Created on the Customer CRM tab. Owns properties, "
         "contracts and invoices. Carries lifetime revenue and "
         "everything they owe you."),
        ("Property ID",
         "Created on the Property Database tab, and points at a "
         "Customer ID. Carries the lawn size, the access, the gate "
         "code and the distance - which is why a quote for an "
         "address you have visited before takes four seconds."),
        ("Job ID",
         "Created on the Job & Work Orders tab, and points at a "
         "property. Timesheets and expenses point at it, which is "
         "how the workbook knows what each visit really cost."),
        ("Invoice ID",
         "Created on the Invoice & Payments tab. Points at a "
         "customer and usually at a job. Carries what is owed and "
         "how late it is."),
    ]:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, body, fmts.chrome("label"))
        s.row_height(row, 30)
        row += 1
    row += 1

    # ------------------------------------------------------ the steps --
    row = s.section(row, "Set it up, in this order", LAST_COL)
    for title, body in STEPS:
        s.merge(row, 1, LAST_COL, title, fmts.chrome("subsection"))
        row += 1
        s.merge(row, 1, LAST_COL, body, fmts.chrome("label"))
        s.row_height(row, 42)
        row += 1
    row += 1

    # ------------------------------------------------- the daily habit --
    row = s.section(row, "Then, the daily habit", LAST_COL)
    row = s.bullets(row, [
        "Morning: open the Route Planner, pick the date and the "
        "crew, print one sheet per truck.",
        "Evening: mark the jobs Completed, put the real hours on "
        "them, and type in the day's receipts.",
        "Friday: raise the invoices for the week's completed work. "
        "The dashboard's 'Completed, unbilled' tile is your list.",
        "Monthly: pick the month on the Profit Analysis tab and "
        "read one row. Fifteen minutes, and you will know more "
        "about your business than most people in this trade know "
        "about theirs.",
    ], LAST_COL, height=24)
    row += 1

    # ------------------------------------------------------ honesty --
    row = s.section(row, "What this workbook does", LAST_COL)
    row = s.bullets(row, WHAT_IT_DOES, LAST_COL, height=24)
    row += 1
    row = s.section(row, "What it does not do", LAST_COL)
    row = s.note(
        row,
        "Said plainly, so you can decide before you rely on it.",
        LAST_COL, height=20)
    row += 1
    row = s.bullets(row, WHAT_IT_DOES_NOT, LAST_COL, height=30)
    row += 1

    # -------------------------------------------------- practical bits --
    row = s.section(row, "Practical things worth knowing", LAST_COL)
    row = s.bullets(row, [
        "Every sheet is protected with the password "
        f"'{cfg.password}' so that formulas cannot be typed over by "
        "accident. White cells are yours; shaded ones calculate "
        "themselves.",
        "Add rows by typing in the next empty row - the formulas are "
        "already there, waiting. Do not insert rows in the middle of "
        "a register.",
        "Filter a register rather than re-sorting it. The automatic "
        "IDs come from the row number, so re-sorting changes them.",
        "Nothing here needs macros, add-ins or a subscription. It "
        "is designed for desktop Excel 2010 and later.",
        "Keep a backup. It is one file, and one file is one thing to "
        "lose.",
    ], LAST_COL, height=28)
    row += 1

    for note, height in [(ROUTE_NOTE, 56), (HONESTY_NOTE, 62),
                         (PAYROLL_NOTE, 52), (WEATHER_NOTE, 44),
                         (PHOTO_NOTE, 44), (PRIVACY_NOTE, 52),
                         (DISCLAIMER, 72)]:
        row = s.note(row, note, LAST_COL, height=height)
        row += 1

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
