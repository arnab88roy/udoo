# Udoo ERP — Master Implementation Plan

## Product Vision
AI-first B2B SaaS ERP for Indian SMEs (1 to 50+ person businesses).
Primary interface is **VEDA AI chat**, not forms.
Competing with Odoo/ERPNext on simplicity, Indian compliance, and zero setup friction.
Pricing: First seat free (1 year) → tiered per-seat model.

---

## Core Product Philosophy

**The conversation IS the ERP.**
VEDA does not link to records — it renders them inline as interactive
cards inside the conversation. Traditional module screens are the
escape hatch for power users, not the primary interface.

**Udoo is to business operations what Cursor is to coding.**
The human and VEDA are co-authors of the same business record.
Both can touch it. No handoff ceremony. No mode switching.

**Three rules of co-authorship:**
- Rule 1 — No silos: Every VEDA action writes to the same Postgres
  tables the form UI reads from.
- Rule 2 — Interruptible: Human can take over mid-task always.
  VEDA can take over a human-started task always.
- Rule 3 — Transparent diffs: Every field VEDA fills carries a
  visual attribution (purple tint). Human can accept all, reject
  all, or edit field by field.

---

**INSTRUCTIONS FOR THE AI AGENT:**
- You MUST work strictly sequentially within each Phase.
- You are forbidden from checking off a parent task until EVERY nested Validation Gate has passed.
- If a Validation Gate fails, stop and fix before proceeding.
- Always read `ARCHITECTURE.md` at the start of every new session before writing any code.
- Always read the relevant `.agents/skills/` SKILL.md files before generating any module code.

---

## Phase 0: Environment & Database Foundation
- [x] **Task 0.1:** Initialize Python virtual environment and `requirements.txt`.
- [x] **Task 0.2:** Setup `backend/app/main.py` with FastAPI, JWT middleware, and Supabase RLS dependency injection.
- [ ] **Task 0.3:** Configure PostgreSQL MCP Server (Supabase).
    - [ ] *Gate:* Start a new conversation and ask the agent to list all tables via MCP. Does it successfully return the live database tables without hallucinating?

---

## Phase 1: Agent Skills & Architecture Docs (The "How")
*These files are loaded by the agent at the start of every session. Complete before any further backend work.*

- [x] **Task 1.1:** Create `ARCHITECTURE.md` at project root.
    - Must include: product vision, tech stack, core rules, module status tracker, RLS strategy, Alembic as sole migration source of truth.
    - [x] *Gate:* Does the file exist and cover all sections above?

- [x] **Task 1.2:** Create `.agents/skills/fastapi-crud-generator/SKILL.md`
    - Must include: CoreMasterBase inheritance rule, tenant_id filter on every query, selectinload pattern, 201 for POST, 404 for not found, kebab-case router prefixes, state machine endpoint naming convention.
    - [x] *Gate:* Run `ls -la .agents/skills/*/SKILL.md`. Does the file exist?

- [x] **Task 1.3:** Create `.agents/skills/erp-state-machine/SKILL.md`
    - Must include: docstatus 0/1/2 definitions, required endpoints per transactional table (submit/cancel/approve/reject), master data defaults to docstatus=1, never hard delete transactional records.
    - [x] *Gate:* File exists with correct content.

- [x] **Task 1.4:** Create `.agents/skills/VEDA-api-contract/SKILL.md`
    - Must include: every Pydantic field must have a Field(description="..."), endpoint descriptions must document valid state transitions, response schemas must include all fields the AI agent needs for decision-making.
    - [x] *Gate:* File exists with correct content.

- [x] **Task 1.5:** Create `.agents/skills/indian-compliance/SKILL.md`
    - Must include: GST rules (CGST/SGST for intra-state, IGST for inter-state), payroll compliance fields (PF 12%, ESI 3.25%, PT by state), invoice mandatory fields per GST law, TDS applicability rules.
    - [x] *Gate:* File exists with correct content.

