"""12 Profit & Loss - rolling twelve months plus YTD."""

from __future__ import annotations

from xlsxwriter.utility import xl_col_to_name

from ..config import Config, EXPENSE_CATEGORIES
from ..writer import SheetWriter
from . import common as C

NAME = "12 Profit & Loss"
MONTHS = 12


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color="#6D2E4F", landscape=True)
    last = MONTHS + 1          # label column + 12 months + YTD
    sheet.banner("12  Profit & Loss",
                 "Net sales, costs and operating profit per month - "
                 "every cell reads tabs 6, 7, 10, 11 and 14.", last)
    row = 4
    sheet.table_head(row, 0, ["Line"] + ["" for _ in range(MONTHS + 1)])
    hdr = row
    for k in range(MONTHS):
        sheet.formula(hdr, 1 + k,
                      f'=TEXT(EDATE(TODAY(),-{MONTHS - 1 - k}),"yyyy-mm")',
                      sheet.f.chrome("header"))
    sheet.write(hdr, 1 + MONTHS, "12-month total", sheet.f.chrome("header"))

    rows: list = []

    def line(label: str, builder, style="money", bold=False):
        rows.append((label, builder, style, bold))

    def ym(col_idx: int) -> str:
        return f"${xl_col_to_name(col_idx)}${hdr}"

    line("Service revenue (net)",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("SalesDates", ym(c))}'
                   f'*(SalesType="Service")*SalesNet),2)')
    line("Retail revenue (net)",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("SalesDates", ym(c))}'
                   f'*(SalesType="Retail")*SalesNet),2)')
    line("Total net sales", None, "money", True)
    line("of which tax collected",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("SalesDates", ym(c))}'
                   f'*SalesTax),2)')
    line("Processing fees",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("SalesDates", ym(c))}'
                   f'*SalesFee),2)')
    for cat in EXPENSE_CATEGORIES:
        line(f"{cat}",
             lambda c, cat=cat: f'ROUND(SUMPRODUCT('
                                f'{C.ym_mask("ExpDates", ym(c))}'
                                f'*(ExpCat="{cat}")*ExpAmount),2)')
    line("Payroll & tips cost",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("PayrollDates", ym(c))}'
                   f'*PayrollCost),2)')
    line("Total operating costs", None, "money", True)
    line("OPERATING PROFIT", None, "money", True)
    line("Break-even revenue", None, "money")
    line("Tax reserve suggestion", None, "money")
    line("Cash in (sales + deposits)",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("SalesDates", ym(c))}'
                   f'*SalesNet)+SUMPRODUCT({C.ym_mask("PayDates", ym(c))}'
                   f'*(PayKind="Deposit")*PayAmount),2)')
    line("Cash out (costs + stock)",
         lambda c: f'ROUND(SUMPRODUCT({C.ym_mask("ExpDates", ym(c))}'
                   f'*ExpAmount)+SUMPRODUCT('
                   f'{C.ym_mask("PayrollDates", ym(c))}*PayrollCost)'
                   f'+SUMPRODUCT({C.ym_mask("PurchDates", ym(c))}'
                   f'*PurchTotal),2)')

    r = hdr + 1
    idx = {}
    for label, builder, style, bold in rows:
        idx[label] = r
        fmt = (sheet.f.calc(style, bold=True) if bold
               else sheet.f.calc(style))
        sheet.write(r, 0, label, sheet.f.calc("text", bold=bold))
        for k in range(MONTHS):
            c = 1 + k
            if builder is not None:
                sheet.formula(r, c, "=" + builder(c), fmt)
        r += 1

    # derived rows, month by month
    for k in range(MONTHS):
        c = 1 + k
        cl = xl_col_to_name(c)
        sheet.formula(idx["Total net sales"], c,
                      f'=ROUND(${cl}${idx["Service revenue (net)"]}+'
                      f'${cl}${idx["Retail revenue (net)"]},2)',
                      sheet.f.calc("money", bold=True))
        cost_first = idx["Rent"]
        cost_last = idx["Payroll & tips cost"]
        sheet.formula(idx["Total operating costs"], c,
                      f'=ROUND(SUM(${cl}${cost_first}:${cl}${cost_last}),2)',
                      sheet.f.calc("money", bold=True))
        sheet.formula(idx["OPERATING PROFIT"], c,
                      f'=ROUND(${cl}${idx["Total net sales"]}-'
                      f'${cl}${idx["Total operating costs"]},2)',
                      sheet.f.calc("money", bold=True))
        fixed = (f'${cl}${idx["Rent"]}+${cl}${idx["Utilities"]}+'
                 f'${cl}${idx["Insurance"]}+${cl}${idx["Software"]}+'
                 f'${cl}${idx["Payroll & tips cost"]}')
        sheet.formula(idx["Break-even revenue"], c,
                      f'=IF(OR(${cl}${idx["Total net sales"]}=0,'
                      f'${cl}${idx["Total net sales"]}-'
                      f'(${cl}${idx["Total operating costs"]}-({fixed}))'
                      f'<=0),"",ROUND(({fixed})/(1-('
                      f'${cl}${idx["Total operating costs"]}-({fixed}))/'
                      f'${cl}${idx["Total net sales"]}),2))',
                      sheet.f.calc("money"))
        sheet.formula(idx["Tax reserve suggestion"], c,
                      f'=IF(${cl}${idx["OPERATING PROFIT"]}<=0,0,ROUND('
                      f'${cl}${idx["OPERATING PROFIT"]}*TaxReserveRate,2))',
                      sheet.f.calc("money"))
    # YTD column = sum of the twelve months
    for label, builder, style, bold in rows:
        r_ = idx[label]
        first_c = xl_col_to_name(1)
        last_c = xl_col_to_name(MONTHS)
        sheet.formula(r_, 1 + MONTHS,
                      f'=ROUND(SUM(${first_c}${r_}:${last_c}${r_}),2)',
                      sheet.f.calc(style, bold=bold))
    r = idx["Cash out (costs + stock)"] + 2
    row = sheet.section(r, "READING IT", last)
    for t in [
        "Net sales are gross minus discounts, refunds and plus tax - the "
        "same number as tab 6, never double counted with deposits.",
        "Break-even uses rent, utilities, insurance, software and payroll "
        "as fixed; everything else as variable.",
        "The tax reserve is a suggestion at your Settings rate - set it "
        "to 0 if you prefer.",
    ]:
        row = sheet.note(row, t, last) + 1
    row += 1
    C.footer(sheet, cfg, last, row)
    sheet.finish(freeze_row=hdr + 1, freeze_col=1,
                 print_area=f"A1:{xl_col_to_name(last)}{row + 2}")
    sheet.protect()
    return sheet
