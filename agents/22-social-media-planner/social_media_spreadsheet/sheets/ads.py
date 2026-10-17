"""Register: Ads - spend and return, side by side."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import number_check

NAME = "Ads"
ROWS = 60

COLUMNS = [
    dict(header="Ad ID", key="id", width=10,
         validate={"validate": "list",
                   "source": ["AD-001", "AD-002", "AD-003", "AD-004",
                              "AD-005", "AD-006", "AD-007", "AD-008"]}),
    dict(header="Platform", key="platform", width=12,
         validate={"validate": "list", "source": "=PlatformList"}),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Objective", key="objective", width=12,
         validate={"validate": "list",
                   "source": ["Awareness", "Traffic", "Engagement",
                              "Leads", "Sales"]}),
    dict(header="Audience", key="audience", width=22, style="wrap"),
    dict(header="Spend", key="spend", width=11, style="money",
         validate=number_check(0, 1000000)),
    dict(header="Impressions", key="impressions", width=11, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="Clicks", key="clicks", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False)),
    dict(header="CTR", key="ctr", width=10, style="percent",
         is_formula=True,
         formula="=IF($G{r}=0,0,$H{r}/$G{r})",
         note="Clicks / impressions."),
    dict(header="CPC", key="cpc", width=10, style="money",
         is_formula=True,
         formula="=IF($H{r}=0,0,$F{r}/$H{r})",
         note="Spend / clicks."),
    dict(header="Conversions", key="conversions", width=11, style="int",
         validate=number_check(0, 1000000, decimal=False)),
    dict(header="Revenue", key="revenue", width=12, style="money",
         validate=number_check(0, 10000000)),
    dict(header="ROAS", key="roas", width=10, style="number",
         is_formula=True,
         formula="=IF($F{r}=0,0,$L{r}/$F{r})",
         note="Revenue / spend."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list",
                   "source": ["Active", "Paused", "Ended", "Testing"]}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.ads() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Ads",
        subtitle="Paid support for the content that earned it. CTR, CPC "
                 "and ROAS calculate themselves - judge every ad on ROAS.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Spend and revenue are yours; the three middle columns "
                  "are locked formulas. If ROAS sits under 1.0 for a week, "
                  "the ad is subsidising the platform.",
        tab_color="#2E7D8F", freeze_cols=1)
