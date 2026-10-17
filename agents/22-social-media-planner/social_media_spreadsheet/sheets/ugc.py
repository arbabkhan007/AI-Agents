"""Register: UGC Tracker."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check, yes_no

NAME = "UGC Tracker"
ROWS = 80

COLUMNS = [
    dict(header="UGC ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"UGC-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Creator", key="creator", width=20,
         note="Who made it."),
    dict(header="Platform", key="platform", width=12,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Type", key="type", width=11,
         validate={"validate": "list", "source": "=ContentTypeList"}),
    dict(header="Received", key="received", width=12, style="date",
         validate=date_check()),
    dict(header="Permission Status", key="permission", width=13,
         validate=yes_no("Do you have written permission?"),
         note="Yes / No. Never post on a maybe."),
    dict(header="Usage Rights", key="rights", width=16,
         note="Repost, paid, whitelisting..."),
    dict(header="Used In", key="used_in", width=18, style="wrap",
         note="Content IDs or placements where it appeared."),
    dict(header="Rating", key="rating", width=9, style="rating",
         validate=number_check(1, 5, decimal=False),
         note="1-5, your pick of the crop."),
    dict(header="Link", key="link", width=24, style="link"),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Days Held", key="days_held", width=10, style="int",
         is_formula=True,
         formula="=IF($E{r}=\"\",\"\",Report_Date-$E{r})",
         note="Days since the content arrived."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.ugc() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="UGC Tracker",
        subtitle="Customer content, permissions and where each piece was "
                 "used. The proof your product lives in real homes.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Permission Status is a hard gate: if it is not a Yes, it "
                  "does not get posted. Usage Rights travels with the "
                  "content forever.",
        tab_color="#7A9E7E", freeze_cols=2)
