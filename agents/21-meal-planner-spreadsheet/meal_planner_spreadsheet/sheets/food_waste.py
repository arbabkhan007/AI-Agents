"""
Food Waste - what got thrown away, why, and what it cost.

Logging waste is the fastest way to cut a food bill.  Each row prices the
wasted quantity from the Ingredients tab, ranks it against everything else
you have binned and shows how much of the month's waste it represents.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer

REASONS = ["Expired", "Spoiled", "Mouldy", "Leftover not eaten",
           "Cooked too much", "Burnt", "Tasted bad", "Bought too much",
           "Child refused", "Plans changed"]
STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("waste_id", "Waste ID", 11, "text", group="what",
            note="Anything you like - 'W-01' is a good pattern."),
        Col("date", "Date", 12, "date"),
        Col("item", "Item", 24, "text",
            note="Must match a name on the Ingredients tab so the cost can "
                 "be looked up."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("qty", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("unit_price", "Price / unit", 11, "calc", group="money",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("cost", "Cost binned", 11, "calc",
            formula='=IF(OR({item}{r}="",{qty}{r}="",'
                    '{unit_price}{r}=""),"",{qty}{r}*{unit_price}{r})'),
        Col("reason", "Reason", 20, "select",
            validate={"type": "list", "source": REASONS},
            note="The reason it was binned - this is what the reports "
                 "group by."),
        Col("recipe", "From recipe", 22, "select",
            validate={"type": "list", "source": "=" + lists("Recipes",
                                                            "recipe")}),
        Col("storage_at_waste", "Stored in", 12, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("avoidable", "Avoidable", 10, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "yes_no")},
            note="No = it was bones, peel or packaging you cannot eat."),
        Col("portion", "Portion", 14, "text"),
        Col("store", "Bought at", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("month", "Month", 11, "calc", group="reporting",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("month_total", "Month total", 12, "calc",
            formula='=IF(OR({date}{r}="",{cost}{r}=""),"",'
                    'SUMIFS({cost_first}:{cost_last},'
                    '{month_first}:{month_last},{month}{r}))'),
        Col("share_of_total", "Share of month", 12, "calc",
            formula='=IF(OR({cost}{r}="",{month_total}{r}="",'
                    '{month_total}{r}=0),"",{cost}{r}/{month_total}{r})'),
        Col("waste_rank", "Waste rank", 10, "calc", group="rankings",
            formula='=IF(OR({item}{r}="",{qty}{r}=""),"",'
                    'COUNTIFS({qty_first}:{qty_last},'
                    '">"&{qty}{r})+1)'),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({avoidable}{r}="No","Unavoidable","Avoidable"))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Food Waste",
        title="Food Waste",
        subtitle="What you binned, why, and what it cost",
        columns=columns,
        rows=cfg.row_count("Food Waste"),
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Pantry", "Leftovers", "Ingredients", "Sustainability",
        "Reports", "Help"])
