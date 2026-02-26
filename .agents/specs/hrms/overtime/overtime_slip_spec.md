Module Name: Overtime Slip
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records the overtime hours worked by an employee for a particular period. On submission, creates payroll entries via Additional Salary.

Dependencies
- Employee
- Company
- Department
- Overtime Type (overtime/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Mandatory.
overtime_type: Link → Overtime Type, Mandatory.
from_date: Date, Mandatory.
to_date: Date, Mandatory.
total_overtime_hours: Float, Read Only.

Child Tables
overtime_details: Table → Overtime Details.
salary_components: Table → Overtime Salary Component.
