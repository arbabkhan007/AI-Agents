"""
Example data.

The workbook ships with a filled copy and a blank copy.  Everything in this
module is written into the filled copy only - it is a realistic three weeks
of meals for a family of four, with the recipes, ingredients, prices, pantry
stock, spending and waste that go with it.

Ingredient names are spelled identically here and on every tab, because the
cost and nutrition lookups match on the name.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

try:
    from .config import Config
except ImportError:                        # pragma: no cover
    from config import Config

# ---------------------------------------------------------------------------
# Ingredients: name, category, unit, price, pack, kcal, protein, carbs, fat,
#              fibre, shelf life, storage, staple, allergens
# ---------------------------------------------------------------------------
INGREDIENTS: List[tuple] = [
    ("Chicken breast", "Meat & Fish", "g", 0.0099, 500, 165, 31, 0, 3.6, 0,
     2, "Fridge", "Yes", ""),
    ("Chicken thigh", "Meat & Fish", "g", 0.0079, 1000, 209, 26, 0, 10.9, 0,
     2, "Fridge", "No", ""),
    ("Beef mince", "Meat & Fish", "g", 0.0119, 500, 250, 26, 0, 15, 0,
     2, "Fridge", "Yes", ""),
    ("Beef stewing steak", "Meat & Fish", "g", 0.0149, 700, 250, 26, 0, 15,
     0, 2, "Fridge", "No", ""),
    ("Pork sausage", "Meat & Fish", "g", 0.0069, 400, 290, 12, 3, 25, 0,
     3, "Fridge", "No", ""),
    ("Bacon", "Meat & Fish", "g", 0.0129, 250, 541, 37, 1.4, 42, 0,
     7, "Fridge", "No", ""),
    ("Salmon fillet", "Meat & Fish", "g", 0.0299, 240, 208, 20, 0, 13, 0,
     1, "Fridge", "No", "fish"),
    ("Cod fillet", "Meat & Fish", "g", 0.0199, 300, 82, 18, 0, 0.7, 0,
     1, "Fridge", "No", "fish"),
    ("Prawns", "Meat & Fish", "g", 0.0199, 200, 99, 24, 0, 0.3, 0,
     1, "Fridge", "No", "shellfish"),
    ("Eggs", "Dairy & Eggs", "piece", 0.42, 6, 78, 6.3, 0.6, 5.3, 0,
     21, "Fridge", "Yes", "egg"),
    ("Milk", "Dairy & Eggs", "ml", 0.0013, 2000, 42, 3.4, 5, 1, 0,
     5, "Fridge", "Yes", "dairy"),
    ("Cheddar cheese", "Dairy & Eggs", "g", 0.0119, 350, 403, 25, 1.3, 33,
     0, 21, "Fridge", "Yes", "dairy"),
    ("Butter", "Dairy & Eggs", "g", 0.0099, 250, 717, 0.9, 0.1, 81, 0,
     60, "Fridge", "Yes", "dairy"),
    ("Greek yoghurt", "Dairy & Eggs", "g", 0.0049, 500, 97, 9, 3.6, 5, 0,
     7, "Fridge", "Yes", "dairy"),
    ("Cream cheese", "Dairy & Eggs", "g", 0.0079, 300, 342, 6, 4, 34, 0,
     14, "Fridge", "No", "dairy"),
    ("Rice", "Grains & Pasta", "g", 0.0021, 1000, 360, 6.7, 79, 0.6, 1.3,
     365, "Pantry", "Yes", ""),
    ("Pasta", "Grains & Pasta", "g", 0.0019, 500, 371, 13, 75, 1.5, 3,
     365, "Pantry", "Yes", "gluten"),
    ("Spaghetti", "Grains & Pasta", "g", 0.0021, 500, 371, 13, 75, 1.5, 3,
     365, "Pantry", "Yes", "gluten"),
    ("Bread", "Bakery", "slice", 0.09, 20, 265, 9, 49, 3.2, 2.7,
     4, "Cupboard", "Yes", "gluten"),
    ("Bread rolls", "Bakery", "piece", 0.35, 6, 289, 9.5, 53, 3.5, 3,
     3, "Cupboard", "No", "gluten"),
    ("Flour", "Baking", "g", 0.0011, 1500, 364, 10, 76, 1, 2.7,
     365, "Pantry", "Yes", "gluten"),
    ("Sugar", "Baking", "g", 0.0012, 1000, 387, 0, 100, 0, 0,
     365, "Pantry", "Yes", ""),
    ("Baking powder", "Baking", "tsp", 0.02, 100, 2, 0, 1, 0, 0,
     365, "Pantry", "No", ""),
    ("Olive oil", "Condiments", "tbsp", 0.11, 500, 119, 0, 0, 13.5, 0,
     365, "Cupboard", "Yes", ""),
    ("Vegetable oil", "Condiments", "tbsp", 0.05, 500, 120, 0, 0, 13.6, 0,
     365, "Cupboard", "Yes", ""),
    ("Soy sauce", "Condiments", "tbsp", 0.06, 250, 8, 1.3, 0.8, 0, 0.1,
     180, "Cupboard", "No", "soy"),
    ("Tinned tomatoes", "Tins & Jars", "can", 0.55, 400, 32, 1.6, 5, 0.3,
     1.5, 365, "Pantry", "Yes", ""),
    ("Tomato puree", "Tins & Jars", "tbsp", 0.05, 200, 32, 1.6, 5, 0.3, 1.5,
     60, "Cupboard", "No", ""),
    ("Coconut milk", "Tins & Jars", "can", 1.05, 400, 230, 2.3, 3, 24, 2.2,
     365, "Pantry", "No", ""),
    ("Tinned sweetcorn", "Tins & Jars", "can", 0.49, 340, 96, 3.2, 21, 1.5,
     2, 365, "Pantry", "No", ""),
    ("Tinned chickpeas", "Tins & Jars", "can", 0.59, 400, 139, 7, 23, 2.6,
     6, 365, "Pantry", "No", ""),
    ("Tinned kidney beans", "Tins & Jars", "can", 0.55, 400, 127, 8.7, 20,
     0.5, 6.5, 365, "Pantry", "No", ""),
    ("Onion", "Vegetables", "piece", 0.28, 3, 44, 1.2, 9, 0.1, 1.7,
     30, "Pantry", "Yes", ""),
    ("Garlic", "Vegetables", "clove", 0.09, 6, 4, 0.2, 1, 0, 0.1,
     21, "Pantry", "Yes", ""),
    ("Carrot", "Vegetables", "piece", 0.12, 6, 41, 0.9, 10, 0.2, 2.8,
     21, "Fridge", "Yes", ""),
    ("Celery", "Vegetables", "stalk", 0.22, 4, 16, 0.7, 3, 0.2, 1.6,
     14, "Fridge", "No", ""),
    ("Bell pepper", "Vegetables", "piece", 0.65, 3, 31, 1, 6, 0.3, 2.1,
     10, "Fridge", "No", ""),
    ("Broccoli", "Vegetables", "piece", 0.79, 1, 55, 3.7, 10, 0.6, 3.3,
     7, "Fridge", "No", ""),
    ("Courgette", "Vegetables", "piece", 0.55, 2, 33, 2.4, 3.1, 0.6, 1.7,
     7, "Fridge", "No", ""),
    ("Spinach", "Vegetables", "g", 0.0069, 200, 23, 2.9, 3.6, 0.4, 2.2,
     5, "Fridge", "No", ""),
    ("Mushrooms", "Vegetables", "g", 0.0059, 250, 22, 3.1, 3.3, 0.3, 1,
     5, "Fridge", "No", ""),
    ("Sweet potato", "Vegetables", "piece", 0.62, 2, 90, 2, 20, 0.2, 3.3,
     21, "Pantry", "No", ""),
    ("Potato", "Vegetables", "g", 0.0014, 2500, 77, 2, 17, 0.1, 2.2,
     30, "Pantry", "Yes", ""),
    ("Cherry tomatoes", "Vegetables", "g", 0.0099, 300, 18, 0.9, 3.9, 0.2,
     1.2, 7, "Fridge", "No", ""),
    ("Cucumber", "Vegetables", "piece", 0.69, 1, 16, 0.7, 3.6, 0.1, 0.5,
     7, "Fridge", "No", ""),
    ("Lettuce", "Vegetables", "piece", 0.99, 1, 15, 1.4, 2.9, 0.2, 1.3,
     5, "Fridge", "No", ""),
    ("Lemon", "Fruit", "piece", 0.45, 3, 29, 1.1, 9, 0.3, 2.8,
     14, "Fridge", "No", ""),
    ("Banana", "Fruit", "piece", 0.19, 5, 89, 1.1, 23, 0.3, 2.6,
     5, "Cupboard", "Yes", ""),
    ("Apple", "Fruit", "piece", 0.35, 4, 52, 0.3, 14, 0.2, 2.4,
     30, "Fridge", "Yes", ""),
    ("Frozen berries", "Frozen", "g", 0.0059, 500, 50, 0.8, 12, 0.3, 3.5,
     180, "Freezer", "No", ""),
    ("Frozen peas", "Frozen", "g", 0.0029, 900, 81, 5.4, 14, 0.4, 5.5,
     180, "Freezer", "Yes", ""),
    ("Oats", "Grains & Pasta", "g", 0.0019, 1000, 389, 16.9, 66, 6.9, 10.6,
     365, "Pantry", "Yes", ""),
    ("Peanut butter", "Condiments", "tbsp", 0.13, 340, 188, 8, 6, 16, 1.8,
     180, "Cupboard", "No", "peanuts"),
    ("Honey", "Condiments", "tbsp", 0.12, 340, 64, 0.1, 17, 0, 0,
     365, "Cupboard", "No", ""),
    ("Stock cube", "Condiments", "cube", 0.08, 12, 3, 0.2, 0.5, 0.1, 0,
     365, "Pantry", "Yes", ""),
    ("Curry paste", "Condiments", "tbsp", 0.16, 200, 45, 1, 4, 3, 0.8,
     90, "Cupboard", "No", ""),
    ("Chilli flakes", "Herbs & Spices", "tsp", 0.04, 40, 6, 0.2, 1, 0.3,
     1.1, 365, "Pantry", "No", ""),
    ("Cumin", "Herbs & Spices", "tsp", 0.04, 40, 8, 0.4, 0.9, 0.5, 0.6,
     365, "Pantry", "No", ""),
    ("Basil", "Herbs & Spices", "tsp", 0.05, 20, 2, 0.3, 0.4, 0.1, 0.4,
     60, "Cupboard", "No", ""),
    ("Coriander", "Herbs & Spices", "sprig", 0.15, 10, 2, 0.2, 0.4, 0.1,
     0.3, 5, "Fridge", "No", ""),
    ("Kitchen roll", "Household", "roll", 2.49, 2, 0, 0, 0, 0, 0,
     0, "Cupboard", "Yes", ""),
    ("Washing up liquid", "Household", "bottle", 1.79, 1, 0, 0, 0, 0, 0,
     0, "Cupboard", "Yes", ""),
]

# ---------------------------------------------------------------------------
# Recipes: name, category, cuisine, servings, prep, cook, kcal, protein,
#          carbs, fat, fibre, sugar, sodium, flags, season, rating, source
# ---------------------------------------------------------------------------
def _r(name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
       sod, flags, season, rating, source):
    return (name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
            sod, flags, season, rating, source)


RECIPES: List[tuple] = [
    _r("Porridge with banana", "Breakfast", "British", 4, 5, 8, 320, 11, 54,
       6, 7, 18, 90, "VGFD", "Any", 4, "Everyday"),
    _r("Scrambled eggs on toast", "Breakfast", "British", 4, 5, 6, 410, 20,
       34, 21, 2, 5, 520, "VGFD", "Any", 4, "Everyday"),
    _r("Overnight oats", "Breakfast", "Any", 2, 10, 0, 380, 14, 52, 12, 8,
       14, 110, "VGFD", "Any", 3, "Blog"),
    _r("Yoghurt and berries", "Breakfast", "Any", 4, 5, 0, 240, 12, 32, 6,
       3, 24, 90, "VGF", "Summer", 4, "Everyday"),
    _r("Pancakes", "Breakfast", "American", 4, 10, 12, 390, 11, 52, 14, 2,
       16, 380, "FV", "Any", 5, "Family recipe"),
    _r("Chicken & veg traybake", "Dinner", "British", 4, 15, 40, 520, 42, 45,
       17, 7, 11, 620, "GFDK", "Any", 5, "Everyday"),
    _r("Spaghetti bolognese", "Dinner", "Italian", 4, 15, 35, 610, 34, 68,
       19, 6, 12, 700, "DFK", "Any", 5, "Everyday"),
    _r("Vegetable curry", "Dinner", "Indian", 4, 15, 30, 480, 14, 72, 14,
       12, 14, 640, "VG", "Any", 4, "Everyday"),
    _r("Chicken curry", "Dinner", "Indian", 4, 20, 35, 560, 40, 52, 20, 6,
       10, 780, "GFDK", "Winter", 5, "Everyday"),
    _r("Salmon & rice", "Dinner", "Any", 4, 10, 25, 540, 36, 52, 20, 4, 6,
       380, "GFDK", "Any", 4, "Everyday"),
    _r("Beef chilli", "Dinner", "Mexican", 4, 15, 45, 590, 36, 55, 24, 11,
       12, 720, "GFDK", "Winter", 5, "Everyday"),
    _r("Pizza night", "Dinner", "Italian", 4, 20, 15, 640, 28, 72, 24, 5,
       10, 900, "FVK", "Any", 5, "Friday tradition"),
    _r("Pasta primavera", "Dinner", "Italian", 4, 15, 20, 470, 18, 66, 14,
       8, 9, 520, "V", "Spring", 4, "Everyday"),
    _r("Fish finger sandwich", "Lunch", "British", 4, 5, 10, 450, 24, 44,
       18, 3, 6, 780, "DFK", "Any", 3, "Quick"),
    _r("Jacket potato & beans", "Lunch", "British", 4, 10, 60, 420, 15, 68,
       9, 11, 10, 640, "VG", "Winter", 4, "Everyday"),
    _r("Chicken Caesar salad", "Lunch", "American", 4, 15, 12, 430, 34, 16,
       24, 4, 5, 720, "GFDK", "Summer", 4, "Everyday"),
    _r("Tomato soup & bread", "Lunch", "British", 4, 10, 25, 380, 12, 54,
       12, 6, 14, 780, "FVD", "Autumn", 5, "Everyday"),
    _r("Pasta salad", "Lunch", "Any", 4, 15, 12, 460, 16, 62, 16, 6, 9,
       560, "V", "Summer", 4, "Everyday"),
    _r("Omelette & salad", "Lunch", "French", 2, 10, 8, 380, 24, 6, 28, 3,
       3, 480, "VGFDK", "Any", 4, "Quick"),
    _r("Beef stew & dumplings", "Dinner", "British", 4, 20, 120, 620, 40, 52,
       24, 7, 9, 720, "DFK", "Winter", 5, "Sunday"),
    _r("Stir fry noodles", "Dinner", "Chinese", 4, 15, 12, 520, 26, 64, 18,
       6, 12, 900, "DF", "Any", 4, "Quick"),
    _r("Tuna pasta bake", "Dinner", "Italian", 4, 15, 30, 560, 34, 58, 20,
       5, 8, 760, "DFK", "Any", 4, "Everyday"),
    _r("Chicken fajitas", "Dinner", "Mexican", 4, 15, 15, 580, 38, 54, 22,
       7, 8, 780, "GFD", "Any", 5, "Friday"),
    _r("Shepherd's pie", "Dinner", "British", 4, 25, 45, 640, 34, 54, 28,
       7, 10, 760, "DFK", "Winter", 5, "Sunday"),
    _r("Vegetable lasagne", "Dinner", "Italian", 4, 25, 50, 590, 26, 58, 26,
       9, 14, 720, "V", "Any", 4, "Batch"),
    _r("Pork sausages & mash", "Dinner", "British", 4, 10, 25, 660, 30, 52,
       34, 6, 8, 900, "GFDK", "Any", 4, "Everyday"),
    _r("Fish pie", "Dinner", "British", 4, 25, 40, 600, 36, 48, 26, 5, 8,
       780, "DFK", "Winter", 4, "Sunday"),
    _r("Chicken fried rice", "Dinner", "Chinese", 4, 15, 12, 540, 32, 62,
       18, 4, 6, 820, "DF", "Any", 4, "Quick"),
    _r("Bolognese pasta bake", "Dinner", "Italian", 4, 20, 35, 620, 36, 60,
       22, 6, 12, 780, "DFK", "Any", 5, "Batch"),
    _r("Lentil soup", "Lunch", "Any", 4, 10, 30, 320, 16, 46, 6, 12, 6,
       560, "VG", "Winter", 4, "Batch"),
    _r("Cheese & tomato toastie", "Lunch", "British", 2, 5, 8, 480, 20, 42,
       24, 3, 7, 900, "V", "Any", 4, "Quick"),
    _r("Chicken noodle soup", "Lunch", "Any", 4, 10, 20, 340, 24, 34, 10,
       4, 5, 780, "DF", "Winter", 4, "Everyday"),
    _r("Chocolate muffins", "Snack", "American", 12, 15, 22, 280, 4.5, 38,
       12, 1.6, 22, 220, "V", "Any", 5, "Baking"),
    _r("Banana bread", "Snack", "American", 8, 15, 55, 260, 4, 42, 8, 1.8,
       20, 200, "V", "Any", 4, "Baking"),
    _r("Rice pudding", "Dessert", "British", 4, 5, 35, 290, 9, 46, 7, 0.6,
       22, 120, "VGF", "Winter", 4, "Everyday"),
    _r("Apple crumble", "Dessert", "British", 6, 15, 40, 380, 4, 62, 13,
       3.4, 30, 90, "FV", "Autumn", 5, "Sunday"),
    _r("Pancakes with honey", "Dessert", "American", 4, 10, 12, 420, 11, 58,
       15, 2, 22, 380, "V", "Any", 5, "Family recipe"),
    _r("Fruit salad", "Snack", "Any", 4, 10, 0, 120, 1.4, 30, 0.3, 4, 22,
       5, "FVG", "Summer", 4, "Everyday"),
]

# ---------------------------------------------------------------------------
# Recipe ingredients: recipe, ingredient, quantity, unit, pack size
# ---------------------------------------------------------------------------
def _ri(recipe, ingredient, qty, unit, pack):
    return (recipe, ingredient, qty, unit, pack)


RECIPE_INGREDIENTS: List[tuple] = [
    _ri("Porridge with banana", "Oats", 80, "g", 1000),
    _ri("Porridge with banana", "Milk", 480, "ml", 2000),
    _ri("Porridge with banana", "Banana", 2, "piece", 5),
    _ri("Porridge with banana", "Honey", 2, "tbsp", 340),
    _ri("Scrambled eggs on toast", "Eggs", 6, "piece", 6),
    _ri("Scrambled eggs on toast", "Butter", 20, "g", 250),
    _ri("Scrambled eggs on toast", "Bread", 4, "slice", 20),
    _ri("Overnight oats", "Oats", 100, "g", 1000),
    _ri("Overnight oats", "Greek yoghurt", 200, "g", 500),
    _ri("Overnight oats", "Milk", 200, "ml", 2000),
    _ri("Overnight oats", "Frozen berries", 80, "g", 500),
    _ri("Yoghurt and berries", "Greek yoghurt", 400, "g", 500),
    _ri("Yoghurt and berries", "Frozen berries", 120, "g", 500),
    _ri("Yoghurt and berries", "Honey", 2, "tbsp", 340),
    _ri("Pancakes", "Flour", 200, "g", 1500),
    _ri("Pancakes", "Eggs", 3, "piece", 6),
    _ri("Pancakes", "Milk", 300, "ml", 2000),
    _ri("Pancakes", "Baking powder", 2, "tsp", 100),
    _ri("Pancakes", "Butter", 30, "g", 250),
    _ri("Chicken & veg traybake", "Chicken breast", 600, "g", 500),
    _ri("Chicken & veg traybake", "Potato", 800, "g", 2500),
    _ri("Chicken & veg traybake", "Carrot", 3, "piece", 6),
    _ri("Chicken & veg traybake", "Bell pepper", 2, "piece", 3),
    _ri("Chicken & veg traybake", "Olive oil", 2, "tbsp", 500),
    _ri("Chicken & veg traybake", "Basil", 2, "tsp", 20),
    _ri("Spaghetti bolognese", "Beef mince", 500, "g", 500),
    _ri("Spaghetti bolognese", "Spaghetti", 400, "g", 500),
    _ri("Spaghetti bolognese", "Tinned tomatoes", 2, "can", 400),
    _ri("Spaghetti bolognese", "Onion", 1, "piece", 3),
    _ri("Spaghetti bolognese", "Garlic", 2, "clove", 6),
    _ri("Spaghetti bolognese", "Tomato puree", 2, "tbsp", 200),
    _ri("Spaghetti bolognese", "Cheddar cheese", 60, "g", 350),
    _ri("Vegetable curry", "Tinned chickpeas", 2, "can", 400),
    _ri("Vegetable curry", "Coconut milk", 1, "can", 400),
    _ri("Vegetable curry", "Tinned tomatoes", 1, "can", 400),
    _ri("Vegetable curry", "Onion", 1, "piece", 3),
    _ri("Vegetable curry", "Spinach", 150, "g", 200),
    _ri("Vegetable curry", "Curry paste", 3, "tbsp", 200),
    _ri("Vegetable curry", "Rice", 300, "g", 1000),
    _ri("Chicken curry", "Chicken thigh", 800, "g", 1000),
    _ri("Chicken curry", "Coconut milk", 1, "can", 400),
    _ri("Chicken curry", "Onion", 2, "piece", 3),
    _ri("Chicken curry", "Curry paste", 4, "tbsp", 200),
    _ri("Chicken curry", "Rice", 300, "g", 1000),
    _ri("Salmon & rice", "Salmon fillet", 480, "g", 240),
    _ri("Salmon & rice", "Rice", 300, "g", 1000),
    _ri("Salmon & rice", "Broccoli", 2, "piece", 1),
    _ri("Salmon & rice", "Lemon", 1, "piece", 3),
    _ri("Beef chilli", "Beef mince", 500, "g", 500),
    _ri("Beef chilli", "Tinned kidney beans", 2, "can", 400),
    _ri("Beef chilli", "Tinned tomatoes", 2, "can", 400),
    _ri("Beef chilli", "Bell pepper", 2, "piece", 3),
    _ri("Beef chilli", "Onion", 1, "piece", 3),
    _ri("Beef chilli", "Chilli flakes", 1, "tsp", 40),
    _ri("Beef chilli", "Rice", 300, "g", 1000),
    _ri("Pizza night", "Flour", 300, "g", 1500),
    _ri("Pizza night", "Tinned tomatoes", 1, "can", 400),
    _ri("Pizza night", "Cheddar cheese", 150, "g", 350),
    _ri("Pizza night", "Bell pepper", 1, "piece", 3),
    _ri("Pizza night", "Mushrooms", 150, "g", 250),
    _ri("Pasta primavera", "Pasta", 400, "g", 500),
    _ri("Pasta primavera", "Courgette", 2, "piece", 2),
    _ri("Pasta primavera", "Cherry tomatoes", 250, "g", 300),
    _ri("Pasta primavera", "Cream cheese", 150, "g", 300),
    _ri("Pasta primavera", "Basil", 2, "tsp", 20),
    _ri("Fish finger sandwich", "Cod fillet", 400, "g", 300),
    _ri("Fish finger sandwich", "Bread", 8, "slice", 20),
    _ri("Fish finger sandwich", "Lettuce", 1, "piece", 1),
    _ri("Jacket potato & beans", "Potato", 1000, "g", 2500),
    _ri("Jacket potato & beans", "Tinned kidney beans", 1, "can", 400),
    _ri("Jacket potato & beans", "Cheddar cheese", 80, "g", 350),
    _ri("Chicken Caesar salad", "Chicken breast", 500, "g", 500),
    _ri("Chicken Caesar salad", "Lettuce", 2, "piece", 1),
    _ri("Chicken Caesar salad", "Bread", 4, "slice", 20),
    _ri("Chicken Caesar salad", "Cheddar cheese", 50, "g", 350),
    _ri("Tomato soup & bread", "Tinned tomatoes", 3, "can", 400),
    _ri("Tomato soup & bread", "Onion", 1, "piece", 3),
    _ri("Tomato soup & bread", "Garlic", 2, "clove", 6),
    _ri("Tomato soup & bread", "Bread", 8, "slice", 20),
    _ri("Pasta salad", "Pasta", 350, "g", 500),
    _ri("Pasta salad", "Tinned sweetcorn", 1, "can", 340),
    _ri("Pasta salad", "Cherry tomatoes", 200, "g", 300),
    _ri("Pasta salad", "Cucumber", 1, "piece", 1),
    _ri("Omelette & salad", "Eggs", 6, "piece", 6),
    _ri("Omelette & salad", "Cheddar cheese", 60, "g", 350),
    _ri("Omelette & salad", "Spinach", 80, "g", 200),
    _ri("Beef stew & dumplings", "Beef stewing steak", 800, "g", 700),
    _ri("Beef stew & dumplings", "Potato", 600, "g", 2500),
    _ri("Beef stew & dumplings", "Carrot", 4, "piece", 6),
    _ri("Beef stew & dumplings", "Onion", 2, "piece", 3),
    _ri("Beef stew & dumplings", "Flour", 200, "g", 1500),
    _ri("Stir fry noodles", "Chicken breast", 500, "g", 500),
    _ri("Stir fry noodles", "Pasta", 300, "g", 500),
    _ri("Stir fry noodles", "Soy sauce", 3, "tbsp", 250),
    _ri("Stir fry noodles", "Bell pepper", 2, "piece", 3),
    _ri("Stir fry noodles", "Mushrooms", 200, "g", 250),
    _ri("Tuna pasta bake", "Pasta", 400, "g", 500),
    _ri("Tuna pasta bake", "Tinned sweetcorn", 1, "can", 340),
    _ri("Tuna pasta bake", "Cheddar cheese", 120, "g", 350),
    _ri("Tuna pasta bake", "Tinned tomatoes", 2, "can", 400),
    _ri("Chicken fajitas", "Chicken breast", 600, "g", 500),
    _ri("Chicken fajitas", "Bread rolls", 6, "piece", 6),
    _ri("Chicken fajitas", "Bell pepper", 3, "piece", 3),
    _ri("Chicken fajitas", "Onion", 2, "piece", 3),
    _ri("Shepherd's pie", "Beef mince", 600, "g", 500),
    _ri("Shepherd's pie", "Potato", 1200, "g", 2500),
    _ri("Shepherd's pie", "Carrot", 3, "piece", 6),
    _ri("Shepherd's pie", "Tinned tomatoes", 1, "can", 400),
    _ri("Vegetable lasagne", "Pasta", 300, "g", 500),
    _ri("Vegetable lasagne", "Courgette", 2, "piece", 2),
    _ri("Vegetable lasagne", "Tinned tomatoes", 2, "can", 400),
    _ri("Vegetable lasagne", "Cheddar cheese", 150, "g", 350),
    _ri("Vegetable lasagne", "Spinach", 200, "g", 200),
    _ri("Pork sausages & mash", "Pork sausage", 800, "g", 400),
    _ri("Pork sausages & mash", "Potato", 1000, "g", 2500),
    _ri("Pork sausages & mash", "Butter", 30, "g", 250),
    _ri("Pork sausages & mash", "Frozen peas", 300, "g", 900),
    _ri("Fish pie", "Cod fillet", 600, "g", 300),
    _ri("Fish pie", "Potato", 1000, "g", 2500),
    _ri("Fish pie", "Milk", 400, "ml", 2000),
    _ri("Fish pie", "Butter", 40, "g", 250),
    _ri("Chicken fried rice", "Chicken breast", 500, "g", 500),
    _ri("Chicken fried rice", "Rice", 300, "g", 1000),
    _ri("Chicken fried rice", "Eggs", 3, "piece", 6),
    _ri("Chicken fried rice", "Frozen peas", 200, "g", 900),
    _ri("Chicken fried rice", "Soy sauce", 2, "tbsp", 250),
    _ri("Bolognese pasta bake", "Beef mince", 500, "g", 500),
    _ri("Bolognese pasta bake", "Pasta", 400, "g", 500),
    _ri("Bolognese pasta bake", "Tinned tomatoes", 2, "can", 400),
    _ri("Bolognese pasta bake", "Cheddar cheese", 120, "g", 350),
    _ri("Lentil soup", "Tinned kidney beans", 1, "can", 400),
    _ri("Lentil soup", "Tinned tomatoes", 2, "can", 400),
    _ri("Lentil soup", "Carrot", 3, "piece", 6),
    _ri("Lentil soup", "Celery", 2, "stalk", 4),
    _ri("Lentil soup", "Stock cube", 2, "cube", 12),
    _ri("Cheese & tomato toastie", "Bread", 4, "slice", 20),
    _ri("Cheese & tomato toastie", "Cheddar cheese", 100, "g", 350),
    _ri("Cheese & tomato toastie", "Butter", 20, "g", 250),
    _ri("Chicken noodle soup", "Chicken breast", 400, "g", 500),
    _ri("Chicken noodle soup", "Pasta", 150, "g", 500),
    _ri("Chicken noodle soup", "Stock cube", 2, "cube", 12),
    _ri("Chicken noodle soup", "Carrot", 2, "piece", 6),
    _ri("Fruit salad", "Apple", 2, "piece", 4),
    _ri("Fruit salad", "Banana", 2, "piece", 5),
    _ri("Fruit salad", "Frozen berries", 100, "g", 500),
    _ri("Chocolate muffins", "Flour", 250, "g", 1500),
    _ri("Chocolate muffins", "Sugar", 150, "g", 1000),
    _ri("Chocolate muffins", "Eggs", 2, "piece", 6),
    _ri("Chocolate muffins", "Butter", 80, "g", 250),
    _ri("Chocolate muffins", "Milk", 150, "ml", 2000),
    _ri("Banana bread", "Flour", 250, "g", 1500),
    _ri("Banana bread", "Banana", 3, "piece", 5),
    _ri("Banana bread", "Sugar", 100, "g", 1000),
    _ri("Banana bread", "Butter", 60, "g", 250),
    _ri("Banana bread", "Eggs", 2, "piece", 6),
    _ri("Rice pudding", "Rice", 120, "g", 1000),
    _ri("Rice pudding", "Milk", 800, "ml", 2000),
    _ri("Rice pudding", "Sugar", 40, "g", 1000),
    _ri("Apple crumble", "Apple", 6, "piece", 4),
    _ri("Apple crumble", "Flour", 200, "g", 1500),
    _ri("Apple crumble", "Butter", 100, "g", 250),
    _ri("Apple crumble", "Sugar", 80, "g", 1000),
    _ri("Apple crumble", "Oats", 60, "g", 1000),
    _ri("Pancakes with honey", "Flour", 200, "g", 1500),
    _ri("Pancakes with honey", "Eggs", 3, "piece", 6),
    _ri("Pancakes with honey", "Milk", 300, "ml", 2000),
    _ri("Pancakes with honey", "Honey", 3, "tbsp", 340),
]


def _flags(text: str) -> Dict[str, str]:
    """'VG' -> vegetarian + vegan, 'GFDK' -> gluten/dairy/kid flags."""
    return {
        "favourite": "Yes" if "F" in text else "No",
        "vegetarian": "Yes" if "V" in text else "No",
        "vegan": "Yes" if "G" in text and "V" in text else "No",
        "gluten_free": "Yes" if "G" in text else "No",
        "dairy_free": "Yes" if "D" in text else "No",
        "nut_free": "Yes" if "N" in text else "No",
        "kid_friendly": "Yes" if "K" in text else "No",
        "batch_friendly": "Yes",
        "freezer_friendly": "Yes",
        "seasonal": "Any",
        "added_on": None,
    }


def build_samples(cfg: Config) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Every example record, keyed by sheet name then row offset."""
    out: Dict[str, Dict[int, Dict[str, Any]]] = {}

    # ---- Lists ------------------------------------------------------------
    from .sheets import lists as lists_mod
    list_columns = {
        "meal_slot": lists_mod.MEAL_SLOTS,
        "unit": lists_mod.UNITS,
        "category": lists_mod.CATEGORIES,
        "cuisine": lists_mod.CUISINES,
        "tag": lists_mod.TAGS,
        "store": lists_mod.STORES,
        "diet": lists_mod.DIETS,
        "status": lists_mod.STATUS,
        "yes_no": lists_mod.YES_NO,
        "recipe_category": lists_mod.RECIPE_CATEGORIES,
    }
    out["Lists"] = {}
    for i in range(40):
        out["Lists"][i] = {
            key: (values[i] if i < len(values) else None)
            for key, values in list_columns.items()}

    # ---- Household --------------------------------------------------------
    members = [
        ("Maya", "Adult", 38, "None", "None", "Mushrooms", 1.0, "Yes",
         "Main cook"),
        ("Dan", "Adult", 41, "None", "Peanuts", "Olives", 1.05, "Yes",
         "Grill duty"),
        ("Ivy", "Child", 8, "None", "None", "Anything spicy", 0.6, "Yes",
         "Packed lunch"),
        ("Theo", "Child", 5, "None", "None", "Fish", 0.5, "No", ""),
    ]
    out["Household"] = {
        i: {"member": m[0], "role": m[1], "age": m[2], "diet": m[3],
            "allergies": m[4], "dislikes": m[5], "servings": m[6],
            "packed_lunch": m[7], "notes": m[8]}
        for i, m in enumerate(members)}

    # ---- Recipes ----------------------------------------------------------
    out["Recipes"] = {}
    for i, r in enumerate(RECIPES):
        (name, cat, cui, srv, prep, cook, kcal, pro, carb, fat, fib, sug,
         sod, flags, season, rating, source) = r
        record = {
            "recipe": name, "category": cat, "cuisine": cui,
            "servings": srv, "prep_time": prep, "cook_time": cook,
            "calories": kcal, "protein": pro, "carbs": carb, "fat": fat,
            "fibre": fib, "sugar": sug, "sodium": sod,
            "seasonal": season, "rating": rating, "source": source,
            "tags": "Quick" if prep + cook <= 30 else "Batch",
            "notes": "Batch cook on Sunday and freeze in portions."
                     if "Batch" in flags else "",
        }
        record.update(_flags(flags))
        out["Recipes"][i] = record

    # ---- Recipe Ingredients ------------------------------------------------
    out["Recipe Ingredients"] = {
        i: {"recipe": r[0], "ingredient": r[1], "quantity": r[2],
            "unit": r[3], "pack_size": r[4], "waste_factor": 0.05,
            "organic": "No"}
        for i, r in enumerate(RECIPE_INGREDIENTS)}

    # ---- Ingredients ------------------------------------------------------
    out["Ingredients"] = {}
    for i, ing in enumerate(INGREDIENTS):
        (name, cat, unit, price, pack, kcal, pro, carb, fat, fib, shelf,
         storage, staple, allergens) = ing
        out["Ingredients"][i] = {
            "ingredient": name, "category": cat, "unit": unit,
            "price": price, "pack_size": pack,
            "calories_per_unit": kcal, "protein_per_unit": pro,
            "carbs_per_unit": carb, "fat_per_unit": fat,
            "fibre_per_unit": fib, "shelf_life_days": shelf,
            "storage": storage, "staple": staple, "organic": "No",
            "seasonal": "Any", "allergens": allergens,
            "notes": "",
        }

    # ---- Meal Plan --------------------------------------------------------
    start = cfg.start_date
    plan: List[Dict[str, Any]] = []

    def add(date_offset: int, slot: str, recipe: str, servings: int,
            status: str = "Planned", rating: float = 0.0, cooked: str = "No"):
        plan.append({
            "plan_id": f"W{date_offset // 7 + 1}-D{date_offset % 7 + 1}",
            "date": start + dt.timedelta(days=date_offset),
            "slot": slot, "recipe": recipe, "servings": servings,
            "status": status, "cooked": cooked, "rating": rating,
            "notes": ""})

    weekly = [
        (0, "Porridge with banana", "Pasta salad", "Chicken & veg traybake",
         "Fruit salad"),
        (1, "Scrambled eggs on toast", "Tomato soup & bread",
         "Spaghetti bolognese", "Banana bread"),
        (2, "Overnight oats", "Chicken Caesar salad", "Vegetable curry",
         "Yoghurt and berries"),
        (3, "Porridge with banana", "Cheese & tomato toastie",
         "Salmon & rice", "Chocolate muffins"),
        (4, "Scrambled eggs on toast", "Omelette & salad", "Pizza night",
         "Fruit salad"),
        (5, "Pancakes", "Jacket potato & beans", "Beef chilli",
         "Apple crumble"),
        (6, "Yoghurt and berries", "Lentil soup", "Beef stew & dumplings",
         "Rice pudding"),
        (7, "Porridge with banana", "Pasta salad", "Chicken curry",
         "Fruit salad"),
        (8, "Scrambled eggs on toast", "Tomato soup & bread",
         "Stir fry noodles", "Banana bread"),
        (9, "Overnight oats", "Chicken Caesar salad", "Tuna pasta bake",
         "Yoghurt and berries"),
        (10, "Porridge with banana", "Cheese & tomato toastie",
         "Chicken fajitas", "Chocolate muffins"),
        (11, "Scrambled eggs on toast", "Omelette & salad",
         "Pasta primavera", "Fruit salad"),
        (12, "Pancakes with honey", "Jacket potato & beans",
         "Shepherd's pie", "Apple crumble"),
        (13, "Yoghurt and berries", "Lentil soup", "Fish pie",
         "Rice pudding"),
        (14, "Porridge with banana", "Pasta salad",
         "Chicken fried rice", "Fruit salad"),
        (15, "Scrambled eggs on toast", "Tomato soup & bread",
         "Vegetable lasagne", "Banana bread"),
        (16, "Overnight oats", "Chicken Caesar salad",
         "Bolognese pasta bake", "Yoghurt and berries"),
        (17, "Porridge with banana", "Cheese & tomato toastie",
         "Pork sausages & mash", "Chocolate muffins"),
        (18, "Scrambled eggs on toast", "Omelette & salad", "Pizza night",
         "Fruit salad"),
        (19, "Pancakes", "Jacket potato & beans", "Beef chilli",
         "Apple crumble"),
        (20, "Yoghurt and berries", "Lentil soup",
         "Chicken & veg traybake", "Rice pudding"),
    ]
    for offset, breakfast, lunch, dinner, snack in weekly:
        add(offset, "Breakfast", breakfast, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.5 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Lunch", lunch, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.0 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Dinner", dinner, 4,
            status="Cooked" if offset < 14 else "Planned",
            rating=4.5 if offset < 14 else 0.0,
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Evening snack", snack, 4,
            status="Eaten" if offset < 14 else "Planned",
            cooked="Yes" if offset < 14 else "No")
        add(offset, "Afternoon snack", "Fruit salad", 4,
            status="Eaten" if offset < 14 else "Planned",
            cooked="Yes" if offset < 14 else "No")
    # a takeaway and an eating out day
    add(5, "Dinner", "Pizza night", 0, status="Takeaway")
    add(12, "Lunch", "Fish finger sandwich", 0, status="Eating out")
    out["Meal Plan"] = {i: rec for i, rec in enumerate(plan)}

    # ---- Grocery List -----------------------------------------------------
    groceries = [
        ("Chicken breast", 600, "g", "Greenfield Market", "Meat & Fish"),
        ("Beef mince", 1100, "g", "Greenfield Market", "Meat & Fish"),
        ("Beef stewing steak", 800, "g", "Butcher", "Meat & Fish"),
        ("Salmon fillet", 480, "g", "Greenfield Market", "Meat & Fish"),
        ("Cod fillet", 1000, "g", "Greenfield Market", "Meat & Fish"),
        ("Pork sausage", 800, "g", "Butcher", "Meat & Fish"),
        ("Eggs", 18, "piece", "Greenfield Market", "Dairy & Eggs"),
        ("Milk", 4000, "ml", "Greenfield Market", "Dairy & Eggs"),
        ("Cheddar cheese", 920, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Butter", 330, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Greek yoghurt", 1100, "g", "Greenfield Market", "Dairy & Eggs"),
        ("Cream cheese", 150, "g", "Corner Grocer", "Dairy & Eggs"),
        ("Rice", 1500, "g", "Bulk Barn", "Grains & Pasta"),
        ("Pasta", 1450, "g", "Bulk Barn", "Grains & Pasta"),
        ("Spaghetti", 400, "g", "Bulk Barn", "Grains & Pasta"),
        ("Oats", 240, "g", "Bulk Barn", "Grains & Pasta"),
        ("Bread", 60, "slice", "Corner Grocer", "Bakery"),
        ("Bread rolls", 6, "piece", "Corner Grocer", "Bakery"),
        ("Flour", 1400, "g", "Bulk Barn", "Baking"),
        ("Sugar", 370, "g", "Bulk Barn", "Baking"),
        ("Olive oil", 2, "tbsp", "Greenfield Market", "Condiments"),
        ("Soy sauce", 5, "tbsp", "Asian Supermarket", "Condiments"),
        ("Tinned tomatoes", 14, "can", "Bulk Barn", "Tins & Jars"),
        ("Tomato puree", 2, "tbsp", "Greenfield Market", "Tins & Jars"),
        ("Coconut milk", 2, "can", "Asian Supermarket", "Tins & Jars"),
        ("Tinned chickpeas", 2, "can", "Bulk Barn", "Tins & Jars"),
        ("Tinned kidney beans", 4, "can", "Bulk Barn", "Tins & Jars"),
        ("Tinned sweetcorn", 1, "can", "Bulk Barn", "Tins & Jars"),
        ("Onion", 12, "piece", "Greenfield Market", "Vegetables"),
        ("Garlic", 12, "clove", "Greenfield Market", "Vegetables"),
        ("Carrot", 17, "piece", "Farmers Market", "Vegetables"),
        ("Celery", 2, "stalk", "Greenfield Market", "Vegetables"),
        ("Bell pepper", 10, "piece", "Farmers Market", "Vegetables"),
        ("Broccoli", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Courgette", 4, "piece", "Farmers Market", "Vegetables"),
        ("Spinach", 630, "g", "Greenfield Market", "Vegetables"),
        ("Mushrooms", 350, "g", "Greenfield Market", "Vegetables"),
        ("Sweet potato", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Potato", 6600, "g", "Farmers Market", "Vegetables"),
        ("Cherry tomatoes", 650, "g", "Farmers Market", "Vegetables"),
        ("Cucumber", 2, "piece", "Greenfield Market", "Vegetables"),
        ("Lettuce", 5, "piece", "Greenfield Market", "Vegetables"),
        ("Lemon", 2, "piece", "Greenfield Market", "Fruit"),
        ("Banana", 14, "piece", "Greenfield Market", "Fruit"),
        ("Apple", 10, "piece", "Farmers Market", "Fruit"),
        ("Frozen berries", 400, "g", "Greenfield Market", "Frozen"),
        ("Frozen peas", 500, "g", "Greenfield Market", "Frozen"),
        ("Curry paste", 7, "tbsp", "Asian Supermarket", "Condiments"),
        ("Stock cube", 6, "cube", "Greenfield Market", "Condiments"),
        ("Basil", 4, "tsp", "Greenfield Market", "Herbs & Spices"),
        ("Coriander", 1, "sprig", "Farmers Market", "Herbs & Spices"),
        ("Baking powder", 4, "tsp", "Bulk Barn", "Baking"),
        ("Honey", 7, "tbsp", "Greenfield Market", "Condiments"),
        ("Kitchen roll", 2, "roll", "Greenfield Market", "Household"),
    ]
    out["Grocery List"] = {
        i: {"item": g[0], "quantity": g[1], "unit": g[2], "store": g[3],
            "aisle": g[4], "buy": "Yes", "bought": "No",
            "week_start": start}
        for i, g in enumerate(groceries)}

    # ---- Pantry -----------------------------------------------------------
    pantry = [
        ("Rice", 1200, "g", "Pantry", 40),
        ("Pasta", 900, "g", "Pantry", 60),
        ("Flour", 1600, "g", "Pantry", 90),
        ("Sugar", 800, "g", "Pantry", 120),
        ("Oats", 900, "g", "Pantry", 70),
        ("Olive oil", 1, "tbsp", "Cupboard", 200),
        ("Tinned tomatoes", 4, "can", "Pantry", 300),
        ("Tinned chickpeas", 1, "can", "Pantry", 280),
        ("Coconut milk", 1, "can", "Pantry", 240),
        ("Stock cube", 8, "cube", "Pantry", 180),
        ("Soy sauce", 1, "tbsp", "Cupboard", 150),
        ("Honey", 1, "tbsp", "Cupboard", 260),
        ("Peanut butter", 1, "tbsp", "Cupboard", 120),
        ("Eggs", 5, "piece", "Fridge", 14),
        ("Milk", 1500, "ml", "Fridge", 4),
        ("Butter", 180, "g", "Fridge", 30),
        ("Cheddar cheese", 320, "g", "Fridge", 12),
        ("Greek yoghurt", 300, "g", "Fridge", 5),
        ("Carrot", 4, "piece", "Fridge", 12),
        ("Bell pepper", 2, "piece", "Fridge", 6),
        ("Broccoli", 1, "piece", "Fridge", 4),
        ("Spinach", 120, "g", "Fridge", 3),
        ("Cherry tomatoes", 200, "g", "Fridge", 5),
        ("Lettuce", 1, "piece", "Fridge", 3),
        ("Lemon", 2, "piece", "Fridge", 10),
        ("Apple", 4, "piece", "Fridge", 20),
        ("Banana", 3, "piece", "Cupboard", 3),
        ("Frozen peas", 600, "g", "Freezer", 90),
        ("Frozen berries", 300, "g", "Freezer", 120),
        ("Chicken breast", 250, "g", "Fridge", 1),
    ]
    out["Pantry"] = {
        i: {"item": p[0], "quantity": p[1], "unit": p[2], "storage": p[3],
            "purchase_date": start - dt.timedelta(days=p[4] // 2),
            "opened_date": None, "store": "Greenfield Market",
            "price_paid": 0.0, "frozen": "No", "servings_left": 2,
            "notes": ""}
        for i, p in enumerate(pantry)}

    # ---- Staples ----------------------------------------------------------
    staples = [
        ("Milk", "ml", 2000, 2, "Greenfield Market", 2.60, "Yes"),
        ("Bread", "slice", 20, 2, "Corner Grocer", 1.80, "Yes"),
        ("Eggs", "piece", 12, 7, "Greenfield Market", 5.04, "Yes"),
        ("Banana", "piece", 5, 4, "Greenfield Market", 0.95, "Yes"),
        ("Potato", "g", 2500, 7, "Farmers Market", 3.50, "Yes"),
        ("Onion", "piece", 3, 10, "Greenfield Market", 0.84, "Yes"),
        ("Rice", "g", 1000, 21, "Bulk Barn", 2.10, "No"),
        ("Cheddar cheese", "g", 350, 10, "Greenfield Market", 4.17, "Yes"),
        ("Kitchen roll", "roll", 2, 21, "Greenfield Market", 4.98, "Yes"),
        ("Washing up liquid", "bottle", 1, 28, "Greenfield Market", 1.79,
         "Yes"),
    ]
    out["Staples"] = {
        i: {"staple": s[0], "usual_unit": s[1], "usual_qty": s[2],
            "buy_interval_days": s[3], "store": s[4],
            "last_bought": start - dt.timedelta(days=s[3] - 1),
            "auto_add": s[6], "qty_to_add": s[2]}
        for i, s in enumerate(staples)}

    # ---- Leftovers --------------------------------------------------------
    leftovers = [
        ("LO-01", "Vegetable curry portions", "Vegetable curry", 3, "Fridge",
         2),
        ("LO-02", "Bolognese portions", "Spaghetti bolognese", 4, "Freezer",
         6),
        ("LO-03", "Shepherd's pie portions", "Shepherd's pie", 2, "Fridge",
         1),
        ("LO-04", "Rice pudding", "Rice pudding", 4, "Fridge", 2),
        ("LO-05", "Chilli portions", "Beef chilli", 3, "Freezer", 8),
        ("LO-06", "Soup portions", "Lentil soup", 2, "Fridge", 3),
        ("LO-07", "Lasagne portions", "Vegetable lasagne", 4, "Freezer",
         10),
    ]
    out["Leftovers"] = {
        i: {"leftover_id": l[0], "item": l[1], "recipe": l[2],
            "cooked_date": start - dt.timedelta(days=l[5]),
            "portions": l[3], "storage": l[4], "portions_left": l[3],
            "used_up": "No", "thrown": "No", "container": "Tupperware",
            "reheats": 1, "notes": ""}
        for i, l in enumerate(leftovers)}

    # ---- Food Waste -------------------------------------------------------
    waste = [
        ("W-01", 2, "Spinach", 80, "g", "Spoiled", "No", "Fridge"),
        ("W-02", 5, "Bread", 4, "slice", "Mouldy", "No", "Cupboard"),
        ("W-03", 8, "Lettuce", 1, "piece", "Expired", "No", "Fridge"),
        ("W-04", 11, "Greek yoghurt", 150, "g", "Expired", "No", "Fridge"),
        ("W-05", 13, "Rice", 200, "g", "Cooked too much", "No", "Fridge"),
        ("W-06", 15, "Mushrooms", 120, "g", "Spoiled", "No", "Fridge"),
        ("W-07", 18, "Banana", 2, "piece", "Bought too much", "No",
         "Cupboard"),
        ("W-08", 19, "Apple", 1, "piece", "Child refused", "No", "Fridge"),
        ("W-09", 20, "Milk", 300, "ml", "Expired", "No", "Fridge"),
        ("W-10", 21, "Broccoli", 1, "piece", "Spoiled", "No", "Fridge"),
    ]
    out["Food Waste"] = {
        i: {"waste_id": w[0], "date": start - dt.timedelta(days=w[1]),
            "item": w[2], "qty": w[3], "unit": w[4], "reason": w[5],
            "avoidable": w[6], "storage_at_waste": w[7],
            "store": "Greenfield Market", "portion": "1 portion",
            "notes": ""}
        for i, w in enumerate(waste)}

    # ---- Meal Prep --------------------------------------------------------
    prep = [
        ("P-01", "Sunday", "Cook the bolognese base", "Spaghetti bolognese",
         8, 40, 1, "Oven"),
        ("P-02", "Sunday", "Roast the chicken for the week",
         "Chicken & veg traybake", 8, 40, 2, "Oven"),
        ("P-03", "Sunday", "Make the curry sauce", "Vegetable curry", 8, 25,
         3, "Hob"),
        ("P-04", "Sunday", "Portion the rice pudding", "Rice pudding", 4, 10,
         4, "No cooking"),
        ("P-05", "Wednesday", "Chop the stir fry vegetables",
         "Stir fry noodles", 4, 15, 1, "No cooking"),
        ("P-06", "Friday", "Make the pizza dough", "Pizza night", 4, 20, 1,
         "Oven"),
        ("P-07", "Saturday", "Bake the muffins", "Chocolate muffins", 12, 25,
         2, "Oven"),
        ("P-08", "Sunday", "Prepare packed lunch boxes", "Pasta salad", 4,
         15, 5, "No cooking"),
    ]
    out["Meal Prep"] = {
        i: {"task_id": p[0], "prep_day": p[1], "task": p[2], "recipe": p[3],
            "servings": p[4], "duration_min": p[5], "order": p[6],
            "equipment": p[7], "assigned_to": "Maya", "batch_qty": p[4],
            "portions": p[4], "linked_slot": "Dinner", "completed": "No",
            "status": "To do", "notes": ""}
        for i, p in enumerate(prep)}

    # ---- Dietary Filters --------------------------------------------------
    filters = [
        ("DF-01", "Dan", "Peanuts", "Nut allergy", "Avoid"),
        ("DF-02", "Theo", "Cod fillet", "Does not like fish", "Preference"),
        ("DF-03", "Ivy", "Chilli flakes", "Too spicy", "Preference"),
        ("DF-04", "", "Prawns", "Shellfish allergy in the family", "Avoid"),
        ("DF-05", "", "Gluten", "Dan is gluten sensitive", "Caution"),
    ]
    out["Dietary Filters"] = {
        i: {"filter_id": d[0], "member": d[1], "exclude": d[2],
            "reason": d[3], "severity": d[4], "active": "Yes", "notes": ""}
        for i, d in enumerate(filters)}

    # ---- Nutrition --------------------------------------------------------
    nutrition = []
    for day in range(21):
        date = start + dt.timedelta(days=day)
        for slot, recipe in (("Breakfast", weekly[day][1]),
                             ("Lunch", weekly[day][2]),
                             ("Dinner", weekly[day][3]),
                             ("Evening snack", weekly[day][4])):
            nutrition.append({
                "date": date, "slot": slot, "recipe": recipe,
                "servings": 1, "water_glasses": 6, "notes": ""})
    out["Nutrition"] = {i: rec for i, rec in enumerate(nutrition)}

    # ---- Budget -----------------------------------------------------------
    months = []
    today = cfg.today
    for back in range(5, -1, -1):
        first = dt.date(today.year, today.month, 1)
        for _ in range(back):
            first = dt.date(first.year - (first.month == 1),
                            (first.month - 2) % 12 + 1, 1)
        months.append(first.strftime("%b %Y"))
    budget_actual = [742.5, 698.2, 815.4, 764.9, 690.3, 812.7]
    out["Budget"] = {
        i: {"month": months[i], "actual_eating_out": budget_actual[i] / 10,
            "notes": ""}
        for i in range(6)}

    # ---- Recipe Costs -----------------------------------------------------
    out["Recipe Costs"] = {
        i: {"recipe": r[0], "notes": ""}
        for i, r in enumerate(RECIPES)}

    # ---- Converter --------------------------------------------------------
    conversions = [
        ("g", "kg", 0.001, "Weight", "500 g = 0.5 kg"),
        ("kg", "g", 1000, "Weight", "1 kg = 1000 g"),
        ("g", "oz", 0.0353, "Weight", "100 g = 3.5 oz"),
        ("oz", "g", 28.35, "Weight", "1 oz = 28 g"),
        ("lb", "g", 453.6, "Weight", "1 lb = 454 g"),
        ("ml", "l", 0.001, "Volume", "500 ml = 0.5 l"),
        ("l", "ml", 1000, "Volume", "1 l = 1000 ml"),
        ("ml", "fl oz", 0.0338, "Volume", "100 ml = 3.4 fl oz"),
        ("fl oz", "ml", 29.57, "Volume", "1 fl oz = 30 ml"),
        ("tsp", "ml", 5, "Volume", "1 tsp = 5 ml"),
        ("tbsp", "ml", 15, "Volume", "1 tbsp = 15 ml"),
        ("tbsp", "tsp", 3, "Volume", "1 tbsp = 3 tsp"),
        ("cup", "ml", 240, "Volume", "1 cup = 240 ml"),
        ("cup", "g", 125, "Weight", "1 cup of flour = 125 g"),
        ("clove", "tsp", 0.5, "Count", "1 clove of garlic = 0.5 tsp"),
        ("slice", "g", 35, "Weight", "1 slice of bread = 35 g"),
        ("piece", "g", 120, "Weight", "1 medium onion = 120 g"),
        ("can", "ml", 400, "Volume", "1 tin = 400 ml"),
        ("punnet", "g", 300, "Weight", "1 punnet = 300 g"),
        ("bunch", "g", 150, "Weight", "1 bunch of herbs = 150 g"),
    ]
    out["Converter"] = {
        i: {"from_unit": c[0], "to_unit": c[1], "factor": c[2],
            "category": c[3], "example": c[4], "notes": ""}
        for i, c in enumerate(conversions)}

    # ---- Rotation ---------------------------------------------------------
    out["Rotation"] = {
        i: {"recipe": r[0], "notes": ""}
        for i, r in enumerate(RECIPES)}

    # ---- Food Safety ------------------------------------------------------
    from .sheets import food_safety as fs_mod
    out["Food Safety"] = {
        i: {"food": row[0], "category": row[1], "storage": row[2],
            "fridge_days": row[3], "freezer_days": row[4],
            "cooked_days": row[5], "safe_temp": row[6],
            "reheat_temp": row[7], "source": "Food standards guidance",
            "notes": ""}
        for i, row in enumerate(fs_mod.ROWS)}

    # ---- Fridge & Freezer -------------------------------------------------
    fridge = [
        ("FF-01", "Bolognese portions", "Spaghetti bolognese", 4, "Freezer",
         6),
        ("FF-02", "Soup portions", "Lentil soup", 4, "Freezer", 5),
        ("FF-03", "Lasagne portions", "Vegetable lasagne", 4, "Freezer", 9),
        ("FF-04", "Chilli portions", "Beef chilli", 3, "Freezer", 7),
        ("FF-05", "Rice pudding", "Rice pudding", 4, "Fridge", 2),
        ("FF-06", "Stew portions", "Beef stew & dumplings", 3, "Fridge", 1),
        ("FF-07", "Curry portions", "Chicken curry", 4, "Freezer", 4),
    ]
    out["Fridge & Freezer"] = {
        i: {"batch_id": fr[0], "item": fr[1], "recipe": fr[2],
            "portions": fr[3], "storage": fr[4],
            "cooked_date": start - dt.timedelta(days=fr[5]),
            "container": "Tupperware", "reheats": 1, "eaten": "No",
            "notes": ""}
        for i, fr in enumerate(fridge)}

    # ---- Grocery Spending ------------------------------------------------
    spending = []
    shops = [
        (21, "Greenfield Market", [("Chicken breast", 500, "g", 4.95),
                                   ("Milk", 2000, "ml", 2.60),
                                   ("Eggs", 12, "piece", 5.04),
                                   ("Bread", 20, "slice", 1.80),
                                   ("Cheddar cheese", 350, "g", 4.17),
                                   ("Butter", 250, "g", 2.48)]),
        (18, "Bulk Barn", [("Rice", 1000, "g", 2.10),
                           ("Pasta", 500, "g", 0.95),
                           ("Flour", 1500, "g", 1.65),
                           ("Oats", 1000, "g", 1.90),
                           ("Tinned tomatoes", 4, "can", 2.20),
                           ("Sugar", 1000, "g", 1.20)]),
        (14, "Greenfield Market", [("Beef mince", 500, "g", 5.95),
                                   ("Carrot", 6, "piece", 0.72),
                                   ("Onion", 3, "piece", 0.84),
                                   ("Spinach", 200, "g", 1.38),
                                   ("Frozen peas", 900, "g", 2.61)]),
        (11, "Farmers Market", [("Potato", 2500, "g", 3.50),
                                ("Bell pepper", 3, "piece", 1.95),
                                ("Apple", 4, "piece", 1.40),
                                ("Cherry tomatoes", 300, "g", 2.97)]),
        (7, "Greenfield Market", [("Salmon fillet", 240, "g", 7.18),
                                  ("Broccoli", 1, "piece", 0.79),
                                  ("Lemon", 3, "piece", 1.35),
                                  ("Greek yoghurt", 500, "g", 2.45),
                                  ("Banana", 5, "piece", 0.95)]),
        (4, "Corner Grocer", [("Bread rolls", 6, "piece", 2.10),
                              ("Cream cheese", 300, "g", 2.37),
                              ("Cucumber", 1, "piece", 0.69),
                              ("Lettuce", 1, "piece", 0.99)]),
        (2, "Asian Supermarket", [("Coconut milk", 2, "can", 2.10),
                                  ("Curry paste", 1, "jar", 1.60),
                                  ("Soy sauce", 250, "ml", 1.29)]),
    ]
    receipt = 1
    for days_ago, store, items in shops:
        for item, qty, unit, price in items:
            spending.append({
                "date": start - dt.timedelta(days=days_ago),
                "store": store, "item": item, "qty": qty, "unit": unit,
                "price": round(price / (qty if qty else 1), 4),
                "receipt_no": f"R-{1000 + receipt}", "payment": "Debit card",
                "on_sale": "No", "savings": 0.0, "notes": ""})
        receipt += 1
    out["Grocery Spending"] = {i: rec for i, rec in enumerate(spending)}

    # ---- Store Prices -----------------------------------------------------
    prices = []
    price_rows = [
        ("Chicken breast", "Greenfield Market", 0.0099, 500, "No"),
        ("Chicken breast", "Bulk Barn", 0.0119, 500, "Yes"),
        ("Beef mince", "Greenfield Market", 0.0119, 500, "No"),
        ("Beef mince", "Butcher", 0.0109, 500, "Yes"),
        ("Rice", "Bulk Barn", 0.0021, 1000, "No"),
        ("Rice", "Greenfield Market", 0.0029, 1000, "No"),
        ("Eggs", "Greenfield Market", 0.42, 6, "No"),
        ("Eggs", "Farmers Market", 0.55, 6, "Yes"),
        ("Milk", "Greenfield Market", 0.0013, 2000, "No"),
        ("Milk", "Corner Grocer", 0.0015, 2000, "No"),
        ("Bread", "Corner Grocer", 0.09, 20, "No"),
        ("Bread", "Greenfield Market", 0.11, 20, "No"),
        ("Cheddar cheese", "Greenfield Market", 0.0119, 350, "No"),
        ("Cheddar cheese", "Bulk Barn", 0.0139, 350, "Yes"),
        ("Pasta", "Bulk Barn", 0.0019, 500, "No"),
        ("Pasta", "Greenfield Market", 0.0026, 500, "No"),
        ("Potato", "Farmers Market", 0.0014, 2500, "No"),
        ("Potato", "Greenfield Market", 0.0019, 2500, "No"),
        ("Tinned tomatoes", "Bulk Barn", 0.55, 400, "No"),
        ("Tinned tomatoes", "Greenfield Market", 0.69, 400, "No"),
    ]
    for i, pr in enumerate(price_rows):
        prices.append({
            "item": pr[0], "store": pr[1], "unit": "g", "price": pr[2],
            "pack_size": pr[3], "date": start - dt.timedelta(days=i % 14),
            "on_sale": pr[4], "usual_price": round(pr[2] * 1.15, 4),
            "notes": ""})
    out["Store Prices"] = {i: rec for i, rec in enumerate(prices)}

    # ---- Stores -----------------------------------------------------------
    stores = [
        ("Greenfield Market", "12 High Street", "555-0101",
         "greenfield.example", "Yes", "No", "Yes", 30.0, 4.99, "Saturday",
         "07:00-22:00", 1.2, "Yes", "Yes", "Yes", "All major cards"),
        ("Corner Grocer", "3 Mill Lane", "555-0102", "", "No", "Yes", "No",
         0.0, 0.0, "n/a", "06:30-19:00", 0.3, "No", "No", "No", "Cash only"),
        ("Bulk Barn", "Unit 4, Trade Park", "555-0103", "bulkbarn.example",
         "No", "Yes", "Yes", 25.0, 0.0, "Wednesday", "08:00-18:00", 4.5,
         "Yes", "Yes", "Yes", "All major cards"),
        ("Farmers Market", "Town square", "", "", "No", "No", "No", 0.0, 0.0,
         "Saturday", "08:00-13:00", 1.0, "Yes", "No", "No", "Cash and cards"),
        ("Asian Supermarket", "88 Dock Road", "555-0105",
         "asiansuper.example", "No", "No", "Yes", 0.0, 0.0, "n/a",
         "09:00-20:00", 3.1, "No", "No", "No", "Cash and cards"),
    ]
    out["Stores"] = {
        i: {"store": s[0], "address": s[1], "phone": s[2], "website": s[3],
            "loyalty": "Greencard" if i == 0 else "", "delivery": s[4],
            "pickup": s[5], "min_order": s[7], "delivery_fee": s[8],
            "delivery_day": s[9], "opening_hours": s[10],
            "distance_km": s[11], "parking": s[12], "organic_range": s[13],
            "bulk_bins": s[14], "cards": s[15],
            "best_for": "Weekly shop" if i == 0 else "Top ups",
            "rating": 5 if i == 0 else 4, "notes": ""}
        for i, s in enumerate(stores)}

    # ---- Events -----------------------------------------------------------
    events = [
        ("Ivy's birthday party", start + dt.timedelta(days=24), 12, "Dinner",
         "Maya", "Home", 90.0, "Pizza night", "", "", "", "Pancakes",
         "Juice and water", 1.0, "Planning"),
        ("Sunday roast for Dan's parents", start + dt.timedelta(days=6), 6,
         "Dinner", "Dan", "Home", 70.0, "Beef stew & dumplings", "", "", "",
         "Apple crumble", "Wine and water", 1.0, "Planning"),
        ("Picnic at the park", start + dt.timedelta(days=35), 5, "Picnic",
         "Maya", "Riverside park", 40.0, "Pasta salad", "", "", "",
         "Fruit salad", "Lemonade", 1.0, "Planning"),
    ]
    out["Events"] = {
        i: {"event": e[0], "date": e[1], "guests": e[2], "meal_type": e[3],
            "host": e[4], "location": e[5], "budget": e[6], "menu_1": e[7],
            "menu_2": e[8], "menu_3": e[9], "menu_4": e[10], "dessert": e[11],
            "drinks": e[12], "servings": e[13], "status": e[14],
            "dietary_notes": "Two nut allergies, one gluten free",
            "leftover_plan": "Send portions home with the guests",
            "notes": ""}
        for i, e in enumerate(events)}

    # ---- Goals ------------------------------------------------------------
    goals = [
        ("Bin less than 5% of the food we buy", "Waste", 5, 4.2, "% of spend",
         120),
        ("Keep the weekly shop under budget", "Budget", 180, 168,
         "currency", 60),
        ("Cook at home 18 times a week", "Cooking", 18, 16, "meals a week",
         90),
        ("Try two new recipes a month", "Variety", 2, 3, "recipes a month",
         30),
        ("Hit 30 g of fibre a day", "Nutrition", 30, 24, "grams a day", 60),
        ("Five packed lunches a week", "Health", 5, 4, "lunches a week", 45),
    ]
    out["Goals"] = {
        i: {"goal": g[0], "category": g[1], "target": g[2], "current": g[3],
            "unit": g[4],
            "deadline": cfg.today + dt.timedelta(days=g[5]),
            "streak": 6 - i, "best_streak": 12 - i, "notes": ""}
        for i, g in enumerate(goals)}

    # ---- Sustainability ---------------------------------------------------
    sus = []
    for back in range(5, -1, -1):
        first = dt.date(today.year, today.month, 1)
        for _ in range(back):
            first = dt.date(first.year - (first.month == 1),
                            (first.month - 2) % 12 + 1, 1)
        sus.append({"month": first.strftime("%b %Y"), "local_shops": 4,
                    "bulk_buys": 3, "packaging_free": 2, "own_grown": 0.5,
                    "notes": ""})
    out["Sustainability"] = {i: rec for i, rec in enumerate(sus)}

    return out
