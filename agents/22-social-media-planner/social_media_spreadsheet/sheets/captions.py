"""Register: Caption Bank."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last

NAME = "Caption Bank"
ROWS = 300

COLUMNS = [
    dict(header="Caption ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"CAP-\"&TEXT({r}-{first}+1,\"000\"))",
         note="Calculated from row order."),
    dict(header="Title", key="title", width=26,
         note="What this caption is for."),
    dict(header="Hook", key="hook", width=32, style="wrap",
         note="The first line. It earns the tap on 'more'."),
    dict(header="Caption Body", key="body", width=56, style="wrap",
         note="The body text. Keep it in your brand voice."),
    dict(header="CTA", key="cta", width=26, style="wrap",
         note="The next step you want the reader to take."),
    dict(header="Emoji / Tone", key="emote", width=16,
         note="Tone tags, e.g. warm, playful."),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"},
         note="Which pillar it serves."),
    dict(header="Platforms", key="platforms", width=18, style="wrap",
         note="Where it works best."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Draft", "Approved", "Archived"]},
         note="Approved captions are safe to schedule."),
    dict(header="Used", key="used", width=9, style="int",
         is_formula=True,
         formula="=COUNTIF([[Content Calendar.caption_ref]],$A{r})",
         note="How many calendar rows use this caption."),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="Variants, translations, anything useful."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.caption_bank() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Caption Bank",
        subtitle="Your reusable words. Write once, approve once, schedule "
                 "anywhere - the calendar tracks where each one lands.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Caption IDs (CAP-001) appear in the Content Calendar's "
                  "Caption Ref column. The Used column counts them live.",
        tab_color="#7A9E7E", freeze_cols=2)
