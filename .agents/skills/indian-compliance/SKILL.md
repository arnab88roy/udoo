---
name: indian-compliance
description: Mandatory rules for Indian tax, payroll, and invoicing compliance in Udoo ERP.
---

# Skill: Indian Business Compliance

All financial and payroll modules in Udoo must be compliant with Indian statutory requirements.
This skill must be read before building any Payroll, Invoice, Quote, or Finance module.

---

## 1. GST (Goods and Services Tax)

### Transaction Type
| Scenario | Tax Type |
|---|---|
| Supplier and customer in same state | CGST (9%) + SGST (9%) |
| Supplier and customer in different states | IGST (18%) |
| Export | Zero-rated / exempt |

### Mandatory Fields on Every Invoice
```
- seller_gstin: VARCHAR(15)       -- 15-digit GSTIN of company
- buyer_gstin: VARCHAR(15)        -- optional if buyer is unregistered (B2C)
- seller_state_code: VARCHAR(2)   -- determines CGST/SGST vs IGST
- buyer_state_code: VARCHAR(2)    -- determines CGST/SGST vs IGST
- invoice_number: VARCHAR         -- sequential per financial year (Apr–Mar)
- invoice_date: DATE
- place_of_supply: VARCHAR(2)     -- state code
- hsn_sac_code: VARCHAR(8)        -- HSN for goods, SAC for services (line item level)
- taxable_value: NUMERIC(18,2)    -- value before GST
- cgst_amount: NUMERIC(18,2)      -- populated for intra-state
- sgst_amount: NUMERIC(18,2)      -- populated for intra-state
- igst_amount: NUMERIC(18,2)      -- populated for inter-state
- total_tax: NUMERIC(18,2)
- total_amount: NUMERIC(18,2)     -- taxable_value + total_tax
```

### Invoice Number Format
- Sequential per financial year: `INV-2526-0001`, `INV-2526-0002`
- Financial year in India: April 1 to March 31
- Never reset within a financial year

---

## 2. Payroll Statutory Deductions

### PF (Provident Fund) — Mandatory if > 20 employees
```
Employee contribution: 12% of Basic Salary
Employer contribution: 12% of Basic Salary (goes to EPF + EPS)
Wage ceiling: ₹15,000/month basic for mandatory applicability
If basic > ₹15,000: PF on actual basic (employer may cap at ₹15,000)
```

### ESI (Employee State Insurance) — Mandatory if gross < ₹21,000/month
```
Employee contribution: 0.75% of Gross Salary
Employer contribution: 3.25% of Gross Salary
Not applicable if monthly gross > ₹21,000
```

### PT (Professional Tax) — State-wise, varies
```
Must be configurable per company/branch state.
Common slabs (Maharashtra example):
  Monthly gross < ₹7,500:   ₹0
  Monthly gross ₹7,500–₹10,000: ₹175
  Monthly gross > ₹10,000:  ₹200 (₹300 in February)

Store as: hr_professional_tax_slabs table with state_code + slab ranges
```

### TDS (Tax Deducted at Source) on Salary — Section 192
```
Annual estimated tax / 12 = monthly TDS deduction
Depends on: declared investments (80C, 80D), HRA exemption, regime choice (old/new)
Store employee's tax regime choice: old_regime | new_regime
```

### Salary Slip Mandatory Fields
```
- employee_id, employee_name, designation, department
- month, year, company
- basic, hra, other_allowances  (earnings)
- pf_employee, esi_employee, pt, tds  (deductions)
- pf_employer, esi_employer  (employer contributions — shown separately)
- gross_pay = sum of earnings
- total_deductions = sum of deductions
- net_pay = gross_pay - total_deductions
- working_days, present_days, lop_days
- lop_deduction = (basic / working_days) * lop_days
```

---

## 3. TDS on Payments (Non-Salary)
*Built in Task 2.11 Finance Module. Sections 194C and 194J are LIVE.*

### Section 194C — Works Contract / Contractor Payments
```
Applies to: contractors, sub-contractors, transport
Individual/HUF rate: 1%
Company rate: 2%
Threshold: ₹30,000 per single payment OR ₹1,00,000 annually
Deducted by: the person making the payment (payer)
```

