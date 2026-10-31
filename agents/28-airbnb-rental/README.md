# Airbnb & Short-Term Rental Management Spreadsheet

An independently built 20-sheet manual rental-management workbook, supplied with a populated example and a reusable blank template. The original long pasted 37-file source was not available for complete transcription in this workspace; this generator is a new implementation based on the available requirements, not a verified reproduction of that code. Features and limits below describe what is actually included.

## Get started

1. Open **Rental-Demo.xlsx** first and review the Getting Started tab. Open **Rental-Blank.xlsx** for your own data. Microsoft Excel needs to recalculate the formulas on opening; use automatic calculation. Some previewers do not calculate Excel formulas and may show cached zeros.
2. On **Settings & Lists**, set the report year, business name, platform percentages and tax assumption. Example fee rates are illustrative; replace them with your actual contract terms. Set each property's own rate, cleaning fee and cleaning cost in **Property Database**; settings defaults are reference values and do not automatically fill property rows.
3. Add properties, guests and vendors before entering bookings. Use their generated IDs. **Do not sort, insert, delete or move populated register rows**: IDs are generated from physical row numbers, and cleaning tasks are tied to booking row positions. Use filters instead. Keep IDs stable when changing records.
4. Enter bookings and owner/maintenance blocks manually, with checkout as the first unoccupied day. Review every booking's Review and Clashes columns. The monthly and next-14-days calendar shows only entries in this workbook; verify availability directly on all platforms before accepting a reservation.
5. Cleaning Schedule automatically mirrors active booking rows; record your cleaner and task updates on the matching row. Check-in/out records and reviews are entered manually using booking IDs. The printable turnover checklist does not write back to the schedule.
6. Enter each actual net bank deposit once in Platform Revenue & Fees. Multiple split deposits are summed by booking; the expected amount and difference are repeated for reference, so do not sum those columns. Enter all actual costs once in Expense Tracker and set **Count in profit?** to Yes when appropriate. Cleaning and maintenance costs shown on operational sheets are not automatically counted as expenses.

White cells are inputs; pale shaded cells are formulas. The sheets are protected against accidental edits with password **premium**. Sheet protection is not encryption or access control: store guest data securely and follow applicable privacy requirements.

## Workbook contents

- Dashboard, Getting Started, Settings & Lists
- Property Database, Booking Tracker, Booking Calendar, Guest Database
- Check-in & Check-out, Cleaning Schedule, Turnover Checklist
- Platform Revenue & Fees, Expense Tracker, Supplies Inventory, Maintenance Log, Reviews Tracker, Staff & Vendors
- Tax Summary, Occupancy & Performance, Monthly Reports, Annual Reports

Default capacity: 30 properties, 900 booking rows and cleaning rows, 400 guests, 900 payout entries, 700 expense entries, 300 supply and maintenance rows, 600 review rows and 60 vendor rows. The 14-day view displays the **first 12 properties**; the monthly calendar can show any one property. Row-based limits are fixed in the generated workbook. The report year can be changed in Settings. The demo has fictional examples and two split deposits for booking BKG-0001.

## Calculation and operational assumptions

- **Room revenue** = valid stay nights × selected nightly rate − room discount, floored at zero. Rate and cleaning-fee override cells may be zero; leave them empty to use the property's current values. Gross before tax adds cleaning and extra fees. Commission and processing percentages apply to that gross. Net booked revenue is gross less platform fees. Estimates use current property and platform settings, so changing a rate or fee retroactively changes prior calculated bookings; use overrides for historical nightly rates and cleaning fees. Platform percentage overrides per booking are not provided.
- **Self-remitted tax** is estimated as room revenue × the configured tax percentage, added to expected payout but excluded from net booked revenue. The Platform option assumes tax is handled externally and records zero host tax. These are simplified assumptions, not a complete tax or accounting system; reconcile actual statements and seek local tax advice.
- Booked and blocked nights are allocated to each calendar month by date overlap, clipped to the property's listed date. Available nights = listed nights less blocked nights. Occupancy = booked nights ÷ available nights; ADR = allocated room revenue ÷ booked nights; RevPAR = allocated room revenue ÷ available nights. ADR and RevPAR exclude cleaning and extra fees. No deduplication of overlapping stays/blocks is performed: resolve all clashes. Current Active status is applied to the whole report year, so changing property status alters historical availability. The workbook does not model temporary inactive dates other than manually entered blocks.
- Monthly **net booked revenue** is grouped by check-in month, while monthly **room revenue** is allocated by stay night. Expenses use expense dates, actual payouts use bank dates. Therefore the monthly sections use different timing bases and should not be treated as reconciled accrual or cash accounts. The tax summary is a categorisation aid only.
- There is no sync, iCal, API, payment processing, messaging, automated backups or encryption. Data-entry validation and protection are not substitutes for reviewing entries or checking live platform calendars. There is no automatic row expansion beyond configured capacity.

## Build and test

Requires Python 3.10+ and XlsxWriter. Regression tests additionally use openpyxl and formulas. Example:

```sh
python -m pip install XlsxWriter openpyxl formulas
python build_airbnb_workbook.py --output Rental-Demo.xlsx
python build_airbnb_workbook.py --blank --output Rental-Blank.xlsx
python build_airbnb_workbook.py --help
python tools/test_workbook.py
```

The test script expects both workbooks in the `download` folder in the repository, or alongside the `source` folder in the download package. `--rows` scales most registers; property capacity remains 30. `--properties` controls up to four example property records, not workbook capacity. `--no-protect` removes sheet protection; `--password` changes it in newly built files. Default output is `output/Airbnb & Short-Term Rental Management Spreadsheet.xlsx`.

Structural XML and formula-engine regression checks were run for the distributed files, including cross-month nights, overlap boundaries, estimated fees, split-payout variance, ADR and RevPAR. **Opening and recalculation in Windows Excel 2010 or newer has not been verified in this environment.** The formulas intentionally avoid modern dynamic-array functions, XLOOKUP, IFS, MAXIFS and TEXTJOIN, but this is not a substitute for testing in the actual target version of Excel. Back up your data and test your copy before operational use.
