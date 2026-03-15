from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr_masters import models
from app.schemas.user_context import UserContext
from app.schemas.ui_response import (
    UIContext,
    UIResponse,
    UIAction,
    make_table_response,
    make_blocker_response,
)
from app.utils.veda_context import context_for_module
from app.utils.org_scope import get_visible_employee_ids
from app.utils.permissions import check_permission


async def list_employees_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    status_filter: Optional[str] = "Active",
) -> UIResponse:
    """
    List employees visible to the current user.

    Permission required: hrms.view
    Org scope applied:
        owner / hr_manager / auditor  → all employees in tenant
        manager                       → direct + indirect reports only
        employee                      → self only
        finance_manager               → BLOCKER (no hrms access)

    Returns:
        TABLE UIResponse  — on success
        BLOCKER UIResponse — if no permission or no visible employees
    """
    # ── Step 1: Permission check ───────────────────────────────────────────
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to employee records.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    # ── Step 2: Org scope ──────────────────────────────────────────────────
    # Returns None  → no filter, user can see everyone
    # Returns []    → empty list, user can see no one (should not happen if perm check passed)
    # Returns [ids] → filter to this list
    visible_ids = await get_visible_employee_ids(db, user, user.tenant_id)

    if visible_ids is not None and len(visible_ids) == 0:
        return make_blocker_response(
            reason="You do not have any employees in your reporting scope.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    # ── Step 3: Query with tenant isolation ───────────────────────────────
    query = (
        select(models.Employee)
        .where(models.Employee.tenant_id == user.tenant_id)
    )

    if status_filter:
        query = query.where(models.Employee.status == status_filter)

    if visible_ids is not None:
        query = query.where(models.Employee.id.in_(visible_ids))

    query = query.order_by(models.Employee.employee_name)

    # ── Step 4: Execute ────────────────────────────────────────────────────
    result = await db.execute(query)
    employees = result.scalars().all()

    # ── Step 5: Build rows ────────────────────────────────────────────────
    rows = []
    for emp in employees:
        rows.append({
            "id": str(emp.id),
            "employee_id": emp.employee_id or "—",
            "employee_name": emp.employee_name or "—",
            "designation_id": str(emp.designation_id) if emp.designation_id else "—",
            "department_id": str(emp.department_id) if emp.department_id else "—",
            "status": emp.status or "Active",
        })

    # ── Step 6: Build UIResponse ──────────────────────────────────────────
    response_context = context_for_module(user.tenant_id, "hrms")

    actions = []
    if check_permission(user, "hrms", "create"):
        actions.append(UIAction(
            action_id="add_employee",
            label="Add Employee",
            style="primary",
            endpoint="/api/employees/",
            method="POST",
            payload={},
            confirmation_required=False,
        ))

    status_label = status_filter.lower() if status_filter else "all"
    return make_table_response(
        message=f"Here are the {status_label} employees ({len(rows)} total):",
        context=response_context,
        columns=["employee_id", "employee_name", "designation_id", "department_id", "status"],
        column_labels={
            "employee_id": "Employee ID",
            "employee_name": "Name",
            "designation_id": "Designation",
            "department_id": "Department",
            "status": "Status",
        },
        rows=rows,
        total=len(rows),
        record_type="employee",
        row_id_field="id",
        actions=actions,
    )
