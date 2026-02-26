Module Name: Full and Final Statement
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
The final settlement document for an exiting employee, consolidating all outstanding assets, liabilities, and dues before clearance.

Dependencies
- Employee
- Company
- Department

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
relieving_date: Date, Mandatory.
status: Select (Draft, In Progress, Completed), Default: Draft.

Child Tables
assets_to_be_returned: Table → Full and Final Asset.
outstanding_statements: Table → Full and Final Outstanding Statement.
