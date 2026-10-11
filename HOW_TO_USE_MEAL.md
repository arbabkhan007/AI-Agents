# How to use the Automated Meal Planner & Grocery List Spreadsheet

A walkthrough for the person who just bought it. Fifteen minutes to set up,
then five minutes a week to keep it going.

You do not have to fill in every tab. If you never batch cook, leave
**Meal Prep** and **Fridge & Freezer** empty - the planner still works from
**Settings**, **Ingredients**, **Recipes**, **Meal Plan** and **Grocery
List** alone.

---

## 1. The colour code

| What you see | What it means |
| --- | --- |
| Warm cream cells | Type here. These cells are unlocked. |
| Soft sage cells | Calculated by the spreadsheet. Leave them alone. |
| Green bands and headers | Column titles. Hover over one for a note about what goes in it. |
| Terracotta | Totals, targets and anything that needs your attention. |

Every tab is protected so the formulas cannot be typed over by accident.
The cream cells stay editable. If you want to change the look of the whole
workbook, unprotect the sheets from **Review > Unprotect Sheet** (password
`premium`) and protect them again when you are done.

---

## 2. Set up your household (Settings tab, 5 minutes)

Open **Settings** and fill in column B:

| Row | Setting | Why it matters |
| --- | --- | --- |
| 6 | Household name | Shown on every print out. |
| 7 | People in the household | Scales servings, budget per person and the nutrition targets. |
| 8 | Main cook / planner | Just a label. |
| 9 | Planning year | Every weekly and monthly plan is built around this year. |
| 10 | Servings per meal | Default portion count copied into new plan rows. |
| 11 | Week starts on | Monday or Sunday. |
| 12 | Measurement system | Metric (g, ml) or Imperial (oz, fl oz). |
| 13-14 | Currency symbol and code | Used in every money format. |
| 15-16 | Shopping day and meal prep day | Drives the reminders on the Dashboard. |
| 19 | Weekly grocery budget | Compared with the actual spend. |
| 26-33 | Daily nutrition targets | Calories, protein, carbs, fat, fibre, sugar, sodium, water - per person. |
| 36-41 | Reminder windows | How early the pantry flags "use it or lose it", how long leftovers keep, how many days before a meal may repeat. |
| 44-49 | Habit targets | Home cooked meals a week, new recipes a month, takeaway limit, packed lunches, waste target. |

**Do this first.** Everything else reads these cells through named ranges
(`Plan_Year`, `Weekly_Budget`, `Calorie_Target`, `Rotation_Gap_Days` and
about fifty more), so changing a number here re-shapes the whole workbook.

---

## 3. Add your ingredients (Ingredients tab, 10 minutes)

One row per thing you buy. The important columns:

| Column | What to put in it |
| --- | --- |
| Ingredient | The name. **Spell it exactly the same way on every tab** - the cost and nutrition lookups match on the name. |
| Category | Which aisle it lives in. This groups the printed grocery list. |
| Unit | The unit the price and the nutrition are quoted in (g, ml, piece, can...). |
| Price / unit | The price of **one unit**, not of a whole pack. Divide the pack price by the pack size: a 500 g pack of pasta at $0.95 is $0.0019 per g. |
| Pack size | How big the pack you buy is, in the same unit. |
| Calories / Protein / Carbs / Fat / Fibre per unit | Per one unit. The Recipes and Nutrition tabs multiply these by quantity. |
| Shelf life (days) | Used to work out the use-by dates on the Pantry tab. |
| Storage | Pantry, Cupboard, Fridge or Freezer. |
| Staple | Yes = you buy it every week, so it is re-added to the grocery list automatically. |

Start with the 20 things you buy most often. Add the rest as you go.

The right hand half of this tab fills itself in as you use the workbook:
how much is in the pantry, how much is needed this week, how many weeks of
stock you have, what you paid last time and whether the price is going up.

---

## 4. Build your recipe book (Recipes + Recipe Ingredients, 20 minutes)

