"""Register: Competitors, with a gap-analysis summary."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Competitors"
ROWS = 25
LAST_COL = 10

COLUMNS = [
    dict(header="Competitor", key="name", width=22,
         note="Who you keep an eye on."),
    dict(header="Website / Handle", key="url", width=26, style="link"),
    dict(header="Platforms", key="platforms", width=20, style="wrap"),
    dict(header="Followers (est.)", key="followers", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Posting Cadence", key="cadence", width=14,
         note="How often they show up."),
    dict(header="Strength", key="strength", width=28, style="wrap",
         note="What they do better than anyone."),
    dict(header="Gap / Weakness", key="gap", width=28, style="wrap",
         note="Where your opening is."),
    dict(header="Top Keywords", key="keywords", width=20, style="wrap"),
    dict(header="Last Checked", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Notes", key="notes", width=26, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.competitors() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Competitors",
        subtitle="Not to copy - to learn from. Check quarterly, note the "
                 "gaps, and build where they are quiet.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="The Gap column is the only one that makes you money. "
                  "Read it before any planning session.",
        tab_color="#B0B0A8", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Gap analysis - top keywords in play", LAST_COL)
    for (c0, c1), head in zip([(0, 2), (3, 5), (6, LAST_COL)],
                              ["Competitor", "Their strength",
                               "Their gap (your opening)"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    n = max(len(spec_obj.samples), 4)
    for offset in range(n):
        src = first + offset
        fmt_label = fmts.cell("text", "calc")
        sheet.merge(row, 0, 2, "", fmt_label)
        sheet.merge(row, 3, 5, "", fmt_label)
        sheet.merge(row, 6, LAST_COL, "", fmt_label)
        sheet.ws.write_formula(
            row, 0,
            sheet.reg.render(f"=IF($A{src}=\"\",\"\",$A{src})"), fmt_label)
        sheet.ws.write_formula(
            row, 3,
            sheet.reg.render(f"=IF($A{src}=\"\",\"\",$F{src})"), fmt_label)
        sheet.ws.write_formula(
            row, 6,
            sheet.reg.render(f"=IF($A{src}=\"\",\"\",$G{src})"), fmt_label)
        row += 1
