Module Name: Expense Claim Detail
Module: HRMS / HR
Type: Child Table (of Expense Claim)
DocStatus: No

Description
A single expense line item within an Expense Claim, specifying the type, date, amount, and sanctioned amount.

Parent
Expense Claim (field: expenses)

Dependencies
- Expense Claim Type (expense/)
- Account (Finance)
- Cost Center (Finance)

Schema Fields
expense_date: Date, Mandatory.
expense_type: Link → Expense Claim Type, Mandatory.
description: Text, Optional.
claim_amount: Currency, Mandatory.
sanctioned_amount: Currency, Optional.
account: Link → Account, Optional.
cost_center: Link → Cost Center, Optional.