**Recipes** - one row per recipe: name, category (Breakfast / Lunch /
Dinner / Snack / Dessert...), cuisine, how many it serves, prep and cook
time, the nutrition per serving, the dietary flags, a rating and any notes.
The calculated columns then show the total time, the cost per serving, the
calories per dollar, how many times you have cooked it and when it was last
on the plan.

**Recipe Ingredients** - one row per ingredient per recipe: pick the
recipe, pick the ingredient, put in the quantity and the unit. The price,
the category and the nutrition are looked up from the Ingredients tab, so:

* change a price once and every recipe that uses it re-prices itself;
* the cost per serving on the Recipes tab appears on its own;
* the pantry check tells you whether you already have enough.

This is the engine of the workbook. If a recipe shows a cost of zero, it
has no ingredient rows yet, or one of the ingredient names does not match
the Ingredients tab exactly.

---

## 5. Plan your first week (Weekly Planner or Meal Plan, 5 minutes)

The easiest way is to plan straight onto the **Meal Plan** tab - one row
per meal:

1. **Date** - the day of the meal.
2. **Meal slot** - Breakfast, Lunch, Dinner, a snack.
3. **Recipe** - pick from your recipe book.
4. **Servings** - how many portions to cook. Leave it blank to cook the
   recipe as written.
5. **Status** - Planned, Cooking, Cooked, Eaten, Skipped, Takeaway,
   Eating out.

The row then works out the calories, the protein, the cost, how it compares
with the rest of that day, whether the meal is too soon after the last time
you had it (the rotation gap on Settings) and whether it trips one of the
dietary filters.

**Weekly Planner** is the same information laid out as a seven day grid.
Set the week starting date in **B6** and the grid fills in from the Meal
Plan. **Monthly Planner** does the same for six weeks of a month with a
theme and a budget for each week.

---

## 6. Shop (Grocery List, 2 minutes)

Open **Grocery List**. Everything you planned is already there, grouped by
aisle, with:

* the quantity scaled to your household and reduced by what is already in
  the pantry (the **Still needed** column);
* the pack count - how many packs of the size you actually buy;
* the line total and the running total;
* a **Buy** flag, a **Bought** flag and a **Price paid** column so you can
  compare what you paid with what you expected;
* a priority: *Must have*, *Nice to have*, *Have it*, *Skip*.

Tick items off as you fill the basket. Then print it: **Print Shopping**,
choose the store, print. It comes out as a tidy tick list in buy order.

Record what you actually spent on the **Grocery Spending** tab and the
budget and reports fill themselves in.

---

## 7. Keep the pantry honest (Pantry, 2 minutes a week)

Add what you buy, with the quantity and the date you bought or opened it.
The pantry works out the use-by date from the shelf life on the Ingredients
tab and flags anything inside the "use it or lose it" window. The Dashboard
shows the six most urgent items, ranked.

**Leftovers** and **Fridge & Freezer** do the same for cooked food: log the
batch, say whether it is in the fridge or the freezer, and the queue tells
you what to eat first. **Meal Prep** is the to-do list for your prep day.

---

## 8. Watch the numbers (Dashboard, Budget, Nutrition, Reports)

* **Dashboard** - pick the week in **C6**. Meals planned, calories a day,
  grocery cost, budget left, items to buy, use-it-or-lose-it count, the
  week day by day, the meals most overdue for another turn, the cheapest
  meals in your book, and the habit and budget alerts.
* **Nutrition** - pick a month in **B6**. Daily averages against your
  targets, and a log you can fill in by hand or by naming a recipe.
* **Budget** - planned versus actual, month by month, with the year to date
  position at the top.
* **Reports** - set the from and to dates in **B6** and **D6**. Spend by
  store and by category, waste by reason, the meals you cooked most, the
  ingredients you spend most on.
* **Goals** - set a target and a deadline; the progress bar fills up.
* **Sustainability** - waste, packaging and how local your shopping is.

---

## 9. Print

| Tab | What it prints |
| --- | --- |
| **Print Week** | The weekly meal plan for the fridge door - one page, portrait. |
| **Print Shopping** | The grocery list with tick boxes, in buy order. |
| **Print Recipe** | A recipe card: ingredients with quantities and costs, the timings, the nutrition, your method notes. |

