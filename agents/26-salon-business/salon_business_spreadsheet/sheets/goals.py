"""17 Goals & Budget - monthly targets versus actuals."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import number_check
from . import common as C
from .. import sample_data

NAME = "17 Goals & Budget"


def spec(cfg: Config) -> SheetSpec:
    ym = "{month}{r}"
    return SheetSpec(
        name=NAME,
        title="17  Goals & Budget",
        subtitle="Revenue targets and expense budgets per month, with "
                 "actuals read straight from the sales and expense "
                 "registers.",
        tab_color="#6D2E4F",
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text="Month is a yyyy-mm stamp (2026-10). Actual columns sum "
                  "every sales and expense row in that month, so the "
                  "variance is always current.",
        columns=[
            Col("month", "Month", 10, "id",
                note="yyyy-mm, e.g. 2026-10."),
            Col("rev_target", "Revenue target", 13, "money",
                validate=number_check(0, 10000000)),
            Col("rev_actual", "Revenue actual", 13, "money",
                formula='IF({month}{r}="","",ROUND(SUMPRODUCT(' +
                        C.ym_mask("SalesDates", ym) +
                        '*SalesNet),2))'),
            Col("rev_var", "Variance", 12, "money",
                formula='IF(OR({month}{r}="",{rev_target}{r}=""),"",'
                        'ROUND(N({rev_actual}{r})-N({rev_target}{r}),2))'),
            Col("rev_att", "Attained", 9, "percent",
                formula='IF(OR({month}{r}="",N({rev_target}{r})=0),"",'
                        '{rev_actual}{r}/{rev_target}{r})'),
            Col("exp_budget", "Expense budget", 13, "money",
                validate=number_check(0, 10000000)),
            Col("exp_actual", "Expense actual", 13, "money",
                formula='IF({month}{r}="","",ROUND(SUMPRODUCT(' +
                        C.ym_mask("ExpDates", ym) + '*ExpAmount),2))'),
            Col("exp_var", "Budget left", 12, "money",
                formula='IF(OR({month}{r}="",{exp_budget}{r}=""),"",'
                        'ROUND(N({exp_budget}{r})-N({exp_actual}{r}),2))'),
        ],
        samples=sample_data.goal_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet, fmts, cfg, reg) -> None:
    row = reg[NAME].last_data_row + 3
    last = 5
    sheet.section(row, "MONTHLY BUDGET BY CATEGORY", last)
    row += 1
    sheet.table_head(row, 0, ["Category", "Monthly budget",
                              "Actual this month", "Variance",
                              "Share of spend"])
    from ..layout import quote_sheet
    exp = quote_sheet("11 Expenses")
    for i, cat in enumerate(__import__(
            "salon_business_spreadsheet.config",
            fromlist=["EXPENSE_CATEGORIES"]).EXPENSE_CATEGORIES):
        r = row + 1 + i
        sheet.write(r, 0, cat, sheet.f.calc("text"))
        sheet.write(r, 1, None, sheet.f.input("money"))
        tmpl = (
            f'=ROUND(SUMIFS({exp}!$K${{first}}:$K${{last}},'
            f'{exp}!$D${{first}}:$D${{last}},$A{r},'
            f'{exp}!$C${{first}}:$C${{last}},' + C.cur_ym() + '),2)'
        ).replace("{first}", str(reg["11 Expenses"].first_data_row)) \
         .replace("{last}", str(reg["11 Expenses"].last_data_row))
        sheet.formula(r, 2, tmpl, sheet.f.calc("money"))
        sheet.formula(r, 3, f'=IF($B{r}="","",ROUND(N($B{r})-$C{r},2))',
                      sheet.f.calc("money"))
        sheet.formula(
            r, 4,
            f'=IF(SUM($C${row + 1}:$C${row + 10})=0,"",'
            f'$C{r}/SUM($C${row + 1}:$C${row + 10}))',
            sheet.f.calc("percent"))
    sheet.note(row + 12,
               "Budgets are yours: type a monthly figure per category and "
               "the variance tracks itself.", last)
