# PROJECT BRIEF: AI-Native ERP Meta-Engine

## 1. Project Identity

**Product Name:** Udoo (AI-Native ERP Meta-Engine)
**Tagline:** The speed of a Modular Monolith with the intelligence of an AI-Native OS.
**Elevator Pitch:** Udoo is a next-generation Enterprise Resource Planning (ERP) platform architected from the ground up to merge the robust, metadata-driven structure of traditional ERPs (like Frappe/ERPNext) with async Python scale and native AI orchestration. It replaces hundreds of static screens with a dynamic frontend powered by strict backend schemas, while autonomous AI agents execute transactional workflows exactly as human users would.

**Target Market:**
- **Customer:** Mid-market to Enterprise organizations.
- **Size:** 50 - 5000+ employees.
- **Industry:** Agnostic core engine with industry-specific vertical modules (starting with HRMS).
- **Geography:** Global, with a structured roadmap for Indian localization and statutory compliance.

**Problem Addressed:**
Traditional ERPs (like Odoo or ERPNext) suffer from technological debt, synchronous blocking architectures, and bolted-on "chatbots" that cannot execute actual business logic. Existing solutions fail modern enterprises that require highly concurrent, API-first software where AI operates as a deeply integrated functional worker rather than a superficial text generator.

---

## 2. Business Model

**Pricing Strategy:** NOT YET DEFINED
**GTM (Go-To-Market) Strategy:** NOT YET DEFINED

**Competitive Positioning:**
- **Vs. Odoo:** Avoids Odoo's heavy XML-based view definitions and monolithic ORM coupling. Udoo enforces strict API contracts (OpenAPI/Pydantic) allowing for fully decoupled, modern SPA/PWA frontends.
- **Vs. ERPNext/Frappe:** Replicates Frappe's genius "Meta-Engine" (DocTypes, state machines, linked documents) but discards its synchronous Python/MariaDB legacy in favor of fully asynchronous FastAPI, Pydantic, and PostgreSQL with Row-Level Security (RLS). Furthermore, AI agents function natively as supervisors and domain experts (via LangGraph and CrewAI) rather than aftermarket add-ons.

---

## 3. Complete Module Roadmap

### Phase 2: Backend MVP (HRMS Vertical Slice)
- **Core Masters (Gender, Salutation, etc.):** Complete
- **Org Masters (Branch, Designation, Department, etc.):** Complete
- **Dependent Masters (Holiday List):** Complete
- **Employee Master & Child Tables:** Complete
- **Transactional Modules (Leave):** Complete
- **Transactional Modules (Attendance):** Planned

### Phase 5+: Horizontal Scaling (Future)
- **Payroll & Expense Management:** Planned
- **Accounting & Financial Management:** Planned
- **CRM & Sales:** Planned
- **Inventory & Manufacturing:** Planned

**Priority Order:** Environment Setup -> Agent Skills -> HRMS Backend MVP -> Frontend MVP -> Agentic Orchestration -> Horizontal Scaling (Other Modules).

**Indian Compliance Requirements (per module):**
- **HRMS/Payroll:** PF, ESI, PT, TDS (Planned - Pending Implementation)
- **Accounting/Sales:** GST (Planned - Pending Implementation)

---

## 4. Current Tech Stack

**Backend:**
- Python 3.9+ 
- FastAPI `fastapi[standard]` (Web Framework)
- Uvicorn `uvicorn` (ASGI Server)
- SQLAlchemy `sqlalchemy` (Async ORM)
- Alembic `alembic` (Database Migrations)
- asyncpg `asyncpg` (PostgreSQL Driver)
- Pydantic `pydantic` (Data Validation & Schema Generation)
- LangGraph `langgraph` (AI Orchestration - Supervisor)
- CrewAI `crewai` (AI Domain Agents)
- Pytest `pytest`, `pytest-asyncio` (Testing)

**Frontend:**
- Next.js (React Framework)
- Supabase JS Client `supabase@^2.76.15`

**Infrastructure & Hosting:**
- PostgreSQL via Supabase (Database Platform) - Hosted on AWS `ap-southeast-2` (Sydney).

**Third-Party Integrations:**
- OpenAI / LLM Providers (via LangGraph/CrewAI) - Planned
- *Other Integrations:* NOT YET DEFINED

---

## 5. Current Architecture

**Folder Structure (Backend):**
- `backend/app/`: Core application logic.
  - `main.py`: FastAPI application entrypoint, global OpenAPI configuration, JWT Middleware for RLS.
  - `dependencies.py`: FastAPI dependency injection (e.g., `get_db`, `get_tenant_id`).
  - `db/database.py`: SQLAlchemy asynchronous engine and session maker setup.
  - `modules/`: Modular Monolith boundaries.
    - `core_masters/`: Base models, Users, Currencies, global lists.
    - `org_masters/`: Departments, Employee Grades, structural definitions.
    - `hr_masters/`: Employee records, Leave types, Leave Applications, Attendance.
- `backend/alembic/`: Database migration scripts.
  - `versions/`: Sequential schema changes (e.g., `3abef1e5ef82_add_leavetype_and_leaveapplication.py`).
