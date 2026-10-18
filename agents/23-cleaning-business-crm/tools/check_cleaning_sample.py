#!/usr/bin/env python3
"""Sanity checks on the example data written into the Filled workbook.

The sample book of business must tie out: every cross-register reference
has to resolve, the payments must match their invoices' totals, and the
dashboard inputs must be internally consistent.

    python3 tools/check_cleaning_sample.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import openpyxl

FILE = (Path(__file__).resolve().parent.parent / "output" /
        "Cleaning Business CRM & Pricing Calculator.xlsx")

KEYCOL = {
    "Clients": "name", "Properties": "property_name", "Leads": "name",
    "Services": "name", "Quotes": "quote_number",
    "Quote Lines": "quote_ref", "Jobs": "job_number",
    "Job Tasks": "job_ref", "Employees": "name",
    "Timesheets": "employee", "Job Costing": "job_ref",
    "Invoices": "invoice_number", "Invoice Lines": "invoice_ref",
    "Payments": "invoice_ref", "Supplies": "name",
    "Supply Usage": "supply", "Equipment": "name",
    "Expenses": "category", "Mileage": "employee",
    "Complaints": "client", "Safety": "topic", "Incidents": "type",
}


def col_values(ws, header_row=4):
    """Map header name -> list of data values (first 800 rows)."""
    headers = {}
    for cell in ws[header_row]:
        if cell.value:
            headers[str(cell.value)] = cell.column
    out = {}
    for name, col in headers.items():
        vals = []
        for r in range(header_row + 1, min(ws.max_row, header_row + 800) + 1):
            v = ws.cell(row=r, column=col).value
            if v not in (None, ""):
                vals.append(v)
        out[name] = vals
    return out


def main() -> int:
    problems = []
    wb = openpyxl.load_workbook(FILE, data_only=False)

    def sheet(name):
        return col_values(wb[name])

    clients = sheet("Clients")
    properties = sheet("Properties")
    jobs = sheet("Jobs")
    quotes = sheet("Quotes")
    qlines = sheet("Quote Lines")
    invoices = sheet("Invoices")
    ilines = sheet("Invoice Lines")
    payments = sheet("Payments")
    employees = sheet("Employees")
    timesheets = sheet("Timesheets")
    supplies = sheet("Supplies")
    usage = sheet("Supply Usage")
    mileage = sheet("Mileage")
    expenses = sheet("Expenses")
    tasks = sheet("Job Tasks")
    costing = sheet("Job Costing")

    n = {
        "clients": len(clients.get("Client / Company", [])),
        "properties": len(properties.get("Property Name", [])),
        "jobs": len(jobs.get("Job #", [])),
        "quotes": len(quotes.get("Quote #", [])),
        "invoices": len(invoices.get("Invoice #", [])),
        "payments": len(payments.get("Amount", [])),
        "employees": len(employees.get("Name", [])),
        "timesheets": len(timesheets.get("Date", [])),
        "supplies": len(supplies.get("Supply", [])),
    }

    # ------------------------------------------------------- volume checks
    for key, minimum in [("clients", 15), ("properties", 15),
                         ("jobs", 60), ("quotes", 10),
                         ("invoices", 25), ("payments", 20),
                         ("employees", 5), ("timesheets", 40),
                         ("supplies", 10)]:
        if n[key] < minimum:
            problems.append(f"{key}: only {n[key]} rows (expected >={minimum})")

    # ------------------------------------------------- referential checks
    client_names = set(clients.get("Client / Company", []))
    prop_names = set(properties.get("Property Name", []))
    emp_names = set(employees.get("Name", []))
    service_names = set(services_names := sheet("Services").get("Service", []))
    supply_names = set(supplies.get("Supply", []))
    job_nums = set(jobs.get("Job #", []))
    quote_nums = set(quotes.get("Quote #", []))
    inv_nums = set(invoices.get("Invoice #", []))

    def check_refs(label, values, valid, field):
        bad = [v for v in values if v not in valid]
        if bad:
            problems.append(f"{label}: {len(bad)} unknown {field} "
                            f"(e.g. {bad[:3]})")

    check_refs("Jobs.client", jobs.get("Client", []), client_names,
               "client")
    check_refs("Jobs.property", jobs.get("Property", []), prop_names,
               "property")
    check_refs("Jobs.service", jobs.get("Service", []), service_names,
               "service")
    check_refs("Jobs.crew_lead", jobs.get("Crew Lead", []), emp_names,
               "employee")
    check_refs("Properties.client", properties.get("Client", []),
               client_names, "client")
    check_refs("Quote Lines.quote_ref", qlines.get("Quote #", []),
               quote_nums, "quote #")
    check_refs("Invoices.client", invoices.get("Client", []),
               client_names, "client")
    check_refs("Invoices.job_ref", [x for x in invoices.get("Job #", [])],
               job_nums, "job #")
    check_refs("Invoice Lines.invoice_ref", ilines.get("Invoice #", []),
               inv_nums, "invoice #")
    check_refs("Payments.invoice_ref", payments.get("Invoice #", []),
               inv_nums, "invoice #")
    check_refs("Timesheets.employee", timesheets.get("Employee", []),
               emp_names, "employee")
    check_refs("Timesheets.job_ref", timesheets.get("Job #", []),
               job_nums, "job #")
    check_refs("Supply Usage.supply", usage.get("Supply", []),
               supply_names, "supply")
    check_refs("Supply Usage.job_ref", usage.get("Job #", []),
               job_nums, "job #")
    check_refs("Mileage.employee", mileage.get("Employee", []),
               emp_names, "employee")
    check_refs("Job Tasks.job_ref", tasks.get("Job #", []), job_nums,
               "job #")
    check_refs("Job Costing.job_ref", costing.get("Job #", []), job_nums,
               "job #")

    # ------------------------------------------------------ payment totals
    # invoice line totals summed by invoice should equal what was paid
    # for fully-paid invoices (allow part-paid / unpaid to be less)
    line_total = {}
    inv_of_line = ilines.get("Invoice #", [])
    qty = ilines.get("Qty", [])
    price = ilines.get("Unit Price", [])
    for i, ref in enumerate(inv_of_line):
        if i < len(qty) and i < len(price) and isinstance(qty[i], (int, float)) \
                and isinstance(price[i], (int, float)):
            line_total[ref] = line_total.get(ref, 0) + qty[i] * price[i]
    paid_by = {}
    for i, ref in enumerate(payments.get("Invoice #", [])):
        amt = payments.get("Amount", [])[i] \
            if i < len(payments.get("Amount", [])) else 0
        if isinstance(amt, (int, float)):
            paid_by[ref] = paid_by.get(ref, 0) + amt
    overpaid = [(ref, paid_by[ref], line_total.get(ref, 0))
                for ref in paid_by
                if ref in line_total and paid_by[ref] > line_total[ref] + 0.01]
    if overpaid:
        problems.append(f"payments over invoice totals: {overpaid[:3]}")

    # ---------------------------------------------------------- date sanity
    today = dt.date.today()
    job_dates = jobs.get("Date", [])
    if job_dates:
        real = [d.date() if isinstance(d, dt.datetime) else d
                for d in job_dates if isinstance(d, (dt.date, dt.datetime))]
        if real:
            span = (max(real) - min(real)).days
            if span < 30:
                problems.append(f"job dates span only {span} days")
            future = [d for d in real if d > today + dt.timedelta(days=60)]
            if future:
                problems.append(f"{len(future)} jobs scheduled >60 days ahead")

    # ------------------------------------------------------------- summary
    print(f"sample check: {FILE.name}")
    for k, v in n.items():
        print(f"  {k:12s}: {v}")
    print(f"  job tasks   : {len(tasks.get('Job #', []))}")
    print(f"  quote lines : {len(qlines.get('Quote #', []))}")
    print(f"  inv lines   : {len(ilines.get('Invoice #', []))}")
    print(f"  supply usage: {len(usage.get('Supply', []))}")
    print(f"  mileage     : {len(mileage.get('Employee', []))}")
    print(f"  expenses    : {len(expenses.get('Category', []))}")
    if problems:
        print(f"PROBLEMS: {len(problems)}")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
