"""9 Body Measurements - eleven sites, four custom, ratios and Navy.

The register stores what the tape said, in the stamped unit.  Ratios
are unit-free; the waist-to-height ratio and the optional Navy body-fat
estimate convert to centimetres inside the formula.  The per-site
summary block (first, latest, change, per cent change) is written by
``decorate`` so it never needs an array formula.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec, col_letter, quote_sheet
from ..writer import SheetWriter, date_check, number_check
from . import common as C
from .. import sample_data

NAME = "9 Body Measurements"

SITES = [
    ("neck", "Neck"), ("shoulders", "Shoulders"), ("chest", "Chest"),
    ("arms", "Arm (R)"), ("forearms", "Forearm (R)"), ("waist", "Waist"),
    ("hips", "Hips"), ("thighs", "Thigh (R)"), ("calves", "Calf (R)"),
    ("c1", "Custom site 1"), ("c2", "Custom site 2"),
    ("c3", "Custom site 3"), ("c4", "Custom site 4"),
]


def _cm(key: str, row: str) -> str:
    return C.cm_from("{%s}%s" % (key, row), "{stamp}%s" % row)


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("id", "ID", 8, "id",
            formula='="M-"&TEXT(ROW()-{first}+1,"000")'),
        Col("date", "Date", 12, "date", validate=date_check()),
    ]
    for key, label in SITES:
        cols.append(Col(key, label, 10, "number1",
                        validate=number_check(5, 250),
                        note="Tape measure, same time of day each time."))
    cols += [
        Col("stamp", "Unit", 7, "flag",
            validate={"validate": "list", "source": ["cm", "in"],
                      "ignore_blank": True}),
        Col("whr", "Waist : hip", 11, "number",
            formula='IF(OR({waist}{r}="",{hips}{r}="",{hips}{r}=0),"",'
                    '{waist}{r}/{hips}{r})',
            note="Unit-free ratio. Under 0.90 (men) / 0.85 (women) is the "
                 "usual WHO line - context, not a verdict."),
        Col("whtr", "Waist : height", 11, "number",
            formula='IF(OR({waist}{r}="",HeightCm=0),"",' +
                    _cm("waist", "{r}") + '/HeightCm)',
            note="Under about 0.5 is the common guide. An estimate from "
                 "your numbers, not medical advice."),
        Col("navy", "Navy body fat %", 13, "number1",
            formula='IF(OR(' + _cm("neck", "{r}") + '="",'
                    + _cm("waist", "{r}") + '="",' + _cm("hips", "{r}")
                    + '=""),"",'
                    'IF(Sex="Male",495/(1.0324*LOG10(' +
                    _cm("waist", "{r}") + '-' + _cm("neck", "{r}") +
                    ')-0.19077*LOG10(HeightCm))-450,'
                    '495/(1.29579*LOG10(' + _cm("waist", "{r}") + '+'
                    + _cm("hips", "{r}") + '-' + _cm("neck", "{r}") +
                    ')-0.35004*LOG10(HeightCm))-450))',
            note="US Navy tape method. Clearly an estimate - tape "
                 "measurements carry a couple of points of error."),
        Col("notes", "Notes", 22, "wrap"),
    ]
    return SheetSpec(
        name=NAME,
        title="9  Body Measurements",
        subtitle="The tape tells you what the scales cannot - thirteen "
                 "sites, ratios and an optional Navy estimate.",
        tab_color="#3E897D",
        rows=cfg.row_count("Body Measurements"),
        freeze_cols=3,
        help_text="Measure in the stamped unit or the workbook unit. The "
                  "summary on the right compares your first and latest "
                  "entry per site. Custom sites are yours to name in the "
                  "header (unprotect first).",
        columns=cols,
        samples=sample_data.measurement_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    """Per-site summary block: first vs latest, change and per cent."""
    spec_ = reg[NAME]
    q = quote_sheet(NAME)
    dates = f"{q}!${spec_.letter('date')}${spec_.first_data_row}:" \
            f"${spec_.letter('date')}${spec_.last_data_row}"
    top = spec_.last_data_row + 3
    row = sheet.section(top, "PER-SITE SUMMARY - FIRST VS LATEST", 8)
    row = sheet.table_head(row, 0, ["Site", "First", "Latest", "Change",
                                    "Change %"],
                           widths=[16, 10, 10, 10, 10])
    first_date = f"MIN({dates})"
    last_date = f"MAX({dates})"
    for key, label in SITES:
        letter = col_letter(spec_.index(key))
        rng = f"{q}!${letter}${spec_.first_data_row}:" \
              f"${letter}${spec_.last_data_row}"
        first_v = f"IF(COUNT({rng})=0,\"\",INDEX({rng},MATCH({first_date}," \
                  f"{dates},0)))"
        last_v = f"IF(COUNT({rng})=0,\"\",INDEX({rng},MATCH({last_date}," \
                 f"{dates},0)))"
        sheet.write(row, 0, label, sheet.f.calc("text"))
        sheet.formula(row, 1, "=" + first_v, sheet.f.calc("number1"))
        sheet.formula(row, 2, "=" + last_v, sheet.f.calc("number1"))
        sheet.formula(row, 3, f'=IF(OR(B{row + 1}="",C{row + 1}=""),"", '
                              f'C{row + 1}-B{row + 1})',
                      sheet.f.calc("number1"))
        sheet.formula(row, 4, f'=IF(OR(B{row + 1}="",B{row + 1}=0,'
                              f'C{row + 1}=""),"",(C{row + 1}-B{row + 1})/'
                              f'B{row + 1})',
                      sheet.f.calc("percent"))
        row += 1
    sheet.note(row + 1, "Change is in the unit you typed. Percent change "
                        "is unit-free, which is why it is the number to "
                        "compare across sites.", 8, height=24)
    sheet.finish(freeze_row=4, freeze_col=2,
                 print_area=f"$A$1:${col_letter(spec_.last_col_index)}$"
                            f"{spec_.last_data_row}")
