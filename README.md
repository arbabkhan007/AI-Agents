# Pet Sitting &amp; Dog Walking Business Spreadsheet

A ready-to-use Excel workbook for a pet sitting and dog walking business, and
the Python program that builds it. Twenty-seven tabs, roughly 50,800 live
formulas, one hidden calculation engine, a modern indigo-and-amber design and
enough example data that every chart and report shows real numbers on the first
open.

* Author: **Novality Store**
* Sheet protection password: **`premium`**
* Works in Excel 2010 and later, LibreOffice Calc and Google Sheets.
* Formulas deliberately avoid XLOOKUP, IFS and dynamic arrays so older Excel
  versions still calculate.

---

## 1. The quick version

```bash
pip install XlsxWriter
python build_pet_sitting_workbook.py
```

The workbook appears at `output/Pet Sitting Business Spreadsheet.xlsx`
(about 860 KB). Open it and read the **Start Here** tab.

Options you will actually use:

| Option | What it does |
| --- | --- |
| `--blank` | Empty registers, no example records |
| `--business "Paws & Claws"` | Your business name on the cover and invoices |
| `--currency "£"` `--currency-code GBP` | Currency symbol and code |
| `--unit miles` | Mileage in miles instead of km |
| `--password secret` | Change the sheet protection password |
| `--author "Your Name"` | Document author / creator |
| `--rows 1000` | More rows of capacity in the big registers |
| `--today 2026-01-01` | Treat this date as "today" when writing example data |
| `--no-protect` | Leave sheets unprotected (development only) |

---

## 2. What is on each tab

The tabs run in the order you work through a job: set up, book it, visit it,
invoice it, get paid, count the money.

### Start Here
A one-screen cover: what the workbook does, how the tabs fit together, which
cells you type in and what the colours mean. Read it first.

### Dashboard
The numbers you check every morning. Twelve KPI tiles (revenue collected,
invoiced, outstanding, overdue, expenses, net profit, profit margin, mileage
claim, cash per visit, bookings in the period, completed visits, upcoming
visits, missed visits, active clients, pets on the books, average rating), a
twelve-month revenue, expenses and profit chart, a top-ten clients list and a
best-performing services list. The period is driven by the two named cells
`Dash_Year` and `Dash_MonthName`, so switching the month is one drop-down, and
sparklines under the month table give you the shape of the year in one row.

### Settings
Every preference in one place: business name and address, contact details,
working hours, tax name and rate, default deposit percentage, mileage rate per
distance unit, currency symbol and code, financial year start, invoice terms,
late fee and the target revenue/expense figures the Budget tab compares
against. Nothing is hard-coded anywhere else — every other tab reads these
cells.

### Lists
The drop-down source data: client types, pet species, service categories,
payment methods, expense categories, staff roles, visit outcomes and so on.
Each list is a dynamic name with forty rows of head-room, so adding a sixth
payment method is a one-cell edit.

### Services
Your service catalogue with price, cost, duration, extra-pet fee, weekend
surcharge and deposit percentage. Every price used anywhere in the workbook
comes from this tab, so a price rise is one edit, not thirty.

### Clients
Name, contact details, address, type, status, preferred pet care instructions,
emergency contact, how they heard about you, plus live columns for bookings,
lifetime revenue, amount outstanding, last visit and next visit. A client
summary block at the top of the tab shows active, inactive and overdue counts.

### Pets
Every animal: name, species, breed, age, weight, owner (looked up from
Clients), feeding schedule, medication, allergies, behaviour notes, vet details
and insurance. Colour-coded by pet type.

### Bookings
The scheduling heart of the workbook. Date, time, client, pet(s), service,
sitter, location, status, notes, plus calculated base charge, extra-pet fee,
weekend surcharge, subtotal, tax and total. A `Schedule check` column flags a
double-booking for the same sitter, and `Days until` and `Timing` columns tell
you what is coming up and what is late.

### Visit Log
What actually happened on the job: check-in and check-out times, duration,
hours worked, GPS distance travelled, outcome, notes, medication given, food
and water checks, and the client rating. `Duration` and `Hours worked` are
computed from the clock times, so the mileage and wage figures are always
consistent with the log.

