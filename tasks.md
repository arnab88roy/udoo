# Master Implementation Plan: AI-Native Modular ERP (Agile MVP Approach)

**INSTRUCTIONS FOR THE AI AGENT:** You MUST work strictly sequentially. You are expressly forbidden from checking off a parent task until EVERY nested Validation Gate beneath it has been executed, verified, and passed. If a Validation Gate fails, you must stop and fix the code before proceeding.

## Phase 0: Environment & Database Foundation
- [x] **Task 0.1:** Initialize Python virtual environment and `requirements.txt`.
- [x] **Task 0.2:** Setup `backend/app/main.py` with FastAPI, JWT middleware, and Supabase RLS dependency injection.
- [ ] **Task 0.3:** Configure PostgreSQL MCP Server (Supabase).
    - [ ] *Gate:* Start a new conversation and ask the agent to list all tables via MCP. Does it successfully return the live database tables without hallucinating?

## Phase 1: Agent Skills Definition (The "How")
- [ ] **Task 1.1:** Create `.agents/skills/fastapi-crud-generator/SKILL.md` (Strict FastAPI boilerplate rules).
- [ ] **Task 1.2:** Create `.agents/skills/erp-relationships/SKILL.md` (UUID and Child Table rules).
- [ ] **Task 1.3:** Create `.agents/skills/rls-security/SKILL.md` (Supabase Tenant Isolation rules).
    - [ ] *Gate:* Run `ls -la .agents/skills/*/SKILL.md`. Do all three files exist with the correct formatting?

## Phase 2: Backend MVP (HRMS Vertical Slice)
*Execute using `.agents/workflows/build-from-spec.md` workflow.*
- [ ] **Task 2.1:** Build Standalone Core Masters.
    *Files:* `specs/hrms/company_spec.md`, `specs/hrms/core_masters/gender_spec.md`, `specs/hrms/core_masters/salutation_spec.md`.
    - [ ] *Gate:* Run `alembic upgrade head`. Did the migrations succeed?
    - [ ] *Gate:* Verify SQL migrations contain `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;`.
- [ ] **Task 2.2:** Build Standalone Org Masters.
    *Files:* `specs/hrms/org_masters/branch_spec.md`, `specs/hrms/org_masters/designation_spec.md`, `specs/hrms/org_masters/employment_type_spec.md`, `specs/hrms/org_masters/skill_spec.md`.
    - [ ] *Gate:* Run `alembic upgrade head`.
- [ ] **Task 2.3:** Build Dependent Masters (Requires Company).
    *Files:* `specs/hrms/org_masters/department_spec.md`, `specs/hrms/core_masters/holiday_list_spec.md`.
    - [ ] *Gate:* Check the MCP database. Are the foreign keys properly linking to the `Company` table?
- [ ] **Task 2.4:** Build Employee Master & Child Tables.
    *Files:* `specs/hrms/employee/employee_master_spec.md`, `specs/hrms/employee/employee_education_spec.md`, `specs/hrms/employee/employee_internal_work_history_spec.md`, `specs/hrms/employee/employee_external_work_history_spec.md`, `specs/hrms/employee/employee_skill_map_spec.md`, `specs/hrms/employee/employee_skill_spec.md`.
    - [ ] *Gate:* Run `pytest backend/app/tests/test_employee.py`.
    - [ ] *Gate:* Start server and hit `GET /employees`. Does the response schema include `tenant_id` and the nested child tables?
- [ ] **Task 2.5:** Build Transactional Modules (Attendance & Leave).
    *Files:* `specs/hrms/attendance/attendance_spec.md`, `specs/hrms/attendance/attendance_request_spec.md`, `specs/hrms/attendance/employee_checkin_spec.md`.
    - [ ] *Gate:* Do the transactional records contain the `docstatus` state machine endpoints (`POST /{id}/submit`)?

## Phase 3: Frontend MVP (Dynamic UI)
*Spawn a dedicated Frontend Agent for this phase.*
- [ ] **Task 3.1:** Initialize React/Vue environment with Tailwind CSS.
    - [ ] *Gate:* Does the local development server start successfully?
- [ ] **Task 3.2:** Build `<GenericDataTable />` and `<GenericErpForm />`.
    - [ ] *Gate:* Point the form at `GET /api/employees/openapi.json`. Does it successfully render the Employee Form without hardcoded HTML?
- [ ] **Task 3.3:** Build HITL Approval Dashboard.
    - [ ] *Gate:* Can a user successfully fetch a `docstatus=0` (Draft) Leave/Attendance Application, approve it, and trigger the `POST /{id}/submit` backend endpoint?

## Phase 4: Agentic MVP (AI Orchestration)
- [ ] **Task 4.1:** Build LangGraph Supervisor & HR Agent.
    - [ ] *Gate:* Can the AI autonomously draft an Attendance Request via the FastAPI and set it to `docstatus=0` for human review?

## Phase 5+: Horizontal Scaling
*Once Phase 2, 3, and 4 are proven working, scale out the rest of the ERP using the exact same pattern.*
- [ ] **Task 5.1:** Payroll & Expense Management Backend (Include `employee_grade_spec.md` here).
- [ ] **Task 5.2:** Accounting & Financial Management Backend.
- [ ] **Task 5.3:** CRM & Sales Backend.
- [ ] **Task 5.4:** Inventory & Manufacturing Backend.