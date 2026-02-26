Module Name: Employee Promotion
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records a formal promotion event for an employee, changing their designation, department, or salary grade. On submission, updates the Employee record and creates Internal Work History entries.

Dependencies
- Employee
- Company
- Department

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
company: Link → Company, Mandatory.
department: Link → Department, Optional.
promotion_date: Date, Mandatory.
amended_from: Link → Employee Promotion, Read Only.

Child Tables
promotion_details: Table → Employee Property History.
