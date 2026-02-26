Module Name: Appraisee
Module: HRMS / HR
Type: Child Table (of Appraisal Cycle)
DocStatus: No

Description
A single employee row within an Appraisal Cycle, representing one participant in the appraisal round.

Parent
Appraisal Cycle (field: appraisees)

Dependencies
- Employee

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
appraisal: Link → Appraisal, Read Only (populated after Appraisal is created).
