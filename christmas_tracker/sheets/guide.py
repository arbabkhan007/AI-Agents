"""
\U0001F4D6 Start Here - the cover page and instruction manual.

Built as a sequence of content blocks (headings, paragraphs, bullet lists and
tables) so the copy can be edited without touching row numbers.  A watercolour
cover banner is inserted when ``assets/`` contains the image for the active
theme.
"""

import os
import struct

from .. import config as C
from ..book import r, ci, cl
from ..styles import wrap_height

KEY = "guide"
LAST_COL = "L"
CONTENT = ("C", "L")          # paragraph span
TABLE_SPANS = {
    "tabs": [("C", "E"), ("F", "H"), ("I", "J"), ("K", "L")],
    "legend": [("C", "D"), ("E", "G"), ("H", "L")],
    "auto": [("C", "E"), ("F", "L")],
}


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    ws.set_column("A:A", 2.2)
    ws.set_column("B:B", 3)
    ws.set_column("C:L", 12)
    width = 120

    body = S.guide_text(size=10.5, bg=th.card)
    body_noborder = S.f(**S.base(font_size=10.5, font_color=th.ink,
                                 bg_color=th.card, align="left",
                                 valign="top", text_wrap=True, indent=1))
    bullet = S.f(**S.base(font_size=10.5, font_color=th.ink, bg_color=th.card,
                          align="left", valign="top", text_wrap=True,
                          border=1, border_color=th.border, indent=1))
    step_no = S.f(**S.base(font_size=14, bold=True, font_color=th.white,
                           bg_color=th.accent, align="center",
                           valign="vcenter", border=1, border_color=th.accent))

    row = 1
    ws.set_row(r(row), 7)
    row += 1

    # ------------------------------------------------------------------
    # cover banner + overlaid title
    # ------------------------------------------------------------------
    image = _banner_path(bk)
    span = 0
    if image:
        w, h = _png_size(image)
        target = 860
        scale = target / float(w)
        height = h * scale
        # set_row() heights are in POINTS and a 20pt row is ~26.7 pixels,
        # so convert the pixel height of the artwork before counting rows.
        span = int(height / 26.7) + 1
        bg = th.cover_bg                # the cells under the see-through
        cover = S.f(**S.base(bg_color=bg))   # middle must match the artwork
        title_row = row + max(1, span // 2 - 1)
        for i in range(span):
            # the overlaid title (28pt) and subtitle (12pt) rows get extra
            # height so the text is not clipped by the 20pt default
            if row + i == title_row:
                ws.set_row(r(row + i), 38)
            elif row + i == title_row + 1:
                ws.set_row(r(row + i), 22)
            else:
                ws.set_row(r(row + i), 20)
            for col in range(1, ci(LAST_COL) + 1):
                ws.write(r(row + i), col, "", cover)
        ws.insert_image(r(row), 1, image,
                        {"x_scale": scale, "y_scale": scale,
                         "object_position": 1})
        ws.merge_range(r(title_row), ci("C"), r(title_row), ci("H"),
                       "\U0001F4D6  START HERE",
                       S.f(**S.base(font_name=th.title_font, font_size=28,
                                    bold=True, font_color=th.primary,
                                    bg_color=bg, align="center",
                                    valign="vcenter")))
        ws.merge_range(r(title_row + 1), ci("C"), r(title_row + 1), ci("H"),
                       "  by %s  \u2022  your %s-minute tour of the %s"
                       % (C.AUTHOR, "3", C.PRODUCT_SHORT),
                       S.f(**S.base(font_size=12, italic=True,
                                    font_color=th.muted, bg_color=bg,
                                    align="center", valign="vcenter")))
        row += span + 1
    else:
        ws.set_row(r(row), 40)
        ws.merge_range(r(row), ci("B"), r(row), ci(LAST_COL),
                       "  \U0001F4D6  START HERE", S.sheet_title)
        row += 1

    ws.set_row(r(row), 6)
    row += 1

    def para(text, style=None, span_cols=CONTENT, minimum=18):
        nonlocal row
        c1, c2 = span_cols
        w = sum(12 for c in range(ci(c1), ci(c2) + 1))
        h = wrap_height(text, w, minimum=minimum)
        ws.merge_range(r(row), ci(c1), r(row), ci(c2), text,
                       style or body)
        ws.set_row(r(row), h)
        row += 1
        return row

    def section(text, style=None):
        nonlocal row
        ws.set_row(r(row), 24)
        ws.merge_range(r(row), ci("B"), r(row), ci(LAST_COL), text,
                       style or S.section)
        row += 1

    def bullets(items, prefix="\u2022  "):
        nonlocal row
        for item in items:
            para(prefix + item, bullet)

    def spacer(h=8):
        nonlocal row
        ws.set_row(r(row), h)
        row += 1

    def table(kind, headers, rows, header_color=None):
        nonlocal row
        spans = TABLE_SPANS[kind]
        ws.set_row(r(row), 24)
        for (c1, c2), label in zip(spans, headers):
            ws.merge_range(r(row), ci(c1), r(row), ci(c2), label,
                           S.header(header_color or th.primary))
        row += 1
        for i, cells in enumerate(rows):
            h = 18
            for (c1, c2), text in zip(spans, cells):
                w = sum(12 for c in range(ci(c1), ci(c2) + 1))
                h = max(h, wrap_height(text, w, minimum=18))
                fmt = S.f(**S.base(font_size=9.5, font_color=th.ink,
                                   bg_color=th.alt if i % 2 else th.card,
                                   align="left", valign="top", text_wrap=True,
                                   border=1, border_color=th.border,
                                   indent=1))
                ws.merge_range(r(row), ci(c1), r(row), ci(c2), text, fmt)
            ws.set_row(r(row), h)
            row += 1

    def steps(items):
        nonlocal row
        for i, (title, text) in enumerate(items, 1):
            ws.merge_range(r(row), ci("B"), r(row + 1), ci("B"), str(i),
                           step_no)
            w = sum(12 for c in range(ci("C"), ci(LAST_COL) + 1))
            h = wrap_height(text, w, minimum=20)
            ws.merge_range(r(row), ci("C"), r(row), ci(LAST_COL),
                           title, S.f(**S.base(font_size=11, bold=True,
                                               font_color=th.primary,
                                               bg_color=th.primary_soft,
                                               align="left", valign="vcenter",
                                               border=1, border_color=th.border,
                                               indent=1)))
            ws.merge_range(r(row + 1), ci("C"), r(row + 1), ci(LAST_COL),
                           text, bullet)
            ws.set_row(r(row), 20)
            ws.set_row(r(row + 1), h)
            row += 2

    # ------------------------------------------------------------------
    # 1. quick start
    # ------------------------------------------------------------------
    section("  \u26A1  THREE-MINUTE QUICK START")
    spacer(6)
    steps([
        ("Set your event.", "\u2699\uFE0F Setup \u2192 Event name and Event "
         "date. Every countdown, deadline and key date in the workbook is "
         "calculated from that one date, so nothing is locked to a year."),
        ("Make the money yours.", "On the same tab pick your currency symbol, "
         "your total budget target, the % that triggers the budget warning, "
         "and how many days counts as \u201Cdue soon\u201D."),
        ("Type your people.", "\u2699\uFE0F Setup \u2192 Your lists: recipients, "
         "relationships, stores, categories, hiding spots. Every dropdown in "
         "every tab reads from these lists and updates instantly."),
        ("Add your gifts.", "\U0001F381 Gift Tracker: one row per present. "
         "Use the Status dropdown as your pipeline (\U0001F4A1 idea \u2192 "
         "\U0001F4E6 delivered). The tinted columns (difference, % of budget, "
         "days left, alert) fill themselves in."),
        ("Plan the money.", "\U0001F4B0 Budget: type a planned amount per "
         "category. The \u201Cpulled in automatically\u201D column adds up the "
         "real money from the gift, shopping, stocking and postage columns."),
        ("Enjoy the dashboard.", "\U0001F384 Dashboard needs no typing at all. "
         "It recalculates the moment you change anything anywhere else."),
    ])
    spacer()

    # ------------------------------------------------------------------
    # 2. tab guide
    # ------------------------------------------------------------------
    section("  \U0001F5C2\uFE0F  WHAT EVERY TAB DOES", style=S.section_accent)
    spacer(6)
    tab_rows = [
        ["\U0001F384 Dashboard", "The command centre: countdown, money, gift "
         "progress, bars, 4 charts, deadlines.", "nothing", "everything"],
        ["\U0001F381 Gift Tracker", "One row per present \u2014 the heart of "
         "the workbook.", "the gift", "difference, %, alerts"],
        ["\U0001F4B0 Budget", "Planned vs actual per category with a warning "
         "level you choose.", "planned amounts", "actuals + charts"],
    ]
    if bk.edition == "premium":
        tab_rows += [
            ["\U0001F4A1 Wish List", "Ideas parked all year, ranked by "
             "priority; detects ideas already on the gift list.",
             "ideas + priority", "in-tracker check"],
            ["\U0001F6CD\uFE0F Shopping List", "Everything that is not a "
             "present: wrapping, cards, baking, decorations.", "the items",
             "totals + budget feed"],
            ["\U0001F4E6 Order Tracker", "Parcels: order numbers, expected "
             "dates, tracking links, late alerts.", "order details",
             "days left + alerts"],
            ["\U0001F380 Wrapping & Hiding", "Mirrors the gift list and adds "
             "hiding spots + gift tags (with Secret Mode).", "hiding spot",
             "mirror of gifts"],
            ["\U0001F48C Card Tracker", "Bought \u2192 written \u2192 posted "
             "\u2192 replied, plus postage costs.", "names + ticks",
             "status + totals"],
            ["\U0001F9E6 Stockings", "Fillers per stocking with a budget and a "
             "per-stocking summary.", "items + costs", "budget vs spent"],
            ["\u2705 To-Do List", "Date-aware checklist; deadlines calculated "
             "from your event date.", "tick when done", "status + overdue"],
        ]
    tab_rows += [
        ["\u2699\uFE0F Setup", "Event, money settings, and every editable "
         "list in the workbook.", "settings + lists", "suggestions"],
        ["\U0001F4D6 Start Here", "This page: tour, legend, automation list, "
         "Google Sheets help, FAQ.", "\u2014", "\u2014"],
        ["_Data (hidden)", "The engine room: every dashboard number, chart "
         "series and deadline is computed here.", "never", "all the maths"],
    ]
    table("tabs", ["Tab", "What it's for", "You type", "Automatic"], tab_rows)
    spacer()

    # ------------------------------------------------------------------
    # 3. legend
    # ------------------------------------------------------------------
    section("  \U0001F3A8  COLOUR & SYMBOL LEGEND", style=S.section_gold)
    spacer(6)
    table("legend", ["Looks like", "Means", "Where you'll see it"], [
        ["\U0001F534 red", "Overdue, over budget, or running late",
         "deadline columns, budget status, order alerts, to-do status"],
        ["\U0001F7E0 amber", "Due soon (inside your Setup window) or nearly "
         "at the budget limit", "deadlines, % used, budget status"],
        ["\U0001F7E2 green", "On track / complete / ticked off",
         "tick boxes, statuses, to-do list, wrapped rows"],
        ["\U0001F535 blue", "Ordered / on the way",
         "gift status, order status"],
        ["\U0001F380 gold", "Wrapped, or a priority must-have",
         "gift status, wrapping tab, wish list"],
        ["\u26AA grey", "Not started yet", "budget rows, card status"],
        ["\u2713 tick", "Pick \u2713 from the dropdown to tick, pick the blank "
         "option to untick",
         "wrapped, given, bought, sent, done, returned"],
        ["\u2588\u2591 bars", "Text progress bars (screenshot-friendly and "
         "print-friendly)", "dashboard, budget, stockings"],
    ])
    spacer()

    # ------------------------------------------------------------------
    # 4. automation list
    # ------------------------------------------------------------------
    section("  \U0001F916  EVERYTHING THAT IS AUTOMATIC",
            style=S.section_accent)
    spacer(6)
    auto = [
        ["Countdown", "Days and weeks until the event, recalculated every "
         "time the file opens."],
        ["Money", "Total budget, spent, remaining, % used, average spend per "
         "person."],
        ["Budget alert", "A plain-English warning at the % you chose in "
         "Setup (\u201Cyou've spent 87% of your Christmas budget\u201D)."],
        ["Gift counts", "Planned, purchased, wrapped, delivered, still to "
         "buy, on order, completion %."],
        ["Per person", "Budget, spend, gift counts and a progress bar for "
         "every recipient."],
        ["Per gift", "Under/over budget, % of budget used, days left, "
         "deadline alert."],
        ["Buttons", "Any pasted link becomes a clickable \U0001F517 button."],
        ["Shopping", "Qty \u00D7 unit = total; tick Bought and the actual (or "
         "estimated) cost flows into the budget."],
        ["Budget feed", "Gift, shopping, stocking and postage money is pulled "
         "into the Budget tab by category."],
        ["Stockings", "Budget, spent, remaining and a progress bar for each "
         "stocking."],
        ["Cards", "Status from the ticks; \u201Ccards sent x / y\u201D; "
         "postage into the budget."],
        ["Orders", "Days until expected; late / arriving-soon / on-the-way "
         "alerts."],
        ["Wish list", "Tells you whether an idea is already on the gift list."],
        ["To-do", "Deadlines from the event date; status from the date; "
         "overdue counts."],
        ["Wrapping", "Mirrors the gift list; Secret Mode blanks the hiding "
         "spots."],
        ["Dashboard", "Four charts, the next five deadlines across every tab, "
         "key dates and the \u201Cwhat's left to do\u201D sentences."],
    ]
    table("auto", ["Feature", "What it does"], auto, header_color=th.accent)
    spacer()

    # ------------------------------------------------------------------
    # 5. google sheets + versions
    # ------------------------------------------------------------------
    section("  \U0001F4E5  USING IT IN GOOGLE SHEETS (AND WHICH EXCEL)")
    spacer(6)
    bullets([
        "Google Sheets: sheets.new \u2192 File \u2192 Import \u2192 Upload "
        "\u2192 choose this .xlsx \u2192 Import location: Replace spreadsheet. "
        "Everything (formulas, dropdowns, colours, charts) converts.",
        "After import, click any tab once so Sheets recalculates; then File "
        "\u2192 Save as Google Sheets to keep your copy in Drive.",
        "Excel: 2016, 2019, 2021 and Microsoft 365 on Windows or Mac. The "
        "file contains no macros, so there are no security warnings and it "
        "opens straight away.",
        "Phone / tablet: opens in the Excel and Google Sheets apps \u2014 "
        "fine for checking the dashboard and ticking things off; do the big "
        "data entry on a computer.",
        "If a number ever looks stale in Excel: Formulas \u2192 Calculation "
        "Options \u2192 Automatic, or press F9.",
    ])
    spacer()

    # ------------------------------------------------------------------
    # 6. FAQ
    # ------------------------------------------------------------------
    section("  \u2753  FREQUENTLY ASKED", style=S.section_gold)
    spacer(6)
    faq = [
        ["How do I add more rows?", "Select the last data row and drag the "
         "little square in its bottom-right corner down (or right-click "
         "\u2192 Insert above the TOTALS row). Formulas, dropdowns and "
         "colours come with the row."],
        ["Can I use it for birthdays?", "Yes \u2014 \u2699\uFE0F Setup \u2192 "
         "pick an occasion or type any event name and date. The dashboard "
         "re-words itself around it."],
        ["How do I change currency?", "\u2699\uFE0F Setup \u2192 Currency "
         "symbol changes every dashboard and summary readout. To show it "
         "inside the tables too: select the money columns \u2192 Home \u2192 "
         "Number format \u2192 Currency."],
        ["Why are the checkboxes dropdowns?", "Because \u2713 dropdowns work "
         "identically in Excel and Google Sheets, whereas Excel's built-in "
         "checkbox controls don't survive conversion. Pick \u2713 to tick, "
         "the blank option to untick."],
        ["Can I delete tabs I don't use?", "Please keep _Data (hidden) \u2014 "
         "the dashboard is computed there. For the rest: leaving a tab empty "
         "is safer than deleting it, but deleting premium tabs won't break "
         "the rest as long as _Data stays."],
        ["How do I hide the hiding spots?", "\u2699\uFE0F Setup \u2192 Secret "
         "Mode = Yes turns them white-on-white instantly. For total privacy, "
         "right-click the column \u2192 Hide."],
        ["Will it print nicely?", "Yes \u2014 every tab is set up landscape, "
         "fitted to one page wide, with the title and column headers repeated "
         "on each page."],
        ["Can we share it in the family?", "Save it to OneDrive, Dropbox or "
         "Drive and share it like any workbook; or import it to Google "
         "Sheets and share a link so everyone ticks together."],
        ["Is it password protected?", "Not by default \u2014 you can edit "
         "everything. If you want it locked down: Review \u2192 Protect "
         "Sheet / Protect Workbook in Excel."],
        ["I changed the event date \u2014 will deadlines move?", "The to-do "
         "list and the dashboard key dates move automatically. Dates you "
         "typed yourself on gift rows and orders stay where you put them."],
    ]
    table("auto", ["Question", "Answer"], faq, header_color=th.gold)
    spacer()

    # ------------------------------------------------------------------
    # 7. licence
    # ------------------------------------------------------------------
    section("  \U0001F4C4  LICENCE & SUPPORT", style=S.section_soft)
    spacer(6)
    para("Personal licence: use it for your own household, every year, for "
         "every occasion. Please don't resell, redistribute or share the file "
         "itself \u2014 send people here instead. If something looks wrong or "
         "you'd love a feature added, message the shop: small improvements "
         "usually ship within days, free, to everyone who already bought it.",
         S.f(**S.base(font_size=10, italic=True, font_color=th.muted,
                      bg_color=th.alt, align="left", valign="top",
                      text_wrap=True, border=1, border_color=th.border,
                      indent=1)))
    spacer()
    ws.set_row(r(row), 26)
    row = bk.nav_row(KEY, row, first_col=1, span=2,
                     max_col=LAST_COL) + 2
    ws.merge_range(r(row), ci("B"), r(row), ci(LAST_COL),
                   "  %s v%s  \u2022  %s  \u2022  made with love (and "
                   "formulas)  \u2022  %s"
                   % (C.PRODUCT, C.VERSION, C.TAGLINE, C.AUTHOR), S.footer)
    bk.page(KEY, LAST_COL, row + 2, landscape=False, zoom=100)
    return ws


# ---------------------------------------------------------------------------
def _banner_path(bk):
    """Watercolour cover art for the Start Here tab, if it exists."""
    if not bk.images:
        return None
    here = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(here, "assets", "banner_%s%s" % (bk.th.key, ext))
        if os.path.exists(path):
            return path
    return None


def _png_size(path):
    """Pixel size of a PNG or JPEG, without needing Pillow."""
    with open(path, "rb") as fh:
        data = fh.read(4096)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + length
    return 1600, 640
