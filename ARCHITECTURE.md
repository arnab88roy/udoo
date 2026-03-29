# Task 1.15 — Update ARCHITECTURE.md

## CONTEXT

This is a documentation-only task. No code changes.
Read the current ARCHITECTURE.md before making any edits.

---

## TASK

Replace the contents of `ARCHITECTURE.md` at the repo root with
the exact content below. Do not modify any other file.

---

## NEW CONTENT FOR ARCHITECTURE.md

Paste this as the complete file:

```markdown
# Udoo ERP — Architecture Reference

---

## Repository

**GitHub (Public):** https://github.com/arnab88roy/udoo
**Raw file access:** https://raw.githubusercontent.com/arnab88roy/udoo/main/

To read any file directly:
  https://raw.githubusercontent.com/arnab88roy/udoo/main/{path/to/file}

Examples:
  https://raw.githubusercontent.com/arnab88roy/udoo/main/tasks.md
  https://raw.githubusercontent.com/arnab88roy/udoo/main/ARCHITECTURE.md
  https://raw.githubusercontent.com/arnab88roy/udoo/main/backend/app/modules/finance/models.py
  https://raw.githubusercontent.com/arnab88roy/udoo/main/.agents/skills/finance-module/SKILL.md

---

## Product Vision
AI-first B2B SaaS ERP for Indian SMEs.
Primary interface is VEDA chat, not forms.
Competing with Odoo/ERPNext on simplicity + AI + zero setup friction.

---

## Core Product Philosophy

### The Conversation IS the ERP
VEDA does not link to records — it renders them inline as interactive
cards inside the conversation. Traditional module screens are the
escape hatch for power users, not the primary interface.

### The Cursor Analogy
Udoo is to business operations what Cursor is to coding.
The human and VEDA are co-authors of the same business record.
Neither blocks the other. The record does not care who filled which field.

### Co-Authorship Rules
1. No silos — every VEDA action writes to the same Postgres tables the form UI reads from
2. Interruptible — human can take over mid-task, VEDA can take over a human-started task
3. Transparent diffs — VEDA-filled fields carry visual attribution (purple tint)

---

## Three Interaction Modes

| Mode | Name | Who drives | AI role | When |
|---|---|---|---|---|
| 1 | **VEDA Auto** | VEDA | Primary — VEDA initiates, pre-fills, executes after HITL confirmation | Default for all daily operations |
| 2 | **VEDA Assist** | User (forms) | Co-pilot — pre-fills fields, flags compliance, answers inline questions | New users, complex records, setup |
| 3 | **Classic** | User (forms) | None — zero AI dependency | AI outage, credits exhausted, user preference |

All three modes write to the same Postgres tables via the same FastAPI endpoints.
Mode is switchable per-session via the top bar. Default is VEDA Auto.
System automatically falls back to Classic when AI is unavailable.

### VEDA Assist Panel Pattern
In VEDA Assist mode, a co-pilot panel appears on the right side of every form.
It calls POST /api/veda/chat with the current form context.
Behaviours:
- On form open: VEDA greets with record context
- On field focus: VEDA suggests valid values
- Pre-save: VEDA runs compliance check (PF ceiling, ESI threshold, etc.)
- Inline Q&A: user asks questions without leaving the form
VEDA responses appear in the panel — they never interrupt the form itself.

---

## Security Model

### Authentication
- Login: POST /api/auth/login (email + password → JWT)
- Token: python-jose HS256, carries user_id + tenant_id + role + employee_id + company_id
- Storage: httpOnly cookie (not localStorage)
- Refresh: POST /api/auth/refresh → new JWT
- Expiry: configurable, default 24h

### Six Roles
| Role | HRMS | Payroll | Finance | Settings | CRM | Tasks |
|---|---|---|---|---|---|---|
| owner | Full | Full | Full | Full | Full | Full |
| hr_manager | Full | Full | None | Partial | None | Full |
| finance_manager | None | View+Approve | Full | Partial | Full | Full |
| manager | View+Approve (team only) | None | None | None | View+Create | Full |
| employee | Self only | View self | None | None | None | Own tasks |
| auditor | View all | View all | View all | View all | View all | View all |

### Permission Check Pattern
Every protected endpoint uses:
```python
require_permission(current_user, "module_name", "action")
# action: view, create, edit, submit, approve, delete
```

### Org Scope Pattern
Every list endpoint for manager/employee roles uses:
```python
visible_ids = await get_visible_employee_ids(db, current_user, tenant_id)
if visible_ids is not None:
    query = query.where(Employee.id.in_(visible_ids))
