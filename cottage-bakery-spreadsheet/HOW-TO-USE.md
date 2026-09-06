# How to Use the Cottage Bakery v4 Spreadsheet

A step-by-step guide for running your cottage bakery with this workbook. It ships
pre-filled with **realistic American demo data** ("Rose & Rye Cottage Bakery") so you
can see every formula working before you replace the numbers with your own.

---

## 1. The two files

| File | Use |
|------|-----|
| `Cottage_Bakery_v4_ENHANCED.xlsx` | Fully editable — play with it, then fill in your real numbers |
| `Cottage_Bakery_v4_ENHANCED_LOCKED.xlsx` | Same workbook, but **formula cells are protected**. Unlock password: **`premium`** |

**Color code (both files):**
- 🟨 **Yellow cells** = editable inputs (type your own values)
- ⬜ White cells = locked formulas / labels (they calculate automatically)

---

## 2. Quick start (10 minutes)

1. Open `Cottage_Bakery_v4_ENHANCED.xlsx`.
2. Go to **Instructions + Setup** and edit the yellow cells **B18–B30** (name, tax
   rate, labor rate, packaging, etc.).
3. Go to **Ingredients + Stock** and replace the demo ingredients with yours
   (name, unit, package size, package cost, stock level).
4. Go to **Recipe Library** and put your own recipes in the long-format ingredient
   list (rows 65+). Costs fill in automatically.
5. Go to **Product List** and set each product's selling price.
6. Log sales in **Orders**, expenses in **Bookkeeping**.
7. Check **Dashboard** daily — profit, stock status, and break-even progress.

---

## 3. Tab-by-tab guide

### 📘 Instructions + Setup
The home tab. Yellow cells B18–B30 are the master settings used across the workbook:

| Cell | Setting | Where it's used |
|------|---------|-----------------|
| B18 | Bakery name | Dashboard / branding |
| B21 | Sales tax % | Pricing reference |
| B22 | Hourly labor rate | Recipe Calculator labor cost |
| B23 | Overhead % | Recipe Calculator (manual — or copy the auto value from `Overhead Expenses!B28`) |
| B24 | Waste % | Recipe Calculator (failed batches) |
| B25 | Packaging default $/unit | Recipe Calculator |
| B29 | Monthly working hours | Overhead tab (hourly rate) |
| B30 | Expected monthly orders | Overhead tab (per-order rate) |

### 🧾 Ingredients + Stock
Every ingredient you buy. For each one fill in: **Unit** (how you buy/stock it),
**Pkg Size**, **Pkg Cost**, **Current Stock**, **Min Alert**.
- `Cost/Unit`, `Stock Value`, and `Status` are formulas — don't type over them.
- `Status` turns **red (OUT)**, **orange (LOW)**, or **green (OK)** automatically.
- Keep unit = grams (g) or ml where possible so recipes convert cleanly.

### 🔁 Unit Conversion (reference only)
A lookup table the workbook uses. No need to edit it. Key idea:

```
Converted qty = Recipe qty × (recipe-unit factor ÷ stock-unit factor)
```

Example: 2 tsp vanilla with ml stock → `2 × 4.92892 ÷ 1 = 9.86 ml`.
**Weight vs volume don't convert automatically** — if a recipe mixes g and cups, the
sheet flags "Check W/V". Weigh it once (1 cup flour ≈ 120–150 g) and enter grams.

### 📖 Recipe Library (unlimited recipe storage)
- Rows 5–54: one line per recipe (name, yield, labor, packaging, overhead/waste %).
- Rows 65+: the **long-format ingredient database** — one row per ingredient per
  recipe. Fill **Recipe ID, Ingredient Name, Qty, Unit**; the cost, conversion, and
  "Type Match" columns calculate themselves.
- The recipe line's `Total Ingredient Cost` uses a `SUMIF` over this database, so it
  works for **any number of recipes**.

### 🧮 Recipe Calculator (3 recipes side by side, full detail)
For costing one recipe in depth. Enter ingredient names (must match
`Ingredients + Stock` exactly), qty, and unit. Labor, packaging, overhead, and waste
roll into **Total Batch Cost** and **Cost/Unit**, with suggested prices below
(2x / 2.5x / 3x / 65%-margin).

### 🏷️ Product List
Your sellable items. Set **Selling Price** (column I) per product. `Cost/Unit` pulls
from the Recipe Library, and `Profit/Unit` + `Margin %` calculate automatically.
`Units Sold` is summed from the Orders tab.

### 🏢 Overhead Expenses
Your fixed monthly costs (rent, utilities, insurance, licenses…). The bottom section
turns them into **hourly**, **per-order**, and **% of revenue** rates. This is the
"true" overhead number to paste into Setup B23 if you want auto overhead.

### 🚀 Startup Costs
One-time money spent to launch (mixer, oven, permits, branding). It calculates:
- Total investment
- **Months to break even** = investment ÷ average monthly profit
- A 24-month break-even table and chart

### 📊 Dashboard
Read-only KPIs: revenue/expenses/profit YTD, overhead, break-even months, active
recipe count, total stock value.

### 🛒 Orders · 💰 Bookkeeping · 🎪 Markets & Events · 👥 Customers
Operational logging: sales, income/expenses, market ROI, and a customer database.
Everything here feeds the Dashboard and Product List.

---

## 4. Daily / weekly rhythm

- **Daily:** log orders (Orders) → update stock used (Ingredients + Stock).
- **Weekly:** check `Status` for LOW/OUT, and place supplier orders.
- **Monthly:** update Bookkeeping expenses + Overhead tab; review break-even.
- **Before each market:** cost a recipe in the Calculator and sanity-check price.

---

## 5. How pricing is calculated

```
Total ingredient cost   = Σ (converted qty × cost per stock unit)
Labor cost              = hours × hourly rate
Packaging               = per-unit × batch yield
Overhead $              = ingredient cost × overhead %
Waste $                 = (ingred + labor + packaging + overhead) × waste %
Total batch cost        = sum of the above + other
Cost per unit           = total batch cost ÷ batch yield
Suggested price         = cost per unit × multiplier (or ÷ (1 − margin))
```

---

## 6. Locked file (password: `premium`)

- Formulas are locked so you can't accidentally break them.
- Yellow input cells stay editable.
- To unlock a sheet: right-click the tab → **Unprotect Sheet** → enter `premium`.

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| `#VALUE!` in a date/calc | Dates must be real dates; type them as `mm/dd/yyyy`, not text |
| `Check W/V` on an ingredient line | You mixed weight (g) and volume (ml) — enter a weight in grams |
| Ingredient cost shows 0 | The ingredient name must match `Ingredients + Stock` **exactly** |
| `#REF!` after deleting rows | Don't delete rows inside tables — clear cells instead |
| Overhead % looks too high/low | Update Setup B23, or copy `Overhead Expenses!B28` into it |

---

## 8. Regenerating the file

Run the builder (requires Python + openpyxl):

```bash
pip install openpyxl
python3 build_cottage_bakery.py
```

It writes both `.xlsx` files next to the script.
