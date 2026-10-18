"""The format book.

One Excel cell format per style key.  The palette lives in
:mod:`cleaning_business_spreadsheet.config`.
"""

from __future__ import annotations

from typing import Any, Dict

from .config import Palette
from .layout import DATA_ROW, HEADER_ROW, NAV_ROW, TITLE_ROW, SheetSpec

TITLE_ROWS_SLICE = (TITLE_ROW, NAV_ROW)   # 1-based, inclusive
HEADER_BAND = HEADER_ROW


class FormatBook:
    """Builds (and caches) every :class:`xlsxwriter.format.Format` used."""

    def __init__(self, workbook: Any, config: Any) -> None:
        self.wb = workbook
        self.cfg = config
        self._cache: Dict[str, Any] = {}
        self._blueprints: Dict[str, Dict[str, Any]] = {}
        self._build()

    # ------------------------------------------------------------- factories
    def _fmt(self, key: str, base: str = "text", **kw: Any) -> Any:
        props = dict(self._blueprints[base])
        props.update(kw)
        self._blueprints[key] = props
        out = self.wb.add_format(props)
        self._cache[key] = out
        return out

    def _build(self) -> None:
        wb, cfg = self.wb, self.cfg
        P = Palette
        money = cfg.money_format
        base_text = {
            "font_name": "Calibri", "font_size": 11,
            "valign": "top", "text_wrap": True,
        }

        def add(props: Dict[str, Any]) -> Any:
            return wb.add_format(props)

        def add_key(key: str, props: Dict[str, Any]) -> Any:
            self._blueprints[key] = dict(props)
            return wb.add_format(props)

        self._cache["text"] = add_key("text", {
            **base_text,
            "border": 1, "border_color": Palette.input_border,
            "bg_color": Palette.input_bg, "locked": False})

        self._cache["text_locked"] = add_key("text_locked", {
            **base_text,
            "border": 1, "border_color": Palette.calc_border,
            "bg_color": Palette.calc_bg, "locked": True})

        self._cache["text_mid"] = add_key("text_mid", {
            **base_text, "align": "vcenter",
            "border": 1, "border_color": Palette.input_border,
            "bg_color": Palette.input_bg, "locked": False})

        self._cache["date"] = self._fmt(
            "date", "text", num_format=cfg.date_format)

        self._cache["date_locked"] = self._fmt(
            "date_locked", "text_locked", num_format=cfg.date_format)

        self._cache["int"] = self._fmt("int", "text", align="center")

        self._cache["int_locked"] = self._fmt(
            "int_locked", "text_locked", align="center")

        self._cache["decimal"] = self._fmt("decimal", "text",
                                           num_format="0.##")

        self._cache["decimal_locked"] = self._fmt(
            "decimal_locked", "text_locked", num_format="0.##")

        self._cache["calc_decimal"] = self._fmt(
            "calc_decimal", "decimal_locked", num_format="0.##",
            bold=True)

        self._cache["pct"] = self._fmt("pct", "text",
                                       num_format="0%", align="center")

        self._cache["pct_locked"] = self._fmt(
            "pct_locked", "text_locked", num_format="0%",
            align="center")

        self._cache["money"] = self._fmt("money", "text",
                                         num_format=money, align="right")

        self._cache["money_locked"] = self._fmt(
            "money_locked", "text_locked", num_format=money,
            align="right")

        self._cache["money_input"] = self._cache["money"]

        self._cache["center"] = self._fmt("center", "text",
                                          align="center", valign="vcenter")

        self._cache["center_locked"] = self._fmt(
            "center_locked", "text_locked", align="center",
            valign="vcenter")

        self._cache["check"] = self._fmt(
            "check", "center", font_size=12, align="center",
            valign="vcenter")

        self._cache["header"] = add_key("header", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": P.white, "bg_color": P.primary,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": P.primary})

        self._cache["title"] = add_key("title", {
            "font_name": "Calibri", "font_size": 18, "bold": True,
            "font_color": P.white, "bg_color": P.ink,
            "align": "left", "valign": "vcenter", "indent": 1})

        self._cache["subtitle"] = add_key("subtitle", {
            "font_name": "Calibri", "font_size": 10,
            "font_color": P.white, "bg_color": P.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            "text_wrap": True})

        self._cache["nav"] = add_key("nav", {
            "font_name": "Calibri", "font_size": 9,
            "font_color": P.primary, "bg_color": P.primary_soft,
            "align": "left", "valign": "vcenter", "indent": 1})

        self._cache["section"] = add_key("section", {
            "font_name": "Calibri", "font_size": 12, "bold": True,
            "font_color": P.white, "bg_color": P.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1})

        self._cache["label"] = add_key("label", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.ink, "bg_color": P.primary_soft,
            "valign": "vcenter", "border": 1,
            "border_color": P.calc_border, "indent": 1})

        self._cache["input"] = add_key("input", {
            "font_name": "Calibri", "font_size": 11,
            "font_color": P.ink, "bg_color": P.input_bg,
            "valign": "vcenter", "border": 1,
            "border_color": Palette.input_border, "locked": False,
            "indent": 1})

        self._cache["input_money"] = self._fmt(
            "input_money", "input", num_format=money, align="right")

        self._cache["input_pct"] = self._fmt(
            "input_pct", "input", num_format="0.0%", align="right")

        self._cache["input_int"] = self._fmt(
            "input_int", "input", num_format="0", align="right")

        self._cache["input_date"] = self._fmt(
            "input_date", "input", num_format=cfg.date_format,
            align="center")

        self._cache["calc"] = add_key("calc", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.ink, "bg_color": P.calc_bg,
            "valign": "vcenter", "border": 1,
            "border_color": Palette.calc_border, "locked": True,
            "indent": 1})

        self._cache["calc_money"] = self._fmt(
            "calc_money", "calc", num_format=money, align="right")

        self._cache["calc_pct"] = self._fmt(
            "calc_pct", "calc", num_format="0%", align="right")

        self._cache["calc_int"] = self._fmt(
            "calc_int", "calc", num_format="0", align="right")

        self._cache["calc_date"] = self._fmt(
            "calc_date", "calc", num_format=cfg.date_format,
            align="center")

        self._cache["calc_day"] = self._fmt(
            "calc_day", "calc", num_format="d", align="center")

        self._cache["calc_month"] = self._fmt(
            "calc_month", "calc", num_format="mmm yyyy",
            align="center")

        self._cache["note"] = add_key("note", {
            "font_name": "Calibri", "font_size": 10,
            "font_color": P.grey_text, "bg_color": P.note_bg,
            "valign": "top", "text_wrap": True, "border": 1,
            "border_color": P.line, "indent": 1})

        self._cache["warning"] = add_key("warning", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.warn_text, "bg_color": P.warn_bg,
            "valign": "vcenter", "border": 1,
            "border_color": P.warn_text, "indent": 1})

        self._cache["good"] = add_key("good", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.good_text, "bg_color": P.good_bg,
            "valign": "vcenter", "border": 1,
            "border_color": P.good_text, "indent": 1})

        self._cache["bad"] = add_key("bad", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.bad_text, "bg_color": P.bad_bg,
            "valign": "vcenter", "border": 1,
            "border_color": P.bad_text, "indent": 1})

        self._cache["info"] = add_key("info", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.info_text, "bg_color": P.info_bg,
            "valign": "vcenter", "border": 1,
            "border_color": P.info_text, "indent": 1})

        self._cache["total_label"] = add_key("total_label", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.white, "bg_color": P.primary,
            "valign": "vcenter", "border": 1, "border_color": P.primary,
            "indent": 1})

        self._cache["total_money"] = self._fmt(
            "total_money", "total_label", num_format=money,
            align="right", indent=0)

        self._cache["total_pct"] = self._fmt(
            "total_pct", "total_label", num_format="0%",
            align="center", indent=0)

        self._cache["total_int"] = self._fmt(
            "total_int", "total_label", num_format="0",
            align="center", indent=0)

        self._cache["total_text"] = self._fmt(
            "total_text", "total_label", indent=0)

        self._cache["link"] = add_key("link", {
            "font_name": "Calibri", "font_size": 11,
            "font_color": P.primary, "bold": True,
            "valign": "vcenter", "border": 1,
            "border_color": Palette.input_border, "locked": False,
            "indent": 1})

        self._cache["print_label"] = add_key("print_label", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.ink, "valign": "vcenter", "indent": 1})

        self._cache["print_value"] = add_key("print_value", {
            "font_name": "Calibri", "font_size": 11,
            "font_color": P.ink, "valign": "vcenter", "indent": 1,
            "bottom": 1, "bottom_color": P.line})

        self._cache["print_money"] = self._fmt(
            "print_money", "print_value", num_format=money,
            align="right")

        self._cache["print_date"] = self._fmt(
            "print_date", "print_value", num_format=cfg.date_format)

        self._cache["print_title"] = add_key("print_title", {
            "font_name": "Calibri", "font_size": 20, "bold": True,
            "font_color": P.ink, "valign": "vcenter"})

        self._cache["print_sub"] = add_key("print_sub", {
            "font_name": "Calibri", "font_size": 11,
            "font_color": P.grey_text, "valign": "vcenter"})

        self._cache["print_header"] = add_key("print_header", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": P.white, "bg_color": P.primary,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": P.primary})

        self._cache["print_cell"] = add_key("print_cell", {
            "font_name": "Calibri", "font_size": 10,
            "font_color": P.ink, "valign": "top", "text_wrap": True,
            "border": 1, "border_color": P.line})

        self._cache["print_cell_money"] = self._fmt(
            "print_cell_money", "print_cell", num_format=money,
            align="right")

        self._cache["print_cell_date"] = self._fmt(
            "print_cell_date", "print_cell", num_format=cfg.date_format)

        self._cache["print_total"] = add_key("print_total", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": P.white, "bg_color": P.primary_mid,
            "valign": "vcenter", "border": 1,
            "border_color": P.primary_mid, "indent": 1})

        self._cache["print_total_money"] = self._fmt(
            "print_total_money", "print_total", num_format=money,
            align="right", indent=0)

        self._cache["checkbox"] = self._fmt(
            "checkbox", "center", font_size=12)

        self._cache["time"] = self._fmt(
            "time", "text", num_format=cfg.time_format, align="center")

        self._cache["time_locked"] = self._fmt(
            "time_locked", "text_locked", num_format=cfg.time_format,
            align="center")

    # --------------------------------------------------------------- lookup
    def __getitem__(self, key: str) -> Any:
        try:
            return self._cache[key]
        except KeyError:
            raise KeyError(f"unknown format style '{key}'") from None

    def formula_style(self, col: Any) -> str:
        """The style a calculated column should use."""
        if not col.is_formula:
            return col.style
        style = col.style
        if style == "text":
            return "text_locked"
        return style if style.endswith("_locked") else f"{style}_locked"

    # ------------------------------------------------- sheet dressing pieces
    def title_band(self, ws: Any, spec: SheetSpec, end_col: int) -> None:
        P = Palette
        ws.merge_range(TITLE_ROW - 1, 0, TITLE_ROW - 1, end_col,
                       f"{spec.name}  ·  {spec.title}", self["title"])
        sub = spec.subtitle or self.cfg.product_name
        ws.merge_range(NAV_ROW - 1, 0, NAV_ROW - 1, end_col, sub,
                       self["subtitle"])
        ws.set_row(TITLE_ROW - 1, 30)
        ws.set_row(NAV_ROW - 1, 18)
        del P

    def header_row(self, ws: Any, spec: SheetSpec) -> None:
        row = spec.header_row - 1
        for i, col in enumerate(spec.columns):
            ws.write(row, i, col.header, self["header"])
        ws.set_row(row, 32)
