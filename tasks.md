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

**Three interaction modes (non-negotiable architecture):**

| Mode | Name | Who drives | AI role | When |
|---|---|---|---|---|
| 1 | **VEDA Auto** | VEDA | Primary — VEDA initiates, pre-fills, executes after HITL confirmation | Default for all daily operations |
| 2 | **VEDA Assist** | User (forms) | Co-pilot — pre-fills fields, flags compliance issues, answers inline questions | New users, complex records, setup |
| 3 | **Classic** | User (forms) | None — zero AI dependency | AI outage, credits exhausted, user preference |

All three modes write to the same Postgres tables via the same FastAPI endpoints.
No data silos between modes. A record created in Classic appears in VEDA Auto.
Mode is switchable per-session via the top bar. Default is VEDA Auto.
System automatically falls back to Classic when AI is unavailable.

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
    - [ ] *Gate:* Start a new conversation and ask the agent to list all tables via MCP.

---

## Phase 1: Agent Skills & Architecture Docs
- [x] **Task 1.1:** Create `ARCHITECTURE.md` at project root.
- [x] **Task 1.2:** Create `.agents/skills/fastapi-crud-generator/SKILL.md`
- [x] **Task 1.3:** Create `.agents/skills/erp-state-machine/SKILL.md`
- [x] **Task 1.4:** Create `.agents/skills/VEDA-api-contract/SKILL.md`
- [x] **Task 1.5:** Create `.agents/skills/indian-compliance/SKILL.md`
- [ ] **Task 1.6:** Archive old Supabase SQL drafts.
    - Move `supabase/20260223*` files to `reference/supabase_drafts/`
    - [ ] *Gate:* No `20260223*.sql` files in active `supabase/` migrations folder
- [x] **Task 1.7:** Create `.agents/skills/veda-ui-response/SKILL.md`
- [x] **Task 1.8:** Create `.agents/skills/veda-context/SKILL.md`
- [x] **Task 1.9:** Create `.agents/skills/frontend-card-system/SKILL.md`
- [x] **Task 1.10:** Create `.agents/skills/rls-security/SKILL.md`
- [x] **Task 1.11:** Create `.agents/skills/erp-relationships/SKILL.md`
- [x] **Task 1.12:** Create `.agents/skills/database-management/SKILL.md`
- [x] **Task 1.13:** Create `.agents/skills/rbac-and-scope/SKILL.md`
- [x] **Task 1.14:** Create `.agents/skills/finance-module/SKILL.md`
- [x] **Task 1.15:** Update `ARCHITECTURE.md` to reflect current state.
    - Update module status: Phase 3 VEDA layer complete, Phase 4 Mode 1 complete
    - Add three-mode architecture diagram and description
    - Add VEDA Assist panel pattern
    - Add Employee-User link pattern
    - [x] *Gate:* ARCHITECTURE.md module status matches actual codebase

---

## Phase 2: Backend MVP ✅ Complete

- [x] **Task 2.1–2.3:** Core Masters, Org Masters, Dependent Masters
    (Company, Currency, Holiday, Branch, Department, Designation,
    Employment Type, Gender, Salutation)
- [x] **Task 2.4:** Employee Master & Child Tables
    (Education, Internal/External Work History)
- [x] **Task 2.5a:** Leave Management (LeaveType, LeaveApplication)
- [x] **Task 2.5b:** Attendance Module
    (EmployeeCheckin, Attendance, AttendanceRequest — full state machines)
- [x] **Task 2.6:** Fix LeaveApplication — add POST /{id}/cancel
- [x] **Task 2.7:** Fix `dependencies.py` — real JWT decode
- [x] **Task 2.8:** Split `hr_masters/router.py` into domain files
- [x] **Task 2.9:** Payroll Module
    (SalaryComponent, SalaryStructure, SalarySlip, PF/ESI/PT/TDS,
    bulk-generate, submit, cancel)
- [x] **Task 2.9b:** UIResponse Pydantic Schema (7 types, all factory functions)
- [x] **Task 2.9c:** Active Record Context System (veda_context.py)
- [x] **Task 2.10:** User Authentication, RBAC & Org Scope (6 roles, permissions matrix)
- [x] **Task 2.11:** Finance Module
    (Client, Quote, Invoice, Payment — GST, state machines, RBAC)

### Backend Gaps — Must fix before first paying customer

**Option C Execution Sequence (agreed):**
Backend endpoints → Classic forms as testing harness → VEDA write tools against verified endpoints

```
2.12 → 2.13 → 4.9 → 4.10 → 4.11 → 3.4 → 4.12 → 4.13 → 4.14 → 2.14
PATCH  Auth   Shell  Setup  Emp    Write  Leave  Attend  Payroll  PDF
+link  endpts +nav   forms  forms  tools  forms  forms   forms
```

