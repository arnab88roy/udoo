Module Name: Training Event
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records a specific training session conducted on a date, tied to a Training Program. Employees attending are listed in the child table. Results and feedback are subsequently recorded per-employee.

Dependencies
- Training Program (training/)
- Company

Schema Fields
event_name: Data, Mandatory.
training_program: Link → Training Program, Mandatory.
event_status: Select (Scheduled, Completed, Cancelled), Default: Scheduled.
start_time: Datetime, Optional.
end_time: Datetime, Optional.
description: Text, Optional.
amended_from: Link → Training Event, Read Only.

Child Tables
employees: Table → Training Event Employee.
