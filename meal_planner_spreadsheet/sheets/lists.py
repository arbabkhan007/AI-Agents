"""
Lists - every drop down source in one place.

The buyer edits these lists once and every planner grid, grocery list,
recipe tag and report follows.  The seven columns below are also published
as dynamic named ranges (``Meal_Slots``, ``Unit_List``, ...) so the
validation on the other tabs always points here.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

MEAL_SLOTS = ["Breakfast", "Morning snack", "Lunch", "Afternoon snack",
              "Dinner", "Evening snack", "Dessert"]

UNITS = ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "clove", "slice",
         "piece", "can", "tin", "packet", "bunch", "handful", "pinch",
         "sprig", "cube", "sheet", "roll", "jar", "bottle", "punnet",
         "stalk", "bulb", "strip", "portion", "bunch"]

CATEGORIES = ["Vegetables", "Fruit", "Meat & Fish", "Dairy & Eggs",
              "Bakery", "Grains & Pasta", "Tins & Jars", "Frozen",
              "Herbs & Spices", "Condiments", "Snacks", "Drinks",
              "Baking", "Household", "Other"]

CUISINES = ["Any", "Italian", "Mexican", "Indian", "Chinese", "Thai",
            "Japanese", "Mediterranean", "Middle Eastern", "French",
            "American", "British", "Caribbean", "African", "Vietnamese",
            "Korean", "Greek", "Spanish", "Turkish", "Moroccan"]

TAGS = ["Quick", "One pot", "Slow cooker", "Air fryer", "Grill", "Oven",
        "No cook", "Batch cook", "Freezer friendly", "Kid friendly",
        "Comfort food", "Light", "High protein", "Low carb", "Budget",
        "Date night", "Picnic", "Soup", "Salad", "Sandwich", "Stew",
        "Curry", "Stir fry", "Pasta", "Rice bowl", "Tacos", "Pizza",
        "Brunch", "Dessert", "Drink"]

STORES = ["Greenfield Market", "Corner Grocer", "Bulk Barn",
          "Farmers Market", "Fresh Direct", "Asian Supermarket",
          "Butcher", "Baker", "Online Order", "Other"]

DIETS = ["None", "Vegetarian", "Vegan", "Pescatarian", "Gluten free",
         "Dairy free", "Nut free", "Halal", "Kosher", "Low FODMAP",
         "Keto", "Paleo", "Low sodium", "Diabetic friendly"]

STATUS = ["Planned", "Cooking", "Cooked", "Eaten", "Skipped", "Takeaway",
          "Eating out", "Leftover"]

RECIPE_CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert",
                     "Drink", "Side", "Sauce", "Base"]

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Lists",
        title="Lists",
        subtitle="Drop down sources - edit these and every planner, grocery "
                 "list and report follows",
        columns=[
            Col("meal_slot", "Meal slots", 18, "select",
                validate={"type": "list", "source": MEAL_SLOTS},
                note="Breakfast, lunch, dinner and the snacks in between."),
            Col("unit", "Units", 12, "select",
                validate={"type": "list", "source": UNITS},
                note="Measurement units used by recipes and the pantry."),
            Col("category", "Categories", 18, "select",
                validate={"type": "list", "source": CATEGORIES},
                note="Aisle / section of the shop."),
            Col("cuisine", "Cuisines", 18, "select",
                validate={"type": "list", "source": CUISINES},
                note="Used for variety reporting and rotation rules."),
            Col("tag", "Tags", 16, "select",
                validate={"type": "list", "source": TAGS},
                note="Recipe tags: quick, one pot, batch cook ..."),
            Col("store", "Stores", 20, "select",
                validate={"type": "list", "source": STORES},
                note="Where you shop. Also drives the store reports."),
            Col("diet", "Dietary needs", 18, "select",
                validate={"type": "list", "source": DIETS},
                note="Household dietary filters."),
            Col("status", "Status", 14, "select",
                validate={"type": "list", "source": STATUS},
                note="Meal plan status values."),
            Col("yes_no", "Yes / No", 10, "select",
                validate={"type": "list", "source": YES_NO}),
            Col("recipe_category", "Recipe categories", 18, "select",
                validate={"type": "list", "source": RECIPE_CATEGORIES},
                note="What kind of meal it is, as opposed to which aisle "
                     "the ingredients come from."),
        ],
        rows=cfg.row_count("Lists"),
        tab_color=Palette.primary_mid,
        freeze_cols=1,
        samples=[],
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec, sample_index=writer.samples.get("Lists"))
    writer.finish_sheet(ws, spec, links=["Dashboard", "Settings", "Recipes",
                                         "Grocery List", "Help"],
                        banding=False)
