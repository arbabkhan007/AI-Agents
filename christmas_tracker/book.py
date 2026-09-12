"""
The build context.

``Book`` owns the workbook, the worksheet registry, the defined names and all
of the little helpers that turn a cell address into a formula fragment.  Sheet
builders receive one ``Book`` and never talk to XlsxWriter's raw indices
directly, which is what keeps the cross-sheet formulas correct when a tab is
missing (Basic edition) or when a capacity changes.
"""

import datetime
import types

import xlsxwriter

try:                                   # xlsxwriter < 3.x
    from xlsxwriter.utility import datetime_to_excel_datetime
except ImportError:                    # xlsxwriter >= 3.x renamed it
    from xlsxwriter.utility import _datetime_to_excel_datetime as \
        datetime_to_excel_datetime

from . import config as C
from .styles import Styles, wrap_height

_XLWorksheet = xlsxwriter.worksheet.Worksheet


def _coerce(value):
    """Cached formula results must be a number, a bool or a string.

    XlsxWriter writes whatever it is given straight into ``<v>``; a
    ``datetime.date`` would produce invalid XML that Excel refuses to open.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (datetime.datetime, datetime.date)):
        return datetime_to_excel_datetime(value, False, False)
    if isinstance(value, (str, int, float)):
        return value
    return str(value)


def _safe_write_formula(self, row, col, formula, cell_format=None, value=0):
    """``write_formula`` that also coerces the cached result."""
    return _XLWorksheet.write_formula(self, row, col, formula, cell_format,
                                      _coerce(value))


def r(n):
    """1-indexed spreadsheet row -> 0-indexed XlsxWriter row."""
    return n - 1


def cellref(col, row):
    return "%s%d" % (col, row)


class Book(object):

    def __init__(self, path, theme, edition="premium", mode="blank",
                 protect=None, images=True, demo=None):
        self.path = path
        self.th = theme
        self.edition = edition
        self.mode = mode            # "blank" | "demo"
        self.protect = protect
        self.images = images
        self.demo = demo

        self.order = C.EDITIONS[edition]
        self.wb = xlsxwriter.Workbook(path)
        self.S = Styles(self.wb, theme)
        self.sheets = {}
        self.stats = {"formulas": 0, "validations": 0, "cond_formats": 0,
                      "charts": 0, "links": 0, "cells": 0}

        self._create_sheets()
        self._define_names()

        self.wb.set_properties({
            "title": C.PRODUCT,
            "subject": C.TAGLINE,
            "author": C.AUTHOR,
            "manager": C.AUTHOR,
            "company": C.AUTHOR,
            "category": "Christmas / Gift Planning Spreadsheet",
            "keywords": ("christmas gift tracker, gift list, budget planner, "
                         "holiday planner, etsy spreadsheet, excel template, "
                         "google sheets, stocking stuffer, card tracker"),
            "comments": ("%s v%s - %s. Works in Excel 2016+ and Google "
                         "Sheets. No macros, nothing to install."
                         % (C.PRODUCT, C.VERSION, C.TAGLINE)),
        })
        self.wb.set_calc_mode("auto")

    # ------------------------------------------------------------------
    # sheet registry
    # ------------------------------------------------------------------
    def _create_sheets(self):
        for key in self.order:
            ws = self.wb.add_worksheet(C.SHEET_NAMES[key])
            ws.write_formula = types.MethodType(_safe_write_formula, ws)
            ws.set_tab_color(self.th.tabs[key])
            ws.hide_gridlines(2)
            self.sheets[key] = ws
        if "data" in self.sheets:
            self.sheets["data"].hide()
        self.sheets["dashboard"].set_first_sheet()
        self.sheets["dashboard"].activate()
        self.sheets["dashboard"].set_zoom(90)

    def ws(self, key):
        return self.sheets[key]

    def has(self, key):
        return key in self.sheets and key != "data"

    def name(self, key):
        return C.SHEET_NAMES[key]

    def q(self, key):
        """Quoted sheet name for use inside formulas."""
        return "'%s'" % C.SHEET_NAMES[key]

    # ------------------------------------------------------------------
    # defined names
    # ------------------------------------------------------------------
    def _define_names(self):
        su = self.q("setup")
        simple = {
            "EventName": "%s!$C$%d" % (su, C.SU_EVENT_NAME),
            "EventDate": "%s!$C$%d" % (su, C.SU_EVENT_DATE),
            "Currency": "%s!$C$%d" % (su, C.SU_CURRENCY),
            "TotalBudget": "%s!$C$%d" % (su, C.SU_BUDGET),
            "AlertAt": "%s!$C$%d" % (su, C.SU_ALERT),
            "DueSoonDays": "%s!$C$%d" % (su, C.SU_DUESOON),
            "SecretMode": "%s!$C$%d" % (su, C.SU_SECRET),
            "CountOrdered": "%s!$C$%d" % (su, C.SU_COUNT_ORDERED),
            "Statuses": "%s!$%s$%d:$%s$%d" % (
                su, C.FIXED_COLS["statuses"], C.SU_FIXED_FIRST,
                C.FIXED_COLS["statuses"], C.SU_FIXED_FIRST + 5),
            "OrderStatuses": "%s!$%s$%d:$%s$%d" % (
                su, C.FIXED_COLS["order_statuses"], C.SU_FIXED_FIRST,
                C.FIXED_COLS["order_statuses"], C.SU_FIXED_FIRST + 5),
            "Priorities": "%s!$%s$%d:$%s$%d" % (
                su, C.FIXED_COLS["priorities"], C.SU_FIXED_FIRST,
                C.FIXED_COLS["priorities"], C.SU_FIXED_FIRST + 2),
            "Tick": "%s!$%s$%d:$%s$%d" % (
                su, C.FIXED_COLS["tick"], C.SU_FIXED_FIRST,
                C.FIXED_COLS["tick"], C.SU_FIXED_FIRST + 1),
        }
        for nm, ref in simple.items():
            self.wb.define_name(nm, "=" + ref)

        first = C.SU_LIST_FIRST
        lastc = C.SU_LIST_FIRST + C.SU_LIST_ROWS - 1
        for key, col in sorted(C.LIST_COLS.items()):
            rng = "%s!$%s$%d:$%s$%d" % (su, col, first, col, lastc)
            self.wb.define_name(
                _name_for_list(key),
                "=OFFSET(%s!$%s$%d,0,0,MAX(1,COUNTA(%s)),1)" % (su, col, first, rng))

        # Occasion presets live on the hidden data sheet.
        d = self.q("data")
        self.wb.define_name(
            "Occasions",
            "=OFFSET(%s!$A$%d,0,0,COUNTA(%s!$A$%d:$A$%d),1)"
            % (d, C.DATA_PRESET_FIRST, d, C.DATA_PRESET_FIRST,
               C.DATA_PRESET_FIRST + C.OCCASION_ROWS - 1))

    # ------------------------------------------------------------------
    # reference helpers
    # ------------------------------------------------------------------
    def col(self, key, field):
        return C.COLS[key][field]

    def rng(self, key, field, first=None, last=None, quoted=True):
        """Absolute range for a column of a tracker sheet."""
        col = self.col(key, field)
        first = C.ROW_FIRST if first is None else first
        last = C.last_row(key) if last is None else last
        ref = "%s!$%s$%d:$%s$%d" % (self.q(key) if quoted else self.name(key),
                                    col, first, col, last)
        return ref

    def cell(self, key, field, row):
        return "%s!$%s$%d" % (self.q(key), self.col(key, field), row)

    def kpi(self, key):
        return "%s!$AF$%d" % (self.q("data"), C.KPI_ROW[key])

    def kpi_fmt(self, key):
        return C.KPI_FMT[key]

    def data_rng(self, col, first, last):
        return "%s!$%s$%d:$%s$%d" % (self.q("data"), col, first, col, last)

    def data_cell(self, col, row):
        return "%s!$%s$%d" % (self.q("data"), col, row)

    def listname(self, key):
        return _name_for_list(key)

    # ------------------------------------------------------------------
    # cached values (so previews look right before Excel recalculates)
    # ------------------------------------------------------------------
    def cached(self, key, default=0):
        if self.demo and key in self.demo.agg:
            return self.demo.agg[key]
        return default

    # ------------------------------------------------------------------
    # money / text formula helpers
    # ------------------------------------------------------------------
    def money(self, value_formula, decimals="#,##0"):
        """Currency-prefixed text, driven by the Currency setting."""
        return 'Currency&TEXT(%s,"%s")' % (value_formula, decimals)

    def bar(self, numerator, denominator, blocks=18):
        """Text progress bar built with REPT()."""
        pct = "MIN(1,IFERROR((%s)/(%s),0))" % (numerator, denominator)
        filled = "ROUND(%s*%d,0)" % (pct, blocks)
        return ('=IFERROR(REPT("\u2588",%s)&REPT("\u2591",%d-%s),"%s")'
                % (filled, blocks, filled, "\u2591" * blocks))

    def bar_static(self, numerator, denominator, blocks=18):
        """Python twin of :meth:`bar` used for cached values."""
        try:
            pct = min(1.0, float(numerator) / float(denominator)) if denominator else 0.0
        except (TypeError, ValueError, ZeroDivisionError):
            pct = 0.0
        filled = int(round(pct * blocks))
        return "\u2588" * filled + "\u2591" * (blocks - filled)

    # ------------------------------------------------------------------
    # page furniture
    # ------------------------------------------------------------------
    def protect_sheet(self, key):
        """Lock every cell whose format says ``locked`` (inputs stay open).

        Used with the ``--protect PASSWORD`` CLI flag so the automatic /
        formula cells cannot be typed over, while the white input cells,
        dropdowns, tick boxes and notes stay editable.
        """
        if not self.protect:
            return
        self.ws(key).protect(self.protect, {
            "objects": True, "scenarios": True, "format_cells": True,
            "format_columns": True, "format_rows": True,
            "insert_rows": True, "insert_columns": True,
            "insert_hyperlinks": True, "delete_rows": True,
            "delete_columns": True, "sort": True, "autofilter": True,
            "select_locked_cells": True, "select_unlocked_cells": True,
        })

    def page(self, key, last_col, last_row, landscape=True, freeze=None,
             fit=True, zoom=90, title_rows=None, paper=9):
        ws = self.sheets[key]
        ws.set_zoom(zoom)
        if landscape:
            ws.set_landscape()
        if fit:
            ws.fit_to_pages(1, 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        ws.set_paper(paper)
        ws.set_header("&L&\"%s,Bold\"&11%s&R&\"%s,Italic\"&9Page &P of &N"
                      % (self.th.body_font, C.PRODUCT_SHORT,
                         self.th.body_font))
        ws.set_footer("&C&\"%s,Italic\"&8&A  \u2022  %s v%s  \u2022  "
                      "\u00A9 %s  \u2022  personal licence"
                      % (self.th.body_font, C.PRODUCT, C.VERSION, C.AUTHOR))
        ws.print_area("A1:%s%d" % (last_col, last_row))
        if title_rows:
            ws.repeat_rows(title_rows[0], title_rows[1])
        if freeze:
            ws.freeze_panes(*freeze)
        self.protect_sheet(key)
        return ws

    def widths(self, key, extra=None):
        ws = self.sheets[key]
        for col, width in sorted((C.WIDTHS.get(key, {}) or {}).items()):
            ws.set_column("%s:%s" % (col, col), width)
        for col, width in sorted((extra or {}).items()):
            ws.set_column("%s:%s" % (col, col), width)
        return ws

    def title_block(self, key, title, subtitle, last_col, home=True):
        """Standard 6-row header band used by every tracker tab."""
        ws = self.sheets[key]
        S = self.S
        ws.set_row(r(C.ROW_SPACER_1), 7)
        ws.set_row(r(C.ROW_TITLE), 30)
        ws.set_row(r(C.ROW_SUBTITLE), 18)
        ws.set_row(r(C.ROW_SPACER_2), 7)
        ws.set_row(r(C.ROW_STATS), 26)
        ws.set_row(r(C.ROW_SPACER_3), 7)
        ws.merge_range(r(C.ROW_TITLE), 1, r(C.ROW_TITLE), _ci(last_col) - 3,
                       title, S.sheet_title)
        for c in range(_ci(last_col) - 2, _ci(last_col) + 1):
            ws.write_blank(r(C.ROW_TITLE), c, None, S.canvas)
        ws.merge_range(r(C.ROW_SUBTITLE), 1, r(C.ROW_SUBTITLE), _ci(last_col) - 3,
                       subtitle, S.sheet_sub)
        if home:
            ws.merge_range(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                           r(C.ROW_SUBTITLE), _ci(last_col),
                           "", S.home_link)
            ws.write_url(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                         "internal:%s!A1" % self.q("dashboard"), S.home_link,
                         "\U0001F3E0  Back to Dashboard")
            self.stats["links"] += 1
        else:
            ws.merge_range(r(C.ROW_SUBTITLE), _ci(last_col) - 2,
                           r(C.ROW_SUBTITLE), _ci(last_col), "", S.canvas)
        return ws

    def stats_strip(self, key, items, row=None, first_col=1, span=2):
        """Row of small formula chips under the sheet title.

        ``items`` is a list of ``(formula_or_text, colour_key, cached)``.
        """
        ws = self.sheets[key]
        row = C.ROW_STATS if row is None else row
        col = first_col
        for formula, color, cached in items:
            fmt = self.S.pill(self.th.soft(color), getattr(self.th, color),
                              size=10.5, bold=True, align="left")
            ws.merge_range(r(row), col, r(row), col + span - 1, "", fmt)
            if formula.startswith("="):
                ws.write_formula(r(row), col, formula, fmt,
                                 cached if cached is not None else 0)
                self.stats["formulas"] += 1
            else:
                ws.write(r(row), col, formula, fmt)
            col += span
        return ws

    def nav_row(self, key, row, first_col=1, span=2, max_col="N"):
        """Bottom navigation buttons (one per visible tab)."""
        ws = self.sheets[key]
        palette = ["primary", "accent", "gold", "info", "plum", "ok",
                   "primary_2", "warn", "accent", "info"]
        col = first_col
        n = 0
        for target in self.order:
            if target == "data":
                continue
            if col + span - 1 > _ci(max_col):
                row += 1
                col = first_col
                ws.set_row(r(row), 24)
            color = getattr(self.th, palette[n % len(palette)])
            fmt = self.S.nav(color)
            if span > 1:
                ws.merge_range(r(row), col, r(row), col + span - 1, "", fmt)
            label = C.SHEET_SHORT[target]
            if target == key:
                label = "\u25B6 " + label
            ws.write_url(r(row), col, "internal:%s!A1" % self.q(target),
                         fmt, label)
            self.stats["links"] += 1
            col += span
            n += 1
        return row

    # ------------------------------------------------------------------
    # painting / writing helpers
    # ------------------------------------------------------------------
    def paint(self, key, row1, col1, row2, col2, fmt):
        ws = self.sheets[key]
        for rr in range(row1, row2 + 1):
            for cc in range(col1, col2 + 1):
                ws.write_blank(rr, cc, None, fmt)

    def band(self, key, row, col1, col2, fmt, height=None):
        ws = self.sheets[key]
        ws.merge_range(r(row), col1, r(row), col2, "", fmt)
        if height:
            ws.set_row(r(row), height)

    def write(self, key, row, col, value, fmt=None, cached=None):
        ws = self.sheets[key]
        self.stats["cells"] += 1
        if isinstance(value, str) and value.startswith("="):
            ws.write_formula(r(row), col, value, fmt,
                             cached if cached is not None else 0)
            self.stats["formulas"] += 1
        elif value is None or value == "":
            ws.write_blank(r(row), col, None, fmt)
        else:
            ws.write(r(row), col, value, fmt)
        return ws

    def merge(self, key, row1, col1, row2, col2, value, fmt=None,
              cached=None):
        ws = self.sheets[key]
        self.stats["cells"] += 1
        if isinstance(value, str) and value.startswith("="):
            ws.merge_range(r(row1), col1, r(row2), col2, "", fmt)
            ws.write_formula(r(row1), col1, value, fmt,
                             cached if cached is not None else 0)
            self.stats["formulas"] += 1
        else:
            ws.merge_range(r(row1), col1, r(row2), col2, value, fmt)
        return ws

    def para(self, key, row, col1, col2, text, fmt, width_chars=None,
             minimum=18):
        """Merged, wrapped paragraph with a row height that actually fits."""
        if width_chars is None:
            width_chars = sum(
                (C.WIDTHS.get(key, {}) or {}).get(_cl(c), 10)
                for c in range(col1, col2 + 1))
        h = wrap_height(text, width_chars, minimum=minimum)
        self.merge(key, row, col1, row, col2, text, fmt)
        self.sheets[key].set_row(r(row), h)
        return row + 1

    def validate(self, key, row1, col1, row2, col2, source, title=None,
                 message=None, error=None, error_type="stop"):
        ws = self.sheets[key]
        opts = {"validate": "list", "source": source, "ignore_blank": True,
                "show_input": bool(title or message),
                "show_error": bool(error)}
        if title:
            opts["input_title"] = title[:32]
        if message:
            opts["input_message"] = message[:255]
        if error:
            opts["error_title"] = "Pick from the list"[:32]
            opts["error_message"] = error[:255]
            opts["error_type"] = error_type
        res = ws.data_validation(r(row1), col1, r(row2), col2, opts)
        if res == 0:
            self.stats["validations"] += 1
        return res

    def cond(self, key, row1, col1, row2, col2, opts):
        ws = self.sheets[key]
        res = ws.conditional_format(r(row1), col1, r(row2), col2, opts)
        if res == 0:
            self.stats["cond_formats"] += 1
        return res

    def chart(self, ctype, **opts):
        ch = self.wb.add_chart(dict({"type": ctype}, **opts))
        ch.show_hidden_data()          # data lives on the hidden _Data sheet
        ch.show_blanks_as("gap")
        self.stats["charts"] += 1
        return ch

    def close(self):
        self.wb.close()


# ----------------------------------------------------------------------
# small utilities
# ----------------------------------------------------------------------
def _ci(letter):
    """Column letter -> 0-indexed column number."""
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def _cl(index):
    """0-indexed column number -> column letter."""
    s = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        s = chr(65 + rem) + s
    return s


_LIST_NAMES = {
    "recipients": "Recipients",
    "relationships": "Relationships",
    "gift_categories": "GiftCategories",
    "stores": "Stores",
    "shop_categories": "ShopCategories",
    "hiding_spots": "HidingSpots",
    "todo_categories": "TodoCategories",
    "stocking_owners": "StockingOwners",
    "stocking_items": "StockingItems",
}


def _name_for_list(key):
    return _LIST_NAMES[key]


def name_for_list(key):
    return _LIST_NAMES[key]


def ci(letter):
    return _ci(letter)


def cl(index):
    return _cl(index)
