Module Name: Attendance Request
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Allows an employee to request their attendance be marked for a date range (e.g., Work From Home or On Duty) when the system did not record a check-in.

Dependencies
- Employee
- Company
- Department
- Shift Type (shift/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Mandatory (fetched from employee).
from_date: Date, Mandatory.
to_date: Date, Mandatory.
half_day: Check, Default: 0.
half_day_date: Date, Mandatory if half_day = 1.
include_holidays: Check, Default: 0.
shift: Link → Shift Type, Optional.
reason: Select (Work From Home, On Duty), Mandatory.
explanation: Small Text, Optional.
amended_from: Link → Attendance Request, Read Only.