```

### Employee-User Link Pattern
Every employee has an optional linked User account.
When HR creates an employee, they can call:
  POST /api/employees/{id}/create-account
This creates a User record with:
- employee_id → Employee.id (FK)
- User.role = "employee" by default
- hashed_password set, credentials sent to employee
Employee model: employee.user_id → User.id
User model: user.employee_id → Employee.id
Both FKs use use_alter=True to avoid circular dependency.
An employee without a User account cannot log in.

### Audit Trail
created_by and modified_by are auto-populated on every record
via SQLAlchemy events reading from current_user_id_ctx ContextVar.
No manual passing required in individual endpoints.

### VEDA Personalisation
VEDA's system prompt is dynamically assembled per user from:
1. Identity: name, designation, company
2. Permissions: which modules and actions are available
3. Scope: which employees/records are visible
4. Context: active record open in the editor
5. Mode: VEDA Auto vs VEDA Assist

---

## Tech Stack
- Backend: FastAPI async, SQLAlchemy, Pydantic
- Database: Supabase PostgreSQL, RLS via tenant_id
- Migrations: Alembic (single source of truth — never Supabase SQL editor)
- JWT: python-jose, HS256, httpOnly cookie storage
- Auth: bcrypt password hashing, python-jose JWT, refresh token flow
- RBAC: Custom permission matrix in permissions.py
- Org scope: PostgreSQL recursive CTEs via SQLAlchemy text()
- AI: LangGraph supervisor + domain agents (HR agent, Payroll agent)
- Frontend: Next.js 16, Tailwind CSS, shadcn/ui, Lucide
- PDF: WeasyPrint/ReportLab for payslip and document generation

---

## Core Rules (Non-Negotiable)
1. Every table has tenant_id — always filter by it
2. Transactional tables have docstatus (0=Draft, 1=Submitted, 2=Cancelled)
3. Child tables are relational — never JSONB
4. Alembic is the only migration system
5. Modules are isolated — no cross-module DB joins
6. AI agents call the same FastAPI endpoints humans use
7. UIResponse is the only valid output from VEDA — never plain text for actions
8. JWT tenant_id always overwrites client-supplied tenant_id
9. Credentials never committed to git — always in .env

---

## Current Module Status

### Backend ✅ All Complete
- core_masters: ✅ Complete (Company, Currency, Holiday, Gender, Salutation)
- org_masters: ✅ Complete (Branch, Department, Designation, Employment Type)
- hr_masters/employee: ✅ Complete (Employee + child tables)
- hr_masters/leave: ✅ Complete (LeaveType, LeaveApplication — full state machine)
- hr_masters/attendance: ✅ Complete (EmployeeCheckin, Attendance, AttendanceRequest)
- payroll: ✅ Complete (SalaryComponent, SalaryStructure, SalarySlip, PF/ESI/PT/TDS)
- finance: ✅ Complete (Client, Quote, Invoice, Payment — GST, state machines)
- ui_response_schema: ✅ Complete (backend/app/schemas/ui_response.py — 7 types)
- veda_chat_endpoint: ✅ Live at POST /api/veda/chat
- veda_context_system: ✅ Complete (backend/app/utils/veda_context.py)
- rbac_and_auth: ✅ Complete (Task 2.10 — 6 roles, permissions matrix)
- org_scope_queries: ✅ Complete (recursive CTE, get_visible_employee_ids)

### Backend — Pending
- auth_endpoints: 📋 Task 2.13 — login, refresh, invite, user management
- employee_patch: 📋 Task 2.12 — PATCH /api/employees/{id}, create-account endpoint
- pdf_generation: 📋 Task 2.14 — payslip PDF, WeasyPrint

### VEDA AI Layer
- veda_supervisor: ✅ Complete (LangGraph, classify_intent, Claude Sonnet)
- hr_agent: ✅ Complete (list_employees, get_employee, list_leave_applications,
                         approve_leave, get_attendance_summary, get_my_permissions)
- payroll_agent: ✅ Complete (get_payroll_status, run_payroll_bulk HITL, get_salary_slip)
- helpers: ✅ Complete (resolve_employee_by_name, fetch_display_names)
- hr_write_tools: 📋 Task 3.4 — add_employee, update_employee, apply_for_leave,
                               cancel_leave, get_leave_balance, submit_payroll,
                               request_attendance_correction, approve_attendance_request
- master_data_tools: 📋 Task 3.5 — create_department, create_designation, etc.
- finance_agent: 📋 Task 3.6
- policy_engine: 📋 Task 3.7
- onboarding_agent: 📋 Task 3.8
- veda_greeting: 📋 Task 3.9

### Frontend
- veda_auto_shell: ✅ Complete (4-panel IDE shell, Task 4.1–4.6)
- veda_auto_chat: ✅ Complete (live API, HITL, context wiring, diff attribution)
- auth_pages: 📋 Task 4.0 — login, forgot password, change password
- mode_switcher: 📋 Task 4.7 — VEDA Auto | VEDA Assist | Classic top bar
- veda_assist_panel: 📋 Task 4.8 — co-pilot panel for forms
- classic_shell: 📋 Task 4.9 — left sidebar navigation
- setup_pages: 📋 Task 4.10 — master data CRUD
- user_management_pages: 📋 Task 4.11 — invite, role, deactivate
- employee_pages: 📋 Task 4.12 — 5-tab employee detail
- leave_pages: 📋 Task 4.13
- attendance_pages: 📋 Task 4.14
- payroll_pages: 📋 Task 4.15
- finance_pages: 📋 Task 4.16
- notification_centre: 📋 Task 4.17
- ai_fallback: 📋 Task 4.18

---

## Frontend Architecture

### VEDA Auto Shell (current)
Four panels (non-negotiable for VEDA Auto mode):
- Activity bar (48px) — module switcher, RBAC-aware icons
- Left panel (240px) — record navigator, recent records, live badge counts
- Center panel (flex:1) — VEDA conversation, inline card rendering
- Right panel (300px) — record inspector, active record type/ID/module

```
┌────┬─────────────────────────────────────────────────────┐
│    │                TOP BAR (48px)                        │
│ A  ├──────────────┬──────────────────┬───────────────────┤
│ C  │              │                  │                   │
│ T  │  LEFT PANEL  │  CENTER PANEL    │   RIGHT PANEL     │
│ I  │  (record     │  ← VEDA CHAT →   │   (record         │
│ V  │   navigator, │  inline cards    │    inspector,     │
│ I  │   badges,    │  render here     │    audit trail)   │
│ T  │   reports)   │                  │                   │
│ Y  │              │                  │                   │
│    │  240px       │  flex: 1         │  300px            │
└────┴──────────────┴──────────────────┴───────────────────┘
 48px
