Module Name: Appraisal
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
An individual performance appraisal record for one employee in an appraisal cycle. Captures ratings against each KRA/goal and computes an overall score.

Dependencies
- Employee
- Company
- Department
- Appraisal Cycle (performance/)
- Appraisal Template (performance/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
appraisal_cycle: Link → Appraisal Cycle, Mandatory.
appraisal_template: Link → Appraisal Template, Mandatory.
total_score: Float, Read Only.
start_date: Date, Optional.
end_date: Date, Optional.
amended_from: Link → Appraisal, Read Only.

Child Tables
goals: Table → Appraisal Goal.
appraisal_kra: Table → Appraisal KRA.
