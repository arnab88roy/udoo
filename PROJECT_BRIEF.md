# PROJECT BRIEF: Udoo — AI-Native ERP for Indian SMEs

## 1. Project Identity

**Product Name:** Udoo
**Tagline:** The conversation IS the ERP.
**Elevator Pitch:** Udoo is an AI-first, multi-tenant B2B SaaS ERP built
for Indian small and medium businesses (1–50+ employees). The primary
interface is VEDA (Virtual Enterprise Decision Assistant) — an AI agent
that understands business context, enforces Indian compliance, and
orchestrates workflows across all modules. Users talk to VEDA instead
of navigating menus. Traditional module screens are the escape hatch for
power users, not the primary interface.

**The Cursor Analogy:**
Udoo is to business operations what Cursor is to coding. The human and
VEDA are co-authors of the same business record. Both can touch it.
No handoff ceremony. No mode switching.

**Three Rules of Co-Authorship:**
- Rule 1 — No silos: Every VEDA action writes to the same Postgres
  tables the form UI reads from.
- Rule 2 — Interruptible: Human can take over mid-task always.
  VEDA can take over a human-started task always.
- Rule 3 — Transparent diffs: Every field VEDA fills carries a visual
  attribution (purple tint). Human can accept all, reject all, or edit
  field by field.

**Target Market:**
- **Customer:** Indian small and medium enterprises
- **Size:** 1–50+ employees, expanding to 5000+
- **Industry:** Agnostic core engine, starting with HRMS + Finance
- **Geography:** India-first, globally deployable architecture

**Problem Addressed:**
Traditional ERPs (Odoo, ERPNext) have technological debt, synchronous
blocking architectures, and bolted-on chatbots that cannot execute real
business logic. Indian SMEs specifically suffer from complex compliance
requirements (GST, PF, ESI, TDS) that existing tools handle poorly.
Udoo replaces static screens with an AI-native interface backed by
strict API contracts and Indian compliance built in from day one.

**Competitive Positioning:**
- **Vs. Odoo:** No XML view definitions, no monolithic ORM coupling.
  Strict OpenAPI/Pydantic contracts, fully decoupled modern frontend.
- **Vs. ERPNext/Frappe:** Replicates Frappe's DocType genius but
  replaces synchronous Python/MariaDB with fully async FastAPI +
  PostgreSQL with RLS. AI agents are native supervisors, not
  aftermarket add-ons.
- **Vs. greytHR/Zoho:** AI-first interface, developer-grade
  architecture, open API, no per-module pricing walls.

---

## 2. Business Model

**Pricing Strategy:** First seat free (1 year) → tiered per-seat model
**GTM Strategy:** Product-led growth — VEDA onboarding in 5 questions,
zero setup friction
**Primary Geography:** India first, then Southeast Asia

---

## 3. Tech Stack

**Backend:**
- Python 3.11+
- FastAPI `fastapi[standard]` — async web framework
- SQLAlchemy — async ORM
- Alembic — sole migration source of truth (never Supabase SQL editor)
- asyncpg — PostgreSQL async driver
- Pydantic — data validation + OpenAPI schema generation
- python-jose — JWT (HS256), tenant_id + user_id + role in payload
- bcrypt — password hashing

**AI Layer:**
- LangGraph — supervisor + domain agent orchestration
- Claude (Anthropic) — primary LLM for VEDA
- UIResponse — typed Pydantic schema for all VEDA outputs
  (7 response types: TABLE, FORM, APPROVAL, BLOCKER, CONFIRM,
  PROGRESS, TEXT)

**Database:**
- PostgreSQL via Supabase (AWS ap-southeast-1)
- Row Level Security (RLS) enforced at DB level via tenant_id
- Alembic manages all schema changes — single source of truth

**Frontend:**
- Next.js 16 + Tailwind CSS + shadcn/ui + Lucide
- Vercel AI SDK (useChat hook + streamText for streaming)
- Browser-based IDE shell layout (4 panels — non-negotiable)

