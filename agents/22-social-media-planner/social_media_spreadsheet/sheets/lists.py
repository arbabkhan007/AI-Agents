"""The `Lists` tab: every drop down in the workbook is fed from here."""

from __future__ import annotations

from typing import Dict, List, Tuple

from ..layout import col_letter, quote_sheet
from ..writer import SheetWriter

NAME = "Lists"
LAST_COL = 9

#: header -> (values, defined name)
LISTS: Dict[str, Tuple[List[str], str]] = {
    "Statuses": (["Idea", "Draft", "In Progress", "Ready", "Scheduled",
                  "Posted", "Paused"], "StatusList"),
    "Platforms": (["Instagram", "TikTok", "Pinterest", "YouTube",
                   "Facebook", "Newsletter", "LinkedIn", "X",
                   "Threads", "Blog"], "PlatformList"),
    "Content Formats": (["Photo", "Video", "Reel", "Carousel", "Story",
                         "Live", "Short", "Pin", "Email", "Article",
                         "Poll", "Carousel Doc"], "FormatList"),
    "Pillars": (["Studio Process", "Product Spotlight", "Behind the Brand",
                 "Education & Tips", "Community & UGC",
                 "Promotions & Launches", "Trends & Moments", "Customer Love"],
                "PillarList"),
    "Campaign Statuses": (["Planning", "Active", "Complete", "Paused",
                           "Cancelled"], "CampaignStatusList"),
    "Goals": (["Awareness", "Engagement", "Follows", "Saves", "Clicks",
               "Traffic", "Sales", "Leads", "Signups", "Community"],
              "GoalList"),
    "Task Statuses": (["To Do", "In Progress", "Done", "Blocked"],
                      "TaskStatusList"),
    "Priorities": (["Low", "Medium", "High", "Critical"], "PriorityList"),
    "Content Types": (["Photo", "Video", "Reel", "Carousel", "Story", "Live",
                       "Short", "Pin", "Email", "Article", "GIF",
                       "Thumbnail"], "ContentTypeList"),
    "Engagement Buckets": (["0-2%", "2-4%", "4-6%", "6-10%", "10%+"],
                           "EngagementBucketList"),
    "Seasons": (["Spring", "Summer", "Autumn", "Winter", "Holiday"],
                "SeasonList"),
    "Compliance Statuses": (["Not Started", "In Review", "Approved",
                             "Changes Needed", "Not Applicable"],
                            "ComplianceStatusList"),
    "Account Statuses": (["Active", "Paused", "Archived", "Planned"],
                         "AccountStatusList"),
    "Outreach Statuses": (["Prospect", "Contacted", "Negotiating",
                           "Active", "Completed", "Paused"],
                          "OutreachStatusList"),
    "UTM Sources": (["instagram", "tiktok", "pinterest", "youtube",
                     "facebook", "newsletter", "blog", "ads", "pr",
                     "affiliate"], "UtmSourceList"),
    "Weekdays": (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                  "Saturday", "Sunday"], "WeekdayList"),
    "Months": (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec"], "MonthList"),
    "Month-Year": (["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26",
                    "Jun-26", "Jul-26", "Aug-26", "Sep-26", "Oct-26",
                    "Nov-26", "Dec-26", "Jan-27", "Feb-27", "Mar-27",
                    "Apr-27", "May-27", "Jun-27", "Jul-27", "Aug-27",
                    "Sep-27", "Oct-27", "Nov-27", "Dec-27"],
                   "MonthYearList"),
    "Colour Tags": (["Warm", "Cool", "Neutral", "Bright", "Seasonal",
                     "Limited"], "ColourTagList"),
    "User Roles": (["Owner", "Manager", "Creator", "Contributor",
                    "Viewer"], "RoleList"),
    "Effort Levels": (["Low", "Medium", "High"], "EffortList"),
    "Impact Levels": (["Low", "Medium", "High"], "ImpactList"),
}


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#B0B0A8")
    f = sheet.f
    sheet.banner(
        "Reference Lists",
        "Every drop down in this workbook reads from these columns. Edit the "
        "words here and the change applies everywhere - formulas follow the "
        "names, not the text.",
        LAST_COL)

    sheet.set_col(0, 0, 12)
    sheet.set_col(1, LAST_COL, 15)
    sheet.row_height(4, 26)

    for col, (header, (values, defined_name)) in enumerate(LISTS.items()):
        sheet.write(4, col, header, f.chrome("header"))
        for i, value in enumerate(values):
            sheet.write(5 + i, col, value, f.cell("text", "plain"))
        top = 6                                   # 1-based first value row
        bottom = 5 + len(values)
        sheet.book.define_name(
            defined_name,
            f"={quote_sheet(NAME)}!${col_letter(col)}${top}:"
            f"${col_letter(col)}${bottom}")
        # Default fill so empty looking columns still show their intent.
        sheet.write(5 + len(values), col, "", f.cell("text", "plain"))

    sheet.write(5 + max(len(v[0]) for v in LISTS.values()), 0,
                "Tip: keep each list under 25 items so the drop downs stay "
                "easy to scan.", f.chrome("note"))
    sheet.finish(freeze_row=5)
    sheet.ws.print_area(f"A1:{chr(65 + LAST_COL)}40")
    return sheet