Rationale: Classic forms verify each endpoint works correctly. VEDA write
tools are built against proven endpoints — any failure is isolated to the
VEDA layer, not the backend. Task 2.14 (PDF) is non-blocking, done last.

- [ ] **Task 2.12:** Employee PATCH endpoint + User-Employee link
    *Currently POST /api/employees/ exists but PATCH /api/employees/{id} is missing.*
    *Also: when an employee is created, there is no corresponding User account.*
    *Without a User account, the employee cannot log in.*

    Changes required:
    - Add `PATCH /api/employees/{id}` endpoint — partial update, tenant-scoped
    - Add `POST /api/employees/{id}/create-account` endpoint:
      Creates a User record linked to the employee, sends invite email
      (or returns a temporary password for now)
    - User.employee_id and Employee.user_id FK both set atomically
    - [x] *Gate:* PATCH /api/employees/{id} updates name and department correctly
    - [x] *Gate:* create-account sets up User linked to employee, JWT works for that user

- [ ] **Task 2.13:** User Management Endpoints
    *Owners need to manage users — invite, deactivate, reset password, change role.*

    Endpoints required:
    - `GET /api/users/` — list all users in tenant (owner only)
    - `POST /api/users/invite` — create user + send invite (owner only)
    - `PATCH /api/users/{id}/role` — change role (owner only)
    - `POST /api/users/{id}/deactivate` — revoke access (owner only)
    - `POST /api/auth/login` — email + password → JWT
    - `POST /api/auth/refresh` — refresh token → new JWT
    - `POST /api/auth/change-password` — authenticated user changes own password
    - `POST /api/auth/reset-password` — owner resets any user's password
    - [ ] *Gate:* Owner invites HR manager, HR manager logs in with credentials
    - [ ] *Gate:* Owner deactivates user, subsequent JWT calls return 401

- [ ] **Task 2.14:** PDF Generation Service
    *Required for payslip download (Task 4.14) and offer letters (Phase 5).*

    - Add WeasyPrint or ReportLab to requirements.txt
    - Create `backend/app/utils/pdf_generator.py`
    - `POST /api/salary-slips/{id}/pdf` → returns PDF file
    - Template: company logo, employee details, earnings/deductions breakdown,
      PF/ESI/PT/TDS clearly separated, employer contributions shown
    - [ ] *Gate:* Salary slip PDF downloads with correct Indian compliance breakdown
    - [ ] *Gate:* PDF includes company name, employee name, month, net pay

---

## Phase 3: VEDA AI Layer

### ✅ Completed

- [x] **Task 3.1:** LangGraph Supervisor + list_employees tool
- [x] **Task 3.2:** HR Agent — Read & Approve Tools
    (get_employee, list_leave_applications, approve_leave,
    get_attendance_summary, get_my_permissions,
    helpers: resolve_employee_by_name, fetch_display_names)
- [x] **Task 3.3:** HR Agent — Payroll Tools
    (get_payroll_status, run_payroll_bulk HITL, get_salary_slip,
    payroll_agent.py wired into LangGraph)

### Write Tools (next priority)

- [ ] **Task 3.4:** VEDA HR Write Tools — Employee Lifecycle
    *Makes VEDA transactional, not just a dashboard.*
    *All tools return FORM UIResponse pre-filled. HITL wiring executes API call.*
    *Requires Task 2.12 (PATCH endpoint) AND Task 4.12 (employee forms) to be complete first.*
    *Classic forms are the testing harness — if the form works, the endpoint is proven.*
    *Build write tools only after the corresponding Classic form is verified end-to-end.*

    Tools:

    `add_employee_tool` (Owner / HR Manager)
    - Extracts: name, joining date, department, designation, employment type
    - Returns FORM UIResponse, veda_filled=True on extracted fields
    - FK pickers: department_id, designation_id, employment_type_id
    - Submit: POST /api/employees/
    - [ ] *Gate:* "Add Rahul Sharma joining April 1 as Software Engineer" → FORM pre-filled

    `update_employee_tool` (Owner / HR Manager)
    - Uses open_record_id context or name disambiguation
    - Returns FORM with current values pre-loaded, changed fields highlighted
    - Submit: PATCH /api/employees/{id}
    - [ ] *Gate:* "Change Dev Patel's department to Engineering" → FORM with dept pre-changed

    `apply_for_leave_tool` (Employee — self only)
    - Extracts: leave_type name, from_date, to_date, reason
    - Fetches available leave types to validate leave_type name
    - Returns FORM UIResponse pre-filled
    - Submit: POST /api/leave-applications/ → POST /{id}/submit
    - [ ] *Gate:* "Apply for casual leave April 3 to 5" → FORM pre-filled with correct type

    `cancel_leave_tool` (Employee — own open/approved leaves)
    - Lists employee's cancellable leaves first
    - Returns CONFIRM UIResponse before cancelling
    - Submit: POST /api/leave-applications/{id}/cancel
    - [ ] *Gate:* "Cancel my leave for April 3" → CONFIRM → cancelled → balance restored

    `get_leave_balance_tool` (All roles — org scoped)
    - Aggregates leave applications to compute remaining days per type
    - Returns TEXT UIResponse with breakdown per leave type
    - [ ] *Gate:* "What's my leave balance?" → TEXT showing days remaining per type

    `submit_payroll_tool` (Owner / HR Manager)
    - Lists all draft slips for month with totals
    - Returns CONFIRM UIResponse with employee count + total net pay
    - Submit: POST /api/salary-slips/{id}/submit for each draft slip
    - [ ] *Gate:* "Submit March payroll" → CONFIRM with total, submits all on confirm

    `request_attendance_correction_tool` (Employee — self only)
    - Extracts: date, correct_status, reason
    - Returns FORM UIResponse pre-filled
    - Submit: POST /api/attendance-requests/ → POST /{id}/submit
    - [ ] *Gate:* "I was present March 25 but marked absent" → FORM pre-filled

    `approve_attendance_request_tool` (Manager / HR Manager)
    - Lists pending correction requests in visible scope
    - Returns APPROVAL UIResponse per request
    - Submit: POST /api/attendance-requests/{id}/approve
    - [ ] *Gate:* "Show pending attendance corrections" → APPROVAL cards list

    Supervisor updates:
    - Add all 8 tools to classify_intent() with parameter extraction
    - [ ] *Gate:* Supervisor correctly routes all 8 new intents

