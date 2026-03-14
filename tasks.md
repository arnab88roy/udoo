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

- [ ] **Task 1.1:** Create `ARCHITECTURE.md` at project root.
    - Must include: product vision, tech stack, core rules, module status tracker, RLS strategy, Alembic as sole migration source of truth.
    - [ ] *Gate:* Does the file exist and cover all sections above?

- [ ] **Task 1.2:** Create `.agents/skills/fastapi-crud-generator/SKILL.md`
    - Must include: CoreMasterBase inheritance rule, tenant_id filter on every query, selectinload pattern, 201 for POST, 404 for not found, kebab-case router prefixes, state machine endpoint naming convention.
    - [ ] *Gate:* Run `ls -la .agents/skills/*/SKILL.md`. Does the file exist?

- [ ] **Task 1.3:** Create `.agents/skills/erp-state-machine/SKILL.md`
    - Must include: docstatus 0/1/2 definitions, required endpoints per transactional table (submit/cancel/approve/reject), master data defaults to docstatus=1, never hard delete transactional records.
    - [ ] *Gate:* File exists with correct content.

- [ ] **Task 1.4:** Create `.agents/skills/VEDA-api-contract/SKILL.md`
    - Must include: every Pydantic field must have a Field(description="..."), endpoint descriptions must document valid state transitions, response schemas must include all fields the AI agent needs for decision-making.
    - [ ] *Gate:* File exists with correct content.

- [ ] **Task 1.5:** Create `.agents/skills/indian-compliance/SKILL.md`
    - Must include: GST rules (CGST/SGST for intra-state, IGST for inter-state), payroll compliance fields (PF 12%, ESI 3.25%, PT by state), invoice mandatory fields per GST law, TDS applicability rules.
    - [ ] *Gate:* File exists with correct content.

- [ ] **Task 1.6:** Archive old Supabase SQL drafts.
    - Move `supabase/20260223000000` through `20260223000005` files to `reference/supabase_drafts/`.
    - Add a `reference/supabase_drafts/README.md` stating: "These are early AI-generated drafts. Alembic is the sole migration source of truth."
    - [ ] *Gate:* No `20260223*.sql` files remain in the active `supabase/` migrations folder.

- [ ] **Task 1.7:** Create `.agents/skills/veda-ui-response/SKILL.md`
    - UIResponse typed schema, all 7 response types, payload shapes
    - [ ] *Gate:* File exists with complete type definitions

- [ ] **Task 1.8:** Create `.agents/skills/veda-context/SKILL.md`
    - Active record context pattern, how context flows through LangGraph
    - [ ] *Gate:* File exists with context schema defined

- [ ] **Task 1.9:** Create `.agents/skills/frontend-card-system/SKILL.md`
    - Card component registry, how UIResponse type maps to React component
    - [ ] *Gate:* File exists with component registry pattern

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

- [ ] **Task 2.9b:** Define UIResponse Pydantic Schema
    *File:* `backend/app/schemas/ui_response.py`

    Create these schemas:

    ```
    UIResponseType: Enum
      TABLE, FORM, APPROVAL, BLOCKER, CONFIRM, TEXT, PROGRESS

    UIAction:
      - action_id: str
      - label: str (display text on button)
      - style: Literal["primary", "secondary", "danger", "ghost"]
      - endpoint: str (FastAPI endpoint to call when clicked)
      - method: Literal["POST", "PUT", "PATCH"]
      - payload: dict (body to send)
      - confirmation_required: bool

    UIContext:
      - open_record_type: Optional[str] (e.g. "employee", "leave_application")
      - open_record_id: Optional[UUID]
      - open_module: Optional[str] (e.g. "hrms", "finance")
      - tenant_id: UUID

    UIResponsePayload variants (one per type):
      TablePayload: columns: List[str], rows: List[dict], total: int
      FormPayload: record_type: str, record_id: Optional[UUID], fields: List[FormField], values: dict
      ApprovalPayload: record_type: str, record_id: UUID, summary: dict, action_options: List[str]
      BlockerPayload: reason: str, resolution_options: List[UIAction]
      ConfirmPayload: summary: dict, warning: Optional[str], is_irreversible: bool
      ProgressPayload: steps: List[ProgressStep], current_step: int, percent: int
      TextPayload: content: str, hints: List[str]

    UIResponse (the root schema):
      - type: UIResponseType
      - message: str (VEDA's spoken response, always present)
      - payload: Union of all payload types
      - actions: List[UIAction]
      - context: UIContext
      - veda_confidence: Optional[float] (0.0-1.0, shown as indicator)
      - audit_note: Optional[str] (written to audit log)
    ```

    - [ ] *Gate:* `python -c "from app.schemas.ui_response import UIResponse; print('OK')"` succeeds
    - [ ] *Gate:* JSON schema export covers all 7 response types

