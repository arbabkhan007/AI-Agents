"""Register: Compliance."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "Compliance"
ROWS = 60

COLUMNS = [
    dict(header="Item ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"COMP-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Item", key="item", width=32, style="wrap",
         note="What needs a permission, licence or approval."),
    dict(header="Content ID", key="content_id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"}),
    dict(header="Type", key="type", width=14,
         validate={"validate": "list",
                   "source": ["Music Rights", "UGC Rights", "Model Release",
                              "Ad Disclosure", "Review", "Trademark",
                              "Privacy"]}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=ComplianceStatusList"}),
    dict(header="Requested", key="requested", width=12, style="date",
         validate=date_check()),
    dict(header="Received", key="received", width=12, style="date",
         validate=date_check()),
    dict(header="Expiry", key="expiry", width=12, style="date",
         validate=date_check()),
    dict(header="Days To Expiry", key="days_expiry", width=11, style="int",
         is_formula=True,
         formula="=IF($H{r}=\"\",\"\",$H{r}-Report_Date)",
         note="Negative means the rights have lapsed."),
    dict(header="Contact", key="contact", width=22),
    dict(header="Notes", key="notes", width=28, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.compliance() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Compliance",
        subtitle="Music licences, UGC permissions, releases and reviews. "
                 "If it is not signed, it does not ship.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Days To Expiry watches every licence. Chase anything "
                  "that says Pending before the content goes live.",
        tab_color="#B0B0A8", freeze_cols=2)
