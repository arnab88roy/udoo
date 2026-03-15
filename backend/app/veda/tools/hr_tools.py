from typing import Optional
from uuid import UUID
from collections import Counter

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
    make_text_response,
    make_form_response,
    make_approval_response,
    FormField,
    FormFieldType,
)
from app.utils.veda_context import context_for_module
from app.utils.org_scope import get_visible_employee_ids
from app.utils.permissions import check_permission, DEFAULT_PERMISSIONS
from app.veda.tools.helpers import resolve_employee_by_name, fetch_display_names


async def list_employees_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    status_filter: Optional[str] = "Active",
) -> UIResponse:
    """
    List employees visible to the current user.
    """
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to employee records.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    visible_ids = await get_visible_employee_ids(db, user, user.tenant_id)

    if visible_ids is not None and len(visible_ids) == 0:
        return make_blocker_response(
            reason="You do not have any employees in your reporting scope.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    query = select(models.Employee).where(models.Employee.tenant_id == user.tenant_id)
    if status_filter:
        query = query.where(models.Employee.status == status_filter)
    if visible_ids is not None:
        query = query.where(models.Employee.id.in_(visible_ids))
    query = query.order_by(models.Employee.employee_name)

    result = await db.execute(query)
    employees = result.scalars().all()

    # Resolve names for display
    names = await fetch_display_names(
        db=db,
        tenant_id=user.tenant_id,
        designation_ids=[emp.designation_id for emp in employees],
        department_ids=[emp.department_id for emp in employees],
    )

    rows = []
    for emp in employees:
        rows.append({
            "id": str(emp.id),
            "employee_number": emp.employee_number or "—",
            "employee_name": emp.employee_name or "—",
            "designation": names["designations"].get(str(emp.designation_id), "—"),
            "department": names["departments"].get(str(emp.department_id), "—"),
            "status": emp.status or "Active",
        })

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

    return make_table_response(
        message=f"Here are the {status_filter.lower() if status_filter else 'all'} employees ({len(rows)} total):",
        context=response_context,
        columns=["employee_number", "employee_name", "designation", "department", "status"],
        column_labels={
            "employee_number": "ID",
            "employee_name": "Name",
            "designation": "Designation",
            "department": "Department",
            "status": "Status",
        },
        rows=rows,
        total=len(rows),
        record_type="employee",
        row_id_field="id",
        actions=actions,
    )


async def get_employee_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    name: Optional[str] = None,
    employee_id: Optional[str] = None,
) -> UIResponse:
    """
    Get detailed FORM view of a specific employee.
    """
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to employee records.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing employee details",
        )

    emp = None
    if employee_id:
        query = select(models.Employee).where(
            models.Employee.employee_number == employee_id,
            models.Employee.tenant_id == user.tenant_id
        )
        result = await db.execute(query)
        emp = result.scalars().first()
    elif name:
        emp, disambiguation = await resolve_employee_by_name(
            db, name, user.tenant_id, user, context
        )
        if disambiguation:
            return disambiguation
    elif context.open_record_type == "employee" and context.open_record_id:
        query = select(models.Employee).where(
            models.Employee.id == context.open_record_id,
            models.Employee.tenant_id == user.tenant_id
        )
        result = await db.execute(query)
        emp = result.scalars().first()

    if not emp:
        return make_blocker_response(
            reason=f"No employee found matching '{employee_id or name or 'context'}'.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing employee details",
        )

    visible_ids = await get_visible_employee_ids(db, user, user.tenant_id)
    if visible_ids is not None and emp.id not in visible_ids:
        return make_blocker_response(
            reason="This employee is outside your reporting scope.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing employee details",
        )

    fields = [
        FormField(name="employee_number", label="Employee ID", field_type=FormFieldType.READONLY),
        FormField(name="employee_name", label="Full Name", field_type=FormFieldType.TEXT, required=True),
        FormField(name="personal_email", label="Email", field_type=FormFieldType.TEXT),
        FormField(name="status", label="Status", field_type=FormFieldType.SELECT, options=[
            {"value": "Active", "label": "Active"},
            {"value": "Inactive", "label": "Inactive"},
            {"value": "Suspended", "label": "Suspended"},
        ]),
    ]
    values = {
        "employee_number": emp.employee_number,
        "employee_name": emp.employee_name,
        "personal_email": emp.personal_email,
        "status": emp.status,
    }

    return make_form_response(
        message=f"Here is the record for {emp.employee_name}:",
        record_type="employee",
        record_id=emp.id,
        fields=fields,
        values=values,
        submit_endpoint=f"/api/employees/{emp.id}",
        submit_method="PATCH",
        context=context,
    )


