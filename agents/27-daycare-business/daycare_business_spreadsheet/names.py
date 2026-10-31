"""Workbook level defined names that point at the register sheets.

The drop-down lists on the `Settings & Lists` tab define their own
names.  These are the ones that have to follow live data - child IDs,
family IDs, the team, the classrooms, the store cupboard - so they are
built from the registry once every register exists.  Each one is an
``OFFSET`` range that grows and shrinks with the number of filled rows,
which is why a child you enroll this morning turns up in the attendance
drop-down this afternoon.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    # the spine of the workbook - every drop-down that must follow data
    "ChildList": ("Child Enrollment", "id"),
    "ChildNames": ("Child Enrollment", "name"),
    "FamilyList": ("Parent Database", "id"),
    "FamilyNames": ("Parent Database", "parent1"),
    "StaffList": ("Staff Database", "id"),
    "StaffNames": ("Staff Database", "name"),
    "ClassroomList": ("Classroom Management", "name"),
    "SupplyList": ("Supply Inventory", "id"),
    "SupplyNames": ("Supply Inventory", "name"),
    "InvoiceList": ("Invoices & Receipts", "id"),
    "WaitlistIDs": ("Waitlist", "id"),
    # columns the dashboard, the analytics and the reports scan
    "ChildStatusCol": ("Child Enrollment", "status"),
    "ChildRoomCol": ("Child Enrollment", "room"),
    "ChildProgramCol": ("Child Enrollment", "program"),
    "ChildDobCol": ("Child Enrollment", "dob"),
    "ChildFamilyCol": ("Child Enrollment", "family"),
    "AttendanceDates": ("Attendance", "date"),
    "AttendanceStatusCol": ("Attendance", "status"),
    "AttendanceChildCol": ("Attendance", "child"),
    "FeeMonths": ("Tuition & Fees", "month"),
    "FeeNet": ("Tuition & Fees", "net"),
    "LedgerMonths": ("Invoices & Receipts", "month"),
    "LedgerBilled": ("Invoices & Receipts", "billed"),
    "LedgerCollected": ("Invoices & Receipts", "collected"),
    "ExpenseMonths": ("Expense Tracker", "month"),
    "ExpenseCategoryCol": ("Expense Tracker", "category"),
    "ExpenseAmounts": ("Expense Tracker", "amount"),
    "PayrollMonths": ("Payroll Tracker", "month"),
    "PayrollCost": ("Payroll Tracker", "total_cost"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            continue
        spec = reg[sheet]
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
