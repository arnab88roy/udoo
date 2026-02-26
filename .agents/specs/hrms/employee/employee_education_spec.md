Module Name: Employee Education
Module: HRMS / Core Masters
Type: Child Table (of Employee)
DocStatus: No

Description
Stores educational qualifications for an employee. Each row represents one educational background entry (school, degree, year, etc.).

Parent
Employee (field: education)

Dependencies
None

Schema Fields
school_univ: Small Text, Optional.
qualification: Data, Optional.
level: Select (Graduate, Post Graduate, Under Graduate), Optional.
year_of_passing: Int, Optional.
class_per: Data, Optional (Class / Percentage).
maj_opt_subj: Text, Optional (Major/Optional Subjects).