- [ ] **Task 2.9c:** Implement Active Record Context System
    *Files:* `backend/app/schemas/veda_request.py`,
    `backend/app/api/veda.py` (new endpoint)

    Create `VEDARequest` schema:
    ```
    VEDARequest:
      - message: str
      - context: UIContext (the active record, passed automatically)
      - conversation_history: List[dict] (last 10 messages)
      - tenant_id: UUID (from JWT, not from body)
    ```

    Create `POST /api/veda/chat` endpoint:
    - Accepts VEDARequest
    - Validates tenant_id from JWT (not from body)
    - For now: returns a mock UIResponse of type TEXT
    - The real LangGraph wiring happens in Phase 3 (AI layer)
    - This establishes the contract so the frontend can be built against it

    - [ ] *Gate:* `POST /api/veda/chat` returns valid UIResponse JSON
    - [ ] *Gate:* Context fields are present in the response even for TEXT type

- [ ] **Task 2.10:** Quote & Invoice Module (Finance).
    *New module:* `backend/app/modules/finance/`

    *Models required:*
    - `Client` → basic client master (name, GSTIN, billing address, state)
    - `Quote` → transactional, with docstatus
    - `QuoteLineItem` → child table (description, qty, rate, GST%)
    - `Invoice` → transactional, with docstatus, linkable to Quote
    - `InvoiceLineItem` → child table

    *Indian compliance mandatory fields:*
    - GSTIN on client and company
    - HSN/SAC code on line items
    - CGST/SGST (intra-state) or IGST (inter-state) auto-calculated
    - Invoice number sequential per financial year

    *State machines:*
    - Quote: Draft → Submitted → Accepted / Rejected / Expired
    - Invoice: Draft → Submitted → Paid / Partially Paid / Cancelled

    - [ ] *Gate:* GST calculation correct for intra-state and inter-state test cases.
    - [ ] *Gate:* `GET /invoices/{id}` includes line items with correct GST breakdown.
    - [ ] *Gate:* Quote → Invoice conversion endpoint works (`POST /quotes/{id}/convert-to-invoice`).

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

- [ ] **Task 3.2:** HR Agent — Core Tools
    Tools to add one at a time:
    - get_employee (by name or ID) → FORM UIResponse
    - list_leave_applications → TABLE UIResponse
    - approve_leave (id) → APPROVAL UIResponse → CONFIRM UIResponse
    - get_attendance_summary → TABLE UIResponse
    - [ ] *Gate:* Full leave approval flow works in chat: list → select → approve → confirm

- [ ] **Task 3.3:** HR Agent — Payroll Tools
    Tools to add:
    - get_payroll_status (month, year) → TABLE UIResponse
    - run_payroll_bulk → PROGRESS UIResponse → CONFIRM UIResponse
    - get_salary_slip (employee, month) → FORM UIResponse
    - [ ] *Gate:* "Run March payroll" triggers PROGRESS then CONFIRM before executing

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
