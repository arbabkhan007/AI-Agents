# Daycare workbook — independently completed

The provided source was incomplete in the workspace. With the user's permission,
`daycare_business_spreadsheet/build.py` was independently implemented to produce
both 23-tab workbooks in `download/`. It is not a verbatim reconstruction of
all original source modules. The earlier shared register architecture and
`sheets/communication.py` are retained as unused partial source; the active
builder is self-contained and uses `config.py` and the existing CLI.

Build with `python -m pip install XlsxWriter`, then run:

```
python build_daycare_workbook.py -o download/Daycare-Demo.xlsx --today 2026-10-31
python build_daycare_workbook.py -o download/Daycare-Blank.xlsx --blank --today 2026-10-31
```

Run `tools/test_workbook.py` with `openpyxl` and `formulas` installed. XML,
23-sheet order, locked formulas, unlocked inputs, password hash, demo/blank,
ledger effects and sample monthly totals were checked. The principal balance
regression (invoice 100, payment 30 = 70) passes, along with credit, write-off,
refund, deposit and cash-effect tests. A separate CLI smoke test covered blank,
custom centre, no-protect, rows scaling and currency. No Windows Excel instance
was available: open/repair-free compatibility in Windows Excel remains unverified.

This is a smaller independently designed implementation, not a feature-for-feature
reconstruction. See `download/READ ME.txt` for functionality, limits, and the
important safety, financial and privacy caveats. No live staff ratio or pickup
authorization decision is implemented. Tax, fee and payroll settings are
references and do not calculate invoices or payroll automatically.