Each print tab has its picker on **row 3**. Everything is set to fit one
page wide on A4 with the headers repeated.

---

## 10. The 36 tabs

| Tab | What it is for |
| --- | --- |
| Start Here | The tour: set up in five steps, the colour key, an index of every tab. |
| Dashboard | The week at a glance. |
| Weekly Planner | One week, day by day. |
| Monthly Planner | Six weeks of a month with themes and budgets. |
| Settings | Household, budget, nutrition targets, reminder windows. |
| Lists | Every drop down source: meal slots, units, aisles, cuisines, tags, stores, diets, statuses. |
| Household | Who you cook for, their diets, allergies and calorie needs. |
| Recipes | Your recipe book with timings, nutrition, cost and rankings. |
| Recipe Ingredients | What goes into each recipe and what it costs. |
| Ingredients | Everything you buy, with price, nutrition, stock and spend. |
| Meal Plan | Every planned meal - the engine of the workbook. |
| Grocery List | The automatic shopping list. |
| Pantry | What you have, what is low, what expires next. |
| Staples | The weekly basics with a buy-by rhythm. |
| Leftovers | Cooked portions and when to eat them. |
| Food Waste | What you binned, why, and what it cost. |
| Meal Prep | Batch cooking tasks in the order to do them. |
| Dietary Filters | Allergies and dietary needs, checked against every recipe. |
| Nutrition | The daily log against your targets. |
| Budget | Planned versus actual food spend, month by month. |
| Recipe Costs | Cost per serving for the whole book, cheapest first. |
| Converter | Unit conversions plus a live calculator. |
| Rotation | How often each meal repeats. |
| Food Safety | How long food keeps, and safe temperatures. |
| Fridge & Freezer | Batch cooked portions and their use-by dates. |
| Grocery Spending | Every shop you record, against the budget. |
| Store Prices | The same item priced at every shop. |
| Stores | Your shops, with spend and best-for notes. |
| Events | Parties and dinner guests, with a menu budget. |
| Goals | Habit goals with a live progress bar. |
| Sustainability | Waste, packaging and local shopping. |
| Reports | Any date range, on one page. |
| Print Week | The printable weekly plan. |
| Print Shopping | The printable grocery list. |
| Print Recipe | The printable recipe card. |
| Help | Questions, answers and troubleshooting. |

---

## 11. When something looks wrong

| Symptom | What to check |
| --- | --- |
| A recipe shows a cost of zero | It has no rows on Recipe Ingredients, or an ingredient name does not match the Ingredients tab exactly. |
| Calories are zero for a planned meal | The recipe has no nutrition entered, or the servings on the plan row are zero. |
| The grocery list is empty | The Meal Plan rows have no date inside the week you are looking at, or the status is set to Skipped. |
| Costs look too high | The price on the Ingredients tab should be the price of one unit, not of a whole pack. |
| A drop down will not let you type | The cell is validated against a list on the Lists tab. Either pick from the list or add your value to that list. |
| `#REF!` errors | A row or column was deleted. Close without saving and reopen the original file. |

---

## 12. Make it yours

| Command | What it does |
| --- | --- |
| `python build_meal_planner_workbook.py --household "The Khans"` | Your household name on the cover of every print out. |
| `python build_meal_planner_workbook.py --currency "£" --currency-code GBP` | Another currency. |
| `python build_meal_planner_workbook.py --units Imperial` | Ounces and fluid ounces. |
| `python build_meal_planner_workbook.py --week-start Sunday` | A Sunday start. |
| `python build_meal_planner_workbook.py --budget 150` | A weekly grocery budget of 150. |
| `python build_meal_planner_workbook.py --rows 400` | More rows of capacity in the big registers. |
| `python build_meal_planner_workbook.py --blank` | An empty workbook with no example data. |

---

*Automated Meal Planner & Grocery List Spreadsheet, by Novality Store.
36 tabs, about 79,000 formulas, every sheet protected with the password
`premium`.*