- [ ] **Task 1.6:** Archive old Supabase SQL drafts.
    - Move `supabase/20260223000000` through `20260223000005` files to `reference/supabase_drafts/`.
    - Add a `reference/supabase_drafts/README.md` stating: "These are early AI-generated drafts. Alembic is the sole migration source of truth."
    - [ ] *Gate:* No `20260223*.sql` files remain in the active `supabase/` migrations folder.

- [x] **Task 1.7:** Create `.agents/skills/veda-ui-response/SKILL.md`
    - UIResponse typed schema, all 7 response types, payload shapes
    - [x] *Gate:* File exists with complete type definitions

- [x] **Task 1.8:** Create `.agents/skills/veda-context/SKILL.md`
    - Active record context pattern, how context flows through LangGraph
    - [x] *Gate:* File exists with context schema defined

- [x] **Task 1.9:** Create `.agents/skills/frontend-card-system/SKILL.md`
    - Card component registry, how UIResponse type maps to React component
    - [x] *Gate:* File exists with component registry pattern

- [x] **Task 1.10:** Create `.agents/skills/rls-security/SKILL.md`
    - RLS enforcement rules, Alembic migration pattern, FastAPI session
      injection, defense in depth with both app-level and DB-level filtering.
    - [x] *Gate:* File exists at `.agents/skills/rls-security/SKILL.md`

- [x] **Task 1.11:** Create `.agents/skills/erp-relationships/SKILL.md`
    - Cross-module FK rules (UUID only, no SQLAlchemy relationship),
      child table rules (relational not JSONB), internal API communication.
    - [x] *Gate:* File exists at `.agents/skills/erp-relationships/SKILL.md`

- [x] **Task 1.12:** Create `.agents/skills/database-management/SKILL.md`
    - Session management, environment-aware pooling, NullPool for tests,
      async teardown hooks, error handling and rollback patterns.
    - [x] *Gate:* File exists at `.agents/skills/database-management/SKILL.md`

- [x] **Task 1.13:** Create `.agents/skills/rbac-and-scope/SKILL.md`
    - 6 roles and permission matrix, require_permission() pattern,
      org scope pattern, self-service own record check,
      VEDA permission check before suggesting actions.
    - [x] *Gate:* File exists at `.agents/skills/rbac-and-scope/SKILL.md`

---

## Phase 2: Backend MVP — HRMS Vertical Slice
*Execute using `.agents/workflows/build-from-spec.md`. Read SKILL.md files before each task.*

### ✅ Completed
- [x] **Task 2.1–2.3:** Core Masters, Org Masters, Dependent Masters (Company, Gender, Salutation, Branch, Designation, Employment Type, Department, Holiday List).
- [x] **Task 2.4:** Employee Master & Child Tables (Education, Internal/External Work History).
    - Validation: `pytest backend/app/tests/test_employee.py` passes.
    - Validation: `GET /api/employees` returns `tenant_id` and nested child tables.
- [x] **Task 2.5a:** Leave Management (LeaveType, LeaveApplication).
    - Validation: docstatus transitions Draft→Submitted→Approved verified in Swagger UI.
    - Validation: Tenant isolation confirmed.
- [x] **Task 2.5b:** Attendance Module.
    *Three models required:*
    - [x] `EmployeeCheckin` → `hr_employee_checkins` (raw log, no docstatus)
    - [x] `Attendance` → `hr_attendance` (docstatus, UNIQUE on employee_id + attendance_date)
    - [x] `AttendanceRequest` → `hr_attendance_requests` (docstatus, full state machine)

    *Routers required:*
    - [x] `/api/employee-checkins` — CRUD only
    - [x] `/api/attendance` — CRUD + `/submit` + `/cancel`
    - [x] `/api/attendance-requests` — CRUD + `/submit` + `/approve` + `/reject` + `/cancel`