- [ ] **Task 3.5:** VEDA Master Data Tools
    *Lets owners configure system through conversation.*
    *Lower priority — Classic UI (Task 4.10) handles this too.*

    `create_department_tool`, `create_designation_tool`,
    `create_leave_type_tool`, `create_salary_structure_tool`
    (Owner / HR Manager — each returns FORM UIResponse)
    - [ ] *Gate:* "Create a department called Engineering" → FORM → saved → appears in pickers

- [ ] **Task 3.6:** Finance Agent
    Tools: list_clients, create_client, create_quote, create_invoice,
    list_invoices, record_payment, get_outstanding_summary
    - [ ] *Gate:* "Create invoice for Sharma Textiles ₹45,000 + GST" → FORM pre-filled
    - [ ] *Gate:* "Sharma paid ₹45,000 against INV-2526-004" → CONFIRM → recorded
    - [ ] *Gate:* "What's total outstanding this month?" → TEXT with amount

- [ ] **Task 3.7:** Policy Engine Schema
    *File:* `backend/app/modules/policy/models.py`
    Stores: approval thresholds, LOP rules, mandatory wait periods, chains
    VEDA queries at runtime — rules NOT hardcoded in prompts
    - [ ] *Gate:* PF/ESI thresholds, approval chains, LOP rules queryable via API

- [ ] **Task 3.8:** Setup / Onboarding Agent
    5-question VEDA Auto conversation → fully configured tenant
    Calls Task 3.5 tools internally (departments, designations, etc.)
    Requires TD-14 (company_type) resolved first
    - [ ] *Gate:* Fresh tenant → conversation → Company + Dept + Leave types + Salary structure

- [ ] **Task 3.9:** Personalised VEDA Greeting (Role-Aware)
    *Requires Task 3.4 (get_leave_balance_tool) to be complete.*
    On login, VEDA pre-fetches pending items scoped to role:
    - Owner: pending approvals count, payroll status, outstanding invoices, attendance summary
    - HR Manager: pending leave approvals, attendance anomalies, next payroll run date
    - Manager: pending team leave approvals, team attendance today
    - Employee: leave balance by type, last payslip status, pending corrections
    - [ ] *Gate:* Owner login → greeting includes real counts from DB
    - [ ] *Gate:* Employee login → shows only personal data, no other employees
    - [ ] *Gate:* Greeting uses get_leave_balance_tool for employee balance

---

## Phase 4: Frontend

### Mode 1 — VEDA Auto ✅ Complete
*4-panel IDE shell. VEDA drives. Human reviews and confirms.*

- [x] **Task 4.1:** IDE Shell + UIResponse Component Registry (7 card types)
- [x] **Task 4.2:** VEDA Chat Engine — live API, loading states, error handling
- [x] **Task 4.3:** Active Record Context Wiring — row click → VEDA knows context
- [x] **Task 4.4:** HITL Approval Flow — action buttons call FastAPI, VEDA continues
- [x] **Task 4.5:** VEDA Diff Attribution — purple tint on VEDA-filled fields
- [x] **Task 4.6:** Role-Aware VEDA Hint Chips

