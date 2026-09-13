"""
Orchestrator: turns (edition, theme, mode) into a finished .xlsx.

Editions
    basic    dashboard + clients + events + quote calculator + expenses +
             payments + setup + guide  (the essentials)
    premium  everything: menu costing, inventory, shopping list, staff,
             equipment, suppliers, calendar, P&L/reports, tax tracker,
             checklists and the printable invoice

Themes
    classic  cream / espresso / copper / brass
    fresh    white / basil / tomato / lemon

Modes
    blank    clean, ready-to-use template (lists + settings pre-seeded)
    demo     filled-in example business, for listing screenshots
"""

import os

from . import theme as themes
from .book import Book
from .demo import Model
from .sheets import (calendar, checklists, clients, dashboard, data,
                     equipment, events, expenses, guide, income, inventory,
                     invoice, menu, quote, reports, setup, shopping, staff,
                     suppliers, tax)

BUILDERS = {
    "data": data.build,
    "setup": setup.build,
    "dashboard": dashboard.build,
    "clients": clients.build,
    "events": events.build,
    "quote": quote.build,
    "menu": menu.build,
    "inventory": inventory.build,
    "shopping": shopping.build,
    "expenses": expenses.build,
    "income": income.build,
    "staff": staff.build,
    "equipment": equipment.build,
    "suppliers": suppliers.build,
    "calendar": calendar.build,
    "reports": reports.build,
    "tax": tax.build,
    "checklists": checklists.build,
    "invoice": invoice.build,
    "guide": guide.build,
}

# Build order: the hidden engine first, then the tabs left-to-right.
BUILD_ORDER = ["data", "setup", "dashboard", "clients", "events", "quote",
               "menu", "inventory", "shopping", "expenses", "income",
               "staff", "equipment", "suppliers", "calendar", "reports",
               "tax", "checklists", "invoice", "guide"]


def build_workbook(path, edition="premium", theme_name="classic",
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
    return ("Catering_Business_Manager_%s_%s%s.xlsx"
            % (edition.upper(), theme_name.capitalize(), suffix))


def build_all(outdir="products", protect=None, images=True):
    """The set of files an Etsy listing actually ships / screenshots."""
    combos = [
        ("premium", "classic", "demo"),    # listing hero + screenshots
        ("premium", "classic", "blank"),   # the product
        ("premium", "fresh", "blank"),     # second style
        ("basic", "classic", "blank"),     # the cheaper tier
        ("basic", "fresh", "blank"),
        ("basic", "classic", "demo"),      # cheaper tier screenshot
    ]
    os.makedirs(outdir, exist_ok=True)
    stats = []
    for edition, theme_name, mode in combos:
        path = os.path.join(outdir,
                            product_filename(edition, theme_name, mode))
        stats.append(build_workbook(path, edition, theme_name, mode,
                                    protect=protect, images=images))
    return stats
