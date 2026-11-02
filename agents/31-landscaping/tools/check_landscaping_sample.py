#!/usr/bin/env python3
"""Check the worked example before it is ever written to a workbook.

Four things go wrong with sample data, and all four are silent:

1. a key that is not an input column on that register - the value is
   dropped and the formula it landed on goes with it;
2. a value that is not a member of the drop-down list the column
   validates against - Excel accepts it, then refuses to let the user
   re-pick it;
3. more sample rows than the register has room for;
4. an ID pointing at a record that does not exist, or a narrative
   that does not add up - stock used that was never bought, an
   odometer that goes backwards, an invoice paid for more than it was
   raised for.

    python3 tools/check_landscaping_sample.py
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from landscaping_spreadsheet import build as B           # noqa: E402
from landscaping_spreadsheet import config as C          # noqa: E402
from landscaping_spreadsheet import sample_data as S     # noqa: E402

Problem = Tuple[str, str]

#: a drop-down whose source is one of these names is checked against
#: the matching list in config.py
LIST_SOURCES: Dict[str, List[str]] = {
    "CustomerTypeList": C.CUSTOMER_TYPES,
    "LeadSourceList": C.LEAD_SOURCES,
    "PaymentTermsList": [row[0] for row in C.PAYMENT_TERMS],
    "PaymentMethodList": C.PAYMENT_METHODS,
    "CustomerStatusList": C.CUSTOMER_STATUSES,
    "PropertyTypeList": C.PROPERTY_TYPES,
    "TerrainList": C.TERRAIN_TYPES,
    "AccessList": C.ACCESS_TYPES,
    "PropertyStatusList": C.PROPERTY_STATUSES,
    "ServiceCategoryList": C.SERVICE_CATEGORIES,
    "PricingUnitList": C.PRICING_UNITS,
    "EquipmentCategoryList": C.EQUIPMENT_CATEGORIES,
    "SeasonList": C.SEASONS,
    "FrequencyList": [row[0] for row in C.FREQUENCIES],
    "CrewRoleList": C.CREW_ROLES,
    "ServiceStatusList": C.SERVICE_STATUSES,
    "QuoteStatusList": C.QUOTE_STATUSES,
    "JobStatusList": C.JOB_STATUSES,
    "PriorityList": C.PRIORITIES,
    "WeatherList": C.WEATHER_CONDITIONS,
    "ContractStatusList": C.CONTRACT_STATUSES,
    "WeekdayList": C.WEEKDAYS,
    "EmploymentTypeList": C.EMPLOYMENT_TYPES,
    "CrewStatusList": C.CREW_STATUSES,
    "CrewNameList": C.CREW_NAMES,
    "AbsenceList": C.ABSENCE_REASONS,
    "TaskTypeList": C.TASK_TYPES,
    "EquipmentStatusList": C.EQUIPMENT_STATUSES,
    "EquipmentConditionList": C.EQUIPMENT_CONDITIONS,
    "VehicleList": C.DEFAULT_VEHICLES,
    "VehicleCostList": C.VEHICLE_COST_TYPES,
    "MaterialCategoryList": C.MATERIAL_CATEGORIES,
    "MaterialUnitList": C.MATERIAL_UNITS,
    "MaterialStatusList": C.MATERIAL_STATUSES,
    "InvoiceStatusList": C.INVOICE_STATUSES,
    "ExpenseCategoryList": C.EXPENSE_CATEGORIES,
    "StockMoveList": C.STOCK_MOVES,
    "TaxCategoryList": C.TAX_CATEGORIES,
    "FeedbackSourceList": C.FEEDBACK_SOURCES,
    "FeedbackTypeList": C.FEEDBACK_TYPES,
    "FeedbackStatusList": C.FEEDBACK_STATUSES,
    "FeedbackCauseList": C.FEEDBACK_CAUSES,
    "CurrencyList": [row[0] for row in C.CURRENCIES]
    if C.CURRENCIES and isinstance(C.CURRENCIES[0], tuple)
    else C.CURRENCIES,
}

#: lists built from the sample data itself rather than from config
ID_SOURCES = {
    "CustomerList": ("customers", "CUS-", 4),
    "PropertyList": ("properties", "PRP-", 4),
    "CrewIDList": ("crew", "EMP-", 3),
    "MaterialIDList": ("materials", "MAT-", 4),
    "EquipmentIDList": ("equipment", "EQP-", 3),
    "ServiceList": ("services", "", 0),
}

#: free text ID columns, checked against the register they point at
FOREIGN_KEYS: List[Tuple[str, str, str, str, int]] = [
    ("jobs", "contract", "contracts", "CON-", 4),
    ("jobs", "quote", "quotes", "QTE-", 4),
    ("jobs", "invoice", "invoices", "INV-", 5),
    ("quotes", "job", "jobs", "JOB-", 5),
    ("quotes", "contract", "contracts", "CON-", 4),
    ("invoices", "job", "jobs", "JOB-", 5),
    ("invoices", "contract", "contracts", "CON-", 4),
    ("timesheets", "job", "jobs", "JOB-", 5),
    ("expenses", "job", "jobs", "JOB-", 5),
    ("feedback", "job", "jobs", "JOB-", 5),
    ("feedback", "property", "properties", "PRP-", 4),
]


def _module_name(module) -> str:
    return module.__name__.rsplit(".", 1)[1]


def check_rows(cfg) -> Tuple[List[Problem], Dict[str, Any],
                              Dict[str, Any]]:
    """Keys, drop-down membership and capacity, register by register."""
    problems: List[Problem] = []
    rows_by_module: Dict[str, Any] = {}
    specs: Dict[str, Any] = {}

    for module in B.REGISTER_MODULES:
        short = _module_name(module)
        spec = module.spec(cfg)
        specs[short] = spec
        rows = S.get(short, cfg)
        rows_by_module[short] = rows
        if not rows:
            problems.append((short, "no sample rows at all"))
            continue
        if len(rows) > spec.rows:
            problems.append((
                short,
                f"{len(rows)} sample rows but the register only has "
                f"room for {spec.rows} - the tail is dropped "
                f"silently"))

        inputs = {col.key: col for col in spec.columns
                  if not col.formula}
        formulas = {col.key for col in spec.columns if col.formula}
        for number, row in enumerate(rows, start=1):
            for key, value in row.items():
                if key in formulas:
                    problems.append((
                        short,
                        f"row {number}: '{key}' is a formula column"))
                    continue
                col = inputs.get(key)
                if col is None:
                    problems.append((
                        short, f"row {number}: '{key}' is not a "
                               f"column on this register"))
                    continue
                if value in (None, ""):
                    continue
                if col.style == "date" and not isinstance(
                        value, _dt.date):
                    problems.append((
                        short, f"row {number}: '{key}' should be a "
                               f"date, got {value!r}"))
                if col.style == "time" and not isinstance(
                        value, _dt.time):
                    problems.append((
                        short, f"row {number}: '{key}' should be a "
                               f"time, got {value!r}"))
                if col.style in ("money", "number", "number1", "int",
                                 "percent", "percent0", "rating") \
                        and isinstance(value, str):
                    problems.append((
                        short, f"row {number}: '{key}' should be a "
                               f"number, got {value!r}"))
                validate = col.validate or {}
                source = validate.get("source")
                if isinstance(source, list):
                    if value not in source:
                        problems.append((
                            short, f"row {number}: '{key}' = "
                                   f"{value!r} is not in {source}"))
                elif isinstance(source, str):
                    name = source.lstrip("=")
                    allowed = LIST_SOURCES.get(name)
                    if allowed is not None and value not in allowed:
                        problems.append((
                            short, f"row {number}: '{key}' = "
                                   f"{value!r} is not in {name}"))
    return problems, rows_by_module, specs


def check_joins(cfg, rows_by_module, specs) -> List[Problem]:
    """Every ID must point at a row that will actually exist."""
    problems: List[Problem] = []
    counts = {name: len(rows) for name, rows in rows_by_module.items()}

    def _check(module: str, key: str, target: str, prefix: str,
               digits: int) -> None:
        limit = counts.get(target, 0)
        for number, row in enumerate(rows_by_module.get(module, []),
                                     start=1):
            value = row.get(key)
            if not value:
                continue
            match = re.fullmatch(prefix + r"(\d{%d})" % digits,
                                 str(value))
            if match is None:
                problems.append((
                    module, f"row {number}: '{key}' = {value!r} is "
                            f"not a {prefix}... ID"))
                continue
            if not 1 <= int(match.group(1)) <= limit:
                problems.append((
                    module, f"row {number}: '{key}' = {value!r} "
                            f"points past the end of {target} "
                            f"({limit} rows)"))

    for name, (target, prefix, digits) in ID_SOURCES.items():
        if not prefix:
            continue
        for module in rows_by_module:
            spec_keys = {
                "CustomerList": "customer",
                "PropertyList": "property",
                "CrewIDList": "employee",
                "MaterialIDList": "material",
                "EquipmentIDList": "equipment",
            }.get(name)
            if spec_keys is None:
                continue
            # only check the column when it really is an ID column on
            # that register - `services.equipment` is a category
            column = next((col for col in specs[module].columns
                           if col.key == spec_keys), None)
            if column is None or column.style != "id":
                continue
            _check(module, spec_keys, target, prefix, digits)

    for module, key, target, prefix, digits in FOREIGN_KEYS:
        _check(module, key, target, prefix, digits)

    # a service name has to be in the catalogue
    catalogue = {row["name"] for row in rows_by_module["services"]}
    for module in ("jobs", "quotes", "contracts"):
        for number, row in enumerate(rows_by_module[module], start=1):
            service = row.get("service")
            if service and service not in catalogue:
                problems.append((
                    module, f"row {number}: service {service!r} is "
                            f"not in the Service Catalog"))

    # a property has to belong to the customer the job names
    owner = {f"PRP-{number:04d}": row["customer"]
             for number, row in enumerate(
                 rows_by_module["properties"], start=1)}
    for module in ("jobs", "quotes", "contracts"):
        for number, row in enumerate(rows_by_module[module], start=1):
            prop, customer = row.get("property"), row.get("customer")
            if prop and customer and owner.get(prop) != customer:
                problems.append((
                    module, f"row {number}: {prop} belongs to "
                            f"{owner.get(prop)}, not {customer}"))
    return problems


def check_narrative(cfg, rows_by_module) -> List[Problem]:
    """Recompute the story in plain Python: stock, odometers, money."""
    problems: List[Problem] = []

    # --- stock: you cannot use what you never bought -----------------
    materials = rows_by_module["materials"]
    balance = {f"MAT-{number:04d}": float(row.get("opening") or 0)
               for number, row in enumerate(materials, start=1)}
    moves = sorted(
        (row for row in rows_by_module["expenses"] if row.get("material")),
        key=lambda row: row["date"])
    for row in moves:
        key = row["material"]
        quantity = float(row.get("quantity") or 0)
        if row.get("movement") == "Purchase":
            balance[key] = balance.get(key, 0) + quantity
        else:
            balance[key] = balance.get(key, 0) - quantity
            if balance[key] < -0.001:
                problems.append((
                    "expenses",
                    f"{row['date']}: {key} goes to "
                    f"{balance[key]:.1f} - more used than bought"))

    # --- odometers only go forwards ----------------------------------
    last: Dict[str, float] = {}
    for row in sorted(rows_by_module["vehicles"],
                      key=lambda entry: entry["date"]):
        odometer = row.get("odometer")
        if not odometer:
            continue
        name = row["vehicle"]
        if name in last and odometer < last[name]:
            problems.append((
                "vehicles",
                f"{row['date']}: {name} odometer {odometer} is "
                f"below the previous {last[name]}"))
        last[name] = odometer

    # --- invoices: never paid more than they were raised for ---------
    for number, row in enumerate(rows_by_module["invoices"], start=1):
        subtotal = float(row.get("subtotal") or 0)
        paid = float(row.get("paid") or 0)
        if paid - subtotal > 0.01:
            problems.append((
                "invoices",
                f"row {number}: paid {paid} against a subtotal of "
                f"{subtotal}"))
        if row.get("status") == "Paid" and abs(paid - subtotal) > 0.01:
            problems.append((
                "invoices",
                f"row {number}: marked Paid but {paid} of "
                f"{subtotal} has arrived"))
        if row.get("paid_date") and not row.get("paid"):
            problems.append((
                "invoices",
                f"row {number}: has a payment date but no payment"))

    # --- jobs: completed work has hours somewhere --------------------
    hours_by_job: Dict[str, float] = {}
    for row in rows_by_module["timesheets"]:
        job = row.get("job")
        if job:
            hours_by_job[job] = hours_by_job.get(job, 0) + 1
    missing = 0
    for number, row in enumerate(rows_by_module["jobs"], start=1):
        if row.get("status") != "Completed":
            continue
        job_id = f"JOB-{number:05d}"
        if not row.get("hours_typed") and job_id not in hours_by_job:
            missing += 1
    if missing:
        problems.append((
            "jobs",
            f"{missing} completed visits have neither typed hours "
            f"nor a timesheet - they will look free"))

    # --- today has a round to print ----------------------------------
    today = cfg.today
    todays = [row for row in rows_by_module["jobs"]
              if row["date"] == today]
    if len(todays) < 4:
        problems.append((
            "jobs", f"only {len(todays)} jobs dated today - the "
                    f"Route Planner will print an empty sheet"))

    # --- the alerts the dashboard promises have something to show ----
    overdue = [row for row in rows_by_module["invoices"]
               if row.get("status") == "Overdue"]
    if len(overdue) < 2:
        problems.append(("invoices", "no overdue invoices to show"))
    if not any(row.get("status") == "Needs service"
               for row in rows_by_module["equipment"]):
        problems.append(("equipment", "nothing due a service"))
    if not any(row.get("status") == "Dormant"
               for row in rows_by_module["customers"]):
        problems.append(("customers", "nobody has gone quiet"))
    return problems


def main() -> int:
    cfg = C.Config()
    problems, rows, specs = check_rows(cfg)
    if rows:
        problems += check_joins(cfg, rows, specs)
        problems += check_narrative(cfg, rows)

    print(f"Sample data: {sum(len(r) for r in rows.values())} rows "
          f"across {len(rows)} registers")
    for name in sorted(rows):
        print(f"  {name:12s} {len(rows[name]):5d}")
    if not problems:
        print("\nNo problems found.")
        return 0
    print(f"\n{len(problems)} problem(s):")
    for where, what in problems[:80]:
        print(f"  [{where}] {what}")
    if len(problems) > 80:
        print(f"  ... and {len(problems) - 80} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
