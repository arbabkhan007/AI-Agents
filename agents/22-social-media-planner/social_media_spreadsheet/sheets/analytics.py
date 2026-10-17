"""Register: Analytics - the weekly pulse numbers everything else reads."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Analytics"
ROWS = 400

COLUMNS = [
    dict(header="Date", key="date", width=12, style="date",
         validate=date_check(),
         note="Week ending, or the day you pulled the numbers."),
    dict(header="Reach", key="reach", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Impressions", key="impressions", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Likes", key="likes", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Comments", key="comments", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Saves", key="saves", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Shares", key="shares", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Engagement Rate", key="engagement_rate", width=12,
         style="percent", is_formula=True,
         formula="=IF($B{r}=\"\",\"\",IF($B{r}=0,0,($D{r}+$E{r}+$F{r}+"
                 "$G{r})/$B{r}))",
         note="(Likes + comments + saves + shares) / reach."),
    dict(header="Best Day", key="best_day", width=12, style="date",
         is_formula=True,
         formula="=IF($H{r}=\"\",\"\",INDEX($A$first:$A$last,"
                 "MATCH(MAX($H$first:$H$last),$H$first:$H$last,0)))",
         note="Best engagement day in the whole table."),
    dict(header="Eng Key", key="eng_key", width=10, hidden=True,
         is_formula=True,
         formula="=IF($H{r}=\"\",\"\",$H{r}+{r}*0.000001)",
         note="Tie breaker for the best day lookup."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.analytics() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Analytics",
        subtitle="The pulse: weekly reach and engagement totals. Everything "
                 "on the dashboards grows from these numbers.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Log the numbers once a week. Engagement Rate and Best "
                  "Day calculate themselves; Best Day searches the whole "
                  "table.",
        tab_color="#2E7D8F", freeze_cols=1)
