Module Name: Training Result
Module: HRMS / HR
Type: Transactional
DocStatus: No

Description
Records pass/fail or score-based results for employees who attended a Training Event.

Dependencies
- Training Event (training/)

Schema Fields
training_event: Link → Training Event, Mandatory.
event_name: Data, Read Only.

Child Tables
employees: Table → Training Result Employee.