- [ ] **Task 4.1b:** Shell Redesign — VEDA Right Panel + ERP Center + Explorer
    *The current 4-panel IDE layout has VEDA chat in the center. That is wrong.*
    *The correct architecture mirrors Antigravity IDE: center is ERP content,*
    *right panel is the AI agent (VEDA). Auto/Assist is a panel-level toggle.*

    **Layout:**
    ```
    ┌──────┬──────────────┬──────────────────────────────────────┬───────────────────┐
    │      │              │  Employees │ Dev Patel │ INV-004 │ + │  VEDA  [Auto ▾]   │
    │  A   │   EXPLORER   ├────────────┴──────────┴─────────┴────┤                   │
    │  C   │   (module    │                                      │  Chat messages    │
    │  T   │    tree)     │      ERP CONTENT                     │  Cards inline     │
    │  I   │              │                                      │  Action results   │
    │  V   │              │  Default: Welcome / onboarding       │                   │
    │  I   │              │  Or: DataTable list page              │                   │
    │  T   │              │  Or: Record detail form               │                   │
    │  Y   │              │                                      │  [Ask VEDA...]    │
    └──────┴──────────────┴──────────────────────────────────────┴───────────────────┘
     48px    260px                    flex: 1                        340px
    ```

    **Key architectural decisions:**
    - Center panel = ERP content ONLY (list pages, record forms, welcome screen)
    - Right panel = VEDA AI agent (chat + cards + actions + context indicator)
    - Auto / Assist = dropdown toggle in VEDA panel header, NOT a top-bar mode
    - Classic = VEDA panel collapsed/hidden, ERP works independently
    - No VEDA tab in the tab bar — tab bar is ERP content tabs only
    - No ModeSwitcher in top bar — replaced by dropdown in VEDA panel
    - Welcome screen shows when no ERP tabs are open (quick links, help, docs)

    **Auto vs Assist:**
    | Mode | VEDA can do |
    |---|---|
    | Auto | Pre-fill forms, execute HITL actions, open records, run payroll |
    | Assist | Answer questions, show data, explain rules. NO action buttons. View-only. |

    **Sub-tasks:**
    - 4.1b-A: Component architecture + shell layout + explorer + tab system +
              VEDA panel with Auto/Assist dropdown + welcome screen
    - 4.1b-B: Resize handles + toggle animation + localStorage persistence +
              tab overflow scroll + keyboard shortcuts

    **What does NOT change:**
    - All card components (InlineTable, InlineForm, ApprovalCard, etc.)
    - All VEDA backend and AI layer
    - UIResponse schema
    - RBAC module visibility rules

    - [ ] *Gate 1:* Explorer panel renders module tree (HRMS, Payroll, Finance, Settings)
    - [ ] *Gate 2:* Explorer panel drag-resize works (180px–400px), persists after refresh
    - [ ] *Gate 3:* Explorer panel toggle collapses/expands with animation, persists
    - [ ] *Gate 4:* Clicking "Employees" in explorer opens Employees list tab in center
    - [ ] *Gate 5:* Clicking a record row opens record in new tab in center
    - [ ] *Gate 6:* Active tab record context auto-passed to VEDA panel
    - [ ] *Gate 7:* VEDA panel shows chat with Auto/Assist dropdown toggle
    - [ ] *Gate 8:* Auto mode: action buttons render on VEDA cards
    - [ ] *Gate 9:* Assist mode: NO action buttons, view-only
    - [ ] *Gate 10:* VEDA panel drag-resize works (280px–500px), persists
    - [ ] *Gate 11:* VEDA panel toggle collapses/expands (= Classic mode)
    - [ ] *Gate 12:* Tab overflow scrolls horizontally with 5+ tabs open
    - [ ] *Gate 13:* Welcome screen renders when no tabs open (quick links, help section)

- [ ] **Task 4.0:** Authentication Pages
    *Blocks everything else — without login, no real user can access the product.*
    *Requires Task 2.13 (auth endpoints) to be complete first.*

    Pages:
    - Login page: email + password → calls POST /api/auth/login → stores JWT
    - Forgot password page: email → triggers reset flow
    - Change password page: authenticated user
    - First login / set password: when invited user logs in for first time

    JWT storage: httpOnly cookie (not localStorage — security requirement)
    Auto-redirect to login if JWT missing or expired
    Auto-redirect to dashboard after successful login

    - [ ] *Gate:* Owner logs in with email/password, gets to VEDA Auto dashboard
    - [ ] *Gate:* Expired JWT → auto-redirect to login, no blank page
    - [ ] *Gate:* Wrong password → clear error message, no token stored

### Design System Foundation (prerequisite for all Classic + VEDA Assist pages)

