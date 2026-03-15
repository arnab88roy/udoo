from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payroll import models
from app.modules.hr_masters import models as hr_models
from app.modules.core_masters import models as core_models
from app.schemas.user_context import UserContext
from app.schemas.ui_response import (
    UIResponse, 
    UIAction,
    UIContext,
    make_text_response, 
    make_table_response, 
    make_confirm_response,
    make_blocker_response
)
from app.utils.permissions import check_permission
from app.veda.tools.helpers import resolve_employee_by_name, fetch_display_names


async def get_payroll_status_tool(
    db: AsyncSession, 
    user: UserContext, 
    context: UIContext,
    month: Optional[int] = None, 
    year: Optional[int] = None
) -> UIResponse:
    """
    Summarizes the state of payroll for a given month and year.
    """
    if not check_permission(user, "payroll", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to payroll records.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing payroll status",
        )

    today = date.today()
    payroll_month = month or today.month
    payroll_year = year or today.year
    month_name = date(payroll_year, payroll_month, 1).strftime("%B %Y")

    # For table of individual slips
    stmt = (
        select(models.SalarySlip)
        .where(
            models.SalarySlip.tenant_id == user.tenant_id,
            models.SalarySlip.payroll_month == payroll_month,
            models.SalarySlip.payroll_year == payroll_year
        )
        .order_by(models.SalarySlip.net_pay.desc())
    )
    result = await db.execute(stmt)
    slips = result.scalars().all()

    if not slips:
        return make_text_response(
            message=f"No payroll records found for **{month_name}**.",
            context=context,
            hints=["Run payroll for this month", "Show employees"]
        )

    # Resolve employee names
    names = await fetch_display_names(
        db=db,
        tenant_id=user.tenant_id,
        employee_ids=[slip.employee_id for slip in slips],
    )

    rows = []
    status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
    for slip in slips:
        rows.append({
            "id": str(slip.id),
            "employee_name": names["employees"].get(str(slip.employee_id), "—"),
            "gross_earnings": f"₹{slip.gross_earnings:,.2f}",
            "total_deductions": f"₹{slip.total_deductions:,.2f}",
            "net_pay": f"₹{slip.net_pay:,.2f}",
            "status": status_map.get(slip.docstatus, "Draft"),
        })

    return make_table_response(
        message=f"Payroll status summary for **{month_name}**:",
        context=context,
        columns=["employee_name", "gross_earnings", "total_deductions", "net_pay", "status"],
        column_labels={
            "employee_name": "Employee",
            "gross_earnings": "Gross",
            "total_deductions": "Deductions",
            "net_pay": "Net Pay",
            "status": "Status"
        },
        rows=rows,
        total=len(rows),
        record_type="salary_slip",
        row_id_field="id",
    )


async def run_payroll_bulk_tool(
    db: AsyncSession, 
    user: UserContext, 
    context: UIContext,
    month: Optional[int] = None, 
    year: Optional[int] = None,
    working_days: Optional[int] = None,
) -> UIResponse:
    """
    Returns a CONFIRM card to trigger bulk payroll generation.
    VEDA never executes payroll directly; it returns the HITL action.
    """
    if not check_permission(user, "payroll", "submit"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have permission to run payroll. "
                   f"Only owners and HR managers can generate payroll.",
            resolution_options=[],
            context=context,
            blocked_task="Running payroll",
        )

    today = date.today()
    payroll_month = month or today.month
    payroll_year = year or today.year
    wdays = working_days or 26
    month_name = date(payroll_year, payroll_month, 1).strftime("%B %Y")

    confirm_action = UIAction(
        action_id="confirm_run_payroll",
        label=f"Run Payroll for {month_name}",
        style="primary",
        endpoint="/api/salary-slips/bulk-generate",
        method="POST",
        payload={
            "company_id": str(user.company_id),
            "payroll_month": payroll_month,
            "payroll_year": payroll_year,
            "working_days": wdays,
        },
        confirmation_required=False,
    )

    return make_confirm_response(
        message=f"Are you sure you want to generate draft salary slips for **{month_name}**?",
        context=context,
        summary={
            "Module": "Payroll",
            "Period": month_name,
            "Working Days": str(wdays),
            "Scope": "All Active Employees",
        },
        warning="This will overwrite existing draft slips for this period if they exist.",
        confirm_action=confirm_action,
    )


async def get_salary_slip_tool(
    db: AsyncSession, 
    user: UserContext, 
    context: UIContext,
    name: Optional[str] = None,
    employee_id: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> UIResponse:
    """
    Retrieves latest salary slip(s) for the user or a specific employee.
    """
    if not check_permission(user, "payroll", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have permission to view salary slips.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing salary slip",
        )

    today = date.today()
    target_employee_id = None

    # Resolve target employee
    if name and (user.is_owner or user.is_hr_manager):
        emp, disambiguation = await resolve_employee_by_name(
            db, name, user.tenant_id, user, context
        )
        if disambiguation:
            return disambiguation
        target_employee_id = emp.id
    elif employee_id:
        emp_query = select(hr_models.Employee).where(
            hr_models.Employee.employee_number == employee_id,
            hr_models.Employee.tenant_id == user.tenant_id,
        )
        result = await db.execute(emp_query)
        emp = result.scalar_one_or_none()
        if not emp:
            return make_blocker_response(
                reason=f"No employee found with ID '{employee_id}'.",
                resolution_options=[],
                context=context,
                blocked_task="Viewing salary slip",
            )
        target_employee_id = emp.id
    elif context.open_record_type == "employee" and context.open_record_id:
        target_employee_id = context.open_record_id
    elif user.employee_id:
        # Default to self
        target_employee_id = user.employee_id
    else:
        return make_blocker_response(
            reason="Please provide an employee name or ID.",
            resolution_options=[],
            context=context,
            blocked_task="Viewing salary slip",
        )

    query = select(models.SalarySlip).where(
        models.SalarySlip.tenant_id == user.tenant_id,
        models.SalarySlip.employee_id == target_employee_id
    )

    if month:
        query = query.where(models.SalarySlip.payroll_month == month)
    if year:
        query = query.where(models.SalarySlip.payroll_year == year)
    else:
        query = query.where(models.SalarySlip.payroll_year == today.year)

    query = query.order_by(models.SalarySlip.payroll_year.desc(), models.SalarySlip.payroll_month.desc())
    result = await db.execute(query)
    slips = result.scalars().all()

    if not slips:
        return make_text_response(
            message="No salary slips found for the specified period.",
            context=context,
            hints=["Show all slips", "Run payroll"]
        )

    rows = []
    status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
    for s in slips:
        month_str = date(s.payroll_year, s.payroll_month, 1).strftime("%b %Y")
        rows.append({
            "id": str(s.id),
            "period": month_str,
            "gross": f"₹{s.gross_earnings:,.2f}",
            "net_pay": f"₹{s.net_pay:,.2f}",
            "status": status_map.get(s.docstatus, "Unknown"),
            "date": s.posting_date.strftime("%Y-%m-%d") if s.posting_date else "-"
        })

    return make_table_response(
        message=f"Salary slips for the selected employee:",
        context=context,
        columns=["period", "gross", "net_pay", "status", "date"],
        column_labels={
            "period": "Period",
            "gross": "Gross",
            "net_pay": "Net Pay",
            "status": "Status",
            "date": "Posting Date"
        },
        rows=rows,
        total=len(rows),
        record_type="salary_slip",
        row_id_field="id",
    )
