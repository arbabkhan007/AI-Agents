"""Register: Budget, with monthly totals and variance block."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import number_check

NAME = "Budget"
ROWS = 120
LAST_COL = 11

COLUMNS = [
    dict(header="Budget ID", key="id", width=11,
         is_formula=True,
         formula="=IF($C{r}=\"\",\"\",\"B-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Month", key="month", width=10,
         validate={"validate": "list", "source": "=MonthYearList"},
         note="e.g. Mar-26. Feeds the monthly totals below."),
    dict(header="Category", key="category", width=18,
         validate={"validate": "list",
                   "source": ["Paid Ads", "Influencers", "Design & Tools",
                              "Photo & Video", "Market Costs",
                              "Promotions", "Email Platform", "Education",
                              "Misc"]}),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Channel", key="channel", width=16,
         note="Where the money goes."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Planned", key="planned", width=11, style="money",
         validate=number_check(0, 1000000)),
    dict(header="Spent", key="spent", width=11, style="money",
         validate=number_check(0, 1000000)),
    dict(header="Variance", key="variance", width=11, style="money",
         is_formula=True,
         formula="=IF($C{r}=\"\",\"\",$G{r}-$H{r})",
         note="Planned minus spent."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Planned", "Approved", "Paid", "Cancelled"]}),
    dict(header="Actual", key="actual", width=11, style="money",
         validate=number_check(0, 1000000),
         note="Invoiced amount - the number the Campaigns tab reads."),
    dict(header="Notes", key="notes", width=26, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.budget() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Budget",
        subtitle="Planned against spent, month by month. The variance "
                 "column never lies - and the Campaigns tab reads Actual.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Month values use the drop down (Mar-26 style) so the "
                  "monthly totals below group correctly.",
        tab_color="#C98F5B", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Monthly totals - planned vs spent", LAST_COL)
    headers = ["Month", "Planned", "Spent", "Left"]
    for (c0, c1), head in zip([(0, 1), (2, 3), (4, 5), (6, 7)], headers):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    sheet.merge(row, 8, LAST_COL, "Spend share", fmts.chrome("header"))
    row += 1
    months = cfg.MONTHS
    months_col = f"$B${first}:$B${last}"
    for month in months:
        fmt_label = fmts.cell("text", "plain")
        fmt_money = fmts.cell("money", "calc")
        sheet.merge(row, 0, 1, month, fmt_label)
        pairs = [("C", "G"), ("E", "H"), ("G", "I")]
        for (c0, c1), letter in zip([(2, 3), (4, 5), (6, 7)],
                                    ["G", "H", "I"]):
            sheet.merge(row, c0, c1, "", fmt_money)
            formula = (f"=SUMIFS(${letter}${first}:${letter}${last},"
                       f"{months_col},$A{row + 1})")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula),
                                   fmt_money)
        sheet.merge(row, 8, LAST_COL, "", fmts.cell("percent", "calc"))
        share = (f"=IF(SUM($H${first}:$H${last})=0,0,SUMIFS($H${first}:"
                 f"$H${last},{months_col},$A{row + 1})/SUM($H${first}:"
                 f"$H${last}))")
        sheet.ws.write_formula(row, 8, sheet.reg.render(share),
                               fmts.cell("percent", "calc"))
        row += 1

    # Total row - sits after the loop, never over a data row.
    fmt_total_label = fmts.chrome("total_label")
    fmt_total = fmts.chrome("total_value")
    sheet.merge(row, 0, 1, "TOTAL", fmt_total_label)
    for (c0, c1), letter in zip([(2, 3), (4, 5), (6, 7)],
                                ["G", "H", "I"]):
        sheet.merge(row, c0, c1, "", fmt_total)
        sheet.ws.write_formula(row, c0,
                               sheet.reg.render(f"=SUM(${letter}${first}:"
                                                f"${letter}${last})"),
                               fmt_total)
    sheet.merge(row, 8, LAST_COL, "", fmt_total)
    row += 1

    row += 1
    row = sheet.section(row, "Category share of spend", LAST_COL)
    for offset, category in enumerate(
            ["Paid Ads", "Influencers", "Design & Tools", "Photo & Video",
             "Market Costs", "Promotions"]):
        fmt_label = fmts.cell("text", "plain")
        fmt_money = fmts.cell("money", "calc")
        fmt_pct = fmts.cell("percent", "calc")
        sheet.merge(row, 0, 2, category, fmt_label)
        sheet.merge(row, 3, 4, "", fmt_money)
        formula = (f"=SUMIFS($H${first}:$H${last},$C${first}:$C${last},"
                   f"$A{row + 1})")
        sheet.ws.write_formula(row, 3, sheet.reg.render(formula), fmt_money)
        sheet.merge(row, 5, 6, "", fmt_pct)
        formula = (f"=IF(SUM($H${first}:$H${last})=0,0,$D{row + 1}/SUM("
                   f"$H${first}:$H${last}))")
        sheet.ws.write_formula(row, 5, sheet.reg.render(formula), fmt_pct)
        row += 1
