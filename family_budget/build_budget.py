"""Build the Novality Premium Family Budget workbook."""
import settings, ledger, planner, summary, dashboard
from common import (cell, font, fill, align, INS, USD, PCT, DATE, NUM,
                    title_band, header_row, protect, set_widths,
                    SECTION_FILL, INPUT_FILL, CALC_FILL, TITLE_FILL, HEADER_FILL)

AUTHOR = "Novality Store"
OUTPUT = "Novality_Family_Budget_Premium.xlsx"


def build_instructions(wb):
    s = wb.create_sheet(INS)
    set_widths(s, [30, 26, 26, 26, 26, 26])
    title_band(s, "📖 Instructions & Help",
               "How to use the Novality Premium Family Budget. Green cells are formulas; cream cells are where you type.",
               6)
    rows = [
        ("HOW IT WORKS", "You only enter information ONCE. The Transaction Ledger, Income and Bills tabs feed every else automatically.", None),
        ("", "", None),
        ("1. ⚙️ Settings", "List your Family Members, Accounts, Categories, Income Sources, Pay Frequencies, Goal Types etc. here once. These fill every dropdown.", None),
        ("2. 💳 Transactions", "This is the master ledger. Pick the Type, Category, Subcategory, Account, Family Member from dropdowns. Month / Year / Day are automatic. Enter each expense/income once.", None),
        ("3. 💰 Income", "Enter each paycheck with gross, federal/state/FICA withholding, 401k/HSA. Net take-home is automatic. Date drives Month/Year/Day.", None),
        ("4. 🧾 Bills & Subs", "List recurring bills with due date & frequency. Annual cost is computed. The 📅 Calendar shows what is due each day.", None),
        ("5. 🏦 Accounts", "Enter every account's current balance. Available credit and Month tracking are automatic.", None),
        ("6. 💸 Debt Manager", "Enter balances, APR, min & extra payments. Snowball & avalanche order, payoff date and interest saved are automatic.", None),
        ("7. 🎯 Goals & Funds", "Set a target, current saved and monthly contribution. % complete, per-paycheck amount and projected completion are automatic.", None),
        ("8. 📋 Budget", "Set a monthly limit per subcategory. Actuals pull from the ledger automatically; over-budget turns red.", None),
        ("", "", None),
        ("ONLY EDIT THE CREAM CELLS", "Formula cells (green) are locked and protected. To change formulas or add more rows: Review → Unprotect Sheet → password: premium.", None),
        ("🧪 Sample data", "Sample data is pre-loaded so you can see everything working. Delete it and add your own, or keep adding rows in the cream areas.", None),
        ("📊 Analytics & 🏠 Dashboard", "All charts and KPI cards read the ledgers automatically. No manual totals needed.", None),
        ("🇺🇸 Taxes", "The Tax Center is an ESTIMATE only. Update the brackets/standard deduction whenever tax law changes.", None),
        ("🔒 Protection", "Every tab is protected. Password = premium. Unlocked (cream) input cells remain editable.", None),
    ]
    r = 4
    for label, detail, _ in rows:
        if label == "HOW IT WORKS":
            cell(s, r, 1, label, bold=True, size=13, bg=SECTION_FILL, locked=False)
            cell(s, r, 2, detail or "", italic=True, size=9, color="3D4A46", locked=False, border=None)
            r += 1
            continue
        if not label and not detail:
            r += 1
            continue
        cell(s, r, 1, label, bold=True, locked=False)
        cell(s, r, 2, detail or "", locked=False, wrap=True)
        s.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        r += 1
    # protection note card
    cell(s, r + 1, 1, "🔐 Protection settings", bold=True, bg=SECTION_FILL, locked=False)
    cell(s, r + 1, 2, "Password: premium   ·   Select unlocked cells = ON   ·   Filtering/Sorting = ON", locked=False, wrap=True)
    s.merge_cells(start_row=r + 1, start_column=2, end_row=r + 1, end_column=6)
    protect(s, allow_sort=False, allow_filter=False)
    return s


def main():
    from openpyxl import Workbook
    wb = Workbook()
    wb.properties.creator = AUTHOR
    wb.properties.title = "Novality Premium Family Budget"
    wb.properties.subject = "Complete U.S. household financial dashboard"
    wb.properties.description = "Premium family budget Google Sheet / Excel workbook by Novality Store"
    wb.calculation.fullCalcOnLoad = True
    wb.remove(wb.active)

    settings.build_settings(wb)
    ledger.build_income(wb)
    ledger.build_transactions(wb)
    ledger.build_bills(wb)
    ledger.build_accounts(wb)
    planner.build_debt(wb)
    planner.build_goals(wb)
    planner.build_savings(wb)
    planner.build_home(wb)
    planner.build_vehicles(wb)
    summary.build_budget(wb)
    summary.build_family(wb)
    summary.build_healthcare(wb)
    summary.build_tax(wb)
    summary.build_analytics(wb)
    summary.build_calendar(wb)
    dashboard.build_dashboard(wb)
    build_instructions(wb)

    # Reorder tabs: Dashboard first, Instructions last.
    order = [dashboard.DASH, ledger.INC, ledger.TXN, summary.BUD, ledger.BIL, ledger.ACC,
             planner.DBT, planner.GOL, planner.INV, planner.HOM, planner.VEH, summary.FAM,
             summary.HEA, summary.TAX, summary.ANA, summary.CAL, settings.SET, INS]
    sheets = wb._sheets
    by = {ws.title: ws for ws in sheets}
    wb._sheets = [by[t] for t in order if t in by]
    wb.active = 0
    wb.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
