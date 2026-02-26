Module Name: Exit Interview
Module: HRMS / HR
Type: Transactional
DocStatus: No

Description
Captures the exit interview conducted with an employee who has resigned, recording their feedback, reasons for leaving, and overall interview outcome.

Dependencies
- Employee
- Company
- Department
- User (for interviewer)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
date: Date, Mandatory.
interview_summary: Text Editor, Optional.
reason_for_leaving: Select, Optional.
relieving_date: Date, Optional.
amended_from: Link → Exit Interview, Read Only.
