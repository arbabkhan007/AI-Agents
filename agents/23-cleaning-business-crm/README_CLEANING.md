# Cleaning Business CRM & Pricing Calculator

A complete back office for a cleaning business in one Excel workbook:
client CRM, property register, quote calculator, job scheduler, crew
planning, timesheets, job costing, invoicing, payments, stock, expenses,
mileage, retention, safety, a financial plan, reports and printable
client documents.

Built by **Novality Store**.

## What you get

| Deliverable | What it is |
|---|---|
| `output/Cleaning Business CRM & Pricing Calculator.xlsx` | Filled with a worked example (Bright & Tidy Cleaning Co.) - 25 clients, 149 jobs, 64 invoices, everything tied out |
| `output/Cleaning Business CRM & Pricing Calculator (Blank).xlsx` | The same workbook, every register empty |
| `download/cleaning-business-crm.zip` | The two workbooks + how-to-run note (the customer download) |
| `download/cleaning-business-crm-source.zip` | The complete generator source (rebuild it yourself) |
| `SOURCE_CODE_CLEANING.md` | All source files in one Markdown document |

**37 tabs. 111,000+ formulas. Excel 2010 safe.**

## The tabs

Start Here · Settings · Dashboard · Quote Calculator · Clients ·
Properties · Leads · Services · Quotes · Quote Lines · Jobs · Job Tasks ·
Calendar · Checklists · Employees · Staff Schedule · Timesheets ·
Job Costing · Invoices · Invoice Lines · Payments · Supplies ·
Supply Usage · Equipment · Expenses · Mileage · Client Retention ·
Complaints · Incidents · Safety · Financial Plan · Reports ·
Print Quote · Print Invoice · Print Job Sheet · Lists · Help

## Rebuild it

```bash
python3 build_cleaning_workbook.py            # filled, with example data
python3 build_cleaning_workbook.py --blank    # empty registers
```

Useful flags (see `--help` for all of them):

```bash
python3 build_cleaning_workbook.py \
    --business "My Clean Co" --owner "Your Name" \
    --currency "£" --currency-code GBP \
    --rate 38 --pay 16 --minimum 80 --tax 20 \
    --units "sq m" --distance km \
    --year 2027 --rows 800
```

## Validate it

```bash
python3 tools/validate_cleaning_workbook.py    # formula syntax + structure
python3 tools/check_cleaning_sample.py         # the example book ties out
python3 tools/find_circular_refs.py "output/Cleaning Business CRM & Pricing Calculator.xlsx"
```

The validator enforces the lessons learned the hard way:

* every formula's parentheses and quotes are balanced (Excel silently
  *deletes* unbalanced formulas and shows a repair log);
* no `==` formula heads, no unreplaced template tokens, no `#REF!`;
* no modern functions (no XLOOKUP / IFS / LET / MINIFS / dynamic arrays);
* every sheet protected; the input cells unlocked;
* document creator is Novality Store.

## How it works

* `cleaning_business_spreadsheet/` - the generator package
  (`build.py` assembles the workbook from declarative sheet specs).
* `cleaning_business_spreadsheet/sheets/` - one module per tab.
* `cleaning_business_spreadsheet/sample_data.py` - the demo book of
  business, generated relative to "today" so the dashboard is always
  alive.
* `tools/` - validation, packaging and export scripts.

Column references in formulas are rendered from templates
(`[[Jobs.client]]`, `{name}{r}`), so columns can be rearranged without
breaking a single formula.

## Protection

Every sheet is protected with the password **`premium`**. White cells
are unlocked and are yours to type in; pale teal cells are locked
formulas. Review > Unprotect Sheet to restructure.

## License

Sold as a digital product by Novality Store. Rebuild, re-brand and
resell the output workbooks; keep the generator source to yourself.