```

### VEDA Assist / Classic Shell (pending)
Two panels:
- Left sidebar (240px) — module navigation, RBAC-aware
- Main content (flex:1) — form pages and list pages
- Right panel (300px, VEDA Assist only) — VEDA co-pilot panel

### UIResponse Contract
Every VEDA response is a typed UIResponse object.
The frontend has a component registry keyed to response types.
Plain text is NEVER returned for actionable operations.

Types: `TABLE | FORM | APPROVAL | BLOCKER | CONFIRM | PROGRESS | TEXT`

Component registry (all built, Task 4.1):
- TABLE → `<InlineTable />` — clickable rows set active record context
- FORM → `<InlineForm />` — VEDA-filled fields show purple tint
- APPROVAL → `<ApprovalCard />` — Approve + Reject actions
- BLOCKER → `<BlockerCard />` — explains why VEDA cannot proceed
- CONFIRM → `<ConfirmCard />` — requires explicit confirmation before execution
- PROGRESS → `<ProgressCard />` — step-by-step long-running operations
- TEXT → `<TextMessage />` — greetings, answers, hint chips

### Active Record Context
The open record (type + ID) is passed to VEDA on every message.
VEDA never needs to be told what record the user is looking at.
Context: `{ open_record_type, open_record_id, open_module, tenant_id }`
Clicking a table row sets open_record_id in the frontend state.
Context flows from frontend → sanitise_request_context() → LangGraph.

### HITL (Human-in-the-Loop) Pattern
VEDA never directly executes write operations.
For every action:
1. VEDA returns CONFIRM or APPROVAL card with action button
2. Human clicks the button
3. Frontend calls the FastAPI endpoint directly
4. On success, frontend sends follow-up message to VEDA
5. VEDA acknowledges and continues conversation
This ensures human is always in control of data mutations.

---

## VEDA AI Architecture

```
POST /api/veda/chat
        ↓
sanitise_request_context()  ← JWT tenant_id always wins
get_current_user()
        ↓
build_initial_state()  ← AgentState TypedDict
        ↓
LangGraph Graph
        ↓
supervisor_node
  ├── classify_intent() ← Claude Sonnet, JSON output
  ├── permission check
  └── route to agent
        ↓
hr_agent_node          payroll_agent_node     (future agents)
  ↓                       ↓
HR_TOOLS             PAYROLL_TOOLS
  ↓                       ↓