---

## 4. Architecture Principles

**Multi-Tenancy:**
Every table has `tenant_id`. Supabase RLS enforces isolation at the
database level. JWT middleware extracts tenant_id on every request.
App-level and DB-level filtering both enforced (defense in depth).

**DocStatus State Machine:**
All transactional documents follow:
Draft (0) → Submitted (1) → Cancelled (2)
Explicit REST endpoints drive transitions (`/submit`, `/approve`,
`/reject`, `/cancel`). Never hard delete transactional records.

**RBAC — Six Roles:**
| Role | HRMS | Payroll | Finance | Settings | CRM | Tasks |
|---|---|---|---|---|---|---|
| owner | Full | Full | Full | Full | Full | Full |
| hr_manager | Full | Full | None | Partial | None | Full |
| finance_manager | None | View+Approve | Full | Partial | Full | Full |
| manager | View+Approve (team only) | None | None | None | View+Create | Full |
| employee | Self only | View self | None | None | None | Own tasks |
| auditor | View all | View all | View all | View all | View all | View all |

Permission check pattern on every protected endpoint:
```python
require_permission(current_user, "module_name", "action")
# action: view, create, edit, submit, approve, delete
```

**Org Scope:**
Every list endpoint for manager/employee roles filters via recursive
PostgreSQL CTE to return only visible employees:
```python
visible_ids = await get_visible_employee_ids(db, current_user, tenant_id)
if visible_ids is not None:
    query = query.where(Employee.id.in_(visible_ids))
```

**Audit Trail:**
`created_by` and `modified_by` auto-populated on every record via
SQLAlchemy events reading from `current_user_id_ctx` ContextVar.
No manual passing required in individual endpoints.

**VEDA Personalisation:**
VEDA's system prompt is dynamically assembled per user from:
1. Identity: name, designation, company
2. Permissions: which modules and actions are available
3. Scope: which employees/records are visible
4. Context: active record open in the editor

**Core Rules (Non-Negotiable):**
1. Every table has tenant_id — always filter by it
2. Transactional tables have docstatus (0/1/2)
3. Child tables are relational — never JSONB
4. Alembic is the only migration system
5. Modules are isolated — no cross-module DB joins
6. AI agents call the same FastAPI endpoints humans use

---

## 5. Module Status

### Phase 0–1: Foundation (Complete)
- Environment setup, FastAPI + JWT middleware ✅
- 14 Agent skill files created in `.agents/skills/` ✅
- ARCHITECTURE.md, tasks.md, PROJECT_BRIEF.md ✅

### Phase 2: Backend MVP (Complete)
| Module | Key Files | Status |
|---|---|---|
| Core Masters | `modules/core_masters/` | ✅ Complete |
| Org Masters | `modules/org_masters/` | ✅ Complete |
| Employee Master + Child Tables | `modules/hr_masters/` | ✅ Complete |
| Leave Management | `modules/hr_masters/routers/leave.py` | ✅ Complete |
| Attendance Management | `modules/hr_masters/routers/attendance.py` | ✅ Complete |
| Payroll (PF/ESI/TDS) | `modules/payroll/` | ✅ Complete |
| RBAC + Org Scope | `utils/permissions.py`, `utils/org_scope.py` | ✅ Complete |
| Finance (GST/Invoicing/TDS/Recurring) | `modules/finance/` | ✅ Complete |
| UIResponse Schema | `schemas/ui_response.py` | ✅ Complete |
| VEDA Chat Endpoint (stub) | `main.py` POST /api/veda/chat | ✅ Complete |
| VEDA Context System | `utils/veda_context.py` | ✅ Complete |

### Phase 3: VEDA AI Layer (Next)
| Task | Description | Status |
|---|---|---|
| Task 3.1 | LangGraph Supervisor + list_employees tool | 🔄 Next |
| Task 3.2 | HR Agent core tools (leave, attendance) | 📋 Planned |
| Task 3.3 | HR Agent payroll tools | 📋 Planned |
| Task 3.4 | Finance Agent | 📋 Planned |
| Task 3.5 | Policy Engine Schema | 📋 Planned |
| Task 3.6 | Setup/Onboarding Agent | 📋 Planned |
| Task 3.7 | Personalised role-aware VEDA greeting | 📋 Planned |