- [x] **Task 4.7a:** Design System Migration
    *Must be completed before Task 4.7 and all subsequent frontend tasks.*
    *Establishes the visual foundation that every Classic and VEDA Assist page builds on.*
    *VEDA Auto dark shell is NOT touched.*

    Part 1 — shadcn/ui initialisation:
    - `npx shadcn@latest init` with New York style, Blue base color, CSS variables on
    - Blue base: primary `221.2 83.2% 53.3%` — consistent with Linear/Supabase/Vercel aesthetic

    Part 2 — Install all required shadcn components and blocks:
    - Core components: button, input, label, form, select, textarea, checkbox,
      radio-group, switch, badge, card, separator, dialog, sheet, dropdown-menu,
      popover, tooltip, toast, alert, avatar, tabs, table, skeleton, scroll-area,
      calendar, date-picker, breadcrumb, progress
    - Sidebar component: `npx shadcn add sidebar`
    - Blocks: `sidebar-07` (Classic/VEDA Assist nav shell),
              `sidebar-15` (VEDA Assist dual-panel layout),
              `dashboard-01` (owner home — KPI cards + chart + DataTable),
              `login-04` (login page — split layout)
    - TanStack Table: `npm install @tanstack/react-table`

    Part 3 — Update globals.css with Udoo design tokens:
    - Light theme (`:root`): white background, blue primary, blue-grey borders
    - Dark theme (`.dark`): existing VEDA Auto dark shell preserved
    - Custom tokens: `--veda-fill` (purple, intentionally distinct from blue brand)
    - Status colour tokens: active/inactive/pending/approved/rejected/draft/submitted

    Part 4 — Create `frontend/lib/design-system.ts`:
    - Badge variant maps for all domain statuses (leave, payroll, employee,
      attendance, invoice)
    - VEDAMode type and labels
    - NAV_MODULES config (used by sidebar in Tasks 4.7 and 4.9)
    - `formatINR()` — Indian number formatting
    - `formatDate()` — Indian date formatting

    - [x] *Gate:* `components.json` shows style: new-york, baseColor: blue
    - [x] *Gate:* At least 25 component files in `frontend/components/ui/`
    - [x] *Gate:* `@tanstack/react-table` present in package.json
    - [x] *Gate:* `globals.css` contains `--veda-fill`, `--primary`, `--sidebar-primary`
    - [x] *Gate:* `frontend/lib/design-system.ts` exists with 100+ lines

### Mode 2 — VEDA Assist

- [x] **Task 4.7:** Mode Switcher + Shell Routing
    Top bar: VEDA Auto | VEDA Assist | Classic
    - VEDA Auto: 4-panel IDE shell
    - VEDA Assist: left sidebar + main content + VEDA co-pilot right panel
    - Classic: left sidebar + main content, no VEDA panel
    Mode stored in localStorage. Persists across page refreshes.
    - [x] *Gate:* Switching modes changes layout without page reload
    - [x] *Gate:* Mode persists after browser refresh
    - [x] *Gate:* RBAC enforced in all three modes identically

- [x] **Task 4.8:** VEDA Assist Panel Component
    *Right-side co-pilot attached to every form page.*
    *Calls POST /api/veda/chat with form context on each interaction.*

    Behaviours:
    - Form open → VEDA greets with record context
    - Field focus → VEDA suggests valid values
    - FK field → VEDA shows matching options as user types
    - Pre-save → VEDA runs compliance check (PF ceiling, ESI threshold, etc.)
    - Inline Q&A: user asks questions without leaving the form
    - VEDA responses in panel — never interrupt the form

    - [x] *Gate:* Employee form in VEDA Assist → panel shows context greeting
    - [x] *Gate:* Basic salary < 50% CTC → VEDA flags before save
    - [x] *Gate:* "What documents does a new employee need?" → VEDA answers in panel

### Mode 3 — Classic (+ shared form pages for VEDA Assist)

- [ ] **Task 4.9:** Classic Shell + Navigation
    Left sidebar, RBAC-scoped sections:
    - HRMS: Employees, Leave, Attendance
    - Payroll: Salary Structures, Salary Slips
    - Finance: Clients, Quotes, Invoices, Payments
    - Setup: Company, Departments, Designations, Leave Types,
              Salary Components, Employment Types, Branches, Holiday List
    - Admin: Users (owner only)
    - [ ] *Gate:* All navigation renders, RBAC hides inaccessible sections
    - [ ] *Gate:* Same sidebar shell used for Classic and VEDA Assist

- [ ] **Task 4.10:** Setup / Master Data Pages
    *Foundation. Must complete before employee pages.*

    Pages (list + create + edit for each):
    - Company (edit only — single record, includes company_type after TD-14)
    - Departments
    - Designations
    - Employment Types
    - Branches
    - Leave Types (max_days, carry_forward, paid/unpaid flag)
    - Salary Components (earning/deduction, fixed/percentage, formula)
    - Salary Structures (link components, CTC breakdown)
    - Holiday List (year-wise, import from CSV)

    - [ ] *Gate:* Owner sets up dept → designation → leave type → salary structure in Classic
    - [ ] *Gate:* Same flow in VEDA Assist with co-pilot active

