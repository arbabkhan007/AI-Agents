"""Register: Team, with a workload summary."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import number_check

NAME = "Team"
ROWS = 25
LAST_COL = 8

COLUMNS = [
    dict(header="Name", key="name", width=20,
         note="Full name - appears in drop downs everywhere."),
    dict(header="Role", key="role", width=24,
         note="What they actually do."),
    dict(header="Email", key="email", width=24),
    dict(header="Initials", key="initials", width=9),
    dict(header="Capacity (hrs/week)", key="capacity", width=12,
         style="int", validate=number_check(0, 80, decimal=False)),
    dict(header="Responsibilities", key="responsibilities", width=32,
         style="wrap", note="Their lanes, in one line."),
    dict(header="Open Tasks", key="open_tasks", width=10, style="int",
         is_formula=True,
         formula="=COUNTIFS([[Tasks.owner]],$A{r},[[Tasks.status]],"
                 "\"<>Done\")",
         note="Live count of tasks not marked Done."),
    dict(header="Status", key="status", width=10,
         validate={"validate": "list",
                   "source": ["Active", "Away", "Paused", "Left"]}),
    dict(header="Notes", key="notes", width=26, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.team() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Team",
        subtitle="Who does what, and how much room they have. Open Tasks "
                 "counts the Tasks tab live.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Names you enter here appear in every Owner drop down.",
        tab_color="#B0B0A8", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Workload summary - live", LAST_COL)
    for (c0, c1), head in zip([(0, 1), (2, 3), (4, 5), (6, LAST_COL)],
                              ["Member", "Role", "Capacity",
                               "Open tasks"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(max(len(spec_obj.samples), 5)):
        src = first + offset
        fmt_label = fmts.cell("text", "calc")
        fmt_int = fmts.cell("int", "calc")
        sheet.merge(row, 0, 1, "", fmt_label)
        sheet.merge(row, 2, 3, "", fmt_label)
        sheet.merge(row, 4, 5, "", fmt_int)
        sheet.merge(row, 6, LAST_COL, "", fmt_int)
        for col, letter in ((0, "A"), (2, "B"), (4, "E"), (6, "G")):
            sheet.ws.write_formula(
                row, col,
                sheet.reg.render(f"=IF($A{src}=\"\",\"\",${letter}{src})"),
                fmt_int if col in (4, 6) else fmt_label)
        row += 1
