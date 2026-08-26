"""The 🏠 Family Dashboard — the premium 'wow' front-end."""
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from common import (cell, font, fill, align, q, T, DASH, ACC, VEH, GOL, HOM, ANA, BUD,
                    TXN, USD, USD0, PCT, PCT0, DATE, NUM, PASSWORD,
                    title_band, header_row, protect, set_widths,
                    TITLE_FILL, HEADER_FILL, HEADER_FILL2, SECTION_FILL, INPUT_FILL,
                    CALC_FILL, TOTAL_FILL, ALT_FILL, GOOD_FILL, WARN_FILL, BAD_FILL,
                    GOOD_FONT, WARN_FONT, BAD_FONT, BOX, FAMILY)
import summary
from summary import (TXN_AMT, TXN_TYPE, TXN_MON, TXN_YR, TXN_SUB, INC_NET, INC_MON, INC_YR,
                     ACC_BAL, ACC_TYPE, BIL_AMT, BIL_MON, BIL_YR, DBT_BAL, DBT_TYPE)
ACC_LIMIT = f"{q(ACC)}!$E$4:$E$103"   # Accounts! Credit Limit column

HOME_REF = q(HOM)
VEH_REF = q(VEH)
GOL_REF = q(GOL)
ANA_REF = q(ANA)
BUD_REF = q(BUD)


def asset_sum(types):
    return "=" + "+".join(f'SUMIF({ACC_TYPE},"{t}",{ACC_BAL})' for t in types)


