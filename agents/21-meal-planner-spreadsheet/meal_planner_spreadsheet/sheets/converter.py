"""
Converter - unit conversions and a live converter you can use.

The reference table below holds the conversion factors between the units you
use most.  The calculator at the top looks the factor up from that table, so
add your own pairs (for example 'cup' to 'g' for flour) and the calculator
handles them straight away.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

CATEGORIES = ["Weight", "Volume", "Count", "Temperature", "Oven", "Tin size"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    columns = [
        Col("from_unit", "From", 12, "text", group="conversion"),
        Col("to_unit", "To", 12, "text"),
        Col("factor", "Multiply by", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 1000000}),
        Col("category", "Category", 13, "select",
            validate={"type": "list", "source": CATEGORIES}),
        Col("example", "Example", 30, "text"),
        Col("reverse", "Reverse", 22, "calc",
            formula='=IF(OR({from_unit}{r}="",{factor}{r}=""),"",'
                    '{to_unit}{r}&" to "&{from_unit}{r}&": divide by "'
                    '&TEXT({factor}{r},"0.####"))'),
        Col("status", "Status", 14, "calc",
            formula='=IF({from_unit}{r}="","",'
                    'IF({factor}{r}=0,"Check the factor","OK"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Converter",
        title="Converter",
        subtitle="Unit conversions, plus a calculator you can use while you "
                 "cook",
        columns=columns,
        rows=cfg.row_count("Converter"),
        header_row=22,
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 14)
    ws.set_column(3, 3, 14)
    ws.set_column(4, 4, 34)
    ws.set_column(5, 5, 24)
    ws.set_column(6, 6, 14)
    ws.set_column(7, 7, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 6, "CONVERTER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 6,
                   "Unit conversions, plus a calculator you can use while "
                   "you cook", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 6,
                   "  |  Recipes   |   Ingredients   |   Pantry   |   "
                   "Weekly Planner   |   Help", f["nav"])

    from_rng = reg.rng("Converter", "from_unit")
    to_rng = reg.rng("Converter", "to_unit")
    factor_rng = reg.rng("Converter", "factor")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 6, "  QUICK CONVERTER", f["section"])

    ws.write(5, 0, "Quantity", f["label"])
    ws.write_number(5, 1, 250, f["input_number"])
    ws.write(6, 0, "From", f["label"])
    ws.write_string(6, 1, "g", f["input_select"])
    ws.write(6, 2, "To", f["label"])
    ws.write_string(6, 3, "oz", f["input_select"])
    ws.write(7, 0, "Result", f["label"])
    ws.write_formula(
        7, 1,
        '=IFERROR($B$6*IFERROR(INDEX(' + factor_rng + ',MATCH(1,INDEX(('
        + from_rng + '=$B$7)*(' + to_rng + '=$D$7),0),0)),"?"),"not in table")',
        f["kpi_value"])
    ws.write(7, 2, "Reverse", f["label"])
    ws.write_formula(
        7, 3,
        '=IFERROR($B$6/IFERROR(INDEX(' + factor_rng + ',MATCH(1,INDEX(('
        + from_rng + '=$B$7)*(' + to_rng + '=$D$7),0),0)),"?"),"not in table")',
        f["kpi_value"])
    ws.set_row(7, 30)

    ws.data_validation(5, 1, 5, 1, {"validate": "decimal",
                                    "criteria": "between",
                                    "minimum": 0, "maximum": 1000000,
                                    "error_type": "warning",
                                    "error_title": "Check this number",
                                    "error_message": "Enter a quantity to "
                                    "convert."})
    ws.data_validation(6, 1, 6, 1,
                       {"validate": "list", "source": "=" + from_rng})
    ws.data_validation(6, 3, 6, 3,
                       {"validate": "list", "source": "=" + to_rng})

    # ---- oven temperatures -------------------------------------------------
    ws.set_row(9, 22)
    ws.merge_range(9, 0, 9, 6, "  OVEN TEMPERATURES", f["section"])
    oven = [("Gas mark", "Fan (C)", "Conventional (C)", "Fahrenheit"),
            ("1/4", 110, 120, 250), ("1/2", 120, 130, 265),
            ("1", 140, 150, 300), ("2", 150, 160, 325),
            ("3", 160, 180, 350), ("4", 170, 190, 375),
            ("5", 180, 200, 400), ("6", 190, 210, 425),
            ("7", 200, 220, 450), ("8", 210, 230, 475),
            ("9", 220, 240, 500)]
    for i, row in enumerate(oven):
        style = f["header"] if i == 0 else f["calc_center"]
        for j, value in enumerate(row):
            ws.write(10 + i, j, value, style)

    writer.write_note(ws, 20, 0,
                  "Add a pair of units to the table below and the quick "
                  "converter above picks it up immediately. Use the factor "
                  "column for 'multiply the From unit by this to get the To "
                  "unit'.", width=7)

    writer.register(ws, spec, sample_index=writer.samples.get("Converter"))
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.primary_mid)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
