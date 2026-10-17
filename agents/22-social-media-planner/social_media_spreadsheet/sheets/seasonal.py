"""Register: Seasonal Planner, with a moments timeline."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "Seasonal Planner"
ROWS = 40
LAST_COL = 10

COLUMNS = [
    dict(header="Moment ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"SEAS-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Name", key="name", width=24,
         note="Holiday, moment or cultural date."),
    dict(header="Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Planning Window", key="window", width=16,
         note="When content for this moment should be made."),
    dict(header="Angle", key="angle", width=28, style="wrap",
         note="Your take - not the generic one."),
    dict(header="Content Ideas", key="offer", width=24, style="wrap",
         note="Offer, hook or content angle."),
    dict(header="Goal", key="goal", width=11,
         validate={"validate": "list", "source": "=GoalList"}),
    dict(header="Platforms", key="platforms", width=20, style="wrap"),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Idea", "Planned", "In Progress", "Live",
                              "Done"]}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Sort Key", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($C{r}=\"\",\"\",IF($C{r}<Report_Date,999999,"
                 "$C{r}+{r}*0.000001))",
         note="Upcoming dates sort first; ties broken by row."),
    dict(header="Days Out", key="days_out", width=10, style="int",
         is_formula=True,
         formula="=IF($C{r}=\"\",\"\",$C{r}-Report_Date)",
         note="Days until the moment."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.seasonal() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    for entry in samples:
        entry.setdefault("status", "Idea")
    return SheetSpec(
        name=NAME, title="Seasonal Planner",
        subtitle="The dates your year turns on. Plan the window, not just "
                 "the day - content for a moment ships two weeks early.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Days Out counts to each moment from the planning date on "
                  "the Settings tab.",
        tab_color="#B0B0A8", freeze_cols=2)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Moments timeline - next up", LAST_COL)
    for (c0, c1), head in zip([(0, 3), (4, 5), (6, 7), (8, 10)],
                              ["Moment", "Date", "Days out", "Goal"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(max(len(spec_obj.samples), 5)):
        fmt_label = fmts.cell("text", "calc")
        fmt_date = fmts.cell("date", "calc")
        fmt_int = fmts.cell("int", "calc")
        fmt_text = fmts.cell("text", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($K${first}:$K${last},{n}),"
            "$K${first}:$K${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 5), "C", fmt_date),
                                      ((6, 7), "L", fmt_int),
                                      ((8, 10), "G", fmt_text)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
