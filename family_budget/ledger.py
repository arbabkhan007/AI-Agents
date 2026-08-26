"""Income, Transactions, Bills & Accounts ledger tabs."""
import datetime as dt
from openpyxl.styles import PatternFill
from common import (cell, font, fill, align, q, T, TXN, INC, BIL, ACC,
                    USD, USD0, PCT, PCT0, DATE, NUM, PASSWORD, LISTS,
                    title_band, header_row, protect, set_widths, add_dv, money_col,
                    TITLE_FILL, HEADER_FILL, HEADER_FILL2, SECTION_FILL, INPUT_FILL,
                    CALC_FILL, TOTAL_FILL, ALT_FILL, BOX, FAMILY, PAY_FREQ, ACCOUNT_TYPES,
                    PAY_METHODS, TX_TYPES, BILL_FREQ, YES_NO, ESS_DISC, MONTHS,
                    INCOME_SOURCES, CATEGORIES, SUBCATEGORIES)

# data row counts
TXN_LAST = 403
INC_LAST = 203
BIL_LAST = 303
ACC_LAST = 103


# ---------------------------------------------------------------------------
# TRANSACTIONS
# ---------------------------------------------------------------------------
def build_transactions(wb):
    s = wb.create_sheet(TXN)
    set_widths(s, [11, 10, 16, 20, 22, 11, 15, 12, 11, 10, 14, 28, 11, 11, 7, 7, 7])
    title_band(s, "💳 Transaction Ledger", "Your single source of truth. Enter each transaction once — the Dashboard, Budget and Analytics read from here. Cream cells are input.",
               17)
    hdr = ["Date", "Type", "Category", "Subcategory", "Merchant", "Amount",
           "Account", "Payment Method", "Family Member", "Recurring?",
           "Ess/Discretionary", "Notes", "Tax Deductible?", "Reimbursable?", "Month", "Year", "Day"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"

    # data rows + formulas
    for r in range(4, TXN_LAST + 1):
        cell(s, r, 1, None, bg=INPUT_FILL, numfmt=DATE, locked=False)
        for c in range(2, 15):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 12))
        cell(s, r, 3, None, bg=INPUT_FILL, locked=False)
        # Month / Year / Day formulas
        cell(s, r, 15, f'=IF(A{r}="","",MONTH(A{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 16, f'=IF(A{r}="","",YEAR(A{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 17, f'=IF(A{r}="","",DAY(A{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
    money_col(s, "F", 4, TXN_LAST)

    # validation
    add_dv(s, "list", f"=L_Transaction_Types", f"B4:B{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Categories", f"C4:C{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Subcategories", f"D4:D{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Account_Types", f"G4:G{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Payment_Methods", f"H4:H{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Family_Members", f"I4:I{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", "L_Yes_No", f"J4:J{TXN_LAST},M4:M{TXN_LAST},N4:N{TXN_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Essential_Discretionary", f"K4:K{TXN_LAST}", allow_blank=True)

    s.auto_filter.ref = f"A3:Q{TXN_LAST}"
    add_cf(s)
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_transactions(s)
    return s


def add_cf(s):
    from openpyxl.formatting.rule import CellIsRule, FormulaRule, ColorScaleRule, DataBarRule
    rng = f"F4:F{TXN_LAST}"
    s.conditional_formatting.add(rng, DataBarRule(start_type="num", start_value=0,
                                                  end_type="max", color="1F7A5C"))
    # color the type cell by value
    s.conditional_formatting.add(f"B4:B{TXN_LAST}",
                                 CellIsRule(operator="equal", formula=['"Expense"'],
                                            fill=PatternFill("solid", fgColor="F4CCCC"),
                                            font=font(color="9C0006")))
    s.conditional_formatting.add(f"B4:B{TXN_LAST}",
                                 CellIsRule(operator="equal", formula=['"Income"'],
                                            fill=PatternFill("solid", fgColor="D9EAD3"),
                                            font=font(color="006100")))


def add_sample_transactions(s):
    random = __import__("random"); random.seed(7)
    today = dt.date.today()
    y, m = today.year, today.month
    # months to cover: current + previous 4, plus some of previous year
    months = []
    for back in range(6):
        yy, mm = y, m - back
        while mm <= 0:
            mm += 12; yy -= 1
        months.append((yy, mm))
    # use only months of the current year for YTD coherence
    months = [x for x in months if x[0] == y or (x[0] == y - 1 and x[1] >= 12)]
    if y == today.year and (today.month - 5) <= 0:
        months = [(y, mm) for mm in range(1, m + 1)]

    merchants = {
        "Housing": [("Mortgage/Rent", "Home Mortgage"), ("Utilities", "Utility Co"),
                    ("Utilities", "Water & Sewer"), ("Utilities", "Electric Co"),
                    ("Home Insurance", "HomeSure Insurance"), ("Repairs/Maintenance", "Handyman")],
        "Transportation": [("Gas", "Shell"), ("Auto Insurance", "GEICO"),
                           ("Maintenance/Repairs", "Auto Shop"), ("Car Payments", "Auto Finance"),
                           ("Parking/Tolls", "City Parking")],
        "Food": [("Groceries", "Kroger"), ("Groceries", "Walmart"), ("Groceries", "Costco"),
                 ("Restaurants", "Olive Garden"), ("Takeout/Delivery", "DoorDash"),
                 ("Coffee", "Starbucks"), ("Restaurants", "Local Diner")],
        "Family": [("Childcare", "Bright Horizons"), ("School", "School District"),
                   ("Activities/Sports", "Soccer League"), ("Clothing", "Target"),
                   ("Allowances", "Kids Allowance"), ("Baby Expenses", "Buy Buy Baby")],
        "Healthcare": [("Health Insurance", "BCBS"), ("Prescriptions", "CVS Pharmacy"),
                       ("Medical Expenses", "Dr. Office"), ("Dental", "Dental Care")],
        "Lifestyle": [("Entertainment", "AMC"), ("Subscriptions", "Netflix"),
                      ("Subscriptions", "Spotify"), ("Subscriptions", "Amazon Prime"),
                      ("Hobbies", "Hobby Shop"), ("Personal Care", "Ulta"), ("Shopping", "Amazon")],
        "Financial": [("Credit Cards", "Capital One"), ("Student Loans", "Navient"),
                      ("Savings", "Transfer to Savings"), ("Investments", "Vanguard"),
                      ("Retirement", "401(k) Contribution")],
        "Giving": [("Charity", "Red Cross"), ("Gifts", "Amazon Gift")],
        "Pets": [("Food", "PetSmart"), ("Vet", "Banfield")],
        "Miscellaneous": [("Fees", "Bank Fee")],
    }
    amounts = {"Mortgage/Rent": 1850, "Utilities": 190, "Water & Sewer": 55, "Electric Co": 145,
               "Home Insurance": 120, "Repairs/Maintenance": 90, "Gas": 58, "Auto Insurance": 130,
               "Maintenance/Repairs": 120, "Car Payments": 420, "Parking/Tolls": 45,
               "Groceries": 210, "Walmart": 95, "Costco": 180, "Restaurants": 62,
               "Takeout/Delivery": 38, "Coffee": 7, "Local Diner": 48,
               "Childcare": 950, "School District": 60, "Soccer League": 85, "Target": 55,
               "Kids Allowance": 20, "Buy Buy Baby": 45, "Health Insurance": 420,
               "CVS Pharmacy": 22, "Dr. Office": 40, "Dental Care": 30,
               "AMC": 32, "Netflix": 15.5, "Spotify": 11, "Amazon Prime": 14.5,
               "Hobby Shop": 25, "Ulta": 40, "Amazon": 63, "Capital One": 210,
               "Navient": 220, "Transfer to Savings": 400, "Vanguard": 300,
               "401(k) Contribution": 500, "Red Cross": 30, "Amazon Gift": 45,
               "PetSmart": 60, "Banfield": 55, "Bank Fee": 12, "Handyman": 150}
    accounts = ["Checking", "Savings", "Credit Card", "HYSA"]
    paymed = {"Checking": "Checking", "Savings": "Savings", "Credit Card": "Credit Card",
              "HYSA": "Cash"}
    members = ["Parent 1", "Parent 2", "Household"]
    ess = {"Groceries": "Essential", "Walmart": "Essential", "Costco": "Essential",
           "Utilities": "Essential", "Water & Sewer": "Essential", "Electric Co": "Essential",
           "Gas": "Essential", "Auto Insurance": "Essential", "Childcare": "Essential",
           "School District": "Essential", "Health Insurance": "Essential",
           "CVS Pharmacy": "Essential", "Dr. Office": "Essential", "Dental Care": "Essential",
           "Mortgage/Rent": "Essential", "Home Insurance": "Essential",
           "Car Payments": "Essential", "Maintenance/Repairs": "Essential",
           "Transfer to Savings": "Essential", "401(k) Contribution": "Essential"}
    recurring = {"Mortgage/Rent": "Yes", "Home Insurance": "Yes", "Car Payments": "Yes",
                 "Auto Insurance": "Yes", "Childcare": "Yes", "Health Insurance": "Yes",
                 "Netflix": "Yes", "Spotify": "Yes", "Amazon Prime": "Yes",
                 "Student Loans": "Yes", "Navient": "Yes", "Transfer to Savings": "Yes",
                 "Vanguard": "Yes", "401(k) Contribution": "Yes", "Utilities": "Yes"}

    rows = []
    # Build ~9 transactions per month for the covered months
    for (yy, mm) in months:
        day_count = (dt.date(yy, mm + 1, 1) - dt.date(yy, mm, 1)).days if mm < 12 else 31
        ndays = (dt.date(yy, mm + 1, 1) - dt.date(yy, mm, 1)).days
        for cat, sublist in merchants.items():
            for sub, merch in sublist:
                # occasionally skip to vary monthly totals
                if random.random() < 0.18:
                    continue
                max_day = min(ndays, 27)
                d = random.randint(3, max_day)
                amt = amounts.get(merch, round(random.uniform(20, 150), 2))
                amt = round(amt * random.uniform(0.85, 1.1), 2)
                date_obj = dt.date(yy, mm, d)
                acc = random.choice(accounts)
                rows.append((date_obj, "Expense", cat, sub, merch, amt, acc,
                             paymed[acc], random.choice(members),
                             recurring.get(merch, "No"), ess.get(merch, "Discretionary"),
                             "", "No", "No"))
    rows.sort(key=lambda x: x[0])
    # write into sheet
    r = 4
    for row in rows:
        if r > TXN_LAST:
            break
        cell(s, r, 1, row[0], bg=INPUT_FILL, numfmt=DATE, locked=False)
        for i, val in enumerate(row[1:], start=2):
            cell(s, r, i, val, bg=INPUT_FILL, locked=False, wrap=(i == 12))
        r += 1


# ---------------------------------------------------------------------------
# INCOME
# ---------------------------------------------------------------------------
def build_income(wb):
    s = wb.create_sheet(INC)
    set_widths(s, [13, 18, 13, 11, 11, 11, 11, 11, 11, 12, 11, 13, 12, 24, 7, 7, 7])
    title_band(s, "💰 Income Tracker", "List every paycheck & income stream. Net take-home is auto-computed from gross minus deductions.",
               17)
    hdr = ["Earner", "Source", "Pay Frequency", "Pay Date", "Gross", "Federal Tax",
           "State/Local Tax", "Social Security Tax", "Medicare Tax", "401(k)/403(b)",
           "HSA/FSA", "Other Deductions", "Net Take-Home", "Remarks", "Month", "Year", "Day"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    for r in range(4, INC_LAST + 1):
        for c in range(1, 15):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 14))
        for c in (5, 6, 7, 8, 9, 10, 11, 12):
            cell(s, r, c, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 13, f'=IF(E{r}="","",E{r}-SUM(F{r}:L{r}))', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 15, f'=IF(D{r}="","",MONTH(D{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 16, f'=IF(D{r}="","",YEAR(D{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 17, f'=IF(D{r}="","",DAY(D{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
    add_dv(s, "list", f"=L_Family_Members", f"A4:A{INC_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Income_Sources", f"B4:B{INC_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Pay_Frequencies", f"C4:C{INC_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A3:Q{INC_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_income(s)
    return s


def add_sample_income(s):
    today = dt.date.today()
    y, m = today.year, today.month
    months = [(y, mm) for mm in range(1, m + 1)]
    rows = []
    freq = {"Weekly": 1, "Biweekly": 2, "Twice Monthly": 2, "Monthly": 1}
    for (yy, mm) in months:
        # Parent 1: biweekly salary, 2 paychecks
        for pay in (5, 19):
            rows.append((yy, mm, pay, "Parent 1", "Salary", "Biweekly", 2600, 210, 95, 161, 38, 260, 0, 60))
        # Parent 2: twice monthly
        for pay in (8, 23):
            rows.append((yy, mm, pay, "Parent 2", "Salary", "Twice Monthly", 1720, 140, 62, 107, 25, 170, 0, 40))
        # side income
        if mm in (m, m - 1):
            rows.append((yy, mm, 20, "Parent 1", "Freelance/Side Hustle", "Irregular", 650, 0, 0, 0, 0, 0, 0, 0))
    for (yy, mm, d, earner, src, fr, gross, fed, state, ss, medic, k, hsa, oth) in rows:
        date_obj = dt.date(yy, mm, d)
        if date_obj > dt.date.today():
            continue
        r = 4
        while s.cell(row=r, column=1).value is not None and r < INC_LAST:
            r += 1
        cell(s, r, 1, earner, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, src, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, fr, bg=INPUT_FILL, locked=False)
        cell(s, r, 4, date_obj, bg=INPUT_FILL, numfmt=DATE, locked=False)
        for i, v in enumerate([gross, fed, state, ss, medic, k, hsa, oth], start=5):
            cell(s, r, i, v, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 14, "", bg=INPUT_FILL, locked=False)


# ---------------------------------------------------------------------------
# BILLS & SUBSCRIPTIONS
# ---------------------------------------------------------------------------
def build_bills(wb):
    s = wb.create_sheet(BIL)
    set_widths(s, [24, 11, 11, 14, 16, 15, 10, 8, 26, 12, 7, 7, 7])
    title_band(s, "🧾 Bills & Subscriptions Calendar", "Track every recurring payment. Annual cost & next month computation are automatic.",
               13)
    hdr = ["Bill Name", "Amount", "Due Date", "Frequency", "Category", "Account Charged",
           "Autopay?", "Paid?", "Notes", "Annual Cost", "Month", "Year", "Day"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    for r in range(4, BIL_LAST + 1):
        for c in range(1, 10):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 9))
        cell(s, r, 2, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 3, None, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 10, f'=IF(C{r}="","",IF(D{r}="Monthly",B{r}*12,IF(D{r}="Weekly",B{r}*52,IF(D{r}="Biweekly",B{r}*26,IF(D{r}="Twice Monthly",B{r}*24,IF(D{r}="Quarterly",B{r}*4,IF(D{r}="Annually",B{r},IF(D{r}="One-time",B{r},""))))))))',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 11, f'=IF(C{r}="","",MONTH(C{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 12, f'=IF(C{r}="","",YEAR(C{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 13, f'=IF(C{r}="","",DAY(C{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
    add_dv(s, "list", f"=L_Bill_Frequencies", f"D4:D{BIL_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Categories", f"E4:E{BIL_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Account_Types", f"F4:F{BIL_LAST}", allow_blank=True)
    add_dv(s, "list", "L_Yes_No", f"G4:G{BIL_LAST},H4:H{BIL_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A3:M{BIL_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_bills(s)
    return s


def add_sample_bills(s):
    today = dt.date.today()
    y, m = today.year, today.month
    bills = [("Home Mortgage", 1850, 1, "Monthly", "Housing", "Checking", "Yes", "Yes"),
             ("Electric", 145, 8, "Monthly", "Housing", "Checking", "Autopay", "Yes"),
             ("Internet", 60, 12, "Monthly", "Housing", "Credit Card", "Autopay", "Yes"),
             ("Water & Sewer", 55, 15, "Monthly", "Housing", "Checking", "Autopay", "Yes"),
             ("Home Insurance", 120, 20, "Monthly", "Housing", "Checking", "Autopay", "Yes"),
             ("Auto Insurance", 130, 22, "Monthly", "Transportation", "Credit Card", "Autopay", "Yes"),
             ("Cell Phone", 90, 25, "Monthly", "Lifestyle", "Credit Card", "Autopay", "Yes"),
             ("Netflix", 15.5, 5, "Monthly", "Lifestyle", "Credit Card", "Autopay", "Yes"),
             ("Spotify", 11, 6, "Monthly", "Lifestyle", "Credit Card", "Autopay", "Yes"),
             ("Amazon Prime", 14.5, 7, "Annually", "Lifestyle", "Credit Card", "Autopay", "Yes"),
             ("Gym Membership", 45, 3, "Monthly", "Lifestyle", "Credit Card", "Autopay", "No"),
             ("Student Loan", 220, 18, "Monthly", "Financial", "Checking", "Autopay", "Yes"),
             ("Property Tax", 250, 30, "Annually", "Housing", "Checking", "No", "No"),
             ("Life Insurance", 55, 10, "Monthly", "Healthcare", "Checking", "Autopay", "Yes")]
    r = 4
    for name, amt, dd, freq, cat, acc, auto, paid in bills:
        if r > BIL_LAST:
            break
        due = dt.date(y, m, min(dd, 28))
        if auto == "Autopay":
            auto = "Yes"
        cell(s, r, 1, name, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, amt, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 3, due, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 4, freq, bg=INPUT_FILL, locked=False)
        cell(s, r, 5, cat, bg=INPUT_FILL, locked=False)
        cell(s, r, 6, acc, bg=INPUT_FILL, locked=False)
        cell(s, r, 7, auto, bg=INPUT_FILL, locked=False)
        cell(s, r, 8, paid, bg=INPUT_FILL, locked=False)
        cell(s, r, 9, "", bg=INPUT_FILL, locked=False)
        r += 1


# ---------------------------------------------------------------------------
# ACCOUNTS
# ---------------------------------------------------------------------------
def build_accounts(wb):
    s = wb.create_sheet(ACC)
    set_widths(s, [24, 16, 13, 14, 12, 14, 12, 12, 7, 7, 24])
    title_band(s, "🏦 Account Tracker", "Every household account with current balance, limits and rates. Available credit is auto-computed.",
               11)
    hdr = ["Account Name", "Account Type", "Owner", "Current Balance", "Credit Limit",
           "Available Credit", "Rate / APY", "Last Updated", "Month", "Year", "Notes"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    for r in range(4, ACC_LAST + 1):
        for c in range(1, 12):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 11))
        cell(s, r, 4, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 5, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, f'=IF(E{r}="","",IF(E{r}=0,"",E{r}-ABS(D{r})))', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 7, None, bg=INPUT_FILL, numfmt=PCT, locked=False)
        cell(s, r, 8, None, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 9, f'=IF(H{r}="","",MONTH(H{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 10, f'=IF(H{r}="","",YEAR(H{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
    add_dv(s, "list", f"=L_Account_Types", f"B4:B{ACC_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Family_Members", f"C4:C{ACC_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A3:K{ACC_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_accounts(s)
    return s


def add_sample_accounts(s):
    today = dt.date.today()
    y, m = today.year, today.month
    accts = [("Chase Checking", "Checking", "Parent 1", 9200, 0, 0, 10, "Checking"),
             ("Wells Fargo Checking", "Checking", "Parent 2", 4300, 0, 0, 10, "Checking"),
             ("Ally Savings", "Savings", "Household", 14500, 0, 0.042, 20, "Savings"),
             ("Ally HYSA", "HYSA", "Household", 28000, 0, 0.047, 21, "Savings"),
             ("Cash", "Cash", "Household", 450, 0, 0, 26, "Cash"),
             ("Capital One Credit", "Credit Card", "Parent 1", 2100, 12000, 0.2499, 15, "Credit Card"),
             ("Visa Credit", "Credit Card", "Parent 2", 830, 6000, 0.2299, 18, "Credit Card"),
             ("401(k) - Fidelity", "401(k)", "Parent 1", 128000, 0, 0.07, 28, "Retirement"),
             ("403(b) - TIAA", "403(b)", "Parent 2", 76000, 0, 0.065, 28, "Retirement"),
             ("Roth IRA", "Roth IRA", "Parent 1", 24000, 0, 0.06, 28, "Retirement"),
             ("Brokerage - Vanguard", "Brokerage", "Parent 1", 54000, 0, 0.0, 28, "Investment"),
             ("529 - College", "529", "Child 1", 21000, 0, 0.05, 28, "Education"),
             ("HSA - Fidelity", "HSA", "Parent 1", 9800, 0, 0.03, 28, "Retirement"),
             ("CD - 12 mo", "CD", "Household", 10000, 0, 0.048, 28, "Savings")]
    r = 4
    for name, atype, owner, bal, lim, rate, dd, note in accts:
        if r > ACC_LAST:
            break
        last = dt.date(y, m, min(dd, 28))
        cell(s, r, 1, name, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, atype, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, owner, bg=INPUT_FILL, locked=False)
        cell(s, r, 4, bal, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 5, lim if lim else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 7, rate if rate else None, bg=INPUT_FILL, numfmt=PCT, locked=False)
        cell(s, r, 8, last, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 11, note, bg=INPUT_FILL, locked=False)
        r += 1
