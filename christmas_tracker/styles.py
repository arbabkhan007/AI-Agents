"""
Every cell format used by the workbook, generated from the active theme.

Sheet builders never build formats inline - they ask ``Styles`` for a
semantic style (``S.cell("money", alt)``), which keeps the two themes
visually consistent and keeps the format cache small.
"""

import math


class Styles(object):

    def __init__(self, wb, th):
        self.wb = wb
        self.th = th
        self._cache = {}
        self._build()

    # ------------------------------------------------------------------
    # core
    # ------------------------------------------------------------------
    def f(self, props=None, **kw):
        """Cached ``workbook.add_format`` (accepts a dict or keywords)."""
        p = dict(props or {})
        p.update(kw)
        key = tuple(sorted((k, str(v)) for k, v in p.items()))
        fmt = self._cache.get(key)
        if fmt is None:
            fmt = self.wb.add_format(p)
            self._cache[key] = fmt
        return fmt

    def base(self, **over):
        """Body-text defaults + overrides."""
        p = {"font_name": self.th.body_font, "font_size": 10.5,
             "font_color": self.th.ink, "valign": "vcenter"}
        p.update(over)
        return p

    # ------------------------------------------------------------------
    # canvases, banners, sections
    # ------------------------------------------------------------------
    def _build(self):
        th = self.th
        self.canvas = self.f({"bg_color": th.bg})
        self.canvas_card = self.f({"bg_color": th.card})

        self.hero_title = self.f(self.base(
            font_name=th.title_font, font_size=26, bold=True,
            font_color=th.white, bg_color=th.primary, align="left",
            valign="vcenter", indent=1))
        self.hero_count = self.f(self.base(
            font_name=th.title_font, font_size=17, bold=True,
            font_color=th.gold_soft, bg_color=th.accent, align="left",
            valign="vcenter", indent=1))
        self.hero_meta = self.f(self.base(
            font_size=10, italic=True, font_color=th.ink,
            bg_color=th.gold_soft, align="left", valign="vcenter", indent=1))

        self.sheet_title = self.f(self.base(
            font_name=th.title_font, font_size=20, bold=True,
            font_color=th.primary, bg_color=th.bg, align="left",
            valign="vcenter", indent=1))
        self.sheet_sub = self.f(self.base(
            font_size=10.5, italic=True, font_color=th.muted,
            bg_color=th.bg, align="left", valign="vcenter", indent=1))
        self.home_link = self.f(self.base(
            font_size=10, bold=True, font_color=th.white, bg_color=th.accent,
            align="center", valign="vcenter", border=1,
            border_color=th.accent))

        self.section = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.white, bg_color=th.primary, align="left",
            valign="vcenter", indent=1))
        self.section_accent = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.white, bg_color=th.accent, align="left",
            valign="vcenter", indent=1))
        self.section_gold = self.f(self.base(
            font_name=th.title_font, font_size=13, bold=True,
            font_color=th.ink, bg_color=th.gold_soft, align="left",
            valign="vcenter", indent=1, bottom=2, bottom_color=th.gold))
        self.section_soft = self.f(self.base(
            font_name=th.title_font, font_size=12, bold=True,
            font_color=th.primary, bg_color=th.primary_soft, align="left",
            valign="vcenter", indent=1, left=4, left_color=th.gold))

        # table header
        self.thead = self.f(self.base(
            font_size=10, bold=True, font_color=th.white, bg_color=th.primary,
            align="center", valign="vcenter", text_wrap=True, border=1,
            border_color=th.primary))

        self.note = self.f(self.base(
            font_size=10, italic=True, font_color=th.muted, bg_color=th.alt,
            align="left", valign="top", text_wrap=True, border=1,
            border_color=th.border, indent=1, locked=False))
        self.note_plain = self.f(self.base(
            font_size=10, italic=True, font_color=th.muted, bg_color=th.bg,
            align="left", valign="top", text_wrap=True))
        self.footer = self.f(self.base(
            font_size=9, italic=True, font_color=th.muted, bg_color=th.bg,
            align="left", valign="vcenter"))

        self.bar_text = self.f(self.base(
            font_name=th.mono_font, font_size=13, bold=True,
            font_color=th.primary_2, bg_color=th.card, align="left",
            valign="vcenter", border=1, border_color=th.border))
        self.bar_label = self.f(self.base(
            font_size=10, bold=True, font_color=th.ink, bg_color=th.card,
            align="left", valign="vcenter", border=1,
            border_color=th.border, indent=1))
        self.bar_pct = self.f(self.base(
            font_name=th.mono_font, font_size=13, bold=True,
            font_color=th.accent, bg_color=th.card, align="center",
            valign="vcenter", border=1, border_color=th.border))

    # ------------------------------------------------------------------
    # table headers in an accent colour
    # ------------------------------------------------------------------
    def header(self, color=None):
        color = color or self.th.primary
        return self.f(self.base(
            font_size=10, bold=True, font_color=self.th.white,
            bg_color=color, align="center", valign="vcenter", text_wrap=True,
            border=1, border_color=color))

    # ------------------------------------------------------------------
    # data cells
    # ------------------------------------------------------------------
    _KINDS = {
        "text":       {"align": "left", "locked": False},
        "center":     {"align": "center", "locked": False},
        "money":      {"align": "right", "num_format": "#,##0.00",
                       "locked": False},
        "money0":     {"align": "right", "num_format": "#,##0",
                       "locked": False},
        "num":        {"align": "right", "num_format": "#,##0",
                       "locked": False},
        "qty":        {"align": "center", "num_format": "#,##0",
                       "locked": False},
        "pct":        {"align": "center", "num_format": "0%",
                       "locked": False},
        "date":       {"align": "center", "num_format": "dd mmm yyyy",
                       "locked": False},
        "tick":       {"align": "center", "font_size": 13, "bold": True,
                       "font_color": "#2F7D4F", "locked": False},
        "wrap":       {"align": "left", "text_wrap": True, "valign": "top",
                       "locked": False},
        "link":       {"align": "left", "font_color": "#2A5D8F",
                       "underline": 1, "locked": False},
        "url":        {"align": "center", "bold": True, "font_size": 10},
        # calculated columns (locked - they must not be typed over)
        "calc":       {"align": "left"},
        "calc_c":     {"align": "center"},
        "calc_wrap":  {"align": "left", "text_wrap": True},
        "calc_money": {"align": "right", "num_format": "#,##0.00"},
        "calc_num":   {"align": "right", "num_format": "#,##0"},
        "calc_pct":   {"align": "center", "num_format": "0%"},
        "calc_date":  {"align": "center", "num_format": "dd mmm yyyy"},
        "calc_tick":  {"align": "center", "font_size": 13, "bold": True},
    }

    def cell(self, kind, alt=False, **over):
        """Data-cell format.  ``alt`` selects the zebra-stripe background."""
        th = self.th
        props = self.base(**self._KINDS[kind])
        if kind.startswith("calc"):
            props["bg_color"] = th.alt
            props["font_color"] = th.ink if kind in ("calc", "calc_wrap",
                                                     "calc_c") else th.ink
            props["locked"] = True
            if kind in ("calc_money", "calc_num", "calc_pct", "calc_date"):
                props["font_color"] = th.primary
        else:
            props["bg_color"] = th.alt if alt else th.card
        props["border"] = 1
        props["border_color"] = th.border
        props.update(over)
        return self.f(**props)

    def idx(self, alt=False):
        """The little grey row-number column."""
        return self.f(self.base(
            font_size=9, font_color=self.th.muted, align="center",
            valign="vcenter", border=1, border_color=self.th.border,
            bg_color=self.th.alt if alt else self.th.card,
            num_format="0"))

    # ------------------------------------------------------------------
    # dashboard furniture
    # ------------------------------------------------------------------
    def kpi_label(self, color, size=9.5, align="left"):
        return self.f(self.base(
            font_size=size, bold=True, font_color=self.th.white,
            bg_color=color, align=align, valign="vcenter", indent=1,
            border=1, border_color=color))

    def kpi_value(self, color, num_format=None, size=21, align="center",
                  bg=None):
        p = self.base(font_name=self.th.title_font, font_size=size, bold=True,
                      font_color=color, bg_color=bg or self.th.card,
                      align=align, valign="vcenter", border=1,
                      border_color=self.th.border)
        if num_format:
            p["num_format"] = num_format
        return self.f(**p)

    def kpi_text(self, color, size=11, align="left", bg=None, bold=True,
                 wrap=False):
        return self.f(self.base(
            font_size=size, bold=bold, font_color=color,
            bg_color=bg or self.th.card, align=align, valign="vcenter",
            border=1, border_color=self.th.border, indent=1 if align == "left" else 0,
            text_wrap=wrap))

    def panel(self, color=None, bg=None, size=10.5, bold=False, align="left",
              wrap=True, font_color=None, valign="top", border=True):
        p = self.base(font_size=size, bold=bold, align=align, valign=valign,
                      text_wrap=wrap,
                      bg_color=bg if bg is not None else self.th.card,
                      font_color=font_color or self.th.ink)
        if border:
            p["border"] = 1
            p["border_color"] = color or self.th.border
            if color:
                p["left"] = 3
                p["left_color"] = color
        return self.f(**p)

    def pill(self, bg, fg, size=9.5, bold=True, align="center"):
        return self.f(self.base(font_size=size, bold=bold, font_color=fg,
                                bg_color=bg, align=align, valign="vcenter",
                                border=1, border_color=bg, text_wrap=False))

    def nav(self, color, size=10.5):
        return self.f(self.base(font_size=size, bold=True,
                                font_color=self.th.white, bg_color=color,
                                align="center", valign="vcenter", border=1,
                                border_color=color))

    def nav_soft(self, size=10.5):
        th = self.th
        return self.f(self.base(font_size=size, bold=True,
                                font_color=th.primary, bg_color=th.primary_soft,
                                align="center", valign="vcenter", border=1,
                                border_color=th.border))

    # ------------------------------------------------------------------
    # conditional-format formats (dxf sources)
    # ------------------------------------------------------------------
    def cf(self, bg=None, fg=None, bold=False, strike=False, italic=False,
           border=None, size=None, align=None, num_format=None):
        th = self.th
        p = {}
        if bg:
            p["bg_color"] = bg
        if fg:
            p["font_color"] = fg
        if bold:
            p["bold"] = True
        if strike:
            p["font_strikeout"] = True
        if italic:
            p["italic"] = True
        if size:
            p["font_size"] = size
        if align:
            p["align"] = align
        if num_format:
            p["num_format"] = num_format
        if border:
            p["border"] = 1
            p["border_color"] = border
        p["font_name"] = th.body_font
        return self.f(**p)

    def cf_state(self, state):
        """Semantic state colours: ok / warn / bad / info / plum / gold."""
        th = self.th
        return self.cf(bg=th.soft(state), fg=getattr(th, state), bold=True,
                       border=th.border)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def guide_text(self, size=10.5, bold=False, italic=False, color=None,
                   bg=None, indent=0, align="left"):
        return self.f(self.base(font_size=size, bold=bold, italic=italic,
                                font_color=color or self.th.ink,
                                bg_color=bg or self.th.card, align=align,
                                valign="top", text_wrap=True, indent=indent,
                                border=1, border_color=self.th.border,
                                locked=False))

    def static_height(self, text, width_chars, line_px=14.6, pad=8,
                      minimum=18):
        """Row height needed to show wrapped ``text`` in ``width_chars``."""
        if not text:
            return minimum
        per_line = max(10, int(width_chars * 0.95))
        lines = 0
        for para in str(text).split("\n"):
            lines += max(1, int(math.ceil(len(para) / float(per_line))))
        return max(minimum, lines * line_px + pad)


def wrap_height(text, width_chars, line_px=14.6, pad=8, minimum=18):
    """Module-level twin of :meth:`Styles.static_height`."""
    if not text:
        return minimum
    per_line = max(10, int(width_chars * 0.95))
    lines = 0
    for para in str(text).split("\n"):
        lines += max(1, int(math.ceil(len(para) / float(per_line))))
    return max(minimum, lines * line_px + pad)
