"""Register: Tasks, with a next-up queue."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "Tasks"
ROWS = 200
LAST_COL = 10

COLUMNS = [
    dict(header="Task ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"T-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Task", key="task", width=36, style="wrap",
         note="Start with a verb. 'Write the drop email', not 'email'."),
    dict(header="Content ID", key="content_id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Optional link to a calendar row."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Due Date", key="due", width=12, style="date",
         validate=date_check()),
    dict(header="Days Left", key="days_left", width=10, style="int",
         is_formula=True,
         formula="=IF($E{r}=\"\",\"\",$E{r}-Report_Date)",
         note="Negative means overdue."),
    dict(header="Priority", key="priority", width=11,
         validate={"validate": "list", "source": "=PriorityList"}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=TaskStatusList"}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Due Flag", key="due_flag", width=12,
         is_formula=True,
         formula="=IF($E{r}=\"\",\"\",IF($H{r}=\"Done\",\"Done\","
                 "IF($E{r}<Report_Date,\"Overdue\",\"Open\")))",
         note="Overdue / Open / Done."),
    dict(header="Due Key", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($E{r}=\"\",\"\",IF($H{r}=\"Done\",999999,"
                 "$E{r}+{r}*0.000001))"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.tasks() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Tasks",
        subtitle="The production line behind the calendar. Owners and due "
                 "dates, with an overdue flag that does not negotiate.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Days Left counts from the planning date on Settings. "
                  "Content ID links a task to its post.",
        tab_color="#B0B0A8", freeze_cols=2)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Next up - due soonest, done last", LAST_COL)
    for (c0, c1), head in zip([(0, 3), (4, 5), (6, 7), (8, LAST_COL)],
                              ["Task", "Due", "Owner", "Flag"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(8):
        fmt_label = fmts.cell("text", "calc")
        fmt_date = fmts.cell("date", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($K${first}:$K${last},{n}),"
            "$K${first}:$K${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 5), "E", fmt_date),
                                      ((6, 7), "D", fmt_label),
                                      ((8, LAST_COL), "J", fmt_label)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
