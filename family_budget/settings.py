"""Settings tab."""
import re
from openpyxl.workbook.defined_name import DefinedName
from common import (cell, font, fill, align, q, T, USD, USD0, PCT, PCT0, DATE, NUM,
                    SET, PASSWORD, LISTS, title_band, header_row, protect, set_widths,
                    TITLE_FILL, HEADER_FILL, SECTION_FILL, INPUT_FILL, CALC_FILL,
                    FAMILY, ACCOUNT_TYPES, CATEGORIES, SUBCATEGORIES, INCOME_SOURCES,
                    PAY_FREQ, PAY_METHODS, TX_TYPES, BILL_FREQ, YES_NO, ESS_DISC,
                    MONTHS, FILING, DEBT_TYPES, GOAL_TYPES, INVEST_TYPES)


def name_for(display):
    name = re.sub(r"[^A-Za-z0-9]+", "_", display)
    return "L_" + name.strip("_")


def build_settings(wb):
    s = wb.create_sheet(SET)
    s.sheet_view.showGridLines = False
    set_widths(s, [24, 12, 20, 12, 20, 12, 20, 12, 20, 12, 20, 12, 20, 12,
                   20, 12, 20, 12, 20, 12, 20, 12, 20, 12, 22])
    title_band(s, "⚙️ Settings / Setup",
               "Set once — every dropdown, formula and chart reads from here. Only the cream cells are editable.", 25)

    cell(s, 4, 1, "REPORTING CONTROL", bold=True, bg=SECTION_FILL, locked=False)
    cell(s, 4, 2, "", bg=SECTION_FILL, locked=False)
    ctrl = [("Current Date", "=TODAY()", DATE),
            ("Current Month", "=MONTH(B5)", NUM),
            ("Current Year", "=YEAR(B5)", NUM)]
    r = 5
    for lab, formula, fmt in ctrl:
        cell(s, r, 1, lab, bold=True, locked=False)
        c = cell(s, r, 2, formula, bg=INPUT_FILL, numfmt=fmt, locked=True, horizontal="center")
        c.font = font(bold=True, color="0B3D2E")
        r += 1
    cell(s, 8, 1, "Tip: the Dashboard uses 'Current Month' & 'Current Year' to pick the",
         italic=True, size=9, color="3D4A46", locked=False, border=None)
    cell(s, 9, 1, "reporting period automatically. Change the date to re-baseline it.",
         italic=True, size=9, color="3D4A46", locked=False, border=None)

    lists_spec = [
        ("Family Members", FAMILY), ("Account Master", ACCOUNT_TYPES),
        ("Categories", CATEGORIES), ("Subcategories", SUBCATEGORIES),
        ("Income Sources", INCOME_SOURCES), ("Pay Frequencies", PAY_FREQ),
        ("Account Types", ACCOUNT_TYPES), ("Payment Methods", PAY_METHODS),
        ("Transaction Types", TX_TYPES), ("Bill Frequencies", BILL_FREQ),
        ("Yes / No", YES_NO), ("Essential / Discretionary", ESS_DISC),
        ("Months", MONTHS), ("Filing Status", FILING), ("Debt Types", DEBT_TYPES),
        ("Goal Types", GOAL_TYPES), ("Investment Types", INVEST_TYPES),
    ]
    start_col, start_row = 1, 12
    for i, (name, items) in enumerate(lists_spec):
        col = start_col + i * 2
        hdr_col = get_col(col)
        cell(s, start_row, col, name, bold=True, bg=SECTION_FILL, horizontal="left", locked=False)
        rr = start_row + 1
        for item in items:
            cell(s, rr, col, item, bg=INPUT_FILL, locked=False, size=9)
            rr += 1
        rng = f"{q(SET)}!${hdr_col}${start_row+1}:${hdr_col}${rr-1}"
        LISTS[name] = rng
        wb.defined_names.add(DefinedName(name_for(name), attr_text=rng))

    wb.defined_names.add(DefinedName("C_Date", attr_text=f"{q(SET)}!$B$5"))
    wb.defined_names.add(DefinedName("C_Month", attr_text=f"{q(SET)}!$B$6"))
    wb.defined_names.add(DefinedName("C_Year", attr_text=f"{q(SET)}!$B$7"))

    s.freeze_panes = "A3"
    protect(s, allow_sort=False, allow_filter=False)
    return s


def get_col(idx):
    from openpyxl.utils import get_column_letter
    return get_column_letter(idx)