async def list_leave_applications_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    status: Optional[str] = "Open",
) -> UIResponse:
    """
    List leave applications. Applies org scope.
    """
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to leave records.",
            resolution_options=[],
            context=context,
            blocked_task="Listing leave applications",
        )

    visible_emp_ids = await get_visible_employee_ids(db, user, user.tenant_id)
    
    query = (
        select(models.LeaveApplication)
        .where(models.LeaveApplication.tenant_id == user.tenant_id)
        .where(models.LeaveApplication.status == status)
        .where(models.LeaveApplication.docstatus == 1)
    )

    if visible_emp_ids is not None:
        query = query.where(models.LeaveApplication.employee_id.in_(visible_emp_ids))

    query = query.order_by(models.LeaveApplication.from_date.desc())
    result = await db.execute(query)
    leaves = result.scalars().all()

    if not leaves:
        return make_text_response(
            message=f"No {status.lower()} leave approvals found — your team is all clear.",
            context=context,
            hints=["Show attendance", "Show all employees"],
        )

    names = await fetch_display_names(
        db=db,
        tenant_id=user.tenant_id,
        employee_ids=[leave.employee_id for leave in leaves],
        leave_type_ids=[leave.leave_type_id for leave in leaves],
    )

    rows = []
    for leave in leaves:
        rows.append({
            "id": str(leave.id),
            "employee_name": names["employees"].get(str(leave.employee_id), "—"),
            "leave_type": names["leave_types"].get(str(leave.leave_type_id), "—"),
            "from_date": leave.from_date.isoformat(),
            "to_date": leave.to_date.isoformat(),
            "days": float(leave.total_leave_days or 0),
            "status": leave.status,
        })

    return make_table_response(
        message=f"I found {len(rows)} {status.lower()} leave applications:",
        context=context,
        columns=["employee_name", "leave_type", "from_date", "to_date", "days", "status"],
        column_labels={
            "employee_name": "Employee",
            "leave_type": "Leave Type",
            "from_date": "From",
            "to_date": "To",
            "days": "Days",
            "status": "Status"
        },
        rows=rows,
        total=len(rows),
        record_type="leave_application",
        row_id_field="id",
    )


async def approve_leave_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    leave_id: Optional[str] = None,
) -> UIResponse:
    """
    Shows an APPROVAL card for a specific leave application.
    """
    if not check_permission(user, "hrms", "approve"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have permission to approve leaves.",
            resolution_options=[],
            context=context,
            blocked_task="Approving leave",
        )

    lid = None
    if leave_id:
        try:
            lid = UUID(leave_id)
        except ValueError:
            pass
    
    if lid is None and context.open_record_type == "leave_application":
        lid = context.open_record_id

    if not lid:
        return make_blocker_response(
            reason="I couldn't identify which leave application you want to approve. Please open the record or provide the ID.",
            resolution_options=[],
            context=context,
            blocked_task="Approving leave",
        )

    query = select(models.LeaveApplication).where(
        models.LeaveApplication.id == lid,
        models.LeaveApplication.tenant_id == user.tenant_id
    )
    result = await db.execute(query)
    leave = result.scalars().first()

    if not leave:
        return make_blocker_response(
            reason="Leave application not found.",
            resolution_options=[],
            context=context,
            blocked_task="Approving leave",
        )

    if leave.status != "Open":
        return make_blocker_response(
            reason=f"This leave application is already {leave.status}.",
            resolution_options=[],
            context=context,
            blocked_task="Approving leave",
        )

    names = await fetch_display_names(
        db=db,
        tenant_id=user.tenant_id,
        employee_ids=[leave.employee_id],
        leave_type_ids=[leave.leave_type_id],
    )

    employee_name = names["employees"].get(str(leave.employee_id), "Unknown Employee")
    leave_type_name = names["leave_types"].get(str(leave.leave_type_id), "—")

    return make_approval_response(
        message=f"Please confirm the approval for {employee_name}'s leave request:",
        record_type="leave_application",
        record_id=leave.id,
        summary={
            "Employee": employee_name,
            "Leave Type": leave_type_name,
            "From": str(leave.from_date),
            "To": str(leave.to_date),
            "Days": str(leave.total_leave_days),
            "Reason": leave.description or "No reason provided",
        },
        approve_endpoint=f"/api/leave-applications/{leave.id}/approve",
        reject_endpoint=f"/api/leave-applications/{leave.id}/cancel",
        context=context,
    )


async def get_attendance_summary_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    days: int = 7,
) -> UIResponse:
    """
    Get a summary of attendance for the visible scope.
    """
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to attendance records.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing attendance summary",
        )

    from datetime import date, timedelta
    start_date = date.today() - timedelta(days=days)

    visible_ids = await get_visible_employee_ids(db, user, user.tenant_id)

    query = (
        select(models.Attendance)
        .where(models.Attendance.tenant_id == user.tenant_id)
        .where(models.Attendance.attendance_date >= start_date)
    )
    if visible_ids is not None:
        query = query.where(models.Attendance.employee_id.in_(visible_ids))

    result = await db.execute(query)
    records = result.scalars().all()

    # Dynamic counting by status
    status_counts = Counter(rec.status for rec in records)
    rows = [
        {"status": status, "count": count}
        for status, count in sorted(status_counts.items())
    ]

    if not rows:
        return make_text_response(
            message=f"No attendance records found for the last {days} days.",
            context=context,
            hints=["Show all employees", "Show pending leaves"],
        )

    return make_table_response(
        message=f"Attendance summary for the last {days} days ({len(records)} records):",
        context=context,
        columns=["status", "count"],
        column_labels={"status": "Status", "count": "Count"},
        rows=rows,
        total=len(rows),
    )


async def get_my_permissions_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
) -> UIResponse:
    """
    Explain the user's permissions in human-friendly text.
    """
    role_perms = DEFAULT_PERMISSIONS.get(user.role, {})
    
    lines = [f"### Your Permissions ({user.role})"]
    for module, perms in role_perms.items():
        allowed = [action for action, val in perms.items() if val]
        if allowed:
            lines.append(f"- **{module.upper()}**: {', '.join(allowed)}")
        else:
            lines.append(f"- **{module.upper()}**: No access")

    return make_text_response(
        message="\n".join(lines),
        context=context,
    )
