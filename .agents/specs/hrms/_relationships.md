# HRMS DocType Relationships Map

This file documents the full dependency graph for all HRMS DocTypes, organized by module. Use this as the authoritative reference when building Supabase schemas, Zod validators, and API routes.

---

## Legend
- **→** : Link (Foreign Key)
- **⊃** : Child Table (has-many with ON DELETE CASCADE)
- **↻** : Self-referencing FK

---

## 1. Foundation Layer (No Dependencies)

These DocTypes have zero external dependencies and must be created first.

| Spec File | DocType | Notes |
|-----------|---------|-------|
| `core_masters/gender_spec.md` | Gender | Core Masters |
| `core_masters/salutation_spec.md` | Salutation | Core Masters |
| `org_masters/branch_spec.md` | Branch | Standalone |
| `org_masters/designation_spec.md` | Designation | Standalone |
| `org_masters/employment_type_spec.md` | Employment Type | Standalone |
| `org_masters/skill_spec.md` | Skill | Standalone |
| `overtime/overtime_type_spec.md` | Overtime Type | Standalone |
| `lifecycle/grievance_type_spec.md` | Grievance Type | Standalone |
| `travel/purpose_of_travel_spec.md` | Purpose of Travel | Standalone |
| `attendance/` (via Company) | — | Depends on Company (Platform) |
| `training/training_program_spec.md` | Training Program | Standalone |
| `performance/kra_spec.md` | KRA | → Department |

---

## 2. Platform Dependency Layer

DocTypes that depend on Platform masters (Company, User, Currency, Account, Cost Center). These are platform-provided and not part of HRMS itself.

| Platform DocType | Used By |
|-----------------|---------|
| Company | Department, Employee, Leave Period, Attendance, and nearly all transactional docs |
| User | Employee (user_id), Leave Application (leave_approver), Shift Request (approver) |
| Currency | Employee, Employee Grade, Leave Encashment |
| Account | Leave Encashment, Expense Claim |
| Cost Center | Leave Encashment, Expense Claim |
| Salary Component | Leave Type (earning_component) |
| Salary Structure | Employee Grade |
| Salary Slip | Leave Application |
| Additional Salary | Leave Encashment |

---

## 3. Org Masters Layer

Must be created after Foundation Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `org_masters/department_spec.md` | Department | → Company, ↻ Department (parent) |
| `org_masters/employee_grade_spec.md` | Employee Grade | → Salary Structure, → Currency |
| `core_masters/holiday_list_spec.md` | Holiday List | → Company |

---

## 4. Employee Layer

The central hub. Must be created after Org Masters.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `employee/employee_master_spec.md` | Employee | → Gender, → Salutation, → Company, → Department, → Designation, → Branch, → Employment Type, → Employee Grade, → Holiday List, → User, → Currency, ↻ Employee (reports_to) |
| `employee/employee_education_spec.md` | Employee Education | ⊃ Employee |
| `employee/employee_external_work_history_spec.md` | Employee External Work History | ⊃ Employee |
| `employee/employee_internal_work_history_spec.md` | Employee Internal Work History | ⊃ Employee, → Branch, → Department, → Designation |
| `employee/employee_skill_map_spec.md` | Employee Skill Map | → Employee |
| `employee/employee_skill_spec.md` | Employee Skill | ⊃ Employee Skill Map, → Skill |
| `employee/employee_training_spec.md` via `training/employee_training_spec.md` | Employee Training | ⊃ Employee Skill Map, → Training Event |

---

## 5. Leave Module Layer