- [x] **Task 2.6:** Fix LeaveApplication — add missing `POST /{id}/cancel` endpoint (docstatus 1→2).
- [x] **Task 2.7:** Fix `dependencies.py` — implement real JWT decode for tenant_id extraction.
- [x] **Task 2.8:** Split `hr_masters/router.py` into domain files.
    - `routers/employees.py`, `routers/leave.py`, `routers/attendance.py`
- [x] **Task 2.9:** Basic Payroll Module.
    - Models: `SalaryComponent`, `SalaryStructure`, `SalarySlip`, `SalarySlipEarning`, `SalarySlipDeduction`
    - Indian compliance: PF 12%, ESI 3.25%/0.75%, PT state-wise, TDS monthly
    - `PayrollCalculator` — pure logic class, no DB calls
    - State machine: Draft → Submitted → Cancelled
    - Endpoints: `POST /salary-slips/bulk-generate`, `/submit`, `/cancel`

### Immediate Backend Tasks (Before Any Frontend Work)

- [x] **Task 2.9b:** Define UIResponse Pydantic Schema
    *File:* `backend/app/schemas/ui_response.py`

    *Schemas created:*
    - `UIResponseType` Enum: TABLE, FORM, APPROVAL, BLOCKER, CONFIRM, PROGRESS, TEXT
    - `UIContext`: open_record_type, open_record_id, open_module, tenant_id
    - `UIAction`: action_id, label, style, endpoint, method, payload,
      confirmation_required, sets_context
    - `FormField` + `FormFieldType`: text, textarea, number, date, select,
      fk_picker, toggle, file, readonly — with veda_filled and veda_confidence
    - `ProgressStep` + `ProgressStepStatus`
    - `TablePayload`: columns, rows, total, record_type, row_id_field
    - `FormPayload`: record_type, record_id, fields, values, submit_endpoint
    - `ApprovalPayload`: record_type, record_id, summary, action_options
    - `BlockerPayload`: reason, resolution_options, blocked_task
    - `ConfirmPayload`: summary, warning, is_irreversible
    - `ProgressPayload`: steps, current_step, percent, task_id
    - `TextPayload`: content, hints
    - `VEDARequest`: message, context, conversation_history (max 10)
    - `UIResponse` (root): type, message, payload, actions, context,
      veda_confidence, audit_note
    - Factory functions: make_text_response, make_table_response,
      make_approval_response, make_progress_response, make_form_response,
      make_blocker_response, make_confirm_response

    - [x] *Gate:* `python -c "from app.schemas.ui_response import UIResponse; print('OK')"` succeeds
    - [x] *Gate:* JSON schema export covers all 7 response types
    - [x] *Gate:* All 7 factory functions tested and operational
    - [x] *Gate:* `POST /api/veda/chat` stub returns valid UIResponse JSON

- [x] **Task 2.9c:** Implement Active Record Context System
    *File:* `backend/app/utils/veda_context.py`

    *Functions created:*
    - `build_context(tenant_id, ...)` — general purpose context builder
    - `null_context(tenant_id)` — for background tasks and home dashboard
    - `context_for_module(tenant_id, module)` — module-scoped, no record
    - `context_for_record(tenant_id, type, id, module)` — specific record
    - `sanitise_request_context(ctx, jwt_tenant)` — JWT always overwrites
      client-supplied tenant_id. Call at top of every VEDA endpoint.
    - `is_record_context_active(ctx)` — bool check
    - `context_matches_type(ctx, type)` — LangGraph guard
    - `describe_context(ctx)` — human-readable string for LangGraph prompts

    *Security guarantee:* Client cannot spoof tenant_id through context body.
    JWT tenant_id always overwrites client-supplied value.

    *Tests:* 9 unit tests in `backend/app/tests/test_veda_context.py`

    *Updated:* `backend/app/main.py` `/api/veda/chat` endpoint uses
    `sanitise_request_context()` and returns `describe_context()` in stub.

    *Updated:* `.agents/skills/veda-context/SKILL.md` — factory function
    reference table and LangGraph agent pattern added.

    - [x] *Gate:* `POST /api/veda/chat` returns valid UIResponse JSON
    - [x] *Gate:* Context fields are present in the response even for TEXT type
    - [x] *Gate:* Record context flows through: employee record open →
      response message contains employee ID and hrms module
    - [x] *Gate:* Null context flows through: home dashboard →
      response message contains "No record is currently open"
    - [x] *Gate:* Tenant spoofing blocked: client-supplied tenant_id
      overwritten by JWT value — 9 tests passed

