Module Name: Expense Claim Type
Module: HRMS / HR
Type: Master (Standalone)
DocStatus: No

Description
Defines a category of reimbursable expense (e.g., Travel, Meals, Accommodation). Controls the maximum claim amount per expense and links to an accounting code.

Dependencies
None

Schema Fields
name: Data, Mandatory, Unique (the expense type name).
expense_type: Data, Mandatory.
description: Text, Optional.

Note: Account-level mappings are done per-company via Expense Claim Account child table on HR Settings or company setup.
