# Udoo ERP — Architecture Reference

## Product Vision
AI-first B2B SaaS ERP for Indian SMEs.
Primary interface is VEDA chat, not forms.
Competing with Odoo/ERPNext on simplicity + AI.

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

## Security Model

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

### Audit Trail
created_by and modified_by are auto-populated on every record
via SQLAlchemy events reading from current_user_id_ctx ContextVar.
No manual passing required in individual endpoints.

### VEDA Personalisation
VEDA's system prompt is dynamically assembled per user from:
1. Identity: name, designation, company
2. Permissions: which modules and actions are available
3. Scope: which employees/records are visible
4. Context: active record open in the editor (Task 2.9c)

## Tech Stack
- Backend: FastAPI async, SQLAlchemy, Pydantic
- Database: Supabase PostgreSQL, RLS via tenant_id
- Migrations: Alembic (single source of truth)
- JWT: python-jose, HS256, tenant_id extracted from payload
- Auth: bcrypt for password hashing, python-jose for JWT
- RBAC: Custom permission matrix in permissions.py
- Org scope: PostgreSQL recursive CTEs via SQLAlchemy text()
- AI: LangGraph supervisor + domain agents
- Frontend: Next.js 16, Tailwind CSS, shadcn/ui, Lucide

## Core Rules
1. Every table has tenant_id — always filter by it
2. Transactional tables have docstatus (0/1/2)
3. Child tables are relational — never JSONB
4. Alembic is the only migration system
5. Modules are isolated — no cross-module DB joins
6. AI agents call the same FastAPI endpoints humans use

## Current Module Status

### Backend
- core_masters: ✅ Complete
- org_masters: ✅ Complete
- hr_masters/employee: ✅ Complete
- hr_masters/leave: ✅ Complete
- hr_masters/attendance: ✅ Complete
- payroll: ✅ Complete
- ui_response_schema: ✅ Complete (backend/app/schemas/ui_response.py)
- veda_chat_endpoint: ✅ Stub live at POST /api/veda/chat
- veda_context_system: ✅ Complete (backend/app/utils/veda_context.py)
- rbac_and_auth: ✅ Task 2.10 (Finished)
- org_scope_queries: ✅ Task 2.10 (Finished)
- finance_module: ✅ Complete
- veda_ai_layer: 📋 Phase 3 — after Finance

### Frontend
- frontend_shell: 📋 Phase 4 — after VEDA AI layer

## Frontend Architecture

### Layout: Browser-based IDE Shell
Four panels (non-negotiable):
- Activity bar (48px) — module switcher with live badges
- Left panel (240px) — record navigator, live badge counts, reports
- Center panel (flex:1) — VEDA conversation, inline card rendering
- Right panel (300px) — record inspector, audit trail, field detail

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

### UIResponse Contract
Every VEDA response is a typed UIResponse object.
The frontend has a component registry keyed to response types.
Text responses alone are NEVER returned for actionable operations.

Types: `TABLE | FORM | APPROVAL | BLOCKER | CONFIRM | TEXT | PROGRESS`

Component registry:
- TABLE → `<InlineTable />`
- FORM → `<InlineForm />`
- APPROVAL → `<ApprovalCard />`
- BLOCKER → `<BlockerCard />`
- CONFIRM → `<ConfirmCard />`
- PROGRESS → `<ProgressCard />`
- TEXT → `<TextMessage />`

### Active Record Context
The open record (type + ID) is passed to VEDA automatically.
VEDA never needs to be told what record the user is looking at.
Context: `{ open_record_type, open_record_id, open_module, tenant_id }`

### Streaming
Vercel AI SDK (useChat hook + streamText).
UIResponse components render progressively as tokens arrive.
