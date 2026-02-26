Module Name: Expense Taxes and Charges
Module: HRMS / HR
Type: Child Table (of Expense Claim)
DocStatus: No

Description
Records applicable tax or levy charges to be included as part of the Expense Claim total.

Parent
Expense Claim (field: taxes)

Dependencies
- Account (Finance)

Schema Fields
account_head: Link → Account, Mandatory.
rate: Float, Optional.
tax_amount: Currency, Mandatory.
total: Currency, Read Only.
