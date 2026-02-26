Module Name: Employee Training
Module: HRMS / HR
Type: Child Table (of Employee Skill Map)
DocStatus: No

Description
A single row recording that an employee attended a specific Training Event, used in their Skill Map profile.

Parent
Employee Skill Map (field: trainings)

Dependencies
- Training Event (training/)

Schema Fields
training_event: Link → Training Event, Mandatory.
training_date: Date, Optional.
training_status: Select (Scheduled, Completed, Cancelled), Optional.