tool_fn(db, user, context, **params)
  ↓
UIResponse
```

### State Schema (AgentState)
Immutable: message, context, user, conversation_history, tenant_id
Mutable: current_agent, tool_name, tool_params, response, error

### Tool Pattern
Every tool function signature:
```python
async def {name}_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    **params,
) -> UIResponse:
```
Tools NEVER call other endpoints. They query the DB directly.
Tools NEVER execute mutations. They return FORM/CONFIRM/APPROVAL cards.
The frontend executes mutations via HITL button clicks.

### Disambiguation Pattern
When a tool needs to find an employee by name:
- 0 matches → BLOCKER response
- 1 match → proceed with that employee
- 2+ matches → TABLE response for user to pick (record_type="employee")
See: backend/app/veda/tools/helpers.py → resolve_employee_by_name()

### Display Name Resolution
Raw UUIDs are never shown to users in table rows.
Before building rows, call fetch_display_names() to batch-resolve:
- designation_id → designation_name
- department_id → department_name
- employee_id → employee_name
- leave_type_id → leave_type_name
See: backend/app/veda/tools/helpers.py → fetch_display_names()

---

## Key File Locations

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, CORS, all router includes
│   ├── dependencies.py            # get_tenant_id(), get_current_user()
│   ├── db/database.py             # AsyncSessionLocal, engine, ContextVar
│   ├── modules/
│   │   ├── core_masters/          # Company, Currency, Holiday, Gender, Salutation
│   │   ├── org_masters/           # Branch, Department, Designation, Employment Type
│   │   ├── hr_masters/
│   │   │   ├── models.py          # Employee, LeaveType, LeaveApplication,
│   │   │   │                      # Attendance, AttendanceRequest, EmployeeCheckin
│   │   │   └── routers/
│   │   │       ├── employees.py
│   │   │       ├── leave.py
│   │   │       └── attendance.py
│   │   ├── payroll/               # SalaryComponent, SalaryStructure, SalarySlip
│   │   └── finance/               # Client, Quote, Invoice, Payment
│   ├── schemas/
│   │   ├── ui_response.py         # UIResponse, all 7 types, factory functions
│   │   └── user_context.py        # UserContext dataclass, role properties
│   ├── utils/
│   │   ├── permissions.py         # DEFAULT_PERMISSIONS, check_permission()
│   │   ├── org_scope.py           # get_visible_employee_ids() recursive CTE
│   │   └── veda_context.py        # build_context(), sanitise_request_context()
│   └── veda/
│       ├── state.py               # AgentState TypedDict, build_initial_state()
│       ├── graph.py               # LangGraph build, veda_graph singleton
│       ├── supervisor.py          # supervisor_node, classify_intent()
│       ├── prompts.py             # describe_user()
│       ├── agents/
│       │   ├── hr_agent.py        # HR_TOOLS registry, hr_agent_node
│       │   └── payroll_agent.py   # PAYROLL_TOOLS registry, payroll_agent_node
│       └── tools/
│           ├── helpers.py         # resolve_employee_by_name, fetch_display_names
│           ├── hr_tools.py        # All HR tool functions
│           └── payroll_tools.py   # All Payroll tool functions
frontend/
├── app/
│   ├── globals.css                # Design tokens (CSS variables)
│   └── page.tsx                  # VEDA Auto shell + chat engine
├── components/veda/
│   ├── VEDACard.tsx               # UIResponse component registry dispatcher
│   ├── VEDAMessage.tsx            # Message bubble (user + assistant)
│   └── cards/                    # All 7 card components + ActionButton
├── lib/
│   └── veda-client.ts            # sendVEDAMessage(), executeAction(), buildNullContext()
└── types/
    └── ui-response.ts            # TypeScript types mirroring Python UIResponse
```
```

---

## VERIFICATION

After writing the file, run:
```bash
grep -c "VEDA Auto\|VEDA Assist\|Classic" ARCHITECTURE.md
```
Expected: at least 10 matches (the three mode names appear throughout).

```bash
grep "veda_ai_layer\|frontend_shell" ARCHITECTURE.md
```
Expected: zero matches (these stale entries must be gone).

```bash
grep "hr_write_tools\|resolve_employee_by_name\|fetch_display_names" ARCHITECTURE.md
```
Expected: all three appear in the file.

---

## COMMIT

```bash
git add ARCHITECTURE.md
git status
git commit -m "docs: Task 1.15 — update ARCHITECTURE.md to reflect current state"
```

Show full git output. DO NOT push — Arnab pushes manually.