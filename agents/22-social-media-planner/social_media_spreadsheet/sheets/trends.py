"""Register: Trends, with an adoption board."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "Trends"
ROWS = 60
LAST_COL = 10

COLUMNS = [
    dict(header="Trend ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"TR-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Trend / Format", key="name", width=24,
         note="The trend as people search it."),
    dict(header="Platform", key="platform", width=14,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Format", key="format", width=13,
         validate={"validate": "list", "source": "=FormatList"}),
    dict(header="Sound / Audio", key="audio", width=16,
         note="Trending audio, or 'Original'."),
    dict(header="Why It Fits", key="why", width=30, style="wrap",
         note="Why this trend belongs to your brand."),
    dict(header="Fit", key="fit", width=9,
         validate={"validate": "list", "source": "=ImpactList"},
         note="High / Medium / Low fit for your brand."),
    dict(header="Date Spotted", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list",
                   "source": ["Watching", "Trying", "Evergreen", "Passed"]}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Sort Key", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",IF($I{r}=\"Evergreen\",2,IF($I{r}="
                 "\"Trying\",1,0))*100000+({r})*0.000001)"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.trends() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Trends",
        subtitle="What is moving right now, and whether it is worth your "
                 "voice. Trying beats watching - but only when it fits.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Fit decides whether you jump in. Evergreen trends are "
                  "formats you can use any week.",
        tab_color="#B0B0A8", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Adoption board - trying first, evergreen next",
                        LAST_COL)
    for (c0, c1), head in zip([(0, 2), (3, 4), (5, 6), (7, LAST_COL)],
                              ["Trend", "Platform", "Status", "Why it fits"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(max(len(spec_obj.samples), 5)):
        fmt_label = fmts.cell("text", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($K${first}:$K${last},{n}),"
            "$K${first}:$K${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        sheet.merge(row, 0, 2, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter in (((3, 4), "C"), ((5, 6), "I"),
                                 ((7, LAST_COL), "F")):
            sheet.merge(row, c0, c1, "", fmt_label)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula),
                                   fmt_label)
        row += 1
