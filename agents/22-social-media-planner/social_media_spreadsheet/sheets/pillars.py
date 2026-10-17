"""Register: Content Pillars, with a live share-of-voice breakdown."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, col_letter, rows_to_last
from ..writer import number_check

NAME = "Content Pillars"
ROWS = 12
LAST_COL = 15         # P: live totals
HELPERS = "O:P"       # helper keys for the pillar ranking

COLUMNS = [
    dict(header="Pillar Name", key="name", width=24,
         note="Short and memorable - it appears in drop downs."),
    dict(header="Purpose / Goal", key="goal", width=24,
         note="What this pillar is meant to achieve."),
    dict(header="Formats", key="formats", width=22, style="wrap",
         note="Best formats for this pillar."),
    dict(header="Tone / Voice", key="voice", width=18,
         note="One line on how it should sound."),
    dict(header="Share of Calendar", key="share", width=12, style="percent",
         validate=number_check(0, 1),
         note="Target share of your content mix. The dashboard compares "
              "this with what you actually published."),
    dict(header="Example Topics", key="examples", width=32, style="wrap",
         note="Three to five topic seeds."),
    dict(header="Preferred Platforms", key="platforms", width=24,
         style="wrap", note="Where this pillar belongs."),
    dict(header="Notes", key="notes", width=26, style="wrap"),
    dict(header="Active Posts", key="active_posts", width=11, style="int",
         is_formula=True,
         formula="=COUNTIFS([[Content Calendar.pillar]],$A{r},"
                 "[[Content Calendar.status]],\"<>Posted\")",
         note="Planned but not yet posted."),
    dict(header="Posted (period)", key="posted", width=11, style="int",
         is_formula=True,
         formula="=COUNTIFS([[Content Calendar.pillar]],$A{r},"
                 "[[Content Calendar.status]],\"Posted\")",
         note="Posted rows in the Content Calendar."),
    dict(header="Total Planned", key="total", width=11, style="int",
         is_formula=True,
         formula="=COUNTIF([[Content Calendar.pillar]],$A{r})",
         note="Every calendar row for this pillar."),
    dict(header="Actual Share", key="actual_share", width=11,
         style="percent", is_formula=True,
         formula="=IF(COUNTA([[Content Calendar.pillar]])=0,0,"
                 "$J{r}/COUNTA([[Content Calendar.pillar]]))",
         note="Share of the whole calendar, calculated live."),
    dict(header="Avg Engagement", key="avg_eng", width=12, style="percent",
         is_formula=True,
         formula="=IF($K{r}=0,0,AVERAGEIF([[Performance.pillar]],$A{r},"
                 "[[Performance.engagement_rate]]))",
         note="Average engagement rate of posts in this pillar."),
    dict(header="Vs Target", key="vs_target", width=12, style="int",
         is_formula=True,
         formula="=IF($E{r}=0,0,$J{r}-ROUND($E{r}*COUNTA("
                 "[[Content Calendar.pillar]]),0))",
         note="Posts above (+) or below (-) your target mix."),
    dict(header="Helper", key="helper_key", width=8, hidden=True,
         is_formula=True, formula="=IF($A{r}=\"\",0,{r})"),
    dict(header="Share Rank", key="rank_key", width=8, hidden=True,
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",RANK($L{r},$L$first:$L$last))",
         note="Ranking helper for the pillar summary."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.pillars() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Content Pillars",
        subtitle="The 4-8 themes everything you post hangs on. Keep the mix "
                 "honest - the columns at the right compare plan with reality.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Set the Share of Calendar you want, then watch the "
                  "Actual Share column after a few weeks of posting.",
        tab_color="#C98F5B", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    """Live share-of-voice table under the register."""
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Share of voice - live from the Content Calendar",
                        LAST_COL)
    headers = ["Pillar", "Target share", "Planned", "Posted", "Actual share",
               "Vs target"]
    widths_span = [(0, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]
    for (c0, c1), head in zip(widths_span, headers):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    sheet.row_height(row, 24)
    row += 1

    summary_last = row + len(spec_obj.samples) - 1 if spec_obj.samples \
        else row + 5
    for offset in range(max(len(spec_obj.samples), 6)):
        src = first + offset
        fmt_label = fmts.cell("text", "calc")
        fmt_pct = fmts.cell("percent", "calc")
        fmt_int = fmts.cell("int", "calc")
        # rank-th pillar name via SMALL on the hidden helper keys
        name_formula = (
            "=IFERROR(INDEX($A${first}:$A${last},"
            "MATCH(SMALL($O${first}:$O${last},{n}),"
            "$O${first}:$O${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        sheet.merge(row, 0, 2, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), col_letter_src, fmt in (
                ((3, 4), "E", fmt_pct), ((5, 6), "K", fmt_int),
                ((7, 8), "J", fmt_int), ((9, 10), "L", fmt_pct),
                ((11, 12), "N", fmt_int)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${col_letter_src}"
                       f"${first}:${col_letter_src}${last},"
                       f"MATCH($A{row + 1},$A${first}:$A${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1

    row += 1
    sheet.merge(row, 0, 12,
                "Shares are calculated from the Content Calendar, so they "
                "move as you plan. If one pillar drifts far below its "
                "target, that is your next idea session.",
                fmts.chrome("note"))
    sheet.row_height(row, 26)
