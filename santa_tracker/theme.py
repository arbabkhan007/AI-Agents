"""
Colour palettes / design systems for the Secret Santa & White Elephant
Party Tracker (Novality Store).

Two themes ship with the product:

  noel    warm cream canvas, deep holly red, pine green, antique gold
  arctic  cool night canvas paper-white, deep navy, ice blue, berry accent
"""


class Theme(object):
    """Small attribute bag so sheet code can read ``th.primary`` etc."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def soft(self, key):
        """Return the pale 'tint' partner of a colour key."""
        return self.__dict__[key + "_soft"]


# ===========================================================================
# NOEL - "classic Christmas parlour"
# ===========================================================================
NOEL = Theme(
    key="noel",
    label="Noel",
    bg="#FBF6EE",
    cover_bg="#FBF6EE",
    card="#FFFFFF",
    alt="#FCF8F1",
    border="#E7D9C6",
    border_strong="#C9AE8C",
    primary="#8C1D2C",          # holly red
    primary_2="#1F5C40",        # pine
    primary_2_soft="#E1EDE5",
    primary_soft="#F5E1E2",
    accent="#1F5C40",           # pine green
    accent_soft="#E1EDE5",
    gold="#B98A2E",             # antique gold
    gold_soft="#F6EDD8",
    ink="#33221E",
    muted="#9A8474",
    white="#FFFFFF",
    ok="#1F5C40",
    ok_soft="#E1EDE5",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#5E6FA3",
    info_soft="#E5E9F4",
    plum="#8C1D2C",
    plum_soft="#F5E1E2",
    title_font="Georgia",
    body_font="Calibri",
    mono_font="Consolas",
    tabs={
        "data": "#9A8474",
        "setup": "#1F5C40",
        "dashboard": "#8C1D2C",
        "participants": "#1F5C40",
        "draw": "#8C1D2C",
        "rules": "#B4761A",
        "budget": "#B98A2E",
        "wishlists": "#5E6FA3",
        "we": "#1F5C40",
        "history": "#5E6FA3",
        "cards": "#8C1D2C",
        "guide": "#9A8474",
    },
)

# ===========================================================================
# ARCTIC - "midnight frost party"
# ===========================================================================
ARCTIC = Theme(
    key="arctic",
    label="Arctic",
    bg="#F4F7FB",
    cover_bg="#F4F7FB",
    card="#FFFFFF",
    alt="#F8FAFD",
    border="#D8E1EC",
    border_strong="#A9BBD0",
    primary="#1F3A5F",          # deep navy
    primary_2="#5B8DB8",        # ice blue
    primary_2_soft="#E4EDF5",
    primary_soft="#E2E9F2",
    accent="#C4485C",           # winter berry
    accent_soft="#F8E3E6",
    gold="#C9A227",             # starlight gold
    gold_soft="#F7F0DA",
    ink="#1E2833",
    muted="#7C8CA0",
    white="#FFFFFF",
    ok="#2F6D5F",
    ok_soft="#E0EEE9",
    warn="#B4761A",
    warn_soft="#FBF0D9",
    bad="#AC2F2F",
    bad_soft="#F7E2E0",
    info="#5B8DB8",
    info_soft="#E4EDF5",
    plum="#1F3A5F",
    plum_soft="#E2E9F2",
    title_font="Trebuchet MS",
    body_font="Trebuchet MS",
    mono_font="Consolas",
    tabs={
        "data": "#7C8CA0",
        "setup": "#5B8DB8",
        "dashboard": "#1F3A5F",
        "participants": "#2F6D5F",
        "draw": "#C4485C",
        "rules": "#B4761A",
        "budget": "#C9A227",
        "wishlists": "#5B8DB8",
        "we": "#2F6D5F",
        "history": "#5B8DB8",
        "cards": "#C4485C",
        "guide": "#7C8CA0",
    },
)

THEMES = {"noel": NOEL, "arctic": ARCTIC}
