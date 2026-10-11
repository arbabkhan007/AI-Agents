"""One module per tab of the workbook."""

from . import (bookings, budget, calc, clients, common, dashboard, expenses,
               health, help_tab, incidents, inventory, invoices, lists,
               messages, mileage, payments, pets, printables, reminders,
               reports, services, settings, staff, start_here, visits)

__all__ = [
    "bookings", "budget", "calc", "clients", "common", "dashboard",
    "expenses", "health", "help_tab", "incidents", "inventory", "invoices",
    "lists", "messages", "mileage", "payments", "pets", "printables",
    "reminders", "reports", "services", "settings", "staff", "start_here",
    "visits",
]
