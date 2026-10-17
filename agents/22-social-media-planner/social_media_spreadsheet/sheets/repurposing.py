"""Register: Repurposing."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "Repurposing"
ROWS = 150

COLUMNS = [
    dict(header="Source Content ID", key="source", width=13,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="The original piece."),
    dict(header="Source Title", key="title", width=30, style="wrap"),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"}),
    dict(header="Original Format", key="from", width=16,
         note="What it was first."),
    dict(header="New Format", key="to", width=18,
         validate={"validate": "list", "source": "=FormatList"},
         note="What it becomes."),
    dict(header="Platform", key="platform", width=13,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Scheduled Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list",
                   "source": ["Idea", "Planned", "In Progress", "Done",
                              "Skipped"]}),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="What to cut, crop or rewrite."),
    dict(header="Per Source", key="per_source", width=10, style="int",
         is_formula=True,
         formula="=IF($A{r}=\"\",0,COUNTIF($A$first:$A$last,$A{r}))",
         note="How many new lives this piece already has."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.repurposing() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    for entry in samples:
        entry.setdefault("platform", "")
    return SheetSpec(
        name=NAME, title="Repurposing",
        subtitle="One idea, many lives. Track every cut-down, crop and "
                 "rewrite so good work keeps working.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="If a piece of content worked once, it earns a second "
                  "life here. Per Source counts how stretched each idea is.",
        tab_color="#7A9E7E", freeze_cols=1)
