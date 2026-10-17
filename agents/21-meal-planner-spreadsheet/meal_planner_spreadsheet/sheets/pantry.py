"""
Pantry - what you have, what is running low, what expires next.

Enter an item, the quantity and the date you bought or opened it.  The
shelf life is looked up from the Ingredients tab, so the expiry date, the
days left and the "use it or lose it" flag all appear on their own, and
anything inside the window you set on Settings rises to the top of the
fridge and freezer rankings.
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

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng

    def ing(key: str) -> str:
        return lists("Ingredients", key)

    columns = [
        Col("item", "Item", 24, "text", group="what",
            note="Must match a name on the Ingredients tab."),
        Col("category", "Category", 16, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "unit")}),
        Col("storage", "Storage", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("purchase_date", "Bought", 12, "date", group="dates"),
        Col("opened_date", "Opened", 12, "date",
            note="Fill this in when you open a jar or a pack."),
        Col("shelf_life_days", "Shelf life (days)", 12, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("shelf_life_days")) + ")"),
        Col("expiry_date", "Use by", 12, "calc",
            formula='=IF(OR({item}{r}="",{shelf_life_days}{r}=""),"",'
                    'IF({opened_date}{r}<>"",'
                    '{opened_date}{r}+{shelf_life_days}{r},'
                    'IF({purchase_date}{r}<>"",'
                    '{purchase_date}{r}+{shelf_life_days}{r},"")))'),
        Col("days_left", "Days left", 10, "calc",
            formula='=IF(OR({item}{r}="",{expiry_date}{r}=""),"",'
                    '{expiry_date}{r}-TODAY())'),
        Col("use_by_status", "Use by status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({days_left}{r}="","No date",'
                    'IF({days_left}{r}<0,"Expired",'
                    'IF({days_left}{r}<=Expiry_Warning_Days,"Use soon",'
                    '"Fresh"))))'),
        Col("recipe_uses", "Used in recipes", 12, "calc", group="use",
            formula='=IF({item}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{item}{r}))'),
        Col("weeks_of_stock", "Weeks of stock", 12, "calc",
            formula='=IF({item}{r}="","",'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("weeks_of_stock")) + ")"),
        Col("reorder_qty", "Reorder qty", 11, "calc",
            formula='=IF(OR({item}{r}="",{weeks_of_stock}{r}=""),"",'
                    'IF({weeks_of_stock}{r}<1,'
                    'MAX(0,1*IFERROR(' + lookup(
                        "{item}{r}", ing("ingredient"),
                        ing("weekly_need")) + ',0)-{quantity}{r}),0))'),
        Col("low_stock", "Stock level", 11, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({weeks_of_stock}{r}="","",'
                    'IF({weeks_of_stock}{r}<1,"Low","OK")))'),
        Col("value", "Value", 11, "calc", group="money",
            formula='=IF(OR({item}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{item}{r}", ing("ingredient"),
                             ing("price")) + ',""))'),
        Col("fridge_rank", "Fridge rank", 10, "calc", group="rankings",
            formula='=IF(OR({storage}{r}<>"Fridge",{days_left}{r}=""),"",'
                    'SUMPRODUCT(({storage_first}:{storage_last}="Fridge")*'
                    '({days_left_first}:{days_left_last}<'
                    '{days_left}{r}))'
                    '+SUMPRODUCT(({storage_first}:{storage_last}="Fridge")*'
                    '({days_left_first}:{days_left_last}='
                    '{days_left}{r})*(ROW({days_left_first}:'
                    '{days_left_last})<ROW()))+1)'),
        Col("freezer_rank", "Freezer rank", 11, "calc",
            formula='=IF(OR({storage}{r}<>"Freezer",{days_left}{r}=""),"",'
                    'SUMPRODUCT(({storage_first}:{storage_last}="Freezer")*'
                    '({days_left_first}:{days_left_last}<'
                    '{days_left}{r}))'
                    '+SUMPRODUCT(({storage_first}:{storage_last}="Freezer")*'
                    '({days_left_first}:{days_left_last}='
                    '{days_left}{r})*(ROW({days_left_first}:'
                    '{days_left_last})<ROW()))+1)'),
        Col("batch", "Batch / lot", 14, "text", group="detail"),
        Col("store", "Store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("price_paid", "Price paid", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("frozen", "Frozen", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("portion", "Portion", 14, "text",
            note="e.g. 2 portions, half a tub."),
        Col("servings_left", "Servings left", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("status", "Status", 13, "calc",
            formula='=IF({item}{r}="","",'
                    'IF({use_by_status}{r}="Expired","Bin it",'
                    'IF({use_by_status}{r}="Use soon","Cook it",'
                    'IF({low_stock}{r}="Low","Running low","Keep"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Pantry",
        title="Pantry",
        subtitle="What you have in the cupboard, fridge and freezer - with "
                 "use-by dates",
        columns=columns,
        rows=cfg.row_count("Pantry"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Ingredients", "Grocery List", "Leftovers",
        "Fridge & Freezer", "Food Waste", "Help"])
