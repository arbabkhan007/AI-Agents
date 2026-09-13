"""
Colour palettes / design systems for the Crochet Craft Fair Tracker.

Two themes ship with the product:

  berry   warm cream canvas, deep berry plum, rose accent, honey gold
  mint    cool paper-white canvas, mint teal, coral accent, lemon gold

Everything else in the workbook is derived from the active theme.
"""


class Theme(object):
    """Small attribute bag so sheet code can read ``th.primary`` etc."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def soft(self, key):
        """Return the pale 'tint' partner of a colour key."""
        return self.__dict__[key + "_soft"]


# ===========================================================================
# BERRY - "yarn shop autumn"
# ===========================================================================
BERRY = Theme(
    key="berry",
    label="Berry",
    bg="#FAF6F1",
    cover_bg="#FAF6F1",
    card="#FFFFFF",
    alt="#FBF7F3",
    border="#E6D9D2",
    border_strong="#CBAFA6",
    primary="#5C3A50",          # deep berry plum
    primary_2="#8A5F79",        # dusty mauve
    primary_2_soft="#EFE2EA",
    primary_soft="#EDE2E8",
    accent="#C05268",           # rose
    accent_soft="#F8E3E7",
    gold="#B98A2E",             # honey
    gold_soft="#F6EDD8",
    ink="#33222C",
    muted="#97818D",
    white="#FFFFFF",
    ok="#4C7A4C",
    ok_soft="#E2EEE0",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#5E6FA3",
    info_soft="#E5E9F4",
    plum="#7A5273",
    plum_soft="#F0E6EE",
    title_font="Georgia",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#97818D",
        "setup": "#8A5F79",
        "dashboard": "#5C3A50",
        "catalog": "#C05268",
        "materials": "#7A5273",
        "production": "#4C7A4C",
        "events": "#B98A2E",
        "sales": "#4C7A4C",
        "eventprofit": "#5E6FA3",
        "reorder": "#AC2F2F",
        "packing": "#C05268",
        "pricing": "#5E6FA3",
        "monthly": "#5C3A50",
        "guide": "#97818D",
    },
)

# ===========================================================================
# MINT - "fresh stitch studio"
# ===========================================================================
MINT = Theme(
    key="mint",
    label="Mint",
    bg="#F7FAF8",
    cover_bg="#F7FAF8",
    card="#FFFFFF",
    alt="#F4F8F5",
    border="#D8E4DD",
    border_strong="#AFC8BC",
    primary="#2F6D5F",          # mint teal
    primary_2="#5E9488",        # sage
    primary_2_soft="#E1EEE9",
    primary_soft="#E3EFEA",
    accent="#E2725B",           # coral
    accent_soft="#FBE7E2",
    gold="#C9A227",             # lemon gold
    gold_soft="#F8F1D9",
    ink="#22332E",
    muted="#7E948C",
    white="#FFFFFF",
    ok="#3E7C4F",
    ok_soft="#E1F0E4",
    warn="#C07C12",
    warn_soft="#FBF1DA",
    bad="#B23A3A",
    bad_soft="#F8E4E2",
    info="#3E6E8E",
    info_soft="#E1ECF2",
    plum="#6C5B94",
    plum_soft="#EBE7F2",
    title_font="Trebuchet MS",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#7E948C",
        "setup": "#5E9488",
        "dashboard": "#2F6D5F",
        "catalog": "#E2725B",
        "materials": "#6C5B94",
        "production": "#3E7C4F",
        "events": "#C9A227",
        "sales": "#3E7C4F",
        "eventprofit": "#3E6E8E",
        "reorder": "#B23A3A",
        "packing": "#E2725B",
        "pricing": "#3E6E8E",
        "monthly": "#2F6D5F",
        "guide": "#7E948C",
    },
)

THEMES = {"berry": BERRY, "mint": MINT}
