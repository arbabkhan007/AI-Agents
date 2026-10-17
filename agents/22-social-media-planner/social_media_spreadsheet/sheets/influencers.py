"""Register: Influencers."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Influencers"
ROWS = 40

COLUMNS = [
    dict(header="Influencer ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"INF-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Name", key="name", width=22,
         note="Person or brand name."),
    dict(header="Handle", key="handle", width=18),
    dict(header="Platform", key="platform", width=12,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Followers", key="followers", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Niche", key="niche", width=20, style="wrap"),
    dict(header="Contact", key="contact", width=22),
    dict(header="Rate / Fee", key="rate", width=11, style="money",
         validate=number_check(0, 100000),
         note="0 means trade or contra deal."),
    dict(header="Deliverables", key="deliverables", width=20, style="wrap"),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=OutreachStatusList"},
         note="From Prospect to Completed."),
    dict(header="Due Date", key="due", width=12, style="date",
         validate=date_check()),
    dict(header="Performance", key="performance", width=18, style="wrap",
         note="What the last collaboration actually did."),
    dict(header="Notes", key="notes", width=26, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.influencers() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Influencers",
        subtitle="Collaborations tracked like campaigns: who, what, when, "
                 "what it cost and what it returned.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Rate 0 means a contra deal. Log the real performance in "
                  "the Performance column - it is the only way to spot the "
                  "partners worth repeating.",
        tab_color="#C98F5B", freeze_cols=2)
