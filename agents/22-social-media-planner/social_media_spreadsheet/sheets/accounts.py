"""Register: Accounts. Calcs sit at the far right so the freeze pane keeps
them out of sight while scrolling the human columns."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, list_from, number_check, yes_no

NAME = "Accounts"
ROWS = 25
LAST_COL = 16          # 0-based: 17 columns A..Q
CALC_COL = 16          # Q: 30 day cadence

COLUMNS = [
    dict(header="Account", key="account", width=26,
         note="Label for the account, platform first."),
    dict(header="Platform", key="platform", width=13,
         validate={"validate": "list", "source": "=PlatformList"},
         note="Which network this account lives on."),
    dict(header="Handle / URL Name", key="handle", width=18,
         note="The @handle or channel name."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"},
         note="Who posts and replies here."),
    dict(header="Purpose", key="purpose", width=26,
         note="Why this account exists, in one line."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list", "source": "=AccountStatusList"},
         note="Active, Paused, Archived or Planned."),
    dict(header="Followers", key="followers", width=10, style="int",
         validate=number_check(0, 100000000, decimal=False),
         note="Last known follower count."),
    dict(header="Avg Engagement Rate", key="engagement", width=12,
         style="percent",
         validate=number_check(0, 1),
         note="(Likes + comments + saves + shares) / reach, 30 day average."),
    dict(header="Posts / Month", key="posts", width=10, style="int",
         validate=number_check(0, 500, decimal=False),
         note="How many posts this account publishes per month."),
    dict(header="Last Post Date", key="last_post", width=12, style="date",
         validate=date_check(),
         note="Most recent published post."),
    dict(header="Ad Spend / Month", key="ad_spend", width=12, style="money",
         validate=number_check(0, 1000000),
         note="Average monthly paid support."),
    dict(header="Contact Email", key="contact", width=20,
         note="Login or business contact email."),
    dict(header="Link", key="url", width=22, style="link",
         note="Link to the profile."),
    dict(header="Notes", key="notes", width=30, style="wrap",
         note="Anything the next person needs to know."),
    dict(header="Helper", key="helper_key", width=10, hidden=True,
         is_formula=True, formula="=IF($A{r}=\"\",0,{r})",
         note="Row index helper, hidden."),
    dict(header="Cadence Rank", key="rank_key", width=10, hidden=True,
         is_formula=True,
         formula="=IF($I{r}=\"\",\"\",COUNTIF($I$first:$I{r},\">0\")"
                 "+COUNTIF($I$first:$I{r},\"=0\")*0.5)",
         note="Ordering helper for the busiest accounts, hidden."),
    dict(header="30 Day Cadence", key="cadence", width=14, style="text",
         is_formula=True,
         formula="=IF($F{r}<>\"Active\",\"--\",IF($I{r}>=20,\"Daily\","
                 "IF($I{r}>=12,\"4x a week\",IF($I{r}>=7,\"Weekly\","
                 "IF($I{r}>0,\"Occasional\",\"Dormant\")))))",
         note="Calculated from posts per month and account status."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.accounts() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Social Accounts",
        subtitle="Every account you post from, who owns it and what it is "
                 "for. The dashboards count active accounts only.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="One row per account. Add accounts before you fill the "
                  "Content Calendar - the dashboard reads this list first.",
        tab_color="#C98F5B", freeze_cols=1)
