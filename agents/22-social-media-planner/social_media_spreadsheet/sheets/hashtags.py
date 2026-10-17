"""Register: Hashtag Bank."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last

NAME = "Hashtag Bank"
ROWS = 120

COLUMNS = [
    dict(header="Hashtag Set ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"HT-\"&TEXT({r}-{first}+1,\"000\"))",
         note="Calculated from row order."),
    dict(header="Set Name", key="name", width=22,
         note="Name the set by its job, not its tags."),
    dict(header="Platform", key="platform", width=13,
         validate={"validate": "list", "source": "=PlatformList"},
         note="Where this set is tuned for."),
    dict(header="Hashtags", key="tags", width=56, style="wrap",
         note="Space separated. Branded tag first, then niche, then broad."),
    dict(header="Tag Count", key="tag_count", width=10, style="int",
         is_formula=True,
         formula="=IF($D{r}=\"\",0,LEN($D{r})-LEN(SUBSTITUTE($D{r},\"#\","
                 "\"\")))",
         note="Counts the # marks - watch platform limits."),
    dict(header="Size / Reach", key="size", width=12,
         validate={"validate": "list",
                   "source": ["Broad", "Medium", "Small", "Niche"]},
         note="How big the tag pool is."),
    dict(header="Use For", key="use_for", width=18,
         note="Pillar or situation this set belongs to."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Active", "Testing", "Archived"]},
         note="Retire sets that stop working."),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="What you learned from using it."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.hashtag_banks() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Hashtag Bank",
        subtitle="Sets of tags, kept short and tested. Rotate them instead "
                 "of pasting the same block every day.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Tag Count watches the platform limits for you. Use For "
                  "maps each set to a pillar so you never post a launch set "
                  "on a care tip.",
        tab_color="#7A9E7E", freeze_cols=1)
