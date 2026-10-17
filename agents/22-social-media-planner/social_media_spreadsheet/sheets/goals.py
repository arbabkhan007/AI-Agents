"""Register: Goals, with progress math."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Goals"
ROWS = 30

COLUMNS = [
    dict(header="Goal ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"G-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Goal", key="name", width=28, style="wrap",
         note="One measurable sentence."),
    dict(header="Metric", key="metric", width=14,
         note="The number you will watch."),
    dict(header="Baseline", key="start", width=11, style="number",
         validate=number_check(0, 100000000)),
    dict(header="Target", key="target", width=11, style="number",
         validate=number_check(0, 100000000)),
    dict(header="Current", key="current", width=11, style="number",
         validate=number_check(0, 100000000),
         note="Update this as the weeks pass."),
    dict(header="Progress", key="progress", width=11, style="percent",
         is_formula=True,
         formula="=IF($E{r}=$D{r},IF($F{r}>=$E{r},1,0),"
                 "MIN(1,MAX(0,($F{r}-$D{r})/($E{r}-$D{r}))))",
         note="Progress from baseline to target."),
    dict(header="Deadline", key="deadline", width=12, style="date",
         validate=date_check()),
    dict(header="Days Left", key="days_left", width=10, style="int",
         is_formula=True,
         formula="=IF($H{r}=\"\",\"\",MAX(0,$H{r}-Report_Date))",
         note="Days until the deadline."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Active", "Achieved", "At Risk", "Paused",
                              "Dropped"]}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Sort Key", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",(1-$G{r})*100000+{r}*0.000001)"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.goals() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Goals",
        subtitle="What this whole machine is for. Baseline, target, "
                 "deadline - and an honest Current column.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Progress and Days Left are calculated. A goal without a "
                  "baseline number is a wish.",
        tab_color="#C98F5B", freeze_cols=2)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Goals furthest behind - fix these first", 11)
    for (c0, c1), head in zip([(0, 3), (4, 6), (7, 8), (9, 11)],
                              ["Goal", "Progress", "Days left", "Status"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(max(len(spec_obj.samples), 5)):
        fmt_label = fmts.cell("text", "calc")
        fmt_pct = fmts.cell("percent", "calc")
        fmt_int = fmts.cell("int", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($M${first}:$M${last},{n}),"
            "$M${first}:$M${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 6), "G", fmt_pct),
                                      ((7, 8), "I", fmt_int),
                                      ((9, 11), "K", fmt_label)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
