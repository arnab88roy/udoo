Module Name: Employee Skill
Module: HRMS / HR
Type: Child Table (of Employee Skill Map)
DocStatus: No

Description
A single row representing one skill entry for an employee, including proficiency rating and the date it was last evaluated.

Parent
Employee Skill Map (field: employee_skills)

Dependencies
- Skill (org_masters)

Schema Fields
skill: Link → Skill, Mandatory.
proficiency: Rating, Mandatory.
evaluation_date: Date, Default: Today.
