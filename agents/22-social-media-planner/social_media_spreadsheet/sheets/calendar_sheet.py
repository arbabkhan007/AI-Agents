"""Register: Content Calendar - the heart of the planner."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check, yes_no

NAME = "Content Calendar"
ROWS = 600
LAST_COL = 24         # Y: Coverage

COLUMNS = [
    dict(header="Content ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"C-\"&TEXT({r}-{first}+1,\"0000\"))",
         note="Calculated. Reference this ID everywhere else."),
    dict(header="Publish Date", key="date", width=12, style="date",
         validate=date_check(),
         note="When it goes live. Format: 2026-03-02."),
    dict(header="Publish Time", key="time", width=10, style="time",
         note="Local time of the account. Optional but recommended."),
    dict(header="Weekday", key="weekday", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",TEXT($B{r},\"ddd\"))",
         note="Calculated from the publish date."),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"},
         note="The content pillar this post serves."),
    dict(header="Format", key="format", width=11,
         validate={"validate": "list", "source": "=FormatList"},
         note="Reel, carousel, story, email..."),
    dict(header="Platforms", key="platforms", width=18, style="wrap",
         note="One or more, comma separated."),
    dict(header="Title / Topic", key="title", width=32, style="wrap",
         note="Working title - what the post is about."),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"},
         note="Optional. Links to the Campaigns tab."),
    dict(header="Caption Ref", key="caption_ref", width=11,
         validate={"validate": "list", "source": "=CaptionIDs"},
         note="Caption Bank ID, e.g. CAP-001."),
    dict(header="Hashtag Set", key="hashtags", width=11,
         validate={"validate": "list", "source": "=HashtagIDs"},
         note="Hashtag Bank ID, e.g. HT-001."),
    dict(header="CTA", key="cta", width=26, style="wrap",
         note="The one action you want the reader to take."),
    dict(header="Visual / Asset Ref", key="asset", width=12,
         validate={"validate": "list", "source": "=AssetIDs"},
         note="Asset ID from the Assets tab."),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"},
         note="Who makes it happen."),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"},
         note="Idea to Posted. Drives every dashboard number."),
    dict(header="Goal", key="goal", width=11,
         validate={"validate": "list", "source": "=GoalList"},
         note="What this post is for."),
    dict(header="Approval Status", key="approval", width=12,
         validate={"validate": "list",
                   "source": ["Not Submitted", "In Review", "Approved",
                              "Changes Needed"]},
         note="For client or team sign-off workflows."),
    dict(header="Publish URL", key="url", width=20, style="link",
         note="Link to the live post, once it is up."),
    dict(header="Notes", key="notes", width=30, style="wrap",
         note="Anything worth remembering about this post."),
    dict(header="Day Key", key="day_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",$B{r}-WEEKDAY($B{r},1)+1)",
         note="Week bucket for the Month View, hidden."),
    dict(header="Queue Key", key="queue_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF(OR($O{r}=\"Posted\",$B{r}=\"\"),\"\",$B{r}+"
                 "{r}*0.000001)",
         note="Queue sort key for the Dashboard, hidden."),
    dict(header="Late Key", key="late_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",IF(AND($B{r}<Report_Date,"
                 "$O{r}<>\"Posted\"),$B{r},\"\"))",
         note="Date of overdue posts, hidden."),
    dict(header="Rank Key", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",COUNT($B$first:$B{r}))",
         note="Ranking helper, hidden."),
    dict(header="Day Nth Key", key="nth_key", width=12, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",TEXT($B{r},\"0\")&\"#\"&COUNTIFS("
                 "$B$first:$B{r},$B{r}))",
         note="Date + nth post that day; Month View looks posts up with "
              "it. Hidden."),
    dict(header="Status Nth Key", key="status_key", width=12, hidden=True,
         is_formula=True,
         formula="=IF(OR($A{r}=\"\",$O{r}=\"\"),\"\",$O{r}&\"#\"&COUNTIFS("
                 "$O$first:$O{r},$O{r}))",
         note="Status + nth row with it; Workflow kanban uses it. Hidden."),
    dict(header="Engagement", key="engagement", width=11, style="percent",
         is_formula=True,
         formula="=IFERROR(INDEX([[Performance.engagement_rate]],"
                 "MATCH($A{r},[[Performance.content_id]],0)),\"\")",
         note="Pulled from the Performance tab by Content ID."),
    dict(header="Coverage", key="coverage", width=13,
         is_formula=True,
         formula="=IF($A{r}=\"\",\"\",IF($J{r}=\"\",\"Caption needed\","
                 "IF($K{r}=\"\",\"Hashtags needed\",IF($M{r}=\"\","
                 "\"Asset needed\",\"Ready\"))))",
         note="Auto checklist: caption, hashtags and asset are all linked."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.content_calendar() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Content Calendar",
        subtitle="600 rows, one post per row. Plan the whole quarter here, "
                 "then let the dashboards do the counting.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="IDs, weekdays and the two right-hand columns calculate "
                  "themselves. Drop downs keep every register in sync - "
                  "add new pillars and campaigns on their own tabs first.",
        tab_color="#2E7D8F", freeze_cols=2)
