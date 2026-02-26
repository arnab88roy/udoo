Module Name: Leave Application
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
The primary document through which employees apply for leave. Goes through an approval workflow (Open → Approved / Rejected). Upon approval, deducts from the Leave Ledger.

Dependencies
- Employee
- Company
- Department
- Leave Type (leave/)
- User (for leave approver)

Schema Fields
naming_series: Select, Mandatory, Default: HR-LAP-.YYYY.-.
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
leave_type: Link → Leave Type, Mandatory.
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Read Only, Mandatory (fetched from employee).
from_date: Date, Mandatory.
to_date: Date, Mandatory.
half_day: Check, Default: 0.
half_day_date: Date, Optional (shown if half_day = 1 and from_date ≠ to_date).
total_leave_days: Float, Read Only.
description: Small Text, Optional (Reason).
leave_balance: Float, Read Only (balance before application).
leave_approver: Link → User, Optional.
leave_approver_name: Data, Read Only.
follow_via_email: Check, Default: 1.
posting_date: Date, Mandatory, Default: Today.
status: Select (Open, Approved, Rejected, Cancelled), Mandatory, Default: Open.
salary_slip: Link → Salary Slip, Optional, Hidden.
letter_head: Link → Letter Head, Optional.
color: Color, Optional.
amended_from: Link → Leave Application, Read Only.
