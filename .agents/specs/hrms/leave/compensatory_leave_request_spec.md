Module Name: Compensatory Leave Request
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Allows an employee to claim compensatory leave for working on a holiday. On approval, a Leave Allocation is created for the claimed leave type.

Dependencies
- Employee
- Department
- Leave Type (leave/)
- Leave Allocation (leave/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
leave_type: Link → Leave Type, Optional.
leave_allocation: Link → Leave Allocation, Read Only.
work_from_date: Date, Mandatory.
work_end_date: Date, Mandatory.
half_day: Check, Default: 0.
half_day_date: Date, Optional (shown if half_day = 1).
reason: Small Text, Mandatory.
amended_from: Link → Compensatory Leave Request, Read Only.