- [x] **Task 2.10:** User Authentication, RBAC & Org Scope Foundation
    *This task must be completed before Finance (2.11) and LangGraph (3.1).*
    *Both depend on knowing WHO the user is and WHAT they can access.*

    *Files created:*
    - `backend/app/schemas/user_context.py` — Typed UserContext dataclass
      with role properties: is_owner, is_hr_manager, is_finance_manager,
      is_manager, is_employee, is_auditor, can_see_all_employees,
      has_payroll_access, has_finance_access
    - `backend/app/utils/permissions.py` — DEFAULT_PERMISSIONS matrix
      for 6 roles × 6 modules × 6 actions. Functions: check_permission(),
      require_permission(), require_own_record()
    - `backend/app/utils/org_scope.py` — Recursive PostgreSQL CTE via
      SQLAlchemy text(). Functions: get_subordinate_ids(),
      get_visible_employee_ids()

    *Files modified:*
    - `backend/app/modules/core_masters/models.py` — User extended with
      role, hashed_password, company_id, employee_id (use_alter circular FK),
      last_login. RolePermission table added. SQLAlchemy event listeners
      auto-populate created_by/modified_by on all tables via ContextVar.
    - `backend/app/db/database.py` — current_user_id_ctx ContextVar added
    - `backend/app/dependencies.py` — get_current_user() added alongside
      get_tenant_id(). ContextVar set on every authenticated request.
      Existing endpoints unchanged.
    - `backend/app/modules/payroll/router.py` — bulk-generate endpoint
      hardened with require_permission(current_user, "payroll", "submit")
    - `backend/generate_test_token.py` — Interactive role selection.
      JWT now carries user_id, role, employee_id, company_id.

    *Migration:* `6fde2351c883_add_rbac_user_roles_org_scope`
    - Alters hr_users: role, hashed_password, company_id, employee_id, last_login
    - Creates hr_role_permissions with RLS enabled
    - Manually adds audit FK constraints to 10 concrete tables
    - Seeds DEFAULT_PERMISSIONS for test tenant

    *Six roles:*
    - `owner` — full access to all 6 modules
    - `hr_manager` — HRMS + Payroll full, Finance/CRM none
    - `finance_manager` — Finance + CRM full, HRMS none
    - `manager` — HRMS view+approve team only, no payroll/finance
    - `employee` — self-service only (own leaves, payslips, attendance)
    - `auditor` — read-only across all 6 modules

    *Tests:* 12 tests in `backend/app/tests/test_rbac.py`
    - 8 original + 4 role segregation tests added in patch
    - Covers: permission matrix, 403 enforcement, own record check,
      HR/Finance boundary, Finance/HRMS boundary, manager scope,
      auditor read-only across all modules

    - [x] *Gate:* alembic upgrade head succeeds
    - [x] *Gate:* pytest backend/app/tests/test_rbac.py — 12 passed
    - [x] *Gate:* created_by auto-populated on new record creation
    - [x] *Gate:* Employee-role token receives 403 on payroll endpoint
    - [x] *Gate:* Org scope query returns correct subordinate IDs

