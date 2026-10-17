# How to use the Meal Planner & Grocery List

A step-by-step guide to setting the workbook up and getting it to run
itself. Set aside about 45 minutes for the first week - after that the
weekly routine is about 15 minutes.

## Before you start

- Open `Meal Planner & Grocery List.xlsx`. Every sheet is protected: you
  can type in the yellow input cells, everything else is calculated.
- The password to unprotect any sheet is `premium`.
- The workbook comes filled with sample data so you can see how each tab
  works. To start clean, select the data rows on each yellow-tabbed table
  and press Delete - the formulas stay where they are.

## Week one: the setup (about 45 minutes)

### 1. Settings (5 minutes)

Set the numbers that everything else follows:

- **Household name and size** - who you are feeding.
- **Weekly food budget** and **eating out budget** - what you want to
  spend.
- **Planning year** - the year the Budget tab covers.
- **Prep day and shopping day** - the two days that shape your week.
- **Calorie target and macro targets** - per person, per day. The
  Nutrition tab uses these.
- **Rotation gap** - how many days before the same meal is allowed back
  in the plan.
- **Leftover fridge days and freezer review days** - how long batch
  cooking keeps.
- **Expiry warning days** - when the pantry should start shouting.
- **Waste reduction target** - what percentage of the food budget you are
  willing to bin.

### 2. Household (2 minutes)

One row per person who eats with you, with an age band, an activity level
and anything they will not eat. This drives the dietary checks on the Meal
Plan tab.

### 3. Dietary Filters (3 minutes)

One row per thing to avoid: the ingredient name, who it applies to and how
serious it is. The reach columns show how much of the recipe book it
touches.

### 4. Recipes and Recipe Ingredients (20 minutes)

Add the five to ten recipes you cook most:

- On **Recipes**, one row per recipe: name, category, cuisine, servings,
  times, the method and rough nutrition per serving.
- On **Recipe Ingredients**, one row per ingredient per recipe: the
  ingredient name, quantity, unit and preparation.

Then add the ingredients those recipes use to the **Ingredients** tab with
a price, a unit and a shelf life in days.

> **The golden rule: ingredient names must match exactly.** If 'Chicken
> breast' is spelled one way on the Ingredients tab and another way on
> Recipe Ingredients, the price cannot be found. Pick one spelling and
> stick to it.

### 5. Staples (5 minutes)

Add the things you buy every week - bread, milk, eggs, coffee - with how
often you buy them. Anything due, or out of stock in the pantry, is
flagged so it never gets forgotten.

### 6. Stores (5 minutes)

One row per shop: whether they deliver, what they are best for and how far
away they are. The spend columns fill themselves in from the Grocery
Spending tab.

## The weekly routine (about 15 minutes)

### 1. Plan the week (10 minutes)

On **Meal Plan**, add one row per meal: the date, the slot (breakfast,
lunch, dinner or snack) and the recipe. Set the servings if you are
cooking more or fewer portions than the recipe makes.

Everything else fills itself in: the nutrition, the cost, how the meal
compares with the rest of the day, whether it is too soon after the last
time you had it and whether it trips a dietary filter. The **Weekly
Planner** and **Print Week** tabs lay the same week out day by day.

> Tip: plan around what is already in the house. The **Pantry** tab shows
> what is about to expire, and the Dashboard's "Use it or lose it" tile
> shows the most urgent six items.

### 2. Shop (3 minutes)

Open **Grocery List**. It already has everything the week needs:

- quantities scaled to your servings
- reduced by what the pantry has
- grouped by aisle, with a price and a running total
- marked with a priority: must-have, nice to have, have it, or skip

Tick the **Bought** column as you shop, and record what you actually spent
on **Grocery Spending**. The **Print Shopping** tab is laid out for one
page by the door.

### 3. Cook and log (2 minutes a day)

- Mark meals as **Cooked** on the Meal Plan tab as you go.
- Anything left over goes on the **Leftovers** tab - the sheet works out
  the use-by date and the order to eat them in.
- Anything you bin goes on **Food Waste**, with the reason and the cost.
  This is the single fastest way to cut a food bill.

### 4. Prep day (optional, 30 minutes)

On **Meal Prep**, list the batch cooking jobs for your prep day: what to
cook, how long it takes and the order to do them in. The batches go on
**Fridge & Freezer** with use-by dates, and the portions go on the
**Leftovers** tab.

## The monthly routine (about 10 minutes)

- **Budget** - add a row for the new month. Planned grocery spend, actual
  grocery spend and the waste cost are calculated for you; type in what
  you spent eating out.
- **Reports** - pick the month and read the ranked tables: favourite
  recipes, most expensive dishes, biggest waste, where the money goes.
- **Rotation** - see which meals are overdue for another turn and which
  are coming round too fast.
- **Goals** - set a habit goal (waste under 5%, 4 home cooked meals a
  week, 2 new recipes a month) and record where you are. The progress bar
  fills up as you go.
- **Sustainability** - waste as a percentage of spend, packaging and local
  shopping, and a green score for the month.

## Tips from people who use it

1. **Plan around the specials.** Check **Store Prices** before you plan;
   the Best buy column shows the cheapest shop for each item.
2. **Cook double.** A second portion costs minutes, not pounds. Plan it as
   a leftover two days later and you get a free meal.
3. **Log the waste for one month.** Most households cut their food waste
   by a quarter just by seeing the number.
4. **Use the left column of the Meal Plan.** The Plan ID column is
   yours - 'W34-D1' (week 34, day 1) is a pattern that keeps things tidy.
5. **Print the week.** The Print Week tab on the fridge door stops the
   "what is for dinner" question before it starts.

## Common questions

**Why can't I change a grey cell?**
It is calculated. The sheet is protected so it cannot be overwritten by
accident. Use Review > Unprotect Sheet with the password `premium` if you
really need to.

**Why does a price not show on the Grocery List?**
An item name does not match the Ingredients tab exactly. Fix the spelling.

**What formulas can I use if I add my own?**
The workbook is built for Excel 2010: SUM, SUMIFS, COUNTIFS, INDEX, MATCH,
IF, IFERROR, TEXT and their friends. Avoid XLOOKUP, FILTER and SORT.

**Can I use it for just me?**
Yes - set Household Size to 1 and everything follows.

**How do I start a new year?**
Copy the workbook file, change the planning year on Settings and add the
new months to the Budget tab. Archive the old Grocery Spending and Food
Waste rows in a separate sheet if you want the history.

## Need more help?

Open the **Help** tab in the workbook - it answers the questions people
ask most, and has a key to the colours. The **Start Here** tab has the map
of all 36 tabs and your first-week checklist.
