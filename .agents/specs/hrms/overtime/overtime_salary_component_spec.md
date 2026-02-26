Module Name: Overtime Salary Component
Module: HRMS / HR
Type: Child Table (of Overtime Slip)
DocStatus: No

Description
Maps a salary component to a calculated amount for overtime compensation within an Overtime Slip.

Parent
Overtime Slip (field: salary_components)

Dependencies
- Salary Component (Payroll)

Schema Fields
salary_component: Link → Salary Component, Mandatory.
amount: Currency, Mandatory.
