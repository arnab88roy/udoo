Module Name: Shift Request
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
An employee-initiated request to be assigned to a specific shift. Requires approver sign-off; on approval, creates a Shift Assignment.

Dependencies
- Employee
- Company
- Department
- Shift Type (shift/)
- User (for approver)

Schema Fields
shift_type: Link → Shift Type, Mandatory.
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Mandatory.
from_date: Date, Mandatory.
to_date: Date, Optional.
approver: Link → User, Mandatory (fetched from employee shift_request_approver).
status: Select (Draft, Approved, Rejected), Mandatory, Default: Draft.
amended_from: Link → Shift Request, Read Only.
