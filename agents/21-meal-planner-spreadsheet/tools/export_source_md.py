"""
export_source_md.py - exports this product's source code as one Markdown file.

Collects every Python file of the product into `SOURCE_CODE_MEAL.md` so it
can be shared or attached to a download page.

Usage:
    python tools/export_source_md.py --product meal
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRODUCTS = {
    "meal": {
        "title": "Meal Planner & Grocery List - Source Code",
        "out": ROOT / "SOURCE_CODE_MEAL.md",
        "files": [
            "build_meal_planner_workbook.py",
            "meal_planner_spreadsheet/__init__.py",
            "meal_planner_spreadsheet/__main__.py",
            "meal_planner_spreadsheet/cli.py",
            "meal_planner_spreadsheet/config.py",
            "meal_planner_spreadsheet/layout.py",
            "meal_planner_spreadsheet/formats.py",
            "meal_planner_spreadsheet/writer.py",
            "meal_planner_spreadsheet/names.py",
            "meal_planner_spreadsheet/build.py",
            "meal_planner_spreadsheet/sample_data.py",
        ] + [
            f"meal_planner_spreadsheet/sheets/{name}.py"
            for name in sorted(
                p.stem for p in
                (ROOT / "meal_planner_spreadsheet" / "sheets").glob("*.py")
                if p.stem != "__init__")
        ] + [
            "tools/validate_meal_workbook.py",
            "tools/check_meal_sample.py",
            "tools/recalc_check.py",
        ],
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default="meal", choices=sorted(PRODUCTS))
    args = parser.parse_args()

    spec = PRODUCTS[args.product]
    out: Path = spec["out"]
    parts = [
        f"# {spec['title']}",
        "",
        f"Exported {datetime.date.today().isoformat()}.",
        "",
    ]
    for rel in spec["files"]:
        path = ROOT / rel
        if not path.exists():
            print(f"  skip (missing): {rel}")
            continue
        parts.append(f"## `{rel}`")
        parts.append("")
        parts.append("```python")
        parts.append(path.read_text(encoding="utf-8").rstrip())
        parts.append("```")
        parts.append("")
        print(f"  + {rel}")

    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