- [ ] **Task 2.11:** Quote & Invoice Module (Finance)
    *Requires Task 2.10 to be complete — built with RBAC from day one.*
    *New module:* `backend/app/modules/finance/`

    *Models required:*
    - `Client` → client master (name, GSTIN, billing address, state code)
    - `Quote` → transactional, docstatus, line items child table
    - `QuoteLineItem` → child table (description, qty, rate, GST%, HSN/SAC)
    - `Invoice` → transactional, docstatus, linkable to Quote
    - `InvoiceLineItem` → child table
    - `Payment` → payment recording against invoice (partial + full)

    *Indian compliance mandatory:*
    - GSTIN on client and company
    - HSN/SAC code on line items
    - CGST/SGST (intra-state) or IGST (inter-state) auto-calculated
    - Invoice number sequential per financial year (INV-2526-0001)
    - Outstanding amount = invoice total - sum of payments

    *State machines:*
    - Quote: Draft → Sent → Accepted / Rejected / Expired
    - Invoice: Draft → Sent → Partially Paid → Paid / Cancelled

    *RBAC integration:*
    - All endpoints require require_permission(user, "finance", action)
    - finance_manager and owner only

    *VEDA scenarios this enables:*
    - "Create a quote for Sharma Textiles for 5 days at ₹15,000/day"
    - "Convert that quote to invoice and mark it sent"
    - "What's my total outstanding this month?"
    - "Sharma Textiles paid ₹45,000 against invoice INV-2526-0004"

    - [x] *Gate:* GST correct for intra-state and inter-state test cases
    - [x] *Gate:* Invoice number sequential per financial year
    - [x] *Gate:* GET /invoices/{id} includes line items + GST breakdown + outstanding
    - [x] *Gate:* POST /quotes/{id}/convert-to-invoice works
    - [x] *Gate:* Employee-role token receives 403 on all finance endpoints

---

## Phase 3: VEDA AI Layer (Build This Before Full Frontend)

IMPORTANT: This phase moves earlier than originally planned.
The AI layer is the product's core differentiator.
Build one tool at a time, adding capabilities module by module.
Do not build a full traditional ERP first.

- [ ] **Task 3.1:** LangGraph Supervisor + First Tool (List Employees)
    - Supervisor routes messages to HR Agent
    - HR Agent has ONE tool: list_employees (calls GET /api/employees/)
    - Returns UIResponse of type TABLE
    - [ ] *Gate:* "Show me all active employees" → returns TABLE UIResponse
    - [ ] *Gate:* Table renders inline in chat (no page navigation)
    - [ ] *Gate:* VEDA system prompt includes user role and scope description
    - [ ] *Gate:* Owner asking "show all employees" returns all 22
    - [ ] *Gate:* Manager asking "show all employees" returns only their team

- [ ] **Task 3.2:** HR Agent — Core Tools
    Tools to add one at a time:
    - get_employee (by name or ID) → FORM UIResponse
    - list_leave_applications → TABLE UIResponse
    - approve_leave (id) → APPROVAL UIResponse → CONFIRM UIResponse
    - get_attendance_summary → TABLE UIResponse
    - get_my_permissions() → TEXT UIResponse listing what the user can do
      "You can approve leaves for your team. You cannot access payroll."
    - [ ] *Gate:* Full leave approval flow works in chat: list → select → approve → confirm

- [ ] **Task 3.3:** HR Agent — Payroll Tools
    Tools to add:
    - get_payroll_status (month, year) → TABLE UIResponse
    - run_payroll_bulk → PROGRESS UIResponse → CONFIRM UIResponse
    - get_salary_slip (employee, month) → FORM UIResponse
    - [ ] *Gate:* "Run March payroll" triggers PROGRESS then CONFIRM before executing
    *Requires role check: only owner and hr_manager can run payroll.*
    *Employee-role requests for payroll get a BLOCKER UIResponse.*

- [ ] **Task 3.4:** Finance Agent
    Tools: create_quote, create_invoice, list_invoices, get_client
    - [ ] *Gate:* "Create invoice for Sharma Textiles for ₹45,000" → FORM UIResponse pre-filled

