Module Name: Leave Allocation
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records the number of leave days officially granted to an employee for a specific Leave Type within a date range. Auto-created by Leave Policy Assignment or created manually.

Dependencies
- Employee
- Company
- Department
- Leave Type (leave/)
- Leave Period (leave/)
- Leave Policy (leave/)
- Leave Policy Assignment (leave/)
- Compensatory Leave Request (leave/)

Schema Fields
naming_series: Select, Mandatory, Default: HR-LAL-.YYYY.-.
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Read Only, Mandatory (fetched from employee).
leave_type: Link → Leave Type, Mandatory.
from_date: Date, Mandatory.
to_date: Date, Mandatory.
new_leaves_allocated: Float, Optional.
carry_forward: Check, Default: 0.
unused_leaves: Float, Read Only (shown if carry_forward = 1).
total_leaves_allocated: Float, Mandatory, Read Only.
total_leaves_encashed: Float, Read Only.
compensatory_request: Link → Compensatory Leave Request, Read Only.
leave_period: Link → Leave Period, Read Only.
leave_policy: Link → Leave Policy, Read Only (fetched from policy assignment).
leave_policy_assignment: Link → Leave Policy Assignment, Read Only.
carry_forwarded_leaves_count: Float, Read Only.
expired: Check, Default: 0, Hidden, Read Only.
description: Small Text, Optional.
amended_from: Link → Leave Allocation, Read Only.

Child Tables
earned_leave_schedule: Table → Earned Leave Schedule, Read Only.