Depends on Employee Layer and Org Masters.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `leave/leave_type_spec.md` | Leave Type | → Salary Component |
| `leave/leave_period_spec.md` | Leave Period | → Company, → Holiday List |
| `leave/leave_policy_spec.md` | Leave Policy | Submittable |
| `leave/leave_policy_detail_spec.md` | Leave Policy Detail | ⊃ Leave Policy, → Leave Type |
| `leave/leave_policy_assignment_spec.md` | Leave Policy Assignment | → Employee, → Leave Policy, → Leave Period. Submittable |
| `leave/leave_allocation_spec.md` | Leave Allocation | → Employee, → Leave Type, → Leave Period, → Leave Policy, → Leave Policy Assignment, → Compensatory Leave Request. Submittable |
| `leave/leave_application_spec.md` | Leave Application | → Employee, → Leave Type, → Department, → Company, → User (approver). Submittable |
| `leave/leave_block_list_spec.md` | Leave Block List | → Company, → Leave Type |
| `leave/leave_block_list_date_spec.md` | Leave Block List Date | ⊃ Leave Block List |
| `leave/leave_block_list_allow_spec.md` | Leave Block List Allow | ⊃ Leave Block List, → User |
| `leave/leave_ledger_entry_spec.md` | Leave Ledger Entry | → Employee, → Leave Type, → Company, → Holiday List. System-created. Submittable |
| `leave/leave_encashment_spec.md` | Leave Encashment | → Employee, → Leave Type, → Leave Period, → Leave Allocation, → Currency, → Account, → Cost Center. Submittable |
| `leave/compensatory_leave_request_spec.md` | Compensatory Leave Request | → Employee, → Leave Type, → Leave Allocation. Submittable |

---

## 6. Attendance Layer

Depends on Employee Layer and Shift Layer (cross-dependency).

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `attendance/attendance_spec.md` | Attendance | → Employee, → Company, → Leave Type, → Leave Application, → Attendance Request, → Shift Type, → Overtime Type. Submittable |
| `attendance/attendance_request_spec.md` | Attendance Request | → Employee, → Company, → Shift Type. Submittable |
| `attendance/employee_checkin_spec.md` | Employee Checkin | → Employee, → Shift Type, → Attendance, → Overtime Type |

---

## 7. Shift Layer

Depends on Employee Layer and Overtime Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `shift/shift_location_spec.md` | Shift Location | Standalone |
| `shift/shift_type_spec.md` | Shift Type | → Holiday List, → Overtime Type |
| `shift/shift_request_spec.md` | Shift Request | → Employee, → Company, → Shift Type, → User (approver). Submittable |
| `shift/shift_assignment_spec.md` | Shift Assignment | → Employee, → Company, → Shift Type, → Shift Location, → Shift Request, → Overtime Type. Submittable |

---

## 8. Overtime Layer

Depends on Employee Layer and Attendance Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `overtime/overtime_type_spec.md` | Overtime Type | Standalone |
| `overtime/overtime_slip_spec.md` | Overtime Slip | → Employee, → Company, → Overtime Type. Submittable |
| `overtime/overtime_details_spec.md` | Overtime Details | ⊃ Overtime Slip, → Attendance |
| `overtime/overtime_salary_component_spec.md` | Overtime Salary Component | ⊃ Overtime Slip, → Salary Component |

---

## 9. Expense Layer

Depends on Employee Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `expense/expense_claim_type_spec.md` | Expense Claim Type | Standalone |
| `expense/expense_claim_spec.md` | Expense Claim | → Employee, → Company, → Currency, → Account, → Cost Center. Submittable |
| `expense/expense_claim_detail_spec.md` | Expense Claim Detail | ⊃ Expense Claim, → Expense Claim Type, → Account, → Cost Center |
| `expense/expense_claim_advance_spec.md` | Expense Claim Advance | ⊃ Expense Claim, → Employee Advance, → Account |
| `expense/expense_taxes_and_charges_spec.md` | Expense Taxes and Charges | ⊃ Expense Claim, → Account |

---

## 10. Travel Layer

Depends on Employee Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `travel/purpose_of_travel_spec.md` | Purpose of Travel | Standalone |
| `travel/travel_request_spec.md` | Travel Request | → Employee, → Company, → Department, → Purpose of Travel. Submittable |
| `travel/travel_itinerary_spec.md` | Travel Itinerary | ⊃ Travel Request |
| `travel/travel_request_costing_spec.md` | Travel Request Costing | ⊃ Travel Request |

