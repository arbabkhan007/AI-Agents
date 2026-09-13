"""Build orchestration: editions, themes, modes and product filenames."""

import os

from . import config as C
from . import theme as T
from .book import Book
from .sheets import (catalog, dashboard, data, eventprofit, events, guide,
                     materials, monthly, packing, pricing, production,
                     reorder, sales, setup)

BUILDERS = {
    "data": data.build,
    "setup": setup.build,
    "dashboard": dashboard.build,
    "catalog": catalog.build,
    "materials": materials.build,
    "production": production.build,
    "events": events.build,
    "sales": sales.build,
    "eventprofit": eventprofit.build,
    "reorder": reorder.build,
    "packing": packing.build,
    "pricing": pricing.build,
    "monthly": monthly.build,
    "guide": guide.build,
}


def product_filename(edition, theme_name, mode):
    return "Crochet_Craft_Fair_Tracker_%s_%s%s.xlsx" % (
        edition.upper(), T.THEMES[theme_name].label,
        "_EXAMPLE" if mode == "demo" else "")


def build_workbook(path, edition="premium", theme_name="berry",
                   mode="blank", protect=None, images=True):
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
    stats["sheets"] = len(bk.order)
    stats["size"] = os.path.getsize(path)
    return stats


def build_all(outdir, protect=None, images=True):
    """The curated six-file Etsy product set."""
    os.makedirs(outdir, exist_ok=True)
    combos = [("premium", "berry", "demo"), ("premium", "berry", "blank"),
              ("premium", "mint", "blank"), ("basic", "berry", "blank"),
              ("basic", "mint", "blank"), ("basic", "berry", "demo")]
    out = []
    for edition, theme_name, mode in combos:
        name = product_filename(edition, theme_name, mode)
        path = os.path.join(outdir, name)
        stats = build_workbook(path, edition, theme_name, mode,
                               protect=protect, images=images)
        out.append((name, stats))
    return out
