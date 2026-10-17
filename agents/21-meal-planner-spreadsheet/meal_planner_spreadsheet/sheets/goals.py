"""
Goals - habit goals with a live progress bar.

Set a target, record where you are now and the bar in the progress column
fills up as you go.  The status column tells you whether you are on track
for the deadline, and the summary at the top counts how many goals are
running, hit or slipping.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

CATEGORIES = ["Waste", "Budget", "Nutrition", "Variety", "Cooking",
              "Shopping", "Health", "Family"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    columns = [
        Col("goal", "Goal", 34, "text", group="what",
            note="Say what you want to change, in your own words."),
        Col("category", "Category", 13, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("target", "Target", 11, "number", group="numbers",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("current", "Where you are now", 13, "number",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("unit", "Unit", 12, "text",
            note="e.g. meals a week, % of spend, kg a month."),
        Col("deadline", "By", 12, "date"),
        Col("progress", "Progress", 11, "calc", group="tracking",
            formula='=IF(OR({goal}{r}="",{target}{r}="",{target}{r}=0),"",'
                    'MIN(1,{current}{r}/{target}{r}))'),
        Col("status", "Status", 15, "calc",
            formula='=IF({goal}{r}="","",'
                    'IF({progress}{r}="","",'
                    'IF({progress}{r}>=1,"Goal hit",'
                    'IF({deadline}{r}="","In progress",'
                    'IF({deadline}{r}<TODAY(),"Missed deadline",'
                    'IF({progress}{r}>=0.5,"On track","Needs work"))))))'),
        Col("streak", "Current streak", 12, "number",
            validate={"type": "integer", "between": 0, "and": 9999}),
        Col("best_streak", "Best streak", 11, "number",
            validate={"type": "integer", "between": 0, "and": 9999}),
        Col("rank", "Rank", 9, "calc", group="rankings",
            formula='=IF({progress}{r}="","",'
                    'COUNTIFS({progress_first}:{progress_last},'
                    '">"&{progress}{r})+1)'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Goals",
        title="Goals",
        subtitle="Habit goals with a live progress bar",
        columns=columns,
        rows=cfg.row_count("Goals"),
        header_row=14,
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 36)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 3, 14)
    ws.set_column(4, 4, 13)
    ws.set_column(5, 5, 12)
    ws.set_column(6, 6, 12)
    ws.set_column(7, 7, 16)
    ws.set_column(8, 9, 13)
    ws.set_column(10, 10, 9)
    ws.set_column(11, 11, 34)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 8, "GOALS", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Habit goals with a live progress bar", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Dashboard   |   Settings   |   Food Waste   |   "
                   "Sustainability   |   Help", f["nav"])

    status_rng = reg.rng("Goals", "status")
    progress_rng = reg.rng("Goals", "progress")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  WHERE YOU ARE", f["section"])
    tiles = [
        ("Goals running", f'=COUNTIFS({status_rng},"<>")', "kpi_value", 1),
        ("Goals hit", f'=COUNTIFS({status_rng},"Goal hit")', "kpi_value", 3),
        ("On track", f'=COUNTIFS({status_rng},"On track")', "kpi_value", 5),
        ("Needs work", f'=COUNTIFS({status_rng},"Needs work")',
         "kpi_value", 7),
    ]
    for label, formula, style, col in tiles:
        ws.write(6, col, label, f["kpi_label"])
        ws.write_formula(7, col, formula, f[style])
    ws.set_row(7, 30)

    ws.write(9, 0, "Average progress", f["label"])
    ws.write_formula(9, 1, f'=IFERROR(AVERAGE({progress_rng}),0)',
                     f["total_percent"])
    ws.write(9, 2, "Best goal", f["label"])
    ws.write_formula(9, 3,
                     '=IFERROR(INDEX(' + reg.rng("Goals", "goal")
                     + ',MATCH(MAX(' + progress_rng + '),' + progress_rng
                     + ',0)),"")', f["calc_text"])
    ws.write(9, 4, "Longest streak", f["label"])
    ws.write_formula(9, 5,
                     '=IFERROR(MAX(' + reg.rng("Goals", "streak") + '),0)',
                     f["calc_number"])

    writer.write_note(ws, 11, 0,
                      "The progress bar is a data bar: it fills up as the "
                      "'Where you are now' column approaches the target. "
                      "Anything at 100% turns green.", width=8)

    writer.register(ws, spec)

    # progress bar + colour the status
    letter = spec.letter("progress")
    rng = f"${letter}${spec.first_data_row}:${letter}${spec.last_data_row}"
    ws.conditional_format(rng, {
        "type": "data_bar", "bar_color": Palette.primary_mid,
        "bar_solid": True, "min_type": "num", "min_value": 0,
        "max_type": "num", "max_value": 1})
    ws.conditional_format(rng, {"type": "cell", "criteria": ">=",
                                "value": 1, "format": f["status_good"]})

    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