- [ ] **Task 3.5:** Policy Engine Schema
    *File:* `backend/app/modules/policy/models.py`
    Stores: approval thresholds, mandatory wait periods, fallback rules
    VEDA queries this at runtime — rules are NOT hardcoded in prompts
    - [ ] *Gate:* PF/ESI thresholds, approval chains, LOP rules all queryable via API

- [ ] **Task 3.6:** Setup/Onboarding Agent
    5-question VEDA conversation → fully configured tenant
    - [ ] *Gate:* Fresh tenant → VEDA conversation → Company + Dept + Leave policy + Salary structure created

- [ ] **Task 3.7:** Personalised VEDA Greeting (Role-Aware Proactive Context)
    On login, VEDA pre-fetches pending items scoped to the user's role:

    Owner sees:
    - Pending approvals count (all types)
    - Payroll status (next run due date)
    - Outstanding invoice total
    - Team attendance summary

    HR Manager sees:
    - Pending leave approvals
    - Attendance anomalies
    - Upcoming payroll run

    Manager sees:
    - Pending leave approvals for their team only
    - Their team's attendance for today

    Employee sees:
    - Their leave balance
    - Their payslip status for last month
    - Their pending attendance corrections

    - [ ] *Gate:* Owner login → VEDA greeting includes payroll + invoice data
    - [ ] *Gate:* Employee login → VEDA greeting shows only personal data
    - [ ] *Gate:* Manager login → VEDA greeting shows only their team data

---

## Phase 4: Frontend — IDE Shell

IMPORTANT: This is NOT a traditional ERP frontend.
The layout is a browser-based IDE. The center panel is the VEDA
conversation. Everything else is chrome around the conversation.

### Layout (non-negotiable):

```
┌────┬─────────────────────────────────────────────────────┐
│    │                TOP BAR (48px)                        │
│ A  ├──────────────┬──────────────────┬───────────────────┤
│ C  │              │                  │                   │
│ T  │  LEFT PANEL  │  CENTER PANEL    │   RIGHT PANEL     │
│ I  │  (record     │  ← VEDA CHAT →   │   (record         │
│ V  │   navigator, │  inline cards    │    inspector,     │
│ I  │   badges,    │  render here     │    field detail,  │
│ T  │   reports)   │                  │    audit trail)   │
│ Y  │              │                  │                   │
│    │  240px       │  flex: 1         │  300px            │
└────┴──────────────┴──────────────────┴───────────────────┘
 48px
```

- [ ] **Task 4.1:** IDE Shell + Component Registry
    Build the 4-panel layout shell.
    Build the UIResponse component registry:
      TABLE type → `<InlineTable />` component
      FORM type → `<InlineForm />` component
      APPROVAL type → `<ApprovalCard />` component
      BLOCKER type → `<BlockerCard />` component
      CONFIRM type → `<ConfirmCard />` component
      PROGRESS type → `<ProgressCard />` component
      TEXT type → `<TextMessage />` component
    - [ ] *Gate:* Shell renders correctly
    - [ ] *Gate:* Mock UIResponse objects render correct components
    *RBAC-aware shell requirements:*
    - Activity bar icons only show modules the user has access to
    - Finance icon hidden for hr_manager role
    - HRMS icon hidden for finance_manager role
    - Settings icon only visible to owner and hr_manager

- [ ] **Task 4.2:** VEDA Chat Engine
    Connect center panel to POST /api/veda/chat
    Stream responses using Vercel AI SDK useChat hook
    Render UIResponse components inline as messages arrive
    - [ ] *Gate:* Real API call → UIResponse → correct component renders

- [ ] **Task 4.3:** Active Record Context Wiring
    Open record type + ID passed automatically on every message
    Record navigator in left panel updates on record open
    Right panel shows inspector for active record
    - [ ] *Gate:* Opening an employee record → VEDA knows context without being told

- [ ] **Task 4.4:** HITL Approval Flow
    Approval cards in chat are interactive — buttons call FastAPI endpoints
    After action: card updates in place, VEDA continues conversation
    - [ ] *Gate:* Leave approval from chat card → DB updates → badge decrements → VEDA confirms

