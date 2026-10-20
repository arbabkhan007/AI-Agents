"""6 Exercise Library - 152 shipped movements, fully editable.

The library is product content, not demo data: it ships in both the
filled and the blank workbook, and it feeds every exercise drop down
through the ``ExerciseNames`` defined name.
"""

from __future__ import annotations

from ..config import Config
from ..exercise_data import EXERCISES, HOW_TO
from ..layout import Col, SheetSpec
from ..writer import SheetWriter, list_from

NAME = "6 Exercise Library"


def _subs(index: int):
    """Two substitutions from the same muscle group, never the move itself."""
    muscle = EXERCISES[index][1]
    same = [i for i, ex in enumerate(EXERCISES)
            if ex[1] == muscle and i != index]
    picks = [same[index % len(same)], same[(index + 7) % len(same)]]
    return [EXERCISES[p]["name"] if isinstance(p, dict) else EXERCISES[p][0]
            for p in picks]


def library_rows():
    """The shipped rows as dictionaries for the grid (input columns)."""
    rows = []
    for i, (name, muscle, secondary, equip, pattern, diff, uni) in \
            enumerate(EXERCISES):
        sub1, sub2 = _subs(i)
        rows.append({
            "name": name, "muscle": muscle, "secondary": secondary,
            "equipment": equip, "pattern": pattern, "difficulty": diff,
            "unilateral": uni, "howto": HOW_TO[pattern],
            "sub1": sub1, "sub2": sub2,
        })
    return rows


def spec(cfg: Config) -> SheetSpec:
    rows = cfg.row_count("Exercise Library")
    return SheetSpec(
        name=NAME,
        title="6  Exercise Library",
        subtitle="152 movements shipped - rename, edit or add your own; "
                 "every drop down in the workbook reads this list.",
        tab_color="#3E897D",
        rows=rows,
        freeze_cols=2,
        help_text="Cream cells are yours. The ID numbers itself; the two "
                  "substitutions are starting suggestions from the same "
                  "muscle group - change them to what you actually reach "
                  "for when a station is taken.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="X-"&TEXT(ROW()-{first}+1,"000")'),
            Col("name", "Exercise", 30, "text",
                note="The name every other tab uses in its drop down."),
            Col("muscle", "Muscle group", 14, "text",
                validate=list_from("ListMuscle")),
            Col("secondary", "Secondary muscles", 20, "text"),
            Col("equipment", "Equipment", 14, "text",
                validate=list_from("ListEquipment")),
            Col("pattern", "Movement pattern", 14, "text",
                validate=list_from("ListPattern")),
            Col("difficulty", "Difficulty", 13, "text",
                validate=list_from("ListDifficulty")),
            Col("unilateral", "One side at a time?", 12, "flag",
                validate={"validate": "list", "source": ["Yes", "No"]}),
            Col("howto", "How to do it", 46, "wrap"),
            Col("sub1", "Substitution 1", 24, "text"),
            Col("sub2", "Substitution 2", 24, "text"),
            Col("notes", "Injury & modification notes", 34, "wrap",
                note="Travel with the exercise: 'swap for neutral grip, "
                     "shoulder friendly'."),
        ],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    """Write the shipped library into the input columns of both builds."""
    spec_ = reg[NAME]
    first = spec_.first_data_row
    keys = ["name", "muscle", "secondary", "equipment", "pattern",
            "difficulty", "unilateral", "howto", "sub1", "sub2"]
    for offset, row in enumerate(library_rows()):
        if offset >= spec_.rows:
            break
        excel_row = first + offset
        for key in keys:
            sheet.write(excel_row - 1, spec_.index(key), row[key],
                        sheet.f.cell(spec_.col(key).style, "input"))
