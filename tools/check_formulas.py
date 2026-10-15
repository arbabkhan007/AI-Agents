#!/usr/bin/env python3
"""
Parse every formula in a workbook the way Excel's formula parser does.

    python tools/check_formulas.py "output/Meal Planner & Grocery List.xlsx"

Excel's repair dialog ("Removed Records: Formula from ...") is almost
always caused by a formula its parser cannot read.  This walks the token
stream of every `<f>` in every sheet part and reports anything that is not
a well formed formula: unbalanced brackets, stray operators, a bare word
that is not a name or a function, a bad reference, a wrong argument count
for a known function.

It is deliberately strict - it errs towards flagging things that Excel
would in fact accept, so every hit is worth a look.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile

SHEET_RE = re.compile(r"xl/worksheets/sheet(\d+)\.xml$")

#: functions and how many arguments each one takes.  None = any count.
ARITY = {
    "IF": (2, 3), "IFERROR": (2, 2), "AND": (1, None), "OR": (1, None),
    "NOT": (1, 1), "SUM": (1, None), "SUMIFS": (3, None),
    "SUMPRODUCT": (1, None), "COUNTIFS": (2, None), "COUNTIF": (2, 2),
    "COUNTA": (1, None), "COUNTBLANK": (1, 1), "COUNT": (1, None),
    "INDEX": (2, 4), "MATCH": (2, 3), "MAX": (1, None), "MIN": (1, None),
    "AVERAGE": (1, None), "AVERAGEIFS": (3, None), "ROUND": (2, 2),
    "ROUNDUP": (2, 2), "ROUNDDOWN": (2, 2), "CEILING": (2, 2),
    "ABS": (1, 1), "TEXT": (2, 2), "TODAY": (0, 0), "NOW": (0, 0),
    "DATEVALUE": (1, 1), "DATE": (3, 3), "YEAR": (1, 1), "MONTH": (1, 1),
    "DAY": (1, 1), "WEEKDAY": (1, 2), "ROW": (0, 1), "COLUMN": (0, 1),
    "ROWS": (1, 1), "COLUMNS": (1, 1), "LEN": (1, 1), "LEFT": (1, 2),
    "RIGHT": (1, 2), "MID": (3, 3), "TRIM": (1, 1), "UPPER": (1, 1),
    "LOWER": (1, 1), "VALUE": (1, 1), "ISBLANK": (1, 1),
    "ISNUMBER": (1, 1), "ISTEXT": (1, 1), "ISERROR": (1, 1),
    "ISNA": (1, 1), "TRUE": (0, 0), "FALSE": (0, 0), "NA": (0, 0),
    "CHOOSE": (2, None), "INT": (1, 1), "MOD": (2, 2), "SIGN": (1, 1),
    "SQRT": (1, 1), "POWER": (2, 2), "SUBTOTAL": (2, None),
}

CELL_RE = re.compile(r"^\$?[A-Za-z]{1,3}\$?\d{1,7}$")
RANGE_RE = re.compile(
    r"^\$?[A-Za-z]{1,3}\$?\d{1,7}:\$?[A-Za-z]{1,3}\$?\d{1,7}$")
COL_RE = re.compile(r"^\$?[A-Za-z]{1,3}:\$?[A-Za-z]{1,3}$")
ROW_RE = re.compile(r"^\$?\d{1,7}:\$?\d{1,7}$")
NAME_RE = re.compile(r"^[A-Za-z_\\][A-Za-z0-9_.\\]*$")
ERRORS = {"#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A", "#NULL!", "#NUM!"}
BOOLEANS = {"TRUE", "FALSE"}


class Bad(Exception):
    pass


def tokenize(text):
    """Split a formula into (kind, value) tokens."""
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch in " \t\n\r":
            i += 1
            continue
        if ch == '"':                                  # string literal
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            if j >= n:
                raise Bad("unterminated string")
            out.append(("str", text[i + 1:j]))
            i = j + 1
            continue
        if ch == "'":                                  # quoted sheet name
            j = text.find("'", i + 1)
            if j < 0:
                raise Bad("unterminated sheet name")
            out.append(("sheet", text[i + 1:j]))
            i = j + 1
            continue
        if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
            j = i
            while j < n and (text[j].isdigit() or text[j] == "."):
                j += 1
            if j < n and text[j] in "eE" and j + 1 < n and \
                    (text[j + 1].isdigit() or text[j + 1] in "+-"):
                j += 2
                while j < n and text[j].isdigit():
                    j += 1
            out.append(("num", text[i:j]))
            i = j
            continue
        if ch.isalpha() or ch in "_$\\":
            j = i
            while j < n and (text[j].isalnum() or text[j] in "_$.\\"):
                j += 1
            word = text[i:j]
            if word.upper() in ERRORS:
                out.append(("error", word.upper()))
            elif CELL_RE.match(word) or COL_RE.match(word) or \
                    ROW_RE.match(word):
                out.append(("ref", word))
            else:
                out.append(("name", word))
            i = j
            continue
        two = text[i:i + 2]
        if two in ("<=", ">=", "<>"):
            out.append(("op", two))
            i += 2
            continue
        if ch in "+-*/^&=<>%(),:{}!;":
            out.append(("op", ch))
            i += 1
            continue
        raise Bad(f"unexpected character {ch!r}")
    return out


class Parser:
    def __init__(self, tokens, sheet_names, defined):
        self.t = tokens
        self.i = 0
        self.sheets = sheet_names
        self.names = defined

    # -- helpers ---------------------------------------------------------
    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def at_op(self, *ops):
        k, v = self.peek()
        return k == "op" and v in ops

    def expect_op(self, op):
        if not self.at_op(op):
            raise Bad(f"expected {op!r}, got {self.peek()!r}")
        self.i += 1

    # -- grammar ---------------------------------------------------------
    def expression(self):
        self.concat()
        while self.at_op("=", "<>", "<", ">", "<=", ">="):
            self.i += 1
            self.concat()

    def concat(self):
        self.additive()
        while self.at_op("&"):
            self.i += 1
            self.additive()

    def additive(self):
        self.multiplicative()
        while self.at_op("+", "-"):
            self.i += 1
            self.multiplicative()

    def multiplicative(self):
        self.unary()
        while self.at_op("*", "/"):
            self.i += 1
            self.unary()

    def unary(self):
        while self.at_op("-", "+"):
            self.i += 1
        self.power()

    def power(self):
        self.postfix()
        if self.at_op("^"):
            self.i += 1
            self.unary()

    def postfix(self):
        self.primary()
        while self.at_op("%"):
            self.i += 1

    def primary(self):
        kind, val = self.peek()
        if kind is None:
            raise Bad("unexpected end of formula")
        if kind in ("num", "str", "error"):
            self.i += 1
            return
        if kind == "ref":
            self.i += 1
            if self.at_op(":"):
                self.i += 1
                k2, v2 = self.peek()
                if k2 != "ref":
                    raise Bad(f"bad range end: {v2!r}")
                self.i += 1
            return
        if kind == "name":
            if val.upper() in BOOLEANS:
                self.i += 1
                return
            self.i += 1
            # function call?
            if self.at_op("("):
                self.call(val.upper())
                return
            # plain name: must be followed by a reference-ish token or be
            # a known defined name / sheet prefix
            k2, v2 = self.peek()
            if k2 == "op" and v2 == "!":
                self.i += 1
                if val.upper() not in self.sheets:
                    raise Bad(f"no such sheet: {val!r}")
                self.reference_tail()
                return
            if k2 == "op" and v2 in ("(", ")", ",", ":", "%") or \
                    k2 is None or (k2 == "op" and v2 in "+-*/^&=<>"):
                if val.upper() not in self.names and \
                        val.upper() not in ARITY:
                    raise Bad(f"bare word {val!r} is not a defined name, "
                              f"a function or a cell reference")
                return
            raise Bad(f"unexpected token after name {val!r}: {v2!r}")
        if kind == "sheet":
            self.i += 1
            if not self.at_op("!"):
                raise Bad("quoted sheet name not followed by '!'")
            self.i += 1
            if val.upper() not in self.sheets:
                raise Bad(f"no such sheet: {val!r}")
            self.reference_tail()
            return
        if kind == "op" and val == "(":
            self.i += 1
            self.expression()
            self.expect_op(")")
            return
        if kind == "op" and val == "{":
            self.array()
            return
        raise Bad(f"unexpected token {val!r}")

    def reference_tail(self):
        kind, val = self.peek()
        if kind not in ("ref", "name"):
            raise Bad(f"expected a reference after '!', got {val!r}")
        if kind == "ref" and not (CELL_RE.match(val) or COL_RE.match(val)
                                  or ROW_RE.match(val)):
            raise Bad(f"not a cell reference: {val!r}")
        self.i += 1
        if self.at_op(":"):
            self.i += 1
            k2, v2 = self.peek()
            if k2 != "ref":
                raise Bad(f"bad range end: {v2!r}")
            self.i += 1

    def array(self):
        self.expect_op("{")
        depth = 1
        while depth:
            kind, val = self.next()
            if kind is None:
                raise Bad("unterminated array")
            if kind == "op" and val == "{":
                depth += 1
            elif kind == "op" and val == "}":
                depth -= 1
            elif kind == "op" and val in (",", ";"):
                continue
            elif kind in ("num", "str", "error", "name"):
                continue
            else:
                raise Bad(f"bad token in array: {val!r}")

    def call(self, name):
        self.expect_op("(")
        args = 0
        if not self.at_op(")"):
            while True:
                if self.at_op(")"):
                    break
                self.expression()
                args += 1
                if self.at_op(","):
                    self.i += 1
                    continue
                break
        self.expect_op(")")
        if name in ARITY:
            lo, hi = ARITY[name]
            if args < lo or (hi is not None and args > hi):
                raise Bad(f"{name} takes {lo}"
                          f"{'' if hi is None else '-' + str(hi)} "
                          f"arguments, got {args}")

    def run(self):
        self.expression()
        if self.i != len(self.t):
            raise Bad(f"trailing tokens: {self.t[self.i:]!r}")


def check(text, sheet_names, defined):
    tokens = tokenize(text)
    Parser(tokens, sheet_names, defined).run()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("workbook")
    ap.add_argument("--limit", type=int, default=25,
                    help="how many failures to print per sheet")
    args = ap.parse_args(argv)

    path = os.path.abspath(args.workbook)
    z = zipfile.ZipFile(path)
    wbx = z.read("xl/workbook.xml").decode("utf8")
    defined = {m.upper() for m in
               re.findall(r'<definedName name="([^"]+)"', wbx)}
    defined |= {"_XLFN", "PRINT_AREA", "PRINT_TITLES"}
    sheets = [s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
              for s in re.findall(r'<sheet name="([^"]*)"', wbx)]
    sheet_names = {s.upper() for s in sheets}

    total = 0
    bad_total = 0
    for name in sorted(z.namelist()):
        m = SHEET_RE.search(name)
        if not m:
            continue
        idx = int(m.group(1))
        sheet = sheets[idx - 1] if idx <= len(sheets) else f"sheet{idx}"
        x = z.read(name).decode("utf8")
        forms = re.findall(r'<f[^>]*>([^<]*)</f>', x)
        bad = []
        for raw in forms:
            total += 1
            text = (raw.replace("&lt;", "<").replace("&gt;", ">")
                       .replace("&quot;", '"').replace("&apos;", "'")
                       .replace("&amp;", "&"))
            try:
                check(text, sheet_names, defined)
            except Bad as exc:
                bad.append((text, str(exc)))
        bad_total += len(bad)
        if bad:
            print(f"\n{sheet}  ({name}): {len(bad)} of {len(forms)} "
                  f"formulas failed")
            for text, why in bad[:args.limit]:
                print(f"    {why}")
                print(f"      {text[:220]}")
    print(f"\nchecked {total:,} formulas across "
          f"{len([n for n in z.namelist() if SHEET_RE.search(n)])} sheets, "
          f"{bad_total} failed")
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
