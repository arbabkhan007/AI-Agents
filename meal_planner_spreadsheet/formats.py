"""
The format book.

One place builds every XlsxWriter format used by the workbook so the look
stays consistent: warm cream input cells, soft sage calculated cells, herb
green headers and a terracotta accent.  Sheets are protected with
``protect`` and the input cells are unlocked so the buyer can type in them
while every formula stays safe.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:                                     # normal package import
    from .config import Config, Palette
except ImportError:                      # pragma: no cover - script import
    from config import Config, Palette


class Formats:
    """Creates and caches every format the workbook needs."""

    def __init__(self, workbook, cfg: Config) -> None:
        self.wb = workbook
        self.cfg = cfg
        self.p = Palette
        self.cache: Dict[str, Any] = {}
        self._build()

    # ---------------------------------------------------------------- helpers
    def _add(self, name: str, props: Dict[str, Any]) -> Any:
        fmt = self.wb.add_format(props)
        self.cache[name] = fmt
        return fmt

    def money_fmt(self, decimals: int = 2) -> str:
        symbol = self.cfg.currency_symbol
        if decimals:
            return f"{symbol}#,##0.{'0' * decimals}"
        return f"{symbol}#,##0"

    def signed_money(self, decimals: int = 2) -> str:
        symbol = self.cfg.currency_symbol
        body = f"{symbol}#,##0.{'0' * decimals}"
        return f"{body};[Red]-{body}"

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        cfg, p = self.cfg, Palette
        locked = {"locked": True}
        unlocked = {"locked": False}

        self._add("title", {
            "font_name": "Calibri", "font_size": 16, "bold": True,
            "font_color": p.white, "bg_color": p.primary,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("subtitle", {
            "font_name": "Calibri", "font_size": 10, "italic": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("nav", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "center", "valign": "vcenter", **locked})
        self._add("nav_left", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})

        self._add("header", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.primary_mid, **locked})
        self._add("header_wide", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.primary_mid, **locked})

        # -- editable cells: cream, unlocked, thin border ---------------------
        self._add("input_text", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "indent": 1, **unlocked})
        self._add("input_text_wrap", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "top",
            "text_wrap": True, "indent": 1, **unlocked})
        self._add("input_number", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": "#,##0.##", "align": "center", **unlocked})
        self._add("input_money", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": self.signed_money(), "align": "right",
            **unlocked})
        self._add("input_date", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": cfg.date_format, "align": "center", **unlocked})
        self._add("input_percent", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "num_format": "0%", "align": "center", **unlocked})
        self._add("input_select", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "align": "center", **unlocked})
        self._add("input_dropdown", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "align": "center", "italic": True, **unlocked})
        self._add("input_lookup", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.info_text,
            "bg_color": p.info_bg, "border": 1,
            "border_color": p.input_border, "valign": "vcenter",
            "indent": 1, **unlocked})
        self._add("input_plain", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.white, "valign": "top", "text_wrap": True,
            "indent": 1, **unlocked})

        # -- calculated cells: soft sage, locked -----------------------------
        base_calc = {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.calc_bg, "border": 1,
            "border_color": p.calc_border, "valign": "vcenter",
            "indent": 1, **locked}
        self._add("calc_text", dict(base_calc))
        self._add("calc_number", dict(base_calc,
                                      num_format="#,##0.##",
                                      align="center"))
        self._add("calc_money", dict(base_calc,
                                     num_format=self.signed_money(),
                                     align="right"))
        self._add("calc_money_0", dict(base_calc,
                                       num_format=self.signed_money(0),
                                       align="right"))
        self._add("calc_percent", dict(base_calc, num_format="0.0%",
                                       align="center"))
        self._add("calc_date", dict(base_calc, num_format=cfg.date_format,
                                    align="center"))
        self._add("calc_weekday", dict(base_calc, num_format="ddd",
                                       align="center"))
        self._add("calc_center", dict(base_calc, align="center"))
        self._add("calc_bold", dict(base_calc, bold=True, align="center"))
        self._add("calc_badge", dict(base_calc, align="center", bold=True,
                                     font_color=p.primary))
        self._add("calc_locked", dict(base_calc, text_wrap=True,
                                      valign="top"))
        self._add("calc_spark", dict(base_calc, align="center",
                                     num_format="#,##0.##",
                                     font_color=p.primary))
        self._add("calc_flag", dict(base_calc, align="center", bold=True))

        # -- totals, bands, notes -------------------------------------------
        self._add("total_label", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "left", "valign": "vcenter", "indent": 1,
            "border": 1, "border_color": p.line, **locked})
        self._add("total_number", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "center", "valign": "vcenter",
            "num_format": "#,##0.##", "border": 1,
            "border_color": p.line, **locked})
        self._add("total_money", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "right", "valign": "vcenter",
            "num_format": self.signed_money(), "border": 1,
            "border_color": p.line, **locked})
        self._add("total_percent", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.primary, "bg_color": p.primary_soft,
            "align": "center", "valign": "vcenter", "num_format": "0.0%",
            "border": 1, "border_color": p.line, **locked})
        self._add("section", {
            "font_name": "Calibri", "font_size": 11, "bold": True,
            "font_color": p.white, "bg_color": p.primary_mid,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("note", {
            "font_name": "Calibri", "font_size": 9, "italic": True,
            "font_color": p.grey_text, "bg_color": p.note_bg,
            "valign": "top", "text_wrap": True, "indent": 1, **locked})
        self._add("label", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.ink, "bg_color": p.white,
            "align": "left", "valign": "vcenter", "indent": 1,
            **locked})
        self._add("label_soft", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.primary_soft, "align": "left",
            "valign": "vcenter", "indent": 1, **locked})

        # -- KPI tiles (used by the dashboards) -----------------------------
        self._add("kpi_label", {
            "font_name": "Calibri", "font_size": 9, "bold": True,
            "font_color": p.primary_mid, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.line, **locked})
        self._add("kpi_value", {
            "font_name": "Calibri", "font_size": 20, "bold": True,
            "font_color": p.primary, "bg_color": p.white,
            "align": "center", "valign": "vcenter",
            "num_format": "#,##0.##", "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_value_money", {
            "font_name": "Calibri", "font_size": 20, "bold": True,
            "font_color": p.accent, "bg_color": p.white,
            "align": "center", "valign": "vcenter",
            "num_format": self.money_fmt(), "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_value_text", {
            "font_name": "Calibri", "font_size": 14, "bold": True,
            "font_color": p.primary, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "border": 1,
            "border_color": p.line, **locked})
        self._add("kpi_sub", {
            "font_name": "Calibri", "font_size": 8, "italic": True,
            "font_color": p.grey_text, "bg_color": p.white,
            "align": "center", "valign": "vcenter", "text_wrap": True,
            "border": 1, "border_color": p.line, **locked})

        # -- status pills ---------------------------------------------------
        for name, (bg, fg) in {
                "good": (p.good_bg, p.good_text),
                "warn": (p.warn_bg, p.warn_text),
                "bad": (p.bad_bg, p.bad_text),
                "info": (p.info_bg, p.info_text)}.items():
            self._add(f"status_{name}", {
                "font_name": "Calibri", "font_size": 10, "bold": True,
                "font_color": fg, "bg_color": bg, "align": "center",
                "valign": "vcenter", "border": 1,
                "border_color": p.line, **locked})

        # -- generic text ---------------------------------------------------
        self._add("plain", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "valign": "vcenter", **locked})
        self._add("plain_bold", {
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": p.ink, "valign": "vcenter", **locked})
        self._add("plain_wrap", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "valign": "top", "text_wrap": True, **locked})
        self._add("link", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.accent,
            "underline": 1, "valign": "vcenter", **locked})
        self._add("check", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.ink,
            "bg_color": p.input_bg, "border": 1,
            "border_color": p.input_border, "align": "center",
            "valign": "vcenter", **unlocked})
        self._add("check_done", {
            "font_name": "Calibri", "font_size": 10, "font_color": p.good_text,
            "bg_color": p.good_bg, "border": 1,
            "border_color": p.line, "align": "center", "valign": "vcenter",
            **locked})

    # ------------------------------------------------------------- accessors
    def __getitem__(self, name: str) -> Any:
        return self.cache[name]

    def get(self, name: str, default: Optional[str] = None) -> Any:
        if name in self.cache:
            return self.cache[name]
        if default is not None:
            return self.cache[default]
        raise KeyError(name)
