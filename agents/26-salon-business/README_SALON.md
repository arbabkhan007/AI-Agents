# Salon Business Management System

A premium 20-tab Excel / Google Sheets product for independent salon
owners, hair stylists, nail technicians, beauty studios, lash artists
and small salon teams: appointments, client CRM, services & pricing,
sales, payments & deposits, staff, commissions, payroll & tips,
expenses, profit & loss, inventory, suppliers & purchases, marketing,
loyalty, goals & budget, analytics, reports and settings.

## Build

    pip install xlsxwriter
    python3 build_salon_workbook.py                     # filled example
    python3 build_salon_workbook.py --blank \
        -o "output/Salon Business Management System (Blank).xlsx"

Useful flags: `--rows N` (scale registers), `--today ISO`,
`--currency SYM`, `--no-protect`, `--password P`, `--author A`.

## Gates

    python3 tools/validate_salon_workbook.py  [workbook.xlsx]
    python3 tools/validate_salon_workbook.py --blank [blank.xlsx]
    python3 tools/check_salon_sample.py [filled] [blank]
    python3 tools/make_download_zip.py --product salon

Every formula is Excel 2010 safe (no XLOOKUP / IFS / LET / dynamic
arrays) and the whole workbook compiles under the strict `formulas`
grammar parser, so Excel opens it without a repair log. Sheets are
protected with the password `premium`; input cells stay unlocked.

## Layout

See `FEATURES_SALON.md` for the 153-point competitive checklist and
what shipped in v1.0.0.
