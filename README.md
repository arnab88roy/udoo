# Udoo — AI-Native ERP for Indian SMEs

> **VEDA** (Virtual Enterprise Decision Assistant) — an AI-first, multi-tenant B2B SaaS ERP built for Indian small and medium enterprises.

---

## What is Udoo?

Udoo is a modular ERP platform where AI is the primary interface. Instead of navigating menus, users talk to VEDA — an AI agent that understands business context, enforces compliance, and orchestrates workflows across all modules.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (async) + SQLAlchemy + Alembic |
| Database | PostgreSQL via Supabase (with RLS) |
| AI Layer | LangGraph + Claude (Anthropic) |
| Frontend | Next.js + Tailwind CSS |
| Auth | JWT + Supabase RLS tenant isolation |

---

## Modules

| Module | Status |
|---|---|
| Core Masters (Company, Currency, Holiday) | ✅ Complete |
| Org Masters (Branch, Department, Designation) | ✅ Complete |
| Employee Master + Child Tables | ✅ Complete |
| Leave Management | ✅ Complete |
| Attendance Management | ✅ Complete |
| Payroll (Salary Components, Slips, PF/ESI/TDS) | ✅ Complete |
| RBAC + Org Scope | ✅ Complete |
| Finance (GST, Invoicing, TDS, Recurring) | ✅ Complete |
| VEDA AI Layer (LangGraph) | 🔄 In Progress |
| Frontend (Dynamic UI) | 📋 Planned |

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system design, module map, and API conventions.

---

## Project Structure

```
udoo/
├── .agents/          # Agent skill definitions and workflows
├── backend/
│   └── app/
│       ├── modules/  # HRMS, Finance, Payroll modules
│       ├── utils/    # RBAC, org scope helpers
│       ├── schemas/  # Pydantic schemas
│       └── tests/    # Pytest test suites
├── supabase/
│   └── migrations/   # Alembic migration files
├── tasks.md          # Master implementation plan
└── ARCHITECTURE.md   # System architecture reference
```

---

## Key Design Principles

- **Multi-tenant**: Every table has `tenant_id`. Supabase RLS enforces isolation at the database level.
- **Indian compliance**: GST (CGST/SGST/IGST), TDS (194C/194J), PF, ESI built in.
- **Docstatus state machine**: All transactional documents follow Draft → Submitted → Cancelled lifecycle.
- **AI-first**: VEDA is the primary interface — not a chatbot bolted on top, but the core interaction layer.

---

## Running Locally

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

---

## License

Private — All rights reserved. © 2025 Udoo.