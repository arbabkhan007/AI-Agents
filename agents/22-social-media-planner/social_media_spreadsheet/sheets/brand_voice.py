"""The `Brand Voice` tab: the voice of the whole content machine."""

from __future__ import annotations

from ..layout import SheetSpec
from ..writer import SheetWriter, list_from, yes_no
from .. import sample_data

NAME = "Brand Voice"
LAST_COL = 5

COLUMNS = [
    dict(header="Voice Attribute", key="attribute", width=20,
         note="One word for how the brand should sound."),
    dict(header="Description", key="description", width=34,
         style="wrap",
         note="What this attribute means in practice."),
    dict(header="Example Line", key="example", width=32, style="wrap",
         note="A line you would actually post."),
    dict(header="Words To Avoid", key="avoid", width=26, style="wrap",
         note="The register of vocabulary to keep out."),
    dict(header="Editorial Checklist", key="checklist", width=32,
         style="wrap",
         note="Questions every caption should pass before it is scheduled."),
    dict(header="Notes", key="notes", width=24, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.brand_voice() if cfg.include_sample_data else []
    for entry in samples:
        entry.setdefault("checklist",
                         "Would Jordan say this out loud?")
        entry.setdefault("notes", "")
    return SheetSpec(
        name=NAME, title="Brand Voice",
        subtitle="How Wildflower sounds, in one page. When a caption feels "
                 "off, it starts here.",
        columns=COLUMNS, rows=cfg.row_count(NAME) or 24, samples=samples,
        first_data_row=8, last_data_row=7 + cfg.row_count(NAME) or 24,
        help_text="Four attributes, one example each, and the words we do "
                  "not use. Copy this into any AI prompt or brief.",
        tab_color="#C98F5B", freeze_cols=1)


def build(book, fmts, cfg, reg) -> SheetWriter:
    from ..writer import SheetWriter as SW
    sheet = SW(book, fmts, cfg, reg, NAME, tab_color="#C98F5B")
    f = sheet.f
    sheet.banner(
        "Brand Voice Guide",
        "The voice behind every caption, email and script. Four words, "
        "with examples and a pre-publish checklist.",
        LAST_COL)

    sheet.set_col(0, 0, 20)
    sheet.set_col(1, 1, 34)
    sheet.set_col(2, 2, 32)
    sheet.set_col(3, 3, 26)
    sheet.set_col(4, 4, 32)
    sheet.set_col(5, LAST_COL, 24)

    row = 4
    row = sheet.section(row, "Voice attributes", LAST_COL)
    header_row = row
    for i, col in enumerate(COLUMNS):
        sheet.write(row, i, col["header"], f.chrome("header_left" if i == 0
                                                    else "header"))
    sheet.row_height(row, 26)
    row += 1

    samples = sample_data.brand_voice() if cfg.include_sample_data else []
    style = ["text", "wrap", "wrap", "wrap", "wrap", "wrap"]
    for offset in range(cfg.row_count(NAME) or 24):
        entry = samples[offset] if offset < len(samples) else {}
        values = [entry.get(c["key"]) for c in COLUMNS]
        if any(v is not None for v in values):
            for i, value in enumerate(values):
                if value is not None:
                    sheet.write(row, i, value, f.cell(style[i], "input"))
        else:
            for i in range(len(COLUMNS)):
                sheet.write(row, i, None, f.cell(style[i], "input"))
        row += 1

    last_data = row - 1
    sheet.ws.autofilter(header_row, 0, last_data, LAST_COL)

    row += 1
    row = sheet.section(row, "Editorial checklist", LAST_COL)
    checks = [
        "Does it sound like a person who makes things with her hands?",
        "Is the first line worth stopping for?",
        "One idea per post - did we cut the second one?",
        "Is there a clear next step for the reader?",
        "Any words from the avoid list? Cut them.",
        "Would we be happy if the maker saw this? (We are the maker.)",
    ]
    for i, check in enumerate(checks, start=1):
        sheet.merge(row, 0, LAST_COL - 1, f"{i}.  {check}",
                    f.chrome("label"))
        sheet.write(row, LAST_COL, None, f.input("flag"),
                    )
        sheet.ws.data_validation(row, LAST_COL, row, LAST_COL,
                                 yes_no("Pass the check?"))
        row += 1

    row += 1
    row = sheet.note(
        row, "Tip: paste the four attributes into your AI prompts and the "
             "caption drafts will come back sounding like you.",
        LAST_COL, height=26)
    sheet.finish(freeze_row=header_row + 1,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row}")
    return sheet
