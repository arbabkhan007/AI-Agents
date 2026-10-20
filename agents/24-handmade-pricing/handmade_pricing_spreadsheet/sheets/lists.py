"""The Lists tab.

Every drop down in the workbook points at a defined name that lives here, so a
maker can add "Ceramics & pottery" or a new waste reason in one place and it
appears in every list on every tab. Below the lists sit the small factor tables
the calculators read: unit conversions, how much harder a Hard pattern is than
an Easy one, what a size L adds to a pattern, what a 24 hour rush costs, and
the margins the Scenarios tab compares.

The defined names are created by this module because only the workbook can
register them, and only after the values are on the sheet.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from ..config import (PRICING_SCENARIOS, ROUNDING_RULES, UNIT_CONVERSIONS,
                      VOLUME_STEPS, Config, Palette)
from ..layout import col_letter, quote_sheet
from ..writer import SheetWriter
from .common import (DIFFICULTY_FACTORS, LISTS, LIST_USED_BY, RUSH_FACTORS,
                     SIZE_FACTORS)

P = Palette

NAME = "Lists"

#: how many lists sit side by side in one band
BLOCK_COLS = 9
#: column the first list starts in (column A is a narrow gutter)
FIRST_COL = 1

SUBTITLE = ("Every drop down in the workbook reads from this tab. Add a value "
            "here and it appears in the list on every other tab.")

HELP = ("Type your own values in the cream cells - the lists grow as you add "
        "rows. Do not rename the tab: the drop downs point at it by name.")


def _chunks(items: Sequence[Any], size: int):
    for i in range(0, len(items), size):
        yield list(items[i:i + size])


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.accent,
                        landscape=True)
    last_col = FIRST_COL + BLOCK_COLS + 1
    sheet.banner(NAME, SUBTITLE, last_col, badge=f"{len(LISTS)} lists")
    sheet.set_col(0, 0, 3.0)
    for i in range(BLOCK_COLS):
        sheet.set_col(FIRST_COL + i, FIRST_COL + i, 21.0)
    sheet.set_col(FIRST_COL + BLOCK_COLS, last_col, 16.0)

    r = sheet.note(3, HELP, last_col, height=30)

    items = list(LISTS.items())
    for block in _chunks(items, BLOCK_COLS):
        r = sheet.section(r, "Drop down lists", last_col, first_col=0)
        sheet.row_height(r, 26)
        longest = max(len(values) for _n, values in block)
        for offset, (list_name, values) in enumerate(block):
            col = FIRST_COL + offset
            used_by = LIST_USED_BY.get(list_name, "")
            sheet.ws.write_comment(
                r, col,
                f"{list_name}\nUsed on: {used_by or 'several tabs'}\n"
                f"{len(values)} values.",
                {"author": cfg.author, "width": 240, "height": 90})
            sheet.write(r, col, list_name.replace("List", ""),
                        fmts.chrome("header_left"))
            for i, value in enumerate(values):
                sheet.write(r + 1 + i, col, value,
                            fmts.cell("text", "input"))
            for i in range(len(values), longest):
                sheet.write(r + 1 + i, col, None, fmts.cell("text", "input"))
            first_excel = r + 2                     # 1 based
            last_excel = first_excel + max(len(values), 1) + 14
            book.define_name(
                list_name,
                f"={quote_sheet(NAME)}!${col_letter(col)}${first_excel}"
                f":${col_letter(col)}${last_excel}")
        r += longest + 18
        r += 1

    # ------------------------------------------------------------ factor tables
    r = sheet.section(r, "Factor tables the calculators read", last_col,
                      first_col=0)
    r = sheet.note(r, "Change a factor and every calculator that uses it "
                      "follows - a Hard pattern costs 35% more time than an "
                      "Easy one by default.", last_col, height=28)

    tables: List[Tuple[str, str, List[str], List[Tuple[str, float]], str]] = [
        ("UnitNames", "Unit conversions", ["Unit", "Base unit", "Factor"],
         [(u, 0.0) for u, _b, _f in UNIT_CONVERSIONS], "units"),
        ("DiffNames", "Difficulty factors", ["Difficulty", "Factor"],
         DIFFICULTY_FACTORS, "factors"),
        ("SizeNames", "Size factors", ["Size", "Factor"], SIZE_FACTORS,
         "factors"),
        ("RushNames", "Rush factors", ["Rush", "Factor"], RUSH_FACTORS,
         "factors"),
        ("ScenarioNames", "Pricing scenarios", ["Scenario", "Margin"],
         [(k, float(v)) for k, v in PRICING_SCENARIOS.items()], "factors"),
        ("VolumeSteps", "Forecast volumes", ["Units a month"],
         [(str(v), 0.0) for v in VOLUME_STEPS], "factors"),
        ("RoundingRules", "Rounding rules", ["Rule"],
         [(rule, 0.0) for rule in ROUNDING_RULES], "factors"),
    ]

    for anchor, title, headers, rows, kind in tables:
        r = sheet.subsection(r, title, last_col, first_col=0)
        for i, head in enumerate(headers):
            sheet.write(r, FIRST_COL + i, head, fmts.chrome("header_left"))
        sheet.row_height(r, 20)
        first_excel = r + 2
        if kind == "units":
            for i, (unit, _base, factor) in enumerate(UNIT_CONVERSIONS):
                base = _base
                sheet.write(r + 1 + i, FIRST_COL, unit,
                            fmts.cell("text", "input"))
                sheet.write(r + 1 + i, FIRST_COL + 1, base,
                            fmts.cell("text", "input"))
                sheet.write(r + 1 + i, FIRST_COL + 2, factor,
                            fmts.cell("number", "input"))
            last_excel = first_excel + len(UNIT_CONVERSIONS) - 1
            _define(book, "UnitNames", FIRST_COL, first_excel, last_excel)
            _define(book, "UnitBase", FIRST_COL + 1, first_excel, last_excel)
            _define(book, "UnitFactor", FIRST_COL + 2, first_excel,
                    last_excel)
            r += len(UNIT_CONVERSIONS) + 2
        else:
            for i, (label, factor) in enumerate(rows):
                sheet.write(r + 1 + i, FIRST_COL, label,
                            fmts.cell("text", "input"))
                if headers[-1] != "Rule":
                    sheet.write(r + 1 + i, FIRST_COL + 1, factor,
                                fmts.cell("number", "input"))
            last_excel = first_excel + max(len(rows) - 1, 0)
            _define(book, anchor, FIRST_COL, first_excel, last_excel)
            if headers[-1] != "Rule":
                _define(book, anchor.replace("Names", "Factors")
                        if anchor.endswith("Names") else anchor + "Factors",
                        FIRST_COL + 1, first_excel, last_excel)
            r += len(rows) + 2

    sheet.ws.freeze_panes(4, 0)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet


def _define(book, name: str, col: int, first_excel: int,
            last_excel: int) -> None:
    letter = col_letter(col)
    book.define_name(
        name,
        f"={quote_sheet(NAME)}!${letter}${first_excel}:${letter}${last_excel}")