- [ ] **Task 4.11:** User Management Pages (Admin section — owner only)
    *Requires Task 2.13 backend.*

    Pages:
    - User list — shows all users, role, status (active/inactive), last login
    - Invite user form — email, role, linked employee (optional at invite time)
    - User detail — change role, deactivate, reset password, link to employee

    - [ ] *Gate:* Owner invites HR manager → HR manager receives credentials → logs in
    - [ ] *Gate:* Owner deactivates user → subsequent login fails with clear message

- [ ] **Task 4.12:** Employee Module Pages
    *Requires Task 4.10 (master data) and Task 2.12 (PATCH endpoint).*
    *Prerequisite for Task 3.4 (VEDA write tools) — verify all employee*
    *CRUD endpoints work through the form before building VEDA tools.*

    Pages:
    - Employee list — search, filter by status/dept/designation, paginated
    - Employee create form
    - Employee detail/edit — tabbed:
      Tab 1: Personal (name, DOB, gender, contact, address, emergency contact)
      Tab 2: Employment (joining date, dept, designation, employment type, manager)
      Tab 3: Payroll (salary structure, bank details, PF/ESI applicability, CTC)
      Tab 4: Documents (upload offer letter, Aadhaar, PAN, certificates)
      Tab 5: History (salary revisions, transfers, role changes — read only)
    - Employee deactivate / reactivate
    - Create user account button (links employee to login credentials)

    - [ ] *Gate:* HR adds complete employee with all 5 tabs in Classic
    - [ ] *Gate:* Employee immediately appears in VEDA Auto "show all employees"
    - [ ] *Gate:* Create account → employee can log in as employee role

- [ ] **Task 4.13:** Leave Module Pages

    Pages:
    - Leave applications list — filter by status/employee/date range
    - Apply for leave (employee self-service) — type dropdown, date picker, reason
    - Leave approval queue — manager/HR, bulk approve/reject with reason
    - Leave balance view — per employee, per type, days used/remaining
    - Leave calendar — monthly, colour-coded by leave type, team view

    - [ ] *Gate:* Employee applies in Classic → appears in manager queue
    - [ ] *Gate:* Manager bulk approves → balances update immediately
    - [ ] *Gate:* Same records visible in VEDA Auto

- [ ] **Task 4.14:** Attendance Module Pages

    Pages:
    - Attendance list — filter by employee/date/status
    - Bulk attendance entry — date + all employees for that day, mark status
    - Attendance correction request (employee self-service)
    - Correction approval queue (manager/HR)
    - Monthly attendance summary — present/absent/leave/half-day per employee

    - [ ] *Gate:* HR marks attendance for 10 employees for a date
    - [ ] *Gate:* Employee submits correction, manager approves, record updates
    - [ ] *Gate:* Monthly summary shows correct counts

- [ ] **Task 4.15:** Payroll Module Pages
    *Requires Task 2.14 (PDF generation).*

    Pages:
    - Payroll run — month/year/working days, generate with preview count
    - Salary slips list — filter by month/employee/status
    - Salary slip detail — full Indian compliance breakdown:
      Earnings: basic, HRA, special allowance, other allowances
      Deductions: PF employee (12%), ESI employee (0.75%), PT, TDS, LOP, advances
      Employer contributions: PF employer (12%), ESI employer (3.25%)
      Net pay
    - Bulk submit — review all drafts, one-click submit with total
    - Payslip PDF download — individual and bulk (zip)

    - [ ] *Gate:* HR generates, reviews, submits payroll end-to-end in Classic
    - [ ] *Gate:* PDF has correct PF/ESI/PT breakdown with employer contributions
    - [ ] *Gate:* Employee sees only their own slip

- [ ] **Task 4.16:** Finance Module Pages

    Pages:
    - Client list + create/edit (GSTIN, billing address, state code)
    - Quote list + create (line items, HSN/SAC codes, GST auto-calculation)
    - Quote detail — convert to invoice, mark sent, accept/reject/expire actions
    - Invoice list + create
    - Invoice detail — record payment (partial + full), mark sent, download PDF
    - Payment list — filter by client/date/amount

    - [ ] *Gate:* Finance manager creates invoice, IGST for inter-state in Classic
    - [ ] *Gate:* CGST+SGST auto-applied for intra-state
    - [ ] *Gate:* Partial payment → outstanding balance updates correctly

