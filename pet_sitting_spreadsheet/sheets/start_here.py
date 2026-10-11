"""`Start Here` - welcome page, navigation menu and setup checklist."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry, col_letter, quote_sheet
from ..writer import SheetWriter, list_from

NAME = "Start Here"
LAST_COL = 9

TOUR = [
    ("Settings", "Your business details, rates, tax, surcharges and "
                 "reminder windows - set this up first."),
    ("Lists", "Every drop down list in the workbook. Rename anything to "
              "match the way you talk about your services."),
    ("Services", "Your price list. Billing unit, rate, extra pet fee and "
                 "profit per service."),
    ("Clients", "Client database with keys, contracts, lifetime revenue "
                "and follow-up flags."),
    ("Pets", "Pet profiles: feeding, medication, vet, vaccinations, "
             "temperament and safety warnings."),
    ("Bookings", "The schedule. Prices itself from the Services tab and "
                 "warns you about double bookings."),
    ("Visit Log", "Proof of every walk and visit: times, care given, mood, "
                  "health notes and client updates."),
    ("Health Log", "Medication administration, vaccinations and vet "
                   "appointments."),
    ("Incidents", "Emergency contacts and incident reports."),
    ("Messages", "Client communication, feedback, ratings and complaints."),
    ("Invoices", "Automatic invoice numbers, due dates, tax, balances and "
                 "ageing."),
    ("Payments", "Cash in: payments, deposits, tips, refunds and bank "
                 "reconciliation."),
    ("Expenses", "Every business cost split into tax, net and claimable."),
    ("Mileage", "Trip log with odometer readings and reimbursement."),
    ("Staff", "Team directory, availability, hours worked and pay due."),
    ("Inventory", "Supplies, stock levels, reorder and expiry alerts."),
    ("Dashboard", "The whole business on one page for any month or year."),
    ("Reports", "Printable analytics for any date range - including a "
                "profit and loss statement."),
    ("Budget", "Targets, budget vs actual, break-even, forecast and cash "
               "flow."),
    ("Reminders", "Everything that needs doing today, plus your own task "
                  "list."),
    ("Print Invoice", "A client-ready invoice - pick the invoice number."),
    ("Print Pet Care", "A one page care sheet to leave with a sitter."),
    ("Print Visit", "A single visit report for the client."),
    ("Print Forms", "Blank forms: registration, consent, incident, "
                    "timesheet, mileage, feedback and checklists."),
    ("Help", "Instructions, formula notes, troubleshooting and version "
             "history."),
]

QUICK_START = [
    "1. Open the Settings tab and enter your business details, currency, "
    "tax rate and mileage rate.",
    "2. Edit the Services tab so the names and prices match what you "
    "actually sell.",
    "3. Add your clients, then their pets (choose the owner from the drop "
    "down so they link up).",
    "4. Add your team on the Staff tab - even if that is only you.",
    "5. Take a booking: pick the client, pet and service and the price "
    "calculates itself.",
    "6. After each visit, add a row to the Visit Log and tick off the care "
    "you gave.",
    "7. Raise an invoice, link the booking, and record the payment when it "
    "lands.",
    "8. Log expenses and trips as you go - future you will thank you at "
    "tax time.",
    "9. Check the Reminders tab every morning and the Dashboard every "
    "week.",
    "10. Print the reports you need at month end and save a dated backup.",
]

CHECKLIST = [
    "Business details added on the Settings tab",
    "Currency, tax rate and payment terms checked",
    "Mileage rate and travel fees set",
    "Service names and prices updated",
    "Drop down lists adjusted to suit my business",
    "Public holidays added for this year",
    "First clients entered",
    "Pets added and linked to their owners",
    "Staff or contractors added",
    "Sample data deleted (rows 5 onwards on each tab)",
    "Invoice number and prefix set the way I want",
    "A backup copy saved somewhere safe",
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.accent,
                    landscape=False)
    ws = s.ws

    s.banner(cfg.product_name, cfg.product_subtitle, LAST_COL, nav=False,
             badge=f"{cfg.author} - v{cfg.version}")

    s.set_col(0, 0, 3)
    s.set_col(1, 1, 22)
    s.set_col(2, 7, 13)
    s.set_col(8, 9, 14)

    row = 3
    ws.merge_range(row, 0, row, LAST_COL, "", fmts.chrome("note_box"))
    ws.write_formula(
        row, 0,
        '="Welcome "&Biz_Owner&" - this workbook is set up for "&Biz_Name'
        '&". Cream cells are yours to type in, grey cells are locked '
        'formulas that do the maths for you."',
        fmts.chrome("note_box"))
    ws.set_row(row, 24)
    row += 2

    # ------------------------------------------------------- quick start
    row = s.section(row, "Quick start - ten minutes to a working workbook",
                    LAST_COL)
    row = s.bullets(row, QUICK_START, LAST_COL, first_col=1, height=16)
    row += 1

    # ---------------------------------------------------------- navigation
    row = s.section(row, "Where everything lives", LAST_COL)
    header = row
    s.write(header, 1, "Tab", fmts.chrome("header_left"))
    s.merge(header, 2, LAST_COL, "What it does", fmts.chrome("header"))
    ws.set_row(header, 20)
    row = header + 1
    link_fmt = fmts.chrome("nav")
    note_fmt = fmts.chrome("note")
    for sheet_name, description in TOUR:
        ws.write_url(row, 1, f"internal:{quote_sheet(sheet_name)}!A1",
                     link_fmt, sheet_name)
        s.merge(row, 2, LAST_COL, description, note_fmt)
        ws.set_row(row, 15)
        row += 1
    row += 1

    # ----------------------------------------------------------- checklist
    row = s.section(row, "Getting started checklist", LAST_COL)
    head = row
    s.write(head, 1, "Step", fmts.chrome("header_left"))
    s.merge(head, 2, 6, "What to do", fmts.chrome("header"))
    s.merge(head, 7, 8, "Done?", fmts.chrome("header"))
    ws.set_row(head, 20)
    first = head + 1
    for i, item in enumerate(CHECKLIST):
        r = first + i
        s.write(r, 1, f"Step {i + 1}", fmts.chrome("label"))
        s.merge(r, 2, 6, item, fmts.chrome("label"))
        ws.merge_range(r, 7, r, 8, "No", fmts.input("flag"))
        ws.data_validation(r, 7, r, 8, list_from("YesNoList"))
        ws.conditional_format(r, 7, r, 8, {
            "type": "text", "criteria": "containing", "value": "Yes",
            "format": fmts.cf("good")})
    last = first + len(CHECKLIST) - 1

    progress_row = last + 1
    s.merge(progress_row, 1, 6, "Setup progress",
            fmts.chrome("total_label"))
    fmt = fmts.chrome("total_value", num_format="0%")
    ws.merge_range(progress_row, 7, progress_row, 8, "", fmt)
    ws.write_formula(
        progress_row, 7,
        f'=COUNTIF($H${first + 1}:$H${last + 1},"Yes")/{len(CHECKLIST)}',
        fmt)
    row = progress_row + 2

    # -------------------------------------------------------- colour key
    row = s.section(row, "How to read the colours", LAST_COL)
    legend = [
        ("legend_input", "Cream cell",
         "Type here. These cells stay unlocked while the sheet is "
         "protected."),
        ("legend_calc", "Grey cell",
         "A locked formula. Protected with the password so it cannot be "
         "overwritten by accident."),
    ]
    for key, label, text in legend:
        s.write(row, 1, label, fmts.chrome(key))
        s.merge(row, 2, LAST_COL, text, note_fmt)
        row += 1
    s.write(row, 1, "Red / amber", fmts.chrome("legend_calc",
                                               bg_color=Palette.bad_bg))
    s.merge(row, 2, LAST_COL,
            "Conditional formatting: red means act today, amber means "
            "act soon, green means you are on top of it.", note_fmt)
    row += 2

    # ------------------------------------------------------------- facts
    row = s.section(row, "Product information", LAST_COL)
    facts = [
        ("Product", cfg.product_name),
        ("Edition", f"Version {cfg.version} - released {cfg.release_date}"),
        ("Author", cfg.author),
        ("Formula protection",
         f"Every sheet is protected. Password: {cfg.password} "
         "(Review > Unprotect Sheet if you need to change a formula)."),
        ("Works with",
         "Microsoft Excel 2010 or newer on Windows and Mac, Excel 365, "
         "and Google Sheets after import."),
        ("Support",
         "See the Help tab for troubleshooting, formula notes and backup "
         "guidance."),
    ]
    for label, text in facts:
        s.write(row, 1, label, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, text, note_fmt)
        ws.set_row(row, 15)
        row += 1

    ws.set_row(row + 1, 18)
    s.merge(row + 1, 0, LAST_COL,
            f"(c) {cfg.author} - thank you for your purchase. "
            "Personal and single-business use.",
            fmts.chrome("subtitle"))

    s.finish(freeze_row=3, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{row + 2}")
    return s
