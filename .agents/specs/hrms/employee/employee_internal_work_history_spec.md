Module Name: Employee Internal Work History
Module: HRMS / Core Masters
Type: Child Table (of Employee)
DocStatus: No

Description
Stores the internal career progression of an employee within the company (previous departments, designations, and branches over time).

Parent
Employee (field: internal_work_history)

Dependencies
- Branch (org_masters)
- Department (org_masters)
- Designation (org_masters)

Schema Fields
branch: Link → Branch, Optional.
department: Link → Department, Optional.
designation: Link → Designation, Optional.
from_date: Date, Optional.
to_date: Date, Optional.
