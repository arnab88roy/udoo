Module Name: Employee Grade
Module: HRMS / HR
Type: Master (Standalone)
DocStatus: No

Description
Defines paygrade levels within the organization (e.g., L1, L2, Senior). Linked to a default salary structure and used in payroll configuration.

Dependencies
- Salary Structure (Payroll module)
- Currency

Schema Fields
name: Data, Mandatory, Unique (set by user/prompt — the grade label itself, e.g. "L1").
default_salary_structure: Link → Salary Structure, Optional.
currency: Link → Currency, Read Only (fetched from salary structure).
default_base_pay: Currency, Optional (depends on default_salary_structure).
