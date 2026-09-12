"""
Orchestrator: turns (edition, theme, mode) into a finished .xlsx.

Editions
    basic    dashboard + gift tracker + budget + shopping + setup + guide
    premium  everything: wish list, orders, wrapping, cards, stockings, to-do

Themes
    festive  cream / pine / burgundy / gold
    minimal  white / sage / clay

Modes
    blank    clean, ready-to-use template (lists + checklist pre-seeded)
    demo     filled-in example family, for listing screenshots
"""

import os

from . import theme as themes
from .book import Book
from .demo import Model
from .sheets import (budget, cards, dashboard, data, gifts, guide, orders,
                     setup, shopping, stockings, todo, wishlist, wrapping)

BUILDERS = {
    "data": data.build,
    "setup": setup.build,
    "gifts": gifts.build,
    "budget": budget.build,
    "shopping": shopping.build,
    "wishlist": wishlist.build,
    "orders": orders.build,
    "wrapping": wrapping.build,
    "cards": cards.build,
    "stockings": stockings.build,
    "todo": todo.build,
    "dashboard": dashboard.build,
    "guide": guide.build,
}

# Build order: the hidden engine first, then the tabs left-to-right.
BUILD_ORDER = ["data", "setup", "gifts", "budget", "shopping", "wishlist",
               "orders", "wrapping", "cards", "stockings", "todo",
               "dashboard", "guide"]


def build_workbook(path, edition="premium", theme_name="festive",
                   mode="blank", protect=None, images=True):
    if edition not in ("basic", "premium"):
        raise ValueError("edition must be 'basic' or 'premium'")
    if mode not in ("blank", "demo"):
        raise ValueError("mode must be 'blank' or 'demo'")
    th = themes.get(theme_name)
    model = Model(mode, edition)
    bk = Book(path, th, edition=edition, mode=mode, protect=protect,
              images=images, demo=model)
    for key in BUILD_ORDER:
        if key in bk.order:
            BUILDERS[key](bk)
    bk.close()
    bk.stats["path"] = path
    bk.stats["size"] = os.path.getsize(path)
    return bk.stats


# ---------------------------------------------------------------------------
# the curated product set written to products/
# ---------------------------------------------------------------------------
def product_filename(edition, theme_name, mode):
    suffix = "_EXAMPLE" if mode == "demo" else ""
    return ("Christmas_Gift_Tracker_%s_%s%s.xlsx"
            % (edition.upper(), theme_name.capitalize(), suffix))


def build_all(outdir="products", protect=None, images=True):
    """The set of files an Etsy listing actually ships / screenshots."""
    combos = [
        ("premium", "festive", "demo"),    # listing hero + screenshots
        ("premium", "festive", "blank"),   # the product
        ("premium", "minimal", "blank"),   # second style
        ("basic", "festive", "blank"),     # the cheaper tier
        ("basic", "minimal", "blank"),
        ("basic", "festive", "demo"),      # cheaper tier screenshot
    ]
    os.makedirs(outdir, exist_ok=True)
    stats = []
    for edition, theme_name, mode in combos:
        path = os.path.join(outdir,
                            product_filename(edition, theme_name, mode))
        stats.append(build_workbook(path, edition, theme_name, mode,
                                    protect=protect, images=images))
    return stats