### Phase 4: Frontend IDE Shell (After Phase 3)
| Task | Description | Status |
|---|---|---|
| Task 4.1 | IDE Shell + UIResponse Component Registry | 📋 Planned |
| Task 4.2 | VEDA Chat Engine (streaming) | 📋 Planned |
| Task 4.3 | Active Record Context Wiring | 📋 Planned |
| Task 4.4 | HITL Approval Flow | 📋 Planned |
| Task 4.5 | VEDA Diff Attribution (purple tint) | 📋 Planned |
| Task 4.6 | Role-Aware VEDA Hint Chips | 📋 Planned |

### Phase 5: Horizontal Scaling (After Phase 4)
- Full Payroll Depth (Form 16, bank files, salary revision)
- Expense Management
- Full Accounting (Chart of accounts, P&L, GSTR-1, GSTR-3B)
- CRM & Sales (Quote-to-Cash pipeline)
- Inventory & Manufacturing
- WhatsApp Integration (key Indian SME retention feature)

---

## 6. Indian Compliance Built In

**HRMS/Payroll:**
- PF: 12% employer + 12% employee on basic (ceiling ₹15,000/month)
- ESI: 3.25% employer + 0.75% employee (ceiling ₹21,000 gross)
- PT: State-wise professional tax deduction table
- TDS: Monthly estimated tax on salary

**Finance/Invoicing:**
- GST: CGST+SGST (intra-state), IGST (inter-state), zero-rated (export)
- TDS: Section 194C (individual 1%, company 2%), Section 194J (10%)
- Invoice numbering: Sequential per financial year (INV-2526-0001)
- GSTIN mandatory on client and company records
- HSN/SAC code mandatory on all line items
- TaxTemplate system — globally deployable, not hardcoded to India

---

## 7. Frontend Layout (Non-Negotiable)
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

UIResponse Component Registry:
- TABLE → `<InlineTable />`
- FORM → `<InlineForm />`
- APPROVAL → `<ApprovalCard />`
- BLOCKER → `<BlockerCard />`
- CONFIRM → `<ConfirmCard />`
- PROGRESS → `<ProgressCard />`
- TEXT → `<TextMessage />`

RBAC-aware shell:
- Activity bar icons only show modules the user has access to
- Finance icon hidden for hr_manager role
- HRMS icon hidden for finance_manager role
- Settings icon only visible to owner and hr_manager

---

## 8. Technical Debt (Before First Paying Customer)

| Item | Description | Priority |
|---|---|---|
| TD-2 | DB-level RLS via current_setting in Alembic migrations | High |
| TD-3 | Audit log table wired to all transactional tables | High |
| TD-4 | Field(description="...") on all Pydantic schemas | High |
| TD-7 | Policy engine — approval thresholds not queryable | High |
| TD-8 | UIResponse schema not yet wired to LangGraph output | High |
| TD-9 | Vercel AI SDK streaming not yet implemented | Medium |
| TD-10 | VEDA diff attribution (purple tint) not yet implemented | Medium |
| TD-11 | Frontend shell uses wrong layout (sidebar vs 4-panel IDE) | Medium |
| TD-12 | Permission checks missing from existing HRMS/Payroll endpoints | High |
| TD-13 | Org scope filtering not applied to existing list endpoints | High |
| TD-14 | Payroll bulk-generate uses company-level salary structure instead of employee-specific | Medium |

---

## 9. Open Decisions

**Business:**
1. Exact per-seat pricing tiers not yet defined
2. GTM motion — PLG vs direct sales not finalised
3. Launch sequencing — India only vs concurrent markets

**Technical:**
1. Caching layer — Redis vs in-memory for high-frequency master data
2. WhatsApp integration timeline