- [ ] **Task 4.17:** Notification Centre
    *In-app notifications for key events. Required before first paying customer.*

    Events that trigger notifications:
    - Leave approved/rejected → employee notified
    - Leave request pending → manager notified
    - Payroll generated → HR Manager notified
    - Attendance correction approved/rejected → employee notified
    - New employee added → HR Manager + owner notified
    - Invoice paid → finance manager notified

    Implementation:
    - `notifications` table in Postgres (tenant_id, user_id, type, message, read, created_at)
    - `GET /api/notifications/` — list unread for current user
    - `POST /api/notifications/{id}/read` — mark as read
    - Bell icon in top bar with unread count badge
    - Notification dropdown with list of recent alerts
    - In-app only for now; email/WhatsApp delivery in Phase 5

    - [ ] *Gate:* Leave approved → employee sees notification in bell icon
    - [ ] *Gate:* Unread count badge decrements on read
    - [ ] *Gate:* Notifications are tenant-isolated

- [ ] **Task 4.18:** AI Availability Detection + Auto Fallback to Classic

    Behaviour:
    - Frontend polls `GET /api/health` every 60 seconds
    - 2 consecutive failures → auto-switch to Classic mode
    - Amber top bar banner: "VEDA unavailable — Classic mode active"
    - VEDA Auto and VEDA Assist buttons greyed out, not hidden
    - Health restored → banner: "VEDA is back — switch to VEDA Auto?" (one click)
    - All Classic and VEDA Assist pages work during outage — zero degradation

    - [ ] *Gate:* Stop backend → banner appears within 2 minutes, Classic fully works
    - [ ] *Gate:* Restart backend → restore prompt appears, switching works
    - [ ] *Gate:* Context preserved when switching back to VEDA Auto

---

## Phase 5: Full HRMS Depth

- [ ] **Task 5.1:** Payroll Depth
    - LOP (Loss of Pay) — auto-deduct for unapproved absences before payroll run
    - Mid-month joiner/leaver proration — partial month salary calculation
    - Salary revision — effective date, retroactive arrears calculation
    - Advance salary — record and deduct from future payslip
    - PF ECR file generation (text file for EPFO portal upload)
    - ESI return file generation (half-yearly)
    - Form 16 generation (Part A from TDS traces + Part B salary computation)
    - Bank transfer file (NEFT/RTGS format — bank-specific templates)
    - Payslip bulk email delivery (per employee via SMTP)

- [ ] **Task 5.2:** Leave Depth
    - Leave balance ledger — proper credit/debit per transaction
    - Leave encashment — convert unused days to payout on resignation/year-end
    - Carry-forward rules — max days rollover, auto-lapse remainder
    - Comp-off — create compensatory off from overtime/holiday work
    - Leave calendar — organisation-wide, team view, conflict detection
    - Half-day leave — morning/afternoon distinction
    - Multi-level approval chains — employee → manager → HR → configurable

- [ ] **Task 5.3:** Attendance Depth
    - Shift management — morning/evening/night, rotational shifts
    - Shift roster — per employee per week assignment
    - Late mark rules — grace period (e.g. 15 min), half-day threshold
    - Overtime recording and calculation
    - GPS/selfie attendance — mobile-first for field staff
    - Biometric device integration — webhook receiver for punches
    - Weekly off configuration — Sunday only, Saturday-Sunday, custom

- [ ] **Task 5.4:** Expense Management
    - Expense claim creation — employee submits with category and amount
    - Receipt upload — image/PDF attachment
    - Approval workflow — manager → finance manager
    - Reimbursement recording — mark as paid
    - Payroll integration — approved expenses added to salary slip as non-taxable
    - Expense policy — per-category limits, VEDA checks against policy

- [ ] **Task 5.5:** Full Accounting Module
    - Chart of accounts — standard Indian COA template
    - Journal entries — manual + auto-generated from payroll/invoices
    - P&L statement — monthly/quarterly/annual
    - Balance sheet
    - Bank reconciliation
    - GST returns — GSTR-1 (outward supplies), GSTR-3B (summary)
    - TDS returns — Form 24Q (salary TDS), Form 26Q (contractor TDS)
    - TDS certificate generation — Form 16A for vendors

- [ ] **Task 5.6:** Recruitment / ATS
    - Job posting — internal + external (Naukri/LinkedIn export)
    - Candidate pipeline — applied → screened → interviewed → offered → joined
    - Interview scheduling — calendar integration
    - Offer letter generation — PDF with salary breakup
    - Seamless handoff to employee onboarding on acceptance

- [ ] **Task 5.7:** Performance Management
    - Goal setting — OKRs or KRA/KPI framework, configurable per company
    - Mid-year and annual review cycles
    - 360° feedback — self, manager, peer, subordinate
    - Performance rating scale — configurable (1-5, A-E, etc.)
    - Performance-linked increment workflow — rating → increment % → salary revision

