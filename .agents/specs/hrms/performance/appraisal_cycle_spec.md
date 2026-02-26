Module Name: Appraisal Cycle
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Defines a period during which performance appraisals are conducted. Links to a template and controls which employees are appraised. Creating an Appraisal Cycle generates individual Appraisal records for each linked employee.

Dependencies
- Appraisal Template (performance/)
- Company
- Department

Schema Fields
cycle_name: Data, Mandatory.
appraisal_template: Link → Appraisal Template, Mandatory.
company: Link → Company, Mandatory.
department: Link → Department, Optional.
start_date: Date, Mandatory.
end_date: Date, Mandatory.
status: Select (Draft, In Progress, Completed), Default: Draft.

Child Tables
appraisees: Table → Appraisee.
