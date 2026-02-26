Module Name: Leave Policy Assignment
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Assigns a Leave Policy to a specific employee for a defined period. On submission, it triggers the auto-creation of Leave Allocations for each leaf type in the policy.

Dependencies
- Employee
- Company
- Leave Policy (leave/)
- Leave Period (leave/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
company: Link → Company, Read Only (fetched from employee).
leave_policy: Link → Leave Policy, Mandatory.
assignment_based_on: Select (Leave Period, Joining Date), Optional.
leave_period: Link → Leave Period, Mandatory if assignment_based_on = Leave Period.
effective_from: Date, Mandatory.
effective_to: Date, Mandatory.
carry_forward: Check, Default: 0.
leaves_allocated: Check, Default: 0, Hidden, Read Only (system flag).
amended_from: Link → Leave Policy Assignment, Read Only.
