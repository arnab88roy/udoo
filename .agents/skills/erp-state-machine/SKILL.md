---
name: erp-state-machine
description: Rules for implementing the docstatus state machine on all transactional ERP tables.
---

# Skill: ERP docstatus State Machine

## 1. The Three States
Every transactional table MUST have a `docstatus` integer column:
- `0` = **Draft** — record is editable, not yet actioned
- `1` = **Submitted** — record is locked, pending or post approval
- `2` = **Cancelled** — terminal state, record is frozen permanently

Master data tables (Company, Department, Employee etc.) default to `docstatus=1`.
Transactional tables (Leave Application, Attendance, Salary Slip etc.) default to `docstatus=0`.

## 2. Required Endpoints Per Transactional Table
Every transactional router MUST implement these endpoints:

```
POST /{id}/submit   → transitions docstatus 0 → 1
                      Reject with 400 if current docstatus != 0

POST /{id}/cancel   → transitions docstatus 1 → 2
                      Reject with 400 if current docstatus != 1
```

For tables with an approval workflow, also add:
```
POST /{id}/approve  → sets status="Approved" (does NOT change docstatus)
                      Reject with 400 if current docstatus != 1

POST /{id}/reject   → sets status="Rejected" (does NOT change docstatus)
                      Reject with 400 if current docstatus != 1
```

## 3. State Transition Validation Pattern
Always validate state before transitioning. Use this exact pattern:
```python
@router.post("/{id}/submit", response_model=schemas.XxxResponse)
async def submit_xxx(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    obj = await get_or_404(db, id, tenant_id)
    if obj.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft records can be submitted.")
    obj.docstatus = 1
    await db.commit()
    return await eager_load_and_return(db, obj.id)
```

## 4. Hard Rules
- **Never hard delete a transactional record.** Cancel it instead (docstatus=2).
- **Cancelled records are immutable.** No further state transitions allowed from docstatus=2.
- **Always return the full eager-loaded response** after any state transition.
- The `status` field (e.g. "Open", "Approved", "Rejected") is separate from `docstatus`.
  `docstatus` controls the workflow lock. `status` carries the business outcome.

## 5. Current Module State Machine Map
| Module | Submit | Approve | Reject | Cancel |
|---|---|---|---|---|
| LeaveApplication | ✅ | ✅ | ❌ missing | ❌ missing |
| Attendance | 🔨 build | — | — | 🔨 build |
| AttendanceRequest | 🔨 build | 🔨 build | 🔨 build | 🔨 build |
| SalarySlip | 📋 planned | — | — | 📋 planned |
| Quote | 📋 planned | 📋 planned | 📋 planned | 📋 planned |
| Invoice | 📋 planned | — | — | 📋 planned |