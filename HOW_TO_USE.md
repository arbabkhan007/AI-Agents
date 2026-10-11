# How to use it

A plain-English manual for the **Pet Sitting & Dog Walking Business
Spreadsheet**. No spreadsheet experience needed — if you can type in a cell and
pick from a drop-down, you can run this.

Read the first two sections before you type anything. After that, use the
contents list to jump to whatever you need.

---

## Contents

1. [The two rules](#1-the-two-rules)
2. [First-time setup](#2-first-time-setup) — about 20 minutes
3. [The daily workflow](#3-the-daily-workflow)
4. [Tab by tab: what to type where](#4-tab-by-tab-what-to-type-where)
5. [How the pricing works](#5-how-the-pricing-works)
6. [Invoicing and getting paid](#6-invoicing-and-getting-paid)
7. [Reading the Dashboard](#7-reading-the-dashboard)
8. [Reports and Budget](#8-reports-and-budget)
9. [Printing](#9-printing)
10. [Reminders: your daily to-do list](#10-reminders-your-daily-to-do-list)
11. [Common tasks](#11-common-tasks)
12. [Troubleshooting](#12-troubleshooting)
13. [Using it in Google Sheets, LibreOffice or Numbers](#13-using-it-in-google-sheets-libreoffice-or-numbers)

---

## 1. The two rules

### Rule 1 — cream cells are for typing, grey cells are not

| Colour | Meaning |
| --- | --- |
| **Cream** `#FFFDF5` | Type here. These are the only cells you need to touch. |
| **Grey** `#F1F5F9` | Calculated. The workbook fills these in for you. |

If a cell is grey, something else in the workbook is working it out. Typing
over it is locked anyway (see rule 2), which is the point — it stops the maths
getting broken by accident.

Everything with a **drop-down arrow** is a pick-list. Click the cell, click the
arrow, choose one. You can also just start typing and Excel will match it.

### Rule 2 — the sheets are protected, on purpose

Every tab is protected with the password **`premium`** so formulas cannot be
overwritten by a stray keystroke. You never need to unprotect anything for
normal use — the cream cells stay editable while the sheet is protected.

If you do need to change something structural (insert a logo, rename a
heading, add a column):

1. Go to the **Review** tab in Excel.
2. Click **Unprotect Sheet**.
3. Type `premium` and press Enter.
4. Make your change.
5. Click **Protect Sheet** again, leave the password box empty or re-enter
   `premium`, and press OK.

> To change the password for good: Review > Unprotect Sheet, then Review >
> Protect Sheet, type your new password twice. Do this on every tab.

### Where everything lives

The tabs run left to right in the order you use them:

```text
Start Here   Dashboard   Settings   Lists   Services
Clients      Pets        Bookings   Visit Log
Health Log   Incidents   Messages
Invoices     Payments    Expenses   Mileage
Staff        Inventory   Reminders
Reports      Budget
Print Invoice   Print Pet Care   Print Visit   Print Forms
Help
Calc  (hidden - the engine, leave it alone)
```

The last tab, **Calc**, is hidden. It holds the helper tables the Dashboard and
Reports read. You never need to open it.

---

## 2. First-time setup

Do these in order. Twenty minutes now saves hours later.

### Step 1 — Open the file properly

Double-click the `.xlsx` file. If Excel shows a yellow **Enable Editing** bar
at the top, click it. If it shows **Enable Content**, click that too — the
workbook has no macros, so nothing risky loads.

### Step 2 — Fill in the Settings tab

Open **Settings**. Work down the page. Everything here feeds the rest of the
workbook, so it only has to be done once.

**Your business details (rows 6–22)**

| What | Why it matters |
| --- | --- |
| Business name | Appears on the cover, invoices and every print sheet |
| Owner, phone, email, website | Printed on invoices and pet care sheets |
| Address, city, state, post code, country | Printed on invoices |
| Business / tax number | Printed on invoices |
| Payment details for invoices | Bank details on the invoice, so clients know where to pay |
| Insurance provider, policy number, renewal date | Feeds the renewal reminders |
| Licence / permit and renewal date | Feeds the renewal reminders |

**Your logo (row 26)** — there is a placeholder box. Unprotect the sheet,
delete the placeholder text, then Insert > Pictures and choose your logo. Drag
it over the box and resize. Re-protect when you are done.

**Money (rows 32–44)**

| Setting | What to put |
| --- | --- |
| Currency symbol | `$`, `£`, `€`, `A$` — whatever you price in |
| Currency code | `USD`, `GBP`, `EUR`, `AUD` |
| Distance unit | `km` or `miles` |
| Financial year starts | The month your tax year begins |
| Tax name | What you call it — "Sales Tax", "VAT", "GST" |
| Registered for tax? | Yes or No |
| Tax rate | As a percentage, e.g. `8%` or `20%` |
| Prices already include tax? | Yes if your listed prices are tax-inclusive |
| Tax reserve to set aside | The share of profit you keep back for tax |

**Invoice numbering (rows 47–51)**

| Setting | What to put |
| --- | --- |
| Invoice prefix | `INV-`, or your own |
| First invoice number | Where your numbering starts, e.g. `1001` |
| Payment terms (days) | How long clients have to pay — 7, 14, 30 |
| Standard deposit | The deposit you ask for up front, e.g. `25%` |
| Late fee | Charged automatically on overdue invoices, e.g. `5%` |

**ID prefixes (rows 52–54)** — `CL-`, `PET-`, `BK-` by default. Change them if
you already use your own reference style.

**Pricing rules (rows 57–64)** — these are the defaults the booking sheet uses.
You can override any of them per booking.

| Setting | What it does |
| --- | --- |
| Additional pet fee (default) | Added for each pet beyond the first |
| Holiday surcharge | Percentage added on the holiday dates you list |
| Weekend surcharge | Percentage added on Saturday and Sunday bookings |
| Emergency / last-minute fee | Flat fee for bookings inside the last-minute window |
| Last-minute window (days) | How close to the booking counts as last-minute |
| Loyalty discount | Given to clients past the loyalty threshold |
| Loyalty threshold (bookings) | How many bookings earns the discount |
| Average staff cost per hour | Used to estimate profit per service |

**Mileage and travel (rows 67–70)**

| Setting | What it does |
| --- | --- |
| Mileage rate per km | What you claim back from the tax office |
| Client travel fee per km | What you charge the client for travel |
| Free travel distance | Distance included before travel is charged |
| Travel time allowance (mins) | Free travel time before time is billed |

**Alerts and automation (rows 73–80)** — how many days ahead the workbook warns
you.

| Setting | Default | Meaning |
| --- | --- | --- |
| Booking reminder lead (days) | 3 | Send a confirmation this many days before |
| Vaccination alert (days before) | 30 | Warn this many days before a jab expires |
| Inactive client after (days) | 60 | Flag a client who has not booked in this long |
| Follow-up after service (days) | 5 | Remind you to check in after a visit |
| Expiry / renewal alert (days) | 30 | Insurance, licence, stock and certificate warnings |
| Default visit length (mins) | 30 | Pre-fills the scheduled visit length |
| Working day starts / ends | 07:00 / 19:00 | Used by the schedule clash check |

**Holidays (rows 85–114)** — list the dates you charge a holiday surcharge for.
Add a date and a note; the booking sheet picks the surcharge up automatically.

### Step 3 — Build your price list on the Services tab

This is the most valuable five minutes you will spend. One row per service:

1. **Service name** — e.g. "Dog Walk - 60 min".
2. **Category** — pick from the drop-down.
3. **Billing unit** — per visit, per hour, per night, per week.
4. **Standard length (mins)** — how long the service normally takes.
5. **Base rate** — your price.
6. **Additional pet fee** — what a second or third dog costs.
7. **Holiday / weekend surcharge** — leave blank to use the Settings default.
8. **Travel fee applies?** — Yes or No.
9. **Staff cost per unit** — what it costs you to deliver (sitter pay, fuel).
10. **Active?** — set to No to retire a service without deleting it.

The sheet then works out your gross profit and margin per service, how many
times each has been booked, and the revenue it has earned. **Change a price
here once and it changes everywhere** — every future booking reprices itself.

### Step 4 — Add your clients and their pets

Go to **Clients** and type into the first cream row. The ID column fills itself
in (`CL-0001`, `CL-0002`, …).

Then go to **Pets**. Pick the owner from the **Owner (client)** drop-down and
the client ID fills itself in. Fill in the bits that matter on a job — feeding,
medication, allergies, behaviour, vet details, key and alarm instructions.
This is the tab you will actually read at 7am standing in someone's hallway.

### Step 5 — Add your team (if you have one)

**Staff**: name, role, contact, pay type and rate, certifications and expiry
dates. The sheet counts each sitter's visits, hours, distance and pay due, and
flags certificates that have expired or are about to.

### Step 6 — You are set up

That is the whole setup. Everything from here is day-to-day typing.

---

## 3. The daily workflow

**Morning — five minutes**

1. Open **Reminders**. It tells you what needs doing today: bookings due in
   the next seven days, invoices overdue, stock running low, certificates to
   renew.
2. Open **Dashboard** and check the six money tiles and the "Upcoming
   (7 days)" count.

**When a client enquires — two minutes**

1. **Bookings** tab, new row.
2. Pick the client, the pets, the service and the sitter.
3. Enter the date, start time and end time.
4. The price calculates itself. Read the **Schedule check** column — if it says
   `Conflict`, that sitter is already booked at that time.
5. Set the status to `Confirmed` and set **Confirmed to client** to Yes.

**After the visit — three minutes**

1. **Visit Log** tab, new row.
2. Pick the booking from the **Booking ID** drop-down — the client, pet,
   service and sitter fill themselves in.
3. Type **Arrived** and **Departed** times. Minutes on site, walk minutes and
   hours worked calculate themselves.
4. Fill in the care checkboxes: fed, fresh water, medication given, potty /
   litter, exercise, grooming, mood, appetite, health observations.
5. Set **Visit status** to `Completed`.
6. Set **Client updated** to Yes once you have sent the report.

**End of the week — ten minutes**

1. **Invoices** — raise anything not yet billed (see section 6).
2. **Payments** — record money that came in.
3. **Expenses** — enter what you spent.
4. **Mileage** — log the trips.
5. **Reminders** — clear anything flagged.

**End of the month — twenty minutes**

1. **Reports** — set the date range and read the profit and loss.
2. **Budget** — compare actual against target.
3. Save a dated copy: File > Save As, add the month to the filename.

---

## 4. Tab by tab: what to type where

Each register works the same way: **type in the cream columns, read the grey
ones**. Rows are pre-formatted and pre-formulated, so a new row is just the
next one down.

### Clients

Type: name, phone, email, address, emergency contact, preferred contact,
referral source, registration date, status, key details, access instructions,
contract status, preferences and notes.

The sheet works out: how many pets, bookings and visits each client has, their
last service, days since, next booking, lifetime revenue, amount outstanding,
average booking value, loyalty status — and flags duplicates and missing
information.

### Pets

Type: name, owner, type, breed, date of birth, gender, weight, colour,
microchip, temperament, behaviour issues, allergies, medical conditions, vet
and emergency clinic details, vaccination dates, insurance, feeding
instructions, medication, walking preferences, potty routine, grooming, risk
flag and handling instructions.

The sheet works out: age, vaccination status (with a colour-coded warning), and
alerts for anything needing attention.

### Bookings

Type: client, pets, service, date, start and end time, quantity or nights,
assigned sitter, status, discount, price override (with a reason), notes.

The sheet works out: day of week, hours, rate, extra pet fee, holiday and
weekend surcharges, travel distance and fee, last-minute fee, discount,
subtotal, tax, booking total, whether it repeats, whether the sitter is
double-booked, whether the visit has been logged, the linked invoice, the
payment status, and what action is needed.

### Visit Log

Type: booking ID (everything else fills in), arrived and departed times, walk
start and end, distance walked, the care checkboxes, mood, appetite, health
observations, incident reference, photos link, visit status and notes.

The sheet works out: minutes on site, whether you were on time, walk minutes,
and an action-needed flag.

### Health Log

Type: date, pet, record type, medication or treatment, dosage, scheduled time,
given time, who gave it, status, supply left, refill due, vet appointment,
cost, whether the owner was notified.

The sheet works out: refill alerts and appointment alerts.

### Incidents

Type: date, pet, sitter, type, severity, description, action taken, cost,
insurance claim number, owner notified, status and notes. Colour-coded by
severity, so the serious ones find you.

### Messages

Type: date, client, message type, channel, direction, summary, whether a reply
came back, satisfaction rating, feedback, whether it is a complaint, the issue,
resolution status and notes. The sheet works out days open and follow-up due.

### Invoices

Type: invoice date, client, booking reference (or leave blank to bill
manually), description, quantity and rate, additional fees, discount.

The sheet works out: the invoice number, the due date, the line amount pulled
straight from the booking, the subtotal, tax, invoice total, deposit, amount
paid, refunds, balance due, invoice status, payment status, days overdue,
ageing bucket, the suggested late fee, and the action needed.

### Payments

Type: payment date, client, invoice number, amount applied, method, reference,
tip, late fee collected, refund given, and whether it has cleared and
reconciled.

The sheet works out: how much of the invoice this payment settles, the
remaining invoice balance, total cash in, and the month.

### Expenses

Type: date, category, description, supplier, amount paid, whether tax was
included, who paid, business or personal, business use percentage, receipt
reference, whether it recurs and when it is next due, approval, related client
or booking, staff member, notes.

The sheet works out: net cost, claimable amount, month and action needed.

### Mileage

Type: trip date, driver, client or booking, purpose, from, to, odometer start
and end (or the manual distance), whether it was a round trip, classification,
fuel, parking, tolls and travel time.

The sheet works out: trip distance, total distance, the rate, your claim, and
the total claimable including fuel, parking and tolls.

### Staff

Type: name, contact, role, employment type, start date, status, availability,
days off, pay type and rate, certifications and expiry, background check,
emergency contact, leave, notes.

The sheet works out: bookings assigned, visits completed, hours worked, km
driven, revenue delivered, pay due, revenue per hour, completion rate,
certificate status and action needed.

### Inventory

Type: item, category, supplier, unit, unit cost, quantity in stock, minimum
level, reorder quantity, last purchased, quantity last bought, last purchase
cost, expiry date, notes.

The sheet works out: stock value, stock status (In stock / Low / Out of
stock), expiry status, usage this month and what to reorder.

### Lists

Every drop-down in the workbook is fed from this tab. To add a new option —
a sixth payment method, a new service category — just type it in the next free
row of that column. The drop-down updates immediately.

---

## 5. How the pricing works

A booking prices itself in this order:

```text
Base charge          from the Services tab, for the service you picked
+ Extra pet fee      (number of pets - 1) x additional pet fee
+ Holiday surcharge  if the booking date is on your holiday list
+ Weekend surcharge  if the booking date is a Saturday or Sunday
+ Travel fee         distance beyond the free allowance x travel fee per km
+ Last-minute fee    if the booking is inside your last-minute window
- Discount           loyalty or manual
= Subtotal
+ Tax                at your tax rate, unless prices include tax
= Booking total
```

You can override any of it. Put a figure in **Price override** and type why in
**Override reason** — the reason is there so future-you knows what happened.

---

## 6. Invoicing and getting paid

### The easy way — invoice from a booking

1. Open **Invoices**, go to the next empty row.
2. Type the invoice date and pick the client.
3. Pick the **Booking ref** from the drop-down.
4. The line amount, subtotal, tax and total all fill themselves in from the
   booking.
5. The invoice number, due date, status, ageing and balance due calculate
   themselves.

Done. The invoice now appears on the Dashboard's outstanding and overdue tiles
if it is not paid.

### The manual way — bill anything

Leave **Booking ref** blank and type a **Description**, a **Qty** and a
**Rate**. Use this for monthly packages, retail sales or one-off charges.

### Recording a payment

1. Open **Payments**, next empty row.
2. Payment date, client, and the invoice number from the drop-down.
3. Amount applied, method, reference.
4. The sheet works out what the payment settles and what is left owing.

Part payments work exactly the same way — record each one against the same
invoice number and the balance comes down each time.

### Chasing money

The **Dashboard** shows **Outstanding** (everything unpaid) and **Overdue**
(past the due date). The **Reports** tab has an invoice ageing table — who owes
you money, and how old the debt is. The **Reminders** tab lists every overdue
invoice row by row.

---

## 7. Reading the Dashboard

Two cells control the whole tab:

| Cell | What it does |
| --- | --- |
| **Year** (C6) | The reporting year |
| **Month** (F6) | Pick a month, or "All year" |

Everything else updates from those two.

**The money tiles** — revenue collected, invoiced, outstanding, overdue,
expenses, net profit, profit margin, average booking value, revenue per active
client, mileage claim, tax to set aside, cash collected per visit.

**The operations tiles** — bookings in the period, completed, cancelled,
upcoming in the next seven days, visits completed, missed visits, active
clients, pets on the books, new clients, repeat clients, unconfirmed bookings
and average rating.

**The month table** — twelve rows, one per month: revenue, invoiced, expenses,
profit, margin, bookings, completed, cancelled, visits, new clients, distance,
last year's revenue and the change. Underneath it, sparklines show the shape of
the year, and a chart plots revenue, expenses and profit together.

**Revenue by service** and **expenses by category** — where the money comes
from and where it goes, with data bars so the big ones stand out.

**Top clients** and **the action list** — your ten best clients this period,
and ten things that need doing today (overdue invoices, unconfirmed bookings,
clashes, visits to log, expired vaccinations, low stock, inactive clients,
unresolved complaints). The red counts are the ones to look at.

---

## 8. Reports and Budget

### Reports

Set the two dates at the top — **From** (B6) and **To** (D6) — and the whole
tab rebuilds for that period. Eight reports:

1. Booking and service delivery
2. Profit and loss for the period
3. Revenue and profit by service
4. Clients, outstanding money and invoice ageing
5. Expenses by category
6. Staff performance
7. Client retention and marketing
8. Cancellation analysis

Use File > Print and choose "Print active sheet" — the print area is already
set.

### Budget

Six inputs drive it:

| Cell | What it is |
| --- | --- |
| **Target_Revenue** (B6) | What you want to earn this year |
| **Target_Expenses** (B7) | What you plan to spend |
| **FixedCosts** (B10) | Costs that do not change month to month |
| **GrowthRate** (B14) | Assumed growth for the forecast |
| **OpeningCash** (B55) | Cash in the bank at the start of the year |
| **SavingsTarget** (B61) | What you are saving towards |

It then shows targets for the dashboard year, budget versus actual month by
month with a chart, the cash flow and owner money, and the year-on-year
comparison.

---

## 9. Printing

Four tabs are set up to print as-is. Each has a drop-down at the top — pick the
record you want and the page fills itself in.

| Tab | Pick | What you get |
| --- | --- | --- |
| **Print Invoice** | Invoice number | A client-ready invoice |
| **Print Pet Care** | Pet | A pet care instruction sheet to leave on the kitchen counter |
| **Print Visit** | Visit ID | A visit summary for the client |
| **Print Forms** | nothing to pick | Six blank forms: client intake, pet information, booking request, emergency contact, incident report, walk sign-in |

Print areas, margins and page orientation are already configured. Just press
Ctrl+P (Cmd+P on a Mac) and print.

---

## 10. Reminders: your daily to-do list

This is the tab that saves your business. It has four alert blocks:

* **Upcoming bookings** in the next seven days
* **Overdue invoices** to chase
* **Stock items** to reorder
* **Certificates** to renew (staff, insurance, licence)

plus the vaccination and treatment due dates from the Health Log. Each block
counts down from **Total alerts** at the top.

Open it every morning. Work down the list. That is the whole system.

---

## 11. Common tasks

### Delete the example data

The filled workbook comes with example clients, pets, bookings and invoices so
you can see how it works. When you are ready:

1. Go to the tab.
2. Select the whole example rows — click the row number on the far left, hold
   Shift and click the last example row number.
3. Press Delete. **Do not right-click and delete the rows** — that would remove
   the formulas underneath.

Or just open the **blank** workbook that came with this download and start
there. It is the same file with empty registers.

### Add a new client, pet or booking

Go to the tab and type in the next empty row. The ID, totals, statuses and
alerts fill themselves in. Do not skip rows — the formulas run down the whole
range, so an empty row in the middle is fine but a deleted row is not.

### Change a price

**Services** tab. Change the base rate. Every future booking reprices itself.
Past bookings and invoices keep the price they were billed at.

### Add a new drop-down option

**Lists** tab. Find the column for that list and type the new option in the
next free row. The drop-down picks it up straight away.

### Add more rows

The registers come pre-formatted: Clients and Pets 250 rows, Bookings and Visit
Log 400, Invoices, Payments, Expenses and Mileage 300, Health Log and Messages
200, Incidents 100, Staff 40, Inventory 120.

If you need more, the honest answer is to rebuild the file with the generator
(see the source code) — or, for a handful of rows, select the last formatted
row, copy it, and paste it down. Copying a formatted row carries the formulas,
validation and formatting with it.

### Change the currency or distance unit

**Settings** tab, rows 32–36. Change the symbol, code and distance unit.
Everything reformats.

### Back up

File > Save As, add the date to the filename, e.g.
`Pet Sitting Business 2026-10.xlsx`. Do this at the end of every month, and
keep client addresses and access codes out of shared drives and email.

---

## 12. Troubleshooting

**A cell shows `#VALUE!` or `#DIV/0!`**
Something it depends on is empty or the wrong type — usually a date typed as
text, or a number in a text column. Check the cells to the left and above; they
are almost always the input that is missing.

**A drop-down is empty**
The list it reads from is empty, or the cell above the list has been cleared.
Check the relevant column on the **Lists** tab.

**The Dashboard shows zeros**
Check the **Year** (C6) and **Month** (F6) cells. If the year is set to a year
with no data, everything reads zero. Also check the **Reports** date range.

**I cannot type in a cell**
It is a calculated cell, and the sheet is protected. That is working as
intended. If you genuinely need to change it, unprotect the sheet with the
password `premium`.

**A booking says `Conflict`**
The same sitter is booked at an overlapping time. Either change the sitter, or
change the time.

**I deleted a row and now formulas are broken**
Undo it (Ctrl+Z). Rows carry the formulas — clear the *contents* instead of
deleting the row.

**The numbers look wrong after I changed a price**
Recalculate: press F9 (or Ctrl+= in some versions). If you are in Google
Sheets, everything recalculates automatically.

---

## 13. Using it in Google Sheets, LibreOffice or Numbers

**Google Sheets** — File > Import > Upload, then open. Drop-downs, conditional
formatting, data validation and formulas all carry over. The workbook uses only
functions that exist in Sheets. One thing to know: Google Sheets does not
support Excel's sparklines, so the sparkline row on the Dashboard and Budget
will look empty — the numbers next to them are still correct, and the charts
work.

**LibreOffice Calc** — open the file directly. Everything works. If a
drop-down behaves oddly, check Tools > Options > Calc > General > "Show list of
recently used functions" is not the cause; the validation itself is fine.

**Apple Numbers** — Numbers will import it, but complex workbooks lose data
validation and some conditional formatting in translation. If you are on a Mac,
use Excel for Mac or LibreOffice rather than Numbers.

---

## Quick reference card

| I want to… | Go to |
| --- | --- |
| See how the business is doing | **Dashboard** |
| Change my prices or business details | **Settings** |
| Add or edit my price list | **Services** |
| Add a client | **Clients** |
| Add a pet | **Pets** |
| Book a job | **Bookings** |
| Record what happened on a visit | **Visit Log** |
| Raise an invoice | **Invoices** |
| Record a payment | **Payments** |
| Log what I spent | **Expenses** |
| Claim mileage | **Mileage** |
| Pay or manage sitters | **Staff** |
| Reorder stock | **Inventory** |
| See what needs doing today | **Reminders** |
| Get a profit and loss report | **Reports** |
| Plan the year | **Budget** |
| Print an invoice or care sheet | **Print Invoice / Print Pet Care** |
| Print a blank form | **Print Forms** |
| Look up what a column means | **Help** |

**Sheet protection password: `premium`**
