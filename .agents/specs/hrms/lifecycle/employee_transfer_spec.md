Module Name: Employee Transfer
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records a formal inter-department or inter-company transfer event for an employee. On submission, updates the Employee record with the new department/branch.

Dependencies
- Employee
- Company
- Department

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
company: Link → Company, Mandatory.
new_company: Link → Company, Optional.
transfer_date: Date, Mandatory.
create_new_employee_id: Check, Default: 0.
new_employee_id: Link → Employee, Read Only.
amended_from: Link → Employee Transfer, Read Only.

Child Tables
transfer_details: Table → Employee Property History.