- [ ] **Task 5.8:** Reporting & Compliance Dashboard
    - Headcount reports — by dept, designation, location, employment type
    - Attrition reports — monthly, quarterly, department-wise
    - Payroll cost reports — CTC vs gross vs net, employer cost
    - Compliance calendar — PF/ESI/PT/TDS due dates with reminder alerts
    - Statutory reports — PF Form 12A, ESI Form 6, PT challan
    - Custom report builder — drag-and-drop fields, export CSV/PDF
    - Target: 50+ standard reports at launch, 100+ by v2

- [ ] **Task 5.9:** Data Import / Migration
    *Required for any SME switching from Excel or another HRMS.*
    - Employee bulk import — CSV template with validation
    - Leave balance import — opening balances when switching mid-year
    - Attendance history import — last 12 months
    - Salary history import — last 6 months for arrears/Form 16
    - Validation report before import — show errors, allow correction
    - [ ] *Gate:* Import 50 employees from CSV, all fields map correctly

- [ ] **Task 5.10:** Notification Delivery (Email + WhatsApp)
    *Extends Task 4.17 in-app notifications to external channels.*
    - Email delivery — SMTP integration, per-event templates
    - WhatsApp delivery — leave approved, payslip ready, attendance alert
      (Indian SMEs operate primarily on WhatsApp — key retention feature)
    - Notification preferences — user can choose channel per event type
    - Bulk announcements — HR broadcasts to all employees

- [ ] **Task 5.11:** Mobile PWA
    *Indian factory workers and field staff use phones exclusively.*
    - Progressive Web App — installable on Android/iOS
    - Mobile-optimised views for: leave application, attendance marking,
      payslip view, notification centre
    - Offline support for attendance marking (sync when connected)

- [ ] **Task 5.12:** CRM & Sales
    - Lead management — source, status, assigned to
    - Opportunity tracking — stage, value, close date
    - Full Quote-to-Cash — lead → quote → invoice → payment
    - Integration with Finance module (invoices flow into accounting)

---

## Ongoing: Technical Debt & Hardening

- [x] **TD-1:** Real JWT decode in `dependencies.py`
- [ ] **TD-2:** Database-level RLS via `current_setting('app.current_tenant_id')`
      in Alembic migrations. Currently only app-level filtering.
- [ ] **TD-3:** Audit log table wired to all transactional tables via SQLAlchemy events.
      Every create/update/delete records who did it and when.
- [ ] **TD-4:** Add `Field(description="...")` to all Pydantic schemas.
      Required for VEDA agent accuracy — Claude reads field descriptions.
- [x] **TD-5:** Performance — replace deep Employee eager loads with EmployeeSummary schema
- [x] **TD-6:** Add POST /leave-applications/{id}/cancel endpoint
- [ ] **TD-7:** Policy engine not built — approval thresholds not queryable via API
- [x] **TD-8:** UIResponse schema wired to LangGraph output
- [x] **TD-9:** Direct fetch streaming implemented
- [x] **TD-10:** VEDA diff attribution (purple tint) implemented
- [x] **TD-11:** Frontend shell uses correct 4-panel IDE layout
- [ ] **TD-12:** Permission checks missing from existing HRMS/Payroll endpoints
      (only endpoints from Task 2.11+ have require_permission).
      Add to all existing endpoints before first paying customer.
- [ ] **TD-13:** Org scope filtering not applied to all list endpoints.
      Add get_visible_employee_ids() to all list endpoints before first paying customer.
- [ ] **TD-14:** `company_type` field missing from Company model.
      Options: sole_proprietorship, partnership, llp, private_limited,
      public_limited, opc, section_8, trust, government.
      Nullable column, Alembic migration required.
      Required for Task 3.8 onboarding agent and PF/ESI compliance thresholds.
- [ ] **TD-15:** Payroll bulk-generate uses company-level salary structure.
      Fix: use employee.salary_structure_id, fall back to company default.
- [ ] **TD-16:** JWT tokens expire after 7 days.
      Production: implement proper refresh token flow (Task 2.13 covers this).
- [ ] **TD-17:** Supabase free tier pauses after 7 days inactivity.
      Production: upgrade to paid plan. Dev: document resume process.
- [ ] **TD-18:** Log files must never be committed.
      Verify *.log in .gitignore, add pre-commit hook to block log files.
- [ ] **TD-19:** CORS currently allows only localhost:3000.
      Production: update to actual domain, remove localhost from allowed origins.
- [ ] **TD-20:** No rate limiting on API endpoints.
      Add per-tenant rate limiting before first paying customer.
      Reference: COST_SCENARIO_STUDY.md rate limit recommendations.
- [ ] **TD-21:** No input sanitisation beyond Pydantic validation.
      Add SQL injection protection audit, XSS prevention on text fields.
- [ ] **TD-22:** Secrets in .env not rotated since project start.
      Rotate JWT_SECRET_KEY and DATABASE_URL password before first paying customer.