### Health Log
Weight, medication, allergies, flea and worm treatments, vaccinations and
dental checks per pet over time, with the last treatment date and a
`Next due` column that drives the reminders on the Health Log.

### Incidents
Anything that went wrong: date, pet, sitter, severity, description, action
taken, cost, insurance claim number and owner-notified flag. Colour-coded by
severity so the red ones find you.

### Messages
Client communication log: date, direction, client, subject, channel, message
body, who handled it and whether it was resolved.

### Invoices
Invoice number, date, due date, client, related booking, description, line
amounts, tax, total, amount paid and balance due. Payment status
(Paid / Part paid / Overdue / Unpaid) is calculated, so is the days overdue.
Two invoice templates and the numbered invoice sheet are driven from here.

### Payments
Money in: date, client, invoice number, amount, method, reference and receipt
number. A summary block at the top shows money received this month, this year
and the outstanding total, and the reconciliation column shows how much of an
invoice is still open.

### Expenses
Money out: date, category, supplier, description, amount, payment method,
whether it is billable to a client, the VAT you can reclaim and the running
total. Categories feed straight into the expense chart on the Dashboard.

### Mileage
Every trip: date, sitter, purpose, start and end distance, distance travelled,
rate per distance unit, claim amount and the tax year it belongs to. A summary
block gives total distance, total claim and the current tax-year figure.

### Staff
Name, role, contact details, start date, hourly rate, commission percentage,
certificate expiry and status, plus calculated visits completed, hours worked,
revenue collected and pay due. `Action needed` flags expired and due
certificates.

### Inventory
Stock control: item, category, supplier, quantity in stock, minimum level,
unit cost, reorder quantity and value. `Stock status` and `Order now` tell you
what to buy before you run out.

### Reminders
The tab that saves the day. Four alert blocks — upcoming bookings in the next
seven days, overdue invoices, stock items to reorder and certificates to renew
— plus the vaccination and treatment due dates from the Health Log. Each block
counts down from `Total alerts`.

### Reports
A period report with a start and end date (a chart of who owes you money by
invoice age sits under the ageing table): revenue, expenses and profit for
the period, a breakdown by service and by expense category, the top five
clients, sitter performance and the best and worst days. `RepFrom` and `RepTo`
are the two dates you change.

### Budget
A planning tab: target revenue and expenses, fixed costs, growth rate, opening
cash and the savings target, with a budget-versus-actual chart for the twelve
months. It shows the budget-versus-actual variance for
revenue, expenses and profit, a monthly forecast with a year total and the
progress towards the savings target.

### Print Invoice, Print Pet Care, Print Visit
Three clean, formatted one-page documents — a client invoice, a pet care
instruction sheet and a visit summary — that fill themselves in from the
record you pick in the drop-down at the top of the tab. Print areas, print
titles and A4 page set-up are already configured.

### Print Forms
Six blank forms to print and hand to a client or take on a job: client intake,
pet information, booking request, emergency contact, incident report and the
walk sign-in sheet.

### Help
Every column explained: what it means, whether it is typed in or calculated,
and which tab the calculated ones come from. Plus a colour legend, a formula
cheat-sheet and the protection rules.

### Calc *(hidden)*
The engine. Helper tables, drop-down sources, ranking lists and the lookup
ranges the report tabs read. It is hidden and protected on purpose — leave it
alone and everything keeps working.

---

## 3. How the colours work

The palette is defined once in `pet_sitting_spreadsheet/config.py` and every
sheet module reads it from there, so the whole workbook stays consistent.

| Colour | Where | Meaning |
| --- | --- | --- |
| Indigo `#4338CA` / `#6366F1` | banners, section bars, titles | structure and headings |
| Indigo-50 `#EEF2FF` | table headers, soft panels | table furniture |
| Amber `#F59E0B` / `#FFFBEB` | KPI tiles, accents, cover | the things to notice |
| Cream `#FFFDF5` | value cells | **type here** |
| Slate-100 `#F1F5F9` | calculated cells | calculated, do not touch |
| Slate-900 `#0F172A` | body text | text |
| Slate-500 `#64748B` | notes, secondary text | secondary text |
| Emerald `#D1FAE5` / `#047857` | status flags | good |
| Amber-100 `#FEF3C7` / `#B45309` | status flags | attention |
| Rose `#FFE4E6` / `#BE123C` | status flags | bad |
| Blue-100 `#DBEAFE` / `#1D4ED8` | status flags | information |
| Slate-50 `#F8FAFC` | note boxes | background notes |