---

## 11. Lifecycle Layer

Depends on Employee Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `lifecycle/employee_advance_spec.md` | Employee Advance | → Employee, → Company, → Account, → Currency. Submittable |
| `lifecycle/employee_promotion_spec.md` | Employee Promotion | → Employee, → Company, → Department. Submittable |
| `lifecycle/employee_property_history_spec.md` | Employee Property History | ⊃ Employee Promotion / Employee Transfer |
| `lifecycle/employee_transfer_spec.md` | Employee Transfer | → Employee, → Company. Submittable |
| `lifecycle/grievance_type_spec.md` | Grievance Type | Standalone |
| `lifecycle/employee_grievance_spec.md` | Employee Grievance | → Employee, → Company, → Department, → Grievance Type |
| `lifecycle/exit_interview_spec.md` | Exit Interview | → Employee, → Company, → Department |
| `lifecycle/full_and_final_statement_spec.md` | Full and Final Statement | → Employee, → Company, → Department. Submittable |
| `lifecycle/full_and_final_asset_spec.md` | Full and Final Asset | ⊃ Full and Final Statement |
| `lifecycle/full_and_final_outstanding_statement_spec.md` | Full and Final Outstanding Statement | ⊃ Full and Final Statement |

---

## 12. Performance Layer

Depends on Employee Layer and Org Masters.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `performance/kra_spec.md` | KRA | → Department |
| `performance/appraisal_template_spec.md` | Appraisal Template | Standalone structure |
| `performance/appraisal_template_goal_spec.md` | Appraisal Template Goal | ⊃ Appraisal Template, → KRA |
| `performance/appraisal_cycle_spec.md` | Appraisal Cycle | → Appraisal Template, → Company, → Department. Submittable |
| `performance/appraisee_spec.md` | Appraisee | ⊃ Appraisal Cycle, → Employee |
| `performance/appraisal_spec.md` | Appraisal | → Employee, → Company, → Appraisal Cycle, → Appraisal Template. Submittable |
| `performance/appraisal_kra_spec.md` | Appraisal KRA | ⊃ Appraisal, → KRA |

---

## 13. Training Layer

Depends on Employee Layer.

| Spec File | DocType | Dependencies |
|-----------|---------|--------------|
| `training/training_program_spec.md` | Training Program | Standalone |
| `training/training_event_spec.md` | Training Event | → Training Program. Submittable |
| `training/training_event_employee_spec.md` | Training Event Employee | ⊃ Training Event, → Employee |
| `training/training_result_spec.md` | Training Result | → Training Event |
| `training/training_result_employee_spec.md` | Training Result Employee | ⊃ Training Result, → Employee |
| `training/employee_training_spec.md` | Employee Training | ⊃ Employee Skill Map, → Training Event |

---

## Recommended Creation Order (for Supabase Migrations)

1. Platform Masters (Company, User, Currency, Account, Cost Center — Platform)
2. Foundation Masters (Gender, Salutation, Branch, Designation, Employment Type, Skill, Overtime Type, Grievance Type, Purpose of Travel, Training Program, Shift Location)
3. Org Masters (Department, Employee Grade, Holiday List)
4. Employee Master + child tables
5. Leave Type → Leave Period → Leave Policy → Leave Policy Assignment → Leave Allocation
6. Shift Type → Shift Request → Shift Assignment
7. Attendance → Employee Checkin
8. Leave Application → Compensatory Leave Request → Leave Ledger Entry → Leave Encashment
9. Overtime Slip + children
10. Expense Module (Expense Claim Type → Expense Claim + children)
11. Travel Module
12. Lifecycle Module (Employee Advance, Promotion, Transfer, Grievance, Exit Interview, Full & Final)
13. Performance Module (KRA → Appraisal Template → Appraisal Cycle → Appraisal)
14. Training Module (Training Event → Training Result)
15. Employee Skill Map + Employee Skill + Employee Training
