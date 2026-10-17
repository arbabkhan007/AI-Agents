"""The five platform planners: Instagram, TikTok, Pinterest, YouTube,
Facebook.  Each is a register, tuned to what that network actually needs."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

HELP_NOTE = ("One row per post on this platform. Content IDs link back to "
             "the master Content Calendar so nothing drifts apart.")


def _spec(cfg, name, title, subtitle, columns, samples_fn, rows=100,
          freeze_cols=2, tab="#2E7D8F"):
    samples = samples_fn() if cfg.include_sample_data else []
    n = cfg.row_count(name) or rows
    return SheetSpec(
        name=name, title=title, subtitle=subtitle,
        columns=columns, rows=n,
        samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, n),
        help_text=HELP_NOTE, tab_color=tab, freeze_cols=freeze_cols)


# ---------------------------------------------------------------- Instagram
INSTAGRAM_COLUMNS = [
    dict(header="Content ID", key="id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Link to the master Content Calendar row."),
    dict(header="Post Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Post Time", key="time", width=10, style="time"),
    dict(header="Post Type", key="type", width=11,
         validate={"validate": "list",
                   "source": ["Feed Photo", "Carousel", "Reel", "Story",
                              "Live", "Collab"]},
         note="Format on Instagram."),
    dict(header="Caption", key="title", width=34, style="wrap",
         note="Working caption or topic."),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"}),
    dict(header="Caption Ref", key="caption_ref", width=11,
         validate={"validate": "list", "source": "=CaptionIDs"}),
    dict(header="Link", key="link", width=22, style="link",
         note="URL of the live post."),
    dict(header="Notes", key="notes", width=28, style="wrap"),
    dict(header="Day Key", key="day_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",$B{r}-WEEKDAY($B{r},1)+1)"),
]


def instagram_spec(cfg):
    return _spec(cfg, "Instagram", "Instagram Planner",
                 "Feed, reels, stories and collabs - planned the way "
                 "Instagram actually works.",
                 INSTAGRAM_COLUMNS, sample_data.instagram, rows=120)


# ------------------------------------------------------------------- TikTok
TIKTOK_COLUMNS = [
    dict(header="Content ID", key="id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Link to the master Content Calendar row."),
    dict(header="Post Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Post Time", key="time", width=10, style="time"),
    dict(header="Hook", key="hook", width=30, style="wrap",
         note="The first 2 seconds. Write this first."),
    dict(header="Trend / Format", key="trend", width=16,
         note="Trend name or format, if you are riding one."),
    dict(header="Sound / Audio", key="sound", width=20,
         note="Trending audio or your own."),
    dict(header="Title", key="title", width=28, style="wrap"),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Pillar", key="pillar", width=18,
         validate={"validate": "list", "source": "=PillarList"}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"}),
    dict(header="Content Ref", key="ref", width=22, style="link",
         note="Link to the live video."),
    dict(header="Notes", key="notes", width=26, style="wrap"),
    dict(header="Day Key", key="day_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",$B{r}-WEEKDAY($B{r},1)+1)"),
]


def tiktok_spec(cfg):
    return _spec(cfg, "TikTok", "TikTok Planner",
                 "Hook first, trend second, product third. Keep the hooks "
                 "honest and the audio intentional.",
                 TIKTOK_COLUMNS, sample_data.tiktok, rows=100)


# ---------------------------------------------------------------- Pinterest
PINTEREST_COLUMNS = [
    dict(header="Pin ID", key="id", width=11,
         is_formula=True,
         formula="=IF($C{r}=\"\",\"\",\"PIN-\"&TEXT({r}-{first}+1,\"000\"))",
         note="Calculated."),
    dict(header="Pin Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Board", key="board", width=20,
         note="Board this pin belongs to."),
    dict(header="Title", key="title", width=34, style="wrap",
         note="Keyword rich - Pinterest is a search engine."),
    dict(header="Destination Link", key="dest", width=28, style="link",
         note="Where the pin sends people."),
    dict(header="Pin Type", key="type", width=11,
         validate={"validate": "list",
                   "source": ["Standard", "Idea", "Video", "Carousel",
                              "Product"]}),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
]


def pinterest_spec(cfg):
    return _spec(cfg, "Pinterest", "Pinterest Planner",
                 "Pins keep working for months. Titles do the heavy "
                 "lifting, so write them like search queries.",
                 PINTEREST_COLUMNS, sample_data.pinterest, rows=80)


# ------------------------------------------------------------------ YouTube
YOUTUBE_COLUMNS = [
    dict(header="Video ID", key="id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Link to the master Content Calendar row."),
    dict(header="Publish Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Video Title", key="title", width=32, style="wrap"),
    dict(header="Type", key="type", width=11,
         validate={"validate": "list",
                   "source": ["Vlog", "Tutorial", "Short", "Live",
                              "Shorts Cut", "Podcast"]}),
    dict(header="YouTube Title", key="title_txt", width=32, style="wrap",
         note="The full title as it will appear on YouTube."),
    dict(header="Description", key="desc", width=36, style="wrap"),
    dict(header="Tags", key="tags", width=20, style="wrap"),
    dict(header="Thumbnail", key="thumb", width=12,
         validate={"validate": "list", "source": "=AssetIDs"},
         note="Asset ID of the thumbnail."),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"}),
    dict(header="Notes", key="notes", width=26, style="wrap"),
]


def youtube_spec(cfg):
    return _spec(cfg, "YouTube", "YouTube Planner",
                 "Long form lives here. Every video should promise three "
                 "shorts and a pin.",
                 YOUTUBE_COLUMNS, sample_data.youtube, rows=40)


# ----------------------------------------------------------------- Facebook
FACEBOOK_COLUMNS = [
    dict(header="Content ID", key="id", width=11,
         validate={"validate": "list", "source": "=ContentIDs"},
         note="Link to the master Content Calendar row."),
    dict(header="Post Date", key="date", width=12, style="date",
         validate=date_check()),
    dict(header="Post Time", key="time", width=10, style="time"),
    dict(header="Post Type", key="type", width=11,
         validate={"validate": "list",
                   "source": ["Photo", "Video", "Link", "Event", "Live",
                              "Note"]}),
    dict(header="Post", key="title", width=34, style="wrap"),
    dict(header="Campaign", key="campaign", width=18,
         validate={"validate": "list", "source": "=CampaignNames"}),
    dict(header="Event Link", key="event", width=18,
         note="Event name, if this promotes one."),
    dict(header="Status", key="status", width=12,
         validate={"validate": "list", "source": "=StatusList"}),
    dict(header="Notes", key="notes", width=28, style="wrap"),
]


def facebook_spec(cfg):
    return _spec(cfg, "Facebook", "Facebook Planner",
                 "Community, events and local reach. Events and groups do "
                 "more work here than pretty photos.",
                 FACEBOOK_COLUMNS, sample_data.facebook, rows=60)


# Alias modules so build.py can import each platform as its own module.
class _PlatformModule:
    def __init__(self, name, spec_fn):
        self.NAME = name
        self._spec_fn = spec_fn

    def spec(self, cfg):
        return self._spec_fn(cfg)


INSTAGRAM = _PlatformModule("Instagram", instagram_spec)
TIKTOK = _PlatformModule("TikTok", tiktok_spec)
PINTEREST = _PlatformModule("Pinterest", pinterest_spec)
YOUTUBE = _PlatformModule("YouTube", youtube_spec)
FACEBOOK = _PlatformModule("Facebook", facebook_spec)
