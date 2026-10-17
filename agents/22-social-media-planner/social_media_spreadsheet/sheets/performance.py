"""Register: Performance - per-post results, linked to the calendar."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Performance"
ROWS = 600

COLUMNS = [
    dict(header="Content ID", key="content_id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Must match a Content Calendar ID so the lookup columns "
              "fill in."),
    dict(header="Post Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Platform", key="platform", width=12,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Impressions", key="impressions", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Reach", key="reach", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Likes", key="likes", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Comments", key="comments", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Saves", key="saves", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Shares", key="shares", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Clicks", key="clicks", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Engagement Rate", key="engagement_rate", width=12,
         style="percent", is_formula=True,
         formula="=IF($A{r}=\"\",\"\",IF($E{r}=0,0,($F{r}+$G{r}+$H{r}+"
                 "$I{r})/$E{r}))",
         note="Engagements divided by reach."),
    dict(header="CTR", key="ctr", width=10, style="percent",
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",IF($D{r}=0,0,$J{r}/$D{r}))",
         note="Clicks divided by impressions."),
    dict(header="Est. Revenue", key="est_revenue", width=12, style="money",
         is_formula=True,
         formula="=IF($A{r}=\"\",0,$J{r}*Setting_AvgOrderValue)",
         note="Clicks x your average order value (Settings tab)."),
    dict(header="Pillar", key="pillar", width=16,
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",IFERROR(INDEX("
                 "[[Content Calendar.pillar]],MATCH($A{r},"
                 "[[Content Calendar.id]],0)),\"Unmatched\"))",
         note="Looked up from the Content Calendar."),
    dict(header="Caption Ref", key="caption_ref", width=11,
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",IFERROR(INDEX("
                 "[[Content Calendar.caption_ref]],MATCH($A{r},"
                 "[[Content Calendar.id]],0)),\"\"))",
         note="Which caption produced the result."),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="What you learned from this post."),
    dict(header="Rev Key", key="rank_key", width=10, hidden=True,
         is_formula=True,
         formula="=IF($A{r}=\"\",0,$M{r}+{r}*0.000001)"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.performance() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Performance",
        subtitle="Post by post, what actually happened. Enter the raw "
                 "numbers - the rates, revenue and pillar lookup are "
                 "automatic.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Content ID must match the Content Calendar. Est. Revenue "
                  "uses the average order value named on the Settings tab.",
        tab_color="#2E7D8F", freeze_cols=1)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Revenue leaders - live from the rows above",
                        14)
    for (c0, c1), head in zip([(0, 3), (4, 6), (7, 9), (10, 14)],
                              ["Content ID", "Pillar", "Est. revenue",
                               "Engagement"]):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    for offset in range(8):
        fmt_label = fmts.cell("text", "calc")
        fmt_money = fmts.cell("money", "calc")
        fmt_pct = fmts.cell("percent", "calc")
        name_formula = (
            "=IFERROR(INDEX($A${first}:$A${last},"
            "MATCH(SMALL($Q${first}:$Q${last},{n}),"
            "$Q${first}:$Q${last},0)),\"\")"
        ).format(first=first, last=last, n=offset + 1)
        # Descending: use LARGE on the unique rev key instead.
        name_formula = name_formula.replace("SMALL(", "LARGE(")
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 6), "N", fmt_label),
                                      ((7, 9), "M", fmt_money),
                                      ((10, 14), "K", fmt_pct)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$A${first}:"
                       f"$A${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
