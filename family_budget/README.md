# 🏠 Novality Premium Family Budget

By **Novality Store**

A complete, premium household financial dashboard in a single `.xlsx` workbook — built for
American families. Every number is **automatic**; you only enter data **once** and the
Dashboard, Budget, Analytics, Calendar and charts update themselves.

> 📦 Download the finished file: **`Novality_Family_Budget_Premium.xlsx`**
> 🔑 All formula cells are **locked & password-protected** (password: `premium`).
> Input cells (cream) stay editable.

---

## Tabs included

| # | Tab | What it does |
|---|-----|--------------|
| 1 | 🏠 Dashboard | Income, spending, surplus, savings rate, net worth, debt, cash, emergency fund, budget vs actual, YTD, goal progress, red/yellow/green alerts, + charts |
| 2 | 💰 Income | Multiple earners, gross → federal/state/FICA/401k/HSA → **net take-home**, pay frequency |
| 3 | 💳 Transactions | Master ledger: date, type, category, subcategory, merchant, amount, account, method, family member, recurring, essential/discretionary, notes |
| 4 | 📋 Budget | Full budget by category/subcategory, automatic actuals & variance, over-budget turns red |
| 5 | 🧾 Bills & Subs | Recurring bills, annual cost, autopay, due-date calendar |
| 6 | 🏦 Accounts | Checking, savings, HYSA, cash, credit cards, 401k/403b/IRA/Roth, brokerage, 529, HSA, CD |
| 7 | 💸 Debt Manager | Snowball & avalanche ranking, payoff date, interest saved |
| 8 | 🎯 Goals & Funds | Unlimited goals + sinking funds, % complete, per-paycheck amount |
| 9 | 📈 Savings & Invest | Auto current balances, contributions, employer match, goal progress |
| 10 | 🏡 Home & Mortgage | Home value, equity, monthly cost + 360-row amortization schedule |
| 11 | 🚗 Vehicles | True cost per vehicle & per mile + cost-per-mile |
| 12 | 👨‍👩‍👧‍👦 Family & Kids | Kids/care spend + spending by family member |
| 13 | 🏥 Healthcare | Health spend + all insurance premiums |
| 14 | 🇺🇸 Tax Center | Filing status, federal/state/FICA, 401k/HSA, **estimate** of refund/owed (labeled ESTIMATE) |
| 15 | 📊 Analytics | YTD summary, category breakdown, monthly trend, needs vs wants, per-person, quick answers |
| 16 | 📅 Calendar | Bills, paydays, debt minimums & subscriptions by day |
| 17 | ⚙️ Settings | Family members, accounts, categories, dropdown lists, report period |
| 18 | 📖 Instructions | How to use + protection info |

---

## How to use

1. **⚙️ Settings** — set your family members, accounts, categories, pay schedules, etc. once.
2. **💰 Income** — add each paycheck (gross, withholdings, 401k/HSA). Net take-home is automatic.
3. **💳 Transactions** — log every purchase/income once. Month / Year / Day and category totals are automatic.
4. **🧾 Bills & Subs** — list recurring bills; annual cost and the calendar fill in automatically.
5. Read the **🏠 Dashboard** and **📊 Analytics** — no manual totals needed.

## Protection

- **Password:** `premium`
- Unprotect any sheet via *Review → Unprotect Sheet*.
- Only the **cream** cells are editable; green formula cells are locked to keep your budget from breaking.

## Regenerating the workbook

```bash
cd family_budget
pip install openpyxl
python3 build_budget.py     # writes Novality_Family_Budget_Premium.xlsx
```

## Notes

- Sample data is pre-loaded so you can see everything working — delete it and add your own.
- Tax-center figures are **estimates** and should be refreshed when tax law changes.
- Built for Excel **and** Google Sheets (import the `.xlsx` directly).
