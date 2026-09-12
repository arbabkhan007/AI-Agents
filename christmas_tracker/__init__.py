"""
Christmas / Ultimate Gift Tracker - Etsy-ready Excel workbook builder.

Built on the XlsxWriter library vendored in this repository.  The package is
deliberately split into small modules so that every tab of the product can be
read (and tweaked) on its own:

    theme.py       colour palettes (festive + minimalist)
    config.py      sheet names, capacities, column maps, list contents
    styles.py      every cell format, derived from the active theme
    book.py        the build context: sheet registry, cross-sheet references
    demo.py        the optional "filled-in example" data set + aggregates
    sheets/        one module per worksheet
    workbook.py    orchestrates a full build

Entry point:  python christmas_gift_tracker.py --all
"""

from .workbook import build_workbook, build_all  # noqa: F401

__version__ = "1.0.0"
__product__ = "Ultimate Christmas Gift Tracker"
