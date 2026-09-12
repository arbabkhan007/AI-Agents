"""
Colour palettes / design systems.

Two themes ship with the product:

  festive   cream canvas, deep pine green, burgundy, antique gold
  minimal   white canvas, charcoal ink, sage green, clay accent

Everything else in the workbook is derived from the active theme, so a new
palette can be added by copying one of the dictionaries below.
"""


class Theme(object):
    """Small attribute bag so sheet code can read ``th.primary`` etc."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def soft(self, key):
        """Return the pale 'tint' partner of a colour key."""
        return self.__dict__[key + "_soft"]


# ===========================================================================
# FESTIVE - "Christmas command centre"
# ===========================================================================
FESTIVE = Theme(
    key="festive",
    label="Festive",
    # canvas + surfaces
    bg="#FFF9EF",            # cream page background
    cover_bg="#FEF6E9",
    card="#FFFFFF",          # white cards
    alt="#FDFAF3",           # zebra stripe
    border="#E4D8C3",        # warm hairline
    border_strong="#CBB894",
    # brand
    primary="#14432A",       # deep pine green
    primary_2="#1E6B45",     # lighter green
    primary_2_soft="#DDEBE1",
    primary_soft="#E4EFE6",
    accent="#7B1E28",        # burgundy
    accent_soft="#F6E4E4",
    gold="#B8912F",          # antique gold
    gold_soft="#FBF2DA",
    # text
    ink="#33261C",
    muted="#8A7A6D",
    white="#FFFFFF",
    # semantic
    ok="#2F7D4F",
    ok_soft="#DFF0E3",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#B02A2A",
    bad_soft="#F8E2E2",
    info="#2A5D8F",
    info_soft="#E3EDF7",
    plum="#6C3A6E",
    plum_soft="#F0E6F2",
    # typography
    title_font="Georgia",
    body_font="Calibri",
    mono_font="Consolas",
    # chart series colours (in draw order)
    series=["#14432A", "#7B1E28", "#B8912F", "#2A5D8F", "#2F7D4F",
            "#6C3A6E", "#C1443C", "#8A7A6D", "#1E6B45", "#B4761A"],
    # worksheet tab colours, per sheet key
    tabs={
        "dashboard": "#7B1E28",
        "gifts": "#14432A",
        "budget": "#B8912F",
        "wishlist": "#6C3A6E",
        "shopping": "#2A5D8F",
        "orders": "#1E6B45",
        "wrapping": "#C1443C",
        "cards": "#B4761A",
        "stockings": "#8C5A2B",
        "todo": "#2F7D4F",
        "setup": "#8A7A6D",
        "guide": "#7B1E28",
        "data": "#BFBFBF",
    },
)


# ===========================================================================
# MINIMAL - clean, modern, "not-Christmassy" (for the second product photo)
# ===========================================================================
MINIMAL = Theme(
    key="minimal",
    label="Minimal",
    bg="#FFFFFF",
    cover_bg="#FFFFFF",
    card="#FFFFFF",
    alt="#FAFAF8",
    border="#E3E3E1",
    border_strong="#C9C9C6",
    primary="#2F4F3E",       # deep sage
    primary_2="#4A6B59",
    primary_2_soft="#E8EEE9",
    primary_soft="#EDF1EE",
    accent="#A65A4A",        # clay
    accent_soft="#F7EDEA",
    gold="#B08D57",
    gold_soft="#F6F1E8",
    ink="#2E2E2E",
    muted="#8B8B8B",
    white="#FFFFFF",
    ok="#4B7A5A",
    ok_soft="#EDF3EE",
    warn="#A98036",
    warn_soft="#F8F2E6",
    bad="#A85450",
    bad_soft="#F8ECEB",
    info="#51708C",
    info_soft="#EDF2F6",
    plum="#6E5A78",
    plum_soft="#F2EFF4",
    title_font="Calibri Light",
    body_font="Calibri",
    mono_font="Consolas",
    series=["#2F4F3E", "#A65A4A", "#B08D57", "#51708C", "#4B7A5A",
            "#6E5A78", "#8C8C8C", "#A98036", "#7C9082", "#B8897E"],
    tabs={
        "dashboard": "#2F4F3E",
        "gifts": "#4A6B59",
        "budget": "#B08D57",
        "wishlist": "#6E5A78",
        "shopping": "#51708C",
        "orders": "#4B7A5A",
        "wrapping": "#A65A4A",
        "cards": "#A98036",
        "stockings": "#8C7355",
        "todo": "#4B7A5A",
        "setup": "#8C8C8C",
        "guide": "#2F4F3E",
        "data": "#BFBFBF",
    },
)


THEMES = {"festive": FESTIVE, "minimal": MINIMAL}


def get(name):
    try:
        return THEMES[name.lower()]
    except KeyError:
        raise SystemExit("Unknown theme '%s' (choose from: %s)"
                         % (name, ", ".join(sorted(THEMES))))
