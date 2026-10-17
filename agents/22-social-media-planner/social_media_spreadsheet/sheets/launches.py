"""Register: Launch Planner, with a countdown dashboard."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Launch Planner"
ROWS = 25
LAST_COL = 14

COLUMNS = [
    dict(header="Launch ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"LNCH-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Product / Drop", key="product", width=26,
         note="What is launching."),
    dict(header="Category", key="category", width=14),
    dict(header="Launch Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Countdown", key="days", width=11, style="int",
         is_formula=True,
         formula="=IF($D{r}=\"\",\"\",$D{r}-Report_Date)",
         note="Days until launch - negative means it shipped."),
    dict(header="Goal", key="goal", width=11,
         validate={"validate": "list", "source": "=GoalList"}),
    dict(header="Target Audience", key="audience", width=18,
         note="Persona names."),
    dict(header="Offer / Bundle", key="offer", width=20, style="wrap"),
    dict(header="Content Plan Ready", key="platforms", width=22,
         style="wrap", note="Platforms and formats planned."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list",
                   "source": ["Idea", "Planned", "In Production", "Active",
                              "Shipped", "Cancelled"]}),
    dict(header="Teaser Rows", key="teasers", width=10, style="int",
         is_formula=True,
         formula="=COUNTIFS([[Content Calendar.campaign]],$B{r},"
                 "[[Content Calendar.date]],\"<\"&$D{r})",
         note="Calendar rows dated before launch day."),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Countdown Rank", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",IF($E{r}=\"\",99999+{r}*0.000001,"
                 "ABS($E{r})+{r}*0.000001))"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.launches() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Launch Planner",
        subtitle="Every drop gets a date, a countdown and a teaser trail in "
                 "the calendar. Nothing launches by accident.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Countdown is live - negative numbers mean the drop has "
                  "passed. Teaser Rows counts calendar posts before launch "
                  "day.",
        tab_color="#C98F5B", freeze_cols=2)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Launch countdown board", LAST_COL)
    headers = ["Product", "Launch date", "Days", "Status"]
    spans = [(0, 3), (4, 5), (6, 7), (8, 11)]
    for (c0, c1), head in zip(spans, headers):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(max(len(spec_obj.samples), 5)):
        rank = offset + 1
        fmt_label = fmts.cell("text", "calc")
        fmt_date = fmts.cell("date", "calc")
        fmt_int = fmts.cell("int", "calc")
        fmt_text = fmts.cell("text", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($N${first}:$N${last},{n}),"
            "$N${first}:$N${last},0)),\"\")"
        ).format(first=first, last=last, n=rank)
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 5), "D", fmt_date),
                                      ((6, 7), "E", fmt_int),
                                      ((8, 11), "K", fmt_text)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
