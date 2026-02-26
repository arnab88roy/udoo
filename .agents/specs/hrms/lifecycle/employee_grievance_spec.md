Module Name: Employee Grievance
Module: HRMS / HR
Type: Transactional
DocStatus: No

Description
Records a formal employee grievance or complaint. Tracks the party raised against, the grievance type, resolution status, and resolution date.

Dependencies
- Employee
- Department
- Grievance Type (lifecycle/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
raised_by: Link → Employee, Optional (party raised against).
raised_by_name: Data, Read Only.
grievance_type: Link → Grievance Type, Mandatory.
grievance_date: Date, Mandatory, Default: Today.
description: Small Text, Mandatory.
status: Select (Open, In Progress, Resolved), Default: Open.
resolution_date: Date, Optional.
resolution_detail: Small Text, Optional.
