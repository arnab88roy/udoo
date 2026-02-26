Module Name: Training Result Employee
Module: HRMS / HR
Type: Child Table (of Training Result)
DocStatus: No

Description
A single employee row within a Training Result, capturing their score and pass/fail status.

Parent
Training Result (field: employees)

Dependencies
- Employee

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
score: Float, Optional.
pass: Check, Default: 0.
