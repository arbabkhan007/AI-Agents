"""
Social Media Content Calendar & Analytics Planner
=================================================

Generates a ready-to-sell Excel workbook for social media managers, creators
and small brands: a 12 month content calendar, idea / caption / hashtag
banks, a production workflow, campaigns, launches, influencer and UGC
trackers, repurposing, competitor and trend research, per-platform planners
for Instagram, TikTok, Pinterest, YouTube and Facebook, monthly analytics,
post level performance scoring, A/B tests, ads, assets, goals, budget and
ROI, team tasks, dashboards, reports and printable briefs.

    python -m social_media_spreadsheet --output "My Planner.xlsx"

or from Python::

    from social_media_spreadsheet import build_workbook, Config
    build_workbook("planner.xlsx", Config(include_sample_data=False))

Every formula cell is locked and every sheet is protected with the password
in :class:`~social_media_spreadsheet.config.Config` (default ``premium``), so
the maths cannot be edited by accident while the input cells stay open.
"""

from .build import build_workbook
from .config import AUTHOR, FORMULA_PASSWORD, Config

__all__ = ["build_workbook", "Config", "AUTHOR", "FORMULA_PASSWORD",
           "__version__"]

__version__ = "1.0.0"
__author__ = AUTHOR
