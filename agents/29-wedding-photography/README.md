# Wedding Photographer Business Manager

Created by Novality Store. This package contains a 23-sheet Excel workbook in two versions:

- **Demo** — fictional example records to explore. Keep it separate from your business data.
- **Blank** — empty registers for your own records. Settings and reference lists retain editable starting defaults; add your own packages before booking.

Both workbooks have protected sheets. The sheet-protection password is **`premium`**. Prepared input cells are unlocked; calculations are locked. Sheet protection is not encryption or a substitute for privacy or backups.

## Get started

1. Open the blank file in Microsoft Excel, save your own copy, and enable editing if Excel asks. Allow the workbook to recalculate. Choose your reporting year and update studio details, currency, tax assumptions, rates, turnaround times, targets, and lists in **Settings & Lists**.
2. Add your own package names, prices and inclusions on **Packages & Pricing**. Enter clients in **Client CRM**, then leads in **Lead Tracker** and weddings in **Wedding Bookings**. Pick the Client ID and package and fill the wedding date, status and other details.
3. Use the generated **Booking ID** on contracts, invoices, timelines, shot lists, editing, galleries, travel, expenses, profit and reviews. Each sheet describes its inputs. In **Profit Analysis**, add exactly one row per booking you want analyzed; it is not created automatically.
4. Record actual invoices, amounts received, dates, refunds and processing fees in **Payments & Invoices**. Record a refund using negative amounts due and received, as applicable. Record your actual business expenses on **Expense Tracker**. Use the calendar, dashboard and reports to review the entered data. Check the selected year and dates when comparing totals.
5. Enter progress, communications and delivery updates manually. Save backups and protect personal information. Do not store payment-card details, identity scans or gallery passwords in the workbook.

## Important operating limits

- **IDs depend on row position.** Do not sort, cut, move, insert or delete populated register rows, and do not change an ID prefix after IDs have been used. Use filters instead. Do not clear a record's trigger field when it is referenced elsewhere; keep its row and update its status. IDs are not permanent database identifiers. Sheet protection helps prevent sorting and structural edits, but cannot prevent every action that might break a link.
- Each register has a fixed prepared range. The standard file provides 200 weddings, 300 clients, 400 leads, 30 packages, 600 payment rows, 900 timeline rows, 1,400 shot rows and 600 expense rows. Other capacities are visible on the sheets. Do not type beyond the prepared rows; rebuild a larger workbook from source if needed.
- Package prices and several assumptions are live lookups, not historical snapshots. Editing a package price or shared setting can change past booking figures. Preserve historical package rows and create a new package name for new pricing. Retired packages remain in the dropdown; avoid selecting them for new bookings. Renaming or deleting a referenced package can break lookups.
- Where a summary uses the first matching editing or gallery row, maintain one primary row per booking. Enter one Profit Analysis row per booking to avoid duplicate analysis totals.
- This is a manual workbook: it does not sync with calendars, email, payment providers or banks; host galleries; collect payments; or create, send or execute contracts. Contract and questionnaire tabs track manually recorded information. Not legal, tax or accounting advice.

## Money and profit assumptions

Booking profit is the pre-tax booking value less direct business-share costs and payment processing fees. Record actual wedding costs once in **Expense Tracker** with the appropriate Booking ID; do not also duplicate payment fees there. Team, editing and travel estimates elsewhere do **not** automatically become actual costs. A direct-cost category without a Booking ID is flagged and excluded from both booking profit and overhead; assign it to the correct booking. Other unlinked operating costs are treated as overhead.

The management cost uses the business-use share of the gross expense. Rows classified as capital/asset or owner drawing, and the tax and national insurance category, are excluded from management profit; this is not an accounting or tax treatment. Profit Analysis allocates each wedding-year's overhead equally across earning bookings for that year. It separately includes gallery after-sales, which booking-based annual figures may omit; avoid entering the same sale as both a booking add-on and gallery after-sale. Different reports can therefore differ in scope, timing and tax treatment. Verify figures and consult an accountant.

## Source and checks

The supplied Python generator and tools are included in the source ZIP. Python 3 and XlsxWriter are required; openpyxl is needed for structural tests, and `formulas` for the optional small-workbook calculation check. From the extracted source folder:

```bash
python -m pip install xlsxwriter openpyxl formulas
python build_wedding_workbook.py --blank -o "Wedding Blank.xlsx"
python build_wedding_workbook.py -o "Wedding Demo.xlsx"
python build_wedding_workbook.py --help
python tools/check_parens.py "Wedding Blank.xlsx"
python tools/validate_wedding_workbook.py "Wedding Blank.xlsx"
```

The release files were structurally checked, including all prepared register cells, sheet protection, formula syntax balance, XML, and unsupported modern-function scans. Smaller blank and demo builds were calculated with an independent Python formula engine; a targeted scenario checked tax, refund status, business-use cost, capital exclusion, contract/review status and overhead allocation. The full 115,596-formula releases were not recalculated with that engine. Formula cached values are initially zero until a spreadsheet application recalculates them. **Windows Excel opening, repair-free behavior and recalculation were not verified in this environment.** Test a copy in your version of Excel before relying on it; other spreadsheet applications may differ.
