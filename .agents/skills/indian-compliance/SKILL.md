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
- Sequential per financial year: `INV-2425-0001`, `INV-2425-0002`
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

## 3. TDS on Payments (Non-Salary) — Future Phase
```
Section 194C: Contractor payments — 1% individual, 2% company
Section 194J: Professional fees — 10%
Section 194A: Interest — 10%
Store as: tds_sections table, linked to vendor/payment type
```

---

## 4. Indian Financial Year
- **April 1 to March 31** — not January to December
- All reports, payroll runs, invoice series must use this calendar
- Store `financial_year` as `VARCHAR` in format `"2425"` (for FY 2024-25)

---

## 5. State Codes (for GST)
Store as a reference table `indian_states`:
```
MH = Maharashtra, DL = Delhi, KA = Karnataka,
TN = Tamil Nadu, GJ = Gujarat, RJ = Rajasthan,
UP = Uttar Pradesh, WB = West Bengal, etc.
```
Used to auto-determine CGST/SGST vs IGST on every invoice.