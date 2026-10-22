"""10 Payroll & Tips - hours, tips, employer cost and period summaries."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import date_check, list_from, number_check
from .. import sample_data

NAME = "10 Payroll & Tips"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="10  Payroll & Tips",
        subtitle="Hours, tips in and out, employer-side reserve and the "
                 "true cost of each pay line.",
        tab_color="#6D2E4F",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="One row per pay line. Period is your own label, e.g. "
                  "2026-10 H1 - the summary block below totals by period.",
        columns=[
            Col("id", "Pay ID", 10, "id",
                formula='="R-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("period", "Period", 12, "text",
                note="Any label: 2026-10 H1, Week 42, October."),
            Col("date", "Pay date", 12, "date", validate=date_check()),
            Col("staff", "Staff", 20, "text",
                validate=list_from("StaffNames")),
            Col("hours", "Hours", 8, "number1",
                validate=number_check(0, 200, False)),
            Col("rate", "Rate", 9, "money",
                formula='IF({staff}{r}="","",IFERROR(INDEX(StaffHourly,'
                        'MATCH({staff}{r},StaffNames,0)),""))'),
            Col("gross", "Gross pay", 11, "money",
                formula='IF({hours}{r}="","",ROUND(N({hours}{r})'
                        '*N({rate}{r}),2))'),
            Col("tips_in", "Tips in", 10, "money",
                validate=number_check(0, 100000),
                note="Tips received by the team for this period."),
            Col("tips_out", "Tips paid out", 11, "money",
                validate=number_check(0, 100000),
                note="What you passed on. The difference stays in the "
                     "business and shows in the cost column."),
            Col("employer_tax", "Employer reserve", 12, "money",
                formula='IF({gross}{r}="","",ROUND(N({gross}{r})*'
                        'PayrollTaxRate,2))',
                note="Gross x the employer-side rate from Settings."),
            Col("total_cost", "Total cost", 11, "money",
                formula='IF({gross}{r}="","",ROUND(N({gross}{r})'
                        '+N({employer_tax}{r})+N({tips_in}{r})'
                        '-N({tips_out}{r}),2))'),
            Col("notes", "Adjustments & approvals", 30, "wrap",
                note="Manual adjustments: who approved them and why."),
        ],
        samples=sample_data.payroll_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Tips are tracked in and out so the P&L only carries what the "
            "business actually keeps.",
            "This tab records payroll; it is not payroll software or tax "
            "advice - confirm rates with your accountant.",
        ],
    )


def decorate(sheet, fmts, cfg, reg) -> None:
    spec_ = reg[NAME]
    row = spec_.last_data_row + 2
    last = spec_.last_col_index
    sheet.section(row, "PAYROLL PERIOD SUMMARY", last)
    row += 1
    heads = ["Period", "Hours", "Gross pay", "Tips in", "Tips paid out",
             "Employer reserve", "Total cost"]
    sheet.table_head(row, 0, heads)
    periods = sorted({s["period"] for s in spec_.samples
                      if s.get("period")}) or ["2026-10 H1"]
    for i, p in enumerate(periods[:12]):
        r = row + 1 + i
        sheet.write(r, 0, p, sheet.f.calc("text"))
        for c, key in enumerate(["hours", "gross", "tips_in", "tips_out",
                                 "employer_tax", "total_cost"], start=1):
            letter = spec_.letter(key)
            rng = f"${letter}${spec_.first_data_row}:${letter}${spec_.last_data_row}"
            sheet.formula(
                r, c,
                f'=IF(SUMIF($A${spec_.first_data_row}:'
                f'$A${spec_.last_data_row},"{p}",{rng})=0,"",'
                f'ROUND(SUMIF($A${spec_.first_data_row}:'
                f'$A${spec_.last_data_row},"{p}",{rng}),2))',
                sheet.f.calc("number1" if key == "hours" else "money"))
    sheet.note(row + len(periods[:12]) + 2,
               "Add a row per period label you use - copy the formulas "
               "down and the summary follows.", last)
