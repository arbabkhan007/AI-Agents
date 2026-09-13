"""
Colour palettes / design systems for the Catering Business Manager.

Two themes ship with the product:

  classic   warm cream canvas, espresso brown, copper, brass gold
  fresh     cool white canvas, basil green, tomato accent, lemon gold

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
# CLASSIC - "bistro ledger"
# ===========================================================================
CLASSIC = Theme(
    key="classic",
    label="Classic",
    bg="#F8F4EC",
    cover_bg="#F8F4EC",
    card="#FFFFFF",
    alt="#FBF8F1",
    border="#E3D9C6",
    border_strong="#C8B795",
    primary="#4B3626",          # espresso
    primary_2="#7A5C43",        # latte
    primary_2_soft="#EBE1D4",
    primary_soft="#EDE6DA",
    accent="#B4652F",           # copper
    accent_soft="#F7E7DB",
    gold="#A9822B",             # brass
    gold_soft="#F6EED7",
    ink="#2E241A",
    muted="#8B7C6B",
    white="#FFFFFF",
    ok="#4C7A4C",
    ok_soft="#E2EEE0",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#3F6E8C",
    info_soft="#E2ECF3",
    plum="#7A5273",
    plum_soft="#F0E6EE",
    title_font="Georgia",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#8B7C6B",
        "setup": "#7A5C43",
        "dashboard": "#4B3626",
        "clients": "#B4652F",
        "events": "#A9822B",
        "quote": "#3F6E8C",
        "menu": "#AC2F2F",
        "inventory": "#4C7A4C",
        "shopping": "#6C9A58",
        "expenses": "#AC2F2F",
        "income": "#4C7A4C",
        "staff": "#7A5273",
        "equipment": "#3F6E8C",
        "suppliers": "#B4761A",
        "calendar": "#A9822B",
        "reports": "#4B3626",
        "tax": "#7A5273",
        "checklists": "#4C7A4C",
        "invoice": "#B4652F",
        "guide": "#8B7C6B",
    },
)

# ===========================================================================
# FRESH - "market garden"
# ===========================================================================
FRESH = Theme(
    key="fresh",
    label="Fresh",
    bg="#FAFBF8",
    cover_bg="#FAFBF8",
    card="#FFFFFF",
    alt="#F4F7F3",
    border="#DCE4DA",
    border_strong="#B9C8B4",
    primary="#2F5D46",          # basil
    primary_2="#56806A",
    primary_2_soft="#E2EDE6",
    primary_soft="#E6F0EA",
    accent="#C4482F",           # tomato
    accent_soft="#F9E4DE",
    gold="#C99A18",             # lemon
    gold_soft="#FAF1D6",
    ink="#22302A",
    muted="#7C8A82",
    white="#FFFFFF",
    ok="#3E7C4F",
    ok_soft="#E0EFE4",
    warn="#C07C12",
    warn_soft="#FBF0D8",
    bad="#B23A3A",
    bad_soft="#F8E3E1",
    info="#3E6E8E",
    info_soft="#E2EDF3",
    plum="#6C5B94",
    plum_soft="#EBE7F3",
    title_font="Calibri Light",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#7C8A82",
        "setup": "#56806A",
        "dashboard": "#2F5D46",
        "clients": "#C4482F",
        "events": "#C99A18",
        "quote": "#3E6E8E",
        "menu": "#B23A3A",
        "inventory": "#3E7C4F",
        "shopping": "#6C9A58",
        "expenses": "#B23A3A",
        "income": "#3E7C4F",
        "staff": "#6C5B94",
        "equipment": "#3E6E8E",
        "suppliers": "#C07C12",
        "calendar": "#C99A18",
        "reports": "#2F5D46",
        "tax": "#6C5B94",
        "checklists": "#3E7C4F",
        "invoice": "#C4482F",
        "guide": "#7C8A82",
    },
)

THEMES = {"classic": CLASSIC, "fresh": FRESH}


def get(name):
    try:
        return THEMES[name]
    except KeyError:
        raise ValueError("unknown theme %r (have %s)"
                         % (name, ", ".join(sorted(THEMES))))
