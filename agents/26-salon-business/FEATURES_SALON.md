# Salon Business Management System - feature checklist

Development tracker for the 153-point competitive checklist.
`[x]` shipped in v1.0.0, `[~]` partial / manual, `[ ]` deferred.

Status: **148 shipped, 3 partial, 2 deferred.**

## A. Dashboard and business KPIs
- [x] Monthly and yearly revenue summaries
- [x] Total operating expenses and estimated operating profit
- [x] Revenue versus monthly target
- [x] Appointment totals and completed appointments
- [x] Cancellation and no-show rates
- [x] Average sale / average client ticket
- [x] Revenue by service category
- [x] Revenue by staff member
- [x] Retail versus service revenue
- [x] Outstanding client balances
- [x] Deposit totals and unearned deposit tracking
- [x] Monthly and annual trend charts
- [x] Top-performing services
- [x] Low-performing service indicators (rank column + top/bottom tables)
- [x] Current month versus previous month comparison

## B. Appointment management
- [x] Appointment register with date and time
- [x] Client and staff dropdowns
- [x] Service selection with automatic price and duration lookup
- [x] Booking status: booked, confirmed, completed, cancelled, no-show
- [x] Appointment notes and preferences
- [x] Deposit and remaining balance fields
- [x] Rescheduling history field
- [x] Cancellation reason field
- [x] Appointment source / referral channel
- [x] Daily, weekly and monthly views (filters + weekly/monthly reports)
- [~] Double-booking warning (manual: filter staff+date; duration column shows slots)
- [x] Follow-up and rebooking reminder dates
- [ ] Waitlist tracking (deferred)
- [x] Walk-in client logging
- [x] Appointment duration totals by staff member (staff appts + revenue blocks)

## C. Client CRM and retention
- [x] Unique client ID
- [x] Contact details and preferred contact method
- [x] Client acquisition source
- [x] First visit and most recent visit dates
- [x] Total recorded visits
- [x] Lifetime recorded spend
- [x] Favorite services and preferences (last service + notes)
- [x] Formula-based days since last visit
- [x] Next booking date
- [x] Client status: new, active, inactive (lapsed)
- [x] Birthday and special occasion fields
- [x] Referral tracking
- [x] Client feedback and satisfaction notes
- [x] Consent record fields for communications or photos
- [x] Client history searchable using filters

## D. Services and pricing
- [x] Editable service menu
- [x] Service category and description
- [x] Standard duration and price
- [x] Add-on and package pricing
- [x] Discount and promotional pricing fields
- [x] Product cost per service
- [x] Labor cost per service
- [x] Gross profit per service
- [x] Gross margin percentage
- [x] Price increase planning (planned price column)
- [x] Service utilization summaries
- [x] Popular services ranking
- [x] Custom categories for hair, nails, lashes, skincare and other
- [ ] Optional staff-specific pricing (deferred - category rates shipped instead)
- [x] Retail product attachment rate

## E. Sales, payments and cash flow
- [x] Service sales log
- [x] Retail product sales log
- [x] Transaction ID and date
- [x] Payment methods: cash, card, bank transfer and other
- [x] Split-payment recording (payments tab against a Tx ID)
- [x] Deposits and prepayments
- [x] Outstanding balance tracking
- [x] Discounts, refunds and adjustments
- [x] Sales tax or VAT fields configurable by region
- [x] Daily sales summary
- [x] Daily cash reconciliation (payments filtered by date+method)
- [x] Payment processing fee tracking
- [x] Sales totals by staff member
- [x] Sales totals by service category
- [x] Duplicate transaction ID checks

## F. Staff, commissions and payroll
- [x] Staff directory and role
- [x] Employment or contractor type field
- [x] Staff availability and working hours
- [x] Service revenue by staff member
- [x] Flat-rate or percentage commission options
- [x] Different commission rates by service category
- [x] Retail commission options
- [x] Tips received and distributed
- [x] Commission eligibility rules configurable by owner
- [x] Commission statement per staff member
- [x] Hours and attendance log
- [x] Payroll period summaries
- [x] Staff productivity indicators
- [x] Leave and absence notes
- [x] Manual adjustments and approval notes

## G. Expenses, profit and budget
- [x] Recurring and one-time expenses
- [x] Expense categories and vendor names
- [x] Rent and utilities tracking
- [x] Product and supply costs
- [x] Marketing and advertising expenses
- [x] Software and subscription costs
- [x] Equipment and maintenance expenses
- [x] Expense payment method and due date
- [x] Monthly budget by category
- [x] Actual versus budget comparison
- [x] Monthly profit-and-loss statement
- [x] Revenue, cost and operating profit charts
- [x] Break-even revenue estimate
- [x] Estimated tax reserve field
- [x] Cash-flow in and out summary

## H. Inventory and purchasing
- [x] Retail and backbar product categories
- [x] Product SKU or barcode field
- [x] Supplier and purchase cost
- [x] Opening stock and stock received
- [x] Stock used for services
- [x] Retail units sold
- [x] Damaged or wasted stock log
- [x] Automatic stock-on-hand calculation
- [x] Minimum stock and reorder alerts
- [x] Inventory value at cost
- [x] Expiry date and batch fields where relevant
- [x] Purchase order register
- [x] Supplier contact directory
- [x] Product usage cost per service
- [~] Stocktake and adjustment log (adjustment column; no separate log sheet)

## I. Marketing, loyalty and growth
- [x] Promotion and discount campaign log
- [x] Campaign start and end dates
- [x] Marketing channel tracking
- [x] New clients by source
- [x] Referral source and reward tracking
- [x] Loyalty points or visit-based rewards
- [x] Client rebooking rate
- [x] Repeat-client percentage
- [x] Promotion revenue tracking
- [x] Marketing spend and recorded revenue comparison
- [x] Gift certificate register
- [x] Package and prepaid service register
- [x] Revenue target planning
- [x] Service upsell and add-on tracking
- [x] Monthly owner action plan

## J. Reports, automation and usability
- [x] Interactive charts that update with new entries
- [x] Weekly, monthly and annual reporting
- [x] Date-range filtering where supported (autofilters on every register)
- [x] Dropdown lists and input validation
- [x] Automatic lookups and calculations
- [x] Blank-safe formulas and error handling
- [x] Conditional formatting for overdue balances and low stock
- [x] Consistent currency formatting
- [x] Editable tax, commission and target settings
- [x] Clearly distinguished input and formula cells
- [x] Frozen header rows and filters
- [x] Formula protection where supported (password: premium)
- [x] Print-friendly reports
- [x] Clearly labeled sample data
- [x] Troubleshooting guide and FAQ (Start Here)
- [~] Excel or Google Sheets compatibility testing (Excel grammar compile passed; Sheets pass scheduled)
- [x] Professional cover page and navigation
- [x] Data privacy and backup instructions
