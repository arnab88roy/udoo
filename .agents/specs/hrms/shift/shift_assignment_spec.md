Module Name: Shift Assignment
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Assigns a specific Shift Type to an employee for a date range. Created manually by HR or auto-created when a Shift Request is approved.

Dependencies
- Employee
- Company
- Department
- Shift Type (shift/)
- Shift Location (shift/)
- Shift Request (shift/)
- Shift Schedule Assignment (shift/)
- Overtime Type (overtime/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Mandatory (fetched from employee).
shift_type: Link → Shift Type, Mandatory.
shift_location: Link → Shift Location, Optional.
status: Select (Active, Inactive), Default: Active.
start_date: Date, Mandatory.
end_date: Date, Optional.
overtime_type: Link → Overtime Type, Optional (fetched from shift_type).
shift_request: Link → Shift Request, Read Only.
shift_schedule_assignment: Link → Shift Schedule Assignment, Read Only.
amended_from: Link → Shift Assignment, Read Only.
