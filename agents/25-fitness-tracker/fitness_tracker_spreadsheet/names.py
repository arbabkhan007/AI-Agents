"""Workbook level defined names that point at the register sheets.

The static drop down lists on `16 Settings & Lists` define their own
names when that tab is built.  These are the ones that have to follow
live data - the exercise library and the food database - so they are
built from the registry once every register exists.  Each one is an
``OFFSET`` range that grows and shrinks with the number of filled rows,
which is why a new exercise appears in the log drop down the moment you
type it.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    "ExerciseNames": ("6 Exercise Library", "name"),
    "LogDates": ("5 Workout Log", "date"),
    "LogExercises": ("5 Workout Log", "exercise"),
    "WeightDates": ("8 Weight Tracker", "date"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            continue
        spec = reg[sheet]
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
