"""Build orchestration: editions, themes, modes and product filenames."""

import os

from . import config as C
from . import theme as T
from .book import Book
from .sheets import (budget, cards, dashboard, data, draw, guide, history,
                     participants, rules, setup, we, wishlists)

BUILDERS = {
    "data": data.build,
    "setup": setup.build,
    "dashboard": dashboard.build,
    "participants": participants.build,
    "draw": draw.build,
    "rules": rules.build,
    "budget": budget.build,
    "wishlists": wishlists.build,
    "we": we.build,
    "history": history.build,
    "cards": cards.build,
    "guide": guide.build,
}


def product_filename(edition, theme_name, mode):
    return "Secret_Santa_White_Elephant_Tracker_%s_%s%s.xlsx" % (
        edition.upper(), T.THEMES[theme_name].label,
        "_EXAMPLE" if mode == "demo" else "")


def build_workbook(path, edition="premium", theme_name="noel",
                   mode="blank", protect=C.PROTECT_PASSWORD, images=True):
    """Write one workbook file and return its build stats."""
    from . import demo as D
    if edition not in ("basic", "premium"):
        raise ValueError("edition must be 'basic' or 'premium'")
    if mode not in ("blank", "demo"):
        raise ValueError("mode must be 'blank' or 'demo'")
    model = D.Demo() if mode == "demo" else None
    bk = Book(path, T.THEMES[theme_name], edition=edition, mode=mode,
              protect=protect, images=images, demo=model)
    for key in bk.order:
        BUILDERS[key](bk)
    bk.close()
    stats = dict(bk.stats)
    stats["size"] = os.path.getsize(path)
    return stats


def build_all(outdir, protect=C.PROTECT_PASSWORD, images=True):
    """The curated six-file Etsy product set."""
    os.makedirs(outdir, exist_ok=True)
    combos = [("premium", "noel", "demo"), ("premium", "noel", "blank"),
              ("premium", "arctic", "blank"), ("basic", "noel", "blank"),
              ("basic", "arctic", "blank"), ("basic", "noel", "demo")]
    out = []
    for edition, theme_name, mode in combos:
        name = product_filename(edition, theme_name, mode)
        path = os.path.join(outdir, name)
        stats = build_workbook(path, edition, theme_name, mode,
                               protect=protect, images=images)
        out.append((name, stats))
    return out