### Section 194J — Professional / Technical Services
```
Applies to: CA fees, legal fees, consulting, technical services,
royalty, non-compete fees
Rate: 10% (2% for technical services from April 2020)
Threshold: ₹30,000 annually
Deducted by: the person making the payment
```

### TDS Threshold Rule
TDS applies on the FULL payment that crosses the threshold —
not just the excess amount above the threshold.

```
Example:
  Annual threshold: ₹30,000
  Payments so far this FY: ₹28,000
  New payment: ₹5,000 (accumulated = ₹33,000 → threshold crossed)
  TDS deducted: on ₹5,000 (the crossing payment, not the ₹3,000 excess)
```

### TDS Accumulation Reset
accumulated_payments_this_year resets to 0 on April 1 each year.
FY is April 1 to March 31.

### Implementation — fin_tds_configs table
```
- client_id (FK → fin_clients)
- is_applicable: Boolean
- section: "194C_individual" | "194C_company" | "194J"
- rate: Numeric (1.0, 2.0, or 10.0)
- threshold_annual: Numeric (default 30000)
- accumulated_payments_this_year: Numeric
```
See .agents/skills/finance-module/SKILL.md Rule 6 for payment-time logic.

---

## 4. Indian Financial Year
- **April 1 to March 31** — not January to December
- All reports, payroll runs, invoice series must use this calendar
- Store `financial_year` as `VARCHAR` in format `"2526"` (for FY 2025-26)

FY code = last 2 digits of start year + last 2 digits of end year:
```
  FY 2024-25 → "2425"
  FY 2025-26 → "2526"
  FY 2026-27 → "2627"
  Date 2026-03-14 → "2526" (still in 2025-26 FY)
  Date 2026-04-01 → "2627" (new FY starts April 1)
```

---

## 5. State Codes (for GST)
Store as a reference table `indian_states`:
```
MH = Maharashtra, DL = Delhi, KA = Karnataka,
TN = Tamil Nadu, GJ = Gujarat, RJ = Rajasthan,
UP = Uttar Pradesh, WB = West Bengal, etc.
```
Used to auto-determine CGST/SGST vs IGST on every invoice.

---

## 6. Finance — Invoice Compliance Rules

### Mandatory Fields on GST Invoice (B2B India)
Every submitted invoice for an Indian B2B transaction must have:
- Company GSTIN (15 characters, alphanumeric)
- Client GSTIN (15 characters) — required for B2B, optional B2C
- HSN code (goods) or SAC code (services) on every line item
- Sequential invoice number per FY (INV-YYYY-NNNN format)
- Invoice date (posting_date)
- Taxable value per line item
- CGST amount + SGST amount (intra-state) OR IGST amount (inter-state)
  — stored separately, never combined
- Total taxable value, total tax, total invoice value
- Place of supply (client state code)

### CGST/SGST vs IGST Determination
```
company.state_code == client.state_code (both Indian, same state)
  → CGST + SGST (each at half the total GST rate)
  → e.g. GST 18%: CGST 9% + SGST 9%

company.state_code != client.state_code (both Indian, different states)
  → IGST (full GST rate as single line)
  → e.g. GST 18%: IGST 18%

client.country_code != "IN" (export / foreign client)
  → Zero rated export — no GST applies
  → Mark as export supply on invoice

Either state_code is None
  → Cannot determine — store as "none", apply zero tax
  → Human must correct before submitting
```

### Invoice Numbering — Financial Year
```
Format: INV-{FY}-{NNNN zero-padded to 4 digits}
Examples:
  INV-2526-0001  (first invoice of FY 2025-26)
  QT-2526-0001   (first quote of FY 2025-26)
  PI-2526-0001   (first proforma of FY 2025-26)

Numbering resets to 0001 at FY start, per company.
```

### Multi-Currency Invoicing for Indian Companies
Indian companies can invoice in foreign currency (USD, GBP, AED etc.)
but must report GST in INR.

```
Rules:
- Invoice amount in client's currency (e.g. USD 10,000)
- Exchange rate at invoice date (RBI reference rate or contracted rate)
- base_total_amount stored in INR for reporting
- For export invoices: GST is zero-rated regardless of currency
- TDS (if applicable) is always calculated and deducted in INR
```