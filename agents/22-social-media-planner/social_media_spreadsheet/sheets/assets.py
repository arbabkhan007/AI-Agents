"""Register: Assets."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import yes_no

NAME = "Assets"
ROWS = 250

COLUMNS = [
    dict(header="Asset ID", key="id", width=11,
         validate={"validate": "list",
                   "source": ["AST-001", "AST-002", "AST-003", "AST-004",
                              "AST-005", "AST-006", "AST-007", "AST-008",
                              "AST-009", "AST-010", "AST-011", "AST-012"]},
         note="Your own numbering, e.g. AST-001."),
    dict(header="Title", key="title", width=28, style="wrap",
         note="What the asset is."),
    dict(header="Type", key="type", width=11,
         validate={"validate": "list", "source": "=ContentTypeList"},
         note="Image, video, carousel, template..."),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"}),
    dict(header="Platforms", key="platforms", width=20, style="wrap"),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Idea", "Draft", "Ready", "In Use",
                              "Archived"]}),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Link / Path", key="url", width=26, style="link",
         note="Where the file lives."),
    dict(header="Rights", key="rights", width=18,
         validate={"validate": "list",
                   "source": ["Owned", "Licensed - repost",
                              "Licensed - repost + paid", "Expiring",
                              "Unverified"]},
         note="Rights status. Unverified means do not post."),
    dict(header="Notes", key="notes", width=26, style="wrap"),
    dict(header="Usage Count", key="usage", width=11, style="int",
         is_formula=True,
         formula="=COUNTIF([[Content Calendar.asset]],$A{r})",
         note="Calendar rows pointing at this asset."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.assets() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Assets",
        subtitle="Every image, clip, template and file, with its rights. "
                 "If it is not here, it does not exist.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Usage Count shows which assets pull their weight. "
                  "Rights travel with the file - when in doubt, do not post.",
        tab_color="#B0B0A8", freeze_cols=1)
