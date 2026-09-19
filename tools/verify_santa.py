#!/usr/bin/env python3
"""
Audit a generated .xlsx without needing Excel (santa edition).

Checks performed
    1. the workbook opens (openpyxl) and every expected tab exists / is hidden
    2. every sheet-qualified reference in every formula points at a real sheet
    3. no modern-only function leaked in without the ``_xlfn.`` prefix older
       Excel versions need
    4. no cell contains the literal strings "None", "#REF!" or "nan"
    5. nothing was written *under* a merged range (Excel only ever shows the
       top-left cell of a merge, so such writes would be invisible)

Usage
    python3 tools/verify_santa.py products/Secret_Santa_*.xlsx
"""

import glob
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

import openpyxl
from openpyxl.utils import (column_index_from_string, get_column_letter,
                            range_boundaries)

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Functions that did not exist in Excel 2007 and therefore must be written as
# _xlfn.NAME by a file generator (XlsxWriter does this automatically for the
# names it knows about).
MODERN = {
    "TEXTJOIN", "CONCAT", "IFS", "SWITCH", "MAXIFS", "MINIFS", "XLOOKUP",
    "XMATCH", "FILTER", "SORT", "SORTBY", "UNIQUE", "SEQUENCE", "LET",
    "LAMBDA", "RANDARRAY", "IMAGE", "TEXTSPLIT", "VSTACK", "HSTACK", "TOCOL",
    "TOROW", "TAKE", "DROP", "CHOOSEROWS", "CHOOSECOLS", "WRAPROWS",
    "WRAPCOLS", "GROUPBY", "PIVOTBY", "REGEXTEST", "REGEXEXTRACT",
    "REGEXREPLACE",
}

FUNC_RE = re.compile(r"(?<![A-Za-z0-9_.])([A-Z][A-Z0-9_.]*)\s*\(")
SHEET_REF_RE = re.compile(r"(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_.]*))!")


def sheet_xml(path):
    """{sheet name: worksheet xml} for low level checks."""
    zf = zipfile.ZipFile(path)
    wbxml = zf.read("xl/workbook.xml").decode()
    rels = dict(re.findall(
        r'Id="(rId\d+)"[^>]*Target="([^"]*worksheets/sheet\d+\.xml)"',
        zf.read("xl/_rels/workbook.xml.rels").decode()))
    out = {}
    for name, rid in re.findall(r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"',
                                wbxml):
        out[name] = zf.read("xl/" + rels[rid].lstrip("/")).decode()
    return out, [n for n in zipfile.ZipFile(path).namelist()]


def hidden_writes(path):
    """Cells written inside a merged range but not at its top-left."""
    xmls, _ = sheet_xml(path)
    out = []
    for name, xml in xmls.items():
        covered = {}
        for m in re.findall(r'<mergeCell ref="([A-Z]+\d+:[A-Z]+\d+)"/>', xml):
            c1, r1, c2, r2 = range_boundaries(m)
            for rr in range(r1, r2 + 1):
                for cc in range(c1, c2 + 1):
                    if (rr, cc) != (r1, c1):
                        covered[(rr, cc)] = m
        root = ET.fromstring(xml)
        for row in root.iter(NS + "row"):
            for c in row.iter(NS + "c"):
                m = re.match(r"([A-Z]+)(\d+)", c.get("r"))
                key = (int(m.group(2)), column_index_from_string(m.group(1)))
                if key not in covered:
                    continue
                v = c.find(NS + "v")
                if c.find(NS + "f") is not None or (
                        v is not None and (v.text or "").strip()):
                    out.append((name, c.get("r"), covered[key]))
    return out


def check_formulas(path, problems):
    wb = openpyxl.load_workbook(path, data_only=False)
    sheetnames = set(wb.sheetnames)
    n_formula = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if not (isinstance(v, str) and v.startswith("=")):
                    continue
                n_formula += 1
                if v in ("None", "nan"):
                    problems.append("%s!%s contains %r"
                                    % (ws.title, cell.coordinate, v))
                body = re.sub(r'"[^"]*"', '""', v)     # drop string literals
                for m in SHEET_REF_RE.finditer(body):
                    ref = m.group(1) or m.group(2)
                    if ref not in sheetnames:
                        problems.append("%s!%s references unknown sheet %r"
                                        % (ws.title, cell.coordinate, ref))
                for m in FUNC_RE.finditer(body):
                    fn = m.group(1).split(".")[-1]
                    if fn in MODERN and "_xlfn." not in m.group(1):
                        problems.append(
                            "%s!%s uses modern function %s without _xlfn."
                            % (ws.title, cell.coordinate, fn))
    return n_formula


def audit(path):
    problems = []
    wb = openpyxl.load_workbook(path, data_only=False)
    n_formula = check_formulas(path, problems)

    n_dv = sum(len(ws.data_validations.dataValidation)
               for ws in wb.worksheets)
    n_cf = sum(len(ws.conditional_formatting._cf_rules)
               for ws in wb.worksheets)
    _, names = sheet_xml(path)
    charts = len([n for n in names if n.startswith("xl/charts/chart")])

    for sheet, ref, merge in hidden_writes(path):
        problems.append("%s!%s is written inside merge %s and would never "
                        "be visible" % (sheet, ref, merge))

    return {
        "path": path,
        "sheets": wb.sheetnames,
        "hidden": [s.title for s in wb.worksheets
                   if s.sheet_state != "visible"],
        "formulas": n_formula,
        "validations": n_dv,
        "cond_formats": n_cf,
        "charts": charts,
        "problems": problems,
    }


def main(argv):
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) if any(c in a for c in "*?[")
                     else [a])
    if not paths:
        print(__doc__)
        return 1
    bad = 0
    for path in paths:
        r = audit(path)
        print("=" * 78)
        print(path)
        print("  sheets   : %s" % ", ".join(r["sheets"]))
        print("  hidden   : %s" % (", ".join(r["hidden"]) or "-"))
        print("  formulas : %-6d validations %-4d cond. formats %-4d "
              "charts %d" % (r["formulas"], r["validations"],
                             r["cond_formats"], r["charts"]))
        if r["problems"]:
            bad += 1
            print("  PROBLEMS (%d):" % len(r["problems"]))
            for p in r["problems"][:25]:
                print("    - %s" % p)
            if len(r["problems"]) > 25:
                print("    ... and %d more" % (len(r["problems"]) - 25))
        else:
            print("  PROBLEMS : none \u2713")
    print("=" * 78)
    print("clean" if not bad else "%d file(s) need attention" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
