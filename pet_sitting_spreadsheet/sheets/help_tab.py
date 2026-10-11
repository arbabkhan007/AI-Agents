"""`Help` - instructions, formula notes, troubleshooting and version log."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry, col_letter
from ..writer import SheetWriter

NAME = "Help"
LAST_COL = 9

HOW_IT_WORKS = [
    "Cream cells are for you. Grey cells are locked formulas - they fill "
    "themselves in as soon as the row has enough information.",
    "Every sheet is protected so a stray keystroke cannot wipe out a "
    "formula. The password is below if you ever need to change one.",
    "Records join up by name, not by hidden ID: pick the client, pet, "
    "service or staff member from the drop down and the rest follows.",
    "The drop downs all live on the Lists tab. Edit a list there and every "
    "sheet picks up the change.",
    "Numbers on the Dashboard, Reports and Budget tabs come from a hidden "
    "sheet called Calc. You never need to open it - it does the heavy "
    "lifting so the visible formulas stay short.",
]

DAILY = [
    "Morning: open the Reminders tab and work through anything with a "
    "count above zero.",
    "Before each job: check the pet's care sheet (Print Pet Care) if "
    "someone else is covering.",
    "After each visit: add a row to the Visit Log and send the client "
    "their update.",
    "Weekly: raise invoices, record payments, log expenses and trips.",
    "Monthly: set the Dashboard period, check the Budget tab and print "
    "the Reports pack.",
    "Yearly: print the full-year report, save a dated copy of the file, "
    "then clear last year's rows from a fresh copy.",
]

TASKS = [
    ("Add a client",
     "Clients tab > first empty row > type the name. The ID, counters and "
     "revenue columns fill themselves in."),
    ("Add a pet",
     "Pets tab > type the pet name, then choose the owner from the drop "
     "down. The pet reference column builds the 'Pet (Owner)' label that "
     "the other sheets use."),
    ("Take a booking",
     "Bookings tab > date, client, pet, service. The price comes from the "
     "Services tab and adds extra pet, weekend, holiday, travel and "
     "last-minute fees automatically."),
    ("Price something differently",
     "Type your figure in the 'Price override' column - it beats the "
     "calculated subtotal. Add a reason so you remember why."),
    ("Log a visit",
     "Visit Log tab > choose the booking ID; the client, pet and service "
     "copy across. Fill in arrival and departure times and the care you "
     "gave."),
    ("Invoice a booking",
     "Invoices tab > invoice date, client, booking ref. The total, due "
     "date, tax and ageing all calculate. Print it from the Print Invoice "
     "tab."),
    ("Invoice several visits at once",
     "Leave the booking ref blank, write your own description and use "
     "Qty x Rate."),
    ("Record a payment",
     "Payments tab > date, client, invoice number, amount. The invoice "
     "balance and status update instantly."),
    ("Take a deposit",
     "Record it on the Payments tab with Deposit = Yes. It counts towards "
     "the invoice and shows in the deposit column."),
    ("Claim mileage",
     "Mileage tab > start and end odometer readings. The claim uses the "
     "mileage rate on the Settings tab."),
    ("Pay your team",
     "Staff tab > set the pay type and rate. Hours and visits come from "
     "the Visit Log, and the wages column shows what is owed."),
    ("Check profit",
     "Dashboard for the headline numbers, Reports for a full profit and "
     "loss over any date range."),
    ("Print a care sheet",
     "Print Pet Care tab > pick the pet reference at the top > print."),
    ("Add more rows",
     "Select the last row of the grid, right click > Insert copied cells, "
     "or copy the last row down. The formulas copy with it."),
]

FORMULA_NOTES = [
    ("Record IDs", "CL-0001, PET-0001, BK-0001 ...",
     "Built from the row number, so they stay unique. Filter the list "
     "instead of re-sorting it and the IDs keep lining up with your other "
     "tabs."),
    ("Booking price", "rate x quantity (or hours) + extras - discount",
     "Looks the service up on the Services tab, then applies the extra "
     "pet fee, weekend and holiday surcharges, travel fee and last-minute "
     "fee from the Settings tab."),
    ("Travel fee", "MAX(0, distance - free distance) x travel rate",
     "Only charges for the distance beyond the free radius."),
    ("Tax", "subtotal x tax rate (or extracted when prices include tax)",
     "Controlled by 'Tax registered' and 'Prices include tax' on the "
     "Settings tab."),
    ("Invoice balance", "total - payments applied",
     "Payments apply as amount minus refund. Tips and late fees are "
     "counted as income but not against the invoice."),
    ("Ageing bucket", "today - due date",
     "Paid, Not due, Current, 1-30, 31-60, 61-90 and 90+ days."),
    ("Double booking check",
     "SUMPRODUCT over same carer, same date, overlapping times",
     "Shows 'Conflict' when two jobs overlap for one person."),
    ("Client revenue", "SUMIFS of payments received for that client",
     "Lifetime revenue, invoiced and outstanding all follow the client "
     "name, so keep names consistent."),
    ("Dashboard period",
     "PeriodStart / PeriodEnd from the year and month pickers",
     "Choose 'All year' for a full year view. Every tile and the service, "
     "expense and client tables follow the picker."),
    ("Mileage claim", "business distance x mileage rate",
     "Personal trips are excluded from the claim and the dashboard."),
    ("Break-even", "fixed costs / gross margin",
     "Gross margin comes from your service rates and staff cost per "
     "service on the Services tab."),
]

TROUBLESHOOTING = [
    ("A cell shows #N/A or a blank where I expected a number",
     "The name in that row does not match a record. Re-pick the client, "
     "pet or service from the drop down rather than typing it."),
    ("I cannot type in a cell",
     "It is a formula cell. Review > Unprotect Sheet, enter the password, "
     "make the change, then protect the sheet again."),
    ("My new rows have no formulas",
     "You typed below the prepared grid. Copy the last prepared row down "
     "as far as you need."),
    ("The totals look wrong",
     "Check the Dashboard year and month pickers, and the From / To dates "
     "on the Reports tab - every figure obeys them."),
    ("Dates look like numbers",
     "Format the cells as a date (Home > Number format > Short date). "
     "This can happen after importing or exporting."),
    ("Nothing recalculates",
     "Press F9, or set Formulas > Calculation Options > Automatic."),
    ("A drop down is missing an option",
     "Add it to the matching column on the Lists tab - the drop downs "
     "grow automatically."),
    ("I want a different currency",
     "Change the currency symbol on the Settings tab, then select the "
     "money columns and apply your own number format if you want the "
     "symbol to change on screen too."),
    ("The file opens in Google Sheets with warnings",
     "Upload to Google Drive and open with Google Sheets. Sheet "
     "protection becomes a warning rather than a password, and "
     "sparklines are redrawn by Sheets - all formulas work."),
]

PRIVACY = [
    "This workbook holds personal information about your clients: names, "
    "addresses, phone numbers and door codes. Treat it like a key safe.",
    "Keep the file on an encrypted drive or in a password protected cloud "
    "folder, and use a file open password (File > Info > Protect "
    "Workbook) if the device is shared.",
    "Only record what you need, and delete alarm codes and key details "
    "once a client leaves.",
    "Back up weekly - keep one copy off the machine you work on.",
    "If a client asks for their data or asks to be deleted, you can "
    "filter the register by their name and export or remove those rows.",
]

VERSIONS = [
    ("1.0", "First release: 27 tabs, 13 registers, dashboard, reports, "
            "budget, reminders and printable forms."),
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.grey_text,
                    landscape=False)

    s.banner("Help & Instructions",
             "Everything you need to run the workbook - and what to do "
             "when something looks wrong.", LAST_COL)

    s.set_col(0, 0, 3)
    s.set_col(1, 1, 30)
    s.set_col(2, 8, 12)
    s.set_col(9, 9, 14)

    row = 4
    row = s.section(row, "How this workbook thinks", LAST_COL)
    row = s.bullets(row, HOW_IT_WORKS, LAST_COL, first_col=1, height=16)
    row += 1

    row = s.section(row, "A simple routine", LAST_COL)
    row = s.bullets(row, DAILY, LAST_COL, first_col=1, height=16)
    row += 1

    row = s.section(row, "How do I ...", LAST_COL)
    s.write(row, 1, "Task", fmts.chrome("header_left"))
    s.merge(row, 2, LAST_COL, "What to do", fmts.chrome("header"))
    row += 1
    for task, answer in TASKS:
        s.write(row, 1, task, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, answer, fmts.chrome("note"))
        s.row_height(row, 26)
        row += 1
    row += 1

    row = s.section(row, "What the formulas do", LAST_COL)
    s.write(row, 1, "Calculation", fmts.chrome("header_left"))
    s.merge(row, 2, 4, "In plain English", fmts.chrome("header"))
    s.merge(row, 5, LAST_COL, "Notes", fmts.chrome("header"))
    row += 1
    for label, plain, note in FORMULA_NOTES:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, 4, plain, fmts.chrome("label"))
        s.merge(row, 5, LAST_COL, note, fmts.chrome("note"))
        s.row_height(row, 26)
        row += 1
    row += 1

    row = s.section(row, "Troubleshooting", LAST_COL)
    s.write(row, 1, "Problem", fmts.chrome("header_left"))
    s.merge(row, 2, LAST_COL, "Fix", fmts.chrome("header"))
    row += 1
    for problem, fix in TROUBLESHOOTING:
        s.write(row, 1, problem, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, fix, fmts.chrome("note"))
        s.row_height(row, 26)
        row += 1
    row += 1

    row = s.section(row, "Protection & passwords", LAST_COL)
    facts = [
        ("Sheet password", cfg.password),
        ("To edit a formula",
         "Review > Unprotect Sheet > enter the password > make your change "
         "> Review > Protect Sheet (tick the same boxes) to lock it again."),
        ("What is locked",
         "Only the grey formula cells, plus the headings and layout. "
         "Every cream cell stays editable while the sheet is protected."),
        ("Rows and columns",
         "You can insert and delete rows and sort with the filter "
         "buttons. Inserting columns is blocked because the formulas "
         "point at specific columns."),
    ]
    for label, text in facts:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, text, fmts.chrome("note"))
        s.row_height(row, 24)
        row += 1
    row += 1

    row = s.section(row, "Looking after client data", LAST_COL)
    row = s.bullets(row, PRIVACY, LAST_COL, first_col=1, height=16)
    row += 1

    row = s.section(row, "Compatibility", LAST_COL)
    compat = [
        ("Microsoft Excel", "2010, 2013, 2016, 2019, 2021 and Microsoft "
                            "365 - Windows and Mac. Everything works."),
        ("Google Sheets", "Upload and open with Google Sheets. Formulas, "
                          "drop downs and conditional formatting carry "
                          "over; sheet protection becomes a Google Sheets "
                          "warning."),
        ("Apple Numbers / LibreOffice",
         "Formulas and layout open fine. Some conditional formats and "
         "sparklines may look different."),
        ("Mobile", "Read and light editing work well in the Excel and "
                   "Google Sheets apps. Do the data entry on a computer "
                   "where you can see the whole grid."),
    ]
    for label, text in compat:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, text, fmts.chrome("note"))
        s.row_height(row, 24)
        row += 1
    row += 1

    row = s.section(row, "Version history", LAST_COL)
    s.write(row, 1, "Version", fmts.chrome("header_left"))
    s.merge(row, 2, LAST_COL, "What changed", fmts.chrome("header"))
    row += 1
    for version, text in VERSIONS:
        s.write(row, 1, version, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, text, fmts.chrome("note"))
        row += 1
    row += 1

    s.note(row,
           f"{cfg.product_name} - (c) {cfg.author}. Licensed for personal "
           "use and for a single business. Please do not resell or "
           "redistribute the file.",
           LAST_COL, height=26)

    s.finish(freeze_row=4, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{row + 2}")
    return s
