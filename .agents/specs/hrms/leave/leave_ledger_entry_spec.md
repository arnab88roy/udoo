Module Name: Leave Ledger Entry
Module: HRMS / HR
Type: Transactional (Submittable, system-created)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
An immutable audit log entry that records every credit or debit to an employee's leave balance. Auto-created by Leave Allocation, Leave Application, and Leave Encashment. Never created manually.

Dependencies
- Employee
- Company
- Leave Type (leave/)
- Holiday List (core_masters)

Schema Fields
employee: Link → Employee, Optional.
employee_name: Data, Read Only (fetched from employee).
leave_type: Link → Leave Type, Optional.
company: Link → Company, Mandatory, Read Only (fetched from employee).
transaction_type: Link → DocType, Optional (e.g., "Leave Allocation", "Leave Application").
transaction_name: Dynamic Link → transaction_type, Optional.
leaves: Float, Optional (positive = credit, negative = debit).
from_date: Date, Optional.
to_date: Date, Optional.
holiday_list: Link → Holiday List, Optional.
is_carry_forward: Check, Default: 0.
is_expired: Check, Default: 0.
is_lwp: Check, Default: 0.
amended_from: Link → Leave Ledger Entry, Read Only.
