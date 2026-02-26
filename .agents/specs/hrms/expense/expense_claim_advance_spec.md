Module Name: Expense Claim Advance
Module: HRMS / HR
Type: Child Table (of Expense Claim)
DocStatus: No

Description
Links a previously issued Employee Advance to an Expense Claim for deduction from the reimbursable amount.

Parent
Expense Claim (field: advances)

Dependencies
- Employee Advance (lifecycle/)

Schema Fields
employee_advance: Link → Employee Advance, Mandatory.
posting_date: Date, Read Only.
advance_account: Link → Account, Read Only.
advance_paid: Currency, Read Only.
unclaimed_amount: Currency, Read Only.
allocated_amount: Currency, Mandatory.
