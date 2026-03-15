"""
Shared helpers for VEDA tool functions.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr_masters import models as hr_models
from app.modules.core_masters import models as core_models
from app.modules.org_masters import models as org_models
from app.schemas.ui_response import UIContext, UIResponse, make_table_response, make_blocker_response
from app.utils.org_scope import get_visible_employee_ids


async def resolve_employee_by_name(
    db: AsyncSession,
    name: str,
    tenant_id: UUID,
    user,
    context: UIContext,
) -> tuple:
    """
    Search employees by name (ilike). Handles three cases:

    Returns (employee, None) if exactly one match found.
    Returns (None, blocker_response) if zero matches found.
    Returns (None, table_response) if multiple matches found —
        returns disambiguation TABLE so user can pick the right one.

    The disambiguation TABLE has record_type="employee" so clicking
    a row sets open_record_id in the frontend context, and the next
    message will use context.open_record_id instead of the name.
    """
    query = (
        select(hr_models.Employee)
        .where(
            hr_models.Employee.tenant_id == tenant_id,
            hr_models.Employee.employee_name.ilike(f"%{name}%"),
        )
        .order_by(hr_models.Employee.employee_name)
    )

    # Apply org scope
    visible_ids = await get_visible_employee_ids(db, user, tenant_id)
    if visible_ids is not None:
        query = query.where(hr_models.Employee.id.in_(visible_ids))

    result = await db.execute(query)
    employees = result.scalars().all()

    if not employees:
        return None, make_blocker_response(
            reason=f"No employee found matching '{name}'. Check the name and try again.",
            resolution_options=[],
            context=context,
            blocked_task="Finding employee",
        )

    if len(employees) == 1:
        return employees[0], None

    # Multiple matches — return disambiguation TABLE
    rows = []
    for emp in employees:
        rows.append({
            "id": str(emp.id),
            "employee_number": emp.employee_number or "—",
            "employee_name": emp.employee_name or "—",
            "department_id": str(emp.department_id) if emp.department_id else "—",
            "status": emp.status or "Active",
        })

    return None, make_table_response(
        message=(
            f"I found {len(employees)} employees matching '{name}'. "
            f"Please click the correct one to continue:"
        ),
        context=context,
        columns=["employee_number", "employee_name", "department_id", "status"],
        column_labels={
            "employee_number": "ID",
            "employee_name": "Name",
            "department_id": "Department",
            "status": "Status",
        },
        rows=rows,
        total=len(rows),
        record_type="employee",
        row_id_field="id",
    )


async def fetch_display_names(
    db: AsyncSession,
    tenant_id: UUID,
    designation_ids: List[UUID] = None,
    department_ids: List[UUID] = None,
    employee_ids: List[UUID] = None,
    leave_type_ids: List[UUID] = None,
) -> dict:
    """
    Batch fetches display names for foreign key UUIDs.
    Returns a dict of dicts:
    {
        "designations": {uuid: "Software Engineer"},
        "departments":  {uuid: "Engineering"},
        "employees":    {uuid: "Dev Patel"},
        "leave_types":  {uuid: "Casual Leave"},
    }

    Use this before building table rows to resolve UUIDs to names.
    """
    result = {
        "designations": {},
        "departments": {},
        "employees": {},
        "leave_types": {},
    }

    if designation_ids:
        unique_ids = list(set(i for i in designation_ids if i))
        if unique_ids:
            stmt = select(
                core_models.Designation.id,
                core_models.Designation.designation_name
            ).where(
                core_models.Designation.id.in_(unique_ids),
                core_models.Designation.tenant_id == tenant_id,
            )
            rows = (await db.execute(stmt)).all()
            result["designations"] = {str(r.id): r.designation_name for r in rows}

    if department_ids:
        unique_ids = list(set(i for i in department_ids if i))
        if unique_ids:
            try:
                stmt = select(
                    org_models.Department.id,
                    org_models.Department.department_name
                ).where(
                    org_models.Department.id.in_(unique_ids),
                    org_models.Department.tenant_id == tenant_id,
                )
                rows = (await db.execute(stmt)).all()
                result["departments"] = {str(r.id): r.department_name for r in rows}
            except Exception:
                pass  # Fallback or error handling

    if employee_ids:
        unique_ids = list(set(i for i in employee_ids if i))
        if unique_ids:
            stmt = select(
                hr_models.Employee.id,
                hr_models.Employee.employee_name
            ).where(
                hr_models.Employee.id.in_(unique_ids),
                hr_models.Employee.tenant_id == tenant_id,
            )
            rows = (await db.execute(stmt)).all()
            result["employees"] = {str(r.id): r.employee_name for r in rows}

    if leave_type_ids:
        unique_ids = list(set(i for i in leave_type_ids if i))
        if unique_ids:
            stmt = select(
                hr_models.LeaveType.id,
                hr_models.LeaveType.leave_type_name
            ).where(
                hr_models.LeaveType.id.in_(unique_ids),
                hr_models.LeaveType.tenant_id == tenant_id,
            )
            rows = (await db.execute(stmt)).all()
            result["leave_types"] = {str(r.id): r.leave_type_name for r in rows}

    return result
