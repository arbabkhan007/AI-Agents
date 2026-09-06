# How to Use the Cottage Bakery Spreadsheet

Two files:

- **Cottage_Bakery_v4_ENHANCED.xlsx** — normal file, everything editable.
- **Cottage_Bakery_v4_ENHANCED_LOCKED.xlsx** — formulas are locked. Password: **premium**.

Yellow cells are for typing. White cells calculate on their own.

The file comes with sample data so you can see how it works. Just type over it.

---

## Getting started

1. Open the spreadsheet.
2. Go to the **Instructions + Setup** tab.
3. Fill in the yellow boxes: your bakery name, sales tax, your hourly rate, etc.
4. Go to **Ingredients + Stock** and put in what you buy: unit, package size, package cost, how much you have.
5. Go to **Recipe Library** and list your recipes and their ingredients (rows 65 and below).
6. Go to **Product List** and set the price you sell each item for.
7. Record sales in **Orders** and costs in **Bookkeeping**.
8. Look at **Dashboard** to see how you're doing.

---

## What each tab is for

- **Instructions + Setup** — your basic settings, used everywhere else.
- **Ingredients + Stock** — everything you buy and what it costs per unit. Tells you when you're low or out.
- **Unit Conversion** — reference table for grams, ml, tsp, cups, etc. Leave it alone.
- **Recipe Library** — your recipes. Type ingredients, it adds up the cost.
- **Recipe Calculator** — cost out one recipe in detail, with suggested prices.
- **Product List** — what you sell and your profit per item.
- **Overhead Expenses** — rent, utilities, insurance, etc. Shows your cost per hour and per order.
- **Startup Costs** — money you spent to get going, and how long to earn it back.
- **Dashboard** — profit, stock, break-even at a glance.
- **Orders / Bookkeeping / Markets & Events / Customers** — day-to-day records.

---

## A few things to know

- Ingredient names in recipes must match the Ingredients tab exactly, or the cost will show 0.
- Use grams or ml for ingredients when you can. That way tsp, tbsp, and cup amounts convert by themselves.
- If a recipe mixes grams and cups, it will say "Check W/V". Weigh it once and type grams instead.
- Don't delete rows inside the tables. Clear the cells instead.
- In the locked file, unprotect a sheet with the password **premium**.

---

## How the price is worked out

Ingredient cost + labor + packaging + overhead + waste = batch cost.
Batch cost ÷ batch yield = cost per unit. Add your margin to get the price.

---

## Rebuild the file

```
pip install openpyxl
python3 build_cottage_bakery.py
```

That makes both xlsx files again.