- `.agents/`: AI configuration and behavioral rules.
  - `skills/`: Markdown criteria for AI code generation (e.g., `fastapi-crud-generator`, `rls-security`).
  - `specs/`: Data definition documents (like Frappe DocTypes) dictating schemas for the AI.
  - `workflows/`: Standard operating procedures for AI tasks (e.g., `build-from-spec`).

**Multi-Tenancy Implementation:**
Universal single-database/single-schema design isolated via PostgreSQL Row-Level Security (RLS). 
1. Every table extends `CoreMasterBase` which mandates a `tenant_id` UUID column.
2. Migrations automatically append `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and attach a strict policy.
3. FastAPI custom middleware extracts the JWT, and dependency injection (`Depends(get_tenant_id)`) guarantees every database query filters strictly by the authenticated tenant. Cross-tenant leakage is blocked at the database execution level via `current_setting('app.current_tenant_id')` logic mapped to the JWT.

**DocStatus State Machine:**
Replicates the Frappe human-in-the-loop workflow.
1. All transactional entities (e.g., `LeaveApplication`) include an integer `docstatus` column.
2. 0 = Draft, 1 = Submitted, 2 = Cancelled.
3. Explicit REST endpoints drive the transition (e.g., `POST /{id}/submit`, `POST /{id}/approve`).
4. The backend validates rules before transition (e.g., only a Draft `docstatus=0` can be Submitted to `docstatus=1`).

**AI Layer:**
The AI functions as a transactional backend worker, not a chatbot frontend.
1. **Supervisor (LangGraph):** Manages overarching workflows and routing decisions.
2. **Workers (CrewAI):** Specialized domain agents (e.g., "HR Assistant").
These agents interact exclusively via the identical FastAPI endpoints utilized by human users. They must serialize requests matching the precise Pydantic validation requirements. Humans monitor their draft creations via the `docstatus=0` queue.

---

## 6. Current Development Status

**Task Completion Status (from `tasks.md`):**
- [x] Task 0.1: Initialize Python virtual environment.
- [x] Task 0.2: Setup backend/app/main.py with FastAPI & JWT.
- [ ] Task 0.3: Configure PostgreSQL MCP Server (Supabase).
- [ ] Task 1.1: Create skills/fastapi-crud-generator/SKILL.md. *(Note: File exists but task is unchecked in tasks.md)*
- [ ] Task 1.2: Create skills/erp-relationships/SKILL.md. *(Note: File exists but task is unchecked in tasks.md)*
- [ ] Task 1.3: Create skills/rls-security/SKILL.md. *(Note: File exists but task is unchecked in tasks.md)*
- [x] Task 2.1: Build Standalone Core Masters.
- [x] Task 2.2: Build Standalone Org Masters.
- [x] Task 2.3: Build Dependent Masters (Requires Company).
- [x] Task 2.4: Build Employee Master & Child Tables.
- [x] Task 2.5: Build Transactional Modules (Leave partial completion checked). *(Attendance pending)*
- [ ] Task 3.1: Initialize React/Vue environment with Tailwind CSS.
- [ ] Task 3.2: Build GenericDataTable and GenericErpForm.
- [ ] Task 3.3: Build HITL Approval Dashboard.
- [ ] Task 4.1: Build LangGraph Supervisor & HR Agent.
- [ ] Task 5.1 -> 5.4: Horizontal Scaling.

**What is working and verified:**
The foundational backend architecture is highly stable. FastAPI router configuration, SQLAlchemy Async ORM mappings, comprehensive database migrations, RLS tenant isolation injection, child table nested routing (`selectinload`), and the DocStatus workflow (`submit` and `approve` transitions) for Leave Applications have been successfully manually verified via Swagger UI.

**What is partially built:**
- Task 2.5 is split: Leave Management is fully completed and tested. Attendance Management is drafted in specs but backend code has not yet been generated.

**What is planned but not started:**
- All Phase 3 Frontend (Generic UI rendering based on OpenAPI schemas).
- All Phase 4 AI Orchestration (LangGraph integration points).
- All Phase 5 Horizontal Modules (Payroll, Accounting, CRM, Inventory).

**Known Bugs / Technical Debt:**
1. The `jwt_authentication_middleware` in `main.py` is currently utilizing a placeholder extraction method (`X-Tenant-ID` header fallback) rather than full JWT signature cryptographic validation. This must be replaced before production.
2. `tasks.md` Phase 1 and Task 0.3 checkboxes are out of sync with physical repository state (files exist but checkboxes are untouched).

---

## 7. Open Decisions

**Architectural Decisions Pending:**
1. Selection of Frontend Framework approach (React vs Vue) to process and render the dense OpenAPI JSON schemas into Generic Forms/DataTables. (Next.js is scaffolded, but exact generic component approach is undecided).
2. Selection of the caching layer (Redis vs Memcached) for high-frequency master data.

**Integrations Pending:**
1. Selection of standard LLM provider for the API agents (GPT-4o vs Claude 3.5 Sonnet vs open source local models).
2. specific Payroll calculation engine integration points for Indian Statutory compliance (Internal vs API to greytHR/RazorpayX).

**Business Decisions Pending:**
1. SaaS Pricing Strategy.
2. Primary GTM motion (PLG vs Enterprise Sales).
3. First launch geography vs concurrent launch.
