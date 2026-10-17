"""Register: Idea Bank."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Idea Bank"
ROWS = 300

COLUMNS = [
    dict(header="Idea ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"IDEA-\"&TEXT({r}-{first}+1,\"000\"))",
         note="Calculated from row order."),
    dict(header="Captured On", key="captured", width=12, style="date",
         validate=date_check(),
         note="When the idea arrived."),
    dict(header="Idea", key="idea", width=38, style="wrap",
         note="One line. If it needs two, it is two ideas."),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"},
         note="Which pillar it serves."),
    dict(header="Format", key="format", width=12,
         validate={"validate": "list", "source": "=FormatList"},
         note="Best format for the idea."),
    dict(header="Platform", key="platform", width=13,
         validate={"validate": "list", "source": "=PlatformList"},
         note="Where it would live."),
    dict(header="Effort", key="effort", width=10,
         validate={"validate": "list", "source": "=EffortList"},
         note="How much work it takes."),
    dict(header="Impact", key="impact", width=10,
         validate={"validate": "list", "source": "=ImpactList"},
         note="How much it could move the needle."),
    dict(header="Score", key="score", width=9, style="rating",
         is_formula=True,
         formula="=IF(OR($G{r}=\"\",$H{r}=\"\"),\"\","
                 "IF($H{r}=\"High\",3,IF($H{r}=\"Medium\",2,1))*2"
                 "+IF($G{r}=\"Low\",2,IF($G{r}=\"Medium\",1,0)))",
         note="Impact x effort score, calculated."),
    dict(header="Status", key="status", width=13,
         validate={"validate": "list",
                   "source": ["Captured", "Planned", "In Calendar",
                              "Published", "Parked"]},
         note="Captured until it becomes a calendar row."),
    dict(header="Content Ref", key="ref", width=12,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Content ID once scheduled."),
    dict(header="Notes", key="notes", width=30, style="wrap",
         note="Why it is worth making."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.idea_bank() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Idea Bank",
        subtitle="Catch ideas before they escape. Score them honestly and "
                 "promote the good ones straight into the calendar.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Idea ID calculates itself. Content Ref links the idea to "
                  "a Content Calendar row once it is scheduled.",
        tab_color="#7A9E7E", freeze_cols=1)