- [ ] **Task 4.5:** VEDA Diff Attribution
    Fields filled by VEDA render with purple tint (like Cursor ghost text)
    Accept all / reject all / field-by-field editing
    - [ ] *Gate:* VEDA-filled form fields visually distinct from human-filled

- [ ] **Task 4.6:** Role-Aware VEDA Hint Chips
    The suggested action chips below VEDA's greeting must be role-appropriate.
    Owner sees: "Run payroll", "Create invoice", "Add employee"
    HR Manager sees: "Approve leaves", "Run payroll", "View attendance"
    Manager sees: "Approve team leaves", "View team attendance"
    Employee sees: "Apply for leave", "View my payslip", "Mark attendance"
    - [ ] *Gate:* Each role sees only their relevant hint chips

---

## Phase 5: Horizontal Scaling
*Use the proven patterns from Phase 2–4 to scale remaining modules.*

- [ ] **Task 5.1:** Full Payroll Depth.
    - Payroll runs, bank transfer files, Form 16, salary revision history.
- [ ] **Task 5.2:** Expense Management.
    - Employee expense claims, approval workflow, reimbursement tracking.
- [ ] **Task 5.3:** Full Accounting Module.
    - Chart of accounts, journal entries, P&L, balance sheet, GST returns (GSTR-1, GSTR-3B).
- [ ] **Task 5.4:** CRM & Sales.
    - Lead, Opportunity, full Quote-to-Cash pipeline.
- [ ] **Task 5.5:** Inventory & Manufacturing.
    - Item master, stock ledger, purchase orders, BOM.
- [ ] **Task 5.6:** WhatsApp Integration.
    - Leave approval via WhatsApp, salary slip delivery, invoice notifications.
    - (Indian SMEs operate primarily on WhatsApp — this is a key retention feature.)

---

## Ongoing: Technical Debt & Hardening
*Address these before first paying customer.*

- [x] **TD-1:** Real JWT decode in `dependencies.py` (Task 2.7 above).
- [ ] **TD-2:** Database-level RLS via `current_setting('app.current_tenant_id')` in Alembic migrations.
- [ ] **TD-3:** Audit log table wired to all transactional tables via SQLAlchemy events.
- [ ] **TD-4:** Add `Field(description="...")` to all Pydantic schemas (required for VEDA agent accuracy).
- [x] **TD-5:** Performance — replace deep Employee eager loads on Leave/Attendance queries with `EmployeeSummary` schema.
- [x] **TD-6:** Add `POST /leave-applications/{id}/cancel` endpoint (currently missing).
- [ ] **TD-7:** Policy engine not built — approval thresholds currently not queryable via API.
- [ ] **TD-8:** UIResponse schema not yet wired to LangGraph output.
- [ ] **TD-9:** Vercel AI SDK streaming not yet implemented.
- [ ] **TD-10:** VEDA diff attribution (purple tint) not yet implemented.
- [ ] **TD-11:** Frontend shell uses wrong layout (sidebar VEDA vs IDE shell with 4 panels).
- [ ] **TD-12:** Permission checks not yet added to existing HRMS and Payroll
      endpoints (only new endpoints from Task 2.11+ have require_permission).
      Add to all existing endpoints before first paying customer.
- [ ] **TD-13:** Org scope filtering not yet applied to existing list endpoints.
      Currently all tenants see all employees regardless of role.
      Add get_visible_employee_ids() to all list endpoints before
      first paying customer.
- [ ] **TD-14:** Payroll bulk-generate uses company-level salary structure
      lookup instead of employee-specific `salary_structure_id`.
      Currently fetches the first active structure for the company.
      When a company has multiple salary structures (e.g. junior vs senior),
      all employees incorrectly get the same structure.
      Fix: Use `employee.salary_structure_id` if set, fall back to
      company default only if null.
      Address before first paying customer with multiple salary grades.
