"""Debt Manager, Goals & Sinking Funds, Savings & Investments, Home & Mortgage, Vehicles."""
from openpyxl.utils import get_column_letter
from common import (cell, font, fill, align, q, T, DBT, GOL, INV, HOM, VEH, ACC,
                    USD, USD0, PCT, PCT0, DATE, NUM, PASSWORD, LISTS,
                    title_band, header_row, protect, set_widths, add_dv, money_col,
                    TITLE_FILL, HEADER_FILL, HEADER_FILL2, SECTION_FILL, INPUT_FILL,
                    CALC_FILL, TOTAL_FILL, ALT_FILL, BOX, FAMILY, DEBT_TYPES, GOAL_TYPES,
                    INVEST_TYPES, ACCOUNT_TYPES, YES_NO)

DBT_FIRST, DBT_LAST = 8, 107
GOL_LAST = 103
INV_FIRST, INV_LAST = 5, 20
VEH_LAST = 33


# ---------------------------------------------------------------------------
# DEBT MANAGER
# ---------------------------------------------------------------------------
def build_debt(wb):
    s = wb.create_sheet(DBT)
    set_widths(s, [22, 20, 14, 13, 13, 11, 13, 13, 11, 7, 7, 7, 12, 12, 14, 22, 10, 10])
    title_band(s, "💸 Debt Payoff Planner", "Snowball & avalanche strategies built in. Interest saved and debt-free date are auto-estimated.",
               18)

    # Summary block
    cell(s, 4, 1, "DEBT SUMMARY", bold=True, bg=SECTION_FILL, locked=False)
    cell(s, 5, 1, "Total Debt", bold=True, locked=False)
    cell(s, 5, 2, f"=SUM(D{DBT_FIRST}:D{DBT_LAST})", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 1, "Total Minimum Payment", bold=True, locked=False)
    cell(s, 6, 2, f"=SUM(G{DBT_FIRST}:G{DBT_LAST})", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 7, 1, "Total Extra Payment", bold=True, locked=False)
    cell(s, 7, 2, f"=SUM(H{DBT_FIRST}:H{DBT_LAST})", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 8, 1, "Est. Interest Remaining", bold=True, locked=False)
    cell(s, 8, 2, f"=SUM(O{DBT_FIRST}:O{DBT_LAST})", bg=CALC_FILL, numfmt=USD, locked=True)

    hdr = ["Debt Name", "Account / Creditor", "Debt Type", "Current Balance", "Original Balance",
           "APR", "Minimum Payment", "Extra Payment", "Due Date", "Month", "Year", "Day",
           "Payoff Date", "Months to Payoff", "Est. Interest Remaining", "Notes",
           "Snowball Order", "Avalanche Order"]
    header_row(s, 10, hdr)
    s.freeze_panes = "A11"

    for r in range(DBT_FIRST, DBT_LAST + 1):
        for c in range(1, 10):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 16))
        for c in (4, 5, 7, 8):
            cell(s, r, c, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, None, bg=INPUT_FILL, numfmt=PCT, locked=False)
        cell(s, r, 9, None, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 10, f'=IF(I{r}="","",MONTH(I{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 11, f'=IF(I{r}="","",YEAR(I{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 12, f'=IF(I{r}="","",DAY(I{r}))', bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 14, f'=IF(D{r}="","",IFERROR(NPER(F{r}/12,-(G{r}+H{r}),D{r}),""))',
             bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 13, f'=IF(N{r}="","",EDATE(TODAY(),ROUNDUP(N{r},0)))', bg=CALC_FILL, numfmt=DATE, locked=True)
        cell(s, r, 15, f'=IF(N{r}="","",(G{r}+H{r})*N{r}-D{r})', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 17, f'=IF(D{r}="","",RANK(D{r},$D${DBT_FIRST}:$D${DBT_LAST},1))',
             bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 18, f'=IF(F{r}="","",RANK(F{r},$F${DBT_FIRST}:$F${DBT_LAST},0))',
             bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")

    add_dv(s, "list", f"=L_Debt_Types", f"C{DBT_FIRST}:C{DBT_LAST}", allow_blank=True)
    add_dv(s, "list", f"=L_Account_Types", f"B{DBT_FIRST}:B{DBT_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A10:R{DBT_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_debt(s)
    return s


def add_sample_debt(s):
    date = __import__("datetime").date
    today = date.today()
    y, m = today.year, today.month
    debts = [("Visa Credit", "Capital One", "Credit Card", 2100, 2500, 0.2499, 63, 150, 15),
             ("Mastercard", "Bank of America", "Credit Card", 830, 2000, 0.2299, 28, 50, 18),
             ("Student Loan", "Navient", "Student Loan", 14500, 25000, 0.045, 220, 100, 5),
             ("Auto Loan", "Toyota Finance", "Auto Loan", 14800, 26000, 0.055, 420, 100, 12),
             ("Personal Loan", "SoFi", "Personal Loan", 5800, 8000, 0.089, 145, 50, 10)]
    r = DBT_FIRST
    for name, acct, dtype, bal, orig, apr, minp, extra, dd in debts:
        if r > DBT_LAST:
            break
        due = date(y, m, min(dd, 28))
        cell(s, r, 1, name, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, acct, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, dtype, bg=INPUT_FILL, locked=False)
        cell(s, r, 4, bal, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 5, orig, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, apr, bg=INPUT_FILL, numfmt=PCT, locked=False)
        cell(s, r, 7, minp, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 8, extra, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 9, due, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 16, "", bg=INPUT_FILL, locked=False)
        r += 1


# ---------------------------------------------------------------------------
# GOALS & SINKING FUNDS
# ---------------------------------------------------------------------------
def build_goals(wb):
    s = wb.create_sheet(GOL)
    set_widths(s, [24, 18, 13, 13, 14, 12, 13, 12, 15, 13, 24])
    title_band(s, "🎯 Financial Goals & Sinking Funds", "Unlimited goals with auto % complete, per-paycheck amount and projected completion date.",
               11)
    hdr = ["Goal Name", "Goal Type", "Target", "Current Saved", "Monthly Contribution",
           "Deadline", "Per Paycheck", "% Complete", "Monthly Needed", "Projected Completion", "Notes"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    for r in range(4, GOL_LAST + 1):
        for c in range(1, 12):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False, wrap=(c == 11))
        for c in (3, 4, 5):
            cell(s, r, c, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, None, bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 7, f'=IF(E{r}="","",E{r}/2)', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 8, f'=IF(C{r}="","",IF(C{r}=0,"",D{r}/C{r}))', bg=CALC_FILL, numfmt=PCT, locked=True)
        cell(s, r, 9, f'=IF(OR(C{r}="",F{r}=""),"",IF(D{r}>=C{r},0,IFERROR((C{r}-D{r})/MAX(1,DATEDIF(TODAY(),F{r},"m")),"")))',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 10, f'=IF(E{r}="","",IF(D{r}>=C{r},"Done",IFERROR(EDATE(TODAY(),(C{r}-D{r})/E{r}),"")))',
             bg=CALC_FILL, numfmt=DATE, locked=True)
    add_dv(s, "list", f"=L_Goal_Types", f"B4:B{GOL_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A3:K{GOL_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_goals(s)
    return s


def add_sample_goals(s):
    today = __import__("datetime").date.today()
    y, m = today.year, today.month
    goals = [("Emergency Fund", "Emergency Fund", 60000, 42500, 500, "401k"),
             ("Christmas 2026", "Christmas", 2500, 900, 150, "401k"),
             ("Family Vacation", "Vacation", 8000, 2200, 400, "401k"),
             ("New Car Fund", "Major Purchase", 20000, 5000, 500, "401k"),
             ("Home Renovation", "Home Repairs", 15000, 3000, 300, "401k"),
             ("College - Child 1", "College", 50000, 21000, 300, "401k")]
    r = 4
    for name, gtype, target, cur, monthly, ddl in goals:
        if r > GOL_LAST:
            break
        cell(s, r, 1, name, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, gtype, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, target, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 4, cur, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 5, monthly, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, __import__("datetime").date(y, 12, 31), bg=INPUT_FILL, numfmt=DATE, locked=False)
        cell(s, r, 11, "", bg=INPUT_FILL, locked=False)
        r += 1


# ---------------------------------------------------------------------------
# SAVINGS & INVESTMENTS
# ---------------------------------------------------------------------------
INVEST_MAP = {
    "Emergency Fund": ["HYSA", "Savings"], "401(k)": ["401(k)"], "403(b)": ["403(b)"],
    "IRA": ["IRA"], "Roth IRA": ["Roth IRA"], "Brokerage": ["Brokerage"], "HSA": ["HSA"],
    "529": ["529"], "CD": ["CD"], "HYSA": ["HYSA"], "Savings": ["Savings"],
    "Cash": ["Cash"], "Checking": ["Checking"],
}


def balance_formula(types):
    acc = q(ACC)
    parts = [f'SUMIF({acc}!$B$4:$B$103,"{t}",{acc}!$D$4:$D$103)' for t in types]
    return "=" + "+".join(parts)


def build_savings(wb):
    s = wb.create_sheet(INV)
    set_widths(s, [18, 15, 15, 14, 15, 15, 14, 15, 12, 24])
    title_band(s, "📈 Savings & Investments", "Current balances pull automatically from the Account Tracker. Track contributions, employer match and goal progress.",
               10)
    hdr = ["Investment Type", "Current Balance", "Monthly Contribution", "YTD Contributions",
           "Employer Match %", "Employer Match $", "Annual Max", "Goal", "Progress", "Notes"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    row = INV_FIRST
    for inv in INVEST_TYPES:
        if inv in INVEST_MAP:
            bal = balance_formula(INVEST_MAP[inv])
        else:
            bal = ""
        cell(s, row, 1, inv, bg=INPUT_FILL, locked=False)
        cell(s, row, 2, bal, bg=CALC_FILL, numfmt=USD, locked=True)
        for c in (3, 4, 8):
            cell(s, row, c, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, row, 5, None, bg=INPUT_FILL, numfmt=PCT, locked=False)
        cell(s, row, 6, f'=IF(AND(C{row}="",E{row}=""),"",IFERROR(C{row}*E{row},0))', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, row, 7, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, row, 9, f'=IF(OR(B{row}="",H{row}=""),"",IF(H{row}=0,"",B{row}/H{row}))', bg=CALC_FILL, numfmt=PCT, locked=True)
        cell(s, row, 10, None, bg=INPUT_FILL, locked=False)
        row += 1
    # totals
    trow = row + 1
    cell(s, trow, 1, "TOTAL", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, trow, 2, f"=SUM(B{INV_FIRST}:B{row-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, trow, 3, f"=SUM(C{INV_FIRST}:C{row-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, trow, 6, f"=SUM(F{INV_FIRST}:F{row-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# HOME & MORTGAGE
# ---------------------------------------------------------------------------
def build_home(wb):
    s = wb.create_sheet(HOM)
    set_widths(s, [30, 16, 14, 14, 14])
    title_band(s, "🏡 Home & Mortgage", "Home equity, total monthly cost and a full mortgage amortization schedule — all auto-calculated.",
               5)
    inputs = [
        ("Home Value", "B5", None, None),
        ("Annual Property Tax", "B6", None, "B5"),
        ("Monthly HOA", "B7", None, "B5"),
        ("Annual Home Insurance", "B8", None, "B5"),
        ("Monthly Maintenance (avg)", "B9", None, "B5"),
        ("Mortgage Balance", "B10", None, "B5"),
        ("Interest Rate (APR)", "B11", PCT, "B5"),
        ("Loan Term (years)", "B12", NUM, "B5"),
    ]
    cell(s, 4, 1, "HOME / MORTGAGE INPUTS", bold=True, bg=SECTION_FILL, locked=False)
    r = 5
    for lab, _ref, fmt, _guard in inputs:
        cell(s, r, 1, lab, bold=True, locked=False)
        cell(s, r, 2, None, bg=INPUT_FILL, numfmt=fmt, locked=False)
        r += 1
    # sample values (replace with your own)
    sample = [420000, 5000, 90, 1400, 150, 285000, 0.055, 30]
    for i, v in enumerate(sample):
        cell(s, 5 + i, 2, v, bg=INPUT_FILL, numfmt=inputs[i][2], locked=False)
    # results
    cell(s, 13, 1, "Monthly P&I Payment", bold=True, locked=False)
    cell(s, 13, 2, "=IFERROR(-PMT(B11/12,B12*12,B10),0)", bg=CALC_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, 14, 1, "Monthly Escrow (Tax+Ins+HOA)", bold=True, locked=False)
    cell(s, 14, 2, "=IFERROR(B6/12+B8/12+B7,0)", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 15, 1, "Total Monthly Housing Cost", bold=True, locked=False)
    cell(s, 15, 2, "=B13+B14+B9", bg=CALC_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, 16, 1, "Annual Carrying Cost", bold=True, locked=False)
    cell(s, 16, 2, "=B15*12", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 17, 1, "Home Equity", bold=True, locked=False)
    cell(s, 17, 2, "=B5-B10", bg=CALC_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, 18, 1, "Loan % Paid", bold=True, locked=False)
    cell(s, 18, 2, '=IF(OR(B10="",B5=""),"",1-B10/B5)', bg=CALC_FILL, numfmt=PCT, locked=True)
    cell(s, 19, 1, "Months Remaining", bold=True, locked=False)
    cell(s, 19, 2, "=IFERROR(NPER(B11/12,-B13,B10),\"\")", bg=CALC_FILL, numfmt=NUM, locked=True)
    cell(s, 20, 1, "Projected Payoff Date", bold=True, locked=False)
    cell(s, 20, 2, '=IFERROR(EDATE(TODAY(),ROUNDUP(B19,0)),"")', bg=CALC_FILL, numfmt=DATE, locked=True)

    # amortization table
    ah = 22
    s.merge_cells(start_row=ah, start_column=1, end_row=ah, end_column=5)
    c = cell(s, ah, 1, "MORTGAGE AMORTIZATION SCHEDULE", bold=True, bg=SECTION_FILL, locked=False)
    c.alignment = align(horizontal="center")
    header_row(s, ah + 1, ["Payment #", "Payment", "Interest", "Principal", "Balance"])
    s.freeze_panes = "A24"
    # starting balance row (label + balance)
    sb = ah + 2
    cell(s, sb, 1, "Start", bold=True, bg=TOTAL_FILL, locked=False, horizontal="center")
    cell(s, sb, 5, "=$B$10", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    start = sb + 1
    for i in range(360):
        r = start + i
        prev = r - 1
        bg = ALT_FILL if i % 2 else None
        cell(s, r, 1, i + 1, bg=bg, numfmt=NUM, locked=True, horizontal="center")
        cell(s, r, 2, f'=IF(E{prev}<=0,"",$B$13)', bg=bg, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 3, f'=IF(E{prev}<=0,"",E{prev}*$B$11/12)', bg=bg, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 4, f'=IF(E{prev}<=0,"",B{r}-C{r})', bg=bg, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 5, f'=IF(E{prev}<=0,"",E{prev}-D{r})', bg=bg, numfmt=USD, locked=True, horizontal="center")
    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# VEHICLES
# ---------------------------------------------------------------------------
def build_vehicles(wb):
    s = wb.create_sheet(VEH)
    set_widths(s, [16, 13, 12, 11, 10, 12, 11, 12, 11, 12, 12, 13, 12, 12, 12])
    title_band(s, "🚗 Vehicle Costs", "Track the true cost of each vehicle — including cost per mile — automatically.",
               15)
    hdr = ["Vehicle", "Owner", "Loan Payment", "Insurance", "Gas", "Maintenance", "Repairs",
           "Registration (ann)", "Tires (ann)", "Parking/Tolls", "Annual Miles", "Current Value",
           "Monthly Total", "Annual Total", "Cost per Mile"]
    header_row(s, 3, hdr)
    s.freeze_panes = "A4"
    for r in range(4, VEH_LAST + 1):
        for c in range(1, 13):
            cell(s, r, c, None, bg=INPUT_FILL, locked=False)
        for c in (3, 4, 5, 6, 7, 8, 9, 10, 12):
            cell(s, r, c, None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 11, None, bg=INPUT_FILL, numfmt=NUM, locked=False)
        cell(s, r, 13, f'=IF(C{r}="","",SUM(C{r}:G{r},J{r})+IF(H{r}="",0,H{r}/12)+IF(I{r}="",0,I{r}/12))',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 14, f'=IF(M{r}="","",M{r}*12)', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 15, f'=IF(OR(K{r}="",K{r}=0),"",N{r}/K{r})', bg=CALC_FILL, numfmt=USD, locked=True)
    add_dv(s, "list", f"=L_Family_Members", f"B4:B{VEH_LAST}", allow_blank=True)
    s.auto_filter.ref = f"A3:O{VEH_LAST}"
    protect(s, allow_sort=True, allow_filter=True)
    add_sample_vehicles(s)
    return s


def add_sample_vehicles(s):
    veh = [("Toyota Camry", "Family", 420, 85, 130, 60, 45, 120, 90, 30, 12000, 13500),
           ("Honda CR-V", "Parent 2", 0, 75, 90, 50, 30, 100, 80, 20, 9000, 21000)]
    r = 4
    for row in veh:
        if r > VEH_LAST:
            break
        cell(s, r, 1, row[0], bg=INPUT_FILL, locked=False)
        for i, v in enumerate(row[1:], start=2):
            if v is None:
                continue
            cell(s, r, i, v, bg=INPUT_FILL, numfmt=USD if i not in (11,) else NUM, locked=False)
        r += 1
