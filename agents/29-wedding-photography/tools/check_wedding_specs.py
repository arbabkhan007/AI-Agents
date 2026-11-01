#!/usr/bin/env python3
"""Fast structural sweep over the wedding product's register specs.

Runs in well under a second and catches, before a workbook is ever
built, the four mistakes that are expensive to find later:

1. a formula whose brackets do not balance (concatenated nested IFs
   lose a closing paren silently);
2. a `{token}` that names no column on that sheet;
3. `a+b/c` where `(a+b)/c` was meant;
4. a COUNTIFS/SUMIFS criteria range that carries its own test.

    python3 tools/check_wedding_specs.py
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wedding_photography_spreadsheet.config import Config      # noqa: E402

TOKEN = re.compile(r"\{([a-z_][a-z0-9_]*)\}")
CALL = re.compile(r"\b(COUNTIFS|SUMIFS|AVERAGEIFS)\s*\(")

#: tokens the engine substitutes that are not column keys
ENGINE_TOKENS = {"r", "r_prev", "first", "last"}


def _strings_out(text: str) -> str:
    return re.sub(r'"[^"]*"', '""', text)


def _args(text: str, start: int):
    """Split the argument list of a call whose '(' is at `start`."""
    depth, out, cur, i = 0, [], "", start
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
            if depth == 1:
                i += 1
                continue
        elif ch == ")":
            depth -= 1
            if depth == 0:
                out.append(cur)
                return out, i
        if depth == 1 and ch == ",":
            out.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    return out, i


def collapsed_criteria(formula: str) -> str:
    body = _strings_out(formula)
    for match in CALL.finditer(body):
        name = match.group(1)
        args, _ = _args(body, match.end() - 1)
        first = 1 if name in ("SUMIFS", "AVERAGEIFS") else 0
        if (len(args) - first) % 2:
            return f"{name}: odd number of range/criteria arguments"
        for text in args[first::2]:
            if re.search(r"[<>=]", text):
                return f"{name}: criteria range carries a test -> {text[:40]}"
    return ""


#: Dividing by one of these is a unit conversion, not a mis-bracket.
#: A wedding timeline is `ceremony_time + minutes/1440` - a date serial
#: plus a fraction of a day - and bracketing it as
#: `(ceremony_time + minutes)/1440` would be the actual bug.
TIME_DIVISORS = ("1440", "86400", "24", "60")


def precedence_slip(formula: str) -> str:
    """`a+b/c` at the top level of a division - almost always a bug."""
    body = _strings_out(formula)
    for match in re.finditer(r"/", body):
        tail = body[match.start() + 1:match.start() + 8]
        if re.match(r"(%s)\b" % "|".join(TIME_DIVISORS), tail):
            continue
        # walk left over the numerator at depth 0
        i, depth = match.start() - 1, 0
        while i >= 0:
            ch = body[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and ch in "+-" and i > 0 and \
                    body[i - 1] not in "(,*/+-<>=&":
                return body[max(0, i - 25):match.start() + 12]
            i -= 1
    return ""


def main() -> int:
    from wedding_photography_spreadsheet.build import REGISTER_MODULES

    cfg = Config()
    problems = 0
    total_cols = 0
    total_formulas = 0

    for module in REGISTER_MODULES:
        spec = module.spec(cfg)
        keys = {c.key for c in spec.columns}
        formulas = [c for c in spec.columns if c.formula]
        total_cols += len(spec.columns)
        total_formulas += len(formulas)

        for column in formulas:
            text = column.formula
            if not isinstance(text, str):
                problems += 1
                print(f"{spec.name}.{column.key}: formula is "
                      f"{type(text).__name__}, not a string")
                continue
            where = f"{spec.name}.{column.key}"

            body = _strings_out(text)
            if body.count("(") != body.count(")"):
                problems += 1
                print(f"{where}: brackets {body.count('(')} open vs "
                      f"{body.count(')')} close")
            if text.count('"') % 2:
                problems += 1
                print(f"{where}: odd number of quotes")
            if text != text.strip():
                problems += 1
                print(f"{where}: stray whitespace around the formula")

            for token in set(TOKEN.findall(text)):
                if token in ENGINE_TOKENS or token in keys:
                    continue
                if token.endswith("_first") and token[:-6] in keys:
                    continue
                if token.endswith("_last") and token[:-5] in keys:
                    continue
                problems += 1
                print(f"{where}: {{{token}}} is not a column on this sheet")

            slip = collapsed_criteria(text)
            if slip:
                problems += 1
                print(f"{where}: {slip}")
            slip = precedence_slip(text)
            if slip:
                problems += 1
                print(f"{where}: a+b/c where (a+b)/c was meant -> {slip}")

        print(f"  {spec.name:26s} {len(spec.columns):3d} cols, "
              f"{len(formulas):3d} formulas, {spec.rows:5d} rows")

    print(f"\n{len(REGISTER_MODULES)} registers, {total_cols} columns, "
          f"{total_formulas} formula columns, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
