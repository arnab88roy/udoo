Module Name: Employee Skill Map
Module: HRMS / HR
Type: Master (per-employee document)
DocStatus: No

Description
A single document per employee that maps their current skills and training history. Acts as a skills profile for an employee.

Dependencies
- Employee

Schema Fields
employee: Link → Employee, Mandatory, Unique.
employee_name: Data, Read Only (fetched from employee).
designation: Data, Read Only (fetched from employee).

Child Tables
employee_skills: Table → Employee Skill.
trainings: Table → Employee Training.
