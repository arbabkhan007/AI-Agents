"""
The writer.

Turns every :class:`~meal_planner_spreadsheet.layout.SheetSpec` into real
Excel rows: the coloured title band, the frozen header row, one pre-built row
per register slot with its validation, conditional format and formula, plus
the sheet protection that locks the calculated columns and leaves the cream
input cells editable.

Nothing here hard codes a column letter - the layout engine renders every
formula template against the registry, so columns can be added, removed or
reordered in the sheet modules without touching the writer.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, Iterable, List, Optional, Sequence

dt_date = _dt.date
dt_datetime = _dt.datetime

try:
    from .config import Config, Palette
    from .layout import (DATA_ROW, HEADER_ROW, NAV_ROW, SUBTITLE_ROW,
                         TITLE_ROW, Col, Registry, SheetSpec, col_letter)
except ImportError:                       # pragma: no cover
    from config import Config, Palette
    from layout import (DATA_ROW, HEADER_ROW, NAV_ROW, SUBTITLE_ROW,
                        TITLE_ROW, Col, Registry, SheetSpec, col_letter)


#: Worksheet protection options.  In XlsxWriter a True value means the
#: action is *allowed* while the sheet is protected.  Formula cells are
#: locked by their format and input cells are unlocked by theirs, so the
#: only thing protection has to do is stop the calculated columns being
#: overtyped.  Selection of both locked and unlocked cells must stay
#: allowed, otherwise the buyer cannot click into the cream input cells
#: at all; the filter and sort buttons have to keep working too.
PROTECT_OPTIONS: Dict[str, bool] = {
    "objects": False,
    "scenarios": False,
    "format_cells": True,
    "format_columns": True,
    "format_rows": True,
    "insert_columns": False,
    "insert_rows": True,
    "insert_hyperlinks": True,
    "delete_columns": False,
    "delete_rows": True,
    "select_locked_cells": True,
    "sort": True,            # filtering / sorting stays available
    "autofilter": True,
    "pivot_tables": False,
    "select_unlocked_cells": True,
}


#: style key -> format name.  `text` deliberately falls back to the calc
#: version when the column is a formula column, so a column can be declared
#: as a plain text column and still be written as a locked formula.
INPUT_STYLES = {
    "text": "input_text",
    "text_wrap": "input_text_wrap",
    "number": "input_number",
    "money": "input_money",
    "date": "input_date",
    "percent": "input_percent",
    "select": "input_select",
    "dropdown": "input_dropdown",
    "lookup": "input_lookup",
    "plain": "input_plain",
    "check": "check",
    "weekday": "input_select",
    "money0": "input_money",
    "percent0": "input_percent",
}

CALC_STYLES = {
    "text": "calc_text",
    "text_wrap": "calc_locked",
    "number": "calc_number",
    "money": "calc_money",
    "money0": "calc_money_0",
    "date": "calc_date",
    "percent": "calc_percent",
    "percent0": "calc_number",
    "select": "calc_center",
    "dropdown": "calc_center",
    "lookup": "calc_text",
    "plain": "plain",
    "check": "calc_center",
    "weekday": "calc_weekday",
    "badge": "calc_badge",
    "flag": "calc_flag",
}


class Writer:
    """Writes sheets into an XlsxWriter workbook."""

    def __init__(self, workbook, cfg: Config, registry: Registry,
                 formats) -> None:
        self.wb = workbook
        self.cfg = cfg
        self.registry = registry
        self.fmt = formats
        self.nav_links: Dict[str, str] = {}
        #: {sheet name: {row offset: {column key: value}}} - example data.
        self.samples: Dict[str, Dict[int, Dict[str, Any]]] = {}

    # ------------------------------------------------------------- primitives
    def sheet(self, name: str):
        ws = self.wb.add_worksheet(name)
        if self.cfg.protect_sheets:
            # Formula cells are locked by their format and input cells are
            # unlocked by theirs, so the sheet stays fully usable while the
            # calculated columns are protected.
            ws.protect(self.cfg.password or "", dict(PROTECT_OPTIONS))
        return ws

    def style_for(self, col: Col) -> Any:
        book = CALC_STYLES if col.is_formula else INPUT_STYLES
        return self.fmt.get(book.get(col.style, "text"), "calc_text")

    # ------------------------------------------------------------- chrome
    def chrome(self, ws, spec: SheetSpec, links: Sequence[str] = ()) -> None:
        """Title band, strapline and navigation strip."""
        p = Palette
        last = spec.last_col_index
        cfg = self.cfg

        ws.set_row(TITLE_ROW - 1, 30)
        ws.set_row(SUBTITLE_ROW - 1, 18)
        ws.set_row(NAV_ROW - 1, 20)
        ws.merge_range(TITLE_ROW - 1, 0, TITLE_ROW - 1, last,
                       spec.title.upper(), self.fmt["title"])
        ws.merge_range(SUBTITLE_ROW - 1, 0, SUBTITLE_ROW - 1, last,
                       spec.subtitle or spec.help_text or cfg.product_subtitle,
                       self.fmt["subtitle"])

        # navigation strip
        ws.merge_range(NAV_ROW - 1, 0, NAV_ROW - 1, last,
                       "  |  ".join(links) if links else
                       f"{cfg.product_name}  |  v{cfg.version}",
                       self.fmt["nav"])

    def headers(self, ws, spec: SheetSpec) -> None:
        hrow = spec.header_row - 1
        ws.set_row(hrow, 32)
        for i, col in enumerate(spec.columns):
            ws.write(hrow, i, col.header, self.fmt["header"])
            if col.note:
                ws.write_comment(hrow, i, col.note,
                                 {"width": 260, "height": 90})
        ws.autofilter(spec.header_row - 1, 0, spec.last_data_row - 1,
                      spec.last_col_index)

    # ------------------------------------------------------------- data rows
    def register(self, ws, spec: SheetSpec,
                 sample_index: Optional[Dict[int, Dict[str, Any]]] = None,
                 ) -> None:
        """Write the header row and every pre-built data row."""
        self.headers(ws, spec)

        if sample_index is None:
            sample_index = self.samples.get(spec.name, {})
        samples = sample_index or {}
        for offset in range(spec.rows):
            row = spec.first_data_row + offset          # 1 based Excel row
            xrow = row - 1
            for col in spec.columns:
                style = self.style_for(col)
                if col.formula:
                    formula = self.registry.render(col.formula, row=row,
                                                   spec=spec)
                    if self._always_blank(formula):
                        # A whole-row guard keeps the sheet tidy and cheap.
                        guard = self._blank_guard(spec, row)
                        if guard:
                            formula = f'=IF({guard},"",{formula[1:]})'
                        else:
                            formula = formula
                    try:
                        ws.write_formula(xrow, spec.index(col.key), formula,
                                         style)
                    except Exception:                      # pragma: no cover
                        ws.write_formula(xrow, spec.index(col.key), "=0",
                                         style)
                    continue

                value = self._sample(samples, offset, col, row)
                if value is None:
                    ws.write_blank(xrow, spec.index(col.key), None, style)
                elif isinstance(value, str) and value.startswith("="):
                    ws.write_formula(xrow, spec.index(col.key), value, style)
                elif isinstance(value, (dt_date, dt_datetime)):
                    ws.write_datetime(xrow, spec.index(col.key), value, style)
                elif col.style in ("number", "money", "money0", "percent",
                                   "percent0", "check"):
                    try:
                        ws.write_number(xrow, spec.index(col.key),
                                        float(value), style)
                    except (TypeError, ValueError):
                        ws.write_blank(xrow, spec.index(col.key), None, style)
                else:
                    ws.write_string(xrow, spec.index(col.key), str(value),
                                    style)

            self._apply_col_extras(ws, spec, xrow)

    # ---------------------------------------------------------------- helpers
    def _sample(self, samples: Dict[int, Dict[str, Any]], offset: int,
                col: Col, row: int) -> Any:
        record = samples.get(offset)
        if not record:
            return None
        value = record.get(col.key)
        if callable(value):
            return value(row)
        return value

    @staticmethod
    def _always_blank(formula: str) -> bool:
        """True when the formula only ever returns blank."""
        body = formula[1:] if formula.startswith("=") else formula
        return body.strip() in ('""', 'IFERROR("","")')

    def _blank_guard(self, spec: SheetSpec, row: int) -> Optional[str]:
        """Return a test that is TRUE while the row is still unused."""
        for key in ("title", "name", "label", "item", "recipe", "date",
                    "meal", "slot", "task", "description"):
            try:
                letter = spec.letter(key)
            except KeyError:
                continue
            return f"${letter}{row}=\"\""
        return None

    def _apply_col_extras(self, ws, spec: SheetSpec, xrow: int) -> None:
        """Validation + conditional formats for one physical row."""
        for col in spec.columns:
            i = spec.index(col.key)
            letter = spec.letter(col.key)
            if col.validate and not col.is_formula:
                self._validation(ws, spec, col, letter, i)
            if col.cf:
                self._conditional(ws, spec, col, letter, i)

    def _validation(self, ws, spec: SheetSpec, col: Col, letter: str,
                    i: int) -> None:
        raw = dict(col.validate)
        kind = raw.pop("type", "list")
        opts: Dict[str, Any] = {"validate": kind}

        if kind == "list":
            source = raw.pop("source", None)
            if isinstance(source, str) and source.startswith("="):
                opts["source"] = source
            elif isinstance(source, (list, tuple)):
                opts["source"] = [str(s) for s in source]
            opts.setdefault("error_type", "stop")
            opts.setdefault("error_title", "Pick from the list")
            opts.setdefault("error_message",
                            col.note or f"Choose a value from the "
                            f"{col.header} list.")
        elif kind in ("integer", "decimal", "date", "time", "length"):
            # our shorthand is {"between": lo, "and": hi}; XlsxWriter calls
            # the same thing criteria/minimum/maximum
            low = raw.pop("between", None)
            high = raw.pop("and", None)
            operator = raw.pop("operator", "between" if low is not None
                               else None)
            if operator:
                opts["criteria"] = operator
            if low is not None:
                opts["minimum"] = low
            if high is not None:
                opts["maximum"] = high
            for key in ("minimum", "maximum"):
                if key in raw:
                    opts[key] = raw.pop(key)
            opts.setdefault("error_type", "warning")
            opts.setdefault("error_title", "Check this entry")
            opts.setdefault("error_message",
                            col.note or f"Enter a {kind} in this cell.")
        else:
            opts.update(raw)

        if col.note:
            opts.setdefault("input_title", col.header)
            opts.setdefault("input_message", col.note)
        opts.setdefault("show_error", True)
        opts.setdefault("show_input", True)
        ws.data_validation(spec.first_data_row - 1, i,
                           spec.last_data_row - 1, i, opts)

    def _conditional(self, ws, spec: SheetSpec, col: Col, letter: str,
                     i: int) -> None:
        for rule in col.cf:
            rule = dict(rule)
            fmt = rule.pop("format", None)
            if fmt is not None and isinstance(fmt, str):
                rule["format"] = self.fmt[fmt]
            rng = rule.pop("range", None)
            if rng:
                first = spec.first_data_row - 1
                last = spec.last_data_row - 1
                rng = self.registry.render(rng, row=None, spec=spec)
                rule_range = rng
            else:
                rule_range = (f"${letter}${spec.first_data_row}:"
                              f"${letter}${spec.last_data_row}")
            ws.conditional_format(rule_range, rule)

    # ------------------------------------------------------------- decoration
    def banding(self, ws, spec: SheetSpec, start_row: int,
                end_row: int, first_col: int, last_col: int,
                colour: str = "primary_soft") -> None:
        """Alternating row shading (applied on top of the cell formats)."""
        if end_row <= start_row:
            return
        bg = Palette.__dict__.get(colour, colour)
        fmt = self.wb.add_format({"bg_color": bg, "border": 1,
                                  "border_color": Palette.calc_border})
        for row in range(start_row, end_row + 1, 2):
            ws.conditional_format(row - 1, first_col, row - 1, last_col,
                                  {"type": "formula",
                                   "criteria": f"=MOD(ROW(),2)=0",
                                   "format": fmt})

    def sparkline(self, ws, row: int, col: int, data_range: str,
                  spark: str = "line", colour: str = None) -> None:
        opts: Dict[str, Any] = {
            "location": [row, col],
            "range": data_range,
            "type": spark,
            "markers": True,
            "high_point": True,
            "low_point": True,
            "empty_cells": "zero",
        }
        if colour:
            opts["series_color"] = colour
        try:
            ws.add_sparkline(row, col, data_range, opts)
        except Exception:                              # pragma: no cover
            pass

    def grid_off(self, ws) -> None:
        ws.hide_gridlines(2)

    def setup_print(self, ws, spec: SheetSpec, landscape: bool = True,
                    fit_width: int = 1, repeat_rows: bool = True,
                    repeat_cols: int = 0) -> None:
        ws.set_landscape()
        ws.set_paper(9)                     # A4
        ws.fit_to_pages(fit_width, 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        ws.center_horizontally()
        ws.set_header(f"&L&\"Calibri,Bold\"{self.cfg.product_name}"
                      f"&R&\"Calibri,Italic\"{spec.name}")
        ws.set_footer("&LPage &P of &N&R&D")
        if repeat_rows:
            ws.repeat_rows(0, spec.header_row - 1)
        if repeat_cols:
            ws.repeat_columns(0, repeat_cols - 1)
        ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)

    def freeze(self, ws, spec: SheetSpec) -> None:
        row = spec.freeze_at or spec.header_row
        ws.freeze_panes(row, spec.freeze_cols)

    def widths(self, ws, spec: SheetSpec) -> None:
        for i, col in enumerate(spec.columns):
            ws.set_column(i, i, col.width, None,
                          {"hidden": 1} if col.hidden else None)

    def finish_sheet(self, ws, spec: SheetSpec, links: Sequence[str] = (),
                     landscape: bool = True, banding: bool = True,
                     freeze: bool = True, print_area: bool = True) -> None:
        self.grid_off(ws)
        self.widths(ws, spec)
        if banding:
            self.banding(ws, spec, spec.first_data_row,
                         spec.last_data_row, 0, spec.last_col_index)
        if freeze:
            self.freeze(ws, spec)
        if print_area:
            self.setup_print(ws, spec, landscape=landscape)
        if spec.tab_color:
            ws.set_tab_color(spec.tab_color)
        else:
            ws.set_tab_color(Palette.primary_mid)
        for link in links:
            self.nav_links.setdefault(link, link)

    # ------------------------------------------------------------- shared UI
    def write_kpi(self, ws, row: int, col: int, label: str,
                  value_formula: str, sub: str = "",
                  style: str = "kpi_value", width: int = 3) -> None:
        """A three row KPI tile: label, value, optional sub label."""
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, label, self.fmt["kpi_label"])
        ws.merge_range(row + 1, col, row + 1, end, None,
                       self.fmt[style])
        ws.write_formula(row + 1, col, value_formula, self.fmt[style])
        if sub:
            ws.merge_range(row + 2, col, row + 2, end, sub,
                           self.fmt["kpi_sub"])
        ws.set_row(row + 1, 30)

    def write_panel(self, ws, row: int, col: int, title: str, width: int = 6,
                    height: int = 22) -> None:
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, title, self.fmt["section"])
        ws.set_row(row, height)

    def write_note(self, ws, row: int, col: int, text: str,
                   width: int = 6) -> None:
        end = min(col + width - 1, 16383)
        ws.merge_range(row, col, row, end, text, self.fmt["note"])
