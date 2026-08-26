"""Budget, Family & Kids, Healthcare, Tax, Analytics and Calendar tabs."""
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference
from common import (cell, font, fill, align, q, T, BUD, FAM, HEA, TAX, ANA, CAL,
                    TXN, INC, BIL, DBT, GOL, ACC, USD, USD0, PCT, PCT0, DATE, NUM,
                    PASSWORD, LISTS, title_band, header_row, protect, set_widths,
                    add_dv, money_col, TITLE_FILL, HEADER_FILL, HEADER_FILL2,
                    SECTION_FILL, INPUT_FILL, CALC_FILL, TOTAL_FILL, ALT_FILL,
                    GOOD_FILL, WARN_FILL, BAD_FILL, BOX, BUDGET, CATEGORIES,
                    SUBCATEGORIES, DEFAULT_BUDGET, FAMILY, FILING, MONTHS, YES_NO,
                    ESS_DISC, GOAL_TYPES)

BUDGET_SUBTOTAL = {}   # category -> subtotal row (in Budget tab)

TXN_F, TXN_L = 4, 403
INC_F, INC_L = 4, 203
BIL_F, BIL_L = 4, 303
DBT_F, DBT_L = 8, 107
GOL_F, GOL_L = 4, 103

TXN_AMT = f"{q(TXN)}!$F${TXN_F}:$F${TXN_L}"
TXN_CAT = f"{q(TXN)}!$C${TXN_F}:$C${TXN_L}"
TXN_SUB = f"{q(TXN)}!$D${TXN_F}:$D${TXN_L}"
TXN_TYPE = f"{q(TXN)}!$B${TXN_F}:$B${TXN_L}"
TXN_MON = f"{q(TXN)}!$O${TXN_F}:$O${TXN_L}"
TXN_YR = f"{q(TXN)}!$P${TXN_F}:$P${TXN_L}"
TXN_DAY = f"{q(TXN)}!$Q${TXN_F}:$Q${TXN_L}"
TXN_FAM = f"{q(TXN)}!$I${TXN_F}:$I${TXN_L}"
TXN_ESS = f"{q(TXN)}!$K${TXN_F}:$K${TXN_L}"

INC_NET = f"{q(INC)}!$M${INC_F}:$M${INC_L}"
INC_MON = f"{q(INC)}!$O${INC_F}:$O${INC_L}"
INC_YR = f"{q(INC)}!$P${INC_F}:$P${INC_L}"
INC_DAY = f"{q(INC)}!$Q${INC_F}:$Q${INC_L}"
INC_GROSS = f"{q(INC)}!$E${INC_F}:$E${INC_L}"
INC_FED = f"{q(INC)}!$F${INC_F}:$F${INC_L}"
INC_ST = f"{q(INC)}!$G${INC_F}:$G${INC_L}"
INC_FICA1 = f"{q(INC)}!$H${INC_F}:$H${INC_L}"
INC_FICA2 = f"{q(INC)}!$I${INC_F}:$I${INC_L}"
INC_401 = f"{q(INC)}!$J${INC_F}:$J${INC_L}"
INC_HSA = f"{q(INC)}!$K${INC_F}:$K${INC_L}"

BIL_AMT = f"{q(BIL)}!$B${BIL_F}:$B${BIL_L}"
BIL_CAT = f"{q(BIL)}!$E${BIL_F}:$E${BIL_L}"
BIL_MON = f"{q(BIL)}!$K${BIL_F}:$K${BIL_L}"
BIL_YR = f"{q(BIL)}!$L${BIL_F}:$L${BIL_L}"
BIL_DAY = f"{q(BIL)}!$M${BIL_F}:$M${BIL_L}"

DBT_MIN = f"{q(DBT)}!$G${DBT_F}:$G${DBT_L}"
DBT_MON = f"{q(DBT)}!$J${DBT_F}:$J${DBT_L}"
DBT_YR = f"{q(DBT)}!$K${DBT_F}:$K${DBT_L}"
DBT_DAY = f"{q(DBT)}!$L${DBT_F}:$L${DBT_L}"
DBT_BAL = f"{q(DBT)}!$D${DBT_F}:$D${DBT_L}"
DBT_TYPE = f"{q(DBT)}!$C${DBT_F}:$C${DBT_L}"

