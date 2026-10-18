"""Workbook assembly.

Order of operations:

1. create the workbook and the format book;
2. register every register-sheet spec (Clients, Jobs, Invoices, ...);
3. write each register in tab order (raw registers first so lookups
   resolve, then the pages that read from them);
4. hand the workbook to the page builders (Start Here, Settings,
   Dashboard, Quote Calculator, schedulers, printables, ...);
5. define the named ranges, set the document properties and close.

Everything is Excel-2010 safe: classic functions only, no dynamic arrays,
no XLOOKUP / IFS / LET / MINIFS / MAXIFS.  Sheets are protected with the
password "premium"; input cells are unlocked.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import xlsxwriter

from .config import Config
from .formats import FormatBook
from .layout import Registry, SheetSpec
from .names import apply_defined_names
from .writer import SheetWriter

# Sheets built from declarative specs, in tab order.
REGISTER_MODULES: List[str] = [
    "clients", "properties", "leads", "services", "quotes", "quote_lines",
    "jobs", "job_tasks", "checklists", "employees", "timesheets",
    "job_costing", "invoices", "invoice_lines", "payments", "supplies",
    "supply_usage", "equipment", "expenses", "mileage", "complaints",
    "safety", "incidents",
]

# Sheets built by hand, in tab order.
PAGE_BUILDERS: List[str] = [
    "start_here", "settings", "dashboard", "quote_calculator", "calendar",
    "staff_schedule", "client_retention", "financial_plan", "reports",
    "print_quote", "print_invoice", "print_job_sheet", "lists", "help",
]

SHEET_ORDER: List[str] = [
    "Start Here", "Settings", "Dashboard", "Quote Calculator",
    "Clients", "Properties", "Leads", "Services", "Quotes", "Quote Lines",
    "Jobs", "Job Tasks", "Calendar", "Checklists", "Employees",
    "Staff Schedule", "Timesheets", "Job Costing", "Invoices",
    "Invoice Lines", "Payments", "Supplies", "Supply Usage", "Equipment",
    "Expenses", "Mileage", "Client Retention", "Complaints", "Incidents",
    "Safety", "Financial Plan", "Reports", "Print Quote", "Print Invoice",
    "Print Job Sheet", "Lists", "Help",
]


def build_workbook(output_path: str,
                   config: Optional[Config] = None) -> str:
    """Build one workbook and return the path written to."""
    import os

    from . import sheets as sheets_pkg
    from . import sample_data as sd

    cfg = config or Config()
    sd.build(cfg)          # generate the demo book (dates relative to today)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    workbook = xlsxwriter.Workbook(
        output_path,
        {"strings_to_numbers": False, "nan_inf_to_errors": True})
    workbook.set_properties({
        "title": cfg.product_name,
        "subject": cfg.product_subtitle,
        "author": cfg.author,
        "manager": cfg.author,
        "company": cfg.author,
        "category": "Spreadsheet template",
        "keywords": ("cleaning business, cleaning service, CRM, quote "
                     "calculator, job scheduler, invoice, expenses"),
        "comments": (f"{cfg.product_name} v{cfg.version} by {cfg.author}"),
    })

    fmts = FormatBook(workbook, cfg)
    reg = Registry()
    writer = SheetWriter(workbook, fmts, reg, cfg)

    # 1. register the specs (creation order is the tab order)
    specs: Dict[str, SheetSpec] = {}
    for mod_name in REGISTER_MODULES:
        mod = getattr(sheets_pkg, mod_name)
        spec = mod.build_register(cfg, fmts)
        reg.add(spec)
        specs[spec.name] = spec

    # 2. raw registers
    written = set()
    for name in SHEET_ORDER:
        if name in specs:
            writer.write_spec(specs[name])
            written.add(name)

    # 3. page builders get (workbook, fmts, reg, cfg) and create their sheet
    for mod_name in PAGE_BUILDERS:
        mod = getattr(sheets_pkg, mod_name)
        mod.build_page(workbook, fmts, reg, cfg)

    # 4. names + close (put the tabs in the canonical order first)
    apply_defined_names(workbook, reg, cfg)
    order = {name: i for i, name in enumerate(SHEET_ORDER)}
    workbook.worksheets_objs.sort(key=lambda ws: order.get(ws.name, 999))
    workbook.close()
    return output_path
