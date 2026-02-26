Module Name: Training Event Employee
Module: HRMS / HR
Type: Child Table (of Training Event)
DocStatus: No

Description
A single employee row within a Training Event, tracking their attendance status.

Parent
Training Event (field: employees)

Dependencies
- Employee

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
attendance_status: Select (Present, Absent), Optional.