def build_dashboard(wb):
    s = wb.create_sheet(DASH)
    s.sheet_view.showGridLines = False
    set_widths(s, [28, 18, 24, 18, 18, 22])
    title_band(s, "🏠 Family Financial Dashboard",
               "Your entire household on one screen. Every number below flows automatically from the other tabs.",
               6)

    cell(s, 4, 1, "Report Period", bold=True, bg=SECTION_FILL, locked=False)
    cell(s, 4, 2, '=TEXT(C_Date,"mmmm yyyy")', bg=CALC_FILL, locked=True, color="0B3D2E", bold=True)

    def section(row, text):
        cell(s, row, 1, text, bold=True, bg=SECTION_FILL, locked=False, size=12)

    def kpi(row, label, formula, numfmt=USD):
        cell(s, row, 1, label, bold=True, locked=False)
        cell(s, row, 2, formula, bg=CALC_FILL, numfmt=numfmt, locked=True, bold=True, horizontal="right")

    # ---- MONTHLY SNAPSHOT ----
    section(6, "MONTHLY SNAPSHOT")
    inc_m = f'=SUMIFS({INC_NET},{INC_MON},C_Month,{INC_YR},C_Year)'
    exp_m = f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_MON},C_Month,{TXN_YR},C_Year)'
    kpi(7, "Gross Monthly Income", inc_m)
    kpi(8, "Monthly Spending", exp_m)
    kpi(9, "Surplus / (Deficit)", "=B7-B8")
    kpi(10, "Savings Rate", '=IF(B7=0,"",B9/B7)', PCT)
    kpi(11, "Bills Due This Month", f'=SUMIFS({BIL_AMT},{BIL_MON},C_Month,{BIL_YR},C_Year)')
    kpi(12, "Monthly Budget", f"={BUD_REF}!$C${summary.BUDGET_TOTAL_ROW}")
    kpi(13, "Budget vs Actual Variance", "=B12-B8")
    kpi(14, "YTD Spending", f'=SUMIFS({TXN_AMT},{TXN_TYPE},"Expense",{TXN_YR},C_Year)')

    # ---- CASH & DEBT ----
    section(16, "CASH & DEBT POSITION")
    liab_cc = f'SUMIFS({ACC_BAL},{ACC_TYPE},"Credit Card")'
    loans = f'SUMIFS({DBT_BAL},{DBT_TYPE},"<>Credit Card")'
    assets = asset_sum(["Checking", "Savings", "HYSA", "Cash", "401(k)", "403(b)", "IRA",
                        "Roth IRA", "Brokerage", "529", "HSA", "FSA", "CD", "Other Investment"])
    kpi(17, "Total Assets", f"{assets}+{HOME_REF}!$B$5+SUM({VEH_REF}!$L$4:$L$33)", USD0)
    kpi(18, "Total Liabilities", f"={liab_cc}+{loans}+{HOME_REF}!$B$10", USD0)
    kpi(19, "Net Worth", "=B17-B18", USD0)
    kpi(20, "Total Debt", f"={liab_cc}+{loans}+{HOME_REF}!$B$10", USD0)
    kpi(21, "Cash Available", asset_sum(["Checking", "Savings", "HYSA", "Cash"]))
    kpi(22, "Emergency Fund (liquid)",
        f'=SUMIFS({ACC_BAL},{ACC_TYPE},"Savings")+SUMIFS({ACC_BAL},{ACC_TYPE},"HYSA")+SUMIFS({ACC_BAL},{ACC_TYPE},"Cash")')
    kpi(23, "Credit Available", f'=SUMIF({ACC_TYPE},"Credit Card",{ACC_LIMIT})-SUMIFS({ACC_BAL},{ACC_TYPE},"Credit Card")')

    # ---- YEAR-TO-DATE ----
    section(25, "YEAR-TO-DATE")
    kpi(26, "YTD Savings", "=B7-B8")
    kpi(27, "YTD Savings Rate", '=IFERROR((B7-B8)/B7,"")', PCT)
    kpi(28, "Avg Monthly Spend", f"={ANA_REF}!$H$6")
    kpi(29, "Subscriptions (YTD)", f'=SUMIFS({TXN_AMT},{TXN_SUB},"Subscriptions",{TXN_YR},C_Year)')
    kpi(30, "Goals Completion %", f'=IF(SUM({GOL_REF}!$C$4:$C$103)=0,"",SUM({GOL_REF}!$D$4:$D$103)/SUM({GOL_REF}!$C$4:$C$103))', PCT)
    kpi(31, "Goals Total Saved", f'=SUM({GOL_REF}!$D$4:$D$103)')
    kpi(32, "Goals Total Target", f'=SUM({GOL_REF}!$C$4:$C$103)')

    # ---- ALERTS ----
    section(34, "ALERTS")
    alerts = [
        ("Emergency Fund (months covered)",
         f'=IFERROR((SUMIFS({ACC_BAL},{ACC_TYPE},"Savings")+SUMIFS({ACC_BAL},{ACC_TYPE},"HYSA")+SUMIFS({ACC_BAL},{ACC_TYPE},"Cash"))/{ANA_REF}!$H$6,"")',
         '=IF(B35="","",IF(B35<3,"🔴 Under 3 months",IF(B35<6,"🟡 3-6 months","🟢 6+ months")))', NUM),
        ("Budget Status (this month)", "=B13",
         '=IF(B36="","",IF(B36<0,"🟡 Over budget","🟢 Under budget"))', USD),
        ("Savings Rate vs 20% target", '=IF(B7=0,"",B9/B7)',
         '=IF(B37="","",IF(B37>=0.2,"🟢 20%+ saved","🟡 Below 20% target"))', PCT),
        ("Credit Utilization",
         f'=IF(SUMIF({ACC_TYPE},"Credit Card",{ACC_LIMIT})=0,"",SUMIFS({ACC_BAL},{ACC_TYPE},"Credit Card")/SUMIF({ACC_TYPE},"Credit Card",{ACC_LIMIT}))',
         '=IF(B38="","",IF(B38>0.3,"🔴 High utilization",IF(B38>0.1,"🟡 Moderate","🟢 Low utilization")))', PCT),
    ]
    for i, (lab, valf, statf, fmt) in enumerate(alerts):
        rr = 35 + i
        cell(s, rr, 1, lab, bold=True, locked=False)
        cell(s, rr, 2, valf, bg=CALC_FILL, numfmt=fmt, locked=True, horizontal="right")
        cell(s, rr, 3, statf, bg=INPUT_FILL, locked=False, horizontal="center")

    # ---- GOALS PROGRESS ----
    side = 41
    section(side, "GOALS & SINKING FUNDS")
    header_row(s, side + 1, ["Goal", "Target", "Current", "% Complete", "Status"], start=1)
    for i in range(6):
        rr = side + 2 + i
        g = 4 + i
        cell(s, rr, 1, f"={GOL_REF}!$A${g}", bg=INPUT_FILL, locked=False)
        cell(s, rr, 2, f"={GOL_REF}!$C${g}", bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, rr, 3, f"={GOL_REF}!$D${g}", bg=CALC_FILL, numfmt=USD, locked=True)
        cell(s, rr, 4, f"={GOL_REF}!$H${g}", bg=CALC_FILL, numfmt=PCT, locked=True)
        cell(s, rr, 5, f'=IF(D{rr}="","",IF(D{rr}>=1,"🏆 Complete","🔵 In progress"))', bg=INPUT_FILL, locked=False, horizontal="center")

    # ---- CHARTS ----
    build_charts(wb, s, anchor_row=side + 10)
    protect(s, allow_sort=False, allow_filter=False)
    return s


def build_charts(wb, s, anchor_row):
    ana = wb[ANA]
    line = LineChart()
    line.title = "Monthly Income vs Spending (this year)"
    line.style = 12
    line.y_axis.title = "USD"
    line.x_axis.title = "Month"
    line.width = 16
    line.height = 9
    data = Reference(ana, min_col=2, min_row=23, max_col=3, max_row=35)
    cats = Reference(ana, min_col=1, min_row=24, max_row=35)
    line.add_data(data, titles_from_data=True)
    line.set_categories(cats)
    s.add_chart(line, f"A{anchor_row}")

    bar = BarChart()
    bar.type = "bar"
    bar.title = "Spending by Category (YTD)"
    bar.y_axis.title = "Amount"
    bar.width = 16
    bar.height = 10
    data2 = Reference(ana, min_col=3, min_row=9, max_row=20)
    cats2 = Reference(ana, min_col=1, min_row=10, max_row=20)
    bar.add_data(data2, titles_from_data=True)
    bar.set_categories(cats2)
    s.add_chart(bar, f"G{anchor_row}")