Tab colours follow the same logic: dark slate for the overview tabs, indigo for
data tabs, amber for the working tabs, emerald for the money tabs and rose for
the risk tabs.

**The rule that matters:** cream cells are for typing in, grey cells are
calculated. Every formula cell is locked and every sheet is protected with the
password `premium`, so the maths cannot be typed over by accident.

---

## 4. How it is built

```
build_pet_sitting_workbook.py      entry point: python build_pet_sitting_workbook.py
pet_sitting_spreadsheet/
  __init__.py      package + version
  __main__.py      python -m pet_sitting_spreadsheet
  cli.py           command line options
  config.py        palette, defaults, named cells, row counts
  layout.py        column widths, page set-up, print areas
  formats.py       every cell format, built from the palette
  writer.py        SheetWriter: banners, sections, KPI tiles, tables
  names.py         defined names, dynamic ranges, cross-sheet references
  build.py         assembles the 27 sheets in order
  sample_data.py   the example records
  sheets/
    common.py      Col, conditional formatting and validation helpers
    lists.py       drop-down source data
    settings.py    services.py   clients.py   pets.py   bookings.py
    visits.py      health.py     incidents.py messages.py
    invoices.py    payments.py   expenses.py  mileage.py
    staff.py       inventory.py  reminders.py calc.py
    dashboard.py   reports.py    budget.py    start_here.py
    printables.py  help_tab.py
tools/
  validate_workbook.py   structural check of the finished file
  check_sample_data.py   every example record joins up
  recalc_check.py        recalculates every formula and looks for errors
  export_source_md.py    the whole program in one markdown document
  make_download_zip.py   a shareable zip of the source
```

Each sheet module exports one `spec(book, fmts, cfg, reg)` function that
receives the workbook, the format bank, the configuration and a registry of
named ranges. It declares its columns as `Col(key, header, width, kind, ...)`
records — a column's header, width, format, formula, conditional formatting and
validation all live in one line — then calls `writer.table()` to write the
header, the formulas and the rules. Changing a column means editing one line.

### Running the checks

```bash
python tools/validate_workbook.py "output/Pet Sitting Business Spreadsheet.xlsx"
python tools/check_sample_data.py "output/Pet Sitting Business Spreadsheet.xlsx"

# real recalculation, needs `formulas`; check a smaller build first
python build_pet_sitting_workbook.py --rows 120 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

`recalc_check.py` loads the file into a formula engine, calculates all
16,000-plus formulas of a small build and reports any cell that does not
evaluate to a real answer. The full 50,800-formula workbook takes several
minutes and a lot of memory, so build small first.

---

## 5. How to use the workbook

[`HOW_TO_USE.md`](HOW_TO_USE.md) is the customer manual: the two rules (cream
cells are for typing, grey cells are calculated; every sheet is protected with
the password `premium`), a twenty-minute first-time setup walkthrough of the
Settings and Services tabs, the daily and weekly workflow, a tab-by-tab guide
to what to type where, how the pricing chain works, invoicing and part
payments, reading the Dashboard, printing, common tasks and troubleshooting.

## 6. Things worth knowing

* **Everything is a formula.** Row IDs (`BK-0001`, `INV-1001`), totals, taxes,
  balances, statuses, reminders and the dashboard are all calculated. Type a
  booking and the invoice, the payment status, the client's lifetime revenue,
  the sitter's pay and the dashboard all move on their own.
* **The registers are pre-formatted for 250–400 rows** depending on the tab,
  with data validation and conditional formatting already applied down the
  whole range. Use `--rows` if you need more.
* **Cross-tab references go through named ranges** (`[[Clients.name]]`,
  `[[Calc.top_clients#1]]`), never raw `Sheet1!A1` addresses, so inserting a
  column never breaks a formula.
* **Three real charts** (Dashboard: revenue/expenses/profit, Reports: invoice
  ageing, Budget: budget versus actual) plus sparklines on the Dashboard and
  Budget for a twelve-month trend in a single row.
* **Sample data is illustrative.** The clients, pets and staff names are made
  up. Delete the rows you do not want and the workbook keeps working.
