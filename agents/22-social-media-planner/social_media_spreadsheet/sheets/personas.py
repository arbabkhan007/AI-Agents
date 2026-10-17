"""Register: Audience Personas."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last

NAME = "Audience Personas"
ROWS = 25

COLUMNS = [
    dict(header="Persona ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"PER-\"&TEXT({r}-{first}+1,\"000\"))",
         note="Calculated from the row position."),
    dict(header="Name", key="name", width=22,
         note="A nickname you will actually remember."),
    dict(header="Age Range", key="age", width=11,
         note="Example: 28-38."),
    dict(header="Location", key="location", width=18,
         note="Where they live or work."),
    dict(header="Values", key="values", width=28, style="wrap",
         note="What they care about beyond the product."),
    dict(header="Problems / Needs", key="problems", width=32, style="wrap",
         note="The problem your content solves for them."),
    dict(header="Preferred Platforms", key="platforms", width=22,
         style="wrap", note="Where to reach them."),
    dict(header="Content They Love", key="content", width=26, style="wrap",
         note="Formats and topics that earn attention."),
    dict(header="Quote", key="quote", width=30, style="wrap",
         note="A sentence in their own words."),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list",
                   "source": ["Active", "Draft", "Archived"]},
         note="Active while this persona drives planning."),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="Buying triggers, seasonality, anything useful."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.personas() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    for entry in samples:
        entry.setdefault("status", "Active")
    return SheetSpec(
        name=NAME, title="Audience Personas",
        subtitle="The people you make content for. Write them like real "
                 "people - campaigns are planned against these rows.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Five good personas beat twenty vague ones. The Audience "
                  "Notes column on the Reports tab quotes these rows.",
        tab_color="#C98F5B", freeze_cols=2)