ACC_BAL = f"{q(ACC)}!$D$4:$D$103"
ACC_TYPE = f"{q(ACC)}!$B$4:$B$103"

BUDGET_TOTAL_ROW = None

ASSET_TYPES = ('"Checking","Savings","HYSA","Cash","401(k)","403(b)","IRA","Roth IRA",'
               '"Brokerage","529","HSA","FSA","CD","Other Investment"')


# ---------------------------------------------------------------------------
# BUDGET
# ---------------------------------------------------------------------------
def build_budget(wb):
    s = wb.create_sheet(BUD)
    set_widths(s, [18, 22, 14, 14, 14, 13, 11, 26])
    title_band(s, "📋 Complete Family Budget", "Set a monthly limit per subcategory. Actuals pull live from the Transaction Ledger; variance is automatic.",
               8)
    header_row(s, 3, ["Category", "Subcategory", "Monthly Budget", "Actual This Month",
                      "Actual YTD", "Variance (This Month)", "% of Budget", "Notes"])
    s.freeze_panes = "A4"
    r = 4
    subtotal_rows = []
    for cat in CATEGORIES:
        subs = BUDGET[cat]
        sub_start = r
        for sub in subs:
            budget = DEFAULT_BUDGET.get((cat, sub), 0)
            cell(s, r, 1, cat, bg=INPUT_FILL, locked=False)
            cell(s, r, 2, sub, bg=INPUT_FILL, locked=False)
            cell(s, r, 3, budget if budget else None, bg=INPUT_FILL, numfmt=USD, locked=False)
            cell(s, r, 4, f'=SUMIFS({TXN_AMT},{TXN_CAT},A{r},{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)',
                 bg=CALC_FILL, numfmt=USD, locked=True)
            cell(s, r, 5, f'=SUMIFS({TXN_AMT},{TXN_CAT},A{r},{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_YR},C_Year)',
                 bg=CALC_FILL, numfmt=USD, locked=True)
            cell(s, r, 6, f'=IF(C{r}="","",C{r}-D{r})', bg=CALC_FILL, numfmt=USD, locked=True)
            cell(s, r, 7, f'=IF(C{r}="","",IF(C{r}=0,"",D{r}/C{r}))', bg=CALC_FILL, numfmt=PCT, locked=True, horizontal="center")
            cell(s, r, 8, None, bg=INPUT_FILL, locked=False)
            r += 1
        end = r - 1
        cell(s, r, 1, cat, bold=True, bg=TOTAL_FILL, locked=False)
        cell(s, r, 2, "Category Subtotal", bold=True, bg=TOTAL_FILL, locked=False)
        cell(s, r, 3, f"=SUM(C{sub_start}:C{end})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
        cell(s, r, 4, f"=SUM(D{sub_start}:D{end})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
        cell(s, r, 5, f"=SUM(E{sub_start}:E{end})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
        cell(s, r, 6, f"=SUM(F{sub_start}:F{end})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
        cell(s, r, 7, f'=IF(C{r}=0,"",D{r}/C{r})', bg=TOTAL_FILL, numfmt=PCT, locked=True, bold=True, horizontal="center")
        cell(s, r, 8, None, bg=TOTAL_FILL, locked=False)
        subtotal_rows.append(r)
        BUDGET_SUBTOTAL[cat] = r
        r += 1
    tr = r + 1
    global BUDGET_TOTAL_ROW
    BUDGET_TOTAL_ROW = tr
    cell(s, tr, 1, "TOTAL", bold=True, bg=HEADER_FILL2, locked=False, color="FFFFFF")
    cell(s, tr, 2, "Grand Total", bold=True, bg=HEADER_FILL2, locked=False, color="FFFFFF")
    for col in (3, 4, 5, 6):
        L = get_column_letter(col)
        refs = ",".join(f"{L}{rr}" for rr in subtotal_rows)
        cell(s, tr, col, f"=SUM({refs})",
             bg=HEADER_FILL2, numfmt=USD, locked=True, bold=True, color="FFFFFF")
    cell(s, tr, 7, f'=IF(C{tr}=0,"",D{tr}/C{tr})', bg=HEADER_FILL2, numfmt=PCT, locked=True, bold=True, color="FFFFFF", horizontal="center")
    cell(s, tr, 8, None, bg=HEADER_FILL2, locked=False)
    # conditional formatting: over budget red, ok green
    cf = s
    cf.conditional_formatting.add(f"D4:D{tr}", CellIsRule(operator="greaterThan",
        formula=[f"C{4}"], fill=PatternFill("solid", fgColor="FFC7CE"), font=font(color="9C0006")))
    protect(s, allow_sort=True, allow_filter=True)
    return s


from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill


# ---------------------------------------------------------------------------
# FAMILY & KIDS
# ---------------------------------------------------------------------------
def build_family(wb):
    s = wb.create_sheet(FAM)
    set_widths(s, [18, 22, 14, 14, 14, 13, 26])
    title_band(s, "👨‍👩‍👧‍👦 Family & Kids", "Family-related spending at a glance, plus spending broken down by family member.",
               7)
    header_row(s, 3, ["Category", "Subcategory", "Monthly Budget", "Actual This Month",
                      "Actual YTD", "Variance", "Notes"])
    s.freeze_panes = "A4"
    subs = BUDGET["Family"]
    r = 4
    sub_start = r
    for sub in subs:
        budget = DEFAULT_BUDGET.get(("Family", sub), 0)
        cell(s, r, 1, "Family", bg=INPUT_FILL, locked=False)
        cell(s, r, 2, sub, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, budget if budget else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 4, f'=SUMIFS({TXN_AMT},{TXN_CAT},"Family",{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 5, f'=SUMIFS({TXN_AMT},{TXN_CAT},"Family",{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 6, f'=IF(C{r}="","",C{r}-D{r})', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 7, None, bg=INPUT_FILL, locked=False)
        r += 1
    tr = r + 1
    cell(s, tr, 1, "TOTAL", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, tr, 2, "Family Total", bold=True, bg=TOTAL_FILL, locked=False)
    for col, letter in ((3, None),):
        pass
    cell(s, tr, 3, f"=SUM(C{4}:C{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, tr, 4, f"=SUM(D{4}:D{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, tr, 5, f"=SUM(E{4}:E{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)

    # By family member table
    mr = tr + 3
    cell(s, mr, 1, "SPENDING BY FAMILY MEMBER (THIS MONTH)", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, mr + 1, ["Family Member", "This Month", "YTD"])
    r = mr + 2
    for mem in FAMILY:
        cell(s, r, 1, mem, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_FAM},A{r},{TXN_MON},C_Month,{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 3, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_FAM},A{r},{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        r += 1
    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# HEALTHCARE & INSURANCE
# ---------------------------------------------------------------------------
def build_healthcare(wb):
    s = wb.create_sheet(HEA)
    set_widths(s, [24, 22, 14, 14, 14, 13, 26])
    title_band(s, "🏥 Healthcare & Insurance", "Healthcare spending vs budget, plus every insurance premium in one place.",
               7)
    header_row(s, 3, ["Category", "Subcategory", "Monthly Budget", "Actual This Month",
                      "Actual YTD", "Variance", "Notes"])
    s.freeze_panes = "A4"
    subs = BUDGET["Healthcare"]
    r = 4
    for sub in subs:
        budget = DEFAULT_BUDGET.get(("Healthcare", sub), 0)
        cell(s, r, 1, "Healthcare", bg=INPUT_FILL, locked=False)
        cell(s, r, 2, sub, bg=INPUT_FILL, locked=False)
        cell(s, r, 3, budget if budget else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 4, f'=SUMIFS({TXN_AMT},{TXN_CAT},"Healthcare",{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 5, f'=SUMIFS({TXN_AMT},{TXN_CAT},"Healthcare",{TXN_SUB},B{r},{TXN_TYPE},"Expense",{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 6, f'=IF(C{r}="","",C{r}-D{r})', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 7, None, bg=INPUT_FILL, locked=False)
        r += 1
    tr = r + 1
    cell(s, tr, 1, "TOTAL", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, tr, 2, "Healthcare Total", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, tr, 3, f"=SUM(C{4}:C{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, tr, 4, f"=SUM(D{4}:D{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, tr, 5, f"=SUM(E{4}:E{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)

    pr = tr + 3
    cell(s, pr, 1, "INSURANCE PREMIUMS & HEALTH DETAILS", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, pr + 1, ["Policy", "Monthly Premium", "Annual Cost", "Deductible",
                           "OOP Max", "HSA/FSA", "Notes"])
    policies = [("Health Insurance", 420, None, 3000, 9200, None),
                ("Dental", 30, None, 150, 1500, None),
                ("Vision", 20, None, 25, 500, None),
                ("Life Insurance", 55, None, None, None, None),
                ("Disability", 40, None, None, None, None),
                ("Auto Insurance", 130, None, 500, None, None),
                ("Home / Renters", 120, None, 1000, None, None)]
    r = pr + 2
    for pol, prem, ded, oop, hsa, notes in policies:
        cell(s, r, 1, pol, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, prem if prem else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 3, f'=IF(B{r}="","",B{r}*12)', bg=CALC_FILL, numfmt=USD, locked=True)
        for col, val in ((4, ded), (5, oop)):
            cell(s, r, col, val if val else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 6, hsa if hsa else None, bg=INPUT_FILL, numfmt=USD, locked=False)
        cell(s, r, 7, "", bg=INPUT_FILL, locked=False)
        r += 1
    trow = r + 1
    cell(s, trow, 1, "TOTAL PREMIUMS", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, trow, 2, f"=SUM(B{pr+2}:B{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, trow, 3, f"=SUM(C{pr+2}:C{r-1})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# TAX CENTER (simplified estimate)
# ---------------------------------------------------------------------------
SINGLE = [(11925, 0.10), (48475, 0.12), (103350, 0.22), (197300, 0.24),
          (250525, 0.32), (626350, 0.35), (None, 0.37)]
MFJ = [(23850, 0.10), (96950, 0.12), (206700, 0.22), (394600, 0.24),
       (501050, 0.32), (751600, 0.35), (None, 0.37)]
HOH = [(17000, 0.10), (64850, 0.12), (103350, 0.22), (197300, 0.24),
       (250525, 0.32), (626350, 0.35), (None, 0.37)]
BRACKETS = {"Single": SINGLE, "Married Filing Jointly": MFJ, "Married Filing Separately": SINGLE,
            "Head of Household": HOH, "Qualifying Surviving Spouse": MFJ}
STD = {"Single": 15000, "Married Filing Jointly": 30000, "Married Filing Separately": 15000,
       "Head of Household": 22500, "Qualifying Surviving Spouse": 30000}


def tax_nested(X, brackets):
    n = len(brackets)
    lower = [0]
    cum = [0]
    for i in range(n - 1):
        lim, rate = brackets[i]
        cum.append(cum[-1] + (lim - lower[-1]) * rate)
        lower.append(lim)
    def seg(i):
        lim, rate = brackets[i]
        return f"{cum[i]}+({X}-{lower[i]})*{rate}"
    res = seg(n - 1)
    for i in range(n - 2, -1, -1):
        lim, _r = brackets[i]
        res = f"IF({X}<={lim},{seg(i)},{res})"
    return res


def fed_formula(X):
    """Estimate federal tax for the chosen filing status (based on cell B5)."""
    single = tax_nested(X, SINGLE)
    mfj = tax_nested(X, MFJ)
    hoh = tax_nested(X, HOH)
    return (f'IF($B$5="Married Filing Jointly",{mfj},'
            f'IF($B$5="Qualifying Surviving Spouse",{mfj},'
            f'IF($B$5="Head of Household",{hoh},{single})))')


def build_tax(wb):
    s = wb.create_sheet(TAX)
    set_widths(s, [34, 18, 34, 18])
    title_band(s, "🇺🇸 U.S. Tax Center", "ESTIMATE ONLY — simplified federal + FICA estimate. Update brackets & deductions when tax rules change.",
               4)
    cell(s, 4, 1, "INPUTS", bold=True, bg=SECTION_FILL, locked=False)
    inputs = [("Filing Status", "list", None),
              ("Gross Income (YTD)", "formula", f'=SUMIFS({INC_GROSS},{INC_YR},C_Year)'),
              ("401(k)/403(b) pre-tax (YTD)", "formula", f'=SUMIFS({INC_401},{INC_YR},C_Year)'),
              ("HSA pre-tax (YTD)", "formula", f'=SUMIFS({INC_HSA},{INC_YR},C_Year)'),
              ("Federal Withheld (YTD)", "formula", f'=SUMIFS({INC_FED},{INC_YR},C_Year)'),
              ("State/Local Withheld (YTD)", "formula", f'=SUMIFS({INC_ST},{INC_YR},C_Year)'),
              ("FICA Withheld (YTD)", "formula", f'=SUMIFS({INC_FICA1},{INC_YR},C_Year)+SUMIFS({INC_FICA2},{INC_YR},C_Year)'),
              ("Other Taxable Income (YTD)", "input", None),
              ("Dependents (count)", "input", None),
              ("Charitable Donations", "input", None),
              ("Mortgage Interest", "input", None),
              ("Property Taxes Paid", "input", None),
              ("State & Local Taxes (SALT)", "formula", "=B10")]
    r = 5
    for lab, kind, formula in inputs:
        cell(s, r, 1, lab, bold=True, locked=False)
        c = cell(s, r, 2, formula if formula else None, bg=CALC_FILL if kind == "formula" else INPUT_FILL,
                 numfmt=USD if lab != "Filing Status" else None, locked=(kind == "formula"))
        r += 1

    ds = 5 + len(inputs) + 2   # standard deduction row
    cell(s, ds, 1, "STANDARD DEDUCTION", bold=True, bg=CALC_FILL, locked=False)
    cell(s, ds, 2, "=IF(B5=\"Married Filing Jointly\",30000,IF(B5=\"Qualifying Surviving Spouse\",30000,IF(B5=\"Head of Household\",22500,15000)))",
         bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ds + 1, 1, "ITEMIZED ESTIMATE", bold=True, bg=CALC_FILL, locked=False)
    cell(s, ds + 1, 2, "=B14+B15+B16+MIN(10000,B17)", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ds + 2, 1, "DEDUCTION USED", bold=True, bg=CALC_FILL, locked=False)
    cell(s, ds + 2, 2, f"=MAX(B{ds},B{ds+1})", bg=CALC_FILL, numfmt=USD, locked=True)

    # Results
    ri = ds + 5
    cell(s, ri, 1, "ESTIMATED TAX POSITION", bold=True, bg=SECTION_FILL, locked=False)
    cell(s, ri + 1, 1, "Adjusted Gross Income (AGI)", bold=True, locked=False)
    cell(s, ri + 1, 2, "=B6-B7-B8", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ri + 2, 1, "Taxable Income", bold=True, locked=False)
    cell(s, ri + 2, 2, f"=MAX(0,B{ri+1}-$B${ds+2})", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ri + 3, 1, "Estimated Federal Tax", bold=True, locked=False)
    cell(s, ri + 3, 2, "=" + fed_formula(f"B{ri+2}"), bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ri + 4, 1, "Estimated FICA (employee)", bold=True, locked=False)
    cell(s, ri + 4, 2, "=IF(B6=\"\",\"\",MIN(B6,176100)*0.062+B6*0.0145)", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ri + 5, 1, "Total Estimated Tax", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, ri + 5, 2, f"=B{ri+3}+B{ri+4}", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, ri + 6, 1, "Total Withheld (Fed + State + FICA)", bold=True, locked=False)
    cell(s, ri + 6, 2, "=B9+B10+B11", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, ri + 7, 1, "EST. REFUND / (AMOUNT OWED)", bold=True, locked=False)
    cell(s, ri + 7, 2, f"=B{ri+6}-B{ri+5}", bg=CALC_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, ri + 7, 4, "Positive = refund. Negative = you may owe.", italic=True, size=9,
         color="3D4A46", locked=False, border=None)

    cell(s, ri + 9, 1, "⚠️ This is a simplified ESTIMATE only. It ignores many credits, deductions, and phaseouts, "
                       "and represents old tax rules. Update the brackets, standard deduction and formulas when "
                       "tax law changes, or consult a professional.", italic=True, size=9, wrap=True,
         color="9C5500", locked=False, border=None)
    s.merge_cells(start_row=ri + 9, start_column=1, end_row=ri + 10, end_column=4)
    add_dv(s, "list", "=L_Filing_Status", "B5", allow_blank=False, error=True)
    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------------------------
def build_analytics(wb):
    s = wb.create_sheet(ANA)
    set_widths(s, [22, 15, 14, 15, 15, 15, 12, 12])
    title_band(s, "📊 Financial Analytics", "Automatic answers — where the money went, trends, needs vs wants, savings rate, debt, and per-person spend.",
               8)

    # ---- YTD summary ----
    cell(s, 4, 1, "YEAR-TO-DATE SUMMARY", bold=True, bg=SECTION_FILL, locked=False)
    labels = ["Total Income", "Total Spending", "Net Savings", "Savings Rate",
              "This Month Spending", "This Month Net", "Total Debt", "Avg Monthly Spend"]
    for i, lab in enumerate(labels, start=1):
        cell(s, 5, i, lab, bold=True, bg=HEADER_FILL2, color="FFFFFF", horizontal="center", wrap=True)
    spend_ytd = f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_YR},C_Year)'
    spend_m = f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)'
    cell(s, 6, 1, f'=SUMIFS({INC_NET},{INC_YR},C_Year)', bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 2, spend_ytd, bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 3, "=A6-B6", bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 4, '=IF(A6=0,"",C6/A6)', bg=CALC_FILL, numfmt=PCT, locked=True, horizontal="center")
    cell(s, 6, 5, spend_m, bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 6, f'=SUMIFS({INC_NET},{INC_MON},C_Month,{INC_YR},C_Year)-E6', bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 7, f'=SUM({DBT_BAL})', bg=CALC_FILL, numfmt=USD, locked=True)
    cell(s, 6, 8, '=IFERROR(AVERAGEIF($C$24:$C$35,">0"),0)', bg=CALC_FILL, numfmt=USD, locked=True)

    # ---- Spending by category ----
    cell(s, 8, 1, "SPENDING BY CATEGORY (YTD)", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, 9, ["Category", "Monthly Budget", "Actual YTD", "Actual This Month",
                      "Variance", "% of Total", "Rank"], start=1)
    r0 = 10
    cat_start = r0
    for i, cat in enumerate(CATEGORIES):
        r = r0 + i
        row = BUDGET_SUBTOTAL.get(cat)
        cell(s, r, 1, cat, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, f"={q(BUD)}!$C${row}" if row else None, bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 3, f'=SUMIFS({TXN_AMT},{TXN_CAT},A{r},{TXN_TYPE},"Expense",{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 4, f'=SUMIFS({TXN_AMT},{TXN_CAT},A{r},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 5, f"=B{r}-C{r}", bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 6, f'=IF($B$6=0,"",C{r}/$B$6)', bg=CALC_FILL, numfmt=PCT, locked=True, horizontal="center")
        cell(s, r, 7, f'=IF(C{r}="","",RANK(C{r},$C${cat_start}:$C${cat_start+len(CATEGORIES)-1},0))',
             bg=CALC_FILL, numfmt=NUM, locked=True, horizontal="center")
        r += 1
    cat_end = r - 1

    # ---- Monthly trend ----
    tr_hdr = cat_end + 2
    cell(s, tr_hdr, 1, "MONTHLY CASH FLOW TREND", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, tr_hdr + 1, ["Month", "Income", "Spending", "Net"], start=1)
    td_start = tr_hdr + 2
    for i, mon in enumerate(MONTHS):
        r = td_start + i
        mnum = i + 1
        cell(s, r, 1, mon, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, f'=SUMIFS({INC_NET},{INC_MON},{mnum},{INC_YR},C_Year)', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 3, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_MON},{mnum},{TXN_YR},C_Year)', bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 4, f"=B{r}-C{r}", bg=CALC_FILL, numfmt=USD, locked=True)
    td_end = td_start + 11

    # ---- Needs vs Wants ----
    nw = td_end + 3
    cell(s, nw, 1, "NEEDS vs WANTS (YTD)", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, nw + 1, ["Type", "Actual", "% of Total"], start=1)
    for i, (lab) in enumerate(["Essential", "Discretionary"]):
        r = nw + 2 + i
        cell(s, r, 1, lab, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_ESS},"{lab}",{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 3, f'=IF($B$6=0,"",B{r}/$B$6)', bg=CALC_FILL, numfmt=PCT, locked=True, horizontal="center")
    tot = nw + 4
    cell(s, tot, 1, "TOTAL", bold=True, bg=TOTAL_FILL, locked=False)
    cell(s, tot, 2, f"=SUM(B{nw+2}:B{nw+3})", bg=TOTAL_FILL, numfmt=USD, locked=True, bold=True)
    cell(s, tot, 3, f'=IF($B$6=0,"",B{tot}/$B$6)', bg=TOTAL_FILL, numfmt=PCT, locked=True, bold=True, horizontal="center")

    # ---- By family member ----
    mb = tot + 3
    cell(s, mb, 1, "SPENDING BY FAMILY MEMBER (THIS MONTH)", bold=True, bg=SECTION_FILL, locked=False)
    header_row(s, mb + 1, ["Family Member", "This Month", "YTD"], start=1)
    for i, mem in enumerate(FAMILY):
        r = mb + 2 + i
        cell(s, r, 1, mem, bg=INPUT_FILL, locked=False)
        cell(s, r, 2, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_FAM},A{r},{TXN_MON},C_Month,{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, r, 3, f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_FAM},A{r},{TXN_YR},C_Year)',
             bg=CALC_FILL, numfmt=USD, locked=True)

    # ---- Quick answers ----
    qa = mb + 2 + len(FAMILY) + 2
    cell(s, qa, 1, "QUICK ANSWERS (YTD)", bold=True, bg=SECTION_FILL, locked=False)
    quick = [("Subscriptions", f'=SUMIFS({TXN_AMT},{TXN_SUB},"Subscriptions",{TXN_YR},C_Year)'),
             ("Restaurants", f'=SUMIFS({TXN_AMT},{TXN_SUB},"Restaurants",{TXN_YR},C_Year)'),
             ("Groceries", f'=SUMIFS({TXN_AMT},{TXN_SUB},"Groceries",{TXN_YR},C_Year)'),
             ("Gas / Fuel", f'=SUMIFS({TXN_AMT},{TXN_SUB},"Gas",{TXN_YR},C_Year)'),
             ("Top Category", f"=INDEX(A{cat_start}:A{cat_end},MATCH(MAX(C{cat_start}:C{cat_end}),C{cat_start}:C{cat_end},0))")]
    for i, (lab, form) in enumerate(quick):
        r = qa + 1 + i
        cell(s, r, 1, lab, bold=True, locked=False)
        cell(s, r, 2, form, bg=CALC_FILL, numfmt=USD if lab != "Top Category" else None, locked=True)

    protect(s, allow_sort=False, allow_filter=False)
    return s


# ---------------------------------------------------------------------------
# CALENDAR
# ---------------------------------------------------------------------------
def build_calendar(wb):
    s = wb.create_sheet(CAL)
    set_widths(s, [6, 14, 15, 15, 15, 15])
    title_band(s, "📅 Financial Calendar", "Everything due on each day of the C_Year / C_Month — bills, paydays, debt payments and subscriptions.",
               6)
    header_row(s, 3, ["Day", "Bills Due", "Paydays / Income", "Debt Minimums", "Subscriptions", "Notes"])
    s.freeze_panes = "A4"
    for d in range(1, 32):
        r = 3 + d
        cell(s, r, 1, d, bg=INPUT_FILL, numfmt=NUM, locked=False, horizontal="center")
        cell(s, r, 2, f'=SUMIFS({BIL_AMT},{BIL_MON},C_Month,{BIL_YR},C_Year,{BIL_DAY},A{r})',
             bg=CALC_FILL, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 3, f'=SUMIFS({INC_NET},{INC_MON},C_Month,{INC_YR},C_Year,{INC_DAY},A{r})',
             bg=CALC_FILL, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 4, f'=SUMIFS({DBT_MIN},{DBT_MON},C_Month,{DBT_YR},C_Year,{DBT_DAY},A{r})',
             bg=CALC_FILL, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 5, f'=SUMIFS({TXN_AMT},{TXN_SUB},"Subscriptions",{TXN_MON},C_Month,{TXN_YR},C_Year,{TXN_DAY},A{r})',
             bg=CALC_FILL, numfmt=USD, locked=True, horizontal="center")
        cell(s, r, 6, None, bg=INPUT_FILL, locked=False)
    # highlight today
    r = 3 + get_day()
    for c in range(1, 7):
        s.cell(row=r, column=c).fill = fill("FFF2CC")
    protect(s, allow_sort=False, allow_filter=False)
    return s


def get_day():
    import datetime
    return datetime.date.today().day
