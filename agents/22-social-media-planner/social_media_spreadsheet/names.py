"""Workbook level defined names that point at the register sheets.

The drop down lists on the `Lists` tab define their own names; these are the
ones that have to follow live data (content IDs, caption IDs, campaign names,
...), so they are built from the registry once every register has been
created.  Each one is an ``OFFSET`` range that grows and shrinks with the
number of filled rows.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    "AccountNames": ("Accounts", "account"),
    "PersonaNames": ("Audience Personas", "name"),
    "PillarNames": ("Content Pillars", "name"),
    "ContentIDs": ("Content Calendar", "id"),
    "ContentTitles": ("Content Calendar", "title"),
    "CaptionIDs": ("Caption Bank", "id"),
    "CaptionTitles": ("Caption Bank", "title"),
    "IdeaIDs": ("Idea Bank", "id"),
    "CampaignNames": ("Campaigns", "name"),
    "LaunchNames": ("Launch Planner", "product"),
    "InfluencerNames": ("Influencers", "name"),
    "CompetitorNames": ("Competitors", "name"),
    "TrendNames": ("Trends", "name"),
    "AssetIDs": ("Assets", "id"),
    "GoalNames": ("Goals", "name"),
    "TeamNames": ("Team", "name"),
    "HashtagIDs": ("Hashtag Bank", "id"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            continue
        spec = reg[sheet]
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
