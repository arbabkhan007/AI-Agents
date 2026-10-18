"""Sheet writer.

Turns a :class:`~cleaning_business_spreadsheet.layout.SheetSpec` into a real
XlsxWriter worksheet: title band, header row, data rows (formulas resolved
through the :class:`~cleaning_business_spreadsheet.layout.Registry`),
validations, notes, conditional formats and the hide-away helper columns.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from xlsxwriter.utility import xl_col_to_name

from .layout import (DATA_ROW, HEADER_ROW, Col, Registry, SheetSpec,
                     cell_ref, quote_sheet)


class SheetWriter:
    """Writes register sheets from their specifications."""

    def __init__(self, workbook: Any, formats: Any, registry: Registry,
                 config: Any) -> None:
        self.wb = workbook
        self.fmts = formats
        self.reg = registry
        self.cfg = config

    # ------------------------------------------------------------------ main
    def write_spec(self, spec: SheetSpec, samples: Optional[List[Dict]] = None
                   ) -> Any:
        ws = self.wb.add_worksheet(spec.name)
        if spec.tab_color:
            ws.set_tab_color(spec.tab_color)

        fmts = self.fmts
        ncols = len(spec.columns)
        end_col = max(ncols - 1, 0)

        # column widths / formats
        for i, col in enumerate(spec.columns):
            style = fmts.formula_style(col) if col.is_formula else col.style
            ws.set_column(i, i, col.width, fmts[style])
            if col.hidden:
                ws.set_column(i, i, col.width, fmts[style], {"hidden": True})

        # title band + header
        fmts.title_band(ws, spec, end_col)
        fmts.header_row(ws, spec)

        # data rows
        samples = samples if samples is not None else spec.samples
        self._write_rows(ws, spec, samples)

        # data validation, notes, conditional formats
        self._apply_validations(ws, spec)
        self._apply_notes(ws, spec)
        self._apply_conditional_formats(ws, spec)

        # freeze panes + filters + gridlines
        freeze_row = spec.freeze_at or spec.first_data_row
        ws.freeze_panes(freeze_row - 1, spec.freeze_cols)
        ws.autofilter(spec.header_row - 1, 0,
                      spec.last_data_row - 1, end_col)
        ws.hide_gridlines(2)
        ws.set_default_row(16)
        if self.cfg.protect_sheets:
            ws.protect(self.cfg.password, {
                "select_unlocked_cells": True,
                "select_locked_cells": True,
                "autofilter": True,
                "sort": True,
            })
        return ws

    # ------------------------------------------------------------- data rows
    def _write_rows(self, ws: Any, spec: SheetSpec,
                    samples: List[Dict]) -> None:
        fmts, reg = self.fmts, self.reg
        first = spec.first_data_row
        n_cols = len(spec.columns)

        for offset in range(spec.rows):
            r = first + offset                    # 1-based Excel row
            xr = r - 1                            # 0-based xlsxwriter row
            sample = samples[offset] if offset < len(samples) else None
            banded = (offset % 2 == 1)

            for i, col in enumerate(spec.columns):
                if col.is_formula:
                    formula = reg.render(col.formula, row=r, spec=spec)
                    style = fmts.formula_style(col)
                    ws.write_formula(xr, i, formula, fmts[style], None)
                    continue

                style = col.style
                value = None
                if sample:
                    value = sample.get(col.key)
                fmt = fmts[style]
                if value is None:
                    ws.write_blank(xr, i, None, fmt)
                elif isinstance(value, bool):
                    ws.write_boolean(xr, i, value, fmt)
                elif isinstance(value, (int, float)):
                    ws.write_number(xr, i, value, fmt)
                else:
                    ws.write(xr, i, value, fmt)
            del banded

    # ------------------------------------------------------------ validation
    def _apply_validations(self, ws: Any, spec: SheetSpec) -> None:
        reg = self.reg
        first, last = spec.first_data_row, spec.last_data_row
        for i, col in enumerate(spec.columns):
            if col.is_formula or not col.validate:
                continue
            v = dict(col.validate)
            dtype = v.pop("type", None)
            if dtype is None:
                continue
            cell_area = (first - 1, i, last - 1, i)
            params: Dict[str, Any] = {"validate": dtype}
            params.update(v)
            # resolve [[...]] tokens inside criteria ranges
            for key in ("source", "minimum", "maximum", "criteria"):
                val = params.get(key)
                if isinstance(val, str) and "[[" in val:
                    params[key] = reg.render(val, spec=spec)
            ws.data_validation(*cell_area, params)

    # ------------------------------------------------------------------ notes
    def _apply_notes(self, ws: Any, spec: SheetSpec) -> None:
        header = spec.header_row - 1
        for i, col in enumerate(spec.columns):
            if col.note:
                ws.write_comment(header, i, col.note,
                                 {"author": self.cfg.author,
                                  "width": 320, "height": 120})

    # -------------------------------------------------- conditional formats
    def _apply_conditional_formats(self, ws: Any, spec: SheetSpec) -> None:
        fmts, reg = self.fmts, self.reg
        first, last = spec.first_data_row, spec.last_data_row
        for i, col in enumerate(spec.columns):
            for rule in col.cf:
                params = dict(rule)
                kind = params.pop("type", "text")
                style = fmts[params.pop("style")]
                area = (first - 1, i, last - 1, i)
                if kind == "text":
                    ws.conditional_format(*area, {
                        "type": "text",
                        "criteria": params.pop("criteria"),
                        "value": params.pop("value"),
                        "format": style})
                elif kind == "cell":
                    value = params.pop("value")
                    if isinstance(value, str) and "[[" in value:
                        value = reg.render(value, spec=spec)
                    ws.conditional_format(*area, {
                        "type": "cell",
                        "criteria": params.pop("criteria"),
                        "value": value,
                        "format": style})
                elif kind == "formula":
                    criteria = params.pop("criteria")
                    ws.conditional_format(*area, {
                        "type": "formula",
                        "criteria": reg.render(criteria, first, spec),
                        "format": style})


def write_title_band(ws: Any, fmts: Any, title: str, subtitle: str,
                     end_col: int, *, subtitle_row: int = 2) -> None:
    """Standalone title band for hand built (non register) sheets."""
    ws.merge_range(0, 0, 0, end_col, title, fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(subtitle_row, 0, subtitle_row, end_col, subtitle,
                   fmts["subtitle"])
    ws.set_row(subtitle_row, 18)
    ws.hide_gridlines(2)
