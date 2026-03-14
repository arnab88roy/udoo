# SKILL: RBAC and Org Scope

## Rule 1 — Every Protected Endpoint Must Check Permissions
The first lines of every non-public endpoint must be:

```python
@router.post("/", status_code=201)
async def create_something(
    data: SomethingCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: UserContext = Depends(get_current_user),
):
    require_permission(current_user, "module_name", "create")
    # ... rest of endpoint
```

## Rule 2 — List Endpoints Must Apply Org Scope
Any endpoint that lists employees or employee-linked records:

```python
@router.get("/")
async def list_leave_applications(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: UserContext = Depends(get_current_user),
):
    require_permission(current_user, "hrms", "view")

    visible_ids = await get_visible_employee_ids(db, current_user, tenant_id)
    query = select(LeaveApplication).where(
        LeaveApplication.tenant_id == tenant_id
    )
    if visible_ids is not None:
        query = query.where(LeaveApplication.employee_id.in_(visible_ids))
    # ... continue
```

## Rule 3 — Self-Service Records Need Own Record Check
For endpoints where employees access their own data:

```python
async def get_my_salary_slip(id: UUID, ...):
    require_permission(current_user, "payroll", "view")
    slip = await get_or_404(db, id, tenant_id)
    require_own_record(current_user, slip.employee_id)
    return slip
```

## Rule 4 — VEDA Must Check Permissions Before Suggesting Actions
In every LangGraph agent tool, check permission before executing:

```python
async def run_payroll_tool(context: UIContext, user: UserContext, ...):
    if not check_permission(user, "payroll", "submit"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) cannot submit payroll. "
                   f"Please ask your HR Manager or Owner.",
            resolution_options=[],
            context=context
        )
    # ... proceed with payroll
```

## Rule 5 — Never Hardcode Role Checks in Business Logic
Always use check_permission() or require_permission().
Never write: if user.role == "owner": ...
Exception: UserContext properties like user.has_payroll_access are acceptable.

## Permission Matrix Quick Reference
| Action | owner | hr_mgr | fin_mgr | manager | employee | auditor |
|---|---|---|---|---|---|---|
| hrms.view | ✅ | ✅ | ❌ | ✅ team | ✅ self | ✅ |
| hrms.approve | ✅ | ✅ | ❌ | ✅ team | ❌ | ❌ |
| payroll.submit | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| finance.create | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| finance.approve | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| settings.edit | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

## Org Scope Quick Reference
| Role | get_visible_employee_ids() returns |
|---|---|
| owner | None (no filter — sees all) |
| hr_manager | None (no filter — sees all) |
| auditor | None (no filter — sees all) |
| finance_manager | [] (sees no employee records) |
| manager | [self + all direct/indirect reports] |
| employee | [self only] |
